"""Harness for SkyyMobs 0.1.17 (elem1: the Wynn element mob side - tools/mobs_0_1_17_patch.py).
Build first:
    python tools/mobs_0_1_17_patch.py && python SkyyMobs/build_skyymobs_0.1.17.py
    python SkyyMobs/test_skyymobs_0.1.17.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  S  static   the patch re-runs to identical bytes (--out), line endings kept, exactly 3 new classes, no new command / system
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.16 -> 0.1.17 (EXPECT below)
  X  exec     EXECUTES MobElem on the defaults (spec 10.6: Yeti Fire +25 / Water -25, Dragon_Fire Fire -50 as a boss, Trork 0, aliases), the
              override columns, a live edit through MobCfg.elemEdit (table, wheel, numbers), the check= hooks, the bridge Functions on bad
              args (never throw), mob:elem:wheel / numbers, the hit cut maths (cutBy) and cutHit with a stub gear:fn:elemDef +
              gear:elem:defScale, the plate texts (suffix, {element} token, plate off, colour markup) + isOurs on them, the health
              signature changing on a table edit (the loaded mobs re-apply = their plates)
  D  live     start twice on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyMobs (every migration + MobCfg.load + MobSpoils.loadV3): 0.1.17
              writes nothing, start 2 changes nothing, the live file (no elem lines) runs with the defaults
  AA engine-access audit
NOT COVERED (UNVERIFIED in game): LevelDamage's two cutHit calls inside the ECS damage dispatch (the pure method they call is executed here);
the client drawing the coloured element part of a plate (plate.colorOn is a trial).
Scratch: tools/dev/scratch/elem1/mobs (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.1.17"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "elem1", "mobs")]
import skyybuild as B
import harness_kit as HK

GEN = os.path.join(HERE, "build_skyymobs_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyymobs_0.1.16.py")
PATCH = os.path.join(ROOT, "tools", "mobs_0_1_17_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMobs-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMobs-0.1.16.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.mobs."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyMobs")
ADDED = ["MobElem", "MobElemFn", "MobElemOfFn"]
EXPECT = {
    "MobCfg": ["+f ELEM_BOSS", "+f ELEM_MOBS", "+f ELEM_PLATE", "+f ELEM_RESIST", "+f ELEM_SHARE", "+f ELEM_WEAK", "+f ELEM_WHEEL", "+m elemEdit",
               "~<clinit>", "~m apply", "~m derive", "~m load", "~m reloadAll", "~m useDefaults"],          # load / reloadAll / useDefaults: the inlined DEF_CFG text
    "MobPlateStep": ["~m run"],          # /mobs platetest puts the element plate back
    "MobLevel": ["+m plateText", "~m apply", "~m isOursFor", "~m plateText"],
    "LevelDamage": ["~m handle"], "MobHooks": ["+m checkElemMobs", "+m checkWheel"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CfgFile": ["~<clinit>"],
    "SkyyMobsPlugin": ["~m setup", "~m shutdown"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
U = "00000000-0000-0000-0000-000000000117"


def tree_hash(root):
    o = {}
    for d, _x, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            o[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return o


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyMobs 0.1.17 - build script') and g.count('VERSION = "0.1.17"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("),
          g.count("makeClass(") - o.count("makeClass(")), (0, 0, 3), "S no new system / command, 3 new classes")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_exec(out, jar, scratch, home):
    import jpype
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    C, E, Lv, H = JClass(PKG + "MobCfg"), JClass(PKG + "MobElem"), JClass(PKG + "MobLevel"), JClass(PKG + "MobHooks")
    Fn, FnOf = JClass(PKG + "MobElemFn")(), JClass(PKG + "MobElemOfFn")()
    Obj = JClass("java.lang.Object")
    uu = JClass("java.util.UUID").fromString(U)
    C.useDefaults()
    d = str(C.DEF_CFG)
    for k in ("elem.mobs=", "elem.weak=25", "elem.resist=25", "elem.bossResist=50", "elem.mobShare=30", "elem.plate=true", "elem.wheel=Earth>Thunder>Water>Fire>Air"):
        K.check(("\n" + k) in d, "X the default file carries %s" % k)

    def m(role, el):
        return int(E.modOf(role, el))
    K.eq([m("Yeti", "Fire"), m("Yeti", "Water"), m("Yeti", "Thunder")], [25, -25, 0], "X Yeti: Fire +25 (ice melts), Water -25, Thunder 0")
    K.eq([m("Dragon_Fire", "Fire"), m("Dragon_Fire", "Water"), m("Dragon_Frost", "Water"), m("Dragon_Frost", "Thunder")], [-50, 25, -50, 25],
         "X the dragons keep their element: own element -50 as bosses, the wheel's beater +25")
    K.eq([m("Trork_Warrior", e) for e in ("Earth", "Thunder", "Water", "Fire", "Air")], [0, 0, 0, 0, 0], "X Trork (no row) = 0 for every element")
    K.eq([m("Fen_Stalker", "Lightning"), m("Fen_Stalker", "Thunder"), m("Pterodactyl", "Wind"), m("Pterodactyl", "Fire")], [25, 25, -25, 25],
         "X old names Lightning / Wind read as Thunder / Air")
    K.eq([m("Skeleton_Burnt_Knight", "Water"), m("Skeleton_Burnt_Knight", "Fire"), m("Skeleton_Archer", "Fire"), m("Skeleton_Frost_Mage", "Fire")], [25, -25, 0, 25],
         "X the most specific pattern wins (Skeleton_Burnt* / Skeleton_Frost*; elem1fix: plain skeletons neutral, frost skeletons weak to Fire)")
    K.eq([m("Crawler_Void", "Earth"), m("Crawler_Void", "Fire"), m("Crawler_Void", "Thunder"), m("Scarak_Fighter", "Water"), m("Scarak_Fighter", "Air")], [25, 0, -25, 0, 25],
         "X elem1fix (the pure wheel, Skyy Q7): Void Thunder weak Earth, not Fire; Scarak Earth weak Air, not Water")
    K.eq([str(FnOf.apply("Yeti")), FnOf.apply("Trork_Warrior") is None, str(FnOf.apply("Golem_Firesteel"))], ["Water", True, "Fire"], "X mob:fn:elemOf")
    K.eq([int(Fn.apply(jpype.JArray(Obj)(["Yeti", "Fire"]))), int(Fn.apply(None)), int(Fn.apply("Yeti")), int(Fn.apply(jpype.JArray(Obj)(["Yeti"]))),
          int(Fn.apply(jpype.JArray(Obj)(["Yeti", "Ice"]))), int(Fn.apply(jpype.JArray(Obj)([None, "Fire"])))], [25, 0, 0, 0, 0, 0],
         "X mob:fn:elem: the Object[] form + bad args = 0, never throws")
    K.eq([str(br.get("mob:elem:wheel")), str(br.get("mob:elem:numbers"))], ["Earth>Thunder>Water>Fire>Air", "25;25;50"], "X mob:elem:wheel + numbers")
    K.check(br.get("mob:elem:custom") is not None and not bool(br.get("mob:elem:custom")), "X elem1fix2: mob:elem:custom FALSE on the default table")
    # the hooks
    K.check(H.checkElemMobs("elem.mobs", "Yeti=Ice") is not None and H.checkElemMobs("elem.mobs", "Yeti") is not None
            and H.checkElemMobs("elem.mobs", "Yeti=Water/Fire") is not None and H.checkElemMobs("elem.mobs", "*=Fire") is not None
            and H.checkElemMobs("elem.mobs", "Yeti=Water//Fire, Trork*=none/none/Air") is None and H.checkElemMobs("elem.mobs", None) is None,
            "X checkElemMobs refuses an unknown word / no = / two columns / a lone *, takes blanks and none")
    K.check(H.checkWheel("elem.wheel", "Earth>Earth>Water>Fire>Air") is not None and H.checkWheel("elem.wheel", "Earth>Thunder>Water>Fire") is not None
            and H.checkWheel("elem.wheel", "Fire>Water>Earth>Thunder>Air") is None, "X checkWheel: the 5 names once each")
    # a live edit: the override columns, the wheel, the numbers, the health / plate signature
    sig0 = str(C.HP_SIG)
    C.ELEM_MOBS = "Trork*=Fire, Trork_Warrior=Earth/Air/Thunder, Kweebec*=none"
    C.ELEM_WEAK, C.ELEM_RESIST, C.ELEM_BOSS = 40, 10, 60
    C.elemEdit(None)
    K.eq([m("Trork_Warrior", "Air"), m("Trork_Warrior", "Thunder"), m("Trork_Warrior", "Earth"), m("Trork_Brawler", "Water"), m("Trork_Brawler", "Fire"),
          m("Trork_Chieftain", "Fire"), m("Kweebec_Razorleaf", "Fire"), m("Yeti", "Fire")], [-10, 40, 0, 40, -10, -60, 0, 0],
         "X live edit: override columns, numbers 40 / 10 / 60 (Trork_Chieftain is a boss), Kweebec none, Yeti gone")
    K.check(str(C.HP_SIG) != sig0 and str(br.get("mob:elem:numbers")) == "40;10;60", "X the edit changes the health signature (plates re-apply) + numbers")
    K.check(bool(br.get("mob:elem:custom")), "X elem1fix2: an edited Mob elements table = mob:elem:custom TRUE (SkyyMenu's chart drops the default exceptions)")
    C.ELEM_WHEEL = "Fire>Water>Earth>Thunder>Air"
    C.elemEdit(None)
    K.eq([m("Trork_Brawler", "Air"), m("Trork_Brawler", "Water"), str(br.get("mob:elem:wheel"))], [40, 0, "Fire>Water>Earth>Thunder>Air"],
         "X a new wheel: Fire's beater is now Air (the one before it, cyclic)")
    C.ELEM_WHEEL = "nonsense"
    C.elemEdit(None)
    K.eq(str(br.get("mob:elem:wheel")), "Earth>Thunder>Water>Fire>Air", "X a bad wheel (hand edit) = the default + WARN")
    C.useDefaults()
    # the hit cut
    K.check(abs(float(E.cutBy(100.0, 30, 0, 100.0)) - 100.0) < 1e-9 and abs(float(E.cutBy(100.0, 30, 100, 100.0)) - 85.0) < 1e-9
            and abs(float(E.cutBy(100.0, 30, 10, 100.0)) - (100 - 30 * 10 / 110.0)) < 1e-9 and abs(float(E.cutBy(100.0, 0, 50, 100.0)) - 100.0) < 1e-9
            and abs(float(E.cutBy(200.0, 100, 1000000, 100.0)) - 200.0 * 100 / 1000100.0) < 1e-6, "X cutBy = amount - share x D / (S + D)")

    @JImplements("java.util.function.Function")
    class Def(object):
        def __init__(self):
            self.calls = []

        @JOverride
        def apply(self, o):
            self.calls.append((str(o[0]), str(o[1])))
            return JClass("java.lang.Integer").valueOf(20 if str(o[1]) == "Water" else 0)
    K.check(abs(float(E.cutHit("Yeti", uu, 100.0)) - 100.0) < 1e-9, "X no SkyyGear (no gear:fn:elemDef) = the hit unchanged")
    dd = Def()
    br.put("gear:fn:elemDef", dd)
    K.check(abs(float(E.cutHit("Yeti", uu, 100.0)) - (100 - 30 * 20 / 120.0)) < 1e-9 and dd.calls[-1] == (U, "Water"), "X cutHit: Yeti's Water part cut by 20 Water Defence (S 100)")
    K.check(abs(float(E.cutHit("Golem_Firesteel", uu, 100.0)) - 100.0) < 1e-9 and abs(float(E.cutHit("Trork_Warrior", uu, 100.0)) - 100.0) < 1e-9,
            "X a Fire mob vs 0 Fire Defence / a mob without element = unchanged")
    br.put("gear:elem:defScale", JClass("java.lang.Integer").valueOf(20))
    K.check(abs(float(E.cutHit("Yeti", uu, 100.0)) - (100 - 30 * 20 / 40.0)) < 1e-9, "X gear:elem:defScale 20 is used")
    br.remove("gear:elem:defScale")
    C.ELEM_SHARE = 0
    C.elemEdit(None)
    K.check(not bool(E.ANY) and abs(float(E.cutHit("Yeti", uu, 100.0)) - 100.0) < 1e-9, "X elem.mobShare 0 = no element hits (ANY off)")
    C.useDefaults()
    # the plates
    K.eq(str(Lv.plateText(32, "Yeti", "Yeti")), "[Lv 32] Yeti - Water", "X plate: [Lv 32] Yeti - Water (spec test 2)")
    K.eq(str(Lv.plateText(5, "Trork Warrior", "Trork_Warrior")), "[Lv 5] Trork Warrior", "X plate: no element = the 0.1.16 text")
    C.ELEM_PLATE = False
    K.eq(str(Lv.plateText(32, "Yeti", "Yeti")), "[Lv 32] Yeti", "X elem.plate off = no element")
    C.ELEM_PLATE = True
    C.FORMAT = "[Lv {level}]{element} {name}"
    K.eq([str(Lv.plateText(32, "Yeti", "Yeti")), str(Lv.plateText(32, "Trork", "Trork_Warrior")), str(Lv.plateText(32, "Trork", None))],
         ["[Lv 32] - Water Yeti", "[Lv 32] Trork", "[Lv 32] Trork"], "X the {element} token")
    K.check(bool(Lv.isOurs("[Lv 32] - Water Yeti")) and bool(Lv.isOurs("[Lv 32] Trork")), "X isOurs knows the token plates")
    C.FORMAT = "[Lv {level}] {name}"
    C.COLOR_ON = True
    t = str(Lv.plateText(32, "Yeti", "Yeti"))
    K.check(t.endswith("<color=#4fa8ff> - Water</color>") and t.startswith("<color=#") and bool(Lv.isOurs(t)) and str(Lv.plain(t)) == "[Lv 32] Yeti - Water",
            "X colour markup: the element part in the Water colour, plain() strips it: %s" % t)
    C.COLOR_ON = False
    K.check(bool(Lv.isOurs("[Lv 32] Yeti - Water")), "X isOurs: an element plate is ours (a mob that stops qualifying still loses it)")
    K.check("elements: 34 element rows" in "elements: " + str(E.text()), "X ready line part: %s" % E.text())
    C.useDefaults()
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    Cfg, S = JClass(PKG + "MobCfg"), JClass(PKG + "MobSpoils")
    P = JClass("java.nio.file.Paths")
    txt = open(os.path.join(home, "config.properties"), encoding="latin-1").read()

    def start():
        Cfg.DIR = P.get(home)
        Cfg.FILE = P.get(os.path.join(home, "config.properties"))
        Cfg.BANDS = P.get(os.path.join(home, "bands.properties"))
        o = [str(JClass(PKG + m).run(P.get(home))) for m in ("MobMig", "MobMig14", "MobMig11", "MobMig12", "MobMigP4")]
        Cfg.load()
        o.append(str(S.loadV3(P.get(home))))
        return o
    h0 = tree_hash(home)
    o1 = start()
    h1 = tree_hash(home)
    ch = sorted(k for k in set(h0) | set(h1) if h0.get(k) != h1.get(k))
    K.check(not ch, "D start 1 on a scratch COPY of the live data: 0.1.17 writes nothing (%s; %s)" % (ch, [x[:60] for x in o1 if x]))
    o2 = start()
    K.check(tree_hash(home) == h1 and all(x == "" for x in o2[:-1]), "D start 2 changes nothing")
    if "elem." not in txt:
        K.check(int(JClass(PKG + "MobElem").modOf("Yeti", "Fire")) == 25 and str(br.get("mob:elem:wheel")) == "Earth>Thunder>Water>Fire>Air",
                "D the live file (no elem lines) runs with the element defaults")
    K.check(Cfg.ELEM_SHARE == 30 or "elem.mobShare" in txt, "D mob share in force: %s" % Cfg.ELEM_SHARE)
    K.save()


HK.run("SkyyMobs", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("exec", run_exec), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyMobs"))
