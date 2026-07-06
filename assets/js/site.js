// Shared nav behaviour: mobile toggle + tap-to-open dropdowns.
(function () {
  var header = document.querySelector('.site-header');
  var toggle = document.querySelector('.nav-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var open = header.classList.toggle('nav-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }
  document.querySelectorAll('.nav-group-btn').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var group = btn.parentElement;
      document.querySelectorAll('.nav-group.open').forEach(function (g) {
        if (g !== group) g.classList.remove('open');
      });
      group.classList.toggle('open');
    });
  });
  document.addEventListener('click', function () {
    document.querySelectorAll('.nav-group.open').forEach(function (g) {
      g.classList.remove('open');
    });
  });
})();
