"""Generate animated assets for the Jenoyrex profile README.
Outputs into /home/claude/out/assets/anim/ and /home/claude/out/assets/coder.gif
"""
from pathlib import Path
from html import escape
import textwrap, random
from PIL import Image

OUT = Path(__file__).resolve().parents[1] / "assets/anim"; OUT.mkdir(parents=True, exist_ok=True)
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets"

BG, BORDER, TEXT, MUTED, ACCENT, MOON = "#0d1117", "#30363d", "#e6edf3", "#8b949e", "#8bb4ff", "#f0e6c8"
SANS = "'Segoe UI', -apple-system, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, 'SFMono-Regular', Consolas, 'Liberation Mono', monospace"
random.seed(7)

def stars(w, h, n, rmax=1.4, cls="tw"):
    out = []
    for i in range(n):
        x, y = random.uniform(4, w - 4), random.uniform(4, h - 4)
        r = random.uniform(0.5, rmax); d = random.uniform(0, 4); dur = random.uniform(2.5, 5)
        out.append(f'<circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="#fff" '
                   f'style="animation-delay:{d:.2f}s;animation-duration:{dur:.2f}s"/>')
    return "\n".join(out)

TW_CSS = ".tw{animation:tw 3s ease-in-out infinite;opacity:.2}@keyframes tw{0%,100%{opacity:.15}50%{opacity:.9}}"

# ---------------------------------------------------------------- divider
def divider():
    w, h = 900, 46
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<style>{TW_CSS}
.line{{stroke-dasharray:900;stroke-dashoffset:900;animation:draw 2.2s ease-out forwards}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}</style>
<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{ACCENT}" stop-opacity="0"/>
<stop offset=".5" stop-color="{ACCENT}" stop-opacity=".55"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></linearGradient>
<linearGradient id="tail" x1="1" x2="0"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>
<line class="line" x1="0" y1="{h/2}" x2="{w}" y2="{h/2}" stroke="url(#g)" stroke-width="1"/>
{stars(w, h, 26)}
<g opacity="0"><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.8;1" dur="5s" begin="1s" repeatCount="indefinite"/>
<g><animateTransform attributeName="transform" type="translate" from="-80 6" to="{w+20} 34" dur="5s" begin="1s" repeatCount="indefinite"/>
<rect x="-60" y="-1" width="60" height="2" fill="url(#tail)" transform="rotate(1.8)"/><circle r="2.2" fill="#fff"/></g></g>
<text x="{w/2}" y="{h/2+5}" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{MOON}">✦</text>
</svg>'''
    (OUT / "divider.svg").write_text(svg)

# ---------------------------------------------------------------- terminal intro
def terminal():
    lines = [
        ("$", "whoami"),
        ("", "jenoy rex · data science engineering student · karnataka, india"),
        ("$", "cat now.txt"),
        ("", "learning: machine learning fundamentals, distributed systems"),
        ("", "doing: building small projects to learn how real software works"),
        ("$", "ls ~/projects"),
        ("", "ctx-receipt  vigil  vaultdrop  adpo  cooperation-lab  tender-radar  pata"),
        ("$", "echo $STATUS"),
        ("", "still learning · feedback and suggestions are always welcome"),
    ]
    w, lh, top = 760, 26, 58
    h = top + lh * len(lines) + 40
    body, t = [], 0.6
    for i, (p, txt) in enumerate(lines):
        y = top + i * lh
        chars = len(txt) + (2 if p else 0)
        dur = max(0.35, chars * 0.028) if p else 0.35
        col = ACCENT if p else TEXT
        label = (f'<tspan fill="#7ee787">{p}</tspan> ' if p else "") + escape(txt)
        cid = f"c{i}"
        body.append(f'''<clipPath id="{cid}"><rect x="22" y="{y-17}" height="24" width="0">
<animate attributeName="width" from="0" to="{w-40}" begin="{t:.2f}s" dur="{dur:.2f}s" fill="freeze" calcMode="{'discrete' if not p else 'linear'}"/></rect></clipPath>
<text x="24" y="{y}" clip-path="url(#{cid})" font-family="{MONO}" font-size="14" fill="{col if p else MUTED if i in (1,) else TEXT}">{label}</text>''')
        t += dur + (0.25 if p else 0.15)
    cy = top + lh * len(lines)
    cursor = (f'<rect x="24" y="{cy-14}" width="9" height="17" fill="{ACCENT}" opacity="0">'
              f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.01;.5;.51" dur="1s" begin="{t:.2f}s" repeatCount="indefinite"/></rect>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<style>{TW_CSS}
.win{{animation:pop .7s cubic-bezier(.2,.8,.2,1) both}}@keyframes pop{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}</style>
<g class="win">
<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="12" fill="{BG}" stroke="{BORDER}"/>
<g opacity=".7">{stars(w, h, 18, 1.1)}</g>
<path d="M.5 12.5a12 12 0 0 1 12-12h{w-25}a12 12 0 0 1 12 12v20h-{w-1}z" fill="#161b22"/>
<circle cx="22" cy="17" r="6" fill="#ff5f57"/><circle cx="42" cy="17" r="6" fill="#febc2e"/><circle cx="62" cy="17" r="6" fill="#28c840"/>
<text x="{w/2}" y="22" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{MUTED}">jenoy@night: ~</text>
{''.join(body)}
{cursor}
</g></svg>'''
    (OUT / "terminal.svg").write_text(svg)

# ---------------------------------------------------------------- project cards
def card(slug, emoji, title, desc, tags, status, delay):
    w, h = 420, 196
    lines = textwrap.wrap(desc, 52)[:3]
    desc_svg = "".join(f'<text x="22" y="{86 + i*20}" font-family="{SANS}" font-size="13.5" fill="{MUTED}">{escape(l)}</text>' for i, l in enumerate(lines))
    x, tag_svg = 22, []
    for tg in tags:
        tw = len(tg) * 7 + 18
        tag_svg.append(f'<rect x="{x}" y="152" width="{tw}" height="22" rx="11" fill="#161b22" stroke="{BORDER}"/>'
                       f'<text x="{x + tw/2}" y="167" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{ACCENT}">{escape(tg)}</text>')
        x += tw + 6
    sw = len(status) * 6.6 + 22
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<style>{TW_CSS}
.card{{animation:rise .9s cubic-bezier(.2,.8,.2,1) {delay}s both}}
@keyframes rise{{from{{opacity:0;transform:translateY(18px)}}to{{opacity:1;transform:none}}}}
.sweep{{animation:sweep 6s linear {delay+1}s infinite}}@keyframes sweep{{0%{{transform:translateX(-160px)}}40%,100%{{transform:translateX({w+160}px)}}}}
.dot{{animation:pulse 2s ease-in-out infinite}}@keyframes pulse{{0%,100%{{opacity:.35}}50%{{opacity:1}}}}</style>
<defs><clipPath id="r"><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14"/></clipPath>
<linearGradient id="sh" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".06"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>
<g class="card">
<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="14" fill="{BG}" stroke="{BORDER}"/>
<g clip-path="url(#r)"><g opacity=".8">{stars(w, h, 12, 1.0)}</g>
<rect class="sweep" x="0" y="0" width="120" height="{h}" fill="url(#sh)" transform="skewX(-20)"/></g>
<text x="22" y="46" font-family="{SANS}" font-size="21" font-weight="700" fill="{TEXT}">{emoji} {escape(title)}</text>
<rect x="{w-22-sw}" y="28" width="{sw}" height="22" rx="11" fill="#0f2a1b" stroke="#238636" stroke-opacity=".6"/>
<circle class="dot" cx="{w-22-sw+11}" cy="39" r="3.5" fill="#3fb950"/>
<text x="{w-22-sw+20}" y="43.5" font-family="{MONO}" font-size="10.5" fill="#7ee787">{escape(status)}</text>
{desc_svg}
{''.join(tag_svg)}
</g></svg>'''
    (OUT / f"card-{slug}.svg").write_text(svg)

PROJECTS = [
    ("ctx-receipt", "🧾", "ctx-receipt", "A small CLI that estimates the tokens AI coding agents pre-load from rules files, skills and MCP configs.", ["TypeScript", "Node.js", "CLI"], "on npm"),
    ("vigil", "🔭", "Vigil", "A learning project on LLM observability: a Python SDK sends traces to a FastAPI API, stored in ClickHouse, viewed in Next.js.", ["Python", "FastAPI", "Next.js"], "demo"),
    ("vaultdrop", "🔐", "VaultDrop", "A file vault experiment where files are encrypted in the browser (Web Crypto, AES-GCM) before they are uploaded.", ["TypeScript", "Express", "Prisma"], "demo"),
    ("adpo", "📊", "ADPO", "Reads GitHub Actions run history and uses simple statistics to point out slow or flaky CI steps.", ["Python", "FastAPI", "React"], "demo"),
    ("cooperation-lab", "🤝", "Cooperation Lab", "A sandbox where AI agents negotiate how to split resources. College group project with two teammates.", ["Python", "SQLite"], "group project"),
    ("tender-radar", "📡", "tender-radar", "Matches EU public tenders from TED to a short business profile and publishes a daily page and RSS feed.", ["Python", "SQLite", "Actions"], "runs daily"),
    ("pata", "🗺️", "Pata", "Early-stage toolkit for working with Indian address data. Version 1 is a gazetteer built from LGD snapshots.", ["Python", "data"], "early stage"),
]

# ---------------------------------------------------------------- tech marquee
def marquee():
    items = ["Python", "TypeScript", "JavaScript", "React", "Next.js", "Tailwind", "Node.js", "Express", "FastAPI",
             "PostgreSQL", "SQLite", "ClickHouse", "Prisma", "SQLAlchemy", "Docker", "GitHub Actions", "pytest", "Vitest", "Git"]
    w, h = 900, 56
    x, pills = 0, []
    for it in items:
        pw = len(it) * 8 + 30
        pills.append(f'<rect x="{x}" y="12" width="{pw}" height="32" rx="16" fill="#161b22" stroke="{BORDER}"/>'
                     f'<text x="{x + pw/2}" y="33" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{TEXT}">{escape(it)}</text>')
        x += pw + 12
    total = x
    row = "".join(pills)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<style>.m{{animation:mv {total/40:.1f}s linear infinite}}@keyframes mv{{from{{transform:translateX(0)}}to{{transform:translateX(-{total}px)}}}}</style>
<defs><linearGradient id="f" x1="0" x2="1"><stop offset="0" stop-color="{BG}"/><stop offset=".08" stop-color="{BG}" stop-opacity="0"/>
<stop offset=".92" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>
<g class="m"><g>{row}</g><g transform="translate({total} 0)">{row}</g></g>
<rect width="{w}" height="{h}" fill="url(#f)"/>
</svg>'''
    (OUT / "stack-marquee.svg").write_text(svg)

# ---------------------------------------------------------------- footer
def footer():
    w, h = 900, 150
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<style>{TW_CSS}
.moon{{animation:float 6s ease-in-out infinite}}@keyframes float{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-6px)}}}}
.msg{{animation:fade 1.6s ease-out .4s both}}@keyframes fade{{from{{opacity:0;letter-spacing:6px}}to{{opacity:1;letter-spacing:1px}}}}</style>
<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="#111a2b"/></linearGradient>
<radialGradient id="glow"><stop offset="0" stop-color="{MOON}" stop-opacity=".35"/><stop offset="1" stop-color="{MOON}" stop-opacity="0"/></radialGradient>
<mask id="cres"><rect width="{w}" height="{h}" fill="#fff"/><circle cx="{w/2+9}" cy="40" r="17" fill="#000"/></mask></defs>
<rect width="{w}" height="{h}" fill="url(#sky)"/>
{stars(w, h-30, 40)}
<g class="moon"><circle cx="{w/2}" cy="44" r="38" fill="url(#glow)"/><circle cx="{w/2}" cy="44" r="18" fill="{MOON}" mask="url(#cres)"/></g>
<text class="msg" x="{w/2}" y="104" text-anchor="middle" font-family="{MONO}" font-size="15" fill="{TEXT}">thanks for stopping by ✦ have a good night</text>
<path d="M0 {h} L0 132 L60 122 L120 130 L190 116 L260 128 L330 118 L400 131 L470 119 L540 129 L610 115 L680 127 L750 120 L820 130 L900 121 L900 {h}Z" fill="#0a0e14"/>
</svg>'''
    (OUT / "footer.svg").write_text(svg)

# ---------------------------------------------------------------- animated coder gif
def coder_gif():
    im = Image.open(SRC / "coder.png").convert("RGBA")
    W, H = im.size
    px = im.load()
    # monitor interior: find bright "code line" pixels in the screen area
    box = (55, 30, 205, 132)
    code = [(x, y) for x in range(box[0], box[2]) for y in range(box[1], box[3])
            if sum(px[x, y][:3]) / 3 > 90 and px[x, y][3] > 0]
    rows = sorted({y for _, y in code})
    groups = []
    for y in rows:
        if groups and y - groups[-1][-1] <= 1: groups[-1].append(y)
        else: groups.append([y])
    screen_col = px[box[0] + 6, box[1] + 4]
    base = im.copy(); bp = base.load()
    for x, y in code: bp[x, y] = screen_col
    frames, durs = [], []
    def lines_frame(n_groups, partial=1.0, cursor=True):
        f = base.copy(); fp = f.load()
        last_end = None
        for gi, g in enumerate(groups[:n_groups]):
            pts = [(x, y) for x, y in code if y in g]
            if gi == n_groups - 1 and partial < 1:
                xs = sorted({x for x, _ in pts}); cut = xs[0] + int((xs[-1] - xs[0]) * partial)
                pts = [(x, y) for x, y in pts if x <= cut]
            for x, y in pts: fp[x, y] = px[x, y]
            if pts: last_end = (max(x for x, _ in pts) + 3, g[0])
        if cursor and last_end:
            cx, cy = last_end
            for dx in range(3):
                for dy in range(-1, 4):
                    if 0 <= cx + dx < W and 0 <= cy + dy < H: fp[cx + dx, cy + dy] = (139, 180, 255, 255)
        return f
    for gi in range(1, len(groups) + 1):
        for p in (0.35, 0.7, 1.0):
            frames.append(lines_frame(gi, p)); durs.append(70)
    for k in range(6):
        frames.append(lines_frame(len(groups), 1.0, cursor=(k % 2 == 0))); durs.append(420)
    def to_p(f):
        f = f.resize((W * 2, H * 2), Image.NEAREST)
        a = f.getchannel("A")
        p = f.convert("RGB").quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        pal = p.getpalette()[:765] + [0, 0, 0]
        p.putpalette(pal)
        mask = a.point(lambda v: 255 if v < 128 else 0)
        p.paste(255, mask=mask)
        p.info["transparency"] = 255
        return p
    big = [to_p(f) for f in frames]
    big[0].save(OUT.parent / "coder.gif", save_all=True, append_images=big[1:], duration=durs, loop=0, disposal=2, transparency=255)
    return len(groups)

divider(); terminal(); marquee(); footer()
for i, p in enumerate(PROJECTS):
    card(*p, delay=0.15 + (i % 2) * 0.35)
print("code line groups:", coder_gif())
