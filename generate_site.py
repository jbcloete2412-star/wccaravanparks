#!/usr/bin/env python3
"""
South Africa Camping Website — Multi-page Site Generator
Parses index.html and generates:
  - Individual park pages (parks/[slug].html)
  - Region hub pages (regions/[slug].html)
  - About, Contact, Guides pages
  - sitemap.xml
"""

from bs4 import BeautifulSoup
import os, re, json
from pathlib import Path

BASE = Path("/sessions/dazzling-zealous-wright/mnt/South Africa CAMPING WEBSITE")
SRC  = BASE / "index.html"
ADSENSE = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4901428323700954" crossorigin="anonymous"></script>'
DOMAIN  = "https://southafricacamp.com"

def slug(text):
    t = text.lower().strip()
    t = re.sub(r"[''&]", "", t)
    t = re.sub(r"[^a-z0-9]+", "-", t)
    return t.strip("-")

def makedirs(*paths):
    for p in paths:
        os.makedirs(p, exist_ok=True)

soup = BeautifulSoup(SRC.read_text(encoding="utf-8"), "html.parser")

parks = []
for art in soup.find_all("article", class_="park-entry"):
    name     = art.get("data-name", "")
    region   = art.get("data-region", "")
    town     = art.get("data-town", "")
    desc_el  = art.find("p", class_="card-desc")
    desc     = desc_el.get_text(" ", strip=True) if desc_el else ""
    tags_els = art.find_all("span", class_="card-tag")
    tags     = [t.get_text(strip=True) for t in tags_els]
    loc_el   = art.find("p", class_="card-location")
    location = loc_el.get_text(" ", strip=True) if loc_el else ""
    gps_el   = art.find("span", class_="card-gps")
    gps      = gps_el.get_text(strip=True) if gps_el else ""
    map_link = art.find("a", class_="card-map-link")
    map_href = map_link.get("href", "") if map_link else ""
    strip_el = art.find("div", class_="card-map-strip")
    strip_cls = ""
    if strip_el:
        for c in strip_el.get("class", []):
            if c in ("coast","karoo","wine","garden"):
                strip_cls = c; break
    contacts = art.find("div", class_="card-contacts")
    phone = website = email = ""
    if contacts:
        for a in contacts.find_all("a"):
            href = a.get("href","")
            if href.startswith("tel:"): phone = href.replace("tel:","")
            elif href.startswith("mailto:"): email = href.replace("mailto:","")
            elif href.startswith("http"): website = href
    region_tag_el = art.find("span", class_="card-region-tag")
    region_label  = region_tag_el.get_text(strip=True) if region_tag_el else region
    parks.append({"name":name,"slug":slug(name),"region":region,"region_label":region_label,
                  "town":town,"tags":tags,"desc":desc,"location":location,"gps":gps,
                  "map_href":map_href,"strip_cls":strip_cls,"phone":phone,"website":website,"email":email})

region_labels = {}
for p in parks:
    region_labels.setdefault(p["region"], p["region_label"])
by_region = {}
for p in parks:
    by_region.setdefault(p["region"], []).append(p)

print(f"Found {len(parks)} parks across {len(by_region)} regions")

SHARED_CSS = """
:root{--sand:#fffbf5;--earth:#ff7043;--deep:#1565c0;--forest:#0288d1;--sage:#26a69a;--sky:#b3e5fc;--ocean:#0277bd;--text:#1a237e;--muted:#5c6bc0;--card-bg:#fff;--border:#e3f2fd}
*{margin:0;padding:0;box-sizing:border-box}html{scroll-behavior:smooth}
body{font-family:'DM Sans',sans-serif;background:#f0f7ff;color:var(--text);line-height:1.7}
a{color:var(--ocean);text-decoration:none}a:hover{text-decoration:underline}
.site-nav{background:#0d3b7a;padding:12px 24px;display:flex;align-items:center;gap:24px;flex-wrap:wrap}
.site-nav .logo{color:#fff;font-size:1.1rem;font-weight:700;text-decoration:none}
.site-nav .logo span{color:#ffca28}
.site-nav a{color:rgba(255,255,255,.82);font-size:.9rem;text-decoration:none}
.site-nav a:hover{color:#fff;text-decoration:underline}
.page-hero{background:linear-gradient(135deg,#0d3b7a 0%,#01579b 50%,#00695c 100%);color:#fff;padding:56px 24px 48px;text-align:center;position:relative}
.page-hero .badge{display:inline-block;background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.3);border-radius:24px;padding:4px 16px;font-size:.8rem;letter-spacing:.06em;margin-bottom:16px}
.page-hero h1{font-size:clamp(1.6rem,4vw,2.8rem);font-weight:700;margin-bottom:12px;line-height:1.2}
.page-hero .subtitle{font-size:1.05rem;opacity:.88;max-width:600px;margin:0 auto 20px}
.page-hero .meta{font-size:.85rem;opacity:.7}
.content-wrap{max-width:860px;margin:0 auto;padding:40px 20px 64px}
.section-title{font-size:1.4rem;font-weight:700;color:var(--text);margin:32px 0 16px;padding-bottom:8px;border-bottom:2px solid var(--border)}
p{margin-bottom:1rem;color:#334}
.park-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px;margin:20px 0}
.park-card{background:#fff;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,40,.08);overflow:hidden;transition:transform .15s}
.park-card:hover{transform:translateY(-2px);box-shadow:0 4px 18px rgba(0,0,40,.13)}
.park-card .strip{height:5px}
.strip.coast{background:linear-gradient(90deg,#0288d1,#40c4ff)}.strip.karoo{background:linear-gradient(90deg,#ff8f00,#ffca28)}
.strip.wine{background:linear-gradient(90deg,#ad1457,#f06292)}.strip.garden{background:linear-gradient(90deg,#2e7d32,#66bb6a)}
.strip.default{background:linear-gradient(90deg,#455a64,#90a4ae)}
.park-card-body{padding:16px}.park-card-region{font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);font-weight:600;margin-bottom:4px}
.park-card-name{font-size:1rem;font-weight:700;color:var(--text);margin-bottom:4px}
.park-card-town{font-size:.83rem;color:var(--muted);margin-bottom:8px}
.park-card-desc{font-size:.84rem;color:#556;line-height:1.55;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;margin-bottom:12px}
.park-card-link{display:inline-block;font-size:.82rem;font-weight:600;color:var(--ocean);border:1px solid var(--ocean);border-radius:6px;padding:4px 12px}
.park-card-link:hover{background:var(--ocean);color:#fff;text-decoration:none}
.park-detail{max-width:860px;margin:0 auto;padding:32px 20px 64px}
.park-detail h2{font-size:1.2rem;font-weight:700;color:var(--text);margin:28px 0 10px;padding-bottom:6px;border-bottom:1px solid var(--border)}
.park-detail .desc-full{font-size:1rem;color:#334;line-height:1.75;margin-bottom:20px}
.info-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;margin:16px 0}
.info-box{background:#fff;border-radius:10px;padding:14px 16px;box-shadow:0 1px 6px rgba(0,0,40,.07)}
.info-box .label{font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);font-weight:600;margin-bottom:4px}
.info-box .value{font-size:.95rem;color:var(--text);font-weight:600}
.tag-row{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 20px}
.tag{background:#e3f2fd;color:#0d47a1;border-radius:20px;padding:4px 12px;font-size:.78rem;font-weight:500}
.cta-row{display:flex;flex-wrap:wrap;gap:12px;margin:24px 0}
.btn{display:inline-block;padding:10px 22px;border-radius:8px;font-size:.9rem;font-weight:700;text-decoration:none}
.btn-primary{background:var(--ocean);color:#fff}.btn-secondary{background:#fff;color:var(--ocean);border:1.5px solid var(--ocean)}
.btn:hover{opacity:.88;text-decoration:none}
.map-embed{width:100%;height:320px;border-radius:12px;border:0;margin:12px 0}
.breadcrumb{font-size:.83rem;color:var(--muted);margin-bottom:20px}.breadcrumb a{color:var(--muted)}.breadcrumb span{color:var(--text);font-weight:600}
.site-footer{background:#0d3b7a;color:rgba(255,255,255,.75);text-align:center;padding:28px 20px;font-size:.85rem;margin-top:64px}
.site-footer a{color:rgba(255,255,255,.75)}
.article-body h2{margin:28px 0 12px;font-size:1.25rem;font-weight:700;color:var(--text);padding-bottom:6px;border-bottom:1px solid var(--border)}
.article-body ul{padding-left:1.4rem;margin-bottom:1rem}.article-body ul li{margin-bottom:.4rem;color:#334;font-size:.95rem}
@media(max-width:600px){.info-grid{grid-template-columns:1fr 1fr}.park-grid{grid-template-columns:1fr}}
"""

def nav():
    return """<nav class="site-nav">
  <a href="/" class="logo">South Africa<span>Camp</span></a>
  <a href="/">Directory</a>
  <a href="/regions/">Regions</a>
  <a href="/guides/best-western-cape-caravan-parks.html">Guides</a>
  <a href="/about.html">About</a>
  <a href="/contact.html">Contact</a>
</nav>"""

def footer():
    return """<footer class="site-footer">
  <p>&copy; 2026 SouthAfricaCamp.com &mdash; The Western Cape Caravan Park Directory</p>
  <p style="margin-top:6px"><a href="/">Home</a> &middot; <a href="/regions/">Regions</a> &middot; <a href="/about.html">About</a> &middot; <a href="/contact.html">Contact</a></p>
</footer>"""

def head(title, desc, canonical, extra_ld=None):
    ld = extra_ld or {"@context":"https://schema.org","@type":"WebSite","name":"SouthAfricaCamp","url":DOMAIN}
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
{ADSENSE}
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<script type="application/ld+json">{json.dumps(ld)}</script>
<style>{SHARED_CSS}</style>
</head>
<body>
{nav()}
"""

# ── Park pages ───────────────────────────────────────────────────────────────
makedirs(BASE / "parks")
for p in parks:
    sl = p["slug"]
    canonical = f"{DOMAIN}/parks/{sl}.html"
    phone_html = f'<a href="tel:{p["phone"]}" class="btn btn-secondary">&#128222; Call</a>' if p["phone"] else ""
    web_html   = f'<a href="{p["website"]}" class="btn btn-secondary" rel="nofollow noopener" target="_blank">&#127760; Website</a>' if p["website"] else ""
    gps_parts  = p["gps"].split(",") if p["gps"] else []
    lat = gps_parts[0].strip().replace('−', '-') if gps_parts else ""
    lng = gps_parts[1].strip().replace('−', '-') if len(gps_parts)>1 else ""
    # Cast to float so JSON-LD emits numbers, not strings
    try:
        lat = float(lat) if lat else ""
        lng = float(lng) if lng else ""
    except ValueError:
        pass
    map_embed  = f'<iframe class="map-embed" loading="lazy" src="https://www.google.com/maps?q={lat},{lng}&output=embed" title="{p["name"]} map" allowfullscreen></iframe>' if lat else ""
    tags_html  = "".join(f'<span class="tag">{t}</span>' for t in p["tags"])
    strip_cls  = p["strip_cls"] or "default"
    ld = {"@context":"https://schema.org","@type":"Campground","name":p["name"],
          "description":p["desc"][:200],"address":{"@type":"PostalAddress","addressLocality":p["town"],"addressRegion":"Western Cape","addressCountry":"ZA"},
          "geo":{"@type":"GeoCoordinates","latitude":lat,"longitude":lng} if lat else {},"url":canonical,"telephone":p["phone"]}
    title  = f"{p['name']} — {p['town']}, Western Cape | SouthAfricaCamp"
    desc_m = f"Full guide to {p['name']} in {p['town']}, Western Cape. {p['desc'][:120]}..."
    nearby = [r for r in by_region.get(p["region"],[]) if r["slug"]!=sl][:3]
    nearby_html = ""
    for n in nearby:
        nearby_html += f"""    <div class="park-card">
      <div class="strip {n['strip_cls'] or 'default'}"></div>
      <div class="park-card-body">
        <div class="park-card-region">{n["region_label"]}</div>
        <div class="park-card-name">{n["name"]}</div>
        <div class="park-card-town">{n["town"]}</div>
        <div class="park-card-desc">{n["desc"][:140]}&#8230;</div>
        <a href="/parks/{n['slug']}.html" class="park-card-link">View details &rarr;</a>
      </div>
    </div>\n"""

    html = head(title, desc_m, canonical, extra_ld=ld)
    html += f"""<div class="page-hero" style="padding:40px 24px 36px">
  <p class="badge">{p["region_label"]}</p>
  <h1>{p["name"]}</h1>
  <p class="subtitle">{p["town"]}, Western Cape</p>
  <p class="meta">{p["location"]}</p>
</div>
<div class="park-detail">
  <div class="breadcrumb"><a href="/">Home</a> &rsaquo; <a href="/regions/{p['region']}.html">{p["region_label"]}</a> &rsaquo; <span>{p["name"]}</span></div>
  <h2>About {p["name"]}</h2>
  <p class="desc-full">{p["desc"]}</p>
  <div class="tag-row">{tags_html}</div>
  <div class="cta-row">
    <a href="{p['map_href']}" class="btn btn-primary" rel="noopener" target="_blank">&#128205; Open in Maps</a>
    {phone_html}{web_html}
  </div>
  <h2>Location &amp; Details</h2>
  <div class="info-grid">
    <div class="info-box"><div class="label">Town</div><div class="value">{p["town"]}</div></div>
    <div class="info-box"><div class="label">Region</div><div class="value">{p["region_label"]}</div></div>
    <div class="info-box"><div class="label">Province</div><div class="value">Western Cape</div></div>
    {"<div class='info-box'><div class='label'>GPS</div><div class='value'>" + p["gps"] + "</div></div>" if p["gps"] else ""}
    {"<div class='info-box'><div class='label'>Phone</div><div class='value'>" + p["phone"] + "</div></div>" if p["phone"] else ""}
  </div>
  {map_embed}
  <h2>Nearby Parks in {p["region_label"]}</h2>
  <div class="park-grid">{nearby_html}  </div>
  <h2>All Western Cape Caravan Parks</h2>
  <p>Browse the full directory of 37 Western Cape caravan parks, filtered by region, facilities, and activities.</p>
  <p style="margin-top:12px"><a href="/" class="btn btn-primary">&larr; Back to full directory</a></p>
</div>
{footer()}
</body></html>"""
    (BASE / "parks" / f"{sl}.html").write_text(html, encoding="utf-8")

print(f"  Park pages: {len(parks)}")

# ── Region pages ─────────────────────────────────────────────────────────────
REGION_INTROS = {
    "cape-peninsula":"The Cape Peninsula offers some of South Africa's most dramatic coastal camping — within sight of Table Mountain, along the wild Atlantic seaboard, and through the fynbos-covered mountains of the Cape of Good Hope.",
    "west-coast":"The West Coast stretches north of Cape Town with sheltered lagoons, world-class kite-surfing, legendary rock lobster, and some of the most untouched coastline in the country.",
    "overberg":"The Overberg — 'over the mountains' — is the heartland of whale watching in South Africa. Every year from June to December, southern right whales come to calve in Walker Bay.",
    "overberg-ext":"The greater Overberg coast from Gordon's Bay to Gansbaai is known for shark cage diving, whale watching, pristine lagoons, and the Kogelberg Biosphere Reserve.",
    "winelands":"The Cape Winelands combines world-class wine routes with mountain camping. Stay a stone's throw from Stellenbosch vineyards, hike the Slanghoek mountains, and wake up to views that rival Tuscany.",
    "breede":"The Breede River Valley — Route 62 territory. Hot springs, apricot farms, wine cellars, and the Langeberg mountain backdrop. Perfect for a slow road trip.",
    "karoo":"The Great Karoo is one of the world's great dark-sky destinations. Semi-desert landscape, extraordinary silence, abundant wildlife, and Beaufort West as your basecamp.",
    "garden-route":"The Garden Route is South Africa's most famous coastal drive — from Mossel Bay to Storms River. Lush forests, blue lagoons, surf breaks, whale sightings, and a national park from sea to mountain.",
    "cederberg":"The Cederberg Wilderness — 71,000 hectares of sandstone peaks, ancient San rock art, and night skies so clear the Milky Way casts shadows. Remote, wild, and completely off-grid.",
    "hartenbos":"Hartenbos, near Mossel Bay, is the family holiday capital of the Garden Route. Home to ATKV's iconic waterpark resort and a string of lagoon camps.",
    "sedgefield":"Sedgefield is the ultimate slow town. Straddling Swartvlei lake, with a lagoon, ocean beach, and paragliding ridge — where Capetonians go to truly switch off.",
    "stillbay":"Still Bay (Stilbaai) sits on the banks of the Goukou River. Blue Flag beach, world-class surf, and a charming fishing village atmosphere.",
    "paternoster":"Paternoster and Tietiesbaai make up one of the most spectacular and remote West Coast destinations. Cape Columbine Nature Reserve, crayfish season, and raw Atlantic scenery.",
}

makedirs(BASE / "regions")
for region, rparks in by_region.items():
    label  = region_labels.get(region, region.replace("-"," ").title())
    intro  = REGION_INTROS.get(region, f"Explore the best caravan parks and camping sites in {label}, Western Cape.")
    canonical = f"{DOMAIN}/regions/{region}.html"
    ld = {"@context":"https://schema.org","@type":"CollectionPage","name":f"Caravan Parks in {label}","description":intro[:200],"url":canonical}
    cards = ""
    for p in rparks:
        cards += f"""    <div class="park-card">
      <div class="strip {p['strip_cls'] or 'default'}"></div>
      <div class="park-card-body">
        <div class="park-card-region">{p["town"]}</div>
        <div class="park-card-name">{p["name"]}</div>
        <div class="park-card-desc">{p["desc"][:160]}&#8230;</div>
        <a href="/parks/{p['slug']}.html" class="park-card-link">View details &rarr;</a>
      </div>
    </div>\n"""
    html  = head(f"Caravan Parks in {label} — Western Cape | SouthAfricaCamp",
                 f"Best caravan parks in {label}, Western Cape. {intro[:120]}...", canonical, extra_ld=ld)
    html += f"""<div class="page-hero">
  <p class="badge">{len(rparks)} parks</p>
  <h1>Caravan Parks in {label}</h1>
  <p class="subtitle">{intro}</p>
</div>
<div class="content-wrap">
  <div class="breadcrumb"><a href="/">Home</a> &rsaquo; <a href="/regions/">All Regions</a> &rsaquo; <span>{label}</span></div>
  <h2 class="section-title">{len(rparks)} Parks in {label}</h2>
  <div class="park-grid">{cards}  </div>
  <h2 class="section-title">About {label}</h2>
  <p>{intro}</p>
  <p style="margin-top:16px"><a href="/" class="btn btn-primary">&larr; Full Western Cape Directory</a></p>
</div>
{footer()}
</body></html>"""
    (BASE / "regions" / f"{region}.html").write_text(html, encoding="utf-8")

# regions index
ri_cards = ""
for region, rparks in by_region.items():
    label = region_labels.get(region, region.replace("-"," ").title())
    intro = REGION_INTROS.get(region,"")[:100]
    ri_cards += f"""    <div class="park-card">
      <div class="strip default"></div>
      <div class="park-card-body">
        <div class="park-card-region">{len(rparks)} parks</div>
        <div class="park-card-name">{label}</div>
        <div class="park-card-desc">{intro}&#8230;</div>
        <a href="/regions/{region}.html" class="park-card-link">Explore &rarr;</a>
      </div>
    </div>\n"""
html = head("Caravan Parks by Region — Western Cape | SouthAfricaCamp",
            "Browse all Western Cape caravan parks by region. Cape Peninsula, Garden Route, West Coast, Winelands, Karoo, Cederberg and more.",
            f"{DOMAIN}/regions/")
html += f"""<div class="page-hero">
  <h1>Western Cape Caravan Parks by Region</h1>
  <p class="subtitle">Explore all 13 regions &mdash; from the wild Cederberg to the Garden Route coast</p>
</div>
<div class="content-wrap">
  <div class="breadcrumb"><a href="/">Home</a> &rsaquo; <span>All Regions</span></div>
  <h2 class="section-title">Browse by Region</h2>
  <div class="park-grid">{ri_cards}  </div>
</div>
{footer()}
</body></html>"""
(BASE / "regions" / "index.html").write_text(html, encoding="utf-8")
print(f"  Region pages: {len(by_region)+1}")

# ── About ────────────────────────────────────────────────────────────────────
html = head("About SouthAfricaCamp — Western Cape Caravan Park Directory",
            "SouthAfricaCamp is South Africa's most detailed directory of Western Cape caravan parks and camping sites.",
            f"{DOMAIN}/about.html")
html += """<div class="page-hero">
  <h1>About SouthAfricaCamp</h1>
  <p class="subtitle">South Africa's most detailed Western Cape camping directory</p>
</div>
<div class="content-wrap">
  <div class="breadcrumb"><a href="/">Home</a> &rsaquo; <span>About</span></div>
  <h2 class="section-title">Who We Are</h2>
  <p>SouthAfricaCamp.com is a free, independent directory of caravan parks and camping sites across the Western Cape. We are campers ourselves &mdash; we&rsquo;ve spent weekends at Tietiesbaai with no cell signal, driven the dust roads into the Cederberg, and queued for a braai spot at Ellensrust in peak season.</p>
  <p>This site exists because finding accurate, up-to-date information about Western Cape camping is harder than it should be. Municipal parks don&rsquo;t answer their phones. Websites go out of date. Facebook groups are full of contradictory advice. We wanted one place with the facts: GPS coordinates, contact numbers, what&rsquo;s on-site, and what the experience is actually like.</p>
  <h2 class="section-title">What We Cover</h2>
  <p>We currently list <strong>37 caravan parks and camping sites</strong> across 13 regions of the Western Cape: Cape Peninsula, West Coast, Cape Winelands, Overberg, Breede River Valley, the Karoo, Garden Route, Cederberg, Hartenbos, Sedgefield, Still Bay, and Paternoster.</p>
  <p>Each listing includes GPS coordinates, contact details, a description of the park, key facilities, and a direct link to Google Maps.</p>
  <h2 class="section-title">Our Goal</h2>
  <p>To expand SouthAfricaCamp into the most comprehensive South African camping directory &mdash; covering all nine provinces, with individual park reviews, seasonal guides, and real campsite photos. We&rsquo;re starting with the Western Cape.</p>
  <p style="margin-top:20px"><a href="/" class="btn btn-primary">&larr; Browse the Directory</a></p>
</div>
""" + footer() + "\n</body></html>"
(BASE / "about.html").write_text(html, encoding="utf-8")

# ── Contact ──────────────────────────────────────────────────────────────────
html = head("Contact SouthAfricaCamp — Submit a Park or Report an Error",
            "Contact the SouthAfricaCamp team to submit a new park listing, report outdated information, or ask about Western Cape camping.",
            f"{DOMAIN}/contact.html")
html += """<div class="page-hero">
  <h1>Contact Us</h1>
  <p class="subtitle">Submit a park, report an error, or just say hello</p>
</div>
<div class="content-wrap">
  <div class="breadcrumb"><a href="/">Home</a> &rsaquo; <span>Contact</span></div>
  <h2 class="section-title">Get in Touch</h2>
  <p>We&rsquo;re a small team of campers maintaining this directory in our spare time. We genuinely want to hear from you &mdash; whether you&rsquo;ve spotted an error, know of a park we&rsquo;ve missed, or want to share your favourite spot.</p>
  <h2 class="section-title">Submit a Missing Park</h2>
  <p>Know a Western Cape caravan park that isn&rsquo;t listed? Send us the park name, address, GPS coordinates, contact number, website, and a brief description. We&rsquo;ll review and add it.</p>
  <h2 class="section-title">Report an Error</h2>
  <p>Phone numbers change. Parks close. Facilities get upgraded. If something is wrong, please let us know &mdash; it takes 30 seconds and helps thousands of people planning their trips.</p>
  <h2 class="section-title">Email</h2>
  <p>Reach us at: <a href="mailto:jbcloete2412@gmail.com">jbcloete2412@gmail.com</a></p>
  <p style="margin-top:8px;font-size:.9rem;color:#556">We aim to respond within 2 working days.</p>
  <p style="margin-top:32px"><a href="/" class="btn btn-primary">&larr; Back to Directory</a></p>
</div>
""" + footer() + "\n</body></html>"
(BASE / "contact.html").write_text(html, encoding="utf-8")
print("  About + Contact pages: 2")

# ── Guides ───────────────────────────────────────────────────────────────────
makedirs(BASE / "guides")

guide_ld = lambda title, url: {
    "@context":"https://schema.org","@type":"Article","headline":title,
    "author":{"@type":"Organization","name":"SouthAfricaCamp"},
    "publisher":{"@type":"Organization","name":"SouthAfricaCamp","url":DOMAIN},
    "datePublished":"2026-01-01","dateModified":"2026-10-01","url":url
}

html = head("Best Western Cape Caravan Parks 2026 — Top 10 Picks | SouthAfricaCamp",
            "Our top 10 Western Cape caravan parks for 2026 — chosen for scenery, facilities, value, and the experiences that stay with you.",
            f"{DOMAIN}/guides/best-western-cape-caravan-parks.html",
            extra_ld=guide_ld("Best Western Cape Caravan Parks 2026", f"{DOMAIN}/guides/best-western-cape-caravan-parks.html"))
html += """<div class="page-hero">
  <p class="badge">Guide &middot; 2026</p>
  <h1>Best Western Cape Caravan Parks 2026</h1>
  <p class="subtitle">Ten parks worth the drive &mdash; chosen for scenery, character, and camping experiences that stay with you</p>
</div>
<div class="content-wrap article-body">
  <div class="breadcrumb"><a href="/">Home</a> &rsaquo; <a href="/guides/">Guides</a> &rsaquo; <span>Top 10 Western Cape Parks</span></div>
  <p>The Western Cape has more caravan parks per kilometre of coastline than almost anywhere in Africa. The challenge isn&rsquo;t finding a park &mdash; it&rsquo;s choosing the right one. We&rsquo;ve camped at dozens and narrowed it to ten that genuinely stand out.</p>
  <h2>1. Tietiesbaai Rest Camp, Paternoster</h2>
  <p>As off-grid as it gets in the Western Cape. The Cape Columbine Nature Reserve has no electricity, no cell signal, and some of the most dramatic Atlantic coast scenery in South Africa. Come during crayfish season (November&ndash;February) and you&rsquo;ll understand why people book a year in advance. <a href="/parks/tietiesbaai-rest-camp.html">Full details &rarr;</a></p>
  <h2>2. Keurbooms Lagoon Caravan Park, Plettenberg Bay</h2>
  <p>The biggest and best-positioned park on the Garden Route &mdash; 270 sites on the Keurbooms River lagoon, with surf nearby, dolphins year-round, and whale sightings from June. <a href="/parks/keurbooms-lagoon-caravan-park.html">Full details &rarr;</a></p>
  <h2>3. Kleinfontein, Cederberg</h2>
  <p>The Cederberg is in a different category entirely. No light pollution, San rock paintings a short hike away, and silence that takes adjustment. The stargazing alone is worth the gravel road. <a href="/parks/kleinfontein.html">Full details &rarr;</a></p>
  <h2>4. West Coast National Park, Langebaan</h2>
  <p>August and September transform the Postberg section into a carpet of wildflowers. Outside flower season, prime birdwatching on the Langebaan lagoon and clean beaches with none of the Cape Town crowds. <a href="/parks/west-coast-national-park.html">Full details &rarr;</a></p>
  <h2>5. Ebb &amp; Flow, Wilderness National Park</h2>
  <p>SANParks manages this one well. The Touw River runs through the camp, you can canoe from your site, and the forest is dense enough to feel off-grid despite being 10 minutes from Wilderness village. <a href="/parks/ebb--flow--wilderness-national-park.html">Full details &rarr;</a></p>
  <h2>6. Jongensfontein Caravan Park, Hessequa</h2>
  <p>Hessequa Municipality&rsquo;s flagship park. Still Bay, Blue Flag beaches, and a lagoon mouth ideal for children. Immaculately maintained. <a href="/parks/jongensfontein-caravan-park.html">Full details &rarr;</a></p>
  <h2>7. Ellensrust Caravan Park, Still Bay</h2>
  <p>338 sites along the Goukou River. Blue Flag beach access, tidal pool, surf nearby, and a proper small-town atmosphere. Better value than most Garden Route parks. <a href="/parks/ellensrust-caravan-park.html">Full details &rarr;</a></p>
  <h2>8. Slanghoek Mountain Resort, Rawsonville</h2>
  <p>Drive 90 minutes from Cape Town and you&rsquo;re in a valley that looks like it belongs in the Alps. Hot tubs fed by mountain springs, vine-covered hillsides, and wine routes 20 minutes away. Best in autumn. <a href="/parks/slanghoek-mountain-resort.html">Full details &rarr;</a></p>
  <h2>9. Imhoff Caravan Park, Kommetjie</h2>
  <p>The closest serious camping to Cape Town that doesn&rsquo;t compromise on setting. Chapman&rsquo;s Peak visible from your stand, Long Beach 150m away, and Kommetjie village for evening walks. <a href="/parks/imhoff-caravan-park.html">Full details &rarr;</a></p>
  <h2>10. Karoo National Park, Beaufort West</h2>
  <p>Black rhino, 200+ bird species, a 4x4 trail, and the darkest skies of any national park in the Western Cape. Stop here on your way to the Garden Route &mdash; budget at least two nights. <a href="/parks/karoo-national-park.html">Full details &rarr;</a></p>
  <h2>Plan Your Trip</h2>
  <p>All ten parks are in the full directory with GPS coordinates, contact details, and direct Google Maps links.</p>
  <p style="margin-top:16px"><a href="/" class="btn btn-primary">Browse All 37 Parks</a> <a href="/regions/" class="btn btn-secondary" style="margin-left:12px">Browse by Region</a></p>
</div>
""" + footer() + "\n</body></html>"
(BASE / "guides" / "best-western-cape-caravan-parks.html").write_text(html, encoding="utf-8")

html = head("Camping in the Cederberg — The Complete Guide | SouthAfricaCamp",
            "Everything you need to know about camping in the Cederberg Wilderness: when to go, where to stay, what to hike, and what to bring.",
            f"{DOMAIN}/guides/camping-cederberg-complete-guide.html",
            extra_ld=guide_ld("Camping in the Cederberg — The Complete Guide", f"{DOMAIN}/guides/camping-cederberg-complete-guide.html"))
html += """<div class="page-hero">
  <p class="badge">Guide &middot; Cederberg</p>
  <h1>Camping in the Cederberg</h1>
  <p class="subtitle">When to go, where to camp, what to hike &mdash; the complete guide to South Africa's wildest mountain wilderness</p>
</div>
<div class="content-wrap article-body">
  <div class="breadcrumb"><a href="/">Home</a> &rsaquo; <a href="/guides/">Guides</a> &rsaquo; <span>Cederberg Camping Guide</span></div>
  <p>The Cederberg Wilderness Area covers roughly 71,000 hectares of sandstone peaks, hidden valleys, and ancient riverbeds 200km north of Cape Town. It&rsquo;s the kind of place that changes your idea of what the Western Cape actually is.</p>
  <h2>When to Go</h2>
  <p><strong>Autumn (March&ndash;May)</strong> is the consensus favourite: cooler temperatures, no crowds, crystal-clear air after the first autumn rains, and the orange-red sandstone glowing in afternoon light. <strong>Spring (September&ndash;October)</strong> brings wildflowers and the best conditions for long hikes. <strong>Summer (December&ndash;January)</strong> can be extremely hot &mdash; avoid for multi-day hikes. <strong>Winter (June&ndash;August)</strong> means cold nights (near-zero), possible snow on the peaks, and empty camps.</p>
  <h2>Where to Stay</h2>
  <ul>
    <li><strong><a href="/parks/kleinfontein.html">Kleinfontein</a></strong> &mdash; basic sites, no electricity, rock art walks. The real Cederberg.</li>
    <li><strong><a href="/parks/kardoesie.html">Kardoesie, Piekenierskloof</a></strong> &mdash; dramatic gorge setting on the N7. Good first night.</li>
    <li><strong>Algeria Campsite (Cape Nature)</strong> &mdash; the main official campsite near Citrusdal. Best for families and first-timers.</li>
    <li><strong>Sanddrif Holiday Resort</strong> &mdash; privately run on the Rondegat River. More facilities, popular in December.</li>
  </ul>
  <h2>Key Hikes</h2>
  <ul>
    <li><strong>Maltese Cross</strong> &mdash; 4.5km to a 20-metre sandstone cross. Iconic.</li>
    <li><strong>Wolfberg Arch</strong> &mdash; one of the most dramatic natural structures in the Western Cape. Hard route (~7km return).</li>
    <li><strong>Wolfberg Cracks</strong> &mdash; narrow gorge passages requiring some squeezing. Unique and fun.</li>
    <li><strong>Sneeuberg Peak</strong> (2,028m) &mdash; the highest point in the Western Cape. Full-day undertaking.</li>
    <li><strong>Rock Art Trail</strong> &mdash; San Bushman paintings thousands of years old. Several accessible near Kleinfontein.</li>
  </ul>
  <h2>What to Bring</h2>
  <ul>
    <li>Warm sleeping bag &mdash; nights drop sharply at altitude even in summer</li>
    <li>Solid hiking boots &mdash; sandstone is rough and slippery when wet</li>
    <li>Sufficient water &mdash; many streams dry up in summer</li>
    <li>Paper map or downloaded offline maps &mdash; cell coverage is unreliable</li>
    <li>Firewood from Citrusdal &mdash; collecting wood in the wilderness area is prohibited</li>
  </ul>
  <h2>Getting There</h2>
  <p>Kleinfontein is approximately 230km from Cape Town via the N7 (Citrusdal) then a gravel road. Allow 3&ndash;3.5 hours. Fill up with fuel in Citrusdal &mdash; there are no fuel stations once you turn off the N7.</p>
  <h2>Permits and Booking</h2>
  <p>The Cederberg Wilderness Area is managed by Cape Nature. Overnight hikers need a permit, bookable via CapeNature.co.za. Private farms book directly. Book early for December, January, and Easter &mdash; popular camps fill months in advance.</p>
  <p style="margin-top:24px"><a href="/regions/cederberg.html" class="btn btn-primary">Cederberg Parks</a> <a href="/" class="btn btn-secondary" style="margin-left:12px">Full Directory</a></p>
</div>
""" + footer() + "\n</body></html>"
(BASE / "guides" / "camping-cederberg-complete-guide.html").write_text(html, encoding="utf-8")

# guides index
html = head("Camping Guides — Western Cape | SouthAfricaCamp",
            "Camping guides for the Western Cape &mdash; best parks lists, regional guides, seasonal tips.",
            f"{DOMAIN}/guides/")
html += """<div class="page-hero">
  <h1>Western Cape Camping Guides</h1>
  <p class="subtitle">In-depth guides to help you plan the perfect camping trip</p>
</div>
<div class="content-wrap">
  <div class="breadcrumb"><a href="/">Home</a> &rsaquo; <span>Guides</span></div>
  <h2 class="section-title">All Guides</h2>
  <div class="park-grid">
    <div class="park-card"><div class="strip garden"></div><div class="park-card-body">
      <div class="park-card-region">Best Parks &middot; 2026</div>
      <div class="park-card-name">Top 10 Western Cape Caravan Parks</div>
      <div class="park-card-desc">Our pick of the ten best caravan parks in the Western Cape, chosen for scenery, character, and experiences that stay with you.</div>
      <a href="/guides/best-western-cape-caravan-parks.html" class="park-card-link">Read guide &rarr;</a>
    </div></div>
    <div class="park-card"><div class="strip karoo"></div><div class="park-card-body">
      <div class="park-card-region">Regional Guide &middot; Cederberg</div>
      <div class="park-card-name">Camping in the Cederberg &mdash; Complete Guide</div>
      <div class="park-card-desc">When to go, where to camp, what to hike, and why the Cederberg is unlike anywhere else in South Africa.</div>
      <a href="/guides/camping-cederberg-complete-guide.html" class="park-card-link">Read guide &rarr;</a>
    </div></div>
  </div>
  <p style="margin-top:32px"><a href="/" class="btn btn-primary">&larr; Browse the Directory</a></p>
</div>
""" + footer() + "\n</body></html>"
(BASE / "guides" / "index.html").write_text(html, encoding="utf-8")
print("  Guides pages: 3")

# ── sitemap.xml ──────────────────────────────────────────────────────────────
urls = ([f"{DOMAIN}/",f"{DOMAIN}/about.html",f"{DOMAIN}/contact.html",
         f"{DOMAIN}/regions/",f"{DOMAIN}/guides/",
         f"{DOMAIN}/guides/best-western-cape-caravan-parks.html",
         f"{DOMAIN}/guides/camping-cederberg-complete-guide.html"] +
        [f"{DOMAIN}/regions/{r}.html" for r in by_region] +
        [f"{DOMAIN}/parks/{p['slug']}.html" for p in parks])
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for u in urls:
    pri = "1.0" if u==f"{DOMAIN}/" else ("0.8" if "/parks/" in u or "/guides/" in u else "0.6")
    sm += f"  <url><loc>{u}</loc><changefreq>monthly</changefreq><priority>{pri}</priority></url>\n"
sm += "</urlset>"
(BASE / "sitemap.xml").write_text(sm, encoding="utf-8")
(BASE / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n", encoding="utf-8")
print("  sitemap.xml + robots.txt: 2")

total = len(parks) + len(by_region) + 1 + 2 + 3 + 2
print(f"\n Done: {total} total files generated")
