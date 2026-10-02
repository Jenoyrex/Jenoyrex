#!/usr/bin/env python3
"""Draw assets/coder.png: a pixel-art coder at a desk at night, seen from behind.

    pip install pillow numpy
    python3 scripts/build_coder.py

Drawn on a 64x56 art-pixel grid and scaled up 4x with nearest-neighbour, in the blue-grey
tones of the banner (assets/source/night.webp). The background is transparent so the piece
sits directly on the README page; the monitor's glow is a sparse ordered dither.
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/coder.png"
W, H, SCALE = 64, 56, 4

# Banner tones, darkest to lightest.
K = [(12, 14, 18), (22, 25, 31), (34, 38, 46), (52, 57, 68), (80, 86, 98),
     (125, 127, 141), (176, 180, 192), (220, 224, 232)]
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16

rgb = np.zeros((H, W, 3), np.uint8)
alpha = np.zeros((H, W), np.uint8)


def px(x0, y0, x1, y1, k):
    """Fill the inclusive art-pixel rectangle (x0, y0)-(x1, y1) with tone k."""
    rgb[y0:y1 + 1, x0:x1 + 1] = K[k]
    alpha[y0:y1 + 1, x0:x1 + 1] = 255


# Glow: dithered halo around the screen, densest at the screen edge.
yy, xx = np.mgrid[0:H, 0:W]
dx = np.maximum(np.maximum(13 - xx, xx - 51), 0)
dy = np.maximum(np.maximum(7 - yy, yy - 33), 0)
glow = np.clip(1 - np.hypot(dx, dy) / 9, 0, 1) * 0.55
dots = (glow > BAYER[yy % 4, xx % 4]) & (yy < 40)
rgb[dots], alpha[dots] = K[2], 255

# Desk: top surface lit by the screen, darker front edge, two legs.
px(3, 40, 60, 40, 4)
px(3, 41, 60, 42, 2)
px(6, 43, 8, 55, 1)
px(55, 43, 57, 55, 1)
lit = (xx >= 12) & (xx <= 52) & (yy == 40)
rgb[lit] = K[5]

# Monitor: bezel, dark screen, stand and base.
px(13, 7, 51, 34, 3)
px(14, 8, 50, 32, 0)
px(30, 35, 34, 38, 2)
px(25, 39, 39, 39, 3)

# Code on the screen: indented lines of varying length and brightness.
lines = [(0, 14, 6), (2, 20, 5), (4, 12, 6), (4, 24, 5), (6, 9, 7), (4, 17, 5), (2, 10, 6),
         (0, 6, 5), (0, 0, 0), (0, 16, 6), (2, 22, 5), (2, 13, 7)]
for i, (indent, length, k) in enumerate(lines):
    y = 10 + i * 2
    if length:
        px(16 + indent, y, min(16 + indent + length, 48), y, k)
px(30, 32 - 2, 31, 32 - 2, 7)   # cursor

# Mug with a little steam, and a short stack of books.
px(49, 35, 52, 39, 3)
px(53, 36, 53, 37, 3)
px(49, 35, 52, 35, 4)
for x, y in ((50, 32), (51, 31), (50, 30), (51, 28)):
    px(x, y, x, y, 3)
px(6, 37, 13, 39, 2)
px(7, 35, 12, 36, 3)
px(6, 34, 11, 34, 4)

# The coder, from behind: head, hood and rounded shoulders, rim-lit by the screen.
cx = 32
body = np.zeros((H, W), bool)
for y in range(23, 37):   # head
    half = np.sqrt(max(0.0, 5.8 ** 2 - (y - 29.0) ** 2))
    body[y, int(round(cx - half)):int(round(cx + half))] = True
body[35:38, cx - 2:cx + 2] = True   # neck
for y, half in zip(range(37, 56), [6, 9, 11, 12, 13] + [13] * 14):   # shoulders and back
    body[y, cx - half:cx + half] = True
rgb[body], alpha[body] = K[1], 255
torso = body & (yy >= 37)
rgb[torso] = K[2]
edge = body & ~np.roll(body, 1, axis=0)   # topmost pixel of each column: catches the glow
edge |= body & ~np.roll(body, 1, axis=1) & (yy < 44)
edge |= body & ~np.roll(body, -1, axis=1) & (yy < 44)
rgb[edge] = K[4]
rgb[body & (yy == 23)] = K[5]
px(cx - 13, 44, cx - 13, 48, 3)   # elbows
px(cx + 12, 44, cx + 12, 48, 3)

# Chair back in front of the lower torso.
px(cx - 9, 46, cx + 8, 55, 1)
px(cx - 9, 46, cx + 8, 46, 3)
px(cx - 9, 46, cx - 9, 55, 2)
px(cx + 8, 46, cx + 8, 55, 2)

img = Image.fromarray(np.dstack([rgb, alpha]), "RGBA").resize((W * SCALE, H * SCALE), Image.NEAREST)
img.save(OUT, optimize=True)
print(f"{OUT.relative_to(ROOT)}: {img.width}x{img.height}, {OUT.stat().st_size / 1024:.1f} KB")
