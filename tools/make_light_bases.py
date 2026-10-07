"""make_light_bases - the vanilla armor sets Skyy picked as LIGHT ARMOR bases, re-leathered black (2026-10-07).

Skyy: "we will use the Ornate bronz set as the bas for copper to iron, Cobalt as the base for thorium and cobalt, and mithril as the base
for adamantine+"; "swap the dark leather on the mithril set to darker, like black leather, then replace all the chain mail slightly lighter
colored black leather., and take the wings off the helmet."; then "id swap the light and dark leather colors. so what was brown is the
light leather, and what was chainmail becomes darker". Choices (docs/answered/gear.md): same treatment on all sets, no cape, Ornate Bronze
gets our own legs (make_light_legs.py), metal recolored per tier; eye glow per tier, no plume on Thorium, wings back on the Mithril tier.

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
import make_light_legs as LL  # noqa: E402

OUT = os.path.join(ROOT, "models-local", "light-armor")
SETS = {
    "mithril": {"src": "Mithril", "pieces": ("Head", "Chest", "Hands", "Legs"), "brown": True, "remove": ("LFin", "RFin")},
    "cobalt": {"src": "Cobalt", "pieces": ("Head", "Chest", "Hands", "Legs"), "brown": True},
    # no Legs in vanilla; Cape dropped; pads False = no extra shoulder-pad shrink (Skyy: "sscale copper and iron back up" -> "Undo the
    # pad shrink only")
    "bronze": {"src": "Bronze_Ornate", "pieces": ("Head", "Chest", "Hands"), "brown": False, "pads": False},
    # Skyy 2026-10-07: "im thinking we should change up onyx. pull up the onyx set, and the prisma set, and convert them both in to light
    # leather armor, and well see what looks better." - their leather is a maroon / plum cloth ("red" mode); metal keeps its colours
    "prisma": {"src": "Prisma", "pieces": ("Head", "Chest", "Hands", "Legs"), "brown": "red"},
}
# which pixels count as the base metal: a hue window (degrees) or near-grey; everything else is an accent and keeps its colour
METAL_HUE = {"mithril": (180, 260), "cobalt": (180, 250), "bronze": (10, 65), "prisma": (0, 360)}
# tier -> (base set, hue degrees or None = keep, saturation multiplier, saturation added, lightness multiplier)
TIERS = {
    "copper": ("bronze", 22, 1.15, 0.05, 0.95),
    "iron": ("bronze", 215, 0.12, 0.0, 1.0),
    "thorium": ("cobalt", 135, 0.9, 0.0, 1.05),
    "cobalt": ("cobalt", None, 1.0, 0.0, 1.0),
    "adamantite": ("mithril", 358, 2.6, 0.18, 0.85),
    "mithril": ("mithril", None, 1.0, 0.0, 1.0),
    "onyxium": ("prisma", None, 1.0, 0.0, 1.0),         # Skyy: "the prisma one looks better for onyxium" (Prisma metal kept)
}
# Skyy 2026-10-07: "match eye glow to tier, drop the plume on the thorium, add the wings back the the mithril helm on the mithril tier,
# and  build copper legs"
GLOW_SRC = {"mithril": (150, 182)}                  # the helmet eye glow (teal) on the base, hue window in degrees
GLOW_HUE = {"adamantite": 0}                        # tier glow hue (tiers not listed keep the base glow)
# nodes dropped per tier: Fluff = the Cobalt helmet plume; FrontBelt1 / BackBelt = the Mithril diagonal cross strap (Skyy deleted it in
# Blockbench on Adamantite / Mithril / Onyxium: "i removed the cross straps on some of the armor")
CROSS_STRAP = ("FrontBelt1", "BackBelt")
# a (name, (x, y, z)) entry removes only the nodes of that name AND box size - Skyy's Thorium helmet edit in Blockbench ("i changed up the
# thorium set a little") dropped the front crest plate (Block 13x13x5) and the two side plates (Block 11x10x3), kept the two back ones
THORIUM_HELM = (("Block", (13, 13, 5)), ("Block", (11, 10, 3)))
TIER_REMOVE = {"thorium": ("Fluff",) + THORIUM_HELM, "adamantite": CROSS_STRAP, "mithril": CROSS_STRAP}
TIER_UNSTRIP = {"mithril"}                          # tiers that keep the nodes their base set removes (the Mithril wings)


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


def is_red_cloth(c):
    """Maroon / plum cloth (Onyxium, Prisma): dark, warm-red to purple hue, some saturation."""
    h, l, s_ = colorsys.rgb_to_hls(c[0] / 255.0, c[1] / 255.0, c[2] / 255.0)
    h *= 360
    return s_ >= 0.15 and l <= 0.45 and (h >= 290 or h <= 20)


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
    ("prisma", "Head"): [(111, 2, 125, 42)],       # the black + red feathers (Skyy: "keep the black and red feathers on the Prisma set")
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


def tier_metal(img, base, tier_cfg, leather_px, glow=None):
    """Re-hue the base metal, keeping lightness (shading) and relative saturation; leather untouched; accents kept, except the
    eye glow, which takes the tier's GLOW_HUE."""
    _, hue, smul, sadd, lmul = tier_cfg
    if hue is None and glow is None:
        return img
    lo, hi = METAL_HUE[base]
    glo, ghi = GLOW_SRC.get(base, (999, 999))
    out = img.copy()
    for y in range(img.h):
        for x in range(img.w):
            c = img.get(x, y)
            if c[3] < 8 or (x, y) in leather_px:
                continue
            h, l, s_ = colorsys.rgb_to_hls(c[0] / 255.0, c[1] / 255.0, c[2] / 255.0)
            if s_ > 0.12 and glow is not None and glo <= h * 360 <= ghi:
                r, g, b = colorsys.hls_to_rgb(glow / 360.0, l, max(s_, 0.7))
                out.put(x, y, (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)), c[3]))
                continue
            if hue is None or (s_ > 0.12 and not (lo <= h * 360 <= hi)):
                continue                                            # accent (gold trim) / tier keeps the base metal
            s2 = max(0.0, min(1.0, s_ * smul + sadd))
            r, g, b = colorsys.hls_to_rgb(hue / 360.0, max(0.0, min(1.0, l * lmul)), s2)
            out.put(x, y, (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)), c[3]))
    return out


def is_leather(img, x, y, brown_mode, leather, keep):
    if in_rects(x, y, keep):
        return False
    if leather:
        return in_rects(x, y, leather)
    if brown_mode == "red":
        return is_red_cloth(img.get(x, y))
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


# Skyy 2026-10-07: "see how the legs on the copper armor are like skin tight to the player, shift everything you can in on the armor sets
# to make it tighter to the players skin, and a little slimmer without messing up the depth on the armor, to make it look slimmer and
# lighter" -> every piece is squeezed toward its bone: x by SLIM_X, z by SLIM_Z (depth layering kept), y untouched; a box that wraps the
# body never gets narrower / shallower than the bone + SLIM_MARGIN (no skin poking through). Our own legs (make_light_legs) are not slimmed.
SLIM_X, SLIM_Z, SLIM_MARGIN = 0.88, 0.97, 0.6
# Skyy: "could you shrink all the armor pads amd scoot them in a little more, to make the sets slimmer?" -> everything on the upper-arm
# bones (shoulder pads) shrinks by PAD_SCALE on every axis on top of the slim, and its sideways offsets shrink by PAD_IN
PAD_BONES, PAD_SCALE, PAD_IN = ("L-Arm", "R-Arm"), 0.85, 0.75
BONE_WD = {                                          # player bone width (x) and depth (z)
    "Head": (30, 28), "Chest": (27.4, 19), "Belly": (26, 18), "Pelvis": (26, 18),
    "L-Arm": (8, 12), "R-Arm": (8, 12), "L-Forearm": (8, 12), "R-Forearm": (8, 12), "L-Hand": (10, 14), "R-Hand": (10, 14),
    "L-Thigh": (10, 12), "R-Thigh": (10, 12), "L-Calf": (10, 12), "R-Calf": (10, 12), "L-Foot": (14, 20), "R-Foot": (14, 20),
}


def slim(nodes, bone=None, cx=0.0, cz=0.0, pads=True):
    """Scale x / z of every non-bone node's position, shape offset and stretch about its bone centre; clamp body-wrapping boxes."""
    for n in nodes:
        name = n.get("name")
        if name in BONE_WD:
            slim(n.get("children") or [], name, 0.0, 0.0, pads)
            continue
        pos = n.get("position") or {}
        shape = n.get("shape") or {}
        pad = pads and bone in PAD_BONES
        fx = SLIM_X * (PAD_IN if pad else 1.0)
        if bone is not None:
            pos["x"] = pos.get("x", 0) * fx
            pos["z"] = pos.get("z", 0) * SLIM_Z
            off = shape.get("offset")
            if off:
                off["x"] = off.get("x", 0) * fx
                off["z"] = off.get("z", 0) * SLIM_Z
        nx = cx + pos.get("x", 0) + ((shape.get("offset") or {}).get("x", 0))
        nz = cz + pos.get("z", 0) + ((shape.get("offset") or {}).get("z", 0))
        size = (shape.get("settings") or {}).get("size")
        st = shape.get("stretch")
        if bone is not None and size and st and shape.get("type") in ("box", "quad"):
            bw, bd = BONE_WD[bone]
            ps = PAD_SCALE if pad else 1.0
            if pad and size.get("y") and "y" in st:
                st["y"] = st["y"] * PAD_SCALE
            for ax, f, bsz, c in (("x", SLIM_X * ps, bw, nx), ("z", SLIM_Z * ps, bd, nz)):
                if ax not in size or not size[ax]:
                    continue
                old = abs(size[ax] * st.get(ax, 1))
                new = old * f
                wraps = old >= bsz * 0.9 and abs(c) < bsz / 2
                if wraps:
                    new = max(new, min(old, bsz + 2 * SLIM_MARGIN))
                sign = -1 if st.get(ax, 1) < 0 else 1
                st[ax] = sign * new / abs(size[ax])
        slim(n.get("children") or [], bone, nx, nz, pads)


# Skyy 2026-10-07: "and give the gloves leather sleves on the cobalt set" -> a light-leather sleeve on each forearm (inside the vanilla
# glove + cuff) and a new upper-arm root with a sleeve up to the shoulder pad. Hands roots anchor on the bone CENTRE (seen in Blockbench).
# Root nodes need settings.isPiece = true to attach to the player bone. Texture grows 64x64 -> 64x96; the forearm sleeve uses free space of the vanilla atlas, the upper sleeve the new rows.
SLEEVE_UV = {   # face -> (x, y, w, h); both sides share them
    "fore": {"front": (32, 36, 9, 16), "back": (41, 36, 9, 16), "left": (50, 36, 13, 16), "right": (44, 16, 13, 16),
             "top": (32, 36, 9, 13), "bottom": (41, 36, 9, 13)},
    "upper": {"front": (0, 64, 9, 20), "back": (9, 64, 9, 20), "left": (18, 64, 13, 20), "right": (31, 64, 13, 20),
              "top": (44, 64, 9, 13), "bottom": (53, 64, 9, 13)},
}


def _sleeve(name, size, pos, uv):
    import make_light_chest as LC
    n = LC.box(name, size, pos)
    n["shape"]["textureLayout"] = {f: {"offset": {"x": r[0], "y": r[1]}, "mirror": {"x": False, "y": False}, "angle": 0}
                                   for f, r in uv.items()}
    n["shape"]["shadingMode"] = "standard"
    return n


def cobalt_sleeves(model, img, leather_px):
    """Adds the sleeves to a Cobalt Hands model (in place) and returns the grown, painted texture."""
    import make_light_chest as LC
    for side in ("L", "R"):
        fore = next(n for n in model["nodes"] if n["name"] == side + "-Forearm")
        fore["children"].append(_sleeve(side + "-ForeSleeve", (9, 16, 13), (0, 0, 0), SLEEVE_UV["fore"]))
        arm = LC.box(side + "-Arm", (0, 0, 0), (0, 0, 0))
        arm["shape"] = {"offset": {"x": 0, "y": 0, "z": 0}, "stretch": {"x": 1, "y": 1, "z": 1}, "textureLayout": {}, "type": "none",
                        "settings": {"isPiece": True}, "unwrapMode": "custom", "visible": True, "doubleSided": False, "shadingMode": "flat"}
        arm["children"] = [_sleeve(side + "-UpperSleeve", (9, 19, 13), (0, -0.5, 0), SLEEVE_UV["upper"])]
        model["nodes"].append(arm)
    out = SA.Img(img.w, 96)
    for y in range(img.h):
        for x in range(img.w):
            out.put(x, y, img.get(x, y))
    for i, part in enumerate(("fore", "upper")):
        for j, (face, r) in enumerate(sorted(SLEEVE_UV[part].items())):
            if face in ("top", "bottom") and part == "fore":
                continue                                    # re-uses the front / back pixels
            f = LC.Face(out, r, 40 + i * 10 + j)
            LL.leather_face(f, LIGHT, stitch=True)
            if part == "upper":                             # a dark strap band near the top
                for u in range(f.w):
                    for v in (3, 4):
                        if v < f.h:
                            f.put(u, v, DARK[1] if v == 4 else DARK[2])
            for yy in range(r[1], r[1] + r[3]):
                for xx in range(r[0], r[0] + r[2]):
                    leather_px.add((xx, yy))
    return out


def _strip_hit(n, names):
    if n.get("name") in names:
        return True
    size = ((n.get("shape") or {}).get("settings") or {}).get("size") or {}
    dims = (size.get("x"), size.get("y"), size.get("z"))
    return any(isinstance(e, tuple) and e[0] == n.get("name") and tuple(e[1]) == dims for e in names)


def strip(nodes, names):
    keep = []
    for n in nodes:
        if _strip_hit(n, names):
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


def tiers_of(name):
    return [(t, c) for t, c in TIERS.items() if c[0] == name]


def main():
    z = SA.assets()
    for name, cfg in SETS.items():
        for p in cfg["pieces"]:
            src = "Common/Items/Armors/%s/%s" % (cfg["src"], p)
            full = json.loads(z.read(src + ".blockymodel").decode("utf-8-sig"))
            model = json.loads(json.dumps(full))
            if cfg.get("remove"):
                model["nodes"] = strip(model["nodes"], cfg["remove"])
            img = SA.png_decode(z.read(src + "_Texture.png"))
            slim(full["nodes"], pads=cfg.get("pads", True))
            slim(model["nodes"], pads=cfg.get("pads", True))
            out, leather_px = recolor(img, (name, p), cfg["brown"])
            if (name, p) == ("cobalt", "Hands"):
                out = cobalt_sleeves(model, out, leather_px)
                full = json.loads(json.dumps(model))
            write(os.path.join(OUT, "base-" + name), p, model, out)
            for tier, tcfg in tiers_of(name):
                tm = json.loads(json.dumps(full if tier in TIER_UNSTRIP else model))
                if tier in TIER_REMOVE:
                    tm["nodes"] = strip(tm["nodes"], TIER_REMOVE[tier])
                write(os.path.join(OUT, "sets", tier), p, tm, tier_metal(out, name, tcfg, leather_px, GLOW_HUE.get(tier)))
        if name == "bronze":                                # our own legs (make_light_legs.py) on the Cobalt legs rig
            rig = json.loads(z.read("Common/Items/Armors/Cobalt/Legs.blockymodel").decode("utf-8-sig"))
            model, img, leather_px = LL.make(rig, LIGHT, DARK)
            write(os.path.join(OUT, "base-" + name), "Legs", model, img)
            for tier, tcfg in tiers_of(name):
                write(os.path.join(OUT, "sets", tier), "Legs", model, tier_metal(img, name, tcfg, leather_px))
        print("wrote base-%s + tiers %s" % (name, ", ".join(t for t, _ in tiers_of(name))))


if __name__ == "__main__":
    main()
