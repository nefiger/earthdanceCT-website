#!/usr/bin/env python3
"""Regenerate sitemap.xml from the HTML pages in the repo root.

Usage: python3 scripts/build_sitemap.py

lastmod comes from the file's most recent git commit date, so re-run this
after content changes and commit the result alongside them. Pages listed in
EXCLUDE never appear in the sitemap; everything else in the repo root is
included automatically, so new pages need no edit here beyond an optional
priority hint.
"""

import subprocess
from datetime import date
from pathlib import Path

BASE = "https://www.earthdancecapetown.co.za/"
ROOT = Path(__file__).resolve().parent.parent

# Not indexable: error page.
EXCLUDE = {"404.html"}

# Anything unlisted defaults to 0.6.
PRIORITY = {
    "index.html": "1.0",
    "glamping-camping.html": "0.9",
    "about.html": "0.8",
    "journey.html": "0.8",
    "practical-info.html": "0.8",
    "faq.html": "0.7",
    "vendors.html": "0.7",
    "volunteers.html": "0.7",
    "love-in-a-bowl.html": "0.7",
    "prayer-for-peace.html": "0.7",
    "privacy.html": "0.3",
    "terms.html": "0.3",
}

CHANGEFREQ = {
    "index.html": "weekly",
    "journey.html": "weekly",
    "glamping-camping.html": "weekly",
    "faq.html": "weekly",
    "practical-info.html": "weekly",
    "privacy.html": "yearly",
    "terms.html": "yearly",
    "history.html": "yearly",
}


def lastmod(path: Path) -> str:
    out = subprocess.run(
        ["git", "log", "-1", "--format=%cs", "--", path.name],
        cwd=ROOT, capture_output=True, text=True,
    ).stdout.strip()
    return out or date.today().isoformat()


def loc(name: str) -> str:
    return BASE if name == "index.html" else BASE + name


def main() -> None:
    pages = sorted(p for p in ROOT.glob("*.html") if p.name not in EXCLUDE)
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    # Home first, then the rest alphabetically.
    pages.sort(key=lambda p: (p.name != "index.html", p.name))
    for page in pages:
        lines += [
            "  <url>",
            f"    <loc>{loc(page.name)}</loc>",
            f"    <lastmod>{lastmod(page)}</lastmod>",
            f"    <changefreq>{CHANGEFREQ.get(page.name, 'monthly')}</changefreq>",
            f"    <priority>{PRIORITY.get(page.name, '0.6')}</priority>",
            "  </url>",
        ]
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n")
    print(f"sitemap.xml — {len(pages)} URLs")


if __name__ == "__main__":
    main()
