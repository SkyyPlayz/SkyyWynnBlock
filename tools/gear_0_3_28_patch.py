"""Derive SkyyGear/build_skyygear_0.3.28.py from the LIVE 0.3.27 (build_skyygear_0.3.27.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_3_27_patch.py). Edit THIS file, never the generated script; every anchor is asserted and every change is undone at the end to
prove nothing else changed. Run:
    python tools/gear_0_3_28_patch.py      then      python SkyyGear/build_skyygear_0.3.28.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.3.28.py   (the 0.3.27 chain on this jar + S328 + H328; --static needs no jar)

0.3.28 (2026-10-18) = ONE FORTUNE RATE ON EVERY LIFELONG TOOL, NO FORTUNE CAP. Skyy (docs/answered/gear.md 2026-10-18): "Yes - make Fortune +10 a
level on every tool (hatchet, Harvester, pole too), same as the pickaxe." + "so the way it works is, there isnt a cap on any of the fortunes.
100%= guaranteed double drop. 150%= 50% triple drop. and so on. so 300%= guaranteed 4 drops" + "okay, lets reduce it from 10 per point to 3. so
you cant get over 100% till you reach T4".
  1. THE RATE: every lifelong tool's Fortune line gives +3 Fortune (+3 %) a level - the pickaxe (lifelong.perkFortune.mining 10 -> 3, and so the
     multitool's pickaxe set) and the hatchet / Harvester / hoe / pole (lifelong.perkFortune 2 -> 3, and so the multitool's hatchet set; the pole's
     line = its double catch %). The watering can has no Fortune line. Level caps unchanged (lifelong.lineCapPerTier 10 x (internal tier + 1);
     the ladder's top step uncapped): Crude 10 levels = 30, Copper (T1) 20 = 60, Iron (T2) 30 = 90, Bronze (T3) 33 = 99 (item 6), Thorium (T4) 40 = 120, Lead /
     Dusk / Cobalt (T5-T7) 50 = 150, Chromium / Azurvane / Adamantite (T8-T10) 60 = 180, Slag / Cinder / Mithril (T11-T13) 70 = 210, Titanium
     (T14) 80 = 240, Lumen (the top step) uncapped. Levels already bought stay; only the value a level changes (no refund).
     So the line passes 100 % only from T4 Thorium (the start of Zone 2; Skyy "at the start of zone 2").
  2. NO FORTUNE CAP: tool.fortune.cap stays 0 (= none, 0.3.17); armor.fortune.cap 15 -> 100 (the Mining / Foraging / Farming armor
     Fortune tops out near 15, so 100 = no real cap and stays inside 0.3.27's 0-100 range; 0 now also parses as NO cap, like tool.fortune.cap;
     a hand-set 0 is a hand edit - kept + noted by migrate0328); lifelong.perkFortune's row max 25 -> 100 (= the mining row's). Gear's own extra-drop
     roll (the sickle's extra Plant Fiber / Sticks, GearSickle.roll) = floor(F / 100) + a (F mod 100) % chance of one more, with no 5-drop cap
     (only the 100-extra safety stop of SkyySkills' perk.fortuneGuard).
  3. TEXTS: the tool tooltip ("Foraging Fortune +150% = 2 drops + 50% for a 3rd (log)") and the Upgrade page's "Next:" line ("Next: +102% =
     2 drops + 2% for a 3rd, 3 pts") say what the % gives (GearTool.fdrops); the row header keeps the short "+99% Mining Fortune" (366 px). The sickle rows' help says no cap.
  4. BETA BUG 12 (research/Beta-Bugs-Triage-2026-10-17.md; Skyy "they shouldn't decide what the item is until it's identified"): a NEW
     random weapon bag (a mob / chest roll with no forced type, or a dropped vanilla weapon's bag) carries grp=w: its name / tooltip / the
     Identify + Anvil panels say "Unidentified Weapon"; at identify (GearUnid.open) the type is picked among every weapon type with a
     candidate in the bag's level range, with the IDENTIFIER's class lean (loot.classLean %, class:weapons). The stored mys (the drop-time
     pick) stays as the fallback: old bags, Untiered / Mythic boss / forced-type bags and armor bags are unchanged; 0.3.27 or the new row
     unid.typeAtIdentify=false open a grp bag as its stored type. Re-identify keeps the type the identify picked.
  5. BETA BUG 17 ("Wooden Hoe" in the Anvil upgrade list): with harvester.only on, plain Tool_Hoe_* / Tool_Sickle_* (not the
     Tool_Sickle_Harvester_* ids) are never Upgrade rows (GearUp.rows: the Anvil Upgrade list, the Upgrade tab, the hub tier-up finder),
     and a lifelong hoe / sickle waiting to merge gets no "not on you" row.
  6. THE T3 FORTUNE CAP (Skyy "so you cant get over 100% till you reach T4"): the FORTUNE line of an internal-tier-3 tool that is not Thorium
     (Bronze, T3) caps at 33 levels (lifelong.lineCapPerTier x 3 + 30 %; 99 %) - GearLL.lineCapP, used where a line's level works / is bought /
     is explained (perkEff, capWhy, the Upgrade page). Its other lines keep 40; Thorium keeps 40 everywhere. A Bronze tool that already holds
     34-40 Fortune levels keeps them saved; only 33 work until it tiers up to Thorium.
  ONE-TIME UPDATE migrate0328 (after migrate0327; the migrate0327 machinery, number compare h7Old): every ONE-LINE entry still holding its 0.3.27
  default is rewritten (lifelong.perkFortune 2 -> 3, lifelong.perkFortune.mining 10 -> 3, armor.fortune.cap 15 -> 100); a hand-edited value is kept +
  noted; History copy verified first, one change-log row per change (Undo in Server Setup), the run-once marker (a fresh 0.3.28 file carries it),
  every other byte and line ending kept. A row the file lacks takes the new default (no change-log row).
Commands: none new. Classes: none new. Config: + unid.typeAtIdentify (absent = on); defaults lifelong.perkFortune 3, lifelong.perkFortune.mining 3,
armor.fortune.cap 100 (migrate0328). SAVED DATA: new weapon bags get one extra field grp=w (older versions ignore it).
ROLLBACK 0.3.28 -> 0.3.27: item-clean. 0.3.27 reads the migrated rows as they are (Fortune 3 / 3 a level, armor cap 100 = inside its 0-100
range; grp=w bags open as their stored type; Bronze Fortune works to 40 again). Only a HAND-SET armor.fortune.cap=0 means "no armor Fortune" to
0.3.27 - set it to 100 first. Undo the migrate0328 rows in Server Setup's change log for the 0.3.27 numbers (2 / 10 / 15).
"""
import os
import sys
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.27.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.28.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.27"' in s and "GENERATED by tools/gear_0_3_27_patch.py" in s, "not the generated 0.3.27 script"
assert "H28_" not in s and "migrate0328" not in s and "fdrops(" not in s
SYS0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
MK0 = s.count(' = mk("')
CHANGES = []


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)
    CHANGES.append((new, old, count))


def after(anchor, text):
    rep(anchor, anchor + text)


def before(anchor, text):
    rep(anchor, text + anchor)


_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyGear") != "0.3.27":
    print("NOTE: tools/deploy_set.py SET pins SkyyGear %s, this patch derives from 0.3.27" % _set.get("SkyyGear"))

HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.3.28 (2026-10-18)"):].rstrip() + "\n"

# ================================================================================================================ docstring + version
rep('''"""SkyyGear 0.3.27 - build script (javassist via jpype). GENERATED by tools/gear_0_3_27_patch.py from the LIVE 0.3.26 (itself GENERATED by
tools/gear_0_3_26_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.27.py -> SkyyGear/SkyyGear-0.3.27.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.27.py. Needs Quirk's private art (../SkyWynn-PRIVATE-art/mining-armor and
../SkyWynn-PRIVATE-art/metal-art/Tools-PRIVATE).

''', '''"""SkyyGear 0.3.28 - build script (javassist via jpype). GENERATED by tools/gear_0_3_28_patch.py from the LIVE 0.3.27 (itself GENERATED by
tools/gear_0_3_27_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.28.py -> SkyyGear/SkyyGear-0.3.28.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.28.py. Needs Quirk's private art (../SkyWynn-PRIVATE-art/mining-armor and
../SkyWynn-PRIVATE-art/metal-art/Tools-PRIVATE).

''' + NOTE + '''
--- 0.3.27 notes ---
''')
rep('VERSION = "0.3.27"\n', 'VERSION = "0.3.28"\n')

# ================================================================================================================ 1 + 2: the rows
PF_OLD, PF_NEW = "2", "3"          # lifelong.perkFortune (hatchet / Harvester / hoe / pole / multitool hatchet set)
PFM_OLD, PFM_NEW = "10", "3"       # lifelong.perkFortune.mining (pickaxe / multitool pickaxe set)
AFC_OLD, AFC_NEW = "15", "100"     # armor.fortune.cap (100 = no real cap; 0 also = no cap from 0.3.28)
rep('''    ("lifelong.perkFortune", "Fortune per perk level", "lifelong", "dec", "2", "0", "25", "", "", "live,danger",
     "Fortune per level of a hatchet, Harvester or pole (100 = sure drop)." + PH, "field:GearCfg.LL_PFORT"),''',
    '''    ("lifelong.perkFortune", "Fortune per perk level", "lifelong", "dec", "3", "0", "100", "", "", "live,danger",
     "Fortune per level: hatchet, Harvester, pole (100 = sure extra drop)." + PH, "field:GearCfg.LL_PFORT"),''')
rep('''    ("lifelong.perkFortune.mining", "Mining Fortune per pickaxe level", "lifelong", "dec", "10", "0", "100", "", "", "live,danger",''',
    '''    ("lifelong.perkFortune.mining", "Mining Fortune per pickaxe level", "lifelong", "dec", "3", "0", "100", "", "", "live,danger",''')
rep('''    ("armor.fortune.cap", "Most Fortune from armor", "garmor", "dec", "15", "0", "100", "", "", "live,danger",
     "Mining Fortune from worn armor (pieces + full set) stops here (Onyxium full set = 15).", "field:GearCfg.GM_FCAP"),''',
    '''    ("armor.fortune.cap", "Most Fortune from armor", "garmor", "dec", "100", "0", "100000", "", "", "live,danger",
     "Most Fortune worn armor gives (pieces + full set); 0 = no cap (Onyxium full set = 15).", "field:GearCfg.GM_FCAP"),''')
rep('''     "Chance per plant a sickle cuts for 1 extra Plant Fiber (150 = 1 sure + a 50% chance of 2; max 5).", "field:GearCfg.SICKLE_FIB"),''',
    '''     "Chance per plant a sickle cuts for 1 extra Plant Fiber (150 = 1 sure + a 50% chance of 2; no cap).", "field:GearCfg.SICKLE_FIB"),''')
rep('''     "Chance per bush / bramble a sickle cuts for 1 extra Stick (sickle.stickPlants; at most 5 per plant).", "field:GearCfg.SICKLE_STC"),''',
    '''     "Chance per bush / bramble a sickle cuts for 1 extra Stick (stickPlants; 150 = 1 sure + 50% of 2).", "field:GearCfg.SICKLE_STC"),''')
rep('''("LL_PFORT", "double", "2.0")''', '''("LL_PFORT", "double", "3.0")''')
rep('''("LL_PFORTM", "double", "10.0")''', '''("LL_PFORTM", "double", "3.0")''')
rep('''("GM_FCAP", "double", repr(MINE_FCAP))''', '''("GM_FCAP", "double", "100.0")''')
rep('''  LL_PFORT = pdec(p, "lifelong.perkFortune", 2.0, 0.0, 25.0);          // 0.3.17 (was 1)''',
    '''  LL_PFORT = pdec(p, "lifelong.perkFortune", 3.0, 0.0, 100.0);          // 0.3.28 (0.3.17 - 0.3.27: 2, max 25)''')
rep('''  LL_PFORTM = pdec(p, "lifelong.perkFortune.mining", 10.0, 0.0, 100.0);''',
    '''  LL_PFORTM = pdec(p, "lifelong.perkFortune.mining", 3.0, 0.0, 100.0);          // 0.3.28 (0.3.22 - 0.3.27: 10)''')
rep('''  GM_FCAP = pdec(p, "armor.fortune.cap", 15.0, 0.0, 100.0);''',
    '''  GM_FCAP = pdec(p, "armor.fortune.cap", 100.0, 0.0, 100000.0);          // 0.3.28: 100 (0.3.27: 15); 0 = no cap (fcapA)''')

rep('''assert [_dp.get(_k) for _k in G322_ROWK] == [ORE_TIERS_DEF, "0.5", TIER_POW_DEF, "10", ORE_FLOOR_DEF]''',
    '''assert [_dp.get(_k) for _k in G322_ROWK] == [ORE_TIERS_DEF, "0.5", TIER_POW_DEF, "3", ORE_FLOOR_DEF]          # 0.3.28: Mining Fortune 10 -> 3''')
# the armor Fortune cap in force (0 = none), the GearCfg.fcap() shape
after('''M(gcf, "public static double fcap() { double c = TOOL_FCAP; return c > 0.0 ? c : 1.0E9; }")
''', '''# 0.3.28: the armor Fortune cap in force - armor.fortune.cap 0 = no cap (the new default 100 is no real cap either) (Skyy 2026-10-18 "there isnt a cap on any of the fortunes")
M(gcf, "public static double fcapA() { double c = GM_FCAP; return c > 0.0 ? c : 1.0E9; }")
''')
rep('''  double fc = @PKG@.GearCfg.GM_FCAP;
''', '''  double fc = @PKG@.GearCfg.fcapA();          // 0.3.28: 0 = no cap
''', 2)
rep('''(armor Fortune up to " + num(@PKG@.GearCfg.GM_FCAP) + ",''',
    '''(armor Fortune " + (@PKG@.GearCfg.GM_FCAP > 0.0 ? "up to " + num(@PKG@.GearCfg.GM_FCAP) : "with no cap") + ",''')

# the sickle's own roll: floor(F / 100) + (F mod 100) % of one more, no 5-drop cap (only the 100-extra safety stop)
rep('''  double x = pct / 100.0;
  if (x > 5.0) x = 5.0;
  int w = (int) Math.floor(x);''', '''  double x = pct / 100.0;
  if (x > 100.0) x = 100.0;          // 0.3.28: no Fortune cap - only the safety stop (SkyySkills perk.fortuneGuard's 100 extra drops)
  int w = (int) Math.floor(x);''')

# ================================================================================================================ 3: the texts
before('''# 0.2.18: one power line of a multitool ("Mining Power -15%: 3 hits per stone (plain pickaxe 3)"); the sign is shown (below x1 = slower)
''', r'''# 0.3.28: what a Fortune % gives (Skyy 2026-10-18 "100%= guaranteed double drop. 150%= 50% triple drop"): 150 -> "2 drops + 50% for a 3rd"
M(gtool, r"""
public static String ordw(long n) {
  long h = n % 100L;
  if (h >= 11L && h <= 13L) return n + "th";
  long d = n % 10L;
  if (d == 1L) return n + "st";
  if (d == 2L) return n + "nd";
  if (d == 3L) return n + "rd";
  return n + "th";
}""")
M(gtool, r"""
public static String fdrops(double f) {
  if (Double.isNaN(f) || !(f > 0.0)) return "1 drop";
  double t = Math.round(f * 10.0) / 10.0;
  long n = (long) Math.floor(t / 100.0);
  double r = Math.round((t - 100.0 * (double) n) * 10.0) / 10.0;
  if (r >= 100.0) { n = n + 1L; r = 0.0; }
  if (r < 0.0) r = 0.0;
  String o = (n + 1L) + (n == 0L ? " drop" : " drops");
  if (r > 0.0) o = o + " + " + @PKG@.Gear.fnum(r) + "% for a " + ordw(n + 2L);
  return o;
}""")
''')
rep('''  txt.add("Mining Fortune +" + @PKG@.Gear.fnum(fm) + " (" + @PKG@.Gear.fnum(fm) + "% extra rock / ore chance)");''',
    '''  txt.add("Mining Fortune +" + @PKG@.Gear.fnum(fm) + "% = " + fdrops(fm) + " (rock / ore)");          // 0.3.28''')
rep('''  txt.add("Foraging Fortune +" + @PKG@.Gear.fnum(fc) + " (" + @PKG@.Gear.fnum(fc) + "% extra log chance)");''',
    '''  txt.add("Foraging Fortune +" + @PKG@.Gear.fnum(fc) + "% = " + fdrops(fc) + " (log)");          // 0.3.28''')
rep('''  txt.add(sk + " Fortune +" + @PKG@.Gear.fnum(fo) + " (" + @PKG@.Gear.fnum(fo) + "% extra " + what + " chance)");''',
    '''  txt.add(sk + " Fortune +" + @PKG@.Gear.fnum(fo) + "% = " + fdrops(fo) + " (" + what + ")");          // 0.3.28''')
rep('''  if (p == 1) return "+" + @PKG@.Gear.fnum((double) lv * @PKG@.GearLL.pfort(k)) + " " + @PKG@.GearLL.KSKILL[k] + " Fortune";          // 0.3.22: pickaxe = the Mining row''',
    '''  if (p == 1) return "+" + @PKG@.Gear.fnum((double) lv * @PKG@.GearLL.pfort(k)) + "% " + @PKG@.GearLL.KSKILL[k] + " Fortune";          // 0.3.28: a % (0.3.22: pickaxe = the Mining row)''')
# the drop math only on the row's D line (the N header label is 366 px - review F1): "Next: +102% = 2 drops + 2% for a 3rd, 3 pts"
rep('''  else { nx = "Next: " + effect(k, p, lv + 1) + " for " + cost + " point" + (cost == 1 ? "" : "s"); can = fr >= cost; }''',
    '''  else if (p == 1 && k != @PKG@.GearLL.POLE && k != @PKG@.GearLL.CAN) { double fv = (double) (lv + 1) * @PKG@.GearLL.pfort(k); nx = "Next: +" + @PKG@.Gear.fnum(fv) + "% = " + @PKG@.GearTool.fdrops(fv) + ", " + cost + " pt" + (cost == 1 ? "" : "s"); can = fr >= cost; }          // 0.3.28: what the next Fortune level gives
  else { nx = "Next: " + effect(k, p, lv + 1) + " for " + cost + " point" + (cost == 1 ? "" : "s"); can = fr >= cost; }''')

# ================================================================================================================ migrate0328
after('''assert all(32 <= ord(_c) < 127 for _c in G327_HEAD) and "=" not in G327_HEAD
''', '''# 0.3.28 FORTUNE: the migrate0328 marker block in a fresh file (no new row)
G328_HEAD = "# ---- Fortune: +3 a level on every lifelong tool, no Fortune cap (SkyyGear 0.3.28) ----"
assert all(32 <= ord(_c) < 127 for _c in G328_HEAD) and "=" not in G328_HEAD
''')
after('''assert sum(1 for _o in H27_OLD if _o.startswith("45,59,")) == 1 and sum(1 for _n in H27_NEW if _n.startswith("39,47,")) == 1
''', '''# 0.3.28 ONE-TIME UPDATE migrate0328 (tools/gear_0_3_28_patch.py): the 0.3.27 defaults -> Fortune 3 a level everywhere + no armor Fortune cap
H28_MARK_ID = "SkyyGear 0.3.28 fortune update"
H28_WHO = "SkyyGear 0.3.28"
H28_MARK = ("# %s (Skyy 2026-10-18): every lifelong tool's Fortune line +3 a level, armor Fortune cap 100 (old defaults 2, 10, 15)" % H28_MARK_ID)
H28_KEYS = ["lifelong.perkFortune", "lifelong.perkFortune.mining", "armor.fortune.cap"]
H28_OLD = ["2", "10", "15"]
H28_NEW = ["3", "3", "100"]
_rowdef = dict((r[0], r[4]) for r in CFG_ROWS)
assert [_rowdef[_k] for _k in H28_KEYS] == H28_NEW, "0.3.28: the Server Setup rows hold the new defaults"
assert all(32 <= ord(_c) < 127 for _c in H28_MARK) and "=" not in H28_MARK and H28_MARK.startswith("# ")
''')
after('''F(gcf, "public static final String[] H27_LN = %s;" % jarr(H27_LN))
''', '''F(gcf, "public static final String H28_MARK = %s;" % jstr(H28_MARK))          # 0.3.28 migrate0328
F(gcf, "public static final String H28_MARK_ID = %s;" % jstr(H28_MARK_ID))
F(gcf, "public static final String H28_WHO = %s;" % jstr(H28_WHO))
F(gcf, "public static final String[] H28_KEYS = %s;" % jarr(H28_KEYS))
F(gcf, "public static final String[] H28_OLD = %s;" % jarr(H28_OLD))
F(gcf, "public static final String[] H28_NEW = %s;" % jarr(H28_NEW))
''')
# the fresh file: the marker block after the 0.3.27 rows
rep('''    for k in G327_ROWK:
        scal(k)
    L += [""] + U26_LINES''', '''    for k in G327_ROWK:
        scal(k)
    L += ["", G328_HEAD, H28_MARK]        # 0.3.28: the migrate0328 marker (the three rows keep their places above)
    L += [""] + U26_LINES''')
after('''assert _dp.get("utdrop.luggage") == UT_LUG_DEF and _dp.get("gear.mythicItems") == MYTHIC_ITEMS_DEF
''', '''assert [_dp.get(_k) for _k in H28_KEYS] == H28_NEW and DEFAULT_TEXT.count(H28_MARK_ID) == 1, "0.3.28: the fresh file's Fortune rows + marker"
''')

# Java: h28Update / h28Log / migrate0328 = the migrate0327 machinery (copied from THIS script), number compare (h7Old), the key itself as log key
_a = s.index('M(gcf, r"""\npublic static Object[] h27Update(String text) {')
_b = s.index('public static synchronized String migrate0327() {')
_b = s.index('}""")\n', _b) + len('}""")\n')
J27 = s[_a:_b]
J28 = J27.replace("H27_", "H28_").replace("h27Update", "h28Update").replace("h27Log", "h28Log").replace("migrate0327", "migrate0328")
for _o, _n in [
        ("h23Old(@PKG@.CfgFile.value(l, k), H28_OLD[i])", "h7Old(@PKG@.CfgFile.value(l, k), H28_OLD[i])"),
        ("boolean rw = ov != null && h23Old(ov, H28_OLD[i])", "boolean rw = ov != null && h7Old(ov, H28_OLD[i])"),
        ("} else if (ov != null && !h23Old(ov, H28_NEW[i])) {", "} else if (ov != null && !h7Old(ov, H28_NEW[i])) {"),
        ('" kept (not the 0.3.26 default, or not one plain line) - the new default is "', '" kept (not the 0.3.27 default, or not one plain line) - the new default is "'),
        ("      rows.add(H28_LK[i]);\n      rows.add(H28_LO[i]);\n      rows.add(H28_LN[i]);",
         "      rows.add(H28_KEYS[i]);\n      rows.add(ov.trim());\n      rows.add(H28_NEW[i]);"),
        ('''  String chg = nch == 0 ? "" : nch + " rows (Untiered level bands" + (at.containsValue(H28_NEW[nk - 1]) ? ", luggage share" : "") + ")";''',
         '''  String chg = nch == 0 ? "" : nch + " rows (Fortune per level, armor Fortune cap)";'''),
        ("(Undo puts the 0.3.26 value back)", "(Undo puts the 0.3.27 value back)"),
        ('"before the 0.3.27 Untiered sources update"', '"before the 0.3.28 Fortune update"'),
        ('"config.properties NOT updated to the 0.3.27 Untiered bands: the old file', '"config.properties NOT updated to the 0.3.28 Fortune defaults: the old file'),
        ('''"config.properties updated to the 0.3.27 defaults: " + chg + " (each zone's Untiered items at its alloy band, no orange luggage; Undo''',
         '''"config.properties updated to the 0.3.28 defaults: " + chg + " (Fortune +3 a level on every lifelong tool, no armor Fortune cap; Undo'''),
        ('"config.properties: the 0.3.27 Untiered update marker was added - no value changed"', '"config.properties: the 0.3.28 Fortune update marker was added - no value changed"'),
        ('"CONFIG 0.3.27 Untiered sources: "', '"CONFIG 0.3.28 Fortune: "'),
        ('"could not update config.properties to the 0.3.27 Untiered bands (the file', '"could not update config.properties to the 0.3.28 Fortune defaults (the file'),
]:
    assert J28.count(_o) == 1, _o
    J28 = J28.replace(_o, _n)
assert "0.3.26" not in J28 and J28.count("0.3.27") == 2 and "H27" not in J28 and "h23Old" not in J28 and "Untiered" not in J28, "the copied machinery names only 0.3.28"
assert "public static boolean h7Old(" in s and s.index("public static boolean h7Old(") < _a
after(J27, '''# ---- 0.3.28 ONE-TIME UPDATE migrate0328 (PROJECT-RULES section 4; tools/gear_0_3_28_patch.py): the migrate0327 machinery (copied), numbers compared
# like migrate0317 (h7Old: "2.0" = "2"); change-log rows = the key, the old value as written, the new default (Undo in Server Setup)
''' + J28)
rep('''  @PKG@.GearCfg.migrate0327();          // 0.3.27: the alloy bands + no orange luggage (only the untouched 0.3.26 defaults)''',
    '''  @PKG@.GearCfg.migrate0327();          // 0.3.27: the alloy bands + no orange luggage (only the untouched 0.3.26 defaults)
  @PKG@.GearCfg.migrate0328();          // 0.3.28: Fortune 3 a level everywhere + no armor Fortune cap (only the untouched 0.3.27 defaults)''')

# ================================================================================================================ manifest
rep('''UNTIERED SOURCES: each zone's Untiered items sit at its alloy band''',
    '''FORTUNE: every lifelong tool's Fortune line +3 a level, no Fortune cap (100% = a sure 2nd drop, 150% = 2 + 50% for a 3rd); weapon bags pick their weapon type at identify; retired hoes / sickles leave the Upgrade list. UNTIERED SOURCES: each zone's Untiered items sit at its alloy band''')

# ================================================================================================================ 4: beta bug 12 - the weapon type at identify
rep('''    ("unid.bags", "Gear drops as mystery bags", "loot", "bool", "true", "", "", "", "", "live,part,danger",
     "Single weapons and armor from mobs and fresh chests become bags. Off = the old style.", "field:GearCfg.UNID_BAGS"),
''', '''    ("unid.bags", "Gear drops as mystery bags", "loot", "bool", "true", "", "", "", "", "live,part,danger",
     "Single weapons and armor from mobs and fresh chests become bags. Off = the old style.", "field:GearCfg.UNID_BAGS"),
    # 0.3.28 (beta bug 12, Skyy "they shouldn't decide what the item is until it's identified")
    ("unid.typeAtIdentify", "Weapon type picked at identify", "loot", "bool", "true", "", "", "", "", "live,danger",
     "Weapon bags say Unidentified Weapon; the type (with class lean) is picked at identify.", "field:GearCfg.UNID_TYPEID"),
''')
rep('''           "utdrop.dungeon"}          # 0.3.27: where orange bags come from (economy)''',
    '''           "utdrop.dungeon",          # 0.3.27: where orange bags come from (economy)
           "unid.typeAtIdentify"}          # 0.3.28: what a weapon bag turns into (items)''')
rep('''G328_HEAD = "# ---- Fortune: +3 a level on every lifelong tool, no Fortune cap (SkyyGear 0.3.28) ----"''',
    '''G328_HEAD = "# ---- Fortune: +3 a level on every lifelong tool, no Fortune cap; weapon bags pick their type at identify (SkyyGear 0.3.28) ----"
G328_ROWK = ["unid.typeAtIdentify"]''')
rep('''    L += ["", G328_HEAD, H28_MARK]        # 0.3.28: the migrate0328 marker (the three rows keep their places above)''',
    '''    L += ["", G328_HEAD, H28_MARK]        # 0.3.28: the migrate0328 marker (the three Fortune rows keep their places above) + the new row
    for k in G328_ROWK:
        scal(k)''')
rep('''("UNID_BAGS", "boolean", "true")''', '''("UNID_BAGS", "boolean", "true"), ("UNID_TYPEID", "boolean", "true")''')
rep('''  UNID_BAGS = pbool(p, "unid.bags", true);''', '''  UNID_BAGS = pbool(p, "unid.bags", true);
  UNID_TYPEID = pbool(p, "unid.typeAtIdentify", true);          // 0.3.28 (beta bug 12)''')
rep('''assert [_dp.get(_k) for _k in H28_KEYS] == H28_NEW and DEFAULT_TEXT.count(H28_MARK_ID) == 1, "0.3.28: the fresh file's Fortune rows + marker"''',
    '''assert [_dp.get(_k) for _k in H28_KEYS] == H28_NEW and DEFAULT_TEXT.count(H28_MARK_ID) == 1, "0.3.28: the fresh file's Fortune rows + marker"
assert _dp.get("unid.typeAtIdentify") == "true", "0.3.28: the fresh file's unid.typeAtIdentify row"''')
# the group flag + its names: "grp" = "w" on a NEW weapon bag; its stored mys stays the drop-time pick (only the fallback - 0.3.27 and
# unid.typeAtIdentify=false open it as that type; nothing to migrate). Never on Untiered / Mythic boss / forced-type bags.
rep('''M(gunid, "public static String title(@BD@ d) { return \\"Unidentified \\" + (rar(d) == @PKG@.GearDefs.R_UT ? \\"Untiered \\" : \\"\\") + typeName(type(d)); }")''',
    '''# 0.3.28 (beta bug 12): a weapon bag whose type is picked at identify (grp w; not Untiered / Mythic; unid.typeAtIdentify on)
M(gunid, "public static boolean grpW(@BD@ d) { return d != null && @PKG@.GearCfg.UNID_TYPEID && \\"w\\".equals(@PKG@.GearData.str(d, \\"grp\\", \\"\\")) && rar(d) != @PKG@.GearDefs.R_UT && pz(d) <= 0; }")
M(gunid, "public static String tname(@BD@ d) { return grpW(d) ? \\"Weapon\\" : typeName(type(d)); }")
M(gunid, "public static String title(@BD@ d) { return \\"Unidentified \\" + (rar(d) == @PKG@.GearDefs.R_UT ? \\"Untiered \\" : \\"\\") + tname(d); }")''')
rep('''  int at = at(d);
  boolean arm = ty >= 0 && @PKG@.GearPool.T_ARM[ty];
  if (arm && at > 0 && @PKG@.GearCfg.SHOW_AT) { txt.add(@PKG@.GearPool.AT_NAME[at] + " armor"); col.add(@PKG@.GearDefs.C_LABEL); }''',
    '''  int at = at(d);
  String tn = tname(d);          // 0.3.28: "Weapon" for a weapon bag (its type is picked at identify)
  boolean arm = ty >= 0 && @PKG@.GearPool.T_ARM[ty];
  if (arm && at > 0 && @PKG@.GearCfg.SHOW_AT) { txt.add(@PKG@.GearPool.AT_NAME[at] + " armor"); col.add(@PKG@.GearDefs.C_LABEL); }''')
rep('''  else { txt.add("Unidentified - which " + typeName(ty).toLowerCase() + " it is, its exact level and its modifiers are decided when you identify it."); col.add(@PKG@.GearDefs.C_GRAY); }''',
    '''  else { txt.add("Unidentified - which " + tn.toLowerCase() + " it is, its exact level and its modifiers are decided when you identify it."); col.add(@PKG@.GearDefs.C_GRAY); }''')
rep('''  txt.add(@PKG@.GearDefs.R_NAME[r].toUpperCase() + " " + typeName(ty).toUpperCase()); col.add(@PKG@.GearView.bold(@PKG@.GearDefs.R_HEX[r]));''',
    '''  txt.add(@PKG@.GearDefs.R_NAME[r].toUpperCase() + " " + tn.toUpperCase()); col.add(@PKG@.GearView.bold(@PKG@.GearDefs.R_HEX[r]));''')
before('''# rarity from the odds column (1 mob, 2 chest, 0 craft) with the level boost: every weight above Normal x (1 + levelShift x (shift - 1))
''', r'''# 0.3.28 (beta bug 12): mark a fresh weapon bag "type at identify" (grp w) and re-render its name / tooltip; off / not a bag = unchanged
M(gunid, r"""
public static @IS@ grouped(@IS@ s) {
  if (s == null || !@PKG@.GearCfg.UNID_TYPEID) return s;
  @BD@ d = doc(s);
  if (d == null) return s;
  d.put("grp", new org.bson.BsonString("w"));
  @IS@ o = s.withMetadata(KEY, (@BV@) d);
  return view(o, d);
}""")
''')
rep('''  if (rg == null) return null;
  return make(ty, at, rarity(col, shift), rg[0], rg[1], src, ls, tier);
}""")''', '''  if (rg == null) return null;
  @IS@ bx = make(ty, at, rarity(col, shift), rg[0], rg[1], src, ls, tier);
  return forceType < 0 && !@PKG@.GearPool.T_ARM[ty] ? grouped(bx) : bx;          // 0.3.28 (bug 12): a random weapon bag keeps its type secret
}""")''')
rep('''  if (rg == null) return null;
  return make(ty, at, rarity(col, col == 1 ? lv : 0), rg[0], rg[1], col == 1 ? "drop" : "chest", src, 0);
}""")''', '''  if (rg == null) return null;
  @IS@ fb = make(ty, at, rarity(col, col == 1 ? lv : 0), rg[0], rg[1], col == 1 ? "drop" : "chest", src, 0);
  return @PKG@.GearPool.T_ARM[ty] ? fb : grouped(fb);          // 0.3.28 (bug 12): a dropped weapon's bag too
}""")''')
# identify: a grp-w bag picks its weapon type now - any weapon type with a candidate in the bag's range, the IDENTIFIER's class lean (loot.classLean %);
# none = the stored type (the 0.3.27 behaviour)
rep('''M(gunid, "public static Object[] open(@BD@ d, java.util.UUID by) { if (d == null) return null; return pickZ(type(d), at(d), rar(d), lo(d), hi(d), 0, by, pz(d)); }")''',
    '''# 0.3.28 (beta bug 12): the identifier's class weapon prefixes (GearLoot.lean's rule, here because GearLoot is compiled later); null = no lean
M(gunid, r"""
public static String[] leanOf(java.util.UUID u) {
  if (u == null) return null;
  try {
    Object c = @PKG@.Gear.bget("class:" + u);
    if (!(c instanceof String) || ((String) c).length() == 0) return null;
    Object list = @PKG@.Gear.bget("class:list");
    if (list instanceof String && ("," + (String) list + ",").indexOf("," + (String) c + ":") < 0) return null;
    Object w = @PKG@.Gear.bget("class:weapons:" + (String) c);
    if (!(w instanceof String) || ((String) w).trim().length() == 0) return null;
    return ((String) w).split(",");
  } catch (Throwable t) { return null; }
}""")
M(gunid, r"""
public static int pickW(int fb, int lo, int hi, String[] lean) {
  int nt = @PKG@.GearPool.T_KEY.length;
  int[] el = new int[nt];
  int n = 0;
  for (int t = 0; t < nt; t++) if (!@PKG@.GearPool.T_ARM[t] && @PKG@.GearPool.levelCount(t, 0, lo, hi) > 0) { el[n] = t; n++; }
  if (n == 0) return fb;
  if (lean != null && lean.length > 0 && @PKG@.GearRoll.RNG.nextDouble() * 100.0 < (double) @PKG@.GearCfg.CLASS_LEAN) {
    int[] le = new int[n];
    int m = 0;
    for (int k = 0; k < n; k++) if (@PKG@.GearPool.leanHit(@PKG@.GearPool.T_KEY[el[k]], lean)) { le[m] = el[k]; m++; }
    if (m > 0) return le[@PKG@.GearRoll.RNG.nextInt(m)];
  }
  return el[@PKG@.GearRoll.RNG.nextInt(n)];
}""")
M(gunid, "public static Object[] open(@BD@ d, java.util.UUID by) { if (d == null) return null; int ty = type(d); if (grpW(d)) ty = pickW(ty, lo(d), hi(d), leanOf(by)); return pickZ(ty, grpW(d) ? 0 : at(d), rar(d), lo(d), hi(d), 0, by, pz(d)); }")''')
# the Identify page / Anvil texts name "Weapon" for such a bag
rep('''  int hi = @PKG@.GearUnid.hi(d);
  String tn = @PKG@.GearUnid.typeName(ty);''', '''  int hi = @PKG@.GearUnid.hi(d);
  String tn = @PKG@.GearUnid.tname(d);          // 0.3.28: "Weapon" for a weapon bag''')
rep('''@PKG@.GearUnid.typeName(@PKG@.GearUnid.type(bd)).toUpperCase() + "   -   "''', '''@PKG@.GearUnid.tname(bd).toUpperCase() + "   -   "''')
rep('''    int at = @PKG@.GearUnid.at(bd);
    String tn = @PKG@.GearUnid.typeName(ty);''', '''    int at = @PKG@.GearUnid.at(bd);
    String tn = @PKG@.GearUnid.tname(bd);          // 0.3.28: "Weapon" for a weapon bag''')

# review F4: the refusal texts never name a grp bag's hidden type, and a grp bag skips the stored-type fit check (open() picks any weapon type)
rep('''  if (fit(ty, at(d), lo(d), hi(d)) == null) return "No " + typeName(ty).toLowerCase() + " exists in " + rangeText(lo(d), hi(d)) + " any more - an admin can help.";''',
    '''  if (!grpW(d) && fit(ty, at(d), lo(d), hi(d)) == null) return "No " + tname(d).toLowerCase() + " exists in " + rangeText(lo(d), hi(d)) + " any more - an admin can help.";          // 0.3.28''')
rep('''    return "No Zone " + pz(b) + " Mythic " + typeName(ty).toLowerCase() + " exists here any more.";''',
    '''    return "No Zone " + pz(b) + " Mythic " + tname(b).toLowerCase() + " exists here any more.";''')
rep('''  if (fit(ty, at(b), lo(b), hi(b)) == null) return "No " + typeName(ty).toLowerCase() + " exists in " + rangeText(lo(b), hi(b)) + " any more.";''',
    '''  if (!grpW(b) && fit(ty, at(b), lo(b), hi(b)) == null) return "No " + tname(b).toLowerCase() + " exists in " + rangeText(lo(b), hi(b)) + " any more.";          // 0.3.28''')
# review F5: the sickle roll's comment
rep('''# 100 = one sure, the rest a chance; at most 5
M(gsck, r"""''', '''# 100 = one sure, the rest a chance (0.3.28: no cap - only the 100-extra safety stop; 0.3.11 - 0.3.27: at most 5)
M(gsck, r"""''')

# ================================================================================================================ 5: beta bug 17 - retired hoes / sickles off the Upgrade tab
rep('''# every item on a ladder the player carries: int[] { section, slot }
M(gup, r"""
public static java.util.ArrayList rows(@INV@ inv) {''', '''# 0.3.28 (beta bug 17 "Wooden Hoe in the Anvil upgrade list"): with harvester.only on, plain hoes / sickles are retired (the Harvester
# replaces them) - never an Upgrade row (the Harvester's own Tool_Sickle_Harvester_ ids stay)
M(gup, r"""
public static boolean retired(String id) {
  if (id == null || !(@PKG@.GearCfg.LL_ON && @PKG@.GearCfg.HARV_ON && @PKG@.GearCfg.HARV_ONLY)) return false;
  return id.startsWith("Tool_Hoe_") || (id.startsWith("Tool_Sickle_") && !id.startsWith(%s));
}""" % jstr(HARV_PRE))
# every item on a ladder the player carries: int[] { section, slot }
M(gup, r"""
public static java.util.ArrayList rows(@INV@ inv) {''')
rep('''      if (it == null || it.isEmpty() || next(it.getItemId()) == null) continue;
      out.add(new int[] { @PKG@.GearStamp.SCAN[k], i });''', '''      if (it == null || it.isEmpty() || next(it.getItemId()) == null || retired(it.getItemId())) continue;          // 0.3.28: + no retired hoe / sickle
      out.add(new int[] { @PKG@.GearStamp.SCAN[k], i });''')
rep('''        String cur = P.getProperty(@PKG@.GearLL.KIND[k] + ".uid");
        if (cur == null) continue;
        int[] at = @PKG@.GearLife.find(inv, pk, cur);''', '''        String cur = P.getProperty(@PKG@.GearLL.KIND[k] + ".uid");
        if (cur == null) continue;
        if (@PKG@.GearUp.retired(@PKG@.GearLL.kid(P, k))) continue;          // 0.3.28 (bug 17): a lifelong hoe / sickle waiting to merge = no row
        int[] at = @PKG@.GearLife.find(inv, pk, cur);''')

# ================================================================================================================ 6: the T3 Fortune cap (Skyy "so you cant get over
# 100% till you reach T4" + "at the start of zone 2"): the FORTUNE line of an internal-tier-3 tool that is not Thorium (= Bronze, T3) caps at
# lineCapPerTier x 3.3 (33 levels = 99 % at 3 a level); Thorium (T4) keeps 40; every other line / tier unchanged
after('''  long c = (long) per * (long) (t + 1);
  return c > (long) LINE_BIG ? LINE_BIG : (int) c;
}""")
''', r'''# 0.3.28: the cap of line p of kind k = lineCap, but the Fortune line (p 1) of a tier-3 tool that is not Thorium (Bronze, T3) stops at
# lifelong.lineCapPerTier x 3 + 30 % of it (33: 99 % at 3 a level - Skyy "cant get over 100% till you reach T4"); the top step stays uncapped
M(gll, r"""
public static int lineCapP(java.util.Properties P, int k, int p) {
  int c = lineCap(P, k);
  if (p != 1 || c >= LINE_BIG) return c;
  String id = kid(P, k);
  if (id == null || tier(id) != 3 || id.toLowerCase().indexOf("thorium") >= 0) return c;
  int per = @PKG@.GearCfg.LL_LCAPT;
  int b = per * 3 + (per * 3) / 10;
  return b < c ? b : c;
}""")
''')
rep('''  int c = isLine(p) ? lineCap(P, k) : (isAbil(p) ? abilCap(u, P, k) : lv);''',
    '''  int c = isLine(p) ? lineCapP(P, k, p) : (isAbil(p) ? abilCap(u, P, k) : lv);          // 0.3.28: the T3 Fortune cap''')
rep('''  if (@PKG@.GearLL.isLine(p)) {
    int c = @PKG@.GearLL.lineCap(P, k);
    if (lv < c) return null;''', '''  if (@PKG@.GearLL.isLine(p)) {
    int c = @PKG@.GearLL.lineCapP(P, k, p);          // 0.3.28: the T3 Fortune cap
    if (lv < c) return null;''')
rep('''  int cap = line ? @PKG@.GearLL.lineCap(P, k) : (@PKG@.GearLL.isAbil(p) ? @PKG@.GearLL.abilCap(u, P, k) : mx);''',
    '''  int cap = line ? @PKG@.GearLL.lineCapP(P, k, p) : (@PKG@.GearLL.isAbil(p) ? @PKG@.GearLL.abilCap(u, P, k) : mx);          // 0.3.28: the T3 Fortune cap''')

# ================================================================================================================ the line-cap table (spec check, printed)
_tier = dict(ast.literal_eval(s[s.index("TOOL_TIERS = [") + len("TOOL_TIERS = "):s.index("]", s.index("TOOL_TIERS = [")) + 1]) +
             ast.literal_eval(s[s.index("G23_ZT = [") + len("G23_ZT = "):s.index("]", s.index("G23_ZT = [")) + 1]))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import tier_tags as _T          # noqa: E402
_lad = list(_T.LADDER[:15])
CAPTAB = [(_m, _lad.index(_m) + 1, (33 if _tier[_m] == 3 and _m != "Thorium" else 10 * (_tier[_m] + 1)) if _m != _lad[-1] else None) for _m in _lad]   # item 6
assert [(_m, _c) for _m, _t, _c in CAPTAB][:5] == [("Copper", 20), ("Iron", 30), ("Bronze", 33), ("Thorium", 40), ("Lead", 50)], CAPTAB[:5]
print("0.3.28 Fortune line at +%s a level, full line per tier (Crude 10 levels = %d): %s" % (PF_NEW, 10 * int(PF_NEW), ", ".join(
    "T%d %s %s" % (_t, _m, ("%d lv = %d%%" % (_c, _c * int(PF_NEW))) if _c else "uncapped") for _m, _t, _c in CAPTAB)))

# ================================================================================================================ checks on the result
_i = s.index
assert _i("public static boolean h7Old(") < _i("public static Object[] h28Update(") < _i("public static String h28Log(") < _i("public static synchronized String migrate0328()")
assert _i("public static synchronized String migrate0327()") < _i("public static Object[] h28Update(") and _i("  @PKG@.GearCfg.migrate0327();") < _i("  @PKG@.GearCfg.migrate0328();")
assert _i("public static String ordw(long n)") < _i("public static String fdrops(double f)") < _i("public static void mlines(") < _i("  if (f == 6) { mlines(owner, id, d, t, txt, col); return; }")
assert _i("public static double fcapA()") < _i("@PKG@.GearCfg.fcapA();")
assert _i("H28_KEYS = [") < _i("def default_text():") and _i("G328_HEAD = ") < _i("def default_text():")
assert s.count("registerSystem(") == SYS0, "no new system"
assert s.count("registerCommand(") == CMD0, "no new command"
assert s.count(' = mk("') == MK0, "no new class"
_u = s
for _new, _old, _cnt in reversed(CHANGES):
    assert _u.count(_new) >= _cnt
    _u = _u.replace(_new, _old)
assert _u == OLD, "the generated script differs from 0.3.27 outside the recorded changes"

open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(DST, ROOT), "(%d lines; 0.3.27 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
