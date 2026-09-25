"""One-time migration: upstream mod assets (whole-file Loads) -> source/nl/ (Dutch text only).

- dictionaries: kept per key; scripts are rebuilt on the current English structure and English
  'hard' atoms (IDs, commands, item lists) are copied into the Dutch text
- slash/caret data: only the text fields are kept
- anything that can't be fixed automatically is listed in review/migration.md
"""
import os
import re

from paths import LEGACY, SOURCE, ROOT, load_json, save_json, vanilla
from textfmt import (FIELD_ASSETS, CARET_ASSETS, LIST_ASSETS, field_indexes, is_script_asset, is_script,
                     reskeleton_script, repair_hard_atoms, soft_signature)

report = {"dropped": [], "script": [], "hard": [], "soft": [], "fields": [], "fixed_script": 0, "fixed_hard": 0}


def legacy_assets():
    for root, _, files in os.walk(LEGACY):
        for fn in files:
            if fn.endswith(".json"):
                yield os.path.relpath(os.path.join(root, fn), LEGACY)[:-5].replace(os.sep, "/")


def migrate_dict(asset, en, nl):
    out = {}
    for k, v in nl.items():
        if k not in en:
            report["dropped"].append(f"{asset}: {k}")
            continue
        e = en[k]
        if not isinstance(v, str) or e is None:
            continue
        if is_script_asset(asset) and is_script(e):
            if v == e:
                out[k] = v
                continue
            r = reskeleton_script(e, v)
            if r is None:
                report["script"].append((asset, k))
                out[k] = v
                continue
            if r != v:
                report["fixed_script"] += 1
            v = r
        elif v == e and not re.search(r"[A-Za-z]{2,}", e):
            continue    # nothing to translate
        fixed, problems = repair_hard_atoms(e, v)
        if problems:
            report["hard"].append((asset, k, problems))
        elif fixed != v:
            report["fixed_hard"] += 1
        v = fixed
        if soft_signature(e) != soft_signature(v):
            report["soft"].append((asset, k))
        out[k] = v
    return out


def migrate_fields(asset, en, nl, sep, indexes_for):
    out = {}
    for k, e in en.items():
        if k not in nl:
            continue
        idx = indexes_for(k)
        if not idx:
            continue
        a, b = e.split(sep), nl[k].split(sep)
        if len(a) != len(b):
            report["fields"].append(f"{asset}: {k} (en {len(a)} fields, nl {len(b)})")
            continue
        fields = {str(i): b[i] for i in idx if i < len(b) and a[i]}
        if fields:
            out[k] = fields
    return out


def migrate_list(en, nl):
    """Map English lines to Dutch lines by aligning the two lists."""
    import difflib
    mapping = {}
    sm = difflib.SequenceMatcher(a=en, b=nl, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "replace" and i2 - i1 == j2 - j1:
            for e, n in zip(en[i1:i2], nl[j1:j2]):
                if e != n:
                    mapping[e] = n
        elif tag != "equal":
            report["dropped"].append(f"credits: unaligned {tag} en{en[i1:i2]} nl{nl[j1:j2]}")
    return mapping


def main():
    n = 0
    for asset in sorted(legacy_assets()):
        nl = load_json(os.path.join(LEGACY, asset + ".json"))
        en = vanilla(asset)
        if asset in FIELD_ASSETS:
            data = migrate_fields(asset, en, nl, "/", lambda k, a=asset: field_indexes(a, k))
        elif asset in CARET_ASSETS:
            data = migrate_fields(asset, en, nl, "^", lambda k, a=asset: CARET_ASSETS[a])
        elif asset in LIST_ASSETS:
            data = migrate_list(en, nl)
        else:
            data = migrate_dict(asset, en, nl)
        save_json(os.path.join(SOURCE, "nl", asset + ".json"), data)
        n += 1

    lines = ["# Migratie-rapport", "",
             f"- {n} assets gemigreerd",
             f"- {report['fixed_script']} scripts automatisch op de huidige Engelse structuur gezet",
             f"- {report['fixed_hard']} teksten met gecorrigeerde ID's/commando's", ""]
    sections = [("Scripts met ander aantal tekstdelen (handmatig)", [f"{a}: {k}" for a, k in report["script"]]),
                ("Harde tokens wijken af (handmatig)", [f"{a}: {k} -> {', '.join(p)}" for a, k, p in report["hard"]]),
                ("Structuur van velden wijkt af", report["fields"]),
                ("Verwijderde sleutels (bestaan niet meer in het spel)", report["dropped"]),
                ("Zachte tokens wijken af (emoties/pagina's, ter controle)", [f"{a}: {k}" for a, k in report["soft"]])]
    for title, items in sections:
        lines += [f"## {title} ({len(items)})", ""] + [f"- `{i}`" for i in items] + [""]
    os.makedirs(os.path.join(ROOT, "review"), exist_ok=True)
    with open(os.path.join(ROOT, "review", "migration.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("\n".join(lines[:6]))
    for title, items in sections:
        print(f"{title}: {len(items)}")


if __name__ == "__main__":
    main()
