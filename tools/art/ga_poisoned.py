"""SkyWynn Foraging armor - F4 Northern - POISONED set (v1). ORIGINAL; no vanilla or Armory pixels.

Started from the IN-GAME Poisoned wood: hues / values sampled from the game's Poisoned log and leaves (item icons); our own pixels.
Near-black purple bark with deep cracks that show a SICKLY YELLOW-GREEN glow inside (the game's poisoned heartwood),
violet leaves, dark moss cloth.
Plate shape: BARBED plates - each plate's lower edge has a tall hooked barb and a small one; forked two-prong crown points.
Mark: a violet THORN LEAF dripping a yellow-green TOXIC DROP on the belt and at the temple.
All tier-4 upgrades come from ga_f4.py (identical for every F4 tree), on top of the tier-2 / tier-3 ones.
"""
import numpy as np
import ga_paint as P
from ga_paint import POISON, POISDK, POISLEAF, POISWOOD, MOSS, hash2, stamp
from ga_oak import _horiz
import ga_f2 as F2
import ga_f4 as F4

TIER, TREE = F4.TIER, "Poisoned"
BARK, DK, LEAF, WOOD, CLOTH = POISON, POISDK, POISLEAF, POISWOOD, MOSS
ME = __import__(__name__)

def base(F, seed=0, scars=True):
    """poisoned bark: dark purple, soft vertical streaks, a few deep cracks lit sickly yellow-green inside."""
    m0 = F.mat == BARK
    h = _horiz(F)
    col = np.floor(h / 2).astype(np.int64)
    F.val[m0] += (0.07 * (hash2(col, np.floor(F.y / 8).astype(np.int64), seed + 131) - 0.5))[m0]
    n2 = P.vnoise(F.W, 7.0, 230 + seed)
    F.val[m0] += 0.04 * np.round((n2[m0] - 0.5) * 3)
    if F.is_side() and scars:
        wav = h + 1.2 * np.sin(F.y * 0.4 + seed)
        c = np.floor(wav / 6.0).astype(np.int64)
        f = wav / 6.0 - c
        seg = np.floor(F.y / 8.0).astype(np.int64)
        on = (hash2(c, seg, seed + 133) < 0.3) & m0
        crack = on & (f < 0.2)
        F.mat[crack] = POISWOOD
        F.val[crack] = 0.05
        F.mat[on & (f >= 0.2) & (f < 0.34)] = DK
        F.val[on & (f >= 0.2) & (f < 0.34)] = 0.6


PROF_STEP, PROF_MAX = 7.0, 3.0


def PROF(hc, step):
    x = hc / step
    barb = np.where(x < 0.3, x / 0.3, np.clip(1 - (x - 0.3) / 0.12, 0, 1)) * PROF_MAX
    small = np.clip(1 - np.abs(x - 0.72) / 0.1, 0, 1) * 1.5
    return np.maximum(barb, small)


LEAF_MASK = [
    "L.....l",
    "LL...ll",
    ".LL.ll.",
    "LLLvlll",
    ".LLvll.",
    "..LvL..",
    "..LvL..",
    "...v...",
    "...s...",
    "...s...",
]
MARK_MASK = [
    "L......l",
    "LL....ll",
    ".LLv.ll.",
    "..LvLl..",
    "LLLvLlll",
    ".LLvlll.",
    "..Lvl...",
    "...v....",
    "...g....",
    "..ggg...",
    "..gGg...",
    "...g....",
]
COL = {"L": (POISLEAF, 0.08), "l": (POISLEAF, -0.12), "v": (POISDK, 0.7), "s": (POISDK, 0.7)}
MARK_COL = {"L": (POISLEAF, 0.1), "l": (POISLEAF, -0.1), "v": (POISDK, 0.7), "g": (POISWOOD, 0.1), "G": (POISWOOD, 0.4)}
MARK_SIZE = (8, 12)
CROWN_MASK = [
    "X.....X",
    "XX...XX",
    ".XX.XX.",
    ".XXXXX.",
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
MARK_HEAD = [dict(name="L-HelmPoisoned", bone="Head", pivot=(17.0, 9.0, 4.0), rot=(0, 90, 0), size=MARK_SIZE, mat=LEAF,
                  paint=p_mark, double=True)]
MARK_CHEST = [dict(name="PoisonedBadge", bone="Belly", pivot=(0, -4.0, 12.15), size=MARK_SIZE, mat=LEAF, paint=p_mark,
                   double=True)]

PIECES = F4.build(ME)
