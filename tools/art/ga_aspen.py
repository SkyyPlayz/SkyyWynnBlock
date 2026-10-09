"""SkyWynn Foraging armor - F1 Grove - ASPEN set (v1). Geometry + paint design (ORIGINAL; no vanilla or Armory pixels).

Started from the IN-GAME Aspen wood: hues / values sampled from the game's Aspen trunk, log end, softwood planks and
golden aspen leaves; our own pixels. Pale khaki-cream bark with soft horizontal bands and DARK EYE-SHAPED SCARS
(aspen bark), pale cream heartwood with rings on cut edges, the game's golden-orange aspen leaves, russet cloth.
Plate shapes vs Oak (jagged), Birch (rounded / curled), Beech (broad smooth), Ash (chevrons): SLENDER TALL VERTICAL
SLATS - every plate is a narrow upright strip with a thin gap line, the strips end at staggered lengths with rounded
tips and open gaps at the hems (light, airy); slim round-topped spire crown points.
Mark: TREMBLING ASPEN LEAVES - round golden leaves on long thin stalks hanging at different angles from a carved
heartwood clasp on the belt, plus a small cluster at the helmet temple. Same family + fit as the other F1 sets
(geometry derived from ga_oak.py).
"""
import math
import numpy as np
import ga_paint as P
from ga_paint import (ROPE, VINE, ASPEN, ASPENDK, GOLDLEAF, ASPWOOD, RUSSET,
                      stamp, stitches, mottle, hash2)
import ga_oak as O
from ga_oak import _horiz, rope_band, twist, _side_cut

TIER, TREE = "F1_Grove", "Aspen"
SLAT = 4.0          # slat width (texels)


# ------------------------------------------------------------------ aspen bark painting
def _eyes(F, cell_w=9.0, cell_h=10.0, seed=0, chance=0.55):
    """dark eye-shaped (almond) scars, sparse, staggered rows. returns (eye, eye_core, eye_lid) masks."""
    h = _horiz(F)
    vert = F.y if F.is_side() else F.z
    row = np.floor(vert / cell_h)
    hh = h + np.where(np.mod(row, 2) == 0, 0.0, cell_w / 2.0)
    col = np.floor(hh / cell_w)
    ri = row.astype(np.int64); ci = col.astype(np.int64)
    on = hash2(ci, ri, seed + 31) < chance
    a = 2.6 + 1.4 * hash2(ci, ri, seed + 32)                      # half width 2.6 .. 4.0
    jx = (hash2(ci, ri, seed + 33) - 0.5) * 2.0
    jy = (hash2(ci, ri, seed + 34) - 0.5) * 3.0
    du = (np.mod(hh, cell_w) - cell_w / 2.0 - jx) / a
    dv = (np.mod(vert, cell_h) - cell_h / 2.0 - jy)
    lens = 1.5 * np.clip(1.0 - du ** 2, 0, 1)                     # almond: tall in the middle, pointed at both ends
    eye = on & (np.abs(du) < 1.0) & (np.abs(dv) < lens)
    core = eye & (np.abs(du) < 0.45) & (np.abs(dv) < 0.6)
    lid = on & ~eye & (np.abs(du) < 1.15) & (dv < 0) & (np.abs(dv) < lens + 1.0)   # lit upper lid
    return eye, core, lid


def aspen_base(F, seed=0, scars=True):
    """in-game-aspen-like bark: pale khaki-cream with soft horizontal bands, a few short dark horizontal dashes and
    (optionally) dark eye-shaped scars."""
    m0 = F.mat == ASPEN
    n2 = P.vnoise(F.W, 9.0, 90 + seed)
    F.val[m0] += 0.03 * np.round((n2[m0] - 0.5) * 3)
    vert = F.y if F.is_side() else F.z
    band = np.floor(vert / 2.0).astype(np.int64)
    F.val[m0] += (0.05 * np.round((hash2(band, band * 0 + 3, seed + 7) - 0.5) * 2) / 2)[m0]
    if F.is_side():
        h = _horiz(F)
        # short horizontal dashes (like the game's aspen side texture)
        dc = np.floor(h / 3.0).astype(np.int64)
        dr = np.floor(vert).astype(np.int64)
        dash = (hash2(dc, dr, seed + 9) < 0.05) & m0
        F.mat[dash] = ASPENDK
        F.val[dash] = 0.4
        if scars:
            eye, core, lid = _eyes(F, seed=seed)
            e = eye & (F.mat == ASPEN)
            F.mat[e] = ASPENDK
            F.val[e] = -0.12
            F.val[core & e] = -0.36
            F.val[lid & (F.mat == ASPEN)] += 0.08


def slats(F, region, w=SLAT, seed=0, joints=True):
    """slender tall vertical plates: narrow upright strips, a thin dark gap line between them, a lit left rim,
    each strip its own tone, and (sometimes) one staggered horizontal joint per strip."""
    region = np.asarray(region, bool) & F.alpha
    if not region.any() or not F.is_side():
        return
    h = _horiz(F)
    c = np.floor(h / w).astype(np.int64)
    f = h / w - np.floor(h / w)
    tone = (hash2(c, c * 0 + 1, seed + 3) - 0.5) * 0.10
    F.val[region] += tone[region]
    gap = region & (f < 1.0 / w)
    F.mat[gap] = ASPENDK
    F.val[gap] = 0.72
    lit = region & (f >= 1.0 / w) & (f < 2.0 / w)
    F.val[lit] += 0.06
    F.val[region & (f > 1 - 1.0 / w)] -= 0.04
    if joints:
        jy = 3.0 + 9.0 * hash2(c, c * 0 + 2, seed + 4)
        y = F.y - F.y[region].min()
        has = hash2(c, c * 0 + 5, seed + 6) < 0.25
        j = region & has & (np.abs(y - jy) < 0.5) & ~gap
        F.mat[j] = ASPENDK
        F.val[j] = 0.65
        F.val[region & has & (np.abs(y - jy + 1.0) < 0.5) & ~gap] += 0.07


def slat_hem(F, w=SLAT, seed=0, airy=3, max_short=3):
    """bottom hem: every strip ends at its own length with rounded tips; the gaps between strips open up near the
    hem (light, airy); pale cut end-grain line at each tip."""
    if F.face not in ("front", "back", "left", "right"):
        return
    h = _horiz(F)
    c = np.floor(h / w).astype(np.int64)
    f = h / w - np.floor(h / w)
    short = np.floor(hash2(c, c * 0 + 7, seed + 8) * (max_short + 1))
    d = F.fh - F.v - short                                  # distance above this strip's tip
    corner = (d < 1) & ((f < 1.0 / w) | (f > 1 - 1.0 / w))
    corner |= (d < 2) & (f < 1.0 / w)
    F.alpha &= ~((d < 0) | corner)
    if airy:
        F.alpha &= ~((f < 1.0 / w) & (d < airy))
    tip = (d >= 0) & (d < 1) & F.alpha
    F.mat[tip] = ASPWOOD
    F.val[tip] -= 0.02


def cut_rim(F, which="bottom"):
    d = {"top": F.v, "bottom": F.fh - F.v, "left": F.u, "right": F.fw - F.u}[which]
    m = (d < 1) & F.alpha
    F.mat[m] = ASPWOOD
    F.val[m] -= 0.04
    return m


def outline_cut(F):
    a = F.alpha
    e = a & ~(P._shift(a, 0, 1) & P._shift(a, 0, -1))
    F.val[e] -= 0.16


def leaflet(F, cu, cv, mat=GOLDLEAF, s=1):
    m = (np.abs(F.u - cu) < 1.0 * s + 0.01) & (np.abs(F.v - cv) < 1.0 * s + 0.01)
    stamp(F, m, mat, hl=0.2, lo=0.1, shadow=0.12, add=0.05)


# ------------------------------------------------------------------ quads: round aspen leaves
ROUND_LEAF_MASK = [          # trembling aspen leaf, long flat stalk at the top: L leaf, l shade, v light vein, s stalk
    "...s...",
    "...s...",
    "...s...",
    "...s...",
    ".LLvLl.",
    "LLLvLll",
    "LvLvLvl",
    "LLvvvll",
    "LLLvLll",
    ".LLvLl.",
    "..LLl..",
    "...l...",
]
LEAF_BUNCH_MASK = [          # three round leaves on one short twig (helmet temple)
    "sssssssss",
    "s...s...s",
    "LL.LLl.Ll",
    "LvlLvlLvl",
    "LLlLLlLLl",
    ".l..l..l.",
]


def _mask_paint(F, rows, colours, flip_v=False):
    """paint a small hand-drawn pixel mask scaled (nearest) onto the face. colours: char -> (mat, val)."""
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


LEAF_COL = {"L": (GOLDLEAF, 0.08), "l": (GOLDLEAF, -0.08), "v": (GOLDLEAF, 0.2), "s": (ASPENDK, 0.75)}


def p_round_leaf(F, stalk_at_top=True):
    """round trembling aspen leaf with a long flat stalk (hand-drawn mask, own pixels)."""
    _mask_paint(F, ROUND_LEAF_MASK, LEAF_COL, flip_v=not stalk_at_top)


def p_leaf(F):
    p_round_leaf(F, stalk_at_top=False)          # Oak-derived leaf quads grow upward from their pivot


def p_hanging_leaf(F):
    p_round_leaf(F, stalk_at_top=True)


def p_leaf_bunch(F):
    _mask_paint(F, LEAF_BUNCH_MASK, LEAF_COL)


def clasp_box(F):
    """carved pale heartwood clasp: end-grain rings with a dark rim (the leaves hang from it)."""
    F.mat[:] = ASPWOOD
    if F.face in ("front", "top"):
        cu, cv = F.fw / 2.0, F.fh / 2.0
        r = np.maximum(np.abs(F.u - cu), np.abs(F.v - cv))
        F.val[(np.floor(r) % 2) == 1] -= 0.12
        rim = r > min(cu, cv) - 1
        F.mat[rim] = ASPENDK
        F.val[rim] = 0.55
    else:
        F.val -= 0.1


# ================================================================== HEAD
def p_cap(F):
    aspen_base(F, seed=1)
    if F.is_side():
        slats(F, F.ly > -2.0, seed=1, joints=False)
        rope_band(F, -4.0, -2.0)
        F.val[F.v < 1] += 0.04
        if F.face == "front":
            k = (np.abs(F.lx - 4.5) < 1.6) & (np.abs(F.ly + 3.0) < 1.6)
            stamp(F, k, ROPE, hl=0.2, lo=0.1, shadow=0.16, add=0.04)


def p_cap_upper(F):
    aspen_base(F, seed=2, scars=False)
    if F.is_side():
        F.val[F.v < 1] += 0.05
        F.mat[F.v > F.fh - 1] = ASPENDK
        F.val[F.v > F.fh - 1] = 0.6


def p_dome(F):
    aspen_base(F, seed=3, scars=False)
    if F.face == "top":
        r = np.hypot(F.lx, F.lz)
        ring = r < 5.5
        F.mat[ring] = ASPWOOD
        F.val[ring & ((np.floor(r * 0.9) % 2) == 1)] -= 0.1
        F.val[r < 1.2] -= 0.1
    else:
        cut_rim(F, "top")


def p_brim(F):
    aspen_base(F, seed=4, scars=False)
    if F.is_side():
        F.val[F.v < 1] += 0.05
        F.mat[F.v > F.fh - 1] = ASPENDK
        F.val[F.v > F.fh - 1] = 0.6
    elif F.face == "top":
        r = np.maximum(np.abs(F.lx) / 18.0, np.abs(F.lz) / 17.0)
        F.val[r > 0.93] += 0.08
    elif F.face == "bottom":
        F.mat[:] = ASPWOOD
        F.val -= 0.2


def p_helmback(F):
    aspen_base(F, seed=5)
    if F.is_side():
        slats(F, F.alpha, seed=5)
        slat_hem(F, seed=5, airy=2, max_short=2)


def p_cheek(F):
    aspen_base(F, seed=6, scars=False)
    if F.is_side():
        slats(F, F.alpha, seed=6, joints=False)
        slat_hem(F, seed=6, airy=2, max_short=2)


def spire(F, length, half_w):
    """slim round-topped spire crown point (a tall slender slat with a rounded top)."""
    top = F.ly.max() + 0.5
    t = top - F.ly                                       # distance below the top
    r = half_w
    allow = np.where(t < r, np.sqrt(np.clip(r * r - (r - t) ** 2, 0, None)) + 0.3, half_w)
    F.alpha &= ~(np.abs(F.lx) > allow)


def p_crown_mid(F):
    aspen_base(F, seed=7, scars=False)
    spire(F, 15.0, 2.5)
    _side_cut(F, 2.5)
    if F.face in ("front", "back"):
        outline_cut(F)
        F.val[np.abs(F.lx) < 0.5] += 0.1
        F.val[(F.lx > 0.5) & F.alpha] -= 0.05
        e = (np.abs(F.lx) < 1.6) & (np.abs(F.ly + 1.0) < 0.6 * np.clip(1 - (F.lx / 1.6) ** 2, 0, 1) + 0.01)
        F.mat[e & F.alpha] = ASPENDK                     # one eye scar on the spire
        F.val[e & F.alpha] = -0.25


def p_crown_side(F):
    aspen_base(F, seed=8, scars=False)
    spire(F, 12.0, 2.0)
    _side_cut(F, 2.0)
    if F.face in ("front", "back"):
        outline_cut(F)
        F.val[np.abs(F.lx) < 0.5] += 0.1
        F.val[(F.lx > 0.5) & F.alpha] -= 0.05


HEAD_OVR = {
    "HelmCap": dict(mat=ASPEN, paint=p_cap),
    "HelmUpper": dict(mat=ASPEN, paint=p_cap_upper),
    "HelmDome": dict(mat=ASPEN, paint=p_dome),
    "HelmBrim": dict(mat=ASPEN, paint=p_brim),
    "HelmBack": dict(mat=ASPEN, paint=p_helmback),
    "R-Cheek": dict(mat=ASPEN, paint=p_cheek),
    # slim spire crown points (Oak jagged, Birch thin spikes, Beech leaf blades, Ash samara wings)
    "CrownMid": dict(mat=ASPEN, paint=p_crown_mid, size=(5, 15, 2), pivot=(0, 18.5, 15.25)),
    "R-CrownSide": dict(mat=ASPEN, paint=p_crown_side, size=(4, 12, 2), pivot=(-8.0, 17.0, 14.75), rot=(0, 0, 8)),
    "R-HelmLeaf": dict(mat=GOLDLEAF, paint=p_leaf, size=(6, 9)),
}
HEAD_ADD = [
    dict(name="HelmBadge", bone="Head", pivot=(0, 10.5, 16.8), size=(4, 4, 2), mat=ASPWOOD, paint=clasp_box,
         skip=("back",)),
    # a small bunch of trembling round leaves at the left temple (the aspen mark)
    dict(name="L-HelmLeaves", bone="Head", pivot=(17.0, 5.0, 4.0), rot=(0, 90, 0), size=(9, 6), offset=(0, -3.0, 0),
         mat=GOLDLEAF, paint=p_leaf_bunch, double=True),
]


# ================================================================== CHEST
def _laced_gap(F, halfw, y0, y1, k=1.0):
    gap = np.abs(F.x) < halfw
    F.mat[gap] = RUSSET
    F.val[gap] = -0.12
    ph = F.y % 4.0
    lace = gap & (np.abs(np.abs(F.x) - np.abs(ph - 2.0) * k) < 0.55)
    F.mat[lace] = ROPE
    F.val[lace] = 0.05
    O.sap_vein(F, 0.0, y0, y1, faint=0.35)


def p_cuirass(F):
    aspen_base(F, seed=10)
    if F.is_side():
        slats(F, F.alpha, seed=10)
        if F.face == "front":
            _laced_gap(F, 2.6, 66.0, 84.0)


def p_breast(F):
    aspen_base(F, seed=11)
    if F.is_side():
        slats(F, F.alpha, seed=11)
        slat_hem(F, seed=11, airy=2, max_short=2)
        F.val[(F.v < 1) & F.alpha] += 0.06
        if F.face == "front":
            inner = (np.abs(F.x) < 3.1) & F.alpha
            F.mat[inner] = ASPWOOD
            eye = inner & ((np.floor(F.y) % 4) == 1)
            F.mat[eye] = ROPE
            F.val[eye] = -0.05


def p_plackart(F):
    aspen_base(F, seed=12)
    if F.is_side():
        slats(F, F.alpha, seed=12)
        if F.face == "front":
            _laced_gap(F, 2.0, 56.0, 68.0, k=0.8)


def p_belt(F):
    """smooth aspen bark belt with wrapped rope ends."""
    aspen_base(F, seed=13, scars=False)
    if F.is_side():
        F.val[F.v < 1] += 0.05
        F.mat[F.v > F.fh - 1] = ASPENDK
        F.val[F.v > F.fh - 1] = 0.6
        wrap = (np.abs(np.abs(F.x) - 6.5) < 1.5)
        F.mat[wrap & F.alpha] = ROPE
        F.val[wrap & (((F.iu + F.iv) % 3) == 0)] -= 0.15


def p_tassel(F):
    aspen_base(F, seed=14, scars=False)
    if F.face in ("front", "back"):
        slats(F, F.alpha, seed=14, joints=False)
        slat_hem(F, seed=14, airy=5, max_short=4)


def p_tassel_back(F):
    aspen_base(F, seed=15, scars=False)
    if F.face in ("front", "back"):
        slats(F, F.alpha, seed=15, joints=False)
        slat_hem(F, seed=15, airy=5, max_short=4)


def p_collar(F):
    twist(F, VINE, 3)
    if F.face == "top":
        r = np.maximum(np.abs(F.lx) / 10.0, np.abs(F.lz) / 8.5)
        F.mat[r < 0.7] = RUSSET
        F.val[r < 0.7] -= 0.3
    if F.face == "front":
        leaflet(F, 3.0, 1.0)
        leaflet(F, F.fw - 3.0, 1.0)
        leaflet(F, F.fw / 2.0, 1.0)


def p_pauldron(F):
    aspen_base(F, seed=16, scars=False)
    if F.is_side():
        F.val[F.v < 1] += 0.05
        F.mat[F.v > F.fh - 1] = ASPENDK
        F.val[F.v > F.fh - 1] = 0.6
        rope_band(F, -0.6, 0.6)
    elif F.face == "top":
        c = np.floor(F.lz / SLAT).astype(np.int64)
        f = F.lz / SLAT - np.floor(F.lz / SLAT)
        F.val += (hash2(c, c * 0 + 1, 16) - 0.5) * 0.08
        g = f < 1.0 / SLAT
        F.mat[g] = ASPENDK
        F.val[g] = 0.6


def p_pauldron_lame(F):
    aspen_base(F, seed=18, scars=False)
    if F.is_side():
        slats(F, F.alpha, w=3.0, seed=18, joints=False)
        cut_rim(F, "top")
        slat_hem(F, w=3.0, seed=18, airy=2, max_short=2)


def p_vine(F):
    twist(F, VINE, 3)
    if F.face == "top":
        for k in range(2, F.fh - 1, 5):
            leaflet(F, 1.5, k + 0.5)


def p_sleeve(F):
    mottle(F, scale=8, amp=0.03, seed=21)
    if F.is_side():
        coord = _horiz(F)
        F.val += 0.05 * np.round(np.sin(2 * math.pi * coord / 3) * 1.5) / 1.5
        rope_band(F, 4.0, 6.0)
        rope_band(F, -7.5, -5.5)


CHEST_OVR = {
    "Cuirass": dict(mat=ASPEN, paint=p_cuirass),
    "R-Breast": dict(mat=ASPEN, paint=p_breast, size=(12, 18, 2)),
    "Collar": dict(paint=p_collar),
    "Plackart": dict(mat=ASPEN, paint=p_plackart),
    "VineBelt": dict(mat=ASPEN, paint=p_belt),
    # long slender slat tassels (airy gaps at the hem)
    "R-Tassel": dict(mat=ASPEN, paint=p_tassel, size=(12, 15, 1), offset=(0, -7.5, 0)),
    "TasselBack": dict(mat=ASPEN, paint=p_tassel_back, size=(24, 14, 1), offset=(0, -7.0, 0)),
    "R-Pauldron": dict(mat=ASPEN, paint=p_pauldron),
    "R-PauldronLame": dict(mat=ASPEN, paint=p_pauldron_lame, size=(3, 10, 15)),
    "L-Vine": dict(paint=p_vine),
    "L-VineLeafA": dict(mat=GOLDLEAF, paint=p_leaf, size=(6, 9)),
    "L-VineLeafB": dict(mat=GOLDLEAF, paint=p_hanging_leaf, size=(5, 8)),
    "R-Sleeve": dict(mat=RUSSET, paint=p_sleeve),
}
CHEST_DROP = ("Acorn", "AcornCap")
CHEST_ADD = [
    # aspen mark: a carved heartwood clasp with 4 round golden leaves trembling on long stalks at different angles
    dict(name="Clasp", bone="Belly", pivot=(0, -5.8, 11.0), size=(5, 5, 2), mat=ASPWOOD, paint=clasp_box, skip=("back",)),
    dict(name="AspenLeaf1", bone="Belly", pivot=(-4.2, -8.4, 13.30), rot=(8, 0, -26), size=(6, 11), offset=(0, -5.5, 0),
         mat=GOLDLEAF, paint=p_hanging_leaf, double=True),
    dict(name="AspenLeaf2", bone="Belly", pivot=(-1.4, -8.4, 13.10), rot=(-6, 0, -8), size=(6, 14), offset=(0, -7.0, 0),
         mat=GOLDLEAF, paint=p_hanging_leaf, double=True),
    dict(name="AspenLeaf3", bone="Belly", pivot=(1.4, -8.4, 13.20), rot=(10, 0, 10), size=(6, 12), offset=(0, -6.0, 0),
         mat=GOLDLEAF, paint=p_hanging_leaf, double=True),
    dict(name="AspenLeaf4", bone="Belly", pivot=(4.2, -8.4, 13.35), rot=(-8, 0, 28), size=(6, 10), offset=(0, -5.0, 0),
         mat=GOLDLEAF, paint=p_hanging_leaf, double=True),
    # a golden leaf tucked into the right shoulder slats (the left shoulder has the vine)
    dict(name="R-ShoulderLeaf", bone="R-Arm", parent="R-Pauldron", pivot=(-2.0, 2.0, -3.0), rot=(-20, 0, 55), size=(6, 9),
         offset=(0, 4.5, 0), mat=GOLDLEAF, paint=p_leaf, double=True),
]


# ================================================================== HANDS
def p_bracer(F):
    aspen_base(F, seed=20)
    if F.is_side():
        slats(F, F.alpha, w=3.0, seed=20, joints=False)
        cut_rim(F, "top")
        rope_band(F, 2.6, 4.6)
        rope_band(F, -5.0, -3.0)


def p_bracer_plate(F):
    aspen_base(F, seed=21, scars=False)
    if F.is_side():
        slats(F, F.alpha, w=3.0, seed=21, joints=False)
        F.val[F.v < 1] += 0.05
        slat_hem(F, w=3.0, seed=21, airy=2, max_short=2)


def p_glove(F):
    aspen_base(F, seed=22, scars=False)
    if F.is_side():
        wrap = ((F.ly > 1.0) & (F.ly < 3.0)) | ((F.ly > -3.0) & (F.ly < -1.0))
        stamp(F, wrap, ROPE, hl=0.12, lo=0.12, shadow=0.16)
        F.val[wrap & (((F.iu + F.iv) % 3) == 0)] -= 0.15
        fingers = F.ly < -4.0
        F.mat[fingers] = RUSSET
        F.val[fingers] -= 0.05
        F.val[fingers & ((F.iu % 3) == 0)] -= 0.1
    elif F.face == "bottom":
        F.mat[:] = RUSSET
        F.val -= 0.15


HANDS_OVR = {
    "R-Bracer": dict(mat=ASPEN, paint=p_bracer),
    "R-BracerPlate": dict(mat=ASPEN, paint=p_bracer_plate),
    "R-Glove": dict(mat=ASPEN, paint=p_glove),
}
HANDS_ADD = [
    dict(name="R-Sprig", bone="R-Forearm", pivot=(-6.3, 3.0, 2.0), rot=(0, -90, 0), size=(6, 9), offset=(0, 4.5, 0),
         mat=GOLDLEAF, paint=p_leaf, double=True, mirror=True),
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
    aspen_base(F, seed=24, scars=False)
    if F.face == "front":
        slats(F, F.alpha, w=3.0, seed=24, joints=False)
        F.val[F.v < 1] += 0.05
        slat_hem(F, w=3.0, seed=24, airy=1, max_short=1)


def p_greave(F):
    aspen_base(F, seed=25)
    if F.is_side():
        slats(F, F.ly > -8.0, seed=25)
        cut_rim(F, "top")
        rope_band(F, 6.0, 8.0)
        rope_band(F, -7.5, -5.5)
        if F.face == "back":
            lace = (np.abs(np.abs(F.lx) - ((F.iv % 4) * 0.5)) < 0.5) & (np.abs(F.lx) < 2.1) & (F.ly > -5.0)
            F.mat[lace] = ROPE
            F.val[lace] = 0.0


def p_boot(F):
    aspen_base(F, seed=26, scars=False)
    F.val -= 0.03
    if F.is_side():
        sole = F.ly < -2.6
        F.mat[sole] = ASPENDK
        F.val[sole] = 0.3
        F.val[sole & (F.ly > -3.6)] += 0.12
        if F.face == "front":
            cap = (F.ly > -2.6) & (F.ly < 1.5) & (np.abs(F.lx) < 5.6)
            stamp(F, cap, ASPEN, hl=0.14, lo=0.12, shadow=0.16, add=0.04)
        if F.face in ("left", "right"):
            wrap = (np.abs(F.lz + 3.0) < 1.6) & (F.ly > -2.6)
            stamp(F, wrap, ROPE, hl=0.12, lo=0.12, shadow=0.16)
            F.val[wrap & (((F.iu + F.iv) % 3) == 0)] -= 0.15
    elif F.face == "top":
        wrap = np.abs(F.lz + 3.0) < 1.6
        stamp(F, wrap, ROPE, hl=0.12, lo=0.12, shadow=0.14)
        F.val[wrap & (((F.iu + F.iv) % 3) == 0)] -= 0.15
    elif F.face == "bottom":
        F.mat[:] = ASPENDK
        F.val[:] = 0.15


LEGS_OVR = {
    "Breeches": dict(mat=RUSSET, paint=p_breeches),
    "R-Trouser": dict(mat=RUSSET, paint=p_trouser),
    "R-Knee": dict(mat=ASPEN, paint=p_knee),
    "R-Greave": dict(mat=ASPEN, paint=p_greave),
    "R-Boot": dict(mat=ASPEN, paint=p_boot),
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
