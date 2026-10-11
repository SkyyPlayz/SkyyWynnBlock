"""SkyWynn Foraging armor - F3 Savanna - DRY set (v1). ORIGINAL; no vanilla or Armory pixels.

Started from the IN-GAME Dry wood: hues / values sampled from the game's Dry log, drywood planks and leaves (item icons); our
own pixels. Warm brown bark with long dark vertical fibres, cream-gold heartwood, the game's bright yellow leaves, rust cloth.
Plate shape: SPLINTER plates - each plate's lower edge is a jagged saw-tooth (split dry wood); splinter-spike crown points.
Mark: a cluster of three round yellow PUFF BLOSSOMS on a twig (dry savanna tree flowers) on the belt clasp and at the temple.
All tier-3 upgrades come from ga_f3.py (identical for every F3 tree), on top of the tier-2 ones (ga_f2.py).
"""
import numpy as np
import ga_paint as P
from ga_paint import DRY, DRYDK, DRYLEAF, DRYWOOD, RUST, hash2, stamp
from ga_oak import _horiz
import ga_f2 as F2
import ga_f3 as F3

TIER, TREE = F3.TIER, "Dry"
BARK, DK, LEAF, WOOD, CLOTH = DRY, DRYDK, DRYLEAF, DRYWOOD, RUST


def base(F, seed=0, scars=True):
    """dry bark: strong long vertical fibres (column streaks), frequent thin dark fibre cracks with a lit left texel."""
    m0 = F.mat == BARK
    n2 = P.vnoise(F.W, 8.0, 160 + seed)
    F.val[m0] += 0.03 * np.round((n2[m0] - 0.5) * 3)
    h = _horiz(F)
    col = np.floor(h).astype(np.int64)
    fib = hash2(col, np.floor(F.y / 6).astype(np.int64), seed + 71) - 0.5
    F.val[m0] += 0.08 * np.round(fib[m0] * 2) / 2
    if F.is_side() and scars:
        wav = h + 0.5 * np.sin(F.y * 0.5 + seed)
        c = np.floor(wav / 3.0).astype(np.int64)
        f = wav / 3.0 - np.floor(wav / 3.0)
        seg = np.floor((F.y + c * 3.7) / 8.0).astype(np.int64)
        on = hash2(c, seg, seed + 73) < 0.5
        crack = on & (f < 0.3) & m0
        F.mat[crack] = DK
        F.val[crack] = 0.35
        lip = on & (f >= 0.3) & (f < 0.62) & m0
        F.val[lip] += 0.06


PROF_STEP, PROF_MAX = 8.0, 2.5


def PROF(hc, step):
    """splinter saw-tooth: two teeth per plate, one long, one short, each a straight slanted cut."""
    x = hc / step
    t = np.mod(x * 2, 1.0)
    amp = np.where(x < 0.5, 2.5, 1.6)
    return t * amp


def plates(F, region, pitch, seed=0, y_top=None):
    F3.profile_plates(F, region, pitch, seed, PROF, PROF_STEP, __import__(__name__), y_top)


def hem(F, seed=0, clip=2):
    F3.profile_hem(F, seed, clip, PROF, PROF_STEP, __import__(__name__), PROF_MAX)


LEAF_MASK = [                # a sprig of small paired leaflets (L lit, l shade, v stem)
    "...L...",
    "..LLl..",
    "LL.v.Ll",
    "Ll.v.ll",
    ".LLvLl.",
    "LL.v.Ll",
    "Ll.v.ll",
    ".LLvLl.",
    "...v...",
    "...s...",
    "...s...",
]
PUFF_MASK = [                # the mark: three round puff blossoms on a twig
    "...PPP.....",
    "..PPPPP.PP.",
    "..PpPPpPPPP",
    "..PPpPPPpPp",
    "...PPP.PPpP",
    "....s...pp.",
    ".PPP.s.s...",
    "PPPPP.ss...",
    "PpPPp.s....",
    ".PpP.ss....",
    "...sss.....",
    "....s......",
]
COL = {"L": (DRYLEAF, 0.06), "l": (DRYLEAF, -0.1), "v": (DRYDK, 0.6), "s": (DRYDK, 0.6)}
PUFF_COL = {"P": (DRYLEAF, 0.16), "p": (DRYLEAF, -0.02), "s": (DRYDK, 0.6)}


def p_leaf(F):
    F2._mask_paint(F, LEAF_MASK, COL)


def p_leaf_hang(F):
    F2._mask_paint(F, LEAF_MASK, COL, flip_v=True)


def p_puffs(F):
    F2._mask_paint(F, PUFF_MASK, PUFF_COL)


def leaflet(F, cu, cv):
    m = (np.abs(F.u - cu) < 1.01) & (np.abs(F.v - cv) < 1.01)
    stamp(F, m, DRYLEAF, hl=0.2, lo=0.1, shadow=0.12, add=0.08)


CROWN_MASK = [               # splinter spike: a tall jagged point with a side splinter
    "...X...",
    "...XX..",
    "..XXX..",
    "..XXX..",
    "..XXXX.",
    ".XXXX.X",
    ".XXXXXX",
    ".XXXXX.",
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
LEAF_SIZE, LEAF_SIZE_SMALL = (7, 11), (6, 9)

MARK_HEAD = [
    dict(name="L-HelmPuffs", bone="Head", pivot=(17.0, 9.0, 4.0), rot=(0, 90, 0), size=(9, 10), offset=(0, 0, 0),
         mat=DRYLEAF, paint=p_puffs, double=True),
]
MARK_CHEST = [
    dict(name="DryBadge", bone="Belly", pivot=(0, -4.0, 12.15), size=(11, 12), offset=(0, 0, 0), mat=DRYLEAF,
         paint=p_puffs, double=True),
]

PIECES = F3.build(__import__(__name__))
