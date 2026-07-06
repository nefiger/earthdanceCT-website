// Gallery: renders the curated PHOTOS list (assets/js/photos-data.js) into a
// masonry grid with a lightbox. Photographer credit stays subtle — a hover
// caption on each tile and a line in the lightbox — per the photo agreements.
(function () {
  var grid = document.getElementById('gallery-grid');
  if (!grid || typeof PHOTOS === 'undefined') return;

  var frag = document.createDocumentFragment();
  PHOTOS.forEach(function (p, idx) {
    var fig = document.createElement('figure');
    var img = document.createElement('img');
    img.loading = 'lazy';
    img.decoding = 'async';
    img.src = 'assets/photos/thumbs/' + p.file;
    img.width = p.w;
    img.height = p.h;
    img.alt = 'Earthdance Cape Town 2025';
    var cap = document.createElement('figcaption');
    cap.textContent = '© ' + p.credit;
    fig.appendChild(img);
    fig.appendChild(cap);
    fig.addEventListener('click', function () { openLightbox(idx); });
    frag.appendChild(fig);
  });
  grid.appendChild(frag);

  // Lightbox
  var lb = document.createElement('div');
  lb.className = 'lightbox';
  lb.innerHTML = '<button class="lb-close" aria-label="Close">×</button>' +
    '<button class="lb-prev" aria-label="Previous">‹</button>' +
    '<button class="lb-next" aria-label="Next">›</button>' +
    '<img alt=""><div class="lb-caption"></div>';
  document.body.appendChild(lb);
  var lbImg = lb.querySelector('img');
  var lbCap = lb.querySelector('.lb-caption');
  var pos = 0;

  function show(i) {
    pos = (i + PHOTOS.length) % PHOTOS.length;
    var p = PHOTOS[pos];
    lbImg.src = 'assets/photos/web/' + p.file;
    lbImg.alt = 'Earthdance Cape Town 2025';
    lbCap.textContent = 'Earthdance Cape Town 2025 · © ' + p.credit +
      ' · ' + (pos + 1) + ' / ' + PHOTOS.length;
  }
  function openLightbox(i) {
    show(i);
    lb.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function close() {
    lb.classList.remove('open');
    lbImg.src = '';
    document.body.style.overflow = '';
  }
  lb.querySelector('.lb-close').addEventListener('click', close);
  lb.querySelector('.lb-prev').addEventListener('click', function (e) { e.stopPropagation(); show(pos - 1); });
  lb.querySelector('.lb-next').addEventListener('click', function (e) { e.stopPropagation(); show(pos + 1); });
  lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
  document.addEventListener('keydown', function (e) {
    if (!lb.classList.contains('open')) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowLeft') show(pos - 1);
    if (e.key === 'ArrowRight') show(pos + 1);
  });
})();
