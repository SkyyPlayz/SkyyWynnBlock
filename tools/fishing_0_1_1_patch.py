"""Derive SkyyFishing/build_skyyfishing_0.1.1.py + SkyyFishing/test_skyyfishing_0.1.1.py from the LIVE 0.1 scripts (the tools/deploy_set.py
SET pin; 0.1 was a fresh build script, so this patch starts the chain - AGENT-BRIEF patch rule: edit THIS file, never the generated ones).
Run:  python tools/fishing_0_1_1_patch.py   then   python SkyyFishing/build_skyyfishing_0.1.1.py   (never --deploy: coordinated deploy)
      then python SkyyFishing/test_skyyfishing_0.1.1.py   (needs SkyyFishing-0.1.jar, the SET pin, next to it for the class compare)

SKYY'S WORDS (2026-10-09, Fishing Bench PARTS screenshot; docs/answered/skills.md LOCKED 2026-10-09):
  "1 problem. bamboo comes from our zone 5. swap this to sticks for the T1 rod and reel."  +  "and its not pulling from my bags"

0.1.1 =
  (1) T1 WITHOUT BAMBOO: the T1 rod recipe 3 Wood Bamboo Trunk + 6 Fibre + 2 Stick -> 6 Stick + 6 Fibre (the reel stays 4 Stick + 3 Fibre,
      no bamboo; a build assert keeps every bench recipe free of Bamboo). T1 is SHOWN as "Wooden" (Wooden Fishing Rod / Wooden Reel: lang,
      bench rows, the upgrade chain "Copper Fishing Rod needs Wooden Fishing Rod", the rod tooltip's reel line, the RIG tab, /fishing help,
      the Server Setup row labels). Item ids, config keys (fish.rod.bamboo.maxKg, fish.reel.bamboo.power), saved data, art paths unchanged
      (FishDefs.TIERS keeps the id words; the new FishDefs.TIER_SHOWN is display only). LOOK: kept - the T0 rod IS the vanilla
      FishingRod model + texture (the only fishing rod in Assets.zip; its blank is bamboo-coloured wood) - there is no plainer vanilla rod.
      OLD RODS (review fix): a rod made by 0.1 carries its tooltip in its metadata (ItemDisplayMetadata: "Bamboo Fishing Rod",
      "Reel: Bamboo Reel") - every Fishing Bench page build re-stamps such rods in place (FishBench.restamp / FishRig.stale: same id,
      rig, quantity, slot; compare-and-swap), so opening the bench renames them. No saved file changes.
  (3) GAME NAMES (review fix): bench / chat text names vanilla items as the game does ("6 Plant Fiber (12/6)", "Copper Ingot", not
      "Fibre" / "Bar Copper"): FishDefs.VN_ID / VN_NAME are read from Assets.zip's en-US server.lang at build time; pretty() uses them.
  (2) MAGIC BAGS AT THE BENCH: the PARTS tab's counts / Ready / "Missing items" and the CRAFT action use the inventory PLUS the Magic Bags
      you carry through SkyySacks' bag take bridge (0.7.13+, the one SkyyBazaar sells through): sacks:fn:count {UUID, id} -> Long (-1 paused
      = 0 here), sacks:fn:take {UUID, id, qty} -> Long removed, sacks:fn:put (refund, only what a take removed) and sacks:fn:commit (paid:
      leaves the refund ledger). Plain java.lang types through skyy.bridge (FishBridge.bag*). ORDER = SkyyBazaar's and the vanilla bench's
      (bag items show as a nearby chest there): INVENTORY FIRST, then the bags. ATOMIC: every input is taken (inventory re-counted, bags =
      what the take reports) before the part is given; any short take or a failed give rolls everything back (inventory undo + sacks:fn:put;
      what the bags refuse to take back goes to the inventory (committed out of the ledger), a full inventory = a claim, never lost); only a
      given part commits the bag takes. World thread only (the page click / build thread - SkyySacks refuses other threads). SkyySacks absent
      or older (no sacks:fn:take) = inventory only (0.1's behaviour).
      RIG and FILLET AND SELL consume only SkyyFishing_* items (rods, reels, parts, fish), which SkyySacks never stores (homeOf = null: no
      bag type holds them) - nothing to pull from bags there; unchanged. The previous rod / part of an upgrade recipe is ours too: inventory.
  UNCHANGED: every item JSON, the stat, interactions, models, art, classes (same 31 + kit 7), commands, saved files, the fishing loop.
  ROLLBACK 0.1.1 -> 0.1: nothing saved changed; the T1 recipe wants bamboo again and the names say Bamboo.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FISH = os.path.join(ROOT, "SkyyFishing")


def load(name):
    raw = open(os.path.join(FISH, name), "rb").read()
    nl = "\r\n" if b"\r\n" in raw else "\n"
    assert nl == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in " + name
    return raw.decode("utf8").replace("\r\n", "\n"), nl


S = {}


def rep(old, new, count=1):
    assert S["s"].count(old) == count, "anchor count %d != %d: %s" % (S["s"].count(old), count, old[:160])
    S["s"] = S["s"].replace(old, new)


# =========================================================================================================== the build script
s, NL = load("build_skyyfishing_0.1.py")
assert 'VERSION = "0.1"\n' in s and "NEW MOD: stage 1 of research/cloud/SkyyFishing-Spec-Draft.md" in s, "not the live SkyyFishing 0.1 build"
S["s"] = s
REG0 = s.count("registerSystem(")

rep('"""SkyyFishing 0.1 - build script (javassist via jpype). NEW MOD: stage 1 of research/cloud/SkyyFishing-Spec-Draft.md section 12.\n'
    'Run:   python SkyyFishing/build_skyyfishing_0.1.py   -> SkyyFishing/SkyyFishing-0.1.jar\n',
    '"""SkyyFishing 0.1.1 - build script (javassist via jpype). GENERATED by tools/fishing_0_1_1_patch.py from the LIVE build_skyyfishing_0.1.py\n'
    '- edit the patch, never this file. 0.1.1 (Skyy 2026-10-09 "bamboo comes from our zone 5. swap this to sticks for the T1 rod and reel."\n'
    '+ "and its not pulling from my bags"): T1 rod = 6 Stick + 6 Fibre, T1 shown as Wooden Fishing Rod / Wooden Reel (same ids); the bench\n'
    'counts and takes recipe inputs from the inventory first, then the Magic Bags you carry (SkyySacks sacks:fn:count / take / put /\n'
    'commit; atomic with rollback; no SkyySacks = inventory only). Details: tools/fishing_0_1_1_patch.py docstring.\n'
    'Base (0.1): NEW MOD: stage 1 of research/cloud/SkyyFishing-Spec-Draft.md section 12.\n'
    'Run:   python SkyyFishing/build_skyyfishing_0.1.1.py   -> SkyyFishing/SkyyFishing-0.1.1.jar\n')
rep("Check: python SkyyFishing/test_skyyfishing_0.1.py    (-Xverify:all, engine asset validators, every new code path executed, start twice on\n"
    "       a scratch copy of live data, engine-access audit; scratch tools/dev/scratch/fishing01/)",
    "Check: python SkyyFishing/test_skyyfishing_0.1.1.py    (-Xverify:all, engine asset validators, every new code path executed, start twice on\n"
    "       a scratch copy of live data, engine-access audit, class compare with 0.1; scratch tools/dev/scratch/fish011/)")
rep('VERSION = "0.1"\n', 'VERSION = "0.1.1"\n')
# ---- (1) display names: TIER_SHOWN (T1 = Wooden); ids keep the TIERS words
rep('REEL_IDS = ["SkyyFishing_Reel_%s" % t for t in REEL_TIERS]\n',
    'REEL_IDS = ["SkyyFishing_Reel_%s" % t for t in REEL_TIERS]\n'
    '# 0.1.1 (Skyy "bamboo comes from our zone 5"): what players SEE for each tier; T0 is made of sticks now -> "Wooden" (ids, config keys,\n'
    '# art paths keep the TIERS words, so every existing rod / reel / setting stays valid)\n'
    'TIER_SHOWN = ["Wooden"] + TIERS[1:]\n'
    'assert len(TIER_SHOWN) == len(TIERS) and "Bamboo" not in TIER_SHOWN\n')
rep('    ("SkyyFishing_Rod_Bamboo", [("Wood_Bamboo_Trunk", 3), ("Ingredient_Fibre", 6), ("Ingredient_Stick", 2)], None, 0, None),\n',
    '    ("SkyyFishing_Rod_Bamboo", [("Ingredient_Stick", 6), ("Ingredient_Fibre", 6)], None, 0, None),     # 0.1.1: sticks, no bamboo (Zone 5)\n')
rep('assert sorted(r[0] for r in RECIPES) == sorted(ROD_IDS[:3] + REEL_IDS + [p[0] for p in PART_IDS])\n',
    'assert sorted(r[0] for r in RECIPES) == sorted(ROD_IDS[:3] + REEL_IDS + [p[0] for p in PART_IDS])\n'
    'assert not [i for r in RECIPES for i, _q in r[1] if "Bamboo" in i], "0.1.1: no bench recipe may need bamboo (it only grows in Zone 5)"\n')
rep('    name_lines(iid, "%s Fishing Rod" % tier, "Max fish weight',
    '    name_lines(iid, "%s Fishing Rod" % TIER_SHOWN[ti], "Max fish weight')
rep('    part_item(REEL_IDS[ri], "reel-t%d-%s.png" % (ri, t.lower()), "%s Reel" % t,',
    '    part_item(REEL_IDS[ri], "reel-t%d-%s.png" % (ri, t.lower()), "%s Reel" % TIER_SHOWN[ri],')
rep('"%s rod max fish weight" % TIERS[i]', '"%s rod max fish weight" % TIER_SHOWN[i]')
rep('"%s reel power" % REEL_TIERS[i]', '"%s reel power" % TIER_SHOWN[i]')
rep('        "public static final String[] TIERS = %s;" % jarr(TIERS),\n',
    '        "public static final String[] TIERS = %s;" % jarr(TIERS),\n'
    '        "public static final String[] TIER_SHOWN = %s;" % jarr(TIER_SHOWN),\n')
rep('  if (r > 0) return TIERS[r - 1] + " Reel";', '  if (r > 0) return TIER_SHOWN[r - 1] + " Reel";')
rep('  return TIERS[ri] + " Fishing Rod";', '  return TIER_SHOWN[ri] + " Fishing Rod";')
rep('  l.add("Reel: " + (reel > 0 ? @PKG@.FishDefs.TIERS[reel - 1] + " Reel (power "',
    '  l.add("Reel: " + (reel > 0 ? @PKG@.FishDefs.TIER_SHOWN[reel - 1] + " Reel (power "')
rep('  return (reel > 0 ? @PKG@.FishDefs.TIERS[reel - 1] + " reel" : "no reel")',
    '  return (reel > 0 ? @PKG@.FishDefs.TIER_SHOWN[reel - 1] + " reel" : "no reel")')
rep('name=J_("nm", "Bamboo Fishing Rod"), sub=J_("sb", "Reel: Bamboo"))', 'name=J_("nm", "Wooden Fishing Rod"), sub=J_("sb", "Reel: Wooden"))')
rep('sub=J_("sb", "Bamboo Reel"), action="Remove")', 'sub=J_("sb", "Wooden Reel"), action="Remove")')
rep('make a Bamboo Fishing Rod there, then right click water', 'make a Wooden Fishing Rod there (sticks + fibre), then right click water')

# ---- (2) Magic Bags: FishBridge.bag* (SkyySacks 0.7.13+ bag take bridge) after skillXp
BRIDGE_ANCHOR = '''  Object r = fn("skill:fn:addxp", new Object[] { u, "Fishing", Long.valueOf(xp), "fishing", key });
  return Boolean.TRUE.equals(r);
}""")
'''
rep(BRIDGE_ANCHOR, BRIDGE_ANCHOR + r'''# 0.1.1 MAGIC BAGS (Skyy "and its not pulling from my bags"): SkyySacks 0.7.13+'s bag take bridge (the one SkyyBazaar sells through).
# sacks:fn:count {UUID, id} -> Long takeable now (-1 paused), sacks:fn:take {UUID, id, Long} -> Long removed (0..qty), sacks:fn:put {UUID,
# id, Long} -> Long returned (only what a take removed, 60 s), sacks:fn:commit {UUID, id, Long} -> Long (paid: leaves the refund ledger).
# World thread only (SkyySacks refuses other threads). No SkyySacks / one without sacks:fn:take = no bags: counts 0, takes 0.
M(BRG, "public static boolean bagsOn() { return has(\"sacks:fn:count\") && has(\"sacks:fn:take\"); }")
M(BRG, r"""
public static long bagCall(String key, Object arg) {
  Object r = fn(key, arg);
  return r instanceof Number ? ((Number) r).longValue() : -2L;
}""")
M(BRG, r"""
public static int bagCount(java.util.UUID u, String id) {
  if (u == null || id == null || !bagsOn()) return 0;
  long r = bagCall("sacks:fn:count", new Object[] { u, id });
  if (r <= 0L) return 0;
  return r > 1000000000L ? 1000000000 : (int) r;
}""")
M(BRG, r"""
public static int bagTake(java.util.UUID u, String id, int n) {
  if (u == null || id == null || n <= 0 || !bagsOn()) return 0;
  long r = bagCall("sacks:fn:take", new Object[] { u, id, Long.valueOf((long) n) });
  if (r <= 0L) return 0;
  if (r > (long) n) @PKG@.FishLog.warn("SkyySacks removed " + r + " " + id + " when " + n + " were asked (bench craft)");
  return r > 1000000000L ? 1000000000 : (int) r;
}""")
M(BRG, r"""
public static int bagPut(java.util.UUID u, String id, int n) {
  if (u == null || id == null || n <= 0) return 0;
  long r = bagCall("sacks:fn:put", new Object[] { u, id, Long.valueOf((long) n) });
  if (r <= 0L) return 0;
  return r > (long) n ? n : (int) r;
}""")
M(BRG, r"""
public static int bagCommit(java.util.UUID u, String id, int n) {
  if (u == null || id == null || n <= 0) return 0;
  long r = bagCall("sacks:fn:commit", new Object[] { u, id, Long.valueOf((long) n) });
  if (r <= 0L) return 0;
  return r > (long) n ? n : (int) r;
}""")
''')

# ---- FishBench: have() = inventory + bags; needText / state count both; craft takes inventory first, then bags, atomic
OLD_NEED = r'''M(BENCH, r"""
public static String needText(@IC@ inv, int r) {
  StringBuilder b = new StringBuilder();
  String prev = @PKG@.FishDefs.R_PREV[r];
  if (prev.length() > 0) b.append(name(prev)).append(" (").append(count(inv, prev) > 0 ? "have" : "missing").append(")");
  for (int i = @PKG@.FishDefs.R_START[r]; i < @PKG@.FishDefs.R_START[r + 1]; i++) {
    if (b.length() > 0) b.append(", ");
    String id = @PKG@.FishDefs.R_IN[i];
    b.append(@PKG@.FishDefs.R_INQ[i]).append(' ').append(@PKG@.FishDefs.pretty(id)).append(" (").append(Math.min(count(inv, id), 9999)).append('/').append(@PKG@.FishDefs.R_INQ[i]).append(')');
  }
  return b.toString();
}""")
# 0 ready, 1 locked, 2 missing items
M(BENCH, r"""
public static int state(@IC@ inv, java.util.UUID u, String key, int r) {
  if (gate(u, key, r) != 0) return 1;
  String prev = @PKG@.FishDefs.R_PREV[r];
  if (prev.length() > 0 && count(inv, prev) < 1) return 2;
  for (int i = @PKG@.FishDefs.R_START[r]; i < @PKG@.FishDefs.R_START[r + 1]; i++) if (count(inv, @PKG@.FishDefs.R_IN[i]) < @PKG@.FishDefs.R_INQ[i]) return 2;
  return 0;
}""")
'''
NEW_NEED = r'''# 0.1.1: a recipe input you have = the inventory + the Magic Bags you carry (SkyySacks; none = the inventory alone)
M(BENCH, r"""
public static int have(@IC@ inv, java.util.UUID u, String id) {
  long n = (long) count(inv, id) + (long) @PKG@.FishBridge.bagCount(u, id);
  return n > 1000000000L ? 1000000000 : (int) n;
}""")
M(BENCH, r"""
public static String needText(@IC@ inv, java.util.UUID u, int r) {
  StringBuilder b = new StringBuilder();
  String prev = @PKG@.FishDefs.R_PREV[r];
  if (prev.length() > 0) b.append(name(prev)).append(" (").append(count(inv, prev) > 0 ? "have" : "missing").append(")");
  for (int i = @PKG@.FishDefs.R_START[r]; i < @PKG@.FishDefs.R_START[r + 1]; i++) {
    if (b.length() > 0) b.append(", ");
    String id = @PKG@.FishDefs.R_IN[i];
    b.append(@PKG@.FishDefs.R_INQ[i]).append(' ').append(@PKG@.FishDefs.pretty(id)).append(" (").append(Math.min(have(inv, u, id), 9999)).append('/').append(@PKG@.FishDefs.R_INQ[i]).append(')');
  }
  return b.toString();
}""")
M(BENCH, "public static String needText(@IC@ inv, int r) { return needText(inv, (java.util.UUID) null, r); }")
# 0 ready, 1 locked, 2 missing items (0.1.1: inputs counted with the bags; the previous rod / part = ours, never in a bag: inventory)
M(BENCH, r"""
public static int state(@IC@ inv, java.util.UUID u, String key, int r) {
  if (gate(u, key, r) != 0) return 1;
  String prev = @PKG@.FishDefs.R_PREV[r];
  if (prev.length() > 0 && count(inv, prev) < 1) return 2;
  for (int i = @PKG@.FishDefs.R_START[r]; i < @PKG@.FishDefs.R_START[r + 1]; i++) if (have(inv, u, @PKG@.FishDefs.R_IN[i]) < @PKG@.FishDefs.R_INQ[i]) return 2;
  return 0;
}""")
# 0.1.1 the bag part of a craft: bl = { id, Integer taken } per bag take. bagUndo = the rollback (sacks:fn:put; what the bags do not take
# back is committed out of SkyySacks' ledger and goes to the inventory, a full one = a claim - never lost); bagDone = paid (commit).
M(BENCH, r"""
public static void bagUndo(@IC@ inv, java.util.UUID u, String key, java.util.ArrayList bl) {
  for (int i = 0; i < bl.size(); i++) {
    Object[] e = (Object[]) bl.get(i);
    String id = (String) e[0];
    int n = ((Integer) e[1]).intValue();
    int back = @PKG@.FishBridge.bagPut(u, id, n);
    int rest = n - back;
    if (rest <= 0) continue;
    @PKG@.FishBridge.bagCommit(u, id, rest);
    if (!@PKG@.FishCore.give(inv, new @IS@(id, rest))) {
      if (key != null) @PKG@.FishStore.addClaim(key, "I|" + id + "|" + rest);
      @PKG@.FishLog.warn("bench craft rollback: " + rest + " " + id + " could not go back to the bags or the inventory of " + u + " - kept as a claim");
    }
  }
  bl.clear();
}""")
M(BENCH, r"""
public static void bagDone(java.util.UUID u, java.util.ArrayList bl) {
  for (int i = 0; i < bl.size(); i++) {
    Object[] e = (Object[]) bl.get(i);
    @PKG@.FishBridge.bagCommit(u, (String) e[0], ((Integer) e[1]).intValue());
  }
  bl.clear();
}""")
'''
rep(OLD_NEED, NEW_NEED)
rep('  if (state(inv, u, key, r) != 0) return "-Missing items for the " + name(out) + ": " + needText(inv, r);',
    '  if (state(inv, u, key, r) != 0) return "-Missing items for the " + name(out) + ": " + needText(inv, u, r);')
rep('''  for (int i = @PKG@.FishDefs.R_START[r]; i < @PKG@.FishDefs.R_START[r + 1]; i++) {
    if (!take(inv, @PKG@.FishDefs.R_IN[i], @PKG@.FishDefs.R_INQ[i], ul)) { undo(inv, ul); return "-Your inventory changed - nothing was used. Try again."; }
  }
  @IS@ made = new @IS@(out, 1);
  if (@PKG@.FishDefs.rodIndex(out) >= 0) made = @PKG@.FishRig.withRig(made, rig);
  if (!@PKG@.FishCore.give(inv, made)) { undo(inv, ul); return "-No room for the " + name(out) + " - nothing was used."; }
''', '''  java.util.ArrayList bl = new java.util.ArrayList();
  for (int i = @PKG@.FishDefs.R_START[r]; i < @PKG@.FishDefs.R_START[r + 1]; i++) {
    String id = @PKG@.FishDefs.R_IN[i];
    int need = @PKG@.FishDefs.R_INQ[i];
    int inInv = count(inv, id);
    int fromInv = need < inInv ? need : inInv;
    if (fromInv > 0 && !take(inv, id, fromInv, ul)) { undo(inv, ul); bagUndo(inv, u, key, bl); return "-Your inventory changed - nothing was used. Try again."; }
    int rest = need - fromInv;
    if (rest > 0) {
      int got = @PKG@.FishBridge.bagTake(u, id, rest);
      if (got > 0) bl.add(new Object[] { id, Integer.valueOf(got) });
      if (got < rest) { undo(inv, ul); bagUndo(inv, u, key, bl); return "-Your bags changed - nothing was used. Try again."; }
    }
  }
  @IS@ made = new @IS@(out, 1);
  if (@PKG@.FishDefs.rodIndex(out) >= 0) made = @PKG@.FishRig.withRig(made, rig);
  if (!@PKG@.FishCore.give(inv, made)) { undo(inv, ul); bagUndo(inv, u, key, bl); return "-No room for the " + name(out) + " - nothing was used."; }
  bagDone(u, bl);
''')
rep('      String sb = @PKG@.FishBench.needText(inv, i);', '      String sb = @PKG@.FishBench.needText(inv, u, i);')

# ---- (3) review fix: the game's own item names in the bench / chat text ("6 Plant Fiber (12/6)", not "6 Fibre"): read from Assets.zip's
# en-US server.lang at BUILD time (never committed) for every vanilla item we name (bench inputs, junk, treasure, fillets); pretty() uses them
rep('_RIN, _RQ, _RS = _flat_recipes()\n', '''_RIN, _RQ, _RS = _flat_recipes()
# 0.1.1: the names the game shows for the vanilla items our text names (bench inputs, junk, treasure, fillets) - Assets.zip's en-US
# server.lang, read at build time (never committed). FishDefs.pretty() uses them ("Plant Fiber" - what the game and SkyySacks call it)
_VLANG = {}
for _ln in az.read("Server/Languages/en-US/server.lang").decode("utf-8-sig").splitlines():
    if _ln.startswith("items.") and "=" in _ln:
        _k, _v = _ln.split("=", 1)
        _k, _v = _k.strip(), _v.strip()
        if _k.endswith(".name") and _v and all(32 <= ord(_c) < 127 for _c in _v):
            _VLANG[_k[len("items."):-len(".name")]] = _v
_VN_ALL = sorted(set(_RIN + [j for j, _w in JUNK_Z1] + FILLET_ITEMS + [i for _g, _n, rows in TREASURE for row in rows for i in row[4]]))
VN_ID = [i for i in _VN_ALL if i in _VLANG]
VN_NAME = [_VLANG[i] for i in VN_ID]
assert set(_RIN) <= set(VN_ID), "a bench input has no vanilla name: %s" % sorted(set(_RIN) - set(VN_ID))
assert _VLANG.get("Ingredient_Fibre") == "Plant Fiber" and _VLANG.get("Ingredient_Stick") == "Stick", "vanilla names moved"
''')
rep('        "public static final String[] R_IN = %s;" % jarr(_RIN),\n',
    '        "public static final String[] R_IN = %s;" % jarr(_RIN),\n'
    '        "public static final String[] VN_ID = %s;" % jarr(VN_ID),\n'
    '        "public static final String[] VN_NAME = %s;" % jarr(VN_NAME),\n')
rep('''public static String pretty(String id) {
  if (id == null) return "?";
  String s = id;''', '''public static String pretty(String id) {
  if (id == null) return "?";
  for (int i = 0; i < VN_ID.length; i++) if (VN_ID[i].equals(id)) return VN_NAME[i];
  String s = id;''')

# ---- (4) review fix: a rod made by 0.1 keeps "Bamboo Fishing Rod" / "Reel: Bamboo Reel" in its stored tooltip (ItemDisplayMetadata).
# The bench re-stamps such rods (same id, same rig, same quantity; only the tooltip is rewritten) every time its page builds - opening the
# bench, every tab, every rebuild - before the RIG list reads the rods (so the click signatures are taken from the re-stamped stacks).
# Compare-and-swap (replaceItemStackInSlot with the stack just read): a moved stack is left alone. World thread (the page build).
rep('''M(RIG, r"""
public static String[] freshRig(String rodId) {''', '''M(RIG, r"""
public static boolean stale(@IS@ s) {
  try {
    if (s == null || s.isEmpty() || @PKG@.FishDefs.rodIndex(s.getItemId()) < 0 || doc(s) == null) return false;
    @BD@ m = s.getMetadata();
    String j = m == null ? "" : m.toJson();
    return j.indexOf("Bamboo Fishing Rod") >= 0 || j.indexOf("Bamboo Reel") >= 0;
  } catch (Throwable t) { return false; }
}""")
M(RIG, r"""
public static String[] freshRig(String rodId) {''')
rep('''M(BENCH, r"""
public static boolean sameAt(@IC@ inv, int slot, String sig) {''', '''# 0.1.1 review fix: 0.1 rods still named Bamboo in their stored tooltip -> re-stamped (same id / rig / quantity), returns how many
M(BENCH, r"""
public static int restamp(@IC@ inv) {
  if (inv == null) return 0;
  int n = 0;
  try {
    int cap = inv.getCapacity();
    for (int i = 0; i < cap; i++) {
      @IS@ s = inv.getItemStack((short) i);
      if (!@PKG@.FishRig.stale(s)) continue;
      @ISST@ rx = inv.replaceItemStackInSlot((short) i, s, @PKG@.FishRig.withRig(s, @PKG@.FishRig.rigOf(s)));
      if (rx != null && rx.succeeded()) n++;
    }
  } catch (Throwable t) { @PKG@.FishLog.warnOnce("restamp:" + t.getClass().getName(), "could not re-name an old Bamboo rod: " + t); }
  return n;
}""")
M(BENCH, r"""
public static boolean sameAt(@IC@ inv, int slot, String sig) {''')
rep('''  try { inv = @PKG@.FishEng.API == null ? null : @PKG@.FishEng.API.inv(c); } catch (Throwable ti) { inv = null; }
  String key = @PKG@.FishBridge.pkey(u);''', '''  try { inv = @PKG@.FishEng.API == null ? null : @PKG@.FishEng.API.inv(c); } catch (Throwable ti) { inv = null; }
  if (inv != null) @PKG@.FishBench.restamp(inv);
  String key = @PKG@.FishBridge.pkey(u);''')
assert S["s"].count("registerSystem(") == REG0
open(os.path.join(FISH, "build_skyyfishing_0.1.1.py"), "w", encoding="utf8", newline=NL).write(S["s"])

# =========================================================================================================== the harness
t, TNL = load("test_skyyfishing_0.1.py")
assert 'VERSION = "0.1"\n' in t and "Harness for SkyyFishing 0.1. " in t, "not the live 0.1 harness"
S["s"] = t
rep('"""Harness for SkyyFishing 0.1. Build first: python SkyyFishing/build_skyyfishing_0.1.py\n\n'
    '    python SkyyFishing/test_skyyfishing_0.1.py [--jar <SkyyFishing-0.1.jar>] [--live <a world folder>] [--keep]\n',
    '"""Harness for SkyyFishing 0.1.1 (GENERATED by tools/fishing_0_1_1_patch.py from test_skyyfishing_0.1.py - edit the patch).\n'
    'Build first: python SkyyFishing/build_skyyfishing_0.1.1.py\n\n'
    '    python SkyyFishing/test_skyyfishing_0.1.1.py [--jar <SkyyFishing-0.1.1.jar>] [--live <a world folder>] [--keep]\n\n'
    '0.1.1 adds: R  the T1 recipe = sticks + fibre (no bamboo anywhere), every recipe input is an Assets.zip item, T1 shown as Wooden\n'
    '              (lang + FishDefs.TIER_SHOWN + the upgrade chain text);\n'
    '            C2 CLASS COMPARE vs SkyyFishing-0.1.jar (the SET pin): same classes, same item / stat / model / art files byte for byte,\n'
    '              lang differs only in the 4 T1 name lines, method / field diff = exactly the new bag + display members;\n'
    '            X16 MAGIC BAGS on REAL containers with a SkyySacks bridge stand-in (the 0.7.13 contract: count / take / put / commit):\n'
    '              counts split between inventory and bags, inventory first, exact amounts, every rollback (short take, no room, put\n'
    '              refused -> inventory / claim), paused bags, SkyySacks absent = inventory only, the page build + craft click with bags.\n')
rep('Scratch: tools/dev/scratch/fishing01/test (deleted', 'Scratch: tools/dev/scratch/fish011/test (deleted')
rep('VERSION = "0.1"\n', 'VERSION = "0.1.1"\nOLD_JAR = os.path.join(HERE, "SkyyFishing-0.1.jar")      # the SET pin (class compare C2)\n')
rep('os.path.join(TOOLS, "dev", "scratch", "fishing01", "test")', 'os.path.join(TOOLS, "dev", "scratch", "fish011", "test")')
# X12: the T1 rod from sticks
rep('''    add("Wood_Bamboo_Trunk", 3)
    add("Ingredient_Fibre", 7)
    add("Ingredient_Stick", 2)
''', '''    add("Ingredient_Fibre", 7)
    add("Ingredient_Stick", 6)
''')
rep('''    K.check(r.startswith("+Crafted") and rstack is not None and int(Rig.reelOf(Rig.rigOf(rstack))) == 1 and count_in(inv, "Wood_Bamboo_Trunk", Bench) == 0
            and count_in(inv, "Ingredient_Fibre", Bench) == 1 and count_in(inv, "Ingredient_Stick", Bench) == 0,
            "X12: Bamboo Fishing Rod crafted: exactly 3 bamboo + 6 fibre + 2 sticks taken, the rod comes with its Bamboo reel fitted: %s" % r)''',
    '''    K.check(r.startswith("+Crafted the Wooden Fishing Rod") and rstack is not None and int(Rig.reelOf(Rig.rigOf(rstack))) == 1
            and count_in(inv, "Ingredient_Fibre", Bench) == 1 and count_in(inv, "Ingredient_Stick", Bench) == 0,
            "X12: Wooden Fishing Rod (id SkyyFishing_Rod_Bamboo) crafted: exactly 6 sticks + 6 fibre taken, no bamboo, the rod comes with its "
            "Wooden reel fitted: %s" % r)''')
rep('''    K.check(str(Bench.craft(inv, U1, key, 2)).startswith("-Locked") and "Pond Fish III" in str(Bench.craft(inv, U1, key, 2)),''',
    '''    _cl = str(Bench.craft(inv, U1, key, 2))
    K.check("Copper Fishing Rod needs" in _cl and str(Bench.needText(inv, U1, 2)).startswith("Wooden Fishing Rod (have)")
            and str(Defs.rodName(0)) == "Wooden Fishing Rod" and str(Defs.partName("SkyyFishing_Reel_Bamboo")) == "Wooden Reel"
            and "Wooden Reel" in "".join(str(x) for x in Rig.rodLines(1, Rig.rigOf(rstack))),
            "X12 0.1.1: the upgrade chain says Wooden (Copper Fishing Rod needs ... / Wooden Fishing Rod (have)), rod + reel + tooltip names: %s" % _cl)
    K.check(str(Bench.craft(inv, U1, key, 2)).startswith("-Locked") and "Pond Fish III" in str(Bench.craft(inv, U1, key, 2)),''')
rep('"X13: page craft (Bamboo Reel) through handleDataEvent: %s" % r)', '"X13: page craft (Wooden Reel) through handleDataEvent: %s" % r)')

# X16: the Magic Bags block, inserted before the X13 page tests (the stand-in stays installed with an EMPTY pool afterwards, so the page
# build / craft clicks of X13 run the bag code path too)
X16 = r'''    # ============================================================================ X16 (0.1.1) MAGIC BAGS: SkyySacks' bag bridge stand-in
    import zipfile as _zf
    _az = _zf.ZipFile(ASSETS)
    _vitems = set(n.rsplit("/", 1)[1][:-5] for n in _az.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    _rin = [str(x) for x in Defs.R_IN]
    K.check(all(i in _vitems for i in _rin) and not [i for i in _rin if "Bamboo" in i]
            and _rin[int(Defs.R_START[0]):int(Defs.R_START[1])] == ["Ingredient_Stick", "Ingredient_Fibre"]
            and [int(x) for x in Defs.R_INQ][int(Defs.R_START[0]):int(Defs.R_START[1])] == [6, 6]
            and _rin[int(Defs.R_START[1]):int(Defs.R_START[2])] == ["Ingredient_Stick", "Ingredient_Fibre"],
            "X16 R: every recipe input is an Assets.zip item, none is bamboo; T1 rod = 6 Stick + 6 Fibre, T1 reel = Stick + Fibre")
    K.check(not bool(Brg.bagsOn()) and int(Brg.bagCount(U1, "Ingredient_Stick")) == 0 and int(Brg.bagTake(U1, "Ingredient_Stick", 3)) == 0,
            "X16: SkyySacks absent = no bags (count 0, take 0) - X12 above ran the inventory-only crafts")
    BAG = {"pool": {}, "owed": {}, "log": [], "paused": False, "steal": 0, "put_ok": True}

    def _a(a):
        return str(a[1]), (int(a[2]) if len(a) > 2 else 0)

    @JImplements("java.util.function.Function")
    class SackCount:
        @JOverride
        def apply(self, a):
            i, _n = _a(a)
            BAG["log"].append(("count", i))
            return JLong(-1 if BAG["paused"] else BAG["pool"].get(i, 0))

    @JImplements("java.util.function.Function")
    class SackTake:
        @JOverride
        def apply(self, a):
            i, n = _a(a)
            if BAG["steal"]:
                BAG["pool"][i] = max(0, BAG["pool"].get(i, 0) - BAG["steal"])
                BAG["steal"] = 0
            t_ = min(n, BAG["pool"].get(i, 0))
            BAG["pool"][i] = BAG["pool"].get(i, 0) - t_
            BAG["owed"][i] = BAG["owed"].get(i, 0) + t_
            BAG["log"].append(("take", i, n, t_))
            return JLong(t_)

    @JImplements("java.util.function.Function")
    class SackPut:
        @JOverride
        def apply(self, a):
            i, n = _a(a)
            t_ = min(n, BAG["owed"].get(i, 0)) if BAG["put_ok"] else 0
            BAG["owed"][i] = BAG["owed"].get(i, 0) - t_
            BAG["pool"][i] = BAG["pool"].get(i, 0) + t_
            BAG["log"].append(("put", i, n, t_))
            return JLong(t_)

    @JImplements("java.util.function.Function")
    class SackCommit:
        @JOverride
        def apply(self, a):
            i, n = _a(a)
            t_ = min(n, BAG["owed"].get(i, 0))
            BAG["owed"][i] = BAG["owed"].get(i, 0) - t_
            BAG["log"].append(("commit", i, n, t_))
            return JLong(t_)
    bridge.put("sacks:fn:count", SackCount())
    bridge.put("sacks:fn:take", SackTake())
    bridge.put("sacks:fn:put", SackPut())
    bridge.put("sacks:fn:commit", SackCommit())
    SH = JClass("java.lang.Short")

    def binv(n, *stacks):
        c = SIC(SH(n).shortValue())
        for i_, q_ in stacks:
            c.addItemStack(IS(i_, q_))
        return c

    def reset(pool):
        BAG["pool"], BAG["owed"], BAG["log"], BAG["paused"], BAG["steal"], BAG["put_ok"] = dict(pool), {}, [], False, 0, True
    Store_.setPond(key, 0)
    # (a) split: 2 sticks in the inventory + 10 in the bags, 6 fibre in the inventory -> Ready, the text counts both, the craft takes the 2
    #     inventory sticks FIRST, then 4 from the bags (committed: paid)
    reset({"Ingredient_Stick": 10})
    b1 = binv(20, ("Ingredient_Stick", 2), ("Ingredient_Fibre", 6))
    K.check(bool(Brg.bagsOn()) and int(Bench.have(b1, U1, "Ingredient_Stick")) == 12 and int(Bench.state(b1, U1, key, 0)) == 0
            and "(12/6)" in str(Bench.needText(b1, U1, 0)) and "(2/6)" in str(Bench.needText(b1, 0)),
            "X16 (a): the bench counts inventory + bags: 6 Stick (12/6) -> Ready; needText without a player = the inventory (2/6): %s"
            % Bench.needText(b1, U1, 0))
    r = str(Bench.craft(b1, U1, key, 0))
    takes = [e for e in BAG["log"] if e[0] == "take"]
    K.check(r.startswith("+Crafted the Wooden Fishing Rod") and count_in(b1, "Ingredient_Stick", Bench) == 0 and count_in(b1, "Ingredient_Fibre", Bench) == 0
            and BAG["pool"]["Ingredient_Stick"] == 6 and takes == [("take", "Ingredient_Stick", 4, 4)] and BAG["owed"].get("Ingredient_Stick") == 0
            and ("commit", "Ingredient_Stick", 4, 4) in BAG["log"] and count_in(b1, "SkyyFishing_Rod_Bamboo", Bench) == 1,
            "X16 (a): craft = 2 sticks from the inventory first, exactly 4 from the bags, 6 fibre from the inventory, the bag take committed, "
            "the rod given: %s %s" % (r, BAG["log"]))
    # (b) inventory first: 8 sticks + 6 fibre in the inventory, 10 in the bags -> the bags are never touched
    reset({"Ingredient_Stick": 10, "Ingredient_Fibre": 10})
    b2 = binv(20, ("Ingredient_Stick", 8), ("Ingredient_Fibre", 6))
    r = str(Bench.craft(b2, U1, key, 0))
    K.check(r.startswith("+Crafted") and count_in(b2, "Ingredient_Stick", Bench) == 2 and BAG["pool"] == {"Ingredient_Stick": 10, "Ingredient_Fibre": 10}
            and not [e for e in BAG["log"] if e[0] in ("take", "put", "commit")],
            "X16 (b): enough in the inventory = the bags are not touched (inventory first)")
    # (c) everything from the bags (empty-ish inventory) + the reel recipe
    reset({"Ingredient_Stick": 4, "Ingredient_Fibre": 3})
    b3 = binv(20)
    r = str(Bench.craft(b3, U1, key, 1))
    K.check(r.startswith("+Crafted the Wooden Reel") and BAG["pool"] == {"Ingredient_Stick": 0, "Ingredient_Fibre": 0}
            and count_in(b3, "SkyyFishing_Reel_Bamboo", Bench) == 1 and sorted(e[1] for e in BAG["log"] if e[0] == "commit") == ["Ingredient_Fibre", "Ingredient_Stick"],
            "X16 (c): Wooden Reel crafted entirely from the bags (4 Stick + 3 Fibre), both takes committed: %s" % r)
    # (d) not enough in total -> Missing items, nothing taken anywhere
    reset({"Ingredient_Stick": 3})
    b4 = binv(20, ("Ingredient_Stick", 2), ("Ingredient_Fibre", 6))
    r = str(Bench.craft(b4, U1, key, 0))
    K.check(r.startswith("-Missing items for the Wooden Fishing Rod") and "(5/6)" in r and count_in(b4, "Ingredient_Stick", Bench) == 2
            and BAG["pool"]["Ingredient_Stick"] == 3 and not [e for e in BAG["log"] if e[0] == "take"],
            "X16 (d): 2 + 3 sticks < 6 = 'Missing items' (5/6), nothing taken: %s" % r)
    # (e) ROLLBACK: the bags change between the count and the take (short take) -> the inventory sticks + fibre come back, the bag part is put back
    reset({"Ingredient_Stick": 10})
    BAG["steal"] = 9
    b5 = binv(20, ("Ingredient_Stick", 2), ("Ingredient_Fibre", 6))
    r = str(Bench.craft(b5, U1, key, 0))
    K.check(r.startswith("-Your bags changed") and count_in(b5, "Ingredient_Stick", Bench) == 2 and count_in(b5, "Ingredient_Fibre", Bench) == 6
            and BAG["pool"]["Ingredient_Stick"] == 1 and BAG["owed"].get("Ingredient_Stick") == 0 and count_in(b5, "SkyyFishing_Rod_Bamboo", Bench) == 0
            and ("put", "Ingredient_Stick", 1, 1) in BAG["log"],
            "X16 (e): a short bag take rolls back: inventory 2 Stick + 6 Fibre again, the 1 taken stick put back in the bag, no rod: %s %s" % (r, BAG["log"]))
    # (f) ROLLBACK: no room for the part (all inputs from the bags, the 1-slot inventory is full) -> every bag take put back
    reset({"Ingredient_Stick": 6, "Ingredient_Fibre": 6})
    b6 = binv(1, ("Rock_Stone_Cobble", 1))
    r = str(Bench.craft(b6, U1, key, 0))
    K.check(r.startswith("-No room for the Wooden Fishing Rod") and BAG["pool"] == {"Ingredient_Stick": 6, "Ingredient_Fibre": 6}
            and not [e for e in BAG["log"] if e[0] == "commit"] and count_in(b6, "Rock_Stone_Cobble", Bench) == 1,
            "X16 (f): no room for the rod = both bag takes put back, nothing committed, nothing given: %s" % r)
    # (g) ROLLBACK where the bags refuse the put (e.g. SkyySacks reloaded): the items go to the inventory (committed out of the ledger)
    reset({"Ingredient_Stick": 10})
    BAG["steal"], BAG["put_ok"] = 9, False
    b7 = binv(20, ("Ingredient_Stick", 2), ("Ingredient_Fibre", 6))
    r = str(Bench.craft(b7, U1, key, 0))
    K.check(r.startswith("-Your bags changed") and count_in(b7, "Ingredient_Stick", Bench) == 3 and count_in(b7, "Ingredient_Fibre", Bench) == 6
            and ("commit", "Ingredient_Stick", 1, 1) in BAG["log"] and BAG["owed"].get("Ingredient_Stick") == 0,
            "X16 (g): a refused put = the taken stick goes to the inventory instead (2 + 1), committed out of the refund ledger: %s" % BAG["log"])
    # (h) ... and with a full inventory too: a claim (handed over later), never lost
    reset({"Ingredient_Stick": 6, "Ingredient_Fibre": 6})
    BAG["put_ok"] = False
    b8 = binv(1, ("Rock_Stone_Cobble", 1))
    cl0 = len(list(Store_.claims(key)))
    r = str(Bench.craft(b8, U1, key, 0))
    cls_ = [str(x) for x in Store_.claims(key)][cl0:]
    K.check(r.startswith("-No room") and sorted(cls_) == ["I|Ingredient_Fibre|6", "I|Ingredient_Stick|6"],
            "X16 (h): bags refuse the put AND the inventory is full = the inputs become claims (handed over later): %s" % cls_)
    for c_ in cls_:
        Store_.dropClaim(key, c_)
    # (i) paused bags (SkyySacks answers -1 during a profile switch) = the inventory alone
    reset({"Ingredient_Stick": 10})
    BAG["paused"] = True
    b9 = binv(20, ("Ingredient_Stick", 2), ("Ingredient_Fibre", 6))
    K.check(int(Bench.have(b9, U1, "Ingredient_Stick")) == 2 and int(Bench.state(b9, U1, key, 0)) == 2
            and str(Bench.craft(b9, U1, key, 0)).startswith("-Missing") and not [e for e in BAG["log"] if e[0] == "take"],
            "X16 (i): paused bags count 0 -> Missing items, nothing taken")
    # (j) the bags do not hold our own items: an upgrade recipe's previous rod stays an inventory check (no bag call for it)
    reset({"SkyyFishing_Rod_Bamboo": 1, "Ingredient_Bar_Copper": 6, "Ingredient_Fibre": 8})
    Store_.setPond(key, 100)
    b10 = binv(20)
    K.check(int(Bench.state(b10, U1, key, 2)) == 2 and "Wooden Fishing Rod (missing)" in str(Bench.needText(b10, U1, 2))
            and not [e for e in BAG["log"] if e[1] == "SkyyFishing_Rod_Bamboo"],
            "X16 (j): the Copper rod's previous rod is looked for in the inventory only (never asked of the bags)")
    # (k) metals from the bags for an upgrade: Wooden rod in the inventory, 6 copper bars + 8 fibre in the bags -> the rig moves over
    b10.addItemStack(Rig.withRig(IS("SkyyFishing_Rod_Bamboo", 1), JArray(JString)(["1", "SkyyFishing_Hook_Barbed_I", "", ""])))
    r = str(Bench.craft(b10, U1, key, 2))
    cs_ = int(Bench.firstSlot(b10, "SkyyFishing_Rod_Copper"))
    K.check(r.startswith("+Crafted the Copper Fishing Rod") and cs_ >= 0 and BAG["pool"]["Ingredient_Bar_Copper"] == 0 and BAG["pool"]["Ingredient_Fibre"] == 0
            and str(Rig.rigOf(b10.getItemStack(SH(cs_).shortValue()))[1]) == "SkyyFishing_Hook_Barbed_I" and count_in(b10, "SkyyFishing_Rod_Bamboo", Bench) == 0,
            "X16 (k): Copper rod from the Wooden rod (inventory) + bars and fibre from the bags; its hook moved over: %s" % r)
    Store_.setPond(key, 0)
    reset({})
    K.notes.append("X16: bag bridge stand-in (SkyySacks 0.7.13 contract) - %d bench crafts with bags" % 11)
'''
rep("    # ============================================================================ X13 the bench PAGE (stand-in subclass: rebuild / close recorded)\n",
    X16 + "    # ============================================================================ X13 the bench PAGE (stand-in subclass: rebuild / close recorded)\n")
# X13 page with bags: the stand-in stays installed (empty pool); after the page's own craft, one craft click pulled from the bags
rep('''    K.check(r.startswith("=The page changed"), "X13: the same click sent twice (double click: the old token) does nothing the 2nd time")
    tok = str(pg.tok)
''', '''    K.check(r.startswith("=The page changed"), "X13: the same click sent twice (double click: the old token) does nothing the 2nd time")
    tok = str(pg.tok)
    # 0.1.1: the page (build + craft click) with the reel's inputs only in the bags
    BAG["pool"], BAG["log"] = {"Ingredient_Stick": 4, "Ingredient_Fibre": 3}, []
    pg.tab = 0
    b, ev = UCB(), UEB()
    pg.build(None, b, ev, S1)
    tok = str(pg.tok)
    _cmds = " ".join(str(x) for x in b.getCommands())
    reels1 = count_in(inv, "SkyyFishing_Reel_Bamboo", Bench)
    st0, fb0 = count_in(inv, "Ingredient_Stick", Bench), count_in(inv, "Ingredient_Fibre", Bench)
    r = click("craft", 1)
    K.check(r.startswith("+Crafted the Wooden Reel") and count_in(inv, "SkyyFishing_Reel_Bamboo", Bench) == reels1 + 1
            and BAG["pool"]["Ingredient_Stick"] + count_in(inv, "Ingredient_Stick", Bench) == 4 + st0 - 4
            and [e for e in BAG["log"] if e[0] == "count"],
            "X13 0.1.1: the page builds with the bag counts and its craft click pulls the missing inputs from the bags: %s" % r)
    BAG["pool"], BAG["log"] = {}, []
    tok = str(pg.tok)
''')
# C2: class compare with SkyyFishing-0.1.jar (the SET pin) + the lang / R checks in the parent
C2 = r'''

def class_members(data):
    """a .class file -> (fields, methods) as sets of 'name descriptor' (constant pool walk, no javap needed)"""
    import struct
    pos = [10]

    def u(n):
        v = data[pos[0]:pos[0] + n]
        pos[0] += n
        return int.from_bytes(v, "big")
    cnt = int.from_bytes(data[8:10], "big")
    cp = [None] * cnt
    i = 1
    while i < cnt:
        tag = u(1)
        if tag == 1:
            ln = u(2)
            cp[i] = data[pos[0]:pos[0] + ln].decode("utf-8", "replace")
            pos[0] += ln
        elif tag in (3, 4):
            u(4)
        elif tag in (5, 6):
            u(8)
            i += 1
        elif tag in (7, 8, 16, 19, 20):
            u(2)
        elif tag in (9, 10, 11, 12, 17, 18):
            u(4)
        elif tag == 15:
            u(3)
        else:
            raise ValueError("cp tag %d" % tag)
        i += 1
    u(6)
    u(2 * u(2))
    out = []
    for _kind in (0, 1):
        s_ = set()
        for _ in range(u(2)):
            u(2)
            nm, ds = cp[u(2)], cp[u(2)]
            for _a in range(u(2)):
                u(2)
                u(u(4))
            s_.add(nm + " " + ds)
        out.append(s_)
    return out[0], out[1]


def part_compare(jz):
    """C2: SkyyFishing-0.1.jar (the SET pin) vs this jar"""
    if not os.path.isfile(OLD_JAR):
        check(False, "C2. %s not found for the class compare" % OLD_JAR)
        return
    oz = zipfile.ZipFile(OLD_JAR)
    on, nn = set(oz.namelist()), set(jz.namelist())
    ocls, ncls = sorted(n for n in on if n.endswith(".class")), sorted(n for n in nn if n.endswith(".class"))
    check(ocls == ncls, "C2. same classes as 0.1 (31 + kit 7): extra %s missing %s" % (sorted(set(ncls) - set(ocls)), sorted(set(ocls) - set(ncls))))
    oa = sorted(n for n in on if not n.endswith(".class") and n != "manifest.json")
    na = sorted(n for n in nn if not n.endswith(".class") and n != "manifest.json")
    diff = [n for n in na if n in on and oz.read(n) != jz.read(n)]
    check(oa == na and diff == ["Server/Languages/en-US/server.lang"],
          "C2. same asset files as 0.1, byte for byte except server.lang (item JSON, stat, models, art unchanged): %s" % diff[:6])
    ol = oz.read("Server/Languages/en-US/server.lang").decode("utf-8").splitlines()
    nl_ = jz.read("Server/Languages/en-US/server.lang").decode("utf-8").splitlines()
    gone, new = sorted(set(ol) - set(nl_)), sorted(set(nl_) - set(ol))
    want = sorted("%sitems.%s.name=%s" % (p, i, n) for p in ("", "server.") for i, n in
                  (("SkyyFishing_Rod_Bamboo", "Wooden Fishing Rod"), ("SkyyFishing_Reel_Bamboo", "Wooden Reel")))
    check(new == want and len(gone) == 4 and all("Bamboo Fishing Rod" in g or "Bamboo Reel" in g for g in gone)
          and not [l for l in nl_ if ".name=" in l and "Bamboo" in l.split("=", 1)[1]],
          "C2/R. lang: only the 4 T1 name lines changed (Wooden Fishing Rod / Wooden Reel), no shown name says Bamboo: +%s -%s" % (new, gone))
    want_add = {"FishBridge": {"bagsOn ()Z", "bagCall (Ljava/lang/String;Ljava/lang/Object;)J", "bagCount (Ljava/util/UUID;Ljava/lang/String;)I",
                               "bagTake (Ljava/util/UUID;Ljava/lang/String;I)I", "bagPut (Ljava/util/UUID;Ljava/lang/String;I)I",
                               "bagCommit (Ljava/util/UUID;Ljava/lang/String;I)I"},
                "FishBench": {"have (Lcom/hypixel/hytale/server/core/inventory/container/ItemContainer;Ljava/util/UUID;Ljava/lang/String;)I",
                              "needText (Lcom/hypixel/hytale/server/core/inventory/container/ItemContainer;Ljava/util/UUID;I)Ljava/lang/String;",
                              "bagUndo (Lcom/hypixel/hytale/server/core/inventory/container/ItemContainer;Ljava/util/UUID;Ljava/lang/String;Ljava/util/ArrayList;)V",
                              "bagDone (Ljava/util/UUID;Ljava/util/ArrayList;)V",
                              "restamp (Lcom/hypixel/hytale/server/core/inventory/container/ItemContainer;)I"},
                "FishRig": {"stale (Lcom/hypixel/hytale/server/core/inventory/ItemStack;)Z"}}
    bad, seen = [], {}
    for c in ncls:
        if c not in on:
            continue
        of, om = class_members(oz.read(c))
        nf, nm = class_members(jz.read(c))
        short = c.rsplit("/", 1)[1][:-6]
        if om - nm or of - nf:
            bad.append((short, "removed", sorted(om - nm) + sorted(of - nf)))
        add_m = nm - om
        add_f = nf - of
        if short == "FishDefs":
            if add_f != {"TIER_SHOWN [Ljava/lang/String;", "VN_ID [Ljava/lang/String;", "VN_NAME [Ljava/lang/String;"} or add_m:
                bad.append((short, "added", sorted(add_f | add_m)))
        elif add_m or add_f:
            seen[short] = add_m | add_f
    for k in set(want_add) | set(seen):
        if seen.get(k, set()) != want_add.get(k, set()):
            bad.append((k, "added", sorted(seen.get(k, set()) ^ want_add.get(k, set()))))
    check(not bad, "C2. member compare vs 0.1: nothing removed; added exactly FishDefs.TIER_SHOWN / VN_ID / VN_NAME, FishBridge.bag* (6), "
                   "FishBench.have / needText(inv, uuid, r) / bagUndo / bagDone / restamp, FishRig.stale: %s" % bad[:4])
    om_ = json.loads(oz.read("manifest.json"))
    nm_ = json.loads(jz.read("manifest.json"))
    om_.pop("Version"), nm_.pop("Version"), om_.pop("Name", None), nm_.pop("Name", None)
    check(om_ == nm_, "C2. manifest unchanged except the version")
    print("C2. class compare vs SkyyFishing-0.1.jar: %d classes, %d assets; member diffs = the bag + display members only" % (len(ncls), len(na)))

'''
rep("\n\n# ====================================================================================================== children\n",
    C2 + "\n# ====================================================================================================== children\n")
# D start1: SkyyFishing 0.1 is LIVE now, so the scratch copy of the world already holds its config.properties -> 0.1.1 must read it
# without rewriting a byte (a world without one still gets the defaults)
rep('''        K.check(before is None and after is not None and b"fish.castRange=12" in after, "D start1: no SkyyFishing data yet -> the default config is written")''',
    '''        if before is None:
            K.check(after is not None and b"fish.castRange=12" in after, "D start1: no SkyyFishing data yet -> the default config is written")
        else:
            K.check(before == after, "D start1: the live 0.1 config.properties (copied) is read by 0.1.1, not rewritten (bytes unchanged)")''')
rep("        part_static()\n","        _jz, _az = part_static()\n        part_compare(_jz)\n")
# X17: the review fixes (old 0.1 rods re-stamped by the page build; the game's item names in the bench text) - inside X13, before Close
X17 = r'''    # ============================================================================ X17 (0.1.1 review fixes)
    # (a) a rod made by 0.1 carries "Bamboo Fishing Rod" / "Reel: Bamboo Reel" in its stored tooltip -> the bench page build re-stamps it
    MSGc = JClass("com.hypixel.hytale.server.core.Message")
    IDMc = JClass("com.hypixel.hytale.server.core.asset.type.item.config.metadata.ItemDisplayMetadata")
    ALc = JClass("java.util.ArrayList")
    _new = Rig.withRig(IS("SkyyFishing_Rod_Bamboo", 1), JArray(JString)(["1", "SkyyFishing_Hook_Barbed_I", "", ""]))
    _l = ALc()
    for x_ in ["Max fish weight: 5 kg", "Reel: Bamboo Reel (power 1)", "Hook: Barbed Hook I", "Line: -", "Sinker: -"]:
        _l.add(JString(x_))
    _old = _new.withMetadata(IDMc.KEYED_CODEC, IDMc(MSGc.raw("Bamboo Fishing Rod"), Rig.lines(_l, Defs.COL_VALUE)))

    def _stk(i_):
        return inv.getItemStack(SH(i_).shortValue())

    def _mj(st):
        if st is None or st.isEmpty() or st.getMetadata() is None:
            return ""
        return str(st.getMetadata().toJson())
    K.check(bool(Rig.stale(_old)) and "Bamboo Fishing Rod" in _mj(_old) and not bool(Rig.stale(_new))
            and not [rid for rid in ("SkyyFishing_Rod_Bamboo", "SkyyFishing_Rod_Copper", "SkyyFishing_Rod_Iron")
                     if bool(Rig.stale(Rig.withRig(IS(rid, 1), Rig.freshRig(rid))))]
            and not bool(Rig.stale(IS("SkyyFishing_Rod_Bamboo", 1))) and not bool(Rig.stale(IS("Ingredient_Stick", 3))) and not bool(Rig.stale(None)),
            "X17 (a): a 0.1-named rod is stale; every 0.1.1 rod, a rod without metadata, other items and null are not")
    rods0 = count_in(inv, "SkyyFishing_Rod_Bamboo", Bench)
    inv.addItemStack(_old)
    _sl = [i_ for i_ in range(int(inv.getCapacity())) if "Bamboo Fishing Rod" in _mj(_stk(i_))]
    pg.tab = 0
    pg.build(None, UCB(), UEB(), S1)
    _st = _stk(_sl[0]) if len(_sl) == 1 else None
    _j = _mj(_st)
    K.check(len(_sl) == 1 and _st is not None and str(_st.getItemId()) == "SkyyFishing_Rod_Bamboo" and int(_st.getQuantity()) == 1
            and "Bamboo Fishing Rod" not in _j and "Bamboo Reel" not in _j and "Wooden Fishing Rod" in _j and "Wooden Reel" in _j
            and [str(x) for x in Rig.rigOf(_st)] == ["1", "SkyyFishing_Hook_Barbed_I", "", ""]
            and count_in(inv, "SkyyFishing_Rod_Bamboo", Bench) == rods0 + 1 and not bool(Rig.stale(_st)),
            "X17 (a): opening the bench re-stamps the old rod in place: Wooden Fishing Rod / Wooden Reel, same id, slot, quantity and rig, "
            "no rod made or lost: %s" % _j[:300])
    _sig = str(Rig.sig(_st))
    pg.tab = 1
    pg.build(None, UCB(), UEB(), S1)
    K.check(str(Rig.sig(_stk(_sl[0]))) == _sig and int(Bench.restamp(inv)) == 0 and _sig in [str(x) for x in pg.rodSigs],
            "X17 (a): a re-stamped rod is left alone by later builds (no churn); the RIG list's click signatures are the re-stamped stack's")
    inv.addItemStack(_old)
    _sl2 = [i_ for i_ in range(int(inv.getCapacity())) if "Bamboo Fishing Rod" in _mj(_stk(i_))]
    K.check(len(_sl2) == 1 and int(Bench.restamp(inv)) == 1 and not [i_ for i_ in range(int(inv.getCapacity())) if bool(Rig.stale(_stk(i_)))]
            and int(Bench.restamp(None)) == 0,
            "X17 (a): FishBench.restamp re-names exactly the stale rods (1), null inventory = 0")
    for s_ in sorted(set(_sl + _sl2), reverse=True):
        inv.removeItemStackFromSlot(SH(s_).shortValue(), JInt(1))
    K.check(count_in(inv, "SkyyFishing_Rod_Bamboo", Bench) == rods0, "X17 (a): the two test rods removed again")
    # (b) the game's own item names: "6 Plant Fiber (2/6)", never "Fibre"; every bench input named as in Assets.zip's en-US server.lang
    _vl = {}
    for ln_ in _az.read("Server/Languages/en-US/server.lang").decode("utf-8-sig").splitlines():
        if ln_.startswith("items.") and "=" in ln_:
            k_, v_ = ln_.split("=", 1)
            if k_.strip().endswith(".name"):
                _vl[k_.strip()[len("items."):-len(".name")]] = v_.strip()
    _bad = sorted(i_ for i_ in set(_rin) if str(Defs.pretty(i_)) != _vl.get(i_))
    _nt = str(Bench.needText(binv(20, ("Ingredient_Fibre", 2)), U1, 0))
    _cu = str(Bench.needText(binv(20), U1, 2))
    K.check(not _bad and str(Defs.pretty("Ingredient_Fibre")) == "Plant Fiber" and str(Defs.pretty("Ingredient_Stick")) == "Stick"
            and "6 Plant Fiber (2/6)" in _nt and "6 Stick (0/6)" in _nt and "Fibre" not in _nt and "Copper Ingot" in _cu
            and str(Defs.pretty("Not_An_Item_X")) == "Not An Item X" and str(Defs.pretty("Ingredient_Not_There")) == "Not There",
            "X17 (b): bench text uses the game's names (%s | %s); unknown ids keep the old spelling; mismatches %s" % (_nt, _cu, _bad))
    pg.tab = 1
    pg.build(None, UCB(), UEB(), S1)
    tok = str(pg.tok)
'''
rep("    c0 = int(pg.closes)\n", X17 + "    c0 = int(pg.closes)\n")
# chat text now uses the game's item name (Ore_Gold = "Gold Ore", not "Ore Gold")
rep('any("holding Ore Gold x2" in t for t in tells()), "X7: Lost Property materials (2 Gold Ore) handed over")',
    'any("holding Gold Ore x2" in t for t in tells()), "X7: Lost Property materials (2 Gold Ore) handed over, named as the game does")')
assert "fishing01" not in S["s"], "a 0.1 scratch path is left in the harness"
open(os.path.join(FISH, "test_skyyfishing_0.1.1.py"), "w", encoding="utf8", newline=TNL).write(S["s"])
print("wrote SkyyFishing/build_skyyfishing_0.1.1.py and SkyyFishing/test_skyyfishing_0.1.1.py")
