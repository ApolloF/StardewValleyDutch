"""Asset registry and helpers for the structure of Stardew text (event scripts, dialogue, mail).

The rule everywhere: the *current English* game data decides the structure (commands, item IDs,
question IDs...), the Dutch source only provides the words.
"""
import re

# ---------------------------------------------------------------- asset registry
# Slash-delimited data: only these field indexes are text. Everything else comes from the game.
FIELD_ASSETS = {
    "Data/hats": [1, 5],
    "Data/Boots": [1, 6],
    "Data/Monsters": [14],
    "Data/Quests": [1, 2, 3, 9],
    "Data/Bundles": [6],
    "Data/PaintData": [0, 2, 4],
    "Data/TV/CookingChannel": [1],
    "Data/NPCGiftTastes": [0, 2, 4, 6, 8],
}
# '^'-delimited data: rebuilt from the English value with these fields replaced.
CARET_ASSETS = {"Data/Achievements": [0, 1]}
# list assets: loaded whole (built from the current English list).
LIST_ASSETS = ["Strings/credits"]


def field_indexes(asset, key):
    if asset == "Data/NPCGiftTastes" and key.startswith("Universal_"):
        return []
    return FIELD_ASSETS[asset]


def is_script_asset(asset):
    return asset.startswith(("Data/Events/", "Data/Festivals/")) and not asset.endswith("FestivalDates")


# ---------------------------------------------------------------- event / festival scripts
_QUOTE = re.compile(r'"([^"]*)"')
_QQ = re.compile(r"quickQuestion (.*?)\(break\)")


def script_spans(s):
    """Text spans in an event/festival script: quoted strings and quickQuestion headers."""
    spans = [m.span(1) for m in _QUOTE.finditer(s)]
    spans += [m.span(1) for m in _QQ.finditer(s)]
    spans.sort()
    return spans


def script_texts(s):
    return [s[a:b] for a, b in script_spans(s)]


def is_script(s):
    return bool(script_spans(s)) and ("/" in s or "\\" in s)


def reskeleton_script(en, nl):
    """English script with its text segments replaced by the Dutch ones (in order).
    Returns None if the number of segments doesn't match."""
    en_spans = script_spans(en)
    nl_txt = script_texts(nl)
    if len(en_spans) != len(nl_txt):
        return None
    out, pos = [], 0
    for (a, b), t in zip(en_spans, nl_txt):
        out.append(en[pos:a]); out.append(t); pos = b
    out.append(en[pos:])
    return "".join(out)


# ---------------------------------------------------------------- dialogue / mail
# "Hard" atoms must be copied verbatim from English: IDs, commands, item lists.
HARD = [
    ("question", re.compile(r"\$q [^#]*")),
    ("response", re.compile(r"\$r [^#]*")),
    ("query", re.compile(r"\$query [^#]*")),
    ("action", re.compile(r"\$action [^#]*")),
    ("switch", re.compile(r"\$[dcpt] [^#|]*?(?=#|$|\|)")),
    ("mailitem", re.compile(r"%item [^%]*%%")),
    ("mailaction", re.compile(r"%action [^%]*%%")),
    ("itemlist", re.compile(r"\[(?:\(\w+\)\w+|\d+)(?: (?:\(\w+\)\w+|\d+))*\]")),
    ("bracketcmd", re.compile(r"\[(?:letterbg|textcolor|#)[^\]]*\]")),
    ("fork", re.compile(r"%fork")),
    ("placeholder", re.compile(r"\{\d+\}")),
    ("localized", re.compile(r"\[LocalizedText [^\]]*\]|\[EscapedText [^\]]*\]")),
]
# "Soft" tokens: counts should normally match, differences are reported for review.
SOFT = re.compile(r"#\$[be]#|\$[hsulak]\b|\$neutral\b|\$\d+\b|%(?:adj|noun|place|spouse|name|farm|favorite|kid1|kid2|pet|firstnameletter|band|book|rival|time|year|season)\b|@|\||¦|\^")


def hard_atoms(s):
    found = []
    for name, rx in HARD:
        for m in rx.finditer(s):
            found.append((m.start(), m.end(), name, m.group()))
    found.sort()
    # drop atoms nested in an earlier one (e.g. an itemlist inside a mail command)
    out, end = [], -1
    for a in found:
        if a[0] >= end:
            out.append(a); end = a[1]
    return out


def repair_hard_atoms(en, nl):
    """Copy English hard atoms into the Dutch text, per atom type, in order.
    Returns (text, problems) where problems lists atom types whose counts differ."""
    en_by, nl_by = {}, {}
    for a in hard_atoms(en):
        en_by.setdefault(a[2], []).append(a[3])
    atoms = hard_atoms(nl)
    for a in atoms:
        nl_by.setdefault(a[2], []).append(a[3])
    problems = []
    for name in set(en_by) | set(nl_by):
        if name == "placeholder":
            if sorted(set(en_by.get(name, []))) != sorted(set(nl_by.get(name, []))):
                problems.append(name)
        elif len(en_by.get(name, [])) != len(nl_by.get(name, [])):
            problems.append(name)
    if problems:
        return nl, problems
    idx = {}
    out, pos = [], 0
    for a, b, name, text in atoms:
        i = idx.get(name, 0); idx[name] = i + 1
        repl = text if name == "placeholder" else en_by[name][i]
        out.append(nl[pos:a]); out.append(repl); pos = b
    out.append(nl[pos:])
    return "".join(out), []


def soft_signature(s):
    return sorted(SOFT.findall(s))
