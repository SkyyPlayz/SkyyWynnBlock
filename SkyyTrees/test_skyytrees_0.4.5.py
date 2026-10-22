"""Harness for SkyyTrees 0.4.5 (Balance P5, the SkyyTrees part: Rich Seams +2.5 Mining Fortune a rank, the Masterwork Pick / Accessory
Plates texts, the Mining tree Fortune budget 40, the one-time TreeMigP5; tools/trees_0_4_5_patch.py + tools/trees_v3_data.py +
tools/trees_v3_effects.py). Build first:
    python tools/trees_0_4_5_patch.py && python SkyyTrees/build_skyytrees_0.4.5.py
    python SkyyTrees/test_skyytrees_0.4.5.py [--keep]
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  S    static   the patch re-runs to identical bytes; line endings kept; one class added (TreeMigP5); setup order 323 -> 324 -> P5
  A    verify   every class loads + initialises
  C    compare  0.4.4 -> 0.4.5: exactly the planned members (EXPECT)
  OLD  the 0.4.4 jar's TreeV3 tables + TreeCfg.PER (dumped in its own JVM)
  DATA vs 0.4.4: only the three upgrade texts changed (Rich Seams / Masterwork Pick / Accessory Plates), gates / maxima / keys unchanged;
       TreeCfg.PER of Mining.MFortune 0.1 -> 0.025 and nothing else; the default file says 0.025 + the P5 marker; trees_v3_effects.check():
       the Mining tree's whole Fortune at max = 40.0 <= TREE_FORT_MAX; Rich Seams at 3 ranks EXECUTED through the jar's own value path
       (TreeCfg.PER x ranks x 100 = 7.5)
  MIG  TreeMigP5.mP5Update (pure text) on every shape: the old default (LF / CRLF / "0.10"), hand-edited (kept + named), doubled /
       continued (kept), missing line, already 0.025, a marked file; run() on real files: History copy, one change-log line, second start
       = nothing, TreeCfg.load reads 0.025; an old 0.3.22 file goes 0.01 -> 0.1 (TreeMig323) -> 0.025 (TreeMigP5) in one start
  LIVE START TWICE on a scratch COPY of the live Skyy_SkyyTrees folder (setup's update chain): trees.properties changes ONLY
       Mining.MFortune.per 0.1 -> 0.025 (Properties) + the marker line; History copy; one change-log line; the second start changes nothing
  AA   engine-access audit
NOT COVERED (UNVERIFIED in game): the page look; the appliers' numbers (their own harnesses: SkyyGear 0.3.35, SkyyAccessories 0.5.30).
"""
import os, sys, json, hashlib, subprocess, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "balp5", "trees")]
import skyybuild as B
import harness_kit as HK
import deploy_set as DS
import trees_v3_data as V3D
import trees_v3_effects as V3E

VERSION = "0.4.5"
PKG = "com.skyy.trees."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyTrees-0.4.4.jar")
GEN = os.path.join(HERE, "build_skyytrees_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyytrees_0.4.4.py")
PATCH = os.path.join(TOOLS, "trees_0_4_5_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = os.path.join(B.HYTALE, "UserData", "Saves", DS.WORLD, "mods", "Skyy_SkyyTrees")
ADDED = ["TreeMigP5"]
EXPECT = {
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "SkyyTreesPlugin": ["~m setup"], "TreeCfg": ["~m load"],   # the version text (DEFAULTS is a compile-time constant)
    "TreeDefs": ["~<clinit>"],   # D_PER (Mining.MFortune 0.025)
    "TreeV3": ["~<clinit>"],     # UTEXT (the three texts)
}
TEXT_KEYS = {"Skill.Mining.b1.r1b": "+2.5 Mining Fortune per rank", "Skill.Mining.b2.r6": "+5 Mining Fortune",
             "Skill.Combat.b2.r4a": "+0.5% max health"}
TABLES = ("GATES", "UMAX", "UCOST", "UKEY", "UTEXT", "UNAME", "UHK", "UROW", "TU0", "TUN", "TNAME", "RNUM")


def tree_hash(root):
    o = {}
    for d, _x, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            o[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return o


def dump(V, C):
    o = {}
    for n in TABLES:
        o[n] = [int(y) if isinstance(y, int) else str(y) for y in getattr(V, n)]
    o["PER"] = [float(x) for x in C.PER]
    return o


def _props(b):
    from jpype import JClass
    p = JClass("java.util.Properties")()
    p.load(JClass("java.io.ByteArrayInputStream")(b))
    return {str(k): str(p.getProperty(k)) for k in p.stringPropertyNames()}


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyTrees 0.4.5 - build script') and g.count('VERSION = "0.4.5"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.eq(g.count("makeClass(") - o.count("makeClass("), 1, "S one class added (TreeMigP5)")
    su = g[g.index("public void setup() {"):]
    K.check(su.index("TreeMig323.run(base);") < su.index("TreeMig324.run(base);") < su.index("TreeMigP5.run(base);") < su.index("CfgPub.start"),
            "S setup: TreeMig323 -> TreeMig324 -> TreeMigP5 -> CfgPub.start")
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
    o = dump(JClass(PKG + "TreeV3"), JClass(PKG + "TreeCfg"))
    json.dump(o, open(os.path.join(scratch, "old044.json"), "w"))
    K.check(len(o["UKEY"]) > 0 and len(o["PER"]) > 50, "OLD the 0.4.4 tables read (%d upgrades, %d nodes)" % (len(o["UKEY"]), len(o["PER"])))
    K.save()


def run_data(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    V, C, D = JClass(PKG + "TreeV3"), JClass(PKG + "TreeCfg"), JClass(PKG + "TreeDefs")
    o, n = json.load(open(os.path.join(scratch, "old044.json"))), dump(V, C)
    for t in ("GATES", "UMAX", "UCOST", "UKEY", "UNAME", "UHK", "UROW", "TU0", "TUN", "TNAME", "RNUM"):
        K.eq(n[t], o[t], "DATA %s unchanged" % t)
    txt = sorted(n["UKEY"][i] for i in range(len(n["UKEY"])) if n["UTEXT"][i] != o["UTEXT"][i])
    K.eq(txt, sorted(TEXT_KEYS), "DATA only the three P5 upgrade texts changed")
    for k, w in TEXT_KEYS.items():
        K.check(w in n["UTEXT"][n["UKEY"].index(k)], "DATA %s text says %r: %s" % (k, w, n["UTEXT"][n["UKEY"].index(k)]))
    pd = [i for i in range(len(n["PER"])) if n["PER"][i] != o["PER"][i]]
    names = [str(D.D_ID[i]) if hasattr(D, "D_ID") else str(i) for i in range(len(n["PER"]))]
    K.check(len(pd) == 1 and abs(o["PER"][pd[0]] - 0.1) < 1e-12 and abs(n["PER"][pd[0]] - 0.025) < 1e-12,
            "DATA TreeCfg.PER: exactly one node 0.1 -> 0.025 (Mining.MFortune): %s" % [(names[i], o["PER"][i], n["PER"][i]) for i in pd])
    dt = str(C.DEFAULTS)
    K.check("\nMining.MFortune.per=0.025\n" in dt and "Balance P5 power (SkyyTrees 0.4.5)" in dt and "\nMining.MFortune.per=0.1\n" not in dt,
            "DATA the new server's default file: Mining.MFortune.per=0.025 + the P5 marker")
    K.check(bool(V3E.check()) and abs(V3E.tree_fort("mining") - V3E.TREE_FORT_MAX) < 1e-9 and V3E.tree_fort("foraging") <= V3E.TREE_FORT_MAX
            and V3E.tree_fort("farming") <= V3E.TREE_FORT_MAX,
            "DATA trees_v3_effects.check(): tree Fortune at max Mining %.1f / Foraging %.1f / Farming %.1f (budget %.0f)" % (
                100 * V3E.tree_fort("mining"), 100 * V3E.tree_fort("foraging"), 100 * V3E.tree_fort("farming"), 100 * V3E.TREE_FORT_MAX))
    # EXECUTED: the jar's own value = TreeCfg.PER x ranks (Rich Seams 3 ranks = MFortune level 3) after TreeCfg.load of a fresh file
    base = os.path.join(scratch, "data")
    os.makedirs(os.path.join(base, "players"), exist_ok=True)
    Paths = JClass("java.nio.file.Paths")
    JClass(PKG + "TreeStore").DIR = Paths.get(os.path.join(base, "players"))
    C.FILE = Paths.get(os.path.join(base, "trees.properties"))
    C.load()
    i = pd[0] if pd else 0
    K.check(abs(float(C.PER[i]) * 3 * 100.0 - 7.5) < 1e-9, "DATA Rich Seams at 3 ranks = %.2f Mining Fortune (TreeCfg.load of a fresh file)" % (float(C.PER[i]) * 300.0))
    K.save()


def run_mig(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    Paths = JClass("java.nio.file.Paths")
    C, Mg, M323 = JClass(PKG + "TreeCfg"), JClass(PKG + "TreeMigP5"), JClass(PKG + "TreeMig323")
    MK = str(Mg.MARK_LINE)
    K.eq(([str(x) for x in Mg.KEY], [str(x) for x in Mg.OLDV], [str(x) for x in Mg.NEWV], str(Mg.WHO)),
         (["Mining.MFortune.per"], ["0.1"], ["0.025"], "SkyyTrees 0.4.5"), "MIG key / old / new / who")

    def upd(t):
        r = Mg.mP5Update(t)
        return None if r is None else (str(r[0]), [str(x) for x in r[1]], [str(x) for x in r[2]])
    cases = []
    for nl in ("\n", "\r\n"):
        src = ("a=1\nMining.MFortune.max=10\nMining.MFortune.per=0.1\nb=2\n").replace("\n", nl)
        exp = ("a=1\nMining.MFortune.max=10\nMining.MFortune.per=0.025\nb=2\n" + MK + "\n").replace("\n", nl)
        cases.append(("old default %r" % nl, upd(src), (exp, ["nodes.Mining[MFortune.per]", "0.1", "0.025"], [])))
    cases.append(("0.10 counts", upd("Mining.MFortune.per=0.10\n"), ("Mining.MFortune.per=0.025\n" + MK + "\n", ["nodes.Mining[MFortune.per]", "0.10", "0.025"], [])))
    g = upd("Mining.MFortune.per=0.2\n")
    cases.append(("hand-edited kept", (g[0], g[1], len(g[2])), ("Mining.MFortune.per=0.2\n" + MK + "\n", [], 1)))
    g = upd("Mining.MFortune.per=0.1\nMining.MFortune.per=0.1\n")
    cases.append(("doubled kept", (g[0], g[1], len(g[2])), ("Mining.MFortune.per=0.1\nMining.MFortune.per=0.1\n" + MK + "\n", [], 1)))
    g = upd("Mining.MFortune.per=0.\\\n1\n")
    cases.append(("continued kept", (g[0], g[1], len(g[2])), ("Mining.MFortune.per=0.\\\n1\n" + MK + "\n", [], 1)))
    cases.append(("no line", upd("a=1\n"), ("a=1\n" + MK + "\n", [], [])))
    cases.append(("already new", upd("Mining.MFortune.per=0.025\n"), ("Mining.MFortune.per=0.025\n" + MK + "\n", [], [])))
    cases.append(("no final break", upd("a=1"), ("a=1\n" + MK + "\n", [], [])))
    cases.append(("marked", upd("x=1\n" + MK + "\nMining.MFortune.per=0.1\n"), None))
    bad = [(nm, gg, e) for nm, gg, e in cases if gg != e]
    for b in bad[:4]:
        print("   MIG", b[0], "got", repr(b[1])[:300], "want", repr(b[2])[:300])
    K.check(not bad, "MIG mP5Update, %d cases: wrong %s" % (len(cases), [b[0] for b in bad]))

    def start(d):
        bp = Paths.get(d)
        JClass(PKG + "TreeStore").DIR = Paths.get(os.path.join(d, "players"))
        C.FILE = Paths.get(os.path.join(d, "trees.properties"))
        C.load()
        a = str(M323.run(bp))
        b = str(JClass(PKG + "TreeMig324").run(bp))
        return a, b, str(Mg.run(bp))
    d = os.path.join(scratch, "mig-file")
    os.makedirs(os.path.join(d, "players"), exist_ok=True)
    fp = os.path.join(d, "trees.properties")
    C.FILE = Paths.get(fp)
    C.load()          # a fresh 0.4.5 default file (carries every marker: nothing to do)
    fresh = open(fp, "rb").read()
    K.check(start(d)[2] == "" and open(fp, "rb").read() == fresh, "MIG a fresh file is left alone (it carries the marker)")
    # a 0.4.4-shaped file: the fresh text with the 0.4.4 value and without the P5 marker
    old44 = fresh.replace(b"\nMining.MFortune.per=0.025\n", b"\nMining.MFortune.per=0.1\n")
    old44 = b"\n".join(l for l in old44.split(b"\n") if b"Balance P5 power (SkyyTrees 0.4.5)" not in l)
    open(fp, "wb").write(old44)
    for x in ("config-history", "config-changes.log"):
        shutil.rmtree(os.path.join(d, x), ignore_errors=True) if x == "config-history" else (os.path.exists(os.path.join(d, x)) and os.remove(os.path.join(d, x)))
    _a, _b, m1 = start(d)
    n1 = open(fp, "rb").read()
    po, pn = _props(old44), _props(n1)
    K.eq(sorted(k for k in set(po) | set(pn) if po.get(k) != pn.get(k)), ["Mining.MFortune.per"], "MIG file: only Mining.MFortune.per changed (Properties)")
    K.check(pn["Mining.MFortune.per"] == "0.025" and abs(float(C.PER[[i for i in range(len(C.PER)) if abs(float(C.PER[i]) - 0.025) < 1e-12][0]]) - 0.025) < 1e-12,
            "MIG file: the line + TreeCfg.load say 0.025: %s" % m1[:160])
    hist = [open(os.path.join(r_, f_), "rb").read() for r_, _d, fs in os.walk(os.path.join(d, "config-history")) for f_ in fs]
    K.check(old44 in hist, "MIG file: config-history holds the 0.4.4 bytes")
    lg = open(os.path.join(d, "config-changes.log"), encoding="latin-1").read()
    K.eq(lg.count("\tSkyyTrees 0.4.5\t-\tupdate\tnodes.Mining[MFortune.per]\t0.1\t0.025\tok"), 1, "MIG file: one Undo-able change-log line")
    K.check(start(d)[2] == "" and open(fp, "rb").read() == n1, "MIG file: the second start changes nothing")
    # an old 0.3.22 file: 0.01 -> 0.1 (TreeMig323) -> 0.025 (TreeMigP5) in ONE start
    d2 = os.path.join(scratch, "mig-0322")
    os.makedirs(os.path.join(d2, "players"), exist_ok=True)
    o22 = old44.replace(b"\nMining.MFortune.per=0.1\n", b"\nMining.MFortune.per=0.01\n").replace(b"\nMining.MFortune.max=10\n", b"\nMining.MFortune.max=20\n")
    o22 = b"\n".join(l for l in o22.split(b"\n") if b"skyytrees-0.3.23-fortune" not in l)
    open(os.path.join(d2, "trees.properties"), "wb").write(o22)
    r = start(d2)
    p22 = _props(open(os.path.join(d2, "trees.properties"), "rb").read())
    K.check((p22["Mining.MFortune.per"], p22["Mining.MFortune.max"]) == ("0.025", "10") and "0.01 -> 0.1" in r[0] and "0.1 -> 0.025" in r[2],
            "MIG a 0.3.22 file: 0.01 -> 0.1 -> 0.025 in one start (max 20 -> 10): %s" % (p22.get("Mining.MFortune.per"),))
    K.save()


def live_start(home):
    from jpype import JClass
    J = lambda n: JClass(PKG + n)
    Paths = JClass("java.nio.file.Paths")
    J("TreeStore").DIR = Paths.get(os.path.join(home, "players"))
    J("TreeCfg").FILE = Paths.get(os.path.join(home, "trees.properties"))
    J("TreeStore").DATA.clear()
    J("TreeCfg").load()
    bp = Paths.get(home)
    out = []
    for m in ("TreeMig", "TreeMig32", "TreeMig33", "TreeMig317", "TreeMig321", "TreeMig323", "TreeMig324", "TreeMigP5"):
        out.append(str(J(m).run(bp)))
    for f in sorted(os.listdir(os.path.join(home, "players"))):
        if f.endswith(".properties"):
            J("TreeStore").readFile(f[:-11])
    return out


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    fp = os.path.join(home, "trees.properties")
    t0 = open(fp, "rb").read()
    lp = os.path.join(home, "config-changes.log")
    l0 = open(lp, "rb").read() if os.path.isfile(lp) else b""
    msgs = live_start(home)
    t1 = open(fp, "rb").read()
    print("   live TreeMigP5:", msgs[-1][:220])
    po, pn = _props(t0), _props(t1)
    K.eq(sorted(k for k in set(po) | set(pn) if po.get(k) != pn.get(k)), ["Mining.MFortune.per"], "LIVE start 1: trees.properties changes only Mining.MFortune.per")
    K.eq((po.get("Mining.MFortune.per"), pn.get("Mining.MFortune.per")), ("0.1", "0.025"), "LIVE Rich Seams 0.1 -> 0.025")
    lo = [x for x in t0.split(b"\n") if not x.startswith(b"Mining.MFortune.per=")]
    ln = [x for x in t1.split(b"\n") if not x.startswith(b"Mining.MFortune.per=") and b"Balance P5 power (SkyyTrees 0.4.5)" not in x]
    K.check(lo == ln, "LIVE every other line byte-identical, in order; the marker the only new line")
    hist = [open(os.path.join(r_, f_), "rb").read() for r_, _d, fs in os.walk(os.path.join(home, "config-history")) for f_ in fs]
    K.check(t0 in hist, "LIVE the config-history copy holds the old bytes")
    lg = open(lp, "rb").read()[len(l0):].decode("utf-8")
    K.eq(lg.count("\tSkyyTrees 0.4.5\t-\tupdate\tnodes.Mining[MFortune.per]\t0.1\t0.025\tok"), 1, "LIVE one change-log line")
    h1 = tree_hash(home)
    msgs2 = live_start(home)
    K.check(tree_hash(home) == h1 and msgs2[-1] == "", "LIVE start 2 changes nothing")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyTrees", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("old", run_old), ("data", run_data), ("mig", run_mig), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyTrees"))
