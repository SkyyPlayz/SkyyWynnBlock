"""make_hotbar_items - DRAFT icons for the SkyWynn hotbar ABILITY ITEMS (ART-RESUME queue #8; research/cloud/Ability-Input-Design.md
section 2): a soulbound hotbar item that casts one thing when you select its slot. Two kinds:
  * MIRROR items - one per class ability (35): the same ability as its key, so the item shows the SAME ability glyph as the approved
    round ability icon (painted by the same painter in make_ability_icons.py), but on a different OBJECT: a square, chamfered,
    class-rimmed stone TABLET with visible thickness, seen as an item (transparent around it), not as a round HUD button.
  * UTILITY items - Loadout (next saved rune loadout) and Hints (replay the class tutorial), in a neutral gold-rimmed slate tablet.
64 x 64 RGBA, hard alpha, no pure #000 / #fff. Deterministic. Writes into art/hotbar-items/ (never touches art/ability-icons/).
    python3 tools/art/make_hotbar_items.py [--out DIR] [--only Meteor,Loadout]
"""
import argparse
import json
import hashlib
import math
import os
import sys

import numpy as np
from PIL import Image

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_ability_icons as M          # noqa: E402  (ramps, painters, ICONS)
from ability_icon_core import (Layer, X, Y, N, SS, SIZE, rs, hx, ramp, poly, circle, capsule, line, glow, down,  # noqa: E402
                               dilate64, down_mask, inner_dist)
import ability_icon_core as K          # noqa: E402

DEFAULT_OUT = os.path.join(os.path.dirname(os.path.dirname(HERE)), "art", "hotbar-items")
ICON_DIR = os.path.join("Common", "Icons", "ItemsGenerated")
PREFIX = "SkyyClasses_AbilityItem_"

# ---------------------------------------------------------------------------------------------------------- tablet geometry
TX0, TY0, TX1, TY1 = 4.5, 4.0, 55.5, 55.0       # front face of the tablet (64-px units)
CH = 6.0                                         # corner chamfer
DEPTH = 2.5                                      # thickness, seen to the lower right
BORDER = 2.8                                     # class-colour border band
LINE = 0.8                                       # dark line between border and face
GS = 0.95                                        # ability glyph scale on the face
FCX, FCY = (TX0 + TX1) / 2, (TY0 + TY1) / 2      # face centre


def chamfer(x0, y0, x1, y1, c):
    return poly([(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c)])


def tablet_masks():
    front = chamfer(TX0, TY0, TX1, TY1, CH)
    body = front.copy()
    k = 0.25
    while k <= DEPTH + 1e-6:
        body |= chamfer(TX0 + k, TY0 + k, TX1 + k, TY1 + k, CH)
        k += 0.25
    side = body & ~front
    b = BORDER
    inner = chamfer(TX0 + b, TY0 + b, TX1 - b, TY1 - b, max(CH - b * 0.45, 1.0))
    face = chamfer(TX0 + b + LINE, TY0 + b + LINE, TX1 - b - LINE, TY1 - b - LINE, max(CH - (b + LINE) * 0.45, 1.0))
    return body, front, side, front & ~inner, inner & ~face, face


BODY, FRONT, SIDE, BORDER_M, LINE_M, FACE = tablet_masks()


def scale_layer(L, s, cx, cy):
    """shrink a 64-unit painter layer by s about the icon centre and move its centre to (cx, cy)"""
    n2 = int(round(N * s))
    out = Layer()
    ox = int(round(cx * SS - n2 / 2.0))
    oy = int(round(cy * SS - n2 / 2.0))
    chans = [L.rgb[..., i] for i in range(3)] + [L.a]
    res = []
    for ch in chans:
        im = Image.fromarray(ch.astype(np.float32), "F").resize((n2, n2), Image.BILINEAR)
        res.append(np.asarray(im))
    canvas = [np.zeros((N, N), np.float32) for _ in range(4)]
    ys0, xs0 = max(oy, 0), max(ox, 0)
    ys1, xs1 = min(oy + n2, N), min(ox + n2, N)
    for c, r in zip(canvas, res):
        c[ys0:ys1, xs0:xs1] = r[ys0 - oy:ys1 - oy, xs0 - ox:xs1 - ox]
    out.rgb = np.stack(canvas[:3], -1).astype(float)
    out.a = canvas[3].astype(float)
    return out


def paint_face(style):
    L = Layer()
    d = np.maximum(np.abs(X - FCX), np.abs(Y - (FCY - 3))) * 0.55 + np.sqrt((X - FCX) ** 2 + (Y - (FCY - 3)) ** 2) * 0.45
    t = np.clip(d / 24.0, 0, 1) ** 1.3
    col = style.field_c[None, None, :] * (1 - t[..., None]) + style.field_e[None, None, :] * t[..., None]
    L.put(FACE | LINE_M, col)
    return L


def paint_tablet(style, stud):
    """side (thickness), class-colour bevelled border, dark line, corner studs, 1-px dark silhouette edge"""
    L = Layer()
    # thickness: darkest rim tones, a little lighter toward the bottom edge's lip
    L.put(SIDE, rs(style.rim, 0.10))
    L.put(SIDE & (inner_dist(SIDE, 6) > 0.9 * SS) & ~K.circle(-99, -99, 1), rs(style.rim, 0.16))
    L.bevel(BORDER_M, style.rim, face=0.6, bevel=1.1, grad=0.22, gain=0.95)
    L.put(LINE_M, style.outline)
    # corner studs on the four chamfers
    b = BORDER / 2
    for sx, sy in ((TX0 + CH * 0.5 + b * 0.55, TY0 + CH * 0.5 + b * 0.55), (TX1 - CH * 0.5 - b * 0.55, TY0 + CH * 0.5 + b * 0.55),
                   (TX0 + CH * 0.5 + b * 0.55, TY1 - CH * 0.5 - b * 0.55), (TX1 - CH * 0.5 - b * 0.55, TY1 - CH * 0.5 - b * 0.55)):
        m = circle(sx, sy, 1.5)
        L.bevel(m, stud, face=0.62, bevel=0.6, grad=0.2, gain=1.0)
    # 1-px dark edge round the whole silhouette
    edge = BODY & ~erode_mask(BODY, 0.9)
    L.put(edge, rs(style.frame, 0.0))
    return L


def erode_mask(m, r64):
    return inner_dist(m, int(r64 * SS) + 2) >= r64 * SS


def compose_item(style, back, glyph, front, glints=(), stud=None):
    stud = M.STEEL if stud is None else stud
    for Lr in (back, glyph, front):
        Lr.rgb *= FACE[..., None]
        Lr.a *= FACE
    fld = paint_face(style)
    base = Layer()
    base.rgb = fld.rgb * (1 - back.a[..., None]) + back.rgb * FACE[..., None]
    base.a = fld.a
    brgb, ba = down(base)
    bcol = brgb / np.maximum(ba[..., None], 1e-6)
    grgb, ga = down(glyph)
    gm = ga >= 0.5
    gcol = grgb / np.maximum(ga[..., None], 1e-6)
    out = bcol.copy()
    fm = down_mask(FACE) >= 0.5
    ol = dilate64(gm) & ~gm & fm
    out[ol] = out[ol] * 0.22 + style.outline * 0.78
    out[gm] = gcol[gm]
    frgb, fa = down(front)
    fcol = frgb / np.maximum(fa[..., None], 1e-6)
    out = out * (1 - fa[..., None]) + fcol * fa[..., None]
    for x, y, c in glints:
        if 0 <= x < SIZE and 0 <= y < SIZE and fm[y, x]:
            out[y, x] = hx(c)
    tab = paint_tablet(style, stud)
    trgb, ta = down(tab)
    tcol = trgb / np.maximum(ta[..., None], 1e-6)
    om = down_mask(BODY)
    k = np.clip(ta / np.maximum(om, 1e-6), 0, 1)[..., None]
    out = out * (1 - k) + tcol * k
    alpha = (om >= 0.5).astype(np.uint8) * 255
    out = np.clip(np.round(out), 0, 255).astype(np.uint8)
    allw = (out >= 252).all(axis=-1)
    out[allw] = (250, 248, 240)
    allb = (out <= 4).all(axis=-1)
    out[allb] = (10, 8, 16)
    rgba = np.dstack([out, alpha])
    rgba[alpha == 0] = 0
    return Image.fromarray(rgba, "RGBA")


def render_mirror(painter, style):
    back, g, front, glints = painter()
    back, g, front = (scale_layer(Lr, GS, FCX, FCY) for Lr in (back, g, front))
    gl = [(int(round(FCX + (x - 32) * GS)), int(round(FCY + (y - 32) * GS)), c) for x, y, c in glints]
    return compose_item(style, back, g, front, gl)


# ---------------------------------------------------------------------------------------------------------- utility items
UTIL = K.Style("Utility", "#aeb4c2", M.STEEL, field_c="#2c3344", field_e="#0d1018", outline="#06080e", frame=M.FRAME,
               glow_c="#d6dae2")                 # neutral steel rim (no class uses steel), slate face, gold studs
RUNE = M.ARCANE
PAGE = ramp("#5c4a3c", "#8a745e", "#b6a080", "#d8c6a0", "#eee2c2", "#faf3de")    # book pages (warm, violet-brown shadows)
COVER = ramp("#2a1422", "#481e30", "#6e2a3e", "#94384c", "#b8566a")              # book cover (wine leather)


def u_layers():
    return Layer(), Layer(), Layer()


def loadout():
    """Loadout: two curved arrows chasing each other round a violet rune stone (swap to the next saved loadout)"""
    back, g, front = u_layers()
    cx, cy = 32.0, 32.0
    glow(back, circle(cx, cy, 10), "#8250e2", 6.0, 0.8)
    # rune stone: a faceted hexagon gem with a carved rune
    hexp = [(cx + 9.0 * math.cos(math.radians(a)), cy + 9.0 * math.sin(math.radians(a))) for a in range(-90, 270, 60)]
    gem = poly(hexp)
    g.bevel(gem, RUNE, face=0.55, bevel=2.0, grad=0.3, gain=1.0)
    rune = line([(cx, cy - 5.0), (cx, cy + 5.0)], 1.3) | line([(cx - 3.5, cy - 2.5), (cx, cy), (cx + 3.5, cy - 2.5)], 1.2) \
        | line([(cx - 3.0, cy + 2.5), (cx + 3.0, cy + 2.5)], 1.1)
    g.put(rune & gem, rs(RUNE, 0.95))
    # two swap arrows on a circle round it
    R, w = 17.0, 2.0
    for a0 in (200.0, 20.0):
        pts = [(cx + R * math.cos(math.radians(a0 + t)), cy + R * math.sin(math.radians(a0 + t))) for t in range(0, 125, 5)]
        band = line(pts, w * 2)
        ah = math.radians(a0 + 125)
        hx_, hy_ = cx + R * math.cos(ah), cy + R * math.sin(ah)
        tx, ty = -math.sin(ah), math.cos(ah)                 # tangent (direction of travel)
        nx, ny = math.cos(ah), math.sin(ah)
        head = poly([(hx_ + tx * 6.0, hy_ + ty * 6.0), (hx_ + nx * 5.2 - tx * 0.5, hy_ + ny * 5.2 - ty * 0.5),
                     (hx_ - nx * 5.2 - tx * 0.5, hy_ - ny * 5.2 - ty * 0.5)])
        g.bevel(band | head, M.GOLD, face=0.66, bevel=1.0, grad=0.3, gain=0.9)
    glints = [(28, 25, "#f1e8ff")]
    return back, g, front, glints


def hints():
    """Hints: an open book (wine leather cover, warm pages with text lines) with a glowing gold question mark rising off it"""
    back, g, front = u_layers()
    glow(back, circle(32, 20, 9), "#ecc458", 6.0, 0.9)
    # book, seen from the front, slightly from above
    cover = poly([(9.0, 40.0), (32.0, 44.5), (55.0, 40.0), (55.0, 47.5), (32.0, 52.0), (9.0, 47.5)])
    g.bevel(cover, COVER, face=0.5, bevel=1.0, grad=0.3, gain=0.9)
    for s_ in (-1, 1):
        pg = poly([(32.0, 47.0), (32.0 + s_ * 21.0, 42.5), (32.0 + s_ * 21.0, 33.5), (32.0 + s_ * 2.0, 36.5), (32.0, 38.5)])
        g.bevel(pg, PAGE, face=0.8 if s_ < 0 else 0.68, bevel=0.8, grad=0.3, gain=0.6)
        for k in range(3):
            y0 = 38.5 + k * 2.6
            g.put(capsule(32.0 + s_ * 4.5, y0 + 0.6, 32.0 + s_ * 17.0, y0 - 1.8, 0.45), rs(PAGE, 0.3))
    g.put(capsule(32.0, 37.5, 32.0, 47.0, 0.55), rs(PAGE, 0.15))                # spine fold
    # question mark: hook + stem + dot
    q = np.zeros(X.shape, bool)
    pts = [(26.5, 16.5), (27.5, 12.5), (31.0, 10.0), (35.5, 10.5), (38.0, 14.0), (37.0, 18.0), (33.0, 21.0), (32.0, 24.5)]
    q |= line(pts, 3.6)
    dot = circle(32.0, 30.0, 2.2)
    g.bevel(q | dot, M.GOLD, face=0.78, bevel=1.0, grad=0.3, gain=0.9)
    glints = [(28, 12, "#fff4cc")]
    return back, g, front, glints


UTILITY = [("Loadout", "Loadout", loadout, "Swap to your next saved rune loadout (utility item, no key of its own; later, once loadouts exist)"),
           ("Hints", "Hints", hints, "Replay the class tutorial hints (utility item)")]


# ---------------------------------------------------------------------------------------------------------- items list
def items():
    """(item_id, display name, class name, kind, renderer) for every hotbar item"""
    out = []
    for st, fn, disp, painter in M.ICONS:
        out.append((PREFIX + st.name + "_" + fn, disp, st.name, "mirror", fn,
                    (lambda p=painter, s=st: render_mirror(p, s))))
    for fn, disp, painter, _what in UTILITY:
        out.append((PREFIX + fn, disp, "Utility", "utility", fn,
                    (lambda p=painter: compose_item(UTIL, *p()[:3], glints=p()[3], stud=M.GOLD))))
    return out


def rel(item_id):
    return os.path.join(ICON_DIR, item_id + ".png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    only = set(x for x in a.only.split(",") if x)
    for item_id, disp, cls, kind, fn, rend in items():
        if only and fn not in only and item_id not in only:
            continue
        p = os.path.join(a.out, rel(item_id))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        rend().save(p, optimize=True)
        print("wrote", p)


if __name__ == "__main__":
    main()
