#!/usr/bin/env python3
"""Generate vendor profile pages from assets/data/vendors.json.

Usage: python3 scripts/build_vendors.py

Each vendor is written to vendors/<slug>/index.html: a photo-hero page (like
stage pages) with a full gallery below, not a single circular portrait like
an artist profile — vendors bring many stall/product photos, not one
headshot. Pages are not yet linked from vendors.html or any nav — they exist
so content can be built and reviewed ahead of a public vendor directory.
"""

import json
from pathlib import Path

from build_artists import esc, footer, header

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "assets/data/vendors.json"
VENDORS_DIR = ROOT / "vendors"
BASE_URL = "https://www.earthdancecapetown.co.za/"


def description_for(vendor: dict) -> str:
    suffix = (
        f" Find {vendor['name']} at Earthdance Cape Town 2026, "
        "18–20 September at Kromrivier Farm."
    )
    description = vendor["summary"].strip() + suffix
    if len(description) <= 160:
        return description
    return f"Meet {vendor['name']}, at Earthdance Cape Town 2026, 18–20 September at Kromrivier Farm."


def head(vendor: dict) -> str:
    name = vendor["name"]
    slug = vendor["slug"]
    canonical = f"{BASE_URL}vendors/{slug}/"
    fallback_image = vendor.get("logo") or "assets/brand/og-image.jpg"
    hero_image = vendor["gallery"][0]["image"] if vendor["gallery"] else fallback_image
    image_url = BASE_URL + hero_image
    description = description_for(vendor)
    same_as = [link["url"] for link in vendor["links"]]
    schema = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": canonical + "#vendor",
        "name": name,
        "url": canonical,
        "image": image_url,
        "description": vendor["summary"],
        "sameAs": same_as,
    }
    if vendor.get("logo"):
        schema["logo"] = BASE_URL + vendor["logo"]
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
<meta name="robots" content="noindex, nofollow">
<meta property="og:title" content="{esc(name)} — Earthdance Cape Town 2026">
<meta property="og:description" content="{esc(description)}">
<meta property="og:image" content="{esc(image_url)}">
<meta property="og:type" content="website">
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
<link rel="stylesheet" href="assets/css/site.css?v=20260910-lineup-grid">
<script type="application/ld+json">{schema_json}</script>
</head>"""


def page_for(vendor: dict, event: dict, previous: dict | None, following: dict | None) -> str:
    name = esc(vendor["name"])
    bio = "".join(f"        <p>{esc(paragraph)}</p>\n" for paragraph in vendor["bio"])

    about = ""
    if bio:
        about = f"""  <section class="section vendor-about">
    <div class="container vendor-reading-column">
      <span class="eyebrow">What they're bringing</span>
      <h2>About {name}</h2>
{bio.rstrip()}
    </div>
  </section>
"""

    gallery_section = ""
    if vendor["gallery"]:
        def tile(shot: dict) -> str:
            contain = shot.get("fit") == "contain"
            tile_class = "vendor-gallery-tile vendor-gallery-tile-contain" if contain else "vendor-gallery-tile"
            backdrop = (
                f'<div class="vendor-gallery-tile-backdrop" style="background-image:url(\'{esc(shot["image"])}\')"></div>'
                if contain
                else ""
            )
            return (
                f'        <div class="{tile_class}">{backdrop}'
                f'<img src="{esc(shot["image"])}" alt="{esc(shot["alt"])}" loading="lazy" decoding="async"></div>'
            )

        gallery_tiles = "\n".join(tile(shot) for shot in vendor["gallery"])
        gallery_section = f"""  <section class="section vendor-gallery-section">
    <div class="container">
      <span class="eyebrow">In the market</span>
      <h2>A closer look at {name}</h2>
      <div class="vendor-gallery">
{gallery_tiles}
      </div>
    </div>
  </section>

"""

    links_section = ""
    if vendor["links"]:
        links = "\n".join(
            f'          <a href="{esc(link["url"])}" target="_blank" rel="noopener">{esc(link["label"])} <span aria-hidden="true">↗</span></a>'
            for link in vendor["links"]
        )
        links_section = f"""  <section class="section section-tint vendor-links-section">
    <div class="container vendor-link-row">
      <div>
        <span class="eyebrow">Keep in touch</span>
        <h2>Find {name} online</h2>
      </div>
      <div class="vendor-links" aria-label="{name} links">
{links}
      </div>
    </div>
  </section>
"""

    has_photos = bool(vendor["gallery"])
    hero_class = "page-hero hero" if has_photos else "page-hero hero vendor-hero-noimage"
    hero_bg = (
        f'<div class="hero-bg" style="background-image:url(\'{esc(vendor["gallery"][0]["image"])}\')"></div>\n    <div class="hero-veil"></div>'
        if has_photos
        else ""
    )
    title_row_class = "vendor-title-row" if has_photos else "vendor-title-row vendor-title-row-noimage"
    if not vendor.get("logo"):
        title_row_class += " vendor-title-row-nologo"
    logo_class = "vendor-logo vendor-logo-plain" if vendor.get("logo_plain") else "vendor-logo"
    logo_img = (
        f'<img class="{logo_class}" src="{esc(vendor["logo"])}" alt="{esc(vendor["logo_alt"])}">'
        if vendor.get("logo")
        else ""
    )

    if previous and following:
        profile_nav = f"""<div class="vendor-profile-nav">
        <a href="vendors/{esc(previous['slug'])}/">
          <span>More vendors</span>
          <strong>← {esc(previous['name'])}</strong>
        </a>
        <a href="vendors/{esc(following['slug'])}/">
          <span>More vendors</span>
          <strong>{esc(following['name'])} →</strong>
        </a>
      </div>"""
    else:
        profile_nav = """<div class="vendor-profile-nav vendor-profile-nav-single">
        <a href="vendor-directory.html">
          <span>Explore vendors</span>
          <strong>← Back to vendors</strong>
        </a>
      </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
{head(vendor)}
<body class="vendor-page">
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
  <section class="{hero_class}">
    {hero_bg}
    <div class="container">
      <nav class="vendor-breadcrumb" aria-label="Breadcrumb">
        <a href="vendor-directory.html">Vendors</a><span aria-hidden="true">/</span><span>{name}</span>
      </nav>
      <div class="{title_row_class}">
        {logo_img}
        <div>
          <span class="eyebrow">{esc(vendor['category'])}</span>
          <h1>{name}</h1>
        </div>
      </div>
      <p class="lede">{esc(vendor['summary'])}</p>
      <div class="stat-strip vendor-facts">
        <div class="stat"><b class="big">{esc(vendor['category'])}</b><span>Category</span></div>
        <div class="stat"><b class="big">{esc(vendor.get('location') or 'TBC')}</b><span>Find them at</span></div>
        <div class="stat"><b class="big">{esc(event['dates'])}</b><span>Weekend</span></div>
        <div class="stat"><b class="big">{esc(vendor.get('price_notes') or 'On the day')}</b><span>Price range</span></div>
      </div>
      <div class="btn-row vendor-actions">
        <a class="vendor-back-link" href="vendor-directory.html">Back to vendors</a>
      </div>
    </div>
  </section>

{gallery_section}{about}  <section class="section vendor-appearance">
    <div class="container vendor-appearance-grid">
      <div>
        <span class="eyebrow">Meet us on the farm</span>
        <h2>{name} at Earthdance Cape Town</h2>
        <p>Find {name} in the vendor village at Kromrivier Farm, 18–20 September 2026.</p>
      </div>
      <div class="vendor-ticket-callout">
        <p>See what's on offer at Kromrivier Farm, 18–20 September.</p>
        <a class="btn btn-pink" href="{esc(event['ticket_url'])}" target="_blank" rel="noopener">Buy tickets</a>
      </div>
    </div>
  </section>

{links_section}  <section class="section vendor-profile-nav-section">
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


def directory_head() -> str:
    canonical = BASE_URL + "vendor-directory.html"
    description = (
        "Meet the traders at Earthdance Cape Town 2026 — food, drink, craft, "
        "clothing and wellness in the market village at Kromrivier Farm."
    )
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
<title>Vendor Directory — Earthdance Cape Town 2026</title>
<meta name="description" content="{esc(description)}">
<meta name="robots" content="noindex, nofollow">
<link rel="canonical" href="{esc(canonical)}">
<link rel="icon" href="assets/brand/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300..800&amp;family=Comfortaa:wght@600;700&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/site.css?v=20260910-lineup-grid">
</head>"""


def directory_card(vendor: dict) -> str:
    name = esc(vendor["name"])
    href = f"vendors/{esc(vendor['slug'])}/"
    if vendor.get("logo"):
        thumb = (
            '<span class="vendor-directory-thumb vendor-directory-thumb-logo">'
            f'<img src="{esc(vendor["logo"])}" alt="" loading="lazy" decoding="async"></span>'
        )
    elif vendor["gallery"]:
        thumb = f'<img class="vendor-directory-thumb" src="{esc(vendor["gallery"][0]["image"])}" alt="" loading="lazy" decoding="async">'
    else:
        initial = esc(vendor["name"][0].upper())
        thumb = f'<span class="vendor-directory-thumb vendor-directory-thumb-blank">{initial}</span>'
    return f"""          <a class="vendor-directory-card" href="{href}">
            {thumb}
            <span class="vendor-directory-card-body">
              <strong>{name}</strong>
              <span>{esc(vendor['summary'])}</span>
            </span>
          </a>"""


# Short description per market-village space, keyed to the "location"
# values used in vendors.json. A location without an entry here still
# renders (falls back to a generic line) rather than breaking the build.
LOCATION_INFO = {
    "Vendor Lane": "The main strip of stalls — the first place to look for food, craft and clothing.",
    "Vendor Village": "A second cluster of stalls in the market village.",
    "Mellow Meadow": "In and around the Mellow Meadow stage, by day workshops, ceremony and sacred fire.",
    "Glamping Avenue": "The path past the glamping area — open to everyone, not just glampers.",
    "Bar area": "Right by the festival bar.",
    "Chill space (Sonic Horizon)": "The chill-out space beside the Sonic Horizon stage.",
}


def locations_section(vendors: list[dict]) -> str:
    counts: dict[str, int] = {}
    for vendor in vendors:
        location = vendor.get("location")
        if location:
            counts[location] = counts.get(location, 0) + 1
    if not counts:
        return ""
    cards = []
    for location in sorted(counts, key=lambda l: (-counts[l], l)):
        count = counts[location]
        tag = "1 trader" if count == 1 else f"{count} traders"
        description = LOCATION_INFO.get(location, "One of the market village spaces.")
        cards.append(f"""        <div class="vendor-location-card">
          <strong>{esc(location)}</strong>
          <span class="vendor-location-count">{tag}</span>
          <p>{esc(description)}</p>
        </div>""")
    cards_html = "\n".join(cards)
    return f"""  <section class="section section-tint">
    <div class="container">
      <span class="eyebrow">Get your bearings</span>
      <h2>Where to find them</h2>
      <p class="bright" style="max-width:60ch;margin-top:10px;">Traders are spread across a few different spaces around the farm.</p>
      <div class="vendor-location-grid">
{cards_html}
      </div>
    </div>
  </section>

"""


def directory_page(data: dict) -> str:
    vendors = data["vendors"]
    categories = ["Food & Drink", "Craft & Goods", "Wellness"]
    groups = []
    for category in categories:
        in_category = sorted(
            (v for v in vendors if v["category"] == category),
            key=lambda v: v["name"].lower(),
        )
        if in_category:
            groups.append((category, in_category))
    leftover = sorted(
        (v for v in vendors if v["category"] not in categories),
        key=lambda v: v["name"].lower(),
    )
    if leftover:
        groups.append(("More", leftover))

    sections = []
    for category, group in groups:
        cards = "\n".join(directory_card(v) for v in group)
        sections.append(f"""      <div class="vendor-directory-category">
        <h2>{esc(category)}</h2>
        <div class="vendor-directory-list">
{cards}
        </div>
      </div>""")
    sections_html = "\n".join(sections)
    locations_html = locations_section(vendors)

    return f"""<!DOCTYPE html>
<html lang="en">
{directory_head()}
<body>
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-W467DMKQ"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
<!-- Meta Pixel Code (noscript) -->
<noscript><img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id=3564053623773252&ev=PageView&noscript=1"
alt=""></noscript>
<!-- End Meta Pixel Code (noscript) -->
{header()}

<main>
  <section class="page-hero hero">
    <div class="hero-bg" style="background-image:url('assets/vendors/images/groove-gear-stall.jpg')"></div>
    <div class="hero-veil"></div>
    <div class="container">
      <span class="eyebrow">Plan Your Visit</span>
      <h1>Meet the <span class="gradient-text">traders</span></h1>
      <p class="lede">Food, drink, craft, clothing and wellness — the people bringing the market village to life at Kromrivier Farm.</p>
    </div>
    <span class="hero-credit">Photo: Groove Gear</span>
  </section>

{locations_html}  <section class="section">
    <div class="container">
      <div class="vendor-directory-columns">
{sections_html}
      </div>
      <div class="ticket-nudge">
        <p>Trading at Earthdance yourself? Applications for our 2026 market village are closed, but you can see what we look for and how it works.</p>
        <a class="btn btn-ghost" href="vendors.html">Vendor info →</a>
      </div>
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
    vendors = data["vendors"]
    slugs = set()
    for vendor in vendors:
        slug = vendor["slug"]
        if slug in slugs:
            raise ValueError(f"Duplicate vendor slug: {slug}")
        slugs.add(slug)

    VENDORS_DIR.mkdir(exist_ok=True)
    for vendor in vendors:
        group = vendors
        if len(group) > 1:
            group_index = group.index(vendor)
            previous = group[group_index - 1]
            following = group[(group_index + 1) % len(group)]
        else:
            previous = None
            following = None
        output_dir = VENDORS_DIR / vendor["slug"]
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "index.html").write_text(
            page_for(vendor, data["event"], previous, following)
        )

    (ROOT / "vendor-directory.html").write_text(directory_page(data))

    print(f"vendors/ — {len(vendors)} profile pages + vendor-directory.html")


if __name__ == "__main__":
    main()
