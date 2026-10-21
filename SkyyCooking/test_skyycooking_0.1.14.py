"""Harness for SkyyCooking 0.1.14 (tools/cooking_0_1_14_patch.py): Skill Trees 3 R3b - the dead 0.3 Cooking nodes are never asked again,
Prep Cook's double-ingredient chance comes from the v3 upgrade Forager's Larder (tools/trees_v3_effects.py).
Build first: python tools/cooking_0_1_14_patch.py && python SkyyCooking/build_skyycooking_0.1.14.py

    python SkyyCooking/test_skyycooking_0.1.14.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.1.13 -> 0.1.14: only the expected members differ (Cook: tree / chances + the new larder / reads; the plugin's setup /
                shutdown; the version texts), non-class entries: manifest.json only
  TR   EXECUTED Cook.tree + Cook.chances (what every Cooking Bench craft's plan() calls) with a fake SkyyTrees (tree:fn:level + tree:fn:bonus
       recording every key asked): Cooking.CGrill / CPrep / CBaker / CIngr / CMaster are NEVER asked; Gourmet / Batch / Frugal / Gourmet II /
       Signature are asked and used as before; Forager's Larder rank 0 = no double ingredients; rank 2 = 6 % (rank x tree.CIngr.per), even
       when SkyyTrees answers a value for the dead Cooking.CIngr (ignored); clamped to max 3; a bad answer = 0; the bench Grade has no Master
       Chef +1 any more; tree:reads:SkyyCooking published / only ours removed
  LIVE every one-time update + CookCfg.load on a scratch COPY of the live Skyy_SkyyCooking (NewBetaTest), twice: start 1 = at most 0.1.13's
       own pending update (no 0.1.14 update exists), start 2 writes nothing
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import skyybuild as B
import trees_v3_effects as V3E

VERSION, OLD = "0.1.14", "0.1.13"
JAR = os.path.join(HERE, "SkyyCooking-%s.jar" % VERSION)
OLD_JAR = os.path.join(HERE, "SkyyCooking-%s.jar" % OLD)
PKG = "com.skyy.cooking."
SCRATCH = HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "st3r3b", "cook"))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyCooking")
EXPECT = {
    "CfgFn": ["~m opExport"],
    "CfgRows": ["~<clinit>", "~m header"],
    "CookCfg": ["~m load"],          # fixer: the new DEFAULTS comments are a constant (no member change)
    "CookIngMig": ["~m migrate"], "CookMig": ["~m logLine", "~m migrate"], "CookTblMig": ["~m migrate"], "CookXpMig": ["~m migrate"],
    "CookNcMig": ["~m migrate"],
    "Cook": sorted(["+f DEAD", "+f I_INGR", "+f FL_KEY", "+f FL_MAX", "+f READS", "+m larder", "+m reads", "~m tree", "~m chances", "~<clinit>"]),
    "SkyyCookingPlugin": ["~m setup", "~m shutdown"],
    "SupCfg": ["~m load"],
}


def run_tr(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JObject, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    Cfg, Cook = JClass(PKG + "CookCfg"), JClass(PKG + "Cook")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyCookTest")
    d = os.path.join(scratch, "tr")
    os.makedirs(d, exist_ok=True)
    Cfg.FILE = Paths.get(os.path.join(d, "cooking.properties"))
    Cfg.load()
    nodes = [str(x) for x in Cfg.NODES]
    K.eq(nodes, ["CGourmet", "CBatch", "CFrugal", "CGrill", "CPrep", "CBaker", "CIngr", "CGourmet2", "CSig", "CMaster"], "TR the node table is unchanged (config rows kept)")
    # fixer: the dead nodes are named unused (a NEW file's comments + the Server Setup row's help), CIngr = Forager's Larder; values unchanged
    dt = str(Cfg.DEFAULTS)
    K.check(all(("# %s: unused since SkyyTrees 0.4" % n_) in dt for n_ in ("CGrill", "CPrep", "CBaker", "CMaster"))
            and "# CIngr: Forager's Larder" in dt and "tree.CGrill.per=0.02" in dt and "tree.CIngr.per=0.03" in dt,
            "LBL a new cooking.properties names CGrill / CPrep / CBaker / CMaster unused and CIngr Forager's Larder (values kept)")
    import zipfile as _zf
    _rows = _zf.ZipFile(jar).read("com/skyy/cooking/CfgRows.class")
    K.check(b"CGrill/CPrep/CBaker/CMaster unused (SkyyTrees 0.4)" in _rows and b"Only a fallback: SkyyTrees' own numbers win" not in _rows,
            "LBL the Server Setup Skill tree row's help names the unused nodes")
    K.eq([nodes[i] for i in range(len(nodes)) if bool(Cook.DEAD[i])], ["CGrill", "CPrep", "CBaker", "CIngr", "CMaster"], "TR the dead nodes")
    K.eq((int(Cook.I_INGR), str(Cook.FL_KEY), int(Cook.FL_MAX)), (6, V3E.key("Cooking", 2, "r1a"), 3), "TR Forager's Larder: slot, key, max")
    br = Cook.bridge()
    LV, BON, ASKED = {}, {}, []

    @JImplements("java.util.function.Function")
    class Lv(object):
        @JOverride
        def apply(self, a):
            ASKED.append(("level", str(a[1])))
            v = LV.get(str(a[1]), 0)
            if v == "boom":
                raise RuntimeError("boom")
            return JString(v) if isinstance(v, str) else JObject(v, "java.lang.Integer")

    @JImplements("java.util.function.Function")
    class Bo(object):
        @JOverride
        def apply(self, a):
            ASKED.append(("bonus", str(a[1])))
            return JObject(BON.get(str(a[1]), 0.0), "java.lang.Double")
    br.put("tree:fn:level", Lv())
    br.put("tree:fn:bonus", Bo())
    u = UUID.fromString("00000000-0000-0000-0000-0000000c0014")
    # every live node at a level, every dead node "answered" too (SkyyTrees would say 0; a stale value must still never be used)
    for n in nodes:
        LV["Cooking." + n] = 5
        BON["Cooking." + n] = 0.2
    t = [int(x) for x in Cook.tree(u)]
    c = [float(x) for x in Cook.chances(u, Cook.tree(u))]
    asked = set(k for _w, k in ASKED)
    dead_asked = sorted(k for k in asked if k in ("Cooking.CGrill", "Cooking.CPrep", "Cooking.CBaker", "Cooking.CIngr", "Cooking.CMaster"))
    K.check(not dead_asked, "TR the dead nodes are NEVER asked from SkyyTrees: %s" % dead_asked)
    K.check(all(("Cooking." + n) in asked for n in ("CGourmet", "CBatch", "CFrugal", "CGourmet2", "CSig")), "TR the live nodes are asked as before")
    K.check(t[0] == 5 and t[1] == 5 and t[2] == 5 and t[7] == 5 and t[8] == 5 and t[3] == t[4] == t[5] == t[9] == 0 and t[6] == 0,
            "TR levels: live nodes 5, dead nodes 0, Forager's Larder rank 0: %s" % t)
    K.check(abs(c[0] - 0.2) < 1e-9 and c[3] == c[4] == c[5] == c[9] == 0.0 and c[6] == 0.0, "TR chances: Gourmet from SkyyTrees, the dead ones 0, no double ingredients: %s" % c)
    LV[str(Cook.FL_KEY)] = 2
    t = Cook.tree(u)
    c = [float(x) for x in Cook.chances(u, t)]
    K.check(int(t[6]) == 2 and abs(c[6] - 0.06) < 1e-9, "TR Forager's Larder rank 2 = 6 %% double ingredients (rank x tree.CIngr.per), the 0.2 answered for Cooking.CIngr ignored: %s" % c[6])
    Cfg.PER[6] = 0.05
    K.check(abs(float(Cook.chances(u, t)[6]) - 0.10) < 1e-9, "TR ... an admin's tree.CIngr.per 0.05 = 10 %% (the row still tunes it)")
    Cfg.PER[6] = 0.03
    LV[str(Cook.FL_KEY)] = 7
    K.eq(int(Cook.tree(u)[6]), 3, "TR a rank of 7 is clamped to the max 3")
    LV[str(Cook.FL_KEY)] = "boom"
    K.eq(int(Cook.tree(u)[6]), 0, "TR a throwing answer = 0")
    LV[str(Cook.FL_KEY)] = "x"
    K.eq(int(Cook.tree(u)[6]), 0, "TR a non-number = 0")
    LV[str(Cook.FL_KEY)] = 1
    # Master Chef: no +1 any more (CMaster is never asked; 0.1.13 gave +1 at level 1)
    tt = Cook.tree(u)
    K.eq(int(Cook.benchGrade(50, tt)), int(Cook.benchGrade(50, JClass("int[]")(10))), "TR the bench Grade has no Master Chef +1 (CMaster dead)")
    br.remove("tree:fn:level")
    K.check([int(x) for x in Cook.tree(u)] == [0] * 10, "TR no SkyyTrees: every level 0 (as 0.1.13)")
    Cook.reads(True)
    K.eq(str(br.get("tree:reads:SkyyCooking")), V3E.key("Cooking", 2, "r1a"), "TR tree:reads:SkyyCooking published")
    br.put("tree:reads:SkyyCooking", "x")
    Cook.reads(False)
    K.eq(str(br.get("tree:reads:SkyyCooking")), "x", "TR shutdown removes only our own value")
    br.put("tree:reads:SkyyCooking", Cook.READS)
    Cook.reads(False)
    K.check(br.get("tree:reads:SkyyCooking") is None, "TR ... ours goes")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Paths = JClass("java.nio.file.Paths")
    Cfg = JClass(PKG + "CookCfg")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyCookTest")

    def snap():
        return dict((os.path.relpath(os.path.join(r, f), home), open(os.path.join(r, f), "rb").read()) for r, ds, fs in os.walk(home) for f in fs)

    def start():
        Cfg.FILE = Paths.get(os.path.join(home, "cooking.properties"))
        for m in ("CookMig", "CookXpMig", "CookTblMig", "CookIngMig", "CookNcMig"):
            JClass(PKG + m).migrate()
        return str(Cfg.load())
    s0 = snap()
    r1 = start()
    s1 = snap()
    r2 = start()
    s2 = snap()
    ch1 = sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k))
    ok1 = all(k == "cooking.properties" or k == "config-changes.log" or k.replace(os.sep, "/").startswith("config-history/") for k in ch1)
    t1 = s1.get("cooking.properties", b"").decode("latin-1")
    K.check(ok1 and (not ch1 or ("maxXpPerMinute=0" in t1 and str(JClass(PKG + "CookNcMig").MARK) in t1)),
            "LIVE start 1: nothing, or only 0.1.13's own one-time update (the live world has not started since 0.1.13; 0.1.14 adds none): %s" % ch1)
    K.check(s1 == s2, "LIVE start 2 writes nothing")
    K.notes.append("LIVE load: %s" % r1[:200])
    K.save()


HK.run(name="SkyyCooking", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
       phases=[("tr", run_tr), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyCooking"))
