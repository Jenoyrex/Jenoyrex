#!/usr/bin/env python3
"""Cut the still banner that closes the README from its source image.

    python3 scripts/build_details.py

assets/horizon.png  "Ave Christus Rex", from assets/source/ave-christus-rex.png (static)
assets/night.gif is not touched.
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
src = Image.open(ROOT / "assets/source/ave-christus-rex.png").convert("RGB")

W, H = 1000, 80                 # the slot's size, unchanged
SCALE = 0.64                    # output px per source px: lettering about 54 px tall
LETTERS_Y = (121, 205)          # the lettering's rows in the source


def fade(img, alpha):
    """Attach an alpha mask (0..1 float array) so the strip dissolves into the page background."""
    a = Image.fromarray((np.clip(alpha, 0, 1) * 255).round().astype(np.uint8))
    out = img.convert("RGBA")
    out.putalpha(a)
    return out


# Banner: a band through the lettering, scaled (not stretched) and centred. The source is
# narrower than the slot, so the band crossfades into its own edge tone, which carries the
# strip to full width; the strip then fades out at every edge like the horizon it replaces.
cy, bh = sum(LETTERS_Y) / 2, H / SCALE
band = src.crop((0, round(cy - bh / 2), src.width, round(cy + bh / 2)))
bw = round(src.width * SCALE)
band = np.asarray(band.resize((bw, H), Image.LANCZOS)).astype(float)
edge = np.concatenate([band[:, :8], band[:, -8:]], axis=1).mean(axis=(0, 1))
strip = np.tile(edge, (H, W, 1))
x0 = (W - bw) // 2
blend = np.clip(np.minimum(np.arange(bw), bw - 1 - np.arange(bw)) / 36.0, 0, 1)[None, :, None]
strip[:, x0:x0 + bw] = band * blend + edge * (1 - blend)

x, y = np.arange(W), np.arange(H)
sides = np.clip(np.minimum(x, W - 1 - x) / 160.0, 0, 1)[None, :] ** 1.5
vert = (np.clip(y / 14.0, 0, 1) * np.clip((H - 1 - y) / 10.0, 0, 1))[:, None]
banner = fade(Image.fromarray(strip.round().astype(np.uint8)), vert * sides)

for name, img in (("horizon.png", banner),):
    img.save(ROOT / "assets" / name, optimize=True)
    print(f"assets/{name}: {img.width}x{img.height}, {(ROOT / 'assets' / name).stat().st_size // 1024} KB")
