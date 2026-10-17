#!/usr/bin/env python3
"""SkyWynn Menu - Void Charms icon (DRAFT). Replaces the brown satchel (Skyy_Menu_Icon_AccessoryBag) on the Void Charms tile.

Skyy 2026-10-17 (tooltip 'Void Charms - ID Skyy_Menu_Icon_AccessoryBag'): "lets change the icon for void charms to be more fitting".
Skyy picked (before the sheet): "a glowing void amulet on a chain" -> candidate A is the chosen one; B and C are small variations
of the same amulet (chain shape / glow strength / setting) for comparison.

Writes (ORIGINAL pixels only; nothing vanilla is read; the neighbour icons on the sheet are OUR art/menu-icons files):
  art/void-charms-icon/Common/Icons/ItemsGenerated/Skyy_Menu_Icon_VoidCharms.png   64 x 64, chosen candidate A
  art/void-charms-icon/candidates/VoidCharms_<A|B|C>_<look>.png                    64 x 64, all three candidates
  art/void-charms-icon/hub-tab/character_accessories.png + _on.png                 72 x 72 faded hub tab icon (candidate A)
  art/void-charms-icon/sheet.png                                                    review sheet
  art/void-charms-icon/manifest.json

Run: python tools/art/make_void_charms_icon.py        (deterministic: two runs = same bytes)
Same painter, palettes and family rules as tools/art/make_menu_icons.py (imported, not edited) and the hub tab fade of
tools/art/make_hub_tab_icons.py (imported, not edited).
"""
import hashlib, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import emblem_png as P
import make_menu_icons as M
from make_menu_icons import Icon, circle, ellipse, rect, poly, capsule, union, diff, ering, star_pts, hx, png_bytes, Canvas
import make_hub_tab_icons as H          # note: sets M.N = 72 on import; every 64 px render below sets M.N = 64 first

ROOT = M.ROOT
OUT = os.path.join(ROOT, "art", "void-charms-icon")
ICON_REL = "Common/Icons/ItemsGenerated/Skyy_Menu_Icon_VoidCharms.png"
NEIGH = ["PocketDimension", "Pets", "Collections"]          # the tiles next to it in the SkyWynn Menu
OLD = "AccessoryBag"
GLINT = "#efe2ff"                                           # brightest void light (not white)


# ====================================================================== the amulet (one builder, three looks)
def chain_pattern(cx, cy):
    """alternating light / dark links along an arc"""
    return lambda x, y: -0.2 if int((math.atan2(y - cy, x - cx) + 4) * 10) % 2 else 0.04


def amulet(name, chain="arc", glow=1, setting="round", metal="gold"):
    ic = Icon(name)
    cx, cy = 32.0, 44.0
    # --- chain (behind everything)
    if chain == "arc":
        ic.add(diff(ering(32, 6, 22, 25, 19.8, 22.8), rect(0, 0, 64, 6)), metal, base=0.55, grad=0.5, bevel=0,
               pattern=chain_pattern(32, 6))
        for bx in (11, 53):
            ic.add(circle(bx, 7, 2.4), metal, mode="sphere", base=0.6)
    else:                                                    # V chain: two straight runs meeting at the bail
        lp = lambda x, y: -0.2 if int((x + y) / 2.2) % 2 else 0.04
        ic.add(capsule(9, 6, 29.5, 29, 1.6), metal, base=0.55, bevel=0, pattern=lp)
        ic.add(capsule(55, 6, 34.5, 29, 1.6), metal, base=0.5, bevel=0, pattern=lp)
        for bx in (9, 55):
            ic.add(circle(bx, 6, 2.4), metal, mode="sphere", base=0.6)
    # --- glow halo behind the setting
    if glow >= 1:
        hr = 15.6 if glow == 1 else 17.0
        hb = 0.0 if glow == 1 else 0.12                    # glow: bright next to the setting, fading outward
        ic.add(circle(cx, cy, hr), "void", tfunc=lambda x, y: 0.92 + hb - 0.62 * (math.hypot(x - cx, y - cy) - 12) / (hr - 12),
               bevel=0, rim=False, cast=False)
    if glow >= 2:                                            # rays left / right / down
        for (x0, y0, x1, y1) in ((cx - 15, cy, cx - 21, cy), (cx + 15, cy, cx + 21, cy), (cx, cy + 15, cx, cy + 19.5)):
            ic.add(capsule(x0, y0, x1, y1, 1.2), "void", base=0.85, bevel=0, rim=False, cast=False)
    # --- bail + setting
    if setting == "round":
        ic.add(ering(32, 30.2, 3.3, 3.3, 1.6, 1.6), metal, base=0.6, bevel=0)
        ic.add(poly(star_pts(cx, cy, 16, 9.5, 4, -45)), metal, base=0.48, grad=0.5)      # four diagonal prongs
        ic.add(circle(cx, cy, 12), metal, mode="sphere", base=0.62, line=True)
        orb_shape, orb_r = circle(cx, cy, 8.8), 8.8
    else:                                                    # teardrop setting, point up
        ic.add(ering(32, 27.5, 3.3, 3.3, 1.6, 1.6), metal, base=0.6, bevel=0)
        ic.add(union(circle(cx, cy + 2, 11.5), poly([(32, 30), (42.4, 41.5), (21.6, 41.5)])), metal, mode="sphere",
               sphere=(cx, cy, 13, 15), base=0.62, line=True)
        orb_shape, orb_r = union(circle(cx, cy + 2, 8.2), poly([(32, 34.5), (39.2, 42.5), (24.8, 42.5)])), 10.0
    # --- the void orb: dark centre-out swirl, lit from the top left
    def orb(x, y, ocx=cx, ocy=(cy if setting == "round" else cy + 1)):
        dx, dy = (x - ocx) / orb_r, (y - ocy) / orb_r
        d = math.hypot(dx, dy); a = math.atan2(dy, dx)
        t = 0.14 + 0.55 * max(0.0, 1 - d) ** 1.2 + 0.27 * math.sin(3 * a + d * 7.5) - 0.12 * (dx + dy)
        return t + (0.08 if glow >= 2 else 0.0)
    ic.add(orb_shape, "void", tfunc=orb, bevel=0.8, bev=0.12, line=True)
    oy = int(cy) if setting == "round" else int(cy) + 1
    ic.px(27, oy - 5, "#cfb2f6"); ic.px(28, oy - 5, GLINT); ic.px(27, oy - 4, "#cfb2f6")    # glass highlight
    ic.px(32, oy, GLINT)                                                                   # bright void core
    # --- sparkles (lilac)
    if glow >= 1:
        ic.sparkle(52, 30, 2 if glow >= 2 else 1, GLINT, "#9a6ee0")
        ic.sparkle(12, 52, 1, GLINT, "#9a6ee0")
        ic.sparkle(51, 57, 1, GLINT, "#9a6ee0")
    else:
        ic.sparkle(51, 31, 1, GLINT, "#9a6ee0")
    return ic


CANDS = [
    ("A", "ArcChainGlow", True, dict(chain="arc", glow=1, setting="round", metal="gold"),
     "CHOSEN: gold link chain in a soft arc, round gold setting with four prongs, a swirling dark-violet void orb, a soft violet glow ring and lilac sparkles"),
    ("B", "VChainBright", False, dict(chain="v", glow=2, setting="round", metal="gold"),
     "variation: straight V chain, stronger glow (bigger violet ring + three light rays, brighter orb)"),
    ("C", "SteelDrop", False, dict(chain="arc", glow=0, setting="drop", metal="steel"),
     "variation: dark steel chain + teardrop setting, no glow ring (the light stays inside the orb)"),
]


def render64(ic):
    M.N = 64
    return ic.render()


def build():
    out = {}
    for key, look, chosen, kw, what in CANDS:
        img = render64(amulet("VoidCharms_" + key, **kw))
        out[key] = (img, png_bytes(img))
    # hub tab version of the chosen one (painted on the 64 grid, centred in 72, sparkles outside the motif dropped, faded)
    kw = CANDS[0][3]
    motif = H.Sheet1Motif(lambda: amulet("VoidCharms_tab", **kw)).render()
    M.N = 64
    tab = {m: H.fade(motif, m) for m in ("normal", "on")}
    return out, tab


# ====================================================================== sheet
BG = (24, 26, 38); PANEL = (34, 37, 52); INK = (226, 228, 236); DIM = (150, 156, 176); GOLDT = hx("#e0b060")
VIO = hx("#aa80d4"); NAVY = (11, 21, 36); SLOT = (22, 38, 58); SLOTE = (44, 66, 96)


def load(rel):
    return P.read_png(open(os.path.join(ROOT, rel), "rb").read())


def menu_icon(name):
    if name == OLD:
        return load("art/accessory-bag-icon/Common/Icons/ItemsGenerated/SkyyAccessories_Bag_Menu.png")
    return load("art/menu-icons/Common/Icons/ItemsGenerated/Skyy_Menu_Icon_%s.png" % name)


def build_sheet(icons, tab):
    W, H_ = 1180, 1010
    cv = Canvas(W, H_, BG)
    cv.text(24, 20, "VOID CHARMS ICON - DRAFT", GOLDT, 4)
    cv.text(24, 60, "REPLACES THE SATCHEL ON THE VOID CHARMS TILE. SKYY PICKED: A GLOWING VOID AMULET ON A CHAIN.", DIM, 2)
    cv.text(24, 82, "64 PX, HARD ALPHA, 1 PX OUTLINE, TOP-LEFT LIGHT, ORIGINAL PIXELS - SAME FAMILY AS THE MENU ICONS.", DIM, 2)
    # --- candidates
    y = 112
    cv.rect(16, y, W - 16, y + 300, PANEL); cv.rect(16, y, W - 16, y + 3, VIO)
    cv.text(28, y + 13, "THE AMULET (A = CHOSEN, B / C = SMALL VARIATIONS)", VIO, 2)
    for k, (key, look, chosen, kw, what) in enumerate(CANDS):
        img = icons[key][0]
        cx = 28 + k * 380; cy = y + 44
        cv.checker(cx, cy, 72, 72, (52, 56, 74), (44, 48, 64)); cv.blit(img, cx + 4, cy + 4)
        cv.rect(cx, cy + 82, cx + 72, cy + 154, NAVY); cv.blit(img, cx + 4, cy + 86)
        cv.rect(cx + 20, cy + 164, cx + 56, cy + 200, NAVY); cv.blit(P.downsample(img, 2), cx + 22, cy + 166)
        cv.checker(cx + 82, cy, 144, 144, (52, 56, 74), (44, 48, 64)); cv.blit(img, cx + 90, cy + 8, 2)
        cv.rect(cx + 82, cy + 150, cx + 226, cy + 214, (214, 218, 226)); cv.blit(img, cx + 122, cy + 150)
        if chosen:
            cv.frame(cx - 6, cy - 6, cx + 360, cy + 252, GOLDT, 2)
        cv.text(cx + 236, cy + 4, key, GOLDT if chosen else INK, 4)
        cv.text(cx + 236, cy + 40, "CHOSEN" if chosen else "VARIATION", GOLDT if chosen else DIM, 2)
        cv.text(cx + 236, cy + 62, look.upper(), DIM, 1)
        words = what.split(": ", 1)[-1].upper().split(" ")
        line, ly = "", cy + 218
        for wd in words:
            if len(line) + len(wd) + 1 > 56:
                cv.text(cx, ly, line, INK, 1); ly += 10; line = ""
            line = (line + " " + wd).strip()
        cv.text(cx, ly, line, INK, 1)
    # --- in the menu, next to its neighbours
    y += 312
    rows = [("NOW", OLD, None)] + [(c[0], None, c[0]) for c in CANDS]
    h = 44 + len(rows) * 86
    cv.rect(16, y, W - 16, y + h, PANEL); cv.rect(16, y, W - 16, y + 3, VIO)
    cv.text(28, y + 13, "IN THE SKYWYNN MENU ROW (MOCK): POCKET DIMENSION - VOID CHARMS - PETS - COLLECTIONS", VIO, 2)
    for r, (lab, old, key) in enumerate(rows):
        ry = y + 40 + r * 86
        cv.text(28, ry + 30, lab, GOLDT if key == "A" else DIM, 3)
        tiles = [menu_icon(NEIGH[0]), menu_icon(OLD) if old else icons[key][0], menu_icon(NEIGH[1]), menu_icon(NEIGH[2])]
        for k, img in enumerate(tiles):
            sx = 120 + k * 80
            cv.rect(sx, ry, sx + 74, ry + 74, SLOT); cv.frame(sx, ry, sx + 74, ry + 74, GOLDT if k == 1 and key == "A" else SLOTE)
            cv.blit(img, sx + 5, ry + 5)
        for k, img in enumerate(tiles):                                    # 32 px row
            sx = 470 + k * 42
            cv.rect(sx, ry + 18, sx + 38, ry + 56, NAVY); cv.blit(P.downsample(img, 2), sx + 3, ry + 21)
        cv.text(660, ry + 32, "SATCHEL - THE ICON BEING REPLACED" if old else ("CHOSEN" if key == "A" else "VARIATION"), DIM, 1)
    # --- hub tab
    y += h + 12
    cv.rect(16, y, W - 16, y + 160, PANEL); cv.rect(16, y, W - 16, y + 3, VIO)
    cv.text(28, y + 13, "CHARACTER HUB TAB (72 PX = 36 UI, FADED BEHIND THE WORD) - OLD TEAL AMULET VS NEW VOID AMULET", VIO, 2)
    old_n = load("art/hub-tab-icons/character_accessories.png"); old_o = load("art/hub-tab-icons/character_accessories_on.png")
    kit = H.KIT
    for k, (st, ic, lab) in enumerate((("Tab", old_n, "OLD"), ("Tab_Selected", old_o, "OLD ON"),
                                       ("Tab", tab["normal"], "NEW"), ("Tab_Selected", tab["on"], "NEW ON"))):
        tx = 28 + k * 280; ty = y + 44
        bg = P.read_png(open(os.path.join(kit, st + "@2x.png"), "rb").read())
        cv.rect(tx, ty, tx + 240, ty + 88, PANEL); cv.blit(bg, tx, ty)
        cv.blit(ic, tx + 84, ty + 8)
        word = "VOID CHARMS"
        col = H.LABEL["buttonText" if st == "Tab_Selected" else "button2Text"]
        cv.text(tx + (240 - len(word) * 12) // 2, ty + 37, word, col, 2)
        cv.text(tx, ty + 96, lab, GOLDT if lab.startswith("NEW") else DIM, 1)
    return cv.png()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    icons, tab = build()
    files = []
    def write(rel, data):
        p = os.path.join(OUT, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as fh: fh.write(data)
        files.append({"path": rel, "bytes": len(data), "sha256": sha(data)})
    write(ICON_REL, icons["A"][1])
    for key, look, chosen, kw, what in CANDS:
        write("candidates/VoidCharms_%s_%s.png" % (key, look), icons[key][1])
    write("hub-tab/character_accessories.png", png_bytes(tab["normal"]))
    write("hub-tab/character_accessories_on.png", png_bytes(tab["on"]))
    write("sheet.png", build_sheet(icons, tab))
    man = {
        "what": "SkyWynn Menu - Void Charms tile icon (replaces the Accessory Bag satchel). DRAFT until Skyy sees the sheet.",
        "status": "DRAFT", "chosen": "A",
        "chosen_why": "Skyy 2026-10-17 picked 'a glowing void amulet on a chain' before the sheet",
        "generator": "tools/art/make_void_charms_icon.py", "deterministic": True, "original_pixels": True,
        "item_id_today": "Skyy_Menu_Icon_AccessoryBag",
        "icon_rules": {"size": [64, 64], "alpha": "hard (0 or 255)", "outline": "1 px #120e1c tinted toward the touching part",
                       "light": "top left", "no_pure_black_or_white": True, "family": "art/menu-icons (tools/art/make_menu_icons.py)"},
        "candidates": [{"key": k, "look": l, "chosen": c, "options": kw, "shows": w,
                        "file": "candidates/VoidCharms_%s_%s.png" % (k, l)} for k, l, c, kw, w in CANDS],
        "hub_tab": {"size": [72, 72], "note": "@2x = 36 x 36 UI; same fade as art/hub-tab-icons; drop-in for character_accessories(_on).png",
                    "files": ["hub-tab/character_accessories.png", "hub-tab/character_accessories_on.png"],
                    "min_contrast": {m: round(H.min_contrast(tab[m], m), 3) for m in ("normal", "on")}},
        "files": files,
    }
    with open(os.path.join(OUT, "manifest.json"), "w", newline="\n") as fh:
        json.dump(man, fh, indent=1); fh.write("\n")
    print("wrote %d files + manifest.json to %s" % (len(files), OUT))


if __name__ == "__main__":
    main()
