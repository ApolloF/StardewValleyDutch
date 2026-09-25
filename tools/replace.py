"""Targeted substring replacements in source text, each asserted to match.

usage: replace.py <edits.json> [layer]

edits.json: [["Asset/Name", "key", "old text", "new text"], ...]
Use key "*" to replace in every entry of the asset (then 'old' must occur at least once).
"""
import os
import sys

from paths import SOURCE, load_json, save_json


def run(edits, layer="nl"):
    cache = {}
    failed = []
    for asset, key, old, new in edits:
        path = os.path.join(SOURCE, layer, asset + ".json")
        data = cache.setdefault(path, load_json(path, default={}))
        base = load_json(os.path.join(SOURCE, "nl", asset + ".json"), default={}) if layer != "nl" else data
        keys = list(dict.fromkeys([*base, *data])) if key == "*" else [key]
        hits = 0
        for k in keys:
            k, _, idx = k.partition("#")    # "key#idx" addresses one field of a slash-delimited entry
            v = data.get(k, base.get(k))    # an override layer starts from the classic text
            if idx:
                v = {**base.get(k, {}), **data.get(k, {})}.get(idx)
            if not isinstance(v, str):
                continue
            n = v.count(old)
            if key != "*" and n != 1:
                break
            if n:
                if idx:
                    data.setdefault(k, {})[idx] = v.replace(old, new)
                else:
                    data[k] = v.replace(old, new)
                hits += n
        if hits == 0 or (key != "*" and hits != 1):
            failed.append((asset, key, old[:60], hits))
    for path, data in cache.items():
        save_json(path, data)
    for f in failed:
        print("NOT APPLIED:", f)
    print(len(edits) - len(failed), "of", len(edits), "edits applied")
    return not failed


if __name__ == "__main__":
    ok = run(load_json(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else "nl")
    sys.exit(0 if ok else 1)
