"""Derive SkyyShards/build_skyyshards_0.4.27.py from the GENERATED SkyyShards 0.4.26 (build_skyyshards_0.4.26.py = the tools/deploy_set.py SET
pin, made by tools/shards_0_4_26_patch.py - edit the patch, never the generated file). Every anchor is asserted once; at the end every change
is undone on a copy and compared with 0.4.26 (tools/soundpass_gen.Patch). Line endings kept.
Run:   python tools/shards_0_4_27_patch.py   then   python SkyyShards/build_skyyshards_0.4.27.py   (never --deploy)
Check: python SkyyShards/test_skyyshards_0.4.27.py

0.4.27 (2026-11-21) = SHARDS BECOME CLICKER-ONLY (round shardx1; Skyy 2026-11-21 docs/answered/world.md "SHARD WORLD -> CLICKER ONLY": "the goal is to
  compleatly replace this with the clicker system, instead of keeping both at once."; "SHARD UPGRADES + TOTEMS -> CLICKER": "replacing this upgrade system,
  with this. and we need to get the totem system working simply and ewasily in this clicker side. cause the current totem thing is bugged, complicated and
  annoying."; "MINING QUARRY CLICKER": "make it a little more clear how much each thing costs, and i need a way for an auto smelt upgrade."; "CLICKER
  BALANCE = SELF-SUSTAINING": "lets make sure we balance the clickers so everything to keep upgrading them can be gotten in the clicker, except maybe main
  island upgrades, and island you need birch to make the birch island so you have to find the tree type first kinda thing."; docs/answered/economy.md
  "MOB COINS": "but the combat one should drop coins from the mobs too."; research/Shard-Clicker-Idea.md suggestion 6).
  SPEC (short; the survey first):
  - SURVEY. Vanilla (Assets.zip): no clicker / idle-upgrade page (0.4.23-0.4.26 surveys). Mods: pie-clicker (learn only, 0.4.23). Nothing new packed.
    The 0.4.23-0.4.26 clickers already READ every island key the walkable shard used (type / size / amt / deco / irr / totems / stored / legacy /
    drops / nsize / luck / smithy), so islands, sub-upgrades, totems and stored items are already "in the clicker"; this round removes the other path.
  - 1. THE WALKABLE SHARD WORLDS ARE RETIRED: Enter Shard is gone (ShWorld2.enter refuses: no new shard world is ever made or loaded by us); the
    Foraging / Mining / Farming / Combat portal (right-click) opens the shard's CLICKER PAGE directly (ShPageFn: view 5); the old menu is never shown
    for those four (the rail of another shard leads to its clicker). A totem block / Totem Bench inside an old shard world opens nothing (a chat line
    says why); the hub stand inside keeps its Back to Island button (a player who logged out inside walks out). Old shard world folders stay on disk untouched
    (the engine still loads every folder at start; our idle check unloads them after shard.unloadSec as before).
    Ranching + Orchard have no clicker yet: they keep their old menu WITHOUT Enter Shard (Collect / Map / Totems tabs) until their clicker exists
    (QUESTION for Skyy, default [keep their menu until their clicker round]).
  - 2. THE CLICKER'S "UPGRADES" BUTTON (top bar, was "Shard menu") opens the SHARD UPGRADES view (ckMode 2) on the same page: left the island's
    SPIRIT TOTEM (tier, 2 modifier slots, the island's other totems listed, "place a totem item you carry" = the old pad placing, data only); right
    the shard-wide upgrades that lived on the old Map / Collect tabs: Storage, Auto-Compactor, Time Compressor, Automation, Offline Harvest (their
    existing ShCore purchases + costs), Sell all (this island's stock, 2 clicks), Pick up Shard (2 clicks). Islands (the map) keeps buying islands.
  - 3. SIMPLE TOTEMS (Skyy's default, world.md): the island's spirit = its first WORKER totem of this shard (Lumber / Quarry / Harvest Spirit, Soul
    Cage). The "Spirit" row (row 2 of every clicker + the upgrades view) BUYS one (tier I, when the island has none) or TIERS IT UP (I..V), cost =
    click.totem.hours[tier] hours of the coin curve at the island's tier + click.totem.ench[tier] of the island's Enchanted item; its effect is the
    island's output a minute now -> after (the real ShMath.rate on a copy). 2 MODIFIER SLOTS = the spirit's own m1 / m2 (Wider / Faster / Replant /
    Compost / Storage - Rare Finder works on bonus totems only, so not offered): pick with < >, Add / Swap on the page; cost = one of that modifier
    item if you carry one (inventory + bags: old items keep their value), else click.totem.modHours + click.totem.modEnch; a swapped-out modifier
    goes into the island's storage as its item (Collect gives it back - nothing lost). No Totem Bench, no pads, no hand-held use on the page, no
    boosters (a booster already burning burns out as before). The island's other totems (support poles, extra workers, hand-placed poles) keep
    working exactly as before and are listed.
    TOTEM ITEMS YOU OWN: kept + useful - "Place one" puts the first totem item of this shard from your inventory onto the shown island (the old
    pad rules: the pad count of its size; the uid dupe guard). TOTEM BENCH blocks / items: kept harmless (no refund: a bench inside a shard world
    opens nothing, outside one it never opened; a bench item stays an item) - the bench tier cap no longer applies (every tier is on the page).
    Hand-held Rain / Fertilizer / Sun Totem I keep working in the overworld as before.
  - 4. COSTS CLEAR: every clicker row (and the upgrades view) shows each cost part on its own line "have / need item" (coins first), GREEN when you
    have it, RED when not (inventory + bags, as the purchase pays); a row without a price shows its reason in up to 3 short lines (never cut off:
    word-wrapped at 34 characters). The rows sit in a scroll list (Mining's 8 rows scroll; 6 rows fit).
  - 5. AUTO-SMELT: the quarry's Smithy row BUYS Smithy I on the page = an Auto-Smelt Pole entry on the quarry's base island (the 0.3 totem; data
    0.4.26 reads too), cost click.mine.smithy1Hours (0.1) h + click.mine.smithy1Ore (64) of the base island's ORE (the quarry mines it before it can
    smelt); then Smithy II (the alloy slider) at its 0.4.24 cost.
  - 6. BALANCE (self-sustaining): every island cost = coins + that island's own items (raw / Enchanted / its seeds); 0.4.26 had outside items in
    three rows: isl.mat.deco (Oak logs + Cobblestone on every shard), isl.mat.irrigation (Water Essence) and combat.mat.* (Void / Life / Water
    Essence) -> now raw / Enchanted of the island (ShMig0427, a one-time update of untouched default lines only, History first, Undo). Shard-wide
    rows (Storage / Compactor / Compressor / Automation / Offline Harvest) keep their items (Skyy's exception); a NEW island needs its own type from
    the world (isl.buyItems, Skyy's Birch example) - unchanged. The report tables every line.
  - 7. COMBAT TOWN COINS: a town kill also earns coins = SkyyMobs' mob:fn:killCoins (role, level) (0.1.26+; absent = no coins, said on the page),
    waiting in the town (combat.i<n>.coins, saved with the loot) until Collect all on the town page pays them (debit + save first, then the purse;
    a refused payment puts them back). Server Setup click.fight.coins (on).
  - 8. IMAGE SHRINK part 2 (tools/ci/ui_budget.py): the old Map tab pictures of the four clicker shards go (6 Base<Zone>@2x 1680 x 1376 -> only
    Ranching / Orchard stay, as 1x), the 43 range rings of the retired totem page go, the clicker map cards ship 1x (drawn at 210 x 140).
  - 9. ONE-TIME PER-PROFILE MIGRATION (ShStore.migrate3, marker clk.done=1, PROJECT-RULES 4): the seed / sapling stores of AUTOMATED shards (their
    totems never use them again) move into that island's storage as items (Collect / the grid give them back); History copy shards/history/
    clicker/<pkey>.pre-0.4.27.properties first (byte-checked), one save, collect.log line with the Undo; nothing else is rewritten (counts of
    islands / totems / items logged before = after). A non-automated shard keeps its store (it still replants): the store strip's "Give seeds" /
    "Take seeds" button serves it (the old seed buttons were on the retired pages).
  NUMBERS (new, Server Setup -> Shards -> Shard clicker): click.totem.hours 0.1,0.25,0.5,1,2, click.totem.ench 2,4,16,40,100, click.totem.modHours 0.5,
    click.totem.modEnch 16, click.mine.smithy1Hours 0.1, click.mine.smithy1Ore 64, click.fight.coins true. Changed defaults (ShMig0427): isl.mat.deco
    raw:16|ench:1|ench:2, isl.mat.irrigation raw:8|ench:1|ench:2, combat.mat.cap raw:16|raw:32,ench:1|raw:64,ench:2, combat.mat.level the same,
    combat.mat.speed raw:8|raw:16,ench:1|raw:32,ench:2.
  SAVED DATA: clk.done=1 (marker); combat.i<n>.coins (town coins not collected yet); spirit purchases / modifiers / Smithy I = ordinary <kind>.i<n>
    .totems entries (0.4.26 reads them); moved seeds = <kind>.i<n>.drops items + .seed=0.
  ROLLBACK 0.4.27 -> 0.4.26: Undo the ShMig0427 rows first (Server Setup > Shards > Changes); Collect all on the Combat town first (0.4.26 ignores
    combat.i<n>.coins - kept in the file, paid again when 0.4.27 is back). Moved seeds stay in storage (0.4.26's grid / Collect pay .drops). The
    walkable worlds come back with 0.4.26 (folders untouched).
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

HERE = os.path.join(ROOT, "SkyyShards")
P = G.Patch(os.path.join(HERE, "build_skyyshards_0.4.26.py"), os.path.join(HERE, "build_skyyshards_0.4.27.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.4.26"\n') and P.has("GENERATED by tools/shards_0_4_26_patch.py") and P.has("fillTown") and not P.has("ckSpirit"), "not the generated SkyyShards 0.4.26"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.27 (2026-11-21)"):].rstrip() + "\n"

# ---------------------------------------------------------------------------------------------------- 0. header + version
P.rep('''"""SkyyShards 0.4.26 - build script (javassist via jpype). GENERATED by tools/shards_0_4_26_patch.py from build_skyyshards_0.4.25.py
(generated by tools/shards_0_4_25_patch.py from 0.4.24, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.26" /''', '''"""SkyyShards 0.4.27 - build script (javassist via jpype). GENERATED by tools/shards_0_4_27_patch.py from build_skyyshards_0.4.26.py
(generated by tools/shards_0_4_26_patch.py from 0.4.25, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.27" / "0.4.26" /''')
P.rep('''Run:   python SkyyShards/build_skyyshards_0.4.26.py   -> SkyyShards/SkyyShards-0.4.26.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.26.py
''', '''Run:   python SkyyShards/build_skyyshards_0.4.27.py   -> SkyyShards/SkyyShards-0.4.27.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.27.py
''' + NOTE + '''
''')
P.rep('VERSION = "0.4.26"\n', 'VERSION = "0.4.27"\n')

# ---------------------------------------------------------------------------------------------------- 1. balance: island costs from the island
P.rep('''for _v in list(MAT48.values()) + BUY_ITEMS48:
    for _part in _v.replace("|", ",").split(","):
        _pid = _part.split(":")[0]
        assert _pid in ("raw", "ench", "seed", "eseed") or _pid in ITEMS or _pid in _SE.IDS, "0.4.8: material %s" % _pid
''', '''for _v in list(MAT48.values()) + BUY_ITEMS48:
    for _part in _v.replace("|", ",").split(","):
        _pid = _part.split(":")[0]
        assert _pid in ("raw", "ench", "seed", "eseed") or _pid in ITEMS or _pid in _SE.IDS, "0.4.8: material %s" % _pid
# 0.4.27 CLICKER BALANCE (Skyy 2026-11-21 "everything to keep upgrading them can be gotten in the clicker"): an island's own upgrades cost only its own
# items (raw / Enchanted) + coins - Decorations (were Oak logs + Cobblestone on every shard), Irrigation (Water Essence) and the Combat rows (Void / Life /
# Water Essence) move onto the island's raw / Enchanted item. ShMig0427 moves the untouched default lines once (History first; Undo).
MIG0427 = [("isl.mat.deco", MAT48["deco"], "raw:16|ench:1|ench:2", "t"), ("isl.mat.irrigation", MAT48["irrigation"], "raw:8|ench:1|ench:2", "t")] + \\
          [("combat.mat.%s" % _mk, CZ_MAT[_i], _nv, "t") for _i, (_mk, _nv) in enumerate((("cap", "raw:16|raw:32,ench:1|raw:64,ench:2"),
                                                                                           ("level", "raw:16|raw:32,ench:1|raw:64,ench:2"),
                                                                                           ("speed", "raw:8|raw:16,ench:1|raw:32,ench:2")))]
MAT48["deco"], MAT48["irrigation"] = MIG0427[0][2], MIG0427[1][2]
for _i in range(3):
    CZ_MAT[_i] = MIG0427[2 + _i][2]
for _v in list(MAT48.values()) + CZ_MAT:
    for _part in _v.replace("|", ",").split(","):
        assert _part.split(":")[0] in ("raw", "ench", "eseed"), "0.4.27: an island cost names only the island's own items: %s" % _part
MIG0427_MK = "skyyshards-0.4.27-clicker"
MIG0427_LINE = "# ---------- SkyyShards 0.4.27 (marker %s, runs once): island upgrades cost the island's own items; only untouched old default lines were changed ----------" % MIG0427_MK
''')
P.rep('''    "# SkyyShards 0.4.20 defaults (marker %s): smaller storage, 20 %% XP, Mining ingots - keep this line." % MIG0420_MK,
''', '''    "# SkyyShards 0.4.20 defaults (marker %s): smaller storage, 20 %% XP, Mining ingots - keep this line." % MIG0420_MK,
    "# SkyyShards 0.4.27 defaults (marker %s): island upgrades cost the island's own items - keep this line." % MIG0427_MK,
''')

# ---------------------------------------------------------------------------------------------------- 2. ShCfg: the new settings
P.rep(r'''          "public static volatile int[] TF_ZT = new int[] { %s };" % ", ".join(str(_x) for _x in TF_ZT)):
    F(cfg, f)
''', r'''          "public static volatile int[] TF_ZT = new int[] { %s };" % ", ".join(str(_x) for _x in TF_ZT)):
    F(cfg, f)
# 0.4.27 (tools/shards_0_4_27_patch.py): simple totems, Smithy I on the page, town coins (Server Setup -> Shards -> Shard clicker)
TOT_H427 = [0.1, 0.25, 0.5, 1.0, 2.0]       # the spirit: buy (tier I), I->II .. IV->V - hours of the coin curve at the island's tier
TOT_E427 = [2, 4, 16, 40, 100]              # + this many of the island's Enchanted item (= 0.4.8's totem.upCost Enchanted counts, buy = 2)
for f in ("public static final double[] DEF_TOT_H = new double[] { %s };" % ", ".join(repr(_x) for _x in TOT_H427),
          "public static volatile double[] TOT_H = new double[] { %s };" % ", ".join(repr(_x) for _x in TOT_H427),
          "public static final int[] DEF_TOT_E = new int[] { %s };" % ", ".join(str(_x) for _x in TOT_E427),
          "public static volatile int[] TOT_E = new int[] { %s };" % ", ".join(str(_x) for _x in TOT_E427),
          "public static volatile double MOD_H = 0.5;", "public static volatile int MOD_E = 16;",
          "public static volatile double MQ_S1H = 0.1;", "public static volatile int MQ_S1ORE = 64;", "public static volatile boolean TF_COINS = true;"):
    F(cfg, f)
''')
P.rep(r'''          "5 numbers, Zone 1..5: the weapon tier a zone's monsters count as (3 tiers above yours = refused).", "reload@config.properties:click.fight.zoneTier")]
''', r'''          "5 numbers, Zone 1..5: the weapon tier a zone's monsters count as (3 tiers above yours = refused).", "reload@config.properties:click.fight.zoneTier")]
# 0.4.27: simple totems, Smithy I, town coins
ROWS += [("click.totem.hours", "Spirit totem coins (curve hours)", "clicker", "text", ",".join("%g" % _x for _x in TOT_H427), "", "80", "", "", "live",
          "5 numbers: buy (tier I), then I->II .. IV->V - hours of the coin curve at the island's tier.", "reload@config.properties:click.totem.hours"),
         ("click.totem.ench", "Spirit totem Enchanted items", "clicker", "text", ",".join(str(_x) for _x in TOT_E427), "", "80", "", "", "live",
          "5 numbers: the island's Enchanted item to buy the spirit, then each tier up.", "reload@config.properties:click.totem.ench"),
         ("click.totem.modHours", "Totem modifier coins (curve hours)", "clicker", "dec", "0.5", "0", "1000", "", "", "live",
          "A modifier bought without a modifier item: hours of the coin curve at the island's tier.", "reload@config.properties:click.totem.modHours"),
         ("click.totem.modEnch", "Totem modifier Enchanted items", "clicker", "int", "16", "0", "100000", "", "", "live",
          "+ this many of the island's Enchanted item (a modifier item you carry pays instead).", "reload@config.properties:click.totem.modEnch"),
         ("click.mine.smithy1Hours", "Smithy I coins (curve hours)", "clicker", "dec", "0.1", "0", "1000", "", "", "live",
          "Smithy I (auto-smelt): hours of the coin curve at the quarry's tier.", "reload@config.properties:click.mine.smithy1Hours"),
         ("click.mine.smithy1Ore", "Smithy I ore", "clicker", "int", "64", "0", "100000", "", "", "live",
          "+ this many of the quarry's own ore.", "reload@config.properties:click.mine.smithy1Ore"),
         ("click.fight.coins", "Town: kills pay coins", "clicker", "bool", "true", "", "", "", "", "live",
          "On: town kills also earn SkyyMobs' kill coins, paid by Collect all on the town page.", "reload@config.properties:click.fight.coins")]
''')
P.rep(r'''          "  TF_ZT = intsOf(p.getProperty(\"click.fight.zoneTier\"), DEF_TF_ZT, 1, 20, \"click.fight.zoneTier\");"]
''', r'''          "  TF_ZT = intsOf(p.getProperty(\"click.fight.zoneTier\"), DEF_TF_ZT, 1, 20, \"click.fight.zoneTier\");"]
_load += ["  TOT_H = decsOf(p.getProperty(\"click.totem.hours\"), DEF_TOT_H, 0.0, 1000.0, \"click.totem.hours\");",   # 0.4.27
          "  TOT_E = intsOf(p.getProperty(\"click.totem.ench\"), DEF_TOT_E, 0, 100000, \"click.totem.ench\");",
          "  MOD_H = decOf(p.getProperty(\"click.totem.modHours\"), 0.5, 0.0, 1000.0);",
          "  MOD_E = intOf(p.getProperty(\"click.totem.modEnch\"), 16, 0, 100000);",
          "  MQ_S1H = decOf(p.getProperty(\"click.mine.smithy1Hours\"), 0.1, 0.0, 1000.0);",
          "  MQ_S1ORE = intOf(p.getProperty(\"click.mine.smithy1Ore\"), 64, 0, 100000);",
          "  TF_COINS = bool(p.getProperty(\"click.fight.coins\"), true);"]
''')

# ---------------------------------------------------------------------------------------------------- 3. ShMig0427 (a copy of ShMig0420's reviewed machinery)
_a = P.s.index("# ================= 0.4.20 ShMig0420 (PROJECT-RULES 4;")
_b = P.s.index('M(smig420, r"""\npublic static synchronized String run(java.nio.file.Path f) {')
_b = P.s.index('}""")\n', _b) + len('}""")\n')
_m420 = P.s[_a:_b]
assert _m420.count("smig420") >= 8 and "MIG0420" in _m420
_m427 = (_m420.replace("smig420", "smig427").replace("ShMig0420", "ShMig0427").replace("MIG0420", "MIG0427").replace("0.4.20", "0.4.27")
         .replace("smaller storage, 20 % XP, Mining ingots", "island upgrades cost the island's own items")
         .replace("storage.tierN, shard.xpPercent, the Mining ore costs", "Decorations / Irrigation / Combat costs from the island's own items")
         .replace("(smaller storage 1k .. 50k an island, shards pay 20 % XP, Mining costs take ingots)", "(island upgrades cost the island's own items: Decorations, Irrigation, Combat)"))   # fix (critic): the INFO line named 0.4.20's change
assert "smaller storage 1k" not in _m427, "ShMig0427 INFO text"
assert "0.4.20" not in _m427 and "smig420" not in _m427 and "storage.tier" not in _m427, "ShMig0427 copy"
P.rep(_m420, _m420 + _m427)
P.rep('''  try { @PKG@.ShMig0420.run(@PKG@.ShCfg.FILE); }   // 0.4.20: untouched storage / XP / Mining ore lines, once (History first; Undo)
  catch (Throwable t) { @PKG@.ShCfg.warn("the 0.4.20 settings update was skipped: " + t); }
''', '''  try { @PKG@.ShMig0420.run(@PKG@.ShCfg.FILE); }   // 0.4.20: untouched storage / XP / Mining ore lines, once (History first; Undo)
  catch (Throwable t) { @PKG@.ShCfg.warn("the 0.4.20 settings update was skipped: " + t); }
  try { @PKG@.ShMig0427.run(@PKG@.ShCfg.FILE); }   // 0.4.27: untouched Decorations / Irrigation / Combat cost lines -> the island's own items, once (History first; Undo)
  catch (Throwable t) { @PKG@.ShCfg.warn("the 0.4.27 settings update was skipped: " + t); }
''')

# ---------------------------------------------------------------------------------------------------- 4. commitKeys: "\\u0001id:qty" = add to that .drops line AFTER the settle
P.rep('''    @PKG@.ShMath.settleAll(kd, p, now());   // production up to now at the old numbers
    for (int i = 0; i < keys.length; i++) p.setProperty(keys[i], vals[i]);
    String e = @PKG@.ShStore.save(k, p);''', '''    @PKG@.ShMath.settleAll(kd, p, now());   // production up to now at the old numbers
    for (int i = 0; i < keys.length; i++) {
      if (vals[i] != null && vals[i].length() > 0 && vals[i].charAt(0) == (char) 1) { p.setProperty(keys[i], addDrops(p.getProperty(keys[i]), vals[i].substring(1))); continue; }   // 0.4.27: a refund into storage, added after the settle
      p.setProperty(keys[i], vals[i]);
    }
    String e = @PKG@.ShStore.save(k, p);''')
P.rep('''M(core, r"""
public static String commitKeys(String k, int kd, java.util.Properties p, String[] keys, String[] vals, long ver) {''', '''# 0.4.27: a .drops line ("id:qty,id:qty") + more ("id:qty,..."), the same item merged (the order kept, new items at the end)
M(core, r"""
public static String addDrops(String cur, String add) {
  java.util.LinkedHashMap m = new java.util.LinkedHashMap();
  String[] parts = new String[] { cur == null ? "" : cur, add == null ? "" : add };
  for (int w = 0; w < 2; w++) {
    String[] a = parts[w].split(",");
    for (int i = 0; i < a.length; i++) {
      String v = a[i].trim();
      int c = v.lastIndexOf(':');
      if (c <= 0) continue;
      long q = 0L;
      try { q = Long.parseLong(v.substring(c + 1).trim()); } catch (Throwable t) { q = 0L; }
      if (q <= 0L) continue;
      String id = v.substring(0, c).trim();
      Object o = m.get(id);
      long h = o instanceof Long ? ((Long) o).longValue() : 0L;
      m.put(id, Long.valueOf(h + q));
    }
  }
  StringBuilder sb = new StringBuilder();
  java.util.Iterator it = m.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry en = (java.util.Map.Entry) it.next();
    if (sb.length() > 0) sb.append(',');
    sb.append((String) en.getKey()).append(':').append(((Long) en.getValue()).longValue());
  }
  return sb.toString();
}""")
M(core, r"""
public static String commitKeys(String k, int kd, java.util.Properties p, String[] keys, String[] vals, long ver) {''')

# ---------------------------------------------------------------------------------------------------- 5. ShCore: simple totems, Smithy I, place a totem item
SIMPLE_TOT = r'''# ================= 0.4.27 SIMPLE TOTEMS (tools/shards_0_4_27_patch.py; Skyy 2026-11-21 "get the totem system working simply and ewasily in this clicker side"):
# the island's SPIRIT = its first worker totem of this shard; Buy (tier I) / Tier up on the clicker page; its 2 modifier slots = the spirit's m1 / m2
M(core, r"""
public static int spiritIdx(int kd, String[] e) {
  for (int i = 0; i < e.length; i++) {
    int ti = @PKG@.ShTotem.idx(@PKG@.ShTotem.parse(e[i])[0]);
    if (ti >= 0 && @PKG@.ShTotem.WORKER[ti] && @PKG@.ShTotem.accepts(ti, kd)) return i;
  }
  return -1;
}""")
M(core, r"""
public static String joinE(String[] e) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < e.length; i++) { if (i > 0) sb.append(','); sb.append(e[i]); }
  return sb.toString();
}""")
M(core, "public static boolean modOk(int mi) { return mi >= 0 && mi < @PKG@.ShTotem.MOD_KEYS.length && !\"rare\".equals(@PKG@.ShTotem.MOD_KEYS[mi]); }")   # Rare Finder: bonus totems only
M(core, r"""
public static long spiritCoins(int cur, double cv) {
  double[] a = @PKG@.ShCfg.TOT_H;
  int i = cur < 0 ? 0 : (cur >= a.length ? a.length - 1 : cur);
  return @PKG@.ShIsl.coins(a[i], cv);
}""")
M(core, r"""
public static Object[] itemCost(String id, long q) {
  if (id == null || id.length() == 0 || q <= 0L) return new Object[] { new String[0], new long[0] };
  return new Object[] { new String[] { id }, new long[] { q } };
}""")
M(core, r"""
public static Object[] spiritMats(int kd, int t, int cur) {
  int[] a = @PKG@.ShCfg.TOT_E;
  int i = cur < 0 ? 0 : (cur >= a.length ? a.length - 1 : cur);
  return itemCost(@PKG@.ShIsl.tok(kd, t, "ench"), (long) a[i]);
}""")
M(core, "public static long modCoins(double cv) { return @PKG@.ShIsl.coins(@PKG@.ShCfg.MOD_H, cv); }")
M(core, "public static Object[] modMats(int kd, int t) { return itemCost(@PKG@.ShIsl.tok(kd, t, \"ench\"), (long) @PKG@.ShCfg.MOD_E); }")
M(core, "public static double tierCv(int t) { return @PKG@.ShCfg.curve(@PKG@.ShIsl.band(@PKG@.ShIsl.TIER[t])); }")   # a bridge: never under the store lock
# Buy the spirit (tier I) or tier it up; `seen` = the tier the page showed (0 = none) - a double click buys once
M(core, r"""
public static String buySpirit0(java.util.UUID u, String k, int kd, int slot, int seen, @IC@[] cs) {
  if (!@PKG@.ShCfg.ON) return "-Shards are switched off on this server.";
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  String no = gateOwn(u, k, kd, p);
  if (no != null) return no;
  if (slot < 0 || slot >= @PKG@.ShMath.SLOTS) return "-Pick an island first.";
  int t0;
  @PKG@.ShStore.LOCK.lock(); try {
    if (!@PKG@.ShMath.hasIsland(kd, p, slot)) return "-That island is not yours yet.";
    t0 = @PKG@.ShIsl.ty(kd, p, slot);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  double cv = tierCv(t0);
  long ver; int cur; String nv; String was = "none";
  @PKG@.ShStore.LOCK.lock(); try {
    if (!@PKG@.ShMath.hasIsland(kd, p, slot) || @PKG@.ShIsl.ty(kd, p, slot) != t0) return "=The page is up to date now - click again.";
    String[] e = @PKG@.ShTotem.entries(kd, p, slot);
    int si = spiritIdx(kd, e);
    cur = si < 0 ? 0 : @PKG@.ShTotem.tierOf(@PKG@.ShTotem.parse(e[si])[1]);
    if (cur != seen) return "=The page is up to date now - click again.";
    if (cur >= 5) return "=This spirit totem is at its highest tier.";
    String[] ne;
    if (si < 0) {
      ne = new String[e.length + 1];
      for (int i = 0; i < e.length; i++) ne[i] = e[i];
      ne[e.length] = @PKG@.ShKind.WORKER[kd] + ":1:::0:" + @PKG@.ShTotem.newUid();
    } else {
      ne = new String[e.length];
      for (int i = 0; i < e.length; i++) ne[i] = e[i];
      String[] f = @PKG@.ShTotem.parse(e[si]);
      was = @PKG@.ShTotem.fmt(f);
      f[1] = String.valueOf(cur + 1);
      ne[si] = @PKG@.ShTotem.fmt(f);
    }
    nv = joinE(ne);
    ver = @PKG@.ShStore.ver(k);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  String r = purchaseM(u, k, kd, p, cs, spiritMats(kd, t0, cur), spiritCoins(cur, cv), new String[] { @PKG@.ShMath.ik(kd, slot, "totems") }, new String[] { nv },
                       "spirit", @PKG@.ShKind.KEYS[kd] + " spirit slot " + slot + " " + was + " -> tier " + (cur + 1), ver);
  if (r != null) return r;
  tlog(u + " " + k + " " + @PKG@.ShKind.KEYS[kd] + " spirit slot " + slot + " " + was + " -> tier " + (cur + 1));
  return cur == 0 ? "+A spirit totem now works the " + @PKG@.ShIsl.tname(t0) + " island - also while you are away."
                  : "+The " + @PKG@.ShIsl.tname(t0) + " island's spirit totem is now tier " + @PKG@.ShTotem.ROMAN[cur] + ".";
}""")
M(core, "public static String buySpirit(java.util.UUID u, String k, int kd, int slot, int seen, @IC@[] cs) { String r = buySpirit0(u, k, kd, slot, seen, cs); @PKG@.ShSnd.ok(u, r, 2); return r; }")
# a modifier into slot j (1 / 2) of the spirit: `shown` = the key the page showed in that slot ("" = empty). One modifier ITEM you carry pays it
# (inventory + bags), else coins + the island's Enchanted item. A swapped-out modifier goes into the island's storage as its item (Collect)
M(core, r"""
public static String buyMod0(java.util.UUID u, String k, int kd, int slot, int j, int mi, String shown, @IC@[] cs) {
  if (!@PKG@.ShCfg.ON) return "-Shards are switched off on this server.";
  if (j != 1 && j != 2) return "";
  if (!modOk(mi)) return "-Pick a modifier first.";
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  String no = gateOwn(u, k, kd, p);
  if (no != null) return no;
  if (slot < 0 || slot >= @PKG@.ShMath.SLOTS) return "-Pick an island first.";
  int t0;
  @PKG@.ShStore.LOCK.lock(); try {
    if (!@PKG@.ShMath.hasIsland(kd, p, slot)) return "-That island is not yours yet.";
    t0 = @PKG@.ShIsl.ty(kd, p, slot);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  double cv = tierCv(t0);
  String mid = @PKG@.ShTotem.MOD_ITEMS[mi];
  boolean useItem = haveAll(u, cs, mid) >= 1L;   // a bridge (bags): outside the lock
  String key = @PKG@.ShTotem.MOD_KEYS[mi];
  long ver; String nv; String back = null; String was;
  @PKG@.ShStore.LOCK.lock(); try {
    if (!@PKG@.ShMath.hasIsland(kd, p, slot) || @PKG@.ShIsl.ty(kd, p, slot) != t0) return "=The page is up to date now - click again.";
    String[] e = @PKG@.ShTotem.entries(kd, p, slot);
    int si = spiritIdx(kd, e);
    if (si < 0) return "-Buy the spirit totem first - modifiers sit on it.";
    String[] f = @PKG@.ShTotem.parse(e[si]);
    String cur = f[j + 1];
    if (!cur.equals(shown == null ? "" : shown)) return "=The page is up to date now - click again.";
    if (cur.equals(key)) return "=That modifier is in this slot already.";
    if (f[j == 1 ? 3 : 2].equals(key)) return "-That modifier is in the other slot already - pick another one.";
    was = @PKG@.ShTotem.fmt(f);
    int oi = @PKG@.ShTotem.modIdx(cur);
    if (oi >= 0) back = @PKG@.ShTotem.MOD_ITEMS[oi];
    f[j + 1] = key;
    String[] ne = new String[e.length];
    for (int i = 0; i < e.length; i++) ne[i] = e[i];
    ne[si] = @PKG@.ShTotem.fmt(f);
    nv = joinE(ne);
    ver = @PKG@.ShStore.ver(k);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  Object[] mats = useItem ? itemCost(mid, 1L) : modMats(kd, t0);
  long coins = useItem ? 0L : modCoins(cv);
  String[] keys = back == null ? new String[] { @PKG@.ShMath.ik(kd, slot, "totems") } : new String[] { @PKG@.ShMath.ik(kd, slot, "totems"), @PKG@.ShMath.ik(kd, slot, "drops") };
  String[] vals = back == null ? new String[] { nv } : new String[] { nv, String.valueOf((char) 1) + back + ":1" };
  String r = purchaseM(u, k, kd, p, cs, mats, coins, keys, vals, "modifier", @PKG@.ShKind.KEYS[kd] + " modifier slot " + slot + " #" + j + " " + was + " + " + key + (back == null ? "" : " (" + back + " -> storage)"), ver);
  if (r != null) return r;
  tlog(u + " " + k + " " + @PKG@.ShKind.KEYS[kd] + " modifier slot " + slot + " #" + j + " " + key + (useItem ? " (item)" : " (bought)") + (back == null ? "" : ", " + back + " -> storage"));
  return "+" + @PKG@.ShTotem.MOD_NAMES[mi] + " on the spirit totem (" + @PKG@.ShTotem.MOD_DESC[mi] + ")" + (back == null ? "." : " - the old modifier is in the island's storage (Collect gives it back).");
}""")
M(core, "public static String buyMod(java.util.UUID u, String k, int kd, int slot, int j, int mi, String shown, @IC@[] cs) { String r = buyMod0(u, k, kd, slot, j, mi, shown, cs); @PKG@.ShSnd.ok(u, r, 2); return r; }")
# Smithy I (Skyy 2026-11-21 "i need a way for an auto smelt upgrade"): an Auto-Smelt Pole entry on the quarry's base island, bought with coins + its own ore
M(core, r"""
public static String buySmithy1_0(java.util.UUID u, String k, int kd, int slot, @IC@[] cs) {
  if (!@PKG@.ShCfg.ON) return "-Shards are switched off on this server.";
  if (!"mine".equals(@PKG@.ShIsl.STYLE[kd])) return "";   // the Mining Shard (ShClk is made after ShCore)
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  String no = gateOwn(u, k, kd, p);
  if (no != null) return no;
  if (slot < 0 || slot >= @PKG@.ShMath.SLOTS) return "-Pick a quarry first.";
  int t0;
  @PKG@.ShStore.LOCK.lock(); try {
    if (!@PKG@.ShMath.hasIsland(kd, p, slot)) return "-That island is not yours yet.";
    t0 = @PKG@.ShIsl.ty(kd, p, slot);
    if (@PKG@.ShTotem.smelts(kd, p, slot)) return "=This quarry smelts already.";
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  double cv = tierCv(t0);
  long ver; String nv;
  @PKG@.ShStore.LOCK.lock(); try {
    if (!@PKG@.ShMath.hasIsland(kd, p, slot) || @PKG@.ShIsl.ty(kd, p, slot) != t0 || @PKG@.ShTotem.smelts(kd, p, slot)) return "=The page is up to date now - click again.";
    String[] e = @PKG@.ShTotem.entries(kd, p, slot);
    String[] ne = new String[e.length + 1];
    for (int i = 0; i < e.length; i++) ne[i] = e[i];
    ne[e.length] = "autosmelt_pole:1:::0:" + @PKG@.ShTotem.newUid();
    nv = joinE(ne);
    ver = @PKG@.ShStore.ver(k);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  String r = purchaseM(u, k, kd, p, cs, itemCost(@PKG@.ShIsl.PROD[t0], (long) @PKG@.ShCfg.MQ_S1ORE), @PKG@.ShIsl.coins(@PKG@.ShCfg.MQ_S1H, cv),
                       new String[] { @PKG@.ShMath.ik(kd, slot, "totems") }, new String[] { nv }, "smithy1", "mining smithy I slot " + slot, ver);
  if (r != null) return r;
  return "+Smithy I: this quarry now smelts every ore it mines into its bar (1 : 1). Smithy II (the alloy slider) is next.";
}""")
M(core, "public static String buySmithy1(java.util.UUID u, String k, int kd, int slot, @IC@[] cs) { String r = buySmithy1_0(u, k, kd, slot, cs); @PKG@.ShSnd.ok(u, r, 2); return r; }")
# the totem items of shard kd in the inventory that may go on an island (not a hand-held Totem I): Object[]{ ci, si, id, doc } of ShInv.totems
M(core, r"""
public static java.util.ArrayList placeable(int kd, @IC@[] cs, long now) {
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.ArrayList l = @PKG@.ShInv.totems(cs);
  for (int i = 0; i < l.size(); i++) {
    Object[] o = (Object[]) l.get(i);
    String id = (String) o[2];
    int ti = @PKG@.ShTotem.itemIdx(id);
    if (ti < 0 || !@PKG@.ShTotem.accepts(ti, kd)) continue;
    String[] f = @PKG@.ShTotem.fromDoc((@BD@) o[3], id, now);
    if (f == null || @PKG@.ShTotem.handHeld(f)) continue;
    out.add(o);
  }
  return out;
}""")
M(core, r"""
public static String turnIn(java.util.UUID u, String k, int kd, int slot, @IC@[] cs) {
  if (cs == null) return "-Your inventory could not be read - try again.";
  java.util.ArrayList l = placeable(kd, cs, now());
  if (l.size() == 0) return "-You carry no totem item for this shard (hand-held Totem I work in your hand anywhere).";
  Object[] o = (Object[]) l.get(0);
  return placeTotem(u, k, kd, slot, ((Integer) o[0]).intValue(), ((Integer) o[1]).intValue(), cs);
}""")
'''
P.rep('''M(core, "public static String buyOffline(java.util.UUID u, String k, int kd, @IC@[] cs) { String r = buyOffline0(u, k, kd, cs); @PKG@.ShSnd.ok(u, r, 2); return r; }")
''', '''M(core, "public static String buyOffline(java.util.UUID u, String k, int kd, @IC@[] cs) { String r = buyOffline0(u, k, kd, cs); @PKG@.ShSnd.ok(u, r, 2); return r; }")
''' + SIMPLE_TOT)

# ---------------------------------------------------------------------------------------------------- 6. the walkable shard worlds are retired
P.rep('''public static String enter(@ST@ st, @REF@ ref, java.util.UUID u, String k, int kd, @WLD@ from) {
  if (!@PKG@.ShCfg.ON) return "-Shards are switched off on this server.";''', '''public static String enter(@ST@ st, @REF@ ref, java.util.UUID u, String k, int kd, @WLD@ from) {
  if (!@PKG@.ShCfg.ON) return "-Shards are switched off on this server.";
  if (k != null) { RETIRED.incrementAndGet(); return "-Shard worlds are retired - your shard is its clicker page now (right-click the portal)."; }   // 0.4.27 (Skyy 2026-11-21 "compleatly replace this with the clicker system")''')
P.rep('''M(w2, "public static @TRF@ arrival() { return arrival(%d); }" % FARM_K)
''', '''M(w2, "public static @TRF@ arrival() { return arrival(%d); }" % FARM_K)
F(w2, "public static final java.util.concurrent.atomic.AtomicLong RETIRED = new java.util.concurrent.atomic.AtomicLong();")   # 0.4.27: Enter Shard refused
''')
# a totem block / Totem Bench inside an old shard world: nothing opens (the hub stand keeps Back to Island)
P.rep('''  if (this.view == 3 || this.view == 4) {
    if (!@PKG@.ShWorlds.isShard(wn)) return "";
    return @PKG@.ShRole.mayBeIn(this.me, @PKG@.ShWorlds.ownerOf(wn)) ? null : "This shard belongs to someone else's island.";
  }''', '''  if (this.view == 3 || this.view == 4) {
    if (!@PKG@.ShWorlds.isShard(wn)) return "";
    if (!@PKG@.ShRole.mayBeIn(this.me, @PKG@.ShWorlds.ownerOf(wn))) return "This shard belongs to someone else's island.";
    return this.view == 4 ? "The Totem Bench is retired - spirit totems are bought and tiered up on your shard's clicker page (right-click the portal on your island, Upgrades)."
                          : "Totems live on your shard's clicker page now (right-click the portal on your island, Upgrades) - this one keeps working there.";   // 0.4.27
  }''')
# the menu: no Enter Shard (Ranching / Orchard keep the rest until their clicker)
P.rep('''def _menu(tseg):
    v = SUI.Appends(sh.appends)
    v.extend(SEG["enter"])
    v.extend(SEG[tseg])''', '''def _menu(tseg):
    v = SUI.Appends(sh.appends)
    v.extend(SEG[tseg])   # 0.4.27: no Enter Shard (the walkable worlds are retired)''')
P.rep('''    jseg("enter"), binds([(P + "Enter", "enter")]),
''', '''    # 0.4.27: no Enter Shard
''')
# the portal opens the clicker (Foraging / Mining / Farming / Combat)
P.rep('''  if (no == null) {
    if (pg.view == 0 && pr != null) { String lk = @PKG@.ShIsl.lockMsg(u, pg.kind); if (lk != null) @PKG@.ShSay.to(pr, "[Shards] " + lk, "@BAD@"); }   // 0.4.8
    return pg;
  }''', '''  if (no == null) {
    if (pg.view == 0) {   // a portal (the hub stand inside an old shard world opens view 1)
      String lk = @PKG@.ShIsl.lockMsg(u, pg.kind);   // 0.4.8: the door's lock (the clicking player's own level)
      if (lk != null) {
        if (pr != null) @PKG@.ShSay.to(pr, "[Shards] " + lk, "@BAD@");
        if (@PKG@.ShClk.clicker(pg.kind)) { REFUSED.incrementAndGet(); LOCKED.incrementAndGet(); pg.stText = lk; return null; }   // fix (critic): a locked clicker shard opens nothing (the old door refused too)
        pg.stText = lk; pg.stCol = "@BAD@";   // Ranching / Orchard: their old menu, the lock line on it
        return pg;
      }
      if (@PKG@.ShClk.clicker(pg.kind)) pg.toClicker();   // 0.4.27: the portal opens the shard's clicker page
      DOORS.incrementAndGet();
      @PKG@.ShIsl.quest(u, "shard:door:" + @PKG@.ShKind.KEYS[pg.kind]);   // fix (critic): SkyyQuests' first_shard + archipelago door tasks (was sent by Enter Shard)
    }
    return pg;
  }''')
P.rep('''F(pfn, "public static final java.util.concurrent.atomic.AtomicLong REFUSED = new java.util.concurrent.atomic.AtomicLong();")
''', '''F(pfn, "public static final java.util.concurrent.atomic.AtomicLong REFUSED = new java.util.concurrent.atomic.AtomicLong();")
F(pfn, "public static final java.util.concurrent.atomic.AtomicLong DOORS = new java.util.concurrent.atomic.AtomicLong();")    # 0.4.27 fix: portal opens = shard:door:<kind> sent
F(pfn, "public static final java.util.concurrent.atomic.AtomicLong LOCKED = new java.util.concurrent.atomic.AtomicLong();")   # 0.4.27 fix: a locked clicker portal
''')
P.rep('''    this.kind = n; this.sel = 0; this.mview = 0; this.tpad = 0; this.pickArm = 0L; this.recArm = 0L;
    return "";''', '''    if (@PKG@.ShClk.clicker(n)) { String lkn = @PKG@.ShIsl.lockMsg(u, n); if (lkn != null) return "-" + lkn; }   // fix (critic): a locked clicker shard stays shut
    this.kind = n; this.sel = 0; this.mview = 0; this.tpad = 0; this.pickArm = 0L; this.recArm = 0L;
    if (@PKG@.ShClk.clicker(n)) toClicker();   // 0.4.27: that shard's clicker page
    return "";''')

# ---------------------------------------------------------------------------------------------------- 7. ShClk: clicker kinds, town kill coins
CLK427 = r'''# 0.4.27: the shards with a clicker page (the portal opens it); the town's kill coins (SkyyMobs mob:fn:killCoins; a bridge: never under the store lock)
M(ckc, "public static boolean clicker(int kd) { return kd == FK || kd == MK || kd == CRK || kd == TK; }")
F(ckc, "public static final java.util.concurrent.atomic.AtomicLong NOCOIN = new java.util.concurrent.atomic.AtomicLong();")
F(ckc, "public static final java.util.concurrent.atomic.AtomicLong KCOINS = new java.util.concurrent.atomic.AtomicLong();")
M(ckc, r"""
public static long coinsFor(int gi, int lvl) {
  if (!@PKG@.ShCfg.TF_COINS || gi < 0 || gi >= T_ROLE.length) return 0L;
  try {
    java.util.function.Function f = @PKG@.ShCfg.fn("mob:fn:killCoins");
    if (f == null) { NOCOIN.incrementAndGet(); return 0L; }
    Object r = f.apply(new Object[] { T_ROLE[gi], Integer.valueOf(lvl < 1 ? 1 : lvl) });
    long c = r instanceof Number ? ((Number) r).longValue() : 0L;
    return c < 0L ? 0L : (c > 1000000000L ? 1000000000L : c);
  } catch (Throwable t) { return 0L; }
}""")
M(ckc, "public static long coinsWaiting(java.util.Properties p, int slot) { long c = @PKG@.ShStore.lng(p, @PKG@.ShMath.ik(TK, slot, \"coins\"), 0L); return c < 0L ? 0L : c; }")
'''
P.rep('''M(ckc, r"""
public static Object[] fight(java.util.UUID u, String k, int kd, int slot, int spot, String hand) {''', CLK427 + '''M(ckc, r"""
public static Object[] fight(java.util.UUID u, String k, int kd, int slot, int spot, String hand) {''')
P.rep('''  if (left > 0.0) return res("", @PKG@.ShCfg.dec(hpMax - left) + " / " + @PKG@.ShCfg.dec(hpMax));
  String[] ids; long[] gq; long total = 0L; long got = 0L;
  @PKG@.ShStore.LOCK.lock(); try {''', '''  if (left > 0.0) return res("", @PKG@.ShCfg.dec(hpMax - left) + " / " + @PKG@.ShCfg.dec(hpMax));
  long kc = coinsFor(gi, (@PKG@.ShCombat.lvLoP(own, z, sz, ml) + @PKG@.ShCombat.lvHiP(own, z, sz, ml)) / 2);   // 0.4.27: the kill's coins (a bridge: before the lock)
  String[] ids; long[] gq; long total = 0L; long got = 0L;
  @PKG@.ShStore.LOCK.lock(); try {''')
P.rep('''    @PKG@.ShMath.heldSet(kd, p, slot, mm);
    String e = @PKG@.ShStore.save(k, p);
    if (e != null) {
      if (old == null) p.remove(dk); else p.setProperty(dk, old);
      unfell(key, spot, hpMax);''', '''    @PKG@.ShMath.heldSet(kd, p, slot, mm);
    String ck = @PKG@.ShMath.ik(kd, slot, "coins");   // 0.4.27: the kill's coins wait in the town (Collect all on the town page pays them)
    String oldC = p.getProperty(ck);
    if (kc > 0L) p.setProperty(ck, String.valueOf(coinsWaiting(p, slot) + kc));
    String e = @PKG@.ShStore.save(k, p);
    if (e != null) {
      if (old == null) p.remove(dk); else p.setProperty(dk, old);
      if (oldC == null) p.remove(ck); else p.setProperty(ck, oldC);
      unfell(key, spot, hpMax);''')
P.rep('''  String r = "+Slew a " + nm + " (Lv " + lvl + ")" + (sb.length() > 0 ? ": " + sb.toString() : " - it dropped nothing") + xt + fit + ".";''',
      '''  if (kc > 0L) KCOINS.addAndGet(kc);
  String r = "+Slew a " + nm + " (Lv " + lvl + ")" + (sb.length() > 0 ? ": " + sb.toString() : " - it dropped nothing") + (kc > 0L ? ", +" + @PKG@.ShCfg.num(kc) + " coins" : "") + xt + fit + ".";''')
# Collect all on the town page pays the waiting coins: debit + save first, then the purse; a refused payment puts them back
PAY427 = r'''M(ckc, r"""
public static String payCoins(java.util.UUID u, String k, int kd) {
  if (kd != TK || u == null) return "";
  if (!@PKG@.ShCfg.ON || @PKG@.ShCore.busy(u)) return "";   // fix2: PROFILES-CONTRACT rule 5 - never into a purse that may still be the last profile's
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "";
  long[] took = new long[@PKG@.ShMath.SLOTS];
  long sum = 0L;
  @PKG@.ShStore.LOCK.lock(); try {
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
    for (int s = 0; s < @PKG@.ShMath.SLOTS; s++) {
      long c = coinsWaiting(p, s);
      if (c <= 0L) continue;
      took[s] = c;
      sum += c;
      p.remove(@PKG@.ShMath.ik(kd, s, "coins"));
    }
    if (sum <= 0L) return "";
    String e = @PKG@.ShStore.save(k, p);
    if (e != null) { p.clear(); p.putAll(old); return "-The town's coins could not be saved - they stay in the town."; }
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (@PKG@.ShPay.addCoins(u, sum)) { @PKG@.ShStore.log(u + " " + k + " combat town coins " + sum); return "+" + @PKG@.ShCfg.num(sum) + " coins"; }
  @PKG@.ShStore.LOCK.lock(); try {   // the purse refused: back into the town (onto what is there now)
    for (int s = 0; s < @PKG@.ShMath.SLOTS; s++) if (took[s] > 0L) p.setProperty(@PKG@.ShMath.ik(kd, s, "coins"), String.valueOf(coinsWaiting(p, s) + took[s]));
    String e2 = @PKG@.ShStore.save(k, p);
    if (e2 != null) { @PKG@.ShCfg.warn("town coins of " + k + " could not be put back (" + e2 + "): " + sum); @PKG@.ShStore.log(u + " " + k + " combat town coins " + sum + " NOT PAID AND NOT SAVED " + e2); }
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  return "-Your purse could not take the town's coins - they stay in the town.";
}""")
'''
P.rep('''# THE CLICK: Object[]{ status ("+..." / "-..." / "=..." / "" = nothing to say), pop text over the tree }. World thread; the bridges outside the store lock
M(ckc, r"""
public static Object[] chop(''', PAY427 + '''# THE CLICK: Object[]{ status ("+..." / "-..." / "=..." / "" = nothing to say), pop text over the tree }. World thread; the bridges outside the store lock
M(ckc, r"""
public static Object[] chop(''')

# ---------------------------------------------------------------------------------------------------- 8. the per-profile migration (ShStore.migrate3)
P.rep('''M(st, "public static void migrate2(String k, java.util.Properties p) { }")   # 0.4.8: the body is set below (after ShMath) - the map migration
''', '''M(st, "public static void migrate2(String k, java.util.Properties p) { }")   # 0.4.8: the body is set below (after ShMath) - the map migration
M(st, "public static void migrate3(String k, java.util.Properties p) { }")   # 0.4.27: the body is set below (after ShMath) - the clicker migration
F(st, "public static final java.util.concurrent.atomic.AtomicLong CLKMIG = new java.util.concurrent.atomic.AtomicLong();")   # 0.4.27: files migrated
''')
P.rep('''    migrate2(k, p);   // 0.4.8: Automation grandfathered, 0.4.6's extra islands -> the next tiers, Mining caves (marker map.done=1)
''', '''    migrate2(k, p);   // 0.4.8: Automation grandfathered, 0.4.6's extra islands -> the next tiers, Mining caves (marker map.done=1)
    migrate3(k, p);   // 0.4.27: the clicker migration - automated shards' seed stores -> storage (marker clk.done=1)
''')
MIG3 = r'''
# ================= 0.4.27 ShStore.migrate3 = THE CLICKER MIGRATION (tools/shards_0_4_27_patch.py; PROJECT-RULES 4): once per profile file, marker clk.done=1.
# The clicker reads every island key the walkable shard used, so islands, sub-upgrades, totems (tiers + modifiers + boosters), stored items and the
# shard-wide upgrades carry over as they are. The ONLY thing without a place any more: the seed / sapling store of an AUTOMATED shard (its totems never
# use it again) -> that island's storage as the seed item (.drops; Collect / the grid give it back), .seed = 0. The file is copied to
# shards/history/clicker/ first (byte-checked), production settled first, ONE save, collect.log line with the Undo. A refused copy / save leaves file
# + memory untouched (tried again at the next load). Nothing to move = the marker rides along with the next save.
M(st, r"""
public static String snapClk(String k) {
  try {
    java.nio.file.Path f = DIR.resolve(k + ".properties");
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "-";
    java.nio.file.Path h = DIR.resolve("history").resolve("clicker");
    java.nio.file.Files.createDirectories(h, new java.nio.file.attribute.FileAttribute[0]);
    byte[] src = java.nio.file.Files.readAllBytes(f);
    String name = k + ".pre-0.4.27.properties";
    java.nio.file.Path t = h.resolve(name);
    if (java.nio.file.Files.exists(t, new java.nio.file.LinkOption[0]) && !java.util.Arrays.equals(src, java.nio.file.Files.readAllBytes(t))) {
      name = k + ".pre-0.4.27." + System.currentTimeMillis() + ".properties";
      t = h.resolve(name);
    }
    if (!java.nio.file.Files.exists(t, new java.nio.file.LinkOption[0])) {
      java.nio.file.Path tmp = h.resolve(name + ".tmp");
      java.nio.file.Files.write(tmp, src, new java.nio.file.OpenOption[0]);
      moveInto(tmp, t);
    }
    if (!java.util.Arrays.equals(src, java.nio.file.Files.readAllBytes(t))) { @PKG@.ShCfg.warnOnce("clksnap:" + k, "the 0.4.27 clicker migration copy of " + k + " does not match the file - not migrated"); return null; }
    return "shards/history/clicker/" + name;
  } catch (Throwable x) {
    @PKG@.ShCfg.warnOnce("clksnapx:" + k, "the 0.4.27 clicker migration of " + k + " is waiting: its History copy could not be written (" + x + ")");
    return null;
  }
}""")
st.getDeclaredMethod("migrate3").setBody(jv(r"""{
  String k = $1;
  java.util.Properties p = $2;
  if (p == null || k == null || "1".equals(p.getProperty("clk.done"))) return;
  LOCK.lock();
  try {
    if ("1".equals(p.getProperty("clk.done"))) return;
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
    long now = System.currentTimeMillis();
    StringBuilder ch = new StringBuilder();
    int isl = 0; int tot = 0; long moved = 0L;
    for (int kd = 0; kd < @PKG@.ShKind.N; kd++) {
      if (!@PKG@.ShMath.owned(kd, p)) continue;
      boolean au = @PKG@.ShIsl.auto(kd, p);
      for (int s = 0; s < @PKG@.ShMath.SLOTS; s++) {
        if (!@PKG@.ShMath.hasIsland(kd, p, s)) continue;
        isl++;
        tot += @PKG@.ShTotem.entries(kd, p, s).length;
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
        ch.append(' ').append(@PKG@.ShKind.KEYS[kd]).append(".i").append(s).append(' ').append(sd2).append(' ').append(id).append(" -> storage");
      }
    }
    if (moved <= 0L) { p.setProperty("clk.done", "1"); CLKCHK.incrementAndGet(); return; }
    String snap = snapClk(k);
    if (snap == null) { p.clear(); p.putAll(old); return; }
    p.setProperty("clk.done", "1");
    String err = save(k, p);
    if (err != null) { p.clear(); p.putAll(old); @PKG@.ShCfg.warnOnce("clksave:" + k, "the 0.4.27 clicker migration of " + k + " is waiting (the file could not be saved: " + err + ")"); return; }
    CLKMIG.incrementAndGet();
    log("clicker migration (SkyyShards @VERSION@) " + k + ":" + ch.toString() + " (" + moved + " items; " + isl + " islands and " + tot + " totems kept as they were) - History copy " + snap + " - Undo: stop the server, copy it back over shards/" + k + ".properties and put SkyyShards 0.4.26 back");
    @PKG@.ShCfg.info("0.4.27 clicker migration: " + k + " -" + ch.toString() + " (collect.log has the Undo)");
  } finally { LOCK.unlock(); }
}"""))
'''
P.rep('''F(st, "public static final java.util.concurrent.atomic.AtomicLong CLKMIG = new java.util.concurrent.atomic.AtomicLong();")   # 0.4.27: files migrated
''', '''F(st, "public static final java.util.concurrent.atomic.AtomicLong CLKMIG = new java.util.concurrent.atomic.AtomicLong();")   # 0.4.27: files migrated
F(st, "public static final java.util.concurrent.atomic.AtomicLong CLKCHK = new java.util.concurrent.atomic.AtomicLong();")   # 0.4.27: files checked, nothing to move
''')
_M2END = '''    log("map migration (SkyyShards @VERSION@) " + k + ":" + ch.toString() + " - History copy " + snap + " - Undo: stop the server, copy it back over shards/" + k + ".properties and put SkyyShards 0.4.7 + SkyyIslands 0.5.24 back");
    @PKG@.ShCfg.info("0.4.8 map migration: " + k + " -" + ch.toString() + " (collect.log has the Undo)");
  } finally { LOCK.unlock(); }
}"""))
'''
P.rep(_M2END, _M2END + MIG3)

# ---------------------------------------------------------------------------------------------------- 9. THE PAGE PARTS: rows with clear costs, the upgrades view
PARTS427 = r'''
# ---- 0.4.27 (tools/shards_0_4_27_patch.py) THE UPGRADE ROWS WITH CLEAR COSTS (Skyy 2026-11-21 "make it a little more clear how much each thing costs"): every row
# = icon | name + level, effect, up to 3 cost lines (one per part, "have / need item", green = you have it, red = not yet; drawn at run time) | its button.
# The rows sit in a scroll list (6 fit, Mining's 8 scroll). Mode 2 = the SHARD UPGRADES view: the island's spirit totem + 2 modifier slots + its other totems
# + "place a totem item", and the shard-wide upgrades that lived on the old Map / Collect tabs (Storage, Auto-Compactor, Time Compressor, Automation,
# Offline Harvest, Sell all) + Pick up Shard.
CK_CL_H, CK_BW, CK_CL_N = 19, 150, 3
CK_NUP_W = CK_UIW - 14                       # a row in the scroll list (room for the bar)


def _ck_row(a_, parent, R_, name, icon, w, h=CK_ROW_H):
    """one upgrade row; returns the width of its cost lines"""
    tw = w - 12 - 56 - 8
    cw = tw - CK_BW - 8
    a_.append((parent, G_.glass_group(R_, w, h, role="inset", layout="Left", pad=6, anchor={"top": 5})))
    a_.append(("#" + R_, "Group #%sI { Anchor: (Width: 56, Height: %d); }" % (R_, h - 12)))
    if icon:
        a_.append(("#" + R_ + "I", SUI.map_pic(R_ + "P", 0, 6, 56, 56, CK_TEX[icon])))
    a_.append(("#" + R_, G_.glass_group(R_ + "T", tw, h - 12, layout="Top", anchor={"left": 8})))
    a_.append(("#" + R_ + "T", G_.glass_group(R_ + "N", tw, 26, layout="Left")))
    a_.append(("#" + R_ + "N", _ck_glab(R_ + "Nm", 17, "title", 210, 26, bold=True, text=name)))
    a_.append(("#" + R_ + "N", _ck_glab(R_ + "L", 15, "xp", tw - 210, 26, bold=True, halign="End")))
    a_.append(("#" + R_ + "T", _ck_glab(R_ + "E", 14, "text", tw, 22)))
    a_.append(("#" + R_ + "T", G_.glass_group(R_ + "K", tw, CK_CL_N * CK_CL_H, layout="Left", anchor={"top": 2})))
    a_.append(("#" + R_ + "K", G_.glass_group(R_ + "Cs", cw, CK_CL_N * CK_CL_H, layout="Top")))
    a_.append(("#" + R_ + "K", G_.glass_group(R_ + "B", CK_BW, CK_CL_N * CK_CL_H, layout="Top", anchor={"left": 8})))
    assert 26 + 22 + 2 + CK_CL_N * CK_CL_H <= h - 12, "0.4.27: a row's parts fit its height"
    return cw


def _ck_btns(prefix, R_, labels, top=12):
    """the on / off button segments of a row (one pair per label variant)"""
    for vi_, lab_ in enumerate(labels):
        for on_ in (True, False):
            b_ = _ck_seg("%s%s%d" % (prefix, "on" if on_ else "off", vi_))
            b_.append(("#" + R_ + "B", G_.glass_button(R_ + "X", lab_, "secondary", w=CK_BW, h=32, disabled=not on_, anchor={"top": top})))


NUP_KINDS = {"F": (CK_UP_NAMES[:2] + ["Spirit totem"] + CK_UP_NAMES[3:], CK_UP_ICON),
             "Q": (Q_UP_NAMES[:2] + ["Miner spirit"] + Q_UP_NAMES[3:], Q_UP_ICON),
             "Fm": (FQ_UP_NAMES[:2] + ["Spirit totem"] + FQ_UP_NAMES[3:], FQ_UP_ICON),
             "T": (TF_UP_NAMES, TF_UP_ICON)}
NUP_CW = None
for _K, (_nm, _ic) in sorted(NUP_KINDS.items()):
    a_ = _ck_seg("nup" + _K)
    a_.append((CK_BODY, G_.glass_group(CKP + "Up", CK_UPW, CK_BODY_H, role="panel", layout="Top", pad=12, anchor={"left": 12})))
    a_.append((CK_UP, G_.glass_group(CKP + "UpH", CK_UIW, 32, layout="Left")))
    a_.append(("#" + CKP + "UpH", _ck_glab(CKP + "UpT", 18, "gold", 150, 32, bold=True, text="UPGRADES")))
    a_.append(("#" + CKP + "UpH", _ck_glab(CKP + "UpCap", 13, "dim", CK_UIW - 150, 32, halign="End")))
    a_.append((CK_UP, SUI.scroll_list(CKP + "UpL", h=CK_BODY_H - 24 - 32 - 4, w=CK_UIW)))
    for _r in range(len(_nm)):
        _cw = _ck_row(a_, "#" + CKP + "UpL", CKP + "U%d" % _r, _nm[_r], _ic[_r], CK_NUP_W)
        assert NUP_CW in (None, _cw)
        NUP_CW = _cw
        _lab = ["Tier up", "Buy"] if _r == 2 else (["Upgrade", "Buy"] if (_K == "Q" and _r == 7) else ["Upgrade"])
        _ck_btns("nup%s%d" % (_K, _r), CKP + "U%d" % _r, _lab)
        a_ = CKA["nup" + _K]
b_ = _ck_seg("nqsl")   # the quarry's Smithy II alloy slider (0.4.24's, in the new row)
b_.append(("#" + CKP + "U7B", G_.glass_group(CKP + "U7S", CK_BW, 32, layout="Left", anchor={"top": 12})))
b_.append(("#" + CKP + "U7S", G_.glass_button(CKP + "U7M", "<", "secondary", w=44, h=32, size=18)))
b_.append(("#" + CKP + "U7S", _ck_glab(CKP + "U7V", 15, "goldHi", CK_BW - 88, 32, bold=True, halign="Center")))
b_.append(("#" + CKP + "U7S", G_.glass_button(CKP + "U7U", ">", "secondary", w=44, h=32, size=18)))
# the store strip: Give / Take seeds (the seed store of a manual shard) - the old Storage tab button's place
for _sn, _sl in (("seedg", "Give seeds"), ("seedt", "Take seeds")):
    a_ = _ck_seg(_sn)
    a_.append(("#" + CKP + "StoBt", G_.glass_button(CKP + "STab", _sl, "secondary", w=150, h=38)))
# the top bar: Upgrades (mode 0 / 1) / Island view (mode 2) in the old "Shard menu" place
a_ = _ck_seg("frame2b")
a_.append((CK_TOP, G_.glass_button(CKP + "MenuB", "Island view", "secondary", w=170, h=38, anchor={"top": 3, "right": 8})))
a_.append((CK_TOP, G_.glass_button(CKP + "Close", "X", "close", w=40, h=40, size=16, anchor={"top": 2})))
a_.append((CK_WIN, 'Group #%sSep { Anchor: (Width: %d, Height: 2, Top: 6, Bottom: 6); Background: "%s"; }' % (CKP, CK_IW, G_.glass_path("Separator"))))
a_.append((CK_WIN, G_.glass_group(CKP + "Body", CK_IW, CK_BODY_H, layout="Left")))
# ---- mode 2: THE SHARD UPGRADES VIEW - left the island's spirit totem, right the whole shard
CK2_W = (CK_IW - 12) // 2
CK2_RW = CK2_W - 24
CK2_NAMES = ["Spirit totem", "Modifier slot 1", "Modifier slot 2", "Storage", "Auto-Compactor", "Time Compressor", "Automation", "Offline Harvest", "Sell"]
CK2_BTN = [["Tier up", "Buy"], ["Add", "Swap"], ["Add", "Swap"], ["Upgrade"], ["Upgrade"], ["Upgrade"], ["Buy"], ["Upgrade"], ["Sell all"]]
CK2_ACT = ['"k2s:" + this.ck2Seen[0]', '"k2m1:" + this.ckMP[0] + ":" + this.ck2Cur[0]', '"k2m2:" + this.ckMP[1] + ":" + this.ck2Cur[1]',
           '"k2st:" + this.ck2Seen[3]', '"k2cp:" + this.ck2Seen[4]', '"k2tc:" + this.ck2Seen[5]', '"k2au:" + this.ck2Seen[6]', '"k2of:" + this.ck2Seen[7]', '"k2sell"']
a_ = _ck_seg("up2")
a_.append((CK_BODY, G_.glass_group(CKP + "VL", CK2_W, CK_BODY_H, role="panel", layout="Top", pad=12)))
a_.append(("#" + CKP + "VL", G_.glass_group(CKP + "VLH", CK2_RW, 32, layout="Left")))
a_.append(("#" + CKP + "VLH", _ck_glab(CKP + "VLT", 18, "gold", 200, 32, bold=True, text="SPIRIT TOTEM")))
a_.append(("#" + CKP + "VLH", _ck_glab(CKP + "VLC", 13, "dim", CK2_RW - 200, 32, halign="End")))
CK2_CW = None
for _r in range(3):
    _cw = _ck_row(a_, "#" + CKP + "VL", CKP + "V%d" % _r, CK2_NAMES[_r], "UpSpirit" if _r == 0 else None, CK2_RW)
    CK2_CW = _cw
    _ck_btns("v%d" % _r, CKP + "V%d" % _r, CK2_BTN[_r], top=2 if _r else 12)
    a_ = CKA["up2"]
a_.append(("#" + CKP + "VL", _ck_wrap(CKP + "VA", 14, "text", CK2_RW, 44, anchor={"top": 8})))
a_.append(("#" + CKP + "VL", G_.glass_group(CKP + "VT", CK2_RW, 84, role="inset", layout="Left", pad=8, anchor={"top": 6})))
a_.append(("#" + CKP + "VT", _ck_wrap(CKP + "VTT", 14, "text", CK2_RW - 16 - CK_BW - 8, 68)))
a_.append(("#" + CKP + "VT", G_.glass_group(CKP + "VTB", CK_BW, 68, layout="Top", anchor={"left": 8})))
for _on in (True, False):
    b_ = _ck_seg("turn%s" % ("on" if _on else "off"))
    b_.append(("#" + CKP + "VTB", G_.glass_button(CKP + "VTX", "Place one", "secondary", w=CK_BW, h=32, disabled=not _on, anchor={"top": 18})))
for _j in (1, 2):   # the modifier picker < name >
    b_ = _ck_seg("v%dpk" % _j)
    b_.append(("#" + CKP + "V%dB" % _j, G_.glass_group(CKP + "V%dPk" % _j, CK_BW, 22, layout="Left")))
    b_.append(("#" + CKP + "V%dPk" % _j, G_.glass_button(CKP + "V%dPM" % _j, "<", "secondary", w=(CK_BW - 6) // 2, h=22, size=15)))
    b_.append(("#" + CKP + "V%dPk" % _j, G_.glass_button(CKP + "V%dPP" % _j, ">", "secondary", w=(CK_BW - 6) // 2, h=22, size=15, anchor={"left": 6})))
a_ = CKA["up2"]
a_.append((CK_BODY, G_.glass_group(CKP + "VR", CK2_W, CK_BODY_H, role="panel", layout="Top", pad=12, anchor={"left": 12})))
a_.append(("#" + CKP + "VR", G_.glass_group(CKP + "VRH", CK2_RW, 32, layout="Left")))
a_.append(("#" + CKP + "VRH", _ck_glab(CKP + "VRT", 18, "gold", 220, 32, bold=True, text="SHARD UPGRADES")))
a_.append(("#" + CKP + "VRH", _ck_glab(CKP + "VRC", 13, "dim", CK2_RW - 220 - 180, 32, halign="End")))
a_.append(("#" + CKP + "VR", SUI.scroll_list(CKP + "VRL", h=CK_BODY_H - 24 - 32 - 4, w=CK2_RW)))
for _r in range(3, 9):
    _cw = _ck_row(a_, "#" + CKP + "VRL", CKP + "V%d" % _r, CK2_NAMES[_r], None, CK2_RW - 14)
    _ck_btns("v%d" % _r, CKP + "V%d" % _r, CK2_BTN[_r])
    a_ = CKA["up2"]
CK2_CWR = _cw
b_ = _ck_seg("pick2")
b_.append(("#" + CKP + "VRH", G_.glass_button(CKP + "VPk", "Pick up Shard", "secondary", w=170, h=30, anchor={"left": 10})))
# the cost line templates (run time; colour = have it / not yet / a reason)
CK_J_CLINE = {}
for _g, _col in ((0, "dim"), (1, "green"), (2, "red")):
    CK_J_CLINE[_g] = _ck_tpl("Label #@ID@ { Anchor: (Width: @W@, Height: %d); Style: %s; }" % (CK_CL_H, G_.glass_text_style(13, _col, bold=_g > 0)),
                             {"@ID@": "id", "@W@": "w"}, {"@ID@": "SkyyShKU0C0", "@W@": str(NUP_CW)})
NUP_J = {}
for _K, (_nm, _ic) in sorted(NUP_KINDS.items()):
    j_ = [_qj("nup" + _K), _ck_jset(CKP + "UpCap", "this.ckUpCap")]
    for _r in range(len(_nm)):
        R_ = CKP + "U%d" % _r
        _lab = 2 if (_r == 2 or (_K == "Q" and _r == 7)) else 1
        _gen = ["  if (this.ckUpOk[%d]) {" % _r]
        for _vi in range(_lab):
            _gen += ["    if (this.ckUpBtn[%d] == %d) {" % (_r, _vi), _qj("nup%s%don%d" % (_K, _r, _vi)), "    }"]
        _gen += [_ck_bind(R_ + "X", '"ku%d:" + this.ckUpSeen[%d]' % (_r, _r)), "  } else {"]
        for _vi in range(_lab):
            _gen += ["    if (this.ckUpBtn[%d] == %d) {" % (_r, _vi), _qj("nup%s%doff%d" % (_K, _r, _vi)), "    }"]
        _gen += ["  }"]
        j_ += [_ck_jset(R_ + "L", "this.ckUpL[%d]" % _r), _ck_jset(R_ + "E", "this.ckUpE[%d]" % _r), '  ckLinesB(b, "%sU", %d, %d, %d);' % (CKP, _r, _r, NUP_CW)]
        if _K == "Q" and _r == 7:
            j_ += ["  if (this.ckQSm == 2 && this.mine) {", _qj("nqsl"), _ck_jset(CKP + "U7V", 'this.ckQPct + " %"'),
                   _ck_bind(CKP + "U7M", '"kq-:" + this.ckQPct'), _ck_bind(CKP + "U7U", '"kq+:" + this.ckQPct'), "  } else {"] + _gen + ["  }"]
        else:
            j_ += _gen
    NUP_J[_K] = j_
UP2_J = [_qj("up2"), _ck_jset(CKP + "VLC", "this.ck2Isl"), _ck_jset(CKP + "VRC", "this.ck2Cap"), _ck_jset(CKP + "VA", "this.ck2Also"), _ck_jset(CKP + "VTT", "this.ck2Turn"),
         "  if (this.ck2TurnOk) {", _qj("turnon"), _ck_bind(CKP + "VTX", '"k2turn"'), "  } else {", _qj("turnoff"), "  }",
         "  if (this.mine) {", _qj("pick2"), _ck_bind(CKP + "VPk", '"k2pick"'), "  }"]
for _r in range(9):
    R_ = CKP + "V%d" % _r
    UP2_J += [_ck_jset(R_ + "L", "this.ck2L[%d]" % _r), _ck_jset(R_ + "E", "this.ck2E[%d]" % _r),
              '  ckLinesB(b, "%sV", %d, %d, %d);' % (CKP, _r, 10 + _r, CK2_CW if _r < 3 else CK2_CWR)]
    if _r in (1, 2):
        UP2_J += ["  if (this.ck2Pk[%d]) {" % (_r - 1), _qj("v%dpk" % _r), _ck_bind(R_ + "PM", '"kmp%d-"' % _r), _ck_bind(R_ + "PP", '"kmp%d+"' % _r), "  }"]
    UP2_J += ["  if (this.ck2Ok[%d]) {" % _r]
    for _vi in range(len(CK2_BTN[_r])):
        UP2_J += ["    if (this.ck2Btn[%d] == %d) {" % (_r, _vi), _qj("v%don%d" % (_r, _vi)), "    }"]
    UP2_J += [_ck_bind(R_ + "X", CK2_ACT[_r]), "  } else {"]
    for _vi in range(len(CK2_BTN[_r])):
        UP2_J += ["    if (this.ck2Btn[%d] == %d) {" % (_r, _vi), _qj("v%doff%d" % (_r, _vi)), "    }"]
    UP2_J += ["  }"]
'''
P.rep('''# the run-time templates (checked with samples)
_tex0 = CK_TEX["Tree1"]''', PARTS427 + '''# the run-time templates (checked with samples)
_tex0 = CK_TEX["Tree1"]''')

# the frame: Upgrades / Island view; mode 2 in the body; the four kinds' new rows; the seed button; Collect all with coins only
P.rep('''_ck_j = [_ckj("frame"), "  if (this.ckMode == 1) {", _ckj("mapb1"), "  } else {", _ckj("mapb0"), "  }", _ckj("frame2"),''',
      '''_ck_j = [_ckj("frame"), "  if (this.ckMode == 1) {", _ckj("mapb1"), "  } else {", _ckj("mapb0"), "  }", "  if (this.ckMode == 2) {", _ckj("frame2b"), "  } else {", _ckj("frame2"), "  }",   # 0.4.27''')
P.rep('''_ck_bind(CKP + "MenuB", '"kback"'), ''', '''_ck_bind(CKP + "MenuB", '(this.ckMode == 2 ? "kisl" : "kup")'), ''')
P.rep('''         "  if (this.ckMode == 1 && this.ckMine) {"] + _QMAP_J + ["  } else if (this.ckMode == 1 && this.ckTown) {"] + _TMAP_J + [''',
      '''         "  if (this.ckMode == 2) {"] + UP2_J + ["  } else if (this.ckMode == 1 && this.ckMine) {"] + _QMAP_J + ["  } else if (this.ckMode == 1 && this.ckTown) {"] + _TMAP_J + [   # 0.4.27: the upgrades view''')
P.rep('''_ck_j += ["  if (this.manage && this.sgN > 0) {", _ckj("colall"), _ck_bind(CKP + "CAll", '"colall"'), "  }",
          _ckj("stotab"), _ck_bind(CKP + "STab", '"kstore"'),''', '''_ck_j += ["  if (this.manage && (this.sgN > 0 || this.ckCoins > 0L)) {", _ckj("colall"), _ck_bind(CKP + "CAll", '"colall"'), "  }",   # 0.4.27: + the town's coins
          "  if (this.ckSeedB == 1 && this.mine) {", _ckj("seedg"), _ck_bind(CKP + "STab", '"kseed"'), "  } else if (this.ckSeedB == 2 && this.mine) {", _ckj("seedt"), _ck_bind(CKP + "STab", '"kseed"'), "  }",   # 0.4.27: the seed store (was: Storage tab)''')
P.rep('''          "  if (this.ckMine) {"] + _QUP_J + ["  } else {", "  if (this.ckFarm) {", _ckj("fup"), "  } else if (this.ckTown) {", _ckj("tup"), "  } else {", _ckj("up"), "  }", _ck_jset(CKP + "UpCap", "this.ckUpCap")]   # 0.4.25: the farm's rows; 0.4.26 the town's
for _r in range(6):
    R_ = CKP + "U%d" % _r
    _ck_j += [_ck_jset(R_ + "L", "this.ckUpL[%d]" % _r), _ck_jset(R_ + "E", "this.ckUpE[%d]" % _r), _ck_jset(R_ + "C", "this.ckUpC[%d]" % _r),
              "  if (this.ckUpOk[%d]) {" % _r, _ckj("upon%d" % _r), _ck_bind(R_ + "X", '"ku%d:" + this.ckUpSeen[%d]' % (_r, _r)),
              "  } else {", _ckj("upoff%d" % _r), "  }"]
_ck_j += ["  }", "  }", _ckj("foot"),''', '''          "  if (this.ckMine) {"] + NUP_J["Q"] + ["  } else if (this.ckFarm) {"] + NUP_J["Fm"] + ["  } else if (this.ckTown) {"] + NUP_J["T"] + ["  } else {"] + NUP_J["F"] + ["  }"]   # 0.4.27: the rows with clear costs
_ck_j += ["  }", _ckj("foot"),''')

# the variant checks of the new parts (each kind's rows with every button, the upgrades view)
P.rep('''# 0.4.24 the quarry variants: each size with every part (springs, smithy, totems, decorations) + the slider row / the Totems row / the other rows on;''',
      '''# 0.4.27 the new rows (each kind, every button variant + the Smithy slider + the seed button) and the upgrades view (every button on, the pickers, Pick up)
N_VARS = []
for _K, (_nm, _ic) in sorted(NUP_KINDS.items()):
    for _vi in (0, 1):
        v_ = SUI.Appends()
        for _n in ["frame", "mapb0", "frame2", "left", "isl3", "cap", "colall", "seedg" if _vi == 0 else "seedt", "nup" + _K]:
            v_.extend(CKA[_n])
        for _r in range(len(_nm)):
            _ln = 2 if (_r == 2 or (_K == "Q" and _r == 7)) else 1
            if _K == "Q" and _r == 7 and _vi == 1:
                v_.extend(CKA["nqsl"])
            else:
                v_.extend(CKA["nup%s%d%s%d" % (_K, _r, "on" if _vi == 0 else "off", min(_vi, _ln - 1))])
        v_.extend(CKA["foot"])
        N_VARS.append(v_)
for _vi in (0, 1):
    v_ = SUI.Appends()
    for _n in ["frame", "mapb0", "frame2b", "up2", "turnon" if _vi == 0 else "turnoff", "pick2", "v1pk", "v2pk"] + \\
              ["v%d%s%d" % (_r, "on" if _vi == 0 else "off", min(_vi, len(CK2_BTN[_r]) - 1)) for _r in range(9)] + ["foot"]:
        v_.extend(CKA[_n])
    N_VARS.append(v_)
for _i, v_ in enumerate(N_VARS):
    v_.check(CKP)
    _pri = sum(1 for p_, mk_ in v_ if 'TexturePath: "SkyyGlass/Primary.png"' in SUI.render(mk_))   # ui-data: counting the Skyglass Primary buttons
    assert _pri <= 1, "0.4.27 clicker variant %d: %d Primary buttons" % (_i, _pri)
SUI.assert_proven([mk_ for v_ in N_VARS for p_, mk_ in v_], what="SkyyShards 0.4.27 clicker rows + upgrades view")
SUI.assert_glass_paths([mk_ for v_ in N_VARS for p_, mk_ in v_])
_n_el = [sum(SUI._strip_quoted(SUI.render(mk_)).count("{") for p_, mk_ in v_) for v_ in N_VARS]
N_ELEMENTS = max(_n_el) + CK_NSPOT * 2 + 1 + 8 * 5 + 9 * CK_CL_N
assert N_ELEMENTS < 1000, "0.4.27: the clicker page stays well under ~1,600 elements: %s" % _n_el
print("0.4.27 clicker rows + upgrades view: %d variants checked, elements %s (+ run time: at most %d)" % (len(N_VARS), _n_el, N_ELEMENTS))
# 0.4.24 the quarry variants: each size with every part (springs, smithy, totems, decorations) + the slider row / the Totems row / the other rows on;''')

# ---------------------------------------------------------------------------------------------------- 10. the page: fields, cost lines, spirit, upgrades view, clicks
P.rep('''          "public boolean ckTown;"):   # 0.4.26 the town''', '''          "public boolean ckTown;",   # 0.4.26 the town
          "public String[] ckCL;", "public int[] ckCG;", "public int[] ckUpBtn;", "public long ckPurse;", "public @IC@[] ckCs;", "public long ckCoins;", "public int ckSeedB;",   # 0.4.27
          "public String[] ck2L;", "public String[] ck2E;", "public boolean[] ck2Ok;", "public int[] ck2Seen;", "public int[] ck2Btn;", "public String[] ck2Cur;",
          "public boolean[] ck2Pk;", "public int[] ckMP;", "public String ck2Isl;", "public String ck2Cap;", "public String ck2Also;", "public String ck2Turn;",
          "public boolean ck2TurnOk;", "public long ckSellArm;", "public long ckPickArm;", "public String[] ckSpF;"):''')

PAGE427 = r'''# ---- 0.4.27 (tools/shards_0_4_27_patch.py): THE CLEAR COST LINES, THE SPIRIT ROW, SMITHY I, THE UPGRADES VIEW (mode 2), THE TOWN'S COINS
M(page, r"""
public void toClicker() {
  this.view = 5; this.ckMode = 0; this.ckSlot = -1; this.ckPop = ""; this.ckPopI = -1;
}""")
M(page, r"""
public static String ckShort(long n) {
  if (n < 0L) return "?";
  if (n < 10000000L) return @PKG@.ShCfg.num(n);
  if (n < 10000000000L) return @PKG@.ShCfg.dec((double) (n / 100000L) / 10.0) + "M";
  return @PKG@.ShCfg.dec((double) (n / 100000000L) / 10.0) + "B";
}""")
# one row's cost: each part on its own line "have / need item" (coins first), green = enough, red = not; the old one-line text stays in ckUpC
M(page, r"""
public String ckCostR(int r, long coins, Object[] mats) {
  String s = ckCost(coins, mats);
  if (this.ckUpC != null && r >= 0 && r < this.ckUpC.length) this.ckUpC[r] = s;
  if (this.ckCL == null || r < 0 || r * 3 + 2 >= this.ckCL.length) return s;
  for (int j = 0; j < 3; j++) { this.ckCL[r * 3 + j] = ""; this.ckCG[r * 3 + j] = 0; }
  int n = 0;
  if (coins > 0L) {
    long h = this.ckPurse;
    this.ckCL[r * 3] = ckShort(h) + " / " + @PKG@.ShCfg.num(coins) + " coins";
    this.ckCG[r * 3] = (h < 0L || h >= coins) ? 1 : 2;
    n = 1;
  }
  String[] ids = mats == null ? new String[0] : (String[]) mats[0];
  long[] q = mats == null ? new long[0] : (long[]) mats[1];
  for (int i = 0; i < ids.length && n < 3; i++) {
    long h = this.ckCs == null ? -1L : havIn(this.ckCs, ids[i], ids);
    this.ckCL[r * 3 + n] = ckShort(h) + " / " + @PKG@.ShCfg.num(q[i]) + " " + @PKG@.ShTotem.pretty(ids[i]);
    this.ckCG[r * 3 + n] = (h >= q[i]) ? 1 : 2;
    n++;
  }
  if (n < 3) {   // fix (critic): a red item line says where to get it (a free 3rd line, dim; <= 34 characters)
    String tip = "";
    for (int i = 0; i < ids.length && i < q.length && tip.length() == 0; i++) {
      long h = this.ckCs == null ? -1L : havIn(this.ckCs, ids[i], ids);
      if (h >= 0L && h < q[i]) tip = ids[i].startsWith("Skyy_Ench_") ? "Tip: Auto-Compactor or craft it" : "Tip: Collect first, or make more";
    }
    if (tip.length() > 0) { this.ckCL[r * 3 + n] = tip; this.ckCG[r * 3 + n] = 0; }
  }
  return s;
}""")
# a row without a price: its reason in up to 3 dim lines of at most 34 characters (word-wrapped, never cut off: a 4th line joins the 3rd)
M(page, r"""
public void ckTextR(int r, String t) {
  if (this.ckCL == null || r < 0 || r * 3 + 2 >= this.ckCL.length) return;
  for (int j = 0; j < 3; j++) { this.ckCL[r * 3 + j] = ""; this.ckCG[r * 3 + j] = 0; }
  if (t == null || t.length() == 0) return;
  String[] w = t.split(" ");
  int ln = 0;
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < w.length; i++) {
    if (sb.length() > 0 && sb.length() + 1 + w[i].length() > 34 && ln < 2) { this.ckCL[r * 3 + ln] = sb.toString(); ln++; sb = new StringBuilder(); }
    if (sb.length() > 0) sb.append(' ');
    sb.append(w[i]);
  }
  if (sb.length() > 0) this.ckCL[r * 3 + ln] = sb.toString();
}""")
M(page, r"""
public boolean ckHasLines(int r) {
  if (this.ckCL == null || r < 0 || r * 3 + 2 >= this.ckCL.length) return false;
  return this.ckCL[r * 3].length() > 0 || this.ckCL[r * 3 + 1].length() > 0 || this.ckCL[r * 3 + 2].length() > 0;
}""")
M(page, r"""
public void ckLinesB(@UCB@ b, String pre, int row, int li, int w) {
  if (this.ckCL == null) return;
  for (int j = 0; j < 3; j++) {
    int i = li * 3 + j;
    if (i >= this.ckCL.length || this.ckCL[i] == null || this.ckCL[i].length() == 0) continue;
    String id = pre + row + "C" + j;
    String par = "#" + pre + row + "Cs";
    int g = this.ckCG[i];
    if (g == 1) b.appendInline(par, @CL1@);
    else if (g == 2) b.appendInline(par, @CL2@);
    else b.appendInline(par, @CL0@);
    b.set("#" + id + ".Text", this.ckCL[i]);
  }
}""".replace("@CL0@", CK_J_CLINE[0]).replace("@CL1@", CK_J_CLINE[1]).replace("@CL2@", CK_J_CLINE[2]))
# before a clicker fill: the purse + the bag map (bridges - never under the store lock), the line tables
M(page, r"""
public void ckPre(@IC@[] cs) {
  this.ckCs = cs;
  this.ckPurse = this.me == null ? -1L : @PKG@.ShPay.coins(this.me);
  bagLoad();
  this.ckCL = new String[60]; this.ckCG = new int[60]; this.ckUpBtn = new int[8];
  for (int i = 0; i < 60; i++) this.ckCL[i] = "";
  this.ckCoins = 0L; this.ckSeedB = 0;
  if (this.ckMP == null) { this.ckMP = new int[] { 1, 0 }; }
  if (this.ck2Pk == null) this.ck2Pk = new boolean[2];
}""")
# the island's spirit row (row 2 of every clicker; the upgrades view copies it): its tier, the island's output a minute now -> after, the cost
M(page, r"""
public void ckSpirit(String k, int kd) {
  this.ckSpF = null;
  if (this.ckUpL == null || this.ckUpL.length < 3) return;
  this.ckUpBtn[2] = 0;
  if (k == null || this.ckSlot < 0 || this.ckT < 0) return;
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return;
  double cv = @PKG@.ShCore.tierCv(this.ckT);   // a bridge: before the lock
  long now = @PKG@.ShCore.now();
  int s = this.ckSlot;
  int cur = 0; double r0 = 0.0; double r1 = 0.0; String[] f = null; StringBuilder also = new StringBuilder(); int n = 0;
  @PKG@.ShStore.LOCK.lock(); try {
    if (!@PKG@.ShMath.hasIsland(kd, p, s) || @PKG@.ShIsl.ty(kd, p, s) != this.ckT) return;
    String[] e = @PKG@.ShTotem.entries(kd, p, s);
    int si = @PKG@.ShCore.spiritIdx(kd, e);
    if (si >= 0) { f = @PKG@.ShTotem.parse(e[si]); cur = @PKG@.ShTotem.tierOf(f[1]); }
    r0 = @PKG@.ShMath.rate(kd, p, s, now);
    if (cur < 5) {
      java.util.Properties q = new java.util.Properties();
      q.putAll(p);
      String[] ne;
      if (si < 0) { ne = new String[e.length + 1]; for (int i = 0; i < e.length; i++) ne[i] = e[i]; ne[e.length] = @PKG@.ShKind.WORKER[kd] + ":1"; }
      else { ne = new String[e.length]; for (int i = 0; i < e.length; i++) ne[i] = e[i]; String[] g = @PKG@.ShTotem.parse(e[si]); g[1] = String.valueOf(cur + 1); ne[si] = @PKG@.ShTotem.fmt(g); }
      @PKG@.ShTotem.setEntries(kd, q, s, ne);
      r1 = @PKG@.ShMath.rate(kd, q, s, now);
    }
    for (int i = 0; i < e.length; i++) {
      if (i == si) continue;
      String[] g = @PKG@.ShTotem.parse(e[i]);
      if (also.length() > 0) also.append(", ");
      also.append(@PKG@.ShTotem.name(g));
      n++;
    }
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  this.ckSpF = f;
  String nm = @PKG@.ShTotem.pretty(@PKG@.ShIsl.PROD[this.ckT]);
  this.ckUpL[2] = cur == 0 ? "None yet" : "Tier " + @PKG@.ShTotem.ROMAN[cur - 1] + " / V";
  this.ckUpSeen[2] = cur;
  this.ckUpBtn[2] = cur == 0 ? 1 : 0;
  if (cur >= 5) { this.ckUpE[2] = @PKG@.ShCfg.dec(r0) + " " + nm + " a minute (highest tier)"; this.ckUpC[2] = ""; ckTextR(2, ""); this.ckUpOk[2] = false; }
  else {
    this.ckUpE[2] = (cur == 0 ? "Buy: " : "") + @PKG@.ShCfg.dec(r0) + " -> " + @PKG@.ShCfg.dec(r1) + " " + nm + " a minute";
    ckCostR(2, @PKG@.ShCore.spiritCoins(cur, cv), @PKG@.ShCore.spiritMats(kd, this.ckT, cur));
    this.ckUpOk[2] = this.mine;
  }
  this.ck2Also = n == 0 ? "No other totems on this island." : "Also on this island (kept, still working): " + also.toString();
}""")
# the quarry's Smithy row while it has no smithy: Smithy I bought right here (coins + the quarry's own ore)
M(page, r"""
public void ckSmithy1(int kd) {
  if (kd != @PKG@.ShClk.MK || this.ckQSm != 0 || this.ckT < 0 || this.ckUpL == null || this.ckUpL.length < 8) return;
  double cv = @PKG@.ShCore.tierCv(this.ckT);
  this.ckUpL[7] = "No smithy";
  this.ckUpE[7] = "Smithy I: ores -> bars (auto-smelt)";
  this.ckUpSeen[7] = 0;
  this.ckUpBtn[7] = 1;
  ckCostR(7, @PKG@.ShIsl.coins(@PKG@.ShCfg.MQ_S1H, cv), @PKG@.ShCore.itemCost(@PKG@.ShIsl.PROD[this.ckT], (long) @PKG@.ShCfg.MQ_S1ORE));
  this.ckUpOk[7] = this.mine;
}""")
M(page, r"""
public void ck2Set(int r, String l, String e, boolean ok, int seen) {
  this.ck2L[r] = l; this.ck2E[r] = e; this.ck2Ok[r] = ok; this.ck2Seen[r] = seen;
}""")
# THE UPGRADES VIEW (mode 2): the spirit (= row 2), its two modifier slots, its other totems, "place a totem item"; the shard-wide upgrades + Sell all
M(page, r"""
public void fillUp2(String k, @IC@[] cs) {
  int kd = this.kind;
  this.ck2L = new String[9]; this.ck2E = new String[9]; this.ck2Ok = new boolean[9]; this.ck2Seen = new int[9]; this.ck2Btn = new int[9]; this.ck2Cur = new String[] { "", "" };
  for (int i = 0; i < 9; i++) { this.ck2L[i] = ""; this.ck2E[i] = ""; }
  this.ck2Pk[0] = false; this.ck2Pk[1] = false;
  this.ck2Isl = this.ckChip == null ? "" : this.ckChip;
  this.ck2Cap = this.mine ? "for the whole " + @PKG@.ShKind.NAMES[kd] + " Shard" : "the island owner buys upgrades";
  this.ck2Turn = ""; this.ck2TurnOk = false;
  if (this.ck2Also == null) this.ck2Also = "";
  java.util.Properties p = k == null ? null : @PKG@.ShStore.get(k);
  if (p == null) return;
  // 0 the spirit (row 2's numbers)
  ck2Set(0, this.ckUpL[2], this.ckUpE[2], this.ckUpOk[2], this.ckUpSeen[2]);
  this.ck2Btn[0] = this.ckUpBtn[2];
  for (int j = 0; j < 3; j++) { this.ckCL[30 + j] = this.ckCL[6 + j]; this.ckCG[30 + j] = this.ckCG[6 + j]; }
  if (this.ckT < 0) { ckTextR(10, "No island yet - open Islands to buy the first one."); }
  // 1 + 2 the modifier slots (the spirit's m1 / m2)
  double cv = this.ckT >= 0 ? @PKG@.ShCore.tierCv(this.ckT) : 1.0;
  for (int j = 1; j <= 2; j++) {
    int r = j;
    int mi = this.ckMP[j - 1];
    if (!@PKG@.ShCore.modOk(mi)) { mi = 0; this.ckMP[j - 1] = 0; }
    String cur = this.ckSpF == null ? "" : this.ckSpF[j + 1];
    this.ck2Cur[j - 1] = cur;
    int ci = @PKG@.ShTotem.modIdx(cur);
    this.ck2Btn[r] = ci >= 0 ? 1 : 0;
    String pick = @PKG@.ShTotem.MOD_NAMES[mi] + ": " + @PKG@.ShTotem.MOD_DESC[mi];
    if (this.ckSpF == null) { ck2Set(r, "Empty", "Pick: " + pick, false, 0); ckTextR(10 + r, "Buy the spirit totem first - modifiers sit on it."); continue; }
    ck2Set(r, ci >= 0 ? @PKG@.ShTotem.MOD_NAMES[ci] : "Empty", "Pick: " + pick, false, 0);
    this.ck2Pk[j - 1] = this.mine;
    String other = this.ckSpF[j == 1 ? 3 : 2];
    if (cur.equals(@PKG@.ShTotem.MOD_KEYS[mi])) { ckTextR(10 + r, "This modifier is in this slot - pick another one with < >."); continue; }
    if (other.equals(@PKG@.ShTotem.MOD_KEYS[mi])) { ckTextR(10 + r, "In the other slot already - pick another one with < >."); continue; }
    long have = cs == null ? -1L : hav(cs, @PKG@.ShTotem.MOD_ITEMS[mi]);
    if (have >= 1L) ckCostR(10 + r, 0L, @PKG@.ShCore.itemCost(@PKG@.ShTotem.MOD_ITEMS[mi], 1L));
    else ckCostR(10 + r, @PKG@.ShCore.modCoins(cv), @PKG@.ShCore.modMats(kd, this.ckT));
    this.ck2Ok[r] = this.mine;
  }
  // the shard-wide upgrades: numbers under the lock, the coin curves (bridges) after it
  int st; int cp; int tc; boolean au; int ol; long cap0; long cap1 = 0L; double tm0; String sid = null; long sn = 0L; int pads = 0; int nt = 0;
  String ow0; String ow1 = "";
  @PKG@.ShStore.LOCK.lock(); try {
    st = @PKG@.ShMath.storageTier(kd, p); cp = @PKG@.ShMath.compactor(kd, p); tc = @PKG@.ShMath.compressor(kd, p); au = @PKG@.ShIsl.auto(kd, p); ol = @PKG@.ShIsl.offLv(kd, p);
    cap0 = @PKG@.ShMath.cap(kd, p);
    if (st < 5) { java.util.Properties q = new java.util.Properties(); q.putAll(p); q.setProperty(@PKG@.ShMath.kk(kd, "storage"), String.valueOf(st + 1)); cap1 = @PKG@.ShMath.cap(kd, q); }
    tm0 = @PKG@.ShTotem.tcMult(kd, p);
    ow0 = @PKG@.ShIsl.offWords(kd, p, ol);
    if (ol < 5) ow1 = @PKG@.ShIsl.offWords(kd, p, ol + 1);
    int s = this.ckSlot;
    if (s >= 0 && @PKG@.ShMath.hasIsland(kd, p, s)) {
      if (kd != @PKG@.ShCombat.CK) { sid = @PKG@.ShCore.sellItem(kd, p, s); sn = @PKG@.ShMath.baseOf(kd, p, s); }
      pads = @PKG@.ShMath.pads(@PKG@.ShMath.size(kd, p, s));
      nt = @PKG@.ShTotem.entries(kd, p, s).length;
    }
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  String up = @PKG@.ShKind.UPG[kd];
  // 3 Storage
  if (st >= 5) { ck2Set(3, "Tier 5 / 5", "Holds " + @PKG@.ShCfg.num(cap0) + " items a new island (highest)", false, st); ckTextR(13, "The highest tier."); }
  else { ck2Set(3, "Tier " + st + " / 5", "Holds " + @PKG@.ShCfg.num(cap0) + " -> " + @PKG@.ShCfg.num(cap1) + " items a new island", this.mine, st);
         ckCostR(13, @PKG@.ShCfg.storeCoins(st + 1), @PKG@.ShCore.itemCost(up, (long) @PKG@.ShCfg.storeEnch(st + 1))); }
  // 4 Auto-Compactor
  if (@PKG@.ShKind.ENCH[kd].length() == 0 && @PKG@.ShKind.SMELT_ENCH[kd].length() == 0) { ck2Set(4, "-", "Nothing this shard makes has an Enchanted form yet", false, cp); ckTextR(14, "Not for this shard."); }
  else if (cp >= 2) { ck2Set(4, "II / II", "Enchanted storage + " + @PKG@.ShCfg.CMP_STORE + " % room (highest)", false, cp); ckTextR(14, "The highest tier."); }
  else { ck2Set(4, cp == 0 ? "None" : "I / II", cp == 0 ? "Stores items as Enchanted (100 take 1 place)" : "+" + @PKG@.ShCfg.CMP_STORE + " % room on every island", this.mine, cp);
         ckCostR(14, @PKG@.ShCfg.CMP_COINS[cp + 1], @PKG@.ShCore.itemCost(up, (long) @PKG@.ShCfg.CMP_ITEMS[cp + 1])); }
  // 5 Time Compressor
  if (tc >= 3) { ck2Set(5, "III / III", "Output x" + @PKG@.ShCfg.dec(tm0) + " (highest)", false, tc); ckTextR(15, "The highest tier."); }
  else { ck2Set(5, tc == 0 ? "None" : @PKG@.ShTotem.ROMAN[tc - 1] + " / III", "Output x" + @PKG@.ShCfg.dec(tm0) + " -> x" + @PKG@.ShCfg.dec(@PKG@.ShCfg.TC_MULT[tc + 1]), this.mine, tc);
         ckCostR(15, @PKG@.ShCfg.TC_COINS[tc + 1], @PKG@.ShCore.itemCost("Ingredient_Void_Essence", (long) @PKG@.ShCfg.TC_VOID[tc + 1])); }
  // 6 Automation
  if (au) { ck2Set(6, "Yes", "Every island works by itself at full speed", false, 1); ckTextR(16, "Bought."); }
  else {
    double acv = @PKG@.ShCfg.curve(@PKG@.ShIsl.stepLv(@PKG@.ShCfg.AUTO_STEP));
    ck2Set(6, "No", "Islands work by themselves at full speed", this.mine, 0);
    ckCostR(16, @PKG@.ShIsl.coins(@PKG@.ShIsl.stepH(@PKG@.ShCfg.AUTO_STEP), acv), @PKG@.ShIsl.mats(kd, @PKG@.ShIsl.LAD0[kd], @PKG@.ShCfg.AUTO_ITEMS[kd], 0, 1L));
  }
  // 7 Offline Harvest
  if (ol >= 5) { ck2Set(7, "5 / 5", "Offline: " + ow0 + " (highest)", false, ol); ckTextR(17, "The highest level."); }
  else if (!au) { ck2Set(7, ol + " / 5", "Offline: " + ow0, false, ol); ckTextR(17, "Buy Automation first."); }
  else {
    double ocv = @PKG@.ShCfg.curve(@PKG@.ShIsl.stepLv(@PKG@.ShCore.offStep(ol)));
    ck2Set(7, ol + " / 5", "Offline: " + ow0 + " -> " + ow1, this.mine, ol);
    ckCostR(17, @PKG@.ShCore.offCoins(ol, ocv), @PKG@.ShCore.itemCost(up, @PKG@.ShCore.offEnch(ol)));
  }
  // 8 Sell all (this island's stock)
  if (kd == @PKG@.ShCombat.CK) { ck2Set(8, "-", "Combat drops are collected, not sold", false, 0); ckTextR(18, "Collect the drops instead."); }
  else if (!@PKG@.ShCfg.SELL_ON) { ck2Set(8, "-", "Selling from the store is switched off", false, 0); ckTextR(18, "Switched off on this server."); }
  else if (sid == null || sn <= 0L) { ck2Set(8, "-", "Nothing stored on this island to sell", false, 0); ckTextR(18, "Collect or sell when it has stock."); }
  else { ck2Set(8, ckShort(sn), "This island's " + @PKG@.ShTotem.pretty(sid) + " stock (Enchanted counts 100)", this.mine, 0); ckTextR(18, "Two clicks: the stock goes at the Bazaar's sell price."); }
  // place a totem item
  int n = cs == null ? 0 : @PKG@.ShCore.placeable(kd, cs, @PKG@.ShCore.now()).size();
  if (this.ckT < 0) this.ck2Turn = "";
  else if (n == 0) this.ck2Turn = "Totem items you carry for this shard go on this island here (" + nt + " of " + pads + " totems now).";
  else { this.ck2Turn = "You carry " + n + (n == 1 ? " totem" : " totems") + " for this shard - place one on this island (" + nt + " of " + pads + " totems now)."; this.ck2TurnOk = this.mine && nt < pads; }
}""")
# after a clicker fill: the spirit row, Smithy I, every priceless row's reason as lines, the town's coins, the seed button, the upgrades view
M(page, r"""
public void ckPost(String k, @IC@[] cs) {
  int kd = this.kind;
  ckSpirit(k, kd);
  ckSmithy1(kd);
  if (this.ckUpC != null) for (int r = 0; r < this.ckUpC.length; r++) if (!ckHasLines(r) && this.ckUpC[r] != null && this.ckUpC[r].length() > 0) ckTextR(r, this.ckUpC[r]);
  java.util.Properties p = k == null ? null : @PKG@.ShStore.get(k);
  if (p == null) return;
  int s = this.ckSlot;
  @PKG@.ShStore.LOCK.lock(); try {
    if (kd == @PKG@.ShClk.TK) for (int i = 0; i < @PKG@.ShMath.SLOTS; i++) this.ckCoins = this.ckCoins + @PKG@.ShClk.coinsWaiting(p, i);
    if (s >= 0 && @PKG@.ShMath.hasIsland(kd, p, s)) {
      int t = @PKG@.ShIsl.ty(kd, p, s);
      boolean seeds = @PKG@.ShIsl.SEED[t].length() > 0 && ("farm".equals(@PKG@.ShIsl.STYLE[kd]) || @PKG@.ShIsl.trees(kd));
      boolean au = @PKG@.ShIsl.auto(kd, p);
      if (seeds && !au) this.ckSeedB = 1;
      else if (seeds && @PKG@.ShIsl.seeds(kd, p, s) > 0L) this.ckSeedB = 2;
    }
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (this.ckCoins > 0L) this.sgHint = @PKG@.ShCfg.num(this.ckCoins) + " coins waiting - Collect all pays them";
  else if (kd == @PKG@.ShClk.TK && @PKG@.ShCfg.TF_COINS && @PKG@.ShCfg.fn("mob:fn:killCoins") == null) this.sgHint = this.sgHint + " (no kill coins: needs SkyyMobs 0.1.26+)";
  if (this.ckMode == 2) fillUp2(k, cs);
}""")
# is the page's island still in that slot? (a profile switch / another island = stale)
M(page, r"""
public boolean ckFresh(String k, int kd, int slot) {
  if (k == null || this.key == null || !k.equals(this.key) || this.ckT < 0) return false;
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return false;
  boolean ok;
  @PKG@.ShStore.LOCK.lock(); try {
    ok = slot >= 0 && slot < @PKG@.ShMath.SLOTS && @PKG@.ShMath.hasIsland(kd, p, slot) && @PKG@.ShIsl.ty(kd, p, slot) == this.ckT;
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  return ok;
}""")
M(page, r"""
public int lvNow(String k, int kd, String w) {
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return -2;
  @PKG@.ShStore.LOCK.lock(); try {
    if (w.equals("st")) return @PKG@.ShMath.storageTier(kd, p);
    if (w.equals("cp")) return @PKG@.ShMath.compactor(kd, p);
    if (w.equals("tc")) return @PKG@.ShMath.compressor(kd, p);
    if (w.equals("au")) return @PKG@.ShIsl.auto(kd, p) ? 1 : 0;
    if (w.equals("of")) return @PKG@.ShIsl.offLv(kd, p);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  return -2;
}""")
# the clicks every clicker kind shares (null = not one of them): Upgrades, the pickers, the upgrades view, the seed button, the town's Collect all
M(page, r"""
public String actCk2(String a, @REF@ ref, @ST@ st) {
  if (a.equals("kup")) { this.ckMode = 2; this.ckPop = ""; this.ckSellArm = 0L; this.ckPickArm = 0L; return ""; }
  if (a.startsWith("kmp") && a.length() >= 5) {   // "kmp1-" / "kmp2+": the modifier picker (memory only)
    int j = (int) (a.charAt(3) - '1');
    if (j < 0 || j > 1 || this.ckMP == null) return "";
    int d = a.charAt(4) == '-' ? -1 : 1;
    int n = @PKG@.ShTotem.MOD_KEYS.length;
    int m = this.ckMP[j];
    for (int i = 0; i < n; i++) { m = ((m + d) % n + n) % n; if (@PKG@.ShCore.modOk(m)) break; }
    this.ckMP[j] = m;
    return "";
  }
  boolean ours = a.startsWith("k2") || a.equals("kseed") || (a.equals("colall") && this.kind == @PKG@.ShClk.TK);
  if (!ours) return null;
  String k = resolve(st);
  if (k == null) return "-Only the island owner and co-op members can use this shard.";
  java.util.UUID u = this.me;
  int kd = this.kind;
  if (a.equals("colall")) {   // the town: its coins first (debit + save, then the purse), then the 0.4.22 Collect all
    if (!@PKG@.ShRole.mayManage(u, k)) return "-Only the island owner collects here.";
    java.util.Properties gp = @PKG@.ShStore.get(k);   // fix2: the coins pass the same gate as Collect (profile loading, owned, lock) - else none move
    String gno = gp == null ? "-" : @PKG@.ShCore.gate(u, k, kd, gp);
    String cr = gno == null ? @PKG@.ShClk.payCoins(u, k, kd) : "";
    String ir = @PKG@.ShCore.collect(u, k, kd, -1, invOf(ref, st));
    if (cr.length() == 0) return ir;
    if (!cr.startsWith("+")) return ir.startsWith("+") ? ir + " " + cr.substring(1) : cr;
    if (ir.startsWith("+")) return ir + " + " + cr.substring(1) + ".";
    return "+Collected " + cr.substring(1) + "." + (ir.length() > 1 && !ir.startsWith("=") ? " " + ir.substring(1) : "");
  }
  if (!this.mine) return "-Only the island owner buys upgrades.";
  @IC@[] cs = invOf(ref, st);
  int s = this.ckSlot;
  if (this.key == null || !k.equals(this.key)) return "=The page is up to date now - click again.";   // a profile switch since the page was drawn
  if (a.equals("kseed")) {   // the seed store: Give (a manual shard) / Take back (automated)
    if (s < 0 || !ckFresh(k, kd, s)) return "=The page is up to date now - click again.";
    java.util.Properties p = @PKG@.ShStore.get(k);
    if (p == null) return "-This shard's file could not be read.";
    boolean au;
    @PKG@.ShStore.LOCK.lock(); try { au = @PKG@.ShIsl.auto(kd, p); } finally { @PKG@.ShStore.LOCK.unlock(); }
    return au ? @PKG@.ShCore.seedsTake(u, k, kd, s, cs) : @PKG@.ShCore.seedsGive(u, k, kd, s, cs);
  }
  if (a.equals("k2pick")) {   // Pick up Shard (2 clicks): the portal goes back into your inventory, islands + storage kept
    long now = System.currentTimeMillis();
    if (now - this.ckPickArm > 10000L) { this.ckPickArm = now; return "=Click Pick up Shard again to pick it up. Its islands and storage are kept."; }
    this.ckPickArm = 0L;
    if (this.testMode) return "=test: pick";
    return @PKG@.ShCore.pickup(u, k, kd, worldOf(st), cs);
  }
  if (a.equals("k2sell")) {   // Sell all (2 clicks): this island's stock (ShCore.sell, mode all)
    if (s < 0 || !ckFresh(k, kd, s)) return "=The page is up to date now - click again.";
    long now = System.currentTimeMillis();
    if (now - this.ckSellArm > 10000L) { this.ckSellArm = now; return "=Click Sell all again to sell this island's stock."; }
    this.ckSellArm = 0L;
    return @PKG@.ShCore.sell(u, k, kd, s, 1, "");
  }
  if (a.equals("k2turn")) {   // place the first totem item of this shard you carry on this island (the old pad rules)
    if (s < 0 || !ckFresh(k, kd, s)) return "=The page is up to date now - click again.";
    return @PKG@.ShCore.turnIn(u, k, kd, s, cs);
  }
  String[] q = a.substring(2).split(":", -1);
  String w = q[0];
  int seen = -1;
  try { seen = q.length > 1 ? Integer.parseInt(q[1]) : -1; } catch (Throwable x) { seen = -1; }
  if (w.equals("s")) {
    if (s < 0 || !ckFresh(k, kd, s)) return "=The page is up to date now - click again.";
    return @PKG@.ShCore.buySpirit(u, k, kd, s, seen, cs);
  }
  if (w.equals("m1") || w.equals("m2")) {   // "k2m<j>:<picked>:<the key the slot showed>"
    if (s < 0 || !ckFresh(k, kd, s)) return "=The page is up to date now - click again.";
    return @PKG@.ShCore.buyMod(u, k, kd, s, w.equals("m1") ? 1 : 2, seen, q.length > 2 ? q[2] : "", cs);
  }
  int lv = lvNow(k, kd, w);
  if (lv == -2) return "";
  if (seen != lv) return "=The page is up to date now - click again.";
  if (w.equals("st")) return @PKG@.ShCore.buyStorage(u, k, kd, cs);
  if (w.equals("cp")) return @PKG@.ShCore.buyCompactor(u, k, kd, cs);
  if (w.equals("tc")) return @PKG@.ShCore.buyCompressor(u, k, kd, cs);
  if (w.equals("au")) return @PKG@.ShCore.buyAuto(u, k, kd, cs);
  if (w.equals("of")) return @PKG@.ShCore.buyOffline(u, k, kd, cs);
  return "";
}""")
'''
P.rep('''M(page, r"""
public static String ckSize(int sz) {''', PAGE427 + '''M(page, r"""
public static String ckSize(int sz) {''')
# every fill's cost lines through ckCostR (the same string + the lines)
_n0 = len(re.findall(r"this\.ckUpC\[(\d)\] = ckCost\(", P.s))
assert _n0 == 22, _n0
_n1 = 0
for _fn in ("fillQuarry", "fillFarm", "fillTown", "fillClick"):
    _a = P.s.index("public void %s(String k, @IC@[] cs, @REF@ ref, @ST@ st) {" % _fn)
    _b = P.s.index('}""")\n', _a)
    _body = P.s[_a:_b]
    _new = re.sub(r"this\.ckUpC\[(\d)\] = ckCost\(", r"this.ckUpC[\1] = ckCostR(\1, ", _body)
    _n1 += _body.count("= ckCost(")
    P.rep(_body, _new)
assert _n1 == _n0, (_n1, _n0)
# build0: the purse + bags before a clicker fill, the 0.4.27 rows after it
P.rep('''  else if (this.view == 5 && this.kind == @PKG@.ShClk.MK) fillQuarry(k, cs, ref, st);   // 0.4.24
  else if (this.view == 5 && this.kind == @PKG@.ShClk.CRK) fillFarm(k, cs, ref, st);   // 0.4.25
  else if (this.view == 5 && this.kind == @PKG@.ShClk.TK) fillTown(k, cs, ref, st);   // 0.4.26
  else if (this.view == 5) fillClick(k, cs, ref, st);   // 0.4.23''', '''  else if (this.view == 5) {   // 0.4.27: ckPre (purse + bags, before any lock) / ckPost (the spirit, Smithy I, cost lines, coins, the upgrades view)
    ckPre(cs);
    if (this.kind == @PKG@.ShClk.MK) fillQuarry(k, cs, ref, st);   // 0.4.24
    else if (this.kind == @PKG@.ShClk.CRK) fillFarm(k, cs, ref, st);   // 0.4.25
    else if (this.kind == @PKG@.ShClk.TK) fillTown(k, cs, ref, st);   // 0.4.26
    else fillClick(k, cs, ref, st);   // 0.4.23
    ckPost(k, cs);
  }''')
# the clicks: the shared ones first; the spirit row + Smithy I buy on the page; no more Shard menu / Storage tab
P.rep('''public String actClick(String a, @REF@ ref, @ST@ st) {
  if (this.kind == @PKG@.ShClk.MK) return actQuarry(a, ref, st);   // 0.4.24 the Mining quarry
  if (!a.startsWith("kt")) this.ckPop = "";
  if (a.equals("kback")) { this.view = 0; this.tab = 1; return ""; }
  if (a.equals("kstore")) { this.view = 0; this.tab = 0; return ""; }''', '''public String actClick(String a, @REF@ ref, @ST@ st) {
  String r27 = actCk2(a, ref, st);   // 0.4.27: Upgrades, the upgrades view, the seed button, the town's coins
  if (r27 != null) return r27;
  if (this.kind == @PKG@.ShClk.MK) return actQuarry(a, ref, st);   // 0.4.24 the Mining quarry
  if (!a.startsWith("kt")) this.ckPop = "";''')
P.rep('''public String actQuarry(String a, @REF@ ref, @ST@ st) {
  if (!a.startsWith("kt")) this.ckPop = "";
  if (a.equals("kback")) { this.view = 0; this.tab = 1; return ""; }
  if (a.equals("kstore")) { this.view = 0; this.tab = 0; return ""; }''', '''public String actQuarry(String a, @REF@ ref, @ST@ st) {
  if (!a.startsWith("kt")) this.ckPop = "";''')
P.rep('''    if (row == 2 || (row == 7 && this.ckQSm == 0)) { this.view = 0; this.tab = 3; this.sel = this.ckTi; this.tpad = 0; return ""; }
    if (row < 0 || row > 7) return "";''', '''    if (row < 0 || row > 7) return "";''')
P.rep('''    @IC@[] cs = invOf(ref, st);
    if (row == 0) return @PKG@.ShClk.buyNode(u, k, kd, s, seen, cs);
    if (row == 6) return @PKG@.ShClk.buyLuck(u, k, kd, s, seen, cs);''', '''    @IC@[] cs = invOf(ref, st);
    if (row == 2) return @PKG@.ShCore.buySpirit(u, k, kd, s, seen, cs);   // 0.4.27: the spirit row buys / tiers up here
    if (row == 7 && seen == 0 && this.ckQSm == 0) return @PKG@.ShCore.buySmithy1(u, k, kd, s, cs);   // 0.4.27: Smithy I on the page
    if (row == 0) return @PKG@.ShClk.buyNode(u, k, kd, s, seen, cs);
    if (row == 6) return @PKG@.ShClk.buyLuck(u, k, kd, s, seen, cs);''')
P.rep('''    if (row == 2) { this.view = 0; this.tab = 3; this.sel = this.ckTi; this.tpad = 0; return ""; }
    if (row < 0 || row > 5) return "";''', '''    if (row < 0 || row > 5) return "";''')
P.rep('''    @IC@[] cs = invOf(ref, st);
    if (row == 0) return @PKG@.ShClk.buyNode(u, k, kd, s, seen, cs);
    java.util.Properties p = @PKG@.ShStore.get(k);''', '''    @IC@[] cs = invOf(ref, st);
    if (row == 2) return @PKG@.ShCore.buySpirit(u, k, kd, s, seen, cs);   // 0.4.27: the spirit row buys / tiers up here
    if (row == 0) return @PKG@.ShClk.buyNode(u, k, kd, s, seen, cs);
    java.util.Properties p = @PKG@.ShStore.get(k);''')

# ---------------------------------------------------------------------------------------------------- 11. IMAGE SHRINK part 2 (tools/ci/ui_budget.py)
SHRINK = r'''# ---- 0.4.27 IMAGE SHRINK part 2 (tools/shards_0_4_27_patch.py; tools/ci/ui_budget.py: the client's UI atlas): the Map tab pictures of the four clicker shards go
# (their old menu never opens again), the 43 range rings of the retired totem page go, Ranching / Orchard keep their Map base as 1x (the 2 x 2 average of
# the @2x picture = what the client showed at 100 %; same markup path), the clicker map cards ship 1x at the size they are drawn (210 x 140)
import zlib as _zl427, struct as _st427, math


def _png_rgba427(data):
    """our own PNGs (8-bit RGBA, not interlaced) -> (w, h, bytearray RGBA)"""
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    i_, idat, w_, h_ = 8, b"", 0, 0
    while i_ < len(data):
        n_ = _st427.unpack(">I", data[i_:i_ + 4])[0]
        t_ = data[i_ + 4:i_ + 8]
        c_ = data[i_ + 8:i_ + 8 + n_]
        if t_ == b"IHDR":
            w_, h_, bd_, ct_, _cm, _fm, il_ = _st427.unpack(">IIBBBBB", c_)
            assert bd_ == 8 and ct_ == 6 and il_ == 0, (bd_, ct_, il_)
        elif t_ == b"IDAT":
            idat += c_
        i_ += 12 + n_
    raw = _zl427.decompress(idat)
    st_, out = w_ * 4, bytearray(w_ * h_ * 4)
    prev = bytearray(st_)
    for y_ in range(h_):
        f_ = raw[y_ * (st_ + 1)]
        ln_ = bytearray(raw[y_ * (st_ + 1) + 1:(y_ + 1) * (st_ + 1)])
        for x_ in range(st_):
            a_ = ln_[x_ - 4] if x_ >= 4 else 0
            b_ = prev[x_]
            c_ = prev[x_ - 4] if x_ >= 4 else 0
            if f_ == 1:
                ln_[x_] = (ln_[x_] + a_) & 255
            elif f_ == 2:
                ln_[x_] = (ln_[x_] + b_) & 255
            elif f_ == 3:
                ln_[x_] = (ln_[x_] + ((a_ + b_) >> 1)) & 255
            elif f_ == 4:
                p_ = a_ + b_ - c_
                pa_, pb_, pc_ = abs(p_ - a_), abs(p_ - b_), abs(p_ - c_)
                ln_[x_] = (ln_[x_] + (a_ if pa_ <= pb_ and pa_ <= pc_ else (b_ if pb_ <= pc_ else c_))) & 255
        out[y_ * st_:(y_ + 1) * st_] = ln_
        prev = ln_
    return w_, h_, out


def _png_half427(data):
    """an @2x PNG -> its 1x PNG (the 2 x 2 average, premultiplied alpha)"""
    w_, h_, px = _png_rgba427(data)
    assert w_ % 2 == 0 and h_ % 2 == 0, (w_, h_)
    o_ = SMAP.Pic(w_ // 2, h_ // 2)
    dst = o_.px
    for y_ in range(h_ // 2):
        r0_, r1_ = 2 * y_ * w_, (2 * y_ + 1) * w_
        for x_ in range(w_ // 2):
            ps_ = (r0_ + 2 * x_, r0_ + 2 * x_ + 1, r1_ + 2 * x_, r1_ + 2 * x_ + 1)
            sa_ = px[ps_[0] * 4 + 3] + px[ps_[1] * 4 + 3] + px[ps_[2] * 4 + 3] + px[ps_[3] * 4 + 3]
            if not sa_:
                continue
            q_ = (y_ * (w_ // 2) + x_) * 4
            for ch_ in range(3):
                dst[q_ + ch_] = int((sum(px[p_ * 4 + ch_] * px[p_ * 4 + 3] for p_ in ps_) + sa_ // 2) // sa_)
            dst[q_ + 3] = (sa_ + 2) // 4
    return SMAP.png(o_)


def _png_fit427(data, W_, H_):
    """an RGBA PNG -> W_ x H_ (area average, premultiplied alpha): a picture right-sized to the size it is drawn at"""
    w_, h_, px = _png_rgba427(data)
    o_ = SMAP.Pic(W_, H_)
    dst = o_.px
    sx, sy = float(w_) / W_, float(h_) / H_
    for y_ in range(H_):
        y0, y1 = y_ * sy, (y_ + 1) * sy
        for x_ in range(W_):
            x0, x1 = x_ * sx, (x_ + 1) * sx
            acc, wa = [0.0, 0.0, 0.0], 0.0
            for yy in range(int(y0), min(h_, int(math.ceil(y1)))):
                fy = min(y1, yy + 1) - max(y0, yy)
                for xx in range(int(x0), min(w_, int(math.ceil(x1)))):
                    f_ = fy * (min(x1, xx + 1) - max(x0, xx))
                    q_ = (yy * w_ + xx) * 4
                    a_ = px[q_ + 3] * f_
                    if a_ <= 0:
                        continue
                    wa += a_
                    for ch_ in range(3):
                        acc[ch_] += px[q_ + ch_] * a_
            if wa <= 0:
                continue
            q_ = (y_ * W_ + x_) * 4
            for ch_ in range(3):
                dst[q_ + ch_] = max(0, min(255, int(acc[ch_] / wa + 0.5)))
            dst[q_ + 3] = max(0, min(255, int(wa / (sx * sy) + 0.5)))
    return SMAP.png(o_)


def _area427(paths):
    n_ = 0
    for p_ in paths:
        if p_.endswith(".png"):
            w_, h_ = SMAP.png_size(MAP_ASSETS[p_])
            n_ += w_ * h_
    return n_


_UI0 = _area427([p_ for p_ in MAP_ASSETS if p_.startswith(MJAR + MDIR)])
_CKK427 = [KINDS[_k] for _k in range(NK) if KINDS[_k] in ("Mining", "Foraging", "Farming", "Combat")]
assert len(_CKK427) == 4
_drop427 = []
for _p in sorted(MAP_ASSETS):
    if not _p.startswith(MJAR + MDIR):
        continue
    _n = _p[len(MJAR + MDIR):]
    if _n.startswith("Range/") or any(_n == "Base%s@2x.png" % _k or re.fullmatch(r"%sE\d+@2x\.png" % _k, _n) for _k in _CKK427):
        _drop427.append(_p)
for _p in _drop427:
    del MAP_ASSETS[_p]
_half427 = [MJAR + MDIR + "Base%s@2x.png" % _k for _k in ("Ranching", "Orchard")] + \
           sorted(_p for _p in MAP_ASSETS if re.fullmatch(re.escape(MJAR + MDIR) + r"Clk(Map|FMap|QMap|TMap)\d+@2x\.png", _p))
assert len(_half427) == 2 + 15 + 15 + len(MQ_LAD) + 5, len(_half427)
for _p in _half427:
    _d = MAP_ASSETS.pop(_p)
    MAP_ASSETS[_p.replace("@2x.png", ".png")] = _png_half427(_d) if "/Base" in _p else _png_fit427(_d, 210, 140)   # the cards are drawn 210 x 140
_UI1 = _area427([p_ for p_ in MAP_ASSETS if p_.startswith(MJAR + MDIR)])
print("0.4.27 image shrink: %d old map / range pictures dropped, %d pictures 1x: the Shards UI pictures %.2f -> %.2f Mpx" % (len(_drop427), len(_half427), _UI0 / 1e6, _UI1 / 1e6))
'''
P.rep('''jar = os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)
man = B.manifest("SkyyShards", VERSION,''', SHRINK + '''jar = os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)
man = B.manifest("SkyyShards", VERSION,''')

# ---------------------------------------------------------------------------------------------------- 11b. ShMig0427 into the jar; the top bar's Upgrades
P.rep('''ALLC = ALLC + [ckc]   # 0.4.23: ShClk''', '''ALLC = ALLC + [ckc]   # 0.4.23: ShClk
ALLC = ALLC + [smig427]   # 0.4.27: ShMig0427''')
P.rep('''a_.append((CK_TOP, G_.glass_button(CKP + "MenuB", "Shard menu", "secondary", w=170, h=38, anchor={"top": 3, "right": 8})))''',
      '''a_.append((CK_TOP, G_.glass_button(CKP + "MenuB", "Upgrades", "secondary", w=170, h=38, anchor={"top": 3, "right": 8})))   # 0.4.27: was Shard menu''')

# ---------------------------------------------------------------------------------------------------- 12. the ready line
P.rep(r'''log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.26:''', r'''log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.27: clicker-only (the portal opens the clicker, no shard worlds; Upgrades = the spirit totem + 2 modifiers and the shard-wide upgrades; every cost line have / need; Smithy I on the quarry page; town kills pay coins); 0.4.26:''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
_i = P.s.index
assert _i("public static String buyOffline0(") < _i("public static String buySpirit0(") < _i("public void ckSpirit("), "ShCore before the page"
assert _i("public static boolean clicker(int kd)") < _i("public void toClicker()") < _i("public Object apply(Object o) { @PR@ pr = (@PR@) o;"), "clicker / toClicker before ShPageFn"
assert _i("public void ckLinesB(") < _i("public void buildClick("), "ckLinesB before buildClick"
assert _i("public String actCk2(") < _i("public String actQuarry("), "actCk2 before actQuarry / actClick"
assert _i("public void ckPost(") < _i("public void build0("), "ckPre / ckPost before build0"
assert _i("public static String addDrops(") < _i("public static String commitKeys("), "addDrops before commitKeys"
assert _i("public static String payCoins(") < _i("public void build0("), "payCoins before the page"
P.finish()
