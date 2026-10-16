"""Harness for SkyyProfiles 0.1.15 (the first-join page fix: the first-profile page waits for SkyyHud 0.3.27's picture rebuild flag
hud:assets:ready:<uuid> + 1 s, else 12 s after the connect; a Profiles page opened before that is re-sent ONCE in full;
tools/profiles_0_1_15_patch.py). Build first: python tools/profiles_0_1_15_patch.py && python SkyyProfiles/build_skyyprofiles_0.1.15.py

    python SkyyProfiles/test_skyyprofiles_0.1.15.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.1.14 -> 0.1.15: + HudGate, PageRedraw; ProfilePage build (+ redraw(), the redrawQueued field), OpenTask.run, ReadyTask.run,
                ProfConnect.accept, ProfQuit.accept, the version texts only; non-class entries: manifest.json
  GATE EXECUTED (tools/hub_tab_kit.stage: the SkyyMenu 0.3.19 harness's engine stand-ins, the REAL PageManager, -Xverify:all):
       HG    HudGate.ready: a connection this jar never saw = ready (0.1.14 behaviour); right after connect = not ready; the flag first
             seen = not yet, seen 1 s = ready; a foreign / FALSE value is not the flag; 11 s without the flag = not ready, 12 s = ready
             (the fallback); the flag gone again = the 1 s starts over; a fast reconnect's OLD quit never clears the new clock
       OPEN  the first-join OpenTask (one poll per run, on the world thread): with the gate closed it never opens (the calm count does
             not even start); the gate open -> 2 calm polls -> exactly ONE Create Profile page (first), prompted marked; more polls
             never open a second one; the 12 s fallback opens it without SkyyHud; another page open = it waits, as before
       REDRAW END TO END on the engine's real SCHEDULED_EXECUTOR: a /profiles page opened BEFORE the gate queues ONE redraw (a
             click's second build queues no second one); while the gate is closed it only polls; the gate open -> ONE world task that
             re-sends that page in full ONCE (one CustomPage packet, REDRAWS + 1), nothing after; a page built after the gate queues
             none; by hand: gate closed = nothing, a page closed / replaced meanwhile = never redrawn, never re-opened
       CALLS bytecode: ProfConnect -> HudGate.connect, ProfQuit -> HudGate.quit, ReadyTask / OpenTask / ProfilePage.build ->
             HudGate.ready, ProfilePage.build -> PageRedraw.<init> + later, PageRedraw.run -> ProfilePage.redraw -> CustomUIPage.rebuild (protected)
  HUB / RB   test_skyyprofiles_0.1.14.py's hub phase + 0.1.13's rebirth-busy phase on the 0.1.15 jar. NOT RUN: 0.1.12's exec / live
             phases - their controls load SkyyProfiles-0.1.11.jar, which is tidied away (the 0.1.14 harness would fail the same way)
  AA   engine-access audit
Not testable without the game (UNVERIFIED): the client drawing the page cleanly after a real join.
Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW
import hub_tab_kit as HT

VERSION = "0.1.15"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyProfiles-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyProfiles-0.1.14.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "hud0327", "profiles")))
PKG = "com.skyy.profiles."
EXPECT = {"ProfilePage": ["+f redrawQueued", "+m redraw", "~m build"], "OpenTask": ["~m run"], "ReadyTask": ["~m run"], "ProfConnect": ["~m accept"],
          "ProfQuit": ["~m accept"],
          # the version texts only (constant pools checked)
          "SkyyProfilesPlugin": ["~m setup"], "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "ProfCfg": ["~m capMigrate"],
          "ProfDel": ["~m archiveLocked"]}
ADDED = ["HudGate", "PageRedraw"]
KEY = "hud:assets:ready:"


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def t14():
    return tmod("test_skyyprofiles_0.1.14.py", "tp0114")


def run_gate(out, jar, scratch, _home):
    from jpype import JClass, JLong
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    P_ = lambda n: JClass(PKG + n)
    Cfg, S, Del, HG, PR_, OT, PG = P_("ProfCfg"), P_("ProfStore"), P_("ProfDel"), P_("HudGate"), P_("PageRedraw"), P_("OpenTask"), P_("ProfilePage")
    home = os.path.join(scratch, "gate-mods", "Skyy_SkyyProfiles")
    os.makedirs(os.path.join(home, "players"), exist_ok=True)
    Paths = E.Paths
    Cfg.FILE = Paths.get(home, "config.properties")
    S.DIR, S.SWDIR, S.INVDIR, S.LOGF = Paths.get(home, "players"), Paths.get(home, "switching"), Paths.get(home, "inventories"), Paths.get(home, "switches.log")
    Del.ARCDIR = Paths.get(home, "archive")
    br = E.bridge
    Long = JClass("java.lang.Long")
    System = JClass("java.lang.System")
    # DeathComponent.getComponentType() reads DamageModule.get(): a stand-in module with its own component type (nobody is dead here)
    DM = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageModule")
    CTc = JClass("com.hypixel.hytale.component.ComponentType")
    dm = E.U.allocateInstance(DM.class_)
    ct = CTc()
    HT.jf(CTc.class_, "index").setInt(ct, 9901)
    HT.jf(CTc.class_, "hashCode").setInt(ct, 9901)
    for f_ in DM.class_.getDeclaredFields():
        f_.setAccessible(True)
        tn = str(f_.getType().getName())
        if tn == str(DM.class_.getName()) and JClass("java.lang.reflect.Modifier").isStatic(f_.getModifiers()):
            f_.set(None, dm)
        elif tn == "com.hypixel.hytale.component.ComponentType" and "eath" in str(f_.getName()):
            f_.set(dm, ct)
    now = lambda: int(System.currentTimeMillis())

    def age(m, u, ms):
        m.put(u, Long.valueOf(JLong(now() - ms)))

    def setflag(u, v=True):
        if v is True:
            br.put(KEY + str(u), E.TRUE)
        elif v is None:
            br.remove(KEY + str(u))
        else:
            br.put(KEY + str(u), v)
    # ---------------------------------------------------------------- HG
    P1 = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-0000000001a1"), "GateOne")
    u1 = P1.pr.getUuid()
    K.check(bool(HG.ready(u1, now())), "HG: a connection this jar never saw = ready (0.1.14 behaviour)")
    HG.connect(P1.pr)
    K.check(not bool(HG.ready(u1, now())), "HG: right after the connect, no flag = not ready")
    setflag(u1, "yes")
    K.check(not bool(HG.ready(u1, now())), "HG: a foreign value under the key is not the flag")
    setflag(u1, E.FALSE)
    K.check(not bool(HG.ready(u1, now())), "HG: Boolean.FALSE is not the flag")
    setflag(u1)
    K.check(not bool(HG.ready(u1, now())) and HG.SEEN.get(u1) is not None, "HG: the flag first seen = not yet (the +1 s starts)")
    age(HG.SEEN, u1, 1000)
    K.check(bool(HG.ready(u1, now())), "HG: the flag seen for 1 s = ready")
    setflag(u1, None)
    K.check(not bool(HG.ready(u1, now())) and HG.SEEN.get(u1) is None, "HG: the flag gone again = not ready, the 1 s starts over")
    age(HG.SINCE, u1, 11000)
    K.check(not bool(HG.ready(u1, now())), "HG: 11 s after the connect without the flag = not ready")
    age(HG.SINCE, u1, 12000)
    K.check(bool(HG.ready(u1, now())), "HG: 12 s after the connect without the flag = ready (the fallback)")
    old = P1.pr
    P1n = E.mkp(u1, "GateOne")                          # a fast reconnect: a NEW PlayerRef before the old quit
    HG.connect(P1n.pr)
    HG.quit(old)
    K.check(HG.SINCE.get(u1) is not None and not bool(HG.ready(u1, now())), "HG: the OLD connection's quit leaves the new connection's clock")
    HG.quit(P1n.pr)
    K.check(HG.SINCE.get(u1) is None and HG.SEEN.get(u1) is None and HG.CONN.get(u1) is None, "HG: its own quit clears it")
    # ---------------------------------------------------------------- OPEN: the first-join OpenTask
    P2 = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-0000000001a2"), "GateTwo")
    u2 = P2.pr.getUuid()
    HG.connect(P2.pr)

    def task(P):
        t = OT(P.pr)
        t.tries = 1000000          # one poll per run(): again() schedules nothing
        return t

    def poll(t, P, wu=None):
        t.onWorld = True
        t.hopWorld = wu or E.W1U
        t.run()
        E.pump(P)

    def pages(P):
        return [k for k in E.kinds(P) if k == "CustomPage"]
    t2 = task(P2)
    for _ in range(4):
        poll(t2, P2)
    K.check(E.pg(P2) is None and int(t2.calm) == 0 and len(pages(P2)) == 0, "OPEN: gate closed -> 4 polls open nothing, the calm count never starts")
    setflag(u2)
    poll(t2, P2)
    K.check(E.pg(P2) is None, "OPEN: the flag just seen -> still waiting (the +1 s)")
    age(HG.SEEN, u2, 1000)
    poll(t2, P2)
    K.check(E.pg(P2) is None and int(t2.calm) == 1, "OPEN: the gate open -> the first calm poll (no page yet)")
    poll(t2, P2)
    pg2 = E.pg(P2)
    K.check(pg2 is not None and str(pg2.getClass().getName()) == PKG + "ProfilePage" and bool(pg2.first) and int(pg2.view) == 1,
            "OPEN: the second calm poll opens the Create Profile page (first, view 1)")
    K.check(len(pages(P2)) == 1 and not bool(pg2.redrawQueued), "OPEN: ONE page packet; built after the gate = no redraw queued")
    K.check("1" == str(S.load(u2).getProperty("prompted")), "OPEN: prompted marked")
    for _ in range(3):
        poll(t2, P2)
    K.check(len(pages(P2)) == 1 and E.same(E.pg(P2), pg2), "OPEN: 3 more polls never open a second page")
    # the 12 s fallback (no SkyyHud / no flag)
    P3 = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-0000000001a3"), "GateThree")
    u3 = P3.pr.getUuid()
    HG.connect(P3.pr)
    t3 = task(P3)
    for _ in range(3):
        poll(t3, P3)
    K.check(E.pg(P3) is None, "OPEN: no flag, 0 s -> nothing")
    age(HG.SINCE, u3, 12000)
    poll(t3, P3)
    poll(t3, P3)
    K.check(E.pg(P3) is not None and bool(E.pg(P3).first) and len(pages(P3)) == 1, "OPEN: no flag after 12 s -> the page opens anyway (the fallback)")
    # another page open: it waits (and never replaces it), then opens once that page is gone
    P4 = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-0000000001a4"), "GateFour")
    HG.connect(P4.pr)
    setflag(P4.pr.getUuid())
    HG.ready(P4.pr.getUuid(), now())
    age(HG.SEEN, P4.pr.getUuid(), 2000)
    other = E.U.allocateInstance(JClass("com.hypixel.hytale.server.core.entity.entities.player.pages.RespawnPage").class_)     # another page
    PMc = JClass("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager")
    HT.jf(PMc.class_, "legacyCustomPage").set(P4.pm, other)
    t4 = task(P4)
    for _ in range(3):
        poll(t4, P4)
    K.check(E.same(E.pg(P4), other) and len(pages(P4)) == 0, "OPEN: another page open -> it waits, never replaces it")
    HT.jf(PMc.class_, "legacyCustomPage").set(P4.pm, None)
    for _ in range(3):
        poll(t4, P4)
    K.check(E.pg(P4) is not None and len(pages(P4)) == 1, "OPEN: that page closed -> ONE first-profile page")
    # ---------------------------------------------------------------- REDRAW
    # (a) END TO END: /profiles opened before the gate queues ONE PageRedraw on the engine's real SCHEDULED_EXECUTOR; it polls every
    #     0.5 s, hops to the player's world once the gate opens, and that world task re-sends the same page in full once
    import time
    NONE_PAGE = JClass("com.hypixel.hytale.protocol.packets.interface_.Page").valueOf("None")

    def wait_queued(w, name, secs=4.0):
        t0 = time.time()
        while time.time() - t0 < secs:
            if name in E.queued(w):
                return True
            time.sleep(0.05)
        return False
    P5 = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-0000000001a5"), "GateFive")
    u5 = P5.pr.getUuid()
    HG.connect(P5.pr)
    S.create(u5, "1", "Fig", "Priest", True)
    err = PG.open(P5.st, P5.ref, P5.pr, 0)
    E.pump(P5)
    pg5 = E.pg(P5)
    K.check(err is None and pg5 is not None and bool(pg5.redrawQueued), "REDRAW: /profiles opened before the gate -> a redraw queued (%s)" % err)
    n0 = len(pages(P5))
    pg5.redraw()                        # a click rebuilds it: build() runs again, still before the gate
    E.pump(P5)
    n0 = len(pages(P5))
    time.sleep(1.3)
    K.check(E.queued(E.W1) == [] and len(pages(P5)) == n0, "REDRAW: gate closed -> the queued redraw only polls (no world task, no packet)")
    r0 = int(PR_.REDRAWS)
    setflag(u5)
    HG.ready(u5, now())
    age(HG.SEEN, u5, 1000)
    K.check(wait_queued(E.W1, "PageRedraw") and E.queued(E.W1) == ["PageRedraw"],
            "REDRAW: gate open -> ONE redraw hops to the player's world (%s; a click's second build queued no second one)" % E.queued(E.W1))
    E.run_world(E.W1)
    E.pump(P5)
    K.check(len(pages(P5)) == n0 + 1 and int(PR_.REDRAWS) == r0 + 1 and E.same(E.pg(P5), pg5),
            "REDRAW: the same page re-sent in full ONCE (one CustomPage packet, REDRAWS + 1, still that page)")
    time.sleep(1.3)
    K.check(E.queued(E.W1) == [] and int(PR_.REDRAWS) == r0 + 1, "REDRAW: nothing more afterwards (the re-send's own build queued no redraw)")
    # (b) a page built after the gate queues none
    P5.pm.setPage(P5.ref, P5.st, NONE_PAGE)
    E.pump(P5)
    PG.open(P5.st, P5.ref, P5.pr, 0)
    E.pump(P5)
    pgA = E.pg(P5)
    K.check(pgA is not None and not bool(pgA.redrawQueued), "REDRAW: a page built after the gate queues no redraw")
    # (c) PageRedraw by hand (one poll per run, nothing scheduled): gate closed = nothing; a page no longer open = never redrawn
    setflag(u5, None)
    HG.SINCE.put(u5, Long.valueOf(JLong(now())))
    rd = PR_(P5.pr, pgA)
    rd.tries = 1000000
    n1 = len(pages(P5))
    for _ in range(3):
        rd.run()
    K.check(E.queued(E.W1) == [] and len(pages(P5)) == n1, "REDRAW: by hand, gate closed -> nothing (no world task, no packet)")
    setflag(u5)
    HG.ready(u5, now())
    age(HG.SEEN, u5, 1000)
    rd2 = PR_(P5.pr, pg5)               # pg5 is no longer the open page (pgA replaced it)
    rd2.tries = 1000000
    rd2.run()
    K.check(E.queued(E.W1) == ["PageRedraw"], "REDRAW: by hand, gate open -> it hops to the player's world")
    E.run_world(E.W1)
    E.pump(P5)
    K.check(len(pages(P5)) == n1 and E.same(E.pg(P5), pgA), "REDRAW: a page that is no longer the open one is never redrawn")
    P5.pm.setPage(P5.ref, P5.st, NONE_PAGE)
    E.pump(P5)
    rd3 = PR_(P5.pr, pgA)
    rd3.tries = 1000000
    n2 = len(pages(P5))
    rd3.run()
    E.run_world(E.W1)
    E.pump(P5)
    K.check(len(pages(P5)) == n2 and E.pg(P5) is None, "REDRAW: a closed page is never re-opened by the redraw")
    # ---------------------------------------------------------------- CALLS (bytecode)
    g = PW.calls(jar)
    K.check(PKG + "HudGate.connect" in g.get("ProfConnect.accept", set()) and PKG + "HudGate.quit" in g.get("ProfQuit.accept", set()),
            "CALLS: PlayerConnectEvent -> HudGate.connect, PlayerDisconnectEvent -> HudGate.quit")
    K.check(all(PKG + "HudGate.ready" in g.get(k, set()) for k in ("ReadyTask.run", "OpenTask.run", "ProfilePage.build", "PageRedraw.run")),
            "CALLS: ReadyTask / OpenTask / ProfilePage.build / PageRedraw ask HudGate.ready")
    K.check(PKG + "PageRedraw.<init>" in g.get("ProfilePage.build", set()) and PKG + "PageRedraw.later" in g.get("ProfilePage.build", set()),
            "CALLS: ProfilePage.build queues the PageRedraw")
    K.check(PKG + "ProfilePage.redraw" in g.get("PageRedraw.run", set())
            and ({PKG + "ProfilePage.rebuild", "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage.rebuild"} & g.get("ProfilePage.redraw", set())),
            "CALLS: PageRedraw re-sends through ProfilePage.redraw = the engine's (protected) CustomUIPage.rebuild")
    K.check(sum(1 for k, v in g.items() if PKG + "PageRedraw.<init>" in v) == 1, "CALLS: ONE place makes a PageRedraw")
    K.save()


def _old(name):
    def f(out, jar, scratch, home):
        T = t14()
        fn = {"hub": T.run_hub, "rb": T.T13.run_rb, "exec": T.T12.run_exec, "live": T.T12.run_live}[name]
        fn(out, jar, scratch, home)
    return f


if __name__ == "__main__":
    HK.run(name="SkyyProfiles", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("gate", run_gate), ("hub", _old("hub")), ("rb", _old("rb"))], script=__file__)
