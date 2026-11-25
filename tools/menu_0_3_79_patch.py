"""Derive SkyyMenu/build_skyymenu_0.3.79.py + SkyyMenu/test_skyymenu_0.3.79.py from the SET pin SkyyMenu 0.3.78 (generated - never re-run
its patch). Run:  python tools/menu_0_3_79_patch.py   then   python SkyyMenu/build_skyymenu_0.3.79.py   (never --deploy)
Check: python SkyyMenu/test_skyymenu_0.3.79.py
Edit THIS patch, never the generated files. Every anchor is asserted once. Line endings kept. --out <build path> [--test-out <test path>]
writes elsewhere (the harness re-run). Pairs with SkyyBank 0.1.19 (tools/bank_0_1_19_patch.py: /bank + the Storage > Bank tab call
menu:fn:bankview); either deploys alone (no caller = the keys sit unused; no keys = SkyyBank opens its old page).

0.3.79 (2026-11-24, round bankroute) = /bank AND SkyyBank's STORAGE > BANK TAB OPEN THE NEW SCREEN'S BANK VIEW WHILE THE OLD MENU IS OFF.
Skyy's words (docs/answered/ui.md 2026-11-22, LOCKED 'RETIRE THE OLD MENU'): "when everything is in the new system id like to disable the old
menu compleatly, so instead of adding things like the full tree button, just build it all into the new system and remove the old "Full tree"";
2026-11-24 "keep building". 0.3.76 left SkyyBank's own doors (the /bank command, its Storage > Bank hub tab = BankHubOpen) on the old bank page:
SkyyMenu's MenuHub.page cannot route a tab another mod owns (0.3.76 OLD8 FIX). So SkyyMenu now offers two bridge Functions SkyyBank calls:
  menu:fn:bankview  apply(java.util.UUID | String uuid) -> String: opens the Market screen on its Bank view (view 4, the 0.3.76 Bank view - ONE
      page packet, the same MarketTab as the bank card's Bank button) for that player. '+The Bank opened in the SkyWynn screen.' = opened;
      '-<reason>' = nothing opened, the caller opens its old page: the old SkyWynn menu is on (Server Setup menu.oldMenu - the old menu stays
      whole while it is on, the same rule as 0.3.75's World > Teleport route); SkyyBank has no bank:fn:view / bank:fn:act (older than 0.1.18);
      no Market screen (SkyyBazaar's bazaar:fn:tab / tabact missing - the MarketTab.open rule); an unknown / offline player; no world / Player
      component / page manager; the page could not open (a [SkyyMenu] WARN). Never throws, never null. The caller runs on the player's world
      thread (the /bank command / a page event, HUBS-CONTRACT 1 - as MenuHubOpen; SkyyMenu does not hop threads here).
  menu:fn:oldmenu   apply(anything) -> java.lang.Boolean: TRUE while the old SkyWynn menu is on (MenuCfg.OLD_MENU, live with Server Setup).
  ONE new class MenuBankFn (the two Functions: op 1 bankview, op 2 oldmenu) put in setup() and removed at shutdown (only OUR objects).
No command / system / picture / lang key / setting / saved data; the Bank view itself is 0.3.76's, unchanged.
ROLLBACK to 0.3.78: safe alone (nothing saved; SkyyBank 0.1.19 then finds no key and opens its old page). SkyyBank 0.1.19 rolls back alone.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

MOD = os.path.join(ROOT, "SkyyMenu")
P = G.Patch(os.path.join(MOD, "build_skyymenu_0.3.78.py"), os.path.join(MOD, "build_skyymenu_0.3.79.py"))
T = G.Patch(os.path.join(MOD, "test_skyymenu_0.3.78.py"), os.path.join(MOD, "test_skyymenu_0.3.79.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    T.dst = os.path.abspath(sys.argv[sys.argv.index("--test-out") + 1]) if "--test-out" in sys.argv else None
assert P.has('VERSION = "0.3.78"\n') and P.has("sacks:fn:upView") and not P.has("menu:fn:bankview"), "not the generated SkyyMenu 0.3.78 script"
SYS0, CMD0, MK0 = P.s.count("registerSystem("), P.s.count("registerCommand("), P.s.count(' = mk("')

# ======================================================================= the BUILD script
P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.78: THE LAST TWO OLD-PAGE DOORS''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.79: /bank + SkyyBank's Storage > Bank tab = the Market screen's Bank view while the old menu is off: two bridge Functions for SkyyBank
       0.1.19 - menu:fn:bankview (opens the Bank view for a UUID; '+' opened / '-' reason, never null) and menu:fn:oldmenu (is the old menu on?);
       ONE new class MenuBankFn (notes: tools/menu_0_3_79_patch.py). CHECKED: SkyyMenu/test_skyymenu_0.3.79.py.
0.3.78: THE LAST TWO OLD-PAGE DOORS''')
P.rep('VERSION = "0.3.78"\n', 'VERSION = "0.3.79"\n')

# ======================================================================= the class
P.rep('''sgt  = mk("SettingsTab", T["PAGE"])   # 0.3.64: THE SETTINGS TAB = ONE SCREEN
''', '''sgt  = mk("SettingsTab", T["PAGE"])   # 0.3.64: THE SETTINGS TAB = ONE SCREEN
mbk  = mk("MenuBankFn")      # 0.3.79: menu:fn:bankview / menu:fn:oldmenu for SkyyBank's /bank + Storage > Bank tab
''')

BANK_JAVA = r'''
# ================= 0.3.79 (bankroute): MenuBankFn = menu:fn:bankview (op 1) / menu:fn:oldmenu (op 2) for SkyyBank 0.1.19's /bank and its
# Storage > Bank hub tab (contract: the header of tools/menu_0_3_79_patch.py). The caller is on the player's world thread (a command / a page
# event, as MenuHubOpen). bankview = the Market screen opened on its Bank view (view 4) - the same MarketTab the bank card's Bank button shows.
mbk.addInterface(pool.get("java.util.function.Function"))
F(mbk, "public int op;")
F(mbk, "public static volatile int OPENED = 0;")
F(mbk, "public static volatile int REFUSED = 0;")
C(mbk, "public MenuBankFn(int op) { this.op = op; }")
M(mbk, r"""
public static String open(java.util.UUID u, String via) {
  if (u == null) return "-Unknown player.";
  if (@PKG@.MenuCfg.OLD_MENU) return "-The old SkyWynn menu is on (Server Setup) - the bank page opens.";
  if (@PKG@.InvCraft.fn("bank:fn:view") == null || @PKG@.InvCraft.fn("bank:fn:act") == null) return "-The Bank view needs SkyyBank 0.1.18 - the bank page opens.";
  if (@PKG@.InvCraft.fn("bazaar:fn:tab") == null || @PKG@.InvCraft.fn("bazaar:fn:tabact") == null) return "-The Market screen is not on this server - the bank page opens.";
  @PR@ pr = null;
  try { pr = @UNI@.get().getPlayer(u); } catch (Throwable t) { pr = null; }
  if (pr == null || !pr.isValid()) return "-That player is not online.";
  @REF@ r = pr.getReference();
  if (r == null || !r.isValid()) return "-That player is not in a world right now.";
  @ST@ st = r.getStore();
  if (st == null) return "-That player is not in a world right now.";
  @PLA@ p = null;
  try { p = (@PLA@) st.getComponent(r, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  if (p == null) return "-That player cannot see pages right now.";
  @PGM@ pm = p.getPageManager();
  if (pm == null) return "-That player cannot see pages right now.";
  @PKG@.MarketTab pg = new @PKG@.MarketTab(pr, via == null ? "/bank" : via);
  pg.pref = r;
  pg.pst = st;
  pg.view = 4;
  try {
    Object cur = pm.getCustomPage();
    if (cur instanceof @PKG@.MenuPage) ((@PKG@.MenuPage) cur).clearGrid();
    pm.openCustomPage(r, st, pg);
  } catch (Throwable t) {
    pg.closed = true;
    @PKG@.MenuUtil.warn("the Bank view could not open for " + pr.getUsername() + " (the bank page opens instead): " + t);
    return "-The SkyWynn screen could not open - the bank page opens.";
  }
  @PKG@.MarketTab.OPENS = @PKG@.MarketTab.OPENS + 1;
  OPENED = OPENED + 1;
  return "+The Bank opened in the SkyWynn screen.";
}""")
M(mbk, r"""
public Object apply(Object o) {
  if (this.op == 2) return @PKG@.MenuCfg.OLD_MENU ? Boolean.TRUE : Boolean.FALSE;
  try {
    java.util.UUID u = null;
    if (o instanceof java.util.UUID) u = (java.util.UUID) o;
    else if (o instanceof String) {
      try { u = java.util.UUID.fromString(((String) o).trim()); } catch (Throwable t) { u = null; }
    }
    String r = open(u, "/bank");
    if (!r.startsWith("+")) REFUSED = REFUSED + 1;
    return r;
  } catch (Throwable t) {
    REFUSED = REFUSED + 1;
    @PKG@.MenuUtil.warn("menu:fn:bankview failed for " + o + " (the bank page opens instead): " + t);
    return "-Something went wrong - the bank page opens.";
  }
}""")
# setup(): put both (returns 2); shutdown(): remove them, only while the key still holds OUR object
M(mbk, r"""
public static int register() {
  java.util.Map br = @PKG@.MenuUtil.bridge();
  br.put("menu:fn:bankview", new @PKG@.MenuBankFn(1));
  br.put("menu:fn:oldmenu", new @PKG@.MenuBankFn(2));
  return 2;
}""")
M(mbk, r"""
public static void unregister() {
  java.util.Map br = @PKG@.MenuUtil.bridge();
  Object a = br.get("menu:fn:bankview");
  if (a instanceof @PKG@.MenuBankFn) br.remove("menu:fn:bankview", a);
  Object b = br.get("menu:fn:oldmenu");
  if (b instanceof @PKG@.MenuBankFn) br.remove("menu:fn:oldmenu", b);
}""")
'''
P.rep('''print("0.3.69 old menu: Server Setup menu.oldMenu (default ON), %d leftover old-page links in the new screen (follow-up rounds)" % len(OLD_LEFT))
''', '''print("0.3.69 old menu: Server Setup menu.oldMenu (default ON), %d leftover old-page links in the new screen (follow-up rounds)" % len(OLD_LEFT))
''' + BANK_JAVA)
P.rep('''# the button is 'Bank' and opens the Market screen's Bank view (SkyyBank 0.1.18 bank:fn:view / bank:fn:act). Still outside SkyyMenu: SkyyBank's own
''', '''# the button is 'Bank' and opens the Market screen's Bank view (SkyyBank 0.1.18 bank:fn:view / bank:fn:act). Still outside SkyyMenu: SkyyBank's own
# (0.3.79 bankroute: with SkyyBank 0.1.19 those two doors ask menu:fn:bankview first and open the Bank view while the old menu is off)
''')

# ======================================================================= plugin: put / remove, the ready line
P.rep('''  br.put("settings:fn:set", new @PKG@.SetSetFn());
''', '''  br.put("settings:fn:set", new @PKG@.SetSetFn());
  int bankRoute = 0;
  try { bankRoute = @PKG@.MenuBankFn.register(); } catch (Throwable t) { @PKG@.MenuUtil.warn("could not put menu:fn:bankview / menu:fn:oldmenu - /bank opens the bank page: " + t); }   // 0.3.79
''')
P.rep('''"has no /smithing") + "); page guard on (a page left open''',
      '''"has no /smithing") + "); /bank + the Storage > Bank tab: the Bank view while the old menu is off (menu:fn:bankview " + (bankRoute == 2 ? "put" : "NOT put") + "); page guard on (a page left open''')
P.rep('''  try { @PKG@.MenuHub.clearAll(); } catch (Throwable t) { }   // 0.3.28: hub:def / Menu's tabs / hub:last off the bridge
''', '''  try { @PKG@.MenuHub.clearAll(); } catch (Throwable t) { }   // 0.3.28: hub:def / Menu's tabs / hub:last off the bridge
  try { @PKG@.MenuBankFn.unregister(); } catch (Throwable t) { }   // 0.3.79: only OUR menu:fn:bankview / menu:fn:oldmenu
''')
P.rep('''wtd, wtab, wsp, scd, stab, sgd, sgt, pl)   # 0.3.50''', '''wtd, wtab, wsp, scd, stab, sgd, sgt, mbk, pl)   # 0.3.79: + MenuBankFn   # 0.3.50''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0 and P.s.count(' = mk("') == MK0 + 1, "0.3.79: one class, no system / command"
assert P.s.count('br.put("menu:fn:bankview"') == 1 and P.s.count('br.put("menu:fn:oldmenu"') == 1
_i = P.s.index
assert _i("public MarketTab(@PR@ pr, String via) {") < _i("public static String open(java.util.UUID u, String via) {") < _i("public void setup() {"), \
    "0.3.79: MenuBankFn after MarketTab, before the plugin"
assert _i("public void clearGrid() {") < _i("public static String open(java.util.UUID u, String via) {")
P.finish()

# ======================================================================= the HARNESS (every 0.3.78 check runs again on the 0.3.79 jar, plus BANKROUTE)
HARNESS_STATIC = r'''    # ---- BANKROUTE (0.3.79; Skyy 11-22 "build it all into the new system", 11-24 "keep building"): menu:fn:bankview / menu:fn:oldmenu
    K.check('br.put("menu:fn:bankview", new @PKG@.MenuBankFn(1));' in g and 'br.put("menu:fn:oldmenu", new @PKG@.MenuBankFn(2));' in g
            and "bankRoute = @PKG@.MenuBankFn.register();" in g and "@PKG@.MenuBankFn.unregister();" in g and "  pg.view = 4;" in g
            and 'if (@PKG@.MenuCfg.OLD_MENU) return "-The old SkyWynn menu is on (Server Setup) - the bank page opens.";' in g
            and 'if (this.op == 2) return @PKG@.MenuCfg.OLD_MENU ? Boolean.TRUE : Boolean.FALSE;' in g,
            "BANKROUTE STATIC setup puts menu:fn:bankview + menu:fn:oldmenu (MenuBankFn), shutdown removes them; bankview refuses while the old menu is on and opens view 4")
    K.check(g.count(' = mk("') == o.count(' = mk("') + 1 and 'mbk  = mk("MenuBankFn")' in g, "BANKROUTE STATIC one class added (MenuBankFn)")
    K.check(("settings", "setup") in left2_ and len(left2_) == 1, "BANKROUTE RATCHET OLD_LEFT = Server Setup only (unchanged)")
'''

HARNESS_ROUTE = r'''    # ---- BANKROUTE (0.3.79): menu:fn:bankview / menu:fn:oldmenu = what SkyyBank 0.1.19's /bank and Storage > Bank tab call (stand-ins for
    # SkyyBank 0.1.18 bank:fn:view / act + SkyyBazaar = OLD8's). Old menu ON = '-' (SkyyBank opens its old page); OFF = the Market screen on the
    # Bank view, ONE packet; every refusal opens nothing.
    @JImplements("java.util.function.Function")
    class FnR(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, o):
            try:
                return self.f(o)
            except Exception:
                import traceback as tb_
                K.notes.append("STUB FAILED: " + " | ".join(tb_.format_exc().splitlines()[-8:]))
    MBF = JV("MenuBankFn")
    for k_ in ("menu:fn:bankview", "menu:fn:oldmenu"):
        BR.remove(k_)
    K.eq(int(MBF.register()), 2, "BANKROUTE REG register puts both")
    BV, BO = BR.get("menu:fn:bankview"), BR.get("menu:fn:oldmenu")
    K.check(BV is not None and BO is not None and str(BV.getClass().getSimpleName()) == "MenuBankFn" and int(BV.op) == 1 and int(BO.op) == 2,
            "BANKROUTE REG menu:fn:bankview (op 1) + menu:fn:oldmenu (op 2) on the bridge")
    BK.update({"locked": False, "dash": None, "vnull": False, "anull": False, "pk": "prof-A", "lvOn": True, "coins": True, "readable": True, "intOn": True})
    saved_ = dict((k_, BR.get(k_)) for k_ in ("bazaar:fn:tab", "bazaar:fn:tabact", "bank:fn:view", "bank:fn:act"))
    for k_, f_ in (("bazaar:fn:tab", f_btab), ("bazaar:fn:tabact", f_bact), ("bank:fn:view", f_kview), ("bank:fn:act", f_kact)):
        BR.put(k_, FnR(f_))
    uO_ = PO.pr.getUuid()
    bstr_ = lambda x_: None if x_ is None else str(x_)
    jb_ = lambda x_: str(x_).lower()

    def route(arg_, what_):
        o_clear()
        f0_ = len(E.sent(PO))
        v0_ = len(BK["views"])
        n0_ = (int(MBF.OPENED), int(MBF.REFUSED))
        r_ = bstr_(BV.apply(arg_))
        E.pump(PO)
        return r_, pages(PO, f0_), len(BK["views"]) - v0_, (int(MBF.OPENED) - n0_[0], int(MBF.REFUSED) - n0_[1])
    # the old menu ON = refused (the old menu stays whole), nothing opened, no bank read
    CFG.OLD_MENU = True
    r_, ps_, nv_, d_ = route(uO_, "ON")
    K.check(jb_(BO.apply(uO_)) == "true" and jb_(BO.apply(None)) == "true" and r_ == "-The old SkyWynn menu is on (Server Setup) - the bank page opens."
            and not ps_ and o_cur() is None and nv_ == 0 and d_ == (0, 1),
            "BANKROUTE old menu ON: menu:fn:oldmenu TRUE; bankview = '-' (SkyyBank opens its old page), nothing opened, no bank read (%s)" % r_)
    # the old menu OFF = the Market screen on its Bank view
    CFG.OLD_MENU = False
    r_, ps_, nv_, d_ = route(uO_, "OFF")
    cur_ = PO.pm.getCustomPage()
    K.check(jb_(BO.apply(uO_)) == "false" and r_ == "+The Bank opened in the SkyWynn screen." and o_cur() == "MarketTab" and int(cur_.view) == 4 and len(ps_) == 1
            and only8(ps_[0]) and nv_ == 1 and d_ == (1, 0) and str(cur_.via) == "/bank" and cur_.pref == PO.ref,
            "BANKROUTE old menu OFF: bankview = '+', the Market screen on the Bank view, ONE packet with ONE bank:fn:view read (%s, %s, %d packets, %d reads)" % (r_, o_cur(), len(ps_), nv_))
    cm_ = cmap(ps_[0]) if ps_ else {}
    K.check(txt4(cm_, "KvP") == "{:,} coins".format(BK["purse"]) and str(MTD.ST_CATSEL) in mk_of(ps_[0], "SkyyMtabKvT4"),
            "BANKROUTE the opened view shows the bank (the stand-in's purse) with the Bank sub-tab selected (%s)" % txt4(cm_, "KvP"))
    p_ = cur_.handleDataEvent(PO.ref, PO.st, json.dumps({"a": "vw:0"})) if cur_ is not None else None
    E.pump(PO)
    K.check(int(cur_.view) == 0 and o_cur() == "MarketTab", "BANKROUTE the Market sub-tab on that screen = the Market cards (a normal Market screen)")
    r_, ps_, nv_, d_ = route(str(uO_), "a String uuid")
    K.check(r_.startswith("+") and o_cur() == "MarketTab" and int(PO.pm.getCustomPage().view) == 4 and len(ps_) == 1, "BANKROUTE apply(String uuid) works too (%s)" % r_)
    # every refusal: nothing opened, the caller opens its old page
    for k_, want_ in (("bank:fn:view", "-The Bank view needs SkyyBank 0.1.18 - the bank page opens."), ("bank:fn:act", "-The Bank view needs SkyyBank 0.1.18 - the bank page opens."),
                      ("bazaar:fn:tab", "-The Market screen is not on this server - the bank page opens."), ("bazaar:fn:tabact", "-The Market screen is not on this server - the bank page opens.")):
        sv_ = BR.remove(k_)
        r_, ps_, nv_, d_ = route(uO_, "no " + k_)
        K.check(r_ == want_ and not ps_ and o_cur() is None and nv_ == 0 and d_ == (0, 1), "BANKROUTE without %s = '-' naming it, nothing opened (%s)" % (k_, r_))
        BR.put(k_, sv_)
    for arg_, what_ in ((None, "null"), ("garbage", "a bad String"), (JClass("java.lang.Integer").valueOf(5), "an Integer")):
        r_, ps_, nv_, d_ = route(arg_, what_)
        K.check(r_ == "-Unknown player." and not ps_ and d_ == (0, 1), "BANKROUTE apply(%s) = '-Unknown player.', nothing opened" % what_)
    r_, ps_, nv_, d_ = route(UUIDc(0x6a, 0x6b), "an offline player")
    K.check(r_ == "-That player is not online." and not ps_ and nv_ == 0, "BANKROUTE an offline / unknown UUID = '-That player is not online.' (%s)" % r_)
    K.eq(str(MBF.open(None, None)), "-Unknown player.", "BANKROUTE open(null, null) = '-Unknown player.'")
    # a player without a usable world reference (left the world between the click and the call)
    rf_ = [f_ for f_ in PO.pr.getClass().getDeclaredFields() if str(f_.getType().getSimpleName()) == "Ref" and not JClass("java.lang.reflect.Modifier").isStatic(f_.getModifiers())]
    if rf_:
        rf_[0].setAccessible(True)
        keep_ = rf_[0].get(PO.pr)
        rf_[0].set(PO.pr, None)
        r_, ps_, nv_, d_ = route(uO_, "no reference")
        rf_[0].set(PO.pr, keep_)
        K.check(r_ in ("-That player is not online.", "-That player is not in a world right now.") and not ps_ and nv_ == 0 and o_cur() is None,
                "BANKROUTE a player with no world reference (PlayerRef.isValid false) = '-', nothing opened (%s)" % r_)
    else:
        K.notes.append("BANKROUTE the stand-in PlayerRef has no Ref field - the no-reference refusal is checked statically only")
    # no Universe (the server starting / stopping): the player lookup throws inside open() and is caught there
    UniC_ = JClass(PH + "server.core.universe.Universe")
    inst_ = E.jf(UniC_.class_, "instance")
    uni_ = inst_.get(None)
    inst_.set(None, None)
    r_, ps_, nv_, d_ = route(uO_, "no Universe")
    inst_.set(None, uni_)
    K.check(r_ == "-That player is not online." and not ps_, "BANKROUTE no Universe (the server starting / stopping) = '-', nothing opened, no throw (%s)" % r_)
    # unregister: only OUR objects go
    oth_ = FnR(lambda o_: None)
    BR.put("menu:fn:oldmenu", oth_)
    MBF.unregister()
    K.check(BR.get("menu:fn:bankview") is None and BR.get("menu:fn:oldmenu") is not None, "BANKROUTE REG unregister removes our bankview, keeps another mod's menu:fn:oldmenu")
    BR.remove("menu:fn:oldmenu")
    for k_, v_ in saved_.items():
        if v_ is None:
            BR.remove(k_)
        else:
            BR.put(k_, v_)
    K.notes.append("BANKROUTE ran: opened %d, refused %d" % (int(MBF.OPENED), int(MBF.REFUSED)))
    o_clear()
'''


def cut(t, start, end):
    i = t.index(start)
    j = t.index(end, i)
    return t[i:j]


T.rep('''"""Harness for SkyyMenu 0.3.78 (the last two old-page doors - the pocket Upgrades view, no Furnace / Tanning Full page; tools/menu_0_3_78_patch.py,''',
      '''"""Harness for SkyyMenu 0.3.79 (/bank + SkyyBank's Storage > Bank tab = the Bank view while the old menu is off; tools/menu_0_3_79_patch.py,
round bankroute). GENERATED by tools/menu_0_3_79_patch.py from the 0.3.78 harness (edit the patch, not this file): every 0.3.78 check runs
again on the 0.3.79 jar (OLD10's ratchet = 'stays gone'), plus
  BANKROUTE STATIC  setup puts menu:fn:bankview + menu:fn:oldmenu (one new class MenuBankFn), shutdown removes them; OLD_LEFT unchanged
            EXEC    old menu ON: oldmenu TRUE, bankview '-' + nothing opened + no bank read; OFF: '+', the Market screen on the Bank view (view 4),
                    ONE packet, ONE bank:fn:view read, the Bank sub-tab selected, the Market sub-tab works; a String uuid; without bank:fn:view /
                    act / bazaar:fn:tab / tabact = '-' naming it; null / bad String / Integer / offline UUID / no world reference / no Universe
                    = '-' and nothing opened; unregister keeps another mod's key
The 0.3.78 harness text follows:
Harness for SkyyMenu 0.3.78 (the last two old-page doors - the pocket Upgrades view, no Furnace / Tanning Full page; tools/menu_0_3_78_patch.py,''')
T.rep('VERSION = "0.3.78"\nJAR', 'VERSION = "0.3.79"\nJAR')
T.rep('OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.77.jar")', 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.78.jar")')
T.rep('GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.77.py")', 'GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.78.py")')
T.rep('PATCH = os.path.join(ROOT, "tools", "menu_0_3_78_patch.py")', 'PATCH = os.path.join(ROOT, "tools", "menu_0_3_79_patch.py")')
T.rep('"scratch", "oldmenu10", "menu"', '"scratch", "bankroute", "menu"')
T.rep('ADDED = []   # 0.3.78: no new class\n', 'ADDED = ["MenuBankFn"]   # 0.3.79: menu:fn:bankview / menu:fn:oldmenu\n')
EXPECT_BODY = '''    "MenuData": ["~<clinit>"], "OpsPage": ["~<clinit>"],   # the version strings
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyMenuPlugin": ["~m setup", "~m shutdown"],'''
T.rep(cut(T.s, 'EXPECT = {   # 0.3.78:', 'if "--expect-dump" in sys.argv:'), '''EXPECT = {   # 0.3.79: + MenuBankFn (ADDED), the plugin puts / removes it, the version strings
''' + EXPECT_BODY + '''
}
''')
T.rep('''    K.check(g.count('VERSION = "0.3.78"') == 1, "S VERSION")
''', '''    K.check(g.count('VERSION = "0.3.79"') == 1, "S VERSION")
''')
# OLD10's ratchet compared 0.3.78 with 0.3.77: against 0.3.78 its rows stay gone
T.rep('''    K.check(lefto_ - left2_ == set([("storage", "pocket"), ("smithing", "recipes")]) and left2_ == set([("settings", "setup")]),
            "OLD10 RATCHET OLD_LEFT lost storage:pocket + smithing:recipes; left = Server Setup only (on purpose) (%d -> %d: %s)" % (len(lefto_), len(left2_), sorted(left2_)))
''', '''    K.check(("storage", "pocket") not in left2_ and ("smithing", "recipes") not in left2_ and left2_ == set([("settings", "setup")]),
            "OLD10 RATCHET (0.3.79: vs 0.3.78) storage:pocket + smithing:recipes stay gone; left = Server Setup only (on purpose) (%d -> %d: %s)" % (len(lefto_), len(left2_), sorted(left2_)))
''' + HARNESS_STATIC)
T.rep('''    CFG.OLD_MENU = False   # as the OLD7 loop left it
    o_clear()
''', HARNESS_ROUTE + '''    CFG.OLD_MENU = False   # as the OLD7 loop left it
    o_clear()
''')
if T.dst:
    T.finish()
