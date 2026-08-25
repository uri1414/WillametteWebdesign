#!/usr/bin/env node
/**
 * optimize-images.mjs — responsive AVIF/WebP derivative pipeline (handbook §2.3).
 *
 * Images are 60-80% of page weight, so this is the biggest single perf lever.
 * Drop full-resolution masters into assets/img/_src/ (gitignored - masters
 * never ship), run this, and get width-stepped AVIF + WebP derivatives plus a
 * ready-to-paste <picture> block for each one.
 *
 *   npm run images                    # process everything in assets/img/_src/
 *   node scripts/optimize-images.mjs hero.jpg --widths 640,960,1280,1920
 *   node scripts/optimize-images.mjs hero.jpg --hero    # emits preload + fetchpriority
 *
 * Requires sharp:  npm install
 */

import { readdirSync, existsSync, mkdirSync, statSync } from 'node:fs';
import { join, parse } from 'node:path';

let sharp;
try {
  sharp = (await import('sharp')).default;
} catch {
  console.error('\n\x1b[31msharp is not installed.\x1b[0m  Run:  npm install\n');
  console.error('sharp handles AVIF + WebP encoding. It is a devDependency - it never ships to the site.\n');
  process.exit(1);
}

const SRC_DIR = 'assets/img/_src';
const OUT_DIR = 'assets/img';

const args = process.argv.slice(2);
const flag = (name, fallback) => {
  const i = args.indexOf(`--${name}`);
  return i !== -1 && args[i + 1] ? args[i + 1] : fallback;
};
const isHero = args.includes('--hero');
const WIDTHS = flag('widths', '640,960,1280,1920').split(',').map(Number).sort((a, b) => a - b);

// Quality settings: AVIF runs lower because it holds detail far better at the
// same number. These are the values that survived side-by-side comparison.
const AVIF_Q = Number(flag('avif-quality', 58));
const WEBP_Q = Number(flag('webp-quality', 78));

if (!existsSync(SRC_DIR)) mkdirSync(SRC_DIR, { recursive: true });
if (!existsSync(OUT_DIR)) mkdirSync(OUT_DIR, { recursive: true });

const named = args.filter((a) => !a.startsWith('--') && !/^\d/.test(a));
const files = named.length
  ? named
  : readdirSync(SRC_DIR).filter((f) => /\.(jpe?g|png|webp|tiff?)$/i.test(f));

if (!files.length) {
  console.log(`\nNo source images found in ${SRC_DIR}/`);
  console.log('Drop full-resolution masters there and re-run. They stay out of git and out of the deploy.\n');
  process.exit(0);
}

const fmtKb = (b) => `${(b / 1024).toFixed(0)} KB`;

for (const file of files) {
  const srcPath = existsSync(join(SRC_DIR, file)) ? join(SRC_DIR, file) : file;
  if (!existsSync(srcPath)) {
    console.error(`\x1b[31m x \x1b[0m ${file} - not found`);
    continue;
  }

  const { name } = parse(srcPath);
  const meta = await sharp(srcPath).metadata();
  const originalBytes = statSync(srcPath).size;

  console.log(`\n\x1b[1m${name}\x1b[0m  ${meta.width}x${meta.height}  ${fmtKb(originalBytes)} source`);

  // Never upscale: a 900px master should not produce a 1920w derivative.
  const widths = WIDTHS.filter((w) => w <= meta.width);
  if (!widths.length) widths.push(meta.width);

  const made = { avif: [], webp: [] };

  for (const w of widths) {
    const avifOut = join(OUT_DIR, `${name}-${w}.avif`);
    const webpOut = join(OUT_DIR, `${name}-${w}.webp`);

    const [avifInfo, webpInfo] = await Promise.all([
      sharp(srcPath).resize({ width: w, withoutEnlargement: true })
        .avif({ quality: AVIF_Q, effort: 4 }).toFile(avifOut),
      sharp(srcPath).resize({ width: w, withoutEnlargement: true })
        .webp({ quality: WEBP_Q }).toFile(webpOut),
    ]);

    made.avif.push({ w, path: `/${avifOut}`, size: avifInfo.size });
    made.webp.push({ w, path: `/${webpOut}`, size: webpInfo.size });

    const saving = (1 - avifInfo.size / originalBytes) * 100;
    console.log(
      `  ${String(w).padStart(4)}w   avif ${fmtKb(avifInfo.size).padStart(7)}   ` +
      `webp ${fmtKb(webpInfo.size).padStart(7)}   \x1b[32m-${saving.toFixed(0)}%\x1b[0m vs source`
    );
  }

  // A JPEG fallback for the handful of clients that support neither format.
  const fallbackW = widths[widths.length - 1];
  const fallback = join(OUT_DIR, `${name}-${fallbackW}.jpg`);
  await sharp(srcPath).resize({ width: fallbackW, withoutEnlargement: true })
    .jpeg({ quality: 82, mozjpeg: true }).toFile(fallback);

  // Intrinsic dimensions of the fallback - these go in width/height to reserve
  // layout space and protect CLS.
  const fbMeta = await sharp(fallback).metadata();

  const srcset = (list) => list.map((d) => `${d.path} ${d.w}w`).join(', ');
  const sizes = isHero ? '100vw' : '(max-width: 768px) 100vw, 50vw';

  console.log(`\n  \x1b[90m--- paste into the page ---\x1b[0m`);
  if (isHero) {
    console.log(`
  <!-- in <head>: preload the LCP image so it starts downloading immediately -->
  <link rel="preload" as="image" type="image/avif"
        href="${made.avif[0].path}"
        imagesrcset="${srcset(made.avif)}"
        imagesizes="${sizes}" fetchpriority="high">`);
  }
  console.log(`
  <picture>
    <source type="image/avif" srcset="${srcset(made.avif)}" sizes="${sizes}">
    <source type="image/webp" srcset="${srcset(made.webp)}" sizes="${sizes}">
    <img src="/${fallback}" alt="TODO: describe the image"
         width="${fbMeta.width}" height="${fbMeta.height}"
         ${isHero ? 'fetchpriority="high" decoding="async"' : 'loading="lazy" decoding="async"'}
         style="object-fit:cover">
  </picture>
`);
}

console.log(`\x1b[90mReminders:\x1b[0m`);
console.log(`  - width + height on every <img> - missing them is a direct CLS hit.`);
console.log(`  - exactly one hero gets fetchpriority="high"; it must NOT be loading="lazy".`);
console.log(`  - everything below the fold: loading="lazy" decoding="async".`);
console.log(`  - a display:none image still downloads - don't render it at all on mobile.\n`);
