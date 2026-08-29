"""Render data/contributions.json as an animated 53-week x 7-day heatmap SVG.

    python scripts/render_heatmap_svg.py   # writes contrib-heatmap.svg
"""
import json
import os
from collections import defaultdict
from datetime import date
from pathlib import Path

STATIC = os.environ.get("STATIC") == "1"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CELL = 12
GAP = 3
LEFT_PAD = 34
TOP_PAD = 34
BOTTOM_PAD = 30
RIGHT_PAD = 16

MONTH_NAMES = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]


def load_data() -> dict:
    return json.loads(Path("data/contributions.json").read_text(encoding="utf-8"))


def build_weeks(days: list[dict]) -> list[list[dict | None]]:
    by_date = {d["date"]: d for d in days}
    ordered = sorted(by_date.values(), key=lambda d: d["date"])
    if not ordered:
        return []

    first = date.fromisoformat(ordered[0]["date"])
    last = date.fromisoformat(ordered[-1]["date"])

    # pad to start on a Sunday like GitHub's own calendar
    start = first
    while start.weekday() != 6:  # Monday=0 ... Sunday=6
        start = start.fromordinal(start.toordinal() - 1)

    weeks: list[list[dict | None]] = []
    cur = start
    week: list[dict | None] = []
    while cur <= last:
        key = cur.isoformat()
        week.append(by_date.get(key))
        if len(week) == 7:
            weeks.append(week)
            week = []
        cur = cur.fromordinal(cur.toordinal() + 1)
    if week:
        while len(week) < 7:
            week.append(None)
        weeks.append(week)
    return weeks


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main() -> None:
    data = load_data()
    weeks = build_weeks(data["days"])
    stats = data["stats"]

    n_weeks = len(weeks)
    width = LEFT_PAD + n_weeks * (CELL + GAP) + RIGHT_PAD
    grid_height = 7 * (CELL + GAP) - GAP
    height = TOP_PAD + grid_height + BOTTOM_PAD + 34  # +legend/footer band

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}">'
    )
    parts.append(f'<rect width="100%" height="100%" fill="#0d1117"/>')

    style = "" if STATIC else (
        "<style>"
        "@keyframes revealCell{from{opacity:0;transform:translate(-6px,-6px)}to{opacity:1;transform:translate(0,0)}}"
        ".cell{animation:revealCell .28s ease-out both}"
        "</style>"
    )
    parts.append(style)

    # month labels: mark the first week column that starts a new month
    seen_months = set()
    for wi, week in enumerate(weeks):
        for day in week:
            if day is None:
                continue
            d = date.fromisoformat(day["date"])
            if d.day <= 7:
                key = (d.year, d.month)
                if key not in seen_months:
                    seen_months.add(key)
                    x = LEFT_PAD + wi * (CELL + GAP)
                    parts.append(
                        f'<text x="{x}" y="{TOP_PAD - 10}" font-family="ui-monospace,Consolas,monospace" '
                        f'font-size="10" fill="#8b949e">{MONTH_NAMES[d.month - 1]}</text>'
                    )
            break

    # day-of-week labels (row index 0=Sunday .. 6=Saturday to match week layout)
    row_label_index = {1: "Mo", 3: "Mi", 5: "Fr"}
    for row, label in row_label_index.items():
        y = TOP_PAD + row * (CELL + GAP) + CELL - 2
        parts.append(
            f'<text x="0" y="{y}" font-family="ui-monospace,Consolas,monospace" '
            f'font-size="9" fill="#8b949e">{label}</text>'
        )

    delay_step = 0.006
    for wi, week in enumerate(weeks):
        for di, day in enumerate(week):
            x = LEFT_PAD + wi * (CELL + GAP)
            y = TOP_PAD + di * (CELL + GAP)
            if day is None:
                continue
            level = day.get("level")
            if level is None:
                level = 0 if day["count"] == 0 else min(4, 1 + day["count"] // 3)
            level = max(0, min(level, len(PALETTE) - 1))
            color = PALETTE[level]
            delay = (wi + di * 0.15) * delay_step * 6
            anim = "" if STATIC else f' style="animation-delay:{delay:.3f}s" class="cell"'
            title = f'{day["count"]} Beiträge am {day["date"]}'
            parts.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{color}"{anim}>'
                f'<title>{esc(title)}</title></rect>'
            )

    # legend
    legend_y = TOP_PAD + grid_height + 22
    parts.append(
        f'<text x="{LEFT_PAD}" y="{legend_y}" font-family="ui-monospace,Consolas,monospace" '
        f'font-size="10" fill="#8b949e">Less</text>'
    )
    lx = LEFT_PAD + 34
    for level, color in enumerate(PALETTE):
        parts.append(f'<rect x="{lx}" y="{legend_y - 9}" width="{CELL}" height="{CELL}" rx="2.5" fill="{color}"/>')
        lx += CELL + GAP
    parts.append(
        f'<text x="{lx + 4}" y="{legend_y}" font-family="ui-monospace,Consolas,monospace" '
        f'font-size="10" fill="#8b949e">More</text>'
    )

    footer = (
        f'{stats["total"]} Beiträge im letzten Jahr · '
        f'aktueller Streak {stats["current_streak"]} Tage · '
        f'längster Streak {stats["longest_streak"]} Tage'
    )
    parts.append(
        f'<text x="{width - RIGHT_PAD}" y="{legend_y}" text-anchor="end" '
        f'font-family="ui-monospace,Consolas,monospace" font-size="10" fill="#8b949e">{esc(footer)}</text>'
    )

    parts.append("</svg>")
    Path("contrib-heatmap.svg").write_text("".join(parts), encoding="utf-8")
    print("wrote contrib-heatmap.svg")


if __name__ == "__main__":
    main()
