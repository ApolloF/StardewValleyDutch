"""Compare every PNG the Dutch mod replaces with the current game texture."""
import os, sys, struct, zlib
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ".")
from xnb import read_xnb, write_png, unpremultiply

C = r"C:\Program Files (x86)\Steam\steamapps\common\Stardew Valley\Content"
A = "StardewValleyDutch/StardewValleyDutch/assets/"
OUT = "img"


def read_png(path):
    d = open(path, "rb").read()
    assert d[:8] == b"\x89PNG\r\n\x1a\n"
    p = 8; idat = b""; plte = None; trns = None
    while p < len(d):
        n = struct.unpack(">I", d[p:p + 4])[0]; t = d[p + 4:p + 8]; body = d[p + 8:p + 8 + n]; p += 12 + n
        if t == b"IHDR": w, h, bd, ct, _, _, il = struct.unpack(">IIBBBBB", body)
        elif t == b"PLTE": plte = body
        elif t == b"tRNS": trns = body
        elif t == b"IDAT": idat += body
    assert bd == 8 and il == 0, (path, bd, il)
    bpp = {6: 4, 2: 3, 3: 1, 0: 1, 4: 2}[ct]
    raw = zlib.decompress(idat); stride = w * bpp
    out = bytearray(); prev = bytearray(stride); i = 0
    for _ in range(h):
        f = raw[i]; line = bytearray(raw[i + 1:i + 1 + stride]); i += 1 + stride
        for x in range(stride):
            a = line[x - bpp] if x >= bpp else 0; b = prev[x]; c = prev[x - bpp] if x >= bpp else 0
            if f == 1: line[x] = (line[x] + a) & 255
            elif f == 2: line[x] = (line[x] + b) & 255
            elif f == 3: line[x] = (line[x] + ((a + b) >> 1)) & 255
            elif f == 4:
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        out += line; prev = line
    if ct == 6: rgba = bytes(out)
    elif ct == 2: rgba = b"".join(bytes(out[j:j + 3]) + b"\xff" for j in range(0, len(out), 3))
    elif ct == 3:
        rgba = bytearray()
        for idx in out:
            rgba += plte[idx * 3:idx * 3 + 3] + bytes([trns[idx] if trns and idx < len(trns) else 255])
        rgba = bytes(rgba)
    elif ct == 4: rgba = b"".join(bytes([out[j]] * 3 + [out[j + 1]]) for j in range(0, len(out), 2))
    else: rgba = b"".join(bytes([v, v, v, 255]) for v in out)
    return w, h, rgba


def diff_mask(w, h, a, b, tile=16):
    """Return set of (tx,ty) tiles that differ (alpha-aware)."""
    tiles = set()
    for y in range(h):
        row = y * w * 4
        ra = a[row:row + w * 4]; rb = b[row:row + w * 4]
        if ra == rb: continue
        for x in range(w):
            i = x * 4
            pa = ra[i:i + 4]; pb = rb[i:i + 4]
            if pa[3] == 0 and pb[3] == 0: continue
            if max(abs(pa[k] - pb[k]) for k in range(4)) > 24:
                tiles.add((x // tile, y // tile))
    return tiles


def compare(rel, pngpath):
    kind, (fmt, w, h, px) = read_xnb(os.path.join(C, rel + ".xnb"))
    game = unpremultiply(px)
    mw, mh, mod = read_png(pngpath)
    base = os.path.join(OUT, rel.replace("/", "_"))
    write_png(base + ".game.png", w, h, game)
    if (mw, mh) != (w, h):
        print(f"{rel:48} SIZE MISMATCH mod={mw}x{mh} game={w}x{h}")
        return
    t = diff_mask(w, h, game, mod)
    total = ((w + 15) // 16) * ((h + 15) // 16)
    print(f"{rel:48} {w}x{h}  differing 16px tiles: {len(t)}/{total}")


def main():
    os.makedirs(OUT, exist_ok=True)
    only = sys.argv[1:] or None
    for root, _, files in os.walk(A):
        for fn in files:
            if not fn.endswith(".png") or fn == "Button.png":
                continue
            rel = os.path.relpath(os.path.join(root, fn), A).replace(os.sep, "/")[:-4]
            if only and rel not in only:
                continue
            compare(rel, os.path.join(root, fn))


if __name__ == "__main__":
    main()
