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
- **Soft conversion:** a **free website audit** that captures the ~90% who
  aren't ready on visit one. The funnel documents call this the single
  highest-leverage element on the page — treat its form as critical path.
- **Positioning wedge:** genuinely bilingual (EN/ES) service for an underserved
  market. Spanish is never an afterthought; `/es/` is a full peer of `/`.
- **Risk reversal:** a 30-day money-back **satisfaction** guarantee. It is
  satisfaction-based and must never be presented as an outcome promise.

Section-by-section source of truth: `docs/FUNNEL-BLUEPRINT.md`.

## Facts that are NOT settled — do not invent them

- **Base city.** Deliberately `null` in `site.config.json`. The homepage FAQ asks
  "Do you work with businesses outside Albany?" and the (541) area code fits
  Albany, so **Albany, OR is the likely base — but it is an inference**. A wrong
  locality is a NAP mismatch against Google Business Profile. Confirm it before
  adding `LocalBusiness` address, geo meta, or city pages. Until then the site
  says only "Based in Oregon" and the schema uses `areaServed` + `addressRegion`,
  which is correct for a service-area business.
- **Guarantee, billing and ownership terms.** The `/terms/` page carries visible
  `NEEDS_REVIEW` callouts for every clause that depends on the signed client
  agreement, and it is `noindex` until they clear. See `docs/BUILD-NOTES.md`.
- **Social profiles.** `sameAs` stays empty until each profile is live, claimed,
  and verified. An unverified URL there is a trust-signal violation.
- **Proof.** There are no clients, reviews or metrics yet. The mockup's sample
  testimonial and "Only 2 spots left" counter were removed for this reason — see
  "Content integrity" below.
- **Anything requiring evidence**: reviews, ratings, years in business, client
  counts, credentials, testimonials.

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

**SEO (§3)**
- One unique `<title>` (~50–60 chars, keyword first, brand last), one unique
  meta description (~140–160), exactly one `<h1>`, logical H2/H3.
- Self-referencing absolute canonical, trailing slash, apex host.
- Folder-style URLs: `/services/website-design/`, lowercase, hyphenated.
- `FAQPage` schema must match the visible Q&A **word for word**. (The
  predecessor site shipped a mismatch here — the audit catches it now.)
- Every page in `sitemap.xml` with a real `lastmod`; no orphans.

**Local (§4)** — this is the big lever for a local service business, often
more than on-page SEO. Google Business Profile, identical NAP everywhere,
citations, and a real review-generation process. See `docs/SEO-PLAYBOOK.md` §2
before writing city pages: swapping only the city name into identical copy is
the #1 mistake and gets treated as doorway pages.

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
scripts/
  audit.mjs           The handbook, executable. Gates the deploy.
  flatten-export.py   Design-tool export -> static EN + ES pages
  build-legal.py      Legal pages from legal_content.py
  legal_content.py    Privacy + Terms copy, EN + ES
  optimize-images.mjs AVIF/WebP responsive pipeline
  inline-css.mjs      Minify + inline the stylesheet
  build-sitemap.mjs   Sitemap with git-derived lastmod
docs/
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
python3 scripts/flatten-export.py <export.html>   # homepage EN + ES
python3 scripts/build-legal.py                    # privacy + terms, EN + ES
npm run preflight
```

**Deliberate structural choice:** the homepage is a real file served directly at
`/`. There is no root redirect or rewrite. The predecessor site needed a forced
200-rewrite to paper over a meta-refresh stub, which was a standing outage risk
(a 301 there caused an infinite redirect loop and took the site down). Keep the
root plain.
