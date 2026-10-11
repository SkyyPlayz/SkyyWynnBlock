"""Derive SkyyGear/build_skyygear_0.2.21.py from the LIVE 0.2.20 (build_skyygear_0.2.20.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_2_20_patch.py). Edit THIS file, never the generated script; every anchor is asserted. Run:
    python tools/gear_0_2_21_patch.py      then      python SkyyGear/build_skyygear_0.2.21.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.2.21.py

0.2.21 = MERGE THE ROLLS (Skyy 2026-10-10, popup "Merge the rolls (Recommended)"; docs/answered/gear.md LOCKED 2026-10-10 'multitool crafting
with rolled tools' line: any pickaxe + hatchet of the tier can make a multitool; it takes the BEST rarity of the two and MERGES their tool
modifiers within the multitool caps; nothing good is lost - an upgrade path).
WHY NOT AT THE BENCH (engine fact, VERIFIED bytecode 2026-10-10, re-proved by the harness on the real CraftingManager): a bench craft takes its
inputs with ItemContainer.removeMaterials -> InternalContainerUtilMaterial, whose item test is ItemStack.isEquivalentType(stack,
MaterialQuantity.toItemStack()) = same item id AND equal metadata (null = null). A recipe input has no metadata, so a stack that carries a
SkyyGear document (every tool crafted since 0.2.17 - "tr":1) is NEVER counted, consumed or offered by the bench (resolveCraftQuantity /
getMaterialCraftLimit count 0 -> craftItem / queueCraft return BEFORE CraftRecipeEvent$Pre fires). 0.2.18 - 0.2.20 had no code guard of their
own: the "refuse rolled inputs" behaviour was this engine rule. No craft event ever sees a rolled tool, so the merge cannot ride on the bench;
it gets its own place - the same way /reforge does.
  1. /multitool (player command, hytale:Adventurer) opens the MULTITOOL page (the Reforge page's vanilla look, GearUi): the left list = every
     pickaxe and hatchet of a multitool tier you carry (hotbar, inventory, backpack, tools); click one pickaxe and one hatchet; the right side
     shows both and the result (rarity, level, the merged lines); "Make multitool" merges them. The multitool replaces the pickaxe in ITS slot;
     the hatchet's slot empties. No coins, no Smithing XP (a multitool assembly never pays craft XP - the two tools paid theirs; the 0.2.18
     salvage cap still holds, so merge -> salvage gives back no more than the two tools would).
  2. THE MERGED DOCUMENT (GearMerge.doc): rarity = the HIGHER of the two inputs (a plain tool - no SkyyGear document, or an old one without
     "tr" and without lines - counts as Normal); "tr":1; level = the multitool's own craft level (GearRoll.craftLevel: the lower of Mining and
     Foraging moved into its band - the bench rule); lines = the pickaxe's lines + the hatchet's lines: only the six multitool keys (mpow cpow
     mfort ffort mwis fwis - anything else is dropped and counted in the log), each value capped at the most a FRESH MULTITOOL can roll at
     its rarity and level (GearMerge.capOf with the multitool's own 6-key pool = GearRoll.bounds, no spare-slot boost; fix round: a pickaxe /
     hatchet pool's boost no longer leaks into the multitool), the same key twice = the higher value, then at most rarity.<id> modifiers lines (the multitool's count for its rarity; over it = the strongest
     lines by value / cap, table order on a tie). Because the output rarity is the higher one, the merged multitool never has fewer lines
     than the better input. Reforge count rfN = the higher of the two; the reforge name rf = the better tool's (pickaxe on a tie). SkyyGear
     stores no "coins spent" - nothing to merge there. Level ups (lvU / lvl0) are not carried: the multitool is made at your level.
     Durability is not carried either: the multitool is a new item at full durability, like a bench craft.
     The page WARNS before the click (gold line, GearMerge.lossText) when lines will be lost (non-multitool keys / over the line count),
     lines will be lowered to the multitool's limit, or the multitool's level is below the better input's level (fix round).
     TWO PLAIN TOOLS = the normal craft roll (GearRoll.craftDoc, exactly what a bench craft gives).
  3. REFUSED (a gold line on the page, nothing moves): a Mythic, Set or Untiered tool, an Untiered-table id, a gear.mythicItems id or a tool
     with a set field ("special tools keep their own powers and are never merged"); an unidentified tool; unreadable / newer SkyyGear data; a
     stack of more than one; a pickaxe and a hatchet of different tiers; multitools off (part.multitool), tool rarity off (part.toolRarity:
     make them at a bench from plain tools), the Multitools mod not loaded; craft.belowBand block (GearRoll.blockWhy, as at the bench);
     profile still loading (profile:busy) or the profile changed since the pick.
  4. DUPE / LOSS SAFETY (GearMerge.merge, world thread, one click): both slots re-checked by fingerprint (GearForge.same: id, quality,
     document hash, durability) and must differ; MERGE-BEGIN in gear.log with BOTH full input documents; (a) the HATCHET leaves first
     (removeItemStackFromSlot, checked empty; MERGE-BEGIN is flushed to disk synchronously first - GearLog.flush, fix round); (b) the pickaxe's slot gets the multitool (setItemStackForSlot, checked); (b) failing = the
     hatchet is put back in its slot (MERGE-FAILED + RESTORED, or MERGE-RESTORE-FAILED with its document for an admin). A crash between (a)
     and (b) can only LOSE the hatchet (its document is in MERGE-BEGIN), never copy anything. After: the item counts are checked (pickaxe id
     -1, hatchet id -1, multitool +1; else MERGE-COUNT + a WARN). A second click with the old fingerprints is refused ("moved or changed").
  5. THE BENCH IS UNCHANGED: plain pickaxe + plain hatchet still craft a multitool at the bench and it rolls like a 0.2.17 tool
     (GearCraftSys -> craftDoc); rolled tools stay invisible to the bench (the engine rule above), so a bench craft can never eat a rolled,
     Mythic or Untiered tool.
TEXT: the ready line lists /multitool; the multitools start line ends "; rolled pickaxes / hatchets merge on /multitool"; the manifest sentence.
SAVED DATA: a merged multitool carries an ordinary 0.2.17 tool document ("src":"merge"); nothing else is stored. No config key, no one-time update.
ROLLBACK (for tools/deploy_set.py, reported, not edited here): 0.2.21 -> 0.2.20 is safe: merged multitools are plain rolled tool documents
0.2.20 reads (its six keys are all valid multitool keys; a merged multitool may hold more lines than a fresh one of its rarity - shown and used
as they are); /multitool goes away.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.20.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.21.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.2.20"' in s and s.startswith('"""SkyyGear 0.2.20 - build script'), "build_skyygear_0.2.20.py is not the live 0.2.20"
assert "GearMerge" not in s and "MultiPage" not in s, "0.2.20 already has the 0.2.21 parts"


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)


# ================================================================================================================ header + version
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
rep('''"""SkyyGear 0.2.20 - build script (javassist via jpype). GENERATED by tools/gear_0_2_20_patch.py from the LIVE 0.2.19 - edit the patch,
never this file. Run: python SkyyGear/build_skyygear_0.2.20.py -> SkyyGear/SkyyGear-0.2.20.jar (never --deploy).

''', '''"""SkyyGear 0.2.21 - build script (javassist via jpype). GENERATED by tools/gear_0_2_21_patch.py from the LIVE 0.2.20 - edit the patch,
never this file. Run: python SkyyGear/build_skyygear_0.2.21.py -> SkyyGear/SkyyGear-0.2.21.jar (never --deploy).

''' + HEAD[HEAD.index("0.2.21 = "):].strip() + '''

0.2.20 (the base, everything below is still true unless 0.2.21 above says otherwise):
''')
rep('VERSION = "0.2.20"', 'VERSION = "0.2.21"')

# ================================================================================================================ 1. GearMulti start line
rep('''+ "; " + sv + "; speed " + @PKG@.GearCfg.MULTI_SPD + "%, Fortune " + @PKG@.GearCfg.MULTI_FORT + "% of a single tool";''',
    '''+ "; " + sv + "; speed " + @PKG@.GearCfg.MULTI_SPD + "%, Fortune " + @PKG@.GearCfg.MULTI_FORT + "% of a single tool; rolled pickaxes / hatchets merge on /multitool";''')

# ================================================================================================================ 2. GearMerge + MultiPage + /multitool
MERGE_PY = r'''# ####################################################################################################################################
# 0.2.21 MERGE THE ROLLS (tools/gear_0_2_21_patch.py header): GearMerge (the merged document + the write), MultiPage (/multitool's page, the
# Reforge page's look), MultiCmd. Placed after /reforge: it calls GearForge, GearStamp, GearRoll, GearView, GearUi and ReforgePage.column.
# The bench cannot do it: its input test is ItemStack.isEquivalentType (same id AND equal metadata), so a tool with a SkyyGear document is
# never counted or taken by any recipe (VERIFIED bytecode, re-checked here).
# ####################################################################################################################################
for _c, _m in (("com.hypixel.hytale.server.core.inventory.container.InternalContainerUtilMaterial", "lambda$testRemoveMaterialFromItems$0"),
               ("com.hypixel.hytale.server.core.inventory.container.InternalContainerUtilMaterial", "lambda$internal_removeMaterialFromSlot$0")):
    assert "ItemStack.isEquivalentType" in _calls(_c, _m), "%s.%s no longer matches by isEquivalentType - re-check the merge reasoning" % (_c, _m)
assert "BsonDocument.equals" in _calls("com.hypixel.hytale.server.core.inventory.ItemStack", "isEquivalentType"), "isEquivalentType no longer compares metadata"
for _c, _m in ((IC, "removeItemStackFromSlot"), (IC, "setItemStackForSlot"), (IC, "getItemStack"), (IS, "getMetadata"), (IS, "getQuantity")):
    B.probe(pool, _c, _m)
gmerge = mk("GearMerge")
mpg = mk("MultiPage", PAGE)
mtc = mk("MultiCmd", APC)
MERGE_CLASSES = [gmerge, mpg, mtc]
# the GearMulti tier index of a vanilla Tool_Pickaxe_<Tier> / Tool_Hatchet_<Tier> of a multitool tier; -1 = not a multitool input
M(gmerge, r"""
public static int tierOf(String id) {
  if (id == null) return -1;
  for (int i = 0; i < @PKG@.GearMulti.TW.length; i++) {
    if (id.equals("Tool_Pickaxe_" + @PKG@.GearMulti.TW[i]) || id.equals("Tool_Hatchet_" + @PKG@.GearMulti.TW[i])) return i;
  }
  return -1;
}""")
# 1 = a pickaxe input, 3 = a hatchet input (GearTool's numbering), 0 = neither
M(gmerge, r"""
public static int famOf(String id) {
  if (tierOf(id) < 0) return 0;
  return id.startsWith("Tool_Pickaxe_") ? 1 : 3;
}""")
M(gmerge, r"""
public static boolean loaded() {
  for (int i = 0; i < @PKG@.GearMulti.TW.length; i++) if (@PKG@.Gear.item(@PKG@.GearMulti.mid(i)) != null) return true;
  return false;
}""")
# the document a merge reads (null = a plain tool, no SkyyGear data)
M(gmerge, r"""
public static @BD@ inDoc(@IS@ s) {
  if (s == null || s.isEmpty()) return null;
  return @PKG@.GearData.effective(s.getItemId(), s.getMetadata());
}""")
# plain = counts as Normal with nothing to carry: no document, or an old one (no "tr") of rarity Normal without lines
M(gmerge, r"""
public static boolean plain(@BD@ d) {
  return d == null || (!@PKG@.GearData.toolRolled(d) && @PKG@.GearData.rarity(d) == 0 && @PKG@.GearData.mods(d).size() == 0);
}""")
M(gmerge, r"""
public static String special(String id) {
  return @PKG@.Gear.itemName(id) + " is a special tool (Mythic, Set or Untiered) - it keeps its own powers and is never merged.";
}""")
# why one input cannot go into a multitool (null = it can); fam 1 pickaxe, 3 hatchet
M(gmerge, r"""
public static String why(@IS@ s, int fam) {
  String w = fam == 1 ? "pickaxe" : "hatchet";
  if (s == null || s.isEmpty()) return "Pick a " + w + " from the list.";
  String id = s.getItemId();
  if (famOf(id) != fam) return @PKG@.Gear.itemName(id) + " is not a " + w + " a multitool can be made from.";
  if (s.getQuantity() != 1) return "That " + w + " is a stack of " + s.getQuantity() + " - split it first.";
  if (@PKG@.GearUt.has(id) || @PKG@.GearUtFx.mythicId(id)) return special(id);
  int st = @PKG@.GearData.state(s.getMetadata());
  if (st == 3) return "The gear data on that " + w + " is unreadable - an admin can check it with /gear read.";
  if (st == 4) return "That " + w + " comes from a newer SkyyGear - it cannot be merged here.";
  @BD@ d = inDoc(s);
  if (st != 0 && d == null) return "The gear data on that " + w + " is unreadable - an admin can check it with /gear read.";
  if (d == null) return null;
  if (!@PKG@.GearData.identified(d)) return "Identify that " + w + " first" + @PKG@.GearCfg.idHow() + ".";
  if (@PKG@.GearData.rarity(d) > 4 || @PKG@.GearSet.of(d) != null) return special(id);
  return null;
}""")
# Object[] { String why (null = they can be merged), Integer tier, String multitool id }
M(gmerge, r"""
public static Object[] check(@IS@ p, @IS@ h, java.util.UUID u) {
  String w = why(p, 1);
  if (w == null) w = why(h, 3);
  if (w != null) return new Object[] { w, Integer.valueOf(-1), null };
  int tp = tierOf(p.getItemId());
  int th = tierOf(h.getItemId());
  if (tp != th) return new Object[] { "The pickaxe and the hatchet must be the same tier (a " + @PKG@.GearMulti.TW[tp] + " pickaxe, a " + @PKG@.GearMulti.TW[th] + " hatchet).", Integer.valueOf(-1), null };
  String mid = @PKG@.GearMulti.mid(tp);
  if (!@PKG@.GearCfg.MULTI_ON) return new Object[] { "Multitools are switched off on this server.", Integer.valueOf(tp), mid };
  if (@PKG@.Gear.item(mid) == null) return new Object[] { "There is no " + @PKG@.GearMulti.TW[tp] + " multitool here (the Multitools mod is not loaded).", Integer.valueOf(tp), mid };
  if (!@PKG@.GearData.toolRolls(mid)) return new Object[] { "Tool rarity is off on this server - make multitools at a bench from plain tools.", Integer.valueOf(tp), mid };
  String bw = @PKG@.GearRoll.blockWhy(mid, u);
  if (bw != null) return new Object[] { bw, Integer.valueOf(tp), mid };
  return new Object[] { null, Integer.valueOf(tp), mid };
}""")
# the most item srcId rolls for stat si at rarity r and level L (its own spare-slot boost included; the 0.2.17 tool caps). The merge passes
# the MULTITOOL's id (fix round, critic 1): a pickaxe / hatchet pool has 3 keys, so its boost would let a line exceed what a fresh
# multitool (6-key pool, no boost) can roll at that rarity and level.
M(gmerge, r"""
public static int capOf(int si, String srcId, int r, int L) {
  int ps = @PKG@.GearRoll.pool(3, srcId).length;
  double b = @PKG@.GearRoll.spare(3, r, ps);
  int[] bb = b > 0.0 ? @PKG@.GearRoll.boundsX(si, r, L, 1.0 + b / 100.0) : @PKG@.GearRoll.bounds(si, r, L);
  return bb[1];
}""")
# one input's lines into best[] (value per stat) / frac[] (value / cap; the cap = mid's, the multitool's); returns the lines it dropped
# (not a multitool key, not positive); info[1] += the lines lowered to the cap
M(gmerge, r"""
public static int addLines(int[] best, double[] frac, @BD@ d, String mid, int r, int L, int[] info) {
  int dropped = 0;
  if (d == null) return 0;
  @BA@ ms = @PKG@.GearData.mods(d);
  for (int k = 0; k < ms.size(); k++) {
    @BV@ v = ms.get(k);
    if (v == null || !v.isDocument()) { dropped++; continue; }
    @BD@ m = v.asDocument();
    int si = @PKG@.GearDefs.sIndex(@PKG@.GearData.str(m, "s", null));
    int val = @PKG@.GearData.num(m, "v", 0);
    if (si < 0 || (@PKG@.GearDefs.S_TMASK[si] & (1 << 6)) == 0 || val <= 0) { dropped++; continue; }
    int hi = capOf(si, mid, r, L);
    if (val > hi) { val = hi; info[1]++; }
    if (val > best[si]) { best[si] = val; frac[si] = (double) val / (double) (hi < 1 ? 1 : hi); }
  }
  return dropped;
}""")
F(gmerge, "public static volatile int LAST_DROPPED = 0;")
F(gmerge, "public static volatile boolean AFTER_THROWS = false;")       # harness switch only (fix round: proves critic 4's fix)
# THE MERGED DOCUMENT (header 2); lvl = the multitool's craft level (GearRoll.craftLevel; -1 = no stamp). Two plain tools = the craft roll.
# info (fix round, critics 2 + 3; shown on the page before the click): [0] input lines lost (not a multitool key / over the line count),
# [1] lines lowered to the multitool cap, [2] the highest level of a rolled input, [3] the multitool's level
M(gmerge, r"""
public static @BD@ docI(String mid, @IS@ p, @IS@ h, java.util.UUID u, int lvl, int[] info) {
  @BD@ pd = inDoc(p);
  @BD@ hd = inDoc(h);
  if (plain(pd) && plain(hd)) return @PKG@.GearRoll.craftDoc(mid, u, lvl);
  if (!plain(pd)) info[2] = @PKG@.GearLevel.level(p.getItemId(), pd);
  if (!plain(hd) && @PKG@.GearLevel.level(h.getItemId(), hd) > info[2]) info[2] = @PKG@.GearLevel.level(h.getItemId(), hd);
  int rp = pd == null ? 0 : @PKG@.GearData.rarity(pd);
  int rh = hd == null ? 0 : @PKG@.GearData.rarity(hd);
  int r = rp >= rh ? rp : rh;
  if (r > 4) r = 0;
  @BD@ d = @PKG@.GearData.base(@PKG@.GearData.kindFor(mid), r, true, "merge");
  d.put("tr", new org.bson.BsonInt32(1));
  if (lvl >= 0) d.put("lvl", new org.bson.BsonInt32(@PKG@.GearLevel.clamp(lvl)));
  int L = @PKG@.GearLevel.level(mid, d);
  int n = @PKG@.GearDefs.NS;
  int[] best = new int[n];
  double[] frac = new double[n];
  info[3] = L;
  int dropped = addLines(best, frac, pd, mid, r, L, info) + addLines(best, frac, hd, mid, r, L, info);
  int cnt = @PKG@.GearCfg.R_MODS[@PKG@.GearCfg.ri(r)];
  boolean[] keep = new boolean[n];
  for (int k = 0; k < cnt; k++) {
    int sel = -1;
    for (int i = 0; i < n; i++) {
      if (keep[i] || best[i] <= 0) continue;
      if (sel < 0 || frac[i] > frac[sel]) sel = i;
    }
    if (sel < 0) break;
    keep[sel] = true;
  }
  @BA@ out = new @BA@();
  for (int i = 0; i < n; i++) {
    if (best[i] <= 0) continue;
    if (keep[i]) out.add(@PKG@.GearData.mod(@PKG@.GearDefs.S_KEY[i], best[i]));
    else dropped++;
  }
  d.put("mods", out);
  int rf = @PKG@.GearData.num(pd, "rfN", 0);
  int rf2 = @PKG@.GearData.num(hd, "rfN", 0);
  if (rf2 > rf) rf = rf2;
  if (rf > 0) d.put("rfN", new org.bson.BsonInt32(rf));
  String nm = rh > rp ? @PKG@.GearData.str(hd, "rf", null) : @PKG@.GearData.str(pd, "rf", null);
  if (nm == null) nm = rh > rp ? @PKG@.GearData.str(pd, "rf", null) : @PKG@.GearData.str(hd, "rf", null);
  if (nm != null) d.put("rf", new org.bson.BsonString(nm));
  info[0] = dropped;
  return d;
}""")
M(gmerge, r"""
public static @BD@ doc(String mid, @IS@ p, @IS@ h, java.util.UUID u, int lvl) {
  int[] info = new int[4];
  @BD@ d = docI(mid, p, h, u, lvl, info);
  LAST_DROPPED = info[0];
  return d;
}""")
# what the merge loses, in words ("" = nothing): the page shows it in gold before the click
M(gmerge, r"""
public static String lossText(int[] info) {
  String w = "";
  if (info[0] > 0) w = info[0] + (info[0] == 1 ? " line does" : " lines do") + " not fit and will be lost";
  if (info[2] > info[3]) w = w + (w.length() > 0 ? "; " : "") + "it is made at Lv " + info[3] + " (your tool is Lv " + info[2] + ")";
  if (info[1] > 0) w = w + (w.length() > 0 ? "; " : "") + info[1] + (info[1] == 1 ? " line is" : " lines are") + " lowered to the multitool's limit";
  return w.length() > 0 ? "Warning: " + w + "." : "";
}""")
# Object[] { String why, String multitool id, BD preview document (null = two plain tools: rolls on merge), Boolean both plain, Integer level,
# String loss warning ("" = nothing lost) }
M(gmerge, r"""
public static Object[] preview(@IS@ p, @IS@ h, java.util.UUID u) {
  Object[] c = check(p, h, u);
  if (c[0] != null) return new Object[] { c[0], c[2], null, Boolean.FALSE, Integer.valueOf(-1), "" };
  String mid = (String) c[2];
  int lvl = @PKG@.GearRoll.craftLevel(mid, u);
  boolean both = plain(inDoc(p)) && plain(inDoc(h));
  int[] info = new int[4];
  @BD@ d = both ? null : docI(mid, p, h, u, lvl, info);
  return new Object[] { null, mid, d, Boolean.valueOf(both), Integer.valueOf(lvl), both ? "" : lossText(info) };
}""")
# every pickaxe / hatchet of a multitool tier the player carries: int[] { section, slot }
M(gmerge, r"""
public static java.util.ArrayList rows(@INV@ inv) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (inv == null) return out;
  for (int k = 0; k < @PKG@.GearStamp.SCAN.length; k++) {
    @IC@ c = @PKG@.GearStamp.section(inv, @PKG@.GearStamp.SCAN[k]);
    if (c == null) continue;
    for (int i = 0; i < c.getCapacity(); i++) {
      @IS@ it = c.getItemStack((short) i);
      if (it == null || it.isEmpty() || famOf(it.getItemId()) == 0) continue;
      out.add(new int[] { @PKG@.GearStamp.SCAN[k], i });
    }
  }
  return out;
}""")
M(gmerge, r"""
public static String json(@IS@ s) {
  if (s == null) return "none";
  @BD@ g = @PKG@.GearData.gearDoc(s.getMetadata());
  return g == null ? (s.getMetadata() == null ? "plain" : "meta:" + s.getMetadata().toJson()) : g.toJson();
}""")
M(gmerge, r"""
public static boolean empty(@IC@ c, int slot) {
  @IS@ x = c.getItemStack((short) slot);
  return x == null || x.isEmpty();
}""")
# after a made merge: the count check + the MERGE line (never throws into merge())
M(gmerge, r"""
public static void after(@IC@[] all, String pid, String hid, String mid, int bp, int bh, int bm, String who, java.util.UUID u, @BD@ nd, int[] info, int ps, int pslot) {
  if (AFTER_THROWS) throw new IllegalStateException("harness: after() throws");
  int ap = @PKG@.GearStamp.countId(all, pid);
  int ah = @PKG@.GearStamp.countId(all, hid);
  int am = @PKG@.GearStamp.countId(all, mid);
  if (ap != bp - 1 || ah != bh - 1 || am != bm + 1) {
    @PKG@.Gear.warn("MULTITOOL MERGE COUNT MISMATCH for " + who + ": " + pid + " " + bp + "->" + ap + ", " + hid + " " + bh + "->" + ah + ", " + mid + " " + bm + "->" + am);
    @PKG@.GearLog.line("MERGE-COUNT " + who + " " + u + " " + pid + " " + bp + "->" + ap + " " + hid + " " + bh + "->" + ah + " " + mid + " " + bm + "->" + am);
  }
  @PKG@.GearLog.line("MERGE " + who + " " + u + " " + mid + " " + @PKG@.GearDefs.R_ID[@PKG@.GearData.rarity(nd)] + " lv" + @PKG@.GearLevel.level(mid, nd) + " [" + @PKG@.GearView.modSummary(nd) + "] rfN " + @PKG@.GearData.num(nd, "rfN", 0) + " dropped " + info[0] + " lowered " + info[1] + " @" + @PKG@.GearForge.where(ps, pslot));
}""")
# THE WRITE (header 4). Object[] { Integer code (1 made, 0 refused - nothing moved, -1 failed - see the message), String message, IS the
# multitool, BD its document }
M(gmerge, r"""
public static Object[] merge(@INV@ inv, int ps, int pslot, String pid, String pfp, int hs, int hslot, String hid, String hfp, java.util.UUID u, String who) {
  @IC@ pc = @PKG@.GearStamp.section(inv, ps);
  @IC@ hc = @PKG@.GearStamp.section(inv, hs);
  if (pc == null || hc == null) return new Object[] { Integer.valueOf(0), "A tool moved or changed - pick it again.", null, null };
  if (pc == hc && pslot == hslot) return new Object[] { Integer.valueOf(0), "Pick a pickaxe and a hatchet (two different slots).", null, null };
  @IS@ p = @PKG@.GearStamp.at(inv, ps, pslot);
  @IS@ h = @PKG@.GearStamp.at(inv, hs, hslot);
  if (!@PKG@.GearForge.same(p, pid, pfp) || !@PKG@.GearForge.same(h, hid, hfp)) return new Object[] { Integer.valueOf(0), "A tool moved or changed - pick it again.", null, null };
  Object[] c = check(p, h, u);
  if (c[0] != null) return new Object[] { Integer.valueOf(0), (String) c[0], null, null };
  String mid = (String) c[2];
  int lvl = @PKG@.GearRoll.craftLevel(mid, u);
  @BD@ nd = null;
  @IS@ ms = null;
  int[] info = new int[4];
  try {
    nd = docI(mid, p, h, u, lvl, info);
    ms = @PKG@.GearData.put(new @IS@(mid, 1), nd, u);
  } catch (Throwable t0) { nd = null; ms = null; @PKG@.Gear.warn("multitool merge: the document could not be made for " + who + ": " + t0); }
  if (nd == null || ms == null || ms.isEmpty()) return new Object[] { Integer.valueOf(0), "The multitool could not be made - nothing was used.", null, null };
  @IC@[] all = @PKG@.GearStamp.allOf(inv);
  int bp = @PKG@.GearStamp.countId(all, pid);
  int bh = @PKG@.GearStamp.countId(all, hid);
  int bm = @PKG@.GearStamp.countId(all, mid);
  String r = @PKG@.GearDefs.R_ID[@PKG@.GearData.rarity(nd)];
  @PKG@.GearLog.line("MERGE-BEGIN " + who + " " + u + " " + pid + " @" + @PKG@.GearForge.where(ps, pslot) + " " + json(p) + " + " + hid + " @" + @PKG@.GearForge.where(hs, hslot) + " " + json(h) + " -> " + mid + " " + r + " lv" + lvl);
  try { @PKG@.GearLog.flush(); } catch (Throwable xf) { }     // fix round (critic 3): MERGE-BEGIN is ON DISK before the hatchet moves
  // (a) the hatchet leaves first: a crash before (b) can only lose it (its document is in MERGE-BEGIN), never copy anything
  Object t1 = null;
  Throwable e1 = null;
  try { t1 = hc.removeItemStackFromSlot((short) hslot); } catch (Throwable x1) { e1 = x1; }
  boolean gone = e1 == null && !(t1 instanceof @TXN@ && !((@TXN@) t1).succeeded()) && empty(hc, hslot);
  if (!gone) {
    String why1 = e1 != null ? String.valueOf(e1) : "the inventory refused it";
    if (empty(hc, hslot)) {
      Object tb = null;
      try { tb = hc.setItemStackForSlot((short) hslot, h); } catch (Throwable xb) { tb = null; }
      if (!@PKG@.GearForge.same(hc.getItemStack((short) hslot), hid, hfp)) {
        @PKG@.Gear.warn("MULTITOOL MERGE: the hatchet of " + who + " (" + u + ") could not be put back - its document is in gear.log (MERGE-RESTORE-FAILED)");
        @PKG@.GearLog.line("MERGE-RESTORE-FAILED " + who + " " + u + " " + hid + " " + json(h) + ": " + why1);
        return new Object[] { Integer.valueOf(-1), "Something went wrong and your hatchet could not be put back - an admin can find it in the server log.", null, null };
      }
    }
    @PKG@.GearLog.line("MERGE-FAILED " + who + " " + u + " (hatchet not taken: " + why1 + ")");
    return new Object[] { Integer.valueOf(-1), "The inventory refused the change - nothing was used.", null, null };
  }
  // (b) the pickaxe's slot gets the multitool
  Object t2 = null;
  Throwable e2 = null;
  try { t2 = pc.setItemStackForSlot((short) pslot, ms); } catch (Throwable x2) { e2 = x2; }
  @IS@ now = pc.getItemStack((short) pslot);
  boolean put = e2 == null && !(t2 instanceof @TXN@ && !((@TXN@) t2).succeeded()) && now != null && !now.isEmpty() && mid.equals(now.getItemId());
  if (!put) {
    String why2 = e2 != null ? String.valueOf(e2) : "the inventory refused it";
    boolean pk = @PKG@.GearForge.same(now, pid, pfp);
    Object tr = null;
    try { tr = hc.setItemStackForSlot((short) hslot, h); } catch (Throwable xr) { tr = null; }
    boolean back = @PKG@.GearForge.same(hc.getItemStack((short) hslot), hid, hfp);
    if (!back || !pk) {
      @PKG@.Gear.warn("MULTITOOL MERGE FAILED for " + who + " (" + u + "): " + why2 + (back ? "" : " - the hatchet could not be put back") + (pk ? "" : " - the pickaxe slot changed") + "; both documents are in gear.log");
      @PKG@.GearLog.line("MERGE-RESTORE-FAILED " + who + " " + u + " " + pid + " " + json(p) + " + " + hid + " " + json(h) + ": " + why2 + " (hatchet back " + back + ", pickaxe kept " + pk + ")");
      return new Object[] { Integer.valueOf(-1), "Something went wrong - an admin can find your tools in the server log.", null, null };
    }
    @PKG@.GearLog.line("MERGE-FAILED " + who + " " + u + " (multitool not written: " + why2 + ") - RESTORED, nothing used");
    return new Object[] { Integer.valueOf(-1), "The inventory refused the multitool - nothing was used.", null, null };
  }
  // fix round (critic 4): the items have moved - the bookkeeping below can never turn a made merge into an error
  try { after(all, pid, hid, mid, bp, bh, bm, who, u, nd, info, ps, pslot); } catch (Throwable xa) { }
  return new Object[] { Integer.valueOf(1), "Made!", ms, nd };
}""")

# ================================================================= MultiPage: /multitool (the Reforge page's vanilla look)
for _f in ("public java.util.ArrayList rows;", "public int pageNo;", "public int pSec;", "public int pSlot;", "public String pId;", "public String pFp;",
           "public int hSec;", "public int hSlot;", "public String hId;", "public String hFp;", "public String info;", "public String epoch;",
           "public long lastClick;", "public @BD@ made;", "public String madeId;"):
    F(mpg, _f)
C(mpg, r"""
public MultiPage(@PR@ pr) {
  super(pr, @LIFE@.CanDismiss);
  this.rows = new java.util.ArrayList();
  this.pageNo = 0;
  this.pSec = -1; this.pSlot = -1; this.pId = null; this.pFp = null;
  this.hSec = -1; this.hSlot = -1; this.hId = null; this.hFp = null;
  this.info = ""; this.lastClick = 0L; this.made = null; this.madeId = null;
  this.epoch = @PKG@.Gear.epoch(pr.getUuid());
}""")
M(mpg, "public void clearP() { this.pSec = -1; this.pSlot = -1; this.pId = null; this.pFp = null; }")
M(mpg, "public void clearH() { this.hSec = -1; this.hSlot = -1; this.hId = null; this.hFp = null; }")
# pick (or put back) a pickaxe / hatchet; false = nothing there
M(mpg, r"""
public boolean pick(@INV@ inv, int s, int slot) {
  @IS@ it = @PKG@.GearStamp.at(inv, s, slot);
  if (it == null || it.isEmpty()) return false;
  int f = @PKG@.GearMerge.famOf(it.getItemId());
  if (f == 0) return false;
  String ep = @PKG@.Gear.epoch(this.playerRef.getUuid());
  if (!ep.equals(this.epoch)) { clearP(); clearH(); this.epoch = ep; }
  this.made = null; this.madeId = null;
  String nm = @PKG@.Gear.itemName(it.getItemId());
  if (f == 1) {
    if (s == this.pSec && slot == this.pSlot) { clearP(); this.info = "=" + nm + " put back."; return true; }
    this.pSec = s; this.pSlot = slot; this.pId = it.getItemId(); this.pFp = @PKG@.GearForge.fp(it);
    this.info = "=" + nm + " is the pickaxe.";
    return true;
  }
  if (s == this.hSec && slot == this.hSlot) { clearH(); this.info = "=" + nm + " put back."; return true; }
  this.hSec = s; this.hSlot = slot; this.hId = it.getItemId(); this.hFp = @PKG@.GearForge.fp(it);
  this.info = "=" + nm + " is the hatchet.";
  return true;
}""")
M(mpg, r"""
public void preselect(@INV@ inv) {
  try {
    if (inv == null) return;
    if (inv.usingToolsItem()) pick(inv, 5, (int) inv.getActiveToolsSlot());
    else pick(inv, 0, (int) inv.getActiveHotbarSlot());
  } catch (Throwable t) { }
}""")
# one picked tool line: icon + name (rarity colour) + where / what
M(mpg, r"""
public void slotLine(@UCB@ b, String gid, String what, @IS@ it, int s, int slot) {
  b.appendInline("#SkyyGAnvil", "Group " + gid + " { Anchor: (Height: 62); LayoutMode: Left; Padding: (Top: 6); }");
  b.appendInline(gid, "Group " + gid + "I { Anchor: (Width: 52, Height: 52); Background: #000000(0.25); }");
  if (it != null) b.appendInline(gid + "I", "ItemIcon { Anchor: (Width: 44, Height: 44, Left: 4, Top: 4); ItemId: \"" + @PKG@.Gear.safe(it.getItemId()) + "\"; }");
  b.appendInline(gid, "Label { Anchor: (Width: 12, Height: 52); Text: \"\"; }");
  b.appendInline(gid, "Group " + gid + "T { Anchor: (Width: 490, Height: 52); LayoutMode: Top; }");
  @BD@ d = it == null ? null : @PKG@.GearMerge.inDoc(it);
  int r = d == null ? 0 : @PKG@.GearData.rarity(d);
  b.appendInline(gid + "T", "Label " + gid + "N { Anchor: (Height: 28); Text: \"\"; Style: (FontSize: 17, RenderBold: true, TextColor: " + (it == null ? "#ffffff" : @PKG@.ReforgePage.rarHex(r)) + ", VerticalAlignment: Center); }");
  b.appendInline(gid + "T", "Label " + gid + "S { Anchor: (Height: 22); Text: \"\"; Style: (FontSize: 14, TextColor: #ffffff(0.6), VerticalAlignment: Center); }");
  if (it == null) {
    b.set(gid + "N.Text", what + ": none picked");
    b.set(gid + "S.Text", "Click a " + what.toLowerCase() + " in the list.");
    return;
  }
  String id = it.getItemId();
  b.set(gid + "N.Text", d == null ? @PKG@.Gear.itemName(id) : @PKG@.GearView.nameText(id, d));
  b.set(gid + "S.Text", what + " - " + (@PKG@.GearMerge.plain(d) ? "plain (counts as Normal)" : @PKG@.GearDefs.R_NAME[r] + ", " + @PKG@.GearData.mods(d).size() + " line(s)") + " - Lv " + @PKG@.GearLevel.level(id, d) + " - in your " + @PKG@.GearForge.where(s, slot));
}""")
M(mpg, r"""
public void bench(@UCB@ b, @UEB@ ev, java.util.UUID u, @IS@ p, @IS@ h) {
  b.appendInline("#SkyyGMain", "Group #SkyyGAnvil { Anchor: (Width: 562); LayoutMode: Top; }");
  b.appendInline("#SkyyGAnvil", "Label #SkyyGAnvilT { Anchor: (Height: 35); Padding: (Horizontal: 8); Text: \"\"; Style: (RenderBold: true, VerticalAlignment: Center, FontSize: 15, TextColor: #afc2c3); }");
  b.set("#SkyyGAnvilT.Text", "Merge");
  b.appendInline("#SkyyGAnvil", "Group { Anchor: (Height: 1); Background: #393426(0.5); }");
  slotLine(b, "#SkyyGPk", "Pickaxe", p, this.pSec, this.pSlot);
  slotLine(b, "#SkyyGHt", "Hatchet", h, this.hSec, this.hSlot);
  b.appendInline("#SkyyGAnvil", "Group { Anchor: (Height: 1); Background: #2b3542; }");
  b.appendInline("#SkyyGAnvil", "Label #SkyyGResN { Anchor: (Height: 32); Text: \"\"; Style: (FontSize: 19, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }");
  b.appendInline("#SkyyGAnvil", "Label #SkyyGResS { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 15, TextColor: #96a9be, VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); }");
  b.appendInline("#SkyyGAnvil", "Group #SkyyGCols { Anchor: (Height: 300); LayoutMode: Left; Padding: (Top: 4); }");
  String why = null;
  String loss = "";
  if (this.made != null && this.madeId != null) {
    int r = @PKG@.GearData.rarity(this.made);
    b.set("#SkyyGResN.Text", "Made: " + @PKG@.GearView.nameText(this.madeId, this.made));
    b.set("#SkyyGResS.Text", @PKG@.GearDefs.R_NAME[r].toUpperCase() + " MULTITOOL - Lv " + @PKG@.GearLevel.level(this.madeId, this.made) + " - it is in the pickaxe's slot.");
    @PKG@.ReforgePage.column(b, "#SkyyGCols", "#SkyyGColR", "Its lines", "#ffffff", this.madeId, this.made, 562);
  } else if (p == null || h == null) {
    b.set("#SkyyGResN.Text", "Result");
    b.set("#SkyyGResS.Text", "Pick a pickaxe and a hatchet of the same tier.");
    why = "Pick a " + (p == null ? "pickaxe" : "hatchet") + " from the list.";
  } else {
    Object[] pv = @PKG@.GearMerge.preview(p, h, u);
    why = (String) pv[0];
    if (why != null) {
      b.set("#SkyyGResN.Text", "Result");
      b.set("#SkyyGResS.Text", "These two cannot be merged:");
    } else if (((Boolean) pv[3]).booleanValue()) {
      String mid = (String) pv[1];
      int lv = ((Integer) pv[4]).intValue();
      b.set("#SkyyGResN.Text", @PKG@.Gear.itemName(mid));
      b.set("#SkyyGResS.Text", "Both tools are plain: it rolls a rarity like a crafted multitool" + (lv >= 0 ? " - Lv " + lv : "") + ".");
    } else {
      String mid = (String) pv[1];
      @BD@ d = (@BD@) pv[2];
      loss = (String) pv[5];
      int r = @PKG@.GearData.rarity(d);
      b.set("#SkyyGResN.Text", @PKG@.GearView.nameText(mid, d));
      b.set("#SkyyGResS.Text", @PKG@.GearDefs.R_NAME[r].toUpperCase() + " MULTITOOL - Lv " + @PKG@.GearLevel.level(mid, d) + " (made at your level) - " + @PKG@.GearData.mods(d).size() + " line(s)");
      @PKG@.ReforgePage.column(b, "#SkyyGCols", "#SkyyGColR", "It will have", "#ffffff", mid, d, 562);
    }
  }
  b.appendInline("#SkyyGAnvil", "Label #SkyyGWhy { Anchor: (Height: 66); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + @PKG@.GearDefs.C_GOLD + ", VerticalAlignment: Center, Wrap: true); }");
  b.set("#SkyyGWhy.Text", this.made != null ? "Pick two more tools to make another one." : (why == null ? "Both tools are used up. No coins." + (loss.length() > 0 ? " " + loss : "") : why));
  boolean off = why != null || this.made != null;
  String lbl = this.made != null ? "Merged" : (off ? "Cannot merge" : "Make multitool");   // fix round (critic C3): no "Cannot merge" after a success
  b.appendInline("#SkyyGAnvil", "Group #SkyyGGo { Anchor: (Height: 56); LayoutMode: Left; Padding: (Top: 8); }");
  b.appendInline("#SkyyGGo", "TextButton #SkyyGBtnMerge { Anchor: (Width: 270, Height: 44); Text: \"" + lbl + "\"; " + @PKG@.GearUi.btn(off ? 3 : 0) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyGBtnMerge", @EVD@.of("a", "merge"));
}""")
M(mpg, r"""
public void list(@UCB@ b, @UEB@ ev, @INV@ inv) {
  boolean t = @PKG@.GearUi.tex();
  b.appendInline("#SkyyGMain", "Group #SkyyGListBox { Anchor: (Width: 470); LayoutMode: Top; }");
  b.appendInline("#SkyyGListBox", "Group #SkyyGListHead { Anchor: (Height: 30); LayoutMode: Left; Padding: (Right: 15, Bottom: 5); }");
  b.appendInline("#SkyyGListHead", "Label #SkyyGHeadItem { Anchor: (Width: 300); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }");
  b.appendInline("#SkyyGListHead", "Label #SkyyGHeadRar { Anchor: (Width: 150); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: #ffffff, HorizontalAlignment: End, VerticalAlignment: Center); }");
  b.set("#SkyyGHeadItem.Text", "Pickaxes + hatchets (" + this.rows.size() + ")");
  b.set("#SkyyGHeadRar.Text", "Rarity - Level");
  int per = t ? 200 : 12;
  int pages = (this.rows.size() + per - 1) / per;
  if (pages < 1) pages = 1;
  if (this.pageNo >= pages) this.pageNo = pages - 1;
  if (this.pageNo < 0) this.pageNo = 0;
  int start = this.pageNo * per;
  if (t) b.appendInline("#SkyyGListBox", "Group #SkyyGList { Anchor: (Height: 634); LayoutMode: TopScrolling; " + @PKG@.GearUi.scroll() + " }");
  else b.appendInline("#SkyyGListBox", "Group #SkyyGList { Anchor: (Height: 590); LayoutMode: Top; }");
  if (this.rows.isEmpty()) {
    b.appendInline("#SkyyGList", "Label #SkyyGEmpty1 { Anchor: (Height: 40); Text: \"\"; Style: (FontSize: 16, TextColor: #96a9be, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyGEmpty1.Text", "No pickaxes or hatchets on you.");
    b.appendInline("#SkyyGList", "Label #SkyyGEmpty2 { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 15, TextColor: #878e9c, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyGEmpty2.Text", "Carry a pickaxe and a hatchet of one tier and click Refresh.");
  }
  for (int i = start; i < this.rows.size() && i < start + per; i++) {
    int[] rw = (int[]) this.rows.get(i);
    @IS@ it = @PKG@.GearStamp.at(inv, rw[0], rw[1]);
    if (it == null || it.isEmpty()) continue;
    String id = it.getItemId();
    @BD@ d = @PKG@.GearMerge.inDoc(it);
    int r = d == null ? 0 : @PKG@.GearData.rarity(d);
    boolean on = (rw[0] == this.pSec && rw[1] == this.pSlot) || (rw[0] == this.hSec && rw[1] == this.hSlot);
    String rid = "#SkyyGRow" + i;
    b.appendInline("#SkyyGList", "Button " + rid + " { Anchor: (Height: 44); LayoutMode: Left; Padding: (Full: 6); " + @PKG@.GearUi.rowStyle(on) + " ItemIcon { Anchor: (Width: 32, Height: 32); ItemId: \"" + @PKG@.Gear.safe(id) + "\"; } Label #SkyyGRowName" + i + " { Anchor: (Width: 262); Padding: (Horizontal: 10, Vertical: 5); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + @PKG@.ReforgePage.rarHex(r) + ", VerticalAlignment: Center); } Label #SkyyGRowSub" + i + " { Anchor: (Width: 140); Padding: (Horizontal: 10, Vertical: 5); Text: \"\"; Style: (FontSize: 14, TextColor: #ffffff(0.6), HorizontalAlignment: End, VerticalAlignment: Center); } }");
    b.set("#SkyyGRowName" + i + ".Text", (d == null ? @PKG@.Gear.itemName(id) : @PKG@.GearView.nameText(id, d)) + (on ? "  (picked)" : ""));
    b.set("#SkyyGRowSub" + i + ".Text", (@PKG@.GearMerge.plain(d) ? "Plain" : @PKG@.GearDefs.R_NAME[r]) + " - Lv " + @PKG@.GearLevel.level(id, d));
    b.appendInline("#SkyyGList", "Group { Anchor: (Height: 2); Background: #ffffff(0.6); }");
    ev.addEventBinding(@BT@.Activating, rid, @EVD@.of("a", "sel:" + i));
  }
  if (!t && pages > 1) {
    b.appendInline("#SkyyGListBox", "Group #SkyyGNav { Anchor: (Height: 44); LayoutMode: Left; Padding: (Top: 4); }");
    b.appendInline("#SkyyGNav", "TextButton #SkyyGBtnPrev { Anchor: (Width: 140, Height: 36); Text: \"Prev\"; " + @PKG@.GearUi.btn(1) + " }");
    b.appendInline("#SkyyGNav", "Label #SkyyGPageTxt { Anchor: (Width: 170, Height: 36); Text: \"\"; Style: (FontSize: 15, TextColor: #96a9be, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyGPageTxt.Text", "Page " + (this.pageNo + 1) + " / " + pages);
    b.appendInline("#SkyyGNav", "TextButton #SkyyGBtnNext { Anchor: (Width: 140, Height: 36); Text: \"Next\"; " + @PKG@.GearUi.btn(1) + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyGBtnPrev", @EVD@.of("a", "prev"));
    ev.addEventBinding(@BT@.Activating, "#SkyyGBtnNext", @EVD@.of("a", "next"));
  }
}""")
M(mpg, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  @PLA@ pl = null;
  try { pl = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { pl = null; }
  @INV@ inv = pl == null ? null : pl.getInventory();
  @IS@ p = null;
  @IS@ h = null;
  if (this.pSec >= 0) {
    p = @PKG@.GearStamp.at(inv, this.pSec, this.pSlot);
    if (!@PKG@.GearForge.same(p, this.pId, this.pFp)) { p = null; clearP(); if (this.made == null) this.info = "-The pickaxe moved or changed - pick it again."; }
  }
  if (this.hSec >= 0) {
    h = @PKG@.GearStamp.at(inv, this.hSec, this.hSlot);
    if (!@PKG@.GearForge.same(h, this.hId, this.hFp)) { h = null; clearH(); if (this.made == null) this.info = "-The hatchet moved or changed - pick it again."; }
  }
  this.rows = @PKG@.GearMerge.rows(inv);
  @PKG@.GearUi.frame(b, "Multitool", 1100, 880);
  b.appendInline("#SkyyGBody", "Label #SkyyGSub { Anchor: (Height: 28); Text: \"\"; Style: (FontSize: 16, TextColor: #96a9be, VerticalAlignment: Center); }");
  b.set("#SkyyGSub.Text", "Pick a pickaxe and a hatchet of the same tier. The multitool keeps the better rarity and both tools' lines.");
  b.appendInline("#SkyyGBody", "Group #SkyyGMain { Anchor: (Height: 680); LayoutMode: Left; Padding: (Top: 6); }");
  list(b, ev, inv);
  b.appendInline("#SkyyGMain", "Label { Anchor: (Width: 14); Text: \"\"; }");
  b.appendInline("#SkyyGMain", @PKG@.GearUi.vsep());
  b.appendInline("#SkyyGMain", "Label { Anchor: (Width: 14); Text: \"\"; }");
  bench(b, ev, u, p, h);
  boolean menu = @PKG@.Gear.bget("config:def:SkyyMenu") != null;
  b.appendInline("#SkyyGBody", "Group #SkyyGBar { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 10); }");
  b.appendInline("#SkyyGBar", "Label #SkyyGInfo { Anchor: (Width: 700, Height: 44); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: " + @PKG@.GearUi.infoColor(this.info) + ", VerticalAlignment: Center); }");
  b.set("#SkyyGInfo.Text", @PKG@.GearUi.infoText(this.info));
  b.appendInline("#SkyyGBar", "TextButton #SkyyGBtnRefresh { Anchor: (Width: 170, Height: 44); Text: \"Refresh\"; " + @PKG@.GearUi.btn(1) + " }");
  b.appendInline("#SkyyGBar", "Label { Anchor: (Width: 12, Height: 44); Text: \"\"; }");
  b.appendInline("#SkyyGBar", "TextButton #SkyyGBtnBack { Anchor: (Width: 170, Height: 44); Text: \"" + (menu ? "Back" : "Close") + "\"; " + @PKG@.GearUi.btn(2) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyGBtnRefresh", @EVD@.of("a", "refresh"));
  ev.addEventBinding(@BT@.Activating, "#SkyyGBtnBack", @EVD@.of("a", "back"));
}""")
# the merge click: double-click guard -> profile:busy -> both picks -> epoch -> GearMerge.merge (re-checks everything, writes, logs)
M(mpg, r"""
public void doMerge(@INV@ inv) {
  long now = System.currentTimeMillis();
  if (now - this.lastClick < 400L) return;
  this.lastClick = now;
  java.util.UUID u = this.playerRef.getUuid();
  if (@PKG@.Gear.busy(u)) { this.info = "-Your profile is still loading - nothing was merged. Try again in a moment."; return; }
  if (this.pSec < 0 || this.hSec < 0) { this.info = "-Pick a pickaxe and a hatchet first."; return; }
  String ep = @PKG@.Gear.epoch(u);
  if (!ep.equals(this.epoch)) { clearP(); clearH(); this.epoch = ep; this.info = "-Your profile changed - pick the tools again."; return; }
  Object[] res = @PKG@.GearMerge.merge(inv, this.pSec, this.pSlot, this.pId, this.pFp, this.hSec, this.hSlot, this.hId, this.hFp, u, this.playerRef.getUsername());
  int code = ((Integer) res[0]).intValue();
  if (code == 1) {
    @BD@ d = (@BD@) res[3];
    this.made = d;
    this.madeId = ((@IS@) res[2]).getItemId();
    this.info = "+Made a " + @PKG@.GearDefs.R_NAME[@PKG@.GearData.rarity(d)] + " " + @PKG@.Gear.itemName(this.madeId) + "!";
    clearP();
    clearH();
    return;
  }
  String msg = (String) res[1];
  if (msg != null && msg.startsWith("A tool moved")) { clearP(); clearH(); }
  this.info = "-" + msg;
}""")
M(mpg, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    String a = @PKG@.Gear.jsonStr(data, "a");
    if (a.length() == 0) return;
    if (a.equals("refresh")) { this.info = ""; this.made = null; this.madeId = null; rebuild(); return; }
    if (a.equals("prev")) { this.pageNo--; rebuild(); return; }
    if (a.equals("next")) { this.pageNo++; rebuild(); return; }
    if (a.equals("back")) {
      if (@PKG@.Gear.bget("config:def:SkyyMenu") != null) {
        try { @CMGR@.get().handleCommand(this.playerRef, "skymenu"); return; } catch (Throwable t1) { }
      }
      close();
      return;
    }
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    @INV@ inv = p == null ? null : p.getInventory();
    if (inv == null) return;
    if (a.startsWith("sel:")) {
      int i = -1;
      try { i = Integer.parseInt(a.substring(4)); } catch (Throwable t) { i = -1; }
      if (i < 0 || this.rows == null || i >= this.rows.size()) return;
      int[] r = (int[]) this.rows.get(i);
      if (!pick(inv, r[0], r[1])) this.info = "-That tool is not there any more.";
      rebuild();
      return;
    }
    if (a.equals("merge")) { doMerge(inv); rebuild(); return; }
  } catch (Throwable t) { @PKG@.Gear.warn("multitool page click failed: " + t); }
}""")
# ================================================================= /multitool (player command)
C(mtc, r"""
public MultiCmd() {
  super("multitool", "Open the Multitool page: merge a pickaxe and a hatchet of the same tier into a multitool that keeps their rolls");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(mtc, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    if (!@PKG@.GearCfg.MULTI_ON) { pr.sendMessage(@MSG@.raw("[Multitool] Multitools are switched off on this server.").color(@PKG@.GearDefs.C_GOLD)); return; }
    if (!@PKG@.GearMerge.loaded()) { pr.sendMessage(@MSG@.raw("[Multitool] The Multitools mod is not loaded on this server.").color(@PKG@.GearDefs.C_GOLD)); return; }
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null) { pr.sendMessage(@MSG@.raw("[Multitool] no player found")); return; }
    @PKG@.GearStamp.scan(pr, p.getInventory());
    @PKG@.MultiPage page = new @PKG@.MultiPage(pr);
    page.preselect(p.getInventory());
    p.getPageManager().openCustomPage(ref, store, page);
  } catch (Throwable t) {
    @PKG@.Gear.warn("/multitool failed: " + t);
    pr.sendMessage(@MSG@.raw("[Multitool] could not open the Multitool page - the server log has the details"));
  }
}""")

'''
rep('''# ####################################################################################################################################
# PART B (2/2): /identify (spec 5.7, pages 5.8).''', MERGE_PY + '''# ####################################################################################################################################
# PART B (2/2): /identify (spec 5.7, pages 5.8).''')

# ================================================================================================================ 3. setup + ready line + class list
rep('''  getCommandRegistry().registerCommand(new @PKG@.ReforgeCmd());
  getCommandRegistry().registerCommand(new @PKG@.GearCmd());''',
    '''  getCommandRegistry().registerCommand(new @PKG@.ReforgeCmd());
  getCommandRegistry().registerCommand(new @PKG@.MultiCmd());          // 0.2.21: merge rolled pickaxes / hatchets into a multitool
  getCommandRegistry().registerCommand(new @PKG@.GearCmd());''')
rep('''log("[SkyyGear] @VER@ ready - /reforge, /identify, /gear (admin:''', '''log("[SkyyGear] @VER@ ready - /reforge, /identify, /multitool, /gear (admin:''')
rep('''+ UB_CLASSES + TOOL_MULTI_CLASSES
assert len(set(str(c.getName()) for c in ALL)) == len(ALL), "a class is listed twice"''',
    '''+ UB_CLASSES + TOOL_MULTI_CLASSES + MERGE_CLASSES
assert len(set(str(c.getName()) for c in ALL)) == len(ALL), "a class is listed twice"''')

# ================================================================================================================ 4. manifest
rep('''multitools of the Multitools mod (by InkBlindCat, MIT) cost a pickaxe + hatchet of their tier and count as both tools''',
    '''multitools of the Multitools mod (by InkBlindCat, MIT) cost a pickaxe + hatchet of their tier and count as both tools (/multitool merges rolled ones: the better rarity, both tools' lines)''')

open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", DST)
