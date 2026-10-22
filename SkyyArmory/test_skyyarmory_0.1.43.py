"""Harness for SkyyArmory 0.1.43 (Balance P5: boss Sigil chances Legendary 3 -> 5 %, Fabled 1.5 -> 3 % + the one-time migrateP5;
tools/armory_0_1_43_patch.py). Build first:
    python tools/armory_0_1_43_patch.py && python SkyyArmory/build_skyyarmory_0.1.43.py
    python SkyyArmory/test_skyyarmory_0.1.43.py [--keep]
Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  S   static   the patch re-runs to identical bytes; no new class / command / system; setup: migrate040 -> migrateP5 -> load
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.42 -> 0.1.43: exactly the planned members (EXPECT)
  X   exec     ArmoryCfg defaults SGL_PCT 0 / 4 / 5 / 3 / 0; mP5Update (pure text) on every shape (both old LF / CRLF / "3.0", one hand-set kept
               + noted, already new silent, no lines -> marker at the end, a marked file); migrateP5 on a real file (History copy, one
               change-log line per key, second start = nothing, ArmoryCfg.load reads 5 / 3); a fresh file carries the marker
  D   live     START TWICE on a scratch COPY of the live Skyy_SkyyArmory (every migration in setup's order + load): only the two Sigil
               lines move (Properties), History copy, two change-log lines; the second start changes nothing
  AA  audit    the engine-access audit
Not executed here (UNVERIFIED until the game): a real boss kill's Sigil roll (ArmorySoul's roll code is unchanged - it reads SGL_PCT).
"""
import os, sys, json, hashlib, subprocess, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "balp5", "arm")]
import skyybuild as B
import harness_kit as HK

VERSION, OLD = "0.1.43", "0.1.42"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyarmory_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyarmory_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "armory_0_1_43_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.armory."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyArmory")
EXPECT = {"ArmoryCfg": ["+f MP5_KEYS", "+f MP5_LAST", "+f MP5_MARK", "+f MP5_MARK_ID", "+f MP5_NEW", "+f MP5_OLD", "+f MP5_WHO", "+m mP5Key",
                        "+m mP5Lk", "+m mP5Log", "+m mP5Same", "+m mP5Update", "+m migrateP5", "~<clinit>", "~m load", "~m reloadAll", "~m useDefaults"],
          "ArmoryCheck": ["~m packCheck", "~m packOf"], "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "CfgRows2": ["~<clinit>"],
          "SkyyArmoryPlugin": ["~m setup", "~m start"]}
MIGS = ("migrate012", "migrate013", "migrate014", "migrate016", "migrate017", "migrate018", "migrate021", "migrate035", "migrate036", "migrate040",
        "migrateP5")


def tree_hash(root):
    o = {}
    for d, _x, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            o[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
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
    K.check(g.startswith('"""SkyyArmory 0.1.43 - build script') and g.count('VERSION = "0.1.43"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand(", "makeClass("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    su = g[g.index("String m12 = @PKG@.ArmoryCfg.migrate012();"):]
    K.check(su.index("migrate040();") < su.index("migrateP5();") < su.index("@PKG@.ArmoryCfg.load();"), "S setup: migrate040 -> migrateP5 -> load")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_exec(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    JClass(PKG + "ArmoryLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyArmory")
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg, Paths = JClass(PKG + "ArmoryCfg"), JClass("java.nio.file.Paths")
    K.eq([float(x) for x in Cfg.SGL_PCT], [0.0, 4.0, 5.0, 3.0, 0.0], "X defaults: Sigil chances Unique 0 / Rare 4 / Legendary 5 / Fabled 3 / Mythic 0")
    MK = str(Cfg.MP5_MARK)

    def upd(t):
        r = Cfg.mP5Update(t)
        return None if r is None else (str(r[0]), str(r[1]), [str(x) for x in r[2]], [str(x) for x in r[3]])
    L, F_ = "sigil.chance.Legendary", "sigil.chance.Fabled"
    CH = "%s 3 -> 5, %s 1.5 -> 3" % (L, F_)
    RB = [L, "3", "5", F_, "1.5", "3"]
    cases = []
    for nl in ("\n", "\r\n"):
        src = ("a=1\n%s=3\n%s=1.5\nb=2\n" % (L, F_)).replace("\n", nl)
        exp = ("a=1\n" + MK + "\n%s=5\n%s=3\nb=2\n" % (L, F_)).replace("\n", nl)
        cases.append(("both old %r" % nl, upd(src), (exp, CH, [], RB)))
    cases.append(("3.0 counts", upd("%s=3.0\n" % L), (MK + "\n%s=5\n" % L, "%s 3.0 -> 5" % L, [], [L, "3.0", "5"])))
    cases.append(("one hand-set", upd("%s=7\n%s=1.5\n" % (L, F_)), (MK + "\n%s=7\n%s=3\n" % (L, F_), "%s 1.5 -> 3" % F_,
                  ["%s=7 kept (custom) - the 0.1.43 (Balance P5) default is 5" % L], [F_, "1.5", "3"])))
    cases.append(("already new", upd("%s=5\n%s=3\n" % (L, F_)), (MK + "\n%s=5\n%s=3\n" % (L, F_), "", [], [])))
    cases.append(("no lines", upd("a=1\n"), ("a=1\n" + MK + "\n", "", [], [])))
    cases.append(("marked", upd(MK + "\n%s=3\n" % L), None))
    bad = [(nm, g, e) for nm, g, e in cases if g != e]
    for b in bad[:4]:
        print("   X", b[0], "got", repr(b[1])[:300], "want", repr(b[2])[:300])
    K.check(not bad, "X mP5Update, %d cases: wrong %s" % (len(cases), [b[0] for b in bad]))
    # migrateP5 on a real file
    d = os.path.join(scratch, "mig")
    os.makedirs(d, exist_ok=True)
    fp = os.path.join(d, "config.properties")
    old = ("# test\r\nsigil.drops=true\r\nsigil.chance.Rare=4\r\n%s=3\r\n%s=1.5\r\nsigil.chance.Mythic=0\r\n" % (L, F_)).encode("latin-1")
    open(fp, "wb").write(old)
    Cfg.DIR, Cfg.FILE = Paths.get(d), Paths.get(fp)
    m1 = str(Cfg.migrateP5())
    nb = open(fp, "rb").read()
    K.eq(nb, old.replace(("%s=3\r\n%s=1.5" % (L, F_)).encode(), (MK + "\r\n%s=5\r\n%s=3" % (L, F_)).encode()), "X file: both move, marker above, CRLF kept")
    K.check(CH in m1, "X file: INFO names the change: %s" % m1)
    hist = [open(os.path.join(r_, f_), "rb").read() for r_, _d, fs in os.walk(os.path.join(d, "config-history")) for f_ in fs]
    K.check(old in hist, "X file: config-history holds the old bytes")
    lg = open(os.path.join(d, "config-changes.log"), encoding="latin-1").read()
    lk_ = lambda k: "sigil.chance[%s]" % k[len("sigil.chance."):]          # fix round: the kit's table key (Undo)
    K.check(lg.count("\tSkyyArmory 0.1.43\t-\tupdate\t%s\t3\t5\tok" % lk_(L)) == 1 and lg.count("\tSkyyArmory 0.1.43\t-\tupdate\t%s\t1.5\t3\tok" % lk_(F_)) == 1,
            "X file: one change-log line per key, as sigil.chance[<Sigil>]: %r" % lg[-300:])
    K.check(str(Cfg.migrateP5()) == "" and open(fp, "rb").read() == nb, "X file: the second start changes nothing")
    Cfg.load()
    K.eq([float(x) for x in Cfg.SGL_PCT][2:4], [5.0, 3.0], "X file: ArmoryCfg.load reads 5 / 3")
    # a fresh file (the loader writes the defaults): carries the marker, nothing to move
    d2 = os.path.join(scratch, "fresh")
    os.makedirs(d2, exist_ok=True)
    Cfg.DIR, Cfg.FILE = Paths.get(d2), Paths.get(os.path.join(d2, "config.properties"))
    Cfg.load()
    t = open(os.path.join(d2, "config.properties"), "rb").read()
    K.check(MK.encode("ascii") in t and ("\n%s=5\n" % L).encode() in t and ("\n%s=3\n" % F_).encode() in t, "X fresh: the default file says 5 / 3 + the marker")
    K.check(str(Cfg.migrateP5()) == "" and open(os.path.join(d2, "config.properties"), "rb").read() == t, "X fresh: left alone")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    JClass(PKG + "ArmoryLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyArmory")
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg = JClass(PKG + "ArmoryCfg")
    Paths = JClass("java.nio.file.Paths")
    Cfg.DIR = Paths.get(home)
    Cfg.FILE = Paths.get(home).resolve("config.properties")
    fp = os.path.join(home, "config.properties")
    lp = os.path.join(home, "config-changes.log")
    l0 = open(lp, "rb").read() if os.path.isfile(lp) else b""
    hashes, mids = [], []
    for start in (1, 2):
        for m in MIGS:
            if m == "migrateP5":
                mids.append(open(fp, "rb").read())
            r = str(getattr(Cfg, m)())
            if m == "migrateP5" and start == 1:
                print("   live migrateP5:", r[:200])
        Cfg.load()
        hashes.append(tree_hash(home))
    t1 = open(fp, "rb").read()
    po, pn = _props(mids[0]), _props(t1)
    K.eq(sorted(k for k in set(po) | set(pn) if po.get(k) != pn.get(k)), ["sigil.chance.Fabled", "sigil.chance.Legendary"], "D start 1: only the two Sigil lines move")
    K.eq((pn["sigil.chance.Legendary"], pn["sigil.chance.Fabled"]), ("5", "3"), "D the live file holds 5 / 3")
    lg = open(lp, "rb").read()[len(l0):].decode("utf-8")
    K.eq(sorted(ln.split("\t")[4] for ln in lg.split("\n") if "\tSkyyArmory 0.1.43\t-\tupdate\t" in ln), ["sigil.chance[Fabled]", "sigil.chance[Legendary]"],
         "D fix: two change-log lines with the kit's table keys sigil.chance[<Sigil>] (Server Setup -> Changes can Undo them)")
    K.check(any(open(os.path.join(r_, f_), "rb").read() == mids[0] for r_, _d, fs in os.walk(os.path.join(home, "config-history")) for f_ in fs),
            "D the config-history copy holds the bytes before the P5 update")
    K.check(hashes[0] == hashes[1], "D start 2 changes nothing")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyArmory", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("exec", run_exec), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyArmory"))
