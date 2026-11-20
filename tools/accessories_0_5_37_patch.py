"""Derive SkyyAccessories/build_skyyaccessories_0.5.37.py from the SET pin SkyyAccessories 0.5.36 (generated - never re-run its patch). Run:
    python tools/accessories_0_5_37_patch.py   then   python SkyyAccessories/build_skyyaccessories_0.5.37.py   (never --deploy)
Check: python SkyyAccessories/test_skyyaccessories_0.5.37.py
Edit THIS patch, never the generated file. Every anchor is asserted once; finish() undoes every change on a copy and compares with 0.5.36.
--out <path> writes elsewhere (the harness re-run).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

NOTE = '''0.5.37 (2026-11-20, round inv5) = THE CHARMS PANEL BRIDGE (SkyyMenu 0.3.54 draws Void Charms INSIDE the inventory: 'All charms' swaps
  the crafting area, no jump to the old Void Charms page). Skyy's words: "Start it now" (11-20); popup 'Where should editing Requip presets (and
  the Charms page) happen instead?' -> "Inside the inventory (Recommended)"; TEST 284 "i dont see the pets the requip, the charms, the pockets,
  the teleports."; approved art research/ui-theme-art/inventory-mockup-charms.png.
  ONE new bridge key, acc:fn:charms = the existing AccBagFn (its apply now also answers the "vc:" ops; acc:fn:bag's own ops are unchanged):
    apply(Object[] { "vc:list" | "vc:tier" | "vc:take" | "vc:put", UUID, profile key ("" for vc:list), arg }) -> String, on the player's
    WORLD THREAD only (else "off|..." / "-..."; nothing moves).
    vc:list  arg "" or "<slot>|<id>" -> "ok|used|cap|bag length|Accessory Power|profile key" + one "c|slot|id|AP|name|rarity|effects" per
             charm (AP < 0 = not counting: -1 a better one of its line counts, -2 the Omni covers it, -3 line off, -4 retired, -5 a second copy
             of the same charm) + "t|line|what it gives" (AccDefs.bonusRows = ALL CHARMS TOGETHER, only the best of each line) + for the picked
             charm "s|slot|id|mode|recipe id|status|AP tag|effects|next name|next rarity" and its costs "n|1 or 0|text" (mode u = Tier up
             possible, m = top of its line / the Omni, x = not counting - a better one is in, n = no tier up). The costs and the status come
             from the EXISTING Void Charms -> Craft rows (AccCraft.stepOf / lineRow / planFor / haveOf: the same "have / need" with Enchanted
             items, the same locks) - NO new recipe, cost or balance.
    vc:tier  arg "<slot>|<id>|<recipe id>" -> AccCraft.craft with the line's next step = the Craft tab's own in-place upgrade (journal,
             rollback, Enchanted opening, CraftRecipeEvent). Refused before anything moves when the slot no longer holds that charm, it is not
             the best of its line, or the recipe id is not the one shown (a double click / a stale panel uses nothing).
    vc:take  arg "<slot>|<id>" -> the page's Unequip (AccStore.unequipK + giveOne; a full inventory = the charm goes back into its slot).
    vc:put   arg "<item id>" -> the page's Equip (canEquipK first, takeOne, equipK, giveBack on a refusal, the upgraded-out one returned).
    Every action checks the PROFILE KEY the panel was drawn for (a profile switch = "-Your profile changed", nothing moves), the profile busy
    gate (moveBlock) and an unreadable bag file, like the page. Answers start with "+" (done) or "-" (nothing changed).
  MERGE 3 and UPGRADE BAG (approved art) are NOT built: Void Charms has no merge rule and no per-player bag upgrade today (the slot count is the
  server setting slots); their costs are Skyy's design call (research/Hubs-Spec.md 4.2) - next round after Skyy picks them.
  SAVED DATA: none (the bag files are written by the same AccStore calls the page uses). No config row, no migration, no new class / system /
  command; one bridge key. ROLLBACK to 0.5.36: safe alone - SkyyMenu 0.3.54 then finds no acc:fn:charms and 'All charms' opens the Void Charms
  page as 0.3.53 did.
'''

P = G.Patch(os.path.join(ROOT, "SkyyAccessories", "build_skyyaccessories_0.5.36.py"), os.path.join(ROOT, "SkyyAccessories", "build_skyyaccessories_0.5.37.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.5.36"') and P.has("tools/accessories_0_5_36_patch.py") and P.has('"sacks:fn:takeOpen"') and not P.has("acc:fn:charms"), "not the generated SkyyAccessories 0.5.36 script"
SYS0, CMD0, CLS0 = P.s.count("registerSystem("), P.s.count("registerCommand("), P.s.count("makeClass(")

P.rep('''"""SkyyAccessories 0.5.36 - build script (derived from the generated build_skyyaccessories_0.5.35.py by tools/accessories_0_5_36_patch.py -
edit the patch, not this file)
Run:   python build_skyyaccessories_0.5.36.py            -> SkyyAccessories/SkyyAccessories-0.5.36.jar   (deploys go through tools/deploy_set.py --yes)
Test:  python test_skyyaccessories_0.5.36.py             (Enchanted items count + pay for a Craft row, executed; start twice on live data)
''', '''"""SkyyAccessories 0.5.37 - build script (derived from the generated build_skyyaccessories_0.5.36.py by tools/accessories_0_5_37_patch.py -
edit the patch, not this file)
Run:   python build_skyyaccessories_0.5.37.py            -> SkyyAccessories/SkyyAccessories-0.5.37.jar   (deploys go through tools/deploy_set.py --yes)
Test:  python test_skyyaccessories_0.5.37.py             (the acc:fn:charms ops executed on the real bag + craft code; 0.5.36's checks; start twice)

''' + NOTE + '''
0.5.36 (the base; generated by tools/accessories_0_5_36_patch.py):
''')
P.rep('VERSION = "0.5.36"', 'VERSION = "0.5.37"')

# ---- AccBagFn.apply moves below AccPage (it now calls AccPage.vc - javassist compiles a call only to a method that already exists)
OLD_APPLY = '''bfn_.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  try {{
    if (!(arg instanceof Object[])) return null;
    Object[] a = (Object[]) arg;
    if (a.length < 3 || !(a[0] instanceof String) || !(a[1] instanceof java.util.UUID) || !(a[2] instanceof String)) return null;
    String op = (String) a[0];
    java.util.UUID u = (java.util.UUID) a[1];
    String k = (String) a[2];
    if ({PKG}.AccStore.DIR == null || !k.equals({PKG}.AccStore.pkey(u))) return null;
    if ({PKG}.AccStore.isBad(k) || {PKG}.AccStore.moveBlock(u) != null) return null;
    if (op.equals("list")) return {PKG}.AccStore.listK(u, k);
    if (a.length < 4 || !(a[3] instanceof String)) return null;
    String id = (String) a[3];
    if (op.equals("take")) return Integer.valueOf({PKG}.AccStore.takeK(u, k, id));
    if (op.equals("put")) {{
      int at = (a.length > 4 && a[4] instanceof Integer) ? ((Integer) a[4]).intValue() : -1;
      return Boolean.valueOf({PKG}.AccStore.putBackK(u, k, id, at));
    }}
    return null;
  }} catch (Throwable t) {{ {PKG}.AccStore.warn("acc:fn:bag failed: " + t); return null; }}
}}""", bfn_))
'''
P.rep(OLD_APPLY, '''# 0.5.37: AccBagFn.apply is added after AccPage (it answers the acc:fn:charms "vc:" ops through AccPage.vc) - see "0.5.37 THE CHARMS PANEL BRIDGE"
''')

VC = r'''# ================= 0.5.37 THE CHARMS PANEL BRIDGE (tools/accessories_0_5_37_patch.py): acc:fn:charms = AccBagFn "vc:" ops -> AccPage.vc
# (SkyyMenu 0.3.54's Charms panel). Every op runs the page's OWN rules: the Craft tab's step / row / craft, Unequip, Equip. World thread only.
JM(page, r"""
public static String vcClean(String t) {
  if (t == null) return "";
  return t.replace('|', '/').replace('\n', ' ').replace('\r', ' ');
}""")
JM(page, r"""
public static int vcInt(String s, int d) {
  if (s == null) return d;
  try { return Integer.parseInt(s.trim()); } catch (Throwable t) { return d; }
}""")
# the picked charm: what it is, can it tier up (the line's NEXT step for this bag, as the Craft tab shows it) and the costs in the "(need N
# more)" style - the same have / need numbers as the Craft row (AccCraft.haveOf: inventory + Void Charms + the Void, Enchanted items counted)
JM(page, r"""
public static String vcSel(java.util.UUID u, String k, @PLA@ p, String[] s, int si) {
  String id = s[si];
  String m = @PKG@.AccDefs.modernOf(id);
  String mode = "n";
  String rid = "";
  String status = "No tier up for this charm";
  String nextName = "";
  String nextRar = "";
  StringBuilder costs = new StringBuilder();
  if (@PKG@.AccDefs.isRetired(id)) status = @PKG@.AccDefs.retiredWhy(id);
  else {
    Object[] st = @PKG@.AccCraft.stepOf(s, m);
    if (st != null) {
      String own = (String) st[2];
      boolean mine = own != null && @PKG@.AccDefs.modernOf(own).equals(m);
      if ("m".equals(st[1])) { mode = "m"; status = "o".equals(st[3]) ? "Your Omni Accessory covers this bench at its top tier" : "Fully upgraded - the top of its line"; }
      else if ("u".equals(st[1]) && !mine) { mode = "x"; status = "Not counting - your " + @PKG@.AccCraft.accName(@PKG@.AccDefs.modernOf(own)) + " is better. Tier up that one, or take this one out."; }
      else if ("u".equals(st[1]) && st[0] != null) {
        com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe r = (com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe) st[0];
        mode = "u";
        rid = r.getId();
        String nx = @PKG@.AccCraft.outId(r);
        nextName = @PKG@.AccCraft.accName(nx);
        nextRar = @PKG@.AccDefs.rarityName(nx);
        String[] row = @PKG@.AccCraft.lineRow(u, k, p, new Object[] { st[0], st[1], st[2], st[3], nx });
        status = row[2];
        if (status.endsWith("LOCKED")) { int e = row[4].indexOf(". "); status = status + " - " + (e > 0 ? row[4].substring(0, e) : row[4]); }
        costs.append("\nn|1|").append(vcClean("this " + @PKG@.AccCraft.accName(m)));
        Object[] pl = null;
        if (p != null && p.getInventory() != null) pl = @PKG@.AccCraft.planFor(u, k, p, r, true);
        com.hypixel.hytale.server.core.inventory.MaterialQuantity[] in = r.getInput();
        String g = @PKG@.AccDefs.groupOf(nx);
        for (int i = 0; in != null && i < in.length; i++) {
          if (in[i] == null) continue;
          if (in[i].getItemId() != null && g != null && g.equals(@PKG@.AccDefs.groupOf(@PKG@.AccDefs.modernOf(in[i].getItemId())))) continue;
          long have = @PKG@.AccCraft.haveOf(u, pl, in[i], in);
          long need = (long) in[i].getQuantity();
          String nm = @PKG@.AccCraft.matName(in[i]);
          costs.append("\nn|").append(have >= need ? "1" : "0").append('|').append(vcClean(need + " " + nm + (have >= need ? "" : "  (need " + (need - have) + " more)")));
        }
      }
    }
  }
  return "\ns|" + si + "|" + id + "|" + mode + "|" + rid + "|" + vcClean(status) + "|" + vcClean(apTag(s, id, true)) + "|" + vcClean(effects(id))
      + "|" + vcClean(nextName) + "|" + vcClean(nextRar) + costs.toString();
}""")
JM(page, r"""
public static String vcList(java.util.UUID u, String k, @PLA@ p, String arg) {
  String[] s = @PKG@.AccCraft.bagSnap(u, k);
  int cap = @PKG@.AccStore.capOf(s);
  int used = 0;
  for (int i = 0; i < s.length; i++) if (s[i] != null) used++;
  StringBuilder b = new StringBuilder();
  b.append("ok|").append(used).append('|').append(cap).append('|').append(s.length).append('|').append(@PKG@.AccPower.apOf(s)).append('|').append(k);
  java.util.HashSet seen = new java.util.HashSet();
  for (int i = 0; i < s.length; i++) {
    if (s[i] == null) continue;
    int a = @PKG@.AccPower.apOne(s, s[i]);
    if (!seen.add(s[i]) && a >= 0) a = -5;
    b.append("\nc|").append(i).append('|').append(s[i]).append('|').append(a).append('|').append(vcClean(@PKG@.AccDefs.pretty(s[i]))).append('|')
     .append(vcClean(@PKG@.AccDefs.rarityName(s[i]))).append('|').append(vcClean(effects(s[i])));
  }
  String[] t = @PKG@.AccDefs.bonusRows(s);
  for (int i = 0; i + 1 < t.length; i = i + 2) if (t[i] != null && t[i].length() > 0) b.append("\nt|").append(vcClean(t[i])).append('|').append(vcClean(t[i + 1]));
  String[] q = arg == null ? new String[0] : arg.split("\\|", -1);
  if (q.length >= 2) {
    int si = vcInt(q[0], -1);
    if (si >= 0 && si < s.length && s[si] != null && s[si].equals(q[1])) b.append(vcSel(u, k, p, s, si));
  }
  return b.toString();
}""")
# TIER UP = the Craft tab's own in-place upgrade of the line's next step; refused BEFORE anything moves when the panel was stale
JM(page, r"""
public static String vcTier(@PR@ pr, @REF@ ref, @ST@ st, @PLA@ p, java.util.UUID u, String k, String arg) {
  String[] q = arg == null ? new String[0] : arg.split("\\|", -1);
  if (q.length < 3) return "-Pick a charm first - nothing was used";
  String[] s = @PKG@.AccCraft.bagSnap(u, k);
  int si = vcInt(q[0], -1);
  String id = q[1];
  if (si < 0 || si >= s.length || s[si] == null || !s[si].equals(id)) return "-That charm moved - nothing was used";
  String m = @PKG@.AccDefs.modernOf(id);
  Object[] sp = null;
  if (!@PKG@.AccDefs.isRetired(id)) sp = @PKG@.AccCraft.stepOf(s, m);
  if (sp == null || sp[0] == null || !"u".equals(sp[1])) return "-" + @PKG@.AccCraft.accName(m) + " cannot tier up - nothing was used";
  if (sp[2] == null || !@PKG@.AccDefs.modernOf((String) sp[2]).equals(m)) return "-Only your best charm of this line can tier up - nothing was used";
  String rid = ((com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe) sp[0]).getId();
  if (!rid.equals(q[2])) return "-That charm changed - look at it again, nothing was used";
  String r = @PKG@.AccCraft.craft(pr, ref, st, p, u, k, rid);
  if (r == null) r = "";
  return (r.startsWith("upgraded") || r.startsWith("crafted") ? "+" : "-") + r;
}""")
# TAKE OUT = the page's Unequip (the slot named, the charm checked; a full inventory puts it straight back)
JM(page, r"""
public static String vcTake(@PLA@ p, java.util.UUID u, String k, String arg) {
  String[] q = arg == null ? new String[0] : arg.split("\\|", -1);
  if (q.length < 2) return "-Pick a charm first - nothing changed";
  String[] s = @PKG@.AccCraft.bagSnap(u, k);
  int si = vcInt(q[0], -1);
  if (si < 0 || si >= s.length || s[si] == null || !s[si].equals(q[1])) return "-That charm moved - nothing changed";
  String id = @PKG@.AccStore.unequipK(u, k, si);
  if (id == null) return "-That charm moved - nothing changed";
  if (!id.equals(q[1])) { @PKG@.AccStore.putK(u, k, si, id); return "-That charm moved - nothing changed"; }
  String give = @PKG@.AccDefs.modernOf(id);
  if (!giveOne(p, give)) { @PKG@.AccStore.putK(u, k, si, id); return "-Your inventory is full - " + @PKG@.AccDefs.pretty(id) + " stays in Void Charms"; }
  return "+Took out " + @PKG@.AccDefs.pretty(give) + " - it is in your inventory" + (give.equals(id) ? "" : " (your older copy came back as the current item)");
}""")
# PUT IN (a charm dragged from the bag onto the panel) = the page's Equip
JM(page, r"""
public static String vcPut(@PLA@ p, java.util.UUID u, String k, String id) {
  if (id == null || id.length() == 0 || !@PKG@.AccDefs.isAccessory(id)) return "-Only charms go into Void Charms - nothing moved";
  if (!carried(p).contains(id)) return "-Could not find " + @PKG@.AccDefs.pretty(id) + " in your inventory - nothing moved";
  if (@PKG@.AccDefs.isRetired(id)) return "-" + @PKG@.AccDefs.retiredWhy(id);
  String put = @PKG@.AccDefs.modernOf(id);
  String why = "Void Charms is full, or the same or a better " + @PKG@.AccDefs.lineLabel(id) + " is already in it";
  if (!@PKG@.AccStore.canEquipK(u, k, put)) return "-" + why;
  if (!takeOne(p, id)) return "-Could not find " + @PKG@.AccDefs.pretty(id) + " in your inventory - nothing moved";
  String res = @PKG@.AccStore.equipK(u, k, put);
  if (res == null) {
    int g = giveBack(p, u, k, id);
    return "-" + (g == 0 ? why : (g == 1 ? why + " - it was kept in a free slot" : "could not give " + @PKG@.AccDefs.pretty(id) + " back - inventory and Void Charms full, reported to the server log"));
  }
  @PKG@.AccSnd.equipped(u, res);
  if (res.length() > 0) {
    String old = @PKG@.AccDefs.modernOf(res);
    int g = giveBack(p, u, k, old);
    return "+Upgraded to " + @PKG@.AccDefs.pretty(id) + " - " + (g == 0 ? @PKG@.AccDefs.pretty(old) + " is back in your inventory" : (g == 1 ? @PKG@.AccDefs.pretty(old) + " was kept in Void Charms - inventory full" : @PKG@.AccDefs.pretty(old) + " could not be returned - reported to the server log"));
  }
  return "+Put " + @PKG@.AccDefs.pretty(put) + " into Void Charms" + (put.equals(id) ? "" : " - converted from an older copy");
}""")
JM(page, r"""
public static String vc(String op, @PR@ pr, @REF@ ref, @ST@ st, @PLA@ p, java.util.UUID u, String k, String arg) {
  boolean list = "vc:list".equals(op);
  String f = list ? "off|" : "-";
  if (u == null || p == null) return f + "Your player could not be read - nothing changed";
  if (@PKG@.AccStore.DIR == null) return f + "Void Charms is still starting - try again";
  String cur = @PKG@.AccStore.pkey(u);
  if (cur == null) return f + "Your profile is not loaded yet - try again";
  if (!list && (k == null || !k.equals(cur))) return "-Your profile changed - pick the charm again (nothing changed)";
  String blk = @PKG@.AccStore.moveBlock(u);
  if (blk != null) return f + blk;
  @PKG@.AccStore.slotsK(u, cur);
  if (@PKG@.AccStore.isBad(cur)) return f + "Your Void Charms file could not be read - nothing changed, tell an admin (server log)";
  if (list) return vcList(u, cur, p, arg);
  if ("vc:tier".equals(op)) return vcTier(pr, ref, st, p, u, cur, arg);
  if ("vc:take".equals(op)) return vcTake(p, u, cur, arg);
  if ("vc:put".equals(op)) return vcPut(p, u, cur, arg);
  return "-Void Charms does not know that - nothing changed";
}""")
# AccBagFn: the player of a "vc:" call (the world thread only) + apply (acc:fn:bag's own ops exactly as 0.5.19 - 0.5.36)
JM(bfn_, r"""
public static Object vcApply(Object[] a) {
  String op = (String) a[0];
  java.util.UUID u = (java.util.UUID) a[1];
  String k = a.length > 2 && a[2] instanceof String ? (String) a[2] : "";
  String arg = a.length > 3 && a[3] instanceof String ? (String) a[3] : "";
  String f = "vc:list".equals(op) ? "off|" : "-";
  @PR@ pr = null;
  try { pr = @UNI@.get().getPlayer(u); } catch (Throwable t) { pr = null; }
  if (pr == null || !pr.isValid()) return f + "You are not online here";
  @REF@ ref = pr.getReference();
  @ST@ st = ref == null ? null : ref.getStore();
  if (st == null || !st.isInThread()) return f + "Void Charms answers on your world thread only - try again";
  @PLA@ p = null;
  try { p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  return @PKG@.AccPage.vc(op, pr, ref, st, p, u, k, arg);
}""")
JM(bfn_, r"""
public Object apply(Object arg) {
  try {
    if (!(arg instanceof Object[])) return null;
    Object[] a = (Object[]) arg;
    if (a.length >= 2 && a[0] instanceof String && ((String) a[0]).startsWith("vc:") && a[1] instanceof java.util.UUID) return vcApply(a);
    if (a.length < 3 || !(a[0] instanceof String) || !(a[1] instanceof java.util.UUID) || !(a[2] instanceof String)) return null;
    String op = (String) a[0];
    java.util.UUID u = (java.util.UUID) a[1];
    String k = (String) a[2];
    if (@PKG@.AccStore.DIR == null || !k.equals(@PKG@.AccStore.pkey(u))) return null;
    if (@PKG@.AccStore.isBad(k) || @PKG@.AccStore.moveBlock(u) != null) return null;
    if (op.equals("list")) return @PKG@.AccStore.listK(u, k);
    if (a.length < 4 || !(a[3] instanceof String)) return null;
    String id = (String) a[3];
    if (op.equals("take")) return Integer.valueOf(@PKG@.AccStore.takeK(u, k, id));
    if (op.equals("put")) {
      int at = (a.length > 4 && a[4] instanceof Integer) ? ((Integer) a[4]).intValue() : -1;
      return Boolean.valueOf(@PKG@.AccStore.putBackK(u, k, id, at));
    }
    return null;
  } catch (Throwable t) { @PKG@.AccStore.warn("acc:fn:bag / acc:fn:charms failed: " + t); return null; }
}""")

'''
P.rep('''fac.addInterface(pool.get("java.util.function.Function"))
fac.addConstructor(CtNewConstructor.make("public AccPageFactory() { }", fac))
''', VC + '''fac.addInterface(pool.get("java.util.function.Function"))
fac.addConstructor(CtNewConstructor.make("public AccPageFactory() { }", fac))
''')
P.rep('''  @PKG@.AccStore.bridge().put("acc:fn:bag", new @PKG@.AccBagFn());       // 0.5.19: benches + /craft count and take accessories from the bag (SkyySacks 0.8.11)
''', '''  @PKG@.AccStore.bridge().put("acc:fn:bag", new @PKG@.AccBagFn());       // 0.5.19: benches + /craft count and take accessories from the bag (SkyySacks 0.8.11)
  @PKG@.AccStore.bridge().put("acc:fn:charms", new @PKG@.AccBagFn());    // 0.5.37: SkyyMenu 0.3.54's Charms panel ("vc:" ops, world thread)
''')
P.rep('''  try { com.skyy.accessories.AccStore.bridge().remove("acc:fn:bag"); } catch (Throwable t) { }   // 0.5.19
''', '''  try { com.skyy.accessories.AccStore.bridge().remove("acc:fn:bag"); } catch (Throwable t) { }   // 0.5.19
  try { com.skyy.accessories.AccStore.bridge().remove("acc:fn:charms"); } catch (Throwable t) { }   // 0.5.37
''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0 and P.s.count("makeClass(") == CLS0, "0.5.37 adds no class, system or command"
assert P.s.count('"acc:fn:charms"') == 2 and P.s.count("public Object apply(Object arg) {\n  try {\n    if (!(arg instanceof Object[])) return null;\n    Object[] a = (Object[]) arg;\n    if (a.length >= 2") == 1, "0.5.37: one key, one apply"
_i = P.s.index
assert _i("public static String vcSel(") < _i("public static String vcList(") < _i("public static String vc(String op") < _i("public static Object vcApply(") < _i('if (a.length >= 2 && a[0] instanceof String && ((String) a[0]).startsWith("vc:")'), "0.5.37: methods before callers"
assert _i("public static int giveBack(") < _i("public static String vcPut(") and _i("public void handleDataEvent(@REF@ ref, @ST@ st, String data)") < _i("public static String vcClean("), "0.5.37: after the page's helpers"
P.finish()
