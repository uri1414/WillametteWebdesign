#!/usr/bin/env python3
"""
flatten-export.py — turn a design-tool export into shippable static HTML.

The homepage was authored in a visual builder that exports a *prototype*, not a
website: the real markup is JSON-escaped inside a `__bundler/template` script,
assets live in a `__bundler/manifest` blob, and the page depends on a ~69 KB
React runtime to resolve two custom elements:

  <sc-if value="{{cond}}">   conditional rendering (language, breakpoint, form state)
  <x-import component=...>   component instances (Button, Input)

Shipping that runtime would mean ~69 KB of main-thread work before a single
button renders. TBT is 30% of the Lighthouse score, so this script resolves
both constructs at build time instead:

  * language conditionals  -> two separate pages (/ and /es/), which also fixes
                              the duplicate element IDs the combined document had
  * breakpoint conditionals-> CSS utility classes (.u-desktop / .u-mobile)
  * form-state conditionals-> both states in the DOM, one hidden, toggled by ~1 KB of JS
  * components             -> plain <a>/<button>/<label> with CSS classes that
                              reproduce the component styles exactly

Usage:
    python3 scripts/flatten-export.py <export.html> [--out .]

Re-runnable: if the design is re-exported, run this again rather than
hand-patching the output.
"""

import argparse
import base64
import json
import pathlib
import re
import sys

from bs4 import BeautifulSoup

# Asset id -> the path it becomes in the repo. Ids come from the export's
# manifest; anything not listed here is reported so it can't be silently lost.
IMAGE_MAP = {
    "4aecfa65-d57d-4bcb-bcd8-bc7b1ad5d912": "valley-hero",
    "72ed8873-3c1c-4acb-9075-3f1821c8ed52": "logo-badge",
    "db0f784f-ffd1-41fb-843d-5aba8dfb554d": "program-badge",
}

# Responsive derivatives produced by scripts/optimize-images.mjs.
IMAGE_WIDTHS = {
    "valley-hero": [640, 960, 1280, 1717],
    "logo-badge": [46, 92, 138],
    "program-badge": [320, 640],
}
IMAGE_FALLBACK_EXT = {"valley-hero": "jpg", "logo-badge": "png", "program-badge": "png"}
IMAGE_INTRINSIC = {"valley-hero": (1717, 916), "logo-badge": (138, 138), "program-badge": (640, 427)}



DRAWER_CTA_LABEL = {
    "en": "Apply for the 30-Day Program",
    "es": "Aplica al Programa de 30 D\u00edas",
}


def drop_style_props(node, props):
    """Remove specific declarations from an inline style attribute.

    Inline styles beat stylesheet rules, so any property the CSS needs to own
    has to be taken out of the attribute rather than fought with !important.
    """
    style = node.get("style")
    if not style:
        return
    kept = [d for d in style.split(";")
            if d.strip() and d.split(":", 1)[0].strip().lower() not in props]
    if kept:
        node["style"] = ";".join(d.strip() for d in kept)
    else:
        del node["style"]


def unwrap(tag):
    """Replace a tag with its children, preserving order."""
    tag.unwrap()


def read_export(path):
    """Pull the escaped template and the asset manifest out of the export."""
    text = pathlib.Path(path).read_text(encoding="utf-8")
    lines = text.split("\n")

    # Match the literal opening tag, not a mention of the selector: the
    # export's own loader script references these type strings too, and a
    # substring match picks up those lines instead of the data blocks.
    template = manifest = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == '<script type="__bundler/template">':
            template = json.loads(lines[i + 1])
        elif stripped == '<script type="__bundler/manifest">':
            manifest = json.loads(lines[i + 1])

    if template is None:
        sys.exit("error: no __bundler/template block found — is this the right export?")
    return template, (manifest or {})


def resolve_buttons(soup):
    """<x-import Button> -> <a class="btn ..."> or <button class="btn ...">."""
    for node in soup.find_all("x-import"):
        comp = node.get("component-from-global-scope", "").split(".")[-1]
        if comp != "Button":
            continue

        href = node.get("href")
        variant = node.get("variant", "primary")
        size = node.get("size", "md")

        tag = soup.new_tag("a", href=href) if href else soup.new_tag("button", type="submit")
        classes = ["btn", f"btn--{variant}"]
        if size != "md":
            classes.append(f"btn--{size}")
        tag["class"] = classes

        # Split a trailing arrow into its own span so it can be animated
        # independently of the label.
        label = node.get_text(" ", strip=True)
        m = re.match(r"^(.*?)\s*([→↓←↑])$", label)
        if m:
            tag.append(m.group(1))
            arrow = soup.new_tag("span")
            arrow["class"] = "arw"
            arrow["aria-hidden"] = "true"
            arrow.string = m.group(2)
            tag.append(" ")
            tag.append(arrow)
        else:
            tag.string = label

        node.replace_with(tag)



# Label (either language) -> the canonical field name submitted to the backend.
FIELD_NAMES = [
    (("business", "negocio"), "business-name"),
    (("website", "sitio"), "website"),
    (("email", "correo"), "email"),
    (("phone", "tel"), "phone"),
    (("name", "nombre"), "name"),
]


def canonical_field_name(label, input_type):
    """Stable, language-independent name for a form field."""
    text = label.lower()
    if input_type == "email":
        return "email"
    for needles, name in FIELD_NAMES:
        if any(n in text for n in needles):
            return name
    # Fall back to an ASCII slug rather than emitting mangled accented bytes.
    slug = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return slug or "field"



def resolve_inputs(soup):
    """<x-import Input> -> <label class="field"> with a real, named control."""
    for node in soup.find_all("x-import"):
        comp = node.get("component-from-global-scope", "").split(".")[-1]
        if comp != "Input":
            continue

        label_text = node.get("label", "")
        placeholder = node.get("placeholder", "")
        input_type = node.get("type", "text")

        # Field names are data keys, not UI. Both language builds must submit
        # the SAME names or Netlify receives two different shapes under one form
        # and the submissions list becomes unusable. (Deriving the name from the
        # label also mangled accents: "Correo electronico" -> "correo-electr-nico".)
        slug = canonical_field_name(label_text, input_type)
        field_id = f"audit-{slug}"

        label = soup.new_tag("label")
        label["class"] = "field"
        label["for"] = field_id

        span = soup.new_tag("span")
        span["class"] = "field__label"
        span.string = label_text
        label.append(span)

        control = soup.new_tag("input")
        control["class"] = "field__input"
        control["type"] = input_type
        control["id"] = field_id
        control["name"] = slug
        control["placeholder"] = placeholder
        if input_type == "email":
            control["required"] = ""
            control["autocomplete"] = "email"
        elif slug == "business-name":
            control["required"] = ""
            control["autocomplete"] = "organization"
        elif slug == "website":
            control["autocomplete"] = "url"
        label.append(control)

        node.replace_with(label)



# The free audit form is the funnel's soft-conversion path. Netlify Forms gives
# it a real backend with no server to run: Netlify detects the form in the
# static HTML at deploy time, and posts to "/" are captured instead of routed.
NAP_CACHE = {}

AUDIT_FORM_COPY = {
    "en": {
        "sending": "Sending\u2026",
        "hp_label": "Leave this field empty",
        "error": "Something went wrong. Please call {phone} or email {email}.",
    },
    "es": {
        "sending": "Enviando\u2026",
        "hp_label": "Deja este campo vac\u00edo",
        "error": "Algo sali\u00f3 mal. Por favor llama al {phone} o escribe a {email}.",
    },
}


def wire_audit_form(soup, form, lang):
    copy = AUDIT_FORM_COPY[lang]

    form["data-audit-form"] = ""
    form["name"] = "audit"
    form["method"] = "post"
    form["action"] = "/"
    form["data-netlify"] = "true"
    form["data-netlify-honeypot"] = "company"
    form["data-sending-label"] = copy["sending"]
    # Localised failure copy, read by site.js. Handing over the phone number
    # keeps a warm lead recoverable when the POST fails.
    form["data-error-label"] = copy["error"].format(
        phone=NAP_CACHE["phoneDisplay"], email=NAP_CACHE["email"])

    # Netlify matches the submission to the form by this field.
    hidden = soup.new_tag("input", type="hidden")
    hidden["name"] = "form-name"
    hidden["value"] = "audit"
    form.insert(0, hidden)

    # Both languages post to the same form so submissions land in one list;
    # this keeps the lead's language with the lead.
    lang_field = soup.new_tag("input", type="hidden")
    lang_field["name"] = "language"
    lang_field["value"] = lang
    form.insert(1, lang_field)

    # Honeypot. Hidden from people and from assistive tech, irresistible to
    # bots. Named to match data-netlify-honeypot above.
    hp_wrap = soup.new_tag("p")
    hp_wrap["class"] = ["visually-hidden"]
    hp_wrap["aria-hidden"] = "true"
    hp_label = soup.new_tag("label")
    hp_label.string = copy["hp_label"]
    hp_input = soup.new_tag("input", type="text")
    hp_input["name"] = "company"
    hp_input["tabindex"] = "-1"
    hp_input["autocomplete"] = "off"
    hp_label.append(hp_input)
    hp_wrap.append(hp_label)
    form.append(hp_wrap)

    # A live region so the outcome is announced, not just shown.
    status = soup.new_tag("p")
    status["data-audit-status"] = ""
    status["role"] = "status"
    status["aria-live"] = "polite"
    status["hidden"] = ""
    status["style"] = "font:600 14px var(--font-ui);color:var(--color-rust);margin:0"
    form.append(status)



def resolve_conditionals(soup, lang, notes):
    """Resolve every <sc-if> for the given language build."""
    other = "es" if lang == "en" else "en"

    for node in list(soup.find_all("sc-if")):
        if node.decomposed:
            continue
        cond = re.sub(r"[{}\s]", "", node.get("value", ""))

        # --- language: keep this build's tree, discard the other ---
        if cond == lang:
            unwrap(node)
        elif cond == other:
            node.decompose()

        # --- breakpoint: becomes a CSS utility class, no JS needed ---
        elif cond in ("isDesktop", "isMobile"):
            wrapper = soup.new_tag("div")
            wrapper["class"] = "u-desktop" if cond == "isDesktop" else "u-mobile"
            node.wrap(wrapper)
            unwrap(node)

        # --- mobile drawer ---
        # The export left this as a sibling of <header>, in normal flow, so on
        # desktop it occupied real layout space even while transparent. Moved
        # inside the sticky header, where it can be an absolutely-positioned
        # dropdown that costs no layout at all when closed.
        elif cond == "menuOpen":
            nav = node.find("nav")
            if nav is not None:
                nav["id"] = "mobile-drawer"
                nav["class"] = (nav.get("class") or []) + ["drawer"]
                nav["data-drawer"] = ""
                # The export positioned this as a sticky flex block in body
                # flow. The stylesheet owns those properties now, so the inline
                # versions have to go or they win by specificity.
                drop_style_props(nav, {"position", "top", "z-index", "display",
                                       "border-bottom", "background", "padding"})
                # The blueprint calls for Apply to stay prominent on mobile,
                # inside the drawer. The export's drawer had navigation only,
                # and the header CTA is hidden at this width to stop it
                # colliding with the wordmark.
                cta = soup.new_tag("a", href="#apply")
                cta["class"] = ["btn", "btn--primary", "drawer-cta"]
                cta["data-drawer-close"] = ""
                cta.append(DRAWER_CTA_LABEL[lang])
                arrow = soup.new_tag("span")
                arrow["class"] = "arw"
                arrow["aria-hidden"] = "true"
                arrow.string = "\u2192"
                cta.append(" ")
                cta.append(arrow)
                nav.insert(0, cta)

                header = soup.find("header")
                if header is not None:
                    header.append(nav.extract())
            node.decompose()

        # --- audit form states: both present, success hidden until submit ---
        elif cond == "notSent":
            form = node.find("form")
            if form is not None:
                wire_audit_form(soup, form, lang)
            unwrap(node)
        elif cond == "sent":
            box = node.find("div")
            if box is not None:
                box["data-audit-success"] = ""
                box["hidden"] = ""
                box["class"] = (box.get("class") or []) + ["audit-success"]
            unwrap(node)

        # --- design-review placeholder notes: never ship these ---
        elif cond == "showPH":
            notes.append(node.get_text(" ", strip=True))
            node.decompose()

        else:
            notes.append(f"UNHANDLED sc-if condition: {cond!r}")
            unwrap(node)


def picture_for(name, *, sizes, cls=None, style=None, alt="", hero=False, lazy=True):
    """Build a <picture> with AVIF -> WebP -> fallback, width/height always set."""
    widths = IMAGE_WIDTHS[name]
    ext = IMAGE_FALLBACK_EXT[name]
    w, h = IMAGE_INTRINSIC[name]
    avif = ", ".join(f"/assets/img/{name}-{x}.avif {x}w" for x in widths)
    webp = ", ".join(f"/assets/img/{name}-{x}.webp {x}w" for x in widths)

    img_attrs = [
        f'src="/assets/img/{name}-{widths[-1]}.{ext}"',
        f'alt="{alt}"',
        f'width="{w}"', f'height="{h}"',
        'decoding="async"',
    ]
    if hero:
        img_attrs.append('fetchpriority="high"')
    elif lazy:
        img_attrs.append('loading="lazy"')
    if cls:
        img_attrs.append(f'class="{cls}"')
    if style:
        img_attrs.append(f'style="{style}"')

    return (
        "<picture>"
        f'<source type="image/avif" srcset="{avif}" sizes="{sizes}">'
        f'<source type="image/webp" srcset="{webp}" sizes="{sizes}">'
        f'<img {" ".join(img_attrs)}>'
        "</picture>"
    )



# ---------------------------------------------------------------------------
# Post-flatten transforms: everything below turns prototype conventions into
# production markup.
# ---------------------------------------------------------------------------

# Distinct style-hover values -> a CSS class each. The export encoded hover as a
# runtime attribute; :hover does the same thing with no JavaScript.
HOVER_CLASSES = {
    "color:var(--color-rust)": "h-rust",
    "color:var(--color-gold)": "h-gold",
    "opacity:1": "h-opaque",
    "background:var(--color-forest-faint)": "h-tint",
}


def fix_camel_attrs(soup):
    """`sc-camel-view-box` is a mangled `viewBox`. SVGs do not scale without it."""
    for node in soup.find_all(attrs={"sc-camel-view-box": True}):
        node["viewBox"] = node["sc-camel-view-box"]
        del node["sc-camel-view-box"]


def resolve_hovers(soup, used):
    for node in soup.find_all(attrs={"style-hover": True}):
        value = node["style-hover"].strip()
        cls = HOVER_CLASSES.get(value)
        if cls:
            node["class"] = (node.get("class") or []) + [cls]
            used.add(cls)
        del node["style-hover"]


def resolve_events(soup, lang):
    """Turn prototype click/submit handlers into real links and hooks."""
    other_home = "/es/" if lang == "en" else "/"

    for node in soup.find_all(attrs={"sc-camel-on-click": True}):
        handler = re.sub(r"[{}\s]", "", node["sc-camel-on-click"])
        del node["sc-camel-on-click"]

        if handler in ("setEs", "setEn"):
            # Language switching is URL-based, so each language is a real,
            # indexable page rather than a JS state flip.
            link = soup.new_tag("a", href=other_home)
            link["hreflang"] = "es" if lang == "en" else "en"
            link["class"] = (node.get("class") or []) + ["lang-switch"]
            if node.get("style"):
                link["style"] = node["style"]
            for child in list(node.contents):
                link.append(child.extract())
            node.replace_with(link)
        elif handler == "toggleMenu":
            node["data-drawer-toggle"] = ""
            node["aria-expanded"] = "false"
            node["aria-controls"] = "mobile-drawer"
        elif handler == "closeMenu":
            node["data-drawer-close"] = ""

    for node in soup.find_all(attrs={"sc-camel-on-submit": True}):
        del node["sc-camel-on-submit"]


def dedupe_hero(soup):
    """Collapse the two hero blocks into one element.

    The export rendered the valley illustration twice -- once inside the
    desktop branch, once inside the mobile branch -- because a runtime
    conditional meant only one ever existed. Flattened to CSS, both are in the
    DOM, and an <img> inside a `display:none` wrapper is still downloaded.
    That would have fetched the LCP image twice on every visit.

    Both branches used the same source, so one element plus responsive CSS
    does the job. The desktop copy is kept (it carries the gradient overlay)
    and the mobile duplicate is removed outright.
    """
    hero_section = soup.find("section", id="top")
    if hero_section is None:
        return

    desktop = hero_section.find("div", class_="u-desktop")
    mobile = hero_section.find("div", class_="u-mobile")

    if desktop is not None:
        desktop["class"] = ["hero-media"]

    if mobile is not None and mobile.find("img") is not None:
        mobile.decompose()


def swap_images(soup, lang):
    swap_images._logo_count = 0
    """Raw asset ids -> responsive <picture> with AVIF/WebP and real dimensions."""
    alt_text = {
        "valley-hero": {
            "en": "Illustration of the Willamette Valley: a river winding between forested hills under a setting sun",
            "es": "Ilustracion del valle de Willamette: un rio entre colinas boscosas bajo un sol poniente",
        },
        "logo-badge": {"en": "Willamette Web Design", "es": "Willamette Web Design"},
        "program-badge": {
            "en": "The Willamette 30-Day Program badge",
            "es": "Insignia del Programa de 30 Dias de Willamette",
        },
    }

    for img in list(soup.find_all("img")):
        src = img.get("src", "")
        name = IMAGE_MAP.get(src)
        if not name:
            continue

        style = img.get("style", "")
        alt = alt_text[name][lang]

        if name == "logo-badge":
            # Rendered at 46px. The source was 1254px -- serving it would have
            # been ~1.4 MB for a 46px mark. Eager (it is above the fold) but
            # never fetchpriority=high: only the LCP element earns that, and
            # marking several images high priority prioritises none of them.
            seen_logo = getattr(swap_images, "_logo_count", 0)
            swap_images._logo_count = seen_logo + 1
            first = seen_logo == 0
            markup = picture_for(name, sizes="46px", alt=alt, style=style,
                                 hero=False, lazy=not first)
        elif name == "valley-hero":
            # The LCP element. Preloaded in <head>, never lazy.
            sizes = "(max-width: 860px) 100vw, 58vw"
            markup = picture_for(name, sizes=sizes, alt=alt, style=style, hero=True, lazy=False)
        else:
            markup = picture_for(name, sizes="(max-width: 700px) 80vw, 320px", alt=alt, style=style)

        pic = BeautifulSoup(markup, "html.parser")
        # The <picture> must inherit the layout role the <img> had.
        if style:
            inner = pic.find("img")
            inner["style"] = style
        img.replace_with(pic)



def extract_faqs(soup):
    """Read the FAQ Q&A straight out of the rendered DOM.

    FAQPage schema must mirror the visible Q&A exactly -- Google suppresses the
    rich result otherwise, and the audit fails the build on a mismatch. Reading
    the questions and answers from the DOM we just built is the only way to
    guarantee they cannot drift: there is no second copy to fall out of sync.
    """
    faqs = []
    for det in soup.find_all("details"):
        summary = det.find("summary")
        if summary is None:
            continue

        # The summary carries the +/- indicator glyphs alongside the question.
        # Copy it, drop anything aria-hidden, and take what a reader actually
        # sees -- otherwise the schema would contain "... ? + -".
        q_node = BeautifulSoup(str(summary), "html.parser")
        for junk in q_node.find_all(attrs={"aria-hidden": "true"}):
            junk.decompose()
        for junk in q_node.find_all(class_=re.compile(r"fq-(plus|minus|chev)")):
            junk.decompose()
        question = " ".join(q_node.get_text(" ", strip=True).split())

        answer_parts = []
        for sib in summary.next_siblings:
            if getattr(sib, "get_text", None):
                answer_parts.append(sib.get_text(" ", strip=True))
            elif isinstance(sib, str):
                answer_parts.append(sib.strip())
        answer = " ".join(" ".join(answer_parts).split())

        if question and answer:
            faqs.append({"q": question, "a": answer})
    return faqs


def tag_footer_year(soup):
    """Mark the copyright year so site.js can keep it current.

    A hardcoded year is the kind of thing nobody notices until January, when
    every page quietly looks abandoned.
    """
    footer = soup.find("footer")
    if footer is None:
        return
    for span in footer.find_all("span"):
        text = span.get_text(" ", strip=True)
        m = re.search(r"(\u00a9|\(c\))\s*(\d{4})", text)
        if not m:
            continue
        year = m.group(2)
        before, _, after = text.partition(year)
        span.clear()
        span.append(before)
        y = soup.new_tag("span")
        y["data-year"] = ""
        y.string = year
        span.append(y)
        span.append(after)
        break


def tag_header_parts(soup):
    """Give the logo lockup real class hooks so CSS can adapt it responsively."""
    header = soup.find("header")
    if header is None:
        return
    logo = header.find("a")
    if logo is None:
        return
    logo["class"] = (logo.get("class") or []) + ["logo"]
    for span in logo.find_all("span", recursive=True):
        if span.get_text(" ", strip=True).upper().startswith("WEBSITES THAT GROW"):
            span["class"] = (span.get("class") or []) + ["logo-tagline"]
            break


def add_motion(soup):
    """Attach reveal/stagger/lift hooks. Purely additive -- no layout changes."""
    header = soup.find("header")
    if header is not None:
        header["class"] = (header.get("class") or []) + ["site-header"]
        header["data-header"] = ""

    # Nav links get the underline-wipe treatment.
    for nav in soup.find_all("nav"):
        for a in nav.find_all("a"):
            a["class"] = (a.get("class") or []) + ["nav-link"]

    # Hero children rise in sequence; everything below the fold reveals on scroll.
    sections = soup.find_all("section")
    for idx, section in enumerate(sections):
        if idx == 0:
            continue
        section["data-reveal"] = ""

    # FAQ accordions.
    for det in soup.find_all("details"):
        det["class"] = (det.get("class") or []) + ["faq-item"]

    # Card grids stagger their children.
    for node in soup.find_all(style=re.compile(r"grid-template-columns\s*:\s*repeat\(auto-f")):
        node["data-stagger"] = ""
        node["data-reveal"] = ""
        for child in node.find_all(recursive=False):
            child["class"] = (child.get("class") or []) + ["lift"]


# ---------------------------------------------------------------------------
# Content integrity
#
# The design mockup carried two invented trust signals. The funnel blueprint
# flags both itself ("the testimonial is sample copy"; "availability numbers
# must reflect live capacity"), and the SEO handbook's honesty rule overrides
# everything else: never fake a trust signal. Both are replaced here with copy
# that does the same persuasive job using only true statements.
# ---------------------------------------------------------------------------

# The mockup's sample quote, in both languages. Matching on the distinctive
# opening clause rather than the whole string keeps this robust to small copy
# edits in a re-export.
FAKE_TESTIMONIAL = {
    "en": "made the whole process easy",
    "es": "hizo todo el proceso f\u00e1cil",
}

HONEST_PROOF = {
    "en": {
        "heading": "What you get, before you pay a cent.",
        "body": ("Every project starts with a walkthrough of exactly what we'll build "
                 "for your business \u2014 the pages, the Google setup, the listings, "
                 "the tracking. You see the plan and the scope in writing before the "
                 "work begins."),
        "attrib": "Backed by the 30-day money-back satisfaction guarantee.",
    },
    "es": {
        "heading": "Lo que recibes, antes de pagar un centavo.",
        "body": ("Cada proyecto empieza con un repaso de exactamente lo que vamos a "
                 "construir para tu negocio \u2014 las p\u00e1ginas, la configuraci\u00f3n de Google, "
                 "los directorios, el seguimiento. Ves el plan y el alcance por escrito "
                 "antes de que empiece el trabajo."),
        "attrib": "Respaldado por la garant\u00eda de satisfacci\u00f3n de 30 d\u00edas.",
    },
}

HONEST_SCARCITY = {
    "en": {
        "eyebrow": "LIMITED MONTHLY INTAKE",
        "headline": "We take on a limited number of new businesses each month",
        "body": ("Every launch gets hands-on attention from the same small team, so we "
                 "cap how many we start at once. Apply and we'll tell you the next "
                 "available start date."),
    },
    "es": {
        "eyebrow": "CUPO MENSUAL LIMITADO",
        "headline": "Aceptamos un n\u00famero limitado de negocios nuevos cada mes",
        "body": ("Cada lanzamiento recibe atenci\u00f3n personal del mismo equipo peque\u00f1o, "
                 "as\u00ed que limitamos cu\u00e1ntos empezamos a la vez. Apl\u00edcate y te decimos "
                 "la pr\u00f3xima fecha disponible."),
    },
}


def fix_unverified_claims(soup, lang, notes):
    """Replace the invented testimonial and the hardcoded scarcity numbers."""
    proof = HONEST_PROOF[lang]
    scarcity = HONEST_SCARCITY[lang]

    # --- 1. The sample testimonial ---
    needle = FAKE_TESTIMONIAL[lang]
    for para in soup.find_all("p"):
        if needle in para.get_text():
            card = para.find_parent("div")
            if card is None:
                continue
            heading = card.find("div")
            if heading is not None:
                heading.string = proof["heading"]
            para.string = proof["body"]
            # The attribution line ("- Maria S., ...") names a client who does
            # not exist. Rewrite it to a claim that is true today.
            attrib = para.find_next_sibling("p")
            if attrib is not None:
                attrib.string = proof["attrib"]
            who = ("Maria S., Cleaning Services, Eugene" if lang == "en"
                   else "Mar\u00eda S., Servicios de Limpieza, Eugene")
            notes.append(
                f"REPLACED invented testimonial (\"{who}\") "
                "with a process-proof card. Swap in a real, permissioned client quote "
                "once one exists -- and only then."
            )
            break

    # --- 2. The hardcoded availability counter ---
    for node in soup.find_all(string=re.compile(r"AVAILABILITY|DISPONIBILIDAD")):
        span = node.parent
        span.string = scarcity["eyebrow"]
        card = span.find_parent("div")
        outer = card.find_parent("div") if card else None
        if outer is None:
            continue
        # The headline div carries the "Only N spots left" claim.
        for div in outer.find_all("div"):
            text = div.get_text(" ", strip=True)
            if re.search(r"(spots?|cupos?|lugares?)\b", text, re.I) and len(text) < 80:
                div.clear()
                div.string = scarcity["headline"]
                break
        for para in outer.find_all("p"):
            if re.search(r"\b\d+\b", para.get_text()):
                para.string = scarcity["body"]
                break
        notes.append(
            "REPLACED hardcoded scarcity (\"Only 2 spots left this month\", "
            "\"SEPTEMBER AVAILABILITY\", \"just 5 businesses at a time\") with the "
            "blueprint's approved honest line. A specific count must be true on the "
            "day it is read, and a hardcoded month goes stale."
        )
        break


def wire_contact_and_legal(soup, lang, cfg):
    """Insert the approved NAP and point the footer legal links at real pages."""
    nap = cfg["nap"]
    prefix = "" if lang == "en" else "/es"

    labels = {
        "en": {"privacy": "Privacy Policy", "terms": "Terms of Service"},
        "es": {"privacy": "Pol\u00edtica de Privacidad", "terms": "T\u00e9rminos del Servicio"},
    }[lang]

    for a in soup.find_all("a", href="#"):
        text = a.get_text(" ", strip=True).lower()
        if "privacy" in text or "privacidad" in text:
            a["href"] = f"{prefix}/privacy/"
            a.string = labels["privacy"]
        elif "terms" in text or "t\u00e9rminos" in text or "terminos" in text:
            a["href"] = f"{prefix}/terms/"
            a.string = labels["terms"]

    # The mockup omitted contact details pending approval; they are approved now.
    contact = soup.new_tag("div")
    contact["style"] = ("display:flex;flex-wrap:wrap;gap:18px;margin-top:14px;"
                        "font:400 13.5px var(--font-ui)")
    phone = soup.new_tag("a", href=nap["phoneHref"])
    phone["style"] = "color:#F8F1E3;opacity:.85;text-decoration:none"
    phone["class"] = ["h-opaque"]
    phone.string = nap["phoneDisplay"]
    email = soup.new_tag("a", href="mailto:" + nap["email"])
    email["style"] = "color:#F8F1E3;opacity:.85;text-decoration:none"
    email["class"] = ["h-opaque"]
    email.string = nap["email"]
    contact.append(phone)
    contact.append(email)

    footer = soup.find("footer")
    if footer is not None:
        anchor_p = footer.find("p")
        if anchor_p is not None:
            anchor_p.insert_after(contact)


# ---------------------------------------------------------------------------
# Page shell
# ---------------------------------------------------------------------------

META = {
    "en": {
        "path": "",
        "title": "Web Design & Local SEO in Oregon | Willamette Web Design",
        "description": ("We build your website and your whole online presence in 30 days "
                        "\u2014 Google, local SEO, listings and lead capture. Oregon-based, "
                        "English & Espa\u00f1ol."),
        "og_title": "Websites That Grow Local Businesses | Willamette Web Design",
        "og_desc": ("A complete local presence in 30 days: custom website, local SEO, "
                    "Google Business Profile, listings, and lead capture. Backed by a "
                    "30-day money-back satisfaction guarantee."),
        "og_alt": "Willamette Web Design \u2014 websites that grow local businesses",
        "locale": "en_US",
        "alt_locale": "es_ES",
        "skip": "Skip to content",
    },
    "es": {
        "path": "es/",
        "title": "Dise\u00f1o Web y SEO Local en Oregon | Willamette Web Design",
        "description": ("Construimos tu sitio web y toda tu presencia en l\u00ednea en 30 d\u00edas "
                        "\u2014 Google, SEO local, directorios y captura de clientes. En "
                        "Oregon, en ingl\u00e9s y espa\u00f1ol."),
        "og_title": "Sitios Web Que Hacen Crecer Negocios Locales | Willamette Web Design",
        "og_desc": ("Una presencia local completa en 30 d\u00edas: sitio web personalizado, "
                    "SEO local, Perfil de Negocio de Google, directorios y captura de "
                    "clientes. Con garant\u00eda de satisfacci\u00f3n de 30 d\u00edas."),
        "og_alt": "Willamette Web Design \u2014 sitios web que hacen crecer negocios locales",
        "locale": "es_ES",
        "alt_locale": "en_US",
        "skip": "Saltar al contenido",
    },
}


def build_head(lang, cfg, css, faqs=None):
    """The full <head>. Every tag here is required by scripts/audit.mjs."""
    m = META[lang]
    origin = cfg["domain"]["origin"]
    nap = cfg["nap"]
    canonical = f"{origin}/{m['path']}"
    og_image = f"{origin}/assets/img/og-image.png"
    ga4 = (cfg.get("analytics") or {}).get("ga4MeasurementId") or ""

    # Schema. Deliberately omitted: aggregateRating, Review, sameAs, and any
    # postal address -- none of those are verified yet, and inventing them
    # violates both the handbook and Google's guidelines.
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "@id": f"{origin}/#website",
                "url": f"{origin}/",
                "name": cfg["brand"]["name"],
                "inLanguage": "en-US" if lang == "en" else "es-US",
                "publisher": {"@id": f"{origin}/#organization"},
            },
            {
                "@type": ["Organization", "ProfessionalService"],
                "@id": f"{origin}/#organization",
                "name": cfg["brand"]["name"],
                "url": f"{origin}/",
                "email": nap["email"],
                "telephone": nap["phoneE164"],
                "image": og_image,
                "logo": {
                    "@type": "ImageObject",
                    "url": f"{origin}/assets/img/logo-badge-138.png",
                    "width": 138,
                    "height": 138,
                },
                "description": m["og_desc"],
                "knowsLanguage": ["en", "es"],
                "areaServed": [
                    {"@type": "City", "name": c} for c in
                    ["Albany, Oregon", "Corvallis, Oregon", "Salem, Oregon", "Lebanon, Oregon"]
                ] + [{"@type": "AdministrativeArea", "name": "Willamette Valley, Oregon"}],
                "address": {
                    "@type": "PostalAddress",
                    "addressRegion": "OR",
                    "addressCountry": "US",
                },
            },
            {
                "@type": "Service",
                "@id": f"{canonical}#service",
                "name": ("Website design and local presence setup"
                         if lang == "en" else
                         "Dise\u00f1o web y configuraci\u00f3n de presencia local"),
                "provider": {"@id": f"{origin}/#organization"},
                "areaServed": {"@type": "AdministrativeArea", "name": "Willamette Valley, Oregon"},
                "availableLanguage": ["en", "es"],
            },
        ],
    }

    # FAQPage, built from the visible Q&A so the two cannot disagree.
    if faqs:
        schema["@graph"].append({
            "@type": "FAQPage",
            "@id": f"{canonical}#faq",
            "isPartOf": {"@id": f"{origin}/#website"},
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": f["q"],
                    "acceptedAnswer": {"@type": "Answer", "text": f["a"]},
                }
                for f in faqs
            ],
        })

    hreflang = (
        f'<link rel="alternate" hreflang="en" href="{origin}/">\n'
        f'<link rel="alternate" hreflang="es" href="{origin}/es/">\n'
        f'<link rel="alternate" hreflang="x-default" href="{origin}/">'
    )

    analytics = ""
    if ga4:
        analytics = f"""
<!-- GA4, deferred to first interaction or 3s idle (handbook 2.6). Loading
     gtag.js directly in <head> costs ~66 KB of main-thread time during load,
     and TBT is 30% of the Lighthouse score. -->
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

<title>{m['title']}</title>
<meta name="description" content="{m['description']}">
<link rel="canonical" href="{canonical}">
{hreflang}

<meta name="theme-color" content="#F3E7CE">
<meta name="geo.region" content="US-OR">

<meta property="og:type" content="website">
<meta property="og:site_name" content="{cfg['brand']['name']}">
<meta property="og:locale" content="{m['locale']}">
<meta property="og:locale:alternate" content="{m['alt_locale']}">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{m['og_title']}">
<meta property="og:description" content="{m['og_desc']}">
<meta property="og:image" content="{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{m['og_alt']}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{m['og_title']}">
<meta name="twitter:description" content="{m['og_desc']}">
<meta name="twitter:image" content="{og_image}">

<link rel="icon" href="/favicon.ico" sizes="16x16 32x32 48x48">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">

<!-- Self-hosted fonts, preloaded so styled text is not waiting on CSS parse. -->
<link rel="preload" as="font" type="font/woff2" href="/assets/fonts/inter-latin.woff2" crossorigin>
<link rel="preload" as="font" type="font/woff2" href="/assets/fonts/roboto-slab-latin.woff2" crossorigin>

<!-- The LCP element. Preloading it starts the download before the CSS that
     positions it has even parsed. -->
<link rel="preload" as="image" type="image/avif"
      href="/assets/img/valley-hero-960.avif"
      imagesrcset="/assets/img/valley-hero-640.avif 640w, /assets/img/valley-hero-960.avif 960w, /assets/img/valley-hero-1280.avif 1280w, /assets/img/valley-hero-1717.avif 1717w"
      imagesizes="(max-width: 860px) 100vw, 58vw" fetchpriority="high">

<!-- Marks JS as available so the reveal styles may hide things. Without this
     class every [data-reveal] element renders plainly visible, so a failed or
     blocked script can never leave the page blank. Inline and synchronous by
     design: it must run before first paint. -->
<script>document.documentElement.className+=' js';</script>

<style id="site-css">{css}</style>
{analytics}
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(",", ":"))}</script>"""

def minify_css(css):
    css = re.sub(r"/\*(?!!)[\s\S]*?\*/", "", css)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{}:;,>~])\s*", r"\1", css)
    css = css.replace(";}", "}")
    return css.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("export")
    ap.add_argument("--out", default=".")
    args = ap.parse_args()

    out_root = pathlib.Path(args.out)
    cfg = json.loads((out_root / "site.config.json").read_text())
    NAP_CACHE.update(cfg["nap"])
    css_src = (out_root / "assets/css/site.css").read_text()

    template, manifest = read_export(args.export)

    unknown = {k for k, v in manifest.items() if v.get("mime", "").startswith("image/")} - set(IMAGE_MAP)
    if unknown:
        print("warning: unmapped image assets in the export:")
        for u in unknown:
            print(f"  {u}  ({manifest[u].get('mime')})")

    all_notes = {}

    for lang in ("en", "es"):
        soup = BeautifulSoup(template, "html.parser")
        notes = []

        for sel in ("helmet", "script"):
            for node in soup.find_all(sel):
                node.decompose()

        fix_camel_attrs(soup)
        tag_header_parts(soup)
        tag_footer_year(soup)
        resolve_conditionals(soup, lang, notes)
        resolve_buttons(soup)
        resolve_inputs(soup)
        resolve_events(soup, lang)
        resolve_hovers(soup, set())
        fix_unverified_claims(soup, lang, notes)
        wire_contact_and_legal(soup, lang, cfg)
        dedupe_hero(soup)
        swap_images(soup, lang)
        add_motion(soup)

        for node in soup.find_all("x-dc"):
            unwrap(node)

        faqs = extract_faqs(soup)

        body = soup.find("body")
        fragment = "".join(str(c) for c in body.children) if body else str(soup)

        leftover = BeautifulSoup(fragment, "html.parser").find_all(
            ["sc-if", "x-import", "x-dc", "helmet"])
        if leftover:
            print(f"  !! {lang}: {len(leftover)} unresolved custom element(s)")

        skip = META[lang]["skip"]
        page = (
            "<!doctype html>\n"
            f'<html lang="{lang}">\n<head>\n'
            + build_head(lang, cfg, minify_css(css_src), faqs)
            + "\n</head>\n<body>\n"
            + f'<a class="skip" href="#main">{skip}</a>\n'
            + '<main id="main">\n'
            + fragment
            + "\n</main>\n"
            + '<script src="/assets/js/site.js" defer></script>\n'
            + "</body>\n</html>\n"
        )

        dest = out_root / ("index.html" if lang == "en" else "es/index.html")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(page, encoding="utf-8")
        all_notes[lang] = notes
        print(f"{lang}: {dest.relative_to(out_root)}  {len(page)/1024:.1f} KB  "
              f"({len(faqs)} FAQ entries in schema)")

    notes_path = out_root / "docs/BUILD-NOTES.md"
    lines = [
        "# Build notes — generated by scripts/flatten-export.py",
        "",
        "Re-generated every time the design export is flattened. Do not edit by hand.",
        "",
        "## Placeholder notes removed from the mockup",
        "",
        "These were design-review annotations in the export. They are stripped from the",
        "shipped pages, and recorded here because each one is still an open item.",
        "",
    ]
    for lang in ("en", "es"):
        lines.append(f"### {lang.upper()}")
        lines.append("")
        for n in all_notes[lang]:
            lines.append(f"- {n}")
        lines.append("")
    notes_path.parent.mkdir(parents=True, exist_ok=True)
    notes_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nnotes -> {notes_path.relative_to(out_root)}")


if __name__ == "__main__":
    main()
