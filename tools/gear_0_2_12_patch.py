"""Derive SkyyGear/build_skyygear_0.2.12.py from the LIVE 0.2.11 (build_skyygear_0.2.11.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_2_11_patch.py). Edit THIS file, never the generated script; every anchor is asserted. Run:
    python tools/gear_0_2_12_patch.py      then      python SkyyGear/build_skyygear_0.2.12.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.2.12.py (deploy WITH SkyySkills 0.4.26 - tools/skills_0_4_26_patch.py).

0.2.12 = TOOLS DO SOMETHING (Skyy 2026-10-05 "axes and pickaxes have the levels, now they need to actually do something." + 2026-10-09 "tools
still dont have chopping speed, and foraging fortune. or tree feller"; docs/answered/gear.md TOOL LEVELS LOCKED 2026-10-02 / ANSWERED
2026-10-03 / REQUEST 2026-10-05; numbers from research/cloud/Tool-Levels-Revision.md sections 2-4 + research/cloud/Gathering-Numbers-Reconciled.md).
  1. A gathering tool's LEVEL now gives it stats (the level it already stored since 0.2; the material band when it has none):
     - POWER (fewer hits per block; Skyy 2026-10-03 named it "Mining Power" / "Chopping Power": "your breaking power makes it take less hits
       to break a block"): pickaxes on rock + ore (SkyyTrees' Heavy Pick rule: an Ore_ id or gather type Rocks / VolcanicRocks / Ore*),
       shovels on Soils, hatchets on Woods ONLY (the Heavy Hatchet HARD RULE: tree / wood breaking only - weapon axes are never tools, a
       hatchet hitting a mob or a stone block is untouched). Factor = tool.power.<pickaxe|hatchet> curve (level:factor, 1.0 = vanilla, never
       below vanilla) x (1 + tool.power.matBonus % x material tier). Hatchets use a lower curve (Skyy 2026-10-03: "lower the damage so one
       chop comes later"): a Thorium hatchet + a maxed Heavy Hatchet still one-chops a log, Copper / Iron never do from the level alone.
       Applied in GearToolHitSys = an EntityEventSystem on the engine's DamageBlockEvent - the SAME hook SkyyTrees' TreeDmgSys uses for
       Heavy Hatchet / Heavy Pick: both multiply the event's damage (order-free, Tool-Levels-Spec 3.1), a cancelled hit is left alone.
     - FORTUNE (1 Fortune = +1 % chance of one extra drop; 100 = one guaranteed extra, SkyBlock style): tool.fortune.perLevel (0.2) x level
       x (1 + tool.fortune.matBonus % x tier) for pickaxes, shovels and hatchets; tool.fortune.perLevelFarm (0.3) for hoes and sickles (they
       get Fortune only, LOCKED 2026-10-02); capped at tool.fortune.cap (25). REUSES SkyySkills' double-drop path ("reused, never a second
       system"): the held tool's Fortune is posted as source "gear" in the shared skill:bonus:<uuid> map (the SkyyTrees "trees" source
       shape; key dd.mining / dd.foraging / dd.farming = Fortune / 100, only the held tool's skill). SkyySkills 0.4.26 rolls it as extra
       drops (above 100 = guaranteed extras + the remainder as a chance, its perk.fortuneMax cap); SkyySkills 0.4.25 (an older partner)
       already adds a dd.<skill> source to its double-drop chance, capped at perk.doubleDropMax. Foraging Fortune follows SkyySkills'
       perk.foraging.doubleDropOnly=_Trunk (logs only), placed blocks never double (SkyySkills' rule).
     - Material tier: Crude / Wood 0, Copper / Scrap 1, Iron / Bronze / Steel 2, Thorium 3, Cobalt 4, Adamantite 5, Mithril 6, Onyxium 7.
  2. The LEVEL REQUIREMENT is real for the bonus only (task + Tool-Levels-Spec: "never break vanilla mining"): a tool above your skill level
     (pickaxe + shovel Mining, hatchet Foraging, hoe + sickle Farming) works exactly like the plain vanilla tool - no power, no Fortune - and
     its tooltip says why ("No tool bonus until Foraging 20 - it works like a plain tool"). Nothing is ever blocked (the 2026-10-02 "cannot
     break blocks" answer is NOT built - see the report). Tools without a stored level (made before 0.2) work at min(their level, your skill)
     (the 2026-10-03 lenient rule for old tools). part.gate off = no requirement; no SkyySkills = no requirement.
  3. TOOLTIP: "Lv N - Requires Mining N" in the vanilla green (red + "(you: M)" when too low) - the "(coming later)" text and the grey
     "(coming later: gathering gear)" line are gone; then "Chopping Power +X%: 4 hits per log (vanilla 5)" (the REAL hit count of the
     vanilla tool's own power on a reference block: pickaxe stone, shovel soil, hatchet log - fix round, critic C1; a modded tool without
     a vanilla power shows "+X% on logs"), "<Skill> Fortune +F (F% extra log / rock / ore / sand / gravel / crop chance)", "No bonus until
     Foraging 20" when too low, and on hatchets "Tree Feller unlocks in the Foraging tree" (Tree Feller IS the SkyyTrees Foraging perk - no second system;
     axes granting it by tier (Tool-Levels-Revision 8) need SkyyTrees to read a "gear" feller.level - not in this round). Rarity / rolls / reforge
     for tools (REQUEST 2026-10-05 part 2) and Sickle Range are NOT in this round (the tool still says NORMAL TOOL).
  4. SERVER SETUP -> Gear -> Tools (new tab): part.tools, tool.power.pickaxe, tool.power.hatchet, tool.power.matBonus,
     tool.fortune.perLevel, tool.fortune.perLevelFarm, tool.fortune.matBonus, tool.fortune.cap. New keys only: a missing line means its
     default (the 0.1.2 rule) - NO one-time update, no live default changes; a fresh file lists them at its end.
  5. Bridge: skill:bonus:<uuid>["gear"] = { dd.<skill>: Fortune / 100, only.<skill>: "Rock_,Rubble_,Ore_" (pickaxe) / "Soil_" (shovel) }
     (fix round, critic B1: a shovel's Fortune never counts on stone / ore, a pickaxe's never on sand / gravel; SkyySkills 0.4.26 reads the
     filter, an older SkyySkills ignores the String key like every reader of skill:bonus (they all skip non-Number values)) (GearTool.post; refreshed on every block hit and at most 1 s after the held item / skill level
     changes - GearHandSys; removed on logout, profile:busy, under-level, a non-tool in hand and at shutdown).
No saved data, no migration, no command, no asset. 2 classes added (GearTool + GearToolHitSys). Rolling back to 0.2.11 is safe (tools lose
their stats again; SkyySkills simply stops seeing the "gear" source).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.11.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.12.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.2.11"' in s and s.startswith('"""SkyyGear 0.2.11 - build script'), "build_skyygear_0.2.11.py is not the live 0.2.11"
assert "GearTool" not in s and "part.tools" not in s, "0.2.11 already has the 0.2.12 parts"
SYS0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)


# ================================================================================================================ header + version
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
rep('''"""SkyyGear 0.2.11 - build script (javassist via jpype). GENERATED by tools/gear_0_2_11_patch.py from the LIVE 0.2.10 - edit the patch,
never this file. Run: python SkyyGear/build_skyygear_0.2.11.py -> SkyyGear/SkyyGear-0.2.11.jar (never --deploy).

0.2.11 = ''', '''"""SkyyGear 0.2.12 - build script (javassist via jpype). GENERATED by tools/gear_0_2_12_patch.py from the LIVE 0.2.11 - edit the patch,
never this file. Run: python SkyyGear/build_skyygear_0.2.12.py -> SkyyGear/SkyyGear-0.2.12.jar (never --deploy).

''' + HEAD[HEAD.index("0.2.12 = "):].strip() + '''

0.2.11 (the base, everything below is still true unless 0.2.12 above says otherwise):
0.2.11 = ''')
rep('VERSION = "0.2.11"', 'VERSION = "0.2.12"')
rep('''crits show a CRIT! popup and vanilla crit sparks; Server Setup -> Gear. Replaces SkyyRolls.''',
    '''crits show a CRIT! popup and vanilla crit sparks; gathering tools get Mining / Chopping Power (fewer hits) and Fortune (extra drops through SkyySkills) from their level, above your skill they work like plain tools; Server Setup -> Gear. Replaces SkyyRolls.''')

# ================================================================================================================ numbers (python side)
TOOL_PY = r'''
# ================================================================= 0.2.12 TOOLS DO SOMETHING (tools/gear_0_2_12_patch.py header): defaults + checks
TOOL_PICK_DEF = "1:1.0,10:1.25,20:1.5,30:1.75,40:2.0,49:2.2,100:3.0"     # Mining Power (pickaxe on rock + ore, shovel on soil); 1.0 = vanilla
TOOL_HATCH_DEF = "1:1.0,10:1.2,20:1.45,30:1.65,40:1.85,49:2.0,100:2.6"   # Chopping Power (hatchet on Woods only) - lower: "one chop comes later"
TOOL_PMAT_DEF = 1.5           # % power per material tier step (Tool-Levels-Revision 2: tool.matBonus 1.5 % per tier)
TOOL_FPER_DEF = 0.2           # Fortune per level, pickaxe / shovel / hatchet (Revision 3)
TOOL_FFARM_DEF = 0.3          # Fortune per level, hoe / sickle (Fortune only, LOCKED 2026-10-02)
TOOL_FMAT_DEF = 2.0           # % Fortune per material tier step (Revision 3: x (1 + 2 % x tier))
TOOL_FCAP_DEF = 25.0          # tool Fortune cap (Revision 4 rule 3: tool.fortune.cap 25)
TOOL_TIERS = [("Crude", 0), ("Wood", 0), ("Copper", 1), ("Scrap", 1), ("Bronze", 2), ("Iron", 2), ("Steel", 2), ("Thorium", 3), ("Cobalt", 4),
              ("Adamantite", 5), ("Mithril", 6), ("Onyxium", 7)]
TOOL_FAMS = ["Tool_Pickaxe_", "Tool_Shovel_", "Tool_Hatchet_", "Tool_Hoe_", "Tool_Sickle_"]   # GearTool.fam 1..5
assert [p for p, _k in TOOL_FAMILIES if p in TOOL_FAMS] and sorted(p for p, _k in TOOL_FAMILIES) == sorted(TOOL_FAMS), "TOOL_FAMILIES changed"


def _tool_tier(i):
    for _w in i.split("_")[2:]:
        for _n, _t in TOOL_TIERS:
            if _w.lower() == _n.lower():
                return _t
    return None


def _tool_pt(txt, lv):
    _p = [(float(a), float(b)) for a, b in (x.split(":") for x in txt.split(","))]
    if lv <= _p[0][0]:
        return _p[0][1]
    for (_l0, _v0), (_l1, _v1) in zip(_p, _p[1:]):
        if lv <= _l1:
            return _v0 + (_v1 - _v0) * (lv - _l0) / (_l1 - _l0)
    return _p[-1][1]


# every vanilla gathering tool resolves a material tier (a new Hytale tool family / material stops the build here)
_TOOL_AZ_IDS = sorted(os.path.basename(n)[:-5] for n in AZ_NAMES if n.startswith("Server/Item/Items/") and n.endswith(".json")
                      and os.path.basename(n).startswith(tuple(TOOL_FAMS)))
_TOOL_NOTIER = [i for i in _TOOL_AZ_IDS if _tool_tier(i) is None]
assert len(_TOOL_AZ_IDS) >= 30 and not _TOOL_NOTIER, "vanilla tools without a material tier: %s" % _TOOL_NOTIER
for _c in (TOOL_PICK_DEF, TOOL_HATCH_DEF):
    _pp = [(float(a), float(b)) for a, b in (x.split(":") for x in _c.split(","))]
    assert _pp[0] == (1.0, 1.0) and all(b >= 1.0 for _a, b in _pp) and all(_pp[i][0] < _pp[i + 1][0] and _pp[i][1] <= _pp[i + 1][1]
                                                                          for i in range(len(_pp) - 1)), "a tool power curve must start at 1:1.0 and never fall"


def tool_hits(base_power, curve, lv, tier):
    """hits to break a block of health 1.0 (the engine rule, Tool-Levels-Spec 2.1 row 12) with the tool's vanilla spec power"""
    import math
    _m = max(1.0, _tool_pt(curve, lv) * (1.0 + TOOL_PMAT_DEF / 100.0 * tier))
    return int(math.ceil(1.0 / (base_power * _m) - 1e-9)), int(math.ceil(1.0 / base_power - 1e-9))


# the report numbers (vanilla spec powers, Assets.zip: Woods Copper 0.2 / Iron 0.3 / Thorium 0.5; Iron pickaxe OreIron 0.25)
TOOL_TABLE = []
for _nm, _pw, _cv, _lv, _ti in (("Copper hatchet on a log", 0.2, TOOL_HATCH_DEF, 10, 1), ("Copper hatchet on a log", 0.2, TOOL_HATCH_DEF, 18, 1),
                                ("Iron hatchet on a log", 0.3, TOOL_HATCH_DEF, 15, 2), ("Iron hatchet on a log", 0.3, TOOL_HATCH_DEF, 23, 2),
                                ("Thorium hatchet on a log", 0.5, TOOL_HATCH_DEF, 20, 3), ("Iron pickaxe on iron ore", 0.25, TOOL_PICK_DEF, 15, 2),
                                ("Iron pickaxe on iron ore", 0.25, TOOL_PICK_DEF, 23, 2)):
    _h, _v = tool_hits(_pw, _cv, _lv, _ti)
    assert _h <= _v, "a tool level made a block slower to break: %s Lv %d" % (_nm, _lv)
    TOOL_TABLE.append("%s Lv %d: %d hits (vanilla %d)" % (_nm, _lv, _h, _v))
# Heavy Hatchet hard rule check: a Thorium hatchet at its band start + a maxed Heavy Hatchet (+100 %) one-chops; Iron / Copper never do
assert 0.5 * _tool_pt(TOOL_HATCH_DEF, 20) * (1 + TOOL_PMAT_DEF / 100.0 * 3) * 2.0 >= 1.0
assert 0.3 * _tool_pt(TOOL_HATCH_DEF, 23) * (1 + TOOL_PMAT_DEF / 100.0 * 2) * 2.0 < 1.0
assert 0.2 * _tool_pt(TOOL_HATCH_DEF, 18) * (1 + TOOL_PMAT_DEF / 100.0 * 1) * 2.0 < 1.0


def tool_fortune(lv, tier, farm=False):
    _v = (TOOL_FFARM_DEF if farm else TOOL_FPER_DEF) * lv * (1.0 + TOOL_FMAT_DEF / 100.0 * tier)
    return round(min(_v, TOOL_FCAP_DEF) * 10.0) / 10.0


assert [tool_fortune(1, 0), tool_fortune(10, 1), tool_fortune(15, 2), tool_fortune(20, 3), tool_fortune(40, 6), tool_fortune(49, 6)] == \
    [0.2, 2.0, 3.1, 4.2, 9.0, 11.0], "Revision section 3 Fortune table"
assert tool_fortune(100, 11) == 24.4 and tool_fortune(100, 11, True) == 25.0, "Revision 3: Lv 100 = 24.4 / 36.6 -> cap 25"
'''
# the numbers need TOOL_FAMILIES + AZ_NAMES (both defined above the CFG rows): right before the config rows' categories
rep('''CFG_CATS = [("general", "General"), ("rarity", "Rarity"), ("levels", "Levels"), ("base", "Level stats"), ("stats", "Stats"),
            ("costs", "Costs"), ("drops", "Drops + craft"), ("loot", "Loot"), ("combat", "Combat"), ("migrate", "Migration")]''',
    TOOL_PY + '''CFG_CATS = [("general", "General"), ("rarity", "Rarity"), ("levels", "Levels"), ("base", "Level stats"), ("stats", "Stats"),
            ("costs", "Costs"), ("drops", "Drops + craft"), ("loot", "Loot"), ("tools", "Tools"), ("combat", "Combat"), ("migrate", "Migration")]''')

# ================================================================================================================ Server Setup rows
rep('''    ("loot.levelShift", "Mob level rarity boost", "loot", "dec", "0.02", "0", "1", "", "", "live,danger",
     "Mob bags: rarities above Normal weigh x(1 + this x (level - 1))." + PH, "field:GearCfg.LEVEL_SHIFT"),
''', '''    ("loot.levelShift", "Mob level rarity boost", "loot", "dec", "0.02", "0", "1", "", "", "live,danger",
     "Mob bags: rarities above Normal weigh x(1 + this x (level - 1))." + PH, "field:GearCfg.LEVEL_SHIFT"),
    # 0.2.12 TOOLS DO SOMETHING (Skyy 2026-10-05 / 2026-10-09). New keys: a missing line means its default (no one-time update)
    ("part.tools", "Tool stats", "tools", "bool", "true", "", "", "", "", "live,part,danger",
     "Tools get Mining / Chopping Power and Fortune from their level. Off = plain vanilla tools.", "field:GearCfg.PART_TOOLS"),
    ("tool.power.pickaxe", "Mining Power by level", "tools", "text", TOOL_PICK_DEF, "3", "300", "", "", "live,danger",
     "Pickaxe on rock + ore, shovel on soil: level:factor, 1.0 = vanilla." + PH,
     "field:GearCfg.TOOL_PICK;check=GearCfg.checkCurve"),
    ("tool.power.hatchet", "Chopping Power by level", "tools", "text", TOOL_HATCH_DEF, "3", "300", "", "", "live,danger",
     "Hatchets on logs only (no weapon axes): level:factor, 1.0 = vanilla." + PH,
     "field:GearCfg.TOOL_HATCH;check=GearCfg.checkCurve"),
    ("tool.power.matBonus", "Power bonus per material tier", "tools", "dec", repr(TOOL_PMAT_DEF), "0", "50", "", "%", "live,danger",
     "% more power per material step (Copper 1, Iron 2 ... Onyxium 7)." + PH, "field:GearCfg.TOOL_PMAT"),
    ("tool.fortune.perLevel", "Fortune per tool level", "tools", "dec", repr(TOOL_FPER_DEF), "0", "10", "", "", "live,danger",
     "Pickaxe, shovel, hatchet (1 Fortune = +1% extra drop)." + PH, "field:GearCfg.TOOL_FPER"),
    ("tool.fortune.perLevelFarm", "Farming Fortune per tool level", "tools", "dec", repr(TOOL_FFARM_DEF), "0", "10", "", "", "live,danger",
     "Hoes and sickles (Fortune only, no power)." + PH, "field:GearCfg.TOOL_FFARM"),
    ("tool.fortune.matBonus", "Fortune bonus per material tier", "tools", "dec", repr(TOOL_FMAT_DEF), "0", "50", "", "%", "live,danger",
     "% more Fortune per material step." + PH, "field:GearCfg.TOOL_FMAT"),
    ("tool.fortune.cap", "Tool Fortune cap", "tools", "dec", repr(TOOL_FCAP_DEF), "0", "1000", "", "", "live,danger",
     "Most Fortune one tool gives (100 = one sure extra drop)." + PH, "field:GearCfg.TOOL_FCAP"),
''')
rep('''LT_HEAD = "# ---- loot: mystery bags, extra mob / chest bags, re-identify (SkyyGear 0.2.11) ----"
''', '''LT_HEAD = "# ---- loot: mystery bags, extra mob / chest bags, re-identify (SkyyGear 0.2.11) ----"
# 0.2.12: the tool rows of a fresh file (an existing file gets each the first time it is changed in Server Setup)
TL_HEAD = "# ---- tools: Mining / Chopping Power + Fortune by tool level (SkyyGear 0.2.12) ----"
TL_ROWK = ["part.tools", "tool.power.pickaxe", "tool.power.hatchet", "tool.power.matBonus", "tool.fortune.perLevel", "tool.fortune.perLevelFarm",
           "tool.fortune.matBonus", "tool.fortune.cap"]
assert all(32 <= ord(_c) < 127 for _c in TL_HEAD) and "=" not in TL_HEAD
''')
rep('''    L += ["", LT_HEAD]         # 0.2.11: the loot rows at the very end of a fresh file (no one-time update adds them)
    for k in LT_ROWK:
        scal(k)
''', '''    L += ["", LT_HEAD]         # 0.2.11: the loot rows at the very end of a fresh file (no one-time update adds them)
    for k in LT_ROWK:
        scal(k)
    L += ["", TL_HEAD]         # 0.2.12: the tool rows at the very end of a fresh file (no one-time update adds them)
    for k in TL_ROWK:
        scal(k)
''')
rep('''              ("DROPONLY_W", "double", "1.0"), ("LOOT_EXCLUDE", "String", '""'), ("LEVEL_SHIFT", "double", "0.02")]''',
    '''              ("DROPONLY_W", "double", "1.0"), ("LOOT_EXCLUDE", "String", '""'), ("LEVEL_SHIFT", "double", "0.02"),
              # 0.2.12 tool stats
              ("PART_TOOLS", "boolean", "true"), ("TOOL_PICK", "String", jstr(TOOL_PICK_DEF)), ("TOOL_HATCH", "String", jstr(TOOL_HATCH_DEF)),
              ("TOOL_PMAT", "double", repr(TOOL_PMAT_DEF)), ("TOOL_FPER", "double", repr(TOOL_FPER_DEF)), ("TOOL_FFARM", "double", repr(TOOL_FFARM_DEF)),
              ("TOOL_FMAT", "double", repr(TOOL_FMAT_DEF)), ("TOOL_FCAP", "double", repr(TOOL_FCAP_DEF))]''')
rep('''F(gcf, "public static final String CURVE_DEF = %s;" % jstr(BASE_CURVE_NEW))      # 0.2.5: the steep Weapon curve F
''', '''F(gcf, "public static final String CURVE_DEF = %s;" % jstr(BASE_CURVE_NEW))      # 0.2.5: the steep Weapon curve F
F(gcf, "public static final String TOOL_PICK_DEF = %s;" % jstr(TOOL_PICK_DEF))     # 0.2.12 Mining Power
F(gcf, "public static final String TOOL_HATCH_DEF = %s;" % jstr(TOOL_HATCH_DEF))   # 0.2.12 Chopping Power
''')
rep('''  LEVEL_SHIFT = pdec(p, "loot.levelShift", 0.02, 0.0, 1.0);
''', '''  LEVEL_SHIFT = pdec(p, "loot.levelShift", 0.02, 0.0, 1.0);
  // 0.2.12 tool stats (Server Setup -> Gear -> Tools); a curve the check would refuse (a hand edit) falls back to its default with one WARN
  PART_TOOLS = pbool(p, "part.tools", true);
  String tpk = ptext(p, "tool.power.pickaxe", TOOL_PICK_DEF);
  if (checkCurve("tool.power.pickaxe", tpk) != null) { @PKG@.Gear.warnOnce("tpcurve:" + tpk, "config.properties: tool.power.pickaxe=" + tpk + " is not a list of level:factor points - the default " + TOOL_PICK_DEF + " is used"); tpk = TOOL_PICK_DEF; }
  TOOL_PICK = tpk.trim();
  String thk = ptext(p, "tool.power.hatchet", TOOL_HATCH_DEF);
  if (checkCurve("tool.power.hatchet", thk) != null) { @PKG@.Gear.warnOnce("thcurve:" + thk, "config.properties: tool.power.hatchet=" + thk + " is not a list of level:factor points - the default " + TOOL_HATCH_DEF + " is used"); thk = TOOL_HATCH_DEF; }
  TOOL_HATCH = thk.trim();
  TOOL_PMAT = pdec(p, "tool.power.matBonus", @TPMAT@, 0.0, 50.0);
  TOOL_FPER = pdec(p, "tool.fortune.perLevel", @TFPER@, 0.0, 10.0);
  TOOL_FFARM = pdec(p, "tool.fortune.perLevelFarm", @TFFARM@, 0.0, 10.0);
  TOOL_FMAT = pdec(p, "tool.fortune.matBonus", @TFMAT@, 0.0, 50.0);
  TOOL_FCAP = pdec(p, "tool.fortune.cap", @TFCAP@, 0.0, 1000.0);
'''.replace("@TPMAT@", "TOOL_PMAT_DEFV").replace("@TFPER@", "TOOL_FPER_DEFV").replace("@TFFARM@", "TOOL_FFARM_DEFV")
    .replace("@TFMAT@", "TOOL_FMAT_DEFV").replace("@TFCAP@", "TOOL_FCAP_DEFV"))
rep('''F(gcf, "public static final String TOOL_HATCH_DEF = %s;" % jstr(TOOL_HATCH_DEF))   # 0.2.12 Chopping Power
''', '''F(gcf, "public static final String TOOL_HATCH_DEF = %s;" % jstr(TOOL_HATCH_DEF))   # 0.2.12 Chopping Power
for _n, _v in (("TOOL_PMAT_DEFV", TOOL_PMAT_DEF), ("TOOL_FPER_DEFV", TOOL_FPER_DEF), ("TOOL_FFARM_DEFV", TOOL_FFARM_DEF),
               ("TOOL_FMAT_DEFV", TOOL_FMAT_DEF), ("TOOL_FCAP_DEFV", TOOL_FCAP_DEF)):
    F(gcf, "public static final double %s = %r;" % (_n, float(_v)))
''')

rep('''           "part.lootMob", "loot.mob.chance", "part.lootChest", "loot.chest.chance", "unid.bags", "unid.reroll.mult", "loot.levelShift"}
''', '''           "part.lootMob", "loot.mob.chance", "part.lootChest", "loot.chest.chance", "unid.bags", "unid.reroll.mult", "loot.levelShift",
           # 0.2.12: the tool part switch + every tool number (gathering speed + Fortune = economy) - confirm in Server Setup
           "part.tools", "tool.power.pickaxe", "tool.power.hatchet", "tool.power.matBonus", "tool.fortune.perLevel", "tool.fortune.perLevelFarm",
           "tool.fortune.matBonus", "tool.fortune.cap"}
''')

# ================================================================================================================ GearTool (before GearView)
GT_PY = r'''
# ================================================================= 0.2.12 GearTool: tool power + Fortune by level (tools/gear_0_2_12_patch.py)
TL = {
    "TDBE": "com.hypixel.hytale.server.core.event.events.ecs.DamageBlockEvent",
    "TBTY": "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType",
    "TBGA": "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockGathering",
    "TBBD": "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockBreakingDropType",
}
for _k in TL:
    assert _k not in T, "0.2.12 token clashes: " + _k
T.update(TL)
for c, m in ((TL["TDBE"], "getItemInHand"), (TL["TDBE"], "getDamage"), (TL["TDBE"], "setDamage"), (TL["TDBE"], "getBlockType"),
             (TL["TDBE"], "isCancelled"), (TL["TBTY"], "getGathering"), (TL["TBTY"], "getId"), (TL["TBGA"], "getBreaking"),
             (TL["TBBD"], "getGatherType"), (IS, "getMetadata"), (IS, "getItemId"), (IS, "isEmpty")):
    B.probe(pool, c, m)
_dbe = pool.get(TL["TDBE"])
assert str(_dbe.getSuperclass().getName()).endswith("CancellableEcsEvent"), "DamageBlockEvent is no longer a CancellableEcsEvent"
assert str(_dbe.getDeclaredMethod("getItemInHand").getReturnType().getName()) == IS, "DamageBlockEvent.getItemInHand no longer returns an ItemStack"
gtool = mk("GearTool")
TOOL_CLASSES = [gtool]
F(gtool, "public static final String[] FAM_PRE = %s;" % jarr(TOOL_FAMS))
F(gtool, 'public static final String[] ROWKEY = new String[] { "mining", "foraging", "farming" };')
F(gtool, "public static final String[] TIER_W = %s;" % jarr([w for w, _t in TOOL_TIERS]))
F(gtool, "public static final int[] TIER_N = %s;" % jints([t for _w, t in TOOL_TIERS]))
F(gtool, 'public static final String SRC = "gear";')
# fix round (tools01fix, critic B1/A3): which blocks a tool's Fortune counts on, posted as only.<skill> next to dd.<skill> (SkyySkills 0.4.26
# matches the broken block's id like perk.<skill>.doubleDropOnly; "" = every block of that skill). Pickaxe = rock + ore, shovel = sand +
# gravel (the only Soil_ blocks with a Mining row); hatchet (Foraging = logs only already), hoe + sickle (crops) need none.
TOOL_ONLY = ["", "Rock_,Rubble_,Ore_", "Soil_", "", "", ""]
F(gtool, "public static final String[] ONLY = %s;" % jarr(TOOL_ONLY))
# fix round (critic C1): the tooltip shows the REAL hit count on a reference block (hits = the smallest n with n x damage >= 1.0, Tool-Levels-Spec
# 2.1 rows 3 + 12): each vanilla pickaxe / shovel / hatchet's own spec power for Rocks (stone) / Soils / Woods (a log), read from Assets.zip
TOOL_REF = {1: "Rocks", 2: "Soils", 3: "Woods"}
_TH = []
for _i in _TOOL_AZ_IDS:
    _f = [k + 1 for k, p in enumerate(TOOL_FAMS) if _i.startswith(p)][0]
    if _f not in TOOL_REF:
        continue
    _tl = az_get(_i, "Tool") or {}
    _pw = [float(sp.get("Power", 0)) for sp in _tl.get("Specs", []) if isinstance(sp, dict) and sp.get("GatherType") == TOOL_REF[_f]]
    if _pw and _pw[0] > 0.0:
        _TH.append((_i, _pw[0]))
assert len(_TH) >= 20 and dict(_TH).get("Tool_Hatchet_Copper") == 0.2 and dict(_TH).get("Tool_Hatchet_Iron") == 0.3, "tool reference powers: %s" % _TH[:5]
F(gtool, "public static final String[] HIT_IDS = %s;" % jarr([i for i, _p in _TH]))
F(gtool, "public static final double[] HIT_PW = new double[] { %s };" % ", ".join(repr(float(p)) for _i, p in _TH))
# UUID -> Object[] { ItemStack held (identity), Long at, double[] stats or null }
F(gtool, "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();")
# fix round 2 (engine critic LOW 1): players who disconnected (GearBye) -> held() posts nothing for them, so a world-thread tick that runs
# after forget() cannot put a stale "gear" source back; cleared by back() on PlayerReadyEvent (GearReady) and at shutdown
F(gtool, "public static final java.util.concurrent.ConcurrentHashMap GONE = new java.util.concurrent.ConcurrentHashMap();")
# counters: 0 hits made stronger, 1 hits left alone (no tool / other block / factor 1), 2 hits of an under-level tool, 3 posts, 4 removals
F(gtool, "public static final long[] N = new long[6];")
F(gtool, "public static boolean FAILED_ONCE = false;")
F(gtool, "public static volatile Object[] PP = null;")
F(gtool, "public static volatile String PSRC = null;")
F(gtool, "public static volatile Object[] HP = null;")
F(gtool, "public static volatile String HSRC = null;")
# 1 pickaxe, 2 shovel, 3 hatchet, 4 hoe, 5 sickle; 0 = not a gathering tool (Skyy* items and Bark Scrapers never)
M(gtool, r"""
public static int fam(String id) {
  if (id == null || !@PKG@.GearData.isTool(id)) return 0;
  for (int i = 0; i < FAM_PRE.length; i++) if (id.startsWith(FAM_PRE[i])) return i + 1;
  return 0;
}""")
M(gtool, r"""
public static int row(int f) {
  if (f == 1 || f == 2) return 0;
  if (f == 3) return 1;
  if (f == 4 || f == 5) return 2;
  return -1;
}""")
M(gtool, r"""
public static String skill(int f) {
  int r = row(f);
  if (r == 0) return "Mining";
  if (r == 1) return "Foraging";
  if (r == 2) return "Farming";
  return "";
}""")
# the material tier from the id's words after Tool_<Family>_ (unknown = 0)
M(gtool, r"""
public static int tier(String id) {
  if (id == null) return 0;
  String[] w = id.split("_");
  for (int i = 2; i < w.length; i++) {
    for (int j = 0; j < TIER_W.length; j++) if (TIER_W[j].equalsIgnoreCase(w[i])) return TIER_N[j];
  }
  return 0;
}""")
M(gtool, r"""
public static synchronized Object[] reP(String s) {
  Object[] p = @PKG@.GearCfg.curvePts(s);
  if (p == null) p = @PKG@.GearCfg.curvePts(@PKG@.GearCfg.TOOL_PICK_DEF);
  PP = p;
  PSRC = s;
  return p;
}""")
M(gtool, r"""
public static synchronized Object[] reH(String s) {
  Object[] p = @PKG@.GearCfg.curvePts(s);
  if (p == null) p = @PKG@.GearCfg.curvePts(@PKG@.GearCfg.TOOL_HATCH_DEF);
  HP = p;
  HSRC = s;
  return p;
}""")
# the power factor (1.0 = vanilla, never below): the family's curve at the level x (1 + matBonus % x tier); hoes / sickles 1.0
M(gtool, r"""
public static double power(int f, int lv, int t) {
  if (!@PKG@.GearCfg.PART_TOOLS || lv <= 0) return 1.0;
  Object[] p = null;
  if (f == 1 || f == 2) {
    String s = @PKG@.GearCfg.TOOL_PICK;
    p = PP;
    if (p == null || s != PSRC) p = reP(s);
  } else if (f == 3) {
    String s2 = @PKG@.GearCfg.TOOL_HATCH;
    p = HP;
    if (p == null || s2 != HSRC) p = reH(s2);
  } else return 1.0;
  double m = @PKG@.GearBase.eval(p, (double) lv) * (1.0 + @PKG@.GearCfg.TOOL_PMAT / 100.0 * (double) (t < 0 ? 0 : t));
  if (Double.isNaN(m) || m < 1.0) return 1.0;
  return m > 100.0 ? 100.0 : m;
}""")
# Fortune points (1 = +1 % extra drop chance), one decimal, capped at tool.fortune.cap
M(gtool, r"""
public static double fortune(int f, int lv, int t) {
  if (!@PKG@.GearCfg.PART_TOOLS || f <= 0 || lv <= 0) return 0.0;
  double per = (f == 4 || f == 5) ? @PKG@.GearCfg.TOOL_FFARM : @PKG@.GearCfg.TOOL_FPER;
  double v = per * (double) lv * (1.0 + @PKG@.GearCfg.TOOL_FMAT / 100.0 * (double) (t < 0 ? 0 : t));
  if (Double.isNaN(v) || !(v > 0.0)) return 0.0;
  if (v > @PKG@.GearCfg.TOOL_FCAP) v = @PKG@.GearCfg.TOOL_FCAP;
  return (double) Math.round(v * 10.0) / 10.0;
}""")
# int[] { need (the tool's level), eff (the level its stats use), active 1/0, have (-2 no SkyySkills, -1 not asked) }. A tool with a stored
# level needs that level; one without (made before 0.2) works at min(its level, your skill) - the 2026-10-03 lenient rule for old tools.
M(gtool, r"""
public static int[] gate(java.util.UUID u, int f, String id, @BD@ d) {
  int need = @PKG@.GearLevel.level(id, d);
  boolean stamped = @PKG@.GearLevel.stamped(d);
  if (!@PKG@.GearCfg.PART_GATE || u == null) return new int[] { need, need, 1, -1 };
  int h = @PKG@.GearGate.have(u, skill(f));
  if (h == -2) return new int[] { need, need, 1, -2 };
  if (h < 0) h = 0;
  int hf = @PKG@.GearLevel.floor(h);
  if (stamped) return new int[] { need, need, hf >= need ? 1 : 0, h };
  int eff = need < hf ? need : hf;
  return new int[] { need, eff, eff >= 1 ? 1 : 0, h };
}""")
# double[] { fam, row, eff level, active 1/0, power factor, Fortune, need, tier } for a stack; null = not a gathering tool
M(gtool, r"""
public static double[] stats(java.util.UUID u, @IS@ s) {
  if (s == null || s.isEmpty()) return null;
  String id = s.getItemId();
  int f = fam(id);
  if (f == 0) return null;
  @BD@ d = null;
  try { d = @PKG@.GearData.gearDoc(s.getMetadata()); } catch (Throwable t0) { d = null; }
  int[] g = gate(u, f, id, d);
  int t = tier(id);
  boolean on = g[2] != 0 && @PKG@.GearCfg.PART_TOOLS;
  double pw = on ? power(f, g[1], t) : 1.0;
  double fo = on ? fortune(f, g[1], t) : 0.0;
  return new double[] { (double) f, (double) row(f), (double) g[1], on ? 1.0 : 0.0, pw, fo, (double) g[0], (double) t };
}""")
# which blocks a family's power works on: pickaxe = rock + ore (SkyyTrees' Heavy Pick rule), shovel = Soils, hatchet = Woods only
M(gtool, r"""
public static boolean onType(int f, @TBTY@ bt) {
  if (bt == null) return false;
  String gt = null;
  try {
    @TBGA@ g = bt.getGathering();
    @TBBD@ br = g == null ? null : g.getBreaking();
    gt = br == null ? null : br.getGatherType();
  } catch (Throwable t) { gt = null; }
  String id = null;
  try { id = bt.getId(); } catch (Throwable t2) { id = null; }
  if (f == 3) return "Woods".equals(gt);
  if (f == 2) return "Soils".equals(gt);
  if (f == 1) return (id != null && id.startsWith("Ore_")) || "Rocks".equals(gt) || "VolcanicRocks".equals(gt) || (gt != null && gt.startsWith("Ore"));
  return false;
}""")
# skill:bonus:<uuid> -> ConcurrentHashMap source -> unmodifiable Map (the SkyyTrees postBonus shape); source "gear" = the held tool's
# dd.<skill> = Fortune / 100. row < 0, no Fortune, or profile:busy -> our source is removed (other sources stay)
M(gtool, r"""
public static void post(java.util.UUID u, int row, double fo, String only) {
  if (u == null) return;
  try {
    java.util.Map b = @PKG@.Gear.bridge();
    String key = "skill:bonus:" + u.toString();
    Object o = b.get(key);
    if (row < 0 || row > 2 || !(fo > 0.0) || @PKG@.Gear.busy(u)) {
      if (o instanceof java.util.Map && ((java.util.Map) o).remove(SRC) != null) N[4] = N[4] + 1L;
      return;
    }
    java.util.HashMap m = new java.util.HashMap();
    m.put("dd." + ROWKEY[row], Double.valueOf(fo / 100.0));
    if (only != null && only.length() > 0) m.put("only." + ROWKEY[row], only);   // fix round: the blocks this tool's Fortune counts on
    java.util.Map src = null;
    if (o instanceof java.util.Map) src = (java.util.Map) o;
    else {
      java.util.concurrent.ConcurrentHashMap n = new java.util.concurrent.ConcurrentHashMap();
      Object prev = b.putIfAbsent(key, n);
      src = prev instanceof java.util.Map ? (java.util.Map) prev : n;
    }
    if (m.equals(src.get(SRC))) return;
    src.put(SRC, java.util.Collections.unmodifiableMap(m));
    N[3] = N[3] + 1L;
  } catch (Throwable t) { @PKG@.Gear.warnOnce("toolpost", "tool Fortune bridge post failed: " + t); }
}""")
# the held stack (GearHandSys every tick, GearToolHitSys every block hit): recomputed when the stack object changes or after 1 s (a skill
# level-up, a profile switch, a Server Setup change), then posted. Returns the stats (null = not a gathering tool).
M(gtool, r"""
public static double[] held(java.util.UUID u, @IS@ s) {
  if (u == null || GONE.containsKey(u)) return null;
  long now = System.currentTimeMillis();
  Object[] e = (Object[]) LAST.get(u);
  if (e != null && e[0] == s) {
    long at = ((Long) e[1]).longValue();
    if (now >= at && now - at < 1000L) return (double[]) e[2];
  }
  double[] st = stats(u, s);
  LAST.put(u, new Object[] { s, Long.valueOf(now), st });
  if (st == null || st[3] == 0.0) post(u, -1, 0.0, null);
  else post(u, (int) st[1], st[5], ONLY[(int) st[0]]);
  return st;
}""")
# a block hit (DamageBlockEvent, synchronous): the new damage. Under-level, a non-tool, a block the family has no power on, or a factor of
# 1 -> unchanged (vanilla). Weapon axes are not tools (fam 0), so their hits are never touched.
M(gtool, r"""
public static float onDamage(java.util.UUID u, @IS@ s, @TBTY@ bt, float dmg) {
  try {
    double[] st = held(u, s);
    if (st == null) { N[1] = N[1] + 1L; return dmg; }
    if (st[3] == 0.0) { N[2] = N[2] + 1L; return dmg; }
    if (!(st[4] > 1.0) || !(dmg > 0.0f) || !onType((int) st[0], bt)) { N[1] = N[1] + 1L; return dmg; }
    N[0] = N[0] + 1L;
    return (float) ((double) dmg * st[4]);
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.Gear.warn("tool power failed (logged once): " + t); }
    return dmg;
  }
}""")
M(gtool, r"""
public static void forget(java.util.UUID u) {
  if (u == null) return;
  GONE.put(u, Long.valueOf(System.currentTimeMillis()));
  LAST.remove(u);
  post(u, -1, 0.0, null);
}""")
M(gtool, r"""
public static void back(java.util.UUID u) {
  if (u != null) GONE.remove(u);
}""")
M(gtool, r"""
public static void clearAll() {
  Object[] ks = LAST.keySet().toArray();
  for (int i = 0; i < ks.length; i++) if (ks[i] instanceof java.util.UUID) post((java.util.UUID) ks[i], -1, 0.0, null);
  LAST.clear();
  GONE.clear();
}""")
# fix round: a vanilla tool's own power on its reference block (0 = unknown id - a modded tool shows no hit count)
M(gtool, r"""
public static double refPower(String id) {
  if (id == null) return 0.0;
  for (int i = 0; i < HIT_IDS.length; i++) if (HIT_IDS[i].equals(id)) return HIT_PW[i];
  return 0.0;
}""")
# hits to break a block of health 1.0 with power p x factor m (the float damage the engine subtracts); -1 = no power
M(gtool, r"""
public static int hits(double p, double m) {
  if (!(p > 0.0) || !(m > 0.0)) return -1;
  double d = (double) ((float) (p * m));
  if (!(d > 0.0)) return -1;
  int n = (int) Math.ceil(1.0 / d - 0.000001);
  return n < 1 ? 1 : n;
}""")
# tooltip lines under the gate line (GearView.lines, tools only); owner null = neutral (no under-level line). Fix round (critics C1 + C6):
# short lines, the power line shows the real hits on a reference block next to vanilla, Fortune names the blocks it really counts on.
M(gtool, r"""
public static void lines(java.util.UUID owner, String id, @BD@ d, java.util.ArrayList txt, java.util.ArrayList col) {
  int f = fam(id);
  if (f == 0 || !@PKG@.GearCfg.PART_TOOLS) return;
  int t = tier(id);
  int[] g = gate(owner, f, id, d);
  int lv = g[0];
  String sk = skill(f);
  if (f <= 3) {
    double pw = power(f, lv, t);
    String pct = (f == 3 ? "Chopping Power" : "Mining Power") + " +" + (int) Math.round((pw - 1.0) * 100.0) + "%";
    double rp = refPower(id);
    int h = hits(rp, pw);
    int v = hits(rp, 1.0);
    String blk = f == 3 ? "log" : (f == 2 ? "soil block" : "stone");
    if (h > 0 && v > 0) txt.add(pct + ": " + h + (h == 1 ? " hit" : " hits") + " per " + blk + " (vanilla " + v + ")");
    else txt.add(pct + " on " + (f == 3 ? "logs" : (f == 2 ? "soil" : "rock and ore")));
    col.add(null);
  }
  double fo = fortune(f, lv, t);
  String what = f == 3 ? "log" : (f == 2 ? "sand / gravel" : (f == 1 ? "rock / ore" : "crop"));
  txt.add(sk + " Fortune +" + @PKG@.Gear.fnum(fo) + " (" + @PKG@.Gear.fnum(fo) + "% extra " + what + " chance)");
  col.add(null);
  if (owner != null && g[2] == 0) {
    txt.add("No bonus until " + sk + " " + lv);
    col.add(@PKG@.GearDefs.C_BAD);
  }
  if (f == 3) {
    txt.add("Tree Feller unlocks in the Foraging tree");   // fix round 2: the SkyyTrees perk, not a hatchet stat
    col.add(@PKG@.GearDefs.C_GRAY);
  }
}""")
M(gtool, r"""
public static String statusText() {
  if (!@PKG@.GearCfg.PART_TOOLS) return "tool stats OFF (part.tools)";
  return "tool stats on (Mining / Chopping Power by tool level, Fortune up to " + @PKG@.Gear.fnum(@PKG@.GearCfg.TOOL_FCAP) + " through skill:bonus source gear; under-level tools work like plain tools)";
}""")
M(gtool, r"""
public static String counters() {
  return "tool hits stronger " + N[0] + ", left alone " + N[1] + ", under-level " + N[2] + "; Fortune posts " + N[3] + ", removals " + N[4] + "; players tracked " + LAST.size();
}""")

'''
rep('''# ================================================================= GearView (spec 6): tooltip, plain lines, sigs
''', GT_PY + '''# ================================================================= GearView (spec 6): tooltip, plain lines, sigs
''')

# ================================================================================================================ the tooltip
rep('''  if (!@PKG@.GearDefs.enforcedKind(kind)) {
    if (gate.length() == 0) return new Object[] { "", null, Boolean.FALSE, "" };
    return new Object[] { lv + " - Requires " + gate + " " + need + " (coming later)", @PKG@.GearDefs.C_GRAY, Boolean.FALSE, gate };
  }''', '''  if (!@PKG@.GearDefs.enforcedKind(kind)) {
    if (gate.length() == 0) return new Object[] { "", null, Boolean.FALSE, "" };
    // 0.2.12: a gathering tool's requirement is real for its BONUS (never blocks): green when met, red + "(you: M)" when too low
    if (@PKG@.GearCfg.PART_TOOLS && @PKG@.GearTool.fam(id) > 0) {
      Object[] tc = @PKG@.GearGate.check(owner, id, d, need);
      String tl = (String) tc[1];
      String treq = lv + " - Requires " + (tl.length() > 0 ? tl : gate) + " " + need;
      int tst = ((Integer) tc[5]).intValue();
      if (tst != 0) return new Object[] { treq, @PKG@.GearDefs.C_GRAY, Boolean.FALSE, gate };
      if (((Boolean) tc[0]).booleanValue()) return new Object[] { treq, @PKG@.GearDefs.C_OK, Boolean.FALSE, gate };
      int th = ((Integer) tc[3]).intValue();
      return new Object[] { treq + " (you: " + (th < 0 ? 0 : th) + ")", @PKG@.GearDefs.C_BAD, Boolean.FALSE, gate };
    }
    return new Object[] { lv + " - Requires " + gate + " " + need, @PKG@.GearDefs.C_GRAY, Boolean.FALSE, gate };
  }''')
rep('''  statLines(id, d, txt, col);
  add(txt, col, "", null);
  add(txt, col, @PKG@.GearDefs.R_NAME[r].toUpperCase() + " " + slotWord(id), hex);''', '''  statLines(id, d, txt, col);
  if (slot == 3) @PKG@.GearTool.lines(owner, id, d, txt, col);   // 0.2.12: tool power + Fortune by level
  add(txt, col, "", null);
  add(txt, col, @PKG@.GearDefs.R_NAME[r].toUpperCase() + " " + slotWord(id), hex);''')
rep('''  if (slot == 3 && gt.indexOf("coming later") < 0) add(txt, col, "(coming later: gathering gear)", @PKG@.GearDefs.C_GRAY);
''', '')

# ================================================================================================================ the block-hit system
rep('''PLAYER_Q = "(@QRY@) @PLA@.getComponentType()"
''', '''PLAYER_Q = "(@QRY@) @PLA@.getComponentType()"
# 0.2.12: GearToolHitSys = the DamageBlockEvent hook SkyyTrees' TreeDmgSys (Heavy Hatchet / Heavy Pick) uses: multiplies the hit's damage
# (BlockHarvestUtils.damageSingleBlock re-reads it after the event); a cancelled hit (SkyyIslands' guard) is left alone; creative never fires it
gtoolh = mk("GearToolHitSys", EES)
TOOL_CLASSES.append(gtoolh)
event_system(gtoolh, "GearToolHitSys", TL["TDBE"], PLAYER_Q, r"""
    if (!(ev instanceof @TDBE@)) return;
    @TDBE@ e = (@TDBE@) ev;
    if (e.isCancelled()) return;
    @PR@ pr = (@PR@) chunk.getComponent(idx, @PR@.getComponentType());
    if (pr == null) return;
    float d0 = e.getDamage();
    float d1 = @PKG@.GearTool.onDamage(pr.getUuid(), e.getItemInHand(), e.getBlockType(), d0);
    if (d1 != d0) e.setDamage(d1);""")
''')
rep('''                                                        "GearSigSlotSys", "GearSigInvSys")))''',
    '''                                                        "GearSigSlotSys", "GearSigInvSys",
                                                        # 0.2.12 tool power (DamageBlockEvent)
                                                        "GearToolHitSys")))''')
# the held tool posts its Fortune (every tick a cheap identity compare; recomputed on a change or after 1 s)
rep('''    @PKG@.GearSpeed.tick(cb, r, pr.getUuid(), held);
  } catch (Throwable t) { @PKG@.Gear.warnOnce("handsys", "hand snapshot failed: " + t); }''',
    '''    @PKG@.GearSpeed.tick(cb, r, pr.getUuid(), held);
    // 0.2.12: the held tool's Fortune on the bridge (skill:bonus:<uuid>["gear"])
    @PKG@.GearTool.held(pr.getUuid(), held);
  } catch (Throwable t) { @PKG@.Gear.warnOnce("handsys", "hand snapshot failed: " + t); }''')
rep('''    @PKG@.GearCharged.forget(u);
    @PKG@.Gear.bridge().remove("gear:stats:" + u);
  } catch (Throwable t) { }''', '''    @PKG@.GearCharged.forget(u);
    @PKG@.Gear.bridge().remove("gear:stats:" + u);
    @PKG@.GearTool.forget(u);   // 0.2.12: our skill:bonus source
  } catch (Throwable t) { }''')
# fix round 2: a player who comes back (join / world switch) gets tool Fortune posts again (GearTool.GONE)
rep('''    @PKG@.GearChestOpen.seen(pr.getUuid());
''', '''    @PKG@.GearChestOpen.seen(pr.getUuid());
    @PKG@.GearTool.back(pr.getUuid());   // 0.2.12 fix round 2
''')
rep('''  try { @PKG@.Gear.bridge().remove("gear:fn:box"); } catch (Throwable t4) { }
''', '''  try { @PKG@.Gear.bridge().remove("gear:fn:box"); } catch (Throwable t4) { }
  try { @PKG@.GearTool.clearAll(); } catch (Throwable t5) { }   // 0.2.12: our skill:bonus sources
''')
rep('''+ @PKG@.GearLoot.statusText() + "; Reforge level up "''', '''+ @PKG@.GearLoot.statusText() + "; " + @PKG@.GearTool.statusText() + "; Reforge level up "''')
rep('''CRIT_CLASSES + [gspd] + SIG_CLASSES + LOOT_CLASSES
''', '''CRIT_CLASSES + [gspd] + SIG_CLASSES + LOOT_CLASSES + TOOL_CLASSES
''')
rep('''      % (", ".join(str(c.getName()).rsplit(".", 1)[1] for c in LOOT_CLASSES), len(LOOT_POOL), len(LOOT_TYPES), len(LT_ROWK)))
''', '''      % (", ".join(str(c.getName()).rsplit(".", 1)[1] for c in LOOT_CLASSES), len(LOOT_POOL), len(LOOT_TYPES), len(LT_ROWK)))
print("0.2.12: tools do something - %s; %d tool rows (Server Setup -> Gear -> Tools); %d vanilla tools with a material tier; %s"
      % (", ".join(str(c.getName()).rsplit(".", 1)[1] for c in TOOL_CLASSES), len(TL_ROWK), len(_TOOL_AZ_IDS), "; ".join(TOOL_TABLE)))
''')

# ================================================================================================================ write
assert s.count("registerSystem(") == SYS0 and s.count("registerCommand(") == CMD0, \
    "0.2.12 registers GearToolHitSys through the _reg list (no new registerSystem text, no command)"
assert "(coming later)\", @PKG@.GearDefs.C_GRAY, Boolean.FALSE, gate" not in s and 'add(txt, col, "(coming later: gathering gear)"' not in s
out = s.replace(LF, NL)
with open(DST, "w", encoding="utf8", newline="") as f:
    f.write(out)
print("wrote %s (%d lines)" % (os.path.relpath(DST, ROOT), out.count(NL) + 1))
