"""Derive SkyySacks/build_skyysacks_0.7.17.py from the SET pin 0.7.16 (edit THIS file, then regenerate: python tools/sacks_0_7_17_patch.py).
0.7.17 = round R2 of research/Requip-Smithing-Spec.md (section 5 contracts, section 6 R2 harness musts). Skyy's words (docs/answered/gear.md
153 / 158): "then also let it pull from the pocket dimension for blocks in the hot bar. (so they auto refill.)" and "we should give this,
and the crafting thing a filter by class. so it only shows things your class can use".

1. HOTBAR BLOCK SLOTS REFILL FROM THE BAGS (Requip "Pocket block" picks). SkyyWardrobe 0.2 publishes requip:pocket:<uuid> =
   java.util.Map<Integer slot, String itemId> (the reserved hotbar slots of the worn loadout). SweepTask.pocketFill (2 s tick, inside
   items(), after the 0.7.11 used-stack refill; and on demand through the new sacks:fn:pocketFill) fills each reserved hotbar slot that is
   EMPTY or holds a smaller plain stack of THAT item, up to its TARGET (review fix 3: requip:pocketN:<uuid> Map<Integer slot, Number> > 0
   (a contract addition for per-pick amounts), else SkyyWardrobe's Server Setup pocket.target via config:fn:SkyyWardrobe "get" > 0, else the
   item's max stack; never above the max stack), from the settled profile's pool:
     - hotbar only; a slot holding another item, or the same item WITH metadata, is never touched; slots not in the map are never touched;
     - only items with a Magic Bag home type (homeOf) whose bag (or the Omni) is carried; never a Magic Bag id; never a non-stacking item;
     - exactly what the slot gained leaves the pool (read back; more than asked = undone + warned), the live-mirror rule (BagMirror
       beforeTake / afterTake) and the KEPT count (the sweep never pulls it back), like the 0.7.11 refill;
     - DECISION: it follows the owner's master switch bags.refill (off = no pocket refill) but NOT the player's own refill mode (the
       loadout pick is the player's explicit opt-in; a player with "Off" on the bag page still gets the slots they reserved in Requip);
     - DECISION: the 0.7.11 sweepLeft skip (bag full + spare items in the main inventory) is not applied to reserved slots - the move is
       one-way (main inventory -> pool -> hotbar) and an emptied reserved slot must refill.
2. sacks:fn:deposit apply(Object[]{UUID, String itemId, Long qty, Integer hotbarSlot}) -> Long accepted: moves up to qty of the plain
   stack IN THAT HOTBAR SLOT into the bags, up to the bag room (caps() - pool); what does not fit stays in the slot. New items enter by
   catOf (the cooked-food rule of the sweep). CONTRACT DEVIATION (review fix 1): the 4th argument is REQUIRED - the spec's 3-argument form
   answers 0 and warns. The function takes the items from the live slot itself (a function that only credits the pool would be a free
   item source - the 0.7.13 "put is never a source" rule), so the caller must NOT lift the stack first: SkyyWardrobe 0.2 giveBack has to
   drop its takeOff / put-back and pass the slot (until it does, its give-back moves nothing and the blocks stay in the slot - never lost).
3. THE CRAFT BRIDGES the /smithing hub (SkyyGear 0.2.23) calls - the /craft rule in ONE place:
   sacks:fn:craftList {UUID, group} -> String[] recipe ids /craft would craft now: the merged Crafting / Smithing / Farming set (Fieldcraft +
     bench recipes whose bench accessory tier the player has in acc:has) that passes KnowSync.allowed, plus coll:recipes (the Collections
     tab), never a table-only / timed recipe. group "smith" = primary output Tool_* / Weapon_* / Armor_* (any bench), "craft" / "farm" = the
     /craft tab groups, "all" / null = everything (SkyyGear filters pack gear itself). null = paused / no player on this thread.
   sacks:fn:craftHave {UUID, recipeId} -> Object[]{Long times, String[] inputs ("res:<type>" for a resource type), Long[] have, Long[] need}
     (have = inventory + carried bags, the /craft count; while the profile settles: inventory only).
   sacks:fn:craftPay {UUID, recipeId, Integer times} -> Object[]{Long paid, String receipt, String reason}: the allow rule again, then the
     /craft payment exactly (materialsFor: the inventory first, then the bag mirror; the engine's removeMaterials; BagMirror.sync books the
     bag part). ALL OR NOTHING: paid = times or 0 (a short payment is rolled back inside the call: every inventory slot restored from its
     snapshot, the bag part credited back) - so "paid less than asked" never reaches the caller. A stack WITH metadata touched by the engine
     = the same rollback (never a metadata stack). The receipt records the inventory part and the bag part; crafts.log CRAFT-PAY.
     The 3rd answer element (reason when refused) is an addition. ENGINE FACT (found by the harness): removeMaterials takes a stack WITH
     metadata for a RESOURCE-TYPE input (an item-id input never does) - so craftHave / craftPay count and pay from a PLAIN COPY of the inventory
     (SackBridge.plainCopy: metadata stacks are never copied; applyCopy then takes exactly what the copy lost from the real slots, read back)
     and metaTouched rolls back anything that slips through anyway. Review fix 2: "plain" also means the durability / max durability /
   quality of a fresh stack (SweepTask.plainFresh) - a damaged tool is never paid with, so a refund (a fresh stack) never repairs one.
   Review fix 4: anything thrown after the bag debit rolls back the same way ("internal error - nothing was taken").
     (The /craft page and vanilla benches have the same resource-type exposure - unchanged here, reported.)
   sacks:fn:craftRefund {UUID, receipt} -> Long: once, by the same player, within 60 s, never after a commit: the bag part back into the
     pool it left, the inventory part back into the inventory (what does not fit: into the bags when the item has a bag home, else dropped
     at the player; never lost). Refused while the player's settled profile is not the receipt's (a switch or a busy flag in between).
   sacks:fn:craftCommit {UUID, receipt} -> Boolean: the craft happened - the receipt can never be refunded.
   sacks:fn:pocketFill UUID -> Long: the pocket refill of item 1 right now (for Requip's Equip; an addition to the contract).
4. /craft SMITHING TAB CLASS FILTER: when gear:fn:classShow (SkyyGear 0.2.23) exists, the Smithing tab hides recipes whose output it answers
   Boolean.FALSE for; anything else (missing key, null, an exception) = shown. The materials line says how many are hidden. Search, the
   other tabs and the craft click are unchanged.
No new command, ECS system, event, class, setting or saved file; pools, refill.properties and crafts.log keep their formats. Rollback
0.7.17 -> 0.7.16 is safe (Requip block slots stop refilling empty slots; the smithing hub's crafting greys out).
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.16.py")
dst = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.17.py")
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new, count=1):
    global s
    assert s.count(old) >= 1, "anchor missing: " + old[:90]
    assert count != 1 or s.count(old) == 1, "anchor not unique: " + old[:90]
    s = s.replace(old, new, count)


assert 'VERSION = "0.7.16"' in s and "BAG_HOLD = _bag_hold()" in s and "pocketFill" not in s, "the source must be the generated 0.7.16 script"
REG0 = s.count("registerCommand(")
SYS0 = s.count("registerSystem(")
GLB0 = s.count("registerGlobal(")
MAKE0 = s.count("pool.makeClass(")
ASSETS0 = s[s.index("# ================= assets ================="):]

# ================= docstring + version =================
rep('"""SkyySacks 0.7.16 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.16.py           -> SkyySacks/SkyySacks-0.7.16.jar   (deploys go through tools/deploy_set.py --yes)' + LF
    + '       python build_skyysacks_0.7.16.py --deploy  -> also copies to Mods/SkyySacks.jar and enables it in the HUD mod world (never used)' + LF,
    '"""SkyySacks 0.7.17 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.17.py           -> SkyySacks/SkyySacks-0.7.17.jar   (deploys go through tools/deploy_set.py --yes)' + LF
    + '       python build_skyysacks_0.7.17.py --deploy  -> also copies to Mods/SkyySacks.jar and enables it in the HUD mod world (never used)' + LF)
rep("are 0.7.15's." + LF + '"""' + LF,
    "are 0.7.15's." + LF
    + "0.7.17 (derived from 0.7.16 by tools/sacks_0_7_17_patch.py - edit the patch, not this file; research/Requip-Smithing-Spec.md round R2;" + LF
    + "Skyy \"then also let it pull from the pocket dimension for blocks in the hot bar. (so they auto refill.)\" + \"we should give this, and the" + LF
    + "crafting thing a filter by class\"): Requip's reserved hotbar block slots (requip:pocket:<uuid>) refill from the bags every 2 s, EMPTY" + LF
    + "slots too (SweepTask.pocketFill; sacks:fn:pocketFill on demand); sacks:fn:deposit (inventory -> bags, caps respected); the smithing" + LF
    + "hub's craft bridges sacks:fn:craftList / craftHave / craftPay / craftRefund / craftCommit (the /craft allow rule + payment in one" + LF
    + "place: inventory first, then bags, all or nothing, receipts refundable once within 60 s); the /craft Smithing tab hides gear SkyyGear's" + LF
    + "gear:fn:classShow says is not for your class. Assets, ids, recipes and saved data are 0.7.16's. Details: the patch docstring." + LF
    + '"""' + LF)
rep('VERSION = "0.7.16"', 'VERSION = "0.7.17"')

# ================= 1. SweepTask.pocketFill + its call in items() =================
POCKET = r"""# ================= 0.7.17 REQUIP POCKET BLOCK SLOTS (tools/sacks_0_7_17_patch.py docstring item 1) =================
# requip:pocket:<uuid> (SkyyWardrobe 0.2) = Map<Integer hotbar slot, String itemId>. Each reserved slot that is EMPTY or holds a smaller
# plain stack of that item is filled up to its target (review fix 3) from the pool of key k (a carried bag of its home type or the Omni). Never
# another item's slot, never a stack with metadata (an EMPTY document counts as none, the review fix 13 rule), never a slot not in the map,
# never a non-stacking item. Read back: exactly what the slot gained leaves the pool and is KEPT. Master switch bags.refill (SackCfg.REFILL_ON)
# only - the player's own refill mode does not apply (the Requip pick is the opt-in). Returns items moved.
# FIX 2 (0.7.17 review): "plain" = no metadata AND the durability / max durability / quality of a fresh new ItemStack(id, n) - a damaged tool
# or a quality stack is never copied, deposited or topped up (a refund or a fresh stack could otherwise repair it for free).
swp.addMethod(CtNewMethod.make(jt(r'''
public static boolean plainFresh(@IS@ it) {
  if (it == null || it.isEmpty() || it.getItemId() == null) return false;
  org.bson.BsonDocument md = it.getMetadata();
  if (md != null && !md.isEmpty()) return false;
  try {
    @IS@ f = new @IS@(it.getItemId(), 1);
    return Double.compare(it.getDurability(), f.getDurability()) == 0 && Double.compare(it.getMaxDurability(), f.getMaxDurability()) == 0
      && it.getQualityIndex() == f.getQualityIndex();
  } catch (Throwable t) { return false; }
}'''), swp))
# FIX 3 (0.7.17 review, spec "up to the target (default = the item's max stack, Server Setup pocket.target)"): the target of a reserved slot =
# requip:pocketN:<uuid> (Map<Integer slot, Number>, > 0; a contract ADDITION for per-pick amounts) else SkyyWardrobe's Server Setup
# pocket.target (config:fn:SkyyWardrobe "get", > 0) else the item's max stack; never above the max stack.
swp.addMethod(CtNewMethod.make(jt(r'''
public static int wardrobeTarget() {
  Object f = null;
  try { f = @PKG@.SackPool.bridge().get("config:fn:SkyyWardrobe"); } catch (Throwable t) { return 0; }
  if (!(f instanceof java.util.function.Function)) return 0;
  try {
    Object r = ((java.util.function.Function) f).apply(new Object[] { "get", "pocket.target" });
    if (!(r instanceof String)) return 0;
    long v = Long.parseLong(((String) r).trim());
    return (v > 0L && v < 100000L) ? (int) v : 0;
  } catch (Throwable t2) { return 0; }
}'''), swp))
swp.addMethod(CtNewMethod.make(jt(r'''
public static int pocketFill(@PLA@ p, String k, java.util.UUID u) {
  if (p == null || k == null || u == null || !@PKG@.SackCfg.REFILL_ON) return 0;
  Object mo = null;
  try { mo = @PKG@.SackPool.bridge().get("requip:pocket:" + u.toString()); } catch (Throwable t0) { mo = null; }
  if (!(mo instanceof java.util.Map)) return 0;
  java.util.ArrayList ents = new java.util.ArrayList();
  try { ents.addAll(((java.util.Map) mo).entrySet()); } catch (Throwable t1) { return 0; }
  if (ents.isEmpty()) return 0;
  @INV@ inv = p.getInventory();
  if (inv == null) return 0;
  @IC@ hb = inv.getHotbar();
  if (hb == null) return 0;
  java.util.HashMap caps = caps(inv);
  if (caps.isEmpty()) return 0;
  @PKG@.BagMirror.beforeTake(k);   // live-mirror rule: book what a crafting window took before the pool is read
  short cap = hb.getCapacity();
  int total = 0;
  int gT = wardrobeTarget();
  java.util.Map nm = null;
  try { Object no = @PKG@.SackPool.bridge().get("requip:pocketN:" + u.toString()); if (no instanceof java.util.Map) nm = (java.util.Map) no; } catch (Throwable t2) { nm = null; }
  for (int i = 0; i < ents.size(); i++) {
    java.util.Map.Entry e = (java.util.Map.Entry) ents.get(i);
    Object ko = e.getKey();
    Object vo = e.getValue();
    if (!(ko instanceof Number) || !(vo instanceof String)) continue;
    int si = ((Number) ko).intValue();
    if (si < 0 || si >= cap) continue;
    String id = (String) vo;
    if (id.startsWith("Skyy_Sack_")) continue;
    String cat = @PKG@.SackDefs.homeOf(id);
    if (cat == null || !caps.containsKey(cat)) continue;
    long have = @PKG@.SackPool.get(k, id);
    if (have <= 0L) continue;
    short s = (short) si;
    @IS@ it = hb.getItemStack(s);
    boolean empty = it == null || it.isEmpty();
    org.bson.BsonDocument md = null;
    int q = 0;
    if (!empty) {
      if (!id.equals(it.getItemId())) continue;
      md = it.getMetadata();
      if (md != null && !md.isEmpty()) continue;
      if (!plainFresh(it)) continue;
      q = it.getQuantity();
    }
    @ITM@ item = empty ? @PKG@.ProcBench.item(id) : it.getItem();
    int max = item == null ? 0 : item.getMaxStack();
    int t = gT;
    if (nm != null) {
      Object tv = null;
      try { tv = nm.get(ko); } catch (Throwable t5) { tv = null; }
      if (tv instanceof Number && ((Number) tv).intValue() > 0) t = ((Number) tv).intValue();
    }
    int top = (t > 0 && t < max) ? t : max;
    if (max <= 1 || q >= top) continue;
    int want = top - q;
    if ((long) want > have) want = (int) have;
    hb.addItemStackToSlot(s, md == null ? new @IS@(id, want) : new @IS@(id, want, md));
    @IS@ after = hb.getItemStack(s);
    int got = (after == null || after.isEmpty() || !id.equals(after.getItemId())) ? 0 : after.getQuantity() - q;
    if (got > want) {
      if (empty) hb.removeItemStackFromSlot(s); else hb.setItemStackForSlot(s, it);
      @PKG@.SackPool.warn("hotbar block refill: slot " + si + " (" + id + ") gained " + got + " of " + want + " asked - undone");
      continue;
    }
    if (got <= 0) continue;
    @PKG@.SackPool.add(k, id, -(long) got);
    @PKG@.BagMirror.afterTake(k, id);   // live-mirror rule: the mirror never offers more than the pool now holds
    @PKG@.SackPool.keep(k, id, (long) got);
    total += got;
  }
  return total;
}'''), swp))
"""
rep("# 0.7.12: the 0.7.11 benchFed pause is gone", POCKET + "# 0.7.12: the 0.7.11 benchFed pause is gone")
rep('''    catch (Throwable t2) { @PKG@.KnowSync.warnOnce("stack refill failed: " + t2); }
  }
  if (u != null) @PKG@.SackPool.SEENQ.put(u, carried(inv));''',
    '''    catch (Throwable t2) { @PKG@.KnowSync.warnOnce("stack refill failed: " + t2); }
  }
  // 0.7.17: Requip's reserved hotbar block slots (requip:pocket:<uuid>) - empty ones too; before the SEENQ snapshot (never "used")
  try { int pf = pocketFill(p, k, u); out[1] = out[1] + pf; }
  catch (Throwable t3) { @PKG@.KnowSync.warnOnce("hotbar block refill (Requip) failed: " + t3); }
  if (u != null) @PKG@.SackPool.SEENQ.put(u, carried(inv));''')

# ================= 4. CraftPage: the Smithing tab class filter =================
CLASSF = r'''# 0.7.17 (Skyy "we should give this, and the crafting thing a filter by class"): gear:fn:classShow (SkyyGear 0.2.23) =
# apply(Object[]{UUID, String itemId}) -> Boolean. 1 = show, 0 = hide (Boolean.FALSE only), -1 = no answer (missing key, other type, an
# exception - warned once a minute): shown. classHidden = how many the last recipesFor() hid (the materials line says so).
cpg.addField(CtField.make("public int classHidden;", cpg))
cpg.addField(CtField.make("public static long CLASSWARN;", cpg))
cpg.addMethod(CtNewMethod.make(jt(r"""
public static int classShow(java.util.UUID u, String itemId) {
  if (u == null || itemId == null) return -1;
  Object f = null;
  try { f = @PKG@.SackPool.bridge().get("gear:fn:classShow"); } catch (Throwable t) { return -1; }
  if (!(f instanceof java.util.function.Function)) return -1;
  Object r = null;
  try { r = ((java.util.function.Function) f).apply(new Object[] { u, itemId }); }
  catch (Throwable t) {
    long now = System.currentTimeMillis();
    if (now - CLASSWARN > 60000L) { CLASSWARN = now; @PKG@.SackPool.warn("craft: gear:fn:classShow failed for " + itemId + " (shown): " + t); }
    return -1;
  }
  if (r instanceof Boolean) return ((Boolean) r).booleanValue() ? 1 : 0;
  return -1;
}"""), cpg))
cpg.addMethod(CtNewMethod.make(jt(r"""
public static String smithNoteText(int hidden) {
  return "Smithing shows gear for your class - " + hidden + " hidden (Show all is in /smithing). Materials: your inventory, then your magic bags.";
}"""), cpg))
cpg.addMethod(CtNewMethod.make(jt(r"""
public void smithNote(@UCB@ b, boolean searching) {
  if (b == null || searching || this.classHidden <= 0 || !"A:smith".equals(this.tab)) return;
  b.set("#SkyyCMatNote.Text", smithNoteText(this.classHidden));
}"""), cpg))
'''
rep('''cpg.addMethod(CtNewMethod.make(f"""
public java.util.ArrayList recipesFor(String tabId, java.util.UUID u) {{
  java.util.ArrayList out = new java.util.ArrayList();
''', CLASSF + '''cpg.addMethod(CtNewMethod.make(f"""
public java.util.ArrayList recipesFor(String tabId, java.util.UUID u) {{
  java.util.ArrayList out = new java.util.ArrayList();
  this.classHidden = 0;
''')
rep('''    if (grp >= 0 && !{PKG}.KnowSync.allowed(rc, u, this.known, this.coll)) continue;
    out.add(rc);''',
    '''    if (grp >= 0 && !{PKG}.KnowSync.allowed(rc, u, this.known, this.coll)) continue;
    // 0.7.17: the Smithing tab hides what gear:fn:classShow says is not for your class (no SkyyGear 0.2.23 = everything shown)
    if (grp == 1) {{
      {MQ} cpo = rc.getPrimaryOutput();
      if (cpo != null && classShow(u, cpo.getItemId()) == 0) {{ this.classHidden = this.classHidden + 1; continue; }}
    }}
    out.add(rc);''')
rep('''b.appendInline("#SkyyCraft", "Label {{ Anchor: (Height: 22); Text: \\\\"Materials are counted from your inventory and your magic bags.\\\\";''',
    '''b.appendInline("#SkyyCraft", "Label #SkyyCMatNote {{ Anchor: (Height: 22); Text: \\\\"Materials are counted from your inventory and your magic bags.\\\\";''')
rep('''  java.util.ArrayList raw = this.tab == null ? new java.util.ArrayList() : (searching ? searchRecipes(u, this.query) : recipesFor(this.tab, u));
''', '''  java.util.ArrayList raw = this.tab == null ? new java.util.ArrayList() : (searching ? searchRecipes(u, this.query) : recipesFor(this.tab, u));
  smithNote(b, searching);   // 0.7.17: "N hidden" on the Smithing tab when gear:fn:classShow hid some
''')

# ================= 2 + 3. SackBridge: deposit, pocketNow, the craft bridges; SackFn modes 5-11 =================
BRIDGE = r'''# ================= 0.7.17 (tools/sacks_0_7_17_patch.py docstring items 2 + 3): deposit, pocket refill now, the smithing craft bridges =================
for _c, _m in ((IC, "removeItemStackFromSlot"), (IC, "setItemStackForSlot"), (IC, "addItemStackToSlot"), (CIC, "removeMaterials"),
               (CIC, "canRemoveMaterials"), (CRM, "getInputMaterials"), (INV, "getCombinedBackpackStorageHotbar"), (SIC, "addOrDropItemStack")):
    B.probe(pool, _c, _m)
# RECEIPTS = receipt id -> Object[]{UUID, String key, LinkedHashMap inventory part, LinkedHashMap bag part, long[]{time, state}, String recipe}
# (state 0 open, 1 refunded, 2 committed; memory only - a restart forgets them = the craft stands, like 0.7.13's OWED ledger)
sbr.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap RECEIPTS = new java.util.concurrent.ConcurrentHashMap();", sbr))
sbr.addField(CtField.make("public static final long RECEIPT_MS = 60000L;", sbr))
sbr.addField(CtField.make("public static long RSEQ = 0L;", sbr))
# sacks:fn:deposit (review fix 1): up to n of the plain stack IN THAT HOTBAR SLOT (4th argument, required) into the bags, never past the
# bag room; whatever does not fit stays in the slot. The 3-argument form is REFUSED (0, warned): taking "any stack of that id" from the
# inventory let a caller that had already lifted the slot's stack (SkyyWardrobe 0.2 giveBack) lose blocks. Only what really left the slot is
# credited (read back). New items enter by catOf (cooked food stays out unless bags.cookedFood). Returns the amount accepted.
sbr.addMethod(CtNewMethod.make(jt(r"""
public static long deposit(java.util.UUID u, String id, long n, int slot) {
  if (u == null || id == null || n <= 0L || id.startsWith("Skyy_Sack_")) return 0L;
  if (slot < 0) {
    @PKG@.KnowSync.warnOnce("sacks:fn:deposit called without its hotbar slot (4th argument, Integer) - nothing moved; the 3-argument form is refused (it could take other stacks than the caller's)");
    return 0L;
  }
  String cat = @PKG@.SackDefs.catOf(id);
  if (cat == null) return 0L;
  String k = @PKG@.SackPool.settledKey(u);
  if (k == null) return 0L;
  @PLA@ p = playerOf(u);
  if (p == null) return 0L;
  @INV@ inv = p.getInventory();
  if (inv == null) return 0L;
  @IC@ hb = inv.getHotbar();
  if (hb == null || slot >= (int) hb.getCapacity()) return 0L;
  Integer cc = (Integer) @PKG@.SweepTask.caps(inv).get(cat);
  if (cc == null) return 0L;
  short s = (short) slot;
  @IS@ it = hb.getItemStack(s);
  if (it == null || it.isEmpty() || !id.equals(it.getItemId()) || !@PKG@.SweepTask.plainFresh(it)) return 0L;
  @PKG@.BagMirror.beforeTake(k);
  long room = (long) cc.intValue() - @PKG@.SackPool.get(k, id);
  if (room <= 0L) return 0L;
  long want = n < room ? n : room;
  int qty = it.getQuantity();
  int take = (long) qty < want ? qty : (int) want;
  if (take <= 0) return 0L;
  @ISS@ tx = hb.removeItemStackFromSlot(s, take);
  if (tx == null || !tx.succeeded()) return 0L;
  @IS@ rem = tx.getRemainder();
  int removed = take - (rem == null ? 0 : rem.getQuantity());
  if (removed <= 0) return 0L;
  @PKG@.SackPool.add(k, id, (long) removed);
  try { @PKG@.CraftLog.later(k, "BAG-DEPOSIT " + id + " " + removed + " (sacks:fn:deposit hotbar slot " + slot + ")"); } catch (Throwable t3) { }
  try { @PKG@.SackPool.saveSoon(k); } catch (Throwable t4) { @PKG@.SackPool.DIRTY.put(k, Boolean.TRUE); }
  return (long) removed;
}""".replace("@ISS@", ISS)), sbr))
# sacks:fn:pocketFill: the 2 s pocket refill of this player right now (Requip's Equip); same gates as the tick (settled key, world thread)
sbr.addMethod(CtNewMethod.make(jt(r"""
public static long pocketNow(java.util.UUID u) {
  if (u == null) return 0L;
  String k = @PKG@.SackPool.settledKey(u);
  if (k == null) return 0L;
  @PLA@ p = playerOf(u);
  if (p == null) return 0L;
  int n = @PKG@.SweepTask.pocketFill(p, k, u);
  if (n > 0) { try { @PKG@.SackPool.saveSoon(k); } catch (Throwable t4) { @PKG@.SackPool.DIRTY.put(k, Boolean.TRUE); } }
  return (long) n;
}"""), sbr))
# the /craft allow rule for one recipe (null = allowed): not table-only / timed; a Collections-tab recipe (coll:recipes); else in the merged
# Crafting / Smithing / Farming set (Fieldcraft + benches up to the accessory tier) and KnowSync.allowed (bag + vanilla knowledge rules)
sbr.addMethod(CtNewMethod.make(jt(r"""
public static String craftWhy(java.util.UUID u, @PLA@ p, @CRR@ r) {
  if (r == null) return "unknown recipe";
  if (@PKG@.CraftPage.tableOnly(r)) return "only at its table (timed)";
  String rid = String.valueOf(r.getId());
  java.util.HashSet coll = @PKG@.CraftPage.collectionRecipes(u);
  if (coll.contains(rid)) return null;
  if (!@PKG@.CraftPage.craftSet(u).contains(rid)) return "needs its bench accessory in your accessory bag";
  if (!@PKG@.KnowSync.allowed(r, u, @PKG@.KnowSync.known(p), coll)) return "you have not unlocked this recipe";
  return null;
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static boolean smithOut(@CRR@ r) {
  @MQ@ po = r == null ? null : r.getPrimaryOutput();
  String id = po == null ? null : po.getItemId();
  return id != null && (id.startsWith("Tool_") || id.startsWith("Weapon_") || id.startsWith("Armor_"));
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static boolean inGroup(@CRR@ r, int g) {
  if (g == 3) return smithOut(r);
  if (g < 0) return true;
  return @PKG@.CraftPage.tabGroup(r) == g;
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static String[] craftList(java.util.UUID u, String group) {
  if (u == null) return null;
  @PLA@ p = playerOf(u);
  if (p == null) return null;
  int g = -1;
  if ("smith".equals(group)) g = 3;
  else if ("craft".equals(group)) g = 0;
  else if ("farm".equals(group)) g = 2;
  else if (group != null && !"all".equals(group)) return new String[0];
  java.util.HashSet coll = @PKG@.CraftPage.collectionRecipes(u);
  java.util.Set known = @PKG@.KnowSync.known(p);
  java.util.TreeSet ids = new java.util.TreeSet();
  java.util.Iterator it = @PKG@.CraftPage.craftSet(u).iterator();
  while (it.hasNext()) {
    String rid = (String) it.next();
    Object o = @CRR@.getAssetMap().getAsset(rid);
    if (!(o instanceof @CRR@)) continue;
    @CRR@ r = (@CRR@) o;
    if (@PKG@.CraftPage.tableOnly(r) || !inGroup(r, g)) continue;
    if (!@PKG@.KnowSync.allowed(r, u, known, coll)) continue;
    ids.add(rid);
  }
  it = coll.iterator();
  while (it.hasNext()) {
    String rid = (String) it.next();
    Object o = @CRR@.getAssetMap().getAsset(rid);
    if (!(o instanceof @CRR@)) continue;
    @CRR@ r = (@CRR@) o;
    if (@PKG@.CraftPage.tableOnly(r) || !inGroup(r, g)) continue;
    ids.add(rid);
  }
  return (String[]) ids.toArray(new String[0]);
}"""), sbr))
# the containers materialsFor pays from (getCombinedBackpackStorageHotbar)
sbr.addMethod(CtNewMethod.make(jt(r"""
public static @IC@[] payConts(@INV@ inv) {
  return new @IC@[] { inv.getBackpack(), inv.getStorage(), inv.getHotbar() };
}"""), sbr))
# ENGINE FACT (found by the harness): removeMaterials takes a stack WITH metadata for a RESOURCE-TYPE input (an item-id input never does),
# and a DelegateItemContainer that hides or locks those slots makes canRemoveMaterials refuse the whole payment. So the bridges count and pay
# from a PLAIN COPY: plainCopy = a SimpleItemContainer holding a copy of every plain stack (SweepTask.plainFresh: no metadata - an EMPTY
# document counts as none - and the durability / quality of a fresh stack, review fix 2)
# of backpack, storage, hotbar in that order (the /craft order), plus where each came from; the engine pays from the copy + the bag mirror;
# applyCopy then removes exactly what the copy lost from the real slots (read back) - the bag mirror's pattern.
# answer: Object[]{SimpleItemContainer copy, int[] container index (-1 = not copied), short[] real slot, int[] quantity copied}
sbr.addMethod(CtNewMethod.make(jt(r"""
public static Object[] plainCopy(@IC@[] cs) {
  int n = 0;
  for (int c = 0; c < cs.length; c++) if (cs[c] != null) n += cs[c].getCapacity();
  if (n < 1) n = 1;
  @SIC@ copy = new @SIC@((short) n);
  int[] ci = new int[n];
  short[] si = new short[n];
  int[] q0 = new int[n];
  for (int i = 0; i < n; i++) ci[i] = -1;
  int at = 0;
  for (int c = 0; c < cs.length; c++) {
    if (cs[c] == null) continue;
    short cap = cs[c].getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = cs[c].getItemStack(s);
      int here = at;
      at++;
      if (it == null || it.isEmpty() || it.getItemId() == null) continue;
      if (!@PKG@.SweepTask.plainFresh(it)) continue;   // review fix 2: no metadata, no damaged / quality stack (a refund is a fresh stack)
      copy.setItemStackForSlot((short) here, new @IS@(it.getItemId(), it.getQuantity()));
      ci[here] = c;
      si[here] = s;
      q0[here] = it.getQuantity();
    }
  }
  return new Object[] { copy, ci, si, q0 };
}"""), sbr))
# what the copy lost -> removed from the real slot it came from (each read back); null = done, else the reason (craftPay rolls back)
sbr.addMethod(CtNewMethod.make(jt(r"""
public static String applyCopy(Object[] pcp, @IC@[] cs) {
  @SIC@ copy = (@SIC@) pcp[0];
  int[] ci = (int[]) pcp[1];
  short[] si = (short[]) pcp[2];
  int[] q0 = (int[]) pcp[3];
  for (int i = 0; i < ci.length; i++) {
    if (ci[i] < 0) continue;
    @IS@ now = copy.getItemStack((short) i);
    int q1 = (now == null || now.isEmpty()) ? 0 : now.getQuantity();
    int d = q0[i] - q1;
    if (d == 0) continue;
    if (d < 0) return "the payment grew a stack - nothing was taken";
    @IC@ c = cs[ci[i]];
    @IS@ real = c.getItemStack(si[i]);
    if (real == null || real.isEmpty() || real.getQuantity() < d) return "your inventory changed during the payment - nothing was taken";
    @ISS@ tx = c.removeItemStackFromSlot(si[i], d);
    if (tx == null || !tx.succeeded()) return "a material could not be taken - nothing was taken";
    @IS@ rem = tx.getRemainder();
    int got = d - (rem == null ? 0 : rem.getQuantity());
    if (got != d) return "a material could not be taken - nothing was taken";
  }
  return null;
}""".replace("@ISS@", ISS)), sbr))
# the view craftHave / craftPay count and pay from: the plain copy first, then the bag mirror (k == null: while the profile settles - the
# copy only, no mirror built). materialsFor first: it books what a bench took (live-mirror rule) and rebuilds the mirror for this recipe.
sbr.addMethod(CtNewMethod.make(jt(r"""
public static @CIC@ payView(@PLA@ p, String k, @CRR@ r, @SIC@ copy) {
  if (k == null) return new @CIC@(new @IC@[] { copy });
  @PKG@.CraftPage.materialsFor(p, k, @PKG@.CraftPage.wantedOne(r));
  return new @CIC@(new @IC@[] { copy, @PKG@.BagMirror.of(k).cont });
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static Object[] craftHave(java.util.UUID u, String rid) {
  if (u == null || rid == null) return null;
  @PLA@ p = playerOf(u);
  if (p == null || p.getInventory() == null) return null;
  Object o = @CRR@.getAssetMap().getAsset(rid);
  if (!(o instanceof @CRR@)) return null;
  @CRR@ r = (@CRR@) o;
  String k = @PKG@.SackPool.settledKey(u);
  @CIC@ mats = payView(p, k, r, (@SIC@) plainCopy(payConts(p.getInventory()))[0]);
  @MQ@[] in = r.getInput();
  int n = in == null ? 0 : in.length;
  String[] ids = new String[n];
  Long[] have = new Long[n];
  Long[] need = new Long[n];
  for (int i = 0; i < n; i++) {
    if (in[i] == null) { ids[i] = "?"; have[i] = Long.valueOf(0L); need[i] = Long.valueOf(0L); continue; }
    ids[i] = in[i].getItemId() != null ? in[i].getItemId() : ("res:" + in[i].getResourceTypeId());
    have[i] = Long.valueOf((long) mats.countRemovableMaterial(in[i]));
    need[i] = Long.valueOf((long) in[i].getQuantity());
  }
  return new Object[] { Long.valueOf((long) @PKG@.CraftPage.limit(r, mats)), ids, have, need };
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static Object[] payFail(String why) {
  return new Object[] { Long.valueOf(0L), null, why };
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static synchronized String nextReceipt() {
  RSEQ = RSEQ + 1L;
  return "r" + Long.toHexString(System.currentTimeMillis()) + "-" + RSEQ;
}"""), sbr))
# (the rollback snapshot of each slot's stack before a payment)
sbr.addMethod(CtNewMethod.make(jt(r"""
public static java.util.ArrayList slotSnap(@IC@[] cs) {
  java.util.ArrayList out = new java.util.ArrayList();
  for (int c = 0; c < cs.length; c++) {
    if (cs[c] == null) { out.add(null); continue; }
    short cap = cs[c].getCapacity();
    @IS@[] a = new @IS@[cap];
    for (short s = 0; s < cap; s++) a[s] = cs[c].getItemStack(s);
    out.add(a);
  }
  return out;
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static boolean sameStack(@IS@ a, @IS@ b) {
  boolean ea = a == null || a.isEmpty();
  boolean eb = b == null || b.isEmpty();
  if (ea || eb) return ea && eb;
  return a == b || (a.getQuantity() == b.getQuantity() && String.valueOf(a.getItemId()).equals(b.getItemId()));
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static void slotRestore(@IC@[] cs, java.util.ArrayList snap) {
  for (int c = 0; c < cs.length; c++) {
    @IS@[] a = (@IS@[]) snap.get(c);
    if (a == null || cs[c] == null) continue;
    for (short s = 0; s < a.length; s++) {
      @IS@ was = a[s];
      @IS@ now = cs[c].getItemStack(s);
      if (was == now) continue;
      if (was == null || was.isEmpty()) { if (now != null && !now.isEmpty()) cs[c].removeItemStackFromSlot(s); }
      else cs[c].setItemStackForSlot(s, was);
    }
  }
}"""), sbr))
# true when a stack WITH metadata (rolled gear, a named item, a filled container) changed since the snapshot
sbr.addMethod(CtNewMethod.make(jt(r"""
public static boolean metaTouched(@IC@[] cs, java.util.ArrayList snap) {
  for (int c = 0; c < cs.length; c++) {
    @IS@[] a = (@IS@[]) snap.get(c);
    if (a == null || cs[c] == null) continue;
    for (short s = 0; s < a.length; s++) {
      @IS@ was = a[s];
      if (was == null || was.isEmpty()) continue;
      org.bson.BsonDocument md = was.getMetadata();
      if (md == null || md.isEmpty()) continue;
      if (!sameStack(was, cs[c].getItemStack(s))) return true;
    }
  }
  return false;
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static void addCount(java.util.LinkedHashMap m, String id, int n) {
  if (id == null || n == 0) return;
  Integer v = (Integer) m.get(id);
  int nv = (v == null ? 0 : v.intValue()) + n;
  if (nv <= 0) m.remove(id); else m.put(id, Integer.valueOf(nv));
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static void creditBags(String k, java.util.LinkedHashMap bag) {
  java.util.Iterator it = bag.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    int v = ((Integer) e.getValue()).intValue();
    if (v > 0) @PKG@.SackPool.add(k, (String) e.getKey(), (long) v);
  }
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static void purgeReceipts(long now) {
  java.util.Iterator it = RECEIPTS.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    long[] t = (long[]) ((Object[]) e.getValue())[4];
    if (now - t[0] > 600000L) it.remove();
  }
}"""), sbr))
# surplus after a payment (whole resource-type items worth more than needed): back where it came from - the bags first, then the inventory;
# invT / bagT shrink by what went back. null = done; else the reason (craftPay then rolls everything back)
sbr.addMethod(CtNewMethod.make(jt(r"""
public static String giveSurplus(String k, @IC@ invC, java.util.LinkedHashMap left, java.util.LinkedHashMap invT, java.util.LinkedHashMap bagT) {
  java.util.ArrayList ids = new java.util.ArrayList(left.keySet());
  for (int i = 0; i < ids.size(); i++) {
    String id = (String) ids.get(i);
    int cnt = ((Integer) left.get(id)).intValue();
    if (cnt <= 0) continue;
    Integer bv = (Integer) bagT.get(id);
    int back = bv == null ? 0 : (bv.intValue() < cnt ? bv.intValue() : cnt);
    if (back > 0) { @PKG@.SackPool.add(k, id, (long) back); addCount(bagT, id, -back); cnt -= back; }
    if (cnt > 0) {
      int b0 = @PKG@.CraftPage.countItem(invC, id);
      invC.addItemStack(new @IS@(id, cnt));
      int got = @PKG@.CraftPage.countItem(invC, id) - b0;
      if (got != cnt) return "the extra materials did not fit back - nothing was taken";
      addCount(invT, id, -cnt);
    }
  }
  return null;
}"""), sbr))
# a refused payment: every inventory slot back to its snapshot, the bag part credited back to the pool it left, one crafts.log line
sbr.addMethod(CtNewMethod.make(jt(r"""
public static Object[] refuse(String k, String rid, int times, String bad, @IC@[] cs, java.util.ArrayList snap, java.util.LinkedHashMap bagT) {
  slotRestore(cs, snap);
  creditBags(k, bagT);
  try { @PKG@.CraftLog.later(k, "CRAFT-PAY-REFUSED " + rid + " x" + times + " (" + bad + ") inventory restored, bags " + bagT + " back (sacks:fn:craftPay)"); } catch (Throwable t3) { }
  try { @PKG@.SackPool.saveSoon(k); } catch (Throwable t4) { @PKG@.SackPool.DIRTY.put(k, Boolean.TRUE); }
  return payFail(bad);
}"""), sbr))
# sacks:fn:craftPay - the /craft payment (CraftPage.handleDataEvent), all or nothing, with a receipt
sbr.addMethod(CtNewMethod.make(jt(r"""
public static Object[] craftPay(java.util.UUID u, String rid, int times) {
  if (u == null || rid == null || times <= 0 || times > 1000) return payFail("bad arguments");
  @PLA@ p = playerOf(u);
  if (p == null || p.getInventory() == null) return payFail("paused");
  String k = @PKG@.SackPool.settledKey(u);
  if (k == null) return payFail("paused");
  Object o = @CRR@.getAssetMap().getAsset(rid);
  if (!(o instanceof @CRR@)) return payFail("unknown recipe");
  @CRR@ r = (@CRR@) o;
  String why = craftWhy(u, p, r);
  if (why != null) return payFail(why);
  @INV@ inv = p.getInventory();
  @IC@[] cs = payConts(inv);
  java.util.ArrayList snap = slotSnap(cs);
  Object[] pcp = plainCopy(cs);
  @SIC@ copy = (@SIC@) pcp[0];
  @CIC@ mats = payView(p, k, r, copy);
  if (@PKG@.CraftPage.limit(r, mats) < times) return payFail("not enough materials");
  java.util.List inputs = @CRM@.getInputMaterials(r, times);
  int n = inputs == null ? 0 : inputs.size();
  if (n == 0) return payFail("this recipe has no inputs");
  if (!mats.canRemoveMaterials(inputs)) return payFail("not enough materials");
  int[] per = new int[n];
  for (int i = 0; i < n; i++) {
    per[i] = ((@MQ@) inputs.get(i)).getQuantity() / times;
    if (per[i] <= 0) per[i] = 1;
  }
  @PKG@.BagMirror m = @PKG@.BagMirror.of(k);
  @IC@ invC = inv.getCombinedBackpackStorageHotbar();
  java.util.HashMap invB = @PKG@.CraftPage.snapshot(copy);
  java.util.HashMap bagB = @PKG@.CraftPage.snapshot(m.cont);
  // review fix 4: anything thrown after the debit still rolls back (slots from the snapshot, the bag part credited back)
  java.util.LinkedHashMap invT = new java.util.LinkedHashMap();
  java.util.LinkedHashMap bagT = new java.util.LinkedHashMap();
  String bad = null;
  boolean synced = false;
  try {
    try { mats.removeMaterials(inputs); } catch (Throwable t0) { @PKG@.SackPool.warn("craft bridge: removeMaterials threw (checked below): " + t0); }
    invT = @PKG@.CraftPage.removedItems(invB, @PKG@.CraftPage.snapshot(copy));
    bagT = @PKG@.CraftPage.removedItems(bagB, @PKG@.CraftPage.snapshot(m.cont));
    m.sync();   // the /craft rule: what left the mirror leaves the pool now
    synced = true;
    String moved = applyCopy(pcp, cs);   // the copy's losses -> the real inventory slots (read back)
    java.util.LinkedHashMap took = new java.util.LinkedHashMap(invT);
    java.util.Iterator bi = bagT.entrySet().iterator();
    while (bi.hasNext()) { java.util.Map.Entry be = (java.util.Map.Entry) bi.next(); addCount(took, (String) be.getKey(), ((Integer) be.getValue()).intValue()); }
    java.util.LinkedHashMap left = @PKG@.CraftPage.reserve(took, inputs, per, times);
    bad = moved;
    if (bad != null) { }
    else if (metaTouched(cs, snap)) bad = "a stack with extra data (rolled gear or a named item) would be used - nothing was taken";
    else if (left == null) bad = "could not take the materials - nothing was taken";
    else bad = giveSurplus(k, invC, left, invT, bagT);
  } catch (Throwable tx) {
    @PKG@.SackPool.warn("craft bridge: the payment of " + rid + " failed and is rolled back: " + tx);
    if (!synced) {
      try { bagT = @PKG@.CraftPage.removedItems(bagB, @PKG@.CraftPage.snapshot(m.cont)); } catch (Throwable ty) { bagT = new java.util.LinkedHashMap(); }
      try { m.sync(); } catch (Throwable tz) { }
    }
    bad = "internal error - nothing was taken";
  }
  if (bad != null) return refuse(k, rid, times, bad, cs, snap, bagT);
  long now = System.currentTimeMillis();
  purgeReceipts(now);
  String rc = nextReceipt();
  RECEIPTS.put(rc, new Object[] { u, k, invT, bagT, new long[] { now, 0L }, rid });
  try { @PKG@.CraftLog.later(k, "CRAFT-PAY " + rid + " x" + times + " inventory " + invT + " bags " + bagT + " receipt " + rc + " (sacks:fn:craftPay)"); } catch (Throwable t3) { }
  if (!bagT.isEmpty()) { try { @PKG@.SackPool.saveSoon(k); } catch (Throwable t4) { @PKG@.SackPool.DIRTY.put(k, Boolean.TRUE); } }
  return new Object[] { Long.valueOf((long) times), rc, null };
}"""), sbr))
# one state change per receipt (st 1 = refund: open, same player, within RECEIPT_MS; st 2 = commit: open, same player) - atomic
sbr.addMethod(CtNewMethod.make(jt(r"""
public static synchronized Object[] claim(java.util.UUID u, String rc, long st, long now) {
  Object[] e = (Object[]) RECEIPTS.get(rc);
  if (e == null || !u.equals(e[0])) return null;
  long[] t = (long[]) e[4];
  if (t[1] != 0L) return null;
  if (st == 1L && now - t[0] > RECEIPT_MS) return null;
  t[1] = st;
  RECEIPTS.remove(rc);
  return e;
}"""), sbr))
# an item the inventory could not take back: into the bags when it has a bag home, else dropped at the player (never lost silently)
sbr.addMethod(CtNewMethod.make(jt(r"""
public static void spill(java.util.UUID u, String k, @PLA@ p, String id, int n) {
  if (n <= 0) return;
  if (@PKG@.SackDefs.homeOf(id) != null) {
    @PKG@.SackPool.add(k, id, (long) n);
    try { @PKG@.CraftLog.later(k, "CRAFT-REFUND-SPILL " + id + " " + n + " into the bags (inventory full)"); } catch (Throwable t3) { }
    return;
  }
  try {
    @PR@ pr = @UNI@.get().getPlayer(u);
    @REF@ r = pr.getReference();
    @SIC@.addOrDropItemStack(r.getStore(), r, p.getInventory().getCombinedStorageHotbarBackpack(), new @IS@(id, n));
    try { @PKG@.CraftLog.later(k, "CRAFT-REFUND-SPILL " + id + " " + n + " dropped at the player (inventory full)"); } catch (Throwable t3) { }
  } catch (Throwable t) {
    @PKG@.SackPool.warn("craft refund: " + n + " x " + id + " did not fit and could not be dropped for " + u + " - LOST, give them back by hand: " + t);
  }
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static long craftRefund(java.util.UUID u, String rc) {
  if (u == null || rc == null || @PKG@.SackPool.CLOSED) return 0L;
  Object[] e0 = (Object[]) RECEIPTS.get(rc);
  if (e0 == null || !u.equals(e0[0])) return 0L;
  String k = (String) e0[1];
  @PLA@ p = playerOf(u);
  if (p == null || p.getInventory() == null) return 0L;
  String cur = @PKG@.SackPool.settledKey(u);
  if (cur == null || !cur.equals(k)) {
    @PKG@.SackPool.warn("craft refund " + rc + " refused: the player's profile is not the one that paid (" + k + ") - the materials stay paid (crafts.log CRAFT-PAY lists them)");
    return 0L;
  }
  Object[] e = claim(u, rc, 1L, System.currentTimeMillis());
  if (e == null) return 0L;
  java.util.LinkedHashMap invT = (java.util.LinkedHashMap) e[2];
  java.util.LinkedHashMap bagT = (java.util.LinkedHashMap) e[3];
  long total = 0L;
  java.util.Iterator bi = bagT.entrySet().iterator();
  while (bi.hasNext()) {
    java.util.Map.Entry be = (java.util.Map.Entry) bi.next();
    int v = ((Integer) be.getValue()).intValue();
    if (v <= 0) continue;
    @PKG@.SackPool.add(k, (String) be.getKey(), (long) v);
    total += (long) v;
  }
  @IC@ c = p.getInventory().getCombinedStorageHotbarBackpack();
  java.util.Iterator ii = invT.entrySet().iterator();
  while (ii.hasNext()) {
    java.util.Map.Entry ie = (java.util.Map.Entry) ii.next();
    String id = (String) ie.getKey();
    int v = ((Integer) ie.getValue()).intValue();
    if (v <= 0) continue;
    int b0 = @PKG@.CraftPage.countItem(c, id);
    c.addItemStack(new @IS@(id, v));
    int got = @PKG@.CraftPage.countItem(c, id) - b0;
    if (got < 0) got = 0;
    if (got > v) got = v;
    if (got < v) spill(u, k, p, id, v - got);
    total += (long) v;
  }
  try { @PKG@.CraftLog.later(k, "CRAFT-REFUND receipt " + rc + " (" + e[5] + ") inventory " + invT + " bags " + bagT + " (sacks:fn:craftRefund)"); } catch (Throwable t3) { }
  try { @PKG@.SackPool.saveSoon(k); } catch (Throwable t4) { @PKG@.SackPool.DIRTY.put(k, Boolean.TRUE); }
  return total;
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static boolean craftCommit(java.util.UUID u, String rc) {
  if (u == null || rc == null) return false;
  Object[] e = claim(u, rc, 2L, System.currentTimeMillis());
  if (e == null) return false;
  try { @PKG@.CraftLog.later((String) e[1], "CRAFT-COMMIT receipt " + rc + " (" + e[5] + ") (sacks:fn:craftCommit)"); } catch (Throwable t3) { }
  return true;
}"""), sbr))
# SackFn modes 5-11 (the answer when the arguments are wrong or the call fails: 5 / 6 / 10 -> 0, 7 / 8 -> null, 9 -> {0, null, reason},
# 11 -> FALSE). Nothing here ever throws to the caller.
sbr.addMethod(CtNewMethod.make(jt(r"""
public static Object dflt(int mode) {
  if (mode == 7 || mode == 8) return null;
  if (mode == 9) return payFail("bad arguments");
  if (mode == 11) return Boolean.FALSE;
  return Long.valueOf(0L);
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static Object call2(int mode, Object o) {
  try {
    if (mode == 6) return (o instanceof java.util.UUID) ? Long.valueOf(pocketNow((java.util.UUID) o)) : Long.valueOf(0L);
    if (!(o instanceof Object[])) return dflt(mode);
    Object[] a = (Object[]) o;
    if (a.length < 2 || !(a[0] instanceof java.util.UUID)) return dflt(mode);
    java.util.UUID u = (java.util.UUID) a[0];
    if (mode == 7) return craftList(u, (a[1] instanceof String) ? (String) a[1] : (String) null);
    if (!(a[1] instanceof String)) return dflt(mode);
    String s1 = (String) a[1];
    if (mode == 8) return craftHave(u, s1);
    if (mode == 10) return Long.valueOf(craftRefund(u, s1));
    if (mode == 11) return craftCommit(u, s1) ? Boolean.TRUE : Boolean.FALSE;
    if (a.length < 3 || !(a[2] instanceof Number)) return dflt(mode);
    long n = ((Number) a[2]).longValue();
    if (mode == 5) {
      int slot = (a.length > 3 && a[3] instanceof Number) ? ((Number) a[3]).intValue() : -1;
      if (a.length > 3 && a[3] != null && !(a[3] instanceof Number)) return dflt(mode);
      return Long.valueOf(deposit(u, s1, n, slot < 0 ? -1 : slot));
    }
    if (mode == 9) return craftPay(u, s1, n > 1000L ? 1001 : (int) n);
  } catch (Throwable t) {
    @PKG@.KnowSync.warnOnce("bag bridge call failed (mode " + mode + "): " + t);
  }
  return dflt(mode);
}"""), sbr))
'''
rep('sfn.addInterface(pool.get("java.util.function.Function"))', BRIDGE + 'sfn.addInterface(pool.get("java.util.function.Function"))')
rep('''public Object apply(Object o) {
  try {
    if (this.mode == 3) return''', '''public Object apply(Object o) {
  try {
    if (this.mode >= 5) return @PKG@.SackBridge.call2(this.mode, o);   // 0.7.17: deposit, pocketFill, the craft bridges
    if (this.mode == 3) return''')
rep("# mode 0 count, 1 take, 2 put, 3 all, 4 commit (review fix).",
    "# mode 0 count, 1 take, 2 put, 3 all, 4 commit (review fix); 0.7.17: 5 deposit, 6 pocketFill, 7 craftList, 8 craftHave, 9 craftPay,"
    + LF + "# 10 craftRefund, 11 craftCommit (SackBridge.call2).")

# ================= plugin: publish the new keys + the ready line =================
rep('''  sbr0.put("sacks:fn:commit", new {PKG}.SackFn(4));   // review fix: a paid take leaves the refund ledger
''', '''  sbr0.put("sacks:fn:commit", new {PKG}.SackFn(4));   // review fix: a paid take leaves the refund ledger
  // 0.7.17 (research/Requip-Smithing-Spec.md section 5): Requip + the /smithing hub
  sbr0.put("sacks:fn:deposit", new {PKG}.SackFn(5));
  sbr0.put("sacks:fn:pocketFill", new {PKG}.SackFn(6));
  sbr0.put("sacks:fn:craftList", new {PKG}.SackFn(7));
  sbr0.put("sacks:fn:craftHave", new {PKG}.SackFn(8));
  sbr0.put("sacks:fn:craftPay", new {PKG}.SackFn(9));
  sbr0.put("sacks:fn:craftRefund", new {PKG}.SackFn(10));
  sbr0.put("sacks:fn:craftCommit", new {PKG}.SackFn(11));
''')
rep("the Bazaar sells from the bags you carry (sacks:fn:take) (bag items",
    "the Bazaar sells from the bags you carry (sacks:fn:take); Requip hotbar block slots refill from the bags, empty ones too (requip:pocket, "
    "sacks:fn:pocketFill, sacks:fn:deposit); the smithing hub crafts with /craft's rule and payment (sacks:fn:craftList / craftHave / craftPay / "
    "craftRefund / craftCommit); the /craft Smithing tab shows gear for your class when SkyyGear publishes gear:fn:classShow (bag items")

# ================= self-checks =================
assert 'VERSION = "0.7.17"' in s and s.count("registerCommand(") == REG0 and s.count("registerSystem(") == SYS0 and s.count("registerGlobal(") == GLB0, \
    "no new command, ECS system or event"
assert s.count("pool.makeClass(") == MAKE0, "no new class"
assert s[s.index("# ================= assets ================="):] == ASSETS0, "0.7.17 changes nothing in the assets section"
assert s.index("public static int pocketFill(") < s.index("public static int[] items("), "pocketFill compiles before items() calls it"
assert s.index("public static boolean plainFresh(") < s.index("public static int pocketFill(") < s.index("public static long deposit("), "plainFresh first"
assert s.index("public static int classShow(") < s.index("public java.util.ArrayList recipesFor("), "classShow before recipesFor"
assert s.index("public void smithNote(") < s.index("public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{\n  this.builtRef = ref;"), "smithNote before CraftPage.build"
assert s.index("public static Object call2(") < s.index("public SackFn(int mode)"), "call2 before SackFn"
for key in ("deposit", "pocketFill", "craftList", "craftHave", "craftPay", "craftRefund", "craftCommit"):
    assert s.count('sbr0.put("sacks:fn:%s"' % key) == 1, key
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
