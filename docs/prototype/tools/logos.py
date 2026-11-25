# Logos without their lettering, for v81: the lettering is set live in the chosen face on top.
#   sxm-mark.png      — logo-transparent.png with "SXM", "Tools" and the slogan faded out (transparent PNG, mark only)
#   mc-logo-live.png  — mc-logo-a.png with "METTA CORPSE" replaced by smoke; the dripping ledge under the kneeling figure stays
# Prints the measured line boxes and colours the live text has to match.
import sys
import numpy as np
from PIL import Image

C = r"D:\rust-projects\persona\.superpowers\brainstorm\1382-1792925805\content"
OUT = sys.argv[1]
BG = np.array([0x13, 0x14, 0x17], np.float32) / 255


def box_blur(a, r, axis):
    pad = [(0, 0)] * a.ndim
    pad[axis] = (r + 1, r)
    c = np.cumsum(np.pad(a, pad, mode="edge"), axis=axis)
    n = a.shape[axis]
    hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
    lo = np.take(c, np.arange(0, n), axis=axis)
    return (hi - lo) / (2 * r + 1)


def blur(a, r):  # three box passes ~ gaussian
    for _ in range(3):
        a = box_blur(box_blur(a, r, 0), r, 1)
    return a


def dilate(m, r):
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                out |= np.roll(np.roll(m, dy, 0), dx, 1)
    return out


def preview(rgba, name):
    a = rgba[..., 3:4]
    rgb = rgba[..., :3] * a + BG * (1 - a)
    Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8)).save(OUT + "\\" + name)


def span(mask):
    idx = np.where(mask)[0]
    return (int(idx.min()), int(idx.max())) if len(idx) else None


# ---------- SXM Tools ----------
s = np.asarray(Image.open(C + r"\logo-transparent.png")).astype(np.float32) / 255
H, W = s.shape[:2]
core = s[..., 3] > .85
lines = {}
for name, (y0, y1, x0) in {"SXM": (0, 300, 520), "Tools": (300, 560, 520), "slogan": (560, H, 0)}.items():
    m = core[y0:y1, x0:]
    ys, xs = span(m.any(1)), span(m.any(0))
    top, bot = ys[0] + y0, ys[1] + y0
    left, right = xs[0] + x0, xs[1] + x0
    # cap height from a flat-topped capital: X / M for SXM (the right 40%), T for Tools (left 18%), I for the slogan (left 2%)
    frac = {"SXM": (.6, 1), "Tools": (0, .18), "slogan": (0, .02)}[name]
    cx0, cx1 = int(left + (right - left) * frac[0]), int(left + (right - left) * frac[1]) + 1
    cs = span(core[y0:y1, cx0:cx1].any(1))
    cap_top, base = cs[0] + y0, cs[1] + y0 + 1
    px_ = s[y0:y1, x0:][m]
    col = np.median(px_[:, :3], axis=0)
    lines[name] = dict(left=left, right=right, top=top, bottom=bot, capTop=cap_top, base=base, cap=base - cap_top,
                       cx=(left + right + 1) / 2, color="#%02X%02X%02X" % tuple(int(round(v * 255)) for v in col))
for k, v in lines.items():
    print("SXM", k, v)

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
keep = np.clip((532 - xx) / 26, 0, 1) * np.clip((578 - yy) / 26, 0, 1)
mark = s.copy()
mark[..., 3] *= keep
Image.fromarray((mark * 255).round().astype(np.uint8), "RGBA").save(C + r"\sxm-mark.png")
preview(mark, "sxm-mark-preview.png")
print("mark alpha left at x>=532:", float(mark[:, 532:, 3].max()), " at y>=578:", float(mark[578:, :, 3].max()))

# ---------- Metta Corpse ----------
im = np.asarray(Image.open(C + r"\mc-logo-a.png")).astype(np.float32) / 255
H, W = im.shape[:2]
al = im[..., 3].copy()
yy, xx = np.mgrid[0:H, 0:W]
# the zone of the lettering; above it the figures stay. Under the kneeling figure (x 600…842) the ledge it kneels on is
# kept down to y 663 (it doubles as the tops of E, T, T); left of it the M and the figure's foot meet at y ~650
ytop = np.where(xx < 560, 600, np.where(xx < 600, 651, np.where(xx <= 842, 664, 633)))
zone = (xx >= 500) & (xx <= 1420) & (yy >= ytop) & (yy <= 800)
letters = dilate(zone & (al > .28), 3) & zone
known = ~dilate(al > .28, 3)   # the figures and the ledge are not smoke either: they would glow into the fill
low = blur(al * known, 9) / np.maximum(blur(known.astype(np.float32), 9), 1e-4)
# film grain: the fine detail of the smoke 170 px further down, laid over the smooth estimate
src = np.roll(al, -170, 0)
grain = src - blur(src, 3)
fill = np.clip(low + grain, 0, 1)
w = np.maximum(letters.astype(np.float32), np.clip(blur(letters.astype(np.float32), 1) * 1.6, 0, 1)) * (yy >= ytop)
out = im.copy()
out[..., 3] = al * (1 - w) + fill * w
out[..., :3] = np.where(w[..., None] > 0, 1.0, im[..., :3])
Image.fromarray((out * 255).round().astype(np.uint8), "RGBA").save(C + r"\mc-logo-live.png")
preview(out[560:820, 470:1440], "mc-live-preview.png")
preview(im[560:820, 470:1440], "mc-orig-preview.png")
# where the figures' ink starts on the left (kneeling figure, above the cut) and the old lettering's ink box
fig = (al > .5) & (yy < 664) & (yy > 450) & (xx > 520) & (xx < 900)
print("kneeling figure ink x:", span(fig.any(0)))
let = (al > .5) & zone
print("old lettering ink x:", span(let.any(0)), "y:", span(let.any(1)))
mx = (al > .5) & (xx >= 500) & (xx < 560) & (yy > 640) & (yy < 800)
print("M ink y (x 500-560):", span(mx.any(1)))
print("left in zone after fill, max alpha:", float(out[..., 3][zone].max()), " p99:", float(np.percentile(out[..., 3][zone], 99)))

