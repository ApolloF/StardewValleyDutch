"""List where item names renamed in the polish layer still appear under their classic name in other texts.

usage: renames.py [Asset ...]    (default: all polished item assets)
"""
import os
import re
import sys

from paths import SOURCE, load_json
from worklist import current

ITEM_ASSETS = ["Strings/Objects", "Strings/BigCraftables", "Strings/Furniture", "Strings/Weapons", "Strings/Tools",
               "Strings/Shirts", "Strings/Pants"]


def all_texts():
    """(asset, key, text) for every classic-layer text, with the polish layer applied on top."""
    root = os.path.join(SOURCE, "nl")
    for dirpath, _, files in os.walk(root):
        for fn in files:
            if not fn.endswith(".json"):
                continue
            asset = os.path.relpath(os.path.join(dirpath, fn), root)[:-5].replace(os.sep, "/")
            for key, value in current(asset).items():
                if isinstance(value, dict):
                    for idx, text in value.items():
                        yield asset, f"{key}#{idx}", text
                elif isinstance(value, str):
                    yield asset, key, value


def renames(assets):
    out = []
    for asset in assets:
        classic = load_json(os.path.join(SOURCE, "nl", asset + ".json"), default={})
        polish = load_json(os.path.join(SOURCE, "polish", asset + ".json"), default={})
        for key, new in polish.items():
            old = classic.get(key)
            if key.endswith("_Name") and isinstance(old, str) and old.strip() and old != new and len(old) > 3:
                out.append((asset, key, old.strip(), new))
    return out


if __name__ == "__main__":
    assets = sys.argv[1:] or ITEM_ASSETS
    texts = list(all_texts())
    for asset, key, old, new in renames(assets):
        pat = re.compile(r"(?<![\w-])" + re.escape(old) + r"(?![\w-])", re.I)
        hits = [(a, k, t) for a, k, t in texts if (a, k) != (asset, key) and not k.endswith("_Name") and pat.search(t)]
        if hits:
            print(f"== {old!r} -> {new!r}  ({key}, {len(hits)} hits)")
            for a, k, t in hits[:6]:
                m = pat.search(t)
                print(f"     {a}:{k}  …{t[max(0, m.start() - 40):m.end() + 30]!r}")
