#!/usr/bin/env python3
"""Render assets/activity.svg, a weekly contribution graph, from data/contributions.json.

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


def weekly(c):
    """Weekly totals (weeks start on Sunday), computed from the verified daily counts."""
    start, end = (dt.date.fromisoformat(c["window"][k]) for k in ("start", "end"))
    first = start - dt.timedelta(days=(start.weekday() + 1) % 7)
    weeks = []
    d = first
    while d <= end:
        total = sum(c["days"].get((d + dt.timedelta(days=i)).isoformat(), 0) for i in range(7))
        weeks.append((d, total))
        d += dt.timedelta(days=7)
    assert sum(t for _, t in weeks) == c["total"], "weekly totals must add up to the verified total"
    return weeks


def render(c):
    weeks = weekly(c)
    w, h = 700, 190
    left, right, top, base = 34, 14, 16, 160
    peak = max(t for _, t in weeks)
    ymax = max(10, -(-peak // 10) * 10)
    xs = [left + i * (w - left - right) / (len(weeks) - 1) for i in range(len(weeks))]
    ys = [base - t / ymax * (base - top) for _, t in weeks]
    parts = []
    for v in range(10, ymax + 1, 10):   # recessive guides
        y = base - v / ymax * (base - top)
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{w - right}" y2="{y:.1f}" stroke="#21262d" stroke-width="1"/>')
        parts.append(f'<text x="{left - 8}" y="{y + 4:.1f}" font-family="{MONO}" font-size="12" fill="{MUTED}" '
                     f'text-anchor="end">{v}</text>')
    parts.append(f'<line x1="{left}" y1="{base}" x2="{w - right}" y2="{base}" stroke="#30363d" stroke-width="1"/>')
    last_month = None
    for (d, _), x in zip(weeks, xs):
        m = (d + dt.timedelta(days=6)).month
        if m != last_month:
            if x <= w - right - 24:   # skip a label that would run off the right edge
                parts.append(f'<text x="{x:.1f}" y="{base + 20}" font-family="{MONO}" font-size="12" fill="{MUTED}">'
                             f'{(d + dt.timedelta(days=6)):%b}'.lower() + '</text>')
            last_month = m
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    parts.append(f'<polyline points="{pts}" fill="none" stroke="#c9d1d9" stroke-width="2" stroke-linejoin="round" '
                 f'stroke-linecap="round"/>')
    i = max(range(len(weeks)), key=lambda k: weeks[k][1])
    wk = weeks[i][0]
    parts.append(f'<circle cx="{xs[i]:.1f}" cy="{ys[i]:.1f}" r="4" fill="#0d1117" stroke="#e6edf3" stroke-width="2"/>')
    start, end = (dt.date.fromisoformat(c["window"][k]) for k in ("start", "end"))
    captured = dt.date.fromisoformat(c["captured"])
    print(f"README caption: weekly contributions · {c['total']} total · {start:%b %Y} – {end:%b %Y} · "
          f"peak {weeks[i][1]} in the week of {wk.day} {wk:%b} · snapshot {captured.day} {captured:%b %Y}".lower())
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
            f'aria-label="Weekly contributions, {start:%B %Y} to {end:%B %Y}: {c["total"]} in total">\n'
            + "\n".join(parts) + "\n</svg>\n")


def main():
    if "--refresh" in sys.argv:
        refresh()
    OUT.write_text(render(json.loads(DATA.read_text())))
    print("rendered", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
