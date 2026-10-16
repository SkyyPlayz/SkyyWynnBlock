"""Harness for SkyyHud 0.3.30 (log fix: the minimap removal on a stopped world thread is skipped quietly; tools/hud_0_3_30_patch.py).
Build first:  python tools/hud_0_3_30_patch.py && python SkyyHud/build_skyyhud_0.3.30.py

    python SkyyHud/test_skyyhud_0.3.30.py [--jar SkyyHud-0.3.30.jar] [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py, -Xverify:all):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.29 -> 0.3.30: Minimap +m stopped, ~m detach; the version texts; non-class entries: the manifest
  D    detach   EXECUTED on the real Minimap.detach with a REAL engine World whose thread no longer accepts tasks (acceptingTasks false:
                World.execute throws the engine's own SkipSentryException(IllegalThreadStateException), as at the 2026-10-16 shutdown):
                no WARN, no error counted, the HUD marked ended / dropped from the session. Control: a world that fails in another way
                (an NPE) is still logged once (WARN) and counted. Minimap.stopped on built exceptions (wrapped, bare, message only, other).
  AA   audit    the engine-access audit
Exit code 1 on any failure.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

VERSION, PREV = "0.3.30", "0.3.29"
PKG = "com.skyy.hud."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyHud-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyHud-%s.jar" % PREV)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "logfix", "h")))
ADDED = []
EXPECT = {
    "Minimap": ["+m stopped", "~m detach"],
    # the version string (the kit's header / export)
    "CfgRows": ["~m header"], "CfgFn": ["~m opExport"], "SkyyHudPlugin": ["~m setup"],
}


def run_detach(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    BK = JClass("com.hypixel.hytale.logger.backend.HytaleLoggerBackend")
    cap = JClass("java.util.concurrent.CopyOnWriteArrayList")()
    BK.subscribe(cap)
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)
    MM, Sess, Hud = JClass(PKG + "Minimap"), JClass(PKG + "MmSess"), JClass(PKG + "MmHud")
    MM.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyHud")
    W = JClass("com.hypixel.hytale.server.core.universe.world.World")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    Store = JClass("com.hypixel.hytale.component.Store")
    AB = JClass("java.util.concurrent.atomic.AtomicBoolean")
    ITS = JClass("java.lang.IllegalThreadStateException")
    SSE = JClass("com.hypixel.hytale.logger.sentry.SkipSentryException")
    RTE = JClass("java.lang.RuntimeException")

    def logs():
        o = [(str(r.getLevel()), str(r.getMessage())) for r in cap if "[SkyyHud]" in str(r.getMessage())]
        cap.clear()
        return o

    def world(accepting):
        w = U.allocateInstance(W.class_)
        if accepting is not None:
            f = W.class_.getDeclaredField("acceptingTasks")
            f.setAccessible(True)
            f.set(w, AB(accepting))
            # TickingThread.currentRun (World.execute reads it before the acceptingTasks test): no run = the thread has stopped
            g = W.class_.getSuperclass().getDeclaredField("currentRun")
            g.setAccessible(True)
            g.set(w, JClass("java.util.concurrent.atomic.AtomicReference")())
        return w

    def sess(w):
        pr = U.allocateInstance(PRef.class_)
        s = Sess(pr)
        s.world = w
        s.store = U.allocateInstance(Store.class_)
        h = U.allocateInstance(Hud.class_)
        s.hud = h
        s.posKnown = True
        return s, h

    # ============================================================== D1 Minimap.stopped
    msg = "World thread is not accepting tasks: skyy-island-test, null"
    K.check(bool(MM.stopped(SSE(ITS(msg)))), "D1 SkipSentryException(IllegalThreadStateException) = stopped (the live 2026-10-16 shape)")
    K.check(bool(MM.stopped(ITS("x"))), "D1 a bare IllegalThreadStateException = stopped")
    K.check(bool(MM.stopped(RTE(msg))), "D1 the 'not accepting tasks' text alone = stopped")
    K.check(not bool(MM.stopped(RTE("boom"))) and not bool(MM.stopped(JClass("java.lang.IllegalStateException")("other"))) and not bool(MM.stopped(None)),
            "D1 any other failure (or none) is NOT 'stopped'")

    # ============================================================== D2 the real engine World, thread stopped
    w = world(False)
    thrown = None
    try:
        w.execute(JClass(PKG + "MmDetach")(None, None, None))
    except Exception as e:
        thrown = e
    K.check(thrown is not None and bool(MM.stopped(thrown)), "D2 the real World.execute on a stopped world thread throws what stopped() recognises: %s" % thrown)
    logs()
    e0 = int(MM.ERRORS)
    s, h = sess(w)
    MM.detach(s, "gone")
    lg = logs()
    K.check(not lg, "D2 Minimap.detach on a stopped world: no WARN (no log line at all): %s" % lg)
    K.eq(int(MM.ERRORS), e0, "D2 ... and no error counted")
    K.check(s.hud is None and bool(h.ended) and not bool(s.posKnown), "D2 ... the HUD is ended and dropped from the session as before")
    s2, _h2 = sess(world(False))
    MM.detach(s2, "gone")
    K.check(not logs() and int(MM.ERRORS) == e0, "D2 a second player at the same shutdown: still nothing")

    # ============================================================== D3 control: another failure is still logged
    s3, _h3 = sess(world(None))    # acceptingTasks null -> World.execute throws an NPE (not a stopped thread)
    MM.detach(s3, "gone")
    lg = logs()
    K.check(len(lg) == 1 and lg[0][0] == "WARNING" and "reaching the world thread to remove the minimap failed" in lg[0][1] and int(MM.ERRORS) == e0 + 1,
            "D3 control: any other failure is logged once (WARN) and counted as before: %s" % [(l, m[:90]) for l, m in lg])
    s4, _h4 = sess(world(None))
    MM.detach(s4, "gone")
    K.check(not logs() and int(MM.ERRORS) == e0 + 2, "D3 ... the second one is only counted (logged once, as before)")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyHud", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("detach", run_detach)], script=__file__)
