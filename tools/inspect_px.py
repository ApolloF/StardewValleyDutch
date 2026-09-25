"""Print a texture region as characters, one per pixel, with a color legend.

usage: inspect_px.py <Asset/Name> <lang|old> x y w h [--top N]
The N most common colors get '.' (background) then letters; rarer colors get '?'.
"""
import collections
import sys

from glyphs import Image
from regions import load, load_old


def dump(img, x0, y0, w, h, top=8):
    counts = collections.Counter(img.get(x, y) for y in range(y0, y0 + h) for x in range(x0, x0 + w))
    marks = ".#+*o=%@&xs"
    legend = {c: marks[i] for i, (c, _) in enumerate(counts.most_common(top)) if i < len(marks)}
    lines = ["      " + "".join(str((x // 10) % 10) for x in range(x0, x0 + w)),
             "      " + "".join(str(x % 10) for x in range(x0, x0 + w))]
    for y in range(y0, y0 + h):
        lines.append(f"{y:5} " + "".join(legend.get(img.get(x, y), "?") for x in range(x0, x0 + w)))
    lines.append("legend: " + "  ".join(f"{m}={c}" for c, m in legend.items()))
    return "\n".join(lines)


if __name__ == "__main__":
    asset, lang = sys.argv[1], sys.argv[2]
    x, y, w, h = map(int, sys.argv[3:7])
    top = int(sys.argv[sys.argv.index("--top") + 1]) if "--top" in sys.argv else 8
    img = load_old(asset) if lang == "old" else load(asset, lang)
    print(dump(img, x, y, w, h, top))
