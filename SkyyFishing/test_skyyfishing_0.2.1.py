"""Harness for SkyyFishing 0.2.1 (round eggs D5b-3: a fish from Void water rolls SkyyPets' secret Void egg; tools/fishing_0_2_1_patch.py).
Build first: python tools/fishing_0_2_1_patch.py && python SkyyFishing/build_skyyfishing_0.2.1.py

    python SkyyFishing/test_skyyfishing_0.2.1.py [--keep]

  S       static: the patch re-runs to identical bytes, line endings kept, +1 class, no command / system; jar: only FishSecret.class added,
          the only non-class change is the manifest
  A / C / AA  verify (-Xverify:all), class compare 0.2.0 -> 0.2.1 (EXPECT), engine-access audit
  X       EXECUTES: FishSecret.voidAt (no SkyyMobs = false; mob:fn:voidAt TRUE / FALSE / null / a throwing bridge = false; the world name + block
          centre passed), FishSecret.onCatch (not Void water / no player / the row off = nothing; no SkyyPets = counted; secretRoll gets
          {UUID, "void", "SkyyFishing:void-catch <fish>"} once); FishCore.cast on a stand-in FishApi executes the Void-water line (a null
          world = not Void); FishCore.land of a FISH from Void water = ONE roll (a Twin Line double still one), from plain water none, a
          junk landing from Void water none; the row's default + text()
  L200    0.2.0's LOGIC phase EXECUTED on this jar (zones, prices, recipes, tags, saved data unchanged)
  LIVE    start twice on a scratch COPY of the live NewBetaTest Skyy_SkyyFishing: FishP3Mig / FishZ2Seed do nothing more, config.properties
          bytes untouched, the new row reads its default (on)
Not testable without the game (UNVERIFIED): mob:fn:voidAt on a loaded Void world chunk (needs the cast on the world thread), SkyyPets'
delivery of the egg. Exit code 1 on any failure.
"""
import os, sys, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.2.1"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "eggs", "fish")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyFishing-%s.jar" % VERSION)]
_cmp0 = HK.run_compare
_spec = importlib.util.spec_from_file_location("test_skyyfishing_0_2_0", os.path.join(HERE, "test_skyyfishing_0.2.0.py"))
T200 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T200)
HK.run_compare = _cmp0          # 0.2.0's compare allowed its new assets; 0.2.1 adds none (only the manifest may change)
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyFishing-0.2.0.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.fishing."
T200.JAR = JAR
GEN = os.path.join(HERE, "build_skyyfishing_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyfishing_0.2.0.py")
PATCH = os.path.join(ROOT, "tools", "fishing_0_2_1_patch.py")
LIVE_DIR = T200.LIVE_DIR
ADDED = ["FishSecret"]
EXPECT = {
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],          # the kit: the new row + the default file text
    "FishCfg": ["+f SECRET_VOID", "~<clinit>", "~m applyAll", "~m applyScalars", "~m seed"],          # applyAll / seed inline DEFAULT_TEXT (the new line)
    "FishCmds": ["~m admin"],          # /fishadmin status (+ the Void counters)
    "FishCore": ["~m cast", "~m land"],
    "FishState": ["+f voidW"],
    "SkyyFishingPlugin": ["~m setup"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
U1S = "00000000-0000-4000-8000-0000000021f1"


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyFishing 0.2.1 - build script') and g.count('VERSION = "0.2.1"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("),
          g.count(' = mk("') - o.count(' = mk("')), (0, 0, 1), "S +1 class, no system / command")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), (["com/skyy/fishing/FishSecret.class"], []), "S only FishSecret.class added")
    K.eq(sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n)), ["manifest.json"], "S the only non-class change is the manifest")
    K.save()


def make_api(st):
    from jpype import JImplements, JOverride, JArray, JDouble

    @JImplements(PKG + "FishApi")
    class Api(object):
        def _n(self, k):
            st["calls"][k] = st["calls"].get(k, 0) + 1
        @JOverride
        def eye(self, c): self._n("eye"); return JArray(JDouble)([0.5, 62.5, 0.5, 0.0, -1.0, 0.0])
        @JOverride
        def feet(self, c): self._n("feet"); return JArray(JDouble)([0.5, 61.0, 0.5])
        @JOverride
        def heldSlot(self, c): self._n("heldSlot"); return st["slot"]
        @JOverride
        def held(self, c): self._n("held"); return st["held"]
        @JOverride
        def clicked(self, c): self._n("clicked"); return False
        @JOverride
        def block(self, c, x, y, z): self._n("block"); return 1 if int(y) <= 60 else 0          # an open sea below y 60
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
        def tell(self, c, text, col): self._n("tell"); st["told"].append(str(text))
        @JOverride
        def inv(self, c): self._n("inv"); return None
        @JOverride
        def later(self, c, r): self._n("later")
        @JOverride
        def fresh(self, c): self._n("fresh"); return None
        @JOverride
        def now(self): self._n("now"); st["t"] += 50; return st["t"]
    return Api()


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray, JObject
    K = HK.Child(out)
    P, mods = T200.setup(K, scratch, "x")
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    Sec, Cfg, Core, Eng, Defs = P("FishSecret"), P("FishCfg"), P("FishCore"), P("FishEng"), P("FishDefs")
    u = JClass("java.util.UUID").fromString(U1S)
    K.check(bool(Cfg.SECRET_VOID), "X fish.secret.void defaults on")
    dt = open(os.path.join(mods, "Skyy_SkyyFishing", "config.properties"), encoding="latin-1").read() if os.path.isfile(os.path.join(mods, "Skyy_SkyyFishing", "config.properties")) else ""
    K.notes.append("X default file has the row: %s" % ("\nfish.secret.void=true" in dt))
    # 1. voidAt
    K.check(not bool(Sec.voidAt("skywynn_z1", 1.5, 60.5, 2.5)) and not bool(Sec.voidAt(None, 0, 0, 0)), "X no SkyyMobs (no mob:fn:voidAt) = not Void water")
    ASK = []
    ANS = {"v": None}

    def vat(o):
        ASK.append((str(o[0]), float(o[1]), float(o[2]), float(o[3])))
        if ANS["v"] == "throw":
            raise RuntimeError("boom")
        return ANS["v"]
    br.put("mob:fn:voidAt", T200.fn_proxy(vat))
    res = []
    for a in (JClass("java.lang.Boolean").TRUE, JClass("java.lang.Boolean").FALSE, None, "throw"):
        ANS["v"] = a
        res.append(bool(Sec.voidAt("Void", 3.5, 40.5, -7.5)))
    K.eq(res, [True, False, False, False], "X mob:fn:voidAt TRUE = Void water; FALSE / null / a throwing bridge = not (never throws)")
    K.eq(ASK[0], ("Void", 3.5, 40.5, -7.5), "X voidAt passes the world name + the block centre")
    # 2. onCatch
    ROLL = []
    RA = {"c": "MISS"}

    def roll(o):
        ROLL.append((str(o[0]), str(o[1]), str(o[2])))
        return RA["c"]
    nd = int(Sec.NODOOR)
    K.eq([Sec.onCatch(u, False, "Fish_X"), Sec.onCatch(None, True, "Fish_X")], [None, None], "X not Void water / no player = nothing")
    K.check(Sec.onCatch(u, True, "Fish_X") is None and int(Sec.NODOOR) == nd + 1, "X no SkyyPets door = nothing (counted)")
    br.put("pets:fn:secretRoll", T200.fn_proxy(roll))
    r1 = str(Sec.onCatch(u, True, "Fish_X"))
    RA["c"] = "OK"
    f0 = int(Sec.FOUND)
    r2 = str(Sec.onCatch(u, True, "Fish_Y"))
    K.eq((r1, r2, ROLL, int(Sec.FOUND)), ("MISS", "OK", [(U1S, "void", "SkyyFishing:void-catch Fish_X"), (U1S, "void", "SkyyFishing:void-catch Fish_Y")], f0 + 1),
         "X a Void catch = ONE pets:fn:secretRoll {UUID, void, source}; OK counted as found")
    Cfg.SECRET_VOID = False
    del ROLL[:]
    K.eq((Sec.onCatch(u, True, "Fish_X"), ROLL), (None, []), "X fish.secret.void off = no roll")
    Cfg.SECRET_VOID = True
    # 3. FishCore.cast: the Void-water line runs (a null world = not Void, no bridge call)
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    Cfg.ON = True
    st = {"calls": {}, "slot": 0, "held": None, "reel": 0, "t": 1000, "told": []}
    Eng.API = make_api(st)
    c = Core.ctxOf(u, "Tester", None, None, None, None, None)
    rod = IS("SkyyFishing_Rod_Copper", 1)
    del ASK[:]
    Core.cast(c, "SkyyFishing_Rod_Copper", 0, rod, None, 1000)
    s = Core.STATES.get(u)
    K.check(s is not None and st["calls"].get("spawnBobber") == 1, "X FishCore.cast ran to the bobber on the stand-in sea (%s; %s)" % (st["calls"], st["told"][-2:]))
    if s is not None:
        K.check(not bool(s.voidW) and ASK == [], "X cast: a world-less context = not Void water (voidAt answers false before any bridge call)")
        # 4. FishCore.land: a FISH from Void water = one roll; plain water none; junk none
        sp0 = 0
        fish = str(Defs.FISH[sp0])
        RA["c"] = "MISS"
        out_ = []
        for kind, vw, dbl in ((0, True, 0.0), (0, False, 0.0), (1, True, 0.0), (0, True, 100.0)):
            Core.STATES.put(u, s)
            s.ended = False
            s.kind = kind
            s.sp = sp0 if kind == 0 else -1
            s.item = "Rock_Stone"
            s.qty = 1
            s.kg = 1.2
            s.cm = 30.0
            s.voidW = vw
            s.stat[P("FishRig").ST_DOUBLE] = dbl
            del ROLL[:]
            try:
                Core.land(c, s, 5000)
                out_.append(list(ROLL))
            except Exception as e:
                out_.append("ERR %s" % e)
        K.eq(out_[0], [(U1S, "void", "SkyyFishing:void-catch " + fish)], "X land: a fish from Void water = ONE secretRoll (%s)" % fish)
        K.eq(out_[1], [], "X land: a fish from plain water = no roll")
        K.eq(out_[2], [], "X land: junk from Void water = no roll")
        K.eq(out_[3], [(U1S, "void", "SkyyFishing:void-catch " + fish)], "X land: a Twin Line double from Void water = still ONE roll")
    Eng.API = None
    t = str(Sec.text())
    K.check("secret Void egg on" in t and "mob:fn:voidAt found" in t and "pets:fn:secretRoll found" in t, "X text(): %s" % t)
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    P, _m = T200.setup(K, scratch, "live", load=False)
    Paths = JClass("java.nio.file.Paths")
    mods = os.path.dirname(home)
    cf = os.path.join(home, "config.properties")
    b0 = open(cf, "rb").read() if os.path.isfile(cf) else None

    def start():
        T200.reset(P)
        r = str(P("FishP3Mig").run(Paths.get(mods))) + " | " + str(P("FishZ2Seed").run(Paths.get(mods)))
        P("FishCfg").load(Paths.get(mods))
        P("FishStore").start(Paths.get(mods))
        P("FishStore").flush()
        return r
    r1 = start()
    K.check(bool(P("FishCfg").SECRET_VOID), "LIVE start 1: fish.secret.void (no line in the live file) = on")
    K.check(b0 is None or open(cf, "rb").read() == b0, "LIVE start 1: config.properties bytes untouched (%s)" % r1[:120])
    r2 = start()
    K.check(r2.strip() == "|" and (b0 is None or open(cf, "rb").read() == b0), "LIVE start 2: nothing changes (%s)" % r2)
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyFishing", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("exec", run_exec), ("l200", T200.run_logic), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyFishing"))
