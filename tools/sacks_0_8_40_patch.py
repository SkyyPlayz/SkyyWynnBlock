"""Derive SkyySacks/build_skyysacks_0.8.40.py from the SET pin 0.8.39 (the GENERATED build_skyysacks_0.8.39.py; edit THIS file, then
regenerate: python tools/sacks_0_8_40_patch.py; never re-run sacks_0_8_39_patch.py on top of it). Every anchor is asserted once; at the end
every change is undone on a copy and compared with 0.8.39 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_40_patch.py   then   python SkyySacks/build_skyysacks_0.8.40.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.40.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.40 (2026-11-21, round inv7) = THE FURNACE / TANNERY BRIDGES for SkyyMenu 0.3.56's themed Furnace + Tanning panel inside the inventory
  (Skyy 2026-11-21 "Start it now" on 'Start the next inventory round (Furnace, skill XP bars, Requip leftovers)?'; 11-14 "furnace and
  tanning will have a custom look and work more like they do in our pack" + on the approved furnace mockup "i donty see how you add the
  fuel. and move the search to the top of the metal row, above coper.").
  Two new keys on skyy.bridge (SackFn modes 23 / 24), java.lang types only, the player's WORLD THREAD only (playerOf: off it they answer
  null, nothing read, nothing moves). They reuse the Crafting page's OWN Furnace / Tannery code - no new rule, cost, time or number:
  1. sacks:fn:furnList {UUID, String bench ("Furnace" / "Tannery"), String selected recipe id, String search} -> String:
     "ok|<bench>|<accessory tier>|<status = ProcBench.describe[0]>|<running unit = describe[1]>|<percent>|<queued>|<queue cap>|<needs fuel
     0/1>|<fuel items loaded>|<fuel cap>|<fuel state 0 none / 1 enough / 2 short>|<fuel time>|<fuel the queue needs>|<ready total>|<profile
     token>" then lines q|<out id>|<name>|<count>|<batch time>|<done in> (the queue, ProcBench.queueRows), o|<id>|<name>|<n> (ready to
     collect), f|<id>|<name>|<count>|<burn time> (loaded fuel, ProcBench.fuelRows), h|<fuel id>|<name>|<have> (fuel you own: inventory +
     the Void, most first = CraftPage.fuelsOwned; only when the bench burns fuel), r|<recipe id>|<output id>|<output qty>|<can make>|<tier
     tag>|<name>|<lock note>|<time each> (the recipes of THAT bench exactly as the Crafting page's tab lists them: CraftPage.benchRecipes +
     the alloys, accessory recipes skipped, ingots first by tier on the Furnace = RecipeCmp.furnaceKey, the 0.8.24 / 0.8.20 alloy locks;
     the search keeps the rows whose name or id holds the words), i|<input id or res:<type>>|<name>|<have>|<per unit> (the selected
     recipe's inputs, counted as the page counts: inventory + every Void stack). "off|<reason>" = the Void paused (profile loading /
     switching), the bench file unreadable (ProcStore.BROKEN), no such bench, or no accessory and nothing in that bench (the page's
     sub-tab rule, CraftPage.benchShown). {UUID, "sum"} -> "sum|<bench>|<ready>|<queued>|<first ready name>" per bench with work (Right
     now; reads only, no advance, no file write).
  2. sacks:fn:furn {UUID, String bench, String op, String arg, String amount, String profile token} -> "+<the page's own answer>" done /
     "-<reason>" refused: op queue (arg = recipe id that IS in the list above, amount = a number or all) = CraftPage.procQueue (inputs
     leave the inventory + the Void with counted removal, rounds, refunds of any extra, Smelting Fortune, the queue cap); fuel (arg = a fuel
     id, amount empty = all that fits / a number / all) = the ADD FUEL branch (room = fuel cap - loaded, have = inventory + the Void) then
     CraftPage.procFuelN (counted removal); collect = CraftPage.procCollect (storage first, only what fits, verified by counting - the rest
     stays in the bench: a full inventory loses nothing); cancel = procCancel (every unfinished unit's inputs to the output slot, then
     collect); unload = procUnload (unburned fuel to the output slot, then collect). The SAME gates as the page: the settled profile key,
     a token that is not the settled profile's (or none) = "-Your profile changed" and NOTHING moves; queue needs the bench accessory
     (tier > 0); a broken bench file refuses; a throw inside saves (saveSoon) and answers "-". Every action is the page's - items are taken
     exactly once (the page's counted removal), a refused queue refunds what it took (procQueue's give-back).
  Test seam (like PLAYERS): SackBridge.FRECIPES (volatile Function, null in the game) - the harness hands the recipe list in.
  No saved-data change (processing/<key>.properties is written by the same ProcStore code as the Crafting page), no config row, no
  system / command. ROLLBACK to 0.8.39: safe alone (the two keys disappear; SkyyMenu 0.3.56 then opens the pack's own Furnace / Tannery
  pages as 0.3.55 did - the queues are the same file).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.39.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.40.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.8.39"\n') and P.has("openPocket") and not P.has("furnList"), "not the live generated SkyySacks 0.8.39"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.40 (2026-11-21"):].rstrip() + "\n"

P.rep('''  No saved-data change (comp.off.<Category> is the 0.8.30 line), no config row, no system / command. ROLLBACK to 0.8.38: safe alone (the
  two ops answer "-Unknown pocket action" and openPocket disappears; SkyyMenu 0.3.55 then hides the toggle and opens the Void page).
''', '''  No saved-data change (comp.off.<Category> is the 0.8.30 line), no config row, no system / command. ROLLBACK to 0.8.38: safe alone (the
  two ops answer "-Unknown pocket action" and openPocket disappears; SkyyMenu 0.3.55 then hides the toggle and opens the Void page).
''' + NOTE)
P.rep('VERSION = "0.8.39"\n', 'VERSION = "0.8.40"\n')
P.rep('''; pocket Upgrades link + Auto-compact toggle (0.8.39)");''',
      '''; pocket Upgrades link + Auto-compact toggle (0.8.39); Furnace / Tannery bridges for the inventory panel (0.8.40)");''')

# ---- SackBridge: the test seam (next to PLAYERS)
P.rep('''sbr.addField(CtField.make("public static volatile java.util.function.Function PLAYERS;", sbr))
''', '''sbr.addField(CtField.make("public static volatile java.util.function.Function PLAYERS;", sbr))
sbr.addField(CtField.make("public static volatile java.util.function.Function FRECIPES;", sbr))   # 0.8.40: harness only (null in the game)
''')

# ---- SackBridge: the Furnace / Tannery list + actions (after openPocket, before fishCall: every CraftPage / ProcBench member is compiled before)
FURN = '''# 0.8.40 (tools/sacks_0_8_40_patch.py): SkyyMenu 0.3.56's FURNACE / TANNING panel - the Crafting page's own Furnace / Tannery code
sbr.addMethod(CtNewMethod.make(jt(r"""
public static String fclean(String s) {
  if (s == null) return "";
  return s.replace('|', '/').replace('\\n', ' ').replace('\\r', ' ');
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static String benchOf(String b) {
  if (b == null) return null;
  if (b.equalsIgnoreCase("Furnace")) return "Furnace";
  if (b.equalsIgnoreCase("Tannery") || b.equalsIgnoreCase("Tanning")) return "Tannery";
  return null;
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static String capFirst(String r) {
  if (r == null || r.length() == 0) return "";
  return String.valueOf(Character.toUpperCase(r.charAt(0))) + r.substring(1);
}"""), sbr))
# the recipes of one timed bench exactly as CraftPage.recipesFor("P:<bench>") lists them (timed: no tableOnly / group / knowledge filter)
sbr.addMethod(CtNewMethod.make(jt(r"""
public static java.util.ArrayList furnRecipes(java.util.UUID u, String bench) {
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.function.Function f = FRECIPES;
  if (f != null) {
    Object o = f.apply(bench);
    if (o instanceof java.util.List) out.addAll((java.util.List) o);
    return out;
  }
  java.util.TreeSet ids = @PKG@.CraftPage.benchRecipes(u, bench);
  if ("Furnace".equals(bench)) ids.addAll(@PKG@.CraftPage.alloyRecipes());
  java.util.Iterator it = ids.iterator();
  while (it.hasNext()) {
    Object o = @CRR@.getAssetMap().getAsset(it.next());
    if (!(o instanceof @CRR@)) continue;
    if (@PKG@.CraftPage.artifact((@CRR@) o)) continue;
    out.add(o);
  }
  return out;
}"""), sbr))
# the player's entity ref + store (null = not in a world); the harness (PLAYERS set) gets {null, null} - procQueue / procCollect accept them
sbr.addMethod(CtNewMethod.make(jt(r"""
public static Object[] furnRS(java.util.UUID u) {
  if (PLAYERS != null) return new Object[] { null, null };
  @PR@ pr = null;
  try { pr = @UNI@.get().getPlayer(u); } catch (Throwable t) { pr = null; }
  if (pr == null || !pr.isValid()) return null;
  @REF@ r = pr.getReference();
  if (r == null || !r.isValid()) return null;
  @ST@ st = r.getStore();
  if (st == null) return null;
  return new Object[] { r, st };
}"""), sbr))
# Right now: every bench with work (reads only - no advance, no create, no file write)
sbr.addMethod(CtNewMethod.make(jt(r"""
public static String furnSum(java.util.UUID u) {
  String k = @PKG@.SackPool.settledKey(u);
  if (k == null || @PKG@.ProcStore.BROKEN.containsKey(k)) return "";
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < @PKG@.ProcStore.BENCHES.length; i++) {
    String b = @PKG@.ProcStore.BENCHES[i];
    @PKG@.ProcBench pb = @PKG@.ProcStore.get(k, b);
    if (pb == null) continue;
    int o = pb.outTotal();
    int qn = pb.queued();
    if (o <= 0 && qn <= 0) continue;
    java.util.ArrayList ol = pb.outList();
    String first = ol.isEmpty() ? "" : @PKG@.ProcBench.itemName((String) ((Object[]) ol.get(0))[0]);
    if (sb.length() > 0) sb.append('\\n');
    sb.append("sum|").append(b).append('|').append(o).append('|').append(qn).append('|').append(fclean(first));
  }
  return sb.toString();
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static String furnList(java.util.UUID u, String b0, String sel, String q) {
  @PLA@ p = playerOf(u);
  if (p == null) return null;
  if ("sum".equals(b0)) return furnSum(u);
  String bench = benchOf(b0);
  if (bench == null) return "off|No such bench";
  String k = @PKG@.SackPool.settledKey(u);
  if (k == null) return "off|The Void is paused (profile loading or switching) - try again in a moment";
  if (@PKG@.ProcStore.BROKEN.containsKey(k)) return "off|Your " + bench + " file could not be read - it was left untouched. Tell an admin.";
  int tier = @PKG@.CraftPage.accTier(@PKG@.CraftPage.accessories(p, u), bench);
  @PKG@.ProcBench pb = @PKG@.ProcStore.get(k, bench);
  if (tier <= 0 && (pb == null || !pb.pending())) return "off|Equip a " + bench + " accessory in your Void Charms to use the " + bench;
  long now = System.currentTimeMillis();
  if (pb != null && pb.advance(now) > 0) @PKG@.ProcStore.markDirty(k);
  @PKG@.ProcBench view = pb != null ? pb : new @PKG@.ProcBench(bench);
  if (pb == null) { view.key = k; view.advance(now); }
  String[] d = view.describe(tier, tier > 0);
  boolean fuel = view.needsFuel && !view.cEternal;
  StringBuilder sb = new StringBuilder();
  sb.append("ok|").append(bench).append('|').append(tier).append('|').append(fclean(d[0])).append('|').append(fclean(d[1])).append('|').append(fclean(d[4]));
  sb.append('|').append(view.queued()).append('|').append(@PKG@.ProcBench.QUEUE_CAP).append('|').append(fuel ? 1 : 0).append('|').append(view.fuelCount());
  sb.append('|').append(@PKG@.ProcBench.FUEL_CAP).append('|').append(view.fuelState()).append('|').append(@PKG@.ProcBench.dur(view.fuelEffMs()));
  sb.append('|').append(@PKG@.ProcBench.dur(view.fuelNeedMs())).append('|').append(view.outTotal()).append('|').append(tok(k));
  java.util.ArrayList qr = view.queueRows();
  for (int i = 0; i < qr.size() && i < 40; i++) {
    Object[] e = (Object[]) qr.get(i);
    sb.append("\\nq|").append(e[0] == null ? "" : fclean((String) e[0])).append('|').append(fclean((String) e[1])).append('|').append(e[2]);
    sb.append('|').append(@PKG@.ProcBench.dur(((Long) e[3]).longValue())).append('|').append(@PKG@.ProcBench.dur(((Long) e[4]).longValue()));
  }
  java.util.ArrayList ol = view.outList();
  for (int i = 0; i < ol.size() && i < 40; i++) {
    Object[] e = (Object[]) ol.get(i);
    String oid = (String) e[0];
    sb.append("\\no|").append(fclean(oid)).append('|').append(fclean(@PKG@.ProcBench.itemName(oid))).append('|').append(e[1]);
  }
  java.util.ArrayList fr = view.fuelRows();
  for (int i = 0; i < fr.size() && i < 20; i++) {
    Object[] e = (Object[]) fr.get(i);
    sb.append("\\nf|").append(e[0] == null ? "" : fclean((String) e[0])).append('|').append(fclean((String) e[1])).append('|').append(e[2]);
    sb.append('|').append(@PKG@.ProcBench.dur(((Long) e[3]).longValue()));
  }
  if (fuel) {
    java.util.ArrayList ho = @PKG@.CraftPage.fuelsOwned(p, k);
    for (int i = 0; i < ho.size() && i < 30; i++) {
      Object[] e = (Object[]) ho.get(i);
      String fid = (String) e[0];
      sb.append("\\nh|").append(fclean(fid)).append('|').append(fclean(@PKG@.ProcBench.itemName(fid))).append('|').append(e[1]);
    }
  }
  if (tier > 0) {
    java.util.ArrayList raw = furnRecipes(u, bench);
    @CIC@ mats = @PKG@.CraftPage.countMats(p, k, @PKG@.CraftPage.procWanted(raw));
    int ctier = "Furnace".equals(bench) ? @PKG@.ProcBench.smelt(k)[0] : 0;
    java.util.Set aKnown = @PKG@.KnowSync.known(p);
    java.util.HashSet aColl = @PKG@.CraftPage.collectionRecipes(u);
    boolean furn = "Furnace".equals(bench);
    String ql = q == null ? "" : q.trim().toLowerCase();
    java.util.ArrayList ent = new java.util.ArrayList();
    @CRR@ selR = null;
    for (int i = 0; i < raw.size(); i++) {
      @CRR@ r0 = (@CRR@) raw.get(i);
      @MQ@ o0 = r0.getPrimaryOutput();
      String id0 = o0 == null ? String.valueOf(r0.getId()) : o0.getItemId();
      if (sel != null && sel.length() > 0 && sel.equals(String.valueOf(r0.getId()))) selR = r0;
      if (ql.length() > 0) {
        String nm0 = @PKG@.ProcBench.itemName(id0).toLowerCase();
        if (nm0.indexOf(ql) < 0 && id0.toLowerCase().indexOf(ql) < 0) continue;
      }
      int l0 = @PKG@.CraftPage.limit(r0, mats);
      String lock = "";
      int an = @PKG@.ProcBench.alloyNeed(r0);
      if (!@PKG@.CraftPage.alloyOk(r0, aKnown, aColl)) { l0 = 0; lock = "your collections unlock this (/collections)"; }
      else if (an > ctier) { l0 = 0; lock = "Furnace Charm T" + an + " unlocks this"; }
      boolean ing0 = furn && o0 != null;
      ent.add(new Object[] { r0, Integer.valueOf(l0), Integer.valueOf(ing0 ? @PKG@.RecipeCmp.furnaceKey(id0) : @PKG@.RecipeCmp.sortKey(id0)), ing0 ? @PKG@.RecipeCmp.furnaceName(id0) : @PKG@.RecipeCmp.sortName(id0), lock });
    }
    java.util.Collections.sort(ent, new @PKG@.RecipeCmp());
    for (int i = 0; i < ent.size() && i < 300; i++) {
      Object[] e = (Object[]) ent.get(i);
      @CRR@ r = (@CRR@) e[0];
      @MQ@ o = r.getPrimaryOutput();
      String oid = o == null ? "" : o.getItemId();
      long each = @PKG@.ProcBench.charmMs(@PKG@.ProcBench.unitMs(r, bench, tier), view.cTime);
      sb.append("\\nr|").append(fclean(String.valueOf(r.getId()))).append('|').append(fclean(oid)).append('|').append(o == null ? 1 : o.getQuantity()).append('|').append(e[1]);
      sb.append('|').append(fclean(@PKG@.RecipeCmp.tierText(oid))).append('|').append(fclean(@PKG@.ProcBench.itemName(oid))).append('|').append(fclean((String) e[4]));
      sb.append('|').append(@PKG@.ProcBench.dur(each));
    }
    if (selR != null) {
      @MQ@[] in = selR.getInput();
      for (int i = 0; in != null && i < in.length && i < 6; i++) {
        if (in[i] == null) continue;
        String iid = in[i].getItemId();
        String rt = in[i].getResourceTypeId();
        int have = mats.countRemovableMaterial(in[i]);
        sb.append("\\ni|").append(iid != null ? fclean(iid) : "res:" + fclean(rt)).append('|');
        sb.append(fclean(iid != null ? @PKG@.ProcBench.itemName(iid) : ("Any " + (rt == null ? "" : rt.replace('_', ' '))))).append('|').append(have).append('|').append(in[i].getQuantity());
      }
    }
  }
  return sb.toString();
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static String furnAct(java.util.UUID u, String b0, String op, String arg, String amt, String want) {
  @PLA@ p = playerOf(u);
  if (p == null) return null;
  String bench = benchOf(b0);
  if (bench == null) return "-No such bench";
  String k = @PKG@.SackPool.settledKey(u);
  if (k == null) return "-The Void is paused (profile loading or switching) - nothing was done";
  if (want == null || want.length() == 0 || !want.equals(tok(k))) return "-Your profile changed - the " + bench + " now shows it; nothing was done";
  if (@PKG@.ProcStore.BROKEN.containsKey(k)) return "-Your " + bench + " file could not be read - nothing was taken";
  Object[] rs = furnRS(u);
  if (rs == null) return "-You are not in a world right now - nothing was done";
  @REF@ ref = (@REF@) rs[0];
  @ST@ st = (@ST@) rs[1];
  String r = null;
  try {
    if ("collect".equals(op)) r = @PKG@.CraftPage.procCollect(p, st, ref, k, bench);
    else if ("cancel".equals(op)) r = @PKG@.CraftPage.procCancel(p, st, ref, k, bench);
    else if ("unload".equals(op)) r = @PKG@.CraftPage.procUnload(p, st, ref, k, bench);
    else if ("fuel".equals(op)) {
      if (arg == null || arg.length() == 0) return "-Pick a fuel first";
      if (@PKG@.ProcBench.fuelQuality(arg) <= 0.0) return "-" + @PKG@.ProcBench.itemName(arg) + " does not burn";
      @PKG@.ProcBench pb = @PKG@.ProcStore.of(k, bench);
      if (!pb.needsFuel) return "-The " + bench + " burns no fuel";
      pb.advance(System.currentTimeMillis());
      int room = @PKG@.ProcBench.FUEL_CAP - pb.fuelCount();
      if (room < 0) room = 0;
      long have = @PKG@.CraftPage.fuelHave(p, k, arg);
      long max = have < (long) room ? have : (long) room;
      long n = @PKG@.SacksPage.parseAmt(amt, max);
      if (n == -2L) return "-Type a number (or leave it empty for all that fits)";
      if (n > max) n = max;
      if (n <= 0L) return room <= 0 ? ("-The fuel slot is full (" + @PKG@.ProcBench.FUEL_CAP + " items)") : ("-You have no " + @PKG@.ProcBench.itemName(arg));
      r = @PKG@.CraftPage.procFuelN(p, st, ref, k, bench, arg, (int) n);
    } else if ("queue".equals(op)) {
      int tier = @PKG@.CraftPage.accTier(@PKG@.CraftPage.accessories(p, u), bench);
      if (tier <= 0) return "-Equip a " + bench + " accessory to queue";
      if (arg == null || arg.length() == 0) return "-Pick a recipe first";
      @CRR@ rec = null;
      java.util.ArrayList raw = furnRecipes(u, bench);
      for (int i = 0; i < raw.size() && rec == null; i++) {
        @CRR@ c = (@CRR@) raw.get(i);
        if (arg.equals(String.valueOf(c.getId()))) rec = c;
      }
      if (rec == null) return "-That recipe is not in your " + bench + " list - nothing was queued";
      long n = @PKG@.SacksPage.parseAmt(amt, 1L);
      if (n == -2L) return "-Type a number or all";
      int w = n > 100000000L ? 0 : (int) n;   // all (or a huge number) = 0 = everything up to the queue room (never an int overflow)
      r = @PKG@.CraftPage.procQueue(p, st, ref, k, bench, tier, rec, w);
    } else return "-Unknown " + bench + " action";
  } catch (Throwable t) {
    @PKG@.CraftPage.saveSoon(k);
    @PKG@.KnowSync.warnOnce(bench + " action " + op + " failed: " + t);
    return "-That did not finish - check your bag, the Void and the " + bench + " (nothing more will move)";
  }
  if (r == null) r = "";
  boolean ok = r.startsWith("queued ") || r.startsWith("loaded ") || r.startsWith("collected ") || r.startsWith("cancelled ") || r.startsWith("unloaded ");
  return (ok ? "+" : "-") + capFirst(r);
}"""), sbr))
'''
P.rep('''sbr.addMethod(CtNewMethod.make(jt(r"""
public static Object fishCall(int mode, Object o) {''', FURN + '''sbr.addMethod(CtNewMethod.make(jt(r"""
public static Object fishCall(int mode, Object o) {''')

# ---- SackFn: modes 23 / 24 before 22
P.rep('''    if (this.mode == 22) {   // 0.8.39 sacks:fn:openPocket {UUID, cat} -> Boolean''',
      '''    if (this.mode == 23 || this.mode == 24) {   // 0.8.40 sacks:fn:furnList {UUID, bench, sel, search} / sacks:fn:furn {UUID, bench, op, arg, amount, token}
      if (!(o instanceof Object[])) return null;
      Object[] a23 = (Object[]) o;
      if (a23.length < 2 || !(a23[0] instanceof java.util.UUID) || !(a23[1] instanceof String)) return null;
      if (this.mode == 23) return @PKG@.SackBridge.furnList((java.util.UUID) a23[0], (String) a23[1], a23.length > 2 && a23[2] instanceof String ? (String) a23[2] : "",
          a23.length > 3 && a23[3] instanceof String ? (String) a23[3] : "");
      if (a23.length < 3 || !(a23[2] instanceof String)) return null;
      return @PKG@.SackBridge.furnAct((java.util.UUID) a23[0], (String) a23[1], (String) a23[2], a23.length > 3 && a23[3] instanceof String ? (String) a23[3] : "",
          a23.length > 4 && a23[4] instanceof String ? (String) a23[4] : "", a23.length > 5 && a23[5] instanceof String ? (String) a23[5] : null);
    }
    if (this.mode == 22) {   // 0.8.39 sacks:fn:openPocket {UUID, cat} -> Boolean''')
P.rep('''|| this.mode == 20 || this.mode == 21) ? null : (this.mode == 22 ? (Object) Boolean.FALSE''',
      '''|| this.mode == 20 || this.mode == 21 || this.mode == 23 || this.mode == 24) ? null : (this.mode == 22 ? (Object) Boolean.FALSE''')
P.rep('''  sbr0.put("sacks:fn:openPocket", new {PKG}.SackFn(22));   // 0.8.39: the pocket panel's Upgrades link (the Void page on that pocket)
''', '''  sbr0.put("sacks:fn:openPocket", new {PKG}.SackFn(22));   // 0.8.39: the pocket panel's Upgrades link (the Void page on that pocket)
  sbr0.put("sacks:fn:furnList", new {PKG}.SackFn(23));   // 0.8.40: the inventory's Furnace / Tanning panel (list; world thread)
  sbr0.put("sacks:fn:furn", new {PKG}.SackFn(24));       // 0.8.40: its actions (queue / fuel / collect / cancel / unload; profile token)
''')
assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.8.40 adds no system / command"
_i = P.s.index
for _m in ("public static String procQueue(", "public static String procFuelN(", "public static String procCollect(", "public static String procCancel(",
           "public static String procUnload(", "public static java.util.ArrayList fuelsOwned(", "public static long fuelHave(", "public static String tierText(",
           "public static int furnaceKey(", "public synchronized java.util.ArrayList queueRows()", "public static String pocketAct("):
    assert _i(_m) < _i("public static String furnList("), "0.8.40: compiled before the furnace bridge: " + _m
assert _i("public static String furnSum(") < _i("public static String furnList(") < _i("public static String furnAct(") < _i("public static Object fishCall(") < _i("if (this.mode == 23 || this.mode == 24)"), "0.8.40: methods before callers"
P.finish()
