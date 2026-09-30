// Vendor pages: click a gallery photo to see it large, with its caption.
// Reuses the .lightbox styles from the main gallery.
(function () {
  var groups = document.querySelectorAll('[data-vendor-shots]');
  if (!groups.length) return;

  var lb = document.createElement('div');
  lb.className = 'lightbox';
  lb.innerHTML = '<button class="lb-close" aria-label="Close">×</button>' +
    '<button class="lb-prev" aria-label="Previous">‹</button>' +
    '<button class="lb-next" aria-label="Next">›</button>' +
    '<img alt=""><div class="lb-caption"></div>';
  document.body.appendChild(lb);
  var lbImg = lb.querySelector('img');
  var lbCap = lb.querySelector('.lb-caption');
  var shots = [];
  var pos = 0;

  function show(i) {
    pos = (i + shots.length) % shots.length;
    var img = shots[pos];
    var caption = img.parentNode.querySelector('figcaption');
    lbImg.src = img.currentSrc || img.src;
    lbImg.alt = img.alt;
    lbCap.textContent = (caption ? caption.textContent + ' · ' : '') + (pos + 1) + ' / ' + shots.length;
  }
  function close() {
    lb.classList.remove('open');
    lbImg.src = '';
    document.body.style.overflow = '';
  }

  Array.prototype.forEach.call(groups, function (group) {
    var images = Array.prototype.slice.call(group.querySelectorAll('.vendor-shot img'));
    images.forEach(function (img, idx) {
      img.addEventListener('click', function () {
        shots = images;
        show(idx);
        lb.classList.add('open');
        document.body.style.overflow = 'hidden';
      });
    });
  });

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
