"""SkyWynn Foraging armor - F1 Grove - BIRCH set. Geometry + paint design (ORIGINAL; no vanilla or Armory pixels).

Same F1 bark-plate family and the same piece fit as Oak (geometry derived from ga_oak.py), its own variation:
 - colours: off-white papery birch bark (never pure white) with charcoal horizontal lenticel dashes and black knot
   "eyes", pale yellow heartwood showing where the bark peels, light spring-green leaves, cool sage cloth
 - mark: hanging CATKINS (a 3-catkin cluster under a carved knot clasp on the belt + a pair on the helmet)
 - shape changes vs Oak: taller thinner 3-point crown, scalloped (rounded) plate edges instead of jagged ones,
   rolled-bark curls along the shoulder plates + tassel tops, a twisted birch-bark belt, twig sprigs on the bracers
Ideas taken from studying The Armory (no copying): plates outlined with a dark under-edge + light rim, long smooth grain
bands instead of speckle, alpha-cut quads for silhouette details (catkins, sprigs) so nothing gets bulky.
"""
import math
import numpy as np
import ga_paint as P
from ga_paint import (ROPE, VINE, SAP, STITCH, BIRCH, BIRCHDK, BLEAF, CATKIN, BWOOD, SAGE,
                      stamp, rivet, stitches, tatter, mottle, wear, hash2)
import ga_oak as O
from ga_oak import _uv_of, _horiz, rope_band, twist, taper_top, _side_cut

TIER, TREE = "F1_Grove", "Birch"


# ------------------------------------------------------------------ birch bark painting
def birch_base(F, seed=0, lent=1.0, knots=True):
    """papery birch: soft horizontal bands, short charcoal lenticel dashes, a few black knot 'eyes'."""
    m0 = F.mat == BIRCH
    mottle(F, scale=8.0, amp=0.025, seed=40 + seed)
    h = _horiz(F)
    vert = F.y if F.is_side() else F.z
    # soft bands (peel layers) 3-6 texels tall, each a slightly different value
    band = np.floor((vert + 5 * hash2(np.floor(h / 6).astype(np.int64), np.full(h.shape, 3, np.int64), seed)) / 4.0)
    lvl = np.floor(hash2(band.astype(np.int64), np.full(h.shape, 9, np.int64), seed) * 3) - 1
    F.val[m0] += 0.035 * lvl[m0]
    # lenticels: 1-texel-tall horizontal dashes, 2-4 long, on about every other row
    r = np.floor(vert + 0.01).astype(np.int64)
    rowok = hash2(r, np.full_like(r, 1), seed + 2) < 0.45
    L = 3
    cell = np.floor((h + 11 * hash2(r, np.full_like(r, 4), seed)) / (L + 3)).astype(np.int64)
    within = np.mod(h + 11 * hash2(r, np.full_like(r, 4), seed), L + 3)
    dash = rowok & (hash2(cell, r, seed + 5) < 0.5 * lent) & (within < 2 + np.floor(2 * hash2(cell, r, seed + 6)))
    d = dash & m0
    F.mat[d] = BIRCHDK
    F.val[d] = 0.12
    below = np.zeros_like(d)
    # light texel under each dash (papery lip)
    if F.is_side():
        below = P._shift(d, 1, 0) & m0 & ~d
        F.val[below] += 0.06
    if knots:
        # knot eyes: dark wedge shapes on a coarse grid
        gx = np.floor(h / 9).astype(np.int64); gy = np.floor(vert / 9).astype(np.int64)
        has = hash2(gx, gy, seed + 7) < 0.22
        cx = gx * 9 + 2 + 5 * hash2(gx, gy, seed + 8); cy = gy * 9 + 2 + 5 * hash2(gx, gy, seed + 9)
        dx = np.abs(h - cx); dy = np.abs(vert - cy)
        eye = has & (dy < 1.01) & (dx < 3.2 - 1.6 * dy) & m0
        F.mat[eye] = BIRCHDK
        F.val[eye] = 0.0
        F.val[eye & (dx < 0.8)] -= 0.08


def scallop_plates(F, region, pitch, seed=0, y_top=None, period=6.0):
    """layered birch plates with ROUNDED (scalloped) lower edges: dark under-edge outline, light rim, and a peeled
    pale-heartwood lip on the plate below."""
    region = np.asarray(region, bool) & F.alpha
    if not region.any():
        return
    if y_top is None:
        y_top = F.y[region].max() + 1e-3
    h = _horiz(F)
    row = np.floor((y_top - F.y) / pitch)
    ph = hash2(row.astype(np.int64), np.full(h.shape, 2, np.int64), seed) * period
    sc = np.round(1.0 * (1 - np.cos(2 * math.pi * (h + ph) / period)))     # 0..2 rounded scallop
    s = (y_top - F.y + sc) / pitch
    k = np.floor(s); f = s - k
    F.val[region] += 0.08 * (0.5 - f[region])
    px = 1.0 / pitch
    rim = region & (f > 1 - 2 * px) & (f <= 1 - px)
    F.val[rim] += 0.08
    edge = region & (f > 1 - px)                       # soft grey outline along the scalloped edge
    F.mat[edge] = BIRCH
    F.val[edge] -= 0.24
    # peeled heartwood just under it, only where the bark has curled (about 1 in 3 scallops)
    curl = hash2(np.floor((h + ph) / period).astype(np.int64), k.astype(np.int64), seed + 4) < 0.35
    lip = region & (f < px) & (k > 0) & curl
    F.mat[lip] = BWOOD
    F.val[lip] -= 0.1


def scallop_hem(F, seed=0, depth=2, period=5.0):
    """rounded torn hem (replaces Oak's jagged tatter)."""
    dv, du = P.face_down(F)
    if (dv, du) == (1, 0):
        dist = F.fh - F.v; col = F.u
    elif (dv, du) == (-1, 0):
        dist = F.v; col = F.u
    elif (dv, du) == (0, 1):
        dist = F.fw - F.u; col = F.v
    else:
        dist = F.u; col = F.v
    cw = F.x + F.z
    cut = np.round(depth * 0.5 * (1 + np.cos(2 * math.pi * (cw / period + hash2(np.zeros_like(F.iu), np.zeros_like(F.iu), seed)))))
    keep = dist > cut
    F.alpha &= keep
    near = F.alpha & (dist <= cut + 1.0)
    F.val[near] -= 0.12


def outline_cut(F):
    a = F.alpha
    e = a & ~(P._shift(a, 0, 1) & P._shift(a, 0, -1))
    F.mat[e] = BIRCH
    F.val[e] -= 0.22


def cut_rim(F, which="bottom"):
    d = {"top": F.v, "bottom": F.fh - F.v, "left": F.u, "right": F.fw - F.u}[which]
    m = (d < 1) & F.alpha
    F.mat[m] = BWOOD
    F.val[m] -= 0.05
    return m


def bleaflet(F, cu, cv, s=1):
    m = (np.abs(F.u - cu) < 1.0 * s + 0.01) & (np.abs(F.v - cv) < 0.6 * s + 0.01)
    m |= (np.abs(F.u - cu) < 0.51) & (np.abs(F.v - cv) < 1.1 * s + 0.01)
    stamp(F, m, BLEAF, hl=0.2, lo=0.1, shadow=0.12, add=0.05)


# ------------------------------------------------------------------ quads: birch leaf, catkin, twig sprig
def p_birch_leaf(F, stem_at_bottom=True):
    """ovate birch leaf with a pointed tip and a toothed edge."""
    F.mat[:] = BLEAF
    t = (F.fh - F.v) / F.fh if stem_at_bottom else F.v / F.fh
    hw = (F.fw / 2.0) * np.clip(np.sin(np.pi * np.clip(t, 0, 1) ** 0.75), 0, 1) ** 0.9
    hw = hw - 0.5 * ((F.iv % 2) == 0)                   # teeth
    du = F.u - F.fw / 2.0
    keep = np.abs(du) <= hw + 0.2
    stem = (np.abs(du) < 0.51) & (t < 0.14)
    F.alpha &= keep | stem
    F.mat[stem] = CATKIN
    F.val[stem] = -0.15
    F.val[np.abs(du) < 0.5] -= 0.1
    F.val[(du < -0.5) & keep] += 0.06
    F.val += 0.08 * (t - 0.5)


def p_catkin(F):
    """hanging catkin: stem on top, a long scaly olive-gold body, rounded ends."""
    F.mat[:] = CATKIN
    t = F.v / F.fh                                       # 0 top .. 1 bottom
    hw = np.where(t < 0.18, 0.5, (F.fw / 2.0) * np.clip(np.clip(np.sin(np.pi * (t - 0.18) / 0.82), 0, 1) ** 0.4, 0.3, 1))
    du = F.u - F.fw / 2.0
    F.alpha &= np.abs(du) <= hw + 0.05
    stem = t < 0.18
    F.mat[stem] = BIRCHDK
    F.val[stem] = 0.25
    scale = ~stem & ((F.iv % 2) == 0)
    F.val[scale] -= 0.12
    F.val[~stem & (du < 0)] += 0.06


def p_sprig(F):
    """small birch twig with two leaves (alpha cut): stem bottom-centre to top-right, leaves left + top."""
    F.alpha[:] = False
    cx = F.fw / 2.0
    t = (F.fh - F.v) / F.fh
    stem_x = cx + (t - 0.1) * 2.0
    stem = (np.abs(F.u - stem_x) < 0.6) & (t < 0.85)
    F.alpha |= stem
    F.mat[stem] = BIRCHDK
    F.val[stem] = 0.3
    for (lx, ly, rx, ry) in ((cx - 1.8, F.fh * 0.45, 1.6, 2.2), (cx + 2.0, F.fh * 0.15, 1.5, 2.0)):
        e = ((F.u - lx) / rx) ** 2 + ((F.v - ly) / ry) ** 2 <= 1.0
        F.alpha |= e
        F.mat[e] = BLEAF
        F.val[e] = 0.0 + 0.08 * (F.u[e] < lx)


# ================================================================== HEAD
def p_cap(F):
    birch_base(F, seed=1)
    if F.is_side():
        rope_band(F, -4.0, -2.0)
        F.val[F.v < 1] += 0.05
        if F.face == "front":
            k = (np.abs(F.lx - 4.5) < 1.6) & (np.abs(F.ly + 3.0) < 1.6)
            stamp(F, k, ROPE, hl=0.2, lo=0.1, shadow=0.16, add=0.04)


def p_cap_upper(F):
    birch_base(F, seed=2, knots=False)
    if F.is_side():
        F.val[F.v > F.fh - 1] -= 0.14


def p_dome(F):
    birch_base(F, seed=3, knots=False)
    if F.face == "top":
        r = np.hypot(F.lx, F.lz)
        ring = r < 5.5
        F.mat[ring] = BWOOD
        F.val[ring & ((np.floor(r * 0.9) % 2) == 1)] -= 0.1
        F.val[r < 1.2] -= 0.1
    else:
        cut_rim(F, "top")


def p_brim(F):
    birch_base(F, seed=4, lent=0.7, knots=False)
    if F.is_side():
        F.val[F.v < 1] += 0.05
        F.val[F.v > F.fh - 1] -= 0.14
    elif F.face == "bottom":
        F.mat[:] = BWOOD
        F.val -= 0.2


def p_helmback(F):
    birch_base(F, seed=5)
    if F.is_side():
        scallop_plates(F, F.alpha, 8.0, seed=5)
        scallop_hem(F, seed=5, depth=2)


def p_cheek(F):
    birch_base(F, seed=6)
    if F.is_side():
        scallop_plates(F, F.alpha, 8.0, seed=6)
        scallop_hem(F, seed=6, depth=2, period=4.0)


def p_crown_mid(F):
    birch_base(F, seed=7, knots=False)
    taper_top(F, F.ly.max() + 0.5, 11.0, 2.6)
    _side_cut(F, 11.0)
    if F.face in ("front", "back"):
        outline_cut(F)


def p_crown_side(F):
    birch_base(F, seed=8, knots=False)
    taper_top(F, F.ly.max() + 0.5, 8.0, 2.1)
    _side_cut(F, 8.0)
    if F.face in ("front", "back"):
        outline_cut(F)


def p_leaf(F):
    p_birch_leaf(F)


HEAD_OVR = {
    "HelmCap": dict(mat=BIRCH, paint=p_cap),
    "HelmUpper": dict(mat=BIRCH, paint=p_cap_upper),
    "HelmDome": dict(mat=BIRCH, paint=p_dome),
    "HelmBrim": dict(mat=BIRCH, paint=p_brim),
    "HelmBack": dict(mat=BIRCH, paint=p_helmback),
    "R-Cheek": dict(mat=BIRCH, paint=p_cheek),
    # taller, thinner crown points (Oak: 7x13 + 6x10)
    "CrownMid": dict(mat=BIRCH, paint=p_crown_mid, size=(5, 16, 2), pivot=(0, 19.0, 15.25)),
    "R-CrownSide": dict(mat=BIRCH, paint=p_crown_side, size=(4, 12, 2), pivot=(-8.0, 17.0, 14.75), rot=(0, 0, 18)),
    "R-HelmLeaf": dict(mat=BLEAF, paint=p_leaf, size=(5, 8)),
}
HEAD_ADD = [
    # the catkin mark: a pair hanging from the brim at the LEFT temple
    dict(name="L-HelmCatkinA", bone="Head", pivot=(17.0, 4.5, 6.0), rot=(0, 90, 0), size=(3, 9), offset=(0, -4.5, 0),
         mat=CATKIN, paint=p_catkin, double=True),
    dict(name="L-HelmCatkinB", bone="Head", pivot=(17.0, 4.5, 2.5), rot=(0, 90, 6), size=(3, 7), offset=(0, -3.5, 0),
         mat=CATKIN, paint=p_catkin, double=True),
]


# ================================================================== CHEST
def _laced_gap(F, halfw, y0, y1, k=1.0):
    gap = np.abs(F.x) < halfw
    F.mat[gap] = SAGE
    F.val[gap] = -0.12
    ph = F.y % 4.0
    lace = gap & (np.abs(np.abs(F.x) - np.abs(ph - 2.0) * k) < 0.55)
    F.mat[lace] = ROPE
    F.val[lace] = 0.05
    O.sap_vein(F, 0.0, y0, y1, faint=0.35)


def p_cuirass(F):
    birch_base(F, seed=10)
    if F.is_side():
        scallop_plates(F, F.alpha, 10.0, seed=10)
        if F.face == "front":
            _laced_gap(F, 2.6, 66.0, 84.0)


def p_breast(F):
    birch_base(F, seed=11)
    if F.is_side():
        scallop_plates(F, F.alpha, 9.0, seed=11)
        scallop_hem(F, seed=11, depth=2)
        cut_rim(F, "top")
        if F.face == "front":
            inner = (np.abs(F.x) < 3.1) & F.alpha
            F.mat[inner] = BWOOD
            eye = inner & ((np.floor(F.y) % 4) == 1)
            F.mat[eye] = ROPE
            F.val[eye] = -0.05


def p_plackart(F):
    birch_base(F, seed=12)
    if F.is_side():
        scallop_plates(F, F.alpha, 9.0, seed=12)
        if F.face == "front":
            _laced_gap(F, 2.0, 56.0, 68.0, k=0.8)


def p_bark_belt(F):
    """twisted strip of birch bark (white + charcoal twist) instead of Oak's ivy vine."""
    F.mat[F.alpha] = BIRCH
    a = F.iu + F.iv if F.face not in ("left", "right") else F.iu - F.iv
    F.val[(a % 4) == 0] -= 0.3
    F.mat[(a % 4) == 0] = BIRCHDK
    F.val[(a % 4) == 1] += 0.06
    if F.is_side():
        F.val[F.v < 1] += 0.04
        F.val[F.v > F.fh - 1] -= 0.1


def p_clasp(F):
    """carved heartwood knot clasp (the catkins hang from it)."""
    F.mat[:] = BWOOD
    if F.face == "front":
        r = np.hypot(F.u - F.fw / 2, F.v - F.fh / 2)
        F.val[(r > 1.0) & (r < 1.8)] -= 0.15
        F.val[r <= 1.0] -= 0.25
        F.val[F.u < 1] += 0.08
        F.val[F.v > F.fh - 1] -= 0.08


def p_tassel(F):
    birch_base(F, seed=13)
    if F.face in ("front", "back"):
        scallop_plates(F, F.alpha, 5.0, seed=13)
        strip = (np.floor(F.u) % 4) == 3 if F.face == "front" else (np.floor(F.fw - F.u) % 4) == 3
        F.alpha &= ~(strip & (F.v > 4))
    scallop_hem(F, seed=13, depth=2, period=4.0)


def p_tassel_back(F):
    birch_base(F, seed=14)
    if F.face in ("front", "back"):
        scallop_plates(F, F.alpha, 5.0, seed=14)
        strip = (np.floor(F.u) % 4) == 3
        F.alpha &= ~(strip & (F.v > 4))
    scallop_hem(F, seed=15, depth=2, period=4.0)


def p_roll(F):
    """rolled bark curl: white outside, pale heartwood spiral on the ends."""
    birch_base(F, seed=16, knots=False)
    if F.face in ("left", "right") and F.node["size"][2] <= 3 or (F.face in ("front", "back") and F.node["size"][0] <= 3):
        F.mat[:] = BWOOD
        F.val[(F.iu + F.iv) % 2 == 0] -= 0.15
    else:
        F.val[F.v > F.fh - 1] -= 0.12
        F.val[F.v < 1] += 0.06


def p_collar(F):
    twist(F, VINE, 3)
    if F.face == "top":
        r = np.maximum(np.abs(F.lx) / 10.0, np.abs(F.lz) / 8.5)
        F.mat[r < 0.7] = SAGE
        F.val[r < 0.7] -= 0.3
    if F.face == "front":
        for cu in (3.0, F.fw - 3.0):
            bleaflet(F, cu, 1.4)


def p_pauldron(F):
    birch_base(F, seed=17)
    if F.face == "top":
        scallop_plates(F, F.alpha, 4.0, seed=17)
    if F.is_side():
        cut_rim(F, "bottom")
        rope_band(F, -0.6, 0.6)


def p_pauldron_lame(F):
    birch_base(F, seed=18)
    if F.is_side():
        cut_rim(F, "top")
        scallop_hem(F, seed=18, depth=2, period=4.0)


def p_vine(F):
    twist(F, VINE, 3)
    if F.face == "top":
        for k in range(2, F.fh - 1, 5):
            bleaflet(F, 1.5, k + 0.5)


def p_sleeve(F):
    mottle(F, scale=8, amp=0.03, seed=21)
    if F.is_side():
        coord = _horiz(F)
        F.val += 0.05 * np.round(np.sin(2 * math.pi * coord / 3) * 1.5) / 1.5
        rope_band(F, 4.0, 6.0)
        rope_band(F, -7.5, -5.5)


CHEST_OVR = {
    "Cuirass": dict(mat=BIRCH, paint=p_cuirass),
    "R-Breast": dict(mat=BIRCH, paint=p_breast),
    "Collar": dict(paint=p_collar),
    "Plackart": dict(mat=BIRCH, paint=p_plackart),
    "VineBelt": dict(mat=BIRCH, paint=p_bark_belt),
    "R-Tassel": dict(mat=BIRCH, paint=p_tassel, size=(11, 12, 1), offset=(0, -6.0, 0)),
    "TasselBack": dict(mat=BIRCH, paint=p_tassel_back),
    "R-Pauldron": dict(mat=BIRCH, paint=p_pauldron),
    "R-PauldronLame": dict(mat=BIRCH, paint=p_pauldron_lame),
    "L-Vine": dict(paint=p_vine),
    "L-VineLeafA": dict(mat=BLEAF, paint=p_leaf),
    "L-VineLeafB": dict(mat=BLEAF, paint=lambda F: p_birch_leaf(F, stem_at_bottom=False)),
    "R-Sleeve": dict(mat=SAGE, paint=p_sleeve),
}
CHEST_DROP = ("Acorn", "AcornCap")
CHEST_ADD = [
    dict(name="Clasp", bone="Belly", pivot=(0, -5.8, 11.0), size=(5, 5, 2), mat=BWOOD, paint=p_clasp, skip=("back",)),
    dict(name="CatkinA", bone="Belly", pivot=(-3.0, -8.0, 12.2), rot=(0, 0, -8), size=(3, 8), offset=(0, -4.0, 0),
         mat=CATKIN, paint=p_catkin, double=True),
    dict(name="CatkinB", bone="Belly", pivot=(0.0, -8.0, 12.3), rot=(0, 0, 0), size=(3, 10), offset=(0, -5.0, 0),
         mat=CATKIN, paint=p_catkin, double=True),
    dict(name="CatkinC", bone="Belly", pivot=(3.0, -8.0, 12.1), rot=(0, 0, 8), size=(3, 7), offset=(0, -3.5, 0),
         mat=CATKIN, paint=p_catkin, double=True),
    # rolled bark curl along the outer edge of each shoulder plate (new shape vs Oak)
    dict(name="R-PauldronRoll", bone="R-Arm", parent="R-Pauldron", pivot=(-6.0, -1.0, 0), size=(3, 3, 16), mat=BIRCH,
         paint=p_roll, mirror=True),
    # rolled bark curl along the top of the front tassels
    dict(name="R-TasselRoll", bone="Pelvis", parent="R-Tassel", pivot=(0, 5.8, 0.6), size=(11, 2, 2),
         mat=BIRCH, paint=p_roll, mirror=True),
]


# ================================================================== HANDS
def p_bracer(F):
    birch_base(F, seed=20)
    if F.is_side():
        scallop_plates(F, F.alpha, 7.0, seed=20)
        cut_rim(F, "top")
        rope_band(F, 2.6, 4.6)
        rope_band(F, -5.0, -3.0)


def p_bracer_plate(F):
    birch_base(F, seed=21)
    if F.is_side():
        cut_rim(F, "top")
        scallop_hem(F, seed=21, depth=2, period=4.0)


def p_glove(F):
    birch_base(F, seed=22, lent=0.8, knots=False)
    if F.is_side():
        wrap = ((F.ly > 1.0) & (F.ly < 3.0)) | ((F.ly > -3.0) & (F.ly < -1.0))
        stamp(F, wrap, ROPE, hl=0.12, lo=0.12, shadow=0.16)
        F.val[wrap & (((F.iu + F.iv) % 3) == 0)] -= 0.15
        fingers = F.ly < -4.0
        F.mat[fingers] = SAGE
        F.val[fingers] -= 0.05
        F.val[fingers & ((F.iu % 3) == 0)] -= 0.1
    elif F.face == "bottom":
        F.mat[:] = SAGE
        F.val -= 0.15


HANDS_OVR = {
    "R-Bracer": dict(mat=BIRCH, paint=p_bracer),
    "R-BracerPlate": dict(mat=BIRCH, paint=p_bracer_plate),
    "R-Glove": dict(mat=BIRCH, paint=p_glove),
}
HANDS_ADD = [
    # twig sprig tucked into the rope band on the outer forearm (alpha-cut quad = silhouette without bulk)
    dict(name="R-Sprig", bone="R-Forearm", pivot=(-6.3, 3.0, 2.0), rot=(0, -90, 0), size=(7, 9), offset=(0, 4.5, 0),
         mat=BLEAF, paint=p_sprig, double=True, mirror=True),
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
    birch_base(F, seed=24, knots=False)
    if F.face == "front":
        cut_rim(F, "top")
        scallop_hem(F, seed=24, depth=1, period=4.0)
        e = (np.abs(F.lx) < 2.2) & (np.abs(F.ly) < 0.6)
        F.mat[e] = BIRCHDK
        F.val[e] = 0.0


def p_greave(F):
    birch_base(F, seed=25)
    if F.is_side():
        scallop_plates(F, F.ly > -8.0, 8.0, seed=25)
        cut_rim(F, "top")
        rope_band(F, 6.0, 8.0)
        rope_band(F, -7.5, -5.5)
        if F.face == "back":
            lace = (np.abs(np.abs(F.lx) - ((F.iv % 4) * 0.5)) < 0.5) & (np.abs(F.lx) < 2.1) & (F.ly > -5.0)
            F.mat[lace] = ROPE
            F.val[lace] = 0.0


def p_boot(F):
    birch_base(F, seed=26, lent=0.8)
    F.val -= 0.03
    if F.is_side():
        sole = F.ly < -2.6
        F.mat[sole] = BIRCHDK
        F.val[sole] = 0.2
        F.val[sole & (F.ly > -3.6)] += 0.12
        if F.face == "front":
            cap = (F.ly > -2.6) & (F.ly < 1.5) & (np.abs(F.lx) < 5.6)
            stamp(F, cap, BIRCH, hl=0.12, lo=0.12, shadow=0.16, add=0.04)
        if F.face in ("left", "right"):
            wrap = (np.abs(F.lz + 3.0) < 1.6) & (F.ly > -2.6)
            stamp(F, wrap, ROPE, hl=0.12, lo=0.12, shadow=0.16)
            F.val[wrap & (((F.iu + F.iv) % 3) == 0)] -= 0.15
    elif F.face == "top":
        wrap = np.abs(F.lz + 3.0) < 1.6
        stamp(F, wrap, ROPE, hl=0.12, lo=0.12, shadow=0.14)
        F.val[wrap & (((F.iu + F.iv) % 3) == 0)] -= 0.15
    elif F.face == "bottom":
        F.mat[:] = BIRCHDK
        F.val[:] = 0.1


LEGS_OVR = {
    "Breeches": dict(mat=SAGE, paint=p_breeches),
    "R-Trouser": dict(mat=SAGE, paint=p_trouser),
    "R-Knee": dict(mat=BIRCH, paint=p_knee),
    "R-Greave": dict(mat=BIRCH, paint=p_greave),
    "R-Boot": dict(mat=BIRCH, paint=p_boot),
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
