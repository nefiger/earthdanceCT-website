#!/usr/bin/env python3
"""Sync the shared footer (incl. the production-partners strip) into every
hand-authored static page. Generated pages (artists/vendors/stages/lineup
browser) already get this from build_artists.footer() at build time; the
static pages carry their own copy of the same markup, so this keeps them
from drifting.

Usage: python3 scripts/sync_footer.py
"""

import re
from pathlib import Path

from build_artists import SIGNUP_END, SIGNUP_START, footer_partners, footer_signup, signup_form

ROOT = Path(__file__).resolve().parent.parent

PAGES = [
    "about.html", "collaborators.html", "crew.html", "faq.html", "gallery.html",
    "gatherings.html", "glamping-camping.html", "history.html", "index.html",
    "love-in-a-bowl.html", "lineup.html", "practical-info.html",
    "prayer-for-peace.html", "privacy.html", "sustainability.html", "terms.html",
    "vendor-directory.html", "vendors.html", "subscribed.html", "volunteers.html",
]

GRID_END_TO_FINE = re.compile(
    r'(</ul>\n      </div>\n    </div>\n)(.*?)(    <div class="footer-fine">)', re.DOTALL
)
HOME_FORM = re.compile(r'(<!-- home-signup:start -->).*?(<!-- home-signup:end -->)', re.DOTALL)
# Pages that must not carry the signup strip (the visitor has just signed up).
NO_SIGNUP = {'subscribed.html'}
FOOTER_OPEN = '<footer class="site-footer">\n  <div class="container">\n'
SIGNUP_BLOCK = re.compile(r'[ ]*' + re.escape(SIGNUP_START) + r'.*?' + re.escape(SIGNUP_END) + r'\n', re.DOTALL)
GRID_OPEN = re.compile(r'^[ ]*<div class="footer-grid">', re.MULTILINE)


def sync() -> None:
    partners_html = footer_partners()
    updated = 0
    skipped = []
    for name in PAGES:
        path = ROOT / name
        full = path.read_text()
        signup_html = footer_signup(anchor=(name != 'index.html'))
        # Only ever touch the footer: the anchor pattern also occurs in page bodies.
        head, sep, text = full.partition('<footer class="site-footer">')
        text = sep + text
        if FOOTER_OPEN not in text or not GRID_END_TO_FINE.search(text):
            skipped.append(name)
            continue
        # Rebuild everything between the end of the footer grid and the fine
        # print from scratch. Earlier versions of this script accumulated stray
        # </div> tags and duplicate partner strips; this makes every run idempotent.
        text = GRID_END_TO_FINE.sub(lambda m: m.group(1) + partners_html + m.group(3), text, count=1)
        text = SIGNUP_BLOCK.sub('', text)
        text = GRID_OPEN.sub('    <div class="footer-grid">', text, count=1)
        if name not in NO_SIGNUP:
            text = text.replace(FOOTER_OPEN, FOOTER_OPEN + '    ' + signup_html, 1)
        text = head + text
        if name == 'index.html':
            text = HOME_FORM.sub(lambda m: m.group(1) + '\n        ' + signup_form('home') + '\n        ' + m.group(2), text)
        path.write_text(text)
        updated += 1
    print(f"sync_footer — {updated} pages updated" + (f", {len(skipped)} skipped: {skipped}" if skipped else ""))


if __name__ == "__main__":
    sync()
