const ALLOWED_EVENTS = new Set(['PageView', 'InitiateCheckout']);
const MAX_BODY_BYTES = 16 * 1024;

function json(body, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'cache-control': 'no-store',
      ...extraHeaders,
    },
  });
}

function corsHeaders(origin) {
  return {
    'access-control-allow-origin': origin,
    'access-control-allow-methods': 'POST, OPTIONS',
    'access-control-allow-headers': 'content-type',
    'access-control-max-age': '86400',
    vary: 'Origin',
  };
}

function optionalString(value, maxLength = 512) {
  return typeof value === 'string' && value.length > 0 && value.length <= maxLength
    ? value
    : undefined;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === 'GET' && url.pathname === '/') {
      return json({ ok: true, service: 'earthdance-meta-capi' });
    }

    if (!env.META_ACCESS_TOKEN || !env.META_PIXEL_ID || !env.ALLOWED_ORIGIN) {
      return json({ ok: false, error: 'Worker configuration is incomplete.' }, 500);
    }

    let allowedOrigin;
    try {
      allowedOrigin = new URL(env.ALLOWED_ORIGIN).origin;
    } catch {
      return json({ ok: false, error: 'Worker origin configuration is invalid.' }, 500);
    }

    const origin = request.headers.get('origin');
    if (origin !== allowedOrigin) {
      return json({ ok: false, error: 'Origin not allowed.' }, 403);
    }

    const cors = corsHeaders(allowedOrigin);

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: cors });
    }

    if (request.method !== 'POST' || url.pathname !== '/events') {
      return json({ ok: false, error: 'Not found.' }, 404, cors);
    }

    const contentType = request.headers.get('content-type') || '';
    if (!contentType.toLowerCase().startsWith('application/json')) {
      return json({ ok: false, error: 'Expected JSON.' }, 415, cors);
    }

    const declaredSize = Number(request.headers.get('content-length') || 0);
    if (declaredSize > MAX_BODY_BYTES) {
      return json({ ok: false, error: 'Request is too large.' }, 413, cors);
    }

    const rawBody = await request.text();
    if (new TextEncoder().encode(rawBody).byteLength > MAX_BODY_BYTES) {
      return json({ ok: false, error: 'Request is too large.' }, 413, cors);
    }

    let body;
    try {
      body = JSON.parse(rawBody);
    } catch {
      return json({ ok: false, error: 'Invalid JSON.' }, 400, cors);
    }

    if (!body || typeof body !== 'object' || Array.isArray(body)) {
      return json({ ok: false, error: 'Invalid event.' }, 400, cors);
    }

    const eventName = body.event_name;
    if (!ALLOWED_EVENTS.has(eventName)) {
      return json({ ok: false, error: 'Event is not allowed.' }, 400, cors);
    }

    const eventId = optionalString(body.event_id, 128);
    if (!eventId || !/^[A-Za-z0-9._:-]+$/.test(eventId)) {
      return json({ ok: false, error: 'Invalid event ID.' }, 400, cors);
    }

    let eventSourceUrl;
    try {
      const sourceUrl = new URL(body.event_source_url);
      if (sourceUrl.origin !== allowedOrigin) throw new Error('Unexpected origin');
      eventSourceUrl = sourceUrl.href;
    } catch {
      return json({ ok: false, error: 'Invalid event source URL.' }, 400, cors);
    }

    const userData = {
      client_ip_address: optionalString(request.headers.get('cf-connecting-ip'), 64),
      client_user_agent: optionalString(request.headers.get('user-agent'), 1024),
      fbp: optionalString(body.fbp),
      fbc: optionalString(body.fbc),
    };

    Object.keys(userData).forEach((key) => {
      if (!userData[key]) delete userData[key];
    });

    const serverEvent = {
      event_name: eventName,
      event_time: Math.floor(Date.now() / 1000),
      event_id: eventId,
      event_source_url: eventSourceUrl,
      action_source: 'website',
      user_data: userData,
    };

    if (eventName === 'InitiateCheckout') {
      serverEvent.custom_data = {
        content_name: 'Earthdance Cape Town 2026 tickets',
      };
    }

    const metaPayload = {
      data: [serverEvent],
      access_token: env.META_ACCESS_TOKEN,
    };

    if (env.META_TEST_EVENT_CODE) {
      metaPayload.test_event_code = env.META_TEST_EVENT_CODE;
    }

    let metaResponse;
    try {
      metaResponse = await fetch(
        `https://graph.facebook.com/v25.0/${encodeURIComponent(env.META_PIXEL_ID)}/events`,
        {
          method: 'POST',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify(metaPayload),
        },
      );
    } catch (error) {
      console.error({ event: 'meta_request_failed', message: error.message });
      return json({ ok: false, error: 'Could not reach Meta.' }, 502, cors);
    }

    let metaResult;
    try {
      metaResult = await metaResponse.json();
    } catch {
      metaResult = {};
    }

    if (!metaResponse.ok || metaResult.error) {
      console.error({
        event: 'meta_event_rejected',
        status: metaResponse.status,
        code: metaResult.error?.code,
        message: metaResult.error?.message,
      });
      return json(
        {
          ok: false,
          error: 'Meta rejected the event.',
          code: metaResult.error?.code,
        },
        502,
        cors,
      );
    }

    console.log({
      event: 'meta_event_sent',
      event_name: eventName,
      event_id: eventId,
      events_received: metaResult.events_received,
    });

    return json(
      {
        ok: true,
        events_received: metaResult.events_received,
      },
      200,
      cors,
    );
  },
};
