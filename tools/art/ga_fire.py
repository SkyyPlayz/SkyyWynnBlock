"""SkyWynn Foraging armor - F5 Wastes - FIRE set (v1). ORIGINAL; no vanilla or Armory pixels.

Started from the IN-GAME Fire wood: every colour sampled from the game's own Fire log side / log top / leaves textures in
Assets.zip (our own pixels): dark red-black cracked bark with glowing lava cracks, glowing red heartwood, charred twigs, charcoal cloth.
FLAME-TONGUE plates (curved pointed flames), flame crown points. Mark: a FIRE FLAME.
All tier-5 upgrades come from ga_f5.py (identical for every F5 tree), on top of the tier-2 / 3 / 4 ones.
"""
import numpy as np
import ga_paint as P
from ga_paint import FIRE_BARK, FIRE_DK, FIRE_LEAF, FIRE_WOOD, FIRE_CLOTH, FIRE_GEM, hash2, stamp
from ga_oak import _horiz
import ga_f2 as F2
import ga_f5 as F5

TIER, TREE = F5.TIER, "Fire"
BARK, DK, LEAF, WOOD, CLOTH, GEM = FIRE_BARK, FIRE_DK, FIRE_LEAF, FIRE_WOOD, FIRE_CLOTH, FIRE_GEM
ME = __import__(__name__)


def base(F, seed=0, scars=True):
    """crack bark."""
    m0 = F.mat == BARK
    h = _horiz(F)
    rw = np.floor(F.y / 8).astype(np.int64)
    hh = h + hash2(rw, rw * 3, seed + 7) * 7
    cl = np.floor(hh / 7).astype(np.int64)
    F.val[m0] += ((0.1 * (hash2(cl, rw, seed + 11) - 0.5)))[m0]
    fy = F.y / 8 - np.floor(F.y / 8)
    fx = hh / 7 - np.floor(hh / 7)
    if F.is_side() and scars:
        hz = hash2(cl, rw, seed + 13) < 0.55
        crack = m0 & (((fy < 1.0 / 8) & hz) | (fx < 1.0 / 7))
        F.mat[crack] = DK
        F.val[crack] = 0.3
        glow = crack & (hash2(cl, rw, seed + 17) < 0.6)
        F.mat[glow] = GEM
        F.val[glow] = -0.05
        if True:
            F.lockval[glow] = True
        lit = m0 & ~crack & (fy >= 1.0 / 8) & (fy < 2.0 / 8)
        F.val[lit] += 0.07


PROF_STEP, PROF_MAX = 5.0, 3.5


def PROF(hc, step):
    return PROF_MAX * (1 - np.abs(2 * hc / step - 1)) ** 2


def plates(F, region, pitch, seed=0, y_top=None):
    F5.profile_plates(F, region, pitch, seed, PROF, PROF_STEP, ME, y_top)


def hem(F, seed=0, clip=2):
    F5.profile_hem(F, seed, clip, PROF, PROF_STEP, ME, PROF_MAX)


LEAF_MASK = [
    "...e...",
    "..eEe..",
    ".eEsEe.",
    "..sss..",
    ".s.s.s.",
    "s..s..s",
    "...s...",
    "...s...",
]
MARK_MASK = [
    "....e....",
    "...eE....",
    "...eEe...",
    "..eEEe.e.",
    "..eEgEeE.",
    ".eEggEEe.",
    ".eEgggEe.",
    "..eEgEe..",
    "...sss...",
]
COL = {"s": (LEAF, 0.1), "e": (GEM, -0.15), "E": (GEM, 0.05)}
MARK_COL = {"e": (GEM, -0.2), "E": (GEM, 0.05), "g": (GEM, 0.3), "s": (DK, 0.5)}


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
    "...XX..",
    "..XXX..",
    "..XXX.X",
    ".XXXXXX",
    ".XXXXX.",
    "XXXXXXX",
    "XXXXXXX",
    "XXXXXXX",
    ".XXXXX.",
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
MARK_CHEST = [dict(name="FireBadge", bone="Belly", pivot=(0, -4.0, 12.15), size=(9, 9), mat=WOOD, paint=p_mark,
                   double=True)]

PIECES = F5.build(ME)
