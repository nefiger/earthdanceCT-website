#!/usr/bin/env python3
"""Build the "Through the Years" gallery band from the past-events archive.

Source images come from the Earthdance Drive folder "PAST EVENTS PICS" —
Facebook exports with no photographer metadata and no year labels, many
carrying their own watermark. They go up uncredited by decision; do not
invent credits for them.

Dedupes by content hash, emits 1600px web images + 520px thumbnails via
sips (macOS), and writes assets/js/past-photos-data.js.

Run: python3 scripts/build_past_photos.py SOURCE_DIR
"""
import hashlib
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else None
WEB_DIR = os.path.join(REPO, "assets", "photos", "past", "web")
THUMB_DIR = os.path.join(REPO, "assets", "photos", "past", "thumbs")
WEB_MAX, THUMB_MAX = 1600, 520
WEB_Q, THUMB_Q = 78, 70


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dims(path):
    out = subprocess.run(
        ["sips", "-g", "pixelWidth", "-g", "pixelHeight", path],
        capture_output=True, text=True,
    ).stdout
    w = h = 0
    for line in out.splitlines():
        if "pixelWidth:" in line:
            w = int(line.split(":")[1])
        elif "pixelHeight:" in line:
            h = int(line.split(":")[1])
    return w, h


def resize(src, dst, longest, quality):
    subprocess.run(
        ["sips", "-s", "format", "jpeg", "-s", "formatOptions", str(quality),
         "-Z", str(longest), src, "--out", dst],
        capture_output=True,
    )


def main():
    if not SRC or not os.path.isdir(SRC):
        sys.exit("usage: build_past_photos.py SOURCE_DIR")
    os.makedirs(WEB_DIR, exist_ok=True)
    os.makedirs(THUMB_DIR, exist_ok=True)

    seen, srcs = set(), []
    for name in sorted(os.listdir(SRC)):
        path = os.path.join(SRC, name)
        if not os.path.isfile(path):
            continue
        digest = md5(path)
        if digest in seen:
            continue
        seen.add(digest)
        srcs.append(path)

    def build(i_path):
        i, path = i_path
        slug = f"past-{i:03d}.jpg"
        web = os.path.join(WEB_DIR, slug)
        thumb = os.path.join(THUMB_DIR, slug)
        resize(path, web, WEB_MAX, WEB_Q)
        resize(path, thumb, THUMB_MAX, THUMB_Q)
        w, h = dims(thumb)
        return {"file": slug, "w": w, "h": h}

    with ThreadPoolExecutor(max_workers=8) as pool:
        photos = list(pool.map(build, enumerate(srcs, 1)))

    photos = [p for p in photos if p["w"] and p["h"]]
    out = os.path.join(REPO, "assets", "js", "past-photos-data.js")
    with open(out, "w") as f:
        f.write("const PAST_PHOTOS = " + json.dumps(photos, separators=(",", ":")) + ";\n")
    print(f"{len(photos)} past photos ({len(srcs)} unique of {len(os.listdir(SRC))} source files)")


if __name__ == "__main__":
    main()
