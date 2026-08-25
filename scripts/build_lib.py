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
