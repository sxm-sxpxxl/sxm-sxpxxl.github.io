"""Metta Corpse logo, 2026-11-19 export: measure the mark and make the site picture.

Same recipe as mc-logo-a.png (2026-11-11): brightness v = max(R, G, B) becomes alpha, the colour is
normalised to v (so the picture is white-ish with alpha), and alpha fades out over the outer 20% of the
width on each side (smoothstep). Measurements are given in 1920 x 1080 picture pixels, like the CSS.
"""
import sys
import numpy as np
from PIL import Image

src, out, out_w = sys.argv[1], sys.argv[2], int(sys.argv[3])
FEATHER = float(sys.argv[4]) if len(sys.argv) > 4 else 0.2   # share of the width that fades out at each side
im = Image.open(src).convert("RGB")
W, H = im.size
a = np.asarray(im).astype(np.float32)
v = a.max(axis=2)
k = 1920 / W

def box(mask):
    ys, xs = np.nonzero(mask)
    return xs.min(), ys.min(), xs.max(), ys.max()

# the mark: figures and lettering, at 50% brightness (as the old M at x 515 was measured), central band only
band = np.zeros_like(v, dtype=bool)
band[int(250 / k):int(900 / k), :] = True
for thr in (128, 64, 200):
    x0, y0, x1, y1 = box((v > thr) & band)
    print(f"mark at v>{thr}: x {x0*k:.1f}..{(x1+1)*k:.1f}  y {y0*k:.1f}..{(y1+1)*k:.1f}  "
          f"= {(x1+1-x0)*k:.1f} x {(y1+1-y0)*k:.1f}  centre x {(x0+x1+1)/2*k:.1f}")

# rows of the lettering vs the figures: brightness profile by row (count of pixels > 128)
rows = ((v > 128) & band).sum(axis=1)
nz = np.nonzero(rows)[0]
runs, start = [], nz[0]
for p, q in zip(nz, nz[1:]):
    if q != p + 1:
        runs.append((start, p)); start = q
runs.append((start, nz[-1]))
print("row runs with ink (1920 px):", [(round(s * k, 1), round((e + 1) * k, 1)) for s, e in runs if e - s > 4])

# leftmost ink of the lettering rows and of the figure rows (50% brightness)
def left_ink(y0, y1):
    m = (v[int(y0 / k):int(y1 / k)] > 128)
    cols = np.nonzero(m.any(axis=0))[0]
    return cols.min() * k, (cols.max() + 1) * k
print("smoke max brightness outside the band:", float(v[~band].max()), " p99.9:", float(np.percentile(v[~band], 99.9)))
for name, (y0, y1) in {"top rows 250..600": (250, 600), "rows 600..900": (600, 900)}.items():
    print(name, "ink x %.1f..%.1f" % left_ink(y0, y1))

# the site picture
small = im.resize((out_w, round(out_w * H / W)), Image.LANCZOS)
b = np.asarray(small).astype(np.float32)
bv = b.max(axis=2)
t = bv / 255.0
u = np.linspace(0, 1, b.shape[1])[None, :]
def S(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)
t = t * S(u / FEATHER) * S((1 - u) / FEATHER)
rgb = np.where(bv[..., None] > 0, np.minimum(255, b * 255 / np.maximum(bv[..., None], 1)), 255)
outa = np.dstack([rgb, t * 255]).round().clip(0, 255).astype(np.uint8)
Image.fromarray(outa, "RGBA").save(out, optimize=True)
print("saved", out, outa.shape[1], "x", outa.shape[0])
