"""Derive SkyySacks/build_skyysacks_0.8.34.py from the SET pin 0.8.33 (the GENERATED build_skyysacks_0.8.33.py; edit THIS file, then
regenerate: python tools/sacks_0_8_34_patch.py; never re-run sacks_0_8_33_patch.py on top of it). Every anchor is asserted once; at the end
every change is undone on a copy and compared with 0.8.33 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_34_patch.py   then   python SkyySacks/build_skyysacks_0.8.34.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.34.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.34 (2026-10-30) = AUGMENTS INTO THE COMBAT BAG (Augments round A2 with SkyyGear 0.3.52; research/Augments-Spec.md 2.4 "Combat bag (homeOf
  startsWith Skyy_Aug_ -> Combat)"; Skyy 2026-10-25 AUGMENTS REPLACE POWDERS; the 0.8.29 rule "if it drops from a mob it goes in combat.").
  SackDefs.homeOf: every id starting Skyy_Aug_ (SkyyGear's 120 augment items: 13 stat kinds x 5 (Swift / Sage since aug2b), Poison x 5, 5 elements x 10 -
  plain items, no metadata) -> "Combat", checked before the generic Skyy_ rule (which would answer null = no bag). So pickups, Deposit all, withdraw,
  /craft + the benches (the Alchemy Bench fuse recipes) and sacks:fn:count / take / put / commit (SkyyGear's Anvil > Augments takes from the
  bags) all see them. RecipeCmp's /craft sort table is re-baked from tools/tier_tags.py at build time (it gained the 120 augment rows:
  they sort by tier in /craft). Nothing else changes.
  No saved-data change (the pool is keyed by item id), no config row, no migration, no new system / command. ROLLBACK to 0.8.33: augments
  stored in a bag stay in the pool (keyed by id) but no longer show / auto-sort until 0.8.34 is back (they are not lost).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.33.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.34.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.8.33"\n') and P.has("fieldRecipe(") and not P.has("Skyy_Aug_"), "not the live generated SkyySacks 0.8.33"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.34 (2026-10-30)"):].rstrip() + "\n"

P.rep('''  changes only on a pocket craft -> one new layout, no refresh ping-pong).
  No saved-data change, no config row, no migration, no new system / command. ROLLBACK to 0.8.32: safe alone (pocket ALL back to the
  one-stack offer; nothing stored).
"""
''', '''  changes only on a pocket craft -> one new layout, no refresh ping-pong).
  No saved-data change, no config row, no migration, no new system / command. ROLLBACK to 0.8.32: safe alone (pocket ALL back to the
  one-stack offer; nothing stored).
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.33"\n', 'VERSION = "0.8.34"\n')
P.rep('''  if (itemId.startsWith("Skyy_")) return cooked(itemId) ? "Farming" : null;
''', '''  // 0.8.34 (Augments A2, SkyyGear 0.3.52): SkyyGear's augment items (Skyy_Aug_<Kind>_<n>, plain stacks) belong to the Combat bag
  if (itemId.startsWith("Skyy_Aug_")) return "Combat";
  if (itemId.startsWith("Skyy_")) return cooked(itemId) ? "Farming" : null;
''')
P.rep('''; pocket ALL / x10 offer the last recipe's inputs (0.8.33)");''', '''; pocket ALL / x10 offer the last recipe's inputs (0.8.33); SkyyGear augments (Skyy_Aug_*) -> Combat (0.8.34)");''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.8.34 adds no system / command"
P.finish()
