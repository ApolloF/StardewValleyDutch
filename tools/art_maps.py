"""Map tilesheets and other textures whose Dutch signs from the old mod are kept.

Only the areas the official translations localize are patched (so every other tile stays the
current 1.6.15 art). Inside those areas the old mod's Dutch sign is used, unless it is listed in
SKIP (the English original is better) or FIX (redrawn here).
"""
import os
import sys

from paths import LEGACY
from glyphs import Image
from images import read_png
from regions import text_areas, load
from artkit import Patches

SEASONS = ("spring", "summer", "fall", "winter")
SHEETS = ([f"Maps/{s}_{k}" for s in SEASONS for k in ("town", "beach", "outdoorsTileSheet")]
          + ["Maps/Festivals", "Maps/DesertTiles", "Maps/bathhouse_tiles", "Maps/coopTiles",
             "Minigames/jojacorps", "Minigames/Intro", "Minigames/Xb1ProfileButton", "LooseSprites/JojaCDForm",
             "LooseSprites/ControllerMaps", "LooseSprites/Cursors", "Maps/townInterior",
             "LooseSprites/JunimoNote"])
# (sheet prefix, x, y): areas where the English original stays
SKIP = [("_town", 124, 272)]          # "Pierre's": Dutch keeps the apostrophe after a silent e


def old_sheet(asset):
    p = os.path.join(LEGACY, asset + ".png")
    return Image(*read_png(p)) if os.path.exists(p) else None


def differs(a, b, x0, y0, x1, y1):
    for y in range(y0, min(y1, a.h, b.h)):
        for x in range(x0, min(x1, a.w, b.w)):
            if a.get(x, y) != b.get(x, y):
                return True
    return False


def build(asset, fixes, whitelist=None):
    en, old = load(asset, "en"), old_sheet(asset)
    p = Patches(asset)
    for n, (x0, y0, x1, y1) in enumerate(text_areas(asset)):
        if whitelist is not None and (x0, y0) not in whitelist:
            continue
        if any(s in asset and (sx, sy) == (x0, y0) for s, sx, sy in SKIP):
            continue
        key = (x0, y0)
        if key in fixes:
            img = fixes[key]()
            if img is not None:
                p.add(f"sign-{x0}-{y0}.png", img, x0, y0)
            continue
        if old is None or not differs(en, old, x0, y0, x1, y1):
            continue
        crop = old.crop(x0, y0, x1 - x0, y1 - y0)
        # the old ControllerMaps painted opaque white where the game is transparent: keep the game's
        for y in range(crop.h):
            for x in range(crop.w):
                if en.get(x0 + x, y0 + y)[3] == 0 and crop.get(x, y) == (255, 255, 255, 255):
                    crop.set(x, y, (0, 0, 0, 0))
        p.add(f"sign-{x0}-{y0}.png", crop, x0, y0)
    p.save()
    return p


def main(only=None):
    from art_signs import FIXES, WHITELIST
    for asset in SHEETS:
        if only and asset not in only:
            continue
        p = build(asset, FIXES.get(asset, {}), WHITELIST.get(asset))
        if "--preview" in sys.argv and p.items:
            views = [(x - 2, y - 2, w + 4, h + 4) for _, _, (x, y, w, h) in p.items]
            p.preview(views, scale=3)


if __name__ == "__main__":
    main([a for a in sys.argv[1:] if not a.startswith("--")] or None)
