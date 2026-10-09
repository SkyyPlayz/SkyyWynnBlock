#!/usr/bin/env python3
"""Writes manifest.json for the SkyWynn gathering-armor art (files, sizes, hashes, textures, node names, counts).
Usage: python3 make_foraging_manifest.py [art_root] [Tier] [Tree]"""
import glob, hashlib, json, os, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "../../art/gathering-armor"))
TIER = sys.argv[2] if len(sys.argv) > 2 else "F1_Grove"
TREE = sys.argv[3] if len(sys.argv) > 3 else "Oak"
MD = "Common/Items/Armors/SkyyForaging/%s/%s" % (TIER, TREE)
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
                 "texture_size": list(tex.size), "icon": "Common/Icons/ItemsGenerated/Armor_Foraging_%s_%s.png" % (TREE, p),
                 "attaches_to_bones": [n["name"] for n in ns if n["kind"].startswith("attach:")],
                 "boxes": boxes, "quads": sum(n["kind"] == "quad" for n in ns), "triangles": boxes * 12,
                 "nodes": ns}
files = []
for f in sorted(glob.glob(os.path.join(ROOT, "**/*"), recursive=True)):
    if os.path.isfile(f) and not f.endswith("manifest.json"):
        rel = os.path.relpath(f, ROOT)
        e = {"path": rel, "bytes": os.path.getsize(f), "sha256": hashlib.sha256(open(f, "rb").read()).hexdigest()}
        if f.endswith(".png"):
            e["image_size"] = list(Image.open(f).size)
        files.append(e)
man = {
    "name": "SkyWynn Foraging armor - %s - %s" % (TIER, TREE),
    "item_id_prefix_suggestion": "Armor_Foraging_%s" % TREE,
    "set": "SkyyForaging", "tier": TIER, "tree": TREE,
    "slots": list(PIECES),
    "format": "Hytale .blockymodel (format: character), boxes + leaf quads, 64 units per block, 1 texel per unit",
    "status": "approved by Skyy 2026-10-08 (\"Yes, the Oak armor looks good, commit it\"); NOT verified in game",
    "skyy_quotes": ["lets still make the farming and gathering armor, but use vanilla for mining, and armory for combat gear.",
                    "do a design per tree type in that set, so every hardwood gets its own design in that trees color"],
    "totals": {"boxes": sum(v["boxes"] for v in pieces.values()), "quads": sum(v["quads"] for v in pieces.values())},
    "pieces": pieces,
    "files": files,
    "generators": "tools/art/: ga_oak.py (design), ga_paint.py (painter), make_foraging_armor.py (models+textures), "
                  "make_foraging_icons.py, make_foraging_sheet.py, make_foraging_manifest.py, validate_foraging.py, "
                  "check_fit_foraging.py, bb_validate_foraging.js, roundtrip_diff_foraging.py",
}
json.dump(man, open(os.path.join(ROOT, "manifest.json"), "w"), indent=1)
print("wrote manifest.json:", len(files), "files")
for p, v in pieces.items():
    print(p, v["boxes"], "boxes", v["triangles"], "tris", v["texture_size"], "bones", v["attaches_to_bones"])
    print("   ", ", ".join(n["name"] for n in v["nodes"] if n["kind"] != "none" and not n["kind"].startswith("attach")))
