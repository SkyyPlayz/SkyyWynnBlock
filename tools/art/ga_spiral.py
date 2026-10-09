"""SkyWynn Foraging armor - F4 Northern - SPIRAL set (v1). ORIGINAL; no vanilla or Armory pixels.

Started from the IN-GAME Spiral wood: hues / values sampled from the game's Spiral log and leaves (item icons); our own pixels.
Pale mint-grey bark CRACKLED into irregular plates (thin dark crack lines), pale aqua heartwood, the game's frosty aqua
curling leaves, deep steel-blue cloth.
Plate shape: CURL plates - each plate's lower edge rolls in soft waves; hooked curl crown points.
Mark: a pale aqua SPIRAL swirl on the belt and at the temple.
All tier-4 upgrades come from ga_f4.py (identical for every F4 tree), on top of the tier-2 / tier-3 ones.
"""
import numpy as np
import ga_paint as P
from ga_paint import SPIRAL, SPIRDK, SPIRLEAF, SPIRWOOD, STEEL, hash2, stamp
from ga_oak import _horiz
import ga_f2 as F2
import ga_f4 as F4

TIER, TREE = F4.TIER, "Spiral"
BARK, DK, LEAF, WOOD, CLOTH = SPIRAL, SPIRDK, SPIRLEAF, SPIRWOOD, STEEL
ME = __import__(__name__)

def base(F, seed=0, scars=True):
    """spiral bark: pale, crackled into irregular staggered plates with thin dark cracks and a lit upper edge."""
    m0 = F.mat == BARK
    h = _horiz(F)
    rv = np.floor((F.y + 2.0 * np.sin(h * 0.5 + seed)) / 5.0).astype(np.int64)
    cu = np.floor((h + rv * 2.3) / 5.0).astype(np.int64)
    F.val[m0] += (0.08 * (hash2(cu, rv, seed + 141) - 0.5))[m0]
    if F.is_side() and scars:
        yy = (F.y + 2.0 * np.sin(h * 0.5 + seed)) / 5.0 - rv
        xx = (h + rv * 2.3) / 5.0 - cu
        crack = ((yy < 0.2) | (xx < 0.2)) & m0
        F.mat[crack] = DK
        F.val[crack] = 0.55
        F.val[(yy > 0.2) & (yy < 0.4) & m0 & ~crack] += 0.06


PROF_STEP, PROF_MAX = 8.0, 3.0


def PROF(hc, step):
    return 1.5 * (1 + np.sin(2 * np.pi * hc / step))


LEAF_MASK = [
    ".LL..L.",
    "L..L.L.",
    "L.L..LL",
    ".L.L..L",
    "...LLL.",
    "..LsL..",
    ".L.s...",
    "...s...",
    "...s...",
    "...s...",
]
MARK_MASK = [
    "..SSSSS..",
    ".S.....S.",
    "S..SSS..S",
    "S.S...S.S",
    "S.S.S.S.S",
    "S.S..SS.S",
    "S..S....S",
    ".S..SSSS.",
    "..S......",
    "...SSSSS.",
]
COL = {"L": (SPIRLEAF, 0.06), "l": (SPIRLEAF, -0.1), "s": (SPIRDK, 0.5)}
MARK_COL = {"S": (SPIRLEAF, 0.12)}
MARK_SIZE = (9, 10)
CROWN_MASK = [
    ".XXXX..",
    "X....X.",
    "X..X.X.",
    "X.XX.X.",
    ".XXXX..",
    "..XXX..",
    "..XXX..",
    "..XXX..",
    "..XXX..",
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
MARK_HEAD = [dict(name="L-HelmSpiral", bone="Head", pivot=(17.0, 9.0, 4.0), rot=(0, 90, 0), size=MARK_SIZE, mat=LEAF,
                  paint=p_mark, double=True)]
MARK_CHEST = [dict(name="SpiralBadge", bone="Belly", pivot=(0, -4.0, 12.15), size=MARK_SIZE, mat=LEAF, paint=p_mark,
                   double=True)]

PIECES = F4.build(ME)
