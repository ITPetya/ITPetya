"""Hand-authored neofetch-style info card SVG. Lines fade/slide in on a stagger.

    python scripts/make_info_card.py         # writes info-card.svg (animated)
    STATIC=1 python scripts/make_info_card.py # writes a frozen frame (local preview)
"""
import os
from pathlib import Path

STATIC = os.environ.get("STATIC") == "1"

WIDTH = 490
BG = "#0d1117"
BORDER = "#30363d"
TITLE_BG = "#161b22"
LABEL_COLOR = "#39d353"
VALUE_COLOR = "#c9d1d9"
DIM_COLOR = "#8b949e"
FONT = "ui-monospace,SFMono-Regular,Consolas,monospace"

TITLE = "itpetya@github ~ neofetch"

FIELDS = [
    ("Now", "Student & Hobby Dev"),
    ("Focus", "Full-Stack & Homelab"),
]

STACK_LINES = [
    "React/TS · Vite · Three.js · Tailwind",
    "Node · Python · C#/.NET · Postgres · GH Actions",
]

HIGHLIGHTS = [
    "Kidge — App + Social-Media-Automation",
    "Schallschutz-Konfigurator — 3D-Webkonfigurator (R3F/CSG)",
    "Pausengong — P2P-Pausenklingel (C#/WinUI3, MQTT)",
    "Abitrack — Noten- & Klausurplaner (React, Netlify, Postgres)",
    "Rack-Manager — Pi-5-Homelab mit Wartungs-Entscheidungssystem",
]

TITLE_BAR_H = 32
ROW_H = 20
STACK_ROW_H = 34
PAD_X = 18
PAD_TOP = 16
HIGHLIGHT_HEADER_H = 26


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main() -> None:
    y = TITLE_BAR_H + PAD_TOP
    rows = []
    delay = 0.0
    stagger = 0.12

    def anim_attrs(start: float) -> str:
        if STATIC:
            return ""
        return (
            f'<animate attributeName="opacity" from="0" to="1" begin="{start:.3f}s" dur="0.35s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'from="-14 0" to="0 0" begin="{start:.3f}s" dur="0.35s" fill="freeze" calcMode="spline" '
            f'keySplines="0.2 0.8 0.2 1" additive="sum"/>'
        )

    init_opacity = "1" if STATIC else "0"

    # field rows (Now / Focus)
    for label, value in FIELDS:
        rows.append(
            f'<g opacity="{init_opacity}">'
            f'<text x="{PAD_X}" y="{y}" font-family="{FONT}" font-size="13" fill="{LABEL_COLOR}" font-weight="bold">{esc(label)}</text>'
            f'<text x="{PAD_X + 70}" y="{y}" font-family="{FONT}" font-size="13" fill="{VALUE_COLOR}">{esc(value)}</text>'
            f"{anim_attrs(delay)}"
            f"</g>"
        )
        delay += stagger
        y += ROW_H

    # stack row (label once, value wraps over two lines)
    rows.append(
        f'<g opacity="{init_opacity}">'
        f'<text x="{PAD_X}" y="{y}" font-family="{FONT}" font-size="13" fill="{LABEL_COLOR}" font-weight="bold">Stack</text>'
        f'<text x="{PAD_X + 70}" y="{y}" font-family="{FONT}" font-size="10.5" fill="{VALUE_COLOR}">{esc(STACK_LINES[0])}</text>'
        f'<text x="{PAD_X + 70}" y="{y + 15}" font-family="{FONT}" font-size="10.5" fill="{VALUE_COLOR}">{esc(STACK_LINES[1])}</text>'
        f"{anim_attrs(delay)}"
        f"</g>"
    )
    delay += stagger
    y += STACK_ROW_H

    # divider
    rows.append(f'<line x1="{PAD_X}" y1="{y - 12}" x2="{WIDTH - PAD_X}" y2="{y - 12}" stroke="{BORDER}"/>')

    # highlights header
    rows.append(
        f'<g opacity="{init_opacity}">'
        f'<text x="{PAD_X}" y="{y + 6}" font-family="{FONT}" font-size="13" fill="{LABEL_COLOR}" font-weight="bold">Highlights</text>'
        f"{anim_attrs(delay)}"
        f"</g>"
    )
    delay += stagger
    y += HIGHLIGHT_HEADER_H

    for line in HIGHLIGHTS:
        rows.append(
            f'<g opacity="{init_opacity}">'
            f'<text x="{PAD_X}" y="{y}" font-family="{FONT}" font-size="11.5" fill="{DIM_COLOR}">•</text>'
            f'<text x="{PAD_X + 14}" y="{y}" font-family="{FONT}" font-size="11.5" fill="{VALUE_COLOR}">{esc(line)}</text>'
            f"{anim_attrs(delay)}"
            f"</g>"
        )
        delay += stagger
        y += ROW_H

    height = y + 14

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" '
        f'width="{WIDTH}" height="{height}">'
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="8" '
        f'fill="{BG}" stroke="{BORDER}"/>'
        f'<path d="M0.5 {TITLE_BAR_H} L0.5 8.5 Q0.5 0.5 8.5 0.5 L{WIDTH - 8.5} 0.5 '
        f'Q{WIDTH - 0.5} 0.5 {WIDTH - 0.5} 8.5 L{WIDTH - 0.5} {TITLE_BAR_H} Z" '
        f'fill="{TITLE_BG}" stroke="{BORDER}"/>'
        f'<circle cx="20" cy="{TITLE_BAR_H / 2}" r="5" fill="#ff5f56"/>'
        f'<circle cx="38" cy="{TITLE_BAR_H / 2}" r="5" fill="#ffbd2e"/>'
        f'<circle cx="56" cy="{TITLE_BAR_H / 2}" r="5" fill="#27c93f"/>'
        f'<text x="{WIDTH / 2}" y="{TITLE_BAR_H / 2 + 4}" text-anchor="middle" '
        f'font-family="{FONT}" font-size="12" fill="{DIM_COLOR}">{esc(TITLE)}</text>'
        f"{''.join(rows)}"
        f"</svg>"
    )

    Path("info-card.svg").write_text(svg, encoding="utf-8")
    print("wrote info-card.svg")


if __name__ == "__main__":
    main()
