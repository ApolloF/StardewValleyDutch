"""Crop a region from several PNGs and stack them vertically (scaled) for viewing.
usage: montage.py out.png x y w h scale file1 file2 ..."""
import sys, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ".")
from images import read_png
from xnb import write_png

out, x0, y0, cw, ch, sc = sys.argv[1], *map(int, sys.argv[2:7])
files = sys.argv[7:]
gap = 4
W = cw * sc; H = (ch * sc + gap) * len(files)
canvas = bytearray(b"\x30\x30\x30\xff" * (W * H))
for n, f in enumerate(files):
    w, h, px = read_png(f)
    for y in range(ch):
        for x in range(cw):
            sx, sy = x0 + x, y0 + y
            if sx >= w or sy >= h: continue
            i = (sy * w + sx) * 4
            p = px[i:i + 4]
            a = p[3] / 255
            col = bytes(int(p[k] * a + 0x30 * (1 - a)) for k in range(3)) + b"\xff"
            for dy in range(sc):
                row = (n * (ch * sc + gap) + y * sc + dy) * W
                for dx in range(sc):
                    j = (row + x * sc + dx) * 4
                    canvas[j:j + 4] = col
write_png(out, W, H, bytes(canvas))
print(out, W, H)
