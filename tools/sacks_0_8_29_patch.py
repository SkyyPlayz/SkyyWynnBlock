"""Derive SkyySacks/build_skyysacks_0.8.29.py from the SET pin 0.8.28 (the GENERATED build_skyysacks_0.8.28.py; edit THIS file, then
regenerate: python tools/sacks_0_8_29_patch.py; never re-run sacks_0_8_28_patch.py on top of it). Every anchor is asserted once; at the end
every change is undone on a copy and compared with 0.8.28 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_29_patch.py   then   python SkyySacks/build_skyysacks_0.8.29.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.29.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.29 (2026-10-24) = MOB DROPS ARE COMBAT. Skyy (inventory screenshot: scraps, a Goblin Ear, a Pile of Skulls and Spider Silk loose in the
  inventory): "the scraps, the goblin ear, the pile of skills and the spider silk should all go in the combat bag. (if it drops from a mob it
  goes in combat.)" (docs/answered/bags.md 2026-10-24). The "scraps" are NOT fabric (the 0.8.9 fabric rule already bags every
  Ingredient_Fabric_Scrap_*): they are the goblins' metal Ingredient_Scraps ("Scraps"), which no rule bagged.
  SackDefs.homeOf gets one more Combat rule, MOB029 (exact ids, checked LAST - after every older rule, so no id that has a bag today moves):
  every item that a vanilla / pack-mod NPC drop list (Server/Drops/NPCs/**) gives and that no bag took, except equipment and keys:
    vanilla (Assets.zip): Ingredient_Scraps (goblins; also scrap piles), Ingredient_Spider_Silk (cave spiders, goblin burner),
      Deco_Bone_Skulls "Pile of Skulls" (burnt praetorian; Souls like Bosses' skeletons too), Ingredient_Rune_Shard "Runestone Shard",
      Ingredient_Gadget_Assembly "Dubious Assembly", Ingredient_Deep_Resource "Bundled Treasure", Ingredient_Enkindled_Resource "Enkindled
      Sigil" (goblin / skeleton elites; also chests), Ingredient_Gobliterator_Core (Gobliterator boss), Ingredient_Voidtaken_Grizzly_Hide
      (Hunt boss; not an Ingredient_Hide_ id, so the Smithing rule never took it)
    pack, by id at runtime only (PROJECT-RULES 2; no pack file read or edited by the jar): Souls like Bosses Goblin_Ear, Skeleton_Skull,
      Wolf_Paw, Goat_Horn, Eye_Of_Frenzy; Dragon Nestkeeper Ingredient_Dragon_Shed_Hide, Ingredient_Nestkeeper_Egg_Fragments (dragon NPC
      drops, not bagged -> Combat by the round default; the main session may hear otherwise from Skyy)
  LEFT ALONE: Coffer_Key (a key), Deco_Trash "Small Scrap Pile" (mostly trash containers / fishing traps, one goblin), weapons / armor /
  tools / arrows / potions (must stay usable), every id that already has a bag (raw meat + egg Farming, hides + bars Smithing, crystals /
  gems / ores / cobble Mining, raw fish Fishing, feathers / wool scraps / bones / essences Combat already), dragon eggs / saddle / spawner /
  dragon items, the Ancient Calamity seal recipe / portal, Rune_Writhing_Flame.
  The Combat "holds" line names the mob drops. Saved data / config / commands / systems / bridge keys: none changed - the pool is keyed by
  item id and only ids that had NO bag get one, so every stored stack keeps its tab and withdraws as before. ROLLBACK to 0.8.28: safe (the
  new ids stored in Combat stay in the pool file, hidden from the tabs until 0.8.29+ again - nothing deleted; they no longer go in).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.28.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.29.py"))
assert P.has('VERSION = "0.8.28"\n') and P.has("craftWhy\", new") and not P.has("MOB029"), "not the live generated SkyySacks 0.8.28"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.29 (2026-10-24)"):].rstrip() + "\n"

P.rep('''  falls back to its own text).
"""
''', '''  falls back to its own text).
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.28"\n', 'VERSION = "0.8.29"\n')

# the id list (exact ids; checked last in homeOf)
P.rep('''COMBAT_PREFIX_089 = "Ingredient_Fabric_Scrap_"
''', '''COMBAT_PREFIX_089 = "Ingredient_Fabric_Scrap_"
# 0.8.29 (Skyy "if it drops from a mob it goes in combat."): the NPC-drop items no older rule bags (survey of Assets.zip + the pack's
# Server/Drops/NPCs lists; equipment / keys / already-bagged ids left alone - patch docstring). Pack ids by id at runtime only.
MOB029_VANILLA = ("Ingredient_Scraps", "Ingredient_Spider_Silk", "Deco_Bone_Skulls", "Ingredient_Rune_Shard", "Ingredient_Gadget_Assembly",
                  "Ingredient_Deep_Resource", "Ingredient_Enkindled_Resource", "Ingredient_Gobliterator_Core",
                  "Ingredient_Voidtaken_Grizzly_Hide")
MOB029_PACK = ("Goblin_Ear", "Skeleton_Skull", "Wolf_Paw", "Goat_Horn", "Eye_Of_Frenzy",          # Souls like Bosses
               "Ingredient_Dragon_Shed_Hide", "Ingredient_Nestkeeper_Egg_Fragments")              # Dragon Nestkeeper
MOB029 = MOB029_VANILLA + MOB029_PACK
assert len(set(MOB029)) == len(MOB029) == 16
''')
P.rep('''SMITH_JAVA = " || ".join(''', '''MOB029_JAVA = " || ".join('itemId.equals("%s")' % _i for _i in MOB029)   # 0.8.29
SMITH_JAVA = " || ".join(''')
P.rep('''      || (itemId.startsWith("Ingredient_") && itemId.endsWith("_Essence"))) return "Combat";
  return null;
}""".replace("@SMITH@", SMITH_JAVA).replace("@SAP@", TREE_SAP).replace("@FABRIC@", COMBAT_PREFIX_089), defs))
''', '''      || (itemId.startsWith("Ingredient_") && itemId.endsWith("_Essence"))) return "Combat";
  // 0.8.29 (Skyy "if it drops from a mob it goes in combat."): the mob drops no rule above bags (exact ids, LAST: no bagged id moves)
  if (@MOB029@) return "Combat";
  return null;
}""".replace("@SMITH@", SMITH_JAVA).replace("@SAP@", TREE_SAP).replace("@FABRIC@", COMBAT_PREFIX_089).replace("@MOB029@", MOB029_JAVA), defs))
''')
P.rep('''            "Combat": "bones, feathers, fabric scraps, essences, venom sacs, chitin, voidhearts and boom powder",
            "Smithing": "bars and ingots, leather, hides, cloth bolts, leather straps, iron studs and charcoal"}   # 0.8.9: fabric -> Combat
''', '''            "Combat": "bones, feathers, fabric scraps, essences, venom sacs, chitin, voidhearts, boom powder and other mob drops",   # 0.8.29
            "Smithing": "bars and ingots, leather, hides, cloth bolts, leather straps, iron studs and charcoal"}   # 0.8.9: fabric -> Combat
''')
assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.8.29 adds no system / command"
P.finish()
