"""Scrape the public contribution calendar HTML fragment (no token needed) and
write data/contributions.json with raw days plus derived stats.

    python scripts/fetch_contributions.py
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "ITPetya"
URL = f"https://github.com/users/{USERNAME}/contributions"


def fetch_days() -> list[dict]:
    resp = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    cells = soup.select("td.ContributionCalendar-day")
    days = []
    if cells:
        for td in cells:
            d = td.get("data-date")
            level = td.get("data-level")
            count_attr = td.get("data-count")
            if not d:
                continue
            if count_attr is not None:
                count = int(count_attr)
            else:
                tt_id = td.get("id")
                count = 0
                if tt_id:
                    tt = soup.select_one(f'tool-tip[for="{tt_id}"]')
                    if tt:
                        txt = tt.get_text(strip=True)
                        digits = "".join(ch for ch in txt.split(" ")[0] if ch.isdigit())
                        count = int(digits) if digits else 0
            days.append({"date": d, "count": count, "level": int(level) if level is not None else None})
    else:
        # fallback: older markup uses <rect> with data-date/data-count
        for rect in soup.select("rect[data-date]"):
            days.append(
                {
                    "date": rect.get("data-date"),
                    "count": int(rect.get("data-count", 0)),
                    "level": int(rect.get("data-level")) if rect.get("data-level") else None,
                }
            )

    days.sort(key=lambda d: d["date"])
    return days


def derive_stats(days: list[dict]) -> dict:
    total = sum(d["count"] for d in days)

    # current streak (from most recent day backwards, allow today=0 to not break it)
    current_streak = 0
    for d in reversed(days):
        if d["count"] > 0:
            current_streak += 1
        else:
            if d["date"] == days[-1]["date"]:
                continue  # today might just not have contributions yet
            break

    longest_streak = 0
    running = 0
    for d in days:
        if d["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    best_day = max(days, key=lambda d: d["count"]) if days else None

    monthly: dict[str, int] = {}
    for d in days:
        month = d["date"][:7]
        monthly[month] = monthly.get(month, 0) + d["count"]

    return {
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly": monthly,
    }


def main() -> None:
    days = fetch_days()
    if not days:
        raise SystemExit("no contribution days parsed — GitHub markup may have changed")

    stats = derive_stats(days)
    out = {
        "username": USERNAME,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "days": days,
        "stats": stats,
    }
    Path("data").mkdir(exist_ok=True)
    Path("data/contributions.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"wrote data/contributions.json ({len(days)} days, {stats['total']} contributions)")


if __name__ == "__main__":
    main()
