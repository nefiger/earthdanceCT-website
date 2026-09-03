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

def act_markup(act: dict) -> str:
    name = html.escape(act["name"], quote=False)
    if act.get("country"):
        name += f'&nbsp;<span class="act-country">{html.escape(act["country"], quote=False)}</span>'
    if act.get("note"):
        name += f'&nbsp;<span class="act-note">{html.escape(act["note"], quote=False)}</span>'
    if act.get("profile"):
        profile_name = act.get("profile_label", act["name"])
        label = html.escape(f'View {profile_name} artist profile', quote=True)
        suffix = html.escape(act.get("profile_suffix", ""), quote=False)
        return f'              <li><a href="{act["profile"]}" aria-label="{label}">{name}</a>{suffix}</li>'
    return f"              <li>{name}</li>"


# Moments rather than artists: they belong to a stage's running order, not to
# an alphabetical index of who is playing.
NOT_ARTISTS = {"Opening ceremony", "Prayer for Peace link-up", "Opening DJ sets"}


def stage_card(stage: dict) -> str:
    acts = sum(
        1
        for b in stage["blocks"]
        for a in b["acts"]
        if a["name"] not in NOT_ARTISTS
    )
    return f"""        <div class="card photo-card">
          <img src="{stage["hero_image"]}" alt="{html.escape(stage["hero_alt"], quote=True)}" loading="lazy">
          <div class="photo-card-body">
            <h3>{stage["name"]}</h3>
            <p>{stage["lede"]}</p>
            <a class="card-link" href="{stage["page"]}">{acts} acts &middot; see the stage &rarr;</a>
          </div>
        </div>"""


def everyone(stages: list[dict]) -> list[dict]:
    """One entry per act across both stages, alphabetical."""
    seen = {}
    for stage in stages:
        for block in stage["blocks"]:
            for act in block["acts"]:
                if act["name"] in NOT_ARTISTS:
                    continue
                seen.setdefault(act["name"], act)
    return sorted(seen.values(), key=lambda a: a["name"].lower().removeprefix("the "))


def main() -> None:
    data = json.loads(DATA.read_text())
    stages = data["stages"]
    out = []

    intro = data["intro"]
    out.append(f'  <section class="section section-tint" id="{intro["id"]}">')
    out.append('    <div class="container">')
    out.append(f'      <span class="eyebrow">{intro["eyebrow"]}</span>')
    out.append(f'      <h2>{intro["heading"]}</h2>')
    out.append(f'      <p class="bright">{intro["body"]}</p>')
    out.append('      <div class="card-grid stage-cards">')
    out += [stage_card(s) for s in stages]
    out.append("      </div>")
    out.append("    </div>")
    out.append("  </section>")
    out.append("")

    acts = everyone(stages)
    out.append('  <section class="section" id="artist-list">')
    out.append('    <div class="container">')
    out.append('      <span class="eyebrow">Everyone announced</span>')
    out.append(f'      <h2>The full list <span class="act-count">{len(acts)} acts</span></h2>')
    out.append(
        '      <p class="bright">Every act confirmed so far, across both stages. '
        "Playing order lives on each stage's own page.</p>"
    )
    out.append('      <ul class="act-index">')
    out += [act_markup(a) for a in acts]
    out.append("      </ul>")
    out.append("    </div>")
    out.append("  </section>")
    out.append("")

    page = PAGE.read_text()
    before = page.split(START)[0]
    after = page.split(END, 1)[1]
    PAGE.write_text(before + START + "\n" + "\n".join(out) + END + after)

    print(f"lineup.html — {len(acts)} acts, {len(stages)} stage cards")


if __name__ == "__main__":
    main()
