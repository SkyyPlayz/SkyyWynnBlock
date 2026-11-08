"""Derive SkyyShards/build_skyyshards_0.4.20.py from the GENERATED SkyyShards 0.4.19 (build_skyyshards_0.4.19.py = the tools/deploy_set.py SET
pin, made by tools/shards_0_4_19_patch.py - edit the patch, never the generated file). Every anchor is asserted once; at the end every change
is undone on a copy and compared with 0.4.19 (tools/soundpass_gen.Patch). Line endings kept.
Run:   python tools/shards_0_4_20_patch.py   then   python SkyyShards/build_skyyshards_0.4.20.py   (never --deploy)
Check: python SkyyShards/test_skyyshards_0.4.20.py

0.4.20 (2026-11-08) = SKYBLOCK STORAGE + TRUE COMPRESSION (round sh020; Skyy 2026-11-08: "add auto compactor to these as an upgrade or a modifer if it isnt
  already, and set the storage cap much lower with upgrade options, skyblock style, so you have to work on upgrading to get a ton of space, or get the
  auto compactor. (i shouldnt be aboe to get 100k of anything untill lateeee game." + popups "1k / 3k / 8k / 20k / 50k" and "True compression" +
  "a lot of my stats leveld way faster than my class" + popup "Shards pay 20% of normal XP" + "on the mining shard, instead of using ore to upgrade, use ingots").
  1. STORAGE I..V = 10 / 30 / 80 / 200 / 500 stacks of 100 per island = 1,000 / 3,000 / 8,000 / 20,000 / 50,000 items (were 243 / 875 / 1993 / 3573 / 5611
     stacks). Island size / upgrade multiplier, the +300 of a Storage modifier and the costs stay. Stock above a new cap is never touched: settle's full
     branch only stops production until it is collected or sold down.
  2. AUTO-COMPACTOR = TRUE COMPRESSION. On a shard with Compactor I / II, wherever the island's item has an Enchanted form NOW (ShMath.compForm: the same
     rule Collect used: Auto-Smelt Pole -> SMELTE, else ENCH; a Mining island without a pole has none), settle turns every 100 base items into 1 Enchanted
     item, also the stock already stored the first time it settles; a leftover under 100 stays as base items. One Enchanted item = 1 space: the island's
     limit is cap x 100 in base items (ShMath.limOf / usedOf / baseOf), so Compactor II's +compactor.store2 % still counts. XP and collections stay exact:
     xpn / xpw now count base items (baseOf = stored + 100 x compressed), and a compressed item credits 100 base items at Collect and Sell.
     THE STORE IS <kind>.i<n>.legacy = "<Enchanted id>:<count>" - no new key. <kind>.i<n>.ench could NOT carry it: it pays the shard's BONUS item
     (Mining Emerald, Foraging Tree Sap; Farming's is Enchanted Wheat even on a Carrot island). legacy is the existing "item:count waiting for Collect"
     line: Collect already pays it, 0.4.19 reads it, and a legacy of another item (a sale that came back after a retype) only pauses compression until the next Collect
     (compOn false: then every Enchanted item and base item counts 1 against the plain cap).
     Collect gives the Enchanted items first; Sell sells the Enchanted stock at bazaar:sell:<Enchanted id> while there is any, then the base leftover at
     its own price (half / all / amount work on the count that is on sale; the view names the item and the leftover). Sell-back of Enchanted goes back into
     legacy (legIn), so compress + Collect + Sell + retype + picking up the shard use one debit-first path. Bonus finds in .ench are unchanged and do not use space.
  3. shard.xpPercent default 50 -> 20 (Skills 0.4.70 has the class-level limit).
  4. MINING COSTS TAKE INGOTS: the material token raw on a type that smelts = its ingot (island purchase, Amount, Irrigation), the Quarry Spirit recipe
     and Automation = Copper Ingots. Cobblestone, Enchanted Cobblestone and essences stay.
  ONE-TIME: ShMig0420 (marker skyyshards-0.4.20-storage; ShMig0419's reviewed machinery): storage.tier1..5, shard.xpPercent, craft.<Quarry Spirit> and up.auto.items.mining,
     each only while its line still holds the old default.
  0.4.19 LEFTOVERS: moonBlade before the lock + per-island offStart were already in 0.4.19 (verified). New here: a failing sell-back retries 60 times a minute apart, then only
     once more at the server stop (a FAILED line in collect.log); ShMath.sync acts on a key only after 3 ticks in the new state (a one-tick unreadable players file cannot
     restart an offline window); the Collect row's sub-line has a length budget (ShPage row; worst case asserted against the row width at build time);
     the last "between visits" label.
  SAVED DATA: <kind>.i<n>.legacy may now hold Enchanted stock. No new keys.
  ROLLBACK 0.4.20 -> 0.4.19 alone: Undo the ShMig0420 rows first (Server Setup > Shards > Changes). Compressed stock stays readable: 0.4.19's Collect pays <kind>.i<n>.legacy
     as that many Enchanted items (it credits XP / collection once per item, not x100 - an under-credit, nothing lost or duplicated); 0.4.19 does not count them against the cap.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

HERE = os.path.join(ROOT, "SkyyShards")
P = G.Patch(os.path.join(HERE, "build_skyyshards_0.4.19.py"), os.path.join(HERE, "build_skyyshards_0.4.20.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.4.19"\n') and P.has("GENERATED by tools/shards_0_4_19_patch.py") and not P.has("ShMig0420"), "not the generated SkyyShards 0.4.19"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.20 (2026-11-08)"):].rstrip() + "\n"

# ---------------------------------------------------------------------------------------------------- 0. header + version
P.rep('''"""SkyyShards 0.4.19 - build script (javassist via jpype). GENERATED by tools/shards_0_4_19_patch.py from build_skyyshards_0.4.18.py
(generated by tools/shards_0_4_18_patch.py from 0.4.17, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.19" /''', '''"""SkyyShards 0.4.20 - build script (javassist via jpype). GENERATED by tools/shards_0_4_20_patch.py from build_skyyshards_0.4.19.py
(generated by tools/shards_0_4_19_patch.py from 0.4.18, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.20" / "0.4.19" /''')
P.rep('''Run:   python SkyyShards/build_skyyshards_0.4.19.py   -> SkyyShards/SkyyShards-0.4.19.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.19.py
0.4.19 (2026-11-08) = THE OFFLINE LIMIT''', '''Run:   python SkyyShards/build_skyyshards_0.4.20.py   -> SkyyShards/SkyyShards-0.4.20.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.20.py
''' + NOTE + '''
0.4.19 notes:
0.4.19 (2026-11-08) = THE OFFLINE LIMIT''')
P.rep('VERSION = "0.4.19"\n', 'VERSION = "0.4.20"\n')

# ---------------------------------------------------------------------------------------------------- 1. storage, XP, ingots: the numbers + the migration's rows
P.rep('''STORE_STACKS = list(P6_STORE)                  # 0.4.4 fix 2: storage tier N = 3 days of a full Large island at Totem N
MIG044 += [("storage.tier%d" % (_i + 1), "%d" % STORE_0443[_i], "%d" % STORE_STACKS[_i], "n") for _i in range(5)]
''', '''# 0.4.20 (Skyy popup 2026-11-08: "1k / 3k / 8k / 20k / 50k"; "i shouldnt be aboe to get 100k of anything untill lateeee game"): stacks of 100 per island (P6_STORE stays as 0.4.4's history)
STORE_STACKS = [10, 30, 80, 200, 500]
MIG044 += [("storage.tier%d" % (_i + 1), "%d" % STORE_0443[_i], "%d" % P6_STORE[_i], "n") for _i in range(5)]
''')
P.rep('''    assert ("\\n%s=%s\\n" % (_k, _n)) in "\\n" + CONFIG_TEXT + "\\n", _k            # the new default file holds the new value
assert CONFIG_TEXT.count(MIG044_MK) == 1''', '''    assert _k.startswith("storage.tier") or ("\\n%s=%s\\n" % (_k, _n)) in "\\n" + CONFIG_TEXT + "\\n", _k   # the new default file holds the new value (0.4.20 moved storage.tierN on: ShMig0420 runs after this one)
assert CONFIG_TEXT.count(MIG044_MK) == 1''')
P.rep('''AUTO_ITEMS48 = ["%s:128" % LAD[_k][0]["prod"] for _k in range(NK)]   # Automation = step 2 + 128 of the shard's T1 raw item
''', '''AUTO_ITEMS_0419 = ["%s:128" % LAD[_k][0]["prod"] for _k in range(NK)]   # Automation = step 2 + 128 of the shard's T1 raw item
AUTO_ITEMS48 = ["%s:128" % (LAD[_k][0]["smelt"] or LAD[_k][0]["prod"]) for _k in range(NK)]   # 0.4.20 (Skyy: "on the mining shard, instead of using ore to upgrade, use ingots"): Mining = Copper Ingots
assert AUTO_ITEMS48[0] == "Ingredient_Bar_Copper:128" and AUTO_ITEMS48[1:] == AUTO_ITEMS_0419[1:], AUTO_ITEMS48
''')
QUARRY_OLD, QUARRY_NEW = "Ore_Copper:128,Ingredient_Life_Essence:8;500", "Ingredient_Bar_Copper:128,Ingredient_Life_Essence:8;500"
P.rep('(TOTEM_ITEM[_TI["quarry_spirit"]], "%s"),' % QUARRY_OLD, '(TOTEM_ITEM[_TI["quarry_spirit"]], "%s"),   # 0.4.20: ingots, not ore (was %s)' % (QUARRY_NEW, QUARRY_OLD))
P.rep('''STORE_COINS_047 = list(STORE_COINS)''', '''# 0.4.20 ONE-TIME UPDATE (one marker): untouched default lines only
MIG0420 = [("storage.tier%d" % (_i + 1), "%d" % P6_STORE[_i], "%d" % STORE_STACKS[_i], "n") for _i in range(5)] + [("shard.xpPercent", "50", "20", "n")] + \
          [("craft." + TOTEM_ITEM[_TI["quarry_spirit"]], "''' + QUARRY_OLD + '''", "''' + QUARRY_NEW + '''", "t"), ("up.auto.items.%s" % KKEYS[0], AUTO_ITEMS_0419[0], AUTO_ITEMS48[0], "t")]
MIG0420_MK = "skyyshards-0.4.20-storage"
MIG0420_LINE = "# ---------- SkyyShards 0.4.20 (marker %s, runs once): smaller storage (1k .. 50k an island), shards pay 20 %% XP, Mining costs take ingots; only untouched old default lines were changed ----------" % MIG0420_MK
STORE_COINS_047 = list(STORE_COINS)''')
P.rep('''    "# shard.xpPercent = Farming XP paid at Collect, in percent of the overworld XP per item (Skyy G9: 50).",
    "shard.xpPercent=50",''', '''    "# shard.xpPercent = skill XP paid when a shard's items are collected or sold, in percent of the overworld XP per item (Skyy 2026-11-08: 20).",
    "shard.xpPercent=20",''')
P.rep('''"public static volatile int XP_PCT = 50;",''', '''"public static volatile int XP_PCT = 20;",''')
P.rep('''    ("shard.xpPercent", "Collect XP (percent)", "production", "int", "50", "0", "100", "", "%", "live",
     "Farming XP paid at Collect, in percent of the overworld XP per item (Skyy: 50).", "field:''', '''    ("shard.xpPercent", "Collect XP (percent)", "production", "int", "20", "0", "100", "", "%", "live",
     "Skill XP paid at Collect and Sell, in percent of the overworld XP per item (Skyy: 20).", "field:''')
P.rep('''"  XP_PCT = intOf(p.getProperty(\\"shard.xpPercent\\"), 50, 0, 100);",''', '''"  XP_PCT = intOf(p.getProperty(\\"shard.xpPercent\\"), 20, 0, 100);",''')
P.rep('''    "# storage.tierN = stacks of 100 each island of the shard holds at storage tier N (0.4.4: 3 days of a full Large island at Totem N).",''',
      '''    "# storage.tierN = stacks of 100 each island of the shard holds at storage tier N (0.4.20: 1,000 .. 50,000 items; an Auto-Compactor counts Enchanted items).",''')
P.rep('''      "Stacks of 100 per island at storage tier %d (default = 3 days of a full Large Totem %s island)." % (i + 1, ROMAN[i]), "field:ShCfg.ST%d''',
      '''      "Stacks of 100 before island bonus (%d = %s items). Auto-Compactor: counts Enchanted items." % (STORE_STACKS[i], format(STORE_STACKS[i] * 100, ",")), "field:ShCfg.ST%d''')
P.rep('''    "# compactor.coinsN / compactor.itemsN = Auto-Compactor tier N (I: Collect gives the Enchanted form of every 100; II: + more storage).",''',
      '''    "# compactor.coinsN / compactor.itemsN = Auto-Compactor tier N (I: islands store 1 Enchanted item for every 100 made; II: + more storage).",''')
P.rep('''    "shard.ui.keepScroll=true",
''', '''    "shard.ui.keepScroll=true",
    "# SkyyShards 0.4.20 defaults (marker %s): smaller storage, 20 %% XP, Mining ingots - keep this line." % MIG0420_MK,
''')

# ---------------------------------------------------------------------------------------------------- 2. ShMig0420 (ShMig0419's reviewed machinery)
_A = P.s.index("smig419 = mk(\"ShMig0419\")")
_B = P.s.index('M(cfg, r"""\npublic static int stacks(int tier) {')
MIG_SRC = P.s[_A:_B]
assert MIG_SRC.count("public static synchronized String run(") == 1 and MIG_SRC.count("MIG0419") >= 6, MIG_SRC.count("MIG0419")
MIG_NEW = (MIG_SRC.replace("smig419", "smig420").replace("ShMig0419", "ShMig0420").replace("MIG0419", "MIG0420").replace("SkyyShards 0.4.19", "SkyyShards 0.4.20")
           .replace("the 0.4.19 default", "the 0.4.20 default").replace("before the 0.4.19 update", "before the 0.4.20 update")
           .replace("(the offline limit)", "(smaller storage, 20 % XP, Mining ingots)").replace("(the offline limit; the file is used as it is)", "(smaller storage, 20 % XP, Mining ingots; the file is used as it is)")
           .replace("(shards make less while the owner is offline: Offline Harvest hours 8..24, were 12..72)", "(smaller storage 1k .. 50k an island, shards pay 20 % XP, Mining costs take ingots)"))
assert "0.4.19" not in MIG_NEW and "offline limit" not in MIG_NEW, re.findall(r".{40}0\.4\.19.{20}", MIG_NEW)[:5]
P.rep('M(cfg, r"""\npublic static int stacks(int tier) {', '''# ================= 0.4.20 ShMig0420 (PROJECT-RULES 4; ShMig0419's reviewed machinery): storage.tierN, shard.xpPercent, the Mining ore costs, only while a line still holds its old default
for _k, _o, _n, _t in MIG0420:
    assert ("\\n%s=%s\\n" % (_k, _n)) in "\\n" + CONFIG_TEXT + "\\n", _k
    assert _o != _n
assert CONFIG_TEXT.count(MIG0420_MK) == 1
''' + MIG_NEW + 'M(cfg, r"""\npublic static int stacks(int tier) {')
P.rep('''  catch (Throwable t) { @PKG@.ShCfg.warn("the 0.4.19 settings update was skipped: " + t); }
''', '''  catch (Throwable t) { @PKG@.ShCfg.warn("the 0.4.19 settings update was skipped: " + t); }
  try { @PKG@.ShMig0420.run(@PKG@.ShCfg.FILE); }   // 0.4.20: untouched storage / XP / Mining ore lines, once (History first; Undo)
  catch (Throwable t) { @PKG@.ShCfg.warn("the 0.4.20 settings update was skipped: " + t); }
''')
P.rep("smig49, smig419, st,", "smig49, smig419, smig420, st,")

# ---------------------------------------------------------------------------------------------------- 3. Mining costs take ingots; which island item an Enchanted id stands for
P.rep('''  if (tk.equals("raw")) return PROD[t];
''', '''  if (tk.equals("raw")) return SMELT[t].length() > 0 ? SMELT[t] : PROD[t];   // 0.4.20: a type that smelts costs ingots ("on the mining shard, instead of using ore to upgrade, use ingots")
''')
P.rep('''M(isl48, r"""
public static String tok(int kd, int t, String tk) {''', '''# 0.4.20: the island item an Enchanted id compresses (null = not one of the ladders' Enchanted forms); ingots count as their ore, as Collect always credited
M(isl48, r"""
public static String enchBase(String id) {
  if (id == null || id.length() == 0) return null;
  for (int t = 0; t < PROD.length; t++) if (id.equals(ENCH[t]) || id.equals(SMELTE[t])) return PROD[t];
  return null;
}""")
M(isl48, r"""
public static String tok(int kd, int t, String tk) {''')

# ---------------------------------------------------------------------------------------------------- 4. ShMath: compression at settle
P.rep('''# settle one island at `now` (ms): returns the items made. 0.2:''', '''# 0.4.20 TRUE COMPRESSION: the Enchanted stock of an island waits in <kind>.i<n>.legacy ("id:count", which Collect pays and 0.4.19 reads); counts of legacy.
M(mth, r"""
public static String legId(int kd, java.util.Properties p, int slot) {
  String s = @PKG@.ShStore.str(p, ik(kd, slot, "legacy"));
  int c = s.lastIndexOf(':');
  return c > 0 ? s.substring(0, c) : "";
}""")
M(mth, r"""
public static long legN(int kd, java.util.Properties p, int slot) {
  String s = @PKG@.ShStore.str(p, ik(kd, slot, "legacy"));
  int c = s.lastIndexOf(':');
  if (c <= 0) return 0L;
  try { long n = Long.parseLong(s.substring(c + 1).trim()); return n < 0L ? 0L : n; } catch (Throwable t) { return 0L; }
}""")
# the Enchanted item waiting on this island ("" = none) and how many
M(mth, r"""
public static String compId(int kd, java.util.Properties p, int slot) {
  String id = legId(kd, p, slot);
  return @PKG@.ShIsl.enchBase(id) != null ? id : "";
}""")
M(mth, r"""
public static long comp(int kd, java.util.Properties p, int slot) {
  return compId(kd, p, slot).length() > 0 ? legN(kd, p, slot) : 0L;
}""")
# the Enchanted form this island compresses into right now ("" = no Auto-Compactor, or no Enchanted form under the current rules: a Mining island needs its pole)
M(mth, r"""
public static String compForm(int kd, java.util.Properties p, int slot) {
  if (compactor(kd, p) < 1 || !hasIsland(kd, p, slot)) return "";
  if (@PKG@.ShKind.ENCH[kd].length() == 0 && @PKG@.ShKind.SMELT_ENCH[kd].length() == 0) return "";
  int t = @PKG@.ShIsl.ty(kd, p, slot);
  boolean sm = @PKG@.ShTotem.smelts(kd, p, slot) && @PKG@.ShIsl.SMELT[t].length() > 0;
  return sm ? @PKG@.ShIsl.SMELTE[t] : @PKG@.ShIsl.ENCH[t];
}""")
# compressing now? (no other item may be waiting in the line: a sale's unsold items after a retype wait until the next Collect)
M(mth, r"""
public static boolean compOn(int kd, java.util.Properties p, int slot) {
  String f = compForm(kd, p, slot);
  if (f.length() == 0) return false;
  String id = legId(kd, p, slot);
  return id.length() == 0 || legN(kd, p, slot) <= 0L || id.equals(f);
}""")
# the stock in base items (1 Enchanted = 100)
M(mth, r"""
public static long baseOf(int kd, java.util.Properties p, int slot) {
  long s = @PKG@.ShStore.lng(p, ik(kd, slot, "stored"), 0L);
  return (s < 0L ? 0L : s) + 100L * comp(kd, p, slot);
}""")
# the limit + the use in the same unit: base items x 100 while compressing, else 1 Enchanted = 1 item against the plain cap
M(mth, r"""
public static long limOf(int kd, java.util.Properties p, int slot) {
  long c = capOf(kd, p, slot);
  if (!compOn(kd, p, slot)) return c;
  return c > 90000000000000L ? 9000000000000000L : c * 100L;
}""")
M(mth, r"""
public static long usedOf(int kd, java.util.Properties p, int slot) {
  long s = @PKG@.ShStore.lng(p, ik(kd, slot, "stored"), 0L);
  if (s < 0L) s = 0L;
  return s + comp(kd, p, slot) * (compOn(kd, p, slot) ? 100L : 1L);
}""")
M(mth, r"""
public static void compSet(int kd, java.util.Properties p, int slot, String id, long n) {
  if (n <= 0L) p.remove(ik(kd, slot, "legacy")); else p.setProperty(ik(kd, slot, "legacy"), id + ":" + n);
}""")
# every full 100 base items -> 1 Enchanted item, under the lock; the base-item total (baseOf) does not change
M(mth, r"""
public static void compress(int kd, java.util.Properties p, int slot) {
  if (!compOn(kd, p, slot)) return;
  long s = @PKG@.ShStore.lng(p, ik(kd, slot, "stored"), 0L);
  if (s < 100L) return;
  long n = s / 100L;
  long c = comp(kd, p, slot);
  compSet(kd, p, slot, compForm(kd, p, slot), c + n);
  p.setProperty(ik(kd, slot, "stored"), String.valueOf(s - n * 100L));
}""")
# the 0.4.8 map migration retypes islands: their Enchanted stock goes back to base items first, so it is kept as that migration's old-item line
M(mth, r"""
public static void uncompress(int kd, java.util.Properties p, int slot) {
  long c = comp(kd, p, slot);
  if (c <= 0L) return;
  long s = @PKG@.ShStore.lng(p, ik(kd, slot, "stored"), 0L);
  p.setProperty(ik(kd, slot, "stored"), String.valueOf((s < 0L ? 0L : s) + c * 100L));
  p.remove(ik(kd, slot, "legacy"));
}""")
# settle one island at `now` (ms): returns the items made. 0.2:''')
P.rep('''  double cur = @PKG@.ShTotem.xpPer(kd, p, slot, size(kd, p, slot), now);
  if (kd != FK) return cur;
  long s = @PKG@.ShStore.lng(p, ik(kd, slot, "stored"), 0L);
  if (s <= 0L) return cur;''', '''  double cur = @PKG@.ShTotem.xpPer(kd, p, slot, size(kd, p, slot), now);
  if (kd != FK) return cur;
  long s = baseOf(kd, p, slot);   // 0.4.20: counted in base items (a compressed item = 100)
  if (s <= 0L) return cur;''')
P.rep('''  if (!hasIsland(kd, p, slot)) return 0L;
  long last = @PKG@.ShStore.lng(p, ik(kd, slot, "last"), now);
  long stored = @PKG@.ShStore.lng(p, ik(kd, slot, "stored"), 0L);
  if (stored < 0L) stored = 0L;
  double xa0 = kd == FK ? xpAvg(kd, p, slot, now) : 0.0;   // 0.4.4 fix 2: the XP per item of the stock already stored
  long cap = capOf(kd, p, slot);
''', '''  if (!hasIsland(kd, p, slot)) return 0L;
  compress(kd, p, slot);   // 0.4.20: stock already stored (the first settle with a Compactor, a pole put back)
  long last = @PKG@.ShStore.lng(p, ik(kd, slot, "last"), now);
  long stored = @PKG@.ShStore.lng(p, ik(kd, slot, "stored"), 0L);
  if (stored < 0L) stored = 0L;
  double xa0 = kd == FK ? xpAvg(kd, p, slot, now) : 0.0;   // 0.4.4 fix 2: the XP per item of the stock already stored
  long lim = limOf(kd, p, slot);   // 0.4.20: both in the same unit (compressing: base items, 1 Enchanted = 100 of them)
  long use = usedOf(kd, p, slot);
''')
P.rep('''  if (paused(kd, p) || stored >= cap) {   // fix (critic): a picked-up shard makes nothing until it is placed again''',
      '''  if (paused(kd, p) || use >= lim) {   // fix (critic): a picked-up shard makes nothing until it is placed again; 0.4.20: over a lowered cap = stock kept, nothing made''')
P.rep('''    } else if (stored + made >= cap) {
      made = cap - stored; last = now;''', '''    } else if (use + made >= lim) {
      made = lim - use; last = now;''')
P.rep('''  p.setProperty(ik(kd, slot, "stored"), String.valueOf(stored));
  if (kd == FK) xpSet(kd, p, slot, stored, xa0 * (double) (stored - made) + (made > 0L ?''', '''  p.setProperty(ik(kd, slot, "stored"), String.valueOf(stored));
  compress(kd, p, slot);   // 0.4.20: every full 100 is stored as 1 Enchanted item
  long bs = baseOf(kd, p, slot);
  if (kd == FK) xpSet(kd, p, slot, bs, xa0 * (double) (bs - made) + (made > 0L ?''')
P.rep('''public static void xpSet(int kd, java.util.Properties p, int slot, long n, double w) {
  if (kd != FK) return;
  if (n < 0L) n = 0L;
  if (n == 0L || Double.isNaN(w) || w < 0.0) w = 0.0;
  p.setProperty(ik(kd, slot, "xpn"), String.valueOf(n));
  p.setProperty(ik(kd, slot, "xpw"), String.valueOf(w));
}""")
''', '''public static void xpSet(int kd, java.util.Properties p, int slot, long n, double w) {
  if (kd != FK) return;
  if (n < 0L) n = 0L;
  if (n == 0L || Double.isNaN(w) || w < 0.0) w = 0.0;
  p.setProperty(ik(kd, slot, "xpn"), String.valueOf(n));
  p.setProperty(ik(kd, slot, "xpw"), String.valueOf(w));
}""")
# 0.4.20: after a debit or a refund of stored / compressed stock, xa = the XP per base item it keeps
M(mth, r"""
public static void xpRe(int kd, java.util.Properties p, int slot, double xa) {
  long b = baseOf(kd, p, slot);
  xpSet(kd, p, slot, b, (double) b * xa);
}""")
''')
P.rep('''  long left = capOf(kd, p, slot) - stored(kd, p, slot);
''', '''  long left = limOf(kd, p, slot) - usedOf(kd, p, slot);   // 0.4.20: in base items while compressing
''')
P.rep('''            long sto = @PKG@.ShMath.stored(kd, p, s);
            if (sto > 0L) {
              p.setProperty(@PKG@.ShIsl.ik(kd, s, "legacy"),''', '''            @PKG@.ShMath.uncompress(kd, p, s);   // 0.4.20: migrate2's settle may just have compressed it; the old item's line below holds base items
            long sto = @PKG@.ShMath.stored(kd, p, s);
            if (sto > 0L) {
              p.setProperty(@PKG@.ShIsl.ik(kd, s, "legacy"),''')
P.rep('''            work = @PKG@.ShMath.stored(kd, p, i) < @PKG@.ShMath.capOf(kd, p, i) && @PKG@.ShMath.rate(kd, p, i, now) > 0.0;''',
      '''            work = @PKG@.ShMath.usedOf(kd, p, i) < @PKG@.ShMath.limOf(kd, p, i) && @PKG@.ShMath.rate(kd, p, i, now) > 0.0;''')

# debounce: one tick of a different key (an unreadable players file answers profile 1 for a moment) must not act as a logout + login
P.rep('''M(mth, r"""
public static void sync(java.util.Set keys, long now) {
  java.util.Iterator it = ONLINE.keySet().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (!keys.contains(k)) outSafe(k, now);
  }
  java.util.Iterator in = keys.iterator();
  while (in.hasNext()) inSafe((String) in.next(), now);
}""")''', '''# 0.4.20 (critic): a key acts only after SYNC_TICKS checks in a row in its new state; a key back to normal forgets its count
F(mth, "public static final java.util.concurrent.ConcurrentHashMap SYNC_C = new java.util.concurrent.ConcurrentHashMap();")
F(mth, "public static volatile int SYNC_TICKS = 3;")
M(mth, r"""
public static boolean syncDue(String k) {
  Object o = SYNC_C.get(k);
  int c = (o == null ? 0 : ((Integer) o).intValue()) + 1;
  if (c >= SYNC_TICKS) { SYNC_C.remove(k); return true; }
  SYNC_C.put(k, Integer.valueOf(c));
  return false;
}""")
M(mth, r"""
public static void sync(java.util.Set keys, long now) {
  java.util.Iterator c0 = SYNC_C.keySet().iterator();
  while (c0.hasNext()) {
    String k0 = (String) c0.next();
    if (keys.contains(k0) == ONLINE.containsKey(k0)) c0.remove();
  }
  java.util.Iterator it = ONLINE.keySet().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (!keys.contains(k) && syncDue(k)) outSafe(k, now);
  }
  java.util.Iterator in = keys.iterator();
  while (in.hasNext()) {
    String k2 = (String) in.next();
    if (!ONLINE.containsKey(k2) && syncDue(k2)) inSafe(k2, now);
  }
}""")''')

# ---------------------------------------------------------------------------------------------------- 5. ShCore: Collect
P.rep('''      if (take[i] > 0L || takeE[i] > 0L) xa[i] = @PKG@.ShMath.xpAvg(kd, p, i, now);
''', '''      if (take[i] > 0L || takeE[i] > 0L || (takeL[i] > 0L && @PKG@.ShMath.hasIsland(kd, p, i))) xa[i] = @PKG@.ShMath.xpAvg(kd, p, i, now);   // 0.4.20: Enchanted stock too
''')
P.rep('''      if (take[i] > 0L) @PKG@.ShMath.xpSet(kd, p, i, @PKG@.ShMath.stored(kd, p, i) - take[i], (double) (@PKG@.ShMath.stored(kd, p, i) - take[i]) * xa[i]);   // 0.4.4 fix 2
      if (take[i] > 0L) p.setProperty(@PKG@.ShMath.ik(kd, i, "stored"), String.valueOf(@PKG@.ShMath.stored(kd, p, i) - take[i]));
''', '''      if (take[i] > 0L) p.setProperty(@PKG@.ShMath.ik(kd, i, "stored"), String.valueOf(@PKG@.ShMath.stored(kd, p, i) - take[i]));
''')
P.rep('''      if (takeL[i] > 0L) p.remove(@PKG@.ShIsl.ik(kd, i, "legacy"));
    }
    p.setProperty(lastKey(kd), String.valueOf(now));''', '''      if (takeL[i] > 0L) p.remove(@PKG@.ShIsl.ik(kd, i, "legacy"));
      if (take[i] > 0L || takeL[i] > 0L) @PKG@.ShMath.xpRe(kd, p, i, xa[i]);   // 0.4.4 fix 2; 0.4.20: base items
    }
    p.setProperty(lastKey(kd), String.valueOf(now));''')
P.rep('''        long gl = @PKG@.ShInv.give(cs, lid[i], takeL[i]);
        if (gl > 0L) { got.put(lid[i], Long.valueOf((got.get(lid[i]) == null ? 0L : ((Long) got.get(lid[i])).longValue()) + gl)); cred.put(lid[i], Long.valueOf((cred.get(lid[i]) == null ? 0L : ((Long) cred.get(lid[i])).longValue()) + gl)); }
        baseGiven += gl;
        xpD += (double) gl * (double) @PKG@.ShCfg.xpOf(kd);
''', '''        String lb = @PKG@.ShIsl.enchBase(lid[i]);   // 0.4.20: Enchanted stock = 100 base items each (XP, collection)
        long lu = lb != null ? 100L : 1L;
        String lc0 = lb != null ? lb : lid[i];
        long gl = @PKG@.ShInv.give(cs, lid[i], takeL[i]);
        if (gl > 0L) { got.put(lid[i], Long.valueOf((got.get(lid[i]) == null ? 0L : ((Long) got.get(lid[i])).longValue()) + gl)); cred.put(lc0, Long.valueOf((cred.get(lc0) == null ? 0L : ((Long) cred.get(lc0)).longValue()) + gl * lu)); }
        baseGiven += gl * lu;
        if (lb != null) gEnch += gl;
        xpD += (double) (gl * lu) * (lb != null && xi > 0.0 ? xi : (double) @PKG@.ShCfg.xpOf(kd));
''')
P.rep('''        if (bm[i] > 0L) @PKG@.ShMath.xpSet(kd, p, i, @PKG@.ShMath.stored(kd, p, i) + bm[i], (double) (@PKG@.ShMath.stored(kd, p, i) + bm[i]) * xa[i]);   // 0.4.4 fix 2
        if (bm[i] > 0L) p.setProperty(@PKG@.ShMath.ik(kd, i, "stored"), String.valueOf(@PKG@.ShMath.stored(kd, p, i) + bm[i]));
''', '''        if (bm[i] > 0L) p.setProperty(@PKG@.ShMath.ik(kd, i, "stored"), String.valueOf(@PKG@.ShMath.stored(kd, p, i) + bm[i]));
''')
P.rep('''        if (bl[i] > 0L) p.setProperty(@PKG@.ShIsl.ik(kd, i, "legacy"), lid[i] + ":" + bl[i]);
''', '''        if (bl[i] > 0L) p.setProperty(@PKG@.ShIsl.ik(kd, i, "legacy"), lid[i] + ":" + bl[i]);
        if (bm[i] > 0L || bl[i] > 0L) @PKG@.ShMath.xpRe(kd, p, i, xa[i]);   // 0.4.4 fix 2; 0.4.20: base items
''')
P.rep('''return nc == 1 ? "+Auto-Compactor I: Collect now gives the Enchanted form of every 100." :''', '''return nc == 1 ? "+Auto-Compactor I: this shard now stores items as Enchanted - 100 items take the space of 1." :''')

# ---------------------------------------------------------------------------------------------------- 6. ShCore: Sell on the Enchanted count
P.rep('''# the item a sale takes from this island (ingots when it smelts = what Collect would give); under the lock
M(core, r"""
public static String sellItem(int kd, java.util.Properties p, int slot) {
  int t = @PKG@.ShIsl.ty(kd, p, slot);
  boolean sm = @PKG@.ShTotem.smelts(kd, p, slot) && @PKG@.ShIsl.SMELT[t].length() > 0;
  return sm ? @PKG@.ShIsl.SMELT[t] : @PKG@.ShIsl.PROD[t];
}""")''', '''# the base item a sale takes from this island (ingots when it smelts = what Collect would give); under the lock
M(core, r"""
public static String baseItem(int kd, java.util.Properties p, int slot) {
  int t = @PKG@.ShIsl.ty(kd, p, slot);
  boolean sm = @PKG@.ShTotem.smelts(kd, p, slot) && @PKG@.ShIsl.SMELT[t].length() > 0;
  return sm ? @PKG@.ShIsl.SMELT[t] : @PKG@.ShIsl.PROD[t];
}""")
# 0.4.20: what is on sale now - the Enchanted stock while there is any, then the base leftover
M(core, r"""
public static String sellItem(int kd, java.util.Properties p, int slot) {
  return @PKG@.ShMath.comp(kd, p, slot) > 0L ? @PKG@.ShMath.compId(kd, p, slot) : baseItem(kd, p, slot);
}""")''')
P.rep('''public static void sellBack(String k, int kd, int slot, long n, double xa, String ci) {
  if (n <= 0L) return;
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) throw new IllegalStateException("the shard file could not be read");
  @PKG@.ShStore.LOCK.lock(); try {
    if (@PKG@.ShMath.hasIsland(kd, p, slot) && ci.equals(@PKG@.ShIsl.PROD[@PKG@.ShIsl.ty(kd, p, slot)])) {
      long s0 = @PKG@.ShMath.stored(kd, p, slot);
      @PKG@.ShMath.xpSet(kd, p, slot, s0 + n, (double) s0 * @PKG@.ShMath.xpAvg(kd, p, slot, now()) + (double) n * xa);   // what was made meanwhile keeps its own XP
      p.setProperty(@PKG@.ShMath.ik(kd, slot, "stored"), String.valueOf(s0 + n));
    } else if (!legIn(kd, p, slot, ci, n)) {
''', '''public static void sellBack(String k, int kd, int slot, long n, double xa, String ci, boolean c) {   // c = ci is Enchanted stock (n of them, legIn merges it into the island's line)
  if (n <= 0L) return;
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) throw new IllegalStateException("the shard file could not be read");
  @PKG@.ShStore.LOCK.lock(); try {
    boolean has0 = @PKG@.ShMath.hasIsland(kd, p, slot);
    long u0 = c ? 100L : 1L;
    long b0 = has0 ? @PKG@.ShMath.baseOf(kd, p, slot) : 0L;
    double xr = has0 && b0 > 0L ? @PKG@.ShMath.xpAvg(kd, p, slot, now()) : xa;
    if (!c && has0 && ci.equals(@PKG@.ShIsl.PROD[@PKG@.ShIsl.ty(kd, p, slot)])) {
      long s0 = @PKG@.ShMath.stored(kd, p, slot);
      @PKG@.ShMath.xpSet(kd, p, slot, b0 + n, (double) b0 * xr + (double) n * xa);   // what was made meanwhile keeps its own XP
      p.setProperty(@PKG@.ShMath.ik(kd, slot, "stored"), String.valueOf(s0 + n));
    } else if (legIn(kd, p, slot, ci, n)) {
      if (c && has0 && ci.equals(@PKG@.ShMath.compId(kd, p, slot))) @PKG@.ShMath.xpSet(kd, p, slot, b0 + n * u0, (double) b0 * xr + (double) (n * u0) * xa);
    } else {
''')
P.rep('''public static void sellBackQ(String k, int kd, int slot, long n, double xa, String ci) {
  try { sellBack(k, kd, slot, n, xa, ci); }
  catch (Throwable t) {
    boolean busy = t instanceof @PKG@.ShBusy;
    if (!busy) @PKG@.ShCfg.warnOnce("sellback", "Sell: unsold items could not go back yet, trying again every minute (logged once): " + t);
    SELLQ.add(new Object[] { k, Integer.valueOf(kd), Integer.valueOf(slot), Long.valueOf(n), Double.valueOf(xa), ci, Long.valueOf(busy ? 0L : now() + 60000L) });   // a busy lock: the next tick; else no disk read every second (never dropped: that would lose the items)
  }
}""")''', '''public static void sellBackQ(String k, int kd, int slot, long n, double xa, String ci, boolean c, int tries) {
  try { sellBack(k, kd, slot, n, xa, ci, c); }
  catch (Throwable t) {
    boolean busy = t instanceof @PKG@.ShBusy;
    if (!busy) @PKG@.ShCfg.warnOnce("sellback", "Sell: unsold items could not go back yet, trying again every minute (logged once): " + t);
    int tn = busy ? tries : tries + 1;   // 0.4.20 (critic): a broken file stops being read after an hour, the entry still gets one last try at the server stop (never dropped)
    if (tn == 60) { @PKG@.ShCfg.warn("Sell: " + n + " " + ci + " still cannot go back to " + k + " - the last try is at the server stop (collect.log has the amount)."); @PKG@.ShStore.log(k + " " + @PKG@.ShKind.KEYS[kd] + " slot " + slot + " SELL back FAILED (retrying once more at the stop) " + n + " " + ci); }
    SELLQ.add(new Object[] { k, Integer.valueOf(kd), Integer.valueOf(slot), Long.valueOf(n), Double.valueOf(xa), ci, Long.valueOf(busy ? 0L : (tn >= 60 ? Long.MAX_VALUE - 1L : now() + 60000L)), Boolean.valueOf(c), Integer.valueOf(tn) });   // a busy lock: the next tick
  }
}""")''')
P.rep('''      else sellBackQ((String) a[0], ((Integer) a[1]).intValue(), ((Integer) a[2]).intValue(), ((Long) a[3]).longValue(), ((Double) a[4]).doubleValue(), (String) a[5]);''',
      '''      else sellBackQ((String) a[0], ((Integer) a[1]).intValue(), ((Integer) a[2]).intValue(), ((Long) a[3]).longValue(), ((Double) a[4]).doubleValue(), (String) a[5], ((Boolean) a[7]).booleanValue(), ((Integer) a[8]).intValue());''')
P.rep('''    if (@PKG@.ShMath.hasIsland(kd, p, slot)) id0 = sellItem(kd, p, slot);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (id0 == null)''', '''    @PKG@.ShMath.settleAll(kd, p, now());   // 0.4.20: compresses, so the item checked below is the item sold
    if (@PKG@.ShMath.hasIsland(kd, p, slot)) id0 = sellItem(kd, p, slot);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (id0 == null)''')
P.rep('''  double xi = 0.0;
  String ci = "";
  @PKG@.ShStore.LOCK.lock(); try {
    long now = now();
    @PKG@.ShMath.settleAll(kd, p, now);
    if (!@PKG@.ShMath.hasIsland(kd, p, slot) || !id0.equals(sellItem(kd, p, slot))) return "=That island changed - the page is up to date now.";
    long s = @PKG@.ShMath.stored(kd, p, slot);
    if (s <= 0L) return "=Nothing is stored there yet.";''', '''  double xi = 0.0;
  String ci = "";
  boolean isC = false;   // 0.4.20: the Enchanted stock is on sale (qty counts Enchanted items, 100 base items each)
  @PKG@.ShStore.LOCK.lock(); try {
    long now = now();
    @PKG@.ShMath.settleAll(kd, p, now);
    if (!@PKG@.ShMath.hasIsland(kd, p, slot) || !id0.equals(sellItem(kd, p, slot))) return "=That island changed - the page is up to date now.";
    long cn = @PKG@.ShMath.comp(kd, p, slot);
    isC = cn > 0L;
    long s = isC ? cn : @PKG@.ShMath.stored(kd, p, slot);
    if (s <= 0L) return "=Nothing is stored there yet.";''')
P.rep('''    ci = @PKG@.ShIsl.PROD[@PKG@.ShIsl.ty(kd, p, slot)];
    xi = @PKG@.ShMath.xpAvg(kd, p, slot, now);   // read before the debit, as Collect
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
    @PKG@.ShMath.xpSet(kd, p, slot, s - qty, (double) (s - qty) * xi);
    p.setProperty(@PKG@.ShMath.ik(kd, slot, "stored"), String.valueOf(s - qty));
''', '''    ci = isC ? @PKG@.ShIsl.enchBase(id0) : @PKG@.ShIsl.PROD[@PKG@.ShIsl.ty(kd, p, slot)];   // 0.4.20: the collection of the item it compresses
    xi = @PKG@.ShMath.xpAvg(kd, p, slot, now);   // read before the debit, as Collect
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
    if (isC) @PKG@.ShMath.compSet(kd, p, slot, id0, s - qty);
    else p.setProperty(@PKG@.ShMath.ik(kd, slot, "stored"), String.valueOf(s - qty));
    @PKG@.ShMath.xpRe(kd, p, slot, xi);
''')
P.rep('''  if (back > 0L) sellBackQ(k, kd, slot, back, xi, ci);
''', '''  if (back > 0L) sellBackQ(k, kd, slot, back, xi, isC ? id0 : ci, isC, 0);
''')
P.rep('''  cred.put(ci, Long.valueOf(sold));
  String extra = payCred(u, kd, sold, 0L, (double) sold * xi, cred);
''', '''  long un = isC ? 100L : 1L;
  cred.put(ci, Long.valueOf(sold * un));
  String extra = payCred(u, kd, sold * un, 0L, (double) (sold * un) * xi, cred);
''')

# ---------------------------------------------------------------------------------------------------- 7. the Collect tab, the tiles: the truth under compression
P.rep('''CAMT_W, CSEL_W = 220, 80  ''', '''CAMT_W, CSEL_W = 240, 80  ''')   # 0.4.20: 305,000 Ench / 305,000 (a maxed Large at Compactor II)
P.rep('''assert CTX_W >= 300 and CHS[0] == 56, (CTX_W, CHS)
''', '''assert CTX_W >= 300 and CHS[0] == 56, (CTX_W, CHS)
# 0.4.20 (critic: nothing cut off): the longest amount and the longest allowed sub-line (Java: at most 60 characters) fit at the biggest row sizes
assert SUI.text_width("305,000 Ench / 305,000", 20, bold=True) <= CAMT_W, CAMT_W
# 0.4.20 (critic 3): every sub-line the row can really build, longest numbers, each shard's bonus name, each ending, cut at the Java limit of 60 characters
_SUBW = max(SUI.text_width((h_ + b_ + t_)[:60], 14)
            for h_ in ("8888888 / hour - full in 888 d 88 h", "8888888 / hour - no worker totem here", "8888888 / hour - FULL - collect to restart it")
            for b_ in ("", " - +88888888 Enchanted", " - +88888888 Emerald", " - +88888888 Tree Sap", " - +88888888 Linen Scraps")
            for t_ in ("", " - +888,888 loose", " - smelted", " - +888,888 loose - smelted"))
assert _SUBW <= CTX_W, (_SUBW, CTX_W)
''')
P.rep('''      long s = @PKG@.ShMath.stored(kd, p, i);
      double r = @PKG@.ShMath.rate(kd, p, i, now);''', '''      long s = @PKG@.ShMath.stored(kd, p, i);
      long cn = @PKG@.ShMath.comp(kd, p, i);   // 0.4.20: the Enchanted stock (100 base items each, 1 space)
      boolean co = @PKG@.ShMath.compOn(kd, p, i);
      double r = @PKG@.ShMath.rate(kd, p, i, now);''')
P.rep('''      total += s;
      xpP += (double) s * @PKG@.ShMath.xpAvg(kd, p, i, now);   // 0.4.4 (fix 2: the XP recorded when the items were made)
      long tf = @PKG@.ShMath.msToFull(kd, p, i, now);
      boolean full = s >= icap;''', '''      total += s + 100L * cn;
      compT += cn;
      xpP += (double) (s + 100L * cn) * @PKG@.ShMath.xpAvg(kd, p, i, now);   // 0.4.4 (fix 2: the XP recorded when the items were made)
      long tf = @PKG@.ShMath.msToFull(kd, p, i, now);
      boolean full = @PKG@.ShMath.usedOf(kd, p, i) >= @PKG@.ShMath.limOf(kd, p, i);''')
P.rep('''      this.cSub[c] = perHour(r) + " / hour - " + (full ? (bonus.length() > 0 || @PKG@.ShTotem.smelts(kd, p, i) ? "FULL" : "FULL - collect to restart it") : (tf < 0L ? "no worker totem here" : "full in " + @PKG@.ShMath.fmtMs(tf))) + bonus + (@PKG@.ShTotem.smelts(kd, p, i) ? " - smelted" : "");
      this.cAmt[c] = @PKG@.ShCfg.num(s) + " / " + @PKG@.ShCfg.num(icap);
''', '''      String loose = (co || cn > 0L) && s > 0L ? " - +" + @PKG@.ShCfg.num(s) + " loose" : "";
      String smlt = @PKG@.ShTotem.smelts(kd, p, i) ? " - smelted" : "";
      String sb0 = perHour(r) + " / hour - " + (full ? (bonus.length() > 0 || smlt.length() > 0 || loose.length() > 0 ? "FULL" : "FULL - collect to restart it") : (tf < 0L ? "no worker totem here" : "full in " + @PKG@.ShMath.fmtMs(tf))) + bonus;
      if (sb0.length() + loose.length() <= 60) sb0 = sb0 + loose;   // 0.4.20: never past the row's width (asserted against 60 characters at build time)
      if (sb0.length() + smlt.length() <= 60) sb0 = sb0 + smlt;
      if (sb0.length() > 60) sb0 = sb0.substring(0, 60);   // 0.4.20: a bonus count too long for the row is cut, the row never overflows
      this.cSub[c] = sb0;
      this.cAmt[c] = cn <= 0L && !co ? @PKG@.ShCfg.num(s) + " / " + @PKG@.ShCfg.num(icap) : @PKG@.ShCfg.num(cn) + " Ench / " + @PKG@.ShCfg.num(icap);   // 0.4.20: 1 Enchanted = 1 space; loose items are on the sub-line (the box fits only this form)
''')
P.rep('''      if (i == this.sellSlot) { svHas = true; svS = s; svEn = en; svXi = @PKG@.ShMath.xpAvg(kd, p, i, now); svIt = @PKG@.ShCore.sellItem(kd, p, i); svCi = @PKG@.ShIsl.PROD[@PKG@.ShIsl.ty(kd, p, i)]; svNm = this.cName[c]; }
''', '''      if (i == this.sellSlot) { svHas = true; svS = cn > 0L ? cn : s; svU = cn > 0L ? 100L : 1L; svLo = cn > 0L ? s : 0L; svLi = @PKG@.ShCore.baseItem(kd, p, i); svEn = en; svXi = @PKG@.ShMath.xpAvg(kd, p, i, now); svIt = @PKG@.ShCore.sellItem(kd, p, i); svCi = cn > 0L ? @PKG@.ShIsl.enchBase(svIt) : @PKG@.ShIsl.PROD[@PKG@.ShIsl.ty(kd, p, i)]; svNm = this.cName[c]; }
''')
P.rep('''  boolean svHas = false; long svS = 0L; long svEn = 0L; double svXi = 0.0; String svIt = ""; String svCi = ""; String svNm = "";   // 0.4.19''',
      '''  boolean svHas = false; long svS = 0L; long svEn = 0L; double svXi = 0.0; String svIt = ""; String svCi = ""; String svNm = "";   // 0.4.19
  long svU = 1L; long svLo = 0L; String svLi = ""; long compT = 0L;   // 0.4.20''')
P.rep('''  fillSell(svHas, svS, svEn, svXi, svIt, svCi, svNm);   // 0.4.19
''', '''  fillSell(svHas, svS, svEn, svXi, svIt, svCi, svNm, svU, svLo, svLi);   // 0.4.19; 0.4.20: what is on sale, what is left after it
''')
P.rep('''public void svTwo(int at, String head, long n, long pr, double xi, String ci) {
  int kd = this.kind;
  this.sv[at] = head + " (" + @PKG@.ShCfg.num(n) + "): about " + @PKG@.ShCfg.num(n * pr) + " coins";
  long xp = @PKG@.ShCore.xpTotal(kd, n, 0L, (double) n * xi);
  this.sv[at + 1] = (xp > 0L ? "+" + @PKG@.ShCfg.num(xp) + " " + @PKG@.ShKind.SKILL[kd] + " XP - " : "") + @PKG@.ShTotem.pretty(ci) + " collection +" + @PKG@.ShCfg.num(n);
}""")''', '''public void svTwo(int at, String head, long n, long pr, double xi, String ci, long u) {   // u = base items one sold item stands for
  int kd = this.kind;
  this.sv[at] = head + " (" + @PKG@.ShCfg.num(n) + "): about " + @PKG@.ShCfg.num(n * pr) + " coins";
  long xp = @PKG@.ShCore.xpTotal(kd, n * u, 0L, (double) (n * u) * xi);
  this.sv[at + 1] = (xp > 0L ? "+" + @PKG@.ShCfg.num(xp) + " " + @PKG@.ShKind.SKILL[kd] + " XP - " : "") + @PKG@.ShTotem.pretty(ci) + " collection +" + @PKG@.ShCfg.num(n * u);
}""")''')
P.rep('''public void fillSell(boolean has, long s, long en, double xi, String it, String ci, String nm) {''', '''public void fillSell(boolean has, long s, long en, double xi, String it, String ci, String nm, long u, long lo, String li) {''')
P.rep('''  this.sv[2] = "Stored: " + @PKG@.ShCfg.num(s);
''', '''  this.sv[2] = "Stored: " + @PKG@.ShCfg.num(s) + " " + @PKG@.ShTotem.pretty(it);   // 0.4.20: names the item on sale
''')
P.rep('''  this.sv[4] = en > 0L ? @PKG@.ShCfg.num(en) + " bonus finds stay here - use Collect for them." : "";
  if (s >= 2L) svTwo(5, "Half", s / 2L, pr, xi, ci); else this.sv[5] = "Half: too few stored";
  if (s >= 1L) svTwo(7, "All", s, pr, xi, ci); else this.sv[7] = "Nothing stored yet";
  if (this.sPrev > s) this.sv[9] = "That is more than is stored.";
  else if (this.sPrev > 0L) svTwo(9, "Amount", this.sPrev, pr, xi, ci);''', '''  String lo0 = lo > 0L ? "Then: " + @PKG@.ShCfg.num(lo) + " " + @PKG@.ShTotem.pretty(li) + ". " : "";   // 0.4.20: the leftover is sold after the Enchanted stock
  this.sv[4] = lo0 + (en > 0L ? @PKG@.ShCfg.num(en) + " bonus finds: use Collect." : "");
  if (s >= 2L) svTwo(5, "Half", s / 2L, pr, xi, ci, u); else this.sv[5] = "Half: too few stored";
  if (s >= 1L) svTwo(7, "All", s, pr, xi, ci, u); else this.sv[7] = "Nothing stored yet";
  if (this.sPrev > s) this.sv[9] = "That is more than is stored.";
  else if (this.sPrev > 0L) svTwo(9, "Amount", this.sPrev, pr, xi, ci, u);''')
P.rep('''  this.cAll[0] = @PKG@.ShCfg.num(total) + " items";
''', '''  this.cAll[0] = compT > 0L ? @PKG@.ShCfg.num(compT) + " Enchanted + " + @PKG@.ShCfg.num(total - 100L * compT) + " items" : @PKG@.ShCfg.num(total) + " items";   // 0.4.20
''')
P.rep('''    this.uTx[3] = "Each island of this shard holds this many items. A full island stops making items.";
''', '''    this.uTx[3] = (@PKG@.ShMath.compactor(kd, p) >= 1 ? "With the Auto-Compactor this counts Enchanted items." : "Each island of this shard holds this many items.") + " A full island stops making items.";   // 0.4.20
''')
P.rep('''(en0.length() > 0 ? "Collect gives 1 " + @PKG@.ShTotem.pretty(en0) + " for every 100 " + @PKG@.ShTotem.pretty(@PKG@.ShKind.PROD[kd]) + "." : "With an Auto-Smelt Pole: 1 " + @PKG@.ShTotem.pretty(en1) + " for every 100 ingots.");''',
      '''(en0.length() > 0 ? "Stores 1 " + @PKG@.ShTotem.pretty(en0) + " per 100 made: 100 x the space." : "With an Auto-Smelt Pole: stores 1 " + @PKG@.ShTotem.pretty(en1) + " per 100 ingots.");''')
P.rep('''else if (cm == 0) { this.mTx[@@RCompA@@] = "Next: 1 " + @PKG@.ShTotem.pretty(en0) + " for every 100"; this.mCol[@@RCompA@@] = "@GOOD@"; }''',
      '''else if (cm == 0) { this.mTx[@@RCompA@@] = "Next: stores 100 items as 1 Enchanted"; this.mCol[@@RCompA@@] = "@GOOD@"; }''')
P.rep('''this.mTx[@@RCompA@@] = "Fully upgraded (+" + @PKG@.ShCfg.CMP_STORE + " % storage)";''', '''this.mTx[@@RCompA@@] = "Stores Enchanted (+" + @PKG@.ShCfg.CMP_STORE + " % storage)";''')
P.rep('''", stored " + @PKG@.ShMath.stored(kd, p, i) + " / " + @PKG@.ShMath.capOf(kd, p, i) +''', '''", stored " + @PKG@.ShMath.stored(kd, p, i) + " + " + @PKG@.ShMath.comp(kd, p, i) + " Enchanted / " + @PKG@.ShMath.capOf(kd, p, i) +''')

# ---------------------------------------------------------------------------------------------------- 8. the last "between visits"; the ready line
P.rep('''("shard.maxOfflineSec", "Longest production between visits", "production",''', '''("shard.maxOfflineSec", "Longest online catch-up", "production",''')
P.rep('''"Longest online gap that counts. Also caps Offline Harvest hours (259200 = 3 days)."''', '''"Online: most time one catch-up counts. Also caps Offline Harvest hours (259200 = 3 days)."''')
P.rep('''"Before Automation: longest online gap that counts. Also caps Offline Harvest hours (7200 = 2 h)."''', '''"Before Automation, online: most time one catch-up counts. Also caps Offline hours (7200 = 2 h)."''')
P.rep('''"# shard.maxOfflineSec = the longest stretch between visits that counts at full speed while the owner is online; also''', '''"# shard.maxOfflineSec = the most time one catch-up can count at full speed while the owner is online; also''')
P.rep('''"# shard.manualOfflineSec = before Automation, the longest stretch between visits that counts while the owner is online; also''', '''"# shard.manualOfflineSec = before Automation, the most time one catch-up can count while the owner is online; also''')
P.rep('''log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.19: offline harvest limit, Sell on the Collect tab;''', '''log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.20: smaller storage, true Auto-Compactor, 20 % XP, Mining ingots; 0.4.19: offline harvest limit, Sell on the Collect tab;''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
P.finish()
