"""make_kunai - SkyWynn metal kunai art, Copper .. Onyxium (7 tiers): textures + inventory icons + a review sheet.

Concept (approved by Skyy 2026-10-07): research/cloud/weapon-art/kunai-v2.png (+ make_weapons_v2.py draw_kunai), Kunai-Ladder.md 7,
weapon-art README "Kunai" row: black cord-wrapped handle + ring pommel on every tier, leaf blade in the tier metal, a ridge line from
Iron, Cobalt angular (hard facets), Adamantite serrated back, gold collar on Mithril + Onyxium, a glow pixel on the high tiers.

Route R1 (vanilla re-texture, like the metal wands in tools/skyyart.py): the vanilla Weapon_Kunai model
(Items/Weapons/Throwing_Knife/Kunai.blockymodel: Handle, Pommel + Pommel_Inner ring, Blade = collar, Blade2/3 boxes + Blade4 quad tip)
already has every part of the concept, so each tier is a NEW TEXTURE of the same size / UV (64x32) on the unchanged vanilla model.
Per node: Handle -> black cord (the vanilla rope's own light/dark wrap pattern gradient-mapped onto the black leather ramp of the
light-armor sheets), Pommel* -> tier metal, Blade (collar) -> tier metal or the vanilla gold trim, Blade2-4 -> tier metal; then the
per-tier details are painted on the same texels (ridge, facets, serration cut into the Blade4 quad's alpha, glow texel).
Colours come from Assets.zip at RUN time (SA.metal_gradient = the tier's vanilla pickaxe head + ingot, SA.band_gradient('Mithril') =
the vanilla gold trim, SA.gem_gradient = the tier's vanilla staff gem). This file holds NO vanilla pixels; only the cord ramp and the
Mithril / Onyxium concept ramps below are ours (black leather of the light-armor sheet; concept cyan / violet of make_weapons_v2.py).

Icons: SA.render_icon with the vanilla Weapon_Kunai IconProperties; SA.check_icon on the vanilla kunai is run first and printed
(2026-10-07: colour 1.88 / alpha 0.15 of 255 - as good as the wand family).

Run:  python tools/art/make_kunai.py
Out:  models-local/art/kunai/ (git-ignored: everything there is vanilla-derived)
        Common/Items/Weapons/Kunai/SkyyArmory_<Metal>_Texture.png   (64x32, UV of the vanilla Kunai model)
        Common/Icons/ItemsGenerated/SkyyArmory_Kunai_<Metal>.png      (64x64, premultiplied)
        previews/<Metal>_256.png  (the same icon view at 256 px), sheet.png, manifest.json
Deterministic: no clocks / randomness; two runs give the same bytes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyyart as SA  # noqa: E402

OUT = os.path.join(ROOT, "models-local", "art", "kunai")
BASE_ITEM = "Server/Item/Items/Weapon/Kunai/Weapon_Kunai.json"
TEX_DIR = "Common/Items/Weapons/Kunai"
ICON_DIR = "Common/Icons/ItemsGenerated"
METALS = SA.METALS   # Copper, Iron, Thorium, Cobalt, Adamantite, Mithril, Onyxium

# node groups of the vanilla Kunai.blockymodel
PARTS = {"cord": ("Handle",), "ring": ("Pommel", "Pommel_Inner"), "collar": ("Blade",), "blade": ("Blade2", "Blade3", "Blade4")}
BLADE_FRONT = ("Blade2", "Blade3", "Blade4")   # their front faces (front + back share texels) carry ridge / facets / glow
TIP_QUAD = "Blade4"
MID_ROW = 10        # the blade's centre texel row (the vanilla blade texels are symmetric about it, checked at run time)


def hx(s):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


# black cord / leather (research/cloud/light-armor/make_sheets.py + tools/make_light_chest.py LEATHER: our own colours)
CORD = tuple(tuple(float(v) for v in hx(c)) for c in ("#0a090c", "#1c191f", "#2b2730", "#3f3946", "#58515f"))

# tier features (Kunai concept row)
RIDGE = ("Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")
FACET = ("Cobalt",)
SERRATED = ("Adamantite",)
GOLD_COLLAR = ("Mithril", "Onyxium")
GLOW = ("Adamantite", "Mithril", "Onyxium")

# recolor() settings per part (+ rim = edge lift on the part's outline texels)
TUNE = {
    "cord": {"lo": 0.0, "hi": 1.0, "rank": 0.6},
    "ring": {"lo": 0.15, "hi": 1.0, "smooth": 0.4, "rank": 0.5, "rim": 0.12},
    "collar": {"lo": 0.25, "hi": 1.0, "smooth": 0.3, "rank": 0.5, "rim": 0.10},
    "blade": {"lo": 0.08, "hi": 0.95, "smooth": 0.6, "rank": 0.5, "rim": 0.10},
}
METAL_TUNE = {   # per-metal changes (same idea as SA.WAND_METAL_TUNE: dark metals need a higher floor to read)
    "Onyxium": {"ring": {"rank": 0.8, "lo": 0.4}, "blade": {"rank": 0.8, "lo": 0.22, "hi": 1.0}, "collar": {"lo": 0.15, "hi": 0.9}},
    "Mithril": {"collar": {"lo": 0.1, "hi": 0.9}},   # the gold trim: rich gold, not the top yellow (= the wand bands)
}
# Concept hue pull (review 2026-10-07: Mithril read as pale silver, Onyxium as near-black grey). The vanilla Mithril / Onyxium
# pickaxe + ingot ramps are almost neutral, so their blade + ring gradient is mixed toward the approved concept ramp of
# research/cloud/weapon-art/make_weapons_v2.py TIERS (our own colours: light cyan, saturated violet). The gold collar is untouched.
CONCEPT_RAMP = {
    "Mithril": ("#1e3a44", "#4e8c98", "#7ec4cc", "#b4ecee", "#f2ffff"),
    "Onyxium": ("#160c22", "#3e2460", "#6b3fa0", "#a06cda", "#e4c8ff"),
}
CONCEPT_MIX = {"Mithril": 0.75, "Onyxium": 0.85}
RIDGE_LIFT, RIDGE_SHADOW = 0.30, -0.12
FACET_LIFT = 0.10        # Cobalt: upper half of the blade lit, lower half shaded, hard split on the ridge
SERRATION_STEP = 3       # Adamantite: a notch every 3 texels along the back (top) edge of the tip quad, painted on the boxes


def tuned(metal, part):
    p = dict(TUNE[part])
    p.update(METAL_TUNE.get(metal, {}).get(part, {}))
    return p


def opaque(img, x, y):
    return 0 <= x < img.w and 0 <= y < img.h and img.px[(y * img.w + x) * 4 + 3] >= 128


def outline_lift(img, rects, edge):
    """{(x, y): edge} for the opaque texels of rects that touch a see-through texel or the rect border (follows a cut-out tip)."""
    out = {}
    for x0, y0, x1, y1 in rects:
        for y in range(y0, y1):
            for x in range(x0, x1):
                if not opaque(img, x, y):
                    continue
                if x in (x0, x1 - 1) or y in (y0, y1 - 1) or not all(opaque(img, x + dx, y + dy) for dx, dy in
                                                                      ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    out[(x, y)] = edge
    return out


def blade_lift(img, model, metal, edge):
    """Lift map for the blade: outline + (Iron+) ridge on MID_ROW with a shadow under it + (Cobalt) hard facet split."""
    lift = {}
    rects = SA.node_rects(model, BLADE_FRONT)
    fronts = [SA.node_rects(model, [n])[0] for n in BLADE_FRONT]   # first rect of each node = its front face
    for x0, y0, x1, y1 in fronts:
        for y in range(y0, y1):
            for x in range(x0, x1):
                if not opaque(img, x, y):
                    continue
                d = 0.0
                if metal in FACET:
                    d += FACET_LIFT if y < MID_ROW else (-FACET_LIFT if y > MID_ROW else 0.0)
                if metal in RIDGE:
                    d += RIDGE_LIFT if y == MID_ROW else (RIDGE_SHADOW if y == MID_ROW + 1 else 0.0)
                if d:
                    lift[(x, y)] = d
    for p, v in outline_lift(img, rects, edge).items():
        if p[1] != MID_ROW:          # keep the ridge running out to the tip
            lift[p] = lift.get(p, 0.0) + v
    return lift


def serrate(img, model):
    """Adamantite serrated back: cut a notch into the top (back) edge of the tip quad every SERRATION_STEP columns (real
    silhouette: the quad is alpha-tested) and darken the matching top-row texels of the Blade2 / Blade3 front faces (boxes:
    a cut there would show the inside)."""
    qx0, qy0, qx1, qy1 = SA.node_rects(model, [TIP_QUAD])[0]
    for x in range(qx0, qx1):
        if (x - qx0) % SERRATION_STEP != 1:
            continue
        for y in range(qy0, MID_ROW):
            if opaque(img, x, y):
                img.put(x, y, (0, 0, 0, 0))
                break
    for n in ("Blade2", "Blade3"):
        x0, y0, x1, y1 = SA.node_rects(model, [n])[0]
        for x in range(x0, x1):
            if (x - x0) % SERRATION_STEP == 1:
                for y in range(y0, MID_ROW):
                    if opaque(img, x, y):
                        r, g, b, a = img.get(x, y)
                        img.put(x, y, (r * 0.45, g * 0.45, b * 0.45, a))
                        break


def glow(img, model, gem):
    """High tiers: one bright texel (+ 4 softer neighbours, a small plus) of the tier's vanilla staff-gem colour on the blade's ridge."""
    x0, y0, x1, y1 = SA.node_rects(model, ["Blade3"])[0]
    hot, soft = SA.sample(gem, 1.0), SA.sample(gem, 0.75)
    x = x0 + 2
    for (px, py), c in (((x, MID_ROW), hot), ((x + 1, MID_ROW), soft), ((x - 1, MID_ROW), soft), ((x, MID_ROW - 1), soft),
                        ((x, MID_ROW + 1), soft)):
        if opaque(img, px, py):
            img.put(px, py, (c[0], c[1], c[2], 255))


def kunai_texture(z, metal, model, base_tex):
    rects = dict((k, SA.node_rects(model, v)) for k, v in PARTS.items())
    metal_g = SA.metal_gradient(z, metal)
    if metal in CONCEPT_RAMP:
        concept = tuple(tuple(float(v) for v in hx(c)) for c in CONCEPT_RAMP[metal])
        metal_g = SA.grad_mix(metal_g, concept, CONCEPT_MIX[metal])
    gold_g = SA.band_gradient(z, "Mithril")      # the vanilla Mithril staff's gold trim
    img = SA.png_decode(base_tex)

    def part(img, grad, name, lift=None):
        p = tuned(metal, name)
        rim = p.pop("rim", None)
        if lift is None and rim:
            lift = outline_lift(img, rects[name], rim)
        return SA.recolor(img, grad, rects[name], lift=lift, as_img=True, **p)

    img = part(img, CORD, "cord")
    img = part(img, metal_g, "ring")
    img = part(img, gold_g if metal in GOLD_COLLAR else metal_g, "collar")
    img = part(img, metal_g, "blade", lift=blade_lift(img, model, metal, tuned(metal, "blade")["rim"]))
    if metal in SERRATED:
        serrate(img, model)
    if metal in GLOW:
        glow(img, model, SA.gem_gradient(z, metal))
    return SA.png_encode(img)


def write(rel, data):
    p = os.path.join(OUT, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(data)
    return p


def composite(icon, bg):
    """Premultiplied icon over an opaque colour."""
    out = SA.Img(icon.w, icon.h)
    for y in range(icon.h):
        for x in range(icon.w):
            r, g, b, a = icon.get(x, y)
            k = 1.0 - a / 255.0
            out.put(x, y, (r + bg[0] * k, g + bg[1] * k, b + bg[2] * k, 255))
    return out


def sheet(icons, cols=7, scale=2, pad=8):
    """Contact sheet: each 64x64 icon at 2x on a dark slot, no labels (order = METALS, left to right)."""
    page_bg, slot_bg, slot_rim = (14, 16, 22), (34, 38, 50), (58, 64, 82)
    cell = 64 * scale + 2 * pad
    rows = (len(icons) + cols - 1) // cols
    W, H = cols * cell + (cols + 1) * pad, rows * cell + (rows + 1) * pad
    out = SA.Img(W, H)
    for y in range(H):
        for x in range(W):
            out.put(x, y, page_bg + (255,))
    for i, png in enumerate(icons):
        cx, cy = pad + (i % cols) * (cell + pad), pad + (i // cols) * (cell + pad)
        for y in range(cell):
            for x in range(cell):
                rim = x in (0, cell - 1) or y in (0, cell - 1)
                out.put(cx + x, cy + y, (slot_rim if rim else slot_bg) + (255,))
        ic = composite(SA.png_decode(png), slot_bg)
        for y in range(64 * scale):
            for x in range(64 * scale):
                c = ic.get(x // scale, y // scale)
                if c[:3] != slot_bg:
                    out.put(cx + pad + x, cy + pad + y, c)
    return SA.png_encode(out)


def check_mid_row(model, tex):
    """The ridge / facet / serration rules assume the blade texels are symmetric about MID_ROW: prove it on the vanilla texture."""
    img = SA.png_decode(tex)
    for x0, y0, x1, y1 in [SA.node_rects(model, [n])[0] for n in BLADE_FRONT]:
        for x in range(x0, x1):
            ys = [y for y in range(y0, y1) if opaque(img, x, y)]
            if ys and abs((ys[0] + ys[-1]) / 2.0 - MID_ROW) > 0.5:
                raise SA.ArtCheckError("make_kunai: vanilla blade column %d is not centred on row %d (%s)" % (x, MID_ROW, ys))


def main():
    z = SA.assets()
    d, model, tex, icon = SA.item_parts(z, BASE_ITEM)
    props = d["IconProperties"]
    have = set(SA.node_names(model))
    for nodes in PARTS.values():
        for n in nodes:
            if n not in have:
                raise SA.ArtCheckError("make_kunai: vanilla Kunai model has no node %r" % n)
    keys = sorted(PARTS)
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            if SA.rects_overlap(SA.node_rects(model, PARTS[keys[i]]), SA.node_rects(model, PARTS[keys[j]])):
                raise SA.ArtCheckError("make_kunai: parts %s and %s share texels" % (keys[i], keys[j]))
    check_mid_row(model, tex)
    ec, ea = SA.check_icon(model, tex, props, icon)
    print("check_icon vanilla Weapon_Kunai: colour %.2f, alpha %.2f / 255" % (ec, ea))
    if ec > 4.0 or ea > 1.5:
        raise SA.ArtCheckError("make_kunai: render_icon does not match the vanilla kunai icon - stop")
    tw, th = SA.png_size(tex) if hasattr(SA, "png_size") else (64, 32)

    manifest, icons = [], []
    for metal in METALS:
        t = kunai_texture(z, metal, model, tex)
        ic = SA.render_icon(model, t, props, 64)
        tex_rel = "%s/SkyyArmory_%s_Texture.png" % (TEX_DIR, metal)
        icon_rel = "%s/SkyyArmory_Kunai_%s.png" % (ICON_DIR, metal)
        write(tex_rel, t)
        write(icon_rel, ic)
        write("previews/%s_256.png" % metal, SA.png_encode(composite(SA.render_icon(model, t, props, 256, as_img=True),
                                                                    (34, 38, 50))))
        icons.append(ic)
        notes = ["R1: vanilla Kunai model unchanged, new %dx%d texture on its UV" % (tw, th), "black cord handle, %s ring pommel"
                 % metal, ("vanilla gold-trim collar" if metal in GOLD_COLLAR else "%s collar" % metal)]
        if metal in CONCEPT_RAMP:
            notes.append("blade + ring metal mixed %d%% toward the concept %s ramp" % (round(CONCEPT_MIX[metal] * 100),
                                                                                  "cyan" if metal == "Mithril" else "violet"))
        if metal in RIDGE:
            notes.append("ridge line")
        if metal in FACET:
            notes.append("angular: hard lit / shaded facets")
        if metal in SERRATED:
            notes.append("serrated back: notches cut in the tip quad alpha + painted on the box blade")
        if metal in GLOW:
            notes.append("glow texel = vanilla %s staff gem colour" % metal)
        manifest.append({"item": "Kunai %s" % metal, "tier": metal, "model_path": d["Model"], "model_base": d["Model"],
                         "texture_path": tex_rel, "icon_path": icon_rel, "icon_properties": props,
                         "player_animations": d.get("PlayerAnimationsId"), "notes": "; ".join(notes)})
    write("sheet.png", sheet(icons))
    write("manifest.json", (json.dumps(manifest, indent=2) + "\n").encode("utf-8"))
    z.close()
    print("make_kunai: %d textures + %d icons + previews + sheet.png + manifest.json -> %s" % (len(METALS), len(METALS), OUT))


if __name__ == "__main__":
    main()
