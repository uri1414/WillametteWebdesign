# Willamette Web Design — project notes for Claude

Marketing site for **Willamette Web Design**, a web design studio serving the
Willamette Valley, Oregon. Static HTML, **no build step**, deployed on Netlify
(`publish = "."`).

This repo is the rebrand of the former **Baseline Studio** site. The business
model changed with the rebrand — do not carry over Baseline's services,
pricing, or positioning copy.

---

## Facts that are confirmed (use these, don't re-derive)

| | |
|---|---|
| Brand name | Willamette Web Design |
| Domain | `https://willametteweb.com` (apex canonical) |
| Phone | (541) 497-9531 → `tel:+15414979531` |
| Email | info@willametteweb.com |
| Base city | Salem, OR — confirmed (was previously an unconfirmed guess of Albany; see history below) |

All of the above live in **`site.config.json`**, which is the single source of
truth. Change a value there, never inside a page. The audit script fails the
build when a `tel:` link or schema `telephone` drifts from it — NAP consistency
is a top-tier local ranking factor and formatting drift alone hurts.

## The business model

The homepage is a **direct-response sales funnel**, not an agency portfolio.
Every section moves toward one action, with a lower-commitment fallback:

- **Primary conversion:** apply for the **Willamette 30-Day Program — $799**
  one-time (website + local SEO + Google Business Profile + listings + lead
  capture), followed by **$99/month** ongoing management.
- **Soft conversion:** a **free presence check** (never "audit" — see below)
  that captures the ~90% who aren't ready on visit one. The funnel documents
  call this the single highest-leverage element on the page — treat its form
  as critical path.
- **Positioning wedge:** genuinely bilingual (EN/ES) service for an underserved
  market. Spanish is never an afterthought; `/es/` is a full peer of `/`.
- **Risk reversal:** a 30-day money-back **satisfaction** guarantee. It is
  satisfaction-based and must never be presented as an outcome promise.

Section-by-section source of truth: `docs/FUNNEL-BLUEPRINT.md`.

## Facts that are NOT settled — do not invent them

- **Base city — now confirmed: Salem, OR.** `site.config.json`'s
  `nap.addressLocality` is `"Salem"`. This was previously left `null`: an
  earlier guess inferred Albany from the (541) area code alone, which was
  explicitly flagged as unconfirmed and never shipped. Salem is a real,
  user-confirmed fact, not an inference — it's safe to state directly ("Based
  in Salem, Oregon") anywhere on the site. `streetAddress`, `postalCode`, and
  `geo.latitude`/`longitude` stay `null`: this is still a service-area
  business with no public storefront, so schema pairs the city-level
  `addressLocality` with `areaServed` rather than a full street address or
  precise coordinates — never add those without an explicit ask. The
  trust line and the "do you work outside X" FAQ are driven by
  `set_base_city()` in `flatten-export.py`, reading `nap.addressLocality` —
  change the city there, not by hand-editing generated HTML. The six city
  pages each explicitly disclose this (service-area model, not a storefront
  in that city, see below) — Salem's own city page states the base directly;
  the other five name Salem as the base while explaining the program runs
  identically for them.
- **Guarantee, billing and ownership terms.** The `/terms/` page carries visible
  `NEEDS_REVIEW` callouts for every clause that depends on the signed client
  agreement, and it is `noindex` until they clear. See `docs/BUILD-NOTES.md`.
- **Social profiles.** `sameAs` stays empty until each profile is live, claimed,
  and verified. An unverified URL there is a trust-signal violation.
- **Proof.** Two real Willamette Valley businesses have been through the full
  program (same scope as the $799 offer, under this brand) — live in about two
  weeks. That fact is stated on the homepage (the "Already done once" card in
  the guarantee section). What is still NOT there: a named, permissioned
  testimonial from either business. Get their explicit sign-off and an actual
  quote before naming them or attributing a quote — until then this stays a
  general, honest statement with no name attached. The mockup's *fabricated*
  sample testimonial and "Only 2 spots left" counter were removed for a
  different reason (they named a person who does not exist / were stale
  numbers) — see "Content integrity" below. Do not confuse the two: this proof
  point is real, it just isn't a quote yet.
- **Anything requiring evidence beyond the above**: reviews, ratings, years in
  business, specific client counts beyond the two noted here, credentials,
  testimonials with a name attached.

**Naming: "presence check", never "audit".** The approved blueprint names the
soft-conversion offer "the free presence check" throughout; the design export
instead wrote "audit" everywhere. `flatten-export.py`'s `rename_presence_check()`
corrects this on every build — visible copy, the Netlify form name
(`presence-check`), and every `data-presence-*` attribute. If a re-export
reintroduces "audit" wording, that transform is where it gets fixed, not in a
one-off edit to the generated HTML.

> **The honesty rule overrides everything** (handbook §1, §9). No fabricated
> reviews, no `aggregateRating` without real ratings, no invented street address,
> no near-duplicate doorway city pages. `npm run audit` fails the build on the
> schema versions of these, but it can't catch invented prose — don't write it.

---

## Content integrity — what was changed and why

The approved design mockup carried two invented trust signals. The funnel
blueprint flags both itself, and the handbook's honesty rule overrides
everything, so both were replaced during the build. **Do not restore them.**

1. **A fabricated testimonial** — a quote attributed to "Maria S., Cleaning
   Services, Eugene", a person who does not exist. Replaced with a
   process-proof card ("What you get, before you pay a cent") that does the same
   persuasive work using only true statements. Swap in a real, permissioned
   client quote once there is one — and only then.

2. **Fabricated scarcity** — "Only 2 spots left this month", "SEPTEMBER
   AVAILABILITY", "just 5 businesses at a time". Hardcoded numbers that were
   already stale and unverifiable. Replaced with the blueprint's own approved
   honest line: "We take on a limited number of new businesses each month."
   A specific count has to be true on the day it is read; a hardcoded month
   rots. If you want a real counter, drive it from live capacity.

`npm run audit` fails the build on the *schema* forms of these
(`aggregateRating`, `Review`, placeholder `sameAs`). It cannot detect invented
prose — that part is on whoever writes the copy.

## Working practices

**Run the preflight before every deploy:**

```bash
npm run preflight     # css sync check → regenerate sitemap → full audit
```

Or the pieces individually:

```bash
npm run audit                 # handbook checklists against every page
npm run audit index.html      # one page
npm run images                # AVIF/WebP derivatives from assets/img/_src/
npm run css                   # minify assets/css/site.css, inline into pages
npm run sitemap               # regenerate sitemap.xml with real lastmod
npm run serve                 # local preview at :8080
```

`npm run audit` exits non-zero on CRITICAL or HIGH findings. Fix in severity
order — CRITICAL → HIGH → MEDIUM → LOW (handbook §7). Don't polish typography
while the contact form is broken.

**Starting a new page:** copy `_templates/page.html`. It already carries the
canonical, Open Graph, schema scaffold, deferred-analytics block, and the
guidance comments for each. Retrofitting SEO onto a finished page is how things
get missed.

**Conserve Netlify credits.** Batch changes into a single PR/deploy rather than
one PR per fix — every push to the deploy branch triggers a build.

**Netlify config cannot be tested from the agent sandbox** (no outbound access
to the live site). Reason through redirect/rewrite and header interactions
carefully before merging, and prefer the smallest change. If a config change is
risky, say so rather than shipping it hopefully.

---

## Non-negotiable technical standards

These are enforced by `scripts/audit.mjs`. They come from `docs/SEO-HANDBOOK.md`.

**Performance (§2)**
- Images ship as `<picture>` AVIF → WebP → JPEG fallback, with a smaller mobile
  source. Generate them with `npm run images`; never hand-place a raw JPEG.
- Every `<img>` has `width` + `height`. Missing them is a direct CLS regression.
- Exactly one hero image gets `fetchpriority="high"` and a `<link rel=preload>`;
  it must never also be `loading="lazy"`. Everything below the fold is
  `loading="lazy" decoding="async"`.
- CSS is **inlined**, not linked. An external stylesheet is render-blocking.
- Fonts are **self-hosted** woff2 with `font-display: swap`, only the weights
  actually used. Never `fonts.googleapis.com` — that's DNS+TCP+TLS to two
  third-party hosts before styled text renders.
- Analytics loads on first interaction or 3s idle, never as a blocking
  `<script src=gtag.js>` in `<head>`. That pattern is worth ~66 KB of
  main-thread time and TBT is 30% of the Lighthouse score.

**Forms (§G-launch)** — enforced by the audit, from the Fast Website Starter
(`docs/FAST-STARTER-REFERENCE.md`):
- Every form has a real backend. The audit fails the build on a form with no
  `action` and no `data-netlify` — a form that posts nowhere loses leads
  invisibly, which is the worst failure mode a marketing site has.
- Netlify Forms needs the hidden `form-name` input to match a submission; the
  audit checks it exists.
- Public forms carry an armed honeypot, and the audit verifies the declared
  honeypot field actually exists.
- Field `name`s are canonical and identical across EN and ES. They are data
  keys, not UI — deriving them from translated labels sends two different
  shapes to one form and mangles accents.

**SEO (§3)**
- One unique `<title>` (~50–60 chars, keyword first, brand last), one unique
  meta description (~140–160), exactly one `<h1>`, logical H2/H3.
- Self-referencing absolute canonical, trailing slash, apex host.
- Folder-style URLs: `/services/website-design/`, lowercase, hyphenated.
- `FAQPage` schema must match the visible Q&A **word for word**. It is
  generated from the built DOM by `flatten-export.py`, so there is no second
  copy to drift; the audit verifies the match either way. (The predecessor site
  shipped a mismatch here.)
- Every page in `sitemap.xml` with a real `lastmod`; no orphans.

**Local (§4)** — this is the big lever for a local service business, often
more than on-page SEO. Google Business Profile, identical NAP everywhere,
citations, and a real review-generation process. See `docs/SEO-PLAYBOOK.md` §2
before touching city pages: swapping only the city name into identical copy is
the #1 mistake and gets treated as doorway pages. The six existing city pages
each carry a genuinely unique intro and FAQ (verified: ~65-70% of each page's
sentences are unique to it, not shared boilerplate) — keep that ratio if you
add another city, not just a copy with the name swapped. `/service-areas/` is
the honest way to cover the rest of the valley without a dedicated (and
inevitably thinner) page for every town — see `build-service-areas.py` below.

---

## Repo layout

```
site.config.json      Single source of truth — NAP, domain, analytics, sameAs
netlify.toml          Deploy, caching, security headers, 404 status
robots.txt            Search + AI crawlers explicitly allowed
llms.txt              Plain-text business summary for AI answer engines
sitemap.xml           Generated — do not hand-edit
404.html              Branded 404, real 404 status
_templates/page.html  Start every new page from this
assets/
  css/site.css        Source stylesheet (inlined into pages by npm run css)
  js/site.js          First-party JS — always loaded with defer
  fonts/              Self-hosted woff2
  img/                Shipped derivatives
  img/_src/           Full-res masters (gitignored, never deployed)
index.html            Homepage (EN) — GENERATED
es/index.html         Homepage (ES) — GENERATED
privacy/, terms/      Legal pages, EN + ES — GENERATED
web-design-<city>-or/ City landing pages, EN + ES — GENERATED
  (albany, corvallis, salem, lebanon, keizer, woodburn — the approved
  service area)
service-areas/         Valley-wide hub page, EN + ES — GENERATED. Links every
                      city page above plus honestly covers towns that don't
                      have one; see SEO-PLAYBOOK.md §2 before adding more
                      dedicated city pages instead of using this hub.
scripts/
  audit.mjs           The handbook, executable. Gates the deploy.
  flatten-export.py   Design-tool export -> static EN + ES homepage
  build-legal.py      Legal pages from legal_content.py
  legal_content.py    Privacy + Terms copy, EN + ES
  build-city-pages.py City pages from city_content.py — reuses the built
                      homepage's header/footer verbatim, so run this AFTER
                      flatten-export.py, not before
  city_content.py     Per-city intro + FAQ copy, EN + ES — genuinely unique
                      per city, not a template; see SEO-PLAYBOOK.md §2
  build-service-areas.py  The /service-areas/ hub page — also reuses the
                      built homepage's header/footer, so after
                      flatten-export.py; order relative to
                      build-city-pages.py doesn't matter
  build_lib.py        extract_faqs(), minify_css(), load_chrome() +
                      rewrite_chrome_links() (reuse the homepage header/
                      footer), service_areas_path() — shared by the
                      generators above (a hyphenated script name can't be
                      imported by another script, hence the separate module)
  optimize-images.mjs AVIF/WebP responsive pipeline
  inline-css.mjs      Minify + inline the stylesheet
  build-sitemap.mjs   Sitemap with git-derived lastmod
docs/
  FAST-STARTER-REFERENCE.md  The handbook as working code; what we adopted
  FUNNEL-BLUEPRINT.md Section-by-section source of truth for the homepage
  FUNNEL-RECOMMENDATIONS.md  The reasoning behind each funnel section
  BUILD-NOTES.md      GENERATED — open items stripped from the mockup
  SEO-HANDBOOK.md     The full reference — performance, SEO, local, GEO
  SEO-PLAYBOOK.md     Service-page and city-page process
  LAUNCH-CHECKLIST.md Pre-launch and post-launch gates
```

**The pages are generated, not hand-written.** `index.html`, `es/index.html`,
and the four legal pages are build output. Editing them directly means the next
build silently discards your change. Edit the source instead:

| To change | Edit |
|---|---|
| Homepage structure or copy | re-export the design, then re-run `flatten-export.py` |
| How the export is transformed | `scripts/flatten-export.py` |
| Styling, motion, components | `assets/css/site.css` |
| Legal copy (EN + ES) | `scripts/legal_content.py` |
| NAP, pricing, service area | `site.config.json` |

Rebuild:

```bash
python3 scripts/flatten-export.py <export.html>   # homepage EN + ES — run first
python3 scripts/build-legal.py                    # privacy + terms, EN + ES
python3 scripts/build-city-pages.py                # city pages — needs the homepage's header/footer, so after flatten-export.py
python3 scripts/build-service-areas.py             # /service-areas/ hub — also needs the homepage's header/footer
npm run preflight
```

**Deliberate structural choice:** the homepage is a real file served directly at
`/`. There is no root redirect or rewrite. The predecessor site needed a forced
200-rewrite to paper over a meta-refresh stub, which was a standing outage risk
(a 301 there caused an infinite redirect loop and took the site down). Keep the
root plain.
