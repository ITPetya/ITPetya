"""Convert the prepped grayscale photo into a self-typing monochrome ASCII SVG.

    python scripts/make_ascii_svg.py   # writes avi-ascii.svg
"""
import os
from pathlib import Path

from PIL import Image

STATIC = os.environ.get("STATIC") == "1"

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense); leading space = blank
COLS = 100
ROWS = 53
CHAR_W = 6.2
CHAR_H = 11
FONT_SIZE = 11
FILL = "#c9d1d9"
CURSOR_FILL = "#39d353"


def image_to_grid(path: str) -> list[str]:
    img = Image.open(path).convert("L")
    img = img.resize((COLS, ROWS), Image.LANCZOS)
    pixels = list(img.getdata())
    ramp_max = len(RAMP) - 1
    rows = []
    for r in range(ROWS):
        row_chars = []
        for c in range(COLS):
            brightness = pixels[r * COLS + c]  # 0=black .. 255=white
            idx = round((255 - brightness) / 255 * ramp_max)
            row_chars.append(RAMP[idx])
        rows.append("".join(row_chars))
    return rows


def esc(ch: str) -> str:
    return {"&": "&amp;", "<": "&lt;", ">": "&gt;"}.get(ch, ch)


def build_svg(rows: list[str]) -> str:
    width = COLS * CHAR_W
    height = ROWS * CHAR_H
    row_dur = 0.045  # seconds per character within a row's wipe
    row_stagger = 0.09  # seconds between each row's start

    defs = []
    body = []

    for r, row in enumerate(rows):
        text = "".join(esc(c) for c in row)
        y = (r + 1) * CHAR_H - 2
        start = r * row_stagger
        row_len = max(len(row.rstrip()), 1)
        wipe_dur = row_len * row_dur
        clip_id = f"clip{r}"

        if STATIC:
            body.append(
                f'<text x="0" y="{y}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" '
                f'font-size="{FONT_SIZE}" fill="{FILL}" xml:space="preserve">{text}</text>'
            )
            continue

        defs.append(
            f'<clipPath id="{clip_id}">'
            f'<rect x="0" y="{r * CHAR_H}" width="0" height="{CHAR_H}">'
            f'<animate attributeName="width" from="0" to="{width}" '
            f'begin="{start:.3f}s" dur="{wipe_dur:.3f}s" fill="freeze" '
            f'calcMode="linear"/>'
            f"</rect>"
            f"</clipPath>"
        )

        body.append(
            f'<g clip-path="url(#{clip_id})">'
            f'<text x="0" y="{y}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" '
            f'font-size="{FONT_SIZE}" fill="{FILL}" xml:space="preserve">{text}</text>'
            f"</g>"
        )

        # small cursor block riding the wipe edge, fades out once the row is done
        cursor_x_expr = f"{row_len * CHAR_W:.1f}"
        body.append(
            f'<rect x="0" y="{r * CHAR_H + 1}" width="{CHAR_W:.1f}" height="{CHAR_H - 2}" '
            f'fill="{CURSOR_FILL}">'
            f'<animate attributeName="x" from="0" to="{cursor_x_expr}" '
            f'begin="{start:.3f}s" dur="{wipe_dur:.3f}s" fill="freeze" calcMode="linear"/>'
            f'<animate attributeName="opacity" from="1" to="0" '
            f'begin="{start + wipe_dur:.3f}s" dur="0.15s" fill="freeze"/>'
            f"</rect>"
        )

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" '
        f'width="{width:.0f}" height="{height:.0f}">'
        f'<rect width="100%" height="100%" fill="#0d1117"/>'
        f"<defs>{''.join(defs)}</defs>"
        f"{''.join(body)}"
        f"</svg>"
    )
    return svg


def main() -> None:
    rows = image_to_grid("scripts/prepped-photo.png")
    svg = build_svg(rows)
    Path("ascii-portrait.svg").write_text(svg, encoding="utf-8")
    print("wrote ascii-portrait.svg")


if __name__ == "__main__":
    main()
