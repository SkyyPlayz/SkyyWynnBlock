"""Harness for SkyyShards 0.4.29 (shard clicker follow-ups - tools/shards_0_4_29_patch.py, on top of 0.4.28).
Build first:
    python tools/shards_0_4_29_patch.py && python SkyyShards/build_skyyshards_0.4.29.py
    python SkyyShards/test_skyyshards_0.4.29.py [--keep] [--only label,label] [--dir <scratch>]

  S29  static   the patch re-runs to identical bytes; header / VERSION / ready line / rollback note; no new registerSystem / registerCommand; line
                endings kept; the new Server Setup row click.saplingLogs (label / help lengths, default 16, 1..10000)
  FQ29 costs    EXECUTED Island size Small -> Medium and Medium -> Large on EVERY Foraging island type: own logs (click.saplingLogs per sapling) + the
                Enchanted part, never a sapling; a type without a sapling asks no logs for it; click.saplingLogs is live (and bounded on load);
                a NEW island still asks for its sapling; Orchard (click.orchard.saplingFruit) and Farming (Eternal seeds) Island size unchanged;
                the cost table printed (the report's table)
  FP29 page     EXECUTED on the Foraging clicker page: the Island size row shows have / need lines with logs (no sapling), Island size bought
                (coins + 4 Enchanted Oak + 128 Oak logs exactly, saplings untouched), a double click buys once, too few logs refused (nothing
                paid), a stale profile refused, Medium -> Large 384 logs
  RF29 fortune  EXECUTED the Ranching clicker's Fortune read: 0 with no source; a skill:bonus dd.ranching source (as any future accessory / pet
                / tree / gear would send) gives Fortune > 0 and the tend rolls replay exactly; a skill:fn:fortune that does not answer Ranching
                (SkyySkills 0.4.73: Mining / Foraging / Farming only - checked in its script) falls back to that sum; the survey (no mod in the SET
                writes dd.ranching) re-checked statically
  then 0.4.28's phases (ranch28 .. mig28) and 0.4.27 .. older ones on THIS jar, A verify, C compare, AA audit,
  live29 START TWICE on a scratch copy of the live data (0.4.28's live check: islands / totems / items before = after; second start = no change)
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess, json, re, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK

VERSION = "0.4.29"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "shardfix2", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.28.jar")
GEN = os.path.join(HERE, "build_skyyshards_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyshards_0.4.28.py")
PATCH = os.path.join(ROOT, "tools", "shards_0_4_29_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."

# the 0.4.28 harness (it loads 0.4.27 -> ... older): its version moves to this one in memory
_T28 = open(os.path.join(HERE, "test_skyyshards_0.4.28.py"), encoding="utf8").read()
assert _T28.count('VERSION = "0.4.28"\n') == 1, "the 0.4.28 harness changed"
_T28 = _T28.replace('VERSION = "0.4.28"\n', 'VERSION = "%s"\n' % VERSION)
_argv = list(sys.argv)
T428 = importlib.util.module_from_spec(importlib.util.spec_from_loader("test_skyyshards_0_4_28", loader=None))
T428.__dict__["__file__"] = os.path.join(HERE, "test_skyyshards_0.4.28.py")
exec(compile(_T28, T428.__file__, "exec"), T428.__dict__)
sys.argv[:] = _argv
T427, T426, T425, T424, T423 = T428.T427, T428.T426, T428.T425, T428.T424, T428.T423
T419, T49, T410, T411, T416 = T428.T419, T428.T49, T428.T410, T428.T411, T428.T416
T428.JAR = JAR
T428.SCRATCH = SCRATCH
OWNER = T428.OWNER
MI, FO, FK, RA, OR, CK = 0, 1, 2, 3, 4, 5
T0 = T428.T0
OAK, EOAK, SAP = "Wood_Oak_Trunk", "Skyy_Ench_Oak", "Plant_Sapling_Oak"


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyShards 0.4.29 - build script') and 'VERSION = "0.4.29"\n' in g, "S29 header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S29 no new %r" % w)
    K.check("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.29:" in g, "S29 the ready line names the round")
    K.check("ROLLBACK 0.4.29 -> 0.4.28 alone" in g and "SAVED DATA: none changed" in g, "S29 the rollback + saved-data notes")
    K.check(g.count('("click.saplingLogs", "Foraging: logs instead of a sapling", "clicker", "int", "16", "1", "10000"') == 1
            and g.count('CK_SAPL = intOf(p.getProperty(\\"click.saplingLogs\\"), 16, 1, 10000);') == 1, "S29 the click.saplingLogs row + its load line")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S29 the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S29 line endings kept")
    K.check(os.path.getmtime(GEN) >= os.path.getmtime(PATCH) and os.path.getmtime(jar) >= os.path.getmtime(GEN), "S29 jar newer than the script, the script newer than the patch")
    K.save()


def _grow(Isl, Cfg, kd, t, sz):
    from jpype import JLong
    m = Isl.mats(kd, t, Cfg.MAT_GROW, sz - 2, JLong(1))
    return dict(zip([str(x) for x in m[0]], [int(x) for x in m[1]]))


# ---------------------------------------------------------------------------------------------------------- FQ29: Foraging Island size = own logs
def run_fcosts(out, jar, scratch, _home):
    from jpype import JString, JLong
    K = HK.Child(out)
    L, ou, W_, p, lv, got = T428._env(scratch, K, "fq")
    Isl, Core, Cfg = L["ShIsl"], L["ShCore"], L["ShCfg"]
    K.eq(int(Cfg.CK_SAPL), 16, "FQ click.saplingLogs defaults to 16")
    K.eq(str(Isl.STYLE[FO]), "grove", "FQ the Foraging kind is the grove style")
    rows = []
    nsap_types = 0
    for ci in range(int(Isl.LADN[FO])):
        t = int(Isl.LAD0[FO]) + ci
        nm, prod, es = str(Isl.tname(t)), str(Isl.PROD[t]), str(Isl.ESEED[t])
        eid = str(Isl.tok(FO, t, JString("ench")))
        own = {prod, eid}
        cv = float(Core.tierCv(t))
        cells = []
        for sz, nsap, ne in ((2, 8, 4), (3, 24, 16)):
            g = _grow(Isl, Cfg, FO, t, sz)
            want = {eid: ne * int(Isl.enchX(FO, t, JString("ench")))}
            if es:
                want[prod] = want.get(prod, 0) + nsap * 16
            K.check(g == want and not any(i.startswith("Plant_Sapling_") for i in g) and set(g) <= own,
                    "FQ %s Island size %s = own logs + Enchanted, no sapling: %s (want %s)" % (nm, "SML"[sz - 1], g, want))
            cells.append(" + ".join("%d %s" % (q, i) for i, q in sorted(g.items())) + " + %s coins" % int(Isl.coins(Isl.growH(sz), cv)))
        K.check(bool(Isl.ownSeed(FO, t, JString("eseed"))) == bool(es) and not bool(Isl.ownSeed(FO, t, JString("seed"))) and not bool(Isl.ownSeed(FO, t, JString("ench"))),
                "FQ %s: ownSeed only for its sapling token (eseed)" % nm)
        if es:
            nsap_types += 1
            K.eq(str(Isl.tok(FO, t, JString("eseed"))), prod, "FQ %s: eseed -> its own log %s" % (nm, prod))
            bm = Isl.mats(FO, t, Cfg.BUY_ITEMS[FO], 0, JLong(1))
            K.check(es in [str(x) for x in bm[0]], "FQ %s: a NEW island still asks for its sapling %s (find the tree type first)" % (nm, es))
        rows.append((nm, prod, es or "-", cells[0], cells[1]))
    K.check(nsap_types >= 10, "FQ %d of %d Foraging types had a sapling in Island size (all now logs)" % (nsap_types, int(Isl.LADN[FO])))
    # live + bounded
    t0 = int(Isl.LAD0[FO])
    Cfg.CK_SAPL = 3
    K.eq(_grow(Isl, Cfg, FO, t0, 2).get(OAK), 24, "FQ click.saplingLogs is live (3 x 8 = 24 Oak logs)")
    Cfg.CK_SAPL = 16
    K.eq(int(Cfg.intOf(JString("0"), 16, 1, 10000)), 1, "FQ ... a 0 on load is raised to 1 (the row's min)")
    # the other kinds unchanged
    for ci in range(int(Isl.LADN[OR])):
        t = int(Isl.LAD0[OR]) + ci
        if str(Isl.ESEED[t]):
            K.eq(_grow(Isl, Cfg, OR, t, 2).get(str(Isl.PROD[t]), 0) - (4 * int(Isl.enchX(OR, t, JString("ench"))) if str(Isl.tok(OR, t, JString("ench"))) == str(Isl.PROD[t]) else 0),
                 8 * int(Cfg.OQ_SAPF), "FQ Orchard %s still pays click.orchard.saplingFruit per sapling" % str(Isl.tname(t)))
    Cfg.OQ_SAPF = 5
    t1 = int(Isl.LAD0[OR])
    K.eq(_grow(Isl, Cfg, OR, t1, 2).get(str(Isl.PROD[t1]), 0), 40, "FQ ... Orchard Apple reads click.orchard.saplingFruit, not click.saplingLogs")
    Cfg.OQ_SAPF = 16
    tf = int(Isl.LAD0[FK])
    gf = _grow(Isl, Cfg, FK, tf, 2)
    K.check(gf.get(str(Isl.ESEED[tf])) == 8 and not bool(Isl.ownSeed(FK, tf, JString("eseed"))), "FQ Farming Wheat Island size still asks 8 Eternal seeds (the farm clicker drops them): %s" % gf)
    K.check(not any(bool(Isl.ownSeed(MI, int(Isl.LAD0[MI]) + i, JString("eseed"))) for i in range(int(Isl.LADN[MI]))), "FQ Mining has no sapling swap")
    print("FQ cost table: Foraging type | log | sapling it asked | Small -> Medium | Medium -> Large")
    for r in rows:
        print("FQ  " + " | ".join(r))
    K.notes.append("FQ cost table: " + json.dumps(rows))
    K.save()


# ---------------------------------------------------------------------------------------------------------- FP29: the Foraging page buys Island size with logs
def _fpage(L, ou, W_):
    pg = T427._page(L, ou, W_, FO)
    L["ShClk"].HAND_TEST = "Tool_Hatchet_Copper"
    T49._build(pg)
    return pg


def run_fpage(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = T428._env(scratch, K, "fp")
    St, M, Isl, Cfg = L["ShStore"], L["ShMath"], L["ShIsl"], L["ShCfg"]
    T423._foraging(L, p, size=1, amt=5, irr=5, deco=5)
    L["coins"]["bal"] = 900000000
    Cfg.GM_COLL = 0
    Cfg.GL_COLL = 0
    cs = T427._give(L, [(EOAK, 30), (OAK, 100), (SAP, 40)])
    cnt = lambda i: int(L["count"](cs, i))
    pg = _fpage(L, ou, W_)
    K.check(int(pg.view) == 5 and int(pg.ckSlot) == 0, "FP the Foraging clicker shows the Oak island")
    cl = [str(pg.ckCL[12 + j]) for j in range(3)]
    K.check(cl[0].endswith(" coins") and cl[1].endswith("/ 4 " + str(L["ShTotem"].pretty(EOAK))) and cl[2] == "100 / 128 " + str(L["ShTotem"].pretty(OAK))
            and not any("Sapling" in x for x in cl) and int(pg.ckCG[14]) == 2,
            "FP the Island size row: have / need lines with logs, no sapling, the short log line red: %s" % cl)
    # too few logs: refused, nothing paid
    b0, e0, s0 = L["coins"]["bal"], cnt(EOAK), cnt(SAP)
    r = T427._ev(pg, "ku4:1")
    K.check(p.getProperty("foraging.i0.size") == "1" and L["coins"]["bal"] == b0 and cnt(EOAK) == e0 and cnt(OAK) == 100 and cnt(SAP) == s0,
            "FP 100 of 128 logs: refused, nothing paid (%s)" % r[:90])
    cs[0].addItemStack(L["IS"](OAK, 100))
    pg = _fpage(L, ou, W_)
    K.check(str(pg.ckCL[14]) == "200 / 128 " + str(L["ShTotem"].pretty(OAK)) and int(pg.ckCG[14]) == 1, "FP ... with 200 logs the line turns good: %s" % pg.ckCL[14])
    r = T427._ev(pg, "ku4:1")
    K.check(p.getProperty("foraging.i0.size") == "2" and 200 - cnt(OAK) == 128 and e0 - cnt(EOAK) == 4 and cnt(SAP) == s0 and L["coins"]["bal"] < b0,
            "FP Island size bought: 128 Oak logs + 4 Enchanted Oak + coins, saplings untouched (%s)" % r[:90])
    b1, o1 = L["coins"]["bal"], cnt(OAK)
    r = T427._ev(pg, "ku4:1")
    K.check(p.getProperty("foraging.i0.size") == "2" and L["coins"]["bal"] == b1 and cnt(OAK) == o1, "FP ... a double click buys once (%s)" % r[:70])
    # a stale profile: refused
    St.LOCK.lock()
    try:
        for s_ in ("amt", "irr", "deco"):
            p.setProperty("foraging.i0." + s_, "5")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    cs[0].addItemStack(L["IS"](OAK, 400))
    pg = _fpage(L, ou, W_)
    K.check(str(pg.ckCL[14]).endswith("/ 384 " + str(L["ShTotem"].pretty(OAK))) and str(pg.ckCL[13]).endswith("/ 16 " + str(L["ShTotem"].pretty(EOAK))),
            "FP Medium -> Large: 384 logs + 16 Enchanted Oak (%s / %s)" % (pg.ckCL[13], pg.ckCL[14]))
    k0 = pg.key
    pg.key = "00000000-0000-0000-0000-000000000000-p9"
    o2 = cnt(OAK)
    r = str(pg.act("ku4:2", None, None))
    K.check(r.startswith("=The page is up to date") and p.getProperty("foraging.i0.size") == "2" and cnt(OAK) == o2, "FP a stale profile: refused (%s)" % r[:70])
    pg.key = k0
    r = T427._ev(pg, "ku4:2")
    K.check(p.getProperty("foraging.i0.size") == "3" and o2 - cnt(OAK) == 384 and cnt(SAP) == s0, "FP ... then Large bought: 384 logs (%s)" % r[:80])
    K.save()


# ---------------------------------------------------------------------------------------------------------- RF29: Ranching Fortune read
def run_rfort(out, jar, scratch, _home):
    from jpype import JString, JClass, JLong, JDouble
    K = HK.Child(out)
    L, ou, W_, p, lv, got = T428._env(scratch, K, "rf")
    St, Core, Cfg, Ck, Isl = L["ShStore"], L["ShCore"], L["ShCfg"], L["ShClk"], L["ShIsl"]
    br, PyFn = L["br"], L["PyFn"]
    T428._ranch(L, p)
    Cfg.CK_CPS = 1000
    CHK = T428.CHK
    HM = JClass("java.util.HashMap")
    bk = "skill:bonus:" + str(ou)
    br.remove("skill:fn:fortune")
    br.remove(bk)
    K.eq(float(Ck.fortuneOf(ou, JString("Ranching"), JString(CHK), JString("dd.ranching"), JString("only.ranching"))), 0.0, "RF no source: Ranching Fortune 0")
    # a source sends dd.ranching (fraction: 0.5 = 50 Fortune? no - the clicker reads the summed number as SkyySkills' extras count) + one that does not
    m = HM()
    acc = HM(); acc.put("dd.ranching", JDouble(1.0)); acc.put("dd.farming", JDouble(3.0))
    gear = HM(); gear.put("dd.ranching", JDouble(5.0)); gear.put("only.ranching", JString("Food_Beef_Raw"))
    m.put("accessories", acc); m.put("gear", gear)
    br.put(bk, m)
    f = float(Ck.fortuneOf(ou, JString("Ranching"), JString(CHK), JString("dd.ranching"), JString("only.ranching")))
    K.eq(f, 1.0, "RF a dd.ranching source gives Fortune > 0 (1.0; dd.farming not counted; a gear source only on its only.ranching product)")
    K.eq(float(Ck.fortuneOf(ou, JString("Ranching"), JString("Food_Beef_Raw"), JString("dd.ranching"), JString("only.ranching"))), 6.0, "RF ... the gear source counts on Raw Beef")
    # SkyySkills' skill:fn:fortune does not answer Ranching (null) -> the sum is used
    calls = []

    def fortune(a):
        calls.append(str(a[1]))
        return None if str(a[1]) == "Ranching" else JString("ok|9.0|0.0|1|1")
    br.put("skill:fn:fortune", PyFn(fortune))
    fb0 = int(Ck.FORT_BR.get())
    f2 = float(Ck.fortuneOf(ou, JString("Ranching"), JString(CHK), JString("dd.ranching"), JString("only.ranching")))
    K.check(f2 == 1.0 and calls[-1:] == ["Ranching"] and int(Ck.FORT_BR.get()) == fb0, "RF skill:fn:fortune without a Ranching answer: the dd.ranching sum (%s, %s)" % (f2, calls))
    # the tend click with that Fortune: exactly the replayed rolls (1.0 = one sure extra a roll = x2)
    now = [T0 + 1000]
    Core.NOW_TEST = now[0]
    seed = 4242
    Ck.RND_TEST = JClass("java.util.Random")(JLong(seed))
    d0 = dict(T425._drops(p, 0, "ranching"))
    for _ in range(int(Cfg.RQ_HP)):
        Ck.chop(ou, JString(OWNER), RA, 0, 0, None)
    Ck.RND_TEST = None
    ex = T428._ex(Ck, 0)
    main, base, eq = T428._replay(Ck, seed, 1.0, int(Cfg.RQ_ROLLS), 1, 2, ex, float(Cfg.RQ_EXTRA) / 1000.0)
    d1 = T425._drops(p, 0, "ranching")
    K.check(d1.get(CHK, 0) - d0.get(CHK, 0) == main and main == 2 * base, "RF a tend with Ranching Fortune 1.0: %d Raw Chicken = 2 x %d (replayed)" % (main, base))
    br.remove("skill:fn:fortune")
    br.remove(bk)
    # the survey, statically: SkyySkills (SET pin) answers Mining / Foraging / Farming only; no SET mod writes dd.ranching
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    src = open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf8").read()
    _a = src.index("SET = [")
    pins = dict(re.findall(r'\("(Skyy\w+)", "([\d.]+)"\)', src[_a:src.index("\n]", _a)]))
    sk = open(os.path.join(ROOT, "SkyySkills", "build_skyyskills_%s.py" % pins["SkyySkills"]), encoding="utf8").read()
    K.check("for (int r = 0; r <= {PKG}.SkillDefs.FARMING && r < {PKG}.SkillDefs.N; r++)" in sk and 'CtField.make("public static final int FARMING = 2;"' in sk.replace("'", '"'),
            "RF SkyySkills %s skill:fn:fortune answers rows 0..FARMING only (no Ranching)" % pins["SkyySkills"])
    hits = []
    for mod in ("SkyyGear", "SkyyAccessories", "SkyyPets", "SkyyTrees", "SkyySkills", "SkyyClasses", "SkyyArmory"):
        if mod not in pins:
            continue
        fp = os.path.join(ROOT, mod, "build_%s_%s.py" % (mod.lower(), pins[mod]))
        if os.path.isfile(fp) and re.search(r"dd\.ranching|fortune\.ranching", open(fp, encoding="utf8").read()):
            hits.append(mod)
    K.check(not hits, "RF no SET mod writes a Ranching Fortune (dd.ranching / fortune.ranching): %s" % hits)
    K.save()


EXPECT = {   # 0.4.28 -> 0.4.29 (CfgFile / CfgFn / ShFill / ShStore / the plugin: the "SkyyShards @VERSION@" strings + the ready line + the new row)
    'CfgFile': ['~<clinit>'], 'CfgFn': ['~m opExport'], 'CfgRows': ['~<clinit>', '~m header'], 'CfgRows1': ['~<clinit>'], 'CfgRows2': ['~<clinit>'],
    'ShCfg': ['+f CK_SAPL', '~<clinit>', '~m loadCfg'], 'ShFill': ['~m markFixed'], 'ShIsl': ['~m enchX', '~m ownSeed'], 'ShPage': ['~m actClick'],
    'ShStore': ['~m migrate', '~m migrate2', '~m migrate3', '~m migrate4', '~m save'], 'SkyyShardsPlugin': ['~m setup'],
}


def _compare29(out, jar, old_jar, pkg, expect, added, removed=()):
    """non-class files: only manifest.json changes"""
    with zipfile.ZipFile(jar) as a, zipfile.ZipFile(old_jar) as b:
        na, nb = set(a.namelist()), set(b.namelist())
        new = sorted(n for n in na - nb if not n.endswith(".class"))
        gone = sorted(n for n in nb - na if not n.endswith(".class"))
        assert not new and not gone, "C non-class files added %s / gone %s" % (new[:5], gone[:5])
        chg = sorted(n for n in na & nb if not n.endswith(".class") and a.read(n) != b.read(n))
        assert chg == ["manifest.json"], "C changed non-class files: %s" % chg[:8]
    print("C. every non-class file unchanged; manifest.json changed")
    cp = os.path.join(SCRATCH, "compare-%s.jar" % VERSION)
    os.makedirs(SCRATCH, exist_ok=True)
    with zipfile.ZipFile(jar) as zi, zipfile.ZipFile(old_jar) as zo0, zipfile.ZipFile(cp, "w", zipfile.ZIP_DEFLATED) as zo:
        for n in zi.namelist():
            if n.endswith(".class") or n == "manifest.json":
                zo.writestr(n, zi.read(n))
        for n in zo0.namelist():
            if not n.endswith(".class") and n != "manifest.json":
                zo.writestr(n, zo0.read(n))
    T419._compare(out, cp, old_jar, pkg, expect, added, removed)


PHASES = [("static", run_static), ("fcosts29", run_fcosts), ("fpage29", run_fpage), ("rfort29", run_rfort)] + \
         [x for x in T428.PHASES if x[0] not in ("static", "livemig28")] + [("livemig29", T428.run_live_mig)]


if __name__ == "__main__":
    HK.run_compare = _compare29
    ph = PHASES
    if "--only" in sys.argv and "--phase" not in sys.argv:
        want = set(HK.arg("--only").split(","))
        ph = [x for x in PHASES if x[0] in want]
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=ph, script=__file__, live=(T416.T46.LIVE_SH, "mods/Skyy_SkyyShards"))
