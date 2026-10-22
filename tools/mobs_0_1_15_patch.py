"""Derive SkyyMobs/build_skyymobs_0.1.15.py from the GENERATED 0.1.14 (build_skyymobs_0.1.14.py = the tools/deploy_set.py SET pin, made by
tools/mobs_0_1_14_patch.py). Every anchor is asserted once; at the end every change is undone on a copy and compared with 0.1.14
(tools/soundpass_gen.Patch); line endings kept.
Run:  python tools/mobs_0_1_15_patch.py   then   python SkyyMobs/build_skyymobs_0.1.15.py   then   python SkyyMobs/test_skyymobs_0.1.15.py
Edit THIS file, never the generated script (never --deploy).

0.1.15 (2026-10-22) = BALANCE PASS P8b, the SkyyMobs part (research/Balance-P8-Rebirth-Spec.md 4.1 / 4.2 / 5.1 / 5.4 item 7; FULL round
  with SkyyTrees 0.4.6 + SkyyClasses 0.1.45 - pin and roll back TOGETHER). Skyy (2026-10-21): "keep going down the list. dont stop until the
  entire list is done" + "just go with the recommended on all of them" (spec Q10 [yes]: the Combat tree loot rows live now, held so the
  UT / Mythic rates stay on the P5 targets).
  1. THE SPOILS ROWS (Combat tree branch 3; tools/trees_v3_effects.py EFFECTS applier SkyyMobs): on a kill by a player (the killing blow;
     a pet's = its owner's, pets:fn:ownerOf), AFTER the engine dropped the mob's own loot (NPCDamageSystems$DropDeathItems) and before its
     corpse goes: Scavenger (+2 % a rank) 1 more item of a fresh roll of the mob's drop list; Coin Purse (3 % a rank) coins = the mob's
     level (SkyyCoins coins:fn:add; vanilla mobs pay no coins, so "+3 % coins" became a chance of coins); Rare Drop (+1 % a rank) 1 more
     of the drop list's rarest item (4 rolls, the least seen); Boss Hunter (+3 % a rank, bosses + mini bosses: SkyyMobs' own rank) the
     whole drop list again; Lucky Kill (2 % a rank) the whole drop list again. Ranks: SkyyTrees tree:fn:level, cached 1 s a player;
     value = min(per x rank, ceiling) (Server Setup -> Mobs -> Skill trees, Skyy_SkyyMobs/trees.properties, a NEW file).
  2. NEVER GEAR, so the UT / Mythic rates stay on P5: SkyyMobs owns no gear roll - SkyyGear's extra bag (loot.mob.chance), its UT meter
     (elite / mini boss / dungeon kills) and its Mythic boss roll (+ pity) run on the KILL, once, exactly as before. An extra roll here
     skips every Weapon_ / Armor_ / Tool_ / Shield / Skyy_ item (no vanilla gear for SkyyGear's death-drop tagging to turn into a bag) and
     calls no gear:fn:*. The harness rolls 10,000 kills with every row maxed: 0 gear stacks, 0 gear calls.
  3. The spawn = the engine's own recipe (ItemComponent.generateItemDrops at the mob + (0, 1, 0) + CommandBuffer.addEntities, as SkyySacks'
     killer share), so SkyySacks' auto-pickup claim at that spot takes it like the mob's own drops. One roll per death (mob UUID map).
  4. tree:reads:SkyyMobs = the 5 keys (put at setup, our value removed at shutdown); SkyyTrees 0.4.6 sells them only while listed.
  5. FIXER (critics 2026-10-22): (a) the Spoils go to the OWNER of the mob's drop as SkyySacks claims it - the top damager (MobCredit, read
     whether or not SkyySacks already took the entry) when that player is in this world, else the killing blow's player - so the ranks
     that roll, the auto-picked items and Coin Purse all belong to the same player; (b) one roll per death holds 10 minutes (a long boss
     corpse never rolls twice; the purge runs at most once a second past 512 entries); (c) "never gear" also skips by the item asset, not
     only the name: any weapon / armour / tool, anything with durability, anything that does not stack (max stack 1: keys, quest items,
     a pack mod's gear under another name).
SAVED DATA: none. One new system (SpoilsSys: NPC + DeathComponent, AFTER DropDeathItems, BEFORE CorpseRemoval; not registered = no
spoils this start, logged) and two classes (MobSpoils, SpoilsSys); no new command.
ROLLBACK 0.1.15 -> 0.1.14: only TOGETHER with SkyyTrees 0.4.5 + SkyyClasses 0.1.44 (0.1.14 lists no keys: SkyyTrees 0.4.6 would show the
Spoils rows as coming soon while its gates count them). trees.properties stays, unread.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G
import trees_v3_effects as V3E

V3E.check()
SP = V3E.rows("SkyyMobs")
assert [(e[2], e[4], e[5]) for e in SP] == [("r1a", "drop", 2.0), ("r1b", "coins", 3.0), ("r3b", "rare", 1.0), ("r4a", "bossRoll", 3.0), ("r5a", "dbl", 2.0)]

P = G.Patch(os.path.join(ROOT, "SkyyMobs", "build_skyymobs_0.1.14.py"), os.path.join(ROOT, "SkyyMobs", "build_skyymobs_0.1.15.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.1.14"') and P.s.startswith('"""SkyyMobs 0.1.14 - build script'), "build_skyymobs_0.1.14.py is not the SET pin 0.1.14"
assert "0.1.15" not in P.s
SYS0, CMD0, PUT0, CLS0 = P.s.count("registerSystem("), P.s.count("registerCommand("), P.s.count("bridge().put("), P.s.count("makeClass(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.1.15 (2026-10-22)"):].rstrip() + "\n\n"

P.rep('''"""SkyyMobs 0.1.14 - build script (javassist via jpype). GENERATED by tools/mobs_0_1_14_patch.py from the SET pin 0.1.13 - edit the
patch, never this file. Run: python SkyyMobs/build_skyymobs_0.1.14.py -> SkyyMobs/SkyyMobs-0.1.14.jar (never --deploy).
Test: python SkyyMobs/test_skyymobs_0.1.14.py
''', '''"""SkyyMobs 0.1.15 - build script (javassist via jpype). GENERATED by tools/mobs_0_1_15_patch.py from the SET pin 0.1.14 - edit the
patch, never this file. Run: python SkyyMobs/build_skyymobs_0.1.15.py -> SkyyMobs/SkyyMobs-0.1.15.jar (never --deploy).
Test: python SkyyMobs/test_skyymobs_0.1.15.py
''' + NOTE)
P.rep('VERSION = "0.1.14"', 'VERSION = "0.1.15"')

# ---------- engine tokens + the probed members of the spoils (the SkyySacks 0.8.3 killer-share recipe)
P.rep('''assert T["HITCAP"] == "35"''', '''assert T["HITCAP"] == "35"
# 0.1.15 (Balance P8b): the spoils system - the engine classes of the death-drop recipe (SkyySacks 0.8.3's killer share, SkyyGear's mobRoll)
T.update({"ETS": "com.hypixel.hytale.component.system.tick.EntityTickingSystem",
          "DTHC": "com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent",
          "ITC": "com.hypixel.hytale.server.core.modules.entity.item.ItemComponent",
          "HLDR": "com.hypixel.hytale.component.Holder",
          "RTF": "com.hypixel.hytale.math.vector.Rotation3f",
          "IMOD": "com.hypixel.hytale.server.core.modules.item.ItemModule",
          "ISTK": "com.hypixel.hytale.server.core.inventory.ItemStack",
          "ITMA": "com.hypixel.hytale.server.core.asset.type.item.config.Item"})''')
P.rep('''for _c, _m, _r, _a in SIGS:
    probe_sig(_c, _m, _r, _a)''', '''# 0.1.15 (Balance P8b): the spoils system's engine members
SIGS += [(G["ETS"], "tick", "void", ["float", "int", G["ACH"], G["ST"], G["CB"]]), (G["ETS"], "isParallel", "boolean", ["int", "int"]),
         (G["DTHC"], "getComponentType", G["CTYPE"], []), (G["DTHC"], "getDeathInfo", G["DMG"], []),
         (G["ROLE"], "getDropListId", "java.lang.String", []), (G["ROLE"], "hasDroppedDeathItems", "boolean", []),
         (G["IMOD"], "get", G["IMOD"], []), (G["IMOD"], "getRandomItemDrops", "java.util.List", ["java.lang.String"]),
         (G["IMOD"], "isEnabled", "boolean", []),
         (G["ITC"], "generateItemDrops", G["HLDR"] + "[]", ["com.hypixel.hytale.component.ComponentAccessor", "java.util.List", G["VEC"], "com.hypixel.hytale.math.vector.Rotation3fc"]),
         (G["CB"], "addEntities", G["REF"] + "[]", [G["HLDR"] + "[]", G["ADDR"]]),
         (G["ISTK"], "<init>", "void", ["java.lang.String", "int"]), (G["ISTK"], "getItemId", "java.lang.String", []),
         (G["ISTK"], "getQuantity", "int", []), (G["ISTK"], "isEmpty", "boolean", []),
         (G["NPCE"], "getRole", G["ROLE"], []), (G["REF"], "getStore", G["ST"], []),
         # fixer: the drop owner (SkyySacks' here(): Universe.getPlayer -> PlayerRef.getReference) + the item-asset gear check
         (G["UNIV"], "getPlayer", G["PR"], ["java.util.UUID"]), (G["PR"], "getReference", G["REF"], []),
         (G["ISTK"], "getItem", G["ITMA"], []), (G["ISTK"], "getMaxDurability", "double", []), (G["ITMA"], "getMaxStack", "int", [])]
for _c, _m, _r, _a in SIGS:
    probe_sig(_c, _m, _r, _a)
B.probe(pool, G["RTF"], "IDENTITY")
for _m in ("getWeapon", "getArmor", "getTool"):   # fixer: the item-asset gear check (any return type: compared with null)
    B.probe(pool, G["ITMA"], _m)
    PROBED.append("Item." + _m)
PROBED.append("Rotation3f.IDENTITY")''')

# ---------- the two classes
P.rep('''mp4 = pool.makeClass(PKG + ".MobMigP4")    # 0.1.14: the one-time Balance P4 combat update of config.properties''',
      '''mp4 = pool.makeClass(PKG + ".MobMigP4")    # 0.1.14: the one-time Balance P4 combat update of config.properties
msp = pool.makeClass(PKG + ".MobSpoils")    # 0.1.15: Balance P8b - the Combat tree's Spoils rows (rules + numbers)
mss = pool.makeClass(PKG + ".SpoilsSys", pool.get(G["ETS"]))   # 0.1.15: ... the death system (after DropDeathItems)''')
P.rep('''m11, m12, mp4]''', '''m11, m12, mp4, msp, mss]''')

# ---------- Server Setup -> Mobs -> Skill trees (10 rows) + the fields they bind (before the kit)
P.rep('''_entries = {"bands.biome": len(BIOME_ROWS), "bands.env": len(ENV_ROWS), "bands.world": 0, "bands.zone": len(ZONE_ROWS),''',
      '''# 0.1.15 (Balance P8b): Skill trees - the 5 Spoils rows, per rank + ceiling (tools/trees_v3_effects.py cfg_rows; field: rows = live)
TREES_FILE = "Skyy_SkyyMobs/trees.properties"
import trees_v3_effects as V3E
V3E.check()
CFG_CATS.append(("trees", "Skill trees"))
CFG_ROWS += V3E.cfg_rows("SkyyMobs", "MobSpoils", TREES_FILE, "trees")
assert len(CFG_CATS) <= 16 and sum(1 for _r in CFG_ROWS if _r[2] == "trees") == 10
_entries = {"bands.biome": len(BIOME_ROWS), "bands.env": len(ENV_ROWS), "bands.world": 0, "bands.zone": len(ZONE_ROWS),''')
P.rep('''_fit_bad, _fit = menu_fit(CFG_ROWS, CFG_CATS, CFG_TITLE, VERSION, CFG_NOTE, [CFG_FILE, BANDS_FILE], _entries)''',
      '''_fit_bad, _fit = menu_fit(CFG_ROWS, CFG_CATS, CFG_TITLE, VERSION, CFG_NOTE, [CFG_FILE, BANDS_FILE, TREES_FILE], _entries)''')
P.rep('''_old_bad, _old = menu_fit([r for r in _old_rows if not r[0].startswith("rank.")], [("levels", "Who gets levels")] + [c for c in CFG_CATS[1:] if c[0] != "rank"], CFG_TITLE, "0.1", CFG_NOTE, [CFG_FILE, BANDS_FILE], _entries)''',
      '''_old_bad, _old = menu_fit([r for r in _old_rows if not r[0].startswith(("rank.", "tree."))], [("levels", "Who gets levels")] + [c for c in CFG_CATS[1:] if c[0] not in ("rank", "trees")], CFG_TITLE, "0.1", CFG_NOTE, [CFG_FILE, BANDS_FILE], _entries)''')
P.rep('''kit = CFG.emit(pool, PKG, MOD=MOD, TITLE="Mobs", VERSION=VERSION, NODE=NODE, CATS=CFG_CATS, ROWS=CFG_ROWS,
               FILES=[CFG_FILE, BANDS_FILE], NOTE=CFG_NOTE,
               RELOAD="MobCfg.reloadAll", KEEP=10, DEFAULTS={"config.properties": CFG_TEXT, "bands.properties": BANDS_TEXT})''',
      '''# 0.1.15 (Balance P8b): MobSpoils' numbers (the kit binds its fields) - the rules come after MobCredit (below)
for _f in [V3E.cfg_text_field("SkyyMobs")] + V3E.cfg_fields("SkyyMobs"):
    F(msp, _f)
for _m in V3E.cfg_methods("SkyyMobs", "@PKG@.MobLog.warn"):
    M(msp, _m)
kit = CFG.emit(pool, PKG, MOD=MOD, TITLE="Mobs", VERSION=VERSION, NODE=NODE, CATS=CFG_CATS, ROWS=CFG_ROWS,
               FILES=[CFG_FILE, BANDS_FILE, TREES_FILE], NOTE=CFG_NOTE,
               RELOAD="MobCfg.reloadAll", KEEP=10, DEFAULTS={"config.properties": CFG_TEXT, "bands.properties": BANDS_TEXT, "trees.properties": V3E.cfg_text("SkyyMobs")})''')

# ---------- MobSpoils rules + SpoilsSys (after MobCredit: petOwner)
SPOILS = r'''# ================================================================= 0.1.15 MobSpoils + SpoilsSys: the Combat tree's Spoils rows (Balance P8b)
# vals(u) = { expiry, drop, coins, rare, bossRoll, dbl } in whole % (min(per x rank, ceiling) each; ranks from SkyyTrees tree:fn:level
# {UUID, "Skill.Combat.b3.<id>"}, cached VAL_MS a player). extra() = the extra { id, count } pairs of one kill (never gear); spawn() makes
# them plain new stacks; coins() = Coin Purse.
# ROLLS = harness seam (always null in the game): dropListId -> List of ItemStack instead of ItemModule.getRandomItemDrops.
_SPK = [V3E.key(_e[0], _e[1], _e[2]) for _e in V3E.rows("SkyyMobs")]
_SPC = ["drop", "coins", "rare", "bossRoll", "dbl"]
assert [_e[4] for _e in V3E.rows("SkyyMobs")] == _SPC
F(msp, "public static final String[] KEY = %s;" % ("new String[] { " + ", ".join(jstr(_k) for _k in _SPK) + " }"))
F(msp, "public static final String READS = %s;" % jstr(V3E.reads_csv("SkyyMobs")))
F(msp, "public static final java.util.concurrent.ConcurrentHashMap C = new java.util.concurrent.ConcurrentHashMap();")
F(msp, "public static final java.util.concurrent.ConcurrentHashMap DONE = new java.util.concurrent.ConcurrentHashMap();")
F(msp, "public static final long VAL_MS = 1000L;")
F(msp, "public static volatile boolean ON = true;")
F(msp, "public static volatile boolean SYS_ON = false;")
F(msp, "public static volatile boolean FAILED = false;")
F(msp, "public static volatile java.util.function.Function ROLLS;")
F(msp, "public static volatile java.util.function.Function PLAYERS;")   # fixer: harness seam (null in the game): UUID -> Boolean in this world
F(msp, "public static final long DONE_MS = 600000L;")   # fixer: one roll per death holds 10 minutes (was 60 s)
F(msp, "public static volatile long PRUNED = 0L;")
F(msp, "public static final java.util.Random RNG = new java.util.Random();")
for _n in ("N_KILLS", "N_DROP", "N_COINS", "N_RARE", "N_BOSS", "N_DBL", "N_GEAR", "N_ITEMS"):
    F(msp, "public static volatile long %s = 0L;" % _n)
M(msp, r"""
public static int rank(java.util.UUID u, String key) {
  try {
    Object f = @PKG@.MobLevel.bridge().get("tree:fn:level");
    if (!(f instanceof java.util.function.Function) || u == null) return 0;
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, key });
    if (!(r instanceof Number)) return 0;
    int n = ((Number) r).intValue();
    return n < 0 ? 0 : (n > 1000 ? 1000 : n);
  } catch (Throwable t) {
    if (!FAILED) { FAILED = true; @PKG@.MobLog.warn("Spoils rows: tree:fn:level failed (logged once; those rows give nothing): " + t); }
    return 0;
  }
}""")
M(msp, r"""
public static double[] vals(java.util.UUID u) {
  long now = System.currentTimeMillis();
  if (u == null) return new double[6];
  Object o = C.get(u);
  if (o instanceof double[] && ((double[]) o)[0] > (double) now) return (double[]) o;
  double[] v = new double[6];
  v[0] = (double) (now + VAL_MS);
  for (int i = 0; i < KEY.length; i++) {
    int rk = rank(u, KEY[i]);
    if (rk <= 0) continue;
    double x = v3per(i) * (double) rk;
    double mx = v3most(i);
    if (x > mx) x = mx;
    if (x > 0.0) v[1 + i] = x;
  }
  if (C.size() > 2048) C.clear();
  C.put(u, v);
  return v;
}""")
# gear never comes from here (SkyyGear's UT / Mythic rates stay as P5 set them): weapons, armour, tools, shields, our own items
M(msp, r"""
public static boolean gear(String id) {
  if (id == null) return true;
  return id.startsWith("Weapon_") || id.startsWith("Armor_") || id.startsWith("Tool_") || id.startsWith("Skyy_") || id.startsWith("Shield")
      || id.indexOf("_Weapon_") >= 0 || id.indexOf("_Armor_") >= 0 || id.indexOf("_Tool_") >= 0 || id.indexOf("_Shield") >= 0;
}""")
# fixer: the item asset says gear / one-of (pure rule + the reader): weapon / armour / tool part, durability, or no stacking
M(msp, r"""
public static boolean uniqOf(Object weapon, Object armor, Object tool, int maxStack, double maxDur) {
  return weapon != null || armor != null || tool != null || maxStack <= 1 || maxDur > 0.0;
}""")
M(msp, r"""
public static boolean uniq(@ISTK@ s) {
  try {
    @ITMA@ it = s.getItem();
    if (it == null) return true;
    return uniqOf(it.getWeapon(), it.getArmor(), it.getTool(), it.getMaxStack(), s.getMaxDurability());
  } catch (Throwable t) { return true; }
}""")
M(msp, r"""
public static java.util.List roll(String dl) {
  if (dl == null || dl.length() == 0) return null;
  java.util.function.Function rf = ROLLS;
  if (rf != null) return (java.util.List) rf.apply(dl);
  @IMOD@ im = @IMOD@.get();
  if (im == null || !im.isEnabled()) return null;
  return im.getRandomItemDrops(dl);
}""")
# a rolled list -> plain { String id, Integer count } pairs without gear (an ItemStack, or a pair from the harness seam); the stacks are
# made new at the spawn (new ItemStack(id, n): never metadata)
M(msp, r"""
public static java.util.ArrayList clean(java.util.List l) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (l == null) return out;
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    String id = null;
    int n = 0;
    if (o instanceof @ISTK@) {
      @ISTK@ s = (@ISTK@) o;
      if (s.isEmpty()) continue;
      id = s.getItemId();
      n = s.getQuantity();
      if (id != null && n > 0 && uniq(s)) { N_GEAR = N_GEAR + 1L; continue; }
    } else if (o instanceof Object[] && ((Object[]) o).length == 2 && ((Object[]) o)[0] instanceof String && ((Object[]) o)[1] instanceof Number) {
      id = (String) ((Object[]) o)[0];
      n = ((Number) ((Object[]) o)[1]).intValue();
    }
    if (id == null || n <= 0) continue;
    if (gear(id)) { N_GEAR = N_GEAR + 1L; continue; }
    out.add(new Object[] { id, Integer.valueOf(n) });
  }
  return out;
}""")
M(msp, "public static String pid(Object p) { return (String) ((Object[]) p)[0]; }")
M(msp, "public static int pn(Object p) { return ((Integer) ((Object[]) p)[1]).intValue(); }")
# Rare Drop: the item of the drop list seen LEAST in 4 rolls (ties: the first seen) - the list's rarest entry, without reading its weights
M(msp, r"""
public static String rarest(String dl) {
  java.util.HashMap n = new java.util.HashMap();
  java.util.ArrayList order = new java.util.ArrayList();
  for (int k = 0; k < 4; k++) {
    java.util.ArrayList l = clean(roll(dl));
    for (int i = 0; i < l.size(); i++) {
      String id = pid(l.get(i));
      Object c = n.get(id);
      if (c == null) order.add(id);
      n.put(id, Integer.valueOf((c == null ? 0 : ((Integer) c).intValue()) + pn(l.get(i))));
    }
  }
  String best = null;
  int bn = Integer.MAX_VALUE;
  for (int i = 0; i < order.size(); i++) {
    String id = (String) order.get(i);
    int c = ((Integer) n.get(id)).intValue();
    if (c < bn) { bn = c; best = id; }
  }
  return best;
}""")
M(msp, r"""
public static java.util.ArrayList extra(java.util.UUID u, String dl, boolean boss, java.util.Random rng) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (!ON || u == null || dl == null || rng == null) return out;
  double[] s = vals(u);
  N_KILLS = N_KILLS + 1L;
  if (s[1] > 0.0 && rng.nextDouble() * 100.0 < s[1]) {
    java.util.ArrayList l = clean(roll(dl));
    if (!l.isEmpty()) { out.add(new Object[] { pid(l.get(rng.nextInt(l.size()))), Integer.valueOf(1) }); N_DROP = N_DROP + 1L; }
  }
  if (s[3] > 0.0 && rng.nextDouble() * 100.0 < s[3]) {
    String id = rarest(dl);
    if (id != null) { out.add(new Object[] { id, Integer.valueOf(1) }); N_RARE = N_RARE + 1L; }
  }
  if (boss && s[4] > 0.0 && rng.nextDouble() * 100.0 < s[4]) {
    java.util.ArrayList l = clean(roll(dl));
    if (!l.isEmpty()) { out.addAll(l); N_BOSS = N_BOSS + 1L; }
  }
  if (s[5] > 0.0 && rng.nextDouble() * 100.0 < s[5]) {
    java.util.ArrayList l = clean(roll(dl));
    if (!l.isEmpty()) { out.addAll(l); N_DBL = N_DBL + 1L; }
  }
  for (int i = 0; i < out.size(); i++) N_ITEMS = N_ITEMS + (long) pn(out.get(i));
  return out;
}""")
# Coin Purse: coins = the mob's level (SkyyCoins coins:fn:add {UUID, Long}); returns the coins asked for (0 = no roll / no SkyyCoins)
M(msp, r"""
public static long coins(java.util.UUID u, int level, java.util.Random rng) {
  if (!ON || u == null || level < 1 || rng == null) return 0L;
  double[] s = vals(u);
  if (!(s[2] > 0.0) || !(rng.nextDouble() * 100.0 < s[2])) return 0L;
  Object f = @PKG@.MobLevel.bridge().get("coins:fn:add");
  if (!(f instanceof java.util.function.Function)) return 0L;
  try { ((java.util.function.Function) f).apply(new Object[] { u, Long.valueOf((long) level) }); } catch (Throwable t) { return 0L; }
  N_COINS = N_COINS + 1L;
  return (long) level;
}""")
# one roll per death (the corpse stays a few ticks, a boss's longer); fixer: entries older than DONE_MS (10 min) go when the map passes
# 512, at most one purge a second
M(msp, r"""
public static boolean first(java.util.UUID mob) {
  if (mob == null) return false;
  long now = System.currentTimeMillis();
  if (DONE.size() > 512 && now - PRUNED > 1000L) {
    PRUNED = now;
    Object[] ks = DONE.keySet().toArray();
    for (int i = 0; i < ks.length; i++) { Object t = DONE.get(ks[i]); if (!(t instanceof Long) || now - ((Long) t).longValue() > DONE_MS) DONE.remove(ks[i]); }
  }
  return DONE.putIfAbsent(mob, Long.valueOf(now)) == null;
}""")
# the killer: the killing blow's Damage$EntitySource (a projectile's = its shooter) - a player in the same store, or a pet's owner
M(msp, r"""
public static java.util.UUID killer(Object dco, @ST@ st, @CB@ cb) {
  try {
    if (!(dco instanceof @DTHC@)) return null;
    @DMG@ d = ((@DTHC@) dco).getDeathInfo();
    if (d == null || !(d.getSource() instanceof @DENT@)) return null;
    @REF@ r = ((@DENT@) d.getSource()).getRef();
    if (r == null || !r.isValid() || r.getStore() != st) return null;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr != null) return pr.getUuid();
    String o = @PKG@.MobCredit.petOwner(cb, r);
    return o == null ? null : java.util.UUID.fromString(o);
  } catch (Throwable t) { return null; }
}""")
# fixer: the owner of the mob's drop as SkyySacks claims it (PickBook.mark: the top damager when in this world, else the killer) - the
# Spoils (ranks, items at the claim spot, Coin Purse) follow it. MobCredit is read, never taken (SkyySacks' take may come first: DEAD).
M(msp, r"""
public static boolean here(java.util.UUID u, @ST@ st) {
  if (u == null) return false;
  java.util.function.Function pf = PLAYERS;
  if (pf != null) return Boolean.TRUE.equals(pf.apply(u));
  if (st == null) return false;
  try {
    @PR@ pr = @UNIV@.get().getPlayer(u);
    @REF@ r = pr == null ? null : pr.getReference();
    return r != null && r.isValid() && r.getStore() == st;
  } catch (Throwable t) { return false; }
}""")
M(msp, r"""
public static String top(String mob) {
  if (mob == null) return null;
  Object o = @PKG@.MobCredit.T.get(mob);
  if (o == null) {
    Object d = @PKG@.MobCredit.DEAD.get(mob);
    if (d instanceof Object[] && System.currentTimeMillis() - ((Long) ((Object[]) d)[0]).longValue() <= @PKG@.MobCredit.DEAD_MS) o = ((Object[]) d)[1];
  }
  if (!(o instanceof @PKG@.MobCredit)) return null;
  Object[] s = ((@PKG@.MobCredit) o).snap();
  return s != null && s[0] instanceof String ? (String) s[0] : null;
}""")
M(msp, r"""
public static java.util.UUID owner(String mob, java.util.UUID killer, @ST@ st) {
  try {
    String t = top(mob);
    if (t != null) {
      java.util.UUID tu = java.util.UUID.fromString(t);
      if (tu.equals(killer) || here(tu, st)) return tu;
    }
  } catch (Throwable x) { }
  return killer;
}""")
M(msp, r"""
public static int spawn(@ST@ st, @CB@ cb, java.util.ArrayList l, @VEC@ at) {
  if (l == null || l.isEmpty() || at == null) return 0;
  java.util.ArrayList is = new java.util.ArrayList();
  for (int i = 0; i < l.size(); i++) is.add(new @ISTK@(pid(l.get(i)), pn(l.get(i))));
  @HLDR@[] hs = @ITC@.generateItemDrops(st, is, at, @RTF@.IDENTITY);
  if (hs == null || hs.length == 0) return 0;
  cb.addEntities(hs, @ADDR@.SPAWN);
  return hs.length;
}""")
M(msp, r"""
public static void reads(boolean on) {
  try {
    java.util.Map b = @PKG@.MobLevel.bridge();
    if (on) b.put("tree:reads:SkyyMobs", READS); else b.remove("tree:reads:SkyyMobs", READS);
  } catch (Throwable t) { }
}""")
M(msp, r"""
public static String text() {
  return "Spoils " + (SYS_ON ? "on" : "OFF (no death system)") + " (kills " + N_KILLS + ", drop " + N_DROP + ", coins " + N_COINS + ", rare " + N_RARE + ", boss " + N_BOSS + ", double " + N_DBL + ", gear skipped " + N_GEAR + ")";
}""")
# SpoilsSys: NPC + DeathComponent, AFTER DropDeathItems (the mob's own loot is out: Role.hasDroppedDeathItems), BEFORE CorpseRemoval
F(mss, "public static Class DDI;")
F(mss, "public static Class CR;")
F(mss, "public java.util.Set deps;")
C(mss, r"""
public SpoilsSys() {
  super();
  this.deps = new java.util.HashSet();
  this.deps.add(new @SDEP@(@ORD@.AFTER, DDI));
  this.deps.add(new @SDEP@(@ORD@.BEFORE, CR));
}""")
M(mss, "public @QRY@ getQuery() { return @QRY@.and(new @QRY@[] { (@QRY@) @NPCE@.getComponentType(), (@QRY@) @DTHC@.getComponentType() }); }")
M(mss, "public java.util.Set getDependencies() { return this.deps; }")
M(mss, "public boolean isParallel(int a, int b) { return false; }")
M(mss, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ st, @CB@ cb) {
  try {
    if (!@PKG@.MobSpoils.ON) return;
    @NPCE@ npc = (@NPCE@) chunk.getComponent(idx, @NPCE@.getComponentType());
    if (npc == null) return;
    @ROLE@ role = npc.getRole();
    if (role == null || !role.hasDroppedDeathItems()) return;
    @UUIDC@ uc = (@UUIDC@) chunk.getComponent(idx, @UUIDC@.getComponentType());
    if (uc == null || uc.getUuid() == null) return;
    java.util.UUID mob = uc.getUuid();
    if (!@PKG@.MobSpoils.first(mob)) return;
    java.util.UUID ku = @PKG@.MobSpoils.owner(mob.toString(), @PKG@.MobSpoils.killer(chunk.getComponent(idx, @DTHC@.getComponentType()), st, cb), st);
    if (ku == null) return;   // fixer: ku = the drop's owner (top damager in this world, else the killer)
    @TC@ tc = (@TC@) chunk.getComponent(idx, @TC@.getComponentType());
    if (tc == null || tc.getPosition() == null) return;
    Object mi = @PKG@.MobLevel.MOBS.get(mob);
    int lvl = mi instanceof @PKG@.MobInfo ? ((@PKG@.MobInfo) mi).level : 0;
    String rw = mi instanceof @PKG@.MobInfo ? @PKG@.MobCfg.rankWord(((@PKG@.MobInfo) mi).rank) : "";
    boolean boss = "boss".equals(rw) || "mini".equals(rw);
    java.util.ArrayList l = @PKG@.MobSpoils.extra(ku, role.getDropListId(), boss, @PKG@.MobSpoils.RNG);
    @PKG@.MobSpoils.coins(ku, lvl, @PKG@.MobSpoils.RNG);
    @VEC@ p = tc.getPosition();
    if (!l.isEmpty()) @PKG@.MobSpoils.spawn(st, cb, l, new @VEC@(p.x, p.y + 1.0, p.z));
  } catch (Throwable t) { @PKG@.MobLog.warnOnce("spoils", "Spoils rows (extra kill loot) failed: " + t); }
}""")

'''
P.rep('''# ================================================================= 0.1.7 mob:fn:credit (bridge, any thread, never throws)''',
      SPOILS + '''# ================================================================= 0.1.7 mob:fn:credit (bridge, any thread, never throws)''')

# ---------- the system, the numbers file, tree:reads:SkyyMobs
P.rep('''  catch (Throwable t7) { CREDIT_ON = false; @PKG@.MobLog.warn("the kill credit could not be registered (" + t7 + ") - this start a mob's whole drop goes to its killer (no top-damager split)"); }
}"""''', '''  catch (Throwable t7) { CREDIT_ON = false; @PKG@.MobLog.warn("the kill credit could not be registered (" + t7 + ") - this start a mob's whole drop goes to its killer (no top-damager split)"); }
  // 0.1.15 (Balance P8b): the Spoils rows - ordered after the engine's own death drop; no ordered system = no spoils (never unordered)
  @PKG@.SpoilsSys.DDI = cls("com.hypixel.hytale.server.npc.systems.NPCDamageSystems$DropDeathItems");
  @PKG@.SpoilsSys.CR = cls("com.hypixel.hytale.server.core.modules.entity.damage.DeathSystems$CorpseRemoval");
  if (@PKG@.SpoilsSys.DDI == null || @PKG@.SpoilsSys.CR == null) @PKG@.MobLog.warn("NPCDamageSystems$DropDeathItems / DeathSystems$CorpseRemoval not found - the Combat tree's Spoils rows give nothing this start");
  else {
    try { getEntityStoreRegistry().registerSystem(new @PKG@.SpoilsSys()); @PKG@.MobSpoils.SYS_ON = true; }
    catch (Throwable t8) { @PKG@.MobSpoils.SYS_ON = false; @PKG@.MobLog.warn("the Spoils death system could not be ordered after DropDeathItems (" + t8 + ") - the Combat tree's Spoils rows give nothing this start"); }
  }
}"""''')
P.rep('''  @PKG@.MobCfg.load();
  @PKG@.MobCfg.ON_HEALTH = new @PKG@.MobRefresh(null);''', '''  @PKG@.MobCfg.load();
  String spt = @PKG@.MobSpoils.loadV3(dir);   // 0.1.15 (Balance P8b): the Spoils rows' numbers (trees.properties, seeded when missing)
  @PKG@.MobCfg.ON_HEALTH = new @PKG@.MobRefresh(null);''')
# fixer 2: publish tree:reads:SkyyMobs only once systems() has registered SpoilsSys (no death system = SkyyTrees keeps the rows "coming soon")
P.rep('''  systems();
  getCommandRegistry().registerCommand(new @PKG@.MobsCmd());''', '''  systems();
  @PKG@.MobSpoils.reads(@PKG@.MobSpoils.SYS_ON);   // 0.1.15: tree:reads:SkyyMobs = the 5 Spoils keys, only while SpoilsSys is registered (SkyyTrees sells them only while listed)
  getCommandRegistry().registerCommand(new @PKG@.MobsCmd());''')
P.rep('''+ "; mob:fn:setLevel; " + @PKG@.MobCfg.bossText() + "; /mobs; settings in Server Setup > Mobs; data in " + dir''',
      '''+ "; mob:fn:setLevel; " + @PKG@.MobCfg.bossText() + "; " + @PKG@.MobSpoils.text() + " " + spt + "; /mobs; settings in Server Setup > Mobs; data in " + dir''')
P.rep('''  try { @PKG@.MobLevel.bridge().remove("mob:fn:boss"); } catch (Throwable t) { }   // 0.1.10''',
      '''  try { @PKG@.MobLevel.bridge().remove("mob:fn:boss"); } catch (Throwable t) { }   // 0.1.10
  try { @PKG@.MobSpoils.reads(false); @PKG@.MobSpoils.C.clear(); @PKG@.MobSpoils.DONE.clear(); @PKG@.MobSpoils.PLAYERS = null; } catch (Throwable t) { }   // 0.1.15''')

assert P.s.count("registerSystem(") == SYS0 + 1 and P.s.count("registerCommand(") == CMD0 and P.s.count("makeClass(") == CLS0 + 2
P.finish()
