"""SkyWynn Foraging armor - F3 Savanna - BOTTLETREE set (v1). ORIGINAL; no vanilla or Armory pixels.

Started from the IN-GAME Bottletree wood: hues / values sampled from the game's Bottletree log, drywood planks and leaves
(item icons); our own pixels. Pale grey-cream bark with soft darker smudges and short dark cracks, cream heartwood, the game's
olive-lime blade leaves, deep teal cloth.
Plate shape: CRENELLATED plates - each plate's lower edge is cut into square teeth; bottle-shaped crown points (swollen body,
narrow neck). Mark: a little BOTTLE TREE (swollen pale trunk with a tuft of green blades) on the belt clasp and at the temple.
All tier-3 upgrades come from ga_f3.py (identical for every F3 tree), on top of the tier-2 ones (ga_f2.py).
"""
import numpy as np
import ga_paint as P
from ga_paint import BOTTLE, BOTDK, BOTLEAF, BOTWOOD, TEAL, hash2, stamp
from ga_oak import _horiz
import ga_f2 as F2
import ga_f3 as F3

TIER, TREE = F3.TIER, "Bottletree"
BARK, DK, LEAF, WOOD, CLOTH = BOTTLE, BOTDK, BOTLEAF, BOTWOOD, TEAL


def base(F, seed=0, scars=True):
    """bottletree bark: pale, soft darker vertical smudges, a few short dark vertical cracks."""
    m0 = F.mat == BARK
    n2 = P.vnoise(F.W, 6.0, 170 + seed)
    F.val[m0] += 0.05 * np.round((n2[m0] - 0.5) * 3)
    h = _horiz(F)
    col = np.floor(h / 2).astype(np.int64)
    sm = hash2(col, np.floor(F.y / 5).astype(np.int64), seed + 81)
    F.val[m0 & (sm < 0.18)] -= 0.08
    if F.is_side() and scars:
        c = np.floor(h / 4.0).astype(np.int64)
        f = h / 4.0 - np.floor(h / 4.0)
        seg = np.floor((F.y + c * 2.3) / 4.0).astype(np.int64)
        on = hash2(c, seg, seed + 83) < 0.22
        crack = on & (f < 0.25) & m0
        F.mat[crack] = DK
        F.val[crack] = 0.3
        lip = on & (f >= 0.25) & (f < 0.5) & m0
        F.val[lip] += 0.05


PROF_STEP, PROF_MAX = 6.0, 2.0


def PROF(hc, step):
    """crenellation: square teeth half a plate wide."""
    return np.where(hc / step < 0.5, PROF_MAX, 0.0)


def plates(F, region, pitch, seed=0, y_top=None):
    F3.profile_plates(F, region, pitch, seed, PROF, PROF_STEP, __import__(__name__), y_top)


def hem(F, seed=0, clip=2):
    F3.profile_hem(F, seed, clip, PROF, PROF_STEP, __import__(__name__), PROF_MAX)


LEAF_MASK = [                # a tuft of 4 thin blades (L lit, l shade, s stem)
    "L..L...",
    "L..L..l",
    "Ll.L.l.",
    ".L.Ll.l",
    ".LlLll.",
    "..LLl..",
    "..LLl..",
    "...L...",
    "...s...",
    "...s...",
]
TREE_MASK = [                # the mark: a little bottle tree
    "L.L.L.L.l",
    ".LlLlLll.",
    "..LLlLl..",
    "...lLl...",
    "....B....",
    "...BBb...",
    "...BBb...",
    "..BBBbb..",
    ".BBBBBbb.",
    ".BBBBBbb.",
    ".BBBBBbb.",
    "..BBBbb..",
    "...ddd...",
]
COL = {"L": (BOTLEAF, 0.06), "l": (BOTLEAF, -0.1), "s": (BOTDK, 0.5)}
TREE_COL = {"L": (BOTLEAF, 0.08), "l": (BOTLEAF, -0.08), "B": (BOTTLE, 0.12), "b": (BOTTLE, -0.04), "d": (BOTDK, 0.4)}


def p_leaf(F):
    F2._mask_paint(F, LEAF_MASK, COL)


def p_leaf_hang(F):
    F2._mask_paint(F, LEAF_MASK, COL, flip_v=True)


def p_tree(F):
    F2._mask_paint(F, TREE_MASK, TREE_COL)


def leaflet(F, cu, cv):
    m = (np.abs(F.u - cu) < 0.51) & (np.abs(F.v - cv) < 1.11)
    m |= (np.abs(F.u - cu + 1.0) < 0.51) & (np.abs(F.v - cv + 0.5) < 0.61)
    stamp(F, m, BOTLEAF, hl=0.2, lo=0.1, shadow=0.12, add=0.05)


CROWN_MASK = [               # bottle: a lip, a narrow neck, a swollen body
    ".XXXXX.",
    "..XXX..",
    "..XXX..",
    ".XXXXX.",
    "XXXXXXX",
    "XXXXXXX",
    "XXXXXXX",
    "XXXXXXX",
    ".XXXXX.",
    "..XXX..",
    "..XXX..",
    "..XXX..",
    "..XXX..",
    "..XXX..",
    "..XXX..",
]


def crown_mid(F):
    F3.mask_crown(F, CROWN_MASK, __import__(__name__), 7)


def crown_side(F):
    F3.mask_crown(F, CROWN_MASK, __import__(__name__), 8)


CROWN_MID_SIZE, CROWN_MID_PIVOT = (7, 15, 2), (0, 18.5, 15.25)
CROWN_SIDE_SIZE, CROWN_SIDE_PIVOT, CROWN_SIDE_ROT = (7, 12, 2), (-9.0, 16.5, 14.75), (0, 0, 14)
LEAF_SIZE, LEAF_SIZE_SMALL = (7, 10), (6, 8)

MARK_HEAD = [
    dict(name="L-HelmTree", bone="Head", pivot=(17.0, 9.0, 4.0), rot=(0, 90, 0), size=(8, 11), offset=(0, 0, 0),
         mat=BOTLEAF, paint=p_tree, double=True),
]
MARK_CHEST = [
    dict(name="BottleBadge", bone="Belly", pivot=(0, -4.0, 12.15), size=(9, 13), offset=(0, 0, 0), mat=BOTTLE,
         paint=p_tree, double=True),
]

PIECES = F3.build(__import__(__name__))
