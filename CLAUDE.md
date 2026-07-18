# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Personal website of Timo Petmanson (petmanson.com) — an electronic-music artist page with albums, collaborations, and a news blog. It is a hand-written static site with **no build system, no package manager, and no tests**. Deployment is just serving these files; preview locally with any static server, e.g. `python3 -m http.server`.

## Structure

- `index.html` — the entire site. One page containing the album sections and every news post as an `<article class="article">` inside `<div class="news">`. **New blog posts are added here**, as a new `<article>` placed at the top of the news list (posts are ordered newest-first, each with an `<h2 class="title">` and a `<div class="date">YYYY-MM-DD</div>`).
- `main.js` — three small pieces: `CreateLightGalleryElements(container_id, path, from, to)` gallery builder, a `--vh` CSS-variable fix for mobile viewport height, and "infinite scroll" that reveals one more article (`visiblearticle` class) each time the user scrolls to the bottom.
- `main.css` / `reset.css` — all styling; no preprocessor.
- `plugins/LightGallery/` — vendored LightGallery library for photo galleries.
- `img/news/<post-name>/` — photos for a post, named `1.jpg`, `2.jpg`, … with matching `1_thumb.jpg` thumbnails.
- `updatedns.py` — standalone dynamic-DNS updater for petmanson.com / mandarones.com via the zone.eu API (needs an API key filled in; not part of the site).
- `albums/`, `recordings/`, `videos/` — media files, gitignored (a few album cover images were committed before the ignore rule and remain tracked).

## Adding a photo gallery to a post

1. Put sequentially numbered JPGs (`1.jpg` … `N.jpg`) in `img/news/<post-name>/`.
2. Generate thumbnails (requires ImageMagick): `./make_thumbnails.sh img/news/<post-name>/*.jpg` — creates `N_thumb.jpg` at 225px.
3. In the article, add an empty `<div id="<name>-gallery"></div>` followed by an inline script:
   ```html
   <script type="text/javascript">
     CreateLightGalleryElements('<name>-gallery', 'img/news/<post-name>', 1, N);
     lightGallery(document.getElementById('<name>-gallery'));
   </script>
   ```

## Conventions

- News posts are written in casual first person, mostly English with occasional Estonian; keep that voice when drafting content.
- Embedded media (SoundCloud, YouTube) uses the providers' standard iframe embed snippets pasted inline.
- URLs to files with spaces are percent-encoded by hand (e.g. `Timo%20Petmanson%20-%20Helisupp.mp3`).
- `sitemap.xml` lists only the root URL, so new posts need no sitemap change. `robots.txt` is used to keep specific photo directories out of search engines (currently the wedding gallery) — preserve those Disallow lines.
