#!/usr/bin/env python3
"""SkyWynn fish species icons - original pixel art, Python + Pillow, deterministic.

Cloud draft 2026-10-06 (concept only, nothing built). One 64 x 64 transparent
icon per species in research/cloud/Fish-Species-Catalog.md (39 fish) plus the
7 junk items and 8 Lost Property wrappers, and a labelled sheet grouped by zone.

Fish are drawn by a small "fish-space" renderer: every pixel is mapped into a
rotated fish frame (u along the body, tail -> snout; v across, back -> belly)
and tested against the body profile, tail, fins, pectoral, eye, gill and
pattern rules of the species. That keeps a clean 1-px outline at any angle.
No game art was copied or looked at; all shapes and palettes are our own.

Run:  python3 research/cloud/fish-art/make_fish.py
Writes: icons/<id>.png (64 x 64) and fish-sheet.png next to this file.
Dev preview: FISH_PREVIEW=<ids or zone numbers or 'items' or 'all'> FISH_OUT=<png> [FISH_SCALE=8] python3 make_fish.py
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))
W = H = 64
LO, HI = 5, 58          # object box (the halo / sparkles live in the margin)


# ---------------------------------------------------------------- colour helpers
def hx(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def ramp(*cols):
    """6 steps: 0 outline, 1 dark, 2 dark-mid, 3 mid, 4 light, 5 highlight"""
    return [hx(c) for c in cols]


def mix(a, b, t=0.5):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,)


def h(x, y, s=0):
    """deterministic hash noise 0..1"""
    n = (x * 374761393 + y * 668265263 + s * 2147483647) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0


def clamp(v, a, b):
    return a if v < a else b if v > b else v


RAR = {   # Skyy's locked rarity colours (Vanilla-UI-Style-Guide; Mythic page colour #CC66CC)
    'Normal': hx('#FFFFFF'), 'Unique': hx('#FFFF55'), 'Rare': hx('#FF55FF'),
    'Legendary': hx('#55FFFF'), 'Fabled': hx('#FF5555'), 'Mythic': hx('#CC66CC'),
    'Junk': hx('#9a9a9a'),
}

# shared ramps
EYE_GOLD = ramp('#1a1206', '#6a4a10', '#b8862a', '#e6b84a', '#ffe08a', '#fff6d0')
EYE_SILV = ramp('#14181e', '#4a5560', '#8a96a2', '#c0c8d0', '#e6ecf0', '#ffffff')
EYE_RED = ramp('#1a0606', '#6a1010', '#b02a1a', '#e8582a', '#ffa060', '#fff0c0')
EYE_TEAL = ramp('#06181a', '#0e5a5a', '#1aa8a0', '#4ae8d8', '#a8fff0', '#ffffff')
EYE_ICE = ramp('#0a1a2a', '#2a5a8a', '#5a9ad0', '#9ad0f4', '#d8f2ff', '#ffffff')
GLOW_LAVA = [hx('#ff4a10'), hx('#ff8a1a'), hx('#ffd04a'), hx('#fff4b0')]
GLOW_BIO = [hx('#1aa8a0'), hx('#3ae8d0'), hx('#a8fff0'), hx('#ffffff')]
GLOW_BIOP = [hx('#8a3ad8'), hx('#c070ff'), hx('#e6b8ff'), hx('#ffffff')]


# ---------------------------------------------------------------- canvas
class Icon:
    def __init__(self):
        self.im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        self.px = self.im.load()

    def get(self, x, y):
        return self.px[x, y] if 0 <= x < W and 0 <= y < H else (0, 0, 0, 0)

    def set(self, x, y, col):
        x, y = int(x), int(y)
        if 0 <= x < W and 0 <= y < H:
            if len(col) == 4 and col[3] < 255:
                self.blend(x, y, col[:3], col[3] / 255)
            else:
                self.px[x, y] = tuple(col[:3]) + (255,)

    def blend(self, x, y, rgb, a):
        if not (0 <= x < W and 0 <= y < H):
            return
        o = self.px[x, y]
        if o[3] == 0:
            self.px[x, y] = tuple(rgb) + (round(255 * a),)
        else:
            oa = o[3] / 255
            na = a + oa * (1 - a)
            c = tuple(round((rgb[i] * a + o[i] * oa * (1 - a)) / na) for i in range(3))
            self.px[x, y] = c + (round(255 * na),)

    def solid(self, x, y):
        return self.get(x, y)[3] > 0


def outline_cols(ic, mask_fn, col):
    """4-neighbour 1-px outline round every opaque pixel"""
    add = []
    for y in range(H):
        for x in range(W):
            if ic.get(x, y)[3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if ic.get(x + dx, y + dy)[3] == 255:
                        add.append((x, y, col(x + dx, y + dy)))
                        break
    for x, y, c in add:
        ic.px[x, y] = c


# ================================================================ the fish renderer
def prof(t, tmax, p, b, a=0.85):
    a = PROF_A[0] if PROF_A[0] else a
    """body depth profile 0..1 along t (0 = peduncle, 1 = snout)"""
    if t <= 0 or t >= 1:
        return p if t <= 0 else 0.0
    if t < tmax:
        s = t / tmax
        return p + (1 - p) * math.sin(s * math.pi / 2) ** a
    s = (t - tmax) / (1 - tmax)
    return max(0.0, 1 - s ** b) ** (1 / b)


PROF_A = [None]
SPINES = [6]


class Fish:
    """Default parameters; species override them (design units, 64-px frame)."""
    L = 54            # total length tail tip -> snout
    TL = 12           # tail fin length
    Ht = 9            # max depth above the centre line
    Hb = 9            # max depth below
    tmax = 0.5
    p = 0.32          # peduncle depth fraction
    b = 1.8           # head bluntness (1.2 pointy .. 3 blunt)
    ang = 18          # degrees, head up-right
    wave = 0.0        # eel wave amplitude
    waven = 1.2
    tail = 'fork'     # fork / round / lunate / trunc / point / heter
    tw = 10           # tail half-span at the trailing edge
    fd = 0.45         # fork depth
    dorsal = [(0.35, 0.72, 6, 'tri')]
    dorsal2 = None
    anal = [(0.18, 0.36, 4, 'tri')]
    pelvic = (0.5, 4)
    pect = (0.68, 0.62, 6, 2.2)    # t, nv, length, width
    eye = (0.88, 0.36, 2.6)        # t, nv, radius
    eyecol = EYE_GOLD
    gill = 0.76
    mouth = 0.55                   # nv of the mouth at the snout
    scale = 4.0                    # scale size (0 = smooth skin)
    back = ramp('#10200c', '#2e4a1a', '#4a6a24', '#6a8a30', '#90ac48', '#c4d870')
    belly = ramp('#3a2a0c', '#a8862e', '#d4b24a', '#ecd070', '#f6e49a', '#fff6c8')
    fin = ramp('#1a1a08', '#5a5a1e', '#8a8a2e', '#b0a83e', '#d4c860', '#f0e8a0')
    split = 0.56                   # nv where the belly colour starts
    lateral = True
    pattern = ()
    snout = 0.0                    # extra jaw length (gar / pike), design units
    barbels = 0
    flat = False                   # flatfish (halibut): eyes on top, no belly split
    glow = None                    # crack / bio glow ramp
    extra = None                   # extra(ic, F, to) painter after the body
    k = 1.0                        # fitted scale

    # ---- geometry
    def ub0(self):
        return self.TL

    def cl(self, u):
        if not self.wave:
            return 0.0
        t = u / self.L
        return self.wave * math.sin(t * math.pi * 2 * self.waven + 0.6) * (1 - 0.6 * t)

    def edges(self, u):
        t = (u - self.TL) / (self.L - self.TL)
        c = self.cl(u)
        PROF_A[0] = getattr(self, 'pa', None)
        pr = prof(t, self.tmax, self.p, self.b)
        return t, c - self.Ht * pr, c + self.Hb * pr


def fish_frame(F, k, ox=0.0, oy=0.0):
    a = math.radians(F.ang)
    ca, sa = math.cos(a), math.sin(a)

    def to_fish(x, y):
        dx, dy = (x + 0.5 - 32 - ox) / k, (y + 0.5 - 32 - oy) / k
        return dx * ca - dy * sa + F.L / 2, dx * sa + dy * ca

    def to_px(u, v):
        u -= F.L / 2
        dx = u * ca + v * sa
        dy = -u * sa + v * ca
        return dx * k + 32 + ox - 0.5, dy * k + 32 + oy - 0.5
    return to_fish, to_px


def fin_h(ft, kind, h_):
    if ft < 0 or ft > 1:
        return -1
    if kind == 'tri':
        return h_ * ((ft / 0.3) if ft < 0.3 else ((1 - ft) / 0.7) ** 0.7)
    if kind == 'sail':
        return h_ * math.sin(math.pi * min(1, ft * 1.15)) ** 0.5
    if kind == 'spiny':
        base = h_ * (min(1, ft / 0.2)) * (1 - 0.35 * ft)
        n = SPINES[0]
        return base * (0.4 + 0.6 * (1 - (ft * n) % 1))
    if kind == 'low':
        return h_ * min(1, ft * 5, (1 - ft) * 5)
    if kind == 'round':
        return h_ * math.sqrt(max(0, 1 - (2 * ft - 1) ** 2))
    if kind == 'back':     # swept-back flag (front tall)
        return h_ * (min(1, ft / 0.15)) * (1 - 0.75 * ft)
    return h_


def classify(F, u, v):
    """part label + local info for a fish-space point"""
    if getattr(F, 'shape', None):
        return F.shape(F, u, v)
    L, TL = F.L, F.TL
    # snout extension (gar / pike jaw)
    if F.snout and L <= u <= L + F.snout:
        s = (u - L) / F.snout
        t, top, bot = F.edges(L - 0.01)
        c = F.cl(L) + F.Hb * 0.15
        hw = 1.6 * (1 - s) + 0.6
        if abs(v - c) <= hw:
            return ('jaw', s, (v - c + hw) / (2 * hw))
    if TL <= u <= L:
        t, top, bot = F.edges(u)
        if top <= v <= bot:
            return ('body', t, (v - top) / max(0.01, bot - top))
        # dorsal fins
        for d in (F.dorsal or []) + (F.dorsal2 or []):
            t0, t1, hh, kind = d
            SPINES[0] = max(3, round((t1 - t0) * (L - TL) / 3.2))
            ft = (t - t0) / (t1 - t0)
            fh = fin_h(ft, kind, hh)
            if fh > 0 and top - fh <= v < top:
                return ('fin', ft, (top - v) / fh, kind)
        for d in (F.anal or []):
            t0, t1, hh, kind = d
            ft = (t - t0) / (t1 - t0)
            fh = fin_h(ft, kind, hh)
            if fh > 0 and bot < v <= bot + fh:
                return ('fin', ft, (v - bot) / fh, kind)
        if F.pelvic:
            pt, ph = F.pelvic
            ft = (t - (pt - 0.09)) / 0.12
            fh = fin_h(ft, 'back', ph)
            if fh > 0 and bot < v <= bot + fh:
                return ('fin', ft, (v - bot) / fh, 'back')
    # tail
    if F.tail != 'point' and TL - TL <= u < TL + 0.5:
        s = (TL - u) / TL        # 0 at peduncle, 1 at trailing edge
        if s < 0:
            s = 0
        c = F.cl(u)
        pw = F.Ht * F.p
        vv = v - c
        if F.tail == 'heter':
            tw = F.tw * (1.15 if vv < 0 else 0.6)
        else:
            tw = F.tw
        hs = pw + (tw - pw) * (s ** 0.75)
        if abs(vv) > hs:
            return None
        r = min(1, abs(vv) / tw)
        if F.tail == 'fork':
            edge = 1 - F.fd * (1 - r) ** 1.2
        elif F.tail == 'lunate':
            edge = 1 - F.fd * (1 - r * r)
        elif F.tail == 'round':
            edge = 1 - 0.35 * r ** 2
        elif F.tail == 'heter':
            edge = (1 - 0.55 * (1 - r)) if vv < 0 else (1 - 0.3 * r ** 2 - 0.25 * (1 - r))
        else:
            edge = 1
        if s <= edge:
            return ('tail', s, vv / tw)
    return None


def render_fish(F, rarity):
    # fit: largest scale k whose drawing stays inside LO..HI
    best = None
    for kk in range(140, 50, -2):
        k = kk / 100
        to_fish, to_px = fish_frame(F, k)
        xs, ys = [], []
        for y in range(-10, H + 10, 1):
            for x in range(-10, W + 10, 1):
                if classify(F, *to_fish(x, y)):
                    xs.append(x); ys.append(y)
        if not xs:
            continue
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        if x1 - x0 <= HI - LO - 2 and y1 - y0 <= HI - LO - 2:
            ox = (LO + 1 + HI - 1) / 2 - (x0 + x1) / 2
            oy = (LO + 1 + HI - 1) / 2 - (y0 + y1) / 2
            best = (k, round(ox), round(oy))
            break
    k, ox, oy = best
    F.k = k
    to_fish, to_px = fish_frame(F, k, ox, oy)
    ic = Icon()
    lab = {}
    for y in range(H):
        for x in range(W):
            c = classify(F, *to_fish(x, y))
            if c:
                lab[(x, y)] = c
    F._lab = lab
    # ---- paint parts
    for (x, y), c in lab.items():
        u, v = to_fish(x, y)
        kind = c[0]
        if kind == 'body':
            col = body_col(F, x, y, u, v, c[1], c[2])
        elif kind == 'jaw':
            lvl = 4 if c[2] < 0.35 else 3 if c[2] < 0.7 else 2
            if h(x, y, 3) < 0.2:
                lvl -= 1
            col = F.back[lvl] if c[2] < 0.5 else F.belly[lvl]
        elif kind == 'tail':
            col = tail_col(F, x, y, u, v, c[1], c[2])
        else:
            col = fin_col(F, x, y, u, v, c[1], c[2], c[3])
        ic.px[x, y] = col
    # separation: fin pixels touching body get the fin's dark shade
    for (x, y), c in lab.items():
        if c[0] in ('fin', 'tail'):
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = lab.get((x + dx, y + dy))
                if n and n[0] == 'body':
                    ic.px[x, y] = F.fin[1]
                    break
    # pectoral fin overlay
    if F.pect:
        pectoral(ic, F, to_fish, to_px)
    # gill line, lateral line, eye, mouth
    head_details(ic, F, to_fish, to_px)
    if F.barbels:
        barbels(ic, F, to_px)
    if F.extra:
        F.extra(ic, F, to_px)
    # outline
    oc = F.back[0]
    outline_cols(ic, None, lambda x, y: oc)
    if F.glow:
        glow_spill(ic, F)
    rarity_fx(ic, rarity)
    return ic


def body_col(F, x, y, u, v, t, nv):
    R = F.back
    lvl = 3
    if nv < 0.09:
        lvl = 3
    elif nv < 0.3:
        lvl = 4
    elif nv < F.split - 0.08:
        lvl = 3
    else:
        lvl = 2
    use_belly = nv >= F.split or (nv >= F.split - 0.06 and (x + y) % 2 == 0)
    if F.flat:
        use_belly = False
    if use_belly:
        R = F.belly
        lvl = 4 if nv < F.split + 0.18 else 3 if nv < 0.86 else 2
    if t < 0.12:
        lvl -= 1
    if t > 0.93 and nv < 0.5:
        lvl += 0
    # screen-space light from the top-left
    if (x + y) > 82 and nv > 0.7:
        lvl -= 1
    # scales
    if F.scale:
        sz = F.scale
        rh = sz * 0.72
        row = math.floor(v / rh)
        uu = u + (row % 2) * sz / 2
        col_ = math.floor(uu / sz)
        lx = uu - col_ * sz
        ly = v - row * rh
        # arc: convex side toward the tail
        d = math.hypot(lx - sz * 0.85, (ly - rh / 2) * 1.15)
        if abs(d - sz * 0.62) < 0.5 / F.k and lx < sz * 0.85:
            lvl -= 1
            F._scl = True
        elif abs(d - sz * 0.62 + 1.0 / F.k) < 0.5 / F.k and lx < sz * 0.75 and 0.15 < nv < 0.8 and h(x, y, 12) < 0.6:
            lvl += 1
    # texture noise
    r = h(x, y, 11)
    if r < 0.06:
        lvl -= 1
    elif r > 0.96 and nv < 0.5:
        lvl += 1
    lvl = clamp(lvl, 1, 5)
    col = R[lvl]
    for pat in F.pattern:
        col = pattern(F, pat, col, x, y, u, v, t, nv, lvl) or col
    # lateral line
    if F.lateral and 0.1 < t < 0.78:
        tt, top, bot = F.edges(u)
        lv_ = top + (bot - top) * (0.4 - 0.06 * math.sin(t * 3))
        if abs(v - lv_) < 0.5 / F.k + 0.05 and int(u * F.k) % 2 == 0:
            col = mix(col, R[1], 0.6)
    return col


def tail_col(F, x, y, u, v, s, r):
    R = F.fin
    lvl = 3 if s < 0.5 else 4
    if r < -0.3:
        lvl += 0
    if r > 0.4:
        lvl -= 1
    # rays radiate from the peduncle
    ang = math.atan2(r * F.tw, s * F.TL + 3)
    if int((ang + 3) * 9) % 2 == 0 and s > 0.15:
        lvl -= 1
    if s > 0.82:
        lvl += 1
    if h(x, y, 5) < 0.05:
        lvl -= 1
    col = R[clamp(lvl, 1, 5)]
    for pat in F.pattern:
        if pat[0] in ('finpat', 'cracks', 'bio', 'frostfin', 'flame'):
            col = pattern(F, pat, col, x, y, u, v, s, 0.5, lvl, part='tail') or col
    return col


def fin_col(F, x, y, u, v, ft, fh, kind):
    R = F.fin
    lvl = 3 if fh < 0.5 else 4
    if kind == 'spiny' and int(u * F.k) % 3 == 0:
        lvl -= 1
    elif int(u * F.k * 0.7) % 2 == 0 and fh > 0.2:
        lvl -= 1
    if fh > 0.85:
        lvl += 1
    col = R[clamp(lvl, 1, 5)]
    for pat in F.pattern:
        if pat[0] in ('finpat', 'cracks', 'bio', 'frostfin', 'flame'):
            col = pattern(F, pat, col, x, y, u, v, ft, fh, lvl, part='fin') or col
    return col


def pectoral(ic, F, to_fish, to_px):
    pt, pnv, plen, pw = F.pect
    ua = F.TL + pt * (F.L - F.TL)
    t, top, bot = F.edges(ua)
    va = top + (bot - top) * pnv
    m = set()
    for y in range(H):
        for x in range(W):
            u, v = to_fish(x, y)
            du = ua - u
            if 0 <= du <= plen:
                dv = v - va - du * 0.35
                w = pw * (1 - du / plen) ** 0.6 + 0.4
                if abs(dv) <= w:
                    m.add((x, y, du / plen))
    pts = {(x, y) for x, y, _ in m}
    for x, y, s in m:
        lvl = 4 if s < 0.4 else 3
        if (x * 2 + y) % 3 == 0:
            lvl -= 1
        ic.px[x, y] = F.fin[lvl]
    for x, y in pts:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in pts and ic.get(*q)[3] and q in F._lab:
                ic.px[q] = F.fin[1] if F._lab[q][0] == 'body' else ic.px[q]


def head_details(ic, F, to_fish, to_px):
    lab = F._lab
    # gill line: an arc bowing toward the head
    ug = F.TL + F.gill * (F.L - F.TL)
    for (x, y), c in (lab.items() if F.gill > 0 else ()):
        if c[0] != 'body':
            continue
        u, v = to_fish(x, y)
        t, top, bot = F.edges(ug)
        nv = (v - top) / max(0.01, bot - top)
        if nv < 0.12 or nv > 0.92:
            continue
        arc = ug + 2.2 * math.sin(math.pi * nv) * (1 if not F.flat else 0.5)
        d = u - arc
        if -0.55 / F.k <= d < 0.55 / F.k:
            ic.px[x, y] = mix(ic.px[x, y], F.back[0], 0.75)
        elif 0.55 / F.k <= d < 1.5 / F.k and nv < 0.7:
            ic.px[x, y] = mix(ic.px[x, y], F.back[5] if nv < F.split else F.belly[5], 0.35)
    # lateral line drawn in body_col; eye
    if not F.eye:
        return
    et, env_, er = F.eye
    ue = F.TL + et * (F.L - F.TL)
    t, top, bot = F.edges(ue)
    ve = top + (bot - top) * env_
    ex, ey = to_px(ue, ve)
    rr = er * F.k
    cx, cy = ex, ey
    E = F.eyecol
    for y in range(int(cy - rr - 2), int(cy + rr + 3)):
        for x in range(int(cx - rr - 2), int(cx + rr + 3)):
            d = math.hypot(x - cx, y - cy)
            if d <= rr + 0.35:
                if d > rr - 0.75:
                    col = E[0]
                elif d > rr * 0.55:
                    col = E[4] if (x - cx) + (y - cy) < -rr * 0.4 else E[3] if (x - cx) + (y - cy) < rr * 0.4 else E[2]
                else:
                    col = (12, 10, 14, 255) if not getattr(F, 'blind', False) else E[3]
                ic.px[x, y] = col
    gx, gy = int(round(cx - rr * 0.35)), int(round(cy - rr * 0.35))
    if F.eyecol is not None and not getattr(F, 'sleep', False):
        ic.px[gx, gy] = (255, 255, 255, 255)
        if rr > 2.4:
            ic.px[gx + 1, gy] = E[5]
    if getattr(F, 'sleep', False):
        # closed lid: a heavy curved line
        for y in range(int(cy - rr - 1), int(cy + rr + 2)):
            for x in range(int(cx - rr - 1), int(cx + rr + 2)):
                d = math.hypot(x - cx, y - cy)
                if d <= rr + 0.35:
                    ic.px[x, y] = F.back[2] if y < cy + 0.5 else F.back[1]
        for x in range(int(cx - rr), int(cx + rr + 1)):
            yy = int(round(cy + 0.4 + 0.25 * abs(x - cx)))
            ic.px[x, yy] = F.back[0]
    # mouth
    if F.mouth is None:
        return
    ut = F.L - 0.6
    t, top, bot = F.edges(F.L - 2.0)
    vm = top + (bot - top) * F.mouth
    for i in range(int(3 * F.k) + 1):
        x, y = to_px(F.L + F.snout - 0.4 - i / F.k, vm + (0.4 if F.snout else 0))
        x, y = int(round(x)), int(round(y))
        if ic.get(x, y)[3]:
            ic.px[x, y] = F.back[0]


def barbels(ic, F, to_px):
    """short whiskers from the mouth, curling back and down (about 6-8 px)"""
    t, top, bot = F.edges(F.L - 2.0)
    n = 7 if F.barbels < 3 else 9
    for i in range(F.barbels):
        u0 = F.L - 1.2 - i * 1.4 / F.k
        v0 = top + (bot - top) * min(0.95, F.mouth + 0.1 + 0.1 * i)
        for st in range(n):
            q = st / F.k
            uu = u0 - q * (0.55 + 0.15 * i)
            vv = v0 + q * 0.75 - 0.02 * q * q
            x, y = to_px(uu, vv)
            x, y = int(round(x)), int(round(y))
            if 0 <= x < W and 0 <= y < H and not (ic.get(x, y)[3] and F._lab.get((x, y), ('',))[0] == 'body' and st < 2):
                ic.px[x, y] = F.belly[3] if st < n // 2 else F.belly[2]


# ---------------------------------------------------------------- patterns
def pattern(F, pat, col, x, y, u, v, t, nv, lvl, part='body'):
    kind = pat[0]
    if kind == 'bars' and part == 'body':           # (bars, n, ramp, width, maxnv)
        _, n, R, wdt, mx = pat
        ph = (t * n) % 1
        if ph < wdt and nv < min(mx, F.split) and not (ph > wdt - 0.08 and nv > min(mx, F.split) - 0.12 and h(x, y, 22) < 0.5):
            return R[clamp(lvl, 1, 5)]
    if kind == 'spots' and part == 'body':          # (spots, density, colour, nvmin, nvmax)
        _, den, c, a, b = pat
        cell = 2.6
        cu, cv = math.floor(u / cell), math.floor(v / cell)
        if a <= nv <= b and h(cu, cv, 21) < den:
            du, dv = u - (cu + 0.5) * cell, v - (cv + 0.5) * cell
            if du * du + dv * dv < 0.9:
                return c
    if kind == 'blotch' and part == 'body':         # koi patches (blotch, ramp, seed, thr)
        _, R, sd, thr = pat
        n = (math.sin(u * 0.33 + sd) + math.sin(v * 0.5 + u * 0.12 + sd * 2) + math.sin((u - v) * 0.21 + sd * 3))
        if n > thr:
            return R[clamp(lvl, 1, 5)]
    if kind == 'stripe' and part == 'body':         # (stripe, nv0, nv1, ramp)
        _, a, b, R = pat
        if a <= nv <= b:
            return R[clamp(lvl, 1, 5)]
    if kind == 'flecks' and part == 'body':         # (flecks, density, colour)
        if h(x, y, 31) < pat[1] and nv < 0.8:
            return pat[2]
    if kind == 'cracks':                            # (cracks, density)
        # cellular cracks: distance to the 2 nearest seeds
        cs = 4.2
        ci, cj = math.floor(u / cs), math.floor(v / cs)
        ds = []
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                ii, jj = ci + di, cj + dj
                sx = (ii + 0.2 + 0.6 * h(ii, jj, 41)) * cs
                sy = (jj + 0.2 + 0.6 * h(ii, jj, 42)) * cs
                ds.append(math.hypot(u - sx, v - sy))
        ds.sort()
        e = ds[1] - ds[0]
        G = F.glow
        lim = 0.55 / F.k + 0.1
        on = h(ci, cj, 43) < pat[1]
        if e < lim and on:
            return G[2] if e < lim * 0.45 else G[1]
        if e < lim * 2.1 and on:
            return mix(col, G[0], 0.45)
    if kind == 'bio':                               # (bio, density, nvmin, nvmax)
        cell = 3.2
        cu, cv = math.floor(u / cell), math.floor(v / cell)
        G = F.glow
        if pat[2] <= nv <= pat[3] or part != 'body':
            if h(cu, cv, 51) < pat[1]:
                du, dv = u - (cu + 0.5) * cell, v - (cv + 0.5) * cell
                d = math.hypot(du, dv) * F.k
                if d < 0.75:
                    return G[3]
                if d < 1.5:
                    return G[1]
                if d < 2.4:
                    return mix(col, G[0], 0.45)
    if kind == 'frost' and part == 'body':          # rime sparkle on the back
        if nv < 0.35 and h(x, y, 61) < pat[1]:
            return hx('#ffffff')
        if nv < 0.12 and h(x, y, 62) < 0.5:
            return mix(col, hx('#e8f6ff'), 0.6)
    if kind == 'frostfin' and part != 'body':
        if nv > 0.8 or (part == 'tail' and t > 0.8):
            return mix(col, hx('#ffffff'), 0.55)
    if kind == 'flame' and part != 'body':
        # fins burn from root (red) to tip (yellow-white)
        f = nv if part == 'fin' else t
        G = GLOW_LAVA
        q = f + 0.18 * (h(x, y, 71) - 0.5)
        return G[0] if q < 0.35 else G[1] if q < 0.62 else G[2] if q < 0.86 else G[3]
    if kind == 'finpat' and part != 'body':         # (finpat, ramp, mode)
        R = pat[1]
        if pat[2] == 'edge' and (nv > 0.72 if part == 'fin' else t > 0.78):
            return R[clamp(lvl, 1, 5)]
        if pat[2] == 'spots' and h(int(u * 0.8), int(v * 0.8), 81) < 0.25:
            return R[2]
        if pat[2] == 'all':
            return R[clamp(lvl, 1, 5)]
    if kind == 'scutes' and part == 'body':         # sturgeon bony plates (scutes, ramp, rows)
        R = pat[1]
        for rnv in pat[2]:
            if abs(nv - rnv) < 0.09:
                ph = (u * 0.42) % 1
                if ph < 0.55:
                    return R[4] if nv < rnv else R[2]
    return None


# ---------------------------------------------------------------- glow + rarity
def glow_spill(ic, F):
    """soft light spilling from the hottest / brightest pixels onto the outline"""
    G = F.glow
    hot = [(x, y) for y in range(H) for x in range(W) if ic.px[x, y][:3] in (G[2][:3], G[3][:3])]
    for x, y in hot:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            c = ic.get(*q)
            if c[3] == 255 and c[:3] == F.back[0][:3]:
                ic.px[q] = mix(F.back[0], G[0], 0.55)


def grow(m, n=1):
    for _ in range(n):
        m = m | {(x + dx, y + dy) for x, y in m for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))}
    return m


def star(ic, sx, sy, arm, c, core=(255, 255, 255, 255)):
    ic.set(sx, sy, core)
    for k_ in range(1, arm + 1):
        a = round(255 * (1 - (k_ - 1) / (arm + 0.5)))
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if ic.get(sx + dx * k_, sy + dy * k_)[3] < 200:
                ic.set(sx + dx * k_, sy + dy * k_, c[:3] + (a,))
    if arm >= 3:
        for dx, dy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            if ic.get(sx + dx, sy + dy)[3] < 200:
                ic.set(sx + dx, sy + dy, c[:3] + (110,))


def free_spot(ic, cands, r=2):
    for sx, sy in cands:
        if all(ic.get(sx + dx, sy + dy)[3] == 0 for dx in range(-r, r + 1) for dy in range(-r, r + 1)):
            return sx, sy
    return None


CORNERS = [(57, 6), (55, 8), (6, 57), (8, 55), (57, 56), (6, 7), (56, 30), (31, 57), (7, 31), (31, 6)]


def halo(ic, col, layers):
    a = {(x, y) for x in range(W) for y in range(H) if ic.px[x, y][3] > 0}
    prev = a
    rings = []
    for _ in range(len(layers)):
        g = grow(prev, 1)
        rings.append(g - prev)
        prev = g
    for ring, al in zip(rings, layers):
        for x, y in ring:
            ic.set(x, y, col[:3] + (al,))


def rarity_fx(ic, r):
    """Normal: nothing. Unique: one small yellow glint. Rare: faint pink rim + a star.
    Legendary: aqua 3-px halo + 3 sparkles. Fabled: red halo + 4 sparkles + embers.
    Mythic: purple double halo (pink inner) + 5 sparkles + orbiting motes."""
    if r in ('Normal', 'Junk', None):
        return
    c = RAR[r]
    used = []

    def spark(arm, n):
        for _ in range(n):
            p = free_spot(ic, [q for q in CORNERS if q not in used], 2 if arm < 3 else 3)
            if not p:
                return
            used.append(p)
            star(ic, p[0], p[1], arm, c)
            arm = max(1, arm - 1)
    if r == 'Unique':
        spark(2, 1)
    elif r == 'Rare':
        halo(ic, c, (60,))
        spark(3, 1)
    elif r == 'Legendary':
        halo(ic, c, (150, 70, 28))
        spark(4, 3)
    elif r == 'Fabled':
        halo(ic, hx('#ffb0a0'), (120,))
        halo(ic, c, (150, 70, 30))
        spark(4, 4)
        for i, (x, y) in enumerate([(12, 50), (50, 13), (16, 9), (49, 52)]):
            if ic.get(x, y)[3] == 0:
                ic.set(x, y, hx('#ffd04a'))
                ic.set(x, y - 1, hx('#ff8a1a')[:3] + (150,))
    elif r == 'Mythic':
        halo(ic, hx('#ffb8f0'), (170,))
        halo(ic, c, (160, 90, 40))
        spark(4, 5)
        for i in range(6):
            a = i / 6 * math.tau + 0.4
            x, y = int(32 + 29 * math.cos(a)), int(32 + 29 * math.sin(a))
            if ic.get(x, y)[3] == 0:
                ic.set(x, y, hx('#f0d0ff') if i % 2 else c)


# ================================================================ species
def fish(**kw):
    F = Fish()
    for k_, v in kw.items():
        setattr(F, k_, v)
    return F


# ---- palettes per zone (all our own)
# Z1 river greens / golds
Z1_OLIVE = ramp('#10200c', '#2e4a1a', '#4a6a24', '#6a8a30', '#90ac48', '#c4d870')
Z1_GOLDB = ramp('#3a2a0c', '#a8862e', '#d4b24a', '#ecd070', '#f6e49a', '#fff6c8')
Z1_FIN = ramp('#1a1a08', '#5a5a1e', '#8a8a2e', '#b0a83e', '#d4c860', '#f0e8a0')
Z1_SILV = ramp('#141c18', '#5a6a60', '#8a9a8c', '#b4c2b2', '#d8e2d4', '#f6fbf0')


def sprite(ic, x, y, rows, pal):
    """paint a tiny pixel sprite; '.' = skip"""
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch != '.':
                ic.set(int(x) + i, int(y) + j, pal[ch])


def at(F, to_px, t, nv):
    u = F.TL + t * (F.L - F.TL)
    tt, top, bot = F.edges(u)
    x, y = to_px(u, top + (bot - top) * nv)
    return int(round(x)), int(round(y))


def top_at(F, to_px, t, dv=0.0):
    u = F.TL + t * (F.L - F.TL)
    tt, top, bot = F.edges(u)
    x, y = to_px(u, top + dv)
    return int(round(x)), int(round(y))


INK = hx('#20232a')
PAPER = ramp('#2a2a2a', '#9a968a', '#c8c4b4', '#e6e2d2', '#f6f4ea', '#ffffff')
STAMP_RED = hx('#c8283a')
STAMP_RED_D = hx('#8a1422')


# ---- extras (lore touches)
def x_bluegill(ic, F, to_px):
    x, y = at(F, to_px, 0.74, 0.3)
    sprite(ic, x - 1, y - 1, ['.ab', 'abb', 'bb.'], {'a': hx('#1a2a5a'), 'b': hx('#0e1430')})


def x_queue(ic, F, to_px):
    x, y = top_at(F, to_px, 0.42, -4.5)
    pal = {'o': INK, 'w': PAPER[4], 'g': PAPER[2], 'n': hx('#4a4a4a'), 's': hx('#c8283a')}
    sprite(ic, x - 2, y - 7, ['oooooo', 'owwwwo', 'onnnwo', 'owgggo', 'onnwwo', 'owwsgo', 'oooooo'], pal)


def x_paperclip(ic, F, to_px):
    x, y = top_at(F, to_px, 0.5, -3.5)
    S, D = hx('#e6ecf0'), hx('#6a7480')
    sprite(ic, x - 2, y - 6, ['.SSS.', 'S...S', 'S.S.S', 'S.S.S', 'S.S.S', 'S.SDS', 'S...S', 'D...D', '.DDD.'],
           {'S': S, 'D': D})


def x_stamp(ic, F, to_px, col=STAMP_RED, txt=True):
    x, y = at(F, to_px, 0.42, 0.5)
    r = 4.3
    for yy in range(y - 6, y + 7):
        for xx in range(x - 6, x + 7):
            d = math.hypot(xx - x, yy - y)
            if abs(d - r) < 0.7 and h(xx, yy, 91) > 0.15:
                ic.set(xx, yy, col[:3] + (225,))
    if txt:
        for xx in range(x - 2, x + 3):
            if h(xx, y, 92) > 0.2:
                ic.set(xx, y, col[:3] + (230,))
        ic.set(x - 1, y - 2, col[:3] + (200,)); ic.set(x + 1, y + 2, col[:3] + (200,))


def x_catfish(ic, F, to_px):
    x_stamp(ic, F, to_px)


def x_badge(ic, F, to_px):
    x, y = at(F, to_px, 0.5, 0.55)
    pal = {'o': INK, 'w': PAPER[4], 'p': hx('#c8a07a'), 'b': hx('#2e60d8'), 'l': hx('#5a8cf0')}
    sprite(ic, x - 3, y - 6, ['..l..', '..b..', 'ooooo', 'obbbo', 'owpwo', 'owwwo', 'onnno', 'ooooo'],
           dict(pal, n=hx('#4a4a4a')))


def x_tag(ic, F, to_px):
    x, y = top_at(F, to_px, 0.55, -2.0)
    pal = {'o': hx('#2a1608'), 'b': hx('#c8c0a8'), 'l': hx('#f4ecd4'), 's': hx('#c8283a'), 'h': hx('#3a2a1a'), 'r': hx('#c8283a')}
    sprite(ic, x - 1, y - 11, ['..s....', '..s....', '..s....', '.ooooo.', 'ollhllo', 'olllllo', 'orrrrro', 'olbbllo', 'olllllo', 'obbbblo', '.ooooo.'], pal)


def x_teeth(ic, F, to_px):
    t, top, bot = F.edges(F.L - 1.8)
    vm = top + (bot - top) * F.mouth
    for i in range(3):
        x, y = to_px(F.L - 1.2 - i * 1.6 / F.k, vm + 0.9)
        ic.set(int(round(x)), int(round(y)), hx('#fff8e8'))


def x_tar(ic, F, to_px):
    for t, n in ((0.35, 3), (0.55, 4), (0.7, 2)):
        x, y = at(F, to_px, t, 1.0)
        for j in range(1, n + 1):
            ic.set(x, y + j, hx('#0a0806') if j < n else hx('#3a3040'))
        ic.set(x, y + n + 1, hx('#7a6a9a')[:3] + (160,))


def x_check(ic, F, to_px):
    x, y = at(F, to_px, 0.45, 0.48)
    G, D = hx('#3aa84a'), hx('#1a6a2a')
    for yy in range(y - 5, y + 6):
        for xx in range(x - 5, x + 6):
            d = math.hypot(xx - x, yy - y)
            if abs(d - 4.4) < 0.7 and h(xx, yy, 93) > 0.12:
                ic.set(xx, yy, G[:3] + (220,))
    sprite(ic, x - 2, y - 2, ['....G', '...G.', 'G.G..', '.G...'], {'G': D})


def x_frostspikes(ic, F, to_px):
    I = ramp('#1a3a5a', '#5a9ad0', '#9ad0f4', '#d8f2ff', '#f0faff', '#ffffff')
    for t, hh in ((0.32, 4), (0.42, 6), (0.52, 5), (0.62, 3)):
        x, y = top_at(F, to_px, t, 0.5)
        for j in range(hh):
            w = max(0, (hh - j) // 3)
            for i in range(-w, w + 1):
                ic.set(x + i, y - j, I[4] if i < 0 else I[2])
        ic.set(x, y - hh, I[5])


def x_zzz(ic, F, to_px):
    x, y = at(F, to_px, 0.95, 0.0)
    pal = {'z': hx('#e8f6ff'), 'b': hx('#5a9ad0')}
    sprite(ic, x - 1, y - 9, ['zzz', '.z.', 'zzz'], pal)
    sprite(ic, x + 3, y - 14, ['zzzz', '..z.', '.z..', 'zzzz'], pal)


def x_crest(ic, F, to_px):
    G = GLOW_LAVA
    for i, (t, hh) in enumerate(((0.86, 5), (0.9, 7), (0.94, 5))):
        x, y = top_at(F, to_px, t, 0.3)
        for j in range(hh):
            ic.set(x + (j // 3), y - j, G[min(3, j * 4 // hh)])


def x_glassbones(ic, F, to_px):
    B = hx('#7aa8c0')
    for i in range(70):
        t = 0.08 + 0.8 * i / 70
        x, y = at(F, to_px, t, 0.5)
        ic.set(x, y, hx('#3a6a86'))
    for t in [0.16 + 0.055 * i for i in range(11)]:
        for nv in (0.25, 0.32, 0.38, 0.44, 0.56, 0.62, 0.68, 0.74):
            x, y = at(F, to_px, t - (abs(nv - 0.5)) * 0.08, nv)
            if h(x, y, 94) > 0.15:
                ic.set(x, y, B[:3] + (210,))


def x_lamprey(ic, F, to_px):
    # gill pores instead of a gill slit, round sucker at the snout
    for i in range(7):
        x, y = at(F, to_px, 0.68 + i * 0.028, 0.45)
        ic.set(x, y, hx('#0c1420'))
    u = F.L
    t, top, bot = F.edges(F.L - 1.5)
    x, y = to_px(F.L - 0.6, (top + bot) / 2)
    x, y = int(round(x)), int(round(y))
    sprite(ic, x - 1, y - 3, ['.ooo', 'oppo', 'opwp', 'oppw', 'opwp', 'oppo', '.ooo'],
           {'o': hx('#0c1420'), 'p': hx('#c87888'), 'w': hx('#fff8e8')})


def x_halibut(ic, F, to_px):
    # second eye on the top edge
    x, y = at(F, to_px, 0.9, 0.12)
    sprite(ic, x - 2, y - 2, ['.oo.', 'oggo', 'oggo', '.oo.'], {'o': EYE_ICE[0], 'g': hx('#0c1420')})
    ic.set(x - 1, y - 1, hx('#ffffff'))


def x_scorch(ic, F, to_px):
    x_stamp(ic, F, to_px, col=hx('#1a0c08'), txt=False)
    x, y = at(F, to_px, 0.42, 0.5)
    for yy in range(y - 6, y + 7):
        for xx in range(x - 6, x + 7):
            d = math.hypot(xx - x, yy - y)
            if abs(d - 5.3) < 0.5 and h(xx, yy, 95) > 0.55:
                ic.set(xx, yy, hx('#ff8a1a'))
    sprite(ic, x - 1, y - 1, ['oo.', '.oo', 'o.o'], {'o': hx('#ffd04a')})


def x_finlets(ic, F, to_px):
    for t in (0.06, 0.11, 0.16):
        for nv, dv in ((0.0, -1.2), (1.0, 1.2)):
            u = F.TL + t * (F.L - F.TL)
            tt, top, bot = F.edges(u)
            x, y = to_px(u, (top if nv == 0 else bot) + dv)
            ic.set(int(round(x)), int(round(y)), F.fin[3])


def x_badge_notice(ic, F, to_px):
    x, y = at(F, to_px, 0.45, 0.5)
    R = ramp('#3a0a10', '#8a1422', '#c8283a', '#ec5a62', '#ffa8a8', '#ffe0e0')
    for yy in range(y - 5, y + 6):
        for xx in range(x - 5, x + 6):
            d = math.hypot(xx - x, yy - y) + 0.6 * math.sin(math.atan2(yy - y, xx - x) * 7)
            if d < 3.9:
                ic.set(xx, yy, R[3] if (xx - x) + (yy - y) < -1 else R[2] if d < 2.6 else R[1])
            elif d < 4.6:
                ic.set(xx, yy, R[0])
    sprite(ic, x - 1, y - 2, ['w.w', 'w.w', 'w.w', '...', '.w.'], {'w': R[5]})


def x_horns(ic, F, to_px):
    Bn = ramp('#2a2018', '#8a7a58', '#c8b890', '#e6dab8', '#fff8e8', '#ffffff')
    for t, ln in ((0.9, 7), (0.83, 6)):
        u0 = F.TL + t * (F.L - F.TL)
        tt, top, bot = F.edges(u0)
        for j in range(ln):
            q = j / F.k
            uu = u0 - q * 0.45 - 0.06 * q * q
            vv = top + 0.6 - q * 1.15
            x, y = to_px(uu, vv)
            x, y = int(round(x)), int(round(y))
            ic.set(x, y, Bn[4] if j == ln - 1 else Bn[3])
            if j < ln - 2:
                ic.set(x + 1, y, Bn[1])
                ic.set(x, y + 1, Bn[2]) if j < 2 else None


# ---- the 39 species
SPECIES = []


def add(zone, sid, name, rar, F):
    SPECIES.append((zone, sid, name, rar, F))


# Z1 Emerald Wilds: river greens and golds
add(1, 'overdue_minnow', 'Overdue Minnow', 'Normal', fish(
    L=54, TL=11, Ht=6.5, Hb=6, tmax=0.55, b=1.7, tw=7.5, fd=0.55, scale=3.0, ang=28,
    dorsal=[(0.45, 0.64, 4.5, 'tri')], anal=[(0.2, 0.36, 3, 'tri')], pect=(0.7, 0.62, 4.5, 1.6),
    eye=(0.86, 0.4, 2.6), eyecol=EYE_SILV,
    back=ramp('#10200c', '#3a5a2a', '#5a7a44', '#7a9a5a', '#a4c07a', '#dcecb0'),
    belly=Z1_SILV, fin=ramp('#1a2010', '#5a6a40', '#7a8a58', '#9aaa74', '#c0cc98', '#e8f0d0'),
    pattern=[('stripe', 0.4, 0.5, ramp('#10200c', '#1e3014', '#2a4018', '#38521e', '#4a6a2a', '#5a7a34'))]))

add(1, 'bluegill_of_good_standing', 'Bluegill of Good Standing', 'Normal', fish(
    L=50, TL=10, Ht=12, Hb=12, tmax=0.5, b=2.3, p=0.26, tw=9, fd=0.2, scale=3.5, ang=14,
    dorsal=[(0.25, 0.55, 5, 'spiny'), (0.55, 0.78, 6, 'round')], anal=[(0.15, 0.42, 5, 'round')],
    pect=(0.68, 0.55, 6, 2.0), eye=(0.87, 0.36, 2.4), eyecol=EYE_GOLD, mouth=0.45,
    back=ramp('#0c1a24', '#1e4a5a', '#2e6a6e', '#4a8a7a', '#74b090', '#b8e0b8'),
    belly=ramp('#3a1a06', '#b0601a', '#e08a2a', '#f4b04a', '#ffd480', '#fff0c8'),
    fin=ramp('#0c1a24', '#2a4a58', '#3e6670', '#5a8a88', '#8ab4a8', '#c8e4d8'),
    pattern=[('bars', 7, ramp('#0c1a24', '#18384a', '#225058', '#306a66', '#4a8a7a', '#6aa890'), 0.38, 0.75)],
    extra=x_bluegill))

add(1, 'rustback_trout', 'Rustback Trout', 'Normal', fish(
    L=58, TL=11, Ht=8, Hb=7.5, tmax=0.48, b=1.7, tw=8, fd=0.18, scale=2.5, ang=28,
    dorsal=[(0.48, 0.68, 6, 'tri'), (0.14, 0.19, 2.5, 'round')], anal=[(0.18, 0.33, 4, 'tri')],
    pect=(0.7, 0.66, 5.5, 1.8), eye=(0.88, 0.38, 2.4), eyecol=EYE_GOLD,
    back=ramp('#1e0c06', '#5a2a12', '#86401a', '#a85a24', '#c87e3e', '#eab070'),
    belly=Z1_GOLDB, fin=ramp('#1e0c06', '#6a3a1a', '#8a5226', '#a86e3a', '#c89058', '#e8c08a'),
    pattern=[('stripe', 0.42, 0.56, ramp('#3a0c10', '#9a3a3a', '#c45a50', '#de7a68', '#f0a08a', '#ffd0c0')),
             ('spots', 0.42, hx('#1a0c06'), 0.05, 0.5)]))

add(1, 'queue_perch', 'Queue Perch', 'Normal', fish(
    L=54, TL=10, Ht=9.5, Hb=9, tmax=0.48, b=1.9, tw=8, fd=0.3, scale=3.0, ang=22,
    dorsal=[(0.42, 0.66, 6, 'spiny'), (0.2, 0.38, 5, 'round')], anal=[(0.17, 0.32, 4.5, 'tri')],
    pelvic=(0.55, 5), pect=(0.7, 0.6, 5, 1.8), eye=(0.87, 0.36, 2.5), eyecol=EYE_GOLD,
    back=ramp('#14200a', '#4a6a1a', '#6e8a24', '#94aa30', '#bcc84a', '#e8ec90'),
    belly=Z1_GOLDB, fin=ramp('#3a1206', '#a8401a', '#d4602a', '#ec8a3a', '#f8b060', '#ffe0a8'),
    pattern=[('bars', 6, ramp('#0c1406', '#22300c', '#2e4210', '#3e5616', '#4e6a1c', '#5e7e24'), 0.3, 0.7)],
    extra=x_queue))

add(1, 'misfiled_carp', 'Misfiled Carp', 'Unique', fish(
    L=56, TL=12, Ht=10, Hb=10, tmax=0.48, b=2.0, tw=9.5, fd=0.42, scale=5.0, ang=22, barbels=1,
    dorsal=[(0.3, 0.75, 4.5, 'back')], anal=[(0.2, 0.32, 4, 'tri')],
    pect=(0.68, 0.66, 5.5, 2.0), eye=(0.88, 0.38, 2.4), eyecol=EYE_GOLD, mouth=0.5,
    back=ramp('#1e1406', '#5a4214', '#86621e', '#a8822a', '#ccaa48', '#f0dc8a'),
    belly=Z1_GOLDB, fin=ramp('#1e1006', '#6a3a14', '#8e5220', '#ae6e30', '#cc904a', '#ecc080'),
    extra=x_paperclip))

add(1, 'stamped_catfish', 'Stamped Catfish', 'Unique', fish(
    L=58, TL=11, Ht=7.5, Hb=8.5, tmax=0.62, b=3.2, p=0.35, tw=8, fd=0.3, scale=0, ang=24, barbels=3,
    dorsal=[(0.62, 0.76, 6, 'tri'), (0.1, 0.17, 2.5, 'round')], anal=[(0.05, 0.42, 4, 'low')],
    pect=(0.78, 0.62, 6, 2.0), eye=(0.9, 0.32, 1.8), eyecol=EYE_GOLD, mouth=0.48,
    back=ramp('#120e08', '#3a3220', '#564a30', '#726442', '#948660', '#c8bc90'),
    belly=ramp('#2a2418', '#9a9070', '#c0b894', '#dcd6b8', '#eeead6', '#fffcf0'),
    fin=ramp('#120e08', '#3a3020', '#544630', '#6e5e42', '#8e7e5c', '#b8aa86'),
    pattern=[('spots', 0.25, hx('#2a2214'), 0.05, 0.5)], extra=x_catfish))

add(1, 'mirebridge_eel', 'Mirebridge Eel', 'Unique', fish(
    L=66, TL=0.5, Ht=4.2, Hb=4.2, tmax=0.7, b=1.6, p=0.05, tail='point', wave=7.0, waven=0.95, pa=1.5, scale=0, ang=22,
    dorsal=[(0.0, 0.62, 2.6, 'low')], anal=[(0.0, 0.5, 2.4, 'low')], pelvic=None,
    pect=(0.8, 0.5, 3, 1.3), eye=(0.94, 0.38, 1.6), eyecol=EYE_GOLD, gill=0.84, lateral=False,
    back=ramp('#0c1408', '#2a3a14', '#3e521c', '#566c26', '#748a36', '#a8bc60'),
    belly=ramp('#2a2208', '#9a8a2a', '#c4b03a', '#ded05a', '#eee488', '#fffac0'),
    fin=ramp('#0c1408', '#3a4418', '#4e5a22', '#66742e', '#869440', '#b0bc6a'),
    pattern=[('spots', 0.35, hx('#1a2410'), 0.0, 0.55)]))

add(1, 'pondering_pike', 'Pondering Pike', 'Rare', fish(
    L=60, TL=11, Ht=6.5, Hb=6.5, tmax=0.45, b=1.25, p=0.45, tw=8, fd=0.42, scale=2.5, ang=32, snout=2.0,
    dorsal=[(0.1, 0.26, 5, 'round')], anal=[(0.08, 0.24, 4.5, 'round')], pelvic=(0.42, 3.5),
    pect=(0.74, 0.7, 4.5, 1.6), eye=(0.86, 0.32, 2.0), eyecol=EYE_GOLD, gill=0.74, mouth=0.52,
    back=ramp('#0a1a0c', '#24461e', '#346028', '#4a7a32', '#6a9a44', '#a8c87a'),
    belly=ramp('#28280e', '#a8a46a', '#cac68c', '#e2deb0', '#f2eed2', '#fffef0'),
    fin=ramp('#1a1408', '#6a4a1a', '#8e6424', '#ae8034', '#cca44e', '#ecd08a'),
    pattern=[('spots', 0.6, hx('#c4d88a'), 0.1, 0.6), ('finpat', ramp('#1a1408', '#3a2a10', '#4a3614', '#5a4418', '#6a521e', '#7a6024'), 'spots')]))

add(1, 'golden_receipt_koi', 'Golden Receipt Koi', 'Legendary', fish(
    L=56, TL=13, Ht=9.5, Hb=9.5, tmax=0.5, b=2.0, tw=11, fd=0.3, scale=4.5, ang=22, barbels=1,
    dorsal=[(0.3, 0.74, 5, 'back')], anal=[(0.2, 0.32, 4.5, 'tri')], tail='fork',
    pect=(0.68, 0.66, 7, 2.6), eye=(0.88, 0.38, 2.3), eyecol=EYE_SILV, mouth=0.5,
    back=ramp('#3a2004', '#b0700a', '#e09a14', '#f8c030', '#ffe070', '#fff8c8'),
    belly=ramp('#3a2004', '#c8901a', '#ecb83a', '#ffd860', '#fff09a', '#fffce0'),
    fin=ramp('#3a2a0c', '#b49a5a', '#d8c48a', '#eee2b8', '#faf4de', '#ffffff'),
    pattern=[('blotch', ramp('#2a2a2a', '#b8b4a4', '#dcd8c8', '#eeeade', '#faf8f0', '#ffffff'), 1.3, 1.25),
             ('flecks', 0.04, hx('#fffbe0')), ('finpat', ramp('#3a3a3a', '#8a8a8a', '#a8a8a8', '#c4c0b0', '#e0dcc8', '#f4f0e0'), 'edge')]))

add(1, 'departmental_goldfish', 'Departmental Goldfish', 'Fabled', fish(
    L=50, TL=17, Ht=11, Hb=12, tmax=0.52, b=2.6, p=0.4, tw=14, fd=0.38, scale=3.5, ang=12, tail='fork',
    dorsal=[(0.25, 0.75, 9, 'sail')], anal=[(0.15, 0.3, 6, 'back')], pelvic=(0.55, 6),
    pect=(0.66, 0.66, 6, 2.2), eye=(0.86, 0.38, 3.0), eyecol=EYE_GOLD, mouth=0.48,
    back=ramp('#3a0e04', '#a8300a', '#e05414', '#ff7a1e', '#ffa848', '#ffe0a0'),
    belly=ramp('#3a1a04', '#c86a14', '#f0942a', '#ffbc4a', '#ffdc80', '#fff6d0'),
    fin=ramp('#3a0e04', '#c04a1a', '#e8742a', '#ffa04a', '#ffcc88', '#fff0d8'),
    pattern=[('flecks', 0.05, hx('#fff2b0'))], extra=x_badge))



# Z2 Howling Sands: desert sand and amber
SAND_B = ramp('#2a1a08', '#7a5a2a', '#a8803e', '#caa458', '#e4c47a', '#fae8b0')
SAND_L = ramp('#3a2a14', '#b89a6a', '#d8bc8a', '#eed8aa', '#f8ead0', '#fffaf0')
AMBER_F = ramp('#2a1404', '#8a4a10', '#c06a14', '#e0901e', '#f4b848', '#ffe098')

add(2, 'oasis_carp', 'Oasis Carp', 'Normal', fish(
    L=56, TL=12, Ht=10, Hb=10, tmax=0.48, b=2.0, tw=9.5, fd=0.42, scale=5.0, ang=22, barbels=1,
    dorsal=[(0.3, 0.75, 4.5, 'back')], anal=[(0.2, 0.32, 4, 'tri')],
    pect=(0.68, 0.66, 5.5, 2.0), eye=(0.88, 0.38, 2.4), eyecol=EYE_GOLD, mouth=0.5,
    back=SAND_B, belly=SAND_L, fin=ramp('#0c2a2a', '#1e6a64', '#2e8e84', '#4ab0a0', '#7ad0c0', '#c0f0e4')))

add(2, 'sandskipper', 'Sandskipper', 'Normal', fish(
    L=54, TL=10, Ht=7, Hb=7.5, tmax=0.7, b=3.0, p=0.35, tw=7, tail='round', scale=0, ang=20,
    dorsal=[(0.62, 0.78, 9, 'sail'), (0.12, 0.55, 3.5, 'low')], anal=[(0.1, 0.5, 3, 'low')], pelvic=(0.66, 3),
    pect=(0.74, 0.7, 7, 2.6), eye=(0.9, 0.08, 2.8), eyecol=EYE_GOLD, gill=0.8, mouth=0.62,
    back=ramp('#20160a', '#6a5232', '#927448', '#b49662', '#d4b884', '#f0dcb0'),
    belly=SAND_L, fin=ramp('#20160a', '#6a4a2a', '#8e6a3e', '#b08c58', '#d0b080', '#f0dcb8'),
    pattern=[('spots', 0.5, hx('#4a3418'), 0.0, 0.6), ('finpat', ramp('#0c1a3a', '#1e3c8a', '#2e5ac0', '#4a80e0', '#80b0f8', '#c8e0ff'), 'edge')]))

add(2, 'dune_piranha', 'Dune Piranha', 'Normal', fish(
    L=50, TL=10, Ht=11, Hb=13, tmax=0.55, b=2.6, p=0.3, tw=9, fd=0.3, scale=2.5, ang=14,
    dorsal=[(0.42, 0.6, 5, 'tri')], anal=[(0.12, 0.42, 5, 'back')], pect=(0.72, 0.62, 5, 1.8),
    eye=(0.88, 0.32, 2.4), eyecol=EYE_RED, mouth=0.62,
    back=ramp('#1a1a1e', '#5a5a64', '#80808a', '#a4a2a8', '#c8c4c2', '#f0ece4'),
    belly=ramp('#3a0a06', '#a8301a', '#d4502a', '#ec7a3a', '#f8a868', '#ffd8b0'),
    fin=ramp('#1a1a1e', '#5a5048', '#7a6e60', '#9a8c78', '#bcae96', '#e0d4bc'),
    pattern=[('flecks', 0.06, hx('#fff0c0')), ('finpat', ramp('#0a0a0a', '#1a1414', '#2a2020', '#3a2c2a', '#4a3a36', '#5a4842'), 'edge')],
    extra=x_teeth))


def x_mirage(ic, F, to_px):
    """the back half shimmers away in heat haze (dithered alpha)"""
    for y in range(H):
        for x in range(W):
            c = ic.get(x, y)
            if c[3] == 0:
                continue
            a = 0
            # distance along the fish axis via to_px inverse is not kept; use the screen diagonal
            q = (x - y + 64) / 128
            if q < 0.33:
                a = 1 - q / 0.33
                if h(x, y, 101) < a * 0.75:
                    ic.px[x, y] = c[:3] + (round(255 * (0.25 + 0.5 * (1 - a))),)


add(2, 'mirage_eel', 'Mirage Eel', 'Unique', fish(
    L=66, TL=0.5, Ht=4.4, Hb=4.4, tmax=0.7, b=1.6, p=0.05, tail='point', wave=7.0, waven=0.95, pa=1.5, scale=0, ang=22,
    dorsal=[(0.0, 0.62, 2.6, 'low')], anal=[(0.0, 0.5, 2.4, 'low')], pelvic=None,
    pect=(0.8, 0.5, 3, 1.3), eye=(0.94, 0.38, 1.6), eyecol=EYE_TEAL, gill=0.84, lateral=False,
    back=ramp('#2a1a0a', '#8a6a3a', '#b4925a', '#d4b67a', '#ecd4a0', '#fff0d0'),
    belly=ramp('#2a2018', '#a898b0', '#c8bcd0', '#e0d8e8', '#f0ecf6', '#ffffff'),
    fin=ramp('#0c2a2a', '#3a8a8a', '#5ab0a8', '#80d0c4', '#b0ecdc', '#e8fff8'),
    pattern=[('bars', 9, ramp('#2a1a2a', '#8a7aa0', '#a898c0', '#c4b8d8', '#e0d8f0', '#ffffff'), 0.25, 0.6)],
    extra=x_mirage))

add(2, 'lost_luggage_grouper', 'Lost Luggage Grouper', 'Rare', fish(
    L=56, TL=10, Ht=11, Hb=11, tmax=0.5, b=2.4, p=0.36, tw=8.5, tail='round', scale=2.5, ang=16,
    dorsal=[(0.28, 0.58, 5, 'spiny'), (0.58, 0.8, 5.5, 'round')], anal=[(0.15, 0.32, 5, 'round')],
    pect=(0.7, 0.62, 6.5, 2.6), eye=(0.86, 0.3, 2.3), eyecol=EYE_GOLD, mouth=0.58, b2=None,
    back=ramp('#1e1006', '#5a3414', '#7e4c1e', '#a0682c', '#c48c48', '#e8bc80'),
    belly=ramp('#2a1a0c', '#a88a5a', '#ccae7a', '#e4cc9c', '#f2e2c0', '#fff6e4'),
    fin=ramp('#1e1006', '#5a3418', '#7a4a22', '#9a6430', '#ba8448', '#dcac76'),
    pattern=[('blotch', ramp('#2a1a0c', '#8a6a42', '#b0905e', '#d0b07c', '#e8cc9e', '#fff0d0'), 0.4, 1.05),
             ('spots', 0.3, hx('#2a160a'), 0.2, 0.9)],
    extra=x_tag))

add(2, 'tar_pit_gudgeon', 'Tar Pit Gudgeon', 'Unique', fish(
    L=54, TL=10, Ht=7.5, Hb=8, tmax=0.55, b=2.0, tw=7.5, fd=0.35, scale=3.0, ang=24, barbels=1,
    dorsal=[(0.42, 0.62, 5, 'tri')], anal=[(0.18, 0.32, 3.5, 'tri')], pect=(0.72, 0.68, 5, 1.8),
    eye=(0.86, 0.36, 2.2), eyecol=EYE_GOLD, mouth=0.56,
    back=ramp('#050406', '#141218', '#221e28', '#322c3a', '#4a4256', '#8a7aa8'),
    belly=ramp('#050406', '#2a2430', '#3a3242', '#4e4458', '#6a5e78', '#a090c0'),
    fin=ramp('#050406', '#16121a', '#241e2a', '#342c3c', '#4a3e56', '#6a5a80'),
    pattern=[('blotch', ramp('#0a0a0a', '#2a4a5a', '#3a6a6a', '#5a8a5a', '#8a9a4a', '#c8b060'), 2.2, 2.05)],
    extra=x_tar))

add(2, 'mirage_sturgeon', 'Mirage Sturgeon', 'Legendary', fish(
    L=60, TL=12, Ht=6.5, Hb=6, tmax=0.4, b=1.25, p=0.3, tail='heter', tw=9, scale=0, ang=26, snout=1.0, barbels=2,
    dorsal=[(0.08, 0.2, 4.5, 'tri')], anal=[(0.06, 0.16, 3.5, 'tri')], pelvic=(0.3, 3),
    pect=(0.78, 0.72, 5, 1.8), eye=(0.86, 0.34, 1.6), eyecol=EYE_GOLD, gill=0.78, mouth=0.85, lateral=False,
    back=ramp('#20160a', '#6a5030', '#8e6e44', '#b08e5e', '#d0b07e', '#f0d8a8'),
    belly=SAND_L, fin=AMBER_F,
    pattern=[('scutes', ramp('#2a1a04', '#a87a2a', '#d4a43a', '#f0c860', '#ffe898', '#fffad0'), (0.06, 0.45))]))

add(2, 'customs_cleared_sandsalmon', 'Customs-Cleared Sandsalmon', 'Fabled', fish(
    L=58, TL=11, Ht=8.5, Hb=7.5, tmax=0.48, b=1.6, tw=8.5, fd=0.25, scale=2.5, ang=26,
    dorsal=[(0.48, 0.66, 6, 'tri'), (0.14, 0.19, 2.5, 'round')], anal=[(0.17, 0.32, 4, 'tri')],
    pect=(0.7, 0.66, 5.5, 1.8), eye=(0.88, 0.36, 2.2), eyecol=EYE_SILV, mouth=0.5,
    back=ramp('#2a0c0a', '#8a3a2a', '#b85a3a', '#d87e52', '#eca878', '#ffd8b0'),
    belly=ramp('#2a2a2a', '#a8a8a0', '#ccccc4', '#e4e4dc', '#f2f2ec', '#ffffff'),
    fin=AMBER_F, pattern=[('spots', 0.3, hx('#5a1a10'), 0.05, 0.4), ('flecks', 0.03, hx('#fff0d0'))],
    extra=x_check))


# Z3 Whisperfrost: icy blues and whites
ICE_B = ramp('#0a1a2a', '#2a4a6a', '#3e6688', '#5a86a8', '#86acc8', '#c8e0f0')
ICE_W = ramp('#2a3440', '#a8b8c8', '#c8d6e2', '#e2ecf4', '#f2f8fc', '#ffffff')
ICE_F = ramp('#0a1a2a', '#4a6e90', '#6a90b0', '#90b4cc', '#bcd8e8', '#eaf6ff')

add(3, 'frost_cod', 'Frost Cod', 'Normal', fish(
    L=58, TL=10, Ht=8.5, Hb=8.5, tmax=0.55, b=1.9, tw=8, tail='trunc', scale=0, ang=24, barbels=1,
    dorsal=[(0.62, 0.78, 4.5, 'round'), (0.38, 0.58, 4, 'round'), (0.12, 0.33, 3.5, 'round')],
    anal=[(0.36, 0.56, 3.5, 'round'), (0.1, 0.32, 3.5, 'round')], pelvic=(0.72, 3.5),
    pect=(0.72, 0.6, 5, 1.8), eye=(0.88, 0.36, 2.3), eyecol=EYE_SILV, mouth=0.56,
    back=ramp('#141a20', '#4a5a66', '#6a7a86', '#8c9ca6', '#b4c2ca', '#e2ecf0'),
    belly=ICE_W, fin=ICE_F, pattern=[('spots', 0.55, hx('#3a4a56'), 0.05, 0.6), ('frostfin',)]))

add(3, 'whisper_char', 'Whisper Char', 'Normal', fish(
    L=56, TL=11, Ht=8, Hb=7.5, tmax=0.48, b=1.7, tw=8, fd=0.25, scale=2.0, ang=26,
    dorsal=[(0.48, 0.68, 6, 'tri'), (0.14, 0.19, 2.5, 'round')], anal=[(0.18, 0.33, 4, 'tri')],
    pect=(0.7, 0.66, 5.5, 1.8), eye=(0.88, 0.38, 2.3), eyecol=EYE_ICE,
    back=ramp('#0a1424', '#22385a', '#30507a', '#466c96', '#6a90b4', '#a8c8e0'),
    belly=ramp('#2a1a20', '#c87888', '#e09aa4', '#f0bcc2', '#f8dce0', '#fff4f6'),
    fin=ramp('#2a1018', '#9a4a5a', '#c06a78', '#da8e98', '#ecb4bc', '#ffe4e8'),
    pattern=[('spots', 0.55, hx('#e8f4ff'), 0.05, 0.55), ('frostfin',)]))

add(3, 'icebound_salmon', 'Icebound Salmon', 'Unique', fish(
    L=58, TL=11, Ht=8.5, Hb=7.5, tmax=0.48, b=1.6, tw=8.5, fd=0.25, scale=2.5, ang=26,
    dorsal=[(0.48, 0.66, 6, 'tri'), (0.14, 0.19, 2.5, 'round')], anal=[(0.17, 0.32, 4, 'tri')],
    pect=(0.7, 0.66, 5.5, 1.8), eye=(0.88, 0.36, 2.2), eyecol=EYE_SILV, mouth=0.5,
    back=ICE_B, belly=ICE_W, fin=ICE_F,
    pattern=[('frost', 0.12), ('spots', 0.2, hx('#1a3048'), 0.15, 0.4), ('frostfin',)]))

add(3, 'glass_pike', 'Glass Pike', 'Rare', fish(
    L=60, TL=11, Ht=6.5, Hb=6.5, tmax=0.45, b=1.25, p=0.45, tw=8, fd=0.42, scale=0, ang=32, snout=2.0,
    dorsal=[(0.1, 0.26, 5, 'round')], anal=[(0.08, 0.24, 4.5, 'round')], pelvic=(0.42, 3.5),
    pect=(0.74, 0.7, 4.5, 1.6), eye=(0.86, 0.32, 2.0), eyecol=EYE_ICE, gill=0.74, mouth=0.52, lateral=False,
    back=ramp('#1a3a4a', '#7ab4c8', '#9cd0e0', '#bce4f0', '#dcf4fa', '#ffffff'),
    belly=ramp('#1a3a4a', '#8ac4d4', '#a8dae6', '#c6ecf4', '#e2f8fc', '#ffffff'),
    fin=ramp('#1a3a4a', '#8ac0d0', '#acd8e6', '#cceef6', '#e8fafe', '#ffffff'),
    pattern=[('frostfin',)], extra=x_glassbones))

add(3, 'permit_lamprey', 'Permit Lamprey', 'Unique', fish(
    L=66, TL=0.5, Ht=4.2, Hb=4.2, tmax=0.75, b=3.0, p=0.05, tail='point', wave=7.0, waven=0.95, pa=1.5, scale=0, ang=22,
    dorsal=[(0.0, 0.3, 2.4, 'low'), (0.32, 0.55, 2.4, 'round')], anal=[(0.0, 0.22, 2.0, 'low')], pelvic=None,
    pect=None, eye=(0.9, 0.34, 1.5), eyecol=EYE_SILV, gill=-1, lateral=False,
    back=ramp('#0c141e', '#34465a', '#4a6078', '#647c94', '#8aa2b6', '#c4d4e0'),
    belly=ICE_W, fin=ICE_F, pattern=[('spots', 0.3, hx('#1a2636'), 0.0, 0.5)], extra=x_lamprey))

add(3, 'snowmelt_trout', 'Snowmelt Trout', 'Normal', fish(
    L=58, TL=11, Ht=8, Hb=7.5, tmax=0.48, b=1.7, tw=8, fd=0.18, scale=2.5, ang=28,
    dorsal=[(0.48, 0.68, 6, 'tri'), (0.14, 0.19, 2.5, 'round')], anal=[(0.18, 0.33, 4, 'tri')],
    pect=(0.7, 0.66, 5.5, 1.8), eye=(0.88, 0.38, 2.4), eyecol=EYE_SILV,
    back=ramp('#0a2024', '#2a5a5e', '#3e787a', '#5a9896', '#86bcb6', '#c8e8e0'),
    belly=ICE_W, fin=ramp('#0a2024', '#3a6a6a', '#548a88', '#78aaa6', '#a4ccc6', '#dcf4ee'),
    pattern=[('stripe', 0.42, 0.56, ramp('#2a1a3a', '#9a7ab8', '#b896d0', '#d2b6e4', '#e8d6f2', '#fbf2ff')),
             ('spots', 0.4, hx('#1a3a6a'), 0.05, 0.5), ('frostfin',)]))

add(3, 'whisper_sturgeon', 'Whisper Sturgeon', 'Rare', fish(
    L=60, TL=12, Ht=6.5, Hb=6, tmax=0.4, b=1.25, p=0.3, tail='heter', tw=9, scale=0, ang=26, snout=1.0, barbels=2,
    dorsal=[(0.08, 0.2, 4.5, 'tri')], anal=[(0.06, 0.16, 3.5, 'tri')], pelvic=(0.3, 3),
    pect=(0.78, 0.72, 5, 1.8), eye=(0.86, 0.34, 1.6), eyecol=EYE_ICE, gill=0.78, mouth=0.85, lateral=False,
    back=ICE_B, belly=ICE_W, fin=ICE_F,
    pattern=[('scutes', ICE_W, (0.06, 0.45)), ('frost', 0.06), ('frostfin',)]))


add(3, 'blizzard_halibut', 'Blizzard Halibut', 'Legendary', fish(
    L=54, TL=9, Ht=12, Hb=12, tmax=0.5, b=2.2, p=0.22, tw=9, tail='trunc', scale=0, ang=14, flat=True,
    dorsal=[(0.08, 0.86, 4, 'low')], anal=[(0.08, 0.72, 4, 'low')], pelvic=None,
    pect=(0.7, 0.55, 5, 2.0), eye=(0.86, 0.22, 2.0), eyecol=EYE_ICE, gill=0.74, mouth=0.4, lateral=True,
    back=ramp('#1a2230', '#5a6e84', '#7a90a6', '#9cb2c6', '#c4d6e4', '#f0f8ff'),
    belly=ICE_W, fin=ICE_F,
    pattern=[('blotch', ramp('#1a2230', '#3a4c62', '#4c6078', '#62788e', '#7c92a8', '#a0b4c8'), 0.9, 1.4),
             ('spots', 0.14, hx('#e8f6ff'), 0.0, 1.0), ('frost', 0.05), ('frostfin',)], extra=x_halibut))

add(3, 'the_sleeper_in_aisle_9', 'The Sleeper in Aisle 9', 'Mythic', fish(
    L=56, TL=10, Ht=12, Hb=12, tmax=0.5, b=2.5, p=0.34, tw=9, tail='round', scale=4.0, ang=10,
    dorsal=[(0.28, 0.58, 4, 'spiny'), (0.58, 0.8, 5, 'round')], anal=[(0.15, 0.32, 5, 'round')],
    pect=(0.7, 0.62, 6.5, 2.6), eye=(0.86, 0.32, 2.4), eyecol=EYE_ICE, mouth=0.6, sleep=True,
    back=ramp('#06101e', '#14284a', '#1e3a66', '#2e5486', '#4a78aa', '#8ab4dc'),
    belly=ramp('#141e2a', '#6a84a0', '#8ea6c0', '#b2c8dc', '#d4e4f0', '#f4faff'),
    fin=ramp('#06101e', '#2a4a74', '#3e6694', '#5a88b4', '#88b0d4', '#c8e4f8'),
    pattern=[('frost', 0.08), ('frostfin',)], extra=lambda ic, F, tp: (x_frostspikes(ic, F, tp), x_zzz(ic, F, tp))))


# Z4 Devastated Lands: lava reds and obsidian with glowing cracks
OBS = ramp('#06040a', '#1a1420', '#2a2030', '#3c2e42', '#56425c', '#7a6280')
OBS_R = ramp('#0a0404', '#2a0c0c', '#4a1414', '#6a1e1a', '#8e2e22', '#c04a30')
LAVA_F = ramp('#1a0402', '#8a1a08', '#c03a0e', '#e86414', '#ff9a2a', '#ffd870')

add(4, 'cinderfin', 'Cinderfin', 'Normal', fish(
    L=56, TL=11, Ht=8.5, Hb=8.5, tmax=0.5, b=1.8, tw=8.5, fd=0.45, scale=0, ang=24,
    dorsal=[(0.38, 0.72, 6, 'tri')], anal=[(0.18, 0.36, 4, 'tri')], pect=(0.7, 0.62, 5.5, 2.0),
    eye=(0.88, 0.36, 2.3), eyecol=EYE_RED, back=OBS, belly=OBS_R, fin=LAVA_F, glow=GLOW_LAVA, lateral=False,
    pattern=[('cracks', 0.45), ('flame',)]))



def ray_shape(F, u, v):
    """Slag Ray seen from above: rounded diamond disc + whip tail (u: tail tip -> snout)"""
    d0 = 22.0
    if d0 <= u <= F.L:
        a = (u - d0) / (F.L - d0)
        if a < 0.42:
            hw = 21 * (a / 0.42) ** 0.75
        else:
            hw = 21 * ((1 - a) / 0.58) ** 0.85
        hw += 2.5 * math.sin(math.pi * a)
        if abs(v) <= hw:
            return ('body', a, (v + hw) / (2 * hw))
    if 0 <= u < d0 + 1:
        w = 0.9 + 0.9 * (u / d0)
        if abs(v - 0.8 * math.sin(u * 0.25)) <= w:
            return ('tail', 1 - u / d0, 0.0)
    return None


def x_ray(ic, F, to_px):
    # eyes + spiracles on top, a ridge of spines along the spine, glowing wing rims
    for side in (-1, 1):
        x, y = to_px(F.L - 6.5, side * 3.2)
        x, y = int(round(x)), int(round(y))
        sprite(ic, x - 1, y - 1, ['.o.', 'oeo', '.o.'], {'o': hx('#06040a'), 'e': hx('#ffd04a')})
        x, y = to_px(F.L - 9.5, side * 3.6)
        ic.set(int(round(x)), int(round(y)), hx('#06040a'))
    for i in range(14):
        x, y = to_px(F.L - 12 - i * 1.6, 0)
        ic.set(int(round(x)), int(round(y)), hx('#ffd04a') if i % 2 else hx('#c04a30'))
    for (x, y), c in F._lab.items():
        if c[0] == 'body' and (c[2] < 0.06 or c[2] > 0.94) and h(x, y, 111) < 0.4:
            ic.px[x, y] = GLOW_LAVA[1] if c[2] < 0.5 else GLOW_LAVA[0]


add(4, 'slag_ray', 'Slag Ray', 'Unique', fish(
    L=56, TL=0, Ht=1, Hb=1, ang=40, shape=ray_shape, eye=None, gill=-1, mouth=None, pect=None, flat=True,
    scale=0, lateral=False, split=2, back=OBS, belly=OBS, fin=ramp('#06040a', '#2a2030', '#3c2e42', '#56425c', '#7a6280', '#a088a8'),
    glow=GLOW_LAVA, pattern=[('cracks', 0.38)], extra=x_ray))

add(4, 'ashen_eel', 'Ashen Eel', 'Unique', fish(
    L=66, TL=0.5, Ht=4.4, Hb=4.4, tmax=0.7, b=1.6, p=0.05, tail='point', wave=7.0, waven=0.95, pa=1.5, scale=0, ang=22,
    dorsal=[(0.0, 0.62, 2.6, 'low')], anal=[(0.0, 0.5, 2.4, 'low')], pelvic=None,
    pect=(0.8, 0.5, 3, 1.3), eye=(0.94, 0.38, 1.6), eyecol=EYE_RED, gill=0.84, lateral=False,
    back=ramp('#0c0a0a', '#3a3634', '#54504c', '#706a64', '#948c84', '#c4bab0'),
    belly=ramp('#1a0c08', '#5a2a1a', '#7a3a22', '#9a5030', '#b86c44', '#d8946a'),
    fin=ramp('#0c0a0a', '#2a1a14', '#3a241a', '#4e3022', '#663e2c', '#8a5a40'), glow=GLOW_LAVA,
    pattern=[('bio', 0.35, 0.0, 0.7)]))

add(4, 'stamp_scorched_kingfish', 'Stamp-Scorched Kingfish', 'Rare', fish(
    L=62, TL=12, Ht=7, Hb=7, tmax=0.5, b=1.5, p=0.18, tail='lunate', tw=10, fd=0.6, scale=0, ang=26,
    dorsal=[(0.62, 0.8, 6, 'back'), (0.28, 0.4, 4, 'tri')], anal=[(0.26, 0.38, 3.5, 'tri')],
    pect=(0.74, 0.55, 6, 1.6), eye=(0.9, 0.38, 2.0), eyecol=EYE_RED, mouth=0.55,
    back=ramp('#0a0606', '#3a1a14', '#5a2a1e', '#7a3c28', '#a05a3a', '#d08860'),
    belly=ramp('#1a1210', '#8a7064', '#ae9282', '#ccb2a0', '#e4d0c0', '#f8ece0'),
    fin=ramp('#0a0606', '#4a1e14', '#6a2c1c', '#8e4024', '#b45a30', '#e08a50'),
    pattern=[('bars', 14, ramp('#0a0606', '#1e0c0a', '#2a1210', '#3a1a14', '#4a2218', '#5a2a1e'), 0.3, 0.45)],
    extra=lambda ic, F, tp: (x_finlets(ic, F, tp), x_scorch(ic, F, tp))))

add(4, 'magma_marlin', 'Magma Marlin', 'Legendary', fish(
    L=60, TL=12, Ht=7, Hb=6.5, tmax=0.45, b=1.4, p=0.16, tail='lunate', tw=11, fd=0.65, scale=0, ang=24, snout=10,
    dorsal=[(0.25, 0.86, 10, 'back')], anal=[(0.14, 0.3, 4.5, 'tri')], pelvic=(0.7, 5),
    pect=(0.78, 0.66, 6, 1.4), eye=(0.9, 0.4, 2.0), eyecol=EYE_RED, mouth=0.55, lateral=False,
    back=OBS, belly=OBS_R, fin=LAVA_F, glow=GLOW_LAVA,
    pattern=[('cracks', 0.75), ('flame',)]))

add(4, 'refund_pending_phoenixfish', 'Refund-Pending Phoenixfish', 'Mythic', fish(
    L=58, TL=20, Ht=9, Hb=8.5, tmax=0.5, b=1.8, p=0.3, tail='fork', tw=15, fd=0.55, scale=3.0, ang=18,
    dorsal=[(0.2, 0.8, 9, 'sail')], anal=[(0.12, 0.42, 6, 'back')], pelvic=(0.6, 6),
    pect=(0.72, 0.62, 8, 2.4), eye=(0.88, 0.36, 2.2), eyecol=EYE_GOLD, mouth=0.52,
    back=ramp('#3a0804', '#a8200a', '#d8400e', '#f06a18', '#ffa030', '#ffe080'),
    belly=ramp('#3a1a04', '#d07a14', '#f0a024', '#ffc840', '#ffe480', '#fff8d0'),
    fin=LAVA_F, glow=GLOW_LAVA, pattern=[('flame',), ('flecks', 0.06, hx('#fff4b0'))], extra=x_crest))


# Z5 Dinosaur Caves: bioluminescent purples and teals
CAVE_P = ramp('#0a0614', '#241838', '#36244e', '#4a3466', '#664c86', '#9478b4')
CAVE_T = ramp('#04141a', '#0e3a44', '#16525a', '#226c70', '#3a8e88', '#6ac0b0')
CAVE_F = ramp('#0a0614', '#2e1e4a', '#422c66', '#5a3e86', '#7c5aac', '#b090dc')
GHOST = ramp('#1a1424', '#8a80a0', '#aaa0be', '#c8c0d8', '#e2dcee', '#faf8ff')
EYE_MILK = ramp('#2a2434', '#8a84a0', '#b4aec8', '#d4d0e2', '#ecebf4', '#ffffff')

add(5, 'blind_gar', 'Blind Gar', 'Normal', fish(
    L=58, TL=10, Ht=5.5, Hb=5.5, tmax=0.45, b=1.2, p=0.55, tail='round', tw=7, scale=2.5, ang=30, snout=7,
    dorsal=[(0.08, 0.2, 4.5, 'round')], anal=[(0.06, 0.18, 4, 'round')], pelvic=(0.45, 3),
    pect=(0.82, 0.7, 4, 1.4), eye=(0.9, 0.38, 1.6), eyecol=EYE_MILK, blind=True, mouth=0.5,
    back=GHOST, belly=ramp('#1a1424', '#a8a0b8', '#c8c0d4', '#e0dae8', '#f0ecf6', '#ffffff'),
    fin=ramp('#1a1424', '#7a6e94', '#9a8eb4', '#b8aed0', '#d6cee6', '#f4f0ff'), glow=GLOW_BIO,
    pattern=[('bio', 0.12, 0.3, 0.6)]))

add(5, 'fossil_coelacanth', 'Fossil Coelacanth', 'Unique', fish(
    L=56, TL=11, Ht=9.5, Hb=9.5, tmax=0.5, b=2.0, p=0.42, tail='round', tw=10, scale=3.5, ang=18,
    dorsal=[(0.58, 0.74, 7, 'tri'), (0.22, 0.34, 5, 'round')], anal=[(0.2, 0.32, 5, 'round')], pelvic=(0.5, 5),
    pect=(0.7, 0.62, 7, 2.2), eye=(0.87, 0.36, 2.4), eyecol=EYE_TEAL, mouth=0.55,
    back=ramp('#060a1a', '#14244a', '#1e3466', '#2c4884', '#4a68a8', '#8aa4d4'),
    belly=ramp('#0a0e20', '#2a3a6a', '#3a4c84', '#52649e', '#7484bc', '#a8b4dc'),
    fin=ramp('#060a1a', '#1e2c5a', '#2c3c74', '#3e5090', '#5a6eae', '#8a9cd0'), glow=GLOW_BIO,
    pattern=[('blotch', ramp('#1a1a2a', '#a8b0c8', '#c8d0e0', '#e2e8f2', '#f2f6fc', '#ffffff'), 2.7, 2.0),
             ('bio', 0.1, 0.1, 0.9)]))


def x_drake(ic, F, to_px):
    x_horns(ic, F, to_px)


add(5, 'drake_eel', 'Drake-Eel', 'Rare', fish(
    L=68, TL=0.5, Ht=5.0, Hb=4.4, tmax=0.78, b=1.9, p=0.05, tail='point', wave=7.0, waven=0.95, pa=1.5, scale=2.5, ang=22,
    dorsal=[(0.05, 0.8, 3.4, 'low')], anal=[(0.0, 0.5, 2.4, 'low')], pelvic=None,
    pect=(0.8, 0.55, 4.5, 1.8), eye=(0.93, 0.36, 1.8), eyecol=EYE_RED, gill=0.86, lateral=False,
    back=CAVE_T, belly=ramp('#1a0a1a', '#6a3a6a', '#8a4e86', '#a868a4', '#c890c4', '#ecc4e8'),
    fin=ramp('#1a0614', '#5a1a3a', '#7a2a4e', '#a03e66', '#c85a84', '#f08ab0'), glow=GLOW_BIOP,
    pattern=[('bio', 0.25, 0.0, 0.45), ('finpat', ramp('#1a0614', '#3a0e24', '#4e1430', '#661c3e', '#80264e', '#a03462'), 'spots')],
    extra=x_drake))

add(5, 'bone_pit_sturgeon', 'Bone Pit Sturgeon', 'Rare', fish(
    L=60, TL=12, Ht=6.5, Hb=6, tmax=0.4, b=1.25, p=0.3, tail='heter', tw=9, scale=0, ang=26, snout=1.0, barbels=2,
    dorsal=[(0.08, 0.2, 4.5, 'tri')], anal=[(0.06, 0.16, 3.5, 'tri')], pelvic=(0.3, 3),
    pect=(0.78, 0.72, 5, 1.8), eye=(0.86, 0.34, 1.6), eyecol=EYE_TEAL, gill=0.78, mouth=0.85, lateral=False,
    back=CAVE_P, belly=ramp('#140e1e', '#5a5070', '#76698e', '#9284ac', '#b4a8c8', '#dcd4ea'), fin=CAVE_F,
    glow=GLOW_BIO, pattern=[('scutes', ramp('#2a2018', '#9a8a68', '#c8b890', '#e6dab8', '#fff8e8', '#ffffff'), (0.06, 0.45, 0.85)),
                            ('bio', 0.08, 0.2, 0.4)]))

add(5, 'pondersaur', 'Pondersaur', 'Legendary', fish(
    L=58, TL=12, Ht=8.5, Hb=8, tmax=0.45, b=1.6, p=0.2, tail='lunate', tw=12, fd=0.7, scale=0, ang=22, snout=7,
    dorsal=[(0.38, 0.6, 8, 'tri')], anal=None, pelvic=(0.3, 6),
    pect=(0.72, 0.7, 9, 2.6), eye=(0.86, 0.34, 3.0), eyecol=EYE_TEAL, mouth=0.5, gill=-1,
    back=CAVE_T, belly=ramp('#141a1a', '#6a8a84', '#8aaaa2', '#aac8c0', '#cce4dc', '#f0fffa'),
    fin=ramp('#04141a', '#14485a', '#1e6070', '#2e7c88', '#4aa0a4', '#86d0c8'), glow=GLOW_BIO,
    pattern=[('bars', 6, ramp('#0a0614', '#2a1a40', '#3a2656', '#4e3470', '#6a4890', '#9070b8'), 0.3, 0.5),
             ('bio', 0.2, 0.0, 0.5)],
    extra=lambda ic, F, tp: x_teeth(ic, F, tp)))


def x_runes(ic, F, to_px):
    # a glowing rune line along the flank (dashes + dots)
    G = F.glow
    for i in range(60):
        t = 0.12 + 0.7 * i / 60
        if (i // 3) % 3 == 2:
            continue
        x, y = at(F, to_px, t, 0.52 + 0.08 * math.sin(i * 0.9))
        ic.set(x, y, G[2] if i % 3 else G[3])


def x_leviathan(ic, F, to_px):
    x_runes(ic, F, to_px)
    x_teeth(ic, F, to_px)
    x_horns(ic, F, to_px)
    x_badge_notice(ic, F, to_px)


add(5, 'final_notice_leviathan', 'Final Notice Leviathan', 'Mythic', fish(
    L=72, TL=0.5, Ht=6.0, Hb=5.4, tmax=0.86, b=2.2, p=0.05, tail='point', wave=7.0, waven=0.95, pa=1.5, scale=3.0, ang=22,
    dorsal=[(0.04, 0.86, 3.6, 'spiny')], anal=[(0.0, 0.55, 2.4, 'low')], pelvic=None,
    pect=(0.8, 0.6, 5.5, 2.2), eye=(0.93, 0.36, 2.0), eyecol=EYE_RED, gill=0.86, lateral=False,
    back=CAVE_P, belly=ramp('#1a0a1a', '#4a2a5a', '#5e3872', '#76488c', '#9466ac', '#c094d8'),
    fin=ramp('#0a0614', '#3a1a5a', '#5a2a86', '#7a3eb0', '#a060d8', '#d4a8ff'), glow=GLOW_BIOP,
    pattern=[('bio', 0.3, 0.0, 0.5)], extra=x_leviathan))



# ================================================================ junk + Lost Property (mask painter)
def _m(fn):
    im = Image.new('1', (W, H), 0)
    fn(ImageDraw.Draw(im))
    px = im.load()
    return {(x, y) for x in range(W) for y in range(H) if px[x, y]}


def mpoly(pts):
    return _m(lambda d: d.polygon(pts, fill=1))


def mrect(x0, y0, x1, y1):
    return {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}


def mell(x0, y0, x1, y1):
    return _m(lambda d: d.ellipse((x0, y0, x1, y1), fill=1))


def mline(pts, w=1):
    return _m(lambda d: d.line(pts, fill=1, width=w))


def paint(ic, mask, R, grad=1.3, noise=0.07, seed=0, edge=True, shadow=True):
    """bevel-shade a part lit from the top-left; 1-px darker rim inside where it overlaps older parts"""
    if not mask:
        return
    ys = [y for _, y in mask]
    xs = [x for x, _ in mask]
    y0, y1, x0, x1 = min(ys), max(ys), min(xs), max(xs)
    hh, ww = max(1, y1 - y0), max(1, x1 - x0)
    if shadow:
        for x, y in mask:
            for q in ((x + 1, y + 1),):
                if q not in mask and ic.get(*q)[3] == 255:
                    c = ic.get(*q)
                    ic.px[q] = (round(c[0] * 0.7), round(c[1] * 0.7), round(c[2] * 0.7), 255)
    for x, y in mask:
        g = (y - y0) / hh * 0.7 + (x - x0) / ww * 0.3
        lvl = 4 - int(g * grad * 2.2)
        if edge:
            if (x - 1, y) not in mask or (x, y - 1) not in mask:
                lvl = 5 if lvl >= 3 else lvl + 2
            elif (x + 1, y) not in mask or (x, y + 1) not in mask:
                lvl = min(lvl, 2) - 0
        r = h(x, y, 200 + seed)
        if r < noise:
            lvl -= 1
        elif r > 1 - noise * 0.5:
            lvl += 1
        ic.px[x, y] = R[clamp(lvl, 1, 5)]
    # inner contour against older parts
    for x, y in mask:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in mask and ic.get(*q)[3] == 255 and q not in _PAINTED_NOW:
                pass


_PAINTED_NOW = set()


def finish_item(ic, oc):
    outline_cols(ic, None, lambda x, y: oc)


def drops(ic, pts):
    for x, y in pts:
        sprite(ic, x, y, ['..a..', '.aba.', 'abcda', 'abdda', '.aaa.'],
               {'a': hx('#1a3a5a'), 'b': hx('#9ad0f4'), 'c': hx('#ffffff'), 'd': hx('#5a9ad0')})


BOOT = ramp('#140c06', '#3a2414', '#54361e', '#6e4a2a', '#8e643a', '#b48a5a')
SOLE = ramp('#0a0806', '#22201c', '#34302a', '#48423a', '#5e584e', '#7a7468')
WOOD = ramp('#1a0e06', '#5a3418', '#7e4c22', '#a0682e', '#c08a44', '#e0b070')
METAL = ramp('#141820', '#4a525e', '#6e7884', '#949ea8', '#bcc4cc', '#eef2f4')
GOLD = ramp('#2a1a04', '#8a5e10', '#c08a1a', '#e4b432', '#f8d868', '#fff4c0')
RUBBER = ramp('#1a0606', '#5a1414', '#7e1e1a', '#a42c22', '#c84a36', '#e8806a')
SEAWEED = ramp('#04140a', '#0e3a1a', '#185a26', '#267a34', '#3ea04a', '#80d07a')
BONE = ramp('#2a2018', '#8a7a58', '#b4a47c', '#d4c8a0', '#ece4c8', '#fffbee')
LEATH = ramp('#140a06', '#4a2414', '#6a341c', '#8a4826', '#ac6438', '#d08c5a')
CARD = ramp('#1e1408', '#7a5a30', '#9e7842', '#bc9656', '#d6b474', '#f0d8a4')
VELVET = ramp('#0e0618', '#2e1450', '#42206e', '#5a2e8e', '#7a48b4', '#a878e0')
WAX = ramp('#2a0606', '#7a1010', '#a81c1a', '#d0302a', '#ec5a4a', '#ffa090')
TIN = ramp('#10161a', '#3a4a52', '#566a74', '#748c96', '#9cb4bc', '#d4e6ea')


def it_boot(ic):
    shaft = mpoly([(18, 8), (34, 8), (35, 34), (30, 38), (18, 38)])
    foot = mpoly([(18, 30), (34, 30), (48, 36), (54, 42), (54, 48), (18, 48)])
    paint(ic, shaft | foot, BOOT, seed=1)
    paint(ic, mrect(16, 48, 55, 52), SOLE, seed=2)
    paint(ic, mrect(16, 6, 36, 10), ramp('#140c06', '#4a2e18', '#664024', '#845632', '#a67446', '#ca9a68'), seed=3)
    for y in range(14, 34, 4):           # laces
        for x in range(27, 33):
            if (x + y // 4) % 2 == 0:
                ic.set(x, y, hx('#d8c8a0'))
        ic.set(26, y, hx('#140c06')); ic.set(33, y, hx('#140c06'))
    for i in range(22, 54, 3):           # stitching on the sole seam
        ic.set(i, 46, hx('#c8a878'))
    for x, y in ((24, 20), (40, 40), (21, 42), (45, 44)):   # wet patches
        for dx in range(3):
            ic.set(x + dx, y, hx('#2a1a10'))
    sprite(ic, 46, 30, ['.gg', 'g..', 'g..'], {'g': hx('#3ea04a')})       # weed caught on the toe
    finish_item(ic, hx('#0a0604'))
    drops(ic, [(40, 55), (8, 40)])


def paper(ic, x0, y0, x1, y1, R=PAPER, curl=True, seed=5):
    m = mrect(x0, y0, x1, y1)
    if curl:
        m -= mpoly([(x1 - 6, y0 - 1), (x1 + 1, y0 - 1), (x1 + 1, y0 + 6)])
    paint(ic, m, R, grad=0.7, noise=0.05, seed=seed)
    if curl:
        paint(ic, mpoly([(x1 - 6, y0), (x1, y0 + 6), (x1 - 6, y0 + 6)]), R, grad=0.4, seed=seed + 1)
    return m


def it_form(ic):
    WET = ramp('#2a2a24', '#a8a490', '#c8c4ae', '#e0dcc8', '#eeeadc', '#fbfaf2')
    paper(ic, 14, 8, 50, 56, WET)
    pal = {'k': hx('#3a3a4a'), 'b': hx('#2e4a8a')}
    sprite(ic, 18, 12, ['kkk.k.kkk..kk.k.kkk', 'k...k.k.k..k..k.k.k', 'kk..k.kk..kk..k.kkk'], pal)
    for y in range(20, 52, 4):           # ink lines bleeding
        for x in range(18, 46):
            r = h(x, y, 300)
            if r < 0.7:
                ic.set(x, y, hx('#5a6a9a') if r < 0.5 else hx('#8a9ac0'))
            if r < 0.08:
                ic.set(x, y + 1, hx('#8a9ac0'))
    for y in range(30, 48):              # water stain
        for x in range(22, 42):
            if (x - 32) ** 2 / 100 + (y - 39) ** 2 / 64 < 1 and h(x, y, 301) < 0.5:
                ic.set(x, y, hx('#b4b8b0'))
    sprite(ic, 36, 44, ['.rrr.', 'r...r', 'r.r.r', 'r...r', '.rrr.'], {'r': STAMP_RED})
    finish_item(ic, hx('#2a2a24'))
    drops(ic, [(6, 30), (53, 50)])


def it_ticket(ic):
    T = ramp('#2a2410', '#a89a5a', '#ccbe7a', '#e4d89a', '#f2eabc', '#fffce0')
    m = mpoly([(8, 22), (56, 14), (58, 40), (10, 48)])
    paint(ic, m, T, grad=0.6, seed=7)
    for i in range(0, 34, 3):            # perforation
        x, y = 45 + i * 0.04, 16 + i * 0.75
        ic.set(round(46 + i * 0.05), round(16 + i * 0.8), hx('#6a5a2a'))
    pal = {'k': hx('#2a2a3a')}
    digits = ['kkk.kkk.kkk', 'k.k.k.k.k.k', 'kkk.kkk.kkk', '..k...k...k', '..k...k...k']
    sprite(ic, 14, 28, ['k.k..kk', 'kkk..k.', '..k..kk'], pal)            # "No"
    sprite(ic, 24, 26, ['k.k.kkk.kkk', 'k.k.k.k.k.k', 'kkk.k.k.k.k', '..k.k.k.k.k', '..k.kkk.kkk'], pal)  # 4 0 0
    for x in range(14, 42):
        if h(x, 36, 310) < 0.6:
            ic.set(x, 36 + (x // 9) % 2, hx('#8a7a4a'))
    for y in range(18, 46):              # wet fold
        ic.set(30 + (y // 7), y, hx('#a8984a'))
    sprite(ic, 49, 24, ['.r.', 'rrr', '.r.'], {'r': hx('#c8283a')})
    finish_item(ic, hx('#2a2410'))
    drops(ic, [(24, 51)])


def it_stamp(ic):
    paint(ic, mell(22, 6, 42, 20), WOOD, seed=9)                       # knob
    paint(ic, mrect(28, 18, 36, 34), WOOD, seed=10)                    # neck
    paint(ic, mrect(14, 34, 50, 42), METAL, seed=11)                   # plate
    paint(ic, mrect(16, 42, 48, 50), RUBBER, seed=12)                  # rubber
    for x in range(18, 47):                                            # mirrored "APPROVED" grooves
        if h(x, 46, 320) < 0.55:
            ic.set(x, 46, hx('#5a1414'))
    sprite(ic, 26, 9, ['.ww.', 'w...'], {'w': hx('#f0d8a4')})
    for x, y in ((20, 37), (44, 37)):
        ic.set(x, y, hx('#2a3038')); ic.set(x - 1, y - 1, hx('#eef2f4'))
    # moss / green water line on the knob
    for x in range(24, 41):
        if h(x, 15, 321) < 0.5:
            ic.set(x, 15 + int(h(x, 16, 322) * 2), hx('#3e7a3a'))
    sprite(ic, 8, 52, ['rr.r.rr', 'r.r..r.', 'rr...rr'], {'r': hx('#c8283a')})   # smudged ink below
    finish_item(ic, hx('#100806'))
    drops(ic, [(50, 22)])


def it_seaweed(ic):
    import random
    for k_, (bx, ln, sw, seed) in enumerate(((22, 46, 1.0, 1), (32, 52, -1.0, 2), (42, 40, 1.0, 3), (28, 34, -1.0, 4))):
        pts = []
        for i in range(ln):
            y = 58 - i
            x = bx + sw * 5 * math.sin(i * 0.16 + seed)
            pts.append((x, y))
        m = set()
        for i, (x, y) in enumerate(pts):
            w = 2.6 * (1 - i / ln) + 1.0 + 0.9 * math.sin(i * 0.5 + seed)
            for xx in range(int(x - w), int(x + w) + 1):
                m.add((xx, int(y)))
        paint(ic, m, SEAWEED if k_ % 2 == 0 else ramp('#0a140a', '#2a3a10', '#3e5216', '#566c1e', '#74902a', '#a8c050'), grad=0.5, seed=seed)
        for i, (x, y) in enumerate(pts[::6]):     # air bladders
            if i % 2 and i > 0:
                sprite(ic, int(x) - 1, int(y), ['.o.', 'oyo', '.o.'], {'o': hx('#3a3a10'), 'y': hx('#c8b040')})
    finish_item(ic, hx('#04100a'))
    drops(ic, [(10, 46), (50, 52)])


def it_scorched(ic):
    SC = ramp('#1a1208', '#8a7040', '#b0925a', '#ceb27a', '#e6d0a0', '#f8ecd0')
    m = mrect(12, 10, 52, 54)
    burn = {(x, y) for x, y in m if (x - 52) ** 2 + (y - 54) ** 2 < 230 + 60 * h(x // 2, y // 2, 330)}
    burn |= {(x, y) for x, y in m if (x - 12) ** 2 + (y - 10) ** 2 < 80 + 40 * h(x // 2, y // 2, 331)}
    paint(ic, m - burn, SC, grad=0.8, seed=13)
    for y in range(16, 46, 4):
        for x in range(16, 46):
            if (x, y) not in burn and h(x, y, 332) < 0.65:
                ic.set(x, y, hx('#3a2a1a'))
    sprite(ic, 16, 12, ['k.k.kk.kkk', 'kkk.k..k..', 'k.k.kk.k..'], {'k': hx('#2a1a0a')})   # complaint header
    # charred, glowing rim
    for x, y in m - burn:
        if any((x + dx, y + dy) in burn for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            ic.px[x, y] = GLOW_LAVA[2] if h(x, y, 333) < 0.5 else GLOW_LAVA[1]
        elif any((x + dx, y + dy) in burn for dx in (-2, 2) for dy in (-2, 2)):
            ic.px[x, y] = hx('#3a2410')
    finish_item(ic, hx('#140a04'))
    for i, (x, y) in enumerate(((50, 40), (52, 34), (49, 28), (53, 22))):  # smoke
        ic.set(x, y, hx('#8a8a90')[:3] + (180 - i * 40,))
        ic.set(x + 1, y - 1, hx('#b4b4ba')[:3] + (150 - i * 30,))


def it_bone(ic):
    shaft = mline([(16, 46), (46, 16)], 7)
    k1 = mell(8, 42, 18, 52) | mell(12, 48, 22, 58)
    k2 = mell(42, 6, 52, 16) | mell(48, 10, 58, 20)
    paint(ic, shaft | k1 | k2, BONE, grad=0.9, seed=14)
    for x, y in ((30, 30), (31, 29), (33, 28), (27, 34)):     # gnaw marks
        ic.set(x, y, hx('#6a5a3a'))
        ic.set(x + 1, y + 1, hx('#4a3e2a'))
    for x, y in ((24, 37), (25, 38), (38, 22), (39, 23)):
        ic.set(x, y, hx('#8a7a58'))
    sprite(ic, 33, 34, ['.gg.', 'g..g'], {'g': hx('#4a3e2a')})   # bite curve
    finish_item(ic, hx('#2a2014'))


def env(ic, R, flap, seal=None):
    paint(ic, mrect(8, 18, 56, 48), R, grad=0.6, seed=15)
    fl = mpoly([(8, 18), (56, 18), (32, 36)])
    paint(ic, fl, flap, grad=0.5, seed=16)
    for i in range(25):                    # flap fold lines
        ic.set(8 + i, 18 + int(i * 0.72), R[1])
        ic.set(56 - i, 18 + int(i * 0.72), R[1])
    for i in range(16):
        ic.set(8 + i, 48 - int(i * 0.6), R[2]); ic.set(56 - i, 48 - int(i * 0.6), R[2])


def it_envelope(ic):
    E = ramp('#2a2014', '#b49a6a', '#d0b888', '#e6d4aa', '#f2e6c8', '#fffaea')
    env(ic, E, ramp('#2a2014', '#a8905e', '#c4aa7c', '#dcc89e', '#ecdcbc', '#fdf4e0'))
    sprite(ic, 13, 39, ['kkk.k..kkk.k.k', 'k.k.k..k...k.k', 'kkk.k..kk..kkk'], {'k': hx('#5a4a3a')})   # "LOST" style tag lines
    sprite(ic, 40, 38, ['bbbbbbbb', 'b.r..r.b', 'bbbbbbbb'], {'b': hx('#2e4a8a'), 'r': hx('#c8283a')})
    sprite(ic, 29, 33, ['.oo.', 'oggo', 'oggo', '.oo.'], {'o': hx('#6a4a10'), 'g': hx('#e4b432')})  # coin peeking
    finish_item(ic, hx('#1e160c'))


def it_damp_parcel(ic):
    P = ramp('#1a1208', '#6a4e28', '#8a6a3a', '#a8864e', '#c4a46a', '#e0c890')
    paint(ic, mpoly([(10, 22), (32, 12), (56, 22), (56, 46), (34, 56), (10, 46)]), P, seed=17)
    top = mpoly([(10, 22), (32, 12), (56, 22), (34, 32)])
    paint(ic, top, ramp('#1a1208', '#7a5a30', '#9a7a44', '#b89658', '#d4b476', '#ecd49c'), seed=18)
    for i in range(24):                   # twine
        ic.set(20 + i, 17 + int(i * 0.42), hx('#e8dcb0'))
        ic.set(22 + i, 27 - int(i * 0.42), hx('#e8dcb0'))
    for y in range(32, 56):
        ic.set(34, y, hx('#e8dcb0'))
    for y in range(26, 50):               # dark wet band
        for x in range(10, 56):
            if ic.get(x, y)[3] and y > 40 + 3 * math.sin(x * 0.4) and h(x, y, 340) < 0.7:
                c = ic.get(x, y)
                ic.px[x, y] = (round(c[0] * 0.72), round(c[1] * 0.72), round(c[2] * 0.8), 255)
    sprite(ic, 40, 33, ['wwwwww', 'wkkkkw', 'wwwwww'], {'w': PAPER[4], 'k': hx('#5a5a6a')})
    finish_item(ic, hx('#140c04'))
    drops(ic, [(14, 53), (54, 49)])


def it_unclaimed(ic):
    paint(ic, mrect(10, 24, 54, 52), CARD, seed=19)
    paint(ic, mpoly([(8, 18), (56, 18), (56, 26), (8, 26)]), ramp('#1e1408', '#8a6838', '#ae8a4c', '#cca862', '#e4c682', '#f8e4b0'), seed=20)
    paint(ic, mrect(28, 18, 36, 52), ramp('#2a1a04', '#a07a2a', '#c49a3a', '#e0ba54', '#f0d47a', '#fff0b8'), grad=0.4, seed=21)
    # "UNCLAIMED" label + red stamp
    paint(ic, mrect(14, 32, 26, 44), PAPER, grad=0.3, seed=22)
    for y in (35, 38, 41):
        for x in range(16, 25):
            if h(x, y, 350) < 0.7:
                ic.set(x, y, hx('#4a4a5a'))
    sprite(ic, 40, 34, ['.rrrr.', 'r....r', 'r.rr.r', 'r....r', '.rrrr.'], {'r': STAMP_RED})
    sprite(ic, 44, 5, ['.ooooo.', 'oqqqqqo', 'oqwwwqo', 'oqqqwqo', 'oqqwwqo', 'oqqwqqo', 'oqqqqqo', 'oqqwqqo', 'oqqqqqo', '.ooooo.'],
           {'o': hx('#1a2a5a'), 'q': hx('#5a8cf0'), 'w': hx('#ffffff')})   # "?" tag
    for i in range(5):
        ic.set(42 - i, 14 + i, hx('#e8dcb0'))
    finish_item(ic, hx('#140c04'))


def it_bait_tin(ic):
    paint(ic, mell(10, 26, 54, 54), TIN, grad=0.8, seed=23)
    paint(ic, mell(10, 18, 54, 44), ramp('#10161a', '#4a5e68', '#6a8490', '#8eaab4', '#b8d0d8', '#eef8fa'), grad=0.6, seed=24)
    paint(ic, mell(16, 22, 48, 40), ramp('#1a1006', '#4a2c14', '#6a4020', '#8a582e', '#ac7440', '#d0985c'), grad=0.4, seed=25)
    # worms + a hook
    for k_, (cx, cy) in enumerate(((26, 30), (36, 28), (31, 34))):
        for i in range(10):
            x = cx + int(4 * math.cos(i * 0.6 + k_))
            y = cy + int(2 * math.sin(i * 0.9 + k_))
            ic.set(x, y, hx('#e07a8a') if i % 3 else hx('#b04a5a'))
    for x in range(12, 53, 4):              # rust specks
        ic.set(x, 46 + (x % 3), hx('#8a4a1a'))
    sprite(ic, 24, 44, ['bbbbbbbbbbbbbb', 'bwwwwwwwwwwwwb', 'bbbbbbbbbbbbbb'], {'b': hx('#c8283a'), 'w': hx('#f4ecd4')})
    finish_item(ic, hx('#0a1014'))


def it_luggage(ic):
    paint(ic, mrect(8, 22, 56, 54), LEATH, seed=26)
    paint(ic, mrect(24, 12, 40, 16) - mrect(27, 15, 37, 16), LEATH, grad=0.5, seed=27)   # handle
    for x in (14, 50):                      # straps
        paint(ic, mrect(x - 2, 22, x + 2, 54), ramp('#140a06', '#2a1408', '#3e1e0e', '#542a14', '#6e3a1e', '#8e5030'), grad=0.5, seed=28)
    for x0 in (8, 52):                      # brass corners
        for y0 in (22, 50):
            paint(ic, mrect(x0, y0, x0 + 4, y0 + 4), GOLD, grad=0.4, seed=29)
    paint(ic, mrect(27, 30, 37, 40), GOLD, seed=30)                                    # lock
    sprite(ic, 31, 33, ['.kk.', '.kk.', '..k.', '..k.'], {'k': hx('#2a1a04')})
    for x in range(8, 57, 2):
        ic.set(x, 26, hx('#c8a878'))          # stitching
        ic.set(x, 51, hx('#c8a878'))
    sprite(ic, 42, 40, ['.ww..', 'wwwww', 'wrrrw', 'wwwww'], {'w': PAPER[4], 'r': hx('#c8283a')})   # claim sticker
    finish_item(ic, hx('#0a0604'))


def it_hook(ic):
    pts = []
    for i in range(60):
        a = i / 59
        if a < 0.55:
            pts.append((40, 8 + a / 0.55 * 30))
        else:
            q = (a - 0.55) / 0.45 * math.pi * 1.05
            pts.append((40 - 10 * (1 - math.cos(q)), 38 + 10 * math.sin(q)))
    m = set()
    for x, y in pts:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                m.add((int(x + dx), int(y + dy)))
    paint(ic, m, GOLD, grad=0.7, seed=31)
    paint(ic, mpoly([(19, 36), (22, 30), (24, 37)]), GOLD, grad=0.4, seed=32)   # barb
    eye = mell(35, 3, 45, 13) - mell(38, 6, 42, 10)
    paint(ic, eye, GOLD, grad=0.5, seed=33)
    # four-leaf clover charm + red tag thread
    for cx, cy in ((44, 22), (48, 22), (46, 20), (46, 24)):
        paint(ic, mell(cx - 2, cy - 2, cx + 2, cy + 2), SEAWEED, grad=0.3, seed=34)
    for i in range(6):
        ic.set(42 - i, 14 + i, hx('#c8283a'))
    finish_item(ic, hx('#1a1004'))


def it_pouch(ic):
    body = mpoly([(14, 22), (50, 22), (56, 40), (50, 56), (14, 56), (8, 40)])
    paint(ic, body, VELVET, seed=35)
    paint(ic, mpoly([(16, 12), (48, 12), (52, 24), (12, 24)]), VELVET, grad=0.5, seed=36)
    for x in range(12, 53):                       # gold cord
        ic.set(x, 24 + (1 if (x // 3) % 2 else 0), GOLD[4] if x % 2 else GOLD[2])
    for i in range(10):
        ic.set(30 - i // 2, 26 + i, GOLD[3]); ic.set(34 + i // 2, 26 + i, GOLD[3])
    paint(ic, mell(26, 34, 38, 46), WAX, grad=0.5, seed=37)                       # seal
    sprite(ic, 29, 37, ['.ww..', 'w..w.', 'w..w.', '.ww..'], {'w': WAX[5]})
    sprite(ic, 12, 44, ['rrrrrrr', 'r.....r', 'rrrrrrr'], {'r': STAMP_RED})        # "DO NOT OPEN" band
    for x in range(14, 50, 3):                    # embroidered stars
        if h(x, 50, 360) < 0.5:
            ic.set(x, 50, GOLD[4])
    finish_item(ic, hx('#08040e'))


def it_director(ic):
    E = ramp('#1a1a24', '#a8a8b8', '#c8c8d6', '#e2e2ec', '#f2f2f8', '#ffffff')
    env(ic, E, ramp('#1a1a24', '#9a9aae', '#bcbccc', '#d8d8e4', '#ececf4', '#ffffff'))
    for x in range(8, 57):                        # gold border
        ic.set(x, 46, GOLD[3])
    for y in range(20, 47):
        ic.set(10, y, GOLD[3]); ic.set(54, y, GOLD[3])
    paint(ic, mell(25, 28, 39, 42), WAX, grad=0.5, seed=38)
    sprite(ic, 29, 31, ['..w..', '.www.', 'wwwww', '.w.w.', 'w...w'], {'w': WAX[5]})   # the Director's crown-star
    for i, (x, y) in enumerate(((22, 42), (24, 44), (41, 42))):
        ic.set(x, y, WAX[2])
    sprite(ic, 13, 40, ['kkkk.kkk', '........', 'kkk.kkkk'], {'k': hx('#4a4a6a')})
    finish_item(ic, hx('#141420'))
    for x, y in ((8, 10), (12, 8)):
        ic.set(x, y, hx('#e8f6ff'))              # frost (Z3+)


ITEMS = [   # (group, id, name, tier label, fx rarity, painter)
    ('Junk', 'soggy_boot', 'Soggy Boot of Unknown Owner', 'Junk', None, it_boot),
    ('Junk', 'form_27b', 'Form 27-B (illegible)', 'Junk', None, it_form),
    ('Junk', 'wet_queue_ticket', 'Wet Queue Ticket "No. 4,000,112"', 'Junk', None, it_ticket),
    ('Junk', 'waterlogged_rubber_stamp', 'Waterlogged Rubber Stamp', 'Junk', None, it_stamp),
    ('Junk', 'clump_of_seaweed', 'Clump of Seaweed', 'Junk', None, it_seaweed),
    ('Junk', 'scorched_complaint_letter', 'Scorched Complaint Letter', 'Junk', None, it_scorched),
    ('Junk', 'gnawed_bone', 'Gnawed Bone of a Previous Applicant', 'Junk', None, it_bone),
    ('Lost Property', 'lost_property_envelope', 'Lost Property Envelope', 'Good', 'Normal', it_envelope),
    ('Lost Property', 'damp_parcel', 'Damp Parcel', 'Good', 'Normal', it_damp_parcel),
    ('Lost Property', 'unclaimed_parcel', 'Unclaimed Parcel', 'Good', 'Normal', it_unclaimed),
    ('Lost Property', 'bait_tin', 'Bait Tin', 'Good', 'Normal', it_bait_tin),
    ('Lost Property', 'locked_luggage_case', 'Locked Luggage Case', 'Great', 'Rare', it_luggage),
    ('Lost Property', 'clerks_lucky_hook', "Clerk's Lucky Hook", 'Great', 'Rare', it_hook),
    ('Lost Property', 'diplomatic_pouch', 'Diplomatic Pouch (Do Not Open)', 'Outstanding', 'Legendary', it_pouch),
    ('Lost Property', 'sealed_envelope_from_the_director', 'Sealed Envelope from the Director', 'Outstanding', 'Legendary', it_director),
]


def render_item(fn, fx):
    ic = Icon()
    fn(ic)
    rarity_fx(ic, fx)
    return ic


# ---------------------------------------------------------------- quick preview (dev)
def preview(path, items, scale=4):
    n = len(items)
    cols = min(n, 6)
    rows = (n + cols - 1) // cols
    im = Image.new('RGBA', (cols * (64 * scale + 8) + 8, rows * (64 * scale + 8) + 8), hx('#2b313d'))
    for i, ic in enumerate(items):
        big = ic.im.resize((64 * scale, 64 * scale), Image.NEAREST)
        x, y = 8 + (i % cols) * (64 * scale + 8), 8 + (i // cols) * (64 * scale + 8)
        im.alpha_composite(big, (x, y))
    im.save(path)


if __name__ == '__main__' and os.environ.get('FISH_PREVIEW'):
    sel = os.environ['FISH_PREVIEW'].split(',')
    items = []
    for z, sid, name, rar, F in SPECIES:
        if sel == ['all'] or sid in sel or str(z) in sel:
            items.append(render_fish(F, rar))
    for g, iid, name, tier, fx, fn in ITEMS:
        if sel == ['all'] or iid in sel or 'items' in sel:
            items.append(render_item(fn, fx))
    preview(os.environ.get('FISH_OUT', '/tmp/prev.png'), items, int(os.environ.get('FISH_SCALE', '4')))


# ================================================================ outputs
ZONES = {1: ('Zone 1 - Emerald Wilds', 'Pond Fish', '#6a9a3a'), 2: ('Zone 2 - Howling Sands', 'Dune Fish', '#d4a24a'),
         3: ('Zone 3 - Whisperfrost', 'Frost Fish', '#8ac0e8'), 4: ('Zone 4 - Devastated Lands', 'Lava Fish', '#ff7a2a'),
         5: ('Zone 5 - Dinosaur Caves', 'Cave Fish', '#b07ae0')}
TIER_COL = {'Junk': '#9a9a9a', 'Good': '#FFFFFF', 'Great': '#FF55FF', 'Outstanding': '#55FFFF'}


def font(sz, bold=False):
    for f in (('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),):
        if os.path.exists(f):
            return ImageFont.truetype(f, sz)
    return ImageFont.load_default()


def wrap(d, text, f, wmax):
    words, lines, cur = text.split(), [], ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if d.textlength(t, font=f) <= wmax:
            cur = t
        else:
            lines.append(cur); cur = w_
    lines.append(cur)
    return lines


def build():
    os.makedirs(os.path.join(OUT, 'icons'), exist_ok=True)
    rows = []          # (header, colour, [(img, name, label, labelcol)])
    for z in range(1, 6):
        cells = []
        for zz, sid, name, rar, F in SPECIES:
            if zz == z:
                ic = render_fish(F, rar)
                ic.im.save(os.path.join(OUT, 'icons', sid + '.png'), optimize=True)
                cells.append((ic.im, name, rar, '#%02X%02X%02X' % RAR[rar][:3]))
        zn, coll, zc = ZONES[z]
        rows.append(('%s  (collection: %s)' % (zn, coll), zc, cells))
    for grp, head in (('Junk', 'Junk (any zone unless noted; flavour, pennies)'), ('Lost Property', 'Lost Property (treasure wrappers; open on use)')):
        cells = []
        for g, iid, name, tier, fx, fn in ITEMS:
            if g == grp:
                ic = render_item(fn, fx)
                ic.im.save(os.path.join(OUT, 'icons', iid + '.png'), optimize=True)
                cells.append((ic.im, name, tier, TIER_COL[tier]))
        rows.append((head, '#c8c4b4', cells))
    # ---- sheet
    S, CW, CH, PAD = 3, 276, 300, 14
    ncol = 10
    fT, fH, fN, fL, fS = font(30, True), font(22, True), font(15, True), font(14, True), font(13)
    tmp = ImageDraw.Draw(Image.new('RGB', (10, 10)))
    heights = []
    for head, zc, cells in rows:
        nr = (len(cells) + ncol - 1) // ncol
        heights.append(44 + nr * CH)
    Wd = PAD * 2 + ncol * CW
    Ht = 150 + sum(heights) + PAD
    im = Image.new('RGBA', (Wd, Ht), hx('#161a22'))
    d = ImageDraw.Draw(im)
    d.text((PAD + 4, 14), 'SkyWynn fishing - species, junk and Lost Property icons (concept v1)', font=fT, fill=hx('#f0ece0'))
    d.text((PAD + 4, 56), 'Cloud draft 2026-10-06, original pixel art made by make_fish.py (no game art). Each icon is 64 x 64; shown 3x on a dark slot, '
           'with the real 1x size in the small slot on the right.', font=fS, fill=hx('#b8b4a8'))
    # legend
    x = PAD + 4
    d.text((x, 84), 'Rarity shown on the icon:', font=fL, fill=hx('#d8d4c8'))
    x += 215
    for r, txt in (('Normal', 'none'), ('Unique', '1 small glint'), ('Rare', 'faint rim + star'), ('Legendary', 'halo + 3 sparkles'),
                   ('Fabled', 'red halo + 4 sparkles + embers'), ('Mythic', 'double halo + 5 sparkles + motes')):
        c = RAR[r]
        d.rectangle((x, 86, x + 12, 98), fill=c, outline=hx('#000000'))
        d.text((x + 18, 84), '%s: %s' % (r, txt), font=fS, fill=c)
        x += 30 + d.textlength('%s: %s' % (r, txt), font=fS)
    d.text((PAD + 4, 110), 'Lost Property tiers reuse the same marks: Good = none, Great = Rare mark, Outstanding = Legendary mark. Junk has none. '
           'Lore touches: ticket, paperclip, ink stamp, ID badge, luggage tag, customs check, scorch stamp, Final Notice seal.',
           font=fS, fill=hx('#b8b4a8'))
    y = 150
    for (head, zc, cells), hh in zip(rows, heights):
        d.rectangle((PAD, y, Wd - PAD, y + 32), fill=hx('#232936'))
        d.rectangle((PAD, y, PAD + 6, y + 32), fill=hx(zc))
        d.text((PAD + 16, y + 4), head, font=fH, fill=hx(zc))
        yy = y + 44
        for i, (img, name, lab, lc) in enumerate(cells):
            cx = PAD + (i % ncol) * CW + 8
            cy = yy + (i // ncol) * CH
            d.rectangle((cx - 2, cy - 2, cx + 64 * S + 1, cy + 64 * S + 1), fill=hx('#454d5c'))
            d.rectangle((cx, cy, cx + 64 * S - 1, cy + 64 * S - 1), fill=hx('#2b313d'))
            im.alpha_composite(img.resize((64 * S, 64 * S), Image.NEAREST), (cx, cy))
            d.rectangle((cx + 64 * S + 6, cy + 64 * S - 66, cx + 64 * S + 71, cy + 64 * S - 1), fill=hx('#2b313d'), outline=hx('#454d5c'))
            im.alpha_composite(img, (cx + 64 * S + 7, cy + 64 * S - 65))
            d.text((cx + 64 * S + 30, cy + 64 * S - 82), '1x', font=fS, fill=hx('#8a8a8a'))
            ty = cy + 64 * S + 6
            for ln in wrap(d, name, fN, CW - 16)[:2]:
                d.text((cx + 134 - d.textlength(ln, font=fN) / 2, ty), ln, font=fN, fill=hx('#f0ece0'))
                ty += 18
            d.text((cx + 134 - d.textlength(lab, font=fL) / 2, ty + 1), lab, font=fL, fill=hx(lc))
        y += hh
    im.convert('RGB').save(os.path.join(OUT, 'fish-sheet.png'), optimize=True)
    return len(SPECIES), len(ITEMS)


if __name__ == '__main__' and not os.environ.get('FISH_PREVIEW'):
    n, m = build()
    print('species', n, 'items', m)
