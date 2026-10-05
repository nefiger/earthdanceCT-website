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

// Waiting-list signup: posts to the Brevo signup Worker, which sends a
// double opt-in confirmation email. The Brevo key never reaches the browser.
(function () {
  var endpoint = 'https://earthdance-brevo-signup.nefiger.workers.dev/subscribe';
  var forms = document.querySelectorAll('form[data-signup]');
  if (!forms.length) return;

  var FALLBACK = "We couldn't add you just now. Please try again shortly, or email info@earthdancecapetown.co.za and we'll add you by hand.";
  var pageSource = (location.pathname.replace(/^\/+|\.html$/g, '').replace(/\/+$/g, '') || 'home');

  forms.forEach(function (form) {
    var status = form.querySelector('.signup-status');
    var button = form.querySelector('button[type="submit"]');
    var shownAt = Date.now();

    function say(message, kind) {
      status.textContent = message;
      status.className = 'signup-status' + (kind ? ' is-' + kind : '');
    }

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      var email = form.elements.email.value.trim();
      if (!email || !form.elements.email.checkValidity()) {
        say('Please enter a valid email address.', 'error');
        form.elements.email.focus();
        return;
      }
      if (!form.elements.consent.checked) {
        say('Please tick the box so we know you want to hear from us.', 'error');
        return;
      }
      button.disabled = true;
      say('Joining…');
      window.fetch(endpoint, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          email: email,
          first_name: form.elements.first_name.value,
          consent: true,
          website: form.elements.website.value,
          source: 'site:' + pageSource,
          elapsed_ms: Date.now() - shownAt
        })
      }).then(function (response) {
        return response.json().catch(function () { return {}; }).then(function (data) {
          if (response.ok && data.ok) {
            form.classList.add('is-done');
            say('Almost there. Check your inbox for a confirmation email and click the link to join the list.', 'ok');
          } else {
            say(response.status >= 500 ? FALLBACK : (data.error || FALLBACK), 'error');
            button.disabled = false;
          }
        });
      }).catch(function () {
        say(FALLBACK, 'error');
        button.disabled = false;
      });
    });
  });
})();

// Homepage hero: play the muted ambient loop only where it is welcome. Skipped
// on small screens, when the visitor prefers reduced motion, or on data saver;
// the photo hero underneath stays as the fallback.
(function () {
  var video = document.querySelector('.hero-video');
  if (!video) return;
  var conn = navigator.connection || {};
  var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var wide = window.matchMedia && window.matchMedia('(min-width: 900px)').matches;
  if (reduced || !wide || conn.saveData) return;
  video.addEventListener('playing', function () {
    video.closest('.hero').classList.add('has-video');
  });
  video.src = video.getAttribute('data-src');
  var started = video.play();
  if (started && started.catch) started.catch(function () {});
})();
