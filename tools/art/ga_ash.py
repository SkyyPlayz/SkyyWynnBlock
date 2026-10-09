"""SkyWynn Foraging armor - F1 Grove - ASH set (v1). Geometry + paint design (ORIGINAL; no vanilla or Armory pixels).

Started from the IN-GAME Ash wood (lesson from Beech v1): hues / values sampled from the game's Ash trunk, log end,
hardwood planks and ash leaves; our own pixels. Dark plum-brown bark with lighter INTERLACING DIAMOND RIDGES (ash bark),
deep furrows, pale tan heartwood on cut edges, the game's deep blue-green ash leaves (pinnate: paired leaflets on a stem),
straw-tan winged seed keys, cool slate cloth.
Plate shapes vs Oak (jagged), Birch (rounded / curled), Beech (broad smooth): CHEVRON plates - every plate ends in a
downward V point, so rows of plates make a diamond lattice; pointed shield-like hems; samara-wing crown points.
Mark: the ASH SAMARA cluster - winged seed keys hanging in a bunch from a carved heartwood clasp on the belt, plus a
small cluster at the helmet temple. Same family + fit as Oak / Birch / Beech (geometry derived from ga_oak.py).
"""
import math
import numpy as np
import ga_paint as P
from ga_paint import (ROPE, VINE, ASH, ASHDK, ASHLEAF, SAMARA, ASHWOOD, SLATE,
                      stamp, stitches, mottle, hash2)
import ga_oak as O
from ga_oak import _uv_of, _horiz, rope_band, twist, taper_top, _side_cut

TIER, TREE = "F1_Grove", "Ash"


# ------------------------------------------------------------------ ash bark painting
def _lattice(F, cell_w=7.0, cell_h=14.0, seed=0):
    """ash bark: broad interlacing ridges around long narrow diamond furrows (staggered rows).
    returns (furrow, furrow_lip, furrow_shadow) masks."""
    h = _horiz(F)
    vert = F.y if F.is_side() else F.z
    row = np.floor(vert / cell_h)
    hh = h + np.where(np.mod(row, 2) == 0, 0.0, cell_w / 2.0)
    col = np.floor(hh / cell_w)
    ri = row.astype(np.int64); ci = col.astype(np.int64)
    # per-cell jitter of size / centre so it looks grown
    jx = (hash2(ci, ri, seed + 11) - 0.5) * 1.6
    jw = 0.75 + 0.5 * hash2(ci, ri, seed + 12)
    du = (np.mod(hh, cell_w) - cell_w / 2.0 - jx) / (cell_w * 0.5 * 0.42 * jw)
    dv = (np.mod(vert, cell_h) - cell_h / 2.0) / (cell_h * 0.5 * 0.86)
    dd = np.abs(du) + np.abs(dv)
    furrow = dd < 1.0
    lip = (dd >= 1.0) & (dd < 1.45) & (du < 0)          # lit ridge edge on the left of each furrow
    shade = (dd >= 1.0) & (dd < 1.45) & (du > 0)
    return furrow, lip, shade


def ash_base(F, seed=0, scars=True):
    """in-game-ash-like bark: dark plum-brown, broad ridges with fine vertical fibres around long narrow diamond
    furrows (the interlacing ash-bark pattern)."""
    m0 = F.mat == ASH
    n2 = P.vnoise(F.W, 10.0, 80 + seed)
    F.val[m0] += 0.04 * np.round((n2[m0] - 0.5) * 3)
    h = _horiz(F)
    col = np.floor(h).astype(np.int64)
    fib = (hash2(col, np.floor(F.y / 4).astype(np.int64), seed + 5) - 0.5)
    F.val[m0] += 0.06 * np.round(fib[m0] * 2) / 2
    if F.is_side():
        fu, lip, sh = _lattice(F, seed=seed)
        F.val[m0 & lip] += 0.10
        F.val[m0 & sh] -= 0.06
        f = fu & m0
        F.mat[f] = ASHDK
        F.val[f] = 0.55
        F.val[f & ~P._shift(f, 1, 0)] = 0.35         # deepest at the top of each furrow


def chevron_plates(F, region, pitch, seed=0, y_top=None, step=8.0):
    """overlapping wooden plates whose lower edges are shallow V points (one V per plate): rows of plates make a
    diamond lattice. Gentle light bevel along the V, soft shadow under it, each plate its own tone."""
    region = np.asarray(region, bool) & F.alpha
    if not region.any():
        return
    if y_top is None:
        y_top = F.y[region].max() + 1e-3
    h = _horiz(F)
    row0 = np.floor((y_top - F.y) / pitch).astype(np.int64)
    off = np.where(row0 % 2 == 0, 0.0, step / 2.0)                 # offset every other row (diamond lattice)
    hc = np.mod(h + off, step)
    vdrop = (step / 2.0 - np.abs(hc - step / 2.0)) * 0.55          # V point: lower in the middle of each plate
    s_ = (y_top - F.y - vdrop) / pitch
    k = np.floor(s_); f = s_ - k
    ki = k.astype(np.int64)
    plate = np.floor((h + np.where(ki % 2 == 0, 0.0, step / 2.0)) / step).astype(np.int64)
    tone = (hash2(plate, ki, seed + 3) - 0.5) * 0.10
    F.val[region] += tone[region] + 0.04 * (0.5 - f[region])
    px = 1.0 / pitch
    under = region & (f > 1 - px) & (k >= 0)
    F.mat[under] = ASHDK
    F.val[under] = 0.55
    bev = region & (f < px) & (k > 0)
    F.mat[bev & (F.mat == ASHDK)] = ASH
    F.val[bev] += 0.08


def point_hem(F, which=("bottom",), clip=2, notch=True, period=6.0):
    """pointed hem: the lower edge is cut into shallow V points (shield tips), with a dark end-grain line."""
    d = {"top": F.v, "bottom": F.fh - F.v, "left": F.u, "right": F.fw - F.u}
    for w in which:
        if w == "bottom":
            if notch and F.face in ("front", "back"):
                ph = np.mod(F.u, period)
                depth = np.abs(ph - period / 2.0) * (2.0 / period) * 2.0     # 0 at the point, 2 at the notch
                F.alpha &= ~(d[w] < depth)
                dd = d[w] - depth
                m = (dd < 1) & (dd >= 0) & F.alpha
            else:
                m = (d[w] < 1) & F.alpha
            F.mat[m] = ASHDK
            F.val[m] = 0.5
        elif w == "top":
            m = (d[w] < 1) & F.alpha
            F.val[m] += 0.05


def cut_rim(F, which="bottom"):
    d = {"top": F.v, "bottom": F.fh - F.v, "left": F.u, "right": F.fw - F.u}[which]
    m = (d < 1) & F.alpha
    F.mat[m] = ASHWOOD
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


# ------------------------------------------------------------------ quads: ash leaf, samaras
ASH_LEAF_MASK = [            # pinnate ash leaf, stem end at the bottom: L = leaflet, l = leaflet shade, s = stem
    "...L...",
    "..LLl..",
    "...s...",
    "LL.s.Ll",
    ".LLsLl.",
    "...s...",
    "LL.s.Ll",
    ".LLsLl.",
    "...s...",
    "...s...",
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


def p_ash_leaf(F, mat=ASHLEAF, stem_at_bottom=True):
    """pinnate ash leaf: paired narrow leaflets on a stem + one at the tip (hand-drawn mask, own pixels)."""
    _mask_paint(F, ASH_LEAF_MASK, {"L": (mat, 0.06), "l": (mat, -0.06), "s": (VINE, 0.0)}, flip_v=not stem_at_bottom)


def p_leaf(F):
    p_ash_leaf(F, ASHLEAF)


def p_leaf2(F):
    p_ash_leaf(F, ASHLEAF, stem_at_bottom=False)


SAMARA_MASK = [             # one winged seed key, stalk at the top: d = seed, W = wing, w = wing shade, v = vein
    ".d.",
    "ddw",
    "ddw",
    "WvW",
    "WvW",
    "WWv",
    "WWv",
    "WWw",
    "WWw",
    ".W.",
]
SAMARA_BUNCH_MASK = [       # three keys hanging from one short twig
    ".sssssss.",
    ".d..d..d.",
    "dd.dd.dd.",
    "WW.WW.WW.",
    "WW.Wv.Ww.",
    "Wv.WW.Ww.",
    "Ww.Ww..W.",
    ".W..W....",
]


def p_samara(F):
    """one winged seed key (hand-drawn mask, own pixels)."""
    _mask_paint(F, SAMARA_MASK, {"d": (SAMARA, -0.2), "W": (SAMARA, 0.06), "w": (SAMARA, -0.06), "v": (SAMARA, -0.12)})


def p_samara_bunch(F):
    """a small bunch of 3 keys on one stalk (used at the helmet temple)."""
    _mask_paint(F, SAMARA_BUNCH_MASK, {"s": (ASHDK, 0.4), "d": (SAMARA, -0.2), "W": (SAMARA, 0.06),
                                       "w": (SAMARA, -0.06), "v": (SAMARA, -0.12)})


def p_sprig(F):
    """ash twig: one pinnate leaf with a seed key tucked beside it."""
    p_ash_leaf(F, ASHLEAF)


def clasp_box(F):
    """carved heartwood clasp: tan end-grain rings with a dark rim (the samaras hang from it)."""
    F.mat[:] = ASHWOOD
    if F.face in ("front", "top"):
        cu, cv = F.fw / 2.0, F.fh / 2.0
        r = np.maximum(np.abs(F.u - cu), np.abs(F.v - cv))
        F.val[(np.floor(r) % 2) == 1] -= 0.12
        rim = r > min(cu, cv) - 1
        F.mat[rim] = ASHDK
        F.val[rim] = 0.45
    else:
        F.val -= 0.1


# ================================================================== HEAD
def p_cap(F):
    ash_base(F, seed=1)
    if F.is_side():
        rope_band(F, -4.0, -2.0)
        F.val[F.v < 1] += 0.04
        if F.face == "front":
            k = (np.abs(F.lx - 4.5) < 1.6) & (np.abs(F.ly + 3.0) < 1.6)
            stamp(F, k, ROPE, hl=0.2, lo=0.1, shadow=0.16, add=0.04)


def p_cap_upper(F):
    ash_base(F, seed=2, scars=False)
    if F.is_side():
        F.val[F.v < 1] += 0.05
        F.mat[F.v > F.fh - 1] = ASHDK
        F.val[F.v > F.fh - 1] = 0.5


def p_dome(F):
    ash_base(F, seed=3, scars=False)
    if F.face == "top":
        r = np.hypot(F.lx, F.lz)
        ring = r < 5.5
        F.mat[ring] = ASHWOOD
        F.val[ring & ((np.floor(r * 0.9) % 2) == 1)] -= 0.1
        F.val[r < 1.2] -= 0.1
    else:
        cut_rim(F, "top")


def p_brim(F):
    ash_base(F, seed=4, scars=False)
    if F.is_side():
        F.val[F.v < 1] += 0.05
        F.mat[F.v > F.fh - 1] = ASHDK
        F.val[F.v > F.fh - 1] = 0.5
    elif F.face == "top":
        r = np.maximum(np.abs(F.lx) / 18.0, np.abs(F.lz) / 17.0)
        F.val[r > 0.93] += 0.08
    elif F.face == "bottom":
        F.mat[:] = ASHWOOD
        F.val -= 0.2


def p_helmback(F):
    ash_base(F, seed=5)
    if F.is_side():
        chevron_plates(F, F.alpha, 6.0, seed=5)
        point_hem(F, ("bottom",), clip=2)


def p_cheek(F):
    ash_base(F, seed=6, scars=False)
    if F.is_side():
        chevron_plates(F, F.alpha, 6.0, seed=6)
        point_hem(F, ("bottom",), clip=0)
        d = F.fh - F.v
        F.alpha &= ~((d < 2.5) & ((F.u < 2) if F.face == "left" else (F.u > F.fw - 2)))


def samara_wing(F, length, half_w):
    """samara-wing crown point: narrow at the base, widening to a broad rounded paddle with a small tip point."""
    top = F.ly.max() + 0.5
    s_ = np.clip((top - F.ly) / length, 0, 1)            # 0 tip .. 1 base
    allow = half_w * (0.45 + 0.55 * np.sin(np.pi * np.clip(0.15 + s_ * 1.1, 0, 1)) ** 0.5)
    allow = np.where(s_ < 0.12, half_w * s_ / 0.12 * 0.6 + 0.35, allow)
    allow = np.where(s_ > 0.75, half_w * (0.45 + 0.55 * (1 - (s_ - 0.75) / 0.25) * 0.4), allow)
    F.alpha &= ~(np.abs(F.lx) > allow)


def p_crown_mid(F):
    ash_base(F, seed=7, scars=False)
    samara_wing(F, 13.0, 3.4)
    _side_cut(F, 13.0)
    if F.face in ("front", "back"):
        outline_cut(F)
        mid = np.abs(F.lx) < 0.5
        F.val[mid] += 0.12
        F.val[(F.lx > 0.5) & F.alpha] -= 0.05


def p_crown_side(F):
    ash_base(F, seed=8, scars=False)
    samara_wing(F, 11.0, 2.9)
    _side_cut(F, 11.0)
    if F.face in ("front", "back"):
        outline_cut(F)
        F.val[np.abs(F.lx) < 0.5] += 0.12
        F.val[(F.lx > 0.5) & F.alpha] -= 0.05


HEAD_OVR = {
    "HelmCap": dict(mat=ASH, paint=p_cap),
    "HelmUpper": dict(mat=ASH, paint=p_cap_upper),
    "HelmDome": dict(mat=ASH, paint=p_dome),
    "HelmBrim": dict(mat=ASH, paint=p_brim),
    "HelmBack": dict(mat=ASH, paint=p_helmback),
    "R-Cheek": dict(mat=ASH, paint=p_cheek),
    # samara-wing crown points (Oak: narrow jagged; Birch: tall thin spikes; Beech: leaf blades)
    "CrownMid": dict(mat=ASH, paint=p_crown_mid, size=(7, 13, 2), pivot=(0, 17.5, 15.25)),
    "R-CrownSide": dict(mat=ASH, paint=p_crown_side, size=(6, 11, 2), pivot=(-9.0, 16.0, 14.75), rot=(0, 0, 16)),
    "R-HelmLeaf": dict(mat=ASHLEAF, paint=p_leaf, size=(7, 10)),
}
HEAD_ADD = [
    # carved heartwood badge at the base of the middle crown point
    dict(name="HelmBadge", bone="Head", pivot=(0, 10.5, 16.8), size=(4, 4, 2), mat=ASHWOOD, paint=clasp_box,
         skip=("back",)),
    # a small bunch of winged seed keys at the left temple (the ash mark)
    dict(name="L-HelmSamaras", bone="Head", pivot=(17.0, 5.0, 4.0), rot=(0, 90, 0), size=(9, 8), offset=(0, -4.0, 0),
         mat=SAMARA, paint=p_samara_bunch, double=True),
]


# ================================================================== CHEST
def _laced_gap(F, halfw, y0, y1, k=1.0):
    gap = np.abs(F.x) < halfw
    F.mat[gap] = SLATE
    F.val[gap] = -0.12
    ph = F.y % 4.0
    lace = gap & (np.abs(np.abs(F.x) - np.abs(ph - 2.0) * k) < 0.55)
    F.mat[lace] = ROPE
    F.val[lace] = 0.05
    O.sap_vein(F, 0.0, y0, y1, faint=0.35)


def p_cuirass(F):
    ash_base(F, seed=10)
    if F.is_side():
        chevron_plates(F, F.alpha, 11.0, seed=10)
        if F.face == "front":
            _laced_gap(F, 2.6, 66.0, 84.0)


def p_breast(F):
    ash_base(F, seed=11)
    if F.is_side():
        chevron_plates(F, F.alpha, 9.0, seed=11)
        point_hem(F, ("bottom", "top"), clip=2)
        if F.face == "front":
            inner = (np.abs(F.x) < 3.1) & F.alpha
            F.mat[inner] = ASHWOOD
            eye = inner & ((np.floor(F.y) % 4) == 1)
            F.mat[eye] = ROPE
            F.val[eye] = -0.05


def p_plackart(F):
    ash_base(F, seed=12)
    if F.is_side():
        chevron_plates(F, F.alpha, 8.0, seed=12)
        if F.face == "front":
            _laced_gap(F, 2.0, 56.0, 68.0, k=0.8)


def p_belt(F):
    """smooth beech bark belt with wrapped rope ends (no ivy)."""
    ash_base(F, seed=13, scars=False)
    if F.is_side():
        F.val[F.v < 1] += 0.05
        F.mat[F.v > F.fh - 1] = ASHDK
        F.val[F.v > F.fh - 1] = 0.5
        wrap = (np.abs(np.abs(F.x) - 6.5) < 1.5)
        F.mat[wrap & F.alpha] = ROPE
        F.val[wrap & (((F.iu + F.iv) % 3) == 0)] -= 0.15


def p_tassel(F):
    ash_base(F, seed=14)
    if F.face in ("front", "back"):
        chevron_plates(F, F.alpha, 6.0, seed=14)
        point_hem(F, ("bottom",), clip=3)


def p_tassel_back(F):
    ash_base(F, seed=15)
    if F.face in ("front", "back"):
        chevron_plates(F, F.alpha, 6.0, seed=15)
        # two broad panels with a clean gap between them (no strips)
        F.alpha &= ~((np.abs(F.lx) < 0.6) & (F.v > 3))
        point_hem(F, ("bottom",), clip=3)


def p_collar(F):
    twist(F, VINE, 3)
    if F.face == "top":
        r = np.maximum(np.abs(F.lx) / 10.0, np.abs(F.lz) / 8.5)
        F.mat[r < 0.7] = SLATE
        F.val[r < 0.7] -= 0.3
    if F.face == "front":
        leaflet(F, 3.0, 1.4, ASHLEAF)
        leaflet(F, F.fw - 3.0, 1.4, ASHLEAF)
        leaflet(F, F.fw / 2.0, 1.4, ASHLEAF)


def p_pauldron(F):
    ash_base(F, seed=16, scars=False)
    if F.is_side():
        F.val[F.v < 1] += 0.05
        F.mat[F.v > F.fh - 1] = ASHDK
        F.val[F.v > F.fh - 1] = 0.5
        rope_band(F, -0.6, 0.6)


def p_pauldron_top(F):
    ash_base(F, seed=17, scars=False)
    if F.is_side():
        F.val[F.v < 1] += 0.05
        F.mat[F.v > F.fh - 1] = ASHDK
        F.val[F.v > F.fh - 1] = 0.5


def p_pauldron_lame(F):
    ash_base(F, seed=18, scars=False)
    if F.is_side():
        cut_rim(F, "top")
        point_hem(F, ("bottom",), clip=0)


def p_vine(F):
    twist(F, VINE, 3)
    if F.face == "top":
        for i, k in enumerate(range(2, F.fh - 1, 5)):
            leaflet(F, 1.5, k + 0.5, ASHLEAF if i % 3 == 2 else ASHLEAF)


def p_sleeve(F):
    mottle(F, scale=8, amp=0.03, seed=21)
    if F.is_side():
        coord = _horiz(F)
        F.val += 0.05 * np.round(np.sin(2 * math.pi * coord / 3) * 1.5) / 1.5
        rope_band(F, 4.0, 6.0)
        rope_band(F, -7.5, -5.5)


CHEST_OVR = {
    "Cuirass": dict(mat=ASH, paint=p_cuirass),
    "R-Breast": dict(mat=ASH, paint=p_breast),
    "Collar": dict(paint=p_collar),
    "Plackart": dict(mat=ASH, paint=p_plackart),
    "VineBelt": dict(mat=ASH, paint=p_belt),
    "R-Tassel": dict(mat=ASH, paint=p_tassel, size=(12, 12, 1), offset=(0, -6.0, 0)),
    "TasselBack": dict(mat=ASH, paint=p_tassel_back, size=(24, 12, 1), offset=(0, -6.0, 0)),
    "R-Pauldron": dict(mat=ASH, paint=p_pauldron),
    "R-PauldronLame": dict(mat=ASH, paint=p_pauldron_lame),
    "L-Vine": dict(paint=p_vine),
    "L-VineLeafA": dict(mat=ASHLEAF, paint=p_leaf, size=(7, 9)),
    "L-VineLeafB": dict(mat=ASHLEAF, paint=lambda F: p_ash_leaf(F, ASHLEAF, stem_at_bottom=False)),
    "R-Sleeve": dict(mat=SLATE, paint=p_sleeve),
}
CHEST_DROP = ("Acorn", "AcornCap")
CHEST_ADD = [
    # ash samara cluster: a carved heartwood clasp with 5 winged seed keys fanning down from it
    dict(name="Clasp", bone="Belly", pivot=(0, -5.8, 11.0), size=(5, 5, 2), mat=ASHWOOD, paint=clasp_box, skip=("back",)),
    dict(name="Samara1", bone="Belly", pivot=(-4.8, -7.5, 12.30), rot=(0, 0, -24), size=(3, 8), offset=(0, -4.0, 0),
         mat=SAMARA, paint=p_samara, double=True),
    dict(name="Samara2", bone="Belly", pivot=(-2.4, -7.5, 12.25), rot=(0, 0, -10), size=(3, 9), offset=(0, -4.5, 0),
         mat=SAMARA, paint=p_samara, double=True),
    dict(name="Samara3", bone="Belly", pivot=(0.0, -7.5, 12.20), rot=(0, 0, 0), size=(3, 10), offset=(0, -5.0, 0),
         mat=SAMARA, paint=p_samara, double=True),
    dict(name="Samara4", bone="Belly", pivot=(2.4, -7.5, 12.15), rot=(0, 0, 10), size=(3, 9), offset=(0, -4.5, 0),
         mat=SAMARA, paint=p_samara, double=True),
    dict(name="Samara5", bone="Belly", pivot=(4.8, -7.5, 12.10), rot=(0, 0, 24), size=(3, 8), offset=(0, -4.0, 0),
         mat=SAMARA, paint=p_samara, double=True),
    # an ash leaf tucked into the right shoulder plate (the left shoulder has the vine)
    dict(name="R-ShoulderLeaf", bone="R-Arm", parent="R-Pauldron", pivot=(-2.0, 2.0, -3.0), rot=(-20, 0, 55), size=(7, 10),
         offset=(0, 5.0, 0), mat=ASHLEAF, paint=p_leaf, double=True),
    # a raised ridge (spine) along the top of each shoulder plate - echoes the ash bark ridges
    dict(name="R-PauldronRidge", bone="R-Arm", parent="R-Pauldron", pivot=(0.5, 2.0, 0), size=(3, 2, 14), mat=ASH,
         paint=p_pauldron_top, mirror=True),
]


# ================================================================== HANDS
def p_bracer(F):
    ash_base(F, seed=20)
    if F.is_side():
        chevron_plates(F, F.alpha, 7.0, seed=20)
        cut_rim(F, "top")
        rope_band(F, 2.6, 4.6)
        rope_band(F, -5.0, -3.0)


def p_bracer_plate(F):
    ash_base(F, seed=21, scars=False)
    if F.is_side():
        F.val[F.v < 1] += 0.05
        point_hem(F, ("bottom",), clip=0)


def p_glove(F):
    ash_base(F, seed=22, scars=False)
    if F.is_side():
        wrap = ((F.ly > 1.0) & (F.ly < 3.0)) | ((F.ly > -3.0) & (F.ly < -1.0))
        stamp(F, wrap, ROPE, hl=0.12, lo=0.12, shadow=0.16)
        F.val[wrap & (((F.iu + F.iv) % 3) == 0)] -= 0.15
        fingers = F.ly < -4.0
        F.mat[fingers] = SLATE
        F.val[fingers] -= 0.05
        F.val[fingers & ((F.iu % 3) == 0)] -= 0.1
    elif F.face == "bottom":
        F.mat[:] = SLATE
        F.val -= 0.15


HANDS_OVR = {
    "R-Bracer": dict(mat=ASH, paint=p_bracer),
    "R-BracerPlate": dict(mat=ASH, paint=p_bracer_plate),
    "R-Glove": dict(mat=ASH, paint=p_glove),
}
HANDS_ADD = [
    dict(name="R-Sprig", bone="R-Forearm", pivot=(-6.3, 3.0, 2.0), rot=(0, -90, 0), size=(7, 10), offset=(0, 5.0, 0),
         mat=ASHLEAF, paint=p_sprig, double=True, mirror=True),
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
    ash_base(F, seed=24, scars=False)
    if F.face == "front":
        F.val[F.v < 1] += 0.05
        point_hem(F, ("bottom",), clip=2)


def p_greave(F):
    ash_base(F, seed=25)
    if F.is_side():
        chevron_plates(F, F.ly > -8.0, 9.0, seed=25)
        cut_rim(F, "top")
        rope_band(F, 6.0, 8.0)
        rope_band(F, -7.5, -5.5)
        if F.face == "back":
            lace = (np.abs(np.abs(F.lx) - ((F.iv % 4) * 0.5)) < 0.5) & (np.abs(F.lx) < 2.1) & (F.ly > -5.0)
            F.mat[lace] = ROPE
            F.val[lace] = 0.0


def p_boot(F):
    ash_base(F, seed=26, scars=False)
    F.val -= 0.03
    if F.is_side():
        sole = F.ly < -2.6
        F.mat[sole] = ASHDK
        F.val[sole] = 0.2
        F.val[sole & (F.ly > -3.6)] += 0.12
        if F.face == "front":
            cap = (F.ly > -2.6) & (F.ly < 1.5) & (np.abs(F.lx) < 5.6)
            stamp(F, cap, ASH, hl=0.14, lo=0.12, shadow=0.16, add=0.04)
        if F.face in ("left", "right"):
            wrap = (np.abs(F.lz + 3.0) < 1.6) & (F.ly > -2.6)
            stamp(F, wrap, ROPE, hl=0.12, lo=0.12, shadow=0.16)
            F.val[wrap & (((F.iu + F.iv) % 3) == 0)] -= 0.15
    elif F.face == "top":
        wrap = np.abs(F.lz + 3.0) < 1.6
        stamp(F, wrap, ROPE, hl=0.12, lo=0.12, shadow=0.14)
        F.val[wrap & (((F.iu + F.iv) % 3) == 0)] -= 0.15
    elif F.face == "bottom":
        F.mat[:] = ASHDK
        F.val[:] = 0.1


LEGS_OVR = {
    "Breeches": dict(mat=SLATE, paint=p_breeches),
    "R-Trouser": dict(mat=SLATE, paint=p_trouser),
    "R-Knee": dict(mat=ASH, paint=p_knee),
    "R-Greave": dict(mat=ASH, paint=p_greave),
    "R-Boot": dict(mat=ASH, paint=p_boot),
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
