"""make_metal_items - SkyWynn NEW-METAL item art (Lead, Dusk, Chromium, Azurvane, Slag, Cinder, Titanium, Lumen + Electrum bar):
ores, bars, Enchanted ingots, the 9 metal-ladder weapon families, the 10 vanilla metal weapon families (sword, longsword, axe, battleaxe,
mace, club, daggers, spear, shortbow, shield - round A2) and the 5 forever tools. Art only - nothing here is wired into a mod.

Why a generator: the repo is PUBLIC and every output is a recolour / re-texture of vanilla art (or of Quirk's PRIVATE tool builds), so
no pixels are committed. This file holds only code + palette numbers (the hex values of Quirk's approved palette cards,
SkyWynn-PRIVATE-art/metal-art/metal-palettes/palettes.md, Skyy approved 2026-10-17). It reads Assets.zip (read-only) and the private
tool folder at RUN time and writes everything into the git-ignored models-local/art/metals/<family>/.

How each family is made (the way the repo already makes the vanilla-metal versions):
  * ore / bar  - the zone's vanilla base ore / ingot texture + its vanilla icon, gradient-mapped onto the new metal (SA.recolor /
                 SA.recolor_icon, the icon kept pixel-exact so no renderer drift), + the metal's pattern. Electrum = vanilla Gold +
                 Silver ingot colours mixed 50/50 (computed from Assets.zip, no hex).
  * Enchanted  - tools/skyyench.py's own "shiny copy" (_shine) of our new bar (collections: base metals only = Lead, Chromium, Slag, Titanium).
  * weapons    - the EXISTING family generators (tools/art/make_kunai / make_staffs / make_spellbooks / make_soulcage / make_fists +
                 skyyart's wand recipe) run with the zone's vanilla base tier as the SHAPE donor (Lead / Dusk -> Thorium, Chromium /
                 Azurvane -> Cobalt, Slag / Cinder -> Adamantite, Titanium / Lumen -> Mithril) while skyyart's colour sources
                 (metal_gradient / band_gradient / gem_gradient) are swapped for the new metal's palette card: metal = base / shade /
                 highlight, trim = the card's trim (brass, cobalt, anodized blue / purple ...), gem = the card's glow colour.
                 The metal texels are found by running the same generator twice (second run with a hue-rotated metal gradient: every
                 texel that changes is metal) and get the card's pattern (veins, Damascus bands, embers, strata, brushed edges ...).
                 Crossbow = the vanilla IRON crossbow, grey texels inside its metal nodes (SkyyArmory 0.1.30's own mask rule), nothing
                 from More Crossbow Tiers. Great Shield = the donor's vanilla shield (plates -> metal, frame -> trim, back kept).
  * vanilla families (A2) - the donor tier's vanilla Weapon_<Family>_<donor> (model by path), texture + icon split into colour classes by
                 hue (vw_rule: donor metal / accent metal / gem; wood, leather, rope and outlines kept) and re-coloured (recolor_item).
  * tools      - Quirk's approved Titanium (base ores) / Lumen (alloys) builds re-coloured per metal (Titanium + Lumen themselves are
                 Quirk's, untouched). Pickaxe / hatchet / can icons = the vanilla Mithril pickaxe / hatchet and the vanilla can icon
                 re-coloured; multitool / harvester icons = render_icon of Quirk's model (they have no vanilla icon).
Icons: vanilla-model families keep the vanilla icon geometry (recolor_icon); own-model families use their generator's own renderer.

Run:   python tools/art/make_metal_items.py [--only ores,bars,ench,wand,...] [--check]
Out:   models-local/art/metals/<family>/Common/...   (git-ignored, vanilla-derived - never commit)
       models-local/art/metals/_sheets/<batch>.png   contact sheets (rows = metals)
       models-local/art/metals/manifest.json         every item: proposed id, output paths, base asset, palette
--check: re-runs everything in memory and compares bytes (deterministic), and validates sizes / alpha / icon frames.
Deterministic: no clocks, no randomness (hash noise only); two runs give the same bytes.
"""
import argparse
import copy
import hashlib
import json
import math
import os
import sys
import zlib
from contextlib import contextmanager

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "art"))
import skyyart as SA          # noqa: E402
import skyyench as SE         # noqa: E402  (the Enchanted "shiny copy")
import make_kunai as MK       # noqa: E402
import make_staffs as MS      # noqa: E402
import make_spellbooks as MB  # noqa: E402
import make_soulcage as MC    # noqa: E402
import make_fists as MF       # noqa: E402
import make_fishing as MFI    # noqa: E402  (fit_props only)

OUT = os.path.join(ROOT, "models-local", "art", "metals")
PRIVATE_TOOLS = os.environ.get("SKYWYNN_PRIVATE_TOOLS", os.path.join(os.path.dirname(ROOT), "SkyWynn-PRIVATE-art", "metal-art",
                                                                       "Tools-PRIVATE"))
ICON_DIR = "Common/Icons/ItemsGenerated"


def hx(s):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


# ===================================================================================================== the palette cards (numbers only)
# zone, ore (has an ore) / alloy, shape donor (the zone's vanilla base tier), card colours, pattern + its colours
METALS = ("Lead", "Dusk", "Chromium", "Azurvane", "Slag", "Cinder", "Titanium", "Lumen")
ORES = ("Lead", "Chromium", "Slag", "Titanium")
SPEC = {
    "Lead":     {"zone": 2, "kind": "ore", "donor": "Thorium", "base": "#606672", "shade": "#3D424C", "hi": "#A6ACB6", "trim": "#8C7446",
                 "glow": None, "pattern": "dents"},
    "Dusk":     {"zone": 2, "kind": "alloy", "donor": "Thorium", "base": "#4C4C5A", "shade": "#312F3C", "hi": "#8F8F9A", "trim": "#8C7446",
                 "glow": "#EAF4E3", "vein": "#81C677", "patina": "#4E6454", "pattern": "veins"},
    "Chromium": {"zone": 3, "kind": "ore", "donor": "Cobalt", "base": "#AEBBCA", "shade": "#69778B", "hi": "#ECEFF1", "trim": "#344C82",
                 "glow": None, "pattern": "streaks"},
    "Azurvane": {"zone": 3, "kind": "alloy", "donor": "Cobalt", "base": "#273C6D", "shade": "#17264A", "hi": "#657FB2", "trim": "#B5C0CF",
                 "glow": "#EEF4F4", "band": "#BBCADA", "pattern": "damascus_bands"},
    "Slag":     {"zone": 4, "kind": "ore", "donor": "Adamantite", "base": "#3B3739", "shade": "#272426", "hi": "#7C7775", "trim": "#54545C",
                 "glow": "#F28D41", "pattern": "embers"},
    "Cinder":   {"zone": 4, "kind": "alloy", "donor": "Adamantite", "base": "#221D1E", "shade": "#171314", "hi": "#595150", "trim": "#414148",
                 "glow": "#F4B15D", "red": "#A23220", "crack": "#E26530", "pattern": "strata"},
    "Titanium": {"zone": 5, "kind": "ore", "donor": "Mithril", "base": "#5F6A7C", "shade": "#2F3D57", "hi": "#A6A9C6", "trim": "#426EB4",
                 "glow": "#BDA8F4", "edge": "#4672B8", "centre": "#603C96", "pattern": "brushed"},
    "Lumen":    {"zone": 5, "kind": "alloy", "donor": "Mithril", "base": "#607088", "shade": "#343E4D", "hi": "#A4B5CA", "trim": "#7551A9",
                 "glow": "#CFF2F4", "line": "#DDE1E9", "core": "#F4F4F4", "pattern": "damascus_lines"},
}
# gem / crystal ramps (dark -> light) around each card's glow colour; None = keep the donor tier's vanilla staff gem (no glow on the card)
GEM = {
    "Lead": None, "Chromium": None,
    "Dusk": ("#2E4A33", "#4E6454", "#81C677", "#B8E0B0", "#EAF4E3"),
    "Azurvane": ("#17264A", "#3D5C93", "#8FA6CC", "#BBCADA", "#EEF4F4"),
    "Slag": ("#4A1A0C", "#A3401A", "#E26A2A", "#F28D41", "#FFD9A8"),
    "Cinder": ("#3A0E0A", "#A23220", "#E26530", "#F4B15D", "#FFE6B8"),
    "Titanium": ("#2A1F4A", "#603C96", "#8C72D0", "#BDA8F4", "#EFE8FF"),
    "Lumen": ("#343E4D", "#7551A9", "#9FD8E0", "#CFF2F4", "#F4FFFF"),
}
SPARKLE = {"Dusk": 0.020, "Azurvane": 0.015, "Cinder": 0.0, "Lumen": 0.015, "Titanium": 0.0, "Electrum": 0.010}


def mixc(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def mulc(a, f):
    return tuple(a[i] * f for i in range(3))


def ramp_grad(stops, steps=24):
    """stops: [(t, rgb)] -> a SA gradient (tuple of `steps` rgb floats)."""
    out = []
    for i in range(steps):
        t = i / float(steps - 1)
        for j in range(len(stops) - 1):
            t0, c0 = stops[j]
            t1, c1 = stops[j + 1]
            if t0 <= t <= t1:
                out.append(mixc(c0, c1, (t - t0) / (t1 - t0) if t1 > t0 else 0.0))
                break
    return tuple(out)


def metal_grad(m):
    s = SPEC[m]
    sh, b, hi = hx(s["shade"]), hx(s["base"]), hx(s["hi"])
    return ramp_grad([(0.0, mulc(sh, 0.55)), (0.25, sh), (0.55, b), (0.82, hi), (1.0, mixc(hi, (255, 255, 255), 0.45))])


def trim_grad(m):
    t = hx(SPEC[m]["trim"])
    return ramp_grad([(0.0, mulc(t, 0.35)), (0.3, mulc(t, 0.7)), (0.6, t), (0.85, mixc(t, (255, 255, 255), 0.35)),
                      (1.0, mixc(t, (255, 255, 255), 0.6))])


def gem_grad(m):
    g = GEM.get(m)
    return None if g is None else ramp_grad([(i / 4.0, hx(c)) for i, c in enumerate(g)])


def electrum_grad(z):
    gold = SA.palette_from([SA._read(z, "Resources/Materials/Ingot_Textures/Gold.png")])
    silver = SA.palette_from([SA._read(z, "Resources/Materials/Ingot_Textures/Silver.png")])
    return SA.grad_mix(gold, silver, 0.5)


def probe_grad(g):
    """the same gradient with every channel moved half way round (mod 256): every texel painted from it differs by ~128."""
    return tuple(tuple((c[k] + 128.0) % 256.0 for k in range(3)) for c in g)


def palette_note(m):
    s = SPEC.get(m)
    if not s:
        return "Electrum = vanilla Gold + Silver ingot colours 50/50 (Assets.zip at run time)"
    extra = ", ".join("%s %s" % (k, s[k]) for k in ("vein", "patina", "band", "red", "crack", "edge", "centre", "line", "core") if k in s)
    return "card Z%d %s: base %s shade %s hi %s trim %s glow %s%s; pattern %s" % (
        s["zone"], m, s["base"], s["shade"], s["hi"], s["trim"], s["glow"] or "-", ("; " + extra) if extra else "", s["pattern"])


# ===================================================================================================== deterministic noise + patterns
def h01(x, y, s=0):
    v = (x * 374761393 + y * 668265263 + s * 2147483647 + 1013904223) & 0xffffffff
    v = ((v ^ (v >> 13)) * 1274126177) & 0xffffffff
    return ((v ^ (v >> 16)) & 0xffffff) / float(0x1000000)


def vnoise(x, y, s=0):
    x0, y0 = int(math.floor(x)), int(math.floor(y))
    fx, fy = x - x0, y - y0
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a, b = h01(x0, y0, s), h01(x0 + 1, y0, s)
    c, d = h01(x0, y0 + 1, s), h01(x0 + 1, y0 + 1, s)
    return (a + (b - a) * fx) + ((c + (d - c) * fx) - (a + (b - a) * fx)) * fy


def frac(v):
    return v - math.floor(v)


def edge_dist(mask, cap=5):
    """{p: steps to the nearest texel outside the mask (0 = on the mask border)}, capped."""
    inside = set(p for p, w in mask.items() if w >= 0.5)
    dist, front = {}, []
    for (x, y) in inside:
        if any((x + dx, y + dy) not in inside for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            dist[(x, y)] = 0
            front.append((x, y))
    d = 0
    while front and d < cap:
        d += 1
        nxt = []
        for (x, y) in front:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (x + dx, y + dy)
                if q in inside and q not in dist:
                    dist[q] = d
                    nxt.append(q)
        front = nxt
    return dist


def apply_pattern(img, mask, m, seed, premul=False):
    """Paint metal m's card pattern onto the texels of `mask` ({(x, y): weight}) of Img img (in place). Pattern colours keep the
    local shading (scaled by the texel's brightness against the card base); glow colours (sparkles, embers, cracks) are emissive.
    premul: img is a premultiplied icon."""
    s = SPEC.get(m, {})
    pat = s.get("pattern")
    spark = SPARKLE.get(m, 0.0)
    if not pat and not spark:
        return img
    base_l = max(SA.luma(hx(s["base"])), 8.0) if s else 128.0
    glow = hx(s["glow"]) if s.get("glow") else (255, 246, 214)
    dist = edge_dist(mask) if pat == "brushed" else None
    ang = (seed % 7) * 0.31 + 0.4
    ca, sa = math.cos(ang), math.sin(ang)
    for (x, y), w in sorted(mask.items()):
        if w <= 0:
            continue
        r, g, b, a = img.get(x, y)
        if a == 0:
            continue
        f = (255.0 / a) if premul else 1.0
        c = (r * f, g * f, b * f)
        k = min(max(SA.luma(c) / base_l, 0.5), 1.5)
        n = c
        if pat == "dents":                        # Lead: soft dents (dull, no shine)
            d = (vnoise(x / 4.5, y / 4.5, seed) - 0.5) * 0.36
            n = mulc(c, 1.0 + d)
        elif pat == "veins":                       # Dusk: thin green vein contours + patina halo
            v = vnoise(x / 5.0, y / 5.0, seed) * 6.0 + vnoise(x / 2.5, y / 2.5, seed + 1) * 0.7
            lv, fr = int(math.floor(v)), frac(v)
            if lv % 2 == 0 and fr < 0.22:
                n = mulc(hx(s["vein"]), min(k, 1.15))
            elif lv % 2 == 0 and (fr < 0.40 or fr > 0.90):
                n = mixc(c, mulc(hx(s["patina"]), k), 0.6)
        elif pat == "streaks":                     # Chromium: mirror chrome, vertical light streaks
            v = vnoise(x / 1.6, y / 11.0, seed)
            if v > 0.62:
                n = mixc(c, hx(s["hi"]), min((v - 0.62) * 2.6, 0.85))
            elif v < 0.28:
                n = mixc(c, mulc(hx(s["shade"]), k), (0.28 - v) * 1.6)
        elif pat == "damascus_bands":              # Azurvane: smooth wavy chromium bands on dark cobalt
            ph = (y + 0.45 * x + 2.2 * math.sin(x * 0.5 + 3.0 * vnoise(x / 6.0, y / 6.0, seed))) / 7.0
            fr = frac(ph)
            if fr < 0.30:
                n = mixc(c, mulc(hx(s["band"]), min(k * 0.8, 1.1)), 0.75)
            elif fr < 0.40:
                n = mulc(c, 0.62)
        elif pat == "embers":                      # Slag: small glowing ember clusters, rare pits, no rust
            e = vnoise(x / 3.2, y / 3.2, seed)
            if e > 0.72:
                n = glow if h01(x, y, seed + 5) < 0.4 else mixc(c, mulc(glow, 0.72), 0.75)
            elif h01(x, y, seed + 9) < 0.02:
                n = mulc(c, 0.55)
        elif pat == "strata":                      # Cinder: jagged red lava strata, glowing crack network, ember spots
            zig = abs(((x * 0.9) % 6.0) - 3.0) * 0.9 + vnoise(x / 5.0, y / 5.0, seed) * 2.5
            fr = frac((y + zig) / 6.5)
            if fr < 0.24:
                n = mixc(c, mulc(hx(s["red"]), min(max(k, 0.7), 1.3)), 0.85)
            gv = vnoise(x / 4.0, y / 4.0, seed + 3) * 5.0
            if abs(frac(gv) - 0.5) < 0.045:
                n = mixc(n, hx(s["crack"]), 0.8)
            if h01(x, y, seed + 11) < 0.015:
                n = glow
        elif pat == "brushed":                     # Titanium: brushed grain, blue plate edges, faint purple centres
            n = mulc(c, 1.0 + (vnoise(x / 9.0, y * 1.0, seed) - 0.5) * 0.14)
            d = dist.get((x, y), 9)
            edge = mulc(hx(s["edge"]), min(max(k, 0.7), 1.3))
            if d <= 0:
                n = mixc(n, edge, 0.55)
            elif d == 1:
                n = mixc(n, edge, 0.32)
            elif d == 2:
                n = mixc(n, edge, 0.14)
            elif d >= 4:
                n = mixc(n, mulc(hx(s["centre"]), min(max(k, 0.8), 1.4)), 0.16)
        elif pat == "damascus_lines":              # Lumen: thin random Damascus Mithril lines with a brighter core
            ph = (x * ca + y * sa + 3.0 * vnoise(x / 6.0, y / 6.0, seed)) / 6.0
            fr = frac(ph)
            if fr < 0.07:
                n = hx(s["core"])
            elif fr < 0.17:
                n = mulc(hx(s["line"]), min(max(k, 0.8), 1.1))
        if spark and h01(x, y, seed + 17) < spark:
            n = glow
        o = mixc(c, n, min(w, 1.0))
        if premul:
            o = mulc(o, a / 255.0)
        img.put(x, y, (o[0], o[1], o[2], a))
    return img


# ===================================================================================================== the skyyart colour-source swap
_ORIG = {"metal": SA.metal_gradient, "band": SA.band_gradient, "gem": SA.gem_gradient}


@contextmanager
def metal_ctx(m, probe=False):
    """Inside: skyyart's metal / band / gem gradients are metal m's card (whatever tier the family code asks for - it asks for the
    shape donor), and the per-metal wand tune overrides are off. probe=True: the metal gradient is hue-rotated (mask finding)."""
    mg, tg, gg = metal_grad(m), trim_grad(m), gem_grad(m)
    if probe:
        mg = probe_grad(mg)
    donor = SPEC[m]["donor"]
    saved = (SA.metal_gradient, SA.band_gradient, SA.gem_gradient, SA.WAND_METAL_TUNE)
    SA.metal_gradient = lambda z, metal: mg
    SA.band_gradient = lambda z, metal: tg
    SA.gem_gradient = (lambda z, metal: gg) if gg is not None else (lambda z, metal: _ORIG["gem"](z, donor))
    SA.WAND_METAL_TUNE = {}
    try:
        yield
    finally:
        SA.metal_gradient, SA.band_gradient, SA.gem_gradient, SA.WAND_METAL_TUNE = saved


def diff_mask(a_png, b_png):
    a, b = SA._img(a_png), SA._img(b_png)
    out = {}
    for y in range(a.h):
        for x in range(a.w):
            p, q = a.get(x, y), b.get(x, y)
            if p[3] == 0:
                continue
            d = max(abs(p[0] - q[0]), abs(p[1] - q[1]), abs(p[2] - q[2]))
            if d > 8:
                out[(x, y)] = min(d / 100.0, 1.0)
    return out


def masked_texture(m, fn):
    """Run texture function fn() (-> PNG bytes) for metal m, find its metal texels with a probe run, paint the card pattern."""
    with metal_ctx(m):
        tex = fn()
    with metal_ctx(m, probe=True):
        tex_p = fn()
    mask = diff_mask(tex, tex_p)
    img = apply_pattern(SA._img(tex), mask, m, seed_of(m))
    return SA.png_encode(img), len(mask)


def seed_of(*parts):
    return zlib.crc32("|".join(parts).encode("utf-8")) & 0xffff


# ===================================================================================================== colour classes of vanilla art
def unpremul(c):
    a = c[3]
    if a == 0:
        return (0, 0, 0)
    f = 255.0 / a
    return (c[0] * f, c[1] * f, c[2] * f)


def classify(img, rule, premul=False, rects=None):
    """{class: {(x, y): 1.0}} of the opaque pixels (alpha >= 1), class = rule(rgb) (None = keep)."""
    out = {}
    pts = SA._region_points(img, rects, 1) if rects else [(x, y, 0) for y in range(img.h) for x in range(img.w)]
    for x, y, _ri in pts:
        c = img.get(x, y)
        if c[3] == 0:
            continue
        k = rule(unpremul(c) if premul else c[:3])
        if k:
            out.setdefault(k, {})[(x, y)] = 1.0
    return out


def nearest_rule(refs):
    rr = [(hx(h), k) for h, k in refs]

    def rule(c):
        best = min(rr, key=lambda r: sum((c[i] - r[0][i]) ** 2 for i in range(3)))
        return best[1]
    return rule


def px_rects(mask):
    return [(x, y, x + 1, y + 1) for (x, y) in sorted(mask)]


def recolor_classes(png, classes, grads, tunes, icon=False):
    """recolour each class's pixels with its gradient (texture: SA.recolor; icon: SA.recolor_icon, premultiplied)."""
    img = SA._img(png)
    for k in sorted(classes):
        if k not in grads or not classes[k]:
            continue
        t = tunes.get(k, {"lo": 0.05, "hi": 1.0, "rank": 0.5})
        if icon:
            img = SA.recolor_icon(img, grads[k], weights=classes[k], as_img=True, **t)
        else:
            img = SA.recolor(img, grads[k], px_rects(classes[k]), as_img=True, **t)
    return img


TUNE_METAL = {"lo": 0.05, "hi": 1.0, "rank": 0.5}     # = the metal wand head span
TUNE_TRIM = {"lo": 0.30, "hi": 0.95, "rank": 0.5}     # ~ the wand band span
TUNE_GEM = {"lo": 0.15, "hi": 1.0, "rank": 0.5}       # = the wand leaves span
METAL_SPAN = {"Lead": {"lo": 0.02, "hi": 0.74}, "Slag": {"hi": 0.88}}   # dull metals: no mirror-white top on vanilla-art recolours


def grads_of(z, m):
    if m == "Electrum":
        g = electrum_grad(z)
        return {"metal": g, "trim": g, "gem": g}
    gg = gem_grad(m) or _ORIG["gem"](z, SPEC[m]["donor"])
    return {"metal": metal_grad(m), "trim": trim_grad(m), "gem": gg}


def recolor_item(z, m, tex_png, icon_png, tex_classes, icon_classes, seed_key):
    """texture + icon of a vanilla-model item for metal m: per-class gradient map, then the card pattern on the metal class."""
    G = grads_of(z, m)
    tunes = {"metal": dict(TUNE_METAL, **METAL_SPAN.get(m, {})), "trim": TUNE_TRIM, "gem": TUNE_GEM}
    t = recolor_classes(tex_png, tex_classes, G, tunes)
    apply_pattern(t, tex_classes.get("metal", {}), m, seed_of(m, seed_key))
    i = None
    if icon_png is not None:
        i = recolor_classes(icon_png, icon_classes, G, tunes, icon=True)
        apply_pattern(i, icon_classes.get("metal", {}), m, seed_of(m, seed_key, "icon"), premul=True)
    return SA.png_encode(t), (SA.png_encode(i) if i is not None else None)


# ===================================================================================================== vanilla item lookup (with Parent)
class Items(object):
    def __init__(self, z):
        self.z = z
        self.idx = {}
        for n in z.namelist():
            if n.startswith("Server/Item/Items/") and n.endswith(".json"):
                self.idx[os.path.basename(n)[:-5]] = n

    def get(self, iid):
        d = json.loads(self.z.read(self.idx[iid]).decode("utf-8-sig"))
        if d.get("Parent") in self.idx:
            p = self.get(d["Parent"])
            p.update(d)
            return p
        return d

    def parts(self, iid):
        d = self.get(iid)
        return d, SA._read(self.z, d["Model"]), SA._read(self.z, d["Texture"]), SA._read(self.z, d["Icon"])


# ===================================================================================================== output bookkeeping
class Out(object):
    def __init__(self, write=True):
        self.write_files = write
        self.files = {}          # rel path -> bytes
        self.manifest = []
        self.rows = {}           # batch -> {metal: [icon png ...]}
        self.cols = {}           # batch -> [column labels]

    def put(self, rel, data):
        if isinstance(data, str):
            data = data.encode("utf-8")
        self.files[rel] = data
        return "models-local/art/metals/" + rel

    def item(self, batch, col, m, pid, family, base, tex=None, icon=None, model=None, extra=None, status="made"):
        e = {"item": pid, "family": family, "metal": m, "base_asset": base, "palette": palette_note(m),
             "texture": tex, "icon": icon, "model": model, "status": status}
        if extra:
            e["notes"] = extra
        self.manifest.append(e)
        return e

    def sheet_icon(self, batch, col, m, icon_png):
        self.rows.setdefault(batch, {}).setdefault(m, {})[col] = icon_png
        cols = self.cols.setdefault(batch, [])
        if col not in cols:
            cols.append(col)

    def flush(self):
        for rel, data in sorted(self.files.items()):
            p = os.path.join(OUT, rel.replace("/", os.sep))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "wb") as fh:
                fh.write(data)


def P(family, *rest):
    return "/".join((family,) + rest)


# ===================================================================================================== batch 1: ores, bars, Enchanted
ORE_DONOR_TEX = {"Lead": "Thorium", "Chromium": "Cobalt", "Slag": "Adamantite", "Titanium": "Mithril"}


def batch_ores(z, items, out):
    for m in ORES:
        d = ORE_DONOR_TEX[m]
        tex = SA._read(z, "Resources/Ores/Ore_Textures/%s.png" % d)
        icon = SA._read(z, "Icons/ItemsGenerated/Ore_%s.png" % d)
        all_t = {"metal": {p: 1.0 for p in classify(SA._img(tex), lambda c: "metal")["metal"]}}
        all_i = classify(SA._img(icon), lambda c: "metal", premul=True)
        t, i = recolor_item(z, m, tex, icon, all_t, all_i, "ore")
        tp = out.put(P("ores", "Common/Resources/Ores/Ore_Textures/SkyyMetal_%s.png" % m), t)
        ip = out.put(P("ores", ICON_DIR, "SkyyMetal_Ore_%s.png" % m), i)
        out.item("ores", "ore", m, "Ore_%s" % m, "ore (item + block CustomModelTexture)",
                 "vanilla Ore_%s (Resources/Ores/Ore_Large.blockymodel + Ore_Textures/%s.png + its icon)" % (d, d), tp, ip,
                 "Resources/Ores/Ore_Large.blockymodel (vanilla, by path)",
                 "block variants (Ore_%s_Stone / _Basalt ...) reuse this texture as CustomModelTexture; their cube icons are not made" % m)
        out.sheet_icon("ores-bars", "ore", m, i)


def batch_bars(z, items, out):
    for m in METALS + ("Electrum",):
        d = SPEC[m]["donor"] if m in SPEC else "Gold"
        tex = SA._read(z, "Resources/Materials/Ingot_Textures/%s.png" % d)
        icon = SA._read(z, "Icons/ItemsGenerated/Ingredient_Bar_%s.png" % d)
        t_cls = {"metal": classify(SA._img(tex), lambda c: "metal").get("metal", {})}
        i_cls = classify(SA._img(icon), lambda c: "metal", premul=True)
        t, i = recolor_item(z, m, tex, icon, t_cls, i_cls, "bar")
        tp = out.put(P("bars", "Common/Resources/Materials/Ingot_Textures/SkyyMetal_%s.png" % m), t)
        ip = out.put(P("bars", ICON_DIR, "SkyyMetal_Bar_%s.png" % m), i)
        out.item("bars", "bar", m, "Ingredient_Bar_%s" % m, "bar / ingot",
                 "vanilla Ingredient_Bar_%s (Resources/Materials/Ingot.blockymodel + Ingot_Textures/%s.png + its icon)" % (d, d), tp, ip,
                 "Resources/Materials/Ingot.blockymodel (vanilla, by path)")
        out.sheet_icon("ores-bars", "bar", m, i)
        if m in ORES:            # Enchanted ingot (collections: base metals only)
            et = SA.png_encode(SE._shine(SA._img(t), False))
            ei = SA.png_encode(SE._shine(SA._img(i), True))
            etp = out.put(P("enchanted", "Common/Items/SkyyCollections/Ench/SkyyMetal_%s.png" % m), et)
            eip = out.put(P("enchanted", ICON_DIR, "SkyyMetal_Ench_%s.png" % m), ei)
            out.item("ores-bars", "ench", m, "Skyy_Ench_%s" % m, "Enchanted ingot (x100)",
                     "our %s bar above + tools/skyyench.py _shine (the same shiny copy as the 8 existing Enchanted ingots)" % m, etp, eip,
                     "Resources/Materials/Ingot.blockymodel (vanilla, by path)")
            out.sheet_icon("ores-bars", "ench", m, ei)


# ===================================================================================================== batch 2: weapons
def wand(z, items, out):
    d, model, _t, _i = SA.item_parts(z, SA.WAND_ITEM)
    for m in METALS:
        donor = SPEC[m]["donor"]
        tex, n = masked_texture(m, lambda: SA.wand_texture(z, donor, "B"))
        icon = SA.render_icon(model, tex, d["IconProperties"], 64)
        tp = out.put(P("wand", "Common/Items/Weapons/Wand/SkyyMetal_Wand_%s_Texture.png" % m), tex)
        ip = out.put(P("wand", ICON_DIR, "SkyyMetal_Wand_%s.png" % m), icon)
        out.item("weapons", "wand", m, "Weapon_Wand_%s" % m, "Wand (Priest)",
                 "vanilla Weapon_Wand_Wood model + skyyart wand recipe style B (wood handle + metal head), %s shape tune" % donor,
                 tp, ip, "Items/Weapons/Wand/Wood.blockymodel (vanilla, by path); IconProperties = Weapon_Wand_Wood's",
                 "%d metal texels patterned" % n)
        out.sheet_icon("wand", "wand", m, icon)


def kunai(z, items, out):
    d, model, vtex, _i = SA.item_parts(z, MK.BASE_ITEM)
    for m in METALS:
        donor = SPEC[m]["donor"]
        tex, n = masked_texture(m, lambda: MK.kunai_texture(z, donor, model, vtex))
        icon = SA.render_icon(model, tex, d["IconProperties"], 64)
        tp = out.put(P("kunai", "Common/Items/Weapons/Kunai/SkyyMetal_Kunai_%s_Texture.png" % m), tex)
        ip = out.put(P("kunai", ICON_DIR, "SkyyMetal_Kunai_%s.png" % m), icon)
        out.item("weapons", "kunai", m, "Weapon_Kunai_%s" % m, "Kunai (Assassin)",
                 "vanilla Weapon_Kunai model (Throwing_Knife/Kunai.blockymodel) + make_kunai.kunai_texture (%s features)" % donor,
                 tp, ip, d["Model"] + " (vanilla, by path); IconProperties = Weapon_Kunai's", "%d metal texels patterned" % n)
        out.sheet_icon("kunai", "kunai", m, icon)


def staffs(z, items, out):
    for m in METALS:
        donor = SPEC[m]["donor"]
        d, vmodel, butt, tip, hand, side = MS.staff_rig(z, donor)
        model, kinds, side = MS.staff_model({"model": vmodel, "_rig": (butt, tip, hand, side)}, donor)
        place, height = MS.pack(model)
        tex, n = masked_texture(m, lambda: MS.paint_texture(model, place, height, kinds, MS.tier_colours(z, donor)))
        icon = SA.render_icon(model, tex, d["IconProperties"], 64)
        mp = out.put(P("staff", "Common/Items/Weapons/Staff/SkyyMetal_Staff_%s.blockymodel" % m), json.dumps(model, indent=2) + "\n")
        tp = out.put(P("staff", "Common/Items/Weapons/Staff/SkyyMetal_Staff_%s_Texture.png" % m), tex)
        ip = out.put(P("staff", ICON_DIR, "SkyyMetal_Staff_%s.png" % m), icon)
        out.item("weapons", "staff", m, "Weapon_Staff_%s" % m, "Mage staff",
                 "make_staffs own model (the %s staff design on the vanilla %s staff rig)" % (donor, donor), tp, ip, mp,
                 "IconProperties = vanilla Weapon_Staff_%s's %s; %d metal texels patterned" % (donor, json.dumps(d["IconProperties"]), n))
        out.sheet_icon("staff", "staff", m, icon)


def bo(z, items, out):
    bd, _bm, _bt, _bi = SA.item_parts(z, MS.BO_ITEM)
    vanilla_bo = json.loads(SA._read(z, bd["Model"]).decode("utf-8-sig"))
    for m in METALS:
        donor = SPEC[m]["donor"]
        model = MS.bo_model(vanilla_bo, donor)
        place, height = MS.pack(model)
        tex, n = masked_texture(m, lambda: MS.bo_texture(z, donor, model, place, height, MS.tier_colours(z, donor)))
        icon = SA.render_icon(model, tex, bd["IconProperties"], 64)
        mp = out.put(P("bo", "Common/Items/Weapons/Staff/SkyyMetal_Bo_%s.blockymodel" % m), json.dumps(model, indent=2) + "\n")
        tp = out.put(P("bo", "Common/Items/Weapons/Staff/SkyyMetal_Bo_%s_Texture.png" % m), tex)
        ip = out.put(P("bo", ICON_DIR, "SkyyMetal_Bo_%s.png" % m), icon)
        out.item("weapons", "bo", m, "Weapon_Bo_%s" % m, "Bo staff (Monk)",
                 "make_staffs own Bo model (%s design, vanilla Bo_Wood rig)" % donor, tp, ip, mp,
                 "IconProperties = vanilla Weapon_Staff_Bo_Wood's; %d metal texels patterned" % n)
        out.sheet_icon("bo", "bo", m, icon)


# spellbook cover leather + bookmark ribbon per new metal (our own colours, echoing each card like BOOK_LEATHER echoes the vanilla tiers)
BOOK_LEATHER = {
    "Lead": ("#0e1014", "#22262e", "#343a44", "#4a525e", "#66707e"),        # slate grey
    "Dusk": ("#0e0c14", "#24202e", "#36303f", "#4a4456", "#625c70"),        # dusky violet-grey
    "Chromium": ("#08102a", "#142456", "#203674", "#2e4a92", "#4864b0"),    # deep cobalt (its trim)
    "Azurvane": ("#070e20", "#12204a", "#1c3064", "#2a4682", "#42609e"),    # dark navy
    "Slag": ("#0c0a0a", "#1e1a1a", "#2c2626", "#3c3434", "#504646"),        # charcoal
    "Cinder": ("#100606", "#2a0c0c", "#3e1210", "#561a16", "#742620"),      # black-red
    "Titanium": ("#0c0e22", "#1e2448", "#2c3462", "#3e4880", "#5660a0"),    # anodized blue
    "Lumen": ("#120a20", "#2a1a46", "#3c2862", "#523a80", "#6c52a0"),       # anodized purple
}
BOOK_RIBBON = {"Lead": ("#2a2010", "#5c4a24", "#8c7446", "#c4a870", "#f0dcae"),      # brass
               "Chromium": ("#2a3440", "#6a7888", "#aebbca", "#dde4ec", "#ffffff")}  # chrome; the rest = their GEM ramp


def spellbooks(z, items, out):
    d, vmodel_b, vtex, _vi = SA.item_parts(z, MB.BASE_ITEM)
    props = d["IconProperties"]
    vanilla = json.loads(vmodel_b.decode("utf-8-sig"))
    for m in METALS:
        donor = SPEC[m]["donor"]
        b = MB.Builder()
        model = MB.build_model(vanilla, donor, b)
        place = MB.pack(b, 64)
        saved = (MB.BOOK_LEATHER[donor], MB.CONCEPT_RIBBON[donor])
        MB.BOOK_LEATHER[donor] = MB.ramp(*BOOK_LEATHER[m])
        MB.CONCEPT_RIBBON[donor] = MB.ramp(*(BOOK_RIBBON.get(m) or GEM[m]))
        try:
            tex, n = masked_texture(m, lambda: MB.make_texture(z, vtex, vanilla, donor, b, place)[0])
        finally:
            MB.BOOK_LEATHER[donor], MB.CONCEPT_RIBBON[donor] = saved
        icon = SA.png_encode(MB.render(model, tex, props))
        mp = out.put(P("spellbook", "Common/Items/Weapons/Spellbook/SkyyMetal_Spellbook_%s.blockymodel" % m),
                     json.dumps(model, indent=2) + "\n")
        tp = out.put(P("spellbook", "Common/Items/Weapons/Spellbook/SkyyMetal_Spellbook_%s_Texture.png" % m), tex)
        ip = out.put(P("spellbook", ICON_DIR, "SkyyMetal_Spellbook_%s.png" % m), icon)
        out.item("weapons", "spellbook", m, "Weapon_Spellbook_%s" % m, "Spellbook (Mage)",
                 "make_spellbooks own model (vanilla Grimoire_Brown nodes + the %s caps / bands / emblem)" % donor, tp, ip, mp,
                 "IconProperties = vanilla Grimoire_Brown's %s; %d metal texels patterned" % (json.dumps(props), n))
        out.sheet_icon("spellbook", "spellbook", m, icon)


def soulcages(z, items, out):
    for m in METALS:
        donor = SPEC[m]["donor"]
        t = SA.METALS.index(donor)
        ess_name, ess_tex = MC.ESSENCE[t]

        def fn():
            head, band = SA._tuned(donor, "head"), SA._tuned(donor, "bands")
            elo, ehi = MC.ESS_SPAN.get(ess_name, (0.0, 1.0))
            M = MC.ramp_fn(SA.metal_gradient(z, donor), head["lo"], head["hi"])
            T = MC.ramp_fn(SA.band_gradient(z, donor), band["lo"], band["hi"])
            E = MC.ramp_fn(SA.palette_from([SA._read(z, ess_tex)]), elo, ehi, MC.ESS_TINT.get(ess_name))
            return SA.png_encode(MC.paint(M, T, E))
        model = MC.build_model(t)
        tex, n = masked_texture(m, fn)
        icon = SA.render_icon(model, tex, MC.ICON_PROPS, 64)
        mp = out.put(P("soulcage", "Common/Items/Weapons/SoulCage/SkyyMetal_SoulCage_%s.blockymodel" % m), json.dumps(model, indent=2) + "\n")
        tp = out.put(P("soulcage", "Common/Items/Weapons/SoulCage/SkyyMetal_SoulCage_%s_Texture.png" % m), tex)
        ip = out.put(P("soulcage", ICON_DIR, "SkyyMetal_SoulCage_%s.png" % m), icon)
        out.item("weapons", "soulcage", m, "Weapon_Wand_SoulCage_%s" % m, "Soul Cage (Priest)",
                 "make_soulcage own model (%s cage: %d tethers, essence %s)" % (donor, MC.TETHERS[t], ess_name), tp, ip, mp,
                 "IconProperties %s; spin animation = the existing %s; %d metal texels patterned"
                 % (json.dumps(MC.ICON_PROPS), MC.ANIM_PATH, n))
        out.sheet_icon("soulcage", "soulcage", m, icon)


def gauntlets(z, items, out):
    rot = MF.FAMILY_ROT.get("Gauntlets", MF.ICON_ROT)
    ref_models = [MF.build_gauntlets(v).model() for v in MF.METALS]
    for mdl in ref_models:
        MF.pack(mdl)
    props = MF.fit_props(ref_models, rot)          # = the built Copper .. Onyxium gauntlets' shared IconProperties
    for m in METALS:
        donor = SPEC[m]["donor"]
        b = MF.build_gauntlets(donor)
        mdl = b.model()
        hgt = MF.pack(mdl)
        item = "SkyyArmory_Fist_Gauntlets_%s" % m

        def fn():
            metal, gold = MF.wand_metal(z, donor)
            pal = {"metal": metal, "gold": gold, "gem": SA.gem_gradient(z, donor), "gold_trim": donor in MF.GOLD_TIERS,
                   "rivets": True, "vplate": donor == "Cobalt"}
            return SA.png_encode(MF.Tex(mdl, hgt, b.kind, pal, sum(ord(ch) for ch in item), rot).img)
        tex, n = masked_texture(m, fn)
        icon = SA.render_icon(mdl, tex, props, 64)
        mp = out.put(P("gauntlets", "Common/Items/Weapons/Fist/SkyyMetal_Gauntlets_%s.blockymodel" % m), json.dumps(mdl, indent=2) + "\n")
        tp = out.put(P("gauntlets", "Common/Items/Weapons/Fist/SkyyMetal_Gauntlets_%s_Texture.png" % m), tex)
        ip = out.put(P("gauntlets", ICON_DIR, "SkyyMetal_Gauntlets_%s.png" % m), icon)
        out.item("weapons", "gauntlets", m, "Weapon_Fist_Gauntlets_%s" % m, "Gauntlets (Monk)",
                 "make_fists own gauntlet model (%s design)" % donor, tp, ip, mp,
                 "IconProperties %s (= the existing gauntlets'); %d metal texels patterned" % (json.dumps(props), n))
        out.sheet_icon("gauntlets", "gauntlets", m, icon)


XB_METAL = ("Stud-Back", "Stud-Mid", "Stud-Front", "Metal-Top", "Trigger", "Trigger2", "Bow-Mid", "Bow-L", "Bow-L2", "Bow-R", "Bow-R2")


def _grey(c, lim=0.2):
    mx = max(c[:3])
    return mx > 1e-6 and (mx - min(c[:3])) / mx < lim


def crossbows(z, items, out):
    """the vanilla IRON crossbow (SkyyArmory 0.1.30 rule: grey texels inside the metal nodes / grey icon pixels = metal)."""
    d, model, vtex, vicon = items.parts("Weapon_Crossbow_Iron")
    ximg, iimg = SA._img(vtex), SA._img(vicon)
    inside = set((x, y) for x, y, _ri in SA._region_points(ximg, SA.node_rects(model, XB_METAL), 1))
    tmask = dict(((x, y), 1.0) for y in range(ximg.h) for x in range(ximg.w)
                 if ximg.get(x, y)[3] >= 1 and _grey(ximg.get(x, y)) and SA.luma(ximg.get(x, y)) >= 24.0 and (x, y) in inside)
    imask = dict(((x, y), 1.0) for y in range(iimg.h) for x in range(iimg.w)
                 if iimg.get(x, y)[3] >= 1 and _grey(iimg.get(x, y)) and SA.luma(iimg.get(x, y)) >= 24.0)
    for m in METALS:
        t, i = recolor_item(z, m, vtex, vicon, {"metal": tmask}, {"metal": imask}, "crossbow")
        tp = out.put(P("crossbow", "Common/Items/Weapons/Crossbow/SkyyMetal_Crossbow_%s_Texture.png" % m), t)
        ip = out.put(P("crossbow", ICON_DIR, "SkyyMetal_Crossbow_%s.png" % m), i)
        out.item("weapons", "crossbow", m, "Weapon_Crossbow_%s_Wynn" % m, "Crossbow (Archer)",
                 "vanilla Weapon_Crossbow_Iron (Items/Weapons/Crossbow/Iron.blockymodel + Iron_Texture + icon); nothing from "
                 "More Crossbow Tiers", tp, ip, d["Model"] + " (vanilla, by path); IconProperties = Weapon_Crossbow_Iron's",
                 "%d metal texels / %d icon px recoloured (SkyyArmory crossbow mask)" % (len(tmask), len(imask)))
        out.sheet_icon("crossbow", "crossbow", m, i)


# vanilla shield colour classes (cluster colours of each vanilla shield texture; numbers only): plate -> metal, frame -> trim
SHIELD_REFS = {
    "Thorium": [("#141416", None), ("#1d1e21", None), ("#3a4d34", "metal"), ("#4f6a3a", "metal"), ("#7a8d4d", "metal"),
                ("#605b3c", "trim"), ("#817453", "trim"), ("#a59371", "trim"), ("#d0be9c", "trim")],
    "Cobalt": [("#1a1007", None), ("#2f1e10", None), ("#4a3018", None), ("#1a293d", "metal"), ("#2c4466", "metal"), ("#384656", "metal"),
               ("#5f6873", "trim"), ("#89919a", "trim"), ("#b4bbc2", "trim")],
    "Adamantite": [("#250207", "metal"), ("#3c161a", "metal"), ("#67251b", "metal"), ("#7e6255", "trim"), ("#9d3912", "trim"),
                   ("#cf6632", "trim"), ("#d5af96", "trim"), ("#3a8ec8", "gem"), ("#8fd8f0", "gem")],
    "Mithril": [("#4d3026", None), ("#936538", "trim"), ("#bc8931", "trim"), ("#edd92f", "trim"), ("#858d8e", "metal"),
                ("#cbc5a9", "metal"), ("#e1e5e3", "metal")],
}


def greatshields(z, items, out):
    for m in METALS:
        donor = SPEC[m]["donor"]
        d, model, vtex, vicon = items.parts("Weapon_Shield_%s" % donor)
        rule = nearest_rule(SHIELD_REFS[donor])
        t_cls = classify(SA._img(vtex), rule)
        i_cls = classify(SA._img(vicon), rule, premul=True)
        t, i = recolor_item(z, m, vtex, vicon, t_cls, i_cls, "greatshield")
        tp = out.put(P("greatshield", "Common/Items/Weapons/Shield/SkyyMetal_GreatShield_%s_Texture.png" % m), t)
        ip = out.put(P("greatshield", ICON_DIR, "SkyyMetal_GreatShield_%s.png" % m), i)
        out.item("weapons", "greatshield", m, "Weapon_GreatShield_%s" % m, "Great Shield (Spellblade)",
                 "vanilla Weapon_Shield_%s (%s + texture + icon), plates -> metal, frame -> trim, back kept" % (donor, d["Model"]),
                 tp, ip, d["Model"] + " (vanilla, by path, Scale x1.5 like the existing Great Shields)",
                 "classes: %s" % ", ".join("%s %d" % (k, len(v)) for k, v in sorted(t_cls.items())))
        out.sheet_icon("greatshield", "greatshield", m, i)


# ===================================================================================================== batch 2b: the vanilla metal families
# (round A2 = SkyyArmory 0.1.34, research/Metals-Tools-Fortune-Spec.md 4.1 Group B; Skyy 2026-10-17 "vanilla-style metal weapons (sword, axe,
# daggers, bow...) in all 8 new metals too"): the 10 vanilla families with a metal ladder, each the zone's vanilla base-tier item (the shape
# donor: model by path, texture + icon re-coloured the recolor_item way). Colour classes of the donor art by hue (numbers only): the donor
# metal -> the card's metal, its light accent metal (Thorium tan, Cobalt / Mithril gold, Adamantite beige) -> the card's trim, the Adamantite
# blue gem -> the card's gem; wood, leather, rope, cloth and outlines are kept. Shield = the Great Shield's SHIELD_REFS (same vanilla shield,
# own seed so the two never share an icon).
VW_FAMILIES = (("sword", "Sword"), ("longsword", "Longsword"), ("axe", "Axe"), ("battleaxe", "Battleaxe"), ("mace", "Mace"),
               ("club", "Club"), ("daggers", "Daggers"), ("spear", "Spear"), ("shortbow", "Shortbow"), ("shield", "Shield"))


VW_KEYS = frozenset(k_ for k_, _f in VW_FAMILIES)


def _hsv(c):
    mx, mn = max(c[:3]), min(c[:3])
    v = mx / 255.0
    s = 0.0 if mx <= 0 else (mx - mn) / float(mx)
    if mx == mn:
        return 0.0, s, v
    r, g, b = c[0], c[1], c[2]
    if mx == r:
        h = ((g - b) / float(mx - mn)) % 6.0
    elif mx == g:
        h = (b - r) / float(mx - mn) + 2.0
    else:
        h = (r - g) / float(mx - mn) + 4.0
    return h * 60.0, s, v


def vw_rule(donor):
    """the hue rule of a donor tier's vanilla weapon art: rgb -> 'metal' / 'trim' / 'gem' / None (kept)."""
    def rule(c):
        h, s, v = _hsv(c)
        if v < 0.09:
            return None
        if donor == "Thorium":
            if 65 <= h <= 170 and s >= 0.18:
                return "metal"
            if 30 <= h < 65 and s >= 0.12 and v >= 0.45:
                return "trim"
        elif donor == "Cobalt":
            if (185 <= h <= 255 and s >= 0.08) or (s < 0.12 and v >= 0.28):
                return "metal"
            if 30 <= h < 70 and s >= 0.2 and v >= 0.55:
                return "trim"
        elif donor == "Adamantite":
            if 180 <= h <= 225 and s >= 0.3:
                return "gem"
            if (h <= 32 or h >= 340) and s >= 0.5 and v >= 0.28:
                return "metal"
            if 15 <= h <= 50 and s < 0.5 and v >= 0.5:
                return "trim"
        elif donor == "Mithril":
            if s < 0.16 and v >= 0.33:
                return "metal"
            if 33 <= h <= 62 and s >= 0.35 and v >= 0.45:
                return "trim"
        return None
    return rule


def vw_batch(key, fam):
    def batch(z, items, out):
        for m in METALS:
            donor = SPEC[m]["donor"]
            vid = "Weapon_%s_%s" % (fam, donor)
            d, model, vtex, vicon = items.parts(vid)
            rule = nearest_rule(SHIELD_REFS[donor]) if fam == "Shield" else vw_rule(donor)
            t_cls = classify(SA._img(vtex), rule)
            i_cls = classify(SA._img(vicon), rule, premul=True)
            t, i = recolor_item(z, m, vtex, vicon, t_cls, i_cls, key)
            folder = os.path.dirname(d["Texture"])
            tp = out.put(P(key, "Common/%s/SkyyMetal_%s_%s_Texture.png" % (folder, fam, m)), t)
            ip = out.put(P(key, ICON_DIR, "SkyyMetal_%s_%s.png" % (fam, m)), i)
            out.item("weapons", key, m, "Weapon_%s_%s_SkyWynn" % (fam, m), "%s (vanilla family)" % fam,
                     "vanilla %s (%s + texture + icon)" % (vid, d["Model"]), tp, ip, d["Model"] + " (vanilla, by path)",
                     "classes: %s" % ", ".join("%s %d" % (k, len(v)) for k, v in sorted(t_cls.items())))
            out.sheet_icon(key, fam, m, i)
    batch.__name__ = "vw_" + key
    return batch


# ===================================================================================================== batch 3: the 5 forever tools
TOOLS = ("Pickaxe", "Hatchet", "Multitool", "Harvester", "WateringCan")
TOOL_ID = {"Pickaxe": "Tool_Pickaxe_%s", "Hatchet": "Tool_Hatchet_%s", "Multitool": "Tool_Multitool_%s_Wynn",
           "Harvester": "Tool_Sickle_Harvester_%s", "WateringCan": "Tool_WaterCan_%s"}
TOOL_ICON_SRC = {"Pickaxe": "Tool_Pickaxe_Mithril", "Hatchet": "Tool_Hatchet_Mithril", "WateringCan": "Tool_Watering_Can"}
GEM_NODES = ("MtGem", "HvGem")
TOOL_VIEW = [0, 0, -45]          # head top-right, handle to the bottom-left like the vanilla tool icons (picked from 14 views)


def quirk_rule(base):
    """colour classes of Quirk's approved tool textures: brown wood / leather + teal can window kept, anodized trim (Titanium blue,
    Lumen purple) -> trim, the rest -> metal."""
    def rule(c):
        r, g, b = c
        if r > b + 6 and r >= g:
            return None                                    # wood / leather
        if g > r + 25 and g >= b - 12 and g > 90:
            return None                                    # teal window / water
        if base == "Titanium" and (b - r) / (b + 1.0) > 0.55:
            return "trim"
        if base == "Lumen" and r - g >= 4 and b - g > 30:
            return "trim"
        return "metal"
    return rule


def vanilla_tool_icon_rule(c):
    r, g, b = c
    if r > b + 15:
        return "trim" if (g >= 0.62 * r and r >= 90) else None     # gold -> trim, brown handle kept
    return "metal"


def flatten_lines(img, mask):
    """Lumen base only: its bright Damascus line texels take the mean of their non-line metal neighbours (alloys get their own pattern)."""
    lines = [p for p in mask if SA.luma(img.get(*p)) > 205]
    ls = set(lines)
    for (x, y) in lines:
        acc, n = [0.0, 0.0, 0.0], 0
        for dy in (-2, -1, 0, 1, 2):
            for dx in (-2, -1, 0, 1, 2):
                q = (x + dx, y + dy)
                if q in mask and q not in ls:
                    c = img.get(*q)
                    acc = [acc[i] + c[i] for i in range(3)]
                    n += 1
        if n:
            img.put(x, y, (acc[0] / n, acc[1] / n, acc[2] / n, img.get(x, y)[3]))


def tools(z, items, out):
    if not os.path.isdir(PRIVATE_TOOLS):
        print("tools: SKIPPED - Quirk's private tool builds not found at %s (set SKYWYNN_PRIVATE_TOOLS)" % PRIVATE_TOOLS)
        return
    for tool in TOOLS:
        icon_props = None
        for m in METALS:
            base = "Lumen" if SPEC[m]["kind"] == "alloy" else "Titanium"
            mpath = os.path.join(PRIVATE_TOOLS, base, tool + ".blockymodel")
            tpath = os.path.join(PRIVATE_TOOLS, base, tool + "_Texture.png")
            model = open(mpath, "rb").read()
            qtex = open(tpath, "rb").read()
            if m in ("Titanium", "Lumen"):
                tex, status, tp = qtex, "done by Quirk (texture untouched)", "PRIVATE " + os.path.relpath(tpath, os.path.dirname(ROOT))
            else:
                img = SA._img(qtex)
                cls = classify(img, quirk_rule(base))
                gem_rects = SA.node_rects(model, [n for n in GEM_NODES if n in SA.node_names(model)])
                if gem_rects:
                    gem = dict(((x, y), 1.0) for x, y, _ri in SA._region_points(img, gem_rects, 1))
                    for k in list(cls):
                        cls[k] = dict((p, w) for p, w in cls[k].items() if p not in gem)
                    cls["gem"] = gem
                if base == "Lumen":
                    flatten_lines(img, cls.get("metal", {}))
                t, _ = recolor_item(z, m, SA.png_encode(img), None, cls, {}, "tool-" + tool)
                tex, status = t, "made"
                tp = out.put(P("tools", "Common/Items/Tools/SkyyMetal/%s/%s_Texture.png" % (tool, m)), tex)
            if tool in TOOL_ICON_SRC:
                d = items.get(TOOL_ICON_SRC[tool])
                d = d["State"]["Filled_Water"] if tool == "WateringCan" else d     # = SkyyGear's can look (the filled can)
                vicon = SA._read(z, d["Icon"])
                rule = (lambda c: "metal") if tool == "WateringCan" else vanilla_tool_icon_rule
                i_cls = classify(SA._img(vicon), rule, premul=True)
                G = grads_of(z, m)
                i = recolor_classes(vicon, i_cls, G, {"metal": dict(TUNE_METAL, **METAL_SPAN.get(m, {})), "trim": TUNE_TRIM}, icon=True)
                apply_pattern(i, i_cls.get("metal", {}), m, seed_of(m, tool, "icon"), premul=True)
                icon = SA.png_encode(i)
                ibase = "vanilla %s icon re-coloured" % TOOL_ICON_SRC[tool]
            else:
                if icon_props is None:
                    icon_props = MFI.fit_props([json.loads(model.decode("utf-8-sig"))], TOOL_VIEW, fill=58.0)
                icon = SA.render_icon(model, tex, icon_props, 64)
                ibase = "render_icon of Quirk's model, IconProperties %s" % json.dumps(icon_props)
            ip = out.put(P("tools", ICON_DIR, "SkyyMetal_%s_%s.png" % (tool, m)), icon)
            model_note = ("vanilla %s model by path (Quirk retextured it)" % {"Pickaxe": "Items/Tools/Pickaxe/Mithril.blockymodel",
                                                                             "Hatchet": "Items/Tools/Hatchet/Mithril.blockymodel",
                                                                             "WateringCan": "the vanilla watering can"}[tool]
                          if tool in TOOL_ICON_SRC else "Quirk's own %s model (PRIVATE %s/%s.blockymodel - see questions)" % (tool, base, tool))
            out.item("tools", tool, m, TOOL_ID[tool] % m, "forever tool: " + tool,
                     "Quirk's approved %s %s build (PRIVATE), recoloured; icon: %s" % (base, tool, ibase), tp, ip, model_note,
                     status=status)
            out.sheet_icon("tools", tool, m, icon)


# ===================================================================================================== sheets (tiny bitmap font, no PIL)
FONT = {  # 5x7, rows top->bottom, bit 4 = left
    "A": (14, 17, 17, 31, 17, 17, 17), "B": (30, 17, 17, 30, 17, 17, 30), "C": (14, 17, 16, 16, 16, 17, 14),
    "D": (30, 17, 17, 17, 17, 17, 30), "E": (31, 16, 16, 30, 16, 16, 31), "F": (31, 16, 16, 30, 16, 16, 16),
    "G": (14, 17, 16, 23, 17, 17, 15), "H": (17, 17, 17, 31, 17, 17, 17), "I": (14, 4, 4, 4, 4, 4, 14),
    "J": (7, 2, 2, 2, 2, 18, 12), "K": (17, 18, 20, 24, 20, 18, 17), "L": (16, 16, 16, 16, 16, 16, 31),
    "M": (17, 27, 21, 21, 17, 17, 17), "N": (17, 17, 25, 21, 19, 17, 17), "O": (14, 17, 17, 17, 17, 17, 14),
    "P": (30, 17, 17, 30, 16, 16, 16), "Q": (14, 17, 17, 17, 21, 18, 13), "R": (30, 17, 17, 30, 20, 18, 17),
    "S": (15, 16, 16, 14, 1, 1, 30), "T": (31, 4, 4, 4, 4, 4, 4), "U": (17, 17, 17, 17, 17, 17, 14),
    "V": (17, 17, 17, 17, 17, 10, 4), "W": (17, 17, 17, 21, 21, 21, 10), "X": (17, 17, 10, 4, 10, 17, 17),
    "Y": (17, 17, 10, 4, 4, 4, 4), "Z": (31, 1, 2, 4, 8, 16, 31), " ": (0, 0, 0, 0, 0, 0, 0), "-": (0, 0, 0, 31, 0, 0, 0),
    "0": (14, 17, 19, 21, 25, 17, 14), "1": (4, 12, 4, 4, 4, 4, 14), "2": (14, 17, 1, 2, 4, 8, 31), "3": (30, 1, 1, 14, 1, 1, 30),
    "4": (2, 6, 10, 18, 31, 2, 2), "5": (31, 16, 30, 1, 1, 17, 14), "6": (6, 8, 16, 30, 17, 17, 14), "7": (31, 1, 2, 4, 8, 8, 8),
    "8": (14, 17, 17, 14, 17, 17, 14), "9": (14, 17, 17, 15, 1, 2, 12),
}


def text(img, x, y, s, col, k=2):
    for ch in s.upper():
        if x + 5 * k > img.w:
            break
        g = FONT.get(ch, FONT[" "])
        for r, bits in enumerate(g):
            for c in range(5):
                if bits & (16 >> c):
                    for yy in range(k):
                        for xx in range(k):
                            img.put(x + c * k + xx, y + r * k + yy, col + (255,))
        x += 6 * k


def contact_sheet(title, cols, rows, scale=2):
    """rows: [(label, {col: icon png})]; every icon at `scale` on a dark inventory-like slot."""
    cell, pad, lab = 64 * scale, 10, 120
    W = max(lab + len(cols) * (cell + pad) + pad, 2 * pad + 18 * len(title))
    H = 40 + 24 + len(rows) * (cell + pad) + pad
    img = SA.Img(W, H)
    bg, slot, rim, ink, dim = (20, 22, 28), (40, 44, 56), (64, 70, 86), (230, 232, 236), (150, 156, 170)
    for y in range(H):
        for x in range(W):
            img.put(x, y, bg + (255,))
    text(img, pad, 12, title, ink, 3)
    for ci, c in enumerate(cols):
        text(img, lab + ci * (cell + pad) + 4, 44, c[:20], dim, 2)
    for ri, (label, icons) in enumerate(rows):
        oy = 64 + ri * (cell + pad)
        text(img, pad, oy + cell // 2 - 7, label, ink, 2)
        for ci, c in enumerate(cols):
            ox = lab + ci * (cell + pad)
            for y in range(cell):
                for x in range(cell):
                    img.put(ox + x, oy + y, (rim if x in (0, cell - 1) or y in (0, cell - 1) else slot) + (255,))
            png = icons.get(c)
            if png is None:
                continue
            ic = SA._img(png)
            for y in range(cell):
                for x in range(cell):
                    r, g, b, a = ic.get(x * ic.w // cell, y * ic.h // cell)
                    if a:
                        f = 1 - a / 255.0
                        img.put(ox + x, oy + y, (r + slot[0] * f, g + slot[1] * f, b + slot[2] * f, 255))
    return SA.png_encode(img)


SHEETS = {
    "ores-bars": "Ores bars Enchanted",
    "weapons-a": "Weapons wand crossbow spellbook kunai bo",
    "weapons-b": "Weapons gauntlets soulcage greatshield staff",
    "weapons-c": "Weapons vanilla families",
    "tools": "Forever tools",
}
SHEET_OF = {"wand": "weapons-a", "crossbow": "weapons-a", "spellbook": "weapons-a", "kunai": "weapons-a", "bo": "weapons-a",
            "gauntlets": "weapons-b", "soulcage": "weapons-b", "greatshield": "weapons-b", "staff": "weapons-b"}
SHEET_OF.update((k_, "weapons-c") for k_, _f in VW_FAMILIES)


def make_sheets(out):
    merged = {}
    for batch, per_metal in out.rows.items():
        key = SHEET_OF.get(batch, batch)
        mm = merged.setdefault(key, ([], {}))
        for c in out.cols[batch]:
            if c not in mm[0]:
                mm[0].append(c)
        for m, icons in per_metal.items():
            mm[1].setdefault(m, {}).update(icons)
    for key, (cols, per_metal) in sorted(merged.items()):
        order = [m for m in METALS + ("Electrum",) if m in per_metal]
        rows = [(m, per_metal[m]) for m in order]
        out.put("_sheets/%s.png" % key, contact_sheet(SHEETS.get(key, key), cols, rows))


# ===================================================================================================== validation
def validate(out, z, items):
    bad = []
    vanilla_ids = set(items.idx)
    for rel, data in out.files.items():
        if not rel.endswith(".png") or rel.startswith("_sheets"):
            continue
        w, h = SA.png_size(data)
        img = SA.png_decode(data)
        if "/Icons/" in rel:
            if (w, h) != (64, 64):
                bad.append("%s: icon %dx%d" % (rel, w, h))
            corners = [img.get(0, 0)[3], img.get(63, 0)[3], img.get(0, 63)[3], img.get(63, 63)[3]]
            if max(corners) > 127:                 # the vanilla staff / Bo view grazes a corner at alpha 49 (existing art too)
                bad.append("%s: icon corners not transparent" % rel)
            op = sum(1 for y in range(64) for x in range(64) if img.get(x, y)[3] == 255)
            if op < (100 if rel.split("/")[0] in VW_KEYS else 150):          # A2: the vanilla Thorium spear icon itself has 136 (thin pole)
                bad.append("%s: only %d opaque px" % (rel, op))
        else:
            if (w % 32) or (h % 32):
                bad.append("%s: texture %dx%d not a multiple of 32" % (rel, w, h))
    for e in out.manifest:
        if e["item"] in vanilla_ids:
            bad.append("proposed id %s is a vanilla id" % e["item"])
    seen = {}
    for e in out.manifest:                         # every icon different from the same family's others
        if not e.get("icon") or not e["icon"].startswith("models-local"):
            continue
        rel = e["icon"][len("models-local/art/metals/"):]
        hsh = hashlib.sha256(out.files[rel]).hexdigest()
        if hsh in seen:
            bad.append("%s icon == %s icon" % (e["item"], seen[hsh]))
        seen[hsh] = e["item"]
    return bad


# ===================================================================================================== main
BATCHES = (("ores", batch_ores), ("bars", batch_bars), ("wand", wand), ("crossbow", crossbows), ("spellbook", spellbooks),
           ("kunai", kunai), ("bo", bo), ("gauntlets", gauntlets), ("soulcage", soulcages), ("greatshield", greatshields),
           ("staff", staffs)) + tuple((k_, vw_batch(k_, f_)) for k_, f_ in VW_FAMILIES) + (("tools", tools),)


def run(only=None):
    z = SA.assets()
    items = Items(z)
    out = Out()
    for name, fn in BATCHES:
        if only and name not in only:
            continue
        fn(z, items, out)
        print("  %-11s %3d items so far" % (name, len(out.manifest)))
    make_sheets(out)
    out.put("README.md", "# models-local/art/metals (git-ignored: vanilla-derived art, never commit)\n\n"
            "Made by `python tools/art/make_metal_items.py` (code + palette numbers only). New-metal ores, bars, Enchanted ingots, "
            "9 weapon families and the 5 forever tools, one folder per family; contact sheets in `_sheets/`; every item with its "
            "output paths, base asset and palette in `manifest.json`. The committed list for the build round: "
            "`research/Metal-Art-Manifest.md`. Nothing here is wired into a mod yet.\n")
    return z, items, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="comma list of: " + ",".join(n for n, _f in BATCHES))
    ap.add_argument("--check", action="store_true", help="build twice in memory, compare bytes, validate")
    a = ap.parse_args()
    only = set(s for s in a.only.split(",") if s) or None
    SA.verify(quiet=True)
    z, items, out = run(only)
    bad = validate(out, z, items)
    if a.check:
        _z2, _i2, out2 = run(only)
        diff = [k for k in out.files if out2.files.get(k) != out.files[k]]
        if diff:
            bad.append("NOT deterministic: %s" % diff[:5])
        print("determinism: %s" % ("OK (byte-identical second build, %d files)" % len(out.files) if not diff else "CHANGED"))
    out.flush()
    man = os.path.join(OUT, "manifest.json")
    old = []
    if only and os.path.exists(man):
        old = [e for e in json.load(open(man, encoding="utf-8")) if e["family"] not in set(x["family"] for x in out.manifest)]
    with open(man, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(old + out.manifest, fh, indent=2)
        fh.write("\n")
    z.close()
    print("make_metal_items: %d items, %d files -> %s" % (len(out.manifest), len(out.files), OUT))
    print("validate: %s" % ("PASS" if not bad else "%d FAIL\n  " % len(bad) + "\n  ".join(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
