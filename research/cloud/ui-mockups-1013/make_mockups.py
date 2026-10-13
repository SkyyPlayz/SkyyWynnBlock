#!/usr/bin/env python3
"""SkyWynn HUD + Settings mockups (cloud draft 2026-10-13, paper only - nothing built).

Draws, next to this script (research/cloud/ui-mockups-1013/):
  a_quest_1080p.png        a_quest_crop.png         QUEST WIDGET (always-on HUD, next 1-3 tasks, progress bar, where to go)
  b_feed_1080p.png         b_feed_crop.png          NOTIFICATION FEED (stacking cards bottom-left, 3 opacity stages, merges)
  c_skillxp_1080p.png      c_skillxp_crop.png       skill-XP flash on the HUD Skills list (before / during / after)
  d_settings_1080p.png     d_settings_crop.png      per-player Settings -> Messages tab (Chat / Feed / Off per message type)
  e_layout_1080p.png       e_layout_clean_1080p.png the whole proposed 1080p HUD, annotated + clean
  f_check_1366x768.png                              the 1366 x 768 check (A uniformly scaled, B unscaled corner anchors)

Style source: the SKY WINDOW kit (art/ui-kit-sky/Common/UI/Custom/SkyyKit/*.png - our own art, 9-sliced here exactly like the
client does: @2x texture, Border in UI units, 1 UI = 1 px at 1080p), colours from tools/skyyui.py COLOR, HUD box look from
SkyyHud/build_skyyhud_0.3.18.py (Background #0b1524(0.72), text #eaf6ff, font 12, 20 px rows).
Fonts: Liberation Sans stands in for the game's Nunito Sans (Default) / Lexend Bold (Secondary); the game font is a bit wider.
Vanilla HUD areas are ESTIMATES (no game files in the cloud) - shaded red and marked "est." - see Layout-Spec.md.

Deterministic: no clock, no unseeded randomness; two runs give the same bytes.
Run: python3 research/cloud/ui-mockups-1013/make_mockups.py
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
KIT = os.path.join(REPO, "art", "ui-kit-sky", "Common", "UI", "Custom", "SkyyKit")
FONT_DIR = "/usr/share/fonts/truetype/liberation"
FONT_R = os.path.join(FONT_DIR, "LiberationSans-Regular.ttf")
FONT_B = os.path.join(FONT_DIR, "LiberationSans-Bold.ttf")

SW, SH = 1920, 1080

# ------------------------------------------------------------------ kit colours (tools/skyyui.py COLOR, copied)
C = {
    "text": "#96a9be", "white": "#ffffff", "title": "#b4c8c9", "panelTitle": "#afc2c3", "caption": "#878e9c",
    "captionLight": "#5a6a7a", "rowName": "#d6e4ee", "rowSub": "#7f93a6", "gold": "#E8A93B", "buttonText": "#bfcdd5",
    "button2Text": "#bdcbd3", "value": "#b7cedd", "error": "#ff6b6b", "success": "#39f493", "warning": "#ffcc00",
    "info": "#7caacc", "disabled": "#797b7c", "progressGreen": "#7caa4a",
    # SkyyHud 0.3.18 widget look (build_skyyhud_0.3.18.py lines 2432 / 2443 / 2140)
    "hudBg": "#0b1524(0.72)", "hudText": "#eaf6ff", "hudGrey": "#8b949e",
}
UI_DATA_COLORS = {"divinity": "#f4e27a", "pumpkin": "#e8862a", "log": "#9a6a3a", "coin": "#f2c94c", "heal": "#39f493",
                  "pet": "#b58cff"}   # sample data colours (placeholder icons only)

# ------------------------------------------------------------------ helpers
_FONTS = {}


def font(size, bold=False):
    k = (size, bold)
    if k not in _FONTS:
        _FONTS[k] = ImageFont.truetype(FONT_B if bold else FONT_R, size)
    return _FONTS[k]


def col(spec, alpha=None):
    """'#rrggbb' or '#rrggbb(0.72)' or a tuple -> RGBA tuple; alpha multiplies."""
    if isinstance(spec, tuple):
        r, g, b = spec[:3]
        a = spec[3] if len(spec) > 3 else 255
    else:
        s = spec
        a = 255
        if "(" in s:
            s, rest = s.split("(")
            a = int(round(float(rest.rstrip(")")) * 255))
        s = s.lstrip("#")
        r, g, b = int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
    if alpha is not None:
        a = int(round(a * alpha))
    return (r, g, b, a)


def text(img, xy, s, size, color, bold=False, anchor="la", alpha=1.0):
    """Draw text on its own layer so alpha blends correctly."""
    f = font(size, bold)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).text(xy, s, font=f, fill=col(color, alpha), anchor=anchor)
    img.alpha_composite(layer)


def tw(s, size, bold=False):
    return font(size, bold).getlength(s)


def rect(img, box, fill, outline=None, width=1):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x, y, w, h = box
    d.rectangle((x, y, x + w - 1, y + h - 1), fill=col(fill) if fill else None,
                outline=col(outline) if outline else None, width=width)
    img.alpha_composite(layer)


def dashed(img, box, color, width=2, dash=8, gap=5):
    x, y, w, h = box
    d = ImageDraw.Draw(img)
    c = col(color)
    for (x0, y0, x1, y1) in ((x, y, x + w - 1, y), (x, y + h - 1, x + w - 1, y + h - 1), (x, y, x, y + h - 1),
                             (x + w - 1, y, x + w - 1, y + h - 1)):
        length = max(abs(x1 - x0), abs(y1 - y0))
        p = 0
        while p < length:
            q = min(p + dash, length)
            if y0 == y1:
                d.line((x0 + p, y0, x0 + q, y0), fill=c, width=width)
            else:
                d.line((x0, y0 + p, x0, y0 + q), fill=c, width=width)
            p += dash + gap


def fade(layer, op):
    if op >= 1.0:
        return layer
    a = layer.getchannel("A").point(lambda v: int(v * op + 0.5))
    out = layer.copy()
    out.putalpha(a)
    return out


_TEX = {}


def tex(name):
    if name not in _TEX:
        _TEX[name] = Image.open(os.path.join(KIT, name + "@2x.png")).convert("RGBA")
    return _TEX[name]


def nine(name, w, h, bh, bv=None):
    """9-slice a kit @2x texture to w x h UI px (1 UI = 1 px). bh / bv = Border in UI units (horizontal / vertical)."""
    if bv is None:
        bv = bh
    src = tex(name)
    sw, sh = src.size
    sx = [0, bh * 2, sw - bh * 2, sw]
    sy = [0, bv * 2, sh - bv * 2, sh]
    dx = [0, bh, w - bh, w]
    dy = [0, bv, h - bv, h]
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for i in range(3):
        for j in range(3):
            s = (sx[i], sy[j], sx[i + 1], sy[j + 1])
            dw, dh = dx[i + 1] - dx[i], dy[j + 1] - dy[j]
            if s[2] <= s[0] or s[3] <= s[1] or dw <= 0 or dh <= 0:
                continue
            out.alpha_composite(src.crop(s).resize((dw, dh), Image.LANCZOS), (dx[i], dy[j]))
    return out


def scaled(name, w, h):
    return tex(name).resize((w, h), Image.LANCZOS)


# ------------------------------------------------------------------ the placeholder world (dark, generic voxel dusk)
def world(seed=1013, crosshair=True):
    rng = random.Random(seed)
    img = Image.new("RGBA", (SW, SH), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    for y in range(SH):          # sky
        t = min(1.0, y / 600.0)
        r = int(20 + 34 * t)
        g = int(28 + 40 * t)
        b = int(44 + 38 * t)
        d.line((0, y, SW, y), fill=(r, g, b, 255))
    for _ in range(90):          # a few dim stars
        x, y = rng.randrange(SW), rng.randrange(380)
        v = rng.randrange(90, 160)
        d.point((x, y), fill=(v, v, v + 20, 255))
    # distant voxel hills
    for layer, (base, colr) in enumerate(((560, (38, 50, 58)), (610, (33, 46, 46)))):
        x = 0
        hgt = base
        while x < SW:
            wdt = rng.randrange(40, 120)
            hgt = max(base - 120, min(base + 30, hgt + rng.randrange(-28, 29)))
            d.rectangle((x, hgt, x + wdt, SH), fill=colr + (255,))
            x += wdt
    # near ground: blocky grass / dirt
    gy = 700
    bs = 60
    for by in range(gy, SH, bs):
        for bx in range(0, SW, bs):
            k = rng.randrange(0, 12)
            top = by == gy
            base = (44, 64, 40) if top else (52, 44, 34)
            c = tuple(max(0, v - k) for v in base)
            d.rectangle((bx, by, bx + bs - 1, by + bs - 1), fill=c + (255,))
            d.line((bx, by, bx + bs - 1, by), fill=tuple(min(255, v + 8) for v in c) + (255,))
    # a few voxel trees
    for tx in (240, 980, 1420, 1690):
        th = rng.randrange(150, 230)
        d.rectangle((tx, gy - th, tx + 22, gy), fill=(58, 42, 30, 255))
        for i in range(5):
            lx = tx - 70 + rng.randrange(0, 60)
            ly = gy - th - 70 + rng.randrange(0, 60)
            d.rectangle((lx, ly, lx + 90, ly + 70), fill=(34 + i * 2, 58 + i * 3, 36, 255))
    if not crosshair:
        return img
    # crosshair
    d.line((SW // 2 - 8, SH // 2, SW // 2 + 8, SH // 2), fill=(230, 230, 230, 255), width=2)
    d.line((SW // 2, SH // 2 - 8, SW // 2, SH // 2 + 8), fill=(230, 230, 230, 255), width=2)
    return img


# ------------------------------------------------------------------ vanilla HUD (ESTIMATED areas, generic stand-ins)
# (name, x, y, w, h, note). Boss bar Top 57 / 66 high is from BossBar.ui as cited in SkyyHud/build_skyyhud_0.3.18.py line 166.
VANILLA = [
    ("Compass", 700, 8, 520, 40, "est."),
    ("Boss bar", 660, 57, 600, 66, "BossBar.ui Top 57, 66 high"),
    ("Chat", 8, 600, 560, 360, "est."),
    ("Chat input", 8, 966, 560, 30, "est., only while typing"),
    ("Held item name", 760, 904, 400, 30, "est."),
    ("Health / Stamina / Mana", 690, 940, 540, 54, "est."),
    ("Hotbar", 690, 1000, 540, 68, "est."),
    ("Item pickup popups", 1560, 760, 352, 220, "est."),
]


def draw_vanilla_standins(img):
    """Generic shapes only (not vanilla art): so the screen reads like a HUD."""
    d = ImageDraw.Draw(img)
    # compass strip
    x, y, w, h = 700, 8, 520, 40
    rect(img, (x, y + 10, w, 20), "#000000(0.35)")
    for i, lab in enumerate(["W", "NW", "N", "NE", "E"]):
        cx = x + 40 + i * 110
        text(img, (cx, y + 20), lab, 13, "#e6e6e6", True, "mm")
    # hotbar slots
    for i in range(9):
        sx = 694 + i * 59
        rect(img, (sx, 1004, 56, 56), "#000000(0.45)", "#c8c8c8(0.55)")
    rect(img, (694 + 4 * 59 - 2, 1002, 60, 60), None, "#ffffff(0.9)", 2)
    # vitals
    rect(img, (700, 948, 250, 12), "#000000(0.5)")
    rect(img, (700, 948, 200, 12), "#c84848(0.9)")
    rect(img, (970, 948, 250, 12), "#000000(0.5)")
    rect(img, (970, 948, 230, 12), "#d8b848(0.9)")
    rect(img, (700, 968, 250, 10), "#000000(0.5)")
    rect(img, (700, 968, 140, 10), "#4878d8(0.9)")
    # chat lines (faded)
    lines = ["[Server] Welcome to SkyWynn!", "Steve: anyone want to do the drake run?", "[Party] Alex: on my way",
             "COLLECTION UP  Pumpkin IV - unlocked Pumpkin Pie"]
    for i, s in enumerate(lines):
        text(img, (16, 860 + i * 24), s, 15, "#ffffff", False, "la", 0.85)


def draw_vanilla_zones(img, labels=True, only=None):
    for (name, x, y, w, h, note) in VANILLA:
        if only and name not in only:
            continue
        layer = Image.new("RGBA", (w, h), (220, 60, 60, 46))
        d = ImageDraw.Draw(layer)
        for k in range(-h, w, 12):   # hatch (clipped by the small layer)
            d.line((k, h, k + h, 0), fill=(230, 80, 80, 70), width=1)
        img.alpha_composite(layer, (x, y))
        dashed(img, (x, y, w, h), "#ff7070(0.85)", 2)
        if labels:
            tag(img, x + 4, y + 4, "VANILLA " + name + "  (" + note + ")", "#5a1818(0.88)", "#ffd0d0")


def tag(img, x, y, s, bg, fg, size=12):
    w = int(tw(s, size, True)) + 10
    rect(img, (x, y, w, size + 8), bg)
    text(img, (x + 5, y + 4), s, size, fg, True)
    return w


# ------------------------------------------------------------------ SkyyHud widgets as shipped (0.3.18 look)
def hud_box(w, h):
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    rect(layer, (0, 0, w, h), C["hudBg"])
    return layer


def hud_oneline(w, s):
    b = hud_box(w, 26)
    text(b, (w // 2, 13), s, 12, C["hudText"], True, "mm")
    return b


def hairline(layer, alpha=0.45):
    """The new HUD widgets' 1 px gold hairline = four 1 px Groups with Background #E8A93B(alpha) (no texture needed)."""
    w, h = layer.size
    c = col(C["gold"], alpha)
    d = ImageDraw.Draw(layer)
    d.line((0, 0, w - 1, 0), fill=c)
    d.line((0, h - 1, w - 1, h - 1), fill=c)
    d.line((0, 0, 0, h - 1), fill=c)
    d.line((w - 1, 0, w - 1, h - 1), fill=c)


# ------------------------------------------------------------------ (a) QUEST WIDGET
QW, QPAD = 300, 10


def arrow(layer, cx, cy, deg, size, color):
    """8-way 'where to go' arrow (deg 0 = straight ahead / up). Pre-drawn pictures in the build (HUD pictures cannot rotate)."""
    ImageDraw.Draw(layer).ellipse((cx - size - 2, cy - size - 2, cx + size + 2, cy + size + 2), outline=col(color, 0.55))
    size -= 1
    a = math.radians(deg)
    pts = [(0, -size), (size * 0.62, size * 0.7), (0, size * 0.32), (-size * 0.62, size * 0.7)]
    rp = [(cx + px * math.cos(a) - py * math.sin(a), cy + px * math.sin(a) + py * math.cos(a)) for px, py in pts]
    ImageDraw.Draw(layer).polygon(rp, fill=col(color))


def diamond(layer, cx, cy, r, color, hollow=False):
    pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    d = ImageDraw.Draw(layer)
    if hollow:
        d.polygon(pts, outline=col(color))
    else:
        d.polygon(pts, fill=col(color))


def tick(layer, x, y, color):
    ImageDraw.Draw(layer).line((x, y + 5, x + 4, y + 9, x + 11, y), fill=col(color), width=2)


def bar(layer, x, y, w, h, frac, fill):
    rect(layer, (x, y, w, h), "#000000(0.5)")
    fw = int(round(w * max(0.0, min(1.0, frac))))
    if fw > 0:
        rect(layer, (x, y, fw, h), fill)
    rect(layer, (x, y, w, 1), "#ffffff(0.08)")


def fit(s, size, bold, maxw):
    if tw(s, size, bold) <= maxw:
        return s
    while s and tw(s + "...", size, bold) > maxw:
        s = s[:-1]
    return s.rstrip() + "..."


def quest_height(tasks, compact=False):
    h = QPAD + 18 + 6 + 1 + 7
    first = True
    for t in tasks:
        if first:
            h += 18
            if t.get("bar") is not None:
                h += 4 + 6
            if t.get("where"):
                h += 4 + 15
            first = False
        else:
            h += 8 + 17
    return h + QPAD


def quest_widget(title, count, tasks, state="normal"):
    """tasks: list of dicts {name, prog, bar(frac|None), where, deg, done}. Returns RGBA QW x H."""
    h = quest_height(tasks)
    L = hud_box(QW, h)
    hairline(L)
    y = QPAD
    # header: gold star point + title, right: step count
    diamond(L, QPAD + 4, y + 9, 4, C["gold"])
    text(L, (QPAD + 14, y + 9), fit(title, 13, True, QW - 2 * QPAD - 70), 13, C["gold"], True, "lm")
    if count:
        text(L, (QW - QPAD, y + 9), count, 12, C["caption"], False, "rm")
    y += 18 + 6
    rect(L, (QPAD, y, QW - 2 * QPAD, 1), "#E8A93B(0.35)")
    y += 1 + 7
    for i, t in enumerate(tasks):
        if i == 0:
            done = t.get("done")
            if done:
                tick(L, QPAD, y + 4, C["success"])
            elif t.get("empty"):
                pass
            else:
                diamond(L, QPAD + 4, y + 9, 4, C["gold"])
            ncol = C["success"] if done else (C["text"] if t.get("empty") else C["rowName"])
            pw = tw(t.get("prog", ""), 14, True)
            text(L, (QPAD + 14, y + 9), fit(t["name"], 14, True, QW - 2 * QPAD - 14 - pw - 8), 14, ncol, True, "lm")
            if t.get("prog"):
                text(L, (QW - QPAD, y + 9), t["prog"], 14, C["success"] if done else C["white"], True, "rm")
            y += 18
            if t.get("bar") is not None:
                y += 4
                bar(L, QPAD + 14, y, QW - 2 * QPAD - 14, 6, t["bar"], C["success"] if done else C["progressGreen"])
                y += 6
            if t.get("where"):
                y += 4
                wc = C["success"] if done else C["info"]
                if t.get("deg") is not None and not done:
                    arrow(L, QPAD + 19, y + 8, t["deg"], 6, wc)
                    text(L, (QPAD + 30, y + 8), fit(t["where"], 12, False, QW - 2 * QPAD - 30), 12, wc, False, "lm")
                else:
                    text(L, (QPAD + 14, y + 8), fit(t["where"], 12, done, QW - 2 * QPAD - 14), 12, wc, done, "lm")
                y += 15
        else:
            y += 8
            diamond(L, QPAD + 4, y + 8, 3, C["text"], hollow=True)
            pw = tw(t.get("prog", ""), 12, False)
            text(L, (QPAD + 14, y + 8), fit(t["name"], 13, False, QW - 2 * QPAD - 14 - pw - 8), 13, C["text"], False, "lm")
            if t.get("prog"):
                text(L, (QW - QPAD, y + 8), t["prog"], 12, C["caption"], False, "rm")
            y += 17
    assert y + QPAD == h, (y, h)
    return L


QUEST_DEFAULT = dict(title="Tutorial - Home Island", count="3 / 21", tasks=[
    {"name": "Chop logs", "prog": "6/10", "bar": 0.6, "where": "NE  42 m  -  Old Grove", "deg": 45},
    {"name": "Craft a crafting accessory", "prog": "0/1"},
    {"name": "Open your Collections", "prog": ""},
])

# ------------------------------------------------------------------ (b) NOTIFICATION FEED
FW, F1, F2, FGAP = 280, 32, 44, 4     # card width, one-line card, two-line card, gap
FEED_MAXH = 4 * F1 + 3 * FGAP          # stack height budget = 140 (4 one-line cards)


def icon(kind, size=22):
    """Placeholder category icons (our own simple drawings, not item art)."""
    L = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    s = size
    if kind == "pumpkin":
        d.ellipse((2, 6, s - 2, s - 2), fill=col(UI_DATA_COLORS["pumpkin"]))
        d.line((s // 2, 7, s // 2, s - 3), fill=col("#b35f14"), width=1)
        d.line((s // 2 - 5, 8, s // 2 - 5, s - 4), fill=col("#b35f14"), width=1)
        d.line((s // 2 + 5, 8, s // 2 + 5, s - 4), fill=col("#b35f14"), width=1)
        d.rectangle((s // 2 - 1, 2, s // 2 + 1, 7), fill=col("#5c8a2e"))
    elif kind == "log":
        d.rectangle((3, 6, s - 6, s - 5), fill=col(UI_DATA_COLORS["log"]))
        d.ellipse((s - 10, 6, s - 2, s - 5), fill=col("#d9b27a"))
        d.ellipse((s - 8, 9, s - 4, s - 8), outline=col("#9a6a3a"))
    elif kind == "coin":
        d.ellipse((3, 3, s - 3, s - 3), fill=col(UI_DATA_COLORS["coin"]), outline=col("#a87a12"))
        d.ellipse((7, 7, s - 7, s - 7), outline=col("#a87a12"))
    elif kind == "heal":
        c = col(UI_DATA_COLORS["heal"])
        d.rectangle((s // 2 - 3, 3, s // 2 + 3, s - 3), fill=c)
        d.rectangle((3, s // 2 - 3, s - 3, s // 2 + 3), fill=c)
    elif kind == "pet":
        c = col(UI_DATA_COLORS["pet"])
        d.ellipse((5, 9, s - 5, s - 3), fill=c)
        for px in (4, 9, 13, 17):
            d.ellipse((px - 2, 3, px + 2, 8), fill=c)
    elif kind == "star":
        cx = cy = s / 2
        pts = []
        for k in range(8):
            r = (s / 2 - 1) if k % 2 == 0 else 3
            a = math.pi / 4 * k - math.pi / 2
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        d.polygon(pts, fill=col(C["gold"]))
    elif kind == "quest":
        d.rectangle((5, 3, s - 5, s - 3), fill=col("#d9c9a0"), outline=col("#8a6a3a"))
        for yy in (8, 12, 16):
            d.line((8, yy, s - 8, yy), fill=col("#8a6a3a"))
    return L


def feed_card(c, op=1.0, bump=False):
    """c = {icon, name, ncol, count, sub, frac}. op = card opacity (fade). bump = merge highlight frame."""
    h = F2 if c.get("sub") else F1
    L = hud_box(FW, h)
    if bump:
        rect(L, (0, 0, FW, h), "#E8A93B(0.18)")
    hairline(L, 0.30 if not bump else 0.85)
    L.alpha_composite(icon(c["icon"]), (6, (F1 - 22) // 2))
    cw = tw(c.get("count", ""), 14, True)
    text(L, (36, F1 // 2), fit(c["name"], 14, True, FW - 36 - 10 - cw - 8), 14, c.get("ncol", C["rowName"]), True, "lm")
    if c.get("count"):
        text(L, (FW - 10, F1 // 2), c["count"], 14, C["gold"] if bump else C["white"], True, "rm")
    if c.get("sub"):
        text(L, (36, 33), c["sub"], 12, C["rowSub"], False, "lm")
        if c.get("frac") is not None:
            bx = 36 + int(tw(c["sub"], 12)) + 10
            bar(L, bx, 31, FW - 10 - bx, 4, c["frac"], C["progressGreen"])
    return fade(L, op)


def feed_stack(cards):
    """cards oldest -> newest (newest at the bottom). Each = (card, opacity, bump). Returns RGBA FW x FEED_MAXH (bottom-aligned)."""
    L = Image.new("RGBA", (FW, FEED_MAXH), (0, 0, 0, 0))
    y = FEED_MAXH
    for c, op, bump in reversed(cards):
        im = feed_card(c, op, bump)
        y -= im.height
        assert y >= 0, "feed stack over its height budget"
        L.alpha_composite(im, (0, y))
        y -= FGAP
    return L


CARD = {
    "pumpkin": {"icon": "pumpkin", "name": "Pumpkin", "count": "x9"},
    "double": {"icon": "log", "name": "Double drop!  Oak Log", "ncol": C["gold"], "count": "x2"},
    "coll": {"icon": "pumpkin", "name": "Pumpkin Collection IV", "sub": "1,240 / 2,500", "frac": 0.496},
    "coins": {"icon": "coin", "name": "+120 coins  Bank interest", "ncol": C["gold"]},
    "heal": {"icon": "heal", "name": "+8 HP  Priest heal", "ncol": C["success"]},
    "pet": {"icon": "pet", "name": "Wolf  +35 Pet XP", "ncol": "#d2b8ff"},
    "quest": {"icon": "quest", "name": "Chop logs", "count": "7/10"},
}

# ------------------------------------------------------------------ (c) SKILLS widget + XP flash (SkyyHud 0.3.11 maths)
SKW, SKTP, SKROW, SKFS, SKVW = 180, 3, 20, 12, 40     # build_skyyhud_0.3.18.py lines 652-657


def skills_widget(rows, flash=None, flash_t=0.0, temp=None, levelup=False):
    """rows = [(name, level)]; flash = {row index: (gain text, frac before, frac after)}; flash_t 0..1 = tint strength.
    temp = (name, level, gain, frac) a hidden skill shown for the flash only. levelup = the flashed row just levelled."""
    all_rows = list(rows) + ([temp[:2]] if temp else [])
    h = SKTP + SKROW * len(all_rows) + SKTP
    L = hud_box(SKW, h)
    for i, (name, lvl) in enumerate(all_rows):
        y = SKTP + i * SKROW
        is_temp = temp is not None and i == len(all_rows) - 1
        f = None
        if flash and i in flash:
            f = flash[i]
        if is_temp:
            f = (temp[2], temp[3], temp[3])
        if f is not None and flash_t > 0:
            rect(L, (0, y, SKW, SKROW), col(C["gold"], 0.30 * flash_t))
            rect(L, (0, y, 2, SKROW), col(C["gold"], 0.95 * flash_t))
        ncol = C["hudText"]
        lcol = C["hudText"]
        if is_temp:
            ncol = lcol = C["value"]
        if f is not None and levelup and not is_temp and flash_t > 0:
            lcol = C["gold"]
        text(L, (6, y + SKROW // 2), name, SKFS, ncol, True, "lm")
        text(L, (SKW - 6, y + SKROW // 2), str(lvl), SKFS, lcol, True, "rm")
        if f is not None and flash_t > 0:
            gain = "LEVEL UP" if (levelup and not is_temp) else f[0]
            gcol = C["gold"] if (levelup and not is_temp) else C["success"]
            text(L, (SKW - 6 - SKVW + 6, y + SKROW // 2), gain, SKFS, gcol, True, "rm", alpha=min(1.0, 0.35 + flash_t))
            # 2 px XP bar along the row bottom: progress to the next level
            frac = f[2]
            bar(L, 6, y + SKROW - 3, SKW - 12, 2, frac, col(C["success"], 0.9))
    return L


SK_ROWS = [("Overall Level", 18), ("Divinity", 24), ("Foraging", 9), ("Farming", 7)]

# ------------------------------------------------------------------ (d) SETTINGS page (Messages tab)
PW, PH = 1100, 860
MSG_ROWS = [
    # label, help line, options, default index, chosen index, locked
    ("Item pickups", "Pumpkin x9 - repeats merge into one card", ("Chat", "Feed", "Off"), 1, 1, False),
    ("Double drops and perk procs", "Double drop! Oak Log x2, Extra potion!", ("Chat", "Feed", "Off"), 1, 1, False),
    ("Skill XP", "+79 Divinity XP - flashes on your HUD skill list", ("Chat", "Skill list", "Off"), 1, 1, False),
    ("Skill level-ups", "DIVINITY LEVEL 25 with its rewards (also a title)", ("Chat", "Feed", "Off"), 0, 0, False),
    ("Coins", "+120 coins bank interest, payments from players", ("Chat", "Feed", "Off"), 1, 0, False),
    ("Collection progress", "Pumpkin Collection IV 1,240 / 2,500", ("Chat", "Feed", "Off"), 1, 2, False),
    ("Collection rank-ups", "COLLECTION UP with the recipes it unlocked", ("Chat", "Feed", "Off"), 0, 0, False),
    ("Quest progress", "Chop logs 7/10 - the quest widget shows it too", ("Chat", "Feed", "Off"), 1, 1, False),
    ("Heals and buffs", "+8 HP from a Priest heal, Well Fed", ("Chat", "Feed", "Off"), 1, 1, False),
    ("Pet and guild XP", "+35 Pet XP, +12 Guild XP", ("Chat", "Feed", "Off"), 1, 1, False),
    ("System and server", "Restarts, warnings, staff messages - always in chat", ("Chat", "Feed", "Off"), 0, 0, True),
]
SEG_W, SEG_H, SEG_GAP = 92, 30, 2


def button(kind, w, h, label, size=14, state=""):
    tname = {"primary": "Primary", "secondary": "Secondary", "tertiary": "Tertiary", "danger": "Danger"}[kind] + state
    border = {"primary": (24, 12), "secondary": (12, 12), "tertiary": (12, 12), "danger": (12, 12)}[kind]
    b = nine(tname, w, h, *border)
    lc = C["buttonText"] if kind in ("primary", "danger") else C["button2Text"]
    if state == "_Active":
        lc = C["white"]
    if state == "_Disabled":
        lc = C["disabled"]
    text(b, (w // 2, h // 2), label, size, lc, True, "mm")
    return b


def segmented(opts, chosen, default, locked):
    w = SEG_W * 3 + SEG_GAP * 2
    L = Image.new("RGBA", (w, SEG_H), (0, 0, 0, 0))
    for i, o in enumerate(opts):
        if locked and i != chosen:
            b = nine("Tertiary", SEG_W, SEG_H, 12)
            b = fade(b, 0.45)
            text(b, (SEG_W // 2, SEG_H // 2), o, 13, C["disabled"], True, "mm")
        else:
            b = button("tertiary", SEG_W, SEG_H, o, 13, "_Active" if i == chosen else "")
        if i == default:   # server-default marker: small gold dot top-right inside the button
            ImageDraw.Draw(b).ellipse((SEG_W - 11, 5, SEG_W - 6, 10), fill=col(C["gold"]))
        L.alpha_composite(b, (i * (SEG_W + SEG_GAP), 0))
    return L


def settings_page():
    P = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    P.alpha_composite(nine("Frame", PW, PH, 32), (0, 0))
    # header bar + ornament + title
    P.alpha_composite(nine("Header", PW - 48, 38, 60, 0), (24, 18))
    orn = scaled("HeaderOrnament", 236, 22)
    P.alpha_composite(orn, ((PW - 236) // 2, 18 - 12))
    text(P, (PW // 2, 18 + 19), "Settings", 18, C["title"], True, "mm")
    P.alpha_composite(scaled("Close", 32, 32), (PW - 24 - 36, 21))
    # tab row (Tab textures, 44 high, equal widths)
    tabs = ["Messages", "Skills", "Collections", "Combat", "Coins", "Profiles", "Cooking", "General"]
    tx0, tw_ = 24, (PW - 48 - 7 * 4) // 8
    for i, t in enumerate(tabs):
        name = "Tab_Selected" if i == 0 else ("Tab_Hovered" if i == 3 else "Tab")
        tb = nine(name, tw_, 44, 20, 12)
        text(tb, (tw_ // 2, 22), t, 15, C["white"] if i == 0 else C["button2Text"], True, "mm")
        P.alpha_composite(tb, (tx0 + i * (tw_ + 4), 66))
    # left panel: the routing list
    lx, ly, lw, lh = 24, 122, 716, 642
    P.alpha_composite(nine("Panel", lw, lh, 12), (lx, ly))
    text(P, (lx + 16, ly + 22), "Where each message goes", 16, C["panelTitle"], True, "lm")
    text(P, (lx + 16, ly + 42), "Your own choice, the same on every profile. Saves on click.", 13, C["caption"], False, "lm")
    segx = lx + lw - 16 - (SEG_W * 3 + SEG_GAP * 2)
    rx, rw = lx + 12, lw - 24
    y = ly + 60
    for i, (lab, helpline, opts, dflt, cho, locked) in enumerate(MSG_ROWS):
        rowname = "Row_Selected" if i == 0 else ("Row_Hovered" if i == 5 else "Row")
        P.alpha_composite(nine(rowname, rw, 48, 8), (rx, y))
        text(P, (rx + 14, y + 16), lab, 15, C["rowName"], True, "lm")
        text(P, (rx + 14, y + 34), fit(helpline, 12, False, segx - rx - 30), 12, C["rowSub"], False, "lm")
        P.alpha_composite(segmented(opts, cho, dflt, locked), (segx, y + 9))
        y += 48 + 4
    assert y <= ly + lh - 10, ("list overflows panel", y, ly + lh)
    # right panel: preview of the selected row + legend + HUD editor link
    px, py, pw_, ph_ = 752, 122, PW - 24 - 752, 642
    P.alpha_composite(nine("Panel", pw_, ph_, 12), (px, py))
    text(P, (px + 16, py + 22), "Preview - Item pickups", 16, C["panelTitle"], True, "lm")
    text(P, (px + 16, py + 50), "In the Feed (bottom-left of the HUD)", 13, C["text"], False, "lm")
    well = nine("PanelInset", pw_ - 32, 92, 8)
    P.alpha_composite(well, (px + 16, py + 62))
    stack = [feed_card(CARD["pumpkin"]), feed_card(CARD["double"])]
    cy = py + 62 + 10
    for s in stack:
        P.alpha_composite(s, (px + 16 + (pw_ - 32 - FW) // 2, cy))
        cy += s.height + FGAP
    text(P, (px + 16, py + 174), "In Chat", 13, C["text"], False, "lm")
    well2 = nine("PanelInset", pw_ - 32, 54, 8)
    P.alpha_composite(well2, (px + 16, py + 186))
    text(P, (px + 28, py + 202), "+9 Pumpkin", 14, C["white"], False, "lm")
    text(P, (px + 28, py + 224), "+2 Oak Log (Double drop!)", 14, C["gold"], False, "lm")
    text(P, (px + 16, py + 264), "Off: nothing is shown. Items, coins and XP", 13, C["caption"], False, "lm")
    text(P, (px + 16, py + 282), "still arrive.", 13, C["caption"], False, "lm")
    rect(P, (px + 16, py + 304, pw_ - 32, 1), "#E8A93B(0.35)")
    # legend
    text(P, (px + 16, py + 326), "How to read this page", 15, C["panelTitle"], True, "lm")
    leg = nine("Tertiary_Active", 46, 22, 12)
    P.alpha_composite(leg, (px + 16, py + 342))
    text(P, (px + 72, py + 353), "your choice", 13, C["text"], False, "lm")
    ImageDraw.Draw(P).ellipse((px + 22, py + 375, px + 29, py + 382), fill=col(C["gold"]))
    text(P, (px + 72, py + 379), "the server's default", 13, C["text"], False, "lm")
    lk = fade(nine("Tertiary", 46, 22, 12), 0.45)
    P.alpha_composite(lk, (px + 16, py + 394))
    text(P, (px + 72, py + 405), "locked by the server", 13, C["text"], False, "lm")
    rect(P, (px + 16, py + 430, pw_ - 32, 1), "#E8A93B(0.35)")
    text(P, (px + 16, py + 452), "Move, resize or hide the Feed and the", 13, C["text"], False, "lm")
    text(P, (px + 16, py + 470), "Quest widget in the HUD Editor.", 13, C["text"], False, "lm")
    P.alpha_composite(button("secondary", pw_ - 32, 36, "Open HUD Editor", 15), (px + 16, py + 488))
    text(P, (px + 16, py + 548), "Feed card time and merge window are", 13, C["caption"], False, "lm")
    text(P, (px + 16, py + 566), "set by the server (Server Setup).", 13, C["caption"], False, "lm")
    # status + footer
    text(P, (24 + 16, 784), "+  Coins: Chat - saved.", 15, C["success"], True, "lm")
    rect(P, (24, 800, PW - 48, 1), "#E8A93B(0.35)")
    P.alpha_composite(button("secondary", 150, 36, "Back", 15, "_Hovered"), (44, 808))
    P.alpha_composite(button("danger", 210, 36, "Reset to defaults", 15), (206, 808))
    P.alpha_composite(button("secondary", 150, 36, "Close", 15), (PW - 44 - 150, 808))
    return P


# ------------------------------------------------------------------ the proposed 1080p layout (top-left x, y, w, h)
def r_tl(dx, dy, w, h):
    return (dx, dy, w, h)


def r_tr(dx, dy, w, h):
    return (SW - w - dx, dy, w, h)


def r_bl(dx, dy, w, h):
    return (dx, SH - h - dy, w, h)


def r_br(dx, dy, w, h):
    return (SW - w - dx, SH - h - dy, w, h)


QH = quest_height(QUEST_DEFAULT["tasks"])
SKH = SKTP + SKROW * len(SK_ROWS) + SKTP
LAYOUT = {   # id: (rect, kind, label, conditional?)
    "Coords": (r_tl(8, 8, 180, 26), "hud", "Coords tl 8,8", False),
    "Zone": (r_tr(8, 8, 180, 26), "hud", "Zone tr 8,8", False),
    "Minimap": (r_tr(8, 40, 160, 160), "hud", "Minimap tr 8,40", False),
    "Gclock": (r_bl(8, 40, 180, 26), "hud", "Game Clock bl 8,40", False),
    "Coins": (r_br(8, 8, 180, 26), "hud", "Coins br 8,8", False),
    "Combat": (((SW - 180) // 2, 130, 180, 37), "cond", "Combat t 0,130 (in combat)", True),
    "Seasons": (r_br(0, 250, 96, 320), "third", "Dynamic Seasons br 0,250", False),
    "Party": (r_tl(8, 200, 340, 116), "cond", "Party tl 8,200 (MOVED from 8,320; in a party)", True),
    "Guild": (r_tl(8, 324, 260, 94), "cond", "Guild tl 8,324 (MOVED from 8,444; in a guild)", True),
    "Skills": (r_tr(8, 240, SKW, SKH), "hud", "Skills tr 8,240 (MOVED from tl 8,544)", False),
    "Abilities": ((1240, SH - 59 - 21, 220, 59), "cond", "Abilities br 460,21 (MOVED from tl 8,760)", True),
    "Quest": (r_tl(8, 42, QW, QH), "new", "NEW Quest widget tl 8,42  300 x %d" % QH, False),
    "Feed": (r_bl(8, 488, FW, FEED_MAXH), "new", "NEW Feed bl 8,488  280 x 140 max", False),
}


def overlaps(a, b, gap=0):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return not (ax + aw + gap <= bx or bx + bw + gap <= ax or ay + ah + gap <= by or by + bh + gap <= ay)


def check_layout(layout, vanilla, sw=SW, sh=SH):
    probs = []
    keys = sorted(layout)
    for i, k in enumerate(keys):
        r = layout[k][0]
        if r[0] < 0 or r[1] < 0 or r[0] + r[2] > sw or r[1] + r[3] > sh:
            probs.append("%s off screen" % k)
        for v in vanilla:
            if v[0] in ("Boss bar",) and k != "Combat":
                pass
            if overlaps(r, v[1:5]):
                probs.append("%s x VANILLA %s" % (k, v[0]))
        for k2 in keys[i + 1:]:
            if overlaps(r, layout[k2][0]):
                probs.append("%s x %s" % (k, k2))
    return probs


# ------------------------------------------------------------------ drawing the HUD
def hud_layer(feature=None, feed_cards=None, sk_args=None, quest_args=None):
    """All widgets at their proposed spots. Conditional widgets drawn as they look when shown."""
    L = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    lay = LAYOUT

    def put(k, im):
        x, y = lay[k][0][:2]
        L.alpha_composite(im, (x, y))

    put("Coords", hud_oneline(180, "X 1204  Y 72  Z -388"))
    put("Zone", hud_oneline(180, "Home Island"))
    mm = hud_box(160, 160)
    d = ImageDraw.Draw(mm)
    d.ellipse((6, 6, 154, 154), fill=(52, 74, 50, 230), outline=col(C["gold"], 0.7), width=2)
    d.rectangle((40, 60, 110, 110), fill=(66, 92, 60, 255))
    d.polygon([(80, 72), (88, 92), (80, 87), (72, 92)], fill=(255, 255, 255, 255))
    text(mm, (80, 14), "N", 11, C["hudText"], True, "mm")
    put("Minimap", mm)
    put("Gclock", hud_oneline(180, "Day 12  14:05"))
    put("Coins", hud_oneline(180, "Coins 12,480"))
    put("Party", party_box())
    put("Guild", guild_box())
    sk = skills_widget(SK_ROWS, **(sk_args or {}))
    x, y = lay["Skills"][0][:2]
    L.alpha_composite(sk, (x, y))
    put("Abilities", abilities_box())
    put("Combat", combat_box())
    seasons = Image.new("RGBA", (96, 320), (0, 0, 0, 0))
    rect(seasons, (0, 0, 96, 320), "#1a1030(0.55)")
    text(seasons, (48, 20), "Season", 12, "#e6dcff", True, "mm")
    text(seasons, (48, 40), "Autumn", 12, "#e6dcff", False, "mm")
    put("Seasons", seasons)
    qa = quest_args or QUEST_DEFAULT
    put("Quest", quest_widget(qa["title"], qa["count"], qa["tasks"]))
    fx, fy, fw_, fh_ = lay["Feed"][0]
    if feed_cards is None:
        feed_cards = [(CARD["coins"], 0.25, False), (CARD["double"], 0.6, False), (CARD["heal"], 1.0, False),
                      (CARD["pumpkin"], 1.0, False)]
    L.alpha_composite(feed_stack(feed_cards), (fx, fy))
    return L


def party_box():
    b = hud_box(340, 116)
    text(b, (8, 14), "Party (3)", 12, C["hudText"], True, "lm")
    for i, (n, hp) in enumerate((("Alex", 0.8), ("Sam", 0.45), ("Rin", 1.0))):
        y = 34 + i * 26
        text(b, (8, y + 6), n, 12, C["hudText"], True, "lm")
        bar(b, 90, y + 3, 230, 6, hp, "#c84848(0.9)")
    return b


def guild_box():
    b = hud_box(260, 94)
    text(b, (8, 14), "[SKY] Cloud Walkers", 12, C["hudText"], True, "lm")
    text(b, (8, 36), "Lv 3  (1,240 / 2,000 XP)", 12, C["hudText"], False, "lm")
    text(b, (8, 58), "Online: Alex, Sam", 12, C["hudGrey"], False, "lm")
    return b


def abilities_box():
    b = hud_box(220, 59)
    text(b, (8, 13), "Meteor", 12, C["hudText"], True, "lm")
    text(b, (212, 13), "23 Mana", 12, C["hudText"], True, "rm")
    text(b, (8, 37), "Mana Barrier", 12, C["hudText"], True, "lm")
    text(b, (212, 37), "12s", 12, C["hudText"], True, "rm")
    bar(b, 8, 48, 204, 4, 0.4, C["info"])
    return b


def combat_box():
    b = hud_box(180, 37)
    text(b, (8, 13), "In combat", 12, C["error"], True, "lm")
    text(b, (172, 13), "4s", 12, C["error"], True, "rm")
    bar(b, 6, 23, 168, 6, 0.66, C["error"])
    return b


KIND_STYLE = {"hud": ("#78b4ff", "#0f2440(0.9)", "#cfe4ff"), "cond": ("#78b4ff", "#0f2440(0.9)", "#cfe4ff"),
              "third": ("#c09cff", "#2a1848(0.9)", "#e6dcff"), "new": ("#E8A93B", "#3a2808(0.92)", "#ffe2a8")}


def annotate(img, feature=None, layout=None):
    layout = layout or LAYOUT
    for k in sorted(layout):
        r, kind, label, cond = layout[k]
        line, bg, fg = KIND_STYLE[kind]
        x, y, w, h = r
        if kind == "new":
            rect(img, (x - 3, y - 3, w + 6, h + 6), None, line + "(0.95)" if "(" not in line else line, 2)
        else:
            dashed(img, (x - 2, y - 2, w + 4, h + 4), line + "(0.8)", 1, 5, 4)
        if k == feature:
            rect(img, (x - 7, y - 7, w + 14, h + 14), None, "#ffe2a8", 2)
    # tags placed after boxes so they sit on top; positions chosen to avoid the boxes they describe
    for k in sorted(layout):
        r, kind, label, cond = layout[k]
        line, bg, fg = KIND_STYLE[kind]
        x, y, w, h = r
        tx, ty = TAGPOS.get(k, (x, y + h + 6))
        tag(img, tx, ty, label, bg, fg, 11)


# tag spots (in free screen space next to each widget)
TAGPOS = {
    "Coords": (196, 12),
    "Zone": (1530, 12),
    "Minimap": (1570, 178),
    "Gclock": (196, 1020),
    "Coins": (1470, 1052),
    "Combat": (1056, 140),
    "Seasons": (1584, 520),
    "Party": (356, 204),
    "Guild": (276, 328),
    "Skills": (1430, 246),
    "Abilities": (1240, 974),
    "Quest": (316, 46),
    "Feed": (296, 446),
}


def legend(img, x, y):
    rows = [("#E8A93B", "NEW widget (this mockup)"), ("#78b4ff", "SkyyHud widget today (dashed; some moved)"),
            ("#c09cff", "third-party widget"), ("#ff7070", "VANILLA HUD area (shaded; mostly estimated)")]
    rect(img, (x, y, 360, 20 + 20 * len(rows)), "#000000(0.72)", "#E8A93B(0.6)")
    for i, (c_, s) in enumerate(rows):
        rect(img, (x + 10, y + 12 + i * 20, 14, 12), c_ + "(0.9)")
        text(img, (x + 32, y + 18 + i * 20), s, 12, "#e8e8e8", False, "lm")


def title_strip(img, s, sub):
    rect(img, (560, 250, 800, 54), "#000000(0.7)", "#E8A93B(0.6)")
    text(img, (960, 268), s, 17, "#ffe2a8", True, "mm")
    text(img, (960, 290), sub, 12, "#d8d8d8", False, "mm")


def composite(feature, ttl, sub, annotated=True, **kw):
    img = world()
    draw_vanilla_standins(img)
    if annotated:
        draw_vanilla_zones(img)
    img.alpha_composite(hud_layer(feature, **kw))
    if annotated:
        annotate(img, feature)
        legend(img, 1150, 600)
        title_strip(img, ttl, sub)
    return img


# ------------------------------------------------------------------ crop sheets
def sheet(w, h):
    img = Image.new("RGBA", (w, h), col("#151d2a"))
    # a strip of the placeholder world so the 72 % HUD background reads like in game
    wbg = world(crosshair=False).crop((0, 520, w if w <= SW else SW, 520 + h))
    if w > SW:
        wbg = wbg.resize((w, h))
    img.alpha_composite(wbg.crop((0, 0, w, h)))
    rect(img, (0, 0, w, h), "#000000(0.25)")
    return img


def label(img, x, y, s, size=13, color="#ffe2a8", bold=True):
    text(img, (x, y), s, size, color, bold)


def dim_h(img, x0, x1, y, s):
    d = ImageDraw.Draw(img)
    c = col("#7fd0ff")
    d.line((x0, y, x1, y), fill=c)
    d.line((x0, y - 4, x0, y + 4), fill=c)
    d.line((x1, y - 4, x1, y + 4), fill=c)
    text(img, ((x0 + x1) // 2, y - 8), s, 11, "#7fd0ff", True, "mm")


def dim_v(img, x, y0, y1, s):
    d = ImageDraw.Draw(img)
    c = col("#7fd0ff")
    d.line((x, y0, x, y1), fill=c)
    d.line((x - 4, y0, x + 4, y0), fill=c)
    d.line((x - 4, y1, x + 4, y1), fill=c)
    text(img, (x + 6, (y0 + y1) // 2), s, 11, "#7fd0ff", True, "lm")


def quest_crop():
    img = sheet(1380, 480)
    label(img, 20, 14, "QUEST WIDGET - 1:1 at 1080p (UI scale 1). SkyyHud box #0b1524(0.72) + 1 px gold hairline #E8A93B(0.45).", 15)
    label(img, 20, 36, "Fonts: stand-in Liberation Sans; game = Nunito Sans (Default). Padding 10 on every side.", 12, "#d8d8d8", False)
    states = [
        ("1 Default - next 3 tasks", QUEST_DEFAULT),
        ("2 Task done (2.5 s), then the list moves up", dict(title="Tutorial - Home Island", count="4 / 21", tasks=[
            {"name": "Chop logs", "prog": "10/10", "bar": 1.0, "where": "Done!  +25 coins  +40 Foraging XP", "done": True},
            {"name": "Craft a crafting accessory", "prog": "0/1"},
            {"name": "Open your Collections", "prog": ""}])),
        ("3 A quest after the tutorial", dict(title="Dragon's Hoard", count="2 / 5", tasks=[
            {"name": "Defeat Ember Drakes", "prog": "2/5", "bar": 0.4, "where": "SW  310 m  -  Ember Crag", "deg": 225},
            {"name": "Bring 3 Drake Scales to Mira", "prog": "1/3"}])),
        ("4 Compact (1 task), far target", dict(title="Tutorial - Island 2", count="12 / 21", tasks=[
            {"name": "Bridge to island 2", "prog": "", "bar": None, "where": "E  64 m  -  follow the arrow", "deg": 90}])),
        ("5 Nothing to do", dict(title="Quests", count="", tasks=[
            {"name": "No active quests", "prog": "", "bar": None, "where": "Pick one at the quest board in the hub", "deg": None,
             "empty": True}])),
    ]
    x, y = 20, 74
    for i, (s, q) in enumerate(states):
        im = quest_widget(q["title"], q["count"], q["tasks"])
        if i == 3:
            x, y = 20 + 2 * 340, 74 + 236
        if i == 4:
            x = 20 + 3 * 340
        label(img, x, y, s, 12)
        img.alpha_composite(im, (x, y + 22))
        if i == 0:
            dim_h(img, x, x + QW, y + 22 + im.height + 14, "300")
            dim_v(img, x + QW + 8, y + 22, y + 22 + im.height, str(im.height))
        x += 340
        if i == 2:
            x, y = 20, 74 + 236
    # anatomy notes
    nx, ny = 20, 330
    notes = [
        "Anatomy (px, top to bottom): pad 10 | header 18 | 6 | gold line 1 | 7 | task 1 name 18 | 4 | bar 6 | 4 | where 15 |",
        "8 | task 2 17 | 8 | task 3 17 | pad 10  = %d high with 3 tasks (%d with 2, %d with 1)." % (
            quest_height(QUEST_DEFAULT["tasks"]), quest_height(QUEST_DEFAULT["tasks"][:2]), quest_height(QUEST_DEFAULT["tasks"][:1])),
        "Header: gold diamond + quest name, Bold 13 #E8A93B; step count 12 #878e9c right.",
        "Task 1 (the one to do now): gold diamond, Bold 14 #d6e4ee, progress Bold 14 white right; bar 6 px",
        "(vanilla ProgressBar, fill shown #7caa4a); where-to-go 12 #7caacc with an 8-way arrow picture.",
        "Tasks 2-3: hollow diamond, 13 #96a9be, progress 12 #878e9c. Long names end in '...'.",
        "Done: tick + green #39f493 + the reward line for 2.5 s, then the list moves up.",
    ]
    for i, s in enumerate(notes):
        text(img, (nx, ny + i * 18), s, 12, "#e6e6e6")
    return img


def feed_crop():
    img = sheet(1400, 620)
    label(img, 20, 14, "NOTIFICATION FEED - 1:1. Cards 280 wide, 32 high (44 with a second line), gap 4, newest at the bottom.", 15)
    label(img, 20, 36, "Stack budget 140 px (4 one-line cards, or 3 with a two-line card); older cards fade out at the top. Box #0b1524(0.72) + hairline #E8A93B(0.30).", 12, "#d8d8d8", False)
    # A: the stack in 3 opacity stages
    x0, y0 = 20, 70
    label(img, x0, y0, "A  One moment: cards at 100 %, 60 %, 25 %", 13)
    st = feed_stack([(CARD["coins"], 0.25, False), (CARD["double"], 0.6, False), (CARD["heal"], 1.0, False),
                     (CARD["pumpkin"], 1.0, False)])
    img.alpha_composite(st, (x0, y0 + 24))
    for i, s in enumerate(("25 %  (4.7 s old)", "60 %  (4.3 s old)", "100 %", "100 %  newest")):
        text(img, (x0 + FW + 10, y0 + 24 + i * (F1 + FGAP) + F1 // 2), s, 12, "#7fd0ff", True, "lm")
    dim_h(img, x0, x0 + FW, y0 + 24 + FEED_MAXH + 14, "280")
    dim_v(img, x0 + FW + 150, y0 + 24, y0 + 24 + FEED_MAXH, "140 max")
    # B: one card's life
    x1 = 520
    label(img, x1, y0, "B  One card's life (opacity)", 13)
    for i, (op, s) in enumerate(((1.0, "0 - 4.0 s  100 %"), (0.6, "4.3 s  60 %"), (0.25, "4.7 s  25 %"),
                                 (0.0, "5.0 s  gone"))):
        yy = y0 + 24 + i * 40
        img.alpha_composite(feed_card(CARD["heal"], op), (x1, yy))
        text(img, (x1 + FW + 10, yy + 16), s, 12, "#7fd0ff", True, "lm")
        if op == 0.0:
            dashed(img, (x1, yy, FW, F1), "#7fd0ff(0.5)", 1, 4, 4)
    # C: merging repeats
    label(img, 20, 300, "C  Merging repeats: the same item within 3 s adds to its card (and restarts its 4 s)", 13)
    seq = [("0.0 s  first pickup", dict(CARD["pumpkin"], count="x1"), False),
           ("0.8 s  +3 merges (gold flash 0.3 s)", dict(CARD["pumpkin"], count="x4"), True),
           ("2.1 s  +5 more", dict(CARD["pumpkin"], count="x9"), False)]
    for i, (s, c, b) in enumerate(seq):
        xx = 20 + i * 330
        text(img, (xx, 330), s, 12, "#7fd0ff", True)
        img.alpha_composite(feed_card(c, 1.0, b), (xx, 350))
    # D: every card type
    label(img, 20, 410, "D  Card types (icons are placeholders; the build uses the item's own icon where the HUD allows it)", 13)
    types = ["pumpkin", "double", "coll", "coins", "heal", "pet", "quest"]
    for i, k in enumerate(types):
        xx = 20 + (i % 4) * 340
        yy = 438 + (i // 4) * 60
        img.alpha_composite(feed_card(CARD[k]), (xx, yy))
    notes = ["Text: name Bold 14 #d6e4ee (gold #E8A93B for coins / double drops, green #39f493 for heals); count Bold 14 white right;",
             "second line 12 #7f93a6 + a 4 px bar. Icon 22 px at x 6. Text starts at x 36. Pad 10 on the right."]
    for i, s in enumerate(notes):
        text(img, (20, 570 + i * 18), s, 12, "#e6e6e6")
    return img


def skillxp_crop():
    img = sheet(1360, 470)
    label(img, 20, 14, "SKILL-XP FLASH on the Skills widget - 1:1 (180 wide, 20 px rows, font 12, SkyyHud 0.3.11 maths)", 15)
    label(img, 20, 36, "XP is added up per skill for 2 s, then the row flashes: gold tint + '+79' in green + a 2 px bar to the next level.", 12, "#d8d8d8", False)
    frames = [
        ("1 Before", dict()),
        ("2 During, 0-0.5 s (full tint)", dict(flash={1: ("+79", 0.97, 0.99)}, flash_t=1.0)),
        ("3 During, 2.5 s (tint fading)", dict(flash={1: ("+79", 0.97, 0.99)}, flash_t=0.45)),
        ("4 After, 4 s (back to normal)", dict()),
    ]
    for i, (s, kw) in enumerate(frames):
        x = 20 + i * 230
        label(img, x, 70, s, 12)
        img.alpha_composite(skills_widget(SK_ROWS, **kw), (x, 92))
    x = 20 + 4 * 230
    label(img, x, 70, "5 Level up (3 s)", 12)
    img.alpha_composite(skills_widget([("Overall Level", 18), ("Divinity", 25), ("Foraging", 9), ("Farming", 7)],
                                      flash={1: ("+79", 0.0, 0.02)}, flash_t=1.0, levelup=True), (x, 92))
    label(img, 20, 200, "6 A hidden skill gains XP: a temporary row joins for the flash, then leaves (Settings: Show / Hide)", 12)
    text(img, (20, 222), "during (5 rows)", 11, "#7fd0ff", True)
    img.alpha_composite(skills_widget(SK_ROWS, temp=("Mining", 12, "+40", 0.31), flash_t=1.0), (20, 238))
    text(img, (250, 222), "after (4 rows again)", 11, "#7fd0ff", True)
    img.alpha_composite(skills_widget(SK_ROWS), (250, 238))
    text(img, (460, 266), "The box grows by one 20 px row while the flash lasts, then shrinks back.", 12, "#7fd0ff", True)
    text(img, (460, 286), "A box anchored at the bottom grows upward instead (SkyyHud keeps the anchored edge still).", 12, "#7fd0ff", True)
    notes = ["Gain text Bold 12 #39f493, right-aligned 6 px left of the 40 px level column; LEVEL UP Bold 12 #E8A93B and the level gold.",
             "Tint #E8A93B at 30 % + a 2 px gold edge on the left; bar 2 px #39f493 on #000000(0.5) along the row bottom.",
             "Bigger numbers shorten: +1,240 / +12.4k. Chat gets no XP line while Skill XP = 'Skill list' (Settings)."]
    for i, s in enumerate(notes):
        text(img, (20, 360 + i * 18), s, 12, "#e6e6e6")
    return img


def settings_crop():
    img = Image.new("RGBA", (PW + 40, PH + 70), col("#151d2a"))
    w = world().crop((410, 110, 410 + PW + 40, 110 + PH + 70))
    img.alpha_composite(w)
    rect(img, (0, 0, PW + 40, PH + 70), "#000000(0.35)")
    label(img, 20, 12, "SETTINGS -> MESSAGES  1:1 page 1100 x 860 (Sky Window kit, neutral Frame). Rows 48 + 4 gap; buttons 92 x 30.", 14)
    img.alpha_composite(settings_page(), (20, 46))
    return img


# ------------------------------------------------------------------ 1366 x 768 check
def check_1366():
    full = composite("Quest", "", "", annotated=False)
    a = full.resize((1366, 768), Image.LANCZOS)
    # B: unscaled - the same UI px on a 1366 x 768 screen; corner anchors keep their offsets
    sw, sh = 1366, 768
    W = world().resize((1366, 768), Image.LANCZOS)
    b = W.copy()

    def v(name, x, y, w, h):
        return (name, x, y, w, h)
    van = [v("Compass", (sw - 520) // 2, 8, 520, 40), v("Chat", 8, sh - 480, 560, 360), v("Health / Stamina / Mana", (sw - 540) // 2, sh - 140, 540, 54),
           v("Hotbar", (sw - 540) // 2, sh - 80, 540, 68), v("Item pickup popups", sw - 360, sh - 320, 352, 220)]
    lay = {}
    for k, (r, kind, lab, cond) in LAYOUT.items():
        x, y, w_, h_ = r
        right = x + w_ / 2 > SW / 2
        bottom = y + h_ / 2 > SH / 2
        if k == "Combat":
            nx = (sw - w_) // 2
        elif k == "Abilities":
            nx = sw // 2 + 280
        else:
            nx = (sw - (SW - x)) if right else x
        ny = (sh - (SH - y)) if bottom else y
        lay[k] = ((nx, ny, w_, h_), kind, k, cond)
    # feed shrinks to fit between the guild / quest boxes and the chat (rule in Layout-Spec.md)
    chat_top = sh - 480
    fx, fy, fw_, fh_ = lay["Feed"][0]
    budget = chat_top - 8 - (lay["Quest"][0][1] + lay["Quest"][0][3] + 8)
    lay["Feed"] = ((fx, chat_top - 8 - min(FEED_MAXH, budget), fw_, min(FEED_MAXH, budget)), "new", "Feed", False)
    for (name, x, y, w_, h_) in van:
        layer = Image.new("RGBA", b.size, (0, 0, 0, 0))
        ImageDraw.Draw(layer).rectangle((x, y, x + w_ - 1, y + h_ - 1), fill=(220, 60, 60, 60))
        b.alpha_composite(layer)
        dashed(b, (x, y, w_, h_), "#ff7070(0.85)", 2)
        tag(b, x + 4, y + 4, "VANILLA " + name + " (est.)", "#5a1818(0.88)", "#ffd0d0", 11)
    probs = []
    order = sorted(lay, key=lambda k: (lay[k][1] == "new", k))     # new widgets drawn last (on top)
    for k in order:
        (x, y, w_, h_), kind, lab, cond = lay[k]
        line, bg, fg = KIND_STYLE[kind]
        rect(b, (x, y, w_, h_), "#0b1524(0.72)")
        rect(b, (x, y, w_, h_), None, line, 2 if kind == "new" else 1)
        tag(b, x + 2, y + 2, k + (" (when shown)" if cond else ""), bg, fg, 10)
        for (name, vx, vy, vw, vh) in van:
            if overlaps((x, y, w_, h_), (vx, vy, vw, vh)):
                probs.append((k, name))
    for k in ("Feed", "Quest"):
        for k2 in sorted(lay):
            if k2 != k and lay[k2][1] != "new" and overlaps(lay[k][0], lay[k2][0]):
                probs.append((k, k2 + " (when shown)" if lay[k2][3] else k2))
    for (k, name) in probs:
        x, y, w_, h_ = lay[k][0]
        rect(b, (x, y, w_, h_), None, "#ff3030", 3)
    out = Image.new("RGBA", (1366 * 2 + 60, 768 + 140), col("#10161f"))
    out.alpha_composite(a, (20, 90))
    out.alpha_composite(b, (1366 + 40, 90))
    label(out, 20, 14, "1366 x 768 CHECK", 18)
    text(out, (20, 46), "A  If the client scales the UI to the screen height (x 0.711): the 1080p layout as-is; 14 px text becomes ~10 px - still readable, no new overlaps.", 13, "#e6e6e6")
    text(out, (20, 66), "B  If it does NOT scale (worst case, 1 UI = 1 px): corner anchors keep their offsets. Red = touches a vanilla area (est.).", 13, "#e6e6e6")
    text(out, (1366 + 40, 868), "B result: " + ("; ".join("%s x %s" % p for p in probs) if probs else "no overlap with vanilla areas")
         + ".  Feed shrinks to %d px (%d cards) to stay above the chat." % (lay["Feed"][0][3], (lay["Feed"][0][3] + FGAP) // (F1 + FGAP)),
         12, "#ffd0a0", True)
    text(out, (20, 868), "A: same as e_layout_clean_1080p.png, scaled down.", 12, "#ffd0a0", True)
    return out, probs, lay


# ------------------------------------------------------------------ main
def save(img, name):
    img.convert("RGB").save(os.path.join(HERE, name), "PNG", optimize=False)


def main():
    probs = check_layout({k: v for k, v in LAYOUT.items()}, VANILLA)
    # the boss bar only shows in a boss fight and the Combat widget sits under it by design (Top 130 > 57 + 66)
    real = [p for p in probs if not p.startswith("Seasons")]
    print("1080p layout overlaps:", real if real else "none")
    save(composite("Quest", "(a) QUEST WIDGET - always on, top-left under Coords",
                   "next 1-3 undone tasks, progress + bar, where to go; never over the chat, compass or minimap"), "a_quest_1080p.png")
    save(quest_crop(), "a_quest_crop.png")
    save(composite("Feed", "(b) NOTIFICATION FEED - bottom-left, directly above the chat",
                   "stacking cards, newest at the bottom, fading at the top; repeats merge (Pumpkin x9)"), "b_feed_1080p.png")
    save(feed_crop(), "b_feed_crop.png")
    save(composite("Skills", "(c) SKILL-XP FLASH - the Skills widget (moved to the right edge)",
                   "Divinity row flashing '+79' (frame 2 of 4); XP leaves the chat",
                   sk_args=dict(flash={1: ("+79", 0.97, 0.99)}, flash_t=1.0)), "c_skillxp_1080p.png")
    save(skillxp_crop(), "c_skillxp_crop.png")
    # settings over the world (HUD hidden behind a page - UNVERIFIED which HUD parts stay)
    img = world()
    draw_vanilla_standins(img)
    draw_vanilla_zones(img)
    sp = settings_page()
    img.alpha_composite(sp, ((SW - PW) // 2, (SH - PH) // 2))
    dashed(img, ((SW - PW) // 2 - 4, (SH - PH) // 2 - 4, PW + 8, PH + 8), "#ffe2a8(0.9)", 2)
    tag(img, (SW - PW) // 2, (SH - PH) // 2 - 30, "NEW Settings -> Messages  1100 x 860, centred (page root = Width / Height only)",
        "#3a2808(0.92)", "#ffe2a8", 12)
    save(img, "d_settings_1080p.png")
    save(settings_crop(), "d_settings_crop.png")
    save(composite(None, "(e) THE PROPOSED 1080p HUD - every widget at its default spot",
                   "gold = new, blue = SkyyHud today (Party / Guild / Skills / Abilities moved), red = vanilla (estimated)"),
         "e_layout_1080p.png")
    save(composite(None, "", "", annotated=False), "e_layout_clean_1080p.png")
    chk, p2, _ = check_1366()
    print("1366x768 unscaled overlaps:", p2 if p2 else "none")
    save(chk, "f_check_1366x768.png")


if __name__ == "__main__":
    main()
