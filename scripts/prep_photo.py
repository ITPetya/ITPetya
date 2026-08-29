"""Prep a source photo for ASCII conversion: remove background, boost local
contrast, composite onto white. Run once per photo:

    python scripts/prep_photo.py source-photo.png
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove, new_session

# Lightweight, portrait-specific model (~176MB) instead of rembg's default
# general-purpose model, which needs far more memory than this machine has.
_SESSION = new_session("u2net_human_seg")


def prep(src_path: str, out_path: str = "scripts/prepped-photo.png") -> None:
    src_bytes = Path(src_path).read_bytes()
    cutout_bytes = remove(src_bytes, session=_SESSION)  # isolates the subject, transparent bg

    cutout = Image.open(__import__("io").BytesIO(cutout_bytes)).convert("RGBA")
    arr = np.array(cutout)
    rgb, alpha = arr[..., :3], arr[..., 3]

    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # Composite onto pure white using the alpha mask, so background maps to
    # the blank end of the ASCII ramp.
    white = np.full_like(gray, 255)
    alpha_f = alpha.astype(np.float32) / 255.0
    composited = (gray.astype(np.float32) * alpha_f + white.astype(np.float32) * (1 - alpha_f)).astype(np.uint8)

    Image.fromarray(composited, mode="L").save(out_path)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python scripts/prep_photo.py <source-photo>")
        sys.exit(1)
    prep(sys.argv[1])
