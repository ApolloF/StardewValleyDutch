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
        data = cache.setdefault(path, load_json(path))
        keys = list(data) if key == "*" else [key]
        hits = 0
        for k in keys:
            v = data.get(k)
            if not isinstance(v, str):
                continue
            n = v.count(old)
            if key != "*" and n != 1:
                break
            if n:
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
