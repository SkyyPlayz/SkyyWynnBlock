"""Harness for SkyyMenu 0.3.43 (the 0.3.42 review follow-up: element % on the Stats page, the Walk cooldown stamped only by a real open,
the falling-edge fallback for a Walk press owed an open; tools/menu_0_3_43_patch.py).
Build first:
    python tools/menu_0_3_43_patch.py && python SkyyMenu/build_skyymenu_0.3.43.py

    python SkyyMenu/test_skyymenu_0.3.43.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py; the SkyyMenu 0.3.19 engine stand-ins, -Xverify:all):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.42 -> 0.3.43: exactly the listed members differ
  W43  EXECUTED:
       STEP    walkStep / cooling / opened (pure): held Walk = one fire, the release finds nothing owed after an open; an IGNORED press
               (no open) does not block the next press (0.3.42 did for 0.4 s); its release fires ONE fallback; the cooldown only after a
               REAL open; row off = nothing owed, nothing fires; a clock that went back does not lock; null / short state arrays are safe;
               the crouch double-tap still fires on long[6]
       TICK    the real MenuHotkey.tick + HotkeyOpen on the real PageManager: no state for an idle player; a held Walk press = ONE open
               (the queued open carries the state array; s[4] stamped by the open, nothing owed; 30 held ticks + the release queue
               nothing); a fast tap whose release falls before the open ran: two queued, ONE open, the second dropped by the cooldown
               (WALK_COOLED, nothing sent); a press over the open Menu ignored silently and NOT stamped; a TOGGLE key: the next press
               (walking true -> false) opens the Menu at once (inside 0.4 s of the ignored press); a HELD press over an open page: the
               release fallback is ignored silently too (same page, nothing sent, no refusal), at most once; refusals (window) apply to
               the fallback too; the player's switch OFF / Server Setup row OFF = nothing; the double-tap crouch still opens
       ELEM    StatsCalc.ELEM_U / RAW_U = "%" x 5 / x 3; groupRow: total + parts with "%", "none" line kept, the Raw row hidden at 0,
               mixed units = no unit on the total; the Stats page still shows 7 % gear rows
  D    live     two starts on a scratch COPY of the live Skyy_SkyyMenu (the 0.3.35 harness's phase)
  AA   engine-access audit
Input itself (whether the client's Walk key is held or toggled) cannot be proven offline.
Exit code 1 on any failure.
"""
import os, sys, time, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "dev"))
import harness_kit as HK
import skyybuild as B

_s42 = importlib.util.spec_from_file_location("test_skyymenu_0_3_42", os.path.join(HERE, "test_skyymenu_0.3.42.py"))
T42 = importlib.util.module_from_spec(_s42)
_s42.loader.exec_module(T42)
T35 = T42.T35
T19 = T42.T19

VERSION = "0.3.43"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.42.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "lean1022", "menu")))
PKG = "com.skyy.menu."
ADDED = []
EXPECT = {
    'CfgFn': ['~m opExport'], 'CfgRows': ['~m header'],                       # the config kit's version text
    'HotkeyOpen': ['+f hs', '+f WALK_COOLED', '+c ', '~c ', '~c ', '~m run', '~<clinit>'],
    'MenuHotkey': ['+m cooling', '+m opened', '~m walkStep', '~m tick'],
    'MenuData': ['~<clinit>'],                                                # the version text
    'OpsPage': ['~<clinit>'],                                                 # the SET versions baked into the Mods list (SET moved since 0.3.42)
    'SkyyMenuPlugin': ['~m setup'],
    'StatsCalc': ['+f ELEM_U', '+f RAW_U', '+m groupRow', '-m groupRow', '~m combatTab', '~<clinit>'],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}


def run_w43(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JArray
    K = HK.Child(out)
    hcls = os.path.join(scratch, "hcls_w")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, jar], verify=True)
    E = T19.engine(scratch, hcls)
    JV = lambda n: JClass(PKG + n)
    Paths = E.Paths
    home = os.path.join(scratch, "home_w")
    os.makedirs(os.path.join(home, "layouts"), exist_ok=True)
    JV("PageGuard").STOP = False
    JV("PageGuard").EXEC = None
    ML = JV("MenuLayout")
    ML.DIR = Paths.get(os.path.join(home, "layouts"))
    ML.DEF_FILE = Paths.get(os.path.join(home, "layout-default.properties"))
    SS = JV("SetStore")
    SS.DIR = Paths.get(os.path.join(home, "settings"))
    JV("SetReg").ADMIN_FILE = Paths.get(os.path.join(home, "settings-defaults.properties"))
    JV("SetReg").registerOwn()
    JV("MenuIO").begin()
    MH = JV("MenuHub")
    BR = JV("MenuUtil").bridge()
    E.br = BR
    MH.register()
    HK_, HO, MC = JV("MenuHotkey"), JV("HotkeyOpen"), JV("MenuCfg")
    MVS = JClass("com.hypixel.hytale.protocol.MovementStates")
    L6 = lambda: JArray(jpype.JLong)(6)

    # ------------------------------------------------------------------ STEP (pure)
    K.eq((bool(MC.WALK_KEY), int(MC.WALK_COOLDOWN_MS)), (True, 400), "STEP: MenuCfg defaults - Walk key on, 400 ms cooldown")

    def ws(s_, w_, t_):
        return bool(HK_.walkStep(s_, w_, t_))
    s = L6()
    K.eq([ws(s, False, 900), ws(s, True, 1000)], [False, True], "STEP: Walk pressed (false -> true) fires")
    K.eq((int(s[5]), int(s[4])), (1, 0), "STEP: the press is owed an open; walkStep stamps NO cooldown (0.3.42 did)")
    HK_.opened(s, True, 1000)
    K.eq((int(s[5]), int(s[4])), (0, 1000), "STEP: opened() (a real Walk open) stamps the cooldown and clears what is owed")
    K.eq([ws(s, True, 1000 + 33 * i) for i in range(1, 40)] + [ws(s, False, 2400)], [False] * 40,
         "STEP: HELD Walk after its open - no repeat, the release fires nothing (one open per press, as 0.3.42)")
    s = L6()
    K.eq([ws(s, True, 1000), ws(s, False, 1050), ws(s, True, 1100)], [True, True, True],
         "STEP: an IGNORED press (no open) - its release fires the fallback, the next press 0.1 s later fires (no cooldown without an open)")
    K.eq(int(s[4]), 0, "STEP: (still no cooldown stamped)")
    s = L6()
    K.eq([ws(s, True, 1000), ws(s, False, 1100)], [True, True], "STEP: fallback once ...")
    K.eq([ws(s, False, 1200), ws(s, False, 1300)], [False, False], "STEP: ... at most once per press (nothing owed after it)")
    s = L6()
    ws(s, True, 1000)
    HK_.opened(s, True, 1000)
    K.eq([ws(s, False, 1100), ws(s, True, 1200), ws(s, False, 1300), ws(s, True, 1450)], [False, False, False, True],
         "STEP: after a REAL open the cooldown blocks a press 0.2 s later (and its release at 0.3 s); 0.45 s fires")
    s = L6()
    ws(s, True, 1000)
    HK_.opened(s, True, 1000)
    K.eq([ws(s, False, 1100), ws(s, True, 1200), ws(s, False, 1500)], [False, False, True],
         "STEP: a press swallowed by the cooldown stays owed - its release after the cooldown fires the fallback")
    s = L6()
    ws(s, True, 5000)
    HK_.opened(s, True, 5000)
    K.eq([ws(s, False, 5050), ws(s, True, 3000)], [False, True], "STEP: a clock that went back does not lock the key")
    HK_.opened(s, False, 9000)
    K.eq((int(s[4]), int(s[5])), (5000, 0), "STEP: a crouch open (walk false) clears what is owed but stamps no Walk cooldown")
    MC.WALK_KEY = False
    s = L6()
    K.eq([ws(s, True, 1000), ws(s, False, 1100), ws(s, True, 2000), ws(s, False, 2100)], [False] * 4, "STEP: Server Setup row off - never fires")
    K.eq((int(s[3]), int(s[5])), (0, 0), "STEP: row off - the edge is tracked, nothing owed")
    ws(s, True, 3000)
    MC.WALK_KEY = True
    K.eq([ws(s, False, 3100), ws(s, True, 3200)], [False, True], "STEP: turned on while held - the release owes nothing, the next press fires")
    MC.WALK_COOLDOWN_MS = 2000
    s = L6()
    ws(s, True, 1000)
    HK_.opened(s, True, 1000)
    K.eq([ws(s, False, 1100), ws(s, True, 2500), ws(s, False, 2600), ws(s, True, 3100)], [False, False, False, True],
         "STEP: the cooldown is live from MenuCfg (2 s)")
    MC.WALK_COOLDOWN_MS = 400
    K.check(not bool(HK_.cooling(None, 1000)) and not bool(HK_.cooling(JArray(jpype.JLong)(3), 1000)), "STEP: cooling(null / short) = false")
    HK_.opened(None, True, 1000)
    HK_.opened(JArray(jpype.JLong)(5), True, 1000)
    K.check(True, "STEP: opened(null / a 0.3.42-size array) is harmless")
    s1 = L6()
    K.eq([bool(HK_.step(s1, c_, True, t_)) for c_, t_ in ((True, 1000), (False, 1100), (True, 1300))], [False, False, True],
         "STEP: double-tap crouch still fires on the long[6] state")

    # ------------------------------------------------------------------ TICK (real system, stand-in chunk)
    UniC = JClass("com.hypixel.hytale.server.core.universe.Universe")
    byU = E.jf(UniC.class_, "playersByUuid").get(UniC.get())
    PH_ = E.player(E.UUID.fromString("00000000-0000-0000-0000-0000000000c3"), name="SkyyToggler")
    byU.put(PH_.pr.getUuid(), PH_.pr)
    E.UniH.PL.add(PH_.pr)
    E.PLAYERS.add(PH_.pr)
    msc = E.MSCc()
    ms_ = MVS()
    ms_.onGround = True
    msc.setMovementStates(ms_)
    PH_.st.row(PH_.ref).put(E.CT_MSC, msc)
    ACH = JClass("com.hypixel.hytale.component.ArchetypeChunk")
    ch = E.U.allocateInstance(ACH.class_)
    E.jf(ACH.class_, "refs").set(ch, JArray(E.REFc)([PH_.ref]))
    E.jf(ACH.class_, "entitiesSize").setInt(ch, 1)
    sysm = HK_()
    HK_.ST.clear()
    HK_.ON = True
    E.W1.tasks = None
    u = PH_.pr.getUuid()

    def tick(n=1):
        for _i in range(n):
            sysm.tick(0.033, 0, ch, PH_.st, None)

    def walk(v, n=1):
        ms_.walking = v
        tick(n)

    def dismiss():
        PH_.pm.handleLegacyCustomPageEvent(PH_.ref, PH_.st, E.CPE(E.CPT.Dismiss, None))
    tick(30)
    K.eq(int(HK_.ST.size()), 0, "TICK: no state kept for a player who neither crouches nor walks")
    f0, wo0, rf0, sk0, co0 = int(HK_.FIRED), int(HO.WALK_OPENED), int(HO.REFUSED), int(HO.WALK_SKIPPED), int(HO.WALK_COOLED)
    walk(True)
    st_ = HK_.ST.get(PH_.ref)
    K.check(st_ is not None and len(st_) == 6, "TICK: the per-player state is long[6]")
    K.eq((int(HK_.FIRED) - f0, E.queued(E.W1)), (1, ["HotkeyOpen"]), "TICK HELD: Walk pressed queues ONE HotkeyOpen")
    t_ = E.W1.tasks.peek()
    K.check(bool(t_.walk) and t_.hs is not None and t_.hs.equals(st_), "TICK HELD: the queued open is the Walk variant and carries the player's state")
    K.check(PH_.pm.getCustomPage() is None and int(st_[4]) == 0, "TICK HELD: nothing opened or stamped inside the tick")
    tick(30)
    before = int(time.time() * 1000)
    E.run_world(E.W1)
    cp = PH_.pm.getCustomPage()
    K.check(cp is not None and str(cp.getClass().getName()) == PKG + "MenuPage" and str(cp.view) == "main", "TICK HELD: the world task opens the Menu")
    K.check(int(st_[4]) >= before - 5 and int(st_[5]) == 0, "TICK HELD: the open stamped the cooldown (s[4]) and cleared what is owed (s[5] 0)")
    E.pump(PH_)
    n0 = len(E.sent(PH_))
    walk(False)
    tick(10)
    K.eq((int(HK_.FIRED) - f0, E.queued(E.W1), int(HO.WALK_OPENED) - wo0), (1, [], 1),
         "TICK HELD: 30 held ticks + the release queue nothing more - ONE open per press (as 0.3.42)")
    # a press over the open Menu: ignored silently and NOT stamped; then a TOGGLE key's next press = the falling edge
    time.sleep(0.45)
    stamp0 = int(st_[4])
    walk(True)
    E.run_world(E.W1)
    K.check(PH_.pm.getCustomPage() == cp and len(E.sent(PH_)) == n0 and int(HO.WALK_SKIPPED) - sk0 == 1 and int(HO.REFUSED) == rf0,
            "TICK TOGGLE: a press over the open Menu is ignored silently (same page, nothing sent, WALK_SKIPPED + 1)")
    K.check(int(st_[4]) == stamp0 and int(st_[5]) == 1, "TICK TOGGLE: the ignored press stamps NO cooldown and stays owed")
    dismiss()
    K.check(PH_.pm.getCustomPage() is None, "TICK TOGGLE: (the page dismissed like Esc; walking stays ON - a toggle key)")
    walk(False)
    K.eq(E.queued(E.W1), ["HotkeyOpen"], "TICK TOGGLE: the next press (walking true -> false) queues the fallback open AT ONCE (inside 0.4 s of the ignored press)")
    E.run_world(E.W1)
    K.check(PH_.pm.getCustomPage() is not None and int(HO.WALK_OPENED) - wo0 == 2, "TICK TOGGLE: the fallback opens the Menu (0.3.42 opened nothing)")
    K.eq(int(st_[5]), 0, "TICK TOGGLE: nothing owed after the open")
    E.pump(PH_)
    tick(10)
    K.eq(E.queued(E.W1), [], "TICK TOGGLE: nothing more queued")
    # a HELD press over an open page: the release fallback is ignored silently too, at most once
    time.sleep(0.45)
    n1, sk1 = len(E.sent(PH_)), int(HO.WALK_SKIPPED)
    walk(True)
    E.run_world(E.W1)
    walk(False)
    K.eq(E.queued(E.W1), ["HotkeyOpen"], "TICK HELD-OVER-PAGE: the release of an ignored held press queues one fallback")
    E.run_world(E.W1)
    tick(10)
    K.check(PH_.pm.getCustomPage() is not None and len(E.sent(PH_)) == n1 and int(HO.WALK_SKIPPED) - sk1 == 2 and int(HO.REFUSED) == rf0
            and E.queued(E.W1) == [], "TICK HELD-OVER-PAGE: both ignored silently (no re-open, nothing sent, no refusal line), nothing more queued")
    dismiss()
    # a FAST TAP: the release falls before the press's open ran - two queued, ONE open, the second dropped by the cooldown
    time.sleep(0.45)
    n2, wo2, co2 = len(E.sent(PH_)), int(HO.WALK_OPENED), int(HO.WALK_COOLED)
    walk(True)
    walk(False)
    K.eq(E.queued(E.W1), ["HotkeyOpen", "HotkeyOpen"], "TICK FAST TAP: the press + its release fallback both queued (the open had not run yet)")
    E.run_world(E.W1)
    K.check(PH_.pm.getCustomPage() is not None and int(HO.WALK_OPENED) - wo2 == 1 and int(HO.WALK_COOLED) - co2 == 1,
            "TICK FAST TAP: ONE open; the second dropped by the cooldown on the world thread (WALK_COOLED + 1) - no flicker")
    E.pump(PH_)
    K.eq(len([k for k in E.kinds(PH_, n2) if k in ("CustomPage", "SetPage")]), 1, "TICK FAST TAP: exactly one page sent")
    dismiss()
    # a press 0.2 s after a REAL open is still blocked (the cooldown itself unchanged)
    walk(True)
    K.eq(E.queued(E.W1), [], "TICK: a press inside 0.4 s of a REAL open queues nothing")
    walk(False)
    K.eq(E.queued(E.W1), [], "TICK: ... nor its quick release (still inside the cooldown)")
    # refusals apply to the fallback too (a container window open)
    time.sleep(0.45)
    CWc = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.ContainerWindow")
    wins_ = E.jf(E.JC("com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager").class_, "windows").get(PH_.wm)
    wins_.put(jpype.JInt(5), E.U.allocateInstance(CWc.class_))
    rf1 = int(HO.REFUSED)
    walk(True)
    E.run_world(E.W1)
    walk(False)
    E.run_world(E.W1)
    K.check(PH_.pm.getCustomPage() is None and int(HO.REFUSED) - rf1 == 2, "TICK: a window open - the press AND its fallback refused (2 refusal lines)")
    wins_.remove(jpype.JInt(5))
    # the player's switch OFF / the Server Setup row OFF
    SS.set(u, "menu.walkmenu", False, False)
    time.sleep(0.45)
    n3 = len(E.sent(PH_))
    walk(True)
    walk(False)
    E.run_world(E.W1)
    K.check(PH_.pm.getCustomPage() is None and len(E.sent(PH_)) == n3, "TICK: the player's switch OFF - neither edge opens anything")
    SS.set(u, "menu.walkmenu", True, False)
    MC.WALK_KEY = False
    f1 = int(HK_.FIRED)
    walk(True)
    walk(False)
    K.check(int(HK_.FIRED) == f1 and E.queued(E.W1) == [], "TICK: Server Setup row off - nothing queued on either edge")
    MC.WALK_KEY = True
    # the double-tap crouch next to it
    time.sleep(1.6)
    E.W1.tasks = None

    def tap():
        ms_.crouching = True
        tick(1)
        time.sleep(0.05)
        ms_.crouching = False
        tick(1)
        time.sleep(0.05)
    tap()
    tap()
    K.check(E.queued(E.W1) == ["HotkeyOpen"] and not bool(E.W1.tasks.peek().walk), "TICK: double-tap crouch still queues its (crouch) open")
    E.run_world(E.W1)
    K.check(PH_.pm.getCustomPage() is not None, "TICK: the double-tap crouch opens the Menu")
    E.pump(PH_)
    dismiss()
    HO(PH_.pr, True).run()
    K.check(PH_.pm.getCustomPage() is not None, "TICK: the 0.3.42 constructor HotkeyOpen(pr, walk) still opens (no state: no cooldown check)")
    E.pump(PH_)
    dismiss()

    # ------------------------------------------------------------------ ELEM (the Stats page units)
    SCc = JV("StatsCalc")
    K.eq(([str(x) for x in SCc.ELEM_U], [str(x) for x in SCc.RAW_U]), (["%"] * 5, ["%"] * 3), "ELEM: ELEM_U / RAW_U are % (SkyyGear 0.3.35+)")
    K.eq([str(x) for x in SCc.ELEM_K] + [str(x) for x in SCc.RAW_K], ["fEarth", "fThunder", "fWater", "fFire", "fAir", "rThunder", "rWater", "rElem"],
         "ELEM: the 8 keys unchanged")
    HM, AL = JClass("java.util.HashMap"), JClass("java.util.ArrayList")
    JD = JClass("java.lang.Double")

    def hm(**kw):
        m = HM()
        for k_, v_ in kw.items():
            m.put(k_, JD(v_))
        return m

    def grp(g, a, keys, shorts, units, name, always):
        rows = AL()
        SCc.groupRow(rows, g, a, keys, shorts, units, name, always)
        return [[str(x) for x in r] for r in rows]
    r1 = grp(hm(fEarth=6.0, fFire=3.0), hm(fEarth=1.0), SCc.ELEM_K, SCc.ELEM_S, SCc.ELEM_U, "Elemental Damage", True)
    K.eq(r1, [["Elemental Damage", "10%", "Earth +7%, Fire +3%"]], "ELEM: total + parts with % (gear + accessories add up)")
    K.eq(grp(hm(), hm(), SCc.ELEM_K, SCc.ELEM_S, SCc.ELEM_U, "Elemental Damage", True), [["Elemental Damage", "0%", "none - it comes from weapons"]],
         "ELEM: nothing - 0% with the 'none' line")
    K.eq(grp(hm(), hm(), SCc.RAW_K, SCc.RAW_S, SCc.RAW_U, "Raw Elemental Damage", False), [], "ELEM: the Raw row stays hidden at 0")
    K.eq(grp(hm(rElem=2.5, rWater=1.0), hm(), SCc.RAW_K, SCc.RAW_S, SCc.RAW_U, "Raw Elemental Damage", False),
         [["Raw Elemental Damage", "3.5%", "Water +1%, Elemental +2.5%"]], "ELEM: the Raw row with %")
    JS = JClass("java.lang.String")
    mix = JArray(JS)(["%", ""])
    K.eq(grp(hm(a=1.0, b=2.0), hm(), JArray(JS)(["a", "b"]), JArray(JS)(["A", "B"]), mix, "Mixed", True), [["Mixed", "3", "A +1%, B +2"]],
         "ELEM: mixed units - no unit on the total, each part its own")
    K.eq(grp(hm(a=1.0), hm(), JArray(JS)(["a"]), JArray(JS)(["A"]), None, "NoUnits", True), [["NoUnits", "1", "A +1"]], "ELEM: null units are safe")
    gk, gu = [str(x) for x in SCc.GK], [str(x) for x in SCc.GU]
    K.eq(sum(1 for x in gu if x == "%"), 7, "ELEM: still 7 % gear rows (True Damage % from 0.3.42)")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("w43", run_w43), ("live", T35.run_live)], script=__file__, live=(T35.LIVE_DIR, "Skyy_SkyyMenu"))
