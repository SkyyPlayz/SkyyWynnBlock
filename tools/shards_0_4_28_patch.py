"""Derive SkyyShards/build_skyyshards_0.4.28.py from the GENERATED SkyyShards 0.4.27 (build_skyyshards_0.4.27.py = the tools/deploy_set.py SET
pin, made by tools/shards_0_4_27_patch.py - edit the patch, never the generated file). Every anchor is asserted once; at the end every change
is undone on a copy and compared with 0.4.27 (tools/soundpass_gen.Patch). Line endings kept.
Run:   python tools/shards_0_4_28_patch.py   then   python SkyyShards/build_skyyshards_0.4.28.py   (never --deploy)
Check: python SkyyShards/test_skyyshards_0.4.28.py

0.4.28 (2026-11-22) = THE RANCHING + ORCHARD CLICKERS (round ranch1; Skyy 2026-11-21 docs/answered/world.md "SHARD WORLD -> CLICKER ONLY": "the goal is
  to compleatly replace this with the clicker system, instead of keeping both at once."; "CLICKER BALANCE = SELF-SUSTAINING": "lets make sure we balance
  the clickers so everything to keep upgrading them can be gotten in the clicker, except maybe main island upgrades, and island you need birch to make the
  birch island so you have to find the tree type first kinda thing."; Skyy 2026-11-21 "build and deploy everything on your list"). The last two shards
  on the old menu (0.4.27 kept Ranching + Orchard on it without Enter Shard) get their clicker; then every shard is clicker-only.
  SPEC (short; the survey first):
  - SURVEY. Vanilla (Assets.zip): no clicker page (0.4.23-0.4.27 surveys). The animals' REAL products are read at build time from
    Server/Drops/NPCs/Livestock/Drop_<Animal>.json + Drop_<Animal>_Harvest.json + Produce/Drop_<Animal>_Produce.json (Chicken: Raw Chicken 1-2 +
    Light Hide 1-2, Light Feathers 1-2, an Egg; Cow: Raw Beef 1-2 + Medium Hide 1-2; Pig: Raw Pork 1-2 + Light Hide; Boar: Wild Meat 1-2 + Medium
    Hide 1-2; Sheep: Wool 1-3 + Wild Meat 1-2, Light Hide; Turkey: Wild Meat 1-2, Light Hide; Goat: Light Hide 1-2 + Wild Meat 1-2; Bison: Raw Beef
    2-3, Medium Hide 2-3; Poop left out). Fruit: Drops_Plant_Crop_Apple_StageFinal_Harvest (1 apple), Plant_Bush_Berry_Red (1-2 berries); the wild
    tree fruits have no vanilla drop list (1 a fruit). Mods: the 0.4.23 survey (pie-clicker, learn only); nothing new packed. Approved art: none
    for Ranching / Orchard in research/ui-theme-art (grep 'ranch' / 'orchard').
  - 1. THE RANCH = view 5 of the Ranching Shard (the portal opens it): ONE ISLAND PER ANIMAL (the ladder: Chicken, Cow, Pig | Boar, Sheep, Turkey |
    Goat, Bison), the map groups them in ZONE clusters (3 a zone = ShIsl.zoneOf; Zones 4-5 empty for now). The animals stand on the island's spots
    (Herd size = the old Herd Size sub-upgrade decides how many). Click an animal by hand: click.ranch.hp (6) clicks, then it is TENDED: click.ranch.rolls
    (2) + Feed quality x click.ranch.sizeRolls (1) rolls, each = the island's product in its vanilla quantity x (1 + Fortune extras: SkyySkills
    skill:fn:fortune "Ranching" when it answers, else the skill:bonus dd.ranching sum - "through the existing reads") and, at click.ranch.extraPermille
    (250 = 25 %) each, one of the animal's other vanilla products (no Fortune). XP = click.xpPercent (25) % of the world's Ranching XP of what was
    tended (SkyySkills P3 ranching.items, copied: Egg 30, Wool 30, Light Feathers 10, Raw Chicken 20, Raw Pork 20, Raw Beef 30, Wild Meat 20, Light
    Hide 10, Medium Hide 20; Heavy Hide 40 = ours). It rests click.ranch.restSec (10) - Water troughs x click.ranch.troughSec (1), at least
    click.ranch.minRestSec (3).
  - 2. THE ORCHARD = view 5 of the Orchard Shard: ONE ISLAND PER FRUIT (Apple, Berries, Coconut | Mango, Pinkberry, Azure | Spiral, Windwillow), zone
    clusters as the ranch. Click a fruit tree (a bush for the berries) by hand: click.orchard.hp (8) clicks, then it is PICKED: click.orchard.fruits
    (3) + Fruit yield x click.orchard.sizeFruits (1) fruits, each = the vanilla quantity (Apple 1, Berries / Pinkberry 1-2, the others 1) x (1 +
    Fortune: skill:fn:fortune "Farming" on the fruit block - Orchard is fed by Farming's perks in the world - else dd.farming). XP = click.xpPercent %
    of click.orchard.xp (a fruit = the world's Farming XP of a crop of its tier, SkyySkills P3: 40 .. 605; Orchard takes that XP in the world). It grows
    new fruit in click.orchard.regrowSec (12) - Irrigation x click.orchard.irrSec (1), at least click.orchard.minRegrowSec (3).
  - 3. BOTH reuse the farm's page (0.4.25 fillFarm, derived here per kind with every swap asserted), the 0.4.27 rows with clear have / need cost lines,
    the UPGRADES view (spirit totem + 2 modifiers + the shard-wide rows), the store strip (the Orchard's sapling store: Give / Take), the .drops store
    (saved at once; Collect / the grid pay it with the collection credit), the click cap, the stale-island / profile-switch guard (ckFresh), a double
    click buying once (the level the page showed). ZONE LOCKS: ShIsl.zoneNeed for Ranching / Orchard = click.ranch.zoneLevel / click.orchard.zoneLevel
    (0 / 20 / 40 / 60 / 80 of Ranching / Orchard - their skills, ShIsl.level); an island you own stays yours and clickable.
  - 4. THE PORTALS OPEN THE CLICKERS; THE OLD MENU GOES: ShClk.clicker() now names all six shards (the portal, the rail, a locked portal = opens
    nothing). The old Map tab pictures of Ranching / Orchard go (BaseRanching / BaseOrchard 840 x 688 + RanchingE / OrchardE): the old menu never opens.
  - 5. SELF-SUSTAINING COSTS: every island upgrade already names only the island's own raw / Enchanted item (0.4.27); a type WITHOUT an Enchanted form
    (Mango, Pinkberry, Azure, Spiral, Windwillow) paid Enchanted OAK LOGS (ShKind.UPG fallback - a Foraging item) -> now 100 of its own fruit per
    Enchanted asked (ShIsl.enchX, Ranching + Orchard only; the 0.3 BENCH_MAT rule "no Enchanted form yet -> 100 of the island's base item"). Shard-wide
    rows (Storage / Compactor / Compressor / Automation / Offline) keep their items (Skyy's exception); a NEW island needs its own type from the world
    (isl.buyItems: Ranching 64 of the product + 2 Capture Crates, Orchard 128 fruit + 16 saplings) - unchanged. The report tables every line.
    FIX (critic ranch1): Island size (isl.mat.grow "eseed:8|eseed:24") asked an Orchard TREE island for saplings the clicker never gives -> each sapling
    = click.orchard.saplingFruit (16) of its own fruit (ShIsl.ownSeed; Medium 128, Large 384 fruit; the berry bushes had no sapling row). Kept: the
    x 100 own fruit per Enchanted (it is SkyySacks' own rate - haveIn counts a Pocket Enchanted as 100; the bags pay: payInvBags draws the Pocket).
  - 6. ONE-TIME PER-PROFILE MIGRATION (ShStore.migrate4, marker clk2.done=1, PROJECT-RULES 4; = 0.4.27's migrate3 pattern): for a profile that owns
    the Ranching or Orchard Shard the file is copied to shards/history/clicker/<pkey>.pre-0.4.28.properties first (byte-checked), an AUTOMATED
    Orchard / Ranching island's seed / sapling store still holding items moves into that island's storage (as migrate3; the clicker never replants
    from it), ONE save with the marker, a collect.log line naming every island / totem / stored item count carried over as it is + the Undo. Nothing
    else is rewritten (islands, sizes, sub-upgrades, totems with tiers / modifiers / boosters, stored items, legacy stock, .drops, Automation, Offline,
    Storage, Compactor all stay - the clicker reads the same keys). A refused copy / save leaves file + memory untouched (tried again at the next
    load). A profile without either shard: the marker rides along with its next save.
  - 7. PICTURES at 1x (tools/ci/ui_budget.py): 8 animals + a hay bed, 8 fruit trees / bushes ripe + picked (the 0.4.23 tree drawings + our fruit),
    110 x 140 each, drawn at build time; the map cards show the same pictures; the row icons reuse 0.4.23 / 0.4.25 icons. The Shards UI area goes DOWN
    (-1.16 Mpx of old Map bases, + ~0.4 Mpx new).
  NUMBERS (new, Server Setup -> Shards -> Shard clicker; all editable): click.ranch.enabled true, click.ranch.hp 6, click.ranch.rolls 2,
    click.ranch.sizeRolls 1, click.ranch.sizeMax 10, click.ranch.extraPermille 250, click.ranch.restSec 10, click.ranch.troughSec 1,
    click.ranch.minRestSec 3, click.ranch.xp 20,30,20,20,30,10,10,40, click.ranch.zoneLevel 0,20,40,60,80, click.orchard.enabled true, click.orchard.hp 8,
    click.orchard.fruits 3, click.orchard.sizeFruits 1, click.orchard.sizeMax 10, click.orchard.regrowSec 12, click.orchard.irrSec 1,
    click.orchard.minRegrowSec 3, click.orchard.xp 40,80,135,185,280,380,460,605, click.orchard.zoneLevel 0,20,40,60,80, click.orchard.saplingFruit 16 (fix). Copied (not new): the Tree size
    coin / Enchanted table for Feed quality / Fruit yield, the 0.4.27 spirit / modifier costs, the Map tab costs for the rest.
  SAVED DATA: ranching.i<n>.nsize / orchard.i<n>.nsize (Feed quality / Fruit yield, missing = 0), ranching.i<n>.drops / orchard.i<n>.drops (tended /
    picked, not collected yet), clk2.done=1 (marker). Old files load unchanged.
  ROLLBACK 0.4.28 -> 0.4.27 alone: no settings migration. Collect all on the Ranching / Orchard Shards first (0.4.27's Collect is generic and pays
    .drops too, so nothing is lost either way); 0.4.27 ignores nsize and clk2.done (kept in the file); the old menus come back without their Map
    pictures (red / white squares on the Map tab - cosmetic) and the five Orchard fruits pay Enchanted Oak again. Undo of the migration: stop the
    server, copy shards/history/clicker/<pkey>.pre-0.4.28.properties back over shards/<pkey>.properties.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

HERE = os.path.join(ROOT, "SkyyShards")
P = G.Patch(os.path.join(HERE, "build_skyyshards_0.4.27.py"), os.path.join(HERE, "build_skyyshards_0.4.28.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.4.27"\n') and P.has("GENERATED by tools/shards_0_4_27_patch.py") and P.has("ckSpirit") and not P.has("fillRanch"), "not the generated SkyyShards 0.4.27"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.28 (2026-11-22)"):].rstrip() + "\n"


def sub1(txt, old, new, n=1):
    """replace old in txt; it must occur exactly n times"""
    c = txt.count(old)
    assert c == n, "0.4.28 anchor count %d (want %d): %s" % (c, n, old[:160])
    return txt.replace(old, new)


# ---------------------------------------------------------------------------------------------------- 0. header + version
P.rep('''"""SkyyShards 0.4.27 - build script (javassist via jpype). GENERATED by tools/shards_0_4_27_patch.py from build_skyyshards_0.4.26.py
(generated by tools/shards_0_4_26_patch.py from 0.4.25, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.27" /''', '''"""SkyyShards 0.4.28 - build script (javassist via jpype). GENERATED by tools/shards_0_4_28_patch.py from build_skyyshards_0.4.27.py
(generated by tools/shards_0_4_27_patch.py from 0.4.26, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.28" / "0.4.27" /''')
P.rep('''Run:   python SkyyShards/build_skyyshards_0.4.27.py   -> SkyyShards/SkyyShards-0.4.27.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.27.py
''', '''Run:   python SkyyShards/build_skyyshards_0.4.28.py   -> SkyyShards/SkyyShards-0.4.28.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.28.py
''' + NOTE + '''
''')
P.rep('VERSION = "0.4.27"\n', 'VERSION = "0.4.28"\n')

# ---------------------------------------------------------------------------------------------------- 1. ShCfg: the ranch's + orchard's settings
P.rep(r'''          "public static volatile double MQ_S1H = 0.1;", "public static volatile int MQ_S1ORE = 64;", "public static volatile boolean TF_COINS = true;"):
    F(cfg, f)
''', r'''          "public static volatile double MQ_S1H = 0.1;", "public static volatile int MQ_S1ORE = 64;", "public static volatile boolean TF_COINS = true;"):
    F(cfg, f)
# 0.4.28 THE RANCHING + ORCHARD CLICKERS (tools/shards_0_4_28_patch.py): their settings (Server Setup -> Shards -> Shard clicker, click.ranch.* / click.orchard.*)
RQ_K, OQ_K = KINDS.index("Ranching"), KINDS.index("Orchard")
assert (RQ_K, OQ_K) == (3, 4) and len(LAD[RQ_K]) == 8 and len(LAD[OQ_K]) == 8
RQ_ZLV = [0, 20, 40, 60, 80]          # Zone 1..5 pens are bought from this Ranching level
OQ_ZLV = [0, 20, 40, 60, 80]          # Zone 1..5 orchards are bought from this Orchard level
# the world's Ranching XP of one item (SkyySkills P3 ranching.items, copied 2026-11-22 from build_skyyskills_0.4.73.py P3_RANCH; Heavy Hide = ours, 2 x Medium)
RQ_ITEM_XP = {"Food_Egg": 30, "Ingredient_Fabric_Scrap_Wool": 30, "Ingredient_Feathers_Light": 10, "Food_Chicken_Raw": 20, "Food_Pork_Raw": 20, "Food_Beef_Raw": 30,
              "Food_Wildmeat_Raw": 20, "Ingredient_Hide_Light": 10, "Ingredient_Hide_Medium": 20, "Ingredient_Hide_Heavy": 40}
RQ_XPD = [RQ_ITEM_XP[_t["prod"]] for _t in LAD[RQ_K]]
OQ_XPD = list(P3_CROP_XP)[:8]          # a fruit = the world's Farming XP of a crop of the same tier (Orchard takes that XP in the world)
assert RQ_XPD == [20, 30, 20, 20, 30, 10, 10, 40] and OQ_XPD == [40, 80, 135, 185, 280, 380, 460, 605], (RQ_XPD, OQ_XPD)
for f in ("public static volatile boolean RQ_ON = true;", "public static volatile int RQ_HP = 6;", "public static volatile int RQ_ROLLS = 2;",
          "public static volatile int RQ_NS_PER = 1;", "public static volatile int RQ_NS_MAX = 10;", "public static volatile int RQ_EXTRA = 250;",
          "public static volatile int RQ_REST = 10;", "public static volatile int RQ_TROUGH = 1;", "public static volatile int RQ_RMIN = 3;",
          "public static final int[] DEF_RQ_XP = new int[] { %s };" % ", ".join(str(_x) for _x in RQ_XPD),
          "public static volatile int[] RQ_XP = new int[] { %s };" % ", ".join(str(_x) for _x in RQ_XPD),
          "public static final int[] DEF_RQ_ZLV = new int[] { %s };" % ", ".join(str(_x) for _x in RQ_ZLV),
          "public static volatile int[] RQ_ZLV = new int[] { %s };" % ", ".join(str(_x) for _x in RQ_ZLV),
          "public static volatile boolean OQ_ON = true;", "public static volatile int OQ_HP = 8;", "public static volatile int OQ_FRUITS = 3;",
          "public static volatile int OQ_NS_PER = 1;", "public static volatile int OQ_NS_MAX = 10;", "public static volatile int OQ_REGROW = 12;",
          "public static volatile int OQ_IRR = 1;", "public static volatile int OQ_RMIN = 3;", "public static volatile int OQ_SAPF = 16;",
          "public static final int[] DEF_OQ_XP = new int[] { %s };" % ", ".join(str(_x) for _x in OQ_XPD),
          "public static volatile int[] OQ_XP = new int[] { %s };" % ", ".join(str(_x) for _x in OQ_XPD),
          "public static final int[] DEF_OQ_ZLV = new int[] { %s };" % ", ".join(str(_x) for _x in OQ_ZLV),
          "public static volatile int[] OQ_ZLV = new int[] { %s };" % ", ".join(str(_x) for _x in OQ_ZLV)):
    F(cfg, f)
''')
P.rep(r'''         ("click.fight.coins", "Town: kills pay coins", "clicker", "bool", "true", "", "", "", "", "live",
          "On: town kills also earn SkyyMobs' kill coins, paid by Collect all on the town page.", "reload@config.properties:click.fight.coins")]
''', r'''         ("click.fight.coins", "Town: kills pay coins", "clicker", "bool", "true", "", "", "", "", "live",
          "On: town kills also earn SkyyMobs' kill coins, paid by Collect all on the town page.", "reload@config.properties:click.fight.coins")]
# 0.4.28: the Ranching + Orchard clickers' rows
ROWS += [("click.ranch.enabled", "Ranching clicker", "clicker", "bool", "true", "", "", "", "", "live",
          "Off: the Ranching clicker's clicks do nothing. Nothing is deleted.", "reload@config.properties:click.ranch.enabled"),
         ("click.ranch.hp", "Ranch: clicks to tend an animal", "clicker", "int", "6", "1", "1000", "", "", "live",
          "Clicks an animal takes before it is tended (its products drop).", "reload@config.properties:click.ranch.hp"),
         ("click.ranch.rolls", "Ranch: drop rolls a tend", "clicker", "int", "2", "1", "1000", "", "", "live",
          "Rolls of the island's product a tend gives before Feed quality (each: the animal's vanilla drop).", "reload@config.properties:click.ranch.rolls"),
         ("click.ranch.sizeRolls", "Ranch: more rolls per Feed quality", "clicker", "int", "1", "0", "100", "", "", "live",
          "Each Feed quality level adds this many rolls to a tend.", "reload@config.properties:click.ranch.sizeRolls"),
         ("click.ranch.sizeMax", "Ranch: Feed quality levels", "clicker", "int", "10", "0", "10", "", "", "live",
          "The highest Feed quality level (costs: the Tree size rows).", "reload@config.properties:click.ranch.sizeMax"),
         ("click.ranch.extraPermille", "Ranch: other products chance (1/1000)", "clicker", "int", "250", "0", "1000", "", "", "live",
          "Chance per roll of each other vanilla product of the animal (hide, eggs ...), in 1/1000.", "reload@config.properties:click.ranch.extraPermille"),
         ("click.ranch.restSec", "Ranch: an animal rests for", "clicker", "int", "10", "1", "3600", "", "s", "live",
          "Seconds before a tended animal can be tended again (before Water troughs).", "reload@config.properties:click.ranch.restSec"),
         ("click.ranch.troughSec", "Ranch: Water troughs shorter rest", "clicker", "int", "1", "0", "600", "", "s", "live",
          "Seconds less rest per Water troughs level.", "reload@config.properties:click.ranch.troughSec"),
         ("click.ranch.minRestSec", "Ranch: shortest rest", "clicker", "int", "3", "0", "3600", "", "s", "live",
          "An animal never rests shorter than this.", "reload@config.properties:click.ranch.minRestSec"),
         ("click.ranch.xp", "Ranch: world XP a product, by animal", "clicker", "text", ",".join(str(_x) for _x in RQ_XPD), "", "200", "", "", "live",
          "8 numbers, animal T1..T8: world Ranching XP of one main product (clicks pay click.xpPercent).", "reload@config.properties:click.ranch.xp"),
         ("click.ranch.zoneLevel", "Ranch zone opens at Ranching level", "clicker", "text", ",".join(str(_x) for _x in RQ_ZLV), "", "60", "", "", "live",
          "5 numbers, Zone 1..5: Ranching islands of a zone are bought from this Ranching level.", "reload@config.properties:click.ranch.zoneLevel"),
         ("click.orchard.enabled", "Orchard clicker", "clicker", "bool", "true", "", "", "", "", "live",
          "Off: the Orchard clicker's clicks do nothing. Nothing is deleted.", "reload@config.properties:click.orchard.enabled"),
         ("click.orchard.hp", "Orchard: clicks to pick a tree", "clicker", "int", "8", "1", "1000", "", "", "live",
          "Clicks a fruit tree takes before it is picked.", "reload@config.properties:click.orchard.hp"),
         ("click.orchard.fruits", "Orchard: fruit a pick", "clicker", "int", "3", "1", "1000", "", "", "live",
          "Fruit rolls a picked tree gives before Fruit yield (each: the fruit's vanilla drop).", "reload@config.properties:click.orchard.fruits"),
         ("click.orchard.sizeFruits", "Orchard: more fruit per Fruit yield", "clicker", "int", "1", "0", "100", "", "", "live",
          "Each Fruit yield level adds this many fruit rolls to a pick.", "reload@config.properties:click.orchard.sizeFruits"),
         ("click.orchard.sizeMax", "Orchard: Fruit yield levels", "clicker", "int", "10", "0", "10", "", "", "live",
          "The highest Fruit yield level (costs: the Tree size rows).", "reload@config.properties:click.orchard.sizeMax"),
         ("click.orchard.regrowSec", "Orchard: new fruit in", "clicker", "int", "12", "1", "3600", "", "s", "live",
          "Seconds before a picked tree has fruit again (before Irrigation).", "reload@config.properties:click.orchard.regrowSec"),
         ("click.orchard.irrSec", "Orchard: Irrigation faster fruit", "clicker", "int", "1", "0", "600", "", "s", "live",
          "Seconds less per Irrigation level.", "reload@config.properties:click.orchard.irrSec"),
         ("click.orchard.minRegrowSec", "Orchard: fastest new fruit", "clicker", "int", "3", "0", "3600", "", "s", "live",
          "A tree never grows new fruit faster than this.", "reload@config.properties:click.orchard.minRegrowSec"),
         ("click.orchard.xp", "Orchard: world XP a fruit, by tree", "clicker", "text", ",".join(str(_x) for _x in OQ_XPD), "", "200", "", "", "live",
          "8 numbers, fruit T1..T8: Orchard XP of one fruit (clicks pay click.xpPercent).", "reload@config.properties:click.orchard.xp"),
         ("click.orchard.saplingFruit", "Orchard: fruit instead of a sapling", "clicker", "int", "16", "1", "10000", "", "", "live",
          "Orchard Island size: own fruit asked per sapling the grow row names.", "reload@config.properties:click.orchard.saplingFruit"),
         ("click.orchard.zoneLevel", "Orchard zone opens at Orchard level", "clicker", "text", ",".join(str(_x) for _x in OQ_ZLV), "", "60", "", "", "live",
          "5 numbers, Zone 1..5: Orchard islands of a zone are bought from this Orchard level.", "reload@config.properties:click.orchard.zoneLevel")]
''')
P.rep(r'''          "  TF_COINS = bool(p.getProperty(\"click.fight.coins\"), true);"]
''', r'''          "  TF_COINS = bool(p.getProperty(\"click.fight.coins\"), true);"]
_load += ["  RQ_ON = bool(p.getProperty(\"click.ranch.enabled\"), true);",   # 0.4.28 the Ranching clicker
          "  RQ_HP = intOf(p.getProperty(\"click.ranch.hp\"), 6, 1, 1000);",
          "  RQ_ROLLS = intOf(p.getProperty(\"click.ranch.rolls\"), 2, 1, 1000);",
          "  RQ_NS_PER = intOf(p.getProperty(\"click.ranch.sizeRolls\"), 1, 0, 100);",
          "  RQ_NS_MAX = intOf(p.getProperty(\"click.ranch.sizeMax\"), 10, 0, 10);",
          "  RQ_EXTRA = intOf(p.getProperty(\"click.ranch.extraPermille\"), 250, 0, 1000);",
          "  RQ_REST = intOf(p.getProperty(\"click.ranch.restSec\"), 10, 1, 3600);",
          "  RQ_TROUGH = intOf(p.getProperty(\"click.ranch.troughSec\"), 1, 0, 600);",
          "  RQ_RMIN = intOf(p.getProperty(\"click.ranch.minRestSec\"), 3, 0, 3600);",
          "  RQ_XP = intsOf(p.getProperty(\"click.ranch.xp\"), DEF_RQ_XP, 0, 1000000, \"click.ranch.xp\");",
          "  RQ_ZLV = intsOf(p.getProperty(\"click.ranch.zoneLevel\"), DEF_RQ_ZLV, 0, 1000, \"click.ranch.zoneLevel\");",
          "  OQ_ON = bool(p.getProperty(\"click.orchard.enabled\"), true);",   # 0.4.28 the Orchard clicker
          "  OQ_HP = intOf(p.getProperty(\"click.orchard.hp\"), 8, 1, 1000);",
          "  OQ_FRUITS = intOf(p.getProperty(\"click.orchard.fruits\"), 3, 1, 1000);",
          "  OQ_NS_PER = intOf(p.getProperty(\"click.orchard.sizeFruits\"), 1, 0, 100);",
          "  OQ_NS_MAX = intOf(p.getProperty(\"click.orchard.sizeMax\"), 10, 0, 10);",
          "  OQ_REGROW = intOf(p.getProperty(\"click.orchard.regrowSec\"), 12, 1, 3600);",
          "  OQ_IRR = intOf(p.getProperty(\"click.orchard.irrSec\"), 1, 0, 600);",
          "  OQ_RMIN = intOf(p.getProperty(\"click.orchard.minRegrowSec\"), 3, 0, 3600);",
          "  OQ_SAPF = intOf(p.getProperty(\"click.orchard.saplingFruit\"), 16, 1, 10000);",   # fix (critic): Island size pays fruit, not world saplings
          "  OQ_XP = intsOf(p.getProperty(\"click.orchard.xp\"), DEF_OQ_XP, 0, 1000000, \"click.orchard.xp\");",
          "  OQ_ZLV = intsOf(p.getProperty(\"click.orchard.zoneLevel\"), DEF_OQ_ZLV, 0, 1000, \"click.orchard.zoneLevel\");"]
''')

# ---------------------------------------------------------------------------------------------------- 2. ShIsl: zone locks + the Enchanted fallback (self-sustaining)
P.rep(r'''public static int zoneNeed(int kd, int t) {
  if (kd != @CKFK@ && kd != @MQK@ && kd != @FQK@) return 0;
  int[] a = kd == @MQK@ ? @PKG@.ShCfg.MQ_ZLV : (kd == @FQK@ ? @PKG@.ShCfg.FQ_ZLV : @PKG@.ShCfg.CK_ZLV);   // 0.4.24 Mining / 0.4.25 Farming zones by their skill level
  int z = zoneOf(t);
  return a == null || z - 1 >= a.length ? 0 : a[z - 1];
}""".replace("@CKFK@", str(CK_FK)).replace("@MQK@", str(MQ_K)).replace("@FQK@", str(FQ_K)))''', r'''public static int zoneNeed(int kd, int t) {
  if (kd != @CKFK@ && kd != @MQK@ && kd != @FQK@ && kd != @RQK@ && kd != @OQK@) return 0;
  int[] a = kd == @MQK@ ? @PKG@.ShCfg.MQ_ZLV : (kd == @FQK@ ? @PKG@.ShCfg.FQ_ZLV : (kd == @RQK@ ? @PKG@.ShCfg.RQ_ZLV : (kd == @OQK@ ? @PKG@.ShCfg.OQ_ZLV : @PKG@.ShCfg.CK_ZLV)));   // 0.4.24 Mining / 0.4.25 Farming / 0.4.28 Ranching + Orchard zones by their skill level
  int z = zoneOf(t);
  return a == null || z - 1 >= a.length ? 0 : a[z - 1];
}""".replace("@CKFK@", str(CK_FK)).replace("@MQK@", str(MQ_K)).replace("@FQK@", str(FQ_K)).replace("@RQK@", str(RQ_K)).replace("@OQK@", str(OQ_K)))''')
# a Ranching / Orchard type without an Enchanted form: "ench" = 100 of its own product (was ShKind.UPG = Enchanted Wheat / Enchanted Oak, outside items)
P.rep(r'''M(isl48, r"""
public static String tok(int kd, int t, String tk) {
  if (tk.equals("raw")) return SMELT[t].length() > 0 ? SMELT[t] : PROD[t];   // 0.4.20: a type that smelts costs ingots ("on the mining shard, instead of using ore to upgrade, use ingots")
  if (tk.equals("ench")) { String e = ENCH[t]; if (e.length() == 0) e = SMELTE[t]; if (e.length() == 0) e = @PKG@.ShKind.UPG[kd]; return e; }''', r'''# 0.4.28 SELF-SUSTAINING (Skyy 2026-11-21 "everything to keep upgrading them can be gotten in the clicker"): a Ranching / Orchard type without an Enchanted
# form pays 100 of its own product per Enchanted asked (the 0.3 BENCH_MAT rule) instead of the shard's UPG item (Enchanted Wheat / Oak = another shard's)
# fix (critic ranch1): an Orchard TREE island's "eseed" (its sapling - the clicker never gives one) = its own fruit x click.orchard.saplingFruit,
# so Island size is gotten in the clicker too; isl.buyItems' "seed" (a NEW island: find the tree type first - Skyy's exception) stays the sapling
M(isl48, r"""
public static boolean ownSeed(int kd, int t, String tk) {
  if (!"eseed".equals(tk) || t < 0 || t >= PROD.length || kd < 0 || kd >= STYLE.length) return false;
  return "orchard".equals(STYLE[kd]) && ESEED[t].length() > 0;
}""")
M(isl48, r"""
public static long enchX(int kd, int t, String tk) {
  if (ownSeed(kd, t, tk)) return (long) @PKG@.ShCfg.OQ_SAPF;   // fix (critic): fruit per sapling asked
  if (!"ench".equals(tk) || t < 0 || t >= PROD.length || kd < 0 || kd >= STYLE.length) return 1L;
  if (ENCH[t].length() > 0 || SMELTE[t].length() > 0) return 1L;
  return ("ranch".equals(STYLE[kd]) || "orchard".equals(STYLE[kd])) ? 100L : 1L;
}""")
M(isl48, r"""
public static String tok(int kd, int t, String tk) {
  if (tk.equals("raw")) return SMELT[t].length() > 0 ? SMELT[t] : PROD[t];   // 0.4.20: a type that smelts costs ingots ("on the mining shard, instead of using ore to upgrade, use ingots")
  if (tk.equals("ench") && enchX(kd, t, tk) > 1L) return PROD[t];   // 0.4.28: x 100 in mats / ShCore.spiritMats / modMats
  if (ownSeed(kd, t, tk)) return PROD[t];   // fix (critic): an Orchard tree island's Island size pays its own fruit (x click.orchard.saplingFruit in mats)
  if (tk.equals("ench")) { String e = ENCH[t]; if (e.length() == 0) e = SMELTE[t]; if (e.length() == 0) e = @PKG@.ShKind.UPG[kd]; return e; }''')
P.rep(r'''    String id = tok(kd, t, x.substring(0, c).trim());
    long n = 0L;
    try { n = Long.parseLong(x.substring(c + 1).trim()); } catch (Throwable e) { n = 0L; }
    if (id == null || id.length() == 0 || n <= 0L || mul <= 0L) continue;
    n = n * mul;''', r'''    String tk0 = x.substring(0, c).trim();
    String id = tok(kd, t, tk0);
    long n = 0L;
    try { n = Long.parseLong(x.substring(c + 1).trim()); } catch (Throwable e) { n = 0L; }
    if (id == null || id.length() == 0 || n <= 0L || mul <= 0L) continue;
    n = n * mul * enchX(kd, t, tk0);   // 0.4.28: 100 of the own product per Enchanted asked (a type without an Enchanted form)''')
P.rep(r'''  return itemCost(@PKG@.ShIsl.tok(kd, t, "ench"), (long) a[i]);''',
      r'''  return itemCost(@PKG@.ShIsl.tok(kd, t, "ench"), (long) a[i] * @PKG@.ShIsl.enchX(kd, t, "ench"));   // 0.4.28: x 100 own product without an Enchanted form''')
P.rep(r'''M(core, "public static Object[] modMats(int kd, int t) { return itemCost(@PKG@.ShIsl.tok(kd, t, \"ench\"), (long) @PKG@.ShCfg.MOD_E); }")''',
      r'''M(core, "public static Object[] modMats(int kd, int t) { return itemCost(@PKG@.ShIsl.tok(kd, t, \"ench\"), (long) @PKG@.ShCfg.MOD_E * @PKG@.ShIsl.enchX(kd, t, \"ench\")); }")   # 0.4.28''')

# ---------------------------------------------------------------------------------------------------- 2b. readable Enchanted names on the new cost lines
# ShTotem.pretty("Skyy_Ench_RawChicken") read "Enchanted RawChicken" / "Enchanted WildFruit": the Ranching + Orchard ladders' Enchanted items now read their
# SkyyCollections display name (tools/skyyench.py: "Enchanted Raw Chicken", "Enchanted Coconut"); every other id reads as before
P.rep('''# a readable name for an item id (the craft tab, chat lines)
M(tot, r"""
public static String pretty(String id) {''', '''_EN428 = dict((_SE.PREFIX + _t[0], _t[6]) for _t in _SE.TABLE)   # 0.4.28 (tools/shards_0_4_28_patch.py): the Ranching / Orchard Enchanted display names
_EN428 = sorted((_t["ench"], _EN428[_t["ench"]]) for _k in (RQ_K, OQ_K) for _t in LAD[_k] if _t["ench"])
assert ("Skyy_Ench_RawChicken", "Enchanted Raw Chicken") in _EN428 and ("Skyy_Ench_WildFruit", "Enchanted Coconut") in _EN428 and len(_EN428) == 11, _EN428
F(tot, "public static final String[] EN_ID = new String[] { %s };" % ", ".join(jlit(_a) for _a, _b in _EN428))   # 0.4.28
F(tot, "public static final String[] EN_NM = new String[] { %s };" % ", ".join(jlit(_b) for _a, _b in _EN428))
# a readable name for an item id (the craft tab, chat lines)
M(tot, r"""
public static String pretty(String id) {''')
P.rep('''  if (s.startsWith("Skyy_Ench_")) s = "Enchanted " + s.substring(10);''', '''  for (int i = 0; i < EN_ID.length; i++) if (EN_ID[i].equals(s)) return EN_NM[i];   // 0.4.28: the Ranching / Orchard Enchanted names
  if (s.startsWith("Skyy_Ench_")) s = "Enchanted " + s.substring(10);''')

# ---------------------------------------------------------------------------------------------------- 3. ShClk: THE RANCH + THE ORCHARD (the tend / pick click)
GATHER_CLK = r'''# ---- 0.4.28 THE RANCHING + ORCHARD CLICKERS (tools/shards_0_4_28_patch.py): ONE ISLAND PER ANIMAL / FRUIT. An animal / a fruit tree = the 0.4.23 tree
# (damage, rest / regrow, the click cap) clicked by hand (no tool gate); a tend = rolls x the animal's vanilla product quantity x (1 + Fortune extras) + at
# click.ranch.extraPermille each other vanilla product; a pick = fruit rolls x the vanilla fruit quantity x (1 + Fortune). Into the island's .drops (saved at once).
RQ_LAD, OQ_LAD = LAD[RQ_K], LAD[OQ_K]
_LIVE = "Server/Drops/NPCs/Livestock/"


def _drop_items(name):
    """[(ItemId, qmin, qmax)] of a vanilla drop list (a missing quantity = 1), every nested container"""
    out, stk = [], [json.loads(AZ.read(name).decode("utf-8-sig"))]
    while stk:
        x_ = stk.pop()
        if isinstance(x_, dict):
            it_ = x_.get("Item")
            if isinstance(it_, dict) and isinstance(it_.get("ItemId"), str):
                q0_ = it_.get("QuantityMin")
                q1_ = it_.get("QuantityMax")
                q0_ = 1 if q0_ is None else int(q0_)
                q1_ = q0_ if q1_ is None else int(q1_)
                out.append((it_["ItemId"], q0_, q1_))
            stk.extend(x_.values())
        elif isinstance(x_, list):
            stk.extend(x_)
    return out


R_QMIN, R_QMAX, R_EX, R_FOUND = [], [], [], []
for _t in RQ_LAD:
    _fs = [_LIVE + "Drop_%s.json" % _t["name"], _LIVE + "Drop_%s_Harvest.json" % _t["name"], _LIVE + "Produce/Drop_%s_Produce.json" % _t["name"]]
    _its = []
    for _f in _fs:
        if _f in AZN:
            _its += _drop_items(_f)
    assert _fs[0] in AZN, "0.4.28: the vanilla drop list of %s is gone (%s)" % (_t["name"], _fs[0])
    _rng = {}
    for _id, _a, _b in _its:
        if _id == "Ingredient_Poop" or _b <= 0:
            continue
        assert _id in ITEMS, "0.4.28: a vanilla animal product is not an item: %s" % _id
        _o = _rng.get(_id)
        _rng[_id] = (max(1, _a), _b) if _o is None else (max(1, min(_o[0], _a)), max(_o[1], _b))
    _main = _rng.pop(_t["prod"], None)
    R_FOUND.append(_main is not None)
    _main = _main or (1, 2)   # Turkey feathers / Bison heavy hide: the ladder's product is not in its vanilla drop list - 1-2 a roll (ours)
    R_QMIN.append(_main[0]); R_QMAX.append(_main[1])
    R_EX.append(",".join("%s:%d:%d" % (_id, _r[0], _r[1]) for _id, _r in sorted(_rng.items())))
assert [_t["name"] for _t in RQ_LAD] == ["Chicken", "Cow", "Pig", "Boar", "Sheep", "Turkey", "Goat", "Bison"]
assert (R_QMIN, R_QMAX) == ([1, 1, 1, 1, 1, 1, 1, 1], [2, 2, 2, 2, 3, 2, 2, 2]), (R_QMIN, R_QMAX)
assert R_FOUND == [True, True, True, True, True, False, True, False], R_FOUND
assert R_EX[0] == "Food_Egg:1:1,Ingredient_Feathers_Light:1:2,Ingredient_Hide_Light:1:2" and R_EX[7] == "Food_Beef_Raw:2:3,Ingredient_Hide_Medium:2:3", R_EX
RX_ITEMS = sorted(set(_x.split(":")[0] for _e in R_EX for _x in _e.split(",") if _x) | set(_t["prod"] for _t in RQ_LAD))
assert all(_i in RQ_ITEM_XP for _i in RX_ITEMS), [_i for _i in RX_ITEMS if _i not in RQ_ITEM_XP]
# the fruit: Apple from the ripe apple block's drop, Berries from the red berry bush (Pinkberry = its wet bush: the same 1-2), the tree fruits 1
_ap = [(_a, _b) for _id, _a, _b in _drop_items("Server/Drops/Crop/Apple/Drops_Plant_Crop_Apple_StageFinal_Harvest.json") if _id == "Plant_Fruit_Apple"]
_br = [(_a, _b) for _id, _a, _b in _drop_items("Server/Drops/Plant/Plant_Bush_Berry_Red.json") if _id == "Plant_Fruit_Berries_Red"]
assert _ap == [(1, 1)] and _br == [(1, 2)], (_ap, _br)
O_Q = {"apple": _ap[0], "berries": _br[0], "pinkberry": _br[0]}
O_QMIN = [O_Q.get(_t["key"], (1, 1))[0] for _t in OQ_LAD]
O_QMAX = [O_Q.get(_t["key"], (1, 1))[1] for _t in OQ_LAD]
O_BLOCK = [_t["fruit"] or _t["prod"] for _t in OQ_LAD]   # the block Fortune's "only" match reads (the fruit block where one exists)
assert [_t["key"] for _t in OQ_LAD] == ["apple", "berries", "coconut", "mango", "pinkberry", "azure", "spiral", "windwillow"]
for f in ("public static final int[] R_QMIN = new int[] { %s };" % ", ".join(str(_x) for _x in R_QMIN),
          "public static final int[] R_QMAX = new int[] { %s };" % ", ".join(str(_x) for _x in R_QMAX),
          "public static final String[] R_EX = new String[] { %s };" % ", ".join(jlit(_x) for _x in R_EX),
          "public static final String[] RX_ID = new String[] { %s };" % ", ".join(jlit(_x) for _x in RX_ITEMS),
          "public static final int[] RX_XP = new int[] { %s };" % ", ".join(str(RQ_ITEM_XP[_x]) for _x in RX_ITEMS),
          "public static final int[] O_QMIN = new int[] { %s };" % ", ".join(str(_x) for _x in O_QMIN),
          "public static final int[] O_QMAX = new int[] { %s };" % ", ".join(str(_x) for _x in O_QMAX),
          "public static final String[] O_BLOCK = new String[] { %s };" % ", ".join(jlit(_x) for _x in O_BLOCK),
          "public static final java.util.concurrent.atomic.AtomicLong TENDED = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong PICKED = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong GATHERED = new java.util.concurrent.atomic.AtomicLong();"):
    F(ckc, f)
M(ckc, "public static boolean gatherOn(int kd) { return kd == RNK ? @PKG@.ShCfg.RQ_ON : (kd == ORK && @PKG@.ShCfg.OQ_ON); }")
M(ckc, r"""
public static long rollsAt(int kd, int ns) {
  if (kd == RNK) return (long) @PKG@.ShCfg.RQ_ROLLS + (long) ns * (long) @PKG@.ShCfg.RQ_NS_PER;
  return (long) @PKG@.ShCfg.OQ_FRUITS + (long) ns * (long) @PKG@.ShCfg.OQ_NS_PER;
}""")
M(ckc, r"""
public static long gatherRegrowMs(int kd, int irr) {
  boolean r = kd == RNK;
  long s = (long) (r ? @PKG@.ShCfg.RQ_REST : @PKG@.ShCfg.OQ_REGROW) - (long) (r ? @PKG@.ShCfg.RQ_TROUGH : @PKG@.ShCfg.OQ_IRR) * (long) (irr < 0 ? 0 : irr);
  long mn = (long) (r ? @PKG@.ShCfg.RQ_RMIN : @PKG@.ShCfg.OQ_RMIN);
  if (s < mn) s = mn;
  return s < 0L ? 0L : s * 1000L;
}""")
M(ckc, r"""
public static int gatherXp(int kd, int ci) {
  int[] a = kd == RNK ? @PKG@.ShCfg.RQ_XP : @PKG@.ShCfg.OQ_XP;
  if (a == null || a.length == 0) return 0;
  int i = ci < 0 ? 0 : (ci >= a.length ? a.length - 1 : ci);
  return a[i];
}""")
M(ckc, r"""
public static int exXp(String id) {
  for (int i = 0; i < RX_ID.length; i++) if (RX_ID[i].equals(id)) return RX_XP[i];
  return 0;
}""")
M(ckc, r"""
public static double extraP() {
  double c = (double) @PKG@.ShCfg.RQ_EXTRA / 1000.0;
  return c < 0.0 ? 0.0 : (c > 1.0 ? 1.0 : c);
}""")
M(ckc, r"""
public static long qroll(long q0, long q1) {
  if (q1 <= q0) return q0;
  long q = q0 + (long) Math.floor(rnd() * (double) (q1 - q0 + 1L));
  return q > q1 ? q1 : q;
}""")
# THE TEND / PICK CLICK (world thread; the bridges outside the store lock): Object[]{ status, pop text }. The rolls (exact order, replayed by the harness):
# per roll [the quantity roll when min < max], the Fortune roll, then (Ranching) per other product [the chance roll, then its quantity roll when min < max]
M(ckc, r"""
public static Object[] gather(java.util.UUID u, String k, int kd, int slot, int spot, String hand) {
  boolean rn = kd == RNK;
  if (kd != RNK && kd != ORK) return res("", "");
  if (!gatherOn(kd)) return res(rn ? "-The Ranching clicker is switched off on this server." : "-The Orchard clicker is switched off on this server.", "");
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
  if (ci < 0 || ci >= (rn ? R_QMIN.length : O_QMIN.length)) return res("=The page is up to date now.", "");
  String prod = @PKG@.ShIsl.PROD[t];
  double f = rn ? fortuneOf(u, "Ranching", prod, "dd.ranching", "only.ranching") : fortuneOf(u, "Farming", O_BLOCK[ci], "dd.farming", "only.farming");
  String key = k + "|" + kd + "|" + slot;   // this kind's own memory (a Foraging / Farming island in the same slot number keeps its own)
  double hpMax = (double) (rn ? @PKG@.ShCfg.RQ_HP : @PKG@.ShCfg.OQ_HP);
  double left = hit(key, spot, 1.0, hpMax, now, gatherRegrowMs(kd, irr));
  CHOPS.incrementAndGet();
  if (left < 0.0) {
    long ms = (long) (-left - 1.0);
    return res((rn ? "=That animal is resting - " : "=That tree is growing new fruit - ") + ((ms + 999L) / 1000L) + " s.", "");
  }
  if (left > 0.0) return res("", @PKG@.ShCfg.dec(hpMax - left) + " / " + @PKG@.ShCfg.dec(hpMax));
  long gM; long baseM; long mainQ; long total; long rolls; String[] exId; long[] exGot;
  @PKG@.ShStore.LOCK.lock(); try {
    if (!@PKG@.ShMath.hasIsland(kd, p, slot) || @PKG@.ShIsl.ty(kd, p, slot) != t) { unfell(key, spot, hpMax); return res("-That island changed meanwhile - the page is up to date now.", ""); }
    rolls = rollsAt(kd, nsize(p, kd, slot));
    long q0 = (long) (rn ? R_QMIN[ci] : O_QMIN[ci]);
    long q1 = (long) (rn ? R_QMAX[ci] : O_QMAX[ci]);
    String[] ex = rn && R_EX[ci].length() > 0 ? R_EX[ci].split(",") : new String[0];
    exId = new String[ex.length];
    long[] e0 = new long[ex.length];
    long[] e1 = new long[ex.length];
    long[] exQ = new long[ex.length];
    for (int e = 0; e < ex.length; e++) {
      String[] a = ex[e].split(":");
      exId[e] = a[0];
      e0[e] = Long.parseLong(a[1]);
      e1[e] = Long.parseLong(a[2]);
    }
    double pe = rn ? extraP() : 0.0;
    mainQ = 0L; baseM = 0L;
    for (long b = 0L; b < rolls && b < 100000L; b++) {
      long q = qroll(q0, q1);
      baseM = baseM + q;
      mainQ = mainQ + q * (1L + (long) extras(f, rnd()));
      for (int e = 0; e < ex.length; e++) if (pe > 0.0 && rnd() < pe) exQ[e] = exQ[e] + qroll(e0[e], e1[e]);
    }
    total = mainQ;
    for (int e = 0; e < ex.length; e++) total = total + exQ[e];
    @PKG@.ShMath.settle(kd, p, slot, now);
    long room = @PKG@.ShMath.limOf(kd, p, slot) - @PKG@.ShMath.usedOf(kd, p, slot);
    if (room <= 0L) { unfell(key, spot, hpMax); return res("-This island's storage is full - Collect first.", ""); }
    gM = mainQ < room ? mainQ : room; room = room - gM;   // what fits: the island's product first, then the other products in order
    exGot = new long[ex.length];
    for (int e = 0; e < ex.length; e++) { exGot[e] = exQ[e] < room ? exQ[e] : room; room = room - exGot[e]; }
    String dk = @PKG@.ShMath.ik(kd, slot, "drops");
    String old = p.getProperty(dk);
    java.util.LinkedHashMap m = @PKG@.ShMath.held(kd, p, slot);
    addTo(m, prod, gM);
    for (int e = 0; e < ex.length; e++) addTo(m, exId[e], exGot[e]);
    @PKG@.ShMath.heldSet(kd, p, slot, m);
    String er = @PKG@.ShStore.save(k, p);
    if (er != null) {
      if (old == null) p.remove(dk); else p.setProperty(dk, old);
      unfell(key, spot, hpMax);
      @PKG@.ShCfg.warnOnce("gsave", "a tended animal / picked tree could not be saved (nothing added, it stands again; logged once): " + er);
      return res("-The shard file could not be saved - nothing was added.", "");
    }
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  FELLS.incrementAndGet();
  if (rn) TENDED.incrementAndGet(); else PICKED.incrementAndGet();
  long got = gM;
  for (int e = 0; e < exGot.length; e++) got = got + exGot[e];
  GATHERED.addAndGet(got);
  long paidM = gM < baseM ? gM : baseM;
  double xpe = (double) paidM * (double) gatherXp(kd, ci);
  for (int e = 0; e < exGot.length; e++) xpe = xpe + (double) exGot[e] * (double) exXp(exId[e]);
  xpe = xpe * (double) @PKG@.ShCfg.CK_XP_PCT / 100.0;
  String skill = @PKG@.ShKind.SKILL[kd];
  long xp = accXp(String.valueOf(u) + "|" + @PKG@.ShCfg.pkey(u) + "|" + kd, xpe);   // this kind's own XP fractions
  String xt = "";
  if (xp > 0L) { long xl = @PKG@.ShCore.owedXp(u, skill, xp); xt = xl > 0L ? " (" + @PKG@.ShCfg.num(xl) + " " + skill + " XP waits)" : " +" + @PKG@.ShCfg.num(xp) + " " + skill + " XP"; }
  StringBuilder sb = new StringBuilder();
  part(sb, gM, prod);
  for (int e = 0; e < exGot.length; e++) part(sb, exGot[e], exId[e]);
  String fit = got < total ? " - the island's storage is full (" + @PKG@.ShCfg.num(total - got) + " did not fit)" : "";
  String r = (rn ? "+Tended a " + @PKG@.ShIsl.tname(t) + ": " : "+Picked a " + @PKG@.ShIsl.tname(t) + " tree: ") + (sb.length() > 0 ? sb.toString() : "nothing fit") + xt + fit + ".";
  String pop = gM > 0L ? "+" + @PKG@.ShCfg.num(gM) + " " + qName(prod) : (got > 0L ? "+" + @PKG@.ShCfg.num(got) : "");
  @PKG@.ShSnd.ok(u, r, 0);
  return res(r, pop);
}""")
'''
# the kind numbers early: ShClk.clicker() (0.4.27, compiled before the fight click) names them
P.rep('''for f in ("public static final int CRK = %d;" % FQ_K,''', '''for f in ("public static final int CRK = %d;" % FQ_K, "public static final int RNK = %d;" % RQ_K, "public static final int ORK = %d;" % OQ_K,   # 0.4.28''')
P.rep(r'''# THE CLICK: Object[]{ status ("+..." / "-..." / "=..." / "" = nothing to say), pop text over the tree }. World thread; the bridges outside the store lock
M(ckc, r"""
public static Object[] chop(''', GATHER_CLK + r'''# THE CLICK: Object[]{ status ("+..." / "-..." / "=..." / "" = nothing to say), pop text over the tree }. World thread; the bridges outside the store lock
M(ckc, r"""
public static Object[] chop(''')
P.rep(r'''M(ckc, "public static boolean clicker(int kd) { return kd == FK || kd == MK || kd == CRK || kd == TK; }")''',
      r'''M(ckc, "public static boolean clicker(int kd) { return kd == FK || kd == MK || kd == CRK || kd == TK || kd == RNK || kd == ORK; }")   # 0.4.28: + Ranching, Orchard''')
P.rep(r'''  if (kd == TK) return fight(u, k, kd, slot, spot, hand);   // 0.4.26: the Combat town
''', r'''  if (kd == TK) return fight(u, k, kd, slot, spot, hand);   // 0.4.26: the Combat town
  if (kd == RNK || kd == ORK) return gather(u, k, kd, slot, spot, hand);   // 0.4.28: the ranch / the orchard
''')
# Feed quality / Fruit yield = the Tree size purchase on a Ranching / Orchard island (same costs), its own maximum and words
P.rep(r'''  if (kd == TK && !@PKG@.ShCfg.TF_ON) return "-The Combat town is switched off on this server.";   // 0.4.26
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  String no = @PKG@.ShCore.gateOwn(u, k, kd, p);
  if (no != null) return no;
  int t0; int lv; long ver;''', r'''  if (kd == TK && !@PKG@.ShCfg.TF_ON) return "-The Combat town is switched off on this server.";   // 0.4.26
  if ((kd == RNK || kd == ORK) && !gatherOn(kd)) return kd == RNK ? "-The Ranching clicker is switched off on this server." : "-The Orchard clicker is switched off on this server.";   // 0.4.28
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  String no = @PKG@.ShCore.gateOwn(u, k, kd, p);
  if (no != null) return no;
  int t0; int lv; long ver;''')
P.rep(r'''  int mx = kd == MK ? @PKG@.ShCfg.MQ_NS_MAX : (kd == CRK ? @PKG@.ShCfg.FQ_NS_MAX : (kd == TK ? @PKG@.ShCfg.TF_NS_MAX : @PKG@.ShCfg.CK_NS_MAX));   // 0.4.24: Vein size on a Mining quarry; 0.4.25 Plot size; 0.4.26 Warrior strength
  if (lv >= mx) return kd == MK ? "=Vein size is at its highest level." : (kd == CRK ? "=Plot size is at its highest level." : (kd == TK ? "=Warrior strength is at its highest level." : "=Tree size is at its highest level."));''',
      r'''  int mx = kd == MK ? @PKG@.ShCfg.MQ_NS_MAX : (kd == CRK ? @PKG@.ShCfg.FQ_NS_MAX : (kd == TK ? @PKG@.ShCfg.TF_NS_MAX : (kd == RNK ? @PKG@.ShCfg.RQ_NS_MAX : (kd == ORK ? @PKG@.ShCfg.OQ_NS_MAX : @PKG@.ShCfg.CK_NS_MAX))));   // 0.4.24: Vein size on a Mining quarry; 0.4.25 Plot size; 0.4.26 Warrior strength; 0.4.28 Feed quality / Fruit yield
  if (lv >= mx) return kd == MK ? "=Vein size is at its highest level." : (kd == CRK ? "=Plot size is at its highest level." : (kd == TK ? "=Warrior strength is at its highest level." : (kd == RNK ? "=Feed quality is at its highest level." : (kd == ORK ? "=Fruit yield is at its highest level." : "=Tree size is at its highest level."))));''')
P.rep(r'''      : (kd == TK ? "+Warrior strength " + nl + "/" + mx + " in the " + @PKG@.ShIsl.tname(t0) + " town: your clicks hit +" + strPct(nl) + " %."''',
      r'''      : (kd == TK ? "+Warrior strength " + nl + "/" + mx + " in the " + @PKG@.ShIsl.tname(t0) + " town: your clicks hit +" + strPct(nl) + " %."
      : (kd == RNK ? "+Feed quality " + nl + "/" + mx + " on the " + @PKG@.ShIsl.tname(t0) + " island: " + rollsAt(kd, nl) + " drop rolls a tend."   // 0.4.28
      : (kd == ORK ? "+Fruit yield " + nl + "/" + mx + " on the " + @PKG@.ShIsl.tname(t0) + " island: " + rollsAt(kd, nl) + " fruit a pick."'''
      )
P.rep(r'''      : "+Tree size " + nl + "/" + mx + " on the " + @PKG@.ShIsl.tname(t0) + " island: " + logsAt(nl) + " logs a felled tree."));''',
      r'''      : "+Tree size " + nl + "/" + mx + " on the " + @PKG@.ShIsl.tname(t0) + " island: " + logsAt(nl) + " logs a felled tree."))));''')

# ---------------------------------------------------------------------------------------------------- 4. the per-profile migration (ShStore.migrate4)
P.rep('''M(st, "public static void migrate3(String k, java.util.Properties p) { }")   # 0.4.27: the body is set below (after ShMath) - the clicker migration
''', '''M(st, "public static void migrate3(String k, java.util.Properties p) { }")   # 0.4.27: the body is set below (after ShMath) - the clicker migration
M(st, "public static void migrate4(String k, java.util.Properties p) { }")   # 0.4.28: the body is set below (after ShMath) - the Ranching + Orchard clicker migration
F(st, "public static final java.util.concurrent.atomic.AtomicLong CLK2MIG = new java.util.concurrent.atomic.AtomicLong();")   # 0.4.28: files migrated
F(st, "public static final java.util.concurrent.atomic.AtomicLong CLK2CHK = new java.util.concurrent.atomic.AtomicLong();")   # 0.4.28: files checked, no Ranching / Orchard Shard
''')
P.rep('''    migrate3(k, p);   // 0.4.27: the clicker migration - automated shards' seed stores -> storage (marker clk.done=1)
''', '''    migrate3(k, p);   // 0.4.27: the clicker migration - automated shards' seed stores -> storage (marker clk.done=1)
    migrate4(k, p);   // 0.4.28: the Ranching + Orchard clicker migration - History copy, journal, automated stores -> storage (marker clk2.done=1)
''')
_a = P.s.index('M(st, r"""\npublic static String snapClk(String k) {')
_b = P.s.index('}""")\n', _a) + len('}""")\n')
_snap = P.s[_a:_b]
_snap2 = sub1(_snap, "public static String snapClk(String k) {", "public static String snapClk2(String k) {   // 0.4.28: = snapClk, the .pre-0.4.28 copy")
_snap2 = sub1(_snap2, 'String name = k + ".pre-0.4.27.properties";', 'String name = k + ".pre-0.4.28.properties";')
_snap2 = sub1(_snap2, 'name = k + ".pre-0.4.27." + System.currentTimeMillis() + ".properties";', 'name = k + ".pre-0.4.28." + System.currentTimeMillis() + ".properties";')
_snap2 = sub1(_snap2, '@PKG@.ShCfg.warnOnce("clksnap:" + k, "the 0.4.27 clicker migration copy of "', '@PKG@.ShCfg.warnOnce("clk2snap:" + k, "the 0.4.28 Ranching / Orchard clicker migration copy of "')
_snap2 = sub1(_snap2, '@PKG@.ShCfg.warnOnce("clksnapx:" + k, "the 0.4.27 clicker migration of "', '@PKG@.ShCfg.warnOnce("clk2snapx:" + k, "the 0.4.28 Ranching / Orchard clicker migration of "')
MIG4 = _snap2 + r'''st.getDeclaredMethod("migrate4").setBody(jv(r"""{
  String k = $1;
  java.util.Properties p = $2;
  if (p == null || k == null || "1".equals(p.getProperty("clk2.done"))) return;
  LOCK.lock();
  try {
    if ("1".equals(p.getProperty("clk2.done"))) return;
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
    long now = System.currentTimeMillis();
    StringBuilder ch = new StringBuilder();
    int isl = 0; int tot = 0; long items = 0L; long moved = 0L; boolean any = false;
    for (int kd = @RQK@; kd <= @OQK@; kd++) {
      if (!@PKG@.ShMath.owned(kd, p)) continue;
      any = true;
      boolean au = @PKG@.ShIsl.auto(kd, p);
      int ki = 0; int kt = 0; long kn = 0L;
      for (int s = 0; s < @PKG@.ShMath.SLOTS; s++) {
        if (!@PKG@.ShMath.hasIsland(kd, p, s)) continue;
        ki++;
        kt += @PKG@.ShTotem.entries(kd, p, s).length;
        kn += @PKG@.ShMath.usedOf(kd, p, s) + @PKG@.ShIsl.seeds(kd, p, s);
        if (!au) continue;
        long sd = @PKG@.ShIsl.seeds(kd, p, s);
        String id = @PKG@.ShIsl.SEED[@PKG@.ShIsl.ty(kd, p, s)];
        if (sd <= 0L || id == null || id.length() == 0) continue;
        @PKG@.ShMath.settle(kd, p, s, now);   // production up to now at the old numbers (an automated shard never takes seeds)
        long sd2 = @PKG@.ShIsl.seeds(kd, p, s);
        if (sd2 <= 0L) continue;
        java.util.LinkedHashMap m = @PKG@.ShMath.held(kd, p, s);
        Object o = m.get(id);
        m.put(id, Long.valueOf((o instanceof Long ? ((Long) o).longValue() : 0L) + sd2));
        @PKG@.ShMath.heldSet(kd, p, s, m);
        p.setProperty(@PKG@.ShIsl.ik(kd, s, "seed"), "0");
        moved += sd2;
        ch.append(", ").append(@PKG@.ShKind.KEYS[kd]).append(".i").append(s).append(' ').append(sd2).append(' ').append(id).append(" -> storage");
      }
      isl += ki; tot += kt; items += kn;
      ch.append(", ").append(@PKG@.ShKind.NAMES[kd]).append(": ").append(ki).append(" islands, ").append(kt).append(" totems, ").append(kn).append(" items");
    }
    if (!any) { p.setProperty("clk2.done", "1"); CLK2CHK.incrementAndGet(); return; }
    String snap = snapClk2(k);
    if (snap == null) { p.clear(); p.putAll(old); return; }
    p.setProperty("clk2.done", "1");
    String err = save(k, p);
    if (err != null) { p.clear(); p.putAll(old); @PKG@.ShCfg.warnOnce("clk2save:" + k, "the 0.4.28 Ranching / Orchard clicker migration of " + k + " is waiting (the file could not be saved: " + err + ")"); return; }
    CLK2MIG.incrementAndGet();
    log("ranching + orchard clicker migration (SkyyShards @VERSION@) " + k + ": carried over as they are" + ch.toString() + (moved > 0L ? " (" + moved + " seeds moved)" : "") + " - History copy " + snap + " - Undo: stop the server, copy it back over shards/" + k + ".properties and put SkyyShards 0.4.27 back");
    @PKG@.ShCfg.info("0.4.28 Ranching / Orchard clicker migration: " + k + " - " + isl + " islands, " + tot + " totems, " + items + " items carried over" + (moved > 0L ? ", " + moved + " seeds -> storage" : "") + " (collect.log has the Undo)");
  } finally { LOCK.unlock(); }
}""".replace("@RQK@", str(RQ_K)).replace("@OQK@", str(OQ_K))))
'''
_M3END = '''    @PKG@.ShCfg.info("0.4.27 clicker migration: " + k + " -" + ch.toString() + " (collect.log has the Undo)");
  } finally { LOCK.unlock(); }
}"""))
'''
P.rep(_M3END, _M3END + "# ================= 0.4.28 ShStore.migrate4 = THE RANCHING + ORCHARD CLICKER MIGRATION (tools/shards_0_4_28_patch.py; PROJECT-RULES 4): once per profile\n"
      "# file, marker clk2.done=1 - History copy first (byte-checked), automated Ranching / Orchard seed stores -> storage, one save, a collect.log journal line\n" + MIG4)

# ---------------------------------------------------------------------------------------------------- 5. the art (1x, pure Python, appended to CLK_ART_SRC)
RO_ART_SRC = r'''# 0.4.28 THE RANCHING + ORCHARD ART (tools/shards_0_4_28_patch.py): 8 animals + a hay bed, 8 fruit trees / bushes ripe + picked. Our own geometry, 1x
# (110 x 140, shipped as drawn: tools/ci/ui_budget.py). RART(keys) / OART(rows) -> {name: Pic}.
ANI_STY = {"chicken": ("#f4efe4", "#ffffff", "#b8ae98"), "cow": ("#f2efe8", "#ffffff", "#a8a49a"), "pig": ("#f0a2aa", "#ffd0d6", "#b0646e"),  # ui-data (picture colours)
           "boar": ("#6a4a32", "#a07a58", "#3a2616"), "sheep": ("#f4eedc", "#ffffff", "#bdb398"), "turkey": ("#7a4e2e", "#b07a4e", "#3e2414"),  # ui-data (picture colours)
           "goat": ("#d8d0c0", "#f6f0e4", "#8a8272"), "bison": ("#5a3a22", "#8a6040", "#2a1a0e")}  # ui-data (picture colours)
ANI_C = {"dark": "#2a1e14", "hoof": "#3a2a1e", "pink": "#f2a0a8", "comb": "#e0302a", "beak": "#f2b630", "horn": "#e8dcc0", "patch": "#2a2622",  # ui-data (picture colours)
         "grass": ("#4fa83a", "#8fd86a", "#2a6a22"), "hay": ("#e2c058", "#fff0a0", "#9a7a2a"), "eye": "#120a06"}  # ui-data (picture colours)


def _grass(pic, cx, by, u):
    ellipse(pic, cx + 2 * u, by + 1 * u, 40 * u, 6 * u, (10, 30, 12), 0.28)
    g = ANI_C["grass"]
    for i in range(9):
        x = cx + (i - 4) * 8 * u + (_hash(i, 3, 7) - 0.5) * 4 * u
        line(pic, x, by, x + (_hash(i, 4, 7) - 0.5) * 6 * u, by - (5 + 5 * _hash(i, 5, 7)) * u, 1.6 * u, _rgb(g[2] if i % 2 else g[0]))


def _quad(pic, cx, by, u, c, seed, body=(30, 15), lift=34, head=(13, 10), hx=26, hy=50, leg=5):
    for x in (-20, -11, 13, 22):
        line(pic, cx + x * u, by - lift * u, cx + (x + 1) * u, by, leg * u, _rgb(c[2]))
        line(pic, cx + (x + 1) * u, by - 3 * u, cx + (x + 1) * u, by, leg * u, _rgb(ANI_C["hoof"]))
    ellipse(pic, cx - 2 * u, by - (lift + body[1] * 0.4) * u, body[0] * u, body[1] * u, shade(c[0], c[1], c[2], cx - 10 * u, by - (lift + 10) * u, body[0] * u, ns=0.06, seed=seed))
    ellipse(pic, cx + hx * u, by - hy * u, head[0] * u, head[1] * u, shade(c[0], c[1], c[2], cx + (hx - 4) * u, by - (hy + 5) * u, head[0] * u, seed=seed + 1))
    disc(pic, cx + (hx + 3) * u, by - (hy + 3) * u, 1.8 * u, _rgb(ANI_C["eye"]))


def animal(key, W=110, H=140, s=1, seed=1):
    w, h = int(W * s), int(H * s)
    pic = Pic(w, h)
    u = float(s)
    cx, by = w / 2.0, h - 12.0 * u
    c = ANI_STY[key]
    _grass(pic, cx, by + 2 * u, u)
    if key in ("chicken", "turkey"):
        if key == "turkey":   # the fan tail behind
            for i in range(7):
                a = _m.radians(-160 + i * 22)
                tx, ty = cx - 12 * u + _m.cos(a) * 30 * u, by - 40 * u + _m.sin(a) * 30 * u
                ellipse(pic, (cx - 12 * u + tx) / 2.0, (by - 40 * u + ty) / 2.0, 7 * u, 17 * u, shade("#8a5a32", "#d8a070", "#4a2a12", tx, ty, 16 * u, seed=i), 0.95)  # ui-data (picture colours)
        for x in (-5, 5):
            line(pic, cx + x * u, by - 16 * u, cx + x * u, by, 2.2 * u, _rgb(ANI_C["beak"]))
        ellipse(pic, cx - 3 * u, by - 30 * u, 20 * u, 16 * u, shade(c[0], c[1], c[2], cx - 9 * u, by - 38 * u, 20 * u, ns=0.05, seed=seed))
        ellipse(pic, cx - 8 * u, by - 30 * u, 10 * u, 7 * u, shade(c[0], c[1], c[2], cx - 12 * u, by - 33 * u, 10 * u, seed=seed + 2), 0.9)
        disc(pic, cx + 14 * u, by - 50 * u, 8.5 * u, shade(c[0], c[1], c[2], cx + 11 * u, by - 53 * u, 9 * u, seed=seed + 1))
        poly(pic, [(cx + 21 * u, by - 52 * u), (cx + 29 * u, by - 49 * u), (cx + 21 * u, by - 46 * u)], _rgb(ANI_C["beak"]))
        if key == "chicken":
            for i, dx in enumerate((-4, 0, 4)):
                disc(pic, cx + (12 + dx) * u, by - (59 - abs(dx) * 0.3) * u, 3 * u, _rgb(ANI_C["comb"]))
        ellipse(pic, cx + 20 * u, by - 42 * u, 2.5 * u, 4.5 * u, _rgb(ANI_C["comb"]))
        disc(pic, cx + 16 * u, by - 52 * u, 1.6 * u, _rgb(ANI_C["eye"]))
        return pic
    if key == "sheep":
        _quad(pic, cx, by, u, ("#3a302a", "#6a5a50", "#1a1410"), seed, body=(24, 12), lift=30, head=(9, 9), hx=27, hy=46, leg=4)  # ui-data (picture colours)
        for i in range(14):
            a = _hash(i, 1, seed) * 2 * _m.pi
            d = _m.sqrt(_hash(i, 2, seed))
            disc(pic, cx - 2 * u + _m.cos(a) * d * 22 * u, by - 38 * u + _m.sin(a) * d * 11 * u, 8 * u, shade(c[0], c[1], c[2], cx - 8 * u, by - 46 * u, 26 * u, seed=i))
        disc(pic, cx + 30 * u, by - 49 * u, 1.6 * u, _rgb("#f0e8d8"))  # ui-data (picture colours)
        return pic
    if key == "bison":   # a big dark body, a shoulder hump, horns, a lowered head
        _quad(pic, cx, by, u, c, seed, body=(32, 17), lift=30, head=(14, 12), hx=28, hy=38, leg=6)
        ellipse(pic, cx + 8 * u, by - 58 * u, 18 * u, 14 * u, shade(c[0], c[1], c[2], cx + 2 * u, by - 64 * u, 18 * u, ns=0.08, seed=seed + 3))
        for d in (-1, 1):
            line(pic, cx + (24 + 6 * d) * u, by - 48 * u, cx + (24 + 12 * d) * u, by - 56 * u, 2.6 * u, _rgb(ANI_C["horn"]))
        return pic
    lift, head, hx, hy = 34, (13, 10), 26, 50
    if key == "pig":
        lift, head, hy = 22, (12, 10), 36
    if key == "boar":
        lift, head, hy = 26, (13, 10), 40
    if key == "goat":
        lift, head, hy = 36, (10, 9), 56
    _quad(pic, cx, by, u, c, seed, body=(28 if key != "goat" else 24, 14 if key != "goat" else 12), lift=lift, head=head, hx=hx, hy=hy, leg=5 if key != "goat" else 4)
    if key == "cow":
        for i, (px, py, r) in enumerate(((-14, 44, 7), (4, 40, 6), (-4, 50, 5), (14, 46, 4))):
            ellipse(pic, cx + px * u, by - py * u, r * u, r * 0.8 * u, _rgb(ANI_C["patch"]), 0.9)
        ellipse(pic, cx + (hx + 9) * u, by - (hy - 4) * u, 6 * u, 5 * u, _rgb(ANI_C["pink"]))
        for d in (-1, 1):
            line(pic, cx + (hx - 3 + 4 * d) * u, by - (hy + 8) * u, cx + (hx - 3 + 7 * d) * u, by - (hy + 14) * u, 2 * u, _rgb(ANI_C["horn"]))
    elif key in ("pig", "boar"):
        disc(pic, cx + (hx + 11) * u, by - (hy - 1) * u, 5 * u, _rgb(ANI_C["pink"] if key == "pig" else c[2]))
        for d in (-1.6, 1.6):
            disc(pic, cx + (hx + 11) * u, by - (hy - 1 + d) * u, 1 * u, _rgb(ANI_C["dark"]))
        if key == "pig":
            for i in range(4):
                a = _m.radians(i * 90)
                disc(pic, cx - 31 * u + _m.cos(a) * 2.5 * u, by - 31 * u + _m.sin(a) * 2.5 * u, 1.4 * u, _rgb(c[2]))
        else:
            line(pic, cx + (hx + 8) * u, by - (hy - 6) * u, cx + (hx + 13) * u, by - (hy + 1) * u, 2 * u, _rgb(ANI_C["horn"]))
            for i in range(8):
                x = cx - 22 * u + i * 6 * u
                line(pic, x, by - 43 * u, x + 2 * u, by - 49 * u, 2 * u, _rgb(c[2]))
    elif key == "goat":
        for d in (-1, 1):
            line(pic, cx + (hx - 2 + 2 * d) * u, by - (hy + 7) * u, cx + (hx - 9 + 3 * d) * u, by - (hy + 17) * u, 2.4 * u, _rgb("#9a8a70"))  # ui-data (picture colours)
        poly(pic, [(cx + (hx + 2) * u, by - (hy - 8) * u), (cx + (hx + 7) * u, by - (hy - 8) * u), (cx + (hx + 4) * u, by - (hy - 16) * u)], _rgb(c[2]))
    for d in (-1, 1):   # the ears
        ellipse(pic, cx + (hx - 6) * u, by - (hy + 8) * u + d * 2 * u, 4 * u, 2.4 * u, _rgb(c[2]), 0.9)
    return pic


def haybed(W=110, H=140, s=1):
    w, h = int(W * s), int(H * s)
    pic = Pic(w, h)
    u = float(s)
    cx, by = w / 2.0, h - 12.0 * u
    _grass(pic, cx, by + 2 * u, u)
    hy = ANI_C["hay"]
    ellipse(pic, cx, by - 8 * u, 34 * u, 11 * u, shade(hy[0], hy[1], hy[2], cx - 10 * u, by - 14 * u, 34 * u, ns=0.12, nsc=3, seed=4))
    for i in range(16):
        x = cx + (_hash(i, 1, 9) - 0.5) * 56 * u
        y = by - (4 + 10 * _hash(i, 2, 9)) * u
        a = (_hash(i, 3, 9) - 0.5) * 1.6
        line(pic, x, y, x + _m.cos(a) * 9 * u, y - _m.sin(a) * 4 * u, 1.1 * u, _rgb(hy[2] if i % 3 else hy[1]), 0.8)
    return pic


def _fruits(pic, col, seed, n=9, r=3.4, top=None):
    # fruit on the leafy part of a tree picture: deterministic spots where the canopy is solid
    w, h = pic.w, pic.h
    lim = top if top is not None else h * 0.62
    done = 0
    for i in range(400):
        if done >= n:
            break
        x = 12 + (w - 24) * _hash(i, 11, seed)
        y = 8 + (lim - 8) * _hash(i, 12, seed)
        k = (int(y) * w + int(x)) * 4
        if pic.c[k + 3] < 0.95:
            continue
        disc(pic, x + 0.6, y + 0.8, r, (20, 10, 6), 0.35)
        disc(pic, x, y, r, shade(col, "#ffffff", "#000000", x - r * 0.4, y - r * 0.4, r * 1.6))  # ui-data (picture colours)
        done += 1


def bush(W=110, H=140, s=1, seed=1, col=None):
    w, h = int(W * s), int(H * s)
    pic = Pic(w, h)
    u = float(s)
    cx, by = w / 2.0, h - 12.0 * u
    _grass(pic, cx, by + 2 * u, u)
    lf = ("#3f9a3a", "#86d070", "#1e5a1e")  # ui-data (picture colours)
    for i, (ox, oy, r) in enumerate(((-20, 14, 16), (18, 14, 16), (0, 22, 20), (-10, 34, 15), (12, 36, 14), (0, 46, 12))):
        ellipse(pic, cx + ox * u, by - oy * u, r * u, r * 0.8 * u, shade(lf[0], lf[1], lf[2], cx + (ox - 6) * u, by - (oy + 6) * u, r * 1.3 * u, ns=0.1, seed=seed + i))
    if col:
        _fruits(pic, col, seed, n=11, r=2.8, top=by - 6 * u)
    return pic


def OART(rows):
    # rows: [(key, tree tier or 0 = a bush, fruit colour)] -> OTree<i> (ripe) + OPick<i> (picked)
    out = {}
    for i, (key, tier, col) in enumerate(rows):
        if tier:
            ripe = tree(tier, 110, 140, s=1)
            _fruits(ripe, col, 50 + i, n=9, r=3.6 if key != "coconut" else 4.2)
            out["OTree%d" % i] = ripe
            out["OPick%d" % i] = tree(tier, 110, 140, s=1)
        else:
            out["OTree%d" % i] = bush(seed=60 + i, col=col)
            out["OPick%d" % i] = bush(seed=60 + i)
    return out


def RART(keys):
    out = {}
    for i, key in enumerate(keys):
        out["RAni%d" % i] = animal(key, seed=70 + i)
    out["RRest"] = haybed()
    return out


'''
P.rep('''def ART(tiers, sizes):
    # every picture of the clicker: {name: Pic}.''', RO_ART_SRC + '''def ART(tiers, sizes):
    # every picture of the clicker: {name: Pic}.''')
P.rep(r'''TF_NPIC = len(_t_pics)
assert TF_NPIC == len(TF_LOOKS) + 1 + 3 + 5 + 4, TF_NPIC
del _t_pics
''', r'''TF_NPIC = len(_t_pics)
assert TF_NPIC == len(TF_LOOKS) + 1 + 3 + 5 + 4, TF_NPIC
del _t_pics
# 0.4.28 THE RANCH'S + ORCHARD'S PICTURES (1x, shipped as drawn: Clk<Name>.png, no @2x - tools/ci/ui_budget.py): 8 animals + a hay bed, 8 fruit trees ripe + picked
O_TREE_T = {"apple": 2, "berries": 0, "coconut": 13, "mango": 14, "pinkberry": 0, "azure": 1, "spiral": 8, "windwillow": 12}   # 0 = a bush; else the 0.4.23 tree of that tier
O_FRUIT_C = {"apple": "#d8302a", "berries": "#c81e3a", "coconut": "#7a4a22", "mango": "#f2a030", "pinkberry": "#ff6ab0", "azure": "#3a8af0",  # ui-data (picture colours)
             "spiral": "#e0a0ff", "windwillow": "#c8e060"}  # ui-data (picture colours)
_ro_t0 = _time423.time()
_ro_pics = CLK_ART["RART"]([_t["key"] for _t in LAD[RQ_K]])
_ro_pics.update(CLK_ART["OART"]([(_t["key"], O_TREE_T[_t["key"]], O_FRUIT_C[_t["key"]]) for _t in LAD[OQ_K]]))
for _n, _pic in sorted(_ro_pics.items()):
    assert re.fullmatch(r"[A-Za-z0-9]+", _n) and _n not in CK_TEX and (_pic.w, _pic.h) == (110, 140), _n
    CK_TEX[_n] = MDIR + "Clk" + _n + ".png"
    SUI.register_map_textures([CK_TEX[_n]])
    MAP_ASSETS[MJAR + MDIR + "Clk" + _n + ".png"] = _pic.png()   # 1x
print("0.4.28 ranch + orchard art: %d pictures drawn in %.1f s (%d KB, 1x)" % (len(_ro_pics), _time423.time() - _ro_t0,
      sum(len(MAP_ASSETS[MJAR + MDIR + "Clk" + _n + ".png"]) for _n in _ro_pics) // 1024))
RO_NPIC = len(_ro_pics)
assert RO_NPIC == 8 + 1 + 8 + 8, RO_NPIC
del _ro_pics
RQ_UP_NAMES = ["Feed quality", "Herd size", "Spirit totem", "Water troughs", "Island size", "Decorations"]
RQ_UP_ICON = ["UpFSize", "UpFCount", "UpSpirit", "UpFIrr", "UpIsize", "UpDeco"]
OQ_UP_NAMES = ["Fruit yield", "Fruit trees", "Spirit totem", "Irrigation", "Island size", "Decorations"]
OQ_UP_ICON = ["UpNsize", "UpNcount", "UpSpirit", "UpFIrr", "UpIsize", "UpDeco"]
assert all(_i in CK_TEX for _i in RQ_UP_ICON + OQ_UP_ICON)
''')

# ---------------------------------------------------------------------------------------------------- 6. the page parts: the two maps, the rows, the Java branches
P.rep('''             "T": (TF_UP_NAMES, TF_UP_ICON)}
NUP_CW = None''', '''             "T": (TF_UP_NAMES, TF_UP_ICON),
             "R": (RQ_UP_NAMES, RQ_UP_ICON), "O": (OQ_UP_NAMES, OQ_UP_ICON)}   # 0.4.28: the ranch + the orchard
NUP_CW = None''')
RO_PAGE = r'''# ---- 0.4.28 THE RANCH + ORCHARD PAGE PARTS (tools/shards_0_4_28_patch.py): the animal / tree pictures (run time, per island) and the two maps (5 zone
# panels with the ladder's 3-a-zone cards M0..M7 - the 0.4.23 card ids, so the shared lock / Open / Buy segments fit; Zones 4-5 empty for now)
CK_PAGE_STATIC += ["public static final String[] R_ANI = new String[] { %s };" % ", ".join(jlit(CK_TEX["RAni%d" % _i]) for _i in range(len(LAD[RQ_K]))),
                   "public static final String[] R_REST = new String[] { %s };" % ", ".join(jlit(CK_TEX["RRest"]) for _i in range(len(LAD[RQ_K]))),
                   "public static final String[] O_TREE = new String[] { %s };" % ", ".join(jlit(CK_TEX["OTree%d" % _i]) for _i in range(len(LAD[OQ_K]))),
                   "public static final String[] O_PICK = new String[] { %s };" % ", ".join(jlit(CK_TEX["OPick%d" % _i]) for _i in range(len(LAD[OQ_K])))]
RO_MAPS = {"rmap": (RQ_K, "PENS", "RAni%d"), "omap": (OQ_K, "ORCHARDS", "OTree%d")}
RO_MAP_J = {}
for _seg, (_kd, _word, _pic) in sorted(RO_MAPS.items()):
    _ln = len(LAD[_kd])
    a_ = _ck_seg(_seg)
    a_.append((CK_BODY, G_.glass_group(CKP + "Map", CK_IW, CK_BODY_H, layout="Left")))
    for _z in range(5):
        Z_ = CKP + "Z%d" % _z
        a_.append(("#" + CKP + "Map", G_.glass_group(Z_, CK_ZW, CK_BODY_H, role="panel", layout="Top", pad=10, anchor={"right": 13} if _z < 4 else None)))
        a_.append(("#" + Z_, _ck_glab(Z_ + "N", 18, "gold", CK_CW, 30, bold=True, text="ZONE %d %s" % (_z + 1, _word))))
        a_.append(("#" + Z_, _ck_glab(Z_ + "S", 14, "dim", CK_CW, 24)))
        for _q in range(3):
            _i = 3 * _z + _q
            if _i >= _ln:
                break
            M_ = CKP + "M%d" % _i
            a_.append(("#" + Z_, G_.glass_group(M_, CK_CW, CK_CARD_H, role="inset", layout="Top", pad=6, anchor={"top": 6})))
            a_.append(("#" + M_, "Group #%sG { Anchor: (Width: %d, Height: 140); }" % (M_, CK_CW - 12)))
            a_.append(("#" + M_ + "G", SUI.map_pic(M_ + "P", (CK_CW - 12 - 110) // 2, 0, 110, 140, CK_TEX[_pic % _i])))
            a_.append(("#" + M_, _ck_glab(M_ + "N", 16, "title", CK_CW - 12, 22, bold=True)))
            a_.append(("#" + M_, _ck_wrap(M_ + "S", 13, "text", CK_CW - 12, 36)))
            a_.append(("#" + M_, G_.glass_group(M_ + "B", CK_CW - 12, 30, layout="Left")))
    j_ = [_qj(_seg)]
    for _i in range(_ln):
        j_ += ["  if (this.ckMLock[%d]) {" % _i, _qj("mlock%d" % _i), "  }",
               "  if (this.ckMB[%d] == 1) {" % _i, _qj("mopen%d" % _i), _ck_bind(CKP + "M%dX" % _i, '"km%d"' % _i),
               "  } else if (this.ckMB[%d] == 2) {" % _i, _qj("mbuy%d" % _i), _ck_bind(CKP + "M%dX" % _i, '"kb%d"' % _i), "  }",
               _ck_jset(CKP + "M%dN" % _i, "this.ckMN[%d]" % _i), _ck_jset(CKP + "M%dS" % _i, "this.ckMS[%d]" % _i)]
    for _z in range(5):
        j_.append(_ck_jset(CKP + "Z%dS" % _z, "this.ckZS[%d]" % _z))
    RO_MAP_J[_seg] = j_

'''
P.rep(r'''# the run-time templates (checked with samples)
_tex0 = CK_TEX["Tree1"]''', RO_PAGE + r'''# the run-time templates (checked with samples)
_tex0 = CK_TEX["Tree1"]''')
P.rep(r'''         _ck_jset(CKP + "Title", '(this.ckMine ? "MINING SHARD" : (this.ckFarm ? "FARMING SHARD" : (this.ckTown ? "COMBAT SHARD" : "FORAGING SHARD")))'),   # 0.4.25 / 0.4.26''',
      r'''         _ck_jset(CKP + "Title", '(this.ckMine ? "MINING SHARD" : (this.ckFarm ? "FARMING SHARD" : (this.ckTown ? "COMBAT SHARD" : (this.kind == @PKG@.ShClk.RNK ? "RANCHING SHARD" : (this.kind == @PKG@.ShClk.ORK ? "ORCHARD SHARD" : "FORAGING SHARD")))))'),   # 0.4.25 / 0.4.26 / 0.4.28''')
P.rep(r'''["  } else if (this.ckMode == 1 && this.ckMine) {"] + _QMAP_J + ["  } else if (this.ckMode == 1 && this.ckTown) {"] + _TMAP_J + [''',
      r'''["  } else if (this.ckMode == 1 && this.ckMine) {"] + _QMAP_J + ["  } else if (this.ckMode == 1 && this.ckTown) {"] + _TMAP_J + \
         ["  } else if (this.ckMode == 1 && this.kind == @PKG@.ShClk.RNK) {"] + RO_MAP_J["rmap"] + ["  } else if (this.ckMode == 1 && this.kind == @PKG@.ShClk.ORK) {"] + RO_MAP_J["omap"] + [   # 0.4.28''')
P.rep(r'''(!this.ckFarm || @PKG@.ShCfg.FQ_ON) && (!this.ckTown || @PKG@.ShCfg.TF_ON)) {''',
      r'''(!this.ckFarm || @PKG@.ShCfg.FQ_ON) && (!this.ckTown || @PKG@.ShCfg.TF_ON) && (this.kind != @PKG@.ShClk.RNK || @PKG@.ShCfg.RQ_ON) && (this.kind != @PKG@.ShClk.ORK || @PKG@.ShCfg.OQ_ON)) {''')
P.rep(r'''["  } else if (this.ckFarm) {"] + NUP_J["Fm"] + ["  } else if (this.ckTown) {"] + NUP_J["T"] + ["  } else {"] + NUP_J["F"] + ["  }"]''',
      r'''["  } else if (this.ckFarm) {"] + NUP_J["Fm"] + ["  } else if (this.ckTown) {"] + NUP_J["T"] + \
          ["  } else if (this.kind == @PKG@.ShClk.RNK) {"] + NUP_J["R"] + ["  } else if (this.kind == @PKG@.ShClk.ORK) {"] + NUP_J["O"] + ["  } else {"] + NUP_J["F"] + ["  }"]   # 0.4.28''')
# the variant checks of the two maps (every card locked + buyable / every card open)
P.rep(r'''print("0.4.27 clicker rows + upgrades view: %d variants checked, elements %s (+ run time: at most %d)" % (len(N_VARS), _n_el, N_ELEMENTS))
''', r'''print("0.4.27 clicker rows + upgrades view: %d variants checked, elements %s (+ run time: at most %d)" % (len(N_VARS), _n_el, N_ELEMENTS))
# 0.4.28 the ranch / orchard maps: every card locked + buyable, and every card open
RO_VARS = []
for _seg, (_kd, _w, _p) in sorted(RO_MAPS.items()):
    for _mode in ("lb", "open"):
        v_ = SUI.Appends()
        _names = ["frame", "mapb1", "frame2", _seg] + (["mlock%d" % _i for _i in range(len(LAD[_kd]))] + ["mbuy%d" % _i for _i in range(len(LAD[_kd]))]
                                                         if _mode == "lb" else ["mopen%d" % _i for _i in range(len(LAD[_kd]))]) + ["foot"]
        for _n in _names:
            v_.extend(CKA[_n])
        RO_VARS.append(v_)
for _i, v_ in enumerate(RO_VARS):
    v_.check(CKP)
    _pri = sum(1 for p_, mk_ in v_ if 'TexturePath: "SkyyGlass/Primary.png"' in SUI.render(mk_))   # ui-data: counting the Skyglass Primary buttons
    assert _pri <= 1, "0.4.28 ranch / orchard map variant %d: %d Primary buttons" % (_i, _pri)
SUI.assert_proven([mk_ for v_ in RO_VARS for p_, mk_ in v_], what="SkyyShards 0.4.28 Ranching / Orchard clicker maps")
SUI.assert_glass_paths([mk_ for v_ in RO_VARS for p_, mk_ in v_])
_ro_el = [sum(SUI._strip_quoted(SUI.render(mk_)).count("{") for p_, mk_ in v_) for v_ in RO_VARS]
assert max(_ro_el) < 1000, "0.4.28: the maps stay well under ~1,600 elements: %s" % _ro_el
print("0.4.28 ranch + orchard maps: %d variants checked, elements %s" % (len(RO_VARS), _ro_el))
''')

# ---------------------------------------------------------------------------------------------------- 7. the page: fillRanch / fillOrch (derived from fillFarm), dispatch, clicks
_FF0 = 'M(page, r"""\npublic void fillFarm(String k, @IC@[] cs, @REF@ ref, @ST@ st) {'
_i0 = P.s.index(_FF0) + len('M(page, r"""\n')
_FF = P.s[_i0:P.s.index('\n}""")\n', _i0)]
assert P.s.count(_FF0) == 1 and _FF.count("public void ") == 1 and "ckCostR(" in _FF


def _derive(name, kc, title, word):
    """fillFarm -> the ranch / orchard fill: its kind, pictures, words, rows; every swap asserted"""
    R = kc == "RNK"
    t = sub1(_FF, "public void fillFarm(String k, @IC@[] cs, @REF@ ref, @ST@ st) {   // 0.4.25: = fillClick for the Farming Shard (tools/shards_0_4_25_patch.py)",
             "public void %s(String k, @IC@[] cs, @REF@ ref, @ST@ st) {   // 0.4.28: = fillFarm for the %s Shard (tools/shards_0_4_28_patch.py)" % (name, title))
    t = sub1(t, "  this.kind = @PKG@.ShClk.CRK;\n", "  this.kind = @PKG@.ShClk.%s;\n" % kc)
    t = sub1(t, '  this.title = "Farming Shard";\n', '  this.title = "%s Shard";\n' % title)
    t = sub1(t, "  this.ckFarm = true;   // 0.4.25: the farm\n", "  this.ckFarm = false;   // 0.4.28: the %s clicker (the page reads this.kind)\n" % title)
    t = sub1(t, "  this.ckTree = F_CROP[0]; this.ckStump = F_HARV;\n", "  this.ckTree = %s[0]; this.ckStump = %s[0];\n" % (("R_ANI", "R_REST") if R else ("O_TREE", "O_PICK")))
    t = sub1(t, '  this.ckChip = "No farm yet";', '  this.ckChip = "%s";' % ("No pen yet" if R else "No orchard yet"))
    t = sub1(t, "  this.ckAxe = @PKG@.ShClk.hoeTier(this.ckHand);   // 0 = bare hands / no farming tool (a Crude hoe in the world's gate)\n",
             "  this.ckAxe = 0;   // 0.4.28: by hand, no tool gate\n")
    t = sub1(t, '''  this.ckInfo = (this.ckAxe > 0 ? "Harvesting with your " + @PKG@.ShTotem.pretty(this.ckHand) + " (T" + this.ckAxe + ")" : "Harvesting by hand (a Crude hoe) - hold a hoe or sickle for higher crops")
      + " - clicks give " + @PKG@.ShCfg.CK_XP_PCT + " % of world XP";
  if (!@PKG@.ShCfg.CK_ON || !@PKG@.ShCfg.FQ_ON) this.ckInfo = "The Farming clicker is switched off on this server.";
''', '''  this.ckInfo = "%s by hand - clicks give " + @PKG@.ShCfg.CK_XP_PCT + " %% of world XP";
  if (!@PKG@.ShCfg.CK_ON || !@PKG@.ShCfg.%s_ON) this.ckInfo = "The %s clicker is switched off on this server.";
''' % ("Tending your animals" if R else "Picking fruit", "RQ" if R else "OQ", title))
    t = sub1(t, '''    if (ti >= F_CROP.length) ti = F_CROP.length - 1;
    this.ckTree = F_CROP[ti]; this.ckStump = F_HARV;   // the island's crop plots; a harvested plot = sprouts while it regrows
''', '''    if (ti >= %s.length) ti = %s.length - 1;
    this.ckTree = %s[ti]; this.ckStump = %s[ti];   // 0.4.28: the island's %s; %s
''' % (("R_ANI", "R_ANI", "R_ANI", "R_REST", "animals", "a tended animal = its hay bed while it rests") if R else
       ("O_TREE", "O_TREE", "O_TREE", "O_PICK", "fruit trees", "a picked tree = the tree without fruit while it grows new fruit")))
    t = sub1(t, '''    this.ckCap = "Click a crop plot to harvest it (" + this.ckTn + " plots, " + @PKG@.ShClk.plantsAt(ns) + " plants a harvest). Your spirits keep working while you are away.";''',
             ('''    this.ckCap = "Click an animal to tend it (" + this.ckTn + " animals, " + @PKG@.ShClk.rollsAt(kd, ns) + " drop rolls a tend). Your spirits keep working while you are away.";''' if R else
              '''    this.ckCap = "Click a fruit tree to pick it (" + this.ckTn + " trees, " + @PKG@.ShClk.rollsAt(kd, ns) + " fruit a pick). Your spirits keep working while you are away.";'''))
    t = sub1(t, "    int mx = @PKG@.ShCfg.FQ_NS_MAX;\n", "    int mx = @PKG@.ShCfg.%s_NS_MAX;\n" % ("RQ" if R else "OQ"))
    w0 = "Drop rolls a tend" if R else "Fruit a pick"
    t = sub1(t, '''    if (ns >= mx) this.ckUpE[0] = "Plants a harvest: " + @PKG@.ShClk.plantsAt(ns) + " (highest)";
    else {
      this.ckUpE[0] = "Plants a harvest " + @PKG@.ShClk.plantsAt(ns) + " -> " + @PKG@.ShClk.plantsAt(ns + 1);''', '''    if (ns >= mx) this.ckUpE[0] = "%s: " + @PKG@.ShClk.rollsAt(kd, ns) + " (highest)";
    else {
      this.ckUpE[0] = "%s " + @PKG@.ShClk.rollsAt(kd, ns) + " -> " + @PKG@.ShClk.rollsAt(kd, ns + 1);''' % (w0, w0))
    t = sub1(t, '''this.ckUpE[1] = "Plots: " + this.ckTn''', '''this.ckUpE[1] = "%s: " + this.ckTn''' % ("Animals" if R else "Fruit trees"))
    t = sub1(t, '''this.ckUpE[1] = "Plots " + this.ckTn''', '''this.ckUpE[1] = "%s " + this.ckTn''' % ("Animals" if R else "Fruit trees"))
    t = sub1(t, '"Spirits farm for you, also while you are away"', '"%s"' % ("Spirits tend your herd, also while you are away" if R else "Spirits pick for you, also while you are away"))
    t = sub1(t, "@PKG@.ShClk.farmRegrowMs(", "@PKG@.ShClk.gatherRegrowMs(kd, ", 3)
    if R:
        t = sub1(t, '"Regrow ', '"Rest ', 2)
    t = sub1(t, '" -> " + ckSize(sz + 1) + ": room for " + @PKG@.ShIsl.tx(sz + 1).length + " plots";',
             '" -> " + ckSize(sz + 1) + ": room for " + @PKG@.ShIsl.tx(sz + 1).length + " %s";' % ("animals" if R else "trees"))
    t = sub1(t, '"First Plot count, Irrigation and Decorations 5/5 ("', '"First %s 5/5 ("' % ("Herd size, Water troughs and Decorations" if R else "Fruit trees, Irrigation and Decorations"))
    t = sub1(t, '} else this.ckCap = "No Farming island yet - open Islands to buy the first one.";', '} else this.ckCap = "No %s island yet - open Islands to buy the first one.";' % title)
    t = sub1(t, "    int tz = L0 + 3 * z;\n", '    if (3 * z >= LN) { this.ckZS[z] = "No %s in this zone yet"; continue; }   // 0.4.28: the ladder ends in Zone 3\n    int tz = L0 + 3 * z;\n' % word)
    assert "F_CROP" not in t and "hoeTier" not in t and "plantsAt" not in t and "FQ_" not in t and "farmRegrowMs" not in t and "Farming" not in t, "%s still names a farm part" % name
    return 'M(page, r"""\n' + t + '\n}""")\n'


RO_FILL = "# 0.4.28: the ranch's + the orchard's page fill = fillFarm with their kind, pictures, words and rows (tools/shards_0_4_28_patch.py)\n" + \
          _derive("fillRanch", "RNK", "Ranching", "pens") + _derive("fillOrch", "ORK", "Orchard", "orchards")
P.rep(_FF0, RO_FILL + _FF0)
P.rep('''    else if (this.kind == @PKG@.ShClk.TK) fillTown(k, cs, ref, st);   // 0.4.26
    else fillClick(k, cs, ref, st);   // 0.4.23''', '''    else if (this.kind == @PKG@.ShClk.TK) fillTown(k, cs, ref, st);   // 0.4.26
    else if (this.kind == @PKG@.ShClk.RNK) fillRanch(k, cs, ref, st);   // 0.4.28
    else if (this.kind == @PKG@.ShClk.ORK) fillOrch(k, cs, ref, st);   // 0.4.28
    else fillClick(k, cs, ref, st);   // 0.4.23''')
P.rep('''  int kd = this.kind == @PKG@.ShClk.CRK ? @PKG@.ShClk.CRK : (this.kind == @PKG@.ShClk.TK ? @PKG@.ShClk.TK : @PKG@.ShClk.FK);   // 0.4.25: the Farming clicker shares this page; 0.4.26 the Combat town''',
      '''  int kd = this.kind == @PKG@.ShClk.CRK ? @PKG@.ShClk.CRK : (this.kind == @PKG@.ShClk.TK ? @PKG@.ShClk.TK : (this.kind == @PKG@.ShClk.RNK ? @PKG@.ShClk.RNK : (this.kind == @PKG@.ShClk.ORK ? @PKG@.ShClk.ORK : @PKG@.ShClk.FK)));   // 0.4.25: the Farming clicker shares this page; 0.4.26 the Combat town; 0.4.28 the ranch + orchard''')
P.rep('''    if (kd == @PKG@.ShClk.TK && !townFresh(k, slot)) return "=The page is up to date now.";   // 0.4.26: a stale town
''', '''    if (kd == @PKG@.ShClk.TK && !townFresh(k, slot)) return "=The page is up to date now.";   // 0.4.26: a stale town
    if ((kd == @PKG@.ShClk.RNK || kd == @PKG@.ShClk.ORK) && !ckFresh(k, kd, slot)) return "=The page is up to date now.";   // 0.4.28: a stale ranch / orchard island
''')
P.rep('''    if (kd == @PKG@.ShClk.TK && !townFresh(k, s)) return "=The page is up to date now - click Upgrade again.";   // 0.4.26: a stale town
''', '''    if (kd == @PKG@.ShClk.TK && !townFresh(k, s)) return "=The page is up to date now - click Upgrade again.";   // 0.4.26: a stale town
    if ((kd == @PKG@.ShClk.RNK || kd == @PKG@.ShClk.ORK) && !ckFresh(k, kd, s)) return "=The page is up to date now - click Upgrade again.";   // 0.4.28: a stale ranch / orchard island
''')

# ---------------------------------------------------------------------------------------------------- 8. IMAGE SHRINK part 3: the old Map tab of Ranching / Orchard goes too
P.rep('''_CKK427 = [KINDS[_k] for _k in range(NK) if KINDS[_k] in ("Mining", "Foraging", "Farming", "Combat")]
assert len(_CKK427) == 4
''', '''_CKK427 = [KINDS[_k] for _k in range(NK) if KINDS[_k] in ("Mining", "Foraging", "Farming", "Combat", "Ranching", "Orchard")]   # 0.4.28: + Ranching, Orchard (their old menu never opens)
assert len(_CKK427) == 6
''')
P.rep('''_half427 = [MJAR + MDIR + "Base%s@2x.png" % _k for _k in ("Ranching", "Orchard")] + \\
           sorted(_p for _p in MAP_ASSETS if re.fullmatch(re.escape(MJAR + MDIR) + r"Clk(Map|FMap|QMap|TMap)\\d+@2x\\.png", _p))
assert len(_half427) == 2 + 15 + 15 + len(MQ_LAD) + 5, len(_half427)''', '''_half427 = sorted(_p for _p in MAP_ASSETS if re.fullmatch(re.escape(MJAR + MDIR) + r"Clk(Map|FMap|QMap|TMap)\\d+@2x\\.png", _p))   # 0.4.28: no Ranching / Orchard Map bases any more
assert len(_half427) == 15 + 15 + len(MQ_LAD) + 5, len(_half427)''')

P.rep("pg.stText = lk; pg.stCol = \"@BAD@\";   // Ranching / Orchard: their old menu, the lock line on it",
      "pg.stText = lk; pg.stCol = \"@BAD@\";   // a kind without a clicker (none since 0.4.28): the lock line on its old menu")   # fix (critic): stale comment
# ---------------------------------------------------------------------------------------------------- 9. the ready line
P.rep(r'''log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.27:''', r'''log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.28: the Ranching + Orchard clickers (the portal opens them: tend animals / pick fruit trees by hand, one island per animal / fruit in zone clusters, Feed quality / Fruit yield, zone locks; every shard is clicker-only now); 0.4.27:''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
_i = P.s.index
assert _i("public static boolean ownSeed(") < _i("public static long enchX(") < _i("public static String tok(") < _i("public static Object[] mats("), "enchX before tok / mats"
assert _i("public static Object[] gather(java.util.UUID u") < _i("public static Object[] chop(java.util.UUID u"), "gather() compiled before chop()"
assert _i("public static double fortuneOf(") < _i("public static Object[] gather(java.util.UUID u"), "fortuneOf before gather"
assert _i("public static void part(StringBuilder sb") < _i("public static Object[] gather(java.util.UUID u"), "part / addTo / rnd before gather"
assert _i("public static long rollsAt(int kd, int ns)") < _i("public static String buyNode("), "rollsAt before buyNode"
assert _i("public static boolean gatherOn(int kd)") < _i("public static String buyNode("), "gatherOn before buyNode"
assert _i("public void fillRanch(") < _i("public void fillOrch(") < _i("public void build0("), "the fills before build0"
assert _i("public boolean ckFresh(") < _i("public String actClick("), "ckFresh before actClick"
assert _i("public static String snapClk2(") < _i('st.getDeclaredMethod("migrate4")'), "snapClk2 before migrate4's body"
P.finish()
