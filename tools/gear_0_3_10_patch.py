"""Derive SkyyGear/build_skyygear_0.3.10.py from the LIVE 0.3.9 (build_skyygear_0.3.9.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_3_9_patch.py). Edit THIS file, never the generated script; every anchor is asserted and every change is undone at the end to
prove nothing else changed. Run:
    python tools/gear_0_3_10_patch.py      then      python SkyyGear/build_skyygear_0.3.10.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.3.10.py

0.3.10 (2026-10-15, lean round "gear0310" = fixes from Skyy's live test):
1. THE "Loading..." HANG ON THE TOOLS TAB (Skyy: "lagged when i tried to apply points" + "ohh i clicked too fast"; screenshot: Fortune Lv 1/10
   bought, 'Fortune is level 1 now (3 points left).', the client's Loading... box stuck): LifePage.handleDataEvent dropped every click that
   came less than 400 ms after the last one with a bare `return` - no page update was sent, and the client waits for an answer to every page
   click, so it stayed on "Loading..." for good (the first click had already bought Fortune 1 and redrawn the page). Server-side nothing was
   slow (a 38 ms packet handler was the worst line). The same silent-return class: an empty / malformed click, a page whose rebuild throws,
   the Craft tab's NAV_MS guard, the Anvil's "mode:" / bad-row / no-inventory paths, the Multitool page's guards.
   FIX A - ALWAYS ANSWER (every /smithing page: Craft = SmithPage, Anvil / Identify = ReforgePage, the old Identify page, Multitool =
   MultiPage, Tools = LifePage): the click handler (with every earlier hook baked in) is wrapped; a click that sent nothing (no rebuild, no
   update, no close) gets one empty page update - but only while this page is still the player's open page (a click that opened another page
   / tab sends nothing more). Counted in GearUi.ACK.
   FIX B - ONCE PER CLICK, NO TIME GUARD ON THE TOOLS TAB: every Tools-tab build gives its paid buttons (+1, Reset, Tier up, Make multitool) a
   new click token; a click is honoured only with the current token, and the token is used up BEFORE anything is spent - so a fast click on
   the redrawn page buys the next level (no more eaten clicks), and a repeat of the same click (same page copy) spends nothing and is
   answered. A click without a token (older page) keeps the 400 ms guard - answered too.
2. TIER UP ON THE TOOLS TAB (Skyy, on the Tools tab "Tier: Crude. Next: Copper Pickaxe on the Anvil for 25 Copper Ingot (Mining 5)": "where
   do i craft my crude pickaxe into a copper? id put that here."): the picked tool's panel has a Tier up button = GearUp.upgrade, the Anvil's
   own tier-up (same check, cost, skill gate, inventory + bags, restore on failure, log lines); the line shows the next tier, the cost with
   what you have and why not. The pole keeps "at the Fishing Bench". The Anvil keeps working.
3. MAKE MULTITOOL ON THE TOOLS TAB, NO MULTITOOL TAB (Skyy: "when you hit rebirth 1 and can make a multi tool id just add that as a button
   here in the tools tab, and drop the multitool tab."): the pickaxe / hatchet panels have a Make multitool row: before rebirth 1 greyed
   with the rebirth line (GearLL.rbGate, multi.rebirthGate); after it the best plain pickaxe + hatchet pair of one tier you carry (highest
   tier, then rarity; your lifelong ones cannot be merged - GearMerge.why) is named and merged by GearMerge.merge (same checks / rolls /
   costs as the Multitool page); the pair is remembered at draw time and a click checks it is still the same two items. While the Tools tab
   exists (part.lifelong on) the Multitool tab is gone (Craft | Anvil | Identify | Tools) and /multitool opens the Tools tab on the pickaxe;
   part.lifelong off = the old Multitool page and tab.
4. THE POLE ROW (Skyy: "also i never got a fishing rod"): Skyy's records (HUD mod p9 lifelong file: no pole.* keys; Skyy_SkyyQuests npcs.tsv:
   no NPC placed) = the pole was never granted - it comes from Marlow's quest (LOCKED 2026-10-12) and Marlow is not placed yet. /pole was
   right; the Tools tab said "Arrives when you have a free inventory slot" for every missing tool. The pole row now says it comes from
   Marlow at the hub pier.
REVIEW FIXES (2026-10-15, same version): 1 a throw after the token was used redraws the page with 'Something went wrong - nothing was
changed. Click Refresh.' (fresh token); 2 one token counter for every Tools page (an older copy's click never matches a newer copy); 3 a pair
that cannot merge shows the merge's own reason; 4 the help / footer name the Tier up button; 5 /multitool sweeps like /toolpoints first.
SAVED DATA: none (no config row, no file, no item key). ROLLBACK 0.3.10 -> 0.3.9 is item-safe (the hang comes back).
"""
import os
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.9.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.10.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.9"' in s and "GENERATED by tools/gear_0_3_9_patch.py" in s and "0.3.10" not in s, "not the generated 0.3.9 script"
assert "skyHde" not in s
CHANGES = []


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)
    CHANGES.append((new, old, count))


def before(anchor, text):
    rep(anchor, text + anchor)


def after(anchor, text):
    rep(anchor, anchor + text)


_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyGear") != "0.3.9":
    print("NOTE: tools/deploy_set.py SET pins SkyyGear %s, this patch derives from 0.3.9" % _set.get("SkyyGear"))

# ================================================================================================================ docstring + version
rep('''"""SkyyGear 0.3.9 - build script (javassist via jpype). GENERATED by tools/gear_0_3_9_patch.py from the LIVE 0.3.8 (itself GENERATED by
tools/gear_0_3_8_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.9.py -> SkyyGear/SkyyGear-0.3.9.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.9.py
''', '''"""SkyyGear 0.3.10 - build script (javassist via jpype). GENERATED by tools/gear_0_3_10_patch.py from the LIVE 0.3.9 (itself GENERATED by
tools/gear_0_3_9_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.10.py -> SkyyGear/SkyyGear-0.3.10.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.10.py

0.3.10 = EVERY /smithing CLICK IS ANSWERED + TIER UP / MAKE MULTITOOL ON THE TOOLS TAB (notes: tools/gear_0_3_10_patch.py): the Tools tab
dropped clicks closer than 400 ms without an answer (the client's "Loading..." box stayed) - every Smithing page now answers every click
(an empty update when the click sent nothing), and the Tools tab's paid buttons use a click token instead of the time guard (each click
once, never twice); the Tools tab gets Tier up (the Anvil's tier-up) and Make multitool (after rebirth 1; the Multitool tab is gone,
/multitool opens the Tools tab); the pole row says it comes from Marlow.

--- 0.3.9 notes ---
''')
rep('VERSION = "0.3.9"\n', 'VERSION = "0.3.10"\n')

# ================================================================================================================ 3. no Multitool tab beside Tools
rep('''  boolean mt = multiTab();
  boolean lt = @PKG@.GearCfg.LL_ON;          // 0.3.0: the Tools tab (/toolpoints)''',
    '''  boolean mt = multiTab() && !@PKG@.GearCfg.LL_ON;          // 0.3.10: multitools are made on the Tools tab (Skyy: "drop the multitool tab")
  boolean lt = @PKG@.GearCfg.LL_ON;          // 0.3.0: the Tools tab (/toolpoints)''')

# ================================================================================================================ LifePage fields + token
rep('''for _f in ("public int sel;", "public String info;", "public long lastClick;", "public String epoch;", "public int armK;", "public long armAt;"):
    F(lpg, _f)''', '''for _f in ("public int sel;", "public String info;", "public long lastClick;", "public String epoch;", "public int armK;", "public long armAt;",
           "public int tok;", "public String mtKey;"):          # 0.3.10: the click token of this build; the multitool pair drawn
    F(lpg, _f)
# review fix 2: tokens come from ONE counter for every Tools page (a click of an older copy never matches a newer copy)
F(lpg, "public static int TOKN = (int) (System.nanoTime() & 1073741823L);")
M(lpg, "public static synchronized int nextTok() { TOKN = TOKN + 1; if (TOKN > 2000000000) TOKN = 1; return TOKN; }")''')
rep('''  java.util.Properties P = @PKG@.GearLL.reg(pk);
  @PKG@.GearUi.frame(b, "Smithing", 1100, 880);
  @PKG@.GearUi.tabs(b, ev, "#SkyyGBody", 4, 1066, "Tools");''', '''  java.util.Properties P = @PKG@.GearLL.reg(pk);
  this.tok = nextTok();          // 0.3.10: every build = a new click token on the paid buttons (one counter for all pages)
  this.mtKey = null;
  @PKG@.GearUi.frame(b, "Smithing", 1100, 880);
  @PKG@.GearUi.tabs(b, ev, "#SkyyGBody", 4, 1066, "Tools");''')
rep('''  ev.addEventBinding(@BT@.Activating, g + "B", @EVD@.of("a", "buy:" + p));''',
    '''  ev.addEventBinding(@BT@.Activating, g + "B", @EVD@.of("a", "buy:" + p + ":" + this.tok));          // 0.3.10: + the click token''')

# the +1 button's text by b.set (the kit's rule: "+" and "(" are no proven inline characters - the 0.3.9 client check is stricter now)
rep(""" TextButton " + g + "B { Anchor: (Width: 160, Height: 44); Text: \\"" + (lv >= mx ? "Max" : "+1 (" + cost + " pt)") + "\\"; " + @PKG@.GearUi.btn(can ? 0 : 3) + " } }");""",
    """ TextButton " + g + "B { Anchor: (Width: 160, Height: 44); Text: \\"\\"; " + @PKG@.GearUi.btn(can ? 0 : 3) + " } }");
  b.set(g + "B.Text", lv >= mx ? "Max" : "+1 (" + cost + " pt)");          // 0.3.10: by b.set""")

# ================================================================================================================ 4. the pole row
rep('''  if (cur == null) w = "Arrives when you have a free inventory slot";''',
    '''  if (cur == null) w = k == @PKG@.GearLL.POLE ? "From Marlow's fishing quest at the hub pier" : "Arrives when you have a free inventory slot";          // 0.3.10: the pole is a quest reward''')

# ================================================================================================================ 2 + 3. the panel's bottom rows
OLD_TAIL = '''  int sp = @PKG@.GearLL.spent(P, k);
  long rc = @PKG@.GearLL.resetCost(P, k);
  b.appendInline("#SkyyGPanel", "Label #SkyyGPReT { Anchor: (Height: 30); Text: \\"\\"; Style: (FontSize: 15, TextColor: #96a9be, VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); }");
  b.set("#SkyyGPReT.Text", sp > 0 ? "Reset: all " + sp + " spent points back for " + @PKG@.Gear.fmt(rc) + " coins (more each time)" : "Reset: nothing spent yet");
  boolean armed = this.armK == k && System.currentTimeMillis() - this.armAt < 8000L;
  b.appendInline("#SkyyGPanel", "TextButton #SkyyGPReset { Anchor: (Width: 300, Height: 44); Text: \\"" + (armed ? "Click again to pay" : "Reset points") + "\\"; " + @PKG@.GearUi.btn(sp > 0 ? 2 : 3) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyGPReset", @EVD@.of("a", "reset"));
  String to = @PKG@.GearUp.next(id);
  String tl = "Tier: " + @PKG@.GearLL.tname(@PKG@.GearLL.tier(id)) + ". ";
  if (k == @PKG@.GearLL.POLE) tl = tl + "Tier it up at the Fishing Bench (the rod recipes keep it your pole).";          // 0.3.6
  else if (to == null) tl = tl + "Top tier for now.";
  else {
    Object[] co = @PKG@.GearUp.cost(id, to);
    StringBuilder sb = new StringBuilder();
    if (co != null) {
      String[] ci = (String[]) co[0];
      int[] cq = (int[]) co[1];
      for (int i = 0; i < ci.length; i++) { if (sb.length() > 0) sb.append(" + "); sb.append(cq[i]).append(' ').append(@PKG@.Gear.itemName(ci[i])); }
    }
    tl = tl + "Next: " + @PKG@.Gear.itemName(to) + " on the Anvil" + (sb.length() > 0 ? " for " + sb.toString() : "") + " (" + @PKG@.GearLL.KSKILL[k] + " " + @PKG@.GearLevel.band(to)[0] + ").";
  }
  b.appendInline("#SkyyGPanel", "Label #SkyyGPTier { Anchor: (Height: 52); Text: \\"\\"; Style: (FontSize: 15, TextColor: #ffffff(0.8), VerticalAlignment: Center, Wrap: true); }");
  b.set("#SkyyGPTier.Text", tl);
}"""'''
NEW_TAIL = '''  int sp = @PKG@.GearLL.spent(P, k);
  long rc = @PKG@.GearLL.resetCost(P, k);
  boolean armed = this.armK == k && System.currentTimeMillis() - this.armAt < 8000L;
  // 0.3.10: three rows of text + button (Reset, Tier up, Make multitool); every paid button carries this build's click token
  b.appendInline("#SkyyGPanel", "Group #SkyyGPReRow { Anchor: (Height: 52); LayoutMode: Left; Label #SkyyGPReT { Anchor: (Width: 392); Text: \\"\\"; Style: (FontSize: 14, TextColor: #96a9be, VerticalAlignment: Center, Wrap: true); } Group { Anchor: (Width: 10); } TextButton #SkyyGPReset { Anchor: (Width: 160, Height: 44); Text: \\"" + (armed ? "Click again" : "Reset points") + "\\"; " + @PKG@.GearUi.btn(sp > 0 ? 2 : 3) + " } }");
  b.set("#SkyyGPReT.Text", armed ? "Click again within 8 s to pay " + @PKG@.Gear.fmt(rc) + " coins and get all " + sp + " points back." : (sp > 0 ? "Reset: all " + sp + " spent points back for " + @PKG@.Gear.fmt(rc) + " coins (more each time)" : "Reset: nothing spent yet"));
  ev.addEventBinding(@BT@.Activating, "#SkyyGPReset", @EVD@.of("a", "reset:" + this.tok));
  tierRow(b, ev, u, inv, pk, P, k, id);
  if (k <= 1 && @PKG@.GearCfg.MULTI_ON && @PKG@.GearMerge.loaded()) mtRow(b, ev, u, inv);
}"""'''
assert s.count(OLD_TAIL[:-4]) == 1, "the panel tail moved"
rep(OLD_TAIL[:-4], NEW_TAIL[:-4])

# the new LifePage methods (before panel: methods before callers)
before('''M(lpg, r"""
public void panel(@UCB@ b, @UEB@ ev, java.util.UUID u, @INV@ inv, String pk, java.util.Properties P) {''', r'''# 0.3.10 TIER UP ON THE TOOLS TAB: the slot of kind k's lifelong tool on the player (null = not on them)
M(lpg, r"""
public static int[] toolAt(@INV@ inv, String pk, java.util.Properties P, int k) {
  if (inv == null || P == null || k < 0 || k >= @PKG@.GearLL.KIND.length) return null;
  String cur = P.getProperty(@PKG@.GearLL.KIND[k] + ".uid");
  if (cur == null) return null;
  int[] at = @PKG@.GearLife.find(inv, pk, cur);
  if (at == null) return null;
  @IS@ x = @PKG@.GearStamp.at(inv, at[0], at[1]);
  if (x == null || x.isEmpty()) return null;
  return at;
}""")
# the cost in words with what the player has: "25 Copper Ingot (12 / 25)"
M(lpg, r"""
public static String costHave(@INV@ inv, java.util.UUID u, Object[] co) {
  if (co == null) return "";
  String[] ci = (String[]) co[0];
  int[] cq = (int[]) co[1];
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < ci.length; i++) {
    int h = inv == null ? 0 : @PKG@.GearUp.have(inv, ci[i]) + @PKG@.GearUp.bagHave(u, ci[i]);
    if (sb.length() > 0) sb.append(" + ");
    sb.append(cq[i]).append(' ').append(@PKG@.Gear.itemName(ci[i])).append(" (").append(h < cq[i] ? h : cq[i]).append(" / ").append(cq[i]).append(')');
  }
  return sb.toString();
}""")
M(lpg, r"""
public void tierRow(@UCB@ b, @UEB@ ev, java.util.UUID u, @INV@ inv, String pk, java.util.Properties P, int k, String id) {
  String tl = "Tier: " + @PKG@.GearLL.tname(@PKG@.GearLL.tier(id)) + ". ";
  if (k == @PKG@.GearLL.POLE) {          // 0.3.6: the pole climbs at the Fishing Bench
    b.appendInline("#SkyyGPanel", "Label #SkyyGPTier { Anchor: (Height: 52); Text: \"\"; Style: (FontSize: 15, TextColor: #ffffff(0.8), VerticalAlignment: Center, Wrap: true); }");
    b.set("#SkyyGPTier.Text", tl + "Tier it up at the Fishing Bench (the rod recipes keep it your pole).");
    return;
  }
  String to = @PKG@.GearUp.next(id);
  boolean can = false;
  if (!@PKG@.GearCfg.UP_ON) tl = tl + "Tiering up is switched off on this server.";
  else if (to == null) tl = tl + "Top tier for now.";
  else {
    int[] at = toolAt(inv, pk, P, k);
    Object[] co = @PKG@.GearUp.cost(id, to);
    String ct = costHave(inv, u, co);
    tl = tl + "Next: " + @PKG@.Gear.itemName(to) + (ct.length() > 0 ? " for " + ct : "") + " (" + @PKG@.GearLL.KSKILL[k] + " " + @PKG@.GearLevel.band(to)[0] + ").";
    String why;
    if (at == null) why = "Not on you - /" + @PKG@.GearLL.KIND[k] + " brings it back.";
    else {
      @IS@ x = @PKG@.GearStamp.at(inv, at[0], at[1]);
      Object[] c = @PKG@.GearUp.check(x, u);
      why = (String) c[0];
      if (why == null) why = @PKG@.GearUp.shortOfU(inv, u, (Object[]) c[2]);
    }
    if (why != null) tl = tl + " " + why;
    can = why == null;
  }
  b.appendInline("#SkyyGPanel", "Group #SkyyGPTierRow { Anchor: (Height: 64); LayoutMode: Left; Label #SkyyGPTier { Anchor: (Width: 392); Text: \"\"; Style: (FontSize: 14, TextColor: #ffffff(0.8), VerticalAlignment: Center, Wrap: true); } Group { Anchor: (Width: 10); } TextButton #SkyyGPUp { Anchor: (Width: 160, Height: 44); Text: \"Tier up\"; " + @PKG@.GearUi.btn(can ? 0 : 3) + " } }");
  b.set("#SkyyGPTier.Text", tl);
  ev.addEventBinding(@BT@.Activating, "#SkyyGPUp", @EVD@.of("a", "up:" + this.tok));
}""")
# the click: GearUp.upgrade = the Anvil's own tier-up (check, materials from inventory + bags, restore on failure, log lines, sound)
M(lpg, r"""
public void tierUp(@INV@ inv) {
  java.util.UUID u = this.playerRef.getUuid();
  int k = this.sel < 0 || this.sel >= @PKG@.GearLL.KIND.length ? 0 : this.sel;
  String K = @PKG@.GearLL.KIND[k];
  if (k == @PKG@.GearLL.POLE) { this.info = "-Tier your pole up at the Fishing Bench."; return; }
  if (!@PKG@.GearCfg.UP_ON) { this.info = "-Tiering up is switched off on this server."; return; }
  if (@PKG@.Gear.busy(u)) { this.info = "-Your profile is still loading - nothing was tiered up. Try again in a moment."; return; }
  String pk = @PKG@.Gear.pkey(u);
  java.util.Properties P = @PKG@.GearLL.reg(pk);
  if (@PKG@.GearLL.bad(P)) { this.info = "-Your lifelong tool list cannot be read right now."; return; }
  int[] at = toolAt(inv, pk, P, k);
  if (at == null) { this.info = "-Your " + K + " is not on you - /" + K + " brings it back."; return; }
  @IS@ x = @PKG@.GearStamp.at(inv, at[0], at[1]);
  Object[] res = @PKG@.GearUp.upgrade(inv, at[0], at[1], x.getItemId(), @PKG@.GearForge.fp(x), u, this.playerRef.getUsername());
  if (((Integer) res[0]).intValue() == 1) {
    @BD@ d = (@BD@) res[3];
    String to = ((@IS@) res[2]).getItemId();
    this.info = "+Your " + K + " is a " + @PKG@.Gear.itemName(to) + " now (" + @PKG@.GearDefs.R_NAME[@PKG@.GearData.rarity(d)] + ", Lv " + @PKG@.GearLevel.level(to, d) + ")!";
    return;
  }
  this.info = "-" + (String) res[1];
}""")
# 0.3.10 MAKE MULTITOOL ON THE TOOLS TAB: the best plain pickaxe + hatchet pair of ONE multitool tier the player carries (GearMerge.why null
# for both: not lifelong, identified, no Set / Mythic; highest tier, then the higher rarity sum). int[] { ps, pslot, hs, hslot } or null
M(lpg, r"""
public static int[] mtPair(@INV@ inv) {
  if (inv == null) return null;
  java.util.ArrayList rs = @PKG@.GearMerge.rows(inv);
  int[] best = null;
  int bs = -1;
  for (int i = 0; i < rs.size(); i++) {
    int[] a = (int[]) rs.get(i);
    @IS@ p = @PKG@.GearStamp.at(inv, a[0], a[1]);
    if (p == null || p.isEmpty() || @PKG@.GearMerge.famOf(p.getItemId()) != 1 || @PKG@.GearMerge.why(p, 1) != null) continue;
    int tp = @PKG@.GearMerge.tierOf(p.getItemId());
    @BD@ pd = @PKG@.GearMerge.inDoc(p);
    int rp = pd == null ? 0 : @PKG@.GearData.rarity(pd);
    for (int j = 0; j < rs.size(); j++) {
      int[] c = (int[]) rs.get(j);
      @IS@ h = @PKG@.GearStamp.at(inv, c[0], c[1]);
      if (h == null || h.isEmpty() || @PKG@.GearMerge.famOf(h.getItemId()) != 3 || @PKG@.GearMerge.tierOf(h.getItemId()) != tp || @PKG@.GearMerge.why(h, 3) != null) continue;
      @BD@ hd = @PKG@.GearMerge.inDoc(h);
      int sc = tp * 100 + rp + (hd == null ? 0 : @PKG@.GearData.rarity(hd));
      if (sc > bs) { bs = sc; best = new int[] { a[0], a[1], c[0], c[1] }; }
    }
  }
  return best;
}""")
M(lpg, r"""
public static String pairKey(@INV@ inv, int[] pr) {
  if (pr == null) return null;
  @IS@ p = @PKG@.GearStamp.at(inv, pr[0], pr[1]);
  @IS@ h = @PKG@.GearStamp.at(inv, pr[2], pr[3]);
  if (p == null || h == null || p.isEmpty() || h.isEmpty()) return null;
  return pr[0] + "/" + pr[1] + "/" + p.getItemId() + "/" + @PKG@.GearForge.fp(p) + "|" + pr[2] + "/" + pr[3] + "/" + h.getItemId() + "/" + @PKG@.GearForge.fp(h);
}""")
M(lpg, r"""
public void mtRow(@UCB@ b, @UEB@ ev, java.util.UUID u, @INV@ inv) {
  String tx;
  String bl = "Make multitool";
  boolean can = false;
  String gate = @PKG@.GearLL.rbGate(u);
  if (gate != null) { tx = "Multitool: " + gate; bl = "Rebirth 1"; }
  else {
    int[] pr = mtPair(inv);
    if (pr == null) tx = "Multitool: carry a pickaxe and a hatchet of the same tier (crafted, not your lifelong ones) and merge them here - they keep their rolls.";
    else {
      @IS@ p = @PKG@.GearStamp.at(inv, pr[0], pr[1]);
      @IS@ h = @PKG@.GearStamp.at(inv, pr[2], pr[3]);
      Object[] pv = @PKG@.GearMerge.preview(p, h, u);
      String why = (String) pv[0];
      String mid = (String) pv[1];
      tx = "Multitool: " + @PKG@.Gear.itemName(p.getItemId()) + " + " + @PKG@.Gear.itemName(h.getItemId()) + (mid != null ? " = " + @PKG@.Gear.itemName(mid) : "") + (why != null ? ". " + why : " (both are used up; the better rarity, both tools' lines).");
      can = why == null;
      if (can) this.mtKey = pairKey(inv, pr);
    }
  }
  b.appendInline("#SkyyGPanel", "Group #SkyyGPMtRow { Anchor: (Height: 64); LayoutMode: Left; Label #SkyyGPMt { Anchor: (Width: 392); Text: \"\"; Style: (FontSize: 14, TextColor: #ffffff(0.8), VerticalAlignment: Center, Wrap: true); } Group { Anchor: (Width: 10); } TextButton #SkyyGPMtB { Anchor: (Width: 160, Height: 44); Text: \"" + bl + "\"; " + @PKG@.GearUi.btn(can ? 0 : 3) + " } }");
  b.set("#SkyyGPMt.Text", tx);
  ev.addEventBinding(@BT@.Activating, "#SkyyGPMtB", @EVD@.of("a", "mt:" + this.tok));
}""")
# the click: the pair drawn on the page must still be the same two items (slot, id, fingerprint), then GearMerge.merge (its own checks again)
M(lpg, r"""
public void makeMt(@INV@ inv) {
  java.util.UUID u = this.playerRef.getUuid();
  if (!@PKG@.GearCfg.MULTI_ON || !@PKG@.GearMerge.loaded()) { this.info = "-Multitools are not available on this server."; return; }
  String gate = @PKG@.GearLL.rbGate(u);
  if (gate != null) { this.info = "-" + gate; return; }
  if (@PKG@.Gear.busy(u)) { this.info = "-Your profile is still loading - nothing was merged. Try again in a moment."; return; }
  int[] pr = mtPair(inv);
  String key = pairKey(inv, pr);
  String drawn = this.mtKey;
  if (pr == null) { this.info = "-Carry a pickaxe and a hatchet of the same tier first (crafted, not your lifelong ones)."; return; }
  @IS@ p = @PKG@.GearStamp.at(inv, pr[0], pr[1]);
  @IS@ h = @PKG@.GearStamp.at(inv, pr[2], pr[3]);
  Object[] pv = @PKG@.GearMerge.preview(p, h, u);          // review fix 3: a pair that cannot merge says why (skill gate, rarity off ...)
  if (pv[0] != null) { this.info = "-" + (String) pv[0]; return; }
  if (drawn == null || !drawn.equals(key)) { this.info = "-Your tools changed - check the pair on the page and click again."; return; }
  Object[] res = @PKG@.GearMerge.merge(inv, pr[0], pr[1], p.getItemId(), @PKG@.GearForge.fp(p), pr[2], pr[3], h.getItemId(), @PKG@.GearForge.fp(h), u, this.playerRef.getUsername());
  if (((Integer) res[0]).intValue() == 1) {
    @BD@ d = (@BD@) res[3];
    this.info = "+Made a " + @PKG@.GearDefs.R_NAME[@PKG@.GearData.rarity(d)] + " " + @PKG@.Gear.itemName(((@IS@) res[2]).getItemId()) + "!";
    return;
  }
  this.info = "-" + (String) res[1];
}""")
''')

# ================================================================================================================ 1B. the Tools tab clicks: token, no time guard
rep('''    long now = System.currentTimeMillis();
    if (now - this.lastClick < 400L && now >= this.lastClick) return;
    this.lastClick = now;
    if (a.startsWith("buy:")) {
      int p = -1;
      try { p = Integer.parseInt(a.substring(4)); } catch (Throwable t4) { p = -1; }
      this.armK = -1;
      this.info = @PKG@.GearLife.buy(u, this.sel, p);
      rebuild();
      return;
    }
    if (a.equals("reset")) {''', '''    long now = System.currentTimeMillis();
    // 0.3.10 ONCE PER CLICK (tools/gear_0_3_10_patch.py 1B): "buy:<perk>:<token>", "reset:<token>", "up:<token>", "mt:<token>" - honoured
    // only with this build's token, used up BEFORE anything is spent; a repeat of the same click spends nothing (the handler's wrapper
    // answers it). A click without a token (an older page) keeps the 400 ms guard. Unknown actions redraw.
    String[] pa = a.split(":");
    String cmd = pa[0];
    if (!cmd.equals("buy") && !cmd.equals("reset") && !cmd.equals("up") && !cmd.equals("mt")) { rebuild(); return; }
    int tw = cmd.equals("buy") ? 3 : 2;
    if (pa.length >= tw) {
      int ct = -1;
      try { ct = Integer.parseInt(pa[tw - 1]); } catch (Throwable t6) { ct = -1; }
      if (ct != this.tok) return;
    } else if (cmd.equals("up") || cmd.equals("mt")) { rebuild(); return; }
    else if (now - this.lastClick < 400L && now >= this.lastClick) return;
    this.tok = nextTok();
    this.lastClick = now;
    if (cmd.equals("up") || cmd.equals("mt")) {
      @PLA@ pl0 = null;
      try { pl0 = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t7) { pl0 = null; }
      @INV@ inv0 = pl0 == null ? null : pl0.getInventory();
      this.armK = -1;
      if (inv0 == null) this.info = "-Your inventory cannot be read right now - nothing changed.";
      else if (cmd.equals("up")) tierUp(inv0);
      else makeMt(inv0);
      rebuild();
      return;
    }
    if (cmd.equals("buy")) {
      int p = -1;
      try { p = pa.length > 1 ? Integer.parseInt(pa[1]) : -1; } catch (Throwable t4) { p = -1; }
      this.armK = -1;
      this.info = @PKG@.GearLife.buy(u, this.sel, p);
      rebuild();
      return;
    }
    if (cmd.equals("reset")) {''')
# review fix 1: a throw after the token was used up redraws the page (fresh token on the buttons) with a line, instead of dead buttons
rep('''  } catch (Throwable t) { @PKG@.Gear.warn("tools page click failed: " + t); }
}""")''', '''  } catch (Throwable t) {
    @PKG@.Gear.warn("tools page click failed: " + t);
    this.info = "-Something went wrong - nothing was changed. Click Refresh.";
    try { rebuild(); } catch (Throwable t9) { }
  }
}""")''')

# ================================================================================================================ 1A + 3: the wrappers (after every hook)
before('''ALL = [gu, gdf, gcf, glg, gql, gdt,''', r'''# ####################################################################################################################################
# 0.3.10 ALWAYS ANSWER (tools/gear_0_3_10_patch.py 1A): the client waits for an answer to every page click ("Loading..."), so every /smithing
# page counts what a click sent (rebuild / sendUpdate / close, counted only once the engine call returned) and a click that sent nothing gets
# ONE empty update - only while the page is still the player's open page (a click that opened another page / tab sends nothing more).
# The click handler with every hook already inserted (tab / anvil / upgrade / Requip / Tools / Identify) is copied to skyHde and wrapped.
# ####################################################################################################################################
from jpype import JClass as _JC10
_JMod = _JC10("javassist.Modifier")
_pagec = pool.get(PAGE)
for _mn, _sig in (("rebuild", "()V"), ("close", "()V"), ("sendUpdate", "(Lcom/hypixel/hytale/server/core/ui/builder/UICommandBuilder;Z)V"),
                  ("handleDataEvent", None)):
    _mm = [m for m in _pagec.getDeclaredMethods() if str(m.getName()) == _mn and (_sig is None or str(m.getSignature()) == _sig)]
    assert len(_mm) == 1 and not _JMod.isFinal(_mm[0].getModifiers()) and not _JMod.isPrivate(_mm[0].getModifiers()), "CustomUIPage.%s %s changed" % (_mn, _sig)
for _c, _m in ((PAGE, "sendUpdate"), (PAGE, "rebuild"), (PAGE, "close"), (PR, "getReference"), ("com.hypixel.hytale.component.Ref", "isValid"),
               ("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager", "getCustomPage")):
    B.probe(pool, _c, _m)
F(gui, "public static final long[] ACK = new long[2];")          # 0 clicks answered by the wrapper's empty update, 1 wrapped clicks
ANSWER_PAGES = [(rpg, "anvil page"), (mpg, "multitool page"), (spg, "smithing page"), (ipg, "identify page"), (lpg, "tools page")]
for _pg, _nm in ANSWER_PAGES:
    for _m in _pg.getDeclaredMethods():
        assert str(_m.getName()) not in ("rebuild", "close", "sendUpdate", "skyHde"), "%s already declares %s" % (_pg.getName(), _m.getName())
    F(_pg, "public int skyAns;")
    M(_pg, "public void rebuild() { super.rebuild(); this.skyAns = this.skyAns + 1; }")
    M(_pg, "public void close() { super.close(); this.skyAns = this.skyAns + 1; }")
    M(_pg, "public void sendUpdate(@UCB@ b, boolean c) { super.sendUpdate(b, c); this.skyAns = this.skyAns + 1; }")
    M(_pg, r"""
public void skyAck() {
  try {
    @REF@ r = this.playerRef.getReference();
    if (r == null || !r.isValid()) return;
    @ST@ s0 = r.getStore();
    if (s0 == null) return;
    @PLA@ p = (@PLA@) s0.getComponent(r, @PLA@.getComponentType());
    if (p == null || p.getPageManager() == null || p.getPageManager().getCustomPage() != this) return;
    sendUpdate(new @UCB@(), false);
    @PKG@.GearUi.ACK[0] = @PKG@.GearUi.ACK[0] + 1L;
  } catch (Throwable t) { }
}""")
    _h = _pg.getDeclaredMethod("handleDataEvent")
    _cp = CtNewMethod.copy(_h, "skyHde", _pg, None)
    _pg.addMethod(_cp)
    _h.setBody(J(r"""{
  int prev = this.skyAns;
  this.skyAns = 0;
  @PKG@.GearUi.ACK[1] = @PKG@.GearUi.ACK[1] + 1L;
  try { skyHde($1, $2, $3); } catch (Throwable t) { @PKG@.Gear.warn("%s click failed: " + t); }
  int got = this.skyAns;
  if (got == 0) skyAck();
  this.skyAns = prev + got;
}""" % _nm))
# 3: /multitool opens the Tools tab (on the pickaxe) while the Tools tab exists; part.lifelong off = the old Multitool page
mtc.getDeclaredMethod("execute").insertBefore(J(r"""{
  if (@PKG@.GearCfg.LL_ON && @PKG@.GearCfg.MULTI_ON && @PKG@.GearMerge.loaded()) {
    try {
      @PLA@ p0 = (@PLA@) $2.getComponent($3, @PLA@.getComponentType());
      if (p0 != null) {
        @PKG@.GearLife.sweep($4, p0.getInventory(), true);          // review fix 5: what /toolpoints does first
        @PKG@.LifePage lp0 = new @PKG@.LifePage($4);
        lp0.sel = 0;
        p0.getPageManager().openCustomPage($3, $2, lp0);
        return;
      }
    } catch (Throwable tm) { @PKG@.Gear.warn("/multitool -> Tools tab failed (the old page opens): " + tm); }
  }
}"""))
print("0.3.10 always answer: %s; /multitool opens the Tools tab while part.lifelong is on" % ", ".join(n for _p, n in ANSWER_PAGES))
''')

# ================================================================================================================ review fix 4: help texts
rep("""Tier them up on the Anvil (the pole at the Fishing Bench).""", """Tier them up with the Tier up button here or on the Anvil (the pole at the Fishing Bench).""")
rep("""   -   Tier up: Anvil tab   -   """, """   -   Tier up: the button on the right (or the Anvil)   -   """)

# ================================================================================================================ the manifest
rep('''Tools (your lifelong pickaxe, hatchet, hoe and sickle and their Upgrade Points; /toolpoints) and Multitool tabs,''',
    '''Tools (your lifelong pickaxe, hatchet, hoe and sickle: their Upgrade Points, Tier up and - after rebirth 1 - Make multitool; /toolpoints, /multitool) tabs (every click answered),''')

# ================================================================================================================ checks on the result
assert s.index("public void tierRow(") < s.index("public void panel(") and s.index("public void mtRow(") < s.index("public void panel(")
assert s.index("public void makeMt(") < s.index("public void handleDataEvent(@REF@ ref, @ST@ st, String data) {\n  try {\n    if (data == null) return;\n    String a = @PKG@.Gear.jsonStr(data, \"a\");\n    if (a.length() == 0) return;\n    if (a.startsWith(\"mode:\")) {\n      String c = a.equals(\"mode:3\")")
assert s.index('_pg.getDeclaredMethod("handleDataEvent").insertBefore(J("{ if (@PKG@.GearAnvil.idTabGo') < s.index("0.3.10 ALWAYS ANSWER (tools")
assert s.count(".insertBefore(") == OLD.count(".insertBefore(") + 1
assert s.rindex('getDeclaredMethod("handleDataEvent").insertBefore(') < s.index("_cp = CtNewMethod.copy(_h, \"skyHde\"")
assert "CtNewMethod" in s[:s.index("0.3.10 ALWAYS ANSWER (tools")]
_u = s
for _new, _old, _cnt in reversed(CHANGES):
    assert _u.count(_new) == _cnt, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old)
assert _u == OLD, "the generated script differs from 0.3.9 outside the recorded changes"
compile(s, DST, "exec")
open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(DST, ROOT), "(%d lines; 0.3.9 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
