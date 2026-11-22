"""Derive SkyyShards/build_skyyshards_0.4.26.py from the GENERATED SkyyShards 0.4.25 (build_skyyshards_0.4.25.py = the tools/deploy_set.py SET
pin, made by tools/shards_0_4_25_patch.py - edit the patch, never the generated file). Every anchor is asserted once; at the end every change
is undone on a copy and compared with 0.4.25 (tools/soundpass_gen.Patch). Line endings kept.
Run:   python tools/shards_0_4_26_patch.py   then   python SkyyShards/build_skyyshards_0.4.26.py   (never --deploy)
Check: python SkyyShards/test_skyyshards_0.4.26.py

0.4.26 (2026-11-21) = SHARD CLICKER 4: THE COMBAT TOWN DEFENSE (round fight1; Skyy 2026-11-14 docs/answered/world.md "COMBAT SHARD = TOWN DEFENSE":
  "combat will be more of a town defense, so you have this little town and some spirit wariors to defend it, you upgrade toyr wariers to make them
  stronger, kill and move faster, then you upgrade the town to attract more monsters, and more kinds of monsters. so it starts by attracting rats, then
  wolves and skeletons, then bears and the big skeletons and trolls and so on. starting with the easiest zone 1 mobs and working up to the hardest. (but
  at max all the kinds of mobs attack at once so it collects all their loot.)"; "(have zone locks for all the shards."; research/Shard-Clicker-Idea.md
  "Combat = town defense"; Skyy 2026-11-21 "build and deploy everything on your list"). Reuses the 0.4.23 clicker page and machinery whole (view 5, the
  island scene, ShClk.hit / tick / accXp, the six upgrade rows, the store grid, Server Setup rows) like 0.4.25 did; today's Combat Shard (0.4.11: one
  island per zone, mobs spawn while you are there, the Soul Cage pool) is unchanged - the town is its "Shard clicker" page.
  SPEC (short; the survey first):
  - SURVEY. Vanilla (Assets.zip): no clicker; the monsters = the zone pools the Combat Shard already uses (CZ_POOL: vanilla roles checked against each
    zone's own spawn files, 0.4.11) + Trork_Warrior for Zone 1 (Skyy's "trolls": vanilla's Trork, in Server/NPC/Spawn/Beacons/Zone1); each role's
    vanilla MaxHealth (Server/NPC/Roles, Modify.MaxHealth or its Reference) = the DIFFICULTY ORDER (Zone 1: Rat 10 ... Golem / Praetorian 224+) and
    its loot = its vanilla DropList on average (0.4.11's _cz_ev; armor / weapons / tools left out). Mods: the 0.4.23 survey (pie-clicker, learn
    only); SkyyMobs adds no new roles to the zone pools. Approved art: none for the town (grep 'town' research/ui-theme-art) - the build draws its own.
  - 1. THE TOWN = view 5 of the Combat Shard's page (its footer's "Shard clicker"): one town per ZONE island (Zone 1..5, the islands you own). Its
    monsters stand on the island's spots: Monsters at once = the world's own Mobs at once table (combat.cap, ShCombat.cap(size, level)), at most the
    spots of that town size. A monster = a kind of the zone's pool in DIFFICULTY ORDER: Town level (= (size - 1) x 5 + the Mobs at once purchase,
    0..15) opens the first ceil(kinds x (level + 1) / 16) kinds (Zone 1: rats first); at Town level 15 (Large, 5 / 5) EVERY kind attacks AT ONCE
    (fixer: a maxed town gets one spot per kind when the zone has more kinds than Mobs at once - Zones 1-3 have 20-22 - on the island's free spots). Clicking a monster = the weapon in your hand: its tier (tools/tier_tags.py weapons, else
    the best metal word) against the zone's monster tier (click.fight.zoneTier 1 / 4 / 7 / 10 / 13) through the SAME damage rule as the other
    clickers (ShClk.dmg: normal / one tier up click.oneTierUp / two up click.twoTierUp / three up = refused); Warrior strength adds
    click.fight.strengthPct (20) % a level. A monster takes click.fight.hp (6) x (1 + click.fight.hpStep (10) % x its place in the zone's order)
    damage. click.maxPerSec counted clicks a second (shared cap). A slain monster's place fills again after click.fight.respawnPct (40) % of the
    world's respawn time for that town (combat.respawn, Spawn speed), at least click.fight.minRespawnSec (2) s (memory only, like a tree's regrow).
  - 2. THE LOOT goes into the town's .drops (the Combat island's rolled-drops store, saved at once, counted against its storage; Collect / a grid
    cell / Collect all already pay it, collection credit, no XP at Collect): that monster's vanilla drops - each item's average a kill, the whole
    part always + one more at the rest's chance; combat.cageSkip items left out (click.fight.cageSkip, on: Void Essence / ores / bars stay a world
    fight's reward, as for the Soul Cage); a kind with no vanilla drops = 1 of the zone's common drop. What does not fit: the rarest first.
    XP: click.xpPercent (25) % of the world's class XP of that kill = its vanilla health x click.fight.xpPerHp (60 / 100 = SkyySkills combat.perHealth
    0.2 x the class skill's x3) x the level factor 1 + 0.13 (L - 1) + 0.004 (L - 1)^2 (combat.levelCurve) at the town's monster level (the owner's
    level when combat.levelWithPlayer, + Monster level); paid to the player's ACTIVE CLASS skill through skill:fn:addxp (no class = no XP). Fixer: XP SkyySkills
    refuses (its default bridge.addxp.skills lists no class skill) is NOT banked as owed XP: the kill and the page say so (an admin can add
    Combat.<Class> to that row), and that player's class is not asked again for 60 s (memory only). The spirit warriors (Soul Cages) keep killing while you are away: the existing Combat
    output (0 XP, Skyy G9) - unchanged.
  - 3. THE SIX UPGRADES (the 0.4.23 rows, Combat words + icons; every one but the first = an existing Combat purchase at its Map tab cost):
    Warrior strength = <kind>.i<n>.nsize (NEW, the Tree size purchase + its cost rows: coins + the town's Enchanted item, Zone 1 = Enchanted Bone), Town level = Mobs at once,
    Spirit warriors = the Totems tab (Soul Cages: kill speed while away), Warrior speed = Spawn speed (the Soul Cages kill faster while away + monsters arrive faster), Town size = Grow
    (more kinds, more at once), Monster level = Mob level (more loot + XP). A button carries the level the page showed: a double click buys once;
    a stale town (profile switch / another zone in that slot) is refused ("the page is up to date now").
  - 4. COMBAT ZONE LOCKS: already there since 0.4.11 (combat.zoneLevel.2..5 = class level 20 / 40 / 60 / 80, asked by buyIsland - the Map tab and the
    town map); the town map shows them (Locked: class level N); a town you own stays yours and playable.
  - 5. FIX (known bug): the Foraging and Mining clickers kept their damage / regrow memory under <profile>|<slot> and their XP fractions under
    <uuid>|<profile> - shared across shard kinds (a Foraging tree and a Mining node in the same slot number shared one damage array). Now
    <profile>|<kind>|<slot> and <uuid>|<profile>|<kind> like Farming (memory only: no saved-data change; a restart already cleared it).
  NUMBERS (new, Server Setup -> Shards -> Shard clicker; all editable): click.fight.enabled true, click.fight.hp 6, click.fight.hpStep 10,
    click.fight.strengthPct 20, click.fight.sizeMax 10, click.fight.respawnPct 40, click.fight.minRespawnSec 2, click.fight.xpPerHp 60,
    click.fight.cageSkip true, click.fight.zoneTier 1,4,7,10,13. Copied (not new): Mobs at once / Spawn speed / Mob level / zone lock tables
    (combat.*), the Tree size coin + Enchanted table for Warrior strength (the Combat island's Enchanted item, ShIsl.tok "ench"), the Map tab costs, the vanilla
    health + drops, the shared click rows (maxPerSec, xpPercent, oneTierUp, twoTierUp, tierStep).
  ART: the build draws its own (TART_SRC, appended to CLK_ART_SRC): monsters by family + tint (rat, wolf, bear, skeleton, big skeleton, spider, snake,
    goblin, trork, golem, zombie, wisp x plain / frost / fire / sand / void / bone / swamp), a slain monster (bones + a grave), 3 town islands
    (houses + a watch tower), 5 map towns, 4 upgrade icons -> Common/UI/Custom/SkyyShards/Map/ClkT*@2x.png + ClkUpT*@2x.png. Spirit totems = 0.4.23's
    totem + spirit pictures.
  SAVED DATA: combat.i<n>.nsize (Warrior strength, missing = 0) - new; combat.i<n>.drops (0.4.22's rolled-drops store) now also holds click loot;
    (fixer: no owed.xp.<class skill> - refused class XP is not banked). Old files load unchanged; no migration.
  ROLLBACK 0.4.26 -> 0.4.25 alone: no migration. 0.4.25 ignores combat nsize (kept in the file) and its Combat Collect pays .drops (0.4.22), so click
    loot still pays out; the town page disappears. The memory-key fix only changes memory.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

HERE = os.path.join(ROOT, "SkyyShards")
P = G.Patch(os.path.join(HERE, "build_skyyshards_0.4.25.py"), os.path.join(HERE, "build_skyyshards_0.4.26.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.4.25"\n') and P.has("GENERATED by tools/shards_0_4_25_patch.py") and P.has("fillFarm") and not P.has("fillTown"), "not the generated SkyyShards 0.4.25"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.26 (2026-11-21)"):].rstrip() + "\n"


def sub1(txt, old, new, n=1):
    """replace old in txt; it must occur exactly n times"""
    c = txt.count(old)
    assert c == n, "fillTown anchor count %d (want %d): %s" % (c, n, old[:160])
    return txt.replace(old, new)


# ---------------------------------------------------------------------------------------------------- 0. header + version
P.rep('''"""SkyyShards 0.4.25 - build script (javassist via jpype). GENERATED by tools/shards_0_4_25_patch.py from build_skyyshards_0.4.24.py
(generated by tools/shards_0_4_24_patch.py from 0.4.23, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.25" /''', '''"""SkyyShards 0.4.26 - build script (javassist via jpype). GENERATED by tools/shards_0_4_26_patch.py from build_skyyshards_0.4.25.py
(generated by tools/shards_0_4_25_patch.py from 0.4.24, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.26" / "0.4.25" /''')
P.rep('''Run:   python SkyyShards/build_skyyshards_0.4.25.py   -> SkyyShards/SkyyShards-0.4.25.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.25.py
''', '''Run:   python SkyyShards/build_skyyshards_0.4.26.py   -> SkyyShards/SkyyShards-0.4.26.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.26.py
''' + NOTE + '''
''')
P.rep('VERSION = "0.4.25"\n', 'VERSION = "0.4.26"\n')

# ---------------------------------------------------------------------------------------------------- 1. ShCfg: the town's settings
P.rep(r'''          "public static volatile int[] FQ_ZLV = new int[] { %s };" % ", ".join(str(_x) for _x in FQ_ZLV)):
    F(cfg, f)
''', r'''          "public static volatile int[] FQ_ZLV = new int[] { %s };" % ", ".join(str(_x) for _x in FQ_ZLV)):
    F(cfg, f)
# 0.4.26 THE COMBAT TOWN (tools/shards_0_4_26_patch.py): its settings (Server Setup -> Shards -> Shard clicker, rows click.fight.*)
TF_K = KINDS.index("Combat")
TF_ZT = [1, 4, 7, 10, 13]          # the weapon tier a zone's monsters count as (the zone's first metal tier: Copper 1, Thorium 4, Cobalt 7, Adamantite 10, Mithril 13)
assert TF_K == 5 and len(TF_ZT) == 5
for f in ("public static volatile boolean TF_ON = true;", "public static volatile int TF_HP = 6;", "public static volatile int TF_HPSTEP = 10;",
          "public static volatile int TF_STR = 20;", "public static volatile int TF_NS_MAX = 10;", "public static volatile int TF_RSP = 40;",
          "public static volatile int TF_RMIN = 2;", "public static volatile int TF_XPHP = 60;", "public static volatile boolean TF_SKIP = true;",
          "public static final int[] DEF_TF_ZT = new int[] { %s };" % ", ".join(str(_x) for _x in TF_ZT),
          "public static volatile int[] TF_ZT = new int[] { %s };" % ", ".join(str(_x) for _x in TF_ZT)):
    F(cfg, f)
''')
P.rep(r'''          "5 numbers, Zone 1..5: Farming islands of a zone are bought from this Farming level.", "reload@config.properties:click.farm.zoneLevel")]
''', r'''          "5 numbers, Zone 1..5: Farming islands of a zone are bought from this Farming level.", "reload@config.properties:click.farm.zoneLevel")]
# 0.4.26: the Combat town's rows
ROWS += [("click.fight.enabled", "Combat town (clicker)", "clicker", "bool", "true", "", "", "", "", "live",
          "Off: the Combat Shard menu shows no town and clicks do nothing. Nothing is deleted.", "reload@config.properties:click.fight.enabled"),
         ("click.fight.hp", "Town: clicks for the easiest monster", "clicker", "int", "6", "1", "1000", "", "", "live",
          "Damage the zone's easiest monster takes (1 click = 1 with a weapon of the zone's tier).", "reload@config.properties:click.fight.hp"),
         ("click.fight.hpStep", "Town: more clicks per harder kind", "clicker", "int", "10", "0", "1000", "", "%", "live",
          "Each kind further up the zone's order (vanilla health) takes this much more damage.", "reload@config.properties:click.fight.hpStep"),
         ("click.fight.strengthPct", "Town: Warrior strength a level", "clicker", "int", "20", "0", "1000", "", "%", "live",
          "Each Warrior strength level adds this much to every click's damage.", "reload@config.properties:click.fight.strengthPct"),
         ("click.fight.sizeMax", "Town: Warrior strength levels", "clicker", "int", "10", "0", "10", "", "", "live",
          "The highest Warrior strength level (costs: the Tree size rows, coins + the town's Enchanted item).", "reload@config.properties:click.fight.sizeMax"),
         ("click.fight.respawnPct", "Town: next monster after", "clicker", "int", "40", "1", "1000", "", "%", "live",
          "Share of the island's world respawn time (Spawn speed) before a slain monster's place fills again.", "reload@config.properties:click.fight.respawnPct"),
         ("click.fight.minRespawnSec", "Town: shortest wait", "clicker", "int", "2", "0", "3600", "", "s", "live",
          "A new monster never comes faster than this.", "reload@config.properties:click.fight.minRespawnSec"),
         ("click.fight.xpPerHp", "Town: world XP per 100 health", "clicker", "int", "60", "0", "10000", "", "", "live",
          "Class XP of a kill per 100 vanilla health, before its level (clicks pay click.xpPercent).", "reload@config.properties:click.fight.xpPerHp"),
         ("click.fight.cageSkip", "Town: no Soul Cage-skipped loot", "clicker", "bool", "true", "", "", "", "", "live",
          "On: click kills leave out combat.cageSkip items (Void Essence, ores, bars), like the Soul Cage.", "reload@config.properties:click.fight.cageSkip"),
         ("click.fight.zoneTier", "Town: monster tier by zone", "clicker", "text", ",".join(str(_x) for _x in TF_ZT), "", "60", "", "", "live",
          "5 numbers, Zone 1..5: the weapon tier a zone's monsters count as (3 tiers above yours = refused).", "reload@config.properties:click.fight.zoneTier")]
''')
P.rep(r'''          "  FQ_ZLV = intsOf(p.getProperty(\"click.farm.zoneLevel\"), DEF_FQ_ZLV, 0, 1000, \"click.farm.zoneLevel\");"]
''', r'''          "  FQ_ZLV = intsOf(p.getProperty(\"click.farm.zoneLevel\"), DEF_FQ_ZLV, 0, 1000, \"click.farm.zoneLevel\");"]
_load += ["  TF_ON = bool(p.getProperty(\"click.fight.enabled\"), true);",   # 0.4.26 the Combat town
          "  TF_HP = intOf(p.getProperty(\"click.fight.hp\"), 6, 1, 1000);",
          "  TF_HPSTEP = intOf(p.getProperty(\"click.fight.hpStep\"), 10, 0, 1000);",
          "  TF_STR = intOf(p.getProperty(\"click.fight.strengthPct\"), 20, 0, 1000);",
          "  TF_NS_MAX = intOf(p.getProperty(\"click.fight.sizeMax\"), 10, 0, 10);",
          "  TF_RSP = intOf(p.getProperty(\"click.fight.respawnPct\"), 40, 1, 1000);",
          "  TF_RMIN = intOf(p.getProperty(\"click.fight.minRespawnSec\"), 2, 0, 3600);",
          "  TF_XPHP = intOf(p.getProperty(\"click.fight.xpPerHp\"), 60, 0, 10000);",
          "  TF_SKIP = bool(p.getProperty(\"click.fight.cageSkip\"), true);",
          "  TF_ZT = intsOf(p.getProperty(\"click.fight.zoneTier\"), DEF_TF_ZT, 1, 20, \"click.fight.zoneTier\");"]
''')

# ---------------------------------------------------------------------------------------------------- 2. FIX: the Foraging / Mining memory per kind
# (a tree / node's damage + regrow and the XP fractions were keyed <profile>|<slot> / <uuid>|<profile> for every kind: now <profile>|<kind>|<slot> /
# <uuid>|<profile>|<kind>, like Farming; memory only)
P.rep('''  String key = k + "|" + slot;
  double hpMax = (double) @PKG@.ShCfg.MQ_HP;''', '''  String key = k + "|" + kd + "|" + slot;   // 0.4.26 fix: the quarry's own node memory (was <profile>|<slot>, shared with the other kinds)
  double hpMax = (double) @PKG@.ShCfg.MQ_HP;''')
P.rep('''  long xp = accXp(String.valueOf(u) + "|" + @PKG@.ShCfg.pkey(u), (double) paid * (double) @PKG@.ShCfg.xpOf(kd) * (double) @PKG@.ShCfg.CK_XP_PCT / 100.0);
  String xt = "";
  if (xp > 0L) { long xl = @PKG@.ShCore.owedXp(u, skill, xp); xt = xl > 0L ? " (" + @PKG@.ShCfg.num(xl) + " " + skill + " XP waits)" : " +" + @PKG@.ShCfg.num(xp) + " " + skill + " XP"; }
  StringBuilder sb = new StringBuilder();
  part(sb, gO, oreOut);''', '''  long xp = accXp(String.valueOf(u) + "|" + @PKG@.ShCfg.pkey(u) + "|" + kd, (double) paid * (double) @PKG@.ShCfg.xpOf(kd) * (double) @PKG@.ShCfg.CK_XP_PCT / 100.0);   // 0.4.26 fix: Mining's own XP fractions
  String xt = "";
  if (xp > 0L) { long xl = @PKG@.ShCore.owedXp(u, skill, xp); xt = xl > 0L ? " (" + @PKG@.ShCfg.num(xl) + " " + skill + " XP waits)" : " +" + @PKG@.ShCfg.num(xp) + " " + skill + " XP"; }
  StringBuilder sb = new StringBuilder();
  part(sb, gO, oreOut);''')
P.rep('''  String key = k + "|" + slot;
  double hpMax = (double) @PKG@.ShCfg.CK_HP;''', '''  String key = k + "|" + kd + "|" + slot;   // 0.4.26 fix: Foraging's own tree memory (was <profile>|<slot>, shared with the other kinds)
  double hpMax = (double) @PKG@.ShCfg.CK_HP;''')
P.rep('''  long xp = accXp(String.valueOf(u) + "|" + @PKG@.ShCfg.pkey(u), (double) paid * (double) @PKG@.ShCfg.xpOf(kd) * (double) @PKG@.ShCfg.CK_XP_PCT / 100.0);
  String xt = "";
  if (xp > 0L) { long xl = @PKG@.ShCore.owedXp(u, skill, xp); xt = xl > 0L ? " (" + @PKG@.ShCfg.num(xl) + " " + skill + " XP waits)" : " +" + @PKG@.ShCfg.num(xp) + " " + skill + " XP"; }
  String nm = @PKG@.ShTotem.pretty(block);''', '''  long xp = accXp(String.valueOf(u) + "|" + @PKG@.ShCfg.pkey(u) + "|" + kd, (double) paid * (double) @PKG@.ShCfg.xpOf(kd) * (double) @PKG@.ShCfg.CK_XP_PCT / 100.0);   // 0.4.26 fix: Foraging's own XP fractions
  String xt = "";
  if (xp > 0L) { long xl = @PKG@.ShCore.owedXp(u, skill, xp); xt = xl > 0L ? " (" + @PKG@.ShCfg.num(xl) + " " + skill + " XP waits)" : " +" + @PKG@.ShCfg.num(xp) + " " + skill + " XP"; }
  String nm = @PKG@.ShTotem.pretty(block);''')
# the pages read the same per-kind keys (the regrowing pictures): fillQuarry + fillClick (fillFarm already had <profile>|<kind>|<slot>)
P.rep('''    String key2 = k + "|" + this.ckSlot;
    for (int i = 0; i < this.ckTn; i++) {
      int oi = ores[i % ores.length] - L0;''', '''    String key2 = k + "|" + kd + "|" + this.ckSlot;   // 0.4.26 fix: per kind (= ShClk.mine)
    for (int i = 0; i < this.ckTn; i++) {
      int oi = ores[i % ores.length] - L0;''')
P.rep('''    String key2 = k + "|" + this.ckSlot;
    for (int i = 0; i < this.ckTn; i++) this.ckGrow[i] = @PKG@.ShClk.readyAt(key2, i) > now;''', '''    String key2 = k + "|" + kd + "|" + this.ckSlot;   // 0.4.26 fix: per kind (= ShClk.chop)
    for (int i = 0; i < this.ckTn; i++) this.ckGrow[i] = @PKG@.ShClk.readyAt(key2, i) > now;''')

# ---------------------------------------------------------------------------------------------------- 3. ShClk: THE TOWN (tables, the fight click)
TOWN_CLK = r'''# ---- 0.4.26 THE COMBAT TOWN (tools/shards_0_4_26_patch.py): one town per Combat zone island; its monsters = the zone's pool kinds in DIFFICULTY ORDER
# (vanilla health), Town level opens them easiest first (all at Town level 15); a click = the weapon in hand through the clickers' damage rule (ShClk.dmg)
# + Warrior strength; a kill = that monster's vanilla loot into the island's .drops (saved at once) + click.xpPercent of the world's class XP.
TF_EXTRA = [["Trork_Warrior"], [], [], [], []]   # Skyy's "trolls" for Zone 1 = vanilla's Trork (Server/NPC/Spawn/Beacons/Zone1)


def _tf_hp(r, depth=0):
    _j = json.loads(AZ.read(_CZ_ROLES[r]).decode("utf-8-sig"))
    for _v in ((_j.get("Modify") or {}).get("MaxHealth"), _j.get("MaxHealth")):
        if isinstance(_v, (int, float)) and _v > 0:
            return int(_v)
    _ref = _j.get("Reference")
    if depth < 4 and isinstance(_ref, str) and _ref in _CZ_ROLES:
        return _tf_hp(_ref, depth + 1)
    return 100


def _tf_look(r, hp):
    """the picture of a role: (family, tint) by its name words (our own drawings)"""
    w = r.split("_")
    fam = None
    for _ks, _f in ((("Rat", "Larva"), "rat"), (("Wolf", "Hyena", "Hound", "Emberwulf", "Leopard", "Tiger", "Raptor"), "wolf"),
                    (("Bear", "Toad", "Crocodile", "Rex"), "bear"), (("Spider", "Scorpion", "Scarak", "Crawler"), "spider"),
                    (("Snake", "Fen", "Snapdragon"), "snake"), (("Goblin", "Cactee", "Outlander"), "goblin"), (("Trork",), "troll"),
                    (("Golem",), "golem"), (("Zombie",), "zombie"), (("Eye", "Spectre", "Wraith", "Spark", "Head"), "wisp")):
        if any(_k in w for _k in _ks):
            fam = _f
            break
    if fam is None and w[0] == "Skeleton":
        fam = "bigskel" if hp >= 100 else "skel"
    fam = fam or "goblin"
    tint = "plain"
    for _ks, _t in ((("Frost", "White", "Polar", "Snow"), "frost"), (("Burnt", "Incandescent", "Magma", "Ember", "Firesteel", "Spark"), "fire"),
                    (("Sand", "Cactee", "Hyena", "Scarak", "Scorpion"), "sand"), (("Void", "Wraith", "Spectre"), "void"), (("Bleached",), "bone"),
                    (("Marsh", "Fen", "Cave"), "swamp")):
        if any(_k in r for _k in _ks):
            tint = _t
            break
    return fam, tint


_TF_FIRST = ("Wolf", "Bear", "Snake", "Spider", "Toad", "Larva", "Crawler", "Eye", "Golem", "Hound", "Leopard", "Tiger", "Raptor", "Rex", "Spark", "Zombie")
_TF_NAME = {"Snake_Rattle": "Rattlesnake", "Snake_Cobra": "Cobra", "Toad_Rhino": "Rhino Toad", "Toad_Rhino_Magma": "Magma Rhino Toad",
            "Fen_Stalker": "Fen Stalker", "Void_Spectre": "Void Spectre", "Spider_Cave": "Cave Spider"}


def _tf_name(r):
    if r in _TF_NAME:
        return _TF_NAME[r]
    w = r.split("_")
    if len(w) > 1 and w[0] in _TF_FIRST:
        return " ".join(w[1:] + [w[0]])
    if len(w) > 2 and w[0] == "Skeleton" and w[1] in ("Burnt", "Frost", "Sand", "Incandescent"):
        return " ".join([w[1], "Skeleton"] + w[2:])
    return " ".join(w)


TF_ROWS = []       # (zone, role, health, rank, drops "id:avg,..." rarest first, look, name)
TF_OFF = [0]
TF_LOOKS = []
for _z in range(CZ_N):
    _src = set()
    for _n, _s in _CZ_SPAWN.items():
        if ("/" + CZ_SRC[_z] + "/") in _n or "/World/Void/" in _n:
            _src |= _s
    _rs = []
    for _part in CZ_POOL[_z]:
        for _r in _part.split(","):
            if _r not in _rs:
                _rs.append(_r)
    for _r in TF_EXTRA[_z]:
        assert _r in _CZ_ROLES and (_r in _src or _r + "_Wander" in _src), "0.4.26: town role %s is not a vanilla %s role" % (_r, CZ_SRC[_z])
        if _r not in _rs:
            _rs.append(_r)
    _hs = sorted(((_tf_hp(_r), _r) for _r in _rs))
    for _rank, (_h, _r) in enumerate(_hs):
        if _r in CZ_DROPS:
            _dl = list(CZ_DROPS[_r])
        else:
            _out = {}
            for _d in re.findall(r'"DropList"\s*:\s*"([^"]+)"', AZ.read(_CZ_ROLES[_r]).decode("utf-8-sig")):
                if _d in _CZ_DROPS:
                    _cz_ev(json.loads(AZ.read(_CZ_DROPS[_d]).decode("utf-8-sig")).get("Container", {}), _out, 1.0)
            _dl = [(_i, round(_q, 4)) for _i, _q in sorted(_out.items()) if _q > 0.0]
        if not _dl:
            _dl = [(CZ_DROP[_z], 1.0)]
        _dl.sort(key=lambda _e: (_e[1], _e[0]))
        _lk = _tf_look(_r, _h)
        if _lk not in TF_LOOKS:
            TF_LOOKS.append(_lk)
        TF_ROWS.append((_z, _r, _h, _rank, ",".join("%s:%g" % _e for _e in _dl), TF_LOOKS.index(_lk), _tf_name(_r)))
    TF_OFF.append(len(TF_ROWS))
_tf1 = [_x[1] for _x in TF_ROWS[TF_OFF[0]:TF_OFF[1]]]
assert _tf1[0] == "Rat" and _tf1.index("Wolf_Black") < _tf1.index("Bear_Grizzly") < _tf1.index("Skeleton_Burnt_Praetorian") and "Trork_Warrior" in _tf1, _tf1
assert all(TF_OFF[_z + 1] - TF_OFF[_z] >= 8 for _z in range(CZ_N)), TF_OFF
assert all(_i in ITEMS for _x in TF_ROWS for _i in [_p.rsplit(":", 1)[0] for _p in _x[4].split(",")]), "0.4.26: every town loot id is a real item"
CK_WEAPS = [(_i, int(_TT48.tier(_i))) for _i in sorted(_TT48.ROWS) if _i.startswith("Weapon_") and _TT48.tier(_i)]
assert ("Weapon_Axe_Lead_SkyWynn", 5) in CK_WEAPS and len(CK_WEAPS) >= 100, CK_WEAPS[:4]
for f in ("public static final int TK = %d;" % TF_K, "public static final int TL_MAX = 15;",
          "public static final String[] WEAP_ID = new String[] { %s };" % ", ".join(jlit(_a) for _a, _t in CK_WEAPS),
          "public static final int[] WEAP_T = new int[] { %s };" % ", ".join(str(_t) for _a, _t in CK_WEAPS),
          "public static final int[] T_OFF = new int[] { %s };" % ", ".join(str(_x) for _x in TF_OFF),
          "public static final String[] T_ROLE = new String[] { %s };" % ", ".join(jlit(_x[1]) for _x in TF_ROWS),
          "public static final int[] T_HP = new int[] { %s };" % ", ".join(str(_x[2]) for _x in TF_ROWS),
          "public static final int[] T_RANK = new int[] { %s };" % ", ".join(str(_x[3]) for _x in TF_ROWS),
          "public static final String[] T_DROP = new String[] { %s };" % ", ".join(jlit(_x[4]) for _x in TF_ROWS),
          "public static final int[] T_PIC = new int[] { %s };" % ", ".join(str(_x[5]) for _x in TF_ROWS),
          "public static final String[] T_NAME = new String[] { %s };" % ", ".join(jlit(_x[6]) for _x in TF_ROWS),
          "public static final java.util.concurrent.ConcurrentHashMap TOWN = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.atomic.AtomicLong SLAIN = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong LOOTED = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong TGATED = new java.util.concurrent.atomic.AtomicLong();"):
    F(ckc, f)
# the weapon's tier (tools/tier_tags.py weapons; another Weapon_ id = its best metal word, else T1); 0 = not a weapon (bare hands / a tool)
M(ckc, r"""
public static int weapTier(String id) {
  if (id == null || id.length() == 0) return 0;
  for (int i = 0; i < WEAP_ID.length; i++) if (WEAP_ID[i].equals(id)) return WEAP_T[i];
  if (!id.startsWith("Weapon_")) return 0;
  String[] w = id.split("_");
  int best = 0;
  for (int i = 0; i < w.length; i++) for (int j = 0; j < METAL_W.length; j++) if (METAL_W[j].equals(w[i]) && METAL_T[j] > best) best = METAL_T[j];
  return best > 0 ? best : 1;
}""")
M(ckc, "public static int zN(int z) { return z < 0 || z + 1 >= T_OFF.length ? 0 : T_OFF[z + 1] - T_OFF[z]; }")
M(ckc, r"""
public static int townLv(int size, int a) {
  int s = size < 1 ? 1 : (size > 3 ? 3 : size);
  int l = a < 0 ? 0 : (a > 5 ? 5 : a);
  return (s - 1) * 5 + l;
}""")
# the kinds open at Town level tl: the first ceil(n x (tl + 1) / 16) of the zone's order (at least 1); all at TL_MAX
M(ckc, r"""
public static int kindsAt(int z, int tl) {
  int n = zN(z);
  if (n <= 0) return 0;
  if (tl >= TL_MAX) return n;
  int t = tl < 0 ? 0 : tl;
  int k = (n * (t + 1) + TL_MAX) / (TL_MAX + 1);
  return k < 1 ? 1 : (k > n ? n : k);
}""")
# monsters at once = the world's Mobs at once (combat.cap) for that size + level, at most the town's spots
M(ckc, r"""
public static int atOnce(int size, int a) {
  int s = size < 1 ? 1 : (size > 3 ? 3 : size);
  int c = @PKG@.ShCombat.cap(s, a);
  int sp = @PKG@.ShIsl.tx(s).length;
  if (c > sp) c = sp;
  if (c > NSPOT) c = NSPOT;
  return c < 1 ? 1 : c;
}""")
# fixer (fidelity critic): a MAXED town (Town level 15) has room for EVERY kind of its zone at once (Skyy: "at max all the kinds of mobs attack at
# once"): Zones 1-3 have 20-22 kinds, more than the Large Mobs at once (18) - the extra ones stand on the island's free spots (Large: 48)
M(ckc, r"""
public static int atOnceZ(int z, int size, int a) {
  int c = atOnce(size, a);
  if (townLv(size, a) < TL_MAX) return c;
  int n = zN(z);
  int s = size < 1 ? 1 : (size > 3 ? 3 : size);
  int sp = @PKG@.ShIsl.tx(s).length;
  if (n > sp) n = sp;
  if (n > NSPOT) n = NSPOT;
  return n > c ? n : c;
}""")
# how many monsters have come to a spot so far (memory, per <profile>|<kind>|<slot>): the next one is another kind
M(ckc, r"""
public static synchronized long arrivals(String key, int spot) {
  Object o = TOWN.get(key);
  if (o == null || spot < 0 || spot >= NSPOT) return 0L;
  return ((long[]) o)[spot];
}""")
M(ckc, r"""
public static synchronized void arrive(String key, int spot) {
  if (key == null || spot < 0 || spot >= NSPOT) return;
  Object o = TOWN.get(key);
  long[] a = o == null ? new long[NSPOT] : (long[]) o;
  if (o == null) TOWN.put(key, a);
  a[spot] = a[spot] + 1L;
}""")
M(ckc, r"""
public static double mix(long x) {
  long z = x * 6364136223846793005L + 1442695040888963407L;
  z = z ^ (z >>> 33);
  z = z * 3935559000370003845L;
  z = z ^ (z >>> 29);
  return (double) (z >>> 11) / 9007199254740992.0;
}""")
# the monster at a spot (a T_ROLE index; -1 = none): below TL_MAX one of the open kinds (deterministic: key, spot, arrivals - the page and the click agree);
# at TL_MAX every kind AT ONCE: spot i < N = kind i (fixer: atOnceZ gives a maxed town N spots or more), extra spots in turn
M(ckc, r"""
public static int roleAt(int z, int tl, int spot, long n, int m, String key) {
  int N = zN(z);
  if (N <= 0 || spot < 0) return -1;
  int idx;
  if (tl >= TL_MAX) idx = spot < N ? spot : (int) (((long) spot + n * (long) (m < 1 ? 1 : m)) % (long) N);
  else {
    int k = kindsAt(z, tl);
    long seed = (long) (key == null ? 0 : key.hashCode()) * 31L + (long) spot * 1000003L + n * 7919L;
    idx = (int) Math.floor(mix(seed) * (double) k);
    if (idx >= k) idx = k - 1;
    if (idx < 0) idx = 0;
  }
  return T_OFF[z] + idx;
}""")
M(ckc, r"""
public static double monHp(int gi) {
  int r = gi >= 0 && gi < T_RANK.length ? T_RANK[gi] : 0;
  double h = (double) @PKG@.ShCfg.TF_HP * (1.0 + (double) @PKG@.ShCfg.TF_HPSTEP / 100.0 * (double) r);
  return h < 1.0 ? 1.0 : h;
}""")
M(ckc, r"""
public static long townRespawnMs(int size, int sp) {
  double s = (double) @PKG@.ShCombat.respawnSec(size, sp) * (double) @PKG@.ShCfg.TF_RSP / 100.0;
  if (s < (double) @PKG@.ShCfg.TF_RMIN) s = (double) @PKG@.ShCfg.TF_RMIN;
  return s < 0.0 ? 0L : (long) Math.round(s * 1000.0);
}""")
M(ckc, r"""
public static int zoneTier(int z) {
  int[] a = @PKG@.ShCfg.TF_ZT;
  if (a == null || a.length == 0) return 1;
  int i = z < 0 ? 0 : (z >= a.length ? a.length - 1 : z);
  return a[i];
}""")
M(ckc, "public static int strPct(int ns) { return ns * @PKG@.ShCfg.TF_STR; }")
# the world's class XP of a kill: vanilla health x click.fight.xpPerHp / 100 x the level factor (combat.levelCurve: 1 + 0.13 (L - 1) + 0.004 (L - 1)^2)
M(ckc, r"""
public static double killXp(int gi, int lvl) {
  if (gi < 0 || gi >= T_HP.length) return 0.0;
  double l = (double) (lvl < 1 ? 1 : lvl) - 1.0;
  return (double) T_HP[gi] * (double) @PKG@.ShCfg.TF_XPHP / 100.0 * (1.0 + 0.13 * l + 0.004 * l * l);
}""")
# the clicking player's ACTIVE class skill (SkyySkills skill:fn:run {UUID, "class"}[5], e.g. "Combat.Warrior"); null = no class / no SkyySkills
M(ckc, r"""
public static String classSkill(java.util.UUID u) {
  if (u == null) return null;
  try {
    java.util.function.Function run = @PKG@.ShCfg.fn("skill:fn:run");
    if (run == null) return null;
    Object c = run.apply(new Object[] { u, "class" });
    if (c instanceof Object[] && ((Object[]) c).length > 5 && ((Object[]) c)[5] instanceof String) {
      String s = (String) ((Object[]) c)[5];
      return s.length() > 0 ? s : null;
    }
  } catch (Throwable x) { }
  return null;
}""")
M(ckc, r"""
public static String classWord(String cs) {
  if (cs == null) return "class";
  int i = cs.lastIndexOf('.');
  return i >= 0 ? cs.substring(i + 1) : cs;
}""")
# fixer (critics: class XP piled up as owed XP forever): SkyySkills grants only the skills in its bridge.addxp.skills row (default: no class skill).
# A refused class XP is NOT banked: the kill says so, and that player + class skill is not asked again for 60 s (memory only, NOXP).
for f in ("public static final java.util.concurrent.ConcurrentHashMap NOXP = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.atomic.AtomicLong XPREF = new java.util.concurrent.atomic.AtomicLong();"):
    F(ckc, f)
M(ckc, r"""
public static boolean classXpOk(java.util.UUID u, String cls, long now) {
  if (u == null || cls == null) return false;
  Object o = NOXP.get(String.valueOf(u) + "|" + cls);
  return o == null || ((Long) o).longValue() <= now;
}""")
M(ckc, r"""
public static String noXpWhy(String cls) {
  return "SkyySkills does not take " + classWord(cls) + " XP from shards - an admin can add " + cls + " to Server Setup -> Skills -> Skills other mods may grant";
}""")
M(ckc, r"""
public static String payClass(java.util.UUID u, String cls, long xp, long now) {
  if (xp <= 0L) return "";
  String nk = String.valueOf(u) + "|" + cls;
  if (!classXpOk(u, cls, now)) { XPREF.incrementAndGet(); return " (no XP: " + noXpWhy(cls) + ")"; }
  if (@PKG@.ShPay.xp(u, cls, xp, "shard:" + cls.toLowerCase())) { NOXP.remove(nk); return " +" + @PKG@.ShCfg.num(xp) + " " + classWord(cls) + " XP"; }
  NOXP.put(nk, Long.valueOf(now + 60000L));
  XPREF.incrementAndGet();
  return " (no XP: " + noXpWhy(cls) + ")";
}""")
# a kill's loot: each "id:avg" part = the whole part + one more at the rest's chance (rnd asked only when there is a rest - the harness replays it);
# combat.cageSkip items left out while click.fight.cageSkip is on. -> Object[]{ String[] ids, long[] qty } (rarest first, the T_DROP order)
M(ckc, r"""
public static Object[] lootOf(int gi) {
  String s = gi >= 0 && gi < T_DROP.length ? T_DROP[gi] : "";
  String[] a = s.length() == 0 ? new String[0] : s.split(",");
  String[] ids = new String[a.length];
  long[] q = new long[a.length];
  for (int i = 0; i < a.length; i++) {
    int c = a[i].lastIndexOf(':');
    ids[i] = c > 0 ? a[i].substring(0, c) : a[i];
    double v = 1.0;
    if (c > 0) { try { v = Double.parseDouble(a[i].substring(c + 1)); } catch (Throwable x) { v = 0.0; } }
    if (!(v > 0.0) || (@PKG@.ShCfg.TF_SKIP && @PKG@.ShCombat.skip(ids[i]))) { q[i] = 0L; continue; }
    long w = (long) Math.floor(v + 0.000000001);
    double fr = v - (double) w;
    q[i] = w + (fr > 0.000000001 && rnd() < fr ? 1L : 0L);
  }
  return new Object[] { ids, q };
}""")
M(ckc, r"""
public static String townWord(String hand) {
  if (hand == null || hand.length() == 0) return "Bare hands";
  return "Your " + @PKG@.ShTotem.pretty(hand);
}""")
# THE FIGHT CLICK (world thread; the bridges outside the store lock): Object[]{ status, pop text over the monster }
M(ckc, r"""
public static Object[] fight(java.util.UUID u, String k, int kd, int slot, int spot, String hand) {
  if (!@PKG@.ShCfg.TF_ON) return res("-The Combat town is switched off on this server.", "");
  int wt = weapTier(hand);
  if (wt <= 0) return res("-Hold a weapon - the town fights with the weapon in your hand.", "");
  long now = @PKG@.ShCore.now();
  if (!tick(u, now)) { CAPPED.incrementAndGet(); return res("", ""); }
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return res("-This shard's file could not be read.", "");
  String no = @PKG@.ShCore.gate(u, k, kd, p);
  if (no != null) return res(no, "");
  int own = @PKG@.ShCombat.ownerLv(k);   // a bridge: outside the lock
  int t; int sz; int a; int ml; int sp; int ns; long use; long lim;
  @PKG@.ShStore.LOCK.lock(); try {
    if (slot < 0 || slot >= @PKG@.ShMath.SLOTS || !@PKG@.ShMath.hasIsland(kd, p, slot)) return res("-That island is not yours yet.", "");
    t = @PKG@.ShIsl.ty(kd, p, slot);
    sz = @PKG@.ShMath.size(kd, p, slot);
    a = @PKG@.ShIsl.sub(p, kd, slot, 0);
    ml = @PKG@.ShIsl.sub(p, kd, slot, 1);
    sp = @PKG@.ShIsl.sub(p, kd, slot, 2);
    ns = nsize(p, kd, slot);
    @PKG@.ShMath.settle(kd, p, slot, now);
    use = @PKG@.ShMath.usedOf(kd, p, slot);
    lim = @PKG@.ShMath.limOf(kd, p, slot);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  int m = atOnceZ(@PKG@.ShCombat.zoneOf(t), sz, a);   // fixer: a maxed town = every kind at once
  if (spot < 0 || spot >= m || spot >= NSPOT) return res("=The page is up to date now.", "");
  if (use >= lim) return res("-This town's storage is full - Collect first.", "");
  int z = @PKG@.ShCombat.zoneOf(t);
  int tl = townLv(sz, a);
  String key = k + "|" + kd + "|" + slot;   // the town's own memory (a Foraging / Mining / Farming island in the same slot number keeps its own)
  int gi = roleAt(z, tl, spot, arrivals(key, spot), m, key);
  if (gi < 0) return res("=The page is up to date now.", "");
  int zt = zoneTier(z);
  double dm = dmg(wt, zt, 0.0) * (1.0 + (double) strPct(ns) / 100.0);
  if (!(dm > 0.0)) {
    TGATED.incrementAndGet();
    return res("-" + townWord(hand) + " (T" + wt + ") is too weak for the Zone " + (z + 1) + " town (T" + zt + " monsters) - like in the world, a weapon fights at most 2 tiers above its own.", "");
  }
  double hpMax = monHp(gi);
  double left = hit(key, spot, dm, hpMax, now, townRespawnMs(sz, sp));
  CHOPS.incrementAndGet();
  if (left < 0.0) { long ms = (long) (-left - 1.0); return res("=A new monster is on its way - " + ((ms + 999L) / 1000L) + " s.", ""); }
  if (left > 0.0) return res("", @PKG@.ShCfg.dec(hpMax - left) + " / " + @PKG@.ShCfg.dec(hpMax));
  String[] ids; long[] gq; long total = 0L; long got = 0L;
  @PKG@.ShStore.LOCK.lock(); try {
    if (!@PKG@.ShMath.hasIsland(kd, p, slot) || @PKG@.ShIsl.ty(kd, p, slot) != t) { unfell(key, spot, hpMax); return res("-That town changed meanwhile - the page is up to date now.", ""); }
    Object[] lo = lootOf(gi);
    ids = (String[]) lo[0];
    long[] q = (long[]) lo[1];
    gq = new long[q.length];
    for (int i = 0; i < q.length; i++) total += q[i];
    @PKG@.ShMath.settle(kd, p, slot, now);
    long room = @PKG@.ShMath.limOf(kd, p, slot) - @PKG@.ShMath.usedOf(kd, p, slot);
    if (room <= 0L) { unfell(key, spot, hpMax); return res("-This town's storage is full - Collect first.", ""); }
    for (int i = 0; i < q.length; i++) { gq[i] = q[i] < room ? q[i] : room; room = room - gq[i]; got += gq[i]; }   // what fits: the rarest first
    String dk = @PKG@.ShMath.ik(kd, slot, "drops");
    String old = p.getProperty(dk);
    java.util.LinkedHashMap mm = @PKG@.ShMath.held(kd, p, slot);
    for (int i = 0; i < ids.length; i++) addTo(mm, ids[i], gq[i]);
    @PKG@.ShMath.heldSet(kd, p, slot, mm);
    String e = @PKG@.ShStore.save(k, p);
    if (e != null) {
      if (old == null) p.remove(dk); else p.setProperty(dk, old);
      unfell(key, spot, hpMax);
      @PKG@.ShCfg.warnOnce("tsave", "a slain town monster's loot could not be saved (nothing added, the monster stands again; logged once): " + e);
      return res("-The shard file could not be saved - nothing was added.", "");
    }
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  arrive(key, spot);   // the next monster at this spot (after the respawn) is another one
  SLAIN.incrementAndGet();
  LOOTED.addAndGet(got);
  int lvl = (@PKG@.ShCombat.lvLoP(own, z, sz, ml) + @PKG@.ShCombat.lvHiP(own, z, sz, ml)) / 2;
  double share = total <= 0L ? 1.0 : (double) got / (double) total;
  double xpe = killXp(gi, lvl) * (double) @PKG@.ShCfg.CK_XP_PCT / 100.0 * share;
  String cls = classSkill(u);
  String xt = "";
  if (cls == null) xt = " (no class chosen yet - no XP)";
  else {
    long xp = accXp(String.valueOf(u) + "|" + @PKG@.ShCfg.pkey(u) + "|" + kd, xpe);   // the town's own XP fractions
    xt = payClass(u, cls, xp, now);   // fixer: paid now or not at all (never banked as owed XP)
  }
  StringBuilder sb = new StringBuilder();
  String first = null; long firstQ = 0L;
  for (int i = ids.length - 1; i >= 0; i--) { part(sb, gq[i], ids[i]); if (first == null && gq[i] > 0L) { first = ids[i]; firstQ = gq[i]; } }
  String nm = T_NAME[gi];
  String fit = got < total ? " - the town's storage is full (" + @PKG@.ShCfg.num(total - got) + " did not fit)" : "";
  String r = "+Slew a " + nm + " (Lv " + lvl + ")" + (sb.length() > 0 ? ": " + sb.toString() : " - it dropped nothing") + xt + fit + ".";
  String pop = first != null ? "+" + @PKG@.ShCfg.num(firstQ) + " " + qName(first) : "Slain!";
  @PKG@.ShSnd.ok(u, r, 0);
  return res(r, pop);
}""")
'''
P.rep(r'''# THE CLICK: Object[]{ status ("+..." / "-..." / "=..." / "" = nothing to say), pop text over the tree }. World thread; the bridges outside the store lock
''', TOWN_CLK + r'''# THE CLICK: Object[]{ status ("+..." / "-..." / "=..." / "" = nothing to say), pop text over the tree }. World thread; the bridges outside the store lock
''')
P.rep(r'''  if (kd == CRK) return harvest(u, k, kd, slot, spot, hand);   // 0.4.25: the Farming clicker
  if (kd != FK) return res("-Only the Foraging, Mining and Farming Shards have a clicker so far.", "");''',
      r'''  if (kd == CRK) return harvest(u, k, kd, slot, spot, hand);   // 0.4.25: the Farming clicker
  if (kd == TK) return fight(u, k, kd, slot, spot, hand);   // 0.4.26: the Combat town
  if (kd != FK) return res("-Only the Foraging, Mining, Farming and Combat Shards have a clicker so far.", "");''')
# Warrior strength = the Tree size purchase on a Combat island (same cost rows; the town's Enchanted item), its own maximum and words
P.rep(r'''  if (kd == CRK && !@PKG@.ShCfg.FQ_ON) return "-The Farming clicker is switched off on this server.";   // 0.4.25
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  String no = @PKG@.ShCore.gateOwn(u, k, kd, p);
  if (no != null) return no;
  int t0; int lv; long ver;''', r'''  if (kd == CRK && !@PKG@.ShCfg.FQ_ON) return "-The Farming clicker is switched off on this server.";   // 0.4.25
  if (kd == TK && !@PKG@.ShCfg.TF_ON) return "-The Combat town is switched off on this server.";   // 0.4.26
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  String no = @PKG@.ShCore.gateOwn(u, k, kd, p);
  if (no != null) return no;
  int t0; int lv; long ver;''')
P.rep(r'''  int mx = kd == MK ? @PKG@.ShCfg.MQ_NS_MAX : (kd == CRK ? @PKG@.ShCfg.FQ_NS_MAX : @PKG@.ShCfg.CK_NS_MAX);   // 0.4.24: Vein size on a Mining quarry; 0.4.25 Plot size
  if (lv >= mx) return kd == MK ? "=Vein size is at its highest level." : (kd == CRK ? "=Plot size is at its highest level." : "=Tree size is at its highest level.");''',
      r'''  int mx = kd == MK ? @PKG@.ShCfg.MQ_NS_MAX : (kd == CRK ? @PKG@.ShCfg.FQ_NS_MAX : (kd == TK ? @PKG@.ShCfg.TF_NS_MAX : @PKG@.ShCfg.CK_NS_MAX));   // 0.4.24: Vein size on a Mining quarry; 0.4.25 Plot size; 0.4.26 Warrior strength
  if (lv >= mx) return kd == MK ? "=Vein size is at its highest level." : (kd == CRK ? "=Plot size is at its highest level." : (kd == TK ? "=Warrior strength is at its highest level." : "=Tree size is at its highest level."));''')
P.rep(r'''      : (kd == CRK ? "+Plot size " + nl + "/" + mx + " on the " + @PKG@.ShIsl.tname(t0) + " island: " + plantsAt(nl) + " plants a harvest."''',
      r'''      : (kd == CRK ? "+Plot size " + nl + "/" + mx + " on the " + @PKG@.ShIsl.tname(t0) + " island: " + plantsAt(nl) + " plants a harvest."
      : (kd == TK ? "+Warrior strength " + nl + "/" + mx + " in the " + @PKG@.ShIsl.tname(t0) + " town: your clicks hit +" + strPct(nl) + " %."''')
P.rep(r'''      : "+Tree size " + nl + "/" + mx + " on the " + @PKG@.ShIsl.tname(t0) + " island: " + logsAt(nl) + " logs a felled tree.");
  @PKG@.ShSnd.ok(u, ok, 2);''', r'''      : "+Tree size " + nl + "/" + mx + " on the " + @PKG@.ShIsl.tname(t0) + " island: " + logsAt(nl) + " logs a felled tree."));
  @PKG@.ShSnd.ok(u, ok, 2);''')

# ---------------------------------------------------------------------------------------------------- 4. the town's art (pure Python, appended to CLK_ART_SRC)
TART_SRC = r'''# 0.4.26 THE COMBAT TOWN ART (tools/shards_0_4_26_patch.py): monsters by family + tint, a slain monster, the town islands, the map towns, four upgrade
# icons. Our own geometry; TART(looks, zone_looks, sizes) -> {name: Pic}; looks = [(family, tint)] by picture index.
MON_BASE = {"rat": ("#8a7a6a", "#c8b8a6", "#463a2e"), "wolf": ("#6a6a72", "#b0b0ba", "#2e2e34"), "bear": ("#7a5232", "#b88a5a", "#3a2414"),  # ui-data (picture colours)
            "skel": ("#e6e0cc", "#ffffff", "#8a846e"), "bigskel": ("#d8d0b8", "#ffffff", "#6e6852"), "spider": ("#3a3036", "#7a6a74", "#141012"),  # ui-data (picture colours)
            "snake": ("#5a8a3a", "#a8d878", "#24401a"), "goblin": ("#6aa040", "#b0e07a", "#2e5a1a"), "troll": ("#7a8a6a", "#b8c8a6", "#3a4630"),  # ui-data (picture colours)
            "golem": ("#8a5a3a", "#d88a4a", "#3a2010"), "zombie": ("#6a8a6a", "#a8c8a0", "#2e4a2e"), "wisp": ("#7a5ad0", "#d0c0ff", "#2a1a5a")}  # ui-data (picture colours)
MON_TINT = {"frost": ("#cfe2f2", "#ffffff", "#6a8aa8"), "fire": ("#8a3a1e", "#ff9a4a", "#2a0a06"), "sand": ("#d2b070", "#fff0c0", "#86663a"),  # ui-data (picture colours)
            "void": ("#5a2a8a", "#c08aff", "#1e0a36"), "bone": ("#e8e2d0", "#ffffff", "#8a8270"), "swamp": ("#5a7a3a", "#a8d070", "#243a14")}  # ui-data (picture colours)
MON_EYE = {"plain": "#ffd84a", "frost": "#7ad8ff", "fire": "#ffb03a", "sand": "#ffe07a", "void": "#ff5aff", "bone": "#ff4a3a", "swamp": "#d8ff5a"}  # ui-data (picture colours)
TWOOD = ("#8a6a3a", "#c09a62", "#4a3418")  # ui-data (picture colours)
TSTEEL = ("#b8c0cc", "#ffffff", "#5a6270")  # ui-data (picture colours)


def _mc(fam, tint):
    return MON_TINT.get(tint) or MON_BASE[fam]


def _eye(pic, x, y, r, col):
    disc(pic, x, y, r * 1.35, _rgb("#120a06"), 0.85)  # ui-data (picture colours)
    disc(pic, x, y, r, _rgb(col))
    disc(pic, x + r * 0.25, y - r * 0.2, r * 0.4, _rgb("#ffffff"), 0.8)  # ui-data (picture colours)


def _sh(c, x, y, r, seed, ns=0.12):
    return shade(c[0], c[1], c[2], x, y, r, ns=ns, nsc=5, seed=seed)


def _humanoid(pic, cx, by, u, c, eye, seed, big=1.0, cloth=None, arms_fwd=False, weapon=None):
    k = u * big
    cl = cloth or c
    line(pic, cx - 3 * k, by - 44 * k, cx - 11 * k, by, 7 * k, _rgb(cl[2]))
    line(pic, cx + 3 * k, by - 44 * k, cx + 11 * k, by, 7 * k, _rgb(cl[2]))
    ellipse(pic, cx, by - 62 * k, 15 * k, 22 * k, _sh(cl, cx - 6 * k, by - 72 * k, 24 * k, seed))
    if arms_fwd:
        line(pic, cx - 8 * k, by - 76 * k, cx + 34 * k, by - 72 * k, 6 * k, _rgb(c[0]))
        line(pic, cx + 8 * k, by - 78 * k, cx + 38 * k, by - 80 * k, 6 * k, _rgb(c[1]))
    else:
        line(pic, cx - 13 * k, by - 78 * k, cx - 20 * k, by - 48 * k, 6 * k, _rgb(c[0]))
        line(pic, cx + 13 * k, by - 78 * k, cx + 22 * k, by - 50 * k, 6 * k, _rgb(c[0]))
    disc(pic, cx, by - 94 * k, 13 * k, _sh(c, cx - 5 * k, by - 99 * k, 15 * k, seed + 1))
    _eye(pic, cx - 5 * k, by - 96 * k, 2.4 * k, eye)
    _eye(pic, cx + 5 * k, by - 96 * k, 2.4 * k, eye)
    if weapon == "dagger":
        line(pic, cx + 22 * k, by - 50 * k, cx + 30 * k, by - 66 * k, 3 * k, _rgb(TSTEEL[0]))
    elif weapon == "club":
        line(pic, cx + 22 * k, by - 50 * k, cx + 38 * k, by - 96 * k, 8 * k, _rgb(TWOOD[0]))
        disc(pic, cx + 39 * k, by - 98 * k, 10 * k, _sh(TWOOD, cx + 35 * k, by - 102 * k, 12 * k, seed + 2))


def _skel(pic, cx, by, u, c, eye, seed, big=False):
    k = u * (1.04 if big else 1.0)
    for sx in (-1, 1):
        line(pic, cx + sx * 3 * k, by - 50 * k, cx + sx * 12 * k, by, 4.5 * k, _rgb(c[0]))
    ellipse(pic, cx, by - 50 * k, 11 * k, 5 * k, _rgb(c[0]))
    line(pic, cx, by - 50 * k, cx, by - 92 * k, 4 * k, _rgb(c[0]))
    for j in range(4):
        y = by - 62 * k - j * 7 * k
        line(pic, cx - (13 - j) * k, y, cx + (13 - j) * k, y, 3 * k, _rgb(c[0]))
    line(pic, cx - 14 * k, by - 88 * k, cx - 22 * k, by - 60 * k, 4 * k, _rgb(c[0]))
    line(pic, cx + 14 * k, by - 88 * k, cx + 26 * k, by - 64 * k, 4 * k, _rgb(c[0]))
    line(pic, cx + 26 * k, by - 64 * k, cx + 40 * k, by - 106 * k, 4 * k, _rgb(TSTEEL[0]))
    line(pic, cx + 20 * k, by - 68 * k, cx + 32 * k, by - 62 * k, 3 * k, _rgb(TWOOD[0]))
    disc(pic, cx, by - 104 * k, 13 * k, _sh(c, cx - 5 * k, by - 109 * k, 15 * k, seed))
    ellipse(pic, cx, by - 93 * k, 8 * k, 4 * k, _rgb(c[0]))
    for sx in (-1, 1):
        disc(pic, cx + sx * 5 * k, by - 106 * k, 3.6 * k, _rgb("#1a120c"))  # ui-data (picture colours)
        disc(pic, cx + sx * 5 * k, by - 106 * k, 1.5 * k, _rgb(eye))
    if big:
        poly(pic, [(cx - 15 * k, by - 106 * k), (cx + 15 * k, by - 106 * k), (cx + 11 * k, by - 117 * k), (cx - 11 * k, by - 117 * k)], _sh(TSTEEL, cx - 6 * k, by - 116 * k, 16 * k, seed + 3))
        ellipse(pic, cx - 24 * k, by - 72 * k, 11 * k, 17 * k, _sh(TSTEEL, cx - 28 * k, by - 80 * k, 16 * k, seed + 4))
        disc(pic, cx - 24 * k, by - 72 * k, 3.5 * k, _rgb(eye))


def monster(fam, tint, W=110, H=140, s=2, seed=1):
    w, h = int(W * s), int(H * s)
    pic = Pic(w, h)
    u = float(s)
    cx, by = w / 2.0, h - 10.0 * u
    c = _mc(fam, tint)
    ey = MON_EYE.get(tint, "#ffd84a")  # ui-data (picture colours)
    ellipse(pic, cx, by + 1 * u, 34 * u, 5 * u, (0, 0, 0), 0.25)
    if fam == "rat":
        line(pic, cx - 20 * u, by - 10 * u, cx - 46 * u, by - 26 * u, 3 * u, _rgb("#d89a9a"))  # ui-data (picture colours)
        ellipse(pic, cx - 2 * u, by - 14 * u, 24 * u, 13 * u, _sh(c, cx - 8 * u, by - 22 * u, 26 * u, seed))
        ellipse(pic, cx + 22 * u, by - 18 * u, 12 * u, 9 * u, _sh(c, cx + 18 * u, by - 22 * u, 13 * u, seed + 1))
        disc(pic, cx + 17 * u, by - 27 * u, 5.5 * u, _rgb(c[1]))
        disc(pic, cx + 17 * u, by - 27 * u, 3 * u, _rgb("#e8a0a8"))  # ui-data (picture colours)
        disc(pic, cx + 33 * u, by - 18 * u, 2.4 * u, _rgb("#e08a9a"))  # ui-data (picture colours)
        _eye(pic, cx + 25 * u, by - 21 * u, 2.2 * u, "#ff4040")  # ui-data (picture colours)
    elif fam == "wolf":
        for x in (-22, -12, 14, 24):
            line(pic, cx + x * u, by - 36 * u, cx + (x + 2) * u, by, 6 * u, _rgb(c[2]))
        line(pic, cx - 30 * u, by - 44 * u, cx - 48 * u, by - 64 * u, 7 * u, _rgb(c[0]))
        ellipse(pic, cx - 4 * u, by - 44 * u, 32 * u, 15 * u, _sh(c, cx - 12 * u, by - 52 * u, 34 * u, seed))
        ellipse(pic, cx + 26 * u, by - 60 * u, 14 * u, 12 * u, _sh(c, cx + 22 * u, by - 66 * u, 15 * u, seed + 1))
        poly(pic, [(cx + 34 * u, by - 64 * u), (cx + 52 * u, by - 56 * u), (cx + 50 * u, by - 50 * u), (cx + 33 * u, by - 51 * u)], _sh(c, cx + 40 * u, by - 60 * u, 12 * u, seed + 2))
        for x in (18, 28):
            poly(pic, [(cx + x * u, by - 68 * u), (cx + (x + 8) * u, by - 70 * u), (cx + (x + 2) * u, by - 82 * u)], _rgb(c[2]))
        disc(pic, cx + 51 * u, by - 55 * u, 2.4 * u, _rgb("#120a06"))  # ui-data (picture colours)
        _eye(pic, cx + 31 * u, by - 62 * u, 2.4 * u, ey)
    elif fam == "bear":
        for x in (-26, -8, 14, 28):
            ellipse(pic, cx + x * u, by - 10 * u, 9 * u, 14 * u, _rgb(c[2]))
        ellipse(pic, cx - 4 * u, by - 44 * u, 40 * u, 30 * u, _sh(c, cx - 16 * u, by - 60 * u, 42 * u, seed))
        disc(pic, cx + 30 * u, by - 66 * u, 18 * u, _sh(c, cx + 24 * u, by - 74 * u, 20 * u, seed + 1))
        disc(pic, cx + 20 * u, by - 82 * u, 6 * u, _rgb(c[0]))
        disc(pic, cx + 40 * u, by - 81 * u, 6 * u, _rgb(c[0]))
        ellipse(pic, cx + 44 * u, by - 60 * u, 10 * u, 7 * u, _rgb(c[1]))
        disc(pic, cx + 52 * u, by - 62 * u, 3 * u, _rgb("#120a06"))  # ui-data (picture colours)
        _eye(pic, cx + 34 * u, by - 70 * u, 2.6 * u, ey)
    elif fam in ("skel", "bigskel"):
        _skel(pic, cx, by, u, c, ey, seed, big=(fam == "bigskel"))
    elif fam == "spider":
        for sx in (-1, 1):
            for j in range(4):
                kx, ky = cx - 6 * u + sx * (18 + 8 * j) * u, by - 46 * u + j * 4 * u
                line(pic, cx - 6 * u, by - 28 * u, kx, ky, 3.2 * u, _rgb(c[2]))
                line(pic, kx, ky, cx - 6 * u + sx * (30 + 7 * j) * u, by, 3 * u, _rgb(c[2]))
        ellipse(pic, cx - 16 * u, by - 30 * u, 22 * u, 17 * u, _sh(c, cx - 22 * u, by - 38 * u, 24 * u, seed))
        disc(pic, cx + 10 * u, by - 26 * u, 11 * u, _sh(c, cx + 6 * u, by - 31 * u, 12 * u, seed + 1))
        for x, y in ((12, -30), (17, -27), (14, -23)):
            disc(pic, cx + x * u, by + y * u, 2 * u, _rgb("#ff3030"))  # ui-data (picture colours)
    elif fam == "snake":
        pts = [(-32, -8), (-18, -10), (-4, -9), (10, -11), (22, -18), (24, -32), (16, -44), (20, -56)]
        for j, (x, y) in enumerate(pts):
            disc(pic, cx + x * u, by + y * u, (9 - j * 0.35) * u, _sh(c, cx + (x - 3) * u, by + (y - 4) * u, 10 * u, seed + j))
        ellipse(pic, cx + 27 * u, by - 62 * u, 12 * u, 8 * u, _sh(c, cx + 24 * u, by - 66 * u, 12 * u, seed + 9))
        line(pic, cx + 38 * u, by - 61 * u, cx + 46 * u, by - 61 * u, 1.6 * u, _rgb("#e03030"))  # ui-data (picture colours)
        line(pic, cx + 46 * u, by - 61 * u, cx + 50 * u, by - 64 * u, 1.4 * u, _rgb("#e03030"))  # ui-data (picture colours)
        line(pic, cx + 46 * u, by - 61 * u, cx + 50 * u, by - 58 * u, 1.4 * u, _rgb("#e03030"))  # ui-data (picture colours)
        _eye(pic, cx + 30 * u, by - 65 * u, 2.2 * u, ey)
    elif fam == "goblin":
        _humanoid(pic, cx, by, u, c, ey, seed, big=0.72, cloth=TWOOD, weapon="dagger")
        k = u * 0.72
        for sx in (-1, 1):
            poly(pic, [(cx + sx * 9 * k, by - 98 * k), (cx + sx * 30 * k, by - 104 * k), (cx + sx * 10 * k, by - 90 * k)], _rgb(c[0]))
    elif fam == "troll":
        k = u * 1.05
        line(pic, cx - 12 * k, by - 40 * k, cx - 16 * k, by, 10 * k, _rgb(c[2]))
        line(pic, cx + 12 * k, by - 40 * k, cx + 16 * k, by, 10 * k, _rgb(c[2]))
        ellipse(pic, cx - 2 * k, by - 64 * k, 28 * k, 30 * k, _sh(c, cx - 12 * k, by - 78 * k, 32 * k, seed))
        line(pic, cx - 22 * k, by - 80 * k, cx - 30 * k, by - 26 * k, 9 * k, _rgb(c[0]))
        line(pic, cx + 22 * k, by - 80 * k, cx + 30 * k, by - 40 * k, 9 * k, _rgb(c[0]))
        line(pic, cx + 30 * k, by - 40 * k, cx + 38 * k, by - 100 * k, 8 * k, _rgb(TWOOD[0]))
        disc(pic, cx + 39 * k, by - 102 * k, 10 * k, _sh(TWOOD, cx + 35 * k, by - 106 * k, 11 * k, seed + 2))
        disc(pic, cx + 6 * k, by - 98 * k, 13 * k, _sh(c, cx + 2 * k, by - 103 * k, 14 * k, seed + 1))
        for sx in (-1, 1):
            line(pic, cx + (6 + sx * 6) * k, by - 90 * k, cx + (6 + sx * 7) * k, by - 96 * k, 2.4 * k, _rgb("#f4f0e0"))  # ui-data (picture colours)
        _eye(pic, cx + 2 * k, by - 101 * k, 2.4 * k, ey)
        _eye(pic, cx + 11 * k, by - 101 * k, 2.4 * k, ey)
    elif fam == "golem":
        for sx in (-1, 1):
            poly(pic, [(cx + sx * 6 * u, by), (cx + sx * 22 * u, by), (cx + sx * 22 * u, by - 34 * u), (cx + sx * 6 * u, by - 34 * u)], _sh(c, cx + sx * 12 * u, by - 24 * u, 16 * u, seed + sx))
        poly(pic, [(cx - 28 * u, by - 34 * u), (cx + 28 * u, by - 34 * u), (cx + 30 * u, by - 92 * u), (cx - 30 * u, by - 92 * u)], _sh(c, cx - 10 * u, by - 76 * u, 40 * u, seed))
        for sx in (-1, 1):
            poly(pic, [(cx + sx * 30 * u, by - 88 * u), (cx + sx * 44 * u, by - 84 * u), (cx + sx * 42 * u, by - 40 * u), (cx + sx * 30 * u, by - 46 * u)], _sh(c, cx + sx * 36 * u, by - 70 * u, 20 * u, seed + 3))
        poly(pic, [(cx - 13 * u, by - 92 * u), (cx + 13 * u, by - 92 * u), (cx + 12 * u, by - 114 * u), (cx - 12 * u, by - 114 * u)], _sh(c, cx - 4 * u, by - 108 * u, 16 * u, seed + 5))
        for (x1, y1, x2, y2) in ((-14, -80, -4, -66), (-4, -66, 8, -72), (8, -72, 16, -50), (-20, -56, -8, -44)):
            line(pic, cx + x1 * u, by + y1 * u, cx + x2 * u, by + y2 * u, 2.4 * u, _rgb("#ff8a3a"))  # ui-data (picture colours)
        _eye(pic, cx - 5 * u, by - 104 * u, 2.6 * u, ey)
        _eye(pic, cx + 5 * u, by - 104 * u, 2.6 * u, ey)
    elif fam == "zombie":
        _humanoid(pic, cx, by, u, c, ey, seed, big=1.0, cloth=("#4a5a6a", "#8a9aaa", "#232c36"), arms_fwd=True)  # ui-data (picture colours)
    else:   # wisp: a floating eye / spirit
        ellipse(pic, cx, by - 64 * u, 34 * u, 34 * u, _rgb(c[1]), 0.22)
        poly(pic, [(cx - 16 * u, by - 56 * u), (cx + 16 * u, by - 56 * u), (cx + 4 * u, by - 20 * u), (cx - 6 * u, by - 26 * u)], _sh(c, cx, by - 46 * u, 20 * u, seed + 1), 0.85)
        ellipse(pic, cx, by - 66 * u, 20 * u, 24 * u, _sh(c, cx - 8 * u, by - 76 * u, 24 * u, seed))
        disc(pic, cx, by - 68 * u, 10 * u, _rgb("#ffffff"))  # ui-data (picture colours)
        disc(pic, cx + 1 * u, by - 68 * u, 6 * u, _rgb(ey))
        disc(pic, cx + 1.5 * u, by - 68 * u, 3 * u, _rgb("#120a06"))  # ui-data (picture colours)
    return pic


def slain(W=110, H=140, s=2):
    w, h = int(W * s), int(H * s)
    pic = Pic(w, h)
    u = float(s)
    cx, by = w / 2.0, h - 10.0 * u
    ellipse(pic, cx, by - 2 * u, 30 * u, 7 * u, _rgb("#5a4632"), 0.8)  # ui-data (picture colours)
    line(pic, cx + 10 * u, by - 4 * u, cx + 10 * u, by - 40 * u, 5 * u, _rgb(TWOOD[0]))
    line(pic, cx + 1 * u, by - 30 * u, cx + 19 * u, by - 30 * u, 5 * u, _rgb(TWOOD[0]))
    bone = MON_TINT["bone"]
    for (x1, y1, x2, y2) in ((-26, -6, -6, -10), (-22, -14, -8, -2)):
        line(pic, cx + x1 * u, by + y1 * u, cx + x2 * u, by + y2 * u, 3 * u, _rgb(bone[0]))
        disc(pic, cx + x1 * u, by + y1 * u, 2.6 * u, _rgb(bone[0]))
        disc(pic, cx + x2 * u, by + y2 * u, 2.6 * u, _rgb(bone[0]))
    disc(pic, cx - 16 * u, by - 16 * u, 7 * u, _sh(bone, cx - 18 * u, by - 19 * u, 8 * u, 3))
    for sx in (-1, 1):
        disc(pic, cx - 16 * u + sx * 2.6 * u, by - 17 * u, 1.6 * u, _rgb("#1a120c"))  # ui-data (picture colours)
    return pic


def _house(pic, x, y, sc, seed):
    hw, hh = 26 * sc, 20 * sc
    poly(pic, [(x - hw / 2, y), (x + hw / 2, y), (x + hw / 2, y - hh), (x - hw / 2, y - hh)], shade("#d8c8a0", "#fff4d8", "#8a7a58", x - hw / 3, y - hh, hw, ns=0.1, nsc=4, seed=seed))  # ui-data (picture colours)
    poly(pic, [(x - hw / 2 - 3 * sc, y - hh), (x + hw / 2 + 3 * sc, y - hh), (x, y - hh - 15 * sc)], shade("#b04a2a", "#f08a5a", "#5a1a0a", x - hw / 4, y - hh - 10 * sc, hw, ns=0.1, nsc=4, seed=seed + 1))  # ui-data (picture colours)
    poly(pic, [(x - 3 * sc, y), (x + 3 * sc, y), (x + 3 * sc, y - 9 * sc), (x - 3 * sc, y - 9 * sc)], _rgb("#4a3018"))  # ui-data (picture colours)
    disc(pic, x + hw / 4, y - hh / 2 - 1 * sc, 2.4 * sc, _rgb("#ffd86a"))  # ui-data (picture colours)


def town(W, H, s=1, seed=1):
    pic = island(W, H, s, seed=seed + 60, hue="#6aa84a")  # ui-data (picture colours)
    w, h = pic.w, pic.h
    cx, cy = w / 2.0, h * 0.34
    rx, ry = w * 0.47, w * 0.47 * 0.36
    nh = 3 + int(W / 220)
    sc = s * W / 550.0
    for j in range(nh):
        a = _m.radians(198 + j * 144.0 / max(1, nh - 1))
        _house(pic, cx + _m.cos(a) * rx * 0.86, cy + _m.sin(a) * ry * 0.78, sc, seed * 7 + j)
    tx, ty = cx - rx * 0.92, cy + ry * 0.05
    poly(pic, [(tx - 8 * sc, ty), (tx + 8 * sc, ty), (tx + 6 * sc, ty - 44 * sc), (tx - 6 * sc, ty - 44 * sc)], shade("#9a9a92", "#e0e0d8", "#4a4a44", tx - 4 * sc, ty - 30 * sc, 14 * sc, ns=0.1, nsc=4, seed=seed))  # ui-data (picture colours)
    poly(pic, [(tx - 10 * sc, ty - 44 * sc), (tx + 10 * sc, ty - 44 * sc), (tx, ty - 58 * sc)], _rgb("#b04a2a"))  # ui-data (picture colours)
    line(pic, tx, ty - 58 * sc, tx, ty - 70 * sc, 1.4 * sc, _rgb(TWOOD[2]))
    poly(pic, [(tx, ty - 70 * sc), (tx + 10 * sc, ty - 66 * sc), (tx, ty - 62 * sc)], _rgb("#4a8ad8"))  # ui-data (picture colours)
    return pic


def tmini(look, zone, W=150, H=100, s=2):
    w, h = int(W * s), int(H * s)
    base = Pic(w, h)
    top = int(h * 0.30)
    paste(base, town(W, int(H * 0.70), s, seed=zone + 1), 0, top, 1.0)
    mo = monster(look[0], look[1], 110, 140, s=1, seed=zone + 3)
    gy = top + h * 0.70 * 0.34
    paste(base, mo, int(w * 0.5 - 110 * 0.40 * s / 2.0), int(gy + 0.08 * h * 0.70 - (140 - 10) * 0.40 * s), 0.40 * s)
    return base


def ticon(kind, s=2):
    W = 56
    p = Pic(int(W * s), int(W * s))
    if kind == "str":
        line(p, 10 * s, 46 * s, 36 * s, 12 * s, 5 * s, _rgb(TSTEEL[0]))
        line(p, 8 * s, 34 * s, 22 * s, 48 * s, 4 * s, _rgb(TWOOD[0]))
        disc(p, 44 * s, 42 * s, 9 * s, _rgb("#4fd88a"))  # ui-data (picture colours)
        line(p, 44 * s, 37 * s, 44 * s, 47 * s, 3 * s, _rgb("#0b1322"))  # ui-data (picture colours)
        line(p, 39 * s, 42 * s, 49 * s, 42 * s, 3 * s, _rgb("#0b1322"))  # ui-data (picture colours)
    elif kind == "lvl":
        _house(p, 22 * s, 48 * s, s * 1.2, 5)
        poly(p, [(44 * s, 10 * s), (54 * s, 24 * s), (48 * s, 24 * s), (48 * s, 40 * s), (40 * s, 40 * s), (40 * s, 24 * s), (34 * s, 24 * s)], _rgb("#4fd88a"))  # ui-data (picture colours)
    elif kind == "spd":
        poly(p, [(12 * s, 22 * s), (26 * s, 22 * s), (30 * s, 38 * s), (44 * s, 40 * s), (44 * s, 48 * s), (12 * s, 48 * s)], shade(TWOOD[0], TWOOD[1], TWOOD[2], 16 * s, 26 * s, 24 * s))
        for j, y in enumerate((18, 28, 38)):
            line(p, (4 + j * 2) * s, y * s, (16 + j * 2) * s, y * s, 2.4 * s, _rgb("#7ad8ff"), 0.9)  # ui-data (picture colours)
    else:   # Monster level: a skull + an up arrow
        bone = MON_TINT["bone"]
        disc(p, 22 * s, 30 * s, 14 * s, shade(bone[0], bone[1], bone[2], 18 * s, 24 * s, 16 * s))
        for sx in (-1, 1):
            disc(p, (22 + sx * 5) * s, 30 * s, 3.8 * s, _rgb("#1a120c"))  # ui-data (picture colours)
        poly(p, [(44 * s, 10 * s), (54 * s, 24 * s), (48 * s, 24 * s), (48 * s, 42 * s), (40 * s, 42 * s), (40 * s, 24 * s), (34 * s, 24 * s)], _rgb("#e05a3a"))  # ui-data (picture colours)
    return p


def TART(looks, zone_looks, sizes):
    out = {}
    for i, (fam, tint) in enumerate(looks):
        out["TMon%d" % i] = monster(fam, tint, 110, 140, s=2, seed=51 + i)
    out["TSlain"] = slain(110, 140, s=2)
    for sz, (W, H) in sorted(sizes.items()):
        out["TIsl%d" % sz] = town(W, H, 1, seed=sz)
    for z, lk in enumerate(zone_looks):
        out["TMap%d" % z] = tmini(lk, z, 150, 100, s=2)
    for k in ("str", "lvl", "spd", "mob"):
        out["UpT" + k.capitalize()] = ticon(k)
    return out


'''
P.rep('''def ART(tiers, sizes):
    # every picture of the clicker: {name: Pic}.''', TART_SRC + '''def ART(tiers, sizes):
    # every picture of the clicker: {name: Pic}.''')
P.rep(r'''FQ_NPIC = len(_f_pics)
assert FQ_NPIC == 34, FQ_NPIC
del _f_pics
''', r'''FQ_NPIC = len(_f_pics)
assert FQ_NPIC == 34, FQ_NPIC
del _f_pics
# 0.4.26 THE TOWN'S PICTURES: one monster per (family, tint) look, a slain monster, 3 town islands, 5 map towns (each with its zone's hardest kind), 4 icons
_t_t0 = _time423.time()
TF_ZLOOK = [TF_LOOKS[TF_ROWS[TF_OFF[_z + 1] - 1][5]] for _z in range(CZ_N)]
_t_pics = CLK_ART["TART"](TF_LOOKS, TF_ZLOOK, CK_ISL)
for _n, _pic in sorted(_t_pics.items()):
    assert re.fullmatch(r"[A-Za-z0-9]+", _n) and _n not in CK_TEX, _n
    CK_TEX[_n] = MDIR + "Clk" + _n + ".png"
    SUI.register_map_textures([CK_TEX[_n]])
    MAP_ASSETS[MJAR + MDIR + "Clk" + _n + "@2x.png"] = _pic.png()
print("0.4.26 town art: %d pictures drawn in %.1f s (%d KB), %d monster looks for %d kinds"
      % (len(_t_pics), _time423.time() - _t_t0, sum(len(MAP_ASSETS[MJAR + MDIR + "Clk" + _n + "@2x.png"]) for _n in _t_pics) // 1024, len(TF_LOOKS), len(TF_ROWS)))
TF_NPIC = len(_t_pics)
assert TF_NPIC == len(TF_LOOKS) + 1 + 3 + 5 + 4, TF_NPIC
del _t_pics
''')

# ---------------------------------------------------------------------------------------------------- 5. the town's page parts (segments) + the Java branches
TOWN_PAGE = r'''# ---- 0.4.26 THE TOWN PAGE PARTS (Combat): the monster pictures (run time, per spot), the town islands, the six upgrade rows with the town's names + icons
# (the 0.4.23 row ids), the town map (5 zone panels with ONE town card each = the 0.4.23 card ids M0 / M3 / M6 / M9 / M12)
CK_PAGE_STATIC += ["public static final String[] T_MON = new String[] { %s };" % ", ".join(jlit(CK_TEX["TMon%d" % _i]) for _i in range(len(TF_LOOKS))),
                   "public static final String T_SLAIN = %s;" % jlit(CK_TEX["TSlain"])]
for _s in (1, 2, 3):
    lay = CK_LAY[_s]
    a_ = _ck_seg("tisl%d" % _s)
    a_.append((CK_SCN, SUI.map_pic(CKP + "Isl", lay["L"], lay["T"], lay["W"], lay["H"], CK_TEX["TIsl%d" % _s])))
TF_UP_NAMES = ["Warrior strength", "Town level", "Spirit warriors", "Warrior speed", "Town size", "Monster level"]
TF_UP_ICON = ["UpTStr", "UpTLvl", "UpSpirit", "UpTSpd", "UpIsize", "UpTMob"]
a_ = _ck_seg("tup")
a_.append((CK_BODY, G_.glass_group(CKP + "Up", CK_UPW, CK_BODY_H, role="panel", layout="Top", pad=12, anchor={"left": 12})))
a_.append((CK_UP, G_.glass_group(CKP + "UpH", CK_UIW, 32, layout="Left")))
a_.append(("#" + CKP + "UpH", _ck_glab(CKP + "UpT", 18, "gold", 150, 32, bold=True, text="UPGRADES")))
a_.append(("#" + CKP + "UpH", _ck_glab(CKP + "UpCap", 13, "dim", CK_UIW - 150, 32, halign="End")))
for _r in range(6):
    R_ = CKP + "U%d" % _r
    a_.append((CK_UP, G_.glass_group(R_, CK_UIW, CK_ROW_H, role="inset", layout="Left", pad=6, anchor={"top": 5})))
    a_.append(("#" + R_, "Group #%sI { Anchor: (Width: 64, Height: %d); }" % (R_, CK_ROW_H - 12)))
    a_.append(("#" + R_ + "I", SUI.map_pic(R_ + "P", 4, 6, 56, 56, CK_TEX[TF_UP_ICON[_r]])))
    a_.append(("#" + R_, G_.glass_group(R_ + "T", CK_TXT_W, CK_ROW_H - 12, layout="Top", anchor={"left": 8})))
    a_.append(("#" + R_ + "T", G_.glass_group(R_ + "N", CK_TXT_W, 26, layout="Left")))
    a_.append(("#" + R_ + "N", _ck_glab(R_ + "Nm", 17, "title", 250, 26, bold=True, text=TF_UP_NAMES[_r])))
    a_.append(("#" + R_ + "N", _ck_glab(R_ + "L", 15, "xp", CK_TXT_W - 250, 26, bold=True, halign="End")))
    a_.append(("#" + R_ + "T", _ck_glab(R_ + "E", 15, "text", CK_TXT_W, 24)))
    a_.append(("#" + R_ + "T", _ck_glab(R_ + "C", 14, "goldHi", CK_TXT_W, 22)))
    a_.append(("#" + R_ + "T", G_.glass_group(R_ + "B", CK_TXT_W, 34, layout="Left")))
    a_.append(("#" + R_ + "B", "Group { Anchor: (Width: %d); }" % (CK_TXT_W - 150)))
TF_CARDS = [3 * _z for _z in range(5)]
a_ = _ck_seg("tmap")
a_.append((CK_BODY, G_.glass_group(CKP + "Map", CK_IW, CK_BODY_H, layout="Left")))
for _z in range(5):
    Z_ = CKP + "Z%d" % _z
    a_.append(("#" + CKP + "Map", G_.glass_group(Z_, CK_ZW, CK_BODY_H, role="panel", layout="Top", pad=10, anchor={"right": 13} if _z < 4 else None)))
    a_.append(("#" + Z_, _ck_glab(Z_ + "N", 18, "gold", CK_CW, 30, bold=True, text="ZONE %d TOWN" % (_z + 1))))
    a_.append(("#" + Z_, _ck_glab(Z_ + "S", 14, "dim", CK_CW, 24)))
    M_ = CKP + "M%d" % TF_CARDS[_z]
    a_.append(("#" + Z_, G_.glass_group(M_, CK_CW, CK_CARD_H, role="inset", layout="Top", pad=6, anchor={"top": 6})))
    a_.append(("#" + M_, "Group #%sG { Anchor: (Width: %d, Height: 140); }" % (M_, CK_CW - 12)))
    a_.append(("#" + M_ + "G", SUI.map_pic(M_ + "P", (CK_CW - 12 - 210) // 2, 0, 210, 140, CK_TEX["TMap%d" % _z])))
    a_.append(("#" + M_, _ck_glab(M_ + "N", 16, "title", CK_CW - 12, 22, bold=True)))
    a_.append(("#" + M_, _ck_wrap(M_ + "S", 13, "text", CK_CW - 12, 36)))
    a_.append(("#" + M_, G_.glass_group(M_ + "B", CK_CW - 12, 30, layout="Left")))
_TMAP_J = [_qj("tmap")]
for _z, _i in enumerate(TF_CARDS):
    _TMAP_J += ["  if (this.ckMLock[%d]) {" % _i, _qj("mlock%d" % _i), "  }",
                "  if (this.ckMB[%d] == 1) {" % _i, _qj("mopen%d" % _i), _ck_bind(CKP + "M%dX" % _i, '"km%d"' % _z),
                "  } else if (this.ckMB[%d] == 2) {" % _i, _qj("mbuy%d" % _i), _ck_bind(CKP + "M%dX" % _i, '"kb%d"' % _z), "  }",
                _ck_jset(CKP + "M%dN" % _i, "this.ckMN[%d]" % _i), _ck_jset(CKP + "M%dS" % _i, "this.ckMS[%d]" % _i)]
for _z in range(5):
    _TMAP_J.append(_ck_jset(CKP + "Z%dS" % _z, "this.ckZS[%d]" % _z))

'''
P.rep(r'''# the run-time templates (checked with samples)
_tex0 = CK_TEX["Tree1"]''', TOWN_PAGE + r'''# the run-time templates (checked with samples)
_tex0 = CK_TEX["Tree1"]''')
P.rep(r'''         _ck_jset(CKP + "Title", '(this.ckMine ? "MINING SHARD" : (this.ckFarm ? "FARMING SHARD" : "FORAGING SHARD"))'),   # 0.4.25''',
      r'''         _ck_jset(CKP + "Title", '(this.ckMine ? "MINING SHARD" : (this.ckFarm ? "FARMING SHARD" : (this.ckTown ? "COMBAT SHARD" : "FORAGING SHARD")))'),   # 0.4.25 / 0.4.26''')
P.rep(r'''         "  if (this.ckMode == 1 && this.ckMine) {"] + _QMAP_J + ["  } else if (this.ckMode == 1) {", "  if (this.ckFarm) {", _ckj("fmap"), "  } else {", _ckj("map"), "  }"]   # 0.4.25: the farm map''',
      r'''         "  if (this.ckMode == 1 && this.ckMine) {"] + _QMAP_J + ["  } else if (this.ckMode == 1 && this.ckTown) {"] + _TMAP_J + [   # 0.4.26: the town map
         "  } else if (this.ckMode == 1) {", "  if (this.ckFarm) {", _ckj("fmap"), "  } else {", _ckj("map"), "  }"]   # 0.4.25: the farm map''')
P.rep(r'''    _ck_j += ["  if (this.ckSz == %d) {" % _s, "  if (this.ckMine) {", _ckj("qisl%d" % _s), "  } else {", _ckj("isl%d" % _s), "  }"]''',
      r'''    _ck_j += ["  if (this.ckSz == %d) {" % _s, "  if (this.ckMine) {", _ckj("qisl%d" % _s), "  } else if (this.ckTown) {", _ckj("tisl%d" % _s), "  } else {", _ckj("isl%d" % _s), "  }"]   # 0.4.26: the town''')
P.rep(r'''    "  if (this.ckSz >= 1 && this.manage && @PKG@.ShCfg.CK_ON && (!this.ckMine || @PKG@.ShCfg.MQ_ON) && (!this.ckFarm || @PKG@.ShCfg.FQ_ON)) {   // the click squares over the trees / nodes / plots (on top of every picture)",''',
      r'''    "  if (this.ckSz >= 1 && this.manage && @PKG@.ShCfg.CK_ON && (!this.ckMine || @PKG@.ShCfg.MQ_ON) && (!this.ckFarm || @PKG@.ShCfg.FQ_ON) && (!this.ckTown || @PKG@.ShCfg.TF_ON)) {   // the click squares over the trees / nodes / plots / monsters (on top of every picture)",''')
P.rep(r'''          "  if (this.ckMine) {"] + _QUP_J + ["  } else {", "  if (this.ckFarm) {", _ckj("fup"), "  } else {", _ckj("up"), "  }", _ck_jset(CKP + "UpCap", "this.ckUpCap")]   # 0.4.25: the farm's rows''',
      r'''          "  if (this.ckMine) {"] + _QUP_J + ["  } else {", "  if (this.ckFarm) {", _ckj("fup"), "  } else if (this.ckTown) {", _ckj("tup"), "  } else {", _ckj("up"), "  }", _ck_jset(CKP + "UpCap", "this.ckUpCap")]   # 0.4.25: the farm's rows; 0.4.26 the town's''')
P.rep(r'''print("0.4.25 farm page: %d variants checked, elements: island at most %d + %d run-time = %d, map %s; %d Skyglass paths"
      % (len(F_VARS), max(_f_el[:-2]), CK_NSPOT * 2 + 1 + 40, F_ELEMENTS, _f_el[-2:], F_GLASS_N))
''', r'''print("0.4.25 farm page: %d variants checked, elements: island at most %d + %d run-time = %d, map %s; %d Skyglass paths"
      % (len(F_VARS), max(_f_el[:-2]), CK_NSPOT * 2 + 1 + 40, F_ELEMENTS, _f_el[-2:], F_GLASS_N))
# 0.4.26 the town variants: each size with its totems (spirit warriors) + the six rows on / off (no decorations / weather on a town); the town map with
# every card locked + bought, and every card open
T_VARS = []
for _s in (1, 2, 3):
    for _on in ("upon", "upoff"):
        v_ = SUI.Appends()
        for _n in ["frame", "mapb0", "frame2", "left", "tisl%d" % _s] + ["tot%d_%d" % (_s, _j) for _j in range(5)] + \
                ["cap", "colall", "stotab", "tup"] + ["%s%d" % (_on, _r) for _r in range(6)] + ["foot"]:
            v_.extend(CKA[_n])
        T_VARS.append(v_)
v_ = SUI.Appends()
for _n in ["frame", "mapb1", "frame2", "tmap"] + ["mlock%d" % _i for _i in TF_CARDS] + ["mbuy%d" % _i for _i in TF_CARDS] + ["foot"]:
    v_.extend(CKA[_n])
T_VARS.append(v_)
v_ = SUI.Appends()
for _n in ["frame", "mapb1", "frame2", "tmap"] + ["mopen%d" % _i for _i in TF_CARDS] + ["foot"]:
    v_.extend(CKA[_n])
T_VARS.append(v_)
for _i, v_ in enumerate(T_VARS):
    v_.check(CKP)
    _pri = sum(1 for p_, mk_ in v_ if 'TexturePath: "SkyyGlass/Primary.png"' in SUI.render(mk_))   # ui-data: counting the Skyglass Primary buttons
    assert _pri <= 1, "0.4.26 town variant %d: %d Primary buttons" % (_i, _pri)
SUI.assert_proven([mk_ for v_ in T_VARS for p_, mk_ in v_], what="SkyyShards 0.4.26 Combat town page")
T_GLASS_N = SUI.assert_glass_paths([mk_ for v_ in T_VARS for p_, mk_ in v_])
_t_el = [sum(SUI._strip_quoted(SUI.render(mk_)).count("{") for p_, mk_ in v_) for v_ in T_VARS]
T_ELEMENTS = max(_t_el[:-2]) + CK_NSPOT * 2 + 1 + 8 * 5
assert T_ELEMENTS < 1000 and max(_t_el[-2:]) < 1000, "0.4.26: the town page stays well under ~1,600 elements: %s / %s" % (T_ELEMENTS, _t_el)
print("0.4.26 town page: %d variants checked, elements: island at most %d + %d run-time = %d, map %s; %d Skyglass paths"
      % (len(T_VARS), max(_t_el[:-2]), CK_NSPOT * 2 + 1 + 40, T_ELEMENTS, _t_el[-2:], T_GLASS_N))
''')

# ---------------------------------------------------------------------------------------------------- 6. the page: the Combat footer, kopen, fill / act for the town
P.rep(r'''|| (this.kind == %d && @PKG@.ShCfg.CK_ON && @PKG@.ShCfg.FQ_ON);   // 0.4.23: the Foraging Shard's footer opens the clicker; 0.4.24: the Mining Shard's the quarry; 0.4.25: the Farming Shard's the farm" % (CK_FK, MQ_K, FQ_K),''',
      r'''|| (this.kind == %d && @PKG@.ShCfg.CK_ON && @PKG@.ShCfg.FQ_ON) || (this.kind == %d && @PKG@.ShCfg.CK_ON && @PKG@.ShCfg.TF_ON);   // 0.4.23: the Foraging Shard's footer opens the clicker; 0.4.24: the Mining Shard's the quarry; 0.4.25: the Farming Shard's the farm; 0.4.26: the Combat Shard's the town" % (CK_FK, MQ_K, FQ_K, TF_K),''')
P.rep(r'''    if (this.view != 0 || (this.kind != @PKG@.ShClk.FK && this.kind != @PKG@.ShClk.MK && this.kind != @PKG@.ShClk.CRK)) return "";
    if (!@PKG@.ShCfg.CK_ON) return "-The shard clicker is switched off on this server.";
    if (this.kind == @PKG@.ShClk.MK && !@PKG@.ShCfg.MQ_ON) return "-The Mining quarry is switched off on this server.";   // 0.4.24
    if (this.kind == @PKG@.ShClk.CRK && !@PKG@.ShCfg.FQ_ON) return "-The Farming clicker is switched off on this server.";   // 0.4.25''',
      r'''    if (this.view != 0 || (this.kind != @PKG@.ShClk.FK && this.kind != @PKG@.ShClk.MK && this.kind != @PKG@.ShClk.CRK && this.kind != @PKG@.ShClk.TK)) return "";
    if (!@PKG@.ShCfg.CK_ON) return "-The shard clicker is switched off on this server.";
    if (this.kind == @PKG@.ShClk.MK && !@PKG@.ShCfg.MQ_ON) return "-The Mining quarry is switched off on this server.";   // 0.4.24
    if (this.kind == @PKG@.ShClk.CRK && !@PKG@.ShCfg.FQ_ON) return "-The Farming clicker is switched off on this server.";   // 0.4.25
    if (this.kind == @PKG@.ShClk.TK && !@PKG@.ShCfg.TF_ON) return "-The Combat town is switched off on this server.";   // 0.4.26''')
P.rep(r'''  else if (this.view == 5 && this.kind == @PKG@.ShClk.CRK) fillFarm(k, cs, ref, st);   // 0.4.25
''', r'''  else if (this.view == 5 && this.kind == @PKG@.ShClk.CRK) fillFarm(k, cs, ref, st);   // 0.4.25
  else if (this.view == 5 && this.kind == @PKG@.ShClk.TK) fillTown(k, cs, ref, st);   // 0.4.26
''')
P.rep("  this.ckMine = true;\n  this.ckFarm = false;   // 0.4.25\n", "  this.ckMine = true;\n  this.ckFarm = false;   // 0.4.25\n  this.ckTown = false;   // 0.4.26\n")
P.rep("   // 0.4.24\n  this.ckFarm = false;   // 0.4.25\n", "   // 0.4.24\n  this.ckFarm = false;   // 0.4.25\n  this.ckTown = false;   // 0.4.26\n")
P.rep("  this.ckFarm = true;   // 0.4.25: the farm\n", "  this.ckFarm = true;   // 0.4.25: the farm\n  this.ckTown = false;   // 0.4.26\n")
TOWN_FILL = r'''# 0.4.26 THE TOWN PAGE (tools/shards_0_4_26_patch.py): the Combat Shard's view 5 - the town of the shown zone island (its monsters per spot from
# ShClk.roleAt, the slain ones while their place fills again), the six town rows, the town map (5 towns, the class level zone locks)
M(page, r"""
public void fillTown(String k, @IC@[] cs, @REF@ ref, @ST@ st) {
  this.kind = @PKG@.ShClk.TK;
  int kd = this.kind;
  this.key = k;
  this.title = "Combat Shard";
  this.ckMine = false; this.ckTexA = null; this.ckTexB = null; this.ckQSm = 0; this.ckQPct = 0; this.ckZone = 0;
  this.ckFarm = false;
  this.ckTown = true;
  this.ckUpL = new String[6]; this.ckUpE = new String[6]; this.ckUpC = new String[6]; this.ckUpOk = new boolean[6]; this.ckUpSeen = new int[6];
  for (int i = 0; i < 6; i++) { this.ckUpL[i] = ""; this.ckUpE[i] = ""; this.ckUpC[i] = ""; this.ckUpOk[i] = false; this.ckUpSeen[i] = 0; }
  this.ckMN = new String[15]; this.ckMS = new String[15]; this.ckMB = new int[15]; this.ckMLock = new boolean[15]; this.ckMCur = new boolean[15];
  for (int i = 0; i < 15; i++) { this.ckMN[i] = ""; this.ckMS[i] = ""; this.ckMB[i] = 0; this.ckMLock[i] = false; this.ckMCur[i] = false; }
  this.ckZS = new String[5];
  for (int i = 0; i < 5; i++) this.ckZS[i] = "";
  this.ckSto = new String[3];
  for (int i = 0; i < 3; i++) this.ckSto[i] = "";
  this.ckGrow = new boolean[@PKG@.ShClk.NSPOT];
  this.ckSz = 0; this.ckTn = 0; this.ckSpN = 0; this.ckWx = 0; this.ckDeco = 0; this.ckAmt = 0; this.ckNs = 0; this.ckT = -1; this.ckTi = 0; this.ckNext = -1;
  this.ckTree = T_MON[0]; this.ckStump = T_SLAIN;
  this.ckChip = "No town yet"; this.ckCap = ""; this.ckUpCap = "";
  if (this.ckPop == null) this.ckPop = "";
  this.ckHand = handId(ref, st);
  this.ckAxe = @PKG@.ShClk.weapTier(this.ckHand);   // 0 = bare hands / not a weapon
  this.mine = k != null && this.me != null && k.equals(@PKG@.ShCfg.pkey(this.me));
  this.manage = k != null && @PKG@.ShRole.mayManage(this.me, k);
  this.bagT = 0L;
  this.sgN = 0; this.sgId = new String[0]; this.sgIc = new String[0]; this.sgQty = new String[0]; this.sgBg = new String[0]; this.sgHint = "Nothing is stored here yet.";
  this.ckInfo = this.ckAxe > 0 ? "Fighting with your " + @PKG@.ShTotem.pretty(this.ckHand) + " (T" + this.ckAxe + ") - click kills give " + @PKG@.ShCfg.CK_XP_PCT + " % of world class XP"
      : "Hold a weapon to fight - the town fights with the weapon in your hand.";
  if (!@PKG@.ShCfg.CK_ON || !@PKG@.ShCfg.TF_ON) this.ckInfo = "The Combat town is switched off on this server.";
  java.util.Properties p = k == null ? null : @PKG@.ShStore.get(k);
  if (p == null) { this.ckCap = k == null ? "Only the island owner and co-op members can use this shard." : "This shard's file could not be read."; return; }
  int LN = @PKG@.ShIsl.LADN[kd];
  int L0 = @PKG@.ShIsl.LAD0[kd];
  int lv = @PKG@.ShIsl.level(this.me, kd);   // the bridges before the store lock (the class level for the zone locks; the owner's level for the monsters)
  this.ckLv = lv;
  int olv = @PKG@.ShCombat.ownerLv(k);
  double[] tcv = new double[LN];
  for (int i = 0; i < LN; i++) tcv[i] = @PKG@.ShCfg.curve(@PKG@.ShIsl.band(@PKG@.ShIsl.TIER[L0 + i]));
  long now = @PKG@.ShCore.now();
  if (this.ckAxe > 0 && @PKG@.ShCfg.CK_ON && @PKG@.ShCfg.TF_ON) {   // fixer: say it when SkyySkills refused this player's class XP (ShClk.payClass)
    String cls0 = @PKG@.ShClk.classSkill(this.me);
    if (cls0 != null && !@PKG@.ShClk.classXpOk(this.me, cls0, now)) this.ckInfo = "Fighting with your " + @PKG@.ShTotem.pretty(this.ckHand) + " (T" + this.ckAxe + ") - no class XP: " + @PKG@.ShClk.noXpWhy(cls0);
  }
  int[] owned = new int[LN];
  int[] osz = new int[LN];
  Object[] gd = null;
  int t = -1; int sz = 0; int amt = 0; int ml = 0; int sp = 0; int ns = 0; int tot = 0; double rate = 0.0; long sto = 0L; long cap = 0L; String offw = "";
  @PKG@.ShStore.LOCK.lock(); try {
    @PKG@.ShMath.settleAll(kd, p, now);
    for (int i = 0; i < LN; i++) { owned[i] = @PKG@.ShIsl.slotOf(kd, p, L0 + i); osz[i] = owned[i] >= 0 ? @PKG@.ShMath.size(kd, p, owned[i]) : 0; }
    if (this.ckSlot < 0 || this.ckSlot >= @PKG@.ShMath.SLOTS || !@PKG@.ShMath.hasIsland(kd, p, this.ckSlot)) {
      this.ckSlot = -1;
      for (int i = 0; i < LN && this.ckSlot < 0; i++) if (owned[i] >= 0) this.ckSlot = owned[i];
    }
    if (this.ckSlot >= 0) {
      int s = this.ckSlot;
      t = @PKG@.ShIsl.ty(kd, p, s); sz = @PKG@.ShMath.size(kd, p, s);
      amt = @PKG@.ShIsl.sub(p, kd, s, 0); ml = @PKG@.ShIsl.sub(p, kd, s, 1); sp = @PKG@.ShIsl.sub(p, kd, s, 2);
      ns = @PKG@.ShClk.nsize(p, kd, s); tot = @PKG@.ShMath.totems(kd, p, s); rate = @PKG@.ShMath.rate(kd, p, s, now);
      sto = @PKG@.ShMath.usedOf(kd, p, s); cap = @PKG@.ShMath.limOf(kd, p, s);
      offw = @PKG@.ShIsl.offWords(kd, p, @PKG@.ShIsl.offLv(kd, p));
    }
    gd = @PKG@.ShCore.gridOf(kd, p);
    this.ckNext = @PKG@.ShIsl.nextTier(kd, p);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  gridFill(gd, kd);   // after the lock
  if (t >= 0) {
    this.ckT = t; this.ckTi = t - L0; this.ckSz = sz; this.ckAmt = amt; this.ckDeco = 0; this.ckWx = 0; this.ckNs = ns;   // a town has no decorations / weather totem
    this.ckSpN = tot > 5 ? 5 : tot;
    int z = @PKG@.ShCombat.zoneOf(t);
    int tl = @PKG@.ShClk.townLv(sz, amt);
    int kn = @PKG@.ShClk.kindsAt(z, tl);
    int zn = @PKG@.ShClk.zN(z);
    this.ckTn = @PKG@.ShClk.atOnceZ(z, sz, amt);   // fixer: a maxed town = every kind at once
    this.ckTexA = new String[@PKG@.ShClk.NSPOT];
    String key2 = k + "|" + kd + "|" + this.ckSlot;   // the town's own memory (= ShClk.fight)
    for (int i = 0; i < this.ckTn; i++) {
      this.ckGrow[i] = @PKG@.ShClk.readyAt(key2, i) > now;
      int gi = @PKG@.ShClk.roleAt(z, tl, i, @PKG@.ShClk.arrivals(key2, i), this.ckTn, key2);
      if (gi >= 0 && @PKG@.ShClk.T_PIC[gi] < T_MON.length) this.ckTexA[i] = T_MON[@PKG@.ShClk.T_PIC[gi]];
    }
    this.ckChip = @PKG@.ShIsl.tname(t) + " Town - " + ckSize(sz);
    this.ckSto[0] = "Spirit warriors: " + tot + (tot == 1 ? " Soul Cage fights" : " Soul Cages fight") + " for this town";
    this.ckSto[1] = "Rate: " + @PKG@.ShCfg.dec(rate) + " drops a minute while you are away";
    this.ckSto[2] = "Stored here " + @PKG@.ShCfg.num(sto) + " / " + @PKG@.ShCfg.num(cap) + " - offline " + offw;
    this.ckCap = "Click a monster to fight it (" + this.ckTn + " at once, " + kn + " of " + zn + " kinds, town level " + tl + " / " + @PKG@.ShClk.TL_MAX + "). Your spirit warriors keep fighting while you are away.";
    double cv = this.ckTi >= 0 && this.ckTi < LN ? tcv[this.ckTi] : 1.0;
    int mx = @PKG@.ShCfg.TF_NS_MAX;
    // 0 Warrior strength (new: the Tree size purchase)
    this.ckUpL[0] = "Lv " + ns + " / " + mx; this.ckUpSeen[0] = ns;
    if (ns >= mx) this.ckUpE[0] = "Your clicks hit +" + @PKG@.ShClk.strPct(ns) + " % (highest)";
    else {
      this.ckUpE[0] = "Your clicks hit +" + @PKG@.ShClk.strPct(ns) + " % -> +" + @PKG@.ShClk.strPct(ns + 1) + " %";
      this.ckUpC[0] = ckCost(@PKG@.ShClk.nodeCoins(ns + 1, cv), @PKG@.ShClk.nodeMats(kd, t, ns + 1));
      this.ckUpOk[0] = this.mine;
    }
    // 1 Town level = Mobs at once (sub 0): more monsters at once + more kinds
    this.ckUpL[1] = "Lv " + tl + " / " + @PKG@.ShClk.TL_MAX; this.ckUpSeen[1] = amt;
    if (amt >= 5) this.ckUpE[1] = this.ckTn + " at once, " + kn + " of " + zn + " kinds" + (sz < 3 ? " - grow the town for more" : " - every kind attacks");
    else {
      this.ckUpE[1] = "At once " + this.ckTn + " -> " + @PKG@.ShClk.atOnceZ(z, sz, amt + 1) + ", kinds " + kn + " -> " + @PKG@.ShClk.kindsAt(z, @PKG@.ShClk.townLv(sz, amt + 1)) + " of " + zn;
      this.ckUpC[1] = ckCost(@PKG@.ShIsl.coins(@PKG@.ShIsl.subH(sz, amt + 1), cv), @PKG@.ShIsl.mats(kd, t, @PKG@.ShCombat.subMat(kd, 0), sz - 1, (long) (amt + 1)));
      this.ckUpOk[1] = this.mine;
    }
    // 2 Spirit warriors = the Soul Cages (the Totems tab): they kill while you are away
    this.ckUpL[2] = tot + (tot == 1 ? " Soul Cage" : " Soul Cages"); this.ckUpSeen[2] = tot;
    this.ckUpE[2] = "Spirit warriors kill for you, also while you are away";
    this.ckUpC[2] = "Place and tier up Soul Cages on the Totems tab (kill speed)";
    this.ckUpOk[2] = true;
    // 3 Warrior speed = Spawn speed (sub 2): the spirit warriors (Soul Cages) kill faster while you are away (ShIsl.mult -> cbSpawnX) + the next monster comes sooner
    this.ckUpL[3] = "Lv " + sp + " / 5"; this.ckUpSeen[3] = sp;
    if (sp >= 5) this.ckUpE[3] = "Warriors kill faster while away - a new monster every " + @PKG@.ShCfg.dec((double) @PKG@.ShClk.townRespawnMs(sz, sp) / 1000.0) + " s" + (sz < 3 ? " - grow the town for more" : " (highest)");
    else {
      this.ckUpE[3] = "Warriors kill faster while away - a new monster every " + @PKG@.ShCfg.dec((double) @PKG@.ShClk.townRespawnMs(sz, sp) / 1000.0) + " s -> " + @PKG@.ShCfg.dec((double) @PKG@.ShClk.townRespawnMs(sz, sp + 1) / 1000.0) + " s";
      this.ckUpC[3] = ckCost(@PKG@.ShIsl.coins(@PKG@.ShIsl.subH(sz, sp + 1), cv), @PKG@.ShIsl.mats(kd, t, @PKG@.ShCombat.subMat(kd, 2), sz - 1, (long) (sp + 1)));
      this.ckUpOk[3] = this.mine;
    }
    // 4 Town size = Grow (needs the three at 5 / 5 / 5)
    this.ckUpL[4] = ckSize(sz) + " (" + sz + " / 3)"; this.ckUpSeen[4] = sz;
    if (sz >= 3) this.ckUpE[4] = "Large - the biggest town";
    else {
      this.ckUpE[4] = ckSize(sz) + " -> " + ckSize(sz + 1) + ": town level " + @PKG@.ShClk.townLv(sz + 1, 0) + "+, up to " + @PKG@.ShClk.atOnceZ(z, sz + 1, 5) + " at once";
      if (amt < 5 || sp < 5 || ml < 5) this.ckUpC[4] = "First Town level, Warrior speed and Monster level 5/5 (" + amt + ", " + sp + ", " + ml + ")";
      else { this.ckUpC[4] = ckCost(@PKG@.ShIsl.coins(@PKG@.ShIsl.growH(sz + 1), cv), @PKG@.ShIsl.mats(kd, t, @PKG@.ShCfg.MAT_GROW, sz - 1, 1L)); this.ckUpOk[4] = this.mine; }
    }
    // 5 Monster level = Mob level (sub 1): stronger monsters, more loot + XP
    this.ckUpL[5] = "Lv " + ml + " / 5"; this.ckUpSeen[5] = ml;
    if (ml >= 5) this.ckUpE[5] = "Monsters Lv " + @PKG@.ShCombat.lvTxtP(olv, z, sz, ml) + (sz < 3 ? " - grow the town for more" : " (highest)");
    else {
      this.ckUpE[5] = "Monsters Lv " + @PKG@.ShCombat.lvTxtP(olv, z, sz, ml) + " -> " + @PKG@.ShCombat.lvTxtP(olv, z, sz, ml + 1) + ": more XP";
      this.ckUpC[5] = ckCost(@PKG@.ShIsl.coins(@PKG@.ShIsl.subH(sz, ml + 1), cv), @PKG@.ShIsl.mats(kd, t, @PKG@.ShCombat.subMat(kd, 1), sz - 1, (long) (ml + 1)));
      this.ckUpOk[5] = this.mine;
    }
    this.ckUpCap = this.mine ? "coins + " + @PKG@.ShTotem.pretty(@PKG@.ShIsl.tok(kd, t, "ench")) + " / the zone's drops" : "the town owner buys upgrades";
  } else this.ckCap = "No Combat island yet - open Islands to buy the first one.";
  // the town map: one town a zone (cards 0 / 3 / 6 / 9 / 12; the class level zone locks = buyIsland's)
  for (int i = 0; i < LN && i < 5; i++) {
    int tt = L0 + i;
    int c = 3 * i;
    int need = @PKG@.ShCombat.need(i);
    boolean open = need <= 0 || lv >= need;
    this.ckMN[c] = @PKG@.ShIsl.tname(tt) + " Town";
    this.ckMCur[c] = owned[i] >= 0 && owned[i] == this.ckSlot;
    this.ckMLock[c] = !open && owned[i] < 0;
    if (owned[i] >= 0) { this.ckMS[c] = (this.ckMCur[c] ? "Shown now - " : "Yours - ") + ckSize(osz[i]); this.ckMB[c] = this.ckMCur[c] ? 0 : 1; }
    else if (!open) this.ckMS[c] = "Locked: class level " + need;
    else if (i == this.ckNext) {
      this.ckMS[c] = "Buy: " + ckCost(@PKG@.ShIsl.coins(@PKG@.ShCfg.BUY_H, tcv[i]), @PKG@.ShIsl.mats(kd, tt, @PKG@.ShCfg.BUY_ITEMS[kd], 0, 1L));
      this.ckMB[c] = this.mine ? 2 : 0;
    }
    else this.ckMS[c] = "Buy the towns before it first";
    this.ckZS[i] = need <= 0 ? "Open" : (open ? "Open - class level " + need : "Locked - class level " + need + (lv >= 0 ? " (you: " + lv + ")" : ""));
  }
}""")
# 0.4.26: a town action is fresh only while the page still shows this profile's town of that zone in that slot (a profile switch / another island = stale)
M(page, r"""
public boolean townFresh(String k, int slot) {
  if (k == null || this.key == null || !k.equals(this.key) || this.ckT < 0) return false;
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return false;
  boolean ok;
  @PKG@.ShStore.LOCK.lock(); try {
    ok = slot >= 0 && slot < @PKG@.ShMath.SLOTS && @PKG@.ShMath.hasIsland(@PKG@.ShClk.TK, p, slot) && @PKG@.ShIsl.ty(@PKG@.ShClk.TK, p, slot) == this.ckT;
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  return ok;
}""")
'''
_FC0 = 'M(page, r"""\npublic void fillClick(String k, @IC@[] cs, @REF@ ref, @ST@ st) {'
P.rep(_FC0, TOWN_FILL + _FC0)
# actClick serves the town too: its kind, the stale-town guard on a monster click and an upgrade
P.rep(r'''  int kd = this.kind == @PKG@.ShClk.CRK ? @PKG@.ShClk.CRK : @PKG@.ShClk.FK;   // 0.4.25: the Farming clicker shares this page''',
      r'''  int kd = this.kind == @PKG@.ShClk.CRK ? @PKG@.ShClk.CRK : (this.kind == @PKG@.ShClk.TK ? @PKG@.ShClk.TK : @PKG@.ShClk.FK);   // 0.4.25: the Farming clicker shares this page; 0.4.26 the Combat town''')
P.rep(r'''    if (kd == @PKG@.ShClk.CRK && !farmFresh(k, slot)) return "=The page is up to date now.";   // 0.4.25: a stale farm island
''', r'''    if (kd == @PKG@.ShClk.CRK && !farmFresh(k, slot)) return "=The page is up to date now.";   // 0.4.25: a stale farm island
    if (kd == @PKG@.ShClk.TK && !townFresh(k, slot)) return "=The page is up to date now.";   // 0.4.26: a stale town
''')
P.rep(r'''    if (kd == @PKG@.ShClk.CRK && !farmFresh(k, s)) return "=The page is up to date now - click Upgrade again.";   // 0.4.25: a stale farm island
''', r'''    if (kd == @PKG@.ShClk.CRK && !farmFresh(k, s)) return "=The page is up to date now - click Upgrade again.";   // 0.4.25: a stale farm island
    if (kd == @PKG@.ShClk.TK && !townFresh(k, s)) return "=The page is up to date now - click Upgrade again.";   // 0.4.26: a stale town
''')
P.rep(r'''          "public boolean ckFarm;"):   # 0.4.25 the farm''', r'''          "public boolean ckFarm;",   # 0.4.25 the farm
          "public boolean ckTown;"):   # 0.4.26 the town''')

# ---------------------------------------------------------------------------------------------------- 7. the ready line
P.rep(r'''log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.25:''', r'''log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.26: the Combat town (Shard clicker in the Combat Shard menu: fight the zone's monsters with your weapon, easiest kinds first, Warrior strength, loot into the town's storage, class XP; Foraging / Mining clicker memory per kind); 0.4.25:''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
_i = P.s.index
assert _i("public static Object[] fight(java.util.UUID u") < _i("public static Object[] chop(java.util.UUID u"), "fight() compiled before chop()"
assert _i("public static Object[] harvest(java.util.UUID u") < _i("public static Object[] fight(java.util.UUID u"), "harvest before fight (part, addTo, rnd, qName)"
assert _i("public static int strPct(int ns)") < _i("public static String buyNode("), "strPct before buyNode"
assert _i("public void fillTown(") < _i("public void build0("), "fillTown before build0"
assert _i("public boolean townFresh(") < _i("public String actClick("), "townFresh before actClick"
assert _i("public static int ownerLv(String k)") < _i("public static Object[] fight(java.util.UUID u"), "ShCombat before ShClk"
P.finish()
