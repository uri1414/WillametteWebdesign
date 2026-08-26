#!/usr/bin/env python3
"""
build-service-pages.py -- generate /services/<slug>/ pages + the /services/
hub, EN + ES.

SEO-PLAYBOOK.md section 1: one page per service someone actually searches
for individually. None of these sell standalone -- there's no per-service
price in site.config.json, only the $799 program -- so every page's closing
section is an honest upsell into the Willamette 30-Day Program rather than a
fake add-to-cart moment.

Reuses the header and footer VERBATIM from the already-built homepage, same
as the city pages and the service-areas hub -- run flatten-export.py first.

    python3 scripts/build-service-pages.py [--out .]
"""

import argparse
import json
import pathlib
import sys
from html import escape

from bs4 import BeautifulSoup

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build_lib import (  # noqa: E402
    extract_faqs,
    load_chrome,
    minify_css,
    rewrite_chrome_links,
    service_page_path,
    services_hub_path,
)
from service_content import HUB, SERVICES  # noqa: E402

LABELS = {
    "en": {
        "skip": "Skip to content",
        "breadcrumb_home": "Home",
        "breadcrumb_services": "Services",
        "breadcrumb_aria": "Breadcrumb",
        "included_kicker": "WHAT'S INVOLVED",
        "included_heading": "What's included",
        "why_kicker": "WHY US",
        "why_heading": "Why work with us on this",
        "faq_kicker": "COMMON QUESTIONS",
        "faq_heading": "Questions about this service",
        "related_kicker": "THE OTHER SERVICES",
        "related_heading": "The rest of a complete local presence",
        "all_services_cta": "All services",
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
        "breadcrumb_services": "Servicios",
        "breadcrumb_aria": "Ruta de navegación",
        "included_kicker": "QUÉ IMPLICA",
        "included_heading": "Qué incluye",
        "why_kicker": "POR QUÉ NOSOTROS",
        "why_heading": "Por qué trabajar con nosotros en esto",
        "faq_kicker": "PREGUNTAS FRECUENTES",
        "faq_heading": "Preguntas sobre este servicio",
        "related_kicker": "LOS OTROS SERVICIOS",
        "related_heading": "El resto de una presencia local completa",
        "all_services_cta": "Todos los servicios",
        "final_heading": "Construyamos algo que te traiga clientes.",
        "final_cta": "Aplica al Programa de 30 Días",
        "final_note": "Toma unos 2 minutos.",
        "apply_cta": "Aplica al Programa de 30 Días",
        "check_cta": "Obtén una revisión de presencia gratis",
        "trust_bilingual": "Inglés y Español",
    },
}


def build_breadcrumb(soup, lang, service_name, canonical, origin):
    lab = LABELS[lang]
    home_url = f"{origin}/" if lang == "en" else f"{origin}/es/"
    hub_url = f"{origin}{services_hub_path(lang)}"
    nav = soup.new_tag("nav", **{"aria-label": lab["breadcrumb_aria"]})
    nav["class"] = ["breadcrumb"]
    ol = soup.new_tag("ol")

    li1 = soup.new_tag("li")
    a1 = soup.new_tag("a", href=home_url)
    a1.string = lab["breadcrumb_home"]
    li1.append(a1)
    sep1 = soup.new_tag("li", **{"aria-hidden": "true"})
    sep1.string = "/"
    ol.append(li1)
    ol.append(sep1)

    items = [{"@type": "ListItem", "position": 1, "name": lab["breadcrumb_home"], "item": home_url}]

    if service_name is not None:
        li2 = soup.new_tag("li")
        a2 = soup.new_tag("a", href=hub_url)
        a2.string = lab["breadcrumb_services"]
        li2.append(a2)
        sep2 = soup.new_tag("li", **{"aria-hidden": "true"})
        sep2.string = "/"
        ol.append(li2)
        ol.append(sep2)
        items.append({"@type": "ListItem", "position": 2, "name": lab["breadcrumb_services"], "item": hub_url})

        li3 = soup.new_tag("li")
        cur = soup.new_tag("span", **{"aria-current": "page"})
        cur.string = service_name
        li3.append(cur)
        ol.append(li3)
        items.append({"@type": "ListItem", "position": 3, "name": service_name, "item": canonical})
    else:
        li2 = soup.new_tag("li")
        cur = soup.new_tag("span", **{"aria-current": "page"})
        cur.string = lab["breadcrumb_services"]
        li2.append(cur)
        ol.append(li2)
        items.append({"@type": "ListItem", "position": 2, "name": lab["breadcrumb_services"], "item": canonical})

    nav.append(ol)
    return nav, items


def cta_row(soup, lang):
    row = soup.new_tag("div", **{"data-stagger": ""})
    row["style"] = "display:flex;gap:14px;flex-wrap:wrap;margin-top:28px"
    lab = LABELS[lang]
    apply_a = soup.new_tag("a", href=f"{'/' if lang=='en' else '/es/'}#apply")
    apply_a["class"] = ["btn", "btn--primary", "btn--lg", "lift"]
    apply_a.append(lab["apply_cta"] + " ")
    arw = soup.new_tag("span", **{"class": "arw", "aria-hidden": "true"})
    arw.string = "→"
    apply_a.append(arw)
    check_a = soup.new_tag("a", href=f"{'/' if lang=='en' else '/es/'}#check")
    check_a["class"] = ["btn", "btn--secondary", "btn--lg", "lift"]
    check_a.string = lab["check_cta"]
    row.append(apply_a)
    row.append(check_a)
    return row


def build_service_body(soup, lang, service, cfg):
    lab = LABELS[lang]
    nap = cfg["nap"]
    content = service[lang]
    origin = cfg["domain"]["origin"]
    canonical = f"{origin}{service_page_path(lang, service['slug'])}"

    main = soup.new_tag("main", id="main")

    breadcrumb, breadcrumb_items = build_breadcrumb(soup, lang, service["name"], canonical, origin)
    main.append(breadcrumb)

    # --- Hero ---
    hero = soup.new_tag("section", **{"data-reveal": ""})
    hero["style"] = "padding:clamp(56px,8vw,96px) clamp(20px,5vw,64px) clamp(40px,6vw,64px)"
    eyebrow = soup.new_tag("p", **{"class": "eyebrow"})
    eyebrow.string = "SERVICES"
    h1 = soup.new_tag("h1")
    h1["style"] = "font-size:clamp(32px,4.4vw,48px);margin-top:14px;max-width:20ch"
    h1.string = content["h1"]
    lead = soup.new_tag("p")
    lead["style"] = "font-size:18px;line-height:1.6;color:var(--text-body);margin-top:18px;max-width:58ch"
    lead.string = content["lead"]
    hero.append(eyebrow)
    hero.append(h1)
    hero.append(lead)
    hero.append(cta_row(soup, lang))

    trust = soup.new_tag("p")
    trust["style"] = "margin-top:20px;font:600 13.5px var(--font-ui);color:var(--text-muted)"
    trust_phone = soup.new_tag("a", href=nap["phoneHref"])
    trust_phone["style"] = "color:inherit"
    trust_phone.string = nap["phoneDisplay"]
    trust.append(trust_phone)
    trust.append(f"  ·  {lab['trust_bilingual']}")
    hero.append(trust)
    main.append(hero)

    # --- Intro ---
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

    # --- What's included ---
    included = soup.new_tag("section", **{"data-reveal": "", "style": "padding:0 clamp(20px,5vw,64px) clamp(56px,8vw,88px);background:#F8F1E3"})
    inc_inner = soup.new_tag("div")
    inc_inner["style"] = "padding-top:clamp(56px,8vw,88px)"
    inc_eyebrow = soup.new_tag("p", **{"class": "eyebrow"})
    inc_eyebrow.string = lab["included_kicker"]
    inc_h2 = soup.new_tag("h2")
    inc_h2["style"] = "font-size:clamp(26px,3.2vw,36px);margin-top:12px"
    inc_h2.string = lab["included_heading"]
    ul = soup.new_tag("ul", **{"data-stagger": ""})
    ul["style"] = "list-style:none;margin-top:28px;display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px 24px;max-width:900px;padding:0"
    for item in content["included"]:
        li = soup.new_tag("li", **{"class": "lift"})
        li["style"] = "display:flex;align-items:flex-start;gap:10px;font-size:15.5px;color:var(--text-body);background:var(--color-cream);border:1px solid var(--border-rule);border-radius:var(--radius-md);padding:12px 14px"
        check = soup.new_tag("span", **{"aria-hidden": "true", "style": "color:var(--color-rust);font-weight:700"})
        check.string = "✓"
        li.append(check)
        span = soup.new_tag("span")
        span.string = item
        li.append(span)
        ul.append(li)
    inc_inner.append(inc_eyebrow)
    inc_inner.append(inc_h2)
    inc_inner.append(ul)
    included.append(inc_inner)
    main.append(included)

    # --- Why us ---
    why = soup.new_tag("section", **{"data-reveal": "", "style": "padding:clamp(56px,8vw,88px) clamp(20px,5vw,64px) 0"})
    why_eyebrow = soup.new_tag("p", **{"class": "eyebrow"})
    why_eyebrow.string = lab["why_kicker"]
    why_h2 = soup.new_tag("h2")
    why_h2["style"] = "font-size:clamp(26px,3.2vw,36px);margin-top:12px"
    why_h2.string = lab["why_heading"]
    why.append(why_eyebrow)
    why.append(why_h2)
    why_grid = soup.new_tag("div", **{"data-stagger": ""})
    why_grid["style"] = "margin-top:28px;display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px"
    for heading, body in content["why_us"]:
        card = soup.new_tag("div", **{"class": "lift"})
        card["style"] = "background:var(--color-cream-raised);border:1px solid var(--border-rule);border-radius:var(--radius-lg);padding:22px 24px"
        h3 = soup.new_tag("h3")
        h3["style"] = "font-size:18px;color:var(--color-forest)"
        h3.string = heading
        p = soup.new_tag("p")
        p["style"] = "margin-top:8px;font-size:14.5px;line-height:1.6;color:var(--text-body)"
        p.string = body
        card.append(h3)
        card.append(p)
        why_grid.append(card)
    why.append(why_grid)
    main.append(why)

    # --- Upsell / better-deal callout ---
    upsell = soup.new_tag("section", **{"data-reveal": "", "style": "padding:clamp(56px,8vw,88px) clamp(20px,5vw,64px)"})
    upsell_card = soup.new_tag("div", **{"class": "lift"})
    upsell_card["style"] = ("max-width:900px;margin:0 auto;background:var(--color-forest);border-radius:var(--radius-lg);"
                            "padding:clamp(28px,4vw,40px);display:flex;flex-wrap:wrap;gap:24px;align-items:center;justify-content:space-between")
    upsell_text = soup.new_tag("div")
    upsell_text["style"] = "max-width:520px"
    upsell_kicker = soup.new_tag("p")
    upsell_kicker["style"] = "font:700 12px var(--font-ui);letter-spacing:.1em;text-transform:uppercase;color:var(--color-gold);margin:0"
    upsell_kicker.string = "GET A BETTER DEAL" if lang == "en" else "CONSIGUE UN MEJOR PRECIO"
    upsell_h3 = soup.new_tag("h3")
    upsell_h3["style"] = "margin-top:10px;font-size:22px;color:var(--color-cream)"
    upsell_h3.string = content["upsell_h"]
    upsell_p = soup.new_tag("p")
    upsell_p["style"] = "margin-top:10px;font-size:14.5px;line-height:1.65;color:rgba(243,231,206,.85)"
    upsell_p.string = content["upsell_b"]
    upsell_text.append(upsell_kicker)
    upsell_text.append(upsell_h3)
    upsell_text.append(upsell_p)
    upsell_link = soup.new_tag("a", href=f"{'/' if lang=='en' else '/es/'}program/")
    upsell_link["class"] = ["btn", "btn--primary", "btn--lg", "lift"]
    upsell_link.append(("See the 30-Day Program" if lang == "en" else "Ve el Programa de 30 Días") + " ")
    arw2 = soup.new_tag("span", **{"class": "arw", "aria-hidden": "true"})
    arw2.string = "→"
    upsell_link.append(arw2)
    upsell_card.append(upsell_text)
    upsell_card.append(upsell_link)
    upsell.append(upsell_card)
    main.append(upsell)

    # --- FAQ ---
    faq = soup.new_tag("section", **{"data-reveal": "", "style": "padding:0 clamp(20px,5vw,64px) clamp(56px,8vw,88px)"})
    faq_eyebrow = soup.new_tag("p", **{"class": "eyebrow"})
    faq_eyebrow.string = lab["faq_kicker"]
    faq_h2 = soup.new_tag("h2")
    faq_h2["style"] = "font-size:clamp(26px,3.2vw,36px);margin-top:12px"
    faq_h2.string = lab["faq_heading"]
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

    # --- Related services ---
    related = soup.new_tag("section", **{"data-reveal": "", "style": "padding:0 clamp(20px,5vw,64px) clamp(56px,8vw,88px)"})
    r_eyebrow = soup.new_tag("p", **{"class": "eyebrow"})
    r_eyebrow.string = lab["related_kicker"]
    r_h2 = soup.new_tag("h2")
    r_h2["style"] = "font-size:clamp(24px,3vw,32px);margin-top:12px"
    r_h2.string = lab["related_heading"]
    r_row = soup.new_tag("div")
    r_row["style"] = "display:flex;gap:12px;flex-wrap:wrap;margin-top:20px"
    for other in SERVICES:
        if other["slug"] == service["slug"]:
            continue
        link = soup.new_tag("a", href=service_page_path(lang, other["slug"]))
        link["class"] = ["btn", "btn--secondary", "btn--sm", "lift"]
        link.string = other["name"]
        r_row.append(link)
    all_link = soup.new_tag("a", href=services_hub_path(lang))
    all_link["class"] = ["btn", "btn--ghost", "btn--sm", "lift"]
    all_link.string = lab["all_services_cta"] + " →"
    r_row.append(all_link)
    related.append(r_eyebrow)
    related.append(r_h2)
    related.append(r_row)
    main.append(related)

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
    arw3 = soup.new_tag("span", **{"class": "arw", "aria-hidden": "true"})
    arw3.string = "→"
    final_a.append(arw3)
    final_btn_wrap.append(final_a)
    final_note = soup.new_tag("p")
    final_note["style"] = "margin-top:14px;font:600 12.5px var(--font-ui);letter-spacing:.06em;color:rgba(243,231,206,.65)"
    final_note.string = lab["final_note"].upper()
    final.append(final_h2)
    final.append(final_btn_wrap)
    final.append(final_note)
    main.append(final)

    return main, breadcrumb_items


def build_service_head(lang, service, cfg, css, faqs, breadcrumb_items):
    content = service[lang]
    origin = cfg["domain"]["origin"]
    canonical = f"{origin}{service_page_path(lang, service['slug'])}"
    alt_en = f"{origin}{service_page_path('en', service['slug'])}"
    alt_es = f"{origin}{service_page_path('es', service['slug'])}"
    og_image = f"{origin}/assets/img/og-image.png"
    ga4 = (cfg.get("analytics") or {}).get("ga4MeasurementId") or ""

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
                "name": service["name"],
                "description": content["lead"],
                "provider": {"@id": f"{origin}/#organization"},
                "areaServed": {"@type": "AdministrativeArea", "name": cfg["serviceArea"]["region"]},
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

    return _head_html(content["title"], content["description"], canonical, alt_en, alt_es,
                      og_image, cfg, css, ga4, schema)


def _head_html(title, description, canonical, alt_en, alt_es, og_image, cfg, css, ga4, schema):
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

<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
<link rel="canonical" href="{canonical}">
{hreflang}

<meta name="theme-color" content="#F3E7CE">
<meta name="geo.region" content="US-OR">

<meta property="og:type" content="website">
<meta property="og:site_name" content="{escape(cfg['brand']['name'])}">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:image" content="{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Willamette Web Design">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{escape(title)}">
<meta name="twitter:description" content="{escape(description)}">
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


def build_hub_body(soup, lang, cfg):
    lab_hub = HUB[lang]
    nap = cfg["nap"]
    origin = cfg["domain"]["origin"]
    canonical = f"{origin}{services_hub_path(lang)}"

    main = soup.new_tag("main", id="main")
    breadcrumb, breadcrumb_items = build_breadcrumb(soup, lang, None, canonical, origin)
    main.append(breadcrumb)

    # --- Hero ---
    hero = soup.new_tag("section", **{"data-reveal": ""})
    hero["style"] = "padding:clamp(56px,8vw,96px) clamp(20px,5vw,64px) clamp(40px,6vw,64px)"
    eyebrow = soup.new_tag("p", **{"class": "eyebrow"})
    eyebrow.string = lab_hub["eyebrow"]
    h1 = soup.new_tag("h1")
    h1["style"] = "font-size:clamp(32px,4.4vw,48px);margin-top:14px;max-width:20ch"
    h1.string = lab_hub["h1"]
    lead = soup.new_tag("p")
    lead["style"] = "font-size:18px;line-height:1.6;color:var(--text-body);margin-top:18px;max-width:60ch"
    lead.string = lab_hub["lead"]
    hero.append(eyebrow)
    hero.append(h1)
    hero.append(lead)
    hero.append(cta_row(soup, lang))
    trust = soup.new_tag("p")
    trust["style"] = "margin-top:20px;font:600 13.5px var(--font-ui);color:var(--text-muted)"
    trust_phone = soup.new_tag("a", href=nap["phoneHref"])
    trust_phone["style"] = "color:inherit"
    trust_phone.string = nap["phoneDisplay"]
    trust.append(trust_phone)
    trust.append(f"  ·  {lab_hub['trust_bilingual']}")
    hero.append(trust)
    main.append(hero)

    # --- Honesty intro ---
    intro = soup.new_tag("section", **{"data-reveal": "", "style": "padding:0 clamp(20px,5vw,64px) clamp(40px,6vw,56px);border-top:1px solid var(--border-rule);margin-top:8px;padding-top:clamp(40px,6vw,56px)"})
    intro_p = soup.new_tag("p")
    intro_p["style"] = "font-size:16.5px;line-height:1.75;color:var(--text-body);max-width:760px"
    intro_p.string = lab_hub["intro"]
    intro.append(intro_p)
    main.append(intro)

    # --- Services grid ---
    grid_section = soup.new_tag("section", **{"data-reveal": "", "style": "padding:0 clamp(20px,5vw,64px) clamp(56px,8vw,88px)"})
    g_eyebrow = soup.new_tag("p", **{"class": "eyebrow"})
    g_eyebrow.string = lab_hub["grid_kicker"]
    g_h2 = soup.new_tag("h2")
    g_h2["style"] = "font-size:clamp(26px,3.2vw,36px);margin-top:12px"
    g_h2.string = lab_hub["grid_heading"]
    grid_section.append(g_eyebrow)
    grid_section.append(g_h2)

    grid = soup.new_tag("div", **{"data-stagger": ""})
    grid["style"] = "display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px;margin-top:28px"
    item_list = []
    for i, service in enumerate(SERVICES, start=1):
        content = service[lang]
        card = soup.new_tag("a", href=service_page_path(lang, service["slug"]), **{"class": "lift"})
        card["style"] = ("display:block;background:var(--color-cream-raised);border:1px solid var(--border-rule);"
                         "border-radius:var(--radius-lg);padding:22px 24px;text-decoration:none")
        name = soup.new_tag("span")
        name["style"] = "display:block;font:700 19px var(--font-display);color:var(--color-forest)"
        name.string = service["name"]
        desc = soup.new_tag("span")
        desc["style"] = "display:block;margin-top:8px;font-size:14px;line-height:1.55;color:var(--text-body)"
        desc.string = content["lead"]
        cta = soup.new_tag("span")
        cta["style"] = "display:inline-block;margin-top:14px;font:700 13px var(--font-ui);color:var(--color-rust)"
        cta.string = lab_hub["card_cta"] + " →"
        card.append(name)
        card.append(desc)
        card.append(cta)
        grid.append(card)

        service_canonical = f"{origin}{service_page_path(lang, service['slug'])}"
        item_list.append({"@type": "ListItem", "position": i, "name": service["name"], "url": service_canonical})

    grid_section.append(grid)
    main.append(grid_section)

    # --- Bundle callout ---
    bundle = soup.new_tag("section", **{"data-reveal": "", "style": "padding:clamp(56px,8vw,88px) clamp(20px,5vw,64px)"})
    bundle_card = soup.new_tag("div", **{"class": "lift"})
    bundle_card["style"] = ("max-width:900px;margin:0 auto;background:var(--color-forest);border-radius:var(--radius-lg);"
                            "padding:clamp(32px,5vw,48px);text-align:center")
    b_kicker = soup.new_tag("p")
    b_kicker["style"] = "font:700 12px var(--font-ui);letter-spacing:.1em;text-transform:uppercase;color:var(--color-gold);margin:0"
    b_kicker.string = lab_hub["bundle_kicker"]
    b_h2 = soup.new_tag("h2")
    b_h2["style"] = "margin-top:12px;font-size:clamp(24px,3vw,32px);color:var(--color-cream);max-width:26ch;margin-left:auto;margin-right:auto"
    b_h2.string = lab_hub["bundle_heading"]
    b_body = soup.new_tag("p")
    b_body["style"] = "margin-top:14px;font-size:15px;line-height:1.65;color:rgba(243,231,206,.85);max-width:60ch;margin-left:auto;margin-right:auto"
    b_body.string = lab_hub["bundle_body"]
    b_link = soup.new_tag("a", href=f"{'/' if lang=='en' else '/es/'}program/")
    b_link["class"] = ["btn", "btn--primary", "btn--lg", "lift"]
    b_link["style"] = "margin-top:22px"
    b_link.append(lab_hub["bundle_cta"] + " ")
    arw = soup.new_tag("span", **{"class": "arw", "aria-hidden": "true"})
    arw.string = "→"
    b_link.append(arw)
    bundle_card.append(b_kicker)
    bundle_card.append(b_h2)
    bundle_card.append(b_body)
    bundle_card.append(b_link)
    bundle.append(bundle_card)
    main.append(bundle)

    return main, breadcrumb_items, item_list


def build_hub_head(lang, cfg, css, breadcrumb_items, item_list):
    lab_hub = HUB[lang]
    origin = cfg["domain"]["origin"]
    canonical = f"{origin}{services_hub_path(lang)}"
    alt_en = f"{origin}{services_hub_path('en')}"
    alt_es = f"{origin}{services_hub_path('es')}"
    og_image = f"{origin}/assets/img/og-image.png"
    ga4 = (cfg.get("analytics") or {}).get("ga4MeasurementId") or ""

    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "@id": f"{canonical}#webpage",
                "url": canonical,
                "name": lab_hub["title"],
                "inLanguage": "en-US" if lang == "en" else "es-US",
                "isPartOf": {"@id": f"{origin}/#website"},
                "breadcrumb": {"@id": f"{canonical}#breadcrumb"},
            },
            {
                "@type": "BreadcrumbList",
                "@id": f"{canonical}#breadcrumb",
                "itemListElement": breadcrumb_items,
            },
            {
                "@type": "ItemList",
                "@id": f"{canonical}#servicelist",
                "itemListElement": item_list,
            },
        ],
    }

    return _head_html(lab_hub["title"], lab_hub["description"], canonical, alt_en, alt_es,
                      og_image, cfg, css, ga4, schema)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=".")
    args = ap.parse_args()
    out_root = pathlib.Path(args.out)

    cfg = json.loads((out_root / "site.config.json").read_text())
    css_src = minify_css((out_root / "assets/css/site.css").read_text())

    chrome = {lang: load_chrome(out_root, lang) for lang in ("en", "es")}

    for lang in ("en", "es"):
        lab = LABELS[lang]
        header_src, footer_src = chrome[lang]

        # --- individual service pages ---
        for service in SERVICES:
            soup = BeautifulSoup("<!doctype html>", "html.parser")
            header = BeautifulSoup(str(header_src), "html.parser").find("header")
            footer = BeautifulSoup(str(footer_src), "html.parser").find("footer")
            urls = {"en": service_page_path("en", service["slug"]), "es": service_page_path("es", service["slug"])}
            rewrite_chrome_links(header, lang, urls)
            rewrite_chrome_links(footer, lang, urls)

            body_main, breadcrumb_items = build_service_body(soup, lang, service, cfg)
            faqs = extract_faqs(body_main)

            html_str = (
                "<!doctype html>\n"
                f'<html lang="{lang}">\n<head>\n'
                + build_service_head(lang, service, cfg, css_src, faqs, breadcrumb_items)
                + "\n</head>\n<body>\n"
                + f'<a class="skip" href="#main">{lab["skip"]}</a>\n'
                + str(header) + "\n"
                + str(body_main) + "\n"
                + str(footer) + "\n"
                + '<script src="/assets/js/site.js" defer></script>\n'
                + "</body>\n</html>\n"
            )

            dest = out_root / service_page_path(lang, service["slug"]).strip("/") / "index.html"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(html_str, encoding="utf-8")
            print(f"{lang}/{service['slug']}: {dest.relative_to(out_root)}  {len(html_str)/1024:.1f} KB  ({len(faqs)} FAQ)")

        # --- services hub ---
        soup = BeautifulSoup("<!doctype html>", "html.parser")
        header = BeautifulSoup(str(header_src), "html.parser").find("header")
        footer = BeautifulSoup(str(footer_src), "html.parser").find("footer")
        urls = {"en": services_hub_path("en"), "es": services_hub_path("es")}
        rewrite_chrome_links(header, lang, urls)
        rewrite_chrome_links(footer, lang, urls)

        body_main, breadcrumb_items, item_list = build_hub_body(soup, lang, cfg)

        html_str = (
            "<!doctype html>\n"
            f'<html lang="{lang}">\n<head>\n'
            + build_hub_head(lang, cfg, css_src, breadcrumb_items, item_list)
            + "\n</head>\n<body>\n"
            + f'<a class="skip" href="#main">{lab["skip"]}</a>\n'
            + str(header) + "\n"
            + str(body_main) + "\n"
            + str(footer) + "\n"
            + '<script src="/assets/js/site.js" defer></script>\n'
            + "</body>\n</html>\n"
        )

        dest = out_root / services_hub_path(lang).strip("/") / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html_str, encoding="utf-8")
        print(f"{lang}/hub: {dest.relative_to(out_root)}  {len(html_str)/1024:.1f} KB")


if __name__ == "__main__":
    main()
