"""SkyWynn Foraging armor - F1 Grove - BEECH set (v2). Geometry + paint design (ORIGINAL; no vanilla or Armory pixels).

v2 after Skyy: "beech looks too much like iron, i need to look a little more like beech wood in the game".
Colours follow the in-game Beech wood (hues / values sampled from the Beech trunk, planks and leaves textures; our own
pixels): warm orange-brown bark with long vertical grain streaks and a few knots, tan heartwood with a dark red-brown
rim on cut edges, the game's fresh beech green leaves (+ one copper accent leaf), brown spiky beechnut husks, deep
loden-green cloth. Plates read as WOOD: each plank its own tone, gentle bevels, slightly wavy hand-cut hems with small
notches; no bright hard metal rims. Same family + fit as Oak / Birch (geometry derived from ga_oak.py).
Mark: the BEECHNUT HUSK (spiky four-part cupule) - belt clasp on a leafy twig + a husk badge on the crown.
"""
import math
import numpy as np
import ga_paint as P
from ga_paint import (ROPE, VINE, BEECH, BEECHDK, CLEAF, FLEAF, HUSK, BEWOOD, UMBER, LODEN,
                      stamp, stitches, mottle, hash2)
import ga_oak as O
from ga_oak import _uv_of, _horiz, rope_band, twist, taper_top, _side_cut

TIER, TREE = "F1_Grove", "Beech"


# ------------------------------------------------------------------ beech bark painting
def beech_base(F, seed=0, scars=True):
    """in-game-beech-like bark: long vertical grain streaks (light + dark strands), soft broad value bands,
    rare small knots ('scars' flag keeps the knots)."""
    m0 = F.mat == BEECH
    h = _horiz(F)
    vert = F.y if F.is_side() else F.z
    # long streaks: noise that changes fast across, slowly along the grain
    S = np.stack([h * 1.0, vert * 0.10, np.full(h.shape, 3.0 * seed)], -1)
    n = P.vnoise(S, 2.2, 70 + seed)
    q = np.round((n - 0.5) * 4) / 4
    F.val[m0] += 0.10 * q[m0]
    # broad soft bands so big plates are not flat
    n2 = P.vnoise(F.W, 10.0, 80 + seed)
    F.val[m0] += 0.05 * np.round((n2[m0] - 0.5) * 3)
    # dark grain strands: 1 texel wide, broken, on some columns
    col = np.floor(h).astype(np.int64)
    seg = np.floor((vert + 7 * hash2(col, np.zeros_like(col), seed + 4)) / 6).astype(np.int64)
    dark = (hash2(col, seg, seed + 5) < 0.11) & m0
    F.mat[dark] = BEECHDK
    F.val[dark] = 0.62
    lite = (hash2(col, seg, seed + 6) > 0.9) & m0 & ~dark
    F.val[lite] += 0.08
    if scars and F.is_side():
        # rare knot: dark oval with a tan ring, grain bends round it
        gx = np.floor(h / 14).astype(np.int64); gy = np.floor(vert / 14).astype(np.int64)
        has = hash2(gx, gy, seed + 7) < 0.08
        cx = gx * 14 + 4 + 6 * hash2(gx, gy, seed + 8); cy = gy * 14 + 4 + 6 * hash2(gx, gy, seed + 9)
        r = np.hypot((h - cx) / 1.0, (vert - cy) / 1.5)
        core = has & (r < 1.2) & m0
        F.mat[core] = BEECHDK; F.val[core] = 0.32
        lip = has & (r >= 1.2) & (r < 1.9) & m0 & (vert > cy)
        F.val[lip] += 0.08
        halo = has & (r >= 1.2) & (r < 2.4) & m0 & (vert <= cy)
        F.val[halo] -= 0.06


def bevel_plates(F, region, pitch, seed=0, y_top=None, step=10.0):
    """overlapping wooden plates: every plate its own tone, a GENTLE light bevel on top, a soft darker shadow
    under the plate above, and a slightly wavy hand-cut lower edge (offset in 2-3 texel chunks)."""
    region = np.asarray(region, bool) & F.alpha
    if not region.any():
        return
    if y_top is None:
        y_top = F.y[region].max() + 1e-3
    h = _horiz(F)
    chunk = np.floor(h / 3).astype(np.int64)
    s0 = (y_top - F.y) / pitch
    row0 = np.floor(s0).astype(np.int64)
    wav = np.floor(hash2(chunk, row0, seed + 2) * 2.0 - 0.3)       # -1, 0 or +1 texel wobble
    s = (y_top - F.y + wav) / pitch
    k = np.floor(s); f = s - k
    ki = k.astype(np.int64)
    shingle = np.floor((h + 5 * hash2(ki, np.full(h.shape, 1, np.int64), seed)) / step).astype(np.int64)
    tone = (hash2(shingle, ki, seed + 3) - 0.5) * 0.10
    F.val[region] += tone[region] + 0.04 * (0.5 - f[region])
    px = 1.0 / pitch
    under = region & (f > 1 - px) & (k >= 0)
    F.mat[under] = BEECHDK
    F.val[under] = 0.55
    bev = region & (f < px) & (k > 0)
    F.val[bev] += 0.06
    seam = region & (np.mod(h + 5 * hash2(ki, np.full(h.shape, 1, np.int64), seed), step) < 1.0) & (k > 0) & ~under
    F.mat[seam] = BEECHDK
    F.val[seam] = 0.68


def bevel_edges(F, which=("bottom",), clip=2, notch=True):
    """soft hand-cut edge: end-grain rim (tan with a dark outer line) + small irregular notches + rounded corners."""
    d = {"top": F.v, "bottom": F.fh - F.v, "left": F.u, "right": F.fw - F.u}
    for w in which:
        if w == "bottom":
            if notch and F.face in ("front", "back"):
                c = np.floor(F.u / 2).astype(np.int64)
                F.alpha &= ~((d[w] < 1) & (hash2(c, np.full(c.shape, 5, np.int64), int(F.fw * 7 + F.fh)) < 0.35))
            m = (d[w] < 1) & F.alpha
            F.mat[m] = BEECHDK
            F.val[m] = 0.5
            m2 = (d[w] >= 1) & (d[w] < 2) & F.alpha
            F.val[m2] -= 0.05
        elif w == "top":
            m = (d[w] < 1) & F.alpha
            F.val[m] += 0.05
    if clip and F.face in ("front", "back"):
        bot = d["bottom"]
        side = np.minimum(d["left"], d["right"])
        corner = (bot + side) < clip + 0.5
        corner |= (bot < clip + 1) & (side < 1)          # rounder corner
        F.alpha &= ~corner


def cut_rim(F, which="bottom"):
    d = {"top": F.v, "bottom": F.fh - F.v, "left": F.u, "right": F.fw - F.u}[which]
    m = (d < 1) & F.alpha
    F.mat[m] = BEWOOD
    F.val[m] -= 0.05
    return m


def outline_cut(F):
    a = F.alpha
    e = a & ~(P._shift(a, 0, 1) & P._shift(a, 0, -1))
    F.val[e] -= 0.18


def leaflet(F, cu, cv, mat, s=1):
    m = (np.abs(F.u - cu) < 1.0 * s + 0.01) & (np.abs(F.v - cv) < 0.6 * s + 0.01)
    m |= (np.abs(F.u - cu) < 0.51) & (np.abs(F.v - cv) < 1.1 * s + 0.01)
    stamp(F, m, mat, hl=0.2, lo=0.1, shadow=0.12, add=0.05)


# ------------------------------------------------------------------ quads: beech leaf, husk spikes, sprig
def p_beech_leaf(F, mat=CLEAF, stem_at_bottom=True):
    """oval beech leaf: pointed tip, gently wavy edge, straight parallel side veins."""
    F.mat[:] = mat
    t = (F.fh - F.v) / F.fh if stem_at_bottom else F.v / F.fh
    hw = (F.fw / 2.0) * np.clip(np.sin(np.pi * np.clip(t, 0, 1) ** 0.85), 0, 1) ** 0.8
    hw = hw - 0.4 * (np.floor(F.v / 2) % 2)
    du = F.u - F.fw / 2.0
    keep = np.abs(du) <= hw + 0.2
    stem = (np.abs(du) < 0.51) & (t < 0.12)
    F.alpha &= keep | stem
    F.mat[stem] = HUSK
    mid = np.abs(du) < 0.5
    F.val[mid] -= 0.12
    vein = keep & ~mid & (np.mod(F.v + np.abs(du) * 0.7, 3.0) < 1.0)
    F.val[vein] -= 0.07
    F.val[(du < -0.5) & keep & ~vein] += 0.05
    F.val += 0.08 * (t - 0.5)


def p_copper_leaf(F):
    p_beech_leaf(F, CLEAF)


def p_green_leaf(F):
    p_beech_leaf(F, FLEAF)


def p_husk_spikes(F):
    """alpha-cut spiky husk silhouette (crossed quads around the clasp): four lobes edged with short bristles."""
    F.mat[:] = HUSK
    cu, cv = F.fw / 2.0, F.fh / 2.0
    du, dv = F.u - cu, F.v - cv
    r = np.hypot(du, dv)
    ang = np.arctan2(dv, du)
    lobe = 0.66 + 0.34 * np.abs(np.sin(2 * ang))                         # four-part cupule (splits on the axes)
    bristle = (np.mod(F.iu + F.iv, 2) == 0)
    R = (min(F.fw, F.fh) / 2.0) * lobe
    F.alpha &= (r <= R - 1.0) | ((r <= R) & bristle)
    F.val += 0.14
    F.val[(r > R - 1.6)] -= 0.16
    split = (np.abs(du) < 0.5) | (np.abs(dv) < 0.5)
    F.val[split & (r > 1.5)] -= 0.2


def p_sprig(F):
    """beech twig with one copper + one green leaf (alpha cut)."""
    F.alpha[:] = False
    cx = F.fw / 2.0
    t = (F.fh - F.v) / F.fh
    stem_x = cx - (t - 0.1) * 1.5
    stem = (np.abs(F.u - stem_x) < 0.6) & (t < 0.8)
    F.alpha |= stem
    F.mat[stem] = HUSK
    F.val[stem] = -0.1
    for (lx, ly, rx, ry, mat) in ((cx + 1.8, F.fh * 0.45, 1.5, 2.4, CLEAF), (cx - 1.6, F.fh * 0.18, 1.4, 2.1, FLEAF)):
        e = ((F.u - lx) / rx) ** 2 + ((F.v - ly) / ry) ** 2 <= 1.0
        F.alpha |= e
        F.mat[e] = mat
        F.val[e] = 0.0 + 0.08 * (F.u[e] < lx)


def husk_box(F):
    """beechnut husk on a box: four pale bristly lobes split open around a glossy dark three-sided nut."""
    F.mat[:] = HUSK
    F.val += 0.18
    if F.face in ("front", "top"):
        cu, cv = F.fw / 2.0, F.fh / 2.0
        du, dv = F.u - cu, F.v - cv
        bristle = (np.mod(F.iu + F.iv, 2) == 0)
        F.val[bristle] -= 0.14
        split = (np.abs(du) < 0.6) | (np.abs(dv) < 0.6)
        F.mat[split] = BEECHDK
        F.val[split] = 0.25
        nut = (np.abs(du) + np.abs(dv)) < 1.6
        F.mat[nut] = BEECHDK
        F.val[nut] = 0.55
        F.val[nut & (du < 0) & (dv < 0)] = 0.9
    else:
        F.val[(np.mod(F.iu + F.iv, 2) == 0)] -= 0.14


# ================================================================== HEAD
def p_cap(F):
    beech_base(F, seed=1)
    if F.is_side():
        rope_band(F, -4.0, -2.0)
        F.val[F.v < 1] += 0.04
        if F.face == "front":
            k = (np.abs(F.lx - 4.5) < 1.6) & (np.abs(F.ly + 3.0) < 1.6)
            stamp(F, k, ROPE, hl=0.2, lo=0.1, shadow=0.16, add=0.04)


def p_cap_upper(F):
    beech_base(F, seed=2, scars=False)
    if F.is_side():
        F.val[F.v < 1] += 0.05
        F.mat[F.v > F.fh - 1] = BEECHDK
        F.val[F.v > F.fh - 1] = 0.5


def p_dome(F):
    beech_base(F, seed=3, scars=False)
    if F.face == "top":
        r = np.hypot(F.lx, F.lz)
        ring = r < 5.5
        F.mat[ring] = BEWOOD
        F.val[ring & ((np.floor(r * 0.9) % 2) == 1)] -= 0.1
        F.val[r < 1.2] -= 0.1
    else:
        cut_rim(F, "top")


def p_brim(F):
    beech_base(F, seed=4, scars=False)
    if F.is_side():
        F.val[F.v < 1] += 0.05
        F.mat[F.v > F.fh - 1] = BEECHDK
        F.val[F.v > F.fh - 1] = 0.5
    elif F.face == "top":
        r = np.maximum(np.abs(F.lx) / 18.0, np.abs(F.lz) / 17.0)
        F.val[r > 0.93] += 0.08
    elif F.face == "bottom":
        F.mat[:] = BEWOOD
        F.val -= 0.2


def p_helmback(F):
    beech_base(F, seed=5)
    if F.is_side():
        bevel_plates(F, F.alpha, 6.0, seed=5)
        bevel_edges(F, ("bottom",), clip=2)


def p_cheek(F):
    beech_base(F, seed=6, scars=False)
    if F.is_side():
        bevel_plates(F, F.alpha, 6.0, seed=6)
        bevel_edges(F, ("bottom",), clip=0)
        d = F.fh - F.v
        F.alpha &= ~((d < 2.5) & ((F.u < 2) if F.face == "left" else (F.u > F.fw - 2)))


def leaf_blade(F, length, half_w):
    """pointed-oval beech-leaf point: sharp tip, widest ~60% down, narrowing again toward the base."""
    top = F.ly.max() + 0.5
    s_ = np.clip((top - F.ly) / length, 0, 1)            # 0 tip .. 1 base
    allow = half_w * np.sin(np.pi * s_ * 0.8) ** 0.75 + 0.35
    F.alpha &= ~(np.abs(F.lx) > allow)


def p_crown_mid(F):
    beech_base(F, seed=7, scars=False)
    leaf_blade(F, 13.0, 3.4)
    _side_cut(F, 13.0)
    if F.face in ("front", "back"):
        outline_cut(F)
        mid = np.abs(F.lx) < 0.5
        F.val[mid] += 0.12
        F.val[(F.lx > 0.5) & F.alpha] -= 0.05


def p_crown_side(F):
    beech_base(F, seed=8, scars=False)
    leaf_blade(F, 11.0, 2.9)
    _side_cut(F, 11.0)
    if F.face in ("front", "back"):
        outline_cut(F)
        F.val[np.abs(F.lx) < 0.5] += 0.12
        F.val[(F.lx > 0.5) & F.alpha] -= 0.05


HEAD_OVR = {
    "HelmCap": dict(mat=BEECH, paint=p_cap),
    "HelmUpper": dict(mat=BEECH, paint=p_cap_upper),
    "HelmDome": dict(mat=BEECH, paint=p_dome),
    "HelmBrim": dict(mat=BEECH, paint=p_brim),
    "HelmBack": dict(mat=BEECH, paint=p_helmback),
    "R-Cheek": dict(mat=BEECH, paint=p_cheek),
    # broad leaf-blade crown points (Oak: narrow jagged; Birch: tall thin spikes)
    "CrownMid": dict(mat=BEECH, paint=p_crown_mid, size=(7, 13, 2), pivot=(0, 17.5, 15.25)),
    "R-CrownSide": dict(mat=BEECH, paint=p_crown_side, size=(6, 11, 2), pivot=(-9.0, 16.0, 14.75), rot=(0, 0, 16)),
    "R-HelmLeaf": dict(mat=FLEAF, paint=p_green_leaf, size=(5, 8)),
}
HEAD_ADD = [
    # husk badge at the base of the middle crown point
    dict(name="HelmHusk", bone="Head", pivot=(0, 10.5, 16.8), size=(5, 5, 2), mat=HUSK, paint=husk_box,
         skip=("back",)),
    # one fresh green leaf behind each copper one (copper + green = the beech mark colours)
    dict(name="R-HelmLeafCopper", bone="Head", pivot=(-14.0, 15.0, 5.0), rot=(-10, -55, 30), size=(4, 7),
         offset=(0, 3.5, 0), mat=CLEAF, paint=p_copper_leaf, double=True, mirror=True),
]


# ================================================================== CHEST
def _laced_gap(F, halfw, y0, y1, k=1.0):
    gap = np.abs(F.x) < halfw
    F.mat[gap] = LODEN
    F.val[gap] = -0.12
    ph = F.y % 4.0
    lace = gap & (np.abs(np.abs(F.x) - np.abs(ph - 2.0) * k) < 0.55)
    F.mat[lace] = ROPE
    F.val[lace] = 0.05
    O.sap_vein(F, 0.0, y0, y1, faint=0.35)


def p_cuirass(F):
    beech_base(F, seed=10)
    if F.is_side():
        bevel_plates(F, F.alpha, 11.0, seed=10)
        if F.face == "front":
            _laced_gap(F, 2.6, 66.0, 84.0)


def p_breast(F):
    beech_base(F, seed=11)
    if F.is_side():
        bevel_plates(F, F.alpha, 9.0, seed=11)
        bevel_edges(F, ("bottom", "top"), clip=2)
        if F.face == "front":
            inner = (np.abs(F.x) < 3.1) & F.alpha
            F.mat[inner] = BEWOOD
            eye = inner & ((np.floor(F.y) % 4) == 1)
            F.mat[eye] = ROPE
            F.val[eye] = -0.05


def p_plackart(F):
    beech_base(F, seed=12)
    if F.is_side():
        bevel_plates(F, F.alpha, 8.0, seed=12)
        if F.face == "front":
            _laced_gap(F, 2.0, 56.0, 68.0, k=0.8)


def p_belt(F):
    """smooth beech bark belt with wrapped rope ends (no ivy)."""
    beech_base(F, seed=13, scars=False)
    if F.is_side():
        F.val[F.v < 1] += 0.05
        F.mat[F.v > F.fh - 1] = BEECHDK
        F.val[F.v > F.fh - 1] = 0.5
        wrap = (np.abs(np.abs(F.x) - 6.5) < 1.5)
        F.mat[wrap & F.alpha] = ROPE
        F.val[wrap & (((F.iu + F.iv) % 3) == 0)] -= 0.15


def p_tassel(F):
    beech_base(F, seed=14)
    if F.face in ("front", "back"):
        bevel_plates(F, F.alpha, 6.0, seed=14)
        bevel_edges(F, ("bottom",), clip=3)


def p_tassel_back(F):
    beech_base(F, seed=15)
    if F.face in ("front", "back"):
        bevel_plates(F, F.alpha, 6.0, seed=15)
        # two broad panels with a clean gap between them (no strips)
        F.alpha &= ~((np.abs(F.lx) < 0.6) & (F.v > 3))
        bevel_edges(F, ("bottom",), clip=3)


def p_collar(F):
    twist(F, VINE, 3)
    if F.face == "top":
        r = np.maximum(np.abs(F.lx) / 10.0, np.abs(F.lz) / 8.5)
        F.mat[r < 0.7] = LODEN
        F.val[r < 0.7] -= 0.3
    if F.face == "front":
        leaflet(F, 3.0, 1.4, FLEAF)
        leaflet(F, F.fw - 3.0, 1.4, FLEAF)
        leaflet(F, F.fw / 2.0, 1.4, CLEAF)


def p_pauldron(F):
    beech_base(F, seed=16, scars=False)
    if F.is_side():
        F.val[F.v < 1] += 0.05
        F.mat[F.v > F.fh - 1] = BEECHDK
        F.val[F.v > F.fh - 1] = 0.5
        rope_band(F, -0.6, 0.6)


def p_pauldron_top(F):
    beech_base(F, seed=17, scars=False)
    if F.is_side():
        F.val[F.v < 1] += 0.05
        F.mat[F.v > F.fh - 1] = BEECHDK
        F.val[F.v > F.fh - 1] = 0.5


def p_pauldron_lame(F):
    beech_base(F, seed=18, scars=False)
    if F.is_side():
        cut_rim(F, "top")
        bevel_edges(F, ("bottom",), clip=0)


def p_vine(F):
    twist(F, VINE, 3)
    if F.face == "top":
        for i, k in enumerate(range(2, F.fh - 1, 5)):
            leaflet(F, 1.5, k + 0.5, CLEAF if i % 3 == 2 else FLEAF)


def p_sleeve(F):
    mottle(F, scale=8, amp=0.03, seed=21)
    if F.is_side():
        coord = _horiz(F)
        F.val += 0.05 * np.round(np.sin(2 * math.pi * coord / 3) * 1.5) / 1.5
        rope_band(F, 4.0, 6.0)
        rope_band(F, -7.5, -5.5)


CHEST_OVR = {
    "Cuirass": dict(mat=BEECH, paint=p_cuirass),
    "R-Breast": dict(mat=BEECH, paint=p_breast),
    "Collar": dict(paint=p_collar),
    "Plackart": dict(mat=BEECH, paint=p_plackart),
    "VineBelt": dict(mat=BEECH, paint=p_belt),
    "R-Tassel": dict(mat=BEECH, paint=p_tassel, size=(12, 12, 1), offset=(0, -6.0, 0)),
    "TasselBack": dict(mat=BEECH, paint=p_tassel_back, size=(24, 12, 1), offset=(0, -6.0, 0)),
    "R-Pauldron": dict(mat=BEECH, paint=p_pauldron),
    "R-PauldronLame": dict(mat=BEECH, paint=p_pauldron_lame),
    "L-Vine": dict(paint=p_vine),
    "L-VineLeafA": dict(mat=FLEAF, paint=p_green_leaf),
    "L-VineLeafB": dict(mat=CLEAF, paint=lambda F: p_beech_leaf(F, CLEAF, stem_at_bottom=False)),
    "R-Sleeve": dict(mat=LODEN, paint=p_sleeve),
}
CHEST_DROP = ("Acorn", "AcornCap")
CHEST_ADD = [
    # beechnut husk clasp: a bristly box + two crossed alpha-cut husk silhouettes behind it (spiky outline, no bulk)
    dict(name="Husk", bone="Belly", pivot=(0, -5.8, 12.0), size=(6, 6, 3), mat=HUSK, paint=husk_box, skip=("back",)),
    dict(name="HuskSpikesA", bone="Belly", pivot=(0, -5.8, 12.6), rot=(0, 0, 0), size=(11, 11), mat=HUSK,
         paint=p_husk_spikes, double=True),
    # the husk hangs on a beech twig: two green leaves fanning out behind it
    dict(name="HuskLeafR", bone="Belly", pivot=(-3.0, -4.0, 12.3), rot=(0, 0, 58), size=(5, 8), offset=(0, 4.0, 0),
         mat=FLEAF, paint=p_green_leaf, double=True),
    dict(name="HuskLeafL", bone="Belly", pivot=(3.0, -4.0, 12.2), rot=(0, 0, -58), size=(5, 8), offset=(0, 4.0, 0),
         mat=FLEAF, paint=p_green_leaf, double=True),
    # a beech sprig tucked into the right shoulder plate (the left shoulder has the vine)
    dict(name="R-ShoulderLeaf", bone="R-Arm", parent="R-Pauldron", pivot=(-2.0, 2.0, -3.5), rot=(-20, 0, 62), size=(5, 8),
         offset=(0, 4.0, 0), mat=FLEAF, paint=p_green_leaf, double=True),
    dict(name="R-ShoulderLeafB", bone="R-Arm", parent="R-Pauldron", pivot=(-2.0, 2.0, -1.0), rot=(15, 0, 40), size=(4, 7),
         offset=(0, 3.5, 0), mat=FLEAF, paint=p_green_leaf, double=True),
    # broad second plate overlapping the top of each shoulder (smooth layered look, ~1 unit thick)
    dict(name="R-PauldronTop", bone="R-Arm", parent="R-Pauldron", pivot=(0.5, 2.0, 0), size=(10, 2, 13), mat=BEECH,
         paint=p_pauldron_top, mirror=True),
]


# ================================================================== HANDS
def p_bracer(F):
    beech_base(F, seed=20)
    if F.is_side():
        bevel_plates(F, F.alpha, 7.0, seed=20)
        cut_rim(F, "top")
        rope_band(F, 2.6, 4.6)
        rope_band(F, -5.0, -3.0)


def p_bracer_plate(F):
    beech_base(F, seed=21, scars=False)
    if F.is_side():
        F.val[F.v < 1] += 0.05
        bevel_edges(F, ("bottom",), clip=0)


def p_glove(F):
    beech_base(F, seed=22, scars=False)
    if F.is_side():
        wrap = ((F.ly > 1.0) & (F.ly < 3.0)) | ((F.ly > -3.0) & (F.ly < -1.0))
        stamp(F, wrap, ROPE, hl=0.12, lo=0.12, shadow=0.16)
        F.val[wrap & (((F.iu + F.iv) % 3) == 0)] -= 0.15
        fingers = F.ly < -4.0
        F.mat[fingers] = LODEN
        F.val[fingers] -= 0.05
        F.val[fingers & ((F.iu % 3) == 0)] -= 0.1
    elif F.face == "bottom":
        F.mat[:] = LODEN
        F.val -= 0.15


HANDS_OVR = {
    "R-Bracer": dict(mat=BEECH, paint=p_bracer),
    "R-BracerPlate": dict(mat=BEECH, paint=p_bracer_plate),
    "R-Glove": dict(mat=BEECH, paint=p_glove),
}
HANDS_ADD = [
    dict(name="R-Sprig", bone="R-Forearm", pivot=(-6.3, 3.0, 2.0), rot=(0, -90, 0), size=(7, 9), offset=(0, 4.5, 0),
         mat=CLEAF, paint=p_sprig, double=True, mirror=True),
]


# ================================================================== LEGS
def p_breeches(F):
    O.cloth_folds(F, 4, seed=6)
    if F.is_side():
        F.val[F.v < 2] -= 0.08


def p_trouser(F):
    O.cloth_folds(F, 4, seed=7)
    if F.is_side() and F.face == "left":
        stitches(F, np.abs(F.lz) < 0.5, period=2)


def p_knee(F):
    beech_base(F, seed=24, scars=False)
    if F.face == "front":
        F.val[F.v < 1] += 0.05
        bevel_edges(F, ("bottom",), clip=2)


def p_greave(F):
    beech_base(F, seed=25)
    if F.is_side():
        bevel_plates(F, F.ly > -8.0, 9.0, seed=25)
        cut_rim(F, "top")
        rope_band(F, 6.0, 8.0)
        rope_band(F, -7.5, -5.5)
        if F.face == "back":
            lace = (np.abs(np.abs(F.lx) - ((F.iv % 4) * 0.5)) < 0.5) & (np.abs(F.lx) < 2.1) & (F.ly > -5.0)
            F.mat[lace] = ROPE
            F.val[lace] = 0.0


def p_boot(F):
    beech_base(F, seed=26, scars=False)
    F.val -= 0.03
    if F.is_side():
        sole = F.ly < -2.6
        F.mat[sole] = BEECHDK
        F.val[sole] = 0.2
        F.val[sole & (F.ly > -3.6)] += 0.12
        if F.face == "front":
            cap = (F.ly > -2.6) & (F.ly < 1.5) & (np.abs(F.lx) < 5.6)
            stamp(F, cap, BEECH, hl=0.14, lo=0.12, shadow=0.16, add=0.04)
        if F.face in ("left", "right"):
            wrap = (np.abs(F.lz + 3.0) < 1.6) & (F.ly > -2.6)
            stamp(F, wrap, ROPE, hl=0.12, lo=0.12, shadow=0.16)
            F.val[wrap & (((F.iu + F.iv) % 3) == 0)] -= 0.15
    elif F.face == "top":
        wrap = np.abs(F.lz + 3.0) < 1.6
        stamp(F, wrap, ROPE, hl=0.12, lo=0.12, shadow=0.14)
        F.val[wrap & (((F.iu + F.iv) % 3) == 0)] -= 0.15
    elif F.face == "bottom":
        F.mat[:] = BEECHDK
        F.val[:] = 0.1


LEGS_OVR = {
    "Breeches": dict(mat=LODEN, paint=p_breeches),
    "R-Trouser": dict(mat=LODEN, paint=p_trouser),
    "R-Knee": dict(mat=BEECH, paint=p_knee),
    "R-Greave": dict(mat=BEECH, paint=p_greave),
    "R-Boot": dict(mat=BEECH, paint=p_boot),
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


HEAD = derive(O.HEAD, HEAD_OVR, add=HEAD_ADD)
CHEST = derive(O.CHEST, CHEST_OVR, drop=CHEST_DROP, add=CHEST_ADD)
HANDS = derive(O.HANDS, HANDS_OVR, add=HANDS_ADD)
LEGS = derive(O.LEGS, LEGS_OVR)
PIECES = {"Head": HEAD, "Chest": CHEST, "Hands": HANDS, "Legs": LEGS}
