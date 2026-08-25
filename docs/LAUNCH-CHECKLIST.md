# Launch checklist — Willamette Web Design

Derived from `SEO-HANDBOOK.md` Part G, with the rebrand-specific gates added.
Work top to bottom. `npm run audit` covers the machine-checkable items; the
rest need a human.

---

## Gate 0 — Rebrand hygiene (specific to this project)

The audit fails the build on all of these, but check them consciously too:

- [ ] Zero occurrences of `thebaselinestudio.com`, `Baseline Studio`,
      `baselineplatformapp`, `info@thebaselinestudio.com`, `503-877-4254`
- [ ] Every `tel:` link is `tel:+15414979531`
- [ ] Every displayed number reads exactly `(541) 497-9531`
- [ ] Every canonical points at `https://willametteweb.com/…`
- [ ] Base city confirmed and set in `site.config.json` (see the (541) vs Salem
      note in `CLAUDE.md`) — **or** all geo meta and `LocalBusiness` schema
      deliberately omitted
- [ ] No Baseline-era services, pricing, or process copy survives

## Gate 1 — Content is real

- [ ] Nothing on the site is fabricated: no invented reviews, ratings, years in
      business, client counts, credentials, or testimonials
- [ ] `sameAs` contains only profiles that are live, claimed, and verified
      (empty is correct until then)
- [ ] No `aggregateRating` and no `Review` schema anywhere
- [ ] City pages, if any, are >60% unique copy with real local specifics —
      not one template with the city name swapped

## Gate 2 — Performance (handbook Part A)

- [ ] `<picture>` AVIF → WebP → fallback everywhere; smaller mobile source
- [ ] Hero preloaded, `fetchpriority="high"`, NOT lazy
- [ ] Below-fold images `loading="lazy" decoding="async"`
- [ ] Every `<img>` has `width` + `height`
- [ ] No hidden-but-downloaded images on mobile (`display:none` still fetches)
- [ ] CSS minified and inlined; no render-blocking `<link rel=stylesheet>`
- [ ] Fonts self-hosted woff2, `display=swap`, only the weights used
- [ ] Analytics deferred to interaction/idle; first-party JS uses `defer`
- [ ] Third-party embeds (maps, chat, booking) lazy-loaded
- [ ] Favicons right-sized (a stray 183 KB favicon PNG is free weight)
- [ ] 3× mobile + 3× desktop PageSpeed runs; compare the range, not one score
- [ ] Renders correctly at 320 / 375 / 390 / 430 px

## Gate 3 — On-page + technical SEO (Part B)

- [ ] Unique title (~50–60) and description (~140–160) on every page
- [ ] Exactly one `<h1>` per page; logical H2/H3
- [ ] Self-referencing canonical; trailing slash consistent
- [ ] Open Graph + Twitter tags + a real 1200×630 preview image
- [ ] `robots.txt` allows search + AI crawlers and points to the sitemap ✔ (done)
- [ ] `sitemap.xml` complete, dynamic `lastmod` — `npm run sitemap`
- [ ] No accidental `noindex`
- [ ] Real 404 status + branded 404 page ✔ (done)
- [ ] Single redirect for `http→https` and `www→apex`; canonical matches the
      final URL. Set the apex as primary domain in the **Netlify UI** — do not
      also add a redirect rule, or it becomes a two-hop chain.
- [ ] Security headers live ✔ (configured)
- [ ] **CSP**: currently `Content-Security-Policy-Report-Only`. Watch the console
      on a real deploy, widen for anything legitimate, *then* rename the key to
      enforce. Shipping an untested enforcing CSP silently kills fonts/analytics.
- [ ] Every important page ≤3 clicks from home; descriptive anchor text; no orphans

## Gate 4 — Structured data (Part B §3.3)

- [ ] `Organization` + `WebSite` site-wide
- [ ] `LocalBusiness` with `areaServed` (service-area business — no invented
      street address), hours *with times*, `priceRange`
- [ ] `Service` / `ItemList` / `BreadcrumbList` / `FAQPage` per page type
- [ ] FAQ schema matches the visible Q&A exactly
- [ ] Validated at search.google.com/test/rich-results and validator.schema.org

## Gate 4.5 — The funnel (this site is a sales funnel, not a brochure)

Source of truth: `docs/FUNNEL-BLUEPRINT.md`. These are the items that decide
whether the page earns anything.

- [x] **The free presence check form has a backend.** Wired to Netlify Forms —
      no server to run. Verified: it POSTs urlencoded to `/` with
      `form-name=presence-check`, the visitor's language, canonical field names
      in both languages, and an armed honeypot.
- [ ] **Turn on form notifications.** Netlify captures submissions but emails
      nobody by default. Netlify → Forms → `presence-check` → Settings → Form
      notifications → add `info@willametteweb.com`. **A captured-but-unnotified
      form looks identical to a working one and loses every lead.**
- [ ] **Submit a real test from the live site and confirm the email arrives.**
      Do not skip this; it is the only thing that proves the chain works.
- [ ] Confirm the honeypot is not catching real people (check Netlify's spam
      folder after the first week).
- [ ] **Follow-up sequence exists behind the presence check.** Most local leads
      convert on the third or fourth touch. Without a sequence, the capture is a
      list nobody emails.
- [ ] **The presence check is productized** (GBP check, mobile speed, listings
      gaps, competitor comparison) so delivering one does not eat a day.
- [x] **No more dead Apply click.** The Final CTA's Apply button had no `<form>`
      to submit — a silent no-op. It now links to `#check`, the working
      presence-check form, until the real flow below exists.
- [ ] **The Apply flow exists.** Every primary CTA still points at `#apply` /
      `#check`, not a real qualification flow. Build the 4-step application (or
      a shortened version), or the interim routing above stays permanent by
      default.
- [ ] Application shows a progress indicator, and step 1 asks the minimum.
- [ ] Conversion tracking fires on: CTA clicks, application start, application
      complete, presence-check submit, phone clicks (blueprint, Technical
      guardrails).
- [ ] Every claim on the page is true today — no invented counts, no sample
      testimonials. See "Content integrity" in `CLAUDE.md`.
- [ ] Guarantee copy never implies a promised number of leads or rankings.

## Gate 5 — Conversion (this is what the site is for)

- [ ] **Contact form posts to a real backend and a test lead lands in an inbox.**
      Until it does, the form must not pretend to submit.
- [ ] Phone visible + tap-to-call in header, footer, and mobile bar
- [ ] Email deliverability: **SPF + DKIM + DMARC** all set for
      `willametteweb.com`. DKIM is the one most often missing — generate the key
      in the mail provider's admin, publish the TXT record, then enable
      authentication. Start DMARC at `p=none`, tighten later; starting at
      `p=reject` before DKIM is live blocks your own mail.

## Gate 6 — Register (post-launch, day one)

- [ ] Google Search Console verified + sitemap submitted
- [ ] GA4 property created for `willametteweb.com` (new — not Baseline's),
      ID set in `site.config.json`, loading deferred
- [ ] Bing Webmaster Tools verified
- [ ] **Google Business Profile** created, verified, filled completely
      (categories, services, hours, service area, photos), linked from the
      footer and added to schema `sameAs`
- [ ] Citations with identical NAP: Bing Places, Apple Business Connect, Yelp,
      local/industry directories

## Gate 7 — Monitor

- [ ] Re-test PageSpeed after launch; keep a before/after note
- [ ] Watch Search Console Coverage/Indexing for the first few weeks
- [ ] Field (CrUX) data appears only after enough real traffic — "No Data" at
      launch is expected, not a bug
- [ ] Review generation process running; respond to every review. Only then add
      real testimonials and `Review` schema.
