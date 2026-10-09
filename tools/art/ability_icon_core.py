#!/usr/bin/env python3
"""ability_icon_core - the small paint engine behind the SkyWynn class ability icons (64x64), our own art drawn from code.

How an icon is made (no vanilla file is read, copied or traced; numpy + Pillow only; deterministic):
  1. every shape is a boolean mask at 8x supersampling (512 x 512), written in 64-px icon units,
  2. shapes are painted like a hand-painted Hytale icon: light from the top (a little left), a crisp 45-degree BEVEL band on
     every shape (from an erosion distance, so the bevel has clean facets), a soft top-to-bottom tone gradient, and colour RAMPS
     whose shadows lean cool / violet and whose lights lean warm (hue-shifted, never pure #000 / #fff),
  3. three layers per icon: BACK (soft glows, translucent domes, light rays - blended over the frame's dark tinted field),
     GLYPH (the opaque symbol - hard alpha, gets a 1 px dark hue-shifted outline at 64 px so it reads at 32 px) and FRONT
     (sparkles / glints over the symbol, no outline),
  4. the round dark FRAME with the CLASS-COLOUR RIM is painted last (bevelled, top lit); outside the circle alpha = 0,
     inside alpha = 255 (hard alpha only).
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SIZE = 64
SS = 8
N = SIZE * SS
C = 32.0                      # icon centre (64-px units)
R_OUT = 31.6                  # outer edge of the frame
R_FRAME_IN = 28.6             # dark frame band: R_OUT .. R_FRAME_IN
R_RIM_IN = 26.2               # class-colour rim: R_FRAME_IN .. R_RIM_IN
R_FIELD = 25.6                # dark inner line R_RIM_IN .. R_FIELD, field inside
LIGHT = np.array([-0.42, -0.80, 0.62])
LIGHT = LIGHT / np.linalg.norm(LIGHT)

# pixel-centre coordinate grids in 64-px units
_ax = (np.arange(N) + 0.5) / SS
X, Y = np.meshgrid(_ax, _ax)


# ------------------------------------------------------------------------------------------------------------------ colour
def hx(s):
    s = s.lstrip("#")
    return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], dtype=float)


def ramp(*cols):
    return np.array([hx(c) for c in cols])


def rs(r, t):
    """sample a dark -> light ramp at t (scalar or array, 0..1)"""
    t = np.clip(np.asarray(t, dtype=float), 0.0, 1.0) * (len(r) - 1)
    i = np.minimum(t.astype(int), len(r) - 2)
    f = (t - i)[..., None]
    return r[i] * (1 - f) + r[i + 1] * f


def hexs(c):
    c = np.clip(np.round(np.asarray(c, dtype=float)), 0, 255).astype(int)
    return "#%02x%02x%02x" % tuple(c)


# ------------------------------------------------------------------------------------------------------------------ shapes
def _img():
    return Image.new("L", (N, N), 0)


def _arr(im):
    return np.asarray(im, dtype=np.uint8) > 127


def _s(p):
    return [(x * SS, y * SS) for x, y in p]


def poly(pts):
    im = _img()
    ImageDraw.Draw(im).polygon(_s(pts), fill=255)
    return _arr(im)


def circle(cx, cy, r):
    return (X - cx) ** 2 + (Y - cy) ** 2 <= r * r


def ellipse(cx, cy, rx, ry, rot=0.0):
    a = math.radians(rot)
    dx, dy = X - cx, Y - cy
    u = dx * math.cos(a) + dy * math.sin(a)
    v = -dx * math.sin(a) + dy * math.cos(a)
    return (u / rx) ** 2 + (v / ry) ** 2 <= 1.0


def ering(cx, cy, rx, ry, w, rot=0.0):
    return ellipse(cx, cy, rx, ry, rot) & ~ellipse(cx, cy, max(rx - w, 0.01), max(ry - w, 0.01), rot)


def ring(cx, cy, r_out, r_in):
    d2 = (X - cx) ** 2 + (Y - cy) ** 2
    return (d2 <= r_out * r_out) & (d2 > r_in * r_in)


def capsule(x0, y0, x1, y1, r0, r1=None):
    """tapered stroke from (x0,y0) radius r0 to (x1,y1) radius r1 (round ends)"""
    r1 = r0 if r1 is None else r1
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy
    t = np.clip(((X - x0) * dx + (Y - y0) * dy) / L2, 0, 1)
    px, py = x0 + t * dx, y0 + t * dy
    r = r0 + (r1 - r0) * t
    return (X - px) ** 2 + (Y - py) ** 2 <= r * r


def line(pts, w):
    m = np.zeros((N, N), bool)
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        m |= capsule(x0, y0, x1, y1, w / 2.0)
    return m


def star(cx, cy, ro, ri, n=5, rot=-90.0):
    pts = []
    for k in range(2 * n):
        a = math.radians(rot + k * 180.0 / n)
        r = ro if k % 2 == 0 else ri
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return poly(pts)


def heart(cx, cy, s):
    """heart of width ~2s, centre of the lobes' line at (cx, cy)"""
    lobe = s * 0.52
    m = circle(cx - s * 0.48, cy - s * 0.12, lobe) | circle(cx + s * 0.48, cy - s * 0.12, lobe)
    m |= poly([(cx - s * 0.98, cy + s * 0.02), (cx + s * 0.98, cy + s * 0.02), (cx, cy + s * 1.05)])
    m |= poly([(cx - s * 0.9, cy - s * 0.15), (cx + s * 0.9, cy - s * 0.15), (cx + s * 0.97, cy + s * 0.1),
               (cx - s * 0.97, cy + s * 0.1)])
    return m


def rotpts(pts, cx, cy, deg):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * ca - (y - cy) * sa, cy + (x - cx) * sa + (y - cy) * ca) for x, y in pts]


def field_disc():
    return circle(C, C, R_FIELD)


# ------------------------------------------------------------------------------------------------------------------ bevel
def _erode(m, cross):
    e = m.copy()
    e[1:, :] &= m[:-1, :]
    e[:-1, :] &= m[1:, :]
    e[:, 1:] &= m[:, :-1]
    e[:, :-1] &= m[:, 1:]
    if not cross:
        e[1:, 1:] &= m[:-1, :-1]
        e[1:, :-1] &= m[:-1, 1:]
        e[:-1, 1:] &= m[1:, :-1]
        e[:-1, :-1] &= m[1:, 1:]
    e[0, :] = e[-1, :] = e[:, 0] = e[:, -1] = False
    return e


def inner_dist(m, maxd):
    """approximate (octagonal) distance to the mask edge in SS px, capped at maxd"""
    d = np.zeros(m.shape, float)
    cur = m.copy()
    for k in range(int(maxd)):
        d += cur
        if not cur.any():
            break
        cur = _erode(cur, cross=(k % 2 == 0))
    return d


def bevel_light(m, bevel=1.4, light=LIGHT):
    """per-pixel brightness offset from the bevel facets: >0 faces the light, <0 faces away, 0 on the flat top"""
    w = max(bevel * SS, 1.0)
    d = inner_dist(m, w + 2)
    h = np.clip(d / w, 0, 1)
    gy, gx = np.gradient(h)
    gx, gy = gx * w, gy * w
    n = np.stack([-gx, -gy, np.ones_like(gx)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    rel = n @ light - light[2]
    return rel, h


def vgrad(m):
    """0 at the top of the mask's bounding box, 1 at the bottom"""
    ys = np.where(m.any(axis=1))[0]
    if len(ys) == 0:
        return np.zeros(m.shape)
    y0, y1 = (ys[0] + 0.5) / SS, (ys[-1] + 0.5) / SS
    return np.clip((Y - y0) / max(y1 - y0, 1e-3), 0, 1)


# ------------------------------------------------------------------------------------------------------------------ layers
class Layer:
    """premultiplied RGBA at SS"""

    def __init__(self):
        self.rgb = np.zeros((N, N, 3), float)
        self.a = np.zeros((N, N), float)

    def put(self, m, col, alpha=1.0):
        """paint colour col (array (3,) or (N,N,3)) over the mask with coverage alpha (scalar or (N,N))"""
        a = np.where(m, alpha, 0.0) if m is not None else np.broadcast_to(alpha, (N, N))
        a = np.clip(a, 0, 1)
        col = np.broadcast_to(np.asarray(col, float), (N, N, 3))
        self.rgb = self.rgb * (1 - a[..., None]) + col * a[..., None]
        self.a = self.a * (1 - a) + a

    def add(self, col, amount):
        """additive light (premultiplied) - glows; alpha grows with the light"""
        amount = np.clip(amount, 0, 1)
        col = np.asarray(col, float)
        self.rgb = self.rgb + col[None, None, :] * amount[..., None]
        self.a = np.clip(self.a + amount, 0, 1)
        self.rgb = np.minimum(self.rgb, 255.0 * self.a[..., None] + 0.0)

    def bevel(self, m, rmp, face=0.55, bevel=1.4, grad=0.22, gain=0.9, light=LIGHT, tone=None):
        """paint a bevelled solid: flat top at `face` (+/- grad from top to bottom), bevel facets +/- gain; tone = extra (N,N)"""
        rel, _ = bevel_light(m, bevel, light)
        t = face + grad * (0.5 - vgrad(m)) + gain * rel
        if tone is not None:
            t = t + tone
        self.put(m, rs(rmp, t))
        return t


def blur(m, r64):
    im = Image.fromarray((np.asarray(m, float) * 255).clip(0, 255).astype(np.uint8), "L")
    im = im.filter(ImageFilter.GaussianBlur(r64 * SS))
    return np.asarray(im, float) / 255.0


def glow(layer, m, col, r64, strength=1.0):
    layer.add(hx(col) if isinstance(col, str) else col, blur(m, r64) * strength)


# ------------------------------------------------------------------------------------------------------------------ compose
def down(layer):
    """box-filter SS -> 64: returns premultiplied rgb (64,64,3) and alpha (64,64)"""
    rgb = layer.rgb.reshape(SIZE, SS, SIZE, SS, 3).mean(axis=(1, 3))
    a = layer.a.reshape(SIZE, SS, SIZE, SS).mean(axis=(1, 3))
    return rgb, a


def dilate64(m, cross=False):
    e = m.copy()
    e[1:, :] |= m[:-1, :]
    e[:-1, :] |= m[1:, :]
    e[:, 1:] |= m[:, :-1]
    e[:, :-1] |= m[:, 1:]
    if not cross:
        e[1:, 1:] |= m[:-1, :-1]
        e[1:, :-1] |= m[:-1, 1:]
        e[:-1, 1:] |= m[1:, :-1]
        e[:-1, :-1] |= m[1:, 1:]
    return e


class Style:
    """per-class frame / field colours"""

    def __init__(self, name, cls_hex, rim, field_c, field_e, outline, frame, glow_c):
        self.name, self.cls_hex = name, cls_hex
        self.rim, self.field_c, self.field_e = rim, hx(field_c), hx(field_e)
        self.outline, self.frame, self.glow = hx(outline), frame, hx(glow_c)


def paint_field(style):
    """the dark, class-tinted round field (radial: lighter tinted centre slightly above middle, darker hue-shifted edge)"""
    L = Layer()
    d = np.sqrt((X - C) ** 2 + (Y - (C - 3)) ** 2) / R_FIELD
    t = np.clip(d, 0, 1) ** 1.3
    col = style.field_c[None, None, :] * (1 - t[..., None]) + style.field_e[None, None, :] * t[..., None]
    L.put(circle(C, C, R_OUT + 1), col)
    return L


def paint_frame(style):
    """round dark frame band + class-colour rim, both bevelled and top lit"""
    L = Layer()
    outer = circle(C, C, R_OUT)
    band = outer & ~circle(C, C, R_FRAME_IN)
    rim = circle(C, C, R_FRAME_IN) & ~circle(C, C, R_RIM_IN)
    inner_line = circle(C, C, R_RIM_IN) & ~circle(C, C, R_FIELD)
    # angle-based light on the ring: top-left bright, bottom-right dark (a raised ring)
    ang = np.arctan2(Y - C, X - C)
    lit = -np.sin(ang) * 0.85 - np.cos(ang) * 0.35            # +1 at the top-left
    lit = lit / 1.0
    rr = np.sqrt((X - C) ** 2 + (Y - C) ** 2)
    # band: rounded cross-section (light on the outer slope at top, inner slope at bottom)
    u = np.clip((rr - R_FRAME_IN) / (R_OUT - R_FRAME_IN), 0, 1)       # 0 inner .. 1 outer
    prof = (0.5 - u) * 2                                              # +1 inner edge, -1 outer edge
    tband = 0.45 + 0.28 * lit - 0.18 * np.abs(prof) * 1.0 + 0.12 * (-prof) * lit
    L.put(band, rs(style.frame, tband))
    u2 = np.clip((rr - R_RIM_IN) / (R_FRAME_IN - R_RIM_IN), 0, 1)
    prof2 = (0.5 - u2) * 2
    trim = 0.55 + 0.32 * lit + 0.10 * (-prof2) * lit - 0.06 * np.abs(prof2)
    L.put(rim, rs(style.rim, trim))
    L.put(inner_line, style.outline)
    # 1-px dark outer edge of the frame (hue-shifted, not black)
    edge = outer & ~circle(C, C, R_OUT - 0.9)
    L.put(edge, rs(style.frame, 0.0))
    return L, outer


def compose(style, back, glyph, front, glints=(), outline_glyph=True, glyph_clip=None, extra=None):
    """build the final 64x64 RGBA. glints = [(x, y, hex)] hand-placed 64-px pixels; extra(rgb, a, gmask) = 64-px hook"""
    clip = field_disc() if glyph_clip is None else glyph_clip
    for Lr in (back, glyph, front):
        Lr.rgb *= clip[..., None]
        Lr.a *= clip
    fld = paint_field(style)
    # back over field (premultiplied over)
    base = Layer()
    base.rgb = fld.rgb * (1 - back.a[..., None]) + back.rgb
    base.a = fld.a
    brgb, ba = down(base)
    bcol = brgb / np.maximum(ba[..., None], 1e-6)
    grgb, ga = down(glyph)
    gm = ga >= 0.5
    gcol = grgb / np.maximum(ga[..., None], 1e-6)
    out = bcol.copy()
    if outline_glyph:
        ol = dilate64(gm) & ~gm
        fd = down_mask(field_disc()) >= 0.5
        ol &= fd
        # outline = background pulled 78% toward the class's dark hue-shifted outline colour
        out[ol] = out[ol] * 0.22 + style.outline * 0.78
    out[gm] = gcol[gm]
    frgb, fa = down(front)
    fcol = frgb / np.maximum(fa[..., None], 1e-6)
    out = out * (1 - fa[..., None]) + fcol * fa[..., None]
    if extra is not None:
        extra(out, gm)
    for x, y, c in glints:
        out[y, x] = hx(c)
    # frame on top
    fr, outer = paint_frame(style)
    frgb, fa = down(fr)
    fcol = frgb / np.maximum(fa[..., None], 1e-6)
    om = down_mask(outer)
    alpha = (om >= 0.5).astype(np.uint8) * 255
    k = np.clip(fa / np.maximum(om, 1e-6), 0, 1)[..., None]      # frame share of the in-circle part of each pixel
    out = out * (1 - k) + fcol * k
    out = np.clip(np.round(out), 0, 255).astype(np.uint8)
    # no pure black / white anywhere
    allw = (out >= 252).all(axis=-1)
    out[allw] = (250, 248, 240)
    allb = (out <= 4).all(axis=-1)
    out[allb] = (10, 8, 16)
    rgba = np.dstack([out, alpha])
    rgba[alpha == 0] = 0
    return Image.fromarray(rgba, "RGBA")


def down_mask(m):
    return np.asarray(m, float).reshape(SIZE, SS, SIZE, SS).mean(axis=(1, 3))
