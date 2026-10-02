#!/usr/bin/env python3
"""Render assets/activity.svg, the contribution calendar, from data/contributions.json.

    python3 scripts/generate_stats.py             # re-render from data/contributions.json
    python3 scripts/generate_stats.py --refresh   # re-fetch with `gh` (GraphQL), then re-render
"""
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA, OUT = ROOT / "data" / "contributions.json", ROOT / "assets" / "activity.svg"
LOGIN = "Jenoyrex"

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
MUTED = "#6e7681"
LEVELS = ["#1b1f24", "#373e47", "#636c76", "#9198a1", "#d1d7e0"]  # 0, 1-2, 3-5, 6-9, 10+


def refresh():
    q = ('query($login:String!){user(login:$login){contributionsCollection{contributionCalendar'
         '{totalContributions weeks{contributionDays{date contributionCount}}}}}}')
    out = subprocess.check_output(["gh", "api", "graphql", "-f", f"query={q}", "-f", f"login={LOGIN}"])
    cal = json.loads(out)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    DATA.write_text(json.dumps({
        "login": LOGIN, "source": "GitHub GraphQL API: user.contributionsCollection.contributionCalendar",
        "captured": dt.date.today().isoformat(),
        "window": {"start": days[0]["date"], "end": days[-1]["date"]},
        "total": cal["totalContributions"],
        "days": {d["date"]: d["contributionCount"] for d in days if d["contributionCount"]}}, indent=2) + "\n")


def level(n):
    return 0 if n == 0 else 1 if n <= 2 else 2 if n <= 5 else 3 if n <= 9 else 4


def render(c):
    start, end = (dt.date.fromisoformat(c["window"][k]) for k in ("start", "end"))
    first = start - dt.timedelta(days=(start.weekday() + 1) % 7)   # Sunday on or before start
    cell, gap, x0, y0 = 10, 3, 2, 22
    weeks = (end - first).days // 7 + 1
    w, h = x0 + weeks * (cell + gap), y0 + 7 * (cell + gap) + 26
    parts, last_month = [], None
    for i in range((end - first).days + 1):
        d = first + dt.timedelta(days=i)
        if d < start:
            continue
        col, row = (d - first).days // 7, (d.weekday() + 1) % 7
        x, y = x0 + col * (cell + gap), y0 + row * (cell + gap)
        n = c["days"].get(d.isoformat(), 0)
        parts.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{LEVELS[level(n)]}">'
                     f'<title>{n} contribution{"" if n == 1 else "s"} on {d.day} {d:%b %Y}</title></rect>')
        if d.day <= 7 and row == 0 and d.month != last_month:
            month = f"{d:%b}".lower()
            parts.append(f'<text x="{x}" y="{y0 - 9}" font-family="{MONO}" font-size="10" fill="{MUTED}">{month}</text>')
            last_month = d.month
    captured = dt.date.fromisoformat(c["captured"])
    caption = (f'{c["total"]} contributions · {start:%b %Y} – {end:%b %Y} · '
               f'snapshot {captured.day} {captured:%b %Y}').lower()
    parts.append(f'<text x="{x0}" y="{h - 6}" font-family="{MONO}" font-size="10.5" fill="{MUTED}">{caption}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
            f'aria-label="Contribution calendar">\n' + "\n".join(parts) + "\n</svg>\n")


def main():
    if "--refresh" in sys.argv:
        refresh()
    OUT.write_text(render(json.loads(DATA.read_text())))
    print("rendered", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
