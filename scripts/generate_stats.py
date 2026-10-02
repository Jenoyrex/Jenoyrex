#!/usr/bin/env python3
"""Render the profile's analytics and achievement images from the data in data/.

    python3 scripts/generate_stats.py             # re-render from data/*.json
    python3 scripts/generate_stats.py --refresh   # re-fetch data with `gh`, then re-render

--refresh needs an authenticated GitHub CLI. Achievements have no GitHub API, so
data/achievements.json is maintained by hand from https://github.com/Jenoyrex?tab=achievements.
"""
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA, OUT = ROOT / "data", ROOT / "assets"
LOGIN = "Jenoyrex"
FEATURED = ["vigil", "VaultDrop", "ADPO", "multi-agent-cooperation"]

FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
BG, PANEL, BORDER, TEXT, MUTED, CYAN, VIOLET = "#0d1117", "#161b22", "#30363d", "#e6edf3", "#8b949e", "#38bdf8", "#a78bfa"
LEVELS = ["#161b22", "#16365a", "#1f5fa8", "#5b6fd6", "#a78bfa"]  # 0, 1-2, 3-5, 6-9, 10+
LANG_COLORS = {"Python": "#3572A5", "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "CSS": "#8a63d2",
               "Shell": "#89e051", "HTML": "#e34c26", "Other": "#6e7681"}


def gh(*args):
    return json.loads(subprocess.check_output(["gh", "api", *args]))


def refresh():
    q = ('query($login:String!){user(login:$login){contributionsCollection{contributionCalendar'
         '{totalContributions weeks{contributionDays{date contributionCount}}}}}}')
    cal = gh("graphql", "-f", f"query={q}", "-f", f"login={LOGIN}")["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    all_days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    days = {d["date"]: d["contributionCount"] for d in all_days if d["contributionCount"]}
    (DATA / "contributions.json").write_text(json.dumps({
        "login": LOGIN, "source": "GitHub GraphQL API: user.contributionsCollection.contributionCalendar",
        "captured": dt.date.today().isoformat(),
        "window": {"start": all_days[0]["date"], "end": all_days[-1]["date"]},
        "total": cal["totalContributions"], "days": days}, indent=2) + "\n")
    (DATA / "languages.json").write_text(json.dumps({
        "source": "GitHub REST API: GET /repos/Jenoyrex/{repo}/languages (bytes per language)",
        "captured": dt.date.today().isoformat(),
        "repos": {r: gh(f"repos/{LOGIN}/{r}/languages") for r in FEATURED}}, indent=2) + "\n")


def fmt_date(d):
    return f"{d.day} {d:%b %Y}"


def card(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">\n'
            f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>\n{body}</svg>\n')


def level(n):
    return 0 if n == 0 else 1 if n <= 2 else 2 if n <= 5 else 3 if n <= 9 else 4


def contributions_svg(c):
    start, end = (dt.date.fromisoformat(c["window"][k]) for k in ("start", "end"))
    first = start - dt.timedelta(days=(start.weekday() + 1) % 7)  # Sunday on or before start
    cell, gap, x0, y0 = 11, 3, 44, 62
    weeks = (end - first).days // 7 + 1
    w = x0 + weeks * (cell + gap) + 20
    parts, last_month = [], None
    for i in range((end - first).days + 1):
        d = first + dt.timedelta(days=i)
        if d < start:
            continue
        col, row = (d - first).days // 7, (d.weekday() + 1) % 7
        x, y = x0 + col * (cell + gap), y0 + row * (cell + gap)
        n = c["days"].get(d.isoformat(), 0)
        parts.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2.5" fill="{LEVELS[level(n)]}">'
                     f'<title>{n} contribution{"s" if n != 1 else ""} on {fmt_date(d)}</title></rect>')
        if d.day <= 7 and row == 0 and d.month != last_month:
            parts.append(f'<text x="{x}" y="{y0 - 8}" font-family="{FONT}" font-size="11" fill="{MUTED}">{d:%b}</text>')
            last_month = d.month
    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        parts.append(f'<text x="{x0 - 8}" y="{y0 + row * (cell + gap) + 9}" font-family="{FONT}" font-size="10" '
                     f'fill="{MUTED}" text-anchor="end">{name}</text>')
    h = y0 + 7 * (cell + gap) + 40
    legend_x = w - 20 - 5 * (cell + gap) - 70
    parts.append(f'<text x="{legend_x}" y="{h - 16}" font-family="{FONT}" font-size="11" fill="{MUTED}">Less</text>')
    for i, col in enumerate(LEVELS):
        parts.append(f'<rect x="{legend_x + 32 + i * (cell + gap)}" y="{h - 26}" width="{cell}" height="{cell}" rx="2.5" fill="{col}"/>')
    parts.append(f'<text x="{legend_x + 36 + 5 * (cell + gap)}" y="{h - 16}" font-family="{FONT}" font-size="11" fill="{MUTED}">More</text>')
    parts.append(f'<text x="{x0}" y="{h - 16}" font-family="{FONT}" font-size="11" fill="{MUTED}">'
                 f'Snapshot of github.com/{c["login"]} · {fmt_date(dt.date.fromisoformat(c["captured"]))}</text>')
    head = (f'<text x="{x0}" y="32" font-family="{FONT}" font-size="15" font-weight="600" fill="{TEXT}">'
            f'{c["total"]} contributions <tspan fill="{MUTED}" font-weight="400">· {start:%b %Y} – {end:%b %Y}</tspan></text>')
    return card(w, h, head + "\n" + "\n".join(parts) + "\n")


def summary_svg(c):
    days = {dt.date.fromisoformat(k): v for k, v in c["days"].items() if v}
    best, run, run_start, best_span = 0, 0, None, None
    for d in sorted(days):
        if run and d - dt.timedelta(days=1) in days:
            run += 1
        else:
            run, run_start = 1, d
        if run > best:
            best, best_span = run, (run_start, d)
    peak = max(days, key=lambda d: (days[d], d))
    stats = [
        (str(c["total"]), "contributions", "last 12 months"),
        (str(len(days)), "active days", "with ≥1 contribution"),
        (str(best), "days in longest streak", f"{best_span[0].day} {best_span[0]:%b} – {fmt_date(best_span[1])}"),
        (str(days[peak]), "on busiest day", fmt_date(peak)),
    ]
    w, h = 420, 210
    out = [f'<text x="24" y="36" font-family="{FONT}" font-size="15" font-weight="600" fill="{CYAN}">Contribution summary</text>']
    for i, (num, label, sub) in enumerate(stats):
        x, y = 24 + (i % 2) * 196, 84 + (i // 2) * 62
        out.append(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="26" font-weight="700" fill="{TEXT}">{num}'
                   f'<tspan font-size="13" font-weight="400" fill="{MUTED}" dx="6">{label}</tspan></text>')
        out.append(f'<text x="{x}" y="{y + 20}" font-family="{FONT}" font-size="11" fill="{MUTED}">{sub}</text>')
    out.append(f'<text x="24" y="{h - 14}" font-family="{FONT}" font-size="10.5" fill="#6e7681">'
               f'Snapshot · {fmt_date(dt.date.fromisoformat(c["captured"]))}</text>')
    return card(w, h, "\n".join(out) + "\n")


def languages_svg(l):
    totals = {}
    for repo in l["repos"].values():
        for lang, n in repo.items():
            totals[lang] = totals.get(lang, 0) + n
    ranked = sorted(totals.items(), key=lambda kv: -kv[1])
    top = ranked[:5]
    other = sum(n for _, n in ranked[5:])
    if other:
        top.append(("Other", other))
    total = sum(n for _, n in top)
    w, h = 420, 210
    out = [f'<text x="24" y="36" font-family="{FONT}" font-size="15" font-weight="600" fill="{CYAN}">Languages '
           f'<tspan fill="{MUTED}" font-weight="400" font-size="12">· featured repositories</tspan></text>',
           f'<clipPath id="bar"><rect x="24" y="54" width="{w - 48}" height="10" rx="5"/></clipPath><g clip-path="url(#bar)">']
    x = 24.0
    for lang, n in top:
        seg = (w - 48) * n / total
        out.append(f'<rect x="{x:.2f}" y="54" width="{seg + 0.5:.2f}" height="10" fill="{LANG_COLORS.get(lang, LANG_COLORS["Other"])}"/>')
        x += seg
    out.append("</g>")
    for i, (lang, n) in enumerate(top):
        cx, cy = 24 + (i % 2) * 196, 94 + (i // 2) * 26
        out.append(f'<circle cx="{cx + 5}" cy="{cy - 4}" r="5" fill="{LANG_COLORS.get(lang, LANG_COLORS["Other"])}"/>')
        out.append(f'<text x="{cx + 18}" y="{cy}" font-family="{FONT}" font-size="13" fill="{TEXT}">{lang} '
                   f'<tspan fill="{MUTED}">{100 * n / total:.1f}%</tspan></text>')
    out.append(f'<text x="24" y="{h - 14}" font-family="{FONT}" font-size="10.5" fill="#6e7681">'
               f'GitHub language bytes · {", ".join(l["repos"])}</text>')
    return card(w, h, "\n".join(out) + "\n")


SHARK = ("M14 40 C24 38 34 30 40 14 C42 24 44 32 52 40 Z")  # stylised fin over a wave line


def achievement_svg(a, captured):
    w, h = 360, 96
    out = [f'<circle cx="48" cy="48" r="30" fill="{PANEL}" stroke="{VIOLET}" stroke-width="2"/>',
           f'<g transform="translate(22 22)"><path d="{SHARK}" fill="{CYAN}"/>'
           f'<path d="M8 44 Q16 39 24 44 T40 44 T56 44" fill="none" stroke="{VIOLET}" stroke-width="2.5" stroke-linecap="round"/></g>',
           f'<rect x="60" y="62" width="30" height="20" rx="10" fill="{VIOLET}"/>',
           f'<text x="75" y="76.5" font-family="{FONT}" font-size="12" font-weight="700" fill="{BG}" text-anchor="middle">'
           f'{a["tier"].replace("x", "×")}</text>',
           f'<text x="100" y="42" font-family="{FONT}" font-size="17" font-weight="600" fill="{TEXT}">{a["name"]}</text>',
           f'<text x="100" y="62" font-family="{FONT}" font-size="12" fill="{MUTED}">{a["description"]}</text>',
           f'<text x="100" y="80" font-family="{FONT}" font-size="10.5" fill="#6e7681">From github.com/{LOGIN} · {captured}</text>']
    return card(w, h, "\n".join(out) + "\n")


def main():
    if "--refresh" in sys.argv:
        refresh()
    c = json.loads((DATA / "contributions.json").read_text())
    l = json.loads((DATA / "languages.json").read_text())
    a = json.loads((DATA / "achievements.json").read_text())
    (OUT / "stats").mkdir(parents=True, exist_ok=True)
    (OUT / "achievements").mkdir(parents=True, exist_ok=True)
    (OUT / "stats" / "contributions.svg").write_text(contributions_svg(c))
    (OUT / "stats" / "summary.svg").write_text(summary_svg(c))
    (OUT / "stats" / "languages.svg").write_text(languages_svg(l))
    captured = fmt_date(dt.date.fromisoformat(a["captured"]))
    for item in a["achievements"]:
        slug = item["name"].lower().replace(" ", "-")
        (OUT / "achievements" / f"{slug}.svg").write_text(achievement_svg(item, captured))
    print("rendered:", ", ".join(str(p.relative_to(ROOT)) for p in sorted((OUT / "stats").glob("*.svg"))
                                  + sorted((OUT / "achievements").glob("*.svg"))))


if __name__ == "__main__":
    main()
