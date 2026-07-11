# Earthdance Cape Town 2026 — website

Static site for [Earthdance Cape Town 2026](https://earthdancecapetown.co.za) (18–20 September 2026, Kromrivier Farm). No build step — plain HTML/CSS/JS, deployable on GitHub Pages or any static host.

**Status: go-live prep.** Public pages are ready to publish from a content/layout point of view. Remaining launch work is analytics setup and final confirmation of a few operational details that are currently worded as "closer to the event" rather than hard promises.

## Pages

| Page | File | Copy source |
|---|---|---|
| Home | `index.html` | website-copy-draft (adapted, expanded) |
| About Earthdance | `about.html` | drafted from storytelling-reset guidance + live-site history |
| Journey to September | `journey.html` | website-copy-draft + warm-ups merged in |
| Heart at Love in a Bowl | `love-in-a-bowl.html` | drafted; grounded in loveinabowl.co.za + Heart recap material |
| Prayer for Peace | `prayer-for-peace.html` | drafted from storytelling-reset guidance + live-site history |
| Vendors | `vendors.html` | website-copy-draft + confirmed packages table |
| Volunteers | `volunteers.html` | website-copy-draft |
| Collaborators | `collaborators.html` | drafted (programming/EOI pathway) |
| Glamping & Camping | `glamping-camping.html` | confirmed 2026 accommodation range (six options) |
| Practical Info | `practical-info.html` | drafted from live-site facts |
| FAQ | `faq.html` | drafted, slimmed per storytelling-reset |
| Sustainability & Waste | `sustainability.html` | drafted from policy brief |
| Gallery | `gallery.html` | curated subset from photo manifest |

Source docs live in the `earthdance-2026` planning repo under `docs/comms/`:
`website-copy-draft-2026-06-21.md` and `website-storytelling-reset-2026-06-21.md`.

## Assets

- `assets/brand/` — logo, wordmark, banners, favicon (web-sized renditions of `earthdance-2026/brand/`).
- `assets/fonts/` — Danube (regular + bold), the Earthdance display face, self-hosted via `@font-face`.
- `assets/photos/web|thumbs/` — a curated subset (~124) of the 656 deduped 2025 photos, interleaved across photographers. Credits are preserved subtly (hover caption + lightbox line), not featured. `scripts/curated-list.txt` records the selection; `assets/js/photos-data.js` is the gallery data.
- `assets/photos/heart/` — Heart gathering photos (Love in a Bowl, 20 June 2026).
- `assets/photos/stay/` — glamping tent photos for the accommodation page.
- `scripts/build_photos.py` — regenerates the full deduped archive from `earthdance-2026/assets/social/raw/PHOTOS 2025` (macOS: uses `sips`); re-run when more photos arrive, then re-prune to the curated list.

## Updating content

Header and footer are duplicated in each page (deliberately — no build step). If you change nav or footer, change it in all pages: `grep -l 'site-nav' *.html`.

Known soft-detail items that still depend on final operational confirmation:

- Humanity warm-up announcement details (`journey.html`, `faq.html`, `index.html`)
- Prayer for Peace surrounding local running order (`prayer-for-peace.html`) — exact global linkup time now confirmed
- Accommodation arrival/check-in guidance (`glamping-camping.html`) — pricing and booking are live on Quicket; Morado Cottage removed for now, may return
- Volunteer exchange/shift structure (`volunteers.html`)
- Collaborator exchange terms (`collaborators.html`)
- Bin locations / refill points (`sustainability.html`)
- Site facilities / re-entry / shuttles (`practical-info.html`)

## Go-live checklist

1. Point the real domain at the host and add `CNAME` if using GitHub Pages.
2. Add analytics/tracking only once the final tool choice and consent approach are settled.
3. Add canonical URLs once the final domain is confirmed.
4. Confirm the remaining soft-detail items as operations lock in, or leave the current "closer to the event" wording in place.
