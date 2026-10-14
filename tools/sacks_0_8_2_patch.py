"""Derive SkyySacks/build_skyysacks_0.8.2.py from the SET pin 0.8.1 (the GENERATED build_skyysacks_0.8.1.py; edit THIS file, then
regenerate: python tools/sacks_0_8_2_patch.py; never re-run sacks_0_8_1_patch.py on top of it).
Run:  python tools/sacks_0_8_2_patch.py   then   python SkyySacks/build_skyysacks_0.8.2.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.2.py

0.8.2 = /pdadmin rarity (Skyy 2026-10-13: "reset all my bags from omni to common if you can. so i can test it"):
  /pdadmin rarity <player> <category|all> <Normal|Unique|Rare|Legendary|Omni>  (admin: skyysacks.admin, like every /pdadmin tool; the
  player must be online - it runs on their world thread with their SETTLED profile key, like /pdadmin omni)
  - category = Mining | Foraging | Farming | Fishing | Combat | Smithing (any case) or all (the six). "Common" is read as Normal (the
    Void's first rarity; Skyy's word), "Mythic" as Omni.
  - Normal..Legendary on ONE category: that category's saved rarity (pd/<key>.properties rar.<Cat>) becomes it. If the Void was Omni by
    /pdadmin omni (the saved omni flag) the flag is cleared and the OTHER five categories become at least Legendary (Omni was above
    Legendary for every category - they drop one step, not to whatever they were before the grant).
  - Normal..Legendary on all: the six rarities become it and the omni flag is cleared.
  - Omni: the omni flag (exactly /pdadmin omni) - Omni is the whole Void, so a category given with Omni is named in the reply only.
  - LOWERING NEVER DELETES ITEMS: only the rarity in pd/<key>.properties changes - the pool (pools/<key>.properties) is not touched.
    A category over its new space keeps every stored item; the sweep / Deposit / sacks:fn:deposit simply put nothing more in (they
    already stop at "room <= 0"), withdrawing works as always. The reply names each category that is over its space now.
  - The reply also says when the Void is STILL Omni (pd.omniAuto with all six Legendary, or an Omni bag conversion still settling) or
    when a bag conversion still settling will raise a category again in up to 30 s (VoidStore.pendRank) - nothing is hidden.
  - migration.log: "/pdadmin rarity: <before> -> <after> by <admin> (items stored N, unchanged)"; crafts.log: VOID-RARITY.
  - Saved through the existing writer job (VoidJob 2 = saveNow), like /pdadmin omni and the upgrade. No new file, key or setting.
Classes changed: VoidStore (+ rarityArgs, setRarity), VoidAdminTask (+ ci, rar, answer; run calls answer), PdAdminCmd (constructor
text, execute). Everything else = 0.8.1 (version constants).
Rollback to 0.8.1: safe (the same pd file keys; 0.8.1 reads the rarity the admin set).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "SkyySacks")
sys.path.insert(0, os.path.join(ROOT, "tools"))
src = os.path.join(HERE, "build_skyysacks_0.8.1.py")
dst = os.path.join(HERE, "build_skyysacks_0.8.2.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.8.1"
s = raw.decode("utf8").replace("\r\n", "\n")
OLD = s
LF = "\n"
assert 'VERSION = "0.8.1"' in s and "setRarity" not in s, "not the live generated 0.8.1"


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:90]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:90])
    s = s.replace(old, new)


GONE_OK = set()


def gone(*lines):
    for ln in lines:
        GONE_OK.add(ln)


# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''like any gathered item. No saved data or setting changes. Details: the patch docstring.
"""
''', '''like any gathered item. No saved data or setting changes. Details: the patch docstring.
0.8.2 (derived from 0.8.1 by tools/sacks_0_8_2_patch.py - edit the patch, not this file; Skyy 2026-10-13 "reset all my bags from omni to
common if you can. so i can test it"): /pdadmin rarity <player> <category|all> <Normal|Unique|Rare|Legendary|Omni> sets a profile's
Void rarity (testing / support); lowering never deletes a stored item - only new deposits stop while a category is over its space.
Details: the patch docstring.
"""
''')
rep('VERSION = "0.8.1"\n', 'VERSION = "0.8.2"\n')
gone('VERSION = "0.8.1"')

# ---------------------------------------------------------------------------------------------------------------- VoidStore.rarityArgs + setRarity
rep('''  migLog(k, "/pdadmin omni: Omni granted");
  return "Omni granted - every category now has the Omni multiplier";
}\'\'\'), vst))
''', '''  migLog(k, "/pdadmin omni: Omni granted");
  return "Omni granted - every category now has the Omni multiplier";
}\'\'\'), vst))
# 0.8.2: /pdadmin rarity <player> <category|all> <rarity> - the two words -> int[] { category index (-1 = all six), rarity 0..4 } or the
# String why not. Common = Normal (Skyy's word), Mythic = Omni.
vst.addMethod(CtNewMethod.make(jt(r\'\'\'
public static Object rarityArgs(String cat, String rar) {
  String c = cat == null ? "" : cat.trim();
  String r = rar == null ? "" : rar.trim().toLowerCase();
  int ci = -2;
  if (c.equalsIgnoreCase("all")) ci = -1;
  else {
    for (int i = 0; i < @PKG@.SackDefs.CATS.length; i++) if (@PKG@.SackDefs.CATS[i].equalsIgnoreCase(c)) ci = i;
  }
  if (ci == -2) return "unknown category '" + c + "' - use Mining, Foraging, Farming, Fishing, Combat, Smithing or all";
  int ri = -1;
  if (r.equals("common")) ri = 0;
  else if (r.equals("mythic")) ri = 4;
  else {
    for (int i = 0; i < @PKG@.SackDefs.RNAME.length; i++) if (@PKG@.SackDefs.RNAME[i].equalsIgnoreCase(r)) ri = i;
  }
  if (ri < 0) return "unknown rarity '" + rar + "' - use Normal (Common), Unique, Rare, Legendary or Omni";
  return new int[] { ci, ri };
}\'\'\'), vst))
# 0.8.2: set the rarity of profile k (ci -1 = all six; r 0..3 = Normal..Legendary, 4 = Omni = the omni flag). Only the VoidState rarity /
# omni flag change (saved by the writer job, like /pdadmin omni) - the pool is never touched, so lowering deletes nothing: a category over
# its new space keeps every item and only takes no more. u = the target (its levels for the reply's space numbers). World thread.
vst.addMethod(CtNewMethod.make(jt(r\'\'\'
public static String setRarity(java.util.UUID u, String k, int ci, int r, String who) {
  @PKG@.VoidState s = st(k);
  if (s == null) return NOREAD;
  String[] cats = @PKG@.SackDefs.CATS;
  if (r < 0 || r > 4 || ci < -1 || ci >= cats.length) return "unknown category or rarity";
  long[] used0 = usedAll(k);
  long items0 = 0L;
  for (int i = 0; i < used0.length; i++) items0 += used0[i];
  StringBuilder was = new StringBuilder();
  for (int i = 0; i < cats.length; i++) { if (i > 0) was.append(", "); was.append(cats[i]).append(' ').append(@PKG@.SackDefs.RNAME[rank(k, i)]); }
  String extra = "";
  if (r == 4) {
    s.omni = true;
    if (ci >= 0) extra = " (Omni is the whole Void - all six categories)";
  } else if (ci < 0) {
    for (int i = 0; i < cats.length; i++) s.rar[i] = r;
    s.omni = false;
  } else {
    if (s.omni) {
      for (int i = 0; i < cats.length; i++) if (i != ci && s.rar[i] < 3) s.rar[i] = 3;
      s.omni = false;
      extra = " (it was Omni: the other categories are Legendary now)";
    }
    s.rar[ci] = r;
  }
  markDirty(k);
  saveAsync(k);
  java.util.HashMap caps = capsK(u, k);
  long[] used = usedAll(k);
  long items = 0L;
  StringBuilder now = new StringBuilder();
  StringBuilder over = new StringBuilder();
  StringBuilder back = new StringBuilder();
  for (int i = 0; i < cats.length; i++) {
    items += used[i];
    if (i > 0) now.append(", ");
    now.append(cats[i]).append(' ').append(@PKG@.SackDefs.RNAME[rank(k, i)]);
    Integer cc = (Integer) caps.get(cats[i]);
    if (cc != null && used[i] > (long) cc.intValue()) { if (over.length() > 0) over.append(", "); over.append(cats[i]).append(' ').append(used[i]).append(" / ").append(cc.intValue()); }
    if (r < 4 && (ci < 0 || ci == i) && pendRank(k, i) > r) { if (back.length() > 0) back.append(", "); back.append(cats[i]); }
  }
  String note = "";
  if (r < 4 && omni(k)) note = note + " It is STILL Omni: " + (pendOmni(k) ? "an Omni bag conversion is still settling." : "all six are Legendary and Server Setup gives Omni automatically (pd.omniAuto).");
  if (back.length() > 0) note = note + " A bag conversion still settling raises " + back + " again within 30 s.";
  migLog(k, "/pdadmin rarity: " + was + " -> " + now + " by " + who + " (items stored " + items0 + ", unchanged: " + items + ")");
  try { @PKG@.CraftLog.later(k, "VOID-RARITY " + (ci < 0 ? "all" : cats[ci]) + " " + @PKG@.SackDefs.RNAME[r] + " by " + who); } catch (Throwable t) { }
  return "Void rarity set" + extra + ": " + now + ". Before: " + was + "."
    + (over.length() > 0 ? " Over the space now: " + over + " - nothing was removed; new items of those categories stop going in until there is room." : " Every stored item still fits.")
    + note;
}\'\'\'), vst))
''')

# ---------------------------------------------------------------------------------------------------------------- VoidAdminTask: mode 4 = rarity
rep('''vat.addConstructor(CtNewConstructor.make(f"public VoidAdminTask(int mode, {PR} admin, {PR} target) {{ this.mode = mode; this.admin = admin; this.target = target; }}", vat))
vat.addMethod(CtNewMethod.make(jt(r\'\'\'
public void run() {
  String msg;
  try {
    @REF@ r = this.target.getReference();
    @ST@ st = r == null ? null : r.getStore();
    @PLA@ p = st == null ? null : (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    String k = @PKG@.SackPool.settledKey(this.target.getUuid());
    if (p == null) msg = "that player is not in a world right now";
    else if (k == null) msg = "that player's profile is loading or switching - try again in a few seconds";
    else if (this.mode == 1) msg = @PKG@.VoidStore.giveBack(p, k);
    else if (this.mode == 3) msg = @PKG@.VoidStore.resume(k);
    else msg = @PKG@.VoidStore.grantOmni(k);
  } catch (Throwable t) { msg = "failed: " + t; }''', '''vat.addConstructor(CtNewConstructor.make(f"public VoidAdminTask(int mode, {PR} admin, {PR} target) {{ this.mode = mode; this.admin = admin; this.target = target; }}", vat))
# 0.8.2: mode 4 = /pdadmin rarity (ci = category index or -1 = all, rar = 0..4); answer = the reply for the target's settled key (the
# branches of 0.8.1's run, moved so a harness executes every mode)
vat.addField(CtField.make("public int ci;", vat))
vat.addField(CtField.make("public int rar;", vat))
vat.addMethod(CtNewMethod.make(jt(r\'\'\'
public static String answer(int mode, @PLA@ p, String k, java.util.UUID u, int ci, int rar, String who) {
  if (p == null) return "that player is not in a world right now";
  if (k == null) return "that player's profile is loading or switching - try again in a few seconds";
  if (mode == 1) return @PKG@.VoidStore.giveBack(p, k);
  if (mode == 3) return @PKG@.VoidStore.resume(k);
  if (mode == 4) return @PKG@.VoidStore.setRarity(u, k, ci, rar, who);
  return @PKG@.VoidStore.grantOmni(k);
}\'\'\'), vat))
vat.addMethod(CtNewMethod.make(jt(r\'\'\'
public void run() {
  String msg;
  try {
    @REF@ r = this.target.getReference();
    @ST@ st = r == null ? null : r.getStore();
    @PLA@ p = st == null ? null : (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    String k = @PKG@.SackPool.settledKey(this.target.getUuid());
    msg = answer(this.mode, p, k, this.target.getUuid(), this.ci, this.rar, this.admin == null ? "?" : this.admin.getUsername());
  } catch (Throwable t) { msg = "failed: " + t; }''')
gone('    if (p == null) msg = "that player is not in a world right now";',
     '''    else if (k == null) msg = "that player's profile is loading or switching - try again in a few seconds";''',
     "    else if (this.mode == 1) msg = @PKG@.VoidStore.giveBack(p, k);",
     "    else if (this.mode == 3) msg = @PKG@.VoidStore.resume(k);",
     "    else msg = @PKG@.VoidStore.grantOmni(k);")

# ---------------------------------------------------------------------------------------------------------------- PdAdminCmd
rep('''  super("pdadmin", "(admin) /pdadmin legacybags <player>|all | resume <player>|all | omni <player> - Void emergency tools (SkyyVoid)");''',
    '''  super("pdadmin", "(admin) /pdadmin legacybags <player>|all | resume <player>|all | omni <player> | rarity <player> <category|all> <rarity> - Void admin tools (SkyyVoid)");''')
gone('''  super("pdadmin", "(admin) /pdadmin legacybags <player>|all | resume <player>|all | omni <player> - Void emergency tools (SkyyVoid)");''')
rep('''    int mode = act.equals("legacybags") ? 1 : (act.equals("omni") ? 2 : (act.equals("resume") ? 3 : 0));
    if (mode == 0 || who.length() == 0) { pr.sendMessage(@MSG@.raw("[SkyyVoid admin] Usage: /pdadmin legacybags <player>|all (gives the old bags that became rarity back and stops old bags converting - before a rollback) | /pdadmin resume <player>|all | /pdadmin omni <player>")); return; }''',
    '''    int mode = act.equals("legacybags") ? 1 : (act.equals("omni") ? 2 : (act.equals("resume") ? 3 : (act.equals("rarity") ? 4 : 0)));
    if (mode == 0 || who.length() == 0) { pr.sendMessage(@MSG@.raw("[SkyyVoid admin] Usage: /pdadmin legacybags <player>|all (gives the old bags that became rarity back and stops old bags converting - before a rollback) | /pdadmin resume <player>|all | /pdadmin omni <player> | /pdadmin rarity <player> <category|all> <Normal|Unique|Rare|Legendary|Omni> (lowering keeps every stored item)")); return; }
    // 0.8.2: /pdadmin rarity <player> <category|all> <rarity> - both words checked here, before the hop to the player's world
    int[] rp = null;
    if (mode == 4) {
      Object pl = @PKG@.VoidStore.rarityArgs(a.length > at + 2 ? a[at + 2] : "", a.length > at + 3 ? a[at + 3] : "");
      if (!(pl instanceof int[])) { pr.sendMessage(@MSG@.raw("[SkyyVoid admin] " + pl + ". Usage: /pdadmin rarity <player> <category|all> <Normal|Unique|Rare|Legendary|Omni>")); return; }
      rp = (int[]) pl;
    }''')
gone('''    int mode = act.equals("legacybags") ? 1 : (act.equals("omni") ? 2 : (act.equals("resume") ? 3 : 0));''',
     '''    if (mode == 0 || who.length() == 0) { pr.sendMessage(@MSG@.raw("[SkyyVoid admin] Usage: /pdadmin legacybags <player>|all (gives the old bags that became rarity back and stops old bags converting - before a rollback) | /pdadmin resume <player>|all | /pdadmin omni <player>")); return; }''')
rep('''    if (who.equalsIgnoreCase("all") && mode != 2) {''', '''    if (who.equalsIgnoreCase("all") && mode != 2 && mode != 4) {''')
gone('''    if (who.equalsIgnoreCase("all") && mode != 2) {''')
rep('''    w.execute(new @PKG@.VoidAdminTask(mode, pr, target));''', '''    @PKG@.VoidAdminTask task = new @PKG@.VoidAdminTask(mode, pr, target);
    if (rp != null) { task.ci = rp[0]; task.rar = rp[1]; }
    w.execute(task);''')
gone('''    w.execute(new @PKG@.VoidAdminTask(mode, pr, target));''')

# ---------------------------------------------------------------------------------------------------------------- guards
assert s.index("public static Object rarityArgs(") < s.index("public static String setRarity(") < s.index("public static String answer(int mode")
assert s.index("public static String answer(int mode") < s.index("msg = answer(this.mode")
_gone = sorted(ln for ln in set(OLD.split(LF)) - set(s.split(LF)))
_bad = [ln for ln in _gone if ln not in GONE_OK]
assert not _bad, "0.8.1 lines lost by accident: %s" % _bad[:5]
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines; 0.8.1 had %d)" % (s.count(LF), OLD.count(LF)))
