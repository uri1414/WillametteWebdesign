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

## Facts that are NOT settled — do not invent them

- **Brand palette, typography, logo/wordmark.** The owner is designing these and
  will send the homepage code. Do not choose colors or fonts on their behalf.
- **Base city.** Deliberately `null` in `site.config.json`. The (541) area code
  covers Eugene / Corvallis / Albany / Bend — **not Salem**, which is 503/971.
  Guessing produces a NAP mismatch against Google Business Profile. Confirm
  before writing any `LocalBusiness` schema, geo meta, or city page.
- **Services, pricing, process.** Coming with the new business plan.
- **Social profiles.** `sameAs` stays empty until each profile is live, claimed,
  and verified. An unverified URL there is a trust-signal violation.
- **Anything requiring evidence**: reviews, ratings, years in business, client
  counts, credentials, testimonials.

> **The honesty rule overrides everything** (handbook §1, §9). No fabricated
> reviews, no `aggregateRating` without real ratings, no invented street address,
> no near-duplicate doorway city pages. `npm run audit` fails the build on the
> schema versions of these, but it can't catch invented prose — don't write it.

---

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
scripts/
  audit.mjs           The handbook, executable. Gates the deploy.
  optimize-images.mjs AVIF/WebP responsive pipeline
  inline-css.mjs      Minify + inline the stylesheet
  build-sitemap.mjs   Sitemap with git-derived lastmod
docs/
  SEO-HANDBOOK.md     The full reference — performance, SEO, local, GEO
  SEO-PLAYBOOK.md     Service-page and city-page process
  LAUNCH-CHECKLIST.md Pre-launch and post-launch gates
```

There is **no `index.html` yet** — the owner is sending the homepage code. Drop
it in at the repo root, then run `npm run preflight` and work the findings.

**Deliberate structural choice:** the homepage is a real file served directly at
`/`. There is no root redirect or rewrite. The predecessor site needed a forced
200-rewrite to paper over a meta-refresh stub, which was a standing outage risk
(a 301 there caused an infinite redirect loop and took the site down). Keep the
root plain.
