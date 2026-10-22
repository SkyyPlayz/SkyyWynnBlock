"""Harness for SkyyTrees 0.4.9 (Balance P7 economy P7b: respec on the coin curve, Wanderer + Cartographer live through SkyyExploration 0.3.3,
the one-time TreeMigP7; tools/trees_0_4_9_patch.py + tools/trees_v3_data.py P7B_TEXT + tools/trees_v3_effects.py EFFECTS). Build first:
    python tools/trees_0_4_9_patch.py && python SkyyTrees/build_skyytrees_0.4.9.py
    python SkyyTrees/test_skyytrees_0.4.9.py [--keep]
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  S    static   the patch re-runs to identical bytes; line endings kept; two classes added (TreeCurve, TreeMigP7); the new texts in the jar
  A    verify   every class loads + initialises
  C    compare  0.4.8 -> 0.4.9: exactly the planned members (EXPECT)
  OLD  the 0.4.8 jar's TreeV3 tables + its default trees.properties (dumped in its own JVM)
  DATA vs 0.4.8: no upgrade max / cost / key / name / row / hook / free perk changed; the texts change exactly on Wanderer + Cartographer;
       R3B + SkyyExploration; only the Exploration gates move (0/3/5/11 -> 0/5/10/15)
  X    exec     EXECUTED: TreeV3.price on the curve (Lv 0 / 1 / 10 / 30 / 50 / 70 / 90 / 100 / 150, n 1 / 2 / clamp 5, the free respec, a
       coins:fn:curve stand-in x2 / broken), curve off = 100 x level x n, respec.base 0 = free; priceText; TreeCfg.load reads respec.base /
       respec.curve (bad / out of range -> clamp / default); the Server Setup rows; Wanderer / Cartographer live only while
       tree:reads:SkyyExploration lists them; tree:fn:level answers their ranks
  MIG  TreeMigP7.update / sameAfter: the 0.4.8 jar's default file -> the marker only; respec.perLevel 250 -> respec.curve=false + row +
       note; respec.curve already there -> kept; the fresh 0.4.9 file = null; CRLF; a file ending inside a continued entry; a second run null
  LIVE START TWICE on a scratch COPY of the live Skyy_SkyyTrees folder (every one-time update in setup order + TreeMigP7): only the marker line
       is added (the live file has no respec.perLevel line), History copy first, every player file reads, start 2 changes nothing
  AA   engine-access audit
NOT COVERED (UNVERIFIED in game): the respec button text on the tree page; SkyyExploration paying the coins (its own harness).
"""
import os, sys, json, subprocess, importlib.util, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "balp7b", "trees")]
import skyybuild as B
import harness_kit as HK
import trees_v3_data as V3D
import trees_v3_effects as V3E
import balance_model as BM

_s = importlib.util.spec_from_file_location("test_skyytrees_0_4_6", os.path.join(HERE, "test_skyytrees_0.4.6.py"))
T46 = importlib.util.module_from_spec(_s)
_argv = list(sys.argv)
_s.loader.exec_module(T46)
sys.argv[:] = _argv

VERSION = "0.4.9"
PKG = "com.skyy.trees."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyTrees-0.4.8.jar")
GEN = os.path.join(HERE, "build_skyytrees_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyytrees_0.4.8.py")
PATCH = os.path.join(TOOLS, "trees_0_4_9_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = T46.LIVE_DIR
ADDED = ["TreeCurve", "TreeMigP7"]
EXPECT = {}
P7B_KEYS = ["Skill.Exploration.b1.r1a", "Skill.Exploration.b1.r3a"]
MK = "Balance P7 economy (SkyyTrees 0.4.9)"
U1 = "77777777-7777-7777-7777-777777777777"


def rcost(L, n=1):   # the model: n x p7_round(2100 x the coin curve default text at L)
    return n * BM.p7_round(2100 * BM.p7_curve_from_text(BM.P7_CURVE_TEXT, max(1, min(100, L))))


def _fn(JImplements, JOverride, f):
    @JImplements("java.util.function.Function")
    class Fn(object):
        @JOverride
        def apply(self, a):
            return f(a)
    return Fn()


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyTrees 0.4.9 - build script') and g.count('VERSION = "0.4.9"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check(g.count("makeClass(") == o.count("makeClass(") + 2 and "tcur, migP7," in g, "S two classes added (TreeCurve, TreeMigP7), written out")
    su = g[g.index("@PKG@.TreeMigP5.run(base);"):]
    K.check(su.index("@PKG@.TreeMigP7.run(base);") < su.index("@PKG@.TreeSk.loadV3(base)"), "S setup: TreeMigP5 -> TreeMigP7 -> the tree rows")
    import zipfile as _zf
    _jb = b"".join(_zf.ZipFile(jar).read(_n) for _n in _zf.ZipFile(jar).namelist() if _n.endswith((".class", ".properties", ".json")))
    for t in (V3D.P7B_TEXT["Exploration.b1.r1a"], V3D.P7B_TEXT["Exploration.b1.r3a"], "Respec follows the coin curve", "Respec cost at Lv 10", MK):
        K.check(t.encode() in _jb, "S in the jar: %s" % t)
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_old(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, OLD_JAR], verify=False)
    o = T46.dump(JClass(PKG + "TreeV3"))
    o["DEFAULTS"] = str(JClass(PKG + "TreeCfg").DEFAULTS)
    json.dump(o, open(os.path.join(scratch, "old048.json"), "w"))
    K.check(len(o["UKEY"]) > 0 and "respec.perLevel=100" in o["DEFAULTS"], "OLD the 0.4.8 tables + default file read (%d upgrades)" % len(o["UKEY"]))
    K.save()


def run_data(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    o, n = json.load(open(os.path.join(scratch, "old048.json"))), T46.dump(JClass(PKG + "TreeV3"))
    for t in ("UMAX", "UCOST", "UKEY", "UNAME", "UROW", "UHK", "TU0", "TUN", "TNAME", "RNUM", "RFK", "RFNAME", "RFTEXT"):
        K.eq(n[t], o[t], "DATA %s unchanged" % t)
    txt = sorted(n["UKEY"][i] for i in range(len(n["UKEY"])) if n["UTEXT"][i] != o["UTEXT"][i])
    K.eq(txt, P7B_KEYS, "DATA the texts change exactly on Wanderer + Cartographer")
    K.eq([n["UTEXT"][n["UKEY"].index(k)] for k in P7B_KEYS], [V3D.P7B_TEXT["Exploration.b1.r1a"], V3D.P7B_TEXT["Exploration.b1.r3a"]], "DATA their texts = tools/trees_v3_data.py P7B_TEXT")
    K.eq(n["R3B"], o["R3B"] + ["SkyyExploration"], "DATA the applier list R3B + SkyyExploration")
    moved, got = [], None
    for tv in range(len(n["TNAME"])):
        for r in range(8):
            if o["GATES"][tv * 8 + r] != n["GATES"][tv * 8 + r]:
                moved.append(n["TNAME"][tv])
        if n["TNAME"][tv] == "Exploration":
            got = ([o["GATES"][tv * 8 + r] for r in range(1, 5)], [n["GATES"][tv * 8 + r] for r in range(1, 5)])
    K.check(set(moved) == {"Exploration"}, "DATA only the Exploration gates move: %s" % sorted(set(moved)))
    K.eq(got, ([0, 3, 5, 11], [0, 5, 10, 15]), "DATA Exploration gates 0/3/5/11 -> 0/5/10/15 (Skyy's 0/5/10/15)")
    K.check(bool(V3E.check()) and not [e for e in V3E.EFFECTS if e[0] == "Exploration" and e[4].startswith("xp.")], "DATA trees_v3_effects.check(): no Exploration XP row")
    K.save()


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JString, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    Paths, UUID, D_, I_ = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("java.lang.Double"), JClass("java.lang.Integer")
    St, Cfg, V, TC = JClass(PKG + "TreeStore"), JClass(PKG + "TreeCfg"), JClass(PKG + "TreeV3"), JClass(PKG + "TreeCurve")
    d = os.path.join(scratch, "exec")
    os.makedirs(os.path.join(d, "players"), exist_ok=True)
    St.DIR = Paths.get(os.path.join(d, "players"))
    fp = os.path.join(d, "trees.properties")
    Cfg.FILE = Paths.get(fp)
    Cfg.load()
    K.check(int(Cfg.V3_RB10) == 2100 and bool(Cfg.V3_RCURVE) and int(Cfg.V3_RBASE) == 100, "X defaults: respec.base 2100, respec.curve on, respec.perLevel 100")
    br = St.bridge()
    br.remove("coins:fn:curve")
    T46._pfile(d, U1, {"Skill.Exploration.b1.r1a": 5, "Skill.Exploration.b1.r3a": 3, "Skill.Exploration.b1.r1b": 3})
    u1 = UUID.fromString(U1)
    data = St.data(u1)
    K.check(not bool(data.bad), "X the player file reads")
    tv = [t for t in range(len(V.TNAME)) if str(V.TNAME[t]) == "Exploration"][0]
    data.rsFree[tv] = False
    K.eq(int(V.price(data, tv, 50)), 0, "X the first respec of a run is free")
    data.rsFree[tv] = True
    lv = (0, 1, 10, 30, 50, 70, 90, 100, 150)
    data.rsN[tv] = 0
    K.eq([int(V.price(data, tv, L)) for L in lv], [rcost(L) for L in lv], "X price on the curve (n 1) = the model at Lv %s" % (lv,))
    K.eq([int(V.price(data, tv, L)) for L in (10, 50, 90)], [2100, 77500, 980000], "X Lv 10 2,100 / Lv 50 77,500 / Lv 90 980,000")
    data.rsN[tv] = 1
    K.eq(int(V.price(data, tv, 50)), 2 * 77500, "X the 2nd paid respec = x2")
    data.rsN[tv] = 9
    K.eq(int(V.price(data, tv, 50)), 5 * 77500, "X the n-th paid respec clamps at respec.maxSteps 5")
    data.rsN[tv] = 0
    br.put("coins:fn:curve", _fn(JImplements, JOverride, lambda a: D_.valueOf(2.0 * float(TC.curveOwn(int(a))))))
    K.eq(int(V.price(data, tv, 50)), BM.p7_round(2100 * 73.6), "X a coins:fn:curve twice the default -> 2,100 x 73.6 rounded")

    def boom(a):
        raise RuntimeError("x")
    br.put("coins:fn:curve", _fn(JImplements, JOverride, boom))
    K.eq(int(V.price(data, tv, 50)), 77500, "X a throwing coins:fn:curve = the built-in curve")
    br.remove("coins:fn:curve")
    txt = str(V.priceText(data, tv, 50))
    K.check(txt == "Respec " + str(JClass(PKG + "TreeDefs").grp(77500)) + " coins", "X priceText: %s" % txt)
    Cfg.V3_RCURVE = False
    K.eq([int(V.price(data, tv, L)) for L in (0, 10, 50)], [100, 1000, 5000], "X respec.curve off = the old 100 x level x n")
    Cfg.V3_RCURVE = True
    Cfg.V3_RB10 = 0
    K.eq(int(V.price(data, tv, 50)), 0, "X respec.base 0 = free")
    K.eq((int(TC.times(9000000000000000, 5)), int(TC.times(0, 5)), int(TC.round(1e20))), (1000000000000000, 0, 1000000000000000), "X TreeCurve guards (cap 1e15)")
    # the loader
    for txt_, want in (("respec.base=5000\nrespec.curve=false\n", (5000, False)), ("respec.base=-5\n", (0, True)), ("respec.base=abc\nrespec.curve=maybe\n", (2100, True)),
                       ("respec.base=99999999999\n", (1000000000, True)), ("", (2100, True))):
        open(fp, "w").write(txt_)
        Cfg.load()
        K.eq((int(Cfg.V3_RB10), bool(Cfg.V3_RCURVE)), want, "X TreeCfg.load %r" % txt_.strip())
    os.remove(fp)
    Cfg.load()
    rows = dict((str(r[0]), [str(x) for x in list(r)]) for r in JClass(PKG + "CfgRows").header()[7])
    K.check(rows.get("respec.curve", [""] * 5)[3:5] == ["bool", "true"] and rows.get("respec.base", [""] * 5)[3:5] == ["int", "2100"]
            and "coin curve off" in rows["respec.perLevel"][10], "X Server Setup rows Trees -> General: respec.curve (bool true), respec.base (int 2100)")
    K.check("\nrespec.curve=true\nrespec.base=2100\n" in str(Cfg.DEFAULTS) and str(Cfg.DEFAULTS).count(MK) == 1, "X the fresh file holds both lines + the marker once")
    # Wanderer / Cartographer: live only while SkyyExploration lists them; tree:fn:level answers their ranks

    @JImplements("java.util.function.Function")
    class Lv(object):
        @JOverride
        def apply(self, a):
            return I_(60)
    br.put("skill:fn:level", Lv())
    ui = dict((str(V.UKEY[i]), i) for i in range(len(V.UKEY)))
    K.check(not any(bool(V.live(ui[k])) for k in P7B_KEYS), "X without tree:reads:SkyyExploration Wanderer / Cartographer are coming soon")
    br.put("tree:reads:SkyyExploration", JString(V3E.reads_csv("SkyyExploration")))
    K.check(all(bool(V.live(ui[k])) for k in P7B_KEYS), "X with SkyyExploration 0.3.3's tree:reads they are live")
    K.eq((int(V.skillRank(u1, P7B_KEYS[0])), int(V.skillRank(u1, P7B_KEYS[1]))), (5, 3), "X tree:fn:level answers Wanderer 5 / Cartographer 3")
    g = V.gates(tv)
    K.eq([int(g[n]) for n in range(1, 5)], [0, 5, 10, 15], "X Exploration gates 0 / 5 / 10 / 15")
    K.save()


def run_mig(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    M, Cfg = JClass(PKG + "TreeMigP7"), JClass(PKG + "TreeCfg")
    OLD = json.load(open(os.path.join(scratch, "old048.json")))["DEFAULTS"]
    NEW = str(Cfg.DEFAULTS)
    P = lambda t: T46._props(t.encode("latin-1"))
    K.check(M.update(JString(NEW)) is None, "MIG the fresh 0.4.9 file carries the marker: nothing to do")
    r = M.update(JString(OLD))
    K.check(r is not None and not bool(r[1]) and list(r[3]) == [] and str(r[0]) == OLD + str(M.MARK_LINE) + "\n" and P(str(r[0])) == P(OLD),
            "MIG the 0.4.8 jar's default file (respec.perLevel=100): only the marker appended")
    K.check(M.update(r[0]) is None, "MIG a second run = null (the marker)")
    hand = OLD.replace("\nrespec.perLevel=100\n", "\nrespec.perLevel=250\n")
    rh = M.update(JString(hand))
    ph = P(str(rh[0]))
    K.check(bool(rh[1]) and ph.get("respec.curve") == "false" and ph.get("respec.perLevel") == "250" and [str(x) for x in rh[3]] == ["respec.curve", "true", "false"]
            and "respec.perLevel=250 kept" in str(rh[2]) and str(rh[0]).endswith("respec.curve=false\n" + str(M.MARK_LINE) + "\n"),
            "MIG respec.perLevel 250 (an admin's): respec.curve=false appended + note + one row, the marker last: %s" % str(rh[2])[:120])
    K.check(bool(M.sameAfter(JString(hand).getBytes("ISO-8859-1"), JString(str(rh[0])).getBytes("ISO-8859-1"), True))
            and not bool(M.sameAfter(JString(hand).getBytes("ISO-8859-1"), JString(str(rh[0]) + "x=1\n").getBytes("ISO-8859-1"), True)), "MIG sameAfter: only respec.curve added")
    h2 = OLD.replace("\nrespec.perLevel=100\n", "\nrespec.perLevel = 100.0\n")
    K.check(not bool(M.update(JString(h2))[1]), "MIG respec.perLevel '100.0' = the default (no respec.curve line)")
    nol = OLD.replace("\nrespec.perLevel=100\n", "\n")
    K.check(not bool(M.update(JString(nol))[1]), "MIG no respec.perLevel line (the live case) = the default: marker only")
    has = hand + "respec.curve=true\n"
    rk = M.update(JString(has))
    K.check(not bool(rk[1]) and P(str(rk[0])).get("respec.curve") == "true" and "already" in str(rk[2]), "MIG a file with respec.curve keeps it")
    crlf = hand.replace("\n", "\r\n")
    rc = M.update(JString(crlf))
    K.check(str(rc[0]).endswith("respec.curve=false\r\n" + str(M.MARK_LINE) + "\r\n") and "\n" not in str(rc[0]).replace("\r\n", ""), "MIG CRLF kept")
    dang = hand.rstrip("\n") + "\nfoo=bar\\"
    rd_ = M.update(JString(dang))
    K.check(P(str(rd_[0])).get("respec.curve") == "false" and P(str(rd_[0])).get("foo") == "bar", "MIG a file ending inside a continued entry: nothing joins it")
    K.save()


def live_start(home):
    from jpype import JClass
    out, bad = T46.live_start(home)
    out.append(str(JClass(PKG + "TreeMigP7").run(JClass("java.nio.file.Paths").get(home))))
    return out, bad


def run_live(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    from jpype import JClass
    fp = os.path.join(home, "trees.properties")
    t0 = open(fp, "rb").read()
    Cfg, Rows, Hist, CLog = JClass(PKG + "TreeCfg"), JClass(PKG + "CfgRows"), JClass(PKG + "CfgHist"), JClass(PKG + "CfgLog")
    msgs, bad = live_start(home)
    print("   live start 1:", [m[:100] for m in msgs if m])
    t1 = open(fp, "rb").read()
    po, pn = T46._props(t0), T46._props(t1)
    dk = sorted(k for k in set(po) | set(pn) if po.get(k) != pn.get(k))
    K.check(dk in ([], ["Mining.MFortune.per"]), "LIVE start 1: no setting changes (at most 0.4.5's TreeMigP5 line): %s" % dk)
    K.check(MK in msgs[-1] and t1.count(MK.encode()) == 1 and "respec.perLevel" not in po, "LIVE TreeMigP7 ran: the marker added (the live file has no respec.perLevel line): %s" % msgs[-1][:120])
    K.check(any(open(os.path.join(r_, f_), "rb").read() == t0 for r_, _d, fs in os.walk(os.path.join(home, "config-history")) for f_ in fs if "trees.properties" in f_),
            "LIVE config-history holds the file as it was before TreeMigP7")
    K.check(int(Cfg.V3_RB10) == 2100 and bool(Cfg.V3_RCURVE), "LIVE the migrated live copy loads: respec on the curve, base 2100")
    K.eq(bad, [], "LIVE every player file reads")
    h1 = T46.tree_hash(home)
    msgs2, bad2 = live_start(home)
    K.check(T46.tree_hash(home) == h1 and bad2 == [] and msgs2[-1] == "", "LIVE start 2 changes nothing")
    K.save()


EXPECT.update({   # checked by hand 2026-10-22: the version / default texts (CfgFile, CfgFn, CfgRows, TreeCfg <clinit>), the 2 respec rows, setup's
                 # TreeMigP7 call + ready line, TreeCfg's two new fields read in apply(), TreeV3's price + the P7b tables (texts, gates, R3B) in <clinit>
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "SkyyTreesPlugin": ["~m setup"],
    "TreeCfg": ["+f V3_RB10", "+f V3_RCURVE", "~<clinit>", "~m apply", "~m load"], "TreeV3": ["~<clinit>", "~m price"]})

if __name__ == "__main__":
    HK.run(name="SkyyTrees", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("old", run_old), ("data", run_data), ("exec", run_exec), ("mig", run_mig), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyTrees"))
