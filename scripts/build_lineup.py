#!/usr/bin/env python3
"""Render the lineup sections in lineup.html from assets/data/lineup.json.

Usage: python3 scripts/build_lineup.py

Edit the JSON, run this, commit both. The generated markup is written
between the LINEUP:START and LINEUP:END markers in lineup.html; nothing
outside those markers is touched.

Each act may carry an optional "country" (rendered after the name) and an
optional "profile" (a page path). Acts with a profile render as links, so
per-artist pages can be added later without changing this script.
"""

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "assets/data/lineup.json"
PAGE = ROOT / "lineup.html"
START, END = "<!-- LINEUP:START -->", "<!-- LINEUP:END -->"

# Per-stage editorial copy. Keyed on the stage id in the JSON.
BLURB = {
    "sonic-horizon": (
        "The kinetic heart of the weekend",
        "Sonic Horizon carries the festival's stronger pulse: psytrance from the "
        "early sets through to the sunrise, and the stage most people mean when they "
        "talk about the Earthdance dancefloor. It is also where the global "
        "<a href=\"prayer-for-peace.html\">Prayer for Peace</a> lands at 01:00 on "
        "Saturday, when the music stops and the whole gathering links up with "
        "Earthdance communities around the world.",
    ),
    "mellow-meadow": (
        "Soft by day, taken over by night",
        "Through the daylight hours Mellow Meadow is the gentler side of the "
        "gathering — workshops, ceremony, slower moments and the central sacred fire. "
        "After dark it changes character entirely, handing the space first to a "
        "techno takeover and then to drum &amp; bass. Same stretch of grass, a "
        "completely different night.",
    ),
}


def act_markup(act: dict) -> str:
    name = html.escape(act["name"], quote=False)
    if act.get("country"):
        name += f' <span class="act-country">{html.escape(act["country"], quote=False)}</span>'
    if act.get("profile"):
        return f'              <li><a href="{act["profile"]}">{name}</a></li>'
    return f"              <li>{name}</li>"


def main() -> None:
    data = json.loads(DATA.read_text())
    out = []
    for i, stage in enumerate(data["stages"]):
        heading, body = BLURB[stage["id"]]
        tint = " section-tint" if i % 2 == 0 else ""
        out.append(f'  <section class="section{tint}" id="{stage["id"]}">')
        out.append('    <div class="container">')
        out.append(f'      <span class="eyebrow">{stage["name"]}</span>')
        out.append(f"      <h2>{heading}</h2>")
        out.append(f'      <p class="bright">{body}</p>')
        for block in stage["blocks"]:
            count = len(block["acts"])
            out.append(
                f'      <h3 class="act-heading">{block["name"]}'
                f' <span class="act-count">{count} acts</span></h3>'
            )
            out.append('      <ul class="act-index">')
            out += [act_markup(a) for a in block["acts"]]
            out.append("      </ul>")
        out.append("    </div>")
        out.append("  </section>")
        out.append("")

    page = PAGE.read_text()
    before = page.split(START)[0]
    after = page.split(END, 1)[1]
    PAGE.write_text(before + START + "\n" + "\n".join(out) + END + after)

    total = sum(len(b["acts"]) for a in data["stages"] for b in a["blocks"])
    print(f"lineup.html — {total} acts across {len(data['stages'])} stages")


if __name__ == "__main__":
    main()
