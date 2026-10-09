"""SkyWynn Foraging armor - F5 Wastes - BANYAN set (v1). ORIGINAL; no vanilla or Armory pixels.

Started from the IN-GAME Banyan wood: every colour sampled from the game's own Banyan log side / log top / leaves textures in
Assets.zip (our own pixels): warm brown bark with long vertical root ridges, tan heartwood, deep green leaves, terracotta cloth.
ROOT-DRIP plates (rounded drips like hanging roots), root-pillar crown points. Mark: a BANYAN TREE with hanging roots.
All tier-5 upgrades come from ga_f5.py (identical for every F5 tree), on top of the tier-2 / 3 / 4 ones.
"""
import numpy as np
import ga_paint as P
from ga_paint import BAN_BARK, BAN_DK, BAN_LEAF, BAN_WOOD, BAN_CLOTH, BAN_GEM, hash2, stamp
from ga_oak import _horiz
import ga_f2 as F2
import ga_f5 as F5

TIER, TREE = F5.TIER, "Banyan"
BARK, DK, LEAF, WOOD, CLOTH, GEM = BAN_BARK, BAN_DK, BAN_LEAF, BAN_WOOD, BAN_CLOTH, BAN_GEM
ME = __import__(__name__)


def base(F, seed=0, scars=True):
    """fibre bark."""
    m0 = F.mat == BARK
    h = _horiz(F)
    col = np.floor(h / 2).astype(np.int64)
    fib = hash2(col, np.floor((F.y + col * 1.7) / 14).astype(np.int64), seed + 101) - 0.5
    F.val[m0] += 0.1 * np.round(fib[m0] * 2) / 2
    n2 = P.vnoise(F.W, 9.0, 200 + seed)
    F.val[m0] += 0.03 * np.round((n2[m0] - 0.5) * 3)
    if F.is_side() and scars:
        c = np.floor(h / 5).astype(np.int64)
        f = h / 5 - np.floor(h / 5)
        seg = np.floor(F.y / 20).astype(np.int64)
        on = hash2(c, seg, seed + 103) < 0.6
        F.mat[on & (f < 0.25) & m0] = DK
        F.val[on & (f < 0.25) & m0] = 0.35
        F.val[on & (f >= 0.25) & (f < 0.5) & m0] += 0.08


PROF_STEP, PROF_MAX = 6.0, 3.5


def PROF(hc, step):
    return PROF_MAX * np.clip(1 - (2 * hc / step - 1) ** 2, 0, 1) ** 4


def plates(F, region, pitch, seed=0, y_top=None):
    F5.profile_plates(F, region, pitch, seed, PROF, PROF_STEP, ME, y_top)


def hem(F, seed=0, clip=2):
    F5.profile_hem(F, seed, clip, PROF, PROF_STEP, ME, PROF_MAX)


LEAF_MASK = [
    "..L..",
    ".LLL.",
    "LLLLL",
    "LlLlL",
    "LLlLL",
    ".LlLl",
    "..l..",
    "..s..",
]
MARK_MASK = [
    ".sss.sss.",
    "s.s.s.s.s",
    "s..sss..s",
    "s..sSs..s",
    "...sSs...",
    "...sSs...",
    "..ssSss..",
    ".s.sSs.s.",
    "s..s.s..s",
]
COL = {"L": (LEAF, 0.08), "l": (LEAF, -0.1), "s": (DK, 0.6)}
MARK_COL = {"s": (LEAF, 0.0), "S": (BARK, 0.05)}


def p_leaf(F):
    F2._mask_paint(F, LEAF_MASK, COL)


def p_leaf_hang(F):
    F2._mask_paint(F, LEAF_MASK, COL, flip_v=True)


def p_mark(F):
    F2._mask_paint(F, MARK_MASK, MARK_COL)
    F.lockval[F.alpha & (F.mat == GEM)] = True


def leaflet(F, cu, cv):
    m = (np.abs(F.u - cu) < 0.51) & (np.abs(F.v - cv) < 1.11)
    m |= (np.abs(F.u - cu) < 1.51) & (np.abs(F.v - cv - 0.5) < 0.51) & ((F.iu % 2) == 0)
    stamp(F, m, LEAF, hl=0.2, lo=0.1, shadow=0.12, add=0.05)


CROWN_MASK = [
    "XXXXXXX",
    "XXXXXXX",
    ".XXXXX.",
    ".XXXXX.",
    "..XXX..",
    "..XXX..",
    "..XXX..",
    "..XXX..",
    "..XXX..",
    "..XXX..",
    ".XXXXX.",
    ".XX.XX.",
    ".XX.XX.",
    "XX...XX",
    "XX...XX",
    "X.....X",
]


def crown_mid(F):
    F5.mask_crown(F, CROWN_MASK, ME, 7)


def crown_side(F):
    F5.mask_crown(F, CROWN_MASK, ME, 8)


CROWN_MID_SIZE, CROWN_MID_PIVOT = (7, 19, 2), (0, 20.5, 15.25)          # F5: taller crown points
CROWN_SIDE_SIZE, CROWN_SIDE_PIVOT, CROWN_SIDE_ROT = (7, 15, 2), (-9.0, 18.0, 14.75), (0, 0, 14)
LEAF_SIZE, LEAF_SIZE_SMALL = (7, 10), (6, 8)
MARK_HEAD = [dict(name="L-HelmMark", bone="Head", pivot=(17.0, 9.0, 4.0), rot=(0, 90, 0), size=(9, 9), mat=LEAF,
                  paint=p_mark, double=True)]
MARK_CHEST = [dict(name="BanyanBadge", bone="Belly", pivot=(0, -4.0, 12.15), size=(9, 9), mat=WOOD, paint=p_mark,
                   double=True)]

PIECES = F5.build(ME)
