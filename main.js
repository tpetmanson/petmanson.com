// Message: thanks for checking out the source code of my homepage.
// Please enjoy the high quality Javascript you will find here.

// Helper function for creating galleries.
function CreateLightGalleryElements(container_id, path, from, to) {
  let container = document.getElementById(container_id)
  console.log(container);
  for (let idx=from ; idx<=to ; ++idx) {
    let a = document.createElement('a')
    a.setAttribute('href', `${path}/${idx}.jpg`)
    let img = document.createElement('img')
    img.setAttribute('src', `${path}/${idx}_thumb.jpg`)
    a.appendChild(img)
    container.appendChild(a);
  }
}

// W E B  P L A Y E R
// Self-hosted replacement for third-party iframe players (YouTube,
// SoundCloud, Bandcamp). Plays audio/video with the browser's native
// controls; put links back to the original sources (Bandcamp, YouTube,
// SoundCloud, ...) in the post HTML next to the player.
//
// Usage:
//   <div id="my-player"></div>
//   <script type="text/javascript">
//     CreateWebPlayer('my-player', {
//       artist: 'Timo Petmanson',        // optional; shown as "by ..." + lock-screen metadata
//       album: 'Voyage To Neptune',      // optional; shown as the header title
//       buy: 'https://timopetmanson.bandcamp.com/album/voyage-to-neptune',
//                                        // optional; adds a "buy" link to the header
//       items: [
//         { title: 'Star diplomat',
//           src: 'albums/released/VoyageToNeptune/...%2001%20Star%20diplomat.mp3',
//           cover: 'albums/released/VoyageToNeptune/cover.jpg',
//           duration: '3:59' },          // duration is an optional display string
//         // ... more items; clicking a row in the list plays it, and when
//         // a track ends the next one starts automatically.
//       ]
//     });
//   </script>
// Whether an item is video is inferred from the src file extension;
// override with an explicit `video: true/false` on the item.

function CreateWebPlayer(container_id, config) {
  let container = document.getElementById(container_id)
  let items = config.items || []
  let current = -1

  container.classList.add('webplayer')

  // The media elements; native controls handle play, seek and volume.
  let cover = document.createElement('img')
  cover.className = 'webplayer-cover'
  cover.setAttribute('alt', 'Cover art')
  let video = document.createElement('video')
  video.className = 'webplayer-video'
  video.controls = true
  video.playsInline = true
  video.preload = config.preload || 'metadata'
  let audio = document.createElement('audio')
  audio.className = 'webplayer-audio'
  audio.controls = true
  audio.preload = config.preload || 'metadata'

  // Bandcamp-style header: title with a "buy" link, then "by <artist>".
  let header = document.createElement('div')
  header.className = 'webplayer-header'
  let headertitle = document.createElement('span')
  headertitle.className = 'webplayer-header-title'
  headertitle.textContent = config.album || (items[0] ? items[0].title : '')
  header.appendChild(headertitle)
  if (config.buy) {
    let buy = document.createElement('a')
    buy.className = 'webplayer-buy'
    buy.setAttribute('href', config.buy)
    buy.setAttribute('target', '_blank')
    buy.setAttribute('rel', 'noopener')
    buy.textContent = 'buy'
    header.appendChild(buy)
  }
  let byline = document.createElement('div')
  byline.className = 'webplayer-byline'
  if (config.artist) byline.textContent = 'by ' + config.artist

  // Track listing: a simple list; click a row to play it.
  let playlist = document.createElement('ol')
  playlist.className = 'webplayer-playlist'
  let rows = []
  items.forEach(function(item, idx) {
    let li = document.createElement('li')
    let row = document.createElement('button')
    row.className = 'webplayer-item'
    row.addEventListener('click', function() { Load(idx, true) })
    let num = document.createElement('span')
    num.className = 'webplayer-item-num'
    num.textContent = idx + 1
    let name = document.createElement('span')
    name.className = 'webplayer-item-title'
    name.textContent = item.title
    let duration = document.createElement('span')
    duration.className = 'webplayer-item-duration'
    duration.textContent = item.duration || ''
    row.appendChild(num)
    row.appendChild(name)
    row.appendChild(duration)
    li.appendChild(row)
    playlist.appendChild(li)
    rows.push(row)
  })

  if (headertitle.textContent) container.appendChild(header)
  if (config.artist) container.appendChild(byline)
  container.appendChild(cover)
  container.appendChild(video)
  container.appendChild(audio)
  if (items.length > 1) container.appendChild(playlist)

  function IsVideo(item) {
    if (item.video !== undefined) return item.video
    return /\.(mp4|m4v|webm|mov|ogv)(\?|$)/i.test(item.src)
  }

  function Load(idx, autoplay) {
    if (idx < 0 || idx >= items.length) return
    audio.pause()
    video.pause()
    current = idx
    let item = items[idx]
    let isvideo = IsVideo(item)
    let media = isvideo ? video : audio

    video.classList.toggle('webplayer-hidden', !isvideo)
    audio.classList.toggle('webplayer-hidden', isvideo)
    cover.classList.toggle('webplayer-hidden', isvideo || !item.cover)
    if (isvideo) {
      audio.removeAttribute('src')
      if (item.cover) video.setAttribute('poster', item.cover)
      else video.removeAttribute('poster')
      video.src = item.src
    } else {
      video.removeAttribute('src')
      video.removeAttribute('poster')
      if (item.cover) cover.src = item.cover
      audio.src = item.src
    }

    rows.forEach(function(row, i) {
      row.classList.toggle('webplayer-item-active', i == idx)
    })

    if (autoplay) {
      let promise = media.play()
      if (promise) promise.catch(function() {})
    }
  }

  function OnEnded() {
    // Automatically continue with the next item.
    if (current < items.length - 1) Load(current + 1, true)
  }
  audio.addEventListener('ended', OnEnded)
  video.addEventListener('ended', OnEnded)

  function OnPlay(ev) {
    // Only one player on the page should play at a time.
    for (let media of document.querySelectorAll('audio, video')) {
      if (media !== ev.target) media.pause()
    }
    // Lock-screen / hardware-key metadata and controls (Media Session API).
    if ('mediaSession' in navigator) {
      let item = items[current]
      navigator.mediaSession.metadata = new MediaMetadata({
        title: item.title,
        artist: config.artist || '',
        album: config.album || '',
        artwork: item.cover ? [{ src: item.cover }] : [],
      })
      navigator.mediaSession.setActionHandler('previoustrack',
        current > 0 ? function() { Load(current - 1, true) } : null)
      navigator.mediaSession.setActionHandler('nexttrack',
        current < items.length - 1 ? function() { Load(current + 1, true) } : null)
    }
  }
  audio.addEventListener('play', OnPlay)
  video.addEventListener('play', OnPlay)

  Load(0, false)
}

// Fix vh on mobiles with custom CSS variable.
function UpdateVhProperty() {
  document.querySelector(':root').style
    .setProperty('--vh', window.innerHeight/100 + 'px');
}

// Update VH in various occasions.
window.addEventListener('resize', UpdateVhProperty);
window.addEventListener('load', UpdateVhProperty);
window.addEventListener('focus', UpdateVhProperty);
UpdateVhProperty();

// Slug of a post page: "<date>-<slugified title>".
// Must match slugify() in generate.py exactly.
function Slugify(text) {
  return text.toLowerCase()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '') // strip combining diacritics
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

// Turn every article title on the index page into a link to its
// dedicated post page generated by generate.py.
function LinkArticleTitles() {
  if (document.body.classList.contains('post-page')) return;
  for (let article of document.getElementsByTagName('article')) {
    let title = article.querySelector('h2.title')
    let date = article.querySelector('div.date')
    if (!title || !date || title.querySelector('a')) continue;
    let slug = date.textContent.trim() + '-' + Slugify(title.textContent)
    let a = document.createElement('a')
    a.setAttribute('href', `posts/${slug}.html`)
    while (title.firstChild) a.appendChild(title.firstChild);
    title.appendChild(a)
  }
}

// Behold, "infinite scroll"!!
var allArticles = []
var numVisibleArticles = 2

function initarticles() {
  allArticles = document.getElementsByTagName('article');
  console.log("Loaded " + allArticles.length + " articles.");
  for (let idx=0 ; idx<Math.min(allArticles.length, numVisibleArticles) ; idx++) {
    allArticles[idx].classList.add('visiblearticle');
  }
  LinkArticleTitles();
}

window.addEventListener('DOMContentLoaded', initarticles);
window.onscroll = function(ev) {
  // https://stackoverflow.com/questions/9439725/how-to-detect-if-browser-window-is-scrolled-to-bottom
  if ((window.innerHeight + window.scrollY) + 1 >= document.body.offsetHeight) {
    if (numVisibleArticles < allArticles.length) {
      allArticles[numVisibleArticles].classList.add('visiblearticle');
      numVisibleArticles+=1;
      console.log(numVisibleArticles);
    }
  }
};
