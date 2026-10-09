"""SkyWynn Foraging armor - F4 Northern - FIR set (v1). ORIGINAL; no vanilla or Armory pixels.

Started from the IN-GAME Fir wood: hues / values sampled from the game's Fir log and leaves (item icons); our own pixels.
Very dark brown bark broken into small rough FLAKES (dark gaps between them), pale tan heartwood, deep green needles,
oatmeal wool cloth (northern).
Plate shape: FIR-TIER plates - each plate's lower edge is a wide shallow V with a sharp point in the middle (like a fir's
branch tiers); stacked fir-tree crown points. Mark: a little FIR TREE (three needle tiers on a short trunk).
All tier-4 upgrades come from ga_f4.py (identical for every F4 tree), on top of the tier-2 / tier-3 ones.
"""
import numpy as np
import ga_paint as P
from ga_paint import FIR, FIRDK, FIRLEAF, FIRWOOD, WOOL, hash2, stamp
from ga_oak import _horiz
import ga_f2 as F2
import ga_f4 as F4

TIER, TREE = F4.TIER, "Fir"
BARK, DK, LEAF, WOOD, CLOTH = FIR, FIRDK, FIRLEAF, FIRWOOD, WOOL
ME = __import__(__name__)

def base(F, seed=0, scars=True):
    """fir bark: dark rough flakes (3 x 4 cells, staggered, each its own tone) with dark gaps."""
    m0 = F.mat == BARK
    h = _horiz(F)
    rv = np.floor(F.y / 4.0).astype(np.int64)
    cu = np.floor((h + (rv % 2) * 1.5) / 3.0).astype(np.int64)
    F.val[m0] += (0.12 * (hash2(cu, rv, seed + 111) - 0.5))[m0]
    n2 = P.vnoise(F.W, 8.0, 210 + seed)
    F.val[m0] += 0.03 * np.round((n2[m0] - 0.5) * 3)
    if F.is_side() and scars:
        fu = (h + (rv % 2) * 1.5) / 3.0 - cu
        fv = F.y / 4.0 - rv
        gap = ((fu < 0.3) | (fv < 0.22)) & m0 & (hash2(cu, rv, seed + 113) < 0.75)
        F.mat[gap] = DK
        F.val[gap] = 0.5
        F.val[(fv > 0.75) & m0 & ~gap] += 0.06


PROF_STEP, PROF_MAX = 8.0, 3.0


def PROF(hc, step):
    x = hc / step
    v = (1 - np.abs(2 * x - 1)) * 1.8
    spike = np.clip(1 - np.abs(x - 0.5) / 0.12, 0, 1) * PROF_MAX
    return np.maximum(v, spike)


LEAF_MASK = [
    "...L...",
    "L.LLL.l",
    ".LLsLl.",
    "L.LsL.l",
    ".LLsLl.",
    "L.LsL.l",
    ".LLsLl.",
    "...s...",
    "...s...",
    "...s...",
]
MARK_MASK = [
    "....L....",
    "...LLl...",
    "..LLLll..",
    "...LLl...",
    "..LLLll..",
    ".LLLLlll.",
    "...LLl...",
    ".LLLLlll.",
    "LLLLLllll",
    "....w....",
    "....w....",
]
COL = {"L": (FIRLEAF, 0.08), "l": (FIRLEAF, -0.1), "s": (FIRDK, 0.6)}
MARK_COL = {"L": (FIRLEAF, 0.1), "l": (FIRLEAF, -0.08), "w": (FIRWOOD, -0.05)}
MARK_SIZE = (9, 11)
CROWN_MASK = [
    "...X...",
    "..XXX..",
    ".XXXXX.",
    "..XXX..",
    ".XXXXX.",
    "XXXXXXX",
    "..XXX..",
    ".XXXXX.",
    "XXXXXXX",
    "..XXX..",
    "..XXX..",
    "..XXX..",
    "..XXX..",
    "..XXX..",
    "..XXX..",
]

def plates(F, region, pitch, seed=0, y_top=None):
    F4.profile_plates(F, region, pitch, seed, PROF, PROF_STEP, ME, y_top)


def hem(F, seed=0, clip=2):
    F4.profile_hem(F, seed, clip, PROF, PROF_STEP, ME, PROF_MAX)


def p_leaf(F):
    F2._mask_paint(F, LEAF_MASK, COL)


def p_leaf_hang(F):
    F2._mask_paint(F, LEAF_MASK, COL, flip_v=True)


def p_mark(F):
    F2._mask_paint(F, MARK_MASK, MARK_COL)


def leaflet(F, cu, cv):
    m = (np.abs(F.u - cu) < 0.51) & (np.abs(F.v - cv) < 1.11)
    m |= (np.abs(F.u - cu) < 1.01) & (np.abs(F.v - cv - 0.5) < 0.51)
    stamp(F, m, LEAF, hl=0.2, lo=0.1, shadow=0.12, add=0.05)


def crown_mid(F):
    F4.mask_crown(F, CROWN_MASK, ME, 7)


def crown_side(F):
    F4.mask_crown(F, CROWN_MASK, ME, 8)


CROWN_MID_SIZE, CROWN_MID_PIVOT = (7, 15, 2), (0, 18.5, 15.25)
CROWN_SIDE_SIZE, CROWN_SIDE_PIVOT, CROWN_SIDE_ROT = (7, 12, 2), (-9.0, 16.5, 14.75), (0, 0, 14)
LEAF_SIZE, LEAF_SIZE_SMALL = (7, 10), (6, 8)
MARK_HEAD = [dict(name="L-HelmFir", bone="Head", pivot=(17.0, 9.0, 4.0), rot=(0, 90, 0), size=MARK_SIZE, mat=LEAF,
                  paint=p_mark, double=True)]
MARK_CHEST = [dict(name="FirBadge", bone="Belly", pivot=(0, -4.0, 12.15), size=MARK_SIZE, mat=LEAF, paint=p_mark,
                   double=True)]

PIECES = F4.build(ME)
