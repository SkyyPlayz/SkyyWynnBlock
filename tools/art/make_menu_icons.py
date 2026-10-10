#!/usr/bin/env python3
"""SkyWynn Menu - one 64 x 64 item icon per menu tile (DRAFT v1, ART-RESUME: "lets make an Icon for everything in this menu").

Writes (all ORIGINAL pixels, no vanilla file is read or copied; the Accessory Bag icon is a byte copy of OUR approved
art/accessory-bag-icon/ icon):
  art/menu-icons/Common/Icons/ItemsGenerated/Skyy_Menu_Icon_<Name>.png   64 x 64 RGBA, hard alpha, 1 px dark outline
  art/menu-icons/sheet.png                                               review sheet (1x + 2x labelled, 32 px, on light, 9x6 menu mock)
  art/menu-icons/manifest.json                                           file list (bytes, sha256), tiles, categories, palettes

Run:  python tools/art/make_menu_icons.py          (deterministic: two runs = same bytes)
Check: python tools/art/validate_menu_icons.py
Pure Python 3 (no Pillow / numpy). PNG helpers + the 5x7 label font come from tools/art/emblem_png.py (the menu emblem's helpers).

How an icon is drawn (same family look as the approved menu emblem):
  1. each icon is a stack of LAYERS (a shape + a 6-7 step colour ramp + a shading mode), painted at 4x supersampling;
  2. light comes from the top left for every icon: a soft gradient across each part, a lit bevel on edges facing the light and a
     dark bevel on edges facing away; 'sphere' / 'cyl' / 'torus' modes shade round parts;
  3. box-filtered to 64 px, then every pixel is snapped to its layer's ramp (crisp pixel-art bands), alpha hard (0 or 255);
  4. 64 px hand rules in code: a contact shadow under parts that sit in front of others, optional 1 px inner line round front
     parts, a light rim on top / left outer edges and a dark rim on bottom / right outer edges, then the 1 px violet-black outline
     (#120e1c, tinted a little toward the part it touches - brown-black next to gold, like the bag and the emblem);
  5. no #000000 / #ffffff anywhere (the lightest steps stop at ~#fff4cf, the darkest at the outline).
"""
import hashlib, json, math, os, struct, sys, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import emblem_png as P

ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "art", "menu-icons")
ICON_DIR_REL = "Common/Icons/ItemsGenerated"
BAG_SRC_REL = "art/accessory-bag-icon/Common/Icons/ItemsGenerated/SkyyAccessories_Bag_Menu.png"
SS = 4                     # supersampling
N = 64                     # icon size (= vanilla item icon size)


def hx(s):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def hexs(c):
    return "#%02x%02x%02x" % tuple(int(round(v)) for v in c[:3])


def mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


OUTLINE = hx("#120e1c")
LIGHT = (-0.53, -0.85)                       # 2D direction TO the light (top left, mostly top)
L3 = (-0.42, -0.62, 0.66)                    # 3D light for round parts
_l = math.sqrt(sum(v * v for v in L3)); L3 = tuple(v / _l for v in L3)

# ====================================================================== palettes (dark -> light; shadows lean violet / blue, lights warm)
PAL = {
    "gold":   ["#3e1f08", "#6e3f0c", "#a2650f", "#d39a22", "#f0c548", "#ffe58a", "#fff4cf"],
    "amber":  ["#3a1606", "#6a2c0a", "#a24a10", "#d8761c", "#f5a332", "#ffcf6a", "#fff0bf"],
    "teal":   ["#0b2227", "#113c3d", "#175d58", "#1e8577", "#2fae97", "#66d4b9", "#bff2e1"],
    "green":  ["#0c2213", "#143d21", "#1d5e30", "#2a853f", "#43aa50", "#80d06c", "#cdf0ad"],
    "violet": ["#1a0f2e", "#2c1a4b", "#45296c", "#623b92", "#8355b5", "#aa80d4", "#dbc3ef"],
    "steel":  ["#14161e", "#242833", "#373d4b", "#525a6b", "#768092", "#a1aaba", "#d0d6e0"],
    "wood":   ["#28130a", "#43220f", "#633617", "#874f24", "#aa6c35", "#c98d4f", "#e3b47a"],
    "mahog":  ["#2a0f0c", "#481a14", "#6a2a1c", "#8c3e26", "#ad5734", "#cc7a4a", "#e6a372"],
    "stone":  ["#25232e", "#3a3744", "#54505e", "#716c7a", "#918b97", "#b4aeb6", "#d6d1d4"],
    "grass":  ["#173a17", "#21541f", "#2f7428", "#43952f", "#62b53a", "#90d257", "#c4ec8c"],
    "soil":   ["#2a160e", "#43251a", "#5f3824", "#7d4f30", "#9a6a42"],
    "cloud":  ["#5f6d96", "#8a9cc8", "#a8b8de", "#c6d4ee", "#e2ecf8"],
    "red":    ["#3a0b12", "#661620", "#982430", "#c93a3c", "#e86a5c", "#f7a493"],
    "blue":   ["#0b1838", "#132c66", "#1f4a9c", "#3170cc", "#58a0ea", "#9ccbf7"],
    "cream":  ["#4a3a2c", "#6e5a44", "#957d5e", "#b9a17c", "#d8c49c", "#efe2c0", "#faf3dd"],
    "navy":   ["#0a1220", "#101c32", "#16284a", "#1f3a66", "#2c5088"],
    "glass":  ["#1d3a48", "#2f5d6e", "#4a8a98", "#77b7c0", "#a9dde0", "#d8f4f2"],
    "void":   ["#0e0820", "#1c1040", "#2e1a66", "#47288f", "#6a3fb8", "#9a6ee0", "#cfb2f6"],
    "magic":  ["#1b1040", "#2e2370", "#3a4596", "#3f72b4", "#3fa8c2", "#7fdcd8", "#cdf8f0"],
    "emerald": ["#06281a", "#0c4a2c", "#137040", "#1f9a55", "#3cc472", "#88eaa6", "#d2fbe0"],
    "vault":  ["#0f1a17", "#1b2b26", "#2a4038", "#3c5a4e", "#557a6a", "#7ea08f", "#b8d0c2"],
    "leather": ["#24110c", "#3b1d12", "#58301b", "#784626", "#975e34", "#b77d4c"],
}
PALC = {k: [hx(c) for c in v] for k, v in PAL.items()}

# ====================================================================== shapes (icon units, 0..64, y down)
class Shape:
    def __init__(self, f, bb):
        self.f, self.bb = f, bb

    def __call__(self, x, y):
        x0, y0, x1, y1 = self.bb
        return x0 <= x <= x1 and y0 <= y <= y1 and self.f(x, y)


def circle(cx, cy, r):
    return Shape(lambda x, y: (x - cx) ** 2 + (y - cy) ** 2 <= r * r, (cx - r, cy - r, cx + r, cy + r))


def ellipse(cx, cy, rx, ry):
    return Shape(lambda x, y: ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0, (cx - rx, cy - ry, cx + rx, cy + ry))


def rot_ellipse(cx, cy, ra, rb, ang):
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang)); m = max(ra, rb)
    def f(x, y):
        dx, dy = x - cx, y - cy
        u, v = dx * c + dy * s, -dx * s + dy * c
        return (u / ra) ** 2 + (v / rb) ** 2 <= 1.0
    return Shape(f, (cx - m, cy - m, cx + m, cy + m))


def rect(x0, y0, x1, y1):
    return Shape(lambda x, y: True, (x0, y0, x1, y1))


def rrect(x0, y0, x1, y1, r):
    def f(x, y):
        cx = min(max(x, x0 + r), x1 - r); cy = min(max(y, y0 + r), y1 - r)
        return (x - cx) ** 2 + (y - cy) ** 2 <= r * r
    return Shape(f, (x0, y0, x1, y1))


def poly(pts):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; n = len(pts)
    def f(x, y):
        ins = False; j = n - 1
        for i in range(n):
            xi, yi = pts[i]; xj, yj = pts[j]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
                ins = not ins
            j = i
        return ins
    return Shape(f, (min(xs), min(ys), max(xs), max(ys)))


def capsule(x0, y0, x1, y1, r):
    dx, dy = x1 - x0, y1 - y0; L2 = dx * dx + dy * dy or 1e-9
    def f(x, y):
        t = max(0.0, min(1.0, ((x - x0) * dx + (y - y0) * dy) / L2))
        return (x - x0 - t * dx) ** 2 + (y - y0 - t * dy) ** 2 <= r * r
    return Shape(f, (min(x0, x1) - r, min(y0, y1) - r, max(x0, x1) + r, max(y0, y1) + r))


def union(*ss):
    bb = (min(s.bb[0] for s in ss), min(s.bb[1] for s in ss), max(s.bb[2] for s in ss), max(s.bb[3] for s in ss))
    return Shape(lambda x, y: any(s(x, y) for s in ss), bb)


def diff(a, *bs):
    return Shape(lambda x, y: a(x, y) and not any(b(x, y) for b in bs), a.bb)


def inter(a, b):
    bb = (max(a.bb[0], b.bb[0]), max(a.bb[1], b.bb[1]), min(a.bb[2], b.bb[2]), min(a.bb[3], b.bb[3]))
    return Shape(lambda x, y: a(x, y) and b(x, y), bb)


def ering(cx, cy, rxo, ryo, rxi, ryi):
    return diff(ellipse(cx, cy, rxo, ryo), ellipse(cx, cy, rxi, ryi))


def star_pts(cx, cy, R, r, n, rot=-90.0):
    pts = []
    for i in range(2 * n):
        a = math.radians(rot + i * 180.0 / n); rr = R if i % 2 == 0 else r
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def gear(cx, cy, R, rb, n, hole=0.0, tooth=0.5, rot=0.0):
    """cog: body radius rb, tooth tips at R (trapezoid-ish teeth: wider at the root), optional hole"""
    def f(x, y):
        dx, dy = x - cx, y - cy; d = math.hypot(dx, dy)
        if d < hole or d > R: return False
        if d <= rb: return True
        a = (math.degrees(math.atan2(dy, dx)) - rot) % (360.0 / n) / (360.0 / n)    # 0..1 inside one tooth period
        k = (d - rb) / (R - rb)                                                   # 0 at the root, 1 at the tip
        half = tooth * (1.0 - 0.35 * k) / 2
        return abs(a - 0.5) <= half
    return Shape(f, (cx - R, cy - R, cx + R, cy + R))


def xform(pts, cx, cy, s, dx=0.0, dy=0.0):
    return [(cx + (x - cx) * s + dx, cy + (y - cy) * s + dy) for x, y in pts]


# ====================================================================== icon painter
class Layer:
    def __init__(self, shape, pal, mode="flat", base=0.55, grad=0.35, bevel=1.1, bev=0.18, pattern=None, cast=True,
                 line=False, rim=True, center=None, tfunc=None, axis=None, torus=None, sphere=None):
        self.shape, self.pal, self.mode = shape, pal, mode
        self.base, self.grad, self.bevel, self.bev = base, grad, bevel, bev
        self.pattern, self.cast, self.line, self.rim = pattern, cast, line, rim
        self.tfunc, self.axis, self.torus = tfunc, axis, torus
        x0, y0, x1, y1 = shape.bb
        self.c = center or ((x0 + x1) / 2, (y0 + y1) / 2)
        self.R = max(x1 - x0, y1 - y0) / 2 or 1.0
        self.sph = sphere or (self.c[0], self.c[1], (x1 - x0) / 2 or 1, (y1 - y0) / 2 or 1)
        self.half = None
        if axis is not None:                      # cylinder: (ax, ay) axis direction, half width across it
            ax, ay = axis; l = math.hypot(ax, ay); self.axis = (ax / l, ay / l)
            px, py = -self.axis[1], self.axis[0]
            corners = [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]
            self.half = max(abs((cx - self.c[0]) * px + (cy - self.c[1]) * py) for cx, cy in corners) * 0.72

    def t(self, x, y):
        if self.tfunc:
            t = self.tfunc(x, y)
        elif self.mode == "sphere":
            cx, cy, rx, ry = self.sph
            nx, ny = (x - cx) / rx, (y - cy) / ry; q = nx * nx + ny * ny
            nz = math.sqrt(max(0.0, 1.0 - q)) if q < 1 else 0.0
            d = max(0.0, nx * L3[0] + ny * L3[1] + nz * L3[2])
            t = 0.12 + 0.88 * d + (self.base - 0.55)
        elif self.mode == "cyl":
            px, py = -self.axis[1], self.axis[0]
            u = ((x - self.c[0]) * px + (y - self.c[1]) * py) / self.half
            u = max(-1.0, min(1.0, u)); nz = math.sqrt(max(0.0, 1 - u * u))
            d = max(0.0, u * px * L3[0] + u * py * L3[1] + nz * L3[2])
            t = 0.1 + 0.9 * d + (self.base - 0.55)
        elif self.mode == "torus":
            cx, cy, rxo, ryo, rxi, ryi = self.torus
            dx, dy = x - cx, y - cy
            a = math.atan2(dy / ((ryo + ryi) / 2), dx / ((rxo + rxi) / 2))
            ex, ey = math.cos(a), math.sin(a)
            ro = math.hypot(rxo * ex, ryo * ey); ri = math.hypot(rxi * ex, ryi * ey); d = math.hypot(dx, dy)
            p = max(-1.0, min(1.0, (d - (ro + ri) / 2) / ((ro - ri) / 2)))
            nz = math.sqrt(max(0.0, 1 - p * p))
            dd = max(0.0, p * ex * L3[0] + p * ey * L3[1] + nz * L3[2])
            t = 0.1 + 0.9 * dd + (self.base - 0.55)
        else:
            d = ((x - self.c[0]) * LIGHT[0] + (y - self.c[1]) * LIGHT[1]) / self.R
            t = self.base + self.grad * 0.5 * d
        if self.bevel:
            b = self.bevel
            if not self.shape(x - LIGHT[0] * b, y - LIGHT[1] * b):
                t -= self.bev * 1.2
            elif not self.shape(x + LIGHT[0] * b, y + LIGHT[1] * b):
                t += self.bev
        if self.pattern:
            t += self.pattern(x, y)
        return t


class Icon:
    def __init__(self, name):
        self.name = name; self.layers = []; self.pix = []

    def add(self, shape, pal, **kw):
        self.layers.append(Layer(shape, PALC[pal] if isinstance(pal, str) else pal, **kw))
        return self.layers[-1]

    def px(self, x, y, c):
        """a hand-placed pixel (sparkles, glints) - drawn after the layers, before the outline"""
        self.pix.append((x, y, hx(c) if isinstance(c, str) else c))

    def sparkle(self, x, y, size=2, core="#fff4cf", arm="#ffe58a"):
        for k in range(1, size + 1):
            col = arm if k < size else mix(hx(arm), hx("#d39a22"), 0.35)
            for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)):
                self.px(x + dx, y + dy, col)
        self.px(x, y, core)

    def render(self):
        n = N * SS; inv = 1.0 / SS
        # per final pixel: per layer -> [count, tsum]
        acc = [[None] * N for _ in range(N)]
        L = self.layers
        bbs = []
        for ly in L:
            x0, y0, x1, y1 = ly.shape.bb
            bbs.append((x0, y0, x1, y1))
        for sy in range(n):
            y = (sy + 0.5) * inv
            cand = [i for i in range(len(L)) if bbs[i][1] <= y <= bbs[i][3]]
            if not cand: continue
            cand.reverse()
            row = acc[sy // SS]
            for sx in range(n):
                x = (sx + 0.5) * inv
                for i in cand:
                    b = bbs[i]
                    if b[0] <= x <= b[2] and L[i].shape(x, y):
                        cell = row[sx // SS]
                        if cell is None:
                            cell = row[sx // SS] = {}
                        e = cell.get(i)
                        if e is None: cell[i] = [1, L[i].t(x, y)]
                        else: e[0] += 1; e[1] += L[i].t(x, y)
                        break
        # snap to ramps (hard alpha: solid when >= half the sub-pixels are covered)
        grid = [[None] * N for _ in range(N)]
        half = SS * SS / 2
        for y in range(N):
            for x in range(N):
                cell = acc[y][x]
                if not cell: continue
                if sum(v[0] for v in cell.values()) < half: continue
                i = max(cell, key=lambda k: (cell[k][0], k))
                t = cell[i][1] / cell[i][0]
                pal = L[i].pal
                idx = int(max(0.0, min(1.0, t)) * (len(pal) - 1) + 0.5)
                grid[y][x] = [i, idx]
        def at(x, y):
            return grid[y][x] if 0 <= x < N and 0 <= y < N else None
        new = [[None if c is None else list(c) for c in row] for row in grid]
        for y in range(N):
            for x in range(N):
                c = grid[y][x]
                if c is None: continue
                i, idx = c; ly = L[i]
                # contact shadow: a part in front (higher layer) just above / left of this pixel
                for nb in (at(x, y - 1), at(x - 1, y)):
                    if nb and nb[0] > i and L[nb[0]].cast:
                        idx -= 1; break
                # outer rim: lit on top / left edges, shaded on bottom / right edges
                if ly.rim:
                    if at(x, y - 1) is None or at(x - 1, y) is None:
                        idx += 1
                    elif at(x, y + 1) is None or at(x + 1, y) is None:
                        idx -= 1
                idx = max(0, min(len(ly.pal) - 1, idx))
                if ly.line:
                    for nb in (at(x, y - 1), at(x - 1, y), at(x + 1, y), at(x, y + 1)):
                        if nb and nb[0] < i:
                            idx = -1; break
                new[y][x] = [i, idx]
        img = P.new(N, N)
        owner = [[None] * N for _ in range(N)]
        for y in range(N):
            for x in range(N):
                c = new[y][x]
                if c is None: continue
                i, idx = c; pal = L[i].pal
                col = mix(OUTLINE, pal[0], 0.55) if idx < 0 else pal[idx]
                img[y][x] = [col[0], col[1], col[2], 255]; owner[y][x] = pal
        for x, y, col in self.pix:
            if 0 <= x < N and 0 <= y < N:
                img[y][x] = [col[0], col[1], col[2], 255]
                if owner[y][x] is None: owner[y][x] = [mix(col, OUTLINE, 0.6)] * 2
        # 1 px outline round the silhouette, tinted toward the part it touches
        out = [[list(p) for p in row] for row in img]
        for y in range(N):
            for x in range(N):
                if img[y][x][3]: continue
                for nx, ny in ((x, y - 1), (x - 1, y), (x + 1, y), (x, y + 1)):
                    if 0 <= nx < N and 0 <= ny < N and img[ny][nx][3]:
                        pal = owner[ny][nx]
                        col = mix(OUTLINE, pal[1], 0.28)
                        if 0.299 * col[0] + 0.587 * col[1] + 0.114 * col[2] > 34:      # pale parts (clouds): keep it dark
                            col = mix(OUTLINE, pal[1], 0.1)
                        out[y][x] = [col[0], col[1], col[2], 255]; break
        # no pure black / white
        for row in out:
            for p in row:
                if p[3]:
                    p[0], p[1], p[2] = [int(round(v)) for v in p[:3]]
                    if p[0] >= 250 and p[1] >= 250 and p[2] >= 250: p[0], p[1], p[2] = 250, 246, 236
                    if p[0] <= 6 and p[1] <= 6 and p[2] <= 6: p[0], p[1], p[2] = OUTLINE
        return out


# ====================================================================== helpers for common parts
def obox(ic, x0, y0, x1, y1, d, pal, base=0.55, kx=0.55, ky=0.6, top=None, front=None, right=None, **kw):
    """3/4 box: front face rect + top face + right face (light from top left: top brightest, right side darkest)"""
    ox, oy = d * kx, d * ky
    f = ic.add(rect(x0, y0, x1, y1), pal, base=base + (front or 0.0), **kw)
    t = ic.add(poly([(x0, y0), (x1, y0), (x1 + ox, y0 - oy), (x0 + ox, y0 - oy)]), pal, base=base + 0.25 + (top or 0.0), **kw)
    r = ic.add(poly([(x1, y0), (x1 + ox, y0 - oy), (x1 + ox, y1 - oy), (x1, y1)]), pal, base=base - 0.22 + (right or 0.0), **kw)
    return f, t, r


def bust(ic, cx, top, s, pal, base=0.6, line=False):
    """a blocky Hytale-style head + shoulders; s = scale (1 = head 18 px wide)"""
    hw = 9 * s
    ic.add(rrect(cx - 15 * s, top + 23 * s, cx + 15 * s, top + 23 * s + 26 * s, 8 * s), pal, base=base - 0.08, grad=0.45, line=line)
    ic.add(rect(cx - 4 * s, top + 17 * s, cx + 4 * s, top + 24 * s), pal, base=base - 0.25, bevel=0, line=False)
    ic.add(rrect(cx - hw, top, cx + hw, top + 19 * s, 3.5 * s), pal, base=base + 0.05, grad=0.5, line=line)


def hstripes(period, amp, phase=0.0):
    return lambda x, y: -amp if int((y + phase) // period) % 2 else 0.0


def folds(freq, amp, x0=0.0):
    return lambda x, y: amp * math.sin((x - x0) * freq)


# ====================================================================== the icons
def icon_teleport():
    ic = Icon("Teleport")
    ic.add(rrect(15, 50, 49, 58, 1.5), "stone", base=0.42, grad=0.5)                       # plinth
    ic.add(rect(12, 47, 52, 51.5), "stone", base=0.68, grad=0.5)                           # plinth top slab
    cx, cy = 32.0, 27.0
    def swirl(x, y):
        dx, dy = (x - cx) / 13.0, (y - cy) / 18.0; r = math.hypot(dx, dy); a = math.atan2(dy, dx)
        return 0.32 + 0.6 * (1 - r) + 0.18 * math.sin(3 * a + r * 9.0)
    ic.add(ellipse(cx, cy, 13.5, 18.5), "amber", tfunc=swirl, bevel=0, rim=False)          # portal energy
    ic.add(ering(cx, cy, 19.5, 24.5, 13, 18), "gold", mode="torus", torus=(cx, cy, 19.5, 24.5, 13, 18), bevel=0, line=True)
    for (sx, sy) in ((cx, cy - 21.3), (cx - 16.3, cy), (cx + 16.3, cy)):                   # amber gem studs
        ic.add(circle(sx, sy, 2.7), "amber", mode="sphere", base=0.75, bevel=0, line=True)
    ic.sparkle(32, 22, 2, "#fff4cf", "#ffcf6a")
    ic.sparkle(54, 10, 2); ic.sparkle(9, 15, 1); ic.sparkle(55, 41, 1)
    return ic


def icon_island():
    ic = Icon("IslandMenu")
    rock = poly([(10, 37), (54, 37), (50, 44), (44, 47), (40, 54), (34, 61), (29, 56), (24, 48), (16, 44)])
    ic.add(ellipse(52, 50, 5, 2.2), "cloud", base=0.7, grad=0.6, bevel=0.8)               # cloud wisp behind (right)
    ic.add(rock, "stone", base=0.42, grad=0.6, pattern=hstripes(4, 0.1, 1))
    ic.add(inter(rock, rect(0, 36, 64, 41)), "soil", base=0.5, grad=0.4, bevel=0, pattern=lambda x, y: -0.12 if (int(x) * 7 + int(y) * 3) % 11 == 0 else 0)
    ic.add(union(ellipse(32, 35, 23, 6.5), *[circle(13 + 6.2 * k, 40.6, 1.6) for k in range(7) if k % 2 == 0]), "grass", base=0.6, grad=0.6)
    ic.add(circle(14, 31, 4.3), "grass", mode="sphere", base=0.5)                          # bush
    ic.add(circle(17.5, 33, 3.2), "grass", mode="sphere", base=0.45)
    # cottage: front gable wall + side wall + roof
    ic.add(rect(20, 23, 34, 35), "cream", base=0.62, grad=0.4)
    ic.add(poly([(34, 23), (40, 19), (40, 31), (34, 35)]), "cream", base=0.32, grad=0.3)
    ic.add(poly([(19, 24), (35, 24), (27, 14)]), "cream", base=0.7, grad=0.3)
    ic.add(poly([(27, 14), (33, 9.5), (42, 19.8), (35.5, 24.6)]), "amber", base=0.5, grad=0.5, pattern=hstripes(2.5, 0.1), line=True)
    ic.add(capsule(18.5, 24.5, 27, 13.6, 1.3), "amber", base=0.55, bevel=0, line=True)
    ic.add(rect(25, 28, 29.5, 35), "wood", base=0.35, grad=0.3)                            # door
    ic.add(poly([(36, 26), (38.5, 24.5), (38.5, 28.5), (36, 30)]), "amber", base=0.95, bevel=0)  # lit window
    ic.add(capsule(48, 13, 48, 34, 0.9), "wood", base=0.55, bevel=0)                        # little flag
    ic.add(poly([(48.5, 12.5), (56, 15.5), (48.5, 19)]), "amber", base=0.62, grad=0.6, line=True)
    ic.add(union(ellipse(11, 52, 6, 2.4), ellipse(15, 50.5, 3.6, 2.2)), "cloud", base=0.72, grad=0.6, bevel=0.8)
    ic.sparkle(9, 9, 1)
    return ic


def icon_pocket():
    ic = Icon("PocketDimension")
    ic.add(union(ellipse(32, 45, 19, 15), poly([(23, 28), (41, 28), (47, 37), (17, 37)])), "teal", mode="sphere",
           sphere=(30, 40, 22, 22), base=0.6, pattern=folds(0.75, 0.06))
    ic.add(ellipse(32, 26.5, 13, 5), "teal", base=0.78, grad=0.5)                           # ruffled opening rim
    ic.add(ellipse(32, 26.2, 10, 3.2), "void", base=0.3, grad=-0.4, bevel=0, rim=False)    # the void inside
    ic.add(poly([(19.5, 31), (44.5, 31), (45, 34), (19, 34)]), "gold", base=0.6, grad=0.6, bevel=0.8)   # drawstring
    ic.add(capsule(37, 34, 35.5, 41, 1.0), "gold", base=0.55, bevel=0)
    ic.add(capsule(38, 34, 41.5, 40, 1.0), "gold", base=0.5, bevel=0)
    ic.add(circle(37.5, 33, 2.3), "gold", mode="sphere", base=0.7, line=True)
    # the swirl rising out of the pouch (flattened spiral)
    caps = []
    pts = []
    th = 0.4
    while th < 4.4 * math.pi:
        r = 1.0 + 1.05 * th
        pts.append((32 + r * math.cos(th), 13 + 0.62 * r * math.sin(th))); th += 0.18
    for (a, b) in zip(pts, pts[1:]):
        caps.append(capsule(a[0], a[1], b[0], b[1], 1.5))
    caps.append(capsule(pts[-1][0], pts[-1][1], 34, 25, 1.7))
    def sw(x, y):
        r = math.hypot(x - 32, (y - 13) / 0.62)
        return 1.05 - r / 24.0
    ic.add(union(*caps), "magic", tfunc=sw, bevel=0.7, line=False)
    ic.sparkle(51, 8, 1, "#cdf8f0", "#7fdcd8"); ic.sparkle(11, 14, 2, "#cdf8f0", "#7fdcd8"); ic.sparkle(53, 24, 1, "#cdf8f0", "#7fdcd8")
    return ic


def icon_hud():
    ic = Icon("HudEditor")
    ic.add(poly([(27, 50), (37, 50), (40, 56), (24, 56)]), "teal", base=0.35)               # stand
    ic.add(rrect(17, 54, 47, 59, 1.5), "teal", base=0.45)
    ic.add(diff(rrect(5, 9, 59, 51, 3.5), rect(9.5, 13.5, 54.5, 46.5)), "teal", base=0.62, grad=0.5)
    ic.add(rect(9.5, 13.5, 54.5, 46.5), "navy", base=0.45, grad=0.5, bevel=0, rim=False,
           pattern=lambda x, y: 0.12 if (x + y) % 16 < 1.2 else 0.0)
    ic.add(rect(13, 18, 34, 23), "navy", base=0.05, bevel=0)                                # health bar slot
    ic.add(rect(14, 19, 30, 22), "red", base=0.62, grad=0.6, bevel=0.7)
    ic.add(rect(13, 25, 30, 30), "navy", base=0.05, bevel=0)                                # mana bar slot
    ic.add(rect(14, 26, 25, 29), "blue", base=0.62, grad=0.6, bevel=0.7)
    ic.add(circle(46, 23.5, 5.6), "gold", base=0.6, mode="sphere")                          # minimap
    ic.add(circle(46, 23.5, 4.2), "grass", base=0.5, grad=0.5, bevel=0,
           pattern=lambda x, y: -0.25 if abs((x - 46) - (y - 23.5) * 0.4) < 0.9 else 0.0)
    for k in range(5):                                                                     # hotbar widget
        ic.add(rect(16.5 + 6.5 * k, 38, 22 + 6.5 * k, 43.5), "steel", base=0.5 if k != 2 else 0.85, grad=0.4, bevel=0.6)
    # dashed gold edit box round the health bar
    for x in range(12, 36):
        if x % 2 == 0: ic.px(x, 16, "#f0c548"); ic.px(x, 24, "#d39a22")
    for y in range(16, 25):
        if y % 2 == 0: ic.px(12, y, "#f0c548"); ic.px(35, y, "#d39a22")
    # pointer arrow
    ic.add(poly([(33, 27), (33, 41), (36.3, 37.8), (38.8, 43.5), (41.2, 42.4), (38.8, 36.8), (43.2, 36.8)]), "cream",
           base=0.9, grad=0.3, bevel=0.7, line=True)
    return ic


def icon_crafting():
    ic = Icon("Crafting")
    y0 = 31.0
    ic.add(rect(49, y0 - 3, 53.5, 51), "wood", base=0.28, grad=0.3)                         # back right leg
    ic.add(rect(13, 47, 41, 50.5), "wood", base=0.35)                                       # stretcher
    ic.add(rect(8, y0 + 7, 13.5, 58), "wood", base=0.5, grad=0.4, pattern=folds(2.2, 0.05))  # front legs
    ic.add(rect(38.5, y0 + 7, 44, 58), "wood", base=0.42, grad=0.4, pattern=folds(2.2, 0.05))
    d = 17.0; kx, ky = 0.55, 0.6; ox, oy = d * kx, d * ky
    x0, x1 = 6.0, 46.0
    ic.add(rect(x0, y0, x1, y0 + 7), "wood", base=0.45, grad=0.4, pattern=lambda x, y: -0.12 if int(x) % 8 == 0 else 0)
    ic.add(poly([(x1, y0), (x1 + ox, y0 - oy), (x1 + ox, y0 + 7 - oy), (x1, y0 + 7)]), "wood", base=0.25)
    top = poly([(x0, y0), (x1, y0), (x1 + ox, y0 - oy), (x0 + ox, y0 - oy)])
    ic.add(top, "wood", base=0.72, grad=0.5, pattern=lambda x, y: -0.13 if int((y - y0 + oy) * 10) % 34 < 4 else 0)
    # teal crafting mat with a 3 x 3 grid on the top face (parallelogram coords)
    ex, ey = (x1 - x0), 0.0; fx, fy = ox, -oy
    det = ex * fy - ey * fx
    def uv(x, y):
        dx, dy = x - x0, y - y0
        return (dx * fy - dy * fx) / det, (ex * dy - ey * dx) / det
    def mat_in(x, y):
        u, v = uv(x, y); return 0.2 <= u <= 0.74 and 0.12 <= v <= 0.9
    def mat_pat(x, y):
        u, v = uv(x, y); uu = (u - 0.2) / 0.54 * 3; vv = (v - 0.12) / 0.78 * 3
        on = min(abs(uu - round(uu)), abs(vv - round(vv)) * 0.6)
        return -0.32 if on < 0.09 else 0.0
    ic.add(Shape(mat_in, top.bb), "teal", base=0.62, grad=0.4, bevel=0.6, pattern=mat_pat, line=True)
    # a little hammer on the bench (front right)
    ic.add(capsule(32, 29, 41, 23.5, 1.0), "wood", base=0.55, bevel=0)
    ic.add(rot_ellipse(41.5, 22.6, 3.4, 1.9, -32 + 90), "steel", base=0.62, mode="sphere", line=True)
    ic.sparkle(54, 8, 1, "#bff2e1", "#66d4b9")
    return ic


def icon_skills():
    ic = Icon("Skills")
    ic.add(poly([(22, 40), (30, 44), (26, 61), (22, 56.5), (17, 60)]), "teal", base=0.4, grad=0.5, pattern=folds(0.9, 0.05))
    ic.add(poly([(42, 40), (34, 44), (38, 61), (42, 56.5), (47, 60)]), "teal", base=0.32, grad=0.5, pattern=folds(0.9, 0.05))
    ic.add(circle(32, 27, 21), "gold", mode="sphere", base=0.62)
    ic.add(circle(32, 27, 16), "teal", mode="sphere", base=0.4, line=True, sphere=(32, 27, 16, 16))
    ic.add(poly(star_pts(32, 27.5, 13, 5.4, 5)), "gold", base=0.72, grad=0.6, bevel=0.9, line=True)
    ic.sparkle(49, 8, 2); ic.sparkle(13, 12, 1)
    return ic


def icon_collections():
    ic = Icon("Collections")
    ic.add(poly([(4, 21), (32, 25), (60, 21), (60, 52), (32, 56), (4, 52)]), "teal", base=0.45, grad=0.5)   # cover
    ic.add(poly([(7, 18), (31, 22), (31, 52), (7, 48)]), "cream", base=0.75, grad=0.4, pattern=lambda x, y: -0.1 if x > 28.5 else 0)
    ic.add(poly([(33, 22), (57, 18), (57, 48), (33, 52)]), "cream", base=0.62, grad=0.4, pattern=lambda x, y: -0.1 if x < 35.5 else 0)
    # 4 framed slots with one thing each (gem, coin, leaf, fish-blue gem)
    slots = [(11, 25), (21, 27), (37, 27), (47, 25)]
    for (sx, sy) in slots:
        ic.add(rect(sx, sy, sx + 8, sy + 8), "cream", base=0.3, bevel=0, cast=False)
    for (sx, sy) in [(11, 38), (21, 40), (37, 40), (47, 38)]:
        ic.add(rect(sx, sy, sx + 8, sy + 8), "cream", base=0.3, bevel=0, cast=False)
    ic.add(poly([(15, 26.5), (18.3, 29.5), (15, 32.5), (11.7, 29.5)]), "red", base=0.6, grad=0.8, bevel=0.6)
    ic.add(circle(25, 31, 3.2), "gold", mode="sphere", base=0.65)
    ic.add(union(ellipse(41, 31, 3.4, 2.0), capsule(38, 34, 41, 31, 0.5)), "grass", base=0.6, grad=0.7, bevel=0.5)
    ic.add(poly([(51, 26.5), (54.3, 29.5), (51, 32.5), (47.7, 29.5)]), "blue", base=0.6, grad=0.8, bevel=0.6)
    ic.add(rect(12.5, 40.5, 17.5, 44.5), "gold", base=0.6, grad=0.6, bevel=0.6)             # ingot
    ic.add(circle(25, 44, 3.0), "emerald", mode="sphere", base=0.6)
    ic.add(poly([(39, 44), (43, 41), (44.5, 44), (43, 47)]), "glass", base=0.6, grad=0.7, bevel=0.5)
    ic.add(rect(48.5, 40, 53.5, 46), "violet", base=0.6, grad=0.6, bevel=0.6)
    ic.add(rect(31, 23, 33, 55), "teal", base=0.28, bevel=0)                                # spine
    ic.sparkle(55, 10, 1, "#bff2e1", "#66d4b9")
    return ic


def icon_profile():
    ic = Icon("YourProfile")
    disc = circle(32, 31, 22)
    ic.add(circle(32, 31, 26), "gold", mode="sphere", base=0.6)
    ic.add(disc, "teal", base=0.22, grad=-0.3, bevel=0, line=True)
    b = Icon("tmp")
    bust(b, 32, 14, 1.0, PALC["teal"], base=0.66)
    for ly in b.layers:
        ly.shape = inter(ly.shape, disc); ic.layers.append(ly)
    ic.layers[-1].line = True; ic.layers[-3].line = True
    ic.sparkle(52, 9, 1)
    return ic


def icon_pets():
    ic = Icon("Pets")
    cx, cy = 32.0, 22.0
    ic.add(ering(cx, cy, 23, 11.5, 17.5, 6.8), "teal", mode="torus", torus=(cx, cy, 23, 11.5, 17.5, 6.8), base=0.55, bevel=0)
    for a in (150, 125, 55, 30):                                                          # gold studs on the front arc
        r = 20.3; ic.add(circle(cx + r * math.cos(math.radians(a)), cy + 9.15 * math.sin(math.radians(a)), 1.4), "gold", base=0.8, bevel=0)
    ic.add(rect(8, 17.5, 13.5, 27.5), "gold", base=0.6, grad=0.6, bevel=0.8)                # buckle
    ic.add(rect(9.6, 19.6, 12, 25.4), "teal", base=0.3, bevel=0, cast=False)
    ic.add(ering(32, 34.5, 3.2, 3.0, 1.6, 1.5), "gold", base=0.55, bevel=0)                 # tag loop
    ic.add(circle(32, 46, 13.5), "gold", mode="sphere", base=0.62, line=True)               # tag
    paw = union(ellipse(32, 50, 5.6, 4.3), circle(25, 43.5, 2.4), circle(29.6, 39.6, 2.5), circle(34.4, 39.6, 2.5), circle(39, 43.5, 2.4))
    ic.add(paw, "teal", base=0.3, grad=0.6, bevel=0.7)
    ic.sparkle(48, 37, 1)
    return ic


def icon_bank():
    ic = Icon("Bank")
    ic.add(rect(8, 24, 56, 47), "stone", base=0.12, grad=0.4, bevel=0)                      # dark hall behind the columns
    for cxp in (13.5, 25, 39, 50.5):
        ic.add(rect(cxp - 3.2, 25, cxp + 3.2, 47), "stone", mode="cyl", axis=(0, 1), base=0.7)
        ic.add(rect(cxp - 4.2, 24, cxp + 4.2, 26.5), "stone", base=0.6, bevel=0)
    ic.add(rect(6, 19.5, 58, 24.5), "stone", base=0.6, grad=0.4)                            # entablature
    ic.add(poly([(5, 20), (59, 20), (32, 6)]), "green", base=0.55, grad=0.6)                # roof
    ic.add(poly([(12, 18.5), (52, 18.5), (32, 9.5)]), "stone", base=0.55, grad=0.5, bevel=0.8)
    ic.add(circle(32, 15, 3.2), "gold", mode="sphere", base=0.7)
    ic.add(rect(7, 47, 57, 51), "stone", base=0.6, grad=0.4)                                # steps
    ic.add(rect(4, 51, 60, 56), "stone", base=0.45, grad=0.4)
    for k in range(4):                                                                     # coin stack (front right)
        yk = 55.5 - 3.2 * k
        ic.add(union(rect(42, yk, 57, yk + 2.6), ellipse(49.5, yk + 2.6, 7.5, 2.3)), "gold", base=0.38, grad=0.5, bevel=0)
        ic.add(ellipse(49.5, yk, 7.5, 2.3), "gold", base=0.8, grad=0.5, bevel=0.6)
    ic.sparkle(55, 39, 1)
    return ic


def icon_vault():
    ic = Icon("Vault")
    ic.add(rect(10, 52, 16, 58), "steel", base=0.25); ic.add(rect(39, 52, 45, 58), "steel", base=0.25)
    obox(ic, 7, 15, 47, 54, 13, "vault", base=0.5, kx=0.55, ky=0.6)
    ic.add(rrect(12, 20, 42, 49, 2), "vault", base=0.6, grad=0.5, line=True)                # door
    ic.add(rect(41, 23, 44.5, 28), "steel", base=0.6, grad=0.4, bevel=0.6)                 # hinges
    ic.add(rect(41, 41, 44.5, 46), "steel", base=0.6, grad=0.4, bevel=0.6)
    for (bx, by) in ((15, 23), (39, 23), (15, 46), (39, 46)):
        ic.add(circle(bx, by, 1.3), "gold", base=0.75, bevel=0)
    cx, cy = 26.5, 34.5
    ic.add(circle(cx, cy, 9), "gold", mode="sphere", base=0.5, line=True)                  # dial wheel
    ic.add(circle(cx, cy, 6.2), "vault", base=0.3, bevel=0, cast=False)
    for a in (45, 135, 225, 315):
        ic.add(capsule(cx, cy, cx + 8.8 * math.cos(math.radians(a)), cy + 8.8 * math.sin(math.radians(a)), 1.25), "gold", base=0.7, bevel=0)
    ic.add(circle(cx, cy, 2.6), "gold", mode="sphere", base=0.75)
    ic.add(circle(36.5, 26, 1.6), "green", base=0.95, bevel=0)                              # green lock lamp
    return ic


def icon_bazaar():
    ic = Icon("Bazaar")
    ic.add(capsule(10, 14, 10, 50, 1.9), "wood", mode="cyl", axis=(0, 1), base=0.5)
    ic.add(capsule(54, 14, 54, 50, 1.9), "wood", mode="cyl", axis=(0, 1), base=0.4)
    # scale on the counter
    ic.add(rect(31, 21, 33.6, 44), "gold", mode="cyl", axis=(0, 1), base=0.55)
    ic.add(capsule(18, 24.5, 46, 24.5, 1.2), "gold", base=0.65, bevel=0)
    ic.add(circle(32.3, 21.5, 2.3), "gold", mode="sphere", base=0.75)
    for px_ in (18, 46):
        ic.add(capsule(px_, 24.5, px_ - 4.5, 33.5, 0.55), "gold", base=0.45, bevel=0, cast=False)
        ic.add(capsule(px_, 24.5, px_ + 4.5, 33.5, 0.55), "gold", base=0.45, bevel=0, cast=False)
    ic.add(circle(17, 32.5, 2.0), "gold", mode="sphere", base=0.8)                         # coins in the left pan
    ic.add(circle(20, 32.5, 2.0), "gold", mode="sphere", base=0.7)
    ic.add(poly([(46, 29.5), (49, 32.5), (46, 34), (43, 32.5)]), "emerald", base=0.65, grad=0.8, bevel=0.5)   # gem in the right pan
    for px_ in (18, 46):
        ic.add(inter(ellipse(px_, 33.5, 6.5, 3.6), rect(0, 33.5, 64, 40)), "gold", base=0.55, grad=0.6, bevel=0.6)
    ic.add(poly([(27, 45), (37.6, 45), (35.5, 41), (29.1, 41)]), "gold", base=0.5, grad=0.5)
    # counter with a green cloth front
    obox(ic, 6, 45, 58, 57, 5, "wood", base=0.55, kx=0.5, ky=0.5)
    ic.add(rect(6, 47, 58, 57), "green", base=0.5, grad=0.4, pattern=lambda x, y: -0.14 if int(x - 6) % 10 >= 5 else 0)
    # striped awning with a scalloped edge
    ic.add(poly([(9, 3), (55, 3), (61, 9.5), (3, 9.5)]), "green", base=0.32, grad=0.4)
    aw = union(rect(3, 9.5, 61, 17), *[circle(6.6 + 7.25 * k, 17, 3.62) for k in range(8)])
    ic.add(aw, "cream", base=0.72, grad=0.5)
    ic.add(Shape(lambda x, y: aw(x, y) and int((x - 3) // 7.25) % 2 == 1, aw.bb), "green", base=0.62, grad=0.5)
    return ic


def icon_auction():
    ic = Icon("AuctionHouse")
    # sound block
    ic.add(union(rect(8, 50, 40, 55.5), ellipse(24, 55.5, 16, 4)), "mahog", base=0.32, grad=0.5)
    ic.add(rect(8, 52, 40, 53.5), "gold", base=0.55, bevel=0)
    ic.add(ellipse(24, 50, 16, 4.6), "mahog", base=0.72, grad=0.5, bevel=0.6)
    ic.add(ellipse(24, 50, 11.5, 3.0), "green", base=0.55, grad=0.5, bevel=0.5, cast=False)
    # handle, then the head (axis up-right)
    hx0, hy0 = 27.0, 25.0
    ic.add(capsule(hx0, hy0, 54, 51, 2.6), "mahog", mode="cyl", axis=(1, 1), base=0.62)
    ic.add(circle(54.5, 51.5, 3.6), "gold", mode="sphere", base=0.65)
    ax, ay = 0.7071, -0.7071; pxv, pyv = 0.7071, 0.7071
    def rr(c0, c1, w0, w1):
        return poly([(hx0 + ax * c0 + pxv * w0, hy0 + ay * c0 + pyv * w0), (hx0 + ax * c1 + pxv * w0, hy0 + ay * c1 + pyv * w0),
                     (hx0 + ax * c1 + pxv * w1, hy0 + ay * c1 + pyv * w1), (hx0 + ax * c0 + pxv * w1, hy0 + ay * c0 + pyv * w1)])
    ic.add(rr(-15, 15, -7.5, 7.5), "mahog", mode="cyl", axis=(ax, ay), base=0.62, center=(hx0, hy0))
    ic.add(rr(-11, -8, -7.9, 7.9), "gold", mode="cyl", axis=(ax, ay), base=0.6, center=(hx0 - 9.5 * ax, hy0 - 9.5 * ay), line=True)
    ic.add(rr(8, 11, -7.9, 7.9), "gold", mode="cyl", axis=(ax, ay), base=0.6, center=(hx0 + 9.5 * ax, hy0 + 9.5 * ay), line=True)
    ic.add(rot_ellipse(hx0 - 15 * ax, hy0 - 15 * ay, 2.6, 7.5, -45), "mahog", base=0.75, grad=0.4, bevel=0.6, line=True)
    ic.sparkle(52, 9, 2); ic.sparkle(8, 34, 1)
    return ic


def icon_reforge():
    ic = Icon("Reforge")
    anvil = poly([(4, 24.5), (11, 22.5), (17, 22), (56, 22), (57, 23), (57, 30), (49, 31.5), (43, 34), (41, 43), (49, 47), (52, 53),
                  (13, 53), (16, 47), (24, 43), (22, 34), (17, 31.5), (11, 28.5)])
    ic.add(anvil, "steel", base=0.42, grad=0.6, pattern=lambda x, y: 0.28 if y < 25 else (-0.1 if 31.5 < y < 43 else 0))
    ic.add(poly([(17, 22), (56, 22), (59, 18.5), (20, 18.5)]), "steel", base=0.82, grad=0.4, bevel=0.6)    # anvil face (top)
    ic.add(poly([(4, 24.5), (11, 22.5), (17, 22), (20, 18.5), (12, 19.5)]), "steel", base=0.72, grad=0.4, bevel=0.5)
    ic.add(rect(14, 50, 51, 53), "steel", base=0.22, bevel=0)
    # glowing blade blank on the anvil
    ic.add(poly([(25, 20.5), (44, 20.5), (47, 18.2), (28, 18.2)]), "amber", base=0.85, grad=0.4, bevel=0.5, line=True)
    ic.add(poly([(25, 20.5), (44, 20.5), (44, 22), (25, 22)]), "amber", base=0.6, bevel=0)
    ic.add(poly(star_pts(36, 9.5, 8.5, 2.2, 4, rot=-90)), "gold", base=0.9, grad=0.3, bevel=0.5)   # spark
    ic.sparkle(24, 6, 2, "#fff4cf", "#ffcf6a"); ic.sparkle(49, 6, 1, "#d2fbe0", "#3cc472"); ic.sparkle(50, 14, 1, "#fff0bf", "#f5a332")
    ic.sparkle(21, 13, 1, "#d2fbe0", "#88eaa6")
    return ic


def gem_facets(cx, cy, s):
    """a brilliant-cut gem, side view: crown (3 facets) + pavilion (3 facets); returns [(pts, base)]"""
    P_ = lambda x, y: (cx + x * s, cy + y * s)
    return [
        ([P_(-10, -6), P_(-5, -12), P_(-5, -6)], 0.78),
        ([P_(-5, -12), P_(5, -12), P_(5, -6), P_(-5, -6)], 0.92),
        ([P_(5, -12), P_(10, -6), P_(5, -6)], 0.5),
        ([P_(-10, -6), P_(-5, -6), P_(0, 12)], 0.6),
        ([P_(-5, -6), P_(5, -6), P_(0, 12)], 0.72),
        ([P_(5, -6), P_(10, -6), P_(0, 12)], 0.32),
    ]


def icon_identify():
    ic = Icon("Identify")
    gx, gy = 23.0, 25.0
    for pts, b in gem_facets(gx, gy, 1.55):
        ic.add(poly(pts), "emerald", base=b, grad=0.3, bevel=0.6)
    lx, ly_, lr = 38.0, 33.0, 13.5
    ic.add(capsule(46.5, 42.5, 57, 55, 3.2), "wood", mode="cyl", axis=(0.7, 0.8), base=0.55)    # handle
    ic.add(capsule(45.5, 41.3, 48.5, 44.7, 3.9), "gold", base=0.6, bevel=0.6)
    lens = circle(lx, ly_, lr - 3.2)
    ic.add(lens, "glass", base=0.45, grad=0.6, bevel=0, rim=False)
    # the gem seen through the lens, magnified 1.45x around the lens centre
    for pts, b in gem_facets(gx, gy, 1.55):
        ic.add(inter(poly(xform(pts, lx, ly_, 1.45)), lens), "emerald", base=b + 0.18, grad=0.3, bevel=0, rim=False, cast=False)
    ic.add(inter(Shape(lambda x, y: -3.5 < (x - lx) + (y - ly_) + 6 < 0.8, lens.bb), lens), "glass", base=0.95, bevel=0, rim=False, cast=False)
    ic.add(ering(lx, ly_, lr, lr, lr - 3.2, lr - 3.2), "gold", mode="torus", torus=(lx, ly_, lr, lr, lr - 3.2, lr - 3.2), bevel=0, line=True)
    ic.sparkle(12, 7, 1, "#d2fbe0", "#88eaa6")
    return ic


def icon_players():
    ic = Icon("Players")
    ic.add(rrect(7, 6, 57, 59, 3.5), "violet", base=0.55, grad=0.5)
    ic.add(rrect(11, 10, 53, 55, 2), "violet", base=0.15, grad=-0.2, bevel=0, line=True)
    for k, (yy, hb) in enumerate(((13, 0.85), (27, 0.6), (41, 0.6))):
        if k == 0:
            ic.add(rrect(12.5, yy - 1, 51.5, yy + 12, 1.5), "violet", base=0.38, bevel=0, cast=False)
        ic.add(rrect(15, yy + 1, 24, yy + 10, 1.6), "violet", base=hb, grad=0.5, bevel=0.6)
        ic.px(17, yy + 5, PAL["violet"][0]); ic.px(21, yy + 5, PAL["violet"][0])
        ic.add(rect(27, yy + 2.5, 48 - 6 * k, yy + 5), "cream", base=0.8 if k == 0 else 0.55, bevel=0)
        ic.add(rect(27, yy + 7, 40 - 3 * k, yy + 8.6), "cream", base=0.4, bevel=0)
    ic.add(circle(47.5, 18.5, 2.2), "gold", mode="sphere", base=0.75)                      # the "you" marker on row 1
    return ic


def icon_party():
    ic = Icon("Party")
    bust(ic, 14.5, 12, 0.78, PALC["violet"], base=0.36)
    bust(ic, 49.5, 12, 0.78, PALC["violet"], base=0.3)
    bust(ic, 32, 13, 1.0, PALC["violet"], base=0.74, line=True)
    for ly in ic.layers:
        ly.shape = inter(ly.shape, rect(0, 0, 64, 61))
    ic.add(poly(star_pts(32, 47, 5.2, 2.2, 5)), "gold", base=0.75, grad=0.5, bevel=0.5)
    ic.sparkle(53, 6, 1)
    return ic


def icon_guild():
    ic = Icon("Guild")
    cloth = poly([(13, 10), (51, 10), (51, 59), (32, 48.5), (13, 59)])
    ic.add(cloth, "violet", base=0.52, grad=0.5, pattern=folds(0.42, 0.09, 13))
    ic.add(diff(cloth, poly([(16.5, 13), (47.5, 13), (47.5, 53.3), (32, 44.6), (16.5, 53.3)])), "gold", base=0.55, grad=0.5, bevel=0, cast=False)
    shield = poly([(24, 19), (40, 19), (40, 30), (32, 38), (24, 30)])
    ic.add(shield, "gold", base=0.65, grad=0.6, bevel=0.8, line=True)
    ic.add(poly([(26.6, 21.4), (37.4, 21.4), (37.4, 29), (32, 34.6), (26.6, 29)]), "violet", base=0.3, grad=0.4, bevel=0, cast=False)
    ic.add(poly(star_pts(32, 27, 4.6, 1.5, 4)), "gold", base=0.85, bevel=0)
    ic.add(capsule(8, 9, 56, 9, 2.4), "gold", mode="cyl", axis=(1, 0), base=0.55)          # crossbar
    ic.add(circle(5.5, 9, 3.3), "gold", mode="sphere", base=0.62)
    ic.add(circle(58.5, 9, 3.3), "gold", mode="sphere", base=0.62)
    return ic


def icon_mods():
    ic = Icon("Mods")
    def piece(dx, dy):
        body = rrect(12 + dx, 19 + dy, 44 + dx, 51 + dy, 2)
        return diff(union(body, circle(28 + dx, 14.5 + dy, 5.6), rect(25 + dx, 16 + dy, 31 + dx, 20 + dy),
                          circle(48.5 + dx, 35 + dy, 5.6), rect(43 + dx, 32 + dy, 47 + dx, 38 + dy)),
                    circle(12 + dx, 35 + dy, 5.0), circle(28 + dx, 51 + dy, 5.0))
    ic.add(piece(3, 3.5), "steel", base=0.22, grad=0.3, bevel=0)                          # thickness
    ic.add(piece(0, 0), "steel", base=0.62, grad=0.6, bevel=1.3, bev=0.22)
    for (bx, by) in ((17, 24), (39, 24), (17, 46), (39, 46)):
        ic.add(circle(bx, by, 1.4), "steel", base=0.35, bevel=0, cast=False)
    ic.add(circle(28, 35, 4.6), "teal", mode="sphere", base=0.55, line=True)               # a small gem: "adds something"
    return ic


def icon_server_setup():
    ic = Icon("ServerSetup")
    ic.add(gear(32, 41, 20.5, 15.5, 9, hole=0, rot=10), "steel", base=0.55, grad=0.6, bevel=1.2, bev=0.2)
    ic.add(circle(32, 41, 7), "steel", base=0.25, grad=-0.3, bevel=0, cast=False)
    ic.add(circle(32, 41, 3.6), "steel", mode="sphere", base=0.65)
    crown = poly([(17, 25), (17, 11), (24.5, 18), (32, 7), (39.5, 18), (47, 11), (47, 25)])
    ic.add(crown, "gold", base=0.62, grad=0.6, bevel=0.9, line=True)
    ic.add(rect(16, 23, 48, 29.5), "gold", base=0.5, grad=0.5, bevel=0.8, line=True)
    for (bx, by) in ((17, 10), (32, 6), (47, 10)):
        ic.add(circle(bx, by, 2.1), "gold", mode="sphere", base=0.75)
    ic.add(circle(32, 26.2, 2.2), "red", mode="sphere", base=0.65)
    ic.add(circle(23, 26.2, 1.5), "violet", mode="sphere", base=0.7)
    ic.add(circle(41, 26.2, 1.5), "violet", mode="sphere", base=0.7)
    return ic


def icon_settings():
    ic = Icon("Settings")
    ic.add(gear(47, 17, 12, 8.6, 8, hole=3.4, rot=22.5), "steel", base=0.42, grad=0.6, bevel=1.0)
    ic.add(gear(26, 38, 22, 16.8, 10, hole=6.8, rot=0), "steel", base=0.6, grad=0.6, bevel=1.3, bev=0.22, line=True)
    ic.add(ering(26, 38, 10.5, 10.5, 6.8, 6.8), "steel", base=0.35, grad=-0.4, bevel=0, cast=False)
    return ic


def icon_tooltips():
    ic = Icon("HoverTooltips")
    bubble = union(rrect(5, 5, 57, 42, 8), poly([(13, 38), (27, 38), (10, 53)]))
    ic.add(bubble, "steel", base=0.72, grad=0.5, bevel=1.2, bev=0.16)
    ic.add(circle(31, 13.5, 3.5), "blue", mode="sphere", base=0.45)
    ic.add(union(rrect(27.5, 19.5, 34.5, 34.5, 1), rect(25, 19.5, 34.5, 22), rect(25, 32, 37, 34.5)), "blue", base=0.35, grad=0.6, bevel=0.6)
    ic.add(poly([(42, 35), (42, 55), (46.6, 50.4), (50.2, 58), (53.6, 56.5), (50.2, 49.2), (56.6, 49.2)]), "cream",
           base=0.9, grad=0.3, bevel=0.7, line=True)
    return ic


# ====================================================================== the tile list (SkyyMenu 0.3.15 main view)
# (Name, tile label, category, main-view slot, builder or None = byte copy of the approved Accessory Bag icon, what it shows)
TILES = [
    ("YourProfile",     "Your Profile",     "stuff",  4,  icon_profile,      "a blocky player bust in a gold-rimmed teal portrait medallion"),
    ("Pets",            "Pets",             "stuff",  5,  icon_pets,         "FALLBACK only: a teal collar with gold studs + buckle and a gold tag with a paw print"),
    ("HoverTooltips",   "Hover Tooltips",   "admin",  8,  icon_tooltips,     "a pale steel speech bubble with a navy 'i' and a hover pointer"),
    ("Teleport",        "Teleport",         "travel", 10, icon_teleport,     "a gold portal ring (amber gem studs) round swirling amber energy on a stone plinth"),
    ("PocketDimension", "Pocket Dimension", "stuff",  11, icon_pocket,       "a teal drawstring pouch with a violet-teal swirl rising out of its void opening"),
    ("AccessoryBag",    "Accessory Bag",    "stuff",  12, None,              "REUSED: the approved Accessory Bag icon (art/accessory-bag-icon), byte copy"),
    ("HudEditor",       "HUD Editor",       "stuff",  13, icon_hud,          "a teal screen frame with HUD widgets (health / mana bars, minimap, hotbar), a dashed gold edit box + pointer"),
    ("Crafting",        "Crafting",         "stuff",  14, icon_crafting,     "a wooden workbench with a teal 3 x 3 crafting mat on top and a little hammer"),
    ("Skills",          "Skills",           "stuff",  15, icon_skills,       "a gold star on a teal medallion with a gold rim and two teal ribbon tails"),
    ("Collections",     "Collections",      "stuff",  16, icon_collections,  "EXTRA (not in the 22 asked): an open teal album with 8 framed slots, a different find in each"),
    ("IslandMenu",      "Island Menu",      "travel", 20, icon_island,       "a round floating island with a cottage (amber roof, lit window), a bush, a little amber flag and clouds"),
    ("Bank",            "Bank",             "money",  21, icon_bank,         "a stone bank front (green roof, gold coin in the pediment, 4 columns) with a stack of gold coins"),
    ("Vault",           "Vault",            "money",  22, icon_vault,        "a big green-steel safe with a gold wheel dial, hinges, bolts and a green lock lamp"),
    ("Bazaar",          "Bazaar",           "money",  23, icon_bazaar,       "a market stall (green / cream striped awning, green cloth counter) with gold scales: coins vs an emerald"),
    ("AuctionHouse",    "Auction House",    "money",  24, icon_auction,      "a mahogany gavel with gold bands over a sound block with a green felt top"),
    ("Reforge",         "Reforge",          "money",  25, icon_reforge,      "a steel anvil with a glowing amber blade blank and a gold spark burst (2 green sparks)"),
    ("Identify",        "Identify",         "money",  26, icon_identify,     "a gold magnifying glass over a cut emerald (the gem shows magnified in the lens)"),
    ("Players",         "Players",          "social", 30, icon_players,      "a violet player-list board: 3 rows of head + name, your row highlighted with a gold dot"),
    ("Party",           "Party",            "social", 31, icon_party,        "3 violet player busts, the front one bigger with a gold party star"),
    ("Guild",           "Guild",            "social", 32, icon_guild,        "a violet swallowtail banner with gold trim and a gold shield crest on a gold crossbar"),
    ("Settings",        "Settings",         "admin",  39, icon_settings,     "two steel cogs (big + small)"),
    ("Mods",            "Mods",             "admin",  40, icon_mods,         "a thick steel puzzle piece with 4 rivets and a teal gem"),
    ("ServerSetup",     "Server Setup",     "admin",  41, icon_server_setup, "a steel cog wearing a gold crown (ruby + 2 amethysts)"),
]
CATS = [("travel", "TRAVEL", "#f5a332", "gold / amber"), ("stuff", "YOUR STUFF", "#2fae97", "teal"),
        ("money", "MONEY", "#43aa50", "green / gold"), ("social", "SOCIAL", "#8355b5", "violet"), ("admin", "ADMIN", "#a1aaba", "gray / steel")]


def icon_rel(name):
    return "%s/Skyy_Menu_Icon_%s.png" % (ICON_DIR_REL, name)


def png_bytes(img):
    w, h = P.size(img)
    raw = bytearray()
    for row in img:
        raw.append(0)
        for p in row:
            raw.extend(bytes(max(0, min(255, int(round(v)))) for v in p))
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)) \
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")


def build_icons():
    """name -> (image, png bytes) - pure, no file writes (the validator uses this for the determinism check)"""
    out = {}
    for name, label, cat, slot, fn, what in TILES:
        if fn is None:
            data = open(os.path.join(ROOT, BAG_SRC_REL), "rb").read()
            out[name] = (P.read_png(data), data)
        else:
            img = fn().render()
            out[name] = (img, png_bytes(img))
    return out


# ====================================================================== sheet (RGB bytearray canvas: the sheet is big)
class Canvas:
    def __init__(self, w, h, c):
        self.w, self.h = w, h; self.b = bytearray(bytes(c) * (w * h))

    def rect(self, x0, y0, x1, y1, c):
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(self.w, x1), min(self.h, y1)
        if x1 <= x0: return
        line = bytes(c) * (x1 - x0)
        for y in range(y0, y1):
            i = (y * self.w + x0) * 3; self.b[i:i + len(line)] = line

    def frame(self, x0, y0, x1, y1, c, t=1):
        self.rect(x0, y0, x1, y0 + t, c); self.rect(x0, y1 - t, x1, y1, c)
        self.rect(x0, y0, x0 + t, y1, c); self.rect(x1 - t, y0, x1, y1, c)

    def checker(self, x0, y0, w, h, a, b, s=8):
        for yy in range(0, h, s):
            for xx in range(0, w, s):
                self.rect(x0 + xx, y0 + yy, min(x0 + xx + s, x0 + w), min(y0 + yy + s, y0 + h), a if (xx // s + yy // s) % 2 == 0 else b)

    def blit(self, img, ox, oy, scale=1):
        sw, sh = P.size(img)
        for y in range(sh):
            row = img[y]
            for x in range(sw):
                p = row[x]; a = p[3] / 255.0
                if a <= 0: continue
                for yy in range(scale):
                    ty = oy + y * scale + yy
                    if not 0 <= ty < self.h: continue
                    for xx in range(scale):
                        tx = ox + x * scale + xx
                        if not 0 <= tx < self.w: continue
                        i = (ty * self.w + tx) * 3
                        for k in range(3):
                            self.b[i + k] = int(round(p[k] * a + self.b[i + k] * (1 - a)))

    def text(self, x, y, s, c, scale=1):
        for ch in s:
            g = P._F.get(ch) or P._F.get(ch.upper()) or P._F[" "]
            for i, bit in enumerate(g):
                if bit == "1":
                    self.rect(x + (i % 5) * scale, y + (i // 5) * scale, x + (i % 5 + 1) * scale, y + (i // 5 + 1) * scale, c)
            x += 6 * scale
        return x

    def png(self):
        raw = bytearray()
        for y in range(self.h):
            raw.append(0); raw.extend(self.b[y * self.w * 3:(y + 1) * self.w * 3])
        def chunk(t, d):
            return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
        return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)) \
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")


BG = (24, 26, 38); PANEL = (34, 37, 52); INK = (226, 228, 236); DIM = (150, 156, 176); GOLDT = hx("#e0b060")


def half(img):
    """64 -> 32 preview (box filter; alpha-weighted)"""
    return P.downsample(img, 2)


def build_sheet(icons):
    W, H = 1500, 2190
    cv = Canvas(W, H, BG)
    cv.text(24, 20, "SKYWYNN MENU ICONS - DRAFT V1", GOLDT, 4)
    cv.text(24, 60, "ONE 64 PX ICON PER MENU TILE. HARD ALPHA, 1 PX OUTLINE, LIGHT FROM THE TOP LEFT, ORIGINAL PIXELS.", DIM, 2)
    cv.text(24, 82, "CATEGORY TINTS: TRAVEL GOLD/AMBER - YOUR STUFF TEAL - MONEY GREEN/GOLD - SOCIAL VIOLET - ADMIN STEEL.", DIM, 2)
    y = 116
    CW, CH = 240, 196
    for cat, title, col, desc in CATS:
        names = [t for t in TILES if t[2] == cat]
        rows = (len(names) + 5) // 6
        h = 40 + rows * CH
        cv.rect(16, y, W - 16, y + h, PANEL)
        cv.rect(16, y, W - 16, y + 3, hx(col))
        cv.text(28, y + 13, "%s  (%s)" % (title, desc.upper()), hx(col), 2)
        for k, t in enumerate(names):
            cx = 28 + (k % 6) * CW; cy = y + 40 + (k // 6) * CH
            img = icons[t[0]][0]
            cv.checker(cx, cy, 72, 72, (52, 56, 74), (44, 48, 64))
            cv.blit(img, cx + 4, cy + 4, 1)
            cv.rect(cx, cy + 82, cx + 72, cy + 154, (11, 21, 36))
            cv.blit(img, cx + 4, cy + 86, 1)
            cv.checker(cx + 82, cy, 144, 144, (52, 56, 74), (44, 48, 64))
            cv.blit(img, cx + 90, cy + 8, 2)
            cv.text(cx, cy + 160, t[1].upper(), INK, 2)
            cv.text(cx, cy + 178, "SLOT %d%s" % (t[3], "  (FALLBACK)" if t[0] == "Pets" else ("  (REUSED)" if t[4] is None else ("  (EXTRA)" if t[0] == "Collections" else ""))), DIM, 1)
        y += h + 12
    # ---------------- menu mock (left) + 32 px / on light (right)
    top = y + 8
    pw, ph = 9 * 78 + 44, 6 * 78 + 150
    px0 = 16
    cv.rect(px0, top, px0 + pw, top + ph, (11, 21, 36))
    cv.rect(px0 + 22, top + 14, px0 + pw - 22, top + 17, GOLDT)
    cv.text(px0 + 22, top + 26, "SKYWYNN MENU", GOLDT, 3)
    cv.text(px0 + 260, top + 33, "(MOCK - NOT THE REAL GAME SCREEN)", DIM, 1)
    gx, gy = px0 + 22, top + 56
    by_slot = {t[3]: t for t in TILES}
    for s in range(54):
        sx, sy = gx + (s % 9) * 78, gy + (s // 9) * 78
        cv.rect(sx, sy, sx + 74, sy + 74, (22, 38, 58)); cv.frame(sx, sy, sx + 74, sy + 74, (44, 66, 96))
        if s in by_slot:
            cv.blit(icons[by_slot[s][0]][0], sx + 5, sy + 5, 1)
    by = gy + 6 * 78 + 10
    bx = px0 + (pw - 168) // 2
    cv.rect(bx, by, bx + 168, by + 40, hx("#5a4420")); cv.text(bx + 54, by + 13, "CLOSE", hx("#ffe9c9"), 2)
    cv.text(px0 + 22, by + 52, "MAIN VIEW, SLOTS AS IN SKYYMENU 0.3.15. PETS SHOWS THE FALLBACK HERE (IN GAME: THE PET'S OWN ART).", DIM, 1)
    # right column
    rx = px0 + pw + 16; rw = W - 16 - rx
    cv.rect(rx, top, rx + rw, top + ph, PANEL)
    cv.text(rx + 12, top + 12, "32 PX (HALF SIZE) ON THE MENU NAVY", INK, 2)
    for k, t in enumerate(TILES):
        sx = rx + 12 + (k % 8) * 42; sy = top + 40 + (k // 8) * 42
        cv.rect(sx, sy, sx + 38, sy + 38, (11, 21, 36))
        cv.blit(half(icons[t[0]][0]), sx + 3, sy + 3, 1)
    ly = top + 40 + 3 * 42 + 16
    cv.text(rx + 12, ly, "64 PX ON A LIGHT BACKGROUND", INK, 2)
    for k, t in enumerate(TILES):
        sx = rx + 12 + (k % 5) * 70; sy = ly + 26 + (k // 5) * 70
        cv.rect(sx, sy, sx + 66, sy + 66, (214, 218, 226))
        cv.blit(icons[t[0]][0], sx + 1, sy + 1, 1)
    return cv.png()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    icons = build_icons()
    os.makedirs(os.path.join(OUT, ICON_DIR_REL), exist_ok=True)
    files = []
    for name, label, cat, slot, fn, what in TILES:
        data = icons[name][1]
        with open(os.path.join(OUT, icon_rel(name)), "wb") as fh:
            fh.write(data)
        files.append({"path": icon_rel(name), "bytes": len(data), "sha256": sha(data)})
    sheet = build_sheet(icons)
    with open(os.path.join(OUT, "sheet.png"), "wb") as fh:
        fh.write(sheet)
    files.append({"path": "sheet.png", "bytes": len(sheet), "sha256": sha(sheet)})
    man = {
        "what": "SkyWynn Menu tile icons - DRAFT v1 (one 64 x 64 item icon per main-view tile of the SkyWynn Menu)",
        "generator": "tools/art/make_menu_icons.py", "validator": "tools/art/validate_menu_icons.py",
        "deterministic": True, "original_pixels": True,
        "icon_rules": {"size": [64, 64], "alpha": "hard (0 or 255)", "outline": "1 px #120e1c tinted toward the touching part",
                       "light": "top left", "no_pure_black_or_white": True, "supersample": SS},
        "categories": {c[0]: {"label": c[1], "tint": c[2], "palette": c[3]} for c in CATS},
        "tiles": [{"name": n, "item_id": "Skyy_Menu_Icon_" + n, "tile": label, "category": cat, "main_slot": slot,
                   "file": icon_rel(n), "shows": what,
                   "source": BAG_SRC_REL if fn is None else "generated"} for n, label, cat, slot, fn, what in TILES],
        "files": files,
        "palettes": PAL,
    }
    with open(os.path.join(OUT, "manifest.json"), "w", newline="\n") as fh:
        json.dump(man, fh, indent=1)
        fh.write("\n")
    print("wrote %d icons + sheet.png + manifest.json to %s" % (len(TILES), OUT))


if __name__ == "__main__":
    main()
