#!/usr/bin/env python3
"""Write art/pebble/manifest.json (paths, sizes, descriptions, node names, animation lengths)."""
import json, os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ART = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.normpath(os.path.join(HERE, "../../art/pebble"))
from pebble_model import NODES
from pebble_anims import ANIMS
from PIL import Image

NPC = "Common/NPC/SkyyTowns/Pebble"
DESC = {
    f"{NPC}/Pebble.blockymodel": "Pebble model, Hytale character format (64 units = 1 block), 25 nodes, boxes + quads only",
    f"{NPC}/Pebble_Texture.png": "Pebble texture 256x192 RGBA, 1 texel per unit, painted top light, hue-shifted shadows, cut-out alpha",
    "Common/Icons/ModelsGenerated/Pebble.png": "Model icon 128x128, 3/4 view like vanilla model icons, premultiplied edge pixels",
    f"{NPC}/Animations/Default/Idle.blockyanim": "Idle: slow breathing wobble, sprout sway, brow lift, blink",
    f"{NPC}/Animations/Default/Walk.blockyanim": "Walk: waddle - body rolls foot to foot, feet stay flat on the ground, arms swing",
    f"{NPC}/Animations/Default/Talk.blockyanim": "Talk: mouth opens/closes (stretch), little head bounce, brow + arm gestures",
    f"{NPC}/Animations/Default/Wave.blockyanim": "Wave: small hop, then R-Arm pebble wave with happy squint",
    f"{NPC}/Animations/Damage/Hurt.blockyanim": "Hurt: wince - lean back, eyes shut, brows down, arms out",
    f"{NPC}/Animations/Damage/Death.blockyanim": "Death: crumbles (head tips off, top slides, arms drop), holds, then pops back together",
    "source/Pebble.bbmodel": "Blockbench 5.2.1 project (Hytale Character format) with the texture and all 6 animations embedded",
    "sheet.png": "Review sheet: front / side / back, icon, one frame per animation, large labels",
    "README.md": "What it is, sizes, how to edit, what is UNVERIFIED in game, open questions for Skyy",
    "manifest.json": "This file",
}
ROLE = {
    "Origin": "root, empty, ground level (y 0)", "Body": "lower rock half; pivot near the ground so the rock rolls when it waddles",
    "Body-Wide": "rounds the lower half", "Body-Base": "rounded underside", "L-Foot": "left stubby foot", "R-Foot": "right stubby foot",
    "L-Arm": "left pebble arm", "R-Arm": "right pebble arm (waves)",
    "Head": "upper rock half with the face - ATTACH NAMEPLATE / CHAT BUBBLE HERE",
    "Head-Wide": "rounds the upper half", "Head-Bulge": "side bulge (rounder silhouette)", "Head-Top": "top step of the rock",
    "Crown": "top step, mossy", "Moss-Cap": "moss clump (sprout grows here)", "Moss-Tuft": "small moss clump",
    "Sprout": "sprout stem", "Sprout-Leaf-L": "sprout leaf", "Sprout-Leaf-R": "sprout leaf",
    "L-Eye": "left dot eye (quad)", "R-Eye": "right dot eye (quad)", "L-Eyelid": "left blink lid (quad, rest stretch y 0.1)",
    "R-Eyelid": "right blink lid (quad, rest stretch y 0.1)", "Mouth": "smile (quad, stretched to open)",
    "L-Brow": "left moss eyebrow", "R-Brow": "right moss eyebrow",
}
files = []
for rel in sorted(DESC):
    p = os.path.join(ART, rel)
    if not os.path.exists(p) and rel != "manifest.json":
        raise SystemExit("missing " + rel)
    e = {"path": rel, "size_bytes": os.path.getsize(p) if rel != "manifest.json" else None, "description": DESC[rel]}
    if rel.endswith(".png"):
        e["pixels"] = list(Image.open(p).size)
    files.append(e)
anims = []
for folder, name, fn in ANIMS:
    rel = f"{NPC}/Animations/{folder}/{name}.blockyanim"
    a = json.load(open(os.path.join(ART, rel)))
    anims.append({"name": name, "folder": folder, "path": rel, "duration_frames": a["duration"], "fps": 60,
                  "seconds": round(a["duration"] / 60, 3), "holdLastKeyframe": a["holdLastKeyframe"],
                  "loops": not a["holdLastKeyframe"], "animated_nodes": sorted(a["nodeAnimations"])})
manifest = {
    "item": "Pebble - the talking rock NPC (SkyWynn guide)",
    "repo_folder": "art/pebble",
    "original_art": True,
    "status": "made 2026-10-08, waiting for Skyy's review (not committed)",
    "model": {
        "path": f"{NPC}/Pebble.blockymodel", "format": "Hytale character (blockymodel), 64 units per block",
        "height_units": 63.2, "height_blocks": 0.99, "body_top_blocks": 0.8, "footprint_blocks": [0.95, 0.71],
        "texture": f"{NPC}/Pebble_Texture.png", "texture_size": [256, 192], "node_count": len(NODES), "max_nodes": 255,
        "faces": "+Z", "head_node": "Head", "nameplate_hint": "Head pivot is 21 units above ground; top of model is 63 units; ~45 units above the Head pivot clears the sprout",
        "nodes": [{"name": n["name"], "parent": n["parent"], "role": ROLE[n["name"]]} for n in NODES],
    },
    "animations": anims,
    "files": files,
    "generator": ["tools/art/make_pebble.py", "tools/art/pebble_model.py", "tools/art/pebble_anims.py", "tools/art/pebble_common.py",
                  "tools/art/make_pebble_previews.py", "tools/art/render_blocky.py", "tools/art/validate_pebble.py", "tools/art/make_pebble_manifest.py"],
}
with open(os.path.join(ART, "manifest.json"), "w") as fh:
    json.dump(manifest, fh, indent=2); fh.write("\n")
print("manifest written", len(files), "files")
