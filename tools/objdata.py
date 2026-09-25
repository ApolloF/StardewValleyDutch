"""Minimal reader for Data/Objects (reflective XNB content): item ID -> name, display-name key, type, category.

Only the first fields of each ObjectData record are read (Name, DisplayName, Description, Type, Category),
which is all the flavored-name generator needs.
"""
import os
import re
import struct

from paths import VANILLA


def _string(d, p):
    """(text, next position) for a nullable string field at p."""
    if d[p] == 0:
        return None, p + 1
    assert d[p] == 2, (p, d[p])
    p += 1
    n = shift = 0
    while True:
        b = d[p]; p += 1
        n |= (b & 0x7F) << shift; shift += 7
        if not b & 0x80:
            break
    return d[p:p + n].decode("utf-8"), p + n


def objects():
    d = open(os.path.join(VANILLA, "en", "Data", "Objects.bin"), "rb").read()
    out = {}
    for m in re.finditer(rb"\x02([\x01-\x3f])", d):
        p, n = m.end(), m.group(1)[0]
        key = d[p:p + n]
        if not re.fullmatch(rb"[\w().]+", key) or d[p + n:p + n + 2] != b"\x03\x02":
            continue
        try:
            q = p + n + 1
            name, q = _string(d, q)
            display, q = _string(d, q)
            _desc, q = _string(d, q)
            typ, q = _string(d, q)
            (category,) = struct.unpack_from("<i", d, q)
        except (AssertionError, IndexError, UnicodeDecodeError):
            continue
        dk = re.search(r"Strings\\Objects:(\w+)\]", display or "")
        out[key.decode()] = {"name": name, "key": dk.group(1) if dk else None, "type": typ, "category": category}
    return out


if __name__ == "__main__":
    import collections
    objs = objects()
    print(len(objs), "objects")
    by_cat = collections.defaultdict(list)
    for k, v in objs.items():
        by_cat[v["category"]].append(f"{k}:{v['name']}")
    for c in (-79, -75, -80, -81, -4):
        print(c, len(by_cat[c]), by_cat[c])
