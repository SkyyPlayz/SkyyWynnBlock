"""SkyyHud 0.3.23 harness - the minimap's QUEST kind (tools/hud_0_3_23_patch.py): SkyyQuests 0.3's map markers (ids "SkyyQuest...") are
drawn as gold diamonds. Built on tools/harness_kit.py: each phase a fresh child JVM (the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP /
TMP / java.io.tmpdir in the scratch folder).

    python SkyyHud/test_skyyhud_0.3.23.py [--jar SkyyHud-0.3.23.jar] [--old SkyyHud-0.3.22.jar] [--dir <scratch>] [--keep]

  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.22 -> 0.3.23: exactly the listed classes / members differ; non-class entries: the manifest
  X20 / X19 / Q / M / ST   EVERY check of the 0.3.22 harness (its x20, x19 - the minimap geometry that now builds 5 kind pictures -,
       quest, msg and live phases) on THIS jar
  QK   quest kind  Minimap.kindOf on real protocol MapMarkers: SkyyQuestNpc<id> / SkyyQuestPlace = 4 whatever their image (even a
                "Player" / "Death" / "Home" image), every other marker keeps its 0.3.22 kind (waypoint 0, death 1, home / spawn / bed 2,
                player 3); MmPng.diamond: a 16 x 16 rhombus in the given colour with the dark dot outline, transparent corners, the same
                outline colour as the dot; Minimap.gen("diamond:<colour>") makes a PNG picture (cached: the same object twice) that differs
                from the dot of the same colour; static: pictures() asks gen for "diamond:" at kind 4 and builds a 5-entry kind table
  AA   audit    the engine-access audit
Not testable without the game (UNVERIFIED): the diamonds on the real minimap (Skyy looks).
Scratch: tools/dev/scratch/quests3/hud (deleted at the end unless --keep). Exit 1 on any failure.
"""
import os, sys, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW

VERSION, PREV = "0.3.23", "0.3.22"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyHud-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(HK.arg("--old", os.path.join(HERE, "SkyyHud-%s.jar" % PREV)))
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "quests3", "hud")))
PKG = "com.skyy.hud."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyHud")
EXPECT = {}
ADDED = []


def load_module(path, alias):
    spec = importlib.util.spec_from_file_location(alias, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def t22():
    return load_module(os.path.join(HERE, "test_skyyhud_0.3.22.py"), "hud0322h")


REBUILD = r'''
import os, sys
src, d, ver = sys.argv[1], sys.argv[2], sys.argv[3]
t = open(src, encoding="utf8").read()
for a, b in (("OUT = B.class_out(HERE)", "OUT = B.class_out(%r)" % d), ('jar = os.path.join(HERE, "SkyyHud-%s.jar" % VERSION)', "jar = os.path.join(%r, 'SkyyHud-%s.jar')" % (d, ver))):
    assert t.count(a) == 1, a
    t = t.replace(a, b)
sys.argv = [src]
exec(compile(t, src, "exec"), {"__file__": src, "__name__": "__main__"})
'''


def old_jar(scratch, ver):
    """the x20 checks (the 0.3.20 harness) compare with SkyyHud-<ver>.jar, which the tidy-up removed: rebuild it from its own build script
    INTO the scratch folder (classes + jar there; SkyyHud/ untouched) in a separate process (one JVM per process)"""
    j = os.path.join(HERE, "SkyyHud-%s.jar" % ver)
    if os.path.isfile(j):
        return j
    d = os.path.join(scratch, "old" + ver.replace(".", ""))
    j = os.path.join(d, "SkyyHud-%s.jar" % ver)
    if not os.path.isfile(j):
        import subprocess
        os.makedirs(d, exist_ok=True)
        subprocess.run([sys.executable, "-c", REBUILD, os.path.join(HERE, "build_skyyhud_%s.py" % ver), d, ver], check=True, stdout=subprocess.DEVNULL)
    return j


def run_x20(out, jar, scratch, home):
    sys.argv += ["--old", old_jar(scratch, "0.3.19")]     # read by the 0.3.20 harness module (its OLD_JAR) when it is loaded below
    t22().run_x20(out, jar, scratch, home)


def run_x19(out, jar, scratch, home):
    t22().run_x19(out, jar, scratch, home)


def run_quest(out, jar, scratch, home):
    t22().run_quest(out, jar, scratch, home)


def run_msg(out, jar, scratch, home):
    t22().run_msg(out, jar, scratch, home)


def run_live(out, jar, scratch, home):
    t22().run_live(out, jar, scratch, home)


def run_qk(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    Mm, Png = JClass(PKG + "Minimap"), JClass(PKG + "MmPng")
    MMK = JClass("com.hypixel.hytale.protocol.packets.worldmap.MapMarker")

    def mk(id_, img):
        m = MMK()
        m.id = id_
        m.markerImage = img
        return m
    cases = [("SkyyQuestNpcmarlow", "Temple_GatewayCTA.png", 4), ("SkyyQuestPlace", "Coordinate.png", 4), ("SkyyQuestNpcboard", "Player.png", 4),
             ("SkyyQuestNpcx", "Death.png", 4), ("SkyyQuestNpcy", "Home.png", 4), ("w1", "Warp.png", 0), ("d1", "Death.png", 1), ("h1", "Home.png", 2),
             ("s1", "Spawn.png", 2), ("p1", "Player.png", 3), ("n1", None, 0), (None, "Coordinate.png", 0), ("skyyquestlower", "Coordinate.png", 0)]
    got = [(c[0], int(Mm.kindOf(mk(c[0], c[1])))) for c in cases]
    K.eq(got, [(c[0], c[2]) for c in cases], "QK kindOf: SkyyQuest* ids = 4 (quest) whatever the image; the 0.3.22 kinds unchanged")
    gold, out_ = 0x11223344, None
    px = list(Png.diamond(gold))
    dot = list(Png.dot(gold))
    K.eq(len(px), 256, "QK diamond: 16 x 16")
    ring = set(dot) - set([gold, 0])
    K.check(px[8 * 16 + 8] == gold and px[7 * 16 + 7] == gold and px[0] == 0 and px[15] == 0 and px[255] == 0 and px[240] == 0,
            "QK diamond: filled centre, transparent corners")
    K.check(len(ring) == 1 and set(px) == set([gold, 0]) | ring, "QK diamond: the dot's outline colour, nothing else (%s)" % sorted(set(px)))
    K.check(px[0 * 16 + 7] != gold and px[8 * 16 + 0] != gold and px[1 * 16 + 7] in ring | set([gold]), "QK diamond: a rhombus (the tips thin, the edges outlined)")
    K.check(px != dot, "QK the diamond differs from the round dot")
    a1 = Mm.gen("diamond:%d" % gold)
    a2 = Mm.gen("diamond:%d" % gold)
    d1 = Mm.gen("dot:%d" % gold)
    K.check(a1 is not None and a1.equals(a2) and d1 is not None and str(a1.getName()) != str(d1.getName()) and str(a1.getName()).endswith(".png"),
            "QK gen('diamond:<colour>') = a cached PNG picture, not the dot's: %s / %s" % (a1 and a1.getName(), d1 and d1.getName()))
    raw = bytes(bytearray((int(x) & 0xff) for x in a1.bytes))
    K.check(raw[:8] == b"\x89PNG\r\n\x1a\n", "QK ... a real PNG")
    g = PW.calls(jar)
    geo = g.get("Minimap.pictures", ())
    K.check(PKG + "Minimap.gen" in geo, "QK pictures() builds the kind pictures through gen()")
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(jar)
    cp.appendClassPath(B.SERVER_JAR)
    mi = cp.get(PKG + "Minimap").getDeclaredMethod("pictures").getMethodInfo()
    consts = [str(mi.getConstPool().getStringInfo(i)) for i in range(1, mi.getConstPool().getSize()) if mi.getConstPool().getTag(i) == 8]
    K.check("diamond:" in consts and "dot:" in consts, "QK pictures() names the diamond picture (kind 4) and the dots: %s" % [c for c in consts if c.endswith(":")])
    K.save()


EXPECT.update({
    "MmPng": ["+m diamond"],                   # the quest kind's picture
    "Minimap": ["~m gen", "~m kindOf", "~m pictures"],   # pictures(): the 5-entry kind table with the diamond
    # the version string (the kit's header / export, the ready line)
    "CfgRows": ["~m header"], "CfgFn": ["~m opExport"], "SkyyHudPlugin": ["~m setup"],
})

if __name__ == "__main__":
    HK.run("SkyyHud", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("x20", run_x20), ("x19", run_x19), ("quest", run_quest), ("msg", run_msg), ("qk", run_qk), ("live", run_live)],
           os.path.abspath(__file__), live=(LIVE_DIR, "Skyy_SkyyHud"))
