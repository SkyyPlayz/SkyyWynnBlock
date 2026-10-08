#!/usr/bin/env python3
"""SkyyFishing UI mockup v2 (cloud draft 2026-10-08, paper only).

Draws research/cloud/Fishing-UI-Mockup.png: A the screen during a fight (50 %), B the minigame HUD widget states (1:1),
C the catch card (1:1), D the Fishing Bench RIG tab (1:1), E the Pond Fish collection page (1:1), F the kit colours used.

Every colour and size comes from tools/skyyui.py (COLOR, RARITY, sizes at the "readable" text scale). The window frame,
button textures and fonts are flat stand-ins (no game files here); the real build uses page_shell / button / tab_row.
Art: our own drawing only - fish icons are loaded from research/cloud/fish-art/icons/ (our generated icons); rod / reel /
hook / line / sinker icons are drawn here as stand-ins (the real icons are the local 3D renders, models-local/art/fishing).
Vanilla items (junk) are shown as an empty labelled slot - never a copy of a vanilla icon.

Deterministic: no randomness except a seeded generator; two runs give the same bytes.
Run: python3 research/cloud/fishing-ui/make_fishing_ui_v2.py
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
CLOUD = os.path.dirname(HERE)
ICONS = os.path.join(CLOUD, "fish-art", "icons")
OUT = os.path.join(CLOUD, "Fishing-UI-Mockup.png")

# ---------------------------------------------------------------- kit values (copied from tools/skyyui.py COLOR / sizes)
C = {
    "text": "#96a9be", "white": "#ffffff", "title": "#b4c8c9", "section": "#9aacbc", "caption": "#878e9c",
    "captionLight": "#5a6a7a", "rowName": "#d6e4ee", "rowSub": "#7f93a6", "rowBadge": "#9aacbc", "disabled": "#797b7c",
    "gold": "#E8A93B", "buttonText": "#bfcdd5", "button2Text": "#bdcbd3", "value": "#b7cedd", "propKey": "#7a8a9a",
    "summary": "#8fa6ba", "error": "#ff6b6b", "success": "#39f493", "warning": "#ffcc00", "info": "#7caacc",
    "have": "#3d913f", "outOfStock": "#cc4444", "selected": "#4274a5", "row": "#101925(0.55)", "well": "#000000(0.15)",
    "hud": "#000000(0.2)", "separator": "#2b3542", "formLine": "#5e512c", "slotBorder": "#1a2530",
    "slotBorderHave": "#2a5a3a", "cardOverlay": "#0a0e12(0.75)", "progressTrack": "#1a2030", "progressFill": "#aa7c4a",
    "progressBlue": "#4a7caa", "progressGreen": "#7caa4a", "panelTitle": "#afc2c3",
}
RARITY = {"Normal": "#FFFFFF", "Unique": "#FFFF55", "Rare": "#FF55FF", "Legendary": "#55FFFF", "Fabled": "#FF5555",
          "Mythic": "#CC66CC", "Set": "#55FF55"}
UI_DATA_COLORS = RARITY  # content colours (fish rarity = the pack ladder, Fish-Species-Catalog section 1 proposal)
TITLE_H, PAD, ROW_GAP, PROP_KEY_W = 38, 17, 3, 150
BTN_H, BTN_SMALL_H, BTN_MIN_W, ROW_ACTION_W = 44, 32, 172, 92
TAB_GAP, TAB_MARGIN, WELL_PAD, WELL_LIST_PAD = 5, 10, 8, 4
ROW_H_READABLE, PROP_ROW_H = 56, 26          # readable scale: property row = 16 + 10
SLOT_FRAME, MEMBAR_H = 68, 22
# readable text scale (vanilla 11 / 12 / 13 / 14 -> 14 / 15 / 16 / 18; 16 / 18 stay)
FS = {"title": 15, "button": 17, "buttonSmall": 14, "default": 16, "rowName": 18, "rowSub": 15, "rowBadge": 15,
      "heading": 18, "propKey": 16, "propValue": 16, "section": 16, "caption": 15, "info": 18}

# mockup-only stand-ins (NOT kit colours: they stand for textures we cannot ship or see here)
STAND = {"canvas": "#0c1016", "body": "#1a2230", "bodyEdge": "#3a4659", "bodyEdge2": "#0d1219", "head": "#141c27",
         "headEdge": "#4a4130", "orn": "#b48a3e", "ornDark": "#5e4a22", "pri": ("#4f86bd", "#355f8e", "#76a5d6"),
         "sec": ("#3b4859", "#2b3644", "#56677c"), "dis": ("#2d3238", "#24282d", "#3b4148"),
         "tint": "#e9edf2", "note": "#c3cbd6", "noteDim": "#7d8794"}

FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_fonts = {}


def font(size, bold=False):
    k = (size, bold)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(FONT_B if bold else FONT_R, size)
    return _fonts[k]


def rgba(col):
    """'#rrggbb' or '#rrggbb(a)' -> (r, g, b, a)."""
    a = 255
    if "(" in col:
        col, al = col[:-1].split("(")
        a = int(round(float(al) * 255))
    col = col.lstrip("#")
    if len(col) == 8:
        a = int(col[6:8], 16)
    return (int(col[0:2], 16), int(col[2:4], 16), int(col[4:6], 16), a)


def mix(c1, c2, t):
    a, b = rgba(c1), rgba(c2)
    return "#%02x%02x%02x" % tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


class Canvas(object):
    def __init__(self, w, h, bg):
        self.im = Image.new("RGBA", (w, h), rgba(bg))
        self.d = ImageDraw.Draw(self.im)

    def rect(self, box, col, outline=None, width=1):
        x0, y0, x1, y1 = [int(round(v)) for v in box]
        if x1 <= x0 or y1 <= y0:
            return
        c = rgba(col) if col else None
        if c is None:
            pass
        elif c[3] < 255:
            layer = Image.new("RGBA", (x1 - x0, y1 - y0), c)
            self.im.alpha_composite(layer, (x0, y0))
        else:
            self.d.rectangle((x0, y0, x1 - 1, y1 - 1), fill=c)
        if outline:
            self.d.rectangle((x0, y0, x1 - 1, y1 - 1), outline=rgba(outline), width=width)
        self.d = ImageDraw.Draw(self.im)

    def vgrad(self, box, top, bottom):
        x0, y0, x1, y1 = [int(v) for v in box]
        for y in range(y0, y1):
            t = (y - y0) / max(1, (y1 - y0 - 1))
            self.d.line((x0, y, x1 - 1, y), fill=rgba(mix(top, bottom, t)))

    def text(self, x, y, s, size, col, bold=False, anchor="la", maxw=None, upper=False):
        if upper:
            s = s.upper()
        f = font(size, bold)
        while maxw and size > 10 and self.d.textlength(s, font=f) > maxw:   # vanilla ShrinkTextToFit (down to 12 px)
            size -= 1
            f = font(size, bold)
        self.d.text((x, y), s, font=f, fill=rgba(col), anchor=anchor)
        return self.d.textlength(s, font=f)

    def tw(self, s, size, bold=False):
        return self.d.textlength(s, font=font(size, bold))

    def wrap(self, x, y, s, size, col, w, bold=False, lh=None):
        lh = lh or int(size * 1.36)
        words, line, yy = s.split(" "), "", y
        for wd in words:
            t = (line + " " + wd).strip()
            if self.tw(t, size, bold) > w and line:
                self.text(x, yy, line, size, col, bold)
                yy += lh
                line = wd
            else:
                line = t
        if line:
            self.text(x, yy, line, size, col, bold)
            yy += lh
        return yy

    def paste(self, img, x, y):
        self.im.alpha_composite(img, (int(x), int(y)))
        self.d = ImageDraw.Draw(self.im)


# ---------------------------------------------------------------- our own stand-in icons (drawn 4x, then reduced)
METAL = {"Bamboo": "#b9a66a", "Copper": "#c8763e", "Iron": "#a9b2bc", "Thorium": "#6fae74", "Cobalt": "#4f7fd0"}


def _ss(size):
    s = size * 4
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im), s


def _done(im, size):
    return im.resize((size, size), Image.LANCZOS)


def icon_rod(size, metal="Copper", reel=None):
    im, d, s = _ss(size)
    m = rgba(METAL[metal])
    dark = tuple(int(v * 0.55) for v in m[:3]) + (255,)
    x0, y0, x1, y1 = s * 0.14, s * 0.88, s * 0.90, s * 0.10
    d.line((x0, y0, x1, y1), fill=(30, 22, 16, 255), width=int(s * 0.075))
    d.line((x0, y0, x1, y1), fill=(92, 64, 40, 255), width=int(s * 0.05))
    hx, hy = x0 + (x1 - x0) * 0.25, y0 + (y1 - y0) * 0.25
    d.line((x0 + 2, y0 - 2, hx, hy), fill=(196, 160, 112, 255), width=int(s * 0.085))      # cork grip
    for t in (0.06, 0.13, 0.20):
        gx, gy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        d.line((gx - 6, gy - 6, gx + 6, gy + 6), fill=(150, 116, 76, 255), width=3)
    for t in (0.42, 0.62, 0.80, 0.95):                                                     # guides in the rod metal
        gx, gy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        r = s * 0.03
        d.ellipse((gx - r, gy - r, gx + r, gy + r), outline=m, width=int(s * 0.016))
    fx, fy = x0 + (x1 - x0) * 0.28, y0 + (y1 - y0) * 0.28
    d.line((fx - 1, fy + 1, fx + s * 0.06, fy - s * 0.06), fill=m, width=int(s * 0.07))     # ferrule
    rm = rgba(METAL[reel]) if reel else m
    rd = tuple(int(v * 0.55) for v in rm[:3]) + (255,)
    cx, cy, r = fx + s * 0.07, fy + s * 0.09, s * 0.105
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=rd)
    d.ellipse((cx - r * 0.8, cy - r * 0.8, cx + r * 0.8, cy + r * 0.8), fill=rm[:3] + (255,))
    d.ellipse((cx - r * 0.3, cy - r * 0.3, cx + r * 0.3, cy + r * 0.3), fill=rd)
    d.line((x1, y1, x1 + s * 0.02, y1 + s * 0.45), fill=(230, 236, 240, 200), width=2)       # line from the tip
    d.line((x0, y0, hx, hy), fill=dark, width=1)
    return _done(im, size)


def icon_reel(size, metal="Iron"):
    im, d, s = _ss(size)
    m = rgba(METAL[metal])
    dk = tuple(int(v * 0.5) for v in m[:3]) + (255,)
    lt = tuple(min(255, int(v * 1.25)) for v in m[:3]) + (255,)
    cx, cy, r = s * 0.46, s * 0.54, s * 0.32
    d.rectangle((cx - s * 0.05, s * 0.12, cx + s * 0.05, cy - r + 4), fill=dk)              # foot
    d.rectangle((cx - s * 0.16, s * 0.10, cx + s * 0.16, s * 0.16), fill=m)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=dk)
    d.ellipse((cx - r * 0.86, cy - r * 0.86, cx + r * 0.86, cy + r * 0.86), fill=m)
    d.arc((cx - r * 0.86, cy - r * 0.86, cx + r * 0.86, cy + r * 0.86), 200, 290, fill=lt, width=int(s * 0.03))
    d.ellipse((cx - r * 0.55, cy - r * 0.55, cx + r * 0.55, cy + r * 0.55), fill=(222, 226, 214, 255))   # wound line
    for k in range(4):
        rr = r * (0.5 - k * 0.08)
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=(180, 186, 176, 255), width=2)
    d.ellipse((cx - r * 0.16, cy - r * 0.16, cx + r * 0.16, cy + r * 0.16), fill=dk)
    ax, ay = cx + r * 0.95, cy + r * 0.55
    d.line((cx, cy, ax, ay), fill=dk, width=int(s * 0.05))                                   # handle arm + knob
    d.ellipse((ax - s * 0.06, ay - s * 0.06, ax + s * 0.06, ay + s * 0.06), fill=(60, 40, 28, 255))
    return _done(im, size)


def icon_hook(size, metal="Copper", kind="barbed"):
    im, d, s = _ss(size)
    m = rgba(METAL[metal])
    dk = tuple(int(v * 0.5) for v in m[:3]) + (255,)
    w = int(s * 0.07)
    cx = s * 0.5
    d.ellipse((cx - s * 0.08, s * 0.08, cx + s * 0.08, s * 0.24), outline=dk, width=w)       # eye
    d.line((cx, s * 0.22, cx, s * 0.62), fill=dk, width=w + 6)
    d.line((cx, s * 0.22, cx, s * 0.62), fill=m, width=w)
    d.arc((cx - s * 0.30, s * 0.40, cx + s * 0.02, s * 0.86), 0, 180, fill=dk, width=w + 6)
    d.arc((cx - s * 0.30, s * 0.40, cx + s * 0.02, s * 0.86), 0, 180, fill=m, width=w)
    tip = (cx - s * 0.28, s * 0.60)
    d.line((cx - s * 0.29, s * 0.66, tip[0], tip[1] - s * 0.06), fill=m, width=w)
    if kind == "barbed":
        d.polygon([(tip[0] - 2, tip[1] - s * 0.08), (tip[0] + s * 0.09, tip[1] + s * 0.02), (tip[0] + 2, tip[1] + s * 0.02)],
                  fill=m)
    else:                                                                                    # lure: a bright feather tuft
        for k, col in enumerate(((240, 90, 60), (250, 200, 70), (90, 170, 230))):
            d.ellipse((cx + s * 0.02 + k * 8, s * 0.26 + k * 10, cx + s * 0.26 + k * 8, s * 0.40 + k * 10), fill=col + (255,))
    d.line((cx - 3, s * 0.24, cx - 3, s * 0.58), fill=(255, 255, 255, 120), width=4)
    return _done(im, size)


def icon_line(size, thread="#d8d2bc"):
    im, d, s = _ss(size)
    t = rgba(thread)
    td = tuple(int(v * 0.7) for v in t[:3]) + (255,)
    x0, x1, y0, y1 = s * 0.18, s * 0.82, s * 0.24, s * 0.76
    d.rectangle((x0 + s * 0.06, y0 + s * 0.08, x1 - s * 0.06, y1 - s * 0.08), fill=t)
    for k in range(9):
        yy = y0 + s * 0.10 + k * (y1 - y0 - s * 0.2) / 8
        d.line((x0 + s * 0.06, yy, x1 - s * 0.06, yy + s * 0.02), fill=td, width=3)
    for xx in (x0, x1 - s * 0.10):
        d.rectangle((xx, y0, xx + s * 0.10, y1), fill=(120, 84, 52, 255))
        d.rectangle((xx + 4, y0 + 4, xx + s * 0.10 - 4, y0 + s * 0.06), fill=(160, 118, 76, 255))
    d.line((x1 - s * 0.06, y0 + s * 0.30, s * 0.94, s * 0.12), fill=t, width=3)
    return _done(im, size)


def icon_sinker(size, stone="#8d939b", kind="weighted"):
    im, d, s = _ss(size)
    c = rgba(stone)
    dk = tuple(int(v * 0.55) for v in c[:3]) + (255,)
    lt = tuple(min(255, int(v * 1.3)) for v in c[:3]) + (255,)
    cx = s * 0.5
    d.ellipse((cx - s * 0.06, s * 0.08, cx + s * 0.06, s * 0.20), outline=(170, 176, 184, 255), width=int(s * 0.03))
    if kind == "weighted":
        pts = [(cx, s * 0.18), (cx + s * 0.28, s * 0.80), (cx - s * 0.28, s * 0.80)]
        d.polygon(pts, fill=dk)
        d.polygon([(cx, s * 0.24), (cx + s * 0.22, s * 0.76), (cx - s * 0.22, s * 0.76)], fill=c)
        d.polygon([(cx, s * 0.24), (cx - s * 0.04, s * 0.76), (cx - s * 0.22, s * 0.76)], fill=lt)
    else:
        d.ellipse((cx - s * 0.24, s * 0.22, cx + s * 0.24, s * 0.84), fill=dk)
        d.ellipse((cx - s * 0.20, s * 0.26, cx + s * 0.20, s * 0.80), fill=c)
        d.ellipse((cx - s * 0.14, s * 0.32, cx - s * 0.02, s * 0.52), fill=lt)
    return _done(im, size)


def icon_fish(name, size):
    p = os.path.join(ICONS, name + ".png")
    im = Image.open(p).convert("RGBA")
    if im.size[0] != size:
        im = im.resize((size, size), Image.NEAREST if size % im.size[0] == 0 else Image.LANCZOS)
    return im


def silhouette(img):
    """An undiscovered species: the icon's own shape in a flat dark tone (our art)."""
    a = img.split()[3]
    flat = Image.new("RGBA", img.size, (8, 12, 18, 255))
    flat.putalpha(a.point(lambda v: 170 if v > 40 else 0))
    return flat


# ---------------------------------------------------------------- kit-shaped drawing helpers
def window(cv, x, y, w, h, title, plain=False):
    """page_shell stand-in: 38 px ContainerHeader (runes unless plain) + ContainerPatch body; gold ornaments 236 x 11."""
    if not plain:
        ox = x + w // 2 - 118
        cv.d.polygon([(ox + 14, y), (ox + 222, y), (ox + 236, y - 1), (ox + 160, y - 12), (ox + 76, y - 12), (ox, y - 1)],
                     fill=rgba(STAND["orn"]), outline=rgba(STAND["ornDark"]))
        cv.d.polygon([(ox + 14, y + h), (ox + 222, y + h), (ox + 160, y + h + 6), (ox + 76, y + h + 6)],
                     fill=rgba(STAND["orn"]), outline=rgba(STAND["ornDark"]))
    cv.vgrad((x, y, x + w, y + TITLE_H), "#1d2735", STAND["head"])
    cv.rect((x, y, x + w, y + TITLE_H), None, outline=STAND["headEdge"])
    if not plain:
        for side in (-1, 1):
            bx = x + w // 2 + side * (w // 2 - 60)
            for k in range(3):
                rx = bx + side * k * 14
                cv.d.polygon([(rx, y + 13), (rx + 5, y + 19), (rx, y + 25), (rx - 5, y + 19)], outline=rgba(STAND["ornDark"]))
    cv.text(x + w // 2, y + 7 + 12, title, FS["title"], C["title"], True, "mm", upper=True)
    cv.rect((x, y + TITLE_H, x + w, y + h), STAND["body"], outline=STAND["bodyEdge"])
    cv.rect((x + 1, y + TITLE_H + 1, x + w - 1, y + h - 1), None, outline=STAND["bodyEdge2"])
    return x + PAD, y + TITLE_H + PAD, w - 2 * PAD, h - TITLE_H - 2 * PAD


def button(cv, x, y, w, text, kind="secondary", size="normal"):
    h = BTN_H if size == "normal" else BTN_SMALL_H
    top, bot, edge = STAND[{"primary": "pri", "secondary": "sec", "disabled": "dis"}[kind]]
    cv.vgrad((x, y, x + w, y + h), top, bot)
    cv.rect((x, y, x + w, y + h), None, outline=edge)
    cv.d.line((x + 2, y + 1, x + w - 3, y + 1), fill=rgba(mix(edge, "#ffffff", 0.25)))
    col = C["disabled"] if kind == "disabled" else (C["buttonText"] if kind == "primary" else C["button2Text"])
    pad = 24 if size == "normal" else 16
    cv.text(x + w / 2, y + h / 2 + 1, text, FS["button"] if size == "normal" else FS["buttonSmall"], col, True, "mm",
            maxw=w - 2 * pad, upper=True)
    return h


def tabs(cv, x, y, w, names, sel):
    n = len(names)
    tw = (w - TAB_GAP * (n - 1)) / n
    for i, nm in enumerate(names):
        button(cv, x + i * (tw + TAB_GAP), y + TAB_MARGIN, tw, nm, "primary" if i == sel else "secondary")
    return TAB_MARGIN + BTN_H + TAB_MARGIN


def well(cv, x, y, w, h):
    cv.rect((x, y, x + w, y + h), C["well"])


def section(cv, x, y, text, col=None):
    cv.text(x + 2, y + 10, text, FS["section"], col or C["section"], True, upper=True)
    return 10 + 20 + 4


def prop(cv, x, y, key, val, vcol=None, key_w=PROP_KEY_W, w=None):
    cv.text(x, y + PROP_ROW_H / 2, key, FS["propKey"], C["propKey"], True, "lm", maxw=key_w)
    cv.text(x + key_w + 8, y + PROP_ROW_H / 2, val, FS["propValue"], vcol or C["value"], False, "lm",
            maxw=(w - key_w - 8) if w else None)
    return PROP_ROW_H + 2


def frame(cv, x, y, size=SLOT_FRAME, icon=None, border="slotBorder", empty_text=None):
    cv.rect((x, y, x + size, y + size), C[border])
    cv.rect((x + 2, y + 2, x + size - 2, y + size - 2), "#0f151d")
    if icon is not None:
        isz = size - 4
        cv.paste(icon if icon.size[0] == isz else icon.resize((isz, isz), Image.LANCZOS), x + 2, y + 2)
    elif empty_text:
        cv.text(x + size / 2, y + size / 2, empty_text, 13, C["captionLight"], True, "mm")


def static_row(cv, x, y, w, h, icon=None, name="", sub=None, tag=None, tag_col=None, bar=True, name_col=None,
               state="static", action=None, action_kind="secondary", icon_size=40):
    aw = ROW_ACTION_W if action else 0
    pw = w - ((4 + aw) if action else 0)
    bg = C["selected"] if state == "selected" else C["row"]
    cv.rect((x, y, x + pw, y + h), bg)
    cx = x + 8
    if bar is not False:
        if bar:
            cv.rect((cx, y, cx + 4, y + h), C["selected"] if state != "selected" else "#7a9cc6")
        cx += 12
    if icon is not None:
        frame_y = y + (h - icon_size) / 2
        cv.paste(icon if icon.size[0] == icon_size else icon.resize((icon_size, icon_size), Image.LANCZOS), cx, frame_y)
        cx += icon_size + 12
    if sub:
        cv.text(cx, y + h / 2 - 11, name, FS["rowName"], name_col or C["rowName"], True, "lm")
        cv.text(cx, y + h / 2 + 12, sub, FS["rowSub"], C["rowSub"], False, "lm", maxw=pw - (cx - x) - 170)
    else:
        cv.text(cx, y + h / 2, name, FS["rowName"], name_col or C["rowName"], True, "lm")
    if tag:
        cv.text(x + pw - 8, y + h / 2, tag, FS["rowBadge"], tag_col or C["rowBadge"], False, "rm")
    if action:
        button(cv, x + pw + 4, y + (h - BTN_SMALL_H) / 2, aw, action, action_kind, "small")
    return h + ROW_GAP


def stat_bar(cv, x, y, w, h, frac, col):
    cv.rect((x, y, x + w, y + h), C["progressTrack"])
    fw = int(round(w * max(0.0, min(1.0, frac))))
    if fw > 0:                                                                   # stat_bar drops its fill at 0
        cv.rect((x, y, x + fw, y + h), C[col] if col in C else col)


def status_line(cv, x, y, text):
    mark = text[0]
    col = {"+": C["success"], "-": C["error"], "=": C["info"]}[mark]
    cv.text(x, y + 15, text, FS["default"], col, True, "lm")
    return 30


def separator(cv, x, y, w):
    cv.rect((x, y + 8, x + w, y + 9), C["separator"])
    return 17


def note(cv, x, y, lines, w=420, size=15, col=None, head=None):
    if head:
        cv.text(x, y, head, 16, STAND["tint"], True)
        y += 24
    for ln in lines:
        y = cv.wrap(x, y, ln, size, col or STAND["note"], w)
        y += 3
    return y


def callout(cv, x, y, n):
    r = 13
    cv.d.ellipse((x - r, y - r, x + r, y + r), fill=rgba("#e8a93b"), outline=rgba("#3a2a10"), width=2)
    cv.text(x, y + 1, str(n), 15, "#1a1206", True, "mm")


# ---------------------------------------------------------------- world backgrounds (our own flat drawing)
def water_patch(w, h, seed):
    rnd = random.Random(seed)
    im = Image.new("RGBA", (w, h), rgba("#2f6f86"))
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / max(1, h - 1)
        d.line((0, y, w, y), fill=rgba(mix("#3f87a0", "#245c72", t)))
    for _ in range(w * h // 4000):
        x, y = rnd.randrange(w), rnd.randrange(h)
        ln = rnd.randrange(10, 34)
        d.line((x, y, x + ln, y), fill=rgba(mix("#5fa2b8", "#3f87a0", 0.3 + rnd.random() * 0.5)), width=1)
    return im


def hud_strip(cv, x, y, w, h, seed):
    cv.paste(water_patch(w, h, seed), x, y)


def scene(seed=7):
    """The 1920 x 1080 world during a fight, our own flat drawing; HUD bits are kit-shaped stand-ins."""
    W, H = 1920, 1080
    sc = Canvas(W, H, "#86b6dc")
    for y in range(0, 470):
        sc.d.line((0, y, W, y), fill=rgba(mix("#7fb2df", "#c9e2ef", y / 470)))
    sc.d.polygon([(0, 470), (180, 400), (420, 430), (600, 380), (760, 440), (900, 470)], fill=rgba("#5d7f62"))
    sc.d.polygon([(1100, 470), (1300, 330), (1420, 360), (1560, 300), (1760, 400), (1920, 380), (1920, 470)],
                 fill=rgba("#567a5c"))
    sc.d.polygon([(1180, 470), (1330, 390), (1500, 420), (1700, 470)], fill=rgba("#4b6d51"))
    sc.paste(water_patch(W, H - 470, seed), 0, 470)
    # voxel shore (our own blocks)
    for i in range(0, 13):
        bx, by = -40 + i * 64, 820 + (i % 3) * 8 + i * 22
        sc.rect((bx, by, bx + 64, H), "#5b8a3c")
        sc.rect((bx, by, bx + 64, by + 14), "#76a84d")
        sc.rect((bx, by + 14, bx + 64, H), "#6b4b2e") if i % 4 == 0 else None
    # bobber, line, rod (first person, bottom right)
    bx, by = 760, 690
    sc.d.ellipse((bx - 34, by - 6, bx + 34, by + 14), outline=rgba("#cfe6ee"), width=3)
    sc.d.ellipse((bx - 12, by - 14, bx + 12, by + 8), fill=rgba("#d23c2c"))
    sc.d.ellipse((bx - 12, by - 4, bx + 12, by + 10), fill=rgba("#f2f2f2"))
    sc.d.line((bx, by - 12, 1195, 640), fill=rgba("#f4f8fa"), width=2)
    sc.d.line((1195, 640, 1440, 1080), fill=rgba("#2e2015"), width=20)
    sc.d.line((1195, 640, 1440, 1080), fill=rgba("#6c4a2c"), width=13)
    sc.d.line((1350, 920, 1440, 1080), fill=rgba("#c6a070"), width=26)
    sc.d.ellipse((1330, 880, 1400, 950), fill=rgba("#5a636c"))
    sc.d.ellipse((1340, 890, 1390, 940), fill=rgba(METAL["Iron"]))
    # "!" above the bobber (world sign; the real look is UNVERIFIED: particle / model / floating text)
    sc.text(bx, by - 90, "!", 84, "#ffcc00", True, "mm")
    # reticle
    sc.d.line((952, 540, 968, 540), fill=(255, 255, 255, 200), width=2)
    sc.d.line((960, 532, 960, 548), fill=(255, 255, 255, 200), width=2)
    # vanilla-like HUD stand-ins: hotbar 9 slots + vitals (positions UNVERIFIED)
    hb_w = 9 * 66
    hx, hy = (W - hb_w) // 2, H - 92
    for i in range(9):
        sc.rect((hx + i * 66, hy, hx + i * 66 + 62, hy + 62), "#000000(0.35)", outline="#ffffff(0.25)")
    sc.rect((hx, hy, hx + 62, hy + 62), "#000000(0.35)", outline="#ffffff(0.8)", width=2)
    sc.paste(icon_rod(56, "Copper", "Iron"), hx + 3, hy + 3)
    stat_bar(sc, hx, hy - 26, 280, 12, 0.86, "#c94a4a")
    stat_bar(sc, hx + hb_w - 280, hy - 26, 280, 12, 0.64, "#d8b74a")
    # the fishing widget at 1:1 on the 1920 screen, 150 px above the vitals
    hud_widget(sc, (W - 440) // 2, hy - 26 - 150 - 96, "fight", 0.55, "8.4 s", "7 per s")
    # SkyyHud coins widget stand-in (existing widget, top left)
    sc.rect((20, 20, 210, 60), C["hud"])
    sc.text(40, 40, "Coins 12,450", 16, C["gold"], True, "lm")
    return sc.im


# ---------------------------------------------------------------- B: the minigame HUD widget (440 x 96, panel "hud")
def hud_widget(cv, x, y, state, frac, right, cps=None):
    w, h = 440, 96
    cv.rect((x, y, x + w, y + h), C["hud"])
    px, py = x + 20, y + 10
    heads = {"bite": ("BITE", C["warning"]), "fight": ("REEL IN", C["title"]), "surge": ("SURGE", C["error"]),
             "almost": ("REEL IN", C["title"]), "lost": ("IT GOT AWAY", C["error"])}
    head, hcol = heads[state]
    cv.text(px, py + 10, head, 16, hcol, True, "lm")
    rcol = C["warning"] if state in ("bite", "almost") else C["value"]
    if right:
        cv.text(x + w - 20, py + 10, right, 16, rcol, True, "rm")
    by = py + 26
    if state == "lost":
        cv.text(px, by + 11, "The bar ran empty", FS["caption"], C["caption"], False, "lm")
        cv.text(px, by + 38, "Cast again - nothing is lost", FS["caption"], C["captionLight"], False, "lm")
        return
    col = {"bite": "warning", "fight": "progressBlue", "surge": "error", "almost": "progressGreen"}[state]
    stat_bar(cv, px, by, 400, 22, frac, C[col])
    if state != "bite":
        tx = px + int(400 * 0.35)
        cv.rect((tx - 1, by - 3, tx + 1, by + 25), C["gold"])
    hint = {"bite": "1.2 s window - Use now", "fight": "Click Use fast", "surge": "The fish pulls hard",
            "almost": "Almost"}[state]
    cv.text(px, by + 38, hint, FS["caption"], C["caption"], False, "lm")
    if cps:
        cv.text(x + w - 20, by + 38, cps, FS["caption"], C["info"], True, "rm")


# ---------------------------------------------------------------- C: the catch card (HUD, 460 x 132)
def catch_card(cv, x, y, kind, icon, name, name_col, l1, l1col, l2, l2col, right_top, right_col, foot):
    w, h = 460, 132
    cv.rect((x, y, x + w, y + h), C["hud"])
    px, py = x + 20, y + 10
    head = {"fish": ("LANDED", C["success"]), "treasure": ("LOST PROPERTY", C["gold"]), "junk": ("JUNK", C["disabled"])}[kind]
    cv.text(px, py + 10, head[0], 16, head[1], True, "lm")
    cv.text(x + w - 20, py + 10, right_top, 16, right_col, True, "rm")
    fy = py + 26
    frame(cv, px, fy, SLOT_FRAME, icon, empty_text=None if icon is not None else "vanilla")
    tx = px + SLOT_FRAME + 12
    cv.text(tx, fy + 12, name, FS["heading"], name_col, True, "lm", maxw=w - (tx - x) - 20)
    cv.text(tx, fy + 36, l1, 16, l1col, True, "lm")
    if l2:
        cv.text(tx, fy + 58, l2, FS["caption"], l2col, True if l2col == C["gold"] else False, "lm")
    cv.text(px, y + h + 16, foot, 14, STAND["noteDim"], False, "lm")


# ---------------------------------------------------------------- D: Fishing Bench, RIG tab (1000 x 760)
def bench_rig(cv, x, y):
    W, H = 1000, 760
    bx, by, bw, bh = window(cv, x, y, W, H, "Fishing Bench")
    cy = by
    cy += tabs(cv, bx, cy, bw, ["Parts", "Rig", "Fillet", "Recipes"], 1)
    cv.text(bx, cy + 10, "Put a rod in, then fit a reel, hook, line and sinker. Parts come off for free.", 16, C["text"], False,
            "lm")
    cy += 28
    top_h = 329
    lw = 520
    rw = bw - lw - 12
    # left well: YOUR RIG
    well(cv, bx, cy, lw, top_h)
    lx, ly = bx + WELL_PAD, cy + WELL_PAD
    frame(cv, lx, ly, 72, icon_rod(68, "Copper", "Iron"))
    cv.text(lx + 72 + 14, ly + 14, "Copper Rod", FS["heading"], RARITY["Rare"], True, "lm")
    cv.text(lx + 72 + 14, ly + 38, "Rare - Lv 12 - reforged", FS["rowSub"], C["rowSub"], False, "lm")
    cv.text(lx + 72 + 14, ly + 60, "Max fish weight 6 kg", FS["rowSub"], C["value"], False, "lm")
    ly += 72 + 10
    parts = [("Reel", icon_reel(40, "Iron"), "Iron Reel", "Reel Power 5.7 per click", True),
             ("Hook", icon_hook(40, "Copper", "lure"), "Lure Hook I", "Fishing Speed +5", True),
             ("Line", None, "Empty", "Click a line below to fit it", False),
             ("Sinker", icon_sinker(40, kind="weighted"), "Weighted Sinker I", "Bar start +5", True)]
    rowh = 48
    for slot, ic, nm, sub, have in parts:
        cv.text(lx + 4, ly + rowh / 2, slot, FS["section"], C["section"], True, "lm", upper=True)
        rx = lx + 84
        rwid = lw - 2 * WELL_PAD - 84
        pw = rwid - 4 - ROW_ACTION_W
        cv.rect((rx, ly, rx + pw, ly + rowh), C["row"])
        frame(cv, rx + 6, ly + 2, 44, ic, empty_text="+" if ic is None else None)
        if ic is None:
            cv.text(rx + 6 + 22, ly + 2 + 22, "+", 24, C["captionLight"], True, "mm")
        cv.text(rx + 62, ly + rowh / 2 - 10, nm, FS["rowName"], C["rowName"] if have else C["disabled"], True, "lm")
        cv.text(rx + 62, ly + rowh / 2 + 12, sub, FS["rowSub"], C["rowSub"], False, "lm")
        if have:
            button(cv, rx + pw + 4, ly + (rowh - BTN_SMALL_H) / 2, ROW_ACTION_W, "Remove", "secondary", "small")
        else:
            button(cv, rx + pw + 4, ly + (rowh - BTN_SMALL_H) / 2, ROW_ACTION_W, "Remove", "disabled", "small")
        ly += rowh + 7
    # right well: RIG TOTAL
    rx0 = bx + lw + 12
    well(cv, rx0, cy, rw, top_h)
    qx, qy = rx0 + WELL_PAD, cy + WELL_PAD - 10
    qy += section(cv, qx, qy, "Rig total")
    kw = 160
    stats = [("Max fish weight", "6 kg", None), ("Reel Power", "5.7 per click", None),
             ("Fishing Speed", "+8", C["success"]), ("Treasure Chance", "5.4%", C["success"]),
             ("Grade luck", "-", C["disabled"]), ("Bar start", "40", C["success"]), ("Time limit", "12 s", None),
             ("Double catch", "-", C["disabled"]), ("Junk", "10%", None), ("Fishing Wisdom", "+2%", C["success"])]
    for k, v, col in stats:
        qy += prop(cv, qx, qy, k, v, col, key_w=kw, w=rw - 2 * WELL_PAD)
    cy += top_h
    # parts in your bags (item_grid, 13 x 2 cells of 64 + 2)
    cy += section(cv, bx, cy - 4, "Parts in your bags - click one to fit it") - 4
    gh = 2 * 66 - 2 + 2 * WELL_LIST_PAD
    well(cv, bx, cy, bw, gh)
    grid_items = [icon_reel(56, "Copper"), icon_hook(56, "Copper", "barbed"), icon_line(56), icon_line(56, "#7fb6d8"),
                  icon_sinker(56, kind="clean"), icon_hook(56, "Iron", "barbed"), icon_sinker(56, "#6d737a", "weighted")]
    for i in range(26):
        gx = bx + (bw - 13 * 66 + 2) // 2 + (i % 13) * 66
        gy = cy + WELL_LIST_PAD + (i // 13) * 66
        cv.rect((gx, gy, gx + 64, gy + 64), C["row"], outline=C["slotBorder"], width=2)
        if i < len(grid_items):
            cv.paste(grid_items[i], gx + 4, gy + 4)
        if i == 2:
            cv.rect((gx, gy, gx + 64, gy + 64), None, outline=C["selected"], width=2)
    cy += gh + 8
    cy += status_line(cv, bx, cy, "+ Fitted Weighted Sinker I")
    cy += separator(cv, bx, cy, bw)
    button(cv, bx, cy, 200, "Take rod out", "secondary")
    button(cv, bx + bw - BTN_MIN_W, cy, BTN_MIN_W, "Close", "secondary")
    cy += BTN_H
    return cy - by, bh        # used vs inner height


# ---------------------------------------------------------------- E: Pond Fish collection page (1000 x 760, plain window)
POND = [  # (icon id, name, rarity, kg range, K from the catalog: min kg / min cm)
    ("overdue_minnow", "Overdue Minnow", "Normal", (0.05, 18)), ("bluegill_of_good_standing", "Bluegill of Good Standing",
                                                                   "Normal", (0.1, 20)),
    ("rustback_trout", "Rustback Trout", "Normal", (0.5, 37)), ("queue_perch", "Queue Perch", "Normal", (0.3, 30)),
    ("misfiled_carp", "Misfiled Carp", "Unique", (2, 52)), ("stamped_catfish", "Stamped Catfish", "Unique", (3.5, 73)),
    ("mirebridge_eel", "Mirebridge Eel", "Unique", (1, 55)), ("pondering_pike", "Pondering Pike", "Rare", (6.5, 93)),
    ("golden_receipt_koi", "Golden Receipt Koi", "Legendary", (1.5, 47)),
    ("departmental_goldfish", "Departmental Goldfish", "Fabled", (0.2, 26)),
]


def length_cm(name, kg):
    """Spec formula L = (100 x grams / K)^(1/3); K fitted to the catalog's min weight / min length."""
    for ic, nm, rar, (mkg, mcm) in POND:
        if nm == name:
            k = 100 * mkg * 1000 / mcm ** 3
            return int(round((100 * kg * 1000 / k) ** (1.0 / 3)))
    raise KeyError(name)


def collection_page(cv, x, y):
    W, H = 1000, 760
    bx, by, bw, bh = window(cv, x, y, W, H, "Pond Fish", plain=True)
    cy = by
    # summary row
    frame(cv, bx, cy, SLOT_FRAME, icon_fish("rustback_trout", 64))
    tx = bx + SLOT_FRAME + 14
    cv.text(tx, cy + 12, "Pond Fish - Tier IV", FS["heading"], C["rowName"], True, "lm")
    cv.text(tx, cy + 36, "Zone 1 ponds and rivers. Every fish you land by fishing counts.", FS["rowSub"], C["rowSub"], False,
            "lm")
    stat_bar(cv, tx, cy + 52, 560, MEMBAR_H, 312 / 500.0, "progressFill")
    cv.text(tx + 560 + 12, cy + 52 + 11, "312 / 500 to Tier V", 16, C["value"], True, "lm")
    cy += 84
    lw = 470
    rw = bw - lw - 12
    col_h = 505
    # left: tiers (scroll_list on the well)
    sy = cy
    cy2 = cy + section(cv, bx, cy - 6, "Tiers") - 6
    lh = col_h - (cy2 - sy)
    well(cv, bx, cy2, lw, lh)
    tiers = [("Tier I - 25", "Bigger Fish Cooler + coins", "Done", C["success"]),
             ("Tier II - 50", "Barbed Hook I, Lure Hook I", "Done", C["success"]),
             ("Tier III - 100", "Copper Rod (+ Copper IV)", "Done", C["success"]),
             ("Tier IV - 250", "Copper Reel, three sinkers", "Done", C["success"]),
             ("Tier V - 500", "Lost Property Hook I, two lines", "312 / 500", C["value"]),
             ("Tier VI - 1,000", "Iron Rod, Angler armor T0-T2", "Locked", C["disabled"]),
             ("Tier VII - 2,500", "Iron Reel, Twin Line I", "Locked", C["disabled"]),
             ("Tier VIII - 5,000", "Fishing Speed +1% for good", "Locked", C["disabled"])]
    ry = cy2 + WELL_LIST_PAD
    inner_w = lw - 2 * WELL_LIST_PAD - 12
    clip_bottom = cy2 + lh - WELL_LIST_PAD
    for i, (nm, sub, tag, tcol) in enumerate(tiers):
        if ry + ROW_H_READABLE > clip_bottom:
            # the scroll list cuts the next row (vanilla TopScrolling)
            part = Canvas(inner_w, ROW_H_READABLE, "#00000000")
            static_row(part, 0, 0, inner_w, ROW_H_READABLE, None, nm, sub, tag, tcol, bar=None,
                       name_col=C["disabled"] if tag == "Locked" else None)
            vis = int(clip_bottom - ry)
            if vis > 0:
                cv.paste(part.im.crop((0, 0, inner_w, vis)), bx + WELL_LIST_PAD, ry)
            break
        ry += static_row(cv, bx + WELL_LIST_PAD, ry, inner_w, ROW_H_READABLE, None, nm, sub, tag, tcol,
                         bar=(i == 4) if i == 4 else None, name_col=C["disabled"] if tag == "Locked" else None)
    # all 8 tiers fit: no scrollbar shown (scroll_list adds one only when the rows overflow)
    # right: species found
    rx0 = bx + lw + 12
    cy3 = cy + section(cv, rx0, cy - 6, "Species found 8 / 10") - 6
    gw = rw
    gh = 2 * (88 + 4) + 2 * WELL_LIST_PAD - 4
    well(cv, rx0, cy3, gw, gh)
    found = {"overdue_minnow", "bluegill_of_good_standing", "rustback_trout", "queue_perch", "misfiled_carp",
             "stamped_catfish", "mirebridge_eel", "pondering_pike"}
    cell = 88
    gap = (gw - 2 * WELL_LIST_PAD - 5 * cell) // 4
    for i, (ic, nm, rar, _) in enumerate(POND):
        cx = rx0 + WELL_LIST_PAD + (i % 5) * (cell + gap)
        cyy = cy3 + WELL_LIST_PAD + (i // 5) * (cell + 4)
        sel = ic == "rustback_trout"
        cv.rect((cx, cyy, cx + cell, cyy + cell), C["selected"] if sel else C["row"])
        img = icon_fish(ic, 64)
        if ic in found:
            cv.paste(img, cx + 12, cyy + 8)
        else:
            cv.paste(silhouette(img), cx + 12, cyy + 8)
            cv.text(cx + cell / 2, cyy + 40, "?", 22, C["captionLight"], True, "mm")
        dot = RARITY[rar] if ic in found else C["captionLight"]
        cv.rect((cx + cell / 2 - 14, cyy + cell - 10, cx + cell / 2 + 14, cyy + cell - 7), dot)
    dy = cy3 + gh + 8
    dh = col_h - (dy - sy)
    well(cv, rx0, dy, gw, dh)
    qx, qy = rx0 + WELL_PAD, dy + WELL_PAD
    cv.text(qx, qy + 12, "Rustback Trout", FS["heading"], RARITY["Normal"], True, "lm")
    cv.text(rx0 + gw - WELL_PAD, qy + 12, "Normal", FS["rowBadge"], C["rowBadge"], False, "rm")
    qy += 32
    best_kg = 4.12
    rows = [("Where", "rivers, cold ponds"), ("When", "spring, autumn - dawn, dusk"),
            ("Your best", "%.2f kg - %d cm" % (best_kg, length_cm("Rustback Trout", best_kg))),
            ("Caught", "41"), ("Server record", "%.2f kg - %d cm" % (4.88, length_cm("Rustback Trout", 4.88))),
            ("Sells for", "26 coins per kg")]
    for k, v in rows:
        qy += prop(cv, qx, qy, k, v, C["gold"] if k == "Sells for" else None, key_w=130, w=gw - 2 * WELL_PAD)
    cy = sy + col_h + 8
    cy += status_line(cv, bx, cy, "= Tier V at 500 unlocks the Lost Property Hook I")
    cy += separator(cv, bx, cy, bw)
    button(cv, bx, cy, BTN_MIN_W, "Back", "secondary")
    button(cv, bx + bw - BTN_MIN_W, cy, BTN_MIN_W, "Close", "secondary")
    cy += BTN_H
    return cy - by, bh


# ---------------------------------------------------------------- the sheet
def main():
    CW, CH = 2200, 2330
    cv = Canvas(CW, CH, STAND["canvas"])
    M = 50
    cv.text(M, 46, "SkyyFishing - UI mockup v2 (cloud draft 2026-10-08, paper only)", 30, STAND["tint"], True, "lm")
    cv.text(M, 84, "Colours, sizes and text scale from tools/skyyui.py (kit 1.4, readable scale). Frames, button textures and "
                   "fonts are flat stand-ins for the vanilla textures; pages and HUD drawn 1:1, the screen at 50%.",
            16, STAND["noteDim"], False, "lm")

    # A - the screen
    ay = 130
    cv.text(M, ay, "A. THE SCREEN DURING A FIGHT (1920 x 1080 at 50%)", 17, STAND["tint"], True, "lm")
    shot = scene().resize((960, 540), Image.LANCZOS)
    cv.paste(shot, M, ay + 20)
    cv.rect((M, ay + 20, M + 960, ay + 560), None, outline="#2b3542")
    callout(cv, M + 380, ay + 20 + 245, 1)
    callout(cv, M + 380 - 140, ay + 20 + 360, 2)
    note(cv, M, ay + 578, ["1  The bite: a yellow \"!\" over the bobber + a splash (world, not UI).",
                           "2  The fishing widget: a HUD panel, 150 px above the vitals, centred. Never a page - the mouse "
                           "stays free for clicking Use."], w=960, size=15)

    # B - widget states
    bx = M + 960 + 60
    cv.text(bx, ay, "B. MINIGAME WIDGET (HUD, 1:1, 440 x 96, panel hud #000000(0.2))", 17, STAND["tint"], True, "lm")
    states = [("bite", 0.62, "Use now", None, "1  BITE", ["Yellow word + a 1.2 s draining bar. Miss it = the fish swims off."]),
              ("fight", 0.55, "8.4 s", "7 per s", "2  REEL IN",
               ["Bar 0-100 starts at the gold tick (35, the sinker moves it). Clicks push it up, the fish pulls it down.",
                "Click rate shown so slow clickers see why they lose."]),
              ("surge", 0.38, "6.1 s", "8 per s", "3  SURGE", ["0.6 s pull x1.6 every 3 s: word + fill turn error red."]),
              ("almost", 0.88, "3.0 s", "9 per s", "4  ALMOST", ["Above 80 the fill turns green; timer yellow under 4 s."]),
              ("lost", 0.0, "", None, "5  LOST", ["Bar empty or time up. Shown 2 s, then hidden."])]
    sy = ay + 20
    for st, fr, right, cps, head, lines in states:
        hud_strip(cv, bx, sy, 480, 116, 11 + len(head))
        hud_widget(cv, bx + 20, sy + 10, st, fr, right, cps)
        note(cv, bx + 500, sy + 8, lines, w=600, size=15, head=head)
        sy += 116 + 12

    # C - catch card
    cy = 860
    cv.text(M, cy, "C. CATCH CARD (HUD, 1:1, 460 x 132, same panel; replaces the widget for 3 s, + one chat line)", 17,
            STAND["tint"], True, "lm")
    cards = [
        ("fish", icon_fish("stamped_catfish", 64), "Stamped Catfish", RARITY["Unique"],
         "7.80 kg - %d cm" % length_cm("Stamped Catfish", 7.80), C["white"], "New personal record", C["gold"], "Unique",
         RARITY["Unique"], "Chat: You caught a Stamped Catfish, 7.80 kg."),
        ("fish", icon_fish("rustback_trout", 64), "Rustback Trout", RARITY["Normal"],
         "2.41 kg - %d cm" % length_cm("Rustback Trout", 2.41), C["white"], "Pond Fish 312 / 500", C["caption"], "Normal",
         RARITY["Normal"], "No record line when it is not one."),
        ("treasure", icon_fish("lost_property_envelope", 64), "Lost Property Envelope", C["rowName"],
         "Great - open it from your bag", C["white"], "Coins, a gear box or materials", C["caption"], "Great", C["gold"],
         "Our own item: it opens into the treasure table."),
        ("junk", None, "Stick", C["rowName"], "x1 - goes to your bag", C["white"], "Junk counts for no collection",
         C["caption"], "", C["disabled"], "Junk = a vanilla item with its own vanilla icon."),
    ]
    xx = M
    for i, cd in enumerate(cards):
        kind, ic, nm, ncol, l1, l1c, l2, l2c, rt, rc, foot = cd
        px = M + i * 530
        hud_strip(cv, px, cy + 20, 500, 152, 31 + i)
        catch_card(cv, px + 20, cy + 30, kind, ic, nm, ncol, l1, l1c, l2, l2c, rt, rc, foot)
    note(cv, M, cy + 222, ["Name in the fish's rarity colour (pack ladder: Normal white, Unique yellow, Rare pink ...). "
                           "Length is worked out from the weight (spec formula L = (100 x g / K)^(1/3)). Species, rarity and "
                           "weight stay hidden until the fish is landed."], w=2100, size=15)

    # D + E - pages
    py = 1150
    cv.text(M, py, "D. FISHING BENCH - RIG TAB (1:1, 1000 x 760, decorated window, 4 tabs)", 17, STAND["tint"], True, "lm")
    ex = M + 1000 + 100
    cv.text(ex, py, "E. POND FISH COLLECTION (1:1, 1000 x 760, plain list window)", 17, STAND["tint"], True, "lm")
    used_d, inner_d = bench_rig(cv, M, py + 40)
    used_e, inner_e = collection_page(cv, ex, py + 40)
    assert used_d <= inner_d and used_e <= inner_e, (used_d, inner_d, used_e, inner_e)
    note(cv, M, py + 40 + 760 + 22,
         ["Rod slot: the icon is the rod item (its default reel - icons are per item id); the name line and Rig total show "
          "the fitted reel. Stat values in the vanilla value colour; bonuses green, none grey. Grid = item_grid, "
          "ItemStack(id, qty) only.", "Parts, Fillet and Recipes tabs: unchanged from v1 (kept in Fishing-UI-Mockup-v1.png)."],
         w=1000, size=15)
    note(cv, ex, py + 40 + 760 + 22,
         ["Tiers on a scrolling well (vanilla never pages). Species grid: found = our icon, missing = a dark shape + \"?\". "
          "Click a fish to see its details below. Rarity bar under each found fish.",
          "Stage 1 only has Pond Fish; Dune / Frost / Lava / Cave and Lost Property use the same page."], w=1000, size=15)

    # F - kit colours used
    fy = 2060
    cv.text(M, fy, "F. KIT COLOURS USED (tools/skyyui.py COLOR names)", 17, STAND["tint"], True, "lm")
    names = ["text", "title", "rowName", "rowSub", "section", "propKey", "value", "caption", "captionLight", "disabled",
             "success", "error", "warning", "info", "gold", "selected", "row", "well", "hud", "slotBorder", "progressTrack",
             "progressFill", "progressBlue", "progressGreen", "separator"]
    for i, n in enumerate(names):
        sx = M + (i % 9) * 236
        syy = fy + 24 + (i // 9) * 66
        cv.rect((sx, syy, sx + 40, syy + 40), STAND["body"])
        cv.rect((sx, syy, sx + 40, syy + 40), C[n], outline="#3a4659")
        cv.text(sx + 50, syy + 12, n, 15, STAND["tint"], True, "lm")
        cv.text(sx + 50, syy + 32, C[n], 13, STAND["noteDim"], False, "lm")

    cv.im.convert("RGB").save(OUT, "PNG", optimize=True)
    print("wrote", OUT, cv.im.size, "rig used %d / %d, collection used %d / %d" % (used_d, inner_d, used_e, inner_e))


if __name__ == "__main__":
    main()
