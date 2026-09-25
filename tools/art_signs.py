"""Signs that are redrawn instead of taken from the old mod (used by art_maps.py)."""
from glyphs import harvest, typeset, draw, Glyph
from artkit import sheet, blank

SIGN_INK = {(81, 80, 84), (161, 161, 161)}


def keep(g, pred):
    return Glyph({p: c for p, c in g.pixels.items() if pred(*p)}, g.w, g.h)


def sewer_sign(season):
    """'SEWER' plate -> 'RIOOL' in the plate's own letters (R from SEWER, O from ÉGOUT,
    I and L cut from the stem and foot of the E)."""
    asset = f"Maps/{season}_town"

    def make():
        en_img = sheet("Maps/spring_town", "en")
        # the letters touch through their highlight columns, so cut them one by one
        r = harvest(en_img, (279, 10, 5, 10), "R", SIGN_INK, 18)["R"]
        e = harvest(en_img, (275, 10, 4, 10), "E", SIGN_INK, 18)["E"]
        o = harvest(sheet("Maps/spring_town", "pt-BR"), (280, 10, 6, 10), "O", SIGN_INK, 18)["O"]
        import collections
        cols = collections.Counter(x for x, _ in e.pixels)
        main = max(cols, key=lambda x: (cols[x], -x))          # the E's full-height stem
        stem = {main, main - 1} if main - 1 in cols else {main}  # plus its highlight column
        bottom = max(y for _, y in e.pixels if y <= 0)
        font = {"R": r, "O": o,
                "I": keep(e, lambda x, y: x in stem),
                "L": keep(e, lambda x, y: x in stem or y >= bottom - 1)}
        rect = (256, 8, 32, 12)
        # every season recolors the plate: learn spring -> season colors from the English sheets
        spring, here = sheet("Maps/spring_town", "en"), sheet(asset, "en")
        cmap = {}
        for y in range(rect[1], rect[1] + rect[3]):
            for x in range(rect[0], rect[0] + rect[2]):
                cmap.setdefault(spring.get(x, y), here.get(x, y))
        ink = {cmap[c][:3] for c in cmap if c[:3] in SIGN_INK}
        font = {k: g.recolor(cmap) for k, g in font.items()}
        img = blank(asset, rect, ink, (258, 9, 286, 19))
        placed, w = typeset("RIOOL", font, tracking=0)
        draw(img, placed, 272 - w // 2 - rect[0], 18 - rect[1])
        return img
    return make


FIXES = {f"Maps/{s}_town": {(256, 8): sewer_sign(s)} for s in ("spring", "summer", "fall", "winter")}


from art_cursors import FIXES as _cursors
FIXES["LooseSprites/Cursors"] = _cursors


def _bits(rows, ink, soft):
    pix = {}
    for yy, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in "#+":
                pix[(x, yy - (len(rows) - 1))] = ink if ch == "#" else soft
    return Glyph(pix, max(len(r) for r in rows), 0)


def te_koop():
    """Shop sign 'FOR SALE' -> 'TE KOOP' (T from Italian IN VENDITA, E and O from FOR SALE,
    P = the R of FOR without its leg, K in the same plain 1px hand)."""
    from glyphs import Image
    ink, soft, bg = (137, 117, 185, 255), (151, 146, 201, 255), (188, 190, 230, 255)
    f = {"T": _bits(["###", ".#.", ".#.", ".#.", ".#."], ink, soft),
         "E": _bits(["###", "#..", "##.", "#..", "###"], ink, soft),
         "K": _bits(["#.#", "#.#", "##.", "#.#", "#.#"], ink, soft),
         "O": _bits(["+#+", "#.#", "#.#", "#.#", "+#+"], ink, soft),
         "P": _bits(["##+", "#.#", "##.", "#..", "#.."], ink, soft)}
    en = sheet("Maps/townInterior")
    img = en.crop(368, 500, 32, 12)
    for y in range(504 - 500, 509 - 500):
        for x in range(0, 31):
            img.set(x, y, bg)
    placed, w = typeset("TE KOOP", f, tracking=1, space=3)
    draw(img, placed, 383 - w // 2 - 368, 508 - 500)
    return img


def kopen_button():
    """JunimoNote 'Kopen': the old mod's letters (German style) without the stray dot."""
    from art_maps import old_sheet
    img = old_sheet("LooseSprites/JunimoNote").crop(516, 288, 64, 16)
    for y in (297, 298, 299):
        img.set(524 - 516, y - 288, (244, 183, 68, 255))
    return img


FIXES["Maps/townInterior"] = {(368, 500): te_koop}
FIXES["LooseSprites/JunimoNote"] = {(516, 288): kopen_button}
# sheets where only these areas may come from the old mod (it carried old art elsewhere)
WHITELIST = {"Maps/townInterior": {(288, 768), (192, 944), (12, 1008), (368, 500)},
             "LooseSprites/JunimoNote": {(516, 288)}}
