"""Compose the Dutch title-screen labels from the game's own hand-drawn letters.

Every letter is cut from an official translation of Minigames/TitleButtons (same brush, same size
class), so NIEUW / LADEN / AFSLUITEN / TERUG / 'Ontwikkeld door' look like ConcernedApe drew them.
Only the label areas are patched; the rest of the sheet stays the current game art.

usage: titlescreen.py [--preview]
"""
import collections
import os
import sys

from paths import ART, LATIN_LANGS, load_json, save_json
from glyphs import Image, Glyph
from xnb import write_png

SHEET = "Minigames/TitleButtons"
LANGS = ["en"] + LATIN_LANGS
RED = {(206, 82, 82), (219, 128, 83)}
WHITE = {(254, 254, 255)}
OUT_DIR = os.path.join(ART, "patches", "Minigames", "TitleButtons")


def sheet(lang="en"):
    return Image.sheet(SHEET, lang)


def cut(lang, x0, x1, y0, y1, colors):
    """Glyph from a sheet box; coordinates relative to (x0, y1) so glyphs align on their bottom row."""
    img = sheet(lang)
    pix = {}
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            c = img.get(x, y)
            if c[:3] in colors:
                pix[(x - x0, y - y1)] = c
    return Glyph(pix, x1 - x0 + 1, y1 - y0 + 1)


def keep(g, pred):
    return Glyph({p: c for p, c in g.pixels.items() if pred(*p)}, g.w, g.h)


def stretch_row(g, row):
    """Make a glyph one pixel taller by repeating one row (row is relative, <= 0)."""
    pix = {}
    for (x, y), c in g.pixels.items():
        if y <= row:
            pix[(x, y - 1)] = c
        if y >= row:
            pix[(x, y)] = c
    return Glyph(pix, g.w, g.h + 1)


def drop_columns(g, cols):
    """Make a glyph narrower by removing whole columns (keeps the brush strokes intact)."""
    cols = sorted(cols)
    pix = {}
    for (x, y), c in g.pixels.items():
        if x in cols:
            continue
        pix[(x - sum(1 for k in cols if k < x), y)] = c
    return Glyph(pix, g.w - len(cols), g.h)


def bottom_aligned(g):
    """Shift a glyph so its lowest pixel sits on row 0 (the baseline)."""
    low = max(y for _, y in g.pixels)
    return Glyph({(x, y - low): c for (x, y), c in g.pixels.items()}, g.w, g.h)


def mirror_right_half(g, axis):
    """Symmetric glyph built from the part right of 'axis' (used to turn a D into an O)."""
    pix = {}
    for (x, y), c in g.pixels.items():
        if x >= axis:
            pix[(x, y)] = c
            pix[(2 * axis - x, y)] = c
    return Glyph(pix, g.w, g.h)


def width_of(g):
    xs = [x for x, _ in g.pixels]
    return (min(xs), max(xs)) if xs else (0, -1)


def layout(glyphs, gap=1, space=4, gaps=None):
    """[(glyph, x_offset, dy)] for a word; None in the list is a space; gaps overrides per boundary."""
    placed, x = [], 0
    for n, item in enumerate(glyphs):
        if item is None:
            x += space
            continue
        g, dy = item if isinstance(item, tuple) else (item, 0)
        g = bottom_aligned(g)
        lo, hi = width_of(g)
        placed.append((g, x - lo, dy))
        x += hi - lo + 1 + (gaps[n] if gaps and n < len(gaps) else gap)
    return placed, x - (gaps[-1] if gaps and len(gaps) >= len(glyphs) else gap)


def blank(rect, text_colors, text_zone):
    """Background of rect with all text removed: per pixel, the most common non-text value across
    the official sheets (text sits in different places per language, the art is identical)."""
    x0, y0, w, h = rect
    zx0, zy0, zx1, zy1 = text_zone
    out = sheet("en").crop(x0, y0, w, h)
    sheets = [sheet(l) for l in LANGS]
    for y in range(max(y0, zy0), min(y0 + h, zy1 + 1)):
        for x in range(max(x0, zx0), min(x0 + w, zx1 + 1)):
            votes = collections.Counter(s.get(x, y) for s in sheets if s.get(x, y)[:3] not in text_colors)
            if votes:
                out.set(x - x0, y - y0, votes.most_common(1)[0][0])
    return out


def stamp(img, placed, x, base_y):
    for g, gx, dy in placed:
        for (px, py), c in g.pixels.items():
            img.set(x + gx + px, base_y + dy + py, c)


def color_map(src_rect, dst_offset):
    """Normal -> hover colors, learned from the English sheet."""
    img = sheet("en")
    x0, y0, w, h = src_rect
    m = {}
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            a, b = img.get(x, y), img.get(x, y + dst_offset)
            if a[3] and b[3]:
                m.setdefault(a, b)
    return m


def recolor(img, mapping):
    out = Image(img.w, img.h, bytes(img.px))
    for y in range(img.h):
        for x in range(img.w):
            c = img.get(x, y)
            if c[3]:
                out.set(x, y, mapping.get(c, c))
    return out


# ------------------------------------------------------------------ letters
def big():
    # the narrow big letters that Italian (NUOVO) and Hungarian (KILÉP) use to fit five letters
    return {
        "N": cut("it-IT", 5, 19, 200, 219, RED),
        "U": cut("it-IT", 21, 28, 199, 219, RED),
        "I": cut("hu-HU", 245, 248, 199, 219, RED),
        "E": cut("hu-HU", 262, 271, 204, 219, RED),
        # English W, three columns narrower so the five letters fit like NUOVO does
        "W": drop_columns(cut("en", 43, 62, 199, 219, RED), [4, 10, 15]),
    }


def small():
    e = cut("de-DE", 238, 243, 204, 215, RED)
    l = cut("de-DE", 251, 254, 204, 215, RED)
    return {
        "A": cut("de-DE", 256, 261, 204, 215, RED),
        "E": e,
        # F: the E without its lower arm
        "F": keep(e, lambda x, y: not (y in (-3, -2) and x >= 2)),
        "S": cut("de-DE", 263, 267, 204, 215, RED),
        "L": l,
        # I: the stem of the L
        "I": keep(l, lambda x, y: x <= 1),
        "U": stretch_row(cut("es-ES", 24, 29, 198, 208, RED), -4),
        "T": cut("es-ES", 33, 38, 210, 220, RED),
        "N": cut("de-DE", 279, 285, 204, 215, RED),
    }


def back_letters():
    i = cut("tr-TR", 335, 340, 262, 271, RED)          # İ without its dot: rows y=-9..0
    stem = {x for (x, y) in i.pixels if y == -4}
    return {
        # T: the İ's top bar plus its stem, bottom serif removed
        "T": keep(i, lambda x, y: y <= -8 or x in stem),
        "E": cut("tr-TR", 318, 323, 259, 272, RED),
        "R": cut("tr-TR", 326, 332, 259, 272, RED),
        "U": stretch_row(cut("fr-FR", 333, 337, 259, 272, RED), -5),
        "G": cut("tr-TR", 308, 315, 259, 272, RED),
    }


def dev_letters(bold):
    if not bold:
        d = cut("en", 184, 190, 318, 331, WHITE)
        return {
            "O": mirror_right_half(d, 3),
            "n": cut("de-DE", 193, 197, 318, 331, WHITE), "t": cut("de-DE", 199, 202, 318, 331, WHITE),
            "w": cut("de-DE", 205, 212, 318, 331, WHITE), "i": cut("de-DE", 215, 215, 318, 331, WHITE),
            "k": cut("de-DE", 225, 228, 318, 331, WHITE), "e": cut("de-DE", 230, 234, 318, 331, WHITE),
            "l": cut("de-DE", 237, 237, 318, 331, WHITE), "d": cut("en", 238, 243, 318, 331, WHITE),
            "o": cut("en", 217, 221, 318, 331, WHITE), "r": cut("it-IT", 201, 205, 318, 331, WHITE),
        }
    d = cut("en", 295, 301, 318, 332, WHITE)
    return {
        "O": mirror_right_half(d, 3),
        "n": cut("de-DE", 305, 309, 318, 332, WHITE), "t": cut("de-DE", 311, 314, 318, 332, WHITE),
        "w": cut("de-DE", 317, 324, 318, 332, WHITE), "i": cut("de-DE", 327, 327, 318, 332, WHITE),
        "k": cut("de-DE", 337, 340, 318, 332, WHITE), "e": cut("de-DE", 342, 346, 318, 332, WHITE),
        "l": cut("de-DE", 349, 349, 318, 332, WHITE), "d": cut("en", 349, 355, 318, 332, WHITE),
        "o": cut("en", 328, 332, 318, 332, WHITE), "r": (cut("it-IT", 312, 316, 318, 332, WHITE), 1),
    }


def word(letters, text):
    return [None if ch == " " else letters[ch] for ch in text]


# ------------------------------------------------------------------ build
BUTTON_W, BUTTON_H, HOVER_DY = 74, 58, 58


def button(index, text_glyphs, base_y, gap=1, gaps=None):
    """Normal+hover image (74x116) for big button #index with the given word."""
    rect = (index * BUTTON_W, 187, BUTTON_W, BUTTON_H)
    zone = (index * BUTTON_W + 5, 197, index * BUTTON_W + 64, 221)
    img = blank(rect, RED, zone)
    placed, w = layout(text_glyphs, gap, gaps=gaps)
    x = 5 + (60 - w) // 2
    stamp(img, placed, x, base_y - 187)
    hover = recolor(img, color_map(rect, HOVER_DY))
    both = Image(BUTTON_W, BUTTON_H * 2, bytes(BUTTON_W * BUTTON_H * 2 * 4))
    both.paste(img, 0, 0)
    both.paste(hover, 0, BUTTON_H)
    return both


def back_button():
    rect = (296, 252, 67, 27)
    img = blank(rect, RED, (303, 258, 347, 273))
    placed, w = layout(word(back_letters(), "TERUG"), 2)
    x = 305 - 296 + (40 - w) // 2
    stamp(img, placed, x, 271 - 252)
    hover = recolor(img, color_map(rect, 27))
    both = Image(67, 54, bytes(67 * 54 * 4))
    both.paste(img, 0, 0)
    both.paste(hover, 0, 27)
    return both


def dev_label(bold):
    rect = (283, 316, 110, 18) if bold else (171, 316, 112, 18)
    img = blank(rect, WHITE, (rect[0], rect[1], rect[0] + rect[2] - 1, rect[1] + rect[3] - 1))
    placed, w = layout(word(dev_letters(bold), "Ontwikkeld door"), 2, 3)
    center = 338 if bold else 226
    ox, oy = center - w // 2 - rect[0], (329 if bold else 328) - 316
    stamp(img, placed, ox, oy)
    # decorative sparkles that now touch a letter would read as accents: paint them as sky
    text = {(ox + gx + px, oy + dy + py) for g, gx, dy in placed for (px, py) in g.pixels}
    sky = collections.Counter(img.get(x, y) for x in range(img.w) for y in range(img.h)
                              if (x, y) not in text).most_common(1)[0][0]
    for y in range(img.h):
        for x in range(img.w):
            if img.get(x, y)[:3] == (159, 182, 255) and any((x + dx, y + dy) in text
                                                           for dx in (-1, 0, 1) for dy in (-2, -1, 0, 1, 2)):
                img.set(x, y, img.get(x - 1, y) if (x - 1, y) not in text else sky)
    return img, rect


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    patches = [p for p in load_json(os.path.join(ART, "patches.json"), default=[]) if p["target"] != SHEET]
    items = []
    items.append(("nieuw.png", button(0, word(big(), "NIEUW"), 218, 1, gaps=[2, 2, 1, 1]), (0, 187, 74, 116)))
    de = sheet("de-DE")
    items.append(("laden.png", de.crop(74, 187, 74, 116), (74, 187, 74, 116)))
    items.append(("afsluiten.png", button(3, word(small(), "AFSLUITEN"), 214, 1), (222, 187, 74, 116)))
    items.append(("terug.png", back_button(), (296, 252, 67, 54)))
    for bold in (False, True):
        img, rect = dev_label(bold)
        items.append((f"ontwikkeld-door{'-hover' if bold else ''}.png", img, rect))
    for fn, img, area in items:
        write_png(os.path.join(OUT_DIR, fn), img.w, img.h, bytes(img.px))
        patches.append({"target": SHEET, "file": f"Minigames/TitleButtons/{fn}", "area": list(area)})
    save_json(os.path.join(ART, "patches.json"), patches)
    print(f"{len(items)} title screen patches written")
    if "--preview" in sys.argv:
        preview(items)


def preview(items, scale=4):
    """Side by side: current game sheet | old Dutch mod | new, for the patched area."""
    from images import read_png
    from paths import LEGACY
    new = sheet("en")
    for fn, img, (x, y, w, h) in items:
        new.paste(img, x, y)
    ow, oh, opx = read_png(os.path.join(LEGACY, "Minigames", "TitleButtons.png"))
    old = Image(ow, oh, opx)
    views = [sheet("en").crop(0, 187, 400, 150), old.crop(0, 187, 400, 150), new.crop(0, 187, 400, 150)]
    W, H = 400 * scale, (150 * scale + 8) * 3
    out = Image(W, H, b"\x30\x30\x30\xff" * (W * H))
    for n, v in enumerate(views):
        for yy in range(v.h):
            for xx in range(v.w):
                c = v.get(xx, yy)
                a = c[3] / 255
                col = (int(c[0] * a + 48 * (1 - a)), int(c[1] * a + 48 * (1 - a)), int(c[2] * a + 48 * (1 - a)), 255)
                for dy in range(scale):
                    for dx in range(scale):
                        out.set(xx * scale + dx, n * (150 * scale + 8) + yy * scale + dy, col)
    path = os.path.join(os.path.dirname(ART), "review", "titlescreen.png")
    write_png(path, out.w, out.h, bytes(out.px))
    print("preview:", path)


if __name__ == "__main__":
    main()
