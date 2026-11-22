"""Derive SkyyMenu/build_skyymenu_0.3.65.py + SkyyMenu/test_skyymenu_0.3.65.py from the SET pin SkyyMenu 0.3.64 (generated - never re-run
its patch). Run:  python tools/menu_0_3_65_patch.py   then   python SkyyMenu/build_skyymenu_0.3.65.py   (never --deploy)
Check: python SkyyMenu/test_skyymenu_0.3.65.py
Edit THIS patch, never the generated files. Every anchor is asserted once. Line endings kept. --out <build path> [--test-out <test path>]
writes elsewhere (the harness re-run).

0.3.65 (2026-11-22, round drop1) = DROPPING FROM THE NEW INVENTORY. Skyy's words (playing on Menu 0.3.63): "i cant drop anything from the new
inventory"; "keep building".
  ROOT CAUSE: the inventory screen's only drop path was the 0.3.50 full-page drop zone (#SkyyInvDz: a transparent one-slot ItemGrid BEHIND the
  window; the client sends Dropped only for the grid under the mouse). Since 0.3.52 (TEST 284 "a full-size window") the window is 1584 of the
  page's 1600 px wide and 906 of its 980 px high, and since 0.3.60 the top bar strip covers the top 48 px - so the zone is hidden behind the
  window everywhere except an 8 px edge left / right and a few px at the bottom; past the page's own edge there is no grid at all (the client
  calls that a cancelled drag: DragCancelled on the source grid = our "Put back"). Drag-out never reached the server (the 11-22 server log
  has no drop line, no drop-check warning - consistent: no Dropped event ever arrived). Q: a custom page gets no key events from the client
  (the vanilla inventory's Q is client-side; DropItemStack packets pass through to the game untouched since 0.3.50 - none arrived), so the
  hint row's "Q Drop" and "Drag out Drop" promised two things that never worked. (TEST 282 never saw drag-out, Q or 1-9 in the log either.)
  FIX:
  1. A DROP slot on the screen (right column, under Right now; the same 1 x 1 Skyglass slot pattern as the furnace fuel slot - activatable,
     its own Dropped + SlotClicking bindings): DRAG any item (bag, hotbar, armour, off-hand) onto it = the game's own drop (InventoryPacket-
     Handler DropItemStack: the game's PlayerRequest event, its game-mode rule (preventsItemDrops) and throwItem at your feet - so pickups /
     ownership work as vanilla) of the dragged amount (whole stack, or the half a right-drag carries). CLICK an item, then the DROP slot
     (within 10 s) = drop that whole stack (the same call). Every drop goes through the old dropOut (expected item id checked - a stale page
     drops nothing; a refused drop puts the item back; the 1.5 s repeat guard = a double event drops once).
  2. The hint row says what works: "Drop - Drag onto DROP" instead of "Q Drop" + "Drag out Drop".
  3. A drop the game itself refused (a game mode / another mod cancelling it) now SAYS so on the caption line (it was a log warning only).
  The full-page drop zone stays (harmless; the edges still count). No other tab screen shows a section-bound inventory grid (checked: only
  InvPage sets InventorySectionId), so no other screen needed this.
  NOT BUILT: Q / Ctrl+Q (the server never sees the key on a custom page - unproven KeyDown binding left out); dragging past the window edge
  (a DEVIATION from "drag outside the window drops it": the window fills the page since TEST 284 - a bigger outside zone needs a smaller window,
  Skyy's call). "1-9 To hotbar" stays in the hint row: unproven either way (shift-click already reaches the game natively on the section-bound
  grid, TEST 282), so it is an explicit in-game check, not a removal.
  FIX ROUND (critics): a click on B while A is held no longer makes B the DROP target, and DROP clicked while an item is held drops the HELD
  item (the drag's key - one drop with its Dropped); every finished move / drop / shift quick move / Sort forgets the last pick (a DROP click
  after a half drag never drops the rest); the "did not drop it" caption only when the count is exactly unchanged (a pickup is no refusal).
  No new class, command, setting, lang key, system, saved data or picture.
  ROLLBACK to 0.3.64: safe alone (nothing saved; the DROP slot just disappears).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

MOD = os.path.join(ROOT, "SkyyMenu")
P = G.Patch(os.path.join(MOD, "build_skyymenu_0.3.64.py"), os.path.join(MOD, "build_skyymenu_0.3.65.py"))
T = G.Patch(os.path.join(MOD, "test_skyymenu_0.3.64.py"), os.path.join(MOD, "test_skyymenu_0.3.65.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    T.dst = os.path.abspath(sys.argv[sys.argv.index("--test-out") + 1]) if "--test-out" in sys.argv else None
assert P.has('VERSION = "0.3.64"\n') and P.has("tools/menu_0_3_64_patch.py") and P.has("SettingsTab")
assert not P.has("SkyyInvDrop"), "not the generated SkyyMenu 0.3.64 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")

# ======================================================================= the BUILD script
P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.64: THE SETTINGS TAB = ONE SCREEN''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.65: DROPPING FROM THE NEW INVENTORY (Skyy 11-22 "i cant drop anything from the new inventory"): the full-page drop zone sat behind the
       full-size window (no Dropped ever reached us); now a DROP slot on the screen - drag an item onto it (whole / half) or click an item then
       DROP = the game's own drop; the hint row no longer promises Q / drag-out; a refused drop says so
       (notes: tools/menu_0_3_65_patch.py). CHECKED: see SkyyMenu/test_skyymenu_0.3.65.py.
0.3.64: THE SETTINGS TAB = ONE SCREEN''')
P.rep('VERSION = "0.3.64"\n', 'VERSION = "0.3.65"\n')

# ---------- (2) the hint row: only what works (Q and drag-past-the-window never reached the server)
P.rep('''IV_HINTS = [("LMB", "Drag to move"), ("RMB", "Drag half"), ("Shift", "Quick move"), ("1-9", "To hotbar"), ("Q", "Drop"),
            ("Drag out", "Drop"), ("Tab / Esc", "Close")]''',
      '''IV_HINTS = [("LMB", "Drag to move"), ("RMB", "Drag half"), ("Shift", "Quick move"), ("1-9", "To hotbar"),
            ("Drop", "Drag onto DROP"), ("Tab / Esc", "Close")]   # 0.3.65: no "Q Drop" / "Drag out Drop" (the server never saw either)
assert not [k_ for k_, _t in IV_HINTS if k_ in ("Q", "Drag out")], "0.3.65: the hint row promises no key that does not work"''')
P.rep('''    "tpNote": "Teleport to your island or the hub.",
''', '''    "tpNote": "Teleport to your island or the hub.",
    "dropHelp": "Click an item, then DROP: the whole stack.",   # 0.3.65
''')

# ---------- (1) the DROP slot: the right column's bottom panel (Right now gives up its empty bottom)
IV_DROP = '''    now_h = IV_BODY_H - sk_h - 10 - IV_DROP_H - 10   # 0.3.65: the DROP panel under Right now
'''
P.rep('''    now_h = IV_BODY_H - sk_h - 10
    nw = IV + "Now"
''', IV_DROP + '''    nw = IV + "Now"
''')
P.rep('''    ap.append(("#" + nw, G_.glass_group(IV + "NowL", riw, now_h - 24 - 26 - 8, layout="Top", anchor={"top": 8})))
''', '''    ap.append(("#" + nw, G_.glass_group(IV + "NowL", riw, now_h - 24 - 26 - 8, layout="Top", anchor={"top": 8})))
    # 0.3.65 (Skyy 11-22 "i cant drop anything from the new inventory"): THE DROP SLOT - drag an item onto it (or click an item, then it)
    # = the game's own drop. The 1 x 1 Skyglass slot pattern of the furnace fuel slot (#SkyyInvFxF): filled activatable + empty in Java.
    dp = IV + "DropP"
    ap.append(("#" + rt, G_.glass_group(dp, IV_COL_R, IV_DROP_H, role="panel", layout="Left", pad=12, anchor={"top": 10})))
    ap.append(("#" + dp, G_.glass_grid(IV + "Drop", 1, 1, drag=False, slot=IV_DROP_S, icon=IV_DROP_S - 10, anchor={"top": 4})))
    dtw = riw - IV_DROP_S - 12
    dtx = IV + "DropTx"
    ap.append(("#" + dp, G_.glass_group(dtx, dtw, IV_DROP_H - 24, layout="Top", anchor={"left": 12})))
    ap.append(("#" + dtx, lab(IV + "DropH", "DROP", 15, "accentHi", bold=True, w=dtw, h=18)))
    ap.append(("#" + dtx, lab(IV + "DropL1", "Drag an item here to drop it", 12, "text", w=dtw, h=16)))
    ap.append(("#" + dtx, lab(IV + "DropL2", "Right-drag drops half a stack", 12, "dim", w=dtw, h=16)))
    ap.append(("#" + dtx, lab(IV + "DropN", "", 12, "dim", w=dtw, h=16)))
    ap.sets.append((IV + "DropN", "Text", IV_TXT["dropHelp"]))
    for _t in ("Drag an item here to drop it", "Right-drag drops half a stack", IV_TXT["dropHelp"]):
        assert SUI.text_width(_t, 12) <= dtw - 4, ("0.3.65: a DROP line fits", _t)
    assert 24 + 26 + 8 + IV_NOWN * 44 <= now_h and IV_DROP_S + 4 <= IV_DROP_H - 24 and 18 + 3 * 16 <= IV_DROP_H - 24, "0.3.65: Right now + DROP fit"
    assert sk_h + 10 + now_h + 10 + IV_DROP_H == IV_BODY_H, "0.3.65: the right column still sums to the body"
''')
P.rep('''IV_TPS, IV_TPI = 40, 32
''', '''IV_TPS, IV_TPI = 40, 32
IV_DROP_H, IV_DROP_S = 90, 58   # 0.3.65: the DROP panel (12 px padding) and its slot
''')
P.rep('''           "MntI", "MntN", "MntL", "NowL", "Tp") + tuple("Nq%d" % k_ for k_ in range(IV_NMAX)) + tuple("Sk%d" % k_ for k_ in range(IV_SKN)):   # skills, now, teleports
    assert IV + _g in _iv_ids, "0.3.50: the page has #" + IV + _g
''', '''           "MntI", "MntN", "MntL", "NowL", "Tp") + tuple("Nq%d" % k_ for k_ in range(IV_NMAX)) + tuple("Sk%d" % k_ for k_ in range(IV_SKN)):   # skills, now, teleports
    assert IV + _g in _iv_ids, "0.3.50: the page has #" + IV + _g
assert IV + "Drop" in _iv_shell_ids and IV + "DropN" in _iv_shell_ids, "0.3.65: the shell has the DROP slot (every inventory mode)"
''')

# ---------- (1) Java: the DROP slot is filled (one empty activatable slot) and bound - drag onto it = 'dz' (the old drop path), click = 'dzc'
P.rep('''  ev.addEventBinding(@BT@.Dropped, "#SkyyInvDz", @EVD@.of("a", "dz"), false);
''', '''  ev.addEventBinding(@BT@.Dropped, "#SkyyInvDz", @EVD@.of("a", "dz"), false);
  b.set("#SkyyInvDrop.Slots", dropSlot());   // 0.3.65: the DROP slot (drag onto it = drop; click an item, then it = drop the stack)
  ev.addEventBinding(@BT@.Dropped, "#SkyyInvDrop", @EVD@.of("a", "dz"), false);
  ev.addEventBinding(@BT@.SlotClicking, "#SkyyInvDrop", @EVD@.of("a", "dzc"), false);
''')
# the last item clicked (for click-then-DROP): a click on a non-empty bag / hotbar / armour / off-hand slot while NOTHING is held (fix drop1
# critic: a click on B while A is held never makes B the item DROP drops), kept 10 s; any finished move / drop / quick move / sort forgets it
# (fix: a later DROP click never drops the rest of a stack that was just half-dragged / moved)
P.rep('''      if (s != null && !s.isEmpty() && this.dg == null) { this.dg = g; this.ds = si; this.di = s.getItemId(); this.dshift = bval(d, "ShiftHeld"); }
''', '''      if (s != null && !s.isEmpty() && this.dg == null) { this.dg = g; this.ds = si; this.di = s.getItemId(); this.dshift = bval(d, "ShiftHeld");
        this.lpg = g; this.lps = si; this.lpi = this.di; this.lpt = System.currentTimeMillis(); }   // 0.3.65: the last pick (click-then-DROP)
''')
P.rep('''  int cslot = ival(d, "SourceSlotId", -1);
  String sg = this.dg;
''', '''  int cslot = ival(d, "SourceSlotId", -1);
  this.lpg = null;   // 0.3.65: a move / drop done = the last pick is used up (a later DROP click drops nothing)
  String sg = this.dg;
''')
P.rep('''if (sh) { moved("shift " + g + ":" + si); answer("Quick moved"); return; }''',
      '''if (sh) { this.lpg = null; moved("shift " + g + ":" + si); answer("Quick moved"); return; }   /* 0.3.65: forgets the last pick */''')
P.rep('''if (a.equals("sort")) { clearDrag(); answer(sort()); return; }''',
      '''if (a.equals("sort")) { clearDrag(); this.lpg = null; answer(sort()); return; }''')
# DROP clicked while an item is HELD (a drag the client did not finish) = the held item (doMove: the same key as its Dropped, so one drop);
# else the last pick
P.rep('''    if (a.equals("dz")) { answer(doMove(d, g, si, true)); return; }
''', '''    if (a.equals("dz")) { answerDrop(doMove(d, g, si, true)); return; }   // 0.3.65: + the DROP slot re-sent empty
    if (a.equals("dzc")) { answerDrop(this.dg != null ? doMove(d, g, si, true) : dropClick()); return; }   // 0.3.65: held item, or click an item then DROP
''')
# a drop the game refused: said on the caption line too (inline - say() comes later in the class)
P.rep('''  if (n1 >= n0) { this.fails = this.fails + 1; @PKG@.MenuUtil.warn("inventory drop-check: the game's own drop did not drop " + sid + " for " + this.playerRef.getUsername() + " (nothing lost)"); }
''', '''  if (n1 >= n0) { this.fails = this.fails + 1; @PKG@.MenuUtil.warn("inventory drop-check: the game's own drop did not drop " + sid + " for " + this.playerRef.getUsername() + " (nothing lost)"); }
  if (n1 == n0 && !this.closed) {   // 0.3.65: and the player sees it (exactly unchanged only: a pickup of the same item meanwhile is no refusal)
    try {
      @UCB@ ub = new @UCB@();
      this.tcap = "The game did not drop it here - it is still in your inventory";
      ub.set("#SkyyInvCap.Text", this.tcap);
      this.sendUpdate(ub);
    } catch (Throwable t) { }
  }
''')
P.rep('''# a native Move / SmartMove packet the client sent a moment ago (InvState.route keeps its time): the game already moved the item''', '''# ---- 0.3.65: the DROP slot (Skyy 11-22 "i cant drop anything from the new inventory"): one empty activatable slot; a click on it drops the
# item clicked last (within 10 s) through the SAME dropOut as a drag (expected id checked, refused = put back, the 1.5 s repeat guard)
F(ipg, "public String lpg;")
F(ipg, "public int lps;")
F(ipg, "public String lpi;")
F(ipg, "public long lpt;")
F(ipg, "public static volatile int DROPCLICKS = 0;")
M(ipg, r"""
public static java.util.ArrayList dropSlot() {
  java.util.ArrayList l = new java.util.ArrayList();
  l.add(new @IGS@());
  return act(l);
}""")
M(ipg, r"""
public String dropClick() {
  String g = this.lpg;
  int s = this.lps;
  String id = this.lpi;
  long age = System.currentTimeMillis() - this.lpt;
  this.lpg = null;
  if (g == null || age < 0L || age > 10000L) { clearDrag(); return "Drag an item onto DROP - or click an item, then DROP"; }
  String key = g + ":" + s + ">world";
  if (dup(key)) { clearDrag(); return "Done"; }
  DROPCLICKS = DROPCLICKS + 1;
  String r = dropOut(g, s, -1, id, this.pref, this.pst);
  moved(key);
  clearDrag();
  return r;
}""")
M(ipg, r"""
public void answerDrop(String cap) {
  @UCB@ ub = new @UCB@();
  putAll(ub);
  ub.set("#SkyyInvDrop.Slots", dropSlot());
  this.tcap = cap == null ? "" : cap;
  ub.set("#SkyyInvCap.Text", this.tcap);
  this.answered = true;
  this.answers = this.answers + 1;
  this.sendUpdate(ub);
}""")
# a native Move / SmartMove packet the client sent a moment ago (InvState.route keeps its time): the game already moved the item''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.3.65: no new system / command"
_i = P.s.index
assert _i("public String dropOut(String sg") < _i("public String dropClick()") < _i('if (a.equals("dzc")) { answerDrop(this.dg != null ? doMove(')
assert _i("public String doMove(String d") < _i('if (a.equals("dzc")) { answerDrop(this.dg != null ? doMove(')
assert _i("public void putAll(@UCB@ b)") < _i("public void answerDrop(String cap)") < _i('if (a.equals("dz")) { answerDrop(')
assert _i("public static java.util.ArrayList act(java.util.ArrayList l)") < _i("public static java.util.ArrayList dropSlot()") < _i('b.set("#SkyyInvDrop.Slots", dropSlot());')
assert _i("public boolean dup(String key)") < _i("public String dropClick()") and _i("public void clearDrag()") < _i("public String dropClick()")
assert _i('F(ipg, "public long lpt;")') < _i("this.lpt = System.currentTimeMillis(); }   // 0.3.65")
P.finish()


# ======================================================================= the HARNESS (derived from the 0.3.64 harness: every 0.3.64 check
# runs again on the 0.3.65 jar - the page has 2 more bindings (the DROP slot) -, plus DROP1)
def cut(t, start, end):
    i = t.index(start)
    j = t.index(end, i)
    return t[i:j]


T.rep('''"""Harness for SkyyMenu 0.3.64 (the Settings tab = one screen; tools/menu_0_3_64_patch.py, round tab6).
GENERATED by tools/menu_0_3_64_patch.py from the 0.3.63 harness (edit the patch, not this file): every 0.3.63 check runs again on the
0.3.64 jar''', '''"""Harness for SkyyMenu 0.3.65 (dropping from the new inventory; tools/menu_0_3_65_patch.py, round drop1).
GENERATED by tools/menu_0_3_65_patch.py from the 0.3.64 harness (edit the patch, not this file): every 0.3.64 check runs again on the
0.3.65 jar (the inventory page has 2 more bindings: the DROP slot), plus
  DROP1 (EXECUTED on the stand-in player with the harness dropper, then the game's own InventoryPacketHandler stand-in):
       PAGE    the DROP slot: one empty activatable slot, Dropped + SlotClicking bound; the old drop zone still bound; the hint row has no
               "Q" / "Drag out"; the answer to a drop re-sends the DROP slot empty
       DRAG    onto DROP: a full bag stack, half a stack (the dragged amount), a hotbar stack; (INV6 player) an armour piece, an off-hand
               item = dropped
       CLICK   click an item, then DROP = its whole stack; DROP with nothing clicked / clicked over 10 s ago = said, nothing dropped;
               the slot changed since the click = nothing dropped
       SAFE    a refused drop keeps the item; a stale page (another item in the slot) drops nothing; the same drag twice / the same click
               twice = ONE drop; a drop the game refused is said on the caption line
The 0.3.64 harness text follows:
Harness for SkyyMenu 0.3.64 (the Settings tab = one screen; tools/menu_0_3_64_patch.py, round tab6).
GENERATED by tools/menu_0_3_64_patch.py from the 0.3.63 harness (edit the patch, not this file): every 0.3.63 check runs again on the
0.3.64 jar''')
T.rep('VERSION = "0.3.64"\nJAR', 'VERSION = "0.3.65"\nJAR')
T.rep('OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.63.jar")', 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.64.jar")')
T.rep('GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.63.py")', 'GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.64.py")')
T.rep('PATCH = os.path.join(ROOT, "tools", "menu_0_3_64_patch.py")', 'PATCH = os.path.join(ROOT, "tools", "menu_0_3_65_patch.py")')
T.rep('"scratch", "tab6", "menu"', '"scratch", "drop1", "menu"')
T.rep('ADDED = ["SettingsTabData", "SettingsTab"]   # 0.3.64: the settings screen\n', 'ADDED = []   # 0.3.65: no new class\n')
T.rep(cut(T.s, 'EXPECT = {   # 0.3.64:', 'if "--expect-dump" in sys.argv:'), '''EXPECT = {   # 0.3.65: the DROP slot (InvPage), the hint row + DROP panel markup (InvData), the version text
    "InvPage": ["+f DROPCLICKS", "+f lpg", "+f lpi", "+f lps", "+f lpt", "+m answerDrop", "+m dropClick", "+m dropSlot", "~<clinit>",
                "~m build", "~m doMove", "~m dropCheck", "~m handleDataEvent"],
    "InvData": ["~<clinit>"],
    "SkyyMenuPlugin": ["~m setup"],                      # the version text
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "OpsPage": ["~<clinit>"], "MenuData": ["~<clinit>"],   # the version string + the Mods list
}
''')
T.rep('''    K.check(g.count('VERSION = "0.3.64"') == 1, "S VERSION")''', '''    K.check(g.count('VERSION = "0.3.65"') == 1, "S VERSION")
    # 0.3.65: the hint row promises no key that does not work; the DROP slot is in the shell and the right column still fits
    K.check('("Drop", "Drag onto DROP")' in g and '("Q", "Drop")' not in g and '("Drag out", "Drop")' not in g
            and "0.3.65: the hint row promises no key that does not work" in g and "0.3.65: the right column still sums to the body" in g
            and "0.3.65: the shell has the DROP slot (every inventory mode)" in g,
            "DROP1 STATIC the hint row has no Q / Drag out; the build asserts the DROP slot is in the shell and the right column fits")''')
T.rep('''    K.eq(len(bl), 7 + 8 + 7 + 4 * 4 + 1 + 5 + 2 + 1 + 2 + 12 + 12 - 1, "PAGE: 72 bindings (0.3.60:''',
      '''    K.eq(len(bl), 7 + 8 + 7 + 4 * 4 + 1 + 5 + 2 + 1 + 2 + 12 + 12 - 1 + 2, "PAGE: 74 bindings (0.3.65: + the DROP slot's Dropped + SlotClicking; 0.3.60:''')

HARNESS_DROP1 = r'''    # ---- DROP1 (0.3.65; Skyy 11-22 "i cant drop anything from the new inventory"): THE DROP SLOT
    bl1_ = [(b_[0], b_[1], b_[2]) for b_ in (binds_of(pk[0]) if pk else [])]
    K.check(("Dropped", "#SkyyInvDrop") in [(b_[0], b_[1]) for b_ in bl1_] and ("SlotClicking", "#SkyyInvDrop") in [(b_[0], b_[1]) for b_ in bl1_]
            and ("Dropped", "#SkyyInvDz") in [(b_[0], b_[1]) for b_ in bl1_]
            and [b_[2] for b_ in bl1_ if b_[:2] == ("Dropped", "#SkyyInvDrop")][0].find('"dz"') >= 0
            and [b_[2] for b_ in bl1_ if b_[:2] == ("SlotClicking", "#SkyyInvDrop")][0].find('"dzc"') >= 0,
            "DROP1 PAGE the DROP slot is bound: Dropped = dz (the drop path), SlotClicking = dzc; the old drop zone still bound")
    ds1_ = json.loads(cm.get("#SkyyInvDrop.Slots", "{}")).get("0", []) if pk else []
    K.check(len(ds1_) == 1 and not [i_ for i_ in IDS if i_ in json.dumps(ds1_[0])],
            "DROP1 PAGE the DROP slot = ONE empty slot (%s)" % (json.dumps(ds1_)[:200]))
    K.check('Text: "Q"' not in txt and 'Text: "Drag out"' not in txt and "Drag onto DROP" in txt and "#SkyyInvDrop " in txt and 'Text: "DROP"' in txt,
            "DROP1 PAGE the hint row: no Q, no Drag out; 'Drop - Drag onto DROP'; the DROP panel is drawn")
    ST.DROPPER = Dropper(True)

    def free1(f_, n_):
        return [i_ for i_ in range(n_) if at(PI, f_, i_) is None][0]

    def dz1(sec_, slot_, iid_, q_, what_):
        return one(ev(PI, {"a": "dz", "SlotIndex": 0, "SourceInventorySectionId": sec_, "SourceSlotId": slot_, "ItemStackId": iid_, "ItemStackQuantity": q_}), what_)
    # DRAG a full bag stack onto DROP
    s1_ = free1("storage", 36)
    put(PI, "storage", s1_, ISc("Rock_Stone", 20))
    n1_ = E.count(PI, "Rock_Stone")
    del DROPS[:]
    pg.lastMoveAt = 0
    p_ = dz1(-2, s1_, "Rock_Stone", 20, "DROP1 DRAG a full stack")
    K.check(DROPS == [("Rock_Stone", 20)] and at(PI, "storage", s1_) is None and E.count(PI, "Rock_Stone") == n1_ - 20 and cap_of(p_) == "Dropped"
            and "#SkyyInvDrop.Slots" in cmap(p_) and "#SkyyInvIs.Slots" in cmap(p_),
            "DROP1 DRAG a full bag stack onto DROP = 20 dropped at the feet, the slot empty, ONE answer re-sends the grids + the DROP slot (%s %s)" % (DROPS, cap_of(p_)))
    # half a stack (a right-drag carries half)
    put(PI, "storage", s1_, ISc("Rock_Stone", 20))
    del DROPS[:]
    pg.lastMoveAt = 0
    p_ = dz1(-2, s1_, "Rock_Stone", 10, "DROP1 DRAG half a stack")
    K.check(DROPS == [("Rock_Stone", 10)] and at(PI, "storage", s1_) == ("Rock_Stone", 10), "DROP1 DRAG half a stack = 10 dropped, 10 stay (%s %s)" % (DROPS, at(PI, "storage", s1_)))
    # the same drag event twice = ONE drop
    del DROPS[:]
    p_ = dz1(-2, s1_, "Rock_Stone", 10, "DROP1 SAFE the same drag again")
    K.check(DROPS == [] and at(PI, "storage", s1_) == ("Rock_Stone", 10), "DROP1 SAFE the same drag event twice = ONE drop (%s)" % cap_of(p_))
    inv(PI, "storage").removeItemStackFromSlot(JShort(s1_))
    # the hotbar
    h1_ = free1("hotbar", 9)
    put(PI, "hotbar", h1_, ISc("Plant_Fruit_Apple", 3))
    del DROPS[:]
    pg.lastMoveAt = 0
    p_ = dz1(-1, h1_, "Plant_Fruit_Apple", 3, "DROP1 DRAG a hotbar stack")
    K.check(DROPS == [("Plant_Fruit_Apple", 3)] and at(PI, "hotbar", h1_) is None, "DROP1 DRAG a hotbar stack onto DROP = dropped (%s)" % DROPS)
    # a stale page: the slot holds another item now = nothing dropped
    put(PI, "storage", s1_, ISc("Wood_Oak_Trunk", 4))
    del DROPS[:]
    pg.lastMoveAt = 0
    p_ = dz1(-2, s1_, "Rock_Stone", 4, "DROP1 SAFE a stale drag")
    K.check(DROPS == [] and at(PI, "storage", s1_) == ("Wood_Oak_Trunk", 4) and "slot changed" in cap_of(p_), "DROP1 SAFE a stale page (another item in the slot) = nothing dropped (%s)" % cap_of(p_))
    # refused = the item stays
    ST.DROPPER = Dropper(False)
    tt1_ = totals(PI)
    pg.lastMoveAt = 0
    p_ = dz1(-2, s1_, "Wood_Oak_Trunk", 4, "DROP1 SAFE a refused drop")
    K.check(totals(PI) == tt1_ and at(PI, "storage", s1_) == ("Wood_Oak_Trunk", 4) and "back in your inventory" in cap_of(p_),
            "DROP1 SAFE a refused drop keeps the item in its slot, nothing lost (%s)" % cap_of(p_))
    ST.DROPPER = Dropper(True)
    # CLICK an item, then DROP = its whole stack (a real click = SlotClicking + the release on the same slot = "Put back")
    def pick1(sl_, what_, sh_=False):
        one(ev(PI, {"a": "sc", "g": "s", "SlotIndex": sl_, "ShiftHeld": sh_}), what_ + " (press)")
        return one(ev(PI, {"a": "rl", "g": "s", "SlotIndex": sl_, "ShiftHeld": sh_}), what_ + " (release)")
    del DROPS[:]
    pg.lastMoveAt = 0
    c0_ = int(PG.DROPCLICKS)
    pick1(s1_, "DROP1 CLICK pick")
    K.check(pg.dg is None and str(pg.lpi) == "Wood_Oak_Trunk", "DROP1 CLICK a click = nothing held, the last pick kept (%s %s)" % (pg.dg, pg.lpi))
    p_ = one(ev(PI, {"a": "dzc", "SlotIndex": 0}), "DROP1 CLICK DROP")
    K.check(DROPS == [("Wood_Oak_Trunk", 4)] and at(PI, "storage", s1_) is None and cap_of(p_) == "Dropped" and int(PG.DROPCLICKS) == c0_ + 1
            and "#SkyyInvDrop.Slots" in cmap(p_), "DROP1 CLICK an item, then DROP = its whole stack dropped (%s %s)" % (DROPS, cap_of(p_)))
    p_ = one(ev(PI, {"a": "dzc", "SlotIndex": 0}), "DROP1 CLICK DROP again")
    K.check(DROPS == [("Wood_Oak_Trunk", 4)] and "click an item" in cap_of(p_), "DROP1 SAFE DROP clicked twice = ONE drop, then the hint (%s)" % cap_of(p_))
    # nothing clicked / clicked too long ago / the slot changed since the click
    put(PI, "storage", s1_, ISc("Rock_Stone", 6))
    del DROPS[:]
    pick1(s1_, "DROP1 CLICK pick (old)")
    pg.lpt = pg.lpt - 11000
    pg.lastMoveAt = 0
    p_ = one(ev(PI, {"a": "dzc", "SlotIndex": 0}), "DROP1 CLICK DROP after 11 s")
    K.check(DROPS == [] and at(PI, "storage", s1_) == ("Rock_Stone", 6) and "click an item" in cap_of(p_), "DROP1 SAFE a click over 10 s old = nothing dropped, said (%s)" % cap_of(p_))
    pick1(s1_, "DROP1 CLICK pick (then changed)")
    inv(PI, "storage").removeItemStackFromSlot(JShort(s1_))
    put(PI, "storage", s1_, ISc("Wood_Oak_Trunk", 2))
    pg.lastMoveAt = 0
    p_ = one(ev(PI, {"a": "dzc", "SlotIndex": 0}), "DROP1 CLICK DROP after the slot changed")
    K.check(DROPS == [] and at(PI, "storage", s1_) == ("Wood_Oak_Trunk", 2) and "slot changed" in cap_of(p_), "DROP1 SAFE the slot changed since the click = nothing dropped (%s)" % cap_of(p_))
    inv(PI, "storage").removeItemStackFromSlot(JShort(s1_))
    # FIX1 (critic): A held (pressed, not released), then B clicked: DROP drops A (the held item), never B
    s2_ = [i_ for i_ in range(36) if i_ != s1_ and at(PI, "storage", i_) is None][0]
    put(PI, "storage", s1_, ISc("Rock_Stone", 7))
    put(PI, "storage", s2_, ISc("Wood_Oak_Trunk", 5))
    del DROPS[:]
    pg.lastMoveAt = 0
    pg.clearDrag()
    pg.lpg = None
    c1_ = int(PG.DROPCLICKS)
    one(ev(PI, {"a": "sc", "g": "s", "SlotIndex": s1_}), "DROP1 FIX1 hold A")
    one(ev(PI, {"a": "sc", "g": "s", "SlotIndex": s2_}), "DROP1 FIX1 click B while A is held")
    K.check(str(pg.lpi) == "Rock_Stone" and int(pg.lps) == s1_, "DROP1 FIX1 a click on B while A is held does not make B the last pick (%s %s)" % (pg.lpi, pg.lps))
    p_ = one(ev(PI, {"a": "dzc", "SlotIndex": 0}), "DROP1 FIX1 DROP while A is held")
    K.check(DROPS == [("Rock_Stone", 7)] and at(PI, "storage", s1_) is None and at(PI, "storage", s2_) == ("Wood_Oak_Trunk", 5) and cap_of(p_) == "Dropped"
            and pg.dg is None and pg.lpg is None and int(PG.DROPCLICKS) == c1_,
            "DROP1 FIX1 DROP while A is held = A (the held item) dropped, B untouched (%s %s %s)" % (DROPS, at(PI, "storage", s2_), cap_of(p_)))
    # FIX1b: the held item's Dropped right after that DROP click = the same key = ONE drop
    put(PI, "storage", s1_, ISc("Rock_Stone", 7))
    del DROPS[:]
    p_ = dz1(-2, s1_, "Rock_Stone", 7, "DROP1 FIX1 the Dropped after the click")
    K.check(DROPS == [] and at(PI, "storage", s1_) == ("Rock_Stone", 7), "DROP1 FIX1 a DROP click + the drag's Dropped = ONE drop (%s %s)" % (DROPS, cap_of(p_)))
    # FIX2 (critic): half a stack dragged onto DROP, then (after the repeat guard) DROP clicked = nothing more dropped
    inv(PI, "storage").removeItemStackFromSlot(JShort(s2_))
    inv(PI, "storage").removeItemStackFromSlot(JShort(s1_))
    put(PI, "storage", s1_, ISc("Rock_Stone", 20))
    del DROPS[:]
    pg.lastMoveAt = 0
    pg.clearDrag()
    one(ev(PI, {"a": "sc", "g": "s", "SlotIndex": s1_}), "DROP1 FIX2 press (drag start)")
    p_ = dz1(-2, s1_, "Rock_Stone", 10, "DROP1 FIX2 half dragged onto DROP")
    K.check(DROPS == [("Rock_Stone", 10)] and at(PI, "storage", s1_) == ("Rock_Stone", 10) and pg.lpg is None,
            "DROP1 FIX2 a drag onto DROP uses up the last pick (%s %s)" % (DROPS, pg.lpg))
    pg.lastMoveAt = 0
    p_ = one(ev(PI, {"a": "dzc", "SlotIndex": 0}), "DROP1 FIX2 DROP clicked after the half drag")
    K.check(DROPS == [("Rock_Stone", 10)] and at(PI, "storage", s1_) == ("Rock_Stone", 10) and "click an item" in cap_of(p_),
            "DROP1 FIX2 DROP clicked after a half drag = the rest stays, the hint (%s %s)" % (DROPS, cap_of(p_)))
    # FIX2b: a shift quick move / a move to another slot also use up the last pick
    del DROPS[:]
    pick1(s1_, "DROP1 FIX2 click before the quick move", True)
    K.check(pg.lpg is None, "DROP1 FIX2 a shift quick move uses up the last pick (%s)" % pg.lpg)
    pg.lastMoveAt = 0
    p_ = one(ev(PI, {"a": "dzc", "SlotIndex": 0}), "DROP1 FIX2 DROP after a quick move")
    K.check(DROPS == [] and at(PI, "storage", s1_) == ("Rock_Stone", 10), "DROP1 FIX2 DROP after a shift quick move = nothing dropped (%s)" % cap_of(p_))
    pick1(s1_, "DROP1 FIX2 click before a move")
    K.check(pg.lpg is not None, "DROP1 FIX2 a plain click keeps the last pick")
    s3_ = [i_ for i_ in range(36) if i_ != s1_ and at(PI, "storage", i_) is None][0]
    pg.lastMoveAt = 0
    one(ev(PI, {"a": "dr", "g": "s", "SlotIndex": s3_, "SourceInventorySectionId": -2, "SourceSlotId": s1_, "ItemStackId": "Rock_Stone", "ItemStackQuantity": 10}), "DROP1 FIX2 a move")
    K.check(pg.lpg is None, "DROP1 FIX2 a move to another slot uses up the last pick (%s)" % pg.lpg)
    pg.lastMoveAt = 0
    p_ = one(ev(PI, {"a": "dzc", "SlotIndex": 0}), "DROP1 FIX2 DROP after a move")
    K.check(DROPS == [] and "click an item" in cap_of(p_), "DROP1 FIX2 DROP after a move = nothing dropped (%s %s)" % (DROPS, cap_of(p_)))
    for i_ in (s1_, s3_):
        if at(PI, "storage", i_) is not None:
            inv(PI, "storage").removeItemStackFromSlot(JShort(i_))
    # FIX3 (critic): the drop check shows its caption only when the count is exactly unchanged (a pickup meanwhile is no refusal)
    put(PI, "storage", s1_, ISc("Rock_Stone", 5))
    pg.tcap = "x"
    f3_ = int(pg.fails)
    pg.dropCheck("Rock_Stone", E.count(PI, "Rock_Stone") - 1)
    K.check(int(pg.fails) == f3_ + 1 and str(pg.tcap) == "x", "DROP1 FIX3 a drop check with MORE of the item now = logged, no 'did not drop' caption (%s)" % pg.tcap)
    pg.dropCheck("Rock_Stone", E.count(PI, "Rock_Stone"))
    K.check(int(pg.fails) == f3_ + 2 and "did not drop it" in str(pg.tcap), "DROP1 FIX3 exactly unchanged = the caption (%s)" % pg.tcap)
    inv(PI, "storage").removeItemStackFromSlot(JShort(s1_))
    pg.lastMoveAt = 0
    ST.DROPPER = None
    pg.clearDrag()
    pg.lpg = None
    E.pump(PI)
'''
T.rep('''    K.check(int(pg.fails) == f1_ + 1, "DROP CHECK: a drop the game did not do counts as a fail (nothing lost)")
''', '''    K.check(int(pg.fails) == f1_ + 1, "DROP CHECK: a drop the game did not do counts as a fail (nothing lost)")
    K.check("did not drop it" in str(pg.tcap), "DROP1 SAFE (0.3.65) a drop the game refused is said on the caption line (%s)" % pg.tcap)
''')
T.rep('''    E.jf(PRc.class_, "packetHandler").set(PI.pr, old_ph)
    T0 = totals(PI)
''', '''    E.jf(PRc.class_, "packetHandler").set(PI.pr, old_ph)
''' + HARNESS_DROP1 + '''    T0 = totals(PI)
''')

HARNESS_DROP1A = r"""    # ---- DROP1 (0.3.65): armour (PA) + off-hand (PB, a usable off-hand item) onto the DROP slot - each piece put back after (later checks)
    ST.DROPPER = Dropper(True)
    ah_ = at(PA, "armor", 0)
    del DROPS[:]
    pgA.lastMoveAt = 0
    p_ = one(ev(PA, {"a": "dz", "SlotIndex": 0, "SourceInventorySectionId": -3, "SourceSlotId": 0, "ItemStackId": ah_[0] if ah_ else "", "ItemStackQuantity": 1}), "DROP1 DRAG an armour piece")
    K.check(ah_ is not None and DROPS == [(ah_[0], 1)] and at(PA, "armor", 0) is None and cap_of(p_) == "Dropped",
            "DROP1 DRAG an armour piece onto DROP = dropped, the armour slot empty (%s %s %s)" % (ah_, DROPS, cap_of(p_)))
    if ah_ is not None and at(PA, "armor", 0) is None:
        put(PA, "armor", 0, ISc(ah_[0], ah_[1]))
    pgA.lastMoveAt = 0
    E.jf(ITc.class_, "utility").set(amap.get("Plant_Fruit_Apple"), UU_)
    uh_ = at(PB, "utility", 0)
    if uh_ is None:
        put(PB, "utility", 0, ISc("Plant_Fruit_Apple", 3))
        uh_ = at(PB, "utility", 0)
    del DROPS[:]
    pgB.lastMoveAt = 0
    p_ = one(ev(PB, {"a": "dz", "SlotIndex": 0, "SourceInventorySectionId": -5, "SourceSlotId": 0, "ItemStackId": uh_[0] if uh_ else "", "ItemStackQuantity": uh_[1] if uh_ else 1}), "DROP1 DRAG an off-hand item")
    K.check(uh_ is not None and DROPS == [uh_] and at(PB, "utility", 0) is None and cap_of(p_) == "Dropped",
            "DROP1 DRAG an off-hand item onto DROP = dropped, the off-hand slot empty (%s %s %s)" % (uh_, DROPS, cap_of(p_)))
    if uh_ is not None and at(PB, "utility", 0) is None:
        put(PB, "utility", 0, ISc(uh_[0], uh_[1]))
    E.jf(ITc.class_, "utility").set(amap.get("Plant_Fruit_Apple"), IUc.DEFAULT)
    ST.DROPPER = None
    pgB.lastMoveAt = 0
    E.pump(PA)
    E.pump(PB)
"""
T.rep("""    pgB.shut()
    E.pump(PB)
""", HARNESS_DROP1A + """    pgB.shut()
    E.pump(PB)
""")
if T.dst:
    T.finish()
