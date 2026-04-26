#!/usr/bin/env node
/**
 * Generate the favicon pack for both portals from the brand-mark SVGs.
 *
 * Per ADR-0010: every portal has a custom favicon. This script is the only
 * supported way to (re)generate the PNGs / ICO. Outputs are committed so
 * portal builds do not depend on running the script.
 *
 * Usage: npm run generate:favicons
 */

const fs = require('fs');
const path = require('path');
const sharp = require('sharp');
const pngToIco = require('png-to-ico');

const ROOT = path.resolve(__dirname, '..');
const BRAND_DIR = path.join(ROOT, 'design-system/brand');
const OUT_BASE = path.join(ROOT, 'design-system/favicons');

const VARIANTS = [
  { name: 'customer', svg: 'brand-mark.svg',       displayName: 'TrésorAI',       shortName: 'TrésorAI'   },
  { name: 'admin',    svg: 'brand-mark-admin.svg', displayName: 'TrésorAI Admin', shortName: 'TresorAdmin' },
];

const SIZE_FILE = {
  16:  'favicon-16.png',
  32:  'favicon-32.png',
  48:  'favicon-48.png',
  180: 'apple-touch-icon-180.png',
  192: 'icon-192.png',
  512: 'icon-512.png',
};
const SIZES = Object.keys(SIZE_FILE).map(Number);

async function generateForVariant(variant) {
  const svgPath = path.join(BRAND_DIR, variant.svg);
  const outDir = path.join(OUT_BASE, variant.name);
  fs.mkdirSync(outDir, { recursive: true });

  const svg = fs.readFileSync(svgPath);

  for (const size of SIZES) {
    const out = path.join(outDir, SIZE_FILE[size]);
    await sharp(svg, { density: 384 })
      .resize(size, size)
      .png()
      .toFile(out);
    console.log(`  ${variant.name}/${SIZE_FILE[size]}`);
  }

  const icoBuf = await pngToIco([
    path.join(outDir, 'favicon-16.png'),
    path.join(outDir, 'favicon-32.png'),
    path.join(outDir, 'favicon-48.png'),
  ]);
  fs.writeFileSync(path.join(outDir, 'favicon.ico'), icoBuf);
  console.log(`  ${variant.name}/favicon.ico`);

  const manifest = {
    name: variant.displayName,
    short_name: variant.shortName,
    icons: [
      { src: '/icon-192.png', sizes: '192x192', type: 'image/png' },
      { src: '/icon-512.png', sizes: '512x512', type: 'image/png' },
    ],
    theme_color: '#047857',
    background_color: '#FAFAF6',
    display: 'standalone',
    start_url: '/',
  };
  fs.writeFileSync(
    path.join(outDir, 'site.webmanifest'),
    JSON.stringify(manifest, null, 2) + '\n',
  );
  console.log(`  ${variant.name}/site.webmanifest`);
}

(async () => {
  for (const v of VARIANTS) {
    console.log(`\nGenerating ${v.name} favicons...`);
    await generateForVariant(v);
  }
  console.log('\nDone.');
})().catch((err) => {
  console.error('generate-favicons failed:', err);
  process.exit(1);
});
