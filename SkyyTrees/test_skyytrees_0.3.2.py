"""Bare-JVM harness for SkyyTrees 0.3.2 (tools/trees_0_3_2_patch.py) - class trees ON by default (Skyy LOCKED 2026-10-05) + the
one-time class.enabled update (TreeMig32). Extends SkyyTrees/test_skyytrees_0.3.1.py (its child-JVM helpers, the stand-in classes and the
bytecode compare are imported from it; its full page-state run stays the 0.3.1 record - 0.3.2 changes no page, rule or saved key).

    python SkyyTrees/test_skyytrees_0.3.2.py [--jar <SkyyTrees-0.3.2.jar>] [--prev <SkyyTrees-0.3.1.jar>] [--live <Skyy_SkyyTrees folder>]
                                             [--dir <scratch inside tools/dev/scratch/>] [--keep]

  A  every class of 0.3.2 and 0.3.1 loads, verifies and initialises (-Xverify:all, the game's own JRE)
  E  class bytes 0.3.1 -> 0.3.2: exactly TreeMig32 added; only TreeCfg / TreeMig / CfgRows / CfgFn / the plugin / the manifest differ
  L  defaults: a fresh start writes the 0.3.2 default file (class.enabled=true + the marker once), class trees ON, TreeMig32 does
     nothing, a second start writes nothing; the Server Setup row's default is true; a missing / unreadable line reads ON; 0.3.1 = OFF
  M  TreeMig32 on scratch COPIES of the live Skyy_SkyyTrees folder in the plugin's start order (TreeCfg.load -> TreeMig.run ->
     TreeMig32.run -> CfgPub.start), each start in a fresh loader: the live file (false -> true: one value, History = the old bytes,
     one Undo line, CLASS_ON follows; start 2 writes nothing; Undo through the kit -> false and start 3 keeps it), a value set by hand
     (config-changes.log / a rotated .2 log) kept, true already, CRLF, no final newline, spacing, off / FALSE, doubled / continued lines,
     an unreadable value, a missing line, History blocked, an unreadable change log, a pre-0.3 file, the marker removed, an empty file,
     and 0.3.1 reading the updated file (rollback); the LIVE files are compared before / after (never written)
  S  EXISTING SAVES with class trees ON: every live player file (copied) read by 0.3.2: no class picks, nothing intact, 0 AP spent, no
     negative balance, respec answers "Nothing to respec" (free, no coin call), ROOT unlocks for its 1 AP, every rune / element slot
     refuses, a hand-owned rune slot is never intact or spent, the stats / tree:fn:bonus stay 0 for the class keys; save + re-read by
     0.3.1 and 0.3.2 keep the picks; a file saved without changes keeps its Properties
"""
import os, sys, re, shutil, subprocess, json, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.3.2", "0.3.1"
PKG = "com.skyy.trees."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "skyytrees-032")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyTrees-%s.jar" % PREV_VERSION)))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE_DIR = os.path.abspath(arg("--live", os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyTrees")))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]
MK = "skyytrees-0.3.2-classon"
MARK_LINE = "# ---------- SkyyTrees 0.3.2 (added once - marker %s): class trees are ON by default (Skyy 2026-10-05) ----------" % MK

# the 0.3.1 harness = the helpers (child JVM start, stand-ins, the javassist stand-in classes, the bytecode compare)
_spec = importlib.util.spec_from_file_location("t031", os.path.join(HERE, "test_skyytrees_0.3.1.py"))
H = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(H)
H.SCRATCH = SCRATCH


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


# ============================================================================================================== child: load
def run_load(jar, out):
    from jpype import JClass
    H._jvm_start([jar])
    Cls = JClass("java.lang.Class")
    ld = JClass("java.lang.ClassLoader").getSystemClassLoader()
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(jar).namelist() if n.endswith(".class")]
    fails = []
    for n in names:
        try:
            Cls.forName(n, True, ld)
        except Exception as e:
            fails.append("%s: %s" % (n, e))
    json.dump({"classes": len(names), "fails": fails}, open(out, "w"))
    os._exit(0)


# ============================================================================================================== child: logic
def run_logic(jar, prev, fake, live, out):
    from jpype import JClass, JArray, JObject, JImplements, JOverride
    H._jvm_start([], [fake])
    R = {"oks": 0, "fails": [], "info": {}}

    def ck(cond, what):
        if cond:
            R["oks"] += 1
        else:
            R["fails"].append(what)
            print("FAIL", what)

    URL, URLCL, File = JClass("java.net.URL"), JClass("java.net.URLClassLoader"), JClass("java.io.File")
    sysl = JClass("java.lang.ClassLoader").getSystemClassLoader()
    Paths, Boolean, Integer = JClass("java.nio.file.Paths"), JClass("java.lang.Boolean"), JClass("java.lang.Integer")
    U, setf, ByTree, me, pr = H._stand_ins()

    def loader(j):
        urls = JArray(URL)(1)
        urls[0] = File(j).toURI().toURL()
        return URLCL(urls, sysl)

    def K(ld):
        return lambda n: JClass(PKG + n, loader=ld)

    def path(p):
        return Paths.get(p)

    def snap(d):
        o = {}
        for r, _ds, fs in os.walk(d):
            for f in fs:
                p = os.path.join(r, f)
                o[os.path.relpath(p, d).replace(os.sep, "/")] = open(p, "rb").read()
        return o

    def jarr(xs):
        return JArray(JObject)(xs)

    C0 = K(loader(jar))
    bridge = C0("TreeStore").bridge()

    def start(base, j=None, kit=True):
        C = K(loader(j or jar))
        b = path(base)
        C("TreeCfg").FILE = b.resolve("trees.properties")
        C("TreeStore").DIR = b.resolve("players")
        s = str(C("TreeCfg").load())
        m = str(C("TreeMig").run(b))
        m32 = str(C("TreeMig32").run(b)) if (j or jar) == jar else ""
        if kit:
            C("CfgPub").start(b.getParent(), None)
        return {"C": C, "sum": s, "mig": m, "m32": m32, "on": bool(C("TreeCfg").CLASS_ON)}

    COUNT = [0]

    def case(name, body, extra=None):
        COUNT[0] += 1
        base = os.path.join(SCRATCH, "m", "%02d-%s" % (COUNT[0], re.sub(r"[^a-z0-9]+", "-", name.lower())), "mods", "Skyy_SkyyTrees")
        shutil.copytree(live, base)
        if body is None:
            os.remove(os.path.join(base, "trees.properties"))
        else:
            open(os.path.join(base, "trees.properties"), "wb").write(body)
        for k, v in (extra or {}).items():
            open(os.path.join(base, k), "ab").write(v)
        return base

    def changed(a, b):
        return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))

    LIVE_TP = os.path.join(live, "trees.properties")
    live_before = open(LIVE_TP, "rb").read()
    live_snap = snap(live)
    ML = (MARK_LINE + "\n").encode("latin-1")

    # ------------------------------------------------------------------ L. defaults
    fresh = os.path.join(SCRATCH, "l", "fresh", "mods", "Skyy_SkyyTrees")
    os.makedirs(fresh)
    r1 = start(fresh)
    f1 = open(os.path.join(fresh, "trees.properties"), "rb").read()
    G = r1["C"]("TreeCfg")
    ck(f1 == str(G.DEFAULTS).encode("utf8") and r1["mig"] == "" and r1["m32"] == "", "L: a fresh start writes the default file, both updates do nothing")
    ck(f1.count(b"\nclass.enabled=true\n") == 1 and b"class.enabled=false" not in f1 and f1.count(MK.encode()) == 1, "L: the default file says class.enabled=true, the marker once")
    ck(r1["on"], "L: class trees ON on a fresh start")
    s1 = snap(fresh)
    r2 = start(fresh)
    ck(snap(fresh) == s1 and r2["m32"] == "" and r2["on"], "L: a second start writes nothing")
    hdr = bridge.get("config:def:SkyyTrees")
    rows = dict((str(r[0]), [str(x) for x in r]) for r in hdr[7])
    ck(len(rows) == 41 and rows["class.enabled"][4] == "true" and "ON by default since 0.3.2" in rows["class.enabled"][10],
       "L: 41 Server Setup rows; class.enabled default true + help: %s" % rows.get("class.enabled"))
    Props = JClass("java.util.Properties")
    for txt, want in (("", True), ("class.enabled=false\n", False), ("class.enabled=true\n", True), ("class.enabled=maybe\n", True), ("class.enabled= FALSE \n", False)):
        p = Props()
        p.load(JClass("java.io.StringReader")(txt))
        Cq = K(loader(jar))
        Cq("TreeCfg").apply(p)
        ck(bool(Cq("TreeCfg").CLASS_ON) == want, "L: TreeCfg reads %r as %s" % (txt, want))
    Cp = K(loader(prev))
    ck(not bool(Cp("TreeCfg").CLASS_ON) and "class.enabled=false" in str(Cp("TreeCfg").DEFAULTS), "L: 0.3.1 (the old seat) still ships OFF")
    ck(str(C0("TreeMig32").MARK_LINE) == MARK_LINE, "L: the marker line")

    # ------------------------------------------------------------------ M. TreeMig32 on copies
    ck(b"\nclass.enabled=false\n" in live_before and MK.encode() not in live_before and b"skyytrees-0.3-trees" in live_before,
       "M: the live file is a 0.3 file with class.enabled=false and no 0.3.2 marker (the case the update is for)")
    LOGRE = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\tSkyyTrees 0\.3\.2\t-\tupdate\tclass\.enabled\tfalse\ttrue\tok$")
    flip = lambda b: b.replace(b"\nclass.enabled=false\n", b"\nclass.enabled=true\n", 1)
    lc = case("live", live_before)
    s0 = snap(lc)
    a = start(lc)
    sa = snap(lc)
    ch = changed(s0, sa)
    bak = [k for k in ch if k.startswith("config-history/") and k.endswith(".bak")]
    ck(ch == sorted(["trees.properties", "config-changes.log", "config-history/index.log"] + bak) and len(bak) == 1,
       "M live: start 1 writes only trees.properties, one History copy + index.log, config-changes.log: %s" % ch)
    ck(len(bak) == 1 and sa[bak[0]] == live_before, "M live: the History copy = the old bytes")
    idx = sa["config-history/index.log"].decode("utf8").strip().split("\n")
    ck(idx[-1].endswith("\tSkyyTrees 0.3.2\tbefore the 0.3.2 class trees ON update") and len(idx) == len(s0.get("config-history/index.log", b"").decode("utf8").strip().split("\n")) + 1,
       "M live: one new index.log line: %s" % idx[-1:])
    ck(sa["trees.properties"] == flip(live_before) + ML, "M live: the new file = the old bytes with ONE value false -> true + the marker line")
    nl = sa["config-changes.log"][len(s0.get("config-changes.log", b"")):].decode("utf8").strip().split("\n")
    ck(len(nl) == 1 and LOGRE.match(nl[0]) is not None and sa["config-changes.log"].startswith(s0.get("config-changes.log", b"")),
       "M live: one change-log line class.enabled false -> true in the kit's format: %s" % nl)
    ck(a["on"] and a["m32"].startswith("trees.properties updated for SkyyTrees 0.3.2: class.enabled false -> true") and a["mig"] == "",
       "M live: CLASS_ON follows the flip at this start, the INFO line: %r" % a["m32"][:140])
    b = start(lc)
    sb = snap(lc)
    ck(changed(sa, sb) == [] and b["m32"] == "" and b["on"], "M live: start 2 writes nothing, class trees ON")
    Cb = b["C"]
    lg = [str(x) for x in Cb("CfgFn")().apply(jarr(["log", Integer.valueOf(20)]))]
    mine = [x for x in lg if "\tSkyyTrees 0.3.2\t" in x]
    ck(len(mine) == 1 and mine[0].split("\t")[4:8] == ["class.enabled", "false", "true", "ok"], "M live: the kit's log lists the update for Undo: %s" % mine)
    un = [str(x) if x is not None else None for x in Cb("CfgFn")().apply(jarr(["set", "class.enabled", "false", None, "console", "yes", "console"]))]
    Cb("CfgPub").flush()
    sc = snap(lc)
    ck(un[0] == "ok" and sc["trees.properties"].count(b"\nclass.enabled=false\n") == 1 and b"\nclass.enabled=true\n" not in sc["trees.properties"]
       and not bool(Cb("TreeCfg").CLASS_ON), "M live: Undo (set back to false) writes false and class trees are OFF: %s" % un)
    c = start(lc)
    ck(c["m32"] == "" and not c["on"] and snap(lc)["trees.properties"] == sc["trees.properties"], "M live: start 3 keeps the undone value (marker)")
    ck(open(LIVE_TP, "rb").read() == live_before and snap(live) == live_snap, "M: the LIVE folder was never written")

    def two(name, body, extra=None, kit=True):
        base = case(name, body, extra)
        x0 = snap(base)
        x = start(base, kit=kit)
        xa = snap(base)
        y = start(base, kit=kit)
        xb = snap(base)
        return base, x0, x, xa, y, xb

    hand = b"2026-10-04T10:00:00\tSkyy\t00000000-0000-7ee5-0000-000000000019\tmenu\tclass.enabled\ttrue\tfalse\tok\n"
    base, x0, x, xa, y, xb = two("hand-set false", live_before, {"config-changes.log": hand})
    ck(xa["trees.properties"] == live_before + ML and xa["config-changes.log"] == x0["config-changes.log"] and not x["on"]
       and "kept - it was set by hand" in x["m32"] and changed(xa, xb) == [] and y["m32"] == "",
       "M hand-set: false kept (marker only, no change-log line, OFF), start 2 nothing: %r" % x["m32"])
    base, x0, x, xa, y, xb = two("hand-set rotated log", live_before, {"config-changes.log.2": hand})
    ck(xa["trees.properties"] == live_before + ML and not x["on"], "M hand-set in config-changes.log.2: kept")
    own = b"2026-10-04T10:00:00\tSkyyTrees 0.3.2\t-\tupdate\tclass.enabled\tfalse\ttrue\tok\n"
    base, x0, x, xa, y, xb = two("own log line only", live_before, {"config-changes.log": own})
    ck(xa["trees.properties"] == flip(live_before) + ML and x["on"], "M a log line written by this update itself is no hand edit: flipped")
    tru = flip(live_before)
    base, x0, x, xa, y, xb = two("true already", tru)
    ck(xa["trees.properties"] == tru + ML and xa.get("config-changes.log") == x0.get("config-changes.log") and x["on"] and "true already" in x["m32"]
       and changed(xa, xb) == [], "M true already (Skyy switched it on live): marker only, no change-log line, ON")
    crlf = live_before.replace(b"\n", b"\r\n")
    base, x0, x, xa, y, xb = two("crlf", crlf)
    t = xa["trees.properties"]
    ck(t == crlf.replace(b"\r\nclass.enabled=false\r\n", b"\r\nclass.enabled=true\r\n", 1) + ML.replace(b"\n", b"\r\n") and t.count(b"\n") == t.count(b"\r\n")
       and x["on"] and changed(xa, xb) == [], "M CRLF: the value flipped, every line ending CRLF, the rest byte for byte")
    nonl = live_before.rstrip(b"\n")
    base, x0, x, xa, y, xb = two("no final newline", nonl)
    ck(xa["trees.properties"] == flip(nonl) + b"\n" + ML and x["on"], "M no final newline: one added, then the marker")
    sp = live_before.replace(b"\nclass.enabled=false\n", b"\n  class.enabled = false  \n")
    base, x0, x, xa, y, xb = two("spacing", sp)
    ck(xa["trees.properties"] == sp.replace(b"\n  class.enabled = false  \n", b"\n  class.enabled = true  \n") + ML and x["on"], "M spacing kept around the new value: %r %r" % (x["m32"], [l for l in xa["trees.properties"].split(bytes([10])) if b"class.enabled" in l]))
    for word in (b"off", b"FALSE"):
        o = live_before.replace(b"\nclass.enabled=false\n", b"\nclass.enabled=" + word + b"\n")
        base, x0, x, xa, y, xb = two("value " + word.decode(), o)
        nl2 = xa["config-changes.log"][len(x0.get("config-changes.log", b"")):].decode("utf8").strip().split("\n")
        ck(xa["trees.properties"] == o.replace(b"\nclass.enabled=" + word + b"\n", b"\nclass.enabled=true\n") + ML and x["on"] and LOGRE.match(nl2[0]) is not None,
           "M class.enabled=%s (the old default as read): flipped, the Undo line says false -> true" % word.decode())
    dup = live_before + b"class.enabled=false\n"
    base, x0, x, xa, y, xb = two("doubled line", dup)
    ck(xa["trees.properties"] == dup + ML and not x["on"] and "doubled" in x["m32"], "M a doubled line: kept (marker only), OFF")
    cont = live_before.replace(b"\nclass.enabled=false\n", b"\nclass.enabled=fal\\\n    se\n")
    base, x0, x, xa, y, xb = two("continued line", cont)
    ck(xa["trees.properties"] == cont + ML and not x["on"], "M a continued line: kept (marker only), OFF")
    odd = live_before.replace(b"\nclass.enabled=false\n", b"\nclass.enabled=maybe\n")
    base, x0, x, xa, y, xb = two("unreadable value", odd)
    ck(xa["trees.properties"] == odd + ML and x["on"] and "not true or false" in x["m32"], "M an unreadable value: kept, read as the 0.3.2 default ON")
    miss = live_before.replace(b"\nclass.enabled=false\n", b"\n")
    base, x0, x, xa, y, xb = two("missing line", miss)
    ck(xa["trees.properties"] == miss + ML and x["on"] and "no class.enabled line" in x["m32"], "M a missing line: marker only, ON (the code default)")
    base = case("history blocked", live_before)
    shutil.rmtree(os.path.join(base, "config-history"))
    open(os.path.join(base, "config-history"), "wb").write(b"not a folder")
    x = start(base, kit=False)
    ck(x["m32"] == "" and open(os.path.join(base, "trees.properties"), "rb").read() == live_before and not x["on"],
       "M History blocked: nothing written, class trees as the file says (OFF)")
    os.remove(os.path.join(base, "config-history"))
    y = start(base)
    ck(y["on"] and MK.encode() in open(os.path.join(base, "trees.properties"), "rb").read(), "M History blocked: the next start updates")
    base = case("change log unreadable", live_before)
    os.remove(os.path.join(base, "config-changes.log"))
    os.makedirs(os.path.join(base, "config-changes.log"))
    x = start(base, kit=False)
    ck(x["m32"] == "" and open(os.path.join(base, "trees.properties"), "rb").read() == live_before and not x["on"],
       "M an unreadable config-changes.log: nothing written (cannot tell a hand edit), OFF")
    shutil.rmtree(os.path.join(base, "config-changes.log"))
    y = start(base)
    ck(y["on"] and open(os.path.join(base, "trees.properties"), "rb").read() == flip(live_before) + ML, "M change log readable again: the next start flips")
    pre03 = live_before[:live_before.index(b"# ---------- SkyyTrees 0.3 (added once")].rstrip(b"\n") + b"\n"
    base, x0, x, xa, y, xb = two("pre-0.3 file", pre03)
    t = xa["trees.properties"]
    ck(t.startswith(pre03) and t.count(b"\nclass.enabled=true\n") == 1 and b"class.enabled=false" not in t and t.count(MK.encode()) == 1
       and x["mig"].startswith("trees.properties updated for SkyyTrees 0.3:") and x["m32"] == "" and x["on"] and changed(xa, xb) == [],
       "M a pre-0.3 file: the 0.3 block brings class.enabled=true + the 0.3.2 marker, TreeMig32 does nothing, ON")
    nomk = flip(live_before)
    base, x0, x, xa, y, xb = two("marker removed after the flip", nomk)
    ck(xa["trees.properties"] == nomk + ML and x["on"], "M the marker removed by hand: only the marker comes back")
    base, x0, x, xa, y, xb = two("empty file", b"")
    ck(MK.encode() in xa["trees.properties"] and b"\nclass.enabled=true\n" in xa["trees.properties"] and x["on"] and changed(xa, xb) == [],
       "M an empty file: the 0.3 block (true + marker), ON")
    # rollback: 0.3.1 on the updated file reads class trees ON and writes nothing
    base = case("rollback to 0.3.1", flip(live_before) + ML)
    z0 = snap(base)
    z = start(base, j=prev)
    ck(z["on"] and z["mig"] == "" and changed(z0, snap(base)) == [], "M rollback: 0.3.1 reads the updated file as ON and writes nothing")

    # ------------------------------------------------------------------ S. existing saves with class trees ON
    pdir = os.path.join(SCRATCH, "s", "players")
    shutil.copytree(os.path.join(live, "players"), pdir)
    keys = sorted(f[:-11] for f in os.listdir(pdir) if f.endswith(".properties"))
    ck(len(keys) >= 1, "S: live player files copied: %d" % len(keys))
    sdir = os.path.join(SCRATCH, "s", "cfg", "mods", "Skyy_SkyyTrees")
    os.makedirs(sdir)
    rs = start(sdir)
    CS = rs["C"]
    Sto, Cls, Cops, Cfg, Fx = CS("TreeStore"), CS("TreeClass"), CS("TreeClassOps"), CS("TreeCfg"), CS("TreeFx")
    Sto.DIR = path(pdir)
    ck(bool(Cfg.CLASS_ON), "S: class trees ON")
    NN, NC = int(Cls.NN), len(list(Cls.CLASSES))
    NID = [str(x) for x in Cls.NID]
    slots = [n for n in range(NN) if bool(Cls.slotComing(n))]
    ck(len(slots) == 18 and NN == 37, "S: 37 nodes, 18 rune / element / capstone slots (A1-A4, M1A-M4B, LE CE RE, LS CS RS): %d" % len(slots))
    CALLS = []

    @JImplements("java.util.function.Function")
    class Coins(object):
        @JOverride
        def apply(self, o):
            CALLS.append(int(o[1].longValue()))
            return Boolean.TRUE
    bridge.put("coins:fn:take", Coins())
    JProps = JClass("java.util.Properties")

    def props(f):
        p = JProps()
        ins = JClass("java.io.FileInputStream")(f)
        try:
            p.load(ins)
        finally:
            ins.close()
        return dict((str(k), str(p.getProperty(k))) for k in p.stringPropertyNames())

    CP = K(loader(prev))
    SP = CP("TreeStore")
    SP.DIR = path(pdir)
    for k in keys:
        fp = os.path.join(pdir, k + ".properties")
        before = props(fp)
        d = Sto.readFile(k)
        ck(not bool(d.bad) and not any(bool(x) for x in d.cown) and all(int(x) == 0 for x in d.crespecAt),
           "S %s: an existing save has no class picks and no class respec time" % k)
        for ci in range(NC):
            it = Cls.intact(d, ci)
            ck(not any(bool(x) for x in it) and int(Cls.spent(it, ci)) == 0 and not any(bool(Cops.negBalance(d, ci, l)) for l in (0, 1, 23, 100))
               and all(int(Cops.priceOf(d, ci, l, False)) == 0 for l in (1, 23, 100)), "S %s class %d: nothing intact, 0 AP spent, no negative balance, respec price 0" % (k, ci))
            r_ = str(Cops.respec(me, d, ci, 23, False))
            ck(r_.startswith("Nothing to respec in your ") and CALLS == [], "S %s class %d: respec = nothing to respec, no coin call: %r" % (k, ci, r_))
        Sto.DATA.clear()
        Sto.install(k, me, d)
        ck(bool(Sto.saveNow(k)) and props(fp) == before, "S %s: saved by 0.3.2 without a change = the same Properties" % k)
        und = JClass("java.util.ArrayList")()
        b_root = str(Cops.buy(me, d, 0, 23, 0, und, False))
        ck(b_root == "Unlocked Root! 1 AP spent - 11 left" and bool(d.cown[0]), "S %s: an Archer at 23 unlocks Root for 1 AP: %r" % (k, b_root))
        refused = [NID[n] for n in slots if str(Cops.buy(me, d, 0, 100, n, None, False)).startswith("Unlocked")]
        ck(refused == [] and not any(bool(d.cown[n]) for n in slots), "S %s: every rune / element / capstone slot refuses (level 100): %s" % (k, refused))
        sp0 = int(Cls.spent(Cls.intact(d, 0), 0))
        Sto.setClassOwn(d, 0, slots[0], True)
        it2 = Cls.intact(d, 0)
        ck(not bool(it2[slots[0]]) and int(Cls.spent(it2, 0)) == sp0, "S %s: a hand-owned rune slot is never intact or spent" % k)
        Sto.setClassOwn(d, 0, slots[0], False)
        Sto.saveNow(k)
        pp = props(fp)
        ck(pp.get("Class.Archer") == "ROOT" and pp.get("v") == before.get("v"), "S %s: the pick is saved (Class.Archer=ROOT), same file version" % k)
        dp = SP.readFile(k)
        ck(bool(dp.cown[0]) and not any(bool(dp.cown[n]) for n in range(1, len(dp.cown))), "S %s: 0.3.1 reads the pick back (rollback keeps it)" % k)
        und.clear()
        r2_ = str(Cops.respec(me, d, 0, 23, False))
        ck(r2_.startswith("Respec done") and CALLS == [2300] and not bool(d.cown[0]), "S %s: respec after the pick costs level x 100 once: %r %s" % (k, r2_, CALLS))
        del CALLS[:]
        Sto.saveNow(k)
        ck("Class.Archer" not in props(fp) or props(fp).get("Class.Archer") == "", "S %s: after the respec no pick is saved" % k)
    bridge.remove("coins:fn:take")
    json.dump(R, open(out, "w"), indent=1)
    os._exit(0)


# ============================================================================================================== parent
EXPECT_CHANGED = {"TreeCfg", "TreeMig", "CfgRows", "CfgFn", "SkyyTreesPlugin"}


def main():
    if "--load" in sys.argv:
        run_load(arg("--load"), arg("--out"))
        return
    if "--bytecode" in sys.argv:
        H.run_bytecode(arg("--bytecode"), arg("--new"), arg("--out"))
        return
    if "--mkfake" in sys.argv:
        H.run_mkfake(arg("--mkfake"))
        return
    if "--logic" in sys.argv:
        run_logic(arg("--logic"), arg("--prev"), arg("--fake"), arg("--live"), arg("--out"))
        return
    for j in (JAR, PREV_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first (without --deploy)" % j)
    root = os.path.join(TOOLS, "dev", "scratch").replace("\\", "/").lower().rstrip("/")
    here = SCRATCH.replace("\\", "/").lower().rstrip("/")
    if here == root or not here.startswith(root + "/"):
        sys.exit("--dir must be a folder INSIDE tools/dev/scratch/, not %s" % SCRATCH)
    if os.path.exists(SCRATCH) and os.listdir(SCRATCH):
        sys.exit("%s is not empty - pass an empty --dir" % SCRATCH)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    me = os.path.abspath(__file__)
    live_before = open(os.path.join(LIVE_DIR, "trees.properties"), "rb").read()
    try:
        for tag, j in (("new", JAR), ("prev", PREV_JAR)):
            o = os.path.join(SCRATCH, "load-%s.json" % tag)
            p = subprocess.run([sys.executable, me, "--load", j, "--out", o, "--dir", SCRATCH], env=env)
            r = json.load(open(o)) if p.returncode == 0 and os.path.isfile(o) else {"classes": 0, "fails": ["child failed"]}
            check(not r["fails"] and r["classes"] > 0, "A: %s: %d classes load, verify and initialise %s" % (os.path.basename(j), r["classes"], r["fails"][:3]))
            print("A: %s: %d classes" % (os.path.basename(j), r["classes"]))
        bc = os.path.join(SCRATCH, "bytecode.json")
        p = subprocess.run([sys.executable, me, "--bytecode", PREV_JAR, "--new", JAR, "--out", bc, "--dir", SCRATCH], env=env)
        check(p.returncode == 0 and os.path.isfile(bc), "E: bytecode child ran")
        zp, zn = zipfile.ZipFile(PREV_JAR), zipfile.ZipFile(JAR)
        added = sorted(set(zn.namelist()) - set(zp.namelist()))
        gone = sorted(set(zp.namelist()) - set(zn.namelist()))
        check(added == ["com/skyy/trees/TreeMig32.class"] and gone == [], "E: added exactly TreeMig32, nothing removed: %s %s" % (added, gone))
        diff = sorted(n for n in set(zp.namelist()) & set(zn.namelist()) if zp.read(n) != zn.read(n))
        dcls = set(n.split("/")[-1][:-6] for n in diff if n.endswith(".class"))
        dother = [n for n in diff if not n.endswith(".class")]
        check(dcls == EXPECT_CHANGED and dother == ["manifest.json"], "E: changed exactly %s + manifest.json: %s %s" % (sorted(EXPECT_CHANGED), sorted(dcls), dother))
        if os.path.isfile(bc):
            res = json.load(open(bc))
            for n, v in sorted(res.items()):
                c = n.split("/")[-1][:-6]
                print("E: %s changed %s new %s gone %s fields new %s consts %s" % (c, [m.split("(")[0] for m in v["changed"]], v["new"], v["gone"], v["fields_new"],
                                                                                   sorted(v["consts"])))
                check(not v["gone"] and not v["fields_gone"], "E: %s loses no method or field" % c)
            pl = res.get("com/skyy/trees/SkyyTreesPlugin.class", {})
            check([m.split("(")[0] for m in pl.get("changed", [])] == ["setup"] or set(m.split("(")[0] for m in pl.get("changed", [])) <= {"setup"},
                  "E: the plugin changes only setup (TreeMig32.run + the version string)")
            cf = res.get("com/skyy/trees/TreeCfg.class", {})
            lh = [h for k_, hs in cf.get("hunks", {}).items() if k_.startswith("load(") for h in (hs if isinstance(hs, list) else [[["?"], ["?"]]])]
            check(set(m.split("(")[0] for m in cf.get("changed", [])) <= {"apply", "<clinit>", "load"} and set(cf.get("consts", {})) <= {"DEFAULTS"}
                  and all(len(h[0]) == len(h[1]) == 1 and h[0][0].startswith('ldc "# SkyyTrees 0.3.1') and h[1][0].startswith('ldc "# SkyyTrees 0.3.2') for h in lh),
                  "E: TreeCfg changes only apply (the default ON), <clinit> (CLASS_ON = true) and the default file text (load: only its inlined copy): %s" % lh)
            mg = res.get("com/skyy/trees/TreeMig.class", {})
            check(set(m.split("(")[0] for m in mg.get("changed", [])) <= {"<clinit>"}, "E: TreeMig changes only its static block (the class block now says true + the marker)")
        fake = os.path.join(SCRATCH, "fake")
        p = subprocess.run([sys.executable, me, "--mkfake", fake, "--dir", SCRATCH], env=env)
        check(p.returncode == 0, "stand-in classes generated")
        lo = os.path.join(SCRATCH, "logic.json")
        p = subprocess.run([sys.executable, me, "--logic", JAR, "--prev", PREV_JAR, "--fake", fake, "--live", LIVE_DIR, "--out", lo, "--dir", SCRATCH], env=env)
        check(p.returncode == 0 and os.path.isfile(lo), "logic child ran")
        if os.path.isfile(lo):
            r = json.load(open(lo))
            OKS[0] += r["oks"]
            for f in r["fails"]:
                FAILS.append(f)
        check(open(os.path.join(LIVE_DIR, "trees.properties"), "rb").read() == live_before, "the live trees.properties is unchanged")
    finally:
        if not KEEP:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyTrees %s vs %s: %d checks passed, %d failed" % (VERSION, PREV_VERSION, OKS[0], len(FAILS)))
    for f in FAILS[:60]:
        print("  FAILED:", f)
    print("SkyyTrees %s bare-JVM harness:" % VERSION, "PASS" if not FAILS else "FAIL")
    sys.exit(0 if not FAILS else 1)


if __name__ == "__main__":
    main()
