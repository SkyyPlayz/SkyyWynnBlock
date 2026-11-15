"""SkyWynn UI theme "Skyglass" - concept art generator (plan P0b, research/Inventory-Screen-Plan.md).

Writes, next to this file:
  theme-sheet.png       the UI kit, every part labelled with its size in px (1 px = 1 UI unit at 1080p, UI scale 1)
  inventory-mockup.png  the Inventory tab of the new screen at 1920 x 1080
  accent-options.png    the same small panel + tab bar + slot row in 3 accent colours

Deterministic: two runs give the same bytes (no randomness, no timestamps). Needs Python 3 + Pillow (tested on Pillow 13).
Fonts: Windows' Bahnschrift (headings, tabs, buttons) and Segoe UI (body) as stand-ins - the game font is the client's own.
Item pictures: ONLY our own committed SkyWynn icons (art/, research/cloud/*-art/); no vanilla file is read.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

# ----------------------------------------------------------------------------------------------------------------- palette
ACCENTS = {  # name: (base, hi, lo, deep, button top, button bottom)
    "Sky Azure": ("#45a8ff", "#8fcbff", "#2a78c8", "#123a5e", "#2f86d8", "#1c5ea6"),
    "Sun Gold": ("#f2b84b", "#ffd98a", "#b9852a", "#4a3410", "#c88f2c", "#8f6118"),
    "Aurora Teal": ("#33d6b5", "#8af0db", "#1f9c84", "#0f3f36", "#22a58b", "#16735f"),
}
PAL = {
    "screen": "#070b13", "window": "#0c1422", "window2": "#101a2c", "panel": "#111b2d", "panel2": "#152138",
    "inset": "#09101c", "line": "#22324b", "lineHi": "#34496b", "edge": "#04070d",
    "gold": "#c9a04e", "goldHi": "#f1d58c", "goldLo": "#6b5122",
    "title": "#eef5ff", "text": "#c2d1e2", "row": "#d6e4ee", "dim": "#7f93a6", "placeholder": "#6e7da1",
    "green": "#4fd88a", "red": "#ff6b6b", "xp": "#e8c25a", "action": "#ffcc00",
    "health": "#e5484d", "mana": "#4d8dff", "stamina": "#f0c53a", "defense": "#9fb0c6",
}
A = {}  # the live accent (set_accent)


def set_accent(name):
    b, hi, lo, deep, bt, bb = ACCENTS[name]
    A.update(base=b, hi=hi, lo=lo, deep=deep, btnTop=bt, btnBot=bb, name=name)


set_accent("Sky Azure")

GEAR_RARITY = [("Normal", "#FFFFFF"), ("Unique", "#FFFF55"), ("Rare", "#FF55FF"), ("Legendary", "#55FFFF"),
               ("Fabled", "#FF5555"), ("Mythic", "#CC66CC"), ("Set", "#55FF55"), ("Untiered", "#FFAA00")]
QUALITY_RARITY = [("Common", "#c9d2dd"), ("Uncommon", "#3e9049"), ("Rare", "#2770b7"), ("Epic", "#8b339e"),
                  ("Legendary", "#bb8a2c"), ("Mythic", "#CC66CC")]
RAR = dict(GEAR_RARITY)


def rgb(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def mix(c1, c2, t):
    a, b = rgb(c1), rgb(c2)
    return "#%02x%02x%02x" % tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


# ----------------------------------------------------------------------------------------------------------------- fonts
FONT_DIR = os.path.join(os.environ.get("WINDIR", "C:/Windows"), "Fonts")
_fonts = {}


def font(kind, size):
    """kind: 'head' (Bahnschrift SemiBold), 'headc' (SemiBold Condensed), 'body', 'bodyb' (Segoe UI Semibold), 'bold'."""
    key = (kind, size)
    if key in _fonts:
        return _fonts[key]
    try:
        if kind in ("head", "headc", "headb"):
            f = ImageFont.truetype(os.path.join(FONT_DIR, "bahnschrift.ttf"), size)
            f.set_variation_by_name({"head": "SemiBold", "headc": "SemiBold Condensed", "headb": "Bold"}[kind])
        else:
            fn = {"body": "segoeui.ttf", "bodyb": "seguisb.ttf", "bold": "segoeuib.ttf", "ital": "segoeuii.ttf"}[kind]
            f = ImageFont.truetype(os.path.join(FONT_DIR, fn), size)
    except OSError:
        f = ImageFont.load_default(size)
    _fonts[key] = f
    return f


def tw(s, f, track=0):
    return int(round(f.getlength(s) + track * max(0, len(s) - 1)))


def text(im, xy, s, f, fill, anchor="la", shadow=True, track=0):
    d = ImageDraw.Draw(im, "RGBA")
    x, y = xy
    if track:
        w = tw(s, f, track)
        if anchor[0] == "m":
            x -= w / 2
        elif anchor[0] == "r":
            x -= w
        anc = "l" + anchor[1]
        for ch in s:
            if shadow:
                d.text((x + 1, y + 1), ch, font=f, fill=(0, 0, 0, 170), anchor=anc)
            d.text((x, y), ch, font=f, fill=rgb(fill) if isinstance(fill, str) else fill, anchor=anc)
            x += f.getlength(ch) + track
        return
    if shadow:
        d.text((x + 1, y + 1), s, font=f, fill=(0, 0, 0, 170), anchor=anchor)
    d.text((x, y), s, font=f, fill=rgb(fill) if isinstance(fill, str) else fill, anchor=anchor)


def rich(im, x, y, parts, anchor_v="m"):
    """parts = [(text, font, colour)] drawn left to right; returns end x."""
    for s, f, c in parts:
        text(im, (x, y), s, f, c, "l" + anchor_v)
        x += tw(s, f)
    return x


# ----------------------------------------------------------------------------------------------------------------- icons
_icons = {}


def icon(rel, size=64):
    key = (rel, size)
    if key in _icons:
        return _icons[key]
    if rel.startswith("px:"):
        im = px_icon(rel[3:]).resize((size, size), Image.NEAREST if size % 16 == 0 else Image.LANCZOS)
        _icons[key] = im
        return im
    im = Image.open(os.path.join(ROOT, rel)).convert("RGBA")
    if im.size[0] != size:
        if im.size[0] % size == 0:
            im = im.reduce(im.size[0] // size)
        else:
            im = im.resize((size, size), Image.LANCZOS)
    _icons[key] = im
    return im


def paste_icon(im, rel, x, y, size=64, alpha=1.0, grey=False):
    ic = icon(rel, size)
    if grey:
        g = ic.convert("LA").convert("RGBA")
        g.putalpha(ic.getchannel("A"))
        ic = g
    if alpha < 1:
        ic = ic.copy()
        ic.putalpha(ic.getchannel("A").point(lambda v: int(v * alpha)))
    im.paste(ic, (int(x), int(y)), ic)


I_ENCH = "research/cloud/enchanted-art/icons-v2/ench-%s.png"
I_ACC = "research/cloud/accessory-art/icons-v2/%s.png"
I_FISH = "research/cloud/fish-art/icons/%s.png"
I_GEAR = "research/cloud/fishing-art/icons/%s.png"
I_HUB = "art/hub-tab-icons/%s_on.png"
I_WARP = "art/warp-icons/Common/Icons/ItemsGenerated/Skyy_Menu_Icon_Warp%s.png"
I_NODE = "art/tree-node-icons/Common/Icons/ItemsGenerated/Skyy_NodeIcon_%s.png"
I_EGG = "art/pet-eggs/Common/Icons/ItemsGenerated/Skyy_PetEgg_%s.png"
I_PET = "art/pets/Common/Icons/ItemsGenerated/SkyyPets_Pet_%s.png"
I_ARM = "art/gathering-armor/Common/Icons/ItemsGenerated/Armor_%s.png"
I_ABIL = "art/hotbar-items/Common/Icons/ItemsGenerated/SkyyClasses_AbilityItem_%s.png"
I_EMB = "art/class-emblems/Common/Icons/ClassEmblems/%s.png"
I_MENU2 = "art/menu-icons-2/Common/Icons/ItemsGenerated/Skyy_Menu_Icon_%s.png"
I_VOID = "art/void-charms-icon/Common/Icons/ItemsGenerated/Skyy_Menu_Icon_VoidCharms.png"

# v3 placeholder item pictures for normal vanilla items (Skyy 11-14: no charm / pet / fishing recipes in inventory crafting).
# Simple ORIGINAL 16 x 16 shapes drawn here - stand-ins only, NOT the game's icons (the real page shows each item's own icon).
def px_icon(name):
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    wood, woodL, grey, greyL = rgb("#8a5a2b"), rgb("#b07a40"), rgb("#9aa6b4"), rgb("#dfe7f0")

    def handle(x0, y0, x1, y1):
        d.line([(x0, y0), (x1, y1)], fill=wood, width=2)
    if name == "pickaxe":
        handle(3, 13, 10, 6)
        d.line([(6, 3), (9, 2), (12, 4), (13, 7), (14, 10)], fill=grey, width=2)
        d.point([(9, 2), (12, 4)], fill=greyL)
    elif name == "axe":
        handle(3, 13, 11, 5)
        d.polygon([(9, 2), (13, 2), (14, 6), (12, 8), (10, 6)], fill=grey)
        d.line([(13, 2), (14, 6)], fill=greyL)
    elif name == "shovel":
        handle(3, 13, 10, 6)
        d.polygon([(9, 4), (12, 1), (15, 4), (12, 7)], fill=grey)
        d.point([(12, 2)], fill=greyL)
    elif name == "sword":
        d.line([(5, 10), (13, 2)], fill=grey, width=2)
        d.line([(6, 9), (13, 2)], fill=greyL)
        d.line([(3, 8), (7, 12)], fill=rgb("#c9a04e"), width=2)
        d.line([(2, 13), (4, 11)], fill=wood, width=2)
    elif name == "torch":
        d.rectangle((7, 7, 8, 14), fill=wood)
        d.ellipse((5, 1, 10, 7), fill=rgb("#ff9a2e"))
        d.ellipse((6, 3, 9, 7), fill=rgb("#ffe27a"))
    elif name == "planks":
        d.rectangle((1, 2, 14, 13), fill=woodL)
        for y in (5, 9):
            d.line([(1, y), (14, y)], fill=wood)
        d.point([(3, 3), (12, 7), (5, 11)], fill=wood)
    elif name == "chest":
        d.rectangle((1, 4, 14, 13), fill=wood)
        d.rectangle((1, 4, 14, 7), fill=woodL)
        d.rectangle((7, 6, 8, 9), fill=rgb("#e8c25a"))
    elif name == "bread":
        d.ellipse((1, 5, 14, 12), fill=rgb("#c98a3e"))
        d.ellipse((2, 5, 13, 9), fill=rgb("#e0a85a"))
        for x in (5, 8, 11):
            d.line([(x, 6), (x - 1, 8)], fill=wood)
    elif name == "stew":
        d.chord((1, 4, 14, 14), 0, 180, fill=wood)
        d.ellipse((1, 5, 14, 9), fill=rgb("#c8582e"))
        d.point([(5, 6), (9, 7), (11, 6)], fill=rgb("#f0c060"))
    elif name == "ingot":
        d.polygon([(2, 10), (5, 6), (14, 6), (11, 10)], fill=grey)
        d.polygon([(2, 10), (11, 10), (11, 12), (2, 12)], fill=rgb("#6c7888"))
        d.line([(5, 7), (12, 7)], fill=greyL)
    elif name == "stick":
        d.line([(3, 13), (12, 3)], fill=wood, width=2)
        d.point([(11, 4)], fill=woodL)
    a = im.getchannel("A").load()
    px = im.load()
    edge = [(x, y) for y in range(16) for x in range(16) if a[x, y] == 0 and any(
        0 <= x + dx < 16 and 0 <= y + dy < 16 and a[x + dx, y + dy] > 0 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for x, y in edge:
        px[x, y] = (8, 10, 16, 255)
    return im


# ----------------------------------------------------------------------------------------------------------------- primitives


def cham(x0, y0, x1, y1, c):
    """Chamfered box polygon (x1 / y1 inclusive)."""
    return [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c)]


def mask_poly(w, h, pts):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return m


def grad_fill(im, box, top, bot, c=0, alpha=255):
    x0, y0, x1, y1 = box
    w, h = x1 - x0 + 1, y1 - y0 + 1
    g = Image.linear_gradient("L").resize((w, h))
    a = Image.new("RGB", (w, h), rgb(top)[:3])
    b = Image.new("RGB", (w, h), rgb(bot)[:3])
    fillim = Image.composite(b, a, g)
    m = mask_poly(w, h, cham(0, 0, w - 1, h - 1, c))
    if alpha < 255:
        m = m.point(lambda v: v * alpha // 255)
    im.paste(fillim, (x0, y0), m)


def outline(im, box, col, c=0, width=1, alpha=255):
    d = ImageDraw.Draw(im, "RGBA")
    x0, y0, x1, y1 = box
    for i in range(width):
        d.polygon(cham(x0 + i, y0 + i, x1 - i, y1 - i, max(0, c - i)), outline=rgb(col, alpha))


def hline(im, x0, x1, y, col, alpha=255):
    ImageDraw.Draw(im, "RGBA").line([(x0, y), (x1, y)], fill=rgb(col, alpha))


def taper_line(im, x0, x1, y, col, peak=255, solid=0.6):
    """A hairline that fades out at both ends (the gold ornament line)."""
    d = ImageDraw.Draw(im, "RGBA")
    n = x1 - x0
    for i in range(n + 1):
        t = i / max(1, n)
        e = min(t, 1 - t) * 2
        a = peak if e >= (1 - solid) else int(peak * e / (1 - solid))
        d.point((x0 + i, y), fill=rgb(col, a))


def glow(im, box, col, radius=6, strength=150, c=0, width=2):
    """Soft outer glow around a box (draw an outline on a local layer, blur, composite)."""
    x0, y0, x1, y1 = box
    m = radius * 3
    w, h = x1 - x0 + 1 + 2 * m, y1 - y0 + 1 + 2 * m
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(layer).polygon(cham(m, m, w - 1 - m, h - 1 - m, c), outline=rgb(col, strength), width=width)
    layer = layer.filter(ImageFilter.GaussianBlur(radius))
    region = im.crop((x0 - m, y0 - m, x0 - m + w, y0 - m + h)).convert("RGBA")
    region = Image.alpha_composite(region, layer)
    im.paste(region.convert("RGB"), (x0 - m, y0 - m))


def shadow(im, box, radius=10, strength=170, off=4):
    x0, y0, x1, y1 = box
    m = radius * 3
    w, h = x1 - x0 + 1 + 2 * m, y1 - y0 + 1 + 2 * m
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(layer).rectangle((m, m + off, w - 1 - m, h - 1 - m + off), fill=(0, 0, 0, strength))
    layer = layer.filter(ImageFilter.GaussianBlur(radius))
    region = im.crop((x0 - m, y0 - m, x0 - m + w, y0 - m + h)).convert("RGBA")
    im.paste(Image.alpha_composite(region, layer).convert("RGB"), (x0 - m, y0 - m))


def ss_glyph(w, h, fn, scale=4):
    """Supersampled glyph: fn(draw, s) draws at s x size; returns an anti-aliased RGBA image w x h."""
    big = Image.new("RGBA", (w * scale, h * scale), (0, 0, 0, 0))
    fn(ImageDraw.Draw(big), scale)
    return big.resize((w, h), Image.LANCZOS)


def put(im, g, x, y):
    im.paste(g, (int(x), int(y)), g)


# ----------------------------------------------------------------------------------------------------------------- glyphs

def g_diamond(size, col, hi=None, dark="#05080e"):
    def f(d, s):
        n = size * s
        d.polygon([(n / 2, 0), (n - 1, n / 2), (n / 2, n - 1), (0, n / 2)], fill=rgb(dark))
        k = s * 1.3
        d.polygon([(n / 2, k), (n - 1 - k, n / 2), (n / 2, n - 1 - k), (k, n / 2)], fill=rgb(col))
        d.polygon([(n / 2, k), (n / 2, n / 2), (k, n / 2)], fill=rgb(hi or mix(col, "#ffffff", 0.45)))
    return ss_glyph(size, size, f)


def g_heart(size, col):
    def f(d, s):
        n = size * s
        r = n * 0.27
        d.ellipse((n * 0.06, n * 0.12, n * 0.06 + 2 * r, n * 0.12 + 2 * r), fill=rgb(col))
        d.ellipse((n * 0.94 - 2 * r, n * 0.12, n * 0.94, n * 0.12 + 2 * r), fill=rgb(col))
        d.polygon([(n * 0.08, n * 0.42), (n * 0.92, n * 0.42), (n * 0.5, n * 0.9)], fill=rgb(col))
        d.ellipse((n * 0.2, n * 0.22, n * 0.36, n * 0.38), fill=rgb(mix(col, "#ffffff", 0.5)))
    return ss_glyph(size, size, f)


def g_drop(size, col):
    def f(d, s):
        n = size * s
        d.ellipse((n * 0.2, n * 0.38, n * 0.8, n * 0.95), fill=rgb(col))
        d.polygon([(n * 0.5, n * 0.04), (n * 0.78, n * 0.55), (n * 0.22, n * 0.55)], fill=rgb(col))
        d.ellipse((n * 0.32, n * 0.55, n * 0.45, n * 0.72), fill=rgb(mix(col, "#ffffff", 0.55)))
    return ss_glyph(size, size, f)


def g_bolt(size, col):
    def f(d, s):
        n = size * s
        d.polygon([(n * 0.58, n * 0.02), (n * 0.18, n * 0.56), (n * 0.46, n * 0.56), (n * 0.36, n * 0.98),
                   (n * 0.84, n * 0.4), (n * 0.54, n * 0.4), (n * 0.7, n * 0.02)], fill=rgb(col))
    return ss_glyph(size, size, f)


def g_shield(size, col):
    def f(d, s):
        n = size * s
        d.polygon([(n * 0.5, n * 0.04), (n * 0.9, n * 0.18), (n * 0.86, n * 0.55), (n * 0.5, n * 0.96),
                   (n * 0.14, n * 0.55), (n * 0.1, n * 0.18)], fill=rgb(col))
        d.polygon([(n * 0.5, n * 0.14), (n * 0.5, n * 0.84), (n * 0.22, n * 0.52), (n * 0.2, n * 0.25)],
                  fill=rgb(mix(col, "#ffffff", 0.35)))
    return ss_glyph(size, size, f)


def g_coin(size):
    def f(d, s):
        n = size * s
        d.ellipse((0, 0, n - 1, n - 1), fill=rgb("#6b4a12"))
        d.ellipse((s, s, n - 1 - s, n - 1 - s), fill=rgb("#e8b53a"))
        d.ellipse((n * 0.22, n * 0.22, n * 0.78, n * 0.78), outline=rgb("#a8781c"), width=int(s * 1.2))
        d.ellipse((n * 0.2, n * 0.12, n * 0.42, n * 0.3), fill=rgb("#fff0b0"))
    return ss_glyph(size, size, f)


def g_envelope(size, col):
    def f(d, s):
        n = size * s
        d.rectangle((n * 0.06, n * 0.2, n * 0.94, n * 0.82), fill=rgb(col))
        d.line([(n * 0.06, n * 0.2), (n * 0.5, n * 0.56), (n * 0.94, n * 0.2)], fill=rgb("#0c1422"), width=int(s * 1.6))
    return ss_glyph(size, size, f)


def g_search(size, col):
    def f(d, s):
        n = size * s
        d.ellipse((n * 0.08, n * 0.08, n * 0.66, n * 0.66), outline=rgb(col), width=int(s * 2))
        d.line([(n * 0.58, n * 0.58), (n * 0.92, n * 0.92)], fill=rgb(col), width=int(s * 2.6))
    return ss_glyph(size, size, f)


def g_x(size, col, wdt=2.4):
    def f(d, s):
        n = size * s
        k = n * 0.2
        d.line([(k, k), (n - k, n - k)], fill=rgb(col), width=int(s * wdt))
        d.line([(n - k, k), (k, n - k)], fill=rgb(col), width=int(s * wdt))
    return ss_glyph(size, size, f)


def g_plus(size, col):
    def f(d, s):
        n = size * s
        k = n * 0.18
        d.line([(n / 2, k), (n / 2, n - k)], fill=rgb(col), width=int(s * 2.4))
        d.line([(k, n / 2), (n - k, n / 2)], fill=rgb(col), width=int(s * 2.4))
    return ss_glyph(size, size, f)


def g_pencil(size, col):
    def f(d, s):
        n = size * s
        d.polygon([(n * 0.66, n * 0.1), (n * 0.9, n * 0.34), (n * 0.36, n * 0.88), (n * 0.12, n * 0.64)], fill=rgb(col))
        d.polygon([(n * 0.12, n * 0.64), (n * 0.36, n * 0.88), (n * 0.06, n * 0.94)], fill=rgb(mix(col, "#000000", 0.4)))
    return ss_glyph(size, size, f)


def g_chev(size, col):
    def f(d, s):
        n = size * s
        d.line([(n * 0.34, n * 0.18), (n * 0.68, n * 0.5), (n * 0.34, n * 0.82)], fill=rgb(col), width=int(s * 2.4))
    return ss_glyph(size, size, f)


def g_check(size, col):
    def f(d, s):
        n = size * s
        d.line([(n * 0.14, n * 0.52), (n * 0.4, n * 0.78), (n * 0.88, n * 0.22)], fill=rgb(col), width=int(s * 2.6))
    return ss_glyph(size, size, f)


def g_sword(size, col):
    def f(d, s):
        n = size * s
        d.line([(n * 0.2, n * 0.8), (n * 0.86, n * 0.14)], fill=rgb(col), width=int(s * 2.4))
        d.line([(n * 0.12, n * 0.62), (n * 0.38, n * 0.88)], fill=rgb(col), width=int(s * 2.4))
    return ss_glyph(size, size, f)


def g_quest(size, col):
    def f(d, s):
        n = size * s
        d.polygon(cham(n * 0.14, n * 0.06, n * 0.86, n * 0.94, n * 0.12), fill=rgb(col))
        d.rectangle((n * 0.44, n * 0.2, n * 0.56, n * 0.62), fill=rgb("#0c1422"))
        d.rectangle((n * 0.44, n * 0.7, n * 0.56, n * 0.82), fill=rgb("#0c1422"))
    return ss_glyph(size, size, f)


# ----------------------------------------------------------------------------------------------------------------- kit parts

def window_frame(im, box, title=None):
    """The window: 1 px edge, 2 px gold trim, dark body, gold corner brackets with an accent gem, ornament on the top edge."""
    x0, y0, x1, y1 = box
    shadow(im, box, 14, 200, 6)
    grad_fill(im, box, PAL["window2"], PAL["window"], c=10)
    outline(im, box, PAL["edge"], c=10)
    outline(im, (x0 + 1, y0 + 1, x1 - 1, y1 - 1), PAL["goldLo"], c=9)
    outline(im, (x0 + 2, y0 + 2, x1 - 2, y1 - 2), PAL["gold"], c=8)
    outline(im, (x0 + 3, y0 + 3, x1 - 3, y1 - 3), "#1d2b42", c=7)
    hline(im, x0 + 12, x1 - 12, y0 + 2, PAL["goldHi"], 140)
    # corner brackets
    d = ImageDraw.Draw(im, "RGBA")
    for cx, cy, sx, sy in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        L = 26
        for i, col in ((5, PAL["gold"]), (6, PAL["goldLo"])):
            d.line([(cx + sx * i, cy + sy * (i + 6)), (cx + sx * i, cy + sy * L)], fill=rgb(col))
            d.line([(cx + sx * (i + 6), cy + sy * i), (cx + sx * L, cy + sy * i)], fill=rgb(col))
        d.line([(cx + sx * 5, cy + sy * 11), (cx + sx * 11, cy + sy * 5)], fill=rgb(PAL["goldHi"]))
        g = g_diamond(11, A["base"], A["hi"])
        put(im, g, cx + sx * 9 - (10 if sx < 0 else 0) - (0 if sx > 0 else 0), cy + sy * 9 - (10 if sy < 0 else 0))
    # top-centre ornament: gem + tapering gold wings
    mx = (x0 + x1) // 2
    taper_line(im, mx - 120, mx - 10, y0 + 3, PAL["goldHi"], 230, 0.3)
    taper_line(im, mx + 10, mx + 120, y0 + 3, PAL["goldHi"], 230, 0.3)
    put(im, g_diamond(15, A["base"], A["hi"]), mx - 7, y0 - 4)
    if title:
        title_plate(im, mx, y0, title)


def title_plate(im, mx, ytop, title):
    f = font("head", 20)
    w = tw(title.upper(), f, 2) + 64
    x0, x1 = mx - w // 2, mx + w // 2
    y0, y1 = ytop - 14, ytop + 18
    grad_fill(im, (x0, y0, x1, y1), "#1b2a44", "#0e1828", c=12)
    outline(im, (x0, y0, x1, y1), PAL["edge"], c=12)
    outline(im, (x0 + 1, y0 + 1, x1 - 1, y1 - 1), PAL["gold"], c=11)
    hline(im, x0 + 12, x1 - 12, y0 + 2, PAL["goldHi"], 120)
    put(im, g_diamond(9, A["base"], A["hi"]), x0 + 14, (y0 + y1) // 2 - 4)
    put(im, g_diamond(9, A["base"], A["hi"]), x1 - 22, (y0 + y1) // 2 - 4)
    text(im, (mx, (y0 + y1) // 2 + 1), title.upper(), f, PAL["title"], "mm", track=2)


def panel(im, box, title=None, link=None, inset=False, c=6):
    x0, y0, x1, y1 = box
    if inset:
        grad_fill(im, box, "#070d18", PAL["inset"], c=c)
        outline(im, box, "#18243a", c=c)
        hline(im, x0 + c, x1 - c, y0 + 1, "#000000", 120)
        return
    grad_fill(im, box, PAL["panel2"], PAL["panel"], c=c)
    outline(im, box, PAL["line"], c=c)
    hline(im, x0 + c, x1 - c, y0 + 1, "#ffffff", 14)
    if title:
        panel_title(im, x0 + 14, y0 + 18, title, x1 - 14)
    if link:
        f = font("head", 15)
        text(im, (x1 - 30, y0 + 18), link, f, A["hi"], "rm")
        put(im, g_chev(14, A["hi"]), x1 - 28, y0 + 11)


def panel_title(im, x, y, title, x_end):
    put(im, g_diamond(9, A["base"], A["hi"]), x, y - 4)
    f = font("head", 16)
    text(im, (x + 16, y), title.upper(), f, PAL["title"], "lm", track=1.5)
    tx = x + 16 + tw(title.upper(), f, 1.5) + 10
    taper_line(im, x, min(x_end, x + 330), y + 13, PAL["gold"], 200, 0.45)
    return tx


def tab(im, box, label, icon_rel=None, state="normal", fsize=16, fkind="head", isz=24):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(im, "RGBA")
    if state == "selected":
        grad_fill(im, (x0, y0, x1, y1 + 1), "#1a2b47", PAL["panel2"], c=0)
        d.polygon(cham(x0, y0, x1, y1 + 6, 4)[:2] + [(x1, y0 + 4), (x1, y1 + 1), (x0, y1 + 1), (x0, y0 + 4)],
                  outline=rgb(PAL["lineHi"]))
        glow(im, (x0 + 4, y0, x1 - 4, y0 + 2), A["base"], 5, 170, 0, 2)
        d.rectangle((x0 + 4, y0, x1 - 4, y0 + 2), fill=rgb(A["base"]))
        hline(im, x0 + 4, x1 - 4, y0, A["hi"])
        col, ialpha = PAL["title"], 1.0
    elif state == "hover":
        grad_fill(im, (x0, y0 + 2, x1, y1), "#16233a", "#111b2d", c=3)
        outline(im, (x0, y0 + 2, x1, y1), "#2a3c5a", c=3)
        d.rectangle((x0 + 6, y0 + 2, x1 - 6, y0 + 3), fill=rgb(A["lo"]))
        col, ialpha = "#dbe7f5", 0.95
    elif state == "pressed":
        grad_fill(im, (x0, y0 + 2, x1, y1), "#0b1322", "#0f192b", c=3)
        outline(im, (x0, y0 + 2, x1, y1), "#2a3c5a", c=3)
        col, ialpha = "#b9c9db", 0.85
    else:
        col, ialpha = "#93a7bf", 0.6
    f = font(fkind, fsize)
    tw_ = tw(label, f) if label else 0
    isz = isz if icon_rel else 0
    total = tw_ + (isz + 6 if (icon_rel and label) else isz)
    cx = (x0 + x1) // 2 - total // 2
    cy = (y0 + y1) // 2 + 1
    if icon_rel:
        paste_icon(im, icon_rel, cx, cy - isz // 2, isz, ialpha, grey=(state == "normal"))
        cx += isz + 6
    if label:
        text(im, (cx, cy), label, f, col, "lm")


def button(im, box, label, kind="primary", state="normal", fsize=16, glyph=None):
    x0, y0, x1, y1 = box
    c = 5
    if kind == "primary":
        top, bot, rim, hi, tc = A["btnTop"], A["btnBot"], A["base"], A["hi"], "#ffffff"
        if state == "hover":
            top, bot, rim = mix(A["btnTop"], "#ffffff", 0.14), mix(A["btnBot"], "#ffffff", 0.12), A["hi"]
        if state == "pressed":
            top, bot, hi = mix(A["btnBot"], "#000000", 0.25), A["btnBot"], A["base"]
    elif kind == "danger":
        top, bot, rim, hi, tc = "#a3343d", "#73202a", "#e45a62", "#ff9aa0", "#ffffff"
        if state == "hover":
            top, bot, rim = "#b8424b", "#842630", "#ff7d84"
        if state == "pressed":
            top, bot = "#5e1820", "#73202a"
    elif kind == "green":
        top, bot, rim, hi, tc = "#2f9d5f", "#1e6e41", "#4fd88a", "#a5f0c6", "#ffffff"
    else:
        top, bot, rim, hi, tc = "#1e2e48", "#152238", "#3a5274", "#5d7aa3", PAL["row"]
        if state == "hover":
            top, bot, rim = "#253858", "#1a2a44", mix(A["base"], "#3a5274", 0.45)
        if state == "pressed":
            top, bot = "#0f1828", "#152238"
    if state == "disabled":
        top, bot, rim, hi, tc = "#161e2c", "#121a27", "#263246", "#263246", "#66758a"
    if state == "hover":
        glow(im, box, rim, 5, 110, c, 2)
    grad_fill(im, box, top, bot, c=c)
    outline(im, box, PAL["edge"], c=c)
    outline(im, (x0 + 1, y0 + 1, x1 - 1, y1 - 1), rim, c=c - 1)
    if state != "pressed" and state != "disabled":
        hline(im, x0 + c + 1, x1 - c - 1, y0 + 2, hi, 150)
    else:
        hline(im, x0 + c + 1, x1 - c - 1, y0 + 2, "#000000", 90)
    dy = 1 if state == "pressed" else 0
    f = font("head", fsize)
    cy = (y0 + y1) // 2 + 1 + dy
    if glyph is not None:
        gw = glyph.size[0]
        total = gw + 6 + (tw(label, f) if label else -6)
        gx = (x0 + x1) // 2 - total // 2
        put(im, glyph, gx, cy - glyph.size[1] // 2)
        if label:
            text(im, (gx + gw + 6, cy), label, f, tc, "lm")
    else:
        text(im, ((x0 + x1) // 2, cy), label, f, tc, "mm")


def slot(im, x, y, state="empty", rarity=None, icon_rel=None, count=None, size=74, keycap=None, ghost=None, dim=False):
    """One item cell (74 x 74 = the engine grid pitch). rarity = a colour -> rarity frame + corner gem."""
    x1, y1 = x + size - 1, y + size - 1
    c = 4
    if state == "selected":
        glow(im, (x, y, x1, y1), A["base"], 5, 200, c, 2)
    frame = "#26354f"
    if rarity:
        frame = mix(rarity, "#0c1422", 0.38)
    if state == "hover":
        frame = "#5a7299" if not rarity else mix(rarity, "#ffffff", 0.25)
    if state == "selected":
        frame = A["base"]
    top, bot = ("#16233a", "#0c1424") if state != "hover" else ("#1d2d49", "#111c30")
    if rarity:
        top = mix(rarity, "#16233a", 0.9)
    grad_fill(im, (x, y, x1, y1), top, bot, c=c)
    # inner rarity glow (fades in from the frame)
    if rarity:
        d = ImageDraw.Draw(im, "RGBA")
        for i in range(7):
            d.polygon(cham(x + 3 + i, y + 3 + i, x1 - 3 - i, y1 - 3 - i, max(0, c - 3)),
                      outline=rgb(rarity, int(55 * (1 - i / 7) ** 1.6)))
    outline(im, (x, y, x1, y1), PAL["edge"], c=c)
    outline(im, (x + 1, y + 1, x1 - 1, y1 - 1), frame, c=c - 1, width=2)
    hline(im, x + c + 2, x1 - c - 2, y + 3, "#ffffff", 26)
    if state == "selected":
        d = ImageDraw.Draw(im, "RGBA")
        L = 12
        for cx, cy, sx, sy in ((x - 2, y - 2, 1, 1), (x1 + 2, y - 2, -1, 1), (x - 2, y1 + 2, 1, -1), (x1 + 2, y1 + 2, -1, -1)):
            d.line([(cx, cy), (cx + sx * L, cy)], fill=rgb(A["hi"]), width=2)
            d.line([(cx, cy), (cx, cy + sy * L)], fill=rgb(A["hi"]), width=2)
    if rarity:
        put(im, g_diamond(11, rarity), x1 - 13, y + 3)
    if ghost is not None and not icon_rel:
        put(im, ghost, x + (size - ghost.size[0]) // 2, y + (size - ghost.size[1]) // 2)
    if icon_rel:
        isz = 64 if size >= 74 else (48 if size >= 56 else 32)
        paste_icon(im, icon_rel, x + (size - isz) // 2, y + (size - isz) // 2, isz, 0.45 if dim else 1.0)
    if count:
        f = font("headb", 16)
        text(im, (x1 - 5, y1 - 3), str(count), f, "#ffffff", "rs")
    if keycap:
        key_cap(im, x + 4, y + 4, keycap, small=True)


def key_cap(im, x, y, label, small=False, f=None):
    f = f or font("headb", 13 if small else 14)
    w = max(18 if small else 22, tw(label, f) + 10)
    h = 18 if small else 22
    grad_fill(im, (x, y, x + w - 1, y + h - 1), "#2a3a56", "#1a2640", c=3)
    outline(im, (x, y, x + w - 1, y + h - 1), "#4a6086", c=3)
    hline(im, x + 3, x + w - 4, y + h - 2, "#0a101c", 255)
    hline(im, x + 3, x + w - 4, y + 1, "#ffffff", 40)
    text(im, (x + w // 2, y + h // 2), label, f, "#e6eef8", "mm", shadow=False)
    return w


def hotbar_marker(im, x, y, size=74):
    """Active hotbar slot: accent frame (drawn by slot(selected)) + a notch tab under the slot."""
    d = ImageDraw.Draw(im, "RGBA")
    cx = x + size // 2
    yb = y + size + 1
    d.polygon([(cx - 14, yb + 1), (cx + 14, yb + 1), (cx + 9, yb + 6), (cx - 9, yb + 6)], fill=rgb(A["base"]))
    d.line([(cx - 13, yb + 1), (cx + 13, yb + 1)], fill=rgb(A["hi"]))


def toggle(im, x, y, on=True, label=None, w=44, h=24):
    def f(d, s):
        W, H = w * s, h * s
        tr = rgb(A["btnTop"]) if on else rgb("#18233a")
        d.rounded_rectangle((0, 0, W - 1, H - 1), radius=H / 2, fill=rgb("#04070d"))
        d.rounded_rectangle((s, s, W - 1 - s, H - 1 - s), radius=H / 2 - s, fill=rgb(A["base"] if on else "#3a4a63"))
        d.rounded_rectangle((2 * s, 2 * s, W - 1 - 2 * s, H - 1 - 2 * s), radius=H / 2 - 2 * s, fill=tr)
        k = H - 6 * s
        kx = W - 3 * s - k if on else 3 * s
        d.ellipse((kx, 3 * s, kx + k, 3 * s + k), fill=rgb("#ffffff" if on else "#8796ab"))
    put(im, ss_glyph(w, h, f), x, y)
    if label:
        text(im, (x + w + 10, y + h // 2), label, font("bodyb", 15), PAL["row"] if on else PAL["dim"], "lm")


def search_box(im, box, placeholder="Search...", focused=False, value=None, icon_on=True):
    x0, y0, x1, y1 = box
    panel(im, box, inset=True, c=4)
    outline(im, box, A["base"] if focused else "#2a3a55", c=4)
    if focused:
        glow(im, box, A["base"], 4, 90, 4, 2)
    cy = (y0 + y1) // 2
    tx0 = x0 + 34 if icon_on else x0 + 10
    if icon_on:
        put(im, g_search(16, "#8ea3bd"), x0 + 10, cy - 8)
    if value:
        text(im, (tx0, cy), value, font("body", 15), "#ffffff", "lm")
        cx = tx0 + tw(value, font("body", 15)) + 2
        ImageDraw.Draw(im).line([(cx, cy - 9), (cx, cy + 8)], fill=rgb(A["hi"]), width=2)
    else:
        text(im, (x0 + 34, cy), placeholder, font("body", 15), PAL["placeholder"], "lm", shadow=False)


def scrollbar(im, x, y0, y1, t0, t1, hover=False):
    panel(im, (x, y0, x + 7, y1), inset=True, c=2)
    grad_fill(im, (x + 1, t0, x + 6, t1), A["hi"] if hover else "#5a7299", A["base"] if hover else "#3a5274", c=2)


def bar(im, box, frac, kind="xp", label=None, label_right=None, segs=0):
    x0, y0, x1, y1 = box
    cols = {"xp": ("#f4d77c", "#c99a2e"), "health": ("#f0646a", "#b02c35"), "mana": ("#78aaff", "#2f62d0"),
            "stamina": ("#ffe07a", "#d29b1a"), "accent": (A["hi"], A["lo"]), "green": ("#7cf0ad", "#2a9a5c"),
            "defense": ("#c5d2e2", "#6c7d95")}[kind]
    panel(im, box, inset=True, c=2)
    fx = x0 + 1 + int((x1 - x0 - 2) * frac)
    if fx > x0 + 2:
        grad_fill(im, (x0 + 1, y0 + 1, fx, y1 - 1), cols[0], cols[1], c=1)
        hline(im, x0 + 2, fx - 1, y0 + 2, "#ffffff", 90)
    if segs:
        d = ImageDraw.Draw(im, "RGBA")
        for i in range(1, segs):
            sx = x0 + (x1 - x0) * i // segs
            d.line([(sx, y0 + 2), (sx, y1 - 2)], fill=(0, 0, 0, 90))
    if label:
        text(im, (x0, y0 - 9), label, font("bodyb", 14), PAL["text"], "ls")
    if label_right:
        text(im, (x1, y0 - 9), label_right, font("bodyb", 14), PAL["xp"] if kind == "xp" else PAL["text"], "rs")


def level_pill(im, x, y, label, col=None):
    col = col or PAL["xp"]
    f = font("headb", 14)
    w = tw(label, f) + 18
    h = 22
    grad_fill(im, (x, y, x + w - 1, y + h - 1), "#2b2212", "#1a140a", c=6)
    outline(im, (x, y, x + w - 1, y + h - 1), PAL["edge"], c=6)
    outline(im, (x + 1, y + 1, x + w - 2, y + h - 2), PAL["gold"], c=5)
    text(im, (x + w // 2, y + h // 2), label, f, PAL["goldHi"], "mm")
    return w


def chip(im, x, y, label, selected=False, h=32, icon_rel=None, fsize=15):
    f = font("head", fsize)
    w = tw(label, f) + 24 + (26 if icon_rel else 0)
    box = (x, y, x + w - 1, y + h - 1)
    if selected:
        grad_fill(im, box, mix(A["base"], "#111b2d", 0.62), mix(A["base"], "#111b2d", 0.78), c=4)
        outline(im, box, A["base"], c=4)
        hline(im, x + 4, x + w - 5, y + 1, A["hi"], 160)
        col = "#ffffff"
    else:
        grad_fill(im, box, "#18253c", "#121c2f", c=4)
        outline(im, box, "#2b3d5b", c=4)
        col = "#a9bad0"
    tx = x + 12
    if icon_rel:
        paste_icon(im, icon_rel, tx - 2, y + h // 2 - 12, 24, 1.0 if selected else 0.75)
        tx += 26
    text(im, (tx, y + h // 2 + 1), label, f, col, "lm")
    return w


def row(im, box, state="normal"):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(im, "RGBA")
    if state == "normal":
        grad_fill(im, box, "#141f33", "#111a2b", c=3)
        outline(im, box, "#1e2c44", c=3)
    elif state == "hover":
        grad_fill(im, box, "#1a2840", "#152136", c=3)
        outline(im, box, "#33496b", c=3)
    else:
        grad_fill(im, box, mix(A["base"], "#141f33", 0.8), mix(A["base"], "#111a2b", 0.88), c=3)
        outline(im, box, mix(A["base"], "#33496b", 0.4), c=3)
        d.rectangle((x0 + 1, y0 + 3, x0 + 3, y1 - 3), fill=rgb(A["base"]))


def tooltip(im, x, y, w=372):
    """The sectioned tooltip (Style Guide 15 colours; header order from docs/answered/ui.md 2026-10-24)."""
    rc = RAR["Legendary"]
    fN, fB, fS, fH = font("headb", 20), font("body", 15), font("bodyb", 15), font("head", 13)
    lines = []  # (kind, payload)
    y0 = y
    h = 470
    x1, y1 = x + w - 1, y + h - 1
    shadow(im, (x, y, x1, y1), 10, 200, 4)
    grad_fill(im, (x, y, x1, y1), "#0e1729", "#0a111e", c=6)
    outline(im, (x, y, x1, y1), PAL["edge"], c=6)
    outline(im, (x + 1, y + 1, x1 - 1, y1 - 1), mix(rc, "#0c1422", 0.35), c=5)
    d = ImageDraw.Draw(im, "RGBA")
    for i in range(10):
        d.line([(x + 6, y + 2 + i), (x1 - 6, y + 2 + i)], fill=rgb(rc, int(40 * (1 - i / 10))))
    put(im, g_diamond(11, rc), x + 6, y + 6)
    put(im, g_diamond(11, rc), x1 - 16, y + 6)
    cy = y + 26
    text(im, (x + w // 2, cy), "Skyreach Longbow", fN, rc, "mm")
    cy += 26
    # header block: slot, tier, class, type, speed, rarity, level
    def kv(k, v, vc=PAL["row"]):
        nonlocal cy
        text(im, (x + 18, cy), k, fB, PAL["dim"], "lm")
        text(im, (x + 150, cy), v, fS, vc, "lm")
        cy += 21
    kv("Slot", "Weapon (main hand)")
    kv("Tier", "T5 Adamantite", "#e0675a")
    kv("Class", "Archer")
    kv("Speed", "Fast")
    kv("Rarity", "Legendary", rc)
    kv("Level", "Combat Lv 30 (24-30)", PAL["xp"])
    cy += 4
    taper_line(im, x + 14, x1 - 14, cy, PAL["gold"], 170, 0.6)
    cy += 14
    text(im, (x + 18, cy), "STATS", fH, PAL["dim"], "lm", track=1.5)
    cy += 21
    for nm, val, good in (("Damage", "+38", True), ("Crit Chance", "+12%", True), ("Dexterity", "+6", True),
                          ("Defense", "-4", False)):
        text(im, (x + 18, cy), val, font("bold", 15), PAL["green"] if good else PAL["red"], "lm")
        text(im, (x + 70, cy), nm, fB, PAL["row"], "lm")
        cy += 21
    cy += 4
    taper_line(im, x + 14, x1 - 14, cy, PAL["gold"], 170, 0.6)
    cy += 14
    text(im, (x + 18, cy), "ABILITY", fH, PAL["dim"], "lm", track=1.5)
    text(im, (x1 - 18, cy), "Right-click", fH, PAL["action"], "rm")
    cy += 21
    text(im, (x + 18, cy), "Gale Shot", font("bold", 15), PAL["xp"], "lm")
    text(im, (x1 - 18, cy), "25 Mana", fS, "#78aaff", "rm")
    cy += 20
    text(im, (x + 18, cy), "A piercing arrow that rides the wind.", fB, "#aebfd3", "lm")
    cy += 24
    taper_line(im, x + 14, x1 - 14, cy, PAL["gold"], 170, 0.6)
    cy += 14
    text(im, (x + 18, cy), "Archer", fS, PAL["green"], "lm")
    text(im, (x + 90, cy), "Combat Lv 30  (you: 27)", fS, PAL["red"], "lm")
    cy += 22
    text(im, (x + 18, cy), "Reforgeable  -  T5 Adamantite bow", fB, PAL["dim"], "lm")
    cy += 21
    text(im, (x + 18, cy), "Click: equip    Shift-click: move", fS, PAL["action"], "lm")
    return h


# ----------------------------------------------------------------------------------------------------------------- the 12 tabs + data
TABS = [("Inventory", I_HUB % "hubrow_character"), ("Skills", I_HUB % "character_skills"),
        ("Class", I_HUB % "character_class"), ("Pets", I_HUB % "character_pets"),
        ("Collections", I_HUB % "character_collections"), ("Storage", I_HUB % "hubrow_storage"),
        ("Crafting", I_HUB % "hubrow_smithing"), ("Market", I_HUB % "hubrow_market"),
        ("Quests", I_HUB % "world_quests"), ("World", I_HUB % "hubrow_world"),
        ("Social", I_HUB % "hubrow_social"), ("Settings", I_HUB % "hubrow_settings")]

SKILLS = [("Mining", I_WARP % "Mining", 31), ("Foraging", I_WARP % "Foraging", 27), ("Farming", I_WARP % "Farming", 24),
          ("Fishing", I_WARP % "Fishing", 19), ("Combat", I_WARP % "Combat", 27), ("Smithing", I_NODE % "Smithing_B1R1a", 15),
          ("Cooking", I_NODE % "Cooking_B1R1a", 12), ("Alchemy", I_NODE % "Alchemy_B1R1a", 9),
          ("Acrobatics", I_NODE % "Acrobatics_B1R1a", 14), ("Exploration", I_NODE % "Exploration_B1R1a", 18),
          ("Beastmastery", I_NODE % "Beastmastery_B1R1a", 11)]


def bg_world(W, H, dim=165):
    """A dimmed sky behind the window (stands in for the game world)."""
    im = Image.new("RGB", (W, H))
    g = Image.linear_gradient("L").resize((W, H))
    im.paste(Image.composite(Image.new("RGB", (W, H), rgb("#e9b98a")[:3]), Image.new("RGB", (W, H), rgb("#3e6fae")[:3]), g))
    d = ImageDraw.Draw(im, "RGBA")
    for i, (cx, cy, r) in enumerate(((300, 700, 260), (1500, 640, 320), (900, 820, 200))):
        d.ellipse((cx - r, cy - r // 5, cx + r, cy + r // 5), fill=(255, 255, 255, 60))
        d.polygon([(cx - r // 2, cy), (cx + r // 2, cy), (cx + r // 6, cy + r // 2), (cx - r // 5, cy + r // 2)],
                  fill=(40, 52, 70, 200))
        d.rectangle((cx - r // 2, cy - 12, cx + r // 2, cy + 2), fill=(70, 120, 70, 220))
    d.rectangle((0, 0, W, H), fill=(4, 7, 13, dim))
    return im


# ----------------------------------------------------------------------------------------------------------------- inventory mockup

def make_mockup_v1():
    set_accent("Sky Azure")
    W, H = 1920, 1080
    im = bg_world(W, H)
    WX0, WY0, WX1, WY1 = 16, 12, 1903, 1067
    window_frame(im, (WX0, WY0, WX1, WY1))

    # ---- top tab bar
    TB0, TB1 = WY0 + 8, WY0 + 62
    grad_fill(im, (WX0 + 5, TB0, WX1 - 5, TB1), "#0a111e", "#0c1525", c=4)
    hline(im, WX0 + 6, WX1 - 6, TB1, PAL["lineHi"])
    taper_line(im, WX0 + 20, WX1 - 20, TB1 + 1, PAL["gold"], 120, 0.8)
    tx = WX0 + 18
    tabw = 117
    for i, (nm, ic) in enumerate(TABS):
        st = "selected" if i == 0 else "normal"
        tab(im, (tx, TB0 + 4, tx + tabw - 1, TB1 - 1), nm, ic, st)
        tx += tabw + 1
    # coins / bank / mail / close
    rx = WX1 - 20
    button(im, (rx - 40, TB0 + 9, rx, TB0 + 49), "", "secondary", glyph=g_x(18, "#d6e4ee"))
    rx -= 54
    mail_x = rx - 40
    button(im, (mail_x, TB0 + 9, rx, TB0 + 49), "", "secondary", glyph=g_envelope(20, "#c2d1e2"))
    put(im, ss_glyph(18, 18, lambda d, s: d.ellipse((0, 0, 18 * s - 1, 18 * s - 1), fill=rgb(PAL["red"]))), rx - 12, TB0 + 3)
    text(im, (rx - 3, TB0 + 12), "2", font("headb", 13), "#ffffff", "mm", shadow=False)
    rx = mail_x - 14
    fv, fk = font("headb", 17), font("head", 13)
    # bank
    bw = 120
    panel(im, (rx - bw, TB0 + 9, rx, TB0 + 49), inset=True, c=4)
    paste_icon(im, I_HUB % "storage_bank", rx - bw + 8, TB0 + 17, 24)
    text(im, (rx - bw + 40, TB0 + 21), "BANK", fk, PAL["dim"], "lm", track=1)
    text(im, (rx - bw + 40, TB0 + 38), "3.2M", fv, "#e9eef7", "lm")
    rx -= bw + 8
    cw = 148
    panel(im, (rx - cw, TB0 + 9, rx, TB0 + 49), inset=True, c=4)
    put(im, g_coin(22), rx - cw + 9, TB0 + 18)
    text(im, (rx - cw + 40, TB0 + 21), "COINS", fk, PAL["dim"], "lm", track=1)
    text(im, (rx - cw + 40, TB0 + 38), "1,245,210", fv, "#ffd76a", "lm")

    CY0, CY1 = 86, 1020
    LX0, LX1 = 32, 452
    MX0, MX1 = 468, 1188
    RX0, RX1 = 1204, 1887

    # ================= LEFT: character
    panel(im, (LX0, CY0, LX1, CY1), "Character")
    text(im, (LX1 - 14, CY0 + 18), "Islander", font("bodyb", 15), PAL["text"], "rm")
    # equipment
    ey = CY0 + 44
    lab = font("head", 13)
    left = [("Head", I_ARM % "Foraging_Maple_Head", "Rare"), ("Chest", I_ARM % "Foraging_Maple_Chest", "Rare"),
            ("Hands", I_ARM % "Foraging_Maple_Hands", "Unique"), ("Legs", I_ARM % "Foraging_Maple_Legs", "Unique")]
    for i, (nm, ic, r) in enumerate(left):
        slot(im, LX0 + 14, ey + i * 76, "empty", RAR[r], ic)
    right = [("Off-hand", None), ("Utility", I_GEAR % "reel-t3-thorium"), ("Utility", None), ("Tool", I_GEAR % "rod-t3-thorium")]
    ghosts = {"Off-hand": g_shield(30, "#2c3c57"), "Utility": g_diamond(24, "#2c3c57", "#36486a", "#1a2538"),
              "Tool": g_sword(30, "#2c3c57")}
    for i, (nm, ic) in enumerate(right):
        slot(im, LX1 - 14 - 74, ey + i * 76, "empty", RAR["Normal"] if ic else None, ic, ghost=ghosts[nm])
    # preview
    px0, px1 = LX0 + 100, LX1 - 100
    py0, py1 = ey, ey + 4 * 76 - 2
    panel(im, (px0, py0, px1, py1), inset=True, c=5)
    d = ImageDraw.Draw(im, "RGBA")
    pcx = (px0 + px1) // 2
    glow_l = Image.new("RGBA", (px1 - px0, py1 - py0), (0, 0, 0, 0))
    ImageDraw.Draw(glow_l).ellipse((30, py1 - py0 - 70, px1 - px0 - 30, py1 - py0 - 20), fill=rgb(A["base"], 110))
    glow_l = glow_l.filter(ImageFilter.GaussianBlur(12))
    reg = im.crop((px0, py0, px1, py1)).convert("RGBA")
    im.paste(Image.alpha_composite(reg, glow_l).convert("RGB"), (px0, py0))
    # blocky stand-in figure (original placeholder, not a game model)
    fig = [((-22, -150), (22, -108), "#d9a87e"), ((-26, -106), (26, -40), "#3a6b45"), ((-40, -104), (-28, -46), "#d9a87e"),
           ((28, -104), (40, -46), "#d9a87e"), ((-24, -40), (-2, 8), "#4a3a2a"), ((2, -40), (24, 8), "#4a3a2a"),
           ((-26, -154), (26, -136), "#5a3b22"), ((-26, -64), (26, -56), "#7a5a2a")]
    base_y = py1 - 46
    for (ax, ay), (bx, by), col in fig:
        d.rectangle((pcx + ax, base_y + ay, pcx + bx, base_y + by), fill=rgb(col), outline=rgb("#05080e"))
    d.rectangle((pcx - 12, base_y - 132, pcx - 6, base_y - 126), fill=rgb("#1a1a2a"))
    d.rectangle((pcx + 6, base_y - 132, pcx + 12, base_y - 126), fill=rgb("#1a1a2a"))
    text(im, (pcx, py0 + 18), "Player preview", font("body", 13), PAL["dim"], "mm", shadow=False)
    # labels under the slot columns
    # Void Charms
    vy = ey + 4 * 76 + 18
    text(im, (LX0 + 14, vy + 10), "VOID CHARMS", font("head", 14), PAL["text"], "lm", track=1.2)
    text(im, (LX0 + 132, vy + 10), "9 / 18", font("bodyb", 14), PAL["dim"], "lm")
    text(im, (LX1 - 30, vy + 10), "All charms", font("head", 14), A["hi"], "rm")
    put(im, g_chev(13, A["hi"]), LX1 - 28, vy + 4)
    charms = [("mana-rare", "Rare"), ("health-unique", "Unique"), ("speed-legendary", "Legendary"),
              ("stamina-normal", "Normal"), ("lantern-unique", "Unique")]
    for i, (ic, r) in enumerate(charms):
        slot(im, LX0 + 14 + i * 79, vy + 24, "empty", RAR[r], I_ACC % ic)
    # pet + mount
    py = vy + 24 + 74 + 18
    half = (LX1 - LX0 - 28 - 10) // 2
    for i, (cap, ic, nm, lv, r) in enumerate((("PET", I_PET % "Hawk", "Hawk", "Lv 42", "Legendary"),
                                                ("MOUNT", I_PET % "Horse", "Horse", "Lv 18", "Rare"))):
        bx = LX0 + 14 + i * (half + 10)
        panel(im, (bx, py, bx + half, py + 84), inset=True, c=4)
        slot(im, bx + 5, py + 5, "empty", RAR[r], ic)
        text(im, (bx + 88, py + 18), cap, font("head", 13), PAL["dim"], "lm", track=1.2)
        text(im, (bx + 88, py + 40), nm, font("bodyb", 16), RAR[r], "lm")
        text(im, (bx + 88, py + 62), lv + "  " + r, font("body", 13), PAL["text"], "lm")
    # class card
    cy = py + 102
    panel(im, (LX0 + 14, cy, LX1 - 14, cy + 84), inset=True, c=4)
    paste_icon(im, I_EMB % "Archer", LX0 + 22, cy + 10, 64)
    text(im, (LX0 + 98, cy + 22), "Archer", font("headb", 20), "#a8e07a", "lm")
    level_pill(im, LX0 + 98 + tw("Archer", font("headb", 20)) + 10, cy + 11, "Lv 23")
    bar(im, (LX0 + 98, cy + 60, LX1 - 26, cy + 70), 0.62, "xp", "Class XP", "1,240 / 2,000")
    # vitals
    vy2 = cy + 102
    vit = [("Health", g_heart(20, PAL["health"]), "412 / 412", "health", 1.0),
           ("Mana", g_drop(20, PAL["mana"]), "96 / 140", "mana", 0.69),
           ("Stamina", g_bolt(20, PAL["stamina"]), "100 / 100", "stamina", 1.0),
           ("Defense", g_shield(20, PAL["defense"]), "184", "defense", 0.46)]
    for i, (nm, g, val, k, fr) in enumerate(vit):
        bx = LX0 + 14 + (i % 2) * (half + 10)
        by = vy2 + (i // 2) * 60
        panel(im, (bx, by, bx + half, by + 50), inset=True, c=4)
        put(im, g, bx + 10, by + 8)
        text(im, (bx + 38, by + 18), nm, font("bodyb", 15), PAL["text"], "lm")
        text(im, (bx + half - 10, by + 18), val, font("headb", 16), "#ffffff", "rm")
        bar(im, (bx + 10, by + 36, bx + half - 10, by + 42), fr, k)
    # combat line + button
    sy = vy2 + 2 * 60 + 4
    panel(im, (LX0 + 14, sy, LX1 - 14, sy + 34), inset=True, c=4)
    x = LX0 + 26
    for k, v in (("Strength", "34"), ("Crit", "12%"), ("Speed", "+8%")):
        x = rich(im, x, sy + 17, [(k + " ", font("body", 14), PAL["dim"]), (v, font("headb", 15), PAL["green"])]) + 18
    button(im, (LX0 + 14, CY1 - 56, LX1 - 14, CY1 - 14), "Stats by source", "secondary")

    # ================= CENTRE TOP: inventory crafting
    CRY1 = 452
    panel(im, (MX0, CY0, MX1, CRY1), "Crafting")
    text(im, (MX1 - 14, CY0 + 18), "Processing: Crafting tab", font("body", 13), PAL["dim"], "rm")
    x = MX0 + 14
    pages = [("All", None), ("Hand", None), ("Workbench", None), ("Armor", None), ("Weapon", None), ("Alchemy", None),
             ("Arcane", None), ("Farming", None)]
    for i, (nm, ic) in enumerate(pages):
        x += chip(im, x, CY0 + 38, nm, i == 0, h=30, fsize=15) + 5
    # toggle + search
    ty = CY0 + 78
    toggle(im, MX0 + 14, ty + 4, True, "Craftable only")
    search_box(im, (MX0 + 210, ty, MX1 - 120, ty + 31), "Search recipes...")
    text(im, (MX1 - 14, ty + 16), "24 recipes", font("bodyb", 14), PAL["dim"], "rm")
    # recipe grid 5 x 3 (scrolls)
    gy = ty + 42
    gx = MX0 + 14
    recipes = [(I_ACC % "mana-rare", "Rare"), (I_ACC % "health-unique", "Unique"), (I_ACC % "speed-normal", "Normal"),
               (I_ACC % "stamina-rare", "Rare"), (I_ACC % "lantern-unique", "Unique"),
               (I_GEAR % "rod-t2-iron", "Normal"), (I_GEAR % "rod-t3-thorium", "Normal"), (I_GEAR % "reel-t2-iron", "Normal"),
               (I_GEAR % "barbed-hook-II", "Normal"), (I_ACC % "regeneration-normal", "Normal"),
               (I_ENCH % "iron-ingot", None), (I_ENCH % "copper-ingot", None), (I_ENCH % "oak-log", None),
               (I_ENCH % "wheat", None), (I_ENCH % "cobblestone", None)]
    for i, (ic, r) in enumerate(recipes):
        st = "selected" if i == 0 else ("hover" if i == 7 else "empty")
        slot(im, gx + (i % 5) * 74, gy + (i // 5) * 74, st, RAR.get(r), ic)
    scrollbar(im, gx + 5 * 74 + 6, gy, gy + 3 * 74 - 1, gy + 2, gy + 120)
    # detail
    dx0, dx1 = gx + 5 * 74 + 24, MX1 - 14
    dy0, dy1 = gy, CRY1 - 12
    panel(im, (dx0, dy0, dx1, dy1), inset=True, c=5)
    slot(im, dx0 + 10, dy0 + 10, "empty", RAR["Rare"], I_ACC % "mana-rare", size=74)
    text(im, (dx0 + 96, dy0 + 22), "Mana Charm", font("headb", 19), RAR["Rare"], "lm")
    text(im, (dx0 + 96, dy0 + 44), "Charm  -  Rare", font("bodyb", 14), PAL["text"], "lm")
    rich(im, dx0 + 96, dy0 + 64, [("+12 ", font("bold", 14), PAL["green"]), ("Max Mana  ", font("body", 14), PAL["row"]),
                                  ("+4% ", font("bold", 14), PAL["green"]), ("Regen", font("body", 14), PAL["row"])])
    iy = dy0 + 88
    ins = [(I_ACC % "mana-unique", "Mana Charm (Unique)", 1, 1), (I_ENCH % "cobalt-ingot", "Enchanted Cobalt Ingot", 7, 4),
           (I_ENCH % "sap", "Enchanted Sap", 9, 8)]
    for ic, nm, have, need in ins:
        paste_icon(im, ic, dx0 + 14, iy + 1, 24)
        text(im, (dx0 + 46, iy + 13), nm, font("body", 15), PAL["row"], "lm")
        ok = have >= need
        text(im, (dx1 - 12, iy + 13), "%d / %d" % (have, need), font("headb", 16), PAL["green"] if ok else PAL["red"], "rm")
        iy += 26
    # status + buttons
    by = dy1 - 42
    sx0 = dx0 + 10
    d = ImageDraw.Draw(im, "RGBA")
    put(im, g_check(14, PAL["green"]), sx0, by - 21)
    text(im, (sx0 + 20, by - 14), "Ready - you can craft 1", font("bodyb", 14), PAL["green"], "lm")
    text(im, (dx1 - 12, by - 14), "+40 Alchemy XP", font("body", 13), PAL["xp"], "rm")
    bw3 = (dx1 - dx0 - 20 - 12) // 3
    button(im, (sx0, by, sx0 + bw3 + 20, by + 34), "Craft", "primary")
    button(im, (sx0 + bw3 + 26, by, sx0 + 2 * bw3 + 16, by + 34), "x10", "secondary", "disabled")
    button(im, (sx0 + 2 * bw3 + 22, by, dx1 - 10, by + 34), "All", "secondary")

    # ================= CENTRE BOTTOM: inventory + bags + hotbar + teleports
    IY0 = CRY1 + 12
    panel(im, (MX0, IY0, MX1, CY1))
    bags = [("Inventory", I_HUB % "hubrow_storage"), ("Mining", I_WARP % "Mining"), ("Foraging", I_WARP % "Foraging"),
            ("Farming", I_WARP % "Farming"), ("Fishing", I_WARP % "Fishing"), ("Combat", I_WARP % "Combat"),
            ("Smithing", I_NODE % "Smithing_B1R1a")]
    bx = MX0 + 8
    bwid = (MX1 - MX0 - 16) // 7
    for i, (nm, ic) in enumerate(bags):
        st = "selected" if i == 0 else "normal"
        tab(im, (bx + i * bwid, IY0 + 6, bx + (i + 1) * bwid - 2, IY0 + 42), nm, ic, st, fsize=15)
    hline(im, MX0 + 6, MX1 - 6, IY0 + 42, PAL["lineHi"])
    gx = MX0 + (MX1 - MX0 - 666) // 2
    gy = IY0 + 52
    inv = {0: (I_ENCH % "iron-ingot", 64, None), 1: (I_ENCH % "copper-ingot", 23, None),
           2: (I_ENCH % "oak-log", 41, None), 3: (I_ENCH % "maple-log", 12, None), 4: (I_FISH % "frost_cod", 6, "Normal"),
           5: (I_FISH % "cinderfin", 2, "Rare"), 6: (I_EGG % "Combat_Rare", 1, None), 8: (I_ARM % "Foraging_Oak_Chest", None, "Normal"),
           9: (I_ENCH % "wheat", 128, None), 10: (I_ENCH % "carrot", 37, None), 11: (I_ENCH % "potato", 9, None),
           13: (I_GEAR % "rod-t2-iron", None, "Normal"), 14: (I_FISH % "glass_pike", 3, "Unique"), 15: (I_ACC % "feather-normal", None, "Normal"),
           18: (I_ENCH % "cobblestone", 256, None), 19: (I_ENCH % "sand", 64, None), 20: (I_ENCH % "clay", 18, None),
           22: (I_GEAR % "lure-hook-I", 4, "Normal"), 23: (I_EGG % "Mining_Uncommon", 1, None), 26: (I_FISH % "magma_marlin", 1, "Legendary"),
           27: (I_ENCH % "sap", 5, None), 28: (I_ENCH % "fibre", 74, None), 31: (I_ARM % "Foraging_Oak_Legs", None, "Normal")}
    for i in range(36):
        it = inv.get(i)
        st = "hover" if i == 12 else "empty"
        if it:
            ic, n, r = it
            slot(im, gx + (i % 9) * 74, gy + (i // 9) * 74, st, RAR[r] if r else None, ic, n)
        else:
            slot(im, gx + (i % 9) * 74, gy + (i // 9) * 74, st)
    # hotbar
    hy = gy + 4 * 74 + 14
    text(im, (gx - 8, hy - 7), "", font("body", 13), PAL["dim"])
    hot = [(I_GEAR % "rod-t3-thorium", None, "Normal"), (I_ABIL % "Archer_ArrowRain", None, None),
           (I_ABIL % "Archer_RapidFire", None, None), (I_ABIL % "Archer_HuntersNet", None, None),
           (I_ENCH % "iron-ingot", 12, None), None, (I_FISH % "frost_cod", 6, "Normal"), None, (I_ACC % "lantern-unique", None, "Unique")]
    panel(im, (gx - 6, hy - 6, gx + 666 + 5, hy + 74 + 9), inset=True, c=5)
    for i in range(9):
        it = hot[i]
        st = "selected" if i == 0 else "empty"
        if it:
            slot(im, gx + i * 74, hy, st, RAR[it[2]] if it[2] else None, it[0], it[1], keycap=str(i + 1))
        else:
            slot(im, gx + i * 74, hy, st, keycap=str(i + 1))
    hotbar_marker(im, gx, hy)
    # teleports under the hotbar
    ty = hy + 74 + 20
    text(im, (gx, ty + 20), "TELEPORT", font("head", 14), PAL["dim"], "lm", track=1.2)
    tx = gx + 96
    tps = [("Island", I_HUB % "world_island"), ("Hub", I_HUB % "hubrow_home")]
    for nm, ic in tps:
        w = 136
        button(im, (tx, ty, tx + w, ty + 40), "", "secondary")
        paste_icon(im, ic, tx + 14, ty + 8, 24)
        text(im, (tx + 46, ty + 21), nm, font("head", 16), PAL["row"], "lm")
        tx += w + 8
    button(im, (tx, ty, tx + 44, ty + 40), "", "secondary", glyph=g_plus(16, "#9fb3cc"))
    button(im, (gx + 666 - 104, ty, gx + 666, ty + 40), "Edit", "secondary", glyph=g_pencil(16, "#c2d1e2"))
    # footer line: space + sort
    fy = CY1 - 26
    text(im, (gx, fy), "27 / 36 slots used", font("bodyb", 14), PAL["dim"], "lm")
    bar(im, (gx + 150, fy - 4, gx + 330, fy + 4), 27 / 36, "accent")
    button(im, (gx + 666 - 104, fy - 16, gx + 666, fy + 16), "Sort", "secondary", fsize=15)
    button(im, (gx + 666 - 256, fy - 16, gx + 666 - 112, fy + 16), "Stash to Void", "secondary", fsize=15)

    # ================= RIGHT: skills + right now
    panel(im, (RX0, CY0, RX1, CRY1), "Skills", link="Open Skills")
    cols = 3
    cw = (RX1 - RX0 - 28 - 2 * 8) // cols
    ch = 70
    for i, (nm, ic, lv) in enumerate(SKILLS + [("Total level", None, sum(s[2] for s in SKILLS))]):
        cx = RX0 + 14 + (i % cols) * (cw + 8)
        cy = CY0 + 42 + (i // cols) * (ch + 8)
        hov = False
        row(im, (cx, cy, cx + cw - 1, cy + ch - 1), "hover" if hov else "normal")
        if ic:
            panel(im, (cx + 8, cy + 9, cx + 59, cy + 60), inset=True, c=4)
            paste_icon(im, ic, cx + 10, cy + 11, 48)
            text(im, (cx + 70, cy + 22), nm, font("bodyb", 16), PAL["row"], "lm")
            level_pill(im, cx + cw - 10 - (tw("%d" % lv, font("headb", 14)) + 18), cy + 11, "%d" % lv)
            bar(im, (cx + 70, cy + 44, cx + cw - 12, cy + 52), ((lv * 37) % 100) / 100.0, "xp")
        else:
            put(im, g_diamond(40, PAL["gold"], PAL["goldHi"]), cx + 14, cy + 15)
            text(im, (cx + 70, cy + 22), "Total level", font("bodyb", 16), PAL["row"], "lm")
            text(im, (cx + 70, cy + 47), str(lv), font("headb", 22), PAL["xp"], "lm")
    # right now
    panel(im, (RX0, IY0, RX1, CY1), "Right now")
    rows = [(g_quest(26, PAL["action"]), "Quest:", "Visit the Farming island", PAL["action"], None),
            (I_WARP % "Foraging", "", "11 unspent points in Foraging", PAL["xp"], None),
            (I_WARP % "Mining", "", "5 unspent points in Mining", PAL["xp"], None),
            (I_EMB % "Archer", "", "2 unspent points in Archer tree", PAL["xp"], None),
            (I_WARP % "Fishing", "Daily:", "Catch 20 fish", PAL["action"], (12, 20)),
            (I_EGG % "Combat_Rare", "", "Rare Combat Egg is ready to hatch", PAL["green"], None),
            (I_ENCH % "iron-ingot", "Furnace:", "64 Iron Ingot ready to collect", PAL["green"], None),
            (I_HUB % "market_bazaar", "Bazaar:", "2 buy orders filled - claim", PAL["green"], None)]
    ry = IY0 + 42
    rh = 52
    for i, (ic, tag, msg, tc, prog) in enumerate(rows):
        st = "hover" if i == 1 else "normal"
        row(im, (RX0 + 14, ry, RX1 - 14, ry + rh - 1), st)
        if isinstance(ic, str):
            paste_icon(im, ic, RX0 + 24, ry + 10, 32)
        else:
            put(im, ic, RX0 + 27, ry + 13)
        x = RX0 + 68
        if tag:
            x = rich(im, x, ry + rh // 2, [(tag + " ", font("bodyb", 16), tc)])
        x = rich(im, x, ry + rh // 2, [(msg, font("body", 16), PAL["row"])])
        if prog:
            bar(im, (RX1 - 200, ry + 22, RX1 - 110, ry + 30), prog[0] / prog[1], "xp")
            text(im, (RX1 - 100, ry + rh // 2), "%d / %d" % prog, font("headb", 14), PAL["xp"], "lm")
        put(im, g_chev(18, A["hi"] if st == "hover" else "#7f93a6"), RX1 - 38, ry + rh // 2 - 9)
        ry += rh + 6
    text(im, (RX0 + 14 + (RX1 - RX0 - 28) // 2, CY1 - 22), "Click a row to go there", font("body", 14), PAL["dim"], "mm")

    # ================= key hints
    hy2 = 1044
    hints = [("LMB", "Take"), ("RMB", "Take one"), ("Shift", "Move"), ("1-9", "To hotbar"), ("Q", "Drop"),
             ("Ctrl", "Drop stack"), ("S", "Sort"), ("Tab / Esc", "Close")]
    fh = font("body", 15)
    total = 0
    for k, v in hints:
        total += max(22, tw(k, font("headb", 14)) + 10) + 6 + tw(v, fh) + 26
    x = (W - total) // 2
    for k, v in hints:
        w = key_cap(im, x, hy2 - 11, k)
        text(im, (x + w + 6, hy2), v, fh, "#aebfd3", "lm")
        x += w + 6 + tw(v, fh) + 26
    return im


# ----------------------------------------------------------------------------------------------------------------- inventory mockup v2
# v2 (Skyy 2026-11-14 review): labelled slot column + off-hand picker; inventory crafting in the VANILLA crafting layout (icon bench
# tabs over the panel, "Crafting > <bench>" title, search + Craftable only, recipe grid | ingredients | preview + Craft / x10 / All);
# the row between the top panel and the grid = [Craft][Mining]...[Smithing] (Craft = crafting, a pocket = that Void bag's contents);
# compact Skills + Right now. Real grids use the vanilla ItemGrid metrics: slot 74 + spacing 2 = 76 pitch.
P = 76          # ItemGrid pitch (InGame/Common.ui: DefaultItemSlotSize 74, DefaultItemSlotSpacing 2)
I_MENU = "art/menu-icons/Common/Icons/ItemsGenerated/Skyy_Menu_Icon_%s.png"

BENCHES = [("Default (hand + Workbench)", I_MENU % "Crafting"), ("Armor bench", I_HUB % "smithing_gear"),
           ("Weapon bench", I_HUB % "character_class"), ("Alchemy bench", I_NODE % "Alchemy_B1R1a"),
           ("Arcane bench", I_HUB % "character_accessories"), ("Farming bench", I_WARP % "Farming")]
POCKETS = [("Craft", I_MENU % "Crafting"), ("Mining", I_WARP % "Mining"), ("Foraging", I_WARP % "Foraging"),
           ("Farming", I_WARP % "Farming"), ("Fishing", I_WARP % "Fishing"), ("Combat", I_WARP % "Combat"),
           ("Smithing", I_NODE % "Smithing_B1R1a")]


def clipped(im, box, fn):
    """Draw fn(sub) on a copy of the box region and paste it back: content is cut at the box edge (a scrolling list)."""
    x0, y0, x1, y1 = box
    sub = im.crop((x0, y0, x1 + 1, y1 + 1))
    fn(sub)
    im.paste(sub, (x0, y0))


def caption(im, cx, y, s, col=None, f=None):
    text(im, (cx, y), s, f or font("bodyb", 13), col or PAL["dim"], "mt")


def bench_tab(im, x, y, w, h, icon_rel, selected):
    """Vanilla-style icon-only top tab sitting on the panel's top edge (vanilla 82 x 62, icon 44; ours 72 x 52, icon 36)."""
    if selected:
        grad_fill(im, (x, y, x + w - 1, y + h + 2), "#1c2d4a", PAL["panel2"], c=0)
        d = ImageDraw.Draw(im, "RGBA")
        d.line([(x, y + h + 2), (x, y + 4), (x + 4, y), (x + w - 5, y), (x + w - 1, y + 4), (x + w - 1, y + h + 2)],
               fill=rgb(PAL["lineHi"]))
        glow(im, (x + 4, y, x + w - 5, y + 2), A["base"], 5, 170, 0, 2)
        d.rectangle((x + 4, y, x + w - 5, y + 2), fill=rgb(A["base"]))
        paste_icon(im, icon_rel, x + (w - 36) // 2, y + (h - 36) // 2 + 2, 36)
    else:
        grad_fill(im, (x, y + 6, x + w - 1, y + h - 1), "#131e31", "#0e1727", c=4)
        outline(im, (x, y + 6, x + w - 1, y + h - 1), "#24344d", c=4)
        paste_icon(im, icon_rel, x + (w - 32) // 2, y + 6 + (h - 6 - 32) // 2, 32, 0.85, grey=True)


def hang_tabs(im, x0, y0, x1, h, items, sel, fsize=16):
    """The Craft / pocket row: tabs hanging from the top panel's bottom edge (the selected one is part of the panel)."""
    n = len(items)
    w = (x1 - x0 + 1 - (n - 1) * 3) // n
    d = ImageDraw.Draw(im, "RGBA")
    for i, (nm, ic) in enumerate(items):
        x = x0 + i * (w + 3)
        if i == sel:
            grad_fill(im, (x, y0 - 2, x + w - 1, y0 + h), PAL["panel"], "#16243c", c=0)
            d.line([(x, y0 - 1), (x, y0 + h - 5), (x + 4, y0 + h - 1), (x + w - 5, y0 + h - 1), (x + w - 1, y0 + h - 5),
                    (x + w - 1, y0 - 1)], fill=rgb(PAL["lineHi"]))
            glow(im, (x + 4, y0 + h - 3, x + w - 5, y0 + h - 1), A["base"], 5, 170, 0, 2)
            d.rectangle((x + 4, y0 + h - 3, x + w - 5, y0 + h - 1), fill=rgb(A["base"]))
            col, alpha, grey = PAL["title"], 1.0, False
        else:
            grad_fill(im, (x, y0 + 1, x + w - 1, y0 + h - 6), "#0e1727", "#131e31", c=4)
            outline(im, (x, y0 + 1, x + w - 1, y0 + h - 6), "#24344d", c=4)
            col, alpha, grey = "#9fb2c8", 0.75, True
        f = font("head", fsize)
        tot = 24 + 6 + tw(nm, f)
        cx = x + (w - tot) // 2
        cy = y0 + (h - (0 if i == sel else 6)) // 2
        paste_icon(im, ic, cx, cy - 12, 24, alpha, grey)
        text(im, (cx + 30, cy + 1), nm, f, col, "lm")


def craft_section(im, X0, X1, Y0, Y1):
    """Inventory crafting in the vanilla crafting layout."""
    th = 52
    tx = X0 + 10
    for i, (nm, ic) in enumerate(BENCHES):
        bench_tab(im, tx, Y0, 72, th, ic, i == 0)
        tx += 76
    text(im, (tx + 8, Y0 + 30), "one tab per equipped bench talisman", font("body", 13), PAL["dim"], "lm")
    PY0 = Y0 + th
    grad_fill(im, (X0, PY0, X1, Y1), PAL["panel2"], PAL["panel"], c=6)
    outline(im, (X0, PY0, X1, Y1), PAL["line"], c=6)
    # re-open the selected tab into the panel
    grad_fill(im, (X0 + 11, PY0 - 1, X0 + 10 + 70, PY0 + 2), "#16233a", PAL["panel2"], c=0)
    # header: Crafting > bench   [search] [Craftable only]
    hy = PY0 + 22
    put(im, g_diamond(9, A["base"], A["hi"]), X0 + 14, hy - 4)
    f = font("head", 16)
    text(im, (X0 + 30, hy), "CRAFTING", f, PAL["title"], "lm", track=1.5)
    ax = X0 + 30 + tw("CRAFTING", f, 1.5) + 8
    put(im, g_chev(14, A["hi"]), ax, hy - 7)
    text(im, (ax + 18, hy), "Default", font("headb", 17), "#ffffff", "lm")
    text(im, (ax + 18 + tw("Default", font("headb", 17)) + 8, hy + 1), "hand + Workbench", font("body", 13), PAL["dim"], "lm")
    toggle(im, X1 - 180, hy - 12, True)
    text(im, (X1 - 128, hy), "Craftable only", font("bodyb", 14), PAL["row"], "lm")
    search_box(im, (X1 - 420, hy - 15, X1 - 196, hy + 15), "Search...")
    taper_line(im, X0 + 12, X1 - 12, PY0 + 42, PAL["gold"], 150, 0.8)
    # content: recipe grid (4 wide, scrolls) | ingredients | preview + buttons
    cy0, cy1 = PY0 + 52, Y1 - 10
    gx = X0 + 12
    recipes = [(I_ACC % "mana-rare", "Rare"), (I_ACC % "health-unique", "Unique"), (I_ACC % "speed-normal", "Normal"),
               (I_ACC % "stamina-rare", "Rare"), (I_ACC % "lantern-unique", "Unique"), (I_GEAR % "rod-t2-iron", "Normal"),
               (I_GEAR % "rod-t3-thorium", "Normal"), (I_GEAR % "reel-t2-iron", "Normal"), (I_GEAR % "barbed-hook-II", "Normal"),
               (I_ACC % "regeneration-normal", "Normal"), (I_ENCH % "iron-ingot", None), (I_ENCH % "copper-ingot", None),
               (I_ENCH % "oak-log", None), (I_ENCH % "wheat", None), (I_ENCH % "cobblestone", None), (I_ENCH % "sand", None)]
    gw = 4 * P - 2

    def grid(sub):
        for i, (ic, r) in enumerate(recipes):
            slot(sub, 0 + (i % 4) * P, 0 + (i // 4) * P, "selected" if i == 0 else "empty", RAR.get(r), ic)
    clipped(im, (gx, cy0, gx + gw + 8, cy1), lambda sub: grid_offset(sub, grid))
    scrollbar(im, gx + gw + 6, cy0, cy1, cy0 + 2, cy0 + 150)
    # ingredients column (vanilla: item name as the panel title, then 72 px ingredient rows)
    ix0, ix1 = gx + gw + 22, X1 - 196
    panel(im, (ix0, cy0, ix1, cy1), inset=True, c=5)
    text(im, ((ix0 + ix1) // 2, cy0 + 18), "Mana Charm", font("headb", 18), RAR["Rare"], "mm")
    text(im, ((ix0 + ix1) // 2, cy0 + 38), "Charm  -  Rare  -  +12 Max Mana", font("body", 13), PAL["text"], "mm")
    iy = cy0 + 54
    for ic, nm, have, need in ((I_ACC % "mana-unique", "Mana Charm (Unique)", 1, 1),
                               (I_ENCH % "cobalt-ingot", "Enchanted Cobalt Ingot", 7, 4), (I_ENCH % "sap", "Enchanted Sap", 9, 8)):
        slot(im, ix0 + 8, iy, "empty", None, ic, size=56)
        text(im, (ix0 + 74, iy + 18), nm, font("body", 14), PAL["row"], "lm")
        text(im, (ix0 + 74, iy + 39), "%d / %d" % (have, need), font("headb", 15), PAL["green"] if have >= need else PAL["red"], "lm")
        iy += 62
    # preview column (vanilla: big item preview on a soft energy glow, progress bar, Craft, then Craft x10 | Craft All)
    px0, px1 = X1 - 184, X1 - 12
    pcx = (px0 + px1) // 2
    layer = Image.new("RGBA", (px1 - px0, 150), (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse((24, 20, px1 - px0 - 24, 130), fill=rgb(A["base"], 120))
    layer = layer.filter(ImageFilter.GaussianBlur(16))
    reg = im.crop((px0, cy0, px1, cy0 + 150)).convert("RGBA")
    im.paste(Image.alpha_composite(reg, layer).convert("RGB"), (px0, cy0))
    big = icon(I_ACC % "mana-rare", 64).resize((128, 128), Image.NEAREST)
    im.paste(big, (pcx - 64, cy0 + 8), big)
    bar(im, (px0 + 6, cy0 + 146, px1 - 6, cy0 + 150), 0.0, "accent")
    put(im, g_check(14, PAL["green"]), px0 + 6, cy0 + 158)
    text(im, (px0 + 24, cy0 + 165), "Ready  +40 Alchemy XP", font("bodyb", 13), PAL["green"], "lm")
    button(im, (px0 + 4, cy1 - 76, px1 - 4, cy1 - 40), "Craft", "primary")
    hw = (px1 - px0 - 14) // 2
    button(im, (px0 + 4, cy1 - 32, px0 + 4 + hw, cy1), "x10", "secondary", "disabled", fsize=15)
    button(im, (px1 - 4 - hw, cy1 - 32, px1 - 4, cy1), "All", "secondary", fsize=15)


def grid_offset(sub, fn):
    fn(sub)


MINING = [("copper-ingot", "1,284"), ("iron-ingot", "912"), ("silver-ingot", "88"), ("gold-ingot", "141"),
          ("thorium-ingot", "356"), ("cobalt-ingot", "47"), ("adamantite-ingot", "12"), ("mithril-ingot", "3"),
          ("onyxium-ingot", "1"), ("cobblestone", "4.2k"), ("rubble", "2.9k"), ("basalt", "640"), ("slate", "515"),
          ("sandstone", "233"), ("sand", "1.1k"), ("clay", "77")]


def pocket_section(im, X0, X1, Y0, Y1):
    """A Void (Pocket Dimension) bag shown in the top panel: its grid, space bar and the condensed actions."""
    panel(im, (X0, Y0, X1, Y1))
    hy = Y0 + 22
    paste_icon(im, I_WARP % "Mining", X0 + 12, hy - 14, 28)
    f = font("head", 16)
    text(im, (X0 + 46, hy), "MINING POCKET", f, PAL["title"], "lm", track=1.5)
    sx = X0 + 46 + tw("MINING POCKET", f, 1.5) + 18
    text(im, (sx, hy), "Space", font("bodyb", 14), PAL["dim"], "lm")
    bar(im, (sx + 50, hy - 4, sx + 230, hy + 4), 12264 / 20000, "accent", segs=4)
    text(im, (sx + 240, hy), "12,264 / 20,000", font("headb", 15), PAL["row"], "lm")
    text(im, (X1 - 30, hy), "Upgrades", font("head", 15), A["hi"], "rm")
    put(im, g_chev(14, A["hi"]), X1 - 28, hy - 7)
    taper_line(im, X0 + 12, X1 - 12, Y0 + 42, PAL["gold"], 150, 0.8)
    # filter row
    fy = Y0 + 52
    search_box(im, (X0 + 12, fy, X0 + 254, fy + 30), "Search this pocket...")
    x = X0 + 262
    for i, nm in enumerate(("All", "Ingots", "Stone")):
        x += chip(im, x, fy, nm, i == 0, 30, fsize=14) + 5
    # bag grid (server-drawn, 6 wide, scrolls)
    gy0, gy1 = fy + 42, Y1 - 10
    gx = X0 + 12
    gw = 6 * P - 2

    def grid(sub):
        for i in range(24):
            if i < len(MINING):
                nm, n = MINING[i]
                slot(sub, (i % 6) * P, (i // 6) * P, "selected" if i == 1 else "empty", None, I_ENCH % nm, n)
            else:
                slot(sub, (i % 6) * P, (i // 6) * P)
    clipped(im, (gx, gy0, gx + gw + 8, gy1), grid)
    scrollbar(im, gx + gw + 6, gy0, gy1, gy0 + 2, gy0 + 170)
    # action panel: selected item, ONE amount box above the buttons (Skyy 10-10), Withdraw / Deposit / Sell / Unpack
    ax0, ax1 = gx + gw + 22, X1 - 12
    panel(im, (ax0, fy, ax1, gy1), inset=True, c=5)
    slot(im, ax0 + 10, gy0 - 32, "empty", None, I_ENCH % "iron-ingot")
    text(im, (ax0 + 96, gy0 - 14), "Enchanted Iron", font("headb", 17), "#ffffff", "lm")
    rich(im, ax0 + 96, gy0 + 9, [("In pocket ", font("body", 14), PAL["dim"]), ("912", font("headb", 15), PAL["row"]),
                                 ("   In bag ", font("body", 14), PAL["dim"]), ("12", font("headb", 15), PAL["row"])])
    rich(im, ax0 + 96, gy0 + 30, [("Sells for ", font("body", 14), PAL["dim"]), ("640", font("headb", 15), "#ffd76a"),
                                  (" each", font("body", 14), PAL["dim"])])
    ay = gy0 + 58
    text(im, (ax0 + 12, ay + 15), "Amount", font("bodyb", 14), PAL["text"], "lm")
    search_box(im, (ax0 + 80, ay, ax1 - 70, ay + 30), "", focused=True, value="64", icon_on=False)
    button(im, (ax1 - 62, ay, ax1 - 10, ay + 30), "Max", "secondary", fsize=14)
    bw = (ax1 - ax0 - 30) // 2
    by = ay + 42
    button(im, (ax0 + 10, by, ax0 + 10 + bw, by + 36), "Withdraw", "primary")
    button(im, (ax1 - 10 - bw, by, ax1 - 10, by + 36), "Deposit", "secondary")
    button(im, (ax0 + 10, by + 44, ax0 + 10 + bw, by + 80), "Sell 64", "secondary")
    button(im, (ax1 - 10 - bw, by + 44, ax1 - 10, by + 80), "Unpack", "secondary")
    ny = by + 96
    rich(im, ax0 + 12, ny, [("Sell 64: ", font("body", 13), PAL["dim"]), ("40,960 coins", font("bodyb", 13), "#ffd76a")])
    rich(im, ax0 + 12, ny + 20, [("Unpack 64: ", font("body", 13), PAL["dim"]), ("6,400 Iron Ingot", font("bodyb", 13), PAL["row"])])
    toggle(im, ax0 + 12, gy1 - 34, True, "Auto-compact")


def make_mockup(mode="craft"):
    set_accent("Sky Azure")
    W, H = 1920, 1080
    im = bg_world(W, H, 205)
    WX0, WY0, WX1, WY1 = 138, 12, 1781, 1067
    window_frame(im, (WX0, WY0, WX1, WY1))
    # ---- top tab bar (12 tabs, condensed labels) + coins / bank / mail / close
    TB0, TB1 = WY0 + 8, WY0 + 62
    grad_fill(im, (WX0 + 5, TB0, WX1 - 5, TB1), "#0a111e", "#0c1525", c=4)
    hline(im, WX0 + 6, WX1 - 6, TB1, PAL["lineHi"])
    taper_line(im, WX0 + 20, WX1 - 20, TB1 + 1, PAL["gold"], 120, 0.8)
    tx = WX0 + 16
    for i, (nm, ic) in enumerate(TABS):
        tab(im, (tx, TB0 + 4, tx + 103, TB1 - 1), nm, ic, "selected" if i == 0 else "normal", 16, "headc")
        tx += 105
    rx = WX1 - 18
    button(im, (rx - 40, TB0 + 9, rx, TB0 + 49), "", "secondary", glyph=g_x(18, "#d6e4ee"))
    rx -= 48
    button(im, (rx - 40, TB0 + 9, rx, TB0 + 49), "", "secondary", glyph=g_envelope(20, "#c2d1e2"))
    put(im, ss_glyph(18, 18, lambda d, s: d.ellipse((0, 0, 18 * s - 1, 18 * s - 1), fill=rgb(PAL["red"]))), rx - 12, TB0 + 3)
    text(im, (rx - 3, TB0 + 12), "2", font("headb", 13), "#ffffff", "mm", shadow=False)
    rx -= 50
    fv, fk = font("headb", 16), font("head", 13)
    panel(im, (rx - 104, TB0 + 9, rx, TB0 + 49), inset=True, c=4)
    paste_icon(im, I_HUB % "storage_bank", rx - 98, TB0 + 17, 24)
    text(im, (rx - 68, TB0 + 21), "BANK", fk, PAL["dim"], "lm", track=1)
    text(im, (rx - 68, TB0 + 38), "3.2M", fv, "#e9eef7", "lm")
    rx -= 112
    panel(im, (rx - 128, TB0 + 9, rx, TB0 + 49), inset=True, c=4)
    put(im, g_coin(22), rx - 120, TB0 + 18)
    text(im, (rx - 90, TB0 + 21), "COINS", fk, PAL["dim"], "lm", track=1)
    text(im, (rx - 90, TB0 + 38), "1,245,210", fv, "#ffd76a", "lm")

    CY0, CY1 = 86, 1020
    LX0, LX1 = WX0 + 16, WX0 + 16 + 420
    CX0, CX1 = LX1 + 16, LX1 + 16 + 760
    RX0, RX1 = CX1 + 16, WX1 - 16

    # ================= LEFT: character
    panel(im, (LX0, CY0, LX1, CY1), "Character")
    text(im, (LX1 - 14, CY0 + 18), "Islander", font("bodyb", 15), PAL["text"], "rm")
    ey = CY0 + 42
    pitch = 92
    left = [("Head", I_ARM % "Foraging_Maple_Head", "Rare"), ("Chest", I_ARM % "Foraging_Maple_Chest", "Rare"),
            ("Hands", I_ARM % "Foraging_Maple_Hands", "Unique"), ("Legs", I_ARM % "Foraging_Maple_Legs", "Unique")]
    lx = LX0 + 14
    for i, (nm, ic, r) in enumerate(left):
        slot(im, lx, ey + i * pitch, "empty", RAR[r], ic)
        caption(im, lx + 37, ey + i * pitch + 76, nm)
    rxs = LX1 - 14 - 74
    offhand = None if mode == "craft" else I_ACC % "lantern-unique"
    slot(im, rxs, ey, "selected" if mode == "craft" else "empty", None if offhand is None else RAR["Unique"], offhand,
         ghost=g_shield(30, "#3a5070"))
    put(im, ss_glyph(20, 20, lambda d, s: (d.rectangle((0, 0, 20 * s, 20 * s), fill=rgb("#0c1422")),
                                          d.polygon([(5 * s, 7 * s), (15 * s, 7 * s), (10 * s, 14 * s)], fill=rgb(A["hi"])))),
        rxs + 52, ey + 52)
    caption(im, rxs + 37, ey + 76, "Off-hand", A["hi"])
    right = [("Utility", I_GEAR % "reel-t3-thorium", "Normal", g_diamond(24, "#2c3c57", "#36486a", "#1a2538")),
             ("Utility", None, None, g_diamond(24, "#2c3c57", "#36486a", "#1a2538")),
             ("Tool", I_GEAR % "rod-t3-thorium", "Normal", g_sword(30, "#2c3c57"))]
    for i, (nm, ic, r, gh) in enumerate(right):
        slot(im, rxs, ey + (i + 1) * pitch, "empty", RAR.get(r), ic, ghost=gh)
        caption(im, rxs + 37, ey + (i + 1) * pitch + 76, nm)
    # preview
    px0, px1 = lx + 74 + 12, rxs - 12
    py0, py1 = ey, ey + 4 * pitch - 20
    panel(im, (px0, py0, px1, py1), inset=True, c=5)
    pcx = (px0 + px1) // 2
    gl = Image.new("RGBA", (px1 - px0, py1 - py0), (0, 0, 0, 0))
    ImageDraw.Draw(gl).ellipse((30, py1 - py0 - 70, px1 - px0 - 30, py1 - py0 - 20), fill=rgb(A["base"], 110))
    gl = gl.filter(ImageFilter.GaussianBlur(12))
    reg = im.crop((px0, py0, px1, py1)).convert("RGBA")
    im.paste(Image.alpha_composite(reg, gl).convert("RGB"), (px0, py0))
    d = ImageDraw.Draw(im, "RGBA")
    base_y = py1 - 46
    fig = [((-22, -150), (22, -108), "#d9a87e"), ((-26, -106), (26, -40), "#3a6b45"), ((-40, -104), (-28, -46), "#d9a87e"),
           ((28, -104), (40, -46), "#d9a87e"), ((-24, -40), (-2, 8), "#4a3a2a"), ((2, -40), (24, 8), "#4a3a2a"),
           ((-26, -154), (26, -136), "#5a3b22"), ((-26, -64), (26, -56), "#7a5a2a")]
    for (ax, ay), (bx, by), col in fig:
        d.rectangle((pcx + ax, base_y + ay, pcx + bx, base_y + by), fill=rgb(col), outline=rgb("#05080e"))
    d.rectangle((pcx - 12, base_y - 132, pcx - 6, base_y - 126), fill=rgb("#1a1a2a"))
    d.rectangle((pcx + 6, base_y - 132, pcx + 12, base_y - 126), fill=rgb("#1a1a2a"))
    text(im, (pcx, py0 + 16), "Player preview", font("body", 13), PAL["dim"], "mm", shadow=False)
    if mode == "craft":
        # the off-hand picker, open (click the off-hand slot): items you can hold in the off-hand, from bag + Void
        bx1 = rxs - 8
        bx0 = bx1 - 224
        by0 = ey + 6
        by1 = by0 + 166
        shadow(im, (bx0, by0, bx1, by1), 8, 200, 3)
        grad_fill(im, (bx0, by0, bx1, by1), "#16233a", "#0e1729", c=6)
        outline(im, (bx0, by0, bx1, by1), PAL["edge"], c=6)
        outline(im, (bx0 + 1, by0 + 1, bx1 - 1, by1 - 1), A["base"], c=5)
        d.polygon([(bx1, ey + 30), (bx1 + 7, ey + 37), (bx1, ey + 44)], fill=rgb(A["base"]))
        text(im, (bx0 + 12, by0 + 18), "Pick off-hand", font("headb", 16), "#ffffff", "lm")
        text(im, (bx0 + 12, by0 + 38), "Items you can hold in it", font("body", 13), PAL["dim"], "lm")
        opts = [(I_ACC % "lantern-unique", "Unique", "Lantern"), (I_ACC % "lantern-normal", "Normal", "Lantern"),
                (None, None, "Empty")]
        for i, (ic, r, nm) in enumerate(opts):
            sx = bx0 + 12 + i * 70
            slot(im, sx, by0 + 54, "hover" if i == 0 else "empty", RAR.get(r), ic, size=64,
                 ghost=g_x(20, "#3a5070") if ic is None else None)
            caption(im, sx + 32, by0 + 122, nm, PAL["row"])
        text(im, (bx0 + 12, by1 - 14), "Key: swap off-hand", font("body", 13), PAL["action"], "lm")
    # Void Charms
    vy = ey + 4 * pitch + 2
    text(im, (lx, vy + 10), "VOID CHARMS", font("head", 14), PAL["text"], "lm", track=1.2)
    text(im, (lx + 118, vy + 10), "9 / 18", font("bodyb", 14), PAL["dim"], "lm")
    text(im, (LX1 - 30, vy + 10), "All charms", font("head", 14), A["hi"], "rm")
    put(im, g_chev(13, A["hi"]), LX1 - 28, vy + 4)
    charms = [("mana-rare", "Rare"), ("health-unique", "Unique"), ("speed-legendary", "Legendary"),
              ("stamina-normal", "Normal"), ("feather-unique", "Unique")]
    for i, (ic, r) in enumerate(charms):
        slot(im, lx + i * P, vy + 24, "empty", RAR[r], I_ACC % ic)
    # pet + mount
    py = vy + 24 + 74 + 12
    half = (LX1 - LX0 - 28 - 10) // 2
    for i, (cap, ic, nm, lv, r) in enumerate((("PET", I_PET % "Hawk", "Hawk", "Lv 42", "Legendary"),
                                                ("MOUNT", I_PET % "Horse", "Horse", "Lv 18", "Rare"))):
        bx = lx + i * (half + 10)
        panel(im, (bx, py, bx + half, py + 84), inset=True, c=4)
        slot(im, bx + 5, py + 5, "empty", RAR[r], ic)
        text(im, (bx + 88, py + 18), cap, font("head", 13), PAL["dim"], "lm", track=1.2)
        text(im, (bx + 88, py + 40), nm, font("bodyb", 16), RAR[r], "lm")
        text(im, (bx + 88, py + 62), lv + "  " + r, font("body", 13), PAL["text"], "lm")
    cy = py + 94
    panel(im, (lx, cy, LX1 - 14, cy + 80), inset=True, c=4)
    paste_icon(im, I_EMB % "Archer", lx + 8, cy + 8, 64)
    text(im, (lx + 84, cy + 20), "Archer", font("headb", 20), "#a8e07a", "lm")
    level_pill(im, lx + 84 + tw("Archer", font("headb", 20)) + 10, cy + 9, "Lv 23")
    bar(im, (lx + 84, cy + 58, LX1 - 26, cy + 68), 0.62, "xp", "Class XP", "1,240 / 2,000")
    vy2 = cy + 90
    vit = [("Health", g_heart(20, PAL["health"]), "412 / 412", "health", 1.0),
           ("Mana", g_drop(20, PAL["mana"]), "96 / 140", "mana", 0.69),
           ("Stamina", g_bolt(20, PAL["stamina"]), "100 / 100", "stamina", 1.0),
           ("Defense", g_shield(20, PAL["defense"]), "184", "defense", 0.46)]
    for i, (nm, g, val, k, fr) in enumerate(vit):
        bx = lx + (i % 2) * (half + 10)
        by = vy2 + (i // 2) * 56
        panel(im, (bx, by, bx + half, by + 48), inset=True, c=4)
        put(im, g, bx + 10, by + 7)
        text(im, (bx + 38, by + 17), nm, font("bodyb", 15), PAL["text"], "lm")
        text(im, (bx + half - 10, by + 17), val, font("headb", 16), "#ffffff", "rm")
        bar(im, (bx + 10, by + 34, bx + half - 10, by + 40), fr, k)
    sy = vy2 + 2 * 56 + 2
    panel(im, (lx, sy, LX1 - 14, sy + 34), inset=True, c=4)
    x = lx + 12
    for k, v in (("Strength", "34"), ("Crit", "12%"), ("Speed", "+8%")):
        x = rich(im, x, sy + 17, [(k + " ", font("body", 14), PAL["dim"]), (v, font("headb", 15), PAL["green"])]) + 16
    button(im, (lx, CY1 - 54, LX1 - 14, CY1 - 14), "Stats by source", "secondary")

    # ================= CENTRE: top panel (Craft or pocket) + hanging tab row + inventory
    TOP1 = 490
    if mode == "craft":
        craft_section(im, CX0, CX1, CY0, TOP1)
    else:
        # bench tabs are part of Craft; a pocket uses the full height
        pocket_section(im, CX0, CX1, CY0, TOP1)
    hang_tabs(im, CX0 + 8, TOP1, CX1 - 8, 38, POCKETS, 0 if mode == "craft" else 1)
    IY0 = TOP1 + 46
    panel(im, (CX0, IY0, CX1, CY1))
    gx = CX0 + (CX1 - CX0 - (9 * P - 2)) // 2
    hy = IY0 + 18
    put(im, g_diamond(9, A["base"], A["hi"]), gx, hy - 4)
    text(im, (gx + 16, hy), "INVENTORY", font("head", 15), PAL["title"], "lm", track=1.5)
    text(im, (gx + 130, hy), "27 / 36", font("bodyb", 14), PAL["dim"], "lm")
    button(im, (gx + 9 * P - 2 - 64, hy - 14, gx + 9 * P - 2, hy + 14), "Sort", "secondary", fsize=14)
    button(im, (gx + 9 * P - 2 - 196, hy - 14, gx + 9 * P - 2 - 72, hy + 14), "Stash to Void", "secondary", fsize=14)
    gy = IY0 + 38
    inv = {0: (I_ENCH % "iron-ingot", 12, None), 1: (I_ENCH % "copper-ingot", 23, None), 2: (I_ENCH % "oak-log", 41, None),
           3: (I_ENCH % "maple-log", 12, None), 4: (I_FISH % "frost_cod", 6, "Normal"), 5: (I_FISH % "cinderfin", 2, "Rare"),
           6: (I_EGG % "Combat_Rare", 1, None), 8: (I_ARM % "Foraging_Oak_Chest", None, "Normal"), 9: (I_ENCH % "wheat", 128, None),
           10: (I_ENCH % "carrot", 37, None), 11: (I_ENCH % "potato", 9, None), 13: (I_GEAR % "rod-t2-iron", None, "Normal"),
           14: (I_FISH % "glass_pike", 3, "Unique"), 15: (I_ACC % "feather-normal", None, "Normal"), 18: (I_ENCH % "cobblestone", 64, None),
           19: (I_ENCH % "sand", 64, None), 20: (I_ENCH % "clay", 18, None), 22: (I_GEAR % "lure-hook-I", 4, "Normal"),
           23: (I_EGG % "Mining_Uncommon", 1, None), 26: (I_FISH % "magma_marlin", 1, "Legendary"), 27: (I_ENCH % "sap", 5, None),
           28: (I_ENCH % "fibre", 74, None), 31: (I_ARM % "Foraging_Oak_Legs", None, "Normal")}
    for i in range(36):
        it = inv.get(i)
        x, y = gx + (i % 9) * P, gy + (i // 9) * P
        if it:
            slot(im, x, y, "empty", RAR.get(it[2]), it[0], it[1])
        else:
            slot(im, x, y)
    hyb = gy + 4 * P + 8
    hot = [(I_GEAR % "rod-t3-thorium", None, "Normal"), (I_ABIL % "Archer_ArrowRain", None, None),
           (I_ABIL % "Archer_RapidFire", None, None), (I_ABIL % "Archer_HuntersNet", None, None),
           (I_ENCH % "iron-ingot", 12, None), None, (I_FISH % "frost_cod", 6, "Normal"), None, (I_ACC % "lantern-unique", None, "Unique")]
    panel(im, (gx - 6, hyb - 6, gx + 9 * P + 3, hyb + 74 + 9), inset=True, c=5)
    for i in range(9):
        it = hot[i]
        st = "selected" if i == 0 else "empty"
        if it:
            slot(im, gx + i * P, hyb, st, RAR.get(it[2]), it[0], it[1], keycap=str(i + 1))
        else:
            slot(im, gx + i * P, hyb, st, keycap=str(i + 1))
    hotbar_marker(im, gx, hyb)
    ty = hyb + 74 + 16
    text(im, (gx, ty + 19), "TELEPORT", font("head", 14), PAL["dim"], "lm", track=1.2)
    tx = gx + 92
    for nm, ic in (("Island", I_HUB % "world_island"), ("Hub", I_HUB % "hubrow_home")):
        button(im, (tx, ty, tx + 130, ty + 38), "", "secondary")
        paste_icon(im, ic, tx + 14, ty + 7, 24)
        text(im, (tx + 46, ty + 20), nm, font("head", 16), PAL["row"], "lm")
        tx += 138
    button(im, (tx, ty, tx + 42, ty + 38), "", "secondary", glyph=g_plus(16, "#9fb3cc"))
    button(im, (gx + 9 * P - 2 - 100, ty, gx + 9 * P - 2, ty + 38), "Edit", "secondary", glyph=g_pencil(16, "#c2d1e2"))

    # ================= RIGHT: compact Skills + Right now
    panel(im, (RX0, CY0, RX1, TOP1), "Skills", link="Open")
    rows = SKILLS + [("Total level", None, sum(s[2] for s in SKILLS))]
    ry = CY0 + 38
    rh = 29
    for i, (nm, ic, lv) in enumerate(rows):
        y = ry + i * rh
        if i % 2 == 0:
            ImageDraw.Draw(im, "RGBA").rectangle((RX0 + 10, y, RX1 - 10, y + rh - 2), fill=(255, 255, 255, 7))
        if ic:
            paste_icon(im, ic, RX0 + 14, y + 1, 24)
            text(im, (RX0 + 46, y + 13), nm, font("bodyb", 14), PAL["row"], "lm")
            bar(im, (RX0 + 168, y + 11, RX1 - 60, y + 16), ((lv * 37) % 100) / 100.0, "xp")
            text(im, (RX1 - 16, y + 13), str(lv), font("headb", 15), PAL["xp"], "rm")
        else:
            put(im, g_diamond(20, PAL["gold"], PAL["goldHi"]), RX0 + 16, y + 3)
            text(im, (RX0 + 46, y + 13), nm, font("bodyb", 14), "#ffffff", "lm")
            text(im, (RX1 - 16, y + 13), str(lv), font("headb", 16), PAL["xp"], "rm")
    panel(im, (RX0, IY0, RX1, CY1), "Right now")
    rn = [(g_quest(20, PAL["action"]), "Quest:", "Visit the Farming island", PAL["action"], None),
          (I_WARP % "Foraging", "11", "points in Foraging tree", PAL["xp"], None),
          (I_WARP % "Mining", "5", "points in Mining tree", PAL["xp"], None),
          (I_EMB % "Archer", "2", "points in Archer tree", PAL["xp"], None),
          (I_WARP % "Fishing", "Daily:", "Catch fish", PAL["action"], (12, 20)),
          (I_EGG % "Combat_Rare", "Egg:", "Rare Combat - hatch", PAL["green"], None),
          (I_ENCH % "iron-ingot", "Furnace:", "64 Iron Ingot ready", PAL["green"], None),
          (I_HUB % "market_bazaar", "Bazaar:", "2 orders filled", PAL["green"], None),
          (g_envelope(20, "#c2d1e2"), "Mail:", "2 new letters", PAL["text"], None)]
    y = IY0 + 38
    for i, (ic, tag, msg, tc, prog) in enumerate(rn):
        row(im, (RX0 + 10, y, RX1 - 10, y + 31), "hover" if i == 0 else "normal")
        if isinstance(ic, str):
            paste_icon(im, ic, RX0 + 16, y + 4, 24)
        else:
            put(im, ic, RX0 + 18, y + 6)
        x = rich(im, RX0 + 48, y + 16, [(tag + " ", font("bodyb", 14), tc), (msg, font("body", 14), PAL["row"])])
        if prog:
            text(im, (RX1 - 34, y + 16), "%d / %d" % prog, font("headb", 14), PAL["xp"], "rm")
        put(im, g_chev(14, A["hi"] if i == 0 else "#7f93a6"), RX1 - 28, y + 9)
        y += 36
    text(im, ((RX0 + RX1) // 2, CY1 - 20), "Click a row to go there", font("body", 13), PAL["dim"], "mm")

    # ================= key hints
    hy2 = 1044
    hints = [("LMB", "Take"), ("RMB", "Take one"), ("Shift", "Move"), ("1-9", "To hotbar"), ("Q", "Drop"),
             ("S", "Sort"), ("Tab / Esc", "Close")]
    fh = font("body", 15)
    total = sum(max(22, tw(k, font("headb", 14)) + 10) + 6 + tw(v, fh) + 26 for k, v in hints)
    x = (W - total) // 2
    for k, v in hints:
        w = key_cap(im, x, hy2 - 11, k)
        text(im, (x + w + 6, hy2), v, fh, "#aebfd3", "lm")
        x += w + 6 + tw(v, fh) + 26
    return im


# ----------------------------------------------------------------------------------------------------------------- inventory mockup v3
# v3 (Skyy's voice review 2026-11-14, research/ui-theme-art/skyy-review-1114.md): compact stacked top tabs; Runeteria-like crafting
# SYSTEM in our theme (icon bench tabs, bench name, paged recipe grid, preview + ingredient icons, Craft / 10x / MAX); compact Skills
# icon grid; a skinny Right now list that holds the QUESTS; icon buttons (sort / quick-stack / put all / take all / stash to Void) at the
# top of the inventory panel, no slots-used line; the column right of the character = off-hand slots; a chest view.

def g_sort(size, col):
    def f(d, s):
        n = size * s
        for i, w in enumerate((0.8, 0.6, 0.4)):
            y = n * (0.22 + i * 0.26)
            d.rectangle((n * 0.1, y, n * (0.1 + w), y + n * 0.13), fill=rgb(col))
    return ss_glyph(size, size, f)


def g_arrows(size, col, up=True, double=False, base=False):
    def f(d, s):
        n = size * s
        ys = (0.12, 0.42) if double else (0.2,)
        for y0 in ys:
            y0 *= n
            if up:
                d.polygon([(n * 0.5, y0), (n * 0.86, y0 + n * 0.3), (n * 0.14, y0 + n * 0.3)], fill=rgb(col))
            else:
                y1 = n - y0
                d.polygon([(n * 0.5, y1), (n * 0.86, y1 - n * 0.3), (n * 0.14, y1 - n * 0.3)], fill=rgb(col))
        if not double:
            d.rectangle((n * 0.4, n * 0.48, n * 0.6, n * 0.74) if up else (n * 0.4, n * 0.26, n * 0.6, n * 0.52), fill=rgb(col))
        if base:
            d.rectangle((n * 0.12, n * 0.82, n * 0.88, n * 0.92), fill=rgb(col))
    return ss_glyph(size, size, f)


def g_void(size):
    def f(d, s):
        n = size * s
        d.ellipse((n * 0.06, n * 0.06, n * 0.94, n * 0.94), fill=rgb("#2a1748"))
        for i, c in enumerate(("#6b3fd0", "#9a6bff", "#c9a8ff")):
            k = n * (0.14 + i * 0.12)
            d.arc((k, k, n - k, n - k), 200 + i * 40, 470 + i * 40, fill=rgb(c), width=int(s * 2.2))
        d.ellipse((n * 0.43, n * 0.43, n * 0.57, n * 0.57), fill=rgb("#ffffff"))
    return ss_glyph(size, size, f)


def g_tri(size, col, right=True):
    def f(d, s):
        n = size * s
        if right:
            d.polygon([(n * 0.3, n * 0.15), (n * 0.78, n * 0.5), (n * 0.3, n * 0.85)], fill=rgb(col))
        else:
            d.polygon([(n * 0.7, n * 0.15), (n * 0.22, n * 0.5), (n * 0.7, n * 0.85)], fill=rgb(col))
    return ss_glyph(size, size, f)


def g_box(size, col):
    def f(d, s):
        n = size * s
        d.rectangle((n * 0.12, n * 0.12, n * 0.88, n * 0.88), outline=rgb(col), width=int(s * 1.6))
    return ss_glyph(size, size, f)


def icon_btn(im, x, y, glyph, state="normal", size=32):
    button(im, (x, y, x + size - 1, y + size - 1), "", "secondary", state, glyph=glyph)


def header_icons(im, x_right, yc, items, hover=None):
    """Small vanilla-pattern icon buttons, right-aligned (items = [(glyph, name)]); returns the left x."""
    x = x_right
    for i, (g, nm) in enumerate(reversed(items)):
        x -= 32
        icon_btn(im, x, yc - 16, g, "hover" if nm == hover else "normal")
        x -= 4
    return x


def mini_tip(im, x, y, title, body):
    f1, f2 = font("bodyb", 14), font("body", 13)
    w = max(tw(title, f1), tw(body, f2)) + 20
    shadow(im, (x, y, x + w, y + 46), 6, 200, 3)
    grad_fill(im, (x, y, x + w, y + 46), "#16233a", "#0e1729", c=4)
    outline(im, (x, y, x + w, y + 46), A["base"], c=4)
    text(im, (x + 10, y + 14), title, f1, "#ffffff", "lm")
    text(im, (x + 10, y + 33), body, f2, PAL["text"], "lm")


def stacked_tab(im, box, label, icon_rel, selected):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(im, "RGBA")
    if selected:
        grad_fill(im, (x0, y0, x1, y1 + 1), "#1a2b47", PAL["panel2"], c=0)
        d.line([(x0, y1 + 1), (x0, y0 + 4), (x0 + 4, y0), (x1 - 4, y0), (x1, y0 + 4), (x1, y1 + 1)], fill=rgb(PAL["lineHi"]))
        glow(im, (x0 + 4, y0, x1 - 4, y0 + 2), A["base"], 5, 170, 0, 2)
        d.rectangle((x0 + 4, y0, x1 - 4, y0 + 2), fill=rgb(A["base"]))
    cx = (x0 + x1) // 2
    paste_icon(im, icon_rel, cx - 12, y0 + 6, 24, 1.0 if selected else 0.7, grey=not selected)
    text(im, (cx, y1 - 11), label, font("headc", 14), PAL["title"] if selected else "#9fb2c8", "mm")


BENCH3 = [("Default", "hand + Workbench", I_MENU % "Crafting"), ("Armor bench", "", I_HUB % "smithing_gear"),
          ("Weapon bench", "", I_HUB % "character_class"), ("Alchemy bench", "", I_NODE % "Alchemy_B1R1a"),
          ("Arcane bench", "", I_NODE % "Mage_B1R1a"), ("Farming bench", "", I_WARP % "Farming")]


def craft_v3(im, X0, X1, Y0, Y1):
    panel(im, (X0, Y0, X1, Y1))
    # icon category / bench tabs (square icon buttons, selected = accent)
    tx = X0 + 12
    for i, (nm, sub, ic) in enumerate(BENCH3):
        box = (tx, Y0 + 10, tx + 47, Y0 + 57)
        if i == 0:
            glow(im, box, A["base"], 4, 150, 4, 2)
            grad_fill(im, box, mix(A["base"], "#111b2d", 0.6), mix(A["base"], "#111b2d", 0.8), c=4)
            outline(im, box, A["base"], c=4)
            paste_icon(im, ic, tx + 6, Y0 + 16, 36)
        else:
            grad_fill(im, box, "#18253c", "#121c2f", c=4)
            outline(im, box, "#2b3d5b", c=4)
            paste_icon(im, ic, tx + 8, Y0 + 18, 32, 0.8)
        tx += 52
    text(im, (tx + 6, Y0 + 34), "+ one tab per bench talisman", font("body", 13), PAL["dim"], "lm")
    toggle(im, X1 - 176, Y0 + 22, True)
    text(im, (X1 - 124, Y0 + 34), "Craftable only", font("bodyb", 14), PAL["row"], "lm")
    # bench name + search
    hy = Y0 + 82
    put(im, g_diamond(9, A["base"], A["hi"]), X0 + 14, hy - 4)
    text(im, (X0 + 30, hy), "DEFAULT", font("head", 17), PAL["title"], "lm", track=1.5)
    text(im, (X0 + 30 + tw("DEFAULT", font("head", 17), 1.5) + 10, hy + 1), "hand + Workbench  -  24 recipes", font("body", 13),
         PAL["dim"], "lm")
    search_box(im, (X1 - 300, hy - 15, X1 - 12, hy + 15), "Search recipes...")
    taper_line(im, X0 + 12, X1 - 12, hy + 22, PAL["gold"], 150, 0.8)
    # recipe grid 5 x 3 (paged)
    gx, gy = X0 + 12, hy + 32
    recipes = [("px:pickaxe", None), ("px:axe", None), ("px:shovel", None), ("px:sword", None), ("px:torch", None),
               ("px:planks", None), ("px:chest", None), ("px:bread", None), ("px:stew", None), ("px:stick", None),
               (I_ARM % "Foraging_Oak_Head", "Normal"), (I_ARM % "Foraging_Oak_Chest", "Normal"), (I_ENCH % "oak-log", None),
               (I_ENCH % "cobblestone", None), (I_ENCH % "wheat", None)]
    for i, (ic, r) in enumerate(recipes):
        slot(im, gx + (i % 5) * P, gy + (i // 5) * P, "selected" if i == 0 else "empty", RAR.get(r), ic)
    py = gy + 3 * P + 14
    icon_btn(im, gx, py - 15, g_tri(14, "#c2d1e2", False), "disabled", 30)
    text(im, (gx + (5 * P) // 2, py), "Page 1 / 2", font("headb", 15), PAL["row"], "mm")
    icon_btn(im, gx + 5 * P - 32, py - 15, g_tri(14, "#ffffff", True), "normal", 30)
    # preview: result, name, ingredient icons have / need, Craft / 10x / MAX
    dx0, dx1 = gx + 5 * P + 12, X1 - 12
    dy0, dy1 = gy, Y1 - 12
    panel(im, (dx0, dy0, dx1, dy1), inset=True, c=5)
    slot(im, dx0 + 10, dy0 + 10, "empty", None, "px:pickaxe")
    text(im, (dx0 + 96, dy0 + 24), "Iron Pickaxe", font("headb", 19), "#ffffff", "lm")
    rich(im, dx0 + 96, dy0 + 46, [("T2 Iron", font("bodyb", 14), "#b8c4d0"), ("  -  Tool", font("body", 14), PAL["text"])])
    rich(im, dx0 + 96, dy0 + 68, [("Mining speed ", font("body", 14), PAL["row"]), ("+35%", font("bold", 14), PAL["green"])])
    text(im, (dx0 + 12, dy0 + 102), "NEEDS", font("head", 13), PAL["dim"], "lm", track=1.5)
    ix = dx0 + 12
    for ic, have, need in (("px:ingot", 7, 3), ("px:stick", 12, 2), ("px:planks", 4, 1)):
        slot(im, ix, dy0 + 114, "empty", None, ic, size=64)
        ok = have >= need
        text(im, (ix + 32, dy0 + 190), "%d / %d" % (have, need), font("headb", 15), PAL["green"] if ok else PAL["red"], "mm")
        ix += 70
    put(im, g_check(14, PAL["green"]), ix + 6, dy0 + 140)
    text(im, (ix + 24, dy0 + 147), "Ready", font("bodyb", 14), PAL["green"], "lm")
    text(im, (ix + 6, dy0 + 168), "You can make 2", font("body", 13), PAL["text"], "lm")
    by = dy1 - 44
    bw = (dx1 - dx0 - 20 - 12) // 4
    button(im, (dx0 + 10, by, dx0 + 10 + 2 * bw, by + 34), "Craft", "primary")
    button(im, (dx0 + 16 + 2 * bw, by, dx0 + 16 + 3 * bw, by + 34), "10x", "secondary", "disabled", fsize=15)
    button(im, (dx0 + 22 + 3 * bw, by, dx1 - 10, by + 34), "MAX", "secondary", fsize=15)


CHEST = [(I_ENCH % "oak-log", "64", None), (I_ENCH % "birch-log", "64", None), (I_ENCH % "maple-log", "37", None),
         (I_ENCH % "stick", "128", None), (I_ENCH % "sap", "22", None), None, (I_FISH % "frost_cod", "8", "Normal"),
         (I_FISH % "icebound_salmon", "3", "Unique"), None,
         (I_ENCH % "wheat", "256", None), (I_ENCH % "carrot", "90", None), (I_ENCH % "potato", "64", None),
         (I_ENCH % "pumpkin", "12", None), None, None, (I_GEAR % "rod-t1-copper", None, "Normal"), None,
         (I_EGG % "Foraging_Common", "1", None),
         (I_ENCH % "cobblestone", "512", None), (I_ENCH % "sand", "64", None), None, None, None, None, None, None, None,
         None, None, None, (I_ARM % "Foraging_Birch_Head", None, "Normal"), None, None, None, None, None]


def chest_v3(im, X0, X1, Y0, Y1):
    panel(im, (X0, Y0, X1, Y1))
    hy = Y0 + 22
    paste_icon(im, I_HUB % "hubrow_storage", X0 + 12, hy - 14, 28)
    text(im, (X0 + 46, hy), "FARM STORAGE", font("head", 16), PAL["title"], "lm", track=1.5)
    text(im, (X0 + 46 + tw("FARM STORAGE", font("head", 16), 1.5) + 10, hy + 1), "Large chest  -  36 slots", font("body", 13),
         PAL["dim"], "lm")
    header_icons(im, X1 - 12, hy, [(g_sort(18, "#c2d1e2"), "Sort"), (g_arrows(18, "#c2d1e2", False, True), "Take all")],
                 hover="Take all")
    taper_line(im, X0 + 12, X1 - 12, Y0 + 42, PAL["gold"], 150, 0.8)
    gx = X0 + (X1 - X0 - (9 * P - 2)) // 2
    gy = Y0 + 54
    for i in range(36):
        it = CHEST[i] if i < len(CHEST) else None
        x, y = gx + (i % 9) * P, gy + (i // 9) * P
        if it:
            slot(im, x, y, "empty", RAR.get(it[2]), it[0], it[1])
        else:
            slot(im, x, y)
    mini_tip(im, X1 - 12 - 72 - 306, hy - 23, "Take all", "Move everything in this chest to your inventory")
    put(im, ss_glyph(8, 14, lambda d, s: d.polygon([(0, 0), (8 * s, 7 * s), (0, 14 * s)], fill=rgb(A["base"]))), X1 - 12 - 72 - 8, hy - 7)


def pocket_v3(im, X0, X1, Y0, Y1):
    panel(im, (X0, Y0, X1, Y1))
    hy = Y0 + 22
    paste_icon(im, I_WARP % "Mining", X0 + 12, hy - 14, 28)
    f = font("head", 16)
    text(im, (X0 + 46, hy), "MINING POCKET", f, PAL["title"], "lm", track=1.5)
    sx = X0 + 46 + tw("MINING POCKET", f, 1.5) + 14
    bar(im, (sx, hy - 4, sx + 150, hy + 4), 12264 / 20000, "accent", segs=4)
    text(im, (sx + 158, hy), "12,264 / 20,000", font("headb", 14), PAL["row"], "lm")
    lx = header_icons(im, X1 - 12, hy, [(g_sort(18, "#c2d1e2"), "Sort"), (g_arrows(18, "#c2d1e2", False, True), "Take all")])
    text(im, (lx - 22, hy), "Upgrades", font("head", 15), A["hi"], "rm")
    put(im, g_chev(14, A["hi"]), lx - 20, hy - 7)
    taper_line(im, X0 + 12, X1 - 12, Y0 + 42, PAL["gold"], 150, 0.8)
    fy = Y0 + 52
    search_box(im, (X0 + 12, fy, X0 + 240, fy + 30), "Search this pocket...")
    x = X0 + 248
    for i, nm in enumerate(("All", "Ingots", "Stone")):
        x += chip(im, x, fy, nm, i == 0, 30, fsize=14) + 5
    gy0, gx = fy + 40, X0 + 12
    for i in range(18):
        x, y = gx + (i % 6) * P, gy0 + (i // 6) * P
        if i < 16:
            nm, n = MINING[i]
            slot(im, x, y, "selected" if i == 1 else "empty", None, I_ENCH % nm, n)
        else:
            slot(im, x, y)
    py = gy0 + 3 * P + 14
    icon_btn(im, gx, py - 15, g_tri(14, "#c2d1e2", False), "disabled", 30)
    text(im, (gx + (6 * P) // 2, py), "Page 1 / 2", font("headb", 15), PAL["row"], "mm")
    icon_btn(im, gx + 6 * P - 32, py - 15, g_tri(14, "#ffffff", True), "normal", 30)
    ax0, ax1 = gx + 6 * P + 12, X1 - 12
    panel(im, (ax0, fy, ax1, Y1 - 12), inset=True, c=5)
    slot(im, ax0 + 8, fy + 8, "empty", None, I_ENCH % "iron-ingot")
    text(im, (ax0 + 90, fy + 26), "Ench. Iron", font("headb", 17), "#ffffff", "lm")
    rich(im, ax0 + 90, fy + 48, [("Here ", font("body", 13), PAL["dim"]), ("912", font("headb", 14), PAL["row"])])
    rich(im, ax0 + 90, fy + 68, [("Sells ", font("body", 13), PAL["dim"]), ("640", font("headb", 14), "#ffd76a")])
    ay = fy + 96
    text(im, (ax0 + 10, ay + 15), "Amount", font("bodyb", 14), PAL["text"], "lm")
    search_box(im, (ax0 + 74, ay, ax1 - 10, ay + 30), "", focused=True, value="64", icon_on=False)
    bw = (ax1 - ax0 - 26) // 2
    by = ay + 40
    button(im, (ax0 + 10, by, ax0 + 10 + bw, by + 34), "Withdraw", "primary", fsize=15)
    button(im, (ax1 - 10 - bw, by, ax1 - 10, by + 34), "Deposit", "secondary", fsize=15)
    button(im, (ax0 + 10, by + 40, ax0 + 10 + bw, by + 74), "Sell", "secondary", fsize=15)
    button(im, (ax1 - 10 - bw, by + 40, ax1 - 10, by + 74), "Unpack", "secondary", fsize=15)
    rich(im, ax0 + 10, by + 94, [("Sell 64: ", font("body", 13), PAL["dim"]), ("40,960 coins", font("bodyb", 13), "#ffd76a")])
    rich(im, ax0 + 10, by + 114, [("Unpack 64: ", font("body", 13), PAL["dim"]), ("6,400 Iron Ingot", font("bodyb", 13), PAL["row"])])
    toggle(im, ax0 + 10, Y1 - 46, True, "Auto-compact")


def make_mockup_v3(mode="craft"):
    set_accent("Sky Azure")
    W, H = 1920, 1080
    im = bg_world(W, H, 205)
    WX0, WY0, WX1, WY1 = 138, 12, 1781, 1067
    window_frame(im, (WX0, WY0, WX1, WY1))
    TB0, TB1 = WY0 + 8, WY0 + 62
    grad_fill(im, (WX0 + 5, TB0, WX1 - 5, TB1), "#0a111e", "#0c1525", c=4)
    hline(im, WX0 + 6, WX1 - 6, TB1, PAL["lineHi"])
    taper_line(im, WX0 + 20, WX1 - 20, TB1 + 1, PAL["gold"], 120, 0.8)
    tx = WX0 + 16
    for i, (nm, ic) in enumerate(TABS):
        stacked_tab(im, (tx, TB0 + 2, tx + 69, TB1 - 1), nm, ic, i == 0)
        tx += 72
    rx = WX1 - 18
    button(im, (rx - 40, TB0 + 9, rx, TB0 + 49), "", "secondary", glyph=g_x(18, "#d6e4ee"))
    rx -= 48
    button(im, (rx - 40, TB0 + 9, rx, TB0 + 49), "", "secondary", glyph=g_envelope(20, "#c2d1e2"))
    put(im, ss_glyph(18, 18, lambda d, s: d.ellipse((0, 0, 18 * s - 1, 18 * s - 1), fill=rgb(PAL["red"]))), rx - 12, TB0 + 3)
    text(im, (rx - 3, TB0 + 12), "2", font("headb", 13), "#ffffff", "mm", shadow=False)
    rx -= 50
    fv, fk = font("headb", 16), font("head", 13)
    panel(im, (rx - 104, TB0 + 9, rx, TB0 + 49), inset=True, c=4)
    paste_icon(im, I_HUB % "storage_bank", rx - 98, TB0 + 17, 24)
    text(im, (rx - 68, TB0 + 21), "BANK", fk, PAL["dim"], "lm", track=1)
    text(im, (rx - 68, TB0 + 38), "3.2M", fv, "#e9eef7", "lm")
    rx -= 112
    panel(im, (rx - 128, TB0 + 9, rx, TB0 + 49), inset=True, c=4)
    put(im, g_coin(22), rx - 120, TB0 + 18)
    text(im, (rx - 90, TB0 + 21), "COINS", fk, PAL["dim"], "lm", track=1)
    text(im, (rx - 90, TB0 + 38), "1,245,210", fv, "#ffd76a", "lm")

    CY0, CY1 = 86, 1020
    LX0, LX1 = WX0 + 16, WX0 + 16 + 420
    CX0, CX1 = LX1 + 16, LX1 + 16 + 760
    RX0, RX1 = CX1 + 16, WX1 - 16

    # ================= LEFT: character (off-hand column right of the preview)
    panel(im, (LX0, CY0, LX1, CY1), "Character")
    text(im, (LX1 - 14, CY0 + 18), "Islander", font("bodyb", 15), PAL["text"], "rm")
    ey = CY0 + 42
    pitch = 92
    lx = LX0 + 14
    for i, (nm, ic, r) in enumerate([("Head", I_ARM % "Foraging_Maple_Head", "Rare"), ("Chest", I_ARM % "Foraging_Maple_Chest", "Rare"),
                                     ("Hands", I_ARM % "Foraging_Maple_Hands", "Unique"), ("Legs", I_ARM % "Foraging_Maple_Legs", "Unique")]):
        slot(im, lx, ey + i * pitch, "empty", RAR[r], ic)
        caption(im, lx + 37, ey + i * pitch + 76, nm)
    rxs = LX1 - 14 - 74
    offs = [(I_ACC % "lantern-unique", "Unique", "In hand"), (I_ACC % "lantern-normal", "Normal", "Off-hand 2"),
            (None, None, "Off-hand 3"), (None, None, "Off-hand 4")]
    for i, (ic, r, cap) in enumerate(offs):
        y = ey + i * pitch
        st = "selected" if (i == 0 and mode == "craft") else "empty"
        slot(im, rxs, y, st, RAR.get(r), ic, ghost=g_shield(28, "#34465f"))
        caption(im, rxs + 37, y + 76, cap, A["hi"] if i == 0 else None)
    key_cap(im, rxs + 4, ey + 4, "F", small=True)
    put(im, ss_glyph(20, 20, lambda d, s: (d.rectangle((0, 0, 20 * s, 20 * s), fill=rgb("#0c1422")),
                                          d.polygon([(5 * s, 7 * s), (15 * s, 7 * s), (10 * s, 14 * s)], fill=rgb(A["hi"])))),
        rxs + 52, ey + 52)
    px0, px1 = lx + 74 + 12, rxs - 12
    py0, py1 = ey, ey + 4 * pitch - 20
    panel(im, (px0, py0, px1, py1), inset=True, c=5)
    pcx = (px0 + px1) // 2
    gl = Image.new("RGBA", (px1 - px0, py1 - py0), (0, 0, 0, 0))
    ImageDraw.Draw(gl).ellipse((30, py1 - py0 - 70, px1 - px0 - 30, py1 - py0 - 20), fill=rgb(A["base"], 110))
    gl = gl.filter(ImageFilter.GaussianBlur(12))
    reg = im.crop((px0, py0, px1, py1)).convert("RGBA")
    im.paste(Image.alpha_composite(reg, gl).convert("RGB"), (px0, py0))
    d = ImageDraw.Draw(im, "RGBA")
    base_y = py1 - 46
    for (ax, ay), (bx, by), col in [((-22, -150), (22, -108), "#d9a87e"), ((-26, -106), (26, -40), "#3a6b45"),
                                    ((-40, -104), (-28, -46), "#d9a87e"), ((28, -104), (40, -46), "#d9a87e"),
                                    ((-24, -40), (-2, 8), "#4a3a2a"), ((2, -40), (24, 8), "#4a3a2a"),
                                    ((-26, -154), (26, -136), "#5a3b22"), ((-26, -64), (26, -56), "#7a5a2a")]:
        d.rectangle((pcx + ax, base_y + ay, pcx + bx, base_y + by), fill=rgb(col), outline=rgb("#05080e"))
    d.rectangle((pcx - 12, base_y - 132, pcx - 6, base_y - 126), fill=rgb("#1a1a2a"))
    d.rectangle((pcx + 6, base_y - 132, pcx + 12, base_y - 126), fill=rgb("#1a1a2a"))
    text(im, (pcx, py0 + 16), "Player preview", font("body", 13), PAL["dim"], "mm", shadow=False)
    if mode == "craft":
        bx1 = rxs - 8
        bx0 = bx1 - 224
        by0 = ey + 6
        by1 = by0 + 166
        shadow(im, (bx0, by0, bx1, by1), 8, 200, 3)
        grad_fill(im, (bx0, by0, bx1, by1), "#16233a", "#0e1729", c=6)
        outline(im, (bx0, by0, bx1, by1), PAL["edge"], c=6)
        outline(im, (bx0 + 1, by0 + 1, bx1 - 1, by1 - 1), A["base"], c=5)
        d.polygon([(bx1, ey + 30), (bx1 + 7, ey + 37), (bx1, ey + 44)], fill=rgb(A["base"]))
        text(im, (bx0 + 12, by0 + 18), "Pick off-hand", font("headb", 16), "#ffffff", "lm")
        text(im, (bx0 + 12, by0 + 38), "Items you can hold in it", font("body", 13), PAL["dim"], "lm")
        for i, (ic, r, nm) in enumerate([(I_ACC % "lantern-unique", "Unique", "Lantern"), (I_ACC % "lantern-normal", "Normal", "Lantern"),
                                         (None, None, "Empty")]):
            sx = bx0 + 12 + i * 70
            slot(im, sx, by0 + 54, "hover" if i == 0 else "empty", RAR.get(r), ic, size=64,
                 ghost=g_x(20, "#3a5070") if ic is None else None)
            caption(im, sx + 32, by0 + 122, nm, PAL["row"])
        text(im, (bx0 + 12, by1 - 14), "F: swap to the next one", font("body", 13), PAL["action"], "lm")
    vy = ey + 4 * pitch + 2
    text(im, (lx, vy + 10), "VOID CHARMS", font("head", 14), PAL["text"], "lm", track=1.2)
    text(im, (lx + 118, vy + 10), "9 / 18", font("bodyb", 14), PAL["dim"], "lm")
    text(im, (LX1 - 30, vy + 10), "All charms", font("head", 14), A["hi"], "rm")
    put(im, g_chev(13, A["hi"]), LX1 - 28, vy + 4)
    for i, (ic, r) in enumerate([("mana-rare", "Rare"), ("health-unique", "Unique"), ("speed-legendary", "Legendary"),
                                 ("stamina-normal", "Normal"), ("feather-unique", "Unique")]):
        slot(im, lx + i * P, vy + 24, "empty", RAR[r], I_ACC % ic)
    py = vy + 24 + 74 + 12
    half = (LX1 - LX0 - 28 - 10) // 2
    for i, (cap, ic, nm, lv, r) in enumerate((("PET", I_PET % "Hawk", "Hawk", "Lv 42", "Legendary"),
                                                ("MOUNT", I_PET % "Horse", "Horse", "Lv 18", "Rare"))):
        bx = lx + i * (half + 10)
        panel(im, (bx, py, bx + half, py + 84), inset=True, c=4)
        slot(im, bx + 5, py + 5, "empty", RAR[r], ic)
        text(im, (bx + 88, py + 18), cap, font("head", 13), PAL["dim"], "lm", track=1.2)
        text(im, (bx + 88, py + 40), nm, font("bodyb", 16), RAR[r], "lm")
        text(im, (bx + 88, py + 62), lv + "  " + r, font("body", 13), PAL["text"], "lm")
    cy = py + 94
    panel(im, (lx, cy, LX1 - 14, cy + 80), inset=True, c=4)
    paste_icon(im, I_EMB % "Archer", lx + 8, cy + 8, 64)
    text(im, (lx + 84, cy + 20), "Archer", font("headb", 20), "#a8e07a", "lm")
    level_pill(im, lx + 84 + tw("Archer", font("headb", 20)) + 10, cy + 9, "Lv 23")
    bar(im, (lx + 84, cy + 58, LX1 - 26, cy + 68), 0.62, "xp", "Class XP", "1,240 / 2,000")
    vy2 = cy + 90
    for i, (nm, g, val, k, fr) in enumerate([("Health", g_heart(20, PAL["health"]), "412 / 412", "health", 1.0),
                                             ("Mana", g_drop(20, PAL["mana"]), "96 / 140", "mana", 0.69),
                                             ("Stamina", g_bolt(20, PAL["stamina"]), "100 / 100", "stamina", 1.0),
                                             ("Defense", g_shield(20, PAL["defense"]), "184", "defense", 0.46)]):
        bx = lx + (i % 2) * (half + 10)
        by = vy2 + (i // 2) * 56
        panel(im, (bx, by, bx + half, by + 48), inset=True, c=4)
        put(im, g, bx + 10, by + 7)
        text(im, (bx + 38, by + 17), nm, font("bodyb", 15), PAL["text"], "lm")
        text(im, (bx + half - 10, by + 17), val, font("headb", 16), "#ffffff", "rm")
        bar(im, (bx + 10, by + 34, bx + half - 10, by + 40), fr, k)
    sy = vy2 + 2 * 56 + 2
    panel(im, (lx, sy, LX1 - 14, sy + 34), inset=True, c=4)
    x = lx + 12
    for k, v in (("Strength", "34"), ("Crit", "12%"), ("Speed", "+8%")):
        x = rich(im, x, sy + 17, [(k + " ", font("body", 14), PAL["dim"]), (v, font("headb", 15), PAL["green"])]) + 16
    button(im, (lx, CY1 - 54, LX1 - 14, CY1 - 14), "Stats by source", "secondary")

    # ================= CENTRE
    TOP1 = 490
    if mode == "craft":
        craft_v3(im, CX0, CX1, CY0, TOP1)
        tabs, sel = POCKETS, 0
    elif mode == "mining":
        pocket_v3(im, CX0, CX1, CY0, TOP1)
        tabs, sel = POCKETS, 1
    else:
        chest_v3(im, CX0, CX1, CY0, TOP1)
        tabs, sel = [("Chest", I_HUB % "hubrow_storage")] + POCKETS, 0
    hang_tabs(im, CX0 + 8, TOP1, CX1 - 8, 38, tabs, sel, fsize=15 if len(tabs) == 7 else 14)
    IY0 = TOP1 + 46
    panel(im, (CX0, IY0, CX1, CY1))
    gx = CX0 + (CX1 - CX0 - (9 * P - 2)) // 2
    hy = IY0 + 20
    put(im, g_diamond(9, A["base"], A["hi"]), gx, hy - 4)
    text(im, (gx + 16, hy), "INVENTORY", font("head", 15), PAL["title"], "lm", track=1.5)
    up = {"craft": None, "mining": "pocket", "chest": "chest"}[mode]
    btns = [(g_sort(18, "#c2d1e2"), "Sort"), (g_arrows(18, "#c2d1e2", True, False, True), "Quick-stack"),
            (g_arrows(18, "#c2d1e2", True, True), "Put all"), (g_void(20), "Stash to Void")]
    hov = {"craft": "Stash to Void", "mining": "Quick-stack", "chest": None}[mode]
    lxh = header_icons(im, gx + 9 * P - 2, hy, btns, hover=hov)
    hint = {"craft": "up arrows go to the Void (no chest open)", "mining": "up arrows go to the Mining pocket",
            "chest": "up arrows go to the chest"}[mode]
    text(im, (lxh - 8, hy), hint, font("body", 13), PAL["dim"], "rm")
    gy = IY0 + 40
    inv = {0: (I_ENCH % "iron-ingot", 12, None), 1: (I_ENCH % "copper-ingot", 23, None), 2: (I_ENCH % "oak-log", 41, None),
           3: (I_ENCH % "maple-log", 12, None), 4: (I_FISH % "frost_cod", 6, "Normal"), 5: (I_FISH % "cinderfin", 2, "Rare"),
           6: (I_EGG % "Combat_Rare", 1, None), 8: (I_ARM % "Foraging_Oak_Chest", None, "Normal"), 9: (I_ENCH % "wheat", 128, None),
           10: (I_ENCH % "carrot", 37, None), 11: (I_ENCH % "potato", 9, None), 13: (I_GEAR % "rod-t2-iron", None, "Normal"),
           14: (I_FISH % "glass_pike", 3, "Unique"), 15: (I_ACC % "feather-normal", None, "Normal"), 18: (I_ENCH % "cobblestone", 64, None),
           19: (I_ENCH % "sand", 64, None), 20: (I_ENCH % "clay", 18, None), 22: (I_GEAR % "lure-hook-I", 4, "Normal"),
           23: (I_EGG % "Mining_Uncommon", 1, None), 26: (I_FISH % "magma_marlin", 1, "Legendary"), 27: (I_ENCH % "sap", 5, None),
           28: (I_ENCH % "fibre", 74, None), 31: (I_ARM % "Foraging_Oak_Legs", None, "Normal")}
    for i in range(36):
        it = inv.get(i)
        x, y = gx + (i % 9) * P, gy + (i // 9) * P
        if it:
            slot(im, x, y, "empty", RAR.get(it[2]), it[0], it[1])
        else:
            slot(im, x, y)
    hyb = gy + 4 * P + 8
    hot = [(I_GEAR % "rod-t3-thorium", None, "Normal"), (I_ABIL % "Archer_ArrowRain", None, None),
           (I_ABIL % "Archer_RapidFire", None, None), (I_ABIL % "Archer_HuntersNet", None, None),
           (I_ENCH % "iron-ingot", 12, None), None, (I_FISH % "frost_cod", 6, "Normal"), None, (I_ACC % "lantern-unique", None, "Unique")]
    panel(im, (gx - 6, hyb - 6, gx + 9 * P + 3, hyb + 74 + 9), inset=True, c=5)
    for i in range(9):
        it = hot[i]
        st = "selected" if i == 0 else "empty"
        if it:
            slot(im, gx + i * P, hyb, st, RAR.get(it[2]), it[0], it[1], keycap=str(i + 1))
        else:
            slot(im, gx + i * P, hyb, st, keycap=str(i + 1))
    hotbar_marker(im, gx, hyb)
    if mode == "mining":
        mini_tip(im, gx + 9 * P - 2 - 318, hy + 20, "Quick-stack", "Move items that match into the Mining pocket")
    # teleport mini hotbar (Skyy: "make the teleport row like a mini hot bar, with icons instead of names")
    ty = hyb + 74 + 12
    text(im, (gx, ty + 22), "TELEPORT", font("head", 14), PAL["dim"], "lm", track=1.2)
    tx = gx + 92
    tps = [(I_MENU2 % "MyIsland", "Island"), (I_MENU2 % "Hub", "Hub")]
    for i in range(10):
        sx = tx + i * 46
        if i < len(tps):
            slot(im, sx, ty, "hover" if i == 0 else "empty", None, tps[i][0], size=44)
        else:
            slot(im, sx, ty, "empty", size=44, ghost=g_plus(14, "#2e405c") if i == len(tps) else None)
    ex = gx + 9 * P - 2 - 44
    button(im, (ex, ty, ex + 43, ty + 43), "", "secondary", glyph=g_pencil(16, "#c2d1e2"))
    if mode == "craft":
        mini_tip(im, tx + 52, ty - 2, "Island", "Teleport to your island")
        put(im, ss_glyph(8, 14, lambda d, s: d.polygon([(8 * s, 0), (0, 7 * s), (8 * s, 14 * s)], fill=rgb(A["base"]))), tx + 45, ty + 14)

    # ================= RIGHT: compact Skills grid + skinny Right now (quests first)
    SK1 = CY0 + 186
    panel(im, (RX0, CY0, RX1, SK1), "Skills", link="Open")
    cells = SKILLS + [("Total", None, sum(s[2] for s in SKILLS))]
    cw = (RX1 - RX0 - 20) // 6
    for i, (nm, ic, lv) in enumerate(cells):
        cx = RX0 + 10 + (i % 6) * cw
        cy = CY0 + 40 + (i // 6) * 72
        box = (cx + 2, cy, cx + cw - 3, cy + 66)
        grad_fill(im, box, "#152138", "#101a2b", c=4)
        outline(im, box, "#22324b", c=4)
        if ic:
            paste_icon(im, ic, cx + cw // 2 - 18, cy + 5, 36)
            text(im, (cx + cw // 2, cy + 54), "Lv %d" % lv, font("headb", 14), PAL["xp"], "mm")
            bar(im, (cx + 8, cy + 44, cx + cw - 9, cy + 46), ((lv * 37) % 100) / 100.0, "xp")
        else:
            put(im, g_diamond(30, PAL["gold"], PAL["goldHi"]), cx + cw // 2 - 15, cy + 8)
            text(im, (cx + cw // 2, cy + 54), str(lv), font("headb", 15), PAL["xp"], "mm")
    RN0 = SK1 + 12
    panel(im, (RX0, RN0, RX1, CY1), "Right now", link="Quests")
    y = RN0 + 40
    text(im, (RX0 + 14, y + 8), "QUEST", font("head", 13), PAL["dim"], "lm", track=1.5)
    text(im, (RX1 - 14, y + 8), "Tracked", font("bodyb", 13), A["hi"], "rm")
    y += 20
    qb = (RX0 + 10, y, RX1 - 10, y + 176)
    panel(im, qb, inset=True, c=5)
    put(im, g_quest(22, PAL["action"]), RX0 + 20, y + 10)
    text(im, (RX0 + 50, y + 18), "The Farming Island", font("headb", 16), PAL["action"], "lm")
    text(im, (RX0 + 50, y + 38), "Story  -  Chapter 2", font("body", 13), PAL["dim"], "lm")
    steps = [(True, "Talk to the Farmer", ""), (True, "Harvest Wheat", "20 / 20"), (False, "Travel to the Farming island", "240 m")]
    sy2 = y + 62
    for done, s, r in steps:
        if done:
            put(im, g_check(16, PAL["green"]), RX0 + 22, sy2 - 8)
            text(im, (RX0 + 46, sy2), s, font("body", 14), PAL["dim"], "lm")
            text(im, (RX1 - 22, sy2), r, font("headb", 14), PAL["green"], "rm")
        else:
            put(im, g_tri(16, A["base"]), RX0 + 22, sy2 - 8)
            text(im, (RX0 + 46, sy2), s, font("bodyb", 14), "#ffffff", "lm")
            text(im, (RX1 - 22, sy2), r, font("headb", 14), A["hi"], "rm")
        sy2 += 24
    rich(im, RX0 + 22, sy2 + 6, [("Reward ", font("body", 13), PAL["dim"]), ("500 coins", font("bodyb", 13), "#ffd76a"),
                                 ("  120 Farming XP", font("bodyb", 13), PAL["xp"])])
    y = qb[3] + 8
    rows_q = [(I_WARP % "Fishing", "Daily:", "Catch 20 fish", PAL["action"], (12, 20)),
              (I_WARP % "Mining", "Weekly:", "Mine 500 ore", PAL["action"], (312, 500)),
              (I_FISH % "lost_luggage_grouper", "Side:", "Lost Luggage", PAL["action"], (2, 5))]
    rows_t = [(I_WARP % "Foraging", "11", "points in Foraging tree", PAL["xp"]), (I_WARP % "Mining", "5", "points in Mining tree", PAL["xp"]),
              (I_EMB % "Archer", "2", "points in Archer tree", PAL["xp"]), (I_EGG % "Combat_Rare", "Egg:", "Rare Combat - hatch", PAL["green"]),
              (I_ENCH % "iron-ingot", "Furnace:", "64 Iron Ingot ready", PAL["green"]),
              (I_HUB % "market_bazaar", "Bazaar:", "2 orders filled", PAL["green"]), (None, "Mail:", "2 new letters", PAL["text"])]

    def skinny(y, ic, tag, msg, tc, prog=None):
        row(im, (RX0 + 10, y, RX1 - 10, y + 27), "normal")
        if ic:
            paste_icon(im, ic, RX0 + 16, y + 2, 24)
        else:
            put(im, g_envelope(18, "#c2d1e2"), RX0 + 19, y + 5)
        rich(im, RX0 + 46, y + 14, [(tag + " ", font("bodyb", 14), tc), (msg, font("body", 14), PAL["row"])])
        if prog:
            text(im, (RX1 - 32, y + 14), "%d / %d" % prog, font("headb", 14), PAL["xp"], "rm")
        put(im, g_chev(13, "#7f93a6"), RX1 - 27, y + 8)
        return y + 30
    for r_ in rows_q:
        y = skinny(y, *r_)
    y += 6
    text(im, (RX0 + 14, y + 8), "TO DO", font("head", 13), PAL["dim"], "lm", track=1.5)
    y += 20
    for r_ in rows_t:
        y = skinny(y, *r_)
    text(im, ((RX0 + RX1) // 2, CY1 - 18), "Click a row to go there", font("body", 13), PAL["dim"], "mm")

    hy2 = 1044
    hints = [("LMB", "Take"), ("RMB", "Take one"), ("Shift", "Move"), ("1-9", "To hotbar"), ("Q", "Drop"),
             ("F", "Swap off-hand"), ("Tab / Esc", "Close")]
    fh = font("body", 15)
    total = sum(max(22, tw(k, font("headb", 14)) + 10) + 6 + tw(v, fh) + 26 for k, v in hints)
    x = (W - total) // 2
    for k, v in hints:
        w = key_cap(im, x, hy2 - 11, k)
        text(im, (x + w + 6, hy2), v, fh, "#aebfd3", "lm")
        x += w + 6 + tw(v, fh) + 26
    return im


# ----------------------------------------------------------------------------------------------------------------- theme sheet

def label(im, x, y, s, size_txt=None):
    text(im, (x, y), s, font("bodyb", 14), "#c2d1e2", "la")
    if size_txt:
        text(im, (x, y + 18), size_txt, font("body", 13), "#7f93a6", "la")


def section(im, y, title, sub=None, W=2000):
    taper_line(im, 40, W - 40, y, PAL["gold"], 200, 0.9)
    put(im, g_diamond(13, A["base"], A["hi"]), 40, y + 14)
    text(im, (62, y + 21), title.upper(), font("headb", 22), PAL["title"], "lm", track=1.5)
    if sub:
        text(im, (62 + tw(title.upper(), font("headb", 22), 1.5) + 18, y + 22), sub, font("body", 15), PAL["dim"], "lm")
    return y + 50


def make_sheet():
    set_accent("Sky Azure")
    W, H = 2000, 3140
    im = Image.new("RGB", (W, H), rgb(PAL["screen"])[:3])
    grad_fill(im, (0, 0, W - 1, H - 1), "#0a1120", "#060a12")
    # header
    text(im, (40, 30), "SKYWYNN UI THEME  \"SKYGLASS\"  -  DRAFT V1", font("headb", 34), PAL["title"], "la", track=1)
    text(im, (40, 76), "Plan P0b (research/Inventory-Screen-Plan.md). Skyy 2026-11-12: \"Custom look\" for every SkyWynn menu; "
                       "11-14: \"try to make the menus simple and easy to understand, look good\".", font("body", 16), PAL["text"])
    text(im, (40, 100), "Dark navy glass panels, a thin gold trim (the Sky Window family Skyy approved), ONE accent colour: Sky Azure. "
                        "All sizes in px = UI units at 1080p, UI scale 1 (textures ship @2x). Stand-in fonts.", font("body", 16), PAL["dim"])
    y = 140
    # ---- palette
    y = section(im, y, "Palette", "one accent, dark panels, green = ready, red = missing")
    sw = [("Accent", A["base"], "selected, primary, focus"), ("Accent hi", A["hi"], "links, highlights"),
          ("Accent lo", A["lo"], "hover lines"), ("Button top", A["btnTop"], "primary face"), ("Button bot", A["btnBot"], "primary face"),
          ("Gold trim", PAL["gold"], "frame + ornament"), ("Gold hi", PAL["goldHi"], "trim light"),
          ("Window", PAL["window"], "page body"), ("Panel", PAL["panel"], "panels"), ("Inset", PAL["inset"], "wells, fields"),
          ("Line", PAL["line"], "panel borders"), ("Title", PAL["title"], "titles"), ("Text", PAL["text"], "body text"),
          ("Row name", PAL["row"], "names, values"), ("Dim", PAL["dim"], "minor info"), ("Ready", PAL["green"], "have / ready / +"),
          ("Missing", PAL["red"], "need / danger / -"), ("Level / XP", PAL["xp"], "levels, XP"), ("Action", PAL["action"], "Click: ..."),
          ("Health", PAL["health"], "vital"), ("Mana", PAL["mana"], "vital"), ("Stamina", PAL["stamina"], "vital"),
          ("Defense", PAL["defense"], "vital")]
    per = 12
    cw = (W - 80) // per
    for i, (nm, hx, use) in enumerate(sw):
        x = 40 + (i % per) * cw
        yy = y + (i // per) * 112
        grad_fill(im, (x, yy, x + cw - 14, yy + 48), hx, hx, c=4)
        outline(im, (x, yy, x + cw - 14, yy + 48), "#000000", c=4)
        hline(im, x + 4, x + cw - 18, yy + 1, "#ffffff", 50)
        text(im, (x, yy + 56), nm, font("bodyb", 14), PAL["row"])
        text(im, (x, yy + 74), hx.upper(), font("headb", 14), PAL["text"])
        text(im, (x, yy + 91), use, font("body", 13), PAL["dim"])
    y += 2 * 112 + 14

    # ---- window frame
    y = section(im, y, "Window frame + title plate", "9-slice: 32 px corners, 1 px stretch strips; ornament + plate are separate textures")
    window_frame(im, (40, y + 30, 640, y + 330), "Void Charms")
    panel(im, (64, y + 70, 616, y + 306), "Panel title", link="Link")
    text(im, (80, y + 120), "Body text on a panel - #c2d1e2", font("body", 16), PAL["text"])
    text(im, (80, y + 144), "Row name / value - #d6e4ee", font("bodyb", 16), PAL["row"])
    text(im, (80, y + 168), "Minor info - #7f93a6", font("body", 15), PAL["dim"])
    panel(im, (80, y + 196, 600, y + 290), inset=True)
    text(im, (96, y + 220), "Inset panel (well) - lists, fields, previews", font("body", 15), PAL["text"])
    label(im, 40, y + 344, "Window 600 x 300 (any size)", "Frame: edge 1 + gold 2 + inner 1 px; chamfer 10; corner bracket 26 px + 11 px accent gem")
    # zoomed corner with 9-slice cuts
    zx, zy = 700, y + 30
    crop = im.crop((40, y + 30, 40 + 72, y + 30 + 72)).resize((288, 288), Image.NEAREST)
    im.paste(crop, (zx, zy))
    d = ImageDraw.Draw(im, "RGBA")
    for k in (32 * 4,):
        for i in range(0, 288, 8):
            d.line([(zx + k, zy + i), (zx + k, zy + i + 4)], fill=(255, 90, 90, 230))
            d.line([(zx + i, zy + k), (zx + i + 4, zy + k)], fill=(255, 90, 90, 230))
    outline(im, (zx - 1, zy - 1, zx + 288, zy + 288), "#33496b")
    label(im, zx, zy + 298, "Corner x4, 9-slice cut (red) at 32 px", "Border 32 UI; edges + centre stretch")
    # title plates
    title_plate(im, 1300, y + 70, "Inventory")
    title_plate(im, 1300, y + 150, "Server Setup")
    label(im, 1100, y + 196, "Title plate: height 32, ends 32 px (9-slice H 32 / V 0)", "Bahnschrift-like caps, tracking 2; gems in the accent")
    # separators
    taper_line(im, 1100, 1700, y + 270, PAL["gold"], 220, 0.5)
    label(im, 1100, y + 282, "Separator: 1 px gold, fades at both ends (texture 64 x 2, H border 16)")
    y += 400

    # ---- tabs
    y = section(im, y, "Top tab bar", "12 tabs, 117 x 54 each at 1080p (124 here); selected tab joins the page below")
    grad_fill(im, (40, y, 1000, y + 66), "#0a111e", "#0c1525", c=4)
    hline(im, 40, 1000, y + 62, PAL["lineHi"])
    tab(im, (52, y + 8, 175, y + 61), "Inventory", TABS[0][1], "selected")
    tab(im, (178, y + 8, 301, y + 61), "Skills", TABS[1][1], "hover")
    tab(im, (304, y + 8, 427, y + 61), "Class", TABS[2][1], "pressed")
    tab(im, (430, y + 8, 553, y + 61), "Pets", TABS[3][1], "normal")
    tab(im, (556, y + 8, 679, y + 61), "Collections", TABS[4][1], "normal")
    for i, s in enumerate(("Selected", "Hover", "Pressed", "Normal", "Normal")):
        label(im, 52 + i * 126, y + 74, s, "124 x 54")
    text(im, (1040, y + 20), "Icon spot: 24 x 24 left of the label (our hub-tab icons, greyed when not selected).",
         font("body", 15), PAL["text"])
    text(im, (1040, y + 44), "Selected: 3 px accent top line + glow, lighter face, no bottom line.", font("body", 15), PAL["text"])
    # sub tabs (bag tabs) + chips
    sy = y + 120
    for i, (nm, ic) in enumerate((("Inventory", I_HUB % "hubrow_storage"), ("Mining", I_WARP % "Mining"),
                                  ("Foraging", I_WARP % "Foraging"))):
        tab(im, (40 + i * 100, sy, 137 + i * 100, sy + 36), nm, ic, "selected" if i == 0 else ("hover" if i == 1 else "normal"), 15)
    hline(im, 40, 340, sy + 36, PAL["lineHi"])
    label(im, 40, sy + 46, "Bag tabs (sub-tab row)", "98 x 36, same states")
    x = 420
    for i, nm in enumerate(("All", "Hand", "Workbench", "Armor")):
        x += chip(im, x, sy + 2, nm, i == 0, 30) + 5
    label(im, 420, sy + 46, "Page chips (crafting pages, filters)", "height 30, width = text + 24")
    y += 220

    # ---- buttons
    y = section(im, y, "Buttons", "40 px high (small 32); chamfer 5; 9-slice border 8")
    states = ("normal", "hover", "pressed", "disabled")
    for r, (kind, nm) in enumerate((("primary", "Craft"), ("secondary", "Stats by source"), ("danger", "Delete"))):
        text(im, (40, y + 20 + r * 66), kind.capitalize(), font("headb", 16), PAL["text"], "lm")
        for i, st in enumerate(states):
            x = 180 + i * 230
            button(im, (x, y + r * 66, x + 199, y + r * 66 + 39), nm, kind, st)
            if r == 2:
                label(im, x, y + 3 * 66 - 8, st.capitalize(), "200 x 40")
    # small + icon buttons
    bx = 1140
    button(im, (bx, y, bx + 136, y + 39), "", "secondary")
    paste_icon(im, I_HUB % "world_island", bx + 14, y + 8, 24)
    text(im, (bx + 46, y + 21), "Island", font("head", 16), PAL["row"], "lm")
    button(im, (bx + 146, y, bx + 190, y + 39), "", "secondary", glyph=g_plus(16, "#9fb3cc"))
    button(im, (bx + 200, y, bx + 304, y + 39), "Edit", "secondary", glyph=g_pencil(16, "#c2d1e2"))
    button(im, (bx + 314, y, bx + 354, y + 39), "", "secondary", glyph=g_x(18, "#d6e4ee"))
    button(im, (bx + 364, y, bx + 404, y + 39), "", "secondary", "hover", glyph=g_x(18, "#ffffff"))
    label(im, bx, y + 48, "Icon + label (teleport), add, Edit, Close (40 x 40)", "icon 24 / glyph 16")
    button(im, (bx, y + 98, bx + 104, y + 129), "Sort", "secondary", fsize=15)
    button(im, (bx + 114, y + 98, bx + 254, y + 129), "Ready", "green", fsize=15)
    label(im, bx, y + 138, "Small 32 high; green = a 'Ready / Collect' state")
    y += 3 * 66 + 50

    # ---- slots
    y = section(im, y, "Item slots", "slot 74 + spacing 2 = 76 pitch (vanilla ItemGrid); icon 64; rarity = frame colour + inner glow + corner gem")
    for i, (st, nm) in enumerate((("empty", "Empty"), ("hover", "Hover"), ("selected", "Selected"))):
        slot(im, 40 + i * 110, y + 10, st)
        label(im, 40 + i * 110, y + 94, nm, "74 x 74")
    slot(im, 380, y + 10, "empty", RAR["Unique"], I_ENCH % "iron-ingot", 64)
    slot(im, 380 + 125, y + 10, "selected", RAR["Rare"], I_ACC % "mana-rare")
    slot(im, 380 + 250, y + 10, "empty", None, None, ghost=g_shield(30, "#2c3c57"))
    slot(im, 380 + 375, y + 10, "empty", RAR["Normal"], I_GEAR % "rod-t3-thorium", keycap="1")
    slot(im, 380 + 500, y + 10, "empty", RAR["Normal"], I_FISH % "frost_cod", 6, dim=True)
    for i, (nm, sz) in enumerate((("Stack count", "bold 16"), ("Selected + rarity", "accent wins"), ("Slot hint", "off-hand / utility"),
                                  ("Hotbar key cap", "18 x 18"), ("Can't use (dimmed)", "icon 45 %"))):
        label(im, 380 + i * 125, y + 94, nm, sz)
    # hotbar marker
    hx = 1040
    panel(im, (hx - 6, y + 4, hx + 3 * 74 + 5, y + 90), inset=True, c=5)
    for i in range(3):
        slot(im, hx + i * 74, y + 10, "selected" if i == 1 else "empty", RAR["Normal"] if i == 1 else None,
             I_GEAR % "rod-t2-iron" if i == 1 else None, keycap=str(i + 1))
    hotbar_marker(im, hx + 74, y + 10)
    label(im, hx, y + 100, "Hotbar active marker", "selected frame + 28 x 6 notch under the slot")
    # key caps
    kx = 1360
    x = kx
    for k in ("1", "Q", "Shift", "Tab / Esc", "LMB"):
        x += key_cap(im, x, y + 20, k) + 10
    label(im, kx, y + 54, "Key cap", "22 high (18 in slots), width = text + 10; text bold 14 / 13")
    y += 150
    # rarity frames
    text(im, (40, y), "Gear rarity ladder (LOCKED, tools/skyyui.py RARITY + Untiered)", font("headb", 17), PAL["text"], "la")
    gicons = [I_ACC % "health-normal", I_ACC % "health-unique", I_ACC % "health-rare", I_ACC % "health-legendary",
              I_FISH % "magma_marlin", I_ACC % "runic-legendary", I_ARM % "Foraging_Crystalwood_Chest", I_ENCH % "onyxium-ingot"]
    for i, (nm, hx_) in enumerate(GEAR_RARITY):
        x = 40 + i * 120
        slot(im, x, y + 30, "empty", hx_, gicons[i])
        text(im, (x, y + 114), nm, font("bodyb", 15), hx_)
        text(im, (x, y + 133), hx_.upper(), font("body", 13), PAL["dim"])
    qx = 1040
    text(im, (qx, y), "Pets / eggs / vanilla qualities (Style Guide 15)", font("headb", 17), PAL["text"], "la")
    qicons = [I_EGG % "Combat_Common", I_EGG % "Combat_Uncommon", I_EGG % "Combat_Rare", I_EGG % "Combat_Epic",
              I_EGG % "Combat_Legendary", I_EGG % "Combat_Mythic"]
    for i, (nm, hx_) in enumerate(QUALITY_RARITY):
        x = qx + i * 120
        slot(im, x, y + 30, "empty", hx_, qicons[i])
        text(im, (x, y + 114), nm, font("bodyb", 15), mix(hx_, "#ffffff", 0.25))
        text(im, (x, y + 133), hx_.upper(), font("body", 13), PAL["dim"])
    y += 170
    text(im, (40, y), "Frame = rarity colour at 62 % over the panel (2 px) + 7 px inner glow; gem 11 x 11 top right; a 1 px dark edge keeps it crisp on any "
                      "background. Readable at 74 px (shown 1:1). v2 mockups use the 76 px pitch.", font("body", 15), PAL["dim"])
    y += 40

    # ---- controls
    y = section(im, y, "Controls", "toggle, search, scrollbar, bars, level pill, list rows")
    toggle(im, 40, y + 8, True, "Craftable only")
    toggle(im, 40, y + 48, False, "Craftable only")
    label(im, 40, y + 84, "Toggle on / off", "44 x 24; knob 18; label 15 semibold")
    search_box(im, (300, y + 4, 640, y + 35), "Search recipes...")
    search_box(im, (300, y + 46, 640, y + 77), focused=True, value="mana")
    label(im, 300, y + 84, "Search box (empty / focused)", "height 32, inset, icon 16, caret in accent")
    panel(im, (700, y, 860, y + 120), inset=True)
    scrollbar(im, 840, y + 6, y + 114, y + 10, y + 56)
    scrollbar(im, 820, y + 6, y + 114, y + 40, y + 86, hover=True)
    label(im, 700, y + 128, "Scrollbar", "8 wide; hover = accent")
    bx = 920
    bar(im, (bx, y + 22, bx + 300, y + 32), 0.62, "xp", "Class XP", "1,240 / 2,000")
    bar(im, (bx, y + 62, bx + 300, y + 68), 1.0, "health")
    bar(im, (bx, y + 80, bx + 300, y + 86), 0.69, "mana")
    bar(im, (bx, y + 98, bx + 300, y + 104), 0.8, "stamina")
    bar(im, (bx, y + 116, bx + 300, y + 124), 0.75, "accent", segs=4)
    label(im, bx, y + 132, "Progress bars", "XP 10 high (gold); vitals 6 high; accent = space / progress")
    lx = 1290
    level_pill(im, lx, y + 10, "Lv 23")
    level_pill(im, lx + 70, y + 10, "31")
    level_pill(im, lx + 116, y + 10, "Lv 100")
    label(im, lx, y + 40, "Level pill", "height 22, width = text + 18")
    for i, st in enumerate(("normal", "hover", "selected")):
        row(im, (lx, y + 82 + i * 46, lx + 420, y + 122 + i * 46), st)
        paste_icon(im, I_WARP % "Foraging", lx + 8, y + 86 + i * 46, 32)
        text(im, (lx + 50, y + 102 + i * 46), "11 unspent points in Foraging", font("body", 16), PAL["row"], "lm")
        put(im, g_chev(18, A["hi"] if st != "normal" else "#7f93a6"), lx + 392, y + 93 + i * 46)
        text(im, (lx + 430, y + 102 + i * 46), st.capitalize(), font("bodyb", 14), PAL["text"], "lm")
    text(im, (lx, y + 228), "List row: height 40-52, chamfer 3; selected = 3 px accent bar + tint", font("body", 13), PAL["dim"])
    y += 270

    # ---- tooltip
    y = section(im, y, "Tooltip", "sectioned layout; Style Guide 15 colours; name, then the header block, then stats")
    th = tooltip(im, 40, y + 10)
    notes = [
        ("Name", "rarity colour, bold 20", RAR["Legendary"]),
        ("Header block", "slot, tier, class, type, speed, rarity, level (Skyy 10-24 order)", PAL["text"]),
        ("Stat values", "green #4fd88a helps / red #ff6b6b costs; number first, bold", PAL["green"]),
        ("Stat names", "soft white #d6e4ee", PAL["row"]),
        ("Level / XP", "gold #e8c25a", PAL["xp"]),
        ("Tier tag", "tier colour from tools/tier_tags.py", "#e0675a"),
        ("Minor info", "dim #7f93a6, last", PAL["dim"]),
        ("Actions", "yellow #ffcc00 ('Click: ...')", PAL["action"]),
        ("Frame", "rarity hairline + top glow + 2 corner gems; 9-slice border 12", PAL["text"]),
        ("Width", "372 (fits 36 characters of body text at 15 px)", PAL["text"]),
    ]
    ny = y + 24
    for k, v, c in notes:
        text(im, (460, ny), k, font("bodyb", 16), c, "lm")
        text(im, (640, ny), v, font("body", 15), PAL["text"], "lm")
        ny += 30
    # a small sample row: inputs have / need
    panel(im, (1300, y + 10, 1960, y + 200), "Recipe inputs (have / need)")
    iy = y + 50
    for ic, nm, have, need in ((I_ACC % "mana-unique", "Mana Charm (Unique)", 1, 1),
                               (I_ENCH % "cobalt-ingot", "Enchanted Cobalt Ingot", 7, 4), (I_ENCH % "sap", "Enchanted Sap", 5, 8)):
        paste_icon(im, ic, 1314, iy, 32)
        text(im, (1356, iy + 16), nm, font("body", 16), PAL["row"], "lm")
        text(im, (1940, iy + 16), "%d / %d" % (have, need), font("headb", 17), PAL["green"] if have >= need else PAL["red"], "rm")
        iy += 40
    text(im, (1314, iy + 14), "Missing 3 Enchanted Sap", font("bodyb", 15), PAL["red"], "lm")
    y += th + 40
    text(im, (40, y), "SkyWynn concept art - original pixels drawn by research/ui-theme-art/make_ui_theme.py. Item pictures are our own "
                      "SkyWynn icons (art/, research/cloud/*-art/). No vanilla Hytale file used.", font("body", 14), PAL["dim"])
    return im.crop((0, 0, W, y + 40))


# ----------------------------------------------------------------------------------------------------------------- accent options

def make_accents():
    W, H = 1890, 470
    im = Image.new("RGB", (W, H))
    grad_fill(im, (0, 0, W - 1, H - 1), "#0a1120", "#060a12")
    text(im, (30, 26), "ACCENT OPTIONS  -  same parts, three accents (pick one)", font("headb", 24), PAL["title"], "la", track=1)
    for k, name in enumerate(("Sky Azure", "Sun Gold", "Aurora Teal")):
        set_accent(name)
        x0 = 30 + k * 620
        y0 = 80
        window_frame(im, (x0, y0, x0 + 590, y0 + 370))
        grad_fill(im, (x0 + 5, y0 + 8, x0 + 585, y0 + 58), "#0a111e", "#0c1525", c=4)
        hline(im, x0 + 6, x0 + 584, y0 + 58, PAL["lineHi"])
        for i, (nm, ic) in enumerate(TABS[:4]):
            tab(im, (x0 + 14 + i * 124, y0 + 12, x0 + 137 + i * 124, y0 + 57), nm, ic, "selected" if i == 0 else ("hover" if i == 2 else "normal"))
        panel(im, (x0 + 18, y0 + 74, x0 + 572, y0 + 352), "Crafting", link="Open")
        toggle(im, x0 + 32, y0 + 114, True, "Craftable only")
        search_box(im, (x0 + 226, y0 + 110, x0 + 556, y0 + 141), focused=True, value="mana")
        for i, (ic, r) in enumerate(((I_ACC % "mana-rare", "Rare"), (I_ACC % "speed-legendary", "Legendary"),
                                     (I_ENCH % "iron-ingot", None), (I_GEAR % "rod-t2-iron", "Normal"), (None, None),
                                     (None, None))):
            slot(im, x0 + 34 + i * 74, y0 + 158, "selected" if i == 0 else "empty", RAR[r] if r else None, ic)
        button(im, (x0 + 34, y0 + 252, x0 + 214, y0 + 291), "Craft", "primary")
        button(im, (x0 + 224, y0 + 252, x0 + 404, y0 + 291), "Craft", "primary", "hover")
        button(im, (x0 + 414, y0 + 252, x0 + 554, y0 + 291), "x10", "secondary")
        bar(im, (x0 + 34, y0 + 318, x0 + 300, y0 + 326), 0.6, "accent", segs=4)
        tag = "%d. %s %s" % (k + 1, name, A["base"].upper()) + ("  (pick)" if k == 0 else "")
        text(im, (x0 + 320, y0 + 322), tag, font("headb", 17), A["hi"], "lm")
    set_accent("Sky Azure")
    return im


def main():
    out = {"theme-sheet.png": make_sheet, "inventory-mockup-v1.png": make_mockup_v1,
           "inventory-mockup-v2.png": lambda: make_mockup("craft"), "inventory-mockup-mining-v2.png": lambda: make_mockup("mining"),
           "inventory-mockup.png": lambda: make_mockup_v3("craft"), "inventory-mockup-mining.png": lambda: make_mockup_v3("mining"),
           "inventory-mockup-chest.png": lambda: make_mockup_v3("chest"),
           "accent-options.png": make_accents}
    only = sys.argv[1:]
    for fn, maker in out.items():
        if only and fn not in only:
            continue
        im = maker()
        im.save(os.path.join(HERE, fn), optimize=True)
        print("wrote", fn, im.size)


if __name__ == "__main__":
    main()
