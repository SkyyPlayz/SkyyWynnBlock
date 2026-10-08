#!/usr/bin/env python3
"""Writes manifest.json for the Dark Leather set (files, sizes, hashes, textures, node names, counts).
Usage: python3 make_manifest.py [art_root]"""
import glob, hashlib, json, os, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "../../art/dark-leather-armor"))
MD = "Common/Items/Armors/SkyyDarkLeather"
PIECES = ("Head", "Chest", "Hands", "Legs")

def nodes_of(m):
    out = []
    def w(ns, parent):
        for n in ns:
            s = n["shape"]
            kind = "attach:" + n["name"] if s.get("settings", {}).get("isPiece") else s["type"]
            out.append({"name": n["name"], "kind": kind, "parent": parent,
                        **({"size": [s["settings"]["size"][k] for k in "xyz"]} if s["type"] == "box" else {})})
            w(n.get("children", []), n["name"])
    w(m["nodes"], None)
    return out

pieces = {}
for p in PIECES:
    m = json.load(open(os.path.join(ROOT, MD, p + ".blockymodel")))
    ns = nodes_of(m)
    tex = Image.open(os.path.join(ROOT, MD, p + "_Texture.png"))
    boxes = sum(n["kind"] == "box" for n in ns)
    pieces[p] = {"model": "%s/%s.blockymodel" % (MD, p), "texture": "%s/%s_Texture.png" % (MD, p),
                 "texture_size": list(tex.size), "icon": "Common/Icons/ItemsGenerated/Armor_SkyyDarkLeather_%s.png" % p,
                 "attaches_to_bones": [n["name"] for n in ns if n["kind"].startswith("attach:")],
                 "boxes": boxes, "quads": sum(n["kind"] == "quad" for n in ns), "triangles": boxes * 12,
                 "nodes": ns}
files = []
for f in sorted(glob.glob(os.path.join(ROOT, "**/*"), recursive=True)):
    if os.path.isfile(f) and not f.endswith(("sheet_with_refs.png", "manifest.json")):
        rel = os.path.relpath(f, ROOT)
        e = {"path": rel, "bytes": os.path.getsize(f), "sha256": hashlib.sha256(open(f, "rb").read()).hexdigest()}
        if f.endswith(".png"):
            e["image_size"] = list(Image.open(f).size)
        files.append(e)
man = {
    "name": "Skyy Dark Leather light armor set",
    "id_prefix": "SkyyDarkLeather",
    "slots": list(PIECES),
    "format": "Hytale .blockymodel (format: character), boxes only, 64 px per block",
    "status": "draft for Skyy's review (light / slim revision) - not committed; NOT verified in game",
    "skyy_feedback_round_1": "It looks great! But it's supposed to be light armor, so I try to slim it up and scale it down, especially the shoulder pads and the helmet, try to make them slim",
    "skyy_feedback_round_2": "Looks great! If just try to make the shoulder pad wrap around the shoulder a little bit if you can",
    "totals": {"boxes": sum(v["boxes"] for v in pieces.values()), "triangles": sum(v["triangles"] for v in pieces.values())},
    "pieces": pieces,
    "files": files,
    "local_only_not_for_repo": ["sheet_with_refs.png (contains Skyy's reference images)"],
    "generators": "tools/art/: make_dark_leather.py (models+textures), make_icons.py, make_sheet.py, validate.py, check_fit.py, "
                  "bb_validate.js + bb_attach_shots.js (Blockbench checks), make_manifest.py",
    "open_questions_defaults": {
        "paths": "Common/Items/Armors/SkyyDarkLeather/* and Common/Icons/ItemsGenerated/Armor_SkyyDarkLeather_* (no repo convention found)",
        "pauldron_side": "LEFT shoulder (right shoulder = leather sleeve + strap brace)",
        "gem_colour": "amber/orange (ref 3 shows blue - easy texture swap)",
        "crown_spikes": "dropped in the light revision (can come back as one small iron prong per side)",
        "helmet_type": "close-fitting leather half-helm with a painted T/V visor (not a cloth hood - the art skill notes say Skyy dislikes hoods)",
        "tabard": "front tabard + back panel (1.25 thick) hang from Pelvis like vanilla cloth; will pass through thighs when walking (vanilla does too)",
        "triangle_budget": "540 tris (target ~600)",
        "item_json": "no item/recipe JSON made - only art",
    },
}
json.dump(man, open(os.path.join(ROOT, "manifest.json"), "w"), indent=1)
print("wrote manifest.json:", len(files), "files")
for p, v in pieces.items():
    print(p, v["boxes"], "boxes", v["triangles"], "tris", v["texture_size"], "bones", v["attaches_to_bones"])
    print("   ", ", ".join(n["name"] for n in v["nodes"] if n["kind"] != "none" and not n["kind"].startswith("attach")))
