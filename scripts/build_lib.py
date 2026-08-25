"""
Shared helpers for the HTML build scripts (flatten-export.py,
build-city-pages.py). Split out into its own module because a script named
with a hyphen -- the convention every build script here follows -- cannot be
imported by another Python script; a plain module can.
"""

import re

from bs4 import BeautifulSoup


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


def minify_css(css):
    css = re.sub(r"/\*(?!!)[\s\S]*?\*/", "", css)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{}:;,>~])\s*", r"\1", css)
    css = css.replace(";}", "}")
    return css.strip()


# Where the real 30-Day Program application lives, per language. The homepage's
# "Apply" buttons, the city pages and the design export all have to agree on
# this, so it is defined once here.
APPLY_PATH = {"en": "/apply/", "es": "/es/apply/"}


def wire_apply_cta_html(html, lang):
    """The same rewrite as wire_apply_cta(), but on already-built HTML.

    Deliberately string-level. Re-parsing a finished page with BeautifulSoup and
    writing it back re-serialises every tag in it -- attributes get reordered,
    void elements get self-closing slashes -- and the other build scripts read
    that output with regexes. Doing exactly that turned

        <link rel="canonical" href="...">   into   <link href="..." rel="canonical"/>

    on the homepage, which build-sitemap.mjs then could not recognise, and the
    homepage silently dropped out of sitemap.xml. Touch only the hrefs.

    Returns the rewritten HTML. Idempotent.
    """
    target = APPLY_PATH[lang]
    out = re.sub(r'href="(?:/es)?/?#apply"', f'href="{target}"', html)
    # The Final CTA's Apply button, routed into the presence-check form while
    # there was no application to send it to.
    out = re.sub(
        r'(<a\b[^>]*href=")(?:/|/es/)?#check("[^>]*>\s*(?:Apply|Aplica)[^<]*)',
        rf'\1{target}\2',
        out,
    )
    return out


def wire_apply_cta(soup, lang):
    """Point every "Apply" call to action at the real application page.

    Before the application existed, these buttons had nowhere to go: the design
    export shipped the Final CTA's Apply button with no href at all, and the
    build routed it to the free presence check as a stopgap so it was not a dead
    click. The application flow is real now (/apply/), so every Apply CTA --
    header, drawer, hero, final section -- points at it.

    Idempotent: safe to run against a page that has already been wired.
    """
    target = APPLY_PATH[lang]
    anchors = {"#apply", "/#apply", "/es/#apply", "#top#apply"}

    for a in soup.find_all("a", href=True):
        if a["href"] in anchors:
            a["href"] = target

    section = soup.find(id="apply")
    if section is None:
        return

    # The stopgap link into the presence-check form, and the export's orphan
    # <button> that never had a destination.
    for a in section.find_all("a", href=True):
        if a["href"].endswith("#check"):
            a["href"] = target
    for btn in section.find_all("button", attrs={"type": "submit"}):
        if btn.find_parent("form") is not None:
            continue  # a real submit button inside a real form; leave it
        link = soup.new_tag("a", href=target)
        link["class"] = btn.get("class", [])
        for child in list(btn.contents):
            link.append(child.extract())
        btn.replace_with(link)
