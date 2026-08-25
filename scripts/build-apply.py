#!/usr/bin/env python3
"""
build-apply.py -- generate the 30-Day Program application flow.

Writes four pages:
    /apply/              /es/apply/              the 4-step application
    /apply/thank-you/    /es/apply/thank-you/    the confirmation page

...and wires the homepage's "Apply" buttons to them. Copy and field
definitions live in scripts/apply_content.py; this file is only the machinery.

Like build-city-pages.py, it reuses the header and footer VERBATIM from the
already-built homepage rather than duplicating that markup, so the application
never drifts from the site's chrome. Run flatten-export.py first.

    python3 scripts/build-apply.py [--out .]

WHY A GENERATED PAGE AND NOT A HAND-WRITTEN ONE
    The EN and ES applications have to stay in lockstep: same steps, same field
    *names* (they are database columns -- see apply_content.py), same
    validation. Two hand-maintained files drift on the first edit; one
    generator with two copy dictionaries cannot.

THE FORM'S CONTRACT WITH THE BACKEND
    <form action="/.netlify/functions/application-start" method="post">
    With JavaScript off that is the whole flow: one post, one complete row,
    a 303 to the confirmation page. With JavaScript on, assets/js/apply.js
    takes over, submits step 1 on its own to create the 'partial' row, and
    finishes with /.netlify/functions/application-complete. Either way the
    application lands in Supabase and nothing depends on the visitor reaching
    the end.
"""

import argparse
import json
import pathlib
import re
import sys
from html import escape

from bs4 import BeautifulSoup

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build_lib import APPLY_PATH, minify_css, wire_apply_cta_html  # noqa: E402
from apply_content import PAGE, STEPS, THANKS  # noqa: E402

THANKS_PATH = {"en": "/apply/thank-you/", "es": "/es/apply/thank-you/"}
START_ENDPOINT = "/.netlify/functions/application-start"
COMPLETE_ENDPOINT = "/.netlify/functions/application-complete"
FORM_NAME = "application"
HONEYPOT = "company"

# Anchors that only exist on the homepage. Bare on that page; from anywhere
# else they have to point back at it explicitly or the browser simply fails to
# scroll, because the id is not on the current page.
HOMEPAGE_ANCHORS = {"how", "included", "about", "check", "top"}

BREADCRUMB_HOME = {"en": "Home", "es": "Inicio"}
BREADCRUMB_ARIA = {"en": "Breadcrumb", "es": "Ruta de navegación"}
BREADCRUMB_APPLY = {"en": "Apply", "es": "Aplicar"}
SKIP = {"en": "Skip to content", "es": "Saltar al contenido"}


# --------------------------------------------------------------------- chrome

def load_chrome(out_root, lang):
    src = out_root / ("index.html" if lang == "en" else "es/index.html")
    if not src.exists():
        sys.exit(f"error: {src} does not exist -- run flatten-export.py first")
    soup = BeautifulSoup(src.read_text(encoding="utf-8"), "html.parser")
    header, footer = soup.find("header"), soup.find("footer")
    if header is None or footer is None:
        sys.exit(f"error: {src} is missing a <header> or <footer> to reuse")
    return header, footer


def rewrite_chrome_links(node, lang, urls, *, on_apply_page):
    """Point homepage-only anchors and the language switch at the right place."""
    home = "/" if lang == "en" else "/es/"
    other = urls["es"] if lang == "en" else urls["en"]

    for a in node.find_all("a", href=True):
        href = a["href"]
        if "lang-switch" in (a.get("class") or []):
            a["href"] = other
        elif href in (APPLY_PATH["en"], APPLY_PATH["es"]):
            # The header/drawer "Apply" button. On the application page itself
            # it should jump to the form, not reload the page the visitor is on.
            a["href"] = "#application" if on_apply_page else APPLY_PATH[lang]
        elif href == "#top":
            a["href"] = home
        elif href.startswith("#") and href[1:] in HOMEPAGE_ANCHORS:
            a["href"] = f"{home}{href}"


# ----------------------------------------------------------------- form parts

def label_span(soup, text, required, lab):
    """The field's label, with an asterisk on the two fields that are required.

    Nothing is marked "(optional)". Only step 1 has required fields, so tagging
    the other twelve as optional would put a caveat on almost every line of the
    form and make it read as longer than it is. The asterisk marks the
    exception, which is what a marker is for.
    """
    span = soup.new_tag("span", **{"class": "field__label"})
    span.append(text)
    if required:
        req = soup.new_tag("span", **{"class": "field__req", "aria-hidden": "true"})
        req.string = " *"
        span.append(req)
    return span


def build_field(soup, field, lang, lab):
    """One field: a labelled input, textarea, or a group of real radios/checkboxes."""
    ftype = field["type"]
    name = field["name"]
    label_text = field["label"][lang]
    hint = (field.get("hint") or {}).get(lang)
    required = bool(field.get("required"))

    if ftype in ("radio", "checkbox"):
        group = soup.new_tag("fieldset", **{"class": "apply-group"})
        group["style"] = "border:0;padding:0;margin:0;min-width:0"
        if field.get("span"):
            group["class"] = ["apply-group", "apply-span"]
        legend = soup.new_tag("legend", **{"class": "apply-legend"})
        legend.string = label_text
        group.append(legend)
        if hint:
            h = soup.new_tag("span", **{"class": "field__hint"})
            h.string = hint
            group.append(h)
        choices = soup.new_tag("div", **{"class": "apply-choices"})
        for opt in field["options"]:
            lbl = soup.new_tag("label", **{"class": "apply-choice"})
            inp = soup.new_tag("input", type=ftype, value=opt["value"])
            inp["name"] = name if ftype == "radio" else f"{name}"
            lbl.append(inp)
            txt = soup.new_tag("span")
            txt.string = opt["label"][lang]
            lbl.append(txt)
            choices.append(lbl)
        group.append(choices)
        return group

    wrap = soup.new_tag("label", **{"class": "field", "for": f"apply-{name}"})
    if field.get("span"):
        wrap["class"] = ["field", "apply-span"]
    wrap.append(label_span(soup, label_text, required, lab))

    if ftype == "textarea":
        control = soup.new_tag("textarea", **{"class": "field__input", "id": f"apply-{name}"})
        control["name"] = name
        control["rows"] = str(field.get("rows", 3))
        control.string = ""
    else:
        control = soup.new_tag("input", **{"class": "field__input", "id": f"apply-{name}"})
        control["name"] = name
        control["type"] = ftype
    placeholder = (field.get("placeholder") or {}).get(lang)
    if placeholder:
        control["placeholder"] = placeholder
    if field.get("autocomplete"):
        control["autocomplete"] = field["autocomplete"]
    if required:
        control["required"] = ""
    wrap.append(control)

    if hint:
        h = soup.new_tag("span", **{"class": "field__hint"})
        h.string = hint
        wrap.append(h)
    return wrap


def build_step(soup, index, step, lang, lab):
    total = len(STEPS)
    fs = soup.new_tag("fieldset", **{"class": "apply-step", "data-apply-step": str(index)})
    if index > 0:
        # A class, deliberately, NOT the hidden attribute: `hidden` in the
        # markup would leave steps 2-4 -- and the submit button inside step 4 --
        # unreachable for a visitor without JavaScript. The CSS only acts on
        # .is-later under html.js, and apply.js drops the class as it takes
        # over, so there is no flash of the whole form either way.
        fs["class"] = ["apply-step", "is-later"]

    legend = soup.new_tag("legend", **{"class": "apply-step__legend"})
    legend.string = step["legend"][lang]
    fs.append(legend)

    note = soup.new_tag("p", **{"class": "apply-step__note"})
    note.string = step["note"][lang]
    fs.append(note)

    grid = soup.new_tag("div", **{"class": "apply-fields"})
    if step.get("two_up"):
        grid["class"] = ["apply-fields", "apply-fields--two"]
    for field in step["fields"]:
        grid.append(build_field(soup, field, lang, lab))
    fs.append(grid)

    is_last = index == total - 1
    nav = soup.new_tag("div", **{"class": "apply-nav" if is_last else "apply-nav apply-nav--steps"})

    if index > 0:
        back = soup.new_tag("button", type="button", **{"class": "btn btn--secondary", "data-apply-back": ""})
        back.string = lab["back"]
        nav.append(back)
        spacer = soup.new_tag("span", **{"class": "apply-nav__spacer"})
        nav.append(spacer)

    if is_last:
        submit = soup.new_tag("button", type="submit", **{"class": "btn btn--primary btn--lg apply-submit"})
        submit.append(lab["submit"] + " ")
        arw = soup.new_tag("span", **{"class": "arw", "aria-hidden": "true"})
        arw.string = "→"
        submit.append(arw)
        nav.append(submit)
    else:
        nxt = soup.new_tag("button", type="button", **{"class": "btn btn--primary", "data-apply-next": ""})
        nxt.append(lab["next"] + " ")
        arw = soup.new_tag("span", **{"class": "arw", "aria-hidden": "true"})
        arw.string = "→"
        nxt.append(arw)
        nav.append(nxt)

    fs.append(nav)
    return fs


def build_form(soup, lang, lab):
    form = soup.new_tag("form", **{
        "id": "application",
        "method": "post",
        "action": START_ENDPOINT,
        "data-apply-form": "",
        "data-apply-start": START_ENDPOINT,
        "data-apply-complete": COMPLETE_ENDPOINT,
        "data-apply-thanks": THANKS_PATH[lang],
        "data-apply-lang": lang,
        "data-sending-label": lab["sending"],
        "data-error-label": lab["error"],
        "data-required-label": lab["msg_required"],
        "data-contact-label": lab["msg_contact"],
        "data-invalid-label": lab["msg_invalid"],
        "data-netlify-honeypot": HONEYPOT,
    })

    # Which language the form was filled in, and the referral code when someone
    # arrived through a referral link. Both are columns on `applications`.
    for hidden_name, value in (("page_language", lang), ("referral_code", "")):
        h = soup.new_tag("input", type="hidden", value=value)
        h["name"] = hidden_name
        form.append(h)

    for i, step in enumerate(STEPS):
        form.append(build_step(soup, i, step, lang, lab))

    # Honeypot: a real person never fills in a field they cannot see.
    hp_wrap = soup.new_tag("p", **{"class": "visually-hidden", "aria-hidden": "true"})
    hp_label = soup.new_tag("label")
    hp_label.append(lab["honeypot"])
    hp_input = soup.new_tag("input", type="text", tabindex="-1", autocomplete="off")
    hp_input["name"] = HONEYPOT
    hp_label.append(hp_input)
    hp_wrap.append(hp_label)
    form.append(hp_wrap)

    status = soup.new_tag("p", **{
        "class": "apply-status", "data-apply-status": "", "role": "status",
        "aria-live": "polite", "hidden": "",
    })
    form.append(status)
    return form


def build_detection_form(soup):
    """The hidden form Netlify Forms parses at deploy time.

    Supabase is the source of truth; Netlify Forms is the backup that produces
    an email alert and a dashboard copy (netlify/functions/lib/db.js mirrors
    every submission into it). Netlify only accepts a submission for a form it
    found in the deployed HTML, so this declaration has to exist -- and it has
    to list every field the mirror sends, or those values are dropped.

    Every input is type=hidden: the fields are never filled in here, and a
    visible input with no label would be an accessibility defect on a form no
    one can see.
    """
    # attrs= rather than **kwargs: `name` is new_tag's own first parameter.
    form = soup.new_tag("form", attrs={"name": FORM_NAME, "data-netlify": "true",
                                       "data-netlify-honeypot": HONEYPOT, "hidden": ""})
    fields = ["form-name", "stage", "application_id", "page_language", HONEYPOT]
    fields += [f["name"] for step in STEPS for f in step["fields"]]
    for fname in fields:
        i = soup.new_tag("input", type="hidden")
        i["name"] = fname
        if fname == "form-name":
            i["value"] = FORM_NAME
        form.append(i)
    return form


# ---------------------------------------------------------------------- pages

def build_breadcrumb(soup, lang, canonical, origin):
    home_url = f"{origin}/" if lang == "en" else f"{origin}/es/"
    nav = soup.new_tag("nav", **{"aria-label": BREADCRUMB_ARIA[lang], "class": "breadcrumb"})
    ol = soup.new_tag("ol")
    li1 = soup.new_tag("li")
    a1 = soup.new_tag("a", href=home_url)
    a1.string = BREADCRUMB_HOME[lang]
    li1.append(a1)
    sep = soup.new_tag("li", **{"aria-hidden": "true"})
    sep.string = "/"
    li2 = soup.new_tag("li")
    cur = soup.new_tag("span", **{"aria-current": "page"})
    cur.string = BREADCRUMB_APPLY[lang]
    li2.append(cur)
    ol.append(li1); ol.append(sep); ol.append(li2)
    nav.append(ol)
    items = [
        {"@type": "ListItem", "position": 1, "name": BREADCRUMB_HOME[lang], "item": home_url},
        {"@type": "ListItem", "position": 2, "name": BREADCRUMB_APPLY[lang], "item": canonical},
    ]
    return nav, items


def build_apply_main(soup, lang, cfg, origin):
    lab = PAGE[lang]
    nap = cfg["nap"]
    canonical = f"{origin}{APPLY_PATH[lang]}"
    main = soup.new_tag("main", id="main")

    breadcrumb, breadcrumb_items = build_breadcrumb(soup, lang, canonical, origin)
    main.append(breadcrumb)

    intro = soup.new_tag("section", **{"data-reveal": ""})
    intro["style"] = "padding:clamp(40px,6vw,72px) clamp(20px,5vw,64px) clamp(28px,4vw,44px)"
    inner = soup.new_tag("div")
    inner["style"] = "max-width:1100px;margin:0 auto"
    eyebrow = soup.new_tag("p", **{"class": "eyebrow"})
    eyebrow.string = lab["eyebrow"]
    h1 = soup.new_tag("h1")
    h1["style"] = "font:700 clamp(32px,4.4vw,50px)/1.12 var(--font-display);color:var(--color-forest);margin:14px 0 0;max-width:16ch"
    h1.string = lab["h1"]
    lead = soup.new_tag("p")
    lead["style"] = "font:400 17px/1.65 var(--font-ui);color:var(--text-body);margin:18px 0 0;max-width:60ch"
    lead.string = lab["lead"]
    terms = soup.new_tag("p")
    terms["style"] = "font:600 14px/1.6 var(--font-ui);color:var(--color-forest);margin:20px 0 0"
    terms.string = lab["terms_line"]
    timing = soup.new_tag("p")
    timing["style"] = "font:400 14.5px/1.6 var(--font-ui);color:var(--text-muted);margin:8px 0 0;max-width:56ch"
    timing.string = lab["time_line"]
    for node in (eyebrow, h1, lead, terms, timing):
        inner.append(node)
    intro.append(inner)
    main.append(intro)

    body = soup.new_tag("section")
    body["style"] = "padding:0 clamp(20px,5vw,64px) clamp(64px,9vw,104px)"
    shell = soup.new_tag("div", **{"class": "apply-shell"})

    card = soup.new_tag("div", **{"class": "apply-card"})
    progress = soup.new_tag("div", **{"class": "apply-progress", "data-apply-progress": ""})
    plabel = soup.new_tag("p", **{"class": "apply-progress__label", "data-apply-progress-label": "",
                                  "data-apply-label": lab["step_of"],
                                  "role": "status", "aria-live": "polite"})
    plabel.string = lab["step_of"].format(n=1, total=len(STEPS))
    track = soup.new_tag("div", **{"class": "apply-progress__track", "aria-hidden": "true"})
    for i in range(len(STEPS)):
        seg = soup.new_tag("span", **{"class": "apply-progress__seg" + (" is-done" if i == 0 else ""),
                                      "data-apply-seg": str(i)})
        track.append(seg)
    progress.append(plabel)
    progress.append(track)
    card.append(progress)
    card.append(build_form(soup, lang, lab))
    shell.append(card)

    aside = soup.new_tag("aside", **{"class": "apply-aside", "data-reveal": ""})

    box1 = soup.new_tag("div", **{"class": "apply-aside__box"})
    h2a = soup.new_tag("h2")
    h2a.string = lab["aside_steps_heading"]
    box1.append(h2a)
    ol = soup.new_tag("ol")
    for item in lab["aside_steps"]:
        li = soup.new_tag("li")
        li.string = item
        ol.append(li)
    box1.append(ol)
    aside.append(box1)

    box2 = soup.new_tag("div", **{"class": "apply-aside__box"})
    h2b = soup.new_tag("h2")
    h2b.string = lab["aside_talk_heading"]
    box2.append(h2b)
    p2 = soup.new_tag("p")
    p2["style"] = "font:400 14.5px/1.6 var(--font-ui);color:var(--text-body);margin:0 0 12px"
    p2.string = lab["aside_talk"]
    box2.append(p2)
    contact = soup.new_tag("p")
    contact["style"] = "display:flex;flex-direction:column;gap:6px;margin:0;font:600 14.5px var(--font-ui)"
    tel = soup.new_tag("a", href=nap["phoneHref"])
    tel["class"] = ["h-rust"]
    tel["style"] = "color:var(--color-forest);text-decoration:none"
    tel.string = nap["phoneDisplay"]
    mail = soup.new_tag("a", href=f"mailto:{nap['email']}")
    mail["class"] = ["h-rust"]
    mail["style"] = "color:var(--color-forest);text-decoration:none"
    mail.string = nap["email"]
    contact.append(tel)
    contact.append(mail)
    box2.append(contact)
    aside.append(box2)

    box3 = soup.new_tag("div", **{"class": "apply-aside__box"})
    h2c = soup.new_tag("h2")
    h2c.string = lab["aside_check_heading"]
    box3.append(h2c)
    p3 = soup.new_tag("p")
    p3["style"] = "font:400 14.5px/1.6 var(--font-ui);color:var(--text-body);margin:0 0 14px"
    p3.string = lab["aside_check"]
    box3.append(p3)
    check_cta = soup.new_tag("a", href=("/#check" if lang == "en" else "/es/#check"))
    check_cta["class"] = ["btn", "btn--secondary", "btn--sm"]
    check_cta.string = lab["aside_check_cta"]
    box3.append(check_cta)
    aside.append(box3)

    shell.append(aside)
    body.append(shell)
    main.append(body)

    main.append(build_detection_form(soup))
    return main, breadcrumb_items


def build_thanks_main(soup, lang, cfg, origin):
    lab = THANKS[lang]
    nap = cfg["nap"]
    booking = (cfg.get("booking") or {}).get("url")
    main = soup.new_tag("main", id="main")

    section = soup.new_tag("section")
    section["style"] = "padding:clamp(64px,9vw,110px) clamp(20px,5vw,64px)"
    wrap = soup.new_tag("div", **{"class": "apply-confirm"})

    mark = soup.new_tag("div", **{"class": "apply-confirm__mark", "aria-hidden": "true"})
    mark.string = "✓"
    wrap.append(mark)

    h1 = soup.new_tag("h1")
    h1["style"] = "font:700 clamp(30px,4vw,46px)/1.15 var(--font-display);color:var(--color-forest);margin:0"
    h1.string = lab["h1"]
    wrap.append(h1)

    lead = soup.new_tag("p")
    lead["style"] = "font:400 17px/1.65 var(--font-ui);color:var(--text-body);margin:18px auto 0;max-width:52ch"
    lead.string = lab["lead"]
    wrap.append(lead)

    if booking:
        bwrap = soup.new_tag("div")
        bwrap["style"] = "margin-top:30px"
        bh = soup.new_tag("p")
        bh["style"] = "font:700 13px var(--font-ui);letter-spacing:.08em;color:var(--color-rust);margin:0 0 12px"
        bh.string = lab["booking_heading"].upper()
        bcta = soup.new_tag("a", href=booking, rel="noopener")
        bcta["class"] = ["btn", "btn--primary", "btn--lg"]
        bcta.append(lab["booking_cta"] + " ")
        arw = soup.new_tag("span", **{"class": "arw", "aria-hidden": "true"})
        arw.string = "→"
        bcta.append(arw)
        bwrap.append(bh)
        bwrap.append(bcta)
        wrap.append(bwrap)

    h2 = soup.new_tag("h2")
    h2["style"] = "font:700 15px var(--font-display);letter-spacing:.04em;color:var(--color-forest);margin:40px 0 0;text-transform:uppercase"
    h2.string = lab["steps_heading"]
    wrap.append(h2)

    ul = soup.new_tag("ul", **{"class": "apply-next"})
    for title, text in lab["steps"]:
        li = soup.new_tag("li")
        arrow = soup.new_tag("span", **{"aria-hidden": "true", "style": "color:var(--color-rust);font-weight:700"})
        arrow.string = "→"
        li.append(arrow)
        inner = soup.new_tag("span")
        b = soup.new_tag("b")
        b.string = title + " "
        inner.append(b)
        inner.append(text)
        li.append(inner)
        ul.append(li)
    wrap.append(ul)

    call = soup.new_tag("p")
    call["style"] = "font:400 15px/1.6 var(--font-ui);color:var(--text-body);margin:32px 0 0"
    before, after = lab["call_line"].split("{phone}")
    call.append(before)
    tel = soup.new_tag("a", href=nap["phoneHref"])
    tel["class"] = ["h-rust"]
    tel["style"] = "color:var(--color-forest);font-weight:700;text-decoration:none"
    tel.string = nap["phoneDisplay"]
    call.append(tel)
    call.append(after)
    wrap.append(call)

    home = soup.new_tag("div")
    home["style"] = "margin-top:26px"
    home_cta = soup.new_tag("a", href=("/" if lang == "en" else "/es/"))
    home_cta["class"] = ["btn", "btn--secondary"]
    home_cta.string = lab["home_cta"]
    home.append(home_cta)
    wrap.append(home)

    section.append(wrap)
    main.append(section)
    return main


# ----------------------------------------------------------------------- head

def build_head(*, lang, cfg, css, title, description, canonical, alt_en, alt_es,
               schema, noindex=False, extra_scripts=""):
    origin = cfg["domain"]["origin"]
    og_image = f"{origin}{cfg['social']['ogImage']}"
    ga4 = (cfg.get("analytics") or {}).get("ga4MeasurementId") or ""

    robots = '<meta name="robots" content="noindex, follow">\n' if noindex else ""

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
{robots}<link rel="alternate" hreflang="en" href="{alt_en}">
<link rel="alternate" hreflang="es" href="{alt_es}">
<link rel="alternate" hreflang="x-default" href="{alt_en}">

<meta name="theme-color" content="#F3E7CE">
<meta name="geo.region" content="US-OR">

<meta property="og:type" content="website">
<meta property="og:site_name" content="{escape(cfg['brand']['name'])}">
<meta property="og:locale" content="{'en_US' if lang == 'en' else 'es_ES'}">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:image" content="{og_image}">
<meta property="og:image:width" content="{cfg['social']['ogImageWidth']}">
<meta property="og:image:height" content="{cfg['social']['ogImageHeight']}">
<meta property="og:image:alt" content="{escape(cfg['social']['ogImageAlt'])}">
<meta name="twitter:card" content="{cfg['social']['twitterCard']}">
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
{analytics}{extra_scripts}
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(",", ":"))}</script>"""


def page_shell(*, lang, head, header, main, footer, scripts, prologue=""):
    return (
        "<!doctype html>\n"
        f'<html lang="{lang}">\n<head>\n'
        + head
        + "\n</head>\n<body>\n"
        + prologue
        + f'<a class="skip" href="#main">{SKIP[lang]}</a>\n'
        + str(header) + "\n"
        + str(main) + "\n"
        + str(footer) + "\n"
        + scripts
        + "</body>\n</html>\n"
    )


# ----------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=".")
    args = ap.parse_args()
    out_root = pathlib.Path(args.out)

    cfg = json.loads((out_root / "site.config.json").read_text())
    origin = cfg["domain"]["origin"]
    css_src = minify_css((out_root / "assets/css/site.css").read_text())

    # 1. Wire the homepage's Apply buttons to the page we are about to build.
    #    The same transform lives in flatten-export.py, so a re-export keeps it;
    #    this applies it to the homepage as it stands today.
    for lang in ("en", "es"):
        src = out_root / ("index.html" if lang == "en" else "es/index.html")
        before = src.read_text(encoding="utf-8")
        after = wire_apply_cta_html(before, lang)
        if before != after:
            src.write_text(after, encoding="utf-8")
            print(f"{lang}: wired homepage Apply buttons -> {APPLY_PATH[lang]}")

    chrome = {lang: load_chrome(out_root, lang) for lang in ("en", "es")}

    # 2. The application pages.
    for lang in ("en", "es"):
        soup = BeautifulSoup("<!doctype html>", "html.parser")
        header_src, footer_src = chrome[lang]
        header = BeautifulSoup(str(header_src), "html.parser").find("header")
        footer = BeautifulSoup(str(footer_src), "html.parser").find("footer")
        rewrite_chrome_links(header, lang, APPLY_PATH, on_apply_page=True)
        rewrite_chrome_links(footer, lang, APPLY_PATH, on_apply_page=True)

        canonical = f"{origin}{APPLY_PATH[lang]}"
        body_main, breadcrumb_items = build_apply_main(soup, lang, cfg, origin)
        program = cfg["pricing"]["program"]

        schema = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "WebPage",
                    "@id": f"{canonical}#webpage",
                    "url": canonical,
                    "name": PAGE[lang]["title"],
                    "inLanguage": "en-US" if lang == "en" else "es-US",
                    "isPartOf": {"@id": f"{origin}/#website"},
                    "about": {"@id": f"{origin}/#organization"},
                    "breadcrumb": {"@id": f"{canonical}#breadcrumb"},
                    "significantLink": f"{origin}{THANKS_PATH[lang]}",
                },
                {
                    "@type": "BreadcrumbList",
                    "@id": f"{canonical}#breadcrumb",
                    "itemListElement": breadcrumb_items,
                },
                {
                    "@type": "Offer",
                    "@id": f"{canonical}#offer",
                    "name": program["name"],
                    "price": str(program["price"]),
                    "priceCurrency": program["currency"],
                    "availability": "https://schema.org/InStock",
                    "url": canonical,
                    "offeredBy": {"@id": f"{origin}/#organization"},
                },
            ],
        }

        head = build_head(
            lang=lang, cfg=cfg, css=css_src,
            title=PAGE[lang]["title"], description=PAGE[lang]["description"],
            canonical=canonical,
            alt_en=f"{origin}{APPLY_PATH['en']}", alt_es=f"{origin}{APPLY_PATH['es']}",
            schema=schema,
        )
        html_str = page_shell(
            lang=lang, head=head, header=header, main=body_main, footer=footer,
            scripts=('<script src="/assets/js/site.js" defer></script>\n'
                     '<script src="/assets/js/apply.js" defer></script>\n'),
        )
        dest = out_root / APPLY_PATH[lang].strip("/") / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html_str, encoding="utf-8")
        print(f"{lang}: {dest.relative_to(out_root)}  {len(html_str)/1024:.1f} KB  "
              f"({len(STEPS)} steps)")

    # 3. The confirmation pages.
    for lang in ("en", "es"):
        soup = BeautifulSoup("<!doctype html>", "html.parser")
        header_src, footer_src = chrome[lang]
        header = BeautifulSoup(str(header_src), "html.parser").find("header")
        footer = BeautifulSoup(str(footer_src), "html.parser").find("footer")
        rewrite_chrome_links(header, lang, THANKS_PATH, on_apply_page=False)
        rewrite_chrome_links(footer, lang, THANKS_PATH, on_apply_page=False)

        canonical = f"{origin}{THANKS_PATH[lang]}"
        body_main = build_thanks_main(soup, lang, cfg, origin)
        schema = {
            "@context": "https://schema.org",
            "@graph": [{
                "@type": "WebPage",
                "@id": f"{canonical}#webpage",
                "url": canonical,
                "name": THANKS[lang]["title"],
                "inLanguage": "en-US" if lang == "en" else "es-US",
                "isPartOf": {"@id": f"{origin}/#website"},
                "about": {"@id": f"{origin}/#organization"},
            }],
        }
        head = build_head(
            lang=lang, cfg=cfg, css=css_src,
            title=THANKS[lang]["title"], description=THANKS[lang]["description"],
            canonical=canonical,
            alt_en=f"{origin}{THANKS_PATH['en']}", alt_es=f"{origin}{THANKS_PATH['es']}",
            schema=schema, noindex=True,
        )
        # A confirmation page has nothing to rank for and would only ever be a
        # thin, duplicate result -- and it can be reached by anyone who guesses
        # the URL, so it must never look like a landing page in search.
        prologue = ("<!-- audit-allow: noindex — a post-submission confirmation page has no "
                    "search intent to serve; indexing it would put a thin, duplicate page in "
                    "the index and let people land here without applying. -->\n")
        html_str = page_shell(
            lang=lang, head=head, header=header, main=body_main, footer=footer,
            scripts='<script src="/assets/js/site.js" defer></script>\n',
            prologue=prologue,
        )
        dest = out_root / THANKS_PATH[lang].strip("/") / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html_str, encoding="utf-8")
        print(f"{lang}: {dest.relative_to(out_root)}  {len(html_str)/1024:.1f} KB")

    booking = (cfg.get("booking") or {}).get("url")
    if not booking:
        print("\nnote: site.config.json booking.url is null, so the confirmation page "
              "shows no booking CTA.\n      Set it and re-run this script to add one "
              "(see docs/APPLICATION-SETUP.md).")


if __name__ == "__main__":
    main()
