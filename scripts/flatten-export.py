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

from build_lib import extract_faqs, minify_css, service_areas_path

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
        field_id = f"presence-{slug}"

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



# The free presence check form is the funnel's soft-conversion path. Netlify
# Forms gives it a real backend with no server to run: Netlify detects the form
# in the static HTML at deploy time, and posts to "/" are captured instead of
# routed.
NAP_CACHE = {}

PRESENCE_FORM_COPY = {
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


def wire_presence_form(soup, form, lang):
    copy = PRESENCE_FORM_COPY[lang]

    form["data-presence-form"] = ""
    form["name"] = "presence-check"
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
    hidden["value"] = "presence-check"
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
    status["data-presence-status"] = ""
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

        # --- presence check form states: both present, success hidden until submit ---
        elif cond == "notSent":
            form = node.find("form")
            if form is not None:
                wire_presence_form(soup, form, lang)
            unwrap(node)
        elif cond == "sent":
            box = node.find("div")
            if box is not None:
                box["data-presence-success"] = ""
                box["hidden"] = ""
                box["class"] = (box.get("class") or []) + ["presence-success"]
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
            #
            # Deliberately drops the export's inline `style` (desktop-only
            # absolute positioning) rather than passing it through: an inline
            # style always beats a class selector regardless of specificity,
            # which permanently overrode the .hero-media img rules in
            # site.css and broke the mobile layout those rules exist for
            # (the image ballooned to 488px wide, absolutely pinned to the
            # bottom-right corner of the whole hero section, on a 390px
            # viewport -- overlapping the CTAs and trust line beneath it).
            # .hero-media img in site.css already fully replicates the
            # desktop positioning for >=861px, so nothing is lost.
            sizes = "(max-width: 860px) 100vw, 58vw"
            markup = picture_for(name, sizes=sizes, alt=alt, hero=True, lazy=False)
        else:
            markup = picture_for(name, sizes="(max-width: 700px) 80vw, 320px", alt=alt, style=style)

        pic = BeautifulSoup(markup, "html.parser")
        # The <picture> must inherit the layout role the <img> had.
        if style:
            inner = pic.find("img")
            inner["style"] = style
        img.replace_with(pic)



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



def promote_card_headings(soup):
    """Turn heading-styled divs into real heading elements.

    The design export used <div> + inline font-display/bold styling to LOOK
    like a sub-heading -- for the eight deliverable cards, the four timeline
    steps, the guarantee card, the process-proof card, and the two pricing
    cards -- without a real heading tag. That flattens the document outline: a
    screen-reader user navigating by heading, or a search engine reading
    heading structure for topical relevance, sees only the page's eight <h2>s
    and nothing below them (SEO-PLAYBOOK.md 3: "logical H2/H3 hierarchy").

    Matched by style (font-family: var(--font-display) + bold weight, a short
    direct text run) rather than a hardcoded string list, so this keeps
    working after a copy edit or a re-export -- it does not need updating when
    the wording changes, only if the visual pattern itself changes.

    Must run AFTER fix_unverified_claims() and wire_contact_and_legal(), which
    locate specific divs by tag name (card.find("div")) to rewrite their text;
    promoting those divs to <h3> first would make that lookup fail silently.
    """
    for div in list(soup.find_all("div")):
        style = div.get("style", "")
        if not re.search(r"font:\s*\d+\s+\d+px[^;]*var\(--font-display\)", style):
            continue
        text = div.get_text(" ", strip=True)
        if not text or len(text) > 80:
            continue
        # The presence-check success message is transient UI state, not
        # crawled page content -- it gets its own aria-live treatment instead.
        if div.find_parent(attrs={"data-presence-success": True}) is not None:
            continue

        div.name = "h3"

        # The two pricing cards show a bare number ("$799"). Announced alone
        # that is meaningless to a screen reader, so borrow the eyebrow label
        # sitting directly above it ("ONE-TIME LAUNCH") for an accessible name.
        if re.fullmatch(r"\$\d[\d,]*(\s*/\s*(mo|mes))?", text):
            eyebrow = div.find_previous_sibling("div")
            if eyebrow is not None:
                label = eyebrow.get_text(" ", strip=True)
                div["aria-label"] = f"{label} \u2014 {text}"


GUARANTEE_HEADING = {
    "en": "30-Day Money-Back Satisfaction Guarantee",
    "es": "Garant\u00eda de Satisfacci\u00f3n de 30 D\u00edas con Devoluci\u00f3n de Dinero",
}


def add_missing_section_heading(soup, lang):
    """The Guarantee section has no <h2> at all in the source design.

    Every other section on the page follows eyebrow -> <h2> -> content. This
    one goes straight from the previous section's content into a two-card
    grid with no heading identifying what the section is about -- a real gap
    in the H2/H3 hierarchy (SEO-PLAYBOOK.md 3), not a cosmetic one: a screen
    reader user navigating by heading skips straight from "30 days" to
    "30-Day Guarantee" with nothing marking the section boundary, and a
    crawler reading heading structure for topical relevance gets the same gap.

    Inserted visually-hidden rather than as new visible copy: the fix is
    structural, and the approved design should not be second-guessed here just
    because the heading was missed. The wording is the blueprint's own
    approved headline for this section (FUNNEL-BLUEPRINT.md, section 07), not
    invented copy.
    """
    section = soup.find(attrs={"data-screen-label": re.compile(r"Guarantee")})
    if section is None:
        return
    h2 = soup.new_tag("h2")
    h2["class"] = ["visually-hidden"]
    h2.string = GUARANTEE_HEADING[lang]
    section.insert(0, h2)


def announce_presence_success(soup):
    """The presence-check success message needs a live region too.

    wire_presence_form() already made the sending/error status an
    aria-live="polite" region. The success swap (site.js sets form.hidden and
    reveals this block) goes through a different element and was missed --
    without this a screen-reader user who submits the form hears nothing at
    all when it succeeds.
    """
    success = soup.find(attrs={"data-presence-success": True})
    if success is not None:
        success["role"] = "status"
        success["aria-live"] = "polite"


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



# The approved blueprint (docs/FUNNEL-BLUEPRINT.md) names the soft-conversion
# offer "the free presence check" throughout. The design export instead wrote
# "audit" in every visible instance -- a drift from the approved copy, not an
# internal inconsistency (it was consistent, just consistently wrong). Fixed
# here rather than in the source export, so it survives a re-export.
RENAME_PRESENCE_CHECK = {
    "en": [
        ("FREE WEBSITE AUDIT", "FREE PRESENCE CHECK"),
        ("free audit", "free presence check"),
    ],
    "es": [
        ("AUDITOR\u00cdA GRATUITA", "REVISI\u00d3N DE PRESENCIA GRATIS"),
        ("AUDITOR\u00cdA GRATIS", "REVISI\u00d3N DE PRESENCIA GRATIS"),
        ("auditor\u00eda gratuita", "revisi\u00f3n de presencia gratuita"),
        ("auditor\u00eda gratis", "revisi\u00f3n de presencia gratis"),
    ],
}


def rename_presence_check(soup, lang):
    """Apply the presence-check renames to every visible text node.

    Walks NavigableStrings rather than the raw HTML so a replacement can never
    land inside an attribute or a <script>/<style> block.
    """
    from bs4 import NavigableString

    pairs = RENAME_PRESENCE_CHECK[lang]
    for node in soup.find_all(string=True):
        if not isinstance(node, NavigableString):
            continue
        if node.find_parent(["script", "style"]) is not None:
            continue
        text = str(node)
        replaced = text
        for old, new in pairs:
            replaced = replaced.replace(old, new)
        if replaced != text:
            node.replace_with(replaced)



def link_service_area(soup, lang, cfg):
    """Turn the footer's plain-text city list into real links to the city pages.

    SEO-PLAYBOOK.md section 2 calls for city pages to be linked "from a
    Service Area dropdown in the nav + the footer" -- without this, the new
    /web-design-<city>-or/ pages have no path in from the site's only
    well-linked page, and a crawler has to find them through the sitemap
    alone. The nav half of that is add_service_area_nav(), below.

    The slug here (city name, lowercased) must match slugify_path() in
    build-city-pages.py -- true for the four approved cities today, but if a
    city with a multi-word name is ever added, both places need updating
    together.
    """
    cities = (cfg.get("serviceArea") or {}).get("cities") or []
    if not cities:
        return

    needle = "Albany \u00b7 Corvallis \u00b7 Salem \u00b7 Lebanon"
    target = soup.find(string=lambda t: t and needle in t)
    if target is not None:
        parent = target.parent
    else:
        # Re-run against chrome that was already linked by a previous run
        # (e.g. patching a built page directly instead of re-flattening the
        # export): locate the existing per-city link list by its href
        # pattern rather than the original plain-text needle, so adding a
        # city to site.config.json and re-running stays idempotent.
        existing = soup.find("a", href=re.compile(r"^/(es/)?web-design-[a-z]+-or/$"))
        if existing is None:
            return
        parent = existing.parent

    parent.clear()

    prefix = "/" if lang == "en" else "/es/"
    for i, city in enumerate(cities):
        if i > 0:
            parent.append(" \u00b7 ")
        a = soup.new_tag("a", href=f"{prefix}web-design-{city.lower()}-or/")
        a["class"] = ["h-opaque"]
        a["style"] = "color:inherit"
        a.string = city
        parent.append(a)

    parent.append(" + ")
    hub = soup.new_tag("a", href=service_areas_path(lang))
    hub["class"] = ["h-opaque"]
    hub["style"] = "color:inherit;text-decoration:underline"
    hub.string = ("surrounding Oregon communities" if lang == "en"
                  else "comunidades cercanas de Oregon")
    parent.append(hub)


NAV_SERVICE_AREA_LABEL = {"en": "SERVICE AREAS", "es": "ÁREAS DE SERVICIO"}
NAV_ALL_AREAS_LABEL = {"en": "All service areas", "es": "Todas las áreas"}


def add_service_area_nav(soup, lang, cfg):
    """Add the "Service Area" dropdown SEO-PLAYBOOK.md sec.2 step 5 calls for.

    The footer link list (link_service_area, above) gives crawlers a path in,
    but a human visitor never scrolls to the footer looking for navigation --
    the header nav is the only place people actually look. A <details> menu
    keeps this native and keyboard-accessible with zero JS, matching how the
    FAQ accordions already work on this site.
    """
    cities = (cfg.get("serviceArea") or {}).get("cities") or []
    header = soup.find("header")
    if header is None or not cities:
        return

    prefix = "/" if lang == "en" else "/es/"
    label = NAV_SERVICE_AREA_LABEL[lang]

    def build_dropdown():
        dd = soup.new_tag("details", **{"class": "nav-dropdown"})
        summary = soup.new_tag("summary")
        summary.string = label
        dd.append(summary)
        menu = soup.new_tag("div", **{"class": "nav-dropdown__menu"})
        for city in cities:
            a = soup.new_tag("a", href=f"{prefix}web-design-{city.lower()}-or/")
            a.string = city
            menu.append(a)
        all_areas = soup.new_tag("a", href=service_areas_path(lang), **{"class": "nav-dropdown__all"})
        all_areas.string = NAV_ALL_AREAS_LABEL[lang]
        menu.append(all_areas)
        dd.append(menu)
        return dd

    desktop_nav = header.select_one(".u-desktop nav")
    if desktop_nav is not None:
        lang_a = desktop_nav.find("a", class_="lang-switch")
        if lang_a is not None and lang_a.parent is not None:
            lang_a.parent.insert_before(build_dropdown())
        else:
            desktop_nav.append(build_dropdown())

    drawer_nav = header.find("nav", class_="drawer")
    if drawer_nav is not None:
        lang_a = drawer_nav.find("a", class_="lang-switch")
        if lang_a is not None:
            lang_a.insert_before(build_dropdown())
        else:
            drawer_nav.append(build_dropdown())


PRESENCE_CHECK_CARD = {
    "en": {
        "eyebrow": "FREE PRESENCE CHECK",
        "amount": "Free",
        "body": ("No commitment — a written report on exactly where you're "
                 "losing local customers. Yours to keep, whether you hire us "
                 "or not."),
        "cta": "Get my free presence check",
    },
    "es": {
        "eyebrow": "REVISIÓN DE PRESENCIA GRATIS",
        "amount": "Gratis",
        "body": ("Sin compromiso — un informe escrito que muestra exactamente "
                 "dónde estás perdiendo clientes locales. Es tuyo, nos "
                 "contrates o no."),
        "cta": "Obtén mi revisión de presencia",
    },
}


def add_presence_check_card(soup, lang):
    """Add a third card to the pricing grid for the free presence check.

    The "value + pricing" section only ever showed the two paid tiers
    (one-time launch, ongoing management) -- the soft-conversion path had no
    presence here at all, even though CLAUDE.md calls the presence check "the
    single highest-leverage element on the page". This is a teaser card that
    matches the other two visually and links to the real form at #check
    further down the page, not a second copy of the form itself (a duplicate
    <form name="presence-check"> would confuse Netlify Forms' detection and
    collide on field ids).
    """
    grid = soup.find("div", style=lambda s: s and
                      "grid-template-columns:repeat(auto-fit,minmax(280px,1fr))" in s)
    if grid is None:
        return
    cards = grid.find_all("div", recursive=False)
    if len(cards) != 2:
        return  # already patched, or the export's structure changed

    copy = PRESENCE_CHECK_CARD[lang]

    card = soup.new_tag("div", **{"class": "lift"})
    card["style"] = "border:1px solid var(--color-river);border-radius:10px;padding:32px"

    eyebrow = soup.new_tag("div")
    eyebrow["style"] = "font:700 12px var(--font-ui);letter-spacing:.1em;color:var(--color-river)"
    eyebrow.string = copy["eyebrow"]

    amount = soup.new_tag("h3", **{"aria-label": f"{copy['eyebrow']} — {copy['amount']}"})
    amount["style"] = "font:800 46px/1 var(--font-display);color:var(--color-forest);margin-top:10px"
    amount.string = copy["amount"]

    body = soup.new_tag("p")
    body["style"] = "font:400 15px/1.6 var(--font-ui);color:var(--text-body);margin:14px 0 0"
    body.string = copy["body"]

    cta_wrap = soup.new_tag("div")
    cta_wrap["style"] = "margin-top:22px"
    cta = soup.new_tag("a", href="#check", **{"class": "btn btn--secondary"})
    cta.append(copy["cta"] + " ")
    arw = soup.new_tag("span", **{"aria-hidden": "true", "class": "arw"})
    arw.string = "→"
    cta.append(arw)
    cta_wrap.append(cta)

    card.append(eyebrow)
    card.append(amount)
    card.append(body)
    card.append(cta_wrap)
    grid.append(card)


TRACK_RECORD_CARD = {
    "en": {
        "heading": "Already done once — in about 2 weeks.",
        "body": ("Two Willamette Valley businesses have been through this exact "
                 "process: full website, Google Business Profile, and listings "
                 "on Yelp, Nextdoor, Apple Business, Bing, and Facebook — all "
                 "live and connected in about two weeks. What usually takes "
                 "months of piecing tools together happened inside one "
                 "program."),
    },
    "es": {
        "heading": "Ya lo hicimos una vez — en unas 2 semanas.",
        "body": ("Dos negocios del valle de Willamette pasaron por este mismo "
                 "proceso completo: sitio web, Perfil de Negocio de Google, y "
                 "directorios en Yelp, Nextdoor, Apple Business, Bing y "
                 "Facebook — todo conectado y en línea en unas dos semanas. "
                 "Lo que normalmente toma meses juntando herramientas por "
                 "separado, pasó dentro de un solo programa."),
    },
}


def add_track_record_card(soup, lang):
    """Add a fourth card to the guarantee/trust grid: real, completed work.

    Two businesses have actually been through the full program (same scope
    as the $799 offer) under this brand -- see CLAUDE.md's "Proof" note. This
    states only what is true today: no client is named (that needs their
    permission and an actual quote first -- see CLAUDE.md), no rating or
    review schema is added, no count is rounded up. Once a named,
    permissioned quote exists, that becomes a real testimonial -- this card
    does not need to wait for that to say something honest right now.
    """
    section = soup.find(attrs={"data-screen-label": lambda v: v and v.startswith("07 Guarantee")})
    if section is None:
        return
    grid = section.find("div", style=lambda s: s and
                         "grid-template-columns:repeat(auto-fit,minmax(280px,1fr))" in s)
    if grid is None:
        return
    cards = grid.find_all("div", recursive=False)
    if len(cards) != 3:
        return  # already patched, or the export's structure changed

    copy = TRACK_RECORD_CARD[lang]

    # grid-column:1/-1 spans the full row on the auto-fit grid instead of
    # sitting alone in a fourth column-track with empty space beside it (the
    # other three cards fill the row evenly; a lone fourth card would not).
    # A wide banner also suits "highlight this" better than a same-sized
    # fourth card would.
    card = soup.new_tag("div", **{"class": "lift"})
    card["style"] = ("grid-column:1/-1;background:#F8F1E3;border:1px solid var(--border-rule);"
                      "border-radius:10px;padding:32px;display:flex;gap:24px;"
                      "flex-wrap:wrap;align-items:flex-start")

    icon = soup.new_tag("svg", **{
        "width": "30", "height": "30", "viewBox": "0 0 24 24", "fill": "none",
        "stroke": "#233D32", "stroke-width": "1.75", "stroke-linecap": "round",
        "stroke-linejoin": "round", "style": "flex-shrink:0",
    })
    circle = soup.new_tag("circle", cx="12", cy="12", r="10")
    check = soup.new_tag("path", d="m9 12 2 2 4-4")
    icon.append(circle)
    icon.append(check)

    text = soup.new_tag("div")
    text["style"] = "flex:1;min-width:240px"

    h3 = soup.new_tag("h3")
    h3["style"] = "font:700 20px var(--font-display);color:var(--color-forest)"
    h3.string = copy["heading"]

    body = soup.new_tag("p")
    body["style"] = "font:400 15px/1.6 var(--font-ui);color:var(--text-body);margin:10px 0 0;max-width:68ch"
    body.string = copy["body"]

    text.append(h3)
    text.append(body)
    card.append(icon)
    card.append(text)
    grid.append(card)


def fix_orphan_apply_button(soup):
    """The Final CTA's Apply button has no destination -- fix it.

    The design export gave this button no href, presumably meaning to trigger
    a real application flow. That flow does not exist yet, so as built the
    button is a <button type="submit"> with no enclosing <form>: a dead click
    that looks identical to a working one. Until the real qualification flow
    is built, route it to the only working conversion mechanism already on the
    page -- the free presence check form.
    """
    apply_section = soup.find(id="apply")
    if apply_section is None:
        return
    for btn in apply_section.find_all("button", attrs={"type": "submit"}):
        if btn.find_parent("form") is not None:
            continue  # a real submit button inside a real form; leave it
        link = soup.new_tag("a", href="#check")
        link["class"] = btn.get("class", [])
        for child in list(btn.contents):
            link.append(child.extract())
        btn.replace_with(link)


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
    #
    # SEO-PLAYBOOK.md section 3 calls for the homepage LocalBusiness schema to
    # carry areaServed, hours, and a service catalog. areaServed is below;
    # hours stays out because site.config.json's hours are still null -- an
    # invented openingHours is worse than none, same honesty rule as the
    # address. The service catalog and pricing ARE real and approved (the
    # funnel blueprint's $799/$99-mo figures), so those are included.
    area_served = [
        {"@type": "City", "name": c} for c in
        ["Albany, Oregon", "Corvallis, Oregon", "Salem, Oregon", "Lebanon, Oregon"]
    ] + [{"@type": "AdministrativeArea", "name": "Willamette Valley, Oregon"}]

    pricing = cfg.get("pricing") or {}
    program, ongoing = pricing.get("program"), pricing.get("ongoing")
    offers = []
    if program:
        offers.append({
            "@type": "Offer",
            "name": program["name"],
            "price": str(program["price"]),
            "priceCurrency": program["currency"],
            "availability": "https://schema.org/InStock",
            "url": f"{origin}/#apply",
        })
    if ongoing:
        offers.append({
            "@type": "Offer",
            "name": ongoing["name"],
            "price": str(ongoing["price"]),
            "priceCurrency": ongoing["currency"],
            "priceSpecification": {
                "@type": "UnitPriceSpecification",
                "price": str(ongoing["price"]),
                "priceCurrency": ongoing["currency"],
                "unitCode": "MON",
            },
        })

    catalog = None
    if cfg.get("services"):
        catalog = {
            "@type": "OfferCatalog",
            "name": program["name"] if program else "Services",
            "itemListElement": [
                {
                    "@type": "Offer",
                    "itemOffered": {"@type": "Service", "name": svc},
                }
                for svc in cfg["services"]
            ],
        }

    organization = {
        # LocalBusiness listed explicitly even though ProfessionalService
        # already implies it in the schema.org type hierarchy -- some
        # consumers match the literal string rather than walking the
        # hierarchy, and the playbook asks for it by name.
        "@type": ["Organization", "LocalBusiness", "ProfessionalService"],
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
        "areaServed": area_served,
        "address": {
            "@type": "PostalAddress",
            "addressRegion": "OR",
            "addressCountry": "US",
        },
    }
    if offers:
        organization["makesOffer"] = offers
    if catalog:
        organization["hasOfferCatalog"] = catalog

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
            organization,
            {
                "@type": "Service",
                "@id": f"{canonical}#service",
                "name": ("Website design and local presence setup"
                         if lang == "en" else
                         "Dise\u00f1o web y configuraci\u00f3n de presencia local"),
                "provider": {"@id": f"{origin}/#organization"},
                "areaServed": area_served,
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
        rename_presence_check(soup, lang)
        resolve_buttons(soup)
        fix_orphan_apply_button(soup)
        resolve_inputs(soup)
        resolve_events(soup, lang)
        resolve_hovers(soup, set())
        fix_unverified_claims(soup, lang, notes)
        wire_contact_and_legal(soup, lang, cfg)
        link_service_area(soup, lang, cfg)
        add_service_area_nav(soup, lang, cfg)
        add_presence_check_card(soup, lang)
        add_track_record_card(soup, lang)
        promote_card_headings(soup)
        add_missing_section_heading(soup, lang)
        announce_presence_success(soup)
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
