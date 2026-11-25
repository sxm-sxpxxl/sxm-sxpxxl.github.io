"""Make a seamless loop of a rendered theme (2026-11-21, the Metta Corpse theme).

The last C seconds are laid over the first C seconds with an equal-power crossfade (sin/cos: right for uncorrelated
material like drones), and the file is cut C seconds short. Looping the result, the last sample is followed by the
sample that followed it in the render, so there is no seam:
    y = x[:N - C];  y[:C] = x[:C] * sin(t * pi / 2) + x[N - C:] * cos(t * pi / 2),  t = 0..1
Writes the loop at the source bit depth (a master) and, optionally, a 16-bit copy (for the prototype).
Usage: theme_loop.py in.wav out-master.wav [out-16bit.wav] [crossfade seconds, default 5]
"""
import sys, wave
import numpy as np

src, out_master = sys.argv[1], sys.argv[2]
out16 = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3].endswith(".wav") else None
C_SEC = float(sys.argv[4]) if len(sys.argv) > 4 else 5.0

with wave.open(src, "rb") as w:
    ch, sw, sr, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
    raw = w.readframes(n)
if sw == 3:
    b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
    x = (b[:, 0].astype(np.int32) | (b[:, 1].astype(np.int32) << 8) | (b[:, 2].astype(np.int32) << 16))
    x = np.where(x & 0x800000, x - 0x1000000, x).astype(np.float64) / 8388608.0
elif sw == 2:
    x = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
else:
    raise SystemExit("only 16- and 24-bit PCM")
x = x.reshape(-1, ch)

C = int(round(C_SEC * sr))
N = len(x)
t = (np.arange(C) + 0.5) / C
fin, fout = np.sin(t * np.pi / 2)[:, None], np.cos(t * np.pi / 2)[:, None]
y = x[: N - C].copy()
y[:C] = x[:C] * fin + x[N - C:] * fout
peak = np.abs(y).max()
print(f"loop {len(y) / sr:.3f} s ({len(y)} frames), crossfade {C_SEC} s, peak {20 * np.log10(peak):.1f} dBFS")
# the seam: the loop's last frame, then its first frame — equal to the render's frames N-C-1 and N-C
print("seam jump (max |y[0]-y[-1]|):", float(np.abs(y[0] - y[-1]).max()), " vs typical step:", float(np.median(np.abs(np.diff(y[:sr], axis=0)))))

def write(path, data, width):
    with wave.open(path, "wb") as w:
        w.setnchannels(ch); w.setsampwidth(width); w.setframerate(sr)
        if width == 3:
            q = np.clip(np.round(data * 8388608.0), -8388608, 8388607).astype(np.int32).reshape(-1)
            q = q & 0xFFFFFF
            bytes3 = np.stack([(q & 0xFF), (q >> 8) & 0xFF, (q >> 16) & 0xFF], axis=1).astype(np.uint8)
            w.writeframes(bytes3.tobytes())
        else:
            rng = np.random.default_rng(1)   # TPDF dither down to 16 bits
            d = (rng.random(data.shape) - rng.random(data.shape)) / 32768.0
            q = np.clip(np.round((data + d) * 32768.0), -32768, 32767).astype("<i2")
            w.writeframes(q.tobytes())
    print("wrote", path)

write(out_master, y, sw)
if out16:
    write(out16, y, 2)
