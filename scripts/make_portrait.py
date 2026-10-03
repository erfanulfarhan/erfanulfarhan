#!/usr/bin/env python3
"""Turn a photo into data/portrait.txt, the ASCII portrait inside whoami.svg.

Run once, locally, on a Mac. The daily job only reads the text file. The
current portrait comes from the same photo as the avatar:

    swiftc -O scripts/person_mask.swift -o /tmp/person_mask
    .venv/bin/python scripts/make_portrait.py ~/Downloads/images/tea-garden.jpg \\
        --frame bust --below 3.7 --cols 90 --light --red 1 \\
        --clahe 1.6 --gamma 1.2 --edges 2.0 --fill 0.08

Apple's Vision finds the face (so the crop is the same whatever the photo's
framing) and cuts the person out of the background, which is what keeps the
background blank instead of a field of characters. CLAHE then evens out the
local contrast, which matters with flat frontal light: without it the face is
one mid grey and prints as a solid block.

ASCII has about thirteen brightness steps, so the useful dials are few:
  --light   dense characters for bright areas, the way the photo looks on a
            dark screen; without it the darkest areas print densest, as ink
  --red     a red filter: skin lightens and blue goes dark, so tinted lenses
            read as sunglasses instead of matching the cheeks
  --gamma   above 1 darkens the mid tones
  --floor   dark ink only: brightness above which a cell is left blank; lower
            it to clear the cheeks and forehead so the features stand out
  --fill    light only: the least ink inside the person, so a black shirt
            still shows as a figure
  --cols    detail; in a head frame the face needs 60 or more columns to read
  --edges   strength of the edge emphasis that keeps features under flat light
  --frame   head (face and shoulders) or bust (down to `--below` face-heights
            under the chin, wide enough for the whole figure: crossed arms)
"""
import argparse
import json
import os
import subprocess

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RAMP = " .`:-=+*cs#%@"          # blank, then light to dense
CELL_ASPECT = 0.5               # a character cell is 0.6 em wide and 1.2 em tall
MASKER = "/tmp/person_mask"


def person_mask(photo, mask_png):
    if not os.path.exists(MASKER):
        subprocess.run(["swiftc", "-O", os.path.join(HERE, "person_mask.swift"), "-o", MASKER], check=True)
    out = subprocess.run([MASKER, photo, mask_png], check=True, capture_output=True, text=True)
    return json.loads(out.stdout.strip().splitlines()[-1])["face"]


def portrait(photo, cols=80, gamma=1.15, floor=0.84, clahe=2.4, edges=1.6, dither=True,
             frame="head", below=3.4, red=0.0, light=False, fill=0.1, work="/tmp"):
    mask_png = os.path.join(work, "portrait-mask.png")
    fx, fy, fw, fh = person_mask(photo, mask_png)
    img = cv2.imread(photo, cv2.IMREAD_GRAYSCALE)
    if red:
        # A red filter, as on black-and-white film: skin lightens and anything
        # blue goes dark. In plain grey, tinted lenses and a shaded cheek can
        # be the same value; here the lenses drop to the darkness of the hair.
        b, _, r = cv2.split(cv2.imread(photo).astype(np.float32))
        deep_red = np.clip(r - np.maximum(b - r, 0), 0, 255)
        img = np.clip((1 - red) * img + red * deep_red, 0, 255).astype(np.uint8)
    mask = cv2.imread(mask_png, cv2.IMREAD_GRAYSCALE)
    H, W = img.shape

    if frame == "head":
        # Head and shoulders, framed on the face: hair above, collar below.
        x0 = max(0, int(fx + fw / 2 - 1.05 * fw)); x1 = min(W, int(fx + fw / 2 + 1.05 * fw))
        y0 = max(0, int(fy - 0.80 * fh)); y1 = min(H, int(fy + fh + 0.62 * fh))
    else:
        # "bust": from the hair down to `below` face-heights under the chin (far
        # enough for crossed arms), as wide as the person is across that span.
        y0 = max(0, int(fy - 0.80 * fh)); y1 = min(H, int(fy + fh + below * fh))
        cols_on = np.where((mask[y0:y1] > 128).any(axis=0))[0]
        pad = int(0.25 * fw)
        x0 = max(0, int(cols_on.min()) - pad); x1 = min(W, int(cols_on.max()) + pad)
    img, mask = img[y0:y1, x0:x1], mask[y0:y1, x0:x1].astype(np.float32) / 255

    scale = 900 / img.shape[1]                      # a common working size for every photo
    img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    mask = cv2.resize(mask, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_LINEAR)
    img = cv2.bilateralFilter(img, 9, 40, 40)       # smooth skin texture, keep the edges
    img = cv2.createCLAHE(clipLimit=clahe, tileGridSize=(8, 8)).apply(img)
    lum = img.astype(np.float32) / 255
    # Edge emphasis (a difference of Gaussians): flat light leaves the brows,
    # eyes and lips only slightly darker than the skin around them, and at
    # thirteen brightness steps that difference vanishes. Deepening each local
    # dip keeps them.
    if edges:
        dog = cv2.GaussianBlur(lum, (0, 0), 1.2) - cv2.GaussianBlur(lum, (0, 0), 4.0)
        lum = np.clip(lum + edges * np.minimum(dog, 0), 0, 1)
    yy, xx = np.mgrid[0:lum.shape[0], 0:lum.shape[1]].astype(np.float32)
    if frame == "head":
        # An oval vignette around the face, so the shoulders and a dark shirt
        # dissolve instead of printing as a solid block that outweighs the face.
        cx, cy = (fx + fw / 2 - x0) * scale, (fy + fh * 0.55 - y0) * scale
        rx, ry = 1.05 * fw * scale, 1.18 * fh * scale
        d = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
        fade = np.clip((d - 0.78) / 0.55, 0, 1)
    else:
        # Only the last stretch fades, so the figure ends softly below the arms.
        fade = np.clip((yy / lum.shape[0] - 0.92) / 0.08, 0, 1)
    fade = fade * fade * (3 - 2 * fade)

    rows = round(cols * img.shape[0] / img.shape[1] * CELL_ASPECT)
    shrink = lambda a: cv2.resize(a, (cols, rows), interpolation=cv2.INTER_AREA)
    if light:
        # Light ink on a dark page: bright areas take the dense characters, the
        # way the photo itself looks on screen. Every cell inside the person
        # keeps at least `fill` of the ramp, so a black shirt still prints as a
        # faint figure instead of vanishing into the background.
        keep = shrink(mask * (1 - fade))
        body = np.clip(shrink(lum * mask) / np.maximum(shrink(mask), 1e-3), 0, 1)
        ink = keep * (fill + (1 - fill) * body ** gamma)
        blank = ink < fill / 2
    else:
        # Dark ink, as on paper: dark areas take the dense characters and
        # everything outside the person, or faded out, is white.
        lum = lum * mask + (1 - mask)
        small = shrink(lum + (1 - lum) * fade) ** gamma
        ink = 1 - small / floor
        blank = small >= floor
    n = len(RAMP) - 1
    # Ordered dithering: a 4x4 Bayer offset of up to half a step, so a smooth
    # gradient becomes a texture instead of stripes of one character.
    bayer = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) + 0.5) / 16 - 0.5
    lines = []
    for r in range(rows):
        chars = []
        for c in range(cols):
            if blank[r, c]:
                chars.append(" ")
                continue
            level = ink[r, c] * n + (bayer[r % 4, c % 4] if dither else 0)
            chars.append(RAMP[max(1, min(n, round(level)))])
        lines.append("".join(chars).rstrip())
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def preview(lines, path, size=10.0):
    """A still, dark, standalone SVG for judging a portrait by eye."""
    import base64
    with open(os.path.join(HERE, "fonts", "jbmono-400.woff2"), "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    lh = size * 1.2
    w = int(max(len(l) for l in lines) * size * 0.6 + 24)
    h = int(len(lines) * lh + 24)
    esc = lambda s: s.replace("&", "&amp;").replace("<", "&lt;")
    rows = "".join(f'<text x="12" y="{12 + (i + 0.8) * lh:.1f}" xml:space="preserve">{esc(l)}</text>'
                   for i, l in enumerate(lines))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
           f'<style>@font-face{{font-family:J;src:url(data:font/woff2;base64,{b64})}}'
           f'text{{font:{size}px J;fill:#c9d1d9}}</style>'
           f'<rect width="{w}" height="{h}" fill="#0d1117"/>{rows}</svg>')
    with open(path, "w") as f:
        f.write(svg)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("photo")
    ap.add_argument("--cols", type=int, default=80)
    ap.add_argument("--gamma", type=float, default=1.15)
    ap.add_argument("--floor", type=float, default=0.84)
    ap.add_argument("--clahe", type=float, default=2.4)
    ap.add_argument("--edges", type=float, default=1.6)
    ap.add_argument("--no-dither", dest="dither", action="store_false")
    ap.add_argument("--frame", choices=("head", "bust"), default="head")
    ap.add_argument("--below", type=float, default=3.4, help="bust: face-heights below the chin")
    ap.add_argument("--red", type=float, default=0.0, help="red filter strength, 0 to 1")
    ap.add_argument("--light", action="store_true", help="dense characters for bright areas")
    ap.add_argument("--fill", type=float, default=0.1, help="light: the least ink inside the person")
    ap.add_argument("--out", default=os.path.join(HERE, "..", "data", "portrait.txt"))
    ap.add_argument("--preview")
    a = ap.parse_args()
    lines = portrait(a.photo, a.cols, a.gamma, a.floor, a.clahe, a.edges, a.dither, a.frame, a.below,
                     a.red, a.light, a.fill)
    if a.preview:
        preview(lines, a.preview)
    else:
        with open(a.out, "w") as f:
            f.write("\n".join(lines) + "\n")
    print(f"{len(lines)} rows x {max(len(l) for l in lines)} cols")
