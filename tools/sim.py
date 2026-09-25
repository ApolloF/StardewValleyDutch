"""Simulate what the game sees in Dutch: vanilla English data + the built patches of an edition."""
import copy
import os

from paths import BUILD, load_json, vanilla
from build import EDITIONS


def simulate(edition):
    """asset -> final data (dict or list) for every text asset the edition patches."""
    root = os.path.join(BUILD, EDITIONS[edition]["folder"])
    content = load_json(os.path.join(root, "content.json"))
    result = {}
    for inc in content["Changes"]:
        if inc["Action"] != "Include":
            continue
        for p in load_json(os.path.join(root, inc["FromFile"]))["Changes"]:
            asset = p["Target"]
            if p["Action"] == "Load" and p["FromFile"].endswith(".json"):
                result[asset] = load_json(os.path.join(root, p["FromFile"]))
                continue
            if p["Action"] != "EditData":
                continue
            data = result.get(asset)
            if data is None:
                data = copy.deepcopy(vanilla(asset))
            for k, v in (p.get("Entries") or {}).items():
                data[k] = v
            for k, fields in (p.get("Fields") or {}).items():
                parts = data[k].split("/")
                for i, t in fields.items():
                    parts[int(i)] = t
                data[k] = "/".join(parts)
            result[asset] = data
    return result
