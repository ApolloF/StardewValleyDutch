"""LooseSprites/Billboard: 'Hulp gevraagd' header, weekday tabs and Pierre's seed poster.

Everything else on the sheet stays the current game art (the old Dutch sheet was pre-1.6).
"""
import sys

from glyphs import harvest, typeset, draw, shrink_row
from artkit import sheet, blank, flip_v, bitmap, Patches

ASSET = "LooseSprites/Billboard"
HEAD_INK = {(51, 47, 37), (224, 176, 132)}
DAY_INK = {(14, 14, 14), (0, 0, 0), (224, 176, 132)}
POSTER_INK = {(87, 87, 87), (201, 149, 100)}


def header(p):
    s = lambda lang: sheet(ASSET, lang)
    area = (95, 33, 150, 25)
    en = harvest(s("en"), area, "Help Wanted", HEAD_INK, 51)
    # German/Spanish letters are drawn one row taller than English/Portuguese/Hungarian:
    # use the 9-row family and slim the German g (two plain side rows out of its bowl)
    de = harvest(s("de-DE"), area, "Aushilfe gesucht", HEAD_INK, 51)
    hu = harvest(s("hu-HU"), area, "Felhívás", HEAD_INK, 51)
    pt = harvest(s("pt-BR"), (82, 33, 175, 25), "Precisa-se de ajuda", HEAD_INK, 51)
    g = shrink_row(shrink_row(de["g"], -5), -5)
    font = {"H": en["H"], "u": pt["u"], "l": en["l"], "p": en["p"], "g": g, "e": en["e"],
            "v": hu["v"], "r": pt["r"], "a": en["a"], "d": en["d"]}
    placed, w = typeset("Hulp gevraagd", font, tracking=3, space=9)
    rect = (90, 33, 160, 26)
    img = blank(ASSET, rect, HEAD_INK, (95, 33, 249, 58))
    draw(img, placed, 172 - w // 2 - rect[0], 51 - rect[1])
    p.add("hulp-gevraagd.png", img, rect[0], rect[1])


def weekdays(p):
    de_img, fr_img = sheet(ASSET, "de-DE"), sheet(ASSET, "fr-FR")
    de = harvest(de_img, (41, 233, 219, 11), "MoDiMiDoFrSaSo", DAY_INK, 242)
    fr = harvest(fr_img, (41, 233, 219, 12), "LuMaMeJeVeSaDi", DAY_INK, 243)
    ink = (14, 14, 14, 255)
    font = {"M": de["M"], "a": de["a"], "D": de["D"], "i": de["i"], "o": de["o"], "r": de["r"],
            "V": fr["V"],
            "W": flip_v(de["M"]),           # a plain 1px M upside down is this font's W
            "Z": bitmap(["######", ".....#", "....#.", "...#..", "..#...", ".#....", "#.....", "######"], ink)}
    # the tab centers, taken from where the German labels sit
    centers = [52, 85, 117, 150, 181, 213, 244]
    rect = (41, 233, 219, 12)
    img = blank(ASSET, rect, DAY_INK, (41, 233, 259, 244))
    for label, cx in zip(["Ma", "Di", "Wo", "Do", "Vr", "Za", "Zo"], centers):
        placed, w = typeset(label, font, tracking=1, kerning={"Di": 1})
        draw(img, placed, cx - w // 2 - rect[0], 242 - rect[1])
    p.add("weekdagen.png", img, rect[0], rect[1])


def poster(p):
    s = lambda lang: sheet(ASSET, lang)
    lines = {
        "de-DE": [("hoher", (290, 147, 37, 8), 154), ("Güte!", (290, 157, 37, 9), 165),
                  ("Nur", (290, 174, 20, 6), 179), ("bei", (291, 182, 12, 6), 187)],
        "es-ES": [("¡Semillas", (290, 139, 37, 8), 145), ("de alta", (290, 147, 37, 7), 153),
                  ("calidad!", (290, 155, 37, 7), 161), ("Solo en", (290, 171, 37, 6), 176)],
        "tr-TR": [("Yalnızca", (290, 157, 37, 7), 163, [297]), ("Bulunur", (290, 177, 37, 8), 183)],
        "pt-BR": [("Sónaloja", (284, 168, 40, 10), 176)],
    }
    got = {}
    for lang, spec in lines.items():
        got[lang] = {}
        for text, rect, base, *split in spec:
            got[lang].update(harvest(s(lang), rect, text, POSTER_INK, base, split[0] if split else None))
    de, es, tr, pt = got["de-DE"], got["es-ES"], got["tr-TR"], got["pt-BR"]
    grey = (87, 87, 87, 255)
    font = {"B": tr["B"], "e": de["e"], "s": es["s"], "t": de["t"], "z": tr["z"], "a": es["a"],
            "d": es["d"], "n": es["n"], "!": de["!"], "l": es["l"], "i": de["i"], "j": pt["j"],
            "b": de["b"],
            # the one letter no official poster has: a capital A in the same 1px hand
            "A": bitmap([".##.", "#..#", "#..#", "####", "#..#", "#..#", "#..#"], grey)}
    rect = (291, 135, 36, 54)
    img = blank(ASSET, rect, POSTER_INK, (291, 135, 326, 179))
    low = blank(ASSET, (291, 180, 12, 9), POSTER_INK)
    img.paste(low, 0, 45)
    for text, x, base in [("Beste", 296, 146), ("zaden!", 295, 158), ("Alleen", 297, 177), ("bij", 292, 187)]:
        placed, _ = typeset(text, font, tracking=1)
        draw(img, placed, x - rect[0], base - rect[1])
    p.add("poster.png", img, rect[0], rect[1])


def main():
    p = Patches(ASSET)
    header(p)
    weekdays(p)
    poster(p)
    p.save()
    if "--preview" in sys.argv:
        p.preview([(84, 28, 176, 34), (270, 118, 64, 76), (38, 228, 226, 20)], scale=4)


if __name__ == "__main__":
    main()
