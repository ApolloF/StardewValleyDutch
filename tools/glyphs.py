"""Cut letters out of the official translations' textures and compose new words from them.

The game's hand-drawn lettering only exists as pixels in the official localized textures, so Dutch
words are assembled from those exact letters (same brush, same colors), never from a font.
"""
import os

from paths import VANILLA
from images import read_png

_cache = {}


class Image:
    def __init__(self, w, h, px):
        self.w, self.h, self.px = w, h, bytearray(px)

    @classmethod
    def load(cls, path):
        if path not in _cache:
            _cache[path] = read_png(path)
        w, h, px = _cache[path]
        return cls(w, h, px)

    @classmethod
    def sheet(cls, asset, lang="en"):
        return cls.load(os.path.join(VANILLA, lang, asset + ".png"))

    def get(self, x, y):
        i = (y * self.w + x) * 4
        return tuple(self.px[i:i + 4])

    def set(self, x, y, c):
        i = (y * self.w + x) * 4
        self.px[i:i + 4] = bytes(c)

    def crop(self, x, y, w, h):
        out = Image(w, h, bytes(w * h * 4))
        for yy in range(h):
            i = ((y + yy) * self.w + x) * 4
            out.px[yy * w * 4:(yy + 1) * w * 4] = self.px[i:i + w * 4]
        return out

    def paste(self, img, x, y):
        for yy in range(img.h):
            i = ((y + yy) * self.w + x) * 4
            self.px[i:i + img.w * 4] = img.px[yy * img.w * 4:(yy + 1) * img.w * 4]


class Glyph:
    """Pixels of one letter: {(dx, dy): rgba} relative to its top-left, plus its baseline row."""
    def __init__(self, pixels, w, h):
        self.pixels, self.w, self.h = pixels, w, h

    def recolor(self, mapping):
        return Glyph({p: mapping.get(c, c) for p, c in self.pixels.items()}, self.w, self.h)

    def without(self, points):
        return Glyph({p: c for p, c in self.pixels.items() if p not in points}, self.w, self.h)

    def plus(self, extra):
        px = dict(self.pixels); px.update(extra)
        w = max(self.w, max((x for x, _ in extra), default=0) + 1)
        h = max(self.h, max((y for _, y in extra), default=0) + 1)
        return Glyph(px, w, h)

    def mirrored(self):
        return Glyph({(self.w - 1 - x, y): c for (x, y), c in self.pixels.items()}, self.w, self.h)


def harvest(img, rect, text, colors, baseline, split=None):
    """Cut the letters of a known word/phrase out of an image.

    rect: area containing only this text; text: what it says (spaces ignored); baseline: the sheet
    row the letters stand on. Letters are split on empty columns; 'split' adds extra cut columns
    for letters that touch. Returns {char: Glyph} (glyph y relative to the baseline, x from 0), or
    raises with the segment list if the count doesn't match."""
    mask = text_mask(img, rect, colors)
    segs = segments(mask)
    for cx in sorted(split or []):
        for i, (a, b) in enumerate(segs):
            if a < cx <= b:
                segs[i:i + 1] = [(a, cx - 1), (cx, b)]
                break
    chars = [c for c in text if c != " "]
    if len(segs) != len(chars):
        raise ValueError(f"{len(segs)} segments for {len(chars)} letters of {text!r}: {segs}")
    out = {}
    for ch, (a, b) in zip(chars, segs):
        pix = {(x - a, y - baseline): img.get(x, y) for (x, y) in mask if a <= x <= b}
        out.setdefault(ch, Glyph(pix, b - a + 1, 0))
    return out


def typeset(text, font, tracking=1, space=4, kerning=None):
    """Lay out text from a {char: Glyph} font on a common baseline -> ([(glyph, x)], width)."""
    placed, x = [], 0
    for i, ch in enumerate(text):
        if ch == " ":
            x += space
            continue
        g = font[ch]
        placed.append((g, x))
        x += g.w + tracking + (kerning or {}).get(text[i:i + 2], 0)
    return placed, x - tracking


def draw(img, placed, x, baseline):
    for g, gx in placed:
        for (px, py), c in g.pixels.items():
            img.set(x + gx + px, baseline + py, c)


def text_mask(img, rect, colors):
    """Set of (x, y) inside rect whose color is one of the text colors."""
    x0, y0, w, h = rect
    return {(x, y) for y in range(y0, y0 + h) for x in range(x0, x0 + w) if img.get(x, y)[:3] in colors}


def segments(mask):
    """Split a text mask into letters by empty columns: [(x0, x1)] inclusive."""
    cols = sorted({x for x, _ in mask})
    out = []
    for x in cols:
        if out and x == out[-1][1] + 1:
            out[-1][1] = x
        else:
            out.append([x, x])
    return [tuple(s) for s in out]


def cut(img, mask, x0, x1, top, bottom):
    """Glyph from the mask columns x0..x1, positioned relative to (x0, top)."""
    pix = {(x - x0, y - top): img.get(x, y) for (x, y) in mask if x0 <= x <= x1 and top <= y <= bottom}
    return Glyph(pix, x1 - x0 + 1, bottom - top + 1)


def ascii(img, rect, colors, marks=".#+*o"):
    x0, y0, w, h = rect
    palette = {c: marks[1 + i % (len(marks) - 1)] for i, c in enumerate(colors)}
    lines = ["     " + "".join(str((x // 10) % 10) for x in range(x0, x0 + w)),
             "     " + "".join(str(x % 10) for x in range(x0, x0 + w))]
    for y in range(y0, y0 + h):
        lines.append(f"{y:4} " + "".join(palette.get(img.get(x, y)[:3], ".") for x in range(x0, x0 + w)))
    return "\n".join(lines)


def compose(glyphs, spacing=1):
    """Lay glyphs out left to right; each item is a Glyph or ('gap', n) or (glyph, dy)."""
    placed, x = [], 0
    for g in glyphs:
        if isinstance(g, tuple) and g[0] == "gap":
            x += g[1]; continue
        dy = 0
        if isinstance(g, tuple):
            g, dy = g
        placed.append((g, x, dy))
        x += g.w + spacing
    width = x - spacing
    height = max(g.h + dy for g, _, dy in placed)
    return placed, width, height


def stamp(img, placed, x, y):
    for g, gx, dy in placed:
        for (px_, py_), c in g.pixels.items():
            img.set(x + gx + px_, y + dy + py_, c)


def shrink_row(g, row):
    """One pixel shorter: drop 'row' and move everything above it down (baseline-relative rows)."""
    pix = {}
    for (x, y), c in g.pixels.items():
        if y == row:
            continue
        pix[(x, y + 1 if y < row else y)] = c
    return Glyph(pix, g.w, g.h)


def line_bands(mask, min_gap=1):
    """Row ranges [(top, bottom)] of text lines: runs of rows that contain ink."""
    rows = sorted({y for _, y in mask})
    bands = []
    for y in rows:
        if bands and y - bands[-1][1] <= min_gap:
            bands[-1][1] = y
        else:
            bands.append([y, y])
    return [tuple(b) for b in bands]


def harvest_lines(img, rect, lines, colors, report=None):
    """Harvest several lines of known text from one area. Line bands are found automatically; the
    baseline of each is the most common bottom row of its letters. Lines whose letter count doesn't
    match are skipped (and listed in 'report')."""
    import collections
    x0, y0, w, h = rect
    mask = text_mask(img, rect, colors)
    bands = line_bands(mask)
    font = {}
    if len(bands) != len(lines):
        if report is not None:
            report.append(f"{len(bands)} bands for {len(lines)} lines {lines}: {bands}")
        return font
    for (top, bottom), text in zip(bands, lines):
        band = {(x, y) for (x, y) in mask if top <= y <= bottom}
        segs = segments(band)
        chars = [c for c in text if c != " "]
        if len(segs) != len(chars):
            if report is not None:
                report.append(f"{text!r}: {len(segs)} segments for {len(chars)} letters")
            continue
        bottoms = collections.Counter(max(y for x, y in band if a <= x <= b) for a, b in segs)
        base = bottoms.most_common(1)[0][0]
        for ch, (a, b) in zip(chars, segs):
            pix = {(x - a, y - base): img.get(x, y) for (x, y) in band if a <= x <= b}
            font.setdefault(ch, Glyph(pix, b - a + 1, 0))
    return font
