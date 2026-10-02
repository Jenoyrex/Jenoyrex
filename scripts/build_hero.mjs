// Builds assets/hero.gif: assets/night.gif with "Jenoy Rex" set in the centre of the scene.
// night.gif itself is only read, never modified; every frame and its timing are kept.
//
//   npm install playwright-core @fontsource/inter
//   FONT_MODULES=./node_modules CHROMIUM=/path/to/chromium node scripts/build_hero.mjs
//
// Needs ffmpeg on PATH.
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const MODS = path.resolve(process.env.FONT_MODULES || 'node_modules');
const { chromium } = createRequire(`${MODS}/`)('playwright-core');
const W = 750, H = 270;   // night.gif's size
const font = (file) => `data:font/woff2;base64,${fs.readFileSync(`${MODS}/@fontsource/inter/files/${file}`).toString('base64')}`;

// Transparent overlay: the name centred on the banner. Clouds drift behind it, so it carries
// a soft dark outline (drawn under the fill) to stay readable over white cloud and dark sky alike.
const html = `<style>
@font-face{font-family:Inter;font-weight:600;src:url(${font('inter-latin-600-normal.woff2')})}
html,body{margin:0;background:transparent}
</style>
<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}">
  <text x="${W / 2}" y="150" text-anchor="middle" font-family="Inter" font-weight="600" font-size="42"
        letter-spacing="-0.5" fill="#e6edf3" stroke="#0b0d12" stroke-opacity="0.7" stroke-width="6"
        stroke-linejoin="round" paint-order="stroke">Jenoy Rex</text>
</svg>`;

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'hero-'));
const overlay = path.join(tmp, 'overlay.png');
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
const page = await browser.newPage({ viewport: { width: W, height: H } });
await page.setContent(html);
await page.evaluate(() => document.fonts.ready);
await page.screenshot({ path: overlay, omitBackground: true });
await browser.close();

execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', path.join(ROOT, 'assets/night.gif'), '-i', overlay,
  '-filter_complex', '[0:v][1:v]overlay=0:0,split[a][b];[a]palettegen=max_colors=48:stats_mode=full[p];[b][p]paletteuse=dither=none:diff_mode=rectangle',
  '-loop', '0', path.join(ROOT, 'assets/hero.gif')]);
fs.rmSync(tmp, { recursive: true });
console.log(`assets/hero.gif: ${(fs.statSync(path.join(ROOT, 'assets/hero.gif')).size / 1024).toFixed(0)} KB`);
