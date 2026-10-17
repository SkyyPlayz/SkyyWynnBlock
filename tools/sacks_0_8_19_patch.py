"""Derive SkyySacks/build_skyysacks_0.8.19.py from the SET pin 0.8.18 (the GENERATED build_skyysacks_0.8.18.py; edit THIS file, then
regenerate: python tools/sacks_0_8_19_patch.py; never re-run sacks_0_8_18_patch.py on top of it). Every anchor is asserted once; at the end
every change is undone on a copy and compared with 0.8.18 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_19_patch.py   then   python SkyySacks/build_skyysacks_0.8.19.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.19.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.19 (2026-10-17) = TEXT ONLY: the charm bag is called Void Charms everywhere a player or admin reads it (the SkyyAccessories 0.5.24 rename,
carried to this mod). Skyy 2026-10-17: "i noticed they are still called accessory's in the settings".
  1. CHAT / PAGE LINES (/craft + benches): "Equip a <bench> accessory in your Void Charms to queue more.", "Materials come from your
     inventory, the Void and your Void Charms - sorted by tier.", "equip the Campfire accessory in your Void Charms to cook here", "your
     Void Charms changed - nothing was used", " (<n> from your Void Charms)", "needs its bench accessory in your Void Charms", the bench
     line "[SkyyVoid] Make room in your inventory - the bench could not take the accessory out of your Void Charms."
  2. SERVER LOG: the two bench WARN lines ("could not go back into the Void Charms of <key>", "putting unused accessories back into Void
     Charms failed") and the ready line ("benches + /craft use Void Charms").
  Unchanged on purpose: ids, config keys, file names, bridge keys (acc:fn:bag, acc:has), permission nodes, saved data; the crafts.log ACCBAG
  lines (a data log: "moved from the bag to the inventory"); single items stay "accessory" ("the Campfire accessory", "accessory not
  equipped", "equip a <bench> accessory to queue"); the Void's own Magic Bags / bag words (they are this mod's bags, not the charm bag);
  the Workbench tab "Bags" (tools/skyywbtab.py, SkyyAccessories owns it); code comments.
  ROLLBACK to 0.8.18: safe (same files, same keys).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.18.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.19.py"))
assert P.has('VERSION = "0.8.18"\n') and P.has("supply:fn:claims") and P.has("tools/sacks_0_8_18_patch.py"), "not the live generated SkyySacks 0.8.18"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.19 (2026-10-17)"):].rstrip() + "\n"

# ---- header, version
P.rep('''  Saved data: none changed; no command / system / class / bridge key added. ROLLBACK to 0.8.17: safe (claimed ids go into the Void again;
  the Flask / Pouch already never matched a Void rule).
"""
''', '''  Saved data: none changed; no command / system / class / bridge key added. ROLLBACK to 0.8.17: safe (claimed ids go into the Void again;
  the Flask / Pouch already never matched a Void rule).
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.18"\n', 'VERSION = "0.8.19"\n')

# ---- 1. chat / page lines
P.rep('''("[SkyyVoid] Make room in your inventory - the bench could not take the accessory out of your Accessory Bag."));''',
      '''("[SkyyVoid] Make room in your inventory - the bench could not take the accessory out of your Void Charms."));''')
P.rep('''" accessory in your accessory bag to queue more."''', '''" accessory in your Void Charms to queue more."''')
P.rep('''"Materials come from your inventory, the Void and your Accessory Bag - sorted by tier."''',
      '''"Materials come from your inventory, the Void and your Void Charms - sorted by tier."''')
P.rep('''return "equip the Campfire accessory in your accessory bag to cook here";''',
      '''return "equip the Campfire accessory in your Void Charms to cook here";''')
P.rep('''return "your Accessory Bag changed - nothing was used";''', '''return "your Void Charms changed - nothing was used";''')
P.rep('''accNote = " (" + fromBag + " from your Accessory Bag)";''', '''accNote = " (" + fromBag + " from your Void Charms)";''')
P.rep('''return "needs its bench accessory in your accessory bag";''', '''return "needs its bench accessory in your Void Charms";''')

# ---- 2. server log lines
P.rep('''" could not go back into the Accessory Bag of " + k + " - dropped at the player instead");''',
      '''" could not go back into the Void Charms of " + k + " - dropped at the player instead");''')
P.rep('''"bench: putting unused accessories back into the Accessory Bag failed: " + t);''',
      '''"bench: putting unused accessories back into Void Charms failed: " + t);''')
P.rep('''benches + /craft use the Accessory Bag (SkyyAccessories 0.5.19 acc:fn:bag)''', '''benches + /craft use Void Charms (SkyyAccessories 0.5.19 acc:fn:bag)''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.8.19 adds no system / command"
P.finish()
