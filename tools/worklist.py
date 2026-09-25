"""Print a chunk of an asset for the polish pass: key | English | current Dutch (polish layer wins).

usage: worklist.py <Asset/Name> <start> <count> [--fields]
"""
import os
import sys

from paths import SOURCE, load_json, vanilla
from textfmt import FIELD_ASSETS, field_indexes


def current(asset):
    nl = load_json(os.path.join(SOURCE, "nl", asset + ".json"), default={})
    pol = load_json(os.path.join(SOURCE, "polish", asset + ".json"), default={})
    out = dict(nl)
    for k, v in pol.items():
        out[k] = {**out.get(k, {}), **v} if isinstance(v, dict) else v
    return out


if __name__ == "__main__":
    asset, start, count = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    en, nl = vanilla(asset), current(asset)
    keys = list(en)[start:start + count]
    for k in keys:
        if asset in FIELD_ASSETS:
            parts = en[k].split("/")
            for i in field_indexes(asset, k):
                if i < len(parts) and parts[i]:
                    print(f"{k}#{i} | {parts[i]} | {nl.get(k, {}).get(str(i), '')}")
        else:
            print(f"{k} | {en[k]} | {nl.get(k, '')}")
    print(f"-- {start}..{start + len(keys) - 1} of {len(en)}")
