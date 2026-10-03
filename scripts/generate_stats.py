#!/usr/bin/env python3
"""Render assets/activity-live.svg, a weekly contribution graph, from data/contributions.json.

    python3 scripts/generate_stats.py                  # re-render from data/contributions.json
    python3 scripts/generate_stats.py --refresh        # fetch the live calendar first (GITHUB_TOKEN or GH_TOKEN)
    python3 scripts/generate_stats.py --input FILE     # use a saved GraphQL response instead of fetching

Data: the GitHub GraphQL API, user.contributionsCollection.contributionCalendar, with no date
range, which is the rolling one-year calendar GitHub draws on the profile page. Days are summed
into Sunday-start weeks, matching the calendar's columns; the first and last weeks are partial.

Output depends only on the calendar (no run timestamp), so an unchanged calendar produces
byte-identical files and the scheduled workflow has nothing to commit.
"""
import datetime as dt
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA, OUT = ROOT / "data" / "contributions.json", ROOT / "assets" / "activity-live.svg"
LOGIN = "Jenoyrex"
SOURCE = "GitHub GraphQL API: user.contributionsCollection.contributionCalendar"

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
BG, GRID, AXIS, MUTED, INK, PEAK = "#0d1117", "#21262d", "#30363d", "#6e7681", "#c9d1d9", "#e6edf3"

QUERY = ("query($login:String!){user(login:$login){contributionsCollection{contributionCalendar"
         "{totalContributions weeks{contributionDays{date contributionCount}}}}}}")


def fetch():
    """The live contribution calendar for LOGIN, as the GraphQL API returns it."""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN is not set; refusing to render without real data")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": f"{LOGIN}-profile-activity"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def summarise(response):
    """The daily counts and window from a GraphQL response, in the shape of data/contributions.json."""
    if response.get("errors"):
        sys.exit(f"GitHub API error: {response['errors']}")
    user = (response.get("data") or {}).get("user")
    if not user:
        sys.exit(f"no user {LOGIN!r} in the GraphQL response")
    cal = user["contributionsCollection"]["contributionCalendar"]
    days = sorted((d["date"], d["contributionCount"]) for w in cal["weeks"] for d in w["contributionDays"])
    if not days:
        sys.exit("the contribution calendar came back empty; refusing to render")
    if len({d for d, _ in days}) != len(days):
        sys.exit("the contribution calendar repeats a date; refusing to render")
    total = sum(n for _, n in days)
    if total != cal["totalContributions"]:
        sys.exit(f"calendar days sum to {total} but totalContributions is {cal['totalContributions']}")
    return {"login": LOGIN, "source": SOURCE,
            "window": {"start": days[0][0], "end": days[-1][0]},
            "total": total,
            "days": {d: n for d, n in days if n}}


def weekly(c):
    """Weekly totals (weeks start on Sunday), computed from the daily counts inside the window."""
    start, end = (dt.date.fromisoformat(c["window"][k]) for k in ("start", "end"))
    first = start - dt.timedelta(days=(start.weekday() + 1) % 7)
    weeks = []
    d = first
    while d <= end:
        total = sum(c["days"].get(day.isoformat(), 0)
                    for day in (d + dt.timedelta(days=i) for i in range(7)) if start <= day <= end)
        weeks.append((d, total))
        d += dt.timedelta(days=7)
    assert sum(t for _, t in weeks) == c["total"], "weekly totals must add up to the calendar total"
    return weeks


def render(c):
    weeks = weekly(c)
    w, h = 700, 214
    left, right, top, base = 34, 14, 16, 160
    peak = max(t for _, t in weeks)
    ymax = max(10, -(-peak // 10) * 10)
    step = 10 * -(-ymax // 50)   # at most five guides, on round numbers
    ymax = -(-ymax // step) * step
    xs = [left + i * (w - left - right) / max(1, len(weeks) - 1) for i in range(len(weeks))]
    ys = [base - t / ymax * (base - top) for _, t in weeks]
    start, end = (dt.date.fromisoformat(c["window"][k]) for k in ("start", "end"))

    parts = [f'<rect width="{w}" height="{h}" rx="6" fill="{BG}"/>']
    for v in range(step, ymax + 1, step):   # recessive guides
        y = base - v / ymax * (base - top)
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{w - right}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
        parts.append(f'<text x="{left - 8}" y="{y + 4:.1f}" class="t" text-anchor="end">{v}</text>')
    parts.append(f'<line x1="{left}" y1="{base}" x2="{w - right}" y2="{base}" stroke="{AXIS}" stroke-width="1"/>')
    last_month = None
    for (d, _), x in zip(weeks, xs):
        m = (d + dt.timedelta(days=6)).month
        if m != last_month:
            if x <= w - right - 24:   # skip a label that would run off the right edge
                label = f"{d + dt.timedelta(days=6):%b}".lower()
                parts.append(f'<text x="{x:.1f}" y="{base + 20}" class="t">{label}</text>')
            last_month = m

    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    parts.append(f'<polyline class="line" points="{pts}" pathLength="1" fill="none" stroke="{INK}" stroke-width="2" '
                 'stroke-linejoin="round" stroke-linecap="round"/>')
    i = max(range(len(weeks)), key=lambda k: weeks[k][1])   # earliest week on a tie
    wk = weeks[i][0]
    if peak:
        parts.append(f'<circle class="peak" cx="{xs[i]:.1f}" cy="{ys[i]:.1f}" r="4" fill="{BG}" stroke="{PEAK}" '
                     'stroke-width="2"/>')

    footer = [f"{c['total']} contributions", f"{start:%b %Y} – {end:%b %Y}".lower()]
    if peak:
        footer.append(f"peak {peak} in the week of {wk.day} {wk:%b}".lower())
    footer.append(f"through {end.day} {end:%b %Y}".lower())
    parts.append(f'<text x="{left}" y="{h - 10}" class="t f">{" · ".join(footer)}</text>')

    label = f"Weekly GitHub contributions, {start:%B %Y} to {end:%B %Y}: {c['total']} in total"
    if peak:
        label += f", peaking at {peak} in the week of {wk.day} {wk:%B %Y}"
    # GitHub shows README SVGs as images: no script or interaction, but CSS animation plays.
    # The line draws once and the peak marker settles in after it; static where motion is reduced.
    style = (f".t{{font-family:{MONO};font-size:12px;fill:{MUTED}}}.f{{font-size:11px}}"
             ".line{stroke-dasharray:1;animation:draw 1.6s cubic-bezier(.4,0,.2,1) both}"
             ".peak{animation:fade .5s ease-out 1.4s both}"
             "@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}"
             "@keyframes fade{from{opacity:0}to{opacity:1}}"
             "@media (prefers-reduced-motion:reduce){.line,.peak{animation:none}}")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
            f'aria-label="{label}">\n<title>{label}</title>\n<style>{style}</style>\n'
            + "\n".join(parts) + "\n</svg>\n")


def main():
    args = sys.argv[1:]
    if "--input" in args:
        response = json.loads(Path(args[args.index("--input") + 1]).read_text())
        DATA.write_text(json.dumps(summarise(response), indent=2) + "\n")
    elif "--refresh" in args:
        DATA.write_text(json.dumps(summarise(fetch()), indent=2) + "\n")
    OUT.write_text(render(json.loads(DATA.read_text())))
    print("rendered", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
