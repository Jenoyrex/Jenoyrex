// Builds the icon tiles and buttons in assets/ from upstream icon packages.
//
//   npm install simple-icons lucide-static @tabler/icons @lobehub/icons-static-svg
//   ICON_MODULES=./node_modules node scripts/build-icons.mjs
//
// Sources and licences are listed in assets/icons/NOTICE.md.
import fs from 'node:fs';
import path from 'node:path';

const MODS = process.env.ICON_MODULES || 'node_modules';
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const out = (p) => { fs.mkdirSync(path.dirname(path.join(ROOT, p)), { recursive: true }); return path.join(ROOT, p); };

const C = { bg: '#161b22', border: '#30363d', text: '#e6edf3', muted: '#8b949e', cyan: '#38bdf8', violet: '#a78bfa' };
const FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif";
const MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace";

const siData = JSON.parse(fs.readFileSync(`${MODS}/simple-icons/data/simple-icons.json`, 'utf8'));
const siList = Array.isArray(siData) ? siData : siData.icons;

// Inner markup of a source SVG (without the <svg> wrapper, <title> and comments).
function inner(file) {
  const s = fs.readFileSync(file, 'utf8').replace(/<!--[\s\S]*?-->/g, '');
  return s.slice(s.indexOf('>', s.indexOf('<svg')) + 1, s.lastIndexOf('</svg>'))
    .replace(/<title>[\s\S]*?<\/title>/g, '').replace(/<path stroke="none" d="M0 0h24v24H0z" fill="none" \/>/g, '').trim();
}
function lum(hex) {
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255)
    .map((v) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}
// Brand colour, blended toward white only as far as needed for 4.5:1 contrast on the tile.
const BG_LUM = lum(C.bg.slice(1));
function tone(hex) {
  const mix = (t) => [0, 2, 4].map((i) => Math.round(parseInt(hex.slice(i, i + 2), 16) * (1 - t) + 255 * t)
    .toString(16).padStart(2, '0')).join('');
  for (let t = 0; t <= 1; t += 0.05) { const h = mix(t); if ((lum(h) + 0.05) / (BG_LUM + 0.05) >= 4.5) return `#${h}`; }
  return C.text;
}

const glyph = {
  si: (slug) => { const d = siList.find((x) => (x.slug || '') === slug) || siList.find((x) => x.title.toLowerCase().replace(/[^a-z0-9]/g, '') === slug);
    if (!d) throw new Error(`simple-icons: ${slug}`); return { body: inner(`${MODS}/simple-icons/icons/${slug}.svg`), color: tone(d.hex), mode: 'fill', title: d.title }; },
  lobe: (name, color) => ({ body: inner(`${MODS}/@lobehub/icons-static-svg/icons/${name}.svg`), color, mode: 'fill' }),
  tabler: (name, color, filled = false) => ({ body: inner(`${MODS}/@tabler/icons/icons/${filled ? 'filled' : 'outline'}/${name}.svg`), color, mode: filled ? 'fill' : 'stroke' }),
  lucide: (name, color) => ({ body: inner(`${MODS}/lucide-static/icons/${name}.svg`), color, mode: 'stroke' }),
};
const paint = (g) => (g.mode === 'fill' ? `fill="${g.color}"` : `fill="none" stroke="${g.color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"`);

// 64x64 tile with a 24-unit glyph scaled to 32px.
function tile(name, label, g) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" role="img" aria-label="${label}">
  <title>${label}</title>
  <rect x="1" y="1" width="62" height="62" rx="14" fill="${C.bg}" stroke="${C.border}" stroke-width="1.5"/>
  <g transform="translate(16 16) scale(1.3333)" ${paint(g)}>${g.body}</g>
</svg>\n`;
}
// Tile for tools without an official logo: their name, set in monospace.
function textTile(label, color) {
  const size = label.length > 7 ? 10.5 : 13;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" role="img" aria-label="${label}">
  <title>${label}</title>
  <rect x="1" y="1" width="62" height="62" rx="14" fill="${C.bg}" stroke="${C.border}" stroke-width="1.5"/>
  <text x="32" y="36.5" font-family="${MONO}" font-size="${size}" font-weight="600" fill="${color}" text-anchor="middle">${label}</text>
</svg>\n`;
}
// Plain glyph (section headings) or small tile (project cards).
const plain = (label, g, size = 24) => `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 24 24" role="img" aria-label="${label}"><title>${label}</title><g ${paint(g)}>${g.body}</g></svg>\n`;
// Pill button with a glyph and a label.
function button(label, g, accent, width) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="40" viewBox="0 0 ${width} 40" role="img" aria-label="${label}">
  <title>${label}</title>
  <rect x="0.75" y="0.75" width="${width - 1.5}" height="38.5" rx="10" fill="${C.bg}" stroke="${accent}" stroke-opacity="0.55" stroke-width="1.5"/>
  <g transform="translate(16 11) scale(0.75)" ${paint(g)}>${g.body}</g>
  <text x="44" y="25" font-family="${FONT}" font-size="14" font-weight="600" fill="${C.text}">${label}</text>
</svg>\n`;
}

const tech = [
  ['python', 'Python', glyph.si('python')],
  ['typescript', 'TypeScript', glyph.si('typescript')],
  ['sql', 'SQL', glyph.tabler('sql', C.cyan)],
  ['fastapi', 'FastAPI', glyph.si('fastapi')],
  ['sqlalchemy', 'SQLAlchemy', glyph.si('sqlalchemy')],
  ['alembic', 'Alembic', null],
  ['express', 'Express', glyph.si('express')],
  ['prisma', 'Prisma', glyph.si('prisma')],
  ['postgresql', 'PostgreSQL', glyph.si('postgresql')],
  ['clickhouse', 'ClickHouse', glyph.si('clickhouse')],
  ['nextjs', 'Next.js', glyph.si('nextdotjs')],
  ['react', 'React', glyph.si('react')],
  ['scikit-learn', 'scikit-learn', glyph.si('scikitlearn')],
  ['fastembed', 'fastembed', null],
  ['anthropic', 'Anthropic API', glyph.lobe('anthropic', '#d97757')],
  ['openai', 'OpenAI API', glyph.lobe('openai', C.text)],
  ['docker', 'Docker', glyph.si('docker')],
  ['github-actions', 'GitHub Actions', glyph.si('githubactions')],
  ['pytest', 'pytest', glyph.si('pytest')],
  ['vitest', 'Vitest', glyph.si('vitest')],
  ['sqlite', 'SQLite', glyph.si('sqlite')],
];
for (const [file, label, g] of tech) {
  fs.writeFileSync(out(`assets/icons/tech/${file}.svg`), g ? tile(file, label, g) : textTile(label, C.violet));
}

const ui = {
  about: ['terminal', C.cyan], connect: ['send', C.cyan], work: ['layers', C.cyan], stack: ['blocks', C.cyan],
  analytics: ['chart-column', C.cyan], achievements: ['trophy', C.cyan],
  vigil: ['radar', C.violet], vaultdrop: ['shield-check', C.violet], adpo: ['workflow', C.violet], 'multi-agent': ['network', C.violet],
};
for (const [file, [name, color]] of Object.entries(ui)) fs.writeFileSync(out(`assets/icons/ui/${file}.svg`), plain(name, glyph.lucide(name, color)));

const buttons = {
  linkedin: ['LinkedIn', glyph.tabler('brand-linkedin', tone('0a66c2'), true), '#0a66c2', 124],
  email: ['Email', glyph.si('gmail'), '#ea4335', 100],
  github: ['GitHub', glyph.si('github'), '#8b949e', 112],
  repository: ['Repository', glyph.si('github'), '#8b949e', 136],
  demo: ['Live demo', glyph.lucide('external-link', C.cyan), C.cyan, 128],
};
for (const [file, [label, g, accent, w]] of Object.entries(buttons)) fs.writeFileSync(out(`assets/buttons/${file}.svg`), button(label, g, accent, w));
console.log(`tech ${tech.length}, ui ${Object.keys(ui).length}, buttons ${Object.keys(buttons).length}`);
