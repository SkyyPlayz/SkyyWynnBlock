"""make_hotbar_sheet - review sheet + manifest for the hotbar ability item icons (DRAFT).
    python3 tools/art/make_hotbar_sheet.py [--out DIR] [--review PATH]
sheet.png: one band per class (+ Utility): each item at 4x with its name, then actual 64 px and 32 px; on top a mock hotbar strip
(our own drawing, NOT the vanilla hotbar) with the round HUD ability icons above it for comparison."""
import argparse
import hashlib
import json
import os
import sys

from PIL import Image, ImageDraw

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_hotbar_items as H      # noqa: E402
import make_ability_icons as M     # noqa: E402
import make_ability_sheet as S     # noqa: E402
from ability_icon_meta import META, CLASS_INFO   # noqa: E402

STATUS = "APPROVED by Skyy + committed (answer: \"Yes, the hotbar icons look good, commit them\")"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def groups():
    g = {}
    for it in H.items():
        g.setdefault(it[2], []).append(it)
    return g


def hud_icon(cls, fn):
    st = next(s for s, f, *_r in M.ICONS if f == fn)
    return Image.open(os.path.join(M.DEFAULT_OUT, M.rel_path(st, fn))).convert("RGBA")


def build_sheet(out, title):
    COLW, PAD = 300, 40
    W = PAD * 2 + 5 * COLW
    gs = groups()
    BAND = 470
    TOP = 140
    MOCK = 330
    H_ = TOP + MOCK + BAND * len(gs) + 30
    im = Image.new("RGBA", (W, H_), S.PAGE + (255,))
    d = ImageDraw.Draw(im)
    d.text((PAD, 22), title, font=S.font(46), fill=S.INK)
    d.text((PAD, 82), "Square tablet = hotbar ITEM (select the slot = cast).  Round button = the HUD ability icon (approved, unchanged).  "
           "Sizes: 4x, then 64 px and 32 px.", font=S.font(22, False), fill=S.SUB)
    # mock hotbar
    y0 = TOP
    d.text((PAD, y0), "In a hotbar (mock - our own slots, not vanilla art): round HUD icons above, hotbar items below",
           font=S.font(28), fill=S.INK)
    d.rounded_rectangle([PAD, y0 + 44, W - PAD, y0 + MOCK - 20], 14, fill=S.HUD, outline=S.HUD_EDGE, width=3)
    demo = [None, ("Mage", "Meteor"), ("Mage", "FrostNova"), None, None, None, None, ("Utility", "Loadout"), ("Utility", "Hints")]
    slot, gap = 84, 12
    x0 = (W - (9 * slot + 8 * gap)) // 2
    for i, it in enumerate(demo):
        sx = x0 + i * (slot + gap)
        sy = y0 + 150
        d.rectangle([sx, sy, sx + slot, sy + slot], fill=(40, 46, 58), outline=(78, 88, 106), width=3)
        if it is None:
            continue
        cls, fn = it
        ic = Image.open(os.path.join(out, H.rel(H.PREFIX + (cls + "_" if cls != "Utility" else "") + fn))).convert("RGBA")
        im.alpha_composite(ic, (sx + 10, sy + 10))
        if cls != "Utility":
            im.alpha_composite(hud_icon(cls, fn), (sx + 10, y0 + 70))
        # a fake cooldown bar on Frost Nova (the item's durability bar = cooldown, design section 2)
        if fn == "FrostNova":
            d.rectangle([sx + 8, sy + slot - 12, sx + slot - 8, sy + slot - 7], fill=(20, 22, 28))
            d.rectangle([sx + 8, sy + slot - 12, sx + 8 + int((slot - 16) * 0.4), sy + slot - 7], fill=(92, 196, 108))
    d.text((x0, y0 + 248), "slot 1 = your weapon (empty here)   |   Frost Nova shows a mock cooldown bar (the item's durability bar)",
           font=S.font(20, False), fill=(170, 178, 192))
    # bands
    y = TOP + MOCK
    for cls, its in gs.items():
        hexc = CLASS_INFO[cls]["hex"] if cls in CLASS_INFO else "#aeb4c2"
        d.rectangle([PAD, y + 6, PAD + 34, y + 40], fill=S.hexrgb(hexc), outline=S.INK, width=2)
        name = cls + (" items" if cls != "Utility" else " items (no class - neutral steel rim)")
        d.text((PAD + 50, y + 2), name, font=S.font(32), fill=S.INK)
        d.line([PAD, y + 50, W - PAD, y + 50], fill=S.hexrgb(hexc), width=4)
        for i, (item_id, disp, _c, kind, fn, _r) in enumerate(its):
            ic = Image.open(os.path.join(out, H.rel(item_id))).convert("RGBA")
            cx = PAD + i * COLW + COLW // 2
            yy = y + 64
            im.alpha_composite(ic.resize((256, 256), Image.NEAREST), (cx - 128, yy))
            S.ctext(d, cx, yy + 264, disp, S.font(28), S.INK)
            sub = META[fn]["slot"] if fn in META else "utility"
            S.ctext(d, cx, yy + 298, sub, S.font(18, False), S.SUB)
            im.alpha_composite(ic, (cx - 64 - 10, yy + 328))
            im.alpha_composite(ic.resize((32, 32), Image.BOX), (cx + 20, yy + 344))
        y += BAND
    return im


def manifest(out):
    files = []
    for item_id, disp, cls, kind, fn, _r in H.items():
        p = os.path.join(out, H.rel(item_id))
        rec = {"path": H.rel(item_id).replace(os.sep, "/"), "bytes": os.path.getsize(p), "sha256": sha(p), "size": [64, 64],
               "item_id": item_id, "kind": kind, "class": cls, "name": disp}
        if kind == "mirror":
            rec["mirrors_ability_icon"] = "art/ability-icons/" + M.rel_path(next(s for s, f, *_r in M.ICONS if f == fn), fn).replace(os.sep, "/")
            rec["slot"] = META[fn]["slot"]
            rec["shows"] = "the %s ability glyph (same painter as the approved round icon) on a square %s tablet" % (disp, cls)
        else:
            rec["what"] = next(w for f, _d, _p, w in H.UTILITY if f == fn)
            rec["shows"] = (H.loadout.__doc__ if fn == "Loadout" else H.hints.__doc__).split(": ", 1)[1].strip()
        files.append(rec)
    for extra, what in (("sheet.png", "review sheet: mock hotbar + every item at 4x / 64 / 32 px"),
                        ("README.md", "what this is, the spec, item list, defaults, UNVERIFIED, open questions")):
        p = os.path.join(out, extra)
        if os.path.exists(p):
            files.append({"path": extra, "bytes": os.path.getsize(p), "what": what} | ({"sha256": sha(p)} if extra.endswith(".png") else {}))
    return {
        "item": "Hotbar ability item icons (ART-RESUME queue #8)",
        "status": STATUS,
        "in_game": "NOT wired in (SkyyClasses phase I2 not built), NOT seen in game",
        "spec": "research/cloud/Ability-Input-Design.md section 2 (select = cast, auto-return, cooldown = durability bar, soulbound); "
                "Q5 default: mirrors of the equipped abilities + utility items",
        "generator": ["tools/art/make_hotbar_items.py", "tools/art/make_hotbar_sheet.py", "tools/art/validate_hotbar_items.py",
                      "(reuses tools/art/make_ability_icons.py painters + ability_icon_core.py)"],
        "deterministic": True,
        "item_id_pattern": H.PREFIX + "<Class>_<Ability> (mirror), " + H.PREFIX + "<Utility> (utility) - PROPOSED, the main session picks the real ids",
        "tablet_geometry_px": {"front": [H.TX0, H.TY0, H.TX1, H.TY1], "chamfer": H.CH, "depth_lower_right": H.DEPTH,
                               "border": H.BORDER, "glyph_scale": H.GS},
        "count": {"mirror": sum(1 for i in H.items() if i[3] == "mirror"), "utility": sum(1 for i in H.items() if i[3] == "utility")},
        "files": files,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=H.DEFAULT_OUT)
    ap.add_argument("--review", default="")
    a = ap.parse_args()
    sh = build_sheet(a.out, "SkyWynn hotbar ability items - draft v1 (for review)")
    sp = os.path.join(a.out, "sheet.png")
    sh.convert("RGB").save(sp, optimize=True)
    print("wrote", sp, sh.size)
    if a.review:
        sh.convert("RGB").save(a.review, optimize=True)
        print("wrote", a.review)
    mp = os.path.join(a.out, "manifest.json")
    with open(mp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest(a.out), f, indent=1, ensure_ascii=False)
        f.write("\n")
    print("wrote", mp)


if __name__ == "__main__":
    main()
