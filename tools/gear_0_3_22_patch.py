"""Derive SkyyGear/build_skyygear_0.3.22.py from the LIVE 0.3.21 (build_skyygear_0.3.21.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_3_21_patch.py). Edit THIS file, never the generated script; every anchor is asserted and every change is undone at the end to
prove nothing else changed. Run:
    python tools/gear_0_3_22_patch.py      then      python SkyyGear/build_skyygear_0.3.22.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.3.22.py   (--static runs without jars / Assets.zip)
The build still reads Quirk's mining armor textures from the PRIVATE art folder (0.3.21; nothing from it is copied into this repo).

0.3.22 (2026-10-17) = THE 15-STEP METAL LADDER (round G1, research/Metals-Tools-Fortune-Spec.md section 5 row G1).
Skyy's words (docs/answered/gear.md 2026-10-17): popup "tools follow ONE tier ladder of all 15 metals in zone order - Copper, Iron, Bronze,
Thorium, Lead, Dusk, Cobalt, Chromium, Azurvane, Adamantite, Slag, Cinder, Mithril, Titanium, Lumen - each one tier above the last (so the
tier tags renumber, e.g. Thorium becomes T4, Lumen T15)?" -> "Yes, full 15-step ladder (Recommended)"; "Yes, all defaults (Recommended)" to the
spec's Q2-Q11 (Fortune +10% a level, no total cap, the tool line keeps its level cap; 5x pickaxe Mining Fortune only; only ore gets harder per
zone; Lead / Chromium / Slag / Titanium tools copy today's next-tier specs).
  1. TIER TAGS (tools/tier_tags.py TT_VERSION 2, the one table): T1 Copper (+ Crude / Wood / Scrap), T2 Iron (+ Steel), T3 Bronze, T4 Thorium,
     T5 Lead, T6 Dusk, T7 Cobalt, T8 Chromium, T9 Azurvane, T10 Adamantite, T11 Slag, T12 Cinder, T13 Mithril, T14 Titanium, T15 Lumen,
     T16 Onyxium (parked). Every tag keeps its word, only the number moves ("T3 Iron" -> "T2 Iron"; Bronze "T3 Iron" -> "T3 Bronze").
     This jar's own texts follow at build time (the watering cans, Harvesters, zone Mining sets in server.lang; the pack items' tag, the
     combat armor tag (GearView.tierFor = tier_tags LEVEL_BANDS: Lv 15 T2, 17 T3, 20 T4, 22 T5 ... 45 T14, 50 T15, Onyxium T16) and the
     Anvil / Upgrade tool tags (GearUpg.tierTag) at run time). Gear's INTERNAL tool tier (0 Crude .. 7 Onyxium: saved documents, line caps
     lifelong.lineCapPerTier x (tier + 1), the log / crop gate, FAMMAX) is NOT renumbered - no saved tool changes tier or cap.
  2. THE ORE GATE (runtime only, no vanilla file changed) - new rows gate.oreTiers (text, Ore:normal T[:half T]), gate.halfFactor (0.5 = 2x
     the hits) and tool.tierPower (the ladder power of a T1..T16 pickaxe). An ore of the table (its block id's 2nd word: Ore_Copper_Stone,
     Ore_Lead_Sandstone_SkyWynn ...) asks the HELD pickaxe / multitool's LADDER tier T (its metal word, tools/tier_tags.py TOOL_METALS):
        T >= normal          normal: the hit = max(vanilla, 0.25 x tierPower[T] / tierPower[normal]) (0.25 = every vanilla pickaxe on its own
                             ore, VERIFIED Assets.zip), then the level / Breaking Power / armor / accessory power as before
        half <= T < normal   0.25 x gate.halfFactor (2x the hits of a right-tier pickaxe)
        lower                0.25 x gate.nextFactor (2.5x) when the NEXT pickaxe step that exists (PICK_T) reaches normal, else
                             x gate.twoUpFactor (10x). NEVER refused (Tool-Levels 7); the old "three up refused" stays for logs only.
     Default table (spec 3.2 + its zone rule "the zone's alloy pick opens the next zone"): Copper 1, Iron 2 (half 1), Silver / Gold 2 (half 1,
     the old Iron rule), Thorium 3, Lead 4 (half 3), Cobalt 6, Chromium 7 (half 6), Adamantite 9, Slag 10 (half 9), Mithril 12, Titanium 13
     (half 12), Onyxium 15 (the Lumen pick opens the parked Zone 6). tool.tierPower default = 1.4^(T-1) (1, 1.4, 1.96 ... 155.57: the
     geometric fit of the vanilla pickaxes' ore powers, Copper -> Mithril). The build prints the hit table (pickaxe x ore, Lv 1).
  3. MINING FORTUNE ROW: lifelong.perkFortune.mining 10 = +10 Fortune (+10 %) a Fortune level on the PICKAXE kind (and so the multitool's
     pickaxe stat set, GearTool.mstats -> perkFx(fam 1)); hatchet / Harvester / pole keep lifelong.perkFortune (2). The line keeps its cap
     (lifelong.lineCapPerTier x the internal tier); no total cap (SkyySkills' "gear" source is uncapped). New key only: no migration.
  4. LEVEL BANDS FOR THE NEW METALS (spec 3.1; weapons A1 / tools G2 read them by the id words <Metal>_SkyWynn - critic L1: never another
     mod's Lead / Titanium id): level.material.Lead_SkyWynn 22,30, Dusk_SkyWynn 24,32, Chromium_SkyWynn 28,40, Azurvane_SkyWynn 31,41,
     Slag_SkyWynn 37,45, Cinder_SkyWynn 39,47, Titanium_SkyWynn 45,55, Lumen_SkyWynn 50,60 (post-rebirth). Existing metals keep their bands
     (Bronze stays 15-23, Skyy's 2026-09-30 lock). ONE-TIME UPDATE migrate0322 (PROJECT-RULES 4, the migrate0321 shape): a pure ADDITION of a
     marked block at the END of config.properties with only the rows the file lacks (any case - the loader matches entries case-blind),
     verified History copy first, atomic ISO-8859-1 write, run-once marker, every other byte and line ending kept. A fresh file carries it.
  5. WEAPON / TOOL METAL ROWS for A1 / G2: GearLL.LT_W / LT_N / LT_WORD (= tools/tier_tags.py TOOL_METALS: the 12 tool words + the 8 zone
     metals and alloys) + the level bands above; G22_OWN_PICKS (empty) is where G2 adds its own pickaxe ids so PICK_T knows their steps.
  6. CRITIC FIXES (main session, same version):
     M1 no ore slower than 0.3.21 (no alloy pickaxe exists before G2): a slowed ore hit starts from the RIGHT-tier pickaxe's own vanilla
        power on that block (GearLL.rpow, 0.3.7's refPow rule - Mithril ore is Rocks: 1.0), and NEW row gate.oreFloor (default Lead,Chromium,
        Slag,Titanium - the zone ores 0.3.21 never gated; G2 empties it once Bronze / Dusk / Azurvane / Cinder / Lumen pickaxes exist): a
        listed ore's slowed hit never ends below its vanilla hit. The build prints the 0.3.21 > 0.3.22 hit table (8 pickaxes x 12 ore blocks)
        and STOPS if any cell is slower.
     M2 the combat armor tag takes the id's metal word first (Armor_Bronze_* "T3 Bronze Heavy", not the shared 15-23 band's "T2 Iron"); the
        level band only for ids without one (tools/tier_tags.py combat_tag = the same rule).
     L1 the level rows above match only <Metal>_SkyWynn (TerrariaToolsWeapons' Armor_Lead_* / Tool_Pickaxe_Lead keep their own level).
     M3 (checked, unchanged): one break is bounded by SkyySkills perk.fortuneGuard (default 100 extra drops); the pickaxe's Fortune (line +
        base) counts on only.mining = Rock_, Rubble_, Ore_ blocks - exactly as in 0.3.21 (spec 2.1 "scope unchanged").
Commands: none new. Config: + gate.oreTiers, gate.halfFactor, gate.oreFloor, tool.tierPower, lifelong.perkFortune.mining (absent = the default), + 8
level.material rows (migrate0322). Classes: none new (GearLL, GearCfg, GearView, GearUpg, GearToolHitSys, LifelongPage + the setup call).
SAVED DATA: none changed (no document, no tier, no cap moves; the config gets 8 added rows).
ROLLBACK 0.3.22 -> 0.3.21: safe. 0.3.21 ignores the 4 new scalar rows; the 8 level.material rows stay (0.3.21 has no item of those metals,
so they do nothing); the ore gate and tags go back to 0.3.21's (lang texts come from the jars). Rolling forward again re-reads everything.
"""
import os
import sys
import ast
import math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.21.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.22.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.21"' in s and "GENERATED by tools/gear_0_3_21_patch.py" in s, "not the generated 0.3.21 script"
assert "gate.oreTiers" not in s and "migrate0322" not in s and "LL_PFORTM" not in s
SYS0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
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


def method(anchor_start):
    """the full text of one M(...) block starting at anchor_start (up to its closing triple quote + paren)"""
    i = s.index(anchor_start)
    j = s.index('}""")', i)
    return s[i:j + len('}""")')]


_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyGear") != "0.3.21":
    print("NOTE: tools/deploy_set.py SET pins SkyyGear %s, this patch derives from 0.3.21" % _set.get("SkyyGear"))

HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.3.22 (2026-10-17)"):].rstrip() + "\n"

# ================================================================================================================ docstring + version
rep('''"""SkyyGear 0.3.21 - build script (javassist via jpype). GENERATED by tools/gear_0_3_21_patch.py from the LIVE 0.3.20 (itself GENERATED by
tools/gear_0_3_20_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.21.py -> SkyyGear/SkyyGear-0.3.21.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.21.py. Needs Quirk's private textures (../SkyWynn-PRIVATE-art/mining-armor).

''', '''"""SkyyGear 0.3.22 - build script (javassist via jpype). GENERATED by tools/gear_0_3_22_patch.py from the LIVE 0.3.21 (itself GENERATED by
tools/gear_0_3_21_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.22.py -> SkyyGear/SkyyGear-0.3.22.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.22.py. Needs Quirk's private textures (../SkyWynn-PRIVATE-art/mining-armor).

''' + NOTE + '''
--- 0.3.21 notes ---
''')
rep('VERSION = "0.3.21"\n', 'VERSION = "0.3.22"\n')

# ================================================================================================================ 1: the zone armor band check (tags)
# 0.3.21 asserted that each zone set's band START sits in its tag's old level range; with the 15-step ladder the tag is the ingot's own step and
# the bands (Skyy-approved 0.3.21 numbers) stay - so the check becomes: the bands climb the ladder, never above 49 (unchanged numbers)
rep('''for _r in ZM_ROWS:          # the band start sits in the tier tag's level range (tier_for_level) and the band rule (start .. next start + 3, <= 49)
    assert TT.tier_for_level(_r[8][0]) == TT.tier("Ingredient_Bar_%s_SkyWynn" % _r[1]) and _r[8][1] <= VANILLA_TOP, _r''',
    '''for _r in ZM_ROWS:          # 0.3.22: the bands climb the 15-step ladder with their ingot's tag (tools/tier_tags.py TT_VERSION 2), never above 49
    assert _r[8][1] <= VANILLA_TOP and TT.tier("Armor_Mining_%s_Head" % _r[1]) == TT.tier("Ingredient_Bar_%s_SkyWynn" % _r[1]) == TT.metal_tier(_r[1]), _r
assert [_r[8][0] for _r in ZM_ROWS] == sorted(_r[8][0] for _r in ZM_ROWS) and [TT.metal_tier(_r[1]) for _r in ZM_ROWS] == sorted(TT.metal_tier(_r[1]) for _r in ZM_ROWS)''')

# ================================================================================================================ 2: rows, fields, the default text
G22_PY = r'''# ================================================================= 0.3.22 THE 15-STEP METAL LADDER (tools/gear_0_3_22_patch.py, round G1)
import math
assert TT.TT_VERSION == "2" and len(TT.LADDER) == 16 and TT.LADDER[2] == "Bronze" and TT.LADDER[-1] == "Onyxium", "tools/tier_tags.py: the 15-step ladder"
assert [w for w, _t in TOOL_TIERS] == [w for w, _t in TT.TOOL_METALS[:len(TOOL_TIERS)]], "TOOL_TIERS words = tools/tier_tags.py TOOL_METALS"
assert all(TT.metal_tier(w) == (3 if w == "Bronze" else TT.display(t)) for w, t in TOOL_TIERS), "the ladder T of every Gear tool word"
# the ore gate table: (ore word, normal from ladder T, half speed from T (0 = none)) - spec 3.2 + its zone rule; Silver / Gold = Iron's row
_ZONES = [("Copper", "Iron", "Bronze"), ("Thorium", "Lead", "Dusk"), ("Cobalt", "Chromium", "Azurvane"), ("Adamantite", "Slag", "Cinder"),
          ("Mithril", "Titanium", "Lumen")]
G22_ORE = [("Copper", 1, 0), ("Iron", 2, 1), ("Silver", 2, 1), ("Gold", 2, 1)]
for _zi in range(1, len(_ZONES)):
    _op = TT.metal_tier(_ZONES[_zi - 1][2])          # the previous zone's alloy pickaxe opens this zone
    G22_ORE += [(_ZONES[_zi][0], _op, 0), (_ZONES[_zi][1], TT.metal_tier(_ZONES[_zi][0]), _op)]
G22_ORE.append(("Onyxium", TT.metal_tier("Lumen"), 0))          # parked Zone 6: the Lumen pickaxe opens it
assert [(w, n, h) for w, n, h in G22_ORE if w in ("Thorium", "Lead", "Cobalt", "Chromium", "Adamantite", "Slag", "Mithril", "Titanium")] == [
    ("Thorium", 3, 0), ("Lead", 4, 3), ("Cobalt", 6, 0), ("Chromium", 7, 6), ("Adamantite", 9, 0), ("Slag", 10, 9), ("Mithril", 12, 0),
    ("Titanium", 13, 12)], "the spec 3.2 table"
ORE_TIERS_DEF = ",".join("%s:%d" % (w, n) if not h else "%s:%d:%d" % (w, n, h) for w, n, h in G22_ORE)
TIER_POW_STEP = 1.4
TIER_POW = [round(TIER_POW_STEP ** (t - 1), 2) for t in range(1, len(TT.LADDER) + 1)]
TIER_POW_DEF = ",".join(("%g" % p) for p in TIER_POW)
ORE_BASE = 0.25          # every vanilla pickaxe on its own ore (VERIFIED below)
# the pickaxe steps that exist (the "next pickaxe" of the lower-than-half rule); G2 appends its own pickaxe ids here
G22_OWN_PICKS = []
PICK_T = sorted(set(TT.metal_tier(_i.split("_")[2]) for _i in list(_TOOL_AZ_IDS) + G22_OWN_PICKS
                    if _i.startswith("Tool_Pickaxe_") and TT.metal_tier(_i.split("_")[2])))
assert PICK_T == [1, 2, 4, 7, 10, 13, 16], "0.3.22: the vanilla pickaxe steps changed: %s" % PICK_T
# the pickaxe of each existing step (the "right-tier" pickaxe whose vanilla power a slowed hit starts from, like 0.3.7's refPow)
PICK_ID = []
for _t in PICK_T:
    _c = sorted(_i for _i in list(_TOOL_AZ_IDS) + G22_OWN_PICKS if _i.startswith("Tool_Pickaxe_") and TT.metal_tier(_i.split("_")[2]) == _t)
    PICK_ID.append("Tool_Pickaxe_" + TT.noun(_t) if "Tool_Pickaxe_" + TT.noun(_t) in _c else _c[0])
assert PICK_ID[:3] == ["Tool_Pickaxe_Copper", "Tool_Pickaxe_Iron", "Tool_Pickaxe_Thorium"], PICK_ID
# 0.3.22 critic M1 (interim until G2's alloy pickaxes): the zone ores never break slower than their vanilla speed (0.3.21 did not gate them)
ORE_FLOOR_DEF = "Lead,Chromium,Slag,Titanium"
_vs = {}
for _m in ("Crude", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"):
    _vs[_m] = [(sp.get("GatherType"), float(sp.get("Power", 0)), sp.get("Quality"), bool(sp.get("IsIncorrect")))
               for sp in (az_get("Tool_Pickaxe_" + _m, "Tool") or {}).get("Specs", []) if isinstance(sp, dict)]
for _m in ("Copper", "Iron", "Thorium", "Cobalt", "Adamantite"):
    assert [p for g, p, q, b in _vs[_m] if g == "Ore" + _m] == [ORE_BASE], "0.3.22: the vanilla %s pickaxe on its own ore is no longer %s" % (_m, ORE_BASE)


def _g22_v(m, gt, q):
    """vanilla power of pickaxe m on a block (gather type gt, quality q; a lower tool quality = 0, UNVERIFIED engine rule)"""
    for g, p, sq, bad in _vs[m]:
        if g == gt:
            return 0.0 if bad or (q is not None and sq is not None and sq < q) else p
    return 0.0


def _g22_brk(i):
    return ((az_get(i, "BlockType") or {}).get("Gathering") or {}).get("Breaking", {})


# the gated ore blocks: one vanilla block per ore word + the zone ores' partner blocks (SkyyWorldGen 0.7.3 copies their mining rule)
_G22_ZB = {"Lead": "Ore_Thorium_Sandstone", "Chromium": "Ore_Cobalt_Shale", "Slag": "Ore_Adamantite_Magma", "Titanium": "Ore_Mithril_Stone"}
G22_BLK = []
for _w, _n, _h in G22_ORE:
    _cand = [_i for _i in sorted(AZ_ITEMS) if _i.startswith("Ore_%s_" % _w)]
    _b = _G22_ZB.get(_w) or ([_i for _i in _cand if str(_g22_brk(_i).get("GatherType", "")).startswith("Ore")] + _cand + [None])[0]
    if _b is None:
        continue          # Onyxium: no vanilla ore block
    G22_BLK.append((_w, _n, _h, _b, _g22_brk(_b).get("GatherType"), _g22_brk(_b).get("Quality")))
assert len(G22_BLK) == 12, [b[:4] for b in G22_BLK]
_OLD_M = {"Copper": 1, "Iron": 2, "Silver": 2, "Gold": 2, "Thorium": 3, "Cobalt": 4, "Adamantite": 5, "Mithril": 6, "Onyxium": 7}
_G22_PK = [("Crude", 0), ("Copper", 1), ("Iron", 2), ("Thorium", 3), ("Cobalt", 4), ("Adamantite", 5), ("Mithril", 6), ("Onyxium", 7)]


def _g22_old(m, mi, w, gt, q):
    """the 0.3.21 Lv 1 hit (zone ores ungated; vanilla ores: one up = the right-tier pickaxe x0.4, two up x0.1, three up refused = 0)"""
    d0 = _g22_v(m, gt, q)
    if w not in _OLD_M:
        return d0
    d = _OLD_M[w] - max(mi, 1)
    if d <= 0:
        return d0
    if d >= 3:
        return 0.0
    return max(_g22_v(_G22_PK[_OLD_M[w]][0], gt, q), d0) * (0.4 if d == 1 else 0.1)


def _g22_new(m, w, n, h, gt, q):
    """the 0.3.22 Lv 1 hit = GearLL.oreDr x slowF"""
    t = max(1, TT.metal_tier(m))
    d0 = _g22_v(m, gt, q)
    if t >= n:
        return max(d0, ORE_BASE * TIER_POW[min(t, 16) - 1] / TIER_POW[min(n, 16) - 1])
    k = [i for i, p in enumerate(PICK_T) if p >= n][0]
    ref = max(ORE_BASE, _g22_v(PICK_ID[k].split("_")[2], gt, q))
    f = 0.5 if (h and t >= h) else (0.4 if min([p for p in PICK_T if p > t] or [999]) >= n else 0.1)
    return max(ref, d0 / f) * f if w in ORE_FLOOR_DEF.split(",") else ref * f


def _g22_hits(x):
    return 0 if x <= 0 else int(math.ceil(1.0 / x - 1e-9))


G22_HITS = []
G22_WORSE = []
for _m, _mi in _G22_PK:
    _row = []
    for _w, _n, _h, _b, _gt, _q in G22_BLK:
        _o, _x = _g22_hits(_g22_old(_m, _mi, _w, _gt, _q)), _g22_hits(_g22_new(_m, _w, _n, _h, _gt, _q))
        _row.append((_o, _x))
        if _o and (not _x or _x > _o):
            G22_WORSE.append((_m, _w, _o, _x))
    G22_HITS.append((_m, _row))
print("0.3.22 ore gate (gate.oreTiers %s; gate.oreFloor %s; tool.tierPower %s) - hits at Lv 1, 0.3.21 > 0.3.22 (0 = refused / no damage):"
      % (ORE_TIERS_DEF, ORE_FLOOR_DEF, TIER_POW_DEF))
print("  %-14s %s" % ("pickaxe", " ".join("%-9s" % ("%s %d" % (_w[:6], _n)) for _w, _n, _h, _b, _gt, _q in G22_BLK)))
for _m, _row in G22_HITS:
    print("  %-14s %s" % ("%s T%d" % (_m, TT.metal_tier(_m)), " ".join("%-9s" % ("%d>%d" % _c) for _c in _row)))
assert not G22_WORSE, "0.3.22 critic M1: an ore breaks slower than in 0.3.21: %s" % G22_WORSE
assert dict(G22_HITS)["Copper"][0] == (4, 4) and dict(G22_HITS)["Thorium"][4] == (4, 3), "0.3.22 hit table"
# the level bands of the new metals (spec 3.1; existing metals keep theirs)
G22_BANDS = [("Lead", 22, 30), ("Dusk", 24, 32), ("Chromium", 28, 40), ("Azurvane", 31, 41), ("Slag", 37, 45), ("Cinder", 39, 47),
             ("Titanium", 45, 55), ("Lumen", 50, 60)]
assert [w for w, _a, _b in G22_BANDS] == [w for w, _t in TT.TOOL_METALS[len(TOOL_TIERS):]] and not set(w.lower() for w, _a, _b in G22_BANDS) & set(t.lower() for t, _s, _c in BD_ALL)
assert all(TT.tier_for_level(_a) == TT.metal_tier(w) for w, _a, _b in G22_BANDS), "the band starts = tools/tier_tags.py LEVEL_BANDS"
assert [_a for w, _a, _b in G22_BANDS] == sorted(_a for w, _a, _b in G22_BANDS)
'''
before('''CFG_ROWS = [
''', G22_PY)
before('''# UPGRADE POINTS (Skyy 2026-10-13 "1 point per skill level"; perks = research/Gathering-Shards-Spec.md 6.3, the ones built now): key,''',
       '''assert sorted(w for w, _m in LL_ORE) == sorted(w for w, _n, _h in G22_ORE if w not in ("Lead", "Chromium", "Slag", "Titanium")), "0.3.22: every 0.3.0 ore stays gated"
''')

# Server Setup rows (the lifelong category, next to the gate rows)
after('''    ("gate.twoUpFactor", "Two tiers up speed", "lifelong", "dec", "0.1", "0.01", "1", "", "x", "live,danger",
     "A block two tiers above your tool breaks at this speed (0.1 = 10x the hits).", "field:GearCfg.GATE_TWO"),
''', '''    # 0.3.22 THE 15-STEP METAL LADDER (round G1): the ore gate by ladder tier, the half speed, the ladder power, the pickaxe Mining Fortune
    ("gate.oreTiers", "Ore tiers (normal : half)", "lifelong", "text", ORE_TIERS_DEF, "0", "600", "", "", "live,danger",
     "Ore:T:H - from ladder tier T it mines normally, from H at half speed, lower slower (never refused).",
     "field:GearCfg.ORE_TIERS;check=GearLL.checkOreTiers"),
    ("gate.halfFactor", "Half speed (ore)", "lifelong", "dec", "0.5", "0.01", "1", "", "x", "live,danger",
     "An ore at its half-speed tier breaks at this speed (0.5 = 2x the hits).", "field:GearCfg.GATE_HALF"),
    ("gate.oreFloor", "Ores never below vanilla speed", "lifelong", "text", ORE_FLOOR_DEF, "0", "300", "", "", "live,danger",
     "These ores never break slower than vanilla (zone ores until their alloy pickaxes exist; then empty).",
     "field:GearCfg.ORE_FLOOR;check=GearLL.checkOreFloor"),
    ("tool.tierPower", "Pickaxe power by ladder tier", "lifelong", "text", TIER_POW_DEF, "0", "400", "", "", "live,danger",
     "T1..T16 pickaxe power on ore at or above its tier (hit x this / the ore tier's).",
     "field:GearCfg.TIER_POW;check=GearLL.checkTierPower"),
    ("lifelong.perkFortune.mining", "Mining Fortune per pickaxe level", "lifelong", "dec", "10", "0", "100", "", "", "live,danger",
     "Fortune per pickaxe level, multitool too (100 = a sure extra drop)." + PH, "field:GearCfg.LL_PFORTM"),
''')
rep('''     "Each Fortune level adds this much (100 = a sure extra drop)." + PH, "field:GearCfg.LL_PFORT"),''',
    '''     "Fortune per level of a hatchet, Harvester or pole (100 = sure drop)." + PH, "field:GearCfg.LL_PFORT"),''')
rep('''     "Crude counts as Copper. 1-2 tiers up slow, 3 up refused; crops 2 up refused. Off = no tier gate.", "field:GearCfg.GATE_ON"),''',
    '''     "Crude = Copper. Ore: gate.oreTiers (never refused). Logs 1-2 up slow, 3 refused. Crops 2 up refused.", "field:GearCfg.GATE_ON"),''')
rep('''           "garmor.zoneBands", "unid.questFree"}''', '''           "garmor.zoneBands", "unid.questFree",
           # 0.3.22: the ore gate + ladder power (gathering speed) and the pickaxe Mining Fortune (= economy)
           "gate.oreTiers", "gate.halfFactor", "tool.tierPower", "lifelong.perkFortune.mining", "gate.oreFloor"}''')
rep('''              ("ZM_BANDS", "String", jstr(ZM_BANDS_DEF)), ("UNID_QFREE", "boolean", "true")]''',
    '''              ("ZM_BANDS", "String", jstr(ZM_BANDS_DEF)), ("UNID_QFREE", "boolean", "true"),
              # 0.3.22 the 15-step metal ladder
              ("ORE_TIERS", "String", jstr(ORE_TIERS_DEF)), ("GATE_HALF", "double", "0.5"), ("TIER_POW", "String", jstr(TIER_POW_DEF)),
              ("LL_PFORTM", "double", "10.0"), ("ORE_FLOOR", "String", jstr(ORE_FLOOR_DEF))]''')
after('''  UNID_QFREE = pbool(p, "unid.questFree", true);          // 0.3.21: quest bags identify free
''', '''  ORE_TIERS = ptext(p, "gate.oreTiers", "@ORETIERS@").trim();          // 0.3.22 (checked where it is used: a bad text = one WARN + the default)
  GATE_HALF = pdec(p, "gate.halfFactor", 0.5, 0.01, 1.0);
  TIER_POW = ptext(p, "tool.tierPower", "@TIERPOW@").trim();
  LL_PFORTM = pdec(p, "lifelong.perkFortune.mining", 10.0, 0.0, 100.0);
  ORE_FLOOR = ptext(p, "gate.oreFloor", "@OREFLOOR@").trim();          // critic M1 (checked where it is used)
''')
rep('''   .replace("@ZMBANDS@", ZM_BANDS_DEF))          # 0.3.21''', '''   .replace("@ZMBANDS@", ZM_BANDS_DEF)          # 0.3.21
   .replace("@ORETIERS@", ORE_TIERS_DEF).replace("@TIERPOW@", TIER_POW_DEF).replace("@OREFLOOR@", ORE_FLOOR_DEF))          # 0.3.22''')
rep('''G321_ROWK = ["unid.questFree"]
''', '''G321_ROWK = ["unid.questFree"]
G322_HEAD = "# ---- the 15-step metal ladder: ore gate + pickaxe Mining Fortune (SkyyGear 0.3.22) ----"
G322_ROWK = ["gate.oreTiers", "gate.halfFactor", "tool.tierPower", "lifelong.perkFortune.mining", "gate.oreFloor"]
''')
rep('''    for k in G321_ROWK:
        scal(k)
''', '''    for k in G321_ROWK:
        scal(k)
    L += ["", G322_HEAD]        # 0.3.22: the new rows (absent = the default; no one-time update)
    for k in G322_ROWK:
        scal(k)
''')

# the level band block (a fresh file carries it before the zone mining armor block; migrate0322 appends the missing rows to an older file)
after('''assert len(set(ZM_LINES)) == len(ZM_LINES) and not set(ZM_LINES) & set(GM_LINES) and ZM_MARK_ID not in GM_MARK and GM_MARK_ID not in ZM_MARK
''', '''# 0.3.22: the level bands of the new ladder metals (pure addition; the migrate0321 shape)
M22_MARK_ID = "SkyyGear 0.3.22 metal ladder levels"
M22_WHO = "SkyyGear 0.3.22"
M22_HEAD = "# ---- The 15-step metal ladder: level bands of the new metals (SkyyGear 0.3.22) ----"
M22_MARK = ("# %s (Skyy 2026-10-17): Lead, Dusk, Chromium, Azurvane, Slag, Cinder, Titanium and Lumen gear gets a level band (their tools and "
            "weapons come in later rounds); Titanium and Lumen go past 49 (after rebirth)" % M22_MARK_ID)
M22_C = "# ---- the zone metals and alloys (our <Metal>_SkyWynn ids only, never another mod's Lead): each row holds min,cap (spec 3.1) ----"
M22_GROUPS = [(M22_C, ["level.material.%s_SkyWynn=%s" % (_t, band_text(_s, _c)) for _t, _s, _c in G22_BANDS])]          # critic L1: our _SkyWynn ids only
M22_LINES = [M22_HEAD, M22_MARK] + [_x for _c, _ls in M22_GROUPS for _x in [_c] + _ls]
assert all(all(32 <= ord(_c) < 127 for _c in _x) for _x in M22_LINES) and all("=" not in _x for _x in (M22_HEAD, M22_MARK, M22_C))
assert len(set(M22_LINES)) == len(M22_LINES) and not set(M22_LINES) & set(ZM_LINES + GM_LINES) and M22_MARK_ID not in ZM_MARK and ZM_MARK_ID not in M22_MARK
''')
rep('''    L += [""] + ZM_LINES       # 0.3.21: the zone mining armor block (migrate0321 adds the missing lines of it to an older file)
''', '''    L += [""] + M22_LINES      # 0.3.22: the new metals' level bands (migrate0322 adds the missing rows of it to an older file)
    L += [""] + ZM_LINES       # 0.3.21: the zone mining armor block (migrate0321 adds the missing lines of it to an older file)
''')
after('''assert _DL[_DL.index(ZM_HEAD) - 1:_DL.index(ZM_HEAD) + len(ZM_LINES) + 1] == [""] + ZM_LINES + [""] and _DL[_DL.index(ZM_HEAD) + len(ZM_LINES) + 1] == GU_LINES[0]
''', '''# 0.3.22: the metal ladder band block once, right before the zone mining armor block; its rows read back
assert DEFAULT_TEXT.count(M22_MARK_ID) == 1 and all(_DL.count(_x) == 1 for _x in M22_LINES)
assert _DL[_DL.index(M22_HEAD) - 1:_DL.index(M22_HEAD) + len(M22_LINES) + 1] == [""] + M22_LINES + [""] and _DL[_DL.index(M22_HEAD) + len(M22_LINES) + 1] == ZM_HEAD
for _t, _s, _c in G22_BANDS:
    assert _dp.get("level.material.%s_SkyWynn" % _t) == band_text(_s, _c) and _dp.get("level.material." + _t) is None
assert [_dp.get(_k) for _k in G322_ROWK] == [ORE_TIERS_DEF, "0.5", TIER_POW_DEF, "10", ORE_FLOOR_DEF], [_dp.get(_k) for _k in G322_ROWK]
''')
after('''F(gcf, "public static final String[] ZM_GK = %s;" % jarr([_x.split("=", 1)[0] for _c, _ls in ZM_GROUPS for _x in _ls]))
''', '''F(gcf, "public static final String M22_MARK = %s;" % jstr(M22_MARK))          # 0.3.22 migrate0322
F(gcf, "public static final String M22_MARK_ID = %s;" % jstr(M22_MARK_ID))
F(gcf, "public static final String M22_WHO = %s;" % jstr(M22_WHO))
F(gcf, "public static final String M22_HEAD = %s;" % jstr(M22_HEAD))
F(gcf, "public static final String[] M22_GC = %s;" % jarr([_c for _c, _ls in M22_GROUPS]))
F(gcf, "public static final int[] M22_GS = %s;" % jints([len(_ls) for _c, _ls in M22_GROUPS]))
F(gcf, "public static final String[] M22_GL = %s;" % jarr([_x for _c, _ls in M22_GROUPS for _x in _ls]))
F(gcf, "public static final String[] M22_GK = %s;" % jarr([_x.split("=", 1)[0] for _c, _ls in M22_GROUPS for _x in _ls]))
''')

# ================================================================================================================ 3: migrate0322 (the migrate0321 shape)
_zmu = method('''public static Object[] zmUpdate(String text) {''')
assert _zmu.count("if (pp.getProperty(ZM_GK[x]) != null)") == 1 and "M22_" not in _zmu
_m22u = _zmu.replace("zmUpdate", "m22Update").replace("ZM_", "M22_").replace("if (pp.getProperty(M22_GK[x]) != null)", "if (has22(pp, M22_GK[x]))")
_mig21 = method('''public static synchronized String migrate0321() {''')
_mig22 = _mig21.replace("migrate0321", "migrate0322").replace("zmUpdate", "m22Update").replace("ZM_WHO", "M22_WHO")
_cut_a = _mig22.index("    if (r == null) {")
_cut_b = _mig22.index("      return \"\";\n    }\n", _cut_a) + len("      return \"\";\n    }\n")
_mig22 = _mig22[:_cut_a] + "    if (r == null) return \"\";\n" + _mig22[_cut_b:]
for _a, _b in (("before the 0.3.21 zone mining armor update", "before the 0.3.22 metal ladder level update"),
               ("NOT updated with the 0.3.21 zone mining armor settings", "NOT updated with the 0.3.22 metal ladder level bands"),
               ("(the built-in zone rows are used, the zone Mining Sets stay off; the next start tries again)",
                "(the new metals have no level band until then; the next start tries again)"),
               ("the 0.3.21 zone mining armor settings were added at the end", "the 0.3.22 metal ladder level bands were added at the end"),
               ("CONFIG 0.3.21 zone mining armor: added", "CONFIG 0.3.22 metal ladder levels: added"),
               ("could not add the 0.3.21 zone mining armor settings", "could not add the 0.3.22 metal ladder level bands")):
    assert _mig22.count(_a) == 1, _a
    _mig22 = _mig22.replace(_a, _b)
assert "0.3.21" not in _mig22 and "zm" not in _mig22 and "ZM_" not in _mig22, _mig22
MIG = ('''# ---- 0.3.22 ONE-TIME UPDATE migrate0322 (PROJECT-RULES section 4; tools/gear_0_3_22_patch.py item 4): the migrate0321 shape (zmUpdate ->
# m22Update on the M22_ block): a pure ADDITION at the END of the file, only the level.material rows the file lacks - in ANY case (the loader
# matches entries case-blind, so an admin's level.material.lead is kept, never doubled); null = the marker is already in a comment line
M(gcf, r"""
public static boolean has22(java.util.Properties pp, String k) {
  if (pp.getProperty(k) != null) return true;
  java.util.Enumeration en = pp.propertyNames();
  while (en.hasMoreElements()) {
    Object o = en.nextElement();
    if (o instanceof String && ((String) o).trim().equalsIgnoreCase(k)) return true;
  }
  return false;
}""")
M(gcf, r"""
''' + _m22u + '''
# setup(), right after migrate0321 and BEFORE load() + CfgPub.start: History copy verified first (lvSaved), atomic write (ISO-8859-1 bytes), one INFO
# line (+ one per note), gear.log; "" = nothing done (no file, marker already there, or a failure - WARN, file untouched, the next start tries again)
M(gcf, r"""
''' + _mig22 + '''
''')
before('''# ---- 0.2.16 ONE-TIME UPDATE migrate0216 (PROJECT-RULES section 4): a pure ADDITION, the 0.2.15 shape. null = the marker is already in a comment
''', MIG)
rep('''  @PKG@.GearCfg.migrate0321();          // 0.3.21: the zone mining armor block (a pure addition of the missing keys)
''', '''  @PKG@.GearCfg.migrate0321();          // 0.3.21: the zone mining armor block (a pure addition of the missing keys)
  @PKG@.GearCfg.migrate0322();          // 0.3.22: the new metals' level bands (a pure addition of the missing rows)
''')

# ================================================================================================================ 4: GearLL - the ladder table, the ore gate
after('''F(gll, "public static final int[] CROP_M = %s;" % jints([_m for _w, _m in LL_CROP]))
''', '''# 0.3.22 THE 15-STEP METAL LADDER: every metal word -> its ladder T (tools/tier_tags.py TOOL_METALS) + the word its tag shows; the ladder nouns
F(gll, "public static final String[] LT_W = %s;" % jarr([_w for _w, _t in TT.TOOL_METALS]))
F(gll, "public static final int[] LT_N = %s;" % jints([_t for _w, _t in TT.TOOL_METALS]))
F(gll, "public static final String[] LT_WORD = %s;" % jarr([TT.metal_word(_w) for _w, _t in TT.TOOL_METALS]))
F(gll, "public static final String[] LT_NOUN = %s;" % jarr(list(TT.LADDER)))
F(gll, "public static final int[] PICK_T = %s;" % jints(PICK_T))          # the pickaxe steps that exist (G2 adds its own)
F(gll, "public static final String[] PICK_ID = %s;" % jarr(PICK_ID))          # critic M1: the right-tier pickaxe of each step
F(gll, "public static final String DFLOOR = %s;" % jstr(ORE_FLOOR_DEF))
F(gll, "public static volatile Object[] OFC = null;")          # { String text, String[] words } the parsed gate.oreFloor
F(gll, "public static final double ORE_BASE = %r;" % ORE_BASE)
F(gll, "public static final String DORE = %s;" % jstr(ORE_TIERS_DEF))
F(gll, "public static final String DTP = %s;" % jstr(TIER_POW_DEF))
F(gll, "public static volatile Object[] OTC = null;")          # { String text, Object[] { String[] words, int[] normal, int[] half } }
F(gll, "public static volatile Object[] TPC = null;")          # { String text, double[] power }
''')
G22_LL = r'''# ---- 0.3.22 THE LADDER TIER of an item id (its first metal word from word 2 on, tools/tier_tags.py TOOL_METALS; 0 = none) + its tag
M(gll, r"""
public static int ltOfWord(String w) {
  if (w == null) return 0;
  for (int j = 0; j < LT_W.length; j++) if (LT_W[j].equalsIgnoreCase(w)) return LT_N[j];
  return 0;
}""")
M(gll, r"""
public static int ltier(String id) {
  if (id == null) return 0;
  String[] w = id.split("_");
  for (int i = 2; i < w.length; i++) {
    int t = ltOfWord(w[i]);
    if (t > 0) return t;
  }
  return 0;
}""")
M(gll, r"""
public static String ltag(String id, int from) {
  if (id == null) return "";
  String[] w = id.split("_");
  for (int i = from; i < w.length; i++) {
    for (int j = 0; j < LT_W.length; j++) if (LT_W[j].equalsIgnoreCase(w[i])) return "T" + LT_N[j] + " " + LT_WORD[j];
  }
  return "";
}""")
M(gll, "public static String lnoun(int t) { return t >= 1 && t <= LT_NOUN.length ? LT_NOUN[t - 1] : String.valueOf(t); }")
M(gll, r"""
public static int nextPick(int t) {
  for (int i = 0; i < PICK_T.length; i++) if (PICK_T[i] > t) return PICK_T[i];
  return 999;
}""")
# gate.oreTiers: "Ore:N[:H]" entries joined by commas (letters only, N 1-99, H 0..N-1, 0 / none = no half speed); null = not that shape
M(gll, r"""
public static Object[] oreParse(String v) {
  if (v == null) return null;
  String[] p = v.split(",");
  java.util.ArrayList ws = new java.util.ArrayList();
  java.util.ArrayList ns = new java.util.ArrayList();
  java.util.ArrayList hs = new java.util.ArrayList();
  for (int i = 0; i < p.length; i++) {
    String t = p[i].trim();
    if (t.length() == 0) continue;
    String[] c = t.split(":");
    if (c.length < 2 || c.length > 3) return null;
    String w = c[0].trim();
    if (w.length() == 0 || w.length() > 32) return null;
    for (int k = 0; k < w.length(); k++) if (!Character.isLetter(w.charAt(k))) return null;
    for (int k = 0; k < ws.size(); k++) if (((String) ws.get(k)).equalsIgnoreCase(w)) return null;
    int n = 0;
    int h = 0;
    try {
      n = Integer.parseInt(c[1].trim());
      if (c.length == 3) h = Integer.parseInt(c[2].trim());
    } catch (Throwable x) { return null; }
    if (n < 1 || n > 99 || h < 0 || h >= n) return null;
    ws.add(w);
    ns.add(Integer.valueOf(n));
    hs.add(Integer.valueOf(h));
    if (ws.size() > 64) return null;
  }
  if (ws.isEmpty()) return null;
  String[] wa = new String[ws.size()];
  int[] na = new int[ws.size()];
  int[] ha = new int[ws.size()];
  for (int i = 0; i < wa.length; i++) {
    wa[i] = (String) ws.get(i);
    na[i] = ((Integer) ns.get(i)).intValue();
    ha[i] = ((Integer) hs.get(i)).intValue();
  }
  return new Object[] { wa, na, ha };
}""")
M(gll, r"""
public static Object[] ores() {
  String v = @PKG@.GearCfg.ORE_TIERS;
  if (v == null) v = DORE;
  Object[] c = OTC;
  if (c != null && v.equals(c[0])) return (Object[]) c[1];
  Object[] t = oreParse(v);
  if (t == null) {
    @PKG@.Gear.warnOnce("oretiers:" + v, "config.properties: gate.oreTiers=" + v + " is not a list of Ore:normal tier[:half tier] - the default " + DORE + " is used");
    t = oreParse(DORE);
  }
  OTC = new Object[] { v, t };
  return t;
}""")
M(gll, r"""
public static String checkOreTiers(String key, String value) {
  if (value == null || oreParse(value) != null) return null;
  return "Write Ore:T:H entries joined by commas (letters, ladder tiers 1-99, the half tier below the normal one, 0 or left out = none), e.g. Copper:1,Iron:2:1.";
}""")
# the gate code of an ore word: normal T x 100 + half T (-1 = not in the table = never gated)
M(gll, r"""
public static int oreM(String w) {
  if (w == null) return -1;
  Object[] t = ores();
  String[] wa = (String[]) t[0];
  int[] na = (int[]) t[1];
  int[] ha = (int[]) t[2];
  for (int i = 0; i < wa.length; i++) if (wa[i].equalsIgnoreCase(w)) return na[i] * 100 + ha[i];
  return -1;
}""")
# tool.tierPower: 1-32 numbers > 0 (<= 1000000), T1 first; null = not that shape
M(gll, r"""
public static double[] tpParse(String v) {
  if (v == null) return null;
  String[] p = v.split(",");
  if (p.length < 1 || p.length > 32) return null;
  double[] a = new double[p.length];
  for (int i = 0; i < p.length; i++) {
    try { a[i] = Double.parseDouble(p[i].trim()); } catch (Throwable x) { return null; }
    if (Double.isNaN(a[i]) || !(a[i] > 0.0) || a[i] > 1000000.0) return null;
  }
  return a;
}""")
M(gll, r"""
public static double[] tpow() {
  String v = @PKG@.GearCfg.TIER_POW;
  if (v == null) v = DTP;
  Object[] c = TPC;
  if (c != null && v.equals(c[0])) return (double[]) c[1];
  double[] a = tpParse(v);
  if (a == null) {
    @PKG@.Gear.warnOnce("tierpow:" + v, "config.properties: tool.tierPower=" + v + " is not 1-32 numbers above 0 - the default " + DTP + " is used");
    a = tpParse(DTP);
  }
  TPC = new Object[] { v, a };
  return a;
}""")
M(gll, r"""
public static double tp(int t) {
  double[] a = tpow();
  int i = t < 1 ? 0 : (t > a.length ? a.length - 1 : t - 1);
  return a[i];
}""")
M(gll, r"""
public static String checkTierPower(String key, String value) {
  if (value == null || tpParse(value) != null) return null;
  return "Write 1-32 numbers above 0 joined by commas, T1 first, e.g. 1,1.4,1.96,2.74.";
}""")
# critic M1: gate.oreFloor = ore words joined by commas (letters only) that never break slower than their vanilla speed; null = not that shape
M(gll, r"""
public static String[] floorParse(String v) {
  if (v == null) return null;
  String[] p = v.split(",");
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < p.length; i++) {
    String t = p[i].trim();
    if (t.length() == 0) continue;
    if (t.length() > 32) return null;
    for (int k = 0; k < t.length(); k++) if (!Character.isLetter(t.charAt(k))) return null;
    l.add(t);
  }
  String[] a = new String[l.size()];
  for (int i = 0; i < a.length; i++) a[i] = (String) l.get(i);
  return a;
}""")
M(gll, r"""
public static boolean floorOre(String w) {
  if (w == null) return false;
  String v = @PKG@.GearCfg.ORE_FLOOR;
  if (v == null) v = DFLOOR;
  Object[] c = OFC;
  String[] a = null;
  if (c != null && v.equals(c[0])) a = (String[]) c[1];
  else {
    a = floorParse(v);
    if (a == null) {
      @PKG@.Gear.warnOnce("orefloor:" + v, "config.properties: gate.oreFloor=" + v + " is not a list of ore words - the default " + DFLOOR + " is used");
      a = floorParse(DFLOOR);
    }
    OFC = new Object[] { v, a };
  }
  for (int i = 0; i < a.length; i++) if (a[i].equalsIgnoreCase(w)) return true;
  return false;
}""")
M(gll, r"""
public static String checkOreFloor(String key, String value) {
  if (value == null || floorParse(value) != null) return null;
  return "Write ore words joined by commas, e.g. Lead,Chromium,Slag,Titanium (empty = none).";
}""")
# critic M1: the hit a slowed ore starts from = the vanilla power of the first existing pickaxe at / above its normal tier on this block's gather
# type (0.3.7's refPow rule), at least ORE_BASE
M(gll, r"""
public static double rpow(@TBTY@ bt, int n) {
  double r = ORE_BASE;
  try {
    int k = -1;
    for (int i = 0; i < PICK_T.length; i++) if (k < 0 && PICK_T[i] >= n) k = i;
    if (k < 0 || bt == null) return r;
    @ITM@ it = @PKG@.Gear.item(PICK_ID[k]);
    if (it == null || it.getTool() == null) return r;
    @TBGA@ g = bt.getGathering();
    @TBBD@ br = g == null ? null : g.getBreaking();
    String gt = br == null ? null : br.getGatherType();
    if (gt == null) return r;
    com.hypixel.hytale.server.core.asset.type.item.config.ItemToolSpec[] sp = it.getTool().getSpecs();
    for (int i = 0; sp != null && i < sp.length; i++) {
      if (sp[i] == null || sp[i].isIncorrect() || !gt.equals(sp[i].getGatherType())) continue;
      double p = (double) sp[i].getPower();
      return p > r ? p : r;
    }
  } catch (Throwable x) { }
  return r;
}""")
# the ore decision (decideI, a pickaxe / multitool in hand; m = oreM's code): int[] { result, 1, m, ladder T, fam, tiers below normal, normal T,
# 0, speed code } - 0 normal; 1 slow with code 4 half (gate.halfFactor), 1 one pickaxe step below (gate.nextFactor), 3 further (gate.twoUpFactor)
M(gll, r"""
public static int[] oreI(String id, int f, int m) {
  int n = m / 100;
  int h = m % 100;
  int t = ltier(id);
  if (t < 1) t = 1;
  if (t >= n) return new int[] { 0, 1, m, t, f, 0, n, 0, 0 };
  if (h > 0 && t >= h) return new int[] { 1, 1, m, t, f, n - t, n, 0, 4 };
  return new int[] { 1, 1, m, t, f, n - t, n, 0, nextPick(t) >= n ? 1 : 3 };
}""")
'''
before('''M(gll, r"""
public static int find(String[] w, int[] m, String x) {''', G22_LL)
rep('''  if (id.startsWith("Ore_") && w.length > 1) return new int[] { 1, find(ORE_W, ORE_M, w[1]) };''',
    '''  if (id.startsWith("Ore_") && w.length > 1) return new int[] { 1, oreM(w[1]) };          // 0.3.22: gate.oreTiers (normal x 100 + half)''')
rep('''  int t = tier(id);
  int te = t < 1 ? 1 : t;
  int fm = f >= 0 && f < FAMMAX.length ? FAMMAX[f] : 7;
  int sh = 0;''', '''  if (c == 1) return oreI(id, f, m);          // 0.3.22: ore by the 15-step ladder (gate.oreTiers; never refused)
  int t = tier(id);
  int te = t < 1 ? 1 : t;
  int fm = f >= 0 && f < FAMMAX.length ? FAMMAX[f] : 7;
  int sh = 0;''')
rep('''M(gll, "public static double slowF(int q) { return q == 1 ? @PKG@.GearCfg.GATE_NEXT : (q == 3 ? @PKG@.GearCfg.GATE_TWO : 1.0); }")''',
    '''M(gll, "public static double slowF(int q) { return q == 1 ? @PKG@.GearCfg.GATE_NEXT : (q == 3 ? @PKG@.GearCfg.GATE_TWO : (q == 4 ? @PKG@.GearCfg.GATE_HALF : 1.0)); }")          # 0.3.22: 4 = an ore's half speed''')
# the slow popup + the speed code of an ore hit (before the logs' one-up / two-up popup)
rep('''    N[1] = N[1] + 1L;
    if (pr != null && u != null) {
      long now = System.currentTimeMillis();
      Object l = SLOW.get(u);''', '''    if (d[1] == 1 && d.length > 8) {          // 0.3.22: an ore of gate.oreTiers - slow, never refused
      N[1] = N[1] + 1L;
      if (pr != null && u != null) {
        long now0 = System.currentTimeMillis();
        Object l0 = SLOW.get(u);
        if (!(l0 instanceof Long) || now0 - ((Long) l0).longValue() > 30000L) {
          SLOW.put(u, Long.valueOf(now0));
          double fx0 = slowF(d[8]);
          @PKG@.GearGate.popup(pr, u, icon, "Slow going", "This ore is above your " + tn + " (T" + d[3] + "): " + (fx0 > 0.0 ? @PKG@.Gear.fnum(1.0 / fx0) : "?") + "x the hits. A T" + d[6] + " " + lnoun(d[6]) + " pickaxe or better breaks it at full speed.");
        }
      }
      return d[8];
    }
    N[1] = N[1] + 1L;
    if (pr != null && u != null) {
      long now = System.currentTimeMillis();
      Object l = SLOW.get(u);''')
# the hit damage of a table ore: normal = max(vanilla, the ladder power), slow = a right-tier pickaxe's hit (then x the speed factor)
rep('''# fix round 2 (safety critic 2): your own lifelong stack that is not the registry's current one (and no journal names it) - the sweep retires''',
    '''# 0.3.22: the hit of a gate.oreTiers ore before the tool's own power (GearTool.onDamage) and the slow factor: at / above its normal tier
# max(vanilla, ORE_BASE x tool.tierPower[T] / tool.tierPower[normal]); slower = ORE_BASE (a right-tier pickaxe's hit); -1 = not such an ore hit
M(gll, r"""
public static float oreDr(@IS@ s, @TBTY@ bt, float d0) {
  try {
    if (!@PKG@.GearCfg.GATE_ON) return -1.0f;
    int[] cm = cat(bt);
    if (cm[0] != 1 || cm[1] < 100) return -1.0f;
    int[] d = decideC(s, 1, cm[1]);
    if (d[0] < 0 || d[0] == 2 || d.length < 9 || d[3] < 1) return -1.0f;
    if (d[0] == 1) {          // critic M1: from the right-tier pickaxe's own power; a gate.oreFloor ore never ends below vanilla (d0) after x slowF
      double rp = rpow(bt, d[6]);
      double f = slowF(d[8]);
      String bid = null;
      try { bid = bt.getId(); } catch (Throwable x2) { bid = null; }
      String[] bw = bid == null ? new String[0] : (bid.startsWith("*") ? bid.substring(1) : bid).split("_");
      if (f > 0.0 && bw.length > 1 && floorOre(bw[1]) && (double) d0 / f > rp) rp = (double) d0 / f;
      return (float) rp;
    }
    double p = ORE_BASE * tp(d[3]) / tp(d[6]);
    return p > (double) d0 ? (float) p : d0;
  } catch (Throwable x) { return -1.0f; }
}""")
# fix round 2 (safety critic 2): your own lifelong stack that is not the registry's current one (and no journal names it) - the sweep retires''')
rep('''    float dr = gq == 1 || gq == 3 ? @PKG@.GearLL.refPow(e.getItemInHand(), e.getBlockType(), d0) : d0;          // 0.3.7: from the right-tier tool's power
    float d1 = @PKG@.GearTool.onDamage(pr.getUuid(), e.getItemInHand(), e.getBlockType(), dr);
    if (gq == 1 || gq == 3) d1 = (float) ((double) d1 * @PKG@.GearLL.slowF(gq));          // 0.3.1: one up / two up''',
    '''    float od = @PKG@.GearLL.oreDr(e.getItemInHand(), e.getBlockType(), d0);          // 0.3.22: a gate.oreTiers ore (the ladder power / a right-tier hit)
    float dr = od >= 0.0f ? od : (gq == 1 || gq == 3 ? @PKG@.GearLL.refPow(e.getItemInHand(), e.getBlockType(), d0) : d0);          // 0.3.7: from the right-tier tool's power
    float d1 = @PKG@.GearTool.onDamage(pr.getUuid(), e.getItemInHand(), e.getBlockType(), dr);
    if (gq == 1 || gq == 3 || gq == 4) d1 = (float) ((double) d1 * @PKG@.GearLL.slowF(gq));          // 0.3.1: one up / two up; 0.3.22: 4 = an ore's half speed''')
rep('''", three up refused, crops two up refused, hands count as Crude on crops, bare hands "''',
    '''", logs three up refused, ore by its ladder tier (gate.oreTiers, half x" + @PKG@.Gear.fnum10(@PKG@.GearCfg.GATE_HALF) + ", never refused), crops two up refused, hands count as Crude on crops, bare hands "''')

# ================================================================================================================ 5: the pickaxe Mining Fortune
rep('''# { power x, Fortune +, Wisdom % + } of the held tool's perks: only a lifelong tool of the holder's own profile (others / off = { 1, 0, 0 })''',
    '''# 0.3.22: Fortune per Fortune level of kind k - the pickaxe (kind 0, and so the multitool's pickaxe side) lifelong.perkFortune.mining, else lifelong.perkFortune
M(gll, "public static double pfort(int k) { return k == 0 ? @PKG@.GearCfg.LL_PFORTM : @PKG@.GearCfg.LL_PFORT; }")
# { power x, Fortune +, Wisdom % + } of the held tool's perks: only a lifelong tool of the holder's own profile (others / off = { 1, 0, 0 })''')
rep('''  double fo = (double) perkEff(u, P, k, 1) * @PKG@.GearCfg.LL_PFORT;''',
    '''  double fo = (double) perkEff(u, P, k, 1) * pfort(k);          // 0.3.22: the pickaxe's Mining Fortune row''')
rep('''  if (p == 1) return "+" + @PKG@.Gear.fnum((double) lv * @PKG@.GearCfg.LL_PFORT) + " " + @PKG@.GearLL.KSKILL[k] + " Fortune";''',
    '''  if (p == 1) return "+" + @PKG@.Gear.fnum((double) lv * @PKG@.GearLL.pfort(k)) + " " + @PKG@.GearLL.KSKILL[k] + " Fortune";          // 0.3.22: pickaxe = the Mining row''')
rep('''"%, Fortune " + @PKG@.Gear.fnum(@PKG@.GearCfg.LL_PFORT) + " a level, "''',
    '''"%, Fortune " + @PKG@.Gear.fnum(@PKG@.GearCfg.LL_PFORT) + " a level (pickaxe " + @PKG@.Gear.fnum(@PKG@.GearCfg.LL_PFORTM) + "), "''')

# ================================================================================================================ 6: the shown tier numbers
rep('''# tools/tier_tags.py tier_for_level (weapon / armor band: Lv 0-9 T1, 10-14 T2, 15-19 T3, 20-24 T4, 25-34 T5, 35-39 T6, 40+ T7; Onyxium ids T8)
M(gvw, r"""
public static int tierFor(int lv, String id) {
  if (id != null && id.indexOf("Onyxium") >= 0) return 8;
  if (lv >= 40) return 7;
  if (lv >= 35) return 6;
  if (lv >= 25) return 5;
  if (lv >= 20) return 4;
  if (lv >= 15) return 3;
  if (lv >= 10) return 2;
  return 1;
}""")''', '''# tools/tier_tags.py tier_for_level (0.3.22: LEVEL_BANDS of the 15-step ladder - Lv 15 T2, 17 T3, 20 T4, 22 T5 ... 45 T14, 50 T15; Onyxium ids T16)
F(gvw, "public static final int[] LB_LO = %s;" % jints([_l for _l, _t in TT.LEVEL_BANDS]))
F(gvw, "public static final int[] LB_T = %s;" % jints([_t for _l, _t in TT.LEVEL_BANDS]))
F(gvw, "public static final int LB_ONYX = %d;" % TT.metal_tier("Onyxium"))
M(gvw, r"""
public static int tierFor(int lv, String id) {
  if (id != null && id.indexOf("Onyxium") >= 0) return LB_ONYX;
  for (int i = 0; i < LB_LO.length; i++) if (lv >= LB_LO[i]) return LB_T[i];
  return 1;
}""")
assert all(TT.tier_for_level(_lv) == next((_t for _l, _t in TT.LEVEL_BANDS if _lv >= _l), 1) for _lv in range(0, 101))''')
# the combat armor tag word: T1 below the Copper band start says Crude (tools/tier_tags.py level_tag) - as 0.3.21 showed Lv 0-9 armor
rep('''      int t = tierFor(@PKG@.GearLevel.band(id)[0], id);
      tg = "T" + t + " " + TT_NOUN[t - 1];''', '''      tg = @PKG@.GearLL.ltag(id, 1);          // critic M2: a metal word in the id first (Armor_Bronze_* = "T3 Bronze"; tools/tier_tags.py combat_tag)
      if (tg.length() == 0) {
        int b0 = @PKG@.GearLevel.band(id)[0];
        int t = tierFor(b0, id);
        tg = "T" + t + " " + (t == 1 && b0 < LB_CRUDE ? "Crude" : TT_NOUN[t - 1]);          // 0.3.22: tools/tier_tags.py level_tag
      }''')
rep('''F(gvw, "public static final int LB_ONYX = %d;" % TT.metal_tier("Onyxium"))''', '''F(gvw, "public static final int LB_ONYX = %d;" % TT.metal_tier("Onyxium"))
F(gvw, "public static final int LB_CRUDE = %d;" % TT.LEVEL_CRUDE)''')
rep('''  if (pi >= 0) return "T" + (pi + 1) + " " + @PKG@.GearLL.tname(pi);          // fix round (critic 3.2): Wooden = T1 Crude, Copper = T2, Iron = T3
  String[] w = id.split("_");
  for (int i = 1; i < w.length; i++) {
    for (int j = 0; j < @PKG@.GearLL.TW.length; j++) {
      if (!@PKG@.GearLL.TW[j].equalsIgnoreCase(w[i])) continue;
      int t = @PKG@.GearLL.TN[j];
      return "T" + (t + 1) + " " + @PKG@.GearLL.tname(t);
    }
  }
  return "";''', '''  if (pi >= 0) {          // fix round (critic 3.2): Wooden = Crude; 0.3.22: the 15-step ladder number (Wooden / Copper T1, Iron T2, Thorium T4)
    int pt = @PKG@.GearLL.ltOfWord(@PKG@.GearLL.tname(pi));
    return pt > 0 ? "T" + pt + " " + @PKG@.GearLL.tname(pi) : "";
  }
  return @PKG@.GearLL.ltag(id, 1);          // 0.3.22: "T7 Cobalt", "T1 Crude" (tools/tier_tags.py TOOL_METALS)''')

# ================================================================================================================ 7: manifest
rep('''ZONE MINING SETS: Lead, Dusk, Chromium, Azurvane, Slag, Cinder, Titanium and Lumen Mining Sets on the vanilla armor models''',
    '''15-STEP METAL LADDER: tier tags T1 Copper .. T15 Lumen (Onyxium T16), ore mined by ladder tier (gate.oreTiers, never refused), pickaxe Mining Fortune +10 a level. ZONE MINING SETS: Lead, Dusk, Chromium, Azurvane, Slag, Cinder, Titanium and Lumen Mining Sets on the vanilla armor models''')

# ================================================================================================================ checks on the result
_i = s.index
assert _i("G22_ORE = [") < _i("CFG_ROWS = [") < _i("LL_ORE = [") < _i("0.3.22: every 0.3.0 ore stays gated") < _i("LL_PERKS = [")
assert _i("public static int[] oreI(String id, int f, int m)") < _i("public static int[] catOf(String bid)") < _i("public static int[] decideI(String id, int c, int m)")
assert _i("public static double tp(int t)") < _i("public static float oreDr(") and _i("public static float refPow(") < _i("public static float oreDr(")
assert _i("public static double pfort(int k)") < _i("public static double[] perkFx(")
assert _i("public static boolean has22(") < _i("public static Object[] m22Update(String text)") < _i("public static synchronized String migrate0322()") < _i("@PKG@.GearCfg.migrate0322();")
assert _i("@PKG@.GearCfg.migrate0321();") < _i("@PKG@.GearCfg.migrate0322();")
assert s.count("registerSystem(") == SYS0, "no new system"
assert s.count("registerCommand(") == CMD0, "no new command"
_u = s
for _new, _old, _cnt in reversed(CHANGES):
    assert _u.count(_new) == _cnt, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old)
assert _u == OLD, "the generated script differs from 0.3.21 outside the recorded changes"
compile(s, DST, "exec")
open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(DST, ROOT), "(%d lines; 0.3.21 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
