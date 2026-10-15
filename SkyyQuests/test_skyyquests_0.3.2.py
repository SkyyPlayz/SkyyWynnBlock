"""SkyyQuests 0.3.2 harness (THE TUTORIAL ON THE 3 STARTER ISLANDS: island places from SkyyIslands 0.5.10; tools/quests_0_3_2_patch.py) on
top of the 0.3.1 harness (test_skyyquests_0.3.1.py: every 0.3.1 / 0.3 phase runs again on the 0.3.2 jar). tools/harness_kit.py phases,
fresh child JVMs (-Xverify:all).

    python SkyyQuests/test_skyyquests_0.3.2.py [--jar SkyyQuests-0.3.2.jar] [--dir <scratch>] [--keep]

  A / C / AA  verify, class compare 0.3.1 -> 0.3.2 (QDefs: + ISL, + islandPlaces, ~ place; QaPlaceCmd; the version texts only), audit
  ISL         EXECUTED with the REAL island:places String of the SkyyIslands 0.5.10 build (its s3_layout(), S3_ONLY=1):
              - no key = 0.3.1: the tutorial's island_two / island_three reach parts are "coming soon", no reach bit
              - with the key: QDefs.place(island2 / island3 / portal / boss ...) = SkyyIslands' places (world "island"); the reach bit
                appears; standing on island 2 in an island world ticks "Bridge to island 2", island 3 ticks "Bridge to island 3"
                (task 11 / 19), the mini boss (where=island3) and the portal (where=portal) have their arrow targets; the widget
                (quest:fn:hud) shows the distance + direction to island 2
              - a places.properties line WINS over SkyyIslands' place; the parsed map is cached per String (same String = the same map,
                a new String = parsed again); the key removed (classic islands) = no island places again; a bad entry is skipped
              - /questadmin place list lists the island places "from SkyyIslands" (static: QaPlaceCmd calls islandPlaces)
  SND D E L P K S N B F ST   the 0.3.1 phases on the 0.3.2 jar (START TWICE on a scratch COPY of the live data in ST)
Scratch: tools/dev/scratch/islands3/quests (deleted unless --keep). Exit 1 on any failure.
"""
import os, sys, shutil, subprocess, importlib.util, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW

if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "islands3", "quests")]
_spec = importlib.util.spec_from_file_location("test_skyyquests_0_3_1", os.path.join(HERE, "test_skyyquests_0.3.1.py"))
T031 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T031)
T03 = T031.T03

VERSION = "0.3.2"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyQuests-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyQuests-0.3.1.jar")
SCRATCH = T03.SCRATCH
FAKE_DIR = T03.FAKE_DIR
PKG = T03.PKG
TB = T03.TB
EXPECT = {
    # loadPlaces / savePlace: the places.properties header constant (PLACES_HEAD, inlined by the compiler) has the 2 new 0.3.2 lines
    "QDefs": ["+f ISL", "+m islandPlaces", "~<clinit>", "~m loadPlaces", "~m place", "~m savePlace"],
    "QaPlaceCmd": ["~m execute"],
    "QMarks": ["~m refresh"],            # fix round: the marker cache also keys on the island places
    "CfgRows": ["~m header"],            # the version text
    "CfgFn": ["~m opExport"],            # the version text
    "SkyyQuestsPlugin": ["~m setup"],    # the version text
}
ADDED = []


def islands_places():
    """the island:places String SkyyIslands 0.5.10 publishes (its build script's layout part, S3_ONLY=1 - no JVM, no build)"""
    os.environ["S3_ONLY"] = "1"
    sp = importlib.util.spec_from_file_location("build_skyyislands_0_5_10_s3", os.path.join(ROOT, "SkyyIslands", "build_skyyislands_0.5.10.py"))
    m = importlib.util.module_from_spec(sp)
    try:
        sp.loader.exec_module(m)
    except ImportError as e:
        assert "S3_ONLY" in str(e), e
    finally:
        del os.environ["S3_ONLY"]
    return m.S3_PLACES_TEXT, m.S3_PLACES


def run_isl(out, jar, scratch, home):
    from jpype import JClass, JObject, JArray, JString
    K = HK.Child(out)
    text, places = islands_places()
    HK.jvm([B.SERVER_JAR, jar, FAKE_DIR, B.JAVASSIST], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    PyFn = T03.fn_class()
    Boolean, Long = JClass("java.lang.Boolean"), JClass("java.lang.Long")
    X = T03.scene3(K, scratch, "isl")
    Eng, Defs, Sto = X.Eng, X.Defs, X.Sto
    Sto.STOPPED = True
    br.put("profile:fn:key", PyFn(lambda a: str(a)))
    br.put("coins:fn:add", PyFn(lambda a: Long(1)))
    br.put("skill:fn:addxp", PyFn(lambda a: Boolean.TRUE))
    br.put("feed:fn:push", PyFn(lambda a: Boolean.TRUE))
    u, p, s = X.player(1)
    tasks = dict((str(t.id), t) for t in X.L.tasks)
    K.check("island_two" in tasks and "island_three" in tasks and str(tasks["island_two"].parts[0].match) == "island2"
            and str(tasks["island_three"].parts[0].match) == "island3" and str(tasks["mini_boss"].where) == "island3" and str(tasks["to_hub"].where) == "portal",
            "ISL the shipped tutorial: task 11 reach island2, task 19 reach island3, task 20 where=island3, task 21 where=portal")
    # ---- no island:places = 0.3.1
    K.check(Defs.place("island2") is None and Defs.islandPlaces().isEmpty(), "ISL no key: no island place (= 0.3.1)")
    K.check(not (X.want(u) & TB["reach"]) and bool(Eng.partSoon(tasks["island_two"].parts[0])), "ISL no key: island_two is coming soon, no reach bit")
    # ---- SkyyIslands 0.5.10's String
    br.put("island:places", JString(text))
    for k, (x, y, z, lab) in places.items():
        q = Defs.place(k)
        K.check(q is not None and str(q.world) == "island" and (float(q.x), float(q.y), float(q.z), str(q.label)) == (x, y, z, lab),
                "ISL place(%s) = SkyyIslands' %s" % (k, places[k]))
    K.check(Defs.place("nowhere") is None and Defs.place("") is None and Defs.place(None) is None, "ISL unknown / empty id = null")
    m1 = Defs.islandPlaces()
    K.check(Defs.islandPlaces() is m1 or Defs.islandPlaces().equals(m1) and JClass("java.lang.System").identityHashCode(Defs.islandPlaces()) == JClass("java.lang.System").identityHashCode(m1),
            "ISL the same String = the cached map (parsed once)")
    K.check(not bool(Eng.partSoon(tasks["island_two"].parts[0])) and not bool(Eng.partSoon(tasks["island_three"].parts[0])), "ISL island_two / island_three are live now")
    Eng.rebuild(u, s)
    K.check(X.want(u) & TB["reach"], "ISL the reach bit appears (the 1 s position hop runs for this player)")
    x2, y2, z2, _l = places["island2"]
    x3, y3, z3, _l3 = places["island3"]
    Eng.position(p, "skyy-island-a1", 8.5, 129.0, 8.5)
    K.check(not X.done(s, "island_two") and not X.done(s, "island_three"), "ISL standing at the spawn: neither bridge task done")
    Eng.position(p, "skyy-hub", x2, y2, z2)
    K.check(not X.done(s, "island_two"), "ISL the island 2 spot in ANOTHER world (the hub) does not count")
    Eng.position(p, "skyy-island-a1", x2 + 3.0, y2, z2 - 2.0)
    K.check(X.done(s, "island_two") and not X.done(s, "island_three"), "ISL standing on island 2 (an island world): task 11 Bridge to island 2 DONE")
    Eng.position(p, "skyy-island-a1", x3 - 2.0, y3, z3 + 1.0)
    K.check(X.done(s, "island_three"), "ISL standing on island 3: task 19 Bridge to island 3 DONE")
    # the widget arrow for a fresh player whose first shown task is a place task (a line of its own, like the 0.3 H4 check)
    open(os.path.join(X.base, "quests", "zplace.properties"), "w").write(
        "line=walk\nname=Walk\nauto=true\ntask.1.id=go\ntask.1.name=Go to the portal\ntask.1.where=portal\ntask.1.type=reach\ntask.1.match=portal\ntask.1.radius=4\n")
    Defs.load()
    u2, p2, s2 = X.player(2)
    while int(s2.claimCount()) > 0:
        s2.takeClaim()
    s2.waitNote = None
    s2.setTrack("walk")
    p2.hideTut = True
    h = Eng.hud(u2)
    K.eq((str(h[0]), str(h[2]), str(h[5])), ("Walk", "Go to the portal", "Hub portal"), "ISL widget: the portal place's label before a position is known")
    px, py, pz, _pl = places["portal"]
    Eng.position(p2, "skyy-island-a2", px - 30.0, py, pz)
    h = Eng.hud(u2)
    K.eq((str(h[5]), int(h[6])), ("E  30 m  -  Hub portal", 2), "ISL widget arrow: 30 blocks west of the portal = E 30 m")
    # fix round (critic): the map / compass marker follows a NEW island:places String (starter.design switched mid-session)
    Marks = JClass(PKG + "QMarks")
    prow = lambda: [tuple(str(x) for x in r_) for r_ in Marks.bridge(u2, "skyy-island-a2") if str(r_[0]) == "portal"]
    Marks.refresh(p2, s2)
    r1 = prow()
    K.check(len(r1) == 1 and float(r1[0][2]) == px, "ISL marker: the portal place marker at SkyyIslands' portal (%s)" % r1)
    moved = ";".join(("portal=island|%s|%s|%s|%s" % (px + 7.0, py, pz, _pl)) if e.startswith("portal=") else e for e in text.split(";"))
    br.put("island:places", JString(moved))
    Marks.refresh(p2, s2)
    r2 = prow()
    K.check(len(r2) == 1 and float(r2[0][2]) == px + 7.0, "ISL marker: a new island:places String moves the marker on the next refresh (was stale before the fix): %s" % r2)
    br.put("island:places", JString(text))
    Marks.refresh(p2, s2)
    K.check(len(prow()) == 1 and float(prow()[0][2]) == px, "ISL marker: back to the published String -> back at the portal")
    # ---- places.properties wins; a new String is parsed again; the key removed
    Defs.savePlace("island2", "island", 1000.0, 64.0, 1000.0, "Admin spot")
    q = Defs.place("island2")
    K.check(q is not None and float(q.x) == 1000.0 and str(q.label) == "Admin spot", "ISL a places.properties line WINS over SkyyIslands' place")
    br.put("island:places", JString(text + ";bad;=x;zz=island|1|2"))
    m2 = Defs.islandPlaces()
    K.check(int(m2.size()) == len(places) and Defs.place("zz") is None, "ISL a new String is parsed again; bad entries skipped (%d places)" % int(m2.size()))
    br.remove("island:places")
    K.check(Defs.islandPlaces().isEmpty() and Defs.place("island3") is None and Defs.place("island2") is not None,
            "ISL the key removed (classic islands): no island places; the admin's own place stays")
    # ---- static
    g = PW.calls(jar)
    K.check(PKG + "QDefs.islandPlaces" in g.get("QaPlaceCmd.execute", set()) and PKG + "QDefs.islandPlaces" in g.get("QDefs.place", set()),
            "STATIC place -> islandPlaces; /questadmin place list -> islandPlaces")
    K.save()


if __name__ == "__main__":
    if "--mkfake" in sys.argv:
        T03.mkfake(HK.arg("--mkfake"), JAR)
        sys.exit(0)
    if "--phase" not in sys.argv:
        shutil.rmtree(FAKE_DIR, ignore_errors=True)
        os.makedirs(FAKE_DIR, exist_ok=True)
        env = dict(os.environ)
        env["TEMP"] = env["TMP"] = os.path.join(FAKE_DIR, "tmp")
        os.makedirs(env["TEMP"], exist_ok=True)
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--mkfake", FAKE_DIR, "--jar", JAR, "--dir", SCRATCH], env=env)
        if r.returncode != 0:
            sys.exit("the stand-in classes were not compiled")
    try:
        HK.run("SkyyQuests", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
               [("isl", run_isl), ("snd", T031.run_snd), ("defs", T03.run_defs), ("engine", T03.run_engine), ("life", T03.run_life),
                ("pay", T03.run_pay), ("crash", T03.run_crash), ("static", T03.run_static), ("npc", T03.run_npc), ("board", T03.run_board),
                ("fish", T03.run_fish), ("live", T03.run_live)],
               os.path.abspath(__file__), live=(T03.LIVE_DIR, "Skyy_SkyyIslands"))
    finally:
        if "--phase" not in sys.argv and "--keep" not in sys.argv:
            shutil.rmtree(FAKE_DIR, ignore_errors=True)
