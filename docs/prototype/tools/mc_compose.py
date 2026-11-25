"""Two rough Metta Corpse compositions for the site tab (2026-11-21), on top of the author's v92 export.

d: "three postures" — the seated person from photo 2, small, between the crawling figure and the meditating one.
e: "rhyming gestures" — the flat hovering hand from photo 1 over the crawling figure, the ring-fingered hand
   from photo 2 beside the meditating figure.
Photos are dark-on-dark, so each piece is lifted (background subtracted, gain) and laid on with "lighten" under a
soft elliptical mask: on the site black turns transparent anyway, so nothing needs cutting out.
All coordinates are 1920 x 1080 picture pixels (the CSS works in them too).
"""
import numpy as np
from PIL import Image

IMG = "C:/Users/Alexey/AppData/Local/Temp/claude/3895ee5ea9eaf820/2f367d6b-2386-47b7-8509-8d6899102de6/images/"
BASE = "D:/media-pool/affinity-projects/metta-corpse/metta-corpse.png"
OUT = "C:/Users/Alexey/AppData/Local/Temp/claude/3895ee5ea9eaf820/2f367d6b-2386-47b7-8509-8d6899102de6/scratchpad/"

base = np.asarray(Image.open(BASE).convert("RGB").resize((1920, 1080), Image.LANCZOS)).astype(np.float32)


def piece(file, box, height=None, width=None, gamma=0.9, edge=0.12, oval=None, bgq=None):
    """Crop, scale, lift and give soft rectangular edges.

    The backdrop level is the median of the crop's border; everything is measured from it, then a gamma lifts
    the dark clothes (gamma < 1) so the body reads as grey on black, as the gloves stay white."""
    im = Image.open(IMG + file).convert("L").crop(box)
    w, h = im.size
    s = height / h if height else width / w
    im = im.resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32)
    hh, ww = a.shape
    b = max(2, round(min(hh, ww) * .05))
    border = np.concatenate([a[:b].ravel(), a[-b:].ravel(), a[:, :b].ravel(), a[:, -b:].ravel()])
    bg = (float(np.percentile(a, bgq)) if bgq is not None else float(np.median(border))) + 3
    a = np.clip(a - bg, 0, None)
    top = float(np.percentile(a, 99.8)) or 1
    a = 255 * np.clip(a / top, 0, 1) ** gamma
    y, x = np.mgrid[0:hh, 0:ww]
    if oval:   # a soft oval hugging the figure instead of the crop's rectangle: (feather share of the radius)
        r = np.sqrt(((x + .5) / ww * 2 - 1) ** 2 + ((y + .5) / hh * 2 - 1) ** 2)
        t = np.clip((1 - r) / oval, 0, 1)
    else:
        d = np.minimum.reduce([(x + .5) / ww, (ww - x - .5) / ww, (y + .5) / hh, (hh - y - .5) / hh])
        t = np.clip(d / edge, 0, 1)
    return a * (t * t * (3 - 2 * t))


def lay(canvas, p, cx=None, cy=None, left=None, top=None, bottom=None):
    hh, ww = p.shape
    x0 = round(cx - ww / 2) if cx is not None else left
    y0 = round(cy - hh / 2) if cy is not None else (top if top is not None else bottom - hh)
    sub = canvas[y0:y0 + hh, x0:x0 + ww]
    np.maximum(sub, p[:sub.shape[0], :sub.shape[1], None], out=sub)   # lighten
    return (x0, y0, x0 + ww, y0 + hh)


# d: three postures
d = base.copy()
# the body is as dark as the backdrop, so it cannot be lifted on its own: instead the lit backdrop around it is kept
# as a soft halo (like the meditating figure's), and the person reads as a dark silhouette in it
im = Image.open(IMG + "91.jpg").convert("L").crop((215, 700, 935, 2000))
s = 380 / im.size[1]
im = im.resize((round(im.size[0] * s), 380), Image.LANCZOS)
a = np.asarray(im).astype(np.float32)
lo, hi = np.percentile(a, 1), np.percentile(a, 99.7)
a = 255 * np.clip((a - lo) / (hi - lo), 0, 1) ** 0.75
hh, ww = a.shape
yy, xx = np.mgrid[0:hh, 0:ww]
r = np.sqrt(((xx + .5) / ww * 2 - 1) ** 2 + ((yy + .5) / hh * 2 - 1) ** 2)
t = np.clip((1 - r) / 0.7, 0, 1)
person = a * (t * t * (3 - 2 * t))
print("d person at", lay(d, person, cx=922, bottom=668))
Image.fromarray(d.round().clip(0, 255).astype(np.uint8)).save(OUT + "mc-comp-d.png")

# e: rhyming gestures
e = base.copy()
flat = piece("90.jpg", (380, 1085, 660, 1225), width=330, gamma=0.85, edge=0.18)
print("e flat hand at", lay(e, flat, cx=735, cy=408))
mudra = piece("91.jpg", (235, 1300, 405, 1465), width=175, gamma=0.85, edge=0.18)
print("e mudra hand at", lay(e, mudra, cx=1478, cy=566))
Image.fromarray(e.round().clip(0, 255).astype(np.uint8)).save(OUT + "mc-comp-e.png")

# a side-by-side preview to look at before they go on the tab
prev = Image.new("RGB", (1920, 1080 * 2 + 10), (60, 20, 20))
prev.paste(Image.open(OUT + "mc-comp-d.png"), (0, 0))
prev.paste(Image.open(OUT + "mc-comp-e.png"), (0, 1090))
prev.resize((960, 1085)).save(OUT + "mc-comp-preview.png")
print("ok")
