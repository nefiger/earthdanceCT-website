const MAX_BODY_BYTES = 4 * 1024;
const MIN_FILL_MS = 2500;
const CONSENT_VERSION = '2026-10-v1';

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

function cleanString(value, maxLength) {
  if (typeof value !== 'string') return '';
  return value.trim().slice(0, maxLength);
}

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === 'GET' && url.pathname === '/') {
      return json({ ok: true, service: 'earthdance-brevo-signup' });
    }

    const required = [
      'BREVO_API_KEY',
      'BREVO_DOI_TEMPLATE_ID',
      'BREVO_LIST_AUDIENCE',
      'BREVO_LIST_WAITLIST',
      'ALLOWED_ORIGIN',
      'CONFIRM_REDIRECT_URL',
    ];
    if (required.some((key) => !env[key])) {
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

    if (request.method !== 'POST' || url.pathname !== '/subscribe') {
      return json({ ok: false, error: 'Not found.' }, 404, cors);
    }

    const contentType = request.headers.get('content-type') || '';
    if (!contentType.toLowerCase().startsWith('application/json')) {
      return json({ ok: false, error: 'Expected JSON.' }, 415, cors);
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
      return json({ ok: false, error: 'Invalid request.' }, 400, cors);
    }

    // Bots: a filled honeypot or an instant submit gets a fake success so
    // they learn nothing, and nothing reaches Brevo.
    const filledTooFast = Number(body.elapsed_ms) < MIN_FILL_MS;
    if (cleanString(body.website, 200) || filledTooFast) {
      return json({ ok: true }, 200, cors);
    }

    const email = cleanString(body.email, 254).toLowerCase();
    if (!EMAIL_RE.test(email)) {
      return json({ ok: false, error: 'Please enter a valid email address.' }, 400, cors);
    }
    if (body.consent !== true) {
      return json({ ok: false, error: 'Please tick the box to join the list.' }, 400, cors);
    }

    const source = cleanString(body.source, 64).replace(/[^A-Za-z0-9._:/-]/g, '') || 'website';
    const firstName = cleanString(body.first_name, 80);

    const attributes = {
      SOURCE: source,
      CONSENT_DATE: new Date().toISOString().slice(0, 10),
      CONSENT_TEXT_VERSION: CONSENT_VERSION,
    };
    if (firstName) attributes.FIRSTNAME = firstName;

    const brevoResponse = await fetch('https://api.brevo.com/v3/contacts/doubleOptinConfirmation', {
      method: 'POST',
      headers: {
        'api-key': env.BREVO_API_KEY,
        'content-type': 'application/json',
        accept: 'application/json',
      },
      body: JSON.stringify({
        email,
        attributes,
        includeListIds: [Number(env.BREVO_LIST_AUDIENCE), Number(env.BREVO_LIST_WAITLIST)],
        templateId: Number(env.BREVO_DOI_TEMPLATE_ID),
        redirectionUrl: env.CONFIRM_REDIRECT_URL,
      }),
    });

    if (brevoResponse.ok) {
      return json({ ok: true }, 200, cors);
    }

    const detail = await brevoResponse.text();
    // An existing contact is not an error for the visitor, and we do not
    // confirm to the browser whether an address is already on the list.
    if (brevoResponse.status === 400 && /already/i.test(detail)) {
      return json({ ok: true }, 200, cors);
    }

    console.error('Brevo signup failed', brevoResponse.status, detail.slice(0, 500));
    return json(
      { ok: false, error: 'Something went wrong on our side. Please try again in a moment.' },
      502,
      cors
    );
  },
};
