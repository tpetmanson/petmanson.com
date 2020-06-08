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
