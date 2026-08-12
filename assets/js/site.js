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

// Meta Pixel + Conversions API events with matching IDs for deduplication.
(function () {
  var endpoint = 'https://earthdance-meta-capi.nefiger.workers.dev/events';
  var ticketUrlPart = 'quicket.co.za/events/368787-earthdance-cape-town-2026';

  function makeEventId(prefix) {
    if (window.crypto && typeof window.crypto.randomUUID === 'function') {
      return prefix + '-' + window.crypto.randomUUID();
    }
    return prefix + '-' + Date.now() + '-' + Math.random().toString(36).slice(2, 12);
  }

  function getCookie(name) {
    var prefix = name + '=';
    var parts = document.cookie ? document.cookie.split(';') : [];
    for (var i = 0; i < parts.length; i += 1) {
      var part = parts[i].trim();
      if (part.indexOf(prefix) === 0) {
        try {
          return decodeURIComponent(part.slice(prefix.length));
        } catch (error) {
          return part.slice(prefix.length);
        }
      }
    }
    return '';
  }

  function getFbc() {
    var cookie = getCookie('_fbc');
    if (cookie) return cookie;

    var fbclid = new URLSearchParams(window.location.search).get('fbclid');
    return fbclid ? 'fb.1.' + Date.now() + '.' + fbclid.slice(0, 400) : '';
  }

  function sendServerEvent(eventName, eventId) {
    var payload = {
      event_name: eventName,
      event_id: eventId,
      event_source_url: window.location.href,
      fbp: getCookie('_fbp'),
      fbc: getFbc(),
    };

    window.fetch(endpoint, {
      method: 'POST',
      mode: 'cors',
      credentials: 'omit',
      keepalive: true,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }).catch(function () {
      // Browser tracking remains available if the server event cannot be sent.
    });
  }

  function sendPageView() {
    if (window.earthdanceMetaPageViewEventId) {
      sendServerEvent('PageView', window.earthdanceMetaPageViewEventId);
    }
  }

  if (document.readyState === 'complete') {
    window.setTimeout(sendPageView, 1000);
  } else {
    window.addEventListener('load', function () {
      window.setTimeout(sendPageView, 1000);
    });
  }

  document.addEventListener('click', function (event) {
    var link = event.target.closest && event.target.closest('a[href]');
    if (!link || link.href.indexOf(ticketUrlPart) === -1) return;

    var eventId = makeEventId('checkout');
    var customData = { content_name: 'Earthdance Cape Town 2026 tickets' };

    if (typeof window.fbq === 'function') {
      window.fbq('track', 'InitiateCheckout', customData, { eventID: eventId });
    }
    sendServerEvent('InitiateCheckout', eventId);
  }, true);
})();
