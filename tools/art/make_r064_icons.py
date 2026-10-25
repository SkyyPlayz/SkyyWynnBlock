#!/usr/bin/env python3
"""SkyWynn round cap064 icons (SkyyTrees 0.6.4 + SkyyClasses 0.1.50, 2026-10-24) - DRAFT v1, our own pixels drawn from code.

Skyy (docs/answered/classes.md 2026-10-24 PER-PATH CAPSTONES + 2ND ASSASSIN ALT): every A1-alt path gets its own branch-1 capstone and the
Assassin gets a second A1-alt (Shadow Mark). This draws, in the approved class-node style (tools/art/make_class_node_icons.py's painter:
class_kit + make_tree_node_icons, pure Python, read-only imports):
  - 11 class-tree node icons: the 8 new path capstones + the 3 Shadow Mark path passives (tools/trees_v3_data.py R064_CAPS / R064_PASSIVES;
    file stem = the node's icon place, e.g. Warrior.b1.r6b -> Skyy_NodeIcon_Warrior_B1R6b)
  - the Shadow Mark ABILITY icon (64 x 64): the approved Assassin ability frame (rim + dark band of art/ability-icons/.../Assassin/
    VanishingAct.png, read and kept pixel for pixel outside the field circle) with a new field + symbol (the lilac hood under an orange
    target mark) - the rune icon (SkyyClasses) and the row-5 ability node (SkyyTrees Skyy_NodeIcon_Assassin_B1R5Free) both use it.
The shared manifests (art/tree-node-icons/manifest-classes.json, art/ability-icons/manifest.json) are NOT touched: the pinned builds count
their entries. Everything lands in art/r064-icons/ with its own manifest.json (sha256 + bytes per file) that the 0.6.4 / 0.1.50 builds check.

Run:   python tools/art/make_r064_icons.py           (writes art/r064-icons; deterministic: two runs = same bytes)
       python tools/art/make_r064_icons.py --check   (build twice, compare, write nothing)
"""
import hashlib, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE)))
import make_tree_node_icons as T
import emblem_png as P
from node_icons.class_kit import *          # noqa: F401,F403 - the class painter parts (read-only)
from node_icons import class_kit as K
import node_icons.class_Warrior as CW
import node_icons.class_Spellblade as CS
import node_icons.class_Archer as CA
import node_icons.class_Monk as CM
import node_icons.class_Mage as CG
import node_icons.class_Priest as CP
import node_icons.class_Assassin as CX

ROOT = T.ROOT
OUT = os.path.join(ROOT, "art", "r064-icons")
ABIL_SRC = os.path.join(ROOT, "art", "ability-icons", "Common", "Icons", "Abilities", "Assassin", "VanishingAct.png")
ABIL_REL = "Common/Icons/Abilities/Assassin/ShadowMark.png"
FRAME_FIELD_R = 26.2          # art/ability-icons/manifest.json frame_geometry_px rim_inner: inside it = the field
FIELD_C, FIELD_E = "#33224e", "#0e0916"   # the Assassin style's field colours (tools/art/make_ability_icons.py ASSASSIN)
AS = C("Assassin")


def smark(ic, cx=28, cy=32, s=1.0):
    """Shadow Mark: the lilac Assassin hood under an orange target mark (the Exposed brand)"""
    hood(ic, cx, cy + 2 * s, 0.85 * s)
    g_target(ic, cx + 14 * s, cy - 14 * s, 0.95 * s, "damage")


# (icon place, category, painter, what it shows, node name)
NODES = [
    ("Warrior.b1.r6b", "ward", lambda ic: (burst(ic, 30, 30, 30, 14, 12, CW.G, base=0.62), CW.oath(ic, 30, 30, 1.0), g_party(ic, 50, 50, 0.8)),
     "the great helm (Guardian's Oath) on a gold burst + a party mark (capstone: the oath binds the whole party in reach)", "Oath of Legions"),
    ("Spellblade.b1.r6b", "ability", lambda ic: (burst(ic, 30, 30, 28, 12, 10, CS.G, base=0.5), CS.sarc(ic, 28, 30, 0.95), CS.momentum(ic, 46, 50, 0.6, "ability")),
     "the Shattering Arc with its shards on a teal burst + blue Momentum chevrons (capstone: arc hits give Momentum back)", "Shatterpoint"),
    ("Archer.b1.r6a", "damage", lambda ic: (burst(ic, 32, 32, 28, 12, 10, CA.G, base=0.5), CA.rain(ic, 30, 28, 0.85), g_target(ic, 48, 48, 0.9, "damage")),
     "falling arrows (Arrow Rain) on a green burst chasing an orange target (capstone: the rain drifts onto the nearest enemy)", "Raincaller"),
    ("Monk.b1.r6a", "damage", lambda ic: (burst(ic, 32, 32, 30, 14, 12, CM.G, base=0.55), shock_rings(ic, 32, 34, 0.9, "damage", 2), CM.fists(ic, 30, 30, 0.95)),
     "the two fists (Hundred Fists) inside orange shockwave rings on a saffron burst (capstone: a shockwave every 5th hit)", "Storm of Fists"),
    ("Mage.b1.r6a", "damage", lambda ic: (burst(ic, 32, 32, 30, 13, 12, "flame", base=0.5), CG.stars(ic, 28, 30, 0.9), star5(ic, 44, 44, 8, "holy")),
     "falling stars (Starfall) on a fire burst + a bright star (capstone: the stars collapse into one blast)", "Supernova"),
    ("Priest.b1.r6b", "health", lambda ic: (burst(ic, 32, 32, 30, 14, 12, "holy", base=0.55), CP.martyr(ic, 30, 30, 1.0), g_ward(ic, 50, 50, 0.8)),
     "the two hearts of Martyr's Grace on a holy burst + a ward (capstone: no drop between jumps, overheal becomes a ward)", "Saint's Covenant"),
    ("Assassin.b1.r6a", "damage", lambda ic: (burst(ic, 32, 32, 28, 12, 10, AS, base=0.5), CX.vanish(ic, 30, 34, 0.95), g_target(ic, 46, 18, 0.8, "damage")),
     "the Vanishing Act smoke on a lilac burst + an orange target (capstone: enemies in the smoke are Exposed)", "Shroud of Night"),
    ("Assassin.b1.r6b", "damage", lambda ic: (burst(ic, 32, 32, 28, 12, 10, AS, base=0.5), g_skull(ic, 24, 28, 1.1), g_target(ic, 44, 44, 0.85, "damage"),
                                               g_fork(ic, 46, 18, 0.8)),
     "a skull (a marked kill) on a lilac burst, the target mark + a fork (capstone: the mark jumps on, First Strike ready)", "Death Sentence"),
    ("Assassin.b1.r2c", "ability", lambda ic: (smark(ic, 26, 30, 0.95), g_hourglass(ic, 50, 48, 1.1)),
     "the hood under the target mark (Shadow Mark) + a blue hourglass (the mark lasts longer)", "Lingering Mark"),
    ("Assassin.b1.r3c", "resource", lambda ic: (smark(ic, 26, 30, 0.95), g_crystal(ic, 48, 46, 0.95), g_down(ic, 56, 26, 0.7, "resource")),
     "the hood under the target mark + a mana crystal with a violet down arrow (costs less)", "Quiet Mark"),
    ("Assassin.b1.r5c", "damage", lambda ic: (smark(ic, 26, 30, 0.95), g_up(ic, 50, 50, 1.0, "damage")),
     "the hood under the target mark + an orange up arrow (a stronger Exposed bonus)", "Killing Intent"),
]


def node_png(place, cat, fn):
    assert cat in K.CLASS_CAT_HEX, cat
    ic = Icon(K.stem_of(place))
    fn(ic)
    return T.png_bytes(ic.render())


def hexc(s):
    return [int(s[1:3], 16), int(s[3:5], 16), int(s[5:7], 16)]


def ability_png():
    """the approved Assassin frame (outside the field circle, pixel for pixel) + a new radial field + the Shadow Mark symbol"""
    src = P.read_png(open(ABIL_SRC, "rb").read())
    assert P.size(src) == (64, 64), "the approved Vanishing Act icon is 64 x 64"
    a, b = hexc(FIELD_C), hexc(FIELD_E)
    out = P.new(64, 64)
    for y in range(64):
        for x in range(64):
            d = math.hypot(x + 0.5 - 32.0, y + 0.5 - 32.0)
            if d >= FRAME_FIELD_R:
                out[y][x] = list(src[y][x])
            else:
                t = min(1.0, d / FRAME_FIELD_R) ** 1.4
                out[y][x] = [int(round(a[k] + (b[k] - a[k]) * t)) for k in range(3)] + [255]
    ic = Icon("ShadowMarkSymbol")
    smark(ic, 30, 33, 0.92)
    sym = ic.render()
    for y in range(64):
        for x in range(64):
            if sym[y][x][3] and math.hypot(x + 0.5 - 32.0, y + 0.5 - 32.0) < FRAME_FIELD_R - 0.6:
                out[y][x] = list(sym[y][x])
    return T.png_bytes(out)


def build():
    files = {}
    nodes = []
    for place, cat, fn, shows, name in NODES:
        stem = K.stem_of(place)
        iid = T.icon_id(place.split(".")[0], stem)
        rel = T.icon_rel(place.split(".")[0], stem)
        data = node_png(place, cat, fn)
        files[rel] = data
        nodes.append({"key": place, "icon_id": iid, "file": rel, "name": name, "category": cat, "accent": K.CLASS_CAT_HEX[cat], "shows": shows})
    files[ABIL_REL] = ability_png()
    return files, nodes


def sheet(files, nodes):
    COLS, CW_, CH_ = 4, 300, 190
    rows = (len(nodes) + 1 + COLS - 1) // COLS
    W, H = 24 + COLS * CW_, 90 + rows * CH_ + 20
    import make_menu_icons as M
    cv = M.Canvas(W, H, T.BG)
    cv.text(24, 20, "SKYWYNN CAP064 - NEW CLASS NODE ICONS + SHADOW MARK - DRAFT V1", T.INK, 3)
    cv.text(24, 54, "8 PATH CAPSTONES, 3 SHADOW MARK PASSIVES, THE SHADOW MARK ABILITY ICON (APPROVED ASSASSIN FRAME). EACH: 2X, 1X, ON THE DISC.", T.DIM, 1)
    items = [(n["name"], n["key"], files[n["file"]], n["shows"]) for n in nodes] + [("Shadow Mark (ability)", ABIL_REL, files[ABIL_REL], "the rune + row-5 node picture")]
    for k, (nm, key, data, shows) in enumerate(items):
        x = 24 + (k % COLS) * CW_
        y = 90 + (k // COLS) * CH_
        img = P.read_png(data)
        cv.checker(x, y, 136, 136, (52, 56, 74), (44, 48, 64))
        cv.blit(img, x + 4, y + 4, 2)
        cv.blit(img, x + 146, y + 4, 1)
        T.node_disc(cv, x + 146, y + 80, 48, img, ring=T.hx("#b58cff"))
        cv.text(x, y + 142, T.clean(nm).upper()[:28], T.INK, 2)
        cv.text(x, y + 160, key.upper()[:44], T.DIM, 1)
        for li, ln in enumerate(T.wrap(T.clean(shows), 46)[:2]):
            cv.text(x, y + 172 + li * 10, ln.upper(), (200, 206, 220), 1)
    return cv.png()


def manifest(files, nodes):
    return {
        "what": "SkyWynn round cap064 icons (SkyyTrees 0.6.4 + SkyyClasses 0.1.50): 11 class-tree node icons + the Shadow Mark ability icon - DRAFT v1",
        "generator": "tools/art/make_r064_icons.py (class_kit painter; the ability frame is the approved Assassin frame of art/ability-icons)",
        "deterministic": True, "original_pixels": True,
        "nodes": nodes,
        "ability": {"id": "ShadowMark", "class": "Assassin", "file": ABIL_REL, "frame_from": "art/ability-icons/" + os.path.relpath(ABIL_SRC, os.path.join(ROOT, "art", "ability-icons")).replace(os.sep, "/"),
                    "shows": "the lilac Assassin hood under an orange target mark (the Exposed brand)"},
        "files": [{"path": p, "bytes": len(d), "sha256": hashlib.sha256(d).hexdigest()} for p, d in sorted(files.items())],
    }


def main():
    if "--check" in sys.argv:
        a, _n = build()
        b, _m = build()
        assert a == b, "not deterministic"
        print("OK: %d files, two builds byte-identical" % len(a))
        return
    files, nodes = build()
    for rel, data in files.items():
        p = os.path.join(OUT, *rel.split("/"))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "wb").write(data)
    open(os.path.join(OUT, "sheet.png"), "wb").write(sheet(files, nodes))
    with open(os.path.join(OUT, "manifest.json"), "w", newline="\n") as fh:
        json.dump(manifest(files, nodes), fh, indent=1)
        fh.write("\n")
    print("wrote %d files + sheet.png + manifest.json -> %s" % (len(files), OUT))


if __name__ == "__main__":
    main()
