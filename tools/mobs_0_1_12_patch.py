"""Derive SkyyMobs/build_skyymobs_0.1.12.py from the GENERATED 0.1.11 (build_skyymobs_0.1.11.py = the tools/deploy_set.py SET pin, made by
tools/mobs_0_1_11_patch.py). Every anchor is asserted; at the end every change is undone on a copy and compared with 0.1.11; line endings kept.
Run:  python tools/mobs_0_1_12_patch.py [--out <path>]   then   python SkyyMobs/build_skyymobs_0.1.12.py   then
      python SkyyMobs/test_skyymobs_0.1.12.py      (never --deploy; --static = the text checks only, no jars needed)
Edit THIS file, never the generated script. --out writes the result somewhere else (the harness's determinism check).

0.1.12 (2026-10-18) = 20 LEVELS PER ZONE (research/Level-Bands-20-Spec.md 1 + 2.5 + 4.1, round level-bands; tools/tier_tags.py TT_VERSION 3).
  Skyy (docs/answered/gear.md 2026-10-18): "im changing it so we have 20 levels per zone" + on the band table "perfect! make sure all the gear
  follows that ... (this way it takes 5 rebirths to reach lvl 100 and get to the end of zone 5." Spec Q4 default: Zone 1 1-20 (unchanged),
  2 20-40, 3 40-60, 4 60-80, 5 80-100.
  1. THE ZONE TOPS = tools/tier_tags.py ZONE_TOPS (20 40 60 80 100; was 20 30 45 60 75 = ZONE_TOPS_V2): bosses.zoneTops default, the build's
     zone checks (ZONE_TOPS / ZONE_FLOORS: Zone 1 1-20, 2 20-40, 3 40-60, 4 60-80), the Python mirror of MobBossFn.zoneOf = TT.zone_of_level
     for every level 1-150 (a Zone 3 boss counts as Zone 3 for SkyyGear's Mythic bags), the Server Setup hint, the manifest text.
  2. EVERY DEFAULT BAND ROW is mapped through the old -> new zone anchors (1 -> 1, 20 -> 20, 30 -> 40, 45 -> 60, 60 -> 80, 75 -> 100; straight
     lines inside a zone, rounded half up): biome / env / zone rows (Zone2_Tier1.* 20-24 -> 20-28, Zone2_Tier3.* 27-30 -> 34-40,
     Zone3_Tier1.* 30-34 -> 40-45, Zone3_Tier3.* 41-45 -> 55-60, Zone4_Tier4.* 45-50 -> 60-67, Zone4_Tier5.* 53-60 -> 71-80); the build prints
     every moved row. Zone 1 rows and the goblin portal rows are unchanged (asserted); env bonuses unchanged. The level colours (plate.colors,
     keyed by a band's lowest level) 1 / 20 / 30 / 45 / 61 -> 1 / 20 / 40 / 60 / 81 (same colours). levels.max 100 stays; no world. rows.
     The zone headings in bands.properties and the zoneTops comment in config.properties say the new numbers.
  3. THE LEVEL CURVE STRETCHED TO LV 100 (Skyy 2026-10-18 popup "Mob levels now go to 100, but the mob strength curve stops growing at Lv 60
     ... Stretch the curve to Lv 100?" -> "Stretch to Lv 100 (Rec.)"): the 8 curve tables (curve.hp / curve.dmg x easy / normal / hard /
     custom) keep their factors, each point moved through the same zmap as the bands: 1 20 25 30 35 40 45 49 55 60 -> 1 20 30 40 47 53 60 65
     73 80, plus a point at Lv 100 = the last segment (Lv 55 -> 60) carried on over the old Zone 5 (60 -> 75): Hard health x28.98 -> x35.07,
     damage x8.78 -> x10.19 at Lv 100. A mob at its new level is within 2.3 % of the same mob at its old level (Zone 2 Lv 40 = the old Lv 30
     exactly), and strength keeps rising through Zone 5. Per level (strength.shape linear): unchanged - its hpCap / dmgCap are multiplier caps,
     not levels. 0.1.11's One hit at most (strength.hitCap 35 %) stays the safety on both shapes.
  4. MIGRATION MobMig12 (PROJECT-RULES 4; MobMig11's reviewed machinery + MobMig.mgKit / mgSaved): ONCE on an EXISTING config.properties (setup,
     after MobMig11, before MobCfg.load). config.properties: bosses.zoneTops still exactly "20 30 45 60 75" -> "20 40 60 80 100" (Skyy's live
     file has no such line = nothing to do, the new code default applies); plate.colors.30 / .45 / .61 still holding their default colour ->
     the same colour at .40 / .60 / .81 (a key rename; skipped + noted when the new key already exists); the exact old zoneTops comment line ->
     the new one; each curve table whose points are ALL still exactly its 0.1.11 defaults is replaced whole by the stretched points (at its
     first line; a table with any edited point is kept + noted). bands.properties: every biome. / env. / zone. row whose LAST entry is a one-line entry holding exactly its 0.1.11 default
     text -> the 0.1.12 default (value text only); the exact old zone heading comment lines -> the new ones. A hand-edited value is kept (one
     INFO line lists them). A verified config-history copy of EACH changed file first (MobMig.mgSaved), bands.properties written before
     config.properties (which gets the run-once marker, so a crash in between retries only what is still old); one config-changes.log line
     per change in the kit's table format (bands.biome[Zone2_Tier1] 20|24 -> 20|28; a colour move = plate.colors[30] #E8A93B -> (none) +
     plate.colors[40] (none) -> #E8A93B) - Undo in Server Setup -> Changes; bytes + line endings kept; a java.util.Properties check per file
     (only the planned keys differ). A fresh file carries the marker (never migrated).
SAVED DATA: none besides that one config update. Mobs already spawned keep their level (a band change only reaches new spawns). No new
command, no new system, no new bridge key (asserted below). One new class MobMig12.
ROLLBACK 0.1.12 -> 0.1.11: safe for items and mobs. The migrated rows stay (0.1.11 reads them as admin values: Zone 2-4 mobs keep the new
levels); Undo them in Server Setup -> Changes first if the old bands are wanted back. Roll back together with the level-bands set (Gear,
Armory, Collections, Bazaar, Auctions).
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyMobs", "build_skyymobs_0.1.11.py")
DST = os.path.join(ROOT, "SkyyMobs", "build_skyymobs_0.1.12.py")
if "--out" in sys.argv:
    DST = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.1.11"' in s and s.startswith('"""SkyyMobs 0.1.11 - build script'), "build_skyymobs_0.1.11.py is not the SET pin 0.1.11"
assert "MobMig12" not in s and "zmap(" not in s and "tier_tags" not in s
SYS0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
PUT0 = s.count("bridge().put(")
CHANGES = []


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:160])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.1.12 (2026-10-18)"):].rstrip() + "\n\n"

# ================================================================================================================ header + version
rep('''"""SkyyMobs 0.1.11 - build script (javassist via jpype). GENERATED by tools/mobs_0_1_11_patch.py from the SET pin 0.1.10 - edit the
patch, never this file. Run: python SkyyMobs/build_skyymobs_0.1.11.py -> SkyyMobs/SkyyMobs-0.1.11.jar (never --deploy).
Test: python SkyyMobs/test_skyymobs_0.1.11.py   (--static: the text checks only)

''', '''"""SkyyMobs 0.1.12 - build script (javassist via jpype). GENERATED by tools/mobs_0_1_12_patch.py from the SET pin 0.1.11 - edit the
patch, never this file. Run: python SkyyMobs/build_skyymobs_0.1.12.py -> SkyyMobs/SkyyMobs-0.1.12.jar (never --deploy).
Test: python SkyyMobs/test_skyymobs_0.1.12.py   (--static: the text checks only)

''' + NOTE + '''0.1.11 (the base, everything below is still true unless 0.1.12 above says otherwise):
''')
rep('VERSION = "0.1.11"', 'VERSION = "0.1.12"')

# ================================================================================================================ the class list
rep('''m11 = pool.makeClass(PKG + ".MobMig11")    # 0.1.11: the one-time hit cap 0 -> 35 + Boss roles without elites update of config.properties
pl = pool.makeClass(PKG + ".SkyyMobsPlugin", pool.get(G["JP"]))
ALL = [lg, gb, bd, mi, cfg, lv, hk, dm, dmu, fn, ps, sc, pt, rf, mh, mc, mm, gp, gd, gdu, ifn, m14, lat, mcr, crs, cfn, sfn, bfn, m11]
''', '''m11 = pool.makeClass(PKG + ".MobMig11")    # 0.1.11: the one-time hit cap 0 -> 35 + Boss roles without elites update of config.properties
m12 = pool.makeClass(PKG + ".MobMig12")    # 0.1.12: the one-time 20-levels-per-zone update of config.properties + bands.properties
pl = pool.makeClass(PKG + ".SkyyMobsPlugin", pool.get(G["JP"]))
ALL = [lg, gb, bd, mi, cfg, lv, hk, dm, dmu, fn, ps, sc, pt, rf, mh, mc, mm, gp, gd, gdu, ifn, m14, lat, mcr, crs, cfn, sfn, bfn, m11, m12]
''')

ZMAP_SRC = '# the old -> new zone anchors (Lv 1 and every zone top); a level between two anchors moves on the straight line, rounded half up\nZONE_ANCHORS = [(1, 1)] + list(zip(TT.ZONE_TOPS_V2, TT.ZONE_TOPS))\n\n\ndef zmap(v):\n    """a 0.1.11 band level -> its 0.1.12 level (Zone 1 = itself)"""\n    for (_a, _b), (_c, _d) in zip(ZONE_ANCHORS, ZONE_ANCHORS[1:]):\n        if _a <= v <= _c:\n            return int(_b + (v - _a) * float(_d - _b) / (_c - _a) + 0.5)\n    raise AssertionError("zmap: %r outside 1-%d" % (v, ZONE_ANCHORS[-1][0]))\n\n\nassert [zmap(_v) for _v in (1, 7, 20, 24, 27, 30, 34, 41, 45, 50, 53, 60, 61, 75)] == [1, 7, 20, 28, 34, 40, 45, 55, 60, 67, 71, 80, 81, 100]\nassert all(zmap(_v) <= zmap(_v + 1) for _v in range(1, 75)), "zmap keeps the order (a band\'s min stays <= its max)"\n'

# ================================================================================================================ 2b. the Level curve stretched to Lv 100
rep('''        assert CURVES[(_k, "easy")][_i][1] <= CURVES[(_k, "normal")][_i][1] <= CURVES[(_k, "hard")][_i][1]
SHAPE_OPTS = "curve|Level curve,linear|Per level"
''', '''        assert CURVES[(_k, "easy")][_i][1] <= CURVES[(_k, "normal")][_i][1] <= CURVES[(_k, "hard")][_i][1]
# 0.1.12 (Skyy 2026-10-18 popup "Mob levels now go to 100, but the mob strength curve stops growing at Lv 60 ... Stretch the curve to Lv 100?"
# -> "Stretch to Lv 100 (Rec.)"): every Level curve point moves to its level in the 20-levels-per-zone map (zmap, the same map as the bands:
# 20 stays 20, 30 -> 40, 45 -> 60, 60 -> 80, 75 -> 100), the factors unchanged - a Zone N mob is about as strong as the old Zone N mob - plus a
# point at Lv 100 = the last segment (Lv 55 -> 60) carried on over the old Zone 5 (60 -> 75), so strength keeps rising through Zone 5. The
# checks above stay on the 0.1.11 tables (CURVES_011, the spec's numbers); MobMig12 moves a file's table only while it is exactly that.
import tier_tags as TT        # 0.1.12: THE band table (tools/tier_tags.py TT_VERSION 3, research/Level-Bands-20-Spec.md 1)
assert TT.TT_VERSION == "3", "0.1.12 needs tools/tier_tags.py TT_VERSION 3 (20 levels per zone)"
@ZMAP@
CURVES_011 = CURVES
CURVE_DEF_TEXT_011 = CURVE_DEF_TEXT


def _stretch(p):
    (_l55, _v55), (_l60, _v60) = p[-2], p[-1]
    _top = round(_v60 + (_v60 - _v55) * float(TT.ZONE_TOPS_V2[-1] - _l60) / (_l60 - _l55), 2)
    return [(zmap(_a), _b) for _a, _b in p] + [(TT.ZONE_TOPS[-1], _top)]


CURVES = dict((_kd, _stretch(_p)) for _kd, _p in CURVES_011.items())
CURVE_DEV = [0.0]
CURVE_DEF_TEXT = [",".join("%d:%s" % (a, num(b)) for a, b in CURVES[kd]) for kd in CURVE_IDX]
for _kd, _p in CURVES.items():
    assert [a for a, _b in _p] == [1, 20, 30, 40, 47, 53, 60, 65, 73, 80, 100], (_kd, _p)
    assert all(_p[i][1] < _p[i + 1][1] for i in range(len(_p) - 1)), "0.1.12: %s rises at every point up to Lv 100" % (_kd,)
    for _L in range(1, 61):       # a mob at its new level is about as strong as at its old level (the points exactly, between them < 4 %)
        _x = next(_bb + (_L - _aa) * float(_dd - _bb) / (_cc - _aa) for (_aa, _bb), (_cc, _dd) in zip(ZONE_ANCHORS, ZONE_ANCHORS[1:]) if _aa <= _L <= _cc)
        _o, _n = curve_eval(CURVES_011[_kd], _L), curve_eval(_p, _x)
        assert abs(_n - _o) <= 0.04 * _o, (_kd, _L, _o, _n)
        CURVE_DEV[0] = max(CURVE_DEV[0], abs(_n - _o) / _o)
    assert curve_eval(_p, 40) == curve_eval(CURVES_011[_kd], 30), "0.1.12: a Zone 2 Lv 40 mob = the old Lv 30"
for _k in CURVE_KINDS:
    for _i in range(11):
        assert CURVES[(_k, "easy")][_i][1] <= CURVES[(_k, "normal")][_i][1] <= CURVES[(_k, "hard")][_i][1]
print("0.1.12 Level curve stretched to Lv 100: points 1 20 30 40 47 53 60 65 73 80 100; old Lv L vs new Lv zmap(L) at most %.1f %% apart; Hard Lv 100 = health x%s / damage x%s"
      % (100 * CURVE_DEV[0], num(CURVES[("hp", "hard")][-1][1]), num(CURVES[("dmg", "hard")][-1][1])))
assert CURVES[("hp", "hard")][-1] == (100, 35.07) and CURVES[("dmg", "hard")][-1] == (100, 10.19), (CURVES[("hp", "hard")][-1], CURVES[("dmg", "hard")][-1])
SHAPE_OPTS = "curve|Level curve,linear|Per level"
'''.replace("@ZMAP@", ZMAP_SRC))
rep('''sum(1 for ln in CFG_LINES if ln.startswith("curve.")) == 80''', '''sum(1 for ln in CFG_LINES if ln.startswith("curve.")) == 88   # 0.1.12: 8 x 11 points''')

# ================================================================================================================ 1. the zone tops (tier_tags)
rep('''BOSS_TOPS_DEF = "20 30 45 60 75"
''', '''import tier_tags as TT        # 0.1.12: THE band table (tools/tier_tags.py TT_VERSION 3, research/Level-Bands-20-Spec.md 1)
assert TT.TT_VERSION == "3", "0.1.12 needs tools/tier_tags.py TT_VERSION 3 (20 levels per zone)"
assert tuple(TT.ZONE_TOPS) == (20, 40, 60, 80, 100) and tuple(TT.ZONE_TOPS_V2) == (20, 30, 45, 60, 75), (TT.ZONE_TOPS, TT.ZONE_TOPS_V2)
BOSS_TOPS_011 = " ".join(str(_t) for _t in TT.ZONE_TOPS_V2)      # the 0.1.10 / 0.1.11 default (what MobMig12 moves)
assert BOSS_TOPS_011 == "20 30 45 60 75"
BOSS_TOPS_DEF = " ".join(str(_t) for _t in TT.ZONE_TOPS)        # 0.1.12: 20 levels per zone
assert BOSS_TOPS_DEF == "20 40 60 80 100"
# (zmap + ZONE_ANCHORS: defined with the Level curve stretch above, 0.1.12)
''')
rep('''assert boss_tops(BOSS_TOPS_DEF, 100) == [20, 30, 45, 60, 75] and boss_tops(BOSS_TOPS_DEF, 74) is None
assert [boss_zone(h, [20, 30, 45, 60, 75]) for h in (1, 20, 21, 30, 31, 45, 46, 60, 61, 75, 76, 90)] == [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 5, 5]
''', '''assert boss_tops(BOSS_TOPS_011, 100) == [20, 30, 45, 60, 75] and boss_tops(BOSS_TOPS_011, 74) is None
assert [boss_zone(h, [20, 30, 45, 60, 75]) for h in (1, 20, 21, 30, 31, 45, 46, 60, 61, 75, 76, 90)] == [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 5, 5]
# 0.1.12: the new default tops = tools/tier_tags.py ZONE_TOPS; MobBossFn.zoneOf's mirror = TT.zone_of_level at every level 1-150
assert boss_tops(BOSS_TOPS_DEF, 100) == list(TT.ZONE_TOPS) and boss_tops(BOSS_TOPS_DEF, 99) is None
assert [boss_zone(h, list(TT.ZONE_TOPS)) for h in (1, 20, 21, 40, 41, 60, 61, 80, 81, 100, 101, 150)] == [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 5, 5]
assert all(boss_zone(_h, list(TT.ZONE_TOPS)) == TT.zone_of_level(_h) for _h in range(1, 151)), "0.1.12: boss zone = TT.zone_of_level"
''')

# ================================================================================================================ 2. the band tables
rep('''# (key, min, max). Zone 1 1-20, Zone 2 20-30, Zone 3 30-45, Zone 4 45-60.
BIOME_ROWS = [''', '''# (key, min, max). Zone 1 1-20, Zone 2 20-30, Zone 3 30-45, Zone 4 45-60 = the 0.1.11 numbers; 0.1.12 maps every row through zmap below
# (Zone 1 1-20, Zone 2 20-40, Zone 3 40-60, Zone 4 60-80 - 20 levels per zone).
BIOME_ROWS = [''')
rep('''ZONE_ROWS = [("Zone1", 1, 7), ("Zone2", 20, 24), ("Zone3", 30, 34), ("Zone4", 45, 50)]
''', '''ZONE_ROWS = [("Zone1", 1, 7), ("Zone2", 20, 24), ("Zone3", 30, 34), ("Zone4", 45, 50)]
# 0.1.12: 20 levels per zone - the 0.1.11 tables kept for MobMig12 + the checks, every level mapped through zmap (bonuses unchanged)
BIOME_ROWS_011, ENV_ROWS_011, ZONE_ROWS_011 = list(BIOME_ROWS), list(ENV_ROWS), list(ZONE_ROWS)
BIOME_ROWS = [(_k, zmap(_a), zmap(_b)) for _k, _a, _b in BIOME_ROWS_011]
ENV_ROWS = [(_k, zmap(_a), zmap(_b), _c) for _k, _a, _b, _c in ENV_ROWS_011]
ZONE_ROWS = [(_k, zmap(_a), zmap(_b)) for _k, _a, _b in ZONE_ROWS_011]
assert ZONE_ROWS == [("Zone1", 1, 7), ("Zone2", 20, 28), ("Zone3", 40, 45), ("Zone4", 60, 67)], ZONE_ROWS
for _o, _n in zip(BIOME_ROWS_011 + ENV_ROWS_011, BIOME_ROWS + ENV_ROWS):
    if _o[0].startswith(("Zone1", "Env_Zone1", "Env_Portal_")):
        assert _o == _n, "0.1.12: Zone 1 / the goblin portals must not change: %r" % (_o,)
_bx = dict((_k, (_a, _b)) for _k, _a, _b in BIOME_ROWS)
assert (_bx["Zone2_Tier1.*"], _bx["Zone2_Tier3.*"], _bx["Zone3_Tier1.*"], _bx["Zone3_Tier3.*"], _bx["Zone4_Tier4.*"], _bx["Zone4_Tier5.*"]) == \\
    ((20, 28), (34, 40), (40, 45), (55, 60), (60, 67), (71, 80)), "spec 2.5's examples"
''')
rep('''ZONE_TOPS = {1: 20, 2: 30, 3: 45, 4: 60}
ZONE_FLOORS = {1: 1, 2: 20, 3: 30, 4: 45}
''', '''ZONE_TOPS = dict((_z, TT.ZONE_TOPS[_z - 1]) for _z in (1, 2, 3, 4))                       # 0.1.12: {1: 20, 2: 40, 3: 60, 4: 80}
ZONE_FLOORS = dict((_z, 1 if _z == 1 else TT.ZONE_TOPS[_z - 2]) for _z in (1, 2, 3, 4))     # 0.1.12: {1: 1, 2: 20, 3: 40, 4: 60}
assert ZONE_TOPS == {1: 20, 2: 40, 3: 60, 4: 80} and ZONE_FLOORS == {1: 1, 2: 20, 3: 40, 4: 60}
''')
rep('''COLOR_ROWS = [("1", SUI.COLOR["rowName"]), ("20", SUI.COLOR["warning"]), ("30", SUI.COLOR["gold"]), ("45", SUI.COLOR["error"]),
              ("61", SUI.RARITY["Mythic"])]
''', '''COLOR_ROWS = [("1", SUI.COLOR["rowName"]), ("20", SUI.COLOR["warning"]), ("30", SUI.COLOR["gold"]), ("45", SUI.COLOR["error"]),
              ("61", SUI.RARITY["Mythic"])]
COLOR_ROWS_011 = list(COLOR_ROWS)
COLOR_ROWS = [(str(zmap(int(_k))), _v) for _k, _v in COLOR_ROWS_011]     # 0.1.12: 1 / 20 / 40 / 60 / 81, the same colours
assert [_k for _k, _v in COLOR_ROWS] == ["1", "20", "40", "60", "81"]
''')
rep('''BIOME_ROWS = expand_biomes(BIOME_PATTERNS)
''', '''BIOME_ROWS = expand_biomes(BIOME_PATTERNS)
BIOME_ROWS_011X = expand_biomes(BIOME_ROWS_011)       # 0.1.12: the 0.1.11 shipped rows (same keys, same order - zmap is per number)
assert [r[0] for r in BIOME_ROWS_011X] == [r[0] for r in BIOME_ROWS]
assert all((zmap(o[1]), zmap(o[2])) == (n[1], n[2]) for o, n in zip(BIOME_ROWS_011X, BIOME_ROWS))
''')
rep('''ENV_ROWS = expand_envs(ENV_PATTERNS)
''', '''ENV_ROWS = expand_envs(ENV_PATTERNS)
ENV_ROWS_011X = expand_envs(ENV_ROWS_011)             # 0.1.12: the 0.1.11 shipped rows
assert [r[0] for r in ENV_ROWS_011X] == [r[0] for r in ENV_ROWS]
assert all((zmap(o[1]), zmap(o[2]), o[3]) == (n[1], n[2], n[3]) for o, n in zip(ENV_ROWS_011X, ENV_ROWS))
''')
rep('''    zname = {1: "Zone 1 Emerald Wilds: Lv 1-20 (the blue forest Forest_Azure, Autumn and Moss at the top)",
             2: "Zone 2 Howling Sands: Lv 20-30", 3: "Zone 3 Whisperfrost Frontiers: Lv 30-45", 4: "Zone 4 Devastated Lands: Lv 45-60"}
''', '''    zname = ZNAME          # 0.1.12: the headings say the new zone bands (ZNAME_011 = the 0.1.11 text MobMig12 swaps)
''')
rep('''def _band_lines():
''', '''ZNAME_011 = {1: "Zone 1 Emerald Wilds: Lv 1-20 (the blue forest Forest_Azure, Autumn and Moss at the top)",
             2: "Zone 2 Howling Sands: Lv 20-30", 3: "Zone 3 Whisperfrost Frontiers: Lv 30-45", 4: "Zone 4 Devastated Lands: Lv 45-60"}
ZNAME = dict(ZNAME_011)
for _z, _nm in ((2, "Howling Sands"), (3, "Whisperfrost Frontiers"), (4, "Devastated Lands")):
    ZNAME[_z] = "Zone %d %s: Lv %d-%d" % (_z, _nm, ZONE_FLOORS[_z], ZONE_TOPS[_z])
assert ZNAME[2] == "Zone 2 Howling Sands: Lv 20-40" and ZNAME[4] == "Zone 4 Devastated Lands: Lv 60-80" and ZNAME[1] == ZNAME_011[1]


def _band_lines():
''')
TOPS_DOC_011 = "# Top level of zones 1, 2, 3 ... (Zone 1 = Lv 1-20, 2 = 20-30, 3 = 30-45, 4 = 45-60, 5 = 60-75). A boss's zone = the first top at"
rep('''    "%s",
    "# or above the top of the level band where it dies (no band there: its own level).",
''' % TOPS_DOC_011, '''    TOPS_DOC,           # 0.1.12: the new zone tops (TOPS_DOC_011 = the 0.1.11 line MobMig12 swaps)
    "# or above the top of the level band where it dies (no band there: its own level).",
''')
rep('''    MG11_MARK,          # 0.1.11: the fresh file carries MobMig11's run-once marker (never migrated)
]
''', '''    MG11_MARK,          # 0.1.11: the fresh file carries MobMig11's run-once marker (never migrated)
    MG12_MARK,          # 0.1.12: the fresh file carries MobMig12's run-once marker (never migrated)
]
''')
rep('''assert CFG_TEXT.count(MG11_MARK_ID) == 1 and "\\nstrength.hitCap=%d\\n" % HITCAP_DEF in CFG_TEXT and "\\nbosses.roles=" + BOSS_ROLES_DEF + "\\n" in CFG_TEXT
''', '''assert CFG_TEXT.count(MG11_MARK_ID) == 1 and "\\nstrength.hitCap=%d\\n" % HITCAP_DEF in CFG_TEXT and "\\nbosses.roles=" + BOSS_ROLES_DEF + "\\n" in CFG_TEXT
assert CFG_TEXT.count(MG12_MARK_ID) == 1 and "\\nbosses.zoneTops=20 40 60 80 100\\n" in CFG_TEXT and TOPS_DOC in CFG_TEXT and TOPS_DOC_011 not in CFG_TEXT
assert "\\nplate.colors.40=" in CFG_TEXT and "\\nplate.colors.30=" not in CFG_TEXT and "\\nplate.colors.81=" in CFG_TEXT
''')
# the marker + the zoneTops comment (defined next to MobMig11's, before CFG_LINES)
rep('''assert MG11_MARK_ID not in MG_MARK + MG14_MARK and MG_MARK_ID not in MG11_MARK and MG14_MARK_ID not in MG11_MARK
''', '''assert MG11_MARK_ID not in MG_MARK + MG14_MARK and MG_MARK_ID not in MG11_MARK and MG14_MARK_ID not in MG11_MARK
# 0.1.12: MobMig12's marker (fresh file + every updated file), History title, change-log name + the zoneTops comment line
import tier_tags as TT        # 0.1.12 (imported again below, next to the zone tops; pure Python)
MG12_MARK_ID = "SkyyMobs 0.1.12 level bands update"
MG12_MARK = ("# %s (2026-10-18): 20 levels per zone - zone tops %s (was %s); Zone 2-4 band rows and level colours moved, Zone 1 unchanged"
             % (MG12_MARK_ID, " ".join(str(_t) for _t in TT.ZONE_TOPS), " ".join(str(_t) for _t in TT.ZONE_TOPS_V2)))
MG12_WHO = "SkyyMobs 0.1.12"
MG12_WHAT = "before the 0.1.12 level bands update"
TOPS_DOC_011 = "@TOPS011@"
TOPS_DOC = ("# Top level of zones 1, 2, 3 ... (Zone 1 = Lv 1-%d, 2 = %d-%d, 3 = %d-%d, 4 = %d-%d, 5 = %d-%d). A boss's zone = the first top at"
            % (TT.ZONE_TOPS[0], TT.ZONE_TOPS[0], TT.ZONE_TOPS[1], TT.ZONE_TOPS[1], TT.ZONE_TOPS[2], TT.ZONE_TOPS[2], TT.ZONE_TOPS[3],
               TT.ZONE_TOPS[3], TT.ZONE_TOPS[4]))
assert TOPS_DOC == "# Top level of zones 1, 2, 3 ... (Zone 1 = Lv 1-20, 2 = 20-40, 3 = 40-60, 4 = 60-80, 5 = 80-100). A boss's zone = the first top at"
for _t in (MG12_MARK, TOPS_DOC, TOPS_DOC_011):
    assert _t.startswith("# ") and all(32 <= ord(_c) < 127 for _c in _t) and '"' not in _t and "@" not in _t, _t
assert "=" not in MG12_MARK
assert MG12_MARK_ID not in MG_MARK + MG14_MARK + MG11_MARK and MG11_MARK_ID not in MG12_MARK
'''.replace("@TOPS011@", TOPS_DOC_011))

# ================================================================================================================ Java texts
rep('''  if (@PKG@.MobCfg.tops(value, mx) == null) return "Type 1-10 whole numbers going up, each 1-" + mx + ", like 20 30 45 60 75.";''',
    '''  if (@PKG@.MobCfg.tops(value, mx) == null) return "Type 1-10 whole numbers going up, each 1-" + mx + ", like 20 40 60 80 100.";''')
rep('''                 "(Zone 1 Lv 1-20, Zone 2 20-30, Zone 3 30-45, Zone 4 45-60), more health and damage per level with a difficulty "''',
    '''                 "(Zone 1 Lv 1-20, Zone 2 20-40, Zone 3 40-60, Zone 4 60-80, Zone 5 80-100), more health and damage per level with a difficulty "''')

# ================================================================================================================ 4. MobMig12
MIG12 = r'''# ---------------------------------------------------------------- MobMig12 (0.1.12): the one-time 20-levels-per-zone update
# PROJECT-RULES 4 (MobMig11's rules on TWO files): a key whose LAST entry is a one-line entry holding exactly its 0.1.11 default moves (value
# text only; a colour row = the same colour under its new level key, skipped + noted when that key already exists); an admin's own value is
# kept (INFO); a missing line = nothing; the exact old comment lines -> the new ones; a verified History copy of each changed file
# (MobMig.mgKit / mgSaved); bands.properties written first, then config.properties with the run-once marker; one config-changes.log line per
# change in the kit's table format (Undo in Server Setup -> Changes); every other byte and the line endings kept; a Properties check per file.
# setup() runs it after MobMig11.run and BEFORE MobCfg.load. Plain java.* + the kit's classes: a bare JVM runs it on scratch copies.
def _m12_rows():
    """config rows (key, old, new, new key or '', log key, new log key or '') + bands rows (key, old, new, log key, log old, log new)"""
    c = [("bosses.zoneTops", BOSS_TOPS_011, BOSS_TOPS_DEF, "", "bosses.zoneTops", "")]
    for (k0, v0), (k1, v1) in zip(COLOR_ROWS_011, COLOR_ROWS):
        assert v0 == v1
        if k0 != k1:
            c.append(("plate.colors." + k0, v0, v0, "plate.colors." + k1, "plate.colors[%s]" % k0, "plate.colors[%s]" % k1))
    b = []
    for (k, a0, b0), (k_, a1, b1) in zip(BIOME_ROWS_011X, BIOME_ROWS):
        assert k == k_
        if (a0, b0) != (a1, b1):
            b.append(("biome." + k, "%d,%d" % (a0, b0), "%d,%d" % (a1, b1), "bands.biome[%s]" % k, "%d|%d" % (a0, b0), "%d|%d" % (a1, b1)))
    for (k, a0, b0, c0), (k_, a1, b1, c1) in zip(ENV_ROWS_011X, ENV_ROWS):
        assert k == k_ and c0 == c1
        if (a0, b0) != (a1, b1):
            b.append(("env." + k, "%d,%d,%d" % (a0, b0, c0), "%d,%d,%d" % (a1, b1, c1), "bands.env[%s]" % k, "%d|%d|%d" % (a0, b0, c0), "%d|%d|%d" % (a1, b1, c1)))
    for (k, a0, b0), (k_, a1, b1) in zip(ZONE_ROWS_011, ZONE_ROWS):
        if (a0, b0) != (a1, b1):
            b.append(("zone." + k, "%d,%d" % (a0, b0), "%d,%d" % (a1, b1), "bands.zone[%s]" % k, "%d|%d" % (a0, b0), "%d|%d" % (a1, b1)))
    return c, b


MG12_C, MG12_B = _m12_rows()
assert [r[0] for r in MG12_C] == ["bosses.zoneTops", "plate.colors.30", "plate.colors.45", "plate.colors.61"], MG12_C
assert len(set(r[0] for r in MG12_B)) == len(MG12_B) and not [r for r in MG12_B if r[0][r[0].index(".") + 1:].startswith(("Zone1", "Env_Zone1", "Env_Portal"))]
MG12_DC = [(TOPS_DOC_011, TOPS_DOC)]
# the 8 Level curve tables (Skyy "Stretch to Lv 100"): a table moves WHOLE, only while every point of it is exactly its 0.1.11 default
MG12_K = []
for _kd in CURVE_IDX:
    _pf = "curve.%s.%s." % _kd
    _om = dict((a, num(b)) for a, b in CURVES_011[_kd])
    _nm = dict((a, num(b)) for a, b in CURVES[_kd])
    _lg = []
    for _L in sorted(set(_om) | set(_nm)):
        if _om.get(_L) != _nm.get(_L):
            _lg.append("%s[%d];%s;%s" % (_pf[:-1], _L, _om.get(_L, "(none)"), _nm.get(_L, "(none)")))
    MG12_K.append((_pf, "|".join("%d=%s" % (a, num(b)) for a, b in CURVES_011[_kd]), "|".join("%d=%s" % (a, num(b)) for a, b in CURVES[_kd]),
                   "|".join("%s%d=%s" % (_pf, a, num(b)) for a, b in CURVES[_kd]), "|".join(_lg)))
assert len(MG12_K) == 8 and all(len(_r[4].split("|")) == 14 for _r in MG12_K)   # 5 points gone, 3 changed, 6 new, [len(_r[4].split("|")) for _r in MG12_K]
MG12_DB = [("# " + ZNAME_011[_z], "# " + ZNAME[_z]) for _z in (2, 3, 4)]
assert BANDS_TEXT.count("\n# " + ZNAME[2] + "\n") == 1 and "# " + ZNAME_011[2] not in BANDS_TEXT
print("0.1.12 bands: %d rows move (Zone 1 + portals unchanged):" % len(MG12_B))
for _r in MG12_B:
    print("   %-52s %s -> %s" % (_r[0], _r[1], _r[2]))
print("0.1.12 colours: " + ", ".join("%s -> %s" % (_r[0], _r[3]) for _r in MG12_C[1:]) + "; bosses.zoneTops %s -> %s" % (BOSS_TOPS_011, BOSS_TOPS_DEF))
for _d in ("public static final String[] C_KEY = %s;" % _jarr([t[0] for t in MG12_C]),
           "public static final String[] C_OLD = %s;" % _jarr([t[1] for t in MG12_C]),
           "public static final String[] C_NEW = %s;" % _jarr([t[2] for t in MG12_C]),
           "public static final String[] C_NKEY = %s;" % _jarr([t[3] for t in MG12_C]),
           "public static final String[] C_LOGK = %s;" % _jarr([t[4] for t in MG12_C]),
           "public static final String[] C_NLOGK = %s;" % _jarr([t[5] for t in MG12_C]),
           "public static final String[] C_DOLD = %s;" % _jarr([t[0] for t in MG12_DC]),
           "public static final String[] C_DNEW = %s;" % _jarr([t[1] for t in MG12_DC]),
           "public static final String[] B_KEY = %s;" % _jarr([t[0] for t in MG12_B]),
           "public static final String[] B_OLD = %s;" % _jarr([t[1] for t in MG12_B]),
           "public static final String[] B_NEW = %s;" % _jarr([t[2] for t in MG12_B]),
           "public static final String[] B_LOGK = %s;" % _jarr([t[3] for t in MG12_B]),
           "public static final String[] B_LOLD = %s;" % _jarr([t[4] for t in MG12_B]),
           "public static final String[] B_LNEW = %s;" % _jarr([t[5] for t in MG12_B]),
           "public static final String[] B_DOLD = %s;" % _jarr([t[0] for t in MG12_DB]),
           "public static final String[] B_DNEW = %s;" % _jarr([t[1] for t in MG12_DB]),
           "public static final String[] K_PFX = %s;" % _jarr([t[0] for t in MG12_K]),
           "public static final String[] K_OLD = %s;" % _jarr([t[1] for t in MG12_K]),
           "public static final String[] K_NEW = %s;" % _jarr([t[2] for t in MG12_K]),
           "public static final String[] K_LINES = %s;" % _jarr([t[3] for t in MG12_K]),
           "public static final String[] K_LOG = %s;" % _jarr([t[4] for t in MG12_K]),
           "public static final String MARK = %s;" % jstr(MG12_MARK),
           "public static final String MARK_ID = %s;" % jstr(MG12_MARK_ID),
           "public static final String WHO = %s;" % jstr(MG12_WHO),
           "public static final String WHAT = %s;" % jstr(MG12_WHAT)):
    F(m12, _d)
M(m12, r"""
public static int idx(String[] keys, String k) {
  if (k == null) return -1;
  for (int i = 0; i < keys.length; i++) if (keys[i].equals(k)) return i;
  return -1;
}""")
# the pure text step for ONE file (ISO-8859-1 chars in and out; the kit's own parser). mark != null: the file that carries the run-once
# marker (null result = the marker is already in a comment line). nkey[i] "" = a value change, else the new key of a rename (same value).
# Result { new text, Integer moved, String[] kept notes, String[] { logKey, old, new }*, String[] { fileKey, value or null }* }. Never throws.
M(m12, r"""
public static Object[] edit(String text, String[] key, String[] oldv, String[] newv, String[] nkey, String[] logk, String[] lold, String[] lnew, String[] nlogk, String[] dOld, String[] dNew, String mark) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  int n = key.length;
  String[] eff = new String[n];
  boolean[] multi = new boolean[n];
  boolean[] hasN = new boolean[n];
  int first = -1;
  int above = -1;
  int run = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (mark != null && s.indexOf(MARK_ID) >= 0) return null;
      if (s.trim().length() == 0) run = -1;
      else if (run < 0) run = k;
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    String fk = @PKG@.CfgFile.key(s);
    int m = idx(key, fk);
    if (m >= 0) {
      if (first < 0) { first = k; above = run >= 0 ? run : k; }
      eff[m] = @PKG@.CfgFile.value(l, k).trim();
      multi[m] = e > k;
    }
    int q = fk == null ? -1 : idx(nkey, fk);
    if (q >= 0 && nkey[q].length() > 0) hasN[q] = true;
    run = -1;
    k = e + 1;
  }
  boolean[] mig = new boolean[n];
  int moved = 0;
  java.util.ArrayList kept = new java.util.ArrayList();
  java.util.ArrayList logs = new java.util.ArrayList();
  java.util.ArrayList props = new java.util.ArrayList();
  for (int i = 0; i < n; i++) {
    if (eff[i] == null) continue;
    boolean ren = nkey[i].length() > 0;
    if (!multi[i] && eff[i].equals(oldv[i]) && !(ren && hasN[i])) {
      mig[i] = true;
      moved++;
      if (ren) {
        logs.add(logk[i]); logs.add(lold[i]); logs.add("(none)");
        logs.add(nlogk[i]); logs.add("(none)"); logs.add(lnew[i]);
        props.add(key[i]); props.add(null);
        props.add(nkey[i]); props.add(newv[i]);
      } else {
        logs.add(logk[i]); logs.add(lold[i]); logs.add(lnew[i]);
        props.add(key[i]); props.add(newv[i]);
      }
    } else if (ren || multi[i] || !eff[i].equals(newv[i])) {
      kept.add(key[i] + "=" + @PKG@.CfgRows.oneLine(eff[i]) + (ren && hasN[i] ? " kept (" + nkey[i] + " is already set)" : " kept (an admin's value)") + " - the 0.1.12 default is " + (ren ? nkey[i] : key[i]) + "=" + newv[i]);
    }
  }
  java.util.ArrayList out = new java.util.ArrayList();
  k = 0;
  while (k < l.size()) {
    String s2 = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s2)) {
      int d = -1;
      for (int j = 0; j < dOld.length; j++) if (dOld[j].equals(s2)) d = j;
      if (d >= 0) out.add(dNew[d] + (raw[k].endsWith("\r") ? "\r" : ""));
      else out.add(raw[k]);
      k++;
      continue;
    }
    int e2 = @PKG@.CfgFile.end(l, k);
    int m2 = idx(key, @PKG@.CfgFile.key(s2));
    if (m2 >= 0 && mig[m2] && e2 == k && @PKG@.CfgFile.value(l, k).trim().equals(oldv[m2])) {
      String cr1 = raw[k].endsWith("\r") ? "\r" : "";
      if (nkey[m2].length() > 0) {
        int p = s2.indexOf(key[m2]);
        out.add(s2.substring(0, p) + nkey[m2] + s2.substring(p + key[m2].length()) + cr1);
      } else out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + newv[m2] + cr1);
    } else {
      for (int q2 = k; q2 <= e2; q2++) out.add(raw[q2]);
    }
    k = e2 + 1;
  }
  if (mark != null) {
    String cr = text.indexOf("\r\n") >= 0 ? "\r" : "";
    int at = first >= 0 ? above : 0;
    String crA = at + 1 < raw.length ? (raw[at].endsWith("\r") ? "\r" : "") : cr;
    out.add(at, mark + crA);
  }
  StringBuilder sb = new StringBuilder(text.length() + 512);
  for (int i = 0; i < out.size(); i++) {
    if (i > 0) sb.append('\n');
    sb.append((String) out.get(i));
  }
  return new Object[] { sb.toString(), Integer.valueOf(moved), (String[]) kept.toArray(new String[0]), (String[]) logs.toArray(new String[0]), (String[]) props.toArray(new String[0]) };
}""")
# 0.1.12 Level curve stretch: a curve table (curve.<kind>.<difficulty>.<level> lines) whose entries are EXACTLY its 0.1.11 default points
# (one-line entries, the same levels and factor texts) is replaced WHOLE by the 0.1.12 points at the place of its first line (that line's CR);
# a table with any other point is kept (one note); a table already at the 0.1.12 points = nothing. Result shape = edit's.
M(m12, r"""
public static boolean sameMap(java.util.HashMap got, String spec) {
  String[] p = spec.split("\\|");
  if (got.size() != p.length) return false;
  for (int i = 0; i < p.length; i++) {
    int e = p[i].indexOf('=');
    Object v = got.get(p[i].substring(0, e));
    if (v == null || !v.equals(p[i].substring(e + 1))) return false;
  }
  return true;
}""")
M(m12, r"""
public static Object[] curveEdit(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  int n = K_PFX.length;
  java.util.HashMap[] got = new java.util.HashMap[n];
  boolean[] multi = new boolean[n];
  int[] first = new int[n];
  for (int t = 0; t < n; t++) { got[t] = new java.util.HashMap(); first[t] = -1; }
  int[] owner = new int[l.size()];
  int k = 0;
  while (k < l.size()) {
    owner[k] = -1;
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) { k++; continue; }
    int e = @PKG@.CfgFile.end(l, k);
    String fk = @PKG@.CfgFile.key(s);
    for (int t = 0; fk != null && t < n; t++) {
      if (fk.startsWith(K_PFX[t]) && fk.length() > K_PFX[t].length()) {
        got[t].put(fk.substring(K_PFX[t].length()).trim(), @PKG@.CfgFile.value(l, k).trim());
        if (e > k) multi[t] = true;
        if (first[t] < 0) first[t] = k;
        for (int q = k; q <= e; q++) owner[q] = t;
      }
    }
    for (int q = k + 1; q <= e && q < owner.length; q++) if (owner[q] < 0) owner[q] = -2;
    k = e + 1;
  }
  boolean[] mig = new boolean[n];
  int moved = 0;
  java.util.ArrayList kept = new java.util.ArrayList();
  java.util.ArrayList logs = new java.util.ArrayList();
  java.util.ArrayList props = new java.util.ArrayList();
  for (int t = 0; t < n; t++) {
    if (got[t].isEmpty()) continue;
    if (!multi[t] && sameMap(got[t], K_OLD[t])) {
      mig[t] = true;
      moved++;
      String[] lg = K_LOG[t].split("\\|");
      for (int i = 0; i < lg.length; i++) { String[] c = lg[i].split(";"); logs.add(c[0]); logs.add(c[1]); logs.add(c[2]); }
      String[] op = K_OLD[t].split("\\|");
      for (int i = 0; i < op.length; i++) { props.add(K_PFX[t] + op[i].substring(0, op[i].indexOf('='))); props.add(null); }
      String[] np = K_NEW[t].split("\\|");
      for (int i = 0; i < np.length; i++) { int e3 = np[i].indexOf('='); props.add(K_PFX[t] + np[i].substring(0, e3)); props.add(np[i].substring(e3 + 1)); }
    } else if (multi[t] || !sameMap(got[t], K_NEW[t])) {
      kept.add(K_PFX[t].substring(0, K_PFX[t].length() - 1) + " kept (an admin's points) - the 0.1.12 default stretches it to Lv 100: " + K_NEW[t]);
    }
  }
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    int t = i < owner.length ? owner[i] : -1;
    if (t >= 0 && mig[t]) {
      if (i == first[t]) {
        String cr1 = raw[i].endsWith("\r") ? "\r" : "";
        String[] nl = K_LINES[t].split("\\|");
        for (int j = 0; j < nl.length; j++) out.add(nl[j] + cr1);
      }
      continue;
    }
    out.add(raw[i]);
  }
  StringBuilder sb = new StringBuilder(text.length() + 512);
  for (int i = 0; i < out.size(); i++) {
    if (i > 0) sb.append('\n');
    sb.append((String) out.get(i));
  }
  return new Object[] { sb.toString(), Integer.valueOf(moved), (String[]) kept.toArray(new String[0]), (String[]) logs.toArray(new String[0]), (String[]) props.toArray(new String[0]) };
}""")
M(m12, r"""
public static String[] cat(String[] a, String[] b) {
  String[] r = new String[a.length + b.length];
  for (int i = 0; i < a.length; i++) r[i] = a[i];
  for (int i = 0; i < b.length; i++) r[a.length + i] = b[i];
  return r;
}""")
M(m12, r"""
public static Object[] cfgUpdate(String text) {
  Object[] a = edit(text, C_KEY, C_OLD, C_NEW, C_NKEY, C_LOGK, C_OLD, C_NEW, C_NLOGK, C_DOLD, C_DNEW, MARK);
  if (a == null) return null;
  Object[] b = curveEdit((String) a[0]);
  return new Object[] { b[0], Integer.valueOf(((Integer) a[1]).intValue() + ((Integer) b[1]).intValue()), cat((String[]) a[2], (String[]) b[2]),
    cat((String[]) a[3], (String[]) b[3]), cat((String[]) a[4], (String[]) b[4]), b[1] };
}""")
M(m12, r"""
public static Object[] bandsUpdate(String text) {
  String[] none = new String[B_KEY.length];
  for (int i = 0; i < none.length; i++) none[i] = "";
  return edit(text, B_KEY, B_OLD, B_NEW, none, B_LOGK, B_LOLD, B_LNEW, none, B_DOLD, B_DNEW, null);
}""")
# the update may change nothing but its planned keys: both texts as java.util.Properties, the old one with the planned changes applied
# ({ key, value } pairs; a null value = the key is gone) must equal the new one exactly
M(m12, r"""
public static boolean same(byte[] old, byte[] nb, String[] props) {
  try {
    java.util.Properties a = new java.util.Properties();
    java.util.Properties b = new java.util.Properties();
    a.load(new java.io.ByteArrayInputStream(old));
    b.load(new java.io.ByteArrayInputStream(nb));
    for (int i = 0; i + 1 < props.length; i += 2) {
      if (props[i + 1] == null) a.remove(props[i]);
      else a.setProperty(props[i], props[i + 1]);
    }
    return a.equals(b);
  } catch (Throwable t) { return false; }
}""")
M(m12, r"""
public static int fileIdx(String end) {
  for (int k = 0; k < @PKG@.CfgRows.FILES.length; k++) if (@PKG@.CfgRows.FILES[k].endsWith(end)) return k;
  return -1;
}""")
M(m12, r"""
public static String mgLog(String k, String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + WHO + "\t-\tupdate\t" + @PKG@.CfgRows.oneLine(k) + "\t" + o + "\t" + n + "\tok";
}""")
M(m12, r"""
public static void logAll(String[] rows) {
  for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(mgLog(rows[i], rows[i + 1], rows[i + 2]));
  if (rows.length > 0) @PKG@.CfgLog.flush();
}""")
# setup(): the INFO lines joined by \n ("" = nothing done: no config.properties - MobCfg.load writes the 0.1.12 defaults with the marker -,
# the marker already there, or a failure: WARN, both files untouched, retried at the next start)
M(m12, r"""
public static synchronized String run(java.nio.file.Path dir) {
  if (dir == null) return "";
  java.nio.file.Path f = dir.resolve("config.properties");
  java.nio.file.Path bf = dir.resolve("bands.properties");
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] oldC = java.nio.file.Files.readAllBytes(f);
    Object[] rc = cfgUpdate(new String(oldC, "ISO-8859-1"));
    if (rc == null) return "";
    byte[] oldB = null;
    if (java.nio.file.Files.exists(bf, new java.nio.file.LinkOption[0])) oldB = java.nio.file.Files.readAllBytes(bf);
    Object[] rb = null;
    if (oldB != null) rb = bandsUpdate(new String(oldB, "ISO-8859-1"));
    byte[] newC = ((String) rc[0]).getBytes("ISO-8859-1");
    byte[] newB = null;
    if (rb != null) newB = ((String) rb[0]).getBytes("ISO-8859-1");
    if (!same(oldC, newC, (String[]) rc[4]) || (rb != null && !same(oldB, newB, (String[]) rb[4]))) {
      @PKG@.MobLog.warn("config.properties / bands.properties NOT updated for the 0.1.12 level bands: the update would change more than its lines (the files are used as they are; the next start tries again)");
      return "";
    }
    boolean bch = rb != null && !java.util.Arrays.equals(oldB, newB);
    int fc = fileIdx("/config.properties");
    int fb = fileIdx("/bands.properties");
    if (fc < 0 || (bch && fb < 0)) return "";
    @PKG@.MobMig.mgKit(f.toAbsolutePath().getParent());
    if (bch) {
      @PKG@.CfgHist.snapshot(fb, oldB, @PKG@.CfgHist.stamp(), WHO, WHAT);
      if (!@PKG@.MobMig.mgSaved(fb, oldB)) {
        @PKG@.MobLog.warn("bands.properties NOT updated for the 0.1.12 level bands: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the files are used as they are; the next start tries again)");
        return "";
      }
    }
    @PKG@.CfgHist.snapshot(fc, oldC, @PKG@.CfgHist.stamp(), WHO, WHAT);
    if (!@PKG@.MobMig.mgSaved(fc, oldC)) {
      @PKG@.MobLog.warn("config.properties NOT updated for the 0.1.12 level bands: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the files are used as they are; the next start tries again)");
      return "";
    }
    if (bch) {
      @PKG@.CfgRows.atomicWrite(bf, newB);
      logAll((String[]) rb[3]);
    }
    @PKG@.CfgRows.atomicWrite(f, newC);
    logAll((String[]) rc[3]);
    int nb = 0;
    if (rb != null) nb = ((Integer) rb[1]).intValue();
    int nc = ((Integer) rc[1]).intValue();
    String msg = "config.properties + bands.properties updated for 0.1.12 (20 levels per zone: zone tops " + C_NEW[0] + "): " + nb + " band rows and " + nc
      + " config rows moved (" + ((Integer) rc[5]).intValue() + " of them Level curve tables, stretched to Lv 100; Zone 1 unchanged; mobs already spawned keep their level; the old files are in config-history; Server Setup -> Changes can undo each line)";
    @PKG@.MobLog.info(msg);
    StringBuilder all = new StringBuilder(msg);
    String[] k1 = (String[]) rc[2];
    String[] k2 = new String[0];
    if (rb != null) k2 = (String[]) rb[2];
    for (int i = 0; i < k1.length; i++) { @PKG@.MobLog.info(k1[i]); all.append('\n').append(k1[i]); }
    if (k2.length > 0) {
      StringBuilder kb = new StringBuilder(k2.length + " band rows kept (an admin's values; the 0.1.12 defaults are in Server Setup -> Mobs -> Level bands):");
      for (int i = 0; i < k2.length && i < 12; i++) kb.append(i == 0 ? " " : "; ").append(k2[i]);
      if (k2.length > 12) kb.append("; ... ").append(k2.length - 12).append(" more");
      @PKG@.MobLog.info(kb.toString());
      all.append('\n').append(kb.toString());
    }
    return all.toString();
  } catch (Throwable t) {
    @PKG@.MobLog.warn("could not update config.properties / bands.properties for the 0.1.12 level bands (the files are used as they are): " + t);
    return "";
  }
}""")

'''
rep('''# ---------------------------------------------------------------- MobCmds: the command bodies (world thread: AbstractPlayerCommand runs there)
''', MIG12 + '''# ---------------------------------------------------------------- MobCmds: the command bodies (world thread: AbstractPlayerCommand runs there)
''')
rep('''  if (mg11.length() > 0) mg = mg.length() > 0 ? mg + "\\n" + mg11 : mg11;
''', '''  if (mg11.length() > 0) mg = mg.length() > 0 ? mg + "\\n" + mg11 : mg11;
  String mg12 = @PKG@.MobMig12.run(dir);   // 0.1.12: 20 levels per zone - untouched zone tops / band rows / colour rows (once; History first; Undo in Server Setup)
  if (mg12.length() > 0) mg = mg.length() > 0 ? mg + "\\n" + mg12 : mg12;
''')

# ================================================================================================================ guards
assert s.count("registerSystem(") == SYS0, "no new system"
assert s.count("registerCommand(") == CMD0, "no new command"
assert s.count("bridge().put(") == PUT0, "no new bridge key"
_i = s.index
assert _i("import tier_tags as TT        # 0.1.12") < _i("def boss_tops(") < _i("assert all(boss_zone(_h, list(TT.ZONE_TOPS))") \
    < _i("BIOME_ROWS_011, ENV_ROWS_011, ZONE_ROWS_011 =") < _i("ZONE_TOPS = dict(") < _i("COLOR_ROWS_011 = list(COLOR_ROWS)") \
    < _i("BIOME_ROWS_011X = expand_biomes(") < _i("ENV_ROWS_011X = expand_envs(") < _i("ZNAME_011 = {") < _i("def _band_lines():") \
    < _i("    MG12_MARK,          # 0.1.12") < _i("MG12_C, MG12_B = _m12_rows()") < _i("F(m12, _d)") < _i("public void setup() {") < _i("@PKG@.MobMig12.run(dir)")
assert _i('MG12_MARK_ID = "') < _i("CFG_LINES = [") and _i("TOPS_DOC = (") < _i("CFG_LINES = [")
assert _i("MobMig11.run(dir)") < _i("MobMig12.run(dir)") < _i("@PKG@.MobCfg.load();\n  @PKG@.MobCfg.ON_HEALTH")
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.1.11 outside the recorded changes"
compile(s, DST, "exec")
with open(DST, "w", encoding="utf8", newline="") as f:
    f.write(s.replace(LF, NL) if NL != LF else s)
print("wrote %s (%d lines; 0.1.11 had %d; %d changes)" % (os.path.relpath(DST, ROOT), s.count(LF), OLD.count(LF), len(CHANGES)))
