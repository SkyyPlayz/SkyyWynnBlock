"""Derive SkyyCollections/build_skyycollections_0.2.2.py from 0.2.1 (0.2.1 is left untouched; line endings preserved).
Regenerate after editing this file: delete SkyyCollections/build_skyycollections_0.2.2.py, run python tools/coll_0_2_2_patch.py.
0.2.2 = in-game server setup + player Settings (research/Server-Setup-Spec.md 4.11 + section 7, research/Settings-Spec.md 3.3), nothing
else. Default behaviour is identical until an admin changes a value.
  1. Admin config kit (tools/skyycfg.py, tools/CONFIG-CONTRACT.md): config:def:SkyyCollections + config:fn:SkyyCollections are
     published at the END of setup() (CfgPub.start, after CollReg.loadAll). Three files, every row bound reload@<file>:<key> (file names
     and keys unchanged); RELOAD = CollKit.reloadAll = exactly what /collections reload always did (loadAll, recipe check, coll:list,
     leaderboard cache, republish), run by the kit on the scheduler after it wrote a changed file. Categories curves, rewards,
     bypass (Coin unlocks), rules, registry. The mod's own parsers' rules are mirrored in check= hooks (CollKit.check*), so a typed
     value the loader would silently replace by its default is refused instead.
     Registry: the rewards.properties lines are the table 'rewards' (empty prefix = the whole file; entry Wheat.3, one text column,
     check= validates the collection id + tier, every recipe:/coins:/xp: token, and refuses when the file already holds a second line
     for that entry - the mod concatenates duplicate lines, the kit would give them all the same value). The 'coll' registry table of
     spec 4.11 is NOT built: a coll.<Id> line has 7 '|'-separated fields and item lists up to ~600 characters, while a kit table has
     1-3 columns, splits typed values on '|' and caps a text column at 200 characters (kit limit, reported). Instead an action row
     'Re-read files' runs the full reload from the menu, so hand edits of coll. lines can be applied in game (the kit's own Reload
     only re-applies BOUND keys).
     /collections reload keeps its reply and adds the kit's reload op (hand edits of bound keys are logged via=file, reload routines
     run after pending in-game writes); the mod's own reload runs FIRST so a stale disk read can never win over a pending kit write.
     shutdown() flushes the kit (CfgPub.shutdown) before the bridge keys are removed.
  2. Player Settings (Settings-Spec 1.3, 3.3): CollUtil.notifyOn / regSetting; registered in setup(): coll.newCollection,
     coll.tierUp (collections), rewards.late (coins, the SkyySkills label/help). Only the chat lines are gated: the new-collection line,
     the COLLECTION UP block + recipe count, the "rewards are owed" line and the "Paid for earlier collection tiers" line.
     Counting, settle, publish and mark stay unconditional.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyCollections", "build_skyycollections_0.2.1.py")
dst = os.path.join(ROOT, "SkyyCollections", "build_skyycollections_0.2.2.py")
assert not os.path.exists(dst), "refusing to overwrite " + dst
raw = open(src, encoding="utf8", newline="").read()
CRLF = "\r\n" in raw
s = raw.replace("\r\n", "\n")

def rep(old, new, count=1):
    global s
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:80])
    s = s.replace(old, new)

# ---------------- docstring + version ----------------
rep('''"""SkyyCollections 0.2.1 - build script (derived from 0.2 by tools/coll_0_2_1_patch.py - edit the patch, not this file; 0.2 was
written fresh: the 0.1.5 per-profile code, the coll:recipes bridge contract and the page command rules are carried over, everything
else follows research/Collections-Spec.md).
''', '''"""SkyyCollections 0.2.2 - build script (derived from 0.2.1 by tools/coll_0_2_2_patch.py - edit the patch, not this file; 0.2.1 was
derived from 0.2 by tools/coll_0_2_1_patch.py; 0.2 was written fresh: the 0.1.5 per-profile code, the coll:recipes bridge contract
and the page command rules are carried over, everything else follows research/Collections-Spec.md).

0.2.2: in-game server setup + player Settings (research/Server-Setup-Spec.md 4.11, research/Settings-Spec.md 3.3), nothing else.
  - Admin config kit (tools/skyycfg.py): SkyWynn Menu -> Server Setup -> Collections (/modconfig). Curves, tier rewards, coin unlocks,
    rules and the rewards.properties table, every row bound to its existing file key (reload:), RELOAD = CollKit.reloadAll (what
    /collections reload always did). Typed values are checked with the mod's own parser rules (CollKit.check*). An action
    'Re-read files' applies hand edits of the coll. lines from the menu. /collections reload also runs the kit's reload (logged).
  - Player Settings (SkyyMenu /settings): coll.newCollection, coll.tierUp, rewards.late gate only the chat lines.
''')
rep('''Run:   python build_skyycollections_0.2.1.py          -> SkyyCollections/SkyyCollections-0.2.1.jar''',
    '''Run:   python build_skyycollections_0.2.2.py          -> SkyyCollections/SkyyCollections-0.2.2.jar''')
rep('''VERSION = "0.2.1"
''', '''VERSION = "0.2.2"
''')
# the build script already has a CFG list (config.properties lines), so the kit module gets another name
rep('''import skyybuild as B
''', '''import skyybuild as B
import skyycfg as SCFG      # 0.2.2: the admin config kit (tools/CONFIG-CONTRACT.md)
''')
# new installs only (an existing config.properties is never rewritten); comments do not change behaviour
rep('''    "# SkyyCollections 0.2 settings. /collections reload re-reads this file, collections.properties and rewards.properties.",
''', '''    "# SkyyCollections 0.2 settings. /collections reload re-reads this file, collections.properties and rewards.properties.",
    "# Also editable in game: SkyWynn Menu -> Server Setup -> Collections (/modconfig). Changes made there are written back here.",
''')

# ---------------- classes: CollKit (hooks + reload), written with the rest ----------------
rep('''nmc = K("CollNameCmd", "APC"); cmd = K("CollCmd", "APC"); sav = K("CollSaver"); pl = K("SkyyCollectionsPlugin", "JP")
ALL = (util, cio, rd, reg, drp, mig, cdat, sto, rew, unl, cred, byp, plc, pend, gctx, btk, ptk, pltk, ktk, atk, rtk, bsy, usy, psy, plsy, ksy,
       tcmp, top, fnc, page, ulc, rlc, gvc, tpc, nmc, cmd, sav, pl)''',
    '''nmc = K("CollNameCmd", "APC"); cmd = K("CollCmd", "APC"); sav = K("CollSaver"); pl = K("SkyyCollectionsPlugin", "JP")
ckit = K("CollKit")   # 0.2.2: admin config kit hooks + the shared reload
ALL = (util, cio, rd, reg, drp, mig, cdat, sto, rew, unl, cred, byp, plc, pend, gctx, btk, ptk, pltk, ktk, atk, rtk, bsy, usy, psy, plsy, ksy,
       tcmp, top, fnc, page, ckit, ulc, rlc, gvc, tpc, nmc, cmd, sav, pl)''')

# ---------------- 2. player Settings helpers (CollUtil has the creating bridge()) ----------------
rep('''# inline UI text: no quotes, braces, colons, semicolons, commas (the SkyySacks rule); dynamic text uses b.set instead
''', r'''# 0.2.2: player Settings registry (research/Settings-Spec.md 1.3; SkyyMenu 0.2+). No SkyyMenu = no answer = today's behaviour (on).
M(util, r"""
public static boolean notifyOn(java.util.UUID u, String key) {
  if (u == null || key == null) return true;
  try {
    Object f = bridge().get("settings:fn:get");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(new Object[] { u, key });
      if (r instanceof Boolean) return ((Boolean) r).booleanValue();
    }
  } catch (Throwable t) { }
  return true;
}""")
M(util, r"""
public static void regSetting(String key, String label, String cat, boolean def, String help) {
  try {
    Object[] a = new Object[] { "SkyyCollections", key, label, cat, Boolean.valueOf(def), help };
    java.util.Map br = bridge();
    br.put("settings:def:" + key, a);
    Object f = br.get("settings:fn:register");
    if (f instanceof java.util.function.Function) ((java.util.function.Function) f).apply(a);
  } catch (Throwable t) { }
}""")
# inline UI text: no quotes, braces, colons, semicolons, commas (the SkyySacks rule); dynamic text uses b.set instead
''')

# ---------------- 2. gates (only the sendMessage calls; payments, markers, publish run as before) ----------------
rep('''  mark(key, d, R);
  if ((coins > 0L || xp > 0L) && pr != null && pr.isValid()) {''',
    '''  mark(key, d, R);
  if ((coins > 0L || xp > 0L) && pr != null && pr.isValid() && @PKG@.CollUtil.notifyOn(u, "rewards.late")) {''')
rep('''    if (on && r[0] <= 0L && r[1] > 0L) pr.sendMessage(@MSG@.raw("New collection: " + R.name[c] + "!   /collections").color("#7fdcff"));''',
    '''    if (on && r[0] <= 0L && r[1] > 0L && @PKG@.CollUtil.notifyOn(u, "coll.newCollection")) pr.sendMessage(@MSG@.raw("New collection: " + R.name[c] + "!   /collections").color("#7fdcff"));''')
rep('''    if (!on) return;
    announce(pr, R, c, ot + 1, nt);
    if (now > before) pr.sendMessage(@MSG@.raw("   " + (now - before) + " new recipe(s) in /craft - Collections tab").color("#c8f0a0"));
    if (paid[2] != 0L) pr.sendMessage(''',
    '''    if (!on) return;
    boolean tierOn = @PKG@.CollUtil.notifyOn(u, "coll.tierUp");
    if (tierOn) announce(pr, R, c, ot + 1, nt);
    if (tierOn && now > before) pr.sendMessage(@MSG@.raw("   " + (now - before) + " new recipe(s) in /craft - Collections tab").color("#c8f0a0"));
    if (paid[2] != 0L && @PKG@.CollUtil.notifyOn(u, "rewards.late")) pr.sendMessage(''')

# ---------------- 1. CollKit + the kit schema (before the commands: the reload command calls CollKit and CfgFn) ----------------
KIT_BLOCK = r'''# ================= 0.2.2: the admin config kit (research/Server-Setup-Spec.md 4.11, tools/CONFIG-CONTRACT.md) =================
# emit() first: CollKit.kitReload and the reload command call CfgFn; the hooks below are found by reflection (checked at kit.write)
# the schema (spec 4.11): every row keeps its file key; the file is the truth, the mod's loaders read it (reload: bindings)
def _csv(xs):
    return ",".join(str(x) for x in xs)
KIT_CATS = [("curves", "Curves"), ("rewards", "Rewards"), ("bypass", "Coin unlocks"), ("rules", "Rules"), ("registry", "Registry")]
KIT_ROWS = []  # (key, label, cat, type, default, min, max, opts, unit, flags, help, bind)
for _k, _n in (("B", "Bulk"), ("S", "Standard"), ("R", "Rare"), ("E", "Elite")):
    KIT_ROWS.append(("curve." + _k, _n + " curve", "curves", "text", _csv(CURVES[_k]), "1", "400", "", "", "live,danger",
                     "Items for tier I, II, ... of %s collections (1-20 rising numbers). Moves every player's tiers." % _n,
                     "reload@collections.properties:curve.%s;check=CollKit.checkCurve" % _k))
KIT_ROWS += [
    ("tier.coins", "Coins per tier", "rewards", "text", _csv(TIER_COINS), "1", "400", "", "", "live,danger",
     "Coins paid at tier I, II, III, ... (the last number repeats for higher tiers).",
     "reload@collections.properties:tier.coins;check=CollKit.checkTierList"),
    ("tier.xp", "Skill XP per tier", "rewards", "text", _csv(TIER_XP), "1", "400", "", "", "live,danger",
     "Farming, Mining, Foraging: skill XP at tier I, II, ... (the last tier pays Last tier XP instead).",
     "reload@collections.properties:tier.xp;check=CollKit.checkTierList"),
    ("tier.lastXp", "Last tier XP", "rewards", "int", "25000", "0", "1000000000", "step=1000", "", "live",
     "Skill XP the LAST tier of a Farming, Mining or Foraging collection pays.",
     "reload@collections.properties:tier.lastXp"),
    ("combat.coinMultiplier", "Combat coin multiplier", "rewards", "dec", "2", "0", "100", "", "x", "live",
     "Combat collections pay no skill XP: their coins x this on tiers III, V, VII and the last one.",
     "reload@collections.properties:combat.coinMultiplier"),
    ("bypass.enabled", "Coin unlocks", "bypass", "bool", "true", "", "", "", "", "live,part,danger",
     "Off: the Buy button says coin unlocks are turned off. Tiers already bought stay unlocked.",
     "reload@config.properties:bypass.enabled"),
    ("bypass.multiplier", "Price multiplier", "bypass", "dec", "5", "0", "1000", "", "x", "live",
     "Price = missing items x unit price x this (never below the minimum price).",
     "reload@config.properties:bypass.multiplier"),
    ("bypass.minPrice", "Minimum price", "bypass", "int", "500", "0", "1000000000000", "step=100", "coins", "live",
     "The lowest price of one coin unlock.",
     "reload@config.properties:bypass.minPrice"),
    ("bypass.fallback", "Fallback unit prices", "bypass", "text", "2,5,25,100", "1", "200", "", "", "live,danger",
     "Coins per missing item when the Bazaar has no price: Bulk,Standard,Rare,Elite.",
     "reload@config.properties:bypass.fallback;check=CollKit.checkFallback"),
    ("bypass.walls", "Highest tier coins can buy", "bypass", "text", "5,4,3,0", "1", "200", "", "", "live,danger",
     "Per curve Bulk,Standard,Rare,Elite (0 = never). Higher tiers must be gathered.",
     "reload@config.properties:bypass.walls;check=CollKit.checkWalls"),
    ("auto", "Auto recipe rule (0.1)", "rules", "bool", "false", "", "", "", "", "live,danger",
     "On: a recipe unlocks once every started input reaches tier I (with item counts: far too many).",
     "reload@config.properties:auto"),
    ("exclude.benches", "Benches never unlocked", "rules", "text", "Alchemybench,Cookingbench,Furnace,Tannery,Campfire,Salvagebench", "", "400",
     "", "", "live", "Recipes of these benches stay at their bench (comma separated bench ids).",
     "reload@config.properties:exclude.benches;check=CollKit.checkBenches"),
    ("bridge.add.felled", "Count felled logs", "rules", "bool", "true", "", "", "", "", "live",
     "Logs that fall when a player cuts a tree count (SkyySkills 0.4.2+).",
     "reload@config.properties:bridge.add.felled"),
    ("cap.perCredit", "Most items per gather", "rules", "int", "256", "0", "1000000000", "", "", "live,adv",
     "Anti-exploit: most items one gather event may add (0 = no cap).",
     "reload@config.properties:cap.perCredit"),
    ("cap.perMinute", "Most items per minute", "rules", "int", "20000", "0", "1000000000", "", "", "live,adv",
     "Anti-exploit, per player per minute (0 = no cap). Admin /collections give is exempt.",
     "reload@config.properties:cap.perMinute"),
    ("bridge.add.sources", "Sources other mods may credit", "rules", "text", "skills:double,skills:felled", "", "400", "", "", "live,adv",
     "coll:fn:add sources (skills:double = double drops). Count felled logs above adds skills:felled.",
     "reload@config.properties:bridge.add.sources;check=CollKit.checkSources"),
    ("migrate", "Old 0.1 counts files", "rules", "choice", "convert", "", "", "convert|Convert,reset|Reset", "", "new,danger,adv",
     "A 0.1 counts file read from now on: convert where exact, or reset (archived, starts at 0).",
     "reload@config.properties:migrate"),
    ("reload.files", "Re-read the collection files", "registry", "action", "", "", "", "Re-read files", "", "live",
     "Same as /collections reload: applies hand edits of collections.properties (the coll. lines) now.",
     "action:CollKit.reloadAction"),
    ("rewards", "Tier rewards (rewards.properties)", "registry", "table", "", "", "", "text;type;Rewards", "", "live,adv",
     "Entry Wheat.3 = recipe:<RecipeId>,coins:<n>,xp:<Skill>:<n> - added to that tier's coins and XP.",
     "reload@rewards.properties:;check=CollKit.checkReward"),
]
kit = SCFG.emit(pool, PKG, MOD="SkyyCollections", TITLE="Collections", VERSION=VERSION, NODE="skyycollections.admin", CATS=KIT_CATS,
                ROWS=KIT_ROWS, FILES=["Skyy_SkyyCollections/config.properties", "Skyy_SkyyCollections/collections.properties",
                                      "Skyy_SkyyCollections/rewards.properties"],
                NOTE="The collection list (coll. lines in collections.properties): edit the file, then Re-read files.",
                RELOAD="CollKit.reloadAll", KEEP=20, ITEMS=ITEM_IDS,
                DEFAULTS={"config.properties": "\n".join(CFG) + "\n", "collections.properties": "\n".join(REG_TXT) + "\n",
                          "rewards.properties": "\n".join(RW) + "\n"})

# ================= 0.2.2: CollKit = the admin config kit's hooks (research/Server-Setup-Spec.md 4.11, tools/CONFIG-CONTRACT.md) =================
# reloadNow = exactly what /collections reload always did. It is also the kit's RELOAD routine (reloadAll): the kit runs it on the
# scheduler after it wrote a changed file, outside every kit lock. No world access - the same calls CollSaver already makes there.
M(ckit, r"""
public static void clearTop() {
  synchronized (@PKG@.CollTop.class) { @PKG@.CollTop.CACHE.clear(); }
}""")
M(ckit, r"""
public static synchronized String[] reloadNow() {
  String a = @PKG@.CollReg.loadAll();
  String v = @PKG@.CollReg.validate();
  @PKG@.CollUtil.bridge().put("coll:list", @PKG@.CollReg.listString());
  clearTop();
  @PKG@.CollUnlocks.republishAll();
  return new String[] { a, v };
}""")
M(ckit, r"""
public static void reloadAll() {
  try {
    String[] r = reloadNow();
    @PKG@.CollUtil.info("settings changed - reloaded: " + r[1] + "; " + r[0]);
  } catch (Throwable t) { @PKG@.CollUtil.warn("reload after a settings change failed: " + t); }
}""")
# the kit's reload op: hand edits of BOUND keys are logged via=file and their reload routine runs after the pending in-game writes
M(ckit, r"""
public static String kitReload(java.util.UUID who, String name, String via) {
  try {
    Object o = new @PKG@.CfgFn().apply(new Object[] { "reload", who, name, via });
    if (o instanceof Object[] && ((Object[]) o).length > 2) return String.valueOf(((Object[]) o)[2]);
  } catch (Throwable t) { @PKG@.CollUtil.warn("config kit reload failed: " + t); }
  return "the config kit did not answer";
}""")
# /collections reload and the 'Re-read files' action. The mod's own reload runs FIRST: if it read the disk before a pending kit write,
# that write's reload routine runs afterwards and wins (the other order could let a stale read overwrite a fresh one).
M(ckit, r"""
public static String fullReload(java.util.UUID who, String name, String via) {
  String[] r = reloadNow();
  String k = kitReload(who, name, via);
  return "reloaded: " + r[1] + "; " + r[0] + "; config: " + k;
}""")
# the kit runs an action only for an admin, or for who = null with via console (its only null-who path), so null = console here
M(ckit, r"""
public static Object[] reloadAction(java.util.UUID who, String name) {
  try {
    String via = "menu";
    if (who == null) via = "console";
    return new Object[] { "ok", null, @PKG@.CollUtil.clip(fullReload(who, name, via), 200) };
  } catch (Throwable t) {
    @PKG@.CollUtil.warn("Re-read files failed: " + t);
    return new Object[] { "error", null, "Re-reading the files failed - see the server log." };
  }
}""")
# check= hooks: null = fine, text = refused with that reason, "?text" = ask first. They mirror the mod's own loaders, which silently
# fall back to the default on a bad value - typed in game such a value is refused instead (spec 1.4.2: reject, never clamp)
M(ckit, r"""
public static long[] nums(String v) {
  String[] p = @PKG@.CollUtil.csv(v);
  long[] out = new long[p.length];
  for (int i = 0; i < p.length; i++) {
    try { out[i] = Long.parseLong(p[i]); } catch (Throwable t) { return null; }
  }
  return out;
}""")
M(ckit, r"""
public static String checkCurve(String key, String value) {
  long[] a = nums(value);
  if (a == null || a.length < 1 || a.length > 20 || !@PKG@.CollReg.ascending(a)) return "Must be 1 to 20 whole numbers above 0, each higher than the one before (like 50,100,250).";
  return null;
}""")
M(ckit, r"""
public static String checkTierList(String key, String value) {
  long[] a = nums(value);
  if (a == null || a.length < 1 || a.length > 20) return "Must be 1 to 20 whole numbers separated by commas, one per tier (I, II, III, ...).";
  for (int i = 0; i < a.length; i++) if (a[i] < 0L) return "No negative numbers.";
  return null;
}""")
M(ckit, r"""
public static String checkFallback(String key, String value) {
  long[] a = nums(value);
  if (a == null || a.length != 4) return "Must be 4 whole numbers: Bulk,Standard,Rare,Elite (like 2,5,25,100).";
  for (int i = 0; i < 4; i++) if (a[i] < 0L) return "No negative numbers.";
  return null;
}""")
M(ckit, r"""
public static String checkWalls(String key, String value) {
  long[] a = nums(value);
  if (a == null || a.length != 4) return "Must be 4 tiers: Bulk,Standard,Rare,Elite (like 5,4,3,0; 0 = never).";
  for (int i = 0; i < 4; i++) if (a[i] < 0L || a[i] > 20L) return "Each tier must be 0 to 20 (0 = coins never unlock that curve).";
  return null;
}""")
M(ckit, r"""
public static String idList(String value, String extra, String what) {
  String[] p = @PKG@.CollUtil.csv(value);
  if (p.length > 50) return "At most 50 " + what + "s.";
  for (int i = 0; i < p.length; i++) {
    String s = p[i];
    for (int k = 0; k < s.length(); k++) {
      char c = s.charAt(k);
      if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || extra.indexOf(c) >= 0)) return "Not a " + what + ": " + s + " (comma separated list).";
    }
  }
  return null;
}""")
M(ckit, r"""
public static String checkBenches(String key, String value) {
  return idList(value, "_-", "bench id");
}""")
M(ckit, r"""
public static String checkSources(String key, String value) {
  return idList(value, "_-:.", "source id");
}""")
# how the mod keys a rewards line: lower-case collection id + "." + the tier as a number (Wheat.03 = wheat.3)
M(ckit, r"""
public static String rewardKey(String k) {
  int dot = k.lastIndexOf('.');
  if (dot <= 0) return k.trim().toLowerCase();
  try { return k.substring(0, dot).trim().toLowerCase() + "." + Integer.parseInt(k.substring(dot + 1).trim()); } catch (Throwable t) { return k.trim().toLowerCase(); }
}""")
# { lines whose key is exactly e, lines the mod reads as the same entry } in rewards.properties on disk (the mod's line rules)
M(ckit, r"""
public static int[] rewardLines(String e) {
  int[] n = new int[2];
  try {
    java.nio.file.Path f = @PKG@.CollReg.BASE.resolve("rewards.properties");
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return n;
    java.util.List lines = @PKG@.CollIO.readLines(f);
    String want = rewardKey(e);
    for (int i = 0; i < lines.size(); i++) {
      String ln = String.valueOf(lines.get(i)).trim();
      if (ln.length() == 0 || ln.startsWith("#")) continue;
      int eq = ln.indexOf('=');
      if (eq <= 0) continue;
      String k = ln.substring(0, eq).trim();
      if (k.equals(e)) n[0] = n[0] + 1;
      if (rewardKey(k).equals(want)) n[1] = n[1] + 1;
    }
  } catch (Throwable t) { }
  return n;
}""")
M(ckit, r"""
public static String rewardToken(String s) {
  if (s.startsWith("recipe:")) {
    String rid = s.substring(7).trim();
    if (rid.length() == 0) return "recipe: needs a recipe id, like recipe:Tool_Hoe_Copper_Recipe_Generated_0.";
    if (!@PKG@.CollMigrate.ready()) return "?Recipes are not loaded yet (server still starting), so " + rid + " cannot be checked. Save it unchecked?";
    @CRR@ rr = null;
    try { rr = (@CRR@) @CRR@.getAssetMap().getAsset(rid); } catch (Throwable t) { }
    if (rr == null) return "Unknown recipe id: " + rid + " (recipe ids end in _Recipe_Generated_0).";
    if (@PKG@.CollReg.excluded(rr)) return rid + " is made at a bench on the Rules list Benches never unlocked - it would never unlock.";
    return null;
  }
  if (s.startsWith("coins:")) {
    try { if (Long.parseLong(s.substring(6).trim()) >= 0L) return null; } catch (Throwable t) { }
    return "coins: needs a whole number from 0 up, like coins:500.";
  }
  if (s.startsWith("xp:")) {
    String[] p = s.split(":");
    boolean good = p.length == 3 && p[1].trim().length() > 0;
    if (good) { try { good = Long.parseLong(p[2].trim()) >= 0L; } catch (Throwable t) { good = false; } }
    if (good) {
      String nm = p[1].trim();
      for (int k = 0; k < nm.length(); k++) { char c = nm.charAt(k); if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z'))) good = false; }
    }
    if (!good) return "xp: needs a skill name (letters only) and a whole number, like xp:Mining:500.";
    String sk = "," + p[1].trim() + ",";
    if (",Mining,Foraging,Farming,Alchemy,Smithing,Cooking,Exploration,".indexOf(sk) < 0) return "?" + p[1].trim() + " is not a skill SkyySkills grants by default (Mining, Foraging, Farming, Alchemy, Smithing, Cooking) - refused XP stays owed. Save anyway?";
    return null;
  }
  return "Unknown reward " + s + " - use recipe:<id>, coins:<n> or xp:<Skill>:<n>.";
}""")
# table rewards: key = rewards[<entry>], value = the line's value or null for a removal (always allowed)
M(ckit, r"""
public static String checkReward(String key, String value) {
  if (value == null) return null;
  int a = key.indexOf('[');
  int b = key.lastIndexOf(']');
  if (a < 0 || b <= a) return null;
  String e = key.substring(a + 1, b);
  String form = "An entry is <CollectionId>.<tier>, like Wheat.3.";
  int dot = e.lastIndexOf('.');
  if (dot <= 0 || dot >= e.length() - 1) return form;
  String id = e.substring(0, dot);
  int t = 0;
  try { t = Integer.parseInt(e.substring(dot + 1)); } catch (Throwable x) { return form; }
  int mx = 20;
  String canon = id + "." + t;
  @PKG@.RegData R = @PKG@.CollReg.D;
  if (R != null) {
    Object ci = R.byId.get(id.toLowerCase());
    if (!(ci instanceof Integer)) return "No collection has the id " + id + " (the coll. names in collections.properties, like Wheat or OakLog).";
    int c = ((Integer) ci).intValue();
    mx = @PKG@.CollReg.maxTier(R, c);
    canon = R.id[c] + "." + t;
  }
  if (t < 1 || t > mx) return id + " has tiers 1 to " + mx + ".";
  if (!canon.equals(e)) return "Write it as " + canon + ".";
  int[] n = rewardLines(canon);
  if (n[0] > 1 || n[1] > n[0]) return "rewards.properties has more than one line for " + canon + " - merge them into one line by hand, then Re-read files.";
  String[] toks = @PKG@.CollUtil.csv(value);
  String ask = null;
  for (int i = 0; i < toks.length; i++) {
    String r = rewardToken(toks[i]);
    if (r == null) continue;
    if (!r.startsWith("?")) return r;
    if (ask == null) ask = r;
  }
  return ask;
}""")
'''
rep('''# ================= commands (HANDOFF command rules: Adventurer group on player commands, admin = requirePermission + no groups) =================
''', KIT_BLOCK + '''
# ================= commands (HANDOFF command rules: Adventurer group on player commands, admin = requirePermission + no groups) =================
''')

# ---------------- /collections reload: same reply, plus the kit's reload op (logged, versioned) ----------------
rep('''    String a = @PKG@.CollReg.loadAll();
    String v = @PKG@.CollReg.validate();
    @PKG@.CollUtil.bridge().put("coll:list", @PKG@.CollReg.listString());
    @PKG@.CollTop.CACHE.clear();
    @PKG@.CollUnlocks.republishAll();
    pr.sendMessage(@MSG@.raw("[Collections] reloaded: " + v + "; " + a));''',
    '''    pr.sendMessage(@MSG@.raw("[Collections] " + @PKG@.CollKit.fullReload(pr.getUuid(), pr.getUsername(), "command")));''')

# ---------------- setup(): register the switches, then publish config:def / config:fn LAST (after loadAll) ----------------
rep('''  this.saver = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.CollSaver(), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyCollections] 0.2.1 ready - item collections, /collections; migration + recipe check run at start; " + s);''',
    '''  this.saver = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.CollSaver(), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);
  @PKG@.CollUtil.regSetting("coll.newCollection", "New collections", "collections", true, "New collection: Copper Ore! - the first item of a kind you gather");
  @PKG@.CollUtil.regSetting("coll.tierUp", "Collection tier-ups", "collections", true, "COLLECTION UP with its rewards and the recipes it unlocked");
  @PKG@.CollUtil.regSetting("rewards.late", "Late reward payouts", "coins", true, "Coins and XP paid later because another mod was not ready");
  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyCollections] 0.2.2 ready - item collections, /collections, admin settings in SkyWynn Menu -> Server Setup (/modconfig); migration + recipe check run at start; " + s);''')

# ---------------- shutdown(): pending kit writes (and their reload routine) before the bridge keys go ----------------
rep('''  try { if (this.saver != null) this.saver.cancel(false); } catch (Throwable t) { }
  try { @PKG@.CollStore.flushDirty(); } catch (Throwable t) { }''',
    '''  try { if (this.saver != null) this.saver.cancel(false); } catch (Throwable t) { }
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }
  try { @PKG@.CollStore.flushDirty(); } catch (Throwable t) { }''')

# ---------------- write the kit classes (deferred hook checks first) ----------------
rep('''for c in ALL:
    c.writeFile(OUT)
print("classes written")
''', '''for c in ALL:
    c.writeFile(OUT)
kit.write(OUT)   # 0.2.2: deferred checks (CollKit hooks exist with the right signatures), then the 7 kit classes
print("classes written:", len(ALL) + len(kit.classes), "(%d kit)" % len(kit.classes))
''')

out = s.replace("\n", "\r\n") if CRLF else s
open(dst, "w", encoding="utf8", newline="").write(out)
print("wrote", dst, "(CRLF)" if CRLF else "(LF)")
