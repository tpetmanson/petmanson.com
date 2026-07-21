#!/usr/bin/env -S uv run
"""Generate dedicated post pages and sitemap.xml from index.html.

index.html stays the single source of truth: this script parses it, extracts
the shared <head> and <footer>, plus every news <article>, and writes one
standalone page per article into posts/. It also
rewrites sitemap.xml and deletes orphaned pages for posts that no longer
exist.

The slug of a post is "<date>-<slugified title>". The exact same slug
algorithm lives in main.js (Slugify), which links article titles on the
index page to the generated pages — keep the two implementations in sync.

Usage: uv run generate.py
"""

import html
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

from bs4 import BeautifulSoup

ROOT = Path(__file__).parent
SITE = "https://petmanson.com"
POSTS_DIR = ROOT / "posts"
DEFAULT_IMAGE = "img/top-banner-min.png"


def slugify(text):
    # Must match Slugify() in main.js exactly.
    text = text.lower()
    text = unicodedata.normalize("NFD", text)
    text = re.sub("[\u0300-\u036f]", "", text)  # strip combining diacritics
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def esc(text):
    return html.escape(text, quote=True)


def absolute_url(path):
    return f"{SITE}/{quote(path, safe='/%')}"


def robots_disallowed_prefixes():
    prefixes = []
    robots = ROOT / "robots.txt"
    if robots.exists():
        for line in robots.read_text().splitlines():
            if line.lower().startswith("disallow:"):
                path = line.split(":", 1)[1].strip().lstrip("/")
                if path:
                    prefixes.append(path)
    return prefixes


@dataclass
class Post:
    slug: str
    title: str
    date: str
    description: str
    image: str  # site-relative path
    content: str  # article html without its own title/date


def extract_description(article, date):
    chunks = []
    for p in article.find_all("p"):
        text = " ".join(p.get_text().split())
        if text:
            chunks.append(text)
        if sum(len(c) for c in chunks) >= 160:
            break
    text = " ".join(chunks)
    if len(text) > 157:
        text = text[:157].rsplit(" ", 1)[0].rstrip(" ,.;:") + "…"
    return text or f"News post by Timo Petmanson from {date}."


def extract_image(article, disallowed):
    img = article.find("img", class_="featured-image") or article.find("img")
    src = img.get("src") if img else None
    if not src:
        # Galleries are built by inline JS; recover the path of the first photo.
        for script in article.find_all("script"):
            m = re.search(
                r"CreateLightGalleryElements\(\s*'[^']*'\s*,\s*'([^']+)'",
                script.string or "",
            )
            if m:
                src = m.group(1) + "/1.jpg"
                break
    if src:
        src = src.lstrip("/")
        # Don't advertise photos that robots.txt keeps out of search engines.
        if any(src.startswith(prefix) for prefix in disallowed):
            src = None
    return src or DEFAULT_IMAGE


def extract_posts(soup):
    disallowed = robots_disallowed_prefixes()
    posts = []
    for article in soup.select("div.news article.article"):
        title_el = article.select_one("h2.title")
        date_el = article.select_one("div.date")
        if title_el is None or date_el is None:
            sys.exit("ERROR: article without <h2 class='title'> or <div class='date'>")
        title = " ".join(title_el.get_text().split())
        date = date_el.get_text().strip()
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            sys.exit(f"ERROR: bad date {date!r} in post {title!r} (want YYYY-MM-DD)")

        description = extract_description(article, date)
        image = extract_image(article, disallowed)

        # The post page shows title and date in the page heading instead.
        title_el.extract()
        date_el.extract()
        classes = article.get("class", [])
        if "visiblearticle" not in classes:
            classes.append("visiblearticle")
        article["class"] = classes

        posts.append(Post(
            slug=f"{date}-{slugify(title)}",
            title=title,
            date=date,
            description=description,
            image=image,
            content=str(article),
        ))

    slugs = [p.slug for p in posts]
    for slug in {s for s in slugs if slugs.count(s) > 1}:
        sys.exit(f"ERROR: duplicate slug {slug!r} — give the posts distinct titles")
    return posts


def build_head_template(soup):
    """Shared <head> content: index.html's head minus title/description,
    with <base href="../"> injected so all relative URLs keep working."""
    head = soup.head
    head.find("title").extract()
    head.find("meta", attrs={"name": "description"}).extract()
    base = soup.new_tag("base", href="../")
    head.find("meta", charset=True).insert_after(base)
    return head.decode_contents()


def seo_block(post):
    url = f"{SITE}/posts/{post.slug}.html"
    image = absolute_url(post.image)
    json_ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post.title,
        "description": post.description,
        "datePublished": post.date,
        "url": url,
        "image": image,
        "inLanguage": "en",
        "author": {"@type": "Person", "name": "Timo Petmanson", "url": SITE},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
    }, ensure_ascii=False, indent=2)
    return f"""\
  <title>{esc(post.title)} — Timo Petmanson</title>
  <meta name="description" content="{esc(post.description)}">
  <meta name="author" content="Timo Petmanson">
  <link rel="canonical" href="{url}">

  <meta property="og:type" content="article">
  <meta property="og:site_name" content="Timo Petmanson">
  <meta property="og:locale" content="en_US">
  <meta property="og:title" content="{esc(post.title)}">
  <meta property="og:description" content="{esc(post.description)}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{image}">
  <meta property="article:published_time" content="{post.date}">
  <meta property="article:author" content="Timo Petmanson">

  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(post.title)}">
  <meta name="twitter:description" content="{esc(post.description)}">
  <meta name="twitter:image" content="{image}">

  <script type="application/ld+json">
{json_ld}
  </script>"""


def nav_html(newer, older):
    # "Previous" is the newer post, "Next" the older one (reading order).
    if newer:
        prev_link = (f'<a class="post-nav-prev" href="posts/{newer.slug}.html" '
                     f'title="{esc(newer.title)}">&laquo; Previous</a>')
    else:
        prev_link = '<span class="post-nav-prev post-nav-disabled">&laquo; Previous</span>'
    if older:
        next_link = (f'<a class="post-nav-next" href="posts/{older.slug}.html" '
                     f'title="{esc(older.title)}">Next &raquo;</a>')
    else:
        next_link = '<span class="post-nav-next post-nav-disabled">Next &raquo;</span>'
    return (f'<nav class="post-nav">{prev_link}'
            f'<a class="post-nav-home" href="./">Main page</a>{next_link}</nav>')


def render_post(post, newer, older, head_template, footer):
    nav = nav_html(newer, older)
    return f"""<!doctype html>
<html lang="en">

<head>
{head_template}
{seo_block(post)}
</head>

<body class="post-page">
<main class="content-wrapper">
<div class="news">
  <h1 class="section-title">{esc(post.title)}</h1>
  <div class="post-date">{post.date}</div>
  {nav}
  {post.content}
  {nav}
</div>

{footer}
</main>

</body>

</html>
"""


def write_sitemap(posts):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    newest = max(p.date for p in posts) if posts else None
    lastmod = f"<lastmod>{newest}</lastmod>" if newest else ""
    lines.append(f"  <url><loc>{SITE}</loc>{lastmod}</url>")
    for post in posts:
        lines.append(f"  <url><loc>{SITE}/posts/{post.slug}.html</loc>"
                     f"<lastmod>{post.date}</lastmod></url>")
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n")


def main():
    soup = BeautifulSoup((ROOT / "index.html").read_text(), "html.parser")

    footer = str(soup.find("footer"))
    posts = extract_posts(soup)
    head_template = build_head_template(soup)  # mutates soup.head, do this last

    POSTS_DIR.mkdir(exist_ok=True)
    for idx, post in enumerate(posts):
        newer = posts[idx - 1] if idx > 0 else None
        older = posts[idx + 1] if idx + 1 < len(posts) else None
        page = render_post(post, newer, older, head_template, footer)
        (POSTS_DIR / f"{post.slug}.html").write_text(page)
    print(f"Wrote {len(posts)} posts to {POSTS_DIR.relative_to(ROOT)}/")

    wanted = {f"{p.slug}.html" for p in posts}
    for orphan in sorted(POSTS_DIR.glob("*.html")):
        if orphan.name not in wanted:
            orphan.unlink()
            print(f"Deleted orphan {orphan.relative_to(ROOT)}")

    write_sitemap(posts)
    print(f"Wrote sitemap.xml with {len(posts) + 1} URLs")


if __name__ == "__main__":
    main()
