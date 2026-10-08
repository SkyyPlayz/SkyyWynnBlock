"""SkyWynn Dark Leather light armor - geometry + paint design (ORIGINAL; no vanilla geometry or pixels).

Brief (Skyy): "a light armor set out of dark leather based off the first image, but with the half plate. Armor type
(single shoulder.) and that helmet style."
 - ref 1: dark violet-charcoal leather, navy cloth + tattered tabard, brown straps / belts / buckles, amber accents
 - ref 2: HALF PLATE chest form, but ONE pauldron (LEFT shoulder by default; right shoulder = just a strap)
 - ref 3: closed knight helm: tall crest rising to a spike, V brow + diamond gem, swept side fins, crown spikes,
          dark face guard with a V opening and vertical grille bars

Node spec (all numbers in Hytale character units, 64 = 1 block; sizes are integers so UVs = face size exactly):
  name, bone (player bone the piece attaches to), pivot (rel. bone BOX CENTRE, or rel. parent node centre),
  rot (euler deg, ZYX like the plugin), size (w,h,d) | quad (w,h), offset (box centre rel. pivot), stretch,
  mat (base material), paint (decorations), skip (faces left out = never visible), double (double sided),
  parent (optional node in the same piece), mirror (True -> an L- copy is generated: x mirrored, texture shared)
"""
import math
import numpy as np
import dl_paint as P
from dl_paint import (LEATHER, CLOTH, STRAP, AMBER, SASH, IRON, GEM, VOID, STITCH,
                      stamp, rivet, stitches, lames, tatter, mottle, wear, emboss, scroll_mask)

# ------------------------------------------------------------------ shared paint helpers
def seg_dist(F, a, b):
    """distance in world XY from each texel to segment a-b (front/back strap lines)."""
    a = np.array(a, float); b = np.array(b, float)
    p = np.stack([F.x, F.y], -1)
    ab = b - a
    t = np.clip(((p - a) @ ab) / (ab @ ab), 0, 1)
    q = a + t[..., None] * ab
    return np.linalg.norm(p - q, axis=-1)


STRAP_A = ((10.5, 92.0), (-11.0, 59.0))     # left shoulder (pauldron side) -> right hip
STRAP_B = ((-10.5, 92.0), (11.0, 59.0))     # right shoulder (brace side) -> left hip
RING = (0.0, 75.9)                          # where the two straps cross


def chest_straps(F, ring=True, width=4.0):
    """the crossed brown straps of ref 1, painted in world space so they run across every chest box."""
    if abs(F.n[2]) < 0.5:
        return
    for a, b in (STRAP_A, STRAP_B):
        d = seg_dist(F, a, b)
        m = d < width / 2
        stamp(F, m, STRAP, hl=0.16, lo=0.14, shadow=0.16)
        F.val[m & (d < 0.5)] -= 0.07
    if ring:
        r = np.hypot(F.x - RING[0], F.y - RING[1])
        ringm = (r < 3.2) & (r > 1.6)
        stamp(F, ringm, IRON, hl=0.3, lo=0.2, shadow=0.18)
        F.val[ringm & (F.y > RING[1] + 1.5)] += 0.15
        inner = r <= 1.6
        F.mat[inner] = STRAP; F.val[inner] = -0.12


def leather_base(F, wear_amt=0.45, seed=0):
    mottle(F, scale=6.5, amp=0.045, seed=3 + seed)
    wear(F, amount=wear_amt, scale=4.5, seed=11 + seed, thr=0.70)


def cloth_base(F, pitch=4, seed=0, wear_amt=0.35):
    """navy cloth: soft vertical folds (flat steps), darker toward the hem, a few warm stains."""
    if F.is_side():
        coord = F.x * abs(F.n[2]) + F.z * abs(F.n[0])
        ph = np.sin(2 * math.pi * coord / pitch + seed)
        F.val += 0.05 * np.round(ph * 1.5) / 1.5
    mottle(F, scale=8, amp=0.03, seed=21 + seed)
    m = wear(F, amount=wear_amt, scale=5.0, seed=17 + seed, thr=0.74)


def trim_edge(F, which, mat=AMBER, width=1, hl=0.22):
    """metal / leather trim strip along a face edge in texture space: 'top','bottom','left','right'."""
    m = {"top": F.v < width, "bottom": F.v > F.fh - width, "left": F.u < width, "right": F.u > F.fw - width}[which]
    stamp(F, m & F.alpha, mat, hl=hl, lo=0.16, shadow=0.14)
    return m


def band_y(F, y0, y1, mat=STRAP, stitch=True, local=True):
    """horizontal band around a box between local (or world) heights y0..y1."""
    y = F.ly if local else F.y
    m = (y > y0) & (y < y1)
    if not m.any():
        return m
    stamp(F, m, mat, hl=0.18, lo=0.15, shadow=0.16)
    if stitch and (y1 - y0) >= 3:
        s = m & ((np.abs(y - (y1 - 1.0)) < 0.5) | (np.abs(y - (y0 + 1.0)) < 0.5))
        stitches(F, s, period=2)
    return m


def buckle(F, cu, cv, w=5, h=4, frame=IRON, prong=AMBER):
    """painted buckle: iron frame + amber prong, strap visible inside."""
    u0, v0 = cu - w / 2, cv - h / 2
    outer = (F.u > u0) & (F.u < u0 + w) & (F.v > v0) & (F.v < v0 + h)
    inner = (F.u > u0 + 1) & (F.u < u0 + w - 1) & (F.v > v0 + 1) & (F.v < v0 + h - 1)
    stamp(F, outer & ~inner, frame, hl=0.32, lo=0.2, shadow=0.18)
    pr = inner & (np.abs(F.u - cu) < 0.51)
    stamp(F, pr, prong, hl=0.25, lo=0.1, shadow=0.0)
    return outer


def scroll_on(F, u0, v0, w, h, seed=0, raise_=1.0, mat=None, hl=0.12, lo=0.12):
    if w < 4 or h < 4:
        return
    emboss(F, scroll_mask(int(w), int(h), seed=seed), u0, v0, raise_=raise_, mat=mat, hl=hl, lo=lo)


def taper_top(F, top, length, half_w, axis="x"):
    """pointed tip: above (top - length) keep only |local axis| <= half_w * (top - ly) / length."""
    ly = F.ly
    c = F.lx if axis == "x" else F.lz
    zone = ly > top - length
    allow = half_w * (top - ly) / length + 0.35
    F.alpha &= ~(zone & (np.abs(c) > allow))


# ================================================================== HEAD (helm after ref 3)
# Stepped shell (Helm > HelmUpper > HelmDome > HelmCap) gives the rounded, tapering closed-helm silhouette in cubes.
# Face: amber V brow, faceted diamond gem in an iron bezel, dark eye band + grille stem = T/V visor, trimmed cheeks.
# Top: tall notched amber crest rising to a spike + ridge; two-segment swept fins; twin-prong crown spikes.

def profile_cut(F, inside, tol=0.35):
    """keep only texels whose local point lies inside the 2D/3D profile (alpha cut-out shapes on boxes)."""
    F.alpha &= inside(F.L[..., 0], F.L[..., 1], F.L[..., 2], tol)


def p_helm(F):
    leather_base(F, 0.35, seed=1)
    f = F.face
    if f == "front":
        ax = np.abs(F.lx)
        y = F.ly - 3.5                                    # head-centre height (box centre sits at -3.5)
        brow_low = 3.6 + (ax - 8.0) * 0.532 - 2.27
        eye = (ax < 11.6) & (y < brow_low + 0.6) & (y > -6.2)
        stem = (ax < 5.8) & (y <= -6.2)
        void = eye | stem
        F.mat[void] = VOID
        F.val[void] = -0.12 + 0.08 * (y[void] > brow_low[void] - 1.2)     # faint light catching under the brow
        # thin amber frame around the eye band (ref 3's gold visor outline)
        edge = ~void & (P._shift(void, 1, 0) | P._shift(void, -1, 0) | P._shift(void, 0, 1) | P._shift(void, 0, -1))
        stamp(F, edge & (y < brow_low - 0.5), AMBER, hl=0.2, lo=0.12, shadow=0.1)
    elif f in ("left", "right"):
        trim_edge(F, "bottom", AMBER, 1)
        for zz in (-11, -1, 9):
            pts = (F.lz > zz - 1) & (F.lz < zz + 1) & (np.abs(F.ly + 9.0) < 1)
            if pts.any():
                rivet(F, F.u[pts].mean(), F.v[pts].mean(), AMBER)
        stitches(F, np.abs(F.ly - 9.5) < 0.5, period=2)
        r = np.hypot(F.lz - 0.5, F.ly + 1.0)              # ear boss
        stamp(F, r < 5.0, None, hl=0.16, lo=0.14, shadow=0.15, add=0.05)
        F.val[(r < 5.0) & (r > 3.8)] -= 0.04
        stamp(F, r < 1.6, AMBER, hl=0.28, lo=0.18, shadow=0.15)
    elif f == "back":
        lames(F, F.ly < 3.0, 4.0, y_top=None)
        for yy in (-1.0, -5.0, -9.0):
            for sx in (-12.5, 12.5):
                rivet(F, *_uv_of(F, (sx, yy, -16.0)), AMBER)
        stamp(F, (np.abs(F.lx) < 1.5) & (F.ly > 3.0), None, hl=0.16, lo=0.12, shadow=0.12, add=0.06)
        trim_edge(F, "bottom", AMBER, 1)


def p_helm_upper(F):
    leather_base(F, 0.4, seed=23)
    if F.is_side():
        trim_edge(F, "bottom", AMBER, 1)
        if F.face in ("front", "back"):
            for sx in (-11, 11):
                rivet(F, F.fw / 2 + sx, 3.6, AMBER, size=1)
    elif F.face == "top":
        F.val -= 0.04


def p_dome_helm(F):
    leather_base(F, 0.4, seed=22)
    if F.face == "top":
        for sx in (-8.8, 8.8):
            stamp(F, np.abs(F.lx - sx) < 0.5, None, hl=-0.1, lo=0.0, shadow=0.0, add=-0.14)
        for sx in (-10, 10):
            for z in (-7, 5):
                rivet(F, *_uv_of(F, (sx, 2, z)), AMBER, size=1)
    elif F.is_side():
        F.val[F.v > F.fh - 1] -= 0.12


def p_helm_cap(F):
    leather_base(F, 0.45, seed=24)
    if F.is_side():
        F.val[F.v > F.fh - 1] -= 0.12
        if F.face in ("left", "right"):
            for k in (3, F.fw - 3):
                rivet(F, k, 1.5, AMBER, size=1)


def p_faceguard(F):
    if F.face == "front":
        F.val += -0.06
        core = (F.u > 1) & (F.u < F.fw - 1) & (F.v > 1) & (F.v < F.fh - 1)
        slot = core & ((F.iu % 2) == 0)
        F.mat[slot] = VOID; F.val[slot] = -0.08
        bars = core & ~slot
        stamp(F, bars, IRON, hl=0.3, lo=0.12, shadow=0.0, add=-0.08)
        frame = ~core
        stamp(F, frame, AMBER, hl=0.22, lo=0.14, shadow=0.1)
    elif F.face == "top":
        F.val -= 0.12
    elif F.face in ("left", "right", "bottom"):
        F.mat[:] = AMBER; F.val -= 0.1


def p_cheek(F):
    leather_base(F, 0.3, seed=2)
    inner = F.lx                                          # +x = toward the face centre for the right cheek
    jaw = lambda ly: 3.5 - (ly + 8.5) * 0.6               # diagonal jaw cut on the inner-bottom corner
    if F.face == "front":
        cut = (F.ly < -3.0) & (inner > jaw(F.ly))
        F.alpha &= ~cut
        trim = F.alpha & ((inner > 2.0) | (inner > jaw(F.ly) - 1.3) & (F.ly < -3.0) | (F.v > F.fh - 1.5))
        stamp(F, trim, AMBER, hl=0.24, lo=0.16, shadow=0.15)
        rivet(F, *_uv_of(F, (-1.2, 5.0, 1.5)), AMBER, size=1)
    elif F.face in ("left", "right", "back", "bottom"):
        if F.face == "right":
            F.alpha &= ~(F.ly < -3.0)
        trim_edge(F, "bottom", AMBER, 1)


def p_brow(F):
    F.val += 0.04
    if F.face == "front":
        F.val[np.abs(F.ly) < 0.5] -= 0.22                  # engraved centre groove
        F.val[np.abs(F.ly - 1) < 0.5] += 0.08
        F.val[(F.u < 1.5) | (F.u > F.fw - 1.5)] += 0.06
        F.val[F.v < 1] += 0.1                              # lit top edge
    elif F.face == "top":
        F.val += 0.12
    elif F.face == "bottom":
        F.val -= 0.14


def p_gem(F):
    """faceted diamond in a dark iron bezel; box is rolled 45 deg so local +y edge = upper-left on screen."""
    if F.face == "front":
        ax, ay = F.lx, F.ly
        h = F.fw / 2
        bezel = (np.abs(ax) > h - 1.0) | (np.abs(ay) > h - 1.0)
        F.mat[bezel] = IRON
        F.val[bezel] = 0.05
        F.val[bezel & ((ay > h - 1.0) | (ax < -(h - 1.0)))] += 0.12
        g = ~bezel
        F.mat[g] = GEM
        up_l = g & (ay >= np.abs(ax))      # upper-left facet  (lit)
        up_r = g & (ax > np.abs(ay))       # upper-right facet
        lo_l = g & (-ax >= np.abs(ay))     # lower-left
        lo_r = g & (-ay > np.abs(ax))      # lower-right (shadow)
        F.val[up_l] = 0.32; F.val[up_r] = 0.16; F.val[lo_l] = -0.02; F.val[lo_r] = -0.16
        table = g & (np.abs(ax) < 1.1) & (np.abs(ay) < 1.1)
        F.val[table] = 0.24
        glint = g & (np.abs(ax + 0.6) < 0.6) & (np.abs(ay - 1.5) < 0.6)
        F.val[glint] = 0.6
    else:
        F.mat[:] = IRON
        F.val += 0.05 if F.face in ("top", "left") else -0.05


def crest_hw(t):
    """half-width of the crest blade along its length t=0 (base, behind the gem) .. 1 (spike tip).
    Full width (3) most of the way so the blade has solid sides; jagged notches cut in; tapers to the spike."""
    hw = np.full(t.shape, 3.0)
    hw = np.where(t <= 0.08, 2.2, hw)
    hw = np.where((t > 0.30) & (t <= 0.36), 2.0, hw)     # notches (ref 3's jagged crest edge)
    hw = np.where((t > 0.50) & (t <= 0.56), 2.0, hw)
    sp = t > 0.64
    hw = np.where(sp, 3.0 - (t - 0.64) / 0.36 * 2.7, hw)
    return hw


def p_crest_front(F):
    H = F.L  # local
    t = (F.ly + 13.5) / 27.0
    hw = crest_hw(t)
    if F.face in ("front", "back"):
        F.alpha &= np.abs(F.lx) <= hw + 0.3
        e = F.alpha & (np.abs(F.lx) > hw - 0.9)
        F.val[e & (F.lx < 0)] += 0.16                     # lit left edge
        F.val[e & (F.lx > 0)] -= 0.12
        groove = (np.abs(F.lx) < 0.5) & (t < 0.86)
        F.val[groove] -= 0.24
        F.val[(np.abs(F.lx + 1.0) < 0.5) & (t < 0.86)] += 0.08
        F.val[t > 0.9] += 0.12                             # bright spike tip
        if F.face == "back":
            F.val -= 0.1
    elif F.face in ("left", "right"):
        F.alpha &= hw >= 2.95                              # sides exist where the blade is full width
        F.val -= 0.08
    else:
        F.alpha[:] = False


def p_crest(F):
    leather_base(F, 0.25, seed=4)
    if F.face == "top":
        stamp(F, np.abs(F.lx) < 1.0, AMBER, hl=0.22, lo=0.12, shadow=0.1)
    elif F.face in ("left", "right"):
        F.val[(np.round(F.lz) % 4 == 0)] -= 0.1
        trim_edge(F, "top", AMBER, 1)
    elif F.face == "back":
        F.val -= 0.06


def _fin_root_inside(x, y, z, tol):
    low = -4.0 + (6.0 - z) / 12.0 * 5.0                  # bottom edge rises toward the back
    top = 4.0 - np.where(np.abs(z - 0.5) < 1.6, 1.8 - np.abs(z - 0.5), 0.0)   # one jagged notch on top
    front = ~((z > 3.5) & (y > 4.0 - (z - 3.5) * 1.6))   # pointed front corner
    return (y >= low - tol) & (y <= top + tol) & front


def _fin_tip_inside(x, y, z, tol):
    low = -3.0 + (5.5 - z) / 11.0 * 4.6                  # tapers to a point at the back-top
    notch = (np.abs(z - 0.5) < 1.4) & (y < low + 1.4 - np.abs(z - 0.5))
    return (y >= low - tol) & (y <= 3.0 + tol) & ~notch


def _fin_paint(F, inside):
    profile_cut(F, inside)
    if F.face in ("left", "right"):
        F.val += 0.04
        line = (np.abs(F.ly - 0.6 + (5.5 - F.lz) * 0.12) < 0.5) & F.alpha
        F.val[line] -= 0.22                               # engraved groove along the blade
        F.val[F.v < 1] += 0.1
    elif F.face == "top":
        F.val += 0.12
    elif F.face in ("bottom", "back"):
        F.val -= 0.12


def p_fin(F):
    _fin_paint(F, _fin_root_inside)
    if F.face in ("left", "right"):
        rivet(F, *_uv_of(F, (0, -0.5, 4.0)), IRON, size=1)


def p_fin_tip(F):
    _fin_paint(F, _fin_tip_inside)


def _spike_inside(x, y, z, tol):
    def prong(c, top):
        hw = np.clip(1.25 * (top - y) / (top + 5.0), 0, None)
        return (np.abs(x - c) <= hw + tol) & (y <= top + tol)
    return prong(-1.2, 5.0) | prong(1.3, 1.5)


def p_spike(F):
    profile_cut(F, _spike_inside, tol=0.3)
    if F.face == "top":
        F.alpha[:] = False
    F.val[F.ly > 2.0] += 0.1
    stamp(F, F.ly < -3.6, AMBER, hl=0.2, lo=0.1, shadow=0.0)


def _uv_of(F, lp):
    """texel coords on this face nearest to a local point (for placing rivets in local space)."""
    d = np.linalg.norm(F.L - np.array(lp, float), axis=-1)
    i = np.unravel_index(np.argmin(d), d.shape)
    return F.u[i], F.v[i]


# ---------------------------------------------------------------- LIGHT helm (Skyy: "slim it up and scale it down")
# One close-fitting leather shell (0.5 off the head) + a low cap; the ref-3 face is PAINTED on the shell (dark T/V
# visor, grille bars, amber frame) so it adds no bulk. Small V brow + gem, slim crest spike, small swept fins.

def p_helm_light(F):
    leather_base(F, 0.35, seed=1)
    f = F.face
    if f == "front":
        ax = np.abs(F.lx); y = F.ly
        brow_c = 3.0 + (ax - 5.6) * 0.532
        brow_low = brow_c - 1.7
        eye = (ax < 10.4) & (y < brow_low + 0.5) & (y > -3.4)
        stem = (ax < 3.4) & (y <= -3.4) & (y > -11.4)
        void = eye | stem
        F.mat[void] = VOID
        F.val[void] = -0.12 + 0.08 * (y[void] > brow_low[void] - 1.0)
        bars = stem & (y < -5.6) & ((F.iu % 2) == 1)
        stamp(F, bars, IRON, hl=0.28, lo=0.1, shadow=0.0, add=-0.08)
        edge = ~void & (P._shift(void, 1, 0) | P._shift(void, -1, 0) | P._shift(void, 0, 1) | P._shift(void, 0, -1))
        stamp(F, edge & (y < brow_low - 0.4), AMBER, hl=0.2, lo=0.12, shadow=0.1)
        trim_edge(F, "bottom", AMBER, 1)
        for sx in (-12.5, 12.5):
            rivet(F, *_uv_of(F, (sx, -10.5, 15)), AMBER, size=1)
    elif f in ("left", "right"):
        trim_edge(F, "bottom", AMBER, 1)
        stitches(F, np.abs(F.ly - 9.5) < 0.5, period=2)
        r = np.hypot(F.lz - 0.5, F.ly + 1.0)              # small ear boss
        stamp(F, r < 3.6, None, hl=0.16, lo=0.14, shadow=0.15, add=0.05)
        stamp(F, r < 1.1, AMBER, hl=0.28, lo=0.18, shadow=0.15)
    elif f == "back":
        lames(F, F.ly < -1.0, 4.0, y_top=None)
        stamp(F, (np.abs(F.lx) < 1.0) & (F.ly > -1.0), None, hl=0.16, lo=0.12, shadow=0.12, add=0.06)
        trim_edge(F, "bottom", AMBER, 1)
    elif f == "top":
        for sx in (-8.0, 8.0):
            stamp(F, np.abs(F.lx - sx) < 0.5, None, hl=-0.1, lo=0.0, shadow=0.0, add=-0.12)


def p_helm_cap_light(F):
    leather_base(F, 0.45, seed=24)
    if F.is_side():
        trim_edge(F, "bottom", AMBER, 1)
    elif F.face == "top":
        stamp(F, np.abs(F.lx) < 0.6, None, hl=0.12, lo=0.1, shadow=0.1, add=0.05)


def crest_hw_light(t):
    """slim crest: full width (2) most of the way, two jagged notches, tapering to the spike."""
    hw = np.full(t.shape, 2.0)
    hw = np.where(t <= 0.08, 1.5, hw)
    hw = np.where((t > 0.30) & (t <= 0.37), 1.3, hw)
    hw = np.where((t > 0.50) & (t <= 0.57), 1.3, hw)
    sp = t > 0.62
    return np.where(sp, 2.0 - (t - 0.62) / 0.38 * 1.75, hw)


def p_crest_light(F):
    t = (F.ly + 10.0) / 20.0
    hw = crest_hw_light(t)
    if F.face in ("front", "back"):
        F.alpha &= np.abs(F.lx) <= hw + 0.3
        e = F.alpha & (np.abs(F.lx) > hw - 0.9)
        F.val[e & (F.lx < 0)] += 0.16
        F.val[e & (F.lx > 0)] -= 0.12
        F.val[(np.abs(F.lx) < 0.5) & (t < 0.8)] -= 0.2
        F.val[t > 0.88] += 0.12
        if F.face == "back":
            F.val -= 0.1
    elif F.face in ("left", "right"):
        F.alpha &= hw >= 1.95
        F.val -= 0.08
    else:
        F.alpha[:] = False


def _fin_light_inside(x, y, z, tol):
    low = -2.5 + (5.0 - z) / 10.0 * 3.8                  # bottom edge sweeps up toward the back tip
    top = 2.5
    front = ~((z > 3.0) & (y > 2.5 - (z - 3.0) * 1.5))
    return (y >= low - tol) & (y <= top + tol) & front


def p_fin_light(F):
    _fin_paint(F, _fin_light_inside)


HEAD = [
    dict(name="Helm", bone="Head", pivot=(0, 0.0, 0.0), size=(31, 29, 30), mat=LEATHER, paint=p_helm_light,
         skip=("bottom",)),
    dict(name="HelmCap", bone="Head", pivot=(0, 15.25, -0.5), size=(23, 2, 23), stretch=(1, 0.75, 1), mat=LEATHER,
         paint=p_helm_cap_light, skip=("bottom",)),
    dict(name="BrowR", bone="Head", pivot=(-5.6, 3.0, 15.6), rot=(0, 0, -28), size=(12, 3, 2), mat=AMBER,
         paint=p_brow, skip=("back",), mirror=True),
    dict(name="Gem", bone="Head", pivot=(0, 4.4, 16.9), rot=(0, 0, 45), size=(6, 6, 2), stretch=(1, 1, 0.8), mat=GEM,
         paint=p_gem, skip=("back",)),
    dict(name="CrestFront", bone="Head", pivot=(0, 5.0, 15.6), rot=(-4, 0, 0), size=(4, 20, 2), offset=(0, 10.0, 0),
         stretch=(1, 1, 0.75), mat=AMBER, paint=p_crest_light, skip=("bottom", "top"), double=True),
    dict(name="FinR", bone="Head", pivot=(-15.6, 5.0, 8.0), rot=(14, 8, 0), size=(2, 5, 10), offset=(-0.2, 0, -5.0),
         mat=AMBER, paint=p_fin_light, double=True, mirror=True),
]


# ================================================================== CHEST (half plate, one LEFT pauldron)
def p_cuirass(F):
    leather_base(F, 0.5, seed=5)
    if F.face in ("front", "back"):
        chest_straps(F, ring=(F.face == "front"))
        if F.face == "back":
            scroll_on(F, F.fw / 2 - 6, 3, 12, 8, seed=5, raise_=0.6)
    elif F.face in ("left", "right"):
        # side lacing (a classic leather cue)
        seam = np.abs(F.lz - 0) < 0.5
        F.val[seam] -= 0.18
        lace = (np.abs(np.abs(F.lz) - ((F.iv % 4) * 0.5)) < 0.5) & (F.ly < 9) & (F.ly > -10) & (np.abs(F.lz) < 2.1)
        stitches(F, lace, period=1)
    elif F.face == "top":
        F.val -= 0.02


def p_breast(F):
    leather_base(F, 0.6, seed=6)
    if F.face == "front":
        c = F.fw / 2
        # painted volume of a shaped half-plate breastplate: two rounded chest lobes either side of a medial ridge
        for cx in (c - 6.5, c + 6.5):
            r = np.hypot((F.u - cx) / 7.0, (F.v - 4.5) / 5.5)
            F.val += 0.13 * np.clip(1 - r, 0, 1) - 0.05 * ((r > 1.0) & (r < 1.35))
        F.val[np.abs(F.u - c + 0.5) < 0.5] += 0.15
        F.val[np.abs(F.u - c - 0.5) < 0.5] -= 0.10
        F.val[F.v < 1] += 0.08
        scroll_on(F, 2, 1, 8, 6, seed=7, raise_=0.7)
        scroll_on(F, F.fw - 10, 1, 8, 6, seed=7, raise_=0.7)
    if F.is_side():
        trim_edge(F, "bottom", AMBER, 1)
    chest_straps(F)


def p_breast_low(F):
    leather_base(F, 0.6, seed=26)
    if F.face == "front":
        c = F.fw / 2
        F.val[np.abs(F.u - c + 0.5) < 0.5] += 0.13
        F.val[np.abs(F.u - c - 0.5) < 0.5] -= 0.09
        F.val += 0.06 * np.clip(1 - np.abs(F.u - c) / 10, 0, 1)
    if F.is_side():
        trim_edge(F, "bottom", AMBER, 1)
    chest_straps(F)


def p_gorget(F):
    leather_base(F, 0.3, seed=7)
    if F.face in ("front", "left", "right", "back"):
        trim_edge(F, "top", AMBER, 1)
        if F.face == "front":
            for cu in (2.5, F.fw - 2.5):
                rivet(F, cu, 1.8, AMBER, size=1)
    elif F.face == "top":
        r = np.maximum(np.abs(F.lx) / 10, np.abs(F.lz) / 8.5)
        F.val -= 0.25 * (r < 0.75)


def p_plackart(F):
    leather_base(F, 0.5, seed=8)
    lames(F, F.alpha, 5.6, y_top=72.0)
    if F.face in ("front", "back"):
        chest_straps(F, ring=False)
        for sx in (-12.5, 12.5):
            for yy in (72 - 5.6 - 0.5 - 1.2,):
                m = (np.abs(F.x - sx) < 1) & (np.abs(F.y - yy) < 1)
                if m.any():
                    rivet(F, F.u[m].mean(), F.v[m].mean(), AMBER)


def p_belt(F):
    F.val += 0.0
    if F.is_side():
        F.val[np.abs(F.v - F.fh / 2) < 0.5] -= 0.08
        F.val[F.v < 1] += 0.08
        for k in range(4, F.fw - 3, 10):
            rivet(F, k + 0.5, F.fh / 2, AMBER)
        if F.face == "front":
            for k in range(3):
                hole = (np.abs(F.u - (F.fw / 2 + 7 + 2 * k)) < 0.5) & (np.abs(F.v - F.fh / 2) < 0.5)
                F.mat[hole] = VOID
    else:
        F.val -= 0.05


def p_buckle(F):
    if F.face == "front":
        outer = np.ones_like(F.alpha)
        inner = (F.u > 1.2) & (F.u < F.fw - 1.2) & (F.v > 1.2) & (F.v < F.fh - 1.2)
        F.mat[inner] = STRAP; F.val[inner] = -0.12
        F.val[outer & ~inner & (F.v < 1)] += 0.25
        F.val[outer & ~inner & (F.v > F.fh - 1)] -= 0.12
        pr = inner & (np.abs(F.u - F.fw / 2) < 0.5)
        stamp(F, pr, AMBER, hl=0.25, lo=0.1, shadow=0.1)
    else:
        F.val += 0.05


def p_hipbelt(F):
    p_belt(F)
    if F.face == "front":
        buckle(F, F.fw / 2 + 9.5, F.fh / 2, w=5, h=4)


def p_tabard(F):
    cloth_base(F, pitch=4, seed=1)
    if F.face in ("front", "back"):
        border = (F.u < 1) | (F.u > F.fw - 1)
        stamp(F, border, STRAP, hl=0.1, lo=0.1, shadow=0.08)
        if F.face == "back":
            F.val -= 0.1
        else:
            # faded amber emblem stitched on the panel: a small diamond echoing the helm gem
            cx, cy = F.fw / 2 + 1.5, 8.5
            dm = (np.abs(F.u - cx) + np.abs(F.v - cy)) < 3.2
            ring = dm & ((np.abs(F.u - cx) + np.abs(F.v - cy)) > 1.9)
            stamp(F, ring, SASH, hl=0.12, lo=0.1, shadow=0.08, add=-0.12)
    tatter(F, depth=6, seed=3)


def p_sash(F):
    F.val += 0.0
    if F.face in ("front", "back"):
        for k in range(0, F.fh, 9):
            scroll_on(F, 0, k + 1, F.fw, 8, seed=9, raise_=0.0, mat=None, hl=-0.2, lo=-0.05)
        F.val[(F.u < 1) | (F.u > F.fw - 1)] -= 0.1
    tatter(F, depth=4, seed=8)


def p_tabard_back(F):
    cloth_base(F, pitch=4, seed=2)
    if F.face in ("front", "back"):
        border = (F.u < 1) | (F.u > F.fw - 1)
        stamp(F, border, STRAP, hl=0.1, lo=0.1, shadow=0.08)
        if F.face == "front":
            F.val -= 0.1
    tatter(F, depth=6, seed=5)


def p_pouch(F):
    leather_base(F, 0.3, seed=9)
    if F.is_side():
        flap = F.v < 3
        stamp(F, flap, None, hl=0.16, lo=0.18, shadow=0.18, add=0.04)
        if F.face in ("back", "left"):
            rivet(F, F.fw / 2, 3.0, AMBER)


def p_brace(F):
    if F.face == "top":
        stitches(F, (np.abs(F.u - 0.5) < 0.5) | (np.abs(F.u - (F.fw - 0.5)) < 0.5), period=2)
        # buckle on the front slope of the shoulder (z ~ +6)
        cv = F.fh / 2 + 6
        outer = (np.abs(F.v - cv) < 2.5) & (F.u > 0.0) & (F.u < F.fw)
        inner = (np.abs(F.v - cv) < 1.5) & (F.u > 1) & (F.u < F.fw - 1)
        stamp(F, outer & ~inner, IRON, hl=0.3, lo=0.2, shadow=0.16)
        stamp(F, inner & (np.abs(F.v - cv) < 0.5), AMBER, hl=0.2, lo=0.1, shadow=0.0)


def p_pauldron(F):
    leather_base(F, 0.5, seed=10)
    if F.face == "top":
        trim = (F.u < 1) | (F.u > F.fw - 1) | (F.v < 1) | (F.v > F.fh - 1)
        stamp(F, trim, AMBER, hl=0.22, lo=0.14, shadow=0.14)
    elif F.is_side():
        trim_edge(F, "bottom", AMBER, 1)
        if F.face in ("front", "back", "right"):
            for k in range(4, F.fw - 2, 7):
                rivet(F, k, 2.6, AMBER)
        if F.face == "right":
            scroll_on(F, 2, 0, F.fw - 4, F.fh - 3, seed=11, raise_=0.7)


def p_pauldron_light(F):
    """low-profile leather shoulder plate: embossed top inside an amber rim, amber edge + rivets."""
    leather_base(F, 0.5, seed=10)
    if F.face == "top":
        rim = (F.u < 1) | (F.u > F.fw - 1) | (F.v < 1) | (F.v > F.fh - 1)
        stamp(F, rim, AMBER, hl=0.22, lo=0.14, shadow=0.12)
        scroll_on(F, 1.5, 1.5, F.fw - 3, F.fh - 3, seed=12, raise_=0.8)
        rivet(F, F.fw / 2, F.fh / 2, AMBER, size=2)
    elif F.is_side():
        trim_edge(F, "bottom", AMBER, 1)
        if F.face in ("front", "back"):
            rivet(F, F.fw - 2.5, 1.5, AMBER, size=1)


def p_wrap(F):
    """thin leather flap that wraps the front / back of the deltoid under the shoulder plate:
    amber edge along the bottom and the outer (+x) edge, a stitched seam under the plate, one rivet."""
    leather_base(F, 0.4, seed=15)
    if F.face in ("front", "back"):
        hx = F.fw / 2
        edge = ((F.ly < -F.fh / 2 + 1) | (F.lx > hx - 1)) & F.alpha
        stamp(F, edge, AMBER, hl=0.22, lo=0.14, shadow=0.12)
        stitches(F, (np.abs(F.ly - (F.fh / 2 - 1.5)) < 0.5) & (F.lx < hx - 1.5), period=2)
        cu, cv = _uv_of(F, (hx - 3.0, -0.3, 0))
        rivet(F, cu, cv, AMBER, size=1)
    elif F.is_side():
        F.val -= 0.04


def p_wrap_lame(F):
    """outer lame running down the upper arm: amber bottom edge, two rivets, embossed line."""
    leather_base(F, 0.4, seed=12)
    if F.is_side():
        trim_edge(F, "bottom", AMBER, 1)
        if F.face == "right":
            for k in (2.5, F.fw - 3.0):
                rivet(F, k, 1.6, AMBER, size=1)


def p_dome(F):
    leather_base(F, 0.55, seed=11)
    if F.face == "top":
        scroll_on(F, 0, 0, F.fw, F.fh - 1, seed=12, raise_=1.0)
        rivet(F, F.fw / 2, F.fh / 2, AMBER, size=2)
    elif F.is_side():
        trim_edge(F, "bottom", AMBER, 1)


def p_lame(F):
    leather_base(F, 0.4, seed=12)
    if F.is_side():
        trim_edge(F, "bottom", AMBER, 1)
        if F.face in ("front", "back"):
            rivet(F, F.fw / 2, 1.6, AMBER)
        if F.face == "right":
            for k in (2, F.fw - 3):
                rivet(F, k + 0.5, 1.6, AMBER)


def p_sleeve(F):
    cloth_base(F, pitch=3, seed=4)
    if F.is_side():
        # segmented leather rerebrace over the cloth on the outer half, held by two straps (ref 1 upper arms)
        if F.face == "left":
            plate = (F.ly > -9.5) & (F.ly < 3.0) & (F.u > 1.5) & (F.u < F.fw - 1.5)
            stamp(F, plate, LEATHER, hl=0.14, lo=0.12, shadow=0.14)
            lames(F, plate, 4.0, y_top=None)
        band_y(F, -7.5, -4.6, STRAP, stitch=False)
        band_y(F, 3.6, 6.0, STRAP, stitch=False)
        if F.face == "left":     # outer face of the right arm
            buckle(F, *_uv_of(F, (-4.5, -6.05, 0)), w=4, h=4)


CHEST = [
    dict(name="Cuirass", bone="Chest", pivot=(0, 0.3, 0.2), size=(29, 22, 21), mat=LEATHER, paint=p_cuirass,
         skip=("bottom",)),
    dict(name="Breastplate", bone="Chest", pivot=(0, 4.4, 11.2), size=(24, 10, 2), mat=LEATHER, paint=p_breast,
         skip=("back",)),
    dict(name="BreastLow", bone="Chest", pivot=(0, -3.2, 11.0), size=(18, 6, 2), mat=LEATHER, paint=p_breast_low,
         skip=("back", "top")),
    dict(name="Gorget", bone="Chest", pivot=(0, 12.0, -0.3), size=(19, 2, 16), mat=LEATHER, paint=p_gorget,
         skip=("bottom",)),
    dict(name="Plackart", bone="Belly", pivot=(0, 0.5, 0.2), size=(27, 16, 20), mat=LEATHER, paint=p_plackart,
         skip=("top", "bottom")),
    dict(name="Belt", bone="Belly", pivot=(0, -5.8, 0.2), size=(28, 3, 21), mat=STRAP, paint=p_belt,
         skip=("bottom",)),
    dict(name="Buckle", bone="Belly", pivot=(0, -5.8, 10.9), size=(5, 4, 1), mat=IRON,
         paint=p_buckle, skip=("back",)),
    dict(name="HipBelt", bone="Pelvis", pivot=(0, 1.8, 0.2), rot=(0, 0, -5), size=(27, 3, 21), mat=STRAP,
         paint=p_hipbelt),
    dict(name="Tabard", bone="Pelvis", pivot=(0, 0.5, 11.2), rot=(-3, 0, 0), size=(12, 25, 1), offset=(0, -12.5, 0),
         stretch=(1, 1, 1.25), mat=CLOTH, paint=p_tabard, skip=("top",), double=True),
    dict(name="Sash", bone="Pelvis", pivot=(-4.4, 0.8, 12.2), rot=(-3, 0, 3), size=(4, 28, 1), offset=(0, -14.0, 0),
         mat=SASH, paint=p_sash, skip=("top",), double=True),
    dict(name="TabardBack", bone="Pelvis", pivot=(0, 0.5, -11.0), rot=(3, 0, 0), size=(19, 25, 1), offset=(0, -12.5, 0),
         stretch=(1, 1, 1.25), mat=CLOTH, paint=p_tabard_back, skip=("top",), double=True),
    dict(name="R-Brace", bone="Chest", pivot=(-10.2, 11.6, 0.2), size=(4, 1, 22), stretch=(1, 1.2, 1), mat=STRAP,
         paint=p_brace, skip=("bottom",)),
    # LEFT pauldron (light, wrapped): top plate + front / back flaps that cup the deltoid + outer lame down the arm
    dict(name="L-Pauldron", bone="L-Arm", pivot=(4.8, 9.6, -0.3), rot=(0, 0, -27), size=(13, 3, 16), mat=LEATHER,
         paint=p_pauldron_light, skip=("bottom",)),
    dict(name="L-PauldronFront", bone="L-Arm", pivot=(3.0, 6.3, 7.35), rot=(7, 0, -24), size=(8, 6, 1),
         stretch=(1, 1, 1.25), mat=LEATHER, paint=p_wrap, double=False),
    dict(name="L-PauldronBack", bone="L-Arm", pivot=(3.4, 5.2, -7.35), rot=(-7, 0, -24), size=(8, 8, 1),
         stretch=(1, 1, 1.25), mat=LEATHER, paint=p_wrap, double=False),
    dict(name="L-Pauldron2", bone="L-Arm", pivot=(6.2, 4.2, -0.3), rot=(0, 0, 10), size=(2, 6, 14), mat=LEATHER,
         paint=p_wrap_lame, skip=("left",)),
    dict(name="R-Sleeve", bone="R-Arm", pivot=(0, -0.9, 0), size=(9, 22, 13), stretch=(1, 1, 1), mat=CLOTH,
         paint=p_sleeve, skip=("bottom",), mirror=True),
]


# ================================================================== HANDS
def p_bracer(F):
    leather_base(F, 0.45, seed=13)
    if F.is_side():
        lames(F, F.ly > -1.0, 3.0, y_top=None)
        b = band_y(F, -3.8, -1.2, STRAP, stitch=False)
        trim_edge(F, "bottom", AMBER, 1)
        if F.face == "left":
            buckle(F, *_uv_of(F, (-5, -2.5, 0)), w=4, h=4)
        stitches(F, np.abs(F.ly - (-5.0)) < 0.5, period=2)


def p_bguard(F):
    leather_base(F, 0.4, seed=14)
    if F.face == "left":
        trim = (F.u < 1) | (F.u > F.fw - 1) | (F.v < 1)
        stamp(F, trim, AMBER, hl=0.22, lo=0.14, shadow=0.14)
        F.val[np.abs(F.u - F.fw / 2) < 0.5] += 0.1
        F.val[np.abs(F.u - F.fw / 2 - 1) < 0.5] -= 0.06
        rivet(F, F.fw / 2, F.fh - 2.5, AMBER)
    elif F.face == "top":
        trim_edge(F, "left", AMBER, 1)


def p_glove(F):
    leather_base(F, 0.35, seed=15)
    if F.face == "left":            # back of the hand (outer side): knuckle plate + studs
        k = (F.ly > -1.5) & (F.ly < 2.5) & (F.u > 1) & (F.u < F.fw - 1)
        stamp(F, k, None, hl=0.18, lo=0.16, shadow=0.16, add=0.05)
        for cu in np.linspace(3, F.fw - 3, 4):
            rivet(F, cu, F.fh / 2 - 0.5, AMBER, size=1)
        fing = (F.ly < -1.5) & ((F.iu % 3) == 0) & (F.u > 1) & (F.u < F.fw - 1)
        F.val[fing] -= 0.16
    elif F.face in ("front", "back", "right"):
        fing = (F.ly < -0.5) & ((F.iu % 3) == 1)
        F.val[fing] -= 0.12
    elif F.face == "bottom":
        F.val[(F.iu % 3) == 1] -= 0.12


def p_cuff(F):
    leather_base(F, 0.35, seed=16)
    if F.is_side():
        trim_edge(F, "top", AMBER, 1)
        stitches(F, np.abs(F.v - 2.5) < 0.5, period=2)
        if F.face == "left":
            rivet(F, F.fw / 2, F.fh - 1.5, AMBER)
    elif F.face == "top":
        r = np.maximum(np.abs(F.lx) / 5, np.abs(F.lz) / 7)
        F.val[r < 0.8] -= 0.22


HANDS = [
    dict(name="R-Bracer", bone="R-Forearm", pivot=(0, -0.5, 0), size=(9, 14, 13), mat=LEATHER, paint=p_bracer,
         mirror=True),
    dict(name="R-BracerGuard", bone="R-Forearm", pivot=(-5.0, -1.0, 0), rot=(0, 0, 8), size=(3, 12, 11),
         stretch=(1.15, 1, 1), mat=LEATHER, paint=p_bguard, skip=("right",), mirror=True),
    dict(name="R-Glove", bone="R-Hand", pivot=(0, -0.2, 0), size=(11, 12, 15), stretch=(1, 1.02, 1), mat=LEATHER,
         paint=p_glove, skip=("top",), mirror=True),
    dict(name="R-GloveCuff", bone="R-Hand", pivot=(0, 5.6, 0), size=(12, 3, 16), stretch=(1, 1, 1), mat=LEATHER,
         paint=p_cuff, mirror=True),
]


# ================================================================== LEGS (feet / boots belong to Legs in Hytale)
def p_breeches(F):
    cloth_base(F, pitch=4, seed=6)
    if F.is_side():
        band_y(F, 4.2, 6.3, STRAP, stitch=False)
        if F.face == "front":
            lace = (np.abs(F.lx) < 0.6) & (F.ly < 3.5)
            F.val[lace] -= 0.14


def p_skirt(F):
    cloth_base(F, pitch=3, seed=7, wear_amt=0.3)
    if F.is_side():
        coord = F.x * abs(F.n[2]) + F.z * abs(F.n[0])
        crease = (np.round(coord) % 3 == 0)
        F.val[crease] -= 0.09
        F.val[(np.round(coord) % 3 == 1)] += 0.04
        tatter(F, depth=3, seed=11)
        F.val[F.ly < -7] -= 0.04


def p_tasset(F):
    """front tasset of the half plate: three overlapping leather lames, amber edge + rivets, hung on a strap."""
    leather_base(F, 0.5, seed=17)
    if F.is_side():
        lames(F, F.alpha, 14 / 3.0, y_top=None)
        trim_edge(F, "bottom", AMBER, 1)
    if F.face == "front":
        for k in range(3):
            for cu in (1.6, F.fw - 1.6):
                rivet(F, cu, k * 14 / 3.0 + 1.9, AMBER, size=1)
        strap = (np.abs(F.u - F.fw / 2) < 1.5) & (F.v < 3.5)
        stamp(F, strap, STRAP, hl=0.12, lo=0.1, shadow=0.12)
        stamp(F, strap & (np.abs(F.v - 2.5) < 0.6), IRON, hl=0.25, lo=0.1, shadow=0.0)
    elif F.face == "top":
        stamp(F, np.abs(F.lx) < 1.5, STRAP, hl=0.1, lo=0.1, shadow=0.1)


def p_knee(F):
    leather_base(F, 0.4, seed=18)
    if F.face == "front":
        rim = (F.u < 1) | (F.u > F.fw - 1) | (F.v < 1) | (F.v > F.fh - 1)
        stamp(F, rim, AMBER, hl=0.22, lo=0.14, shadow=0.12)
        boss = (np.abs(F.u - F.fw / 2) < 1.6) & (np.abs(F.v - F.fh / 2) < 1.1)
        stamp(F, boss, None, hl=0.2, lo=0.14, shadow=0.14, add=0.05)
        rivet(F, F.fw / 2, F.fh / 2, AMBER, size=1)
    elif F.face == "top":
        F.val += 0.04


def p_greave(F):
    """segmented greave; bottom 4 units = turned-down boot cuff (lames + amber trim)."""
    leather_base(F, 0.5, seed=19)
    if F.is_side():
        cuff = F.ly < -7.5
        lames(F, (F.ly > -0.5), 4.6, y_top=None)
        lames(F, cuff, 2.0, y_top=None)
        stamp(F, cuff & (F.ly > -8.5), AMBER, hl=0.22, lo=0.14, shadow=0.14)
        band_y(F, -3.5, -0.7, STRAP, stitch=False)
        if F.face == "left":
            buckle(F, *_uv_of(F, (-5.5, -2.1, 0)), w=4, h=4)
            rivet(F, *_uv_of(F, (-5.5, -10.0, 0)), AMBER)
        if F.face == "front":
            c = F.fw / 2
            ridge = (F.ly > -0.7)
            F.val[ridge & (np.abs(F.u - c + 0.5) < 0.5)] += 0.12
            F.val[ridge & (np.abs(F.u - c - 0.5) < 0.5)] -= 0.07
            scroll_on(F, 1, 1, F.fw - 2, 4, seed=20, raise_=0.6)
        if F.face == "back":
            lace = (np.abs(np.abs(F.lx) - ((F.iv % 4) * 0.5)) < 0.5) & (np.abs(F.lx) < 2.1) & ~cuff
            stitches(F, lace, period=1)
        stitches(F, np.abs(F.ly + 5.0) < 0.5, period=2)


def p_bootcuff(F):
    leather_base(F, 0.35, seed=20)
    if F.is_side():
        lames(F, F.alpha, 2.5, y_top=None)
        trim_edge(F, "top", AMBER, 1)
        if F.face == "left":
            rivet(F, F.fw / 2, 3.0, AMBER)
    elif F.face == "top":
        F.val[np.maximum(np.abs(F.lx) / 6, np.abs(F.lz) / 7) < 0.82] -= 0.2


def p_boot(F):
    leather_base(F, 0.35, seed=21)
    F.val -= 0.03
    if F.is_side():
        sole = F.ly < -2.6
        stamp(F, sole, STRAP, hl=0.16, lo=0.12, shadow=0.16, add=-0.08)
        if F.face == "front":
            # raised toe cap with a stitched seam
            cap = (F.ly > -2.6) & (F.ly < 1.2) & (np.abs(F.lx) < 5.6)
            stamp(F, cap, LEATHER, hl=0.16, lo=0.1, shadow=0.16, add=0.05)
            stitches(F, cap & (np.abs(F.ly - 0.4) < 0.5) & (np.abs(F.lx) < 4.6), period=2)
        if F.face in ("left", "right"):
            # ankle strap wrapping the boot, iron buckle on the outer side
            strap = (np.abs(F.lz + 2.5) < 1.5) & (F.ly > -2.6)
            stamp(F, strap, STRAP, hl=0.14, lo=0.12, shadow=0.16)
            if F.face == "right":
                bk = (np.abs(F.lz + 2.5) < 2.0) & (np.abs(F.ly - 0.6) < 1.6)
                stamp(F, bk & ~((np.abs(F.lz + 2.5) < 1.0) & (np.abs(F.ly - 0.6) < 0.6)), IRON, hl=0.3, lo=0.1, shadow=0.2)
            # heel counter
            heel = (F.lz < -7.5) & (F.ly > -2.6)
            F.val[heel] += 0.04
    elif F.face == "top":
        inst = F.lz > -2.0
        lames(F, inst, 3.2, axis=lambda G: G.z * 1.0 + 0, y_top=None, rim=0.15, line=0.22)
        strap = np.abs(F.lz + 3.5) < 1.5
        stamp(F, strap, STRAP, hl=0.14, lo=0.12, shadow=0.14)
        heel = F.lz < -6.5
        F.val[heel] -= 0.05
    elif F.face == "bottom":
        F.mat[:] = STRAP
        F.val -= 0.3


LEGS = [
    dict(name="Breeches", bone="Pelvis", pivot=(0, 0, 0.2), size=(26, 12, 20), stretch=(1, 1.04, 0.98), mat=CLOTH,
         paint=p_breeches, skip=("top",)),
    dict(name="R-Skirt", bone="R-Thigh", pivot=(0.2, -0.5, 0), size=(11, 21, 14), stretch=(1, 1, 1), mat=CLOTH,
         paint=p_skirt, skip=("top", "bottom"), double=True, mirror=True),
    dict(name="R-Tasset", bone="R-Thigh", pivot=(-1.2, 3.6, 7.6), rot=(-5, -14, 0), size=(8, 12, 1), stretch=(1, 1, 1.3), mat=LEATHER,
         paint=p_tasset, skip=("back", "bottom"), mirror=True),
    dict(name="R-Knee", bone="R-Calf", pivot=(0, 9.6, 6.9), size=(8, 5, 2), stretch=(1, 1, 1), mat=LEATHER,
         paint=p_knee, skip=("back",), mirror=True),
    dict(name="R-Greave", bone="R-Calf", pivot=(0, 2.5, 0.1), size=(11, 23, 13), stretch=(1, 1, 1), mat=LEATHER,
         paint=p_greave, skip=("bottom",), mirror=True),
    dict(name="R-Boot", bone="R-Foot", pivot=(0, 0.0, 0.3), size=(14, 8, 20), stretch=(1, 1, 1), mat=LEATHER,
         paint=p_boot, mirror=True),
]

PIECES = {"Head": HEAD, "Chest": CHEST, "Hands": HANDS, "Legs": LEGS}
