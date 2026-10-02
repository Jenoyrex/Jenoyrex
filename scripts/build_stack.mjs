// Builds the monochrome technology tiles in assets/stack/ (logo + label, no background).
//
//   npm install simple-icons @lobehub/icons-static-svg
//   ICON_MODULES=./node_modules node scripts/build_stack.mjs
//
// Logos: simple-icons (CC0-1.0) and @lobehub/icons-static-svg (MIT, Anthropic and OpenAI).
// They remain trademarks of their owners and are used only to identify the technologies.
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const MODS = path.resolve(process.env.ICON_MODULES || 'node_modules');
const GLYPH = '#c9d1d9', LABEL = '#8b949e';
const MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace";

function inner(file) {
  const s = fs.readFileSync(file, 'utf8').replace(/<!--[\s\S]*?-->/g, '');
  return s.slice(s.indexOf('>', s.indexOf('<svg')) + 1, s.lastIndexOf('</svg>')).replace(/<title>[\s\S]*?<\/title>/g, '').trim();
}
const si = (slug) => inner(`${MODS}/simple-icons/icons/${slug}.svg`);
const lobe = (name) => inner(`${MODS}/@lobehub/icons-static-svg/icons/${name}.svg`);

// Evidenced in the featured repositories (see README "Selected work").
const stack = [
  ['python', 'PYTHON', si('python')], ['typescript', 'TYPESCRIPT', si('typescript')],
  ['javascript', 'JAVASCRIPT', si('javascript')], ['fastapi', 'FASTAPI', si('fastapi')],
  ['sqlalchemy', 'SQLALCHEMY', si('sqlalchemy')], ['postgresql', 'POSTGRESQL', si('postgresql')],
  ['clickhouse', 'CLICKHOUSE', si('clickhouse')], ['express', 'EXPRESS', si('express')],
  ['prisma', 'PRISMA', si('prisma')], ['nextjs', 'NEXT.JS', si('nextdotjs')],
  ['react', 'REACT', si('react')], ['scikit-learn', 'SCIKIT-LEARN', si('scikitlearn')],
  ['anthropic', 'ANTHROPIC', lobe('anthropic')], ['openai', 'OPENAI', lobe('openai')],
  ['docker', 'DOCKER', si('docker')], ['github-actions', 'GH ACTIONS', si('githubactions')],
];

fs.mkdirSync(path.join(ROOT, 'assets/stack'), { recursive: true });
for (const [file, label, body] of stack) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="104" height="84" viewBox="0 0 104 84" role="img" aria-label="${label}">
  <title>${label}</title>
  <g transform="translate(36 10) scale(1.3333)" fill="${GLYPH}">${body}</g>
  <text x="52" y="72" font-family="${MONO}" font-size="12" letter-spacing="0.5" fill="${LABEL}" text-anchor="middle">${label}</text>
</svg>\n`;
  fs.writeFileSync(path.join(ROOT, `assets/stack/${file}.svg`), svg);
}
console.log(`assets/stack: ${stack.length} tiles`);
