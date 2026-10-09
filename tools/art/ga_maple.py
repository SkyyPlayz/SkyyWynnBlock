"""SkyWynn Foraging armor - F2 Autumn - MAPLE set (v1). ORIGINAL; no vanilla or Armory pixels.

Started from the IN-GAME (Crimson) Maple wood: hues / values sampled from the game's Maple trunk, log end, redwood planks,
crimson maple leaves and maple seeds; our own pixels. Mauve-brown bark with long vertical fibres and dark cracks, peach
heartwood with rings, the game's crimson maple leaves, tan-and-red maple seed pairs, mustard cloth (autumn).
Plate shape vs the F1 trees: LOBED plates - every plate edge is cut into maple-leaf lobes (one big middle point between two
smaller side points); maple-leaf crown points. Mark: a crimson MAPLE LEAF on the knot-boss belt clasp with a SAMARA PAIR
(the double-winged "helicopter" seed) hanging under it, and a samara pair at the helmet temple.
All tier-2 upgrades come from ga_f2.py (identical for every F2 tree).
"""
import numpy as np
import ga_paint as P
from ga_paint import MAPLE, MAPLEDK, MLEAF, MWOOD, MSEED, MUSTARD, hash2, stamp
from ga_oak import _horiz, _side_cut
import ga_f2 as F2

TIER, TREE = F2.TIER, "Maple"
BARK, DK, LEAF, WOOD, CLOTH = MAPLE, MAPLEDK, MLEAF, MWOOD, MUSTARD


def base(F, seed=0, scars=True):
    """maple bark: long vertical fibre streaks, a few long dark wavy cracks with a lit left lip."""
    m0 = F.mat == BARK
    n2 = P.vnoise(F.W, 9.0, 140 + seed)
    F.val[m0] += 0.04 * np.round((n2[m0] - 0.5) * 3)
    h = _horiz(F)
    col = np.floor(h).astype(np.int64)
    fib = hash2(col, np.floor(F.y / 5).astype(np.int64), seed + 41) - 0.5
    F.val[m0] += 0.06 * np.round(fib[m0] * 2) / 2
    if F.is_side() and scars:
        wav = h + 0.9 * np.sin(F.y * 0.35 + seed)
        c = np.floor(wav / 5.0).astype(np.int64)
        f = wav / 5.0 - np.floor(wav / 5.0)
        seg = np.floor(F.y / 7.0).astype(np.int64)
        on = hash2(c, seg, seed + 43) < 0.45
        crack = on & (f < 0.2) & m0
        F.mat[crack] = DK
        F.val[crack] = 0.15
        lip = on & (f >= 0.2) & (f < 0.4) & m0
        F.val[lip] += 0.08


def _lobe(hc, step):
    """maple-leaf lobe profile over one plate width (0..2.6): a broad big middle point, two smaller side points,
    narrow notches between them."""
    x = hc / step                                            # 0..1
    big = np.clip(1 - np.abs(x - 0.5) / 0.26, 0, 1) * 2.6
    small = np.clip(1 - np.abs(np.abs(x - 0.5) - 0.34) / 0.14, 0, 1) * 1.5
    return np.maximum(big, small)


def plates(F, region, pitch, seed=0, y_top=None, step=10.0):
    """overlapping plates whose lower edges are cut into maple-leaf lobes (dark shadow line under each lobed edge,
    gentle bevel above it, each plate its own tone)."""
    region = np.asarray(region, bool) & F.alpha
    if not region.any():
        return
    if y_top is None:
        y_top = F.y[region].max() + 1e-3
    h = _horiz(F)
    row0 = np.floor((y_top - F.y) / pitch).astype(np.int64)
    off = np.where(row0 % 2 == 0, 0.0, step / 2.0)
    hc = np.mod(h + off, step)
    s_ = (y_top - F.y - _lobe(hc, step)) / pitch
    k = np.floor(s_); f = s_ - k
    ki = k.astype(np.int64)
    plate = np.floor((h + np.where(ki % 2 == 0, 0.0, step / 2.0)) / step).astype(np.int64)
    F.val[region] += ((hash2(plate, ki, seed + 3) - 0.5) * 0.10)[region] + 0.04 * (0.5 - f[region])
    dv, du = P.face_down(F)
    kd = np.roll(k, (-dv, -du), axis=(0, 1))              # the plate row of the texel just below
    under = region & (kd > k) & (k >= 0)
    F.mat[under] = DK
    F.val[under] = -0.05
    ku = np.roll(k, (dv, du), axis=(0, 1))
    bev = region & (ku < k) & (k > 0)
    F.mat[bev & (F.mat == DK)] = BARK
    F.val[bev] += 0.12


def hem(F, seed=0, clip=2, step=10.0):
    """lobed hem: the bottom edge is cut into maple-leaf lobes, pale cut end-grain line along it."""
    if F.face not in ("front", "back", "left", "right"):
        return
    d = F.fh - F.v
    if F.face in ("front", "back") and clip:
        depth = 2.6 - _lobe(np.mod(F.u, step), step)          # 0 at the points, 2.6 at the notches
        F.alpha &= ~(d < depth)
        dd = d - depth
    else:
        dd = d
    m = (dd >= 0) & (dd < 1) & F.alpha
    F.mat[m] = WOOD
    F.val[m] -= 0.06


MAPLE_LEAF_MASK = [          # maple leaf: 3 big lobes + 2 small lower lobes, stem at the bottom (L leaf, l shade, v vein, s stem)
    ".....L.....",
    "....LLl....",
    ".L..LLl..L.",
    ".LL.LvL.Ll.",
    "LLLLLvLLLll",
    ".LLvLvLvLl.",
    "..LLvvvLl..",
    ".LLLLvLLll.",
    "LL..LvL..ll",
    ".....s.....",
    ".....s.....",
]
SAMARA_PAIR_MASK = [         # maple seed pair: two red seeds joined at the top, tan wings spreading down in a V
    "....ss....",
    "...dddd...",
    "..dd..dd..",
    ".WWw..wWW.",
    "WWw....wWW",
    "WW......WW",
    "Ww......wW",
    "W........W",
]
LEAF_COL = {"L": (MLEAF, 0.06), "l": (MLEAF, -0.08), "v": (MLEAF, -0.16), "s": (MAPLEDK, 0.7)}
SEED_COL = {"s": (MAPLEDK, 0.7), "d": (MLEAF, -0.1), "W": (MSEED, 0.06), "w": (MSEED, -0.08)}


def p_leaf(F):
    F2._mask_paint(F, MAPLE_LEAF_MASK, LEAF_COL)


def p_leaf_hang(F):
    F2._mask_paint(F, MAPLE_LEAF_MASK, LEAF_COL, flip_v=True)


def p_samara_pair(F):
    F2._mask_paint(F, SAMARA_PAIR_MASK, SEED_COL)


def leaflet(F, cu, cv):
    m = (np.abs(F.u - cu) < 1.01) & (np.abs(F.v - cv) < 0.61)
    m |= (np.abs(F.u - cu) < 0.51) & (np.abs(F.v - cv) < 1.11)
    stamp(F, m, MLEAF, hl=0.2, lo=0.1, shadow=0.12, add=0.05)


CROWN_MID_MASK = [           # maple-leaf crown point (top lobe + two side spurs)
    "...X...",
    "..XXX..",
    "..XXX..",
    "X.XXX.X",
    "XXXXXXX",
    ".XXXXX.",
    ".XXXXX.",
    "..XXX..",
    "..XXX..",
    "..XXX..",
    "..XXX..",
    "..XXX..",
    "..XXX..",
    "..XXX..",
    "..XXX..",
]


def _crown(F, seed):
    base(F, seed=seed, scars=False)
    if F.face in ("front", "back"):
        H, W = len(CROWN_MID_MASK), len(CROWN_MID_MASK[0])
        iv = np.clip((F.v / F.fh * H).astype(int), 0, H - 1)
        iu = np.clip((F.u / F.fw * W).astype(int), 0, W - 1)
        ch = np.array([list(r) for r in CROWN_MID_MASK])[iv, iu]
        F.alpha &= ch == "X"
        a = F.alpha
        e = a & ~(P._shift(a, 0, 1) & P._shift(a, 0, -1))
        F.val[e] -= 0.16
        F.val[np.abs(F.lx) < 0.5] += 0.1
    else:
        _side_cut(F, F.fh * 0.6)


def crown_mid(F):
    _crown(F, 7)


def crown_side(F):
    _crown(F, 8)


CROWN_MID_SIZE, CROWN_MID_PIVOT = (7, 15, 2), (0, 18.5, 15.25)
CROWN_SIDE_SIZE, CROWN_SIDE_PIVOT, CROWN_SIDE_ROT = (7, 12, 2), (-9.0, 16.5, 14.75), (0, 0, 14)
LEAF_SIZE, LEAF_SIZE_SMALL = (9, 9), (7, 7)

MARK_HEAD = [
    dict(name="L-HelmSamaras", bone="Head", pivot=(17.0, 5.0, 4.0), rot=(0, 90, 0), size=(10, 8), offset=(0, -4.0, 0),
         mat=MSEED, paint=p_samara_pair, double=True),
]
MARK_CHEST = [
    # big crimson maple leaf on the knot boss, a samara pair hanging under it
    dict(name="MapleBadge", bone="Belly", pivot=(0, -5.8, 12.15), size=(11, 11), offset=(0, 0, 0), mat=MLEAF,
         paint=p_leaf, double=True),
    dict(name="SamaraPair", bone="Belly", pivot=(0, -10.8, 12.4), rot=(6, 0, 0), size=(10, 8), offset=(0, -4.0, 0),
         mat=MSEED, paint=p_samara_pair, double=True),
]

PIECES = F2.build(__import__(__name__))
