"""LooseSprites/Cursors: the text sprites that are redrawn (the rest comes from art_maps-style reuse).

- fishing tutorial box: 'Klik: balk omhoog / Loslaten: balk omlaag / Leg de balk op de vis'
- slot machine buttons: 'WED 10', 'WED 100', 'KLAAR' ('CALICO SPIN' stays as in the original)
- 'NIEUW!' and 'KLAAR' tags, skip button as the official German one
"""
import sys

from glyphs import harvest_lines, typeset, draw, Glyph
from artkit import sheet, blank, Patches

ASSET = "LooseSprites/Cursors"
FISH_W = {(208, 210, 216), (57, 64, 78), (97, 103, 116)}
FISH_G = {(130, 229, 0), (57, 64, 78), (97, 103, 116)}
WHITE, GREEN = (208, 210, 216, 255), (130, 229, 0, 255)


def union(*glyphs_offsets):
    pix = {}
    for g, dx in glyphs_offsets:
        for (x, y), c in g.pixels.items():
            key = (x + dx, y)
            if key not in pix or c[:3] in ((208, 210, 216), (130, 229, 0)):
                pix[key] = c
    w = max(x for x, _ in pix) + 1
    return Glyph(pix, w, 0)


def fishing_font():
    en, hu = sheet(ASSET, "en"), sheet(ASSET, "hu-HU")
    f = {}
    for img, spec in [(en, [(1334, 1351, ["Click to", "raise bar"], FISH_W), (1353, 1371, ["Release to", "lower bar"], FISH_W),
                            (1373, 1392, ["Keep bar", "behind fish"], FISH_G)]),
                      (hu, [(1334, 1351, ["Kattintás:", "megnövel"], FISH_W), (1353, 1371, ["Elenged:", "lecsökkent"], FISH_W)])]:
        for top, bot, lines, ink in spec:
            for ch, g in harvest_lines(img, (648, top, 40, bot - top + 1), lines, ink).items():
                f.setdefault(ch, g)
    # shapes only: recolored per section later
    shape = {ch: Glyph({p: (WHITE if c[:3] in ((208, 210, 216), (130, 229, 0)) else c) for p, c in g.pixels.items()}, g.w, 0)
             for ch, g in f.items()}
    n = shape["n"]
    shape["m"] = union((n, 0), (n, n.w - 1))                    # two n's sharing a stem
    l = shape["l"]
    shape["L"] = Glyph({**l.pixels, (1, 0): WHITE, (2, 0): WHITE}, 3, 0)
    shape["v"] = Glyph({(0, -3): WHITE, (0, -2): WHITE, (2, -3): WHITE, (2, -2): WHITE,
                        (1, -1): WHITE, (1, 0): WHITE, (0, -1): (97, 103, 116, 255), (2, -1): (97, 103, 116, 255)}, 3, 0)
    return shape


def recolor(font, color):
    return {ch: Glyph({p: (color if c == WHITE else c) for p, c in g.pixels.items()}, g.w, 0) for ch, g in font.items()}


def fishing(p):
    font = fishing_font()
    rect = (648, 1334, 40, 60)
    # erase text in the three sections, not the divider rows (they share an edge color)
    img = blank(ASSET, rect, FISH_W | FISH_G, (648, 1334, 687, 1351), fill=(0, 10, 29, 255))
    for zone in [(648, 1353, 687, 1371), (648, 1373, 687, 1392)]:
        part = blank(ASSET, (648, zone[1], 40, zone[3] - zone[1] + 1), FISH_W | FISH_G, zone, fill=(0, 10, 29, 255))
        img.paste(part, 0, zone[1] - 1334)
    sections = [(WHITE, ["Klik: balk", "omhoog"], [1342, 1350]),
                (WHITE, ["Loslaten:", "omlaag"], [1362, 1370]),
                (GREEN, ["Leg de balk", "op de vis"], [1382, 1390])]
    for color, lines, bases in sections:
        f = recolor(font, color)
        for text, base in zip(lines, bases):
            placed, w = typeset(text, f, tracking=1, space=3)
            draw(img, placed, 668 - (w + 1) // 2 - rect[0], base - rect[1])
    p.add("vissen-uitleg.png", img, rect[0], rect[1])


def bits(rows, ink, soft):
    """Glyph transcribed from an official sprite: '#' ink, '+' soft edge; last row = baseline."""
    pix = {}
    for yy, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in "#+":
                pix[(x, yy - (len(rows) - 1))] = ink if ch == "#" else soft
    return Glyph(pix, max(len(r) for r in rows), 0)


def tags(img):
    """'NEW!' -> 'NIEUW' (orange tag) and 'DONE' -> 'KLAAR' (green tag), letters as in the
    official tags (N and U from Italian NUOVO, E and W from English, K from Hungarian KÉSZ,
    A from Italian FATTO, R from German FERTIG)."""
    o, g = (175, 58, 0, 255), (0, 38, 0, 255)
    orange = {"N": ["##.", "#.#", "#.#", "#.#", "#.#"], "I": ["#", "#", "#", "#", "#"],
              "E": ["###", "#..", "##.", "#..", "###"], "U": ["#.#", "#.#", "#.#", "#.#", "###"],
              "W": ["#...#", "#...#", "#.#.#", "#.#.#", ".#.#."]}
    green = {"K": ["#.#", "#.#", "##.", "#.#", "#.#"], "L": ["#..", "#..", "#..", "#..", "###"],
             "A": [".#.", "#.#", "###", "#.#", "#.#"], "R": ["###", "#.#", "##.", "#.#", "#.#"]}
    for word, font, ink, (x0, x1), text_color in [("NIEUW", orange, o, (318, 338), (175, 58, 0)),
                                                   ("KLAAR", green, g, (342, 362), (0, 38, 0))]:
        f = {k: bits(v, ink, ink) for k, v in font.items()}
        part = blank(ASSET, (x0, 412, x1 - x0 + 1, 5), {text_color})
        img.paste(part, x0, 412)
        placed, w = typeset(word, f, tracking=1)
        draw(img, placed, x0 + (x1 - x0 + 1 - w + 1) // 2, 416)


def slots(img):
    """Slot machine buttons: 'BET 10/100' -> 'WED 10/100', 'DONE' -> 'KLAAR'."""
    glyphs = {"W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", "+#.#+"],
              "E": ["##", "#.", "#.", "##", "#.", "#.", "##"],
              "D": ["##+", "#.#", "#.#", "#.#", "#.#", "#.#", "##+"],
              "1": ["#"] * 7,
              "0": ["+##+", "#..#", "#..#", "#..#", "#..#", "#..#", "+##+"],
              "K": ["#..#", "#..#", "#.#.", "##..", "#.#.", "#..#", "#..#"],
              "L": ["#..", "#..", "#..", "#..", "#..", "#..", "###"],
              "A": ["+#+", "#.#", "#.#", "###", "#.#", "#.#", "#.#"],
              "R": ["##+", "#.#", "#.#", "##.", "#.#", "#.#", "#.#"]}
    for word, top, bg, ink, soft, right in [("WED 10", 388, (216, 126, 0, 255), (68, 18, 28, 255), (177, 78, 5, 255), 471),
                                            ("WED 100", 401, (216, 76, 0, 255), (68, 18, 40, 255), (177, 38, 5, 255), 476),
                                            ("KLAAR", 414, (216, 126, 0, 255), (68, 18, 28, 255), (177, 78, 5, 255), 469)]:
        f = {k: bits(v, ink, soft) for k, v in glyphs.items()}
        for y in range(top, top + 7):
            for x in range(443, right + 1):
                img.set(x, y, bg)
        placed, w = typeset(word, f, tracking=1, space=4)
        draw(img, placed, 443 + (right - 443 + 1 - w) // 2, top + 6)


_composed = None


def composed():
    """The English Cursors sheet with all redrawn texts applied (cached)."""
    global _composed
    if _composed is None:
        from glyphs import Image
        en = sheet(ASSET)
        img = Image(en.w, en.h, bytes(en.px))
        p = Patches(ASSET)
        fishing(p)
        for _, part, (x, y, w, h) in p.items:
            img.paste(part, x, y)
        tags(img)
        slots(img)
        _composed = img
    return _composed


def area(x0, y0, x1, y1):
    return lambda: composed().crop(x0, y0, x1 - x0, y1 - y0)


# used by art_maps.py (keys are the official text areas of the sheet)
FIXES = {(644, 1328): area(644, 1328, 692, 1400), (440, 384): area(440, 384, 508, 436),
         (316, 408): area(316, 408, 364, 420)}
