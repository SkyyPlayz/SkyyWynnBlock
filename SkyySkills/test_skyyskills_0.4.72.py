"""SkyySkills 0.4.72 - harness for THE READ-ONLY FORTUNE BRIDGE skill:fn:fortune (tools/skills_0_4_72_patch.py). Build first:
    python tools/skills_0_4_72_patch.py && python SkyySkills/build_skyyskills_0.4.72.py
    python SkyySkills/test_skyyskills_0.4.72.py [--keep]
Phases (each a fresh child JVM: -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes, 0.4.71's patch still regenerates 0.4.71, line endings kept, 1 class / 0 systems / 0 commands
                 added, skill:fn:fortune published once, the jar adds exactly SkillFortFn
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.4.71 -> 0.4.72: exactly the planned members (EXPECT) + SkillFortFn
  FO    EXECUTED SkillFortFn on a real SkillStore: total = Perks.fortune(u, row, level, block) for Mining / Foraging (the level perk + a skill:bonus
                 source + the held tool with only.<skill>), level part = Perks.chance, bonus flag = bridge.bonus.enabled (off: the sources drop out),
                 perk.only.<skill> not matching the block = 0 + match 0, skill names in any case; not loaded = null (no file read); bad arguments
                 = null; READ ONLY (the data array, the store and the Fortune counters unchanged)
  PR    the 0.4.71 skill:fn:prog cases on THIS jar (regression)
  SH / HL / PK   the 0.4.70 cases on THIS jar (regression)
  LIVE  start twice on a scratch COPY of the live Skyy_SkyySkills: no file changes at all
  AA    engine-access audit
"""
import os, sys, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "mine1", "sk")]
_cmp0 = HK.run_compare
_eq00 = HK.Child.eq


def _mod(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    a = list(sys.argv)
    s.loader.exec_module(m)
    sys.argv[:] = a
    return m


T71 = _mod(os.path.join(HERE, "test_skyyskills_0.4.71.py"), "test_skyyskills_0_4_71")
HK.run_compare = _cmp0
HK.Child.eq = _eq00
T70 = T71.T70
T67, T53 = T70.T67, T70.T53
VERSION = "0.4.72"
PKG = "com.skyy.skills."
GEN = os.path.join(HERE, "build_skyyskills_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyskills_0.4.71.py")
PATCH = os.path.join(TOOLS, "skills_0_4_72_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.71.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = T70.LIVE_DIR
ADDED = ["SkillFortFn"]
EXPECT = {   # the bridge put in setup; every other change = the VERSION text those members embed (the generated script differs from 0.4.71 only in
             # the docstring, VERSION, SkillFortFn and its put - checked in S)
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'CurveP9Mig': ['~m run'],
    'ManaGuard': ['~m armReport2', '~m intReport', '~m packReport'],
    'SkillCfg': ['~m load'],
    'SkyySkillsPlugin': ['~m setup'],
}
ORDER = ["MINING", "FORAGING", "FARMING", "ACROBATICS", "ALCHEMY", "SMITHING", "COOKING", "EXPLORATION", "FISHING", "RANCHING", "ORCHARD"]


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read().replace("\r\n", "\n")
    o = open(GEN_OLD, encoding="utf8", newline="").read().replace("\r\n", "\n")
    K.check(g.startswith('"""SkyySkills 0.4.72') and g.count('VERSION = "0.4.72"') == 1, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem(")
            and g.count("makeClass(") == o.count("makeClass(") + 1, "S 1 new class, no new command / system")
    K.check(g.count('bridge().put("skill:fn:fortune"') == 1 and "prog71, fort72, dfn" in g, "S skill:fn:fortune published once; SkillFortFn written")
    body = lambda t: t[t.index('"""', 3):]
    gx = body(g)
    i0, i1 = gx.index("# 0.4.72 skill:fn:fortune"), gx.rindex('}}""", fort72))') + len('}}""", fort72))') + 1
    gx = (gx[:i0] + gx[i1:]).replace('VERSION = "0.4.72"', 'VERSION = "0.4.71"')
    for ln_ in [l_ + chr(10) for l_ in gx.split(chr(10)) if "SkillFortFn" in l_ and ("makeClass" in l_ or "skill:fn:fortune" in l_)]:
        gx = gx.replace(ln_, "", 1)
    gx = gx.replace("sbn, xfn, prog71, fort72, dfn,", "sbn, xfn, prog71, dfn,")
    K.check(gx == body(o), "S below the docstring the script = 0.4.71 except VERSION + the SkillFortFn block, its class line, its put and the write list")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    for patch, ref in ((PATCH, GEN), (os.path.join(TOOLS, "skills_0_4_71_patch.py"), GEN_OLD)):
        cp = os.path.join(d, os.path.basename(ref))
        p = subprocess.run([sys.executable, patch, "--out", cp], capture_output=True, text=True)
        K.check(p.returncode == 0 and open(cp, "rb").read() == open(ref, "rb").read(), "S %s re-generates its script byte for byte: %s" % (os.path.basename(patch), p.stderr[-300:]))
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    nn, on = set(zn.namelist()), set(zo.namelist())
    K.eq(sorted(nn ^ on), sorted("com/skyy/skills/%s.class" % c for c in ADDED), "S the jar adds exactly SkillFortFn")
    K.eq(sorted(n for n in nn & on if not n.endswith(".class") and zn.read(n) != zo.read(n)), ["manifest.json"], "S changed non-class entries = manifest.json")
    K.save()


def run_fo(out, jar, scratch, _home):
    from jpype import JInt, JClass, JArray, JString
    K = HK.Child(out)
    J = T67._cls(jar)
    SD, ST, PK, BC = J("SkillDefs"), J("SkillStore"), J("Perks"), J("BridgeCfg")
    T70._load(J, scratch, "fo")
    br = ST.bridge()
    N = int(SD.N)
    MIN, FOR = int(SD.MINING), int(SD.FORAGING)
    d = JArray(JClass("long"))(2 * N)
    u = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-000000072000")
    k = str(u)
    ST.DATA.put(k, d)
    d[MIN] = T70._xp_for(SD, MIN, 40) + 5
    d[FOR] = T70._xp_for(SD, FOR, 25) + 5
    before = [int(x) for x in d]
    n0 = int(ST.DATA.size())
    fn0 = [int(x) for x in PK.FN]
    fn = J("SkillFortFn")()
    Obj = JClass("java.lang.Object")
    Dbl = JClass("java.lang.Double")

    def ask(skill, fam):
        a = JArray(Obj)(3)
        a[0] = u
        a[1] = JString(skill)
        a[2] = JString(fam) if fam is not None else None
        r = fn.apply(a)
        return None if r is None else str(r)

    def parse(r):
        f = r.split("|")
        return f[0], float(f[1]), float(f[2]), f[3], f[4]

    def pf(row, lv, fam):
        return float(PK.fortune(u, JInt(row), JInt(lv), JString(fam)))

    # 1. the level perk only (no skill:bonus): total = Perks.fortune
    r = ask("Mining", "Ore_Copper_Stone")
    K.check(r is not None and r.startswith("ok|"), "FO an answer for a loaded profile (%s)" % r)
    ok, tot, lvp, bon, mt = parse(r)
    lvl = int(PK.rowLevel(u, JInt(MIN)))
    K.check(lvl == 40, "FO Mining level 40 read (%d)" % lvl)
    K.check(abs(lvp - float(PK.chance(JInt(MIN), JInt(lvl)))) < 1e-12 and lvp > 0.0, "FO the level part = Perks.chance (%s)" % lvp)
    K.check(abs(tot - pf(MIN, lvl, "Ore_Copper_Stone")) < 1e-12, "FO the total = Perks.fortune (%s)" % tot)
    K.check(bon == "1" and mt == "1", "FO bonus flag on, the block matches (%s %s)" % (bon, mt))
    # 2. a skill:bonus source (trees) + a held pickaxe limited to ore blocks (SkyyGear's only.mining)
    src = JClass("java.util.HashMap")()
    t1 = JClass("java.util.HashMap")()
    t1.put("dd.mining", Dbl(0.75))
    t1.put("dd.foraging", Dbl(0.5))
    g1 = JClass("java.util.HashMap")()
    g1.put("dd.mining", Dbl(1.25))
    g1.put("only.mining", JString("Ore_"))
    src.put("trees", t1)
    src.put("gear", g1)
    br.put("skill:bonus:" + k, src)
    ok, tot2, lvp2, bon2, mt2 = parse(ask("mining", "Ore_Copper_Stone"))
    want = pf(MIN, lvl, "Ore_Copper_Stone")
    K.check(abs(tot2 - want) < 1e-12 and tot2 >= tot + 0.75 + 1.25 - 1e-9, "FO + the tree source + the held pickaxe on an ore: %s (= Perks.fortune %s)" % (tot2, want))
    ok, tot3, _l3, _b3, mt3 = parse(ask("MINING", "Rock_Stone"))
    K.check(abs(tot3 - pf(MIN, lvl, "Rock_Stone")) < 1e-12 and tot3 < tot2 - 1.0, "FO the tool's only.mining does not name stone: its part drops out (%s < %s)" % (tot3, tot2))
    ok, tf, lf, bf, mf = parse(ask("Foraging", "Wood_Oak_Trunk"))
    lvlf = int(PK.rowLevel(u, JInt(FOR)))
    K.check(abs(tf - pf(FOR, lvlf, "Wood_Oak_Trunk")) < 1e-12 and tf >= 0.5 and mf == "1", "FO Foraging on an oak log = Perks.fortune (%s)" % tf)
    # 3. perk.only.foraging ("_Trunk", the default) does not name a plank: no extra drops in the world either
    ok, tp, lp, bp_, mp = parse(ask("Foraging", "Wood_Oak_Planks"))
    K.check(tp == 0.0 and mp == "0" and lp > 0.0, "FO a block perk.only.foraging does not name: total 0, match 0, the level part still shown (%s %s %s)" % (tp, mp, lp))
    # 4. bridge.bonus.enabled off: the sources drop out, the flag says so
    BC.BONUS = False
    ok, tb, lb, bb, mb = parse(ask("Mining", "Ore_Copper_Stone"))
    K.check(bb == "0" and abs(tb - pf(MIN, lvl, "Ore_Copper_Stone")) < 1e-12 and tb < tot2, "FO bridge.bonus.enabled off: flag 0, the sources drop out (%s)" % tb)
    BC.BONUS = True
    # 5. wrong arguments / not loaded
    K.check(ask("Fishing", "x") is None and ask("Nope", "x") is None, "FO a skill without Fortune rows = null")
    K.check(fn.apply(u) is None and fn.apply(None) is None and fn.apply(JString("x")) is None, "FO not an Object[] = null")
    a2 = JArray(Obj)(2)
    a2[0] = u
    a2[1] = JString("Mining")
    r2 = fn.apply(a2)
    K.check(r2 is not None and str(r2).startswith("ok|"), "FO no block id = the no-filter rule (%s)" % r2)
    a3 = JArray(Obj)(3)
    a3[0] = u
    a3[1] = JString("Mining")
    a3[2] = JClass("java.lang.Integer")(5)
    K.check(fn.apply(a3) is None, "FO a non-String block = null")
    K.eq([int(x) for x in d], before, "FO READ ONLY: the data array unchanged")
    K.eq(int(ST.DATA.size()), n0, "FO READ ONLY: no profile loaded or added")
    K.eq([int(x) for x in PK.FN], fn0, "FO READ ONLY: the Fortune roll counters unchanged")
    br.remove("skill:bonus:" + k)
    ST.DATA.remove(k)
    K.check(ask("Mining", "Ore_Copper_Stone") is None and int(ST.DATA.size()) == n0 - 1, "FO not loaded = null, NOTHING loaded (no file read)")
    K.save()


def run_live(out, jar, scratch, home):
    K = HK.Child(out)
    J = T67._cls(jar)
    s0 = T53.snapd(home)
    T67._start(J, home)
    s1 = T53.snapd(home)
    K.eq(sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k)), [], "LIVE start 1: nothing written")
    T67._start(J, home)
    K.check(T53.snapd(home) == s1, "LIVE start 2 changes nothing")
    K.save()


if __name__ == "__main__":
    phases = [("static", run_static), ("fo", run_fo), ("pr", T71.run_pr), ("sh", T70.run_sh), ("hl", T70.run_hl), ("pk", T70.run_pk), ("live", run_live)]
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=phases, script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
