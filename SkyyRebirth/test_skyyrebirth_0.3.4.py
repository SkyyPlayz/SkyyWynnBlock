"""SkyyRebirth 0.3.4 - harness for REBIRTH ON BY DEFAULT (tools/rebirth_0_3_4_patch.py): rebirth.on defaults to true + the one-time
migration RbCfg.migOn (an untouched old rebirth.on=false -> true, once).
Build first: python tools/rebirth_0_3_4_patch.py && python SkyyRebirth/build_skyyrebirth_0.3.4.py

    python SkyyRebirth/test_skyyrebirth_0.3.4.py --dir <empty folder inside tools/dev/scratch/> [--keep]

  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.3.3 -> 0.3.4: exactly the planned members differ (RbCfg: default + migOn; setup(); the kit's default text / header)
  M   mig      RbCfg.migOn EXECUTED on real files: an untouched LF file (the live NewBetaTest text) -> true + marker, every other byte kept,
               the old bytes in config-history, one config-changes.log line false -> true, loadCfg reads ON; run twice = nothing; the same in
               CRLF; admin-edited values (true, TRUE, no, a continued value) KEPT (marker only, no change-log line); no line -> appended;
               config-history not writable -> file untouched, next run tries again; no file -> nothing, loadCfg writes the 0.3.4 default
               (marker included, ON); the Server Setup row default is true; setup() calls migOn before loadCfg before CfgPub.start
  S   stat     test_skyyrebirth_0.3.3.py's stat phase on this jar (rebirth:fn:stat, unchanged)
  D   live     a scratch COPY of the live NewBetaTest Skyy_SkyyRebirth: start 1 = only rebirth.on false -> true + marker (+ history /
               change log); start 2 writes nothing; the kit starts on the migrated file
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.3.4"
RB = "com.skyy.rebirth."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyRebirth-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyRebirth-0.3.3.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "gates01", "rb")))
LIVE_RB = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyRebirth")


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


T33 = _load("t_rb033", os.path.join(HERE, "test_skyyrebirth_0.3.3.py"))
T33.VERSION = VERSION
T33.JAR = JAR

EXPECT = {
    "RbCfg": ["~<clinit>", "~m loadCfg", "~m writeDefaults", "+f MIG_ID", "+f MIG_MARK", "+f MIG_KEY", "+f MIG_OLD", "+f MIG_NEW", "+f MIG_WHO", "+f MIG_LAST",
              "+m migPlan", "+m migSame", "+m migFileIdx", "+m migSaved", "+m migLine", "+m migOn"],
    "SkyyRebirthPlugin": ["~m setup"],
    "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"],
    "RbStore": ["~m writeNow"],
}
ADDED = []


def tree(d):
    out = {}
    for r, _ds, fs in os.walk(d):
        for f in fs:
            p = os.path.join(r, f)
            out[os.path.relpath(p, d).replace(os.sep, "/")] = open(p, "rb").read()
    return out


def kit_home(home):
    from jpype import JClass, JArray
    P = JClass("java.nio.file.Paths")
    path = lambda p_: P.get(p_, JArray(JClass("java.lang.String"))([]))
    R = lambda n: JClass(RB + n)
    R("CfgRows").HOME = path(home)
    R("CfgHist").init()
    R("CfgLog").init()
    Cfg = R("RbCfg")
    Cfg.DIR = path(home)
    Cfg.FILE = path(os.path.join(home, "config.properties"))
    return Cfg, path


def setup_calls(jar):
    """the invoke order inside SkyyRebirthPlugin.setup() (javassist, read only)"""
    from jpype import JClass
    pool = JClass("javassist.ClassPool")(True)
    pool.appendClassPath(jar)
    pool.appendClassPath(B.SERVER_JAR)
    m = pool.get(RB + "SkyyRebirthPlugin").getDeclaredMethod("setup")
    ci = m.getMethodInfo().getCodeAttribute().iterator()
    cp = m.getMethodInfo().getConstPool()
    names = []
    while ci.hasNext():
        i = ci.next()
        op = ci.byteAt(i)
        if op in (0xb6, 0xb7, 0xb8, 0xb9):
            idx = ci.u16bitAt(i + 1)
            cls = cp.getInterfaceMethodrefClassName(idx) if op == 0xb9 else cp.getMethodrefClassName(idx)
            nm = cp.getInterfaceMethodrefName(idx) if op == 0xb9 else cp.getMethodrefName(idx)
            names.append("%s.%s" % (str(cls).split(".")[-1], nm))
    return names


def run_mig(out, jar, scratch, _home):
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    K = HK.Child(out)
    home = os.path.join(scratch, "m", "mods", "Skyy_SkyyRebirth")
    os.makedirs(home)
    Cfg, path = kit_home(home)
    cfgf = os.path.join(home, "config.properties")
    hist_d = os.path.join(home, "config-history")
    chg_f = os.path.join(home, "config-changes.log")
    MARK = str(Cfg.MIG_MARK).encode("latin-1")

    def hist_has(b_):
        return os.path.isdir(hist_d) and any(open(os.path.join(hist_d, f_), "rb").read() == b_ for f_ in os.listdir(hist_d) if f_.endswith(".bak"))

    def chg():
        return open(chg_f, encoding="utf-8").read().splitlines() if os.path.isfile(chg_f) else []

    def mig_on(b_):
        open(cfgf, "wb").write(b_)
        return str(Cfg.migOn(path(cfgf))), open(cfgf, "rb").read()

    live_cfg = os.path.join(LIVE_RB, "config.properties")
    A_ = open(live_cfg, "rb").read() if os.path.isfile(live_cfg) else None
    K.check(A_ is not None and b"\r\n" not in A_ and A_.count(b"\nrebirth.on=false\n") == 1,
            "M the live NewBetaTest config.properties (read only) is an LF file holding rebirth.on=false")
    if A_ is None:
        A_ = b"# head\nrebirth.on=false\nrebirth.max=10\n"
    wantA = A_.replace(b"\nrebirth.on=false\n", b"\nrebirth.on=true\n" + MARK + b"\n")
    n0 = len(chg())
    rA, gotA = mig_on(A_)
    cl = chg()
    K.check(gotA == wantA and "rebirth.on false -> true" in rA and hist_has(A_) and len(cl) == n0 + 1
            and "\trebirth.on\tfalse\ttrue\tok" in cl[-1] and "SkyyRebirth 0.3.4" in cl[-1],
            "M an untouched LF rebirth.on=false -> true: the marker under it, every other byte kept, the old bytes in config-history, one "
            "change-log line false -> true (Undo = false) (%s / %s)" % (rA, cl[-1:]))
    Cfg.ON = False
    Cfg.loadCfg(False)
    K.check(bool(Cfg.ON), "M loadCfg reads the migrated file: rebirth ON")
    rA2 = str(Cfg.migOn(path(cfgf)))
    K.check(rA2 == "" and open(cfgf, "rb").read() == gotA and len(chg()) == n0 + 1, "M run once: the second start changes nothing (%r)" % rA2)
    C_ = A_.replace(b"\n", b"\r\n")
    rC, gotC = mig_on(C_)
    K.check(gotC == wantA.replace(b"\n", b"\r\n") and hist_has(C_) and len(chg()) == n0 + 2 and b"\n" not in gotC.replace(b"\r\n", b""),
            "M the same file in CRLF: true + marker in CRLF, every other byte kept, history copy, one more change-log line (%s)" % rC)
    rC2 = str(Cfg.migOn(path(cfgf)))
    K.check(rC2 == "" and open(cfgf, "rb").read() == gotC and len(chg()) == n0 + 2, "M CRLF run twice: nothing")
    n1 = len(chg())
    for b_, label in ((b"a=1\nrebirth.on=true\nrebirth.max=10\n", "true"), (b"a=1\r\nrebirth.on = TRUE\r\nrebirth.max=10\r\n", "TRUE (CRLF)"),
                      (b"rebirth.on=no\nrebirth.max=10\n", "no"), (b"rebirth.on=\\\n  false\nrebirth.max=10\n", "a continued value"),
                      (b"rebirth.on=false\nrebirth.on=true\n", "false then true (last wins)")):
        r_, got_ = mig_on(b_)
        lines = b_.split(b"\n")
        # the marker goes right under the last rebirth.on entry
        if label == "a continued value":
            want_ = b"rebirth.on=\\\n  false\n" + MARK + b"\nrebirth.max=10\n"
        elif label == "false then true (last wins)":
            want_ = b"rebirth.on=false\nrebirth.on=true\n" + MARK + b"\n"
        else:
            nl = b"\r\n" if b"\r\n" in b_ else b"\n"
            ls = b_.split(nl)
            k_ = [i for i, x in enumerate(ls) if x.startswith(b"rebirth.on")][-1]
            want_ = nl.join(ls[:k_ + 1] + [MARK] + ls[k_ + 1:])
        Cfg.loadCfg(False)
        K.check(got_ == want_ and "kept" in r_ and len(chg()) == n1 and hist_has(b_),
                "M an admin's rebirth.on (%s) is KEPT: only the marker is added, no change-log line (%r / %r)" % (label, r_, got_))
        if label == "no":
            K.check(not bool(Cfg.ON), "M ... rebirth.on=no still reads OFF (an admin's choice)")
    D_ = b"rebirth.max=10\ncaps.levels=10\n"
    rD, gotD = mig_on(D_)
    Cfg.loadCfg(False)
    K.check(gotD == D_ + b"rebirth.on=true\n" + MARK + b"\n" and "line added" in rD and len(chg()) == n1 + 1 and bool(Cfg.ON),
            "M no rebirth.on line (it read the old default false) -> rebirth.on=true appended + marker, one change-log line (%s / %r)" % (rD, gotD))
    D2 = b"rebirth.max=10"
    rD2, gotD2 = mig_on(D2)
    K.check(gotD2 == D2 + b"\nrebirth.on=true\n" + MARK + b"\n", "M no line and no final newline: appended on its own line (%r)" % gotD2)
    # a failure: config-history cannot be written (a FILE where the folder should be) -> untouched, the next start tries again
    import shutil
    shutil.rmtree(hist_d)
    open(hist_d, "wb").write(b"x")
    E_ = b"x=1\nrebirth.on=false\n"
    nE = len(chg())
    rE, gotE = mig_on(E_)
    K.check(rE == "" and gotE == E_ and len(chg()) == nE, "M config-history not writable: the file is untouched, no change-log line (%r)" % rE)
    os.remove(hist_d)
    rE2, gotE2 = str(Cfg.migOn(path(cfgf))), open(cfgf, "rb").read()
    K.check(gotE2 == b"x=1\nrebirth.on=true\n" + MARK + b"\n" and hist_has(E_), "M ... the next start migrates it (%s)" % rE2)
    # a fresh install: no file -> nothing; loadCfg writes the 0.3.4 default (marker included, ON)
    os.remove(cfgf)
    K.check(str(Cfg.migOn(path(cfgf))) == "" and not os.path.exists(cfgf), "M no file: nothing to do")
    Cfg.ON = False
    c = str(Cfg.loadCfg(True))
    fresh = open(cfgf, "rb").read()
    K.check(bool(Cfg.ON) and "rebirth ON" in c and fresh.count(b"\nrebirth.on=true\n" + MARK + b"\n") == 1 and Cfg.migPlan(fresh.decode("latin-1")) is None
            and str(Cfg.migOn(path(cfgf))) == "" and open(cfgf, "rb").read() == fresh,
            "M a fresh 0.3.4 file: rebirth.on=true + the marker, ON, migOn never touches it (%s)" % c[:60])
    os.remove(cfgf)
    open(cfgf, "wb").write(b"rebirth.max=5\n")
    os.chmod(cfgf, 0o644)
    Cfg.ON = False
    Cfg.loadCfg(False)
    K.check(bool(Cfg.ON), "M a file without rebirth.on reads ON (the code default is true)")
    rows = dict((str(r[0]), [str(x) for x in list(r)]) for r in JClassR("CfgRows").header()[7])
    K.check(rows["rebirth.on"][4] == "true", "M the Server Setup row default is true: %s" % rows["rebirth.on"])
    calls = setup_calls(jar)
    idx = lambda n: calls.index(n) if n in calls else -1
    K.check(0 <= idx("RbCfg.migOn") < idx("RbCfg.loadCfg") < idx("CfgPub.start") and idx("CfgHist.init") < idx("RbCfg.migOn")
            and idx("CfgLog.init") < idx("RbCfg.migOn"),
            "M setup(): CfgHist.init / CfgLog.init, then migOn, then loadCfg, then CfgPub.start: %s" % [c_ for c_ in calls if c_.split(".")[0] in ("RbCfg", "CfgPub", "CfgHist", "CfgLog")][:8])
    K.save()


def JClassR(n):
    from jpype import JClass
    return JClass(RB + n)


def run_live(out, jar, scratch, home):
    from jpype import JClass
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    K = HK.Child(out)
    mods = os.path.dirname(home)
    cfgf = os.path.join(home, "config.properties")
    old = open(cfgf, "rb").read()
    t0 = tree(home)
    Cfg, path = kit_home(home)
    r1 = str(Cfg.migOn(path(cfgf)))
    c1 = str(Cfg.loadCfg(True))
    t1 = tree(home)
    new = open(cfgf, "rb").read()
    MARK = str(Cfg.MIG_MARK).encode("latin-1")
    added = sorted(set(t1) - set(t0))
    K.check(new == old.replace(b"\nrebirth.on=false\n", b"\nrebirth.on=true\n" + MARK + b"\n") and new != old and bool(Cfg.ON),
            "D start 1 on the live copy: rebirth.on false -> true + the marker, every other byte kept, rebirth ON (%s)" % r1)
    K.check(all(a_.startswith("config-history/") or a_ == "config-changes.log" for a_ in added)
            and all(t1[k_] == t0[k_] for k_ in t0 if k_ != "config.properties"),
            "D start 1 adds only config-history + config-changes.log; nothing else changed: %s" % added)
    r2 = str(Cfg.migOn(path(cfgf)))
    Cfg.loadCfg(True)
    K.check(r2 == "" and tree(home) == t1, "D start 2 writes nothing (%r)" % r2)
    JClass(RB + "CfgPub").start(path(mods), None)
    JClass(RB + "CfgPub").flush()
    K.check(tree(home) == t1, "D the config kit starts on the migrated file and writes nothing")
    K.notes.append("D live: %s | %s" % (r1, c1[:80]))
    K.save()


if __name__ == "__main__":
    assert os.path.isfile(B.JAVASSIST), B.JAVASSIST
    HK.run(name="SkyyRebirth", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=RB, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("mig", run_mig), ("stat", T33.run_stat), ("live", run_live)],
           script=__file__, live=(LIVE_RB, "Skyy_SkyyRebirth"))
