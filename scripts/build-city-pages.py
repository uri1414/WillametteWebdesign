#!/usr/bin/env python3
"""
build-city-pages.py -- generate /web-design-<city>-or/ landing pages.

SEO-PLAYBOOK.md section 2's process for service-area pages: one page per city,
genuinely unique content (not a doorway page), Service schema with
areaServed = that city, linked from the footer, added to the sitemap.

Reuses the header and footer VERBATIM from the already-built homepage (rather
than hand-duplicating that markup here) so a city page is structurally
identical to the homepage's chrome and never drifts from it -- run
flatten-export.py first. Anchors that only make sense on the homepage
(#how, #included, #apply, ...) are rewritten to point at it explicitly.

    python3 scripts/build-city-pages.py [--out .]
"""

import argparse
import json
import pathlib
import re
import sys
from html import escape

from bs4 import BeautifulSoup

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build_lib import extract_faqs, minify_css  # noqa: E402
from city_content import CITIES  # noqa: E402

# Anchors that exist only on the homepage. Bare on that page; from anywhere
# else they must point back at it explicitly or the browser just fails to
# scroll (the id isn't on the current page).
HOMEPAGE_ANCHORS = {"how", "included", "about", "apply", "check"}

LABELS = {
    "en": {
        "skip": "Skip to content",
        "breadcrumb_home": "Home",
        "breadcrumb_aria": "Breadcrumb",
        "included_heading": "What's included",
        "included_kicker": "EVERY BUILD INCLUDES",
        "pricing_line": ("$799 one-time, backed by a 30-day money-back "
                         "satisfaction guarantee. Then $99/month for ongoing "
                         "management."),
        "pricing_cta": "See full pricing",
        "faq_kicker": "COMMON QUESTIONS",
        "other_cities_kicker": "MID-WILLAMETTE VALLEY",
        "other_cities_heading": "Also serving nearby",
        "final_heading": "Let's build something that brings you business.",
        "final_cta": "Apply for the 30-Day Program",
        "final_note": "Takes about 2 minutes.",
        "apply_cta": "Apply for the 30-Day Program",
        "check_cta": "Get a free presence check",
        "trust_bilingual": "English & Español",
    },
    "es": {
        "skip": "Saltar al contenido",
        "breadcrumb_home": "Inicio",
        "breadcrumb_aria": "Ruta de navegación",
        "included_heading": "Qué incluye",
        "included_kicker": "CADA PROYECTO INCLUYE",
        "pricing_line": ("$799 pago único, respaldado por una garantía de "
                         "satisfacción de 30 días con devolución de dinero. "
                         "Luego $99/mes de gestión continua."),
        "pricing_cta": "Ver precios completos",
        "faq_kicker": "PREGUNTAS FRECUENTES",
        "other_cities_kicker": "VALLE MEDIO DE WILLAMETTE",
        "other_cities_heading": "También servimos cerca",
        "final_heading": "Construyamos algo que te traiga clientes.",
        "final_cta": "Aplica al Programa de 30 Días",
        "final_note": "Toma unos 2 minutos.",
        "apply_cta": "Aplica al Programa de 30 Días",
        "check_cta": "Obtén una revisión de presencia gratis",
        "trust_bilingual": "Inglés y Español",
    },
}


def load_chrome(out_root, lang):
    """Pull header + footer out of the already-built homepage."""
    src = out_root / ("index.html" if lang == "en" else "es/index.html")
    if not src.exists():
        sys.exit(f"error: {src} does not exist -- run flatten-export.py first")
    soup = BeautifulSoup(src.read_text(encoding="utf-8"), "html.parser")
    header = soup.find("header")
    footer = soup.find("footer")
    if header is None or footer is None:
        sys.exit(f"error: {src} is missing a <header> or <footer> to reuse")
    return header, footer


def rewrite_chrome_links(node, lang, current_url):
    """Point homepage-only anchors and the language switch at the right place."""
    home = "/" if lang == "en" else "/es/"
    other_home_relative = current_url["es"] if lang == "en" else current_url["en"]

    for a in node.find_all("a", href=True):
        href = a["href"]
        if href == "#top":
            a["href"] = home
        elif href.startswith("#") and href[1:] in HOMEPAGE_ANCHORS:
            a["href"] = f"{home}{href}"
        elif "lang-switch" in (a.get("class") or []):
            a["href"] = other_home_relative


def slugify_path(lang, slug):
    return f"/web-design-{slug}-or/" if lang == "en" else f"/es/web-design-{slug}-or/"


def build_breadcrumb(soup, lang, city_name, canonical, origin):
    home_url = f"{origin}/" if lang == "en" else f"{origin}/es/"
    lab = LABELS[lang]
    nav = soup.new_tag("nav", **{"aria-label": lab["breadcrumb_aria"]})
    nav["class"] = ["breadcrumb"]
    ol = soup.new_tag("ol")
    li1 = soup.new_tag("li")
    a1 = soup.new_tag("a", href=home_url)
    a1.string = lab["breadcrumb_home"]
    li1.append(a1)
    sep = soup.new_tag("li", **{"aria-hidden": "true"})
    sep.string = "/"
    li2 = soup.new_tag("li")
    cur = soup.new_tag("span", **{"aria-current": "page"})
    cur.string = city_name
    li2.append(cur)
    ol.append(li1)
    ol.append(sep)
    ol.append(li2)
    nav.append(ol)
    return nav, [
        {"@type": "ListItem", "position": 1, "name": lab["breadcrumb_home"], "item": home_url},
        {"@type": "ListItem", "position": 2, "name": city_name, "item": canonical},
    ]


def build_body(soup, lang, city, cfg):
    lab = LABELS[lang]
    nap = cfg["nap"]
    content = city[lang]
    origin = cfg["domain"]["origin"]
    canonical = f"{origin}{slugify_path(lang, city['slug'])}"
    city_full = f"{city['name']}, Oregon" if lang == "en" else f"{city['name']}, Oregon"

    main = soup.new_tag("main", id="main")

    breadcrumb, breadcrumb_items = build_breadcrumb(soup, lang, city["name"], canonical, origin)
    main.append(breadcrumb)

    # --- Hero: text-only, no illustration -- these are secondary landing
    # pages, and re-downloading the homepage's hero art on every one would
    # spend byte budget for no LCP benefit here. ---
    hero = soup.new_tag("section", **{"data-reveal": ""})
    hero["style"] = "padding:clamp(56px,8vw,96px) clamp(20px,5vw,64px) clamp(40px,6vw,64px)"
    eyebrow = soup.new_tag("p")
    eyebrow["class"] = ["eyebrow"]
    eyebrow.string = f"WEB DESIGN · {city['name'].upper()}, OREGON"
    h1 = soup.new_tag("h1")
    h1["style"] = "font-size:clamp(32px,4.4vw,48px);margin-top:14px;max-width:18ch"
    h1.string = content["h1"]
    lead = soup.new_tag("p")
    lead["style"] = "font-size:18px;line-height:1.6;color:var(--text-body);margin-top:18px;max-width:56ch"
    lead.string = content["lead"]

    cta_row = soup.new_tag("div", **{"data-stagger": ""})
    cta_row["style"] = "display:flex;gap:14px;flex-wrap:wrap;margin-top:28px"
    apply_a = soup.new_tag("a", href=f"{'/' if lang=='en' else '/es/'}#apply")
    apply_a["class"] = ["btn", "btn--primary", "btn--lg", "lift"]
    apply_a.append(lab["apply_cta"] + " ")
    arw1 = soup.new_tag("span", **{"class": "arw", "aria-hidden": "true"})
    arw1.string = "→"
    apply_a.append(arw1)
    check_a = soup.new_tag("a", href=f"{'/' if lang=='en' else '/es/'}#check")
    check_a["class"] = ["btn", "btn--secondary", "btn--lg", "lift"]
    check_a.string = lab["check_cta"]
    cta_row.append(apply_a)
    cta_row.append(check_a)

    trust = soup.new_tag("p")
    trust["style"] = "margin-top:20px;font:600 13.5px var(--font-ui);color:var(--text-muted)"
    trust_phone = soup.new_tag("a", href=nap["phoneHref"])
    trust_phone["style"] = "color:inherit"
    trust_phone.string = nap["phoneDisplay"]
    trust.append(trust_phone)
    trust.append(f"  ·  {lab['trust_bilingual']}")

    hero.append(eyebrow)
    hero.append(h1)
    hero.append(lead)
    hero.append(cta_row)
    hero.append(trust)
    main.append(hero)

    # --- Intro (the genuinely unique per-city content) ---
    intro = soup.new_tag("section", **{"data-reveal": ""})
    intro["style"] = "padding:0 clamp(20px,5vw,64px) clamp(56px,8vw,88px);border-top:1px solid var(--border-rule);margin-top:8px;padding-top:clamp(56px,8vw,88px)"
    intro_wrap = soup.new_tag("div")
    intro_wrap["style"] = "max-width:760px"
    for para_text in content["intro"]:
        p = soup.new_tag("p")
        p["style"] = "font-size:16.5px;line-height:1.75;color:var(--text-body);margin-top:16px"
        p.string = para_text
        intro_wrap.append(p)
    intro.append(intro_wrap)
    main.append(intro)

    # --- What's included: a scannable checklist (playbook's own template
    # wording), not a re-run of the homepage's full icon-card grid. ---
    included = soup.new_tag("section", **{"data-reveal": "", "style": "padding:0 clamp(20px,5vw,64px) clamp(56px,8vw,88px);background:#F8F1E3"})
    inc_inner = soup.new_tag("div")
    inc_inner["style"] = "padding-top:clamp(56px,8vw,88px)"
    inc_eyebrow = soup.new_tag("p", **{"class": "eyebrow"})
    inc_eyebrow.string = lab["included_kicker"]
    inc_h2 = soup.new_tag("h2")
    inc_h2["style"] = "font-size:clamp(26px,3.2vw,36px);margin-top:12px"
    inc_h2.string = lab["included_heading"]
    ul = soup.new_tag("ul", **{"data-stagger": ""})
    ul["style"] = "list-style:none;margin-top:28px;display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px 24px;max-width:900px;padding:0"
    for svc in cfg["services"]:
        li = soup.new_tag("li", **{"class": "lift"})
        li["style"] = "display:flex;align-items:flex-start;gap:10px;font-size:15.5px;color:var(--text-body);background:var(--color-cream);border:1px solid var(--border-rule);border-radius:var(--radius-md);padding:12px 14px"
        check = soup.new_tag("span", **{"aria-hidden": "true", "style": "color:var(--color-rust);font-weight:700"})
        check.string = "✓"
        li.append(check)
        span = soup.new_tag("span")
        span.string = svc
        li.append(span)
        ul.append(li)
    inc_inner.append(inc_eyebrow)
    inc_inner.append(inc_h2)
    inc_inner.append(ul)

    pricing_p = soup.new_tag("p")
    pricing_p["style"] = "margin-top:28px;font-size:15.5px;color:var(--text-body);max-width:640px"
    pricing_p.string = lab["pricing_line"] + " "
    pricing_link = soup.new_tag("a", href=f"{'/' if lang=='en' else '/es/'}#included")
    pricing_link["class"] = ["h-rust"]
    pricing_link["style"] = "font-weight:700;text-decoration:underline;text-underline-offset:3px"
    pricing_link.string = lab["pricing_cta"] + " →"
    pricing_p.append(pricing_link)
    inc_inner.append(pricing_p)
    included.append(inc_inner)
    main.append(included)

    # --- FAQ (visible <details>, mirrored into FAQPage schema) ---
    faq = soup.new_tag("section", **{"data-reveal": "", "style": "padding:clamp(56px,8vw,88px) clamp(20px,5vw,64px)"})
    faq_eyebrow = soup.new_tag("p", **{"class": "eyebrow"})
    faq_eyebrow.string = lab["faq_kicker"]
    faq_h2 = soup.new_tag("h2")
    faq_h2["style"] = "font-size:clamp(26px,3.2vw,36px);margin-top:12px"
    faq_h2.string = content["h1"].split(" in ")[0] if lang == "en" else lab["faq_kicker"].title()
    faq.append(faq_eyebrow)
    faq.append(faq_h2)
    faq_wrap = soup.new_tag("div")
    faq_wrap["style"] = "max-width:760px;margin-top:24px"
    for q, a in content["faq"]:
        det = soup.new_tag("details", **{"class": "faq-item"})
        det["style"] = "border-bottom:1px solid var(--border-rule);padding:16px 0"
        summ = soup.new_tag("summary")
        summ["style"] = "display:flex;justify-content:space-between;align-items:center;gap:12px;font:700 16px var(--font-ui);color:var(--color-forest)"
        q_span = soup.new_tag("span")
        q_span.string = q
        chev = soup.new_tag("span", **{"class": "fq-chev", "aria-hidden": "true"})
        chev.string = "▾"
        summ.append(q_span)
        summ.append(chev)
        body = soup.new_tag("p", **{"class": "faq-body"})
        body["style"] = "margin-top:10px;font-size:15px;line-height:1.65;color:var(--text-body)"
        body.string = a
        det.append(summ)
        det.append(body)
        faq_wrap.append(det)
    faq.append(faq_wrap)
    main.append(faq)

    # --- Other cities we serve (cross-links; also the thing that keeps
    # these pages from being SEO-orphaned from each other) ---
    others = soup.new_tag("section", **{"data-reveal": "", "style": "padding:0 clamp(20px,5vw,64px) clamp(56px,8vw,88px)"})
    oth_eyebrow = soup.new_tag("p", **{"class": "eyebrow"})
    oth_eyebrow.string = lab["other_cities_kicker"]
    oth_h2 = soup.new_tag("h2")
    oth_h2["style"] = "font-size:clamp(24px,3vw,32px);margin-top:12px"
    oth_h2.string = lab["other_cities_heading"]
    oth_row = soup.new_tag("div")
    oth_row["style"] = "display:flex;gap:12px;flex-wrap:wrap;margin-top:20px"
    for other in CITIES:
        if other["slug"] == city["slug"]:
            continue
        link = soup.new_tag("a", href=slugify_path(lang, other["slug"]))
        link["class"] = ["btn", "btn--secondary", "btn--sm", "lift"]
        link.string = other["name"]
        oth_row.append(link)
    others.append(oth_eyebrow)
    others.append(oth_h2)
    others.append(oth_row)
    main.append(others)

    # --- Final CTA ---
    final = soup.new_tag("section", **{"style": "background:var(--color-forest);padding:clamp(64px,9vw,100px) clamp(20px,5vw,64px);text-align:center"})
    final_h2 = soup.new_tag("h2")
    final_h2["style"] = "color:var(--color-cream);font-size:clamp(28px,3.6vw,42px);max-width:20ch;margin:0 auto"
    final_h2.string = lab["final_heading"]
    final_btn_wrap = soup.new_tag("div")
    final_btn_wrap["style"] = "margin-top:28px"
    final_a = soup.new_tag("a", href=f"{'/' if lang=='en' else '/es/'}#apply")
    final_a["class"] = ["btn", "btn--primary", "btn--lg"]
    final_a.append(lab["final_cta"] + " ")
    arw2 = soup.new_tag("span", **{"class": "arw", "aria-hidden": "true"})
    arw2.string = "→"
    final_a.append(arw2)
    final_btn_wrap.append(final_a)
    final_note = soup.new_tag("p")
    final_note["style"] = "margin-top:14px;font:600 12.5px var(--font-ui);letter-spacing:.06em;color:rgba(243,231,206,.65)"
    final_note.string = lab["final_note"].upper()
    final.append(final_h2)
    final.append(final_btn_wrap)
    final.append(final_note)
    main.append(final)

    return main, breadcrumb_items


def build_head(lang, city, cfg, css, faqs, breadcrumb_items):
    content = city[lang]
    origin = cfg["domain"]["origin"]
    nap = cfg["nap"]
    canonical = f"{origin}{slugify_path(lang, city['slug'])}"
    alt_en = f"{origin}{slugify_path('en', city['slug'])}"
    alt_es = f"{origin}{slugify_path('es', city['slug'])}"
    og_image = f"{origin}/assets/img/og-image.png"
    ga4 = (cfg.get("analytics") or {}).get("ga4MeasurementId") or ""
    city_full = f"{city['name']}, Oregon"

    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "@id": f"{canonical}#webpage",
                "url": canonical,
                "name": content["title"],
                "inLanguage": "en-US" if lang == "en" else "es-US",
                "isPartOf": {"@id": f"{origin}/#website"},
                "about": {"@id": f"{canonical}#service"},
                "breadcrumb": {"@id": f"{canonical}#breadcrumb"},
            },
            {
                "@type": "BreadcrumbList",
                "@id": f"{canonical}#breadcrumb",
                "itemListElement": breadcrumb_items,
            },
            {
                "@type": "Service",
                "@id": f"{canonical}#service",
                "name": (f"Website design and local presence setup in {city_full}"
                         if lang == "en" else
                         f"Diseño web y presencia local en {city_full}"),
                "provider": {"@id": f"{origin}/#organization"},
                "areaServed": {"@type": "City", "name": city_full},
                "availableLanguage": ["en", "es"],
                "url": canonical,
            },
        ],
    }
    if faqs:
        schema["@graph"].append({
            "@type": "FAQPage",
            "@id": f"{canonical}#faq",
            "isPartOf": {"@id": f"{origin}/#website"},
            "mainEntity": [
                {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
                for f in faqs
            ],
        })

    hreflang = (
        f'<link rel="alternate" hreflang="en" href="{alt_en}">\n'
        f'<link rel="alternate" hreflang="es" href="{alt_es}">\n'
        f'<link rel="alternate" hreflang="x-default" href="{alt_en}">'
    )

    analytics = ""
    if ga4:
        analytics = f"""
<script>
(function(){{
  var ID='{ga4}';
  window.dataLayer=window.dataLayer||[];
  function gtag(){{dataLayer.push(arguments);}}
  window.gtag=gtag; gtag('js',new Date()); gtag('config',ID);
  var done=false;
  function load(){{
    if(done)return; done=true;
    var s=document.createElement('script');
    s.async=true; s.src='https://www.googletagmanager.com/gtag/js?id='+ID;
    document.head.appendChild(s);
  }}
  ['scroll','mousemove','touchstart','click','keydown'].forEach(function(e){{
    window.addEventListener(e,load,{{once:true,passive:true}});
  }});
  setTimeout(load,3000);
}})();
</script>"""

    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>{escape(content['title'])}</title>
<meta name="description" content="{escape(content['description'])}">
<link rel="canonical" href="{canonical}">
{hreflang}

<meta name="theme-color" content="#F3E7CE">
<meta name="geo.region" content="US-OR">

<meta property="og:type" content="website">
<meta property="og:site_name" content="{escape(cfg['brand']['name'])}">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{escape(content['title'])}">
<meta property="og:description" content="{escape(content['description'])}">
<meta property="og:image" content="{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Willamette Web Design">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{escape(content['title'])}">
<meta name="twitter:description" content="{escape(content['description'])}">
<meta name="twitter:image" content="{og_image}">

<link rel="icon" href="/favicon.ico" sizes="16x16 32x32 48x48">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">

<link rel="preload" as="font" type="font/woff2" href="/assets/fonts/inter-latin.woff2" crossorigin>
<link rel="preload" as="font" type="font/woff2" href="/assets/fonts/roboto-slab-latin.woff2" crossorigin>

<script>document.documentElement.className+=' js';</script>

<style id="site-css">{css}</style>
{analytics}
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(",", ":"))}</script>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=".")
    args = ap.parse_args()
    out_root = pathlib.Path(args.out)

    cfg = json.loads((out_root / "site.config.json").read_text())
    css_src = minify_css((out_root / "assets/css/site.css").read_text())

    chrome = {lang: load_chrome(out_root, lang) for lang in ("en", "es")}

    for city in CITIES:
        urls = {l2: slugify_path(l2, city["slug"]) for l2 in ("en", "es")}
        for lang in ("en", "es"):
            lab = LABELS[lang]
            soup = BeautifulSoup("<!doctype html>", "html.parser")

            header_src, footer_src = chrome[lang]
            header = BeautifulSoup(str(header_src), "html.parser").find("header")
            footer = BeautifulSoup(str(footer_src), "html.parser").find("footer")
            rewrite_chrome_links(header, lang, urls)
            rewrite_chrome_links(footer, lang, urls)

            body_main, breadcrumb_items = build_body(soup, lang, city, cfg)

            faqs = extract_faqs(body_main)

            html_str = (
                "<!doctype html>\n"
                f'<html lang="{lang}">\n<head>\n'
                + build_head(lang, city, cfg, css_src, faqs, breadcrumb_items)
                + "\n</head>\n<body>\n"
                + f'<a class="skip" href="#main">{lab["skip"]}</a>\n'
                + str(header) + "\n"
                + str(body_main) + "\n"
                + str(footer) + "\n"
                + '<script src="/assets/js/site.js" defer></script>\n'
                + "</body>\n</html>\n"
            )

            dest = out_root / slugify_path(lang, city["slug"]).strip("/") / "index.html"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(html_str, encoding="utf-8")
            print(f"{lang}/{city['slug']}: {dest.relative_to(out_root)}  "
                  f"{len(html_str)/1024:.1f} KB  ({len(faqs)} FAQ)")


if __name__ == "__main__":
    main()
