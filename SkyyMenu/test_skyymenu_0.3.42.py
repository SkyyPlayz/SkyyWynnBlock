"""Harness for SkyyMenu 0.3.42 (the Walk key (Left Alt) opens the SkyWynn Menu; tools/menu_0_3_42_patch.py).
Build first:
    python tools/menu_0_3_42_patch.py && python SkyyMenu/build_skyymenu_0.3.42.py

    python SkyyMenu/test_skyymenu_0.3.42.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py; the SkyyMenu 0.3.19 engine stand-ins, -Xverify:all):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.41 -> 0.3.42: exactly the listed members differ
  W42  EXECUTED - the Walk key:
       STEP    walkStep(): the rising edge fires once, holding never repeats, a re-press inside the cooldown does not, after it does; the
               Server Setup row off = nothing (the edge is still tracked); a clock that went back does not lock it; the cooldown is live
       CFG     MenuCfg defaults (on, 400 ms), config.properties walkKey / walkKeyCooldownMs read + clamped (200-5000), missing = defaults;
               the Server Setup header carries menu.walkKey (bool) + menu.walkKeyCooldownMs (int ms); the template lists both
       TICK    the real MenuHotkey.tick over a stand-in chunk + the real MovementStatesComponent: no state for a player who neither crouches
               nor walks; walking false -> true queues ONE HotkeyOpen (walk) on the player's world, nothing opened inside the tick; the
               world task opens the SkyWynn Menu (main view) through the real PageManager; holding Walk 30 ticks = nothing more;
               a press while the Menu is open = ignored SILENTLY (same page, nothing sent, no refusal line, WALK_SKIPPED + 1);
               cooldown inside the tick; the player switch menu.walkmenu OFF = nothing opens; Server Setup row off = nothing queued;
               a window open / profile busy / dead (DeathComponent stand-in) = refused; the double-tap crouch still works next to it
       QUIT    MenuQuit (PlayerDisconnectEvent) drops the player's hotkey state at once; prune still drops a dead ref
       TEXT    the settings switch (General, ON), the defaults template line, the Mods line, the grant chat line, the Stats page's True
               Damage % (SkyyGear 0.3.35)
  D    live     two starts on a scratch COPY of the live Skyy_SkyyMenu (the 0.3.35 harness's phase)
  AA   engine-access audit
Input itself (the client sending walking=true when Alt is pressed, also while standing) cannot be proven offline.
Exit code 1 on any failure.
"""
import os, sys, time, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "dev"))
import harness_kit as HK
import skyybuild as B

_s41 = importlib.util.spec_from_file_location("test_skyymenu_0_3_41", os.path.join(HERE, "test_skyymenu_0.3.41.py"))
T41 = importlib.util.module_from_spec(_s41)
_s41.loader.exec_module(T41)
T35 = T41.T35
T19 = T35.T19

VERSION = "0.3.42"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.41.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "menu042", "menu")))
PKG = "com.skyy.menu."
ADDED = []
EXPECT = {
    'CfgFn': ['~m opExport'], 'CfgRows': ['~<clinit>', '~m header'],          # the config kit's version text + the two new rows
    'CfgFile': ['~<clinit>'],                                                 # the rows' file bindings (walkKey, walkKeyCooldownMs)
    'GrantTask': ['~m grantNow'],                                             # the chat line names the Walk key
    'HotkeyOpen': ['+f walk', '+f WALK_OPENED', '+f WALK_SKIPPED', '+m wantedWalk', '+m isDead', '+c ',
                   '~c ', '~m run', '~<clinit>'],
    'MenuCfg': ['+f WALK_KEY', '+f WALK_COOLDOWN_MS', '~m load', '~<clinit>', '~m init'],
    'MenuData': ['+f WALK_SW_KEY', '~<clinit>'],
    'MenuHotkey': ['+m walkStep', '+m forget', '~m tick'],
    'MenuQuit': ['~m accept'],
    'OpsPage': ['~<clinit>'],
    'SetReg': ['~m loadAdmin'],
    'SkyyMenuPlugin': ['~m setup'],
    'StatsCalc': ['~<clinit>'],
}


def run_w42(out, jar, scratch, _home):
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
    MH, MD = JV("MenuHub"), JV("MenuData")
    BR = JV("MenuUtil").bridge()
    E.br = BR
    MH.register()
    HK_, HO, MC = JV("MenuHotkey"), JV("HotkeyOpen"), JV("MenuCfg")
    MVS = JClass("com.hypixel.hytale.protocol.MovementStates")

    # ------------------------------------------------------------------ STEP (pure)
    K.eq((bool(MC.WALK_KEY), int(MC.WALK_COOLDOWN_MS)), (True, 400), "CFG: MenuCfg defaults - Walk key on, 400 ms cooldown")

    def seq(events, s_=None):
        s_ = s_ if s_ is not None else JArray(jpype.JLong)(5)
        return [bool(HK_.walkStep(s_, w_, t_)) for w_, t_ in events]
    K.eq(seq([(False, 900), (True, 1000)]), [False, True], "STEP: Walk pressed (false -> true) fires")
    K.eq(seq([(True, 1000)] + [(True, 1000 + 33 * i) for i in range(1, 40)]), [True] + [False] * 39, "STEP: holding Walk never repeats")
    K.eq(seq([(True, 1000), (False, 1100), (True, 1200)]), [True, False, False], "STEP: a re-press 0.2 s later (inside 0.4 s) does not fire")
    K.eq(seq([(True, 1000), (False, 1100), (True, 1450)]), [True, False, True], "STEP: a re-press 0.45 s later fires")
    K.eq(seq([(True, 1000), (False, 1100), (True, 1200), (False, 1300), (True, 1500)]), [True, False, False, False, True],
         "STEP: a press swallowed by the cooldown does not move it (the next one after 0.4 s fires)")
    K.eq(seq([(True, 5000), (False, 5050), (True, 3000)]), [True, False, True], "STEP: a clock that went back does not lock the key")
    MC.WALK_KEY = False
    s0 = JArray(jpype.JLong)(5)
    K.eq(seq([(True, 1000), (False, 1100), (True, 2000)], s0), [False, False, False], "STEP: Server Setup row off - never fires")
    K.eq(int(s0[3]), 1, "STEP: the edge is still tracked while off")
    MC.WALK_KEY = True
    K.eq(seq([(True, 3000)], s0), [False], "STEP: turned back on while Walk is HELD - no fire until the next press")
    K.eq(seq([(False, 3100), (True, 3200)], s0), [False, True], "STEP: the next press fires")
    MC.WALK_COOLDOWN_MS = 2000
    K.eq(seq([(True, 1000), (False, 1100), (True, 2500), (False, 2600), (True, 3100)]), [True, False, False, False, True],
         "STEP: the cooldown is live from MenuCfg (2 s)")
    MC.WALK_COOLDOWN_MS = 400
    # the crouch double-tap's own step() is untouched next to it (the shared long[5] state)
    s1 = JArray(jpype.JLong)(5)
    K.eq([bool(HK_.step(s1, c_, True, t_)) for c_, t_ in ((True, 1000), (False, 1100), (True, 1300))], [False, False, True],
         "STEP: double-tap crouch still fires on the long[5] state")

    # ------------------------------------------------------------------ CFG (file + Server Setup)
    cfgf = os.path.join(scratch, "w42-config.properties")
    keepF = MC.FILE
    for txt_, want_ in (("walkKey=false\nwalkKeyCooldownMs=1000\n", (False, 1000)), ("walkKeyCooldownMs=50\n", (True, 200)),
                        ("walkKeyCooldownMs=99999\nwalkKey=off\n", (False, 5000)), ("walkKey=maybe\nwalkKeyCooldownMs=abc\n", (True, 400)),
                        ("giveItem=true\nhotkeyGapMs=400\n", (True, 400))):
        open(cfgf, "w").write(txt_)
        MC.FILE = Paths.get(cfgf)
        MC.load()
        K.eq((bool(MC.WALK_KEY), int(MC.WALK_COOLDOWN_MS)), want_, "CFG: config.properties %r -> %s" % (txt_.strip(), want_))
    MC.FILE = Paths.get(os.path.join(scratch, "w42-missing.properties"))
    MC.WALK_KEY = False
    MC.load()
    K.eq((bool(MC.WALK_KEY), int(MC.WALK_COOLDOWN_MS)), (True, 400), "CFG: no config file - defaults")
    MC.FILE = keepF
    txt = str(MD.MENU_CFG_TEXT)
    K.check("walkKey=true" in txt and "walkKeyCooldownMs=400" in txt, "CFG: the config.properties template lists walkKey + walkKeyCooldownMs")
    JV("CfgPub").publish()
    hdr = BR.get("config:def:SkyyMenu")
    rows_ = dict((str(rw[0]), [str(x) for x in rw]) for rw in hdr[7])
    K.check("menu.walkKey" in rows_ and rows_["menu.walkKey"][1] == "Open the Menu with the Walk key (Alt)" and rows_["menu.walkKey"][3:5] == ["bool", "true"],
            "CFG: Server Setup row menu.walkKey (bool, ON): %s" % rows_.get("menu.walkKey"))
    K.check("menu.walkKeyCooldownMs" in rows_ and rows_["menu.walkKeyCooldownMs"][3:10] == ["int", "400", "200", "5000", "step=50", "ms", "live,adv"],
            "CFG: Server Setup row menu.walkKeyCooldownMs (int ms 200-5000, default 400): %s" % rows_.get("menu.walkKeyCooldownMs"))

    # ------------------------------------------------------------------ TICK (real system, stand-in chunk)
    UniC = JClass("com.hypixel.hytale.server.core.universe.Universe")
    byU = T19_jf(E, UniC.class_, "playersByUuid").get(UniC.get())
    PH_ = E.player(E.UUID.fromString("00000000-0000-0000-0000-0000000000c1"), name="SkyyWalker")
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

    def press(hold=1):
        ms_.walking = True
        tick(hold)
        ms_.walking = False
        tick(1)
    tick(30)
    K.eq(int(HK_.ST.size()), 0, "TICK: no state kept for a player who neither crouches nor walks")
    f0, wo0, rf0 = int(HK_.FIRED), int(HO.WALK_OPENED), int(HO.REFUSED)
    ms_.walking = True
    tick(1)
    K.eq((int(HK_.FIRED) - f0, E.queued(E.W1)), (1, ["HotkeyOpen"]), "TICK: Walk pressed queues ONE HotkeyOpen on the player's world")
    K.check(bool(E.W1.tasks.peek().walk), "TICK: the queued open is the Walk variant")
    K.check(PH_.pm.getCustomPage() is None, "TICK: nothing opened inside the system's tick")
    tick(30)
    K.eq(int(HK_.FIRED) - f0, 1, "TICK: holding Walk 30 ticks fires nothing more")
    E.run_world(E.W1)
    cp = PH_.pm.getCustomPage()
    K.check(cp is not None and str(cp.getClass().getName()) == PKG + "MenuPage" and str(cp.view) == "main",
            "TICK: the world task opens the SkyWynn Menu (main view) through the real PageManager")
    K.eq(int(HO.WALK_OPENED) - wo0, 1, "TICK: WALK_OPENED counted")
    E.pump(PH_)
    ms_.walking = False
    tick(1)
    time.sleep(0.45)
    n1, sk0 = len(E.sent(PH_)), int(HO.WALK_SKIPPED)
    press()
    K.eq(E.queued(E.W1), ["HotkeyOpen"], "TICK: a press while the Menu is open is queued (the page check runs on the world thread)")
    E.run_world(E.W1)
    K.check(PH_.pm.getCustomPage() == cp and len(E.sent(PH_)) == n1, "TICK: Menu already open - same page, nothing sent (no re-open, no close)")
    K.eq((int(HO.WALK_SKIPPED) - sk0, int(HO.REFUSED) - rf0), (1, 0), "TICK: ignored SILENTLY (WALK_SKIPPED + 1, no refusal line)")
    PH_.pm.handleLegacyCustomPageEvent(PH_.ref, PH_.st, E.CPE(E.CPT.Dismiss, None))
    K.check(PH_.pm.getCustomPage() is None, "TICK: (the page dismissed like Esc)")
    press()
    K.eq(E.queued(E.W1), [], "TICK: a re-press inside the 0.4 s cooldown queues nothing")
    time.sleep(0.45)
    press()
    E.run_world(E.W1)
    K.check(PH_.pm.getCustomPage() is not None, "TICK: after the cooldown the Walk key opens the Menu again")
    E.pump(PH_)
    PH_.pm.handleLegacyCustomPageEvent(PH_.ref, PH_.st, E.CPE(E.CPT.Dismiss, None))
    # the player's own switch
    SS.set(u, "menu.walkmenu", False, False)
    K.check(not bool(HO.wantedWalk(u)) and bool(HO.wanted(u)), "TICK: menu.walkmenu OFF - wantedWalk false, the crouch switch untouched")
    time.sleep(0.45)
    n2 = len(E.sent(PH_))
    press()
    E.run_world(E.W1)
    K.check(PH_.pm.getCustomPage() is None and len(E.sent(PH_)) == n2, "TICK: the player's switch OFF - nothing opens, nothing sent")
    SS.set(u, "menu.walkmenu", True, False)
    # the Server Setup row
    MC.WALK_KEY = False
    time.sleep(0.45)
    f1 = int(HK_.FIRED)
    press()
    K.check(int(HK_.FIRED) == f1 and E.queued(E.W1) == [], "TICK: Server Setup row off - nothing queued")
    K.check(not bool(HO.wantedWalk(u)), "TICK: Server Setup row off - wantedWalk false even for a player with the switch on")
    MC.WALK_KEY = True
    # refusals on the world thread: a window, profile busy, dead
    CWc = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.ContainerWindow")
    wins_ = E.jf(E.JC("com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager").class_, "windows").get(PH_.wm)
    wins_.put(jpype.JInt(5), E.U.allocateInstance(CWc.class_))
    rf1 = int(HO.REFUSED)
    HO(PH_.pr, True).run()
    K.check(PH_.pm.getCustomPage() is None and int(HO.REFUSED) == rf1 + 1, "TICK: a container window open - refused, nothing opened")
    wins_.remove(jpype.JInt(5))
    BR.put("profile:busy:" + str(u), True)
    HO(PH_.pr, True).run()
    K.check(PH_.pm.getCustomPage() is None and int(HO.REFUSED) == rf1 + 2, "TICK: profile:busy - refused")
    BR.remove("profile:busy:" + str(u))
    K.check(not bool(HO.isDead(PH_.st, PH_.ref)), "TICK: isDead false (and no exception) when the damage module is not there")
    DMc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageModule")
    dm = E.U.allocateInstance(DMc.class_)
    CTc = JClass("com.hypixel.hytale.component.ComponentType")
    ct_d = CTc()
    E.jf(CTc.class_, "index").setInt(ct_d, 990)
    E.jf(CTc.class_, "hashCode").setInt(ct_d, 990)
    Mod = JClass("java.lang.reflect.Modifier")
    for f_ in DMc.class_.getDeclaredFields():
        f_.setAccessible(True)
        if Mod.isStatic(f_.getModifiers()) and f_.getType() == DMc.class_:
            f_.set(None, dm)
        elif not Mod.isStatic(f_.getModifiers()) and str(f_.getType().getName()) == "com.hypixel.hytale.component.ComponentType" and "eath" in str(f_.getName()):
            f_.set(dm, ct_d)
    DTH = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent")
    K.check(DTH.getComponentType() == ct_d, "TICK: (the DeathComponent type stand-in is in place)")
    K.check(not bool(HO.isDead(PH_.st, PH_.ref)), "TICK: alive - isDead false")
    PH_.st.row(PH_.ref).put(ct_d, E.U.allocateInstance(DTH.class_))
    HO(PH_.pr, True).run()
    K.check(PH_.pm.getCustomPage() is None and int(HO.REFUSED) == rf1 + 3 and bool(HO.isDead(PH_.st, PH_.ref)), "TICK: dead - refused")
    PH_.st.row(PH_.ref).remove(ct_d)
    HO(PH_.pr, True).run()
    K.check(PH_.pm.getCustomPage() is not None and int(HO.REFUSED) == rf1 + 3, "TICK: alive again, no window, not busy - it opens")
    E.pump(PH_)
    PH_.pm.handleLegacyCustomPageEvent(PH_.ref, PH_.st, E.CPE(E.CPT.Dismiss, None))
    # the double-tap crouch next to it (the crouch variant is not the Walk variant)
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
    PH_.pm.handleLegacyCustomPageEvent(PH_.ref, PH_.st, E.CPE(E.CPT.Dismiss, None))
    # after shutdown
    HK_.ON = False
    time.sleep(0.45)
    f2 = int(HK_.FIRED)
    press()
    K.check(int(HK_.FIRED) == f2 and E.queued(E.W1) == [], "TICK: after shutdown (ON false) the Walk key does nothing")
    HK_.ON = True

    # ------------------------------------------------------------------ QUIT
    K.eq(int(HK_.ST.size()), 1, "QUIT: one state for the player")
    PDE = JClass("com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent")
    ev = E.U.allocateInstance(PDE.class_)
    for f_ in [f for c in (PDE.class_, PDE.class_.getSuperclass()) if c is not None for f in c.getDeclaredFields()]:
        if str(f_.getType().getName()) == "com.hypixel.hytale.server.core.universe.PlayerRef":
            f_.setAccessible(True)
            f_.set(ev, PH_.pr)
    K.check(ev.getPlayerRef() == PH_.pr, "QUIT: (the stand-in disconnect event names the player)")
    JV("MenuQuit")().accept(ev)
    K.eq(int(HK_.ST.size()), 0, "QUIT: MenuQuit drops the player's hotkey state at once")
    HK_.forget(None)
    K.check(True, "QUIT: forget(null) is harmless")
    press()
    K.eq(int(HK_.ST.size()), 1, "QUIT: (a new press makes a new state)")
    E.jf(E.REFc.class_, "index").setInt(PH_.ref, -2147483648)
    HK_.prune()
    K.eq(int(HK_.ST.size()), 0, "QUIT: prune still drops a dead ref (world change)")

    # ------------------------------------------------------------------ TEXT
    d = JV("SetReg").DEFS.get("menu.walkmenu")
    K.check(d is not None and str(d[3]) == "general" and bool(d[4]) and str(d[0]) == "SkyyMenu",
            "TEXT: the switch menu.walkmenu is registered (General, ON, SkyyMenu)")
    K.check("#menu.walkmenu=true" in str(MD.SET_TEMPLATE), "TEXT: the settings defaults template lists it")
    K.check(bool(HO.wantedWalk(E.UUID.fromString("00000000-0000-0000-0000-0000000000b8"))), "TEXT: a player who never chose = ON")
    blob = []
    for f_ in MD.class_.getDeclaredFields():
        try:
            f_.setAccessible(True)
            v = f_.get(None)
            if v is None:
                continue
            try:
                blob.extend(str(x) for x in list(v))
            except Exception:
                blob.append(str(v))
        except Exception:
            pass
    blob = "\n".join(blob)
    K.check("Your Walk key (Alt) or double-tap crouch - open the menu (/settings)" in blob and "Double-tap crouch while standing" not in blob,
            "TEXT: the Mods list line names the Walk key (Alt)")
    K.check("Open the Menu with the Walk key (Alt)" in blob, "TEXT: the switch label")
    gcls = JClass("javassist.ClassPool")(True)
    gcls.insertClassPath(jar)
    ccg = gcls.get(PKG + "GrantTask")
    consts = ccg.getClassFile().getConstPool()
    strs = [str(consts.getStringInfo(i)) for i in range(1, consts.getSize()) if consts.getTag(i) == 8]
    K.check([s_ for s_ in strs if "press your Walk key (Alt)" in s_], "TEXT: the item grant chat line names the Walk key (Alt)")
    SCc = JV("StatsCalc")
    gk, gu = [str(x) for x in SCc.GK], [str(x) for x in SCc.GU]
    K.check("tdmg" in gk and gu[gk.index("tdmg")] == "%", "TEXT: the Stats page shows True Damage with % (SkyyGear 0.3.35)")
    K.eq(sum(1 for x in gu if x == "%"), 7, "TEXT: 7 % rows on the Stats page (0.3.41: 6 + True Damage)")
    K.save()


def T19_jf(E, c, name):
    return E.jf(c, name)


if __name__ == "__main__":
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("w42", run_w42), ("live", T35.run_live)], script=__file__, live=(T35.LIVE_DIR, "Skyy_SkyyMenu"))
