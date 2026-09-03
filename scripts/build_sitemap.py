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

# Not indexable: error page, private campaign pages, and the journey.html
# redirect stub kept for old links.
EXCLUDE = {"404.html", "journey.html", "homecoming-6f1b92.html"}

# Anything unlisted defaults to 0.6. Artist profile pages use 0.7 below.
PRIORITY = {
    "index.html": "1.0",
    "lineup.html": "0.9",
    "glamping-camping.html": "0.9",
    "about.html": "0.8",
    "gatherings.html": "0.8",
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
    "gatherings.html": "weekly",
    "glamping-camping.html": "weekly",
    "faq.html": "weekly",
    "practical-info.html": "weekly",
    "privacy.html": "yearly",
    "terms.html": "yearly",
    "history.html": "yearly",
}


def relative_name(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def lastmod(path: Path) -> str:
    out = subprocess.run(
        ["git", "log", "-1", "--format=%cs", "--", relative_name(path)],
        cwd=ROOT, capture_output=True, text=True,
    ).stdout.strip()
    return out or date.today().isoformat()


def loc(path: Path) -> str:
    name = relative_name(path)
    if name == "index.html":
        return BASE
    if name.startswith(("artists/", "stages/")) and name.endswith("/index.html"):
        return BASE + name.removesuffix("index.html")
    return BASE + name


def priority(path: Path) -> str:
    name = relative_name(path)
    if name.startswith("stages/"):
        return "0.8"
    if name.startswith("artists/"):
        return "0.7"
    return PRIORITY.get(name, "0.6")


def changefreq(path: Path) -> str:
    name = relative_name(path)
    if name.startswith(("artists/", "stages/")):
        return "monthly"
    return CHANGEFREQ.get(name, "monthly")


def main() -> None:
    pages = [p for p in ROOT.glob("*.html") if p.name not in EXCLUDE]
    pages += sorted((ROOT / "artists").glob("*/index.html"))
    pages += sorted((ROOT / "stages").glob("*/index.html"))
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    # Home first, then the rest alphabetically.
    pages.sort(key=lambda p: (relative_name(p) != "index.html", relative_name(p)))
    for page in pages:
        lines += [
            "  <url>",
            f"    <loc>{loc(page)}</loc>",
            f"    <lastmod>{lastmod(page)}</lastmod>",
            f"    <changefreq>{changefreq(page)}</changefreq>",
            f"    <priority>{priority(page)}</priority>",
            "  </url>",
        ]
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n")
    print(f"sitemap.xml — {len(pages)} URLs")


if __name__ == "__main__":
    main()
