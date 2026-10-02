// Renders assets/hero.gif: a 4-second seamless loop, 1000x250.
//
//   npm install playwright-core @fontsource/inter @fontsource/jetbrains-mono
//   FONT_MODULES=./node_modules CHROMIUM=/path/to/chromium node scripts/hero/render.mjs
//
// Needs ffmpeg on PATH. Only the graph and the cursor move; all text is static.
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../..');
const MODS = path.resolve(process.env.FONT_MODULES || 'node_modules');
const { chromium } = createRequire(`${MODS}/`)('playwright-core');
const W = 1000, H = 250, FPS = 12, SECONDS = 4, FRAMES = FPS * SECONDS;
const font = (pkg, file) => `data:font/woff2;base64,${fs.readFileSync(`${MODS}/@fontsource/${pkg}/files/${file}`).toString('base64')}`;

const C = { bg: '#0d1117', grid: '#1b2230', text: '#f0f6fc', sub: '#c9d1d9', muted: '#8b949e', edge: '#2d3748', cyan: '#38bdf8', violet: '#a78bfa', node: '#475569' };

// Graph, in banner coordinates.
const N = { a: [640, 70], b: [700, 162], c: [726, 112], d: [770, 196], e: [810, 82], f: [858, 176], g: [880, 128], h: [930, 186], i: [948, 92] };
const EDGES = [['a', 'c'], ['c', 'e'], ['e', 'g'], ['g', 'i'], ['c', 'd'], ['d', 'f'], ['f', 'g'], ['a', 'b'], ['b', 'd'], ['e', 'f'], ['i', 'h'], ['h', 'f']];
const ACTIVE = [['b', 'c', 'e', 'g', 'i'], ['a', 'c', 'd', 'f', 'h'], ['b', 'd', 'f', 'g', 'i']]; // particle routes
const HOT = { c: C.cyan, e: C.violet, g: C.violet, d: C.cyan, f: C.violet };

function along(route, u) {
  const pts = route.map((k) => N[k]);
  const lens = pts.slice(1).map((p, i) => Math.hypot(p[0] - pts[i][0], p[1] - pts[i][1]));
  let dist = u * lens.reduce((x, y) => x + y, 0);
  for (let i = 0; i < lens.length; i++) {
    if (dist <= lens[i]) { const t = dist / lens[i]; return [pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t]; }
    dist -= lens[i];
  }
  return pts.at(-1);
}

function frame(f) {
  const t = f / FRAMES; // 0..1 over the loop
  const grid = [];
  for (let x = 20; x < W; x += 24) for (let y = 14; y < H; y += 24) grid.push(`<circle cx="${x}" cy="${y}" r="1" fill="${C.grid}"/>`);
  const edges = EDGES.map(([p, q]) => `<line x1="${N[p][0]}" y1="${N[p][1]}" x2="${N[q][0]}" y2="${N[q][1]}" stroke="${C.edge}" stroke-width="1.4"/>`);
  const particles = [];
  ACTIVE.forEach((route, r) => {
    for (const lag of [0, 0.035, 0.07]) {
      const u = ((t + r / ACTIVE.length - lag) % 1 + 1) % 1;
      const [x, y] = along(route, u);
      particles.push(`<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${lag ? 2 : 3}" fill="${r === 1 ? C.violet : C.cyan}" opacity="${1 - lag * 9}"/>`);
    }
  });
  const nodes = Object.entries(N).map(([k, [x, y]], i) => {
    const hot = HOT[k];
    const pulse = hot ? 0.5 + 0.5 * Math.sin(2 * Math.PI * (t + i / 9)) : 0;
    return (hot ? `<circle cx="${x}" cy="${y}" r="${9 + 5 * pulse}" fill="none" stroke="${hot}" stroke-opacity="${0.35 * (1 - pulse)}"/>` : '')
      + `<circle cx="${x}" cy="${y}" r="${hot ? 6 : 4.5}" fill="${C.bg}" stroke="${hot || C.node}" stroke-width="2"/>`;
  });
  const cursorOn = Math.floor(t * SECONDS * 2) % 2 === 0; // blinks twice per second
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
  <rect width="${W}" height="${H}" fill="${C.bg}"/>${grid.join('')}${edges.join('')}${particles.join('')}${nodes.join('')}
  <text x="56" y="70" font-family="JetBrains Mono" font-size="16" fill="${C.muted}">~/jenoyrex <tspan fill="${C.cyan}">$</tspan> whoami</text>
  ${cursorOn ? `<rect x="242" y="56" width="9" height="18" fill="${C.cyan}"/>` : ''}
  <text x="52" y="132" font-family="Inter" font-weight="700" font-size="58" fill="${C.text}" letter-spacing="-1">Jenoy Rex</text>
  <rect x="56" y="148" width="64" height="3" rx="1.5" fill="${C.cyan}"/>
  <text x="56" y="184" font-family="Inter" font-weight="600" font-size="22" fill="${C.sub}">Data Science Engineering · Backend &amp; ML Systems</text>
  <text x="56" y="214" font-family="JetBrains Mono" font-size="14" fill="${C.muted}">APIs · data pipelines · LLM evaluation · security</text>
</svg>`;
}

const css = `@font-face{font-family:Inter;font-weight:600;src:url(${font('inter', 'inter-latin-600-normal.woff2')})}
@font-face{font-family:Inter;font-weight:700;src:url(${font('inter', 'inter-latin-700-normal.woff2')})}
@font-face{font-family:'JetBrains Mono';src:url(${font('jetbrains-mono', 'jetbrains-mono-latin-400-normal.woff2')})}
html,body{margin:0;background:${C.bg}}`;

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'hero-'));
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
const page = await browser.newPage({ viewport: { width: W, height: H } });
for (let f = 0; f < FRAMES; f++) {
  await page.setContent(`<style>${css}</style>${frame(f)}`);
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: path.join(tmp, `f${String(f).padStart(3, '0')}.png`) });
}
await browser.close();
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', path.join(tmp, 'f%03d.png'),
  '-vf', 'split[a][b];[a]palettegen=max_colors=64:stats_mode=full[p];[b][p]paletteuse=dither=none:diff_mode=rectangle',
  '-loop', '0', path.join(ROOT, 'assets/hero.gif')]);
fs.rmSync(tmp, { recursive: true });
console.log(`assets/hero.gif: ${FRAMES} frames @ ${FPS} fps, ${(fs.statSync(path.join(ROOT, 'assets/hero.gif')).size / 1024).toFixed(0)} KB`);
