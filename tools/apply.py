"""Apply a batch of text changes to a source layer.

usage: apply.py <batch.json> [layer]      (layer defaults to 'nl'; use 'polish' for the polished edition)

batch.json: {"Strings/Objects": {"Key": "tekst", ...}, "Data/hats": {"61": {"1": "beschrijving"}}, ...}
A value of null removes the key from the layer.
"""
import os
import sys

from paths import SOURCE, load_json, save_json


def apply(batch, layer="nl"):
    n = 0
    for asset, entries in batch.items():
        path = os.path.join(SOURCE, layer, asset + ".json")
        data = load_json(path, default={})
        for k, v in entries.items():
            if v is None:
                data.pop(k, None)
            elif isinstance(v, dict) and isinstance(data.get(k), dict):
                data[k] = {**data[k], **v}
            else:
                data[k] = v
            n += 1
        save_json(path, data)
    return n


if __name__ == "__main__":
    batch = load_json(sys.argv[1])
    layer = sys.argv[2] if len(sys.argv) > 2 else "nl"
    print(apply(batch, layer), "entries applied to", layer)
