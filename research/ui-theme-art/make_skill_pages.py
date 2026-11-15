"""SkyWynn skill pages + shard clicker - concept art (2026-11-14), same Skyglass theme / Sky Azure accent as the approved v5 art.

Skyy's words: docs/answered/ui.md 2026-11-14 "SKILL PAGE LAYOUT" + docs/answered/world.md 2026-11-14 "SHARDS -> MENU CLICKER";
idea notes: research/Shard-Clicker-Idea.md. README: research/ui-theme-art/README.md ("Skill pages + shard clicker").

Writes, next to this file (1920 x 1080):
  skill-page-mining.png              one page per skill (Mining, Lv 31): gear, collections path, skill tree, stats, shard card
  skill-page-mining-locked.png       the same page for a Mining Lv 6 player: shard card LOCKED (Lv 10)
  shard-clicker-foraging.png         the Foraging shard clicker: small T1 Oak Island, one tree to click, one spirit totem, upgrades
  shard-clicker-foraging-grown.png   the same island upgraded: bigger, 4 trees, 2 spirit totems, weather totem, decorations, bridge
  shard-clicker-zoomed-out.png       zoomed-out map of the islands (T1 Oak, T2 Beech, T3 Maple locked, T4 Dry locked)

Deterministic (no randomness, no timestamps): two runs give the same bytes. Imports the UI kit helpers from make_ui_theme.py (it does
not change that file's output) and the tree layout relax pass from tools/skyymap.py. Item / node pictures: only our own committed icons
(art/, research/cloud/*-art/). The spirits, totems, islands and trees are ORIGINAL drawings made here in code.
Run: PYTHONPATH=<tools/dev/scratch/pil> python research/ui-theme-art/make_skill_pages.py [file.png ...]
"""
import importlib.util
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))

from PIL import Image, ImageDraw, ImageFilter  # noqa: E402
import make_ui_theme as K  # noqa: E402
from make_ui_theme import (PAL, A, RAR, rgb, mix, font, tw, text, rich, paste_icon, put, ss_glyph, grad_fill, outline, hline,  # noqa: E402
                           taper_line, glow, panel, panel_title, button, slot, key_cap, toggle, bar, level_pill, chip, row,
                           g_diamond, g_coin, g_check, g_x, g_chev, g_search, g_plus, g_pencil, window_v4, px_armor, put_px, px_icon,
                           I_WARP, I_NODE, I_ACC, I_ENCH, I_HUB, I_MENU2, I_PET)
import skyymap  # noqa: E402

_spec = importlib.util.spec_from_file_location("trees_v3_data", os.path.join(ROOT, "tools", "trees_v3_data.py"))
TV3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TV3)
MINING_TREE = [t for t in TV3.TREES if t["name"] == "Mining"][0]

TREE_COL = "#8fc8ff"     # SUI.TREE_COLOR["Mining"] (tools/skyyui.py)
GOLD = "#E8A93B"         # skyymap ART gold
TIER = {"Copper": "#e08a4a", "Iron": "#b8c4d0", "Thorium": "#7fd07a", "Cobalt": "#6f9cff", "Adamantite": "#e0675a",
        "Mithril": "#8fe6ff", "Onyxium": "#b98ae8"}


def C(c):
    if c is None:
        return None
    if isinstance(c, str):
        return rgb(c)
    if len(c) == 2 and isinstance(c[0], str):
        return rgb(c[0], c[1])
    return c


# ================================================================================================================ supersampled art canvas
class Art:
    """Draw at s x size in art px, then resize down (anti-aliased). All coordinates in art px."""

    def __init__(self, w, h, s=3, bg=(0, 0, 0, 0)):
        self.w, self.h, self.s = w, h, s
        self.im = Image.new("RGBA", (w * s, h * s), bg)
        self.d = ImageDraw.Draw(self.im, "RGBA")

    def P(self, pts):
        return [(x * self.s, y * self.s) for x, y in pts]

    def _local(self, xs, ys, pad, fn):
        """Draw fn(draw, ox, oy) on a small layer around the points (big px) and alpha-composite it (real blending)."""
        X0, Y0 = int(math.floor(min(xs) - pad)), int(math.floor(min(ys) - pad))
        X1, Y1 = int(math.ceil(max(xs) + pad)), int(math.ceil(max(ys) + pad))
        lay = Image.new("RGBA", (max(1, X1 - X0), max(1, Y1 - Y0)), (0, 0, 0, 0))
        fn(ImageDraw.Draw(lay), X0, Y0)
        self._comp(lay, X0, Y0)

    def ell(self, cx, cy, rx, ry, fill, ol=None, w=1.0):
        s = self.s
        b = ((cx - rx) * s, (cy - ry) * s, (cx + rx) * s, (cy + ry) * s)
        self._local([b[0], b[2]], [b[1], b[3]], w * s + 2, lambda d, ox, oy: d.ellipse(
            (b[0] - ox, b[1] - oy, b[2] - ox, b[3] - oy), fill=C(fill), outline=C(ol), width=max(1, int(round(w * s))) if ol else 0))

    def poly(self, pts, fill, ol=None, w=1.0):
        P = self.P(pts)
        self._local([p[0] for p in P], [p[1] for p in P], w * self.s + 2, lambda d, ox, oy: d.polygon(
            [(x - ox, y - oy) for x, y in P], fill=C(fill), outline=C(ol), width=max(1, int(round(w * self.s))) if ol else 1))

    def line(self, pts, fill, w=1.0):
        P = self.P(pts)
        ww = max(1, int(round(w * self.s)))
        self._local([p[0] for p in P], [p[1] for p in P], ww + 2, lambda d, ox, oy: d.line(
            [(x - ox, y - oy) for x, y in P], fill=C(fill), width=ww, joint="curve"))

    def rect(self, box, fill, r=0, ol=None, w=1.0):
        s = self.s
        x0, y0, x1, y1 = box
        if x1 <= x0 or y1 <= y0:
            return
        r = min(r, (x1 - x0) / 2.0, (y1 - y0) / 2.0)
        b = (x0 * s, y0 * s, x1 * s, y1 * s)
        self._local([b[0], b[2]], [b[1], b[3]], w * s + 2, lambda d, ox, oy: d.rounded_rectangle(
            (b[0] - ox, b[1] - oy, b[2] - ox, b[3] - oy), radius=r * s, fill=C(fill), outline=C(ol),
            width=max(1, int(round(w * s))) if ol else 0))

    def arc(self, box, a0, a1, fill, w=1.0):
        s = self.s
        b = tuple(v * s for v in box)
        self._local([b[0], b[2]], [b[1], b[3]], w * s + 2, lambda d, ox, oy: d.arc(
            (b[0] - ox, b[1] - oy, b[2] - ox, b[3] - oy), a0, a1, fill=C(fill), width=max(1, int(round(w * s)))))

    def chord(self, box, a0, a1, fill, ol=None):
        s = self.s
        b = tuple(v * s for v in box)
        self._local([b[0], b[2]], [b[1], b[3]], s + 2, lambda d, ox, oy: d.chord(
            (b[0] - ox, b[1] - oy, b[2] - ox, b[3] - oy), a0, a1, fill=C(fill), outline=C(ol), width=s))

    def glow(self, cx, cy, rx, ry, col, alpha=140, blur=10):
        s = self.s
        m = int(blur * 3)
        x0, y0 = int(cx - rx - m), int(cy - ry - m)
        w, h = int(2 * (rx + m)) + 2, int(2 * (ry + m)) + 2
        lay = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))
        ImageDraw.Draw(lay).ellipse(((cx - rx - x0) * s, (cy - ry - y0) * s, (cx + rx - x0) * s, (cy + ry - y0) * s), fill=C((col, alpha)))
        lay = lay.filter(ImageFilter.GaussianBlur(blur * s / 2.0))
        self._comp(lay, x0 * s, y0 * s)

    def _comp(self, lay, X, Y):
        W, H = self.im.size
        cx0, cy0 = max(0, -X), max(0, -Y)
        cx1, cy1 = min(lay.size[0], W - X), min(lay.size[1], H - Y)
        if cx1 <= cx0 or cy1 <= cy0:
            return
        self.im.alpha_composite(lay.crop((cx0, cy0, cx1, cy1)), (X + cx0, Y + cy0))

    def blob(self, box, fn, fill, ol="#10203a", ow=2.0, shade=None):
        """A cartoon shape: fn(d, T) draws white shapes on a local mask (T(x, y) -> mask px, T.s = scale); outlined by dilation."""
        s = self.s
        x0, y0, x1, y1 = box
        pad = int(ow * s) + 2
        W, H = int((x1 - x0) * s) + 2 * pad, int((y1 - y0) * s) + 2 * pad
        m = Image.new("L", (W, H), 0)

        def T(x, y):
            return ((x - x0) * s + pad, (y - y0) * s + pad)
        T.s = s
        fn(ImageDraw.Draw(m), T)
        X, Y = int(x0 * s) - pad, int(y0 * s) - pad
        if ol:
            k = int(ow * s) * 2 + 1
            big = m.filter(ImageFilter.MaxFilter(k if k % 2 else k + 1))
            lay = Image.new("RGBA", (W, H), C(ol))
            lay.putalpha(big)
            self._comp(lay, X, Y)
        lay = Image.new("RGBA", (W, H), C(fill))
        lay.putalpha(m)
        self._comp(lay, X, Y)
        return m, X, Y

    def done(self):
        return self.im.resize((self.w, self.h), Image.LANCZOS)


def paste_art(im, art_img, x, y):
    im.paste(art_img, (int(x), int(y)), art_img)


def grey_img(img, dark=0.55):
    g = img.convert("LA").convert("RGBA")
    g.putalpha(img.getchannel("A"))
    if dark < 1:
        g = Image.composite(Image.blend(g, Image.new("RGBA", g.size, (8, 12, 20, 255)), 1 - dark), g, img.getchannel("A"))
        g.putalpha(img.getchannel("A"))
    return g


# ================================================================================================================ drawn pieces (original)
def spirit(a, cx, cy, r, body="#9ff0ff", deep="#3a9ed8", hat=None, arms_up=False, carry=None):
    """A cute floating spirit: round head, curling wisp tail, big sparkly eyes, blush, tiny arms. hat: 'miner' / 'leaf' / None."""
    a.glow(cx, cy + r * 0.4, r * 1.55, r * 1.75, body, 120, r * 0.55)
    ol = mix(deep, "#0a1426", 0.55)

    def shape(d, T):
        s = T.s
        d.ellipse((*T(cx - r, cy - r), *T(cx + r, cy + r)), fill=255)
        pts = [(cx - r * 0.98, cy + r * 0.1), (cx - r * 0.85, cy + r * 0.75), (cx - r * 0.45, cy + r * 1.25), (cx + r * 0.05, cy + r * 1.55),
               (cx + r * 0.55, cy + r * 1.62), (cx + r * 0.95, cy + r * 1.45), (cx + r * 0.62, cy + r * 1.3), (cx + r * 0.6, cy + r * 1.0),
               (cx + r * 0.9, cy + r * 0.55), (cx + r * 0.98, cy + r * 0.1)]
        d.polygon([T(x, y) for x, y in pts], fill=255)
        d.ellipse((*T(cx + r * 0.78, cy + r * 1.28), *T(cx + r * 1.08, cy + r * 1.58)), fill=255)
        # little arms
        if arms_up:
            d.ellipse((*T(cx - r * 1.28, cy - r * 0.05), *T(cx - r * 0.82, cy + r * 0.38)), fill=255)
            d.ellipse((*T(cx + r * 0.82, cy - r * 0.05), *T(cx + r * 1.28, cy + r * 0.38)), fill=255)
        else:
            d.ellipse((*T(cx - r * 1.2, cy + r * 0.28), *T(cx - r * 0.78, cy + r * 0.66)), fill=255)
            d.ellipse((*T(cx + r * 0.78, cy + r * 0.28), *T(cx + r * 1.2, cy + r * 0.66)), fill=255)
    a.blob((cx - r * 1.4, cy - r * 1.1, cx + r * 1.4, cy + r * 1.75), shape, body, ol, max(1.4, r * 0.07))
    # soft shading + shine
    a.ell(cx + r * 0.25, cy + r * 0.55, r * 0.65, r * 0.45, (deep, 60))
    a.ell(cx - r * 0.38, cy - r * 0.5, r * 0.36, r * 0.24, ("#ffffff", 170))
    a.ell(cx - r * 0.62, cy - r * 0.18, r * 0.09, r * 0.09, ("#ffffff", 200))
    # face
    for sx in (-1, 1):
        ex = cx + sx * r * 0.36
        a.ell(ex, cy + r * 0.08, r * 0.17, r * 0.24, "#16233a")
        a.ell(ex - r * 0.05, cy - r * 0.03, r * 0.07, r * 0.08, "#ffffff")
        a.ell(ex + r * 0.06, cy + r * 0.17, r * 0.035, r * 0.035, "#ffffff")
        a.ell(cx + sx * r * 0.63, cy + r * 0.36, r * 0.15, r * 0.08, ("#ff8fb0", 170))
    a.arc((cx - r * 0.16, cy + r * 0.2, cx + r * 0.16, cy + r * 0.46), 20, 160, "#16233a", max(1.2, r * 0.06))
    if hat == "miner":
        hc, hd = "#f3c64a", "#a87a18"

        def h(d, T):
            d.chord((*T(cx - r * 0.86, cy - r * 1.12), *T(cx + r * 0.86, cy - r * 0.02)), 180, 360, fill=255)
            d.rounded_rectangle((*T(cx - r * 1.0, cy - r * 0.62), *T(cx + r * 1.0, cy - r * 0.46)), radius=r * 0.08 * T.s, fill=255)
        a.blob((cx - r * 1.1, cy - r * 1.2, cx + r * 1.1, cy - r * 0.4), h, hc, ol, max(1.2, r * 0.06))
        a.ell(cx - r * 0.2, cy - r * 0.9, r * 0.25, r * 0.08, (hd, 120))
        a.glow(cx, cy - r * 0.78, r * 0.5, r * 0.4, "#fff2a8", 200, r * 0.25)
        a.ell(cx, cy - r * 0.78, r * 0.17, r * 0.17, "#fffbe0", ol, 1.2)
    elif hat == "leaf":
        a.line([(cx, cy - r * 0.95), (cx + r * 0.05, cy - r * 1.3)], "#3f7a2a", max(1.5, r * 0.08))
        for sx in (-1, 1):
            tip = (cx + sx * r * 0.55, cy - r * 1.42)
            base = (cx + r * 0.03, cy - r * 1.28)
            a.poly([base, (cx + sx * r * 0.2, cy - r * 1.6), tip, (cx + sx * r * 0.3, cy - r * 1.22)], "#7ad35a", "#2c5a1e", 1.2)
            a.line([base, tip], ("#3f7a2a", 200), 1)
    if carry == "pick":
        a.line([(cx + r * 1.05, cy + r * 0.55), (cx + r * 1.6, cy - r * 0.35)], "#8a5a2b", max(2, r * 0.13))
        a.poly([(cx + r * 1.15, cy - r * 0.55), (cx + r * 1.62, cy - r * 0.55), (cx + r * 2.0, cy - r * 0.2), (cx + r * 1.62, cy - r * 0.38),
                (cx + r * 1.3, cy - r * 0.35)], "#c9d4e0", ol, 1.2)
    elif carry == "log":
        a.rect((cx - r * 0.9, cy + r * 0.3, cx + r * 0.9, cy + r * 0.72), "#9a6435", r * 0.2, ol, 1.2)
        a.ell(cx + r * 0.9, cy + r * 0.51, r * 0.12, r * 0.21, "#e2b679", ol, 1)


def totem(a, cx, by, h, accent="#45a8ff", top="wings", wood="#8a5a2b", glowing=True):
    """A carved spirit totem pole (3 faces). top: 'wings' / 'picks' (crossed pickaxes) / 'cloud' (weather)."""
    w = h * 0.3
    ol = "#1c1208"
    a.ell(cx, by, w * 0.9, w * 0.28, ("#000000", 80))
    seg = h / 3.2
    y = by
    woodL, woodD = mix(wood, "#ffffff", 0.22), mix(wood, "#000000", 0.3)
    for i in range(3):
        ww = w * (1.0 - i * 0.08)
        y0 = y - seg
        a.rect((cx - ww / 2, y0, cx + ww / 2, y), wood, 3, ol, 1.4)
        a.rect((cx - ww / 2 + 2, y0 + 2, cx - ww / 2 + ww * 0.22, y - 2), (woodL, 160), 2)
        a.rect((cx + ww / 2 - ww * 0.18, y0 + 2, cx + ww / 2 - 2, y - 2), (woodD, 150), 2)
        # face
        ey = y0 + seg * 0.36
        for sx in (-1, 1):
            a.ell(cx + sx * ww * 0.22, ey, ww * 0.13, seg * 0.12, accent if i == 1 else "#f2efe6", ol, 1.2)
            a.ell(cx + sx * ww * 0.22, ey, ww * 0.05, seg * 0.06, "#14100a")
            a.line([(cx + sx * ww * 0.08, ey - seg * 0.2), (cx + sx * ww * 0.36, ey - seg * 0.24)], ol, 1.6)
        if i == 0:
            a.rect((cx - ww * 0.22, y0 + seg * 0.58, cx + ww * 0.22, y0 + seg * 0.8), "#3a2412", 2, ol, 1)
            for k in range(4):
                tx = cx - ww * 0.16 + k * ww * 0.107
                a.rect((tx, y0 + seg * 0.58, tx + ww * 0.06, y0 + seg * 0.66), "#f2efe6", 0)
        elif i == 1:
            a.arc((cx - ww * 0.18, y0 + seg * 0.45, cx + ww * 0.18, y0 + seg * 0.85), 20, 160, ol, 1.8)
            if glowing:
                a.glow(cx, y0 + seg * 0.36, ww * 0.55, seg * 0.25, accent, 150, 6)
        else:
            a.poly([(cx - ww * 0.1, y0 + seg * 0.55), (cx + ww * 0.1, y0 + seg * 0.55), (cx, y0 + seg * 0.82)], "#e0b04a", ol, 1)
        y = y0
    if top == "wings":
        for sx in (-1, 1):
            a.poly([(cx + sx * w * 0.35, y + seg * 0.25), (cx + sx * w * 1.25, y - seg * 0.15), (cx + sx * w * 1.05, y + seg * 0.15),
                    (cx + sx * w * 1.2, y + seg * 0.22), (cx + sx * w * 0.4, y + seg * 0.62)], accent, ol, 1.4)
            a.line([(cx + sx * w * 0.5, y + seg * 0.35), (cx + sx * w * 1.0, y + seg * 0.08)], (mix(accent, "#ffffff", 0.5), 220), 1.4)
        a.poly([(cx - w * 0.3, y + 2), (cx, y - seg * 0.5), (cx + w * 0.3, y + 2)], mix(accent, "#000000", 0.2), ol, 1.4)
    elif top == "picks":   # two crossed pickaxes on top
        for sx in (-1, 1):
            x0_, y0_ = cx - sx * w * 0.75, y + seg * 0.15
            x1_, y1_ = cx + sx * w * 0.55, y - seg * 1.15
            L = math.hypot(x1_ - x0_, y1_ - y0_)
            ux, uy = (x1_ - x0_) / L, (y1_ - y0_) / L
            nx, ny = -uy, ux
            a.line([(x0_, y0_), (x1_, y1_)], "#1c1208", max(4.0, w * 0.2))
            a.line([(x0_, y0_), (x1_, y1_)], "#b07a40", max(2.4, w * 0.12))
            k = w * 0.62

            def q(fu, fn):
                return (x1_ + ux * fu * k + nx * fn * k, y1_ + uy * fu * k + ny * fn * k)
            a.poly([q(-0.35, 1.0), q(0.08, 0.35), q(0.2, 0.0), q(0.08, -0.35), q(-0.35, -1.0), q(-0.02, -0.3), q(-0.08, 0.0), q(-0.02, 0.3)],
                   "#d4dde8", ol, 1.3)
        a.ell(cx, y - seg * 0.12, w * 0.2, w * 0.2, accent, ol, 1.3)
        a.glow(cx, y - seg * 0.12, w * 0.32, w * 0.32, accent, 150, 5)
    elif top == "cloud":
        cy = y - seg * 0.55
        for dx, dy, rr in ((-0.45, 0.05, 0.42), (0.0, -0.18, 0.55), (0.45, 0.05, 0.42)):
            a.ell(cx + dx * w * 1.4, cy + dy * w, rr * w * 1.1, rr * w * 0.9, "#eef4fb", "#6f8299", 1.2)
        a.ell(cx, cy + w * 0.12, w * 0.95, w * 0.28, "#eef4fb")
        for k in range(5):
            dx = (k - 2) * w * 0.32
            a.line([(cx + dx, cy + w * 0.45), (cx + dx - w * 0.08, cy + w * 0.75)], ("#5fb4ff", 220), 1.6)


def tree(a, cx, by, sc=1.0, kind="oak", hit=False):
    """A cute top-down-ish (3/4 view) tree: shadow, trunk with root flares, a round puffy canopy."""
    cols = {"oak": ("#2f7a3a", "#4ea24a", "#86d35e"), "beech": ("#4f8a2e", "#7cb840", "#c3e36a"),
            "maple": ("#a33a22", "#d8642c", "#f4a24a"), "dry": ("#7a6a3a", "#a89a5a", "#d6c886")}[kind]
    ol = "#13200f"
    a.ell(cx + 8 * sc, by + 4 * sc, 70 * sc, 18 * sc, ("#000000", 70))
    tk = "#7a4a26"
    a.poly([(cx - 13 * sc, by - 70 * sc), (cx + 13 * sc, by - 70 * sc), (cx + 16 * sc, by - 6 * sc), (cx + 30 * sc, by + 4 * sc),
            (cx + 8 * sc, by + 2 * sc), (cx, by + 7 * sc), (cx - 9 * sc, by + 2 * sc), (cx - 30 * sc, by + 5 * sc), (cx - 16 * sc, by - 6 * sc)],
           tk, ol, 1.6)
    a.poly([(cx - 10 * sc, by - 68 * sc), (cx - 4 * sc, by - 68 * sc), (cx - 6 * sc, by - 4 * sc), (cx - 13 * sc, by - 4 * sc)], ("#a8703f", 200))
    cy = by - 120 * sc
    blobs = [(-48, 18, 44), (48, 18, 44), (0, 30, 50), (-30, -26, 46), (30, -26, 46), (0, -48, 44), (0, -4, 56)]

    def canopy(d, T):
        for dx, dy, r in blobs:
            d.ellipse((*T(cx + (dx - r) * sc, cy + (dy - r) * sc), *T(cx + (dx + r) * sc, cy + (dy + r) * sc)), fill=255)
    a.blob((cx - 100 * sc, cy - 100 * sc, cx + 100 * sc, cy + 90 * sc), canopy, cols[1], ol, 1.8 * max(0.7, sc))
    for dx, dy, r in ((-40, 34, 30), (40, 34, 30), (0, 46, 30)):
        a.ell(cx + dx * sc, cy + dy * sc, r * sc, r * sc * 0.6, (cols[0], 170))
    for dx, dy, r in ((-34, -34, 26), (10, -56, 22), (-6, -18, 20), (34, -30, 18)):
        a.ell(cx + dx * sc, cy + dy * sc, r * sc, r * sc * 0.75, (cols[2], 170))
    for dx, dy in ((-20, -10), (24, 8), (-50, 10), (52, -2), (0, 22)):
        a.ell(cx + dx * sc, cy + dy * sc, 3 * sc, 3 * sc, (cols[0], 200))
    if kind == "oak":   # a few acorns
        for dx, dy in ((-30, 10), (28, -6), (6, 30)):
            a.ell(cx + dx * sc, cy + dy * sc, 4 * sc, 5 * sc, "#b07a3a", ol, 1)
    if hit:
        for k in range(7):
            ang = math.radians(-160 + k * 23)
            r0, r1 = 110 * sc, 132 * sc
            a.line([(cx + r0 * math.cos(ang), cy + r0 * math.sin(ang) * 0.9), (cx + r1 * math.cos(ang), cy + r1 * math.sin(ang) * 0.9)],
                   ("#ffffff", 230), 3)


def island(a, cx, cy, rx, ry, depth, grass="#5cbf4a", rock="#7a6a58", ores=None, cliff_steps=7):
    """A floating island seen from above at an angle: grass top, dirt band, rock underside with a pointed bottom."""
    ol = "#1a1410"
    pts = []
    n = 40
    for i in range(n + 1):
        t = math.pi * i / n
        x = cx + rx * math.cos(t)
        y = cy + ry * math.sin(t) * 0.95 + ry * 0.12
        pts.append((x, y))
    under = []
    for i in range(cliff_steps + 1):
        t = i / cliff_steps
        x = cx - rx + 2 * rx * t
        prof = math.sin(math.pi * t) ** 1.3
        jag = (8 if i % 2 else -6) * (1 - abs(0.5 - t))
        under.append((x, cy + ry * 0.4 + depth * prof + jag))
    rock_pts = pts[::-1] + under[1:-1]

    def rk(d, T):
        d.polygon([T(x, y) for x, y in pts + under[::-1]], fill=255)
    a.blob((cx - rx - 4, cy - 4, cx + rx + 4, cy + ry + depth + 20), rk, rock, ol, 2)
    # strata
    for k, f in enumerate((0.35, 0.6, 0.82)):
        band = [(cx - rx * (1 - f * 0.55) + 6, cy + ry * 0.6 + depth * f * 0.5), (cx, cy + ry * 0.7 + depth * f),
                (cx + rx * (1 - f * 0.55) - 6, cy + ry * 0.6 + depth * f * 0.5)]
        a.line(band, (mix(rock, "#000000", 0.35), 170), 2)
    a.poly([(cx - rx * 0.3, cy + ry * 0.9), (cx + rx * 0.2, cy + ry * 1.0), (cx, cy + ry * 0.7 + depth * 0.95)], (mix(rock, "#000000", 0.3), 110))
    if ores:
        for i, (fx, fy, col) in enumerate(ores):
            ox, oy = cx + rx * fx, cy + ry * 0.75 + depth * fy
            a.poly([(ox - 7, oy), (ox, oy - 7), (ox + 7, oy), (ox, oy + 7)], col, ol, 1.2)
            a.ell(ox - 2, oy - 2, 2, 2, ("#ffffff", 210))
    # hanging roots
    for k in range(5):
        x = cx - rx * 0.7 + k * rx * 0.35
        yb = cy + ry * 0.95 + (k % 2) * 6
        a.line([(x, yb), (x + 4, yb + 18 + (k % 3) * 8), (x - 2, yb + 30 + (k % 3) * 8)], ("#4a3a20", 200), 2)
    # dirt band + grass top
    a.ell(cx, cy + ry * 0.14, rx, ry, "#8a5a32", ol, 2)

    def top(d, T):
        d.ellipse((*T(cx - rx, cy - ry), *T(cx + rx, cy + ry)), fill=255)
    a.blob((cx - rx - 2, cy - ry - 2, cx + rx + 2, cy + ry + 2), top, grass, ol, 2)
    a.ell(cx - rx * 0.12, cy - ry * 0.18, rx * 0.8, ry * 0.68, (mix(grass, "#ffffff", 0.18), 120))
    a.ell(cx, cy + ry * 0.55, rx * 0.9, ry * 0.4, (mix(grass, "#000000", 0.15), 70))
    for k in range(int(rx / 18)):
        t = (k * 0.6180339) % 1.0
        u = (k * 0.41421) % 1.0
        ang = t * 2 * math.pi
        rr = 0.25 + 0.65 * u
        gx, gy = cx + rx * rr * math.cos(ang), cy + ry * rr * math.sin(ang)
        a.line([(gx - 3, gy), (gx - 1, gy - 6)], (mix(grass, "#000000", 0.35), 200), 1.4)
        a.line([(gx + 1, gy), (gx + 3, gy - 7)], (mix(grass, "#000000", 0.35), 200), 1.4)


def cloud(a, cx, cy, sc=1.0, alpha=200):
    for dx, dy, rx, ry in ((-40, 6, 34, 20), (0, -8, 44, 28), (42, 6, 32, 20), (0, 12, 70, 16)):
        a.ell(cx + dx * sc, cy + dy * sc, rx * sc, ry * sc, ("#ffffff", alpha))


def rock_pile(a, cx, cy, sc=1.0, ore="#e08a4a"):
    ol = "#1a1410"
    for dx, dy, r in ((-14, 2, 14), (12, 4, 12), (0, -8, 16)):
        a.ell(cx + dx * sc, cy + dy * sc, r * sc, r * sc * 0.8, "#8c8f96", ol, 1.4)
        a.ell(cx + dx * sc - 4 * sc, cy + dy * sc - 4 * sc, r * sc * 0.4, r * sc * 0.25, ("#ffffff", 70))
    for dx, dy in ((-6, -10), (10, 2), (-16, 4)):
        a.poly([(cx + (dx - 4) * sc, cy + dy * sc), (cx + dx * sc, cy + (dy - 4) * sc), (cx + (dx + 4) * sc, cy + dy * sc),
                (cx + dx * sc, cy + (dy + 4) * sc)], ore)


def crystal(a, cx, by, sc=1.0, col="#7fd07a"):
    ol = "#10200f"
    for dx, h, w in ((-9, 26, 7), (0, 38, 9), (10, 22, 7)):
        x = cx + dx * sc
        a.poly([(x - w * sc, by), (x - w * sc * 0.8, by - h * sc * 0.75), (x, by - h * sc), (x + w * sc * 0.8, by - h * sc * 0.75),
                (x + w * sc, by)], col, ol, 1.2)
        a.line([(x, by - h * sc), (x - w * sc * 0.3, by - 2)], ("#ffffff", 140), 1.2)
    a.glow(cx, by - 18 * sc, 22 * sc, 22 * sc, col, 110, 8)


def flower(a, x, y, col):
    for k in range(5):
        ang = k * 2 * math.pi / 5
        a.ell(x + 3.2 * math.cos(ang), y + 3.2 * math.sin(ang), 2.6, 2.6, col)
    a.ell(x, y, 2, 2, "#ffe27a")


def mushroom(a, x, y, sc=1.0):
    ol = "#1a1410"
    a.rect((x - 3 * sc, y - 8 * sc, x + 3 * sc, y), "#f2e6d0", 2, ol, 1)
    a.chord((x - 9 * sc, y - 18 * sc, x + 9 * sc, y - 2 * sc), 180, 360, "#e0483e", ol)
    a.ell(x - 3 * sc, y - 12 * sc, 1.6 * sc, 1.6 * sc, "#ffffff")
    a.ell(x + 4 * sc, y - 13 * sc, 1.3 * sc, 1.3 * sc, "#ffffff")


def lamp_post(a, x, by):
    ol = "#1a1410"
    a.ell(x, by, 9, 3, ("#000000", 70))
    a.rect((x - 2, by - 44, x + 2, by), "#3a3a44", 1, ol, 1)
    a.glow(x, by - 50, 18, 18, "#ffd678", 170, 8)
    a.rect((x - 7, by - 58, x + 7, by - 42), "#ffe7a0", 2, ol, 1.2)
    a.poly([(x - 9, by - 58), (x, by - 66), (x + 9, by - 58)], "#3a3a44", ol, 1)


def fence(a, x0, x1, y):
    ol = "#1a1410"
    a.rect((x0, y - 14, x1, y - 10), "#c79a5c", 1, ol, 1)
    a.rect((x0, y - 6, x1, y - 3), "#c79a5c", 1, ol, 1)
    x = x0
    while x <= x1:
        a.rect((x - 2.5, y - 20, x + 2.5, y + 2), "#b0844a", 1, ol, 1)
        x += 18


def pond(a, cx, cy, rx, ry):
    a.ell(cx, cy, rx + 4, ry + 3, "#8a8d94", "#1a1410", 1.4)
    a.ell(cx, cy, rx, ry, "#3f9ad8")
    a.ell(cx - rx * 0.3, cy - ry * 0.3, rx * 0.4, ry * 0.25, ("#ffffff", 90))
    a.ell(cx + rx * 0.4, cy + ry * 0.1, 7, 4, "#5cbf4a", "#1f4a1a", 1)


def bridge(a, x0, y0, x1, y1, ghost=False, width=26):
    """A plank bridge from (x0, y0) to (x1, y1) with rope rails (ghost = dashed outline: not built yet)."""
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = -uy, ux
    n = int(L / 13)
    ol = "#1a1410"
    for i in range(n):
        t0, t1 = i / n, (i + 0.75) / n
        sag = math.sin(math.pi * (t0 + t1) / 2) * 10
        p = [(x0 + (x1 - x0) * t + nx * sgn * width / 2, y0 + (y1 - y0) * t + ny * sgn * width / 2 + sag) for t, sgn in
             ((t0, -1), (t1, -1), (t1, 1), (t0, 1))]
        if ghost:
            a.poly(p, ("#cfe6ff", 40), ("#cfe6ff", 150), 1.2)
        else:
            a.poly(p, "#b98a52" if i % 2 else "#a77a45", ol, 1.1)
    if not ghost:
        for sgn in (-1, 1):
            pts = [(x0 + (x1 - x0) * t + nx * sgn * width / 2, y0 + (y1 - y0) * t + ny * sgn * width / 2 + math.sin(math.pi * t) * 10 - 10)
                   for t in [k / 12 for k in range(13)]]
            a.line(pts, "#5a3a1c", 2)


# ================================================================================================================ small icons (original)
def art_icon(fn, size=64, s=4):
    a = Art(size, size, s)
    fn(a, size)
    return a.done()


def ic_log(a, n):
    ol = "#1a1006"
    a.rect((n * 0.12, n * 0.34, n * 0.74, n * 0.7), "#8a5a2b", n * 0.06, ol, 1.4)
    a.line([(n * 0.18, n * 0.44), (n * 0.66, n * 0.44)], ("#5e3c1c", 220), 1.4)
    a.line([(n * 0.2, n * 0.6), (n * 0.62, n * 0.6)], ("#5e3c1c", 220), 1.4)
    a.ell(n * 0.74, n * 0.52, n * 0.13, n * 0.18, "#e2b679", ol, 1.4)
    a.ell(n * 0.74, n * 0.52, n * 0.06, n * 0.09, None, "#a8743c", 1.2)


def ic_sap(a, n):
    ol = "#2a1806"
    a.poly([(n * 0.5, n * 0.14), (n * 0.72, n * 0.52), (n * 0.66, n * 0.78), (n * 0.5, n * 0.86), (n * 0.34, n * 0.78), (n * 0.28, n * 0.52)],
           "#e8a23a", ol, 1.4)
    a.ell(n * 0.42, n * 0.56, n * 0.06, n * 0.1, ("#fff2c0", 200))


def ic_sapling(a, n):
    ol = "#132010"
    a.ell(n * 0.5, n * 0.82, n * 0.26, n * 0.08, "#6a4a2a", ol, 1.2)
    a.line([(n * 0.5, n * 0.8), (n * 0.5, n * 0.4)], "#3f7a2a", 2.2)
    a.poly([(n * 0.5, n * 0.5), (n * 0.2, n * 0.34), (n * 0.3, n * 0.22), (n * 0.5, n * 0.42)], "#7ad35a", ol, 1.2)
    a.poly([(n * 0.5, n * 0.42), (n * 0.8, n * 0.22), (n * 0.84, n * 0.36), (n * 0.5, n * 0.52)], "#5cbf4a", ol, 1.2)


def ic_apple(a, n):
    ol = "#2a0a0a"
    a.ell(n * 0.5, n * 0.58, n * 0.3, n * 0.27, "#e0483e", ol, 1.6)
    a.ell(n * 0.4, n * 0.5, n * 0.08, n * 0.06, ("#ffffff", 150))
    a.line([(n * 0.5, n * 0.34), (n * 0.54, n * 0.18)], "#5a3a1c", 2)
    a.poly([(n * 0.54, n * 0.24), (n * 0.76, n * 0.16), (n * 0.66, n * 0.3)], "#5cbf4a", ol, 1)


def ic_tree(a, n):
    tree(a, n * 0.5, n * 0.9, n / 170.0)


def ic_trees(a, n):
    tree(a, n * 0.3, n * 0.78, n / 290.0)
    tree(a, n * 0.7, n * 0.92, n / 260.0)


def ic_totem(a, n):
    totem(a, n * 0.5, n * 0.95, n * 0.72, "#45a8ff")


def ic_weather(a, n):
    totem(a, n * 0.5, n * 0.98, n * 0.55, "#5fb4ff", top="cloud", glowing=False)


def ic_island(a, n):
    island(a, n * 0.5, n * 0.42, n * 0.42, n * 0.2, n * 0.3, cliff_steps=5)


def ic_deco(a, n):
    flower(a, n * 0.3, n * 0.6, "#ff8fb0")
    flower(a, n * 0.62, n * 0.72, "#fff0a0")
    mushroom(a, n * 0.7, n * 0.5, n / 40.0)
    lamp_post(a, n * 0.25, n * 0.98) if n >= 60 else None


def g_lock(size, col="#c2d1e2", body="#2a3446"):
    def f(d, s):
        n = size * s
        d.rounded_rectangle((n * 0.2, n * 0.44, n * 0.8, n * 0.94), radius=n * 0.1, fill=rgb(body), outline=rgb(col), width=max(1, int(s * size / 14)))
        d.arc((n * 0.3, n * 0.08, n * 0.7, n * 0.66), 180, 360, fill=rgb(col), width=max(2, int(s * size / 9)))
        d.line([(n * 0.3, n * 0.37), (n * 0.3, n * 0.46)], fill=rgb(col), width=max(2, int(s * size / 9)))
        d.line([(n * 0.7, n * 0.37), (n * 0.7, n * 0.46)], fill=rgb(col), width=max(2, int(s * size / 9)))
        d.ellipse((n * 0.44, n * 0.58, n * 0.56, n * 0.7), fill=rgb(col))
        d.rectangle((n * 0.48, n * 0.66, n * 0.52, n * 0.82), fill=rgb(col))
    return ss_glyph(size, size, f)


def g_star(size, col):
    def f(d, s):
        n = size * s
        pts = []
        for k in range(10):
            ang = -math.pi / 2 + k * math.pi / 5
            r = n * (0.48 if k % 2 == 0 else 0.2)
            pts.append((n / 2 + r * math.cos(ang), n / 2 + r * math.sin(ang)))
        d.polygon(pts, fill=rgb(col), outline=rgb("#3a2a08"))
    return ss_glyph(size, size, f)


def g_back(size, col):
    def f(d, s):
        n = size * s
        d.line([(n * 0.62, n * 0.18), (n * 0.3, n * 0.5), (n * 0.62, n * 0.82)], fill=rgb(col), width=int(s * 2.4))
    return ss_glyph(size, size, f)


def g_cursor(size):
    def f(d, s):
        n = size * s
        pts = [(n * 0.1, n * 0.05), (n * 0.1, n * 0.8), (n * 0.3, n * 0.62), (n * 0.45, n * 0.95), (n * 0.58, n * 0.89), (n * 0.44, n * 0.57),
               (n * 0.72, n * 0.57)]
        d.polygon(pts, fill=rgb("#ffffff"), outline=rgb("#0a0f18"), width=int(s * 1.5))
    return ss_glyph(size, size, f)


def footer(im, hints):
    hy2 = 1044
    fh = font("body", 15)
    total = sum(max(22, tw(k, font("headb", 14)) + 10) + 6 + tw(v, fh) + 26 for k, v in hints)
    x = (1920 - total) // 2
    for k, v in hints:
        w = key_cap(im, x, hy2 - 11, k)
        text(im, (x + w + 6, hy2), v, fh, "#aebfd3", "lm")
        x += w + 6 + tw(v, fh) + 26


# ================================================================================================================ skill page
SKILL4 = [("Combat", I_WARP % "Combat"), ("Mining", I_WARP % "Mining"), ("Farming", I_WARP % "Farming"), ("Foraging", I_WARP % "Foraging")]

PLAYER = {
    "hi": dict(lv=31, xp=(18420, 25000), skills={"Combat": 27, "Mining": 31, "Farming": 24, "Foraging": 27},
               metal="#b8c4d0", set_name="Iron Mining set", set_n="4 / 4",
               armor=[("head", "Rare"), ("chest", "Rare"), ("hands", "Unique"), ("legs", "Normal")],
               tool=("Copper Pickaxe", "T1 Copper", "Lv 14", 0.58),
               charms=[(I_ACC % "stonehide-rare", "Rare"), (I_ACC % "lantern-unique", "Unique"), ("px:furnace", None), (I_ACC % "speed-normal", "Normal")],
               stats=[("MINING", [("Mining Speed", "+48%", "g"), ("Mining Fortune", "+61", "g"), ("Mining Wisdom", "+6% XP", "g"),
                                  ("Breaking Power", "T1 Copper", "tier"), ("Vein Burst", "3 ores", "g"), ("Gem chance", "+0.12%", "g"),
                                  ("Light radius", "+2", "g")]),
                      ("SURVIVAL", [("Health", "245", "g"), ("Defense", "+41", "g"), ("Mana", "30", "g"), ("Stamina", "100", "g"),
                                    ("Walk Speed", "-2%", "r")]),
                      ("COMBAT", [("Damage", "+14", "g"), ("Crit Chance", "5%", "g"), ("Attack Speed", "+0%", "n")])],
               fort=[("Tool", 10, "#e08a4a"), ("Gear", 40.5, "#8fc8ff"), ("Charms", 6, "#ff8fe0"), ("Pets", 4.5, "#7cf0ad")],
               ranks={(0, 0, "r1a"): 5, (0, 0, "r1b"): 3, (0, 1, "r2a"): 3, (0, 1, "r2b"): 1, (0, 2, "r3a"): 2, (0, 3, "r4a"): 1,
                      (1, 0, "r1a"): 3, (1, 0, "r1b"): 1, (1, 1, "r2a"): 1, (2, 0, "r1a"): 2, (2, 0, "r1b"): 1, (2, 2, "r3a"): 1},
               sel=(0, 3, "r4a"),
               colls=[("Copper Ore VI", 2140, 2500, "Next: Enchanted Copper"), ("Iron Ore II", 365, 500, "Next: Iron recipes"),
                      ("Thorium Ore I", 37, 50, "Next: Thorium recipes")]),
    "lo": dict(lv=6, xp=(410, 900), skills={"Combat": 4, "Mining": 6, "Farming": 3, "Foraging": 5},
               metal="#e08a4a", set_name="Copper Mining set", set_n="2 / 4",
               armor=[("head", "Normal"), ("chest", "Normal"), (None, None), (None, None)],
               tool=("Copper Pickaxe", "T1 Copper", "Lv 3", 0.3),
               charms=[(I_ACC % "speed-normal", "Normal"), (None, None), (None, None), (None, None)],
               stats=[("MINING", [("Mining Speed", "+12%", "g"), ("Mining Fortune", "+9", "g"), ("Mining Wisdom", "+0% XP", "n"),
                                  ("Breaking Power", "T1 Copper", "tier"), ("Vein Burst", "-", "n"), ("Gem chance", "0%", "n"),
                                  ("Light radius", "+0", "n")]),
                      ("SURVIVAL", [("Health", "110", "g"), ("Defense", "+11", "g"), ("Mana", "20", "g"), ("Stamina", "100", "g"),
                                    ("Walk Speed", "+0%", "n")]),
                      ("COMBAT", [("Damage", "+3", "g"), ("Crit Chance", "5%", "g"), ("Attack Speed", "+0%", "n")])],
               fort=[("Tool", 4, "#e08a4a"), ("Gear", 4, "#8fc8ff"), ("Charms", 1, "#ff8fe0"), ("Pets", 0, "#7cf0ad")],
               ranks={(0, 0, "r1a"): 3, (0, 0, "r1b"): 1, (1, 0, "r1a"): 1},
               sel=(0, 1, "r2a"),
               colls=[("Copper Ore II", 82, 100, "Next: Copper Pocket Shard")]),
}

PATH = [("Copper", "T1 Copper", 1, "copper"), ("Iron", "T2 Iron", 8, "iron"), ("Thorium", "T4 Thorium", 20, "thorium"),
        ("Cobalt", "T7 Cobalt", 40, "cobalt"), ("Adamantite", "T10 Adamantite", 60, "adamantite"), ("Mithril", "T13 Mithril", 80, "mithril"),
        ("Onyxium", "T16 Onyxium", 100, "onyxium")]


def stats_column(im, P, x0, y0, x1, y1):
    panel(im, (x0, y0, x1, y1), "Your stats")
    toggle(im, x0 + 14, y0 + 40, True, "With your Mining set on", w=40, h=22)
    y = y0 + 84
    fN, fV = font("body", 15), font("bold", 15)
    for head, rows in P["stats"]:
        text(im, (x0 + 14, y), head, font("head", 13), PAL["dim"], "lm", track=1.5)
        taper_line(im, x0 + 14 + tw(head, font("head", 13), 1.5) + 8, x1 - 14, y, PAL["gold"], 120, 0.7)
        y += 24
        for nm, v, kind in rows:
            row(im, (x0 + 10, y - 11, x1 - 10, y + 11), "normal")
            text(im, (x0 + 20, y), nm, fN, PAL["row"], "lm")
            col = {"g": PAL["green"], "r": PAL["red"], "n": PAL["dim"], "tier": TIER["Copper"]}[kind]
            text(im, (x1 - 20, y), v, fV, col, "rm")
            y += 25
        y += 10
    # four power sources for Mining Fortune
    y += 4
    text(im, (x0 + 14, y), "MINING FORTUNE COMES FROM", font("head", 13), PAL["dim"], "lm", track=1.2)
    y += 20
    tot = sum(v for _n, v, _c in P["fort"]) or 1
    bx0, bx1 = x0 + 14, x1 - 14
    panel(im, (bx0, y, bx1, y + 14), inset=True, c=2)
    x = bx0 + 1
    for nm, v, c in P["fort"]:
        w = int(round((bx1 - bx0 - 2) * v / tot))
        if w > 1:
            grad_fill(im, (x, y + 1, min(bx1 - 1, x + w - 1), y + 13), mix(c, "#ffffff", 0.2), mix(c, "#000000", 0.25), c=1)
        x += w
    y += 30
    for nm, v, c in P["fort"]:
        put(im, g_diamond(10, c), x0 + 16, y - 5)
        text(im, (x0 + 32, y), nm, font("body", 15), PAL["row"], "lm")
        vs = ("+%g" % v) if v else "0"
        text(im, (x1 - 20, y), vs, font("bold", 15), PAL["green"] if v else PAL["dim"], "rm")
        y += 23
    text(im, (x0 + 14, y + 8), "Tool + gear + charms + pets stack.", font("body", 14), PAL["dim"], "lm")
    text(im, (x0 + 14, y + 30), "Hover a stat: every source", font("bodyb", 14), PAL["action"], "lm")


def skills_grid(im, P, x0, y0, x1):
    y1 = y0 + 284
    panel(im, (x0, y0, x1, y1), "Skills")
    cw = (x1 - x0 - 28 - 8) // 2
    ch = 104
    for i, (nm, ic) in enumerate(SKILL4):
        cx = x0 + 14 + (i % 2) * (cw + 8)
        cy = y0 + 38 + (i // 2) * (ch + 8)
        box = (cx, cy, cx + cw - 1, cy + ch - 1)
        sel = nm == "Mining"
        if sel:
            glow(im, box, A["base"], 4, 150, 4, 2)
            grad_fill(im, box, mix(A["base"], "#111b2d", 0.6), mix(A["base"], "#111b2d", 0.82), c=4)
            outline(im, box, A["base"], c=4)
        else:
            grad_fill(im, box, "#18253c", "#121c2f", c=4)
            outline(im, box, "#2b3d5b", c=4)
        paste_icon(im, ic, cx + cw // 2 - 20, cy + 8, 40, 1.0 if sel else 0.85)
        text(im, (cx + cw // 2, cy + 60), nm, font("headb", 16), "#ffffff" if sel else PAL["row"], "mm")
        lv = P["skills"][nm]
        text(im, (cx + cw // 2, cy + 79), "Lv %d" % lv, font("headb", 14), PAL["xp"], "mm")
        bar(im, (cx + 12, cy + 90, cx + cw - 13, cy + 96), (lv * 37 % 100) / 100.0, "xp")
    text(im, (x0 + (x1 - x0) // 2, y1 - 9), "More skills get their page later", font("body", 14), PAL["dim"], "ms")
    return y1


def shard_picture(w, h, locked=False):
    a = Art(w, h, 3)
    # sky disc background
    for k in range(18):
        t = k / 17.0
        a.ell(w / 2, h * 0.5, w * 0.62 * (1 - t * 0.55), h * 0.62 * (1 - t * 0.55), (mix("#2a5fa0", "#9fd4ff", t), 255))
    cloud(a, w * 0.18, h * 0.2, 0.55, 150)
    cloud(a, w * 0.86, h * 0.34, 0.45, 120)
    # rocky mining island behind him
    island(a, w * 0.58, h * 0.42, w * 0.34, h * 0.09, h * 0.28, grass="#9aa3ab", rock="#6f6a66",
           ores=[(-0.5, 0.15, TIER["Copper"]), (0.2, 0.32, TIER["Iron"]), (-0.1, 0.55, TIER["Thorium"]), (0.55, 0.12, TIER["Cobalt"])],
           cliff_steps=6)
    # mine entrance in the cliff (timber frame)
    mx, my = w * 0.62, h * 0.58
    a.rect((mx - 15, my - 18, mx + 15, my + 12), "#14100c", 6, "#1a1410", 1.2)
    a.rect((mx - 19, my - 22, mx - 13, my + 13), "#9a6a3a", 1, "#1a1410", 1)
    a.rect((mx + 13, my - 22, mx + 19, my + 13), "#9a6a3a", 1, "#1a1410", 1)
    a.rect((mx - 22, my - 26, mx + 22, my - 19), "#b07a40", 1, "#1a1410", 1)
    a.glow(mx, my, 10, 8, "#ffb04a", 120, 5)
    for gx, gy in ((0.36, 0.4), (0.7, 0.44), (0.62, 0.37)):
        a.ell(w * gx, h * gy, 7, 3, ("#5fa04a", 220))
    rock_pile(a, w * 0.43, h * 0.42, 0.8, TIER["Copper"])
    crystal(a, w * 0.52, h * 0.44, 0.75, TIER["Thorium"])
    totem(a, w * 0.76, h * 0.45, h * 0.3, "#45a8ff", top="picks")
    # the spirit in front
    spirit(a, w * 0.34, h * 0.68, h * 0.14, body="#a8ecff", deep="#3a8ed8", hat="miner", carry="pick")
    for k, (fx, fy) in enumerate(((0.12, 0.48), (0.88, 0.7), (0.62, 0.86), (0.2, 0.86))):
        a.ell(w * fx, h * fy, 2.2, 2.2, ("#ffffff", 210))
        a.glow(w * fx, h * fy, 5, 5, "#bfe8ff", 160, 4)
    img = a.done()
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=10, fill=255)
    img.putalpha(Image.composite(img.getchannel("A"), Image.new("L", (w, h), 0), m))
    if locked:
        img = grey_img(img, 0.45)
    return img


def shard_card(im, P, x0, y0, x1, y1, locked):
    panel(im, (x0, y0, x1, y1), "Mining shard")
    if not locked:
        text(im, (x1 - 14, y0 + 18), "Open", font("head", 15), A["hi"], "rm")
        put(im, g_chev(14, A["hi"]), x1 - 12, y0 + 11)
    px0, py0 = x0 + 12, y0 + 38
    pw, ph = x1 - x0 - 24, 330
    pic = shard_picture(pw, ph, locked)
    im.paste(pic, (px0, py0), pic)
    outline(im, (px0, py0, px0 + pw - 1, py0 + ph - 1), "#ffffff" if not locked else "#3a4658", c=8, alpha=60 if not locked else 255)
    if not locked:
        glow(im, (px0, py0, px0 + pw - 1, py0 + ph - 1), A["base"], 6, 120, 8, 2)
        put(im, K.g_tri(16, "#ffffff"), px0 + pw - 30, py0 + ph - 30)
    else:
        lk = g_lock(64, "#d6e4ee", "#1a2232")
        put(im, lk, px0 + pw // 2 - 32, py0 + ph // 2 - 52)
        text(im, (px0 + pw // 2, py0 + ph // 2 + 34), "LOCKED", font("headb", 22), "#d6e4ee", "mm", track=2)
    y = py0 + ph + 26
    fk, fv = font("body", 15), font("bodyb", 15)
    if not locked:
        rich(im, x0 + 14, y, [("Mining Shard", font("headb", 18), "#ffffff"), ("  -  ", fk, PAL["dim"]), ("open", font("headb", 18), PAL["green"])])
        y += 32
        for k, v, c in (("Spirits", "2  (Totem Lv 3)", PAL["row"]), ("Stored", "1,284 items (no limit)", PAL["row"]),
                        ("Rate", "42 Iron Ore / h", PAL["green"]), ("Offline", "35% for 12 h", PAL["row"]),
                        ("Clicks", "25% of world XP", PAL["xp"])):
            text(im, (x0 + 14, y), k, fk, PAL["dim"], "lm")
            text(im, (x0 + 84, y), v, fv, c, "lm")
            y += 24
        button(im, (x0 + 14, y1 - 58, x1 - 14, y1 - 22), "Open shard", "primary", fsize=17)
        text(im, (x0 + (x1 - x0) // 2, y1 - 8), "or click the picture", font("body", 13), PAL["dim"], "ms")
    else:
        rich(im, x0 + 14, y, [("Mining Shard", font("headb", 18), "#8a97a8"), ("  -  ", fk, PAL["dim"]), ("locked", font("headb", 18), PAL["red"])])
        y += 34
        text(im, (x0 + 14, y), "Unlocks at Mining Lv 10", font("headb", 17), PAL["xp"], "lm")
        y += 30
        bar(im, (x0 + 14, y, x1 - 14, y + 12), P["lv"] / 10.0, "xp")
        text(im, (x0 + 14, y + 28), "You: Mining Lv %d" % P["lv"], fv, PAL["row"], "lm")
        text(im, (x1 - 14, y + 28), "%d / 10" % P["lv"], font("headb", 15), PAL["xp"], "rm")
        y += 58
        for s_ in ("Then: your own island with a", "mining spirit who digs for you", "while you play or are offline."):
            text(im, (x0 + 14, y), s_, fk, PAL["dim"], "lm")
            y += 22
        button(im, (x0 + 14, y1 - 58, x1 - 14, y1 - 22), "Locked - Mining Lv 10", "primary", "disabled", fsize=16)


def top_panel(im, P, x0, y0, x1, y1):
    panel(im, (x0, y0, x1, y1))
    # head
    fx, fy = x0 + 14, y0 + 12
    box = (fx, fy, fx + 59, fy + 59)
    glow(im, box, A["base"], 4, 140, 6, 2)
    grad_fill(im, box, mix(A["base"], "#111b2d", 0.6), mix(A["base"], "#111b2d", 0.85), c=6)
    outline(im, box, A["base"], c=6)
    paste_icon(im, I_WARP % "Mining", fx + 6, fy + 6, 48)
    text(im, (fx + 76, fy + 18), "MINING", font("headb", 28), PAL["title"], "lm", track=2)
    text(im, (fx + 76, fy + 46), "Gear, collections, tree and shard in one page", font("body", 14), PAL["dim"], "lm")
    # level badge
    bx = x0 + 440
    grad_fill(im, (bx, fy + 2, bx + 70, fy + 58), "#2b2212", "#1a140a", c=8)
    outline(im, (bx, fy + 2, bx + 70, fy + 58), PAL["edge"], c=8)
    outline(im, (bx + 1, fy + 3, bx + 69, fy + 57), PAL["gold"], c=7)
    text(im, (bx + 35, fy + 15), "LEVEL", font("head", 11), PAL["goldHi"], "mm", track=1.5)
    text(im, (bx + 35, fy + 38), str(P["lv"]), font("headb", 28), "#ffe7a8", "mm")
    # xp bar + next unlock
    xb0, xb1 = bx + 90, x1 - 14
    xp, need = P["xp"]
    bar(im, (xb0, fy + 20, xb1, fy + 32), xp / float(need), "xp", "Lv %d  ->  %d" % (P["lv"], P["lv"] + 1),
        "%s / %s XP" % (format(xp, ","), format(need, ",")))
    if P["lv"] >= 10:
        parts = [("NEXT UNLOCK  ", font("head", 14), PAL["xp"]), ("Lv 32:", font("bodyb", 15), PAL["row"]),
                 (" +1 tree point", font("bodyb", 15), PAL["green"]), ("      Lv 40:", font("bodyb", 15), PAL["row"]),
                 (" Cobalt ore + the Cobalt collection", font("bodyb", 15), TIER["Cobalt"])]
    else:
        parts = [("NEXT UNLOCK  ", font("head", 14), PAL["xp"]), ("Lv 8:", font("bodyb", 15), PAL["row"]),
                 (" Iron ore + the Iron collection", font("bodyb", 15), TIER["Iron"]), ("      Lv 10:", font("bodyb", 15), PAL["row"]),
                 (" your Mining Shard", font("bodyb", 15), PAL["green"])]
    rich(im, xb0, fy + 50, parts)
    taper_line(im, x0 + 14, x1 - 14, y0 + 84, PAL["gold"], 140, 0.85)
    # ---- gear row
    gy = y0 + 104
    fh = font("head", 13)
    # tool
    tx = x0 + 14
    text(im, (tx, gy), "TOOL", fh, PAL["dim"], "lm", track=1.5)
    slot(im, tx, gy + 16, "empty", None, None, size=64)
    put_px(im, px_icon("pickaxe"), tx + 8, gy + 24, 48)
    nm, tier, lvs, frac = P["tool"]
    text(im, (tx + 76, gy + 28), nm, font("headb", 16), "#ffffff", "lm")
    rich(im, tx + 76, gy + 48, [(tier, font("bodyb", 14), TIER["Copper"]), ("  " + lvs, font("bodyb", 14), PAL["xp"])])
    bar(im, (tx + 76, gy + 62, tx + 210, gy + 68), frac, "xp")
    text(im, (tx + 76, gy + 80), "Lifelong", font("body", 13), PAL["dim"], "lm")
    text(im, (tx, gy + 104), "Upgrade tab", font("head", 14), A["hi"], "lm")
    put(im, g_chev(13, A["hi"]), tx + tw("Upgrade tab", font("head", 14)) + 2, gy + 97)
    d = ImageDraw.Draw(im, "RGBA")
    d.line([(x0 + 240, gy - 8), (x0 + 240, gy + 112)], fill=rgb(PAL["line"]))
    # armor
    ax = x0 + 256
    rich(im, ax, gy, [("ARMOR", fh, PAL["dim"]), ("   %s %s" % (P["set_name"], P["set_n"]), font("bodyb", 13), RAR["Set"])])
    for i, (piece, rr) in enumerate(P["armor"]):
        sx = ax + i * 70
        if piece:
            slot(im, sx, gy + 16, "empty", RAR[rr], None, size=64)
            put_px(im, px_armor(piece, P["metal"], mix(P["metal"], "#000000", 0.4)), sx + 8, gy + 24, 48)
        else:
            slot(im, sx, gy + 16, "empty", None, None, size=64)
            text(im, (sx + 32, gy + 48), ["Head", "Chest", "Hands", "Legs"][i], font("body", 13), PAL["placeholder"], "mm", shadow=False)
    rx = ax + 4 * 70 + 6
    button(im, (rx, gy + 18, rx + 112, gy + 50), "Requip", "secondary", fsize=15, glyph=g_pencil(14, "#c2d1e2"))
    text(im, (rx + 56, gy + 66), "Mining preset", font("body", 13), PAL["dim"], "mm")
    if P["lv"] >= 10:
        rich(im, ax, gy + 104, [("Set bonus  ", font("body", 14), PAL["dim"]), ("+22.5", font("bold", 14), PAL["green"]),
                                (" Fortune  ", font("body", 14), PAL["row"]), ("+10%", font("bold", 14), PAL["green"]), (" Speed", font("body", 14), PAL["row"])])
    else:
        rich(im, ax, gy + 104, [("Set bonus  ", font("body", 14), PAL["dim"]), ("needs 4 / 4 pieces", font("bodyb", 14), PAL["red"])])
    d.line([(x0 + 660, gy - 8), (x0 + 660, gy + 112)], fill=rgb(PAL["line"]))
    # charms
    cx0 = x0 + 676
    text(im, (cx0, gy), "CHARMS", fh, PAL["dim"], "lm", track=1.5)
    text(im, (x1 - 30, gy), "Charms page", font("head", 14), A["hi"], "rm")
    put(im, g_chev(13, A["hi"]), x1 - 28, gy - 7)
    for i, (ic, rr) in enumerate(P["charms"]):
        sx = cx0 + i * 70
        st = "selected" if (i == 1 and P["lv"] >= 10) or (i == 0 and P["lv"] < 10) else "empty"
        if ic is None:
            slot(im, sx, gy + 16, "empty", None, None, size=64)
            put(im, g_plus(18, "#3a4e6e"), sx + 23, gy + 39)
        elif ic.startswith("px:"):
            slot(im, sx, gy + 16, st, None, ic, size=64)
        else:
            slot(im, sx, gy + 16, st, RAR[rr], ic, size=64)
    ux = cx0 + 4 * 70 + 6
    if P["lv"] >= 10:
        cname, frm, to = "Lantern", "Unique", "Rare"
        cost = [("Lantern -> Rare:  ", font("body", 14), PAL["dim"]), ("2,500 coins", font("bodyb", 14), PAL["green"]),
                ("  64 Tree Sap", font("bodyb", 14), PAL["green"])]
    else:
        cname, frm, to = "Speed", "Normal", "Unique"
        cost = [("Speed -> Unique:  ", font("body", 14), PAL["dim"]), ("500 coins", font("bodyb", 14), PAL["green"]),
                ("  32 Feathers", font("bodyb", 14), PAL["red"])]
    text(im, (ux, gy + 26), cname, font("headb", 16), RAR[frm], "lm")
    rich(im, ux, gy + 46, [(frm, font("bodyb", 13), RAR[frm]), ("  ->  ", font("body", 13), PAL["dim"]), (to, font("bodyb", 13), RAR[to])])
    button(im, (ux, gy + 58, x1 - 14, gy + 84), "Upgrade", "primary" if P["lv"] >= 10 else "primary", "normal" if P["lv"] >= 10 else "disabled",
           fsize=15)
    rich(im, cx0, gy + 104, cost)


def collections_panel(im, P, x0, y0, x1, y1):
    panel(im, (x0, y0, x1, y1), "Collections - ore path", link="Collections page")
    text(im, (x0 + 290, y0 + 18), "Tiers open with your Mining LEVEL;  recipes + rewards with the COLLECTION",
         font("body", 14), PAL["dim"], "lm")
    n = len(PATH)
    step = (x1 - x0 - 28) / float(n)
    lv = P["lv"]
    ny = y0 + 88
    centers = [int(x0 + 14 + step * (i + 0.5)) for i in range(n)]
    d = ImageDraw.Draw(im, "RGBA")
    nxt = next((i for i, p in enumerate(PATH) if p[2] > lv), None)
    for i in range(n - 1):
        a_, b_ = centers[i] + 34, centers[i + 1] - 34
        lit = PATH[i + 1][2] <= lv
        if lit:
            d.line([(a_, ny), (b_, ny)], fill=rgb(GOLD), width=3)
        else:
            xx = a_
            while xx < b_:
                d.line([(xx, ny), (min(b_, xx + 6), ny)], fill=rgb("#3a4658"), width=2)
                xx += 11
    for i, (nm, tag, need, key) in enumerate(PATH):
        cx = centers[i]
        open_ = need <= lv
        coll = P["colls"][i] if i < len(P["colls"]) else None
        cur = open_ and (i == len(P["colls"]) - 1)
        text(im, (cx, y0 + 46), tag, font("bodyb", 14), TIER[nm] if open_ else "#6b7788", "mm")
        if open_:
            slot(im, cx - 30, ny - 30, "selected" if cur else "empty", TIER[nm], I_ENCH % ("%s-ingot" % key), size=60)
        else:
            slot(im, cx - 30, ny - 30, "empty", None, I_ENCH % ("%s-ingot" % key), size=60, dim=True)
            put(im, g_lock(22, "#c2d1e2"), cx + 10, ny + 8)
        ly = ny + 46
        if open_:
            put(im, g_check(13, PAL["green"]), cx - tw("Mining %d" % need, font("bodyb", 14)) // 2 - 12, ly - 7)
            text(im, (cx + 6, ly), "Mining %d" % need, font("bodyb", 14), PAL["green"], "mm")
        elif i == nxt:
            text(im, (cx, ly), "Mining %d / %d" % (lv, need), font("headb", 14), PAL["xp"], "mm")
        else:
            text(im, (cx, ly), "Mining %d" % need, font("bodyb", 14), "#6b7788", "mm")
        if coll:
            cn, have, want, nx = coll
            text(im, (cx, ly + 20), cn, font("bodyb", 14), PAL["row"], "mm")
            bar(im, (cx - 62, ly + 32, cx + 62, ly + 42), have / float(want), "green")
            text(im, (cx, ly + 56), "%s / %s" % (format(have, ","), format(want, ",")), font("headb", 13), PAL["xp"], "mm")
            text(im, (cx, ly + 74), nx, font("body", 13), "#aebfd3", "mm")
        else:
            text(im, (cx, ly + 20), "%s Ore" % nm, font("body", 14), "#5d6a7c", "mm")
            bar(im, (cx - 62, ly + 32, cx + 62, ly + 42), 0, "green")
            if i == nxt:
                text(im, (cx, ly + 56), "NEXT TIER", font("headb", 13), PAL["xp"], "mm", track=1)
                text(im, (cx, ly + 74), "opens at Mining %d" % need, font("body", 13), "#aebfd3", "mm")
            else:
                text(im, (cx, ly + 56), "locked", font("body", 13), "#5d6a7c", "mm")


def node_pic(size, state, k=0, m=1, cap=False, diamond=False):
    """state: locked / ready / learnt / max. Pips (k of m) along the bottom of the ring."""
    ring = {"locked": "#4a535c", "ready": GOLD, "learnt": TREE_COL, "max": TREE_COL}[state]

    def f(d, s):
        n = size * s
        if diamond:
            c = n / 2
            d.polygon([(c, 1), (n - 1, c), (c, n - 1), (1, c)], fill=rgb("#101822"), outline=rgb(ring))
            d.polygon([(c, 3 * s), (n - 3 * s, c), (c, n - 3 * s), (3 * s, c)], outline=rgb(ring))
            d.polygon([(c, 4 * s), (n - 4 * s, c), (c, n - 4 * s), (4 * s, c)], outline=rgb(ring))
            return
        d.ellipse((0, 0, n - 1, n - 1), fill=rgb("#0a0f16"))
        d.ellipse((s, s, n - 1 - s, n - 1 - s), fill=rgb("#101822"), outline=rgb(ring), width=int(3 * s))
        if state != "locked" and m > 0:
            r = n / 2 - 2.2 * s
            pr = max(2.2, size / 16.0) * s
            span = min(math.radians(110), math.radians(24) * (m - 1))
            for i in range(m):
                ang = math.pi / 2 + (span / 2 - (span * i / (m - 1) if m > 1 else 0))
                px, py = n / 2 + r * math.cos(ang), n / 2 + r * math.sin(ang)
                d.ellipse((px - pr, py - pr, px + pr, py + pr), fill=rgb("#ffd36b" if i < k else "#2a323a"), outline=rgb("#0a0f16"))
    pic = ss_glyph(size, size, f)
    if state == "max":
        g = Image.new("RGBA", (size + 24, size + 24), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse((8, 8, size + 15, size + 15), outline=rgb(TREE_COL, 170), width=4)
        g = g.filter(ImageFilter.GaussianBlur(4))
        g.alpha_composite(pic, (12, 12))
        return g, 12
    return pic, 0


def tree_panel(im, P, x0, y0, x1, y1):
    panel(im, (x0, y0, x1, y1), "Skill tree")
    spent = sum(P["ranks"].values())
    free = P["lv"] - spent
    rich(im, x0 + 160, y0 + 18, [("Points  ", font("body", 15), PAL["dim"]), ("%d free" % free, font("headb", 16), PAL["xp"]),
                                 ("   %d spent  (1 per Mining level)" % spent, font("body", 15), PAL["dim"])])
    # legend
    lx = x1 - 470
    for st, lab in (("learnt", "learnt"), ("ready", "ready"), ("locked", "locked")):
        pic, off = node_pic(18, st, 1 if st == "learnt" else 0, 1)
        im.paste(pic, (lx - off, y0 + 9 - off), pic)
        if st == "locked":
            put(im, g_lock(11), lx + 9, y0 + 17)
        text(im, (lx + 24, y0 + 18), lab, font("body", 14), PAL["text"], "lm")
        lx += 32 + tw(lab, font("body", 14)) + 14
    hp = ss_glyph(20, 20, lambda d, s: d.ellipse((s, s, 19 * s, 19 * s), outline=rgb("#4fe3ff"), width=int(2.5 * s)))
    put(im, hp, lx, y0 + 8)
    text(im, (lx + 26, y0 + 18), "selected", font("body", 14), PAL["text"], "lm")
    lx += 40 + tw("selected", font("body", 14)) + 10
    text(im, (lx, y0 + 18), "no zoom, no scroll", font("body", 14), PAL["dim"], "lm")
    # ---- layout: fan, emblem at bottom centre, branches at -62 / 0 / +62 degrees
    CX0, CY0, CX1, CY1 = x0 + 10, y0 + 36, x1 - 10, y1 - 8
    cx, cy = (CX0 + CX1) / 2.0, CY1 - 50
    node = 44
    axm, aym = (CX1 - cx) - node / 2 - 14, cy - CY0 - node / 2 - 22
    ring0, s_ = 0.30, node + 14
    angs = [math.radians(-62), 0.0, math.radians(62)]
    nodes, edges, juncs = [], [], {}
    gates = [r["gate"] for r in MINING_TREE["branches"][0]["rows"]]
    for bi, b in enumerate(MINING_TREE["branches"]):
        bc = angs[bi]
        prev = "emb"
        for ri, rowd in enumerate(b["rows"]):
            f = ring0 + (1 - ring0) * ri / 5.0
            ax, ay = axm * f, aym * f
            its = skyymap.items_of(rowd)
            da = s_ / math.hypot(ax * math.cos(bc), ay * math.sin(bc))
            jid = (bi, ri, "J")
            juncs[jid] = (cx + ax * math.sin(bc), cy - ay * math.cos(bc))
            edges.append((prev, jid, "spine", ri))
            for j, (kind, uid) in enumerate(its):
                a_ = bc + (j - (len(its) - 1) / 2.0) * da
                size = node if kind == "up" else int(node * 0.7)
                if rowd.get("cap"):
                    size = 54
                nid = (bi, ri, uid)
                nodes.append(dict(id=nid, kind=kind, a=a_, ax=ax, ay=ay, size=size, x=cx + ax * math.sin(a_), y=cy - ay * math.cos(a_),
                                  cap=bool(rowd.get("cap")), m=(rowd["ups"][[u["id"] for u in rowd["ups"]].index(uid)]["max"] if kind == "up" else 1),
                                  name=(rowd["ups"][[u["id"] for u in rowd["ups"]].index(uid)]["name"] if kind == "up" else rowd["free"]["name"])))
                if kind == "up":
                    edges.append((jid, nid, "spoke", ri))
            prev = jid
    skyymap.relax(nodes, cx, cy)
    byid = dict((n["id"], n) for n in nodes)
    for bi in range(3):   # junctions that sit on a node (free diamond / centred single node)
        for ri in range(6):
            jx, jy = juncs[(bi, ri, "J")]
            for n in nodes:
                if n["id"][:2] == (bi, ri) and (n["kind"] == "free" or math.hypot(n["x"] - jx, n["y"] - jy) < 3):
                    juncs[(bi, ri, "J")] = (n["x"], n["y"], n["size"] / 2.0 + 2)
    spent_ok = lambda ri: spent >= gates[ri]  # noqa: E731

    def endp(e):
        if e == "emb":
            return cx, cy, 46
        if e[2] == "J":
            j = juncs[e]
            return (j[0], j[1], j[2]) if len(j) == 3 else (j[0], j[1], 6)
        n = byid[e]
        return n["x"], n["y"], n["size"] / 2.0 + 2
    d = ImageDraw.Draw(im, "RGBA")
    for lit_pass in (False, True):
        for a_e, b_e, kind, ri in edges:
            if kind == "spine":
                lit = spent_ok(ri)
            else:
                lit = P["ranks"].get(b_e, 0) > 0
            if lit != lit_pass:
                continue
            (ax_, ay_, ra), (bx_, by_, rb) = endp(a_e), endp(b_e)
            L = math.hypot(bx_ - ax_, by_ - ay_)
            if L < ra + rb + 4:
                continue
            ux, uy = (bx_ - ax_) / L, (by_ - ay_) / L
            t = ra + 3
            col = rgb(GOLD) if lit else rgb("#3a4658")
            while t <= L - rb - 3:
                px_, py_ = ax_ + ux * t, ay_ + uy * t
                rr = 2.0 if lit else 1.6
                d.ellipse((px_ - rr, py_ - rr, px_ + rr, py_ + rr), fill=col)
                t += 7
    for (bi, ri, _j), j in juncs.items():
        if len(j) == 2:
            put(im, g_diamond(11, GOLD if spent_ok(ri) else "#4a535c"), j[0] - 5, j[1] - 5)
    # emblem
    er = 44
    glow(im, (int(cx - er), int(cy - er), int(cx + er), int(cy + er)), TREE_COL, 8, 120, er, 3)
    em = ss_glyph(2 * er, 2 * er, lambda d_, s: (d_.ellipse((0, 0, 2 * er * s - 1, 2 * er * s - 1), fill=rgb("#0e1a2c"), outline=rgb(TREE_COL), width=int(3 * s)),
                                              d_.ellipse((7 * s, 7 * s, (2 * er - 7) * s, (2 * er - 7) * s), outline=rgb(GOLD), width=int(1.5 * s))))
    put(im, em, cx - er, cy - er)
    paste_icon(im, I_WARP % "Mining", cx - 26, cy - 34, 52)
    level_pill(im, int(cx - 24), int(cy + 18), "Lv %d" % P["lv"])
    # branch banners
    bn = [(b["name"], b["theme"]) for b in MINING_TREE["branches"]]
    caps = [byid[(bi, 5, "r6")] for bi in range(3)]
    for bi, (nm, th) in enumerate(bn):
        c = caps[bi]
        if bi == 1:
            bx, by_, al = c["x"] + 40, c["y"] - 8, "l"
        elif bi == 0:
            bx, by_, al = CX0 + 8, CY1 - 34, "l"
        else:
            bx, by_, al = CX1 - 8, CY1 - 34, "r"
        if bi != 1:
            put(im, g_diamond(11, TREE_COL), (bx if al == "l" else bx - 11), by_ - 26)
            text(im, (bx + (16 if al == "l" else -16), by_ - 21), "BRANCH %d" % (bi + 1), font("head", 12), PAL["dim"], al + "m", track=1.2)
        text(im, (bx, by_), nm.upper(), font("headb", 15), TREE_COL, al + "m", track=1.5)
        text(im, (bx, by_ + 18), th, font("body", 14), PAL["dim"], al + "m")
    # nodes
    sel = P["sel"]
    for n in nodes:
        bi, ri, uid = n["id"]
        open_ = spent_ok(ri)
        k = P["ranks"].get(n["id"], 0)
        if not open_:
            st = "locked"
        elif n["kind"] == "free":
            st = "max"
        elif k >= n["m"]:
            st = "max"
        elif k > 0:
            st = "learnt"
        else:
            st = "ready" if (P["lv"] - spent) > 0 else "locked"
        sz = n["size"]
        pic, off = node_pic(sz, st, k, n["m"], n["cap"], n["kind"] == "free")
        lx, ly = int(round(n["x"] - sz / 2.0)), int(round(n["y"] - sz / 2.0))
        im.paste(pic, (lx - off, ly - off), pic)
        if n["kind"] == "free":
            nm_ = "B%dR%dFree" % (bi + 1, ri + 1)
        elif n["cap"]:
            nm_ = "B%dR6" % (bi + 1)
        else:
            nm_ = "B%dR%d%s" % (bi + 1, ri + 1, uid[-1])
        rel = I_NODE % ("Mining_" + nm_)
        isz = 20 if n["kind"] == "free" else (32 if n["cap"] else 26)
        if os.path.exists(os.path.join(ROOT, rel)):
            paste_icon(im, rel, n["x"] - isz / 2.0, n["y"] - isz / 2.0 - (2 if n["kind"] == "up" and not n["cap"] else 0), isz,
                       0.4 if st == "locked" else 1.0, grey=(st == "locked"))
        if st == "locked" and n["kind"] != "free":
            put(im, g_lock(14, "#aab4c0"), lx + sz - 13, ly + sz - 14)
        if n["cap"]:
            put(im, g_star(16, "#ffd36b" if open_ else "#6b7380"), lx + sz // 2 - 8, ly - 6)
        if n["id"] == sel:
            hp = ss_glyph(sz + 14, sz + 14, lambda d_, s: d_.ellipse((s, s, (sz + 13) * s, (sz + 13) * s), outline=rgb("#4fe3ff"), width=int(3 * s)))
            put(im, hp, lx - 7, ly - 7)
            selnode = n
    # talent card (top-left corner) + respec (top-right)
    sn = selnode
    bi, ri, uid = sn["id"]
    rowd = MINING_TREE["branches"][bi]["rows"][ri]
    up = [u for u in rowd["ups"] if u["id"] == uid][0]
    k = P["ranks"].get(sn["id"], 0)
    tx0, ty0, tx1, ty1 = CX0 + 4, CY0 + 6, CX0 + 330, CY0 + 156
    panel(im, (tx0, ty0, tx1, ty1), inset=True, c=6)
    outline(im, (tx0, ty0, tx1, ty1), "#2b5f7a", c=6)
    text(im, (tx0 + 12, ty0 + 16), "%s - ROW %d" % (MINING_TREE["branches"][bi]["name"].upper(), ri + 1), font("head", 12), PAL["dim"], "lm", track=1.2)
    text(im, (tx0 + 12, ty0 + 40), up["name"], font("headb", 19), "#ffffff", "lm")
    text(im, (tx1 - 12, ty0 + 40), "Rank %d / %d" % (k, up["max"]), font("headb", 15), PAL["xp"], "rm")
    txt = up["text"]
    words, line, ly2 = txt.split(), "", ty0 + 66
    for w_ in words:
        if tw(line + " " + w_, font("body", 14)) > tx1 - tx0 - 24:
            text(im, (tx0 + 12, ly2), line.strip(), font("body", 14), PAL["green"], "lm")
            line, ly2 = "", ly2 + 19
        line += " " + w_
    text(im, (tx0 + 12, ly2), line.strip(), font("body", 14), PAL["green"], "lm")
    text(im, (tx0 + 12, ty1 - 20), "Cost 1 point", font("body", 14), PAL["dim"], "lm")
    can = P["lv"] - spent > 0
    button(im, (tx1 - 112, ty1 - 36, tx1 - 12, ty1 - 8), "Learn", "primary", "normal" if can else "disabled", fsize=15)
    rx1 = CX1 - 4
    button(im, (rx1 - 150, CY0 + 8, rx1, CY0 + 38), "Respec tree", "secondary", fsize=14)
    text(im, (rx1, CY0 + 54), "2,300 coins", font("body", 14), PAL["dim"], "rm")
    text(im, (rx1, CY0 + 74), "Row 6 opens at 25 points", font("body", 14), PAL["dim"], "rm")


def make_skill_page(key="hi"):
    P = PLAYER[key]
    im, (WX0, WY0, WX1, WY1) = window_v4("Skills")
    X0, X1 = WX0 + 16, WX1 - 16
    Y0, Y1 = 86, 1020
    LX1 = X0 + 250
    RX0 = X1 - 266
    MX0, MX1 = LX1 + 12, RX0 - 12
    stats_column(im, P, X0, Y0, LX1, Y1)
    top_panel(im, P, MX0, Y0, MX1, Y0 + 236)
    collections_panel(im, P, MX0, Y0 + 246, MX1, Y0 + 456)
    tree_panel(im, P, MX0, Y0 + 466, MX1, Y1)
    gy = skills_grid(im, P, RX0, Y0, X1)
    shard_card(im, P, RX0, gy + 10, X1, Y1, locked=P["lv"] < 10)
    footer(im, [("LMB", "Select / learn"), ("Hover", "Details"), ("Shift+LMB", "Learn max"), ("Tab / Esc", "Close")])
    return im


# ================================================================================================================ shard clicker
UPG = {
    "small": [("Tree size", ic_tree, "Lv 2 / 10", [("Logs per fell  ", None), ("3 -> 4", "g")], "5,000", 4, 23, True),
              ("Tree count", ic_trees, "Lv 1 / 6", [("Trees  ", None), ("1 -> 2", "g")], "12,000", 8, 23, True),
              ("Spirit totem", ic_totem, "Lv 1 / 10", [("Chop every  ", None), ("6.0 s -> 5.0 s", "g"), (",  2 logs", None)], "8,000", 6, 23, True),
              ("Weather totem", ic_weather, "not built", [("Regrow  ", None), ("10 s -> 8 s", "g")], "20,000", 16, 23, "buy"),
              ("Island size", ic_island, "Small (1 / 5)", [("+1 spirit pole, ", None), ("+3 tree spots", "g")], "50,000", 32, 23, False),
              ("Decorations", ic_deco, "Lv 0 / 5", [("Looks;  at max ", None), ("+2% drops", "g")], "2,500", 2, 23, True)],
    "grown": [("Tree size", ic_tree, "Lv 6 / 10", [("Logs per fell  ", None), ("7 -> 8", "g")], "60,000", 24, 190, True),
              ("Tree count", ic_trees, "Lv 4 / 6", [("Trees  ", None), ("4 -> 5", "g")], "150,000", 48, 190, "Needs Island 3"),
              ("Spirit totem", ic_totem, "Lv 5 / 10", [("Chop every  ", None), ("3.5 s -> 3.0 s", "g"), (",  4 logs", None)], "45,000", 20, 190, True),
              ("Weather totem", ic_weather, "Lv 3 / 10", [("Regrow  ", None), ("6 s -> 5 s", "g")], "40,000", 18, 190, True),
              ("Island size", ic_island, "Medium (2 / 5)", [("+1 spirit pole, ", None), ("+3 tree spots", "g")], "250,000", 96, 190, "Need Lv 30"),
              ("Decorations", ic_deco, "Lv 4 / 5", [("Looks;  at max ", None), ("+2% drops", "g")], "20,000", 12, 190, True)],
}


def clicker_header(im, X0, X1, y, grown=False, zoomed=False):
    button(im, (X0, y, X0 + 150, y + 36), "Foraging page", "secondary", fsize=15, glyph=g_back(14, "#c2d1e2"))
    paste_icon(im, I_WARP % "Foraging", X0 + 166, y - 2, 40)
    text(im, (X0 + 214, y + 18), "FORAGING SHARD", font("headb", 24), PAL["title"], "lm", track=2)
    x = X0 + 214 + tw("FORAGING SHARD", font("headb", 24), 2) + 16
    x += level_pill(im, x, y + 7, "Foraging Lv 27") + 10
    if zoomed:
        x += chip(im, x, y + 3, "All islands", True) + 10
    else:
        x += chip(im, x, y + 3, "T1 Oak Island" + ("  -  Medium" if grown else "  -  Small"), True) + 10
    text(im, (X1 - 190, y + 10), "Clicks: 25% of world XP", font("bodyb", 14), PAL["xp"], "rm")
    text(im, (X1 - 190, y + 28), "Spirits: 0 XP", font("body", 14), PAL["dim"], "rm")
    button(im, (X1 - 174, y, X1, y + 36), "Zoom in" if zoomed else "Zoom out", "secondary", fsize=15, glyph=g_search(16, "#c2d1e2"))
    taper_line(im, X0, X1, y + 50, PAL["gold"], 150, 0.85)


def sky_view(w, h):
    a = Art(w, h, 3, bg=rgb("#7fc0f0"))
    for k in range(24):
        t = k / 23.0
        a.rect((0, h * t, w, h * (t + 1 / 23.0) + 1), mix("#8fd0ff", "#4a8fd6", t))
    for fx, fy, sc, al in ((0.08, 0.12, 0.8, 150), (0.86, 0.1, 1.0, 140), (0.12, 0.86, 1.1, 120), (0.9, 0.78, 0.9, 120),
                           (0.5, 0.95, 1.4, 100), (0.38, 0.06, 0.6, 110)):
        cloud(a, w * fx, h * fy, sc, al)
    return a


def oak_island_scene(a, cx, cy, grown):
    if not grown:
        island(a, cx, cy, 320, 140, 190, grass="#5cbf4a", rock="#7a6a58")
        # empty tree spot
        a.ell(cx - 190, cy + 30, 46, 20, ("#ffffff", 40), ("#ffffff", 170), 1.6)
        a.ell(cx + 0, cy + 0, 0, 0, None)
        for fx, fy in ((-0.6, -0.2), (0.7, 0.05), (0.15, 0.62)):
            a.ell(cx + 320 * fx, cy + 140 * fy, 9, 5, "#8c8f96", "#1a1410", 1)
        totem(a, cx + 190, cy + 60, 120, "#45a8ff", top="wings")
        spirit(a, cx + 270, cy - 40, 30, body="#b8ffd8", deep="#3aa86a", hat="leaf", carry="log")
        tree(a, cx - 20, cy + 40, 1.1, "oak", hit=True)
        return
    island(a, cx, cy, 520, 205, 210, grass="#5cbf4a", rock="#7a6a58")
    pond(a, cx + 300, cy + 90, 70, 30)
    fence(a, cx - 470, cx - 300, cy + 110)
    for k in range(16):
        t = (k * 0.6180339) % 1
        u = (k * 0.7548777) % 1
        ang = t * 2 * math.pi
        flower(a, cx + 470 * (0.3 + 0.6 * u) * math.cos(ang), cy + 180 * (0.3 + 0.6 * u) * math.sin(ang),
               ["#ff8fb0", "#fff0a0", "#c9a0ff", "#ffffff"][k % 4])
    mushroom(a, cx - 120, cy + 150, 1.2)
    mushroom(a, cx - 100, cy + 160, 0.8)
    lamp_post(a, cx - 260, cy + 120)
    lamp_post(a, cx + 140, cy + 170)
    totem(a, cx + 420, cy - 10, 130, "#5fb4ff", top="cloud", glowing=False)
    a.ell(cx + 420, cy - 182, 40, 10, ("#7fc0ff", 60))
    totem(a, cx - 400, cy + 30, 120, "#45a8ff", top="wings")
    spirit(a, cx - 330, cy - 70, 26, body="#b8ffd8", deep="#3aa86a", hat="leaf", carry="log")
    totem(a, cx + 230, cy + 10, 120, "#45a8ff", top="wings")
    spirit(a, cx + 300, cy - 80, 26, body="#b8ffd8", deep="#3aa86a", hat="leaf", arms_up=True)
    tree(a, cx - 210, cy - 20, 0.75, "oak")
    tree(a, cx + 60, cy - 40, 0.75, "oak")
    tree(a, cx - 50, cy + 110, 0.8, "oak")
    tree(a, cx - 150, cy + 60, 1.0, "oak", hit=True)


def storage_strip(im, x0, y0, x1, y1, grown):
    panel(im, (x0, y0, x1, y1), "Shard storage")
    text(im, (x0 + 200, y0 + 18), "no stack limit", font("body", 14), PAL["dim"], "lm")
    items = [(art_icon(ic_log), "1,284" if not grown else "18,402", "Oak Log"), (None, "412" if not grown else "5,930", "Stick"),
             (art_icon(ic_sap), "58" if not grown else "811", "Tree Sap"), (art_icon(ic_sapling), "37" if not grown else "402", "Oak Sapling"),
             (art_icon(ic_apple), "6" if not grown else "131", "Apple")]
    sx = x0 + 14
    for pic, cnt, nm in items:
        slot(im, sx, y0 + 36, "empty", None, None, size=64)
        if pic is None:
            put_px(im, px_icon("stick"), sx + 8, y0 + 44, 48)
        else:
            p = pic.resize((48, 48), Image.LANCZOS)
            im.paste(p, (sx + 8, y0 + 44), p)
        text(im, (sx + 59, y0 + 96), cnt, font("headb", 15), "#ffffff", "rs")
        sx += 70
    for i in range(3):
        slot(im, sx, y0 + 36, "empty", None, None, size=64)
        sx += 70
    rx = sx + 16
    rows = [("Spirits", "1 at work" if not grown else "2 at work", PAL["row"]), ("Rate", "14 Oak Log / min" if not grown else "71 Oak Log / min",
                                                                                 PAL["green"]),
            ("Offline", "35% for 12 h", PAL["row"])]
    yy = y0 + 46
    for k, v, c in rows:
        text(im, (rx, yy), k, font("body", 15), PAL["dim"], "lm")
        text(im, (rx + 70, yy), v, font("bodyb", 15), c, "lm")
        yy += 23
    button(im, (x1 - 170, y0 + 36, x1 - 14, y0 + 72), "Collect all", "primary", fsize=16)
    button(im, (x1 - 170, y0 + 80, x1 - 14, y0 + 108), "Send to Void", "secondary", fsize=14)


def upgrades_panel(im, x0, y0, x1, y1, key):
    panel(im, (x0, y0, x1, y1), "Upgrades")
    text(im, (x1 - 14, y0 + 18), "coins + Enchanted Oak Log", font("body", 13), PAL["dim"], "rm")
    rows = UPG[key]
    rh = (y1 - y0 - 44) // len(rows)
    ench = I_ENCH % "oak-log"
    for i, (nm, icf, lvl, eff, coins, need_e, have_e, ok) in enumerate(rows):
        ry0 = y0 + 38 + i * rh
        ry1 = ry0 + rh - 8
        row(im, (x0 + 10, ry0, x1 - 10, ry1), "normal")
        slot(im, x0 + 18, ry0 + 10, "empty", None, None, size=56)
        ic = art_icon(icf, 48)
        im.paste(ic, (x0 + 22, ry0 + 14), ic)
        tx = x0 + 84
        text(im, (tx, ry0 + 20), nm, font("headb", 17), "#ffffff", "lm")
        text(im, (x1 - 20, ry0 + 20), lvl, font("headb", 14), PAL["xp"], "rm")
        parts = [(s_, font("bodyb", 14) if c == "g" else font("body", 14), PAL["green"] if c == "g" else PAL["row"]) for s_, c in eff]
        rich(im, tx, ry0 + 44, parts)
        cy_ = ry0 + 72
        put(im, g_coin(16), tx, cy_ - 8)
        afford_c = True
        text(im, (tx + 22, cy_), coins, font("headb", 14), "#ffd76a", "lm")
        ex = tx + 30 + tw(coins, font("headb", 14))
        paste_icon(im, ench, ex, cy_ - 11, 22)
        enough = have_e >= need_e
        text(im, (ex + 26, cy_), "%d / %d" % (min(have_e, 999), need_e), font("headb", 14), PAL["green"] if enough else PAL["red"], "lm")
        lab = "Buy" if ok == "buy" else "Upgrade"
        st = "normal" if ok is True or ok == "buy" else "disabled"
        if ok is False:
            lab = "Need more"
        elif isinstance(ok, str) and ok != "buy":
            lab = ok
        button(im, (x1 - 128, ry1 - 36, x1 - 18, ry1 - 8), lab, "green" if ok == "buy" else "primary", st, fsize=14)
        _ = afford_c


def view_caption(im, x, y, s_):
    f = font("bodyb", 15)
    grad_fill(im, (x - 8, y - 15, x + tw(s_, f) + 10, y + 14), "#0e1729", "#0a111e", c=5, alpha=210)
    text(im, (x, y), s_, f, "#ffffff", "lm")


def make_clicker(grown=False):
    im, (WX0, WY0, WX1, WY1) = window_v4("Skills")
    X0, X1 = WX0 + 16, WX1 - 16
    clicker_header(im, X0, X1, 86, grown)
    VX0, VY0, VX1, VY1 = X0, 148, X1 - 350, 876
    w, h = VX1 - VX0 + 1, VY1 - VY0 + 1
    a = sky_view(w, h)
    oak_island_scene(a, w // 2 - (0 if not grown else 40), h // 2 - 10 + (0 if not grown else 10), grown)
    if grown:
        # bridge to the next island off the right edge
        bridge(a, w // 2 + 470, h // 2 + 40, w + 30, h // 2 + 10)
    view = a.done()
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=8, fill=255)
    im.paste(view, (VX0, VY0), m)
    outline(im, (VX0, VY0, VX1, VY1), PAL["edge"], c=8)
    outline(im, (VX0 + 1, VY0 + 1, VX1 - 1, VY1 - 1), "#34496b", c=7)
    cx, cy = VX0 + w // 2 - (0 if not grown else 40), VY0 + h // 2 - 10 + (0 if not grown else 10)
    if not grown:
        tcx, tby = cx - 20, cy + 40
        # hit counter over the tree
        hx, hy = tcx - 150, tby - 330
        grad_fill(im, (hx - 20, hy, hx + 300, hy + 34), "#0e1729", "#0a111e", c=6)
        outline(im, (hx - 20, hy, hx + 300, hy + 34), "#34496b", c=6)
        ex = rich(im, hx - 8, hy + 17, [("Hits ", font("body", 15), PAL["dim"]), ("2 / 4", font("headb", 16), "#ffffff"),
                                         ("  -  your Copper Hatchet", font("bodyb", 15), TIER["Copper"])])
        K.pips(im, ex + 10, hy + 12, 2, 4, w=10, gap=3)
        # +3 Oak Log pop
        px_, py_ = tcx + 110, tby - 250
        lg = art_icon(ic_log, 40)
        im.paste(lg, (px_, py_ - 20), lg)
        text(im, (px_ + 44, py_), "+3 Oak Log", font("headb", 24), "#ffffff", "lm")
        text(im, (px_ + 44, py_ + 24), "Fortune +1", font("bodyb", 14), PAL["green"], "lm")
        put(im, g_cursor(30), tcx + 30, tby - 120)
        # tree spot + totem labels
        text(im, (cx - 190, cy + 72), "Tree spot 2 - Tree count", font("bodyb", 14), "#ffffff", "mm")
        sp = (cx + 190, cy + 82)
        grad_fill(im, (sp[0] - 92, sp[1], sp[0] + 92, sp[1] + 44), "#0e1729", "#0a111e", c=6, alpha=225)
        outline(im, (sp[0] - 92, sp[1], sp[0] + 92, sp[1] + 44), "#34496b", c=6)
        text(im, (sp[0], sp[1] + 13), "Spirit totem Lv 1", font("headb", 14), "#ffffff", "mm")
        text(im, (sp[0], sp[1] + 31), "next chop in 2.4 s", font("body", 13), PAL["green"], "mm")
        view_caption(im, VX0 + 18, VY1 - 22, "Click the tree: hits and drops use your real hatchet (Breaking Power, Fortune)")
    else:
        tcx, tby = cx - 150, cy + 60
        rich(im, tcx - 120, tby - 300, [("+8 Oak Log", font("headb", 22), "#ffffff")])
        put(im, g_cursor(26), tcx + 20, tby - 110)
        for (lx, ly), s_ in (((cx + 420, cy - 220), "Weather totem Lv 3 - regrow 6 s"), ((cx - 400, cy + 50), "Spirit totem Lv 5"),
                             ((cx + 230, cy + 30), "Spirit totem Lv 1 (new pole)")):
            bw = tw(s_, font("bodyb", 13)) + 18
            grad_fill(im, (lx - bw // 2, ly, lx + bw // 2, ly + 24), "#0e1729", "#0a111e", c=5, alpha=225)
            outline(im, (lx - bw // 2, ly, lx + bw // 2, ly + 24), "#34496b", c=5)
            text(im, (lx, ly + 12), s_, font("bodyb", 13), "#ffffff", "mm")
        bx_, by_ = VX1 - 150, cy - 10
        grad_fill(im, (bx_ - 10, by_ - 64, bx_ + 132, by_ - 18), "#0e1729", "#0a111e", c=6, alpha=230)
        outline(im, (bx_ - 10, by_ - 64, bx_ + 132, by_ - 18), A["base"], c=6)
        text(im, (bx_ + 61, by_ - 50), "T2 Beech Island", font("headb", 15), "#ffffff", "mm")
        text(im, (bx_ + 61, by_ - 30), "click the bridge", font("body", 13), PAL["action"], "mm")
        view_caption(im, VX0 + 18, VY1 - 22, "Upgraded: 4 trees, 2 spirit totems, a weather totem, decorations and a bridge to the next island")
    storage_strip(im, VX0, VY1 + 10, VX1, 1020, grown)
    upgrades_panel(im, VX1 + 12, VY0, X1, 1020, "grown" if grown else "small")
    footer(im, [("LMB", "Chop / select"), ("Hover", "Details"), ("Shift+LMB", "Upgrade max"), ("Tab / Esc", "Close")])
    return im


def make_zoomed():
    im, (WX0, WY0, WX1, WY1) = window_v4("Skills")
    X0, X1 = WX0 + 16, WX1 - 16
    clicker_header(im, X0, X1, 86, True, zoomed=True)
    VX0, VY0, VX1, VY1 = X0, 148, X1 - 350, 1020
    w, h = VX1 - VX0 + 1, VY1 - VY0 + 1
    a = sky_view(w, h)
    isl = [(250, 520, 1.0, "oak", True), (620, 300, 0.75, "beech", True), (900, 610, 0.75, "maple", False), (1120, 300, 0.65, "dry", False)]
    # bridges first (under the islands)
    bridge(a, 250 + 150, 520 - 30, 620 - 120, 300 + 30)
    bridge(a, 620 + 110, 300 + 40, 900 - 110, 610 - 40, ghost=True)
    bridge(a, 900 + 90, 610 - 40, 1120 - 90, 300 + 40, ghost=True)
    for k, (ix, iy, sc, kind, owned) in enumerate(isl):
        sub = Art(w, h, 3)
        island(sub, ix, iy, 200 * sc, 85 * sc, 130 * sc, grass={"oak": "#5cbf4a", "beech": "#7cc04a", "maple": "#c0a24a", "dry": "#c8b46a"}[kind])
        if kind == "oak":
            tree(sub, ix - 90, iy - 10, 0.45, "oak")
            tree(sub, ix + 10, iy - 30, 0.5, "oak")
            tree(sub, ix + 90, iy + 5, 0.45, "oak")
            tree(sub, ix - 20, iy + 40, 0.5, "oak")
            totem(sub, ix - 150, iy + 20, 60, "#45a8ff")
            totem(sub, ix + 150, iy + 30, 60, "#45a8ff")
            spirit(sub, ix + 170, iy - 40, 14, body="#b8ffd8", deep="#3aa86a", hat="leaf")
        elif kind == "beech":
            tree(sub, ix - 30, iy + 10, 0.55, "beech")
            totem(sub, ix + 90, iy + 20, 55, "#45a8ff")
            spirit(sub, ix + 110, iy - 30, 12, body="#b8ffd8", deep="#3aa86a", hat="leaf")
        elif kind == "maple":
            tree(sub, ix, iy + 10, 0.55, "maple")
        else:
            tree(sub, ix, iy + 10, 0.5, "dry")
        img = sub.im
        if not owned:
            img = grey_img(img, 0.6)
        a.im.alpha_composite(img)
    view = a.done()
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=8, fill=255)
    im.paste(view, (VX0, VY0), m)
    outline(im, (VX0, VY0, VX1, VY1), PAL["edge"], c=8)
    outline(im, (VX0 + 1, VY0 + 1, VX1 - 1, VY1 - 1), "#34496b", c=7)
    labels = [("T1 Oak Island", "Medium - 4 trees - 2 spirits", "You are here", "#8fe08a"),
              ("T2 Beech Island", "Small - 1 tree - 1 spirit", "Click to go", "#c3e36a"),
              ("T3 Maple Island", "Needs Maple Log collection II", "412 / 500", "#f4a24a"),
              ("T4 Dry Island", "Needs Foraging Lv 20 + T3 Maple", "locked", "#d6c886")]
    for (ix, iy, sc, kind, owned), (t1, t2, t3, col) in zip(isl, labels):
        lx, ly = VX0 + ix, VY0 + iy + int(85 * sc) + int(130 * sc) + 16
        if iy < 400:   # upper islands: the plate goes above them (keeps the bridges clear)
            ly = VY0 + iy - 185
        bw = max(tw(t1, font("headb", 16)), tw(t2, font("body", 13))) + 30
        grad_fill(im, (lx - bw // 2, ly, lx + bw // 2, ly + 66), "#0e1729", "#0a111e", c=6, alpha=235)
        outline(im, (lx - bw // 2, ly, lx + bw // 2, ly + 66), A["base"] if t3 == "You are here" else ("#34496b" if owned else "#3a4658"), c=6)
        text(im, (lx, ly + 15), t1, font("headb", 16), col if owned else "#8a97a8", "mm")
        text(im, (lx, ly + 35), t2, font("body", 13), PAL["row"] if owned else PAL["dim"], "mm")
        text(im, (lx, ly + 54), t3, font("bodyb", 13), PAL["action"] if owned else (PAL["xp"] if "/" in t3 else PAL["dim"]), "mm")
        if not owned:
            put(im, g_lock(34, "#d6e4ee"), lx - 17, VY0 + iy - 40)
    # islands list
    x0, y0, x1, y1 = VX1 + 12, VY0, X1, 1020
    panel(im, (x0, y0, x1, y1), "Islands")
    rows = [("T1 Oak Island", "Owned - Medium", "Oak", True, "Here"), ("T2 Beech Island", "Owned - Small", "Beech", True, "Go"),
            ("T3 Maple Island", "Maple Log coll. II  412 / 500", "Maple", False, "Buy"),
            ("T4 Dry Island", "Foraging Lv 20, then T3", "Dry", False, "Locked")]
    ry = y0 + 40
    for nm, sub_, kind, owned, btn in rows:
        row(im, (x0 + 10, ry, x1 - 10, ry + 112), "selected" if btn == "Here" else "normal")
        ic = art_icon(lambda a_, n, k=kind.lower(): tree(a_, n * 0.5, n * 0.9, n / 170.0, k), 48)
        if not owned:
            ic = grey_img(ic, 0.7)
        slot(im, x0 + 20, ry + 12, "empty", None, None, size=56)
        im.paste(ic, (x0 + 24, ry + 16), ic)
        text(im, (x0 + 88, ry + 24), nm, font("headb", 16), "#ffffff" if owned else "#8a97a8", "lm")
        text(im, (x0 + 88, ry + 46), sub_, font("body", 13), PAL["row"] if owned else PAL["dim"], "lm")
        if btn == "Here":
            text(im, (x1 - 24, ry + 92), "You are here", font("bodyb", 14), A["hi"], "rm")
        elif btn == "Go":
            button(im, (x1 - 120, ry + 74, x1 - 22, ry + 102), "Go", "primary", fsize=15)
        elif btn == "Buy":
            put(im, g_coin(16), x0 + 88, ry + 62)
            text(im, (x0 + 110, ry + 70), "250,000", font("headb", 14), "#ffd76a", "lm")
            button(im, (x1 - 120, ry + 74, x1 - 22, ry + 102), "Buy", "green", "disabled", fsize=15)
        else:
            put(im, g_lock(18), x1 - 40, ry + 80)
        ry += 122
    text(im, (x0 + 14, ry + 14), "Each island is one wood tier,", font("body", 14), PAL["dim"], "lm")
    text(im, (x0 + 14, ry + 34), "like the world (same level +", font("body", 14), PAL["dim"], "lm")
    text(im, (x0 + 14, ry + 54), "collection). Bridges join them.", font("body", 14), PAL["dim"], "lm")
    footer(im, [("LMB", "Pick an island"), ("Hover", "Details"), ("Tab / Esc", "Close")])
    return im


def main():
    out = {"skill-page-mining.png": lambda: make_skill_page("hi"),
           "skill-page-mining-locked.png": lambda: make_skill_page("lo"),
           "shard-clicker-foraging.png": lambda: make_clicker(False),
           "shard-clicker-foraging-grown.png": lambda: make_clicker(True),
           "shard-clicker-zoomed-out.png": make_zoomed}
    only = sys.argv[1:]
    for fn, maker in out.items():
        if only and fn not in only:
            continue
        im = maker()
        im.save(os.path.join(HERE, fn), optimize=True)
        print("wrote", fn, im.size)


if __name__ == "__main__":
    main()
