"""Compose the README/site banner "STARDEW VALLEY NEDERLANDS" from the old "STARDEW VALLEY DUTCH" banner.

Every letter is cut from art/banner-dutch.png itself (same planks, nails, outline and shadow), so the
new word matches the old banner exactly. N does not occur in it and is built from the planks of the H
and the left arm of the V, sheared a little so the diagonal reaches from plank to plank.

usage: banner.py   -> art/banner-nederlands.png
"""
import os

from paths import ART
from images import read_png
from xnb import write_png

SRC = os.path.join(ART, "banner-dutch.png")
OUT = os.path.join(ART, "banner-nederlands.png")
PREFIX_END = 739          # "STARDEW VALLEY" plus the leaves before the third word
GAP = 5                   # columns between the solid parts of two letters (as in the old banner)
MARGIN = 2                # columns after the trailing leaf


def is_leaf(c):
    return c[3] and c[1] > c[0] + 15 and c[1] >= c[2]   # the leaf outline is teal (g == b); shadows are grey


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = [[(0, 0, 0, 0)] * w for _ in range(h)]

    def over(self, x, y, c):
        """Alpha-composite c over the pixel at (x, y)."""
        if not (0 <= x < self.w and 0 <= y < self.h) or not c[3]:
            return
        r, g, b, a = self.px[y][x]
        sa, da = c[3] / 255, a / 255
        oa = sa + da * (1 - sa)
        mix = lambda s, d: round((s * sa + d * da * (1 - sa)) / oa)
        self.px[y][x] = (mix(c[0], r), mix(c[1], g), mix(c[2], b), round(oa * 255))

    def rgba(self):
        return b"".join(bytes(c) for row in self.px for c in row)


def load():
    w, h, raw = read_png(SRC)
    return w, h, [[tuple(raw[(y * w + x) * 4:(y * w + x) * 4 + 4]) for x in range(w)] for y in range(h)]


def cut(src, x0, x1, keep=lambda x, y: True, leaves=False):
    """{(x, y): rgba} of the source columns x0..x1 (source coordinates), without leaves unless asked."""
    return {(x, y): c for y, row in enumerate(src) for x in range(x0, x1 + 1)
            if (c := row[x])[3] and keep(x, y) and is_leaf(c) == leaves}


def solid_span(piece):
    xs = [x for (x, _), c in piece.items() if c[3] > 200 and not is_leaf(c)]
    return min(xs), max(xs)


def shift(piece, dx, shear=0.0, top=0):
    return {(x + dx + round((y - top) * shear), y): c for (x, y), c in piece.items()}


def letter_n(src):
    """N: the diagonal (left arm of the V, sheared) under the two planks of the H."""
    left = cut(src, 932, 950)
    right = cut(src, 963, 983, keep=lambda x, y: not (58 <= y <= 77 and x < 966))
    for y in range(58, 78):                        # fill the plank's own left shadow where the crossbar was
        for x in range(963, 966):
            if src[50][x][3]:
                right[(x, y)] = src[50][x]
    v_split = lambda x, y: x <= (441 if y < 70 else 450)
    diag = shift(cut(src, 412, 450, keep=v_split), 0, shear=0.2, top=31)
    # left plank body starts at 937, the V arm at 418: put the arm's top half on the left plank
    diag = shift(diag, 937 - 418 + 6)
    d_right = max(x for (x, y) in diag if y > 85)
    right = shift(right, d_right - 980)            # right plank covers the bottom of the diagonal
    return [diag, left, right]


def main():
    w, h, src = load()
    letters = {
        "E": [cut(src, 257, 306)],
        "D": [cut(src, 209, 257)],
        "R": [cut(src, 166, 207)],
        "L": [cut(src, 516, 560, keep=lambda x, y: x <= (557 if y < 80 else 560))],
        "A": [cut(src, 458, 513, keep=lambda x, y: x >= (466 if y < 60 else 458))],
        "S": [cut(src, 24, 74, keep=lambda x, y: y >= 29)],   # above: remnants of the leaves
        "N": letter_n(src),
    }
    trailing_leaf = cut(src, 976, w - 1, keep=lambda x, y: y < 60, leaves=True)

    placed = []
    pos = 741                                      # solid start of the old "D" of DUTCH
    for ch in "NEDERLANDS":
        layers = letters[ch]
        lo = min(solid_span(p)[0] for p in layers)
        hi = max(solid_span(p)[1] for p in layers)
        placed += [shift(p, pos - lo) for p in layers]
        pos += hi - lo + 1 + GAP
    h_right = 981                                  # leaf position relative to the H it followed
    last_solid = pos - GAP - 1
    leaf = shift(trailing_leaf, last_solid - h_right)
    width = max(x for x, _ in leaf) + 1 + MARGIN

    out = Canvas(width, h)
    for y in range(h):
        for x in range(PREFIX_END + 1):
            out.over(x, y, src[y][x])
    for piece in placed + [leaf]:
        for (x, y), c in sorted(piece.items(), key=lambda kv: (kv[0][1], kv[0][0])):
            out.over(x, y, c)
    write_png(OUT, width, h, out.rgba())
    print(f"{OUT}  ({width}x{h})")


if __name__ == "__main__":
    main()
