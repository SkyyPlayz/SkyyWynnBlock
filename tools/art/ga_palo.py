"""SkyWynn Foraging armor - F3 Savanna - PALO set (v1). ORIGINAL; no vanilla or Armory pixels.

Started from the IN-GAME Palo wood: hues / values sampled from the game's Palo log, greenwood planks and blossoms (item
icons); our own pixels. Smooth olive-green bark (the green-barked palo) with fine horizontal lenticel dashes, pale
yellow-green heartwood, the game's orange-gold palo blossoms, chocolate cloth.
Plate shape: CHEVRON plates - each plate's lower edge is one big downward V (arrow); arrowhead crown points.
Mark: a spray of two orange 5-petal PALO BLOSSOMS on the belt clasp and at the temple.
All tier-3 upgrades come from ga_f3.py (identical for every F3 tree), on top of the tier-2 ones (ga_f2.py).
"""
import numpy as np
import ga_paint as P
from ga_paint import PALO, PALODK, PALOLEAF, PALOWOOD, COCOA, hash2, stamp
from ga_oak import _horiz
import ga_f2 as F2
import ga_f3 as F3

TIER, TREE = F3.TIER, "Palo"
BARK, DK, LEAF, WOOD, CLOTH = PALO, PALODK, PALOLEAF, PALOWOOD, COCOA


def base(F, seed=0, scars=True):
    """palo bark: smooth green, soft vertical sheen streaks, short horizontal dark lenticel dashes."""
    m0 = F.mat == BARK
    n2 = P.vnoise(F.W, 9.0, 180 + seed)
    F.val[m0] += 0.04 * np.round((n2[m0] - 0.5) * 3)
    h = _horiz(F)
    col = np.floor(h / 2).astype(np.int64)
    st = hash2(col, np.floor(F.y / 10).astype(np.int64), seed + 91) - 0.5
    F.val[m0] += 0.05 * np.round(st[m0] * 2) / 2
    if F.is_side() and scars:
        cell_u = np.floor(h / 4.0).astype(np.int64)
        cell_v = np.floor(F.y / 3.0).astype(np.int64)
        on = hash2(cell_u, cell_v, seed + 93) < 0.2
        fu = h / 4.0 - np.floor(h / 4.0)
        fv = F.y / 3.0 - np.floor(F.y / 3.0)
        dash = on & (fu > 0.2) & (fu < 0.8) & (fv < 0.34) & m0
        F.mat[dash] = DK
        F.val[dash] = 0.45


PROF_STEP, PROF_MAX = 10.0, 3.0


def PROF(hc, step):
    """chevron: one big downward V per plate."""
    x = hc / step
    return (1 - np.abs(2 * x - 1)) * PROF_MAX


def plates(F, region, pitch, seed=0, y_top=None):
    F3.profile_plates(F, region, pitch, seed, PROF, PROF_STEP, __import__(__name__), y_top)


def hem(F, seed=0, clip=2):
    F3.profile_hem(F, seed, clip, PROF, PROF_STEP, __import__(__name__), PROF_MAX)


LEAF_MASK = [                # a spray of orange florets on a green-brown stem
    ".P...P.",
    "PpP.PpP",
    ".P.s.P.",
    "...s...",
    ".P.s.P.",
    "PpPsPpP",
    ".P.s.P.",
    "...s...",
    "...s...",
]
BLOSSOM_MASK = [             # the mark: two 5-petal blossoms on a forked stem
    "..P........",
    "PPPPP...P..",
    ".PcP..PPPPP",
    "PP.PP..PcP.",
    "..s...PP.PP",
    "..s.....s..",
    "...s...s...",
    "....s.s....",
    ".....s.....",
    ".....s.....",
]
COL = {"P": (PALOLEAF, 0.08), "p": (PALOLEAF, -0.14), "s": (PALO, -0.05)}
BLOSSOM_COL = {"P": (PALOLEAF, 0.1), "c": (PALOLEAF, -0.3), "s": (PALO, -0.05)}


def p_leaf(F):
    F2._mask_paint(F, LEAF_MASK, COL)


def p_leaf_hang(F):
    F2._mask_paint(F, LEAF_MASK, COL, flip_v=True)


def p_blossoms(F):
    F2._mask_paint(F, BLOSSOM_MASK, BLOSSOM_COL)


def leaflet(F, cu, cv):
    m = (np.abs(F.u - cu) < 1.01) & (np.abs(F.v - cv) < 0.51)
    m |= (np.abs(F.u - cu) < 0.51) & (np.abs(F.v - cv) < 1.01)
    stamp(F, m, PALOLEAF, hl=0.2, lo=0.1, shadow=0.12, add=0.05)


CROWN_MASK = [               # arrowhead
    "...X...",
    "..XXX..",
    "..XXX..",
    ".XXXXX.",
    ".XXXXX.",
    "XXXXXXX",
    "XX.X.XX",
    "X.XXX.X",
    "..XXX..",
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
LEAF_SIZE, LEAF_SIZE_SMALL = (7, 9), (6, 8)

MARK_HEAD = [
    dict(name="L-HelmBlossoms", bone="Head", pivot=(17.0, 9.0, 4.0), rot=(0, 90, 0), size=(10, 9), offset=(0, 0, 0),
         mat=PALOLEAF, paint=p_blossoms, double=True),
]
MARK_CHEST = [
    dict(name="PaloBadge", bone="Belly", pivot=(0, -4.0, 12.15), size=(11, 10), offset=(0, 0, 0), mat=PALOLEAF,
         paint=p_blossoms, double=True),
]

PIECES = F3.build(__import__(__name__))
