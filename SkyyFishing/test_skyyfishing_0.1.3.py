"""Harness for SkyyFishing 0.1.3 (lag fixes: FishTick early-out, no per-tick allocation, rig cache, saves on SkyyFishing-IO, lock-free
bridge; tools/fishing_0_1_3_patch.py). Build first: python tools/fishing_0_1_3_patch.py && python SkyyFishing/build_skyyfishing_0.1.3.py

    python SkyyFishing/test_skyyfishing_0.1.3.py [--keep]

Phases (each a fresh child JVM, the game's JRE, TEMP / TMP in scratch; tools/harness_kit.py + tools/perfworld_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.2 -> 0.1.3: exactly the planned members differ (+ FishSeen, FishIO); every non-class entry identical but manifest.json
  X  exec     EVERY NEW CODE PATH (-Xverify:all) through the FishApi seam (a counting stand-in): bridge0 / bridge; static: FishTick.tick
              makes no FishCtx (ctxOf), kick hands FishGiveTask a copy; ctxOf = the player's ONE context, refilled; an IDLE player
              (no rod, no line) over 200 ticks: 200 held() reads and nothing else per tick - no clicked(), no heldSlot(), the reel read
              ONCE (then known 0), no rig parse, no later() (= no world hop), IDLE +200; the epoch watch every 10 ticks still runs
              (a profile switch while idle is recorded); a ROD in hand over 200 ticks: the rig parsed ONCE (same stack), the reel set to
              its look once and checked every 20 ticks; a new stack object (a rig change) = parsed again; putting the rod away = the
              reel look reset to 0 on the next tick; a line out = the full 0.1.2 path (clicked() read every tick); FishIO thread factory
              (SkyyFishing-IO, daemon) + FishStore.stopIO
  AA engine-access audit
Behaviour regression (the 0.1.2 engine child on this jar, 188 ok / 0 fail on 2026-10-13):
  python SkyyFishing/test_skyyfishing_0.1.2.py --mkfake <scratch>/fake --dir <scratch> --jar SkyyFishing/SkyyFishing-0.1.3.jar
  python SkyyFishing/test_skyyfishing_0.1.2.py --engine --out <scratch>/engine.json --dir <scratch> --jar SkyyFishing/SkyyFishing-0.1.3.jar
(never run that harness without --dir: its default scratch is another round's folder and it deletes it first).
Scratch: tools/dev/scratch/perfworld/fishing (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW

VERSION = "0.1.3"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyFishing-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyFishing-0.1.2.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "perfworld", "fishing")))
PKG = "com.skyy.fishing."

EXPECT = {
    "FishBridge": ["+f BRIDGE", "+m bridge0", "~m bridge"],
    "FishCore": ["+f IDLE", "+f RIGS", "+m seen", "+m ctxOf", "+m periodic", "~m tickPlayer", "~m kick", "~<clinit>"],
    "FishTick": ["~m tick"],
    "FishStore": ["+f IOX", "+m stopIO", "~<clinit>"],
    "SkyyFishingPlugin": ["~m setup", "~m shutdown"],
    # the config kit (tools/skyycfg.py, rebuilt): its lock-free CfgRows.bridge (2026-10-13) + the kit id / export header text
    "CfgRows": ["+f BRIDGE", "+m bridge0", "~m bridge", "~m header", "~<clinit>"],
    "CfgFn": ["~m opExport"],
    "FishCfg": ["~m applyAll", "~m seed"],   # the kit's default config text (a constant) changed with the kit
    "FishCmds": ["~m admin"],                # the /fishadmin stats line names the version
    "FishDefs": ["~<clinit>"],               # the junk names read from Assets.zip at build time are 0.7's ("Small Scrap Pile" ...)
    "FishEngApi": ["~m block"],              # the same two calls, now resolved to their 0.7 owner ChunkGrid (ChunkStore extends it)
}
ADDED = ["FishSeen", "FishIO"]


def make_api(st):
    from jpype import JImplements, JOverride

    @JImplements(PKG + "FishApi")
    class Api(object):
        def _n(self, k):
            st["calls"][k] = st["calls"].get(k, 0) + 1
        @JOverride
        def eye(self, c): self._n("eye"); return None
        @JOverride
        def feet(self, c): self._n("feet"); return None
        @JOverride
        def heldSlot(self, c): self._n("heldSlot"); return st["slot"]
        @JOverride
        def held(self, c): self._n("held"); return st["held"]
        @JOverride
        def clicked(self, c): self._n("clicked"); return False
        @JOverride
        def block(self, c, x, y, z): self._n("block"); return -1
        @JOverride
        def getReel(self, c): self._n("getReel"); return st["reel"]
        @JOverride
        def setReel(self, c, v): self._n("setReel"); st["reel"] = int(v)
        @JOverride
        def spawnBobber(self, c, s): self._n("spawnBobber")
        @JOverride
        def moveBobber(self, c, s, x, y, z): self._n("moveBobber")
        @JOverride
        def tagBobber(self, c, s, t): self._n("tagBobber")
        @JOverride
        def removeBobber(self, s): self._n("removeBobber")
        @JOverride
        def particle(self, c, i, x, y, z): self._n("particle")
        @JOverride
        def drawLine(self, c, pts, n, secs): self._n("drawLine")
        @JOverride
        def sound(self, c, i, x, y, z): self._n("sound")
        @JOverride
        def hudState(self, c, s, state, txt): self._n("hudState")
        @JOverride
        def hudSet(self, c, s, bar, t, cps): self._n("hudSet")
        @JOverride
        def hudHide(self, c, s): self._n("hudHide")
        @JOverride
        def tell(self, c, text, col): self._n("tell")
        @JOverride
        def inv(self, c): self._n("inv"); return None
        @JOverride
        def later(self, c, r): self._n("later")
        @JOverride
        def fresh(self, c): self._n("fresh"); return None
        @JOverride
        def now(self): self._n("now"); st["t"] += 50; return st["t"]
    return Api()


# ====================================================================================================== X: every new code path
def run_exec(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    Brg, Core, Eng, Defs, Ctx, Store, FIO, State = P("FishBridge"), P("FishCore"), P("FishEng"), P("FishDefs"), P("FishCtx"), P("FishStore"), P("FishIO"), P("FishState")
    Sys, UUID, IS = JClass("java.lang.System"), JClass("java.util.UUID"), JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    # ---- A: bridge
    K.check(Brg.BRIDGE is None, "X bridge: BRIDGE empty before the first call")
    m1 = Brg.bridge()
    K.check(Sys.identityHashCode(Sys.getProperties().get("skyy.bridge")) == Sys.identityHashCode(m1) and Sys.identityHashCode(Brg.BRIDGE) == Sys.identityHashCode(m1)
            and Sys.identityHashCode(Brg.bridge()) == Sys.identityHashCode(m1) and Sys.identityHashCode(Brg.bridge0()) == Sys.identityHashCode(m1),
            "X bridge: created once, cached in BRIDGE, the same map")
    PW.bridge_static(K, jar)
    g = PW.calls(jar)
    K.check(PKG + "FishCtx.<init>" not in g["FishTick.tick"] and PKG + "FishCore.ctxOf" in g["FishTick.tick"], "X static: FishTick.tick makes no FishCtx (ctxOf)")
    K.check(PKG + "FishCtx.<init>" in g["FishCore.kick"], "X static: kick hands FishGiveTask a copy of the context")
    t = FIO().newThread(None)
    K.check(str(t.getName()) == "SkyyFishing-IO" and t.isDaemon(), "X FishIO.newThread: SkyyFishing-IO, daemon")
    # ---- ctxOf
    u = UUID.fromString("00000000-0000-4000-8000-000000000007")
    c1 = Core.ctxOf(u, "Tester", None, None, None, None, None)
    c2 = Core.ctxOf(u, "Tester2", None, None, None, None, None)
    K.check(Sys.identityHashCode(c1) == Sys.identityHashCode(c2) and str(c2.name) == "Tester2", "X ctxOf: the player's ONE context, refilled")
    # ---- the tick through the seam
    st = {"calls": {}, "held": None, "slot": 0, "reel": 3, "t": 1000000}
    Eng.API = make_api(st)
    idle0 = Core.IDLE
    for i in range(200):
        Core.tickPlayer(c1)
    cl = st["calls"]
    K.check(cl.get("held") == 200 and cl.get("clicked", 0) == 0 and cl.get("heldSlot", 0) == 0 and cl.get("getReel") == 1 and cl.get("setReel") == 1
            and st["reel"] == 0 and cl.get("later", 0) == 0 and Core.IDLE == idle0 + 200,
            "X IDLE (no rod, no line) x200: 200 held() reads, no click / slot read, the reel read ONCE and reset to 0, no later() hop: %s" % cl)
    seen = Core.SEEN.get(u)
    K.check(seen is not None and seen.ticks == 199 and seen.reel == 0, "X FishSeen: the tick counter as an int (199), reel known 0")
    # epoch watch while idle
    br = Brg.bridge()
    br.put("profile:epoch:" + str(u), JClass("java.lang.Long")(5))
    for i in range(10):
        Core.tickPlayer(c1)
    br.put("profile:epoch:" + str(u), JClass("java.lang.Long")(6))
    for i in range(10):
        Core.tickPlayer(c1)
    K.check(Core.EPOCH_AT.get(u) is not None and int(Core.EPOCHS.get(u)) == 6, "X idle: the profile-epoch watch still runs (a switch is recorded)")
    # rod in hand: real ItemStack objects, allocated without the Item asset store (a bare JVM has none) - item id + quantity set
    Uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    Uf.setAccessible(True)
    U = Uf.get(None)
    Mod = JClass("java.lang.reflect.Modifier")

    def mkstack(id_):
        o = U.allocateInstance(IS.class_)
        for fl in IS.class_.getDeclaredFields():
            if Mod.isStatic(fl.getModifiers()):
                continue
            n = str(fl.getName()).lower()
            fl.setAccessible(True)
            if str(fl.getType().getName()) == "java.lang.String" and "id" in n:
                fl.set(o, id_)
            elif str(fl.getType().getName()) == "int" and "quant" in n:
                fl.setInt(o, 1)
        return o
    rods = list(Defs.RODS)
    rod = mkstack(str(rods[0]))
    K.check(str(rod.getItemId()) == str(rods[0]) and not rod.isEmpty(), "X the stand-in rod stack reads as %s" % rods[0])
    st["held"], st["calls"], st["slot"] = rod, {}, 2
    rigs0 = Core.RIGS
    for i in range(200):
        Core.tickPlayer(c1)
    cl = st["calls"]
    want = int(Core.SEEN.get(u).rigReel)
    K.check(Core.RIGS == rigs0 + 1 and cl.get("clicked") == 200 and cl.get("heldSlot") == 200 and st["reel"] == want
            and 9 <= cl.get("getReel", 0) <= 12 and cl.get("setReel", 0) == (1 if want != 0 else 0),
            "X ROD x200: the rig parsed ONCE, the reel set once (%d) and checked every 20 ticks: %s" % (want, cl))
    st["held"] = mkstack(str(rods[0]))
    Core.tickPlayer(c1)
    K.check(Core.RIGS == rigs0 + 2, "X a new stack object (a rig change) is parsed again")
    st["slot"] = 3
    Core.tickPlayer(c1)
    K.check(Core.RIGS == rigs0 + 3, "X another slot is parsed again")
    st["reel"] = 5
    st["held"], st["calls"] = None, {}
    Core.tickPlayer(c1)
    Core.SEEN.get(u).reel = 5
    Core.tickPlayer(c1)
    K.check(st["reel"] == 0 and st["calls"].get("setReel") == 1, "X rod put away: the reel look reset to 0: %s" % st["calls"])
    # a line out = the full path (clicked() every tick) even with no rod in hand -> the line is cancelled like 0.1.2
    s = State(u)
    s.phase = 5
    s.hudUntil = 0
    Core.STATES.put(u, s)
    st["calls"] = {}
    Core.tickPlayer(c1)
    K.check(st["calls"].get("clicked") == 1 and Core.STATES.get(u) is None, "X a result card (phase 5) takes the full path (and ends as 0.1.2)")
    # the save thread
    Store.IOX = JClass("java.util.concurrent.Executors").newSingleThreadScheduledExecutor(FIO())
    Store.stopIO()
    K.check(Store.IOX is None, "X FishStore.stopIO stops the writer")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyFishing", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec)], script=__file__)
