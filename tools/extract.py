"""Extract vanilla game content into vanilla/<lang>/ so the other tools can compare against it.

Text assets (string dicts and lists) become JSON, textures become PNG, structured data is kept as
raw decompressed bytes (.bin) so references like [LocalizedText ...] can still be scanned.
Run again after every game update.
"""
import os
import re
import sys
import time

from paths import CONTENT, VANILLA, LANGS, save_json
from xnb import read_xnb, write_png, unpremultiply

TEXT_DIRS = ["Strings", "Characters/Dialogue", "Data"]
# textures the mod translates (officially localized ones + the extra map sheets)
TEXTURES = [
    "LooseSprites/Billboard", "LooseSprites/ControllerMaps", "LooseSprites/Cursors",
    "LooseSprites/JojaCDForm", "LooseSprites/JunimoNote", "LooseSprites/LanguageButtons",
    "LooseSprites/yellowLettersLogo",
    "Maps/bathhouse_tiles", "Maps/coopTiles", "Maps/DesertTiles", "Maps/Festivals",
    "Maps/MovieTheaterJoja_TileSheet_international", "Maps/townInterior",
    "Minigames/Intro", "Minigames/jojacorps", "Minigames/TitleButtons", "Minigames/Xb1ProfileButton",
    "Maps/FishingDerbyTiles", "Maps/samshowtiles", "Maps/springobjects",
] + [f"Maps/{s}_{k}" for s in ("spring", "summer", "fall", "winter") for k in ("beach", "outdoorsTileSheet", "town")]
LOCALE = re.compile(r"\.(" + "|".join(LANGS) + r")$")


def export(src, dst_base):
    kind, val = read_xnb(src)
    if kind in ("dict", "list"):
        save_json(dst_base + ".json", val)
    elif kind == "texture":
        fmt, w, h, px = val
        if fmt == 0:
            os.makedirs(os.path.dirname(dst_base), exist_ok=True)
            write_png(dst_base + ".png", w, h, unpremultiply(px))
    else:
        os.makedirs(os.path.dirname(dst_base), exist_ok=True)
        with open(dst_base + ".bin", "wb") as f:
            f.write(val[1])
    return kind


def main():
    t = time.time()
    count = 0
    for sub in TEXT_DIRS:
        for root, _, files in os.walk(os.path.join(CONTENT, sub)):
            for fn in files:
                if not fn.endswith(".xnb"):
                    continue
                rel = os.path.relpath(os.path.join(root, fn), CONTENT)[:-4].replace(os.sep, "/")
                m = LOCALE.search(rel)
                lang = m.group(1) if m else "en"
                if lang not in ("en", "de-DE", "fr-FR"):   # two reference languages are enough for text
                    continue
                asset = LOCALE.sub("", rel)
                export(os.path.join(root, fn), os.path.join(VANILLA, lang, asset))
                count += 1
    for tex in TEXTURES:
        for lang in ["en"] + LANGS:
            src = os.path.join(CONTENT, tex + ("" if lang == "en" else "." + lang) + ".xnb")
            if os.path.exists(src):
                export(src, os.path.join(VANILLA, lang, tex))
                count += 1
    print(f"extracted {count} assets to {VANILLA} in {time.time() - t:.0f}s")


if __name__ == "__main__":
    sys.exit(main())
