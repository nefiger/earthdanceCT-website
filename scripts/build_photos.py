#!/usr/bin/env python3
"""Build web-optimised gallery assets from the 2025 photo archive.

- Dedupes identical files by content hash ("Copy of ..." duplicates at the
  archive root are the main case).
- Preserves photographer credit: folder name wins; loose BLF-named files at
  the root are credited to BEELEAF Photography; anything else uncredited is
  kept under "Photographer TBC" rather than dropped.
- Excludes phone-gallery screenshots (Screenshot_*.jpg) and the stray
  20241103_111450.jpg which predates the 2025 event.
- Emits 1600px web images + 520px thumbnails via sips, and a manifest
  (assets/js/photos-data.js + assets/photos/manifest.json).

Run from anywhere: python3 scripts/build_photos.py [SOURCE_DIR]
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else \
    "/Users/nefiger/projects/earthdance-2026/assets/social/raw/PHOTOS 2025"

WEB_DIR = os.path.join(REPO, "assets", "photos", "web")
THUMB_DIR = os.path.join(REPO, "assets", "photos", "thumbs")
WEB_MAX, THUMB_MAX = 1600, 520
WEB_Q, THUMB_Q = 78, 70

CREDITS = {
    "Alison Swan Photograhpy Earth Dance 2025":
        ("alison-swan", "Alison Swan Photography"),
    "BEELEAF Photography": ("beeleaf", "BEELEAF Photography"),
    "JACO BREWER": ("jaco-brewer", "Jaco Brewer"),
    "Tamia Visagie": ("tamia-visagie", "Tamia Visagie"),
}
ROOT_BEELEAF = re.compile(r"BLF|Earthdance CT_2025")
UNCREDITED = ("uncredited", "Photographer TBC")
EXCLUDE = re.compile(r"^(Screenshot_|20241103_111450)")


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def collect():
    """Return {hash: chosen source path}, preferring folder > root > copy-of."""

    def rank(rel):
        base = os.path.basename(rel)
        if os.sep in rel:
            return 0  # inside a photographer folder
        return 2 if base.startswith("Copy of ") else 1

    chosen = {}
    for root, _, files in os.walk(SRC):
        for name in sorted(files):
            if not name.lower().endswith((".jpg", ".jpeg")):
                continue
            rel = os.path.relpath(os.path.join(root, name), SRC)
            if EXCLUDE.match(os.path.basename(rel)):
                continue
            digest = md5(os.path.join(SRC, rel))
            if digest not in chosen or rank(rel) < rank(chosen[digest]):
                chosen[digest] = rel
    return chosen


def credit_for(rel):
    top = rel.split(os.sep)[0] if os.sep in rel else None
    if top in CREDITS:
        return CREDITS[top]
    if ROOT_BEELEAF.search(os.path.basename(rel)):
        return CREDITS["BEELEAF Photography"]
    return UNCREDITED


def slugify(name):
    stem = os.path.splitext(name)[0]
    stem = re.sub(r"^Copy of ", "", stem)
    stem = re.sub(r"[{}()\[\]]", "", stem)
    stem = re.sub(r"[^A-Za-z0-9]+", "-", stem).strip("-").lower()
    return stem or "photo"


def sips(src, dest, max_px, quality):
    subprocess.run(
        ["sips", "--resampleHeightWidthMax", str(max_px),
         "-s", "format", "jpeg", "-s", "formatOptions", str(quality),
         src, "--out", dest],
        check=True, capture_output=True)


def dims(path):
    out = subprocess.run(
        ["sips", "-g", "pixelWidth", "-g", "pixelHeight", path],
        check=True, capture_output=True, text=True).stdout
    w = int(re.search(r"pixelWidth: (\d+)", out).group(1))
    h = int(re.search(r"pixelHeight: (\d+)", out).group(1))
    return w, h


def natural_key(s):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s.lower())]


def main():
    chosen = collect()
    groups = {}  # slug -> {display, photos: [rel...]}
    for rel in chosen.values():
        slug, display = credit_for(rel)
        groups.setdefault(slug, {"display": display, "rels": []})["rels"].append(rel)

    jobs, manifest = [], {"credits": []}
    order = ["alison-swan", "beeleaf", "tamia-visagie", "jaco-brewer", "uncredited"]
    for slug in [s for s in order if s in groups]:
        g = groups[slug]
        os.makedirs(os.path.join(WEB_DIR, slug), exist_ok=True)
        os.makedirs(os.path.join(THUMB_DIR, slug), exist_ok=True)
        photos = []
        for i, rel in enumerate(sorted(g["rels"],
                                       key=lambda r: natural_key(os.path.basename(r))), 1):
            fname = f"{slug}-{i:03d}-{slugify(os.path.basename(rel))}.jpg"
            src = os.path.join(SRC, rel)
            web = os.path.join(WEB_DIR, slug, fname)
            thumb = os.path.join(THUMB_DIR, slug, fname)
            jobs.append((src, web, WEB_MAX, WEB_Q))
            jobs.append((src, thumb, THUMB_MAX, THUMB_Q))
            photos.append({"file": f"{slug}/{fname}", "source": rel})
        manifest["credits"].append(
            {"slug": slug, "display": g["display"], "photos": photos})

    print(f"{sum(len(c['photos']) for c in manifest['credits'])} unique photos "
          f"from {len(jobs) // 2 and len(chosen)} chosen files; converting...")
    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(lambda j: sips(*j), jobs))

    for c in manifest["credits"]:
        for p in c["photos"]:
            w, h = dims(os.path.join(THUMB_DIR, p["file"]))
            p["w"], p["h"] = w, h

    os.makedirs(os.path.join(REPO, "assets", "js"), exist_ok=True)
    with open(os.path.join(REPO, "assets", "photos", "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    with open(os.path.join(REPO, "assets", "js", "photos-data.js"), "w") as f:
        f.write("const PHOTO_MANIFEST = ")
        json.dump(manifest, f, separators=(",", ":"))
        f.write(";\n")
    for c in manifest["credits"]:
        print(f"  {c['display']}: {len(c['photos'])} photos")
    print("done")


if __name__ == "__main__":
    main()
