"""SkyWynn Foraging armor - F4 Northern - CEDAR set (v1). ORIGINAL; no vanilla or Armory pixels.

Started from the IN-GAME Cedar wood: hues / values sampled from the game's Cedar log and leaves (item icons); our own pixels.
Warm orange-brown bark in long slightly twisting FIBRE STRIPS with peeling light edges, rosy-tan heartwood, the game's
teal cedar fronds, burgundy cloth.
Plate shape: ARCH plates - each plate's lower edge is a pointed arch (curved sides meeting in a point); flame-shaped crown
points. Mark: a CEDAR ROSE (the cedar cone's rosette) on the belt and at the temple.
All tier-4 upgrades come from ga_f4.py (identical for every F4 tree), on top of the tier-2 / tier-3 ones.
"""
import numpy as np
import ga_paint as P
from ga_paint import CEDAR, CEDDK, CEDLEAF, CEDWOOD, BURGUNDY, hash2, stamp
from ga_oak import _horiz
import ga_f2 as F2
import ga_f4 as F4

TIER, TREE = F4.TIER, "Cedar"
BARK, DK, LEAF, WOOD, CLOTH = CEDAR, CEDDK, CEDLEAF, CEDWOOD, BURGUNDY
ME = __import__(__name__)

def base(F, seed=0, scars=True):
    """cedar bark: long fibre strips running slightly diagonal, a dark seam and a light peeling edge on each strip."""
    m0 = F.mat == BARK
    h = _horiz(F) + F.y * 0.12
    s = np.floor(h / 3.0).astype(np.int64)
    f = h / 3.0 - s
    F.val[m0] += (0.08 * (hash2(s, np.floor(F.y / 14).astype(np.int64), seed + 121) - 0.5))[m0]
    n2 = P.vnoise(F.W, 8.0, 220 + seed)
    F.val[m0] += 0.03 * np.round((n2[m0] - 0.5) * 3)
    if F.is_side() and scars:
        seam = (f < 0.28) & m0 & (hash2(s, np.floor(F.y / 9).astype(np.int64), seed + 123) < 0.7)
        F.mat[seam] = DK
        F.val[seam] = 0.4
        F.val[(f > 0.28) & (f < 0.6) & m0] += 0.06


PROF_STEP, PROF_MAX = 9.0, 3.0


def PROF(hc, step):
    x = hc / step
    return (1 - np.sqrt(np.abs(2 * x - 1))) * PROF_MAX


LEAF_MASK = [
    ".L.L.L.",
    "LlLLLlL",
    ".LLsLl.",
    "LlLsLlL",
    ".LLsLl.",
    "..LsL..",
    "..LsL..",
    "...s...",
    "...s...",
    "...s...",
]
MARK_MASK = [
    "...RRR...",
    ".RRrRrRR.",
    ".RrRRRrR.",
    "RRRrcrRRR",
    "RrRcccRrR",
    "RRRrcrRRR",
    ".RrRRRrR.",
    ".RRrRrRR.",
    "...RRR...",
]
COL = {"L": (CEDLEAF, 0.08), "l": (CEDLEAF, -0.1), "s": (CEDDK, 0.6)}
MARK_COL = {"R": (CEDWOOD, 0.06), "r": (CEDWOOD, -0.16), "c": (CEDDK, 0.6)}
MARK_SIZE = (9, 9)
CROWN_MASK = [
    "...X...",
    "...XX..",
    "..XXX..",
    ".XXXX..",
    ".XXXXX.",
    "XXXXXXX",
    "XXXXXXX",
    ".XXXXX.",
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
MARK_HEAD = [dict(name="L-HelmCedar", bone="Head", pivot=(17.0, 9.0, 4.0), rot=(0, 90, 0), size=MARK_SIZE, mat=LEAF,
                  paint=p_mark, double=True)]
MARK_CHEST = [dict(name="CedarBadge", bone="Belly", pivot=(0, -4.0, 12.15), size=MARK_SIZE, mat=LEAF, paint=p_mark,
                   double=True)]

PIECES = F4.build(ME)
