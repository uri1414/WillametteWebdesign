# Design sources

The inputs the site is generated from. **Nothing here is served** — see the
`/design/*` rule in `netlify.toml`.

## homepage-template.html

The homepage markup extracted from the visual-builder export. The original
export is a 7.4 MB single file that wraps this markup, JSON-escaped, inside a
`__bundler/template` script, alongside a manifest of base64 assets. Almost all
of that weight was the three illustrations, which now live here as PNGs and ship
as AVIF/WebP derivatives, so keeping the original wrapper would have meant
carrying ~5 MB of duplicated base64.

`scripts/flatten-export.py` accepts the original export. If you re-export from
the design tool, run it against the fresh file and replace this template:

```bash
python3 scripts/flatten-export.py ~/Downloads/new-export.html
```

## source-art/

Full-resolution masters. `scripts/optimize-images.mjs` and the favicon/OG
generation read from these; only the derivatives in `assets/img/` are deployed.

| File | Source size | Rendered at | Ships as |
|---|---|---|---|
| `valley-hero.png` | 1717×916, 1.9 MB | hero background | AVIF/WebP 640–1717w, 13–53 KB |
| `logo-badge.png` | 1254×1254, 1.4 MB | 46×46 in the header | AVIF/WebP 46/92/138, ~2 KB served |
| `program-badge.png` | 1536×1024, 1.5 MB | ≤320 px | AVIF/WebP 320/640, 11–24 KB |

Together the masters are 4.8 MB; a visitor downloads roughly 40 KB of imagery.
Never reference a file from this directory in a page.
