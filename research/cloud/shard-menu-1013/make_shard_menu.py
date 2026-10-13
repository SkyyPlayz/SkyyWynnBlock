#!/usr/bin/env python3
"""SkyWynn SHARD MENU mockups (cloud draft 2026-10-13, paper only - nothing built).

One page, four tabs. It opens from the shard portal on your main island (right-click, like a vanilla portal's menu) and from the
menu stand on the shard's hub island (research/Shard-Islands-Ideas.md, docs/answered/skills.md lines 108-113).

Draws, next to this script (research/cloud/shard-menu-1013/):
  shard_0_layout.png            the page shell + every tab's regions as a wireframe with pixel boxes (LAYOUT FIRST)
  shard_a_collect_1080p.png     Collect tab   (stored output, per-row Collect, Collect all, capacity bar)
  shard_b_upgrades_1080p.png    Upgrades tab  (Storage / Auto-Compactor / Time Compressor; affordable / missing / requirement)
  shard_c_islands_1080p.png     Islands tab   (8 fixed slots around the hub as a map; filled / empty / locked; side panel)
  shard_d_totems_1080p.png      Totems tab    (placed totems + free places; selected totem: slots, fuel, pick up)
  shard_e_states.png            states: tabs, header (portal / hub / full), buttons, slots, side-panel variants, chips, empty tabs
  shard_f_check_1366x768.png    the 1366 x 768 fit check (A scaled to the screen height, B unscaled)

Style: the SKY WINDOW kit (art/ui-kit-sky/Common/UI/Custom/SkyyKit/*.png, our own art), 9-sliced like the client does it
(@2x texture, Border in UI units, 1 UI = 1 px at 1080p). The kit helpers, the fonts (Liberation Sans standing in for Nunito Sans /
Lexend) and the placeholder world are REUSED from research/cloud/ui-mockups-1013/make_mockups.py so both sets match.
Shard icon: research/cloud/icons-1013/icons/Skyy_Shard_Portal_Farming.png (our own draft icon). Every other picture here (crops,
totems, upgrade symbols, the island map) is a simple placeholder drawing made by this script - not item art, not vanilla art.

Layout checks (run every time): every registered box must sit inside its parent with no overlap with its siblings, and no two
text boxes may overlap; text given a max width must fit it. The run prints "layout: OK" or the list of problems.

Deterministic: no clock, only seeded randomness; two runs give the same bytes.
Run: python3 research/cloud/shard-menu-1013/make_shard_menu.py
"""
import importlib.util
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
_spec = importlib.util.spec_from_file_location(
    "skyy_mockkit", os.path.join(REPO, "research", "cloud", "ui-mockups-1013", "make_mockups.py"))
MK = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(MK)
ICONS = os.path.join(REPO, "research", "cloud", "icons-1013", "icons")

C = MK.C
col, nine, scaled, fade, font, tw, fit = MK.col, MK.nine, MK.scaled, MK.fade, MK.font, MK.tw, MK.fit
SW, SH = 1920, 1080
PW, PH = 1100, 860                      # page size (fits the verified 1120 x 952 page area)
PX, PY = (SW - PW) // 2, (SH - PH) // 2  # centred: 410, 110

# ------------------------------------------------------------------ the shell grid (page coordinates) - see Shard-Menu-Spec.md section 2
M = 24                       # content padding inside the Frame (kit README: 24 keeps the corner windows clear)
HDR = (24, 18, 1052, 38)     # Header bar
STRIP = (24, 66, 1052, 76)   # shard summary strip (Panel)
TABY, TABH, TABG = 152, 44, 4
TABW = (1052 - 3 * TABG) // 4          # 260
CT, CB = 206, 770            # content top / bottom (564 high)
LP = (24, CT, 700, CB - CT)  # left panel
RP = (736, CT, 340, CB - CT) # right panel
STATUS_Y = 785               # status line centre
LINE_Y = 800                 # gold line
FOOT = 808                   # footer buttons top (36 high)
TABS = ["Collect", "Upgrades", "Islands", "Totems"]

# ------------------------------------------------------------------ sample data (all PLACEHOLDER numbers - Questions for Skyy)
FARMING_LVL = 12
COINS = 48200
TIME_MULT = {0: 1.00, 1: 1.10, 2: 1.25, 3: 1.50, 4: 1.75, 5: 2.00}
BASE_RATE = 330              # items / hour at x1.00 with this shard's islands + totems
RATE = int(BASE_RATE * TIME_MULT[2])          # 412
RATE_NEXT = int(BASE_RATE * TIME_MULT[3])     # 495
STORAGE_CAP = {1: 1000, 2: 2500, 3: 5000, 4: 10000, 5: 20000, 6: 40000, 7: 80000, 8: 160000}
# stored output: (icon, name, source line, count, xp each, collection key, collection count each)
STORED = [
    ("wheat", "Wheat", "Wheat Island (Large)", 1720, 0.4, "Wheat", 1),
    ("ench_wheat", "Enchanted Wheat", "Auto-Compactor (100 Wheat each)", 18, 40.0, "Wheat", 100),
    ("lettuce", "Lettuce", "Lettuce Island (Medium)", 636, 0.5, "Lettuce", 1),
    ("ench_lettuce", "Enchanted Lettuce", "Auto-Compactor (100 Lettuce each)", 4, 50.0, "Lettuce", 100),
    ("seeds", "Wheat Seeds", "Wheat Island (Large)", 410, 0.1, None, 0),
    ("carrot", "Carrot", "Carrot Island (Small)", 352, 0.6, "Carrot", 1),
]
STORED_TOTAL = sum(s[3] for s in STORED)      # 3,140
XP_TOTAL = sum(s[3] * s[4] for s in STORED)
COLL = {"Wheat": ("VI", 18240, 25000), "Lettuce": ("IV", 3800, 5000), "Carrot": ("II", 760, 1500)}
CROP_COL = {"wheat": "#e2b532", "lettuce": "#6cc04a", "carrot": "#ee8a2a", "corn": "#f2d040", "cauliflower": "#e9e4d0",
            "turnip": "#c86aa8", "pumpkin": "#e8862a", "aubergine": "#7a4aa8", "tomato": "#e04838", "chilli": "#d02828",
            "cotton": "#f0f0f0", "rice": "#d8d0a0", "potato": "#c09858", "onion": "#e0c890", "ench_wheat": "#f7e9a8",
            "seeds": "#a87a3a", "ench_lettuce": "#9be070"}

# ------------------------------------------------------------------ layout registry + checks
REG = []        # (name, box, parent)          solid boxes
TXT = []        # (name, bbox)                 text boxes (page coords)
PROBLEMS = []


def reg(name, box, parent=None):
    REG.append((name, tuple(int(v) for v in box), parent))
    return box


def inside(a, b, pad=0):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax >= bx + pad and ay >= by + pad and ax + aw <= bx + bw - pad and ay + ah <= by + bh - pad


def ovl(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


def check(page):
    boxes = {n: b for n, b, p in REG}
    for n, b, p in REG:
        if p and p in boxes and not inside(b, boxes[p]):
            PROBLEMS.append("%s: %s outside parent %s %s" % (page, n, p, boxes[p]))
    for i in range(len(REG)):
        for j in range(i + 1, len(REG)):
            n1, b1, p1 = REG[i]
            n2, b2, p2 = REG[j]
            if p1 == p2 and ovl(b1, b2):
                PROBLEMS.append("%s: %s overlaps %s" % (page, n1, n2))
    for i in range(len(TXT)):
        for j in range(i + 1, len(TXT)):
            if ovl(TXT[i][1], TXT[j][1]):
                PROBLEMS.append("%s: text '%s' overlaps text '%s'" % (page, TXT[i][0], TXT[j][0]))
    REG.clear()
    TXT.clear()


def T(img, xy, s, size, color, bold=False, anchor="la", maxw=None, within=None, alpha=1.0, track=True):
    """Text with checks: maxw = must fit; within = (x, y, w, h) it must stay inside. Registered for the overlap check."""
    if maxw is not None and tw(s, size, bold) > maxw:
        PROBLEMS.append("text too wide (%d > %d): %s" % (tw(s, size, bold), maxw, s))
    MK.text(img, xy, s, size, color, bold, anchor, alpha)
    l, t, r, b = ImageDraw.Draw(img).textbbox(xy, s, font=font(size, bold), anchor=anchor)
    bb = (l, t, r - l, b - t)
    if within is not None and not inside(bb, within):
        PROBLEMS.append("text '%s' %s leaves its box %s" % (s, bb, within))
    if track:
        TXT.append((s, bb))
    return bb


def R(img, box, fill, outline=None, width=1):
    MK.rect(img, box, fill, outline, width)


def put(P, im, x, y, name=None, parent=None):
    P.alpha_composite(im, (int(x), int(y)))
    if name:
        reg(name, (x, y, im.width, im.height), parent)


def button(kind, w, h, label, size=15, state="", label_color=None):
    b = MK.button(kind, w, h, label, size, state) if label_color is None else MK.button(kind, w, h, "", size, state)
    if label_color is not None:
        MK.text(b, (w // 2, h // 2), label, size, label_color, True, "mm")
    if tw(label, size, True) > w - 16:
        PROBLEMS.append("button label too wide: %s" % label)
    return b


def gold_line(P, x, y, w, a=0.35):
    R(P, (x, y, w, 1), "#E8A93B(%s)" % a)


def bar(P, x, y, w, h, frac, fill, back="#000000(0.55)", add=None, add_fill="#39f493"):
    """Progress bar: frac filled; add = an extra part (what you are about to gain), drawn brighter after the fill."""
    R(P, (x, y, w, h), back)
    fw = int(round(w * max(0.0, min(1.0, frac))))
    if fw > 0:
        R(P, (x, y, fw, h), fill)
    if add:
        aw = int(round(w * max(0.0, min(1.0, frac + add)))) - fw
        if aw > 0:
            R(P, (x + fw, y, aw, h), add_fill)
    R(P, (x, y, w, 1), "#ffffff(0.10)")
    R(P, (x, y, w, h), None, "#E8A93B(0.30)")


def chip(P, x, y, s, color, anchor_right=False, size=12):
    w = int(tw(s, size, True)) + 16
    h = 20
    if anchor_right:
        x = x - w
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 10, fill=col(color, 0.18), outline=col(color, 0.75))
    MK.text(lay, (w // 2, h // 2), s, size, color, True, "mm")
    P.alpha_composite(lay, (int(x), int(y)))
    TXT.append((s, (int(x), int(y), w, h)))
    return w


def pips(P, x, y, n, filled, w=22, h=8, gap=4, nxt=False):
    for i in range(n):
        bx = x + i * (w + gap)
        if i < filled:
            R(P, (bx, y, w, h), C["gold"])
            R(P, (bx, y, w, 2), "#fff2c8(0.6)")
        elif nxt and i == filled:
            R(P, (bx, y, w, h), "#39f493(0.25)", "#39f493(0.9)")
        else:
            R(P, (bx, y, w, h), "#000000(0.55)", "#E8A93B(0.35)")
    return n * (w + gap) - gap


def slot(size, icon_name=None, dim=False):
    s = scaled("SlotEmpty", size, size)
    if icon_name:
        ic = item_icon(icon_name, int(size * 0.62))
        s.alpha_composite(ic, ((size - ic.width) // 2, (size - ic.height) // 2))
    return fade(s, 0.45) if dim else s


# ------------------------------------------------------------------ placeholder icons (drawn at 64, scaled down)
def _poly(d, pts, fill, outline=None):
    d.polygon(pts, fill=col(fill), outline=col(outline) if outline else None)


def _icon64(kind):
    L = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    O = "#1c1430"
    if kind in ("wheat", "ench_wheat"):
        for dx, lean in ((-9, -6), (0, 0), (9, 6)):
            d.line((32 + dx * 0.4, 60, 32 + dx + lean, 18), fill=col("#9a7a2a"), width=3)
            for k in range(5):
                gy = 20 + k * 6
                gx = 32 + dx + lean * (1 - k / 6.0)
                d.ellipse((gx - 6, gy - 3, gx - 1, gy + 4), fill=col("#e2b532"), outline=col("#8a6418"))
                d.ellipse((gx + 1, gy - 3, gx + 6, gy + 4), fill=col("#f0c84a"), outline=col("#8a6418"))
            d.ellipse((32 + dx + lean - 3, 10, 32 + dx + lean + 3, 19), fill=col("#f4d86a"), outline=col("#8a6418"))
        d.rectangle((24, 46, 40, 50), fill=col("#c0392b"))
    elif kind in ("lettuce", "ench_lettuce"):
        for r, c in ((26, "#3f8a2e"), (21, "#5aa83a"), (15, "#7cc850"), (8, "#a8e070")):
            d.ellipse((32 - r, 36 - r * 0.85, 32 + r, 36 + r * 0.85), fill=col(c), outline=col("#2a5a1e"))
        d.line((32, 20, 32, 50), fill=col("#d8f0b0"), width=2)
    elif kind == "carrot":
        _poly(d, [(18, 22), (46, 22), (34, 60), (30, 60)], "#ee8a2a", "#8a4210")
        for yy in (30, 38, 46):
            d.line((24 + (yy - 22) * 0.35, yy, 32, yy + 2), fill=col("#b85a14"), width=2)
        for a in (-30, 0, 30):
            ang = math.radians(a - 90)
            d.line((32, 22, 32 + 16 * math.cos(ang), 22 + 16 * math.sin(ang)), fill=col("#4a9a2e"), width=5)
    elif kind == "corn":
        d.ellipse((20, 8, 44, 56), fill=col("#f2d040"), outline=col("#8a6a10"))
        for yy in range(14, 52, 6):
            d.line((22, yy, 42, yy), fill=col("#c8a020"))
        _poly(d, [(16, 60), (22, 26), (32, 58)], "#5aa83a", "#2a5a1e")
        _poly(d, [(48, 60), (42, 26), (32, 58)], "#4a9a2e", "#2a5a1e")
    elif kind == "seeds":
        for (x, y, a) in ((22, 34, -30), (36, 26, 20), (38, 44, 60), (24, 48, 10)):
            seed = Image.new("RGBA", (24, 16), (0, 0, 0, 0))
            ImageDraw.Draw(seed).ellipse((1, 1, 22, 14), fill=col("#c89a52"), outline=col("#6a4a1a"))
            ImageDraw.Draw(seed).line((6, 5, 14, 5), fill=col("#f0d090"), width=2)
            seed = seed.rotate(a, expand=True, resample=Image.BICUBIC)
            L.alpha_composite(seed, (int(x - seed.width / 2), int(y - seed.height / 2)))
    elif kind == "eternal":
        d.ellipse((6, 6, 58, 58), fill=col("#39f493", 0.16))
        d.ellipse((18, 14, 46, 52), fill=col("#7ae06a"), outline=col("#1e6a2a"))
        d.ellipse((24, 20, 34, 32), fill=col("#d8ffb8"))
        d.line((32, 14, 32, 6), fill=col("#2e8a3a"), width=3)
        _poly(d, [(32, 8), (44, 2), (42, 12)], "#4ac85a", "#1e6a2a")
        for sx, sy in ((10, 18), (52, 40), (14, 50)):
            _poly(d, [(sx, sy - 5), (sx + 2, sy), (sx, sy + 5), (sx - 2, sy)], "#fff6c0")
    elif kind == "coins":
        for i, (x, y) in enumerate(((14, 40), (14, 33), (14, 26), (30, 42), (30, 35))):
            d.ellipse((x, y, x + 22, y + 11), fill=col("#f2c94c"), outline=col("#8a6410"))
        d.ellipse((30, 12, 56, 38), fill=col("#f6d460"), outline=col("#8a6410"), width=2)
        d.ellipse((36, 18, 50, 32), outline=col("#a87a12"), width=2)
    elif kind == "storage":   # chest
        d.rectangle((8, 24, 56, 56), fill=col("#8a5a2e"), outline=col(O), width=2)
        d.rounded_rectangle((8, 10, 56, 28), 6, fill=col("#a06a36"), outline=col(O), width=2)
        for x in (14, 46):
            d.rectangle((x, 10, x + 4, 56), fill=col("#e8a93b"))
        d.rectangle((28, 24, 36, 34), fill=col("#f2d060"), outline=col(O))
        d.line((10, 40, 54, 40), fill=col("#6a4220"), width=2)
    elif kind == "compactor":
        d.rectangle((10, 6, 54, 18), fill=col("#8a96a8"), outline=col(O), width=2)
        d.rectangle((28, 18, 36, 28), fill=col("#5a6678"))
        d.rectangle((16, 28, 48, 34), fill=col("#aab6c8"), outline=col(O), width=2)
        d.rectangle((20, 40, 44, 58), fill=col("#e2b532"), outline=col(O), width=2)
        d.rectangle((24, 44, 40, 54), fill=col("#f4d86a"))
        for sx, sy in ((8, 46), (56, 44), (52, 58)):
            _poly(d, [(sx, sy - 5), (sx + 2, sy), (sx, sy + 5), (sx - 2, sy)], "#c99cff")
    elif kind == "time":      # hourglass
        d.rectangle((14, 6, 50, 12), fill=col("#e8a93b"), outline=col(O), width=2)
        d.rectangle((14, 52, 50, 58), fill=col("#e8a93b"), outline=col(O), width=2)
        _poly(d, [(18, 12), (46, 12), (34, 32), (46, 52), (18, 52), (30, 32)], "#bfe6ff", O)
        _poly(d, [(22, 16), (42, 16), (32, 28)], "#f2d060")
        _poly(d, [(32, 38), (44, 50), (20, 50)], "#f2d060")
        d.line((32, 30, 32, 44), fill=col("#f2d060"), width=2)
        d.arc((2, 2, 62, 62), 200, 320, fill=col("#7caacc"), width=3)
        _poly(d, [(54, 18), (60, 10), (62, 22)], "#7caacc")
    elif kind == "lock":
        d.arc((18, 6, 46, 38), 180, 360, fill=col("#b7c3cf"), width=6)
        d.line((21, 22, 21, 30), fill=col("#b7c3cf"), width=6)
        d.line((43, 22, 43, 30), fill=col("#b7c3cf"), width=6)
        d.rounded_rectangle((12, 28, 52, 58), 5, fill=col("#e8a93b"), outline=col(O), width=2)
        d.ellipse((28, 36, 36, 44), fill=col(O))
        d.rectangle((30, 42, 34, 50), fill=col(O))
    elif kind == "plus":
        d.rectangle((28, 12, 36, 52), fill=col("#E8A93B"))
        d.rectangle((12, 28, 52, 36), fill=col("#E8A93B"))
    elif kind == "xp":
        pts = []
        for k in range(10):
            r = 26 if k % 2 == 0 else 11
            a = math.pi / 5 * k - math.pi / 2
            pts.append((32 + r * math.cos(a), 33 + r * math.sin(a)))
        _poly(d, pts, "#39f493", "#126a3a")
    elif kind == "essence":
        _poly(d, [(32, 4), (48, 30), (32, 60), (16, 30)], "#e05a8a", O)
        _poly(d, [(32, 10), (40, 30), (32, 50)], "#ff9ac0")
    elif kind == "replant":
        d.arc((8, 8, 56, 56), 30, 300, fill=col("#7caacc"), width=4)
        _poly(d, [(50, 4), (60, 18), (44, 18)], "#7caacc")
        d.line((32, 50, 32, 30), fill=col("#3f8a2e"), width=4)
        _poly(d, [(32, 34), (18, 24), (22, 38)], "#6cc04a", "#2a5a1e")
        _poly(d, [(32, 30), (46, 20), (42, 34)], "#7cc850", "#2a5a1e")
        d.rectangle((24, 50, 40, 56), fill=col("#6a4a2a"))
    elif kind == "area":       # upgrade item "Wider Area"
        d.rectangle((10, 10, 54, 54), outline=col("#7caacc"), width=3)
        for (a, b, c2, e) in ((32, 32, 8, 8), (32, 32, 56, 8), (32, 32, 8, 56), (32, 32, 56, 56)):
            d.line((a, b, c2, e), fill=col("#bfe6ff"), width=3)
        d.ellipse((24, 24, 40, 40), fill=col("#e8a93b"), outline=col(O))
    elif kind.startswith("totem"):
        tint = {"totem_harvest": "#e2b532", "totem_fert": "#8a6a3a", "totem_rain": "#4aa6e8", "totem_sun": "#f4c030",
                "totem_moon": "#9466ee"}.get(kind, "#e2b532")
        d.rectangle((24, 6, 40, 60), fill=col("#7a5230"), outline=col(O), width=2)
        for i, yy in enumerate((8, 26, 44)):
            d.rectangle((20, yy, 44, yy + 15), fill=col("#9a6a3e"), outline=col(O), width=2)
            d.rectangle((25, yy + 4, 29, yy + 8), fill=col(tint))
            d.rectangle((35, yy + 4, 39, yy + 8), fill=col(tint))
            d.line((27, yy + 12, 37, yy + 12), fill=col(O), width=2)
        _poly(d, [(20, 10), (6, 4), (20, 18)], tint, O)
        _poly(d, [(44, 10), (58, 4), (44, 18)], tint, O)
        d.ellipse((50, 26, 58, 34), fill=col(tint, 0.9))
        d.ellipse((6, 36, 12, 42), fill=col(tint, 0.8))
    if kind.startswith("ench_"):
        g = L.getchannel("A").filter(ImageFilter.MaxFilter(5))
        glow = Image.new("RGBA", L.size, col("#c070ff"))
        glow.putalpha(g.point(lambda v: int(v * 0.55)))
        out = Image.new("RGBA", L.size, (0, 0, 0, 0))
        out.alpha_composite(glow)
        out.alpha_composite(L)
        d2 = ImageDraw.Draw(out)
        for sx, sy in ((10, 12), (54, 22), (50, 54)):
            _poly(d2, [(sx, sy - 6), (sx + 2, sy), (sx, sy + 6), (sx - 2, sy)], "#ffffff")
            _poly(d2, [(sx - 6, sy), (sx, sy - 2), (sx + 6, sy), (sx, sy + 2)], "#ffffff")
        L = out
    return L


_IC = {}


def item_icon(kind, size):
    k = (kind, size)
    if k not in _IC:
        _IC[k] = _icon64(kind).resize((size, size), Image.LANCZOS)
    return _IC[k]


def shard_icon(size=64):
    im = Image.open(os.path.join(ICONS, "Skyy_Shard_Portal_Farming.png")).convert("RGBA")
    return im if size == 64 else im.resize((size, size), Image.NEAREST)


# ------------------------------------------------------------------ page shell
def shell(tab, mode="portal", status=None, hover_tab=None, stored=STORED_TOTAL, totems=4):
    """mode: 'portal' (opened on your island: Enter Shard + Pick up) / 'hub' (inside the shard: Back to Island)."""
    P = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    put(P, nine("Frame_World", PW, PH, 32), 0, 0, "page")
    put(P, nine("Header", HDR[2], HDR[3], 60, 0), HDR[0], HDR[1], "header", "page")
    P.alpha_composite(scaled("HeaderOrnament", 236, 22), ((PW - 236) // 2, HDR[1] - 12))
    T(P, (PW // 2, HDR[1] + 19), "Farming Shard", 18, C["title"], True, "mm", maxw=400)
    P.alpha_composite(scaled("Close", 32, 32), (PW - 24 - 36, 21))
    strip(P, mode, stored=stored, totems=totems)
    for i, t in enumerate(TABS):
        name = "Tab_Selected" if t == tab else ("Tab_Hovered" if t == hover_tab else "Tab")
        tb = nine(name, TABW, TABH, 20, 12)
        MK.text(tb, (TABW // 2, TABH // 2), t, 15, C["white"] if t == tab else C["button2Text"], True, "mm")
        put(P, tb, 24 + i * (TABW + TABG), TABY, "tab " + t, "page")
    if status:
        T(P, (24 + 16, STATUS_Y), status[0], 15, status[1], True, "lm", maxw=1000)
    gold_line(P, 24, LINE_Y, PW - 48)
    if mode == "portal":
        put(P, button("secondary", 170, 36, "Pick up Shard", 15), 44, FOOT, "btn pickup", "page")
    put(P, button("secondary", 150, 36, "Close", 15), PW - 44 - 150, FOOT, "btn close", "page")
    return P


def strip(P, mode, full=False, stored=STORED_TOTAL, totems=4):
    x, y, w, h = STRIP
    put(P, nine("Panel", w, h, 12), x, y, "strip", "page")
    put(P, shard_icon(64), x + 12, y + 6, "strip icon", "strip")
    tx = x + 12 + 64 + 14
    pct = stored / STORAGE_CAP[3]
    rate = RATE if totems else 0
    T(P, (tx, y + 26), "3 islands  ·  %d totems  ·  Time x%.2f  ·  %d items / hour" % (totems, TIME_MULT[2], rate), 15,
      C["rowName"], True, "lm", maxw=470)
    sub = {"portal": "Opened from the portal on your island  ·  Farming Sprites work here",
           "hub": "You are on the hub island of this shard  ·  Farming Sprites work here"}[mode]
    T(P, (tx, y + 50), sub, 13, C["caption"], False, "lm", maxw=470)
    # storage mini bar
    sx, sw_ = 590, 250
    if full:
        T(P, (sx, y + 24), "Storage FULL", 13, C["error"], True, "lm")
        T(P, (sx + sw_, y + 24), "%s / %s" % (f"{STORAGE_CAP[3]:,}", f"{STORAGE_CAP[3]:,}"), 13, C["error"], True, "rm")
        bar(P, sx, y + 38, sw_, 10, 1.0, "#ff6b6b")
        T(P, (sx, y + 60), "Production stopped - collect now", 12, C["error"], False, "lm", maxw=sw_)
    else:
        T(P, (sx, y + 24), "Storage", 13, C["panelTitle"], True, "lm")
        T(P, (sx + sw_, y + 24), "%s / %s" % (f"{stored:,}", f"{STORAGE_CAP[3]:,}"), 13, C["value"], True, "rm")
        bar(P, sx, y + 38, sw_, 10, pct, C["progressGreen"])
        if rate:
            hrs = (STORAGE_CAP[3] - stored) / rate
            T(P, (sx, y + 60), "Full in %d h %02d m" % (int(hrs), int(round((hrs - int(hrs)) * 60))), 12, C["rowSub"], False,
              "lm", maxw=sw_)
        else:
            T(P, (sx, y + 60), "No totems - nothing is harvested", 12, C["warning"], False, "lm", maxw=sw_)
    bw, bh = 180, 44
    if mode == "portal":
        b = button("primary", bw, bh, "Enter Shard", 16)
    else:
        b = button("secondary", bw, bh, "Back to Island", 16)
    put(P, b, x + w - 16 - bw, y + (h - bh) // 2, "strip btn", "strip")


def panel(P, box, name, title=None, caption=None, right=None):
    x, y, w, h = box
    put(P, nine("Panel", w, h, 12), x, y, name, "page")
    if title:
        T(P, (x + 16, y + 22), title, 16, C["panelTitle"], True, "lm", maxw=w - 32)
    if caption:
        T(P, (x + 16, y + 43), caption, 13, C["caption"], False, "lm", maxw=w - 32)
    if right:
        T(P, (x + w - 16, y + 22), right[0], 13, right[1], True, "rm")


# ------------------------------------------------------------------ (a) COLLECT
def collect_tab(P, empty=False):
    panel(P, LP, "left", "Stored in this shard", "Collect to get the items, collection progress and Farming XP.",
          ("%d kinds" % (0 if empty else len(STORED)), C["caption"]))
    x0, y0 = LP[0] + 12, LP[1] + 62
    rw, rh = LP[2] - 24, 56
    if empty:
        wb = (LP[0] + 12, y0, rw, 6 * 60 - 4)
        put(P, nine("PanelInset", wb[2], wb[3], 8), wb[0], wb[1], "empty well", "left")
        T(P, (wb[0] + wb[2] // 2, wb[1] + wb[3] // 2 - 14), "Nothing to collect yet", 16, C["panelTitle"], True, "mm")
        T(P, (wb[0] + wb[2] // 2, wb[1] + wb[3] // 2 + 12), "Your islands are growing. Come back soon.", 13, C["caption"],
          False, "mm")
    else:
        for i, (ic, name, src, n, xp, ck, cn) in enumerate(STORED):
            y = y0 + i * (rh + 4)
            rn = "Row_Hovered" if i == 2 else "Row"
            put(P, nine(rn, rw, rh, 8), x0, y, "row%d" % i, "left")
            put(P, slot(44, ic), x0 + 8, y + 6)
            T(P, (x0 + 62, y + 19), name, 15, C["gold"] if ic.startswith("ench_") else C["rowName"], True, "lm", maxw=300)
            T(P, (x0 + 62, y + 39), "%s  ·  %s XP each" % (src, ("%g" % xp)), 12, C["rowSub"], False, "lm", maxw=330)
            T(P, (x0 + rw - 12 - 96 - 16, y + rh // 2), "%s" % f"{n:,}", 17, C["white"], True, "rm")
            put(P, button("tertiary", 96, 30, "Collect", 13, "_Hovered" if i == 2 else ""), x0 + rw - 12 - 96, y + 13,
                "rowbtn%d" % i, "row%d" % i)
    # capacity bar
    yb = LP[1] + LP[3] - 130
    gold_line(P, LP[0] + 16, yb, LP[2] - 32, 0.25)
    stored = 0 if empty else STORED_TOTAL
    T(P, (LP[0] + 16, yb + 20), "Storage", 15, C["panelTitle"], True, "lm")
    T(P, (LP[0] + LP[2] - 16, yb + 20), "%s / %s  (%d %%)" % (f"{stored:,}", f"{STORAGE_CAP[3]:,}",
                                                              round(100 * stored / STORAGE_CAP[3])), 15, C["value"], True, "rm")
    bx, by, bw_, bh_ = LP[0] + 16, yb + 34, LP[2] - 32, 16
    R(P, (bx, by, bw_, bh_), "#000000(0.55)")
    if not empty:
        cx = bx
        for (ic, name, src, n, xp, ck, cn) in STORED:     # stacked fill, one colour per item
            seg = int(round(bw_ * n / STORAGE_CAP[3]))
            R(P, (cx, by, seg, bh_), CROP_COL[ic] + "(0.85)")
            R(P, (cx, by, 1, bh_), "#000000(0.35)")
            cx += seg
    R(P, (bx, by, bw_, bh_), None, "#E8A93B(0.35)")
    if not empty:      # legend for the stacked bar
        lx = bx
        for (ic, name, src, n, xp, ck, cn) in STORED:
            R(P, (lx, yb + 60, 10, 10), CROP_COL[ic] + "(0.85)", "#000000(0.6)")
            lab = name.replace("Enchanted", "Ench.")
            T(P, (lx + 14, yb + 65), lab, 12, C["rowSub"], False, "lm")
            lx += 14 + int(tw(lab, 12)) + 16
        if lx > bx + bw_:
            PROBLEMS.append("storage legend too wide")
    hrs = (STORAGE_CAP[3] - stored) / RATE
    T(P, (LP[0] + 16, yb + 88), "Full in %d h %02d m at %d items / hour. A full shard stops producing." %
      (int(hrs), int(round((hrs - int(hrs)) * 60)), RATE), 13, C["text"], False, "lm", maxw=LP[2] - 32)
    T(P, (LP[0] + 16, yb + 107), "Raise the limit in Upgrades -> Storage. Each Enchanted item counts as 1.", 13, C["caption"],
      False, "lm", maxw=LP[2] - 32)
    collect_all_panel(P, empty)


def collect_all_panel(P, empty=False, full_inv=False):
    x, y, w, h = RP
    panel(P, RP, "right", "Collect all", "You get all of this at once:")
    wx, wy, ww, wh = x + 16, y + 58, w - 32, 222
    put(P, nine("PanelInset", ww, wh, 8), wx, wy, "sum well", "right")
    if empty:
        T(P, (wx + ww // 2, wy + wh // 2), "Nothing stored", 14, C["caption"], True, "mm")
    else:
        put(P, item_icon("seeds", 22) if False else item_icon("storage", 22), wx + 12, wy + 12)
        T(P, (wx + 42, wy + 23), "%s items" % f"{STORED_TOTAL:,}", 15, C["white"], True, "lm")
        T(P, (wx + ww - 12, wy + 23), "%d kinds" % len(STORED), 13, C["caption"], False, "rm")
        put(P, item_icon("xp", 22), wx + 12, wy + 42)
        T(P, (wx + 42, wy + 53), "+%s Farming XP" % f"{int(XP_TOTAL):,}", 15, C["success"], True, "lm")
        gold_line(P, wx + 12, wy + 76, ww - 24, 0.25)
        T(P, (wx + 12, wy + 92), "Collections", 13, C["panelTitle"], True, "lm")
        gain = {}
        for (ic, name, src, n, xp, ck, cn) in STORED:
            if ck:
                gain[ck] = gain.get(ck, 0) + n * cn
        yy = wy + 108
        for ck in ("Wheat", "Lettuce", "Carrot"):
            rank, have, need = COLL[ck]
            g = gain[ck]
            T(P, (wx + 12, yy + 9), "%s %s" % (ck, rank), 13, C["rowName"], True, "lm")
            T(P, (wx + ww - 12, yy + 9), "+%s" % f"{g:,}", 13, C["success"], True, "rm")
            bar(P, wx + 12, yy + 20, ww - 24, 6, have / need, C["progressGreen"], add=g / need)
            yy += 36
    if empty:
        T(P, (x + 16, y + h - 16 - 48 - 16), "Last collected just now", 12, C["caption"], False, "lm")
        put(P, button("primary", w - 32, 48, "Collect all", 17, "_Disabled"), x + 16, y + h - 16 - 48, "collect all", "right")
        return
    # where the items go
    gy = wy + wh + 16
    T(P, (x + 16, gy + 10), "Where the items go", 14, C["panelTitle"], True, "lm")
    T(P, (x + 16, gy + 30), "Sacks first, then your inventory.", 13, C["text"], False, "lm", maxw=w - 32)
    if full_inv:
        T(P, (x + 16, gy + 50), "Inventory full: 420 Carrot stay here.", 13, C["warning"], True, "lm", maxw=w - 32)
    else:
        MK.tick(P, x + 16, gy + 44, C["success"])
        T(P, (x + 36, gy + 50), "Everything fits.", 13, C["success"], True, "lm", maxw=w - 52)
    gold_line(P, x + 16, gy + 72, w - 32, 0.25)
    for k, line in enumerate(("Farming XP and collection progress", "are only given when you collect.")):
        T(P, (x + 16, gy + 92 + k * 18), line, 12, C["caption"], False, "lm", maxw=w - 32)
    T(P, (x + 16, y + h - 16 - 48 - 16), "Last collected 7 h 37 m ago", 12, C["caption"], False, "lm")
    state = "_Hovered"
    put(P, button("primary", w - 32, 48, "Collect all", 17, state), x + 16, y + h - 16 - 48, "collect all", "right")


# ------------------------------------------------------------------ (b) UPGRADES
UPG = [
    # key, icon, name, level, max, now, next, desc lines, costs [(icon, name, have, need)], req (text, ok), state
    ("storage", "storage", "Storage", 3, 8, "%s items" % f"{STORAGE_CAP[3]:,}", "%s items" % f"{STORAGE_CAP[4]:,}",
     ["The most this shard holds. When it is", "full, the islands stop producing."],
     [("coins", "Coins", COINS, 25000), ("ench_wheat", "Enchanted Wheat", 40, 32), ("eternal", "Eternal Wheat Seeds", 6, 4)],
     ("Farming 10", True), "ok"),
    ("compactor", "compactor", "Auto-Compactor", 1, 2, "Crops -> Enchanted", "+ seeds and drops",
     ["Turns every 100 of a crop into 1", "Enchanted crop. Saves storage."],
     [("coins", "Coins", COINS, 40000), ("ench_wheat", "Enchanted Wheat", 40, 64), ("ench_lettuce", "Enchanted Lettuce", 12, 64)],
     ("Farming 10", True), "missing"),
    ("time", "time", "Time Compressor", 2, 5, "x%.2f  (%d / h)" % (TIME_MULT[2], RATE), "x%.2f  (%d / h)" % (TIME_MULT[3], RATE_NEXT),
     ["Time runs faster inside the shard,", "so every island makes more per hour."],
     [("coins", "Coins", COINS, 60000), ("ench_wheat", "Enchanted Wheat", 40, 128), ("eternal", "Eternal Lettuce Seeds", 2, 8)],
     ("Farming 20", False), "req"),
]


def upgrade_card(P, x, y, w, h, u, state=None, hover=False):
    key, ic, name, lvl, mx, now, nxt, desc, costs, req, st = u
    st = state or st
    nm = "card " + key
    put(P, nine("CardFrame", w, h, 32), x, y, nm, "page")
    put(P, item_icon(ic, 64), x + (w - 64) // 2, y + 26, nm + " icon", nm)
    T(P, (x + w // 2, y + 110), name, 18, C["rowName"], True, "mm", maxw=w - 48)
    maxed = st == "max"
    if maxed and key == "storage":
        now = "%s items" % f"{STORAGE_CAP[8]:,}"
    lvl_s = "Level %d / %d" % (mx if maxed else lvl, mx)
    T(P, (x + w // 2, y + 134), lvl_s, 14, C["gold"] if maxed else C["value"], True, "mm")
    pw_ = mx * 22 + (mx - 1) * 4
    pips(P, x + (w - pw_) // 2, y + 148, mx, mx if maxed else lvl, nxt=not maxed)
    if key == "compactor":   # on / off switch (saves on click)
        sw = 2 * 64 + 2
        sx = x + (w - sw) // 2
        put(P, button("tertiary", 64, 24, "On", 12, "_Active"), sx, y + 164, nm + " on", nm)
        put(P, button("tertiary", 64, 24, "Off", 12), sx + 66, y + 164, nm + " off", nm)
    iy = y + 198
    iw = w - 48
    put(P, nine("PanelInset", iw, 66, 8), x + 24, iy, nm + " well", nm)
    T(P, (x + 36, iy + 18), "Now", 13, C["caption"], False, "lm")
    T(P, (x + 24 + iw - 12, iy + 18), now, 14, C["white"], True, "rm", maxw=iw - 70)
    if maxed:
        T(P, (x + 36, iy + 46), "Next", 13, C["caption"], False, "lm")
        T(P, (x + 24 + iw - 12, iy + 46), "Fully upgraded", 14, C["gold"], True, "rm")
    else:
        T(P, (x + 36, iy + 46), "Next", 13, C["caption"], False, "lm")
        T(P, (x + 24 + iw - 12, iy + 46), nxt, 14, C["success"], True, "rm", maxw=iw - 70)
    for k, line in enumerate(desc):
        T(P, (x + 24, iy + 84 + k * 18), line, 13, C["text"], False, "lm", maxw=iw)
    cy = iy + 130
    if maxed:
        T(P, (x + w // 2, cy + 50), "Nothing left to buy here.", 13, C["caption"], False, "mm")
    else:
        T(P, (x + 24, cy), "Cost", 14, C["panelTitle"], True, "lm")
        T(P, (x + w - 24, cy), "have / need", 12, C["caption"], False, "rm")
        for k, (cic, cname, have, need) in enumerate(costs):
            ry = cy + 14 + k * 28
            put(P, item_icon(cic, 22), x + 24, ry + 2)
            ok = have >= need
            T(P, (x + 54, ry + 13), cname, 13, C["rowName"], False, "lm", maxw=136)
            T(P, (x + w - 24, ry + 13), "%s / %s" % (f"{have:,}", f"{need:,}"), 13, C["success"] if ok else C["error"], True,
              "rm", maxw=100)
        ry = cy + 14 + 3 * 28 + 6
        rtxt, rok = req
        if rok:
            MK.tick(P, x + 24, ry + 2, C["success"])
            T(P, (x + 44, ry + 8), "Needs %s  (you: %d)" % (rtxt, FARMING_LVL), 13, C["success"], False, "lm")
        else:
            T(P, (x + 24, ry + 8), "x", 14, C["error"], True, "lm", track=False)
            T(P, (x + 44, ry + 8), "Needs %s  (you: %d)" % (rtxt, FARMING_LVL), 13, C["error"], True, "lm")
    by = y + h - 24 - 44
    bw = w - 48
    if maxed:
        b = button("tertiary", bw, 44, "MAX LEVEL", 15, "_Active", label_color=C["gold"])
    elif st == "ok":
        b = button("primary", bw, 44, "Upgrade to Level %d" % (lvl + 1), 15, "_Hovered" if hover else "")
    elif st == "missing":
        miss = sum(1 for c in costs if c[2] < c[3])
        b = button("primary", bw, 44, "Missing %d item%s" % (miss, "s" if miss > 1 else ""), 15, "_Disabled")
    else:
        b = button("primary", bw, 44, "Needs " + req[0], 15, "_Disabled")
    put(P, b, x + 24, by, nm + " buy", nm)


def upgrades_tab(P):
    w = (1052 - 2 * 16) // 3
    for i, u in enumerate(UPG):
        upgrade_card(P, 24 + i * (w + 16), CT, w, CB - CT, u, hover=(i == 0))


# ------------------------------------------------------------------ (c) ISLANDS
MAP = (36, CT + 56, 676, CB - CT - 56 - 12)       # map well inside the left panel
SIZES = {"S": ("Small", 26, "8 x 8", 64, 1), "M": ("Medium", 34, "12 x 12", 144, 2), "L": ("Large", 42, "16 x 16", 256, 3)}
SLOTS = [  # slot no, state, crop, size, unlock level
    (1, "filled", "wheat", "L", 0),
    (2, "filled", "lettuce", "M", 0),
    (3, "filled", "carrot", "S", 0),
    (4, "empty", None, None, 0),
    (5, "empty", None, None, 10),
    (6, "locked", None, None, 15),
    (7, "locked", None, None, 20),
    (8, "locked", None, None, 25),
]


def slot_pos(i):
    cx, cy = MAP[0] + MAP[2] // 2, MAP[1] + MAP[3] // 2
    a = math.radians(-90 + 45 * i)
    return cx + 250 * math.cos(a), cy + 168 * math.sin(a)


def draw_island(L, cx, cy, r, crop, glow=None):
    d = ImageDraw.Draw(L)
    # underside rock (floating island)
    d.polygon([(cx - r * 0.9, cy + r * 0.15), (cx + r * 0.9, cy + r * 0.15), (cx + r * 0.35, cy + r * 1.05),
               (cx, cy + r * 1.35), (cx - r * 0.4, cy + r * 1.0)], fill=col("#4a4458"), outline=col("#2a2438"))
    d.polygon([(cx - r * 0.4, cy + r * 0.3), (cx + r * 0.2, cy + r * 0.3), (cx, cy + r * 1.2)], fill=col("#5c5670"))
    d.ellipse((cx - r, cy - r * 0.62, cx + r, cy + r * 0.5), fill=col("#5a3e28"), outline=col("#2a1e14"))
    d.ellipse((cx - r, cy - r * 0.7, cx + r, cy + r * 0.38), fill=col("#4e9a3a"), outline=col("#2a5a1e"))
    if crop == "hub":
        d.ellipse((cx - r * 0.55, cy - r * 0.42, cx + r * 0.55, cy + r * 0.18), fill=col("#8a8a96"), outline=col("#4a4a56"))
        # portal arch + swirl
        d.rounded_rectangle((cx - 13, cy - r * 0.42 - 34, cx + 13, cy - r * 0.2), 10, fill=col("#3a2a5a"), outline=col("#c9a8ff"),
                            width=2)
        d.ellipse((cx - 8, cy - r * 0.42 - 26, cx + 8, cy - r * 0.42 - 6), fill=col("#9466ee"))
        d.ellipse((cx - 4, cy - r * 0.42 - 20, cx + 4, cy - r * 0.42 - 12), fill=col("#e2d4ff"))
        # menu stand
        d.rectangle((cx + 24, cy - 14, cx + 32, cy + 2), fill=col("#7a5230"), outline=col("#2a1e14"))
        d.rectangle((cx + 20, cy - 20, cx + 36, cy - 12), fill=col("#e8a93b"), outline=col("#2a1e14"))
        return
    if crop:
        c = CROP_COL[crop]
        rows = max(2, int(r / 7))
        for k in range(rows):
            yy = cy - r * 0.48 + (k + 0.5) * (r * 0.78 / rows)
            half = r * 0.78 * math.sqrt(max(0.0, 1 - ((yy - (cy - r * 0.16)) / (r * 0.56)) ** 2))
            d.line((cx - half, yy, cx + half, yy), fill=col("#6a4a2a"), width=3)
            xx = cx - half + 3
            while xx < cx + half - 2:
                d.ellipse((xx - 2, yy - 3, xx + 2, yy + 1), fill=col(c))
                xx += 6


def pill(P, cx, cy, s, color, size=13):
    w = int(tw(s, size, True)) + 14
    lay = Image.new("RGBA", (w, 20), (0, 0, 0, 0))
    ImageDraw.Draw(lay).rounded_rectangle((0, 0, w - 1, 19), 9, fill=(10, 18, 34, 170))
    P.alpha_composite(lay, (int(cx - w / 2), int(cy - 10)))
    T(P, (cx, cy), s, size, color, True, "mm")


def islands_map(P, sel=3, hover=4):
    x, y, w, h = MAP
    put(P, nine("PanelInset", w, h, 8), x, y, "map", "left")
    # sky inside the well
    sky = Image.new("RGBA", (w - 8, h - 8), (0, 0, 0, 255))
    ds = ImageDraw.Draw(sky)
    for yy in range(h - 8):
        t = yy / (h - 8)
        ds.line((0, yy, w, yy), fill=(int(40 + 40 * t), int(78 + 52 * t), int(130 + 50 * t), 255))
    rng = random.Random(1013)
    cl = Image.new("RGBA", sky.size, (0, 0, 0, 0))
    dc = ImageDraw.Draw(cl)
    for _ in range(26):
        cx_, cy_ = rng.randrange(-40, w), rng.randrange(0, h)
        rw_, rh_ = rng.randrange(50, 140), rng.randrange(14, 30)
        dc.ellipse((cx_, cy_, cx_ + rw_, cy_ + rh_), fill=(235, 242, 255, rng.randrange(24, 52)))
    cl = cl.filter(ImageFilter.GaussianBlur(6))
    sky.alpha_composite(cl)
    P.alpha_composite(sky, (x + 4, y + 4))
    L = Image.new("RGBA", P.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    hx, hy = x + w // 2, y + h // 2
    # bridges first (only filled slots have one); planned bridges dotted
    for i, (no, st, crop, size, lv) in enumerate(SLOTS):
        sx, sy = slot_pos(i)
        ang = math.atan2(sy - hy, sx - hx)
        r_end = SIZES[size][1] if size else 30
        x0, y0 = hx + 58 * math.cos(ang), hy + 38 * math.sin(ang)
        x1, y1 = sx - r_end * 0.9 * math.cos(ang), sy - r_end * 0.6 * math.sin(ang)
        if st == "filled":
            nx, ny = -math.sin(ang) * 6, math.cos(ang) * 6
            d.polygon([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)], fill=col("#8a5a2e"),
                      outline=col("#3a2414"))
            n = int(math.hypot(x1 - x0, y1 - y0) / 7)
            for k in range(1, n):
                px_, py_ = x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n
                d.line((px_ + nx, py_ + ny, px_ - nx, py_ - ny), fill=col("#5a3a1e"), width=1)
        else:
            n = int(math.hypot(x1 - x0, y1 - y0) / 10)
            for k in range(1, n):
                px_, py_ = x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n
                d.ellipse((px_ - 1.5, py_ - 1.5, px_ + 1.5, py_ + 1.5), fill=(255, 255, 255, 70 if st == "empty" else 35))
    P.alpha_composite(L)
    L = Image.new("RGBA", P.size, (0, 0, 0, 0))
    draw_island(L, hx, hy - 6, 62, "hub")
    P.alpha_composite(L)
    pill(P, hx, hy + 76, "Hub  (portal + menu)", "#ffffff")
    for i, (no, st, crop, size, lv) in enumerate(SLOTS):
        sx, sy = slot_pos(i)
        L = Image.new("RGBA", P.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(L)
        R0 = 46
        lx, ly, py = sx, sy + R0 + 12, sy + R0 + 24
        if i == 0:      # the top slot: label to the RIGHT (its bridge runs down to the hub, below it)
            lab0 = "%s  ·  %s" % (crop.capitalize(), SIZES[size][0]) if crop else ""
            lx, ly, py = sx + R0 + 4 + (tw(lab0, 13, True) + 14) / 2, sy - 4, sy + 10
        if no == sel:
            for k, a in ((10, 40), (6, 80), (3, 140)):
                d.ellipse((sx - R0 - k, sy - R0 - k, sx + R0 + k, sy + R0 + k), outline=(232, 169, 59, a), width=3)
            d.ellipse((sx - R0, sy - R0, sx + R0, sy + R0), fill=(232, 169, 59, 40), outline=col(C["gold"]), width=2)
        elif no == hover:
            d.ellipse((sx - R0, sy - R0, sx + R0, sy + R0), fill=(255, 255, 255, 36), outline=(255, 255, 255, 200), width=2)
        if st == "filled":
            P.alpha_composite(L)
            L = Image.new("RGBA", P.size, (0, 0, 0, 0))
            draw_island(L, sx, sy - 4, SIZES[size][1], crop)
            P.alpha_composite(L)
            lab = "%s  ·  %s" % (crop.capitalize(), SIZES[size][0])
            pill(P, lx, ly, lab, "#ffffff" if no != sel else "#ffe2a8")
            for k in range(3):      # size pips under the label
                px_ = lx - 19 + k * 14
                R(P, (px_, py, 10, 4), C["gold"] if k < "SML".index(size) + 1 else "#000000(0.5)")
        elif st == "empty":
            if no != hover:
                for k in range(0, 360, 20):
                    a0 = math.radians(k)
                    d.arc((sx - 30, sy - 30, sx + 30, sy + 30), k, k + 11, fill=(255, 255, 255, 190), width=2)
            else:
                d.ellipse((sx - 30, sy - 30, sx + 30, sy + 30), outline=(255, 255, 255, 230), width=2)
            P.alpha_composite(L)
            P.alpha_composite(item_icon("plus", 26), (int(sx - 13), int(sy - 13)))
            pill(P, lx, ly, "Add island", "#ffffff")
        else:
            for k in range(0, 360, 20):
                d.arc((sx - 30, sy - 30, sx + 30, sy + 30), k, k + 11, fill=(255, 255, 255, 80), width=2)
            d.ellipse((sx - 29, sy - 29, sx + 29, sy + 29), fill=(10, 16, 30, 110))
            P.alpha_composite(L)
            P.alpha_composite(item_icon("lock", 26), (int(sx - 13), int(sy - 13)))
            pill(P, lx, ly, "Farming %d" % lv, "#c8d4e0")
        reg("slot%d" % no, (sx - R0, sy - R0, 2 * R0, 2 * R0), "map")
        T(P, (sx - R0 + 2, sy - R0 + 8), str(no), 11, "#ffffff", True, "lm", alpha=0.6)


def islands_tab(P, side="filled"):
    panel(P, LP, "left", "Islands around the hub", "Pick a slot. Any island fits any slot; it grows in place.")
    legend_x = LP[0] + LP[2] - 16
    T(P, (legend_x, LP[1] + 22), "5 of 8 slots open", 13, C["value"], True, "rm")
    islands_map(P)
    if side == "filled":
        side_filled(P)
    elif side == "empty":
        side_empty(P)
    elif side == "locked":
        side_locked(P)
    elif side == "max":
        side_filled(P, maxed=True)


def size_steps(P, x, y, cur, w):
    bw = (w - 2 * 4) // 3
    for k, key in enumerate("SML"):
        lab = SIZES[key][0]
        if k < cur:
            st, lc = "_Active", C["gold"]
        elif k == cur:
            st, lc = "", C["success"]
        else:
            st, lc = "", C["button2Text"]
        b = button("tertiary", bw, 30, lab, 13, st, label_color=lc if k != cur else C["success"])
        if k > cur:
            b = fade(b, 0.6)
        put(P, b, x + k * (bw + 4), y, "size%d" % k, "right")
    return bw


def side_filled(P, maxed=False):
    x, y, w, h = RP
    size = "L" if maxed else "S"
    panel(P, RP, "right", "Slot 3  -  Carrot Island" if not maxed else "Slot 1  -  Wheat Island",
          "Large  ·  fully grown" if maxed else "Small  ·  bridge to the hub built")
    T(P, (x + 16, y + 74), "Island size", 13, C["panelTitle"], True, "lm")
    size_steps(P, x + 16, y + 86, 3 if maxed else 1, w - 32)
    wy = y + 130
    put(P, nine("PanelInset", w - 32, 128, 8), x + 16, wy, "fx well", "right")
    cur = SIZES[size]
    nxt = SIZES["L" if maxed else "M"]
    rows = [("Size (blocks)", cur[2], None if maxed else nxt[2]),
            ("Farm plots", str(cur[3]), None if maxed else str(nxt[3])),
            ("Totem places", str(cur[4]), None if maxed else str(nxt[4])),
            ("Carrot / hour", "%d" % int(46 * TIME_MULT[2]), None if maxed else "%d" % int(46 * 144 / 64 * TIME_MULT[2]))]
    if maxed:
        rows[3] = ("Wheat / hour", "%d" % int(150 * TIME_MULT[2]), None)
    if not maxed:
        T(P, (x + w - 28, wy + 14), "now  ->  next", 11, C["caption"], False, "rm")
    for k, (lab, a, b) in enumerate(rows):
        ry = wy + 34 + k * 24
        T(P, (x + 28, ry), lab, 13, C["text"], False, "lm")
        if b is None:
            T(P, (x + w - 28, ry), a, 14, C["white"], True, "rm")
        else:
            bw_ = tw(b, 14, True)
            T(P, (x + w - 28, ry), b, 14, C["success"], True, "rm")
            T(P, (x + w - 28 - bw_ - 8, ry), "->", 13, C["caption"], True, "rm")
            T(P, (x + w - 28 - bw_ - 8 - 22, ry), a, 14, C["white"], True, "rm")
    cy = wy + 128 + 22
    if maxed:
        T(P, (x + 16, cy), "This island is at its biggest size.", 13, C["caption"], False, "lm")
        T(P, (x + 16, cy + 18), "Improve it with totems (Totems tab).", 13, C["caption"], False, "lm")
        put(P, button("primary", w - 32, 44, "Fully grown", 15, "_Disabled"), x + 16, y + h - 16 - 36 - 10 - 44, "btn up",
            "right")
    else:
        T(P, (x + 16, cy), "Cost to grow to Medium", 14, C["panelTitle"], True, "lm")
        T(P, (x + w - 16, cy), "have / need", 12, C["caption"], False, "rm")
        costs = [("carrot", "Carrot", 2310, 2000), ("eternal", "Eternal Carrot Seeds", 5, 4), ("coins", "Coins", COINS, 15000)]
        for k, (cic, cname, have, need) in enumerate(costs):
            ry = cy + 14 + k * 28
            put(P, item_icon(cic, 22), x + 16, ry + 2)
            T(P, (x + 46, ry + 13), cname, 13, C["rowName"], False, "lm", maxw=150)
            T(P, (x + w - 16, ry + 13), "%s / %s" % (f"{have:,}", f"{need:,}"), 13, C["success"] if have >= need else C["error"],
              True, "rm")
        put(P, button("primary", w - 32, 44, "Grow to Medium", 16, "_Hovered"), x + 16, y + h - 16 - 36 - 10 - 44, "btn up",
            "right")
    put(P, button("secondary", w - 32, 36, "Totems on this island (%d)" % (3 if maxed else 0), 14), x + 16, y + h - 16 - 36,
        "btn totems", "right")


CROPS_ADD = [("corn", "Corn", "ok"), ("cauliflower", "Cauliflower", "Carrot V"), ("turnip", "Turnip", "Carrot V"),
             ("pumpkin", "Pumpkin", "Farming 15"), ("aubergine", "Aubergine", "Farming 15"), ("tomato", "Tomato", "Farming 20")]


def crop_chip_icon(kind, size):
    if kind in ("wheat", "lettuce", "carrot", "corn"):
        return item_icon(kind, size)
    L = Image.new("RGBA", (64, 64), (0, 0, 0, 0))     # generic crop: a round fruit in the crop colour
    d = ImageDraw.Draw(L)
    d.ellipse((10, 14, 54, 58), fill=col(CROP_COL[kind]), outline=col("#1c1430"), width=2)
    d.ellipse((18, 20, 30, 32), fill=(255, 255, 255, 90))
    d.rectangle((30, 4, 34, 16), fill=col("#4a9a2e"))
    return L.resize((size, size), Image.LANCZOS)


def side_empty(P):
    x, y, w, h = RP
    panel(P, RP, "right", "Slot 4  -  empty", "Pick a crop. Its island starts Small.")
    gx, gy = x + 16, y + 62
    cw, chh, g = (w - 32 - 8) // 3, 74, 4
    for k, (kind, nm, lock) in enumerate(CROPS_ADD):
        cx_ = gx + (k % 3) * (cw + 4)
        cy_ = gy + (k // 3) * (chh + g)
        rn = "Row_Selected" if k == 0 else "Row"
        tile = nine(rn, cw, chh, 8)
        if lock != "ok":
            tile = fade(tile, 0.55)
        put(P, tile, cx_, cy_, "crop%d" % k, "right")
        ic = crop_chip_icon(kind, 32)
        if lock != "ok":
            ic = fade(ic, 0.4)
        P.alpha_composite(ic, (cx_ + (cw - 32) // 2, cy_ + 8))
        T(P, (cx_ + cw // 2, cy_ + 50), nm, 13, C["rowName"] if lock == "ok" else C["disabled"], True, "mm", maxw=cw - 8)
        if lock != "ok":
            T(P, (cx_ + cw // 2, cy_ + 65), lock, 11, C["error"], False, "mm", maxw=cw - 8)
    T(P, (x + 16, gy + 2 * (chh + g) + 8), "Wheat, Lettuce and Carrot already have", 12, C["caption"], False, "lm")
    T(P, (x + 16, gy + 2 * (chh + g) + 24), "an island here (one island per crop).", 12, C["caption"], False, "lm")
    cy = gy + 2 * (chh + g) + 52
    T(P, (x + 16, cy), "Cost to add a Corn island", 14, C["panelTitle"], True, "lm")
    T(P, (x + w - 16, cy), "have / need", 12, C["caption"], False, "rm")
    costs = [("corn", "Corn", 410, 256), ("eternal", "Eternal Corn Seeds", 1, 2), ("coins", "Coins", COINS, 10000)]
    for k, (cic, cname, have, need) in enumerate(costs):
        ry = cy + 14 + k * 28
        put(P, item_icon(cic, 22), x + 16, ry + 2)
        T(P, (x + 46, ry + 13), cname, 13, C["rowName"], False, "lm", maxw=150)
        T(P, (x + w - 16, ry + 13), "%s / %s" % (f"{have:,}", f"{need:,}"), 13, C["success"] if have >= need else C["error"],
          True, "rm")
    put(P, button("primary", w - 32, 44, "Missing 1 item", 15, "_Disabled"), x + 16, y + h - 16 - 44, "btn add", "right")


def side_locked(P):
    x, y, w, h = RP
    panel(P, RP, "right", "Slot 6  -  locked", "This slot opens at a Farming level.")
    put(P, item_icon("lock", 64), x + (w - 64) // 2, y + 76, "lock icon", "right")
    T(P, (x + w // 2, y + 166), "Opens at Farming 15", 17, C["gold"], True, "mm")
    T(P, (x + w // 2, y + 190), "You are Farming %d" % FARMING_LVL, 13, C["text"], False, "mm")
    bar(P, x + 40, y + 206, w - 80, 8, FARMING_LVL / 15.0, C["progressGreen"])
    T(P, (x + w // 2, y + 230), "%d / 15" % FARMING_LVL, 12, C["caption"], False, "mm")
    gold_line(P, x + 16, y + 254, w - 32, 0.25)
    T(P, (x + 16, y + 276), "Slot openings", 14, C["panelTitle"], True, "lm")
    for k, (s, lv) in enumerate(((1, "start"), (2, "start"), (3, "start"), (4, "start"), (5, "Farming 10"), (6, "Farming 15"),
                                 (7, "Farming 20"), (8, "Farming 25"))):
        ry = y + 298 + k * 22
        done = lv == "start" or int(lv.split()[1]) <= FARMING_LVL
        T(P, (x + 28, ry), "Slot %d" % s, 13, C["text"], False, "lm")
        T(P, (x + w - 28, ry), lv, 13, C["success"] if done else (C["gold"] if s == 6 else C["caption"]), True, "rm")


# ------------------------------------------------------------------ (d) TOTEMS
TOTEMS = [
    # icon, name, tier, island, worker line, status, slots used
    ("totem_harvest", "Harvest Spirit Pole", "II", "Wheat Island", "2 Sprites  ·  range 9 x 9", ("Working", "#39f493"), 2),
    ("totem_fert", "Fertilizer Pole", "I", "Wheat Island", "growth +15 %  ·  range 7 x 7", ("Working", "#39f493"), 1),
    ("totem_rain", "Rain Pole", "I", "Wheat Island", "keeps plots watered  ·  range 7 x 7", ("Working", "#39f493"), 0),
    ("totem_harvest", "Harvest Spirit Totem", "I", "Lettuce Island", "1 Sprite  ·  range 5 x 5", ("Waiting: nothing ripe", "#ffcc00"), 0),
]


def totems_tab(P, empty=False, full_storage=False):
    panel(P, LP, "left", "Totems in this shard", None, ("%d of 6 places used" % (0 if empty else 4), C["value"]))
    fx, fy = LP[0] + 16, LP[1] + 40
    filt = [("All (%d)" % (0 if empty else 4), True), ("Wheat (3)", False), ("Lettuce (1)", False), ("Carrot (0)", False)]
    if empty:
        filt = [("All (0)", True), ("Wheat (0)", False), ("Lettuce (0)", False), ("Carrot (0)", False)]
    bx = fx
    for lab, act in filt:
        bw = int(tw(lab, 13, True)) + 28
        put(P, button("tertiary", bw, 28, lab, 13, "_Active" if act else ""), bx, fy, "filter " + lab, "left")
        bx += bw + 4
    x0, y0 = LP[0] + 12, LP[1] + 80
    rw, rh = LP[2] - 24, 64
    rows = [] if empty else list(TOTEMS)
    k = 0
    for i, (ic, nm, tier, isl, wl, stt, used) in enumerate(rows):
        y = y0 + k * (rh + 4)
        rn = "Row_Selected" if i == 0 else "Row"
        put(P, nine(rn, rw, rh, 8), x0, y, "trow%d" % i, "left")
        put(P, slot(52, ic), x0 + 8, y + 6)
        T(P, (x0 + 72, y + 21), "%s %s" % (nm, tier), 15, C["rowName"], True, "lm", maxw=300)
        T(P, (x0 + 72, y + 43), "%s  ·  %s" % (isl, wl), 12, C["rowSub"], False, "lm", maxw=360)
        s_txt, s_col = stt
        if full_storage:
            s_txt, s_col = "Stopped: storage full", "#ff6b6b"
        chip(P, x0 + rw - 14, y + 12, s_txt, s_col, anchor_right=True)
        T(P, (x0 + rw - 14, y + 46), "Upgrade slots %d / 2" % used, 12, C["caption"], False, "rm")
        k += 1
    free = [("Lettuce Island", 1), ("Carrot Island", 1)] if not empty else [("Wheat Island", 3), ("Lettuce Island", 2),
                                                                              ("Carrot Island", 1)]
    for isl, n in free:
        y = y0 + k * (rh + 4)
        g = fade(nine("Row", rw, rh, 8), 0.5)
        put(P, g, x0, y, "free%d" % k, "left")
        L = Image.new("RGBA", P.size, (0, 0, 0, 0))
        MK.dashed(L, (x0 + 8, y + 6, 52, 52), "#ffffff(0.35)", 1, 4, 4)
        P.alpha_composite(L)
        P.alpha_composite(fade(item_icon("plus", 22), 0.7), (x0 + 23, y + 21))
        T(P, (x0 + 72, y + 21), "Free totem place%s - %s" % ("s" if n > 1 else "", isl) if n > 1 else
          "Free totem place - %s" % isl, 15, C["text"], True, "lm", maxw=420)
        T(P, (x0 + 72, y + 43), "Stand on the island and place a totem from your hotbar.", 12, C["caption"], False, "lm",
          maxw=480)
        if n > 1:
            T(P, (x0 + rw - 14, y + rh // 2), "x%d" % n, 15, C["caption"], True, "rm")
        k += 1
    hy = LP[1] + LP[3] - 50
    gold_line(P, LP[0] + 16, hy - 12, LP[2] - 32, 0.25)
    T(P, (LP[0] + 16, hy + 6), "Craft totems at the Farmer's Workbench. Tier them up on the Anvil (Upgrade tab).", 13,
      C["caption"], False, "lm", maxw=LP[2] - 32)
    T(P, (LP[0] + 16, hy + 26), "Bigger islands give more totem places (Small 1, Medium 2, Large 3).", 13, C["caption"],
      False, "lm", maxw=LP[2] - 32)
    if empty:
        side_no_totem(P)
    else:
        side_totem(P, mode="portal")


def side_totem(P, mode="portal"):
    x, y, w, h = RP
    panel(P, RP, "right")
    put(P, slot(72, "totem_harvest"), x + 16, y + 16, "big icon", "right")
    T(P, (x + 100, y + 32), "Harvest Spirit Pole", 17, C["rowName"], True, "lm", maxw=w - 116)
    T(P, (x + 100, y + 54), "Tier II of III  ·  Wheat Island", 13, C["value"], False, "lm", maxw=w - 116)
    pips(P, x + 100, y + 70, 3, 2, w=30, h=7)
    wy = y + 104
    put(P, nine("PanelInset", w - 32, 104, 8), x + 16, wy, "stats", "right")
    for k, (a, b, c2) in enumerate((("Workers", "2 Farming Sprites", C["white"]), ("Range", "9 x 9 blocks", C["white"]),
                                     ("Harvest speed", "1 crop / 2.0 s", C["white"]), ("Status", "Working", C["success"]))):
        ry = wy + 16 + k * 24
        T(P, (x + 28, ry), a, 13, C["text"], False, "lm")
        T(P, (x + w - 28, ry), b, 13, c2, True, "rm")
    sy = wy + 104 + 22
    T(P, (x + 16, sy), "Upgrade slots", 14, C["panelTitle"], True, "lm")
    T(P, (x + w - 16, sy), "click a slot to change", 11, C["caption"], False, "rm")
    for k, (ic, lab) in enumerate((("area", "Wider Area"), ("replant", "Auto-Replant"))):
        sx = x + 16 + k * ((w - 32) // 2)
        put(P, slot(56, ic), sx, sy + 14, "uslot%d" % k, "right")
        T(P, (sx + 64, sy + 34), lab, 13, C["rowName"], True, "lm", maxw=86)
        T(P, (sx + 64, sy + 52), "+2 range" if k == 0 else "on", 12, C["success"], False, "lm")
    fy = sy + 86
    T(P, (x + 16, fy), "Booster fuel (optional)", 14, C["panelTitle"], True, "lm")
    put(P, slot(56, "essence"), x + 16, fy + 14, "fuel", "right")
    T(P, (x + 80, fy + 32), "Life Essence x12", 13, C["rowName"], True, "lm", maxw=w - 96)
    T(P, (x + 80, fy + 50), "+20 % growth  ·  31 m left", 12, C["success"], False, "lm", maxw=w - 96)
    ny = fy + 82
    put(P, nine("PanelInset", w - 32, 64, 8), x + 16, ny, "next tier", "right")
    T(P, (x + 28, ny + 16), "Next: Tier III", 13, C["panelTitle"], True, "lm")
    T(P, (x + w - 28, ny + 16), "Anvil -> Upgrade tab", 12, C["caption"], False, "rm")
    T(P, (x + 28, ny + 42), "3 Sprites  ·  range 13 x 13  ·  1 crop / 1.5 s", 12, C["success"], False, "lm", maxw=w - 56)
    bw = (w - 32 - 8) // 2
    by = y + h - 16 - 36
    put(P, button("secondary", bw, 36, "Pick up", 15, "_Hovered"), x + 16, by, "btn pick", "right")
    if mode == "portal":
        put(P, button("secondary", bw, 36, "Go to totem", 15, "_Disabled"), x + 16 + bw + 8, by, "btn go", "right")
        T(P, (x + 16 + bw + 8 + bw // 2, by - 12), "inside the shard only", 11, C["caption"], False, "mm")
    else:
        put(P, button("secondary", bw, 36, "Go to totem", 15), x + 16 + bw + 8, by, "btn go", "right")


def side_no_totem(P):
    x, y, w, h = RP
    panel(P, RP, "right", "No totems yet", "Totems automate your islands.")
    put(P, item_icon("totem_harvest", 64), x + (w - 64) // 2, y + 80, "ic", "right")
    lines = ["1. Craft a Harvest Spirit Totem at", "   the Farmer's Workbench.", "2. Enter the shard and stand on", "   an island.",
             "3. Place the totem. Its Sprites", "   harvest ripe crops into the", "   shard storage."]
    for k, s in enumerate(lines):
        T(P, (x + 16, y + 172 + k * 20), s, 13, C["text"], False, "lm", maxw=w - 32)


# ------------------------------------------------------------------ compositions
def on_world(P, tag_txt):
    img = MK.world()
    MK.rect(img, (0, 0, SW, SH), "#000000(0.30)")
    img.alpha_composite(P, (PX, PY))
    MK.tag(img, PX, PY - 32, tag_txt, "#3a2808(0.92)", "#ffe2a8", 12)
    return img


def page(tab, mode="portal", **kw):
    status = {"Collect": ("+  Collected 120 Carrot  (+72 Farming XP)", C["success"]),
              "Upgrades": ("+  Time Compressor: Level 2 bought - time now runs x1.25.", C["success"]),
              "Islands": ("Slot 3 selected. Carrot Island can grow to Medium.", C["value"]),
              "Totems": ("Harvest Spirit Pole II selected.", C["value"])}[tab]
    P = shell(tab, mode, status)
    {"Collect": collect_tab, "Upgrades": upgrades_tab, "Islands": islands_tab, "Totems": totems_tab}[tab](P, **kw)
    check(tab + (" " + str(kw) if kw else ""))
    return P


def label(img, x, y, s, size=14, color="#ffe2a8"):
    MK.text(img, (x, y), s, size, color, True)


def layout_sheet():
    """LAYOUT FIRST: the shell with every region boxed + its pixel box; below it each tab's content grid (x 0.25)."""
    sc = 0.25
    gw, gh = int(PW * sc), int((CB - CT + 24) * sc)
    W, H = PW + 80, 80 + PH + 60 + gh + 6 * 15 + 30
    img = Image.new("RGBA", (W, H), col("#10161f"))
    label(img, 40, 18, "SHARD MENU - LAYOUT: page 1100 x 860 UI, centred (1 UI = 1 px at 1080p). Boxes = x, y, w, h in page px.", 16)
    MK.text(img, (40, 44), "Gold = the shell (the same on every tab). Blue = the content area. Below: each tab's grid at 1:4.", 13,
            "#c8d4e0")
    ox, oy = 40, 80
    img.alpha_composite(nine("Frame_World", PW, PH, 32), (ox, oy))
    boxes = [("Header", HDR, "lt"), ("Summary strip (Panel)", STRIP, "rb")]
    for i, t in enumerate(TABS):
        boxes.append(("Tab " + t, (24 + i * (TABW + TABG), TABY, TABW, TABH), "lt"))
    boxes += [("Left panel", LP, "lt"), ("Right panel", RP, "lt"), ("Status line", (24, STATUS_Y - 10, 1052, 20), "lt"),
              ("Pick up Shard", (44, FOOT, 170, 36), "lt"), ("Close", (PW - 44 - 150, FOOT, 150, 36), "lt")]
    for name, (x, y, w, h), where in boxes:
        c = "#7fd0ff" if name in ("Left panel", "Right panel") else "#E8A93B"
        MK.rect(img, (ox + x, oy + y, w, h), c + "(0.10)", c + "(0.9)", 1)
        st = "%s %d,%d %dx%d" % (name.replace("Tab ", ""), x, y, w, h)
        if where == "rb":
            MK.text(img, (ox + x + w - 6, oy + y + h - 3), st, 10, "#ffffff", True, "rd")
        else:
            MK.text(img, (ox + x + 5, oy + y + 4), st, 11 if w > 160 else 10, "#ffffff", True)
    bx_e = 24 + 1052 - 16 - 180
    for name, (x, y, w, h) in (("icon 64", (36, 72, 64, 64)), ("summary text, max 470 w", (114, 78, 470, 54)),
                               ("storage mini bar 250 w", (590, 78, 250, 54)), ("Enter Shard 180x44", (bx_e, 82, 180, 44))):
        MK.rect(img, (ox + x, oy + y, w, h), None, "#ffffff(0.6)", 1)
        MK.text(img, (ox + x + 3, oy + y + 3), name, 10, "#ffffff")
    MK.text(img, (ox + 44 + 180, oy + FOOT + 18), "<- portal view only (hub view: no Pick up)", 11, "#c8d4e0", False, "lm")
    grids = {
        "Collect": [("left panel: up to 6 rows 676x56, gap 4", LP), ("right panel: Collect all", RP),
                    ("storage bar 668x16", (40, CB - 130 + 34, 668, 16)), ("Collect all 308x48", (752, CB - 64, 308, 48))],
        "Upgrades": [("card %d 340x564" % (i + 1), (24 + i * 356, CT, 340, CB - CT)) for i in range(3)] +
                    [("buy button 292x44 (each card)", (48, CB - 68, 292, 44))],
        "Islands": [("left panel", LP), ("map well 676x496", MAP), ("side panel", RP),
                    ("Grow 308x44 + Totems 308x36", (752, CB - 16 - 36 - 10 - 44, 308, 90))],
        "Totems": [("filters 28 high", (40, CT + 40, 400, 28)), ("rows 676x64, gap 4", (36, CT + 80, 676, 6 * 68 - 4)),
                   ("selected totem", RP), ("Pick up / Go to 150x36", (752, CB - 52, 308, 36))],
    }
    gy = oy + PH + 30
    for i, t in enumerate(TABS):
        gx = ox + i * (gw + 0) + (0 if i == 0 else 0)
        gx = ox + int(i * (PW / 4.0))
        label(img, gx, gy, t, 13, "#7fd0ff")
        g = Image.new("RGBA", (gw, gh), col("#0d1527"))
        for name, (x, y, w, h) in grids[t]:
            MK.rect(g, (int(x * sc), int((y - CT + 12) * sc), max(2, int(w * sc)), max(2, int(h * sc))), "#7fd0ff(0.12)",
                    "#7fd0ff(0.9)")
        img.alpha_composite(g, (gx, gy + 20))
        for k, (name, (x, y, w, h)) in enumerate(grids[t]):
            s2 = fit("%s @ %d,%d" % (name, x, y), 10, False, gw - 4)
            MK.text(img, (gx, gy + 24 + gh + k * 15), s2, 10, "#c8d4e0")
    return img


def states_sheet():
    W, H = 1920, 1470
    img = Image.new("RGBA", (W, H), col("#10161f"))
    bgc = (13, 21, 39, 255)
    label(img, 30, 16, "SHARD MENU - STATES (all at 1:1 UI px)", 18)

    def frame_bg(w, h):
        return Image.new("RGBA", (w, h), bgc)

    # 1. tabs
    y = 56
    label(img, 30, y, "1  Tab states: normal / hovered / selected (Tab, Tab_Hovered, Tab_Selected; 260 x 44, Bold 15)")
    for k, (nm, st) in enumerate((("Tab", "Collect"), ("Tab_Hovered", "Upgrades"), ("Tab_Selected", "Islands"))):
        tb = nine(nm, TABW, TABH, 20, 12)
        MK.text(tb, (TABW // 2, TABH // 2), st, 15, C["white"] if nm == "Tab_Selected" else C["button2Text"], True, "mm")
        img.alpha_composite(tb, (30 + k * (TABW + 20), y + 24))
    # 2. header strip variants
    y = 140
    label(img, 30, y, "2  Summary strip: from the PORTAL (Enter Shard)  /  inside the shard at the HUB (Back to Island)  /  storage FULL")
    for k, (mode, full) in enumerate((("portal", False), ("hub", False), ("portal", True))):
        P = Image.new("RGBA", (PW, 90), bgc)
        Q = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
        strip(Q, mode, full)
        P.alpha_composite(Q.crop((0, 60, PW, 150)), (0, 0))
        img.alpha_composite(P.crop((20, 0, PW - 20, 90)), (30, y + 22 + k * 92))
        REG.clear()
        TXT.clear()
    # 3. buy button states
    y = 440
    label(img, 30, y, "3  Buy / grow button (Primary 292 x 44): affordable (hovered) / missing items / requirement not met / maxed")
    for k, b in enumerate((button("primary", 292, 44, "Upgrade to Level 4", 15, "_Hovered"),
                           button("primary", 292, 44, "Missing 2 items", 15, "_Disabled"),
                           button("primary", 292, 44, "Needs Farming 20", 15, "_Disabled"),
                           button("tertiary", 292, 44, "MAX LEVEL", 15, "_Active", label_color=C["gold"]))):
        img.alpha_composite(b, (30 + k * 312, y + 26))
    # 4. maxed upgrade card + 5. island slot states
    y = 520
    label(img, 30, y, "4  Upgrade card at MAX")
    P = frame_bg(372, 600)
    upgrade_card(P, 16, 16, 340, 564, UPG[0], state="max")
    img.alpha_composite(P, (30, y + 24))
    REG.clear()
    TXT.clear()
    label(img, 430, y, "5  Island slot states on the map (96 px circles): filled S / M / L, selected, hovered empty, empty, locked")
    P = Image.new("RGBA", (1100, 200), (0, 0, 0, 0))
    sky = Image.new("RGBA", (1100, 200), (58, 98, 150, 255))
    P.alpha_composite(sky)
    demo = [("S", "carrot", "filled"), ("M", "lettuce", "filled"), ("L", "wheat", "filled"), ("S", "carrot", "sel"),
            ("", None, "hover"), ("", None, "empty"), ("", None, "locked")]
    for k, (sz, crop, st) in enumerate(demo):
        sx, sy = 70 + k * 150, 80
        L = Image.new("RGBA", P.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(L)
        if st == "sel":
            for kk, a in ((10, 40), (6, 80), (3, 140)):
                d.ellipse((sx - 46 - kk, sy - 46 - kk, sx + 46 + kk, sy + 46 + kk), outline=(232, 169, 59, a), width=3)
            d.ellipse((sx - 46, sy - 46, sx + 46, sy + 46), fill=(232, 169, 59, 40), outline=col(C["gold"]), width=2)
        if st == "hover":
            d.ellipse((sx - 46, sy - 46, sx + 46, sy + 46), fill=(255, 255, 255, 36), outline=(255, 255, 255, 200), width=2)
            d.ellipse((sx - 30, sy - 30, sx + 30, sy + 30), outline=(255, 255, 255, 230), width=2)
        if st in ("empty", "locked"):
            for kk in range(0, 360, 20):
                d.arc((sx - 30, sy - 30, sx + 30, sy + 30), kk, kk + 11, fill=(255, 255, 255, 190 if st == "empty" else 80),
                      width=2)
            if st == "locked":
                d.ellipse((sx - 29, sy - 29, sx + 29, sy + 29), fill=(10, 16, 30, 110))
        P.alpha_composite(L)
        if crop:
            L = Image.new("RGBA", P.size, (0, 0, 0, 0))
            draw_island(L, sx, sy - 4, SIZES[sz][1], crop)
            P.alpha_composite(L)
            lab = SIZES[sz][0] + (" (selected)" if st == "sel" else "")
        elif st == "locked":
            P.alpha_composite(item_icon("lock", 26), (sx - 13, sy - 13))
            lab = "Locked"
        else:
            P.alpha_composite(item_icon("plus", 26), (sx - 13, sy - 13))
            lab = "Empty (hovered)" if st == "hover" else "Empty"
        MK.text(P, (sx, sy + 66), lab, 13, "#ffffff", True, "mm")
    img.alpha_composite(P, (430, y + 24))
    # 6. side panels: empty slot (add) / locked slot / max island
    y = 760
    label(img, 430, y, "6  Islands side panel: empty slot (pick a crop)  /  locked slot  /  fully grown island")
    for k, side in enumerate(("empty", "locked", "max")):
        Q = Image.new("RGBA", (PW, PH), bgc)
        {"empty": side_empty, "locked": side_locked, "max": lambda q: side_filled(q, maxed=True)}[side](Q)
        check("side " + side)
        img.alpha_composite(Q.crop((RP[0] - 8, RP[1] - 8, RP[0] + RP[2] + 8, RP[1] + RP[3] + 8)), (430 + k * 368, y + 24))
    # 7. status chips + empty states
    y = 1360
    label(img, 30, y, "7  Totem status chips")
    cx = 30
    for s_txt, s_col in (("Working", "#39f493"), ("Waiting: nothing ripe", "#ffcc00"), ("Stopped: storage full", "#ff6b6b"),
                         ("Picked up", "#878e9c")):
        P = Image.new("RGBA", (220, 24), bgc)
        w = chip(P, 0, 2, s_txt, s_col)
        img.alpha_composite(P.crop((0, 0, w + 2, 24)), (cx, y + 26))
        cx += w + 14
    TXT.clear()
    label(img, 30, y + 70, "Empty tabs: Collect with nothing stored = 'Nothing to collect yet' + Collect all disabled; "
                           "Totems with none placed = how-to panel (see shard_e2_empty_states.png).", 13, "#c8d4e0")
    return img


def empties_sheet():
    """Two empty-state pages side by side at half size (for the states sheet's 'see below')."""
    a = shell("Collect", "portal", None, stored=0)
    collect_tab(a, empty=True)
    check("Collect empty")
    b = shell("Totems", "hub", None, totems=0, stored=0)
    totems_tab(b, empty=True)
    check("Totems empty")
    out = Image.new("RGBA", (PW + 40, 2 * PH + 120), col("#10161f"))
    label(out, 20, 14, "EMPTY STATES at 1:1 - Collect (nothing stored, from the portal) and Totems (none placed, at the hub)", 15)
    out.alpha_composite(a, (20, 50))
    out.alpha_composite(b, (20, 70 + PH))
    return out


def check_1366():
    full = on_world(page("Islands"), "SHARD MENU -> Islands")
    a = full.resize((1366, 768), Image.LANCZOS)
    sw, sh = 1366, 768
    b = MK.world().resize((sw, sh), Image.LANCZOS)
    MK.rect(b, (0, 0, sw, sh), "#000000(0.30)")
    P = page("Islands")
    ox, oy = (sw - PW) // 2, (sh - PH) // 2      # 133, -46
    b.alpha_composite(P.crop((0, -oy, PW, -oy + sh)), (ox, 0))
    MK.dashed(b, (ox, 0, PW, sh), "#ff7070(0.95)", 3)
    MK.tag(b, ox + 8, 8, "page 1100 x 860 > 768: %d px cut at the top and bottom" % (-oy), "#5a1818(0.92)", "#ffd0d0", 12)
    out = Image.new("RGBA", (1366 * 2 + 60, 768 + 150), col("#10161f"))
    out.alpha_composite(a, (20, 96))
    out.alpha_composite(b, (1366 + 40, 96))
    label(out, 20, 14, "SHARD MENU - 1366 x 768 CHECK", 18)
    MK.text(out, (20, 46), "A  The client scales the UI to the screen height (x %.3f): the page fits whole; 13 px text becomes ~%.1f px, "
            "11 px becomes ~%.1f px." % (768 / 1080, 13 * 768 / 1080, 11 * 768 / 1080), 13, "#e6e6e6")
    MK.text(out, (20, 68), "B  The client does NOT scale (1 UI = 1 px): the page is taller than the screen; the header and the footer "
            "are cut off (same as every 1100+ x 860+ page we have).", 13, "#e6e6e6")
    MK.text(out, (20, 768 + 112), "A: whole page, every control reachable.", 13, "#ffd0a0", True)
    MK.text(out, (1366 + 40, 768 + 112), "B: fallback if needed = a compact 1100 x 720 variant (strip folded into the header, "
            "rows 48, cards 500 high) - not drawn.", 13, "#ffd0a0", True)
    return out


def save(img, name):
    img.convert("RGB").save(os.path.join(HERE, name), "PNG", optimize=False)


def main():
    save(layout_sheet(), "shard_0_layout.png")
    save(on_world(page("Collect"), "NEW  SHARD MENU -> Collect   1100 x 860, centred   (opened from the shard portal on your island)"),
         "shard_a_collect_1080p.png")
    save(on_world(page("Upgrades"), "NEW  SHARD MENU -> Upgrades   Storage / Auto-Compactor / Time Compressor"),
         "shard_b_upgrades_1080p.png")
    save(on_world(page("Islands"), "NEW  SHARD MENU -> Islands   8 fixed slots around the hub; Slot 3 selected"),
         "shard_c_islands_1080p.png")
    save(on_world(page("Totems"), "NEW  SHARD MENU -> Totems   placed totems + free places; Harvest Spirit Pole selected"),
         "shard_d_totems_1080p.png")
    save(states_sheet(), "shard_e_states.png")
    save(empties_sheet(), "shard_e2_empty_states.png")
    save(check_1366(), "shard_f_check_1366x768.png")
    print("totals: stored %d, XP %.1f, rate %d -> %d / h" % (STORED_TOTAL, XP_TOTAL, RATE, RATE_NEXT))
    print("layout: OK" if not PROBLEMS else "layout problems:\n  " + "\n  ".join(PROBLEMS))


if __name__ == "__main__":
    main()
