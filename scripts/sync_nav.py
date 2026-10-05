#!/usr/bin/env python3
"""Sync the shared header navigation (and the brand line) into every HTML page.

The nav is duplicated in each page (no build step), so this keeps them from
drifting. The canonical markup lives in build_artists.NAV_HTML. Pages that
carry no signup form (404, redirect stubs, the post-signup confirmation page)
get a nav button that points at the homepage form instead of a dead #join-list.

Usage: python3 scripts/sync_nav.py   (run after sync_footer.py)
"""

import re
import subprocess
from pathlib import Path

from build_artists import NAV_HTML

ROOT = Path(__file__).resolve().parent.parent
NAV_BLOCK = re.compile(r'    <nav id="site-nav" class="site-nav">.*?</nav>', re.DOTALL)
OLD_BRAND = "<span>earthdance<em>Cape Town 2026</em></span>"
NEW_BRAND = "<span>earthdance<em>Cape Town</em></span>"


def main() -> None:
    files = subprocess.check_output(["git", "ls-files", "*.html"], cwd=ROOT, text=True).split()
    updated = skipped = 0
    for name in files:
        path = ROOT / name
        text = path.read_text()
        if not NAV_BLOCK.search(text):
            skipped += 1
            continue
        nav = NAV_HTML
        if 'id="join-list"' not in text:
            nav = nav.replace('href="#join-list"', 'href="index.html#join-list"')
        new = NAV_BLOCK.sub(lambda m: nav, text, count=1).replace(OLD_BRAND, NEW_BRAND)
        if new != text:
            path.write_text(new)
            updated += 1
    print(f"sync_nav — {updated} pages updated, {skipped} without a nav block")


if __name__ == "__main__":
    main()
