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
