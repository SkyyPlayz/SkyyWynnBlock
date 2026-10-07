"""make_light_bases - the vanilla armor sets Skyy picked as LIGHT ARMOR bases, re-leathered black (2026-10-07).

Skyy: "we will use the Ornate bronz set as the bas for copper to iron, Cobalt as the base for thorium and cobalt, and mithril as the base
for adamantine+"; "swap the dark leather on the mithril set to darker, like black leather, then replace all the chain mail slightly lighter
colored black leather., and take the wings off the helmet."; then "id swap the light and dark leather colors. so what was brown is the
light leather, and what was chainmail becomes darker". Choices (docs/answered/gear.md): same treatment on all sets, no cape, Ornate Bronze
gets our own legs (not built yet), metal recolored per tier (next step).

Reads Assets.zip Common/Items/Armors/<set>/ (read-only) and writes edited copies to the git-ignored models-local/light-armor/base-<set>/
(vanilla-derived - PROJECT-RULES 2: never commit the output):
- leather (brown pixels, or the hand-mapped LEATHER_RECTS where the metal itself is brown, as on bronze) -> LIGHT black leather
- chain mail (grey pixels inside CHAIN_RECTS, the 2x2 checker areas) -> smooth DARK black leather; chain flaps with holes made solid
- REMOVE nodes dropped (the Mithril helmet wings); KEEP_RECTS left untouched (the Cobalt plume)
- Chest leather gets a small diamond pattern (Skyy: "do a small scale pattern in the leather on the body")
- TIERS: every tier is its base set with the metal re-hued, shading untouched (Skyy: "for the metal, match the sharing, just swap out
  the coloring"); accents outside the base metal's hue (Mithril gold trim, helmet eye glow) are kept
Out:  models-local/light-armor/base-<set>/ and models-local/light-armor/sets/<tier>/ (Head/Chest/Hands[/Legs] .blockymodel + _Texture.png)
Run:  python tools/make_light_bases.py
"""
import colorsys
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyyart as SA  # noqa: E402

OUT = os.path.join(ROOT, "models-local", "light-armor")
SETS = {
    "mithril": {"src": "Mithril", "pieces": ("Head", "Chest", "Hands", "Legs"), "brown": True, "remove": ("LFin", "RFin")},
    "cobalt": {"src": "Cobalt", "pieces": ("Head", "Chest", "Hands", "Legs"), "brown": True},
    "bronze": {"src": "Bronze_Ornate", "pieces": ("Head", "Chest", "Hands"), "brown": False},   # no Legs in vanilla; Cape dropped
}
# which pixels count as the base metal: a hue window (degrees) or near-grey; everything else is an accent and keeps its colour
METAL_HUE = {"mithril": (180, 260), "cobalt": (180, 250), "bronze": (10, 65)}
# tier -> (base set, hue degrees or None = keep, saturation multiplier, saturation added, lightness multiplier)
TIERS = {
    "copper": ("bronze", 22, 1.15, 0.05, 0.95),
    "iron": ("bronze", 215, 0.12, 0.0, 1.0),
    "thorium": ("cobalt", 135, 0.9, 0.0, 1.05),
    "cobalt": ("cobalt", None, 1.0, 0.0, 1.0),
    "adamantite": ("mithril", 358, 2.6, 0.18, 0.85),
    "mithril": ("mithril", None, 1.0, 0.0, 1.0),
    "onyxium": ("mithril", 278, 2.4, 0.15, 0.8),
}


def hx(s):
    return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))


DARK = [hx(c) for c in ("#08070a", "#141217", "#1f1c23", "#2c2831", "#3b3641")]       # dark black leather (chain replacement)
LIGHT = [hx(c) for c in ("#151318", "#221f27", "#2f2b35", "#3e3946", "#504a59")]      # lighter black leather (brown replacement)


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
    return r >= g >= b - 4 and r - b >= 10 and mx <= 150 and (mx - mn) <= 0.8 * mx


def is_grey(c):
    mx, mn = max(c[0], c[1], c[2]), min(c[0], c[1], c[2])
    return mx - mn <= 40 and c[2] >= c[0] - 6


# texture rects (x0, y0, x1, y1 exclusive), mapped by eye 2026-10-07. Chain = the vanilla 2x2-pixel checker.
CHAIN_RECTS = {
    ("mithril", "Chest"): [(62, 46, 108, 64),      # chain skirt under the belly plate
                           (108, 46, 135, 64),     # sleeves
                           (135, 40, 167, 64)],    # hanging side chains (with holes)
    ("mithril", "Head"): [(72, 13, 86, 31),        # neck guard, back
                          (54, 47, 90, 62)],       # neck guard, front / sides (below the gold trim)
}
LEATHER_RECTS = {                                  # sets whose metal is brown too: leather by area, not by colour
    ("bronze", "Chest"): [(0, 16, 28, 58),         # undershirt + belly
                          (63, 22, 91, 58),        # front / back tabard (emblem kept as a lighter tone)
                          (0, 59, 48, 95),         # side flaps
                          (28, 35, 62, 40)],       # rope belt
    ("bronze", "Hands"): [(33, 0, 57, 22)],        # gloves
}
KEEP_RECTS = {
    ("cobalt", "Head"): [(112, 0, 128, 20)],       # the plume (Fluff quads)
}


def in_rects(x, y, rects):
    return any(x0 <= x < x1 and y0 <= y < y1 for x0, y0, x1, y1 in rects)


def chain_mask(img, key):
    """Grey pixels inside the chain rects (gold trim keeps its colour)."""
    mask = [[False] * img.w for _ in range(img.h)]
    for x0, y0, x1, y1 in CHAIN_RECTS.get(key, ()):
        for y in range(y0, min(y1, img.h)):
            for x in range(x0, min(x1, img.w)):
                c = img.get(x, y)
                if c[3] >= 128 and is_grey(c):
                    mask[y][x] = True
    return mask


def quilt(col, x, y, on):
    """Small diamond quilting (4-pixel cells): dark seams, a lit pixel just above each seam."""
    if not on:
        return col
    d, e = (x + y) % 4, (x - y) % 4
    f = 0.72 if (d == 0 or e == 0) else (1.18 if d == 1 else 1.0)
    return tuple(max(0, min(255, int(v * f))) for v in col)


def tier_metal(img, base, tier_cfg, leather_px):
    """Re-hue the base metal, keeping lightness (shading) and relative saturation; accents and leather untouched."""
    _, hue, smul, sadd, lmul = tier_cfg
    if hue is None:
        return img
    lo, hi = METAL_HUE[base]
    out = img.copy()
    for y in range(img.h):
        for x in range(img.w):
            c = img.get(x, y)
            if c[3] < 8 or (x, y) in leather_px:
                continue
            h, l, s_ = colorsys.rgb_to_hls(c[0] / 255.0, c[1] / 255.0, c[2] / 255.0)
            if s_ > 0.12 and not (lo <= h * 360 <= hi):
                continue                                            # accent (gold trim, eye glow)
            s2 = max(0.0, min(1.0, s_ * smul + sadd))
            r, g, b = colorsys.hls_to_rgb(hue / 360.0, max(0.0, min(1.0, l * lmul)), s2)
            out.put(x, y, (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)), c[3]))
    return out


def is_leather(img, x, y, brown_mode, leather, keep):
    if in_rects(x, y, keep):
        return False
    if leather:
        return in_rects(x, y, leather)
    return brown_mode and is_brown(img.get(x, y))


def blur_luma(img, x, y, r=2):
    s = n = 0
    for yy in range(max(0, y - r), min(img.h, y + r + 1)):
        for xx in range(max(0, x - r), min(img.w, x + r + 1)):
            c = img.get(xx, yy)
            if c[3] >= 128:
                s += luma(c)
                n += 1
    return s / n if n else 0


def recolor(img, key, brown_mode):
    pattern = key[1] == "Chest"
    chain = chain_mask(img, key)
    leather = LEATHER_RECTS.get(key, ())
    keep = KEEP_RECTS.get(key, ())
    out = img.copy()
    mask = SA.Img(img.w, img.h)
    touched = set()
    bl = [luma(img.get(x, y)) for y in range(img.h) for x in range(img.w)
          if img.get(x, y)[3] >= 128 and is_leather(img, x, y, brown_mode, leather, keep)]
    lo, hi = (min(bl), max(bl)) if bl else (0, 1)
    for y in range(img.h):
        for x in range(img.w):
            c = img.get(x, y)
            if c[3] < 128:
                continue
            if in_rects(x, y, keep):
                continue
            if chain[y][x]:
                t = (blur_luma(img, x, y) - 40) / 160.0
                n = ((x * 7 + y * 13) % 5) / 40.0           # faint grain so it reads as leather, not flat paint
                col = quilt(ramp(DARK, 0.25 + 0.6 * t + n), x, y, pattern)
                out.put(x, y, (col[0], col[1], col[2], 255))
                mask.put(x, y, (40, 80, 255, 255))
                touched.add((x, y))
            elif is_leather(img, x, y, brown_mode, leather, keep):
                t = (luma(c) - lo) / max(1.0, hi - lo)
                col = quilt(ramp(LIGHT, t), x, y, pattern)
                out.put(x, y, (col[0], col[1], col[2], c[3]))
                mask.put(x, y, (255, 40, 40, 255))
                touched.add((x, y))
    # chain flaps with holes -> solid leather: fill transparent pixels enclosed left/right by chain pixels on the same row
    for y in range(img.h):
        xs = [x for x in range(img.w) if chain[y][x]]
        if len(xs) < 2:
            continue
        for x in range(xs[0], xs[-1] + 1):
            if img.get(x, y)[3] < 128 and any(chain[y][k] for k in range(max(0, x - 3), x)) and \
                    any(chain[y][k] for k in range(x + 1, min(img.w, x + 4))):
                col = ramp(DARK, 0.35)
                out.put(x, y, (col[0], col[1], col[2], 255))
                mask.put(x, y, (40, 200, 255, 255))
                touched.add((x, y))
    return out, touched


def strip(nodes, names):
    keep = []
    for n in nodes:
        if n.get("name") in names:
            continue
        n["children"] = strip(n.get("children") or [], names)
        keep.append(n)
    return keep


def write(out_dir, piece, model, img):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, piece + ".blockymodel"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(model, fh, indent=2)
    with open(os.path.join(out_dir, piece + "_Texture.png"), "wb") as fh:
        fh.write(SA.png_encode(img))


def main():
    z = SA.assets()
    for name, cfg in SETS.items():
        for p in cfg["pieces"]:
            src = "Common/Items/Armors/%s/%s" % (cfg["src"], p)
            model = json.loads(z.read(src + ".blockymodel").decode("utf-8-sig"))
            if cfg.get("remove"):
                model["nodes"] = strip(model["nodes"], cfg["remove"])
            img = SA.png_decode(z.read(src + "_Texture.png"))
            out, leather_px = recolor(img, (name, p), cfg["brown"])
            write(os.path.join(OUT, "base-" + name), p, model, out)
            for tier, tcfg in TIERS.items():
                if tcfg[0] == name:
                    write(os.path.join(OUT, "sets", tier), p, model, tier_metal(out, name, tcfg, leather_px))
        print("wrote base-%s + tiers %s" % (name, ", ".join(t for t, c in TIERS.items() if c[0] == name)))


if __name__ == "__main__":
    main()
