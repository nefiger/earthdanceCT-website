#!/usr/bin/env python3
"""Generate a page per stage from assets/data/lineup.json.

Usage: python3 scripts/build_stages.py

Each stage is written to stages/<id>/index.html. Copy (lede, story, hero image)
lives in the JSON alongside the acts, so a stage page and the lineup page never
drift apart. Set times are deliberately not rendered here: they live in
schedule.json and are not published yet.
"""

import html
import json
from pathlib import Path

from build_artists import esc, footer, header


def plain(text: str) -> str:
    """Copy carries inline HTML entities; meta tags and schema want the words."""
    return html.unescape(text)

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "assets/data/lineup.json"
ARTISTS = ROOT / "assets/data/artists.json"
STAGES_DIR = ROOT / "stages"
BASE_URL = "https://www.earthdancecapetown.co.za/"
TICKETS = (
    "https://www.quicket.co.za/events/368787-earthdance-cape-town-2026/"
    "?ref=link-campaign&amp;lc=website#/"
)


def act_markup(act: dict) -> str:
    name = html.escape(act["name"], quote=False)
    if act.get("country"):
        name += f'&nbsp;<span class="act-country">{html.escape(act["country"], quote=False)}</span>'
    if act.get("note"):
        name += f'&nbsp;<span class="act-note">{html.escape(act["note"], quote=False)}</span>'
    if act.get("profile"):
        label = esc(f'View {act.get("profile_label", act["name"])} artist profile')
        return f'              <li><a href="{act["profile"]}" aria-label="{label}">{name}</a></li>'
    return f"              <li>{name}</li>"


def medallion(artist: dict) -> str:
    """The lineup-page profile medallion, reused so a face means the same thing
    wherever it appears."""
    logo = " lineup-profile-logo" if artist["image_kind"] == "logo" else ""
    style = (
        f'--artist-image-position:{esc(artist["image_position"])};'
        f'--artist-image-scale:{esc(str(artist.get("image_scale", "1")))};'
        f'--artist-image-translate-x:{esc(str(artist.get("image_translate_x", "0%")))};'
        f'--artist-image-translate-y:{esc(str(artist.get("image_translate_y", "0%")))};'
        f'--artist-image-background:{esc(str(artist.get("image_background", "#0d0a24")))}'
    )
    return f"""        <a class="lineup-profile" href="artists/{esc(artist['slug'])}/">
          <span class="lineup-profile-medallion{logo}" style="{style}">
            <span class="lineup-profile-crop"><img src="{esc(artist['image'])}" alt="" loading="lazy" decoding="async"></span>
            <img class="lineup-profile-frame" src="assets/artists/flower-frame-small.png" alt="" aria-hidden="true" loading="lazy" decoding="async">
          </span>
          <strong>{esc(artist['name'])}</strong>
        </a>"""


def faces_for(stage: dict, by_slug: dict) -> list[dict]:
    """Profiled artists on this stage, in playing order, once each."""
    seen, out = set(), []
    for block in stage["blocks"]:
        for act in block["acts"]:
            slug = (act.get("profile") or "").strip("/").removeprefix("artists/")
            if slug and slug not in seen and slug in by_slug:
                seen.add(slug)
                out.append(by_slug[slug])
    return out


def head(stage: dict) -> str:
    name = stage["name"]
    canonical = BASE_URL + stage["page"]
    image_url = BASE_URL + stage["hero_image"]
    description = stage["lede"]
    schema = {
        "@context": "https://schema.org",
        "@type": "MusicEvent",
        "@id": canonical + "#stage",
        "name": f"{name} — Earthdance Cape Town 2026",
        "startDate": "2026-09-18",
        "endDate": "2026-09-20",
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "url": canonical,
        "image": image_url,
        "description": plain(description),
        "location": {
            "@type": "Place",
            "name": f"{name}, Kromrivier Farm",
            "address": {
                "@type": "PostalAddress",
                "addressRegion": "Western Cape",
                "addressCountry": "ZA",
            },
        },
        "offers": {
            "@type": "Offer",
            "url": TICKETS.replace("&amp;", "&"),
            "availability": "https://schema.org/InStock",
        },
    }
    schema_json = json.dumps(schema, ensure_ascii=False).replace("</", "<\\/")
    return f"""<head>
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
}})(window,document,'script','dataLayer','GTM-W467DMKQ');</script>
<!-- End Google Tag Manager -->
<!-- Meta Pixel Code -->
<script>
!function(f,b,e,v,n,t,s)
{{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)}};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '3564053623773252');
window.earthdanceMetaPageViewEventId = 'pageview-' + Date.now() + '-' +
  Math.random().toString(36).slice(2, 12);
fbq('track', 'PageView', {{}}, {{eventID: window.earthdanceMetaPageViewEventId}});
</script>
<!-- End Meta Pixel Code -->
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(name)} — Earthdance Cape Town 2026</title>
<meta name="description" content="{esc(plain(description))}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:title" content="{esc(name)} — Earthdance Cape Town 2026">
<meta property="og:description" content="{esc(plain(description))}">
<meta property="og:image" content="{esc(image_url)}">
<meta property="og:image:alt" content="{esc(stage['hero_alt'])}">
<meta property="og:type" content="website">
<meta property="og:url" content="{esc(canonical)}">
<meta property="og:site_name" content="Earthdance Cape Town">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(name)} — Earthdance Cape Town 2026">
<meta name="twitter:description" content="{esc(plain(description))}">
<meta name="twitter:image" content="{esc(image_url)}">
<link rel="canonical" href="{esc(canonical)}">
<base href="../../">
<link rel="icon" href="assets/brand/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300..800&amp;family=Comfortaa:wght@600;700&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/site.css?v=20260903-cta">
<script type="application/ld+json">{schema_json}</script>
</head>"""


def page_for(stage: dict, other: dict, by_slug: dict) -> str:
    name = esc(stage["name"])
    story = "\n".join(f"        <p class=\"bright\">{p}</p>" for p in stage["story"])
    facts = "\n".join(
        f'        <div class="stat"><b class="big gradient-text">{f["value"]}</b>'
        f'<span>{f["label"]}</span></div>'
        for f in stage["facts"]
    )
    cards = "\n".join(
        f'        <div class="card"><div class="card-accent"></div>'
        f'<h3>{c["title"]}</h3><p>{c["body"]}</p></div>'
        for c in stage["character"]
    )

    days = []
    for block in stage["blocks"]:
        count = len(block["acts"])
        tag = f"{count} act" if count == 1 else f"{count} acts"
        acts = "\n".join(act_markup(a) for a in block["acts"])
        days.append(
            f'      <h3 class="act-heading" id="{esc(block["id"])}">{esc(block["name"])}'
            f' <span class="act-count">{tag}</span></h3>\n'
            f'      <ul class="act-index">\n{acts}\n      </ul>'
        )
    days = "\n".join(days)

    faces = faces_for(stage, by_slug)
    faces_section = ""
    if faces:
        face_cards = "\n".join(medallion(a) for a in faces)
        faces_section = f"""  <section class="section stage-faces-section" id="faces">
    <div class="container">
      <span class="eyebrow">Artist profiles</span>
      <h2>Who you'll hear here</h2>
      <p class="bright">{len(faces)} of the artists on this stage have a profile so far. More of the lineup lands between now and September.</p>
      <div class="stage-faces">
{face_cards}
      </div>
      <div class="ticket-nudge">
        <p>One ticket covers both stages, all three days, and everything between them.</p>
        <a class="btn btn-pink" href="{TICKETS}" target="_blank" rel="noopener">Book your Earthdance weekend</a>
      </div>
    </div>
  </section>

"""

    return f"""<!DOCTYPE html>
<html lang="en">
{head(stage)}
<body class="stage-page">
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-W467DMKQ"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
<!-- Meta Pixel Code (noscript) -->
<noscript><img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id=3564053623773252&amp;ev=PageView&amp;noscript=1"
alt=""></noscript>
<!-- End Meta Pixel Code (noscript) -->
{header()}

<main>
  <section class="page-hero hero">
    <div class="hero-bg" style="background-image:url('{esc(stage["hero_image"])}')"></div>
    <div class="hero-veil"></div>
    <div class="container">
      <span class="eyebrow">Stage</span>
      <h1>{name}</h1>
      <p class="lede">{stage["lede"]}</p>
      <div class="stat-strip stage-facts">
{facts}
      </div>
    </div>
    <span class="hero-credit">Photo: {esc(stage["hero_credit"])}</span>
  </section>

{faces_section}  <section class="section section-tint">
    <div class="container">
      <span class="eyebrow">The stage</span>
      <h2>What happens here</h2>
{story}
      <div class="card-grid vivid">
{cards}
      </div>
    </div>
  </section>

  <section class="section" id="who-is-playing">
    <div class="container">
      <span class="eyebrow">Playing here</span>
      <h2>Everyone on {name}</h2>
      <p class="bright">The full running order for this stage, in playing order. Set times follow once the running order is locked.</p>
{days}
    </div>
  </section>

  <section class="section">
    <div class="container">
      <div class="ticket-nudge">
        <p>That whole running order plays out over three days at Kromrivier Farm, 18&ndash;20 September.</p>
        <a class="btn btn-pink" href="{TICKETS}" target="_blank" rel="noopener">Get your Earthdance 2026 ticket</a>
      </div>
      <div class="artist-profile-nav">
        <a href="{esc(other["page"])}">
          <span>The other stage</span>
          <strong>{esc(other["name"])} &rarr;</strong>
        </a>
        <a href="lineup.html#announced-artists">
          <span>Everyone announced</span>
          <strong>Full lineup &rarr;</strong>
        </a>
      </div>
    </div>
  </section>
</main>

{footer()}
<script src="assets/js/site.js" defer></script>
</body>
</html>
"""


def main() -> None:
    data = json.loads(DATA.read_text())
    by_slug = {a["slug"]: a for a in json.loads(ARTISTS.read_text())["artists"]}
    stages = data["stages"]
    STAGES_DIR.mkdir(exist_ok=True)
    for i, stage in enumerate(stages):
        other = stages[(i + 1) % len(stages)]
        out = STAGES_DIR / stage["id"]
        out.mkdir(parents=True, exist_ok=True)
        (out / "index.html").write_text(page_for(stage, other, by_slug))
    print(f"stages/ — {len(stages)} stage pages")


if __name__ == "__main__":
    main()
