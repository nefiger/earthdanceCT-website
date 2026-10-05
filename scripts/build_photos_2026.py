#!/usr/bin/env python3
"""Build the curated 2026 gallery set from the photographers' source folders.

Source folders (not in the repo) sit under SOURCE_DIR, e.g. ~/Downloads:
  "Kayflow Earthdance 2026", "Earthdance " (Kayflow's, overlaps the first) and
  "Main Event Pics 2026" (phone photos: Samsung SM-G950F is Mike Aldridge,
  SM-G996B is Christo).

Writes web (1800px) and thumb (520px) JPEGs to assets/photos/2026/ and the
gallery data file assets/js/photos-2026-data.js. Every output is re-encoded
without metadata: the phone originals carry GPS coordinates, which must never
be published. Credits stay subtle (hover caption + lightbox line), as for 2025.

Usage: python3 scripts/build_photos_2026.py [SOURCE_DIR]   (default ~/Downloads)
Needs Pillow.
"""

import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/photos/2026"
DATA = ROOT / "assets/js/photos-2026-data.js"
WEB_EDGE, THUMB_EDGE = 1800, 520

CREDITS = {
    "Kayflow": "Kayflow",
    "Mike Aldridge": "Mike Aldridge",
    "Christo": "Christo",
}

# (photographer, source folder, source file) in display order.
SELECTION = [
    ('Kayflow', 'Kayflow Earthdance 2026', 'IMG_8931.JPG'),
    ('Mike Aldridge', 'Main Event Pics 2026', '20260919_181013.jpg'),
    ('Christo', 'Main Event Pics 2026', '20260919_074552.jpg'),
    ('Kayflow', 'Kayflow Earthdance 2026', 'IMG_8977.JPG'),
    ('Kayflow', 'Kayflow Earthdance 2026', 'IMG_8987.JPG'),
    ('Mike Aldridge', 'Main Event Pics 2026', '20260920_014716.jpg'),
    ('Christo', 'Main Event Pics 2026', '20260919_093418.jpg'),
    ('Kayflow', 'Kayflow Earthdance 2026', 'IMG_9054.JPG'),
    ('Mike Aldridge', 'Main Event Pics 2026', '20260920_021136.jpg'),
    ('Kayflow', 'Kayflow Earthdance 2026', 'IMG_9033.JPG'),
    ('Christo', 'Main Event Pics 2026', '20260919_093512.jpg'),
    ('Kayflow', 'Kayflow Earthdance 2026', 'IMG_9057.JPG'),
    ('Mike Aldridge', 'Main Event Pics 2026', '20260920_113957.jpg'),
    ('Kayflow', 'Kayflow Earthdance 2026', 'IMG_9082.JPG'),
    ('Christo', 'Main Event Pics 2026', '20260919_120018.jpg'),
    ('Kayflow', 'Kayflow Earthdance 2026', 'IMG_9096.JPG'),
    ('Mike Aldridge', 'Main Event Pics 2026', '20260920_121211.jpg'),
    ('Kayflow', 'Kayflow Earthdance 2026', 'IMG_9106.JPG'),
    ('Mike Aldridge', 'Main Event Pics 2026', '20260920_121234.jpg'),
    ('Kayflow', 'Kayflow Earthdance 2026', 'IMG_9129.JPG'),
    ('Christo', 'Main Event Pics 2026', '20260919_151514.jpg'),
    ('Kayflow', 'Kayflow Earthdance 2026', 'IMG_9132.JPG'),
    ('Mike Aldridge', 'Main Event Pics 2026', '20260920_121307.jpg'),
    ('Kayflow', 'Kayflow Earthdance 2026', 'IMG_9157.JPG'),
    ('Christo', 'Main Event Pics 2026', '20260919_154642.jpg'),
    ('Kayflow', 'Kayflow Earthdance 2026', 'IMG_9198.JPG'),
    ('Mike Aldridge', 'Main Event Pics 2026', '20260920_121309.jpg'),
    ('Kayflow', 'Kayflow Earthdance 2026', 'IMG_9221.JPG'),
    ('Christo', 'Main Event Pics 2026', '20260920_115741.jpg'),
    ('Kayflow', 'Kayflow Earthdance 2026', 'IMG_9234.JPG'),
    ('Mike Aldridge', 'Main Event Pics 2026', '20260920_121317.jpg'),
    ('Kayflow', 'Kayflow Earthdance 2026', 'IMG_9255.JPG'),
    ('Mike Aldridge', 'Main Event Pics 2026', '20260920_121332.jpg'),
    ('Kayflow', 'Kayflow Earthdance 2026', 'IMG_9292.JPG'),
    ('Christo', 'Main Event Pics 2026', '20260920_143331.jpg'),
    ('Kayflow', 'Kayflow Earthdance 2026', 'IMG_9280.JPG'),
    ('Mike Aldridge', 'Main Event Pics 2026', '20260920_121339.jpg'),
    ('Kayflow', 'Kayflow Earthdance 2026', 'IMG_9305.JPG'),
    ('Christo', 'Main Event Pics 2026', '20260920_143332.jpg'),
    ('Kayflow', 'Earthdance ', 'IMG_9126.JPG'),
    ('Mike Aldridge', 'Main Event Pics 2026', '20260920_121437.jpg'),
    ('Kayflow', 'Earthdance ', 'IMG_9163.JPG'),
    ('Christo', 'Main Event Pics 2026', '20260920_143346.jpg'),
    ('Mike Aldridge', 'Main Event Pics 2026', '20260920_121442.jpg'),
    ('Kayflow', 'Earthdance ', 'IMG_9200.JPG'),
]


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def save(im: Image.Image, path: Path, edge: int, quality: int) -> tuple[int, int]:
    im = im.copy()
    im.thumbnail((edge, edge), Image.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Saving a fresh Image drops EXIF/GPS: do not pass exif= here.
    im.convert("RGB").save(path, "JPEG", quality=quality, optimize=True, progressive=True)
    return im.size


def main() -> None:
    source = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path.home() / "Downloads"
    photos, counters = [], {}
    for who, folder, name in SELECTION:
        counters[who] = counters.get(who, 0) + 1
        out_name = f"{slug(who)}-{counters[who]:03d}.jpg"
        rel = f"{slug(who)}/{out_name}"
        with Image.open(source / folder / name) as raw:
            im = ImageOps.exif_transpose(raw)
            save(im, OUT / "web" / rel, WEB_EDGE, 82)
            w, h = save(im, OUT / "thumbs" / rel, THUMB_EDGE, 78)
        photos.append({"file": rel, "w": w, "h": h, "credit": CREDITS[who]})
    DATA.write_text("const PHOTOS_2026 = " + json.dumps(photos, ensure_ascii=False) + ";\n")
    print(f"{len(photos)} photos -> {OUT}")


if __name__ == "__main__":
    main()
