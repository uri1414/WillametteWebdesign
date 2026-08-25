#!/usr/bin/env python3
"""
build-legal.py — generate the Privacy Policy and Terms of Service pages.

Four pages from one source: /privacy/, /terms/, /es/privacy/, /es/terms/.
Content lives in scripts/legal_content.py so the English and Spanish versions
cannot drift apart structurally.

NEEDS_REVIEW items render as a visible callout on the page. That is deliberate:
an unresolved legal term should be impossible to miss in review, and the page
carries a noindex until they are cleared, so a draft can never be indexed.

    python3 scripts/build-legal.py [--out .]
"""

import argparse
import json
import pathlib
import sys
from datetime import date
from html import escape

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from legal_content import PRIVACY, TERMS  # noqa: E402

LABELS = {
    "en": {
        "skip": "Skip to content",
        "home": "Back to home",
        "review_title": "Needs review before launch",
        "draft": ("This page is a working draft. It is accurate about how the website "
                  "behaves, but the highlighted items below depend on the signed client "
                  "agreement and must be confirmed — ideally by a lawyer — before "
                  "launch. This page is set to noindex until then."),
        "legal_note": ("This document is provided for information and is not legal "
                       "advice."),
    },
    "es": {
        "skip": "Saltar al contenido",
        "home": "Volver al inicio",
        "review_title": "Requiere revisión antes del lanzamiento",
        "draft": ("Esta página es un borrador de trabajo. Describe con exactitud cómo "
                  "funciona el sitio, pero los puntos resaltados dependen del contrato "
                  "firmado y deben confirmarse — preferiblemente con un abogado — antes "
                  "del lanzamiento. Hasta entonces la página está marcada como noindex."),
        "legal_note": ("Este documento es informativo y no constituye asesoría legal."),
    },
}


def render_blocks(blocks, cfg, lang):
    nap = cfg["nap"]
    out = []
    for kind, value in blocks:
        if kind == "p":
            out.append(f"<p>{escape(value).format(email=escape(nap['email']))}</p>")
        elif kind == "h3":
            out.append(f"<h3>{escape(value)}</h3>")
        elif kind == "ul":
            items = "".join(f"<li>{escape(i)}</li>" for i in value)
            out.append(f"<ul>{items}</ul>")
        elif kind == "contact":
            out.append(
                '<p class="legal-contact">'
                f'<a href="mailto:{escape(nap["email"])}">{escape(nap["email"])}</a><br>'
                f'<a href="{escape(nap["phoneHref"])}">{escape(nap["phoneDisplay"])}</a><br>'
                f'<span>{escape("Willamette Valley, Oregon, USA")}</span>'
                "</p>"
            )
        elif kind == "review":
            out.append(
                '<aside class="legal-review" role="note">'
                f'<strong>{escape(LABELS[lang]["review_title"])}</strong> '
                f"{escape(value)}</aside>"
            )
    return "\n".join(out)


def build(doc, kind, lang, cfg, css, today):
    origin = cfg["domain"]["origin"]
    prefix = "" if lang == "en" else "es/"
    path = f"{prefix}{kind}/"
    canonical = f"{origin}/{path}"
    alt_en = f"{origin}/{kind}/"
    alt_es = f"{origin}/es/{kind}/"
    lab = LABELS[lang]

    has_review = any(
        k == "review" for _, blocks in doc["sections"] for k, _ in blocks
    )

    body = []
    for heading, blocks in doc["sections"]:
        body.append(f"<section><h2>{escape(heading)}</h2>\n{render_blocks(blocks, cfg, lang)}</section>")

    # A draft with unresolved terms must not be indexable.
    # A draft carrying unresolved legal terms must not be indexable. The
    # audit-allow directive records *why*, so the exemption is reviewable and
    # disappears with the draft rather than lingering as a silent suppression.
    robots = (
        '<meta name="robots" content="noindex, follow">\n'
        "<!-- audit-allow: noindex — draft legal terms pending sign-off; "
        "indexing unconfirmed terms would publish them as authoritative. -->"
    ) if has_review else ""

    draft_banner = (
        f'<aside class="legal-draft" role="note"><p>{escape(lab["draft"])}</p></aside>'
        if has_review else ""
    )

    schema = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": doc["h1"],
        "url": canonical,
        "inLanguage": "en-US" if lang == "en" else "es-US",
        "isPartOf": {"@id": f"{origin}/#website"},
        "publisher": {"@id": f"{origin}/#organization"},
        "dateModified": today,
    }

    # Deferred to first interaction or 3s idle, same as every other page
    # (handbook 2.6) -- a blocking gtag.js in <head> is ~66 KB of main-thread
    # work for data nobody needs in the first 3 seconds, and TBT is 30% of
    # the Lighthouse score. Omitted entirely if no ID is configured yet.
    ga4 = (cfg.get("analytics") or {}).get("ga4MeasurementId") or ""
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

    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(doc['title'])}</title>
<meta name="description" content="{escape(doc['description'])}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="en" href="{alt_en}">
<link rel="alternate" hreflang="es" href="{alt_es}">
<link rel="alternate" hreflang="x-default" href="{alt_en}">
{robots}
<meta name="theme-color" content="#F3E7CE">
<meta property="og:type" content="article">
<meta property="og:site_name" content="{escape(cfg['brand']['name'])}">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{escape(doc['title'])}">
<meta property="og:description" content="{escape(doc['description'])}">
<meta property="og:image" content="{origin}/assets/img/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Willamette Web Design">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{escape(doc['title'])}">
<meta name="twitter:description" content="{escape(doc['description'])}">
<meta name="twitter:image" content="{origin}/assets/img/og-image.png">
<link rel="icon" href="/favicon.ico" sizes="16x16 32x32 48x48">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="preload" as="font" type="font/woff2" href="/assets/fonts/inter-latin.woff2" crossorigin>
<style id="site-css">{css}</style>
<style id="page-css">
.legal-wrap {{ max-width: 760px; margin: 0 auto; padding: 56px clamp(20px,5vw,32px) 96px; }}
.legal-top {{ display:flex; align-items:center; gap:12px; margin-bottom:40px; }}
.legal-top img {{ width:44px; height:44px; }}
.legal-wrap h1 {{ font-size: clamp(32px,5vw,46px); margin:0 0 10px; }}
.legal-updated {{ font:600 13px var(--font-ui); letter-spacing:.06em; text-transform:uppercase; color:var(--text-muted); margin:0 0 28px; }}
.legal-intro {{ font-size:18px; line-height:1.65; margin:0 0 8px; }}
.legal-wrap section {{ margin-top:40px; }}
.legal-wrap h2 {{ font-size:24px; margin:0 0 14px; }}
.legal-wrap h3 {{ font-size:17px; margin:22px 0 8px; font-family:var(--font-ui); font-weight:700; color:var(--color-forest); }}
.legal-wrap p {{ margin:0 0 14px; line-height:1.7; }}
.legal-wrap ul {{ margin:0 0 14px; padding-left:22px; line-height:1.7; }}
.legal-wrap li {{ margin-bottom:7px; }}
.legal-contact a {{ color:var(--color-rust); font-weight:600; }}
.legal-draft {{ background:var(--color-forest); color:var(--color-cream); border-radius:var(--radius-lg); padding:20px 24px; margin:0 0 36px; }}
.legal-draft p {{ margin:0; font-size:15px; line-height:1.6; }}
.legal-review {{ border-left:3px solid var(--color-rust); background:rgba(213,104,60,.07); padding:14px 18px; margin:0 0 16px; border-radius:0 var(--radius-md) var(--radius-md) 0; font-size:14.5px; line-height:1.6; }}
.legal-review strong {{ display:block; color:var(--color-rust); font:700 12px var(--font-ui); letter-spacing:.08em; text-transform:uppercase; margin-bottom:5px; }}
.legal-foot {{ margin-top:56px; padding-top:24px; border-top:1px solid var(--border-rule); display:flex; flex-wrap:wrap; gap:16px; justify-content:space-between; align-items:center; }}
.legal-foot p {{ margin:0; font-size:13px; color:var(--text-muted); }}
</style>
{analytics}
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(",", ":"))}</script>
</head>
<body>
<a class="skip" href="#main">{escape(lab['skip'])}</a>
<main id="main" class="legal-wrap">
  <a class="legal-top" href="/{prefix}">
    <img src="/assets/img/logo-badge-46.png" alt="Willamette Web Design" width="46" height="46" decoding="async">
    <span class="eyebrow">Willamette Web Design</span>
  </a>

  <h1>{escape(doc['h1'])}</h1>
  <p class="legal-updated">{escape(doc['updated']).replace('{date}', today)}</p>
  {draft_banner}
  <p class="legal-intro">{escape(doc['intro'])}</p>

{chr(10).join(body)}

  <div class="legal-foot">
    <p>{escape(lab['legal_note'])}</p>
    <a class="btn btn--secondary btn--sm" href="/{prefix}">{escape(lab['home'])}</a>
  </div>
</main>
</body>
</html>
"""


def minify_css(css):
    import re
    css = re.sub(r"/\*(?!!)[\s\S]*?\*/", "", css)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{}:;,>~])\s*", r"\1", css)
    return css.replace(";}", "}").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=".")
    args = ap.parse_args()
    root = pathlib.Path(args.out)

    cfg = json.loads((root / "site.config.json").read_text())
    css = minify_css((root / "assets/css/site.css").read_text())
    today = date.today().isoformat()

    for kind, source in (("privacy", PRIVACY), ("terms", TERMS)):
        for lang in ("en", "es"):
            html = build(source[lang], kind, lang, cfg, css, today)
            rel = f"{kind}/index.html" if lang == "en" else f"es/{kind}/index.html"
            dest = root / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(html, encoding="utf-8")
            print(f"  {rel}  {len(html)/1024:.1f} KB")


if __name__ == "__main__":
    main()
