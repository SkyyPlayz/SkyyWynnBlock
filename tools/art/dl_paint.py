"""Painting engine for the SkyWynn Dark Leather armor textures (original procedural hand-painted style).

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
LEATHER, CLOTH, STRAP, AMBER, SASH, IRON, GEM, VOID, STITCH = range(9)
MAT_NAMES = ["leather", "cloth", "strap", "amber", "sash", "iron", "gem", "void", "stitch"]
RAMPS = {
    LEATHER: [(0.00, (21, 18, 29)), (0.20, (31, 27, 39)), (0.35, (41, 36, 49)), (0.50, (53, 47, 60)),
              (0.65, (67, 59, 72)), (0.80, (87, 76, 88)), (1.00, (124, 106, 114))],
    CLOTH: [(0.00, (18, 18, 42)), (0.20, (26, 26, 58)), (0.35, (34, 34, 74)), (0.50, (44, 44, 92)),
            (0.65, (57, 56, 110)), (0.80, (73, 71, 130)), (1.00, (100, 96, 154))],
    STRAP: [(0.00, (40, 22, 24)), (0.20, (58, 34, 30)), (0.35, (78, 47, 36)), (0.50, (98, 62, 43)),
            (0.65, (120, 78, 51)), (0.80, (146, 98, 62)), (1.00, (182, 132, 86))],
    AMBER: [(0.00, (88, 32, 22)), (0.20, (126, 50, 22)), (0.35, (162, 74, 22)), (0.50, (196, 102, 28)),
            (0.65, (222, 134, 38)), (0.80, (240, 170, 62)), (1.00, (252, 218, 140))],
    SASH: [(0.00, (92, 36, 24)), (0.20, (126, 54, 26)), (0.35, (156, 76, 28)), (0.50, (186, 100, 36)),
           (0.65, (208, 124, 46)), (0.80, (226, 150, 64)), (1.00, (240, 186, 108))],
    IRON: [(0.00, (26, 24, 38)), (0.20, (40, 38, 55)), (0.35, (56, 54, 73)), (0.50, (75, 73, 94)),
           (0.65, (99, 97, 118)), (0.80, (132, 130, 150)), (1.00, (180, 178, 194))],
    GEM: [(0.00, (108, 26, 14)), (0.30, (174, 54, 14)), (0.50, (218, 94, 20)), (0.70, (244, 148, 40)),
          (0.85, (252, 194, 88)), (1.00, (254, 234, 178))],
    VOID: [(0.00, (16, 13, 25)), (0.50, (24, 20, 37)), (1.00, (44, 37, 60))],
    STITCH: [(0.00, (60, 50, 54)), (0.50, (96, 83, 80)), (1.00, (136, 118, 106))],
}
WARM = np.array((104, 66, 46), float)       # worn / scuffed leather tint (ref 1's orange-brown wear)
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
        self.mat = np.full((fh, fw), node.get("mat", LEATHER), int)
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


def rivet(F, cu, cv, mat=AMBER, size=2):
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
    F.val += amp * q * (F.mat == F.node.get("mat", LEATHER))


def wear(F, amount=0.5, scale=5.0, seed=11, thr=0.64):
    """warm scuffed patches on leather (blobs, not grain)."""
    n = vnoise(F.W + 31.7, scale, seed)
    m = (n > thr) & np.isin(F.mat, [LEATHER])
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
