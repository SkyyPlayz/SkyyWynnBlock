"""make_clicker_art.py - SAMPLE SHEETS for the shard clicker art upgrade (Skyy 2026-11-22: "please upgrade all the visuals in all the clickers. i
want the islands, the totems and the monsters to all lo9ok like and match the Hytale look and feel."). Step 1 only: a sample for Skyy's approval;
the build round later moves this renderer into the SkyyShards build (CLK_ART_SRC) - see clicker-art-README.md.

Two sheets, one run, deterministic (pure Python: zlib + struct + tools/skyyart.png_decode; no clocks, no randomness - two runs = same bytes):
  research/ui-theme-art/clicker-art/clicker-hytale-samples.png   VANILLA-DERIVED (Hytale block textures + the game's own model icons read from
      Assets.zip at run time) -> git-ignored folder, never commit.
  research/ui-theme-art/clicker-hytale-samples-own.png           OUR OWN DRAWING in the same voxel style (procedural painted textures, our own
      voxel monsters / totem / spirit; no vanilla pixels) + the CURRENT art (our own 0.4.29 drawings, read from the built SkyyShards jar) -> committable.

Run:  python research/ui-theme-art/make_clicker_art.py [--assets <Assets.zip>] [--jar <SkyyShards-0.4.29.jar>]
Assets.zip is opened read-only (zipfile mode 'r'); nothing is written outside research/ui-theme-art/.

The look: chunky voxel islands drawn block by block in a 2:1 isometric view (grass / dirt / stone layers, depth-darkened sides, warm sunlit tops,
cool shaded sides), voxel houses + trees, monsters / spirits = the game's model icons (vanilla sheet) or our voxel models (own sheet), soft
ground shadows, rendered at 2x and box-filtered down (smooth edges, no seams).
"""
import os, sys, math, struct, zlib, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyyart as SA  # noqa: E402  (png_decode + the Assets.zip path only)

OUT_VANILLA = os.path.join(HERE, "clicker-art", "clicker-hytale-samples.png")
OUT_OWN = os.path.join(HERE, "clicker-hytale-samples-own.png")
SS = 2  # internal supersampling of every voxel render


# ============================================================ pictures
class Pic(object):
    """w x h straight-alpha RGBA8 in a bytearray"""
    __slots__ = ("w", "h", "px")

    def __init__(self, w, h, col=(0, 0, 0, 0)):
        self.w, self.h = int(w), int(h)
        self.px = bytearray(bytes(bytearray(col)) * (self.w * self.h))

    @staticmethod
    def of(img):
        p = Pic(img.w, img.h)
        p.px = bytearray(img.px)
        return p

    def get(self, x, y):
        i = (y * self.w + x) * 4
        return self.px[i], self.px[i + 1], self.px[i + 2], self.px[i + 3]

    def over(self, x, y, r, g, b, a):
        if a <= 0 or x < 0 or y < 0 or x >= self.w or y >= self.h:
            return
        i = (y * self.w + x) * 4
        p = self.px
        if a >= 255:
            p[i], p[i + 1], p[i + 2], p[i + 3] = _c(r), _c(g), _c(b), 255
            return
        fa = a / 255.0
        da = p[i + 3] / 255.0
        oa = fa + da * (1 - fa)
        if oa <= 0:
            return
        k = da * (1 - fa)
        p[i] = _c((r * fa + p[i] * k) / oa)
        p[i + 1] = _c((g * fa + p[i + 1] * k) / oa)
        p[i + 2] = _c((b * fa + p[i + 2] * k) / oa)
        p[i + 3] = _c(oa * 255)

    def paste(self, src, x0, y0, mul=1.0):
        for y in range(src.h):
            ty = y0 + y
            if ty < 0 or ty >= self.h:
                continue
            for x in range(src.w):
                i = (y * src.w + x) * 4
                a = src.px[i + 3]
                if a:
                    self.over(x0 + x, ty, src.px[i], src.px[i + 1], src.px[i + 2], a * mul)

    def rect(self, x0, y0, w, h, col):
        col = tuple(col) + (255,) * (4 - len(col))
        for y in range(max(0, y0), min(self.h, y0 + h)):
            for x in range(max(0, x0), min(self.w, x0 + w)):
                self.over(x, y, *col)

    def vgrad(self, x0, y0, w, h, c0, c1):
        x0, x1 = max(0, x0), min(self.w, x0 + w)
        for y in range(max(0, y0), min(self.h, y0 + h)):
            t = (y - y0) / float(max(1, h - 1))
            row = bytes(bytearray([_c(c0[k] + (c1[k] - c0[k]) * t) for k in range(3)] + [255])) * (x1 - x0)
            i = (y * self.w + x0) * 4
            self.px[i:i + len(row)] = row

    def frame(self, x0, y0, w, h, col, t=2):
        self.rect(x0, y0, w, t, col)
        self.rect(x0, y0 + h - t, w, t, col)
        self.rect(x0, y0, t, h, col)
        self.rect(x0 + w - t, y0, t, h, col)

    def png(self):
        raw = bytearray()
        st = self.w * 4
        for y in range(self.h):
            raw.append(0)
            raw += self.px[y * st:(y + 1) * st]

        def chunk(t, b):
            return struct.pack(">I", len(b)) + t + b + struct.pack(">I", zlib.crc32(t + b) & 0xffffffff)
        return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", self.w, self.h, 8, 6, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


def _c(v):
    v = int(v + 0.5)
    return 0 if v < 0 else (255 if v > 255 else v)


def resize(src, nw, nh):
    """area-average resample on premultiplied colour (any scale), separable"""
    nw, nh = max(1, int(nw)), max(1, int(nh))

    def taps(n_in, n_out):
        sc = n_in / float(n_out)
        out = []
        for o in range(n_out):
            a, b = o * sc, (o + 1) * sc
            t = []
            i = int(a)
            while i < b and i < n_in:
                w = min(b, i + 1) - max(a, i)
                if w > 1e-9:
                    t.append((i, w / sc))
                i += 1
            out.append(t)
        return out
    sp = src.px
    pre = [0.0] * (src.w * src.h * 4)
    for i in range(0, len(sp), 4):
        a = sp[i + 3] / 255.0
        pre[i], pre[i + 1], pre[i + 2], pre[i + 3] = sp[i] * a, sp[i + 1] * a, sp[i + 2] * a, sp[i + 3]
    tx = taps(src.w, nw)
    mid = [0.0] * (nw * src.h * 4)
    for y in range(src.h):
        rb = y * src.w * 4
        mb = y * nw * 4
        for x in range(nw):
            r = g = b = a = 0.0
            for (sx, w) in tx[x]:
                j = rb + sx * 4
                r += pre[j] * w
                g += pre[j + 1] * w
                b += pre[j + 2] * w
                a += pre[j + 3] * w
            k = mb + x * 4
            mid[k], mid[k + 1], mid[k + 2], mid[k + 3] = r, g, b, a
    ty = taps(src.h, nh)
    out = Pic(nw, nh)
    op = out.px
    for y in range(nh):
        for x in range(nw):
            r = g = b = a = 0.0
            for (sy, w) in ty[y]:
                j = (sy * nw + x) * 4
                r += mid[j] * w
                g += mid[j + 1] * w
                b += mid[j + 2] * w
                a += mid[j + 3] * w
            k = (y * nw + x) * 4
            if a > 0.5:
                f = 255.0 / a
                op[k], op[k + 1], op[k + 2], op[k + 3] = _c(r * f), _c(g * f), _c(b * f), _c(a)
    return out


def crop_alpha(p, thr=8):
    xs, ys = [], []
    for y in range(p.h):
        for x in range(p.w):
            if p.px[(y * p.w + x) * 4 + 3] > thr:
                xs.append(x)
                ys.append(y)
    if not xs:
        return p
    x0, x1, y0, y1 = min(xs), max(xs) + 1, min(ys), max(ys) + 1
    o = Pic(x1 - x0, y1 - y0)
    for y in range(y0, y1):
        o.px[(y - y0) * o.w * 4:(y - y0 + 1) * o.w * 4] = p.px[(y * p.w + x0) * 4:(y * p.w + x1) * 4]
    return o


def fit(p, mw, mh):
    s = min(mw / float(p.w), mh / float(p.h))
    return resize(p, max(1, round(p.w * s)), max(1, round(p.h * s)))


def light(p, top=1.06, bot=0.86, warm=True):
    """soft top light on a flat icon: brighter / warmer on top, cooler at the feet"""
    o = Pic(p.w, p.h)
    o.px = bytearray(p.px)
    for y in range(p.h):
        t = y / float(max(1, p.h - 1))
        m = top + (bot - top) * t
        wr, wb = (1.03, 0.96) if warm and t < 0.5 else (0.98, 1.03)
        for x in range(p.w):
            i = (y * p.w + x) * 4
            if o.px[i + 3]:
                o.px[i] = _c(o.px[i] * m * wr)
                o.px[i + 1] = _c(o.px[i + 1] * m)
                o.px[i + 2] = _c(o.px[i + 2] * m * wb)
    return o


def shadow(dst, cx, cy, rx, ry, a=90):
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            d = ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2
            if d < 1:
                dst.over(x, y, 20, 24, 18, a * (1 - d) ** 0.8)


def glow(dst, cx, cy, r, col, a=150):
    for y in range(int(cy - r), int(cy + r) + 1):
        for x in range(int(cx - r), int(cx + r) + 1):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy) / r
            if d < 1:
                dst.over(x, y, col[0], col[1], col[2], a * (1 - d) ** 2)


# ============================================================ deterministic noise
def h01(x, y, s=0):
    v = ((x * 73856093) ^ (y * 19349663) ^ (s * 83492791) ^ 0x9e3779b9) & 0xffffffff
    v ^= v >> 13
    v = (v * 0x5bd1e995) & 0xffffffff
    v ^= v >> 15
    return v / 4294967296.0


def vnoise(x, y, s=0):
    xi, yi = int(math.floor(x)), int(math.floor(y))
    fx, fy = x - xi, y - yi
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a, b = h01(xi, yi, s), h01(xi + 1, yi, s)
    c, d = h01(xi, yi + 1, s), h01(xi + 1, yi + 1, s)
    return (a + (b - a) * fx) * (1 - fy) + (c + (d - c) * fx) * fy


def fbm(x, y, s=0):
    return 0.6 * vnoise(x, y, s) + 0.3 * vnoise(x * 2.1, y * 2.1, s + 7) + 0.1 * vnoise(x * 4.3, y * 4.3, s + 13)


# ============================================================ textures (vanilla from Assets.zip, or our own painted ones)
def tex_new(n=32):
    return Pic(n, n, (0, 0, 0, 255))


def mix(c0, c1, t):
    return tuple(c0[k] + (c1[k] - c0[k]) * t for k in range(3))


def paint(n, fn):
    t = tex_new(n)
    for y in range(n):
        for x in range(n):
            r, g, b = fn(x, y)
            i = (y * n + x) * 4
            t.px[i], t.px[i + 1], t.px[i + 2] = _c(r), _c(g), _c(b)
    return t


def own_textures():
    """our own painted 32 px block textures in a warm Hytale-like palette (no vanilla pixels)"""
    T = {}

    def grass(x, y):
        n = fbm(x / 6.0, y / 6.0, 1)
        c = mix((78, 138, 44), (128, 182, 66), n)
        h = h01(x, y, 2)
        if h > 0.93:
            c = (154, 204, 86)
        elif h < 0.06:
            c = (60, 112, 38)
        return c
    T["grass_top"] = paint(32, grass)

    def dirt(x, y, s=3):
        n = fbm(x / 5.0, y / 5.0, s)
        c = mix((112, 74, 42), (152, 108, 62), n)
        h = h01(x, y, s + 1)
        if h > 0.95:
            c = (176, 140, 96)
        elif h < 0.05:
            c = (84, 54, 32)
        return c
    T["dirt"] = paint(32, dirt)

    def gside(x, y):
        lip = 7 + int(4 * vnoise(x / 3.0, 0.5, 4)) + (1 if h01(x, 0, 5) > 0.7 else 0)
        if y < lip:
            return grass(x, y)
        if y == lip:
            return (58, 98, 34)
        return dirt(x, y)
    T["grass_side"] = paint(32, gside)

    def stone(x, y, s=6, base=((104, 104, 98), (150, 146, 132))):
        n = fbm(x / 7.0, y / 4.0, s)
        c = mix(base[0], base[1], n)
        e = abs(vnoise(x / 5.0, y / 3.0, s + 2) - 0.5)
        if e < 0.035:
            c = mix(c, (64, 62, 58), 0.7)
        if h01(x, y, s + 3) > 0.96:
            c = mix(c, (186, 182, 166), 0.6)
        return c
    T["stone"] = paint(32, stone)
    T["stone_moss"] = paint(32, lambda x, y: mix(stone(x, y, 9), (88, 128, 52), 0.55) if fbm(x / 6.0, y / 6.0, 11) > 0.55 else stone(x, y, 9))
    T["stone_deep"] = paint(32, lambda x, y: stone(x, y, 21, ((82, 84, 90), (124, 124, 126))))

    def planks(x, y, base=((122, 82, 48), (162, 114, 66))):
        row = y // 8
        if y % 8 == 7:
            return mix(base[0], (40, 26, 16), 0.6)
        n = 0.55 * vnoise(x / 9.0 + row * 3.7, row * 1.3, 14) + 0.45 * vnoise(x / 1.5, y / 4.0 + row, 15)
        c = mix(base[0], base[1], n)
        if (x + row * 11) % 32 == 0:
            c = mix(c, (40, 26, 16), 0.5)
        return c
    T["planks"] = paint(32, planks)
    T["planks_dark"] = paint(32, lambda x, y: planks(x, y, ((70, 46, 30), (104, 70, 42))))

    def plaster(x, y):
        if x < 3 or x > 28 or y < 3 or y > 28:
            return mix((92, 60, 36), (120, 82, 48), vnoise(x / 2.0, y / 6.0, 16))
        return mix((206, 186, 150), (236, 222, 190), fbm(x / 5.0, y / 5.0, 17))
    T["wall"] = paint(32, plaster)

    def window(x, y):
        if 9 <= x <= 22 and 8 <= y <= 23:
            if x in (9, 22) or y in (8, 23) or x == 15 or x == 16 or y == 15:
                return (78, 50, 30)
            return mix((255, 196, 96), (255, 226, 150), (y - 8) / 15.0)
        return plaster(x, y)
    T["window"] = paint(32, window)

    def door(x, y):
        if x < 4 or x > 27 or y < 2:
            return plaster(x, y)
        if x in (4, 27) or y == 2:
            return (60, 38, 22)
        c = planks(x, y + (x // 6) * 3, ((86, 54, 30), (122, 80, 44)))
        if 21 <= x <= 23 and 16 <= y <= 18:
            c = (210, 180, 90)
        return c
    T["door"] = paint(32, door)

    def roof(x, y):
        row = y // 6
        off = 4 if row % 2 else 0
        if y % 6 == 5:
            return (96, 36, 30)
        if (x + off) % 8 == 0:
            return (120, 46, 36)
        return mix((168, 66, 48), (206, 98, 66), fbm(x / 4.0, y / 3.0, 18) * (1 - (y % 6) / 9.0))
    T["roof"] = paint(32, roof)

    def bark(x, y):
        n = vnoise(x / 1.6, y / 9.0, 19)
        c = mix((82, 54, 34), (128, 88, 54), n)
        if abs(vnoise(x / 2.5, y / 12.0, 20) - 0.5) < 0.05:
            c = (60, 38, 24)
        return c
    T["log"] = paint(32, bark)
    T["log_top"] = paint(32, lambda x, y: mix((176, 132, 80), (120, 82, 48), 0.5 + 0.5 * math.sin(math.hypot(x - 15.5, y - 15.5) * 1.3))
                         if math.hypot(x - 15.5, y - 15.5) < 14 else bark(x, y))

    def leaves(x, y):
        n = fbm(x / 4.0, y / 4.0, 22)
        c = mix((42, 98, 38), (100, 160, 56), n)
        if h01(x, y, 23) > 0.9:
            c = (128, 184, 70)
        if n < 0.3:
            c = (30, 70, 30)
        return c
    T["leaves"] = paint(32, leaves)

    def cobble(x, y):
        best, sec, cid = 9e9, 9e9, 0
        for cy in range(-1, 5):
            for cx in range(-1, 5):
                px = (cx + 0.25 + 0.5 * h01(cx % 4, cy % 4, 24)) * 8
                py = (cy + 0.25 + 0.5 * h01(cx % 4, cy % 4, 25)) * 8
                d = math.hypot(x - px, y - py)
                if d < best:
                    best, sec, cid = d, best, (cx % 4) * 4 + cy % 4
                elif d < sec:
                    sec = d
        if sec - best < 1.2:
            return (62, 60, 54)
        k = h01(cid, 1, 26)
        return mix(mix((112, 110, 100), (158, 154, 140), k), (186, 182, 168), max(0, 0.35 - best / 14.0))
    T["cobble"] = paint(32, cobble)

    def tilled(x, y):
        if y % 8 in (0, 1):
            return mix((58, 36, 22), (74, 48, 28), vnoise(x / 3.0, y, 27))
        return mix((92, 58, 34), (126, 84, 50), fbm(x / 4.0, y / 3.0, 28))
    T["tilled"] = paint(32, tilled)
    T["water"] = paint(32, lambda x, y: mix((52, 120, 178), (96, 170, 214), fbm(x / 6.0 + y / 9.0, y / 3.0, 29)))
    return T


def _crop_opaque(img, n=32):
    best = None
    for y0 in range(0, img.h - n + 1, 4):
        for x0 in range(0, img.w - n + 1, 4):
            cnt = 0
            for y in range(y0, y0 + n, 2):
                for x in range(x0, x0 + n, 2):
                    if img.px[(y * img.w + x) * 4 + 3] < 250:
                        cnt += 1
            if best is None or cnt < best[0]:
                best = (cnt, x0, y0)
            if cnt == 0:
                break
        if best and best[0] == 0:
            break
    _, x0, y0 = best
    o = tex_new(n)
    for y in range(n):
        o.px[y * n * 4:(y + 1) * n * 4] = img.px[((y0 + y) * img.w + x0) * 4:((y0 + y) * img.w + x0 + n) * 4]
    for i in range(3, len(o.px), 4):
        o.px[i] = 255
    return o


def _tint(img, col):
    o = Pic.of(img)
    for i in range(0, len(o.px), 4):
        l = (o.px[i] + o.px[i + 1] + o.px[i + 2]) / 765.0
        o.px[i], o.px[i + 1], o.px[i + 2] = _c(col[0] * l * 1.6), _c(col[1] * l * 1.6), _c(col[2] * l * 1.6)
    return o


def vanilla_sources(zpath):
    """read the vanilla block textures + model / item icons we need (read-only); returns (textures, icons)"""
    z = zipfile.ZipFile(zpath, "r")

    def rd(n):
        return Pic.of(SA.png_decode(z.read(n)))
    bt = "Common/BlockTextures/"
    own = own_textures()
    T = {
        "grass_top": rd(bt + "Soil_Grass_Sunny.png"), "grass_side": rd(bt + "Soil_Grass_Sunny_Side.png"), "dirt": rd(bt + "Soil_Dirt.png"),
        "stone": rd(bt + "Rock_Stone.png"), "stone_moss": rd(bt + "Rock_Stone_Mossy.png"), "stone_deep": rd(bt + "Rock_Stone_2.png"),
        "planks": rd(bt + "Wood_Lightwood_Planks.png"), "planks_dark": rd(bt + "Wood_Hardwood_Planks.png"), "wall": rd(bt + "Wood_Village_Wall_01.png"),
        "log": rd(bt + "Wood_Apple_Trunk_Side.png"), "cobble": rd(bt + "Rock_Stone_Cobble_Side.png"), "tilled": rd(bt + "Soil_Dirt_Tilled.png"),
        "leaves": _crop_opaque(rd("Common/Blocks/Foliage/Leaves/Ball_Textures/Oak.png")),
        "roof": _crop_opaque(rd("Common/Blocks/Structures/Roofs/Slope_Textures/Redwood.png")),
        "log_top": own["log_top"], "water": own["water"],
    }
    # window / door = the vanilla wall with our lit window / plank door painted over it (still vanilla-derived: stays in the ignored sheet)
    for k in ("window", "door"):
        w = Pic.of(T["wall"])
        o = own[k]
        for y in range(32):
            for x in range(32):
                if (k == "window" and 9 <= x <= 22 and 8 <= y <= 23) or (k == "door" and 4 <= x <= 27 and y >= 2):
                    i = (y * 32 + x) * 4
                    w.px[i:i + 4] = o.px[i:i + 4]
        T[k] = w
    I = {}
    for n in ("Rat", "Spider", "Skeleton_Fighter", "Trork_Warrior", "Goblin_Scrapper", "Wolf_Black", "Spirit_Root", "Spirit_Ember", "Spirit_Frost"):
        I[n] = rd("Common/Icons/ModelsGenerated/%s.png" % n)
    for n in ("Plant_Crop_Wheat_Stage_4", "Plant_Crop_Carrot", "Plant_Crop_Lettuce"):
        I[n] = rd("Common/Icons/ItemsGenerated/%s.png" % n)
    z.close()
    return T, I


# ============================================================ the voxel renderer (2:1 isometric, painter's order, cached face sprites)
class Vox(object):
    """scr(i, j, k) = ((i - j) * A, (i + j) * B - k * H) in internal (SS x) pixels"""

    def __init__(self, A, B, H, tex, bevel=()):
        self.A, self.B, self.H = A, B, H
        self.tex = tex
        self.bevel = set(bevel)
        self.cache = {}

    def scr(self, i, j, k):
        return (i - j) * self.A, (i + j) * self.B - k * self.H

    def sprite(self, key, face, shade):
        ck = (key, face, shade)
        if ck in self.cache:
            return self.cache[ck]
        A, B, H = self.A, self.B, self.H
        if face == "T":
            o, du, dv = (0.0, -H), (A, B), (-A, B)
            tk = key + "@top" if (key + "@top") in self.tex else key
        elif face == "R":
            o, du, dv = (0.0, 2 * B - H), (A, -B), (0.0, H)
            tk = key
        else:
            o, du, dv = (-A, B - H), (A, B), (0.0, H)
            tk = key
        t = self.tex[tk]
        det = du[0] * dv[1] - du[1] * dv[0]
        tw, th = t.w, t.h
        e = 0.7 / min(A, H)
        sh = shade / 100.0
        if face == "T":
            mr, mg, mb = sh * 1.05, sh * 1.02, sh * 0.92
        else:
            mr, mg, mb = sh * 0.97, sh * 0.99, sh * 1.05
        bev = key in self.bevel
        rows = []
        for y in range(-H - 1, 2 * B + 1):
            run = []
            x0 = None
            for x in range(-A - 1, A + 1):
                acc = [0, 0, 0]
                n = 0
                inside = False
                for (sx, sy) in ((0.25, 0.25), (0.75, 0.25), (0.25, 0.75), (0.75, 0.75)):
                    px, py = x + sx - o[0], y + sy - o[1]
                    u = (px * dv[1] - py * dv[0]) / det
                    v = (du[0] * py - du[1] * px) / det
                    if -e <= u <= 1 + e and -e <= v <= 1 + e:
                        inside = True
                    uu, vv = min(max(u, 0.0), 0.9999), min(max(v, 0.0), 0.9999)
                    i = (int(vv * th) * tw + int(uu * tw)) * 4
                    acc[0] += t.px[i]
                    acc[1] += t.px[i + 1]
                    acc[2] += t.px[i + 2]
                    n += 1
                if not inside:
                    if x0 is not None:
                        break
                    continue
                if x0 is None:
                    x0 = x
                px, py = x + 0.5 - o[0], y + 0.5 - o[1]
                u = (px * dv[1] - py * dv[0]) / det
                v = (du[0] * py - du[1] * px) / det
                m = 1.0
                if bev:
                    ed = min(u, v, 1 - u, 1 - v) * min(A, H)
                    if ed < 1.0:
                        m = 0.84 if face != "T" else 1.12
                run += [_c(acc[0] / n * mr * m), _c(acc[1] / n * mg * m), _c(acc[2] / n * mb * m), 255]
            if x0 is not None:
                rows.append((y, x0, bytes(bytearray(run))))
        self.cache[ck] = rows
        return rows

    def render(self, blocks, shade_fn=None, pad=2):
        """blocks {(i, j, k): texkey} -> (Pic at internal scale, (ox, oy) = screen of world (0, 0, 0))"""
        A, B, H = self.A, self.B, self.H
        xs, ys = [], []
        for (i, j, k) in blocks:
            sx, sy = self.scr(i, j, k)
            xs += [sx - A, sx + A]
            ys += [sy - H, sy + 2 * B]
        ox, oy = -min(xs) + pad, -min(ys) + pad
        P = Pic(max(xs) - min(xs) + 2 * pad + 2, max(ys) - min(ys) + 2 * pad + 2)
        W = P.w
        order = sorted(blocks, key=lambda b: (b[0] + b[1] + b[2], b[2], b[0]))
        for b in order:
            i, j, k = b
            key = blocks[b]
            faces = []
            if (i, j, k + 1) not in blocks:
                faces.append("T")
            if (i + 1, j, k) not in blocks:
                faces.append("R")
            if (i, j + 1, k) not in blocks:
                faces.append("L")
            if not faces:
                continue
            sx, sy = self.scr(i, j, k)
            sx += ox
            sy += oy
            for f in faces:
                base = {"T": 100, "L": 80, "R": 63}[f]
                sh = shade_fn(b, f, base) if shade_fn else base
                for (y, x0, row) in self.sprite(key, f, sh):
                    yy = sy + y
                    if 0 <= yy < P.h:
                        xx = sx + x0
                        a = (yy * W + xx) * 4
                        P.px[a:a + len(row)] = row
        return P, (ox, oy)


# ============================================================ models
def box(d, x0, y0, z0, x1, y1, z1, key):
    for i in range(x0, x1):
        for j in range(y0, y1):
            for k in range(z0, z1):
                d[(i, j, k)] = key


def island(a, b, depth, seed, flat_top=0):
    """a voxel floating island: ellipse a x b in screen terms (s = i - j, t = i + j), grass / dirt / stone layers, a cone underneath"""
    blocks, top = {}, {}
    R = int(a + b) + 2
    for i in range(-R, R + 1):
        for j in range(-R, R + 1):
            s, t = i - j, i + j
            r = math.sqrt((s / float(a)) ** 2 + (t / float(b)) ** 2)
            r += (vnoise(i / 3.0, j / 3.0, seed) - 0.5) * 0.16
            if r > 1.0:
                continue
            kt = 0
            if not flat_top and t < -b * 0.35 and fbm(i / 4.0, j / 4.0, seed + 1) > 0.62:
                kt = 1
            d = int(depth * (1 - min(1.0, max(0.0, r)) ** 1.5) ** 0.85 + (vnoise(i / 2.0, j / 2.0, seed + 2) - 0.5) * 3) + 2
            top[(i, j)] = kt
            for k in range(kt - d, kt + 1):
                if k == kt:
                    key = "grass"
                elif k >= kt - 2:
                    key = "dirt"
                else:
                    hh = h01(i, j * 7 + k, seed + 3)
                    key = "stone_moss" if (k >= kt - 4 and hh > 0.8) else ("stone_deep" if k < kt - 7 else "stone")
                blocks[(i, j, k)] = key
    return blocks, top


def house(bl, i0, j0, w, d, h, k0=1, door_side="L"):
    box(bl, i0, j0, k0, i0 + w, j0 + d, k0 + h, "wall")
    # windows + door on the two visible faces
    for k in range(k0, k0 + h):
        for i in range(i0, i0 + w):
            if k == k0 + 1 and i % 2 == 1:
                bl[(i, j0 + d - 1, k)] = "window"
        for j in range(j0, j0 + d):
            if k == k0 + 1 and j % 2 == 0:
                bl[(i0 + w - 1, j, k)] = "window"
    bl[(i0 + w // 2, j0 + d - 1, k0)] = "door"
    for c in ((i0, j0), (i0 + w - 1, j0), (i0, j0 + d - 1), (i0 + w - 1, j0 + d - 1)):
        for k in range(k0, k0 + h):
            bl[(c[0], c[1], k)] = "log"
    m = 0
    while True:
        ja, jb = j0 - 1 + m, j0 + d - m
        if ja > jb:
            break
        for i in range(i0, i0 + w):
            for j in range(ja, jb + 1):
                bl[(i, j, k0 + h + m)] = "roof"
        m += 1


def tower(bl, i0, j0, k0=1):
    box(bl, i0, j0, k0, i0 + 2, j0 + 2, k0 + 6, "cobble")
    box(bl, i0 - 1, j0 - 1, k0 + 6, i0 + 3, j0 + 3, k0 + 7, "planks")
    for (a, b) in ((-1, -1), (2, -1), (-1, 2), (2, 2)):
        bl[(i0 + a, j0 + b, k0 + 7)] = "log"
    box(bl, i0 - 1, j0 - 1, k0 + 8, i0 + 3, j0 + 3, k0 + 9, "roof")
    box(bl, i0, j0, k0 + 9, i0 + 2, j0 + 2, k0 + 10, "roof")
    bl[(i0 + 1, j0 + 1, k0 + 1)] = "window"


def tree(bl, i0, j0, k0=1, hgt=4, r=2):
    for k in range(k0, k0 + hgt):
        bl[(i0, j0, k)] = "log"
    for di in range(-r, r + 1):
        for dj in range(-r, r + 1):
            for dk in range(-1, r + 1):
                if di * di + dj * dj + (dk * 1.3) ** 2 <= r * r + 1.2 and h01(di + i0, dj + j0, dk + 40) > 0.08:
                    p = (i0 + di, j0 + dj, k0 + hgt + dk)
                    if p not in bl:
                        bl[p] = "leaves"


def totem_model(spirit_col):
    bl = {}
    box(bl, 0, 0, 0, 9, 9, 2, "cobble")
    box(bl, 2, 2, 2, 7, 7, 17, "log")
    for (ka, eye) in ((13, "eye"), (6, "eye")):
        for (i, j) in ((3, 6), (5, 6)):
            bl[(i, j, ka)] = eye
        for (i, j) in ((6, 3), (6, 5)):
            bl[(i, j, ka)] = eye
        for i in (3, 4, 5):
            bl[(i, 6, ka - 2)] = "mouth"
        for j in (3, 4, 5):
            bl[(6, j, ka - 2)] = "mouth"
        bl[(4, 7, ka - 1)] = "log"
        bl[(7, 4, ka - 1)] = "log"
    for (i0, i1, ks) in ((-3, 2, (13, 14, 15)), (7, 12, (13, 14, 15))):
        for i in range(i0, i1):
            far = (i0 - i) if i0 < 0 else (i - i0)
            for k in ks:
                if (i0 < 0 and k >= 13 + max(0, 1 - (i - i0))) or (i0 > 0 and k >= 13 + max(0, (i - i0) - 3)) or k == 15:
                    bl[(i, 4, k)] = "planks"
    box(bl, 3, 3, 17, 6, 6, 19, spirit_col)
    return bl


# own voxel monsters (our own shapes) -------------------------------------------------------
def m_rat():
    b = {}
    box(b, 0, 0, 1, 8, 4, 4, "fur")
    box(b, 1, 0, 4, 7, 4, 5, "fur")
    box(b, 8, 1, 1, 11, 3, 4, "fur")
    b[(11, 1, 2)] = b[(11, 2, 2)] = "pink"
    b[(10, 2, 3)] = "eyeb"
    for (i, j) in ((8, 0), (8, 3)):
        box(b, i, j, 4, i + 1, j + 1, 6, "pink")
    for (i, j) in ((1, 0), (1, 3), (6, 0), (6, 3)):
        b[(i, j, 0)] = "pink"
    for n, i in enumerate(range(-1, -6, -1)):
        b[(i, 2, 1 + (1 if n >= 3 else 0))] = "pink"
    return b


def m_spider():
    b = {}
    box(b, 0, 0, 2, 6, 6, 6, "chitin")
    box(b, 1, 1, 6, 5, 5, 7, "chitin")
    for p in ((2, 2, 7), (3, 3, 7), (3, 2, 7), (2, 3, 7)):
        b[p] = "red"
    box(b, 6, 1, 2, 9, 5, 5, "chitin")
    for j in (1, 2, 3, 4):
        b[(8, j, 4)] = "red" if j in (2, 3) else "eyeb"
    b[(9, 2, 2)] = b[(9, 3, 2)] = "bone"
    for n in range(4):
        i = 1 + 2 * n
        for (dj, k) in ((6, 5), (7, 6), (8, 6), (9, 5), (10, 4), (10, 3), (10, 2), (10, 1), (10, 0)):
            b[(i, dj, k)] = "leg"
            b[(i, 5 - dj, k)] = "leg"
    return b


def m_skeleton():
    b = {}
    for i in (1, 3):
        box(b, i, 1, 0, i + 1, 2, 6, "bone")
    box(b, 1, 1, 6, 4, 2, 7, "bone")
    for k in range(7, 12):
        box(b, 0, 0, k, 5, 3, k + 1, "bone" if k % 2 else "dark")
    box(b, 2, 1, 7, 3, 2, 12, "bone")
    box(b, -1, 1, 7, 0, 2, 12, "bone")
    box(b, 5, 1, 7, 6, 2, 12, "bone")
    box(b, 0, 0, 12, 5, 4, 16, "bone")
    for i in (1, 3):
        box(b, i, 3, 13, i + 1, 4, 15, "dark")
    b[(1, 3, 14)] = b[(3, 3, 14)] = "red"
    box(b, 1, 3, 12, 4, 4, 13, "dark")
    box(b, 6, 1, 7, 7, 2, 9, "planks_dark")
    box(b, 6, 0, 9, 7, 3, 10, "iron")
    box(b, 6, 1, 10, 7, 2, 17, "iron")
    return b


def m_goblin():
    b = {}
    for i in (1, 3):
        box(b, i, 1, 0, i + 1, 2, 3, "leather")
    box(b, 0, 0, 3, 5, 3, 7, "leather")
    box(b, 0, 2, 5, 5, 3, 6, "iron")
    box(b, -1, 1, 3, 0, 2, 7, "gskin")
    box(b, 5, 1, 3, 6, 2, 7, "gskin")
    box(b, 0, 0, 7, 5, 4, 11, "gskin")
    box(b, -2, 1, 9, 0, 2, 10, "gskin")
    box(b, 5, 1, 9, 7, 2, 10, "gskin")
    b[(-3, 1, 10)] = b[(7, 1, 10)] = "gskin"
    b[(1, 3, 9)] = b[(3, 3, 9)] = "yellow"
    box(b, 1, 3, 8, 4, 4, 8 + 1, "dark")
    b[(2, 3, 8)] = "bone"
    box(b, 6, 1, 1, 7, 2, 7, "planks_dark")
    box(b, 6, 0, 7, 7, 3, 10, "log")
    return b


def m_spirit():
    b = {}
    box(b, 0, 0, 2, 5, 5, 6, "log")
    for p in ((1, 1, 6), (2, 2, 6), (3, 1, 6), (1, 3, 6), (3, 3, 6), (2, 2, 7), (0, 2, 6), (4, 2, 6)):
        b[p] = "leaves"
    b[(2, 4, 4)] = "glow"
    b[(4, 2, 4)] = "glow"
    for (i, j) in ((0, 4), (4, 0), (2, 4), (4, 3)):
        b[(i, j, 1)] = "log"
    b[(0, 4, 0)] = b[(4, 0, 0)] = "log"
    return b


def solid(col, seed=1, n=8, var=0.18):
    return paint(n, lambda x, y: tuple(c * (1 - var / 2 + var * fbm(x / 2.0, y / 2.0, seed)) for c in col))


def model_tex(T):
    M = dict(T)
    M.update({"fur": solid((118, 106, 96), 51), "pink": solid((214, 142, 140), 52), "eyeb": solid((24, 20, 20), 53, var=0.05),
              "chitin": solid((70, 52, 40), 54, var=0.3), "red": solid((210, 40, 34), 55), "bone": solid((226, 218, 190), 56, var=0.12),
              "leg": solid((52, 40, 32), 57), "dark": solid((44, 34, 32), 58, var=0.1), "iron": solid((176, 182, 190), 59, var=0.12),
              "leather": solid((112, 74, 42), 60, var=0.25), "gskin": solid((116, 156, 64), 61, var=0.2), "yellow": solid((250, 220, 70), 62, var=0.05),
              "glow": solid((150, 255, 110), 63, var=0.05), "eye": solid((255, 214, 90), 64, var=0.05), "mouth": solid((40, 26, 18), 65, var=0.05),
              "sglow_g": solid((120, 240, 120), 66, var=0.08), "sglow_b": solid((110, 190, 255), 67, var=0.08)})
    return M


def render_model(bl, tex, A=6, B=3, H=7):
    v = Vox(A, B, H, tex, bevel=("fur", "chitin", "bone", "leg", "iron", "leather", "gskin", "log", "planks", "planks_dark", "cobble",
                                 "red", "pink", "dark", "eyeb", "yellow", "eye", "mouth"))
    glowkeys = ("glow", "eye", "red", "yellow", "sglow_g", "sglow_b")
    p, _ = v.render(bl, shade_fn=lambda b, f, base: 100 if bl[b] in glowkeys else base)
    return crop_alpha(resize(p, p.w // SS, p.h // SS))


# ============================================================ scenes
def tex_with_tops(T):
    X = dict(T)
    X["grass"] = T["grass_side"]
    X["grass@top"] = T["grass_top"]
    X["log@top"] = T["log_top"]
    return X


def island_scene(T, kind, W, Ht, mobs=None, plots=None, crop_icons=None):
    """the island picture (W x Ht at 1x): voxel island + houses / trees (combat) or crop plots (farming); returns (Pic, proj)"""
    A, B, H = 12 * SS // 2, 6 * SS // 2, 12 * SS // 2   # 1x: a block = 12 x 6 x 12 px ... scaled to fit below
    if kind == "combat":
        bl, top = island(26, 12, 13, 5)
        # back row (t = i + j < 0) inside the ellipse: three houses, a watch tower on the left rim, trees on the right
        house(bl, -10, 0, 4, 3, 3)
        house(bl, -5, -5, 4, 3, 3)
        house(bl, 1, -9, 4, 3, 3)
        tower(bl, -10, 7)
        tree(bl, 7, -10, 1, 4, 2)
        tree(bl, 11, -8, 1, 3, 2)
        tree(bl, -8, -6, 1, 3, 1)
        for n in range(-6, 8):  # a cobble road across the town (along s)
            for w in (0, 1):
                p_ = (n // 2 + w, -(n - n // 2) + w, 0)
                if p_ in bl:
                    bl[p_] = "cobble"
    else:
        bl, top = island(20, 10, 11, 9, flat_top=1)
        tree(bl, -9, -8, 1, 4, 2)
        tree(bl, 8, -10, 1, 3, 2)
        house(bl, -2, -11, 3, 3, 2)
        for (pi, pj) in plots:
            for i in range(pi, pi + 4):
                for j in range(pj, pj + 4):
                    bl[(i, j, 0)] = "tilled"
            for i in range(pi - 1, pi + 5):
                for j in (pj - 1, pj + 4):
                    if (i, j, 0) in bl:
                        bl[(i, j, 0)] = "planks"
            for j in range(pj - 1, pj + 5):
                for i in (pi - 1, pi + 4):
                    if (i, j, 0) in bl:
                        bl[(i, j, 0)] = "planks"
    tex = tex_with_tops(T)
    tex["tilled@top"] = T["tilled"]
    tex["tilled"] = T["dirt"]
    v = Vox(A * 2, B * 2, H * 2, tex, bevel=("wall", "window", "door", "roof", "log", "planks", "cobble"))

    def shade(b, f, base):
        i, j, k = b
        kt = top.get((i, j), 0)
        dk = max(0, kt - k)
        m = max(0.5, 1 - 0.045 * dk) if f != "T" else 1.0 - 0.03 * int(3 * h01(i, j, 77))
        return int(base * m / 2) * 2
    p, (ox, oy) = v.render(bl, shade)
    big = resize(p, p.w // SS, p.h // SS)
    s = min((W - 8) / float(big.w), (Ht - 8) / float(big.h))
    pic = resize(big, round(big.w * s), round(big.h * s))
    out = Pic(W, Ht)
    px0, py0 = (W - pic.w) // 2, Ht - pic.h - 4
    # grass tufts + flowers (our own little marks) on the open grass
    occupied = set((b[0], b[1]) for b in bl if b[2] >= 1)
    out.paste(pic, px0, py0)
    sc = s / SS

    def proj(i, j, k=1):
        sx = (i - j) * v.A + ox
        sy = (i + j) * v.B - k * v.H + oy
        return px0 + sx * sc, py0 + sy * sc
    for (i, j), kt in sorted(top.items()):
        if kt != 0 or (i, j) in occupied or bl.get((i, j, 0)) != "grass" or h01(i, j, 91) < 0.82:
            continue
        x, y = proj(i + 0.5, j + 0.5, 1)
        hh = h01(i, j, 92)
        if hh > 0.7:
            cols = [(236, 214, 90), (230, 120, 140), (240, 240, 250), (150, 180, 255)]
            c = cols[int(h01(i, j, 93) * 4)]
            out.over(int(x), int(y) - 1, 60, 120, 40, 255)
            out.over(int(x), int(y) - 2, c[0], c[1], c[2], 255)
        else:
            for dx, hgt in ((-1, 2), (0, 3), (1, 2)):
                for yy in range(hgt):
                    out.over(int(x) + dx, int(y) - yy, 70 + 20 * yy, 130 + 18 * yy, 46, 230)
    if plots and crop_icons:
        for (pi, pj), ic in zip(plots, crop_icons):
            cells = sorted(((i, j) for i in range(pi, pi + 4) for j in range(pj, pj + 4)), key=lambda c: (c[0] + c[1], c[0]))
            for (i, j) in cells:
                x, y = proj(i + 0.5, j + 0.5, 1)
                out.paste(ic, int(x - ic.w / 2), int(y - ic.h + 2))
    if mobs:
        for (i, j, ic) in sorted(mobs, key=lambda m: (m[0] + m[1])):
            x, y = proj(i + 0.5, j + 0.5, 1)
            shadow(out, x, y, ic.w * 0.42, max(3, ic.w * 0.12), 110)
            out.paste(ic, int(x - ic.w / 2), int(y - ic.h + 3))
    return out


def card(ic, W=110, H=140, mh=118):
    """a monster picture as the page's 110 x 140 card: fit, feet on a soft shadow"""
    p = Pic(W, H)
    f = fit(ic, W - 8, mh)
    shadow(p, W / 2.0, H - 12, f.w * 0.42, 6, 120)
    p.paste(f, (W - f.w) // 2, H - 12 - f.h + 4)
    return p


def totem_card(T, spirit_pic, spirit_col, W=120, Ht=220):
    tex = model_tex(tex_with_tops(T))
    tm = render_model(totem_model(spirit_col), tex, A=10, B=5, H=11)
    p = Pic(W, Ht)
    f = fit(tm, W - 6, Ht - 70)
    shadow(p, W / 2.0, Ht - 10, f.w * 0.45, 7, 130)
    tx, ty = (W - f.w) // 2, Ht - 10 - f.h + 4
    p.paste(f, tx, ty)
    sp = fit(spirit_pic, 84, 64)
    gcol = (140, 255, 140) if spirit_col == "sglow_g" else (140, 200, 255)
    glow(p, W / 2.0, ty - 32, 44, gcol, 120)
    p.paste(sp, (W - sp.w) // 2, max(2, ty - 34 - sp.h // 2))
    return p


# ============================================================ text (our own 5 x 7 font)
FONT = {
    "A": "0E 11 11 1F 11 11 11", "B": "1E 11 11 1E 11 11 1E", "C": "0E 11 10 10 10 11 0E", "D": "1E 11 11 11 11 11 1E",
    "E": "1F 10 10 1E 10 10 1F", "F": "1F 10 10 1E 10 10 10", "G": "0E 11 10 17 11 11 0F", "H": "11 11 11 1F 11 11 11",
    "I": "0E 04 04 04 04 04 0E", "J": "07 02 02 02 02 12 0C", "K": "11 12 14 18 14 12 11", "L": "10 10 10 10 10 10 1F",
    "M": "11 1B 15 15 11 11 11", "N": "11 11 19 15 13 11 11", "O": "0E 11 11 11 11 11 0E", "P": "1E 11 11 1E 10 10 10",
    "Q": "0E 11 11 11 15 12 0D", "R": "1E 11 11 1E 14 12 11", "S": "0F 10 10 0E 01 01 1E", "T": "1F 04 04 04 04 04 04",
    "U": "11 11 11 11 11 11 0E", "V": "11 11 11 11 11 0A 04", "W": "11 11 11 15 15 15 0A", "X": "11 11 0A 04 0A 11 11",
    "Y": "11 11 11 0A 04 04 04", "Z": "1F 01 02 04 08 10 1F", "0": "0E 11 13 15 19 11 0E", "1": "04 0C 04 04 04 04 0E",
    "2": "0E 11 01 02 04 08 1F", "3": "1F 02 04 02 01 11 0E", "4": "02 06 0A 12 1F 02 02", "5": "1F 10 1E 01 01 11 0E",
    "6": "06 08 10 1E 11 11 0E", "7": "1F 01 02 04 08 08 08", "8": "0E 11 11 0E 11 11 0E", "9": "0E 11 11 0F 01 02 0C",
    " ": "00 00 00 00 00 00 00", "-": "00 00 00 0E 00 00 00", ".": "00 00 00 00 00 0C 0C", ",": "00 00 00 00 0C 04 08",
    ":": "00 0C 0C 00 0C 0C 00", "/": "00 01 02 04 08 10 00", "(": "02 04 08 08 08 04 02", ")": "08 04 02 02 02 04 08",
    "+": "00 04 04 1F 04 04 00", "=": "00 00 1F 00 1F 00 00", "'": "04 04 08 00 00 00 00", "?": "0E 11 01 02 04 00 04",
    "%": "18 19 02 04 08 13 03", "_": "00 00 00 00 00 00 1F", ">": "08 04 02 01 02 04 08", "<": "02 04 08 10 08 04 02",
}


def text(dst, x, y, s, sc=2, col=(240, 236, 220)):
    for ch in s.upper():
        rows = FONT.get(ch, FONT["?"]).split()
        for ry, hx in enumerate(rows):
            v = int(hx, 16)
            for rx in range(5):
                if v & (16 >> rx):
                    for dy in range(sc):
                        for dx in range(sc):
                            dst.over(x + rx * sc + dx + 1, y + ry * sc + dy + 1, 10, 10, 14, 200)
                    for dy in range(sc):
                        for dx in range(sc):
                            dst.over(x + rx * sc + dx, y + ry * sc + dy, col[0], col[1], col[2], 255)
        x += 6 * sc
    return x


# ============================================================ current art (our own 0.4.29 drawings, from the built jar)
def find_jar(arg):
    if arg:
        return arg
    p = os.path.normpath(ROOT).replace("\\", "/")
    roots = [ROOT]
    k = p.find("/.claude/worktrees/")
    if k > 0:
        roots.append(p[:k])
    for r in roots:
        q = os.path.join(r, "SkyyShards", "SkyyShards-0.4.29.jar")
        if os.path.isfile(q):
            return q
    return None


def current_art(jar):
    if not jar:
        return None
    z = zipfile.ZipFile(jar, "r")
    d = {}
    for n in z.namelist():
        b = n.rsplit("/", 1)[-1]
        if b.startswith("Clk") and b.endswith(".png"):
            d[b[3:-4].replace("@2x", "")] = n
    out = {}
    for k in ("TIsl2", "Isl1", "Totem", "Spirit", "FCrop0", "FCrop1", "FCrop2") + tuple("TMon%d" % i for i in range(32)):
        if k in d:
            out[k] = Pic.of(SA.png_decode(z.read(d[k])))
    z.close()
    return out


# current monster picture per family: TF_LOOKS order (0.4.29 build), Zone 1 by vanilla MaxHealth -> the first looks are Zone 1's
CUR_PICK = {"Rat": "rat", "Spider": "spider", "Skeleton": "skel", "Troll": "troll"}


# ============================================================ the sheet
BG0, BG1 = (34, 40, 52), (24, 28, 36)
SKY0, SKY1 = (120, 176, 226), (206, 228, 240)


def panel(dst, x, y, w, h, sky=True):
    if sky:
        dst.vgrad(x, y, w, h, SKY0, SKY1)
    else:
        dst.vgrad(x, y, w, h, (60, 66, 80), (46, 50, 62))
    dst.frame(x - 2, y - 2, w + 4, h + 4, (196, 160, 96), 2)


# today's ClkTMon<n> pictures (0.4.29 TF_LOOKS order, checked on a contact sheet 2026-11-22): 0 rat, 9 spider (plain), 4 skeleton,
# 5 troll (Trork), 2 goblin
CUR_TROLL, CUR_GOBLIN = (0, 9, 4, 5), (0, 9, 4, 2)


def build_sheet(T, mon_icons, names, cur_idx, spirit_pic, spirit_col, crop_icons, cur, title, note):
    Wd, Hd = 1500, 1110
    S = Pic(Wd, Hd, BG1 + (255,))
    S.vgrad(0, 0, Wd, Hd, BG0, BG1)
    text(S, 30, 18, title, 3, (255, 224, 150))
    text(S, 30, 50, note, 2, (200, 200, 210))
    LX, RX = 30, 770
    # ---- (A) combat
    y = 86
    text(S, LX, y, "(A) COMBAT ZONE 1 TOWN - NEW (ISLAND 700 X 400 = MEDIUM)", 2, (255, 214, 120))
    text(S, RX, y, "CURRENT 0.4.29 (CLKTISL2 + CLKTMON)", 2, (170, 176, 190))
    y += 24
    panel(S, LX, y, 700, 400)
    panel(S, RX, y, 700, 400)
    spots = [(1, 8), (8, 2), (-3, 6), (5, 1)]
    hs = [32, 44, 78, 90]
    mobs = [(spots[n][0], spots[n][1], fit(mon_icons[n], 200, hs[n])) for n in range(4)]
    isl = island_scene(T, "combat", 700, 400, mobs=mobs)
    S.paste(isl, LX, y)
    if cur and "TIsl2" in cur:
        S.paste(cur["TIsl2"], RX, y)
        for n, (cx, cy) in enumerate(((300, 300), (420, 250), (220, 240), (500, 310))):
            m = cur.get("TMon%d" % cur_idx[n])
            if m:
                f = fit(crop_alpha(m), 200, hs[n] * 1.1)
                S.paste(f, RX + cx - f.w // 2, y + cy - f.h)
    y += 412
    text(S, LX, y, "MONSTER CARDS 110 X 140 (ONE PER KIND, SHOWN AT RUN TIME ON EACH SPOT)", 2, (255, 214, 120))
    y += 22
    for n in range(4):
        x = LX + n * 175
        panel(S, x, y, 110, 140, sky=False)
        S.paste(card(mon_icons[n]), x, y)
        text(S, x, y + 146, names[n][:14], 1, (220, 220, 230))
        if cur:
            m = cur.get("TMon%d" % cur_idx[n])
            panel(S, RX + n * 175, y, 110, 140, sky=False)
            if m:
                S.paste(resize(m, 110, 140), RX + n * 175, y)
            text(S, RX + n * 175, y + 146, names[n][:14], 1, (200, 200, 210))
    y += 172
    # ---- (B) totem  (C) farming
    text(S, LX, y, "(B) TOTEM", 2, (255, 214, 120))
    text(S, LX + 170, y, "(C) FARMING ZONE 1, 3 CROP PLOTS (520 X 300)", 2, (255, 214, 120))
    text(S, RX, y, "CURRENT: CLKTOTEM, CLKISL1 + CLKFCROP", 2, (170, 176, 190))
    y += 24
    panel(S, LX, y, 120, 220, sky=False)
    S.paste(totem_card(T, spirit_pic, spirit_col), LX, y)
    panel(S, LX + 170, y, 520, 300)
    plots = [(-6, 1), (-1, 5), (4, 0)]
    S.paste(island_scene(T, "farm", 520, 300, plots=plots, crop_icons=crop_icons), LX + 170, y)
    if cur:
        panel(S, RX, y, 120, 220, sky=False)
        if "Totem" in cur:
            t = fit(cur["Totem"], 110, 160)
            S.paste(t, RX + (120 - t.w) // 2, y + 220 - t.h - 6)
        if "Spirit" in cur:
            sp = fit(cur["Spirit"], 60, 56)
            S.paste(sp, RX + (120 - sp.w) // 2, y + 4)
        panel(S, RX + 170, y, 520, 300)
        if "Isl1" in cur:
            S.paste(cur["Isl1"], RX + 170, y)
            for n, (cx, cy) in enumerate(((170, 150), (270, 190), (370, 150))):
                c = cur.get("FCrop%d" % n)
                if c:
                    f = resize(c, 66, 84)
                    S.paste(f, RX + 170 + cx - 33, y + cy - 40)
    y += 312
    text(S, LX, y, "SAME RENDERER FOR EVERY CLICKER: FORAGING TREES, MINING QUARRY TERRACES + ORE NODES, RANCH ANIMALS, ORCHARD TREES.", 2, (200, 200, 210))
    text(S, LX, y + 22, "GENERATOR: RESEARCH/UI-THEME-ART/MAKE_CLICKER_ART.PY  -  README: CLICKER-ART-README.MD", 2, (160, 164, 176))
    return S


def main(argv):
    zpath = SA.ASSETS_ZIP
    jar = None
    for n, a in enumerate(argv):
        if a == "--assets":
            zpath = argv[n + 1]
        if a == "--jar":
            jar = argv[n + 1]
    cur = current_art(find_jar(jar))
    # ---- OWN sheet (no vanilla pixels): our painted textures + our voxel monsters, totem, spirit, crops
    OT = own_textures()
    MT = model_tex(tex_with_tops(OT))
    own_mons = [light(render_model(m(), MT), 1.04, 0.9) for m in (m_rat, m_spider, m_skeleton, m_goblin)]
    own_spirit = render_model(m_spirit(), MT, A=8, B=4, H=9)

    def crop_px(kind):
        p = Pic(9, 14)
        for x in range(9):
            hgt = 9 + int(4 * h01(x, 1, {"w": 1, "c": 2, "l": 3}[kind]))
            for yy in range(hgt):
                if kind == "w":
                    c = (214, 176, 80) if yy > hgt - 4 else (150, 150, 64)
                    if x % 2 == 0:
                        p.over(x, 13 - yy, c[0], c[1], c[2], 255)
                elif kind == "c":
                    if x % 2 == 1 and yy > 4:
                        p.over(x, 13 - yy, 80, 160, 60, 255)
                    if yy < 3 and 2 <= x <= 6:
                        p.over(x, 13 - yy, 236, 128, 40, 255)
                else:
                    if yy < 6 and abs(x - 4) < 5 - yy * 0.6:
                        p.over(x, 13 - yy, 110 + 15 * yy, 180, 70, 255)
        return p
    own_crops = [crop_px("w"), crop_px("c"), crop_px("l")]
    S = build_sheet(OT, own_mons, ["RAT", "SPIDER", "SKELETON", "GOBLIN"], CUR_GOBLIN, own_spirit, "sglow_g", own_crops, cur,
                    "SHARD CLICKERS - HYTALE LOOK SAMPLE (OUR OWN DRAWING, COMMITTABLE)",
                    "LEFT = NEW VOXEL STYLE: OUR PAINTED TEXTURES + OUR VOXEL MONSTERS (NO GAME PIXELS). RIGHT = TODAY'S ART.")
    open(OUT_OWN, "wb").write(S.png())
    print("wrote", OUT_OWN, S.w, S.h)
    # ---- VANILLA-DERIVED sheet: real Hytale block textures + the game's own model icons (git-ignored folder)
    if os.path.isfile(zpath):
        VT, VI = vanilla_sources(zpath)
        mons = [light(crop_alpha(VI[n])) for n in ("Rat", "Spider", "Skeleton_Fighter", "Trork_Warrior")]
        crops = [fit(crop_alpha(VI[n]), 20, 24) for n in ("Plant_Crop_Wheat_Stage_4", "Plant_Crop_Carrot", "Plant_Crop_Lettuce")]
        S = build_sheet(VT, mons, ["RAT", "SPIDER", "SKELETON FIGHTER", "TRORK WARRIOR"], CUR_TROLL, crop_alpha(VI["Spirit_Root"]), "sglow_g", crops, cur,
                        "SHARD CLICKERS - HYTALE LOOK SAMPLE (VANILLA TEXTURES + MODEL ICONS)",
                        "LEFT = NEW: BLOCK TEXTURES + MONSTER / SPIRIT ICONS READ FROM ASSETS.ZIP AT BUILD TIME. RIGHT = TODAY'S ART. LOCAL ONLY.")
        os.makedirs(os.path.dirname(OUT_VANILLA), exist_ok=True)
        open(OUT_VANILLA, "wb").write(S.png())
        print("wrote", OUT_VANILLA, S.w, S.h)
    else:
        print("Assets.zip not found - vanilla sheet skipped")


if __name__ == "__main__":
    main(sys.argv[1:])
