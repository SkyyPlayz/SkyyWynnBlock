#!/usr/bin/env python3
"""Writes the ONE shared manifest.json for the SkyWynn gathering-armor art: every tree set found under
Common/Items/Armors/SkyyForaging/<Tier>/<Tree>/ (files, sizes, hashes, textures, node names, counts, status).
Usage: python3 make_foraging_manifest.py [art_root]"""
import glob, hashlib, json, os, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "../../art/gathering-armor"))
BASE = "Common/Items/Armors/SkyyForaging"
PIECES = ("Head", "Chest", "Hands", "Legs")
STATUS = {
    "F1_Grove/Oak": "v2 (in-game Oak wood colours) approved by Skyy 2026-10-09 (\"they all look great!\"); v1 approved 2026-10-08 (\"Yes, the Oak armor looks good, commit it\"); NOT verified in game",
    "F1_Grove/Beech": "approved by Skyy 2026-10-09 (\"Yes, the Beech armor looks good, commit it\"; v2 after \"beech looks too much like iron, i need to look a little more like beech wood in the game\"); NOT verified in game",
    "F1_Grove/Ash": "approved by Skyy 2026-10-09 (\"they all look great!\"); NOT verified in game",
    "F1_Grove/Aspen": "approved by Skyy 2026-10-09 (\"Yes, the Aspen armor looks good, commit it\"); NOT verified in game",
    "F2_Autumn/Maple": "approved by Skyy 2026-10-09 (\"They look great! A little more blue on the azure, and we should be good\"); NOT verified in game",
    "F1_Grove/Birch": "v2 (in-game Birch wood colours) approved by Skyy 2026-10-09 (\"they all look great!\"); v1 approved 2026-10-09 (\"Yes, the Birch armor looks good, commit it\"); NOT verified in game",
}


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


sets = {}
for d in sorted(glob.glob(os.path.join(ROOT, BASE, "*", "*"))):
    tier, tree = d.split(os.sep)[-2:]
    md = "%s/%s/%s" % (BASE, tier, tree)
    pieces = {}
    for p in PIECES:
        m = json.load(open(os.path.join(ROOT, md, p + ".blockymodel")))
        ns = nodes_of(m)
        tex = Image.open(os.path.join(ROOT, md, p + "_Texture.png"))
        boxes = sum(n["kind"] == "box" for n in ns)
        pieces[p] = {"model": "%s/%s.blockymodel" % (md, p), "texture": "%s/%s_Texture.png" % (md, p),
                     "texture_size": list(tex.size),
                     "icon": "Common/Icons/ItemsGenerated/Armor_Foraging_%s_%s.png" % (tree, p),
                     "source": "source/%s/%s/%s.bbmodel" % (tier, tree, p),
                     "attaches_to_bones": [n["name"] for n in ns if n["kind"].startswith("attach:")],
                     "boxes": boxes, "quads": sum(n["kind"] == "quad" for n in ns), "nodes": ns}
    sets["%s/%s" % (tier, tree)] = {
        "tier": tier, "tree": tree, "item_id_prefix_suggestion": "Armor_Foraging_%s" % tree,
        "sheet": "sheet-%s.png" % tree.lower(),
        "status": STATUS.get("%s/%s" % (tier, tree), "draft"),
        "totals": {"boxes": sum(v["boxes"] for v in pieces.values()), "quads": sum(v["quads"] for v in pieces.values())},
        "pieces": pieces}

files = []
for f in sorted(glob.glob(os.path.join(ROOT, "**/*"), recursive=True)):
    if os.path.isfile(f) and not f.endswith("manifest.json"):
        rel = os.path.relpath(f, ROOT)
        e = {"path": rel, "bytes": os.path.getsize(f), "sha256": hashlib.sha256(open(f, "rb").read()).hexdigest()}
        if f.endswith(".png"):
            e["image_size"] = list(Image.open(f).size)
        files.append(e)
man = {
    "name": "SkyWynn gathering armor - Foraging (one 4-piece set per tree type)",
    "set": "SkyyForaging",
    "slots": list(PIECES),
    "format": "Hytale .blockymodel (format: character), boxes + alpha-cut quads, 64 units per block, 1 texel per unit",
    "skyy_quotes": ["lets still make the farming and gathering armor, but use vanilla for mining, and armory for combat gear.",
                    "do a design per tree type in that set, so every hardwood gets its own design in that trees color"],
    "sets": sets,
    "files": files,
    "generators": "tools/art/: ga_<tree>.py (design, e.g. ga_oak.py, ga_birch.py), ga_paint.py (painter), make_foraging_armor.py "
                  "(GA_DESIGN=ga_<tree>), make_foraging_icons.py, make_foraging_sheet.py, make_foraging_manifest.py, "
                  "validate_foraging.py (GA_TREE=<Tree>), check_fit_foraging.py, bb_validate_foraging.js, roundtrip_diff_foraging.py",
}
json.dump(man, open(os.path.join(ROOT, "manifest.json"), "w"), indent=1)
print("wrote manifest.json:", len(files), "files;", ", ".join("%s %d boxes %d quads" % (k, v["totals"]["boxes"], v["totals"]["quads"]) for k, v in sets.items()))
