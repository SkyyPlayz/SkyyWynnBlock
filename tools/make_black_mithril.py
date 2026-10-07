"""make_black_mithril - Skyy's idea (2026-10-07): the vanilla Mithril armor set re-leathered as a light-armor base.

Skyy: "swap the dark leather on the mithril set to darker, like black leather, then replace all the chain mail slightly lighter colored
black leather., and take the wings off the helmet."

Reads Assets.zip Common/Items/Armors/Mithril/{Head,Chest,Hands,Legs} (read-only) and writes the edited copies to the git-ignored
models-local/light-armor/mithril-black/ (vanilla-derived - PROJECT-RULES 2: never commit the output):
- brown leather pixels (warm, dark, not gold) -> black leather, keeping their light / dark shading
- chain mail (grey pixels inside CHAIN_RECTS, the 2x2 checker areas) -> smooth, slightly lighter black leather (shading from the blurred original);
  chain flaps with holes become solid leather flaps
- Head: the wing nodes (LFin / RFin and their quads) removed
Run:  python tools/make_black_mithril.py [--mask]   (--mask also writes <piece>_mask.png: red = leather, blue = chain)
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyyart as SA  # noqa: E402

OUT = os.path.join(ROOT, "models-local", "light-armor", "mithril-black")
PIECES = ("Head", "Chest", "Hands", "Legs")
WING_NODES = ("LFin", "RFin")


def hx(s):
    return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))


BLACK = [hx(c) for c in ("#08070a", "#141217", "#1f1c23", "#2c2831", "#3b3641")]      # black leather (brown replacement)
SOFT = [hx(c) for c in ("#151318", "#221f27", "#2f2b35", "#3e3946", "#504a59")]       # slightly lighter (chain replacement)


def luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def ramp(pal, t):
    t = max(0.0, min(1.0, t)) * (len(pal) - 1)
    i = min(int(t), len(pal) - 2)
    f = t - i
    a, b = pal[i], pal[i + 1]
    return tuple(int(round(a[k] + (b[k] - a[k]) * f)) for k in range(3))


def is_brown(c):
    r, g, b = c[0], c[1], c[2]
    mx, mn = max(r, g, b), min(r, g, b)
    return r >= g >= b - 4 and r - b >= 10 and mx <= 150 and (mx - mn) <= 0.6 * mx


def is_grey(c):
    mx, mn = max(c[0], c[1], c[2]), min(c[0], c[1], c[2])
    return mx - mn <= 40 and c[2] >= c[0] - 6


# chain mail areas (texture pixels, x0, y0, x1, y1 exclusive) - the vanilla chain is a 2x2-pixel checker, mapped by eye 2026-10-07
CHAIN_RECTS = {
    "Chest": [(62, 46, 108, 64),      # chain skirt under the belly plate
              (108, 46, 135, 64),     # sleeves
              (135, 40, 167, 64)],    # hanging side chains (with holes)
    "Head": [(72, 13, 86, 31),        # neck guard, back
             (54, 47, 90, 62)],       # neck guard, front / sides (below the gold trim)
}


def chain_mask(img, piece):
    """Grey pixels inside the chain rects (gold trim keeps its colour)."""
    mask = [[False] * img.w for _ in range(img.h)]
    for x0, y0, x1, y1 in CHAIN_RECTS.get(piece, ()):
        for y in range(y0, min(y1, img.h)):
            for x in range(x0, min(x1, img.w)):
                c = img.get(x, y)
                if c[3] >= 128 and is_grey(c):
                    mask[y][x] = True
    return mask


def blur_luma(img, x, y, r=2):
    s = n = 0
    for yy in range(max(0, y - r), min(img.h, y + r + 1)):
        for xx in range(max(0, x - r), min(img.w, x + r + 1)):
            c = img.get(xx, yy)
            if c[3] >= 128:
                s += luma(c)
                n += 1
    return s / n if n else 0


def recolor(img, piece):
    chain = chain_mask(img, piece)
    out = img.copy()
    mask = SA.Img(img.w, img.h)
    bl = [luma(img.get(x, y)) for y in range(img.h) for x in range(img.w)
          if img.get(x, y)[3] >= 128 and is_brown(img.get(x, y))]
    lo, hi = (min(bl), max(bl)) if bl else (0, 1)
    for y in range(img.h):
        for x in range(img.w):
            c = img.get(x, y)
            if c[3] < 128:
                continue
            if chain[y][x]:
                t = (blur_luma(img, x, y) - 40) / 160.0
                n = ((x * 7 + y * 13) % 5) / 40.0           # faint grain so it reads as leather, not flat paint
                col = ramp(SOFT, 0.25 + 0.6 * t + n)
                out.put(x, y, (col[0], col[1], col[2], 255))
                mask.put(x, y, (40, 80, 255, 255))
            elif is_brown(c):
                t = (luma(c) - lo) / max(1.0, hi - lo)
                col = ramp(BLACK, t)
                out.put(x, y, (col[0], col[1], col[2], c[3]))
                mask.put(x, y, (255, 40, 40, 255))
    # chain flaps with holes -> solid leather: fill transparent pixels enclosed left/right by chain pixels on the same row
    for y in range(img.h):
        xs = [x for x in range(img.w) if chain[y][x]]
        if len(xs) < 2:
            continue
        for x in range(xs[0], xs[-1] + 1):
            if img.get(x, y)[3] < 128 and any(chain[y][k] for k in range(max(0, x - 3), x)) and \
                    any(chain[y][k] for k in range(x + 1, min(img.w, x + 4))):
                col = ramp(SOFT, 0.35)
                out.put(x, y, (col[0], col[1], col[2], 255))
                mask.put(x, y, (40, 200, 255, 255))
    return out, mask


def strip(nodes, names):
    keep = []
    for n in nodes:
        if n.get("name") in names:
            continue
        n["children"] = strip(n.get("children") or [], names)
        keep.append(n)
    return keep


def main():
    want_mask = "--mask" in sys.argv
    z = SA.assets()
    os.makedirs(OUT, exist_ok=True)
    for p in PIECES:
        model = json.loads(z.read("Common/Items/Armors/Mithril/%s.blockymodel" % p).decode("utf-8-sig"))
        if p == "Head":
            model["nodes"] = strip(model["nodes"], WING_NODES)
        img = SA.png_decode(z.read("Common/Items/Armors/Mithril/%s_Texture.png" % p))
        out, mask = recolor(img, p)
        with open(os.path.join(OUT, p + ".blockymodel"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(model, fh, indent=2)
        with open(os.path.join(OUT, p + "_Texture.png"), "wb") as fh:
            fh.write(SA.png_encode(out))
        if want_mask:
            with open(os.path.join(OUT, p + "_mask.png"), "wb") as fh:
                fh.write(SA.png_encode(mask))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
