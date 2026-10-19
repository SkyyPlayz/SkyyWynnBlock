"""Harness for SkyyWorldGen 0.7.7 (the old 0.6 zone world unloads when empty, beta bug 4 lag part 5; tools/worldgen_0_7_7_patch.py).
Build first:
    python tools/worldgen_0_7_7_patch.py && python SkyyWorldGen/build_skyyworldgen_0.7.7.py

    python SkyyWorldGen/test_skyyworldgen_0.7.7.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.7.6 -> 0.7.7: exactly the EXPECTED members differ (WgCfg UNLOAD_S + its row / file line, WgOpen.decide busy + touch,
               WgWeather.tick calls WgUnload.tick, version texts); added class WgUnload; non-class entries: manifest.json + the
               instance templates + the server.lang header (version text only)
  F    func     WgUnload.decide (60 s empty -> unload, players / a trip in the last 120 s / a load or creation running / NEVER / the
               setting 0 = keep, clock reset), unload / tick without an engine = nothing (busy cleared), WgCfg zones.unloadOldSeconds
               default 60 clamped 0..86400; the generated script: removeWorld only in WgUnload.unload after the DeleteOnRemove guard
               and the player re-check, tick only for WORLDS[ZONES] and only while skywynn_zones2 exists, decide answers 5 while busy
  AA   audit    the engine-access audit
Not testable without a server (UNVERIFIED here): the real removeWorld / loadWorld (SkyyShards probes S1 / S2 + the smoke test).
Exit code 1 on any failure.
"""
import os, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import skyybuild as B

VERSION = "0.7.7"
OLD_VERSION = "0.7.6"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyWorldGen-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyWorldGen-%s.jar" % OLD_VERSION)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "unl", "wg")))
PKG = "com.skyy.worldgen."
LANG = "Server/Languages/en-US/server.lang"
EXPECT = {
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "SkyyWorldGenPlugin": ["~m setup"], "WgStore": ["~m markCreated"],
    "WgCfg": ["+f UNLOAD_S", "~<clinit>", "~m apply", "~m load", "~m reloadAll"],   # load + reloadAll hold the default file text
    "WgOpen": ["~m decide"], "WgWeather": ["~m tick"],
}
ADDED = ["WgUnload"]
if "--expect-dump" in sys.argv:
    EXPECT = {}

if HK.arg("--phase") == "compare":
    _eq0 = HK.Child.eq

    def _eq(self, got, want, what):
        if what == "C: non-class entries changed" and want == ["manifest.json"]:
            ok = "manifest.json" in got and all(n in ("manifest.json", LANG) or n.endswith("/instance.bson") for n in got)
            if ok and LANG in got:      # server.lang: only its header comment names the version
                a = zipfile.ZipFile(OLD_JAR).read(LANG).decode("utf8").splitlines()
                b = zipfile.ZipFile(HK.arg("--jar", JAR)).read(LANG).decode("utf8").splitlines()
                ok = len(a) == len(b) and [i for i in range(len(a)) if a[i] != b[i]] == [0] and a[0].replace(OLD_VERSION, VERSION) == b[0]
            return self.check(ok, "C: non-class entries changed = manifest.json + instance templates + server.lang header (version text only): %s" % sorted(got))
        return _eq0(self, got, want, what)
    HK.Child.eq = _eq


def body(gen, start):
    s = gen[gen.index(start):]
    return s[:s.index('}""")')]


def run_func(out, jar, scratch, _home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=False)
    from jpype import JClass, JLong, JInt, JString
    U, Cfg, Zn = JClass(PKG + "WgUnload"), JClass(PKG + "WgCfg"), JClass(PKG + "WgZones")
    old = str(Zn.WORLDS[int(Zn.ZONES)])
    K.eq(old, "skywynn_zones", "F the unload target is the 0.6 world skywynn_zones (WORLDS[ZONES])")
    K.eq(str(Zn.WORLDS[int(Zn.ZONES2)]), "skywynn_zones2", "F ... and skywynn_zones2 is the one whose existence it needs")
    K.eq(int(Cfg.UNLOAD_S), 60, "F zones.unloadOldSeconds defaults to 60 s")
    now = 10 ** 12
    lim = 60000

    def d(players=0, t=0, lm=lim, opening=False, wn=old):
        return int(U.decide(JString(wn) if wn is not None else None, JInt(players), JLong(now + t), JLong(lm), opening))
    K.check(d() == 1 and d(t=59999) == 1 and d(t=60000) == 2, "F empty: the clock starts, unload at 60 s")
    K.check(d(players=1, t=61000) == 0 and not U.EMPTY.containsKey(JString(old)), "F a player there -> kept, the clock reset")
    K.check(d(t=62000) == 1 and d(t=122000) == 2, "F empty again -> the clock starts over")
    U.EMPTY.clear()
    K.check(d(opening=True) == 0 and d(opening=True, t=10 ** 7) == 0, "F never while a load / creation of it runs")
    K.check(d(lm=-1) == 0 and U.EMPTY.isEmpty(), "F the setting 0 (limit < 0) = never, no clock kept")
    K.check(d(wn=None) == 0, "F null = nothing")
    U.NEVER.put(JString(old), JClass("java.lang.Boolean").TRUE)
    K.check(d() == 0 and d(t=10 ** 7) == 0, "F never a world on the NEVER list (config said delete on remove)")
    U.NEVER.clear()
    U.touch(JString(old))
    real = int(JClass("java.lang.System").currentTimeMillis())
    K.check(int(U.decide(JString(old), JInt(0), JLong(real + 119000), JLong(lim), False)) == 0, "F never within 120 s after a /zone trip (touch)")
    K.check(int(U.decide(JString(old), JInt(0), JLong(real + 121000), JLong(lim), False)) == 1, "F ... after that the clock starts")
    U.USED.clear()
    U.BUSY.put(JString(old), JClass("java.lang.Boolean").TRUE)
    K.check(bool(U.busy(JString(old))) and int(U.unload(JString(old))) == 0 and U.BUSY.containsKey(JString(old)), "F busy(): a second unload of it = nothing")
    U.BUSY.clear()
    U.EMPTY.put(JString(old), JClass("java.lang.Long")(1))
    r = int(U.unload(JString(old)))
    K.check(r in (0, -1) and not U.BUSY.containsKey(JString(old)) and not U.EMPTY.containsKey(JString(old)), "F unload without an engine: nothing, busy + clock cleared (%d)" % r)
    K.check(int(U.unload(None)) == 0, "F unload(null) = nothing")
    try:
        U.NEXT = 0
        K.check(int(U.tick()) == 0, "F tick without an engine = nothing")
        K.check(int(U.tick()) == 0 and int(U.NEXT) > 0, "F tick acts at most every 30 s")
    except Exception as e:
        K.check(False, "F tick without an engine threw: %s" % e)
    Cfg.UNLOAD_S = 0
    U.NEXT = 0
    U.EMPTY.put(JString(old), JClass("java.lang.Long")(1))
    K.check(int(U.tick()) == 0 and U.EMPTY.isEmpty(), "F tick with the setting 0: nothing, clocks forgotten")
    Cfg.UNLOAD_S = 60
    gen = open(os.path.join(HERE, "build_skyyworldgen_%s.py" % VERSION), encoding="utf-8").read()
    K.check(gen.count("removeWorld(") == 1, "F Universe.removeWorld is called once in the script (WgUnload.unload)")
    ub = body(gen, "public static int unload(String wn)")
    K.check("u.removeWorld(wn)" in ub and ub.index("c.isDeleteOnRemove() || c.isDeleteOnUniverseStart()") < ub.index("u.removeWorld(wn)")
            and ub.index("w.getPlayerCount() > 0") < ub.index("u.removeWorld(wn)") and "w == d" in ub,
            "F unload: the DeleteOnRemove guard, the player re-check and the default-world guard run before removeWorld")
    tb = body(gen, "public static int tick()")
    K.check("WORLDS[@PKG@.WgZones.ZONES]" in tb and "WORLDS[@PKG@.WgZones.ZONES2]" in tb and tb.index("isWorldLoadable(z2)") < tb.index("unload(wn)"),
            "F tick: only the 0.6 world, only while skywynn_zones2 exists (loaded or on disk)")
    db = body(gen, "public static int decide(int zi, @WLD@ from)")
    K.check(db.index("@PKG@.WgUnload.busy(name)) return 5") < db.index("uni.getWorld(name)"), "F WgOpen.decide answers 5 (try again) while the world is being unloaded")
    K.check("setDeleteOnRemove" not in gen and "setRemovalConditions" not in gen, "F nothing sets DeleteOnRemove / RemovalConditions")
    K.check("zones.unloadOldSeconds=60" in gen and '"field:WgCfg.UNLOAD_S"' in gen, "F the Server Setup row + the default config line")
    K.save()


if __name__ == "__main__":
    HK.run("SkyyWorldGen", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED, [("func", run_func)], __file__)
