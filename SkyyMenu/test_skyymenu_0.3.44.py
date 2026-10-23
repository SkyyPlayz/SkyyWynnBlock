"""Harness for SkyyMenu 0.3.44 (UI round R1 part A: double-tap crouch = a choice with the quest tracker fold as the untouched default, the
menu:walkkey / menu:crouch bridge flags, Your Stats by source; tools/menu_0_3_44_patch.py).
Build first:
    python tools/menu_0_3_44_patch.py && python SkyyMenu/build_skyymenu_0.3.44.py

    python SkyyMenu/test_skyymenu_0.3.44.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py; the SkyyMenu 0.3.19 engine stand-ins, -Xverify:all):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.43 -> 0.3.44: exactly the listed members differ
  M44  EXECUTED:
       CHOICE  SoundSw.crouchChoice on real settings files: untouched = Fold; an own menu.hotkey=true (chosen ON before 0.3.44) = Open
               the menu; own OFF / the server default OFF = Nothing; menu.crouchfold true / false wins; the files are never written by
               the reading; Reset all = Fold again
       FLAGS   menu:walkkey:<uuid> "1" / "0" (Server Setup row + the player's switch), menu:crouch:<uuid> fold / menu / off: published by
               SoundSw.pub, again by SetStore.set of each watched key, removed by forget
       TICK    the real MenuHotkey.tick + HotkeyOpen: a double-tap crouch with Fold + hud:fn:questFold answering TRUE = folded (the
               function got { uuid, "toggle" }, no page, nothing sent, FOLDED + 1); FALSE / missing / throwing = the Menu opens (FOLD_FELL);
               Open the menu = the Menu (the function not called); Nothing = nothing queued at all; the Walk key opens the Menu whatever
               the choice
       SET     Settings > General: the Double-tap crouch row has 3 buttons (the choice selected), no ON / OFF; page rules +
               assert_menu_page; each choice click saves (menu.hotkey + menu.crouchfold), says so, answers with EXACTLY ONE packet; every
               other row keeps ON / OFF (one packet each)
       STATS   StatsCalc on real bridge values: gear:stats does not hold Charms / Pets / Trees (SkyyGear 0.3.38 withExtra false - the
               spec's question, read from the SET SkyyGear script); a gear row = Base | Gear | Charms | Pets (floored) | Trees (only while
               tree:reads:SkyyGear lists gear:extras) | Class, total = the sum; Defense's skill Defense in Base; Class Weapon Damage
               level part in Base + balance in Class; Health / Mana / Stamina from real EntityStatValue modifiers by key; cell colours;
               the element groups add charms + pets + trees; the column header rows + the Sources legend; the page BUILT: page rules +
               assert_menu_page, every table cell set, Refresh = exactly one packet
  D    live     two starts on a scratch COPY of the live Skyy_SkyyMenu (the 0.3.35 harness's phase)
  AA   engine-access audit
Not testable offline (UNVERIFIED): the client's input, the look of the table at the player's UI scale.
Exit code 1 on any failure.
"""
import os, sys, re, time, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "dev"))
import harness_kit as HK
import skyybuild as B
import skyyui as SUI

_s42 = importlib.util.spec_from_file_location("test_skyymenu_0_3_42", os.path.join(HERE, "test_skyymenu_0.3.42.py"))
T42 = importlib.util.module_from_spec(_s42)
_s42.loader.exec_module(T42)
T35 = T42.T35
T19 = T42.T19

VERSION = "0.3.44"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.43.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "uir1a", "menu")))
PKG = "com.skyy.menu."
ADDED = []
EXPECT = {
    'CfgFile': ['~<clinit>'],                                                # fix 2: the defaults template's menu.crouchfold line
    'SetDefCfg': ['~m customGet', '~m customRead', '~m customSet'],          # fix 2: the menu.crouchDefault Server Setup row
    'SetReg': ['~m loadAdmin'],                                              # fix 2: the inlined template text
    'CfgFn': ['~m opExport'], 'CfgRows': ['~<clinit>', '~m header'],          # the config kit's version text + the two hotkey row helps
    'GrantTask': ['~m grantNow'],                                            # the welcome line names the double-tap crouch fold
    'HotkeyOpen': ['+f FOLDED', '+f FOLD_FELL', '+m fold', '~<clinit>', '~m run'],
    'MenuData': ['+f CFOLD_KEY', '+f CROUCH_FLAG', '+f KEY_FLAG', '+f QFOLD_FN', '+f STG_CH_LABELS', '+f UI_SCHB', '+f UI_SCHSELB',
                 '+f UI_STXTCB', '~<clinit>'],                               # + the version / row label / help / Mods texts
    'OpsPage': ['~<clinit>'],                                                # the Mods list's SkyyMenu line (Walk key / crouch)
    'SetStore': ['~m set'],                                                  # publishes the flags when a watched key changes
    'SettingsPage': ['~m build', '~m handleDataEvent'],                      # the choice row
    'SkyyMenuPlugin': ['~m setup'],                                          # the version text
    'SoundSw': ['+m crouchChoice', '+m flags', '+m walkOn', '+m watched', '~m forget', '~m pub'],
    'StatsCalc': ['+f COLS', '+f COL_STAT', '+f COL_TOTAL', '+f LEG_HEAD', '+f LEG_N', '+f LEG_T', '+f LEG_TOTAL', '+m cellCol', '+m cellOf', '+m col',
                  '+m defT', '+m gearT', '+m listed', '+m petsKv', '+m plus', '+m tparts', '+m treesKv', '+m trow', '-m defRow', '-m gearRow',
                  '~<clinit>', '~m allRows', '~m classDamage', '~m combatTab', '~m mainTab', '~m vital', '~m vitalRow'],
    'StatsPage': ['~m build'],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}


def run_m44(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JArray, JImplements, JOverride, JObject
    K = HK.Child(out)
    hcls = os.path.join(scratch, "hcls_m")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, jar], verify=True)
    E = T19.engine(scratch, hcls)
    JV = lambda n: JClass(PKG + n)
    Paths = E.Paths
    home = os.path.join(scratch, "home_m")
    sdir = os.path.join(home, "settings")
    os.makedirs(os.path.join(home, "layouts"), exist_ok=True)
    os.makedirs(sdir, exist_ok=True)
    JV("PageGuard").STOP = False
    JV("PageGuard").EXEC = None
    ML = JV("MenuLayout")
    ML.DIR = Paths.get(os.path.join(home, "layouts"))
    ML.DEF_FILE = Paths.get(os.path.join(home, "layout-default.properties"))
    SS, SR, SW, MD, MC = JV("SetStore"), JV("SetReg"), JV("SoundSw"), JV("MenuData"), JV("MenuCfg")
    SS.DIR = Paths.get(sdir)
    SR.ADMIN_FILE = Paths.get(os.path.join(home, "settings-defaults.properties"))
    SR.registerOwn()
    JV("MenuIO").begin()
    MH = JV("MenuHub")
    BR = JV("MenuUtil").bridge()
    E.br = BR
    MH.register()
    UUID = JClass("java.util.UUID")
    Boolean = JClass("java.lang.Boolean")

    # ------------------------------------------------------------------ CHOICE
    def uid(n):
        return UUID.fromString("00000000-0000-0000-0000-0000000004%02d" % n)

    def wfile(u, lines):
        open(os.path.join(sdir, str(u) + ".properties"), "w", encoding="utf-8").write("_v=1\n" + "".join(l_ + "\n" for l_ in lines))
    cases = [(1, [], 0, "untouched (no line) = Fold quest tracker (Skyy's new default)"),
             (2, ["menu.hotkey=true"], 1, "an OWN menu.hotkey=true (chosen ON before 0.3.44) = Open the menu (kept)"),
             (3, ["menu.hotkey=false"], 2, "an own menu.hotkey=false = Nothing (kept)"),
             (4, ["menu.crouchfold=true"], 0, "menu.crouchfold=true = Fold"),
             (5, ["menu.crouchfold=false"], 1, "menu.crouchfold=false = Open the menu"),
             (6, ["menu.hotkey=true", "menu.crouchfold=true"], 0, "ON + crouchfold true = Fold"),
             (7, ["menu.hotkey=false", "menu.crouchfold=true"], 2, "OFF wins over crouchfold = Nothing")]
    for n, lines, want, what in cases:
        wfile(uid(n), lines)
    before = dict((f, open(os.path.join(sdir, f), "rb").read()) for f in os.listdir(sdir))
    for n, lines, want, what in cases:
        K.eq(int(SW.crouchChoice(uid(n))), want, "CHOICE: " + what)
    after = dict((f, open(os.path.join(sdir, f), "rb").read()) for f in os.listdir(sdir))
    K.check(before == after, "CHOICE: reading the choice writes no file (no migration needed)")
    K.eq(int(SW.crouchChoice(None)), 2, "CHOICE: no uuid = Nothing")
    SR.adminPut("menu.hotkey", Boolean.FALSE)
    K.eq(int(SW.crouchChoice(uid(1))), 2, "CHOICE: the server default OFF (Server Setup) = Nothing for an untouched player")
    SR.adminPut("menu.hotkey", None)
    K.eq(int(SS.resetAll(uid(2))), 1, "CHOICE: Reset all on the 'chose ON' player")
    K.eq(int(SW.crouchChoice(uid(2))), 0, "CHOICE: ... back to the default Fold")
    # fix pass 2: the server default (Server Setup -> Menu "Double-tap crouch default: fold quests" = the menu.crouchfold defaults line)
    SDC = JV("SetDefCfg")
    K.eq(str(SDC.customGet("menu.crouchDefault")), "true", "FIX2a: the crouch default row reads ON while no line is set")
    r_ = SDC.customSet("menu.crouchDefault", "false")
    K.eq((str(r_[0]), str(r_[1]), str(r_[3][0]), str(r_[3][1])), ("ok", "false", "menu.crouchfold", "false"),
         "FIX2a: setting it OFF writes the menu.crouchfold=false defaults line")
    K.eq(str(SDC.customGet("menu.crouchDefault")), "false", "FIX2a: ... and reads back OFF")
    K.eq([int(SW.crouchChoice(uid(n))) for n in (1, 2, 3, 4, 5)], [1, 1, 2, 0, 1],
         "FIX2a: server default OFF -> untouched = Open the menu; own lines still win (ON=Open, OFF=Nothing, own fold / open kept)")
    SR.adminPut("menu.hotkey", Boolean.FALSE)
    K.eq(int(SW.crouchChoice(uid(1))), 2, "FIX2a: menu.hotkey OFF as the server default still = Nothing")
    SR.adminPut("menu.hotkey", None)
    SDC.customSet("menu.crouchDefault", "true")
    K.eq(int(SW.crouchChoice(uid(1))), 0, "FIX2a: server default ON -> untouched = Fold")
    SR.adminPut("menu.crouchfold", None)
    JMap = JClass("java.util.HashMap")
    vm = JMap()
    vm.put("menu.crouchfold", "false")
    vm.put("menu.tooltips", "true")
    K.eq((str(SDC.customRead("menu.crouchDefault", vm)), str(SDC.customRead("menu.tooltipsDefault", vm)), SDC.customRead("menu.other", vm)),
         ("false", "true", None), "FIX2a: customRead maps each row to its own defaults line")
    K.check("menu.crouchfold=true folds" in str(MD.SET_TEMPLATE), "FIX2a: the defaults template explains menu.crouchfold")

    # ------------------------------------------------------------------ FLAGS
    u1 = uid(1)
    SW.pub(u1)
    K.eq((str(BR.get("menu:walkkey:" + str(u1))), str(BR.get("menu:crouch:" + str(u1)))), ("1", "fold"), "FLAGS: pub -> walkkey 1, crouch fold")
    SS.set(u1, "menu.walkmenu", False, False)
    K.eq(str(BR.get("menu:walkkey:" + str(u1))), "0", "FLAGS: the player's Walk switch OFF -> walkkey 0 at once (SetStore.set)")
    SS.set(u1, "menu.walkmenu", True, False)
    MC.WALK_KEY = False
    SW.pub(u1)
    K.eq(str(BR.get("menu:walkkey:" + str(u1))), "0", "FLAGS: Server Setup's Walk row OFF -> walkkey 0 (the sweep / next pub)")
    MC.WALK_KEY = True
    SS.set(u1, "menu.crouchfold", False, False)
    K.eq(str(BR.get("menu:crouch:" + str(u1))), "menu", "FLAGS: crouchfold false -> crouch menu at once")
    SS.set(u1, "menu.hotkey", False, False)
    K.eq(str(BR.get("menu:crouch:" + str(u1))), "off", "FLAGS: hotkey OFF -> crouch off at once")
    SS.set(u1, "menu.hotkey", True, False)
    SS.set(u1, "menu.crouchfold", True, False)
    K.eq((str(BR.get("menu:walkkey:" + str(u1))), str(BR.get("menu:crouch:" + str(u1)))), ("1", "fold"), "FLAGS: back to 1 / fold")
    # fix pass 2: a stale put is corrected by the re-read in flags(): plant wrong values, publish, they follow the settings
    BR.put("menu:crouch:" + str(u1), "off")
    BR.put("menu:walkkey:" + str(u1), "0")
    SW.flags(u1)
    K.eq((str(BR.get("menu:walkkey:" + str(u1))), str(BR.get("menu:crouch:" + str(u1)))), ("1", "fold"), "FIX2d: flags() re-publishes the current values")
    SW.forget(u1)
    K.check(BR.get("menu:walkkey:" + str(u1)) is None and BR.get("menu:crouch:" + str(u1)) is None, "FLAGS: forget removes both flags")
    for k_, w_ in (("menu.hotkey", True), ("menu.walkmenu", True), ("menu.crouchfold", True), ("menu.sounds", True), ("menu.tooltips", False)):
        K.eq(bool(SW.watched(k_)), w_, "FLAGS: watched(%s) = %s" % (k_, w_))

    # ------------------------------------------------------------------ TICK (real system, stand-in chunk)
    @JImplements("java.util.function.Function")
    class Fold(object):
        def __init__(self):
            self.ans, self.calls, self.boom = True, [], False

        @JOverride
        def apply(self, a):
            self.calls.append([str(x) for x in a])
            if self.boom:
                raise RuntimeError("boom")
            return Boolean.TRUE if self.ans is True else (Boolean.FALSE if self.ans is False else self.ans)
    fold = Fold()
    UniC = JClass("com.hypixel.hytale.server.core.universe.Universe")
    byU = E.jf(UniC.class_, "playersByUuid").get(UniC.get())
    PH_ = E.player(uid(20), name="SkyyCroucher")
    byU.put(PH_.pr.getUuid(), PH_.pr)
    E.UniH.PL.add(PH_.pr)
    E.PLAYERS.add(PH_.pr)
    MVS = JClass("com.hypixel.hytale.protocol.MovementStates")
    msc = E.MSCc()
    ms_ = MVS()
    ms_.onGround = True
    msc.setMovementStates(ms_)
    PH_.st.row(PH_.ref).put(E.CT_MSC, msc)
    ACH = JClass("com.hypixel.hytale.component.ArchetypeChunk")
    ch = E.U.allocateInstance(ACH.class_)
    E.jf(ACH.class_, "refs").set(ch, JArray(E.REFc)([PH_.ref]))
    E.jf(ACH.class_, "entitiesSize").setInt(ch, 1)
    HK_, HO = JV("MenuHotkey"), JV("HotkeyOpen")
    sysm = HK_()
    HK_.ST.clear()
    HK_.ON = True
    E.W1.tasks = None
    u = PH_.pr.getUuid()
    MC.HOTKEY_COOLDOWN_MS = 500

    def tick(n=1):
        for _i in range(n):
            sysm.tick(0.033, 0, ch, PH_.st, None)

    def tap():
        ms_.crouching = True
        tick(1)
        time.sleep(0.04)
        ms_.crouching = False
        tick(1)
        time.sleep(0.04)

    def dtap():
        time.sleep(0.6)
        tap()
        tap()

    def dismiss():
        if PH_.pm.getCustomPage() is not None:
            PH_.pm.handleLegacyCustomPageEvent(PH_.ref, PH_.st, E.CPE(E.CPT.Dismiss, None))
    BR.put("hud:fn:questFold", fold)
    f0, ff0 = int(HO.FOLDED), int(HO.FOLD_FELL)
    n0 = len(E.sent(PH_))
    dtap()
    K.eq(E.queued(E.W1), ["HotkeyOpen"], "TICK: a double-tap crouch queues its HotkeyOpen (one detector, unchanged)")
    E.run_world(E.W1)
    K.check(fold.calls == [[str(u), "toggle"]], "TICK FOLD: the untouched player's double tap calls hud:fn:questFold { uuid, toggle }: %s" % fold.calls)
    K.check(PH_.pm.getCustomPage() is None and len(E.sent(PH_)) == n0 and int(HO.FOLDED) - f0 == 1, "TICK FOLD: TRUE = folded - no page, nothing sent, FOLDED + 1")
    for label, setup in (("FALSE", lambda: setattr(fold, "ans", False)), ("a non-Boolean", lambda: setattr(fold, "ans", "yes")),
                         ("throwing", lambda: setattr(fold, "boom", True))):
        setup()
        dtap()
        E.run_world(E.W1)
        K.check(PH_.pm.getCustomPage() is not None and int(HO.FOLD_FELL) - ff0 >= 1, "TICK FOLD: the function answers %s -> the Menu opens (FOLD_FELL)" % label)
        E.pump(PH_)
        dismiss()
        fold.ans, fold.boom = True, False
        ff0 = int(HO.FOLD_FELL)
    BR.remove("hud:fn:questFold")
    dtap()
    E.run_world(E.W1)
    K.check(PH_.pm.getCustomPage() is not None and int(HO.FOLD_FELL) - ff0 == 1, "TICK FOLD: no hud:fn:questFold (older SkyyHud) -> the Menu opens as 0.3.43")
    E.pump(PH_)
    dismiss()
    BR.put("hud:fn:questFold", fold)
    SS.set(u, "menu.crouchfold", False, False)
    c0 = len(fold.calls)
    dtap()
    E.run_world(E.W1)
    K.check(PH_.pm.getCustomPage() is not None and len(fold.calls) == c0, "TICK OPEN: 'Open the menu' opens the Menu, the fold function not called")
    E.pump(PH_)
    dismiss()
    SS.set(u, "menu.hotkey", False, False)
    E.W1.tasks = None
    dtap()
    K.check(E.queued(E.W1) in ([], ["HotkeyOpen"]), "TICK NOTHING: (queued %s)" % E.queued(E.W1))
    E.run_world(E.W1)
    K.check(PH_.pm.getCustomPage() is None and len(fold.calls) == c0, "TICK NOTHING: 'Nothing' - no page, no fold")
    time.sleep(0.45)
    ms_.walking = True
    tick(1)
    E.run_world(E.W1)
    K.check(PH_.pm.getCustomPage() is not None, "TICK WALK: the Walk key opens the Menu whatever the crouch choice")
    E.pump(PH_)
    dismiss()
    ms_.walking = False
    tick(1)
    E.run_world(E.W1)
    dismiss()
    SS.set(u, "menu.hotkey", True, False)
    SS.set(u, "menu.crouchfold", True, False)

    # ------------------------------------------------------------------ SET (the Settings page)
    def openp(X, pg):
        X.pm.openCustomPage(X.ref, X.st, pg)
        E.pump(X)
        return pg

    def click(X, pg, a):
        n_ = len(E.sent(X))
        pg.handleDataEvent(X.ref, X.st, '{"a":"%s"}' % a)
        k_ = E.kinds(X, n_)
        E.pump(X)
        return k_
    SP = E.player(uid(21), name="SkyySetter")
    byU.put(SP.pr.getUuid(), SP.pr)
    us = SP.pr.getUuid()
    sg = openp(SP, JV("SettingsPage")(SP.pr, -1))
    gen = [i for i, c in enumerate(list(MD.SET_CAT_ID)) if str(c) == "general"][0]
    click(SP, sg, "stab%d" % gen)
    keys = [str(x) for x in sg.rowKeys]
    K.check("menu.hotkey" in keys, "SET: the General category lists the Double-tap crouch row (%d rows)" % len(keys))
    r = keys.index("menu.hotkey")
    c, e = T35.build_page(sg, SP)
    apps, _els = T35.page_rules(K, c, e, "Settings (General)")
    try:
        SUI.assert_menu_page(apps, hub="settings", what="Settings (General)", sets=[(s, T35.unq(d)) for ty, s, t, d in c if ty == "Set"])
        K.check(True, "SET: assert_menu_page (General)")
    except Exception as ex:
        K.check(False, "SET: assert_menu_page: %s" % ex)
    btn = [t for ty, s, t, d in c if (t or "").startswith("TextButton #SkyyStgCh%dn" % r)]
    K.check(len(btn) == 3 and 'Text: "Fold quest tracker"' in btn[0] and 'Text: "Open the menu"' in btn[1] and 'Text: "Nothing"' in btn[2],
            "SET: the row has the 3 choice buttons")
    K.check("#7fe07f" in btn[0] and "#7fe07f" not in btn[1] and "#e07070" not in btn[2], "SET: Fold (the current choice) is the selected one")
    K.check(not [t for ty, s, t, d in c if re.match(r"TextButton #SkyyStg(On|Off)%d " % r, t or "")], "SET: ... and no ON / OFF on that row")
    bnd = dict((s, d) for s, d in e)
    K.check(all(("sch%dn%d" % (r, k_)) in str(bnd.get("#SkyyStgCh%dn%d" % (r, k_))) for k_ in range(3)), "SET: the 3 buttons are bound")
    o = 0 if r != 0 else 1
    K.check("#SkyyStgOn%d" % o in bnd and "#SkyyStgOff%d" % o in bnd, "SET: another row keeps ON / OFF")
    for k_, (hk, cf, want) in enumerate(((True, True, 0), (True, False, 1), (False, None, 2))):
        kd = click(SP, sg, "sch%dn%d" % (r, k_))
        K.eq(kd, ["UpdatePage"] if kd and kd[0] == "UpdatePage" else kd[:1], "SET: (packet kinds %s)" % kd)
        K.eq(len(kd), 1, "SET: choice %d answers with exactly one packet" % k_)
        K.eq(int(SW.crouchChoice(us)), want, "SET: choice %d saved" % k_)
        v_ = SS.own(us, "menu.hotkey")
        K.check(v_ is not None and bool(v_) == hk, "SET: ... menu.hotkey own %s" % v_)
        if cf is not None:
            K.check(SS.own(us, "menu.crouchfold") is not None and bool(SS.own(us, "menu.crouchfold")) == cf, "SET: ... menu.crouchfold %s" % cf)
        K.check(str(MD.STG_CH_LABELS[k_]) in str(sg.status) and "saved" in str(sg.status), "SET: ... the status says %r" % str(sg.status))
    c2, _e2 = T35.build_page(sg, SP)
    b2 = [t for ty, s, t, d in c2 if (t or "").startswith("TextButton #SkyyStgCh%dn" % r)]
    K.check(len(b2) == 3 and "#e07070" in b2[2] and "#7fe07f" not in b2[0], "SET: after Nothing the Nothing button is the selected (red) one")
    kd = click(SP, sg, "soff%d" % o)
    K.eq(len(kd), 1, "SET: an ON / OFF row still answers with exactly one packet")
    click(SP, sg, "son%d" % o)
    click(SP, sg, "sch%dn0" % r)

    # ------------------------------------------------------------------ STATS
    SC = JV("StatsCalc")
    gtxt = open(os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.38.py"), encoding="utf-8").read()
    K.check('String ss = @PKG@.GearStats.statsString(@PKG@.GearStats.totalsInv(u, inv, false));' in gtxt
            and '"gear:stats:" + u, ss' in gtxt and "if (withExtra) {" in gtxt,
            "STATS: VERIFIED in the SET SkyyGear 0.3.38: gear:stats = totalsInv(withExtra false) - no Charms / Pets / Trees in it")
    HM_ = JClass("java.util.HashMap")
    CHM = JClass("java.util.concurrent.ConcurrentHashMap")
    JD, JI = JClass("java.lang.Double"), JClass("java.lang.Integer")
    sx = UUID.fromString("00000000-0000-0000-0000-000000000531")
    BR.put("gear:fn:stats", fold)
    BR.put("gear:stats:" + str(sx), "str:40,cc:10,def:20,dmg:5")
    BR.put("gear:extra:" + str(sx), "str:5,cd:12")
    pm = HM_()
    pm.put("str", JD(4.6))
    pm.put("str ", JD(3.0))
    pm.put("cc", JI(2))
    pm.put("swing.mining", JD(1.0))
    BR.put("pets:stats:" + str(sx), pm)
    xm = CHM()
    xm.put("trees", "str:3")
    xm.put("nexus", "def:4")
    BR.put("gear:extras:" + str(sx), xm)

    def rowsOf(tab):
        al = SC.rows(sx, tab, None)
        return [[None if y is None else str(y) for y in r_] for r_ in al]

    def find(rs, name):
        for r_ in rs:
            if r_[0] == name:
                return r_
        return None
    rs = rowsOf(0)
    st_ = find(rs, "Strength")
    K.eq(st_, ["Strength", "52", "", "-", "+40", "+5", "+7", "-", "-"],
         "STATS: Strength (SkyyGear not reading gear:extras yet): Gear 40, Charms 5, Pets 7 (4.6 + 3 floored), Trees not counted")
    BR.put("tree:reads:SkyyGear", "bp.mining, gear:extras ,dd.mining")
    rs = rowsOf(0)
    K.eq(find(rs, "Strength"), ["Strength", "55", "", "-", "+40", "+5", "+7", "+3", "-"], "STATS: ... with gear:extras in tree:reads:SkyyGear: Trees +3, total 55")
    K.eq(find(rs, "Crit Chance"), ["Crit Chance", "12%", "", "-", "+10%", "-", "+2%", "-", "-"], "STATS: Crit Chance with the % unit")
    BR.put("skill:def:" + str(sx), JD(15.0))
    rs = rowsOf(0)
    K.eq(find(rs, "Defense"), ["Defense", "39", "", "+15", "+20", "-", "-", "+4", "-"], "STATS: Defense - the skill Defense in Base, the Nexus post in Trees")
    K.check(find(rs, "Speed") is not None and len(find(rs, "Speed")) == 3, "STATS: Speed stays a text row (its words)")
    K.check(find(rs, "Health") == ["Health", "-", "not read - click Refresh"], "STATS: no vitals read -> the Health text row")
    # Class Weapon Damage: the level part in Base, the class balance in Class
    BR.put("profile:class:" + str(sx), "Warrior")
    BR.put("class:" + str(sx), "Warrior")
    BR.put("class:skill:" + str(sx), "Swordsmanship")
    BR.put("skill:" + str(sx), "Swordsmanship:50,Mining:3")
    BR.put("skill:dmg:" + str(sx), JD(12.5))
    rc = rowsOf(1)
    K.eq(find(rc, "Class Weapon Damage"), ["Class Weapon Damage", "22.5%", "", "+10%", "-", "-", "-", "-", "+12.5%"],
         "STATS: Class Weapon Damage = level 50 x 0.2 % in Base + the 12.5 % balance in Class")
    K.eq(find(rc, "Damage"), ["Damage", "5%", "", "-", "+5%", "-", "-", "-", "-"], "STATS: Damage (Combat) by source")
    # vitals from real EntityStatValue modifiers
    ESV = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue")
    SMO = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier")
    MTG = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget")
    CAL = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType")
    v = E.U.allocateInstance(ESV.class_)
    E.jf(ESV.class_, "max").setFloat(v, 240.0)
    mods = HM_()
    for k_, a_ in (("skyygear_hp", 30.0), ("skyyacc_health", 20.0), ("skyypet_health", 10.0), ("skyytree_health", 5.0),
                   ("skyyskill_rebirthhp", 6.0), ("skyyskill_classhp", 12.0), ("skyyskill_overallhp", 7.0), ("someone_else", 3.0)):
        mods.put(k_, SMO(MTG.MAX, CAL.ADDITIVE, float(a_)))
    E.jf(ESV.class_, "modifiers").set(v, mods)
    vv = [str(x) for x in SC.vital(v)]
    K.eq(vv[3:], ["157", "+30", "+20", "+10", "+11", "+12"], "STATS: Health 240 = Base 157 (the game + armour + Overall + others) | Gear 30 | "
                                                              "Charms 20 | Pets 10 | Trees 11 (tree + Nexus) | Class 12")
    K.eq(vv[0], "240", "STATS: the total is the max")
    al = JClass("java.util.ArrayList")()
    SC.vitalRow(al, "Health", JArray(JObject)([JArray(JClass("java.lang.String"))(vv), None, None]), 0)
    K.eq([str(x) for x in al.get(0)], ["Health", "240", "", "157", "+30", "+20", "+10", "+11", "+12"], "STATS: the Health TABLE row")
    for t_, want in (("-", "#7f93a6"), ("+5", "#7ee08a"), ("-3", "#ff7a7a"), ("157", "#d6e4ee"), ("", "#7f93a6"), (None, "#7f93a6")):
        K.eq(str(SC.cellCol(t_, 0)), want, "STATS: cell colour of %r" % t_)
    ax = SC.plus(SC.plus(SC.kv("fFire:2"), SC.kv("fFire:1,fAir:4")), SC.kv("fAir:1"))
    K.eq((float(SC.get(ax, "fFire")), float(SC.get(ax, "fAir"))), (3.0, 5.0), "STATS: plus() adds the element parts (charms + pets + trees)")
    K.eq((bool(SC.listed("a, b ,c", "b")), bool(SC.listed("ab,c", "b")), bool(SC.listed(None, "b"))), (True, False, False), "STATS: listed() = whole tokens")
    allr = [[None if y is None else str(y) for y in r_] for r_ in SC.allRows(sx, None)]
    heads = [r_[1] for r_ in allr if r_[0] is None and r_[1] is not None]
    K.eq(heads, ["Main", "Combat", "Gathering", "Sources"], "STATS: the sections + the Sources legend")
    colh = [i for i, r_ in enumerate(allr) if r_[0] is None and r_[1] is None]
    K.check(len(colh) == 2 and allr[colh[0] - 1][1] == "Main" and allr[colh[1] - 1][1] == "Combat", "STATS: a column header row under Main and Combat (not Gathering)")
    leg = [r_[0] for r_ in allr[[i for i, r_ in enumerate(allr) if r_[1] == "Sources"][0] + 1:]]
    K.eq(leg, ["Base", "Gear", "Charms", "Pets", "Trees", "Class", "Total"], "STATS: the legend rows (+ the Total caveat)")
    _tot = allr[-1]
    K.check(_tot[0] == "Total" and "not counted yet" in " ".join(x for x in _tot if x), "FIX2: the legend's last row says Total misses some tree / Rebirth bonuses: %s" % _tot)
    # the page itself
    PS = E.player(sx, name="SkyyStats")
    byU.put(sx, PS.pr)
    stp = openp(PS, JV("StatsPage")(PS.pr, 0))
    c3, e3 = T35.build_page(stp, PS)
    apps3, _x = T35.page_rules(K, c3, e3, "Your Stats (by source)")
    try:
        info = SUI.assert_menu_page(apps3, hub="character", what="Your Stats", sets=[(s, T35.unq(d)) for ty, s, t, d in c3 if ty == "Set"])
        K.check(True, "STATS: assert_menu_page (rows %d, sub rows %d)" % (info["rows"], info["subs"]))
    except Exception as ex:
        K.check(False, "STATS: assert_menu_page: %s" % ex)
    sets3 = dict((s, T35.unq(d)) for ty, s, t, d in c3 if ty == "Set")
    ist = [i for i, r_ in enumerate(allr) if r_[0] == "Strength"][0]
    K.eq([sets3.get("#SkyyStatC%dn%d.Text" % (ist, k_)) for k_ in range(6)] + [sets3.get("#SkyyStatV%d.Text" % ist)],
         ["-", "+40", "+5", "+7", "+3", "-", "55"], "STATS: the page sets every Strength cell + the total")
    cm = [t for ty, s, t, d in c3 if (t or "").startswith("Label #SkyyStatC%dn1 " % ist)]
    K.check(len(cm) == 1 and "#7ee08a" in cm[0] and "RenderBold: true" in cm[0] and "End" in cm[0], "STATS: a positive cell is green, bold, End-aligned")
    cd = [t for ty, s, t, d in c3 if (t or "").startswith("Label #SkyyStatC%dn0 " % ist)]
    K.check(len(cd) == 1 and "#7f93a6" in cd[0], "STATS: an empty cell is the dim grey")
    tv = [t for ty, s, t, d in c3 if (t or "").startswith("Label #SkyyStatV%d " % ist)]
    K.check(len(tv) == 1 and "#e8c25a" in tv[0] and "RenderBold: true" in tv[0], "STATS: the total is bold gold")
    K.eq([sets3.get("#SkyyStatC%dn%d.Text" % (colh[0], k_)) for k_ in range(6)] + [sets3.get("#SkyyStatN%d.Text" % colh[0]), sets3.get("#SkyyStatV%d.Text" % colh[0])],
         ["Base", "Gear", "Charms", "Pets", "Trees", "Class", "Stat", "Total"], "STATS: the column header row")
    isp = [i for i, r_ in enumerate(allr) if r_[0] == "Speed"][0]
    K.check(sets3.get("#SkyyStatS%d.Text" % isp) is not None and "#SkyyStatC%dn0.Text" % isp not in sets3, "STATS: Speed drawn as a text row")
    kd = click(PS, stp, "trefresh")
    K.eq(len(kd), 1, "STATS: Refresh answers with exactly one packet (%s)" % kd)
    MH.clearAll()
    JV("MenuIO").stop(2000)
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("m44", run_m44), ("live", T35.run_live)], script=__file__, live=(T35.LIVE_DIR, "Skyy_SkyyMenu"))
