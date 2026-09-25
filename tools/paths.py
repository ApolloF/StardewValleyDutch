"""Shared locations for the tools. Override the game folder with the SDV_PATH environment variable."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = os.environ.get("SDV_PATH", r"C:\Program Files (x86)\Steam\steamapps\common\Stardew Valley")
CONTENT = os.path.join(GAME, "Content")
MODS = os.path.join(GAME, "Mods")

VANILLA = os.path.join(ROOT, "vanilla")          # extracted game data (gitignored)
SOURCE = os.path.join(ROOT, "source")            # Dutch text sources
ART = os.path.join(ROOT, "art")                  # glyphs and image patches
BUILD = os.path.join(ROOT, "build")              # generated mod folders (gitignored)
LEGACY = os.path.join(ROOT, "StardewValleyDutch", "assets")  # upstream mod assets

LANGS = ["de-DE", "es-ES", "fr-FR", "hu-HU", "it-IT", "ja-JP", "ko-KR", "pt-BR", "ru-RU", "tr-TR", "zh-CN"]
LATIN_LANGS = ["de-DE", "es-ES", "fr-FR", "hu-HU", "it-IT", "pt-BR", "tr-TR"]


def load_json(path, default=None):
    if default is not None and not os.path.exists(path):
        return default
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def vanilla(asset, lang="en"):
    """Load an extracted vanilla text asset, e.g. vanilla('Strings/Objects')."""
    return load_json(os.path.join(VANILLA, lang, asset + ".json"))
