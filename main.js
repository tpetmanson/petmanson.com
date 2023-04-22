// Message: thanks for checking out the source code of my homepage.
// Please enjoy the high quality Javascript you will find here.

// Helper function for creating galleries.
function CreateLightGalleryElements(container_id, path, from, to) {
  let container = document.getElementById(container_id)
  console.log(container);
  for (let idx=from ; idx<=to ; ++idx) {
    console.log(idx)
    let a = document.createElement('a')
    a.setAttribute('href', `${path}/${idx}.jpg`)
    let img = document.createElement('img')
    img.setAttribute('src', `${path}/${idx}_thumb.jpg`)
    a.appendChild(img)
    container.appendChild(a);
  }
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

// Behold, "infinite scroll"!!
var allArticles = []
var numVisibleArticles = 2

function initarticles() {
  allArticles = document.getElementsByTagName('article');
  console.log("Loaded " + allArticles.length + " articles.");
  for (let idx=0 ; idx<Math.min(allArticles.length, numVisibleArticles) ; idx++) {
    allArticles[idx].classList.add('visiblearticle');
  }
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
