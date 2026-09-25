"""Automatic, idempotent fixes on source/ text.

- gender switches must be written ${male^female}$
- zero-width spaces are not in the game font (they render as '*')
"""
import os
import re
import sys

from paths import SOURCE, load_json, save_json

GENDER = re.compile(r"(\$?)\{([^{}\d][^{}]*\^[^{}]*)\}(\$?)")


def fix_text(s):
    s = GENDER.sub(lambda m: "${" + m.group(2) + "}$", s)
    s = s.replace("​", "")
    return s


def walk(v):
    if isinstance(v, str):
        return fix_text(v)
    if isinstance(v, dict):
        return {k: walk(x) for k, x in v.items()}
    if isinstance(v, list):
        return [walk(x) for x in v]
    return v


def main():
    changed = 0
    for layer in ("nl", "polish"):
        base = os.path.join(SOURCE, layer)
        for root, _, files in os.walk(base):
            for fn in files:
                if not fn.endswith(".json"):
                    continue
                p = os.path.join(root, fn)
                data = load_json(p)
                new = walk(data)
                if new != data:
                    save_json(p, new)
                    changed += 1
                    print("fixed", os.path.relpath(p, SOURCE))
    print(changed, "files changed")


if __name__ == "__main__":
    sys.exit(main())
