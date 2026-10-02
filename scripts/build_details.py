#!/usr/bin/env python3
"""Cut the two still details used in the README from the banner's source image.

    python3 scripts/build_details.py

assets/moon.png     close-up of the moon (static)
assets/horizon.png  the hills and water along the bottom of the scene (static)
assets/night.gif is not touched.
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
src = Image.open(ROOT / "assets/source/night.webp").convert("RGB")


def fade(img, alpha):
    """Attach an alpha mask (0..1 float array) so the crop dissolves into the page background."""
    a = Image.fromarray((np.clip(alpha, 0, 1) * 255).astype(np.uint8))
    out = img.convert("RGBA")
    out.putalpha(a)
    return out


# Moon: square crop around the disc, fading out radially beyond the glow.
moon = src.crop((1677, 62, 1887, 272))
yy, xx = np.mgrid[0:moon.height, 0:moon.width]
r = np.hypot(xx - (1782 - 1677), yy - (167 - 62))
moon = fade(moon, (104 - r) / 18)

# Horizon: hills and water along the bottom of the scene, fading out at every edge
# (strongly from the top, gently at the sides and bottom) so it reads as a horizon, not a crop.
horizon = src.crop((0, 545, 2000, 705)).resize((1000, 80), Image.BOX)
top = np.clip(np.arange(80) / 28.0, 0, 1)[:, None]
bottom = np.clip((79 - np.arange(80)) / 10.0, 0, 1)[:, None]
x = np.arange(1000)
sides = np.clip(np.minimum(x, 999 - x) / 160.0, 0, 1)[None, :]
horizon = fade(horizon, top * bottom * sides ** 1.5)

for name, img in (("moon.png", moon), ("horizon.png", horizon)):
    img.save(ROOT / "assets" / name, optimize=True)
    print(f"assets/{name}: {img.width}x{img.height}, {(ROOT / 'assets' / name).stat().st_size // 1024} KB")
