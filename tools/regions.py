"""Find the text areas of a texture and render review sheets.

Officially localized textures: the areas are where any official Latin translation differs from
English. Extra map sheets (not localized by the game): where the old Dutch mod differs.

usage: regions.py <Asset/Name> [--old]      -> prints clusters, writes review/regions/<asset>.png
"""
import os
import sys

from paths import VANILLA, LEGACY, ROOT, LATIN_LANGS
from glyphs import Image
from xnb import write_png

TILE = 4


def load(asset, lang):
    p = os.path.join(VANILLA, lang, asset + ".png")
    return Image.load(p) if os.path.exists(p) else None


def load_old(asset):
    p = os.path.join(LEGACY, asset + ".png")
    return Image.load(p) if os.path.exists(p) else None


def diff_tiles(a, b, tile=TILE):
    out = set()
    w, h = min(a.w, b.w), min(a.h, b.h)
    for y in range(h):
        for x in range(w):
            p, q = a.get(x, y), b.get(x, y)
            if p[3] == 0 and q[3] == 0:
                continue
            if max(abs(p[i] - q[i]) for i in range(4)) > 24:
                out.add((x // tile, y // tile))
    return out


def clusters(tiles, gap=2):
    tiles = set(tiles)
    seen, boxes = set(), []
    for t in sorted(tiles):
        if t in seen:
            continue
        stack, comp = [t], []
        seen.add(t)
        while stack:
            cx, cy = stack.pop(); comp.append((cx, cy))
            for dx in range(-gap, gap + 1):
                for dy in range(-gap, gap + 1):
                    n = (cx + dx, cy + dy)
                    if n in tiles and n not in seen:
                        seen.add(n); stack.append(n)
        xs = [c[0] for c in comp]; ys = [c[1] for c in comp]
        boxes.append((min(xs) * TILE, min(ys) * TILE, (max(xs) + 1) * TILE, (max(ys) + 1) * TILE))
    return sorted(boxes, key=lambda b: (b[1], b[0]))


def text_areas(asset, use_old=False):
    en = load(asset, "en")
    tiles = set()
    if use_old:
        old = load_old(asset)
        if old:
            tiles |= diff_tiles(en, old)
    else:
        for lang in LATIN_LANGS:
            img = load(asset, lang)
            if img and (img.w, img.h) == (en.w, en.h):
                tiles |= diff_tiles(en, img)
    return clusters(tiles)


def render(asset, boxes, columns, scale=3, pad=2):
    rows = []
    for (x0, y0, x1, y1) in boxes:
        x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
        rows.append((x0, y0, x1 + pad - x0, y1 + pad - y0))
    col_w = max(r[2] for r in rows) * scale + 6
    H = sum(r[3] * scale + 6 for r in rows)
    W = col_w * len(columns)
    out = Image(W, H, b"\x30\x30\x30\xff" * (W * H))
    y = 0
    for (x0, y0, w, h) in rows:
        for c, img in enumerate(columns):
            if img is None:
                continue
            for yy in range(h):
                for xx in range(w):
                    if x0 + xx >= img.w or y0 + yy >= img.h:
                        continue
                    p = img.get(x0 + xx, y0 + yy)
                    a = p[3] / 255
                    col = tuple(int(p[k] * a + 0x30 * (1 - a)) for k in range(3)) + (255,)
                    for dy in range(scale):
                        for dx in range(scale):
                            out.set(c * col_w + xx * scale + dx, y + yy * scale + dy, col)
        y += h * scale + 6
    path = os.path.join(ROOT, "review", "regions", asset.replace("/", "_") + ".png")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    write_png(path, W, H, bytes(out.px))
    return path


if __name__ == "__main__":
    asset = sys.argv[1]
    use_old = "--old" in sys.argv
    boxes = text_areas(asset, use_old)
    for b in boxes:
        print(f"  x={b[0]:4} y={b[1]:4} w={b[2] - b[0]:4} h={b[3] - b[1]:4}")
    cols = [load(asset, "en"), load(asset, "de-DE"), load(asset, "fr-FR"), load_old(asset)]
    print(render(asset, boxes, cols))
