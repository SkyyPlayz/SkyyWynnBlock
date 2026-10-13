#!/usr/bin/env python3
"""SkyWynn /rebirth page mockups (cloud draft 2026-10-13, paper only - nothing built).

Draws, next to this script (research/cloud/rebirth-page-1013/):
  a_idle_1080p.png            the radial tree page, nobody hovering (Nexus asleep: class not at cap)
  a_layout_annotated_1080p.png the same page with every box, radius and size marked
  b_hover_notmet_1080p.png    hovering the Nexus while a requirement is NOT met
  c_hover_met_1080p.png       hovering the Nexus with every requirement met (Nexus awake)
  d_confirm_1080p.png         after the click: the confirm step (resets / keeps / gains, 3 s count, Not yet / Rebirth)
  e_node_tooltip_1080p.png    hovering a part-levelled node (node tooltip) + a selected node in the side panel
  f_fallback_tabs_1080p.png   FALLBACK if the UI cannot place nodes freely / draw diagonal lines: one tab per arm, a row ladder
  g_check_1366x768.png        the 1366 x 768 fit check of the main page (A scaled, B unscaled)
  h_states_crop.png           1:1 and 2x: Nexus states, node states, confirm button states, plain-text tooltip fallback

Kit: the SKY WINDOW textures (art/ui-kit-sky/Common/UI/Custom/SkyyKit/*@2x.png), 9-sliced exactly like
research/cloud/ui-mockups-1013/make_mockups.py does (that file is imported for nine(), scaled(), world(), button(), the colours and
fonts, so both sets match). The Nexus picture is LOADED AT RENDER TIME from
research/cloud/icons-1013/icons/Skyy_Nexus_Of_The_Void.png, so a re-run picks up a redrawn icon.
Fonts: Liberation Sans stands in for the game's Nunito Sans / Lexend (the game font is a little wider).

Every number in the scenario (levels, points, XP, caps) is a placeholder that follows research/cloud/Rebirth-Research.md.
Deterministic: no clock, seeded randomness only; two runs give the same bytes.
Run: python3 research/cloud/rebirth-page-1013/make_rebirth.py
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
nine, scaled, col, font, tw, fade, button, world, dashed = MK.nine, MK.scaled, MK.col, MK.font, MK.tw, MK.fade, MK.button, MK.world, MK.dashed
C = MK.C
NEXUS_PNG = os.path.join(REPO, "research", "cloud", "icons-1013", "icons", "Skyy_Nexus_Of_The_Void.png")

SW, SH = 1920, 1080

# ====================================================================== small drawing helpers
def T(img, xy, s, size, color, bold=False, anchor="la", alpha=1.0):
    """Text on a small layer (fast + alpha-correct on transparent layers)."""
    f = font(size, bold)
    x0, y0, x1, y1 = ImageDraw.Draw(img).textbbox(xy, s, font=f, anchor=anchor)
    pad = 2
    w, h = int(x1 - x0) + 2 * pad + 2, int(y1 - y0) + 2 * pad + 2
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((xy[0] - int(x0) + pad, xy[1] - int(y0) + pad), s, font=f, fill=col(color, alpha), anchor=anchor)
    _paste_clip(img, lay, int(x0) - pad, int(y0) - pad)
    return x1 - x0


def _paste_clip(img, lay, x, y):
    cx, cy = max(0, -x), max(0, -y)
    lay = lay.crop((cx, cy, lay.width, lay.height))
    img.alpha_composite(lay, (x + cx, y + cy))


def R(img, box, fill=None, outline=None, width=1):
    x, y, w, h = box
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(lay).rectangle((0, 0, w - 1, h - 1), fill=col(fill) if fill else None,
                                  outline=col(outline) if outline else None, width=width)
    img.alpha_composite(lay, (x, y))


def fit(s, size, bold, maxw):
    if tw(s, size, bold) <= maxw:
        return s
    while s and tw(s + "...", size, bold) > maxw:
        s = s[:-1]
    return s.rstrip() + "..."


def hline(img, x, y, w, color="#E8A93B(0.35)"):
    R(img, (x, y, w, 1), color)


def tick(img, x, y, ok, size=14):
    """Pre-rendered status icons (in game: 3 tiny textures, or the words OK / NO in the plain fallback)."""
    lay = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    s = size
    if ok == "ok":
        d.line((2, s * 0.55, s * 0.42, s - 3, s - 2, 3), fill=col(C["success"]), width=3, joint="curve")
    elif ok == "no":
        d.line((3, 3, s - 4, s - 4), fill=col(C["error"]), width=3)
        d.line((3, s - 4, s - 4, 3), fill=col(C["error"]), width=3)
    else:  # warn
        d.polygon(((s / 2, 1), (s - 1, s - 2), (1, s - 2)), fill=col(C["warning"]))
        d.rectangle((s / 2 - 1, 5, s / 2, s - 7), fill=(20, 20, 20, 255))
        d.rectangle((s / 2 - 1, s - 5, s / 2, s - 4), fill=(20, 20, 20, 255))
    img.alpha_composite(lay, (int(x), int(y)))


def cursor(img, x, y):
    pts = [(0, 0), (0, 17), (4, 13), (7, 20), (10, 19), (7, 12), (12, 12)]
    lay = Image.new("RGBA", (16, 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.polygon([(px + 1, py + 1) for px, py in pts], fill=(255, 255, 255, 255), outline=(10, 10, 10, 255))
    img.alpha_composite(lay, (int(x), int(y)))


def lock_glyph(img, cx, cy, color):
    d = ImageDraw.Draw(img)
    c = col(color)
    d.rectangle((cx - 5, cy - 1, cx + 5, cy + 6), fill=c)
    d.arc((cx - 4, cy - 8, cx + 4, cy + 2), 180, 360, fill=c, width=2)


def glow(size, color, radius, blur):
    """A soft round glow (pre-rendered texture in game)."""
    lay = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    c = size // 2
    ImageDraw.Draw(lay).ellipse((c - radius, c - radius, c + radius, c + radius), fill=col(color))
    return lay.filter(ImageFilter.GaussianBlur(blur))


def tag(img, x, y, s, bg="#3a2808(0.92)", fg="#ffe2a8", size=12):
    w = int(tw(s, size, True)) + 12
    R(img, (x, y, w, size + 10), bg)
    T(img, (x + 6, y + 5), s, size, fg, True)
    return w


# ====================================================================== scenario (placeholders; research/cloud/Rebirth-Research.md)
ARMS = [  # name, colour, B (points formula), run XP / XP-to-cap ratio r, XP to cap (placeholder), unspent points, levels per row
    ("Class", "#e8606a", 12, 1.00, 3_000_000, 4, [[5, 5, 3], [5, 4, 0], [2, 0], [0, 0], [0]]),
    ("Mining", "#4aa6e8", 8, 2.30, 2_400_000, 11, [[5, 5, 4], [3, 3, 2], [3, 2], [0, 0], [0]]),
    ("Foraging", "#46b856", 8, 1.20, 2_400_000, 2, [[5, 3, 1], [3, 0, 0], [0, 0], [0, 0], [0]]),
    ("Farming", "#e2b532", 8, 0.60, 2_400_000, 9, [[3, 2, 1], [0, 0, 0], [0, 0], [0, 0], [0]]),
    ("Fishing", "#3cc8c8", 8, 0.10, 2_400_000, 3, [[0, 0, 0], [0, 0, 0], [0, 0], [0, 0], [0]]),
    ("Alchemy", "#b77cf0", 8, 0.30, 1_800_000, 0, [[3, 1, 0], [0, 0, 0], [0, 0], [0, 0], [0]]),
    ("Smithing", "#e0864a", 8, 0.80, 1_800_000, 5, [[5, 4, 0], [1, 0, 0], [0, 0], [0, 0], [0]]),
    ("Cooking", "#ec6aa6", 8, 0.26, 1_800_000, 1, [[1, 1, 0], [0, 0, 0], [0, 0], [0, 0], [0]]),
]
ROW_MAX = [5, 5, 5, 5, 1]          # levels per node, by row (row 5 = the keystone, 1 level)
GATE = 8                            # levels in a row that open the next row (Skyy, docs/answered/skills.md line 117)
REBIRTHS, MAX_REBIRTHS = 6, 10
CLASS_NOW = 96
CAP_NOW = 50 + 10 * REBIRTHS        # 110
STAT_NOW = 3 * REBIRTHS             # +18 %
BANK_BAL = 3_200_000
BANK_NOW = 1.10                     # percentage points stacked so far (placeholder)
NODE_NAMES = {  # examples only (Rebirth-Research 2.4: time savers + small stat boosts, no coin faucets)
    ("Mining", 1, 0): ("Void-Forged Pick", "Pickaxe rebirth modifier: Mining Fortune", "+%d Mining Fortune", 3),
    ("Smithing", 0, 1): ("Quick Hands", "Upgrade cost in /smithing", "-%d %% upgrade cost", 2),
    ("Foraging", 2, 0): ("Heartwood", "Foraging XP", "+%d %% Foraging XP", 2),
}


def run_points(B, r):
    """Rebirth-Research 2.3: floor(B * sqrt(r)); a skill under 25 % of its cap XP pays 0."""
    return 0 if r < 0.25 else int(math.floor(B * math.sqrt(r)))


def level_cost(k):
    """Rebirth-Research 2.4: the k-th level bought in one arm (k from 0) costs ceil(1.08^k)."""
    return int(math.ceil(1.08 ** k))


def arm_state(a):
    rows = a[6]
    spent = [sum(r) for r in rows]
    open_rows = 1
    for i in range(4):
        if spent[i] >= GATE:
            open_rows = i + 2
        else:
            break
    total = sum(spent)
    return dict(spent=spent, open=open_rows, total=total, cost=level_cost(total),
                gate=(spent[open_rows - 1] if open_rows < 5 else None))


ST = {a[0]: arm_state(a) for a in ARMS}
GAIN = {a[0]: run_points(a[2], a[3]) for a in ARMS}


def next_point_xp(B, r, capxp):
    p = run_points(B, r)
    need_r = max(0.25, ((p + 1) / B) ** 2) if p else 0.25
    return int(round(need_r * capxp - r * capxp))


# ====================================================================== page geometry (page-local px, 1 UI = 1 px at 1080p)
PW, PH = 1600, 952
PX, PY = (SW - PW) // 2, (SH - PH) // 2          # 160, 64
LP = (24, 66, 316, 862)                          # left panel: your rebirth + points per arm
CV = (356, 66, 888, 862)                         # the tree canvas (PanelInset)
RP = (1260, 66, 316, 862)                        # right panel: selected node + how it works + legend
TCX, TCY = CV[0] + CV[2] // 2, CV[1] + CV[3] // 2   # tree centre (800, 497) page-local = (960, 561) on screen
ROW_R = [178, 233, 288, 342, 390]                # row radii
LAT = [[-48, 0, 48], [-48, 0, 48], [-27, 27], [-27, 27], [0]]   # sideways offsets of the nodes in a row
NODE, KEY = 36, 44                               # node / keystone sizes
NEXUS_R = 72                                     # Nexus plate radius (the 128 icon sits inside)
CHIP_R = 120                                     # arm name chips
FORK = 26                                        # forks start this far before their row
ARM_DEG = [-90 + 45 * i for i in range(8)]   # arm angles (screen degrees, 0 = right, clockwise); Class straight up.
# Axis + diagonal arms line up with the 8 little branches drawn in the Nexus icon, so each spoke continues one of them.


# Where each arm points (index into ARM_DEG, clockwise from the top). Neighbours share a theme: Mining - Smithing,
# Farming - Alchemy, Fishing - Cooking. The shortest names sit on the left / right arms, where a chip lies along its spoke.
ARM_SLOT = {"Class": 0, "Foraging": 1, "Mining": 2, "Smithing": 3, "Alchemy": 4, "Farming": 5, "Fishing": 6, "Cooking": 7}


def arm_dir(i):
    a = math.radians(ARM_DEG[ARM_SLOT[ARMS[i][0]]])
    return math.cos(a), math.sin(a)


def node_pos(i, row, j):
    dx, dy = arm_dir(i)
    px, py = -dy, dx
    r, l = ROW_R[row], LAT[row][j]
    return TCX + dx * r + px * l, TCY + dy * r + py * l


def spoke_pt(i, r):
    dx, dy = arm_dir(i)
    return TCX + dx * r, TCY + dy * r


def chip_box(i):
    name = ARMS[i][0].upper()
    w = int(tw(name, 12, True)) + 16
    x, y = spoke_pt(i, CHIP_R)
    return (int(round(x - w / 2)), int(round(y - 11)), w, 22)


# ====================================================================== the Nexus button
_NEX = {}


def nexus_icon():
    if "i" not in _NEX:
        im = Image.open(NEXUS_PNG).convert("RGBA")
        if im.size != (128, 128):
            im = im.resize((128, 128), Image.NEAREST)
        _NEX["i"] = im
    return _NEX["i"]


def nexus(state):
    """state: asleep / awake / hover-asleep / hover-awake / pressed. 200 x 200 layer, centre 100,100.
    In game: one TextButton 144 x 144 whose Default / Hovered / Pressed backgrounds are these pictures (plate + ring + icon)."""
    S = 200
    L = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    awake = "awake" in state
    hov = "hover" in state or state == "pressed"
    if awake:
        L.alpha_composite(glow(S, "#E8A93B(0.45)", 84, 12))
        L.alpha_composite(glow(S, "#9466ee(0.55)", 78, 7))
    elif hov:
        L.alpha_composite(glow(S, "#9466ee(0.35)", 78, 8))
    d = ImageDraw.Draw(L)
    c = S // 2
    r = NEXUS_R
    d.ellipse((c - r, c - r, c + r, c + r), fill=col("#0b0818"))
    ring = "#E8A93B" if awake else "#5b4a8f"
    d.ellipse((c - r, c - r, c + r, c + r), outline=col(ring, 1.0 if awake else 0.85), width=3)
    d.ellipse((c - r + 5, c - r + 5, c + r - 5, c + r - 5), outline=col(ring, 0.35), width=1)
    ic = nexus_icon()
    if not awake:   # asleep: dimmer icon
        ic = _dim(ic, 0.62)
    if state == "pressed":
        ic = ic.resize((120, 120), Image.LANCZOS)
    L.alpha_composite(ic, (c - ic.width // 2, c - ic.height // 2))
    if hov:
        d = ImageDraw.Draw(L)
        d.ellipse((c - r - 4, c - r - 4, c + r + 4, c + r + 4), outline=col("#ffffff", 0.85), width=2)
    return L


def _dim(im, f):
    r, g, b, a = im.split()
    r, g, b = (ch.point(lambda v: int(v * f)) for ch in (r, g, b))
    return Image.merge("RGBA", (r, g, b, a))


# ====================================================================== nodes
def node_img(colour, level, maxlv, kind, hover=False, selected=False, gate_text=None, key=False):
    """kind: locked / gate / open. One pre-rendered texture per (arm, kind, level) in game + a hover + a selected overlay.
    Layer is 52 x 52, centre 26,26."""
    S = 52
    L = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    c = S // 2
    rad = (KEY if key else NODE) // 2
    if kind == "open" and level == maxlv:
        L.alpha_composite(glow(S, col(colour, 0.55), rad, 4))
    d = ImageDraw.Draw(L)
    if kind == "locked":
        d.ellipse((c - rad, c - rad, c + rad, c + rad), fill=col("#121825(0.92)"), outline=col("#343c4e"), width=2)
        lock_glyph(L, c, c, "#4a5468")
    elif kind == "gate":
        d.ellipse((c - rad, c - rad, c + rad, c + rad), fill=col("#141b2a(0.95)"), outline=col(colour, 0.40), width=2)
        T(L, (c, c), gate_text, 12, "#9aa6b6", True, "mm")
    else:
        maxed = level == maxlv
        fill = col(colour, 0.62) if maxed else (col(colour, 0.22) if level else col("#0e1524(0.95)"))
        d.ellipse((c - rad, c - rad, c + rad, c + rad), fill=col("#0e1524"))
        d.ellipse((c - rad, c - rad, c + rad, c + rad), fill=fill)
        # level ring: maxlv segments in the outer 3 px band
        seg = 360.0 / maxlv
        gap = 10 if maxlv > 1 else 0
        for k in range(maxlv):
            a0 = -90 + k * seg + gap / 2
            a1 = a0 + seg - gap
            lit = k < level
            d.arc((c - rad, c - rad, c + rad, c + rad), a0, a1,
                  fill=col("#E8A93B") if (maxed and lit) else (col(colour) if lit else col("#2b3446")), width=4)
        if key:
            d.ellipse((c - rad + 7, c - rad + 7, c + rad - 7, c + rad - 7), outline=col(colour, 0.7), width=1)
        txt = str(level)
        T(L, (c, c), txt, 15 if not key else 16, "#ffffff" if level else "#96a9be", True, "mm")
    if hover:
        d = ImageDraw.Draw(L)
        d.ellipse((c - rad - 2, c - rad - 2, c + rad + 2, c + rad + 2), outline=col("#ffffff", 0.95), width=2)
    if selected:
        d = ImageDraw.Draw(L)
        d.ellipse((c - rad - 4, c - rad - 4, c + rad + 4, c + rad + 4), outline=col("#ffe2a8"), width=2)
    return L


def node_kind(arm, row, j):
    st = ST[arm[0]]
    lv = arm[6][row][j]
    if row < st["open"]:
        return "open", lv
    if row == st["open"]:
        return "gate", 0
    return "locked", 0


# ====================================================================== the tree canvas
def canvas_bg():
    x, y, w, h = CV
    L = nine("PanelInset", w, h, 8)
    void = Image.new("RGBA", (w - 8, h - 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(void)
    cx, cy = (w - 8) // 2, (h - 8) // 2
    for k in range(40, 0, -1):          # radial void tint, darkest at the centre
        rr = k * 14
        a = int(110 * (1 - k / 40.0) ** 1.6) + 20
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=(16, 10, 34, min(255, a)))
    rng = random.Random(1013)
    for _ in range(170):                # faint stars (static art)
        sx, sy = rng.randrange(6, w - 14), rng.randrange(6, h - 14)
        v = rng.randrange(70, 150)
        d.point((sx, sy), fill=(v, v, min(255, v + 40), 255))
    for r in ROW_R:                     # faint guide rings at each row radius
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(255, 255, 255, 9), width=1)
    L.alpha_composite(void, (4, 4))
    return L


def tree_lines(layer):
    """Static line art per arm and per 'rows open' state (5 x 8 = 40 pictures in game; see the spec).
    Lit = arm colour + glow up to the last open row; the rest dim."""
    glow_l = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_l)
    d = ImageDraw.Draw(layer)
    ox, oy = CV[0], CV[1]
    dim = col("#2c3448")
    for i, arm in enumerate(ARMS):
        st = ST[arm[0]]
        colour = arm[1]
        lit_to = ROW_R[st["open"] - 1]
        # spoke
        s0 = spoke_pt(i, NEXUS_R + 6)
        s1 = spoke_pt(i, lit_to)
        s2 = spoke_pt(i, ROW_R[4])
        d.line((s0[0] - ox, s0[1] - oy, s2[0] - ox, s2[1] - oy), fill=dim, width=2)
        gd.line((s0[0] - ox, s0[1] - oy, s1[0] - ox, s1[1] - oy), fill=col(colour, 0.8), width=8)
        d.line((s0[0] - ox, s0[1] - oy, s1[0] - ox, s1[1] - oy), fill=col(colour), width=3)
        # forks
        for row in range(5):
            f0 = spoke_pt(i, ROW_R[row] - FORK)
            for j in range(len(LAT[row])):
                if LAT[row][j] == 0:
                    continue
                p = node_pos(i, row, j)
                if row < st["open"]:
                    gd.line((f0[0] - ox, f0[1] - oy, p[0] - ox, p[1] - oy), fill=col(colour, 0.7), width=7)
                    d.line((f0[0] - ox, f0[1] - oy, p[0] - ox, p[1] - oy), fill=col(colour), width=3)
                else:
                    d.line((f0[0] - ox, f0[1] - oy, p[0] - ox, p[1] - oy), fill=dim, width=2)
    glow_l = glow_l.filter(ImageFilter.GaussianBlur(4))
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    out.alpha_composite(glow_l)
    out.alpha_composite(layer)
    return out


def all_nodes():
    """[(arm index, row, j, (x, y) page-local, size)]"""
    out = []
    for i, arm in enumerate(ARMS):
        for row in range(5):
            for j in range(len(LAT[row])):
                out.append((i, row, j, node_pos(i, row, j), KEY if row == 4 else NODE))
    return out


def check_tree():
    """Layout proof: every node inside the canvas with 12 px to spare, no two nodes (with their hover ring) closer than 6 px,
    chips clear of each other / the Nexus / the nodes."""
    probs = []
    ns = all_nodes()
    x0, y0, w, h = CV
    for (i, row, j, (x, y), s) in ns:
        r = s / 2 + 4
        if x - r < x0 + 12 or x + r > x0 + w - 12 or y - r < y0 + 12 or y + r > y0 + h - 12:
            probs.append(("node outside canvas", ARMS[i][0], row, j))
    mind = 1e9
    for a in range(len(ns)):
        for b in range(a + 1, len(ns)):
            (_, _, _, (xa, ya), sa), (_, _, _, (xb, yb), sb) = ns[a], ns[b]
            dd = math.hypot(xa - xb, ya - yb) - sa / 2 - sb / 2
            mind = min(mind, dd)
            if dd < 10 - 1e-6:   # selected ring (5 px out) + 5 px clear
                probs.append(("nodes too close", ns[a][:3], ns[b][:3], round(dd, 1)))
    chips = [chip_box(i) for i in range(8)]
    for a in range(8):
        cx, cy, cw, chh = chips[a]
        for b in range(a + 1, 8):
            if MK.overlaps(chips[a], chips[b], 4):
                probs.append(("chips overlap", a, b))
        # nexus circle (+ hover ring 4) vs chip: nearest point of the chip box to the centre
        nx = min(max(TCX, cx), cx + cw)
        ny = min(max(TCY, cy), cy + chh)
        if math.hypot(nx - TCX, ny - TCY) < NEXUS_R + 6 + 4:
            probs.append(("chip touches the Nexus", a))
        for (i, row, j, (x, y), s) in ns:
            nx = min(max(x, cx), cx + cw)
            ny = min(max(y, cy), cy + chh)
            if math.hypot(nx - x, ny - y) < s / 2 + 6:
                probs.append(("chip touches a node", a, i, row, j))
    return probs, mind


def tree(selected=None, hover=None, nexus_state="asleep"):
    """The canvas layer (CV size) with lines, nodes, chips and the Nexus."""
    x0, y0, w, h = CV
    L = canvas_bg()
    L.alpha_composite(tree_lines(Image.new("RGBA", (w, h), (0, 0, 0, 0))))
    for (i, row, j, (x, y), s) in all_nodes():
        arm = ARMS[i]
        kind, lv = node_kind(arm, row, j)
        st = ST[arm[0]]
        gt = "%d/%d" % (st["gate"], GATE) if kind == "gate" else None
        img = node_img(arm[1], lv, ROW_MAX[row], kind, hover=(hover == (i, row, j)), selected=(selected == (i, row, j)),
                       gate_text=gt, key=(row == 4))
        L.alpha_composite(img, (int(round(x - x0 - 26)), int(round(y - y0 - 26))))
    for i in range(8):
        cx, cy, cw, chh = chip_box(i)
        chip = Image.new("RGBA", (cw, chh), (0, 0, 0, 0))
        dd = ImageDraw.Draw(chip)
        dd.rounded_rectangle((0, 0, cw - 1, chh - 1), 6, fill=col("#0b1224(0.92)"), outline=col(ARMS[i][1], 0.75), width=1)
        T(chip, (cw // 2, chh // 2), ARMS[i][0].upper(), 12, ARMS[i][1], True, "mm")
        L.alpha_composite(chip, (cx - x0, cy - y0))
    nx = nexus(nexus_state)
    L.alpha_composite(nx, (TCX - x0 - 100, TCY - y0 - 100))
    return L


# ====================================================================== page chrome + side panels
def frame_page(w, h, title):
    P = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    P.alpha_composite(nine("Frame", w, h, 32), (0, 0))
    P.alpha_composite(nine("Header", w - 48, 38, 60, 0), (24, 18))
    P.alpha_composite(scaled("HeaderOrnament", 236, 22), ((w - 236) // 2, 6))
    T(P, (w // 2, 37), title, 18, C["title"], True, "mm")
    P.alpha_composite(scaled("Close", 32, 32), (w - 24 - 36, 21))
    return P


def prop_rows(P, x, y, w, rows, size=14, step=24):
    for k, (lab, val, vc) in enumerate(rows):
        T(P, (x, y + k * step), lab, size, C["text"], False, "lm")
        T(P, (x + w, y + k * step), val, size, vc or C["rowName"], True, "rm")
    return y + len(rows) * step


def left_panel(P, nexus_awake=False, compact=False, box=LP):
    x, y, w, h = box
    if not compact:
        P.alpha_composite(nine("Panel", w, h, 12), (x, y))
    ix, iw = x + 16, w - 32
    T(P, (ix, y + 22), "Your rebirth", 16, C["panelTitle"], True, "lm")
    if nexus_awake:
        T(P, (ix, y + 46), "Nexus awake - Class %d / %d" % (CAP_NOW, CAP_NOW), 13, C["success"], True, "lm")
    else:
        T(P, (ix, y + 46), "Nexus asleep - Class %d / %d" % (CLASS_NOW, CAP_NOW), 13, C["warning"], True, "lm")
    rows = [("Rebirths", "%d / %d" % (REBIRTHS, MAX_REBIRTHS), None), ("Stat boost", "+%d %%" % STAT_NOW, C["success"]),
            ("Class cap", str(CAP_NOW), None), ("Skill caps", "+%d" % (10 * REBIRTHS), None),
            ("Bank bonus", "+%.2f %%" % BANK_NOW, C["success"]), ("Title", "Void-Touched VI", C["gold"])]
    yy = prop_rows(P, ix, y + 76, iw, rows)
    hline(P, ix, yy - 2, iw)
    if compact:
        return
    T(P, (ix, yy + 20), "Points to spend", 16, C["panelTitle"], True, "lm")
    T(P, (ix, yy + 40), "Each arm spends its own points.", 13, C["caption"], False, "lm")
    ry = yy + 54
    for i, arm in enumerate(ARMS):
        st = ST[arm[0]]
        rw = w - 24
        P.alpha_composite(nine("Row", rw, 50, 8), (x + 12, ry))
        d = ImageDraw.Draw(P)
        d.rounded_rectangle((x + 24, ry + 12, x + 34, ry + 22), 2, fill=col(arm[1]))
        T(P, (x + 42, ry + 17), arm[0], 15, C["rowName"], True, "lm")
        sub = "Levels %d / 55" % st["total"]
        sub += ("  -  Row %d: %d / %d" % (st["open"] + 1, st["gate"], GATE)) if st["open"] < 5 else ""
        T(P, (x + 24, ry + 36), fit(sub, 12, False, rw - 80), 12, C["rowSub"], False, "lm")
        pc = C["gold"] if arm[5] >= st["cost"] else C["caption"]
        T(P, (x + 12 + rw - 12, ry + 19), str(arm[5]), 20, pc, True, "rm")
        T(P, (x + 12 + rw - 12, ry + 38), "pts", 12, C["caption"], False, "rm")
        ry += 54
    T(P, (ix, ry + 14), "Gold = enough for the next level.", 13, C["caption"], False, "lm")
    T(P, (ix, ry + 32), "Prices rise with each level bought", 13, C["caption"], False, "lm")
    T(P, (ix, ry + 50), "in an arm (cheap first).", 13, C["caption"], False, "lm")
    by = y + h - 16 - 36
    assert ry + 60 < by, ("left panel overflow", ry, by)
    P.alpha_composite(button("secondary", iw, 36, "Back", 15), (ix, by))


def legend_block(P, x, y, w):
    T(P, (x, y), "Node states", 15, C["panelTitle"], True, "lm")
    items = [(node_img("#4aa6e8", 0, 5, "locked"), "Locked (row not open yet)"),
             (node_img("#4aa6e8", 0, 5, "gate", gate_text="5/8"), "Next row: 5 of 8 levels done"),
             (node_img("#4aa6e8", 0, 5, "open"), "Open, level 0"),
             (node_img("#4aa6e8", 3, 5, "open"), "Level 3 of 5"),
             (node_img("#4aa6e8", 5, 5, "open"), "Maxed (gold ring)"),
             (node_img("#4aa6e8", 0, 1, "open", key=True), "Keystone (1 level, big effect)")]
    yy = y + 16
    for img, lab in items:
        P.alpha_composite(img, (x - 6, yy - 6))
        T(P, (x + 52, yy + 20), lab, 13, C["text"], False, "lm")
        yy += 44
    return yy


def right_panel(P, sel=(1, 1, 0), status=None):
    x, y, w, h = RP
    P.alpha_composite(nine("Panel", w, h, 12), (x, y))
    ix, iw = x + 16, w - 32
    i, row, j = sel
    arm = ARMS[i]
    st = ST[arm[0]]
    name, what, fmt, per = NODE_NAMES[(arm[0], row, j)]
    lv = arm[6][row][j]
    T(P, (ix, y + 22), "Selected node", 16, C["panelTitle"], True, "lm")
    well = nine("PanelInset", iw, 268, 8)
    P.alpha_composite(well, (ix, y + 40))
    P.alpha_composite(node_img(arm[1], lv, ROW_MAX[row], "open", selected=True), (ix + 8, y + 50))
    T(P, (ix + 66, y + 66), fit(name, 17, True, iw - 76), 17, C["white"], True, "lm")
    T(P, (ix + 66, y + 88), "%s - Row %d" % (arm[0], row + 1), 13, arm[1], True, "lm")
    rows = [("Level", "%d / %d" % (lv, ROW_MAX[row]), None),
            ("Now", fmt % (per * lv), C["success"]),
            ("Next level", fmt % (per * (lv + 1)), C["info"]),
            ("Cost", "%d %s points" % (st["cost"], arm[0]), None),
            ("You have", "%d" % arm[5], C["gold"] if arm[5] >= st["cost"] else C["error"])]
    T(P, (ix + 12, y + 122), fit(what, 13, False, iw - 24), 13, C["caption"], False, "lm")
    prop_rows(P, ix + 12, y + 150, iw - 24, rows, 14, 24)
    ok = arm[5] >= st["cost"]
    P.alpha_composite(button("primary", iw - 24, 40, "Buy level %d" % (lv + 1), 15, "" if ok else "_Disabled"), (ix + 12, y + 260))
    T(P, (ix, y + 330), status or "Click a node to select it here.", 13, C["success"] if status else C["caption"], bool(status), "lm")
    hline(P, ix, y + 348, iw)
    T(P, (ix, y + 370), "How the tree works", 15, C["panelTitle"], True, "lm")
    lines = ["Each arm spends its own points,", "earned at rebirth from that skill.",
             "8 levels in a row open the next row.", "The last node of an arm is a keystone.",
             "Hover the Nexus for what a rebirth", "gives; click it to rebirth."]
    for k, s in enumerate(lines):
        T(P, (ix, y + 394 + k * 19), s, 13, C["text"], False, "lm")
    hline(P, ix, y + 514, iw)
    end = legend_block(P, ix + 4, y + 536, iw)
    assert end < y + h - 8, ("right panel overflow", end, y + h)


def main_page(sel=(1, 1, 0), hover=None, nexus_state="asleep", status=None):
    P = frame_page(PW, PH, "Rebirth - Nexus of the Void")
    left_panel(P, nexus_awake="awake" in nexus_state)
    P.alpha_composite(tree(selected=sel, hover=hover, nexus_state=nexus_state), (CV[0], CV[1]))
    right_panel(P, sel, status)
    return P


# ====================================================================== tooltips
TIP_W, TIP_PAD = 400, 16          # vanilla TextTooltipStyle MaxWidth 400 (tools/skyyui.py TOOLTIP_MAX_W)


def tip_box(lines):
    """lines: (kind, *args) -> a tooltip picture. kinds: title, sub, head, req, kv, text, rule, gap, cta"""
    H = {"title": 26, "sub": 20, "head": 24, "req": 22, "kv": 21, "kv2": 21, "text": 20, "rule": 13, "gap": 6, "cta": 26}
    h = TIP_PAD * 2 + sum(H[l[0]] for l in lines)
    L = Image.new("RGBA", (TIP_W, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    d.rounded_rectangle((0, 0, TIP_W - 1, h - 1), 6, fill=col("#0a101c(0.98)"), outline=col("#E8A93B(0.6)"), width=1)
    d.rounded_rectangle((2, 2, TIP_W - 3, h - 3), 5, outline=col("#000000(0.6)"), width=1)
    x, y, iw = TIP_PAD, TIP_PAD, TIP_W - 2 * TIP_PAD
    for l in lines:
        k = l[0]
        hh = H[k]
        m = y + hh // 2
        if k == "title":
            T(L, (x, m), l[1], 18, l[2] if len(l) > 2 else "#d8c8ff", True, "lm")
        elif k == "sub":
            T(L, (x, m), l[1], 13, C["caption"], False, "lm")
        elif k == "head":
            T(L, (x, m + 2), l[1], 13, C["gold"], True, "lm")
        elif k == "req":
            tick(L, x, m - 7, l[1])
            T(L, (x + 22, m), fit(l[2], 14, False, iw - 120), 14, C["rowName"], False, "lm")
            T(L, (x + iw, m), l[3], 14, {"ok": C["success"], "no": C["error"], "warn": C["warning"]}[l[1]], True, "rm")
        elif k == "kv":
            T(L, (x, m), l[1], 14, C["text"], False, "lm")
            T(L, (x + iw, m), l[2], 14, l[3] if len(l) > 3 else C["rowName"], True, "rm")
        elif k == "kv2":   # two key/value pairs side by side (points per arm)
            half = (iw - 24) // 2
            for n, (a, b, c_, sub) in enumerate((l[1], l[2])):
                xx = x + n * (half + 24)
                ImageDraw.Draw(L).rounded_rectangle((xx, m - 5, xx + 9, m + 4), 2, fill=col(c_))
                T(L, (xx + 16, m), a, 14, C["rowName"], False, "lm")
                if sub:
                    T(L, (xx + half - 24, m), sub, 12, C["caption"], False, "rm")
                T(L, (xx + half, m), b, 14, C["gold"] if b != "0" else C["caption"], True, "rm")
        elif k == "text":
            T(L, (x, m), fit(l[1], 13, False, iw), 13, l[2] if len(l) > 2 else C["text"], False, "lm")
        elif k == "rule":
            hline(L, x, m, iw, "#E8A93B(0.30)")
        elif k == "cta":
            T(L, (TIP_W // 2, m), l[1], 15, l[2], True, "mm")
        y += hh
    return L


def nexus_tip(met):
    nxt = REBIRTHS + 1
    cls = CAP_NOW if met else CLASS_NOW
    lines = [("title", "Nexus of the Void"), ("sub", "Rebirth %d of %d  -  the void imprints your soul" % (nxt, MAX_REBIRTHS)),
             ("rule",), ("head", "REQUIREMENTS"),
             ("req", "ok" if met else "no", "Class level", "%d / %d" % (cls, CAP_NOW)),
             ("req", "ok", "Rebirths done", "%d / %d" % (REBIRTHS, MAX_REBIRTHS)),
             ("req", "ok", "No open Bazaar or AH orders", "OK"),
             ("req", "ok", "Not in combat", "OK"),
             ("req", "ok" if met else "warn", "Mailbox empty", "OK" if met else "3 items"),
             ("rule",), ("head", "WHAT YOU GET" + ("" if met else "  (at Class %d)" % CAP_NOW))]
    for a in range(0, 8, 2):
        pair = []
        for b in (a, a + 1):
            arm = ARMS[b]
            g = GAIN[arm[0]]
            pair.append((arm[0], str(g), arm[1], "needs 25 %" if g == 0 else ""))
        lines.append(("kv2", pair[0], pair[1]))
    bank = min(1.0, 0.25 * math.log10(1 + BANK_BAL / 100000.0))
    lines += [("gap",),
              ("kv", "All stats", "+3 %%  (%d -> %d %%)" % (STAT_NOW, STAT_NOW + 3), C["success"]),
              ("kv", "Caps", "Class %d -> %d, skills +10" % (CAP_NOW, CAP_NOW + 10)),
              ("kv", "Bank interest", "+%.2f %%  (%s at reset)" % (bank, "3.2M"), C["success"]),
              ("kv", "Title", "Void-Touched VII", C["gold"])]
    best = max(ARMS[1:], key=lambda a: a[3])
    lines += [("text", "Next %s point in %s XP" % (best[0], format(next_point_xp(best[2], best[3], best[4]), ",")), C["info"]),
              ("rule",)]
    if met:
        lines.append(("cta", "Click the Nexus to rebirth", C["success"]))
    else:
        lines.append(("cta", "Reach Class %d to wake the Nexus" % CAP_NOW, C["warning"]))
    return tip_box(lines)


def node_tip(sel, locked=False):
    i, row, j = sel
    arm = ARMS[i]
    st = ST[arm[0]]
    name, what, fmt, per = NODE_NAMES[(arm[0], row, j)]
    lv = arm[6][row][j]
    if locked:
        lines = [("title", name, arm[1]), ("sub", "%s arm - Row %d - locked" % (arm[0], row + 1)), ("rule",),
                 ("text", what), ("kv", "At level 1", fmt % per), ("rule",),
                 ("req", "no", "Levels in Row %d" % row, "%d / %d" % (st["spent"][row - 1], GATE)),
                 ("text", "Spend %d more levels in Row %d to open this row." % (GATE - st["spent"][row - 1], row), C["caption"])]
        return tip_box(lines)
    ok = arm[5] >= st["cost"]
    lines = [("title", name, arm[1]), ("sub", "%s arm - Row %d - node %d" % (arm[0], row + 1, j + 1)), ("rule",),
             ("text", what), ("kv", "Level", "%d / %d" % (lv, ROW_MAX[row])),
             ("kv", "Now", fmt % (per * lv), C["success"]), ("kv", "Next level", fmt % (per * (lv + 1)), C["info"]),
             ("rule",),
             ("kv", "Cost", "%d %s points" % (st["cost"], arm[0])),
             ("kv", "You have", str(arm[5]), C["gold"] if ok else C["error"]),
             ("cta", "Click to select, then Buy" if ok else "Not enough %s points" % arm[0], C["success"] if ok else C["error"])]
    return tip_box(lines)


def plain_tip(met):
    """The vanilla TextTooltip fallback: ONE label, FontSize 16, wrap, MaxWidth 400, Padding 24 (tools/skyyui.py line 2352)."""
    rows = ["Nexus of the Void - Rebirth %d" % (REBIRTHS + 1), "",
            ("OK" if met else "NO") + "  Class level %d / %d" % (CAP_NOW if met else CLASS_NOW, CAP_NOW),
            "OK  Rebirths %d / %d" % (REBIRTHS, MAX_REBIRTHS), "OK  No open orders, not in combat", "",
            "You get: Class %d, Mining %d, Foraging %d," % (GAIN["Class"], GAIN["Mining"], GAIN["Foraging"]),
            "Farming %d, Fishing %d, Alchemy %d, Smithing %d," % (GAIN["Farming"], GAIN["Fishing"], GAIN["Alchemy"], GAIN["Smithing"]),
            "Cooking %d points. +3 %% stats, caps +10." % GAIN["Cooking"], "",
            "Click to rebirth." if met else "Reach Class %d first." % CAP_NOW]
    lh = 21
    h = 24 * 2 + len(rows) * lh
    L = Image.new("RGBA", (TIP_W, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    d.rounded_rectangle((0, 0, TIP_W - 1, h - 1), 8, fill=col("#1c2230(0.96)"), outline=col("#5a6474"), width=2)
    for k, s in enumerate(rows):
        assert tw(s, 16) <= TIP_W - 48, ("plain tooltip line too long", s)
        T(L, (24, 24 + k * lh + lh // 2), s, 16, "#e6e6e6", False, "lm")
    return L


# ====================================================================== confirm step
MW, MH = 900, 610


def confirm_modal(count=2, hover_yes=False):
    M = frame_page(MW, MH, "Rebirth %d - touch the Nexus?" % (REBIRTHS + 1))
    T(M, (MW // 2, 78), "The void imprints your soul. Levels and coins reset; your progress stays.", 14, C["text"], False, "mm")
    # two columns
    cy, ch = 96, 236
    cols = [("RESETS", C["error"], ["Class level %d -> 1" % CAP_NOW, "Every skill level and its XP",
                                    "Coins and bank (3.2M) -> bank deal", "Lifelong tools -> Crude, level 0",
                                    "   (rarity and stats are kept)", "Gathering armor -> base tier"]),
            ("YOU KEEP", C["success"], ["Island and shard upgrades", "Collections (counts and recipes)",
                                        "Items, gear, vault, accessories", "Pets, cosmetics, titles",
                                        "Rebirth tree levels + unspent points", "Quests and zones"])]
    cw = (MW - 48 - 16) // 2
    for n, (head, hc, items) in enumerate(cols):
        x = 24 + n * (cw + 16)
        M.alpha_composite(nine("Panel", cw, ch, 12), (x, cy))
        T(M, (x + 16, cy + 22), head, 15, hc, True, "lm")
        hline(M, x + 16, cy + 38, cw - 32)
        for k, s in enumerate(items):
            yy = cy + 58 + k * 28
            if not s.startswith("   "):
                d = ImageDraw.Draw(M)
                d.rounded_rectangle((x + 18, yy - 3, x + 24, yy + 3), 1, fill=col(hc))
            assert tw(s.strip(), 14) <= cw - 50, ("confirm item too long", s)
            T(M, (x + 34, yy), s.strip(), 14, C["rowName"] if not s.startswith("   ") else C["caption"], False, "lm")
    # gains
    gy, gh = cy + ch + 12, 158
    M.alpha_composite(nine("Panel", MW - 48, gh, 12), (24, gy))
    T(M, (40, gy + 22), "YOU GAIN", 15, C["gold"], True, "lm")
    T(M, (MW - 40, gy + 22), "points go to each arm of the tree", 13, C["caption"], False, "rm")
    chw, chh, gap = (MW - 48 - 32 - 3 * 10) // 4, 34, 10
    for k, arm in enumerate(ARMS):
        x = 40 + (k % 4) * (chw + gap)
        y = gy + 42 + (k // 4) * (chh + 8)
        well = nine("PanelInset", chw, chh, 8)
        M.alpha_composite(well, (x, y))
        d = ImageDraw.Draw(M)
        d.rounded_rectangle((x + 10, y + 12, x + 20, y + 22), 2, fill=col(arm[1]))
        T(M, (x + 28, y + 17), arm[0], 14, C["rowName"], True, "lm")
        g = GAIN[arm[0]]
        T(M, (x + chw - 10, y + 17), "+%d" % g, 16, C["gold"] if g else C["caption"], True, "rm")
    bank = min(1.0, 0.25 * math.log10(1 + BANK_BAL / 100000.0))
    extras = "+3 %% all stats (%d -> %d %%)    Caps +10    Bank +%.2f %%    Title Void-Touched VII" % (STAT_NOW, STAT_NOW + 3, bank)
    assert tw(extras, 14, True) <= MW - 80
    T(M, (MW // 2, gy + gh - 20), extras, 14, C["success"], True, "mm")
    # footer: note + buttons
    by = MH - 16 - 40
    note = ("Read the lists - Rebirth unlocks in %d s." % count) if count else "This cannot be undone. Items are never deleted."
    T(M, (MW // 2, by - 22), note, 13, C["warning"] if count else C["caption"], bool(count), "mm")
    M.alpha_composite(button("secondary", 220, 40, "Not yet", 15), (44, by))
    if count:
        M.alpha_composite(button("secondary", 280, 40, "Rebirth (%d)" % count, 15, "_Disabled"), (MW - 44 - 280, by))
    else:
        M.alpha_composite(button("danger", 280, 40, "Rebirth %d" % (REBIRTHS + 1), 15, "_Hovered" if hover_yes else ""),
                          (MW - 44 - 280, by))
    assert gy + gh + 8 < by - 34, ("confirm overflow", gy + gh, by)
    return M


def hold_button(frac, w=280, h=40):
    """Hold-to-confirm variant (UNVERIFIED: needs press / release events): the fill grows while the mouse is held 1.5 s."""
    b = button("danger", w, h, "", 15)
    fill = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    fw = int(round((w - 8) * frac))
    if fw > 0:
        ImageDraw.Draw(fill).rounded_rectangle((4, 4, 4 + fw, h - 5), 4, fill=col("#E8A93B(0.55)"))
    b.alpha_composite(fill)
    T(b, (w // 2, h // 2), "Hold to rebirth" if frac < 1 else "Rebirth!", 15, C["white"], True, "mm")
    return b


# ====================================================================== fallback: tabs per arm + a row ladder (verified page size)
FW_, FH_ = 1120, 870
FCOL_W, FCOL_GAP = 136, 22
FCARD_H, FCARD_GAP = 120, 10


def node_card(arm, row, j, w, h, selected=False):
    """One node as a card (fallback ladder). Row / Row_Selected texture; not open = the same card at 55 %."""
    kind, lv = node_kind(arm, row, j)
    st = ST[arm[0]]
    c = nine("Row_Selected" if selected else "Row", w, h, 8)
    if kind != "open":
        c = fade(c, 0.55)
    names = ["Deep Veins", "Stone Sense", "Quick Pick", "Ore Echo", "Dust Magnet", "Shard Pulse", "Vein Walker", "Gem Eye",
             "Heart of Stone", "Cave Sense", "Void Drill"]
    nm, what, fmt, per = NODE_NAMES.get((arm[0], row, j), (names[[0, 3, 6, 8, 10][row] + j], "", "+%d %% " + arm[0] + " XP", 2))
    T(c, (10, 17), fit(nm, 14, True, w - 20), 14, C["rowName"] if kind == "open" else C["disabled"], True, "lm")
    maxlv = ROW_MAX[row]
    if kind == "open":
        pw = (w - 20 - (maxlv - 1) * 4) // maxlv
        for k in range(maxlv):
            lit = k < lv
            R(c, (10 + k * (pw + 4), 34, pw, 6), ("#E8A93B" if lv == maxlv else arm[1]) if lit else "#2b3446")
        T(c, (10, 58), "Level %d / %d" % (lv, maxlv), 13, C["white"] if lv else C["text"], True, "lm")
        T(c, (10, 80), fit(fmt % (per * max(lv, 1)), 12, False, w - 20), 12, C["success"] if lv else C["caption"], False, "lm")
        if lv == maxlv:
            T(c, (10, 102), "MAX", 12, C["gold"], True, "lm")
        else:
            T(c, (10, 102), "Next: %d pts" % st["cost"], 12, C["gold"] if arm[5] >= st["cost"] else C["caption"], False, "lm")
    else:
        lock_glyph(c, w // 2, 54, "#5a6476")
        T(c, (w // 2, 82), "Locked", 13, C["disabled"], True, "mm")
        if kind == "gate":
            T(c, (w // 2, 102), "Row %d: %d / %d" % (row, st["gate"], GATE), 12, C["caption"], False, "mm")
    return c


def fallback_page(arm_i=1, nexus_state="asleep"):
    P = frame_page(FW_, FH_, "Rebirth - Nexus of the Void")
    tabw = (FW_ - 48 - 7 * 4) // 8
    for k, arm in enumerate(ARMS):
        name = "Tab_Selected" if k == arm_i else "Tab"
        tb = nine(name, tabw, 44, 20, 12)
        lab = arm[0]
        pts = str(arm[5])
        wl, wp = tw(lab, 15, True), tw(pts, 15, True)
        x0 = (tabw - (wl + 6 + wp)) / 2
        T(tb, (x0, 22), lab, 15, C["white"] if k == arm_i else C["button2Text"], True, "lm")
        T(tb, (x0 + wl + 6, 22), pts, 15, C["gold"] if arm[5] >= ST[arm[0]]["cost"] else C["caption"], True, "lm")
        ImageDraw.Draw(tb).rectangle((14, 40, tabw - 15, 41), fill=col(arm[1], 0.9 if k == arm_i else 0.45))
        assert wl + 6 + wp <= tabw - 16
        P.alpha_composite(tb, (24 + k * (tabw + 4), 66))
    # left: fixed Nexus column
    lx, ly, lw, lh = 24, 122, 260, FH_ - 24 - 122
    P.alpha_composite(nine("Panel", lw, lh, 12), (lx, ly))
    P.alpha_composite(nexus(nexus_state), (lx + lw // 2 - 100, ly + 12))
    T(P, (lx + lw // 2, ly + 206), "Rebirth %d" % (REBIRTHS + 1), 16, C["panelTitle"], True, "mm")
    T(P, (lx + lw // 2, ly + 228), "Hover for details, click to rebirth", 12, C["caption"], False, "mm")
    left_panel(P, "awake" in nexus_state, compact=True, box=(lx, ly + 238, lw, 0))
    hy = ly + 238 + 76 + 6 * 24 + 22
    T(P, (lx + 16, hy), "How the tree works", 15, C["panelTitle"], True, "lm")
    for k, s_ in enumerate(["Each arm spends its own points,", "earned at rebirth from that skill.",
                            "8 levels in a row open the next.", "Prices rise with each level", "bought in an arm.",
                            "Row 5 is the keystone."]):
        T(P, (lx + 16, hy + 24 + k * 19), s_, 13, C["text"], False, "lm")
    assert hy + 24 + 6 * 19 < ly + lh - 16 - 36 - 10
    P.alpha_composite(button("secondary", lw - 32, 36, "Back", 15), (lx + 16, ly + lh - 16 - 36))
    # right: the arm ladder
    arm = ARMS[arm_i]
    st = ST[arm[0]]
    rx, ry, rw, rh = 300, 122, FW_ - 24 - 300, FH_ - 24 - 122
    P.alpha_composite(nine("Panel", rw, rh, 12), (rx, ry))
    T(P, (rx + 16, ry + 22), "%s arm" % arm[0], 16, arm[1], True, "lm")
    T(P, (rx + rw - 16, ry + 22), "%d points to spend  -  next level costs %d" % (arm[5], st["cost"]), 14, C["gold"], True, "rm")
    T(P, (rx + 16, ry + 44), "Rows open from the Nexus outward: 8 levels in a row open the next.", 13, C["caption"], False, "lm")
    total_w = 5 * FCOL_W + 4 * FCOL_GAP
    cx0 = rx + (rw - total_w) // 2
    top = ry + 70
    cards_top = top + 46
    col_h = 3 * FCARD_H + 2 * FCARD_GAP
    centres = []
    for row in range(5):
        x = cx0 + row * (FCOL_W + FCOL_GAP)
        n = len(LAT[row])
        opened = row < st["open"]
        T(P, (x + FCOL_W // 2, top + 10), "Row %d" % (row + 1) + ("  (keystone)" if row == 4 else ""), 14,
          C["panelTitle"] if opened else C["disabled"], True, "mm")
        if row == 0:
            sub, sc = "%d levels" % st["spent"][0], C["caption"]
        elif opened:
            sub, sc = "open  -  %d levels" % st["spent"][row], C["success"]
        else:
            sub, sc = "needs 8 in Row %d" % row, C["caption"]
        T(P, (x + FCOL_W // 2, top + 30), sub, 12, sc, False, "mm")
        ys = []
        for j in range(n):
            y = cards_top + (col_h - (n * FCARD_H + (n - 1) * FCARD_GAP)) // 2 + j * (FCARD_H + FCARD_GAP)
            P.alpha_composite(node_card(arm, row, j, FCOL_W, FCARD_H, selected=(row == 1 and j == 0)), (x, y))
            ys.append(y + FCARD_H // 2)
        centres.append((x, ys))
    # connectors (axis-aligned 2 px Groups only): out of each column's middle -> vertical bus -> into each card
    for row in range(4):
        x, ys = centres[row]
        nx, nys = centres[row + 1]
        lit = row + 1 < st["open"]
        c_ = col(arm[1]) if lit else col("#2c3448")
        d = ImageDraw.Draw(P)
        bx = x + FCOL_W + FCOL_GAP // 2
        allys = ys + nys
        d.rectangle((bx - 1, min(allys), bx, max(allys)), fill=c_)
        for y in ys:
            d.rectangle((x + FCOL_W, y - 1, bx, y), fill=c_)
        for y in nys:
            d.rectangle((bx, y - 1, nx, y), fill=c_)
    # selected node strip
    sy = cards_top + col_h + 24
    sh = 150
    P.alpha_composite(nine("PanelInset", rw - 32, sh, 8), (rx + 16, sy))
    name, what, fmt, per = NODE_NAMES[("Mining", 1, 0)]
    lv = arm[6][1][0]
    P.alpha_composite(node_img(arm[1], lv, 5, "open", selected=True), (rx + 26, sy + 12))
    T(P, (rx + 86, sy + 28), name, 17, C["white"], True, "lm")
    T(P, (rx + 86, sy + 50), "%s - Row 2  -  %s" % (arm[0], what), 13, C["caption"], False, "lm")
    rows = [("Level", "%d / 5" % lv, None), ("Now", fmt % (per * lv), C["success"]), ("Next level", fmt % (per * (lv + 1)), C["info"])]
    prop_rows(P, rx + 32, sy + 84, 300, rows, 14, 22)
    rows2 = [("Cost", "%d %s points" % (st["cost"], arm[0]), None), ("You have", str(arm[5]), C["gold"])]
    prop_rows(P, rx + 372, sy + 84, 200, rows2, 14, 22)
    P.alpha_composite(button("primary", 170, 40, "Buy level %d" % (lv + 1), 15), (rx + rw - 32 - 170, sy + sh - 52))
    T(P, (rx + 16, sy + sh + 22), "+  Void-Forged Pick level 3 bought - 7 Mining points spent.", 14, C["success"], True, "lm")
    assert sy + sh + 40 < ry + rh, ("fallback overflow", sy + sh, ry + rh)
    return P


# ====================================================================== screens
def screen(page, ox=PX, oy=PY, caption=None):
    img = world()
    R(img, (0, 0, SW, SH), "#000000(0.45)")         # the world behind a page, dimmed (client look UNVERIFIED)
    img.alpha_composite(page, (ox, oy))
    if caption:
        tag(img, ox, max(6, oy - 34), caption)
    return img


def annotate(img):
    """Boxes, sizes and radii on top of the idle page."""
    def box(b, lab, colr="#7fd0ff"):
        x, y, w, h = b
        dashed(img, (PX + x, PY + y, w, h), colr, 2)
        t = "%s  %d,%d  %d x %d" % (lab, x, y, w, h)
        tag(img, PX + x + w - 8 - int(tw(t, 11, True)) - 12, PY + y + 6, t, "#08263a(0.92)", "#bfe8ff", 11)
    box(LP, "Left panel")
    box(CV, "Tree canvas (PanelInset)")
    box(RP, "Right panel")
    d = ImageDraw.Draw(img)
    cx, cy = PX + TCX, PY + TCY
    for k, r in enumerate(ROW_R):
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=col("#7fd0ff(0.55)"), width=1)
        a = math.radians(-112.5)
        tag(img, int(cx + math.cos(a) * r - 24), int(cy + math.sin(a) * r - 10), "R%d %d" % (k + 1, r), "#08263a(0.92)", "#bfe8ff", 11)
    d.ellipse((cx - NEXUS_R, cy - NEXUS_R, cx + NEXUS_R, cy + NEXUS_R), outline=col("#ffe2a8"), width=1)
    d.ellipse((cx - CHIP_R, cy - CHIP_R, cx + CHIP_R, cy + CHIP_R), outline=col("#ffe2a8(0.5)"), width=1)
    tag(img, PX + 10, PY + PH + 30, "Nexus button 144 x 144 (plate r %d, gold circle), centre %d,%d page = %d,%d screen.  Arm chips on r %d "
        "(faint gold circle), 22 high, 8 px side padding.  Blue circles = row radii R1-R5." % (NEXUS_R, TCX, TCY, PX + TCX, PY + TCY, CHIP_R),
        "#3a2808(0.95)", "#ffe2a8", 12)
    tag(img, PX + 10, PY + PH + 4, "Page 1600 x 952 at %d,%d (root = Width / Height only, centred). Nodes 36, keystone 44, "
        "row gaps 55 / 55 / 54 / 48, sideways 48 (3 nodes) / 27 (2 nodes). Arms every 45 degrees, Class at the top." % (PX, PY),
        "#08263a(0.95)", "#bfe8ff", 12)


def check_1366(page_img):
    full = screen(page_img)
    a = full.resize((1366, 768), Image.LANCZOS)
    b = world().resize((1366, 768), Image.LANCZOS)
    R(b, (0, 0, 1366, 768), "#000000(0.45)")
    bx, by = (1366 - PW) // 2, (768 - PH) // 2      # centred, overflowing
    b.alpha_composite(page_img.crop((-bx, -by, -bx + 1366, -by + 768)), (0, 0))
    lay = Image.new("RGBA", (1366, 768), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lay)
    dl.rectangle((0, 0, 1365, 767), outline=(255, 48, 48, 255), width=4)
    b.alpha_composite(lay)
    tag(b, 20, 20, "page 1600 x 952 > screen: %d px cut on each side, %d px top and bottom" % (-bx, -by), "#5a1818(0.92)", "#ffd0d0", 13)
    out = Image.new("RGBA", (1366 * 2 + 60, 768 + 150), col("#10161f"))
    out.alpha_composite(a, (20, 96))
    out.alpha_composite(b, (1366 + 40, 96))
    s = 768 / 1080.0
    T(out, (20, 18), "1366 x 768 CHECK - the main /rebirth page", 18, "#ffe2a8", True)
    T(out, (20, 48), "A  The client scales the UI to the screen height (x %.3f): page %d x %d fits (%d px spare each side). Smallest text 12 -> %.1f px, "
      "node digit 15 -> %.1f px, node 36 -> %.0f px." % (s, round(PW * s), round(PH * s), (1366 - round(PW * s)) // 2, 12 * s, 15 * s, 36 * s),
      13, "#e6e6e6")
    T(out, (20, 70), "B  The client does NOT scale (worst case, 1 UI = 1 px): the page is larger than the screen - true of every page we have "
      "(1120 x 930). The fallback page (1120 x 870) fits the width but not the height either.", 13, "#e6e6e6")
    T(out, (20, 96 + 768 + 16), "A: same as a_idle_1080p.png, scaled down.", 12, "#ffd0a0", True)
    T(out, (1366 + 40, 96 + 768 + 16), "B: centred page, cut at the red line.", 12, "#ffd0a0", True)
    return out


def states_crop():
    W, H = 1840, 900
    img = Image.new("RGBA", (W, H), col("#121a27"))
    T(img, (20, 14), "STATES - 1:1 unless marked 2x", 18, "#ffe2a8", True)
    # Nexus states
    T(img, (20, 56), "Nexus button (144 x 144 hit area; layer 200 x 200 with glow)", 14, "#ffe2a8", True)
    for k, (st, lab) in enumerate([("asleep", "asleep (class not at cap)"), ("hover-asleep", "hover, asleep"),
                                   ("awake", "awake (all met): glows gold"), ("hover-awake", "hover, awake"),
                                   ("pressed", "pressed (icon 120)")]):
        x = 20 + k * 210
        img.alpha_composite(nexus(st), (x, 72))
        T(img, (x + 100, 282), lab, 12, "#d8d8d8", False, "mm")
    # node states at 2x
    T(img, (1080, 56), "Nodes at 2x (36 px; keystone 44)", 14, "#ffe2a8", True)
    items = [(node_img("#4aa6e8", 0, 5, "locked"), "locked"), (node_img("#4aa6e8", 0, 5, "gate", gate_text="5/8"), "next row 5/8"),
             (node_img("#4aa6e8", 0, 5, "open"), "open 0"), (node_img("#4aa6e8", 2, 5, "open"), "level 2"),
             (node_img("#4aa6e8", 4, 5, "open"), "level 4"), (node_img("#4aa6e8", 5, 5, "open"), "maxed"),
             (node_img("#4aa6e8", 3, 5, "open", hover=True), "hover"), (node_img("#4aa6e8", 3, 5, "open", selected=True), "selected"),
             (node_img("#e8606a", 0, 1, "locked", key=True), "keystone locked"), (node_img("#e8606a", 0, 1, "open", key=True), "keystone open"),
             (node_img("#e8606a", 1, 1, "open", key=True), "keystone max")]
    for k, (n, lab) in enumerate(items):
        x = 1080 + (k % 6) * 124
        y = 76 + (k // 6) * 136
        img.alpha_composite(n.resize((104, 104), Image.NEAREST), (x, y))
        T(img, (x + 52, y + 112), lab, 12, "#d8d8d8", False, "mm")
    # confirm button states
    y0 = 330
    T(img, (20, y0), "Confirm button (280 x 40): A = 3 s count (recommended), B = hold to confirm (UNVERIFIED: needs press / release events)",
      14, "#ffe2a8", True)
    for k, cnt in enumerate([3, 2, 1]):
        img.alpha_composite(button("secondary", 280, 40, "Rebirth (%d)" % cnt, 15, "_Disabled"), (20 + k * 300, y0 + 22))
    img.alpha_composite(button("danger", 280, 40, "Rebirth 7", 15), (920, y0 + 22))
    img.alpha_composite(button("danger", 280, 40, "Rebirth 7", 15, "_Hovered"), (1220, y0 + 22))
    for k, lab in enumerate(["A 0 s - disabled", "A 1 s", "A 2 s", "A 3 s - enabled", "A hover"]):
        T(img, ([20, 320, 620, 920, 1220][k] + 140, y0 + 76), lab, 12, "#d8d8d8", False, "mm")
    for k, f in enumerate([0.0, 0.6, 1.0]):
        img.alpha_composite(hold_button(f), (20 + k * 300, y0 + 98))
        T(img, (20 + k * 300 + 140, y0 + 152), ["B not held", "B held 0.9 of 1.5 s", "B done -> rebirth"][k], 12, "#d8d8d8", False, "mm")
    # tooltips
    y1 = 520
    T(img, (20, y1), "Plain-text fallback (vanilla TextTooltip)", 14, "#ffe2a8", True)
    T(img, (20, y1 + 18), "one 16 px label, max 400 wide, padding 24", 12, "#d8d8d8")
    img.alpha_composite(plain_tip(False), (20, y1 + 40))
    T(img, (460, y1), "Locked node tooltip", 14, "#ffe2a8", True)
    img.alpha_composite(node_tip((2, 2, 0), locked=True), (460, y1 + 22))
    T(img, (900, y1), "Arm colours (placeholders, Q2)", 14, "#ffe2a8", True)
    for k, arm in enumerate(ARMS):
        x = 900 + (k % 2) * 200
        y = y1 + 30 + (k // 2) * 34
        ImageDraw.Draw(img).rounded_rectangle((x, y, x + 22, y + 22), 4, fill=col(arm[1]))
        T(img, (x + 32, y + 11), "%s  %s" % (arm[0], arm[1]), 13, "#e6e6e6", False, "lm")
    T(img, (1320, y1), "Gain text rule", 14, "#ffe2a8", True)
    rules = ["Points = floor(B x sqrt(r)), r = run XP / XP to cap.", "B = 12 for Class, 8 for skills.",
             "r under 0.25 pays 0 ('needs 25 %').", "Level cost = ceil(1.08 ^ k), k = levels", "already bought in that arm."]
    for k, s in enumerate(rules):
        T(img, (1320, y1 + 30 + k * 20), s, 13, "#e6e6e6", False, "la")
    return img


def save(img, name):
    img.convert("RGB").save(os.path.join(HERE, name), "PNG", optimize=False)


def main():
    probs, mind = check_tree()
    print("tree layout problems:", probs if probs else "none", "| closest node gap (px):", round(mind, 1))
    assert not probs
    idle = main_page()
    save(screen(idle, caption="(a) /rebirth - idle: the Nexus sleeps (Class %d / %d)" % (CLASS_NOW, CAP_NOW)), "a_idle_1080p.png")
    ann = screen(idle)
    annotate(ann)
    save(ann, "a_layout_annotated_1080p.png")
    # hover, not met
    P = main_page(nexus_state="hover-asleep")
    img = screen(P, caption="(b) hover the Nexus - a requirement is NOT met")
    cx, cy = PX + TCX, PY + TCY
    tip = nexus_tip(False)
    tx, ty = cx + NEXUS_R + 16, min(SH - 8 - tip.height, max(8, cy + 12 - tip.height // 2))
    img.alpha_composite(tip, (tx, ty))
    cursor(img, cx + 30, cy + 22)
    save(img, "b_hover_notmet_1080p.png")
    print("nexus tooltip (not met):", tip.size, "at", (tx, ty))
    # hover, met
    P = main_page(nexus_state="hover-awake")
    img = screen(P, caption="(c) hover the Nexus - every requirement met (the Nexus is awake)")
    tip = nexus_tip(True)
    tx, ty = cx + NEXUS_R + 16, min(SH - 8 - tip.height, max(8, cy + 12 - tip.height // 2))
    img.alpha_composite(tip, (tx, ty))
    cursor(img, cx + 30, cy + 22)
    save(img, "c_hover_met_1080p.png")
    # confirm
    P = main_page(nexus_state="awake")
    img = screen(P, caption="(d) click -> confirm step (count 2 s left)")
    R(img, (0, 0, SW, SH), "#000000(0.55)")
    M = confirm_modal(count=2)
    img.alpha_composite(M, ((SW - MW) // 2, (SH - MH) // 2))
    save(img, "d_confirm_1080p.png")
    img2 = Image.new("RGBA", (MW + 40, MH + 60), col("#121a27"))
    T(img2, (20, 14), "Confirm step at 1:1 after the 3 s count (Rebirth enabled, hovered)", 14, "#ffe2a8", True)
    img2.alpha_composite(confirm_modal(count=0, hover_yes=True), (20, 40))
    save(img2, "d_confirm_ready_crop.png")
    # node tooltip
    sel = (1, 1, 0)
    hov = (6, 0, 1)
    P = main_page(sel=sel, hover=hov, status="+  Void-Forged Pick level 3 bought.")
    img = screen(P, caption="(e) hover a node (Smithing, Row 1) - Void-Forged Pick is selected on the right")
    nx_, ny_ = node_pos(*hov)
    tip = node_tip(hov)
    sx, sy = PX + int(nx_) + 22, PY + int(ny_) + 18
    if sx + tip.width > SW - 8:
        sx = PX + int(nx_) - 22 - tip.width
    sy = min(sy, SH - 8 - tip.height)
    img.alpha_composite(tip, (sx, sy))
    cursor(img, PX + nx_ + 4, PY + ny_ + 2)
    save(img, "e_node_tooltip_1080p.png")
    # fallback
    F = fallback_page()
    save(screen(F, (SW - FW_) // 2, (SH - FH_) // 2, caption="(f) FALLBACK: one tab per arm, rows as a ladder outward from the Nexus "
                "(1120 x 870, inside the verified 1120 x 952)"), "f_fallback_tabs_1080p.png")
    save(check_1366(idle), "g_check_1366x768.png")
    save(states_crop(), "h_states_crop.png")


if __name__ == "__main__":
    main()
