# Willamette Web Design

Marketing site for Willamette Web Design — static HTML, no build step, deployed
on Netlify.

**Live:** https://willametteweb.com
**Contact:** info@willametteweb.com · (541) 497-9531

---

## Quick start

```bash
npm install        # sharp, for the image pipeline (dev only — never ships)
npm run serve      # local preview at http://localhost:8080
npm run preflight  # run before every deploy
```

## Commands

| Command | What it does |
|---|---|
| `npm run preflight` | CSS sync check → regenerate sitemap → full audit. **Run before every deploy.** |
| `npm run audit` | Checks every page against the SEO/performance handbook. Exits 1 on CRITICAL/HIGH. |
| `npm run audit index.html` | Audit one page |
| `npm run images` | Turn masters in `assets/img/_src/` into responsive AVIF + WebP, and print the `<picture>` block to paste |
| `npm run css` | Minify `assets/css/site.css` and inline it into every page |
| `npm run sitemap` | Regenerate `sitemap.xml` with git-derived `lastmod` |

## Adding a page

1. Copy `_templates/page.html` to `your-path/index.html` (folder-style URLs).
2. Replace every `{{TOKEN}}`.
3. `npm run sitemap && npm run audit`.
4. Fix findings in severity order: CRITICAL → HIGH → MEDIUM → LOW.

## Docs

- **`CLAUDE.md`** — project conventions, what's confirmed vs. what must not be
  invented. Read this first.
- **`docs/SEO-HANDBOOK.md`** — the full reference: Core Web Vitals, SEO, local
  SEO, GEO, checklists.
- **`docs/SEO-PLAYBOOK.md`** — service-page and city-page process.
- **`docs/LAUNCH-CHECKLIST.md`** — the gates between here and going live.

## Conventions worth knowing

- **`site.config.json` is the single source of truth** for the domain, phone,
  and email. Never hardcode them into a page — the audit fails on drift, because
  inconsistent NAP directly costs local ranking.
- **CSS is inlined, not linked.** An external stylesheet is render-blocking.
- **Fonts are self-hosted.** No `fonts.googleapis.com`.
- **Analytics loads on interaction/idle**, never blocking in `<head>`.
- **The homepage is a plain file at `/`** — no root redirect or rewrite. Keep it
  that way; the predecessor site's rewrite-over-a-stub setup was an outage risk.
- **Nothing unverified ships.** No invented reviews, ratings, addresses, or
  credentials. Empty beats fabricated.
