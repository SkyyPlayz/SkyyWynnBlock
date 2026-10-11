"""SkyWynn Foraging armor - F5 Wastes - BAMBOO set (v1). ORIGINAL; no vanilla or Armory pixels.

Started from the IN-GAME Bamboo wood: every colour sampled from the game's own Bamboo log side / log top / leaves textures in
Assets.zip (our own pixels): lime-green bamboo bark with pale node bands, green heartwood, yellow-green blade leaves, deep jade cloth.
NODE plates (straight edges with small V notches like bamboo joints), segmented-cane crown points. Mark: a BAMBOO SHOOT
with two blades.
All tier-5 upgrades come from ga_f5.py (identical for every F5 tree), on top of the tier-2 / 3 / 4 ones.
"""
import numpy as np
import ga_paint as P
from ga_paint import BAM_BARK, BAM_DK, BAM_LEAF, BAM_WOOD, BAM_CLOTH, BAM_GEM, hash2, stamp
from ga_oak import _horiz
import ga_f2 as F2
import ga_f5 as F5

TIER, TREE = F5.TIER, "Bamboo"
BARK, DK, LEAF, WOOD, CLOTH, GEM = BAM_BARK, BAM_DK, BAM_LEAF, BAM_WOOD, BAM_CLOTH, BAM_GEM
ME = __import__(__name__)


def base(F, seed=0, scars=True):
    """nodes bark."""
    m0 = F.mat == BARK
    h = _horiz(F)
    st = hash2(np.floor(h / 2).astype(np.int64), 0 * np.floor(h).astype(np.int64), seed + 5) - 0.5
    F.val[m0] += (0.05 * np.round(st * 2))[m0]
    if F.is_side() and scars:
        fy = np.mod(F.y + 3.0, 10.0)
        F.val[m0 & (fy < 1.0)] += 0.16
        F.mat[m0 & (fy >= 1.0) & (fy < 2.0)] = DK
        F.val[m0 & (fy >= 1.0) & (fy < 2.0)] = 0.5
        F.val[m0 & (fy >= 2.0) & (fy < 4.0)] -= 0.05


PROF_STEP, PROF_MAX = 6.0, 2.5


def PROF(hc, step):
    return PROF_MAX * np.minimum(1.0, np.abs(hc - step / 2.0) / 1.2)


def plates(F, region, pitch, seed=0, y_top=None):
    F5.profile_plates(F, region, pitch, seed, PROF, PROF_STEP, ME, y_top)


def hem(F, seed=0, clip=2):
    F5.profile_hem(F, seed, clip, PROF, PROF_STEP, ME, PROF_MAX)


LEAF_MASK = [
    "...L",
    "..LL",
    "..Ll",
    ".Ll.",
    ".Ll.",
    "Ll..",
    "Ll..",
    "l...",
    "s...",
    "s...",
]
MARK_MASK = [
    "..L...L..",
    ".Ll...lL.",
    "Ll.....lL",
    "...sss...",
    "...SSS...",
    "...sss...",
    "...SSS...",
    "...sss...",
    "...SSS...",
]
COL = {"L": (LEAF, 0.08), "l": (LEAF, -0.1), "s": (BARK, 0.0)}
MARK_COL = {"L": (LEAF, 0.08), "l": (LEAF, -0.1), "s": (BARK, -0.12), "S": (BARK, 0.1)}


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
    ".X.X.X.",
    "..XXX..",
    "..XXX..",
    "..XXX..",
    ".XXXXX.",
    "..XXX..",
    "..XXX..",
    "..XXX..",
    ".XXXXX.",
    "..XXX..",
    "..XXX..",
    "..XXX..",
    ".XXXXX.",
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
MARK_CHEST = [dict(name="BambooBadge", bone="Belly", pivot=(0, -4.0, 12.15), size=(9, 9), mat=WOOD, paint=p_mark,
                   double=True)]

PIECES = F5.build(ME)
