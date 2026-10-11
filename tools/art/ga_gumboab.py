"""SkyWynn Foraging armor - F3 Savanna - GUMBOAB set (v1). ORIGINAL; no vanilla or Armory pixels.

Started from the IN-GAME Gumboab wood: hues / values sampled from the game's Gumboab log, lightwood planks and leaves (item
icons); our own pixels. Smooth grey-taupe bark with soft vertical streaks and horizontal FOLDS (the thick baobab-like trunk),
cream-tan heartwood, the game's sage-olive blade leaves, ochre cloth (savanna).
Plate shape: wide TERRACED plates - each plate's lower edge is a broad flat step with angled ends; flat-topped tower crown points.
Mark: a FAN of 5 long sage gumboab blades on the belt clasp and at the helmet temple.
All tier-3 upgrades come from ga_f3.py (identical for every F3 tree), on top of the tier-2 ones (ga_f2.py).
"""
import numpy as np
import ga_paint as P
from ga_paint import GUMBOAB, GUMDK, GUMLEAF, GUMWOOD, OCHRE, hash2, stamp
from ga_oak import _horiz
import ga_f2 as F2
import ga_f3 as F3

TIER, TREE = F3.TIER, "Gumboab"
BARK, DK, LEAF, WOOD, CLOTH = GUMBOAB, GUMDK, GUMLEAF, GUMWOOD, OCHRE


def base(F, seed=0, scars=True):
    """gumboab bark: smooth, soft long vertical streaks, a few horizontal folds (dark line, lit lip above)."""
    m0 = F.mat == BARK
    n2 = P.vnoise(F.W, 10.0, 150 + seed)
    F.val[m0] += 0.03 * np.round((n2[m0] - 0.5) * 3)
    h = _horiz(F)
    col = np.floor(h).astype(np.int64)
    st = hash2(col, np.floor(F.y / 7).astype(np.int64), seed + 61) - 0.5
    F.val[m0] += 0.07 * np.round(st[m0] * 2) / 2
    streak = (hash2(col, np.floor(F.y / 11).astype(np.int64), seed + 67) < 0.12) & m0
    F.val[streak] -= 0.08
    if F.is_side() and scars:
        wav = F.y + 0.6 * np.sin(h * 0.45 + seed)
        r = np.floor(wav / 6.0).astype(np.int64)
        f = wav / 6.0 - np.floor(wav / 6.0)
        seg = np.floor(h / 9.0).astype(np.int64)
        on = hash2(seg, r, seed + 63) < 0.28
        fold = on & (f < 0.17) & m0
        F.mat[fold] = DK
        F.val[fold] = 0.3
        lip = on & (f >= 0.17) & (f < 0.34) & m0
        F.val[lip] += 0.07


PROF_STEP, PROF_MAX = 12.0, 2.0


def PROF(hc, step):
    """terrace: a broad flat step with angled ends (V notch between plates)."""
    x = hc / step
    return np.clip(np.minimum(x, 1 - x) / 0.18, 0, 1) * PROF_MAX


def plates(F, region, pitch, seed=0, y_top=None):
    F3.profile_plates(F, region, pitch, seed, PROF, PROF_STEP, __import__(__name__), y_top)


def hem(F, seed=0, clip=2):
    F3.profile_hem(F, seed, clip, PROF, PROF_STEP, __import__(__name__), PROF_MAX)


BLADE_MASK = [               # 3 long blades from one stem (L lit, l shade, v vein, s stem)
    "L...L...l",
    "Ll..L..ll",
    ".L..Lv.l.",
    ".Ll.Lv.l.",
    "..L.Lvll.",
    "..LlLvl..",
    "...LLvl..",
    "...LLl...",
    "....Ll...",
    "....s....",
    "....s....",
]
FAN_MASK = [                 # the mark: a fan of 5 long blades
    "L....L....l",
    "LL...L...ll",
    ".L...Lv..l.",
    ".LL..Lv.ll.",
    "L.L..Lv.l.l",
    "LL.L.Lvl.ll",
    ".LL.LLvl.l.",
    "..LLLLvlll.",
    "...LLLvll..",
    ".....s.....",
    ".....s.....",
]
COL = {"L": (GUMLEAF, 0.06), "l": (GUMLEAF, -0.1), "v": (GUMLEAF, -0.18), "s": (GUMDK, 0.7)}


def p_leaf(F):
    F2._mask_paint(F, BLADE_MASK, COL)


def p_leaf_hang(F):
    F2._mask_paint(F, BLADE_MASK, COL, flip_v=True)


def p_fan(F):
    F2._mask_paint(F, FAN_MASK, COL)


def leaflet(F, cu, cv):
    m = (np.abs(F.u - cu) < 0.51) & (np.abs(F.v - cv) < 1.11)
    m |= (np.abs(F.u - cu - 0.7) < 0.51) & (np.abs(F.v - cv + 0.6) < 0.61)
    stamp(F, m, GUMLEAF, hl=0.2, lo=0.1, shadow=0.12, add=0.05)


CROWN_MASK = [               # flat-topped swollen trunk (the thick gumboab), angled top corners
    ".XXXXX.",
    "XXXXXXX",
    "XXXXXXX",
    "XXXXXXX",
    ".XXXXX.",
    ".XXXXX.",
    ".XXXXX.",
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
LEAF_SIZE, LEAF_SIZE_SMALL = (9, 11), (7, 9)

MARK_HEAD = [
    dict(name="L-HelmFan", bone="Head", pivot=(17.0, 9.0, 4.0), rot=(0, 90, 0), size=(9, 9), offset=(0, 0, 0),
         mat=GUMLEAF, paint=p_fan, double=True),
]
MARK_CHEST = [
    dict(name="GumboabBadge", bone="Belly", pivot=(0, -4.0, 12.15), size=(11, 11), offset=(0, 0, 0), mat=GUMLEAF,
         paint=p_fan, double=True),
]

PIECES = F3.build(__import__(__name__))
