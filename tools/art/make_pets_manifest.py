#!/usr/bin/env python3
"""Write art/pets/manifest.json: every file (path, bytes, what), per pet: nodes, animations, sizes, proposed ids."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from pets_models import PETS
ART = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.normpath(os.path.join(HERE, "../../art/pets"))
ROLE = {"Rabbit": "skill pet - Farming", "Chicken": "skill pet - Farming", "Goat": "skill pet - Mining", "Warthog": "skill pet - Mining",
        "Bear": "skill pet - Foraging", "Turkey": "skill pet - Foraging", "Wolf": "combat pet", "Boar": "combat pet",
        "Hawk": "class pet - Archer", "Ram": "class pet - Warrior + mount", "Skrill": "class pet - Mage", "Tusker": "class pet - Berserker",
        "Mouflon": "class pet - Priest + mount", "Horse": "mount pet", "Camel": "mount pet"}
files = []
for dp, dn, fn in os.walk(ART):
    for f in sorted(fn):
        p = os.path.relpath(os.path.join(dp, f), ART)
        what = ("model" if f.endswith(".blockymodel") else "texture" if f.endswith("_Texture.png") else "animation" if f.endswith(".blockyanim")
                else "model icon 128x128" if "ModelsGenerated" in p else "item icon 64x64" if "ItemsGenerated" in p
                else "Blockbench project" if f.endswith(".bbmodel") else "review sheet" if f == "sheet.png" else "doc")
        files.append({"path": p.replace(os.sep, "/"), "bytes": os.path.getsize(os.path.join(dp, f)), "what": what})
files.sort(key=lambda x: x["path"])
pets = {}
for pet in PETS:
    root = f"Common/NPC/SkyyPets/{pet}"
    model = json.load(open(os.path.join(ART, root, "Models", pet + ".blockymodel")))
    names = []
    def walk(n):
        names.append(n["name"]); [walk(c) for c in n.get("children", [])]
    [walk(n) for n in model["nodes"]]
    from PIL import Image
    tw, th = Image.open(os.path.join(ART, root, "Models", pet + "_Texture.png")).size
    anims = []
    for f in sorted(os.listdir(os.path.join(ART, root, "Animations/Default"))):
        a = json.load(open(os.path.join(ART, root, "Animations/Default", f)))
        anims.append({"name": f[:-11], "file": f"{root}/Animations/Default/{f}", "frames_60fps": a["duration"],
                      "seconds": round(a["duration"] / 60, 3), "loops": not a["holdLastKeyframe"], "nodes": sorted(a["nodeAnimations"])})
    spec = PETS[pet]()
    boxes = sum(1 for n in spec["nodes"] if n["shape"] and n["shape"][0] == "box"); quads = sum(1 for n in spec["nodes"] if n["shape"] and n["shape"][0] == "quad")
    pets[pet] = {"role": ROLE[pet], "model": f"{root}/Models/{pet}.blockymodel", "texture": f"{root}/Models/{pet}_Texture.png",
                 "texture_size": [tw, th], "nodes": len(names), "boxes": boxes, "quads": quads, "tris": boxes * 12 + quads * 2,
                 "node_names": names, "animations": anims, "rig": spec["rig"], "mount": bool(spec.get("mount")),
                 "attach": {"nameplate": "Head", "rider_seat": "Saddle" if "Saddle" in names else None},
                 "proposed_ids": {"npc_model": f"SkyyPets_{pet}", "pet_item": f"SkyyPets_Pet_{pet}",
                                  "item_icon": f"Icons/ItemsGenerated/SkyyPets_Pet_{pet}.png", "model_icon": f"Icons/ModelsGenerated/SkyyPets_{pet}.png",
                                  "name_key": f"skyypets.pet.{pet.lower()}.name"},
                 "scale_note": "files are the Lv 100 (1.0x) size; Pets-Spec 6: 0.6x at Lv 1"}
out = {"item": "pets (ART-RESUME queue #7)", "status": "DRAFT for Skyy's review - not committed", "units": "64 = 1 block, 1 unit = 1 texel",
       "format": "Hytale Models plugin 0.10.0 'character' (64 px/block), shading flat, Blockbench 5.2.1",
       "pets": pets, "files": files}
json.dump(out, open(os.path.join(ART, "manifest.json"), "w"), indent=1)
print(len(files), "files")
