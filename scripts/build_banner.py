#!/usr/bin/env python3
"""Animate assets/source/night.webp into assets/night.gif: the clouds drift, nothing else moves.

    pip install pillow numpy scipy   # and ffmpeg on PATH
    python3 scripts/build_banner.py

The picture is split into three layers:
  * a static sky (stars, moon, sky gradient) with the clouds removed,
  * the clouds, as colour + opacity,
  * the static mountains and water, drawn last so clouds pass behind them.
The cloud layer is snapped to the image's pixel-art grid, reduced to a few tones, and
slid one art pixel per frame with wrap-around, so the loop is seamless.
"""
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "assets/source/night.webp", ROOT / "assets/night.gif"
OUT_W = 750          # source art pixels are ~8 px at 2000 px wide -> exactly 3 px here
ART_PX = 3           # output pixels per art pixel; clouds move one art pixel per frame
FPS = 5              # 15 px/s: one full drift across the banner every 50 s
OPACITY_LEVELS = 6
CLOUD_TONES = 7
PALETTE = 32
EDGE_FADE = 45      # px over which clouds fade out at the banner's left and right edges
MIN_CLOUD_ALPHA = 0.15


def layers():
    src = np.asarray(Image.open(SRC).convert("RGB")).astype(np.float32)
    H, W, _ = src.shape
    lum = src.mean(2)
    yy = np.arange(H)[:, None]

    # Foreground: the mountain line (9+ consecutive very dark rows) and everything below y=540.
    dark = (lum < 16) & (yy >= 430)
    run = ndi.uniform_filter1d(dark.astype(np.float32), 9, axis=0, origin=-4) > 0.99
    first = np.where(run.any(0), run.argmax(0), H)
    first = np.minimum(ndi.median_filter(first, 25, mode="nearest"), 540)
    fg = yy >= first[None, :]

    # Sky brightness per row and 100-px block, from pixels that are not cloud-bright.
    sky = ~fg & (lum < np.percentile(lum[~fg], 70))
    bg = np.zeros_like(lum)
    for y in range(H):
        cs, vs = [], []
        for x0 in range(0, W, 100):
            sel = sky[y, x0:x0 + 100]
            if sel.sum() > 10:
                cs.append(x0 + 50)
                vs.append(np.median(lum[y, x0:x0 + 100][sel]))
        bg[y] = np.interp(np.arange(W), cs, vs) if cs else np.median(lum[y])
    bg = ndi.uniform_filter(bg, (15, 1))

    # Stars (small, bright, compact) and the moon stay put.
    labels, n = ndi.label((lum - bg > 6) & ~fg)
    sizes = ndi.sum(np.ones_like(lum), labels, range(1, n + 1))
    peaks = ndi.maximum(lum, labels, range(1, n + 1))
    boxes = ndi.find_objects(labels)

    def compact(i):
        h, w = boxes[i][0].stop - boxes[i][0].start, boxes[i][1].stop - boxes[i][1].start
        return max(h, w) <= 3 * min(h, w)

    stars = np.isin(labels, [i + 1 for i in range(n) if sizes[i] < 700 and peaks[i] > 80 and compact(i)])
    ys, xs = np.mgrid[0:H, 0:W]
    static = ndi.binary_dilation(stars, iterations=3) | ((xs - 1782) ** 2 + (ys - 167) ** 2 < 112 ** 2)

    # Cloud opacity = how far a pixel rises above the sky; keep only regions that get properly opaque.
    alpha = np.clip((lum - bg - 2.5) / 60.0, 0, 1)
    alpha[fg | static] = 0
    alpha = ndi.binary_opening(alpha > 0, iterations=1) * alpha
    reg, m = ndi.label(alpha > 0)
    peak = ndi.maximum(alpha, reg, range(1, m + 1))
    alpha = np.where(np.isin(reg, [i + 1 for i in range(m) if peak[i] >= 0.2]), alpha, 0)
    # Only cloud bodies move: pixels at least MIN_CLOUD_ALPHA opaque plus a thin soft edge.
    # Fainter haze (e.g. the mist along the horizon) stays in the static sky, untouched.
    alpha = np.where(ndi.binary_dilation(alpha >= MIN_CLOUD_ALPHA, iterations=3), alpha, 0)

    clear = ~fg & (alpha == 0) & ~static
    tint = (src[clear] - lum[clear][:, None]).mean(0)
    sky_rgb = bg[..., None] + tint
    clean = np.where((alpha > 0)[..., None], sky_rgb, src)            # sky with the clouds lifted out
    premult = np.where((alpha > 0)[..., None], src - sky_rgb * (1 - alpha[..., None]), 0)
    return src, clean, alpha, premult, fg, tint


def resize(x, w):
    h = round(x.shape[0] * w / x.shape[1])
    chans = [x] if x.ndim == 2 else [x[..., c] for c in range(x.shape[2])]
    out = [np.asarray(Image.fromarray(c.astype(np.float32)).resize((w, h), Image.BOX)) for c in chans]
    return out[0] if x.ndim == 2 else np.stack(out, -1)


def snap(x, b):
    h, w = x.shape[:2]
    hh, ww = h // b * b, w // b * b
    y = x[:hh, :ww].reshape(hh // b, b, ww // b, b, *x.shape[2:]).mean((1, 3))
    out = x.copy()
    out[:hh, :ww] = np.repeat(np.repeat(y, b, 0), b, 1)
    return out


def cloud_layers():
    """Output-resolution layers: static background, static foreground mask, moving cloud layer."""
    src, clean, alpha, premult, fg, tint = layers()
    src, clean, premult = (resize(v, OUT_W) for v in (src, clean, premult))
    alpha, fg = resize(alpha, OUT_W), resize(fg.astype(np.float32), OUT_W) > 0.5
    # Fade the cloud layer out at the left and right edges: wisps cut off by the original frame
    # would otherwise meet as a hard vertical seam when they wrap around.
    x = np.arange(OUT_W)
    taper = np.clip(np.minimum(x, OUT_W - 1 - x) / EDGE_FADE, 0, 1)
    taper = taper * taper * (3 - 2 * taper)
    alpha, premult = alpha * taper, premult * taper[:, None]
    alpha, premult = snap(alpha, ART_PX), snap(premult, ART_PX)

    # Posterise the clouds: a few opacity steps, and tones taken from the clouds' own colours.
    colour = np.where(alpha > 0.02, (premult / np.maximum(alpha[..., None], 1e-3)).mean(2), 0)
    weights = alpha[alpha > 0.02]
    order = np.argsort(colour[alpha > 0.02])
    cdf = np.cumsum(weights[order]) / weights.sum()
    tones = np.interp((np.arange(CLOUD_TONES) + 0.5) / CLOUD_TONES, cdf, colour[alpha > 0.02][order])
    alpha = np.round(alpha * (OPACITY_LEVELS - 1)) / (OPACITY_LEVELS - 1)
    tone = tones[np.abs(colour[..., None] - tones).argmin(-1)]
    premult = (tone[..., None] + tint) * alpha[..., None]

    return src, clean, alpha, premult, fg


def frame_at(f, src, clean, alpha, premult, fg):
    a = np.roll(alpha, f * ART_PX, axis=1)[..., None]
    frame = clean * (1 - a) + np.roll(premult, f * ART_PX, axis=1)
    frame[fg] = src[fg]
    return np.clip(frame + 0.5, 0, 255).astype(np.uint8)


def main():
    src, clean, alpha, premult, fg = cloud_layers()
    tmp = Path(tempfile.mkdtemp())
    frames = OUT_W // ART_PX
    for f in range(frames):
        Image.fromarray(frame_at(f, src, clean, alpha, premult, fg)).save(tmp / f"f{f:04d}.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(tmp / "f%04d.png"),
                    "-vf", f"split[a][b];[a]palettegen=max_colors={PALETTE}:stats_mode=full[p];"
                           "[b][p]paletteuse=dither=none:diff_mode=rectangle",
                    "-loop", "0", str(OUT)], check=True)
    shutil.rmtree(tmp)
    print(f"{OUT.relative_to(ROOT)}: {frames} frames, {OUT_W}x{src.shape[0]}, {FPS} fps, "
          f"{OUT.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
