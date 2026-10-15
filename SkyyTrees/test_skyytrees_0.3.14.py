"""SkyyTrees 0.3.14 - harness for BASE TREE SAP (tools/trees_0_3_14_patch.py), with the 0.3.11 replant scenarios as the regression on the
0.3.14 jar. Child JVMs run the game's own JRE with the cached HytaleServer.jar copy, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch
folder. The live save data is only READ and copied into scratch.

    python SkyyTrees/test_skyytrees_0.3.14.py --dir <empty folder inside tools/dev/scratch/> [--keep]

SECTIONS: A load + verify both jars (0.3.14 + 0.3.13); CC class compare 0.3.13 -> 0.3.14 (no class added / removed; structural changes only in
TreeGather + TreeCfg, + the ready line (kit version) in SkyyTreesPlugin.setup; the one new field TreeCfg.SAP_BASE); JT assets byte for byte 0.3.13's, manifest = 0.3.13's but the version;
SP the base roll EXECUTED on the real classes: the natural check (skill:fn:placed FALSE = natural; TRUE / null / missing / throwing = never),
trunk ids only, the rate over 200 000 rolls at 10 % (the default) and 2.5 % within 5 sigma, 0 % never, 100 % always, a placed position never over
20 000 rolls, the perk stacking (two independent rolls: perk 10 % + base 10 % = 0.20 sap a log, both at once ~1 %), the Collections credit
(coll:fn:add {UUID, Ingredient_Tree_Sap, 1, skills:felled, profile key}; missing / throwing / refusing = no throw), the config row + apply
(default 10, decimals, clamps 0-100, junk = default), the default file line, static: run() and felled() both call sapBase after the Sap
Tapper roll, sapBase = sapBaseRoll -> giveItem + sapCredit; SkyyCollections (SET script) accepts skills:felled by default;
RP every 0.3.11 replant scenario on the 0.3.14 jar; ST start twice on a scratch copy of the live Skyy_SkyyTrees (= 0.3.13's start);
Z the engine-access audit.
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.3.14", "0.3.13"
PKG = "com.skyy.trees."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "trees0314", "tr")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyTrees-%s.jar" % PREV_VERSION)))
_saved = list(sys.argv)
sys.argv = [sys.argv[0], "--dir", SCRATCH, "--jar", JAR, "--prev", PREV_JAR]
_spec = importlib.util.spec_from_file_location("test_skyytrees_0_3_13", os.path.join(HERE, "test_skyytrees_0.3.13.py"))
T313 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T313)
sys.argv = _saved
T313.SCRATCH, T313.JAR, T313.PREV_JAR = SCRATCH, JAR, PREV_JAR
T311 = T313.T311
T311.SCRATCH, T311.JAR, T311.PREV_JAR = SCRATCH, JAR, PREV_JAR
T310 = T313.T310
T310.SCRATCH, T310.JAR, T310.PREV_JAR = SCRATCH, JAR, PREV_JAR
LIVE = T310.LIVE
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


# ============================================================================================================ child: SP (the base sap)
def run_sp(out):
    from jpype import JClass, JImplements, JOverride, JString, JBoolean
    import skyybuild as B
    import harness_kit as HK
    import perfworld_kit as PW
    import soundpass_kit as SK
    HK.jvm([B.SERVER_JAR, JAR, B.JAVASSIST], verify=True)
    R = {"checks": [], "notes": []}

    def ck(c, w):
        R["checks"].append([bool(c), w])
        if not c:
            print("FAIL", w)
    T = lambda n: JClass(PKG + n)
    Gat, Cfg, Store = T("TreeGather"), T("TreeCfg"), T("TreeStore")
    UUID, P = JClass("java.util.UUID"), JClass("java.util.Properties")
    TRUE, FALSE = JClass("java.lang.Boolean").TRUE, JClass("java.lang.Boolean").FALSE
    br = Store.bridge()

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f
            self.calls = []

        @JOverride
        def apply(self, a):
            self.calls.append([str(x) for x in a])
            return self.f(a)
    # ---- the config row + apply
    rows = SK.kit_rows(T("CfgRows"))
    row = rows.get("trees.sapBaseChance", [None] * 11)
    ck(row[1:10] == ["Base Tree Sap chance", "abilities", "dec", "10", "0", "100", "", "%", "live"] and "Collections" in str(row[10]) and "Sap Tapper" in str(row[10]),
       "SP Server Setup -> Trees -> Abilities: Base Tree Sap chance (dec, 10 %%, 0-100, live; help names Collections + Sap Tapper): %s" % (row,))
    Cfg.apply(P())
    ck(abs(float(Cfg.SAP_BASE) - 0.10) < 1e-12, "SP a file without the line = 10 %% (got %s)" % float(Cfg.SAP_BASE))
    for txt, want in (("2.5", 0.025), ("0", 0.0), ("100", 1.0), ("250", 1.0), ("-3", 0.0), ("abc", 0.10), ("NaN", 0.10), (" 7 ", 0.07)):
        p_ = P()
        p_.setProperty("trees.sapBaseChance", txt)
        Cfg.apply(p_)
        ck(abs(float(Cfg.SAP_BASE) - want) < 1e-12, "SP trees.sapBaseChance=%r -> %s (got %s)" % (txt, want, float(Cfg.SAP_BASE)))
    ck("trees.sapBaseChance=10" in str(Cfg.DEFAULTS), "SP a fresh trees.properties lists trees.sapBaseChance=10")
    Cfg.apply(P())
    # ---- the natural check (SkyySkills' skill:fn:placed)
    W = "skyy-island-test"
    placed = set([(1, 64, 1)])
    answer = ["track"]

    def pf(a):
        if answer[0] == "null":
            return None
        if answer[0] == "throw":
            return 1 / 0
        return TRUE if (int(a[1]), int(a[2]), int(a[3])) in placed else FALSE
    pfn = Fn(pf)
    br.remove("skill:fn:placed")
    ck(not bool(Gat.sapBaseOk(W, 5, 64, 5, "Wood_Oak_Trunk")), "SP no SkyySkills (no skill:fn:placed) = no base sap (safe side)")
    br.put("skill:fn:placed", pfn)
    ck(bool(Gat.sapBaseOk(W, 5, 64, 5, "Wood_Oak_Trunk")), "SP a natural log (placed tracker says FALSE) qualifies")
    ck(pfn.calls and pfn.calls[-1] == [W, "5", "64", "5"], "SP skill:fn:placed asked with {world, x, y, z}: %s" % pfn.calls[-1:])
    ck(not bool(Gat.sapBaseOk(W, 1, 64, 1, "Wood_Oak_Trunk")), "SP a PLAYER-PLACED log (tracker TRUE) never")
    answer[0] = "null"
    ck(not bool(Gat.sapBaseOk(W, 5, 64, 5, "Wood_Oak_Trunk")), "SP tracker unknown (null: ignorePlaced=false) = never")
    answer[0] = "throw"
    ck(not bool(Gat.sapBaseOk(W, 5, 64, 5, "Wood_Oak_Trunk")), "SP a throwing tracker = never, no throw")
    answer[0] = "track"
    for id_, want in (("Wood_Oak_Trunk", True), ("Wood_Birch_Trunk_Full", True), ("Wood_Fir_Trunk", True), ("Wood_Oak_Planks", False),
                      ("Wood_Oak_Branch_Long", False), ("Plant_Leaves_Oak", False), ("Rock_Stone", False), (None, False)):
        ck(bool(Gat.sapBaseOk(W, 5, 64, 5, id_)) == want, "SP block %s -> %s" % (id_, want))
    ck(not bool(Gat.sapBaseOk(None, 5, 64, 5, "Wood_Oak_Trunk")), "SP no world name = never")
    # ---- the rate (the real ThreadLocalRandom roll)
    N = 200000
    for pct in (0.10, 0.025):
        Cfg.SAP_BASE = pct
        hits = sum(1 for _ in range(N) if Gat.sapBaseRoll(W, 5, 64, 5, "Wood_Oak_Trunk"))
        sd = (pct * (1 - pct) / N) ** 0.5
        ck(abs(hits / N - pct) <= 5 * sd, "SP rate at %.1f %%: %d / %d = %.4f (tolerance +-%.4f)" % (pct * 100, hits, N, hits / N, 5 * sd))
        R["notes"].append("rate %.3f -> %.5f over %d rolls" % (pct, hits / N, N))
    Cfg.SAP_BASE = 0.10
    ck(sum(1 for _ in range(20000) if Gat.sapBaseRoll(W, 1, 64, 1, "Wood_Oak_Trunk")) == 0, "SP a placed log over 20 000 rolls at 10 %: never")
    Cfg.SAP_BASE = 0.0
    ck(sum(1 for _ in range(20000) if Gat.sapBaseRoll(W, 5, 64, 5, "Wood_Oak_Trunk")) == 0, "SP 0 %: never (off)")
    Cfg.SAP_BASE = 1.0
    ck(sum(1 for _ in range(2000) if Gat.sapBaseRoll(W, 5, 64, 5, "Wood_Oak_Trunk")) == 2000, "SP 100 %: every natural log")
    # ---- the perk stacks: run() / felled() roll Sap Tapper (v[FSap]) and then the base - two independent rolls on the same log
    Cfg.SAP_BASE = 0.10
    tot = both = 0
    for _ in range(N):
        a_ = bool(Gat.roll(0.10))
        b_ = bool(Gat.sapBaseRoll(W, 5, 64, 5, "Wood_Oak_Trunk"))
        tot += int(a_) + int(b_)
        both += int(a_ and b_)
    sd2 = (2 * 0.09 / N) ** 0.5
    ck(abs(tot / N - 0.20) <= 5 * sd2, "SP perk 10 %% (Sap Tapper max) + base 10 %% = %.4f sap a log (0.20 expected)" % (tot / N))
    ck(abs(both / N - 0.01) <= 5 * (0.01 * 0.99 / N) ** 0.5, "SP both on the same log %.4f (0.01 expected: independent)" % (both / N))
    # ---- the Collections credit
    me = UUID(0x5a9, 314)
    br.remove("coll:fn:add")
    ck(not bool(Gat.sapCredit(me)), "SP no SkyyCollections: no credit, no throw")
    cf = Fn(lambda a: TRUE)
    br.put("coll:fn:add", cf)
    ck(bool(Gat.sapCredit(me)) and cf.calls == [[str(me), "Ingredient_Tree_Sap", "1", "skills:felled", str(Store.pkey(me))]],
       "SP coll:fn:add {UUID, Ingredient_Tree_Sap, 1, skills:felled, profile key}: %s" % cf.calls)
    @JImplements("java.util.function.Function")
    class Key(object):                    # profile:fn:key takes the bare UUID
        @JOverride
        def apply(self, u):
            return JString(str(u) + "-p9")
    br.put("profile:fn:key", Key())
    cf.calls[:] = []
    Gat.sapCredit(me)
    ck(cf.calls and cf.calls[0][4] == str(me) + "-p9", "SP the profile key follows profile:fn:key (SkyyCollections refuses after a switch): %s" % cf.calls)
    br.remove("profile:fn:key")
    br.put("coll:fn:add", Fn(lambda a: FALSE))
    ck(not bool(Gat.sapCredit(me)), "SP a refused credit (FALSE) = false, no throw")
    br.put("coll:fn:add", Fn(lambda a: 1 / 0))
    ck(not bool(Gat.sapCredit(me)), "SP a throwing coll:fn:add = false, no throw")
    ck(not bool(Gat.sapCredit(None)), "SP no player = no credit")
    br.remove("coll:fn:add")
    # ---- static: who calls what
    g = PW.calls(JAR)
    run_c, fel_c, sb_c = g.get("TreeGather.run", set()), g.get("TreeGather.felled", set()), g.get("TreeGather.sapBase", set())
    ck(PKG + "TreeGather.sapBase" in run_c and PKG + "TreeGather.sapBase" in fel_c, "STATIC run() (hand / Tree Feller breaks) and felled() (felled logs) both call sapBase")
    ck(set([PKG + "TreeGather.sapBaseRoll", PKG + "TreeGather.giveItem", PKG + "TreeGather.sapCredit"]) <= sb_c,
       "STATIC sapBase = sapBaseRoll -> giveItem (the Sap Tapper delivery) + sapCredit: %s" % sorted(sb_c))
    ck(PKG + "TreeAbil.placed" in g.get("TreeGather.sapBaseOk", set()) and PKG + "TreeCalc.fn" in g.get("TreeGather.sapBaseOk", set()),
       "STATIC sapBaseOk asks SkyySkills' placed tracker through TreeAbil.placed (unknown = placed)")
    callers = sorted(k for k, v in g.items() if PKG + "TreeGather.sapBase" in v)
    ck(callers == ["TreeGather.felled", "TreeGather.run"], "STATIC only run() and felled() give base sap: %s" % callers)
    R["notes"].append("SP %d checks" % len(R["checks"]))
    json.dump(R, open(out, "w"), indent=1)
    sys.stdout.flush()
    os._exit(0)


# ============================================================================================================ parent
def main():
    if "--sp" in sys.argv:
        return run_sp(arg("--out"))
    if "--rp" in sys.argv:
        return T311.run_rp(arg("--out"))
    T = T310.t36()
    if "--load" in sys.argv:
        return T.run_load(arg("--load"), arg("--out"))
    if "--cc" in sys.argv:
        return T.sk().run_cc(arg("--cc"), arg("--prevjar"), arg("--out"), arg("--repl"))
    if "--st" in sys.argv:
        return T.t34().run_start(arg("--st"), arg("--fake"), arg("--live"), arg("--out"), arg("--tag"))
    if "--mkfake" in sys.argv:
        T.t34().t33().H.run_mkfake(arg("--mkfake"))
        return
    if "--audit" in sys.argv:
        H = T.t34().t33().H
        H.SCRATCH = SCRATCH
        H.run_audit(arg("--audit"), arg("--fake"), arg("--out"))
        return
    for j in (JAR, PREV_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    sroot = os.path.realpath(os.path.join(TOOLS, "dev", "scratch"))
    if not os.path.realpath(SCRATCH).startswith(sroot + os.sep):
        sys.exit("--dir must be inside tools/dev/scratch/ (deleted afterwards): %s" % SCRATCH)
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    live_before = T310.snap(LIVE)
    me = os.path.abspath(__file__)

    def child(args_, out_):
        with open(out_ + ".log", "wb") as lf:
            subprocess.run([sys.executable, me] + args_ + ["--out", out_, "--dir", SCRATCH], env=env, stdout=lf, stderr=subprocess.STDOUT, cwd=SCRATCH)
        if not os.path.isfile(out_):
            print(open(out_ + ".log", encoding="utf8", errors="replace").read()[-3000:])
            return None
        return json.load(open(out_))
    try:
        for tag, j in (("new", JAR), ("prev", PREV_JAR)):
            r = child(["--load", j], os.path.join(SCRATCH, "load-%s.json" % tag)) or {}
            check(r and not r.get("load_fails") and r.get("classes", 0) >= 30,
                  "A (%s): %s classes load, verify (-Xverify:all), initialise %s" % (tag, r.get("classes"), r.get("load_fails", [])[:3]))
        rules = [[r"storage\.ChunkGrid\.", "storage.ChunkStore."]]
        cc = child(["--cc", JAR, "--prevjar", PREV_JAR, "--repl", json.dumps({"versions": [VERSION, PREV_VERSION], "rules": rules})],
                   os.path.join(SCRATCH, "cc.json"))
        check(cc is not None, "CC: the compare child ran")
        if cc:
            cls_ = cc["classes"]
            KIT = {"CfgFn", "CfgRows", "CfgPub", "CfgKit", "CfgHist", "CfgImp", "CfgText", "CfgFile"}
            check(not cc["added"] and not cc["gone"], "CC: no class added or removed: %s %s" % (cc["added"], cc["gone"]))
            struct = dict((c, sorted(m.split("(")[0] for m in v["structural"])) for c, v in cls_.items() if v["structural"] and c not in KIT)
            print("CC. 0.3.13 -> 0.3.14 structural: %s" % struct)
            # SkyyTreesPlugin.setup: only its ready line, which names the shared UI kit's version (tools/skyyui.py) - no UI asset changed (JT)
            check(set(struct) <= {"TreeGather", "TreeCfg", "SkyyTreesPlugin"} and struct.get("SkyyTreesPlugin", ["setup"]) == ["setup"],
                  "CC: structural changes only in TreeGather + TreeCfg (+ the ready line in SkyyTreesPlugin.setup): %s" % sorted(struct))
            check(set(struct.get("TreeGather", [])) <= {"felled", "run", "sapBase", "sapBaseOk", "sapBaseRoll", "sapCredit"},
                  "CC: TreeGather changes = run / felled + the 4 new sap methods: %s" % struct.get("TreeGather"))
            newf = dict((c, v["fields_new"]) for c, v in cls_.items() if v["fields_new"])
            print("CC. new fields: %s" % newf)
            check(newf == {"TreeCfg": ["SAP_BASE:D"]}, "CC: the only new field is TreeCfg.SAP_BASE (double): %s" % newf)
            gone = dict((c, v["fields_gone"]) for c, v in cls_.items() if v["fields_gone"])
            check(not gone, "CC: no field removed: %s" % gone)
        zj, zp = zipfile.ZipFile(JAR), zipfile.ZipFile(PREV_JAR)
        nn = set(n for n in zj.namelist() if not n.endswith(".class"))
        np_ = set(n for n in zp.namelist() if not n.endswith(".class"))
        diff = sorted(n for n in (nn | np_) if n != "manifest.json" and (n not in nn or n not in np_ or zj.read(n) != zp.read(n)))
        check(not diff, "JT: every asset is byte for byte 0.3.13's: %s" % diff[:5])
        mn, mp = json.loads(zj.read("manifest.json")), json.loads(zp.read("manifest.json"))
        mnd, mpd = dict(mn), dict(mp)
        mnd.pop("Description", None)
        mpd.pop("Description", None)
        check(json.dumps(mnd, sort_keys=True) == json.dumps(mpd, sort_keys=True).replace(PREV_VERSION, VERSION), "JT: manifest = 0.3.13's but the version (+ description)")
        # SkyyCollections (the SET pin's script, read only): skills:felled is a default source, also for old config files
        cs = os.path.join(ROOT, "SkyyCollections", "build_skyycollections_0.2.16.py")
        ct = open(cs, encoding="utf8").read() if os.path.isfile(cs) else ""
        check('"bridge.add.sources=skills:double,skills:felled,shard"' in ct and "skills:felled is accepted even when missing" in ct,
              "SC: SkyyCollections 0.2.16 accepts coll:fn:add source skills:felled by default (old files too)")
        sp = child(["--sp"], os.path.join(SCRATCH, "sp.json"))
        check(sp is not None, "SP ran")
        if sp:
            for n_ in sp.get("notes", []):
                print("SP. " + n_)
            for ok, what in sp.get("checks", []):
                check(ok, what)
            check(len(sp.get("checks", [])) >= 35, "SP: every base-sap scenario ran (%d checks)" % len(sp.get("checks", [])))
        rp = child(["--rp"], os.path.join(SCRATCH, "rp.json"))
        check(rp is not None, "RP ran")
        if rp:
            for ok, what in rp.get("checks", []):
                check(ok, what)
            check(len(rp.get("checks", [])) >= 65, "RP: every 0.3.11 replant scenario ran on 0.3.14 (%d checks)" % len(rp.get("checks", [])))
        fake = os.path.join(SCRATCH, "fake")
        subprocess.run([sys.executable, me, "--mkfake", fake, "--dir", SCRATCH], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=SCRATCH)
        sts = {}
        for tag, j in (("new", JAR), ("prev", PREV_JAR)):
            sts[tag] = child(["--st", j, "--fake", fake, "--live", LIVE, "--tag", tag], os.path.join(SCRATCH, "st-%s.json" % tag))
            check(sts[tag] is not None and len(sts[tag].get("starts", [])) == 2, "ST (%s): two starts ran" % tag)
        if sts.get("new") and sts.get("prev"):
            T34 = T.t34()
            nz = lambda r: T34.norm_start(r).replace(VERSION, "0.3.X").replace(PREV_VERSION, "0.3.X")
            sn, sp_ = sts["new"]["starts"], sts["prev"]["starts"]
            check(nz(sn[0]) == nz(sp_[0]), "ST: start 1 of 0.3.14 = 0.3.13's (the live file is not rewritten): %s / %s" % (sn[0]["changed"], sp_[0]["changed"]))
            check(sn[1]["changed"] == [] and sn[1]["sum"] == sn[0]["sum"], "ST: start 2 changes nothing and reads the same: %s" % sn[1]["changed"])
            print("ST. start twice on the live copy: start 1 changed %s (same as 0.3.13), start 2 nothing" % sn[0]["changed"])
        au = child(["--audit", JAR, "--fake", fake], os.path.join(SCRATCH, "audit.json"))
        check(au is not None, "Z: the audit child ran")
        if au:
            check(not au.get("refused") and au.get("refs", 0) > 2000, "Z: engine-access audit: %s references, 0 refused: %s" % (au.get("refs"), str(au.get("refused"))[:400]))
            check(len(au.get("control") or []) >= 1, "Z: the audit's control is refused")
            print("Z. %s references, %d refused" % (au.get("refs"), len(au.get("refused") or [])))
        check(T310.snap(LIVE) == live_before, "the live Skyy_SkyyTrees folder was never written (only read + copied)")
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyTrees %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
