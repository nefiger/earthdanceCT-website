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

# Editorial copy keyed on the section id in the JSON.
BLURB = {
    "announced-artists": (
        "The lineup so far",
        "These artists are confirmed for Earthdance Cape Town 2026. Stage details "
        "and set times will be shared closer to the festival.",
    ),
}


def act_markup(act: dict) -> str:
    name = html.escape(act["name"], quote=False)
    if act.get("country"):
        name += f'&nbsp;<span class="act-country">{html.escape(act["country"], quote=False)}</span>'
    if act.get("profile"):
        profile_name = act.get("profile_label", act["name"])
        label = html.escape(f'View {profile_name} artist profile', quote=True)
        suffix = html.escape(act.get("profile_suffix", ""), quote=False)
        return f'              <li><a href="{act["profile"]}" aria-label="{label}">{name}</a>{suffix}</li>'
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
            coming = block.get("status") == "coming"
            if coming:
                tag = "To be announced"
            elif block.get("kind") == "programme":
                tag = f'{len(block["items"])} strands'
            else:
                tag = f'{len(block["acts"])} acts'
            out.append(
                f'      <h3 class="act-heading" id="{block["id"]}">{block["name"]}'
                f' <span class="act-count">{tag}</span></h3>'
            )
            if coming:
                out.append(f'      <p class="act-holding">{block["holding"]}</p>')
                items = block.get("items") or []
                if items:
                    out.append('      <ul class="act-index act-index-quiet">')
                    out += [f"              <li>{i}</li>" for i in items]
                    out.append("      </ul>")
            elif block.get("kind") == "programme":
                out.append('      <ul class="act-index">')
                out += [f"              <li>{i}</li>" for i in block["items"]]
                out.append("      </ul>")
            else:
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

    total = sum(len(b.get("acts", [])) for a in data["stages"] for b in a["blocks"])
    print(f"lineup.html — {total} acts across {len(data['stages'])} stages")


if __name__ == "__main__":
    main()
