"""Harness for SkyyGear 0.3.30 (tools/gear_0_3_30_patch.py header = half-tier ores at full speed, no Bronze armor in the bags)
    python tools/gear_0_3_30_patch.py && python SkyyGear/build_skyygear_0.3.30.py
    python SkyyGear/test_skyygear_0.3.30.py [--keep]          (S330 + H329 + H330 on one booted engine)
    python SkyyGear/test_skyygear_0.3.30.py --static [--keep]  (no jar)

  The 0.3.29 harness is loaded as a library (its engine boot + its H329 phase, which still holds on this jar: 0.3.30 changes no band, set,
  multitool or 0.3.29 migration behaviour); H330 runs right after it on the same booted engine.
  STATIC (--static)
       G  the patch run TWICE in a scratch tree -> byte-identical, = SkyyGear/build_skyygear_0.3.30.py, compiles, line endings kept
       A  anchors: VERSION; no new system / command / class; h30Update / h30Log / migrate0330 after h7Old and migrate0329; the popup guard;
          bzOut in GearPool.table; the Server Setup row (default 1, new label); the fresh-file marker
  S330 the jar 0.3.29 -> 0.3.30: no entry added or removed; only class files + the manifest change
  H330 (the h319 child) - real code:
       A  gate.halfFactor: the fresh file 1, GearCfg.GATE_HALF 1.0, slowF(4) 1.0 (one up 0.4 / two up 0.1 unchanged); a live edit 0.5 -> slowF(4) 0.5
       B  GearLL.oreI: Copper (T1) on Iron ore = code 4 (half tier), Copper on Lead = slow (not 4); GearLL.hit's guard returns 4 with no slow count
       C  bag pool: GearPool.bzOut on every Armor_Bronze_* id, never on Steel / Heavy Leather; the build-time pool still has a Heavy piece per slot
       D  migrate0330: h30Update on a 0.3.29-shaped file (CRLF): gate.halfFactor 0.5 -> 1 in place, marker at the END, one change-log row,
          a second run = null; a hand-set 1.0 kept with no note and no row; a hand-set 0.75 kept + noted; LF stays LF; a file without the row
          only gets the marker
       L  LIVE DATA: a scratch COPY of the test world's config.properties (UserData read only) through h30Update - a second run is a no-op
Scratch: tools/dev/scratch/g330/h330 (deleted at the end unless --keep). Exit code 1 on any failure (--static: 0 = PASS).
"""
import os, sys, shutil, zipfile, re, subprocess, atexit

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
STATIC = "--static" in sys.argv
if STATIC:
    sys.dont_write_bytecode = True


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


VERSION = "0.3.30"
V329 = "0.3.29"
SCR_BASE = os.path.join(TOOLS, "dev", "scratch", "g330", "h330")
SCR_ROOT = os.path.abspath(arg("--root", os.path.join(SCR_BASE, "gear")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
J329 = os.path.abspath(os.path.join(HERE, "SkyyGear-%s.jar" % V329))                       # read only
PKG = "com.skyy.gear."
PATCH = os.path.join(TOOLS, "gear_0_3_30_patch.py")
GEN = os.path.join(HERE, "build_skyygear_0.3.30.py")
GEN329 = os.path.join(HERE, "build_skyygear_0.3.29.py")
LIVE_DIR = os.path.join(SCR_BASE, "live")

if not STATIC:
    _H329 = os.path.join(HERE, "test_skyygear_0.3.29.py")
    _T329 = open(_H329, encoding="utf-8").read()
    _T329 = _T329[:_T329.rindex('if __name__ == "__main__":')]
    _argv = sys.argv
    sys.argv = [_H329, "--jar", JAR, "--root", SCR_ROOT, "--dir", SCRATCH] + [a for a in _argv[1:] if a in ("--keep", "--h319")] + \
        (["--out", arg("--out")] if arg("--out") else [])
    H329 = {"__name__": "skyygear_h329", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
    exec(compile(_T329, _H329 + " (library, 0.3.30)", "exec"), H329)
    sys.argv = _argv
    H328 = H329["H328"]
    H319, H320, H316 = H329["H319"], H329["H320"], H329["H316"]
    for _h in (H329, H328, H328["H327"], H328["H326"], H328["H325"], H320, H319):
        _h["VERSION"] = VERSION
    FAILS, OKS = H316["FAILS"], H316["OKS"]
else:
    FAILS, OKS = [], [0]


def check(cond, what):
    if STATIC:
        if cond:
            OKS[0] += 1
        else:
            FAILS.append(what)
            print("FAIL", what)
        return
    H316["check"](cond, what)


def entries(j):
    z = zipfile.ZipFile(j)
    return dict((n, z.read(n)) for n in z.namelist())


# ====================================================================================================== S330 (the parent, no engine)
def run_assets330():
    ea, eb = entries(J329), entries(JAR)
    check(sorted(ea) == sorted(eb), "S330: 0.3.29 -> 0.3.30 adds / removes no entry: + %s - %s" % (sorted(set(eb) - set(ea))[:4], sorted(set(ea) - set(eb))[:4]))
    diff = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n])
    other = [n for n in diff if not n.endswith(".class") and n != "manifest.json"]
    check(not other, "S330: only class files + the manifest change (%d changed): other %s" % (len(diff), other[:6]))


# ====================================================================================================== H330 (the h319 child, real code)
def _h330(L, K):
    from jpype import JClass, JString, JInt
    P = lambda n: JClass(PKG + n)
    Cfg, apply = L["Cfg"], L["apply"]
    LL, Pool = P("GearLL"), P("GearPool")
    Props, SR = JClass("java.util.Properties"), JClass("java.io.StringReader")

    def kc(cond, what):
        K.check(bool(cond), "H330 " + what)
    apply()
    fresh = str(Cfg.defaultsText())
    pf = Props()
    pf.load(SR(fresh))
    # ============================================================== A: gate.halfFactor
    sf = [float(LL.slowF(JInt(q))) for q in (0, 1, 3, 4)]
    kc(str(pf.getProperty("gate.halfFactor")) == "1" and float(Cfg.GATE_HALF) == 1.0 and sf == [1.0, 0.4, 0.1, 1.0],
       "A: the fresh file gate.halfFactor=1, GATE_HALF 1.0, slowF 0/1/3/4 = %s" % sf)
    apply(gate__halfFactor="0.5")
    s5 = float(LL.slowF(JInt(4)))
    apply()
    kc(s5 == 0.5 and float(LL.slowF(JInt(4))) == 1.0, "A: a live gate.halfFactor=0.5 edit slows the half tier again (%s), back to 1.0" % s5)
    # ============================================================== B: the half tier decision (Copper pickaxe on Iron = code 4; Lead = slow)
    mi, ml = int(LL.oreM("Iron")), int(LL.oreM("Lead"))
    di = [int(x) for x in LL.decideI("Tool_Pickaxe_Copper", JInt(1), JInt(mi))]
    dl = [int(x) for x in LL.decideI("Tool_Pickaxe_Copper", JInt(1), JInt(ml))]
    kc(mi // 100 == 2 and mi % 100 == 1 and di[0] == 1 and di[8] == 4 and dl[0] == 1 and dl[8] in (1, 3),
       "B: Copper (T1) on Iron (normal T2, half T1) = the half tier (code 4, now full speed); on Lead it stays slow: %s / %s (m %d / %d)" % (di, dl, mi, ml))
    # (GearLL.hit needs a real block type; its full-speed guard is checked statically - STATIC A)
    # ============================================================== C: the bag pool
    ids = ["Armor_Bronze_Ornate_Head", "Armor_Bronze_Ornate_Chest", "Armor_Bronze_Ornate_Hands", "Armor_Bronze_Head", "Armor_Bronze_Legs"]
    keep = ["Armor_Steel_Head", "Armor_Leather_Heavy_Chest", "Armor_Iron_Head", "Weapon_Sword_Bronze"]
    kc(all(bool(Pool.bzOut(i)) for i in ids) and not any(bool(Pool.bzOut(i)) for i in keep) and not bool(Pool.bzOut(None)),
       "C: GearPool.bzOut = every Armor_Bronze_* id (Ornate + plain), never Steel / Heavy Leather / Iron / a Bronze sword")
    pid = [str(x) for x in Pool.P_ID]
    kc(all(i in pid for i in ids[:3]), "C: the Ornate pieces stay in the build table (P_ID unchanged; only never a candidate)")
    # ============================================================== D: migrate0330
    m = str(Cfg.H30_MARK)
    fl = fresh.split("\n")
    kc(fl.count(m) == 1 and [str(x) for x in Cfg.H30_KEYS] == ["gate.halfFactor"] and [str(x) for x in Cfg.H30_OLD] == ["0.5"] and [str(x) for x in Cfg.H30_NEW] == ["1"],
       "D: the fresh file carries the marker once; keys / old / new")
    o29 = [x for x in fl if x != m]
    o29 = [("gate.halfFactor=0.5" if x.startswith("gate.halfFactor=") else x) for x in o29]
    t29 = "\r\n".join(o29)
    r = Cfg.h30Update(JString(t29))
    nt = str(r[0]) if r is not None else ""
    rows = [str(x) for x in r[3]] if r is not None else []
    pn = Props()
    pn.load(SR(nt))
    nl = nt.split("\r\n")
    dif = [(a_, b_) for a_, b_ in zip(o29, nl) if a_ != b_ and a_.strip()]
    kc(r is not None and str(pn.getProperty("gate.halfFactor")) == "1" and [x for x in nl if x.strip()][-1] == m and "\n" not in nt.replace("\r\n", "")
       and dif == [("gate.halfFactor=0.5", "gate.halfFactor=1")] and rows == ["gate.halfFactor", "0.5", "1"] and len(nl) == len(o29) + 1,
       "D: h30Update rewrites only gate.halfFactor in place, marker at the END, CRLF kept, one change-log row: %s / %s / %s" % (str(r[1]) if r is not None else None, dif[:3], rows))
    kc(Cfg.h30Update(JString(nt)) is None, "D: a second run = null (run-once marker)")
    r1 = Cfg.h30Update(JString("\n".join(("gate.halfFactor=1.0" if x.startswith("gate.halfFactor=") else x) for x in o29)))
    p1 = Props()
    p1.load(SR(str(r1[0]) if r1 is not None else ""))
    kc(r1 is not None and str(p1.getProperty("gate.halfFactor")) == "1.0" and len(list(r1[2])) == 0 and len(list(r1[3])) == 0 and "\r" not in str(r1[0]),
       "D: a hand-set 1.0 (Server Setup) is kept with no note and no change-log row; LF stays LF")
    r2 = Cfg.h30Update(JString("\n".join(("gate.halfFactor=0.75" if x.startswith("gate.halfFactor=") else x) for x in o29)))
    n2 = [str(x) for x in r2[2]] if r2 is not None else []
    p2 = Props()
    p2.load(SR(str(r2[0]) if r2 is not None else ""))
    kc(r2 is not None and str(p2.getProperty("gate.halfFactor")) == "0.75" and len(n2) == 1 and n2[0].startswith("gate.halfFactor=0.75 kept") and len(list(r2[3])) == 0,
       "D: a hand-set 0.75 is kept + noted: %s" % n2)
    r3 = Cfg.h30Update(JString("\n".join(x for x in o29 if not x.startswith("gate.halfFactor="))))
    kc(r3 is not None and len(list(r3[3])) == 0 and str(r3[1]) == "" and m in str(r3[0]), "D: a file without the row only gets the marker")
    # ============================================================== L: live data (a scratch COPY of the test world's file)
    lf = os.environ.get("SKYY_G330_LIVE")
    if lf and os.path.isfile(lf):
        txt = open(lf, "rb").read().decode("ISO-8859-1")
        t9 = Cfg.h29Update(JString(txt))          # the live file first gets 0.3.29's update (the real start order), then 0.3.30's
        if t9 is not None:
            txt = str(t9[0])
        rl = Cfg.h30Update(JString(txt))
        if rl is None:
            kc(str(Cfg.H30_MARK_ID) in txt, "L: the live copy already carries the 0.3.30 marker")
        else:
            lt = str(rl[0])
            pl = Props()
            pl.load(SR(lt))
            ol, nl_ = txt.split("\n"), lt.split("\n")
            CRLF = chr(13) + chr(10)
            kc(Cfg.h30Update(JString(lt)) is None and ((CRLF in txt) == (CRLF in lt)) and len(nl_) == len(ol) + 1
               and sum(1 for a_, b_ in zip(ol, nl_) if a_ != b_) <= 2 and str(Cfg.H30_MARK_ID) in lt,
               "L: the live copy migrates (gate.halfFactor -> %s) and a second run is a no-op" % pl.getProperty("gate.halfFactor"))
            K.notes.append("H330 live copy: gate.halfFactor -> %s; rows %s; notes %s" % (pl.getProperty("gate.halfFactor"), [str(x) for x in rl[3]], [str(x) for x in rl[2]]))
    else:
        K.notes.append("H330 L: no live config copy (SKYY_G330_LIVE unset) - skipped")
    print("  note (h330): A-D ran")


if not STATIC:
    _H329_PHASE = H319["_h319"]          # the 0.3.29 lib's wrapper (H329 only)

    def _h319_h330(L, K):
        _H329_PHASE(L, K)
        try:
            _h330(L, K)
        except Exception:
            import traceback
            traceback.print_exc()
            K.check(False, "H330: the phase raised: %s" % traceback.format_exc()[-1800:])
    H319["_h319"] = _h319_h330


# ====================================================================================================== STATIC (no jars)
def run_static():
    base = os.path.join(SCR_BASE, "static")
    shutil.rmtree(base, ignore_errors=True)
    outs = []
    try:
        for k in range(2):
            r = os.path.join(base, "run%d" % k)
            os.makedirs(os.path.join(r, "tools"))
            os.makedirs(os.path.join(r, "SkyyGear"))
            shutil.copyfile(PATCH, os.path.join(r, "tools", os.path.basename(PATCH)))
            shutil.copyfile(os.path.join(TOOLS, "deploy_set.py"), os.path.join(r, "tools", "deploy_set.py"))
            shutil.copyfile(GEN329, os.path.join(r, "SkyyGear", os.path.basename(GEN329)))
            p = os.path.join(r, "tools", os.path.basename(PATCH))
            pr = subprocess.run([sys.executable, "-B", "-c",
                                 "import sys\nsys.dont_write_bytecode = True\np = sys.argv[1]\n"
                                 "g = {'__name__': '__main__', '__file__': p}\nexec(compile(open(p, encoding='utf8').read(), p, 'exec'), g)\n", p],
                                capture_output=True, text=True)
            check(pr.returncode == 0, "G: the patch runs in a scratch tree (run %d): %s" % (k, (pr.stderr or "")[-600:]))
            f = os.path.join(r, "SkyyGear", "build_skyygear_0.3.30.py")
            outs.append(open(f, "rb").read() if os.path.isfile(f) else b"")
        check(outs[0] and outs[0] == outs[1], "G: two runs give byte-identical scripts (deterministic)")
        if os.path.isfile(GEN):
            check(outs[0] == open(GEN, "rb").read(), "G: = SkyyGear/build_skyygear_0.3.30.py (the committed file is the patch's output)")
        src = open(GEN329, "rb").read()
        check((b"\r\n" in src) == (b"\r\n" in outs[0]), "G: the source's line endings are kept")
        s = outs[0].decode("utf8").replace("\r\n", "\n")
        try:
            compile(s, "build_skyygear_0.3.30.py", "exec")
            check(True, "G")
        except SyntaxError as e:
            check(False, "G: the generated script compiles: %s" % e)
        s0 = src.decode("utf8").replace("\r\n", "\n")
        check('VERSION = "0.3.30"\n' in s and "GENERATED by tools/gear_0_3_30_patch.py" in s, "A: VERSION 0.3.30 + the GENERATED header")
        check(s.count("registerSystem(") == s0.count("registerSystem(") and s.count("registerCommand(") == s0.count("registerCommand(")
              and s.count(' = mk("') == s0.count(' = mk("'), "A: no new system, command or class")
        i = s.index
        check(i("public static boolean h7Old(") < i("public static Object[] h30Update(") < i("public static String h30Log(") < i("public static synchronized String migrate0330()")
              < i("  @PKG@.GearCfg.migrate0330();") and i("  @PKG@.GearCfg.migrate0329();") < i("  @PKG@.GearCfg.migrate0330();"),
              "A: helpers before their callers; migrate0330 runs after migrate0329")
        g = s[i("public static int hit(@PR@ pr, @IS@ s, @TBTY@ bt) {"):]
        g = g[:g.index('}""")')]
        a_ = g.index("if (d[1] == 1 && d.length > 8) {")
        check(g.index("if (slowF(d[8]) >= 1.0) return d[8];", a_) < g.index('"Slow going", "This ore is above your "', a_) and g.count("slowF(d[8]) >= 1.0") == 1,
              "A: GearLL.hit returns before the ore's Slow going popup when its speed is full")
        t_ = s[i("public static Object[] table() {"):]
        t_ = t_[:t_.index('}""")')]
        check("!bzOut(id)" in t_ and i("public static boolean bzOut(String id)") < i("public static Object[] table() {") and 'BZ_OUT = "Armor_Bronze_"' in s,
              "A: GearPool.table drops every Armor_Bronze_* id (bzOut before table)")
        check('("gate.halfFactor", "Half-tier ore speed", "lifelong", "dec", "1", "0.01", "1",' in s and '("GATE_HALF", "double", "1.0")' in s
              and 'pdec(p, "gate.halfFactor", 1.0, 0.01, 1.0)' in s and "An ore at its half-speed tier breaks at this speed" not in s,
              "A: the Server Setup row (default 1, label, help), GearCfg literal + parse default")
        check('L += ["", G330_HEAD, H30_MARK]' in s and 'H30_OLD = ["0.5"]' in s and 'H30_NEW = ["1"]' in s, "A: the fresh-file marker + the migration values")
        check("loot.exclude" in s and s.count('"loot.exclude"') == s0.count('"loot.exclude"'), "A: loot.exclude untouched")
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCR_BASE, ignore_errors=True)
    print("STATIC %s: %d ok, %d failed" % ("PASS" if not FAILS else "FAIL", OKS[0], len(FAILS)))
    return 0 if not FAILS else 1


# ====================================================================================================== main
def _live_copy():
    """a scratch COPY of the test world's config.properties (UserData is read only)"""
    try:
        import deploy_set
        w = deploy_set.WORLD
    except Exception:
        w = "NewBetaTest"
    src = os.path.join(os.environ.get("APPDATA", ""), "Hytale", "UserData", "Saves", w, "mods", "Skyy_SkyyGear", "config.properties")
    if not os.path.isfile(src):
        print("  note: no live config at %s - H329 / H330 L skipped" % src)
        return
    os.makedirs(LIVE_DIR, exist_ok=True)
    dst = os.path.join(LIVE_DIR, "config.properties")
    shutil.copyfile(src, dst)
    os.environ["SKYY_G330_LIVE"] = dst
    os.environ["SKYY_G329_LIVE"] = dst


def main():
    if STATIC:
        sys.exit(run_static())
    if "--h319" in sys.argv:
        H319["run_h319"](arg("--out"))
        return
    if any(a.startswith("--") and a not in ("--keep", "--dir", "--jar", "--root", "--out", "--only") for a in sys.argv[1:]):
        H320["main"]()          # an older child flag (--mkfake ...) - the chain dispatches it; never the full run again
        return
    assert os.path.isfile(J329) and os.path.isfile(JAR), (J329, JAR)
    if "--keep" not in sys.argv:
        atexit.register(lambda: shutil.rmtree(SCR_BASE, ignore_errors=True))
    run_assets330()
    _live_copy()
    H320["run_fallback"](lambda x: x == "h319", [])


if __name__ == "__main__":
    main()
