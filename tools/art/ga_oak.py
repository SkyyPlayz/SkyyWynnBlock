"""SkyWynn Foraging armor - F1 Grove - OAK set. Geometry + paint design (ORIGINAL; no vanilla geometry or pixels).

Brief (Skyy): "lets still make the farming and gathering armor" / "do a design per tree type in that set, so every
hardwood gets its own design in that trees color". Approved concept family = layered bark plates with jagged lower
edges, vertical bark grain, vine/root trims, twisted vine belt, sap vein up the chest, small leaves, wrapped bark
gauntlets, moss-grey cloth trousers, bark greaves + wrapped bark boots. Tier 1 (F1 Grove) echoes Copper: open plates
with a laced gap, thin rope bands, ONE vine over the left shoulder, rope lashing, small 3-point crown, faint sap.
Oak identity: grey-brown deeply furrowed oak bark, pale cut-oak plate rims, lobed oak leaves, an acorn clasp + badge.
Helmet in every tier (ART-RESUME default): an open-faced bark kettle helm (Copper echo) with the 3-point crown on it.
Keep it NOT bulky: plates sit ~1 unit off the body like the Dark Leather revision.

Node spec: see make_foraging_armor.py (same as the Dark Leather pipeline).
"""
import math
import numpy as np
import ga_paint as P
from ga_paint import (BARK, WOOD, ROPE, VINE, LEAF, SAP, CLOTH, ACORN, ACORNCAP, STITCH,
                      stamp, rivet, stitches, lames, tatter, mottle, wear, hash2)

TIER, TREE = "F1_Grove", "Oak"


# ------------------------------------------------------------------ shared paint helpers
def _uv_of(F, lp):
    d = np.linalg.norm(F.L - np.array(lp, float), axis=-1)
    i = np.unravel_index(np.argmin(d), d.shape)
    return F.u[i], F.v[i]


def _horiz(F):
    """world coordinate running across the face (for vertical grain)."""
    if F.is_side():
        return F.x * abs(F.n[2]) + F.z * abs(F.n[0])
    return F.x


def bark_base(F, seed=0, wear_amt=0.2, depth=1.0, grain=True):
    """oak bark, Hytale-flat: long vertical streaks (2-3 value levels per column run) split by a few long dark
    furrows that break and rejoin; a light ridge texel left of each furrow (light from the upper left)."""
    mottle(F, scale=7.0, amp=0.03, seed=3 + seed)
    wear(F, amount=wear_amt, scale=4.0, seed=11 + seed, thr=0.8)
    if not grain:
        return
    h = _horiz(F)
    vert = F.y if F.is_side() else F.z
    col = np.floor(h + 0.01).astype(np.int64)
    run = col // 2
    lvl = np.floor(hash2(run, np.full_like(run, 2), seed) * 3) - 1          # -1, 0, 1 per 2-texel run
    m0 = (F.mat == BARK)
    F.val[m0] += 0.045 * lvl[m0]

    def furrow(c):
        L = 7 + np.floor(6 * hash2(c, np.full_like(c, 6), seed))
        seg = np.floor((vert + hash2(c, np.full_like(c, 5), seed) * 11) / L).astype(np.int64)
        return (hash2(c // 1, seg, seed + 1) < 0.22) & ((c % 2) == 0)
    fur = furrow(col) & m0
    F.val[fur] -= 0.18 * depth
    ridge = furrow(col + 1) & ~fur & m0
    F.val[ridge] += 0.06 * depth


def cut_rim(F, which="bottom", width=1):
    """pale cut-oak edge where the plate is broken off (shows the heartwood)."""
    d = {"top": F.v, "bottom": F.fh - F.v, "left": F.u, "right": F.fw - F.u}[which]
    m = (d < width) & F.alpha
    F.mat[m] = WOOD
    F.val[m] -= 0.05
    return m


def jag_plates(F, region, pitch, depth=2, seed=0, y_top=None):
    """layered bark plates: each row overlaps the one below with a JAGGED lower edge + pale cut rim + shadow."""
    region = np.asarray(region, bool) & F.alpha
    if not region.any():
        return
    if y_top is None:
        y_top = F.y[region].max() + 1e-3
    h = _horiz(F)
    hc = np.floor(h / 2).astype(np.int64)
    s0 = (y_top - F.y) / pitch
    row = np.floor(s0).astype(np.int64)
    # jagged: per (row, 2-texel column) the edge drops 0..depth texels
    jag = np.floor(hash2(hc, row, seed + 3) * (depth + 0.99))
    s = (y_top - F.y + jag) / pitch
    k = np.floor(s); f = s - k
    F.val[region] += 0.12 * (0.5 - f[region])
    px = 1.0 / pitch
    edge = region & (f > 1 - px)          # lit lower lip of the upper plate
    F.val[edge] += 0.1
    below = region & (f < px) & (k > 0)   # dark gap / shadow where it overlaps the next plate
    F.val[below] -= 0.26


def rope_band(F, y0, y1, local=True, mat=ROPE):
    """thin twisted twine band (diagonal strands)."""
    y = F.ly if local else F.y
    m = (y > y0) & (y < y1) & F.alpha
    if not m.any():
        return m
    stamp(F, m, mat, hl=0.12, lo=0.12, shadow=0.16)
    strand = m & (((F.iu + F.iv) % 3) == 0)
    F.val[strand] -= 0.16
    F.val[m & (((F.iu + F.iv) % 3) == 1)] += 0.06
    return m


def twist(F, mat=VINE, pitch=3):
    """twisted vine / rope surface over the whole face."""
    F.mat[F.alpha] = mat
    a = F.iu + F.iv if F.face not in ("left", "right") else F.iu - F.iv
    F.val[(a % pitch) == 0] -= 0.17
    F.val[(a % pitch) == 1] += 0.07


def leaflet(F, cu, cv, s=1):
    """tiny painted oak leaf (2-3 texels) on vines / collars."""
    m = (np.abs(F.u - cu) < 1.0 * s + 0.01) & (np.abs(F.v - cv) < 0.6 * s + 0.01)
    m |= (np.abs(F.u - cu) < 0.51) & (np.abs(F.v - cv) < 1.1 * s + 0.01)
    stamp(F, m, LEAF, hl=0.2, lo=0.1, shadow=0.12, add=0.05)
    return m


def oak_leaf_shape(t, w):
    """half width of an oak leaf at t (0 stem .. 1 tip): rounded lobes, narrow at the stem."""
    env = np.clip(np.sin(np.pi * np.clip(t, 0, 1) ** 0.9), 0, 1) ** 0.7
    lobe = 0.55 + 0.45 * np.abs(np.cos(np.pi * 2.0 * (t - 0.08)))
    return w * env * lobe


def p_leaf_quad(F, stem_at_bottom=True, w=None):
    """whole oak leaf cut out of a quad: lobed outline, midrib, two-tone."""
    F.mat[:] = LEAF
    t = (F.fh - F.v) / F.fh if stem_at_bottom else F.v / F.fh
    ww = (F.fw / 2.0) if w is None else w
    hw = oak_leaf_shape(t, ww)
    du = F.u - F.fw / 2.0
    keep = np.abs(du) <= hw + 0.15
    stem = (np.abs(du) < 0.51) & (t < 0.12)
    F.alpha &= keep | stem
    F.mat[stem] = VINE
    mid = np.abs(du) < 0.5
    F.val[mid] -= 0.12
    F.val[(du < -0.5) & keep] += 0.06         # lit half
    F.val[(np.abs(du) > hw - 0.9) & keep & ~mid] -= 0.06
    F.val += 0.08 * (t - 0.5)


def acorn_badge(F, cu, cv):
    """painted acorn: cap + nut (3x5)."""
    nut = (np.abs(F.u - cu) < 1.6) & (F.v > cv) & (F.v < cv + 3.0)
    cap = (np.abs(F.u - cu) < 2.1) & (F.v > cv - 1.4) & (F.v <= cv)
    stamp(F, nut, ACORN, hl=0.2, lo=0.12, shadow=0.14)
    stamp(F, cap, ACORNCAP, hl=0.16, lo=0.1, shadow=0.1)
    F.val[nut & (np.abs(F.u - cu + 0.5) < 0.5)] += 0.1


def sap_vein(F, x0, y0, y1, faint=0.3):
    """faint glowing sap line (tier 1 = faint): a wavy trunk with two short branches, world xy on front faces."""
    if F.n[2] < 0.5:
        return
    yy = F.y
    xc = x0 + 0.8 * np.sin((yy - y0) * 0.45)
    trunk = (np.abs(F.x - xc) < 0.5) & (yy > y0) & (yy < y1)
    m = trunk
    for (by, dirx) in ((y0 + (y1 - y0) * 0.55, -1), (y0 + (y1 - y0) * 0.8, 1)):
        t = (yy - by)
        br = (t > 0) & (t < 3.5) & (np.abs(F.x - (x0 + dirx * t * 0.9)) < 0.5)
        m = m | br
    m &= F.alpha
    F.mat[m] = SAP
    F.val[m] += -0.25 + 0.25 * faint
    F.lockval[m] = False


def taper_top(F, top, length, half_w, axis="x"):
    ly = F.ly
    c = F.lx if axis == "x" else F.lz
    zone = ly > top - length
    allow = half_w * (top - ly) / length + 0.35
    F.alpha &= ~(zone & (np.abs(c) > allow))


# ================================================================== HEAD: open-faced bark kettle helm + 3-point crown
def p_cap(F):
    bark_base(F, seed=1)
    if F.is_side():
        rope_band(F, -4.0, -2.0)                    # rope lashing round the brow
        F.val[F.v < 1] += 0.06
        if F.face == "front":
            # rope knot just right of centre under the crown
            k = (np.abs(F.lx - 4.5) < 1.6) & (np.abs(F.ly + 3.0) < 1.6)
            stamp(F, k, ROPE, hl=0.2, lo=0.1, shadow=0.16, add=0.04)
    elif F.face == "top":
        r = np.maximum(np.abs(F.lx) / 16.0, np.abs(F.lz) / 15.0)
        F.val[r < 0.72] -= 0.04


def p_cap_upper(F):
    bark_base(F, seed=6)
    if F.is_side():
        F.val[F.v > F.fh - 1] -= 0.1


def p_dome(F):
    bark_base(F, seed=2)
    if F.face == "top":
        # growth-ring knot on the crown of the helm (cut oak top)
        r = np.hypot(F.lx, F.lz)
        ring = (r < 5.5)
        F.mat[ring] = WOOD
        F.val[ring & ((np.floor(r * 0.9) % 2) == 1)] -= 0.12
        F.val[r < 1.2] -= 0.1
    else:
        cut_rim(F, "top")


def p_brim(F):
    bark_base(F, seed=3, depth=0.7)
    if F.is_side():
        F.val[F.v < 1] += 0.05
        F.val[F.v > F.fh - 1] -= 0.1
    elif F.face == "top":
        r = np.maximum(np.abs(F.lx) / 18.0, np.abs(F.lz) / 17.0)
        F.val[r > 0.93] += 0.06
    elif F.face == "bottom":
        F.val -= 0.2


def p_helmback(F):
    bark_base(F, seed=4)
    if F.is_side():
        jag_plates(F, F.alpha, 4.5, depth=2, seed=4)
        tatter(F, depth=2, seed=4)


def p_cheek(F):
    bark_base(F, seed=5)
    if F.is_side():
        jag_plates(F, F.alpha, 5.0, depth=1, seed=5)
        tatter(F, depth=2, seed=6)
        if F.face == "left":
            cu, cv = _uv_of(F, (0, 4.5, 3.0))
            rivet(F, cu, cv, WOOD)


def _outline_cut(F):
    """pale cut-oak rim along every alpha edge of a cut-out point (reads as a carved bark point)."""
    a = F.alpha
    e = a & ~(P._shift(a, 0, 1) & P._shift(a, 0, -1))
    F.mat[e] = WOOD
    F.val[e] -= 0.08


def _side_cut(F, length):
    """left/right faces of a tapered point: keep only the part below the taper (its edges are cut-outs)."""
    if F.face in ("left", "right"):
        F.alpha &= F.ly <= F.ly.max() + 0.5 - length


def p_crown_mid(F):
    bark_base(F, seed=7)
    taper_top(F, F.ly.max() + 0.5, 8.0, 3.2)
    _side_cut(F, 8.0)
    if F.face in ("front", "back"):
        _outline_cut(F)
        F.val[(np.abs(F.lx) < 0.5) & (F.ly > -2)] += 0.08
        if F.face == "front":
            acorn_badge(F, F.fw / 2.0, F.fh - 5.2)


def p_crown_side(F):
    bark_base(F, seed=8)
    taper_top(F, F.ly.max() + 0.5, 6.0, 2.6)
    _side_cut(F, 6.0)
    if F.face in ("front", "back"):
        _outline_cut(F)


def p_leaf(F):
    p_leaf_quad(F)


HEAD = [
    dict(name="HelmCap", bone="Head", pivot=(0, 9.75, -0.5), size=(32, 10, 31), mat=BARK, paint=p_cap,
         skip=("bottom",)),
    dict(name="HelmUpper", bone="Head", pivot=(0, 16.0, -0.5), size=(28, 3, 27), mat=BARK, paint=p_cap_upper,
         skip=("bottom",)),
    dict(name="HelmDome", bone="Head", pivot=(0, 18.25, -0.5), size=(22, 2, 21), stretch=(1, 0.75, 1), mat=BARK,
         paint=p_dome, skip=("bottom",)),
    dict(name="HelmBrim", bone="Head", pivot=(0, 5.0, -0.5), size=(36, 2, 34), mat=BARK, paint=p_brim),
    dict(name="HelmBack", bone="Head", pivot=(0, -4.0, -15.25), size=(32, 18, 2), mat=BARK, paint=p_helmback,
         skip=("top",)),
    dict(name="R-Cheek", bone="Head", pivot=(-15.75, -2.5, -7.0), size=(2, 14, 14), mat=BARK, paint=p_cheek,
         skip=("top",), mirror=True),
    dict(name="CrownMid", bone="Head", pivot=(0, 17.5, 15.25), size=(7, 13, 2), mat=BARK, paint=p_crown_mid,
         skip=("top", "bottom")),
    dict(name="R-CrownSide", bone="Head", pivot=(-9.0, 16.0, 14.75), rot=(0, 0, 14), size=(6, 10, 2), mat=BARK,
         paint=p_crown_side, skip=("top", "bottom"), mirror=True),
    dict(name="R-HelmLeaf", bone="Head", pivot=(-14.5, 15.5, 9.0), rot=(10, -35, 38), size=(6, 9),
         offset=(0, 4.0, 0), mat=LEAF, paint=p_leaf, double=True, mirror=True),
]


# ================================================================== CHEST: open bark cuirass, laced gap, vine trims
LACE_X = 2.0


def p_cuirass(F):
    bark_base(F, seed=10)
    if F.is_side():
        jag_plates(F, F.alpha, 7.0, depth=2, seed=10)
        if F.face == "front":
            # laced gap: moss cloth shows between the two breast plates, rope X lacing + faint sap vein
            gap = np.abs(F.x) < 2.6
            F.mat[gap] = CLOTH
            F.val[gap] = -0.12
            ph = (F.y * 1.0) % 4.0
            lace = gap & (np.abs(np.abs(F.x) - np.abs(ph - 2.0)) < 0.55)
            F.mat[lace] = ROPE
            F.val[lace] = 0.05
            sap_vein(F, 0.0, 66.0, 84.0, faint=0.35)


def p_breast(F):
    bark_base(F, seed=11)
    if F.is_side():
        jag_plates(F, F.alpha, 6.0, depth=2, seed=11)
        tatter(F, depth=3, seed=11)
        cut_rim(F, "top")
        if F.face == "front":
            # inner edge rim (cut oak) beside the laced gap + rope eyelets
            inner = np.abs(F.x) < 3.1
            F.mat[inner & F.alpha] = WOOD
            for yy in (70.0, 74.0, 78.0, 82.0):
                cu, cv = _uv_of(F, (F.lx[0, 0] * 0 + (F.fw / 2.0 - 1.0) * np.sign(-F.x.mean()), 0, 0))
            eye = inner & (((np.floor(F.y) % 4) == 1)) & F.alpha
            F.mat[eye] = ROPE
            F.val[eye] = -0.05


def p_plackart(F):
    bark_base(F, seed=12)
    if F.is_side():
        jag_plates(F, F.alpha, 6.0, depth=2, seed=12)
        if F.face == "front":
            gap = np.abs(F.x) < 2.0
            F.mat[gap] = CLOTH
            F.val[gap] = -0.15
            ph = F.y % 4.0
            lace = gap & (np.abs(np.abs(F.x) - np.abs(ph - 2.0) * 0.8) < 0.55)
            F.mat[lace] = ROPE
            F.val[lace] = 0.0
            sap_vein(F, 0.0, 56.0, 68.0, faint=0.35)


def p_vine_belt(F):
    twist(F, VINE, 3)
    if F.is_side():
        F.val[F.v < 1] += 0.06
        F.val[F.v > F.fh - 1] -= 0.08
        # leaflets along the belt
        for k in range(3, F.fw - 2, 7):
            leaflet(F, k + 0.5 * (hash2(np.array(k), np.array(1), 4) > 0.5), 0.6 if (k // 7) % 2 else F.fh - 0.6)


def p_acorn(F):
    F.mat[:] = ACORN
    if F.face == "front":
        F.val[F.u < 1.5] += 0.12
        F.val[F.u > F.fw - 1] -= 0.08
        F.val[F.v > F.fh - 1] -= 0.08
        tip = (F.v > F.fh - 1) & ((F.u < 1) | (F.u > F.fw - 1))
        F.alpha &= ~tip


def p_acorn_cap(F):
    F.mat[:] = ACORNCAP
    F.val[((F.iu + F.iv) % 2) == 0] -= 0.1     # scaly cup
    if F.face == "top":
        stem = (np.abs(F.lx) < 0.6) & (np.abs(F.lz) < 0.6)
        F.mat[stem] = WOOD


def p_tassel(F):
    bark_base(F, seed=13)
    if F.face in ("front", "back"):
        jag_plates(F, F.alpha, 7.0, depth=2, seed=13)
        F.val[(F.u < 1) | (F.u > F.fw - 1)] -= 0.06
        strip = (np.floor(F.u) % 4) == 3 if F.face == "front" else (np.floor(F.fw - F.u) % 4) == 3
        F.alpha &= ~(strip & (F.v > 5))
        F.val[(np.floor(F.u) % 4) == 2] -= 0.05
    tatter(F, depth=4, seed=13)


def p_tassel_back(F):
    bark_base(F, seed=14)
    if F.face in ("front", "back"):
        jag_plates(F, F.alpha, 7.0, depth=2, seed=14)
        # split into strips (a gap every 4 texels) so it reads as hanging bark tassels
        strip = (np.floor(F.u) % 4) == 3
        F.alpha &= ~(strip & (F.v > 3))
    tatter(F, depth=4, seed=15)


def p_collar(F):
    twist(F, VINE, 3)
    if F.face == "top":
        r = np.maximum(np.abs(F.lx) / 10.0, np.abs(F.lz) / 8.5)
        F.val[r < 0.7] -= 0.3
        F.mat[r < 0.7] = CLOTH
    if F.face == "front":
        for cu in (3.0, F.fw - 3.0):
            leaflet(F, cu, 1.4)


def p_pauldron(F):
    bark_base(F, seed=16)
    if F.face == "top":
        jag_plates(F, F.alpha, 4.0, depth=1, seed=16, )
        F.val[np.abs(F.lz) < 0.6] -= 0.0
    if F.is_side():
        cut_rim(F, "bottom")
        rope_band(F, -0.6, 0.6)


def p_pauldron_lame(F):
    bark_base(F, seed=17)
    if F.is_side():
        cut_rim(F, "top")
        tatter(F, depth=2, seed=17)


def p_vine(F):
    twist(F, VINE, 3)
    if F.face == "top":
        for k in range(2, F.fh - 1, 5):
            leaflet(F, 1.5, k + 0.5)


def p_sleeve(F):
    P.mottle(F, scale=8, amp=0.03, seed=21)
    if F.is_side():
        coord = _horiz(F)
        F.val += 0.05 * np.round(np.sin(2 * math.pi * coord / 3) * 1.5) / 1.5
        rope_band(F, 4.0, 6.0)
        rope_band(F, -7.5, -5.5)


CHEST = [
    dict(name="Cuirass", bone="Chest", pivot=(0, 0.3, 0.2), size=(29, 22, 21), mat=BARK, paint=p_cuirass,
         skip=("bottom",)),
    dict(name="R-Breast", bone="Chest", pivot=(-8.0, 0.5, 11.25), size=(12, 17, 2), mat=BARK, paint=p_breast,
         skip=("back",), mirror=True),
    dict(name="Collar", bone="Chest", pivot=(0, 12.0, -0.3), size=(20, 3, 17), mat=VINE, paint=p_collar,
         skip=("bottom",)),
    dict(name="Plackart", bone="Belly", pivot=(0, 0.5, 0.2), size=(27, 16, 20), mat=BARK, paint=p_plackart,
         skip=("top", "bottom")),
    dict(name="VineBelt", bone="Belly", pivot=(0, -5.8, 0.2), size=(28, 3, 21), mat=VINE, paint=p_vine_belt,
         skip=("bottom",)),
    dict(name="Acorn", bone="Belly", pivot=(0, -7.3, 11.0), size=(4, 4, 2), mat=ACORN, paint=p_acorn,
         skip=("back",)),
    dict(name="AcornCap", bone="Belly", pivot=(0, -4.8, 11.0), size=(6, 2, 3), mat=ACORNCAP, paint=p_acorn_cap,
         skip=("back",)),
    dict(name="R-Tassel", bone="Pelvis", pivot=(-6.5, 0.5, 11.3), rot=(6, 0, 3), size=(11, 13, 1),
         offset=(0, -6.5, 0), stretch=(1, 1, 1.25), mat=BARK, paint=p_tassel, skip=("top",), double=True,
         mirror=True),
    dict(name="TasselBack", bone="Pelvis", pivot=(0, 0.5, -11.2), rot=(-6, 0, 0), size=(23, 12, 1),
         offset=(0, -6.0, 0), stretch=(1, 1, 1.25), mat=BARK, paint=p_tassel_back, skip=("top",), double=True),
    dict(name="R-Pauldron", bone="R-Arm", pivot=(-5.0, 9.6, -0.3), rot=(0, 0, 27), size=(13, 4, 16), mat=BARK,
         paint=p_pauldron, skip=("bottom",), mirror=True),
    dict(name="R-PauldronLame", bone="R-Arm", pivot=(-6.6, 3.4, -0.3), rot=(0, 0, -8), size=(3, 8, 15), mat=BARK,
         paint=p_pauldron_lame, mirror=True),
    # ONE vine over the LEFT shoulder (tier-1 concept detail), with two oak leaves
    dict(name="L-Vine", bone="L-Arm", parent="L-Pauldron", pivot=(0.5, 2.5, 0), size=(3, 2, 18), mat=VINE,
         paint=p_vine),
    dict(name="L-VineLeafA", bone="L-Arm", parent="L-Vine", pivot=(1.5, 0.5, 6.0), rot=(-70, 0, -25), size=(6, 8),
         offset=(0, 3.5, 0), mat=LEAF, paint=p_leaf, double=True),
    dict(name="L-VineLeafB", bone="L-Arm", parent="L-Vine", pivot=(1.5, 0.5, -6.5), rot=(70, 0, -35), size=(5, 7),
         offset=(0, -3.0, 0), mat=LEAF, paint=lambda F: p_leaf_quad(F, stem_at_bottom=False), double=True),
    dict(name="R-Sleeve", bone="R-Arm", pivot=(0, -0.9, 0), size=(9, 22, 13), mat=CLOTH, paint=p_sleeve,
         skip=("bottom",), mirror=True),
]


# ================================================================== HANDS: wrapped bark gauntlets (fingerless)
def p_bracer(F):
    bark_base(F, seed=20)
    if F.is_side():
        jag_plates(F, F.alpha, 5.0, depth=1, seed=20)
        cut_rim(F, "top")
        rope_band(F, 2.6, 4.6)
        rope_band(F, -5.0, -3.0)


def p_bracer_plate(F):
    bark_base(F, seed=21)
    if F.is_side():
        cut_rim(F, "top")
        tatter(F, depth=2, seed=21)
        if F.face == "left":
            cu, cv = _uv_of(F, (0, 1.0, 0))
            leaflet(F, cu, cv, s=1.4)


def p_glove(F):
    """wrapped bark gauntlet: bark back-of-hand + strips of twine wrapped round, fingerless (cloth at the knuckles)."""
    bark_base(F, seed=22, depth=0.8)
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


def p_cuff(F):
    twist(F, ROPE, 3)


HANDS = [
    dict(name="R-Bracer", bone="R-Forearm", pivot=(0, -0.5, 0), size=(9, 14, 13), mat=BARK, paint=p_bracer,
         mirror=True),
    dict(name="R-BracerPlate", bone="R-Forearm", pivot=(-5.0, -0.5, 0), rot=(0, 0, 6), size=(2, 12, 10),
         mat=BARK, paint=p_bracer_plate, skip=("right",), mirror=True),
    dict(name="R-Glove", bone="R-Hand", pivot=(0, -0.2, 0), size=(11, 12, 15), stretch=(1, 1.02, 1), mat=BARK,
         paint=p_glove, skip=("top",), mirror=True),
    dict(name="R-GloveCuff", bone="R-Hand", pivot=(0, 5.6, 0), size=(12, 2, 16), mat=ROPE, paint=p_cuff,
         mirror=True),
]


# ================================================================== LEGS: moss trousers, bark greaves, bark boots
def cloth_folds(F, pitch=4, seed=0):
    mottle(F, scale=8, amp=0.035, seed=21 + seed)
    if F.is_side():
        coord = _horiz(F)
        ph = np.sin(2 * math.pi * coord / pitch + seed)
        F.val += 0.05 * np.round(ph * 1.5) / 1.5


def p_breeches(F):
    cloth_folds(F, 4, seed=6)
    if F.is_side():
        F.val[F.v < 2] -= 0.08              # under the belt


def p_trouser(F):
    cloth_folds(F, 4, seed=7)
    if F.is_side():
        # patched knee-side + stitched seam on the outer leg
        if F.face == "left":
            stitches(F, np.abs(F.lz) < 0.5, period=2)


def p_knee(F):
    bark_base(F, seed=24)
    if F.face == "front":
        cut_rim(F, "top")
        tatter(F, depth=1, seed=24)
        cu, cv = _uv_of(F, (0, 0, 0))
        rivet(F, cu, cv, WOOD)


def p_greave(F):
    bark_base(F, seed=25)
    if F.is_side():
        jag_plates(F, F.ly > -8.0, 5.0, depth=2, seed=25)
        cut_rim(F, "top")
        rope_band(F, 6.0, 8.0)
        rope_band(F, -7.5, -5.5)
        if F.face == "back":
            lace = (np.abs(np.abs(F.lx) - ((F.iv % 4) * 0.5)) < 0.5) & (np.abs(F.lx) < 2.1) & (F.ly > -5.0)
            F.mat[lace] = ROPE
            F.val[lace] = 0.0


def p_boot(F):
    bark_base(F, seed=26, depth=0.8)
    F.val -= 0.03
    if F.is_side():
        sole = F.ly < -2.6
        F.mat[sole] = WOOD
        F.val[sole] -= 0.22
        F.val[sole & (F.ly > -3.6)] += 0.08
        if F.face == "front":
            cap = (F.ly > -2.6) & (F.ly < 1.5) & (np.abs(F.lx) < 5.6)
            stamp(F, cap, BARK, hl=0.14, lo=0.12, shadow=0.16, add=0.05)
        if F.face in ("left", "right"):
            wrap = (np.abs(F.lz + 3.0) < 1.6) & (F.ly > -2.6)
            rope_band(F, -99, 99) if False else None
            stamp(F, wrap, ROPE, hl=0.12, lo=0.12, shadow=0.16)
            F.val[wrap & (((F.iu + F.iv) % 3) == 0)] -= 0.15
    elif F.face == "top":
        wrap = np.abs(F.lz + 3.0) < 1.6
        stamp(F, wrap, ROPE, hl=0.12, lo=0.12, shadow=0.14)
        F.val[wrap & (((F.iu + F.iv) % 3) == 0)] -= 0.15
        F.val[F.lz < -6.5] -= 0.05
    elif F.face == "bottom":
        F.mat[:] = WOOD
        F.val -= 0.3


def p_bootwrap(F):
    twist(F, ROPE, 3)
    if F.is_side():
        F.val[F.v < 1] += 0.05


LEGS = [
    dict(name="Breeches", bone="Pelvis", pivot=(0, 0, 0.2), size=(26, 12, 20), stretch=(1, 1.04, 0.98), mat=CLOTH,
         paint=p_breeches, skip=("top",)),
    dict(name="R-Trouser", bone="R-Thigh", pivot=(0.2, -0.5, 0), size=(11, 21, 14), mat=CLOTH,
         paint=p_trouser, skip=("top", "bottom"), double=True, mirror=True),
    dict(name="R-Knee", bone="R-Calf", pivot=(0, 9.6, 6.9), size=(8, 6, 2), mat=BARK,
         paint=p_knee, skip=("back",), mirror=True),
    dict(name="R-Greave", bone="R-Calf", pivot=(0, 2.5, 0.1), size=(11, 23, 13), mat=BARK,
         paint=p_greave, skip=("bottom",), mirror=True),
    dict(name="R-Boot", bone="R-Foot", pivot=(0, 0.0, 0.3), size=(14, 8, 20), mat=BARK,
         paint=p_boot, mirror=True),
]

PIECES = {"Head": HEAD, "Chest": CHEST, "Hands": HANDS, "Legs": LEGS}
