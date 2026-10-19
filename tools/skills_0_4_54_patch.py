"""Derive SkyySkills/build_skyyskills_0.4.54.py from the GENERATED SkyySkills 0.4.53 (build_skyyskills_0.4.53.py = the tools/deploy_set.py SET
pin; 0.4.53 came from 0.4.52 by tools/skills_0_4_53_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). rep(old, new) with asserted single anchors; at the end every change is undone on a copy and compared with
0.4.53 (nothing else changed); 0.4.53 stays untouched, its line endings are kept (tools/soundpass_gen.Patch).
Run:  python tools/skills_0_4_54_patch.py   then   python SkyySkills/build_skyyskills_0.4.54.py   (never --deploy)
      then  python SkyySkills/test_skyyskills_0.4.54.py

Queued item (RESUME, from tools/skills_0_4_53_patch.py item 4: "Enchanted alloys (no table row) pay smithing.smeltDefault once a smelt
(follow-up: their own rows)") = "Enchanted alloy Smithing XP rows".
ROLLBACK to 0.4.53: harmless - 0.4.53 reads the 6 smithing.xp.Skyy_Ench_* lines as ordinary table rows (it would pay them too); without the
lines (removed in Server Setup or the config-history copy "before the 0.4.54 Enchanted alloys XP update") it pays smithing.smeltDefault again.
No player file, no new command / system / bridge key.
"""
import os, sys, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

# ---- the values. NO Enchanted metal row exists in the SMITH_XP table (Enchanted Iron / Copper ... are never smelted - they are compressed at
# the Workbench), so the task's fallback rule applies: (bars in the Enchanted recipe) x (the alloy bar's XP) x 0.5. Every Enchanted alloy's own
# recipe is 100 bars (SkyyCollections: 100 Ingredient_Bar_<Alloy> -> 1 Skyy_Ench_<Alloy>, tools/skyyench.py RATIO 100).
# A SkyyAlloy smelt (SkyyWorldGen Alloy_Ench_<Alloy>: 1 Enchanted A + 1 Enchanted B -> 2 Enchanted alloy) pays the row ONCE (0.4.53 rule), so
# one Enchanted smelt = 200 alloy bars = 100 plain smelts' worth, paid at half: 100 x bar XP x 0.5 = 50 x bar XP.
EN_RATIO, EN_FACTOR = 100, 0.5
EN_BAR = [("Bronze", 16), ("Dusk", 45), ("Azurvane", 38), ("Cinder", 75), ("Lumen", 63), ("Electrum", 28)]   # = the 0.4.49 alloy rows
EN_SMITH = [("Skyy_Ench_" + _n, int(EN_RATIO * _x * EN_FACTOR + 0.5)) for _n, _x in EN_BAR]
assert EN_SMITH == [("Skyy_Ench_Bronze", 800), ("Skyy_Ench_Dusk", 2250), ("Skyy_Ench_Azurvane", 1900), ("Skyy_Ench_Cinder", 3750),
                    ("Skyy_Ench_Lumen", 3150), ("Skyy_Ench_Electrum", 1400)], EN_SMITH
EN_LINES = [("smithing.xp.%s" % _i, str(_x)) for _i, _x in EN_SMITH]
EN_IDS = [_i for _i, _x in EN_SMITH]
EN_MARK_ID = "SkyySkills 0.4.54 Enchanted alloys"
EN_MARK = "# SkyySkills 0.4.54 Enchanted alloys: Smithing XP per SkyyAlloy smelt of each Enchanted alloy (100 bars x the bar XP x 0.5)."
EN_HEAD = ["# ---------- " + EN_MARK_ID + " ----------", EN_MARK,
           "# One smelt (1 + 1 Enchanted ingots -> 2 Enchanted alloy, SkyySacks /craft Furnace) pays the row once."]
for _x in EN_HEAD:
    assert "=" not in _x and _x.startswith("# ") and len(_x) <= 140 and all(ord(_ch) < 128 for _ch in _x), _x

NOTE = '''0.4.54 (2026-10-19) = ENCHANTED ALLOY SMITHING XP ROWS (the follow-up 0.4.53 item 4 named: "Enchanted alloys (no table row) pay
  smithing.smeltDefault once a smelt (follow-up: their own rows)").
  1. SMITHING XP (smithing.xp.<id>, paid ONCE per SkyyAlloy smelt - RecipeXp.classify, 0.4.53): Skyy_Ench_Bronze 800, Skyy_Ench_Dusk 2250,
     Skyy_Ench_Azurvane 1900, Skyy_Ench_Cinder 3750, Skyy_Ench_Lumen 3150, Skyy_Ench_Electrum 1400. RULE: no Enchanted metal row exists to copy a
     ratio from, so (bars in the Enchanted recipe 100) x (the alloy bar's XP: 16 / 45 / 38 / 75 / 63 / 28) x 0.5. One smelt makes 2 Enchanted
     = 200 alloy bars = 100 plain smelts, so the Enchanted route pays half the plain route's Smithing XP for the same bars (no XP farm through
     compress -> smelt). The ids are SkyyCollections' (tools/skyyench.py Skyy_Ench_<Alloy>), CHECKED against the SET SkyyCollections jar.
  2. DEFAULTS: the rows are in SmithCfg.defaultsMap, so a file without the lines already pays them; a fresh file has them in its Smithing
     section + the marker.
  3. MIGRATION En54Mig (a clone of Zo49Mig / Fa53Mig's reviewed block-append machinery) ONCE on an EXISTING xp.properties (setup, after
     Fa53Mig, before SkillCfg.load): ONE block (marker head + only the lines the file lacks; an admin's own line kept) appended in the file's
     line ending; no existing line changes (Properties check); config-history copy first; atomicWrite; one INFO line.
  No saved player data change, no new command / system / bridge key. ROLLBACK to 0.4.53: harmless (it reads the lines as table rows; without
  them it pays smithing.smeltDefault again).
'''

P = G.Patch(os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.53.py"), os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.54.py"))
assert P.has('VERSION = "0.4.53"') and P.has("Fa53Mig") and not P.has("En54Mig"), "not the generated SkyySkills 0.4.53 script"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")

# ================================================================================================ docstring + version
P.rep('''"""SkyySkills 0.4.53 - build script (derived from the generated 0.4.52 by tools/skills_0_4_53_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.54 - build script (derived from the generated 0.4.53 by tools/skills_0_4_54_patch.py - edit the patch, not this file;
''' + NOTE + '''  CHECKED: SkyySkills/test_skyyskills_0.4.54.py.
0.4.53 was derived from the generated 0.4.52 by tools/skills_0_4_53_patch.py;
''')
P.rep('VERSION = "0.4.53"', 'VERSION = "0.4.54"')

# ================================================================================================ the ids (SkyyCollections makes them)
P.rep('''ITEM_IDS |= set(ZO_IDS)
''', '''ITEM_IDS |= set(ZO_IDS)
# 0.4.54: the Enchanted alloys are SkyyCollections' items (tools/skyyench.py) - CHECKED against the SET pin's SkyyCollections jar
import ast as _ast54
EN_IDS = ''' + json.dumps(EN_IDS) + '''
_t54 = _ast54.parse(open(os.path.join(HERE, "..", "tools", "deploy_set.py"), encoding="utf8").read())
_set54 = [dict(_ast54.literal_eval(n.value)) for n in _t54.body if isinstance(n, _ast54.Assign) and any(getattr(x, "id", "") == "SET" for x in n.targets)][0]
_cj54 = os.path.join(HERE, "..", "SkyyCollections", "SkyyCollections-%s.jar" % _set54["SkyyCollections"])
assert os.path.isfile(_cj54), "0.4.54: the SET SkyyCollections jar (Enchanted alloy ids) is not built: " + _cj54
with zipfile.ZipFile(_cj54) as _zc54:
    _have54 = set(os.path.basename(n)[:-5] for n in _zc54.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
assert not [i for i in EN_IDS if i not in _have54], "0.4.54: %s misses Enchanted alloy ids: %s" % (os.path.basename(_cj54), [i for i in EN_IDS if i not in _have54])
ITEM_IDS |= set(EN_IDS)
print("0.4.54: %d Enchanted alloy ids checked against %s" % (len(EN_IDS), os.path.basename(_cj54)))
''')

# ================================================================================================ the default file: SMITH_XP rows + the marker
P.rep(''', ('Ingredient_Bar_Electrum_SkyWynn', 28)] + [("Potion_Empty", 2), ("Ingredient_Charcoal", 0)]   # 0.4.49: + the zone ingots + alloys''',
      ''', ('Ingredient_Bar_Electrum_SkyWynn', 28)] + ''' + repr(EN_SMITH) + ''' + [("Potion_Empty", 2), ("Ingredient_Charcoal", 0)]   # 0.4.54: + the Enchanted alloys; 0.4.49: + the zone ingots + alloys''')
P.rep('''SMITH_L.append(ZO_MARK)   # 0.4.49''', '''EN54_MARK_ID = "''' + EN_MARK_ID + '''"
EN54_MARK = "''' + EN_MARK + '''"
EN54_HEAD = ''' + repr(EN_HEAD) + '''
SMITH_L.append(EN54_MARK)   # 0.4.54: En54Mig's run-once marker (a fresh file only; its rows are in the SMITH_XP lines above)
SMITH_L.append(ZO_MARK)   # 0.4.49''')
P.rep('''assert DEFAULTS.count(ZO_MARK_ID) == 1 and all(_dp.get(_k)''', '''assert DEFAULTS.count(EN54_MARK_ID) == 1 and all(_dp.get(_k) == _v for _k, _v in ''' + repr(EN_LINES) + '''), "0.4.54: the default file holds the 6 Enchanted alloy rows + the marker"
assert DEFAULTS.count(ZO_MARK_ID) == 1 and all(_dp.get(_k)''')

# ================================================================================================ En54Mig = Zo49Mig's code, the 6 lines
P.rep('''fa53 = pool.makeClass(PKG + ".Fa53Mig")        # 0.4.53: the one-time Farming level list block appended to an existing xp.properties
''', '''fa53 = pool.makeClass(PKG + ".Fa53Mig")        # 0.4.53: the one-time Farming level list block appended to an existing xp.properties
en54 = pool.makeClass(PKG + ".En54Mig")        # 0.4.54: the one-time Enchanted alloy Smithing XP lines appended to an existing xp.properties
''')
_a = P.s.index('zo49.addField(CtField.make("public static final String MARK_ID = %s;" % json.dumps(ZO_MARK_ID), zo49))')
_m = P.s.index('# pure text step. null = nothing to do; else { new text, String[] added keys }', _a)
_e = P.s.index('could not update xp.properties for 0.4.49', _m)
_e = P.s.index('}"""), zo49))\n', _e) + len('}"""), zo49))\n')
CL = '''en54.addField(CtField.make("public static final String MARK_ID = %s;" % json.dumps(EN54_MARK_ID), en54))
en54.addField(CtField.make("public static final String HEAD = %s;" % json.dumps("\\n".join(EN54_HEAD) + "\\n"), en54))
en54.addField(CtField.make("public static final String[] KEYS = %s;" % jarr([_k for _k, _v in ''' + repr(EN_LINES) + ''']), en54))
en54.addField(CtField.make("public static final String[] VALS = %s;" % jarr([_v for _k, _v in ''' + repr(EN_LINES) + ''']), en54))
en54.addField(CtField.make('public static final String WHO = "SkyySkills 0.4.54";', en54))
assert all(("\\n" + _k + "=" + _v + "\\n") in ("\\n" + DEFAULTS) for _k, _v in ''' + repr(EN_LINES) + '''), "0.4.54: an En54Mig line is not the default file's"
''' + P.s[_m:_e]


def _sub(t, o, n):
    assert t.count(o) >= 1, o
    return t.replace(o, n)


CL = _sub(CL, "zone ores + alloys XP", "Enchanted alloys Smithing XP")
CL = _sub(CL, "before the 0.4.49 zone ores XP update", "before the 0.4.54 Enchanted alloys XP update")
CL = _sub(CL, "(Mining XP for the zone ores, Smithing XP for their ingots and the alloys)", "(Smithing XP for the 6 Enchanted alloys)")
CL = CL.replace("0.4.49", "0.4.54").replace("zo49", "en54")
assert "zo49" not in CL and "0.4.49" not in CL and "zone" not in CL and "Mining XP" not in CL, [l for l in CL.splitlines() if "zone" in l or "49" in l][:5]
EN_JAVA = """
# ---- En54Mig (0.4.54; a clone of Zo49Mig's reviewed block-append machinery): ONCE on an EXISTING xp.properties, setup() right after
# Fa53Mig.run, BEFORE SkillCfg.load. Nothing to do = no file or a comment line holding MARK_ID (a fresh default file carries it). Else ONE
# block appended after the last line in the file's own line ending: the head (marker) + ONLY the 6 smithing.xp.Skyy_Ench_* lines the file
# lacks (an admin's own line kept as it is). No existing line changes (Properties check), config-history copy first, atomicWrite, one INFO
# line. A failure = WARN, file untouched, retried next start. (The rows are in SmithCfg.defaultsMap too - a file without them pays them.)
""" + CL
P.rep('''
# ================= SkillIO.run (0.4.32 C): the SkyySkills-IO jobs''', EN_JAVA + '''
# ================= SkillIO.run (0.4.32 C): the SkyySkills-IO jobs''')
P.rep('''  {PKG}.Fa53Mig.run();        // 0.4.53: Farming's own level list into an existing xp.properties, once; History first
''', '''  {PKG}.Fa53Mig.run();        // 0.4.53: Farming's own level list into an existing xp.properties, once; History first
  {PKG}.En54Mig.run();        // 0.4.54: the Enchanted alloy Smithing XP lines into an existing xp.properties, once; History first
''')
P.rep('''nc53, fa53, lvf, ob50,''', '''nc53, fa53, en54, lvf, ob50,''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
P.finish()
print("wrote SkyySkills/build_skyyskills_0.4.54.py (%d changes); Enchanted alloy rows %s" % (len(P.changes), EN_SMITH))
