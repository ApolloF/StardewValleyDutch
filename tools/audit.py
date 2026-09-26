"""Quality checks on the Dutch text as the game will see it (vanilla + built patches).

usage: audit.py [classic|polished] [--all]    (writes review/audit-<edition>.md)

Errors break things in-game; warnings need a human look.
"""
import collections
import functools
import os
import re
import sys

from paths import ROOT, SOURCE, CONTENT, VANILLA, load_json, vanilla
from sim import simulate
from textfmt import (FIELD_ASSETS, CARET_ASSETS, LIST_ASSETS, field_indexes, is_script_asset, is_script,
                     script_texts, hard_atoms, soft_signature)
from xnb import read_spritefont_chars

PLACEHOLDER_TEXT = {"beschrijving", "naam", "description", "name", "todo", "tbd", "tekst", "text", "xxx"}
PH = re.compile(r"\{\d+\}")
GENDER_OK = re.compile(r"\$\{[^{}]*\}\$")
TOKEN = re.compile(r"%[a-z]+[a-z0-9_]*")
# dialogue tokens the game replaces (a Dutch line may use one the English line doesn't)
KNOWN_TOKENS = {"%adj", "%noun", "%place", "%spouse", "%name", "%farm", "%favorite", "%kid1", "%kid2", "%pet",
                "%firstnameletter", "%band", "%book", "%rival", "%time", "%year", "%season", "%fork", "%item",
                "%action", "%secretsanta", "%revealtaste", "%endearment", "%endearmentlower"}
BRACE = re.compile(r"[{}]")
NAMED = re.compile(r"\{[A-Za-z_]+(?::[A-Za-z_]+)?\}")    # special order tokens: {Greeting}, {Monster:LocalizedName}
# words a Dutch sentence can't end on; a text ending on one where the English ends properly was cut off
DANGLING = {"de", "het", "een", "van", "voor", "met", "naar", "om", "te", "aan", "bij", "en", "of", "maar", "dat",
            "die", "dit", "deze", "jou", "zijn", "hun", "dezelfde", "als", "wanneer", "door", "tot", "wordt", "zal",
            "moet", "waar", "wacht", "honderden", "een", "wonder", "redt", "the", "a", "and"}
END_OK = re.compile(r"[.!?…)\"'”»:;*~-]\s*$")


def cut_off(en_part, nl_part):
    """Why a Dutch text part looks cut off compared to its English counterpart (or None)."""
    e, n = en_part.strip(), nl_part.strip()
    if not e or not n:
        return None
    if n.count("(") != n.count(")") and e.count("(") == e.count(")"):
        return "haakjes niet gesloten"
    if re.search(r"\S  +\S", n) and not re.search(r"\S  +\S", e):
        return "dubbele spatie (woord weggevallen?)"
    if END_OK.search(e) and not END_OK.search(n):
        last = re.findall(r"[\wÀ-ÿ']+$", n)
        if last and last[0].lower() in DANGLING:
            return f"eindigt op '{last[0]}'"
    return None


def text_parts(asset, key, value):
    """Only the translatable parts of a value (no commands, IDs, internal names)."""
    if asset in FIELD_ASSETS:
        idx = field_indexes(asset, key)
        parts = value.split("/")
        return [parts[i] for i in idx if i < len(parts)]
    if asset in CARET_ASSETS:
        parts = value.split("^")
        return [parts[i] for i in CARET_ASSETS[asset]]
    if is_script_asset(asset) and is_script(value):
        return script_texts(value)
    if (is_script_asset(asset) and "/" in value) or value.startswith("!image"):
        return []    # command script / image reference without text
    out, pos = [], 0
    for a, b, name, _ in hard_atoms(value):
        out.append(value[pos:a]); pos = b
    out.append(value[pos:])
    return ["".join(out)]


@functools.lru_cache(maxsize=None)
def _lang_asset(lang, asset):
    path = os.path.join(VANILLA, lang, asset + ".json")
    data = load_json(path) if os.path.exists(path) else None
    return data if isinstance(data, dict) else {}


def allowed_placeholders(asset, key):
    allowed = set()
    for lang in ("en", "de-DE", "fr-FR"):
        v = _lang_asset(lang, asset).get(key)
        if isinstance(v, str):
            allowed |= set(PH.findall(v))
    return allowed


def audit(edition):
    sim = simulate(edition)
    font = read_spritefont_chars(os.path.join(CONTENT, "Fonts", "SmallFont.xnb"))
    allow_en = set(load_json(os.path.join(SOURCE, "allow_english.json"), default=[]))
    glossary = load_json(os.path.join(SOURCE, "glossary.json"), default={"terms": []})["terms"]
    issues = collections.defaultdict(list)   # (level, check) -> [(asset, key, detail)]

    def add(level, check, asset, key, detail=""):
        issues[(level, check)].append((asset, key, detail))

    for asset, data in sorted(sim.items()):
        if asset in LIST_ASSETS:
            continue
        en = vanilla(asset)
        for key, ev in en.items():
            nv = data.get(key)
            if not isinstance(ev, str) or not isinstance(nv, str):
                continue
            nl_text = text_parts(asset, key, nv)
            en_text = text_parts(asset, key, ev)
            joined = " ".join(nl_text)
            # --- errors
            if asset not in FIELD_ASSETS and asset not in CARET_ASSETS:
                ph = set(PH.findall(nv))
                if not ph <= allowed_placeholders(asset, key) | set(PH.findall(ev)):
                    add("E", "placeholder niet door het spel gevuld", asset, key, f"{sorted(ph)} in: {nv[:90]}")
                stripped = PH.sub("", GENDER_OK.sub("", nv))
                if BRACE.search(stripped) and not BRACE.search(PH.sub("", GENDER_OK.sub("", ev))):
                    add("E", "losse { of } (kapotte ${..^..}$ of string.Format)", asset, key, nv[:90])
                if is_script_asset(asset) and is_script(ev):
                    if len(script_texts(ev)) != len(script_texts(nv)):
                        add("E", "script: aantal tekstdelen wijkt af", asset, key)
                else:
                    ea = collections.Counter((n, t) for _, _, n, t in hard_atoms(ev) if n != "placeholder")
                    na = collections.Counter((n, t) for _, _, n, t in hard_atoms(nv) if n != "placeholder")
                    if ea != na:
                        add("E", "commando's/ID's wijken af van Engels", asset, key, f"en {dict(ea)} nl {dict(na)}")
            bad_named = set(NAMED.findall(nv)) - set(NAMED.findall(ev))
            if bad_named:
                add("E", "onbekend {token} (het spel vult het niet in)", asset, key, " ".join(sorted(bad_named)))
            if "$y '" in ev and ev.count("_") != nv.count("_"):
                add("E", "keuzevraag ($y): aantal antwoorden wijkt af", asset, key, f"en {ev.count('_')} nl {nv.count('_')}")
            bad_tokens = set(TOKEN.findall(nv)) - set(TOKEN.findall(ev)) - KNOWN_TOKENS
            if bad_tokens and nv != ev:
                add("E", "onbekende %token (vertaald of kapot)", asset, key, " ".join(sorted(bad_tokens)))
            for t in nl_text:
                low = t.strip().lower().rstrip(".")
                if low in PLACEHOLDER_TEXT and ev.strip().lower().rstrip(".") not in PLACEHOLDER_TEXT:
                    add("E", "plaatshouder-tekst", asset, key, t)
            if not joined.strip() and " ".join(en_text).strip() and not PH.search(nv):
                add("E", "lege tekst", asset, key, ev[:80])
            bad = sorted({c for c in joined if c not in font and c not in "\n\r\t"})
            if bad:
                add("E", "teken ontbreekt in het lettertype", asset, key, " ".join(f"U+{ord(c):04X}" for c in bad))
            # --- warnings
            if nv == ev and re.search(r"[A-Za-z]{3,}", " ".join(en_text)) and f"{asset}:{key}" not in allow_en:
                add("W", "nog Engels", asset, key, ev[:90])
            elen, nlen = len(" ".join(en_text)), len(joined)
            if elen > 40 and nlen < 0.4 * elen:
                add("W", "mogelijk afgekapt", asset, key, joined[:90])
            plain = asset not in FIELD_ASSETS and asset not in CARET_ASSETS and not (is_script_asset(asset) and is_script(ev))
            pairs = [(ev, nv)] if plain else list(zip(en_text, nl_text)) if len(en_text) == len(nl_text) else []
            if pairs:
                for ep, np_ in pairs:
                    why = cut_off(ep, np_)
                    if why:
                        add("E", "zin afgebroken", asset, key, f"{why}: …{np_.strip()[-70:]}")
                        break
            if soft_signature(ev) != soft_signature(nv) and nv != ev:
                add("W", "emoties/paginering anders dan Engels", asset, key)
            for term in glossary:
                for bad_form in term.get("avoid", []):
                    if re.search(r"(?<![\w-])" + re.escape(bad_form) + r"(?![\w-])", joined):
                        add("W", "terminologie", asset, key, f"'{bad_form}' -> '{term['nl'][0]}'")
        missing = [k for k in en if k not in data]
        for k in missing:
            add("W", "sleutel ontbreekt in vertaling", asset, k)

    # text assets the game has but the mod doesn't touch at all
    for root, _, files in os.walk(os.path.join(VANILLA, "en", "Strings")):
        for fn in files:
            asset = os.path.relpath(os.path.join(root, fn), os.path.join(VANILLA, "en"))[:-5].replace(os.sep, "/")
            if fn.endswith(".json") and asset not in sim:
                add("E", "tekstbestand helemaal niet vertaald", asset, "*", f"{len(load_json(os.path.join(root, fn)))} teksten")
    return issues


def report(edition, issues, show_all=False):
    lines = [f"# Audit: {edition}", ""]
    total = collections.Counter()
    for (level, check), items in sorted(issues.items()):
        total[level] += len(items)
        lines.append(f"## [{level}] {check} ({len(items)})")
        lines += [f"- `{a}:{k}` {d}" for a, k, d in items[: None if show_all else 300]]
        lines.append("")
    os.makedirs(os.path.join(ROOT, "review"), exist_ok=True)
    with open(os.path.join(ROOT, "review", f"audit-{edition}.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"{edition}: {total['E']} errors, {total['W']} warnings")
    for (level, check), items in sorted(issues.items()):
        print(f"  [{level}] {len(items):5}  {check}")
    return total["E"]


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    eds = args or ["classic", "polished"]
    errors = sum(report(e, audit(e), "--all" in sys.argv) for e in eds)
    sys.exit(1 if errors else 0)
