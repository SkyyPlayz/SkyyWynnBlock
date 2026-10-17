"""Derive SkyyGear/build_skyygear_0.3.17.py from the LIVE 0.3.16 (build_skyygear_0.3.16.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_3_16_patch.py). Edit THIS file, never the generated script; every anchor is asserted and every change is undone at the end to
prove nothing else changed. Run:
    python tools/gear_0_3_17_patch.py      then      python SkyyGear/build_skyygear_0.3.17.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.3.17.py

0.3.17 (2026-10-16) = ROUND T1, TOOL UPGRADES (research/Collections-Tools-Redesign-Spec.md section 6 + the LAST section = Skyy's answers, word for
word in docs/answered/gear.md + economy.md 2026-10-16). Skyy's words: "remove the cap on the tools speed upgrade. like in the skill tree, lets have
breaking power(amount of damage it does to the block. the higher it is the less hits.) and breaking/swing speed. (tool swings faster. needed to
increase mining speed once a block breaks in 1 hit.) i wouldnt cap either. and id make the fortune caps really high too. (past 100% chance to drop
double, it goes to a triple drop chance. so 200% is guaranteed 3 drops. no max %)" + "lets drop the scaling. keep it to 1 point is 1 level" ->
"perfect, lets use that" + popup "Yes, 10 levels per tier (Recommended)" + "things like vein mine and tree feller should be capped by the tools
level (so your skill level.) and not the tier ... the tool can cap at like 6 and the tree can give like 4 for a total of 10." + "make vein mine and
tree feller cheap to buy at first, but really expensive to max on the tool. (like double price every time.)" + "i like the two pools idea ... so
when breaking logs it uses the hatchet spec, and when mining it uses the pickaxe specs" + REQUIP SELL = SALVAGE popup "Salvage to materials
(Recommended)" (docs/answered/bags.md: "returns part of the materials the piece took (e.g. 25-50% of its ingots / Enchanted items), never coins").
1. THE THREE LINES (LL_PERKS; the saved order is locked, the new line is APPENDED; saved by key):
   - Breaking Power (key spd, was "Speed"): +lifelong.perkSpeed % Mining / Chopping Power a level (default 2 -> 5);
   - Breaking Speed (key swing, NEW, appended): +lifelong.perkSwing % swing speed a level (default 3). STORED + SHOWN + published as the bridge
     Double gear:swing:<uuid> (the held lifelong pickaxe / hatchet's %); SkyyTrees applies it in round T2 and lists "swing" in gear:perk:readers -
     until then the Tools tab says "Comes with the next SkyyTrees update" and the line cannot be bought (the Vein Mine / Tree Feller rule);
   - Fortune (key fort): +lifelong.perkFortune a level (default 1 -> 2).
   Each costs a FLAT lifelong.lineCost point a level (1). No hard max: each line caps at lifelong.lineCapPerTier x the tool's tier (10: Crude 10,
   Copper 20, Iron 30 ...; the TOP tier of the tool's ladder is uncapped; 0 = no tier cap). Points above the cap stay banked (free points wait).
2. NO TOOL CAPS: tool.fortune.cap 25 -> 0 = none (GearCfg.fcap()); the Power clamp x100 -> the row tool.power.max (1000, a sanity guard).
3. VEIN MINE / TREE FELLER (the tool part): max lifelong.abilityMax (6) levels, level n needs TOOL level n x lifelong.abilityLevelStep (8: Lv 8,
   16, 24, 32, 40, 48 - the tool level = your skill level inside the tier's band), level n costs lifelong.abilityCost x 2^(n-1) (1, 2, 4, 8, 16,
   32 = 63 for all six). No tier need any more. gear:fn:perk answers the level the tool may use now (SkyyTrees adds its tree levels on top).
4. POINTS: earned = (skill level - 1) + SkyyCollections' coll:fn:toolPts {profile key, skill} (lifelong.collPoints, cached 2 s; no SkyyCollections
   = 0). Each kind its own pool (pickaxe = Mining, hatchet = Foraging ...).
5. THE MULTITOOL'S TWO SETS: a lifelong multitool (none exist yet - the lifelong merge is its own round) uses the PICKAXE kind's lines on stone /
   ore and the HATCHET kind's on logs (GearTool.mstats adds GearLL.perkFx(fam 1) and (fam 3) to its two sides); Mining points upgrade the pickaxe
   set, Foraging points the hatchet set - the two pools already are per kind.
6. THE COLLECTION TIER-UP GATE (lifelong.collGate): a lifelong tool tier-up asks SkyyCollections coll:fn:tierup {profile key, "<kind>:<Tier>"}
   (pickaxe / hatchet / harvester / can; the pole climbs at the Fishing Bench): null = not gated (open), "1|..." unlocked, "0|Id|Name|tier|need|have"
   = refused "Needs the Iron Ore collection IV (312 / 500) to tier up to ...". No SkyyCollections / an error = open (logged once).
7. ONE-TIME UPDATES (PROJECT-RULES 4):
   a. config.properties migrate0317 (the migrate0314 machinery): lifelong.perkSpeed 2 -> 5, lifelong.perkFortune 1 -> 2, tool.fortune.cap 25 -> 0,
      only a one-line entry still holding exactly the old default (number compare); hand-edited kept + noted; verified History copy first; one
      config-changes.log row each (Undo); the marker at the end (a fresh file carries it); every other byte + line ending kept.
   b. the per-profile registry (GearLife.t1Mig, in the lifelong look before the pass): a saved LINE level above its 10 x tier cap is lowered to
      the cap - its points are free again (spent is derived from the levels: nothing is lost). Vein Mine / Tree Feller are never lowered (their
      cap follows the skill level and is applied live by perkEff - critic fix). Verified history copy (lifelong/history/<pk>.pre-0.3.17.properties)
      before any lowering, marker t1=1, a gear.log LL-T1MIG line per change + one chat line. Cost changes need no migration (spent is derived:
      Vein Mine / Tree Feller 3 / 5 / 8 -> 1 / 2 / 4 gives points back by itself; the flat 1-point lines cost what they cost).
8. SALVAGE BRIDGE gear:fn:salvage (for SkyyWardrobe's Requip SALVAGE button, a later round): Object[] { UUID, String itemId, BsonDocument metadata,
   String mode } or Object[] { UUID, BsonDocument itemDoc {Id, Metadata}, String mode }; mode "quote" (default), "commit" or "release" ->
   Object[] { String why (null = fine), String[] ids, Long[] qty, String key }. Skyy's popup answer (bags.md 2026-10-16) "Drops give less
   (Recommended)": a CRAFTED piece (gear document src "craft" - every crafted / Smithing roll - or "merge", a multitool made from crafted tools)
   gives salvage.pct[rarity] % (25,30,35,40,45,50 Normal..Mythic) of its crafting recipe + every tier-up step's cost along its upgrade ladder;
   any other piece (mob / chest / bag drops, quests, legacy) counts as DROPPED and gives only salvage.dropPct % (10) of its BASE recipe (the
   piece's own recipe, else its ladder's first piece's - no tier-up materials). Rounded down, at least 1 of the biggest input. NEVER coins
   (no coin path at all - U3). Lifelong tools, unidentified pieces and pieces with no recipe are refused. The KEY = item id + the document's
   birth stamps (at, b0) + its rolls (mods) - stable while the piece is used. "commit" records the key in the per-profile journal
   Skyy_SkyyGear/salvage/<pk>.properties BEFORE it answers (atomic write) - the same piece is refused a second time; "release" takes a key
   back out (the caller's removal failed after a commit). CALLER CONTRACT (SkyyWardrobe Requip): quote (show it) -> remove the piece (journaled)
   -> commit -> give the materials storage-first; the removal failed after the commit -> release; the commit refused -> put the piece back.
   salvage.on switches it off.
Commands: none added or removed. Pages: the Tools (Upgrade) tab rows show the caps ("Lv 12 / 20 (Copper cap)"), Breaking Speed's row, the
collection points; 6 perk rows fit (smaller rows when 5+). Server Setup rows (new): lifelong.perkSwing, lifelong.lineCost, lifelong.lineCapPerTier,
lifelong.abilityMax, lifelong.abilityLevelStep, lifelong.abilityCost, lifelong.collPoints, lifelong.collGate, tool.power.max, salvage.on,
salvage.pct; changed defaults: lifelong.perkSpeed 5, lifelong.perkFortune 2, tool.fortune.cap 0 (= none).
SAVED DATA: the registry key <kind>.up.swing (new), t1=1 (marker); Skyy_SkyyGear/salvage/<pk>.properties (new); lifelong/history/ copies.
ROLLBACK 0.3.17 -> 0.3.16: items safe. 0.3.16 ignores <kind>.up.swing (those points show as spent there), clamps Breaking Power / Fortune lines
to 10 and Vein Mine / Tree Feller to 3 (the saved levels stay), charges the old 3 / 5 / 8 Vein Mine costs (free points can show 0 until a Reset)
and reads tool.fortune.cap=0 as "no Fortune" - Undo the three config rows in Server Setup's change log BEFORE rolling back.
"""
import os
import sys
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.16.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.17.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.16"' in s and "GENERATED by tools/gear_0_3_16_patch.py" in s, "not the generated 0.3.16 script"
assert "gear:fn:salvage" not in s and "PK_SWING" not in s
CHANGES = []


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)
    CHANGES.append((new, old, count))


def before(anchor, text):
    rep(anchor, text + anchor)


def after(anchor, text):
    rep(anchor, anchor + text)


def rep_in(start, end, pairs):
    """Inside the region start .. end (both unique, start first) replace each (old, new, count) - counted inside the region only."""
    assert s.count(start) == 1 and s.count(end) == 1, (s.count(start), s.count(end), start[:80], end[:80])
    i, j = s.index(start), s.index(end)
    assert i < j
    reg = s[i:j]
    new = reg
    for o, n_, c in pairs:
        assert new.count(o) == c, "region anchor count %d (want %d): %s" % (new.count(o), c, o[:140])
        new = new.replace(o, n_)
    rep(reg, new)


_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyGear") != "0.3.16":
    print("NOTE: tools/deploy_set.py SET pins SkyyGear %s, this patch derives from 0.3.16" % _set.get("SkyyGear"))

HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.3.17 (2026-10-16)"):].rstrip() + "\n"

# ================================================================================================================ docstring + version
rep('''"""SkyyGear 0.3.16 - build script (javassist via jpype). GENERATED by tools/gear_0_3_16_patch.py from the LIVE 0.3.15 (itself GENERATED by
tools/gear_0_3_15_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.16.py -> SkyyGear/SkyyGear-0.3.16.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.16.py
''', '''"""SkyyGear 0.3.17 - build script (javassist via jpype). GENERATED by tools/gear_0_3_17_patch.py from the LIVE 0.3.16 (itself GENERATED by
tools/gear_0_3_16_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.17.py -> SkyyGear/SkyyGear-0.3.17.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.17.py

''' + NOTE + '''
--- 0.3.16 notes ---
''')
rep('VERSION = "0.3.16"\n', 'VERSION = "0.3.17"\n')

# ================================================================================================================ 1-3, 7a, 8: Server Setup rows
rep('''    ("lifelong.perkSpeed", "Speed per perk level", "lifelong", "dec", "2", "0", "50", "", "%", "live,danger",
     "Each Speed level: this % more Mining / Chopping Power." + PH, "field:GearCfg.LL_PSPD"),
    ("lifelong.perkFortune", "Fortune per perk level", "lifelong", "dec", "1", "0", "25", "", "", "live,danger",
     "Each Fortune level adds this much Fortune (tool cap applies)." + PH, "field:GearCfg.LL_PFORT"),''',
    '''    ("lifelong.perkSpeed", "Breaking Power per level", "lifelong", "dec", "5", "0", "50", "", "%", "live,danger",
     "Each level: this % more Mining / Chopping Power (fewer hits)." + PH, "field:GearCfg.LL_PSPD"),
    ("lifelong.perkFortune", "Fortune per perk level", "lifelong", "dec", "2", "0", "25", "", "", "live,danger",
     "Each Fortune level adds this much (100 = a sure extra drop)." + PH, "field:GearCfg.LL_PFORT"),''')
rep('''    ("tool.fortune.cap", "Tool Fortune cap", "tools", "dec", repr(TOOL_FCAP_DEF), "0", "1000", "", "", "live,danger",
     "Most Fortune one tool gives (100 = one sure extra drop)." + PH, "field:GearCfg.TOOL_FCAP"),''',
    '''    ("tool.fortune.cap", "Tool Fortune cap", "tools", "dec", "0", "0", "100000", "", "", "live,danger",
     "Most Fortune one tool gives (100 = one sure extra drop); 0 = no cap." + PH, "field:GearCfg.TOOL_FCAP"),
    # 0.3.17 T1: the Power clamp (was a fixed x100) - a sanity guard only
    ("tool.power.max", "Most tool Power (x)", "tools", "dec", "1000", "1", "100000", "", "x", "live,danger",
     "A tool's Power factor never goes above this (a guard; Breaking Power has no cap of its own).", "field:GearCfg.POW_MAX"),''')
G317_ROWS = '''    # 0.3.17 T1 TOOL UPGRADES (tools/gear_0_3_17_patch.py)
    ("lifelong.perkSwing", "Breaking Speed per level", "lifelong", "dec", "3", "0", "50", "", "%", "live,danger",
     "Each level: the tool swings this % faster (SkyyTrees applies it)." + PH, "field:GearCfg.LL_PSWING"),
    ("lifelong.lineCost", "Points per line level", "lifelong", "int", "1", "1", "100", "", "", "live,danger",
     "Points a Breaking Power / Speed / Fortune level costs (flat)." + PH, "field:GearCfg.LL_LCOST"),
    ("lifelong.lineCapPerTier", "Line levels per tool tier", "lifelong", "int", "10", "0", "1000", "", "", "live,danger",
     "Each line caps at this x the tier (Crude 10, Copper 20 ...); top tier uncapped. 0 = no cap.", "field:GearCfg.LL_LCAPT"),
    ("lifelong.abilityMax", "Vein Mine / Tree Feller tool max", "lifelong", "int", "6", "0", "10", "", "", "live,danger",
     "Most Vein Mine / Tree Feller levels on the tool (the skill tree adds its own on top).", "field:GearCfg.LL_ABMAX"),
    ("lifelong.abilityLevelStep", "Tool levels per ability level", "lifelong", "int", "8", "1", "49", "", "", "live,danger",
     "Vein Mine / Tree Feller level n needs tool level n x this (8: Lv 8, 16, 24 ...).", "field:GearCfg.LL_ABSTEP"),
    ("lifelong.abilityCost", "Ability first level cost", "lifelong", "int", "1", "1", "1000", "", "", "live,danger",
     "Vein Mine / Tree Feller level 1 costs this; every level doubles it (1, 2, 4, 8, 16, 32).", "field:GearCfg.LL_ABCOST"),
    ("lifelong.collPoints", "Upgrade points from collections", "lifelong", "bool", "true", "", "", "", "", "live,danger",
     "On = SkyyCollections' tool points add to each skill's Upgrade Points.", "field:GearCfg.LL_COLLPTS"),
    ("lifelong.collGate", "Tool tier-ups need the collection", "lifelong", "bool", "true", "", "", "", "", "live,danger",
     "On = a lifelong tool tiers up only once its collection tier unlocked it (SkyyCollections).", "field:GearCfg.LL_COLLGATE"),
    ("salvage.on", "Gear salvage (Requip)", "smithing", "bool", "true", "", "", "", "", "live,danger",
     "Salvage gives back part of a piece's materials (never coins). Off = nothing salvages.", "field:GearCfg.SALV_ON"),
    ("salvage.pct", "Salvage % by rarity", "smithing", "text", "25,30,35,40,45,50", "1", "60", "", "", "live,danger",
     "Normal..Mythic: % of the recipe + tier-up materials a crafted piece gives back (6 numbers 0-100).", "field:GearCfg.SALV_PCT;check=GearSalv.check"),
    ("salvage.dropPct", "Salvage % of dropped gear", "smithing", "int", "10", "0", "100", "", "%", "live,danger",
     "A dropped (not crafted) piece gives back this % of its base recipe only (Skyy: drops give less).", "field:GearCfg.SALV_DROP"),
'''
after('''    ("lifelong.stickCost", "Enchanted Sticks per tier-up", "lifelong", "text", "0,0,0,2,4,8,16,32", "1", "60", "", "", "live,danger",
     "Crude to Onyxium: Enchanted Sticks a tool tier-up INTO that tier costs extra (8 numbers 0-999).", "field:GearCfg.LL_STICKS;check=GearUp.checkSticks"),
''', G317_ROWS)
G317_KEYS = ["lifelong.perkSwing", "lifelong.lineCost", "lifelong.lineCapPerTier", "lifelong.abilityMax", "lifelong.abilityLevelStep",
             "lifelong.abilityCost", "lifelong.collPoints", "lifelong.collGate", "salvage.on", "salvage.pct", "salvage.dropPct"]
rep('''           "sigil.miniWords", "sigil.bossWords", "sigil.bagLists"}''', '''           "sigil.miniWords", "sigil.bossWords", "sigil.bagLists",
           # 0.3.17: the tool upgrade lines / caps / costs / collection points + gate (gathering speed, Fortune = economy), salvage (items)
           "tool.power.max", ''' + ", ".join('"%s"' % _k for _k in G317_KEYS) + '''}''')
after('''assert all(32 <= ord(_c) < 127 for _c in H4_MARK) and "=" not in H4_MARK and H4_MARK.startswith("# ")
''', '''G317_HEAD = "# ---- tool upgrades: Breaking Power / Breaking Speed / Fortune, Vein Mine / Tree Feller, collection points, salvage (SkyyGear 0.3.17) ----"
G317_ROWK = ["tool.power.max"] + ''' + repr(G317_KEYS) + '''
assert all(32 <= ord(_c) < 127 for _c in G317_HEAD) and "=" not in G317_HEAD
# 0.3.17 ONE-TIME UPDATE migrate0317: the run-once marker (a comment line; a fresh file carries it right under G317_HEAD)
H7_MARK_ID = "SkyyGear 0.3.17 default update"
H7_WHO = "SkyyGear 0.3.17"
H7_KEYS = ["lifelong.perkSpeed", "lifelong.perkFortune", "tool.fortune.cap"]
H7_OLD = ["2", "1", "25"]
H7_NEW = ["5", "2", "0"]
H7_MARK = ("# %s (Skyy 2026-10-16): Breaking Power 5 %% a level, Fortune 2 a level, no tool Fortune cap (old defaults 2, 1, 25)" % H7_MARK_ID)
assert all(32 <= ord(_c) < 127 for _c in H7_MARK) and "=" not in H7_MARK and H7_MARK.startswith("# ")
''')
after('''    L += ["", G314_HEAD]        # 0.3.14: the new rows (no one-time update adds them; absent = the default) + the migrate0314 marker
    L += [H4_MARK]
    for k in G314_ROWK:
        scal(k)
''', '''    L += ["", G317_HEAD]        # 0.3.17: the new rows (absent = the default) + the migrate0317 marker
    L += [H7_MARK]
    for k in G317_ROWK:
        scal(k)
''')
rep('''("LL_PSPD", "double", "2.0"), ("LL_PFORT", "double", "1.0"),''', '''("LL_PSPD", "double", "5.0"), ("LL_PFORT", "double", "2.0"),''')
rep('''("TOOL_FCAP", "double", repr(TOOL_FCAP_DEF)),''', '''("TOOL_FCAP", "double", "0.0"),''')
rep('''              ("SIGD_BOSSW", "String", jstr("Boss,Guardian,Duke,Dragon,Chieftain,Hedera")), ("SIGD_BAGS", "String", jstr("Zone1_Encounters_,Zone2_Encounters_,Zone3_Encounters_,Zone4_Encounters_"))]''',
    '''              ("SIGD_BOSSW", "String", jstr("Boss,Guardian,Duke,Dragon,Chieftain,Hedera")), ("SIGD_BAGS", "String", jstr("Zone1_Encounters_,Zone2_Encounters_,Zone3_Encounters_,Zone4_Encounters_")),
              # 0.3.17 T1 tool upgrades + salvage
              ("POW_MAX", "double", "1000.0"), ("LL_PSWING", "double", "3.0"), ("LL_LCOST", "int", "1"), ("LL_LCAPT", "int", "10"),
              ("LL_ABMAX", "int", "6"), ("LL_ABSTEP", "int", "8"), ("LL_ABCOST", "int", "1"), ("LL_COLLPTS", "boolean", "true"),
              ("LL_COLLGATE", "boolean", "true"), ("SALV_ON", "boolean", "true"), ("SALV_PCT", "String", jstr("25,30,35,40,45,50")), ("SALV_DROP", "int", "10")]''')
rep('''  TOOL_FCAP = pdec(p, "tool.fortune.cap", TOOL_FCAP_DEFV, 0.0, 1000.0);''',
    '''  TOOL_FCAP = pdec(p, "tool.fortune.cap", 0.0, 0.0, 100000.0);          // 0.3.17: 0 = no cap (fcap())
  POW_MAX = pdec(p, "tool.power.max", 1000.0, 1.0, 100000.0);          // 0.3.17: the Power guard (was a fixed x100)''')
rep('''  LL_PSPD = pdec(p, "lifelong.perkSpeed", 2.0, 0.0, 50.0);
  LL_PFORT = pdec(p, "lifelong.perkFortune", 1.0, 0.0, 25.0);''', '''  LL_PSPD = pdec(p, "lifelong.perkSpeed", 5.0, 0.0, 50.0);          // 0.3.17: Breaking Power (was 2)
  LL_PFORT = pdec(p, "lifelong.perkFortune", 2.0, 0.0, 25.0);          // 0.3.17 (was 1)''')
after('''  SIGD_BAGS = ptext(p, "sigil.bagLists", "Zone1_Encounters_,Zone2_Encounters_,Zone3_Encounters_,Zone4_Encounters_").trim();
''', '''  // 0.3.17 T1 tool upgrades + salvage
  LL_PSWING = pdec(p, "lifelong.perkSwing", 3.0, 0.0, 50.0);
  LL_LCOST = (int) plong(p, "lifelong.lineCost", 1L, 1L, 100L);
  LL_LCAPT = (int) plong(p, "lifelong.lineCapPerTier", 10L, 0L, 1000L);
  LL_ABMAX = (int) plong(p, "lifelong.abilityMax", 6L, 0L, 10L);
  LL_ABSTEP = (int) plong(p, "lifelong.abilityLevelStep", 8L, 1L, 49L);
  LL_ABCOST = (int) plong(p, "lifelong.abilityCost", 1L, 1L, 1000L);
  LL_COLLPTS = pbool(p, "lifelong.collPoints", true);
  LL_COLLGATE = pbool(p, "lifelong.collGate", true);
  SALV_ON = pbool(p, "salvage.on", true);
  SALV_PCT = ptext(p, "salvage.pct", "25,30,35,40,45,50").trim();
  SALV_DROP = (int) plong(p, "salvage.dropPct", 10L, 0L, 100L);
''')
# GearCfg.fcap(): the tool Fortune cap in force (0 = none)
before('''# 0.2.1 ready line part: the base stats in force (live values)
M(gcf, r"""
public static String baseText() {''', r'''# 0.3.17: the tool Fortune cap in force - tool.fortune.cap 0 (the new default) = no cap (Skyy 2026-10-16 "no max %")
M(gcf, "public static double fcap() { double c = TOOL_FCAP; return c > 0.0 ? c : 1.0E9; }")
M(gcf, "public static double pmax() { double c = POW_MAX; return c >= 1.0 ? c : 1.0; }")
# ---- 0.3.17 ONE-TIME UPDATE migrate0317 (PROJECT-RULES section 4; tools/gear_0_3_17_patch.py item 7a; the migrate0314 machinery with number values).
# Pure text step: null = the marker is already in a comment line (a fresh 0.3.17 file carries it). Else { new text, "a 2 -> 5, ..." ("" = none),
# String[] notes, String[] log rows (key, old, new) }. Per key of H7_KEYS: every ONE-LINE entry holding exactly the old default (as a number) is
# rewritten when the LAST entry (the one Properties keeps) holds it (value text only: key, separator, CR kept). The marker goes to the END.
M(gcf, r"""
public static boolean h7Old(String v, String old) {
  if (v == null || old == null) return false;
  try { return Double.parseDouble(v.trim()) == Double.parseDouble(old); } catch (Throwable t) { return false; }
}""")
M(gcf, r"""
public static Object[] h7Update(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  for (int i = 0; i < l.size(); i++) {
    String t0 = ((String) l.get(i)).trim();
    if ((t0.startsWith("#") || t0.startsWith("!")) && t0.indexOf(H7_MARK_ID) >= 0) return null;
  }
  java.util.Properties pp = new java.util.Properties();
  try { pp.load(new java.io.StringReader(text)); } catch (Throwable x) { }
  int nk = H7_KEYS.length;
  int[] last = new int[nk];
  boolean[] lastOne = new boolean[nk];
  for (int i = 0; i < nk; i++) last[i] = -1;
  java.util.HashSet cand = new java.util.HashSet();
  int tail = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) { k++; continue; }
    int e = @PKG@.CfgFile.end(l, k);
    if (e == l.size() - 1) tail = k;
    String key = @PKG@.CfgFile.key(s);
    for (int i = 0; key != null && i < nk; i++) {
      if (!key.equals(H7_KEYS[i])) continue;
      last[i] = k;
      lastOne[i] = e == k;
      if (e == k && h7Old(@PKG@.CfgFile.value(l, k), H7_OLD[i])) cand.add(i + ":" + k);
    }
    k = e + 1;
  }
  StringBuilder chg = new StringBuilder();
  java.util.ArrayList notes = new java.util.ArrayList();
  java.util.ArrayList rows = new java.util.ArrayList();
  java.util.HashMap at = new java.util.HashMap();
  for (int i = 0; i < nk; i++) {
    String ov = pp.getProperty(H7_KEYS[i]);
    boolean rw = ov != null && h7Old(ov, H7_OLD[i]) && lastOne[i] && last[i] >= 0 && cand.contains(i + ":" + last[i]);
    if (rw) {
      java.util.Iterator it = cand.iterator();
      while (it.hasNext()) {
        String c = (String) it.next();
        if (c.startsWith(i + ":")) at.put(Integer.valueOf(Integer.parseInt(c.substring(c.indexOf(':') + 1))), H7_NEW[i]);
      }
      if (chg.length() > 0) chg.append(", ");
      chg.append(H7_KEYS[i]).append(' ').append(ov.trim()).append(" -> ").append(H7_NEW[i]);
      rows.add(H7_KEYS[i]);
      rows.add(ov.trim());
      rows.add(H7_NEW[i]);
    } else if (ov != null) {
      notes.add(H7_KEYS[i] + "=" + @PKG@.CfgRows.oneLine(ov.trim()) + " kept (not the 0.3.16 default " + H7_OLD[i] + ", or not one plain line) - the new default would be " + H7_NEW[i]);
    }
  }
  java.util.ArrayList blk = new java.util.ArrayList();
  blk.add(H7_MARK);
  String crDef = text.indexOf("\r\n") >= 0 ? "\r" : "";
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    Object nv = at.get(Integer.valueOf(i));
    if (nv != null) {
      String s2 = (String) l.get(i);
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + (String) nv + (raw[i].endsWith("\r") ? "\r" : ""));
    } else out.add(raw[i]);
  }
  chPut(out, chEnd(l, tail, raw), blk, crDef);
  StringBuilder sb = new StringBuilder(text.length() + 256);
  for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append('\n'); sb.append((String) out.get(i)); }
  return new Object[] { sb.toString(), chg.toString(), (String[]) notes.toArray(new String[0]), (String[]) rows.toArray(new String[0]) };
}""")
M(gcf, r"""
public static String h7Log(String k, String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + H7_WHO + "\t-\tupdate\t" + @PKG@.CfgRows.oneLine(k) + "\t" + o + "\t" + n + "\tok";
}""")
M(gcf, r"""
public static synchronized String migrate0317() {
  java.nio.file.Path f = FILE;
  if (f == null || Boolean.getBoolean("skyy.harness.no317")) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = h7Update(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    lvKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), H7_WHO, "before the 0.3.17 default update");
    if (!lvSaved(old)) {
      @PKG@.Gear.warn("config.properties NOT updated to the 0.3.17 defaults: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[3];
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(h7Log(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String chg = (String) r[1];
    String[] notes = (String[]) r[2];
    String msg = chg.length() > 0
      ? "config.properties updated to the 0.3.17 defaults: " + chg + " (Breaking Power 5 % a level, Fortune 2 a level, no tool Fortune cap; Undo in Server Setup's change log; the old file is kept in config-history)"
      : "config.properties: the 0.3.17 default update marker was added - no value changed";
    @PKG@.Gear.info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < notes.length; i++) { @PKG@.Gear.info(notes[i]); all.append('\n').append(notes[i]); }
    @PKG@.GearLog.line("CONFIG 0.3.17 defaults: " + (chg.length() > 0 ? chg : "no value changed") + (notes.length > 0 ? "; " + notes.length + " notes" : ""));
    return all.toString();
  } catch (Throwable t) {
    @PKG@.Gear.warn("could not update config.properties to the 0.3.17 defaults (the file is used as it is): " + t);
    return "";
  }
}""")
''')
rep('''F(gcf, "public static final String H4_MARK = %s;" % jstr(H4_MARK))          # 0.3.14 migrate0314
''', '''F(gcf, "public static final String H4_MARK = %s;" % jstr(H4_MARK))          # 0.3.14 migrate0314
F(gcf, "public static final String H7_MARK = %s;" % jstr(H7_MARK))          # 0.3.17 migrate0317
F(gcf, "public static final String H7_MARK_ID = %s;" % jstr(H7_MARK_ID))
F(gcf, "public static final String H7_WHO = %s;" % jstr(H7_WHO))
F(gcf, "public static final String[] H7_KEYS = %s;" % jarr(H7_KEYS))
F(gcf, "public static final String[] H7_OLD = %s;" % jarr(H7_OLD))
F(gcf, "public static final String[] H7_NEW = %s;" % jarr(H7_NEW))
''')
rep('''  @PKG@.GearCfg.migrate0314();          // 0.3.14: hoe.areaElsewhere + sigil.mythicUse false -> true (only the old default)
  @PKG@.GearCfg.load();''', '''  @PKG@.GearCfg.migrate0314();          // 0.3.14: hoe.areaElsewhere + sigil.mythicUse false -> true (only the old default)
  @PKG@.GearCfg.migrate0317();          // 0.3.17: perkSpeed 2 -> 5, perkFortune 1 -> 2, tool.fortune.cap 25 -> 0 (only the old defaults)
  @PKG@.GearCfg.load();''')

# ================================================================================================================ 1 + 3: the perk table
rep('''LL_PERKS = [("spd", "Speed", 10, 1 | 2, [1] * 10, [0] * 10),
            ("fort", "Fortune", 10, 15 | 16, [1] * 10, [0] * 10),          # 0.3.6: + the pole (Fishing Fortune = double catch %)
            ("wis", "Wisdom", 5, 15 | 16, [2] * 5, [2] * 5),               # 0.3.6: + the pole (Fishing XP %)
            ("vein", "Vein Mine", 3, 1, [3, 5, 8], [2, 3, 4]),
            ("fell", "Tree Feller", 3, 2, [3, 5, 8], [2, 3, 4]),''',
    '''# 0.3.17 T1: spd = Breaking Power, fort = Fortune, swing = Breaking Speed are LINES (GearLL.isLine: a flat lifelong.lineCost a level, no hard max,
# capped by lifelong.lineCapPerTier x tier - the table's max / costs below are not read for them); vein / fell are ABILITIES (GearLL.isAbil: max
# lifelong.abilityMax, level n costs lifelong.abilityCost x 2^(n-1), needs tool level n x lifelong.abilityLevelStep - no tier need)
LL_PERKS = [("spd", "Breaking Power", 10, 1 | 2, [1] * 10, [0] * 10),
            ("fort", "Fortune", 10, 15 | 16, [1] * 10, [0] * 10),          # 0.3.6: + the pole (Fishing Fortune = double catch %)
            ("wis", "Wisdom", 5, 15 | 16, [2] * 5, [2] * 5),               # 0.3.6: + the pole (Fishing XP %)
            ("vein", "Vein Mine", 10, 1, [1, 2, 4, 8, 16, 32, 64, 128, 256, 512], [0] * 10),
            ("fell", "Tree Feller", 10, 2, [1, 2, 4, 8, 16, 32, 64, 128, 256, 512], [0] * 10),''')
rep('''             ("bloom", "Bloom", 5, 1 << 5, [1, 2, 2, 3, 3], [0] * 5)]
''', '''             ("bloom", "Bloom", 5, 1 << 5, [1, 2, 2, 3, 3], [0] * 5)]
LL_PERKS += [("swing", "Breaking Speed", 10, 1 | 2, [1] * 10, [0] * 10)]          # 0.3.17 T1: APPENDED (the saved order is locked)
assert [_p[0] for _p in LL_PERKS].index("swing") == 10
''')
rep('''for _pn in ("cap", "grow", "last", "bloom"):          # 0.3.12 the watering can's points''',
    '''for _pn in ("swing", "vein", "fell"):          # 0.3.17 T1
    F(gll, "public static final int PK_%s = %d;" % (_pn.upper(), [_p[0] for _p in LL_PERKS].index(_pn)))
F(gll, "public static final int LINE_BIG = 1000000;")          # 0.3.17: "no cap" for a line (a level count no one reaches)
F(gll, "public static final java.util.concurrent.ConcurrentHashMap CPTS = new java.util.concurrent.ConcurrentHashMap();")   # 0.3.17 "pk|skill" -> Object[] { Long pts, Long at }
F(gll, "public static final long[] TN17 = new long[6];")          # 0.3.17: 0 collection point asks, 1 cache hits, 2 tier-ups gated, 3 gate asks, 4 bridge errors, 5 t1 lowerings
for _pn in ("cap", "grow", "last", "bloom"):          # 0.3.12 the watering can's points''')

# the 0.3.17 helpers sit right before perkOf (methods before callers)
rep('''M(gll, r"""
public static int perkOf(java.util.Properties P, int k, int p) {
  if (!perkFor(k, p)) return 0;
  long v = getl(P, KIND[k] + ".up." + PK[p], 0L);
  if (v < 0L) return 0;
  return v > (long) PKMAX[p] ? PKMAX[p] : (int) v;
}""")
M(gll, "public static int pkCost(int p, int lvl) { return p < 0 || p >= PK.length || lvl < 1 || lvl > PKMAX[p] ? 0 : PKCOST[p * 10 + lvl - 1]; }")
M(gll, "public static int pkNeed(int p, int lvl) { return p < 0 || p >= PK.length || lvl < 1 || lvl > PKMAX[p] ? 99 : PKNEED[p * 10 + lvl - 1]; }")
M(gll, r"""
public static int spent(java.util.Properties P, int k) {
  int n = 0;
  for (int p = 0; p < PK.length; p++) {
    int lv = perkOf(P, k, p);
    for (int l = 1; l <= lv; l++) n = n + pkCost(p, l);
  }
  return n;
}""")
# 1 point per skill level (Skyy 2026-10-13): earned = skill level - 1 (a new player at level 1 has none); no SkyySkills = 0
M(gll, r"""
public static int earned(java.util.UUID u, int k) {
  int h = skill(u, k);
  return h > 1 ? h - 1 : 0;
}""")''', r'''# ---- 0.3.17 T1 (tools/gear_0_3_17_patch.py items 1-4): lines (Breaking Power / Breaking Speed / Fortune) and abilities (Vein Mine / Tree Feller)
M(gll, "public static boolean isLine(int p) { return p == 0 || p == 1 || p == PK_SWING; }")
M(gll, "public static boolean isAbil(int p) { return p == PK_VEIN || p == PK_FELL; }")
# the highest level a perk may be saved at (lines: none in practice; abilities: lifelong.abilityMax; the rest: the table)
M(gll, r"""
public static int pkMax(int p) {
  if (p < 0 || p >= PK.length) return 0;
  if (isLine(p)) return LINE_BIG;
  if (isAbil(p)) { int m = @PKG@.GearCfg.LL_ABMAX; return m < 0 ? 0 : (m > 10 ? 10 : m); }
  return PKMAX[p];
}""")
# the top tier of kind k's ladder for the tool id it has now (a tool AT it = no tier cap; Skyy: "the top tier uncapped")
M(gll, r"""
public static int topTier(int k, String id) {
  String l = id == null ? null : ladOf(k, id);
  if (l == null || l.length() == 0) l = k >= 0 && k < KLAD.length ? KLAD[k] : "";
  int m = 0;
  String[] a = l.split(",");
  for (int i = 0; i < a.length; i++) { int t = tier(a[i].trim()); if (t > m) m = t; }
  return m;
}""")
# a line's cap for kind k (Skyy 2026-10-16 "Yes, 10 levels per tier"): lifelong.lineCapPerTier x (tier + 1) - Crude 10, Copper 20, Iron 30 ...;
# the ladder's top tier and lifelong.lineCapPerTier 0 = LINE_BIG (no cap)
M(gll, r"""
public static int lineCap(java.util.Properties P, int k) {
  int per = @PKG@.GearCfg.LL_LCAPT;
  if (per <= 0 || k < 0 || k >= KIND.length) return LINE_BIG;
  String id = P == null ? null : P.getProperty(KIND[k] + ".id");
  int t = id == null ? 0 : tier(id);
  if (t < 0) t = 0;
  if (id != null && t >= topTier(k, id)) return LINE_BIG;
  long c = (long) per * (long) (t + 1);
  return c > (long) LINE_BIG ? LINE_BIG : (int) c;
}""")
# an ability's cap for kind k (Skyy 2026-10-16 "capped by the tools level (so your skill level.) and not the tier"): tool level / step, at most
# lifelong.abilityMax; no SkyySkills (level unknown) = the max
M(gll, r"""
public static int abilCap(java.util.UUID u, java.util.Properties P, int k) {
  int mx = pkMax(PK_VEIN);
  if (k < 0 || k >= KIND.length || P == null) return mx;
  String id = P.getProperty(KIND[k] + ".id");
  if (id == null) id = KCRUDE[k];
  int lv = u == null ? -1 : levelFor(u, id);
  if (lv < 0) return mx;
  int st = @PKG@.GearCfg.LL_ABSTEP < 1 ? 1 : @PKG@.GearCfg.LL_ABSTEP;
  int c = lv / st;
  return c < mx ? c : mx;
}""")
''' + '''M(gll, r"""
public static int perkOf(java.util.Properties P, int k, int p) {
  if (!perkFor(k, p)) return 0;
  long v = getl(P, KIND[k] + ".up." + PK[p], 0L);
  if (v < 0L) return 0;
  int mx = pkMax(p);
  return v > (long) mx ? mx : (int) v;
}""")
# 0.3.17: the level a perk WORKS at now = the saved level inside its cap (a line: 10 x tier; an ability: the tool level); the rest = saved
M(gll, r"""
public static int perkEff(java.util.UUID u, java.util.Properties P, int k, int p) {
  int lv = perkOf(P, k, p);
  if (lv <= 0) return 0;
  int c = isLine(p) ? lineCap(P, k) : (isAbil(p) ? abilCap(u, P, k) : lv);
  return lv < c ? lv : c;
}""")
# 0.3.17: lines a flat lifelong.lineCost; abilities lifelong.abilityCost x 2^(lvl-1) (Skyy "like double price every time"); the rest the table
M(gll, r"""
public static int pkCost(int p, int lvl) {
  if (p < 0 || p >= PK.length || lvl < 1 || lvl > pkMax(p)) return 0;
  if (isLine(p)) return @PKG@.GearCfg.LL_LCOST < 1 ? 1 : @PKG@.GearCfg.LL_LCOST;
  if (isAbil(p)) {
    long c = (long) (@PKG@.GearCfg.LL_ABCOST < 1 ? 1 : @PKG@.GearCfg.LL_ABCOST);
    for (int i = 1; i < lvl && c < 1000000000L; i++) c = c * 2L;
    return c > 1000000000L ? 1000000000 : (int) c;
  }
  return PKCOST[p * 10 + lvl - 1];
}""")
# the TIER a level needs (lines and abilities: none - abilities need a tool LEVEL instead, pkNeedLv)
M(gll, "public static int pkNeed(int p, int lvl) { return p < 0 || p >= PK.length || lvl < 1 || lvl > pkMax(p) ? 99 : (isLine(p) || isAbil(p) ? 0 : PKNEED[p * 10 + lvl - 1]); }")
M(gll, "public static int pkNeedLv(int p, int lvl) { return isAbil(p) && lvl >= 1 ? lvl * (@PKG@.GearCfg.LL_ABSTEP < 1 ? 1 : @PKG@.GearCfg.LL_ABSTEP) : 0; }")
M(gll, r"""
public static int spent(java.util.Properties P, int k) {
  long n = 0L;
  for (int p = 0; p < PK.length; p++) {
    int lv = perkOf(P, k, p);
    if (lv <= 0) continue;
    if (isLine(p)) { n = n + (long) lv * (long) pkCost(p, 1); continue; }
    for (int l = 1; l <= lv; l++) n = n + (long) pkCost(p, l);
  }
  return n > 1000000000L ? 1000000000 : (int) n;
}""")
# 0.3.17 item 4: SkyyCollections' tool points for kind k's skill (coll:fn:toolPts {profile key, skill} -> Long; DERIVED there, never saved) -
# cached 2 s per profile + skill; off / no SkyyCollections / an error = 0
M(gll, r"""
public static int collPts(java.util.UUID u, int k) {
  if (!@PKG@.GearCfg.LL_COLLPTS || u == null || k < 0 || k >= KSKILL.length) return 0;
  String pk = @PKG@.Gear.pkey(u);
  String ck = pk + "|" + KSKILL[k];
  long now = System.currentTimeMillis();
  Object c = CPTS.get(ck);
  if (c instanceof Object[]) {
    Object[] e = (Object[]) c;
    long at = ((Long) e[1]).longValue();
    if (now >= at && now - at < 2000L) { TN17[1] = TN17[1] + 1L; return ((Long) e[0]).intValue(); }
  }
  long v = 0L;
  java.util.function.Function f = @PKG@.Gear.fn("coll:fn:toolPts");
  if (f != null) {
    try {
      TN17[0] = TN17[0] + 1L;
      Object r = f.apply(new Object[] { pk, KSKILL[k] });
      if (r instanceof Number) v = ((Number) r).longValue();
    } catch (Throwable t) { v = 0L; TN17[4] = TN17[4] + 1L; @PKG@.Gear.warnOnce("colltp", "coll:fn:toolPts (SkyyCollections) failed - no collection Upgrade Points for now (logged once): " + t); }
  }
  if (v < 0L) v = 0L;
  if (v > 1000000L) v = 1000000L;
  CPTS.put(ck, new Object[] { Long.valueOf(v), Long.valueOf(now) });
  return (int) v;
}""")
# 1 point per skill level (Skyy 2026-10-13): skill level - 1 (a new player at level 1 has none); no SkyySkills = 0; 0.3.17: + the collection points
M(gll, r"""
public static int earned(java.util.UUID u, int k) {
  int h = skill(u, k);
  return (h > 1 ? h - 1 : 0) + collPts(u, k);
}""")''')
rep('''  java.util.Properties P = reg(@PKG@.Gear.pkey(u));
  double pw = 1.0 + (double) perkOf(P, k, 0) * @PKG@.GearCfg.LL_PSPD / 100.0;
  double fo = (double) perkOf(P, k, 1) * @PKG@.GearCfg.LL_PFORT;''', '''  java.util.Properties P = reg(@PKG@.Gear.pkey(u));
  double pw = 1.0 + (double) perkEff(u, P, k, 0) * @PKG@.GearCfg.LL_PSPD / 100.0;          // 0.3.17: Breaking Power inside its tier cap
  double fo = (double) perkEff(u, P, k, 1) * @PKG@.GearCfg.LL_PFORT;''')

# ================================================================================================================ 6: the collection tier-up gate
rep('''  int need = @PKG@.GearLevel.band(to)[0];
  if (@PKG@.GearLevel.floor(h) >= need) return null;
  return "You need " + KSKILL[k] + " " + need + " to tier up to " + an(@PKG@.Gear.itemName(to)) + " (you: " + h + ").";
}""")''', '''  int need = @PKG@.GearLevel.band(to)[0];
  if (@PKG@.GearLevel.floor(h) >= need) return collWhy(u, to);          // 0.3.17: + the collection gate
  return "You need " + KSKILL[k] + " " + need + " to tier up to " + an(@PKG@.Gear.itemName(to)) + " (you: " + h + ").";
}""")''')
before('''# a tier-up needs the skill level the new tier starts at (its level.material start)
M(gll, r"""
public static String tierWhy(java.util.UUID u, String to) {''', r'''# 0.3.17 item 6: the SkyyCollections token kind of a tier-up target ("pickaxe", "hatchet", "harvester", "can"; null = not gated: the pole, others)
M(gll, r"""
public static String collKind(String to) {
  int k = kOf(to);
  if (k == 0) return "pickaxe";
  if (k == 1) return "hatchet";
  if (k == 2 || k == 3) return "harvester";
  if (k == CAN) return "can";
  return null;
}""")
M(gll, r"""
public static String roman(int n) {
  String[] r = new String[] { "", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV" };
  return n >= 0 && n < r.length ? r[n] : String.valueOf(n);
}""")
# null = the collection allows it (or does not gate it / no SkyyCollections / an error / lifelong.collGate off), else the reason
M(gll, r"""
public static String collWhy(java.util.UUID u, String to) {
  if (!@PKG@.GearCfg.LL_COLLGATE || u == null || to == null) return null;
  String ck = collKind(to);
  if (ck == null) return null;
  java.util.function.Function f = @PKG@.Gear.fn("coll:fn:tierup");
  if (f == null) return null;
  Object r = null;
  try {
    TN17[3] = TN17[3] + 1L;
    r = f.apply(new Object[] { @PKG@.Gear.pkey(u), ck + ":" + tname(tier(to)) });
  } catch (Throwable t) { TN17[4] = TN17[4] + 1L; @PKG@.Gear.warnOnce("colltu", "coll:fn:tierup (SkyyCollections) failed - tier-ups are not gated for now (logged once): " + t); return null; }
  if (!(r instanceof String)) return null;
  String[] a = ((String) r).split("\\|", -1);
  if (a.length < 6 || !"0".equals(a[0])) return null;
  TN17[2] = TN17[2] + 1L;
  int t = 0;
  try { t = Integer.parseInt(a[3].trim()); } catch (Throwable x) { t = 0; }
  return "Needs the " + a[2] + " collection " + roman(t) + " (" + a[5] + " / " + a[4] + ") to tier up to " + an(@PKG@.Gear.itemName(to)) + " - /collections.";
}""")
''')

# ================================================================================================================ the tooltip's upgrade line: what works now
rep('''    for (int p = 0; p < PK.length; p++) {
      int lv = perkOf(P, k, p);
      if (lv <= 0) continue;
      if (sb.length() > 0) sb.append(", ");
      sb.append(PKN[p]).append(' ').append(lv);
    }''', '''    for (int p = 0; p < PK.length; p++) {
      int lv = perkEff(ow, P, k, p);          // 0.3.17: the level it works at (inside its cap)
      if (lv <= 0) continue;
      if (sb.length() > 0) sb.append(", ");
      sb.append(PKN[p]).append(' ').append(lv);
    }''')

# ================================================================================================================ 5 + 2: GearTool (two sets, no Fortune cap, the Power guard)
rep_in('''public static double fortune(int f, int lv, int t) {''', '''public static int[] gate(java.util.UUID u, int f, String id, @BD@ d) {''', [
    ('''  if (v > @PKG@.GearCfg.TOOL_FCAP) v = @PKG@.GearCfg.TOOL_FCAP;''', '''  if (v > @PKG@.GearCfg.fcap()) v = @PKG@.GearCfg.fcap();''', 1)])
rep_in('''public static double[] eff(int f, int lv, int t, @BD@ d) {''', '''M(gtool, "public static double r1(double x) {''', [
    ('''  if (pw > 100.0) pw = 100.0;''', '''  if (pw > @PKG@.GearCfg.pmax()) pw = @PKG@.GearCfg.pmax();''', 1),
    ('''  if (fo > @PKG@.GearCfg.TOOL_FCAP) fo = @PKG@.GearCfg.TOOL_FCAP;''', '''  if (fo > @PKG@.GearCfg.fcap()) fo = @PKG@.GearCfg.fcap();''', 1)])
rep_in('''public static double[] mstats(java.util.UUID u, String id, @BD@ d) {''', '''public static double[] stats(java.util.UUID u, @IS@ s) {''', [
    ('''    wc = b[2];
    double xm =''', '''    wc = b[2];
    if (@PKG@.GearLL.mine(u, d)) {          // 0.3.17 item 5: a LIFELONG multitool = two sets: the pickaxe kind's lines on stone / ore, the hatchet kind's on logs
      double[] qa = @PKG@.GearLL.perkFx(u, 1, d);
      double[] qb = @PKG@.GearLL.perkFx(u, 3, d);
      pm = pm * qa[0]; if (pm > @PKG@.GearCfg.pmax()) pm = @PKG@.GearCfg.pmax();
      pc = pc * qb[0]; if (pc > @PKG@.GearCfg.pmax()) pc = @PKG@.GearCfg.pmax();
      fm = r1(fm + qa[1]); fc = r1(fc + qb[1]);
      wm = wm + qa[2]; wc = wc + qb[2];
    }
    double xm =''', 1),
    ('''      pm = pm * xm; if (pm > 100.0) pm = 100.0;
      pc = pc * xm; if (pc > 100.0) pc = 100.0;
      fm = fm * xm; if (fm > @PKG@.GearCfg.TOOL_FCAP) fm = @PKG@.GearCfg.TOOL_FCAP; fm = r1(fm);
      fc = fc * xm; if (fc > @PKG@.GearCfg.TOOL_FCAP) fc = @PKG@.GearCfg.TOOL_FCAP; fc = r1(fc);''',
     '''      pm = pm * xm; if (pm > @PKG@.GearCfg.pmax()) pm = @PKG@.GearCfg.pmax();
      pc = pc * xm; if (pc > @PKG@.GearCfg.pmax()) pc = @PKG@.GearCfg.pmax();
      fm = fm * xm; if (fm > @PKG@.GearCfg.fcap()) fm = @PKG@.GearCfg.fcap(); fm = r1(fm);
      fc = fc * xm; if (fc > @PKG@.GearCfg.fcap()) fc = @PKG@.GearCfg.fcap(); fc = r1(fc);''', 1)])
rep('''    if (px[0] > 1.0 && f <= 3) { pw = pw * px[0]; if (pw > 100.0) pw = 100.0; }
    if (px[1] > 0.0) { fo = fo + px[1]; if (fo > @PKG@.GearCfg.TOOL_FCAP) fo = @PKG@.GearCfg.TOOL_FCAP; fo = (double) Math.round(fo * 10.0) / 10.0; }''',
    '''    if (px[0] > 1.0 && f <= 3) { pw = pw * px[0]; if (pw > @PKG@.GearCfg.pmax()) pw = @PKG@.GearCfg.pmax(); }          // 0.3.17: the guard row, no x100
    if (px[1] > 0.0) { fo = fo + px[1]; if (fo > @PKG@.GearCfg.fcap()) fo = @PKG@.GearCfg.fcap(); fo = (double) Math.round(fo * 10.0) / 10.0; }''')
rep('''      if (f <= 3) { pw = pw * px[3]; if (pw > 100.0) pw = 100.0; }
      fo = fo * px[3]; if (fo > @PKG@.GearCfg.TOOL_FCAP) fo = @PKG@.GearCfg.TOOL_FCAP; fo = (double) Math.round(fo * 10.0) / 10.0;''',
    '''      if (f <= 3) { pw = pw * px[3]; if (pw > @PKG@.GearCfg.pmax()) pw = @PKG@.GearCfg.pmax(); }
      fo = fo * px[3]; if (fo > @PKG@.GearCfg.fcap()) fo = @PKG@.GearCfg.fcap(); fo = (double) Math.round(fo * 10.0) / 10.0;''')
rep_in('''public static float mdamage(java.util.UUID u, double[] st, @TBTY@ bt, float dmg) {''', '''public static float onDamage(java.util.UUID u, @IS@ s, @TBTY@ bt, float dmg) {''', [
    ('''  if (m > 100.0) m = 100.0;''', '''  if (m > @PKG@.GearCfg.pmax()) m = @PKG@.GearCfg.pmax();''', 1)])
rep('''"tool stats on (Mining / Chopping Power by tool level, Fortune up to " + @PKG@.Gear.fnum(@PKG@.GearCfg.TOOL_FCAP) + " through skill:bonus source gear;''',
    '''"tool stats on (Mining / Chopping Power by tool level, Fortune " + (@PKG@.GearCfg.TOOL_FCAP > 0.0 ? "up to " + @PKG@.Gear.fnum(@PKG@.GearCfg.TOOL_FCAP) : "with no cap") + " through skill:bonus source gear;''')
# 1: Breaking Speed published for SkyyTrees (gear:swing:<uuid>, Double %) when the held stack's stats are recomputed; gone on leave
rep('''  double[] st = stats(u, s);
  LAST.put(u, new Object[] { s, Long.valueOf(now), st });''', '''  double[] st = stats(u, s);
  LAST.put(u, new Object[] { s, Long.valueOf(now), st });
  @PKG@.GearLL.swingPost(u, s);          // 0.3.17: Breaking Speed % for SkyyTrees (gear:swing:<uuid>)''')
rep('''public static void forget(java.util.UUID u) {
  if (u == null) return;
  GONE.put(u, Long.valueOf(System.currentTimeMillis()));
  LAST.remove(u);
  post(u, -1, 0.0, null);
}''', '''public static void forget(java.util.UUID u) {
  if (u == null) return;
  GONE.put(u, Long.valueOf(System.currentTimeMillis()));
  LAST.remove(u);
  post(u, -1, 0.0, null);
  try { @PKG@.Gear.bridge().remove("gear:swing:" + u.toString()); } catch (Throwable t) { }          // 0.3.17
}''')
before('''# the write side hooks (bodies set by GearLife below: GearRefreshTask / GearStampTask are compiled before GearLife exists)
M(gll, "public static void joinHook(@PR@ pr, @INV@ inv) { }")''', r'''# 0.3.17 item 1: the held stack's Breaking Speed % (its OWN lifelong pickaxe / hatchet; a lifelong multitool = the higher of its two sets)
# -> the bridge Double gear:swing:<uuid> (removed when 0); SkyyTrees reads it in round T2. Never throws.
M(gll, r"""
public static double swingOf(java.util.UUID u, @IS@ s) {
  if (!@PKG@.GearCfg.LL_ON || u == null || s == null || s.isEmpty()) return 0.0;
  @BD@ d = null;
  try { d = @PKG@.GearData.gearDoc(s.getMetadata()); } catch (Throwable t) { d = null; }
  if (!mine(u, d)) return 0.0;
  int f = @PKG@.GearData.toolFam(s.getItemId());
  java.util.Properties P = reg(@PKG@.Gear.pkey(u));
  if (bad(P)) return 0.0;
  int a = f == 1 || f == 6 ? perkEff(u, P, 0, PK_SWING) : 0;
  int b = f == 3 || f == 6 ? perkEff(u, P, 1, PK_SWING) : 0;
  int lv = a > b ? a : b;
  return lv <= 0 ? 0.0 : (double) lv * @PKG@.GearCfg.LL_PSWING;
}""")
M(gll, r"""
public static void swingPost(java.util.UUID u, @IS@ s) {
  if (u == null) return;
  try {
    double v = swingOf(u, s);
    java.util.Map b = @PKG@.Gear.bridge();
    String key = "gear:swing:" + u.toString();
    if (v > 0.0) {
      Object o = b.get(key);
      if (!(o instanceof Double) || ((Double) o).doubleValue() != v) b.put(key, Double.valueOf(v));
    } else b.remove(key);
  } catch (Throwable t) { }
}""")
''')

# ================================================================================================================ the pole + gear:fn:perk: the level that works now
rep('''        dc = dc + (double) @PKG@.GearLL.perkOf(P, k, 1) * @PKG@.GearCfg.LL_PFORT * rb;''',
    '''        dc = dc + (double) @PKG@.GearLL.perkEff(u, P, k, 1) * @PKG@.GearCfg.LL_PFORT * rb;          // 0.3.17: inside its tier cap''')
rep('''      for (int p = 0; p < @PKG@.GearLL.PK.length; p++) if (@PKG@.GearLL.PK[p].equals(a[2])) return Integer.valueOf(@PKG@.GearLL.perkOf(P, k, p));''',
    '''      for (int p = 0; p < @PKG@.GearLL.PK.length; p++) if (@PKG@.GearLL.PK[p].equals(a[2])) return Integer.valueOf(@PKG@.GearLL.perkEff(u, P, k, p));          // 0.3.17: the level the tool may use now''')

# ================================================================================================================ buying a level (the caps)
rep('''  int lv = @PKG@.GearLL.perkOf(P, k, p);
  if (lv >= @PKG@.GearLL.PKMAX[p]) return "-" + nm + " is already at its top level (" + @PKG@.GearLL.PKMAX[p] + ").";
  int need = @PKG@.GearLL.pkNeed(p, lv + 1);
  String id = P.getProperty(K + ".id");
  int t = id == null ? 0 : @PKG@.GearLL.tier(id);
  if (t < need) return "-" + nm + " " + (lv + 1) + " needs " + @PKG@.GearLL.an(@PKG@.GearLL.tname(need)) + " " + K + " or better - tier yours up on the Anvil.";''',
    '''  int lv = @PKG@.GearLL.perkOf(P, k, p);
  if (lv >= @PKG@.GearLL.pkMax(p)) return "-" + nm + " is already at its top level (" + @PKG@.GearLL.pkMax(p) + ").";
  int need = @PKG@.GearLL.pkNeed(p, lv + 1);
  String id = P.getProperty(K + ".id");
  int t = id == null ? 0 : @PKG@.GearLL.tier(id);
  if (t < need) return "-" + nm + " " + (lv + 1) + " needs " + @PKG@.GearLL.an(@PKG@.GearLL.tname(need)) + " " + K + " or better - tier yours up on the Anvil.";
  String cw = capWhy(u, P, k, p, lv);          // 0.3.17: the line cap (10 x tier) / the ability's tool level
  if (cw != null) return "-" + cw;''')
before('''# a perk level (the Tools page): "+" bought, "-" why not
M(glf, r"""
public static String buy(java.util.UUID u, int k, int p) {''', r'''# 0.3.17: why the NEXT level of perk p (now at lv) cannot be bought yet because of its cap (null = it can): a line at 10 x tier (points stay
# banked), an ability above what the tool level allows
M(glf, r"""
public static String capWhy(java.util.UUID u, java.util.Properties P, int k, int p, int lv) {
  String nm = @PKG@.GearLL.PKN[p];
  String id = P.getProperty(@PKG@.GearLL.KIND[k] + ".id");
  if (id == null) id = @PKG@.GearLL.KCRUDE[k];
  if (@PKG@.GearLL.isLine(p)) {
    int c = @PKG@.GearLL.lineCap(P, k);
    if (lv < c) return null;
    return nm + " is at " + c + ", the most " + @PKG@.GearLL.an(@PKG@.GearLL.tname(@PKG@.GearLL.tier(id))) + " " + @PKG@.GearLL.kname(k, id).toLowerCase() + " takes - tier it up for " + @PKG@.GearCfg.LL_LCAPT + " more levels (your points stay banked).";
  }
  if (@PKG@.GearLL.isAbil(p)) {
    int c = @PKG@.GearLL.abilCap(u, P, k);
    if (lv + 1 <= c) return null;
    int tl = @PKG@.GearLL.levelFor(u, id);
    return nm + " " + (lv + 1) + " needs tool Lv " + @PKG@.GearLL.pkNeedLv(p, lv + 1) + " (your " + @PKG@.GearLL.kname(k, id).toLowerCase() + " is Lv " + (tl < 1 ? 1 : tl) + " - it levels with " + @PKG@.GearLL.KSKILL[k] + ").";
  }
  return null;
}""")
''')

# ================================================================================================================ the Tools tab
rep('''  if (p == 0) return "+" + @PKG@.Gear.fnum((double) lv * @PKG@.GearCfg.LL_PSPD) + "% " + (k == 1 ? "Chopping" : "Mining") + " Power";''',
    '''  if (p == 0) return "+" + @PKG@.Gear.fnum((double) lv * @PKG@.GearCfg.LL_PSPD) + "% " + (k == 1 ? "Chopping" : "Mining") + " Power";
  if (p == @PKG@.GearLL.PK_SWING) return "+" + @PKG@.Gear.fnum((double) lv * @PKG@.GearCfg.LL_PSWING) + "% swing speed";          // 0.3.17''')
rep('''public void perkRow(@UCB@ b, @UEB@ ev, java.util.UUID u, java.util.Properties P, int k, int p, String id) {
  int lv = @PKG@.GearLL.perkOf(P, k, p);
  int mx = @PKG@.GearLL.PKMAX[p];
  int t = @PKG@.GearLL.tier(id);
  boolean on = @PKG@.GearLL.perkOn2(k, p);          // 0.3.6
  int cost = @PKG@.GearLL.pkCost(p, lv + 1);
  int need = @PKG@.GearLL.pkNeed(p, lv + 1);
  int fr = @PKG@.GearLL.free(u, P, k);
  String nx;
  boolean can = false;
  if (!on) nx = k == @PKG@.GearLL.POLE ? "Needs SkyyFishing 0.1.6 or newer" : "Comes with the next SkyyTrees update";          // 0.3.6
  else if (lv >= mx) nx = "Top level";
  else if (t < need) nx = "Next level needs " + @PKG@.GearLL.an(@PKG@.GearLL.tname(need)) + " " + @PKG@.GearLL.KIND[k];
  else { nx = "Next: " + effect(k, p, lv + 1) + " for " + cost + " point" + (cost == 1 ? "" : "s"); can = fr >= cost; }
  String g = "#SkyyGPk" + p;
  b.appendInline("#SkyyGPanel", "Group " + g + " { Anchor: (Height: 76); LayoutMode: Left; Padding: (Full: 8); Background: #000000(0.25); Group { Anchor: (Width: 366); LayoutMode: Top; Label " + g + "N { Anchor: (Height: 30); Text: \\"\\"; Style: (FontSize: 17, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); } Label " + g + "D { Anchor: (Height: 26); Text: \\"\\"; Style: (FontSize: 14, TextColor: #96a9be, VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); } } Group { Anchor: (Width: 10); } TextButton " + g + "B { Anchor: (Width: 160, Height: 44); Text: \\"\\"; " + @PKG@.GearUi.btn(can ? 0 : 3) + " } }");
  b.set(g + "B.Text", lv >= mx ? "Max" : "+1 (" + cost + " pt)");          // 0.3.10: by b.set
  b.set(g + "N.Text", @PKG@.GearLL.PKN[p] + "   Lv " + lv + " / " + mx + (lv > 0 ? "   (" + effect(k, p, lv) + ")" : ""));
  b.set(g + "D.Text", nx);
  b.appendInline("#SkyyGPanel", "Group { Anchor: (Height: 6); }");''',
    '''public void perkRow(@UCB@ b, @UEB@ ev, java.util.UUID u, java.util.Properties P, int k, int p, String id) {
  int lv = @PKG@.GearLL.perkOf(P, k, p);
  int mx = @PKG@.GearLL.pkMax(p);          // 0.3.17: lines have no hard max, abilities lifelong.abilityMax
  int t = @PKG@.GearLL.tier(id);
  boolean on = @PKG@.GearLL.perkOn2(k, p);          // 0.3.6
  int cost = @PKG@.GearLL.pkCost(p, lv + 1);
  int need = @PKG@.GearLL.pkNeed(p, lv + 1);
  int fr = @PKG@.GearLL.free(u, P, k);
  boolean line = @PKG@.GearLL.isLine(p);
  int cap = line ? @PKG@.GearLL.lineCap(P, k) : (@PKG@.GearLL.isAbil(p) ? @PKG@.GearLL.abilCap(u, P, k) : mx);
  int ef = @PKG@.GearLL.perkEff(u, P, k, p);
  String cw = @PKG@.GearLife.capWhy(u, P, k, p, lv);
  String nx;
  boolean can = false;
  if (!on) nx = k == @PKG@.GearLL.POLE ? "Needs SkyyFishing 0.1.6 or newer" : "Comes with the next SkyyTrees update";          // 0.3.6
  else if (lv >= mx) nx = "Top level";
  else if (t < need) nx = "Next level needs " + @PKG@.GearLL.an(@PKG@.GearLL.tname(need)) + " " + @PKG@.GearLL.KIND[k];
  else if (cw != null) nx = line ? "Cap " + cap + " for " + @PKG@.GearLL.an(@PKG@.GearLL.tname(t)) + " tool - tier up for " + @PKG@.GearCfg.LL_LCAPT + " more (points stay banked)" : "Next level needs tool Lv " + @PKG@.GearLL.pkNeedLv(p, lv + 1);          // 0.3.17
  else { nx = "Next: " + effect(k, p, lv + 1) + " for " + cost + " point" + (cost == 1 ? "" : "s"); can = fr >= cost; }
  String g = "#SkyyGPk" + p;
  int nr = 0;
  for (int q = 0; q < @PKG@.GearLL.PK.length; q++) if (@PKG@.GearLL.perkFor(k, q)) nr++;
  boolean sm = nr >= 5;          // 0.3.17: 5 perk rows (+ Breaking Speed) fit the panel at 62 px a row
  b.appendInline("#SkyyGPanel", "Group " + g + " { Anchor: (Height: " + (sm ? 62 : 76) + "); LayoutMode: Left; Padding: (Full: " + (sm ? 4 : 8) + "); Background: #000000(0.25); Group { Anchor: (Width: 366); LayoutMode: Top; Label " + g + "N { Anchor: (Height: " + (sm ? 28 : 30) + "); Text: \\"\\"; Style: (FontSize: 17, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 12); } Label " + g + "D { Anchor: (Height: " + (sm ? 24 : 26) + "); Text: \\"\\"; Style: (FontSize: 14, TextColor: #96a9be, VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); } } Group { Anchor: (Width: 10); } TextButton " + g + "B { Anchor: (Width: 160, Height: " + (sm ? 40 : 44) + "); Text: \\"\\"; " + @PKG@.GearUi.btn(can ? 0 : 3) + " } }");
  b.set(g + "B.Text", lv >= mx ? "Max" : "+1 (" + cost + " pt)");          // 0.3.10: by b.set
  String lt = line ? (cap >= @PKG@.GearLL.LINE_BIG ? " (no cap)" : " / " + cap) : " / " + mx;
  b.set(g + "N.Text", @PKG@.GearLL.PKN[p] + "   Lv " + lv + lt + (ef > 0 ? "   (" + effect(k, p, ef) + ")" : ""));
  b.set(g + "D.Text", nx);
  b.appendInline("#SkyyGPanel", "Group { Anchor: (Height: " + (sm ? 4 : 6) + "); }");''')
rep('''  b.set("#SkyyGPSub.Text", fr + " of " + er + " points free - you get 1 point for every " + @PKG@.GearLL.KSKILL[k] + " level");''',
    '''  int cp = @PKG@.GearLL.collPts(u, k);          // 0.3.17: + the collection points
  b.set("#SkyyGPSub.Text", fr + " of " + er + " points free - 1 point for every " + @PKG@.GearLL.KSKILL[k] + " level" + (cp > 0 ? " + " + cp + " from collections" : ""));''')

# ================================================================================================================ 7b: the per-profile one-time update (GearLife)
before('''M(glf, r"""
public static void sweep0(@PR@ pr, @INV@ inv, boolean force) {''', r'''# ---- 0.3.17 ONE-TIME UPDATE of a profile's registry (tools/gear_0_3_17_patch.py item 7b): a saved LINE level (Breaking Power / Speed / Fortune)
# ABOVE its 10 x tier cap is lowered to the cap (its points are free again - spent is derived from the levels). Vein Mine / Tree Feller are NEVER
# lowered (critic fix: their cap follows the skill level - perkEff caps them live, a reborn / low-skill player keeps the levels). Verified history
# copy first (lifelong/history/<pk>.pre-0.3.17.properties), marker t1=1, LL-T1MIG lines + one chat line. Nothing above a cap = only the marker
# (it rides the next registry save). Returns true when the registry was written here.
M(glf, r"""
public static boolean t1Hist(String pk) {
  try {
    java.nio.file.Path f = @PKG@.GearLL.file(pk);
    if (f == null || !java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return true;
    byte[] old = java.nio.file.Files.readAllBytes(f);
    java.nio.file.Path hd = f.toAbsolutePath().getParent().resolve("history");
    java.nio.file.Files.createDirectories(hd, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path h = hd.resolve(f.getFileName().toString().replace(".properties", "") + ".pre-0.3.17.properties");
    if (java.nio.file.Files.exists(h, new java.nio.file.LinkOption[0])) return true;
    java.nio.file.Files.write(h, old, new java.nio.file.OpenOption[0]);
    return java.util.Arrays.equals(old, java.nio.file.Files.readAllBytes(h));
  } catch (Throwable t) { @PKG@.Gear.warn("lifelong 0.3.17 update: the history copy of " + pk + " failed (nothing changed; the next look tries again): " + t); return false; }
}""")
M(glf, r"""
public static boolean t1Mig(@PR@ pr, String pk, java.util.Properties P) {
  if (P == null || "1".equals(P.getProperty("t1")) || Boolean.getBoolean("skyy.harness.no317")) return false;
  java.util.UUID u = pr == null ? null : pr.getUuid();
  java.util.Properties old = (java.util.Properties) P.clone();
  StringBuilder sb = new StringBuilder();
  for (int k = 0; k < @PKG@.GearLL.KIND.length; k++) {
    for (int p = 0; p < @PKG@.GearLL.PK.length; p++) {
      if (!@PKG@.GearLL.perkFor(k, p) || !@PKG@.GearLL.isLine(p)) continue;          // critic fix: LINES only (Vein Mine / Tree Feller follow the skill: perkEff caps them live, nothing is lowered)
      int lv = @PKG@.GearLL.perkOf(P, k, p);
      if (lv <= 0) continue;
      int c = @PKG@.GearLL.lineCap(P, k);
      if (lv <= c) continue;
      String key = @PKG@.GearLL.KIND[k] + ".up." + @PKG@.GearLL.PK[p];
      if (c > 0) P.setProperty(key, String.valueOf(c)); else P.remove(key);
      if (sb.length() > 0) sb.append(", ");
      sb.append(@PKG@.GearLL.KIND[k]).append(' ').append(@PKG@.GearLL.PKN[p]).append(' ').append(lv).append(" -> ").append(c);
    }
  }
  P.setProperty("t1", "1");
  if (sb.length() == 0) return false;
  if (!t1Hist(pk)) { P.clear(); P.putAll(old); return false; }
  if (!@PKG@.GearLL.save(pk, P)) { P.clear(); P.putAll(old); return false; }
  @PKG@.GearLL.TN17[5] = @PKG@.GearLL.TN17[5] + 1L;
  if (u != null) @PKG@.GearTool.LAST.remove(u);
  @PKG@.GearLog.line("LL-T1MIG " + u + " " + pk + " " + sb);
  @PKG@.Gear.info("lifelong 0.3.17 update: " + pk + " " + sb + " (the new caps; the points are free again; history copy kept)");
  tellOnce(pr, "t1mig", "Tool upgrades changed: " + sb + " (the new caps) - those points are free again on the Upgrade tab.", 5000L);
  return true;
}""")
''')
rep('''  rbApply(pr, pk, P);          // 0.3.5 REBIRTH R7: a committed rebirth record -> the registry (once)
''', '''  rbApply(pr, pk, P);          // 0.3.5 REBIRTH R7: a committed rebirth record -> the registry (once)
  t1Mig(pr, pk, P);          // 0.3.17: saved levels above the new caps -> the cap (once, history first)
''')

# ================================================================================================================ 8: the salvage bridge (late: GearUp exists)
G317_LATE = r'''# ####################################################################################################################################
# 0.3.17 item 8 (tools/gear_0_3_17_patch.py): gear:fn:salvage = GearSalvFn over GearSalv - part of a piece's recipe + tier-up materials, NEVER coins.
# ####################################################################################################################################
gsalv = mk("GearSalv")
gsalvfn = mk("GearSalvFn")
G317_CLASSES = [gsalv, gsalvfn]
F(gsalv, "public static final java.util.concurrent.ConcurrentHashMap REC = new java.util.concurrent.ConcurrentHashMap();")   # output id -> Object[] { ids, qty } | FALSE
F(gsalv, "public static volatile int REC_N = -1;")
F(gsalv, "public static volatile String PSRC = null;")
F(gsalv, "public static volatile int[] PCT = new int[] { 25, 30, 35, 40, 45, 50 };")
F(gsalv, "public static final long[] N = new long[5];")          # 0 quotes, 1 commits, 2 refused repeats, 3 refused other, 4 errors
M(gsalv, r"""
public static int[] parse(String v) {
  if (v == null) return null;
  String[] p = v.split(",");
  if (p.length != 6) return null;
  int[] a = new int[6];
  for (int i = 0; i < 6; i++) {
    try { a[i] = Integer.parseInt(p[i].trim()); } catch (Throwable t) { return null; }
    if (a[i] < 0 || a[i] > 100) return null;
  }
  return a;
}""")
M(gsalv, r"""
public static String check(String key, String value) {
  return parse(value) == null ? "Salvage % by rarity: 6 whole numbers from 0 to 100 (Normal, Unique, Rare, Legendary, Fabled, Mythic), joined by commas." : null;
}""")
M(gsalv, r"""
public static int pct(int r) {
  String v = @PKG@.GearCfg.SALV_PCT;
  if (v != null && !v.equals(PSRC)) {
    int[] a = parse(v);
    if (a == null) @PKG@.Gear.warnOnce("salvpct:" + v.hashCode(), "config.properties: salvage.pct '" + v + "' is not 6 numbers 0-100 - the default 25,30,35,40,45,50 applies");
    PCT = a == null ? new int[] { 25, 30, 35, 40, 45, 50 } : a;
    PSRC = v;
  }
  int[] a2 = PCT;
  if (r < 0) r = 0;
  return r < a2.length ? a2[r] : a2[a2.length - 1];
}""")
# the inputs of the recipe whose primary output is id (quantity 1; the lowest recipe id wins), cached until the store's size changes; null = none
M(gsalv, r"""
public static Object[] recipeIn(String id) {
  if (id == null) return null;
  java.util.Map m = null;
  try { m = @CRR@.getAssetMap().getAssetMap(); } catch (Throwable t) { m = null; }
  if (m == null) return null;
  if (m.size() != REC_N) { REC.clear(); REC_N = m.size(); }
  Object c = REC.get(id);
  if (c instanceof Object[]) return (Object[]) c;
  if (c != null) return null;
  Object[] best = null;
  String bid = null;
  java.util.Iterator it = new java.util.ArrayList(m.values()).iterator();
  while (it.hasNext()) {
    Object o = it.next();
    if (!(o instanceof @CRR@)) continue;
    @CRR@ rc = (@CRR@) o;
    @MQ@ po = rc.getPrimaryOutput();
    if (po == null || !id.equals(po.getItemId()) || po.getQuantity() != 1) continue;
    String rid = rc.getId();
    if (best != null && (rid == null || (bid != null && rid.compareTo(bid) >= 0))) continue;
    @MQ@[] in = rc.getInput();
    if (in == null) continue;
    java.util.ArrayList ids = new java.util.ArrayList();
    java.util.ArrayList qs = new java.util.ArrayList();
    for (int i = 0; i < in.length; i++) {
      @MQ@ q = in[i];
      if (q == null || q.getItemId() == null || q.getQuantity() < 1) continue;
      int j = ids.indexOf(q.getItemId());
      if (j >= 0) qs.set(j, Integer.valueOf(((Integer) qs.get(j)).intValue() + q.getQuantity()));
      else { ids.add(q.getItemId()); qs.add(Integer.valueOf(q.getQuantity())); }
    }
    String[] ia = new String[ids.size()];
    int[] qa = new int[ids.size()];
    for (int i = 0; i < ia.length; i++) { ia[i] = (String) ids.get(i); qa[i] = ((Integer) qs.get(i)).intValue(); }
    best = new Object[] { ia, qa };
    bid = rid;
  }
  REC.put(id, best == null ? (Object) Boolean.FALSE : (Object) best);
  return best;
}""")
# the step INTO id on the upgrade ladders (its from id; null = none)
M(gsalv, r"""
public static String prevOf(String id) {
  if (id == null) return null;
  Object[] tb = @PKG@.GearUp.tab();
  String[] f = (String[]) tb[0];
  String[] t = (String[]) tb[1];
  for (int i = 0; i < t.length && i < f.length; i++) if (id.equals(t[i]) && f[i] != null && !f[i].equals(id)) return f[i];
  return null;
}""")
M(gsalv, r"""
public static void add(java.util.LinkedHashMap acc, String[] ids, int[] q) {
  if (ids == null || q == null) return;
  for (int i = 0; i < ids.length && i < q.length; i++) {
    if (ids[i] == null || q[i] <= 0) continue;
    Object o = acc.get(ids[i]);
    long v = o instanceof Long ? ((Long) o).longValue() : 0L;
    acc.put(ids[i], Long.valueOf(v + (long) q[i]));
  }
}""")
# every material the piece took: walk the ladder down (each step's cost: written or the live recipe, + the Enchanted Sticks), then the first
# piece's own recipe; at most 12 steps (a loop in the ladders stops there)
M(gsalv, r"""
public static java.util.LinkedHashMap mats(String id) {
  java.util.LinkedHashMap acc = new java.util.LinkedHashMap();
  String cur = id;
  java.util.HashSet seen = new java.util.HashSet();
  for (int d = 0; d < 12 && cur != null && seen.add(cur); d++) {
    String pv = prevOf(cur);
    Object[] c = null;
    if (pv != null) c = @PKG@.GearUp.cost(pv, cur);
    if (c == null) {
      Object[] r = recipeIn(cur);
      if (r != null) add(acc, (String[]) r[0], (int[]) r[1]);
      break;
    }
    add(acc, (String[]) c[0], (int[]) c[1]);
    cur = pv;
  }
  return acc;
}""")
# 0.3.17 critic fix (Skyy "Drops give less"): a dropped piece's BASE recipe = its own recipe, else the first piece of its ladder's (no steps)
M(gsalv, r"""
public static java.util.LinkedHashMap baseMats(String id) {
  java.util.LinkedHashMap acc = new java.util.LinkedHashMap();
  String cur = id;
  java.util.HashSet seen = new java.util.HashSet();
  for (int d = 0; d < 12 && cur != null && seen.add(cur); d++) {
    Object[] r = recipeIn(cur);
    if (r != null) { add(acc, (String[]) r[0], (int[]) r[1]); break; }
    cur = prevOf(cur);
  }
  return acc;
}""")
M(gsalv, "public static boolean crafted(@BD@ d) { String s = @PKG@.GearData.str(d, \"src\", \"\"); return \"craft\".equals(s) || \"merge\".equals(s); }")
# a document's key for the journal (critic fix: STABLE fields only - the item id, the birth stamps at / b0 and the rolls; never the whole
# document, whose level / counters change with use)
M(gsalv, r"""
public static String num(@BD@ d, String k) {
  if (d == null) return "0";
  @BV@ v = d.get(k);
  return v != null && v.isNumber() ? String.valueOf(v.asNumber().longValue()) : "0";
}""")
M(gsalv, r"""
public static String keyOf(String id, @BD@ d) {
  @BV@ ms = d == null ? null : d.get("mods");
  String mj = ms == null ? "" : String.valueOf(ms);
  return id + "|" + num(d, "at") + "|" + num(d, "b0") + "|" + Integer.toHexString(mj.hashCode()) + "|" + mj.length();
}""")
M(gsalv, "public static Object[] no(String why) { N[3] = N[3] + 1L; return new Object[] { why, new String[0], new Long[0], null }; }")
# Object[] { String why (null = fine), String[] ids, Long[] qty, String key }
M(gsalv, r"""
public static Object[] quote(java.util.UUID u, String id, @BD@ md) {
  N[0] = N[0] + 1L;
  if (!@PKG@.GearCfg.SALV_ON) return no("Salvaging is switched off on this server.");
  if (u == null || id == null || id.length() == 0) return no("Pick a piece of gear first.");
  if (@PKG@.Gear.item(id) == null) return no("There is no item " + id + " on this server.");
  @BD@ d = null;
  try { d = md == null ? null : @PKG@.GearData.gearDoc(md); } catch (Throwable t) { d = null; }
  if (d == null) return no(@PKG@.Gear.itemName(id) + " is no SkyyGear piece - it cannot be salvaged.");
  if (@PKG@.GearLL.isLL(d)) return no("Lifelong tools are never salvaged - they stay with you.");
  if (!@PKG@.GearData.identified(d)) return no("Identify " + @PKG@.Gear.itemName(id) + " first" + @PKG@.GearCfg.idHow() + ".");
  boolean cr = crafted(d);          // critic fix (Skyy "Drops give less"): crafted = recipe + tier-ups x rarity %, dropped = base recipe x salvage.dropPct
  java.util.LinkedHashMap m = cr ? mats(id) : baseMats(id);
  if (m.isEmpty()) return no(@PKG@.Gear.itemName(id) + " has no recipe to salvage (boss, quest and Untiered pieces cannot be salvaged).");
  int pc = cr ? pct(@PKG@.GearData.rarity(d)) : @PKG@.GearCfg.SALV_DROP;
  java.util.ArrayList ids = new java.util.ArrayList();
  java.util.ArrayList qs = new java.util.ArrayList();
  String big = null;
  long bq = 0L;
  java.util.Iterator it = m.keySet().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    long v = ((Long) m.get(k)).longValue();
    if (v > bq) { bq = v; big = k; }
    long g = v * (long) pc / 100L;
    if (g <= 0L) continue;
    ids.add(k);
    qs.add(Long.valueOf(g));
  }
  if (ids.isEmpty() && big != null && pc > 0) { ids.add(big); qs.add(Long.valueOf(1L)); }
  if (ids.isEmpty()) return no("Salvaging " + @PKG@.Gear.itemName(id) + " gives nothing back on this server (salvage.pct).");
  String[] ia = (String[]) ids.toArray(new String[0]);
  Long[] qa = (Long[]) qs.toArray(new Long[0]);
  return new Object[] { null, ia, qa, keyOf(id, d) };
}""")
M(gsalv, r"""
public static java.nio.file.Path jfile(String pk) {
  java.nio.file.Path d = @PKG@.GearCfg.DIR;
  if (d == null || pk == null || pk.length() == 0) return null;
  return d.resolve("salvage").resolve(@PKG@.GearLL.safeKey(pk) + ".properties");
}""")
# the commit: the quote + the piece's key written to the profile's journal BEFORE the answer (atomic: tmp + move); a key already there = refused
M(gsalv, r"""
public static synchronized Object[] commit(java.util.UUID u, String id, @BD@ md) {
  Object[] q = quote(u, id, md);
  if (q[0] != null) return q;
  String key = (String) q[3];
  String pk = @PKG@.Gear.pkey(u);
  java.nio.file.Path f = jfile(pk);
  if (f == null) return no("Your profile is not ready - nothing was salvaged.");
  try {
    java.util.Properties J = new java.util.Properties();
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
      try { J.load(in); } finally { in.close(); }
    }
    if (J.getProperty(key) != null) { N[2] = N[2] + 1L; return no("That piece was salvaged already - nothing more to give."); }
    J.setProperty(key, String.valueOf(System.currentTimeMillis()));
    java.nio.file.Files.createDirectories(f.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = f.resolveSibling(f.getFileName().toString() + ".tmp");
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
    try { J.store(out, "SkyyGear salvage journal (0.3.17): one line per salvaged piece - a piece listed here is never salvaged again"); } finally { out.close(); }
    java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE });
  } catch (Throwable t) {
    N[4] = N[4] + 1L;
    @PKG@.Gear.warn("salvage journal write failed for " + pk + " (nothing salvaged): " + t);
    return no("The salvage could not be saved - nothing was salvaged.");
  }
  N[1] = N[1] + 1L;
  String[] ia = (String[]) q[1];
  Long[] qa = (Long[]) q[2];
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < ia.length; i++) { if (i > 0) sb.append(','); sb.append(ia[i]).append('*').append(qa[i]); }
  @PKG@.GearLog.line("SALVAGE " + u + " " + pk + " " + id + " -> " + sb + " (no coins)");
  return q;
}""")
# release: the caller's removal failed after a commit - the key leaves the journal again (atomic); not there = refused
M(gsalv, r"""
public static synchronized Object[] release(java.util.UUID u, String id, @BD@ md) {
  if (u == null || id == null) return no("Pick a piece of gear first.");
  @BD@ d = null;
  try { d = md == null ? null : @PKG@.GearData.gearDoc(md); } catch (Throwable t) { d = null; }
  if (d == null) return no("No gear document - nothing to release.");
  String key = keyOf(id, d);
  String pk = @PKG@.Gear.pkey(u);
  java.nio.file.Path f = jfile(pk);
  if (f == null || !java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return no("That piece was not salvaged.");
  try {
    java.util.Properties J = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
    try { J.load(in); } finally { in.close(); }
    if (J.remove(key) == null) return no("That piece was not salvaged.");
    java.nio.file.Path tmp = f.resolveSibling(f.getFileName().toString() + ".tmp");
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
    try { J.store(out, "SkyyGear salvage journal (0.3.17): one line per salvaged piece - a piece listed here is never salvaged again"); } finally { out.close(); }
    java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE });
  } catch (Throwable t) {
    N[4] = N[4] + 1L;
    @PKG@.Gear.warn("salvage journal release failed for " + pk + ": " + t);
    return no("The release could not be saved.");
  }
  @PKG@.GearLog.line("SALVAGE-RELEASE " + u + " " + pk + " " + id);
  return new Object[] { null, new String[0], new Long[0], key };
}""")
M(gsalv, "public static String statusText() { return \"salvage \" + (@PKG@.GearCfg.SALV_ON ? \"on (gear:fn:salvage, \" + @PKG@.GearCfg.SALV_PCT + \" % by rarity, never coins; quotes \" + N[0] + \", commits \" + N[1] + \", repeats refused \" + N[2] + \")\" : \"OFF (salvage.on)\"); }")
gsalvfn.addInterface(pool.get("java.util.function.Function"))
C(gsalvfn, "public GearSalvFn() { }")
M(gsalvfn, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof Object[])) return @PKG@.GearSalv.no("gear:fn:salvage takes Object[] { UUID, item id, metadata, mode }.");
    Object[] a = (Object[]) o;
    if (a.length < 2 || !(a[0] instanceof java.util.UUID)) return @PKG@.GearSalv.no("gear:fn:salvage takes Object[] { UUID, item id, metadata, mode }.");
    java.util.UUID u = (java.util.UUID) a[0];
    String id = null;
    @BD@ md = null;
    String mode = "quote";
    if (a[1] instanceof String) {
      id = (String) a[1];
      if (a.length > 2 && a[2] instanceof @BD@) md = (@BD@) a[2];
      if (a.length > 3 && a[3] instanceof String) mode = (String) a[3];
    } else if (a[1] instanceof @BD@) {
      @BD@ doc = (@BD@) a[1];
      String[] ik = new String[] { "Id", "ItemId", "id", "itemId" };
      for (int i = 0; i < ik.length && id == null; i++) { @BV@ v = doc.get(ik[i]); if (v != null && v.isString()) id = v.asString().getValue(); }
      String[] mk2 = new String[] { "Metadata", "metadata" };
      for (int i = 0; i < mk2.length && md == null; i++) { @BV@ v = doc.get(mk2[i]); if (v != null && v.isDocument()) md = v.asDocument(); }
      if (a.length > 2 && a[2] instanceof String) mode = (String) a[2];
    }
    if ("commit".equals(mode)) return @PKG@.GearSalv.commit(u, id, md);
    if ("release".equals(mode)) return @PKG@.GearSalv.release(u, id, md);
    return @PKG@.GearSalv.quote(u, id, md);
  } catch (Throwable t) {
    @PKG@.GearSalv.N[4] = @PKG@.GearSalv.N[4] + 1L;
    @PKG@.Gear.warnOnce("salvfn", "gear:fn:salvage failed: " + t);
    return @PKG@.GearSalv.no("Salvage failed - nothing was salvaged.");
  }
}""")
pl.getDeclaredMethod("start").insertAfter(J("""{
  @PKG@.Gear.bridge().put("gear:fn:salvage", new @PKG@.GearSalvFn());          // 0.3.17: SkyyWardrobe's Requip SALVAGE (materials, never coins)
  @PKG@.Gear.info("[SkyyGear] 0.3.17: tool lines uncapped (Breaking Power " + @PKG@.Gear.fnum(@PKG@.GearCfg.LL_PSPD) + "%, Breaking Speed " + @PKG@.Gear.fnum(@PKG@.GearCfg.LL_PSWING) + "%, Fortune " + @PKG@.Gear.fnum(@PKG@.GearCfg.LL_PFORT) + " a level, " + @PKG@.GearCfg.LL_LCOST + " point, cap " + @PKG@.GearCfg.LL_LCAPT + " x tier), Vein Mine / Tree Feller max " + @PKG@.GearCfg.LL_ABMAX + " by tool level, collection points " + (@PKG@.GearCfg.LL_COLLPTS ? "on" : "off") + ", collection tier-up gate " + (@PKG@.GearCfg.LL_COLLGATE ? "on" : "off") + "; " + @PKG@.GearSalv.statusText());
}"""))
pl.getDeclaredMethod("shutdown").insertBefore(J("""{ try { @PKG@.Gear.bridge().remove("gear:fn:salvage"); } catch (Throwable t17) { } }"""))
print("0.3.17 T1: GearSalv / GearSalvFn (gear:fn:salvage); the lines / caps / costs in GearLL; t1Mig in the lifelong look; migrate0317 in setup")
'''
before('''from jpype import JClass as _JC10
''', G317_LATE)
rep('''+ G313_CLASSES + G314_CLASSES + G315_CLASSES''', '''+ G313_CLASSES + G314_CLASSES + G315_CLASSES + G317_CLASSES''')

# ================================================================================================================ checks on the result
_i = s.index
assert _i("public static boolean isLine(int p)") < _i("public static int perkOf(java.util.Properties P, int k, int p)") < _i("public static int perkEff(") \
    < _i("public static int spent(java.util.Properties P, int k)") < _i("public static int earned(java.util.UUID u, int k)") < _i("public static double[] perkFx(")
assert _i("public static String collWhy(") < _i("return collWhy(u, to);")
assert _i("public static String capWhy(") < _i("public static String buy(java.util.UUID u, int k, int p)") < _i("@PKG@.GearLife.capWhy(u, P, k, p, lv)")
assert _i("public static boolean t1Mig(") < _i("public static void sweep0(@PR@ pr, @INV@ inv, boolean force)")
assert _i("public static void swingPost(") < _i("@PKG@.GearLL.swingPost(u, s);")
assert _i("public static double fcap()") < _i("public static double fortune(int f, int lv, int t)")
assert s.count("> @PKG@.GearCfg.TOOL_FCAP)") == 0, "a TOOL_FCAP clamp is left (use fcap())"
assert s.count("@PKG@.GearLL.PKMAX[p]") == 1 and s.count("migrate0317();") == 1
_u = s
for _new, _old, _cnt in reversed(CHANGES):
    assert _u.count(_new) == _cnt, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old)
assert _u == OLD, "the generated script differs from 0.3.16 outside the recorded changes"
compile(s, DST, "exec")
open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(DST, ROOT), "(%d lines; 0.3.16 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
