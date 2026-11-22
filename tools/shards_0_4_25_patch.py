"""Derive SkyyShards/build_skyyshards_0.4.25.py from the GENERATED SkyyShards 0.4.24 (build_skyyshards_0.4.24.py = the tools/deploy_set.py SET
pin, made by tools/shards_0_4_24_patch.py - edit the patch, never the generated file). Every anchor is asserted once; at the end every change
is undone on a copy and compared with 0.4.24 (tools/soundpass_gen.Patch). Line endings kept.
Run:   python tools/shards_0_4_25_patch.py   then   python SkyyShards/build_skyyshards_0.4.25.py   (never --deploy)
Check: python SkyyShards/test_skyyshards_0.4.25.py

0.4.25 (2026-11-21) = SHARD CLICKER 3: FARMING (round farm1; Skyy 2026-11-14 docs/answered/world.md "FARMING + FORAGING SHARD ISLANDS BY ZONE": "lets make
  farming and foraging do something similar, so farming still does an island per crop, but the zone 2 stuff is in a different cluster of zone 2 islands with
  the zone 2 crops."; "(have zone locks for all the shards. so you can get shards for zone 2 stuff like thorium before unlocking it."; research/
  Shard-Clicker-Idea.md "Farming crop plots"; Skyy 2026-11-21 "build and deploy everything on your list"). Reuses the 0.4.23 Foraging clicker's page and
  machinery whole (view 5, the island scene, ShClk.hit / tick / extras / accXp, the .drops store, the six upgrade rows, the zone map, Server Setup rows) and
  the 0.4.24 Fortune bridge (skill:fn:fortune).
  SPEC (short; the survey first):
  - SURVEY. Vanilla (Assets.zip): no clicker page; the crops = the 15-crop ladder (tools/tier_tags.py CROP_LADDER, LAD[Farming], one island per crop since
    0.4.8). A ripe crop's world drop (Server/Drops/Crop/<C>/Drops_Plant_Crop_<C>_StageFinal_Harvest.json, read at build time) = the crop item (QuantityMin ..
    QuantityMax: Wheat 1-2, Corn / Potato / Onion 2-4, Tomato / Chilli / Cotton / Rice 1-3, the rest 1) + 2-9 Life Essence + its ETERNAL seed bag at Weight
    0.5 (= 0.5 %); no plain seeds (those come from the planted block). The Mushroom (spores, T15) has no final-stage list: 1 cap, no seeds. Mods: the
    0.4.23 survey (pie-clicker, learn only); nothing new packed. Approved art: none for Farming in research/ui-theme-art (grep 'farm') - the build draws its own.
  - 1. THE FARM = view 5 of the Farming Shard's page (its footer's "Shard clicker", as Foraging / Mining): ONE ISLAND PER CROP (the island you own of that
    crop), the map groups them in a cluster per ZONE (3 crops a zone: Zone 1 Wheat / Lettuce / Carrot ... Zone 5 Potato / Onion / Mushroom). The island's
    plots stand on its tree spots (Plot count = Tree Amount decides how many). Click a plot with the hoe / sickle in your hand - or bare hands (a Crude
    hoe, Skyy 2026-10-14 "Hands count as Crude"): THE WORLD'S FARMING GATE (SkyyGear gear:fn:farmTier with the crop block + the held item: normal / one tier
    up = click.farm.oneTierUp (40 %) damage a click, NO Fortune, click.farm.oneTierUpXp (50 %) XP / two or more up = refused, no hit counted); no SkyyGear =
    not gated. A plot takes click.farm.hp (8) damage, then is harvested: click.farm.plants (3) + Plot size x click.farm.sizePlants (1) PLANTS, each = the
    crop's vanilla quantity (a random whole number in its QuantityMin..Max) x (1 + Fortune extras - skill:fn:fortune "Farming" for the crop block, else
    the skill:bonus dd.farming sum) + click.farm.eternalPermille (5 = vanilla's 0.5 %) chance of 1 Eternal seed bag (no Fortune on seeds). XP =
    click.xpPercent (25) % of click.farm.xp (the world's Farming XP of one harvested plant of that crop, SkyySkills P3: 40 .. 1,850) per plant whose crop
    fit. click.maxPerSec (8) counted clicks a second (the shared cap). A plot regrows in click.farm.regrowSec (10) - Irrigation x click.farm.irrSec (1),
    at least click.farm.minRegrowSec (3) (memory only).
  - 2. THE DROPS go into the island's .drops (0.4.23's store, saved at once, counted against its storage; Collect / a grid cell / Collect all pay them first
    with the collection credit; no XP at Collect - the click paid it). What does not fit: the Eternal seeds first, then the crop.
  - 3. THE SIX UPGRADES = the Map tab's / 0.4.23's purchases (coins + the island's Enchanted crop): Plot size = <kind>.i<n>.nsize (0.4.23's Tree size purchase
    + its cost rows), Plot count = Tree Amount, Spirit totems = the Totems tab, Irrigation = Irrigation (regrow speed + its output bonus), Island size = Grow,
    Decorations. A button carries the level the page showed: a double click buys once; a stale island (profile switch / another island in that slot) is
    refused ("the page is up to date now").
  - 4. ZONE LOCKS FOR FARMING (Skyy "have zone locks for all the shards"): ShIsl.zoneNeed for Farming = click.farm.zoneLevel (0 / 20 / 40 / 60 / 80 Farming,
    until a real zone signal exists); buyIsland0 asks it (Map tab + the farm map); an island you own stays yours and clickable (nothing lost).
  NUMBERS (new, Server Setup -> Shards -> Shard clicker; all editable): click.farm.enabled true, click.farm.hp 8, click.farm.plants 3, click.farm.sizePlants 1,
    click.farm.sizeMax 10, click.farm.eternalPermille 5, click.farm.regrowSec 10, click.farm.irrSec 1, click.farm.minRegrowSec 3, click.farm.oneTierUp 40,
    click.farm.oneTierUpXp 50, click.farm.xp 40,80,135,185,280,380,460,605,750,860,1050,1250,1400,1600,1850, click.farm.zoneLevel 0,20,40,60,80. Copied (not
    new): the crop quantities + the 0.5 % Eternal seed chance (vanilla), the Tree size coin / Enchanted table for Plot size, the Map tab costs for the rest.
  ART: the build draws its own (FART_SRC, appended to CLK_ART_SRC): 15 crop plots (tilled soil + the crop's plants: wheat stalks, lettuce heads, carrot /
    turnip tops, corn, cauliflower curds, pumpkins, aubergines, tomatoes on stakes, chillies, cotton puffs, a rice paddy, potato bushes, onions, mushrooms),
    a harvested plot (sprouts), 15 map farm islands, 3 upgrade icons -> Common/UI/Custom/SkyyShards/Map/ClkF*@2x.png + ClkUpF*@2x.png. The island, spirit
    totems, the weather (rain) totem = Irrigation and the decorations are 0.4.23's pictures.
  CONFIG KIT: emit(..., HOLDERS=2) - the 13 new rows took CfgRows.<clinit> over the JVM's 64 KB method cap; the per-row arrays now sit in
    CfgRows1 / CfgRows2 (same keys, defaults, files, order and bridge contract; tools/skyycfg.py ROW HOLDERS).
  SAVED DATA: farming.i<n>.nsize (Plot size, missing = 0) and farming.i<n>.drops (harvested, not collected yet). Old files load unchanged; no migration
    (nothing moved or rewritten).
  ROLLBACK 0.4.25 -> 0.4.24 alone: no migration. 0.4.24 ignores farming nsize (kept in the file); its Collect is generic (ShCore.collectHeld runs for
    every non-Combat shard and gridOf merges every shard's .drops), so harvested farming crops still show and pay out on 0.4.24 - Collect all on the
    Farming Shard first is only a tidy-up step. Farming zone locks disappear (islands buyable at any level again).
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

HERE = os.path.join(ROOT, "SkyyShards")
P = G.Patch(os.path.join(HERE, "build_skyyshards_0.4.24.py"), os.path.join(HERE, "build_skyyshards_0.4.25.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.4.24"\n') and P.has("GENERATED by tools/shards_0_4_24_patch.py") and P.has("fillQuarry") and not P.has("fillFarm"), "not the generated SkyyShards 0.4.24"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.25 (2026-11-21)"):].rstrip() + "\n"


def sub1(txt, old, new, n=1):
    """replace old in txt; it must occur exactly n times"""
    c = txt.count(old)
    assert c == n, "fillFarm anchor count %d (want %d): %s" % (c, n, old[:160])
    return txt.replace(old, new)


# ---------------------------------------------------------------------------------------------------- 0. header + version
P.rep('''"""SkyyShards 0.4.24 - build script (javassist via jpype). GENERATED by tools/shards_0_4_24_patch.py from build_skyyshards_0.4.23.py
(generated by tools/shards_0_4_23_patch.py from 0.4.22, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.24" /''', '''"""SkyyShards 0.4.25 - build script (javassist via jpype). GENERATED by tools/shards_0_4_25_patch.py from build_skyyshards_0.4.24.py
(generated by tools/shards_0_4_24_patch.py from 0.4.23, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.25" / "0.4.24" /''')
P.rep('''Run:   python SkyyShards/build_skyyshards_0.4.24.py   -> SkyyShards/SkyyShards-0.4.24.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.24.py
''', '''Run:   python SkyyShards/build_skyyshards_0.4.25.py   -> SkyyShards/SkyyShards-0.4.25.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.25.py
''' + NOTE + '''
''')
P.rep('VERSION = "0.4.24"\n', 'VERSION = "0.4.25"\n')

# ---------------------------------------------------------------------------------------------------- 1. ShCfg: the farm's settings
P.rep(r'''          "public static volatile int[] MQ_GW = new int[] { %s };" % ", ".join(str(_x) for _x in MQ_GW)):
    F(cfg, f)
''', r'''          "public static volatile int[] MQ_GW = new int[] { %s };" % ", ".join(str(_x) for _x in MQ_GW)):
    F(cfg, f)
# 0.4.25 THE FARMING CLICKER (tools/shards_0_4_25_patch.py): its settings (Server Setup -> Shards -> Shard clicker, rows click.farm.*)
FQ_K = KINDS.index("Farming")
FQ_ZLV = [0, 20, 40, 60, 80]          # Zone 1..5 farm islands are bought from this Farming level
FQ_XPD = list(P3_CROP_XP)             # the world's Farming XP of one harvested plant, crop T1..T15 (SkyySkills P3 3.3, copied)
assert FQ_K == FARM_K == 2 and len(FQ_ZLV) == 5 and len(FQ_XPD) == 15
for f in ("public static volatile boolean FQ_ON = true;", "public static volatile int FQ_HP = 8;", "public static volatile int FQ_PLANTS = 3;",
          "public static volatile int FQ_NS_PER = 1;", "public static volatile int FQ_NS_MAX = 10;", "public static volatile int FQ_ETERNAL = 5;",
          "public static volatile int FQ_REGROW = 10;", "public static volatile int FQ_IRR = 1;", "public static volatile int FQ_RMIN = 3;",
          "public static volatile int FQ_UP1 = 40;", "public static volatile int FQ_UPXP = 50;",
          "public static final int[] DEF_FQ_XP = new int[] { %s };" % ", ".join(str(_x) for _x in FQ_XPD),
          "public static volatile int[] FQ_XP = new int[] { %s };" % ", ".join(str(_x) for _x in FQ_XPD),
          "public static final int[] DEF_FQ_ZLV = new int[] { %s };" % ", ".join(str(_x) for _x in FQ_ZLV),
          "public static volatile int[] FQ_ZLV = new int[] { %s };" % ", ".join(str(_x) for _x in FQ_ZLV)):
    F(cfg, f)
''')
P.rep(r'''         ("click.mine.zoneLevel", "Quarry zone opens at Mining level", "clicker", "text", ",".join(str(_x) for _x in MQ_ZLV), "", "60", "", "", "live",
          "5 numbers, Zone 1..5: Mining islands of a zone are bought from this Mining level.", "reload@config.properties:click.mine.zoneLevel")]
''', r'''         ("click.mine.zoneLevel", "Quarry zone opens at Mining level", "clicker", "text", ",".join(str(_x) for _x in MQ_ZLV), "", "60", "", "", "live",
          "5 numbers, Zone 1..5: Mining islands of a zone are bought from this Mining level.", "reload@config.properties:click.mine.zoneLevel")]
# 0.4.25: the Farming clicker's rows
ROWS += [("click.farm.enabled", "Farming clicker", "clicker", "bool", "true", "", "", "", "", "live",
          "Off: the Farming Shard menu shows no clicker and clicks do nothing. Nothing is deleted.", "reload@config.properties:click.farm.enabled"),
         ("click.farm.hp", "Farm: clicks to harvest a plot", "clicker", "int", "8", "1", "1000", "", "", "live",
          "Damage a crop plot takes before it is harvested (1 click = 1 with a hoe of the crop's tier).", "reload@config.properties:click.farm.hp"),
         ("click.farm.plants", "Farm: plants a harvest", "clicker", "int", "3", "1", "1000", "", "", "live",
          "Plants a harvested plot gives before Plot size (each: the crop's vanilla drop).", "reload@config.properties:click.farm.plants"),
         ("click.farm.sizePlants", "Farm: more plants per Plot size", "clicker", "int", "1", "0", "100", "", "", "live",
          "Each Plot size level adds this many plants to a harvest.", "reload@config.properties:click.farm.sizePlants"),
         ("click.farm.sizeMax", "Farm: Plot size levels", "clicker", "int", "10", "0", "10", "", "", "live",
          "The highest Plot size level (costs: the Tree size rows).", "reload@config.properties:click.farm.sizeMax"),
         ("click.farm.eternalPermille", "Farm: Eternal seed chance (1/1000)", "clicker", "int", "5", "0", "1000", "", "", "live",
          "Chance a harvested plant drops 1 Eternal seed bag, in 1/1000 (vanilla: 0.5 % = 5).", "reload@config.properties:click.farm.eternalPermille"),
         ("click.farm.regrowSec", "Farm: a plot regrows in", "clicker", "int", "10", "1", "3600", "", "s", "live",
          "Seconds before a harvested plot can be harvested again (before Irrigation).", "reload@config.properties:click.farm.regrowSec"),
         ("click.farm.irrSec", "Farm: Irrigation faster regrow", "clicker", "int", "1", "0", "600", "", "s", "live",
          "Seconds less regrow per Irrigation level.", "reload@config.properties:click.farm.irrSec"),
         ("click.farm.minRegrowSec", "Farm: shortest regrow", "clicker", "int", "3", "0", "3600", "", "s", "live",
          "A plot never regrows faster than this.", "reload@config.properties:click.farm.minRegrowSec"),
         ("click.farm.oneTierUp", "Farm: crop 1 tier up: damage", "clicker", "int", "40", "1", "100", "", "%", "live",
          "A crop one tier above your hoe / sickle: damage a click (40 % = 2.5x the clicks), no Fortune.", "reload@config.properties:click.farm.oneTierUp"),
         ("click.farm.oneTierUpXp", "Farm: crop 1 tier up: XP", "clicker", "int", "50", "0", "100", "", "%", "live",
          "XP share for a crop one tier above your hoe / sickle (the world gives half).", "reload@config.properties:click.farm.oneTierUpXp"),
         ("click.farm.xp", "Farm: world XP a plant, by crop", "clicker", "text", ",".join(str(_x) for _x in FQ_XPD), "", "200", "", "", "live",
          "15 numbers, crop T1..T15: Farming XP of one plant in the world (clicks pay click.xpPercent).", "reload@config.properties:click.farm.xp"),
         ("click.farm.zoneLevel", "Farm zone opens at Farming level", "clicker", "text", ",".join(str(_x) for _x in FQ_ZLV), "", "60", "", "", "live",
          "5 numbers, Zone 1..5: Farming islands of a zone are bought from this Farming level.", "reload@config.properties:click.farm.zoneLevel")]
''')
P.rep(r'''          "  MQ_ZLV = intsOf(p.getProperty(\"click.mine.zoneLevel\"), DEF_MQ_ZLV, 0, 1000, \"click.mine.zoneLevel\");"]
''', r'''          "  MQ_ZLV = intsOf(p.getProperty(\"click.mine.zoneLevel\"), DEF_MQ_ZLV, 0, 1000, \"click.mine.zoneLevel\");"]
_load += ["  FQ_ON = bool(p.getProperty(\"click.farm.enabled\"), true);",   # 0.4.25 the Farming clicker
          "  FQ_HP = intOf(p.getProperty(\"click.farm.hp\"), 8, 1, 1000);",
          "  FQ_PLANTS = intOf(p.getProperty(\"click.farm.plants\"), 3, 1, 1000);",
          "  FQ_NS_PER = intOf(p.getProperty(\"click.farm.sizePlants\"), 1, 0, 100);",
          "  FQ_NS_MAX = intOf(p.getProperty(\"click.farm.sizeMax\"), 10, 0, 10);",
          "  FQ_ETERNAL = intOf(p.getProperty(\"click.farm.eternalPermille\"), 5, 0, 1000);",
          "  FQ_REGROW = intOf(p.getProperty(\"click.farm.regrowSec\"), 10, 1, 3600);",
          "  FQ_IRR = intOf(p.getProperty(\"click.farm.irrSec\"), 1, 0, 600);",
          "  FQ_RMIN = intOf(p.getProperty(\"click.farm.minRegrowSec\"), 3, 0, 3600);",
          "  FQ_UP1 = intOf(p.getProperty(\"click.farm.oneTierUp\"), 40, 1, 100);",
          "  FQ_UPXP = intOf(p.getProperty(\"click.farm.oneTierUpXp\"), 50, 0, 100);",
          "  FQ_XP = intsOf(p.getProperty(\"click.farm.xp\"), DEF_FQ_XP, 0, 1000000, \"click.farm.xp\");",
          "  FQ_ZLV = intsOf(p.getProperty(\"click.farm.zoneLevel\"), DEF_FQ_ZLV, 0, 1000, \"click.farm.zoneLevel\");"]
''')

# the 13 new rows took CfgRows.<clinit> over the JVM's 64 KB method cap (67,130 bytes; found by the harness's -Xverify load): the kit's ROW HOLDERS
# (tools/skyycfg.py HOLDERS=2, SkyyArmory 0.1.33 first) - the same arrays, contents and order in CfgRows1 / CfgRows2, joined by CfgRows
P.rep(r'''               RELOAD="ShCfg.reloadKit", KEEP=10, DEFAULTS={"config.properties": CONFIG_TEXT,''',
      r'''               RELOAD="ShCfg.reloadKit", KEEP=10, HOLDERS=2, DEFAULTS={"config.properties": CONFIG_TEXT,''')

# ---------------------------------------------------------------------------------------------------- 2. ShIsl: Farming zone locks (by Farming level)
P.rep(r'''public static int zoneNeed(int kd, int t) {
  if (kd != @CKFK@ && kd != @MQK@) return 0;
  int[] a = kd == @MQK@ ? @PKG@.ShCfg.MQ_ZLV : @PKG@.ShCfg.CK_ZLV;   // 0.4.24: the Mining quarry zones by Mining level (Skyy "zone locks for all the shards")
  int z = zoneOf(t);
  return a == null || z - 1 >= a.length ? 0 : a[z - 1];
}""".replace("@CKFK@", str(CK_FK)).replace("@MQK@", str(MQ_K)))''', r'''public static int zoneNeed(int kd, int t) {
  if (kd != @CKFK@ && kd != @MQK@ && kd != @FQK@) return 0;
  int[] a = kd == @MQK@ ? @PKG@.ShCfg.MQ_ZLV : (kd == @FQK@ ? @PKG@.ShCfg.FQ_ZLV : @PKG@.ShCfg.CK_ZLV);   // 0.4.24 Mining / 0.4.25 Farming zones by their skill level
  int z = zoneOf(t);
  return a == null || z - 1 >= a.length ? 0 : a[z - 1];
}""".replace("@CKFK@", str(CK_FK)).replace("@MQK@", str(MQ_K)).replace("@FQK@", str(FQ_K)))''')

# ---------------------------------------------------------------------------------------------------- 3. ShClk: THE FARM (the world gate, the harvest)
FARM_CLK = r'''# ---- 0.4.25 THE FARMING CLICKER (tools/shards_0_4_25_patch.py): ONE ISLAND PER CROP. A plot = the 0.4.23 tree (damage, regrow, the click cap) with the
# hoe / sickle in hand (bare hands = a Crude hoe) under the WORLD's farming gate (SkyyGear gear:fn:farmTier); a harvest = plants x the crop's vanilla quantity
# x (1 + Fortune extras) + the vanilla Eternal seed chance, into the island's .drops (saved at once); XP = click.xpPercent of the world's XP a plant.
FQ_LAD = LAD[FQ_K]
assert len(FQ_LAD) == 15 and [_t["tier"] for _t in FQ_LAD] == list(range(1, 16)) and [_t["name"] for _t in FQ_LAD] == list(_TT48.CROP_LADDER)
FQ_GROW, FQ_QMIN, FQ_QMAX, FQ_ESEED, FQ_EWT = [], [], [], [], []
for _t in FQ_LAD:
    assert _t["grow"] in ITEMS and _t["prod"] in ITEMS, (_t["grow"], _t["prod"])
    _dn = "Server/Drops/Crop/%s/Drops_Plant_Crop_%s_StageFinal_Harvest.json" % (_t["name"], _t["name"])
    _q, _e = None, None
    if _dn in AZN:   # the ripe crop's vanilla drop: the crop item (Quantity min..max) + its Eternal seed bag at a Weight (0.5 = 0.5 %)
        _stk = [json.loads(AZ.read(_dn).decode("utf-8-sig"))]
        while _stk:
            _x = _stk.pop()
            if isinstance(_x, dict):
                _it = _x.get("Item")
                if isinstance(_it, dict) and _it.get("ItemId") == _t["prod"]:
                    _q = (int(_it.get("QuantityMin", 1)), int(_it.get("QuantityMax", _it.get("QuantityMin", 1))))
                if isinstance(_it, dict) and _it.get("ItemId") == _t["eseed"]:
                    _e = float(_x.get("Weight", 100.0))
                _stk.extend(_x.values())
            elif isinstance(_x, list):
                _stk.extend(_x)
        assert _q is not None and 1 <= _q[0] <= _q[1] <= 10 and _e is not None, (_t["name"], _q, _e)
    else:   # the Mushroom: no final-stage list in vanilla (the block is the cap) - 1 cap a plant, no seeds
        assert _t["name"] == "Mushroom", _dn
        _q, _e = (1, 1), None
    FQ_GROW.append(_t["grow"]); FQ_QMIN.append(_q[0]); FQ_QMAX.append(_q[1])
    FQ_ESEED.append(_t["eseed"] if _e is not None else ""); FQ_EWT.append(_e)
assert set(_w for _w in FQ_EWT if _w is not None) == {0.5}, "the vanilla Eternal seed weight changed: %s - check click.farm.eternalPermille (5)" % FQ_EWT
assert (FQ_QMIN[0], FQ_QMAX[0]) == (1, 2) and FQ_ESEED[0] == "Plant_Seeds_Wheat_Eternal" and FQ_ESEED[14] == "", (FQ_QMIN, FQ_QMAX, FQ_ESEED)
CK_HOES = [(_i, int(_TT48.tier(_i))) for _i in sorted(_TT48.ROWS) if _i.startswith(("Tool_Hoe_", "Tool_Sickle_")) and _TT48.tier(_i)]
assert ("Tool_Hoe_Crude", 1) in CK_HOES and ("Tool_Sickle_Harvester_Thorium", 4) in CK_HOES, CK_HOES[:6]
for f in ("public static final int CRK = %d;" % FQ_K,
          "public static final String[] HOE_ID = new String[] { %s };" % ", ".join(jlit(_a) for _a, _t in CK_HOES),
          "public static final int[] HOE_T = new int[] { %s };" % ", ".join(str(_t) for _a, _t in CK_HOES),
          "public static final String[] F_GROW = new String[] { %s };" % ", ".join(jlit(_x) for _x in FQ_GROW),
          "public static final int[] F_QMIN = new int[] { %s };" % ", ".join(str(_x) for _x in FQ_QMIN),
          "public static final int[] F_QMAX = new int[] { %s };" % ", ".join(str(_x) for _x in FQ_QMAX),
          "public static final String[] F_ESEED = new String[] { %s };" % ", ".join(jlit(_x) for _x in FQ_ESEED),
          "public static final java.util.concurrent.atomic.AtomicLong HARVESTED = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong GATED = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong GATE_BR = new java.util.concurrent.atomic.AtomicLong();"):
    F(ckc, f)
# the hoe / sickle's tier for the page (tools/tier_tags.py: hoes, sickles, Harvesters); another id with "Hoe" / "Sickle" = its best metal word (else T1);
# 0 = no farming tool (bare hands / anything else = a Crude hoe in the world's gate)
M(ckc, r"""
public static int hoeTier(String id) {
  if (id == null || id.length() == 0) return 0;
  for (int i = 0; i < HOE_ID.length; i++) if (HOE_ID[i].equals(id)) return HOE_T[i];
  if (id.indexOf("Hoe") < 0 && id.indexOf("Sickle") < 0) return 0;
  String[] w = id.split("_");
  int best = 0;
  for (int i = 0; i < w.length; i++) for (int j = 0; j < METAL_W.length; j++) if (METAL_W[j].equals(w[i]) && METAL_T[j] > best) best = METAL_T[j];
  return best > 0 ? best : 1;
}""")
# THE WORLD'S FARMING GATE: SkyyGear gear:fn:farmTier Object[]{ UUID, crop block id, held item id (null = bare hands) } -> Integer -1 not gated, 0 normal,
# 1 one tier up (slow, no Fortune, half XP), 2 refused; no answer (no SkyyGear / an error) = -1 (not gated)
M(ckc, r"""
public static int farmGate(java.util.UUID u, String block, String hand) {
  String h = hand;
  if (h != null && h.length() == 0) h = null;
  try {
    java.util.function.Function f = @PKG@.ShCfg.fn("gear:fn:farmTier");
    if (f != null) {
      Object r = f.apply(new Object[] { u, block, h });
      if (r instanceof Integer) {
        GATE_BR.incrementAndGet();
        int v = ((Integer) r).intValue();
        return v < -1 ? -1 : (v > 2 ? 2 : v);
      }
    }
  } catch (Throwable x) { }
  return -1;
}""")
M(ckc, "public static long plantsAt(int ns) { return (long) @PKG@.ShCfg.FQ_PLANTS + (long) ns * (long) @PKG@.ShCfg.FQ_NS_PER; }")
M(ckc, r"""
public static long farmRegrowMs(int irr) {
  long s = (long) @PKG@.ShCfg.FQ_REGROW - (long) @PKG@.ShCfg.FQ_IRR * (long) (irr < 0 ? 0 : irr);
  if (s < (long) @PKG@.ShCfg.FQ_RMIN) s = (long) @PKG@.ShCfg.FQ_RMIN;
  return s < 0L ? 0L : s * 1000L;
}""")
M(ckc, r"""
public static double eternalP() {
  double c = (double) @PKG@.ShCfg.FQ_ETERNAL / 1000.0;
  return c < 0.0 ? 0.0 : (c > 1.0 ? 1.0 : c);
}""")
M(ckc, r"""
public static int farmXp(int ci) {
  int[] a = @PKG@.ShCfg.FQ_XP;
  if (a == null || a.length == 0) return 0;
  int i = ci < 0 ? 0 : (ci >= a.length ? a.length - 1 : ci);
  return a[i];
}""")
M(ckc, r"""
public static String toolWord(String hand) {
  if (hand == null || hand.length() == 0) return "Bare hands (a Crude hoe)";
  return "Your " + @PKG@.ShTotem.pretty(hand);
}""")
# THE HARVEST CLICK (world thread; the bridges outside the store lock): Object[]{ status, pop text over the plot }. The rolls (exact order, replayed by
# the harness): per plant [the quantity roll when min < max], the Fortune roll, [the Eternal seed roll when the crop has one]
M(ckc, r"""
public static Object[] harvest(java.util.UUID u, String k, int kd, int slot, int spot, String hand) {
  if (!@PKG@.ShCfg.FQ_ON) return res("-The Farming clicker is switched off on this server.", "");
  long now = @PKG@.ShCore.now();
  if (!tick(u, now)) { CAPPED.incrementAndGet(); return res("", ""); }
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return res("-This shard's file could not be read.", "");
  String no = @PKG@.ShCore.gate(u, k, kd, p);
  if (no != null) return res(no, "");
  int t; int n; int irr; long use; long lim;
  @PKG@.ShStore.LOCK.lock(); try {
    if (slot < 0 || slot >= @PKG@.ShMath.SLOTS || !@PKG@.ShMath.hasIsland(kd, p, slot)) return res("-That island is not yours yet.", "");
    t = @PKG@.ShIsl.ty(kd, p, slot);
    n = @PKG@.ShIsl.treeN(@PKG@.ShMath.size(kd, p, slot), @PKG@.ShIsl.sub(p, kd, slot, 0));
    irr = @PKG@.ShIsl.sub(p, kd, slot, 2);
    @PKG@.ShMath.settle(kd, p, slot, now);
    use = @PKG@.ShMath.usedOf(kd, p, slot);
    lim = @PKG@.ShMath.limOf(kd, p, slot);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (spot < 0 || spot >= n || spot >= NSPOT) return res("=The page is up to date now.", "");
  if (use >= lim) return res("-This island's storage is full - Collect first.", "");
  int ci = t - @PKG@.ShIsl.LAD0[kd];
  if (ci < 0 || ci >= F_GROW.length) return res("=The page is up to date now.", "");
  String block = F_GROW[ci];
  int g = farmGate(u, block, hand);
  if (g >= 2) {
    GATED.incrementAndGet();
    return res("-" + toolWord(hand) + " cannot harvest " + @PKG@.ShIsl.tname(t) + " - like in the world, a crop two tiers above your hoe or sickle cannot be harvested.", "");
  }
  double f = g == 1 ? 0.0 : fortuneOf(u, "Farming", block, "dd.farming", "only.farming");
  String key = k + "|" + kd + "|" + slot;   // the farm's own plot memory (a Foraging / Mining island in the same slot number keeps its own)
  double hpMax = (double) @PKG@.ShCfg.FQ_HP;
  double dm = g == 1 ? (double) @PKG@.ShCfg.FQ_UP1 / 100.0 : 1.0;
  double left = hit(key, spot, dm, hpMax, now, farmRegrowMs(irr));
  CHOPS.incrementAndGet();
  if (left < 0.0) { long ms = (long) (-left - 1.0); return res("=That plot is growing back - " + ((ms + 999L) / 1000L) + " s.", ""); }
  if (left > 0.0) return res("", @PKG@.ShCfg.dec(hpMax - left) + " / " + @PKG@.ShCfg.dec(hpMax));
  long gC; long gS; long baseC; long plants; long total; String cropId; String seedId;
  @PKG@.ShStore.LOCK.lock(); try {
    if (!@PKG@.ShMath.hasIsland(kd, p, slot) || @PKG@.ShIsl.ty(kd, p, slot) != t) { unfell(key, spot, hpMax); return res("-That island changed meanwhile - the page is up to date now.", ""); }
    plants = plantsAt(nsize(p, kd, slot));
    cropId = @PKG@.ShIsl.PROD[t];
    seedId = F_ESEED[ci];
    long q0 = (long) F_QMIN[ci];
    long q1 = (long) F_QMAX[ci];
    double pe = seedId.length() > 0 ? eternalP() : 0.0;
    long crop = 0L; long seed = 0L;
    baseC = 0L;
    for (long b = 0L; b < plants && b < 100000L; b++) {
      long q = q0;
      if (q1 > q0) { q = q0 + (long) Math.floor(rnd() * (double) (q1 - q0 + 1L)); if (q > q1) q = q1; }
      baseC = baseC + q;
      crop = crop + q * (1L + (long) extras(f, rnd()));
      if (pe > 0.0 && rnd() < pe) seed = seed + 1L;
    }
    total = crop + seed;
    @PKG@.ShMath.settle(kd, p, slot, now);
    long room = @PKG@.ShMath.limOf(kd, p, slot) - @PKG@.ShMath.usedOf(kd, p, slot);
    if (room <= 0L) { unfell(key, spot, hpMax); return res("-This island's storage is full - Collect first.", ""); }
    gS = seed < room ? seed : room; room = room - gS;   // what fits: the Eternal seeds first, then the crop
    gC = crop < room ? crop : room;
    String dk = @PKG@.ShMath.ik(kd, slot, "drops");
    String old = p.getProperty(dk);
    java.util.LinkedHashMap m = @PKG@.ShMath.held(kd, p, slot);
    addTo(m, seedId, gS);
    addTo(m, cropId, gC);
    @PKG@.ShMath.heldSet(kd, p, slot, m);
    String e = @PKG@.ShStore.save(k, p);
    if (e != null) {
      if (old == null) p.remove(dk); else p.setProperty(dk, old);
      unfell(key, spot, hpMax);
      @PKG@.ShCfg.warnOnce("fsave", "a harvested plot's crops could not be saved (nothing added, the plot stands again; logged once): " + e);
      return res("-The shard file could not be saved - nothing was added.", "");
    }
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  FELLS.incrementAndGet();
  HARVESTED.addAndGet(gC + gS);
  long paidP = baseC <= 0L ? 0L : (gC >= baseC ? plants : plants * gC / baseC);
  String skill = @PKG@.ShKind.SKILL[kd];
  double xpe = (double) paidP * (double) farmXp(ci) * (double) @PKG@.ShCfg.CK_XP_PCT / 100.0 * (g == 1 ? (double) @PKG@.ShCfg.FQ_UPXP / 100.0 : 1.0);
  long xp = accXp(String.valueOf(u) + "|" + @PKG@.ShCfg.pkey(u) + "|" + kd, xpe);   // Farming's own XP fractions
  String xt = "";
  if (xp > 0L) { long xl = @PKG@.ShCore.owedXp(u, skill, xp); xt = xl > 0L ? " (" + @PKG@.ShCfg.num(xl) + " " + skill + " XP waits)" : " +" + @PKG@.ShCfg.num(xp) + " " + skill + " XP"; }
  StringBuilder sb = new StringBuilder();
  part(sb, gC, cropId);
  part(sb, gS, seedId);
  String up = g == 1 ? " (a tier above your tool: no Fortune, " + @PKG@.ShCfg.FQ_UPXP + " % XP)" : "";
  String fit = gC + gS < total ? " - the island's storage is full (" + @PKG@.ShCfg.num(total - gC - gS) + " did not fit)" : "";
  String r = "+Harvested a " + @PKG@.ShIsl.tname(t) + " plot: " + sb.toString() + xt + up + fit + ".";
  String pop = gC > 0L ? "+" + @PKG@.ShCfg.num(gC) + " " + qName(cropId) : "+" + @PKG@.ShCfg.num(gS) + " " + qName(seedId);
  @PKG@.ShSnd.ok(u, r, 0);
  return res(r, pop);
}""")
'''
P.rep(r'''# THE CLICK: Object[]{ status ("+..." / "-..." / "=..." / "" = nothing to say), pop text over the tree }. World thread; the bridges outside the store lock
''', FARM_CLK + r'''# THE CLICK: Object[]{ status ("+..." / "-..." / "=..." / "" = nothing to say), pop text over the tree }. World thread; the bridges outside the store lock
''')
P.rep(r'''  if (kd == MK) return mine(u, k, kd, slot, spot, hand);   // 0.4.24: the Mining quarry
  if (kd != FK) return res("-Only the Foraging and Mining Shards have a clicker so far.", "");''',
      r'''  if (kd == MK) return mine(u, k, kd, slot, spot, hand);   // 0.4.24: the Mining quarry
  if (kd == CRK) return harvest(u, k, kd, slot, spot, hand);   // 0.4.25: the Farming clicker
  if (kd != FK) return res("-Only the Foraging, Mining and Farming Shards have a clicker so far.", "");''')
# Plot size = the Tree size purchase on a Farming island (same costs), its own maximum and words
P.rep(r'''  if (kd == MK && !@PKG@.ShCfg.MQ_ON) return "-The Mining quarry is switched off on this server.";   // 0.4.24
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  String no = @PKG@.ShCore.gateOwn(u, k, kd, p);
  if (no != null) return no;
  int t0; int lv; long ver;''', r'''  if (kd == MK && !@PKG@.ShCfg.MQ_ON) return "-The Mining quarry is switched off on this server.";   // 0.4.24
  if (kd == CRK && !@PKG@.ShCfg.FQ_ON) return "-The Farming clicker is switched off on this server.";   // 0.4.25
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  String no = @PKG@.ShCore.gateOwn(u, k, kd, p);
  if (no != null) return no;
  int t0; int lv; long ver;''')
P.rep(r'''  int mx = kd == MK ? @PKG@.ShCfg.MQ_NS_MAX : @PKG@.ShCfg.CK_NS_MAX;   // 0.4.24: Vein size on a Mining quarry
  if (lv >= mx) return kd == MK ? "=Vein size is at its highest level." : "=Tree size is at its highest level.";''',
      r'''  int mx = kd == MK ? @PKG@.ShCfg.MQ_NS_MAX : (kd == CRK ? @PKG@.ShCfg.FQ_NS_MAX : @PKG@.ShCfg.CK_NS_MAX);   // 0.4.24: Vein size on a Mining quarry; 0.4.25 Plot size
  if (lv >= mx) return kd == MK ? "=Vein size is at its highest level." : (kd == CRK ? "=Plot size is at its highest level." : "=Tree size is at its highest level.");''')
P.rep(r'''  String ok = kd == MK ? "+Vein size " + nl + "/" + mx + " on the Zone " + @PKG@.ShIsl.zoneOf(t0) + " quarry: " + blocksAt(nl) + " blocks a mined node."
      : "+Tree size " + nl + "/" + mx + " on the " + @PKG@.ShIsl.tname(t0) + " island: " + logsAt(nl) + " logs a felled tree.";''',
      r'''  String ok = kd == MK ? "+Vein size " + nl + "/" + mx + " on the Zone " + @PKG@.ShIsl.zoneOf(t0) + " quarry: " + blocksAt(nl) + " blocks a mined node."
      : (kd == CRK ? "+Plot size " + nl + "/" + mx + " on the " + @PKG@.ShIsl.tname(t0) + " island: " + plantsAt(nl) + " plants a harvest."
      : "+Tree size " + nl + "/" + mx + " on the " + @PKG@.ShIsl.tname(t0) + " island: " + logsAt(nl) + " logs a felled tree.");''')

# ---------------------------------------------------------------------------------------------------- 4. the farm's art (pure Python, appended to CLK_ART_SRC)
FART_SRC = r'''# 0.4.25 THE FARMING CLICKER ART (tools/shards_0_4_25_patch.py): one crop plot per crop (tilled soil + its plants), a harvested plot (sprouts), the map's
# farm islands, three upgrade icons. Our own geometry; FART(crops) -> {name: Pic}; crops = ladder keys by rank.
CROP_STY = {"wheat": ("stalk", "#e2b84a", "#fff0a0", "#8a6a1e"), "lettuce": ("head", "#7ccf4a", "#d2f7a0", "#3a7a22"),  # ui-data (picture colours)
            "carrot": ("root", "#ef8a2a", "#ffc27a", "#9a4a10"), "corn": ("tall", "#f2d24a", "#fff3a8", "#a8841a"),  # ui-data (picture colours)
            "cauliflower": ("curd", "#f2eee0", "#ffffff", "#b8b098"), "turnip": ("root", "#c89ad8", "#f4e4ff", "#7a4a8a"),  # ui-data (picture colours)
            "pumpkin": ("gourd", "#f08a24", "#ffc070", "#9a4a0e"), "aubergine": ("hang", "#6a2a8a", "#b07ad0", "#2e0e44"),  # ui-data (picture colours)
            "tomato": ("stake", "#e8402e", "#ff9a80", "#8a1a10"), "chilli": ("hang2", "#d8301e", "#ff8a6a", "#7a120a"),  # ui-data (picture colours)
            "cotton": ("puff", "#f8f8f4", "#ffffff", "#b8b8b0"), "rice": ("paddy", "#d8d070", "#f8f0b0", "#7a8a30"),  # ui-data (picture colours)
            "potato": ("bush", "#b08850", "#e0c08a", "#6a4a24"), "onion": ("bulb", "#e8c890", "#fff0d0", "#9a7040"),  # ui-data (picture colours)
            "mushroom": ("shroom", "#a8683a", "#e0a878", "#5a3018")}  # ui-data (picture colours)
LEAF = ("#4fa83a", "#a6e07a", "#235a1a")  # ui-data (picture colours)
SOIL = ("#6b4a2e", "#a07a52", "#3a2614")  # ui-data (picture colours)
STEM = {"wheat": "#b89a3a", "rice": "#5aa83a", "corn": "#5a9a3a", "tassel": "#d8b060", "stake": "#8a6a3a", "cotton": "#7a5a3a", "gourd": "#5a7a2a",  # ui-data (picture colours)
        "cap": "#efe4cc", "capL": "#ffffff", "capD": "#a89a80", "spot": "#f4e0c8", "water": ("#3f8ad0", "#8fd0f0")}  # ui-data (picture colours)


def _leaf(pic, x, y, rx, ry, seed=0, col=LEAF):
    ellipse(pic, x + rx * 0.12, y + ry * 0.16, rx, ry, _rgb(col[2]), 0.55)
    ellipse(pic, x, y, rx, ry, shade(col[0], col[1], col[2], x - rx * 0.3, y - ry * 0.3, max(rx, ry) * 1.2, ns=0.1, nsc=max(2.0, rx / 3.0), seed=seed))


def _soil(pic, cx, by, u, wet=False):
    ellipse(pic, cx + 3 * u, by + 2 * u, 50 * u, 9 * u, (10, 30, 12), 0.35)
    ellipse(pic, cx, by - 5 * u, 50 * u, 15 * u, shade(SOIL[0], SOIL[1], SOIL[2], cx - 14 * u, by - 12 * u, 50 * u, ns=0.18, nsc=3 * u, seed=5))
    if wet:
        ellipse(pic, cx, by - 6 * u, 42 * u, 11 * u, vgrad(STEM["water"][0], STEM["water"][1], by - 17 * u, by + 5 * u), 0.85)
    for i in range(3):
        yy = by - (12 - i * 6) * u
        hw = 44 * u * _m.sqrt(max(0.05, 1.0 - ((yy - (by - 5 * u)) / (15 * u)) ** 2))
        line(pic, cx - hw * 0.9, yy, cx + hw * 0.9, yy, 1.6 * u, _rgb(SOIL[2]), 0.25 if wet else 0.5)


def _sprout(pic, x, y, u, seed):
    line(pic, x, y, x, y - 6 * u, 1.2 * u, _rgb(LEAF[2]))
    _leaf(pic, x - 3 * u, y - 7 * u, 3 * u, 1.8 * u, seed)
    _leaf(pic, x + 3 * u, y - 7.5 * u, 3 * u, 1.8 * u, seed + 1)


def _plant(pic, st, x, y, u, seed):
    kind, mc, lc, dc = st
    if kind in ("stalk", "paddy"):   # wheat / rice: a bundle of stalks with ears
        n = 6 if kind == "stalk" else 7
        for i in range(n):
            dx = (i - (n - 1) / 2.0) * 2.3 * u
            tx = x + dx * 2.0 + (_hash(i, 1, seed) - 0.5) * 3 * u
            ty = y - ((40 if kind == "stalk" else 30) + 10 * _hash(i, 2, seed)) * u
            line(pic, x + dx, y, tx, ty + 6 * u, 1.3 * u, _rgb(STEM["wheat" if kind == "stalk" else "rice"]))
            ellipse(pic, tx, ty, (2.8 if kind == "stalk" else 1.8) * u, (8 if kind == "stalk" else 5) * u, shade(mc, lc, dc, tx - u, ty - 3 * u, 8 * u))
    elif kind == "head":   # lettuce: overlapping leaves
        for i, (ox, oy, r) in enumerate(((-6, -6, 8), (6, -6, 8), (0, -3, 9), (-3, -11, 7), (4, -12, 6))):
            _leaf(pic, x + ox * u, y + oy * u, r * u, r * 0.8 * u, seed + i, (mc, lc, dc))
    elif kind == "curd":   # cauliflower: leaves round a white curd
        for i, ox in enumerate((-9, 9)):
            _leaf(pic, x + ox * u, y - 6 * u, 8 * u, 6 * u, seed + i)
        _leaf(pic, x, y - 3 * u, 12 * u, 6 * u, seed + 3)
        for i in range(9):
            a = _hash(i, 3, seed) * 2 * _m.pi
            d = 5 * u * _m.sqrt(_hash(i, 4, seed))
            disc(pic, x + _m.cos(a) * d, y - 10 * u + _m.sin(a) * d * 0.7, 3.4 * u, shade(mc, lc, dc, x - 3 * u, y - 13 * u, 9 * u))
    elif kind in ("root", "bulb"):   # carrot / turnip: a fan of leaves over the root's top; onion: spikes over the bulb
        for i in range(6 if kind == "root" else 5):
            a = _m.radians((-150 + i * 24) if kind == "root" else (-120 + i * 15))
            tx, ty = x + _m.cos(a) * (18 if kind == "root" else 12) * u, y - 6 * u + _m.sin(a) * (22 if kind == "root" else 30) * u
            line(pic, x, y - 4 * u, tx, ty, (1.2 if kind == "root" else 1.8) * u, _rgb(LEAF[2] if kind == "root" else LEAF[0]))
            if kind == "root":
                _leaf(pic, tx, ty, 3.5 * u, 2.6 * u, seed + i)
        ellipse(pic, x, y - (2 if kind == "root" else 4) * u, 7 * u, (5 if kind == "root" else 6) * u, shade(mc, lc, dc, x - 2 * u, y - 5 * u, 7 * u))
    elif kind == "tall":   # corn: a stalk, long leaves, a cob
        line(pic, x, y, x, y - 76 * u, 3 * u, _rgb(STEM["corn"]))
        for yy, dr in ((20, 1), (34, -1), (48, 1), (60, -1)):
            poly(pic, [(x, y - yy * u), (x + dr * 20 * u, y - (yy + 12) * u), (x + dr * 24 * u, y - (yy + 8) * u), (x + dr * 4 * u, y - (yy - 2) * u)],
                 shade(LEAF[0], LEAF[1], LEAF[2], x, y - yy * u, 20 * u))
        ellipse(pic, x + 5 * u, y - 44 * u, 4.5 * u, 11 * u, shade(mc, lc, dc, x + 3 * u, y - 48 * u, 11 * u))
        poly(pic, [(x + 1 * u, y - 34 * u), (x + 9 * u, y - 34 * u), (x + 8 * u, y - 46 * u)], _rgb(LEAF[2]))
        line(pic, x, y - 76 * u, x + 3 * u, y - 84 * u, 1.2 * u, _rgb(STEM["tassel"]))
    elif kind == "gourd":   # pumpkin: vine leaves + a ribbed pumpkin
        _leaf(pic, x - 12 * u, y - 10 * u, 9 * u, 6 * u, seed)
        _leaf(pic, x + 13 * u, y - 9 * u, 8 * u, 5 * u, seed + 1)
        ellipse(pic, x, y - 8 * u, 13 * u, 10 * u, shade(mc, lc, dc, x - 4 * u, y - 12 * u, 14 * u))
        for dx in (-6, 0, 6):
            line(pic, x + dx * u, y - 17 * u, x + dx * 1.2 * u, y + 1 * u, 1 * u, _rgb(dc), 0.6)
        poly(pic, [(x - 1.5 * u, y - 17 * u), (x + 1.5 * u, y - 17 * u), (x + 3 * u, y - 23 * u), (x, y - 23 * u)], _rgb(STEM["gourd"]))
    elif kind in ("hang", "hang2", "stake"):   # aubergine / chilli / tomato: a leafy plant with its fruit
        if kind == "stake":
            line(pic, x + 6 * u, y, x + 6 * u, y - 56 * u, 2 * u, _rgb(STEM["stake"]))
        for i, (ox, oy, r) in enumerate(((-7, -24, 10), (7, -28, 10), (0, -40, 9), (0, -16, 9))):
            _leaf(pic, x + ox * u, y + oy * u, r * u, r * 0.8 * u, seed + i)
        if kind == "hang":
            for ox, oy in ((-8, -14), (6, -18), (1, -28)):
                ellipse(pic, x + ox * u, y + oy * u, 4 * u, 9 * u, shade(mc, lc, dc, x + (ox - 2) * u, y + (oy - 4) * u, 9 * u))
        elif kind == "hang2":
            for ox, oy in ((-9, -16), (-2, -24), (7, -18), (3, -34)):
                ellipse(pic, x + ox * u, y + oy * u, 2.2 * u, 6.5 * u, shade(mc, lc, dc, x + (ox - 1) * u, y + (oy - 3) * u, 6 * u))
        else:
            for ox, oy in ((-8, -22), (6, -30), (-2, -38), (8, -16)):
                disc(pic, x + ox * u, y + oy * u, 4.6 * u, shade(mc, lc, dc, x + (ox - 2) * u, y + (oy - 2) * u, 5 * u))
    elif kind == "puff":   # cotton: thin stalks with white puffs
        for i, (ox, hh) in enumerate(((-6, 30), (0, 38), (6, 32))):
            line(pic, x + ox * 0.4 * u, y, x + ox * u, y - hh * u, 1.4 * u, _rgb(STEM["cotton"]))
            _leaf(pic, x + ox * u - 3 * u, y - hh * 0.55 * u, 4 * u, 2.5 * u, seed + i)
            disc(pic, x + ox * u, y - hh * u, 5.5 * u, shade(mc, lc, dc, x + ox * u - 2 * u, y - hh * u - 2 * u, 6 * u))
    elif kind == "bush":   # potato: a leafy bush, the tubers peeking out
        for i, (ox, oy, r) in enumerate(((-8, -12, 9), (8, -13, 9), (0, -20, 10))):
            _leaf(pic, x + ox * u, y + oy * u, r * u, r * 0.8 * u, seed + i)
        for ox in (-11, 9):
            ellipse(pic, x + ox * u, y - 1 * u, 5 * u, 3.5 * u, shade(mc, lc, dc, x + (ox - 2) * u, y - 2 * u, 5 * u))
    else:   # mushroom: a pale stem + a brown cap with spots
        poly(pic, [(x - 3 * u, y), (x - 2.5 * u, y - 14 * u), (x + 2.5 * u, y - 14 * u), (x + 3 * u, y)], shade(STEM["cap"], STEM["capL"], STEM["capD"], x, y - 7 * u, 6 * u))
        pts = [(x + _m.cos(_m.pi + i * _m.pi / 16) * 13 * u, y - 13 * u + _m.sin(_m.pi + i * _m.pi / 16) * 10 * u) for i in range(17)]
        poly(pic, pts, shade(mc, lc, dc, x - 4 * u, y - 20 * u, 13 * u))
        for i in range(4):
            disc(pic, x + (_hash(i, 7, seed) - 0.5) * 16 * u, y - (16 + 5 * _hash(i, 8, seed)) * u, 1.6 * u, _rgb(STEM["spot"]), 0.85)


def fplot(st, W=110, H=140, s=2, seed=1, harvested=False):
    w, h = int(W * s), int(H * s)
    pic = Pic(w, h)
    u = float(s)
    cx, by = w / 2.0, h - 10.0 * u
    _soil(pic, cx, by, u, wet=(st[0] == "paddy" and not harvested))
    for i, (dx, dy) in enumerate(((-26, -13), (0, -16), (26, -13), (-14, -3), (14, -3))):
        x, y = cx + dx * u, by + dy * u
        if harvested:
            _sprout(pic, x, y, u, seed + 7 * i)
        else:
            _plant(pic, st, x, y, u * (0.85 if i < 3 else 1.0), seed + 7 * i)
    return pic


def fmini(st, tier, W=150, H=100, s=2):
    # the cluster map's farm island: a small floating island + 3 plots of that crop
    w, h = int(W * s), int(H * s)
    base = Pic(w, h)
    top = int(h * 0.30)
    paste(base, island(W, int(H * 0.70), s, seed=tier + 20), 0, top, 1.0)
    pl = fplot(st, 110, 140, s=1, seed=tier)
    gy = top + h * 0.70 * 0.34
    for fx, dy, sc in ((0.30, -0.06, 0.30), (0.70, -0.06, 0.30), (0.5, 0.08, 0.36)):
        paste(base, pl, int(w * fx - 110 * sc * s / 2.0), int(gy + dy * h * 0.70 - (140 - 10) * sc * s), sc * s)
    return base


def ficon(kind, st, s=2):
    W = 56
    p = Pic(int(W * s), int(W * s))
    if kind == "size":
        paste(p, fplot(st, 110, 140, s=1, seed=5), int(-2 * s), int(-6 * s), 0.46 * s)
        disc(p, 44 * s, 42 * s, 9 * s, _rgb("#4fd88a"))  # ui-data (picture colours)
        line(p, 44 * s, 37 * s, 44 * s, 47 * s, 3 * s, _rgb("#0b1322"))  # ui-data (picture colours)
        line(p, 39 * s, 42 * s, 49 * s, 42 * s, 3 * s, _rgb("#0b1322"))  # ui-data (picture colours)
    elif kind == "count":
        pl = fplot(st, 110, 140, s=1, seed=6)
        for ox, oy, sc in ((-10, -4, 0.32), (20, -6, 0.32), (5, 6, 0.36)):
            paste(p, pl, int(ox * s), int(oy * s), sc * s)
    else:   # Irrigation: a watering can + drops
        poly(p, [(12 * s, 26 * s), (34 * s, 26 * s), (36 * s, 46 * s), (10 * s, 46 * s)], shade("#7c9ab8", "#d8e8f8", "#34506e", 18 * s, 30 * s, 22 * s))  # ui-data (picture colours)
        line(p, 34 * s, 36 * s, 48 * s, 20 * s, 3.2 * s, _rgb("#5a7a9a"))  # ui-data (picture colours)
        ellipse(p, 49 * s, 19 * s, 3.2 * s, 2.2 * s, _rgb("#5a7a9a"))  # ui-data (picture colours)
        for a in range(7):
            r_ = _m.radians(180 + a * 30)
            line(p, 23 * s + _m.cos(r_) * 9 * s, 26 * s + _m.sin(r_) * 9 * s, 23 * s + _m.cos(r_ + 0.5) * 9 * s, 26 * s + _m.sin(r_ + 0.5) * 9 * s, 2.2 * s, _rgb("#5a7a9a"))  # ui-data (picture colours)
        for x_, y_ in ((50, 28), (46, 34), (52, 38), (48, 46)):
            ellipse(p, x_ * s, y_ * s, 1.8 * s, 2.6 * s, _rgb("#5fb0ff"), 0.95)  # ui-data (picture colours)
    return p


def FART(crops):
    out = {}
    for i, key in enumerate(crops):
        st = CROP_STY[key]
        out["FCrop%d" % i] = fplot(st, 110, 140, s=2, seed=31 + i)
        out["FMap%d" % i] = fmini(st, i + 1, 150, 100, s=2)
    out["FHarv"] = fplot(CROP_STY["wheat"], 110, 140, s=2, seed=3, harvested=True)
    out["UpFSize"] = ficon("size", CROP_STY["wheat"])
    out["UpFCount"] = ficon("count", CROP_STY["carrot"])
    out["UpFIrr"] = ficon("irr", None)
    return out


'''
P.rep('''def ART(tiers, sizes):
    # every picture of the clicker: {name: Pic}.''', FART_SRC + '''def ART(tiers, sizes):
    # every picture of the clicker: {name: Pic}.''')
P.rep(r'''MQ_NPIC = len(_q_pics)
del _q_pics
''', r'''MQ_NPIC = len(_q_pics)
del _q_pics
# 0.4.25 THE FARM'S PICTURES: one plot + one map farm island per crop, a harvested plot, 3 upgrade icons
_f_t0 = _time423.time()
_f_pics = CLK_ART["FART"]([_t["key"] for _t in LAD[FQ_K]])
for _n, _pic in sorted(_f_pics.items()):
    assert re.fullmatch(r"[A-Za-z0-9]+", _n) and _n not in CK_TEX, _n
    CK_TEX[_n] = MDIR + "Clk" + _n + ".png"
    SUI.register_map_textures([CK_TEX[_n]])
    MAP_ASSETS[MJAR + MDIR + "Clk" + _n + "@2x.png"] = _pic.png()
print("0.4.25 farm art: %d pictures drawn in %.1f s (%d KB)" % (len(_f_pics), _time423.time() - _f_t0,
      sum(len(MAP_ASSETS[MJAR + MDIR + "Clk" + _n + "@2x.png"]) for _n in _f_pics) // 1024))
FQ_NPIC = len(_f_pics)
assert FQ_NPIC == 34, FQ_NPIC
del _f_pics
''')

# ---------------------------------------------------------------------------------------------------- 5. the farm's page parts (segments) + the Java branches
FARM_PAGE = r'''# ---- 0.4.25 THE FARM PAGE PARTS (Farming): the crop plot pictures (run time, per island), the six upgrade rows with the farm's names + icons (the 0.4.23
# row ids: the Foraging rows' Java fills them), the farm map (5 zone clusters of 3 crops; the 0.4.23 card ids, locks, Open / Buy buttons)
CK_PAGE_STATIC += ["public static final String[] F_CROP = new String[] { %s };" % ", ".join(jlit(CK_TEX["FCrop%d" % _i]) for _i in range(len(LAD[FQ_K]))),
                   "public static final String F_HARV = %s;" % jlit(CK_TEX["FHarv"])]
FQ_UP_NAMES = ["Plot size", "Plot count", "Spirit totems", "Irrigation", "Island size", "Decorations"]
FQ_UP_ICON = ["UpFSize", "UpFCount", "UpSpirit", "UpFIrr", "UpIsize", "UpDeco"]
a_ = _ck_seg("fup")
a_.append((CK_BODY, G_.glass_group(CKP + "Up", CK_UPW, CK_BODY_H, role="panel", layout="Top", pad=12, anchor={"left": 12})))
a_.append((CK_UP, G_.glass_group(CKP + "UpH", CK_UIW, 32, layout="Left")))
a_.append(("#" + CKP + "UpH", _ck_glab(CKP + "UpT", 18, "gold", 150, 32, bold=True, text="UPGRADES")))
a_.append(("#" + CKP + "UpH", _ck_glab(CKP + "UpCap", 13, "dim", CK_UIW - 150, 32, halign="End")))
for _r in range(6):
    R_ = CKP + "U%d" % _r
    a_.append((CK_UP, G_.glass_group(R_, CK_UIW, CK_ROW_H, role="inset", layout="Left", pad=6, anchor={"top": 5})))
    a_.append(("#" + R_, "Group #%sI { Anchor: (Width: 64, Height: %d); }" % (R_, CK_ROW_H - 12)))
    a_.append(("#" + R_ + "I", SUI.map_pic(R_ + "P", 4, 6, 56, 56, CK_TEX[FQ_UP_ICON[_r]])))
    a_.append(("#" + R_, G_.glass_group(R_ + "T", CK_TXT_W, CK_ROW_H - 12, layout="Top", anchor={"left": 8})))
    a_.append(("#" + R_ + "T", G_.glass_group(R_ + "N", CK_TXT_W, 26, layout="Left")))
    a_.append(("#" + R_ + "N", _ck_glab(R_ + "Nm", 17, "title", 250, 26, bold=True, text=FQ_UP_NAMES[_r])))
    a_.append(("#" + R_ + "N", _ck_glab(R_ + "L", 15, "xp", CK_TXT_W - 250, 26, bold=True, halign="End")))
    a_.append(("#" + R_ + "T", _ck_glab(R_ + "E", 15, "text", CK_TXT_W, 24)))
    a_.append(("#" + R_ + "T", _ck_glab(R_ + "C", 14, "goldHi", CK_TXT_W, 22)))
    a_.append(("#" + R_ + "T", G_.glass_group(R_ + "B", CK_TXT_W, 34, layout="Left")))
    a_.append(("#" + R_ + "B", "Group { Anchor: (Width: %d); }" % (CK_TXT_W - 150)))
a_ = _ck_seg("fmap")
a_.append((CK_BODY, G_.glass_group(CKP + "Map", CK_IW, CK_BODY_H, layout="Left")))
for _z in range(5):
    Z_ = CKP + "Z%d" % _z
    a_.append(("#" + CKP + "Map", G_.glass_group(Z_, CK_ZW, CK_BODY_H, role="panel", layout="Top", pad=10, anchor={"right": 13} if _z < 4 else None)))
    a_.append(("#" + Z_, _ck_glab(Z_ + "N", 18, "gold", CK_CW, 30, bold=True, text="ZONE %d FARMS" % (_z + 1))))
    a_.append(("#" + Z_, _ck_glab(Z_ + "S", 14, "dim", CK_CW, 24)))
    for _q in range(3):
        _i = 3 * _z + _q
        M_ = CKP + "M%d" % _i
        a_.append(("#" + Z_, G_.glass_group(M_, CK_CW, CK_CARD_H, role="inset", layout="Top", pad=6, anchor={"top": 6})))
        a_.append(("#" + M_, "Group #%sG { Anchor: (Width: %d, Height: 140); }" % (M_, CK_CW - 12)))
        a_.append(("#" + M_ + "G", SUI.map_pic(M_ + "P", (CK_CW - 12 - 210) // 2, 0, 210, 140, CK_TEX["FMap%d" % _i])))
        a_.append(("#" + M_, _ck_glab(M_ + "N", 16, "title", CK_CW - 12, 22, bold=True)))
        a_.append(("#" + M_, _ck_wrap(M_ + "S", 13, "text", CK_CW - 12, 36)))
        a_.append(("#" + M_, G_.glass_group(M_ + "B", CK_CW - 12, 30, layout="Left")))

'''
P.rep(r'''# the run-time templates (checked with samples)
_tex0 = CK_TEX["Tree1"]''', FARM_PAGE + r'''# the run-time templates (checked with samples)
_tex0 = CK_TEX["Tree1"]''')
P.rep(r'''         _ck_jset(CKP + "Title", '(this.ckMine ? "MINING SHARD" : "FORAGING SHARD")'),''',
      r'''         _ck_jset(CKP + "Title", '(this.ckMine ? "MINING SHARD" : (this.ckFarm ? "FARMING SHARD" : "FORAGING SHARD"))'),   # 0.4.25''')
P.rep(r'''["  } else if (this.ckMode == 1) {", _ckj("map")]''',
      r'''["  } else if (this.ckMode == 1) {", "  if (this.ckFarm) {", _ckj("fmap"), "  } else {", _ckj("map"), "  }"]   # 0.4.25: the farm map''')
P.rep(r'''    "  if (this.ckSz >= 1 && this.manage && @PKG@.ShCfg.CK_ON && (!this.ckMine || @PKG@.ShCfg.MQ_ON)) {   // the click squares over the trees / nodes (on top of every picture)",''',
      r'''    "  if (this.ckSz >= 1 && this.manage && @PKG@.ShCfg.CK_ON && (!this.ckMine || @PKG@.ShCfg.MQ_ON) && (!this.ckFarm || @PKG@.ShCfg.FQ_ON)) {   // the click squares over the trees / nodes / plots (on top of every picture)",''')
P.rep(r'''["  } else {", _ckj("up"), _ck_jset(CKP + "UpCap", "this.ckUpCap")]''',
      r'''["  } else {", "  if (this.ckFarm) {", _ckj("fup"), "  } else {", _ckj("up"), "  }", _ck_jset(CKP + "UpCap", "this.ckUpCap")]   # 0.4.25: the farm's rows''')
P.rep(r'''print("0.4.24 quarry page: %d variants checked, elements: island at most %d + %d run-time = %d, map %s; %d Skyglass paths"
      % (len(Q_VARS), max(_q_el[:-2]), CK_NSPOT * 2 + 1 + 40, Q_ELEMENTS, _q_el[-2:], Q_GLASS_N))
''', r'''print("0.4.24 quarry page: %d variants checked, elements: island at most %d + %d run-time = %d, map %s; %d Skyglass paths"
      % (len(Q_VARS), max(_q_el[:-2]), CK_NSPOT * 2 + 1 + 40, Q_ELEMENTS, _q_el[-2:], Q_GLASS_N))
# 0.4.25 the farm variants: each island size with every part (decorations, totems, the rain totem = Irrigation) + the six rows on / off; the farm map
# with every card locked + bought, and every card open
F_VARS = []
for _s in (1, 2, 3):
    for _on in ("upon", "upoff"):
        v_ = SUI.Appends()
        for _n in ["frame", "mapb0", "frame2", "left", "isl%d" % _s] + ["deco%d_%d" % (_s, _j) for _j in range(5)] + ["tot%d_%d" % (_s, _j) for _j in range(5)] + \
                ["wx%d" % _s, "cap", "colall", "stotab", "fup"] + ["%s%d" % (_on, _r) for _r in range(6)] + ["foot"]:
            v_.extend(CKA[_n])
        F_VARS.append(v_)
v_ = SUI.Appends()
for _n in ["frame", "mapb1", "frame2", "fmap"] + ["mlock%d" % _i for _i in range(15)] + ["mbuy%d" % _i for _i in range(15)] + ["foot"]:
    v_.extend(CKA[_n])
F_VARS.append(v_)
v_ = SUI.Appends()
for _n in ["frame", "mapb1", "frame2", "fmap"] + ["mopen%d" % _i for _i in range(15)] + ["foot"]:
    v_.extend(CKA[_n])
F_VARS.append(v_)
for _i, v_ in enumerate(F_VARS):
    v_.check(CKP)
    _pri = sum(1 for p_, mk_ in v_ if 'TexturePath: "SkyyGlass/Primary.png"' in SUI.render(mk_))   # ui-data: counting the Skyglass Primary buttons
    assert _pri <= 1, "0.4.25 farm variant %d: %d Primary buttons" % (_i, _pri)
SUI.assert_proven([mk_ for v_ in F_VARS for p_, mk_ in v_], what="SkyyShards 0.4.25 Farming clicker page")
F_GLASS_N = SUI.assert_glass_paths([mk_ for v_ in F_VARS for p_, mk_ in v_])
_f_el = [sum(SUI._strip_quoted(SUI.render(mk_)).count("{") for p_, mk_ in v_) for v_ in F_VARS]
F_ELEMENTS = max(_f_el[:-2]) + CK_NSPOT * 2 + 1 + 8 * 5
assert F_ELEMENTS < 1000 and max(_f_el[-2:]) < 1000, "0.4.25: the farm page stays well under ~1,600 elements: %s / %s" % (F_ELEMENTS, _f_el)
print("0.4.25 farm page: %d variants checked, elements: island at most %d + %d run-time = %d, map %s; %d Skyglass paths"
      % (len(F_VARS), max(_f_el[:-2]), CK_NSPOT * 2 + 1 + 40, F_ELEMENTS, _f_el[-2:], F_GLASS_N))
''')

# ---------------------------------------------------------------------------------------------------- 6. the page: the Farming footer, kopen, fill / act for the farm
P.rep(r'''    "  boolean ckF = (this.kind == %d && @PKG@.ShCfg.CK_ON) || (this.kind == %d && @PKG@.ShCfg.CK_ON && @PKG@.ShCfg.MQ_ON);   // 0.4.23: the Foraging Shard's footer opens the clicker; 0.4.24: the Mining Shard's the quarry" % (CK_FK, MQ_K),''',
      r'''    "  boolean ckF = (this.kind == %d && @PKG@.ShCfg.CK_ON) || (this.kind == %d && @PKG@.ShCfg.CK_ON && @PKG@.ShCfg.MQ_ON) || (this.kind == %d && @PKG@.ShCfg.CK_ON && @PKG@.ShCfg.FQ_ON);   // 0.4.23: the Foraging Shard's footer opens the clicker; 0.4.24: the Mining Shard's the quarry; 0.4.25: the Farming Shard's the farm" % (CK_FK, MQ_K, FQ_K),''')
P.rep(r'''    if (this.view != 0 || (this.kind != @PKG@.ShClk.FK && this.kind != @PKG@.ShClk.MK)) return "";
    if (!@PKG@.ShCfg.CK_ON) return "-The shard clicker is switched off on this server.";
    if (this.kind == @PKG@.ShClk.MK && !@PKG@.ShCfg.MQ_ON) return "-The Mining quarry is switched off on this server.";   // 0.4.24''',
      r'''    if (this.view != 0 || (this.kind != @PKG@.ShClk.FK && this.kind != @PKG@.ShClk.MK && this.kind != @PKG@.ShClk.CRK)) return "";
    if (!@PKG@.ShCfg.CK_ON) return "-The shard clicker is switched off on this server.";
    if (this.kind == @PKG@.ShClk.MK && !@PKG@.ShCfg.MQ_ON) return "-The Mining quarry is switched off on this server.";   // 0.4.24
    if (this.kind == @PKG@.ShClk.CRK && !@PKG@.ShCfg.FQ_ON) return "-The Farming clicker is switched off on this server.";   // 0.4.25''')
P.rep(r'''  else if (this.view == 5) fillClick(k, cs, ref, st);   // 0.4.23
''', r'''  else if (this.view == 5 && this.kind == @PKG@.ShClk.CRK) fillFarm(k, cs, ref, st);   // 0.4.25
  else if (this.view == 5) fillClick(k, cs, ref, st);   // 0.4.23
''')
P.rep(r'''  this.title = "Mining Shard";
  this.ckMine = true;
''', r'''  this.title = "Mining Shard";
  this.ckMine = true;
  this.ckFarm = false;   // 0.4.25
''')
P.rep(r'''  this.ckMine = false; this.ckTexA = null; this.ckTexB = null; this.ckQSm = 0; this.ckQPct = 0; this.ckZone = 0;   // 0.4.24
''', r'''  this.ckMine = false; this.ckTexA = null; this.ckTexB = null; this.ckQSm = 0; this.ckQPct = 0; this.ckZone = 0;   // 0.4.24
  this.ckFarm = false;   // 0.4.25
''')
# fillFarm = fillClick (as patched above) with the farm's kind, pictures, tool, words and Plot size numbers - derived here, every swap asserted
_FC0 = 'M(page, r"""\npublic void fillClick(String k, @IC@[] cs, @REF@ ref, @ST@ st) {'
_FC1 = '\n}""")\nM(page, r"""\npublic void buildClick('
_i0 = P.s.index(_FC0) + len('M(page, r"""\n')
_FT = P.s[_i0:P.s.index(_FC1, _i0)]
assert P.s.count(_FC0) == 1 and _FT.count("public void ") == 1
_FT = sub1(_FT, "public void fillClick(String k, @IC@[] cs, @REF@ ref, @ST@ st) {", "public void fillFarm(String k, @IC@[] cs, @REF@ ref, @ST@ st) {   // 0.4.25: = fillClick for the Farming Shard (tools/shards_0_4_25_patch.py)")
_FT = sub1(_FT, "  this.kind = @PKG@.ShClk.FK;\n", "  this.kind = @PKG@.ShClk.CRK;\n")
_FT = sub1(_FT, '  this.title = "Foraging Shard";\n', '  this.title = "Farming Shard";\n')
_FT = sub1(_FT, "  this.ckFarm = false;   // 0.4.25\n", "  this.ckFarm = true;   // 0.4.25: the farm\n")
_FT = sub1(_FT, "  this.ckTree = CK_TREE[0]; this.ckStump = CK_STUMP[0];\n", "  this.ckTree = F_CROP[0]; this.ckStump = F_HARV;\n")
_FT = sub1(_FT, '  this.ckChip = "No island yet";', '  this.ckChip = "No farm yet";')
_FT = sub1(_FT, "  this.ckAxe = @PKG@.ShClk.axeTier(this.ckHand);\n", "  this.ckAxe = @PKG@.ShClk.hoeTier(this.ckHand);   // 0 = bare hands / no farming tool (a Crude hoe in the world's gate)\n")
_FT = sub1(_FT, '''  this.ckInfo = this.ckAxe > 0 ? "Chopping with your " + @PKG@.ShTotem.pretty(this.ckHand) + " (T" + this.ckAxe + ") - clicks give " + @PKG@.ShCfg.CK_XP_PCT + " % of world XP"
      : "Hold a hatchet to chop - the clicker uses the hatchet in your hand.";
  if (!@PKG@.ShCfg.CK_ON) this.ckInfo = "The shard clicker is switched off on this server.";
''', '''  this.ckInfo = (this.ckAxe > 0 ? "Harvesting with your " + @PKG@.ShTotem.pretty(this.ckHand) + " (T" + this.ckAxe + ")" : "Harvesting by hand (a Crude hoe) - hold a hoe or sickle for higher crops")
      + " - clicks give " + @PKG@.ShCfg.CK_XP_PCT + " % of world XP";
  if (!@PKG@.ShCfg.CK_ON || !@PKG@.ShCfg.FQ_ON) this.ckInfo = "The Farming clicker is switched off on this server.";
''')
_FT = sub1(_FT, '''    int tt = @PKG@.ShIsl.TIER[t];
    int ti = tt < 1 ? 0 : (tt > CK_TREE.length ? CK_TREE.length - 1 : tt - 1);
    this.ckTree = CK_TREE[ti]; this.ckStump = CK_STUMP[ti];
''', '''    int ti = t - L0;
    if (ti < 0) ti = 0;
    if (ti >= F_CROP.length) ti = F_CROP.length - 1;
    this.ckTree = F_CROP[ti]; this.ckStump = F_HARV;   // the island's crop plots; a harvested plot = sprouts while it regrows
''')
_FT = sub1(_FT, '''    this.ckCap = "Click a tree to chop it (" + this.ckTn + " trees, " + @PKG@.ShClk.logsAt(ns) + " logs a tree). Your spirits keep working while you are away.";''',
           '''    this.ckCap = "Click a crop plot to harvest it (" + this.ckTn + " plots, " + @PKG@.ShClk.plantsAt(ns) + " plants a harvest). Your spirits keep working while you are away.";''')
_FT = sub1(_FT, "    int mx = @PKG@.ShCfg.CK_NS_MAX;\n", "    int mx = @PKG@.ShCfg.FQ_NS_MAX;\n")
_FT = sub1(_FT, '    String key2 = k + "|" + this.ckSlot;\n', '    String key2 = k + "|" + kd + "|" + this.ckSlot;   // the farm\'s own plot memory (= ShClk.harvest)\n')
_FT = sub1(_FT, '''    if (ns >= mx) this.ckUpE[0] = "Logs a felled tree: " + @PKG@.ShClk.logsAt(ns) + " (highest)";
    else {
      this.ckUpE[0] = "Logs a felled tree " + @PKG@.ShClk.logsAt(ns) + " -> " + @PKG@.ShClk.logsAt(ns + 1);''', '''    if (ns >= mx) this.ckUpE[0] = "Plants a harvest: " + @PKG@.ShClk.plantsAt(ns) + " (highest)";
    else {
      this.ckUpE[0] = "Plants a harvest " + @PKG@.ShClk.plantsAt(ns) + " -> " + @PKG@.ShClk.plantsAt(ns + 1);''')
_FT = sub1(_FT, '''this.ckUpE[1] = "Trees: " + this.ckTn''', '''this.ckUpE[1] = "Plots: " + this.ckTn''')
_FT = sub1(_FT, '''this.ckUpE[1] = "Trees " + this.ckTn''', '''this.ckUpE[1] = "Plots " + this.ckTn''')
_FT = sub1(_FT, '"Spirits chop for you, also while you are away"', '"Spirits farm for you, also while you are away"')
_FT = sub1(_FT, "@PKG@.ShClk.regrowMs(", "@PKG@.ShClk.farmRegrowMs(", 3)
_FT = sub1(_FT, '" -> " + ckSize(sz + 1) + ": room for " + @PKG@.ShIsl.tx(sz + 1).length + " trees";', '" -> " + ckSize(sz + 1) + ": room for " + @PKG@.ShIsl.tx(sz + 1).length + " plots";')
_FT = sub1(_FT, '"First Tree count, Weather and Decorations 5/5 ("', '"First Plot count, Irrigation and Decorations 5/5 ("')
_FT = sub1(_FT, '} else this.ckCap = "No Foraging island yet - open Islands to buy the first one.";', '} else this.ckCap = "No Farming island yet - open Islands to buy the first one.";')
assert "CK_TREE" not in _FT and "axeTier" not in _FT and "logsAt" not in _FT and "regrowMs(irr" not in _FT.replace("farmRegrowMs(irr", ""), "fillFarm still names a Foraging part"
FARM_FILL = 'M(page, r"""\n' + _FT + '\n}""")\n' + r'''# 0.4.25: a farm action is fresh only while the page still shows this profile's island of that crop in that slot (a profile switch / another island = stale)
M(page, r"""
public boolean farmFresh(String k, int slot) {
  if (k == null || this.key == null || !k.equals(this.key) || this.ckT < 0) return false;
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return false;
  boolean ok;
  @PKG@.ShStore.LOCK.lock(); try {
    ok = slot >= 0 && slot < @PKG@.ShMath.SLOTS && @PKG@.ShMath.hasIsland(@PKG@.ShClk.CRK, p, slot) && @PKG@.ShIsl.ty(@PKG@.ShClk.CRK, p, slot) == this.ckT;
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  return ok;
}""")
'''
P.rep(_FC0, FARM_FILL + _FC0)
# actClick serves the farm too: its kind, the stale-island guard on a plot click and an upgrade
P.rep(r'''  int kd = @PKG@.ShClk.FK;
  if (a.startsWith("kt")) {   // a tree: "kt<spot>:<island slot>" = what the page showed
    int c = a.indexOf(':');
    int spot = -1; int slot = -1;
    try { spot = Integer.parseInt(a.substring(2, c < 0 ? a.length() : c)); slot = c < 0 ? -1 : Integer.parseInt(a.substring(c + 1)); } catch (Throwable x) { spot = -1; }
    if (spot < 0 || slot < 0 || slot != this.ckSlot) return "=The page is up to date now.";
''', r'''  int kd = this.kind == @PKG@.ShClk.CRK ? @PKG@.ShClk.CRK : @PKG@.ShClk.FK;   // 0.4.25: the Farming clicker shares this page
  if (a.startsWith("kt")) {   // a tree / a plot: "kt<spot>:<island slot>" = what the page showed
    int c = a.indexOf(':');
    int spot = -1; int slot = -1;
    try { spot = Integer.parseInt(a.substring(2, c < 0 ? a.length() : c)); slot = c < 0 ? -1 : Integer.parseInt(a.substring(c + 1)); } catch (Throwable x) { spot = -1; }
    if (spot < 0 || slot < 0 || slot != this.ckSlot) return "=The page is up to date now.";
    if (kd == @PKG@.ShClk.CRK && !farmFresh(k, slot)) return "=The page is up to date now.";   // 0.4.25: a stale farm island
''')
P.rep(r'''    if (s < 0) return "-Pick an island first.";
    @IC@[] cs = invOf(ref, st);''', r'''    if (s < 0) return "-Pick an island first.";
    if (kd == @PKG@.ShClk.CRK && !farmFresh(k, s)) return "=The page is up to date now - click Upgrade again.";   // 0.4.25: a stale farm island
    @IC@[] cs = invOf(ref, st);''')
P.rep(r'''          "public boolean ckMine;", "public String[] ckTexA;", "public String[] ckTexB;", "public int ckQSm;", "public int ckQPct;", "public int ckZone;"):   # 0.4.24 the quarry''',
      r'''          "public boolean ckMine;", "public String[] ckTexA;", "public String[] ckTexB;", "public int ckQSm;", "public int ckQPct;", "public int ckZone;",   # 0.4.24 the quarry
          "public boolean ckFarm;"):   # 0.4.25 the farm''')

# ---------------------------------------------------------------------------------------------------- 7. the ready line
P.rep(r'''log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.24:''', r'''log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.25: the Farming Shard clicker (Shard clicker in the Farming Shard menu: harvest crop plots with your hoe / sickle under the world's farming gate, one island per crop in zone clusters, Plot size, Farming zone locks; Fortune via skill:fn:fortune); 0.4.24:''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
_i = P.s.index
assert _i("public static Object[] harvest(java.util.UUID u") < _i("public static Object[] chop(java.util.UUID u"), "harvest() compiled before chop()"
assert _i("public static double fortuneOf(") < _i("public static Object[] harvest(java.util.UUID u"), "fortuneOf before harvest"
assert _i("public static Object[] mine(java.util.UUID u") < _i("public static Object[] harvest(java.util.UUID u"), "mine before harvest (part, addTo, rnd)"
assert _i("public static long plantsAt(int ns)") < _i("public static String buyNode("), "plantsAt before buyNode"
assert _i("public void fillFarm(") < _i("public void build0("), "fillFarm before build0"
assert _i("public boolean farmFresh(") < _i("public String actClick("), "farmFresh before actClick"
P.finish()
