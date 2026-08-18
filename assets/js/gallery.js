// Gallery: renders photo sets into masonry grids with a shared lightbox.
//
// Two sets exist. The curated 2025 set (PHOTOS, assets/js/photos-data.js) keeps
// photographer credit subtle — hover caption plus a lightbox line — per the
// photo agreements. The past-events set (PAST_PHOTOS) has no credit metadata
// and goes up uncredited by decision, so it renders without a caption.
(function () {
  var sets = [];

  function mount(gridId, photos, opts) {
    var grid = document.getElementById(gridId);
    if (!grid || !photos || !photos.length) return;

    var set = {
      photos: photos,
      thumbDir: opts.thumbDir,
      webDir: opts.webDir,
      alt: opts.alt,
      credited: !!opts.credited
    };
    sets.push(set);

    var frag = document.createDocumentFragment();
    photos.forEach(function (p, idx) {
      var fig = document.createElement('figure');
      var img = document.createElement('img');
      img.loading = 'lazy';
      img.decoding = 'async';
      img.src = set.thumbDir + p.file;
      img.width = p.w;
      img.height = p.h;
      img.alt = set.alt;
      fig.appendChild(img);
      if (set.credited) {
        var cap = document.createElement('figcaption');
        cap.textContent = '© ' + p.credit;
        fig.appendChild(cap);
      }
      fig.addEventListener('click', function () { open(set, idx); });
      frag.appendChild(fig);
    });
    grid.appendChild(frag);
  }

  mount('gallery-grid', typeof PHOTOS === 'undefined' ? null : PHOTOS, {
    thumbDir: 'assets/photos/thumbs/',
    webDir: 'assets/photos/web/',
    alt: 'Earthdance Cape Town 2025',
    credited: true
  });
  mount('past-grid', typeof PAST_PHOTOS === 'undefined' ? null : PAST_PHOTOS, {
    thumbDir: 'assets/photos/past/thumbs/',
    webDir: 'assets/photos/past/web/',
    alt: 'Earthdance Cape Town, earlier years',
    credited: false
  });

  if (!sets.length) return;

  var lb = document.createElement('div');
  lb.className = 'lightbox';
  lb.innerHTML = '<button class="lb-close" aria-label="Close">×</button>' +
    '<button class="lb-prev" aria-label="Previous">‹</button>' +
    '<button class="lb-next" aria-label="Next">›</button>' +
    '<img alt=""><div class="lb-caption"></div>';
  document.body.appendChild(lb);
  var lbImg = lb.querySelector('img');
  var lbCap = lb.querySelector('.lb-caption');
  var active = sets[0];
  var pos = 0;

  function show(i) {
    var n = active.photos.length;
    pos = (i + n) % n;
    var p = active.photos[pos];
    lbImg.src = active.webDir + p.file;
    lbImg.alt = active.alt;
    lbCap.textContent = active.alt +
      (active.credited ? ' · © ' + p.credit : '') +
      ' · ' + (pos + 1) + ' / ' + n;
  }
  function open(set, i) {
    active = set;
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
