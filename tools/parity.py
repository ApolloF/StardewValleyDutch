"""Compare the simulated classic edition with the old (whole-file) Dutch mod.

Every difference must be intentional: gameplay fields now come from the game, English IDs/commands
were copied in, or a translation was fixed on purpose.
"""
import collections
import os
import sys

from paths import LEGACY, load_json, vanilla
from sim import simulate
from textfmt import FIELD_ASSETS, CARET_ASSETS, LIST_ASSETS, field_indexes


def main(verbose=False):
    sim = simulate("classic")
    counts = collections.Counter()
    samples = collections.defaultdict(list)
    for root, _, files in os.walk(LEGACY):
        for fn in files:
            if not fn.endswith(".json"):
                continue
            asset = os.path.relpath(os.path.join(root, fn), LEGACY)[:-5].replace(os.sep, "/")
            old = load_json(os.path.join(root, fn))
            new = sim.get(asset)
            en = vanilla(asset)
            if asset in LIST_ASSETS:
                continue
            for k in en:
                o, n = old.get(k), (new or en).get(k)
                if o == n:
                    continue
                if asset in FIELD_ASSETS or asset in CARET_ASSETS:
                    sep = "^" if asset in CARET_ASSETS else "/"
                    idx = CARET_ASSETS.get(asset) or field_indexes(asset, k)
                    ot, nt = o.split(sep), n.split(sep)
                    if all(ot[i] == nt[i] for i in idx if i < len(nt)):
                        counts["gameplay fields from game (intended)"] += 1
                        continue
                    kind = "text field differs"
                elif o == en[k]:
                    kind = "old was English, now omitted (same result)"
                else:
                    kind = "text differs"
                counts[kind] += 1
                samples[kind].append((asset, k, o, n))
    for kind, c in counts.most_common():
        print(f"{c:6}  {kind}")
        if kind.startswith(("text", "old")) or verbose:
            for asset, k, o, n in samples[kind][:40 if verbose else 6]:
                print(f"         {asset}:{k}\n            old: {str(o)[:150]}\n            new: {str(n)[:150]}")


if __name__ == "__main__":
    main("-v" in sys.argv)
