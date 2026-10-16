"""Derive SkyySacks/build_skyysacks_0.8.13.py from the SET pin 0.8.12 (the GENERATED build_skyysacks_0.8.12.py; edit THIS file, then
regenerate: python tools/sacks_0_8_13_patch.py; never re-run sacks_0_8_12_patch.py on top of it). Every anchor is asserted; at the end every
change is undone on a copy and compared with 0.8.12 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_13_patch.py   then   python SkyySacks/build_skyysacks_0.8.13.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.13.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.13 = /recipes LEAVES /craft (round hubcoll, 2026-10-16, with SkyyCollections 0.2.22). Skyy's words: LOCKED 2026-10-10 (docs/answered/ui.md)
"Collections + Recipes (recipes shown inside each collection)"; popup 2026-10-16 -> "Merge now". research/Hubs-Spec.md 1.2 footnote: /recipes
was an alias in BOTH SkyySacks and SkyyCollections (the last one registered wins); Collections keeps it, SkyySacks drops it. So CraftCmd no
longer adds the alias "recipes" (/craft, /craft <words> unchanged); /recipes is SkyyCollections 0.2.22's command (the merged Collections tab).
Nothing else changes: the tier sort table and the Enchanted Void homes are FROZEN to the tables 0.8.12 was built with (tools/tier_tags.py
+ tools/skyyench.py at 52298ac, read from git by this patch) - the 83 C1 Enchanted rows join in the queued Sacks round. No saved data.
ROLLBACK to 0.8.12: safe (roll SkyyCollections back to 0.2.21 with it: two /recipes owners otherwise).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)
import subprocess, types

# The tables 0.8.12 was built with: tools/skyyench.py + tools/tier_tags.py at 52298ac (the 0.8.12 docstring). The C1 rows that joined them
# since (SkyyCollections 0.2.21: 83 Enchanted items) get their Void homes + sort rows in the QUEUED Sacks round (RESUME: "Sacks rebuild
# (homes for 103 rows, Combat / Smithing cats)"), not here: this round changes only the alias. Read from git (read only), frozen as literals.
BUILT_WITH = "52298ac"


def _old_module(rel, name):
    src = subprocess.check_output(["git", "-C", ROOT, "show", BUILT_WITH + ":" + rel]).decode("utf8")
    m = types.ModuleType(name + "_" + BUILT_WITH)
    m.__file__ = os.path.join(ROOT, rel)
    exec(compile(src, rel + "@" + BUILT_WITH, "exec"), m.__dict__)
    return m


OEN = _old_module("tools/skyyench.py", "skyyench")
OTT = _old_module("tools/tier_tags.py", "tier_tags")


def _tt_grp(i):   # = the build script's _tt_grp on the OLD table
    f = OTT.family(i)
    if f == "crop":
        return i[len("Plant_Crop_"):-len("_Item")], 0
    if f == "seed":
        if i.endswith("_Eternal"):
            return i[len("Plant_Seeds_"):-len("_Eternal")], 3
        return i[len("Plant_Seeds_"):], 2
    if f == "enchanted":
        _b = dict(OTT.ENCH_BASE).get(i[len("Skyy_Ench_"):])
        if _b and OTT.family(_b) == "crop":
            return _b[len("Plant_Crop_"):-len("_Item")], 1
    return "", 9


F_IDS = sorted(OTT.ROWS)
F_TIERS = [OTT.tier(_i) for _i in F_IDS]
F_GRPS = [_tt_grp(_i) for _i in F_IDS]
F_HOME = OEN.sacks_home_java()
assert len(OEN.TABLE) == 20 and "Skyy_Ench_Stick" in F_HOME, "52298ac: the 20 Enchanted rows (the Enchanted Stick last)"

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.12.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.13.py"))
assert P.has('VERSION = "0.8.12"\n') and P.has("PdOnce") and P.has('  addAliases(new String[] { "recipes" });\n'), "not the live generated SkyySacks 0.8.12"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.13 = /recipes LEAVES"):].rstrip() + "\n"

# ================================================================================================ header, version
P.rep('''  ROLLBACK to 0.8.11: safe (the lifelong/ folder is ignored; /pocket is gone, /pd still gives the item).
"""
''', '''  ROLLBACK to 0.8.11: safe (the lifelong/ folder is ignored; /pocket is gone, /pd still gives the item).
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.12"\n', 'VERSION = "0.8.13"\n')

# ================================================================================================ /craft: no /recipes alias
P.rep('''  super("craft", "Open inventory crafting (materials from your inventory and the Void) - /craft <words> opens it searching");
  addAliases(new String[] { "recipes" });
''', '''  super("craft", "Open inventory crafting (materials from your inventory and the Void) - /craft <words> opens it searching");
''')

# ================================================================================================ the frozen tables (see BUILT_WITH)
P.rep('''TT_IDS = sorted(TT.ROWS)
TT_TIERS = [TT.tier(_i) for _i in TT_IDS]
TT_GRPS = [_tt_grp(_i) for _i in TT_IDS]
''', '''# 0.8.13: FROZEN to the table 0.8.12 was built with (tools/tier_tags.py at %s; tools/sacks_0_8_13_patch.py) - the C1 rows join in the
# queued Sacks round (homes for 103 rows), not in this alias-only round
TT_IDS = %r
TT_TIERS = %r
TT_GRPS = %r
''' % (BUILT_WITH, F_IDS, F_TIERS, F_GRPS))
P.rep('''defs.addMethod(CtNewMethod.make(EN.sacks_home_java(), defs))
''', '''# 0.8.13: FROZEN to tools/skyyench.py at %s (the 20 rows 0.8.12 homes; tools/sacks_0_8_13_patch.py)
SACKS_HOME_JAVA = %r
defs.addMethod(CtNewMethod.make(SACKS_HOME_JAVA, defs))
''' % (BUILT_WITH, F_HOME))

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "no system / command added or removed"
assert 'addAliases(new String[] { "recipes" })' not in P.s
P.finish()
