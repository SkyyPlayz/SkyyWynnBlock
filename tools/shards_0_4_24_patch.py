"""Derive SkyyShards/build_skyyshards_0.4.24.py from the GENERATED SkyyShards 0.4.23 (build_skyyshards_0.4.23.py = the tools/deploy_set.py SET
pin, made by tools/shards_0_4_23_patch.py - edit the patch, never the generated file). Every anchor is asserted once; at the end every change
is undone on a copy and compared with 0.4.23 (tools/soundpass_gen.Patch). Line endings kept.
Run:   python tools/shards_0_4_24_patch.py   then   python SkyyShards/build_skyyshards_0.4.24.py   (never --deploy)
Check: python SkyyShards/test_skyyshards_0.4.24.py

0.4.24 (2026-11-21) = SHARD CLICKER 2: THE MINING QUARRY + THE SMITHY (round mine1; Skyy 2026-11-14 docs/answered/world.md "MINING SHARD = QUARRY, ONE
  ISLAND PER ZONE": "the mine one is a big quarry that also has an island per zone instead of by ore. so the zone 1 island gives copper, iron with an
  upgrade. (silver and gold are found in all of them with upgrades to make them more common, but it follows vanilla trends, so silverr is most popular in
  zone 3. so you uprgade the miner spirits and the quarry to mine faster, and upgrade your chances of getting something good per block mined. (this way you
  get all the stone types too, not just ore.)"; "SKILL PAGE ALLOYS + MINING SHARD SMITHY": "in the mining shard we will add a upgrade/addon with a smithy. the
  smithy makes all ares auto smelt to bars, and with an upgrade allow you to automatically smelt some of your ores into an alloy (slider for % of ore auto
  smelted to an alloy."; "have zone locks for all the shards"; on shard-clicker-mining.png "i love it"; Skyy 2026-11-21 "build and deploy everything on
  your list"). Reuses the 0.4.23 Foraging clicker's machinery whole (ShClk, page view 5, the .drops store, the click cap, the tier gate, the upgrades'
  costs, the zone map, Server Setup rows, the per-profile XP fractions).
  SPEC (short; the survey first):
  - SURVEY. Vanilla (Assets.zip): no quarry / clicker page; an ore block drops its ore AND its host rock's cobble (Ore_Copper_Stone -> Ore_Copper +
    Rock_Stone_Cobble) - so every quarry block gives its zone's stone. Silver / Gold (Server/World/Default/Ores/Zone1-4 + Zones/Zone3_Tier2/Cave/Ores):
    a thin Silver vein in zones 1-4, Gold in zones 1-3, both with extra cave veins only in Zone 3 = Silver most common in zone 3, no Gold in zone 4 (our
    default weights follow that; Skyy: "found in all of them", so zone 4 / 5 keep a small chance). Furnace: 1 ore -> 1 bar (vanilla recipes; the
    0.3 Auto-Smelt Pole already does 1 : 1); alloys: SkyyWorldGen's SkyyAlloy recipes (0.7.5+) 1 bar + 1 bar -> 2 alloy bars, zone pairs Copper + Iron
    -> Bronze, Thorium + Lead -> Dusk, Cobalt + Chromium -> Azurvane, Adamantite + Slag -> Cinder, Mithril + Titanium -> Lumen (copied numbers, no new
    balance). Mods: pie-clicker (0.4.23's survey) only; nothing new packed.
  - 1. THE QUARRY = view 5 of the Mining Shard's page (the footer's "Shard clicker", as Foraging): ONE QUARRY PER ZONE. The zone's quarry is its lowest
    owned Mining island (the BASE island: its storage, upgrades, totems); every Mining island you own in that zone adds its ore's NODES to the quarry
    (Zone 1: Copper; Iron = the Iron island = "Iron with an upgrade", bought from the quarry's map at the Map tab's cost). Node spots = the island's tree
    spots (Ore Amount decides how many, as Tree count); spot i mines ore i mod (owned ores of the zone). Click a node with your real pickaxe: the
    WORLD's tier gate (as 0.4.23: one tier up 2.5x the hits, two up 10x, three+ refused), Breaking Power bp.mining, click.maxPerSec counted clicks.
    A node takes click.mine.hp (12) damage, then breaks into click.mine.blocks (3) + Vein size x click.mine.sizeBlocks (1) BLOCKS; every block = 1 cobble
    of the node's host rock + click.mine.orePercent (40 %) + Lucky x click.mine.oreLuck (8 %) chance of 1 ore + a Silver / Gold chance of
    (click.mine.rarePermille (10 = 1 %) + Lucky x click.mine.rareLuck (10)) / 1000 x the zone's click.mine.silverWeight / goldWeight / 10
    (10,10,20,10,5 / 8,8,15,3,3); every ore / Silver / Gold found rolls Fortune (skill:fn:fortune = SkyySkills' own number for that ore block, else the
    0.4.23 skill:bonus sum of dd.mining). XP = click.xpPercent (25) % of xp.copper per BASE ore / Silver / Gold that fit (cobble and Fortune extras pay
    none). The node refills in click.mine.refillSec (10) - Springs x click.mine.springSec (1), at least click.mine.minRefillSec (3) (memory only).
  - 2. THE DROPS go into the base island's .drops (0.4.23's store, saved at once, counted against its storage; Collect / a grid cell / Collect all pay
    them first; the collection credit of a bar = its ore, an alloy = its two ores half each). What does not fit: the good finds first, then ore, then cobble.
  - 3. THE SMITHY (row 8): Smithy I = an Auto-Smelt Pole on the quarry's base island (the 0.3 totem, its existing cost - placed on the Totems tab): every
    ore / Silver / Gold the clicker mines is stored as its bar, 1 : 1. Smithy II (new key mining.i<n>.smithy = 1; click.mine.smithyHours (0.25) hours
    of the coin curve + click.mine.smithyEnch (16) of the island's Enchanted bar) adds the ALLOY SLIDER mining.i<n>.alloyPct (0-100 in
    click.mine.alloyStep (10) steps; click.mine.alloyDefault (50) after buying; < / > buttons, free, the kit has no proven slider): pct % of the new bars
    of the zone's two alloy metals pair with the other metal's stored bars, 1 + 1 -> 2 alloy bars (bars out = bars in; nothing without a partner bar).
    Fractions wait in memory per island; what found no partner is dropped (never a backlog, never a free bar).
  - 4. THE EIGHT UPGRADES (coins + the island's Enchanted bar, exactly the Map tab's / 0.4.23's costs where they map): Vein size = mining.i<n>.nsize
    (0.4.23's Tree size purchase + numbers), Ore nodes = Ore Amount, Miner spirits = the Totems tab, Springs = Underground Springs, Island size = Grow,
    Decorations, Lucky finds = NEW mining.i<n>.luck 0..click.mine.luckMax (5) at the Ore Amount cost of that level, Smithy (above). A button carries
    the level the page showed: a double click buys once.
  - 5. ZONE LOCKS FOR MINING (Skyy "have zone locks for all the shards"): ShIsl.zoneNeed for Mining = click.mine.zoneLevel (0 / 20 / 40 / 60 / 80
    Mining, until a real zone signal exists); buyIsland0 asks it (Map tab + quarry map); an island you own stays yours (nothing lost). Onyxium (T16,
    parked Zone 6) sits in the Zone 5 quarry.
  - 6. FORTUNE BRIDGE (SkyySkills 0.4.72 skill:fn:fortune): both clickers ask SkyySkills for the exact Fortune of the block (level perk + every source +
    caps + bridge.bonus.enabled); without it the 0.4.23 own sum is used.
  NUMBERS (new, Server Setup -> Shards -> Shard clicker; all editable): click.mine.enabled true, click.mine.hp 12, click.mine.blocks 3,
    click.mine.sizeBlocks 1, click.mine.sizeMax 10, click.mine.orePercent 40, click.mine.oreLuck 8, click.mine.rarePermille 10, click.mine.rareLuck 10,
    click.mine.silverWeight 10,10,20,10,5, click.mine.goldWeight 8,8,15,3,3, click.mine.luckMax 5, click.mine.refillSec 10, click.mine.springSec 1,
    click.mine.minRefillSec 3, click.mine.smithyHours 0.25, click.mine.smithyEnch 16, click.mine.alloyDefault 50, click.mine.alloyStep 10,
    click.mine.zoneLevel 0,20,40,60,80. Copied (not new): 1 ore -> 1 bar, 1 + 1 -> 2 alloy, the Tree size coin / Enchanted table for Vein size, the
    Ore Amount cost for Lucky finds.
  ART: research/ui-theme-art/shard-clicker-mining.png was the basic design; the build draws its own (CLK_ART_SRC QART: 3 quarry islands with terraces,
    11 ore nodes + 11 rubble piles (host rock + ore flecks per ore), 11 map quarries, springs, smithy, 5 upgrade icons) -> Common/UI/Custom/SkyyShards/Map/ClkQ*@2x.png.
  SAVED DATA: mining.i<n>.nsize / .luck / .smithy / .alloyPct (missing = 0 / 0 / 0 / 50) and mining.i<n>.drops (mined, not collected yet). Old files
    load unchanged; no migration (nothing is moved or rewritten).
  ROLLBACK 0.4.24 -> 0.4.23 alone: no migration. 0.4.23 ignores nsize / luck / smithy / alloyPct on Mining (kept in the file) and never pays
    mining .drops but counts them against the island's storage (an island full of mined blocks pauses until 0.4.24 is back): before rolling back,
    Collect all on the Mining Shard. Mining zone locks disappear (islands buyable at any level again). SkyySkills 0.4.72 may stay or go alone.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

HERE = os.path.join(ROOT, "SkyyShards")
P = G.Patch(os.path.join(HERE, "build_skyyshards_0.4.23.py"), os.path.join(HERE, "build_skyyshards_0.4.24.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.4.23"\n') and P.has("GENERATED by tools/shards_0_4_23_patch.py") and P.has("ShClk") and not P.has("fillQuarry"), "not the generated SkyyShards 0.4.23"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.24 (2026-11-21)"):].rstrip() + "\n"

# ---------------------------------------------------------------------------------------------------- 0. header + version
P.rep('''"""SkyyShards 0.4.23 - build script (javassist via jpype). GENERATED by tools/shards_0_4_23_patch.py from build_skyyshards_0.4.22.py
(generated by tools/shards_0_4_22_patch.py from 0.4.21, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.23" /''', '''"""SkyyShards 0.4.24 - build script (javassist via jpype). GENERATED by tools/shards_0_4_24_patch.py from build_skyyshards_0.4.23.py
(generated by tools/shards_0_4_23_patch.py from 0.4.22, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.24" / "0.4.23" /''')
P.rep('''Run:   python SkyyShards/build_skyyshards_0.4.23.py   -> SkyyShards/SkyyShards-0.4.23.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.23.py
''', '''Run:   python SkyyShards/build_skyyshards_0.4.24.py   -> SkyyShards/SkyyShards-0.4.24.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.24.py
''' + NOTE + '''
''')
P.rep('VERSION = "0.4.23"\n', 'VERSION = "0.4.24"\n')

# ---------------------------------------------------------------------------------------------------- 1. ShCfg: the quarry's settings
P.rep(r'''assert len(CK_NS_H) == len(CK_NS_Q) == 10 and len(CK_ZLV) == 5 and CK_FK == 1
''', r'''assert len(CK_NS_H) == len(CK_NS_Q) == 10 and len(CK_ZLV) == 5 and CK_FK == 1
# 0.4.24 THE MINING QUARRY (tools/shards_0_4_24_patch.py): its settings (Server Setup -> Shards -> Shard clicker, rows click.mine.*)
MQ_K = KINDS.index("Mining")
MQ_ZLV = [0, 20, 40, 60, 80]          # Zone 1..5 quarry islands are bought from this Mining level
MQ_SW = [10, 10, 20, 10, 5]           # Silver weight a zone (tenths of the rare chance): vanilla's thin vein in zones 1-4 + the Zone 3 cave veins
MQ_GW = [8, 8, 15, 3, 3]              # Gold weight a zone: zones 1-3 + the Zone 3 cave veins, none in vanilla zone 4 (Skyy: "found in all of them")
assert MQ_K == 0 and len(MQ_ZLV) == len(MQ_SW) == len(MQ_GW) == 5
for f in ("public static volatile boolean MQ_ON = true;", "public static volatile int MQ_HP = 12;", "public static volatile int MQ_BLOCKS = 3;",
          "public static volatile int MQ_NS_PER = 1;", "public static volatile int MQ_NS_MAX = 10;", "public static volatile int MQ_ORE = 40;",
          "public static volatile int MQ_ORE_LUCK = 8;", "public static volatile int MQ_RARE = 10;", "public static volatile int MQ_RARE_LUCK = 10;",
          "public static volatile int MQ_LUCK_MAX = 5;", "public static volatile int MQ_REFILL = 10;", "public static volatile int MQ_SPRING = 1;",
          "public static volatile int MQ_RMIN = 3;", "public static volatile double MQ_SM_H = 0.25;", "public static volatile int MQ_SM_Q = 16;",
          "public static volatile int MQ_ALLOY_DEF = 50;", "public static volatile int MQ_ALLOY_STEP = 10;",
          "public static final int[] DEF_MQ_ZLV = new int[] { %s };" % ", ".join(str(_x) for _x in MQ_ZLV),
          "public static volatile int[] MQ_ZLV = new int[] { %s };" % ", ".join(str(_x) for _x in MQ_ZLV),
          "public static final int[] DEF_MQ_SW = new int[] { %s };" % ", ".join(str(_x) for _x in MQ_SW),
          "public static volatile int[] MQ_SW = new int[] { %s };" % ", ".join(str(_x) for _x in MQ_SW),
          "public static final int[] DEF_MQ_GW = new int[] { %s };" % ", ".join(str(_x) for _x in MQ_GW),
          "public static volatile int[] MQ_GW = new int[] { %s };" % ", ".join(str(_x) for _x in MQ_GW)):
    F(cfg, f)
''')
P.rep(r'''         ("click.zoneLevel", "Zone opens at Foraging level", "clicker", "text", ",".join(str(_x) for _x in CK_ZLV), "", "60", "", "", "live",
          "5 numbers, Zone 1..5: islands of a zone are bought from this Foraging level.", "reload@config.properties:click.zoneLevel")]
''', r'''         ("click.zoneLevel", "Zone opens at Foraging level", "clicker", "text", ",".join(str(_x) for _x in CK_ZLV), "", "60", "", "", "live",
          "5 numbers, Zone 1..5: islands of a zone are bought from this Foraging level.", "reload@config.properties:click.zoneLevel")]
# 0.4.24: the Mining quarry's rows
ROWS += [("click.mine.enabled", "Mining quarry", "clicker", "bool", "true", "", "", "", "", "live",
          "Off: the Mining Shard menu shows no quarry and clicks do nothing. Nothing is deleted.", "reload@config.properties:click.mine.enabled"),
         ("click.mine.hp", "Quarry: hits to break a node", "clicker", "int", "12", "1", "1000", "", "", "live",
          "Damage an ore node takes before it breaks (1 hit = 1 with a pickaxe of the ore's tier).", "reload@config.properties:click.mine.hp"),
         ("click.mine.blocks", "Quarry: blocks per node", "clicker", "int", "3", "1", "1000", "", "", "live",
          "Blocks a broken node gives before Vein size (each: 1 cobble + a chance of ore).", "reload@config.properties:click.mine.blocks"),
         ("click.mine.sizeBlocks", "Quarry: more blocks per Vein size", "clicker", "int", "1", "0", "100", "", "", "live",
          "Each Vein size level adds this many blocks to a broken node.", "reload@config.properties:click.mine.sizeBlocks"),
         ("click.mine.sizeMax", "Quarry: Vein size levels", "clicker", "int", "10", "0", "10", "", "", "live",
          "The highest Vein size level (costs: the Tree size rows).", "reload@config.properties:click.mine.sizeMax"),
         ("click.mine.orePercent", "Quarry: ore chance a block", "clicker", "int", "40", "0", "100", "", "%", "live",
          "Chance a mined block also gives 1 ore (Lucky finds adds more).", "reload@config.properties:click.mine.orePercent"),
         ("click.mine.oreLuck", "Quarry: ore chance per Lucky level", "clicker", "int", "8", "0", "100", "", "%", "live",
          "More ore chance per Lucky finds level.", "reload@config.properties:click.mine.oreLuck"),
         ("click.mine.rarePermille", "Quarry: Silver / Gold base (1/1000)", "clicker", "int", "10", "0", "1000", "", "", "live",
          "Silver / Gold chance a block in 1/1000 (10 = 1 %), times the zone weight / 10.", "reload@config.properties:click.mine.rarePermille"),
         ("click.mine.rareLuck", "Quarry: Silver / Gold per Lucky", "clicker", "int", "10", "0", "1000", "", "", "live",
          "More Silver / Gold chance (1/1000) per Lucky finds level.", "reload@config.properties:click.mine.rareLuck"),
         ("click.mine.silverWeight", "Quarry: Silver weight by zone", "clicker", "text", ",".join(str(_x) for _x in MQ_SW), "", "60", "", "", "live",
          "5 numbers, Zone 1..5 (10 = x1): vanilla has the most Silver in zone 3.", "reload@config.properties:click.mine.silverWeight"),
         ("click.mine.goldWeight", "Quarry: Gold weight by zone", "clicker", "text", ",".join(str(_x) for _x in MQ_GW), "", "60", "", "", "live",
          "5 numbers, Zone 1..5 (10 = x1): vanilla has Gold in zones 1-3, most in zone 3.", "reload@config.properties:click.mine.goldWeight"),
         ("click.mine.luckMax", "Quarry: Lucky finds levels", "clicker", "int", "5", "0", "5", "", "", "live",
          "The highest Lucky finds level (each costs what Ore Amount costs at that level).", "reload@config.properties:click.mine.luckMax"),
         ("click.mine.refillSec", "Quarry: a node refills in", "clicker", "int", "10", "1", "3600", "", "s", "live",
          "Seconds before a broken node can be mined again (before Springs).", "reload@config.properties:click.mine.refillSec"),
         ("click.mine.springSec", "Quarry: Springs faster refill", "clicker", "int", "1", "0", "600", "", "s", "live",
          "Seconds less refill per Underground Springs level.", "reload@config.properties:click.mine.springSec"),
         ("click.mine.minRefillSec", "Quarry: shortest refill", "clicker", "int", "3", "0", "3600", "", "s", "live",
          "A node never refills faster than this.", "reload@config.properties:click.mine.minRefillSec"),
         ("click.mine.smithyHours", "Smithy II coins (curve hours)", "clicker", "text", "0.25", "", "20", "", "", "live",
          "Hours of the coin curve at the quarry's tier for Smithy II (the alloy slider).", "reload@config.properties:click.mine.smithyHours"),
         ("click.mine.smithyEnch", "Smithy II Enchanted bars", "clicker", "int", "16", "0", "100000", "", "", "live",
          "Enchanted bars of the quarry's ore Smithy II costs.", "reload@config.properties:click.mine.smithyEnch"),
         ("click.mine.alloyDefault", "Smithy II: alloy share at first", "clicker", "int", "50", "0", "100", "", "%", "live",
          "The alloy slider's value right after Smithy II is bought.", "reload@config.properties:click.mine.alloyDefault"),
         ("click.mine.alloyStep", "Smithy II: slider step", "clicker", "int", "10", "1", "100", "", "%", "live",
          "How much one - / + click moves the alloy slider.", "reload@config.properties:click.mine.alloyStep"),
         ("click.mine.zoneLevel", "Quarry zone opens at Mining level", "clicker", "text", ",".join(str(_x) for _x in MQ_ZLV), "", "60", "", "", "live",
          "5 numbers, Zone 1..5: Mining islands of a zone are bought from this Mining level.", "reload@config.properties:click.mine.zoneLevel")]
''')
P.rep(r'''          "  CK_ZLV = intsOf(p.getProperty(\"click.zoneLevel\"), DEF_CK_ZLV, 0, 1000, \"click.zoneLevel\");"]
''', r'''          "  CK_ZLV = intsOf(p.getProperty(\"click.zoneLevel\"), DEF_CK_ZLV, 0, 1000, \"click.zoneLevel\");"]
_load += ["  MQ_ON = bool(p.getProperty(\"click.mine.enabled\"), true);",   # 0.4.24 the Mining quarry
          "  MQ_HP = intOf(p.getProperty(\"click.mine.hp\"), 12, 1, 1000);",
          "  MQ_BLOCKS = intOf(p.getProperty(\"click.mine.blocks\"), 3, 1, 1000);",
          "  MQ_NS_PER = intOf(p.getProperty(\"click.mine.sizeBlocks\"), 1, 0, 100);",
          "  MQ_NS_MAX = intOf(p.getProperty(\"click.mine.sizeMax\"), 10, 0, 10);",
          "  MQ_ORE = intOf(p.getProperty(\"click.mine.orePercent\"), 40, 0, 100);",
          "  MQ_ORE_LUCK = intOf(p.getProperty(\"click.mine.oreLuck\"), 8, 0, 100);",
          "  MQ_RARE = intOf(p.getProperty(\"click.mine.rarePermille\"), 10, 0, 1000);",
          "  MQ_RARE_LUCK = intOf(p.getProperty(\"click.mine.rareLuck\"), 10, 0, 1000);",
          "  MQ_SW = intsOf(p.getProperty(\"click.mine.silverWeight\"), DEF_MQ_SW, 0, 1000, \"click.mine.silverWeight\");",
          "  MQ_GW = intsOf(p.getProperty(\"click.mine.goldWeight\"), DEF_MQ_GW, 0, 1000, \"click.mine.goldWeight\");",
          "  MQ_LUCK_MAX = intOf(p.getProperty(\"click.mine.luckMax\"), 5, 0, 5);",
          "  MQ_REFILL = intOf(p.getProperty(\"click.mine.refillSec\"), 10, 1, 3600);",
          "  MQ_SPRING = intOf(p.getProperty(\"click.mine.springSec\"), 1, 0, 600);",
          "  MQ_RMIN = intOf(p.getProperty(\"click.mine.minRefillSec\"), 3, 0, 3600);",
          "  { double[] smh = decsOf(p.getProperty(\"click.mine.smithyHours\"), new double[] { 0.25 }, 0.0, 1000.0, \"click.mine.smithyHours\"); MQ_SM_H = smh.length > 0 ? smh[0] : 0.25; }",
          "  MQ_SM_Q = intOf(p.getProperty(\"click.mine.smithyEnch\"), 16, 0, 100000);",
          "  MQ_ALLOY_DEF = intOf(p.getProperty(\"click.mine.alloyDefault\"), 50, 0, 100);",
          "  MQ_ALLOY_STEP = intOf(p.getProperty(\"click.mine.alloyStep\"), 10, 1, 100);",
          "  MQ_ZLV = intsOf(p.getProperty(\"click.mine.zoneLevel\"), DEF_MQ_ZLV, 0, 1000, \"click.mine.zoneLevel\");"]
''')

# ---------------------------------------------------------------------------------------------------- 2. ShIsl: Mining zone locks (by Mining level)
P.rep(r'''public static int zoneNeed(int kd, int t) {
  if (kd != @CKFK@) return 0;
  int[] a = @PKG@.ShCfg.CK_ZLV;
  int z = zoneOf(t);
  return a == null || z - 1 >= a.length ? 0 : a[z - 1];
}""".replace("@CKFK@", str(CK_FK)))''', r'''public static int zoneNeed(int kd, int t) {
  if (kd != @CKFK@ && kd != @MQK@) return 0;
  int[] a = kd == @MQK@ ? @PKG@.ShCfg.MQ_ZLV : @PKG@.ShCfg.CK_ZLV;   // 0.4.24: the Mining quarry zones by Mining level (Skyy "zone locks for all the shards")
  int z = zoneOf(t);
  return a == null || z - 1 >= a.length ? 0 : a[z - 1];
}""".replace("@CKFK@", str(CK_FK)).replace("@MQK@", str(MQ_K)))''')

# ---------------------------------------------------------------------------------------------------- 3. Collect: the collection credit of a smelted bar / an alloy = its ore(s)
P.rep(r'''# 0.4.23 THE CLICKED DROPS (<kind>.i<n>.drops of a non-Combat shard - what the clicker felled): the Collect pattern (debit + SAVE first, a refused save
''', r'''# 0.4.24 THE QUARRY'S BARS: the collection credit of a bar = its ore (as the Auto-Smelt Pole's Collect always credited), an alloy bar = its two
# ores half each (1 + 1 -> 2: every alloy bar stands for one ore); Silver / Gold bars = Silver / Gold Ore
MQ_ALLOYS = [("Ingredient_Bar_Bronze", "Ingredient_Bar_Copper", "Ingredient_Bar_Iron"),
             ("Ingredient_Bar_Dusk_SkyWynn", "Ingredient_Bar_Thorium", "Ingredient_Bar_Lead_SkyWynn"),
             ("Ingredient_Bar_Azurvane_SkyWynn", "Ingredient_Bar_Cobalt", "Ingredient_Bar_Chromium_SkyWynn"),
             ("Ingredient_Bar_Cinder_SkyWynn", "Ingredient_Bar_Adamantite", "Ingredient_Bar_Slag_SkyWynn"),
             ("Ingredient_Bar_Lumen_SkyWynn", "Ingredient_Bar_Mithril", "Ingredient_Bar_Titanium_SkyWynn")]   # SkyyWorldGen WG_ALLOYS, zone 1..5 (copied)
MQ_RARE = [("Ore_Silver", "Ingredient_Bar_Silver"), ("Ore_Gold", "Ingredient_Bar_Gold")]
for _a, _x, _y in MQ_ALLOYS:
    assert (_a in ITEMS or _a in WG48) and _x in [_t["smelt"] for _t in LAD[MQ_K]] and _y in [_t["smelt"] for _t in LAD[MQ_K]], (_a, _x, _y)
for _o, _b in MQ_RARE:
    assert _o in ITEMS and _b in ITEMS, (_o, _b)
for f in ("public static final String[] AL_ID = new String[] { %s };" % ", ".join(jlit(_a[0]) for _a in MQ_ALLOYS),
          "public static final String[] AL_A = new String[] { %s };" % ", ".join(jlit(_a[1]) for _a in MQ_ALLOYS),
          "public static final String[] AL_B = new String[] { %s };" % ", ".join(jlit(_a[2]) for _a in MQ_ALLOYS),
          "public static final String[] RB_ORE = new String[] { %s };" % ", ".join(jlit(_r[0]) for _r in MQ_RARE),
          "public static final String[] RB_BAR = new String[] { %s };" % ", ".join(jlit(_r[1]) for _r in MQ_RARE),
          "public static final java.util.concurrent.ConcurrentHashMap AL_PAR = new java.util.concurrent.ConcurrentHashMap();"):   # fix: <uuid>|<alloy> -> the alloy bars credited so far (memory)
    F(core, f)
M(core, r"""
public static String oreOfBar(String id) {
  if (id == null) return null;
  for (int t = 0; t < @PKG@.ShIsl.PROD.length; t++) if (@PKG@.ShIsl.SMELT[t].length() > 0 && id.equals(@PKG@.ShIsl.SMELT[t])) return @PKG@.ShIsl.PROD[t];
  for (int i = 0; i < RB_BAR.length; i++) if (id.equals(RB_BAR[i])) return RB_ORE[i];
  return null;
}""")
M(core, r"""
public static long owedAs(java.util.UUID u, String id, long c) {
  if (id == null || c <= 0L) return 0L;
  for (int i = 0; i < AL_ID.length; i++) {
    if (!id.equals(AL_ID[i])) continue;
    String a = oreOfBar(AL_A[i]);
    String b = oreOfBar(AL_B[i]);
    String pk = String.valueOf(u) + "|" + AL_ID[i];   // fix: the two ores take turns across Collects (one bar at a time credits A, B, A, B ...)
    java.util.concurrent.atomic.AtomicLong al = (java.util.concurrent.atomic.AtomicLong) AL_PAR.get(pk);
    if (al == null) { AL_PAR.putIfAbsent(pk, new java.util.concurrent.atomic.AtomicLong()); al = (java.util.concurrent.atomic.AtomicLong) AL_PAR.get(pk); }
    long st0 = al.getAndAdd(c);
    long ha = (st0 % 2L == 0L) ? (c + 1L) / 2L : c / 2L;
    long hb = c - ha;
    long r = 0L;
    if (a != null && ha > 0L) r += owed(u, a, ha);
    if (b != null && hb > 0L) r += owed(u, b, hb);
    return r;
  }
  String o = oreOfBar(id);
  return owed(u, o != null ? o : id, c);
}""")
# 0.4.23 THE CLICKED DROPS (<kind>.i<n>.drops of a non-Combat shard - what the clicker felled): the Collect pattern (debit + SAVE first, a refused save
''')
P.rep(r'''    long oc = owed(u, (String) en.getKey(), c);   // the collection credit, as Collect (no lock held)''',
      r'''    long oc = owedAs(u, (String) en.getKey(), c);   // the collection credit, as Collect (no lock held); 0.4.24: a bar = its ore, an alloy = its two ores''')

# ---------------------------------------------------------------------------------------------------- 4. ShClk: Fortune through SkyySkills (both clickers), the pickaxe, THE QUARRY
P.rep(r'''public static double bonusSum(java.util.UUID u, String key, String block) {
  if (u == null) return 0.0;''', r'''public static double bonusSumK(java.util.UUID u, String key, String block, String onlyKey) {   // 0.4.24: the only.<skill> key is a parameter
  if (u == null) return 0.0;''')
P.rep(r'''        Object on = m.get("only.foraging");
        if (on != null && !onlyHit(String.valueOf(on), block)) continue;''', r'''        Object on = m.get(onlyKey);
        if (on != null && !onlyHit(String.valueOf(on), block)) continue;''')
P.rep(r'''M(ckc, "public static double fortune(java.util.UUID u, String block) { return bonusSum(u, \"dd.foraging\", block); }")''', r'''M(ckc, "public static double bonusSum(java.util.UUID u, String key, String block) { return bonusSumK(u, key, block, \"only.foraging\"); }")
# 0.4.24 FORTUNE = SkyySkills' own number for that block (skill:fn:fortune, SkyySkills 0.4.72: "ok|<total>|<level part>|<bonus on>|<match>" - the level
# perk + every source + its caps + bridge.bonus.enabled + perk.only); no SkyySkills 0.4.72 = 0.4.23's own sum of the skill:bonus sources
F(ckc, "public static final java.util.concurrent.atomic.AtomicLong FORT_BR = new java.util.concurrent.atomic.AtomicLong();")
M(ckc, r"""
public static double fortuneOf(java.util.UUID u, String skill, String block, String ddKey, String onlyKey) {
  if (u == null) return 0.0;
  try {
    java.util.function.Function f = @PKG@.ShCfg.fn("skill:fn:fortune");
    if (f != null) {
      Object r = f.apply(new Object[] { u, skill, block });
      if (r instanceof String && ((String) r).startsWith("ok|")) {
        String[] a = ((String) r).split("\\|");
        if (a.length > 1) {
          double d = Double.parseDouble(a[1]);
          if (!Double.isNaN(d) && !Double.isInfinite(d)) { FORT_BR.incrementAndGet(); return d <= 0.0 ? 0.0 : (d > 100.0 ? 100.0 : d); }
        }
      }
    }
  } catch (Throwable x) { }
  return bonusSumK(u, ddKey, block, onlyKey);
}""")
M(ckc, "public static double fortune(java.util.UUID u, String block) { return fortuneOf(u, \"Foraging\", block, \"dd.foraging\", \"only.foraging\"); }")''')

QRY_CLK = r'''# ---- 0.4.24 THE MINING QUARRY (tools/shards_0_4_24_patch.py): ONE QUARRY PER ZONE = the zone's lowest owned Mining island (its storage, upgrades,
# totems); every owned Mining island of the zone adds its ore's nodes. A node = the 0.4.23 tree (damage, regrow, the click cap, the tier gate) with a
# pickaxe; it breaks into blocks: 1 cobble of the ore's host rock each + a chance of ore / Silver / Gold (Lucky finds), Fortune on the finds, the
# Smithy (Auto-Smelt Pole: bars 1 : 1; Smithy II: the alloy slider, SkyyWorldGen's 1 + 1 -> 2), into the base island's .drops (saved at once).
CK_PICKS = [(_i, int(_TT48.tier(_i))) for _i in sorted(_TT48.ROWS) if _i.startswith("Tool_Pickaxe_") and _TT48.tier(_i)]
assert ("Tool_Pickaxe_Copper", 1) in CK_PICKS and ("Tool_Pickaxe_Iron", 2) in CK_PICKS, CK_PICKS[:4]
MQ_LAD = LAD[MQ_K]
MQ_COB = {"Rock_Stone": "Rock_Stone_Cobble", "Rock_Sandstone": "Rock_Sandstone_Cobble", "Rock_Shale": "Rock_Shale_Cobble",
          "Rock_Magma_Cooled": "Rock_Magma_Cooled_Cobble", "Rock_Volcanic": "Rock_Volcanic_Cobble", "Rock_Basalt": "Rock_Basalt_Cobble"}   # vanilla Gathering drops
assert len(MQ_LAD) == 11 and all(_t["host"] in MQ_COB and MQ_COB[_t["host"]] in ITEMS and _t["res1"] and _t["smelt"] for _t in MQ_LAD)
assert [_a[1] for _a in MQ_ALLOYS] + [_a[2] for _a in MQ_ALLOYS] == [_t["smelt"] for _t in MQ_LAD if _t["key"] != "onyxium"][0::2] + [_t["smelt"] for _t in MQ_LAD if _t["key"] != "onyxium"][1::2], "the zone alloy pairs = the ladder's metals two by two"
MQ_ALLOY_OUT = 2   # SkyyWorldGen 0.7.5+ (Skyy 2026-10-18): "as many bars out as bars in - 1 Copper + 1 Iron = 2 Bronze"
for f in ("public static final int MK = %d;" % MQ_K, "public static final int ALLOY_OUT = %d;" % MQ_ALLOY_OUT,
          "public static final String[] PICK_ID = new String[] { %s };" % ", ".join(jlit(_a) for _a, _t in CK_PICKS),
          "public static final int[] PICK_T = new int[] { %s };" % ", ".join(str(_t) for _a, _t in CK_PICKS),
          "public static final String[] Q_BLOCK = new String[] { %s };" % ", ".join(jlit(_t["res1"]) for _t in MQ_LAD),
          "public static final String[] Q_ORE = new String[] { %s };" % ", ".join(jlit(_t["prod"]) for _t in MQ_LAD),
          "public static final String[] Q_BAR = new String[] { %s };" % ", ".join(jlit(_t["smelt"]) for _t in MQ_LAD),
          "public static final String[] Q_COB = new String[] { %s };" % ", ".join(jlit(MQ_COB[_t["host"]]) for _t in MQ_LAD),
          "public static final String[] QA_ID = new String[] { %s };" % ", ".join(jlit(_a[0]) for _a in MQ_ALLOYS),
          "public static final String[] QA_A = new String[] { %s };" % ", ".join(jlit(_a[1]) for _a in MQ_ALLOYS),
          "public static final String[] QA_B = new String[] { %s };" % ", ".join(jlit(_a[2]) for _a in MQ_ALLOYS),
          "public static final String[] R_ORE = new String[] { %s };" % ", ".join(jlit(_r[0]) for _r in MQ_RARE),
          "public static final String[] R_BAR = new String[] { %s };" % ", ".join(jlit(_r[1]) for _r in MQ_RARE),
          "public static volatile java.util.Random RND_TEST = null;",
          "public static final java.util.concurrent.ConcurrentHashMap ALLOYACC = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.atomic.AtomicLong MINED = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong ALLOYED = new java.util.concurrent.atomic.AtomicLong();"):
    F(ckc, f)
# the pickaxe's tier: tools/tier_tags.py's pickaxes; another id with "Pickaxe" / "Multitool" = the best metal word in it (else T1); 0 = not a pickaxe
M(ckc, r"""
public static int pickTier(String id) {
  if (id == null || id.length() == 0) return 0;
  for (int i = 0; i < PICK_ID.length; i++) if (PICK_ID[i].equals(id)) return PICK_T[i];
  if (id.indexOf("Pickaxe") < 0 && id.indexOf("Multitool") < 0) return 0;
  String[] w = id.split("_");
  int best = 0;
  for (int i = 0; i < w.length; i++) for (int j = 0; j < METAL_W.length; j++) if (METAL_W[j].equals(w[i]) && METAL_T[j] > best) best = METAL_T[j];
  return best > 0 ? best : 1;
}""")
M(ckc, r"""
public static double rnd() {
  java.util.Random r = RND_TEST;
  return r != null ? r.nextDouble() : Math.random();
}""")
# the Mining ladder types this profile owns in zone z, tier order (at most 3); under ShStore.LOCK
M(ckc, r"""
public static int[] zoneOwned(java.util.Properties p, int z) {
  int L0 = @PKG@.ShIsl.LAD0[MK];
  int LN = @PKG@.ShIsl.LADN[MK];
  int[] a = new int[3];
  int n = 0;
  for (int i = 0; i < LN; i++) {
    int t = L0 + i;
    if (@PKG@.ShIsl.zoneOf(t) != z || @PKG@.ShIsl.slotOf(MK, p, t) < 0) continue;
    if (n < 3) { a[n] = t; n++; }
  }
  int[] r = new int[n];
  for (int i = 0; i < n; i++) r[i] = a[i];
  return r;
}""")
M(ckc, r"""
public static int baseSlot(java.util.Properties p, int z) {
  int[] o = zoneOwned(p, z);
  return o.length == 0 ? -1 : @PKG@.ShIsl.slotOf(MK, p, o[0]);
}""")
M(ckc, "public static boolean isBase(java.util.Properties p, int kd, int slot) { return kd != MK || (slot >= 0 && baseSlot(p, @PKG@.ShIsl.zoneOf(@PKG@.ShIsl.ty(kd, p, slot))) == slot); }")   # fix: under ShStore.LOCK
M(ckc, "public static int luck(java.util.Properties p, int kd, int slot) { int m = @PKG@.ShCfg.MQ_LUCK_MAX; return @PKG@.ShStore.intv(p, @PKG@.ShMath.ik(kd, slot, \"luck\"), 0, 0, m < 0 ? 0 : (m > 5 ? 5 : m)); }")
M(ckc, "public static int smithy(java.util.Properties p, int kd, int slot) { return @PKG@.ShStore.intv(p, @PKG@.ShMath.ik(kd, slot, \"smithy\"), 0, 0, 1); }")
M(ckc, "public static int alloyPct(java.util.Properties p, int kd, int slot) { return @PKG@.ShStore.intv(p, @PKG@.ShMath.ik(kd, slot, \"alloyPct\"), @PKG@.ShCfg.MQ_ALLOY_DEF, 0, 100); }")
M(ckc, "public static long blocksAt(int ns) { return (long) @PKG@.ShCfg.MQ_BLOCKS + (long) ns * (long) @PKG@.ShCfg.MQ_NS_PER; }")
M(ckc, r"""
public static long refillMs(int spr) {
  long s = (long) @PKG@.ShCfg.MQ_REFILL - (long) @PKG@.ShCfg.MQ_SPRING * (long) (spr < 0 ? 0 : spr);
  if (s < (long) @PKG@.ShCfg.MQ_RMIN) s = (long) @PKG@.ShCfg.MQ_RMIN;
  return s < 0L ? 0L : s * 1000L;
}""")
M(ckc, r"""
public static double oreP(int lk) {
  double c = ((double) @PKG@.ShCfg.MQ_ORE + (double) @PKG@.ShCfg.MQ_ORE_LUCK * (double) (lk < 0 ? 0 : lk)) / 100.0;
  return c < 0.0 ? 0.0 : (c > 1.0 ? 1.0 : c);
}""")
M(ckc, r"""
public static double rareP(int lk, int z, boolean gold) {
  int[] w = gold ? @PKG@.ShCfg.MQ_GW : @PKG@.ShCfg.MQ_SW;
  int zi = z < 1 ? 0 : z - 1;
  double wt = w == null || w.length == 0 ? 0.0 : (double) w[zi < w.length ? zi : w.length - 1] / 10.0;
  double c = ((double) @PKG@.ShCfg.MQ_RARE + (double) @PKG@.ShCfg.MQ_RARE_LUCK * (double) (lk < 0 ? 0 : lk)) / 1000.0 * wt;
  return c < 0.0 ? 0.0 : (c > 1.0 ? 1.0 : c);
}""")
M(ckc, r"""
public static String qName(String id) {
  if (id == null) return "";
  if (id.startsWith("Rock_") && id.endsWith("_Cobble")) return id.substring(5, id.length() - 7).replace('_', ' ') + " Cobble";
  String s = @PKG@.ShTotem.pretty(id);
  int i = s.indexOf(" SkyWynn");
  return i >= 0 ? s.substring(0, i) + s.substring(i + 8) : s;
}""")
M(ckc, r"""
public static long heldOf(java.util.Map m, String id) {
  Object o = m.get(id);
  return o instanceof Long ? ((Long) o).longValue() : 0L;
}""")
M(ckc, r"""
public static void addTo(java.util.LinkedHashMap m, String id, long d) {
  if (id == null || id.length() == 0 || d == 0L) return;
  long v = heldOf(m, id) + d;
  if (v <= 0L) m.remove(id); else m.put(id, Long.valueOf(v));
}""")
# the alloy share: each new bar of the zone's two alloy metals adds pct / 200 of a pair (a pair = 2 bars -> pct % of the bars); whole pairs are made from
# the stock of BOTH metals (a = the first, b = the second, after the new bars); what found no partner is dropped (never a backlog). Memory per island.
M(ckc, r"""
public static synchronized double accGet(String key) {
  Object o = ALLOYACC.get(key);
  return o == null ? 0.0 : ((double[]) o)[0];
}""")
M(ckc, r"""
public static synchronized void accSet(String key, double v) {
  Object o = ALLOYACC.get(key);
  double[] a = o == null ? new double[1] : (double[]) o;
  if (o == null) ALLOYACC.put(key, a);
  a[0] = v < 0.0 ? 0.0 : v;
}""")
M(ckc, r"""
public static synchronized long alloyStep(String key, long nb, int pct, long a, long b) {
  if (nb <= 0L || pct <= 0) return 0L;
  double acc = accGet(key) + (double) nb * (double) (pct > 100 ? 100 : pct) / 200.0;
  long want = (long) Math.floor(acc + 0.000000001);
  long have = a < b ? a : b;
  long pairs = want < have ? want : have;
  if (pairs < 0L) pairs = 0L;
  acc = acc - (double) want;
  accSet(key, acc);
  return pairs;
}""")
M(ckc, r"""
public static void part(StringBuilder sb, long n, String id) {
  if (n <= 0L || id == null) return;
  if (sb.length() > 0) sb.append(", ");
  sb.append('+').append(@PKG@.ShCfg.num(n)).append(' ').append(qName(id));
}""")
# THE QUARRY CLICK (world thread; the bridges outside the store lock): Object[]{ status, pop text over the node }
M(ckc, r"""
public static Object[] mine(java.util.UUID u, String k, int kd, int slot, int spot, String hand) {
  if (!@PKG@.ShCfg.MQ_ON) return res("-The Mining quarry is switched off on this server.", "");
  int pt = pickTier(hand);
  if (pt <= 0) return res("-Hold a pickaxe - the quarry mines with the pickaxe in your hand.", "");
  long now = @PKG@.ShCore.now();
  if (!tick(u, now)) { CAPPED.incrementAndGet(); return res("", ""); }
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return res("-This shard's file could not be read.", "");
  String no = @PKG@.ShCore.gate(u, k, kd, p);
  if (no != null) return res(no, "");
  int z; int[] ores; int n; int spr; long use; long lim;
  @PKG@.ShStore.LOCK.lock(); try {
    if (slot < 0 || slot >= @PKG@.ShMath.SLOTS || !@PKG@.ShMath.hasIsland(kd, p, slot)) return res("-That island is not yours yet.", "");
    z = @PKG@.ShIsl.zoneOf(@PKG@.ShIsl.ty(kd, p, slot));
    ores = zoneOwned(p, z);
    if (ores.length == 0 || @PKG@.ShIsl.slotOf(kd, p, ores[0]) != slot) return res("=The page is up to date now.", "");
    n = @PKG@.ShIsl.treeN(@PKG@.ShMath.size(kd, p, slot), @PKG@.ShIsl.sub(p, kd, slot, 0));
    spr = @PKG@.ShIsl.sub(p, kd, slot, 2);
    @PKG@.ShMath.settle(kd, p, slot, now);
    use = @PKG@.ShMath.usedOf(kd, p, slot);
    lim = @PKG@.ShMath.limOf(kd, p, slot);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (spot < 0 || spot >= n || spot >= NSPOT) return res("=The page is up to date now.", "");
  if (use >= lim) return res("-This island's storage is full - Collect first.", "");
  int ot = ores[spot % ores.length];
  int oi = ot - @PKG@.ShIsl.LAD0[kd];
  String fam = Q_BLOCK[oi];
  double bps = bonusSumK(u, "bp.mining", (String) null, "only.mining");
  double f = fortuneOf(u, "Mining", fam, "dd.mining", "only.mining");
  String key = k + "|" + slot;
  double hpMax = (double) @PKG@.ShCfg.MQ_HP;
  int wt = @PKG@.ShIsl.TIER[ot];
  double dm = dmg(pt, wt, bps);
  if (!(dm > 0.0)) return res("-Your T" + pt + " pickaxe is too low a tier for T" + wt + " " + @PKG@.ShIsl.NAME[ot] + " - like in the world, a pickaxe mines at most 2 tiers above its own.", "");
  double left = hit(key, spot, dm, hpMax, now, refillMs(spr));
  CHOPS.incrementAndGet();
  if (left < 0.0) { long ms = (long) (-left - 1.0); return res("=That ore node is refilling - " + ((ms + 999L) / 1000L) + " s.", ""); }
  if (left > 0.0) return res("", @PKG@.ShCfg.dec(hpMax - left) + " / " + @PKG@.ShCfg.dec(hpMax));
  long gO; long gS; long gG; long gC; long base; long total; long pairs = 0L;
  String oreOut; String silOut; String golOut; String cobOut = Q_COB[oi]; String aId = ""; String aA = ""; String aB = "";
  @PKG@.ShStore.LOCK.lock(); try {
    if (!@PKG@.ShMath.hasIsland(kd, p, slot) || @PKG@.ShIsl.slotOf(kd, p, ot) < 0 || @PKG@.ShIsl.slotOf(kd, p, ores[0]) != slot) { unfell(key, spot, hpMax); return res("-That quarry changed meanwhile - the page is up to date now.", ""); }
    boolean sm = @PKG@.ShTotem.smelts(kd, p, slot);
    int lk = luck(p, kd, slot);
    long bl = blocksAt(nsize(p, kd, slot));
    double po = oreP(lk);
    double ps = rareP(lk, z, false);
    double pg = rareP(lk, z, true);
    long cob = 0L; long ore = 0L; long sil = 0L; long gol = 0L;
    base = 0L;
    for (long b = 0L; b < bl && b < 100000L; b++) {
      cob = cob + 1L;
      if (rnd() < po) { ore = ore + 1L + (long) extras(f, rnd()); base = base + 1L; }
      if (rnd() < ps) { sil = sil + 1L + (long) extras(f, rnd()); base = base + 1L; }
      if (rnd() < pg) { gol = gol + 1L + (long) extras(f, rnd()); base = base + 1L; }
    }
    oreOut = sm && Q_BAR[oi].length() > 0 ? Q_BAR[oi] : Q_ORE[oi];
    silOut = sm ? R_BAR[0] : R_ORE[0];
    golOut = sm ? R_BAR[1] : R_ORE[1];
    total = cob + ore + sil + gol;
    @PKG@.ShMath.settle(kd, p, slot, now);
    long room = @PKG@.ShMath.limOf(kd, p, slot) - @PKG@.ShMath.usedOf(kd, p, slot);
    if (room <= 0L) { unfell(key, spot, hpMax); return res("-This island's storage is full - Collect first.", ""); }
    gG = gol < room ? gol : room; room = room - gG;   // what fits: the good finds first, then the ore, then the stone
    gS = sil < room ? sil : room; room = room - gS;
    gO = ore < room ? ore : room; room = room - gO;
    gC = cob < room ? cob : room;
    String dk = @PKG@.ShMath.ik(kd, slot, "drops");
    String old = p.getProperty(dk);
    java.util.LinkedHashMap m = @PKG@.ShMath.held(kd, p, slot);
    addTo(m, golOut, gG);
    addTo(m, silOut, gS);
    addTo(m, oreOut, gO);
    addTo(m, cobOut, gC);
    double acc0 = accGet(key);
    int zi = z - 1;
    if (sm && smithy(p, kd, slot) >= 1 && gO > 0L && zi >= 0 && zi < QA_ID.length && (oreOut.equals(QA_A[zi]) || oreOut.equals(QA_B[zi]))) {
      pairs = alloyStep(key, gO, alloyPct(p, kd, slot), heldOf(m, QA_A[zi]), heldOf(m, QA_B[zi]));
      if (pairs > 0L) {
        aId = QA_ID[zi]; aA = QA_A[zi]; aB = QA_B[zi];
        addTo(m, aA, -pairs);
        addTo(m, aB, -pairs);
        addTo(m, aId, (long) ALLOY_OUT * pairs);
      }
    }
    @PKG@.ShMath.heldSet(kd, p, slot, m);
    String e = @PKG@.ShStore.save(k, p);
    if (e != null) {
      if (old == null) p.remove(dk); else p.setProperty(dk, old);
      accSet(key, acc0);
      unfell(key, spot, hpMax);
      @PKG@.ShCfg.warnOnce("qsave", "a mined node's blocks could not be saved (nothing added, the node stands again; logged once): " + e);
      return res("-The shard file could not be saved - nothing was added.", "");
    }
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  long got = gO + gS + gG + gC;
  FELLS.incrementAndGet();
  MINED.addAndGet(got);
  if (pairs > 0L) ALLOYED.addAndGet(pairs);
  long good = gO + gS + gG;
  long paid = good < base ? good : base;
  String skill = @PKG@.ShKind.SKILL[kd];
  long xp = accXp(String.valueOf(u) + "|" + @PKG@.ShCfg.pkey(u), (double) paid * (double) @PKG@.ShCfg.xpOf(kd) * (double) @PKG@.ShCfg.CK_XP_PCT / 100.0);
  String xt = "";
  if (xp > 0L) { long xl = @PKG@.ShCore.owedXp(u, skill, xp); xt = xl > 0L ? " (" + @PKG@.ShCfg.num(xl) + " " + skill + " XP waits)" : " +" + @PKG@.ShCfg.num(xp) + " " + skill + " XP"; }
  StringBuilder sb = new StringBuilder();
  part(sb, gO, oreOut);
  part(sb, gS, silOut);
  part(sb, gG, golOut);
  part(sb, gC, cobOut);
  String al = pairs > 0L ? " - Smithy: " + @PKG@.ShCfg.num(pairs) + " " + qName(aA) + " + " + @PKG@.ShCfg.num(pairs) + " " + qName(aB) + " -> " + @PKG@.ShCfg.num((long) ALLOY_OUT * pairs) + " " + qName(aId) : "";
  String fit = got < total ? " - the quarry's storage is full (" + @PKG@.ShCfg.num(total - got) + " did not fit)" : "";
  String r = "+Mined a " + @PKG@.ShIsl.tname(ot) + " node: " + sb.toString() + al + xt + fit + ".";
  String pop = gO > 0L ? "+" + @PKG@.ShCfg.num(gO) + " " + qName(oreOut) : (gS > 0L ? "+" + @PKG@.ShCfg.num(gS) + " " + qName(silOut) : (gG > 0L ? "+" + @PKG@.ShCfg.num(gG) + " " + qName(golOut) : "+" + @PKG@.ShCfg.num(gC) + " " + qName(cobOut)));
  @PKG@.ShSnd.ok(u, r, 0);
  return res(r, pop);
}""")
'''
P.rep(r'''# THE CLICK: Object[]{ status ("+..." / "-..." / "=..." / "" = nothing to say), pop text over the tree }. World thread; the bridges outside the store lock
''', QRY_CLK + r'''# THE CLICK: Object[]{ status ("+..." / "-..." / "=..." / "" = nothing to say), pop text over the tree }. World thread; the bridges outside the store lock
''')
P.rep(r'''  if (kd != FK) return res("-Only the Foraging Shard has a clicker so far.", "");''',
      r'''  if (kd == MK) return mine(u, k, kd, slot, spot, hand);   // 0.4.24: the Mining quarry
  if (kd != FK) return res("-Only the Foraging and Mining Shards have a clicker so far.", "");''')
# Vein size = the Tree size purchase on a Mining quarry (same costs), its own maximum and words
P.rep(r'''  if (!@PKG@.ShCfg.ON || !@PKG@.ShCfg.CK_ON) return "-The shard clicker is switched off on this server.";
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  String no = @PKG@.ShCore.gateOwn(u, k, kd, p);
  if (no != null) return no;
  int t0; int lv; long ver;''', r'''  if (!@PKG@.ShCfg.ON || !@PKG@.ShCfg.CK_ON) return "-The shard clicker is switched off on this server.";
  if (kd == MK && !@PKG@.ShCfg.MQ_ON) return "-The Mining quarry is switched off on this server.";   // 0.4.24
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  String no = @PKG@.ShCore.gateOwn(u, k, kd, p);
  if (no != null) return no;
  int t0; int lv; long ver;''')
P.rep(r'''  int mx = @PKG@.ShCfg.CK_NS_MAX;
  if (lv >= mx) return "=Tree size is at its highest level.";''', r'''  int mx = kd == MK ? @PKG@.ShCfg.MQ_NS_MAX : @PKG@.ShCfg.CK_NS_MAX;   // 0.4.24: Vein size on a Mining quarry
  if (lv >= mx) return kd == MK ? "=Vein size is at its highest level." : "=Tree size is at its highest level.";''')
P.rep(r'''  String ok = "+Tree size " + nl + "/" + mx + " on the " + @PKG@.ShIsl.tname(t0) + " island: " + logsAt(nl) + " logs a felled tree.";''',
      r'''  String ok = kd == MK ? "+Vein size " + nl + "/" + mx + " on the Zone " + @PKG@.ShIsl.zoneOf(t0) + " quarry: " + blocksAt(nl) + " blocks a mined node."
      : "+Tree size " + nl + "/" + mx + " on the " + @PKG@.ShIsl.tname(t0) + " island: " + logsAt(nl) + " logs a felled tree.";''')

QRY_BUY = r'''# ---- 0.4.24 the quarry's own purchases: Lucky finds (mining.i<n>.luck at the Ore Amount cost of that level), Smithy II (mining.i<n>.smithy + the
# slider's first value; needs the Auto-Smelt Pole = Smithy I), the alloy slider (- / +, free; a stale value refused)
M(ckc, r"""
public static String buyLuck(java.util.UUID u, String k, int kd, int slot, int seen, @IC@[] cs) {
  if (!@PKG@.ShCfg.ON || !@PKG@.ShCfg.CK_ON || !@PKG@.ShCfg.MQ_ON) return "-The Mining quarry is switched off on this server.";
  if (kd != MK) return "-Lucky finds is a Mining quarry upgrade.";
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  String no = @PKG@.ShCore.gateOwn(u, k, kd, p);
  if (no != null) return no;
  int t0; int lv; int sz; long ver;
  @PKG@.ShStore.LOCK.lock(); try {
    if (slot < 0 || slot >= @PKG@.ShMath.SLOTS || !@PKG@.ShMath.hasIsland(kd, p, slot)) return "-That island is not yours yet.";
    if (!isBase(p, kd, slot)) return "=The page is up to date now - open the quarry again.";   // fix: a stale slot (profile switch) never buys on a non-quarry island
    t0 = @PKG@.ShIsl.ty(kd, p, slot);
    lv = luck(p, kd, slot);
    sz = @PKG@.ShMath.size(kd, p, slot);
    ver = @PKG@.ShStore.ver(k);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (seen >= 0 && seen != lv) return "=The page is up to date now - click Upgrade again.";
  int mx = @PKG@.ShCfg.MQ_LUCK_MAX;
  if (lv >= mx) return "=Lucky finds is at its highest level.";
  double cv = @PKG@.ShCfg.curve(@PKG@.ShIsl.band(@PKG@.ShIsl.TIER[t0]));
  int nl = lv + 1;
  String r = @PKG@.ShCore.purchaseM(u, k, kd, p, cs, @PKG@.ShIsl.mats(kd, t0, @PKG@.ShCombat.subMat(kd, 0), sz - 1, (long) nl), @PKG@.ShIsl.coins(@PKG@.ShIsl.subH(sz, nl), cv),
                                    new String[] { @PKG@.ShMath.ik(kd, slot, "luck") }, new String[] { String.valueOf(nl) }, "luck",
                                    @PKG@.ShKind.KEYS[kd] + " luck slot " + slot + " " + @PKG@.ShIsl.KEY[t0] + " " + lv + " -> " + nl, ver);
  if (r != null) return r;
  int z = @PKG@.ShIsl.zoneOf(t0);
  String ok = "+Lucky finds " + nl + "/" + mx + " on the Zone " + z + " quarry: ore " + @PKG@.ShCfg.dec(oreP(nl) * 100.0) + " % a block, Silver "
      + @PKG@.ShCfg.dec(rareP(nl, z, false) * 100.0) + " %, Gold " + @PKG@.ShCfg.dec(rareP(nl, z, true) * 100.0) + " %.";
  @PKG@.ShSnd.ok(u, ok, 2);
  return ok;
}""")
M(ckc, r"""
public static long smithyCoins(double cv) { return @PKG@.ShIsl.coins(@PKG@.ShCfg.MQ_SM_H, cv); }""")
M(ckc, r"""
public static Object[] smithyMats(int kd, int t) { return @PKG@.ShIsl.mats(kd, t, "ench:" + (long) (@PKG@.ShCfg.MQ_SM_Q < 0 ? 0 : @PKG@.ShCfg.MQ_SM_Q), 0, 1L); }""")
M(ckc, r"""
public static String buySmithy(java.util.UUID u, String k, int kd, int slot, int seen, @IC@[] cs) {
  if (!@PKG@.ShCfg.ON || !@PKG@.ShCfg.CK_ON || !@PKG@.ShCfg.MQ_ON) return "-The Mining quarry is switched off on this server.";
  if (kd != MK) return "-The Smithy is a Mining quarry upgrade.";
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  String no = @PKG@.ShCore.gateOwn(u, k, kd, p);
  if (no != null) return no;
  int t0; int lv; boolean pole; long ver;
  @PKG@.ShStore.LOCK.lock(); try {
    if (slot < 0 || slot >= @PKG@.ShMath.SLOTS || !@PKG@.ShMath.hasIsland(kd, p, slot)) return "-That island is not yours yet.";
    if (!isBase(p, kd, slot)) return "=The page is up to date now - open the quarry again.";   // fix: a stale slot (profile switch) never buys on a non-quarry island
    t0 = @PKG@.ShIsl.ty(kd, p, slot);
    lv = smithy(p, kd, slot);
    pole = @PKG@.ShTotem.smelts(kd, p, slot);
    ver = @PKG@.ShStore.ver(k);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (seen >= 0 && seen != lv) return "=The page is up to date now - click Upgrade again.";
  if (lv >= 1) return "=Smithy II is built - move the alloy slider.";
  if (!pole) return "-Place an Auto-Smelt Pole on this quarry first (Totems tab) - the Smithy is built around it.";
  double cv = @PKG@.ShCfg.curve(@PKG@.ShIsl.band(@PKG@.ShIsl.TIER[t0]));
  int pc = @PKG@.ShCfg.MQ_ALLOY_DEF;
  String r = @PKG@.ShCore.purchaseM(u, k, kd, p, cs, smithyMats(kd, t0), smithyCoins(cv),
                                    new String[] { @PKG@.ShMath.ik(kd, slot, "smithy"), @PKG@.ShMath.ik(kd, slot, "alloyPct") }, new String[] { "1", String.valueOf(pc) }, "smithy",
                                    @PKG@.ShKind.KEYS[kd] + " smithy slot " + slot + " " + @PKG@.ShIsl.KEY[t0] + " 0 -> 1", ver);
  if (r != null) return r;
  int zi = @PKG@.ShIsl.zoneOf(t0) - 1;
  String an = zi >= 0 && zi < QA_ID.length ? qName(QA_ID[zi]) : "the alloy";
  String ok = "+Smithy II built: " + pc + " % of the new " + (zi >= 0 && zi < QA_ID.length ? qName(QA_A[zi]) + " and " + qName(QA_B[zi]) : "bars") + " become " + an + " (1 + 1 -> 2).";
  @PKG@.ShSnd.ok(u, ok, 2);
  return ok;
}""")
M(ckc, r"""
public static String setAlloy(java.util.UUID u, String k, int kd, int slot, int seen, int dir) {
  if (!@PKG@.ShCfg.ON || !@PKG@.ShCfg.CK_ON || !@PKG@.ShCfg.MQ_ON) return "-The Mining quarry is switched off on this server.";
  if (kd != MK) return "";
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  String no = @PKG@.ShCore.gateOwn(u, k, kd, p);
  if (no != null) return no;
  int nv;
  @PKG@.ShStore.LOCK.lock(); try {
    if (slot < 0 || slot >= @PKG@.ShMath.SLOTS || !@PKG@.ShMath.hasIsland(kd, p, slot)) return "-That island is not yours yet.";
    if (!isBase(p, kd, slot)) return "=The page is up to date now - open the quarry again.";   // fix: a stale slot (profile switch) never buys on a non-quarry island
    if (smithy(p, kd, slot) < 1) return "-Build Smithy II first - it adds the alloy slider.";
    int cur = alloyPct(p, kd, slot);
    if (seen != cur) return "=The page is up to date now.";
    int st = @PKG@.ShCfg.MQ_ALLOY_STEP < 1 ? 1 : @PKG@.ShCfg.MQ_ALLOY_STEP;
    nv = cur + (dir < 0 ? -st : st);
    if (nv < 0) nv = 0;
    if (nv > 100) nv = 100;
    if (nv == cur) return dir < 0 ? "=The alloy share is at 0 %." : "=The alloy share is at 100 %.";
    String ak = @PKG@.ShMath.ik(kd, slot, "alloyPct");
    String old = p.getProperty(ak);
    p.setProperty(ak, String.valueOf(nv));
    String e = @PKG@.ShStore.save(k, p);
    if (e != null) {
      if (old == null) p.remove(ak); else p.setProperty(ak, old);
      @PKG@.ShCfg.warnOnce("qalloy", "the alloy slider could not be saved (unchanged; logged once): " + e);
      return "-The shard file could not be saved - the slider is unchanged.";
    }
    @PKG@.ShStore.log(u + " " + k + " " + @PKG@.ShKind.KEYS[kd] + " alloyPct slot " + slot + " " + cur + " -> " + nv);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  return "+Alloy share " + nv + " %.";
}""")

'''
P.rep(r'''# ---- THE ART (our own drawings; CLK_ART_SRC above): drawn now, shipped as Common/UI/Custom/SkyyShards/Map/Clk<Name>@2x.png, registered map textures
''', QRY_BUY + r'''# ---- THE ART (our own drawings; CLK_ART_SRC above): drawn now, shipped as Common/UI/Custom/SkyyShards/Map/Clk<Name>@2x.png, registered map textures
''')

# ---------------------------------------------------------------------------------------------------- 5. the quarry's art (pure Python, appended to CLK_ART_SRC)
QART_SRC = r'''# 0.4.24 THE MINING QUARRY ART (tools/shards_0_4_24_patch.py): quarry islands (stone terraces), ore nodes + rubble per ore (host rock + ore flecks),
# map quarries, springs, smithy, upgrade icons. Our own geometry; QART(ores, sizes) -> {name: Pic}; ores = [(name, host, ore colour)] by ladder rank.
ROCK = {"Rock_Stone": ("#8e9198", "#d4d8e0", "#474a52"), "Rock_Sandstone": ("#d2ae74", "#f8e0b0", "#86663a"),  # ui-data (picture colours)
        "Rock_Shale": ("#5f6975", "#a6b0bd", "#2c323a"), "Rock_Magma_Cooled": ("#4d3c38", "#8c6c62", "#201614"),  # ui-data (picture colours)
        "Rock_Volcanic": ("#3e3739", "#7c7274", "#191517"), "Rock_Basalt": ("#4d535d", "#8e96a4", "#21252d")}  # ui-data (picture colours)


def _boulder(pic, cx, by, rx, ry, host, seed, ns=0.16):
    b, l, d = ROCK[host]
    pts = []
    for i in range(14):
        a = _m.pi + i * _m.pi / 13.0
        j = 0.86 + 0.26 * _hash(i, 3, seed)
        pts.append((cx + _m.cos(a) * rx * j, by - 2 + _m.sin(a) * ry * j * (1.0 if _m.sin(a) < 0 else 0.15)))
    ellipse(pic, cx + rx * 0.12, by + ry * 0.06, rx * 1.05, ry * 0.22, (10, 20, 12), 0.38)
    poly(pic, [(p[0] + rx * 0.06, p[1] + ry * 0.06) for p in pts], _rgb(d), 0.7)
    poly(pic, pts, shade(b, l, d, cx - rx * 0.2, by - ry * 0.6, max(rx, ry) * 1.1, ns=ns, nsc=max(2.0, rx / 5.0), seed=seed))
    for i in range(4):
        x0 = cx + (_hash(i, 5, seed) - 0.5) * rx * 1.2
        y0 = by - ry * (0.25 + 0.6 * _hash(i, 6, seed))
        line(pic, x0, y0, x0 + (_hash(i, 7, seed) - 0.5) * rx * 0.5, y0 + ry * 0.22, max(1.0, rx * 0.035), _rgb(d), 0.55)
    return pts


def _flecks(pic, cx, by, rx, ry, col, n, seed, sz):
    c = _rgb(col)
    hi = _mix(c, (255, 255, 255), 0.55)
    dk = _mix(c, (0, 0, 0), 0.45)
    for i in range(n):
        a = _hash(i, 11, seed) * _m.pi + _m.pi
        d = 0.15 + 0.62 * _m.sqrt(_hash(i, 12, seed))
        x, y = cx + _m.cos(a) * rx * d, by - ry * 0.12 + _m.sin(a) * ry * d * 0.95
        s = sz * (0.7 + 0.6 * _hash(i, 13, seed))
        poly(pic, [(x, y - s * 1.2), (x + s, y), (x, y + s * 0.9), (x - s, y)], _cl(dk))
        poly(pic, [(x, y - s * 1.05), (x + s * 0.82, y - s * 0.05), (x, y + s * 0.6), (x - s * 0.82, y - s * 0.05)], shade(c, hi, dk, x - s * 0.3, y - s * 0.4, s * 1.4))
        disc(pic, x - s * 0.3, y - s * 0.5, s * 0.22, (255, 255, 255), 0.8)


def qnode(host, col, W=110, H=140, s=2, seed=1):
    w, h = int(W * s), int(H * s)
    pic = Pic(w, h)
    cx, by = w / 2.0, h - 10.0 * s
    _boulder(pic, cx + 18 * s, by, 18 * s, 22 * s, host, seed + 7)
    _flecks(pic, cx + 18 * s, by, 15 * s, 20 * s, col, 3, seed + 7, 2.6 * s)
    _boulder(pic, cx - 6 * s, by, 36 * s, 50 * s, host, seed)
    _flecks(pic, cx - 6 * s, by, 31 * s, 46 * s, col, 9, seed, 4.2 * s)
    for i in range(5):
        x = cx + (_hash(i, 21, seed) - 0.5) * 70 * s
        ellipse(pic, x, by + 1 * s, (2 + 3 * _hash(i, 22, seed)) * s, 1.8 * s, _rgb(ROCK[host][2]), 0.85)
    return pic


def qrubble(host, col, W=110, H=140, s=2, seed=1):
    w, h = int(W * s), int(H * s)
    pic = Pic(w, h)
    cx, by = w / 2.0, h - 10.0 * s
    for i, (dx, rx, ry) in enumerate(((-20, 14, 10), (14, 16, 11), (-2, 12, 14), (26, 9, 7), (-32, 8, 6))):
        _boulder(pic, cx + dx * s, by + (i % 2) * 2 * s, rx * s, ry * s, host, seed + 31 * i, ns=0.2)
    _flecks(pic, cx - 2 * s, by, 10 * s, 12 * s, col, 2, seed + 3, 2.0 * s)
    for i in range(9):
        disc(pic, cx + (_hash(i, 41, seed) - 0.5) * 80 * s, by - _hash(i, 42, seed) * 4 * s, (1.0 + 1.4 * _hash(i, 43, seed)) * s, _rgb(ROCK[host][1]), 0.7)
    return pic


def quarry(W, H, s=1, seed=1, host="Rock_Stone"):
    pic = island(W, H, s, seed=seed + 40, hue="#7f9a52")  # ui-data (picture colours)
    w, h = pic.w, pic.h
    cx, cy = w / 2.0, h * 0.34
    rx, ry = w * 0.47, w * 0.47 * 0.36
    b, l, d = ROCK[host]
    ellipse(pic, cx, cy + ry * 0.02, rx * 0.95, ry * 0.92, shade(b, l, d, cx - rx * 0.3, cy - ry * 0.4, rx, ns=0.14, nsc=7 * s, seed=seed))
    for k in range(1, 4):
        f = 1.0 - 0.21 * k
        c0 = _mix(_rgb(b), _rgb(d), 0.16 * k)
        ellipse(pic, cx + rx * 0.03 * k, cy + ry * 0.07 * k + ry * 0.05, rx * 0.95 * f + 2 * s, ry * 0.92 * f + 2 * s, _rgb(l), 0.35)
        ellipse(pic, cx + rx * 0.03 * k, cy + ry * 0.07 * k + ry * 0.08, rx * 0.95 * f, ry * 0.92 * f, shade(_cl(c0), l, d, cx - rx * 0.2, cy, rx * f, ns=0.12, nsc=6 * s, seed=seed + k))
    ellipse(pic, cx + rx * 0.12, cy + ry * 0.3, rx * 0.2, ry * 0.16, _rgb(d), 0.55)
    for i in range(int(60 * w / 700.0)):
        a = _hash(i, 51, seed) * 2 * _m.pi
        dd = 0.2 + 0.75 * _m.sqrt(_hash(i, 52, seed))
        disc(pic, cx + _m.cos(a) * rx * dd * 0.95, cy + _m.sin(a) * ry * dd * 0.9, (0.8 + 1.4 * _hash(i, 53, seed)) * s, _rgb(l if i % 3 else d), 0.7)
    for i in range(3):
        x0 = cx - rx * 0.62 + i * rx * 0.55
        line(pic, x0, cy - ry * 0.55 + i * 3 * s, x0 + rx * 0.3, cy - ry * 0.58 + i * 3 * s, 1.6 * s, _rgb("#6a4a2a"), 0.9)  # ui-data (picture colours)
    return pic


def qspring(W=60, H=44, s=2):
    w, h = int(W * s), int(H * s)
    pic = Pic(w, h)
    cx, cy = w / 2.0, h * 0.62
    for i in range(12):
        a = i * 2 * _m.pi / 12
        _boulder(pic, cx + _m.cos(a) * w * 0.4, cy + _m.sin(a) * h * 0.26 + 4 * s, 6 * s, 5 * s, "Rock_Stone", 70 + i, ns=0.1)
    ellipse(pic, cx, cy, w * 0.36, h * 0.24, vgrad("#2f7fd0", "#9ad6ff", cy - h * 0.24, cy + h * 0.24))  # ui-data (picture colours)
    ellipse(pic, cx - w * 0.1, cy - h * 0.06, w * 0.12, h * 0.05, _rgb("#e8f6ff"), 0.75)  # ui-data (picture colours)
    for i in range(5):
        disc(pic, cx + (_hash(i, 61, 3) - 0.5) * w * 0.4, cy - h * (0.2 + 0.5 * _hash(i, 62, 3)), (1.4 + 1.6 * _hash(i, 63, 3)) * s, _rgb("#cfeeff"), 0.85)  # ui-data (picture colours)
    return pic


def qsmithy(W=72, H=64, s=2):
    w, h = int(W * s), int(H * s)
    pic = Pic(w, h)
    by = h - 6 * s
    ellipse(pic, w * 0.5, by + 2 * s, w * 0.46, 5 * s, (10, 20, 12), 0.38)
    fx = w * 0.32
    poly(pic, [(fx - 20 * s, by), (fx - 18 * s, by - 46 * s), (fx + 18 * s, by - 46 * s), (fx + 20 * s, by)], shade("#7a6a62", "#c8b8a8", "#3a302a", fx - 8 * s, by - 30 * s, 26 * s, ns=0.12, nsc=3 * s, seed=4))  # ui-data (picture colours)
    poly(pic, [(fx - 9 * s, by - 46 * s), (fx - 7 * s, by - 58 * s), (fx + 7 * s, by - 58 * s), (fx + 9 * s, by - 46 * s)], _rgb("#5a4c46"))  # ui-data (picture colours)
    ellipse(pic, fx, by - 14 * s, 10 * s, 9 * s, _rgb("#2a1a12"))  # ui-data (picture colours)
    ellipse(pic, fx, by - 13 * s, 8 * s, 6.5 * s, vgrad("#ffe27a", "#ff6a1a", by - 20 * s, by - 7 * s))  # ui-data (picture colours)
    disc(pic, fx, by - 16 * s, 14 * s, _rgb("#ff9a3a"), 0.18)  # ui-data (picture colours)
    ax = w * 0.72
    poly(pic, [(ax - 6 * s, by), (ax - 4 * s, by - 12 * s), (ax + 4 * s, by - 12 * s), (ax + 6 * s, by)], _rgb("#3a3e46"))  # ui-data (picture colours)
    poly(pic, [(ax - 16 * s, by - 12 * s), (ax + 14 * s, by - 12 * s), (ax + 18 * s, by - 18 * s), (ax - 10 * s, by - 20 * s), (ax - 18 * s, by - 17 * s)],
         shade("#5c626e", "#c8d0dc", "#22262e", ax - 6 * s, by - 18 * s, 18 * s))  # ui-data (picture colours)
    for i, c in enumerate(("#e6a04a", "#c8c8d0")):  # ui-data (picture colours)
        poly(pic, [(ax - 12 * s + i * 6 * s, by - 21 * s), (ax - 2 * s + i * 6 * s, by - 21 * s), (ax + i * 6 * s, by - 25 * s), (ax - 10 * s + i * 6 * s, by - 25 * s)], _rgb(c))
    return pic


def qmini(host, col, tier, W=150, H=100, s=2):
    w, h = int(W * s), int(H * s)
    base = Pic(w, h)
    top = int(h * 0.30)
    paste(base, quarry(W, int(H * 0.70), s, seed=tier, host=host), 0, top, 1.0)
    nd = qnode(host, col, 110, 140, s=1, seed=tier)
    gy = top + h * 0.70 * 0.34
    for fx, dy, sc in ((0.30, -0.06, 0.30), (0.70, -0.06, 0.30), (0.5, 0.08, 0.36)):
        paste(base, nd, int(w * fx - 110 * sc * s / 2.0), int(gy + dy * h * 0.70 - (140 - 10) * sc * s), sc * s)
    return base


def qicon(kind, col="#d8823a", s=2):  # ui-data (picture colours)
    W = 56
    p = Pic(int(W * s), int(W * s))
    if kind == "vein":
        paste(p, qnode("Rock_Stone", col, 110, 140, s=1, seed=5), int(-2 * s), int(-8 * s), 0.46 * s)
        disc(p, 44 * s, 42 * s, 9 * s, _rgb("#4fd88a"))  # ui-data (picture colours)
        line(p, 44 * s, 37 * s, 44 * s, 47 * s, 3 * s, _rgb("#0b1322"))  # ui-data (picture colours)
        line(p, 39 * s, 42 * s, 49 * s, 42 * s, 3 * s, _rgb("#0b1322"))  # ui-data (picture colours)
    elif kind == "nodes":
        nd = qnode("Rock_Stone", col, 110, 140, s=1, seed=6)
        for ox, oy, sc in ((-10, -2, 0.32), (20, -4, 0.32), (5, 8, 0.36)):
            paste(p, nd, int(ox * s), int(oy * s), sc * s)
    elif kind == "spring":
        paste(p, qspring(60, 44, s=1), int(-2 * s), int(10 * s), 0.98 * s)
    elif kind == "luck":
        for i, (x, y, c) in enumerate(((18, 34, "#e0e4ea"), (34, 30, "#f2c94c"), (26, 42, "#f2c94c"))):  # ui-data (picture colours)
            poly(p, [(x * s, (y - 8) * s), ((x + 7) * s, y * s), (x * s, (y + 6) * s), ((x - 7) * s, y * s)], shade(c, "#ffffff", "#6a5a2a", (x - 2) * s, (y - 3) * s, 8 * s))  # ui-data (picture colours)
        for x, y, r in ((40, 14, 3.0), (12, 18, 2.2), (46, 40, 2.0)):
            line(p, (x - r * 2) * s, y * s, (x + r * 2) * s, y * s, 1.4 * s, _rgb("#fff4b0"))  # ui-data (picture colours)
            line(p, x * s, (y - r * 2) * s, x * s, (y + r * 2) * s, 1.4 * s, _rgb("#fff4b0"))  # ui-data (picture colours)
    else:
        paste(p, qsmithy(72, 64, s=1), int(-6 * s), int(-4 * s), 0.86 * s)
    return p


def QART(ores, sizes):
    out = {}
    for sz, (W, H) in sorted(sizes.items()):
        out["QIsl%d" % sz] = quarry(W, H, 1, seed=sz)
    for i, (nm, host, col) in enumerate(ores):
        out["QNode%d" % i] = qnode(host, col, 110, 140, s=2, seed=11 + i)
        out["QRub%d" % i] = qrubble(host, col, 110, 140, s=2, seed=11 + i)
        out["QMap%d" % i] = qmini(host, col, i + 1, 150, 100, s=2)
    out["QSpring"] = qspring(60, 44, s=2)
    out["QSmithy"] = qsmithy(72, 64, s=2)
    for k in ("vein", "nodes", "spring", "luck", "smithy"):
        out["UpQ" + k.capitalize()] = qicon(k, s=2)
    return out


'''
P.rep('''def ART(tiers, sizes):
    # every picture of the clicker: {name: Pic}.''', QART_SRC + '''def ART(tiers, sizes):
    # every picture of the clicker: {name: Pic}.''')
P.rep(r'''print("0.4.23 clicker art: %d pictures drawn in %.1f s (%d KB)" % (len(_ck_pics), _time423.time() - _ck_t0,
      sum(len(MAP_ASSETS[MJAR + MDIR + "Clk" + _n + "@2x.png"]) for _n in _ck_pics) // 1024))
del _ck_pics
''', r'''print("0.4.23 clicker art: %d pictures drawn in %.1f s (%d KB)" % (len(_ck_pics), _time423.time() - _ck_t0,
      sum(len(MAP_ASSETS[MJAR + MDIR + "Clk" + _n + "@2x.png"]) for _n in _ck_pics) // 1024))
del _ck_pics
# 0.4.24 THE QUARRY'S PICTURES: one node / rubble / map quarry per Mining ore (its host rock + our ore colour), 3 quarry islands, springs, smithy, icons
MQ_ORE_COL = {"copper": "#d8823a", "iron": "#d6b8a8", "thorium": "#86d86a", "lead": "#8f9ab4", "cobalt": "#3f7ce0", "chromium": "#cfe0ee",  # ui-data (picture colours)
              "adamantite": "#e0443a", "slag": "#c0702c", "mithril": "#72e2e0", "titanium": "#eeeef6", "onyxium": "#7a44b0"}  # ui-data (picture colours)
assert sorted(MQ_ORE_COL) == sorted(_t["key"] for _t in MQ_LAD)
_q_t0 = _time423.time()
_q_pics = CLK_ART["QART"]([(_t["name"], _t["host"], MQ_ORE_COL[_t["key"]]) for _t in MQ_LAD], CK_ISL)
for _n, _pic in sorted(_q_pics.items()):
    assert re.fullmatch(r"[A-Za-z0-9]+", _n) and _n not in CK_TEX, _n
    CK_TEX[_n] = MDIR + "Clk" + _n + ".png"
    SUI.register_map_textures([CK_TEX[_n]])
    MAP_ASSETS[MJAR + MDIR + "Clk" + _n + "@2x.png"] = _pic.png()
print("0.4.24 quarry art: %d pictures drawn in %.1f s (%d KB)" % (len(_q_pics), _time423.time() - _q_t0,
      sum(len(MAP_ASSETS[MJAR + MDIR + "Clk" + _n + "@2x.png"]) for _n in _q_pics) // 1024))
MQ_NPIC = len(_q_pics)
del _q_pics
''')

# ---------------------------------------------------------------------------------------------------- 6. the quarry's page parts (segments + run-time Java)
QRY_PAGE = r'''# ---- 0.4.24 THE QUARRY PAGE PARTS (Mining): the quarry island pictures, springs + smithy on it, the eight upgrade rows (compact: the button on the right,
# the Smithy row's - / + alloy slider), the quarry map (5 zones of their 2-3 ores; the cards keep the 0.4.23 ids M<3 x zone + n>)
CK_PAGE_STATIC += ["public static final String[] Q_NODE = new String[] { %s };" % ", ".join(jlit(CK_TEX["QNode%d" % _i]) for _i in range(len(MQ_LAD))),
                   "public static final String[] Q_RUB = new String[] { %s };" % ", ".join(jlit(CK_TEX["QRub%d" % _i]) for _i in range(len(MQ_LAD)))]
MQ_ZT = [[_i for _i, _t in enumerate(MQ_LAD) if min(5, (_t["tier"] - 1) // 3 + 1) == _z] for _z in range(1, 6)]   # = ShIsl.zoneOf (3 tiers a zone, capped at 5)
assert [len(_x) for _x in MQ_ZT] == [2, 2, 2, 2, 3] and sum(MQ_ZT, []) == list(range(len(MQ_LAD))), MQ_ZT
MQ_CARD = [-1] * 15
for _z, _ids in enumerate(MQ_ZT):
    for _q, _li in enumerate(_ids):
        MQ_CARD[3 * _z + _q] = _li
CK_PAGE_STATIC.append("public static final int[] QCARD = new int[] { %s };" % ", ".join(str(_c) for _c in MQ_CARD))
for _s in (1, 2, 3):
    lay = CK_LAY[_s]
    a_ = _ck_seg("qisl%d" % _s)
    a_.append((CK_SCN, SUI.map_pic(CKP + "Isl", lay["L"], lay["T"], lay["W"], lay["H"], CK_TEX["QIsl%d" % _s])))
    a_ = _ck_seg("qsp%d" % _s)
    _l, _t = _ck_bot("QSpring", 60, 44, lay["wx"])
    a_.append((CK_SCN, SUI.map_pic(CKP + "Wx", _l, _t, 60, 44, CK_TEX["QSpring"])))
    a_ = _ck_seg("qsm%d" % _s)
    _sx = (int(round(lay["cx"] - (lay["wx"][0] - lay["cx"]))), lay["wx"][1] + 6)
    _l, _t = _ck_bot("QSmithy", 72, 64, _sx)
    a_.append((CK_SCN, SUI.map_pic(CKP + "Sm", _l, _t, 72, 64, CK_TEX["QSmithy"])))
# the eight upgrade rows (Mining)
Q_ROWS, Q_ROW_H = 8, 84
Q_UP_NAMES = ["Vein size", "Ore nodes", "Miner spirits", "Springs", "Island size", "Decorations", "Lucky finds", "Smithy"]
Q_UP_ICON = ["UpQVein", "UpQNodes", "UpSpirit", "UpQSpring", "UpIsize", "UpDeco", "UpQLuck", "UpQSmithy"]
Q_UP_BTN = ["Upgrade", "Upgrade", "Totems", "Upgrade", "Upgrade", "Upgrade", "Upgrade", "Upgrade"]
Q_BW = 150
Q_TXT_W = CK_UIW - 12 - 64 - 8 - 6 - Q_BW
assert Q_TXT_W >= 240, Q_TXT_W
a_ = _ck_seg("qup")
a_.append((CK_BODY, G_.glass_group(CKP + "Up", CK_UPW, CK_BODY_H, role="panel", layout="Top", pad=12, anchor={"left": 12})))
a_.append((CK_UP, G_.glass_group(CKP + "UpH", CK_UIW, 32, layout="Left")))
a_.append(("#" + CKP + "UpH", _ck_glab(CKP + "UpT", 18, "gold", 150, 32, bold=True, text="UPGRADES")))
a_.append(("#" + CKP + "UpH", _ck_glab(CKP + "UpCap", 13, "dim", CK_UIW - 150, 32, halign="End")))
for _r in range(Q_ROWS):
    R_ = CKP + "Q%d" % _r
    a_.append((CK_UP, G_.glass_group(R_, CK_UIW, Q_ROW_H, role="inset", layout="Left", pad=6, anchor={"top": 5})))
    a_.append(("#" + R_, "Group #%sI { Anchor: (Width: 64, Height: %d); }" % (R_, Q_ROW_H - 12)))
    a_.append(("#" + R_ + "I", SUI.map_pic(R_ + "P", 4, 8, 56, 56, CK_TEX[Q_UP_ICON[_r]])))
    a_.append(("#" + R_, G_.glass_group(R_ + "T", Q_TXT_W, Q_ROW_H - 12, layout="Top", anchor={"left": 8})))
    a_.append(("#" + R_ + "T", G_.glass_group(R_ + "N", Q_TXT_W, 26, layout="Left")))
    a_.append(("#" + R_ + "N", _ck_glab(R_ + "Nm", 16, "title", 130, 26, bold=True, text=Q_UP_NAMES[_r])))
    a_.append(("#" + R_ + "N", _ck_glab(R_ + "L", 14, "xp", Q_TXT_W - 130, 26, bold=True, halign="End")))
    a_.append(("#" + R_ + "T", _ck_glab(R_ + "E", 13, "text", Q_TXT_W, 22)))
    a_.append(("#" + R_ + "T", _ck_glab(R_ + "C", 13, "goldHi", Q_TXT_W, 22)))
    a_.append(("#" + R_, G_.glass_group(R_ + "B", Q_BW, Q_ROW_H - 12, layout="Top", anchor={"left": 6})))
    b_ = _ck_seg("qon%d" % _r)
    b_.append(("#" + R_ + "B", G_.glass_button(R_ + "X", Q_UP_BTN[_r], "secondary", w=Q_BW, h=32, anchor={"top": 18})))
    b_ = _ck_seg("qoff%d" % _r)
    b_.append(("#" + R_ + "B", G_.glass_button(R_ + "X", Q_UP_BTN[_r], "secondary", w=Q_BW, h=32, disabled=True, anchor={"top": 18})))
b_ = _ck_seg("qtot7")
b_.append(("#" + CKP + "Q7B", G_.glass_button(CKP + "Q7X", "Totems", "secondary", w=Q_BW, h=32, anchor={"top": 18})))
b_ = _ck_seg("qsl")
b_.append(("#" + CKP + "Q7B", G_.glass_group(CKP + "Q7S", Q_BW, 32, layout="Left", anchor={"top": 18})))
b_.append(("#" + CKP + "Q7S", G_.glass_button(CKP + "Q7M", "<", "secondary", w=44, h=32, size=18)))
b_.append(("#" + CKP + "Q7S", _ck_glab(CKP + "Q7V", 15, "goldHi", Q_BW - 88, 32, bold=True, halign="Center")))
b_.append(("#" + CKP + "Q7S", G_.glass_button(CKP + "Q7U", ">", "secondary", w=44, h=32, size=18)))
assert 32 + Q_ROWS * (Q_ROW_H + 5) <= CK_BODY_H - 24, "the eight quarry rows fit the panel"
# the quarry map: five zone panels with their ores' cards
a_ = _ck_seg("qmap")
a_.append((CK_BODY, G_.glass_group(CKP + "Map", CK_IW, CK_BODY_H, layout="Left")))
for _z in range(5):
    Z_ = CKP + "Z%d" % _z
    a_.append(("#" + CKP + "Map", G_.glass_group(Z_, CK_ZW, CK_BODY_H, role="panel", layout="Top", pad=10, anchor={"right": 13} if _z < 4 else None)))
    a_.append(("#" + Z_, _ck_glab(Z_ + "N", 18, "gold", CK_CW, 30, bold=True, text="ZONE %d QUARRY" % (_z + 1))))
    a_.append(("#" + Z_, _ck_glab(Z_ + "S", 14, "dim", CK_CW, 24)))
    for _q, _li in enumerate(MQ_ZT[_z]):
        M_ = CKP + "M%d" % (3 * _z + _q)
        a_.append(("#" + Z_, G_.glass_group(M_, CK_CW, CK_CARD_H, role="inset", layout="Top", pad=6, anchor={"top": 6})))
        a_.append(("#" + M_, "Group #%sG { Anchor: (Width: %d, Height: 140); }" % (M_, CK_CW - 12)))
        a_.append(("#" + M_ + "G", SUI.map_pic(M_ + "P", (CK_CW - 12 - 210) // 2, 0, 210, 140, CK_TEX["QMap%d" % _li])))
        a_.append(("#" + M_, _ck_glab(M_ + "N", 16, "title", CK_CW - 12, 22, bold=True)))
        a_.append(("#" + M_, _ck_wrap(M_ + "S", 13, "text", CK_CW - 12, 36)))
        a_.append(("#" + M_, G_.glass_group(M_ + "B", CK_CW - 12, 30, layout="Left")))
MQ_CARDS = [_c for _c in range(15) if MQ_CARD[_c] >= 0]


def _qj(name):
    return CKA[name].java("b")   # = _ckj (defined further down)


_QMAP_J = [_qj("qmap")]
for _i in MQ_CARDS:
    _QMAP_J += ["  if (this.ckMLock[%d]) {" % _i, _qj("mlock%d" % _i), "  }",
                "  if (this.ckMB[%d] == 1) {" % _i, _qj("mopen%d" % _i), _ck_bind(CKP + "M%dX" % _i, '"km%d"' % _i),
                "  } else if (this.ckMB[%d] == 2) {" % _i, _qj("mbuy%d" % _i), _ck_bind(CKP + "M%dX" % _i, '"kb%d"' % _i), "  }",
                _ck_jset(CKP + "M%dN" % _i, "this.ckMN[%d]" % _i), _ck_jset(CKP + "M%dS" % _i, "this.ckMS[%d]" % _i)]
for _z in range(5):
    _QMAP_J.append(_ck_jset(CKP + "Z%dS" % _z, "this.ckZS[%d]" % _z))
_QUP_J = [_qj("qup"), _ck_jset(CKP + "UpCap", "this.ckUpCap")]
for _r in range(Q_ROWS):
    R_ = CKP + "Q%d" % _r
    _QUP_J += [_ck_jset(R_ + "L", "this.ckUpL[%d]" % _r), _ck_jset(R_ + "E", "this.ckUpE[%d]" % _r), _ck_jset(R_ + "C", "this.ckUpC[%d]" % _r)]
    if _r == 7:
        _QUP_J += ["  if (this.ckQSm == 2 && this.mine) {", _qj("qsl"), _ck_jset(CKP + "Q7V", 'this.ckQPct + " %"'),
                   _ck_bind(CKP + "Q7M", '"kq-:" + this.ckQPct'), _ck_bind(CKP + "Q7U", '"kq+:" + this.ckQPct'),
                   "  } else if (this.ckQSm == 0) {", _qj("qtot7"), _ck_bind(CKP + "Q7X", '"ku7:0"'),
                   "  } else if (this.ckUpOk[7]) {", _qj("qon7"), _ck_bind(CKP + "Q7X", '"ku7:" + this.ckUpSeen[7]'),
                   "  } else {", _qj("qoff7"), "  }"]
    else:
        _QUP_J += ["  if (this.ckUpOk[%d]) {" % _r, _qj("qon%d" % _r), _ck_bind(R_ + "X", '"ku%d:" + this.ckUpSeen[%d]' % (_r, _r)),
                   "  } else {", _qj("qoff%d" % _r), "  }"]

'''
P.rep(r'''# the run-time templates (checked with samples)
_tex0 = CK_TEX["Tree1"]''', QRY_PAGE + r'''# the run-time templates (checked with samples)
_tex0 = CK_TEX["Tree1"]''')
# the title follows the shard; the map / the island pictures / springs + smithy / the upgrade panel branch on ckMine; a node's picture per spot
P.rep(r'''         _ck_jset(CKP + "ChipT", "this.ckChip"), _ck_jset(CKP + "Info", "this.ckInfo"),''',
      r'''         _ck_jset(CKP + "ChipT", "this.ckChip"), _ck_jset(CKP + "Info", "this.ckInfo"),
         _ck_jset(CKP + "Title", '(this.ckMine ? "MINING SHARD" : "FORAGING SHARD")'),''')
P.rep(r'''         "  if (this.ckMode == 1) {", _ckj("map")]''', r'''         "  if (this.ckMode == 1 && this.ckMine) {"] + _QMAP_J + ["  } else if (this.ckMode == 1) {", _ckj("map")]''')
P.rep(r'''    _ck_j += ["  if (this.ckSz == %d) {" % _s, _ckj("isl%d" % _s)]''',
      r'''    _ck_j += ["  if (this.ckSz == %d) {" % _s, "  if (this.ckMine) {", _ckj("qisl%d" % _s), "  } else {", _ckj("isl%d" % _s), "  }"]''')
P.rep(r'''    _ck_j += ["    if (this.ckWx > 0) {", _ckj("wx%d" % _s), "    }", "  }"]''',
      r'''    _ck_j += ["    if (this.ckWx > 0) {", "    if (this.ckMine) {", _ckj("qsp%d" % _s), "    } else {", _ckj("wx%d" % _s), "    }", "    }",
              "    if (this.ckMine && this.ckQSm > 0) {", _ckj("qsm%d" % _s), "    }", "  }"]''')
P.rep(r'''        "      String tex = this.ckGrow != null && i < this.ckGrow.length && this.ckGrow[i] ? this.ckStump : this.ckTree;",''',
      r'''        "      String tex = this.ckGrow != null && i < this.ckGrow.length && this.ckGrow[i] ? (this.ckTexB != null && i < this.ckTexB.length && this.ckTexB[i] != null ? this.ckTexB[i] : this.ckStump)"
        " : (this.ckTexA != null && i < this.ckTexA.length && this.ckTexA[i] != null ? this.ckTexA[i] : this.ckTree);",   # 0.4.24: a quarry node's picture per spot''')
P.rep(r'''    "  if (this.ckSz >= 1 && this.manage && @PKG@.ShCfg.CK_ON) {   // the click squares over the trees (on top of every picture)",''',
      r'''    "  if (this.ckSz >= 1 && this.manage && @PKG@.ShCfg.CK_ON && (!this.ckMine || @PKG@.ShCfg.MQ_ON)) {   // the click squares over the trees / nodes (on top of every picture)",''')
P.rep(r'''          _ckj("up"), _ck_jset(CKP + "UpCap", "this.ckUpCap")]''', r'''          "  if (this.ckMine) {"] + _QUP_J + ["  } else {", _ckj("up"), _ck_jset(CKP + "UpCap", "this.ckUpCap")]''')
P.rep(r'''_ck_j += ["  }", _ckj("foot"),''', r'''_ck_j += ["  }", "  }", _ckj("foot"),''')
# the checks of the quarry variants (each island size with all its parts + the slider; the quarry map with every card variant)
P.rep(r'''print("0.4.23 clicker page: %d x %d, %d variants checked, elements: island %s + %d run-time = %d at most, map %d; %d Skyglass paths; %d run-time templates"
      % (CK_W, CK_H, len(CK_VARS), _ck_el[:3], CK_NSPOT * 2 + 1 + 40, CK_ELEMENTS, _ck_el[3], CK_GLASS_N, len(CK_SAMPLES)))
''', r'''print("0.4.23 clicker page: %d x %d, %d variants checked, elements: island %s + %d run-time = %d at most, map %d; %d Skyglass paths; %d run-time templates"
      % (CK_W, CK_H, len(CK_VARS), _ck_el[:3], CK_NSPOT * 2 + 1 + 40, CK_ELEMENTS, _ck_el[3], CK_GLASS_N, len(CK_SAMPLES)))
# 0.4.24 the quarry variants: each size with every part (springs, smithy, totems, decorations) + the slider row / the Totems row / the other rows on;
# the quarry map with every card locked + bought
Q_VARS = []
for _s in (1, 2, 3):
    for _r7 in ("qsl", "qtot7", "qon7", "qoff7"):
        v_ = SUI.Appends()
        for _n in ["frame", "mapb0", "frame2", "left", "qisl%d" % _s] + ["deco%d_%d" % (_s, _j) for _j in range(5)] + ["tot%d_%d" % (_s, _j) for _j in range(5)] + \
                ["qsp%d" % _s, "qsm%d" % _s, "cap", "colall", "stotab", "qup"] + ["qon%d" % _r for _r in range(7)] + [_r7, "foot"]:
            v_.extend(CKA[_n])
        Q_VARS.append(v_)
v_ = SUI.Appends()
for _n in ["frame", "mapb1", "frame2", "qmap"] + ["mlock%d" % _i for _i in MQ_CARDS] + ["mbuy%d" % _i for _i in MQ_CARDS] + ["foot"]:
    v_.extend(CKA[_n])
Q_VARS.append(v_)
v_ = SUI.Appends()
for _n in ["frame", "mapb1", "frame2", "qmap"] + ["mopen%d" % _i for _i in MQ_CARDS] + ["foot"]:
    v_.extend(CKA[_n])
Q_VARS.append(v_)
for _i, v_ in enumerate(Q_VARS):
    v_.check(CKP)
    _pri = sum(1 for p_, mk_ in v_ if 'TexturePath: "SkyyGlass/Primary.png"' in SUI.render(mk_))   # ui-data: counting the Skyglass Primary buttons
    assert _pri <= 1, "0.4.24 quarry variant %d: %d Primary buttons" % (_i, _pri)
SUI.assert_proven([mk_ for v_ in Q_VARS for p_, mk_ in v_], what="SkyyShards 0.4.24 Mining quarry page")
Q_GLASS_N = SUI.assert_glass_paths([mk_ for v_ in Q_VARS for p_, mk_ in v_])
_q_el = [sum(SUI._strip_quoted(SUI.render(mk_)).count("{") for p_, mk_ in v_) for v_ in Q_VARS]
Q_ELEMENTS = max(_q_el[:-2]) + CK_NSPOT * 2 + 1 + 8 * 5
assert Q_ELEMENTS < 1000 and max(_q_el[-2:]) < 1000, "0.4.24: the quarry page stays well under ~1,600 elements: %s / %s" % (Q_ELEMENTS, _q_el)
print("0.4.24 quarry page: %d variants checked, elements: island at most %d + %d run-time = %d, map %s; %d Skyglass paths"
      % (len(Q_VARS), max(_q_el[:-2]), CK_NSPOT * 2 + 1 + 40, Q_ELEMENTS, _q_el[-2:], Q_GLASS_N))
''')

# ---------------------------------------------------------------------------------------------------- 7. the page: the Mining footer, kopen, fill / act for the quarry
P.rep(r'''    "  boolean ckF = this.kind == %d && @PKG@.ShCfg.CK_ON;   // 0.4.23: the Foraging Shard's footer opens the clicker" % CK_FK,''',
      r'''    "  boolean ckF = (this.kind == %d && @PKG@.ShCfg.CK_ON) || (this.kind == %d && @PKG@.ShCfg.CK_ON && @PKG@.ShCfg.MQ_ON);   // 0.4.23: the Foraging Shard's footer opens the clicker; 0.4.24: the Mining Shard's the quarry" % (CK_FK, MQ_K),''')
P.rep(r'''    if (this.view != 0 || this.kind != @PKG@.ShClk.FK) return "";
    if (!@PKG@.ShCfg.CK_ON) return "-The shard clicker is switched off on this server.";''', r'''    if (this.view != 0 || (this.kind != @PKG@.ShClk.FK && this.kind != @PKG@.ShClk.MK)) return "";
    if (!@PKG@.ShCfg.CK_ON) return "-The shard clicker is switched off on this server.";
    if (this.kind == @PKG@.ShClk.MK && !@PKG@.ShCfg.MQ_ON) return "-The Mining quarry is switched off on this server.";   // 0.4.24''')
P.rep(r'''  else if (this.view == 5) fillClick(k, cs, ref, st);   // 0.4.23
''', r'''  else if (this.view == 5 && this.kind == @PKG@.ShClk.MK) fillQuarry(k, cs, ref, st);   // 0.4.24
  else if (this.view == 5) fillClick(k, cs, ref, st);   // 0.4.23
''')
P.rep(r'''  this.kind = @PKG@.ShClk.FK;
  int kd = this.kind;
  this.key = k;
  this.title = "Foraging Shard";''', r'''  this.kind = @PKG@.ShClk.FK;
  int kd = this.kind;
  this.key = k;
  this.title = "Foraging Shard";
  this.ckMine = false; this.ckTexA = null; this.ckTexB = null; this.ckQSm = 0; this.ckQPct = 0; this.ckZone = 0;   // 0.4.24''')
P.rep(r'''public String actClick(String a, @REF@ ref, @ST@ st) {
  if (!a.startsWith("kt")) this.ckPop = "";''', r'''public String actClick(String a, @REF@ ref, @ST@ st) {
  if (this.kind == @PKG@.ShClk.MK) return actQuarry(a, ref, st);   // 0.4.24 the Mining quarry
  if (!a.startsWith("kt")) this.ckPop = "";''')

QRY_PAGE_M = r'''# 0.4.24 THE QUARRY (view 5 of the Mining Shard): the fill (bridges before the store lock, the quarry + the map read under it) and the clicks
M(page, r"""
public void fillQuarry(String k, @IC@[] cs, @REF@ ref, @ST@ st) {
  int kd = @PKG@.ShClk.MK;
  this.kind = kd;
  this.key = k;
  this.title = "Mining Shard";
  this.ckMine = true;
  this.ckUpL = new String[8]; this.ckUpE = new String[8]; this.ckUpC = new String[8]; this.ckUpOk = new boolean[8]; this.ckUpSeen = new int[8];
  for (int i = 0; i < 8; i++) { this.ckUpL[i] = ""; this.ckUpE[i] = ""; this.ckUpC[i] = ""; this.ckUpOk[i] = false; this.ckUpSeen[i] = 0; }
  this.ckMN = new String[15]; this.ckMS = new String[15]; this.ckMB = new int[15]; this.ckMLock = new boolean[15]; this.ckMCur = new boolean[15];
  for (int i = 0; i < 15; i++) { this.ckMN[i] = ""; this.ckMS[i] = ""; this.ckMB[i] = 0; this.ckMLock[i] = false; this.ckMCur[i] = false; }
  this.ckZS = new String[5];
  for (int i = 0; i < 5; i++) this.ckZS[i] = "";
  this.ckSto = new String[3];
  for (int i = 0; i < 3; i++) this.ckSto[i] = "";
  this.ckGrow = new boolean[@PKG@.ShClk.NSPOT];
  this.ckTexA = new String[@PKG@.ShClk.NSPOT];
  this.ckTexB = new String[@PKG@.ShClk.NSPOT];
  this.ckSz = 0; this.ckTn = 0; this.ckSpN = 0; this.ckWx = 0; this.ckDeco = 0; this.ckAmt = 0; this.ckNs = 0; this.ckT = -1; this.ckTi = 0; this.ckNext = -1;
  this.ckQSm = 0; this.ckQPct = 0; this.ckZone = 0;
  this.ckTree = Q_NODE[0]; this.ckStump = Q_RUB[0];
  this.ckChip = "No quarry yet"; this.ckCap = ""; this.ckUpCap = "";
  if (this.ckPop == null) this.ckPop = "";
  this.ckHand = handId(ref, st);
  this.ckAxe = @PKG@.ShClk.pickTier(this.ckHand);
  this.mine = k != null && this.me != null && k.equals(@PKG@.ShCfg.pkey(this.me));
  this.manage = k != null && @PKG@.ShRole.mayManage(this.me, k);
  this.bagT = 0L;
  this.sgN = 0; this.sgId = new String[0]; this.sgIc = new String[0]; this.sgQty = new String[0]; this.sgBg = new String[0]; this.sgHint = "Nothing is stored here yet.";
  this.ckInfo = this.ckAxe > 0 ? "Mining with your " + @PKG@.ShTotem.pretty(this.ckHand) + " (T" + this.ckAxe + ") - clicks give " + @PKG@.ShCfg.CK_XP_PCT + " % of world XP"
      : "Hold a pickaxe to mine - the quarry uses the pickaxe in your hand.";
  if (!@PKG@.ShCfg.CK_ON || !@PKG@.ShCfg.MQ_ON) this.ckInfo = "The Mining quarry is switched off on this server.";
  java.util.Properties p = k == null ? null : @PKG@.ShStore.get(k);
  if (p == null) { this.ckCap = k == null ? "Only the island owner and co-op members can use this shard." : "This shard's file could not be read."; return; }
  int LN = @PKG@.ShIsl.LADN[kd];
  int L0 = @PKG@.ShIsl.LAD0[kd];
  int lv = @PKG@.ShIsl.level(this.me, kd);   // the bridges before the store lock
  this.ckLv = lv;
  double[] tcv = new double[LN];
  for (int i = 0; i < LN; i++) tcv[i] = @PKG@.ShCfg.curve(@PKG@.ShIsl.band(@PKG@.ShIsl.TIER[L0 + i]));
  long now = @PKG@.ShCore.now();
  int[] own = new int[LN];
  Object[] gd = null;
  int[] ores = new int[0];
  int t = -1; int z = 0; int sz = 0; int amt = 0; int deco = 0; int irr = 0; int ns = 0; int tot = 0; int lk = 0; int smy = 0; int pct = 0; boolean pole = false;
  double rate = 0.0; long sto = 0L; long cap = 0L; String offw = "";
  @PKG@.ShStore.LOCK.lock(); try {
    @PKG@.ShMath.settleAll(kd, p, now);
    for (int i = 0; i < LN; i++) own[i] = @PKG@.ShIsl.slotOf(kd, p, L0 + i);
    int s0 = -1;
    if (this.ckSlot >= 0 && this.ckSlot < @PKG@.ShMath.SLOTS && @PKG@.ShMath.hasIsland(kd, p, this.ckSlot)) s0 = @PKG@.ShClk.baseSlot(p, @PKG@.ShIsl.zoneOf(@PKG@.ShIsl.ty(kd, p, this.ckSlot)));
    for (int zz = 1; zz <= 5 && s0 < 0; zz++) s0 = @PKG@.ShClk.baseSlot(p, zz);
    this.ckSlot = s0;
    if (s0 >= 0) {
      t = @PKG@.ShIsl.ty(kd, p, s0); z = @PKG@.ShIsl.zoneOf(t); ores = @PKG@.ShClk.zoneOwned(p, z);
      sz = @PKG@.ShMath.size(kd, p, s0);
      amt = @PKG@.ShIsl.sub(p, kd, s0, 0); deco = @PKG@.ShIsl.sub(p, kd, s0, 1); irr = @PKG@.ShIsl.sub(p, kd, s0, 2);
      ns = @PKG@.ShClk.nsize(p, kd, s0); tot = @PKG@.ShMath.totems(kd, p, s0); rate = @PKG@.ShMath.rate(kd, p, s0, now);
      lk = @PKG@.ShClk.luck(p, kd, s0); smy = @PKG@.ShClk.smithy(p, kd, s0); pct = @PKG@.ShClk.alloyPct(p, kd, s0); pole = @PKG@.ShTotem.smelts(kd, p, s0);
      sto = @PKG@.ShMath.usedOf(kd, p, s0); cap = @PKG@.ShMath.limOf(kd, p, s0);
      offw = @PKG@.ShIsl.offWords(kd, p, @PKG@.ShIsl.offLv(kd, p));
    }
    gd = @PKG@.ShCore.gridOf(kd, p);
    this.ckNext = @PKG@.ShIsl.nextTier(kd, p);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  gridFill(gd, kd);   // after the lock
  if (t >= 0 && ores.length > 0) {
    this.ckT = t; this.ckTi = t - L0; this.ckSz = sz; this.ckAmt = amt; this.ckDeco = deco; this.ckWx = irr; this.ckNs = ns; this.ckZone = z;
    this.ckSpN = tot > 5 ? 5 : tot;
    this.ckTn = @PKG@.ShIsl.treeN(sz, amt);
    if (this.ckTn > @PKG@.ShClk.NSPOT) this.ckTn = @PKG@.ShClk.NSPOT;
    String key2 = k + "|" + this.ckSlot;
    for (int i = 0; i < this.ckTn; i++) {
      int oi = ores[i % ores.length] - L0;
      int qi = oi < 0 ? 0 : (oi >= Q_NODE.length ? Q_NODE.length - 1 : oi);
      this.ckTexA[i] = Q_NODE[qi]; this.ckTexB[i] = Q_RUB[qi];
      this.ckGrow[i] = @PKG@.ShClk.readyAt(key2, i) > now;
    }
    this.ckQSm = !pole ? 0 : (smy >= 1 ? 2 : 1);
    this.ckQPct = pct;
    this.ckChip = "Zone " + z + " Quarry - " + ckSize(sz);
    StringBuilder on = new StringBuilder();
    for (int i = 0; i < ores.length; i++) { if (i > 0) on.append(", "); on.append(@PKG@.ShIsl.NAME[ores[i]]); }
    int zi = z - 1;
    this.ckSto[0] = "Ores: " + on.toString() + " + Silver / Gold finds; spirits: " + tot + (tot == 1 ? " totem" : " totems");
    this.ckSto[1] = "Spirit rate: " + @PKG@.ShCfg.dec(rate) + " a minute" + (pole ? " - the Smithy smelts" : "");
    this.ckSto[2] = "Stored here " + @PKG@.ShCfg.num(sto) + " / " + @PKG@.ShCfg.num(cap) + " - offline " + offw;
    String nx = "";   // fix: the zone's next ore (Zone 1: Iron) = buy its island on the quarry map
    for (int i = 0; i < LN && nx.length() == 0; i++) {
      if (own[i] >= 0 || @PKG@.ShIsl.zoneOf(L0 + i) != z) continue;
      int nd = @PKG@.ShIsl.zoneNeed(kd, L0 + i);
      nx = " Add " + @PKG@.ShIsl.NAME[L0 + i] + ": buy its island on Islands" + (nd > 0 ? " (" + @PKG@.ShIsl.skillWord(kd) + " " + nd + ")" : "") + ".";
    }
    this.ckCap = "Click an ore node to mine it (" + this.ckTn + " nodes, " + @PKG@.ShClk.blocksAt(ns) + " blocks each: stone + a chance of ore)." + (nx.length() > 0 ? nx : " Spirits mine while you are away.");
    double cv = this.ckTi >= 0 && this.ckTi < LN ? tcv[this.ckTi] : 1.0;
    // 0 Vein size (= 0.4.23's Tree size purchase)
    int mx = @PKG@.ShCfg.MQ_NS_MAX;
    this.ckUpL[0] = "Lv " + ns + " / " + mx; this.ckUpSeen[0] = ns;
    if (ns >= mx) this.ckUpE[0] = "Blocks a node: " + @PKG@.ShClk.blocksAt(ns) + " (highest)";
    else {
      this.ckUpE[0] = "Blocks a node " + @PKG@.ShClk.blocksAt(ns) + " -> " + @PKG@.ShClk.blocksAt(ns + 1);
      this.ckUpC[0] = ckCost(@PKG@.ShClk.nodeCoins(ns + 1, cv), @PKG@.ShClk.nodeMats(kd, t, ns + 1));
      this.ckUpOk[0] = this.mine;
    }
    // 1 Ore nodes = Ore Amount (sub 0)
    this.ckUpL[1] = "Lv " + amt + " / 5"; this.ckUpSeen[1] = amt;
    if (amt >= 5) this.ckUpE[1] = "Nodes: " + this.ckTn + (sz < 3 ? " - grow for more" : " (highest)");
    else {
      this.ckUpE[1] = "Nodes " + this.ckTn + " -> " + @PKG@.ShIsl.treeN(sz, amt + 1);
      this.ckUpC[1] = ckCost(@PKG@.ShIsl.coins(@PKG@.ShIsl.subH(sz, amt + 1), cv), @PKG@.ShIsl.mats(kd, t, @PKG@.ShCombat.subMat(kd, 0), sz - 1, (long) (amt + 1)));
      this.ckUpOk[1] = this.mine;
    }
    // 2 Miner spirits = the placed totems (the Totems tab)
    this.ckUpL[2] = tot + (tot == 1 ? " totem" : " totems"); this.ckUpSeen[2] = tot;
    this.ckUpE[2] = "Spirits mine, also when away";
    this.ckUpC[2] = "More / higher totems = faster";
    this.ckUpOk[2] = true;
    // 3 Springs = Underground Springs (sub 2): a faster refill + its output bonus
    this.ckUpL[3] = "Lv " + irr + " / 5"; this.ckUpSeen[3] = irr;
    if (irr >= 5) this.ckUpE[3] = "Refill " + (@PKG@.ShClk.refillMs(irr) / 1000L) + " s" + (sz < 3 ? " - grow for more" : " (highest)");
    else {
      this.ckUpE[3] = "Refill " + (@PKG@.ShClk.refillMs(irr) / 1000L) + " s -> " + (@PKG@.ShClk.refillMs(irr + 1) / 1000L) + " s, +" + @PKG@.ShCfg.dec(@PKG@.ShCfg.IRR_PCT) + " % output";
      this.ckUpC[3] = ckCost(@PKG@.ShIsl.coins(@PKG@.ShIsl.subH(sz, irr + 1), cv), @PKG@.ShIsl.mats(kd, t, @PKG@.ShCombat.subMat(kd, 2), sz - 1, (long) (irr + 1)));
      this.ckUpOk[3] = this.mine;
    }
    // 4 Island size = Grow (needs the three at 5 / 5 / 5)
    this.ckUpL[4] = ckSize(sz) + " (" + sz + " / 3)"; this.ckUpSeen[4] = sz;
    if (sz >= 3) this.ckUpE[4] = "Large - the biggest quarry";
    else {
      this.ckUpE[4] = ckSize(sz) + " -> " + ckSize(sz + 1) + ": room for " + @PKG@.ShIsl.tx(sz + 1).length + " nodes";
      if (amt < 5 || irr < 5 || deco < 5) this.ckUpC[4] = "Needs 5/5/5 first (" + amt + "/" + irr + "/" + deco + ")";
      else { this.ckUpC[4] = ckCost(@PKG@.ShIsl.coins(@PKG@.ShIsl.growH(sz + 1), cv), @PKG@.ShIsl.mats(kd, t, @PKG@.ShCfg.MAT_GROW, sz - 1, 1L)); this.ckUpOk[4] = this.mine; }
    }
    // 5 Decorations (sub 1)
    this.ckUpL[5] = "Lv " + deco + " / 5"; this.ckUpSeen[5] = deco;
    if (deco >= 5) this.ckUpE[5] = "All decorations" + (sz < 3 ? " - grow for more" : " (highest)");
    else {
      this.ckUpE[5] = "Looks + " + @PKG@.ShCfg.dec(@PKG@.ShCfg.DECO_PCT) + " % output a level";
      this.ckUpC[5] = ckCost(@PKG@.ShIsl.coins(@PKG@.ShIsl.subH(sz, deco + 1), cv), @PKG@.ShIsl.mats(kd, t, @PKG@.ShCombat.subMat(kd, 1), sz - 1, (long) (deco + 1)));
      this.ckUpOk[5] = this.mine;
    }
    // 6 Lucky finds (new: mining.i<n>.luck; the Ore Amount cost of that level)
    int lmx = @PKG@.ShCfg.MQ_LUCK_MAX;
    this.ckUpL[6] = "Lv " + lk + " / " + lmx; this.ckUpSeen[6] = lk;
    String ln = "Ore " + @PKG@.ShCfg.dec(@PKG@.ShClk.oreP(lk) * 100.0) + " %, Silver " + @PKG@.ShCfg.dec(@PKG@.ShClk.rareP(lk, z, false) * 100.0) + " %, Gold " + @PKG@.ShCfg.dec(@PKG@.ShClk.rareP(lk, z, true) * 100.0) + " %";
    if (lk >= lmx) this.ckUpE[6] = ln;   // the level shows Lv 5 / 5
    else {
      this.ckUpE[6] = "Ore " + @PKG@.ShCfg.dec(@PKG@.ShClk.oreP(lk) * 100.0) + " -> " + @PKG@.ShCfg.dec(@PKG@.ShClk.oreP(lk + 1) * 100.0) + " %, Silver " + @PKG@.ShCfg.dec(@PKG@.ShClk.rareP(lk, z, false) * 100.0) + " -> " + @PKG@.ShCfg.dec(@PKG@.ShClk.rareP(lk + 1, z, false) * 100.0) + " %";
      this.ckUpC[6] = ckCost(@PKG@.ShIsl.coins(@PKG@.ShIsl.subH(sz, lk + 1), cv), @PKG@.ShIsl.mats(kd, t, @PKG@.ShCombat.subMat(kd, 0), sz - 1, (long) (lk + 1)));
      this.ckUpOk[6] = this.mine;
    }
    // 7 Smithy: the Auto-Smelt Pole (bars) -> Smithy II (the alloy slider)
    String an = zi >= 0 && zi < @PKG@.ShClk.QA_ID.length ? @PKG@.ShClk.qName(@PKG@.ShClk.QA_ID[zi]) : "the alloy";
    String ab = zi >= 0 && zi < @PKG@.ShClk.QA_ID.length ? @PKG@.ShClk.qName(@PKG@.ShClk.QA_A[zi]) + " + " + @PKG@.ShClk.qName(@PKG@.ShClk.QA_B[zi]) : "two bars";
    this.ckUpSeen[7] = smy;
    if (this.ckQSm == 0) { this.ckUpL[7] = "No smithy"; this.ckUpE[7] = "Auto-Smelt Pole: ores -> bars"; this.ckUpC[7] = "Place one on the Totems tab"; this.ckUpOk[7] = true; }
    else if (this.ckQSm == 1) {
      this.ckUpL[7] = "Bars"; this.ckUpE[7] = "Smithy II: " + an + " slider";
      this.ckUpC[7] = ckCost(@PKG@.ShClk.smithyCoins(cv), @PKG@.ShClk.smithyMats(kd, t));
      this.ckUpOk[7] = this.mine;
    } else { this.ckUpL[7] = "Smithy II"; this.ckUpE[7] = pct + " % of new bars -> " + an; this.ckUpC[7] = "1 + 1 -> 2 " + an; }
    this.ckUpCap = this.mine ? "coins + " + @PKG@.ShTotem.pretty(@PKG@.ShIsl.tok(kd, t, "ench")) : "the island owner buys upgrades";
  } else this.ckCap = "No Mining island yet - open Islands to buy the first one.";
  // the quarry map: five zones of their ores (QCARD: card -> ladder rank)
  for (int c = 0; c < 15 && c < QCARD.length; c++) {
    int li = QCARD[c];
    if (li < 0 || li >= LN) continue;
    int tt = L0 + li;
    int need = @PKG@.ShIsl.zoneNeed(kd, tt);
    boolean open = need <= 0 || lv == -1 || lv >= need;
    int zc = @PKG@.ShIsl.zoneOf(tt);
    this.ckMN[c] = @PKG@.ShIsl.tname(tt);
    this.ckMCur[c] = own[li] >= 0 && t >= 0 && zc == z;
    this.ckMLock[c] = !open && own[li] < 0;
    if (own[li] >= 0) { this.ckMS[c] = (this.ckMCur[c] ? "Shown now" : "Yours") + " - in the Zone " + zc + " quarry"; this.ckMB[c] = this.ckMCur[c] ? 0 : 1; }
    else if (!open) this.ckMS[c] = "Locked: " + @PKG@.ShIsl.skillWord(kd) + " " + need;
    else if (li == this.ckNext) {
      this.ckMS[c] = "Buy: " + ckCost(@PKG@.ShIsl.coins(@PKG@.ShCfg.BUY_H, tcv[li]), @PKG@.ShIsl.mats(kd, tt, @PKG@.ShCfg.BUY_ITEMS[kd], 0, 1L));
      this.ckMB[c] = this.mine ? 2 : 0;
    }
    else this.ckMS[c] = "Buy the islands before it first";
  }
  for (int zz = 0; zz < 5; zz++) {
    int li0 = QCARD[3 * zz];
    int need = li0 >= 0 && li0 < LN ? @PKG@.ShIsl.zoneNeed(kd, L0 + li0) : 0;
    boolean open = need <= 0 || lv == -1 || lv >= need;
    this.ckZS[zz] = need <= 0 ? "Open" : (open ? "Open - " + @PKG@.ShIsl.skillWord(kd) + " " + need : "Locked - " + @PKG@.ShIsl.skillWord(kd) + " " + need + (lv >= 0 ? " (you: " + lv + ")" : ""));
  }
}""")
M(page, r"""
public String actQuarry(String a, @REF@ ref, @ST@ st) {
  if (!a.startsWith("kt")) this.ckPop = "";
  if (a.equals("kback")) { this.view = 0; this.tab = 1; return ""; }
  if (a.equals("kstore")) { this.view = 0; this.tab = 0; return ""; }
  if (a.equals("kmap")) { this.ckMode = 1; return ""; }
  if (a.equals("kisl")) { this.ckMode = 0; return ""; }
  String k = resolve(st);
  if (k == null) return "-Only the island owner and co-op members can use this shard.";
  java.util.UUID u = this.me;
  int kd = @PKG@.ShClk.MK;
  if (a.startsWith("kt")) {   // a node: "kt<spot>:<quarry slot>" = what the page showed
    int c = a.indexOf(':');
    int spot = -1; int slot = -1;
    try { spot = Integer.parseInt(a.substring(2, c < 0 ? a.length() : c)); slot = c < 0 ? -1 : Integer.parseInt(a.substring(c + 1)); } catch (Throwable x) { spot = -1; }
    if (spot < 0 || slot < 0 || slot != this.ckSlot) return "=The page is up to date now.";
    Object[] r = @PKG@.ShClk.chop(u, k, kd, slot, spot, handId(ref, st));
    String s0 = (String) r[0];
    String pp = (String) r[1];
    if (pp.length() > 0 || s0.length() > 0) { this.ckPop = pp; this.ckPopI = spot; }
    return s0;
  }
  if (a.startsWith("km")) {   // the map: show the quarry of that card's zone (a Mining island you own)
    int c = -1;
    try { c = Integer.parseInt(a.substring(2)); } catch (Throwable x) { c = -1; }
    int li = c >= 0 && c < QCARD.length ? QCARD[c] : -1;
    java.util.Properties p = @PKG@.ShStore.get(k);
    if (p == null || li < 0 || li >= @PKG@.ShIsl.LADN[kd]) return "";
    int s;
    @PKG@.ShStore.LOCK.lock(); try {
      int tt = @PKG@.ShIsl.LAD0[kd] + li;
      s = @PKG@.ShIsl.slotOf(kd, p, tt) < 0 ? -1 : @PKG@.ShClk.baseSlot(p, @PKG@.ShIsl.zoneOf(tt));
    } finally { @PKG@.ShStore.LOCK.unlock(); }
    if (s < 0) return "-That island is not yours yet.";
    this.ckSlot = s; this.ckMode = 0;
    return "";
  }
  if (a.startsWith("kb")) {   // the map: buy the next Mining island (tier order, the zone lock, the Map tab's cost)
    int c = -1;
    try { c = Integer.parseInt(a.substring(2)); } catch (Throwable x) { c = -1; }
    if (!this.mine) return "-Only the island owner buys islands.";
    int li = c >= 0 && c < QCARD.length ? QCARD[c] : -1;
    if (li < 0 || li >= @PKG@.ShIsl.LADN[kd]) return "";
    String r = @PKG@.ShCore.buyIsland(u, k, kd, li, invOf(ref, st));
    if (r.startsWith("+")) {
      java.util.Properties p = @PKG@.ShStore.get(k);
      if (p != null) {
        int s;
        @PKG@.ShStore.LOCK.lock(); try { int tt = @PKG@.ShIsl.LAD0[kd] + li; s = @PKG@.ShIsl.slotOf(kd, p, tt) < 0 ? -1 : @PKG@.ShClk.baseSlot(p, @PKG@.ShIsl.zoneOf(tt)); } finally { @PKG@.ShStore.LOCK.unlock(); }
        if (s >= 0) { this.ckSlot = s; this.ckMode = 0; }
      }
    }
    return r;
  }
  if (a.startsWith("kq")) {   // the alloy slider: "kq-:<value shown>" / "kq+:<value shown>"
    if (!this.mine) return "-Only the island owner moves the alloy slider.";
    int c = a.indexOf(':');
    int seen = -1;
    try { seen = c < 0 ? -1 : Integer.parseInt(a.substring(c + 1)); } catch (Throwable x) { seen = -1; }
    if (seen < 0 || this.ckSlot < 0) return "=The page is up to date now.";
    return @PKG@.ShClk.setAlloy(u, k, kd, this.ckSlot, seen, a.startsWith("kq-") ? -1 : 1);
  }
  if (a.startsWith("ku")) {   // an upgrade row: "ku<row>:<level the page showed>" (a double click buys once)
    int c = a.indexOf(':');
    int row = -1; int seen = -1;
    try { row = Integer.parseInt(a.substring(2, c < 0 ? a.length() : c)); seen = c < 0 ? -1 : Integer.parseInt(a.substring(c + 1)); } catch (Throwable x) { row = -1; }
    if (row == 2 || (row == 7 && this.ckQSm == 0)) { this.view = 0; this.tab = 3; this.sel = this.ckTi; this.tpad = 0; return ""; }
    if (row < 0 || row > 7) return "";
    if (!this.mine) return "-Only the island owner buys upgrades.";
    int s = this.ckSlot;
    if (s < 0) return "-Pick a quarry first.";
    java.util.Properties pb = @PKG@.ShStore.get(k);   // fix: the slot must still be this profile's quarry (base) island
    if (pb == null) return "-This shard's file could not be read.";
    boolean base;
    @PKG@.ShStore.LOCK.lock(); try { base = s < @PKG@.ShMath.SLOTS && @PKG@.ShMath.hasIsland(kd, pb, s) && @PKG@.ShClk.isBase(pb, kd, s); } finally { @PKG@.ShStore.LOCK.unlock(); }
    if (!base) return "=The page is up to date now - click Upgrade again.";
    @IC@[] cs = invOf(ref, st);
    if (row == 0) return @PKG@.ShClk.buyNode(u, k, kd, s, seen, cs);
    if (row == 6) return @PKG@.ShClk.buyLuck(u, k, kd, s, seen, cs);
    if (row == 7) return @PKG@.ShClk.buySmithy(u, k, kd, s, seen, cs);
    java.util.Properties p = @PKG@.ShStore.get(k);
    if (p == null) return "-This shard's file could not be read.";
    int which = row == 1 ? 0 : (row == 3 ? 2 : 1);
    int cur;
    @PKG@.ShStore.LOCK.lock(); try {
      if (!@PKG@.ShMath.hasIsland(kd, p, s)) return "-That island is not yours yet.";
      cur = row == 4 ? @PKG@.ShMath.size(kd, p, s) : @PKG@.ShIsl.sub(p, kd, s, which);
    } finally { @PKG@.ShStore.LOCK.unlock(); }
    if (seen != cur) return "=The page is up to date now - click Upgrade again.";
    if (row == 4) return @PKG@.ShCore.grow(u, k, kd, s, cs);
    return @PKG@.ShCore.buySub(u, k, kd, s, which, cs);
  }
  if (a.startsWith("gc:")) {   // a store cell = that item kind (the mined blocks first, then the stock)
    if (!@PKG@.ShRole.mayManage(u, k)) return "-Only the island owner collects here.";
    return @PKG@.ShCore.collectKind(u, k, kd, a.substring(3), invOf(ref, st));
  }
  if (a.equals("colall")) {
    if (!@PKG@.ShRole.mayManage(u, k)) return "-Only the island owner collects here.";
    return @PKG@.ShCore.collect(u, k, kd, -1, invOf(ref, st));
  }
  return "";
}""")
'''
P.rep(r'''M(page, r"""
public void fillClick(String k, @IC@[] cs, @REF@ ref, @ST@ st) {''', QRY_PAGE_M + r'''M(page, r"""
public void fillClick(String k, @IC@[] cs, @REF@ ref, @ST@ st) {''')
P.rep(r'''          "public String[] ckMN;", "public String[] ckMS;", "public int[] ckMB;", "public boolean[] ckMLock;", "public boolean[] ckMCur;", "public String[] ckZS;"):''',
      r'''          "public String[] ckMN;", "public String[] ckMS;", "public int[] ckMB;", "public boolean[] ckMLock;", "public boolean[] ckMCur;", "public String[] ckZS;",
          "public boolean ckMine;", "public String[] ckTexA;", "public String[] ckTexB;", "public int ckQSm;", "public int ckQPct;", "public int ckZone;"):   # 0.4.24 the quarry''')

# ---------------------------------------------------------------------------------------------------- 8. the ready line
P.rep(r'''log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.23:''', r'''log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.24: the Mining Shard quarry (Shard clicker in the Mining Shard menu: mine ore nodes with your pickaxe, one quarry a zone, Lucky finds, the Smithy + alloy slider, Mining zone locks; Fortune via skill:fn:fortune); 0.4.23:''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
_i = P.s.index
assert _i("public static Object[] mine(java.util.UUID u") < _i("public static Object[] chop(java.util.UUID u"), "mine() compiled before chop()"
assert _i("public static double fortuneOf(") < _i("public static Object[] mine(java.util.UUID u"), "fortuneOf before mine"
assert _i("public static long blocksAt(int ns)") < _i("public static String buyNode("), "blocksAt before buyNode"
assert _i("public String actQuarry(") < _i("public String actClick("), "actQuarry before actClick"
assert _i("public static long owedAs(") < _i("public static String collectHeld("), "owedAs before collectHeld"
assert _i("public static int baseSlot(") < _i("public static boolean isBase(") < _i("public static String buyLuck("), "baseSlot before isBase before buyLuck"
P.finish()
