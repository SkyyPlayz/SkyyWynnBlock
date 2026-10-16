"""Harness for SkyyHud 0.3.27 (the first-join page fix: the minimap's statics + its ONE RequestCommonAssetsRebuild at connect, never
under an open custom page, and the skyy.bridge flag hud:assets:ready:<uuid>; tools/hud_0_3_27_patch.py). Build first:
python tools/hud_0_3_27_patch.py && python SkyyHud/build_skyyhud_0.3.27.py

    python SkyyHud/test_skyyhud_0.3.27.py [--jar SkyyHud-0.3.27.jar] [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py; the engine stand-ins of tools/hub_tab_kit.stage = the SkyyMenu 0.3.19 harness's: the REAL
PageManager, worlds whose execute() queues, the Universe, players, -Xverify:all):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.26 -> 0.3.27: + MmRebuild; Minimap statics / handle / step / hello / quit / shutdown + the flag / rebuild methods
                + FLAGGED; MmSess's 5 rebuild fields; the version texts only; non-class entries: the manifest
  R27  EXECUTED (Minimap's own code, its thread parked - every tick by hand):
       CONNECT  hello() of a player with no entity in a world yet: one "hello" request; the next tick sends the 47 statics (14 masks,
                32 arrows, the dark picture) THEN exactly one RequestCommonAssetsRebuild straight from the minimap thread (no world
                task), and hud:assets:ready:<uuid> = Boolean.TRUE; a later statics() (the first attach) sends nothing more
       WORLD    a player already in a world with no page: the pictures go at the tick, the rebuild waits for ONE world-thread check
                (MmRebuild queued on THAT world); running the world writes it + the flag
       PAGE     a custom page open: the check writes nothing (no flag; one log line "has a page open"); re-checked at later ticks
                (still nothing); the page closed -> the next tick's check writes exactly ONE rebuild + the flag ("after the open page
                closed"); more ticks: no second rebuild
       ATTACH   (review fix) the minimap switched on while a page is open: attach() shows NO HUD while the rebuild waits (pending,
                no MmAttach, its no-stream log flag untouched), still none at later ticks; the page closed -> the rebuild goes, the next
                tick's step() re-runs the attach -> the HUD (MmAttach queued)
       STALE    (review fix) a world-thread check whose world stopped before it ran: no second check within 3 s, a new one after 3 s
       NOMAP    BetterMap missing (BM 2): hello() flags at once (no session, no request); minimap off in Server Setup: flagged at once,
                the session exists, no "hello" request, no picture
       QUIT     a disconnect removes the flag; a fast reconnect: the new connection starts unflagged, the OLD connection's quit leaves
                the new flag; a foreign value under the key is never removed (remove(key, TRUE) only)
       STOP     shutdown() removes every flag this jar put (and nothing else)
       CALLS    bytecode: MmConnect -> Minimap.hello, MmQuit -> Minimap.quit, MmRebuild -> Minimap.rebuildCheck, the plugin's shutdown ->
                Minimap.shutdown; ONE writeNoCache(RequestCommonAssetsRebuild) in the jar (rebuildSend)
  AA   audit    the engine-access audit
Not testable without the game (UNVERIFIED): the client repacking its atlas BEFORE the profile page opens on a real join.
Exit code 1 on any failure.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import hub_tab_kit as HT
import perfworld_kit as PW

VERSION = "0.3.27"
PKG = "com.skyy.hud."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyHud-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyHud-0.3.26.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "hud0327", "h")))
ADDED = ["MmRebuild"]
EXPECT = {
    "Minimap": ["+f FLAGGED", "+m flag", "+m flagKey", "+m rebuild", "+m rebuildCheck", "+m rebuildSend", "+m unflag", "+m unflagAll",
                "+m unflagFor", "+m unflagKey", "~<clinit>", "~m attach", "~m handle", "~m hello", "~m quit", "~m shutdown", "~m statics", "~m step"],
    "MmSess": ["+f rbAsk", "+f rbAskAt", "+f rbAt", "+f rbDone", "+f rbNext", "+f rbWaitLogged"],
    # the version string (the kit's header / export, the ready line)
    "CfgRows": ["~m header"], "CfgFn": ["~m opExport"], "SkyyHudPlugin": ["~m setup"],
}
KEY = "hud:assets:ready:"


def run_r27(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    H = lambda n: JClass(PKG + n)
    MM, MC = H("Minimap"), H("MmCfg")
    TRUE = E.TRUE
    STPE = JClass("java.util.concurrent.ScheduledThreadPoolExecutor")
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    PMc = JClass("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager")
    HOLD = JClass("com.hypixel.hytale.component.Holder")
    MM.EXEC = STPE(1)            # parked: ensureExec() starts no thread, every tick runs here by hand
    MC.BM = 1
    MC.ENABLED = True
    br = E.bridge

    def kinds(P, i0=0):
        return [str(p.getClass().getSimpleName()) for p in E.sent(P)[i0:]]

    def tail():
        return [str(x) for x in MM.tail()]

    def tick(n=1):
        for _ in range(n):
            MM.tick()

    def flagged(P):
        return E.same(br.get(KEY + str(P.pr.getUuid())), TRUE)

    def sess(P):
        return MM.SESS.get(P.pr.getUuid())

    def outside(P):
        """a player connecting: no entity in a world yet (only the holder)"""
        HT.jf(PRc.class_, "entity").set(P.pr, None)
        HT.jf(PRc.class_, "holder").set(P.pr, E.U.allocateInstance(HOLD.class_))

    def statics_ok(ks, what):
        ni = ks.count("AssetInitialize")
        nf = ks.count("AssetFinalize")
        K.check(ni == 47 and nf == 47, "%s: the 47 statics (14 masks + 32 arrows + dark) were sent (%d / %d)" % (what, ni, nf))
    # ---------------------------------------------------------------- CONNECT: no entity in a world yet
    P1 = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-00000000a271"), "HudConnect")
    outside(P1)
    MM.hello(P1.pr)
    K.check(int(MM.REQ.size()) == 1 and str(MM.REQ.peek().kind) == "hello", "CONNECT: hello() queues ONE hello request")
    K.check(not flagged(P1) and len(kinds(P1)) == 0, "CONNECT: nothing sent and no flag before the minimap tick")
    tick()
    ks = kinds(P1)
    statics_ok(ks, "CONNECT")
    K.check(ks.count("RequestCommonAssetsRebuild") == 1 and ks[-1] == "RequestCommonAssetsRebuild",
            "CONNECT: exactly ONE RequestCommonAssetsRebuild, AFTER every picture (%d, last %s)" % (ks.count("RequestCommonAssetsRebuild"), ks[-1:]))
    K.check(E.queued(E.W1) == [], "CONNECT: no world task (no entity = no page can be open)")
    K.check(flagged(P1) and E.same(MM.FLAGGED.get(P1.pr.getUuid()), P1.pr), "CONNECT: hud:assets:ready:<uuid> = Boolean.TRUE (FLAGGED = this connection)")
    s1 = sess(P1)
    K.check(s1 is not None and bool(s1.rbDone) and int(s1.rbAt) > 0, "CONNECT: the session's rebuild is marked done")
    K.check(any("at connect, before the player is in a world" in t for t in tail()), "CONNECT: one log line names it")
    n0 = len(kinds(P1))
    MM.statics(s1)
    tick(3)
    K.check(len(kinds(P1)) == n0, "CONNECT: a later statics() (the first attach) and more ticks send nothing more (%d new)" % (len(kinds(P1)) - n0))
    # ---------------------------------------------------------------- WORLD: in a world, no page open
    P2 = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-00000000a272"), "HudWorld")
    MM.hello(P2.pr)
    tick()
    ks = kinds(P2)
    statics_ok(ks, "WORLD")
    K.check("RequestCommonAssetsRebuild" not in ks and not flagged(P2), "WORLD: the pictures went, the rebuild waits for the world-thread check")
    K.check(E.queued(E.W1) == ["MmRebuild"], "WORLD: ONE MmRebuild queued on the player's world (%s)" % E.queued(E.W1))
    tick(2)
    K.check(E.queued(E.W1) == ["MmRebuild"], "WORLD: a check on its way is never doubled by later ticks (%s)" % E.queued(E.W1))
    E.run_world(E.W1)
    ks = kinds(P2)
    K.check(ks.count("RequestCommonAssetsRebuild") == 1 and flagged(P2), "WORLD: the check found no page -> ONE rebuild + the flag")
    tick(3)
    E.run_world(E.W1)
    K.check(kinds(P2).count("RequestCommonAssetsRebuild") == 1 and E.queued(E.W1) == [], "WORLD: no second rebuild, no more checks")
    # ---------------------------------------------------------------- PAGE: a custom page open at that moment
    P3 = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-00000000a273"), "HudPage")
    pg = E.U.allocateInstance(H("WidgetsPage").class_)
    HT.jf(PMc.class_, "legacyCustomPage").set(P3.pm, pg)
    K.check(E.same(P3.pm.getCustomPage(), pg), "PAGE: the stand-in page is the open custom page")
    MM.hello(P3.pr)
    tick()
    E.run_world(E.W1)
    s3 = sess(P3)
    K.check("RequestCommonAssetsRebuild" not in kinds(P3) and not flagged(P3) and bool(s3.rbWaitLogged),
            "PAGE: a page is open -> no rebuild, no flag")
    K.check(sum(1 for t in tail() if "HudPage has a page open (WidgetsPage)" in t) == 1, "PAGE: one log line says it waits")
    for _ in range(3):
        s3.rbNext = 0
        tick()
        E.run_world(E.W1)
    K.check("RequestCommonAssetsRebuild" not in kinds(P3) and not flagged(P3), "PAGE: re-checked 3 times while the page stays open: still nothing")
    K.check(sum(1 for t in tail() if "HudPage has a page open" in t) == 1, "PAGE: ... and logged only once")
    HT.jf(PMc.class_, "legacyCustomPage").set(P3.pm, None)
    s3.rbNext = 0
    tick()
    E.run_world(E.W1)
    K.check(kinds(P3).count("RequestCommonAssetsRebuild") == 1 and flagged(P3), "PAGE: the page closed -> ONE rebuild + the flag")
    K.check(any("HudPage's minimap pictures + the one picture rebuild sent after the open page closed" in t for t in tail()), "PAGE: logged 'after the open page closed'")
    for _ in range(3):
        s3.rbNext = 0
        tick()
        E.run_world(E.W1)
    K.check(kinds(P3).count("RequestCommonAssetsRebuild") == 1, "PAGE: no second rebuild afterwards")
    # a player who moved to another world before the check ran: the check never reads the other world's store, it retries
    P3b = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-00000000a27b"), "HudMove")
    MM.hello(P3b.pr)
    tick()
    ESc = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")

    def move(P, w, wu):
        HT.jf(PRc.class_, "worldUuid").set(P.pr, wu)
        HT.jf(ESc.class_, "world").set(P.st.getExternalData(), w)
    move(P3b, E.W2, E.W2U)
    E.run_world(E.W1)
    K.check("RequestCommonAssetsRebuild" not in kinds(P3b) and not flagged(P3b) and not bool(sess(P3b).rbAsk),
            "PAGE: the store is not the checking world's (moved on) -> no rebuild yet, a retry is allowed")
    sess(P3b).rbNext = 0
    tick()
    K.check(E.queued(E.W2) == ["MmRebuild"], "PAGE: the retry asks the player's NEW world thread (%s)" % E.queued(E.W2))
    move(P3b, E.W1, E.W1U)
    E.run_world(E.W2)
    K.check("RequestCommonAssetsRebuild" not in kinds(P3b), "PAGE: moved back before that check ran -> again no rebuild from the wrong world")
    sess(P3b).rbNext = 0
    tick()
    E.run_world(E.W1)
    K.check(kinds(P3b).count("RequestCommonAssetsRebuild") == 1 and flagged(P3b), "PAGE: back in its world -> ONE rebuild + the flag")
    # ---------------------------------------------------------------- ATTACH (review fix): no HUD while the rebuild waits
    import time
    LS, HC = H("LayoutStore"), H("HudCfg")
    hdir = os.path.join(scratch, "hudhome")
    os.makedirs(os.path.join(hdir, "layouts"), exist_ok=True)
    LS.DIR = E.Paths.get(os.path.join(hdir, "layouts"))
    LS.CACHE.clear()
    HC.FILE = E.Paths.get(os.path.join(hdir, "config.properties"))
    HC.load()
    WMMc = JClass("com.hypixel.hytale.server.core.universe.world.worldmap.WorldMapManager")
    WMSc = JClass("com.hypixel.hytale.server.core.universe.world.worldmap.WorldMapSettings")
    UWMSc = JClass("com.hypixel.hytale.protocol.packets.worldmap.UpdateWorldMapSettings")
    L2O = JClass("com.hypixel.fastutil.longs.Long2ObjectConcurrentHashMap")
    from jpype import JFloat, JInt
    wmm = E.U.allocateInstance(WMMc.class_)
    HT.jf(WMMc.class_, "images").set(wmm, L2O())
    sp = UWMSc()
    sp.enabled = True
    HT.jf(WMMc.class_, "worldMapSettings").set(wmm, WMSc(None, JFloat(0.5), JFloat(1.0), JInt(1), JInt(64), sp))
    HT.jf(JClass("com.hypixel.hytale.server.core.universe.world.World").class_, "worldMapManager").set(E.W1, wmm)
    P7 = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-00000000a277"), "HudAttach")
    K.check(LS.get(P7.pr.getUuid()).get("Minimap") is not None and bool(LS.get(P7.pr.getUuid()).get("Minimap").en), "ATTACH: the default layout has the minimap on")
    pg7 = E.U.allocateInstance(H("WidgetsPage").class_)
    HT.jf(PMc.class_, "legacyCustomPage").set(P7.pm, pg7)
    MM.hello(P7.pr)
    tick()
    E.run_world(E.W1)
    s7 = sess(P7)
    s7.world, s7.store, s7.wuuid, s7.wname, s7.realSeen = E.W1, P7.st, E.W1U, "harness_home", True
    s7.rbNext = 0
    MM.attach(s7, JClass("java.lang.System").currentTimeMillis(), True)
    K.check(s7.hud is None and bool(s7.pending) and not bool(s7.pendLogged) and "MmAttach" not in E.queued(E.W1) and not bool(s7.rbDone),
            "ATTACH: a page open, the rebuild waits -> attach() shows NO HUD (pending, no MmAttach; queued %s)" % E.queued(E.W1))
    for _ in range(3):
        s7.rbNext = 0
        tick()
        E.run_world(E.W1)
    K.check(s7.hud is None and "RequestCommonAssetsRebuild" not in kinds(P7), "ATTACH: 3 more ticks with the page open: still no HUD, no rebuild")
    HT.jf(PMc.class_, "legacyCustomPage").set(P7.pm, None)
    s7.rbNext = 0
    tick()
    K.check(E.queued(E.W1) == ["MmRebuild"] and s7.hud is None, "ATTACH: the page closed -> the check is asked first (%s), still no HUD" % E.queued(E.W1))
    E.run_world(E.W1)
    K.check(kinds(P7).count("RequestCommonAssetsRebuild") == 1 and flagged(P7), "ATTACH: ... the rebuild goes + the flag")
    tick()
    K.check(s7.hud is not None and "MmAttach" in E.queued(E.W1) and not bool(s7.pending),
            "ATTACH: the next tick re-runs the attach -> the HUD (MmAttach queued: %s)" % E.queued(E.W1))
    K.check(kinds(P7).count("RequestCommonAssetsRebuild") == 1, "ATTACH: still ONE rebuild")
    E.W1.tasks.clear()
    # ---------------------------------------------------------------- STALE (review fix): a check whose world stopped
    P8 = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-00000000a278"), "HudStale")
    MM.hello(P8.pr)
    tick()
    s8 = sess(P8)
    K.check(E.queued(E.W1) == ["MmRebuild"] and bool(s8.rbAsk) and int(s8.rbAskAt) > 0, "STALE: a check is asked (rbAskAt set)")
    E.W1.tasks.clear()                                   # the world stopped: the task never runs
    tick(3)
    K.check(E.queued(E.W1) == [] and bool(s8.rbAsk), "STALE: within 3 s no second check")
    s8.rbAskAt = int(s8.rbAskAt) - 3001
    tick()
    K.check(E.queued(E.W1) == ["MmRebuild"], "STALE: after 3 s the check is asked again (%s)" % E.queued(E.W1))
    E.run_world(E.W1)
    K.check(kinds(P8).count("RequestCommonAssetsRebuild") == 1 and flagged(P8) and not bool(s8.rbAsk), "STALE: ... it runs: ONE rebuild + the flag")
    # ---------------------------------------------------------------- NOMAP: no pictures will come -> flagged at once
    MC.BM = 2
    P4 = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-00000000a274"), "HudNoMap")
    MM.REQ.clear()
    MM.hello(P4.pr)
    K.check(flagged(P4) and sess(P4) is None and int(MM.REQ.size()) == 0 and len(kinds(P4)) == 0,
            "NOMAP: BetterMap missing -> flagged at once, no session, no request, nothing sent")
    MM.quit(P4.pr)
    K.check(br.get(KEY + str(P4.pr.getUuid())) is None, "NOMAP: the disconnect removes it")
    MC.BM = 1
    MC.ENABLED = False
    P5 = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-00000000a275"), "HudOff")
    MM.REQ.clear()
    MM.hello(P5.pr)
    K.check(flagged(P5) and sess(P5) is not None and int(MM.REQ.size()) == 0, "NOMAP: minimap off in Server Setup -> flagged at once, session kept, no hello request")
    tick(2)
    E.run_world(E.W1)
    K.check(len(kinds(P5)) == 0, "NOMAP: ... and no picture / rebuild goes")
    MC.ENABLED = True
    # ---------------------------------------------------------------- QUIT: disconnects, fast reconnects, foreign values
    MM.quit(P1.pr)
    tick()
    K.check(br.get(KEY + str(P1.pr.getUuid())) is None and MM.FLAGGED.get(P1.pr.getUuid()) is None, "QUIT: a disconnect removes the flag")
    old = P2.pr
    K.check(flagged(P2), "QUIT: P2 is flagged before its reconnect")
    P2n = E.mkp(P2.pr.getUuid(), "HudWorld")           # the same player, a NEW connection (PlayerRef) before the old quit
    outside(P2n)
    MM.hello(P2n.pr)
    K.check(br.get(KEY + str(P2n.pr.getUuid())) is None, "QUIT: the new connection starts unflagged (the old flag is gone)")
    MM.quit(old)
    tick()
    ks = kinds(P2n)
    K.check(ks.count("RequestCommonAssetsRebuild") == 1 and flagged(P2n) and E.same(MM.FLAGGED.get(P2n.pr.getUuid()), P2n.pr),
            "QUIT: the new connection got its own pictures + ONE rebuild and its flag")
    MM.quit(old)
    tick()
    K.check(flagged(P2n), "QUIT: the OLD connection's quit leaves the new connection's flag")
    P6 = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-00000000a276"), "HudForeign")
    MC.BM = 2
    MM.hello(P6.pr)
    MC.BM = 1
    br.put(KEY + str(P6.pr.getUuid()), "someone else's")
    MM.quit(P6.pr)
    K.check(str(br.get(KEY + str(P6.pr.getUuid()))) == "someone else's", "QUIT: a foreign value under the key is never removed")
    br.remove(KEY + str(P6.pr.getUuid()))
    # ---------------------------------------------------------------- STOP: shutdown removes every flag of this jar
    K.check(flagged(P2n) and flagged(P3) and flagged(P5) and flagged(P7) and flagged(P8), "STOP: five flags are up before the shutdown")
    br.put(KEY + "00000000-0000-0000-0000-0000000000ff", TRUE)          # not ours (never in FLAGGED)
    MM.shutdown()
    K.check(not flagged(P2n) and not flagged(P3) and not flagged(P5) and not flagged(P7) and not flagged(P8) and int(MM.FLAGGED.size()) == 0, "STOP: shutdown removed every flag this jar put")
    K.check(E.same(br.get(KEY + "00000000-0000-0000-0000-0000000000ff"), TRUE), "STOP: ... and left a key it never put")
    # ---------------------------------------------------------------- CALLS (bytecode)
    g = PW.calls(jar)
    K.check(PKG + "Minimap.hello" in g.get("MmConnect.accept", set()) and PKG + "Minimap.quit" in g.get("MmQuit.accept", set()),
            "CALLS: PlayerConnectEvent -> Minimap.hello, PlayerDisconnectEvent -> Minimap.quit")
    K.check(PKG + "Minimap.rebuildCheck" in g.get("MmRebuild.run", set()), "CALLS: MmRebuild.run -> Minimap.rebuildCheck")
    K.check(PKG + "Minimap.shutdown" in g.get("SkyyHudPlugin.shutdown", set()) and PKG + "Minimap.unflagAll" in g.get("Minimap.shutdown", set()),
            "CALLS: the plugin's shutdown -> Minimap.shutdown -> unflagAll")
    K.check(PKG + "Minimap.rebuild" in g.get("Minimap.statics", set()) and PKG + "Minimap.rebuild" in g.get("Minimap.step", set())
            and PKG + "Minimap.statics" in g.get("Minimap.attach", set()) and PKG + "Minimap.statics" in g.get("Minimap.handle", set()),
            "CALLS: statics() at the hello request and the first attach, the rebuild through rebuild() (+ the step retry)")
    writers = sorted(k for k, v in g.items() if "com.hypixel.hytale.protocol.packets.setup.RequestCommonAssetsRebuild.<init>" in v)
    K.check(writers == ["Minimap.rebuildSend"], "CALLS: ONE place builds a RequestCommonAssetsRebuild: %s" % writers)
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyHud", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("r27", run_r27)], script=__file__)
