"""Build a Content Patcher mod folder from source/.

usage: build.py [classic|polished|all] [--install]

classic  = source/nl                       -> build/[CP] Stardew Valley Nederlands (Klassiek)
polished = source/nl + source/polish       -> build/[CP] Stardew Valley Nederlands
"""
import json
import os
import re
import shutil
import sys

from paths import SOURCE, BUILD, ART, MODS, load_json, save_json, vanilla
from textfmt import FIELD_ASSETS, CARET_ASSETS, LIST_ASSETS

VERSION = "2.0.1"
UNIQUE_ID = "JanFokke.StardewValleyDutch"      # unchanged: keeps the language setting and replaces the old mod
EDITIONS = {
    "polished": {"folder": "[CP] Stardew Valley Nederlands", "layers": ["nl", "polish"],
                 "desc": "Nederlandse vertaling van Stardew Valley, volledig opgepoetst."},
    "classic": {"folder": "[CP] Stardew Valley Nederlands (Klassiek)", "layers": ["nl"],
                "desc": "Nederlandse vertaling van Stardew Valley: de bekende vertaling, aangevuld en gerepareerd."},
}
GROUPS = [("Characters/Dialogue/", "Dialogen"), ("Strings/schedules/", "Dialogen"), ("Data/Events/", "Gebeurtenissen"),
          ("Data/Festivals/", "Festivals"), ("Strings/", "Teksten"), ("Data/", "Gegevens")]


def source_assets(layer):
    base = os.path.join(SOURCE, layer)
    for root, _, files in os.walk(base):
        for fn in files:
            if fn.endswith(".json") and not fn.startswith("_"):
                yield os.path.relpath(os.path.join(root, fn), base)[:-5].replace(os.sep, "/")


def merged_source(layers):
    """asset -> data, later layers override earlier ones per key (and per field)."""
    out = {}
    for layer in layers:
        for asset in source_assets(layer):
            data = load_json(os.path.join(SOURCE, layer, asset + ".json"))
            cur = out.setdefault(asset, {})
            for k, v in data.items():
                if isinstance(v, dict) and isinstance(cur.get(k), dict):
                    cur[k] = {**cur[k], **v}
                else:
                    cur[k] = v
    return out


def patch_for(asset, data):
    en = vanilla(asset)
    log = asset
    if asset in FIELD_ASSETS:
        fields = {k: {i: t for i, t in v.items()} for k, v in data.items() if k in en}
        return {"LogName": log, "Action": "EditData", "Target": asset, "Fields": fields}
    if asset in CARET_ASSETS:
        entries = {}
        for k, v in data.items():
            if k not in en:
                continue
            parts = en[k].split("^")
            for i, t in v.items():
                parts[int(i)] = t
            entries[k] = "^".join(parts)
        return {"LogName": log, "Action": "EditData", "Target": asset, "Entries": entries}
    if asset in LIST_ASSETS:
        return None   # handled as a Load of a generated file
    # keys the game looks up without English having them: per-ingredient names for flavored goods
    extra = re.compile(r"\w+_Flavored_\(O\)[\w.]+_Name") if asset == "Strings/Objects" else None
    entries = {k: v for k, v in data.items() if k in en or (extra and extra.fullmatch(k))}
    return {"LogName": log, "Action": "EditData", "Target": asset, "Entries": entries}


def group_of(asset):
    for prefix, name in GROUPS:
        if asset.startswith(prefix):
            return name
    return "Overig"


def build(edition, install=False):
    ed = EDITIONS[edition]
    out = os.path.join(BUILD, ed["folder"])
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "data"))
    os.makedirs(os.path.join(out, "assets"))
    src = merged_source(ed["layers"])
    lang = load_json(os.path.join(SOURCE, "language.json"))

    changes = [
        {"LogName": "Taal", "Action": "EditData", "Target": "Data/AdditionalLanguages",
         "Entries": {"{{ModId}}_Dutch": {**lang, "ID": "{{ModId}}_Dutch", "ButtonTexture": "Mods/{{ModId}}/Button"}}},
        {"LogName": "Taalknop", "Action": "Load", "Target": "Mods/{{ModId}}/Button", "FromFile": "assets/Button.png"},
    ]
    shutil.copy(os.path.join(ART, "Button.png"), os.path.join(out, "assets", "Button.png"))

    groups = {}
    for asset in sorted(src):
        if asset in LIST_ASSETS:
            mapping = src[asset]
            lst = [mapping.get(line, line) for line in vanilla(asset)]
            fn = "data/" + asset.replace("/", "_") + ".json"
            save_json(os.path.join(out, fn), lst)
            groups.setdefault("Teksten", []).append(
                {"LogName": asset, "Action": "Load", "Target": asset, "FromFile": fn})
            continue
        p = patch_for(asset, src[asset])
        if p and (p.get("Entries") or p.get("Fields")):
            groups.setdefault(group_of(asset), []).append(p)

    images = load_json(os.path.join(ART, "patches.json"), default=[])
    img_changes = []
    for img in images:
        rel = img["file"]
        dst = os.path.join(out, "assets", rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(os.path.join(ART, "patches", rel), dst)
        x, y, w, h = img["area"]
        img_changes.append({"LogName": f"{img['target']} {rel}", "Action": "EditImage", "Target": img["target"],
                            "FromFile": "assets/" + rel, "ToArea": {"X": x, "Y": y, "Width": w, "Height": h},
                            "PatchMode": img.get("mode", "Replace"), "Priority": "Early"})
    if img_changes:
        groups["Afbeeldingen"] = img_changes

    for name, patches in groups.items():
        fn = f"data/{name}.json"
        save_json(os.path.join(out, fn), {"Changes": patches})
        changes.append({"LogName": name, "Action": "Include", "FromFile": fn, "When": {"Language": "nl"}})

    save_json(os.path.join(out, "content.json"), {"Format": "2.9.0", "Changes": changes})
    save_json(os.path.join(out, "manifest.json"), {
        "Name": "Stardew Valley Nederlands" + (" (Klassiek)" if edition == "classic" else ""),
        "Author": "Spawk en JanFokke, bijgewerkt door rhansenne en Azelion",
        "Version": VERSION,
        "Description": ed["desc"],
        "UniqueID": UNIQUE_ID,
        "UpdateKeys": ["GitHub:janfokke/StardewValleyDutch", "Nexus:24290"],
        "ContentPackFor": {"UniqueID": "Pathoschild.ContentPatcher", "MinimumVersion": "2.9.0"},
    })
    n_entries = sum(len(p.get("Entries") or p.get("Fields") or {}) for ps in groups.values() for p in ps)
    print(f"{edition}: {out}  ({sum(len(p) for p in groups.values())} patches, {n_entries} entries, {len(img_changes)} images)")
    if install:
        dst = os.path.join(MODS, ed["folder"])
        for other in EDITIONS.values():      # only one edition may be installed at a time
            o = os.path.join(MODS, other["folder"])
            if os.path.exists(o):
                shutil.rmtree(o)
        shutil.copytree(out, dst)
        print("installed to", dst)
    return out


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    which = args[0] if args else "all"
    for e in (EDITIONS if which == "all" else [which]):
        build(e, install="--install" in sys.argv and which != "all")
