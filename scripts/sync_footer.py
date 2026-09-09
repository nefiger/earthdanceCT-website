#!/usr/bin/env python3
"""Sync the shared footer (incl. the production-partners strip) into every
hand-authored static page. Generated pages (artists/vendors/stages/lineup
browser) already get this from build_artists.footer() at build time; the
static pages carry their own copy of the same markup, so this keeps them
from drifting.

Usage: python3 scripts/sync_footer.py
"""

from pathlib import Path

from build_artists import footer_partners

ROOT = Path(__file__).resolve().parent.parent

PAGES = [
    "about.html", "collaborators.html", "crew.html", "faq.html", "gallery.html",
    "gatherings.html", "glamping-camping.html", "history.html", "index.html",
    "love-in-a-bowl.html", "lineup.html", "practical-info.html",
    "prayer-for-peace.html", "privacy.html", "sustainability.html", "terms.html",
    "vendor-directory.html", "vendors.html", "volunteers.html",
]

MARKER_BEFORE = '    </div>\n    <div class="footer-fine">'


def sync() -> None:
    partners_html = footer_partners()
    updated = 0
    skipped = []
    for name in PAGES:
        path = ROOT / name
        text = path.read_text()
        if MARKER_BEFORE not in text:
            skipped.append(name)
            continue
        # Idempotent: drop any previously-synced strip before reinserting.
        if '<div class="footer-partners">' in text:
            start = text.index('<div class="footer-partners">')
            end = text.index(MARKER_BEFORE, start)
            text = text[:start] + text[end:]
        replacement = f'    </div>\n{partners_html}    <div class="footer-fine">'
        text = text.replace(MARKER_BEFORE, replacement, 1)
        path.write_text(text)
        updated += 1
    print(f"sync_footer — {updated} pages updated" + (f", {len(skipped)} skipped: {skipped}" if skipped else ""))


if __name__ == "__main__":
    sync()
