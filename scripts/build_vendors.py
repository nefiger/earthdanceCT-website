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
    image_url = BASE_URL + vendor["gallery"][0]["image"]
    description = description_for(vendor)
    same_as = [link["url"] for link in vendor["links"]]
    schema = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": canonical + "#vendor",
        "name": name,
        "url": canonical,
        "image": image_url,
        "logo": BASE_URL + vendor["logo"],
        "description": vendor["summary"],
        "sameAs": same_as,
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
<link rel="stylesheet" href="assets/css/site.css?v=20260907-vendors2">
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

    gallery_tiles = "\n".join(
        f'        <img src="{esc(shot["image"])}" alt="{esc(shot["alt"])}" loading="lazy" decoding="async">'
        for shot in vendor["gallery"]
    )

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
        <a href="vendors.html">
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
  <section class="page-hero hero">
    <div class="hero-bg" style="background-image:url('{esc(vendor["gallery"][0]["image"])}')"></div>
    <div class="hero-veil"></div>
    <div class="container">
      <nav class="vendor-breadcrumb" aria-label="Breadcrumb">
        <a href="vendors.html">Vendors</a><span aria-hidden="true">/</span><span>{name}</span>
      </nav>
      <div class="vendor-title-row">
        <img class="vendor-logo" src="{esc(vendor['logo'])}" alt="{esc(vendor['logo_alt'])}">
        <div>
          <span class="eyebrow">{esc(vendor['category'])}</span>
          <h1>{name}</h1>
        </div>
      </div>
      <p class="lede">{esc(vendor['summary'])}</p>
      <div class="stat-strip vendor-facts">
        <div class="stat"><b class="big">{esc(vendor['category'])}</b><span>Category</span></div>
        <div class="stat"><b class="big">{esc(event['venue'])}</b><span>Find them at</span></div>
        <div class="stat"><b class="big">{esc(event['dates'])}</b><span>Weekend</span></div>
        <div class="stat"><b class="big">{esc(vendor.get('price_notes') or 'On the day')}</b><span>Price range</span></div>
      </div>
      <div class="btn-row vendor-actions">
        <a class="vendor-back-link" href="vendors.html">Back to vendors</a>
      </div>
    </div>
  </section>

  <section class="section vendor-gallery-section">
    <div class="container">
      <span class="eyebrow">In the market</span>
      <h2>See {name}</h2>
      <div class="vendor-gallery">
{gallery_tiles}
      </div>
    </div>
  </section>

{about}  <section class="section vendor-appearance">
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

    print(f"vendors/ — {len(vendors)} profile pages (not linked from anywhere yet)")


if __name__ == "__main__":
    main()
