#!/usr/bin/env python3
"""SkyWynn Heavy Armor tier 1 - Heavy Leather, v2 detail pass (cloud draft 2026-10-06).

Original pixel art, drawn from code (no copied art, no game files).
Run:  python3 research/cloud/heavy-armor/make_heavy_v2.py
Writes the *-v2.png files next to this script. Deterministic: same code -> same bytes.
The v1 script (make_heavy.py) and its PNGs are left as they are.

Same approved design as v1 ("Both good", Skyy 2026-10-06), redrawn at 2x with the v2 painter of
research/cloud/light-armor/make_sheets_v2.py (imported, never changed):
  * 128 x 192 figure grid (v1 64 x 84): every v1 part keeps its place, v1 (x, y) -> v2 (2x, 2y + DY);
  * 7-step ramps, whole-part gradient lit top-left, 2-px bevel, 1-px dark outline;
  * boiled leather: mottled hide, pores, burnished edges, tooled border grooves, saddle stitching, scuffs;
  * padding: puffed quilted channels with stitched seams and a linen weave;
  * domed iron studs with a highlight and a cast shadow, bevelled brass buckles with prongs, belt holes.
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'light-armor'))
import make_sheets as ms  # noqa: E402  (ramp / font / colours only)
import make_sheets_v2 as v2  # noqa: E402  (painter + masks)
from PIL import Image, ImageDraw  # noqa: E402

from make_sheets_v2 import (rect, ell, poly, line, R, E, P, Y, mirror, S, MX, clip, erode, dil,  # noqa: E402
                            ring, bottom_rim, top_rim, grain, grooves, chain, Fig, rivet, buckle,
                            hsh, mix, ramp7, W, H)

SET_SCALE, SHEET_SCALE, CHEST_SCALE = 4, 3, 4
BG, BG_SHADOW, INK = v2.BG, v2.BG_SHADOW, v2.INK
SUB = (60, 64, 70, 255)

# ---------------------------------------------------------------- palettes (v1 colours -> 7 steps)
HIDE = ramp7(ms.ramp('#1f0f07', '#4a2814', '#6a3c1f', '#8a542c', '#ab7040'))      # boiled brown leather
PAD = ramp7(ms.ramp('#4a3520', '#8f7149', '#b39365', '#cfb183', '#ead4a8'))       # tan gambeson
PAD_IN = ramp7(ms.ramp('#2e2114', '#5e4830', '#77603f', '#8f7650', '#a68c63'))    # padding, far side / back
STRAP = ramp7(ms.ramp('#140a05', '#33200f', '#4a2f18', '#634024', '#7d5533'))     # dark straps + belt
STUD = ramp7(ms.ramp('#1e1f22', '#4c4f55', '#72767d', '#9da1a8', '#c9ccd1'))      # dull iron studs
BRASS = ramp7(ms.BRASS)
DUMMY = v2.DUMMY
SOLE = v2.SOLE
THREAD_HIDE = ms.hx('#b8925e')     # light saddle stitching on brown hide
THREAD_PAD = ms.hx('#6e5634')      # brown quilting thread on tan padding
THREAD_STRAP = ms.hx('#7a5c3a')    # stitching on the dark straps


# ---------------------------------------------------------------- textures
def boiled(seed=0, amt=1.35):
    """boiled hide: big soft mottling, pores, a few hard bright flecks of wax"""
    def f(x, y, L):
        L += (hsh(x // 5, y // 4, seed) - 0.5) * 0.16 * amt
        L += (hsh(x // 2, y // 2, seed + 1) - 0.5) * 0.07 * amt
        h = hsh(x, y, seed + 2)
        if h < 0.07:
            L -= 0.17 * amt
        elif h > 0.968:
            L += 0.14 * amt
        return L
    return f


def gamb(seed=0, P_=8, V=10):
    """quilted gambeson: vertical puffed channels every P_ px, shallow cross seams every V px, linen weave"""
    def f(x, y, L):
        u, v = x % P_, (y + (x // P_) * 3) % V
        if u == 0:
            return 0.62 if y % 4 == 0 else -0.05         # seam with a thread stitch every 4th px
        L += {1: 0.24, 2: 0.12, P_ - 2: -0.10, P_ - 1: -0.22}.get(u, 0)
        if v == 0:
            L -= 0.22
        elif v == 1:
            L += 0.10
        elif v == V - 1:
            L -= 0.06
        L += 0.04 if (x + y) % 2 else -0.02             # linen weave
        if hsh(x, y, seed) < 0.05:
            L -= 0.1
        return L
    return f


def lames(*rows, shadow=True):
    """overlapping hide bands (v1 rows): shadow above the seam, dark seam, lit top edge of the band below"""
    ys = {Y(r) for r in rows}

    def f(x, y, L):
        if y in ys:
            return -1
        if y - 1 in ys:
            return L + 0.26
        if y - 2 in ys:
            return L + 0.10
        if shadow and y + 1 in ys:
            return L - 0.14
        return L
    return f


def rolls(P_=6):
    """rolled padding (gorget / boot cuff): vertical rolls"""
    def f(x, y, L):
        u = x % P_
        if u == 0:
            return 0.0
        return L + {1: 0.22, 2: 0.10, P_ - 1: -0.18}.get(u, 0) + (0.03 if (x + y) % 2 else 0)
    return f


# ---------------------------------------------------------------- details
STUD_ROWS = [".00.",
             "0650",
             "0431",
             ".00."]


def shade(f, x, y, t=0.45):
    if 0 <= x < W and 0 <= y < H:
        c = f.px[x, y]
        if c[3]:
            f.px[x, y] = mix(c, (10, 5, 2), t)


def stud(f, x, y, side=0, rp=STUD):
    """domed stud at v1 (x, y) (a v1 2x2 stud), mirrored for side 1; highlight + cast shadow"""
    x0 = 2 * x if side == 0 else W - 1 - (2 * x + 3)
    y0 = Y(y)
    for q in ((x0 + 4, y0 + 1), (x0 + 4, y0 + 2), (x0 + 1, y0 + 4), (x0 + 2, y0 + 4), (x0 + 3, y0 + 3)):
        shade(f, *q)
    f.stamp(x0, y0, STUD_ROWS, rp)


def tooled(f, m, rp, d=3):
    """a pressed groove d px inside the edge, lit on its lower / right lip (boiled-leather tooling)"""
    g = ring(m, d)
    inner = erode(m, d + 1)
    for (x, y) in g:
        f.put(x, y, rp[1])
    for (x, y) in inner:
        if (x, y - 1) in g or (x - 1, y) in g:
            f.put(x, y, rp[5])


def plate(f, m, rp=None, seed=0, tool=True, stitch=True, scuff=3, tex=None, **kw):
    """one boiled-leather plate: mottled hide, tooled groove, saddle stitches, scuffs"""
    rp = rp or HIDE
    f.paint(m, rp, tex=chain(boiled(seed), tex), **kw)
    if tool and len(erode(m, 5)) > 12:
        tooled(f, m, rp, 3)
    if stitch:
        f.stitch(m, THREAD_HIDE, d=2 if not tool else 5, per=4, on=2)
    if scuff:
        f.scuffs(m, scuff, seed, rp[5])


def lame_stitch(f, m, rows, col=THREAD_HIDE):
    ys = {Y(r) + 3 for r in rows}
    for (x, y) in erode(m, 2):
        if y in ys and x % 4 in (0, 1):
            f.put(x, y, col)


def strap(f, m, seed=0, holes=(), **kw):
    f.paint(m, STRAP, tex=chain(grain(seed, 0.09), kw.pop('tex', None)), base=kw.pop('base', 0.45), **kw)
    f.stitch(m, THREAD_STRAP, d=1, per=3, on=1)
    for (x, y) in holes:
        f.put(x, y, STRAP[0])
        f.put(x + 1, y, STRAP[1])


# ---------------------------------------------------------------- the figure
def draw_heavy(back=False, bust=False):
    f = Fig()
    sides = (0, 1)
    PADX = PAD_IN if back else PAD

    # --- mannequin (neutral faceless figure, same as the Light v2 sheets)
    if not bust:
        for side in sides:
            f.paint(S(R(21, 48, 31, 81), side), DUMMY, kind='dummy')
    for side in sides:
        f.paint(S(R(13, 22, 19, 58), side), DUMMY, kind='dummy')
    f.paint(R(27, 14, 36, 22), DUMMY, kind='dummy')
    if not bust:
        f.paint(v2.HEAD, DUMMY, kind='dummy', grad=0.35)

    # --- legs: padded trousers, big knee cops, studded greaves, heavy boots
    if not bust:
        for side in sides:
            leg = S(R(20, 48, 31, 74), side)
            f.paint(leg, PADX, tex=gamb(4 + side), grad=0.3)
            gr = S(P([(20, 64), (31, 64), (31, 76), (21, 76)]), side)
            plate(f, gr, seed=20 + side, tex=lames(69), tool=False, stitch=False, scuff=2)
            f.stitch(gr, THREAD_HIDE, d=2, per=4, on=2, ys=(Y(64), Y(68)))
            lame_stitch(f, gr, (69,))
            if not back:
                for sx, sy in ((22, 66), (22, 72), (29, 66), (29, 72)):
                    stud(f, sx, sy, side)
            km = S(E(19, 56, 32, 67), side)
            plate(f, km, seed=30 + side, tex=lames(61), tool=False, stitch=False, scuff=2, grad=0.36)
            f.stitch(km, THREAD_HIDE, d=2, per=4, on=2)
            boss = S(E(23, 58, 28, 63), side)
            plate(f, boss, seed=35 + side, tool=False, stitch=False, scuff=0, grad=0.5)   # raised knee boss
            if not back:
                stud(f, 25, 60, side)
            bm = S(R(19, 75, 32, 82) | R(18, 78, 32, 82), side)
            f.paint(bm, STRAP, tex=chain(grain(40 + side, 0.1), grooves(Y(80))), base=0.5, grad=0.35)
            f.stitch(bm, THREAD_STRAP, d=2, per=3, on=1, ys=(Y(75), Y(79)))
            sole = S(R(18, 82, 32, 82), side)
            f.paint(sole, SOLE, tex=lambda x, y, L: L - 0.35 if x % 3 == 0 else L)        # hobnailed sole
            toe = S(R(18, 79, 22, 81), side)
            plate(f, toe, seed=44 + side, tool=False, stitch=False, scuff=0, edge_ref=bm)  # toe cap
            cuff = S(R(19, 74, 32, 76), side)
            f.paint(cuff, PADX, tex=rolls(5), grad=0.35)                                   # boot cuff roll
            st = S(R(20, 78, 31, 79), side)
            plate(f, st, seed=46 + side, tool=False, stitch=False, scuff=0, outline=False)
            if not back:
                bx = 2 * 24 if side == 0 else W - 1 - (2 * 24 + 9)
                buckle(f, bx, Y(77) - 2, BRASS, w=10, h=10)
            f.scuffs(bm, 3, 48 + side, STRAP[5])

    # --- tassets: three big studded flaps over the hips (front), two on the back
    if not bust:
        skirt = R(18, 46, 45, 62)
        f.paint(skirt, PADX, tex=gamb(7), grad=0.3)                                    # padded skirt
        flaps = [(18, 26, 56), (27, 36, 58), (37, 45, 56)] if not back else [(18, 31, 57), (32, 45, 57)]
        for k, (x0, x1, y1) in enumerate(flaps):
            tm = R(x0, 46, x1, y1) | R(x0 + 1, y1 + 1, x1 - 1, y1 + 1)
            plate(f, tm, seed=50 + k, tex=lames(52), scuff=3, grad=0.3)
            lame_stitch(f, tm, (52,))
            f.paint(bottom_rim(tm, 4) - bottom_rim(tm, 1), PAD, outline=False, tex=rolls(4), kind='trim')
            if not back:
                stud(f, x0 + 2, y1 - 3)
                stud(f, x1 - 3, y1 - 3)

    # --- arms: padded sleeve, thick studded bracer, full leather gauntlet
    for side in sides:
        sl = S(R(12, 32, 20, 43), side)
        f.paint(sl, PADX, tex=gamb(9 + side, 6, 8), grad=0.3)
        br = S(P([(11, 44), (21, 44), (21, 53), (11, 53)]), side)
        plate(f, br, seed=60 + side, tex=lames(48), tool=False, stitch=False, scuff=2)
        lame_stitch(f, br, (48,))
        bs = S(R(11, 44, 21, 45), side)
        strap(f, bs, 62 + side, outline=False)                                            # bracer strap
        if not back:
            stud(f, 13, 50, side)
            stud(f, 18, 50, side)
        else:   # lacing on the back of the bracer
            for y in range(Y(46) + 1, Y(53), 3):
                f.put(MX(30, side), y, PAD[5])
                f.put(MX(31, side), y + 1, PAD[3])
                f.put(MX(32, side), y, PAD[5])
        gl = S(R(12, 53, 20, 59) | R(11, 54, 21, 58), side)
        f.paint(gl, STRAP, tex=chain(grain(64 + side, 0.1), grooves(Y(56))), base=0.5, grad=0.35)
        for k in range(3):                                                                 # finger lines + knuckle pads
            fx = MX(2 * (14 + 2 * k), side)
            for y in range(Y(57), Y(59) + 1):
                f.put(fx + (1 if side else 0), y, STRAP[0])
            q = MX(2 * (14 + 2 * k) - 2, side)
            f.put(q, Y(55), STRAP[6])
            f.put(q + 1, Y(55), STRAP[5])
            f.put(q, Y(55) + 1, STRAP[4])
        f.stitch(gl, THREAD_STRAP, d=1, per=4, on=1, ys=(Y(53), Y(54)))

    # --- torso: tan gambeson under a thick boiled-leather cuirass
    torso = R(18, 20, 45, 48)
    f.paint(torso, PADX, tex=gamb(11), grad=0.25)
    cu = P([(20, 21), (43, 21), (44, 30), (42, 41), (21, 41), (19, 30)])
    if not back:
        plate(f, cu, seed=70, scuff=0, grad=0.3)
        for side in sides:
            pl = S(P([(21, 23), (30, 23), (30, 31), (22, 32)]), side)
            plate(f, pl, seed=72 + side, edge_ref=pl, scuff=3, grad=0.4)
            for sx, sy in ((22, 24), (28, 24), (23, 29), (28, 29)):
                stud(f, sx, sy, side)
        # centre ridge: lit left half, shaded right half
        for y in range(Y(23), Y(39) + 2):
            f.put(62, y, HIDE[6])
            f.put(63, y, HIDE[5])
            f.put(64, y, HIDE[1])
            f.put(65, y, HIDE[0] if y % 5 else HIDE[1])
        ab = R(21, 33, 42, 41)
        plate(f, ab, seed=75, tex=lames(35, 38), tool=False, stitch=False, scuff=4, grad=0.25)
        lame_stitch(f, ab, (35, 38))
        for sx in (22, 27, 35, 40):
            stud(f, sx, 33)
        for sx in (22, 40):
            stud(f, sx, 39)
        for side in sides:     # dark shoulder straps holding the cuirass, with holes
            sm = S(R(22, 19, 24, 41), side)
            strap(f, sm, 77 + side, tex=grooves(Y(26), Y(34)),
                  holes=[(MX(46, side) - (1 if side else 0), y) for y in (Y(29), Y(31), Y(37) - 4)])
            stud(f, 22, 37, side, BRASS)
    else:
        plate(f, cu, seed=80, tex=lames(28, 32, 36), tool=False, stitch=False, scuff=5, grad=0.3)
        lame_stitch(f, cu, (28, 32, 36))
        f.stitch(cu, THREAD_HIDE, d=2, per=4, on=2, ys=(Y(21), Y(27)))
        xs = P([(20, 22), (23, 22), (43, 39), (40, 40)])
        for k, m in enumerate((xs, mirror(xs))):                                          # crossed back straps
            strap(f, m, 82 + k)
        hub = E(28, 27, 35, 34)
        f.paint(hub, STRAP, tex=grain(84, 0.08), grad=0.45, base=0.55)
        f.stitch(hub, THREAD_STRAP, d=2, per=2, on=1)
        rivet(f, 63, Y(30) + 1, BRASS)

    # --- thick double belt with a big brass buckle
    belt = R(17, 41, 46, 47)
    f.paint(belt, STRAP, tex=chain(grain(90, 0.1), grooves(Y(44))), base=0.5, grad=0.3)
    f.stitch(belt, THREAD_STRAP, d=1, per=3, on=1)
    for y in (Y(44) + 2,):
        for x in range(2 * 17 + 3, 2 * 46 - 2, 3):
            f.put(x, y, THREAD_STRAP)
    if not back:
        for x in range(2 * 38 + 6, 2 * 44, 5):                                           # belt holes
            f.put(x, Y(42) + 2, STRAP[0])
            f.put(x, Y(42) + 3, STRAP[0])
            f.put(x + 1, Y(42) + 3, STRAP[2])
        buckle(f, 56, Y(41) - 1, BRASS, w=16, h=16)
        f.paint(rect(60, Y(41) + 3, 67, Y(41) + 10), STRAP, outline=False, base=0.3, grad=0.1)  # strap through
        buckle(f, 56, Y(41) - 1, BRASS, w=16, h=16)
        for sx in (20, 24, 38, 42):
            stud(f, sx, 42, 0, BRASS)
        pouch = R(40, 46, 46, 54)
        plate(f, pouch, seed=92, tool=False, scuff=2, grad=0.35)
        flap = R(40, 46, 46, 49) | rect(2 * 41, Y(50), 2 * 46, Y(50) + 1)
        plate(f, flap, seed=93, tool=False, stitch=False, scuff=0, base=0.38, edge_ref=pouch | flap)
        f.stitch(flap, THREAD_HIDE, d=1, per=4, on=2)
        stud(f, 42, 48, 0, BRASS)
    else:
        for sx in (20, 26, 31, 36, 42):
            stud(f, sx, 42, 0, BRASS)

    # --- padded collar roll (gorget)
    gor = E(19, 15, 44, 28) & R(0, 17, 63, 25)
    f.paint(gor, PADX, tex=rolls(6), grad=0.35)
    f.stitch(gor, THREAD_PAD, d=1, per=3, on=1, ys=(Y(17), Y(18)))
    if not back:
        cs = R(25, 18, 38, 20)
        strap(f, cs, 95)
        rivet(f, 52, Y(19) + 1, STUD, small=True)
        rivet(f, 74, Y(19) + 1, STUD, small=True)
    else:
        f.paint(R(25, 17, 38, 19), PAD_IN, tex=rolls(4), grad=0.3)

    # --- big layered pauldrons (lowest plate first, top cap last), studded rims
    p3 = clip(E(9, 26, 21, 41), y0=Y(33))
    p2 = clip(E(8, 21, 22, 36), y0=Y(27))
    p1 = E(6, 15, 23, 29)
    for side in sides:
        for k, pm in ((3, p3), (2, p2), (1, p1)):
            pm = S(pm, side)
            plate(f, pm, seed=100 + 3 * side + k, tool=(k == 1), stitch=False, scuff=2 + (k == 1) * 2,
                  grad=0.4, base=0.5 - 0.04 * (k - 1))
            f.paint(bottom_rim(pm, 4) - bottom_rim(pm, 1), PAD, outline=False, tex=rolls(4), kind='trim')
            f.stitch(pm, THREAD_HIDE, d=5 if k == 1 else 3, per=4, on=2,
                     ys=(min(y for _, y in pm) + 3, max(y for _, y in pm) - 5))
        if not back:
            for x in (9, 13, 17):
                stud(f, x, 25, side)
            for x in (11, 16):
                stud(f, x, 32, side)
        else:
            for x in (10, 15, 20):
                stud(f, x, 25, side)
        tab = S(R(14, 16, 19, 18), side)
        strap(f, tab, 110 + side)                                                         # shoulder strap tab
        rivet(f, MX(2 * 16 + 1, side) - (1 if side else 0), Y(17) + 1, STUD, small=True)

    # --- helm: padded leather cap, studded brow band, cheek guards, nose guard
    if not bust:
        cap = dil(v2.HEAD, 2) & rect(0, 0, W - 1, Y(9) + 1)
        seams = {55, 63, 73} if not back else {54, 63, 72}

        def capt(x, y, L):
            if x in seams:
                return -1
            if x - 1 in seams:
                return L + 0.22
            return L
        plate(f, cap, seed=120, tex=capt, tool=False, stitch=False, scuff=3, grad=0.4)
        for sx in seams:                                                                  # panel stitches
            for y in range(Y(0) + 2, Y(7), 3):
                f.put(sx - 2, y, THREAD_HIDE)
                f.put(sx + 2, y + 1, THREAD_HIDE)
        rivet(f, 63, Y(0) - 1, STUD)                                                       # top knob
        brow = R(21, 7, 42, 10)
        f.paint(brow, PADX, tex=rolls(5) if back else gamb(122, 6, 99), grad=0.4)
        f.stitch(brow, THREAD_PAD, d=1, per=3, on=1)
        if back:
            ng = R(22, 10, 41, 15)
            plate(f, ng, seed=124, tex=lames(13), tool=False, stitch=False, scuff=2)        # neck guard
            lame_stitch(f, ng, (13,))
        else:
            for side in sides:
                ck = S(P([(21, 10), (25, 10), (25, 17), (22, 18)]), side)
                plate(f, ck, seed=126 + side, tool=False, scuff=1, grad=0.4)              # cheek guards
                stud(f, 23, 13, side)
            nose = rect(62, Y(10), 65, Y(14) + 1) | rect(61, Y(14), 66, Y(14) + 3)
            plate(f, nose, seed=128, tool=False, stitch=False, scuff=0, grad=0.6)        # nose guard
            for y in range(Y(10) + 1, Y(14) + 2):
                f.put(62, y, HIDE[6])
            for sx in (23, 27, 35, 39):
                stud(f, sx, 8)
    return f


# ---------------------------------------------------------------- output
font = ms.font


def scaled(f, s):
    return v2.scaled(f, s)


def save(im, name):
    im = im.convert('RGB').quantize(colors=160, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    p = os.path.join(HERE, name)
    im.save(p, optimize=True)
    return os.path.getsize(p)


def label(im, text, sub, n=24):
    return v2.label(im, text, sub, n)


def closeup(f, box, s=CHEST_SCALE):
    crop = f.im.crop(box)
    ch = crop.resize((crop.width * s, crop.height * s), Image.NEAREST)
    base = Image.new('RGBA', ch.size, BG)
    base.alpha_composite(ch)
    return base


def main():
    sizes = {}
    fr, bk, bu = draw_heavy(), draw_heavy(back=True), draw_heavy(bust=True)
    a, b = scaled(fr, SET_SCALE), scaled(bk, SET_SCALE)
    pair = Image.new('RGBA', (a.width * 2 + 16, a.height), BG)
    pair.paste(a, (0, 0))
    pair.paste(b, (a.width + 16, 0))
    d = ImageDraw.Draw(pair)
    d.text((10, 8), 'front', font=font(16), fill=INK)
    d.text((a.width + 26, 8), 'back', font=font(16), fill=INK)
    sizes['heavy-leather-set-v2.png'] = save(label(pair, 'Heavy Leather Armor (Heavy tier 1, v2)',
                                                   'Lv 1-13  |  2x detail  |  concept, cloud draft'),
                                             'heavy-leather-set-v2.png')
    ch = closeup(bu, (4, Y(9), 124, Y(62)))
    sizes['heavy-leather-chest-v2.png'] = save(label(ch, 'Heavy Leather Cuirass (v2)', 'Lv 1-13  |  front close-up'),
                                               'heavy-leather-chest-v2.png')

    # overview sheet: Light Copper v2 (bulk comparison) | Heavy front | Heavy back | cuirass close-up
    a3, b3 = scaled(fr, SHEET_SCALE), scaled(bk, SHEET_SCALE)
    light = scaled(v2.draw_figure(1), SHEET_SCALE)
    chs = closeup(bu, (4, Y(9), 124, Y(62)), 5)
    gap, top, labh = 20, 96, 56
    cells = [(light, 'Light Copper v2 (for scale)', 'Lv 10-18  |  existing design'),
             (a3, 'Heavy Leather - front', 'Lv 1-13  |  Heavy tier 1'),
             (b3, 'Heavy Leather - back', ''),
             (chs, 'Cuirass close-up', 'front, 5x')]
    sw = sum(c[0].width for c in cells) + gap * (len(cells) + 1)
    sheet = Image.new('RGBA', (sw, top + a3.height + labh + 60), BG)
    d = ImageDraw.Draw(sheet)
    d.text((sw // 2, 16), 'SkyWynn Heavy Armor tier 1 - Heavy Leather v2 (cloud draft)', font=font(40), fill=INK, anchor='mt')
    d.text((sw // 2, 62), '2x detail (128 x 192 figure grid, v1 was 64 x 84)  |  same approved design  |  boiled hide, '
           'quilted gambeson, domed iron studs, brass buckles', font=font(18), fill=SUB, anchor='mt')
    x = gap
    for im, t1, t2 in cells:
        sheet.paste(im, (x, top + (a3.height - im.height) // 2))
        d.text((x + im.width // 2, top + a3.height + 6), t1, font=font(24), fill=INK, anchor='mt')
        d.text((x + im.width // 2, top + a3.height + 34), t2, font=font(15), fill=SUB, anchor='mt')
        x += im.width + gap
    y = top + a3.height + labh + 22
    x = gap
    for nm, rp in (('hide', HIDE), ('padding', PAD), ('straps', STRAP), ('studs', STUD), ('buckles', BRASS)):
        for j, col in enumerate(rp[1:]):
            d.rectangle((x + j * 16, y, x + 12 + j * 16, y + 12), fill=col, outline=rp[0])
        d.text((x + 104, y - 2), nm, font=font(15), fill=INK)
        x += 200
    sizes['heavy-armor-sheet-v2.png'] = save(sheet, 'heavy-armor-sheet-v2.png')

    k = list(fr.kind.values())
    print('armor px (front):', len(k) - k.count('dummy'))
    for n, s in sizes.items():
        print(f'{n:30s} {s // 1024:5d} KB')


if __name__ == '__main__':
    main()
