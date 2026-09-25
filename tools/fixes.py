"""Automatic, idempotent fixes on source/ text.

- gender switches must be written ${male^female}$
- zero-width spaces are not in the game font (they render as '*')
- page breaks typed as #e# / #b# instead of #$e# / #$b#
- portrait emotions ($h, $s, ...) that the English has at the end of a page but the Dutch lost
"""
import collections
import os
import re
import sys

from paths import SOURCE, load_json, save_json, vanilla
from textfmt import FIELD_ASSETS, CARET_ASSETS, LIST_ASSETS, is_script_asset, is_script

GENDER = re.compile(r"(\$?)\{([^{}\d][^{}]*\^[^{}]*)\}(\$?)")
PAGE = re.compile(r"(#\$[bek]#)")
EMOTION_END = re.compile(r"(\$(?:[hsula]|neutral|\d+))\s*$")
DUP_EMOTION = re.compile(r"(\$(?:[hsula]|neutral|\d+))\.\1(?=$|#|\")")
COMPLEX = re.compile(r"\$q |\$r |\$query|\$action|%fork|\$y |\$d |\||\^|\$p |\$c ")
stats = collections.Counter()


def fix_text(s):
    s = GENDER.sub(lambda m: "${" + m.group(2) + "}$", s)
    s = s.replace("​", "")
    return s


def restore_emotions(en, nl):
    """Give each Dutch page the portrait emotion its English page ends with."""
    if COMPLEX.search(en) or COMPLEX.search(nl):
        return nl
    ep, np_ = PAGE.split(en), PAGE.split(nl)
    if len(ep) != len(np_) or ep[1::2] != np_[1::2]:
        return nl
    out = []
    for i, (e, n) in enumerate(zip(ep, np_)):
        if i % 2 == 0:
            me, mn = EMOTION_END.search(e), EMOTION_END.search(n)
            if me and not mn and n.strip():
                n = n.rstrip() + me.group(1)
                stats["emotion restored"] += 1
        out.append(n)
    return "".join(out)


def fix_entry(asset, key, value, en):
    value = fix_text(value)
    e = en.get(key) if isinstance(en, dict) else None
    if not isinstance(e, str):
        return value
    for sep in ("#$e#", "#$b#"):
        typo = sep.replace("$", "")
        if sep in e and typo in value:
            value = value.replace(typo, sep)
            stats["page break typo"] += 1
    dedup = DUP_EMOTION.sub(r"\1", value)
    if dedup != value:
        value = dedup
        stats["duplicated emotion"] += 1
    if not (is_script_asset(asset) and is_script(e)):
        value = restore_emotions(e, value)
    return value


def main():
    changed = 0
    for layer in ("nl", "polish"):
        base = os.path.join(SOURCE, layer)
        for root, _, files in os.walk(base):
            for fn in files:
                if not fn.endswith(".json") or fn.startswith("_"):
                    continue
                p = os.path.join(root, fn)
                asset = os.path.relpath(p, base)[:-5].replace(os.sep, "/")
                data = load_json(p)
                if asset in FIELD_ASSETS or asset in CARET_ASSETS or asset in LIST_ASSETS or not isinstance(data, dict):
                    new = {k: ({i: fix_text(t) for i, t in v.items()} if isinstance(v, dict) else v)
                           for k, v in data.items()} if isinstance(data, dict) else data
                else:
                    en = vanilla(asset)
                    new = {k: fix_entry(asset, k, v, en) if isinstance(v, str) else v for k, v in data.items()}
                if new != data:
                    save_json(p, new)
                    changed += 1
    print(changed, "files changed", dict(stats))


if __name__ == "__main__":
    sys.exit(main())
