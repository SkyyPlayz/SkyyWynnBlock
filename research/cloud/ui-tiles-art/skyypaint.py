#!/usr/bin/env python3
"""skyypaint - a tiny pure-Python painter for SkyWynn concept art (no Pillow, no numpy, no game files).

Used by research/cloud/ui-tiles-art/make_tiles.py and research/cloud/page-emblems-art/make_emblems.py.
Everything is our own geometry: anti-aliased polygons (exact span coverage, 4 sub-rows), textured faces
(a jittered texel grid = Hytale's chunky painted-block look), oblique boxes and 2:1 iso cubes, a 5 x 7
bitmap font for the review sheets, a PNG writer / reader (zlib only). Deterministic: no clock, no random
module - every 'random' value comes from hsh(). Same input = same bytes.
"""
import math
import struct
import zlib


# ------------------------------------------------------------------ colour + hash
def hx(s):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def mul(c, k):
    return (max(0, min(255, c[0] * k)), max(0, min(255, c[1] * k)), max(0, min(255, c[2] * k)))


def mix(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


def hsh(*v):
    """deterministic 0..1 from integers"""
    h = 2166136261
    for x in v:
        x = int(x) & 0xFFFFFFFF
        for _ in range(4):
            h ^= x & 0xFF
            h = (h * 16777619) & 0xFFFFFFFF
            x >>= 8
    h ^= h >> 13
    h = (h * 0x5bd1e995) & 0xFFFFFFFF
    h ^= h >> 15
    return (h & 0xFFFFFF) / float(0xFFFFFF)


# ------------------------------------------------------------------ canvas
class Canvas(object):
    def __init__(self, w, h, bg=None):
        self.w, self.h = w, h
        n = w * h
        if bg is None:
            self.r = [0.0] * n
            self.g = [0.0] * n
            self.b = [0.0] * n
            self.a = [0.0] * n
        else:
            self.r = [bg[0] / 255.0] * n
            self.g = [bg[1] / 255.0] * n
            self.b = [bg[2] / 255.0] * n
            self.a = [1.0] * n

    def blend(self, x, y, c, a):
        if a <= 0.0 or x < 0 or y < 0 or x >= self.w or y >= self.h:
            return
        if a > 1.0:
            a = 1.0
        i = y * self.w + x
        A = self.a[i]
        oa = a + A * (1.0 - a)
        if oa <= 0.0:
            return
        k = A * (1.0 - a)
        self.r[i] = (c[0] / 255.0 * a + self.r[i] * k) / oa
        self.g[i] = (c[1] / 255.0 * a + self.g[i] * k) / oa
        self.b[i] = (c[2] / 255.0 * a + self.b[i] * k) / oa
        self.a[i] = oa

    def get(self, x, y):
        i = y * self.w + x
        return (self.r[i] * 255.0, self.g[i] * 255.0, self.b[i] * 255.0, self.a[i])

    def paste(self, src, ox, oy, alpha=1.0):
        for y in range(src.h):
            for x in range(src.w):
                i = y * src.w + x
                a = src.a[i] * alpha
                if a > 0.0:
                    self.blend(ox + x, oy + y, (src.r[i] * 255.0, src.g[i] * 255.0, src.b[i] * 255.0), a)

    # -------------------------------------------------------------- polygon fill (exact horizontal coverage, ss sub-rows)
    def poly(self, pts, col, a=1.0, ss=4):
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        y0 = max(0, int(math.floor(min(ys))))
        y1 = min(self.h - 1, int(math.ceil(max(ys))))
        n = len(pts)
        edges = []
        for i in range(n):
            ax, ay = pts[i]
            bx, by = pts[(i + 1) % n]
            if ay != by:
                edges.append((ax, ay, bx, by))
        fn = callable(col)
        w = self.w
        for y in range(y0, y1 + 1):
            cov = {}
            for s in range(ss):
                sy = y + (s + 0.5) / ss
                xs = []
                for ax, ay, bx, by in edges:
                    if (ay <= sy < by) or (by <= sy < ay):
                        xs.append(ax + (sy - ay) * (bx - ax) / (by - ay))
                xs.sort()
                for k in range(0, len(xs) - 1, 2):
                    xa, xb = max(0.0, xs[k]), min(float(w), xs[k + 1])
                    if xb <= xa:
                        continue
                    ia, ib = int(xa), int(xb)
                    if ia == ib:
                        cov[ia] = cov.get(ia, 0.0) + (xb - xa) / ss
                    else:
                        cov[ia] = cov.get(ia, 0.0) + (ia + 1 - xa) / ss
                        for x in range(ia + 1, ib):
                            cov[x] = cov.get(x, 0.0) + 1.0 / ss
                        if ib < w:
                            cov[ib] = cov.get(ib, 0.0) + (xb - ib) / ss
            for x, cv in cov.items():
                if fn:
                    c = col(x + 0.5, y + 0.5)
                    if c is None:
                        continue
                    if len(c) == 4:
                        self.blend(x, y, c, min(1.0, cv) * a * c[3])
                    else:
                        self.blend(x, y, c, min(1.0, cv) * a)
                else:
                    self.blend(x, y, col, min(1.0, cv) * a)

    def rect(self, x, y, w, h, col, a=1.0):
        self.poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], col, a)

    def circle(self, cx, cy, r, col, a=1.0, n=None):
        self.poly(circ_pts(cx, cy, r, r, n), col, a)

    def ellipse(self, cx, cy, rx, ry, col, a=1.0, rot=0.0):
        self.poly(circ_pts(cx, cy, rx, ry, None, rot), col, a)

    def ring(self, cx, cy, r0, r1, col, a=1.0):
        n = max(48, int(r1 * 1.6))
        outer = circ_pts(cx, cy, r1, r1, n)
        inner = circ_pts(cx, cy, r0, r0, n)
        # one even-odd polygon: the outer circle, a horizontal bridge (skipped edges), the inner circle backwards
        self.poly(outer + [outer[0], inner[0]] + inner[:0:-1] + [inner[0]], col, a)

    def line(self, x0, y0, x1, y1, wd, col, a=1.0, cap=True):
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L * wd / 2.0, dx / L * wd / 2.0
        self.poly([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)], col, a)
        if cap and wd >= 2.5:
            self.circle(x0, y0, wd / 2.0, col, a)
            self.circle(x1, y1, wd / 2.0, col, a)

    def stroke(self, pts, wd, col, a=1.0, closed=True):
        n = len(pts)
        m = n if closed else n - 1
        for i in range(m):
            p, q = pts[i], pts[(i + 1) % n]
            self.line(p[0], p[1], q[0], q[1], wd, col, a, cap=False)
        if wd >= 2.5:
            for p in pts:
                self.circle(p[0], p[1], wd / 2.0, col, a, n=12)

    def glow(self, cx, cy, r, col, a=1.0):
        """a soft round light (alpha falls off to the edge)"""
        def f(x, y):
            d = math.hypot(x - cx, y - cy) / r
            if d >= 1.0:
                return None
            t = (1.0 - d) ** 2
            return (col[0], col[1], col[2], t)
        self.poly(circ_pts(cx, cy, r, r, 48), f, a)

    def sparkle(self, cx, cy, r, col=(255, 248, 210), a=1.0):
        self.glow(cx, cy, r * 1.4, col, 0.45 * a)
        self.poly(star_pts(cx, cy, r, 0.18, 4), col, a)
        self.poly(star_pts(cx, cy, r * 0.55, 0.25, 4, math.pi / 4), (255, 255, 255), 0.8 * a)

    # -------------------------------------------------------------- textured faces
    def face(self, o, eu, ev, base, nu, nv, seed, jit=0.10, light=1.0, pick=None, edge=0.0, a=1.0):
        """parallelogram o + s*eu + t*ev, a nu x nv texel grid; each texel = base (or pick(iu, iv)) x light x (1 +- jit);
        edge > 0 darkens the outer texel ring a touch (a painted block's rim)"""
        det = eu[0] * ev[1] - eu[1] * ev[0]
        if abs(det) < 1e-6:
            return
        pts = [o, (o[0] + eu[0], o[1] + eu[1]), (o[0] + eu[0] + ev[0], o[1] + eu[1] + ev[1]), (o[0] + ev[0], o[1] + ev[1])]

        def f(x, y):
            px, py = x - o[0], y - o[1]
            s = (px * ev[1] - py * ev[0]) / det
            t = (eu[0] * py - eu[1] * px) / det
            iu = min(nu - 1, max(0, int(s * nu)))
            iv = min(nv - 1, max(0, int(t * nv)))
            c = pick(iu, iv) if pick else base
            k = light * (1.0 + jit * (hsh(seed, iu, iv) * 2.0 - 1.0))
            if edge and (iu == 0 or iv == 0 or iu == nu - 1 or iv == nv - 1):
                k *= 1.0 - edge
            return mul(c, k)
        self.poly(pts, f, a)

    def box(self, x, y, w, h, d, col, seed=1, tex=(4, 4), jit=0.09, top=None, side=None, outline=(24, 18, 22), ow=2.0,
            pick_front=None, pick_top=None, pick_side=None, lights=(1.0, 1.2, 0.68), edge=0.08):
        """an oblique 3/4 box: front w x h at (x, y), depth d going up-right; textured faces + a dark silhouette line"""
        nu, nv = tex
        du = max(1, int(round(nu * d / max(1.0, w))))
        dv = max(1, int(round(nv * d / max(1.0, h))))
        self.face((x, y), (w, 0), (0, h), col, nu, nv, seed, jit, lights[0], pick_front, edge)
        if d > 0:
            self.face((x, y), (w, 0), (d, -d / 2.0), top or col, nu, du, seed + 7, jit, lights[1], pick_top, edge)
            self.face((x + w, y), (d, -d / 2.0), (0, h), side or col, du, nv, seed + 13, jit, lights[2], pick_side, edge)
        if outline is not None and ow > 0:
            sil = [(x, y), (x + d, y - d / 2.0), (x + w + d, y - d / 2.0), (x + w + d, y + h - d / 2.0), (x + w, y + h), (x, y + h)]
            self.stroke(sil, ow, outline, 0.85)

    def cube(self, tx, ty, s, top, left, right, seed=1, n=4, jit=0.10, pick_top=None, pick_left=None, pick_right=None, h=None,
             outline=None):
        """a 2:1 iso cube, T = the top face's back corner; s = half width; h = side height (default s)"""
        h = s if h is None else h
        self.face((tx - s, ty + s / 2.0), (s, s / 2.0), (0, h), left, n, n, seed + 3, jit, 0.86, pick_left, 0.06)
        self.face((tx, ty + s), (s, -s / 2.0), (0, h), right, n, n, seed + 5, jit, 0.64, pick_right, 0.06)
        self.face((tx, ty), (s, s / 2.0), (-s, s / 2.0), top, n, n, seed, jit, 1.12, pick_top, 0.05)
        if outline is not None:
            self.stroke([(tx, ty), (tx + s, ty + s / 2.0), (tx + s, ty + s / 2.0 + h), (tx, ty + s + h), (tx - s, ty + s / 2.0 + h),
                         (tx - s, ty + s / 2.0)], 1.6, outline, 0.6)

    # -------------------------------------------------------------- backgrounds
    def vgrad(self, x, y, w, h, stops, a=1.0):
        """vertical gradient through [(t, colour), ...]"""
        def f(px, py):
            t = (py - y) / float(h)
            for i in range(len(stops) - 1):
                t0, c0 = stops[i]
                t1, c1 = stops[i + 1]
                if t <= t1 or i == len(stops) - 2:
                    u = 0.0 if t1 == t0 else max(0.0, min(1.0, (t - t0) / (t1 - t0)))
                    return mix(c0, c1, u)
            return stops[-1][1]
        self.rect(x, y, w, h, f, a)

    def cloud(self, cx, cy, sc, col=(255, 255, 255), a=0.85, seed=1, shade=(196, 214, 238)):
        """a puffy cloud = overlapping discs; a flat bluish underside"""
        puffs = []
        for i in range(7):
            ox = (i - 3) * 0.32 * sc + (hsh(seed, i) - 0.5) * 0.12 * sc
            r = (0.30 + 0.22 * (1.0 - abs(i - 3) / 3.0) + 0.08 * hsh(seed, i, 9)) * sc
            puffs.append((cx + ox, cy - r * 0.55, r))
        for px, py, r in puffs:
            self.circle(px, py + r * 0.18, r, shade, a)
        for px, py, r in puffs:
            self.circle(px - r * 0.06, py, r * 0.92, col, a)

    def vignette(self, strength=0.35, bottom=0.0, bottom_h=0):
        cx, cy = self.w / 2.0, self.h / 2.0
        R = math.hypot(cx, cy)
        for y in range(self.h):
            for x in range(self.w):
                d = math.hypot(x + 0.5 - cx, y + 0.5 - cy) / R
                k = 1.0 - strength * max(0.0, d - 0.55) / 0.45
                if bottom_h and y >= self.h - bottom_h:
                    k *= 1.0 - bottom * (y - (self.h - bottom_h)) / float(bottom_h)
                i = y * self.w + x
                self.r[i] *= k
                self.g[i] *= k
                self.b[i] *= k

    def round_mask(self, radius):
        """cut the canvas corners round (alpha) - the tile picture's soft corners"""
        w, h = self.w, self.h
        for y in range(h):
            for x in range(w):
                cx = radius if x < radius else (w - radius if x >= w - radius else None)
                cy = radius if y < radius else (h - radius if y >= h - radius else None)
                if cx is None or cy is None:
                    continue
                d = math.hypot(x + 0.5 - cx, y + 0.5 - cy) - radius
                if d > -0.5:
                    i = y * w + x
                    self.a[i] *= max(0.0, min(1.0, 0.5 - d))

    # -------------------------------------------------------------- text (5 x 7 bitmap font, our own)
    def text(self, x, y, s, col, sc=2, shadow=None, spacing=1):
        cx = x
        for ch in s.upper():
            g = FONT.get(ch, FONT["?"])
            if shadow is not None:
                for r, row in enumerate(g):
                    for c, bit in enumerate(row):
                        if bit == "1":
                            self.rect(cx + c * sc + max(1, sc // 2), y + r * sc + max(1, sc // 2), sc, sc, shadow, 0.8)
            for r, row in enumerate(g):
                for c, bit in enumerate(row):
                    if bit == "1":
                        self.rect(cx + c * sc, y + r * sc, sc, sc, col)
            cx += (len(g[0]) + spacing) * sc
        return cx

    def to_rgba(self):
        out = bytearray()
        for i in range(self.w * self.h):
            a = self.a[i]
            out += bytes((q(self.r[i]), q(self.g[i]), q(self.b[i]), q(a)))
        return bytes(out)


def text_w(s, sc=2, spacing=1):
    return sum((len(FONT.get(ch, FONT["?"])[0]) + spacing) * sc for ch in s.upper()) - spacing * sc


def q(v):
    v = int(round(v * 255.0))
    return 0 if v < 0 else (255 if v > 255 else v)


def circ_pts(cx, cy, rx, ry, n=None, rot=0.0):
    if n is None:
        n = max(20, int(max(rx, ry) * 1.4))
    cr, sr = math.cos(rot), math.sin(rot)
    out = []
    for i in range(n):
        t = 2.0 * math.pi * i / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        out.append((cx + x * cr - y * sr, cy + x * sr + y * cr))
    return out


def star_pts(cx, cy, r, inner=0.4, n=5, rot=0.0):
    out = []
    for i in range(2 * n):
        t = rot - math.pi / 2.0 + math.pi * i / n
        rr = r if i % 2 == 0 else r * inner
        out.append((cx + rr * math.cos(t), cy + rr * math.sin(t)))
    return out


def gear_pts(cx, cy, r_out, r_in, teeth, rot=0.0, tw=0.42):
    """a gear outline: teeth flat-topped trapezoids"""
    out = []
    step = 2.0 * math.pi / teeth
    for i in range(teeth):
        a0 = rot + i * step
        for f, r in ((0.0, r_in), (0.5 - tw / 2 - 0.08, r_in), (0.5 - tw / 2, r_out), (0.5 + tw / 2, r_out), (0.5 + tw / 2 + 0.08, r_in)):
            t = a0 + f * step
            out.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    return out


def rot_pts(pts, cx, cy, ang):
    c, s = math.cos(ang), math.sin(ang)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


def downscale2(src):
    """2 x 2 box filter, alpha-weighted (the @1x copy of an @2x picture)"""
    w, h = src.w // 2, src.h // 2
    dst = Canvas(w, h)
    for y in range(h):
        for x in range(w):
            sr = sg = sb = sa = 0.0
            for dy in (0, 1):
                for dx in (0, 1):
                    i = (2 * y + dy) * src.w + 2 * x + dx
                    a = src.a[i]
                    sr += src.r[i] * a
                    sg += src.g[i] * a
                    sb += src.b[i] * a
                    sa += a
            j = y * w + x
            if sa > 0:
                dst.r[j], dst.g[j], dst.b[j] = sr / sa, sg / sa, sb / sa
            dst.a[j] = sa / 4.0
    return dst


def resample(src, w, h):
    """area-average resample to w x h (alpha-weighted) - for shrinking an approved PNG into a ring"""
    dst = Canvas(w, h)
    fx, fy = src.w / float(w), src.h / float(h)
    for y in range(h):
        y0, y1 = y * fy, (y + 1) * fy
        for x in range(w):
            x0, x1 = x * fx, (x + 1) * fx
            sr = sg = sb = sa = tw = 0.0
            for sy in range(int(y0), min(src.h, int(math.ceil(y1)))):
                wy = min(y1, sy + 1) - max(y0, sy)
                for sx in range(int(x0), min(src.w, int(math.ceil(x1)))):
                    wx = min(x1, sx + 1) - max(x0, sx)
                    wt = wx * wy
                    i = sy * src.w + sx
                    a = src.a[i] * wt
                    sr += src.r[i] * a
                    sg += src.g[i] * a
                    sb += src.b[i] * a
                    sa += a
                    tw += wt
            j = y * w + x
            if sa > 0:
                dst.r[j], dst.g[j], dst.b[j] = sr / sa, sg / sa, sb / sa
            dst.a[j] = sa / tw if tw else 0.0
    return dst


# ------------------------------------------------------------------ PNG
def png_bytes(cv):
    raw = cv.to_rgba()
    rows = bytearray()
    st = cv.w * 4
    for y in range(cv.h):
        rows.append(0)
        rows += raw[y * st:(y + 1) * st]

    def chunk(t, body):
        return struct.pack(">I", len(body)) + t + body + struct.pack(">I", zlib.crc32(t + body) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(rows), 9)) + chunk(b"IEND", b""))


def save(cv, path):
    data = png_bytes(cv)
    with open(path, "wb") as f:
        f.write(data)
    return data


def load_png(path):
    """8-bit RGB / RGBA / palette PNG, non-interlaced -> Canvas"""
    data = open(path, "rb").read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", path
    pos, idat, plte, trns = 8, b"", None, None
    w = h = ct = bd = 0
    while pos < len(data):
        n = struct.unpack(">I", data[pos:pos + 4])[0]
        t = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + n]
        if t == b"IHDR":
            w, h, bd, ct, _, _, il = struct.unpack(">IIBBBBB", body)
            assert bd == 8 and il == 0, (path, bd, il)
        elif t == b"IDAT":
            idat += body
        elif t == b"PLTE":
            plte = body
        elif t == b"tRNS":
            trns = body
        pos += 12 + n
    bpp = {2: 3, 6: 4, 3: 1, 0: 1, 4: 2}[ct]
    raw = zlib.decompress(idat)
    st = w * bpp
    prev = bytearray(st)
    cv = Canvas(w, h)
    p = 0
    for y in range(h):
        ft = raw[p]
        line = bytearray(raw[p + 1:p + 1 + st])
        p += 1 + st
        for i in range(st):
            a = line[i - bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i - bpp] if i >= bpp else 0
            if ft == 1:
                line[i] = (line[i] + a) & 255
            elif ft == 2:
                line[i] = (line[i] + b) & 255
            elif ft == 3:
                line[i] = (line[i] + (a + b) // 2) & 255
            elif ft == 4:
                pp = a + b - c
                pa, pb, pc = abs(pp - a), abs(pp - b), abs(pp - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        prev = line
        for x in range(w):
            j = y * w + x
            if ct == 6:
                r, g, b_, al = line[4 * x:4 * x + 4]
            elif ct == 2:
                r, g, b_ = line[3 * x:3 * x + 3]
                al = 255
            elif ct == 3:
                k = line[x]
                r, g, b_ = plte[3 * k:3 * k + 3]
                al = trns[k] if trns is not None and k < len(trns) else 255
            elif ct == 4:
                r = g = b_ = line[2 * x]
                al = line[2 * x + 1]
            else:
                r = g = b_ = line[x]
                al = 255
            cv.r[j], cv.g[j], cv.b[j], cv.a[j] = r / 255.0, g / 255.0, b_ / 255.0, al / 255.0
    return cv


# ------------------------------------------------------------------ 5 x 7 font (our own glyphs)
_G = {
    "A": "01110 10001 10001 11111 10001 10001 10001", "B": "11110 10001 10001 11110 10001 10001 11110",
    "C": "01110 10001 10000 10000 10000 10001 01110", "D": "11110 10001 10001 10001 10001 10001 11110",
    "E": "11111 10000 10000 11110 10000 10000 11111", "F": "11111 10000 10000 11110 10000 10000 10000",
    "G": "01110 10001 10000 10111 10001 10001 01111", "H": "10001 10001 10001 11111 10001 10001 10001",
    "I": "111 010 010 010 010 010 111", "J": "00111 00010 00010 00010 00010 10010 01100",
    "K": "10001 10010 10100 11000 10100 10010 10001", "L": "10000 10000 10000 10000 10000 10000 11111",
    "M": "10001 11011 10101 10101 10001 10001 10001", "N": "10001 11001 10101 10011 10001 10001 10001",
    "O": "01110 10001 10001 10001 10001 10001 01110", "P": "11110 10001 10001 11110 10000 10000 10000",
    "Q": "01110 10001 10001 10001 10101 10010 01101", "R": "11110 10001 10001 11110 10100 10010 10001",
    "S": "01111 10000 10000 01110 00001 00001 11110", "T": "11111 00100 00100 00100 00100 00100 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110", "V": "10001 10001 10001 10001 10001 01010 00100",
    "W": "10001 10001 10001 10101 10101 10101 01010", "X": "10001 10001 01010 00100 01010 10001 10001",
    "Y": "10001 10001 01010 00100 00100 00100 00100", "Z": "11111 00001 00010 00100 01000 10000 11111",
    "0": "01110 10001 10011 10101 11001 10001 01110", "1": "010 110 010 010 010 010 111",
    "2": "01110 10001 00001 00010 00100 01000 11111", "3": "11110 00001 00001 01110 00001 00001 11110",
    "4": "00010 00110 01010 10010 11111 00010 00010", "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110", "7": "11111 00001 00010 00100 01000 01000 01000",
    "8": "01110 10001 10001 01110 10001 10001 01110", "9": "01110 10001 10001 01111 00001 00010 01100",
    " ": "000 000 000 000 000 000 000", "-": "000 000 000 111 000 000 000", ".": "0 0 0 0 0 0 1",
    ",": "00 00 00 00 00 01 10", ":": "0 0 1 0 0 1 0", "/": "00001 00010 00010 00100 01000 01000 10000",
    "(": "01 10 10 10 10 10 01", ")": "10 01 01 01 01 01 10", "@": "01110 10001 10111 10101 10111 10000 01110",
    "+": "000 000 010 111 010 000 000", "%": "11001 11010 00010 00100 01000 01011 10011", "'": "1 1 0 0 0 0 0",
    "?": "01110 10001 00001 00010 00100 00000 00100", "=": "000 000 111 000 111 000 000", "#": "01010 11111 01010 01010 11111 01010 00000",
    ">": "100 010 001 001 001 010 100", "<": "001 010 100 100 100 010 001", "!": "1 1 1 1 1 0 1", "_": "00000 00000 00000 00000 00000 00000 11111",
    "[": "11 10 10 10 10 10 11", "]": "11 01 01 01 01 01 11", "&": "01100 10010 10100 01000 10101 10010 01101",
}
FONT = dict((k, v.split()) for k, v in _G.items())
