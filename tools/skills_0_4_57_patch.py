"""Derive SkyySkills/build_skyyskills_0.4.57.py from the GENERATED SkyySkills 0.4.56 (build_skyyskills_0.4.56.py = the tools/deploy_set.py SET
pin; 0.4.56 came from 0.4.55 by tools/skills_0_4_56_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). rep(old, new) with asserted single anchors; at the end every change is undone on a copy and compared with
0.4.56 (nothing else changed); 0.4.56 stays untouched, its line endings are kept (tools/soundpass_gen.Patch).
Run:  python tools/skills_0_4_57_patch.py   then   python SkyySkills/build_skyyskills_0.4.57.py   (never --deploy)
      then  python SkyySkills/test_skyyskills_0.4.57.py
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G
import balance_model as BM   # the P3 numbers (research/Balance-P3-XP-Spec.md + A:197 levels.scale) - ONE source for the model and this build

assert BM.LEVELS_SCALE == 120 and BM.P3_BASE[:3] == [275, 625, 1050] and len(BM.P3_LEVELS) == 100
assert [round(f, 2) for f in BM.F_T] == [1.0, 2.11, 3.6, 4.91, 7.43, 10.04, 12.15, 15.95, 19.68, 22.59, 27.67, 32.52, 36.23, 42.59, 48.56, 53.07]

NOTE = '''0.4.57 (2026-10-20) = BALANCE PASS P3 - XP (research/Balance-P3-XP-Spec.md; with SkyyCooking 0.1.15, SkyyExploration 0.3.2,
  SkyyCollections 0.2.30, SkyyFishing 0.1.12 - deploy together). Skyy (2026-10-18): "instead of starting fast and slowing, lets try to balance
  the xp gain, and how much more each level costs to make all skills, and your class level pretty close to the same rate" + popup 2026-10-20
  (A:197) "Middle: Lv 50 at ~33 h"; every other spec question takes its recommended default.
  1. ONE CURVE: levels= = R(1100 x f(L) x s(L)) (spec section 2, asserted) x levels.scale 120 % (tools/balance_model.py puts class Lv 50 at
     33.1 h with it; 130 % = 35.9 h) - SkillDefs.DEFAULT_PER = the 100 % base (the curve-size row's reference), DEFAULT_RUN = the 120 % list
     (a fresh file / a file without levels=). levels.class.sameAsOthers default true (the class skills level on levels= too); the own
     lists levels.skill.Mining / Farming leave the defaults (the table stays for admins); gather.boost.skills default empty (the quick start
     is in s(L)).
  2. XP PER ACTION x THE TIER FACTOR F(T) (spec 3.1-3.8): ores (50 x F, Silver / Gold / Prisma at their spawn tier), Rock_Crystal_ 40,
     Rock_Gem_ 200, every trunk species by its tier_tags tier (33 x F; new block rows for the species that had none), crops (38 x F), herbs,
     Berry / Apple, ranching.items x10, alchemy.tierXp 1500 / 7400 / 18200 / 33900 / 54400 + every alchemy.xp row by its bench tier ratio
     (Morph 7400 as the spec lists it; the Popberry bomb stays 10 - the craft-loop guard), Smithing bars = their ore, alloys by tier,
     Enchanted alloys = 100 bars x the bar XP x 0.5 (the 0.4.54 rule), Potion_Empty 20, Acrobatics x1.5 (sprint 0.4, run 0.25, walk 0.08,
     jump 3, dodge 5, fall 15, perfect dodge 8).
  3. P3Xp (new class) in the XP gain paths (gain4's earned XP, felled logs, ranching, the party share, BridgeXp grants / crafts), after the
     xp multiplier and before the tree / VP bonuses: xp.skillMult.<Skill> (table, Class = every class skill), the CATCH-UP (catchup.*: a
     catchup.skills slot more than catchup.freeLevels levels behind the active class skill +catchup.perLevel % a level, at most catchup.max %),
     the PAST-LIFE BOOST (rebirth.pastLifeXp entry n while the slot is below the last run's cap = runBase + raise x (n-1)/n; rebirth 6+ at the
     100 clamp: every level), the OWN-LEVEL FACTOR (xp.levelFactor.skills Acrobatics,Fishing: x f(own level) on own XP - for Fishing the
     SkyyFishing catches, skill:fn:addxp source "fishing"). Exploration never. Stats page: "Catch-up XP +30 % (8 levels behind your class)",
     "Past-life XP x1.2 below level 50", the level factor and a server multiplier.
  4. SKYYREBIRTH 0.4.0's FOR SKYYSKILLS list: (1) SkillBonus.xpBonus takes the "rebirth" source's xp.<skill> for every boostable non-class
     skill even when bridge.bonus.xpSkills omits it (Exploration excluded); a SkyyFishing catch counts as earned XP (so Hand Echo: Fishing
     works; Collections / Quests Fishing grants stay exact); (2) COMBAT ECHO on kill XP: x (1 + (combatxp - allxp) / 100) from rebirth:fn:stat
     (RbStat, the 1 s cache), for the killer and each party member's share; the "rebirth" source's xp.combat no longer adds to every class
     XP (SkillV3.classXp - it was Combat Echo counted on all class XP); (3) the facts carry arm.acrobatics. rebirth:reads:SkyySkills =
     "xp.combat,xp.alchemy,xp.smithing,xp.fishing,xp.acrobatics" (put at setup, our value removed at shutdown).
  5. ONE-TIME MIGRATIONS (PROJECT-RULES 4), setup() right after Xp56Mig, BEFORE SkillCfg.load, in this order:
     CurveP3Mig (saved XP, KEEP LEVELS, spec 6.2): reads the OLD tables from xp.properties as it is (P3Mig.plan tells the new ones), copies
       players/ + level-floors.properties to history/curve-p3/<stamp>/ and reads every copy back (a failure = WARN, nothing changed, no
       config update, retried next start), maps each changed slot: level Lo + progress p kept (new = newCum(Lo) + round(p x newNeed(Lo)));
       XP at / past the profile's cap keeps its ratio to the cap total (the cap from rebirth:fn:cap; unknown -> the level mapping);
       only the <Slot>= values change (bytes, order, line endings, .paid kept), each file atomic; floors' "XP then" -> newCum(level);
       Skyy_SkyySkills/curve-p3.properties (done.<pkey> per file, complete=) = the run-once marker; one line in curve-p3.log with the Undo.
     P3Mig (xp.properties, spec 6.1; Nc53Mig's machinery + line drops + one appended block): every P3 key whose LAST entry is a one-line
       entry holding exactly the 0.4.56 default -> the new value (the own lists: the line removed); an admin's value kept (INFO) - its slot's
       saved XP is not moved; the P3 block (catch-up / past-life / level-factor rows + the trunk rows the file lacks + the marker) appended
       once; config-history copy first (verified), one config-changes.log row per change (Undo), Properties check, bytes / line endings kept.
  ROLLBACK to 0.4.56: restore history/curve-p3/<stamp>/ (players/ + rebirth/ + level-floors.properties) with the server stopped FIRST, then
  Server Setup -> Changes -> Undo the P3 rows (or restore the config-history copy), and delete Skyy_SkyySkills/curve-p3.properties - 0.4.56 on
  the new XP with the old lists shows other levels. (0.4.57 notices a full put-back made with no play in between and moves again by itself.)
'''

P = G.Patch(os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.56.py"), os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.57.py"))
assert P.has('VERSION = "0.4.56"') and P.has("Xp56Mig"), "not the generated SkyySkills 0.4.56 script"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")

P.rep('''"""SkyySkills 0.4.56 - build script (derived from the generated 0.4.55 by tools/skills_0_4_56_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.57 - build script (derived from the generated 0.4.56 by tools/skills_0_4_57_patch.py - edit the patch, not this file;
''' + NOTE + '''  CHECKED: SkyySkills/test_skyyskills_0.4.57.py.
0.4.56 was derived from the generated 0.4.55 by tools/skills_0_4_56_patch.py;
''')
P.rep('VERSION = "0.4.56"', 'VERSION = "0.4.57"')

# ---------------------------------------------------------------------------------------------------- 1. the P3 level list (Python)
P.rep('''CLASS_LEVELS_TEXT = ",".join(str(x) for x in CLASS_LEVELS)
''', '''CLASS_LEVELS_TEXT = ",".join(str(x) for x in CLASS_LEVELS)
# 0.4.57 BALANCE P3 (research/Balance-P3-XP-Spec.md section 2; tools/balance_model.py): ONE list for the class and every skill. P3_BASE = the
# spec's levels= (100 % = the curve-size row's reference, SkillDefs.DEFAULT_PER); P3_LEVELS = P3_BASE x levels.scale P3_SCALE % (Skyy popup
# 2026-10-20 A:197 "Middle: Lv 50 at ~33 h"; the model puts class Lv 50 at 33.1 h) = what a fresh file / a file without levels= uses
# (SkillDefs.DEFAULT_RUN). LEVELS (the 0.4.3 - 0.4.56 list) stays the "old default" of the P3 updates (P3Mig, CurveP3Mig: DEFAULT_056).
from fractions import Fraction as _F57
def _p3f(L): return 1 + _F57(13, 100) * (L - 1) + _F57(4, 1000) * (L - 1) ** 2
def _p3s(L): return _F57(L, 4) if L <= 4 else (_F57(1) if L <= 60 else 1 + _F57(18, 1000) * (L - 60))
def _p3r(x):
    st = 5 if x < 1000 else (50 if x < 10000 else 100)
    return int(round(float(x) / st)) * st   # the spec's rounding (Python round, half to even: 1925 -> 1900)
P3_BASE = @@BASE@@
assert P3_BASE == [_p3r(1100 * _p3f(_L) * _p3s(_L)) for _L in range(1, 101)], "0.4.57: the spec section 2 list"
assert (sum(P3_BASE[:20]), sum(P3_BASE[:50]), sum(P3_BASE)) == (58150, 406200, 2944700), "0.4.57: the spec section 2 totals"
P3_SCALE = @@SCALE@@
import math as _m57
P3_LEVELS = [int(_m57.floor(_x * (P3_SCALE / 100.0) + 0.5)) for _x in P3_BASE]   # = SkillKit.scaledTo(base, 120): Math.round(x x 1.2)
assert P3_LEVELS == @@LEVELS@@, "0.4.57: tools/balance_model.py's P3_LEVELS"
assert round(sum(P3_LEVELS) * 100.0 / sum(P3_BASE)) == P3_SCALE   # SkillKit.pctOf -> the curve-size row reads 120
P3_LEVELS_TEXT = ",".join(str(_x) for _x in P3_LEVELS)
LEVELS_056_TEXT = ",".join(str(_x) for _x in LEVELS)
'''.replace("@@BASE@@", repr(BM.P3_BASE)).replace("@@SCALE@@", str(BM.LEVELS_SCALE)).replace("@@LEVELS@@", repr(BM.P3_LEVELS)))
assert P.has("\nimport math\n") or P.has("import math,") or P.has("import os, sys, json, math") or True

# DEFAULT_PER = the 100 % base; DEFAULT_RUN = the 120 % list; DEFAULT_056 = the old default (P3 updates)
P.rep('''defs.addField(CtField.make("public static final long[] DEFAULT_PER = new long[] { %s };" % ", ".join("%dL" % x for x in LEVELS), defs))
''', '''defs.addField(CtField.make("public static final long[] DEFAULT_PER = new long[] { %s };" % ", ".join("%dL" % x for x in P3_BASE), defs))   # 0.4.57: the P3 base = 100 %
defs.addField(CtField.make("public static final long[] DEFAULT_RUN = new long[] { %s };" % ", ".join("%dL" % x for x in P3_LEVELS), defs))   # 0.4.57: the default list (levels.scale 120 %)
defs.addField(CtField.make("public static final long[] DEFAULT_056 = new long[] { %s };" % ", ".join("%dL" % x for x in LEVELS), defs))   # 0.4.57: the 0.4.3 - 0.4.56 default (the P3 updates)
''')
P.rep('''cfg.addField(CtField.make('public static final String NEW_LEVELS = "%s";' % ",".join(str(x) for x in LEVELS), cfg))''',
      '''cfg.addField(CtField.make('public static final String NEW_LEVELS = "%s";' % P3_LEVELS_TEXT, cfg))   # 0.4.57: the 0.1/0.2 50-level default -> the P3 list''')
P.rep('''    {PKG}.SkillDefs.setTable({PKG}.SkillDefs.DEFAULT_PER);
    java.util.HashMap ex = new java.util.HashMap();''', '''    {PKG}.SkillDefs.setTable({PKG}.SkillDefs.DEFAULT_RUN);   // 0.4.57: no / a bad levels= line = the P3 list (levels.scale 120 %)
    java.util.HashMap ex = new java.util.HashMap();''')
P.rep('''    {PKG}.SkillDefs.setClassTable(cper, bool(p, "levels.class.sameAsOthers", false));''',
      '''    {PKG}.SkillDefs.setClassTable(cper, bool(p, "levels.class.sameAsOthers", true));   // 0.4.57: default true (P3 one curve)''')
P.rep('''  if (l == null) l = c ? {PKG}.SkillDefs.DEFAULT_CPER : {PKG}.SkillDefs.DEFAULT_PER;''',
      '''  if (l == null) l = c ? {PKG}.SkillDefs.DEFAULT_CPER : {PKG}.SkillDefs.DEFAULT_RUN;   // 0.4.57: no levels= line = the P3 list''')
P.rep('''LEVELS_TEXT = ",".join(str(x) for x in LEVELS)
CFG_CATS''', '''LEVELS_TEXT = P3_LEVELS_TEXT   # 0.4.57: the P3 list (was the 0.4.3 - 0.4.56 levels=)
CFG_CATS''')

# the class curve block (appended to a pre-0.4.12 file): the switch now on
P.rep('''CURVE_L.append("levels.class.sameAsOthers=false")
L.append("")''', '''CURVE_L.append("levels.class.sameAsOthers=true")   # 0.4.57 (Balance P3): one curve for the class and every skill
L.append("")''')
P.rep('''assert [_ln for _ln in CURVE_L if not _ln.startswith("#")] == ["levels.class=" + CLASS_LEVELS_TEXT, "levels.class.sameAsOthers=false"]''',
      '''assert [_ln for _ln in CURVE_L if not _ln.startswith("#")] == ["levels.class=" + CLASS_LEVELS_TEXT, "levels.class.sameAsOthers=true"]''')
P.rep('''assert CURVE_DEFAULTS.count("\\nlevels.class.sameAsOthers=false\\n") == 1   # SkillCfg.ensureCurve drops that line when the file has the key''',
      '''assert CURVE_DEFAULTS.count("\\nlevels.class.sameAsOthers=true\\n") == 1   # SkillCfg.ensureCurve drops that line when the file has the key (0.4.57: true)''')
P.rep('''  if (p.getProperty("levels.class.sameAsOthers") != null) b = b.replace("\\\\nlevels.class.sameAsOthers=false\\\\n", "\\\\n");''',
      '''  if (p.getProperty("levels.class.sameAsOthers") != null) b = b.replace("\\\\nlevels.class.sameAsOthers=true\\\\n", "\\\\n");   // 0.4.57: the block says true''')

# gathering pace: no default skills (the quick start is in the curve now)
P.rep('''gpc.addField(CtField.make('public static final String DEFAULT_SKILLS = "Foraging,Farming";', gpc))   # 0.4.16: Mining has its own level list''',
      '''gpc.addField(CtField.make('public static final String DEFAULT_SKILLS = "";', gpc))   # 0.4.57 (Balance P3): none - the quick start is in the level list (0.4.16: Foraging,Farming)''')
P.rep('''for _d in ("public static volatile boolean[] SLOTS = new boolean[] { false, true, true };", 'public static volatile String TEXT = "Foraging,Farming";',''',
      '''for _d in ("public static volatile boolean[] SLOTS = new boolean[] { false, false, false };", 'public static volatile String TEXT = "";',   # 0.4.57''')

# ---------------------------------------------------------------------------------------------------- 2. the P3 data + the fresh default file
P3DATA = r'''
# ================= 0.4.57 BALANCE P3 - the XP rows, the P3 update plan and the fresh default file (tools/skills_0_4_57_patch.py) =================
# F(T) = f(band start of tier T) as the spec prints it (2 decimals; section 3); xp = base x F(T) rounded to 5 below 1,000, else 50 (Python round)
import tier_tags as _TT57
P3_FT = [1.0, 2.11, 3.6, 4.91, 7.43, 10.04, 12.15, 15.95, 19.68, 22.59, 27.67, 32.52, 36.23, 42.59, 48.56, 53.07]
assert P3_FT == [round(float(_p3f(_b)), 2) for _b in (1, 8, 15, 20, 28, 35, 40, 48, 55, 60, 68, 75, 80, 88, 95, 100)]
def p3_xp(base, t):
    x = base * P3_FT[t - 1]
    return int(round(x / 5.0)) * 5 if x < 1000 else int(round(x / 50.0)) * 50
# 3.1 Mining (base 50): tier_tags metal tiers; Silver / Gold / Prisma are untagged -> the tier where they spawn (spec GUESS)
P3_ORE_T = dict((_m, _TT57.metal_tier(_m)) for _m in ("Copper", "Iron", "Thorium", "Lead", "Cobalt", "Chromium", "Adamantite", "Slag", "Mithril",
                                                     "Titanium", "Onyxium"))
P3_ORE_T.update({"Silver": 3, "Gold": 5, "Prisma": 15})
P3_ORE = dict((_m, p3_xp(50, _t)) for _m, _t in P3_ORE_T.items())
assert P3_ORE == {"Copper": 50, "Iron": 105, "Silver": 180, "Thorium": 245, "Lead": 370, "Gold": 370, "Cobalt": 610, "Chromium": 800,
                  "Adamantite": 1150, "Slag": 1400, "Mithril": 1800, "Titanium": 2150, "Prisma": 2450, "Onyxium": 2650}, P3_ORE
P3_LOG = [p3_xp(33, _t) for _t in range(1, 16)]
assert P3_LOG == [35, 70, 120, 160, 245, 330, 400, 525, 650, 745, 915, 1050, 1200, 1400, 1600], P3_LOG
P3_CROP_T = dict((_c, _i + 1) for _i, _c in enumerate(_TT57.CROP_LADDER))
P3_CROP = dict((_c, p3_xp(38, _t)) for _c, _t in P3_CROP_T.items())
assert [P3_CROP[_c] for _c in _TT57.CROP_LADDER] == [40, 80, 135, 185, 280, 380, 460, 605, 750, 860, 1050, 1250, 1400, 1600, 1850]
# (key, old 0.4.56 default(s) '|' separated, new value or None = the line removed, change-log row key)
P3_KEYS = []
def _p3k(k, o, n, row=None):
    P3_KEYS.append((k, o, n, row or k))
_p3k("levels", LEVELS_056_TEXT, P3_LEVELS_TEXT)
_p3k("levels.class.sameAsOthers", "false", "true")
_p3k("levels.skill.Mining", ",".join(str(_x) for _x in MINING_PER), None, "levels.skill[Mining]")
_p3k("levels.skill.Farming", FARM_LIST, None, "levels.skill[Farming]")
_p3k("gather.boost.skills", "Foraging,Farming|Foraging, Farming", "")
_p3k("prefix.Ore_", "Mining:5", "Mining:50", "prefix[Ore_]")
for _ore, _old in (("Copper", 5), ("Iron", 8), ("Silver", 10), ("Gold", 12), ("Cobalt", 15), ("Thorium", 18), ("Mithril", 25), ("Adamantite", 30),
                   ("Onyxium", 40), ("Prisma", 50), ("Lead", 18), ("Chromium", 15), ("Slag", 30), ("Titanium", 25)):
    _p3k("prefix.Ore_" + _ore, "Mining:%d" % _old, "Mining:%d" % P3_ORE[_ore], "prefix[Ore_%s]" % _ore)
_p3k("prefix.Rock_Crystal_", "Mining:8", "Mining:40", "prefix[Rock_Crystal_]")
_p3k("prefix.Rock_Gem_", "Mining:40", "Mining:200", "prefix[Rock_Gem_]")
_p3k("suffix._Trunk", "Foraging:6", "Foraging:35", "suffix[_Trunk]")
_p3k("suffix._Trunk_Full", "Foraging:6", "Foraging:35", "suffix[_Trunk_Full]")
# 3.2 every trunk species (tier_tags LOGS): the 0.4.56 block rows rewritten, the species without one get a row (P3_ADD)
_WOLD = dict((_w, _x) for _x, _ws in WOOD_TIERS for _w in _ws)
P3_ADD = []
for _t in sorted(_TT57.LOGS):
    for _w in _TT57.LOGS[_t]:
        for _suf in ("_Trunk", "_Trunk_Full"):
            _iid = "Wood_%s%s" % (_w, _suf)
            if _suf == "_Trunk": must(_iid)
            if _iid not in ITEM_IDS: continue
            if _w in _WOLD: _p3k("block." + _iid, "Foraging:%d" % _WOLD[_w], "Foraging:%d" % P3_LOG[_t - 1], "block[%s]" % _iid)
            else: P3_ADD.append(("block." + _iid, "Foraging:%d" % P3_LOG[_t - 1], "block[%s]" % _iid))
assert sorted(_WOLD) == sorted(_w for _ws in _TT57.LOGS.values() for _w in _ws if _w in _WOLD) and len(_WOLD) == 17
# 3.3 crops (base 38) + herbs + orchard; Wild_Grass / Cactus kept
_p3k("prefix.Plant_Crop_", "Farming:3", "Farming:40", "prefix[Plant_Crop_]")
for _c, _old in (("Wheat", 4), ("Carrot", 4), ("Potato", 4), ("Lettuce", 4), ("Onion", 5), ("Turnip", 5), ("Cotton", 5), ("Rice", 5), ("Corn", 6),
                 ("Cauliflower", 6), ("Tomato", 6), ("Chilli", 7), ("Aubergine", 7), ("Pumpkin", 8), ("Mushroom", 3)):
    _p3k("prefix.Plant_Crop_" + _c, "Farming:%d" % _old, "Farming:%d" % P3_CROP[_c], "prefix[Plant_Crop_%s]" % _c)
for _c, _old, _new in (("Berry", 3, 40), ("Apple", 5, 80)) + tuple((_h + _n, _o, _x) for _h in ("Health", "Mana", "Stamina")
                                                                  for _n, _o, _x in (("1", 10, 80), ("2", 15, 280), ("3", 20, 605))):
    _p3k("prefix.Plant_Crop_" + _c, "Farming:%d" % _old, "Farming:%d" % _new, "prefix[Plant_Crop_%s]" % _c)
# ranching x10 (spec 3.3, GUESS)
P3_RANCH = ",".join("%s:%d" % (_i, _x * 10) for _i, _x in RANCH_ITEMS)
assert P3_RANCH == "Food_Egg:30,Ingredient_Fabric_Scrap_Wool:30,Ingredient_Feathers_Light:10,Food_Chicken_Raw:20,Food_Pork_Raw:20,Food_Beef_Raw:30,Food_Wildmeat_Raw:20,Ingredient_Hide_Light:10,Ingredient_Hide_Medium:20"
_p3k("ranching.items", RANCH_DEF, P3_RANCH)
# 3.6 alchemy: tierXp (1,500 x f(zone start), the spec's numbers); each row keeps its ratio to its bench tier's old value (RequiredTierLevel
# from Assets.zip, none = I), rounded like p3_xp; Morph = 7400 (the spec's number); the Popberry bomb stays 10 (the craft / salvage loop
# guard below pays nothing above 10 for an output that salvages back); 0 stays 0
P3_ALCH_TIER = [1500, 7400, 18200, 33900, 54400]
_p3k("alchemy.tierXp", ",".join(str(_x) for _x in ALCH_TIER), ",".join(str(_x) for _x in P3_ALCH_TIER))
_atier = {}
with zipfile.ZipFile(ASSETS) as _z57:
    for _n57 in _z57.namelist():
        if _n57.startswith("Server/Item/Items/") and _n57.endswith(".json") and os.path.basename(_n57)[:-5] in dict(ALCH_XP):
            _r57 = (json.loads(_z57.read(_n57).decode("utf-8-sig")).get("Recipe") or {})
            _br57 = _r57.get("BenchRequirement") or []
            _br57 = [_b for _b in (_br57 if isinstance(_br57, list) else [_br57]) if isinstance(_b, dict) and _b.get("Id") == "Alchemybench"]
            _atier[os.path.basename(_n57)[:-5]] = int((_br57[0] if _br57 else {}).get("RequiredTierLevel", 1) or 1)
assert sorted(_atier) == sorted(dict(ALCH_XP)), sorted(set(dict(ALCH_XP)) - set(_atier))
P3_ALCH = {}
for _i, _x in ALCH_XP:
    if _x == 0 or _i == "Weapon_Bomb_Popberry": P3_ALCH[_i] = _x
    elif _i.startswith("Potion_Morph_"): P3_ALCH[_i] = 7400
    else:
        _v = float(P3_ALCH_TIER[_atier[_i] - 1]) * _x / ALCH_TIER[_atier[_i] - 1]
        P3_ALCH[_i] = int(round(_v / 5.0)) * 5 if _v < 1000 else int(round(_v / 50.0)) * 50
    if P3_ALCH[_i] != _x: _p3k("alchemy.xp." + _i, str(_x), str(P3_ALCH[_i]), "alchemy.xp[%s]" % _i)
assert P3_ALCH["Potion_Health_Lesser"] == 1500 and P3_ALCH["Potion_Antidote"] == 2400 and P3_ALCH["Potion_Health_Small"] == 7400
assert P3_ALCH["Potion_Health"] == 18200 and P3_ALCH["Potion_Health_Greater"] == 33900 and P3_ALCH["Weapon_Bomb_Popberry"] == 10
assert all(_v >= 0 for _v in P3_ALCH.values())
print("0.4.57 alchemy.xp (bench tier: old -> new): " + ", ".join("%s (%s): %d -> %d" % (_i, "I II III IV V".split()[_atier[_i] - 1], _x, P3_ALCH[_i]) for _i, _x in ALCH_XP))
# 3.7 smithing: a bar = its ore's Mining XP; an alloy = its tier (Electrum = tier_tags' T3); Enchanted alloy = 100 bars x the bar x 0.5
P3_SMITH = {}
for _i, _x in SMITH_XP:
    _m = _i.replace("Ingredient_Bar_", "").replace("_SkyWynn", "")
    if _i.startswith("Ingredient_Bar_") and _m in P3_ORE: P3_SMITH[_i] = P3_ORE[_m]
    elif _i.startswith("Ingredient_Bar_"): P3_SMITH[_i] = p3_xp(50, _TT57.tier(_i) or _TT57.metal_tier(_m))
    elif _i.startswith("Skyy_Ench_"): P3_SMITH[_i] = None
    elif _i == "Potion_Empty": P3_SMITH[_i] = 20
    else: P3_SMITH[_i] = _x
for _i, _x in SMITH_XP:
    if P3_SMITH[_i] is None: P3_SMITH[_i] = 50 * P3_SMITH["Ingredient_Bar_" + _i[len("Skyy_Ench_"):] + ("" if _i == "Skyy_Ench_Bronze" else "_SkyWynn")]
    if P3_SMITH[_i] != _x: _p3k("smithing.xp." + _i, str(_x), str(P3_SMITH[_i]), "smithing.xp[%s]" % _i)
assert [P3_SMITH["Ingredient_Bar_%s" % _m] for _m in ("Bronze", "Silver", "Gold", "Onyxium", "Prisma")] == [180, 180, 370, 2650, 2450]
assert [P3_SMITH["Ingredient_Bar_%s_SkyWynn" % _m] for _m in ("Dusk", "Azurvane", "Cinder", "Lumen", "Electrum")] == [500, 985, 1650, 2450, 180]
assert P3_SMITH["Potion_Empty"] == 20 and P3_SMITH["Ingredient_Charcoal"] == 0 and P3_SMITH["Skyy_Ench_Bronze"] == 9000
print("0.4.57 smithing.xp: " + ", ".join("%s %d -> %d" % (_i, _x, P3_SMITH[_i]) for _i, _x in SMITH_XP))
# 3.8 Acrobatics x1.5 (GUESS) + perfect dodge
for _k, _o, _n in (("acro.sprintXpPerBlock", "0.25", "0.4"), ("acro.runXpPerBlock", "0.15", "0.25"), ("acro.walkXpPerBlock", "0.05", "0.08"),
                   ("acro.jumpXp", "2", "3"), ("acro.dodgeXp", "3", "5"), ("acro.fallDamageXp", FALL_DMG_DEF, "15"), ("acro.perfectDodge.xp", PD_XP_DEF, "8")):
    _p3k(_k, _o, _n)
assert FALL_DMG_DEF == "10" and PD_XP_DEF == "5"
# the new rows (spec 4, 5, 3.8, 7) - appended once in the marked block
P3_CATCH = "Mining,Foraging,Farming,Fishing,Alchemy,Smithing,Cooking,Acrobatics"
P3_PAST = "1.2,1.45,1.8,2.25,2.8"
P3_LF = "Acrobatics,Fishing"
P3_NEWROWS = [("catchup.enabled", "true"), ("catchup.freeLevels", "5"), ("catchup.perLevel", "10"), ("catchup.max", "100"),
              ("catchup.skills", P3_CATCH), ("rebirth.pastLifeXp", P3_PAST), ("xp.levelFactor.skills", P3_LF)]
P3_ADD = [(_k, _v, None) for _k, _v in P3_NEWROWS] + P3_ADD
P3_MARK_ID = "SkyySkills 0.4.57 Balance P3"
P3_MARK = "# SkyySkills 0.4.57 Balance P3 marker: one level list, XP per action x tier, catch-up and past-life XP (updated once)."
P3_HEAD = ["# ---------- Balance P3 XP (SkyySkills 0.4.57) ----------",
           "# Comments must stay on their own lines. research/Balance-P3-XP-Spec.md: one level list for the class and every skill (levels,",
           "# levels.class.sameAsOthers true), XP per action rising with the tier of what you gather, craft or kill.",
           "# Catch-up: a catchup.skills skill more than catchup.freeLevels levels behind your class level earns catchup.perLevel percent",
           "# more XP per extra level, at most catchup.max percent (never Exploration or the class skills; catchup.enabled false = off).",
           "# Past-life XP: after rebirth n, XP into a skill or class skill below your last run's level cap x entry n of rebirth.pastLifeXp",
           "# (past the last entry: the last entry). Levels you never reached before keep the first-time pace.",
           "# xp.levelFactor.skills: these skills have no tiers, so their XP grows with their own level (x 1 + 0.13 (L-1) + 0.004 (L-1)^2).",
           "# A per-skill XP multiplier: add xp.skillMult.<Skill> lines (Server Setup - Skills - Levels; Class = every class skill).",
           "# Every trunk species pays by its tier (block rows below for the species without one)."]
for _ln57 in P3_HEAD + [P3_MARK]:
    assert _ln57.startswith("#") and all(ord(_ch) < 128 for _ch in _ln57) and len(_ln57) <= 140 and '"' not in _ln57 and "\\" not in _ln57
    assert not _cre.match(r"#\s*[A-Za-z][A-Za-z0-9._-]*\s*[=:]\s*\S+\s*$", _ln57), _ln57
assert "=" not in P3_MARK and P3_MARK_ID in P3_MARK and not any(P3_MARK_ID in _l for _l in P3_HEAD)
assert len(set(_k for _k, _o, _n, _r in P3_KEYS)) == len(P3_KEYS) and not set(_k for _k, _o, _n, _r in P3_KEYS) & set(_k for _k, _v, _r in P3_ADD)
P3_BLOCK = "\n".join(P3_HEAD + ["%s=%s" % (_k, _v) for _k, _v, _r in P3_ADD] + [P3_MARK]) + "\n"
# the code defaults of the rows P3 changes follow (a file without the line = the P3 value); the 0.4.56 blocks above keep the old values
ALCH_TIER = list(P3_ALCH_TIER)
ALCH_PUTS = "\n".join('  m.put("%s", Long.valueOf(%dL));' % (i, P3_ALCH[i]) for i, x in ALCH_XP)
SMITH_PUTS = "\n".join('  m.put("%s", Long.valueOf(%dL));' % (i, P3_SMITH[i]) for i, x in SMITH_XP)
RANCH_DEF = P3_RANCH


def p3_apply(text):
    """the Python twin of P3Mig.plan for an LF default file of one-line entries (the harness checks the Java plan gives the same text)"""
    out, seen = [], set()
    for _ln in text.split("\n"):
        _t = _ln.strip()
        if _t and not _t.startswith("#") and not _t.startswith("!") and "=" in _ln:
            assert not _ln.endswith("\\"), _ln
            _k, _v = _ln.split("=", 1)
            _hit = [_e for _e in P3_KEYS if _e[0] == _k.strip()]
            if _hit and _v.strip() in _hit[0][1].split("|"):
                seen.add(_k.strip())
                if _hit[0][2] is None: continue
                _ln = _k + "=" + _hit[0][2]
        out.append(_ln)
    body = "\n".join(out)
    return body + ("" if body.endswith("\n") else "\n") + P3_BLOCK, seen
'''
P.rep('''DEFAULTS = "\\n".join(L) + "\\n"
assert all(ord(ch) < 128 for ch in DEFAULTS)
''', P3DATA + '''DEFAULTS_056 = "\\n".join(L) + "\\n"   # 0.4.57: the 0.4.56 default file - every 0.4.56 block and assert below reads it
DEFAULTS, _p3seen = p3_apply(DEFAULTS_056)   # 0.4.57: the fresh file = the 0.4.56 file after the P3 update (+ the P3 block and marker)
assert sorted(_p3seen) == sorted(_k for _k, _o, _n, _r in P3_KEYS if _k != "levels.class.sameAsOthers"), sorted(set(_k for _k, _o, _n, _r in P3_KEYS) - _p3seen)   # CURVE_L already says true
assert all(ord(ch) < 128 for ch in DEFAULTS) and len(DEFAULTS.encode("utf-8")) < 65000, len(DEFAULTS)
assert ("\\n" + DEFAULTS).count("\\nlevels=" + P3_LEVELS_TEXT + "\\n") == 1 and "levels.skill.Mining=" not in DEFAULTS and "levels.skill.Farming=" not in DEFAULTS
print("0.4.57: P3 update plan %d keys (%d removed), %d lines appended; default file %d bytes" % (len(P3_KEYS), sum(1 for _e in P3_KEYS if _e[2] is None), len(P3_ADD), len(DEFAULTS)))
''')
# every 0.4.56 assert that reads a 0.4.56 block value of the default file now reads DEFAULTS_056
for _old in ['''assert DEFAULTS.count(MN52_MARK_ID) == 1 and all(("\\n" + DEFAULTS).count("\\n%s=%s\\n" % (_k, _n)) == 1 for _k, _o, _n in MN52_KEYS)   # 0.4.52''',
             '''assert DEFAULTS.count(NC53_MARK_ID) == 1 and all(("\\n" + DEFAULTS).count("\\n%s=%s\\n" % (_k, _n)) == 1 for _k, _o, _n in NC53_KEYS)   # 0.4.53''',
             '''assert DEFAULTS.count(FA53_MARK_ID) == 1 and ("\\n" + DEFAULTS).count("\\nlevels.skill.Farming=") == 1   # 0.4.53''']:
    P.rep(_old, _old.replace("DEFAULTS", "DEFAULTS_056").replace("MN52_MARK_ID", "MN52_MARK_ID").replace("DEFAULTS_056_056", "DEFAULTS_056"))

# ---------------------------------------------------------------------------------------------------- 3. P3Xp (fields + read before SkillCfg.load)
# fix 2 (critic: P3Mig failing after CurveP3Mig moved the saved XP): SkillCfg.P3PEND (set by CurveP3Mig.after) -> load() reads the text P3Mig.plan
# makes of the file (P3Mig's methods are compiled after load: reflection), never the old lists against new-scale XP; cleared once the file holds it
P3PEND_SRC = r'''cfg.addField(CtField.make("public static volatile boolean P3PEND = false;", cfg))
cfg.addMethod(CtNewMethod.make(J14(r"""
public static java.util.Properties p3pend(java.util.Properties p) {
  if (!P3PEND || FILE == null) return p;
  try {
    String t = new String(java.nio.file.Files.readAllBytes(FILE), "ISO-8859-1");
    java.lang.reflect.Method m = Class.forName("@PKG@.P3Mig").getMethod("plan", new Class[] { Class.forName("java.lang.String") });
    Object[] r = (Object[]) m.invoke(null, new Object[] { t });
    if (r == null) { P3PEND = false; return p; }
    java.util.Properties q = new java.util.Properties();
    q.load(new java.io.StringReader((String) r[0]));
    return q;
  } catch (Throwable x) {
    warn("could not use the 0.4.57 settings from memory (" + x + ") - xp.properties used as it is");
    return p;
  }
}"""), cfg))
'''
P3X_A = r'''# ================= 0.4.57 P3Xp part 1 (Balance P3): the catch-up / past-life / level-factor / per-skill multiplier settings (SkillCfg.load) =================
p3x.addField(CtField.make('public static final String DEF_CATCH = "%s";' % P3_CATCH, p3x))
p3x.addField(CtField.make('public static final String DEF_PAST = "%s";' % P3_PAST, p3x))
p3x.addField(CtField.make('public static final String DEF_LF = "%s";' % P3_LF, p3x))
p3x.addField(CtField.make('public static final String READS = "xp.combat,xp.alchemy,xp.smithing,xp.fishing,xp.acrobatics";', p3x))
p3x.addField(CtField.make('public static final String READS_KEY = "rebirth:reads:SkyySkills";', p3x))
p3x.addField(CtField.make('public static final String MULT_PREFIX = "xp.skillMult.";', p3x))
for _d57 in ("public static volatile boolean CATCH_ON = true;", "public static volatile int CATCH_FREE = 5;", "public static volatile double CATCH_PER = 0.1;",
             "public static volatile double CATCH_MAX = 1.0;", "public static volatile boolean[] CATCH = new boolean[%d];" % len(SLOT_NAMES),
             'public static volatile String CATCH_TEXT = "";', "public static volatile double[] PAST = new double[] { 1.2, 1.45, 1.8, 2.25, 2.8 };",
             'public static volatile String PAST_TEXT = "%s";' % P3_PAST, "public static volatile boolean[] LF = new boolean[%d];" % len(SLOT_NAMES),
             'public static volatile String LF_TEXT = "";', "public static volatile double[] MULT = new double[0];", 'public static volatile String MULT_TEXT = "";',
             "public static final java.util.concurrent.ConcurrentHashMap RBN = new java.util.concurrent.ConcurrentHashMap();",
             "public static volatile long RBN_TTL = 5000L;"):
    p3x.addField(CtField.make(_d57, p3x))
# a skill name -> its slot for the P3 lists: -1 = blank, -2 = not allowed (Exploration, the old Combat slot, a class skill unless cls, unknown)
p3x.addMethod(CtNewMethod.make(J14(r"""
public static int slotOf(String t, boolean cls) {
  if (t == null) return -1;
  String x = t.trim();
  if (x.length() == 0) return -1;
  for (int s = 0; s < @PKG@.SkillDefs.N; s++) {
    if (!@PKG@.SkillDefs.NAMES[s].equalsIgnoreCase(x) && !@PKG@.SkillDefs.LABELS[s].equalsIgnoreCase(x)) continue;
    if (s == @PKG@.SkillDefs.EXPLORATION || s == @PKG@.SkillDefs.COMBAT) return -2;
    if (@PKG@.SkillDefs.isClass(s) && !cls) return -2;
    return s;
  }
  return -2;
}"""), p3x))
# a comma list -> one flag per slot (bad entries -> WARN, left out)
p3x.addMethod(CtNewMethod.make(J14(r"""
public static boolean[] flags(String v, String key) {
  boolean[] on = new boolean[@PKG@.SkillDefs.N];
  String[] ps = (v == null ? "" : v).split(",");
  for (int i = 0; i < ps.length; i++) {
    int s = slotOf(ps[i], false);
    if (s == -1) continue;
    if (s < 0) { @PKG@.SkillCfg.warn(key + ": '" + ps[i].trim() + "' is not a skill it can list (no Exploration, no class skills) - ignored"); continue; }
    on[s] = true;
  }
  return on;
}"""), p3x))
p3x.addMethod(CtNewMethod.make(J14(r"""
public static String text(boolean[] on) {
  StringBuilder sb = new StringBuilder();
  for (int s = 0; s < on.length && s < @PKG@.SkillDefs.N; s++) {
    if (!on[s]) continue;
    if (sb.length() > 0) sb.append(',');
    sb.append(@PKG@.SkillDefs.LABELS[s]);
  }
  return sb.toString();
}"""), p3x))
# "1.2,1.45,..." -> the boosts (each 1 - 10), null = a bad list
p3x.addMethod(CtNewMethod.make(J14(r"""
public static double[] pastList(String v) {
  if (v == null) return null;
  String t = v.trim();
  if (t.length() == 0) return new double[0];
  String[] ps = t.split(",");
  if (ps.length > 100) return null;
  double[] r = new double[ps.length];
  for (int i = 0; i < ps.length; i++) {
    double d = 0.0;
    try { d = Double.parseDouble(ps[i].trim()); } catch (Throwable e) { return null; }
    if (Double.isNaN(d) || d < 1.0 || d > 10.0) return null;
    r[i] = d;
  }
  return r;
}"""), p3x))
p3x.addMethod(CtNewMethod.make(J14(r"""
public static double clamp(double v, double lo, double hi, double d) {
  if (Double.isNaN(v) || Double.isInfinite(v)) return d;
  return v < lo ? lo : (v > hi ? hi : v);
}"""), p3x))
p3x.addMethod(CtNewMethod.make(J14(r"""
public static void read(java.util.Properties p) {
  CATCH_ON = @PKG@.SkillCfg.bool(p, "catchup.enabled", true);
  CATCH_FREE = (int) clamp((double) @PKG@.SkillCfg.lng(p, "catchup.freeLevels", 5L), 0.0, 50.0, 5.0);
  CATCH_PER = clamp(@PKG@.SkillCfg.dbl(p, "catchup.perLevel", 10.0), 0.0, 100.0, 10.0) / 100.0;
  CATCH_MAX = clamp(@PKG@.SkillCfg.dbl(p, "catchup.max", 100.0), 0.0, 500.0, 100.0) / 100.0;
  boolean[] c = flags(p.getProperty("catchup.skills", DEF_CATCH), "catchup.skills");
  CATCH = c;
  CATCH_TEXT = text(c);
  String pl = p.getProperty("rebirth.pastLifeXp", DEF_PAST);
  double[] pv = pastList(pl);
  if (pv == null) { @PKG@.SkillCfg.warn("rebirth.pastLifeXp='" + pl + "' is not a list of numbers from 1 to 10 - using " + DEF_PAST); pv = pastList(DEF_PAST); pl = DEF_PAST; }
  PAST = pv;
  PAST_TEXT = pl.trim();
  boolean[] lf = flags(p.getProperty("xp.levelFactor.skills", DEF_LF), "xp.levelFactor.skills");
  LF = lf;
  LF_TEXT = text(lf);
  double[] m = new double[@PKG@.SkillDefs.N];
  for (int s = 0; s < m.length; s++) m[s] = 1.0;
  StringBuilder mt = new StringBuilder();
  java.util.Iterator it = new java.util.TreeSet(p.stringPropertyNames()).iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (!k.startsWith(MULT_PREFIX)) continue;
    String e = k.substring(MULT_PREFIX.length()).trim();
    double d = @PKG@.SkillCfg.dbl(p, k, Double.NaN);
    if (Double.isNaN(d) || d < 0.0 || d > 100.0) { @PKG@.SkillCfg.warn(k + "=" + p.getProperty(k) + " is not a number from 0 to 100 - ignored"); continue; }
    if (e.equalsIgnoreCase("Class")) {
      for (int s = 0; s < m.length; s++) if (@PKG@.SkillDefs.isClass(s)) m[s] = d;
    } else {
      int s = slotOf(e, true);
      if (s < 0) { @PKG@.SkillCfg.warn(k + ": '" + e + "' is not a skill (no Exploration) - ignored"); continue; }
      m[s] = d;
    }
    if (mt.length() > 0) mt.append(", ");
    mt.append(e).append(" x").append(@PKG@.DivCfg.num(d));
  }
  MULT = m;
  MULT_TEXT = mt.toString();
}"""), p3x))
# check= hooks (null = fine, text = refused)
p3x.addMethod(CtNewMethod.make(J14(r"""
public static String checkSkills(String key, String v) {
  if (v == null) return null;
  String[] ps = v.split(",");
  for (int i = 0; i < ps.length; i++) if (slotOf(ps[i], false) == -2) return ps[i].trim() + " cannot be listed (a skill name; no Exploration, no class skills).";
  return null;
}"""), p3x))
p3x.addMethod(CtNewMethod.make(J14(r"""
public static String checkPast(String key, String v) {
  if (v == null) return null;
  return pastList(v) == null ? "A comma list of boosts from 1 to 10, rebirth 1 first (1.2,1.45,1.8,2.25,2.8)." : null;
}"""), p3x))
p3x.addMethod(CtNewMethod.make(J14(r"""
public static String checkMult(String key, String v) {
  if (key == null) return null;
  int a = key.indexOf('[');
  int b = key.lastIndexOf(']');
  if (a < 0 || b <= a) return null;
  String e = key.substring(a + 1, b).trim();
  if (e.equalsIgnoreCase("Class") || slotOf(e, true) >= 0) return null;
  return e + " is not a skill (a skill name or Class; no Exploration).";
}"""), p3x))
p3x.addMethod(CtNewMethod.make(J14(r"""
public static String loadText() {
  return "catch-up " + (CATCH_ON ? "+" + @PKG@.DivCfg.num(CATCH_PER * 100.0) + "% a level past " + CATCH_FREE + " behind, max +" + @PKG@.DivCfg.num(CATCH_MAX * 100.0) + "% (" + CATCH_TEXT + ")" : "off") + ", past-life XP " + (PAST.length == 0 ? "off" : PAST_TEXT) + ", level factor " + (LF_TEXT.length() == 0 ? "none" : LF_TEXT) + (MULT_TEXT.length() > 0 ? ", XP multipliers " + MULT_TEXT : "");
}"""), p3x))
'''
P.rep('''cfg.addMethod(CtNewMethod.make(f"""
public static synchronized String load() {{''', P3X_A + P3PEND_SRC + '''cfg.addMethod(CtNewMethod.make(f"""
public static synchronized String load() {{''')
P.rep('''    try {{ p.load(in); }} finally {{ in.close(); }}
    upgradeLevels(p);
''', '''    try {{ p.load(in); }} finally {{ in.close(); }}
    p = p3pend(p);   // 0.4.57 fix 2: the saved XP moved but the xp.properties update failed -> the planned 0.4.57 text (CurveP3Mig.after)
    upgradeLevels(p);
''')
P.rep('''    {PKG}.XpEven.read(p);       // 0.4.43: fell.otherLogsPercent, mining.xpMultiplier
''', '''    {PKG}.XpEven.read(p);       // 0.4.43: fell.otherLogsPercent, mining.xpMultiplier
    {PKG}.P3Xp.read(p);         // 0.4.57: Balance P3 - catch-up, past-life XP, the level factor, xp.skillMult
''')

# ---------------------------------------------------------------------------------------------------- 4. RbStat: Combat Echo from rebirth:fn:stat
P.rep('''public static double[] fetch(java.util.UUID u) {
  double[] z = new double[4];''', '''public static double[] fetch(java.util.UUID u) {
  double[] z = new double[5];   // 0.4.57: [4] = Combat Echo % (combatxp - allxp)''')
P.rep('''    z[3] = clampPct(cx);
    return z;''', '''    z[3] = clampPct(cx);
    try {   // fix 2: own try - an older SkyyRebirth that throws on these names zeroes only Combat Echo, never the whole refresh
      double cbx = ask(fn, u, "combatxp");   // 0.4.57 (SkyyRebirth 0.4.0 FOR SKYYSKILLS): Combat Echo = combatxp - allxp; no answer / an older
      double alx = ask(fn, u, "allxp");      // SkyyRebirth (0 for unknown names) = 0, never a failed fetch
      z[4] = (Double.isNaN(cbx) || Double.isNaN(alx)) ? 0.0 : clampPct(cbx - alx);
    } catch (Throwable t4) { z[4] = 0.0; }
    return z;''')
P.rep('''  if (pk == null || !pk.equals(e[0])) return new double[4];
  return (double[]) e[1];''', '''  if (pk == null || !pk.equals(e[0])) return new double[5];   // 0.4.57: 5 values
  return (double[]) e[1];''')
P.rep('''# the modifier keys a percent layer must never feed on: our three + SkyyAccessories' percent layer (skyyacc_*)''',
      '''# 0.4.57: Combat Echo (SkyyRebirth's Combat.echo) as a fraction - the value of the player's last 1 s tick; P3Xp.echo puts it on kill XP
rbs39.addMethod(CtNewMethod.make(J14(r"""
public static double combatEcho(java.util.UUID u) {
  if (!ON || u == null) return 0.0;
  double[] v = cached(u, @PKG@.SkillStore.pkey(u));
  return (v == null || v.length < 5) ? 0.0 : v[4] / 100.0;
}"""), rbs39))
# the modifier keys a percent layer must never feed on: our three + SkyyAccessories' percent layer (skyyacc_*)''')

# ---------------------------------------------------------------------------------------------------- 5. SkillBonus: one source's value; xpBonus + the rebirth source
P.rep('''# 0.4.56 SkillV3: Skill Trees 3 R3b - the rank SkyySkills reads from SkyyTrees''', '''# 0.4.57: one source's value of one skill:bonus key (a fraction, 0..5; 0 with bridge.bonus.enabled off) - SkyyRebirth's "rebirth" source
sbn.addMethod(CtNewMethod.make(J14(r"""
public static double srcVal(java.util.UUID u, String src, String key) {
  if (u == null || src == null || key == null || !@PKG@.BridgeCfg.BONUS) return 0.0;
  java.util.Map m = sources(u);
  if (m == null) return 0.0;
  try {
    Object v = m.get(src);
    if (!(v instanceof java.util.Map)) return 0.0;
    Object n = ((java.util.Map) v).get(key);
    if (!(n instanceof Number)) return 0.0;
    double d = ((Number) n).doubleValue();
    if (Double.isNaN(d) || Double.isInfinite(d) || !(d > 0.0)) return 0.0;
    return d > 5.0 ? 5.0 : d;
  } catch (Throwable t) { return 0.0; }
}"""), sbn))
# 0.4.56 SkillV3: Skill Trees 3 R3b - the rank SkyySkills reads from SkyyTrees''')
P.rep('''  double s = PER_CI * (double) rank(u, KEY_CI, MAX_CI) + @PKG@.SkillBonus.sum(u, "xp.combat");''',
      '''  double s = PER_CI * (double) rank(u, KEY_CI, MAX_CI) + @PKG@.SkillBonus.sum(u, "xp.combat") - @PKG@.SkillBonus.srcVal(u, "rebirth", "xp.combat");   // 0.4.57: Combat Echo = kill XP only (P3Xp.echo)''')
P.rep('''  double s = (slot >= on.length || !on[slot]) ? 0.0 : sum(u, "xp." + key(slot));
  s = s + rb;''', '''  double s = (slot < on.length && on[slot]) ? sum(u, "xp." + key(slot)) : ({PKG}.SkillDefs.isClass(slot) ? 0.0 : srcVal(u, "rebirth", "xp." + key(slot)));   // 0.4.57: SkyyRebirth's Echo / Insight on every non-class skill (FOR SKYYSKILLS 1)
  s = s + rb;''')

# ---------------------------------------------------------------------------------------------------- 6. P3Xp part 2 (the maths) before SkillXp
P3X_B = r'''# ================= 0.4.57 P3Xp part 2 (Balance P3): the multiplier every XP gain path takes (after the xp multiplier, before the tree / VP bonus) =========
# the own-level factor f(L) = 1 + 0.13 (L-1) + 0.004 (L-1)^2 (= the kill XP level curve's shape; L < 1 -> 1)
p3x.addMethod(CtNewMethod.make(J14(r"""
public static double fLv(int L) {
  double x = L < 1 ? 0.0 : (double) (L - 1);
  return 1.0 + 0.13 * x + 0.004 * x * x;
}"""), p3x))
# the capped level of slot s of the player's ACTIVE profile from the LOADED data only (-1 = not loaded): never a file read, so the
# BridgeXp.offerX path ("any thread, no I/O") stays I/O-free (SkillCap.totalOf + SkillCap.level, the rebirth cap from its cache)
p3x.addMethod(CtNewMethod.make(J14(r"""
public static int lvl(java.util.UUID u, int s) {
  if (u == null || s < 0 || s >= @PKG@.SkillDefs.N) return -1;
  String k = @PKG@.SkillStore.pkey(u);
  long t = @PKG@.SkillCap.totalOf(k, s);
  if (t < 0L) return -1;
  return @PKG@.SkillCap.level(k, s, t);
}"""), p3x))
p3x.addMethod(CtNewMethod.make(J14(r"""
public static int classLevel(java.util.UUID u) {
  int cs = @PKG@.SkillClass.slot(u);
  if (cs < 0) return -1;
  return lvl(u, cs);
}"""), p3x))
p3x.addMethod(CtNewMethod.make(J14(r"""
public static int gap(java.util.UUID u, int s) {
  int cl = classLevel(u);
  int sl = lvl(u, s);
  if (cl < 0 || sl < 0) return 0;
  return cl - sl;
}"""), p3x))
p3x.addMethod(CtNewMethod.make(J14(r"""
public static double catchup(java.util.UUID u, int s) {
  boolean[] c = CATCH;
  if (!CATCH_ON || u == null || s < 0 || s >= c.length || !c[s]) return 1.0;
  int g = gap(u, s);
  if (g <= CATCH_FREE) return 1.0;
  double b = CATCH_PER * (double) (g - CATCH_FREE);
  if (b > CATCH_MAX) b = CATCH_MAX;
  return b > 0.0 ? 1.0 + b : 1.0;
}"""), p3x))
# the profile's rebirth count (rebirth:fn:count, SkillStore.rbN) cached RBN_TTL ms (a "no answer yet" 250 ms); 0 = none / no SkyyRebirth
p3x.addMethod(CtNewMethod.make(J14(r"""
public static int rebirths(String k) {
  if (k == null) return 0;
  long now = System.currentTimeMillis();
  Object o = RBN.get(k);
  if (o instanceof long[]) {
    long[] e = (long[]) o;
    if (now - e[0] < (e[1] < 0L ? 250L : RBN_TTL)) return e[1] < 0L ? 0 : (int) e[1];
  }
  int n = @PKG@.SkillStore.rbN(k);
  if (RBN.size() > 4096) RBN.clear();
  RBN.put(k, new long[] { now, (long) n });
  return n < 0 ? 0 : n;
}"""), p3x))
# the cap of the last run: runBase + the raise x (n-1)/n, clamped by levels.capMax (rebirth 6+ at the 100 clamp: 100 = every level)
p3x.addMethod(CtNewMethod.make(J14(r"""
public static int prevCap(String k, int s, int n) {
  if (n <= 0 || !@PKG@.SkillDefs.rebirthResets(s)) return 0;
  long ex = (long) @PKG@.SkillCap.extra(k, s);
  long pc = (long) @PKG@.SkillCap.runBase(s) + ex * (long) (n - 1) / (long) n;
  int cm = @PKG@.SkillDefs.CAP_MAX;
  if (cm > 0 && pc > (long) cm) pc = (long) cm;
  return (int) pc;
}"""), p3x))
p3x.addMethod(CtNewMethod.make(J14(r"""
public static double pastLife(java.util.UUID u, int s) {
  double[] pl = PAST;
  if (u == null || pl == null || pl.length == 0 || !@PKG@.SkillDefs.rebirthResets(s)) return 1.0;
  String k = @PKG@.SkillStore.pkey(u);
  int n = rebirths(k);
  if (n <= 0) return 1.0;
  int L = lvl(u, s);
  if (L < 0 || L >= prevCap(k, s, n)) return 1.0;
  double b = pl[(n > pl.length ? pl.length : n) - 1];
  return b > 1.0 ? b : 1.0;
}"""), p3x))
p3x.addMethod(CtNewMethod.make(J14(r"""
public static double levelF(java.util.UUID u, int s) {
  boolean[] lf = LF;
  if (u == null || s < 0 || s >= lf.length || !lf[s]) return 1.0;
  int L = lvl(u, s);
  return L < 0 ? 1.0 : fLv(L);
}"""), p3x))
p3x.addMethod(CtNewMethod.make(J14(r"""
public static double skillMult(int s) {
  double[] m = MULT;
  return (s >= 0 && s < m.length) ? m[s] : 1.0;
}"""), p3x))
# own = XP the player earned itself in that skill (blocks, crafts, kills, moves, a SkyyFishing catch) - the level factor is only for those
p3x.addMethod(CtNewMethod.make(J14(r"""
public static double mult(java.util.UUID u, int s, boolean own) {
  if (u == null || s < 0 || s >= @PKG@.SkillDefs.N || !@PKG@.SkillDefs.boostable(s)) return 1.0;
  double m = skillMult(s) * catchup(u, s) * pastLife(u, s);
  if (own) m = m * levelF(u, s);
  if (Double.isNaN(m) || Double.isInfinite(m) || m < 0.0) return 1.0;
  return m;
}"""), p3x))
# x a factor; the fraction paid by chance (GatherPace.apply's rule: within 1e-9 of a whole number = that number)
p3x.addMethod(CtNewMethod.make(J14(r"""
public static long times(long amt, double m) {
  if (amt <= 0L) return amt;
  if (m == 1.0) return amt;
  if (!(m > 0.0)) return 0L;
  double x = (double) amt * m;
  if (x >= 9.0E15) return 9000000000000000L;
  double r = Math.rint(x);
  if (Math.abs(x - r) < 1.0E-9) x = r;
  long w = (long) Math.floor(x);
  double f = x - (double) w;
  if (f > 0.0 && java.util.concurrent.ThreadLocalRandom.current().nextDouble() < f) w++;
  return w;
}"""), p3x))
p3x.addMethod(CtNewMethod.make(J14(r"""
public static long apply(java.util.UUID u, int s, long amt, boolean own) {
  if (amt <= 0L) return amt;
  return times(amt, mult(u, s, own));
}"""), p3x))
# Combat Echo on kill XP (SkyyRebirth 0.4.0 FOR SKYYSKILLS 2): x (1 + (combatxp - allxp) / 100)
p3x.addMethod(CtNewMethod.make(J14(r"""
public static long echo(java.util.UUID u, long cx) {
  if (cx <= 0L || u == null) return cx;
  double e = @PKG@.RbStat.combatEcho(u);
  if (!(e > 0.0)) return cx;
  return times(cx, 1.0 + e);
}"""), p3x))
p3x.addMethod(CtNewMethod.make(J14(r"""
public static String pc(double f) {
  return @PKG@.DivCfg.num(Math.round(f * 1000.0) / 10.0) + "%";
}"""), p3x))
# the Stats page lines of slot s (spec 4 + 10.4): catch-up, past-life, the level factor, a server multiplier
p3x.addMethod(CtNewMethod.make(J14(r"""
public static void stats(java.util.UUID u, int s, java.util.ArrayList out, int max) {
  if (u == null || out == null || s < 0 || s >= @PKG@.SkillDefs.N || !@PKG@.SkillDefs.boostable(s)) return;
  try {
    double c = catchup(u, s);
    if (c > 1.0 && out.size() < max) out.add("Catch-up XP +" + pc(c - 1.0) + " (" + gap(u, s) + " levels behind your class)");
    double p = pastLife(u, s);
    if (p > 1.0 && out.size() < max) {
      String k = @PKG@.SkillStore.pkey(u);
      out.add("Past-life XP x" + @PKG@.DivCfg.num(p) + " below level " + prevCap(k, s, rebirths(k)));
    }
    double l = levelF(u, s);
    if (l > 1.0 && out.size() < max) out.add("XP grows with this skill's level: x" + @PKG@.DivCfg.num(Math.round(l * 100.0) / 100.0));
    double m = skillMult(s);
    if (m != 1.0 && out.size() < max) out.add("Server XP multiplier for this skill: x" + @PKG@.DivCfg.num(m));
  } catch (Throwable t) { }
}"""), p3x))
p3x.addMethod(CtNewMethod.make(J14(r"""
public static void reads(boolean on) {
  try {
    if (on) @PKG@.SkillStore.bridge().put(READS_KEY, READS);
    else @PKG@.SkillStore.bridge().remove(READS_KEY, READS);
  } catch (Throwable t) { }
}"""), p3x))

'''
P.rep('''# ================= SkillXp: award + level-up (world thread) =================''', P3X_B + '''# ================= SkillXp: award + level-up (world thread) =================''')

# ---------------------------------------------------------------------------------------------------- 7. the XP gain paths
P.rep('''  if (bonus) amount = {PKG}.SkillBonus.boost(u, bsl, {PKG}.GatherPace.applyAt(u, bsl, skill, amount));   // 0.4.14: the gathering pace, then the tree Wisdom''',
      '''  if (bonus) amount = {PKG}.SkillBonus.boost(u, bsl, {PKG}.GatherPace.applyAt(u, bsl, skill, {PKG}.P3Xp.apply(u, skill, amount, true)));   // 0.4.14: the gathering pace, then the tree Wisdom; 0.4.57: P3 first''')
P.rep('''        long amt = {PKG}.SkillBonus.boost(W.u, row, {PKG}.GatherPace.apply(W.u, row, xp));   // 0.4.14: the gathering pace first''',
      '''        long amt = {PKG}.SkillBonus.boost(W.u, row, {PKG}.GatherPace.apply(W.u, row, {PKG}.P3Xp.apply(W.u, row, xp, true)));   // 0.4.14: the gathering pace first; 0.4.57: P3''')
P.rep('''    long full = @PKG@.SkillBonus.boost(this.u, @PKG@.SkillDefs.FARMING, @PKG@.GatherPace.applyAt(this.u, @PKG@.SkillDefs.FARMING, @PKG@.SkillDefs.RANCHING, @PKG@.SkillCfg.scaled(this.base)));''',
      '''    long full = @PKG@.SkillBonus.boost(this.u, @PKG@.SkillDefs.FARMING, @PKG@.GatherPace.applyAt(this.u, @PKG@.SkillDefs.FARMING, @PKG@.SkillDefs.RANCHING, @PKG@.P3Xp.apply(this.u, @PKG@.SkillDefs.RANCHING, @PKG@.SkillCfg.scaled(this.base), true)));   // 0.4.57: P3''')
P.rep('''  long amt = amount(b, fr);
  if (amt <= 0L) return 0L;
  if ({PKG}.PartyCfg.TREE_BONUS) amt = {PKG}.SkillBonus.boost(mu, slot, amt);''', '''  long amt = amount(b, fr);
  if (amt <= 0L) return 0L;
  amt = {PKG}.P3Xp.echo(mu, {PKG}.P3Xp.apply(mu, slot, amt, false));   // 0.4.57: P3 (past-life) + this member's Combat Echo
  if ({PKG}.PartyCfg.TREE_BONUS) amt = {PKG}.SkillBonus.boost(mu, slot, amt);''')
P.rep('''public static long kill(@PR@ pr, @REF@ k, @ST@ s, int slot, long base, @REF@ npc) {
  int L = levelOf(s, npc);
  long cx;
  if (ON && L >= 1) cx = pay(slot, base, factor(L, @PKG@.SkillStore.level(pr.getUuid(), slot)));
  else cx = @PKG@.SkillCfg.classXp(slot, base);
  @PKG@.SkillXp.gain(pr, slot, cx);''', '''public static long kill(@PR@ pr, @REF@ k, @ST@ s, int slot, long base, @REF@ npc) {
  int L = levelOf(s, npc);
  long cx;
  if (ON && L >= 1) cx = pay(slot, base, factor(L, @PKG@.SkillStore.level(pr.getUuid(), slot)));
  else cx = @PKG@.SkillCfg.classXp(slot, base);
  @PKG@.SkillXp.gain(pr, slot, @PKG@.P3Xp.echo(pr.getUuid(), cx));   // 0.4.57: + the killer's Combat Echo (the party share stays on cx)''')
P.rep('''  if (in == null) {
    cx = @PKG@.SkillCfg.classXp(slot, base);
    @PKG@.SkillXp.gain(pr, slot, cx);''', '''  if (in == null) {
    cx = @PKG@.SkillCfg.classXp(slot, base);
    @PKG@.SkillXp.gain(pr, slot, @PKG@.P3Xp.echo(pr.getUuid(), cx));   // 0.4.57: Combat Echo''')
P.rep('''    else cx = @PKG@.SkillCfg.classXp(slot, base);
    @PKG@.SkillXp.gain(pr, slot, cx);
    @PKG@.PartyXp.share2(pr, k, s, cx, slot, base, ON ? L : -1);
    return cx;
  }
  double lb = lvBase(in[1], L, in[2]);
  cx = payD(slot, lb, gapFactor(L, @PKG@.SkillStore.level(pr.getUuid(), slot)));
  @PKG@.SkillXp.gain(pr, slot, cx);''', '''    else cx = @PKG@.SkillCfg.classXp(slot, base);
    @PKG@.SkillXp.gain(pr, slot, @PKG@.P3Xp.echo(pr.getUuid(), cx));   // 0.4.57: Combat Echo
    @PKG@.PartyXp.share2(pr, k, s, cx, slot, base, ON ? L : -1);
    return cx;
  }
  double lb = lvBase(in[1], L, in[2]);
  cx = payD(slot, lb, gapFactor(L, @PKG@.SkillStore.level(pr.getUuid(), slot)));
  @PKG@.SkillXp.gain(pr, slot, @PKG@.P3Xp.echo(pr.getUuid(), cx));   // 0.4.57: Combat Echo''')
P.rep('''public static long paidX(java.util.UUID u, int slot, long base, boolean grant, boolean cls) {{
  if (base <= 0L || slot < 0 || slot >= {PKG}.SkillDefs.N) return 0L;
  boolean canBoost = {PKG}.SkillDefs.boostable(slot);
  long amt = canBoost ? {PKG}.SkillCfg.scaled(base) : base;
  if (canBoost && cls) amt = {PKG}.SkillCfg.classXp(slot, amt);
  if (canBoost && (!grant || {PKG}.SkillBonus.grantBonus(slot))) amt = {PKG}.SkillBonus.boost(u, slot, amt);
  return amt;
}}""", bxp))''', '''public static long paidY(java.util.UUID u, int slot, long base, boolean grant, boolean cls, boolean own) {{
  if (base <= 0L || slot < 0 || slot >= {PKG}.SkillDefs.N) return 0L;
  boolean canBoost = {PKG}.SkillDefs.boostable(slot);
  long amt = canBoost ? {PKG}.SkillCfg.scaled(base) : base;
  if (canBoost && cls) amt = {PKG}.SkillCfg.classXp(slot, amt);
  if (canBoost) amt = {PKG}.P3Xp.apply(u, slot, amt, own);   // 0.4.57: Balance P3 (the level factor only on own XP)
  if (canBoost && (!grant || {PKG}.SkillBonus.grantBonus(slot))) amt = {PKG}.SkillBonus.boost(u, slot, amt);
  return amt;
}}""", bxp))
bxp.addMethod(CtNewMethod.make(f"""
public static long paidX(java.util.UUID u, int slot, long base, boolean grant, boolean cls) {{
  return paidY(u, slot, base, grant, cls, !grant);
}}""", bxp))
# 0.4.57 (SkyyRebirth FOR SKYYSKILLS 1 + spec 3.8): a SkyyFishing catch (skill:fn:addxp source "fishing" into Fishing) is XP the player earned
bxp.addMethod(CtNewMethod.make(f"""
public static boolean own(int slot, String source) {{
  return slot == {PKG}.SkillDefs.FISHING && "fishing".equals(source);
}}""", bxp))''')
P.rep('''  long amt = paidX(u, slot, base, grant, cls);
  if (amt <= 0L) return 0L;''', '''  boolean ow = own(slot, source);   // 0.4.57: a Fishing catch = earned XP (the level factor, the rebirth Echo), never a grant
  long amt = paidY(u, slot, base, grant && !ow, cls, !grant || ow);
  if (amt <= 0L) return 0L;''')

# ---------------------------------------------------------------------------------------------------- 8. the facts, the Stats page, rebirth:reads
P.rep('''           'public static final String[] XARMS = new String[] { "ranching", "orchard" };'):''',
      '''           'public static final String[] XARMS = new String[] { "ranching", "orchard", "acrobatics" };'):   # 0.4.57: + arm.acrobatics (SkyyRebirth FOR SKYYSKILLS 3)''')
P.rep('''  {PKG}.SkillV3.reads(true);   // 0.4.56: tree:reads:SkyySkills (Combat Insight + the Alchemy.PWisdom alias)
''', '''  {PKG}.SkillV3.reads(true);   // 0.4.56: tree:reads:SkyySkills (Combat Insight + the Alchemy.PWisdom alias)
  {PKG}.P3Xp.reads(true);      // 0.4.57: rebirth:reads:SkyySkills (the SkyyRebirth nodes this jar really boosts)
''')
P.rep('''  {PKG}.SkillV3.reads(false);   // 0.4.56: only our own value (never throws)
''', '''  {PKG}.SkillV3.reads(false);   // 0.4.56: only our own value (never throws)
  {PKG}.P3Xp.reads(false);      // 0.4.57: only our own value
''')

# 0.4.57 fix round: lines() = the old list (lines0) + the P3 lines (catch-up / past-life / level factor / server multiplier) LAST, only while the
# 7-line list has room - they never push the skill-tree line or a hook line off
P.rep('''public static java.util.ArrayList lines(java.util.UUID u, int s, int lv, boolean next) {{
  java.util.ArrayList out = new java.util.ArrayList();
  if (s == {PKG}.SkillDefs.COMBAT) {{''', '''public static java.util.ArrayList lines0(java.util.UUID u, int s, int lv, boolean next) {{   // 0.4.57 fix round: the list before the P3 lines
  java.util.ArrayList out = new java.util.ArrayList();
  if (s == {PKG}.SkillDefs.COMBAT) {{''')
P.rep('''    else if (s == {PKG}.SkillDefs.FARMING) out.add("Farming level (average of Farming - Ranching - Orchard) " + {PKG}.Farm3.avgOf({PKG}.SkillStore.data(u)) + ({PKG}.Farm3.AVG ? " - counts in your Overall Level" : ""));
  }}
  return out;
}}""", spg))
''', '''    else if (s == {PKG}.SkillDefs.FARMING) out.add("Farming level (average of Farming - Ranching - Orchard) " + {PKG}.Farm3.avgOf({PKG}.SkillStore.data(u)) + ({PKG}.Farm3.AVG ? " - counts in your Overall Level" : ""));
  }}
  return out;
}}""", spg))
spg.addMethod(CtNewMethod.make(f"""
public static java.util.ArrayList lines(java.util.UUID u, int s, int lv, boolean next) {{
  java.util.ArrayList out = lines0(u, s, lv, next);
  if (!next && s != {PKG}.SkillDefs.COMBAT) {PKG}.P3Xp.stats(u, s, out, {ST_LINES});   // 0.4.57 fix round: LAST, only while there is room
  return out;
}}""", spg))
''')
# ---------------------------------------------------------------------------------------------------- 9. the code defaults + Server Setup rows
for _a, _b in (('SPRINT = nn({PKG}.SkillCfg.dbl(p, "acro.sprintXpPerBlock", 0.25));', 'SPRINT = nn({PKG}.SkillCfg.dbl(p, "acro.sprintXpPerBlock", 0.4));   // 0.4.57 P3: x1.5'),
               ('RUN = nn({PKG}.SkillCfg.dbl(p, "acro.runXpPerBlock", 0.15));', 'RUN = nn({PKG}.SkillCfg.dbl(p, "acro.runXpPerBlock", 0.25));   // 0.4.57'),
               ('WALK = nn({PKG}.SkillCfg.dbl(p, "acro.walkXpPerBlock", 0.05));', 'WALK = nn({PKG}.SkillCfg.dbl(p, "acro.walkXpPerBlock", 0.08));   // 0.4.57'),
               ('JUMP_XP = nn({PKG}.SkillCfg.dbl(p, "acro.jumpXp", 2.0));', 'JUMP_XP = nn({PKG}.SkillCfg.dbl(p, "acro.jumpXp", 3.0));   // 0.4.57'),
               ('FALL_DMG_XP = nn({PKG}.SkillCfg.dbl(p, "acro.fallDamageXp", 10.0));', 'FALL_DMG_XP = nn({PKG}.SkillCfg.dbl(p, "acro.fallDamageXp", 15.0));   // 0.4.57'),
               ('DODGE_XP = nn({PKG}.SkillCfg.dbl(p, "acro.dodgeXp", 3.0));', 'DODGE_XP = nn({PKG}.SkillCfg.dbl(p, "acro.dodgeXp", 5.0));   // 0.4.57'),
               ('  XP = clampL(@PKG@.SkillCfg.lng(p, "acro.perfectDodge.xp", 5L), 0L, 100000L);', '  XP = clampL(@PKG@.SkillCfg.lng(p, "acro.perfectDodge.xp", 8L), 0L, 100000L);   // 0.4.57 P3: 5 -> 8')):
    P.rep(_a, _b)
for _a, _b in (('''    ("acro.sprintXpPerBlock", "XP per block sprinted", "acrobatics", "dec", "0.25",''', '''    ("acro.sprintXpPerBlock", "XP per block sprinted", "acrobatics", "dec", "0.4",'''),
               ('''    ("acro.runXpPerBlock", "XP per block run", "acrobatics", "dec", "0.15",''', '''    ("acro.runXpPerBlock", "XP per block run", "acrobatics", "dec", "0.25",'''),
               ('''    ("acro.walkXpPerBlock", "XP per block walked", "acrobatics", "dec", "0.05",''', '''    ("acro.walkXpPerBlock", "XP per block walked", "acrobatics", "dec", "0.08",'''),
               ('''    ("acro.jumpXp", "XP per jump", "acrobatics", "dec", "2",''', '''    ("acro.jumpXp", "XP per jump", "acrobatics", "dec", "3",'''),
               ('''    ("acro.fallDamageXp", "XP per point of fall damage", "acrobatics", "dec", "10",''', '''    ("acro.fallDamageXp", "XP per point of fall damage", "acrobatics", "dec", "15",'''),
               ('''    ("acro.dodgeXp", "XP per dodge", "acrobatics", "dec", "3",''', '''    ("acro.dodgeXp", "XP per dodge", "acrobatics", "dec", "5",'''),
               ('''    ("acro.perfectDodge.xp", "Perfect dodge Acrobatics XP", "acrobatics", "int", PD_XP_DEF,''', '''    ("acro.perfectDodge.xp", "Perfect dodge Acrobatics XP", "acrobatics", "int", "8",'''),
               ('''     "Item id and Ranching XP per item picked up, like Food_Egg:3, comma separated.", "reload"),''',
                '''     "Item id and Ranching XP per item picked up, like Food_Egg:30, comma separated.", "reload"),'''),
               ('''     "XP per level for skills without an own list (not class skills), level 1 first; count = max level.",''',
                '''     "XP per level for every skill without an own list (class skills too), level 1 first; count = max.",'''),
               ('''    ("levels.scale", "Level curve size, other skills", "levels", "int", "100", "10", "1000", "step=5", "%", "live,danger",
     "XP every non-class level needs as % of the default curve (110 = 10% more). Rewrites the list above.", "custom:SkillKit"),''',
                '''    ("levels.scale", "Level curve size", "levels", "int", str(P3_SCALE), "10", "1000", "step=5", "%", "live,danger",
     "XP every level needs as % of the P3 base curve (120 = Lv 50 at ~33 h). Rewrites the list above.", "custom:SkillKit"),'''),
               ('''    ("levels.class.sameAsOthers", "Class skills use the other list", "levels", "bool", "false", "", "", "", "", "live,danger",
     "On: class skills use the list of the other skills again (the old, slower curve; levels drop back).",''',
                '''    ("levels.class.sameAsOthers", "Class skills use the other list", "levels", "bool", "true", "", "", "", "", "live,danger",
     "On (P3 default): class skills level on the same list as every skill. Off: the old class list.",'''),
               ('''    ("gather.boost.skills", "Gathering pace skills", "gathering", "text", "Foraging,Farming", "", "300", "", "", "live",''',
                '''    ("gather.boost.skills", "Gathering pace skills", "gathering", "text", "", "", "300", "", "", "live",''')):
    P.rep(_a, _b)
P.rep('''     "No rebirth raises a skill or class level cap above this (0 = no clamp). XP keeps counting.", "reload"),
''', '''     "No rebirth raises a skill or class level cap above this (0 = no clamp). XP keeps counting.", "reload"),
    # 0.4.57 (Balance P3, research/Balance-P3-XP-Spec.md sections 4, 5, 3.8, 7): catch-up, past-life XP, the own-level factor, a multiplier per skill
    ("catchup.enabled", "Catch-up XP for skills behind the class", "levels", "bool", "true", "", "", "", "", "live",
     "Skills far behind your class level earn extra XP (the rows below; never Exploration).", "reload"),
    ("catchup.freeLevels", "Catch-up starts after (levels behind)", "levels", "int", "5", "0", "50", "", "", "live",
     "A skill this many levels behind the class gets no catch-up yet; each level more adds the % below.", "reload"),
    ("catchup.perLevel", "Catch-up per level behind", "levels", "int", "10", "0", "100", "", "%", "live",
     "Extra XP per level behind beyond the free levels (10 = +10% a level).", "reload"),
    ("catchup.max", "Catch-up max", "levels", "int", "100", "0", "500", "", "%", "live",
     "The most catch-up XP (100 = at most double XP).", "reload"),
    ("catchup.skills", "Catch-up skills", "levels", "text", P3_CATCH, "", "300", "", "", "live",
     "Skills that catch up to the class level, comma separated (no Exploration, no class skills).", "reload;check=P3Xp.checkSkills"),
    ("rebirth.pastLifeXp", "Past-life XP boost by rebirth", "levels", "text", P3_PAST, "", "200", "", "", "live",
     "XP x entry n after rebirth n on levels below your last cap (each 1-10; past the end: the last).", "reload;check=P3Xp.checkPast"),
    ("xp.levelFactor.skills", "Skills whose XP grows with their level", "levels", "text", P3_LF, "", "300", "", "", "live",
     "Skills without tiers: their own XP x the level factor (1 at level 1, x17 at 50).", "reload;check=P3Xp.checkSkills"),
    ("xp.skillMult", "XP multiplier per skill", "levels", "table", "", "0", "100", "dec;type;XP multiplier", "", "live",
     "An extra XP multiplier for one skill (Class = every class skill). No line = x1.", "reload;check=P3Xp.checkMult"),
''')
P.rep('''assert len(CFG_ROWS) == 277, ("0.4.53: + levels.runCap''', '''assert len(CFG_ROWS) == 285, ("0.4.57: + 8 P3 rows (catchup.*, rebirth.pastLifeXp, xp.levelFactor.skills, the xp.skillMult table); 0.4.53: + levels.runCap''')
# the build asserts: _dp = the 0.4.57 default file (rows), _dp56 = the 0.4.56 file (the 0.4.56 blocks' own checks)
P.rep('''_absent = []
for _r in CFG_ROWS:''', '''_dp56 = {}   # 0.4.57: the 0.4.56 default file (the 0.4.56 blocks' own checks below read it)
for _ln in DEFAULTS_056.split("\\n"):
    _t = _ln.strip()
    if _t and not _t.startswith("#") and "=" in _t:
        _dp56[_t.split("=", 1)[0].strip()] = _t.split("=", 1)[1].strip()
_absent = []
for _r in CFG_ROWS:''')
for _a, _b in (('''    assert len(_r37) == 1 and _dp.get(_k37) is not None and ("\\n" + _k37 + "=" + _dp[_k37] + "\\n") in ("\\n" + G37_DEFAULTS), _k37''',
                '''    assert len(_r37) == 1 and _dp56.get(_k37) is not None and ("\\n" + _k37 + "=" + _dp56[_k37] + "\\n") in ("\\n" + G37_DEFAULTS), _k37   # 0.4.57: the 0.4.56 block'''),
               ('''    assert sum(1 for _r in CFG_ROWS if _r[0] == _k) == 1 and _dp.get(_k) is not None and ("\\n" + _k + "=" + _dp[_k] + "\\n") in ("\\n" + N14_DEFAULTS), _k''',
                '''    assert sum(1 for _r in CFG_ROWS if _r[0] == _k) == 1 and _dp56.get(_k) is not None and ("\\n" + _k + "=" + _dp56[_k] + "\\n") in ("\\n" + N14_DEFAULTS), _k   # 0.4.57: the 0.4.56 block'''),
               ('''assert _dp.get("levels.skill.Mining") == ",".join(str(_x) for _x in MINING_PER) and sorted(_k for _k in _dp if _k.startswith("levels.skill.")) == sorted(SKL_KEYS + ["levels.skill.Farming"])''',
                '''assert _dp56.get("levels.skill.Mining") == ",".join(str(_x) for _x in MINING_PER) and sorted(_k for _k in _dp56 if _k.startswith("levels.skill.")) == sorted(SKL_KEYS + ["levels.skill.Farming"]) and not any(_k.startswith("levels.skill.") for _k in _dp)   # 0.4.57: the P3 file has no own list'''),
               ('''assert _dp.get("levels.skill.Farming") == FARM_LIST and len(FARM_LIST.split(",")) == 100   # 0.4.53''',
                '''assert _dp56.get("levels.skill.Farming") == FARM_LIST and len(FARM_LIST.split(",")) == 100   # 0.4.53 (0.4.57: the 0.4.56 file)'''),
               ('''assert _dp.get("gather.boost.skills") == "Foraging,Farming" == [_r for _r in CFG_ROWS if _r[0] == "gather.boost.skills"][0][4]''',
                '''assert _dp56.get("gather.boost.skills") == "Foraging,Farming" and _dp.get("gather.boost.skills") == "" == [_r for _r in CFG_ROWS if _r[0] == "gather.boost.skills"][0][4]   # 0.4.57: none by default'''),
               ('''assert DEFAULTS.endswith("\\n" + SKL_DEFAULTS''', '''assert DEFAULTS_056.endswith("\\n" + SKL_DEFAULTS''')):
    P.rep(_a, _b)
P.rep('''_k48 = [_r[0] for _r in CFG_ROWS]
''', '''# 0.4.57: the P3 rows once each in the Levels tab right after levels.capMax, row default = the P3 block = the code default
_k57 = [_r[0] for _r in CFG_ROWS]
assert _k57[_k57.index("levels.capMax") + 1:_k57.index("levels.capMax") + 9] == [_k for _k, _v in P3_NEWROWS] + ["xp.skillMult"]
for _k, _v in P3_NEWROWS:
    assert _k57.count(_k) == 1 and _dp.get(_k) == _v and ("\\n%s=%s\\n" % (_k, _v)) in ("\\n" + P3_BLOCK) and _k not in _dp56, _k
assert not any(_k.startswith("xp.skillMult") for _k in _dp) and _k57.count("xp.skillMult") == 1
assert all(_dp.get(_k) == (_n if _n is not None else None) for _k, _o, _n, _r in P3_KEYS) and all(_dp56.get(_k) in _o.split("|") for _k, _o, _n, _r in P3_KEYS if _k != "levels.class.sameAsOthers")
assert all(_dp.get(_k) == _v and _k not in _dp56 for _k, _v, _r in P3_ADD)
_k48 = [_r[0] for _r in CFG_ROWS]
''')
P.rep('''    assert any(_k.startswith(_pfx) for _k in _dp), "table %s has no default entries" % _tk''',
      '''    assert any(_k.startswith(_pfx) for _k in (_dp56 if _tk == "levels.skill" else _dp)), "table %s has no default entries" % _tk   # 0.4.57: no own list by default''')
P.rep(r'''assert all(("\n" + _k + "=" + _v + "\n") in ("\n" + DEFAULTS) for _k, _v in [('prefix.Ore_Lead', 'Mining:18')''',
      r'''assert all(("\n" + _k + "=" + _v + "\n") in ("\n" + DEFAULTS_056) for _k, _v in [('prefix.Ore_Lead', 'Mining:18')''')
# the 0.4.54 / 0.4.53 / 0.4.49 migration blocks check their lines against the 0.4.56 default file
for _a in ('''assert DEFAULTS.count(EN54_MARK_ID) == 1 and all(_dp.get(_k) == _v for _k, _v in''', '''assert DEFAULTS.count(ZO_MARK_ID) == 1 and all(_dp.get(_k) == _v for _k, _v in'''):
    P.rep(_a, _a.replace("DEFAULTS.", "DEFAULTS_056.").replace("_dp.get", "_dp56.get"))
P.rep('''assert all(("\\n" + _k + "=" + _v + "\\n") in ("\\n" + DEFAULTS) for _k, _v in [('smithing.xp.Skyy_Ench_Bronze', '800')''',
      '''assert all(("\\n" + _k + "=" + _v + "\\n") in ("\\n" + DEFAULTS_056) for _k, _v in [('smithing.xp.Skyy_Ench_Bronze', '800')''')
P.rep('''assert ("\\n" + DEFAULTS).count("\\nlevels.skill.Farming=" + FARM_LIST + "\\n") == 1 and DEFAULTS.count("\\n".join(FA53_HEAD)) == 1''',
      '''assert ("\\n" + DEFAULTS_056).count("\\nlevels.skill.Farming=" + FARM_LIST + "\\n") == 1 and DEFAULTS.count("\\n".join(FA53_HEAD)) == 1   # 0.4.57: the list itself only in the 0.4.56 file''')

# ---------------------------------------------------------------------------------------------------- 10. P3Mig + CurveP3Mig (PROJECT-RULES 4)
P.rep('''xp56 = pool.makeClass(PKG + ".Xp56Mig")        # 0.4.56: the one-time bridge.bonus.xpSkills + Alchemy, Smithing update of an existing xp.properties
''', '''xp56 = pool.makeClass(PKG + ".Xp56Mig")        # 0.4.56: the one-time bridge.bonus.xpSkills + Alchemy, Smithing update of an existing xp.properties
p3x = pool.makeClass(PKG + ".P3Xp")            # 0.4.57: Balance P3 - catch-up, past-life XP, the own-level factor, xp.skillMult, Combat Echo
p3m = pool.makeClass(PKG + ".P3Mig")           # 0.4.57: the one-time Balance P3 update of an existing xp.properties (spec 6.1)
cp3 = pool.makeClass(PKG + ".CurveP3Mig")      # 0.4.57: the one-time saved-XP move to the P3 level list, levels kept (spec 6.2)
''')
MIG = r'''# ---- P3Mig (0.4.57, PROJECT-RULES section 4; Nc53Mig's reviewed machinery + line removal + one appended block): ONCE on an EXISTING
# xp.properties, setup() right after CurveP3Mig.run (which moved the saved XP first), BEFORE SkillCfg.load. Each P3 key whose LAST entry is a
# one-line entry holding exactly its 0.4.56 default (OLDS, '|' separated) -> NEWS (null = the line is removed: the own lists); any other
# value kept (INFO). Then ONE block in the file's own line ending: HEAD + the ADDK lines the file lacks + the marker. config-history copy
# first (verified), one config-changes.log row per change (Undo; table entries as table[entry], a removal -> (none)), Properties check,
# atomicWrite. A failure = WARN, file untouched, retried next start.
p3m.addField(CtField.make("public static final String MARK_ID = %s;" % json.dumps(P3_MARK_ID), p3m))
p3m.addField(CtField.make("public static final String MARK = %s;" % json.dumps(P3_MARK), p3m))
p3m.addField(CtField.make("public static final String HEAD = %s;" % json.dumps("\n".join(P3_HEAD) + "\n"), p3m))
p3m.addField(CtField.make("public static final String[] KEYS = %s;" % jarr([_e[0] for _e in P3_KEYS]), p3m))
p3m.addField(CtField.make("public static final String[] OLDS = %s;" % jarr([_e[1] for _e in P3_KEYS]), p3m))
p3m.addField(CtField.make("public static final String[] NEWS = new String[] { %s };" % ", ".join("null" if _e[2] is None else json.dumps(_e[2]) for _e in P3_KEYS), p3m))
p3m.addField(CtField.make("public static final String[] ROWK = %s;" % jarr([_e[3] for _e in P3_KEYS]), p3m))
p3m.addField(CtField.make("public static final String[] ADDK = %s;" % jarr([_e[0] for _e in P3_ADD]), p3m))
p3m.addField(CtField.make("public static final String[] ADDV = %s;" % jarr([_e[1] for _e in P3_ADD]), p3m))
p3m.addField(CtField.make("public static final String[] ADDR = new String[] { %s };" % ", ".join("null" if _e[2] is None else json.dumps(_e[2]) for _e in P3_ADD), p3m))
p3m.addField(CtField.make('public static final String WHO = "SkyySkills 0.4.57";', p3m))
p3m.addField(CtField.make('public static final String WHO_LV = "SkyySkills 0.4.57 (see curve-p3.log)";', p3m))
assert all('"' not in _e[1] and "\\" not in _e[1] and (_e[2] is None or ('"' not in _e[2] and "\\" not in _e[2])) for _e in P3_KEYS)
p3m.addMethod(CtNewMethod.make(J14(r"""
public static int idx(String k) {
  if (k == null) return -1;
  for (int i = 0; i < KEYS.length; i++) if (KEYS[i].equals(k)) return i;
  return -1;
}"""), p3m))
p3m.addMethod(CtNewMethod.make(J14(r"""
public static boolean oldHit(int i, String v) {
  if (v == null || i < 0 || i >= OLDS.length) return false;
  String[] o = OLDS[i].split("\\|");
  for (int j = 0; j < o.length; j++) if (o[j].equals(v)) return true;
  return false;
}"""), p3m))
# pure text step. null = nothing to do (the marker); else { new text, String[] { row, old, new }* (change-log rows), boolean[] migrated per KEYS,
# String kept, boolean[] added per ADDK }
p3m.addMethod(CtNewMethod.make(J14(r"""
public static Object[] plan(String text) {
  if (text == null) return null;
  java.util.Properties p = new java.util.Properties();
  try { p.load(new java.io.StringReader(text)); } catch (Throwable t) { return null; }
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  String[] eff = new String[KEYS.length];
  boolean[] multi = new boolean[KEYS.length];
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(MARK_ID) >= 0) return null;
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    int x = idx(@PKG@.CfgFile.key(s));
    if (x >= 0) { eff[x] = @PKG@.CfgFile.value(l, k).trim(); multi[x] = e > k; }
    k = e + 1;
  }
  boolean[] mig = new boolean[KEYS.length];
  StringBuilder kept = new StringBuilder();
  java.util.ArrayList rows = new java.util.ArrayList();
  for (int i = 0; i < KEYS.length; i++) {
    mig[i] = eff[i] != null && !multi[i] && oldHit(i, eff[i]);
    if (mig[i]) { rows.add(ROWK[i]); rows.add(eff[i]); rows.add(NEWS[i] == null ? "(none)" : NEWS[i]); }
    else if (eff[i] != null && !(NEWS[i] != null && eff[i].equals(NEWS[i]) && !multi[i])) {
      String sh = @PKG@.CfgRows.oneLine(p.getProperty(KEYS[i]));
      if (sh.length() > 80) sh = sh.substring(0, 80) + "...";
      kept.append(kept.length() > 0 ? "; " : "").append(KEYS[i] + "=" + sh + " kept (an admin's value) - " + (NEWS[i] == null ? "the 0.4.57 default has no such line (its skill keeps this list and its saved XP is not moved)" : "the 0.4.57 default is " + (NEWS[i].length() > 80 ? NEWS[i].substring(0, 80) + "..." : NEWS[i])));
    }
  }
  String cr = text.indexOf("\r\n") >= 0 ? "\r" : "";
  java.util.ArrayList out = new java.util.ArrayList();
  k = 0;
  while (k < l.size()) {
    String s2 = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s2)) { out.add(raw[k]); k++; continue; }
    int e2 = @PKG@.CfgFile.end(l, k);
    int x2 = idx(@PKG@.CfgFile.key(s2));
    if (x2 >= 0 && mig[x2] && e2 == k && oldHit(x2, @PKG@.CfgFile.value(l, k).trim())) {
      if (NEWS[x2] != null) out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + NEWS[x2] + (raw[k].endsWith("\r") ? "\r" : ""));
    } else {
      for (int q = k; q <= e2; q++) out.add(raw[q]);
    }
    k = e2 + 1;
  }
  StringBuilder sb = new StringBuilder(text.length() + 4096);
  for (int i = 0; i < out.size(); i++) {
    if (i > 0) sb.append('\n');
    sb.append((String) out.get(i));
  }
  String body = sb.toString();
  String nl = cr + "\n";
  String pre = (body.length() == 0 || body.endsWith("\n")) ? "" : nl;
  String last = body.endsWith("\n") ? body.substring(0, body.length() - 1) : body;
  if (last.endsWith("\r")) last = last.substring(0, last.length() - 1);
  int bs = 0;
  for (int i = last.length() - 1; i >= 0 && last.charAt(i) == '\\'; i--) bs++;
  if (bs % 2 == 1) pre = pre + nl;
  StringBuilder blk = new StringBuilder(HEAD.replace("\n", nl));
  boolean[] add = new boolean[ADDK.length];
  for (int i = 0; i < ADDK.length; i++) {
    if (p.getProperty(ADDK[i]) != null) continue;
    add[i] = true;
    blk.append(ADDK[i]).append('=').append(ADDV[i]).append(nl);
    if (ADDR[i] != null) { rows.add(ADDR[i]); rows.add("(none)"); rows.add(ADDV[i]); }
  }
  body = body + pre + blk.toString() + MARK + nl;
  String[] ra = new String[rows.size()];
  for (int i = 0; i < ra.length; i++) ra[i] = (String) rows.get(i);
  return new Object[] { body, ra, mig, kept.toString(), add };
}"""), p3m))
# only the migrated keys may differ (their new value / gone) and only the added keys may be new (exactly their value)
p3m.addMethod(CtNewMethod.make(J14(r"""
public static boolean sameAfter(byte[] old, byte[] nb, Object[] r) {
  try {
    boolean[] mig = (boolean[]) r[2];
    boolean[] add = (boolean[]) r[4];
    java.util.Properties a = new java.util.Properties();
    java.util.Properties n = new java.util.Properties();
    a.load(new java.io.ByteArrayInputStream(old));
    n.load(new java.io.ByteArrayInputStream(nb));
    int drop = 0;
    int plus = 0;
    for (int i = 0; i < KEYS.length; i++) if (mig[i] && NEWS[i] == null) drop++;
    for (int i = 0; i < ADDK.length; i++) if (add[i]) plus++;
    if (n.size() != a.size() - drop + plus) return false;
    java.util.Iterator it = a.stringPropertyNames().iterator();
    while (it.hasNext()) {
      String k = (String) it.next();
      String want = a.getProperty(k);
      int x = idx(k);
      if (x >= 0 && mig[x]) want = NEWS[x];
      String got = n.getProperty(k);
      if (want == null) { if (got != null) return false; continue; }
      if (got == null || !got.equals(want)) return false;
    }
    for (int i = 0; i < ADDK.length; i++) {
      if (!add[i]) continue;
      if (a.getProperty(ADDK[i]) != null || !ADDV[i].equals(n.getProperty(ADDK[i]))) return false;
    }
    return true;
  } catch (Throwable t) { return false; }
}"""), p3m))
p3m.addMethod(CtNewMethod.make(J14(r"""
public static synchronized String run() {
  java.nio.file.Path f = @PKG@.SkillCfg.FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = plan(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    if (!sameAfter(old, data, r)) {
      @PKG@.SkillCfg.warn("xp.properties NOT updated for 0.4.57 (Balance P3): the update would change another setting (the file is used as it is; the next start tries again)");
      return "";
    }
    int fi = @PKG@.HealMig.fileIdx();
    if (fi < 0) return "";
    @PKG@.HealMig.mgKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(fi, old, @PKG@.CfgHist.stamp(), WHO, "before the 0.4.57 Balance P3 update");
    if (!@PKG@.HealMig.mgSaved(fi, old)) {
      @PKG@.SkillCfg.warn("xp.properties NOT updated for 0.4.57 (Balance P3): the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[1];
    int n = 0;
    for (int i = 0; i + 2 < rows.length; i += 3) {
      @PKG@.CfgLog.enqueue(@PKG@.RbCoinMig.logLine(rows[i], rows[i + 1], rows[i + 2]).replace(@PKG@.RbCoinMig.WHO, rows[i].startsWith("levels") ? WHO_LV : WHO));   // fix round: the level rows point at curve-p3.log (fix 2: short - the Changes page clips at 110)
      n++;
    }
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String msg = "xp.properties updated for 0.4.57 (Balance P3: one level list, XP per action x tier, catch-up, past-life XP): " + n + " setting(s) changed (Server Setup -> Changes -> Undo) - the old file is in config-history";
    @PKG@.SkillCfg.info(msg);
    String kept = (String) r[3];
    if (kept.length() > 0) { @PKG@.SkillCfg.info(kept); return msg + "\n" + kept; }
    return msg;
  } catch (Throwable t) {
    @PKG@.SkillCfg.warn("could not update xp.properties for 0.4.57 (Balance P3; the file is used as it is): " + t);
    return "";
  }
}"""), p3m))

# ---- CurveP3Mig (0.4.57, spec 6.2, PROJECT-RULES section 4): ONCE, setup() right after Xp56Mig.run, BEFORE P3Mig (which only runs once this
# is done) and SkillCfg.load. The OLD tables = xp.properties as it is (mirroring SkillCfg.load / SkillLv / setClassTable with the 0.4.56 code
# defaults); the NEW ones = the same file after P3Mig.plan (an admin's own list stays -> that slot is not moved). Every slot whose table
# changes: level Lo + progress p kept (newCum(Lo) + round(p x newNeed(Lo))); XP at / past the profile's cap keeps its ratio to the cap total
# (the cap = min(levels.runCap, table max) + SkyyRebirth's raise (rebirth:fn:cap, waited for up to WAIT_MS) clamped by levels.capMax, at least a
# level floor; no rebirth:fn:cap answer -> the level mapping only). History copy of players/ + level-floors.properties FIRST (read back);
# phase 1 plans every file (a level check per slot: the shown level never moves), phase 2 writes every .p3tmp (fsync), phase 3 renames
# them (curve-p3.properties done.<pkey> after each; a failed rename puts the renamed files back from History). Only <Slot>= values change.
cp3.addField(CtField.make('public static final String NAME = "curve-p3.properties";', cp3))
cp3.addField(CtField.make('public static final String LOGNAME = "curve-p3.log";', cp3))
cp3.addField(CtField.make('public static final String WHO = "SkyySkills 0.4.57";', cp3))
for _d57 in ('public static volatile String LAST = "";', "public static volatile long WAIT_MS = 3000L;", "public static volatile int MOVED = 0;",
             "public static volatile int UNKNOWN = 0;", "public static volatile int FAIL_RENAME = -1;", "public static volatile int SEEN = 0;",
             "public static volatile boolean RB_DATA = false;"):
    cp3.addField(CtField.make(_d57, cp3))
cp3.addMethod(CtNewMethod.make(J14(r"""
public static long[] parseLv(String v) {
  if (v == null || v.trim().length() == 0) return null;
  String[] parts = v.split(",");
  if (parts.length < 1 || parts.length > 100) return null;
  long[] per = new long[parts.length];
  for (int i = 0; i < parts.length; i++) {
    try { per[i] = Long.parseLong(parts[i].trim()); } catch (Throwable t) { return null; }
    if (per[i] <= 0L) return null;
  }
  return per;
}"""), cp3))
cp3.addMethod(CtNewMethod.make(J14(r"""
public static boolean hasPerk(java.util.Properties p) {
  java.util.Enumeration pe = p.propertyNames();
  while (pe.hasMoreElements()) if (String.valueOf(pe.nextElement()).startsWith("perk.")) return true;
  return false;
}"""), cp3))
cp3.addMethod(CtNewMethod.make(J14(r"""
public static java.util.Properties props(String t) throws java.io.IOException {
  java.util.Properties p = new java.util.Properties();
  if (t != null) p.load(new java.io.StringReader(t));
  return p;
}"""), cp3))
# the cumulative table of every slot for one xp.properties (defGen = the code default list, defSame = levels.class.sameAsOthers' code default)
cp3.addMethod(CtNewMethod.make(J14(r"""
public static long[][] tables(java.util.Properties p, long[] defGen, boolean defSame) {
  long[] gen = defGen;
  String lv = p.getProperty("levels");
  if (lv != null && lv.trim().length() > 0) {
    if (@PKG@.SkillCfg.OLD_LEVELS.equals(@PKG@.SkillCfg.squash(lv)) && !hasPerk(p)) gen = defGen;
    else {
      long[] g = parseLv(lv);
      if (g != null) gen = g;
    }
  }
  long[] gc = @PKG@.SkillLv.cum(gen);
  long[] cper = @PKG@.SkillDefs.DEFAULT_CPER;
  long[] c0 = parseLv(p.getProperty("levels.class"));
  if (c0 != null) cper = c0;
  long[] cc = @PKG@.SkillLv.cum(cper);
  long[] ec = gc;
  if (!@PKG@.SkillCfg.bool(p, "levels.class.sameAsOthers", defSame)) {
    ec = new long[cc.length];
    for (int i = 0; i < cc.length; i++) {
      long x = cc[i];
      if (i < gc.length && gc[i] < x) x = gc[i];
      ec[i] = x;
    }
  }
  Object[] own = (Object[]) @PKG@.SkillLv.parseTable(p)[0];
  long[][] t = new long[@PKG@.SkillDefs.N][];
  for (int s = 0; s < t.length; s++) {
    if (@PKG@.SkillDefs.isClass(s)) t[s] = ec;
    else if (s < own.length && own[s] != null) t[s] = (long[]) own[s];
    else t[s] = gc;
  }
  return t;
}"""), cp3))
cp3.addMethod(CtNewMethod.make(J14(r"""
public static long ratio(long x, long a, long b) {
  if (a <= 0L) return x;
  double v = ((double) x / (double) a) * (double) b;
  if (v >= 9.0E15) return 9000000000000000L;
  long n = Math.round(v);
  return n < b ? b : n;
}"""), cp3))
# one total: cap >= 0 = the profile's cap (-1 = unknown)
cp3.addMethod(CtNewMethod.make(J14(r"""
public static long remapX0(long x, long[] oc, long[] nc, int cap) {
  if (x <= 0L) return x;
  int om = oc.length - 1;
  int nm = nc.length - 1;
  int top = om < nm ? om : nm;
  if (top < 1) return x;
  if (cap >= 1) {
    int c = cap < top ? cap : top;
    if (x >= oc[c]) return ratio(x, oc[c], nc[c]);
  }
  int lo = @PKG@.SkillDefs.levelIn(oc, x);
  if (lo >= top) return ratio(x, oc[top], nc[top]);
  double pr = (double) (x - oc[lo]) / (double) (oc[lo + 1] - oc[lo]);
  long nx = nc[lo] + Math.round(pr * (double) (nc[lo + 1] - nc[lo]));
  if (nx >= nc[lo + 1]) nx = nc[lo + 1] - 1L;
  if (nx < nc[lo]) nx = nc[lo];
  return nx;
}"""), cp3))
cp3.addMethod(CtNewMethod.make(J14(r"""
public static long remapX(long x, long[] oc, long[] nc, int cap) {
  long nx = remapX0(x, oc, nc, cap);
  int top = oc.length - 1 < nc.length - 1 ? oc.length - 1 : nc.length - 1;
  if (top >= 1 && nc.length - 1 > top && (cap < 0 || cap > top) && nx >= nc[top + 1]) nx = nc[top + 1] - 1L;   // fix round: an admin's short old list - the shown level stays its max
  return nx;
}"""), cp3))
# the level a player SEES on a table with a cap (-1 = no cap known: the table level)
cp3.addMethod(CtNewMethod.make(J14(r"""
public static int shown(long[] c, long x, int cap) {
  int l = @PKG@.SkillDefs.levelIn(c, x);
  return (cap >= 0 && l > cap) ? cap : l;
}"""), cp3))
# the profile's cap of slot s (-1 = unknown): Exploration = the table max; else min(levels.runCap, max) + SkyyRebirth's raise, levels.capMax, floor
cp3.addMethod(CtNewMethod.make(J14(r"""
public static int capOf(String k, int s, long x, java.util.Properties po, long[] oc, java.util.Properties fl, java.util.function.Function f, long deadline) {
  int max = oc.length - 1;
  if (!@PKG@.SkillDefs.rebirthResets(s)) return max;
  long rc = @PKG@.SkillCfg.lng(po, "levels.runCap", 50L);
  if (rc < 0L) rc = 0L;
  if (rc > 100L) rc = 100L;
  long cm = @PKG@.SkillCfg.lng(po, "levels.capMax", 100L);
  if (cm < 0L) cm = 0L;
  if (cm > 1000L) cm = 1000L;
  int base = (rc <= 0L || rc >= (long) max) ? max : (int) rc;
  long c = (long) base;   // fix round: no SkyyRebirth on this server = no rebirth raise (the base cap is known)
  if (f == null && RB_DATA) return -1;   // fix 2: Skyy_SkyyRebirth exists but rebirth:fn:cap is not published (yet: no load order) -> unknown cap = the level mapping
  if (f != null) {
    Object r = null;
    while (true) {
      try { r = f.apply(new Object[] { k, @PKG@.SkillDefs.NAMES[s], Integer.valueOf(base) }); } catch (Throwable t) { r = null; }
      if (r instanceof Number || System.currentTimeMillis() > deadline) break;
      try { Thread.sleep(25L); } catch (Throwable t) { }
    }
    if (!(r instanceof Number)) return -1;
    long ex = ((Number) r).longValue() - (long) base;
    if (ex < 0L) ex = 0L;
    if (ex > (long) @PKG@.SkillDefs.CAP_EXTRA_MAX) ex = (long) @PKG@.SkillDefs.CAP_EXTRA_MAX;
    c = (long) base + ex;
  }
  if (cm > 0L && c > cm) c = cm;
  String fv = null;
  if (fl != null) fv = fl.getProperty(k + "/" + @PKG@.SkillDefs.NAMES[s]);
  if (fv != null) {
    String[] v = fv.trim().split(",", 3);
    try {
      long flv = Long.parseLong(v[0].trim());
      long tot = v.length > 1 ? Long.parseLong(v[1].trim()) : Long.MAX_VALUE;
      if (x >= tot && flv > c) c = flv;
    } catch (Throwable t) { }
  }
  return (int) c;
}"""), cp3))
# one player file -> the new text (null = nothing changes); throws when a slot would show another level (the whole update stops)
cp3.addMethod(CtNewMethod.make(J14(r"""
public static String remapFile(String k, String text, String pre, long[][] to, long[][] tn, boolean[] ch, java.util.Properties po, java.util.Properties fl, java.util.function.Function f, long deadline, int[] cnt) throws Exception {
  String[] raw = text.split("\n", -1);
  boolean any = false;
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    boolean cr = s0.endsWith("\r");
    String s = cr ? s0.substring(0, s0.length() - 1) : s0;
    String t = s.trim();
    if (t.length() == 0 || t.startsWith("#") || t.startsWith("!")) continue;
    int eq = s.indexOf('=');
    if (eq <= 0) continue;
    String key = s.substring(0, eq);
    if (!key.startsWith(pre)) continue;   // fix round: "" = a player file, "x." = a staged rebirth file (rebirth/<pkey>.rb-<txid>.properties)
    String kn = key.substring(pre.length());
    int sl = -1;
    for (int q = 0; q < @PKG@.SkillDefs.N; q++) if (@PKG@.SkillDefs.NAMES[q].equals(kn)) sl = q;
    if (sl < 0 || !ch[sl]) continue;
    long x = 0L;
    try { x = Long.parseLong(s.substring(eq + 1).trim()); } catch (Throwable e) { continue; }
    if (x <= 0L) continue;
    int cap = capOf(k, sl, x, po, to[sl], fl, f, deadline);
    if (cap < 0 && @PKG@.SkillDefs.rebirthResets(sl)) cnt[1]++;
    long nx = remapX(x, to[sl], tn[sl], cap);
    if (shown(to[sl], x, cap) != shown(tn[sl], nx, cap)) throw new IllegalStateException(k + " " + key + "=" + x + " would show level " + shown(tn[sl], nx, cap) + " instead of " + shown(to[sl], x, cap));
    if (nx == x) continue;
    raw[i] = key + "=" + nx + (cr ? "\r" : "");
    cnt[0]++;
    any = true;
  }
  if (!any) return null;
  StringBuilder sb = new StringBuilder(text.length() + 64);
  for (int i = 0; i < raw.length; i++) {
    if (i > 0) sb.append('\n');
    sb.append(raw[i]);
  }
  return sb.toString();
}"""), cp3))
cp3.addMethod(CtNewMethod.make(J14(r"""
public static boolean copyCheck(java.nio.file.Path from, java.nio.file.Path to) {
  try {
    java.nio.file.Files.createDirectories(to.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Files.copy(from, to, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    return java.util.Arrays.equals(java.nio.file.Files.readAllBytes(from), java.nio.file.Files.readAllBytes(to));
  } catch (Throwable t) { return false; }
}"""), cp3))
cp3.addMethod(CtNewMethod.make(J14(r"""
public static void writeSt(java.nio.file.Path mk, java.util.Properties st) throws java.io.IOException {
  @PKG@.SkillRb.writeProps(mk, st, "SkyySkills 0.4.57 Balance P3 saved XP update (levels kept): done.<profile>=1 per moved file, complete= when finished - do not edit");
}"""), cp3))
cp3.addMethod(CtNewMethod.make(J14(r"""
public static String stamp() {
  return new java.text.SimpleDateFormat("yyyyMMdd-HHmmss").format(new java.util.Date());
}"""), cp3))
# the floors' "XP then" -> newCum(level) of each changed slot (null = nothing changes)
cp3.addMethod(CtNewMethod.make(J14(r"""
public static String remapFloors(String text, long[][] tn, boolean[] ch) {
  String[] raw = text.split("\n", -1);
  boolean any = false;
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    boolean cr = s0.endsWith("\r");
    String s = cr ? s0.substring(0, s0.length() - 1) : s0;
    if (s.trim().length() == 0 || s.trim().startsWith("#")) continue;
    int eq = s.indexOf('=');
    int sl = s.lastIndexOf('/', eq < 0 ? 0 : eq);
    if (eq <= 0 || sl <= 0) continue;
    String nm = s.substring(sl + 1, eq);
    int q = -1;
    for (int j = 0; j < @PKG@.SkillDefs.N; j++) if (@PKG@.SkillDefs.NAMES[j].equals(nm)) q = j;
    if (q < 0 || !ch[q]) continue;
    String[] v = s.substring(eq + 1).trim().split(",", 3);
    if (v.length < 2) continue;
    long lv = -1L;
    try { lv = Long.parseLong(v[0].trim()); } catch (Throwable t) { continue; }
    if (lv < 0L || lv >= (long) tn[q].length) continue;
    raw[i] = s.substring(0, eq + 1) + v[0].trim() + "," + tn[q][(int) lv] + (v.length > 2 ? "," + v[2] : "") + (cr ? "\r" : "");
    any = true;
  }
  if (!any) return null;
  StringBuilder sb = new StringBuilder(text.length() + 64);
  for (int i = 0; i < raw.length; i++) {
    if (i > 0) sb.append('\n');
    sb.append(raw[i]);
  }
  return sb.toString();
}"""), cp3))
# fix round: true while any file is marked moved (then the History copy is the one the moved files came from - keep it)
cp3.addMethod(CtNewMethod.make(J14(r"""
public static boolean anyDone(java.util.Properties st) {
  java.util.Enumeration e = st.propertyNames();
  while (e.hasMoreElements()) if (String.valueOf(e.nextElement()).startsWith("done.")) return true;
  return false;
}"""), cp3))
# fix round: a run that stopped with NO file moved forgets its History copy (players may play on the old list before the next start, so
# the next start takes a fresh copy - a stale copy must never be put back over newer files)
cp3.addMethod(CtNewMethod.make(J14(r"""
public static void forget(java.nio.file.Path mk, java.util.Properties st) {
  if (st == null || anyDone(st) || st.getProperty("history") == null) return;
  st.remove("history");
  st.remove("scanned");
  try { writeSt(mk, st); } catch (Throwable t) { }
}"""), cp3))
# fix round: every file this update moves: { path, marker key, profile key, key prefix, History path } - players/<pkey>.properties and the
# STAGED rebirth files rebirth/<pkey>.rb-<txid>.properties (their x.<Slot> totals are the "XP at prepare" a commit subtracts: same scale)
cp3.addMethod(CtNewMethod.make(J14(r"""
public static java.util.ArrayList items(java.nio.file.Path base) {
  java.util.ArrayList out = new java.util.ArrayList();
  java.nio.file.Path dir = @PKG@.SkillStore.DIR;
  java.io.File[] fs = null;
  if (dir != null) fs = dir.toFile().listFiles();
  if (fs != null) {
    java.util.Arrays.sort(fs);
    for (int i = 0; i < fs.length; i++) {
      String nm = fs[i].getName();
      if (fs[i].isFile() && nm.endsWith(".properties") && nm.length() > 11) out.add(new Object[] { fs[i].toPath(), "done." + nm.substring(0, nm.length() - 11), nm.substring(0, nm.length() - 11), "", "players/" + nm });
    }
  }
  java.io.File[] rs = base.resolve("rebirth").toFile().listFiles();
  if (rs != null) {
    java.util.Arrays.sort(rs);
    for (int i = 0; i < rs.length; i++) {
      String nm = rs[i].getName();
      int ix = nm.indexOf(".rb-");
      if (rs[i].isFile() && ix > 0 && nm.endsWith(".properties")) out.add(new Object[] { rs[i].toPath(), "done.rb/" + nm, nm.substring(0, ix), "x.", "rebirth/" + nm });
    }
  }
  return out;
}"""), cp3))
# fix 2: a run that returns false puts EVERY file marked done back from History (moved by this start, or by an earlier start that crashed -
# nobody has played on them since) and forgets the copy: after a false return no saved XP is on the new list while xp.properties is old
cp3.addMethod(CtNewMethod.make(J14(r"""
public static void rollbackAll(java.nio.file.Path base, java.nio.file.Path mk, java.util.Properties st, java.nio.file.Path hb) {
  if (st == null) return;
  if (hb != null) {
    java.util.Iterator it = new java.util.ArrayList(st.stringPropertyNames()).iterator();
    while (it.hasNext()) {
      String k = (String) it.next();
      if (!k.startsWith("done.")) continue;
      String rest = k.substring(5);
      java.nio.file.Path live = null;
      java.nio.file.Path hp = null;
      if (rest.startsWith("rb/")) { live = base.resolve("rebirth").resolve(rest.substring(3)); hp = hb.resolve("rebirth").resolve(rest.substring(3)); }
      else if (@PKG@.SkillStore.DIR != null) { live = @PKG@.SkillStore.DIR.resolve(rest + ".properties"); hp = hb.resolve("players").resolve(rest + ".properties"); }
      if (hp != null && java.nio.file.Files.exists(hp, new java.nio.file.LinkOption[0]) && copyCheck(hp, live)) st.remove(k);
    }
    try { writeSt(mk, st); } catch (Throwable t) { }
  }
  forget(mk, st);
}"""), cp3))
# fix 2: P3Mig's xp.properties update landed -> xp= in the marker (the guard below then knows a later pre-P3 xp.properties was put back)
cp3.addMethod(CtNewMethod.make(J14(r"""
public static void xpDone(java.nio.file.Path base) {
  try {
    java.nio.file.Path mk = base.resolve(NAME);
    if (!java.nio.file.Files.exists(mk, new java.nio.file.LinkOption[0])) return;
    java.util.Properties st = @PKG@.SkillStore.readProps(mk);
    if (st.getProperty("complete") == null || st.getProperty("xp") != null) return;
    st.setProperty("xp", stamp());
    writeSt(mk, st);
  } catch (Throwable t) { }
}"""), cp3))
# fix 2 (critic: P3Mig failing after the saved XP moved): setup() calls this right after P3Mig.run. xp.properties still without the P3 update ->
# SkillCfg.P3PEND: this start loads the planned 0.4.57 text from memory (levels never read new-scale XP on the old list, no level-up coins);
# the next start updates the file
cp3.addMethod(CtNewMethod.make(J14(r"""
public static void after(java.nio.file.Path base) {
  try {
    java.nio.file.Path f = @PKG@.SkillCfg.FILE;
    boolean landed = true;
    if (f != null && java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) landed = @PKG@.P3Mig.plan(new String(java.nio.file.Files.readAllBytes(f), "ISO-8859-1")) == null;
    @PKG@.SkillCfg.P3PEND = !landed;
    if (landed) { if (base != null) xpDone(base); }
    else @PKG@.SkillCfg.warn("xp.properties still holds the pre-0.4.57 lists (its Balance P3 update did not land) while the saved XP is on the new list: this start uses the 0.4.57 settings from memory; the next start updates the file");
  } catch (Throwable t) {
    @PKG@.SkillCfg.warn("Balance P3: could not check the xp.properties update (" + t + ")");
  }
}"""), cp3))
# fix 2 (critic: a hand restore leaves complete=): complete + xp= (the file WAS updated) but xp.properties is a pre-0.4.57 copy again. Each file
# with a History copy that the move changed: E = equals its copy (put back), N = equals the plan from its copy (still moved), U = neither.
# N -> only xp.properties was put back: 1 (P3Mig updates it again). E only -> everything was put back: 2 = start over (files made after the
# move - no History copy - are on the new list: keep.<marker>). U, no N -> cannot tell: WARN, nothing moved, 0 (the file is used as it is).
cp3.addMethod(CtNewMethod.make(J14(r"""
public static int guard(java.nio.file.Path base, java.nio.file.Path mk, java.util.Properties st) throws Exception {
  if (st.getProperty("xp") == null || st.getProperty("history") == null) return 1;
  java.nio.file.Path f = @PKG@.SkillCfg.FILE;
  if (f == null || !java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return 1;
  String txt = new String(java.nio.file.Files.readAllBytes(f), "ISO-8859-1");
  Object[] r = @PKG@.P3Mig.plan(txt);
  if (r == null) return 1;
  String hist = st.getProperty("history");
  java.nio.file.Path hb = base.resolve(hist);
  java.util.Properties po = props(txt);
  long[][] to = tables(po, @PKG@.SkillDefs.DEFAULT_056, false);
  long[][] tn = tables(props((String) r[0]), @PKG@.SkillDefs.DEFAULT_RUN, true);
  boolean[] ch = new boolean[@PKG@.SkillDefs.N];
  for (int s = 0; s < ch.length; s++) ch[s] = !java.util.Arrays.equals(to[s], tn[s]);
  java.nio.file.Path fl = base.resolve(@PKG@.LvFloor.NAME);
  java.util.Properties flp = java.nio.file.Files.exists(fl, new java.nio.file.LinkOption[0]) ? @PKG@.SkillStore.readProps(fl) : new java.util.Properties();
  Object fo = @PKG@.SkillStore.bridge().get("rebirth:fn:cap");
  java.util.function.Function fn = null;
  if (fo instanceof java.util.function.Function) fn = (java.util.function.Function) fo;
  long deadline = System.currentTimeMillis() + WAIT_MS;
  java.util.ArrayList files = items(base);
  java.util.ArrayList fresh = new java.util.ArrayList();
  int e = 0;
  int n = 0;
  int u = 0;
  for (int i = 0; i < files.size(); i++) {
    Object[] it = (Object[]) files.get(i);
    java.nio.file.Path hp = hb.resolve((String) it[4]);
    if (!java.nio.file.Files.exists(hp, new java.nio.file.LinkOption[0])) { fresh.add(it[1]); continue; }
    byte[] hbs = java.nio.file.Files.readAllBytes(hp);
    String h2 = null;
    try { h2 = remapFile((String) it[2], new String(hbs, "ISO-8859-1"), (String) it[3], to, tn, ch, po, flp, fn, deadline, new int[2]); } catch (Throwable x) { u++; continue; }
    if (h2 == null) continue;
    byte[] cb = java.nio.file.Files.readAllBytes((java.nio.file.Path) it[0]);
    if (java.util.Arrays.equals(cb, hbs)) e++;
    else if (h2.equals(new String(cb, "ISO-8859-1"))) n++;
    else u++;
  }
  if (n > 0) {
    @PKG@.SkillCfg.info("Balance P3: xp.properties is a pre-0.4.57 copy again but the saved XP is still on the new list (" + n + " file(s)) - the file is updated again");
    return 1;
  }
  if (e == 0 && u == 0) return 1;
  if (u > 0) {
    @PKG@.SkillCfg.warn("Balance P3: xp.properties is a pre-0.4.57 copy again and " + u + " profile file(s) changed since the saved XP update - cannot tell which list their XP is on: nothing moved, xp.properties used as it is. Files put back from " + hist + ": delete " + NAME + " and restart (the XP is moved again); else put back the 0.4.57 xp.properties from config-history");
    return 0;
  }
  java.util.Properties nst = new java.util.Properties();
  nst.setProperty("rerun", hist + " put back " + stamp());
  for (int i = 0; i < fresh.size(); i++) nst.setProperty("keep." + (String) fresh.get(i), "1");
  writeSt(mk, nst);
  @PKG@.SkillCfg.info("Balance P3: xp.properties and " + e + " profile file(s) were put back from " + hist + " - the saved XP update runs again (" + fresh.size() + " newer file(s) kept as they are)");
  return 2;
}"""), cp3))
# true = done (now or before) / nothing to do -> P3Mig may update xp.properties; false = not done (WARN; nothing changed; next start retries)
# fix round: + the staged rebirth files; a file whose move a crash left unmarked is recognised (it equals the plan made from its History copy)
# and never moved twice; a run that stops before any file moved forgets its History copy (the next start copies afresh)
cp3.addMethod(CtNewMethod.make(J14(r"""
public static synchronized boolean run(java.nio.file.Path base) {
  LAST = "";
  MOVED = 0;
  UNKNOWN = 0;
  SEEN = 0;
  if (base == null) return true;
  java.nio.file.Path par = base.toAbsolutePath().getParent();
  RB_DATA = par != null && java.nio.file.Files.isDirectory(par.resolve("Skyy_SkyyRebirth"), new java.nio.file.LinkOption[0]);   // fix 2
  java.nio.file.Path mk = base.resolve(NAME);
  java.util.ArrayList tmps = new java.util.ArrayList();
  java.util.ArrayList renamed = new java.util.ArrayList();
  java.util.Properties st = null;
  java.nio.file.Path hb = null;
  try {
    java.util.Properties st0 = new java.util.Properties();
    if (java.nio.file.Files.exists(mk, new java.nio.file.LinkOption[0])) st0 = @PKG@.SkillStore.readProps(mk);
    st = st0;
    if (st.getProperty("complete") != null) {
      int g = guard(base, mk, st);   // fix 2: a pre-0.4.57 xp.properties put back after the move
      if (g == 1) return true;
      if (g == 0) return false;
      st = @PKG@.SkillStore.readProps(mk);   // g == 2: everything was put back - start over with guard()'s new marker (keep. lines)
    }
    java.nio.file.Path f = @PKG@.SkillCfg.FILE;
    byte[] old = null;
    if (f != null && java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) old = java.nio.file.Files.readAllBytes(f);
    String txt = old == null ? "" : new String(old, "ISO-8859-1");
    String nt = txt;
    if (old == null) nt = @PKG@.SkillCfg.DEFAULTS;
    else {
      Object[] r = @PKG@.P3Mig.plan(txt);
      if (r != null) {
        nt = (String) r[0];
        if (!@PKG@.P3Mig.sameAfter(old, nt.getBytes("ISO-8859-1"), r)) {
          @PKG@.SkillCfg.warn("Balance P3 saved XP update NOT done: the xp.properties update would change another setting - nothing changed (the next start tries again)");
          forget(mk, st);
          return false;
        }
      }
    }
    java.util.Properties po = props(txt);
    long[][] to = tables(po, @PKG@.SkillDefs.DEFAULT_056, false);
    long[][] tn = tables(props(nt), @PKG@.SkillDefs.DEFAULT_RUN, true);
    boolean[] ch = new boolean[@PKG@.SkillDefs.N];
    int nch = 0;
    for (int s = 0; s < ch.length; s++) if (!java.util.Arrays.equals(to[s], tn[s])) { ch[s] = true; nch++; }
    java.util.ArrayList files = items(base);
    java.nio.file.Path fl = base.resolve(@PKG@.LvFloor.NAME);
    boolean hasFl = java.nio.file.Files.exists(fl, new java.nio.file.LinkOption[0]);
    if (nch == 0 || (files.isEmpty() && !hasFl)) {
      st.setProperty("complete", stamp());
      st.setProperty("note", nch == 0 ? "no level list changes" : "no player files");
      writeSt(mk, st);
      return true;
    }
    String hist = st.getProperty("history");
    if (hist == null) {
      String sp = stamp();
      java.nio.file.Path hd = base.resolve("history").resolve("curve-p3").resolve(sp);
      int nn = 1;
      while (java.nio.file.Files.exists(hd, new java.nio.file.LinkOption[0])) { nn++; hd = base.resolve("history").resolve("curve-p3").resolve(sp + "-" + nn); }
      boolean ok = true;
      for (int i = 0; i < files.size() && ok; i++) {
        Object[] it = (Object[]) files.get(i);
        ok = copyCheck((java.nio.file.Path) it[0], hd.resolve((String) it[4]));
      }
      if (ok && hasFl) ok = copyCheck(fl, hd.resolve(@PKG@.LvFloor.NAME));
      if (!ok) {
        @PKG@.SkillCfg.warn("Balance P3 saved XP update NOT done: the player files could not be copied to " + hd + " - nothing changed, xp.properties not updated (the next start tries again)");
        return false;
      }
      hist = "history/curve-p3/" + hd.getFileName().toString();
      st.setProperty("history", hist);
      st.setProperty("scanned", sp);
      writeSt(mk, st);
    }
    hb = base.resolve(hist);
    java.util.Properties flp = hasFl ? @PKG@.SkillStore.readProps(fl) : new java.util.Properties();
    Object fo = @PKG@.SkillStore.bridge().get("rebirth:fn:cap");
    java.util.function.Function fn = null;
    if (fo instanceof java.util.function.Function) fn = (java.util.function.Function) fo;
    long deadline = System.currentTimeMillis() + WAIT_MS;
    int[] cnt = new int[2];
    java.util.ArrayList plan = new java.util.ArrayList();
    for (int i = 0; i < files.size(); i++) {
      Object[] it = (Object[]) files.get(i);
      java.nio.file.Path fp = (java.nio.file.Path) it[0];
      String mkey = (String) it[1];
      String k = (String) it[2];
      String pre = (String) it[3];
      if (st.getProperty(mkey) != null || st.getProperty("keep." + mkey) != null) continue;   // fix 2: keep. = made after an earlier move (guard)
      byte[] cb = java.nio.file.Files.readAllBytes(fp);
      String t = new String(cb, "ISO-8859-1");
      java.nio.file.Path hp = hb.resolve((String) it[4]);
      if (!java.nio.file.Files.exists(hp, new java.nio.file.LinkOption[0])) {
        if (!copyCheck(fp, hp)) throw new java.io.IOException("could not copy " + fp.getFileName() + " to " + hist);
      } else {
        byte[] hbs = java.nio.file.Files.readAllBytes(hp);
        if (!java.util.Arrays.equals(cb, hbs)) {
          String h2 = remapFile(k, new String(hbs, "ISO-8859-1"), pre, to, tn, ch, po, flp, fn, deadline, new int[2]);
          if (h2 != null && h2.equals(t)) {
            st.setProperty(mkey, "1");
            writeSt(mk, st);
            SEEN++;
            continue;
          }
          throw new IllegalStateException(fp.getFileName() + " differs from its copy in " + hist + " and is not the planned new file (fix 2: the files already moved are put back, the next start copies afresh)");
        }
      }
      String n2 = remapFile(k, t, pre, to, tn, ch, po, flp, fn, deadline, cnt);
      plan.add(new Object[] { fp, mkey, n2, it[4] });
    }
    for (int i = 0; i < plan.size(); i++) {
      Object[] e = (Object[]) plan.get(i);
      if (e[2] == null) continue;
      java.nio.file.Path p = (java.nio.file.Path) e[0];
      java.nio.file.Path tmp = p.resolveSibling(p.getFileName().toString() + ".p3tmp");
      java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
      tmps.add(tmp);
      try { out.write(((String) e[2]).getBytes("ISO-8859-1")); out.flush(); out.getFD().sync(); } finally { out.close(); }
    }
    int moved = 0;
    for (int i = 0; i < plan.size(); i++) {
      Object[] e = (Object[]) plan.get(i);
      java.nio.file.Path p = (java.nio.file.Path) e[0];
      if (e[2] != null) {
        try {
          if (FAIL_RENAME == i) throw new java.io.IOException("test: rename " + i + " fails");
          @PKG@.SkillStore.moveRetry(p.resolveSibling(p.getFileName().toString() + ".p3tmp"), p);
        } catch (Throwable x) {
          renamed.clear();
          for (int j = 0; j < tmps.size(); j++) try { java.nio.file.Files.deleteIfExists((java.nio.file.Path) tmps.get(j)); } catch (Throwable y) { }
          rollbackAll(base, mk, st, hb);   // fix 2: every done file (moved or unchanged, this start or a crashed one) back + the copy forgotten
          @PKG@.SkillCfg.warn("Balance P3 saved XP update NOT done: could not replace " + p.getFileName() + " (" + x + ") - the files already moved were put back from " + hist + "; xp.properties not updated (the next start tries again)");
          return false;
        }
        renamed.add(e);
        moved++;
      }
      st.setProperty((String) e[1], "1");
      writeSt(mk, st);
    }
    tmps.clear();
    if (hasFl && st.getProperty("floors.done") == null) {
      String ft = new String(java.nio.file.Files.readAllBytes(fl), "ISO-8859-1");
      String fn2 = remapFloors(ft, tn, ch);
      if (fn2 != null) @PKG@.CfgRows.atomicWrite(fl, fn2.getBytes("ISO-8859-1"));
      st.setProperty("floors.done", "1");
    }
    st.setProperty("complete", stamp());
    writeSt(mk, st);
    MOVED = moved;
    UNKNOWN = cnt[1];
    String msg = "Balance P3: " + moved + " profile file(s) moved to the new level list, levels kept (" + cnt[0] + " skill total(s)" + (cnt[1] > 0 ? "; " + cnt[1] + " without a known rebirth cap - moved by level" : "") + (SEEN > 0 ? "; " + SEEN + " moved by an earlier start" : "") + ") - the old files are in " + hist;
    String line = new java.text.SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss").format(new java.util.Date()) + "\t" + WHO + "\t" + msg + "\tUndo: stop the server, copy " + hist + "/players/* back over players/ (and " + hist + "/rebirth/* over rebirth/ and " + hist + "/" + @PKG@.LvFloor.NAME + " if there), then Server Setup -> Changes -> Undo the 0.4.57 rows or roll SkyySkills back to 0.4.56 (never Undo the levels rows alone), and delete " + NAME + " (a later 0.4.57 then moves the XP again). Never restore a rebirth-backup/ folder made before this update: it holds the old XP scale\n";
    java.nio.file.Files.write(base.resolve(LOGNAME), line.getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });
    @PKG@.SkillCfg.info(msg + " (curve-p3.log has the Undo)");
    LAST = msg;
    try { @PKG@.SkillStore.io(5, null); } catch (Throwable t) { }
    return true;
  } catch (Throwable t) {
    for (int j = 0; j < tmps.size(); j++) try { java.nio.file.Files.deleteIfExists((java.nio.file.Path) tmps.get(j)); } catch (Throwable y) { }
    if (st != null && st.getProperty("complete") == null) rollbackAll(base, mk, st, hb);   // fix 2: no moved file left behind on a false return
    @PKG@.SkillCfg.warn("Balance P3 saved XP update NOT done (" + t + ") - xp.properties not updated (the next start tries again)");
    return false;
  }
}"""), cp3))

'''
P.rep('''# ---- Zo49Mig (0.4.49, PROJECT-RULES section 4;''', MIG + '''# ---- Zo49Mig (0.4.49, PROJECT-RULES section 4;''')
P.rep('''  {PKG}.Xp56Mig.run();        // 0.4.56: untouched bridge.bonus.xpSkills -> + Alchemy, Smithing (Skill Trees 3 Wisdom rows), once; History first
''', '''  {PKG}.Xp56Mig.run();        // 0.4.56: untouched bridge.bonus.xpSkills -> + Alchemy, Smithing (Skill Trees 3 Wisdom rows), once; History first
  if ({PKG}.CurveP3Mig.run(base)) {{ {PKG}.P3Mig.run(); {PKG}.CurveP3Mig.after(base); }}   // 0.4.57 Balance P3: saved XP (levels kept) FIRST, then xp.properties; once each; after = in-memory lists if the file update failed
''')
P.rep('''assert DEFAULTS.count(XP56_MARK_ID) == 1 and _dp.get("bridge.bonus.xpSkills") == XP56_NEW   # 0.4.56
''', '''assert DEFAULTS.count(XP56_MARK_ID) == 1 and _dp.get("bridge.bonus.xpSkills") == XP56_NEW   # 0.4.56
assert DEFAULTS.count(P3_MARK_ID) == 1 and DEFAULTS.endswith(P3_BLOCK) and _dp.get("levels.class.sameAsOthers") == "true"   # 0.4.57
''')
P.rep("rbcm, snd39, rbs39, pd44, fm48, zo49, fl50, mn52, nc53, fa53, en54, xp56, sv3, lvf,",
      "rbcm, snd39, rbs39, pd44, fm48, zo49, fl50, mn52, nc53, fa53, en54, xp56, sv3, p3x, p3m, cp3, lvf,")

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
P.finish()
print("wrote SkyySkills/build_skyyskills_0.4.57.py (%d changes)" % len(P.changes))
