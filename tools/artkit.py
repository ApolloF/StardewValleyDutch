"""Shared helpers for the image patches: clean backgrounds, patch registration and previews."""
import collections
import os

from paths import ART, ROOT, LATIN_LANGS, LEGACY, load_json, save_json
from glyphs import Image, Glyph
from xnb import write_png

LANGS = ["en"] + LATIN_LANGS


def sheet(asset, lang="en"):
    return Image.sheet(asset, lang)


def sheets(asset):
    out = []
    for lang in LANGS:
        try:
            s = sheet(asset, lang)
        except FileNotFoundError:
            continue
        out.append(s)
    return out


def blank(asset, rect, ink, zone=None, fill=None):
    """Crop of the English sheet with all ink removed inside zone (sheet coords x0,y0,x1,y1).
    Each ink pixel becomes the most common non-ink value at that spot across the official sheets
    (text sits in different places per language, the art underneath is identical); 'fill'
    forces a flat color instead."""
    x0, y0, w, h = rect
    zx0, zy0, zx1, zy1 = zone or (x0, y0, x0 + w - 1, y0 + h - 1)
    ss = sheets(asset)
    en = ss[0]
    out = en.crop(x0, y0, w, h)
    for y in range(max(y0, zy0), min(y0 + h, zy1 + 1)):
        for x in range(max(x0, zx0), min(x0 + w, zx1 + 1)):
            if fill is not None:
                if en.get(x, y)[:3] in ink:
                    out.set(x - x0, y - y0, fill)
                continue
            votes = collections.Counter(s.get(x, y) for s in ss if x < s.w and y < s.h and s.get(x, y)[:3] not in ink)
            if votes:
                out.set(x - x0, y - y0, votes.most_common(1)[0][0])
    return out


def flip_v(g):
    """Vertically mirrored glyph around its own x-height box (e.g. M -> W)."""
    ys = [y for _, y in g.pixels]
    lo, hi = min(ys), max(ys)
    return Glyph({(x, lo + hi - y): c for (x, y), c in g.pixels.items()}, g.w, g.h)


def bitmap(rows, ink, soft=None):
    """Glyph from strings: '#' = ink, '+' = soft edge color; the last row sits on the baseline.
    Rows below the baseline can be given by a trailing '|' marker row count (not needed so far)."""
    pix = {}
    n = len(rows)
    for yy, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == "#":
                pix[(x, yy - (n - 1))] = ink
            elif ch == "+" and soft:
                pix[(x, yy - (n - 1))] = soft
    return Glyph(pix, max(len(r) for r in rows), n)


class Patches:
    """Collects the image patches of one target asset and writes them + art/patches.json."""

    def __init__(self, asset):
        self.asset = asset
        self.items = []

    def add(self, name, img, x, y):
        self.items.append((name, img, (x, y, img.w, img.h)))

    def save(self):
        folder = os.path.join(ART, "patches", *self.asset.split("/"))
        os.makedirs(folder, exist_ok=True)
        all_patches = [p for p in load_json(os.path.join(ART, "patches.json"), default=[]) if p["target"] != self.asset]
        for name, img, area in self.items:
            write_png(os.path.join(folder, name), img.w, img.h, bytes(img.px))
            all_patches.append({"target": self.asset, "file": f"{self.asset}/{name}", "area": list(area)})
        save_json(os.path.join(ART, "patches.json"), all_patches)
        print(f"{self.asset}: {len(self.items)} patches")

    def patched(self):
        img = sheet(self.asset)
        img = Image(img.w, img.h, bytes(img.px))
        for _, p, (x, y, w, h) in self.items:
            img.paste(p, x, y)
        return img

    def preview(self, view, scale=3, name=None):
        """review/<asset>.png: rows = views (x, y, w, h); columns = game, old Dutch mod, new."""
        old_path = os.path.join(LEGACY, self.asset + ".png")
        from images import read_png
        old = Image(*read_png(old_path)) if os.path.exists(old_path) else None
        cols = [sheet(self.asset), old, self.patched()]
        col_w = max(v[2] for v in view) * scale + 8
        H = sum(v[3] * scale + 8 for v in view)
        W = col_w * len(cols)
        out = Image(W, H, b"\x30\x30\x30\xff" * (W * H))
        yoff = 0
        for (vx, vy, vw, vh) in view:
            for c, img in enumerate(cols):
                if img is None:
                    continue
                for yy in range(vh):
                    for xx in range(vw):
                        if vx + xx >= img.w or vy + yy >= img.h:
                            continue
                        p = img.get(vx + xx, vy + yy)
                        a = p[3] / 255
                        col = tuple(int(p[k] * a + 0x30 * (1 - a)) for k in range(3)) + (255,)
                        for dy in range(scale):
                            for dx in range(scale):
                                out.set(c * col_w + xx * scale + dx, yoff + yy * scale + dy, col)
            yoff += vh * scale + 8
        path = os.path.join(ROOT, "review", (name or self.asset.replace("/", "_")) + ".png")
        write_png(path, W, H, bytes(out.px))
        print("preview:", path)
        return path
