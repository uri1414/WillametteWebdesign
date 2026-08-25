#!/usr/bin/env python3
"""
build-service-areas.py -- generate the /service-areas/ hub page (EN + ES).

The six dedicated /web-design-<city>-or/ pages (build-city-pages.py) only
cover part of the Willamette Valley. This hub page is the honest way to
cover the rest: it names the whole service region, links out to every
dedicated city page, and says plainly that other valley towns are served
too without inventing a dedicated page (and its fake specificity) for each
one. See CLAUDE.md's honesty rule -- no invented per-town claims here.

Reuses the header and footer VERBATIM from the already-built homepage, same
as the city pages, so it never drifts from that chrome -- run
flatten-export.py (or the homepage patch) and build-city-pages.py first,
though the order relative to build-city-pages.py does not matter here.

    python3 scripts/build-service-areas.py [--out .]
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
    service_areas_path,
)
from city_content import CITIES  # noqa: E402

LABELS = {
    "en": {
        "skip": "Skip to content",
        "breadcrumb_home": "Home",
        "breadcrumb_current": "Service Areas",
        "breadcrumb_aria": "Breadcrumb",
        "eyebrow": "SERVICE AREAS",
        "h1": "Web Design & Local SEO Across the Willamette Valley",
        "lead": ("One team, the whole valley. Six Mid-Willamette Valley cities "
                 "have their own dedicated page below -- and if your town isn't "
                 "one of them, we very likely still cover it."),
        "apply_cta": "Apply for the 30-Day Program",
        "check_cta": "Get a free presence check",
        "trust_bilingual": "English & Español",
        "cities_kicker": "DEDICATED CITY PAGES",
        "cities_heading": "Six cities, six local pages",
        "cities_body": ("Each city below gets its own page, written for that "
                        "city specifically -- not the same copy with the name "
                        "swapped."),
        "city_link_cta": "See details",
        "wider_kicker": "THE REST OF THE VALLEY",
        "wider_heading": "Don't see your town? We probably still cover it.",
        "wider_body": ("Willamette Web Design is a service-area business -- the "
                       "whole program runs by call, email, and video, so it "
                       "doesn't depend on a business being in one of the six "
                       "cities above. If you're anywhere in the Mid or South "
                       "Willamette Valley, get in touch and we'll tell you "
                       "plainly whether you're in range."),
        "faq_kicker": "COMMON QUESTIONS",
        "faq_heading": "Service area questions",
        "faq": [
            (
                "Is my town listed here?",
                "Only six cities have a dedicated page so far -- Albany, "
                "Corvallis, Salem, Lebanon, Keizer, and Woodburn. That's a "
                "starting list, not the full service area: we take on "
                "businesses across the wider Mid and South Willamette Valley "
                "too.",
            ),
            (
                "What if my business isn't in one of the six cities above?",
                "Reach out with your city name and we'll tell you directly "
                "whether you're in range -- most of the Willamette Valley is. "
                "The program runs the same way regardless of which town you're "
                "in: calls, email, and a couple of video check-ins, no local "
                "office required.",
            ),
            (
                "Do you charge more to work with a smaller town or a business "
                "further from the cities you list?",
                "No -- the $799 program and $99/month ongoing management are "
                "the same fixed price everywhere in the service area.",
            ),
        ],
    },
    "es": {
        "skip": "Saltar al contenido",
        "breadcrumb_home": "Inicio",
        "breadcrumb_current": "Áreas de Servicio",
        "breadcrumb_aria": "Ruta de navegación",
        "eyebrow": "ÁREAS DE SERVICIO",
        "h1": "Diseño Web y SEO Local en Todo el Valle de Willamette",
        "lead": ("Un solo equipo, todo el valle. Seis ciudades del valle medio "
                 "de Willamette tienen su propia página dedicada abajo -- y si "
                 "tu pueblo no es una de ellas, es muy probable que igual te "
                 "cubramos."),
        "apply_cta": "Aplica al Programa de 30 Días",
        "check_cta": "Obtén una revisión de presencia gratis",
        "trust_bilingual": "Inglés y Español",
        "cities_kicker": "PÁGINAS DEDICADAS POR CIUDAD",
        "cities_heading": "Seis ciudades, seis páginas locales",
        "cities_body": ("Cada ciudad abajo tiene su propia página, escrita "
                        "específicamente para esa ciudad -- no el mismo texto "
                        "con el nombre cambiado."),
        "city_link_cta": "Ver detalles",
        "wider_kicker": "EL RESTO DEL VALLE",
        "wider_heading": "¿No ves tu pueblo? Probablemente igual te cubrimos.",
        "wider_body": ("Willamette Web Design es un negocio de área de "
                       "servicio -- todo el programa funciona por llamada, "
                       "correo y video, así que no depende de que tu negocio "
                       "esté en una de las seis ciudades de arriba. Si estás "
                       "en cualquier parte del valle medio o sur de Willamette, "
                       "contáctanos y te diremos con claridad si estás dentro "
                       "del área."),
        "faq_kicker": "PREGUNTAS FRECUENTES",
        "faq_heading": "Preguntas sobre el área de servicio",
        "faq": [
            (
                "¿Está mi pueblo en esta lista?",
                "Por ahora solo seis ciudades tienen página dedicada -- "
                "Albany, Corvallis, Salem, Lebanon, Keizer y Woodburn. Esa es "
                "una lista inicial, no toda el área de servicio: también "
                "trabajamos con negocios en el resto del valle medio y sur de "
                "Willamette.",
            ),
            (
                "¿Qué pasa si mi negocio no está en una de las seis ciudades "
                "de arriba?",
                "Escríbenos con el nombre de tu ciudad y te diremos "
                "directamente si estás dentro del área -- la mayor parte del "
                "valle de Willamette lo está. El programa funciona igual sin "
                "importar en qué pueblo estés: llamadas, correo y un par de "
                "videollamadas, sin necesidad de oficina local.",
            ),
            (
                "¿Cobran más por trabajar con un pueblo más pequeño o más "
                "lejos de las ciudades que listan?",
                "No -- el programa de $799 y la gestión continua de $99/mes "
                "tienen el mismo precio fijo en toda el área de servicio.",
            ),
        ],
    },
}


def slug_url(lang, slug):
    return f"/web-design-{slug}-or/" if lang == "en" else f"/es/web-design-{slug}-or/"


def build_breadcrumb(soup, lang, canonical, origin):
    lab = LABELS[lang]
    home_url = f"{origin}/" if lang == "en" else f"{origin}/es/"
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
    cur.string = lab["breadcrumb_current"]
    li2.append(cur)
    ol.append(li1)
    ol.append(sep)
    ol.append(li2)
    nav.append(ol)
    return nav, [
        {"@type": "ListItem", "position": 1, "name": lab["breadcrumb_home"], "item": home_url},
        {"@type": "ListItem", "position": 2, "name": lab["breadcrumb_current"], "item": canonical},
    ]


def build_body(soup, lang, cfg):
    lab = LABELS[lang]
    nap = cfg["nap"]
    origin = cfg["domain"]["origin"]
    canonical = f"{origin}{service_areas_path(lang)}"

    main = soup.new_tag("main", id="main")

    breadcrumb, breadcrumb_items = build_breadcrumb(soup, lang, canonical, origin)
    main.append(breadcrumb)

    # --- Hero ---
    hero = soup.new_tag("section", **{"data-reveal": ""})
    hero["style"] = "padding:clamp(56px,8vw,96px) clamp(20px,5vw,64px) clamp(40px,6vw,64px)"
    eyebrow = soup.new_tag("p", **{"class": "eyebrow"})
    eyebrow.string = lab["eyebrow"]
    h1 = soup.new_tag("h1")
    h1["style"] = "font-size:clamp(32px,4.4vw,48px);margin-top:14px;max-width:22ch"
    h1.string = lab["h1"]
    lead = soup.new_tag("p")
    lead["style"] = "font-size:18px;line-height:1.6;color:var(--text-body);margin-top:18px;max-width:60ch"
    lead.string = lab["lead"]

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

    # --- Dedicated city pages grid ---
    cities_section = soup.new_tag("section", **{"data-reveal": "", "style": "padding:0 clamp(20px,5vw,64px) clamp(56px,8vw,88px);border-top:1px solid var(--border-rule);margin-top:8px;padding-top:clamp(56px,8vw,88px)"})
    c_eyebrow = soup.new_tag("p", **{"class": "eyebrow"})
    c_eyebrow.string = lab["cities_kicker"]
    c_h2 = soup.new_tag("h2")
    c_h2["style"] = "font-size:clamp(26px,3.2vw,36px);margin-top:12px"
    c_h2.string = lab["cities_heading"]
    c_body = soup.new_tag("p")
    c_body["style"] = "font-size:16.5px;line-height:1.7;color:var(--text-body);margin-top:14px;max-width:62ch"
    c_body.string = lab["cities_body"]

    grid = soup.new_tag("div", **{"data-stagger": ""})
    grid["style"] = "display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin-top:28px"
    item_list = []
    for i, city in enumerate(CITIES, start=1):
        content = city[lang]
        card = soup.new_tag("a", href=slug_url(lang, city["slug"]), **{"class": "lift"})
        card["style"] = ("display:block;background:var(--color-cream-raised);"
                          "border:1px solid var(--border-rule);border-radius:var(--radius-lg);"
                          "padding:20px 22px;text-decoration:none")
        name = soup.new_tag("span")
        name["style"] = "display:block;font:700 19px var(--font-display);color:var(--color-forest)"
        name.string = city["name"]
        county = soup.new_tag("span")
        county["style"] = "display:block;margin-top:4px;font:600 12.5px var(--font-ui);letter-spacing:.04em;color:var(--text-muted)"
        county.string = city["county"]
        cta = soup.new_tag("span")
        cta["style"] = "display:inline-block;margin-top:14px;font:700 13px var(--font-ui);color:var(--color-rust)"
        cta.string = lab["city_link_cta"] + " →"
        card.append(name)
        card.append(county)
        card.append(cta)
        grid.append(card)

        city_canonical = f"{origin}{slug_url(lang, city['slug'])}"
        item_list.append({
            "@type": "ListItem",
            "position": i,
            "name": content["h1"],
            "url": city_canonical,
        })

    cities_section.append(c_eyebrow)
    cities_section.append(c_h2)
    cities_section.append(c_body)
    cities_section.append(grid)
    main.append(cities_section)

    # --- The wider valley (honest, no invented per-town claims) ---
    wider = soup.new_tag("section", **{"data-reveal": "", "style": "padding:0 clamp(20px,5vw,64px) clamp(56px,8vw,88px);background:#F8F1E3"})
    w_inner = soup.new_tag("div")
    w_inner["style"] = "padding-top:clamp(56px,8vw,88px);max-width:760px"
    w_eyebrow = soup.new_tag("p", **{"class": "eyebrow"})
    w_eyebrow.string = lab["wider_kicker"]
    w_h2 = soup.new_tag("h2")
    w_h2["style"] = "font-size:clamp(26px,3.2vw,36px);margin-top:12px"
    w_h2.string = lab["wider_heading"]
    w_body = soup.new_tag("p")
    w_body["style"] = "font-size:16.5px;line-height:1.75;color:var(--text-body);margin-top:16px"
    w_body.string = lab["wider_body"]
    w_inner.append(w_eyebrow)
    w_inner.append(w_h2)
    w_inner.append(w_body)
    wider.append(w_inner)
    main.append(wider)

    # --- FAQ ---
    faq = soup.new_tag("section", **{"data-reveal": "", "style": "padding:clamp(56px,8vw,88px) clamp(20px,5vw,64px)"})
    faq_eyebrow = soup.new_tag("p", **{"class": "eyebrow"})
    faq_eyebrow.string = lab["faq_kicker"]
    faq_h2 = soup.new_tag("h2")
    faq_h2["style"] = "font-size:clamp(26px,3.2vw,36px);margin-top:12px"
    faq_h2.string = lab["faq_heading"]
    faq.append(faq_eyebrow)
    faq.append(faq_h2)
    faq_wrap = soup.new_tag("div")
    faq_wrap["style"] = "max-width:760px;margin-top:24px"
    for q, a in lab["faq"]:
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

    # --- Final CTA ---
    final = soup.new_tag("section", **{"style": "background:var(--color-forest);padding:clamp(64px,9vw,100px) clamp(20px,5vw,64px);text-align:center"})
    final_h2 = soup.new_tag("h2")
    final_h2["style"] = "color:var(--color-cream);font-size:clamp(28px,3.6vw,42px);max-width:20ch;margin:0 auto"
    final_h2.string = lab["h1"]
    final_btn_wrap = soup.new_tag("div")
    final_btn_wrap["style"] = "margin-top:28px"
    final_a = soup.new_tag("a", href=f"{'/' if lang=='en' else '/es/'}#apply")
    final_a["class"] = ["btn", "btn--primary", "btn--lg"]
    final_a.append(lab["apply_cta"] + " ")
    arw2 = soup.new_tag("span", **{"class": "arw", "aria-hidden": "true"})
    arw2.string = "→"
    final_a.append(arw2)
    final_btn_wrap.append(final_a)
    final.append(final_h2)
    final.append(final_btn_wrap)
    main.append(final)

    return main, breadcrumb_items, item_list


def build_head(lang, cfg, css, faqs, breadcrumb_items, item_list):
    lab = LABELS[lang]
    origin = cfg["domain"]["origin"]
    canonical = f"{origin}{service_areas_path(lang)}"
    alt_en = f"{origin}{service_areas_path('en')}"
    alt_es = f"{origin}{service_areas_path('es')}"
    og_image = f"{origin}/assets/img/og-image.png"
    ga4 = (cfg.get("analytics") or {}).get("ga4MeasurementId") or ""
    title = (f"Willamette Valley Service Areas | {cfg['brand']['name']}"
              if lang == "en" else
              f"Áreas de Servicio del Valle | {cfg['brand']['name']}")
    description = (
        "Web design and local SEO across the Willamette Valley: Albany, "
        "Corvallis, Salem, Lebanon, Keizer, Woodburn, and nearby towns. "
        "Bilingual. $799, 30 days."
        if lang == "en" else
        "Diseño web y SEO local en todo el valle de Willamette: Albany, "
        "Corvallis, Salem, Lebanon, Keizer, Woodburn y pueblos cercanos. "
        "Bilingüe. $799, 30 días."
    )

    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "@id": f"{canonical}#webpage",
                "url": canonical,
                "name": title,
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
                "name": ("Website design and local presence setup across the "
                         "Willamette Valley" if lang == "en" else
                         "Diseño web y presencia local en todo el valle de Willamette"),
                "provider": {"@id": f"{origin}/#organization"},
                "areaServed": {
                    "@type": "AdministrativeArea",
                    "name": cfg["serviceArea"]["region"],
                },
                "availableLanguage": ["en", "es"],
                "url": canonical,
            },
            {
                "@type": "ItemList",
                "@id": f"{canonical}#citylist",
                "itemListElement": item_list,
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=".")
    args = ap.parse_args()
    out_root = pathlib.Path(args.out)

    cfg = json.loads((out_root / "site.config.json").read_text())
    css_src = minify_css((out_root / "assets/css/site.css").read_text())

    for lang in ("en", "es"):
        lab = LABELS[lang]
        soup = BeautifulSoup("<!doctype html>", "html.parser")

        header_src, footer_src = load_chrome(out_root, lang)
        header = BeautifulSoup(str(header_src), "html.parser").find("header")
        footer = BeautifulSoup(str(footer_src), "html.parser").find("footer")
        urls = {"en": service_areas_path("en"), "es": service_areas_path("es")}
        rewrite_chrome_links(header, lang, urls)
        rewrite_chrome_links(footer, lang, urls)

        body_main, breadcrumb_items, item_list = build_body(soup, lang, cfg)

        faqs = extract_faqs(body_main)

        html_str = (
            "<!doctype html>\n"
            f'<html lang="{lang}">\n<head>\n'
            + build_head(lang, cfg, css_src, faqs, breadcrumb_items, item_list)
            + "\n</head>\n<body>\n"
            + f'<a class="skip" href="#main">{lab["skip"]}</a>\n'
            + str(header) + "\n"
            + str(body_main) + "\n"
            + str(footer) + "\n"
            + '<script src="/assets/js/site.js" defer></script>\n'
            + "</body>\n</html>\n"
        )

        dest = out_root / service_areas_path(lang).strip("/") / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html_str, encoding="utf-8")
        print(f"{lang}: {dest.relative_to(out_root)}  {len(html_str)/1024:.1f} KB  ({len(faqs)} FAQ)")


if __name__ == "__main__":
    main()
