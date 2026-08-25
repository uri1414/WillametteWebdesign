#!/usr/bin/env node
/**
 * audit.mjs — the Website Optimization & SEO Handbook, made executable.
 *
 * Every check below maps to a line in docs/SEO-HANDBOOK.md (Part G checklists)
 * or docs/SEO-PLAYBOOK.md. The section is printed with each finding so a
 * failure tells you where to read.
 *
 * Zero dependencies — runs on plain Node, no install step, so it can gate a
 * deploy from anywhere.
 *
 *   node scripts/audit.mjs                 # audit every .html in the repo
 *   node scripts/audit.mjs index.html      # audit specific files
 *   node scripts/audit.mjs --json          # machine-readable output
 *
 * Exit code: 0 if no CRITICAL or HIGH findings, 1 otherwise.
 * Fix in severity order (handbook §7): CRITICAL → HIGH → MEDIUM → LOW.
 */

import { readFileSync, readdirSync, statSync, existsSync } from 'node:fs';
import { join, relative, extname, basename } from 'node:path';

const ROOT = process.cwd();
const CONFIG = existsSync(join(ROOT, 'site.config.json'))
  ? JSON.parse(readFileSync(join(ROOT, 'site.config.json'), 'utf8'))
  : {};
const ORIGIN = CONFIG?.domain?.origin ?? '';

const SEVERITY = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 };
const SKIP_DIRS = new Set(['node_modules', '.git', '.netlify', 'reports', '_src', 'docs', '_templates']);

/* ---------------------------------------------------------------- helpers */

const stripComments = (html) => html.replace(/<!--[\s\S]*?-->/g, '');

/**
 * Normalise text so a schema string and the rendered page compare fairly.
 * Without this, a question written as "couldn&rsquo;t" in HTML and "couldn't"
 * in JSON-LD reads as a mismatch when it is really the same sentence.
 */
function normalise(text) {
  return text
    .replace(/&nbsp;|&#160;/g, ' ')
    .replace(/&amp;|&#38;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;|&#34;|&ldquo;|&rdquo;|[\u201C\u201D]/g, '"')
    .replace(/&apos;|&#39;|&rsquo;|&lsquo;|[\u2018\u2019]/g, "'")
    .replace(/&mdash;|[\u2014]/g, '--')
    .replace(/&ndash;|[\u2013]/g, '-')
    .replace(/&hellip;|[\u2026]/g, '...')
    .replace(/\s+/g, ' ')
    .trim();
}

/** Text with <script>/<style>/comments removed — i.e. what a reader sees. */
function visibleText(html) {
  return normalise(
    stripComments(html)
      .replace(/<(script|style|template|noscript)\b[^>]*>[\s\S]*?<\/\1>/gi, ' ')
      .replace(/<[^>]+>/g, ' ')
  );
}

function tagsOf(html, tag) {
  const out = [];
  const re = new RegExp(`<${tag}\\b[^>]*>`, 'gi');
  let m;
  while ((m = re.exec(html))) out.push(m[0]);
  return out;
}

function attr(tag, name) {
  const m = tag.match(new RegExp(`\\b${name}\\s*=\\s*("([^"]*)"|'([^']*)'|([^\\s>]+))`, 'i'));
  return m ? (m[2] ?? m[3] ?? m[4] ?? '') : null;
}

const hasAttr = (tag, name) => new RegExp(`\\b${name}\\b`, 'i').test(tag);

function metaContent(html, key, kind = 'name') {
  const re = new RegExp(`<meta\\b[^>]*\\b${kind}\\s*=\\s*["']${key}["'][^>]*>`, 'i');
  const m = html.match(re);
  return m ? attr(m[0], 'content') : null;
}

function countMeta(html, key, kind = 'name') {
  const re = new RegExp(`<meta\\b[^>]*\\b${kind}\\s*=\\s*["']${key}["']`, 'gi');
  return (html.match(re) || []).length;
}

/** JSON-LD blocks, parsed. Returns { ok:[objects], bad:[{raw,error}] }. */
function jsonLd(html) {
  const ok = [], bad = [];
  const re = /<script\b[^>]*type\s*=\s*["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi;
  let m;
  while ((m = re.exec(html))) {
    try {
      const parsed = JSON.parse(m[1].trim());
      (Array.isArray(parsed) ? parsed : [parsed]).forEach((o) => ok.push(o));
    } catch (e) {
      bad.push({ raw: m[1].slice(0, 120), error: e.message });
    }
  }
  return { ok, bad };
}

/** Walk a schema graph (handles @graph nesting) yielding every node. */
function* schemaNodes(objs) {
  const stack = [...objs];
  while (stack.length) {
    const node = stack.pop();
    if (!node || typeof node !== 'object') continue;
    if (Array.isArray(node)) { stack.push(...node); continue; }
    yield node;
    for (const v of Object.values(node)) {
      if (v && typeof v === 'object') stack.push(v);
    }
  }
}

/* ------------------------------------------------------------ the checks */

function auditFile(absPath) {
  const rel = relative(ROOT, absPath);
  const raw = readFileSync(absPath, 'utf8');
  const html = stripComments(raw);
  const findings = [];
  const add = (severity, section, message) => findings.push({ severity, section, message });

  const isErrorPage = /(^|\/)404\.html$/.test(rel);

  /* ===================== Document basics ===================== */

  if (!/^\s*<!doctype html>/i.test(raw)) {
    add('HIGH', '§3.1', 'Missing <!doctype html> — triggers quirks mode.');
  }

  const htmlTag = tagsOf(html, 'html')[0];
  const lang = htmlTag ? attr(htmlTag, 'lang') : null;
  if (!lang) {
    add('HIGH', '§3.1', 'No lang attribute on <html> — hurts accessibility and hreflang signals.');
  }

  if (!/<meta\b[^>]*charset\s*=\s*["']?utf-8/i.test(html)) {
    add('CRITICAL', '§9', 'No <meta charset="utf-8"> — curly quotes and em-dashes render as mojibake ("â€"").');
  }

  if (!/<meta\b[^>]*name\s*=\s*["']viewport["']/i.test(html)) {
    add('CRITICAL', '§3.2', 'No viewport meta — the page is not mobile-friendly, which is a ranking factor.');
  }

  /* ===================== Title ===================== */

  const titles = raw.match(/<title\b[^>]*>([\s\S]*?)<\/title>/gi) || [];
  if (titles.length === 0) {
    add('CRITICAL', '§3.1', 'No <title>. Every page needs exactly one.');
  } else if (titles.length > 1) {
    add('HIGH', '§3.1', `${titles.length} <title> tags — there must be exactly one.`);
  } else {
    const text = titles[0].replace(/<\/?title[^>]*>/gi, '').trim();
    if (!text) {
      add('CRITICAL', '§3.1', '<title> is empty.');
    } else if (text.length > 60) {
      add('MEDIUM', '§3.1', `<title> is ${text.length} chars — truncates in results past ~60. ("${text.slice(0, 62)}…")`);
    } else if (text.length < 30) {
      add('LOW', '§3.1', `<title> is only ${text.length} chars — room to add the keyword or location. ("${text}")`);
    }
  }

  /* ===================== Meta description ===================== */

  const descCount = countMeta(html, 'description');
  const desc = metaContent(html, 'description');
  if (descCount === 0) {
    if (!isErrorPage) add('HIGH', '§3.1', 'No meta description — Google writes its own snippet instead of your ad copy.');
  } else if (descCount > 1) {
    add('HIGH', '§3.1', `${descCount} meta descriptions — keep exactly one.`);
  } else if (desc) {
    if (desc.length > 165) add('MEDIUM', '§3.1', `Meta description is ${desc.length} chars — truncates past ~160.`);
    else if (desc.length < 110) add('LOW', '§3.1', `Meta description is only ${desc.length} chars — aim for ~140–160.`);
  }

  /* ===================== Headings ===================== */

  const h1s = raw.match(/<h1\b[^>]*>([\s\S]*?)<\/h1>/gi) || [];
  if (h1s.length === 0) {
    add('HIGH', '§3.1', 'No <h1>. Every page needs exactly one, matching its intent.');
  } else if (h1s.length > 1) {
    add('HIGH', '§3.1', `${h1s.length} <h1> tags — there must be exactly one.`);
  }

  const levels = [...html.matchAll(/<h([1-6])\b/gi)].map((m) => Number(m[1]));
  for (let i = 1; i < levels.length; i++) {
    if (levels[i] - levels[i - 1] > 1) {
      add('LOW', '§3.1', `Heading level jumps h${levels[i - 1]} → h${levels[i]} — never pick a heading for its visual size.`);
      break;
    }
  }

  /* ===================== Canonical ===================== */

  const canonicals = (html.match(/<link\b[^>]*rel\s*=\s*["']canonical["'][^>]*>/gi) || []);
  if (canonicals.length === 0) {
    if (!isErrorPage) add('HIGH', '§3.1', 'No self-referencing canonical.');
  } else if (canonicals.length > 1) {
    add('HIGH', '§3.1', `${canonicals.length} canonical tags — conflicting signals; keep one.`);
  } else {
    const href = attr(canonicals[0], 'href') || '';
    if (!/^https:\/\//i.test(href)) {
      add('HIGH', '§3.1', `Canonical must be an absolute https URL (found "${href}").`);
    } else if (ORIGIN && !href.startsWith(ORIGIN)) {
      add('CRITICAL', '§3.1', `Canonical points off-origin: "${href}" (expected ${ORIGIN}/…). A stale predecessor domain here de-indexes the page.`);
    }
    if (CONFIG?.domain?.trailingSlash && /\/[^/.]+$/.test(href)) {
      add('LOW', '§3.1', `Canonical "${href}" has no trailing slash — keep it consistent site-wide.`);
    }
  }

  /* ===================== Indexability ===================== */

  const robotsMeta = metaContent(html, 'robots') || '';
  if (/noindex/i.test(robotsMeta) && !isErrorPage) {
    add('CRITICAL', '§3.2', 'Page is set to noindex — it will not rank. Remove before launch.');
  }

  /* ===================== Social / Open Graph ===================== */

  const og = {
    title: metaContent(html, 'og:title', 'property'),
    description: metaContent(html, 'og:description', 'property'),
    image: metaContent(html, 'og:image', 'property'),
    url: metaContent(html, 'og:url', 'property'),
    type: metaContent(html, 'og:type', 'property'),
  };
  const missingOg = Object.entries(og).filter(([, v]) => !v).map(([k]) => `og:${k}`);
  if (missingOg.length && !isErrorPage) {
    add('MEDIUM', '§3.1', `Missing Open Graph tags: ${missingOg.join(', ')} — shared links show no preview.`);
  }
  if (og.image && !metaContent(html, 'og:image:alt', 'property')) {
    add('LOW', '§3.1', 'og:image has no og:image:alt.');
  }
  if (og.image && !/^https:\/\//i.test(og.image)) {
    add('MEDIUM', '§3.1', 'og:image must be an absolute URL — relative paths do not resolve in most scrapers.');
  }
  if (!metaContent(html, 'twitter:card') && !isErrorPage) {
    add('LOW', '§3.1', 'No twitter:card — set summary_large_image for a full-width preview.');
  }

  /* ===================== Images (perf + CLS + a11y) ===================== */

  const imgs = tagsOf(html, 'img');
  let heroCandidates = 0;

  imgs.forEach((img) => {
    const src = attr(img, 'src') || attr(img, 'data-src') || '(no src)';
    const label = basename(src.split('?')[0]);

    if (attr(img, 'alt') === null) {
      add('HIGH', '§G-perf', `<img ${label}> has no alt attribute. (Decorative? Use alt="".)`);
    }
    if (!attr(img, 'width') || !attr(img, 'height')) {
      add('HIGH', '§2.3', `<img ${label}> is missing width/height — this is a direct CLS regression.`);
    }
    if (hasAttr(img, 'fetchpriority') && (attr(img, 'fetchpriority') || '').toLowerCase() === 'high') {
      heroCandidates++;
      if ((attr(img, 'loading') || '').toLowerCase() === 'lazy') {
        add('CRITICAL', '§2.3', `<img ${label}> is both fetchpriority=high and loading=lazy — these cancel out and wreck LCP.`);
      }
    }
    if (/\.(jpe?g|png)$/i.test(src) && !/<picture\b/i.test(html)) {
      add('MEDIUM', '§2.3', `<img ${label}> is ${extname(src).slice(1).toUpperCase()} with no <picture> AVIF/WebP sources — usually the single biggest byte win.`);
    }
  });

  if (imgs.length > 3) {
    const lazy = imgs.filter((i) => (attr(i, 'loading') || '').toLowerCase() === 'lazy').length;
    if (lazy === 0) {
      add('MEDIUM', '§2.3', `${imgs.length} images and none use loading="lazy" — everything below the fold downloads up front.`);
    }
  }
  if (imgs.length > 0 && heroCandidates === 0 && !isErrorPage) {
    add('MEDIUM', '§2.3', 'No image marked fetchpriority="high". If the LCP element is an image, mark it and preload it.');
  }
  if (heroCandidates > 1) {
    add('MEDIUM', '§2.3', `${heroCandidates} images marked fetchpriority="high" — prioritising everything prioritises nothing.`);
  }

  /* ===================== Render-blocking CSS / fonts ===================== */

  const stylesheets = (html.match(/<link\b[^>]*rel\s*=\s*["']stylesheet["'][^>]*>/gi) || []);
  stylesheets.forEach((link) => {
    const href = attr(link, 'href') || '';
    const isAsync = /media\s*=\s*["']print["']/i.test(link) || hasAttr(link, 'onload');
    if (/fonts\.googleapis\.com/i.test(href)) {
      add('HIGH', '§2.5', 'Google Fonts loaded cross-origin — DNS+TCP+TLS to a third party before text renders. Self-host the woff2 files instead.');
    } else if (!isAsync) {
      add('MEDIUM', '§2.4', `Render-blocking stylesheet "${href}" — inline it (small site) or inline the critical CSS and load the rest async.`);
    }
  });

  if (/@font-face/i.test(raw) && !/font-display\s*:\s*swap/i.test(raw)) {
    add('MEDIUM', '§2.5', '@font-face without font-display:swap — text stays invisible during the font load.');
  }

  /* ===================== JavaScript / main thread ===================== */

  const headMatch = raw.match(/<head\b[^>]*>([\s\S]*?)<\/head>/i);
  const head = headMatch ? headMatch[1] : '';

  tagsOf(head, 'script').forEach((s) => {
    const src = attr(s, 'src');
    if (!src) return;
    const deferred = hasAttr(s, 'defer') || hasAttr(s, 'async');
    if (/googletagmanager\.com\/gtag\/js/i.test(src)) {
      add('HIGH', '§2.6', 'gtag.js is loaded directly in <head> (~66 KB of main-thread work during load). Queue the config and load the script on first interaction or idle — this is what took the reference site to 0 ms TBT.');
    } else if (!deferred) {
      add('HIGH', '§2.6', `Render-blocking script "${src}" in <head> — add defer.`);
    }
  });

  // Inline scripts declaring names that collide with window globals (handbook §9).
  const inlineScripts = [...raw.matchAll(/<script\b(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi)].map((m) => m[1]);
  const WINDOW_GLOBALS = ['top', 'self', 'parent', 'name', 'status', 'length', 'origin', 'closed', 'location', 'history'];
  inlineScripts.forEach((code) => {
    WINDOW_GLOBALS.forEach((g) => {
      if (new RegExp(`\\b(?:const|let|var)\\s+${g}\\b`).test(code)) {
        add('CRITICAL', '§9', `Inline script declares "${g}", which collides with a window global — the whole script throws silently and every handler in it dies.`);
      }
    });
  });

  /* ===================== Structured data ===================== */

  const { ok: schemas, bad } = jsonLd(raw);
  bad.forEach((b) => add('HIGH', '§3.3', `Malformed JSON-LD (${b.error}) — invalid schema is ignored entirely.`));

  const nodes = [...schemaNodes(schemas)];
  const types = new Set(nodes.flatMap((n) => (Array.isArray(n['@type']) ? n['@type'] : [n['@type']])).filter(Boolean));

  if (schemas.length === 0 && !isErrorPage) {
    add('MEDIUM', '§3.3', 'No JSON-LD structured data. Schema is what makes AI engines confident about your facts.');
  }

  // The honesty rule — non-negotiable (handbook §9).
  for (const node of nodes) {
    if (node.aggregateRating || node['@type'] === 'AggregateRating') {
      add('CRITICAL', '§9', 'aggregateRating found in schema. Never ship ratings markup without real, verifiable reviews — it violates Google guidelines and FTC rules.');
    }
    if (node['@type'] === 'Review') {
      add('CRITICAL', '§9', 'Review schema found. Only mark up genuine reviews you actually received.');
    }
    if (node.sameAs) {
      const links = Array.isArray(node.sameAs) ? node.sameAs : [node.sameAs];
      links.filter((l) => typeof l === 'string' && (l.includes('example.com') || l.endsWith('#') || l.trim() === ''))
        .forEach((l) => add('HIGH', '§3.3', `Placeholder sameAs link "${l}" — sameAs must point only at verified profiles you own.`));
    }
    if (node.telephone && CONFIG?.nap?.phoneE164 && node.telephone.replace(/[^\d+]/g, '') !== CONFIG.nap.phoneE164) {
      add('HIGH', '§4', `schema telephone "${node.telephone}" does not match site.config.json (${CONFIG.nap.phoneE164}). NAP drift hurts local ranking.`);
    }
  }

  // FAQPage schema must mirror the visible Q&A exactly.
  if (types.has('FAQPage')) {
    const faqNode = nodes.find((n) => n['@type'] === 'FAQPage');
    const questions = (faqNode?.mainEntity ?? []).filter((q) => q && q['@type'] === 'Question');
    const text = visibleText(raw);
    const missing = questions.filter((q) => {
      const name = normalise(String(q.name || ''));
      return name && !text.includes(name);
    });
    missing.forEach((q) =>
      add('HIGH', '§3.3', `FAQ schema question is not visible on the page: "${String(q.name).slice(0, 70)}…". FAQ schema must match the visible Q&A exactly.`)
    );
  }

  /* ===================== NAP consistency ===================== */

  const text = visibleText(raw);
  if (CONFIG?.nap?.phoneDisplay) {
    const telLinks = tagsOf(html, 'a').filter((a) => (attr(a, 'href') || '').startsWith('tel:'));
    telLinks.forEach((a) => {
      const href = attr(a, 'href');
      if (href.replace(/[^\d+]/g, '') !== CONFIG.nap.phoneE164) {
        add('HIGH', '§4', `tel: link "${href}" does not match the canonical number ${CONFIG.nap.phoneE164}. Every tel: link must be identical.`);
      }
    });
    // A visible number with no tap-to-call is a conversion leak on mobile.
    if (text.includes(CONFIG.nap.phoneDisplay) && telLinks.length === 0) {
      add('MEDIUM', '§G-launch', `The phone number is displayed but nothing links to tel:${CONFIG.nap.phoneE164} — mobile visitors can't tap to call.`);
    }
  }

  /* ===================== Leftover predecessor branding ===================== */

  const STALE = [
    ['thebaselinestudio.com', 'CRITICAL'],
    ['Baseline Studio', 'HIGH'],
    ['baselineplatformapp', 'HIGH'],
    ['info@thebaselinestudio.com', 'CRITICAL'],
    ['503-877-4254', 'CRITICAL'],
    ['5038774254', 'CRITICAL'],
  ];
  STALE.forEach(([needle, sev]) => {
    if (raw.toLowerCase().includes(needle.toLowerCase())) {
      add(sev, 'rebrand', `Leftover Baseline Studio reference: "${needle}". Every one of these must be gone before launch.`);
    }
  });

  /* ===================== Accessibility / semantics ===================== */

  if (!/<main\b/i.test(html) && !isErrorPage) {
    add('MEDIUM', '§3.1', 'No <main> landmark — screen readers and Google both use it to find the primary content.');
  }
  if (!/class\s*=\s*["'][^"']*skip/i.test(html) && !/#(main|content)["']/i.test(html) && !isErrorPage) {
    add('LOW', '§3.1', 'No skip-to-content link.');
  }

  const genericAnchors = tagsOf(html, 'a').length && [...raw.matchAll(/<a\b[^>]*>([\s\S]{0,40}?)<\/a>/gi)]
    .map((m) => visibleText(m[1]).toLowerCase())
    .filter((t) => ['click here', 'here', 'read more', 'learn more', 'this link'].includes(t));
  if (genericAnchors && genericAnchors.length > 2) {
    add('LOW', '§3.5', `${genericAnchors.length} links use generic anchor text ("click here" / "read more") — use descriptive text instead.`);
  }

  /* ===================== Page weight ===================== */

  const kb = Buffer.byteLength(raw, 'utf8') / 1024;
  if (kb > 150) {
    add('MEDIUM', '§2.2', `HTML document is ${kb.toFixed(0)} KB before assets — large inline payloads delay first paint.`);
  }

  return { file: rel, sizeKb: Number(kb.toFixed(1)), findings };
}

/* ------------------------------------------------------- discovery + CLI */

function walk(dir, acc = []) {
  for (const entry of readdirSync(dir)) {
    if (SKIP_DIRS.has(entry) || entry.startsWith('.')) continue;
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) walk(full, acc);
    else if (extname(full) === '.html') acc.push(full);
  }
  return acc;
}

const args = process.argv.slice(2);
const asJson = args.includes('--json');
const targets = args.filter((a) => !a.startsWith('--'));
const files = targets.length ? targets.map((f) => join(ROOT, f)) : walk(ROOT);

if (files.length === 0) {
  console.log('No HTML files found yet — nothing to audit.');
  console.log('The scaffold is ready; drop pages in and re-run.');
  process.exit(0);
}

const results = files.map(auditFile);
const all = results.flatMap((r) => r.findings);
const tally = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 };
all.forEach((f) => tally[f.severity]++);
const blocking = tally.CRITICAL + tally.HIGH;

if (asJson) {
  console.log(JSON.stringify({ tally, results }, null, 2));
  process.exit(blocking ? 1 : 0);
}

const COLOR = { CRITICAL: '\x1b[41m\x1b[97m', HIGH: '\x1b[31m', MEDIUM: '\x1b[33m', LOW: '\x1b[90m' };
const RESET = '\x1b[0m';
const BOLD = '\x1b[1m';

console.log(`\n${BOLD}Willamette Web Design — preflight audit${RESET}`);
console.log(`${files.length} page(s) · handbook: docs/SEO-HANDBOOK.md\n`);

for (const r of results) {
  if (!r.findings.length) {
    console.log(`\x1b[32m✔\x1b[0m ${BOLD}${r.file}${RESET} \x1b[90m(${r.sizeKb} KB)${RESET} — clean`);
    continue;
  }
  console.log(`${BOLD}${r.file}${RESET} \x1b[90m(${r.sizeKb} KB)${RESET}`);
  r.findings
    .sort((a, b) => SEVERITY[a.severity] - SEVERITY[b.severity])
    .forEach((f) => {
      console.log(`  ${COLOR[f.severity]} ${f.severity} ${RESET} \x1b[90m${f.section}\x1b[0m  ${f.message}`);
    });
  console.log('');
}

console.log(`${BOLD}Summary${RESET}  ` +
  `${COLOR.CRITICAL} ${tally.CRITICAL} critical ${RESET} ` +
  `\x1b[31m${tally.HIGH} high\x1b[0m · ` +
  `\x1b[33m${tally.MEDIUM} medium\x1b[0m · ` +
  `\x1b[90m${tally.LOW} low\x1b[0m`);

if (blocking) {
  console.log(`\n\x1b[31mBlocking: fix CRITICAL and HIGH before deploying.\x1b[0m (handbook §7 — severity order)\n`);
} else if (tally.MEDIUM || tally.LOW) {
  console.log(`\n\x1b[32mNo blocking findings.\x1b[0m Medium/low items are worth a pass before launch.\n`);
} else {
  console.log(`\n\x1b[32mAll checks pass.\x1b[0m\n`);
}

process.exit(blocking ? 1 : 0);
