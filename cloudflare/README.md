# Earthdance Meta Conversions API Worker

This Worker securely forwards approved website events to Meta's Conversions API.
The website remains hosted on GitHub Pages; the Meta access token lives only in
Cloudflare.

## Cloudflare bindings

- `META_ACCESS_TOKEN` — secret
- `META_PIXEL_ID` — text, `3564053623773252`
- `ALLOWED_ORIGIN` — text, `https://www.earthdancecapetown.co.za`
- `META_TEST_EVENT_CODE` — optional secret used temporarily during Meta Test Events

The dashboard Worker code is stored in `meta-capi-worker.mjs`.

`Purchase` requests are accepted with or without `META_TEST_EVENT_CODE`. When
the test code is present, Meta routes them to Test Events; without it, they are
production events. Confirmed purchase tracking should be sent by a trusted
Quicket webhook or other server-to-server integration.

# Earthdance waiting-list signup Worker

`brevo-signup-worker.mjs` receives the footer signup form (`form[data-signup]`,
handled in `assets/js/site.js`) and creates a Brevo contact through Brevo's
**double opt-in** endpoint, so every contact has confirmed their address. The
Brevo API key lives only in Cloudflare.

Endpoint: `POST /subscribe` (JSON: `email`, `first_name`, `consent`, `source`,
`website` honeypot, `elapsed_ms`). Deploy it as a Worker named
`earthdance-brevo-signup` so the URL matches `site.js`.

## Cloudflare bindings

- `BREVO_API_KEY` — secret
- `BREVO_DOI_TEMPLATE_ID` — text, id of the Brevo double opt-in email template
- `BREVO_LIST_AUDIENCE` — text, id of the "Earthdance Audience" list
- `BREVO_LIST_WAITLIST` — text, id of the "2027 Waiting list" list
- `ALLOWED_ORIGIN` — text, `https://www.earthdancecapetown.co.za`
- `CONFIRM_REDIRECT_URL` — text, where the confirmation link lands

## Brevo setup

Contact attributes (create these first or Brevo rejects the call): `SOURCE`
(text), `CONSENT_DATE` (date), `CONSENT_TEXT_VERSION` (text). `FIRSTNAME` is
built in. The double opt-in template must be tagged `optin` and contain the
confirmation link as `{{ doubleoptin }}` (start from Brevo's "Default Template
Double opt-in confirmation" in Campaigns > Templates). Change `CONSENT_VERSION` in the Worker whenever the
consent wording in `scripts/build_artists.py` (`footer_signup`) changes, then
re-run `scripts/sync_footer.py` and the page builders.
