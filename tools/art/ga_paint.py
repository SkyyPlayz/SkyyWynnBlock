"""Painting engine for the SkyWynn Foraging armor textures (copied from the Dark Leather painter, own materials) (original procedural hand-painted style).

Every texel of every face knows: its texel coords (u, v), its node-local point (L), its world point at rest pose (W),
the world normal of its face. Light is painted in from above (top faces brightest, gradient down every side face,
brighter near the head, darker toward the feet), rims catch light on upward edges, ambient occlusion comes from
every other box of the full equipped set + the body, then decorations (straps, lames, trims, rivets, buckles,
embossing, stitches, tatters) are stamped on, each with a raised bevel and a drop shadow.
Values are quantised into flat painterly steps (no grain); every material ramp is hue-shifted
(violet / blue shadows, warm lights) and never reaches pure black or white.
"""
import math
import numpy as np

# ------------------------------------------------------------------ materials (value 0..1 -> colour)
# Oak palette (F1 Grove, key log). v2: hues from the in-game Oak trunk / log end / leaves (values only, own pixels):
# red-brown oak bark, orange-tan cut oak at plate rims, twine rope, ivy vine,
# oak-leaf green, a faint green sap (tier 1 = faint), moss-grey cloth under the bark, acorn brown.
BARK, WOOD, ROPE, VINE, LEAF, SAP, CLOTH, ACORN, ACORNCAP, STITCH = range(10)
MAT_NAMES = ["bark", "wood", "rope", "vine", "leaf", "sap", "cloth", "acorn", "acorncap", "stitch"]
RAMPS = {
    BARK: [(0.00, (30, 14, 12)), (0.20, (46, 22, 16)), (0.35, (62, 32, 22)), (0.50, (82, 44, 29)),
           (0.65, (100, 56, 36)), (0.80, (124, 74, 48)), (1.00, (160, 108, 72))],
    WOOD: [(0.00, (70, 32, 22)), (0.20, (104, 54, 36)), (0.35, (134, 82, 52)), (0.50, (162, 110, 70)),
           (0.65, (176, 132, 86)), (0.80, (190, 154, 104)), (1.00, (214, 186, 134))],
    ROPE: [(0.00, (52, 40, 34)), (0.20, (84, 66, 44)), (0.35, (114, 92, 58)), (0.50, (146, 120, 74)),
           (0.65, (176, 148, 92)), (0.80, (204, 178, 116)), (1.00, (232, 212, 156))],
    VINE: [(0.00, (16, 32, 22)), (0.20, (24, 48, 26)), (0.35, (34, 64, 30)), (0.50, (46, 82, 36)),
           (0.65, (62, 104, 44)), (0.80, (86, 130, 56)), (1.00, (130, 170, 84))],
    LEAF: [(0.00, (18, 40, 12)), (0.20, (30, 60, 16)), (0.35, (42, 80, 18)), (0.50, (54, 104, 22)),
           (0.65, (66, 122, 26)), (0.80, (86, 142, 34)), (1.00, (132, 180, 64))],
    SAP: [(0.00, (40, 84, 40)), (0.30, (70, 128, 52)), (0.50, (102, 162, 66)), (0.70, (138, 196, 88)),
          (0.85, (172, 220, 120)), (1.00, (212, 240, 170))],
    CLOTH: [(0.00, (22, 24, 26)), (0.20, (32, 35, 34)), (0.35, (44, 47, 43)), (0.50, (58, 61, 54)),
            (0.65, (74, 77, 66)), (0.80, (94, 96, 82)), (1.00, (128, 128, 108))],
    ACORN: [(0.00, (70, 34, 22)), (0.20, (104, 54, 26)), (0.35, (138, 76, 32)), (0.50, (170, 100, 42)),
            (0.65, (196, 126, 56)), (0.80, (220, 156, 78)), (1.00, (240, 196, 126))],
    ACORNCAP: [(0.00, (40, 28, 26)), (0.25, (66, 48, 36)), (0.50, (98, 74, 50)), (0.75, (132, 104, 70)),
               (1.00, (176, 146, 102))],
    STITCH: [(0.00, (60, 50, 40)), (0.50, (110, 92, 64)), (1.00, (160, 138, 96))],
}
# Birch (F1 Grove). v2: hues from the in-game Birch trunk / log end / lightwood planks / leaves (own pixels): warm
# cream papery bark (never pure white), grey-brown lenticels / knot "eyes", pale tan heartwood,
# the game's lime yellow-green birch leaves, olive-gold catkins, cool sage cloth.
BIRCH, BIRCHDK, BLEAF, CATKIN, BWOOD, SAGE = range(10, 16)
MAT_NAMES += ["birch", "birchdark", "birchleaf", "catkin", "birchwood", "sage"]
RAMPS.update({
    BIRCH: [(0.00, (100, 86, 78)), (0.20, (140, 124, 112)), (0.35, (172, 154, 138)), (0.50, (198, 180, 162)),
            (0.65, (214, 197, 178)), (0.80, (228, 214, 196)), (1.00, (240, 230, 214))],
    BIRCHDK: [(0.00, (40, 32, 30)), (0.25, (62, 52, 48)), (0.50, (88, 76, 68)), (0.75, (116, 102, 90)),
              (1.00, (146, 130, 116))],
    BLEAF: [(0.00, (58, 72, 10)), (0.20, (90, 110, 14)), (0.35, (116, 138, 18)), (0.50, (140, 164, 24)),
            (0.65, (158, 184, 32)), (0.80, (176, 202, 50)), (1.00, (206, 226, 104))],
    CATKIN: [(0.00, (66, 54, 30)), (0.25, (104, 88, 40)), (0.50, (144, 124, 54)), (0.75, (182, 162, 76)),
             (1.00, (218, 202, 120))],
    BWOOD: [(0.00, (110, 90, 74)), (0.20, (150, 128, 108)), (0.35, (176, 154, 130)), (0.50, (196, 174, 146)),
            (0.65, (210, 190, 156)), (0.80, (222, 206, 166)), (1.00, (236, 224, 188))],
    SAGE: [(0.00, (26, 30, 32)), (0.20, (38, 44, 44)), (0.35, (52, 60, 56)), (0.50, (68, 78, 70)),
           (0.65, (86, 96, 86)), (0.80, (108, 118, 104)), (1.00, (142, 150, 132))],
})
# Beech (F1 Grove), v2: hues sampled from the in-game Beech trunk / planks / leaves (values only, own pixels): warm
# orange-brown bark with long vertical grain streaks, dark red-brown grain + rims, tan heartwood, the game's fresh beech
# green, a copper accent leaf, brown spiky nut husks, deep loden-green cloth.
BEECH, BEECHDK, CLEAF, FLEAF, HUSK, BEWOOD, UMBER, LODEN = range(16, 24)
MAT_NAMES += ["beech", "beechdark", "copperleaf", "freshleaf", "husk", "beechwood", "umber", "loden"]
RAMPS.update({
    BEECH: [(0.00, (40, 26, 20)), (0.20, (66, 43, 28)), (0.35, (90, 59, 35)), (0.50, (114, 77, 44)),
            (0.65, (134, 93, 52)), (0.80, (156, 113, 64)), (1.00, (186, 144, 90))],
    BEECHDK: [(0.00, (26, 16, 14)), (0.25, (42, 26, 20)), (0.50, (60, 36, 26)), (0.75, (80, 50, 32)),
              (1.00, (104, 68, 42))],
    CLEAF: [(0.00, (70, 30, 20)), (0.20, (102, 46, 24)), (0.35, (132, 64, 28)), (0.50, (160, 84, 34)),
            (0.65, (184, 106, 44)), (0.80, (206, 134, 62)), (1.00, (230, 174, 100))],
    FLEAF: [(0.00, (28, 52, 16)), (0.20, (44, 78, 20)), (0.35, (58, 100, 24)), (0.50, (74, 122, 28)),
            (0.65, (92, 144, 32)), (0.80, (116, 166, 44)), (1.00, (164, 204, 82))],
    HUSK: [(0.00, (60, 48, 26)), (0.25, (100, 84, 44)), (0.50, (140, 120, 66)), (0.75, (176, 156, 96)),
           (1.00, (210, 192, 136))],
    BEWOOD: [(0.00, (76, 46, 31)), (0.20, (110, 78, 50)), (0.35, (140, 104, 66)), (0.50, (164, 124, 78)),
             (0.65, (178, 142, 90)), (0.80, (192, 162, 102)), (1.00, (216, 192, 136))],
    UMBER: [(0.00, (30, 24, 24)), (0.20, (44, 36, 34)), (0.35, (60, 50, 44)), (0.50, (78, 66, 56)),
            (0.65, (98, 84, 70)), (0.80, (120, 104, 86)), (1.00, (156, 138, 114))],
    LODEN: [(0.00, (18, 26, 22)), (0.20, (26, 38, 30)), (0.35, (36, 50, 38)), (0.50, (48, 64, 46)),
            (0.65, (62, 80, 56)), (0.80, (80, 98, 68)), (1.00, (112, 128, 92))],
})
# Ash (F1 Grove): hues sampled from the in-game Ash trunk / log end / hardwood planks / leaves (values only, own pixels):
# dark plum-brown bark with lighter interlacing ridges, deep red-brown furrows, pale tan heartwood, the game's deep
# blue-green ash leaves, straw-tan winged seed keys (samaras), cool slate cloth.
ASH, ASHDK, ASHLEAF, SAMARA, ASHWOOD, SLATE = range(24, 30)
MAT_NAMES += ["ash", "ashdark", "ashleaf", "samara", "ashwood", "slate"]
RAMPS.update({
    ASH: [(0.00, (28, 18, 16)), (0.20, (44, 28, 24)), (0.35, (58, 38, 32)), (0.50, (74, 50, 41)),
          (0.65, (92, 64, 51)), (0.80, (114, 82, 64)), (1.00, (146, 112, 86))],
    ASHDK: [(0.00, (16, 10, 10)), (0.25, (26, 16, 15)), (0.50, (38, 24, 21)), (0.75, (52, 33, 28)),
            (1.00, (72, 48, 40))],
    ASHLEAF: [(0.00, (10, 34, 24)), (0.20, (16, 52, 34)), (0.35, (22, 68, 44)), (0.50, (30, 86, 54)),
              (0.65, (42, 104, 62)), (0.80, (60, 126, 74)), (1.00, (104, 162, 106))],
    SAMARA: [(0.00, (70, 52, 30)), (0.25, (112, 88, 52)), (0.50, (150, 124, 78)), (0.75, (184, 160, 108)),
             (1.00, (214, 196, 146))],
    ASHWOOD: [(0.00, (70, 48, 36)), (0.20, (104, 76, 56)), (0.35, (130, 98, 72)), (0.50, (153, 122, 90)),
              (0.65, (166, 138, 100)), (0.80, (180, 156, 114)), (1.00, (206, 188, 142))],
    SLATE: [(0.00, (20, 24, 30)), (0.20, (30, 36, 44)), (0.35, (42, 50, 58)), (0.50, (56, 64, 72)),
            (0.65, (72, 80, 88)), (0.80, (92, 100, 106)), (1.00, (126, 132, 136))],
})
# Aspen (F1 Grove): hues sampled from the in-game Aspen trunk / log end / softwood planks / golden aspen leaves (values
# only, own pixels): pale khaki-cream bark with soft horizontal bands, dark eye-shaped scars, pale cream heartwood with
# rings, the game's golden-orange aspen leaves, russet cloth (the colour of the aspen's softwood planks).
ASPEN, ASPENDK, GOLDLEAF, ASPWOOD, RUSSET = range(30, 35)
MAT_NAMES += ["aspen", "aspendark", "goldleaf", "aspenwood", "russet"]
RAMPS.update({
    ASPEN: [(0.00, (62, 56, 44)), (0.20, (96, 88, 68)), (0.35, (128, 116, 90)), (0.50, (154, 140, 110)),
            (0.65, (172, 156, 124)), (0.80, (186, 172, 144)), (1.00, (208, 198, 174))],
    ASPENDK: [(0.00, (24, 21, 19)), (0.25, (40, 35, 30)), (0.50, (60, 53, 44)), (0.75, (86, 77, 62)),
              (1.00, (118, 105, 80))],
    GOLDLEAF: [(0.00, (96, 44, 10)), (0.20, (140, 72, 14)), (0.35, (172, 98, 18)), (0.50, (196, 124, 20)),
               (0.65, (214, 144, 24)), (0.80, (228, 162, 40)), (1.00, (244, 196, 90))],
    ASPWOOD: [(0.00, (92, 76, 54)), (0.20, (128, 108, 80)), (0.35, (156, 136, 104)), (0.50, (180, 160, 126)),
              (0.65, (196, 178, 142)), (0.80, (208, 192, 156)), (1.00, (226, 214, 180))],
    RUSSET: [(0.00, (30, 20, 16)), (0.20, (48, 32, 24)), (0.35, (66, 44, 32)), (0.50, (88, 58, 40)),
             (0.65, (110, 74, 50)), (0.80, (132, 92, 62)), (1.00, (166, 124, 88))],
})
# ---- F2 Autumn + Azure (tier 2: a modest step up from F1 - same family, more layers, pegs, stronger sap) ----
# Maple: hues sampled from the in-game Crimson Maple trunk / log end / redwood planks / leaves / seeds (own pixels): mauve-brown
# bark, peach heartwood, the game's crimson maple leaves, tan-and-red maple seed pairs, mustard cloth (autumn).
MAPLE, MAPLEDK, MLEAF, MWOOD, MSEED, MUSTARD = range(35, 41)
MAT_NAMES += ["maple", "mapledark", "mapleleaf", "maplewood", "mapleseed", "mustard"]
RAMPS.update({
    MAPLE: [(0.00, (26, 17, 18)), (0.20, (44, 30, 30)), (0.35, (60, 42, 42)), (0.50, (80, 57, 56)),
            (0.65, (98, 70, 68)), (0.80, (118, 86, 82)), (1.00, (150, 114, 106))],
    MAPLEDK: [(0.00, (14, 9, 10)), (0.25, (24, 15, 16)), (0.50, (36, 24, 24)), (0.75, (52, 35, 35)),
              (1.00, (72, 50, 49))],
    MLEAF: [(0.00, (52, 14, 18)), (0.20, (78, 22, 26)), (0.35, (104, 32, 34)), (0.50, (132, 44, 42)),
            (0.65, (156, 58, 46)), (0.80, (178, 78, 54)), (1.00, (210, 120, 80))],
    MWOOD: [(0.00, (80, 52, 44)), (0.20, (120, 82, 64)), (0.35, (152, 106, 80)), (0.50, (180, 128, 98)),
            (0.65, (194, 144, 110)), (0.80, (206, 160, 124)), (1.00, (226, 190, 152))],
    MSEED: [(0.00, (70, 30, 28)), (0.25, (110, 60, 44)), (0.50, (150, 110, 82)), (0.75, (180, 146, 110)),
            (1.00, (212, 186, 146))],
    MUSTARD: [(0.00, (40, 26, 12)), (0.20, (64, 42, 16)), (0.35, (90, 60, 22)), (0.50, (118, 82, 30)),
              (0.65, (142, 102, 38)), (0.80, (164, 124, 52)), (1.00, (198, 160, 88))],
})
WARM = np.array((104, 92, 64), float)       # sun-faded / worn bark tint
QSTEP = 0.05                                # value quantisation -> flat painted clusters


def ramp(mat_arr, val):
    out = np.zeros(val.shape + (3,))
    for m, stops in RAMPS.items():
        sel = mat_arr == m
        if not sel.any():
            continue
        xs = np.array([s[0] for s in stops]); cs = np.array([s[1] for s in stops], float)
        v = np.clip(val[sel], 0, 1)
        out[sel] = np.stack([np.interp(v, xs, cs[:, c]) for c in range(3)], -1)
    return out


# ------------------------------------------------------------------ deterministic noise (world space, low frequency only)
def _hash3(ix, iy, iz, seed):
    h = (ix * 374761393 + iy * 668265263 + iz * 2147483647 + seed * 144665) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0


def vnoise(P, scale, seed):
    q = np.asarray(P, float).reshape(-1, 3) / scale
    i0 = np.floor(q).astype(np.int64); fr = q - i0; fr = fr * fr * (3 - 2 * fr)
    out = np.zeros(len(q))
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                hv = _hash3(i0[:, 0] + dx, i0[:, 1] + dy, i0[:, 2] + dz, seed)
                w = (fr[:, 0] if dx else 1 - fr[:, 0]) * (fr[:, 1] if dy else 1 - fr[:, 1]) * (fr[:, 2] if dz else 1 - fr[:, 2])
                out += hv * w
    return out.reshape(np.asarray(P).shape[:-1])


def hash2(u, v, seed):
    return _hash3(np.asarray(u, np.int64), np.asarray(v, np.int64), np.zeros_like(np.asarray(u, np.int64)), seed)


# ------------------------------------------------------------------ face context
class Face:
    """One face being painted. Arrays are (fh, fw)."""

    def __init__(self, node, face, fw, fh, L, W, n, edge_up, edge_front):
        self.node, self.face, self.fw, self.fh = node, face, fw, fh
        self.L, self.W, self.n = L, W, n
        vv, uu = np.mgrid[0:fh, 0:fw]
        self.u, self.v = uu + 0.5, vv + 0.5
        self.iu, self.iv = uu, vv
        self.mat = np.full((fh, fw), node.get("mat", BARK), int)
        self.val = np.zeros((fh, fw))
        self.alpha = np.ones((fh, fw), bool)
        self.warm = np.zeros((fh, fw))
        self.edge_up, self.edge_front = edge_up, edge_front   # per edge (top, bottom, left, right) world up / front-ness
        self.lockval = np.zeros((fh, fw), bool)

    # world helpers
    @property
    def x(self): return self.W[..., 0]
    @property
    def y(self): return self.W[..., 1]
    @property
    def z(self): return self.W[..., 2]
    @property
    def lx(self): return self.L[..., 0]
    @property
    def ly(self): return self.L[..., 1]
    @property
    def lz(self): return self.L[..., 2]

    def is_side(self):
        return abs(self.n[1]) < 0.7

    def facing(self, d, thr=0.6):
        return float(np.dot(self.n, d)) > thr


# ------------------------------------------------------------------ stamping primitives
def _shift(m, dv, du):
    out = np.zeros_like(m)
    H, W = m.shape
    ys = slice(max(dv, 0), H + min(dv, 0)); yd = slice(max(-dv, 0), H + min(-dv, 0))
    xs = slice(max(du, 0), W + min(du, 0)); xd = slice(max(-du, 0), W + min(-du, 0))
    out[ys, xs] = m[yd, xd]
    return out


def stamp(F, mask, mat=None, raise_=1.0, shadow=0.13, hl=0.15, lo=0.13, add=0.0, down=None):
    """Paint a raised shape: material, top/left bevel highlight, bottom/right bevel shade, drop shadow below it.
    'down' = texture direction of world-down on this face ((dv, du)); default from the face orientation."""
    mask = np.asarray(mask, bool) & F.alpha
    if not mask.any():
        return mask
    dv, du = down if down is not None else face_down(F)
    if mat is not None:
        F.mat[mask] = mat
        F.val[mask] = 0.0
    F.val[mask] += add
    up_n = _shift(mask, dv, du)          # mask moved down: texel whose UPPER neighbour is in mask
    dn_n = _shift(mask, -dv, -du)        # texel whose lower neighbour is in mask
    top_edge = mask & ~dn_n.astype(bool) if False else mask & ~_shift(mask, dv, du)
    bot_edge = mask & ~_shift(mask, -dv, -du)
    F.val[top_edge] += hl * raise_
    F.val[bot_edge] -= lo * raise_
    # side edges (perpendicular)
    pv, pu = du, dv
    side = mask & (~_shift(mask, pv, pu) | ~_shift(mask, -pv, -pu))
    F.val[side & ~top_edge & ~bot_edge] -= 0.03 * raise_
    # drop shadow just below, outside the mask
    if shadow:
        ds = up_n & ~mask & F.alpha
        F.val[ds] -= shadow * raise_
        ds2 = _shift(up_n, dv, du) & ~mask & ~ds & F.alpha
        F.val[ds2] -= shadow * 0.4 * raise_
    return mask


def face_down(F):
    """texture-space step (dv, du) that points most toward world-down on this face."""
    best, bd = (1, 0), -9
    for dv, du in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        iv0, iu0 = F.fh // 2, F.fw // 2
        iv1, iu1 = min(max(iv0 + dv, 0), F.fh - 1), min(max(iu0 + du, 0), F.fw - 1)
        if (iv1, iu1) == (iv0, iu0):
            continue
        d = F.W[iv0, iu0, 1] - F.W[iv1, iu1, 1]
        if d > bd:
            bd, best = d, (dv, du)
    if bd < 0.2:     # horizontal face: 'down' in texture = toward the front edge (closer to viewer) for top faces
        best2, bf = (1, 0), -9
        for dv, du in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            iv0, iu0 = F.fh // 2, F.fw // 2
            iv1, iu1 = min(max(iv0 + dv, 0), F.fh - 1), min(max(iu0 + du, 0), F.fw - 1)
            if (iv1, iu1) == (iv0, iu0):
                continue
            d = F.W[iv1, iu1, 2] - F.W[iv0, iu0, 2]
            if d > bf:
                bf, best2 = d, (dv, du)
        return best2
    return best


def rivet(F, cu, cv, mat=WOOD, size=2):
    """small round-ish stud centred at texel (cu, cv) (face texel coords, may be float)."""
    m = (np.abs(F.u - cu) < size / 2 + 0.01) & (np.abs(F.v - cv) < size / 2 + 0.01)
    stamp(F, m, mat, hl=0.3, lo=0.2, shadow=0.16)
    F.val[m] += 0.05
    return m


def stitches(F, line_mask, period=2, phase=0):
    """dashed thread along a 1-px line mask (alternate texels by u+v parity)."""
    m = line_mask & (((F.iu + F.iv + phase) % period) == 0) & F.alpha
    F.mat[m] = STITCH
    F.val[m] = 0.0
    F.lockval[m] = False
    return m


def lames(F, region, pitch, y_top=None, mat=None, axis="y", rim=0.17, line=0.24, grad=0.13, seam_world=None):
    """segmented (overlapping) plates: each segment light at its top, darker toward its bottom,
    a dark shadow line where the next plate tucks under, a bright rim on each plate's top edge.
    axis 'y' = world height; segments indexed from y_top downward."""
    region = np.asarray(region, bool) & F.alpha
    if not region.any():
        return
    coord = F.y if axis == "y" else axis(F)
    if y_top is None:
        y_top = coord[region].max() + 1e-3
    s = (y_top - coord) / pitch
    k = np.floor(s); f = s - k
    if mat is not None:
        F.mat[region] = mat
    F.val[region] += grad * (0.5 - f[region])
    px = 1.0 / pitch
    F.val[region & (f > 1 - px)] -= line
    F.val[region & (f < px) & (k > 0)] += rim
    F.val[region & (f >= px) & (f < 2 * px) & (k > 0)] += rim * 0.3


def tatter(F, depth=3, seed=1, edge="bottom", min_keep=0):
    """jagged torn hem: cut texels near the bottom edge (in world terms) with a deterministic ragged profile."""
    dv, du = face_down(F)
    if (dv, du) == (1, 0):
        dist = F.fh - F.v; col = F.iu
    elif (dv, du) == (-1, 0):
        dist = F.v; col = F.iu
    elif (dv, du) == (0, 1):
        dist = F.fw - F.u; col = F.iv
    else:
        dist = F.u; col = F.iv
    # profile per column (use world coords so neighbouring faces line up roughly)
    cw = np.round(F.x + F.z).astype(int)
    h = hash2(cw // 3, np.zeros_like(cw), seed)
    h2 = hash2(cw, np.ones_like(cw), seed + 7)
    cut = np.floor(h * (depth + 0.99)).astype(int)
    cut = np.where(h2 > 0.82, depth, cut)                      # occasional deep notch
    keep = dist > cut + min_keep
    edge_px = keep & ~(_shift(keep, -dv, -du) if True else keep)
    F.alpha &= keep
    # frayed darker edge on the remaining hem
    near = F.alpha & (dist <= cut + 1.0)
    F.val[near] -= 0.10
    return keep


def mottle(F, scale=7.0, amp=0.05, seed=3, levels=3):
    n = vnoise(F.W, scale, seed)
    q = np.round((n - 0.5) * 2 * (levels - 1) / 2) / max((levels - 1) / 2, 1)
    F.val += amp * q * (F.mat == F.node.get("mat", BARK))


def wear(F, amount=0.5, scale=5.0, seed=11, thr=0.64):
    """warm scuffed patches on leather (blobs, not grain)."""
    n = vnoise(F.W + 31.7, scale, seed)
    m = (n > thr) & np.isin(F.mat, [BARK, CLOTH, SAGE, UMBER, LODEN, SLATE])
    F.warm[m] = np.maximum(F.warm[m], amount * np.clip((n[m] - thr) / 0.12, 0.4, 1.0))
    return m


# ------------------------------------------------------------------ scrollwork (embossed / filigree motifs)
def scroll_mask(w, h, seed=0, mirror=True, turns=1.35, thick=1.0):
    """1-px line art of a symmetric pair of curling scrolls + stem, sized w x h texels."""
    m = np.zeros((h, w), bool)
    half = w / 2.0 if mirror else w
    def plot(x, y):
        ix, iy = int(round(x)), int(round(y))
        if 0 <= ix < w and 0 <= iy < h:
            m[iy, ix] = True
            if mirror:
                jx = int(round(w - 1 - x))
                if 0 <= jx < w:
                    m[iy, jx] = True
    rng = np.random.RandomState(seed)
    # main spiral: from the centre-bottom stem curling outward and up into a volute
    cx, cy = half * 0.52, h * 0.42
    R0 = min(half * 0.42, h * 0.36)
    for t in np.linspace(0, turns * 2 * math.pi, 400):
        r = R0 * (1 - t / (turns * 2 * math.pi + 1.2))
        plot(cx + r * math.cos(t + math.pi), cy - r * math.sin(t + math.pi) * 0.95)
    # stem from the volute to the centre line
    for t in np.linspace(0, 1, 120):
        x = (cx - R0) + (half - 1 - (cx - R0)) * t
        y = cy + R0 * 0.2 + (h * 0.88 - cy - R0 * 0.2) * (t ** 1.6)
        plot(x, y)
    # small leaf curl
    lx, ly, lr = half * 0.28, h * 0.78, min(half, h) * 0.14
    for t in np.linspace(0, 1.6 * math.pi, 80):
        r = lr * (1 - t / (1.9 * math.pi))
        plot(lx + r * math.cos(t), ly - r * math.sin(t))
    return m


def emboss(F, mask_local, u0, v0, raise_=1.0, mat=None, hl=0.12, lo=0.12):
    """raised tooling: mask_local (h, w) placed at texel (u0, v0)."""
    h, w = mask_local.shape
    big = np.zeros((F.fh, F.fw), bool)
    ys0, xs0 = int(v0), int(u0)
    for j in range(h):
        for i in range(w):
            if mask_local[j, i] and 0 <= ys0 + j < F.fh and 0 <= xs0 + i < F.fw:
                big[ys0 + j, xs0 + i] = True
    big &= F.alpha
    if mat is not None:
        F.mat[big] = mat
    F.val[big] += hl * raise_
    dv, du = face_down(F)
    sh = _shift(big, dv, du) & ~big & F.alpha
    F.val[sh] -= lo * raise_
    return big


# ------------------------------------------------------------------ compose
def base_light(F, ao):
    n = F.n
    v = 0.50 + 0.26 * n[1] + 0.07 * n[2] - 0.02 * abs(n[0])
    val = np.full((F.fh, F.fw), v)
    # gradient down every side face (relative to the face's own height range)
    if F.is_side():
        y = F.y; y0, y1 = y.min(), y.max()
        if y1 - y0 > 1:
            t = (y - y0) / (y1 - y0)
            val += 0.15 * (t - 0.5)
    # imaginary spotlight above the model: head/shoulders brighter, feet darker
    val += 0.10 * (F.y - 62) / 60.0
    val -= 0.34 * ao
    # rims: per edge, brightness by how much the edge faces up / front
    d = {"top": F.v, "bottom": F.fh - F.v, "left": F.u, "right": F.fw - F.u}
    for k, (eu, ef) in zip(("top", "bottom", "left", "right"), zip(F.edge_up, F.edge_front)):
        r1 = d[k] < 1.0
        r2 = (d[k] >= 1.0) & (d[k] < 2.0)
        amt = 0.03 + 0.15 * max(eu, 0) - 0.11 * max(-eu, 0) + 0.06 * max(ef, 0)
        val[r1] += amt
        val[r2] += amt * 0.25 if amt > 0 else amt * 0.2
    return val


def compose(F, base):
    v = base + F.val
    v = np.round(v / QSTEP) * QSTEP
    rgb = ramp(F.mat, v)
    w = np.clip(F.warm, 0, 1)[..., None]
    # warm wear keeps the texel's value (luminance-ish) but pulls hue toward WARM
    lum = rgb.mean(-1, keepdims=True)
    warm_col = WARM / WARM.mean() * lum
    rgb = rgb * (1 - w * 0.55) + warm_col * (w * 0.55)
    rgba = np.zeros((F.fh, F.fw, 4), np.uint8)
    rgba[..., :3] = np.clip(np.round(rgb), 0, 255).astype(np.uint8)
    rgba[..., 3] = np.where(F.alpha, 255, 0)
    return rgba
