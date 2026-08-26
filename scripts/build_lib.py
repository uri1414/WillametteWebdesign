"""
Shared helpers for the HTML build scripts (flatten-export.py,
build-city-pages.py, build-service-areas.py). Split out into its own module
because a script named with a hyphen -- the convention every build script
here follows -- cannot be imported by another Python script; a plain module
can.
"""

import re
import sys

from bs4 import BeautifulSoup

# Anchors that exist only on the homepage. Bare on that page; from any page
# that reuses its header/footer verbatim they must point back at it
# explicitly or the browser just fails to scroll (the id isn't on the
# current page).
HOMEPAGE_ANCHORS = {"how", "included", "about", "apply", "check"}


def load_chrome(out_root, lang):
    """Pull header + footer out of the already-built homepage.

    Any secondary page (a city page, the service-areas hub) reuses these
    VERBATIM rather than hand-duplicating the markup, so it never drifts
    from the homepage's chrome -- run flatten-export.py first.
    """
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


def service_areas_path(lang):
    """URL of the /service-areas/ hub page -- same slug in both languages,
    matching how /privacy/ and /terms/ work, so every generator that links to
    it (the nav, the footer, each city page) agrees on one path."""
    return "/service-areas/" if lang == "en" else "/es/service-areas/"


def services_hub_path(lang):
    """URL of the /services/ hub page -- same slug convention as
    service_areas_path()."""
    return "/services/" if lang == "en" else "/es/services/"


def service_page_path(lang, slug):
    """URL of a single /services/<slug>/ page."""
    return f"/services/{slug}/" if lang == "en" else f"/es/services/{slug}/"


def minify_css(css):
    css = re.sub(r"/\*(?!!)[\s\S]*?\*/", "", css)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{}:;,>~])\s*", r"\1", css)
    css = css.replace(";}", "}")
    return css.strip()
