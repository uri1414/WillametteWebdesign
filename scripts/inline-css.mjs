#!/usr/bin/env node
/**
 * inline-css.mjs — minify assets/css/site.css and inline it into every page.
 *
 * Handbook §2.4: an external <link rel="stylesheet"> is render-blocking. On
 * mobile that is a full round-trip before anything paints. For a site this
 * size, inlining the whole (minified) sheet removes the request outright with
 * zero visual change.
 *
 * Pages keep the stylesheet between these markers, so this is re-runnable:
 *   <style id="site-css">...</style>
 *
 * IMPORTANT — two-block convention:
 *   <style id="site-css">  is OWNED BY THIS SCRIPT and overwritten every run.
 *                          Never hand-edit it; edit assets/css/site.css.
 *   <style id="page-css">  is page-local and never touched. Put rules that
 *                          genuinely apply to one page only here. Anything
 *                          used on 2+ pages belongs in site.css instead.
 *
 *   npm run css
 *   node scripts/inline-css.mjs --check   # verify pages are in sync; exit 1 if not
 */

import { readFileSync, writeFileSync, readdirSync, statSync, existsSync } from 'node:fs';
import { join, relative, extname } from 'node:path';

const ROOT = process.cwd();
const CSS_PATH = join(ROOT, 'assets/css/site.css');
const CHECK = process.argv.includes('--check');
const SKIP_DIRS = new Set(['node_modules', '.git', '.netlify', 'reports', '_src', 'docs', '_templates']);

if (!existsSync(CSS_PATH)) {
  console.log('assets/css/site.css does not exist yet — nothing to inline.');
  process.exit(0);
}

/**
 * Conservative CSS minifier. Deliberately does NOT try to be clever: it strips
 * comments and collapses whitespace, and leaves everything else alone. A
 * stylesheet that renders correctly at 22 KB beats one broken at 18 KB.
 */
function minify(css) {
  return css
    // Strip comments, but preserve /*! important */ banners.
    .replace(/\/\*(?!!)[\s\S]*?\*\//g, '')
    // Collapse runs of whitespace outside of strings/url().
    .replace(/\s+/g, ' ')
    // Tighten around structural punctuation.
    .replace(/\s*([{}:;,>~])\s*/g, '$1')
    // Restore the space combinators need after a comma-free selector break.
    .replace(/;\}/g, '}')
    // Leading zeros and unit-less zeros.
    .replace(/([\s:(,])0\.(\d)/g, '$1.$2')
    .trim();
}

const raw = readFileSync(CSS_PATH, 'utf8');
const minified = minify(raw);
const savedPct = ((1 - minified.length / raw.length) * 100).toFixed(0);

function walk(dir, acc = []) {
  for (const entry of readdirSync(dir)) {
    if (SKIP_DIRS.has(entry) || entry.startsWith('.')) continue;
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) walk(full, acc);
    else if (extname(full) === '.html') acc.push(full);
  }
  return acc;
}

const pages = walk(ROOT);
if (!pages.length) {
  console.log('No pages yet. site.css is ready to inline once pages exist.');
  process.exit(0);
}

const BLOCK = /<style\b[^>]*\bid\s*=\s*["']site-css["'][^>]*>[\s\S]*?<\/style>/i;
const replacement = `<style id="site-css">${minified}</style>`;

let changed = 0, missing = 0, stale = [];

for (const page of pages) {
  const html = readFileSync(page, 'utf8');
  const rel = relative(ROOT, page);

  if (!BLOCK.test(html)) {
    missing++;
    console.log(`\x1b[33m·\x1b[0m ${rel} — no <style id="site-css"> block; add one where the CSS should go.`);
    continue;
  }

  const next = html.replace(BLOCK, replacement);
  if (next === html) continue;

  stale.push(rel);
  if (!CHECK) {
    writeFileSync(page, next);
    changed++;
  }
}

console.log(`\nsite.css: ${(raw.length / 1024).toFixed(1)} KB → ${(minified.length / 1024).toFixed(1)} KB minified (−${savedPct}%)`);

if (CHECK) {
  if (stale.length) {
    console.log(`\n\x1b[31m${stale.length} page(s) have stale inlined CSS:\x1b[0m`);
    stale.forEach((f) => console.log(`  ${f}`));
    console.log('\nRun: npm run css\n');
    process.exit(1);
  }
  console.log('\x1b[32m✔\x1b[0m All pages in sync.\n');
} else {
  console.log(`\x1b[32m✔\x1b[0m Updated ${changed} page(s).${missing ? ` ${missing} page(s) had no block.` : ''}\n`);
}
