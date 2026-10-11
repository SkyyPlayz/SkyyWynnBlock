"""SkyWynn Foraging armor - F3 tier builder (shared by every F3 tree: Gumboab, Dry, Bottletree, Palo). ORIGINAL; no vanilla
or Armory pixels.

PROGRESSION RULE (Skyy 2026-10-09: "Beautiful I want the armor sets consistent across the set, but each set should be a little
different visually, so they start simple and get a little cooler each set you get to that's better"):
same family + fit as F1 / F2. F3 = everything F2 has (ga_f2.py: pegs, shoulder caps, forked sap, belt boss, crest, knee
bosses) PLUS, exactly the same for every F3 tree (approved ladder: "F3 angular plates, bigger layered shoulders, a gorget,
sap glow up the arms"):
  1. ANGULAR plates: every tree's plate edges are angular (each tree its own angular cut), and the thin plates (breast plates,
     tassels, cheek guards, helmet back, bracer plates) get cut corners
  2. BIGGER, LAYERED shoulders: a wider pauldron + cap, a carved angular ridge on the cap, and a second lame under the first
  3. a GORGET: a taller neck guard ring + an angled front plate with a pointed (chevron) lower edge and a sap drop
  4. SAP GLOW UP THE ARMS: a glowing sap vein up the outside of each arm (bracer -> sleeve -> shoulder lame)
Room is left for F4 (thorns / spikes, tall pauldrons, glowing chest knot, double crest) and F5 (ornate, gold, the most impressive).
"""
import numpy as np
import ga_paint as P
from ga_paint import SAP, hash2
from ga_oak import _horiz
import ga_f2 as F2

TIER = "F3_Savanna"


# ------------------------------------------------------------------ shared angular plate / hem painters (tree gives the edge profile)
def profile_plates(F, region, pitch, seed, prof, step, T, y_top=None):
    """overlapping plate rows whose lower edges follow prof(hc, step) (depth in texels, angular per tree): dark shadow
    line under each edge, bevel above it, each plate its own tone."""
    region = np.asarray(region, bool) & F.alpha
    if not region.any():
        return
    if y_top is None:
        y_top = F.y[region].max() + 1e-3
    h = _horiz(F)
    row0 = np.floor((y_top - F.y) / pitch).astype(np.int64)
    off = np.where(row0 % 2 == 0, 0.0, step / 2.0)
    hc = np.mod(h + off, step)
    s_ = (y_top - F.y - prof(hc, step)) / pitch
    k = np.floor(s_); f = s_ - k
    ki = k.astype(np.int64)
    plate = np.floor((h + np.where(ki % 2 == 0, 0.0, step / 2.0)) / step).astype(np.int64)
    F.val[region] += ((hash2(plate, ki, seed + 3) - 0.5) * 0.10)[region] + 0.04 * (0.5 - f[region])
    dv, du = P.face_down(F)
    kd = np.roll(k, (-dv, -du), axis=(0, 1))
    under = region & (kd > k) & (k >= 0)
    F.mat[under] = T.DK
    F.val[under] = -0.05
    ku = np.roll(k, (dv, du), axis=(0, 1))
    bev = region & (ku < k) & (k > 0)
    F.mat[bev & (F.mat == T.DK)] = T.BARK
    F.val[bev] += 0.12


def profile_hem(F, seed, clip, prof, step, T, pmax):
    """angular hem: the bottom edge cut to the tree's profile, pale cut end-grain line along it."""
    if F.face not in ("front", "back", "left", "right"):
        return
    d = F.fh - F.v
    if F.face in ("front", "back") and clip:
        depth = pmax - prof(np.mod(F.u, step), step)
        F.alpha &= ~(d < depth)
        dd = d - depth
    else:
        dd = d
    m = (dd >= 0) & (dd < 1) & F.alpha
    F.mat[m] = T.WOOD
    F.val[m] -= 0.06


def chamfer(F, c, faces=("front", "back"), top=False):
    """tier 3: cut the lower (and optionally upper) corners of a thin plate at 45 degrees; dark edge line along the cut."""
    if F.face not in faces:
        return
    side = np.minimum(F.u, F.fw - F.u)
    for d in ([F.fh - F.v] + ([F.v] if top else [])):
        cut = (side + d) < c
        F.alpha &= ~cut
        edge = ((side + d) >= c) & ((side + d) < c + 1.2) & F.alpha
        F.val[edge] -= 0.08


def sap_vein(F, along, across, lo, hi, seed=0):
    """tier 3: glowing sap vein (wavy, small side forks every few texels) with a soft halo."""
    xc = 0.7 * np.sin((along - lo) * 0.5 + seed)
    m = (np.abs(across - xc) < 0.5) & (along > lo) & (along < hi)
    for k, b in enumerate(np.arange(lo + 2.5, hi - 1.0, 4.0)):
        dirn = 1 if k % 2 == 0 else -1
        t = along - b
        m |= (t > 0) & (t < 2.2) & (np.abs(across - (xc + dirn * (0.8 + t * 0.9))) < 0.5)
    m &= F.alpha
    h = (P._shift(m, 0, 1) | P._shift(m, 0, -1) | P._shift(m, 1, 0) | P._shift(m, -1, 0)) & ~m & F.alpha
    F.val[h] += 0.07
    F.warm[h] = 0
    F.mat[m] = SAP
    F.val[m] = 0.14
    F.lockval[m] = False
    return m


def mask_crown(F, mask, T, seed):
    """crown point cut to a hand-drawn silhouette (X), dark outline, lit centre line."""
    from ga_oak import _side_cut
    T.base(F, seed=seed, scars=False)
    if F.face in ("front", "back"):
        H, W = len(mask), len(mask[0])
        iv = np.clip((F.v / F.fh * H).astype(int), 0, H - 1)
        iu = np.clip((F.u / F.fw * W).astype(int), 0, W - 1)
        ch = np.array([list(r) for r in mask])[iv, iu]
        F.alpha &= ch == "X"
        a = F.alpha
        e = a & ~(P._shift(a, 0, 1) & P._shift(a, 0, -1) & P._shift(a, 1, 0))
        F.val[e] -= 0.16
        F.val[(np.abs(F.lx) < 0.5) & a] += 0.1
    else:
        _side_cut(F, F.fh * 0.6)


def _outer(F):
    """the arm face pointing away from the body."""
    return F.is_side() and F.face in ("left", "right") and F.n[0] * np.sign(F.x.mean()) > 0.7


def _wrap(old, *extra):
    def paint(F):
        old(F)
        for e in extra:
            e(F)
    return paint


# ------------------------------------------------------------------ build one F3 tree
def build(T):
    """T: an F2-style tree spec (see ga_f2.build) + PROF(hc, step), PROF_STEP, PROF_MAX (the tree's angular edge)."""
    pieces = F2.build(T)
    BARK, DK, WOOD, CLOTH = T.BARK, T.DK, T.WOOD, T.CLOTH

    def node(piece, name):
        for n in pieces[piece]:
            if n["name"] == name:
                return n
        raise KeyError(name)

    def wrap(piece, name, *extra, **upd):
        n = node(piece, name)
        n["paint"] = _wrap(n["paint"], *extra)
        n.update(upd)

    # 1. angular cut corners on the thin plates
    wrap("Chest", "R-Breast", lambda F: chamfer(F, 3.0))
    wrap("Chest", "R-Tassel", lambda F: chamfer(F, 3.0))
    wrap("Chest", "TasselBack", lambda F: chamfer(F, 3.0))
    wrap("Head", "HelmBack", lambda F: chamfer(F, 4.0))
    wrap("Head", "R-Cheek", lambda F: chamfer(F, 3.0, faces=("left", "right")))
    wrap("Hands", "R-BracerPlate", lambda F: chamfer(F, 2.5, faces=("left", "right"), top=True))

    # 2. bigger, layered shoulders
    def p_lame2(F):
        T.base(F, seed=19, scars=False)
        if F.is_side():
            F.mat[F.v < 1] = WOOD
            F.val[F.v < 1] -= 0.04
            T.hem(F, seed=19, clip=0)
        if _outer(F):
            sap_vein(F, F.ly, F.lz, -3.5, 3.5, seed=2)

    def p_fin(F):
        T.base(F, seed=27, scars=False)
        if F.face == "top":
            F2.sap_line_local(F, 0.0, axis="lx", along="lz", lo=-6.0, hi=6.0)
        elif F.face in ("left", "right"):
            # angular saw-tooth ridge: the top edge steps down toward both ends
            d = np.abs(F.lz)
            F.alpha &= ~((F.v < 1) & (d > 3.0))
            F.mat[F.v > F.fh - 1] = DK
            F.val[F.v > F.fh - 1] = 0.2
            F.val[F.v < 1] += 0.08
        elif F.face in ("front", "back"):
            F.mat[:] = WOOD
            F.val -= 0.05

    node("Chest", "R-Pauldron")["size"] = (15, 4, 18)
    node("Chest", "R-PauldronCap")["size"] = (11, 3, 15)
    wrap("Chest", "R-PauldronLame", lambda F: sap_vein(F, F.ly, F.lz, -3.5, 3.8, seed=1) if _outer(F) else None)
    pieces["Chest"] += [
        dict(name="R-PauldronFin", bone="R-Arm", parent="R-PauldronCap", pivot=(0.5, 2.0, 0), size=(2, 2, 12), mat=BARK,
             paint=p_fin, mirror=True),
        dict(name="R-PauldronLame2", bone="R-Arm", pivot=(-7.4, -1.6, -0.3), rot=(0, 0, -12), size=(2, 6, 14), mat=BARK,
             paint=p_lame2, mirror=True),
    ]

    # 3. gorget
    def p_gorget(F):
        T.base(F, seed=28, scars=False)
        if F.is_side():
            F.mat[F.v < 1] = WOOD
            F.val[F.v < 1] += 0.06
            F.mat[F.v > F.fh - 1] = DK
            F.val[F.v > F.fh - 1] = 0.2
            if F.face == "front":
                F2.pegs(F, [(-8.5, F.y.mean()), (8.5, F.y.mean())], T, r=0.7)
        elif F.face == "top":
            r = np.maximum(np.abs(F.lx) / 11.0, np.abs(F.lz) / 9.5)
            F.mat[r < 0.72] = CLOTH
            F.val[r < 0.72] -= 0.3

    def p_gorget_plate(F):
        T.base(F, seed=29, scars=False)
        if F.face == "front":
            cu = F.fw / 2.0
            depth = 3.0 * (1 - np.abs(F.u - cu) / cu)               # pointed (chevron) lower edge
            d = F.fh - F.v
            F.alpha &= ~(d < 3.0 - depth)
            dd = d - (3.0 - depth)
            rim = (dd >= 0) & (dd < 1) & F.alpha
            F.mat[rim] = WOOD
            F.val[rim] -= 0.04
            F.mat[F.v < 1] = WOOD
            F.val[F.v < 1] += 0.06
            gem = (np.abs(F.u - cu) + np.abs(F.v - 2.5) < 1.6) & F.alpha
            F.mat[gem] = SAP
            F.val[gem] = 0.2
            F.lockval[gem] = False
            h = (P._shift(gem, 0, 1) | P._shift(gem, 0, -1) | P._shift(gem, 1, 0) | P._shift(gem, -1, 0)) & ~gem & F.alpha
            F.val[h] += 0.06
            F2.pegs(F, [(-5.5, F.y.max() - 1.5), (5.5, F.y.max() - 1.5)], T, r=0.7)
        elif F.face in ("left", "right"):
            F.alpha &= F.v < 2
        else:
            F.val -= 0.1

    c = node("Chest", "Collar")
    c.update(size=(22, 4, 19), pivot=(0, 12.3, -0.3), mat=BARK, paint=p_gorget)
    pieces["Chest"].append(dict(name="GorgetPlate", bone="Chest", pivot=(0, 8.8, 12.6), rot=(-8, 0, 0), size=(16, 6, 2),
                                mat=BARK, paint=p_gorget_plate))

    # 4. sap glow up the arms (bracer -> sleeve -> lames)
    # (on the outer face AND on the front face near the outer edge, so it reads from the front)
    def arm_sap(lo, hi, seed, edge):
        def paint(F):
            if _outer(F):
                sap_vein(F, F.ly, F.lz, lo, hi, seed=seed)
            elif F.face == "front":
                sap_vein(F, F.ly, F.lx + edge, lo, hi, seed=seed + 5)
        return paint
    wrap("Hands", "R-Bracer", arm_sap(-6.5, 6.8, 3, 2.6))
    wrap("Hands", "R-BracerPlate", lambda F: sap_vein(F, F.ly, F.lz, -5.0, 5.0, seed=6) if _outer(F) else None)
    wrap("Chest", "R-Sleeve", arm_sap(-11.0, 4.0, 4, 2.6))
    return pieces
