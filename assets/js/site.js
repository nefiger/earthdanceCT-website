// Shared nav behaviour: mobile toggle + tap-to-open dropdowns.
(function () {
  var header = document.querySelector('.site-header');
  var toggle = document.querySelector('.nav-toggle');
  function closeGroups() {
    document.querySelectorAll('.nav-group.open').forEach(function (g) {
      g.classList.remove('open');
    });
  }
  if (toggle) {
    toggle.addEventListener('click', function () {
      var open = header.classList.toggle('nav-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (!open) closeGroups();
    });
  }
  document.querySelectorAll('.nav-group-btn').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      var group = btn.parentElement;
      document.querySelectorAll('.nav-group.open').forEach(function (g) {
        if (g !== group) g.classList.remove('open');
      });
      group.classList.toggle('open');
    });
  });
  document.querySelectorAll('.nav-drop').forEach(function (drop) {
    drop.addEventListener('click', function (e) {
      e.stopPropagation();
    });
  });
  document.querySelectorAll('.nav-drop a').forEach(function (link) {
    link.addEventListener('click', function () {
      closeGroups();
      if (header) header.classList.remove('nav-open');
      if (toggle) toggle.setAttribute('aria-expanded', 'false');
    });
  });
  document.addEventListener('click', function () {
    closeGroups();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      closeGroups();
      if (header) header.classList.remove('nav-open');
      if (toggle) toggle.setAttribute('aria-expanded', 'false');
    }
  });
})();
