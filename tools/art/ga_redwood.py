"""SkyWynn Foraging armor - F4 Northern - REDWOOD set (v1). ORIGINAL; no vanilla or Armory pixels.

Started from the IN-GAME Redwood wood: hues / values sampled from the game's Redwood log, planks and leaves (item icons); our
own pixels. Rich red-brown STRINGY bark (many thin vertical fibres, a few deep furrows), salmon heartwood, dark green needles,
deep navy cloth.
Plate shape: SPIKE plates - each plate's lower edge is a row of narrow pointed teeth; tall spire crown points (the tallest tree).
Mark: a REDWOOD CONE with a needle sprig on the belt and at the temple.
All tier-4 upgrades come from ga_f4.py (identical for every F4 tree), on top of the tier-2 / tier-3 ones.
"""
import numpy as np
import ga_paint as P
from ga_paint import REDWOOD, REDDK, REDLEAF, REDWOOD_W, NAVY, hash2, stamp
from ga_oak import _horiz
import ga_f2 as F2
import ga_f4 as F4

TIER, TREE = F4.TIER, "Redwood"
BARK, DK, LEAF, WOOD, CLOTH = REDWOOD, REDDK, REDLEAF, REDWOOD_W, NAVY
ME = __import__(__name__)


def base(F, seed=0, scars=True):
    """stringy redwood bark: every column its own long fibre tone, some deep dark furrows with a lit left lip."""
    m0 = F.mat == BARK
    h = _horiz(F)
    col = np.floor(h).astype(np.int64)
    fib = hash2(col, np.floor((F.y + col * 1.7) / 9).astype(np.int64), seed + 101) - 0.5
    F.val[m0] += 0.09 * np.round(fib[m0] * 2) / 2
    n2 = P.vnoise(F.W, 9.0, 200 + seed)
    F.val[m0] += 0.03 * np.round((n2[m0] - 0.5) * 3)
    if F.is_side() and scars:
        c = np.floor(h / 4.0).astype(np.int64)
        f = h / 4.0 - np.floor(h / 4.0)
        seg = np.floor(F.y / 12.0).astype(np.int64)
        on = hash2(c, seg, seed + 103) < 0.4
        F.mat[on & (f < 0.25) & m0] = DK
        F.val[on & (f < 0.25) & m0] = 0.35
        F.val[on & (f >= 0.25) & (f < 0.5) & m0] += 0.08


PROF_STEP, PROF_MAX = 4.0, 3.0


def PROF(hc, step):
    return (1 - np.abs(2 * hc / step - 1)) * PROF_MAX


def plates(F, region, pitch, seed=0, y_top=None):
    F4.profile_plates(F, region, pitch, seed, PROF, PROF_STEP, ME, y_top)


def hem(F, seed=0, clip=2):
    F4.profile_hem(F, seed, clip, PROF, PROF_STEP, ME, PROF_MAX)


LEAF_MASK = [                # a flat needle spray (L lit, l shade, s twig)
    "L..L..L",
    ".L.L.L.",
    "L.LsL.l",
    ".L.s.l.",
    "LL.s.ll",
    ".LLsll.",
    "L.LsL.l",
    "..LsL..",
    "...s...",
    "...s...",
]
CONE_MASK = [                # the mark: a redwood cone (scaled oval) under a needle sprig
    "L.L.L.L.l",
    ".LLLsLll.",
    "...LsL...",
    "....s....",
    "...CCc...",
    "..CcCcc..",
    "..CCcCc..",
    "..CcCcc..",
    "..CCcCc..",
    "...Ccc...",
    "....c....",
]
COL = {"L": (REDLEAF, 0.08), "l": (REDLEAF, -0.1), "s": (REDDK, 0.6)}
CONE_COL = {"L": (REDLEAF, 0.08), "l": (REDLEAF, -0.1), "s": (REDDK, 0.6), "C": (REDWOOD_W, 0.04), "c": (REDWOOD_W, -0.18)}


def p_leaf(F):
    F2._mask_paint(F, LEAF_MASK, COL)


def p_leaf_hang(F):
    F2._mask_paint(F, LEAF_MASK, COL, flip_v=True)


def p_cone(F):
    F2._mask_paint(F, CONE_MASK, CONE_COL)


def leaflet(F, cu, cv):
    m = (np.abs(F.u - cu) < 0.51) & (np.abs(F.v - cv) < 1.11)
    m |= (np.abs(F.u - cu) < 1.51) & (np.abs(F.v - cv - 0.5) < 0.51) & ((F.iu % 2) == 0)
    stamp(F, m, REDLEAF, hl=0.2, lo=0.1, shadow=0.12, add=0.05)


CROWN_MASK = [               # a tall spire
    "...X...",
    "...X...",
    "..XXX..",
    "..XXX..",
    "..XXX..",
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


def crown_mid(F):
    F4.mask_crown(F, CROWN_MASK, ME, 7)


def crown_side(F):
    F4.mask_crown(F, CROWN_MASK, ME, 8)


CROWN_MID_SIZE, CROWN_MID_PIVOT = (7, 15, 2), (0, 18.5, 15.25)
CROWN_SIDE_SIZE, CROWN_SIDE_PIVOT, CROWN_SIDE_ROT = (7, 12, 2), (-9.0, 16.5, 14.75), (0, 0, 14)
LEAF_SIZE, LEAF_SIZE_SMALL = (7, 10), (6, 8)
MARK_HEAD = [dict(name="L-HelmCone", bone="Head", pivot=(17.0, 9.0, 4.0), rot=(0, 90, 0), size=(9, 11), mat=REDLEAF,
                  paint=p_cone, double=True)]
MARK_CHEST = [dict(name="RedwoodBadge", bone="Belly", pivot=(0, -4.0, 12.15), size=(9, 11), mat=REDWOOD_W, paint=p_cone,
                   double=True)]

PIECES = F4.build(ME)
