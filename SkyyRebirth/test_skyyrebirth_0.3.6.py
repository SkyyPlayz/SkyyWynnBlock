"""SkyyRebirth 0.3.6 - harness for REBIRTHS UNLIMITED BY DEFAULT (tools/rebirth_0_3_6_patch.py): rebirth.max 0 = no limit (the new default)
+ the one-time migration RbCfg.migMax (an untouched old rebirth.max=10 -> 0, once).
Build first: python tools/rebirth_0_3_6_patch.py && python SkyyRebirth/build_skyyrebirth_0.3.6.py

    python SkyyRebirth/test_skyyrebirth_0.3.6.py --dir <empty folder inside tools/dev/scratch/> [--keep]

  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.3.5 -> 0.3.6: exactly the planned members differ
  L   limit    RbCfg.lim / maxTxt / ofMax with 0 and 10; loadCfg (no line / 0 / 10 / -5 / 5000); RbCheck.reqs' "Rebirths done" line (no limit:
               "OK ... (no limit)" at 0 and 500; a limit of 10: "NO ... 10 / 10"); RbCheck.tip (no "of", never maxed / maxed with a limit);
               rebirth:fn:stat "all" past 10 rebirths (stat.cap still caps it); the level-cap math unchanged (50 + 10 x n; SkyySkills clamps)
  M   mig      RbCfg.migMax EXECUTED on real files: the live NewBetaTest text (rebirth.max=10) -> 0 + marker, every other byte kept, the old bytes
               in config-history, one config-changes.log line 10 -> 0, loadCfg reads 0; run twice = nothing; CRLF; admin values (5, 100, a
               continued value) KEPT (marker only); no line -> marker only (it reads 0); config-history not writable -> untouched, next start
               migrates; no file -> nothing; a fresh file (rebirth.max=0 + marker) is never touched; migOn (0.3.4) still behaves the same
               through migPlanT; setup(): migOn, migMax, loadCfg, CfgPub.start in that order
  D   live     a scratch COPY of the live NewBetaTest Skyy_SkyyRebirth: start 1 = only rebirth.max 10 -> 0 + marker (+ history / change
               log); start 2 writes nothing; the kit starts on the migrated file
  P            test_skyyrebirth_0.3.5.py's page phase on this jar (the kit hub page, every fit text incl. the new no-limit lines)
  X (--exec)   test_skyyrebirth_0.3.5.py's exec phase with the CURRENT SET participant jars. 2026-10-19: 15 MARKET / CONTINUE / ECHO / STEP
               checks fail IDENTICALLY with the 0.3.5 jar (the old harness expects SkyySkills 0.4.47 / Auctions 0.1.10 / Bazaar 0.1.18
               numbers and wording) - no new failure from 0.3.6, so it is opt-in until that harness is brought up to the current set
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import deploy_set as DS

VERSION = "0.3.6"
RB = "com.skyy.rebirth."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyRebirth-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyRebirth-0.3.5.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "cr41", "rb")))
LIVE_RB = os.path.join(B.USERDATA, "Saves", DS.WORLD, "mods", "Skyy_SkyyRebirth")


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


T34 = _load("t_rb034", os.path.join(HERE, "test_skyyrebirth_0.3.4.py"))
_COMPARE = HK.run_compare
T35 = _load("t_rb035", os.path.join(HERE, "test_skyyrebirth_0.3.5.py"))
HK.run_compare = _COMPARE       # 0.3.5's compare override expects its kit art: 0.3.6 changes no non-class entry but manifest.json
for _m in (T34, T35, T35.T32, T35.T32.T31, T35.T3, T35.T2):
    _m.VERSION = VERSION
    _m.JAR = JAR
_PIN = dict(DS.SET)
_J = lambda mod: os.path.join(ROOT, mod, "%s-%s.jar" % (mod, _PIN[mod]))
T35.T2.SK_JAR, T35.T2.CO_JAR, T35.T2.BK_JAR, T35.T2.PF_JAR = _J("SkyySkills"), _J("SkyyCoins"), _J("SkyyBank"), _J("SkyyProfiles")
T35.T3.AH_JAR, T35.T3.BZ_JAR, T35.T32.GEAR_JAR = _J("SkyyAuctions"), _J("SkyyBazaar"), _J("SkyyGear")
os.environ["SKYY_HARNESS_CP"] = os.pathsep.join([p_ for p_ in os.environ.get("SKYY_HARNESS_CP", "").split(os.pathsep) if p_ and "SkyyCore" not in p_] + [_J("SkyyCore")])

EXPECT = {
    "RbCfg": ["~<clinit>", "~m loadCfg", "~m writeDefaults", "~m migPlan", "~m migSame", "+m migPlanT", "+m migSameT", "+m migLineT", "+m migMax",
              "+m lim", "+m maxTxt", "+m ofMax", "+f MAX_MIG_ID", "+f MAX_MIG_MARK", "+f MAX_MIG_KEY", "+f MAX_MIG_OLD", "+f MAX_MIG_NEW",
              "+f MAX_MIG_WHO", "+f MAX_MIG_LAST"],
    "SkyyRebirthPlugin": ["~m setup"],
    "RbCheck": ["~m reqs", "~m gains", "~m tip"], "RbTree": ["~m stat", "~m cos"], "RbFn": ["~m apply"], "RbTx": ["~m begin0", "~m decide", "~m dryRun", "~m status"],
    "RbPage": ["~m fill"],
    "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"],
    "RbStore": ["~m writeNow"],
}
ADDED = []
R = lambda n: __import__("jpype").JClass(RB + n)


def run_limit(out, jar, scratch, _home):
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    from jpype import JClass
    K = HK.Child(out)
    Cfg = R("RbCfg")
    K.check(int(Cfg.MAX) == 0, "L the code default of rebirth.max is 0 (no limit)")
    Cfg.MAX = 0
    K.check(int(Cfg.lim()) == 2147483647 and str(Cfg.maxTxt()) == "no limit" and str(Cfg.ofMax()) == "", "L no limit: lim = Integer.MAX_VALUE, 'no limit', no ' of'")
    Cfg.MAX = 10
    K.check(int(Cfg.lim()) == 10 and str(Cfg.maxTxt()) == "10" and str(Cfg.ofMax()) == " of 10", "L a limit of 10: 10 / '10' / ' of 10'")
    home = os.path.join(scratch, "l")
    os.makedirs(home)
    Cfg2, path = T34.kit_home(home)
    f = os.path.join(home, "config.properties")
    for txt, want in ((b"caps.levels=10\n", 0), (b"rebirth.max=0\n", 0), (b"rebirth.max=10\n", 10), (b"rebirth.max=-5\n", 0), (b"rebirth.max=5000\n", 1000)):
        open(f, "wb").write(txt)
        c = str(Cfg.loadCfg(False))
        K.check(int(Cfg.MAX) == want and ((", max no limit," in c) if want == 0 else ((", max %d," % want) in c)), "L loadCfg %r -> MAX %d (%s)" % (txt, want, c[:40]))
    rows = dict((str(r[0]), [str(x) for x in list(r)]) for r in R("CfgRows").header()[7])
    K.check(rows["rebirth.max"][4:7] == ["0", "0", "1000"] and "0 = no limit" in rows["rebirth.max"][10], "L Server Setup row: default 0, 0 - 1000, help says 0 = no limit: %s" % rows["rebirth.max"])
    # RbCheck.reqs' rebirth count line (an empty bridge: the other lines say what is missing)
    HM = JClass("java.util.concurrent.ConcurrentHashMap")
    Cfg.BRIDGE = HM()
    U = JClass("java.util.UUID").randomUUID()
    lines = {}
    for mx, n in ((0, 0), (0, 500), (10, 3), (10, 10)):
        Cfg.MAX = mx
        try:
            r = R("RbCheck").reqs(U, "default", n)
            lines[(mx, n)] = str(r[0][2])
        except Exception as ex:
            lines[(mx, n)] = "THREW %s" % ex
    K.check(lines[(0, 0)] == "OK  Rebirths done 0 (no limit)" and lines[(0, 500)] == "OK  Rebirths done 500 (no limit)"
            and lines[(10, 3)] == "OK  Rebirths done 3 / 10" and lines[(10, 10)] == "NO  Rebirths done 10 / 10", "L reqs' rebirth line: %s" % lines)
    req = [JClass("java.lang.String[]")(["OK  a"]), JClass("java.lang.String[]")(["x"]), JClass("java.lang.Boolean").TRUE, JClass("java.lang.Boolean").FALSE, None]
    gain = [JClass("java.lang.String[]")(["Mining  +3 points"]), JClass("java.lang.String[]")(["x"]), "Caps", JClass("java.lang.Integer")(3), "Caps +10 levels", JClass("java.lang.Boolean").FALSE]
    JO = JClass("java.lang.Object[]")
    Cfg.MAX = 0
    t0 = str(R("RbCheck").tip(250, JO(req), JO(gain)))
    Cfg.MAX = 10
    t1 = str(R("RbCheck").tip(4, JO(req), JO(gain)))
    t2 = str(R("RbCheck").tip(10, JO(req), JO(gain)))
    K.check("Rebirth 251 - the void imprints your soul" in t0 and "WHAT YOU WOULD GET" in t0 and "Max rebirths" not in t0, "L tip, no limit: 'Rebirth 251 - ...', gains shown")
    K.check("Rebirth 5 of 10 - the void" in t1 and "Max rebirths reached (10 of 10)" in t2 and "WHAT YOU WOULD GET" not in t2, "L tip with a limit of 10: as 0.3.5")
    # rebirth:fn:stat "all": 3 % a rebirth, cap 30 % (unchanged), no longer stopped at 10 rebirths by the max
    P = JClass("java.util.Properties")()
    Cfg.MAX = 0
    a0 = [float(R("RbTree").stat(P, n, "all")) for n in (5, 9, 50)]
    Cfg.MAX = 3
    a1 = float(R("RbTree").stat(P, 9, "all"))
    K.check(a0 == [15.0, 27.0, 30.0] and a1 == 9.0, "L stat all: no limit 15 / 27 / 30 (cap) ; a limit of 3 -> 9 (%s, %s)" % (a0, a1))
    K.check([int(R("RbMath").cap(50, "Mining", n)) for n in (0, 5, 6)] == [50, 100, 110] and int(R("RbMath").cap(50, "Exploration", 6)) == 50,
            "L the cap math is unchanged (50 + 10 a rebirth; SkyySkills levels.capMax 100 clamps it)")
    Cfg.MAX = 0
    K.save()


def run_mig(out, jar, scratch, _home):
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    K = HK.Child(out)
    home = os.path.join(scratch, "m", "mods", "Skyy_SkyyRebirth")
    os.makedirs(home)
    Cfg, path = T34.kit_home(home)
    cfgf = os.path.join(home, "config.properties")
    hist_d = os.path.join(home, "config-history")
    chg_f = os.path.join(home, "config-changes.log")
    MARK = str(Cfg.MAX_MIG_MARK).encode("latin-1")

    def hist_has(b_):
        return os.path.isdir(hist_d) and any(open(os.path.join(hist_d, f_), "rb").read() == b_ for f_ in os.listdir(hist_d) if f_.endswith(".bak"))

    def chg():
        return open(chg_f, encoding="utf-8").read().splitlines() if os.path.isfile(chg_f) else []

    def mig(b_):
        open(cfgf, "wb").write(b_)
        return str(Cfg.migMax(path(cfgf))), open(cfgf, "rb").read()

    live_cfg = os.path.join(LIVE_RB, "config.properties")
    A_ = open(live_cfg, "rb").read() if os.path.isfile(live_cfg) else None
    K.check(A_ is not None and A_.count(b"\nrebirth.max=10\n") == 1, "M the live config.properties (read only) holds rebirth.max=10")
    if A_ is None:
        A_ = b"# head\nrebirth.on=true\nrebirth.max=10\ncaps.levels=10\n"
    wantA = A_.replace(b"\nrebirth.max=10\n", b"\nrebirth.max=0\n" + MARK + b"\n")
    n0 = len(chg())
    rA, gotA = mig(A_)
    cl = chg()
    K.check(gotA == wantA and "rebirth.max 10 -> 0" in rA and hist_has(A_) and len(cl) == n0 + 1
            and "\trebirth.max\t10\t0\tok" in cl[-1] and "SkyyRebirth 0.3.6" in cl[-1],
            "M an untouched rebirth.max=10 -> 0: the marker under it, every other byte kept, the old bytes in config-history, one change-log "
            "line 10 -> 0 (Undo = 10) (%s / %s)" % (rA, cl[-1:]))
    Cfg.MAX = 7
    Cfg.loadCfg(False)
    K.check(int(Cfg.MAX) == 0, "M loadCfg reads the migrated file: no limit")
    rA2 = str(Cfg.migMax(path(cfgf)))
    K.check(rA2 == "" and open(cfgf, "rb").read() == gotA and len(chg()) == n0 + 1, "M run once: the second start changes nothing (%r)" % rA2)
    K.check(str(Cfg.migOn(path(cfgf))) == "" and open(cfgf, "rb").read() == gotA, "M the 0.3.4 migOn still sees its own marker and does nothing")
    C_ = A_.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    rC, gotC = mig(C_)
    K.check(gotC == wantA.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n") and hist_has(C_) and len(chg()) == n0 + 2 and b"\n" not in gotC.replace(b"\r\n", b""),
            "M the same file in CRLF: 0 + marker in CRLF, every other byte kept, history copy, one more change-log line (%s)" % rC)
    n1 = len(chg())
    for b_, label, mx in ((b"a=1\nrebirth.max=5\ncaps.levels=10\n", "5", 5), (b"a=1\r\nrebirth.max = 100\r\ncaps.levels=10\r\n", "100 (CRLF)", 100),
                          (b"rebirth.max=1000\n", "1000", 1000), (b"rebirth.max=\\\n  10\ncaps.levels=10\n", "a continued value", 10),
                          (b"rebirth.max=10\nrebirth.max=20\n", "10 then 20 (last wins)", 20)):
        r_, got_ = mig(b_)
        if label == "a continued value":
            want_ = b"rebirth.max=\\\n  10\n" + MARK + b"\ncaps.levels=10\n"
        elif label.startswith("10 then 20"):
            want_ = b"rebirth.max=10\nrebirth.max=20\n" + MARK + b"\n"
        else:
            nl = b"\r\n" if b"\r\n" in b_ else b"\n"
            ls = b_.split(nl)
            k_ = [i for i, x in enumerate(ls) if x.startswith(b"rebirth.max")][-1]
            want_ = nl.join(ls[:k_ + 1] + [MARK] + ls[k_ + 1:])
        Cfg.loadCfg(False)
        K.check(got_ == want_ and "kept" in r_ and len(chg()) == n1 and hist_has(b_) and int(Cfg.MAX) == mx,
                "M an admin's rebirth.max (%s) is KEPT: only the marker is added, no change-log line, reads %d (%r / %r)" % (label, mx, r_, got_))
    D_ = b"rebirth.on=true\ncaps.levels=10\n"
    rD, gotD = mig(D_)
    Cfg.loadCfg(False)
    K.check(gotD == D_ + MARK + b"\n" and "no setting changed" in rD and len(chg()) == n1 and int(Cfg.MAX) == 0,
            "M no rebirth.max line (reads the new default 0): marker only, no change-log line (%s / %r)" % (rD, gotD))
    D2 = b"caps.levels=10"
    rD2, gotD2 = mig(D2)
    K.check(gotD2 == D2 + b"\n" + MARK + b"\n", "M no line and no final newline: the marker on its own line (%r)" % gotD2)
    shutil.rmtree(hist_d)
    open(hist_d, "wb").write(b"x")
    E_ = b"x=1\nrebirth.max=10\n"
    nE = len(chg())
    rE, gotE = mig(E_)
    K.check(rE == "" and gotE == E_ and len(chg()) == nE, "M config-history not writable: the file is untouched, no change-log line (%r)" % rE)
    os.remove(hist_d)
    rE2, gotE2 = str(Cfg.migMax(path(cfgf))), open(cfgf, "rb").read()
    K.check(gotE2 == b"x=1\nrebirth.max=0\n" + MARK + b"\n" and hist_has(E_), "M ... the next start migrates it (%s)" % rE2)
    # 0.3.4's migOn through migPlanT: the same result as 0.3.4 (false -> true + its marker; no line -> appended)
    ON_MARK = str(Cfg.MIG_MARK).encode("latin-1")
    open(cfgf, "wb").write(b"a=1\nrebirth.on=false\nrebirth.max=10\n")
    str(Cfg.migOn(path(cfgf)))
    K.check(open(cfgf, "rb").read() == b"a=1\nrebirth.on=true\n" + ON_MARK + b"\nrebirth.max=10\n", "M migOn (0.3.4) unchanged: false -> true + its marker")
    open(cfgf, "wb").write(b"rebirth.max=10\n")
    str(Cfg.migOn(path(cfgf)))
    K.check(open(cfgf, "rb").read() == b"rebirth.max=10\nrebirth.on=true\n" + ON_MARK + b"\n", "M migOn (0.3.4) unchanged: a missing line is appended")
    open(cfgf, "wb").write(b"rebirth.on=yes\n")
    rk = str(Cfg.migOn(path(cfgf)))
    K.check("rebirth.on=yes kept (an admin's value) - the 0.3.4 default is true (rebirth on)" in rk, "M migOn (0.3.4) unchanged: the kept note (%s)" % rk)
    os.remove(cfgf)
    K.check(str(Cfg.migMax(path(cfgf))) == "" and not os.path.exists(cfgf), "M no file: nothing to do")
    Cfg.MAX = 7
    c = str(Cfg.loadCfg(True))
    fresh = open(cfgf, "rb").read()
    K.check(int(Cfg.MAX) == 0 and fresh.count(b"\nrebirth.max=0\n" + MARK + b"\n") == 1 and str(Cfg.migMax(path(cfgf))) == "" and str(Cfg.migOn(path(cfgf))) == ""
            and open(cfgf, "rb").read() == fresh, "M a fresh 0.3.6 file: rebirth.max=0 + the marker, no limit, neither migration touches it (%s)" % c[:70])
    calls = T34.setup_calls(jar)
    idx = lambda n: calls.index(n) if n in calls else -1
    K.check(0 <= idx("RbCfg.migOn") < idx("RbCfg.migMax") < idx("RbCfg.loadCfg") < idx("CfgPub.start") and idx("CfgHist.init") < idx("RbCfg.migMax"),
            "M setup(): migOn, then migMax, then loadCfg, then CfgPub.start: %s" % [c_ for c_ in calls if c_.split(".")[0] in ("RbCfg", "CfgPub", "CfgHist", "CfgLog")][:8])
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    K = HK.Child(out)
    mods = os.path.dirname(home)
    cfgf = os.path.join(home, "config.properties")
    old = open(cfgf, "rb").read()
    t0 = T34.tree(home)
    Cfg, path = T34.kit_home(home)
    r0 = str(Cfg.migOn(path(cfgf)))
    r1 = str(Cfg.migMax(path(cfgf)))
    c1 = str(Cfg.loadCfg(True))
    t1 = T34.tree(home)
    new = open(cfgf, "rb").read()
    MARK = str(Cfg.MAX_MIG_MARK).encode("latin-1")
    added = sorted(set(t1) - set(t0))
    K.check(r0 == "" and new == old.replace(b"\nrebirth.max=10\n", b"\nrebirth.max=0\n" + MARK + b"\n") and new != old and int(Cfg.MAX) == 0,
            "D start 1 on the live copy: rebirth.max 10 -> 0 + the marker, every other byte kept, no limit (%s)" % r1)
    K.check(all(a_.startswith("config-history/") or a_ == "config-changes.log" for a_ in added)
            and all(t1[k_] == t0[k_] for k_ in t0 if k_ not in ("config.properties", "config-changes.log") and not k_.startswith("config-history/")),
            "D start 1 adds only config-history + config-changes.log; nothing else changed: %s" % added)
    r2 = str(Cfg.migMax(path(cfgf)))
    Cfg.loadCfg(True)
    K.check(r2 == "" and T34.tree(home) == t1, "D start 2 writes nothing (%r)" % r2)
    JClass(RB + "CfgPub").start(path(mods), None)
    JClass(RB + "CfgPub").flush()
    K.check(T34.tree(home) == t1, "D the config kit starts on the migrated file and writes nothing")
    K.notes.append("D live: %s | %s" % (r1, c1[:80]))
    K.save()


if __name__ == "__main__":
    assert os.path.isfile(B.JAVASSIST), B.JAVASSIST
    if "--phase" not in sys.argv:
        for j_ in (T35.T2.SK_JAR, T35.T2.CO_JAR, T35.T2.BK_JAR, T35.T2.PF_JAR, T35.T3.AH_JAR, T35.T3.BZ_JAR, T35.T32.GEAR_JAR, OLD_JAR, _J("SkyyCore")):
            assert os.path.isfile(j_), j_
    HK.run(name="SkyyRebirth", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=RB, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("limit", run_limit), ("mig", run_mig), ("live", run_live),
                   ("page", T35.T32.sub(T35.run_page, "p"))]
           + ([("exec", T35.T32.sub(T35.T32.dev(T35.T3.run_exec, T35.X03_DEV), "x3"))] if "--exec" in sys.argv else []),
           script=__file__, live=(LIVE_RB, "Skyy_SkyyRebirth"))
