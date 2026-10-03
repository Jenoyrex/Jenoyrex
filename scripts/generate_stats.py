#!/usr/bin/env python3
"""Render assets/activity.svg, a weekly contribution graph, from GitHub's contribution calendar.

    python3 scripts/generate_stats.py                 # re-render from data/contributions.json
    python3 scripts/generate_stats.py --refresh       # fetch the live calendar first (needs GITHUB_TOKEN)
    python3 scripts/generate_stats.py --input FILE    # use a saved GraphQL response instead of fetching

Data source: the GitHub GraphQL API, user.contributionsCollection.contributionCalendar, the
same calendar GitHub draws on the profile page for the last year. It counts what GitHub counts
as a contribution: commits to a repository's default branch, issues and pull requests opened,
pull request reviews, and repositories created (plus anonymised private contributions only if
the profile opts in). Days are summed into Sunday-start weeks, matching the calendar's columns.

The calendar covers the last year day by day (365 days), so it spans 53 Sunday-start weeks:
the first and last are partial (e.g. 3 Oct 2025 to 2 Oct 2026 is a 2-day week labelled by
Sunday 28 Sep 2025, 51 full weeks, and a 6-day week from Sunday 27 Sep 2026). A week is keyed
by its Sunday; only days inside the window are counted.

The script writes only:
  data/contributions.json   weekly totals, keyed by each week's Sunday
  assets/activity.svg       the graph
  README.md                 the image and caption between the activity markers
Nothing in these files depends on the time of the run, so an unchanged calendar produces
byte-identical output and the scheduled workflow has nothing to commit.
"""
import datetime as dt
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA, OUT, README = ROOT / "data/contributions.json", ROOT / "assets/activity.svg", ROOT / "README.md"
LOGIN = "Jenoyrex"
SOURCE = "GitHub GraphQL API: user.contributionsCollection.contributionCalendar"
MARKERS = ("<!-- activity:start -->", "<!-- activity:end -->")

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
MUTED, INK, GRID, BASE, BG = "#6e7681", "#c9d1d9", "#21262d", "#30363d", "#0d1117"

QUERY = """query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
    }
  }
}"""


def fetch():
    """The live contribution calendar for LOGIN, as GitHub's GraphQL API returns it."""
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
    """Weekly totals from a GraphQL response, keyed by the Sunday that starts each week."""
    if response.get("errors"):
        sys.exit(f"GitHub API error: {response['errors']}")
    cal = response["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = {}
    for week in cal["weeks"]:
        for day in week["contributionDays"]:
            d = dt.date.fromisoformat(day["date"])
            sunday = d - dt.timedelta(days=(d.weekday() + 1) % 7)
            weeks[sunday] = weeks.get(sunday, 0) + day["contributionCount"]
    if not weeks:
        sys.exit("the contribution calendar came back empty; refusing to render")
    total = sum(weeks.values())
    if total != cal["totalContributions"]:
        print(f"note: calendar days sum to {total}, totalContributions is {cal['totalContributions']}; "
              "the graph and caption use the day sums", file=sys.stderr)
    return {"login": LOGIN, "source": SOURCE, "week_start": "sunday",
            "note": "keys are the Sunday starting each week; the first and last weeks are partial, "
                    "since the calendar covers the last year day by day",
            "total": total,
            "weeks": {k.isoformat(): weeks[k] for k in sorted(weeks)}}


def nice_max(peak):
    """Axis top and grid step: a round step giving at most five gridlines, top at least 10."""
    for step in (2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000):
        top = max(10, -(-peak // step) * step)
        if top // step <= 5:
            return top, step
    return -(-peak // 1000) * 1000, 1000


def render(c):
    weeks = [(dt.date.fromisoformat(k), n) for k, n in c["weeks"].items()]
    w, h = 700, 190
    left, right, top, base = 34, 14, 16, 160
    peak = max(n for _, n in weeks)
    ymax, step = nice_max(peak)
    xs = [left + i * (w - left - right) / max(1, len(weeks) - 1) for i in range(len(weeks))]
    ys = [base - n / ymax * (base - top) for _, n in weeks]

    parts = []
    for v in range(step, ymax + 1, step):   # recessive guides
        y = base - v / ymax * (base - top)
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{w - right}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
        parts.append(f'<text x="{left - 8}" y="{y + 4:.1f}" class="t" text-anchor="end">{v}</text>')
    parts.append(f'<line x1="{left}" y1="{base}" x2="{w - right}" y2="{base}" stroke="{BASE}" stroke-width="1"/>')
    last_month = None
    for (d, _), x in zip(weeks, xs):
        m = (d + dt.timedelta(days=6)).month
        if m != last_month:
            if x <= w - right - 24:   # skip a label that would run off the right edge
                parts.append(f'<text x="{x:.1f}" y="{base + 20}" class="t">{(d + dt.timedelta(days=6)):%b}'.lower()
                             + '</text>')
            last_month = m

    path = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    parts.append(f'<path class="line" d="{path}" pathLength="1" fill="none" stroke="{INK}" stroke-width="2" '
                 'stroke-linejoin="round" stroke-linecap="round"/>')
    if peak:
        i = max(range(len(weeks)), key=lambda k: weeks[k][1])
        parts.append(f'<circle class="peak" cx="{xs[i]:.1f}" cy="{ys[i]:.1f}" r="4" fill="{BG}" stroke="#e6edf3" '
                     'stroke-width="2"/>')
    parts.append(f'<circle class="now" cx="{xs[-1]:.1f}" cy="{ys[-1]:.1f}" r="2.5" fill="{INK}"/>')

    # CSS animation is the only motion GitHub renders in a README image (no script, no hover):
    # the line draws once, the peak marker settles in after it, and the current week's point
    # breathes slowly. Without animation support the graph is simply static in its final state;
    # the reduced-motion rule applies wherever the browser passes that preference into images.
    style = (f".t{{font-family:{MONO};font-size:12px;fill:{MUTED}}}"
             ".line{stroke-dasharray:1;animation:draw 1.8s cubic-bezier(.4,0,.2,1) both}"
             ".peak{animation:fade .5s ease-out 1.5s both}"
             ".now{animation:fade .4s ease-out 1.7s both,breathe 3.2s ease-in-out 2.1s infinite}"
             "@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}"
             "@keyframes fade{from{opacity:0}to{opacity:1}}"
             "@keyframes breathe{0%,100%{opacity:1}50%{opacity:.3}}"
             "@media (prefers-reduced-motion:reduce){.line,.peak,.now{animation:none}}")
    label = alt(c)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
            f'aria-label="{label}">\n<title>{label}</title>\n<style>{style}</style>\n'
            + "\n".join(parts) + "\n</svg>\n")


def span(c):
    """First and last week (their Sundays) and the peak week; months are read from week ends, as on the axis."""
    keys = list(c["weeks"])
    first, last = dt.date.fromisoformat(keys[0]), dt.date.fromisoformat(keys[-1])
    peak = max(keys, key=lambda k: c["weeks"][k])
    return first + dt.timedelta(days=6), last, dt.date.fromisoformat(peak), c["weeks"][peak]


def alt(c):
    start, last, peak, n = span(c)
    end = last + dt.timedelta(days=6)
    text = f"Weekly GitHub contributions, {start:%B %Y} to {end:%B %Y}: {c['total']} in total"
    if n:
        text += f", peaking at {n} in the week of {peak.day} {peak:%B %Y}"
    return text


def caption(c):
    start, last, peak, n = span(c)
    # "In the last year" is GitHub's own wording for this calendar; the latest week is still
    # in progress when it is drawn, so it is described by its start, not as complete.
    parts = ["weekly contributions",
             f"{c['total']} in the last year ({start:%b %Y} – {last + dt.timedelta(days=6):%b %Y})"]
    if n:
        parts.append(f"peak {n} in the week of {peak.day} {peak:%b}")
    parts.append(f"latest week from {last.day} {last:%b %Y}")
    return " · ".join(parts).lower()


def update_readme(c):
    text = README.read_text()
    start, end = MARKERS
    # The end marker closes the caption line itself, so the line that follows it in the README
    # (the achievement note) stays in the same paragraph, exactly as before.
    if text.count(start) != 1 or text.count(end) != 1:
        sys.exit(f"README.md must contain exactly one {start} … {end} block")
    block = (f'{start}\n<img src="./assets/activity.svg" width="100%" alt="{alt(c)}" />\n\n'
             f"<sub>{caption(c)}</sub>{end}")
    README.write_text(re.sub(re.escape(start) + r".*?" + re.escape(end), lambda _: block, text, flags=re.S))


def main():
    args = sys.argv[1:]
    if "--refresh" in args or "--input" in args:
        response = (json.loads(Path(args[args.index("--input") + 1]).read_text()) if "--input" in args
                    else fetch())
        DATA.write_text(json.dumps(summarise(response), indent=2) + "\n")
    c = json.loads(DATA.read_text())
    OUT.write_text(render(c))
    update_readme(c)
    print(f"{c['total']} contributions over {len(c['weeks'])} weeks; caption: {caption(c)}")


if __name__ == "__main__":
    main()
