"""SkyWynn Foraging armor - F2 tier builder (shared by every F2 tree: Maple, Azure). ORIGINAL; no vanilla or Armory pixels.

PROGRESSION RULE (Skyy 2026-10-09: "Beautiful I want the armor sets consistent across the set, but each set should be a little
different visually, so they start simple and get a little cooler each set you get to that's better"):
same family + fit as F1 (geometry derived from ga_oak.py); every F2 tree gets EXACTLY the same tier-2 upgrades (only wood colours,
plate shape and mark change per tree). F2 over F1 - a clear but modest step up:
  1. an extra shoulder layer: a raised cap plate on top of each pauldron, with a heartwood rim and pegs
  2. wooden PEGS (like rivets) holding the plates: cuirass, breast plates, plackart, belt, bracers, greaves, knees
  3. STRONGER SAP: a brighter, thicker sap vein with 4 branches + a soft halo up the chest, a second vein up the back,
     a sap line along the new helmet crest and the shoulder caps
  4. belt upgrade: heartwood trim bands + pegs, a bigger carved knot boss as the clasp
  5. a helmet CREST: a carved ridge over the helmet from brow to nape, and a taller middle crown point
  6. round knot-boss knee caps
Room is left for F3 (angular shapes, bigger shoulders), F4 (spikes / thorns), F5 (ornate, gold, the most impressive).
"""
import math
import numpy as np
import ga_paint as P
from ga_paint import ROPE, VINE, SAP, stamp, stitches, mottle, hash2
import ga_oak as O
from ga_oak import _horiz, rope_band, twist, _side_cut

TIER = "F2_Autumn"


# ------------------------------------------------------------------ tier-2 painters (shared)
def pegs(F, pts, T, local=False, r=1.0):
    """round wooden pegs (2x2 texels): heartwood head, lit top-left, dark rim bottom-right. pts: (x, y) world (front/back
    faces) or local (lx, ly) when local=True."""
    if not F.is_side():
        return
    for (px, py) in pts:
        if local:
            a, b = F.lx, F.ly
        else:
            a = _horiz(F) if F.face in ("left", "right") else F.x
            b = F.y
        m = (np.abs(a - px) < r) & (np.abs(b - py) < r) & F.alpha
        if not m.any():
            continue
        F.mat[m] = T.WOOD
        F.val[m] = 0.08
        F.val[m & ~P._shift(m, 1, 0)] += 0.08                # lit top row
        F.val[m & ~P._shift(m, -1, 0)] -= 0.12               # darker bottom row
        dv, du = P.face_down(F)
        sh = P._shift(m, dv, du) & ~m & F.alpha
        F.mat[sh] = T.DK
        F.val[sh] = 0.2


def sap2(F, x0, y0, y1, back=False, halo=True):
    """tier-2 sap vein: brighter + thicker than F1, 4 branches with tiny forks, soft 1-texel halo."""
    if (F.n[2] < 0.5) if not back else (F.n[2] > -0.5):
        return
    yy = F.y
    xc = x0 + 0.9 * np.sin((yy - y0) * 0.42)
    m = (np.abs(F.x - xc) < 0.5) & (yy > y0) & (yy < y1)
    L = y1 - y0
    for k, (by, dirx) in enumerate(((y0 + L * 0.30, 1), (y0 + L * 0.50, -1), (y0 + L * 0.68, 1), (y0 + L * 0.84, -1))):
        t = yy - by
        ln = 4.5 if k < 2 else 3.5
        br = (t > 0) & (t < ln) & (np.abs(F.x - (x0 + dirx * (1.0 + t * 0.95))) < 0.5)
        fork = (t > ln - 1.6) & (t < ln + 0.6) & (np.abs(F.x - (x0 + dirx * (1.0 + (ln - 1.6) * 0.95 + 1.4))) < 0.5)
        m = m | br | fork
    m &= F.alpha
    if halo:
        h = (P._shift(m, 0, 1) | P._shift(m, 0, -1)) & ~m & F.alpha
        F.val[h] += 0.08
        F.warm[h] = 0
    F.mat[m] = SAP
    F.val[m] = 0.1
    F.lockval[m] = False


def sap_line_local(F, axis_val, axis="lz", lo=-99, hi=99, along="ly"):
    a = getattr(F, axis)
    b = getattr(F, along)
    m = (np.abs(a - axis_val) < 0.5) & (b > lo) & (b < hi) & F.alpha
    F.mat[m] = SAP
    F.val[m] = 0.05
    return m


def wood_band(F, y0, y1, T, local=True):
    y = F.ly if local else F.y
    m = (y > y0) & (y < y1) & F.alpha
    F.mat[m] = T.WOOD
    F.val[m] -= 0.02
    F.val[m & (y > y1 - 1)] += 0.07
    F.val[m & (y < y0 + 1)] -= 0.08
    return m


def knot_boss(F, T):
    """carved round knot boss (belt clasp / knee): concentric end-grain rings, dark rim."""
    F.mat[:] = T.WOOD
    if F.face in ("front", "top"):
        cu, cv = F.fw / 2.0, F.fh / 2.0
        r = np.hypot((F.u - cu) / max(cu, 1), (F.v - cv) / max(cv, 1)) * min(cu, cv)
        F.val[(np.floor(r) % 2) == 1] -= 0.12
        rim = r > min(cu, cv) - 1
        F.mat[rim] = T.DK
        F.val[rim] = 0.15
        F.alpha &= ~(np.hypot((F.u - cu) / cu, (F.v - cv) / cv) > 1.08)
    else:
        F.val -= 0.1


def _mask_paint(F, rows, colours, flip_v=False):
    H, W = len(rows), len(rows[0])
    iv = np.clip((F.v / F.fh * H).astype(int), 0, H - 1)
    iu = np.clip((F.u / F.fw * W).astype(int), 0, W - 1)
    if flip_v:
        iv = H - 1 - iv
    ch = np.array([list(r) for r in rows])[iv, iu]
    F.alpha &= ch != "."
    for c, (mat, val) in colours.items():
        m = ch == c
        F.mat[m] = mat
        F.val[m] = val


# ------------------------------------------------------------------ build one F2 tree
def build(T):
    """T: a tree spec (module or namespace) with: TREE, BARK, DK, LEAF, WOOD, CLOTH, base(F, seed, scars),
    plates(F, region, pitch, seed), hem(F, seed, clip), crown_mid(F), crown_side(F), p_leaf(F), p_leaf_hang(F),
    leaflet(F, cu, cv), MARK_HEAD (list of add dicts), MARK_CHEST (list of add dicts)."""
    BARK, DK, WOOD, CLOTH, LEAF = T.BARK, T.DK, T.WOOD, T.CLOTH, T.LEAF

    def cut_rim(F, which="bottom"):
        d = {"top": F.v, "bottom": F.fh - F.v, "left": F.u, "right": F.fw - F.u}[which]
        m = (d < 1) & F.alpha
        F.mat[m] = WOOD
        F.val[m] -= 0.05

    def dark_rim(F):
        F.val[F.v < 1] += 0.05
        F.mat[F.v > F.fh - 1] = DK
        F.val[F.v > F.fh - 1] = 0.2

    # ---------------- HEAD
    def p_cap(F):
        T.base(F, seed=1)
        if F.is_side():
            wood_band(F, -4.0, -2.0, T)                      # tier 2: heartwood brow band (F1: rope)
            pegs(F, [(-10.0, -3.0), (10.0, -3.0), (-4.0, -3.0), (4.0, -3.0)], T, local=True, r=0.9)
            F.val[F.v < 1] += 0.04

    def p_cap_upper(F):
        T.base(F, seed=2, scars=False)
        if F.is_side():
            dark_rim(F)

    def p_dome(F):
        T.base(F, seed=3, scars=False)
        if F.face == "top":
            r = np.hypot(F.lx, F.lz)
            ring = r < 5.5
            F.mat[ring] = WOOD
            F.val[ring & ((np.floor(r * 0.9) % 2) == 1)] -= 0.1
        else:
            cut_rim(F, "top")

    def p_brim(F):
        T.base(F, seed=4, scars=False)
        if F.is_side():
            dark_rim(F)
        elif F.face == "top":
            r = np.maximum(np.abs(F.lx) / 18.0, np.abs(F.lz) / 17.0)
            F.val[r > 0.93] += 0.08
        elif F.face == "bottom":
            F.mat[:] = WOOD
            F.val -= 0.2

    def p_helmback(F):
        T.base(F, seed=5)
        if F.is_side():
            T.plates(F, F.alpha, 6.0, seed=5)
            T.hem(F, seed=5, clip=2)

    def p_cheek(F):
        T.base(F, seed=6, scars=False)
        if F.is_side():
            T.plates(F, F.alpha, 6.0, seed=6)
            T.hem(F, seed=6, clip=0)
            if F.face in ("left", "right"):
                pegs(F, [(0.0, 4.0)], T, local=True, r=0.9)

    def p_crest(F):
        """tier 2: carved crest ridge over the helmet, sap line along its top."""
        T.base(F, seed=9, scars=False)
        if F.face == "top":
            sap_line_local(F, 0.0, axis="lx", along="lz", lo=-7.0, hi=7.0)
        elif F.is_side():
            F.mat[F.v > F.fh - 1] = DK
            F.val[F.v > F.fh - 1] = 0.2
            if F.face == "front":
                F.mat[:] = WOOD

    HEAD_OVR = {
        "HelmCap": dict(mat=BARK, paint=p_cap),
        "HelmUpper": dict(mat=BARK, paint=p_cap_upper),
        "HelmDome": dict(mat=BARK, paint=p_dome),
        "HelmBrim": dict(mat=BARK, paint=p_brim),
        "HelmBack": dict(mat=BARK, paint=p_helmback),
        "R-Cheek": dict(mat=BARK, paint=p_cheek),
        "CrownMid": dict(mat=BARK, paint=T.crown_mid, size=T.CROWN_MID_SIZE, pivot=T.CROWN_MID_PIVOT),
        "R-CrownSide": dict(mat=BARK, paint=T.crown_side, size=T.CROWN_SIDE_SIZE, pivot=T.CROWN_SIDE_PIVOT,
                            rot=T.CROWN_SIDE_ROT),
        "R-HelmLeaf": dict(mat=LEAF, paint=T.p_leaf, size=T.LEAF_SIZE),
    }
    HEAD_ADD = [
        dict(name="HelmCrest", bone="Head", pivot=(0, 20.5, -2.0), size=(2, 3, 16), mat=BARK, paint=p_crest),
        dict(name="HelmBadge", bone="Head", pivot=(0, 10.5, 16.8), size=(5, 5, 2), mat=WOOD,
             paint=lambda F: knot_boss(F, T), skip=("back",)),
    ] + list(T.MARK_HEAD)

    # ---------------- CHEST
    def _laced_gap(F, halfw, y0, y1, k=1.0):
        gap = np.abs(F.x) < halfw
        F.mat[gap] = CLOTH
        F.val[gap] = -0.12
        ph = F.y % 4.0
        lace = gap & (np.abs(np.abs(F.x) - np.abs(ph - 2.0) * k) < 0.55)
        F.mat[lace] = ROPE
        F.val[lace] = 0.05
        sap2(F, 0.0, y0, y1)

    def p_cuirass(F):
        T.base(F, seed=10)
        if F.is_side():
            T.plates(F, F.alpha, 11.0, seed=10)
            if F.face == "front":
                _laced_gap(F, 2.6, 64.0, 85.0)
            if F.face == "back":
                sap2(F, 0.0, 66.0, 84.0, back=True)
                pegs(F, [(-9.0, 80.0), (9.0, 80.0), (-9.0, 70.0), (9.0, 70.0)], T)

    def p_breast(F):
        T.base(F, seed=11)
        if F.is_side():
            T.plates(F, F.alpha, 9.0, seed=11)
            T.hem(F, seed=11, clip=2)
            if F.face == "front":
                inner = (np.abs(F.x) < 3.1) & F.alpha
                F.mat[inner] = WOOD
                eye = inner & ((np.floor(F.y) % 4) == 1)
                F.mat[eye] = ROPE
                F.val[eye] = -0.05
                pegs(F, [(-11.5, 81.0), (11.5, 81.0), (-11.5, 74.0), (11.5, 74.0)], T)

    def p_plackart(F):
        T.base(F, seed=12)
        if F.is_side():
            T.plates(F, F.alpha, 8.0, seed=12)
            if F.face == "front":
                _laced_gap(F, 2.0, 55.0, 68.0, k=0.8)
                pegs(F, [(-8.0, 62.0), (8.0, 62.0)], T)

    def p_belt(F):
        """tier 2 belt: heartwood trim bands top + bottom, pegs, rope wraps."""
        T.base(F, seed=13, scars=False)
        if F.is_side():
            top = F.v < 1
            bot = F.v > F.fh - 1.01
            F.mat[top | bot] = WOOD
            F.val[top] += 0.05
            F.val[bot] -= 0.1
            wrap = (np.abs(np.abs(F.x) - 6.5) < 1.5) & ~top & ~bot
            F.mat[wrap & F.alpha] = ROPE
            F.val[wrap & (((F.iu + F.iv) % 3) == 0)] -= 0.15
            if F.face in ("front", "back"):
                pegs(F, [(-10.5, F.y.mean()), (10.5, F.y.mean())], T, r=0.6)

    def p_tassel(F):
        T.base(F, seed=14)
        if F.face in ("front", "back"):
            T.plates(F, F.alpha, 6.0, seed=14)
            T.hem(F, seed=14, clip=3)

    def p_tassel_back(F):
        T.base(F, seed=15)
        if F.face in ("front", "back"):
            T.plates(F, F.alpha, 6.0, seed=15)
            F.alpha &= ~((np.abs(F.lx) < 0.6) & (F.v > 3))
            T.hem(F, seed=15, clip=3)

    def p_collar(F):
        twist(F, WOOD, 3)                                    # tier 2: carved heartwood root collar (F1: vine)
        F.val -= 0.05
        if F.face == "top":
            r = np.maximum(np.abs(F.lx) / 10.0, np.abs(F.lz) / 8.5)
            F.mat[r < 0.7] = CLOTH
            F.val[r < 0.7] -= 0.3
        if F.face == "front":
            for cu in (3.0, F.fw - 3.0, F.fw / 2.0):
                T.leaflet(F, cu, 1.4)

    def p_pauldron(F):
        T.base(F, seed=16, scars=False)
        if F.is_side():
            dark_rim(F)
            rope_band(F, -0.6, 0.6)

    def p_pauldron_cap(F):
        """tier 2: raised shoulder cap - heartwood rim, two pegs, sap line along the top."""
        T.base(F, seed=17, scars=False)
        if F.is_side():
            F.mat[F.v < 1] = WOOD
            F.val[F.v < 1] += 0.06
            F.mat[F.v > F.fh - 1] = DK
            F.val[F.v > F.fh - 1] = 0.2
        elif F.face == "top":
            sap_line_local(F, 0.0, axis="lx", along="lz", lo=-5.0, hi=5.0)
            for z in (-5.0, 5.0):
                m = (np.abs(F.lz - z) < 1.0) & (np.abs(F.lx - 2.5) < 1.0)
                F.mat[m] = WOOD
                F.val[m] = 0.1

    def p_pauldron_lame(F):
        T.base(F, seed=18, scars=False)
        if F.is_side():
            cut_rim(F, "top")
            T.hem(F, seed=18, clip=0)

    def p_vine(F):
        twist(F, VINE, 3)
        if F.face == "top":
            for k in range(2, F.fh - 1, 5):
                T.leaflet(F, 1.5, k + 0.5)

    def p_sleeve(F):
        mottle(F, scale=8, amp=0.03, seed=21)
        if F.is_side():
            coord = _horiz(F)
            F.val += 0.05 * np.round(np.sin(2 * math.pi * coord / 3) * 1.5) / 1.5
            rope_band(F, 4.0, 6.0)
            rope_band(F, -7.5, -5.5)

    CHEST_OVR = {
        "Cuirass": dict(mat=BARK, paint=p_cuirass),
        "R-Breast": dict(mat=BARK, paint=p_breast),
        "Collar": dict(paint=p_collar),
        "Plackart": dict(mat=BARK, paint=p_plackart),
        "VineBelt": dict(mat=BARK, paint=p_belt),
        "R-Tassel": dict(mat=BARK, paint=p_tassel, size=(12, 13, 1), offset=(0, -6.5, 0)),
        "TasselBack": dict(mat=BARK, paint=p_tassel_back, size=(24, 13, 1), offset=(0, -6.5, 0)),
        "R-Pauldron": dict(mat=BARK, paint=p_pauldron),
        "R-PauldronLame": dict(mat=BARK, paint=p_pauldron_lame),
        "L-Vine": dict(paint=p_vine),
        "L-VineLeafA": dict(mat=LEAF, paint=T.p_leaf, size=T.LEAF_SIZE),
        "L-VineLeafB": dict(mat=LEAF, paint=T.p_leaf_hang, size=T.LEAF_SIZE_SMALL),
        "R-Sleeve": dict(mat=CLOTH, paint=p_sleeve),
    }
    CHEST_ADD = [
        # tier 2: raised cap plate on each shoulder (the extra shoulder layer)
        dict(name="R-PauldronCap", bone="R-Arm", parent="R-Pauldron", pivot=(0.8, 2.5, 0), size=(9, 3, 13), mat=BARK,
             paint=p_pauldron_cap, mirror=True),
        dict(name="Clasp", bone="Belly", pivot=(0, -5.8, 11.0), size=(6, 6, 2), mat=WOOD, paint=lambda F: knot_boss(F, T),
             skip=("back",)),
        dict(name="R-ShoulderLeaf", bone="R-Arm", parent="R-Pauldron", pivot=(-2.0, 2.0, -3.0), rot=(-20, 0, 55),
             size=T.LEAF_SIZE, offset=(0, T.LEAF_SIZE[1] / 2.0, 0), mat=LEAF, paint=T.p_leaf, double=True),
    ] + list(T.MARK_CHEST)

    # ---------------- HANDS
    def p_bracer(F):
        T.base(F, seed=20)
        if F.is_side():
            T.plates(F, F.alpha, 7.0, seed=20)
            cut_rim(F, "top")
            rope_band(F, 2.6, 4.6)
            wood_band(F, -5.0, -3.0, T)
            if F.face in ("front", "back"):
                pegs(F, [(-2.5, -4.0), (2.5, -4.0)], T, local=True, r=0.7)

    def p_bracer_plate(F):
        T.base(F, seed=21, scars=False)
        if F.is_side():
            F.val[F.v < 1] += 0.05
            T.hem(F, seed=21, clip=0)
            if F.face in ("left", "right"):
                m = ((np.abs(F.lz) < 0.9) & ((np.abs(F.ly - 3.5) < 0.9) | (np.abs(F.ly + 1.5) < 0.9))) & F.alpha
                F.mat[m] = WOOD
                F.val[m] = 0.1

    def p_glove(F):
        T.base(F, seed=22, scars=False)
        if F.is_side():
            wrap = ((F.ly > 1.0) & (F.ly < 3.0)) | ((F.ly > -3.0) & (F.ly < -1.0))
            stamp(F, wrap, ROPE, hl=0.12, lo=0.12, shadow=0.16)
            F.val[wrap & (((F.iu + F.iv) % 3) == 0)] -= 0.15
            fingers = F.ly < -4.0
            F.mat[fingers] = CLOTH
            F.val[fingers] -= 0.05
            F.val[fingers & ((F.iu % 3) == 0)] -= 0.1
        elif F.face == "bottom":
            F.mat[:] = CLOTH
            F.val -= 0.15

    def p_glove_cuff(F):
        twist(F, WOOD, 3)                                    # tier 2: heartwood cuff
        F.val -= 0.04

    HANDS_OVR = {
        "R-Bracer": dict(mat=BARK, paint=p_bracer),
        "R-BracerPlate": dict(mat=BARK, paint=p_bracer_plate),
        "R-Glove": dict(mat=BARK, paint=p_glove),
        "R-GloveCuff": dict(paint=p_glove_cuff),
    }
    HANDS_ADD = [
        dict(name="R-Sprig", bone="R-Forearm", pivot=(-6.3, 3.0, 2.0), rot=(0, -90, 0), size=T.LEAF_SIZE,
             offset=(0, T.LEAF_SIZE[1] / 2.0, 0), mat=LEAF, paint=T.p_leaf, double=True, mirror=True),
    ]

    # ---------------- LEGS
    def p_breeches(F):
        O.cloth_folds(F, 4, seed=6)
        if F.is_side():
            F.val[F.v < 2] -= 0.08

    def p_trouser(F):
        O.cloth_folds(F, 4, seed=7)
        if F.is_side() and F.face == "left":
            stitches(F, np.abs(F.lz) < 0.5, period=2)

    def p_knee(F):
        if F.face == "front":
            knot_boss(F, T)
        else:
            T.base(F, seed=24, scars=False)

    def p_greave(F):
        T.base(F, seed=25)
        if F.is_side():
            T.plates(F, F.ly > -8.0, 9.0, seed=25)
            cut_rim(F, "top")
            wood_band(F, 6.0, 8.0, T)
            rope_band(F, -7.5, -5.5)
            if F.face == "front":
                pegs(F, [(-3.5, 7.0), (3.5, 7.0)], T, local=True, r=0.7)
            if F.face == "back":
                lace = (np.abs(np.abs(F.lx) - ((F.iv % 4) * 0.5)) < 0.5) & (np.abs(F.lx) < 2.1) & (F.ly > -5.0)
                F.mat[lace] = ROPE
                F.val[lace] = 0.0

    def p_boot(F):
        T.base(F, seed=26, scars=False)
        F.val -= 0.03
        if F.is_side():
            sole = F.ly < -2.6
            F.mat[sole] = DK
            F.val[sole] = 0.25
            F.val[sole & (F.ly > -3.6)] += 0.12
            if F.face == "front":
                cap = (F.ly > -2.6) & (F.ly < 1.5) & (np.abs(F.lx) < 5.6)
                stamp(F, cap, BARK, hl=0.14, lo=0.12, shadow=0.16, add=0.04)
            if F.face in ("left", "right"):
                wrap = (np.abs(F.lz + 3.0) < 1.6) & (F.ly > -2.6)
                stamp(F, wrap, WOOD, hl=0.12, lo=0.12, shadow=0.16)
        elif F.face == "top":
            wrap = np.abs(F.lz + 3.0) < 1.6
            stamp(F, wrap, WOOD, hl=0.12, lo=0.12, shadow=0.14)
        elif F.face == "bottom":
            F.mat[:] = DK
            F.val[:] = 0.1

    LEGS_OVR = {
        "Breeches": dict(mat=CLOTH, paint=p_breeches),
        "R-Trouser": dict(mat=CLOTH, paint=p_trouser),
        "R-Knee": dict(mat=WOOD, paint=p_knee, size=(7, 7, 2)),
        "R-Greave": dict(mat=BARK, paint=p_greave),
        "R-Boot": dict(mat=BARK, paint=p_boot),
    }

    def derive(nodes, ovr, drop=(), add=()):
        out = []
        for n in nodes:
            if n["name"] in drop:
                continue
            m = dict(n)
            m.update(ovr.get(n["name"], {}))
            out.append(m)
        return out + [dict(a) for a in add]

    return {
        "Head": derive(O.HEAD, HEAD_OVR, add=HEAD_ADD),
        "Chest": derive(O.CHEST, CHEST_OVR, drop=("Acorn", "AcornCap"), add=CHEST_ADD),
        "Hands": derive(O.HANDS, HANDS_OVR, add=HANDS_ADD),
        "Legs": derive(O.LEGS, LEGS_OVR),
    }
