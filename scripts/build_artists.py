#!/usr/bin/env python3
"""Generate evergreen artist profile pages from assets/data/artists.json.

Usage: python3 scripts/build_artists.py

Each artist is written to artists/<slug>/index.html so the public URL remains
useful beyond a single edition of the festival. Artist data stays separate from
the generated pages; update the JSON and run this script again.
"""

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "assets/data/artists.json"
LINEUP_DATA = ROOT / "assets/data/lineup.json"
ARTISTS_DIR = ROOT / "artists"
LINEUP_PAGE = ROOT / "lineup.html"
LINEUP_START = "<!-- ARTIST-BROWSER:START -->"
LINEUP_END = "<!-- ARTIST-BROWSER:END -->"
BASE_URL = "https://www.earthdancecapetown.co.za/"


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def stages_by_slug() -> dict[str, list[dict]]:
    """slug -> the stages that artist plays, so a profile can lead back to them."""
    lineup = json.loads(LINEUP_DATA.read_text())
    out: dict[str, list[dict]] = {}
    for stage in lineup["stages"]:
        for block in stage["blocks"]:
            for act in block["acts"]:
                slug = (act.get("profile") or "").strip("/").removeprefix("artists/")
                if not slug:
                    continue
                seen = out.setdefault(slug, [])
                if not any(x["id"] == stage["id"] for x in seen):
                    seen.append({"id": stage["id"], "name": stage["name"], "page": stage["page"]})
    return out


def stage_links(stages: list[dict]) -> str:
    return " <span aria-hidden=\"true\">&middot;</span> ".join(
        f'<a href="{esc(st["page"])}">{esc(st["name"])}</a>' for st in stages
    )


def description_for(artist: dict) -> str:
    suffix = (
        f" See {artist['name']} at Earthdance Cape Town 2026, "
        "18–20 September at Kromrivier Farm."
    )
    description = artist["summary"].strip() + suffix
    if len(description) <= 160:
        return description
    shorter = (
        f"Meet {artist['name']}, appearing at Earthdance Cape Town 2026, "
        "18–20 September at Kromrivier Farm."
    )
    return shorter


def head(artist: dict) -> str:
    name = artist["name"]
    slug = artist["slug"]
    canonical = f"{BASE_URL}artists/{slug}/"
    image_url = BASE_URL + artist["image"]
    description = description_for(artist)
    same_as = [link["url"] for link in artist["links"]]
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Person",
                "@id": canonical + "#artist",
                "name": name,
                "url": canonical,
                "image": image_url,
                "description": artist["summary"],
                "sameAs": same_as,
            },
            {
                "@type": "MusicEvent",
                "@id": BASE_URL + "#event",
                "name": "Earthdance Cape Town 2026",
                "startDate": "2026-09-18",
                "endDate": "2026-09-20",
                "eventStatus": "https://schema.org/EventScheduled",
                "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
                "url": BASE_URL,
                "image": BASE_URL + "assets/brand/og-image.jpg",
                "location": {
                    "@type": "Place",
                    "name": "Kromrivier Farm",
                    "address": {
                        "@type": "PostalAddress",
                        "addressRegion": "Western Cape",
                        "addressCountry": "ZA",
                    },
                },
                "performer": {"@id": canonical + "#artist"},
                "offers": {
                    "@type": "Offer",
                    "url": "https://www.quicket.co.za/events/368787-earthdance-cape-town-2026/#/tickets",
                    "availability": "https://schema.org/InStock",
                },
            },
        ],
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
<meta name="description" content="{esc(description)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:title" content="{esc(name)} — Earthdance Cape Town 2026">
<meta property="og:description" content="{esc(description)}">
<meta property="og:image" content="{esc(image_url)}">
<meta property="og:image:alt" content="{esc(artist['image_alt'])}">
<meta property="og:type" content="profile">
<meta property="og:url" content="{esc(canonical)}">
<meta property="og:site_name" content="Earthdance Cape Town">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(name)} — Earthdance Cape Town 2026">
<meta name="twitter:description" content="{esc(description)}">
<meta name="twitter:image" content="{esc(image_url)}">
<link rel="canonical" href="{esc(canonical)}">
<base href="../../">
<link rel="icon" href="assets/brand/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300..800&amp;family=Comfortaa:wght@600;700&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/site.css?v=20260903-stagelinks">
<script type="application/ld+json">{schema_json}</script>
</head>"""


def header() -> str:
    return """<header class="site-header">
  <div class="container nav-wrap">
    <a class="brand" href="index.html">
      <img src="assets/brand/logo-180.png" alt="Earthdance Cape Town — heart, lotus and globe emblem">
      <span>earthdance<em>Cape Town 2026</em></span>
    </a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="site-nav" aria-label="Menu"><span></span></button>
    <nav id="site-nav" class="site-nav">
      <div class="nav-group">
        <button class="nav-group-btn" type="button">About</button>
        <div class="nav-drop">
          <a href="about.html">About Earthdance</a>
          <a href="history.html">History</a>
          <a href="prayer-for-peace.html">Prayer for Peace</a>
        </div>
      </div>
      <div class="nav-group">
        <button class="nav-group-btn" type="button">Gatherings</button>
        <div class="nav-drop">
          <a href="gatherings.html">The Road to September</a>
          <a href="love-in-a-bowl.html">Heart at Love in a Bowl</a>
        </div>
      </div>
      <div class="nav-group">
        <button class="nav-group-btn" type="button">Lineup</button>
        <div class="nav-drop">
          <a href="lineup.html">Full lineup</a>
          <a href="stages/mellow-meadow/">Mellow Meadow</a>
          <a href="stages/sonic-horizon/">Sonic Horizon</a>
        </div>
      </div>
      <div class="nav-group">
        <button class="nav-group-btn" type="button">Get Involved</button>
        <div class="nav-drop">
          <a href="vendors.html">Vendors</a>
          <a href="volunteers.html">Volunteers</a>
          <a href="collaborators.html">Collaborators</a>
        </div>
      </div>
      <div class="nav-group">
        <button class="nav-group-btn" type="button">Plan</button>
        <div class="nav-drop">
          <a href="glamping-camping.html">Glamping &amp; Camping</a>
          <a href="practical-info.html">Practical Info</a>
          <a href="practical-info.html#gates">Gates &amp; Entry</a>
          <a href="faq.html">FAQ</a>
          <a href="sustainability.html">Sustainability</a>
        </div>
      </div>
      <a href="gallery.html">Gallery</a>
      <a class="btn btn-pink nav-cta" href="https://www.quicket.co.za/events/368787-earthdance-cape-town-2026/?ref=link-campaign&amp;lc=website#/" target="_blank" rel="noopener">Buy Tickets</a>
    </nav>
  </div>
</header>"""


def footer() -> str:
    return """<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <img src="assets/brand/logo-180.png" alt="">
        <p>Earthdance Cape Town is part of a worldwide movement for peace, connection and collective celebration.</p>
      </div>
      <div>
        <h4>The Festival</h4>
        <ul>
          <li><a href="about.html">About Earthdance</a></li>
          <li><a href="lineup.html">Lineup</a></li>
          <li><a href="history.html">History</a></li>
          <li><a href="https://earthdance.org/" target="_blank" rel="noopener">Earthdance Global</a></li>
          <li><a href="https://earthdance.org/event/earthdance-cape-town-south-africa-2026/" target="_blank" rel="noopener">Cape Town on Earthdance.org</a></li>
          <li><a href="gatherings.html">The Road to September</a></li>
          <li><a href="love-in-a-bowl.html">Heart at Love in a Bowl</a></li>
          <li><a href="prayer-for-peace.html">Prayer for Peace</a></li>
          <li><a href="gallery.html">Gallery</a></li>
        </ul>
      </div>
      <div>
        <h4>Get Involved</h4>
        <ul>
          <li><a href="vendors.html">Vendors</a></li>
          <li><a href="volunteers.html">Volunteers</a></li>
          <li><a href="collaborators.html">Collaborators</a></li>
          <li><a href="https://linktr.ee/EarthdanceCT" target="_blank" rel="noopener">Linktree</a></li>
        </ul>
      </div>
      <div>
        <h4>Plan</h4>
        <ul>
          <li><a href="glamping-camping.html">Glamping &amp; Camping</a></li>
          <li><a href="practical-info.html">Practical Info</a></li>
          <li><a href="faq.html">FAQ</a></li>
          <li><a href="sustainability.html">Sustainability &amp; Waste</a></li>
          <li><a href="https://www.quicket.co.za/events/368787-earthdance-cape-town-2026/?ref=link-campaign&amp;lc=website#/" target="_blank" rel="noopener">Buy Tickets</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-fine">
      <span>© 2026 Soulstream Festivals Pty. Ltd.</span>
      <span><a href="mailto:info@earthdancecapetown.co.za">info@earthdancecapetown.co.za</a> · <a href="https://linktr.ee/EarthdanceCT" target="_blank" rel="noopener">linktr.ee/EarthdanceCT</a></span>
      <span><a href="privacy.html">Privacy Policy</a> · <a href="terms.html">Terms &amp; Conditions</a></span>
    </div>
  </div>
</footer>"""


def lineup_browser(artists: list[dict]) -> str:
    profiles = []
    for artist in artists:
        if not artist.get("lineup_card", True):
            continue
        logo_class = " lineup-profile-logo" if artist["image_kind"] == "logo" else ""
        image_scale = esc(str(artist.get("image_scale", "1")))
        image_translate_x = esc(str(artist.get("image_translate_x", "0%")))
        image_translate_y = esc(str(artist.get("image_translate_y", "0%")))
        image_background = esc(str(artist.get("image_background", "#0d0a24")))
        profiles.append(
            f"""        <a class="lineup-profile" href="artists/{esc(artist['slug'])}/">
          <span class="lineup-profile-medallion{logo_class}" style="--artist-image-position:{esc(artist['image_position'])};--artist-image-scale:{image_scale};--artist-image-translate-x:{image_translate_x};--artist-image-translate-y:{image_translate_y};--artist-image-background:{image_background}">
            <span class="lineup-profile-crop"><img src="{esc(artist['image'])}" alt="" loading="lazy" decoding="async"></span>
            <img class="lineup-profile-frame" src="assets/artists/flower-frame-small.png" alt="" aria-hidden="true" loading="lazy" decoding="async">
          </span>
          <strong>{esc(artist['name'])}</strong>
        </a>"""
        )

    profiles.append(
        """        <div class="lineup-profile lineup-profile-coming" aria-label="More artist profiles coming">
          <span class="lineup-profile-medallion">
            <span class="lineup-profile-crop" aria-hidden="true"><span class="lineup-profile-spark">✦</span></span>
            <img class="lineup-profile-frame" src="assets/artists/flower-frame-small.png" alt="" aria-hidden="true" loading="lazy" decoding="async">
          </span>
          <strong>More artist stories coming</strong>
        </div>"""
    )

    return f"""  <section class="section lineup-browser" aria-labelledby="browse-artists-title">
    <div class="container">
      <div class="lineup-browser-head">
        <div>
          <span class="eyebrow">Artist profiles are landing</span>
          <h2 id="browse-artists-title">Meet the artists</h2>
          <p>A lineup is more than a list of names. Explore the music and stories behind some of the artists joining us at Kromrivier Farm.</p>
        </div>
        <nav class="lineup-jumps" aria-label="Jump to a lineup section">
          <a href="lineup.html#announced-artists"><span>See everyone announced</span><strong>Full lineup</strong></a>
        </nav>
      </div>
      <div class="lineup-profile-strip" aria-label="Published artist profiles">
{chr(10).join(profiles)}
      </div>
    </div>
  </section>"""


def page_for(
    artist: dict,
    event: dict,
    previous: dict | None,
    following: dict | None,
    stages: list[dict],
) -> str:
    name = esc(artist["name"])
    position = esc(artist["image_position"])
    image_scale = esc(str(artist.get("image_scale", "1")))
    image_translate_x = esc(str(artist.get("image_translate_x", "0%")))
    image_translate_y = esc(str(artist.get("image_translate_y", "0%")))
    image_background = esc(str(artist.get("image_background", "#0d0a24")))
    compact_name = artist.get("compact_name") or (
        len(artist["name"]) > 9 and " " not in artist["name"]
    )
    name_class = " class=\"artist-name-long\"" if compact_name else ""
    lineup_href = "lineup.html#announced-artists"
    image_class = " artist-portrait-logo" if artist["image_kind"] == "logo" else ""
    bio = "".join(f"        <p>{esc(paragraph)}</p>\n" for paragraph in artist["bio"])

    stage_cell = stage_links(stages) if stages else "To be announced"
    crumb_stage = (
        f'<a href="{esc(stages[0]["page"])}">{esc(stages[0]["name"])}</a>'
        '<span aria-hidden="true">/</span>'
        if len(stages) == 1 else ""
    )
    if len(stages) == 1:
        stage_sentence = f'{name} plays {stage_links(stages)} at Earthdance Cape Town 2026.'
    elif len(stages) > 1:
        prose = " and ".join(
            f'<a href="{esc(st["page"])}">{esc(st["name"])}</a>' for st in stages
        )
        stage_sentence = f'{name} plays both stages at Earthdance Cape Town 2026: {prose}.'
    else:
        stage_sentence = f'{name} joins the Earthdance Cape Town 2026 lineup.'
    about = ""
    if bio:
        about = f"""  <section class="section artist-about">
    <div class="container artist-reading-column">
      <span class="eyebrow">Behind the sound</span>
      <h2>About {name}</h2>
{bio.rstrip()}
    </div>
  </section>
"""

    extra_links = [
        link for link in artist["links"] if link["url"] != artist["primary_link"]["url"]
    ]
    links_section = ""
    if extra_links:
        links = "\n".join(
            f'          <a href="{esc(link["url"])}" target="_blank" rel="noopener">{esc(link["label"])} <span aria-hidden="true">↗</span></a>'
            for link in extra_links
        )
        links_section = f"""  <section class="section section-tint artist-links-section">
    <div class="container artist-link-row">
      <div>
        <span class="eyebrow">Keep listening</span>
        <h2>Find {name} online</h2>
      </div>
      <div class="artist-links" aria-label="{name} links">
{links}
      </div>
    </div>
  </section>
"""

    if previous and following:
        profile_nav = f"""<div class="artist-profile-nav">
        <a href="artists/{esc(previous['slug'])}/">
          <span>More artist profiles</span>
          <strong>← {esc(previous['name'])}</strong>
        </a>
        <a href="artists/{esc(following['slug'])}/">
          <span>More artist profiles</span>
          <strong>{esc(following['name'])} →</strong>
        </a>
      </div>"""
    else:
        profile_nav = f"""<div class="artist-profile-nav artist-profile-nav-single">
        <a href="{lineup_href}">
          <span>Explore the artists</span>
          <strong>Back to the lineup →</strong>
        </a>
      </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
{head(artist)}
<body class="artist-page">
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
  <section class="artist-hero">
    <div class="artist-hero-wash" aria-hidden="true"></div>
    <div class="container">
      <nav class="artist-breadcrumb" aria-label="Breadcrumb">
        <a href="lineup.html">Lineup</a><span aria-hidden="true">/</span>{crumb_stage}<span>{name}</span>
      </nav>
      <div class="artist-hero-grid">
        <div class="artist-intro">
          <span class="eyebrow">Artist profile</span>
          <h1{name_class}>{name}</h1>
          <p class="artist-summary">{esc(artist['summary'])}</p>
          <div class="btn-row artist-actions">
            <a class="btn btn-lime" href="{esc(artist['primary_link']['url'])}" target="_blank" rel="noopener">{esc(artist['primary_link']['label'])} <span aria-hidden="true">↗</span></a>
            <a class="artist-back-link" href="{lineup_href}">Back to the lineup</a>
          </div>
        </div>
        <figure class="artist-portrait{image_class}" style="--artist-image-position:{position};--artist-image-scale:{image_scale};--artist-image-translate-x:{image_translate_x};--artist-image-translate-y:{image_translate_y};--artist-image-background:{image_background}">
          <div class="artist-portrait-crop">
            <img src="{esc(artist['image'])}" alt="{esc(artist['image_alt'])}">
          </div>
          <img class="artist-portrait-frame" src="assets/artists/flower-frame.png" alt="" aria-hidden="true">
        </figure>
      </div>
      <div class="artist-event-facts" aria-label="Performance details">
        <div><span class="artist-fact-label">Appearing at</span><strong>{esc(event['name'])}</strong></div>
        <div><span class="artist-fact-label">Weekend</span><strong>{esc(event['dates'])}</strong></div>
        <div><span class="artist-fact-label">Stage</span><strong>{stage_cell}</strong></div>
        <div><span class="artist-fact-label">Set time</span><strong>Coming soon</strong></div>
      </div>
    </div>
  </section>

{about}  <section class="section artist-appearance">
    <div class="container artist-appearance-grid">
      <div>
        <span class="eyebrow">Meet us on the farm</span>
        <h2>{name} at Earthdance Cape Town</h2>
        <p>{stage_sentence} Set times and performance details will be added once the full running order is locked.</p>
      </div>
      <div class="artist-ticket-callout">
        <p>See {name} at Kromrivier Farm, 18–20 September.</p>
        <a class="btn btn-pink" href="{esc(event['ticket_url'])}" target="_blank" rel="noopener">Buy tickets to see {name}</a>
      </div>
    </div>
  </section>

{links_section}  <section class="section artist-profile-nav-section">
    <div class="container">
      {profile_nav}
    </div>
  </section>
</main>

{footer()}
<script src="assets/js/site.js?v=20260812-capi1"></script>
</body>
</html>
"""


def main() -> None:
    data = json.loads(DATA.read_text())
    artists = data["artists"]
    slugs = set()
    for artist in artists:
        slug = artist["slug"]
        if slug in slugs:
            raise ValueError(f"Duplicate artist slug: {slug}")
        slugs.add(slug)

    by_stage = stages_by_slug()
    ARTISTS_DIR.mkdir(exist_ok=True)
    for artist in artists:
        group = artists
        if len(group) > 1:
            group_index = group.index(artist)
            previous = group[group_index - 1]
            following = group[(group_index + 1) % len(group)]
        else:
            previous = None
            following = None
        output_dir = ARTISTS_DIR / artist["slug"]
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "index.html").write_text(
            page_for(artist, data["event"], previous, following, by_stage.get(artist["slug"], []))
        )

    lineup = LINEUP_PAGE.read_text()
    if LINEUP_START not in lineup or LINEUP_END not in lineup:
        raise ValueError("lineup.html is missing ARTIST-BROWSER markers")
    before = lineup.split(LINEUP_START, 1)[0]
    after = lineup.split(LINEUP_END, 1)[1]
    LINEUP_PAGE.write_text(
        before
        + LINEUP_START
        + "\n"
        + lineup_browser(artists)
        + "\n"
        + LINEUP_END
        + after
    )

    print(f"artists/ — {len(artists)} profile pages; lineup artist browser updated")


if __name__ == "__main__":
    main()
