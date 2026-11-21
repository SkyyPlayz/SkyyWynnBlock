"""SkyySkills 0.4.71 - harness for THE READ-ONLY SKILL XP PROGRESS BRIDGE skill:fn:prog (tools/skills_0_4_71_patch.py). Build first:
    python tools/skills_0_4_71_patch.py && python SkyySkills/build_skyyskills_0.4.71.py
    python SkyySkills/test_skyyskills_0.4.71.py [--keep]
Phases (each a fresh child JVM: -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes, 0.4.70's patch still regenerates 0.4.70, line endings kept, 1 class / 0 systems / 0 commands
                 added, skill:fn:prog published once, the jar adds exactly SkillProgFn
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.4.70 -> 0.4.71: exactly the planned members (EXPECT) + SkillProgFn
  PR    EXECUTED SkillProgFn on a real SkillStore: the class line first ("your class"), the 11 skills in the levelsOf order, level / into /
                 need = SkillCap's own numbers (into + the level's start = the total), icon + colour = SkillDefs; MAX level = need 0; no class
                 chosen = no class line; not loaded = null (no file read); not a UUID = null; READ ONLY (the data array and the store unchanged)
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
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "inv7", "sk")]
_cmp0 = HK.run_compare
_eq00 = HK.Child.eq


def _mod(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    a = list(sys.argv)
    s.loader.exec_module(m)
    sys.argv[:] = a
    return m


T70 = _mod(os.path.join(HERE, "test_skyyskills_0.4.70.py"), "test_skyyskills_0_4_70")
HK.run_compare = _cmp0
HK.Child.eq = _eq00
T67, T53 = T70.T67, T70.T53
VERSION = "0.4.71"
PKG = "com.skyy.skills."
GEN = os.path.join(HERE, "build_skyyskills_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyskills_0.4.70.py")
PATCH = os.path.join(TOOLS, "skills_0_4_71_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.70.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = T70.LIVE_DIR
ADDED = ["SkillProgFn"]
EXPECT = {   # the bridge put in setup; every other change = the VERSION text those members embed (the generated script differs from 0.4.70 only in
             # the docstring, VERSION, SkillProgFn and its put - checked in S)
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
    K.check(g.startswith('"""SkyySkills 0.4.71') and g.count('VERSION = "0.4.71"') == 1, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem(")
            and g.count("makeClass(") == o.count("makeClass(") + 1, "S 1 new class, no new command / system")
    K.check(g.count('bridge().put("skill:fn:prog"') == 1 and "prog71, dfn" in g, "S skill:fn:prog published once; SkillProgFn written")
    body = lambda t: t[t.index('"""', 3):]
    gx = body(g)
    i0, i1 = gx.index("# 0.4.71 skill:fn:prog"), gx.rindex('}}""", prog71))') + len('}}""", prog71))') + 1
    gx = (gx[:i0] + gx[i1:]).replace("0.4.71", "0.4.70")
    for ln_ in [l_ + chr(10) for l_ in gx.split(chr(10)) if "SkillProgFn" in l_ and ("makeClass" in l_ or "skill:fn:prog" in l_)]:
        gx = gx.replace(ln_, "", 1)
    gx = gx.replace("sbn, xfn, prog71, dfn,", "sbn, xfn, dfn,")
    K.check(gx == body(o), "S below the docstring the script = 0.4.70 except VERSION + the SkillProgFn block, its class line, its put and the write list")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    for patch, ref in ((PATCH, GEN), (os.path.join(TOOLS, "skills_0_4_70_patch.py"), GEN_OLD)):
        cp = os.path.join(d, os.path.basename(ref))
        p = subprocess.run([sys.executable, patch, "--out", cp], capture_output=True, text=True)
        K.check(p.returncode == 0 and open(cp, "rb").read() == open(ref, "rb").read(), "S %s re-generates its script byte for byte: %s" % (os.path.basename(patch), p.stderr[-300:]))
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    nn, on = set(zn.namelist()), set(zo.namelist())
    K.eq(sorted(nn ^ on), sorted("com/skyy/skills/%s.class" % c for c in ADDED), "S the jar adds exactly SkillProgFn")
    K.eq(sorted(n for n in nn & on if not n.endswith(".class") and zn.read(n) != zo.read(n)), ["manifest.json"], "S changed non-class entries = manifest.json")
    K.save()


def run_pr(out, jar, scratch, _home):
    from jpype import JInt, JLong, JClass, JArray
    K = HK.Child(out)
    J = T67._cls(jar)
    SD, ST, CAP = J("SkillDefs"), J("SkillStore"), J("SkillCap")
    T70._load(J, scratch, "pr")
    br = ST.bridge()
    N = int(SD.N)
    MIN, ARCH, EXP = int(SD.MINING), int(SD.indexOf("Archer")), int(SD.EXPLORATION)
    d = JArray(JClass("long"))(2 * N)
    u = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-000000071000")
    k = str(u)
    ST.DATA.put(k, d)
    br.put("class:fn:allowed", J("SkillAddFn")())   # a Function = SkyyClasses is loaded
    br.put("class:" + k, "Archer")
    d[ARCH] = T70._xp_for(SD, ARCH, 30) + 77
    d[MIN] = T70._xp_for(SD, MIN, 31) + 500
    d[EXP] = 9000000000000
    before = [int(x) for x in d]
    n0 = int(ST.DATA.size())
    fn = J("SkillProgFn")()
    r = fn.apply(u)
    K.check(r is not None, "PR an answer for a loaded profile")
    ls = str(r).split("\n") if r is not None else []
    K.eq(ls[0] if ls else None, "ok|" + str(SD.LABELS[ARCH]), "PR the header names the class skill")
    order = [int(getattr(SD, n)) for n in ORDER]
    K.eq([l_.split("|")[0] for l_ in ls[1:]], [str(SD.LABELS[ARCH])] + [str(SD.LABELS[s]) for s in order], "PR the class first, then the 11 skills in the levelsOf order")

    def chk(line, s, what):
        f = line.split("|")
        t = int(d[s])
        lv, into, need = int(f[1]), int(f[2]), int(f[3])
        K.check(lv == int(CAP.level(k, JInt(s), JLong(t))) and need == int(CAP.need(k, JInt(s), JLong(t))) and (need == 0 or into == int(CAP.into(k, JInt(s), JLong(t))))
                and f[4] == str(SD.ICONS[s]) and f[5] == str(SD.COLORS[s]), "PR %s: level / into / need = SkillCap's numbers, icon + colour = SkillDefs (%s)" % (what, line))
        return lv, into, need
    lv, into, need = chk(ls[1], ARCH, "the class (Archery)")
    K.check(lv == 30 and into == 77 and need > 0, "PR the class: Lv 30, 77 XP into it (%d / %d)" % (into, need))
    lv, into, need = chk(ls[1 + 1 + ORDER.index("MINING")], MIN, "Mining")
    K.check(lv == 31 and into == 500 and need > 500, "PR Mining: Lv 31, 500 into it (%d)" % need)
    lv, into, need = chk(ls[1 + 1 + ORDER.index("EXPLORATION")], EXP, "Exploration at max")
    K.check(need == 0 and into == 0, "PR a MAX level = need 0, into 0 (Lv %d)" % lv)
    K.eq([int(x) for x in d], before, "PR READ ONLY: the data array unchanged")
    K.eq(int(ST.DATA.size()), n0, "PR READ ONLY: no profile loaded or added")
    br.remove("class:" + k)
    r2 = fn.apply(u)
    ls2 = str(r2).split("\n") if r2 is not None else []
    K.check(ls2 and ls2[0] == "ok|" and len(ls2) == 1 + len(ORDER), "PR no class chosen: no class line, the 11 skills (%s)" % (ls2[:1],))
    ST.DATA.remove(k)
    K.check(fn.apply(u) is None and int(ST.DATA.size()) == n0 - 1, "PR not loaded = null, NOTHING loaded (no file read)")
    K.check(fn.apply("not a uuid") is None and fn.apply(None) is None, "PR not a UUID = null")
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
    phases = [("static", run_static), ("pr", run_pr), ("sh", T70.run_sh), ("hl", T70.run_hl), ("pk", T70.run_pk), ("live", run_live)]
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=phases, script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
