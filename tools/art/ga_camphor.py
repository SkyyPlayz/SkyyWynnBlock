"""SkyWynn Foraging armor - F5 Wastes - CAMPHOR set (v1). ORIGINAL; no vanilla or Armory pixels.

Started from the IN-GAME Camphor wood: every colour sampled from the game's own Camphor log side / log top / leaves textures in
Assets.zip (our own pixels): pale grey camphor bark with soft patches and fine cracks, near-white heartwood, teal-green leaves, deep teal cloth.
SCALLOP plates (round bumps), stacked-cloud crown points. Mark: a camphor LEAF CLUSTER (teal leaf trio).
All tier-5 upgrades come from ga_f5.py (identical for every F5 tree), on top of the tier-2 / 3 / 4 ones.
"""
import numpy as np
import ga_paint as P
from ga_paint import CAM_BARK, CAM_DK, CAM_LEAF, CAM_WOOD, CAM_CLOTH, CAM_GEM, hash2, stamp
from ga_oak import _horiz
import ga_f2 as F2
import ga_f5 as F5

TIER, TREE = F5.TIER, "Camphor"
BARK, DK, LEAF, WOOD, CLOTH, GEM = CAM_BARK, CAM_DK, CAM_LEAF, CAM_WOOD, CAM_CLOTH, CAM_GEM
ME = __import__(__name__)


def base(F, seed=0, scars=True):
    """patch bark."""
    m0 = F.mat == BARK
    n = P.vnoise(F.W, 7.0, 300 + seed)
    F.val[m0] += 0.06 * np.round((n[m0] - 0.5) * 4) / 2
    if F.is_side() and scars:
        h = _horiz(F)
        n2 = P.vnoise(F.W, 4.0, 330 + seed)
        line = m0 & (np.abs(n2 - 0.5) < 0.025)
        F.mat[line] = DK
        F.val[line] = 0.6


PROF_STEP, PROF_MAX = 5.0, 2.5


def PROF(hc, step):
    return PROF_MAX * np.sqrt(np.clip(1 - (2 * hc / step - 1) ** 2, 0, 1))


def plates(F, region, pitch, seed=0, y_top=None):
    F5.profile_plates(F, region, pitch, seed, PROF, PROF_STEP, ME, y_top)


def hem(F, seed=0, clip=2):
    F5.profile_hem(F, seed, clip, PROF, PROF_STEP, ME, PROF_MAX)


LEAF_MASK = [
    "..L..",
    ".LLL.",
    "LLlLL",
    "LLlLl",
    ".Llll",
    "..l..",
    "..s..",
    "..s..",
]
MARK_MASK = [
    "..LL.LL..",
    ".LLLlLLL.",
    ".LlLlLlL.",
    "..LLlLL..",
    "...LlL...",
    "..LL.LL..",
    ".LlL.LlL.",
    "..L...L..",
    "....s....",
]
COL = {"L": (LEAF, 0.08), "l": (LEAF, -0.1), "s": (DK, 0.6)}
MARK_COL = {"L": (LEAF, 0.08), "l": (LEAF, -0.12), "s": (DK, 0.5)}


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
    "...X...",
    "..XXX..",
    ".XXXXX.",
    "..XXX..",
    ".XXXXX.",
    "XXXXXXX",
    ".XXXXX.",
    "..XXX..",
    ".XXXXX.",
    "XXXXXXX",
    "XXXXXXX",
    ".XXXXX.",
    "..XXX..",
    "..XXX..",
    "..XXX..",
    "..XXX..",
    "..XXX..",
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
MARK_CHEST = [dict(name="CamphorBadge", bone="Belly", pivot=(0, -4.0, 12.15), size=(9, 9), mat=WOOD, paint=p_mark,
                   double=True)]

PIECES = F5.build(ME)
