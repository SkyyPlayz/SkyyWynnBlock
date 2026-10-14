"""SkyyClasses 0.1.20 - harness for CHAT OVERFLOW -> FEED (tools/classes_0_1_20_patch.py, the shared tools/skyyroute.py MsgRoute) + the
Hytale 0.7 build fixes (the flamethrower prefix, the staff / dagger count minimums).
Build first: python tools/classes_0_1_20_patch.py && python SkyyClasses/build_skyyclasses_0.1.20.py

    python SkyyClasses/test_skyyclasses_0.1.20.py --dir <empty folder inside tools/dev/scratch/> [--keep]

Every JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in scratch. Live save data is only READ / copied.
  OLD  test_skyyclasses_0.1.19.py's own sections on the 0.1.20 jar (its --l loadout-bridge checks, its START TWICE on a scratch COPY of
       the live Skyy_SkyyClasses folder: nothing written)
  A    verify   every class loads + initialises with -Xverify:all (tools/harness_kit.py)
  C    compare  0.1.19 -> 0.1.20: exactly the planned members differ; MsgRoute added
  R    route    EXECUTED with a stand-in SkyyHud on the skyy.bridge map: MsgRoute (no SkyyHud = chat, the 2 s cache, odd answers);
                HealMsg.deliver for every route (chat = "[Classes] " + the text = 0.1.19's line; feed = one heal card, kind heal, no icon,
                the text; a refused card = the chat line; off = nothing; an old SkyyHud = chat); given / taken / due() batches -> deliver
                (the texts 0.1.19 builds, word for word: its own HealMsg on the same input); flushDue runs with no Universe (nothing
                thrown out); ClassRules: Weapon_Flamethrower_Scrap -> "flamethrowers" (0.1.19: "that weapon"), still unassigned;
                SESSION: 10 heal batches with no SkyyHud (= 0.1.19) and with the Feed default -> tools/dev/scratch/msgroute/session/classes.json
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, shutil, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.20"
PKG = "com.skyy.classes."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyClasses-0.1.19.jar")
BASE = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "msgroute", "cl")))
SCRATCH = BASE if "--phase" in sys.argv else os.path.join(BASE, "h")
SESSION = os.environ.get("SKYYROUTE_SESSION") or os.path.join(ROOT, "tools", "dev", "scratch", "msgroute", "session")
T19 = os.path.join(HERE, "test_skyyclasses_0.1.19.py")

EXPECT = {
    "HealMsg": ["+m deliver", "~m flushDue"],
    "ClassQuit": ["~m accept"],              # + MsgRoute.forget(u) on leave
    "ClassDefs": ["~<clinit>"],              # the 0.7 prefix Weapon_Flamethrower_ (was Flamethrower_)
    # version texts only: the ready line / pack name, kits.properties "version", the config kit's export header
    "SkyyClassesPlugin": ["~m setup"],
    "KitMigrate": ["~m runOnce"],
    "CfgFn": ["~m opExport"],
    # the config kit (tools/skyycfg.py) gained the lock-free bridge (research/Code-Structure-Audit.md quick win 1) after 0.1.19 was built:
    # every rebuilt mod picks it up - CfgRows.bridge() caches the map in BRIDGE, bridge0 = the old body
    "CfgRows": ["+f BRIDGE", "+m bridge0", "~m bridge", "~m header"],
}
ADDED = ["MsgRoute"]


def loader_for(jar):
    from jpype import JClass, JArray
    files = [jar, B.SERVER_JAR]
    arr = JArray(JClass("java.net.URL"))(len(files))
    for i, f in enumerate(files):
        arr[i] = JClass("java.io.File")(f).toURI().toURL()
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getPlatformClassLoader())


def run_route(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    MR, HM, Cfg, Rul = P("MsgRoute"), P("HealMsg"), P("ClassCfg"), P("ClassRules")
    UUID, Bool = JClass("java.util.UUID"), JClass("java.lang.Boolean")
    bridge = Cfg.bridge()

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, o):
            return self.f(o)

    S = {"route": {}, "ok": True, "cards": [], "asks": 0}

    def f_route(o):
        S["asks"] += 1
        return S["route"].get(str(o[1]), "chat")

    def f_feed(o):
        S["cards"].append((str(o[1]), None if o[2] is None else str(o[2]), str(o[3]), None if o[4] is None else int(o[4])))
        return Bool.TRUE if S["ok"] else Bool.FALSE
    FR, FF = Fn(f_route), Fn(f_feed)

    def hud(on=True, route=None):
        for k in ("msgroute:fn:get", "feed:fn:push"):
            bridge.remove(k)
        if on:
            bridge.put("msgroute:fn:get", FR)
            bridge.put("feed:fn:push", FF)
        S["route"], S["ok"], S["cards"], S["asks"] = dict(route or {}), True, [], 0
        MR.CACHE.clear()

    u = UUID.fromString("00000000-0000-4000-8000-000000000120")
    # review fix 2026-10-13: every jar's MsgRoute copy comes from the same tools/skyyroute.py (gate() included, unused by Classes)
    K.check(MR.gate(u, "heal", "a", 1000, 0) and not MR.gate(u, "heal", "b", 1000, 0) and MR.gate(u, "heal", "a", 1000, 0), "R MsgRoute.gate (shared copy): new key once a second, same key passes")
    MR.GATE.clear()
    v = UUID.fromString("00000000-0000-4000-8000-000000000121")
    hud(False)
    K.eq(str(MR.route(u, "heal")), "chat", "R MsgRoute: no SkyyHud -> chat")
    hud(True, {"heal": "feed"})
    MR.route(u, "heal")
    MR.route(u, "heal")
    K.check(S["asks"] == 1, "R MsgRoute: cached (one ask for two routes)")
    hud(True, {"heal": "maybe"})
    K.eq(str(MR.route(u, "heal")), "chat", "R MsgRoute: an odd answer -> chat")
    K.check(MR.BR is not None, "R MsgRoute: the bridge map is cached (ClassCfg.bridge's System lock taken once)")

    # ---- deliver, every route
    T = "Heals: +8 HP to you"
    hud(True, {"heal": "chat"})
    K.eq(str(HM.deliver(u, T)), "[Classes] " + T, "R deliver chat = 0.1.19's line")
    hud(False)
    K.eq(str(HM.deliver(u, T)), "[Classes] " + T, "R deliver, an old / no SkyyHud = the chat line")
    hud(True, {"heal": "feed"})
    K.check(HM.deliver(u, T) is None and S["cards"] == [("heal", None, T, None)], "R deliver feed: one heal card, no chat line: %s" % S["cards"])
    hud(True, {"heal": "feed"})
    S["ok"] = False
    K.eq(str(HM.deliver(u, T)), "[Classes] " + T, "R deliver feed refused -> the chat line")
    hud(True, {"heal": "off"})
    o0 = int(MR.OFF.get())
    K.check(HM.deliver(u, T) is None and S["cards"] == [] and int(MR.OFF.get()) == o0 + 1, "R deliver off: nothing")
    K.check(HM.deliver(None, T) is None and HM.deliver(u, None) is None, "R deliver: null in -> null")

    # ---- the batch texts = 0.1.19's (its own HealMsg on the same input)
    L = loader_for(OLD_JAR)
    OHM = JClass(PKG + "HealMsg", loader=L)
    for M in (HM, OHM):
        M.GIVEN.clear(); M.TAKEN.clear(); M.LASTG.clear(); M.LASTT.clear()
        M.given(u, u, 8.0)
        M.given(u, v, 12.5)
        M.taken(v, u, "Skyy", 12.5)
    nd, od = HM.due(1000000, 2000), OHM.due(1000000, 2000)
    nt = sorted((str(e[0]), str(e[1]), str(e[2])) for e in nd)
    ot = sorted((str(e[0]), str(e[1]), str(e[2])) for e in od)
    K.check(nt == ot and len(nt) == 2, "R due(): the same batch texts as 0.1.19: %s" % nt)
    hud(True, {"heal": "feed"})
    lines = [HM.deliver(UUID.fromString(a), b) for a, b, _k in nt]
    K.check(lines == [None, None] and sorted(c[2] for c in S["cards"]) == sorted(b for _a, b, _k in nt), "R due -> deliver feed: two cards %s" % S["cards"])
    # flushDue with no Universe: entries are taken, the per-entry try keeps going, nothing escapes
    HM.given(u, u, 3.0)
    try:
        HM.flushDue()
        ok = True
    except Exception as e:
        ok = False
    K.check(ok and HM.GIVEN.isEmpty(), "R flushDue runs without a Universe (the batch is taken, nothing thrown)")
    # ---- the 0.7 flamethrower prefix
    t_new = str(Rul.blockText(u, "Weapon_Flamethrower_Scrap", False))
    K.notes.append("flamethrower refusal (no class): %s" % t_new)
    D = P("ClassDefs")
    K.check(str(D.nounOf("Weapon_Flamethrower_Scrap")) == "flamethrowers", "R 0.7: Weapon_Flamethrower_Scrap is named 'flamethrowers': %s" % D.nounOf("Weapon_Flamethrower_Scrap"))
    OD = JClass(PKG + "ClassDefs", loader=L)
    K.check(int(D.ownerOf("Weapon_Flamethrower_Scrap")) == int(OD.ownerOf("Weapon_Flamethrower_Scrap")),
            "R 0.7: its owner is unchanged vs 0.1.19 (%s)" % D.ownerOf("Weapon_Flamethrower_Scrap"))

    # ---- SESSION: 10 heal batches (the 2026-10-11 log had 10 "[Classes] Heals:" lines in 12 minutes)
    def session(defaults):
        hud(defaults is not None, defaults)
        n = 0
        for i in range(10):
            MR.CACHE.clear()
            if HM.deliver(u, "Heals: +%d HP to you" % (8 + i)) is not None:
                n += 1
        return n, len(S["cards"])
    before, after = session(None), session({"heal": "feed"})
    K.check(before[0] == 10 and after[0] == 0 and after[1] == 10, "R SESSION classes: 10 heal lines without SkyyHud, %d with the Feed default (%d cards)" % (after[0], after[1]))
    os.makedirs(SESSION, exist_ok=True)
    json.dump({"mod": "SkyyClasses " + VERSION, "before": before[0], "after": after[0], "cards": after[1], "what": "10 heal lines"},
              open(os.path.join(SESSION, "classes.json"), "w"), indent=1)
    K.save()


def old_sections():
    """test_skyyclasses_0.1.19.py --l (the loadout bridge) and --s (start twice on a live copy) on the 0.1.20 jar"""
    d = os.path.join(BASE, "t19")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(os.path.join(d, "tmp"))
    env = dict(os.environ, TEMP=os.path.join(d, "tmp"), TMP=os.path.join(d, "tmp"), JAVA_TOOL_OPTIONS="-XX:-UsePerfData")
    p = subprocess.run([sys.executable, T19, "--jar", JAR, "--dir", d], env=env, capture_output=True, text=True)
    tail = (p.stdout or "").strip().splitlines()[-6:]
    print("OLD. test_skyyclasses_0.1.19.py on the 0.1.20 jar:\n   " + "\n   ".join(tail))
    # its CC section compares 0.1.18 -> its --jar (0.1.20 here) and expects 0.1.19's changes - every other check must pass
    fails = [ln for ln in (p.stdout or "").splitlines() if ln.strip().startswith("FAIL")]
    other = [f for f in fails if " CC " not in f and not f.strip().startswith("FAIL CC")]
    HK.check(not other, "OLD 0.1.19 sections (loadout bridge L, start twice ST) pass on the 0.1.20 jar: %s" % other[:3])
    HK.check(any("checks passed" in ln for ln in tail), "OLD 0.1.19 harness ran to the end")
    shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    if "--phase" not in sys.argv:
        assert os.path.realpath(BASE).startswith(os.path.realpath(os.path.join(ROOT, "tools", "dev", "scratch")) + os.sep)
        old_sections()
    HK.run(name="SkyyClasses", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("route", run_route)], script=__file__)
