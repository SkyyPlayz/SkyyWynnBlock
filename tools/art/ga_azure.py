"""SkyWynn Foraging armor - F2 Autumn - AZURE set (v3). ORIGINAL; no vanilla or Armory pixels.

Started from the IN-GAME Azure wood: hues / values sampled from the game's Azure trunk, log end, leaves and glowing azure
petals; our own pixels. v1 colours (plum-purple bark with SWIRLING diagonal grain, indigo cloth) with only the parts that were
already blue a little brighter in v3 (Skyy: "Take the V1 azure, and make the parts that are already blue a little brighter blue,
and add some more leaves to the design."): brighter blue leaves, blue-silver heartwood and cyan petals; more small azure leaves
at the crown, collar, shoulders, belt, bracers and knees.
Plate shape vs the F1 trees and Maple: CRESCENT plates - every plate's lower edge curves up between sharp hooked points (an
upside-down scallop: concave arcs, points at the joins); curved crescent crown points. Mark: a spray of GLOWING AZURE PETALS
(3 cyan crescent petals) on the knot-boss belt clasp and at the helmet temple.
All tier-2 upgrades come from ga_f2.py (identical for every F2 tree).
"""
import numpy as np
import ga_paint as P
from ga_paint import AZURE, AZUREDK, ALEAF, AWOOD, PETAL, INDIGO, hash2, stamp
from ga_oak import _horiz, _side_cut
import ga_f2 as F2

TIER, TREE = F2.TIER, "Azure"
BARK, DK, LEAF, WOOD, CLOTH = AZURE, AZUREDK, ALEAF, AWOOD, INDIGO


def base(F, seed=0, scars=True):
    """azure bark: swirling diagonal grain streaks, a few dark curving furrows with a lit upper lip."""
    m0 = F.mat == BARK
    n2 = P.vnoise(F.W, 9.0, 170 + seed)
    F.val[m0] += 0.04 * np.round((n2[m0] - 0.5) * 3)
    h = _horiz(F)
    diag = h * 0.6 + F.y + 1.6 * np.sin(h * 0.33 + seed)       # swirling diagonal coordinate
    band = np.floor(diag / 1.5).astype(np.int64)
    F.val[m0] += (0.06 * np.round((hash2(band, band * 0 + 7, seed + 51) - 0.5) * 2) / 2)[m0]
    if F.is_side() and scars:
        c = np.floor(diag / 6.0).astype(np.int64)
        f = diag / 6.0 - np.floor(diag / 6.0)
        seg = np.floor(h / 6.0).astype(np.int64)
        on = hash2(c, seg, seed + 53) < 0.4
        fur = on & (f < 0.17) & m0
        F.mat[fur] = DK
        F.val[fur] = 0.15
        lip = on & (f >= 0.17) & (f < 0.34) & m0
        F.val[lip] += 0.08


def _cusp(hc, step):
    """crescent profile: 0 at the sharp points (plate joins), rising to 2.2 in the middle (the arc curves up)."""
    x = hc / step
    return 2.2 * (1 - ((x - 0.5) / 0.5) ** 2)


def plates(F, region, pitch, seed=0, y_top=None, step=8.0):
    """overlapping plates whose lower edges are crescents (concave arcs between sharp points)."""
    region = np.asarray(region, bool) & F.alpha
    if not region.any():
        return
    if y_top is None:
        y_top = F.y[region].max() + 1e-3
    h = _horiz(F)
    row0 = np.floor((y_top - F.y) / pitch).astype(np.int64)
    off = np.where(row0 % 2 == 0, 0.0, step / 2.0)
    hc = np.mod(h + off, step)
    s_ = (y_top - F.y + _cusp(hc, step)) / pitch            # arcs curve UP (edge higher in the middle)
    k = np.floor(s_); f = s_ - k
    ki = k.astype(np.int64)
    plate = np.floor((h + np.where(ki % 2 == 0, 0.0, step / 2.0)) / step).astype(np.int64)
    F.val[region] += ((hash2(plate, ki, seed + 3) - 0.5) * 0.10)[region] + 0.04 * (0.5 - f[region])
    dv, du = P.face_down(F)
    kd = np.roll(k, (-dv, -du), axis=(0, 1))
    under = region & (kd > k) & (k >= 0)
    F.mat[under] = DK
    F.val[under] = -0.05
    ku = np.roll(k, (dv, du), axis=(0, 1))
    bev = region & (ku < k) & (k > 0)
    F.mat[bev & (F.mat == DK)] = BARK
    F.val[bev] += 0.12


def hem(F, seed=0, clip=2, step=8.0):
    """crescent hem: the bottom edge is cut into concave arcs between sharp hooked points; silver cut line along it."""
    if F.face not in ("front", "back", "left", "right"):
        return
    d = F.fh - F.v
    if F.face in ("front", "back") and clip:
        depth = _cusp(np.mod(F.u, step), step)
        F.alpha &= ~(d < depth)
        dd = d - depth
    else:
        dd = d
    m = (dd >= 0) & (dd < 1) & F.alpha
    F.mat[m] = WOOD
    F.val[m] -= 0.06


AZURE_LEAF_MASK = [          # azure leaf: broad pointed oval with a curled tip, stem at the bottom
    "....LL.",
    "...LLl.",
    "..LLvLl",
    ".LLvLLl",
    ".LLvLll",
    "LLvLLl.",
    "LLvLll.",
    ".LvLl..",
    "..sl...",
    "..s....",
]
PETAL_SPRAY_MASK = [         # three glowing crescent petals on one short stalk
    "P.......P",
    "PP..P..PP",
    ".PG.PG.Gp",
    ".pPGPGPp.",
    "..pPGPp..",
    "...pPp...",
    "....s....",
    "....s....",
]
LEAF_COL = {"L": (ALEAF, 0.06), "l": (ALEAF, -0.08), "v": (ALEAF, 0.18), "s": (AZUREDK, 0.7)}
PETAL_COL = {"P": (PETAL, 0.12), "p": (PETAL, -0.06), "G": (PETAL, 0.42), "s": (AZUREDK, 0.7)}


def p_leaf(F):
    F2._mask_paint(F, AZURE_LEAF_MASK, LEAF_COL)


def p_leaf_hang(F):
    F2._mask_paint(F, AZURE_LEAF_MASK, LEAF_COL, flip_v=True)


def p_petals(F):
    F2._mask_paint(F, PETAL_SPRAY_MASK, PETAL_COL)
    F.lockval[F.mat == PETAL] = False


def leaflet(F, cu, cv):
    m = (np.abs(F.u - cu) < 1.01) & (np.abs(F.v - cv) < 0.61)
    m |= (np.abs(F.u - cu) < 0.51) & (np.abs(F.v - cv) < 1.11)
    stamp(F, m, ALEAF, hl=0.2, lo=0.1, shadow=0.12, add=0.05)


CRESCENT_MASK = [            # curved crescent crown point (hooks to the right)
    ".....XX",
    "....XX.",
    "...XXX.",
    "..XXX..",
    "..XXX..",
    ".XXXX..",
    ".XXXX..",
    ".XXXX..",
    ".XXXXX.",
    "..XXXX.",
    "..XXXXX",
    "..XXXX.",
    "..XXX..",
    "..XXX..",
    "..XXX..",
]


def _crown(F, seed, flip=False):
    base(F, seed=seed, scars=False)
    if F.face in ("front", "back"):
        H, W = len(CRESCENT_MASK), len(CRESCENT_MASK[0])
        iv = np.clip((F.v / F.fh * H).astype(int), 0, H - 1)
        iu = np.clip((F.u / F.fw * W).astype(int), 0, W - 1)
        if flip != (F.face == "back"):
            iu = W - 1 - iu
        ch = np.array([list(r) for r in CRESCENT_MASK])[iv, iu]
        F.alpha &= ch == "X"
        a = F.alpha
        e = a & ~(P._shift(a, 0, 1) & P._shift(a, 0, -1))
        F.val[e] -= 0.16
        inner = a & P._shift(a, 0, 1) & ~P._shift(a, 0, -1)
        F.mat[inner & (F.v < F.fh * 0.6)] = WOOD                 # silver inner edge of the crescent
    else:
        _side_cut(F, F.fh * 0.6)


def crown_mid(F):
    _crown(F, 7)


def crown_side(F):
    _crown(F, 8, flip=True)


CROWN_MID_SIZE, CROWN_MID_PIVOT = (7, 15, 2), (0, 18.5, 15.25)
CROWN_SIDE_SIZE, CROWN_SIDE_PIVOT, CROWN_SIDE_ROT = (7, 12, 2), (-9.0, 16.5, 14.75), (0, 0, 14)
LEAF_SIZE, LEAF_SIZE_SMALL = (7, 10), (6, 8)

SMALL = (4, 6)              # v3: small flat azure leaves added around the set (Skyy: "add some more leaves to the design")

MARK_HEAD = [
    # two small leaves at the base of the middle crown point
    dict(name="R-CrownLeaf", bone="Head", pivot=(-3.2, 16.0, 16.4), rot=(0, 0, 32), size=SMALL, offset=(0, 3.0, 0),
         mat=ALEAF, paint=p_leaf, double=True, mirror=True),
    dict(name="L-HelmPetals", bone="Head", pivot=(17.0, 5.0, 4.0), rot=(0, 90, 0), size=(9, 8), offset=(0, -4.0, 0),
         mat=PETAL, paint=p_petals, double=True),
]
MARK_CHEST = [
    # a spray of 3 glowing azure petals rising from the knot-boss clasp, + 2 hanging azure leaves
    dict(name="PetalSpray", bone="Belly", pivot=(0, -6.5, 12.2), size=(11, 10), offset=(0, 0, 0), mat=PETAL,
         paint=p_petals, double=True),
    dict(name="AzureLeafL", bone="Belly", pivot=(-2.2, -8.6, 12.35), rot=(6, 0, -22), size=(6, 8), offset=(0, -4.0, 0),
         mat=ALEAF, paint=p_leaf_hang, double=True),
    dict(name="AzureLeafR", bone="Belly", pivot=(2.2, -8.6, 12.3), rot=(-6, 0, 22), size=(6, 8), offset=(0, -4.0, 0),
         mat=ALEAF, paint=p_leaf_hang, double=True),
    # v3 extra leaves: two more hanging from the belt, a pair at the collar, one more on each shoulder cap
    dict(name="R-BeltLeaf", bone="Belly", pivot=(-5.0, -8.2, 12.2), rot=(4, 0, -40), size=SMALL, offset=(0, -3.0, 0),
         mat=ALEAF, paint=p_leaf_hang, double=True, mirror=True),
    dict(name="R-CollarLeaf", bone="Chest", pivot=(-6.0, 9.8, 11.6), rot=(-15, 0, 38), size=SMALL, offset=(0, 3.0, 0),
         mat=ALEAF, paint=p_leaf, double=True, mirror=True),
    dict(name="R-CapLeaf", bone="R-Arm", parent="R-Pauldron", pivot=(1.0, 2.6, 4.5), rot=(25, 0, 40), size=SMALL,
         offset=(0, 3.0, 0), mat=ALEAF, paint=p_leaf, double=True, mirror=True),
]
EXTRA_HANDS = [
    dict(name="R-Sprig2", bone="R-Forearm", pivot=(-6.3, 1.5, -2.5), rot=(0, -90, 0), size=SMALL, offset=(0, 3.0, 0),
         mat=ALEAF, paint=p_leaf, double=True, mirror=True),
]
EXTRA_LEGS = [
    dict(name="R-KneeLeaf", bone="R-Calf", parent="R-Knee", pivot=(2.2, 2.0, 1.2), rot=(0, 0, -35), size=SMALL,
         offset=(0, 3.0, 0), mat=ALEAF, paint=p_leaf, double=True, mirror=True),
]

PIECES = F2.build(__import__(__name__))
