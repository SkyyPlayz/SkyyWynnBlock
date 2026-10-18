"""Harness for SkyyMobs 0.1.10 (mob:fn:boss - who is a boss, which zone, who hurt it, for SkyyGear 0.3.19's Mythic bags;
tools/mobs_0_1_10_patch.py). Every 0.1.9 check (run from test_skyymobs_0.1.9.py's own code, which runs 0.1.8's) on the 0.1.10 jar + B10.
Build first: python tools/mobs_0_1_10_patch.py && python SkyyMobs/build_skyymobs_0.1.10.py

    python SkyyMobs/test_skyymobs_0.1.10.py [--keep] [--dir <scratch>]
    python SkyyMobs/test_skyymobs_0.1.10.py --static      (no jars / Assets.zip / server jar: the text checks only)

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.9 -> 0.1.10: MobCfg (+ the boss fields, + tops / bosses / isBoss / bossText, ~ apply, the default file text),
              MobCredit (+ shares, + sharesOf), MobHooks (+ checkZoneTops), the plugin (setup / shutdown: the bridge key + the ready line),
              the kit's version / rows texts; added MobBossFn; non-class: manifest only
  X  exec     every 0.1.9 exec check (+ 0.1.8's), then EXECUTED B10:
              classification: the default Boss roles (Goblin_Duke*, Trork_Chieftain, Dragon_*, Skeleton_Elite*) + the *_Boss* guard (another
              mod's Dungeon_Crypt_Boss), any case; a non-boss -> null; an empty row = no bosses
              zone: the REAL MobLevel.lookupAt band on a stand-in world (bands.default as the band): hi 20 -> 1, 21 -> 2, 75 -> 5, 90 -> 5;
              custom tops; no band -> the NPC's own level (MobLevel.MOBS, world-checked); neither -> 0
              credit: MobCredit.hit x5 -> players top first (a tie keeps the first hitter), shares sum 1, the entry still there after the call
              (read only); npc null -> empty arrays; bad arguments -> null (never throws)
              loader: a config without the boss lines = the defaults; an empty Boss roles; a bad Zone top levels = WARN + the default;
              checkZoneTops; the fresh default file carries both lines
              bridge put (setup) / remove (shutdown) of mob:fn:boss by the class-file bytes
  D  live     the 0.1.8 live check (the live Skyy_SkyyMobs copy loads the same settings with 0.1.9 and 0.1.10, twice; bytes unchanged)
  AA engine-access audit
  --static    (runs alone, before anything else) the generated build_skyymobs_0.1.10.py text: the bridge put + remove, the two rows and
              their defaults / labels / help lengths, the loader + default file lines, no new registerSystem / registerCommand vs 0.1.9,
              the javassist limits on the new Java, methods before callers, the Python mirrors (boss_tops / boss_zone) on the zone ladder,
              and determinism: tools/mobs_0_1_10_patch.py --out <scratch copy> gives identical bytes.
Scratch: tools/dev/scratch/trial-armor-drops/mobs (the jar phases delete it unless --keep; --static only its static/ subfolder). Exit code 1 on any failure.
"""
import os, sys, re, ast, subprocess, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.1.10"
GEN = os.path.join(HERE, "build_skyymobs_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyymobs_0.1.9.py")
PATCH = os.path.join(ROOT, "tools", "mobs_0_1_10_patch.py")
SCRATCH_DEF = os.path.join(ROOT, "tools", "dev", "scratch", "trial-armor-drops", "mobs")


# ================================================================================================================ --static
def HK_arg(name, default=None):
    if name in sys.argv and sys.argv.index(name) + 1 < len(sys.argv):
        return sys.argv[sys.argv.index(name) + 1]
    return default


def java_blocks(text):
    """every M / C / F call's Java text: [(kind, class var, text)]"""
    out = [(m.group(1), m.group(2), m.group(3)) for m in re.finditer(r'\b(M|C|F)\((\w+), r"""(.*?)"""(?=\)|\.replace\(| %)', text, re.S)]
    out += [(m.group(1), m.group(2), ast.literal_eval(m.group(3))) for m in re.finditer(r'\b(M|C|F)\((\w+), ("(?:[^"\\\n]|\\.)*")\)', text)]
    return out


def run_static():
    fails, ok = [], [0]

    def check(c, what):
        if c:
            ok[0] += 1
        else:
            fails.append(what)
            print("FAIL", what)
        return c
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    check(g.startswith('"""SkyyMobs 0.1.10 - build script') and g.count('VERSION = "0.1.10"') == 1 and "0.1.9 (the base," in g,
          "S header + VERSION 0.1.10 (the 0.1.9 notes kept as the base)")
    check(g.count("0.1.10 (2026-10-17) = WHO IS A BOSS") == 1 and "ROLLBACK 0.1.10 -> 0.1.9: safe" in g and "SAVED DATA: none" in g,
          "S the 0.1.10 notes are in the generated docstring (what / Skyy / contract / rows / saved data / rollback)")
    try:
        compile(g, GEN, "exec")
        check(True, "")
    except SyntaxError as e:
        check(False, "S the generated script compiles as Python: %s" % e)
    # bridge put + remove
    su = g[g.index("public void setup() {"):]
    su = su[:su.index('}""")')]
    sd = g[g.index("protected void shutdown() {"):]
    sd = sd[:sd.index('}""")')]
    check(su.count('bridge().put("mob:fn:boss", new @PKG@.MobBossFn());') == 1 and su.index('put("mob:fn:setLevel"') < su.index('put("mob:fn:boss"'),
          "S setup() puts mob:fn:boss (a MobBossFn) after mob:fn:setLevel")
    check(sd.count('bridge().remove("mob:fn:boss");') == 1, "S shutdown() removes mob:fn:boss")
    check("@PKG@.MobCfg.bossText()" in su and g.count('"mob:fn:boss (no bosses)"') == 1, "S the ready line names mob:fn:boss (MobCfg.bossText)")
    # no new system / command
    check(g.count("registerSystem(") == o.count("registerSystem(") and g.count("registerCommand(") == o.count("registerCommand("),
          "S no new registerSystem / registerCommand vs 0.1.9 (%d / %d)" % (g.count("registerSystem("), g.count("registerCommand(")))
    check(g.count("makeClass(") == o.count("makeClass(") + 1 and 'bfn = pool.makeClass(PKG + ".MobBossFn")' in g and ", sfn, bfn]" in g,
          "S exactly one new class (MobBossFn), in ALL")
    # rows: evaluate the two tuples with the literal defaults
    tree = ast.parse(g)
    env = {}
    for n in tree.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and n.targets[0].id in ("BOSSES", "BOSS_TOPS_DEF"):
            env[n.targets[0].id] = ast.literal_eval(n.value)
    for n in tree.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and n.targets[0].id == "BOSS_ROLES_DEF":
            env["BOSS_ROLES_DEF"] = eval(compile(ast.Expression(n.value), GEN, "eval"), {}, dict(env))
    check(env.get("BOSS_ROLES_DEF") == "Goblin_Duke*, Trork_Chieftain, Dragon_*, Skeleton_Elite*, *_Boss*" and env.get("BOSS_TOPS_DEF") == "20 30 45 60 75",
          "S defaults: Boss roles = BOSSES + *_Boss* %r, Zone top levels %r" % (env.get("BOSS_ROLES_DEF"), env.get("BOSS_TOPS_DEF")))
    rows = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Tuple) and len(n.elts) == 12 and isinstance(n.elts[0], ast.Constant) and str(n.elts[0].value).startswith("bosses."):
            rows[n.elts[0].value] = eval(compile(ast.Expression(n), GEN, "eval"), {}, dict(env))
    r1, r2 = rows.get("bosses.roles"), rows.get("bosses.zoneTops")
    check(r1 == ("bosses.roles", "Boss roles", "levels", "text", env.get("BOSS_ROLES_DEF"), "", "2000", "", "", "live",
                 "Boss role ids or Prefix* / *Part* patterns. A boss kill can drop Mythic gear (SkyyGear).", "field:MobCfg.BOSS_ROLES;after=MobCfg.bosses"),
          "S row bosses.roles: %r" % (r1,))
    check(r2 is not None and r2[:10] == ("bosses.zoneTops", "Zone top levels", "levels", "text", "20 30 45 60 75", "", "60", "", "", "live")
          and r2[11] == "field:MobCfg.BOSS_TOPS;after=MobCfg.bosses;check=MobHooks.checkZoneTops", "S row bosses.zoneTops: %r" % (r2,))
    check(all(r is not None and len(r[1]) <= 40 and len(r[10]) <= 100 and "danger" not in r[9] for r in (r1, r2)),
          "S labels <= 40, help <= 100 characters, not danger: %s" % [(len(r[1]), len(r[10])) for r in (r1, r2) if r])
    i_sr = g.index('"reload@%s:scale.role.;check=MobHooks.checkScaleRole" % CFG_FILE),')
    check(i_sr < g.index('("bosses.roles", "Boss roles"') < g.index('("bosses.zoneTops", "Zone top levels"') < g.index('("strength.shape", "Strength shape"'),
          "S the two rows sit on the Which mobs tab after Fixed level by role")
    check('"bosses.roles=" + BOSS_ROLES_DEF,' in g and '"bosses.zoneTops=" + BOSS_TOPS_DEF,' in g
          and g.index('"plate.colors.%s=%s" % (k, v) for k, v in COLOR_ROWS]') < g.index('"bosses.roles=" + BOSS_ROLES_DEF') < g.index('CFG_TEXT = "\\n".join(CFG_LINES)'),
          "S the default file carries both lines (at its end)")
    ap = g[g.index("public static synchronized void apply(java.util.Properties c, java.util.Properties b) {"):]
    ap = ap[:ap.index('}""")')]
    check('BOSS_ROLES = c.getProperty("bosses.roles", BOSS_ROLES_DEF).trim();' in ap and 'BOSS_TOPS = c.getProperty("bosses.zoneTops", BOSS_TOPS_DEF).trim();' in ap
          and ap.index("MAX_LEVEL = intOf(") < ap.index("bosses(null);"),
          "S the loader reads both keys with the default when absent (no update step), after levels.max, then MobCfg.bosses")
    # the new Java: javassist limits + methods before callers
    old_j = set(t for _k, _v, t in java_blocks(o))
    new_j = [(k, v, t) for k, v, t in java_blocks(g) if t not in old_j]
    names = ["%s:%s" % (v, t.strip().split("(")[0].split()[-1]) for k, v, t in new_j if k == "M"]
    check(sorted(names) == sorted(["cfg:tops", "cfg:bosses", "cfg:isBoss", "cfg:bossText", "cfg:apply", "mh:checkZoneTops", "mcr:shares", "mcr:sharesOf", "mcr:read",
                                   "bfn:zoneOf", "bfn:bandHi", "bfn:npcLevel", "bfn:zoneAt", "bfn:answer", "bfn:apply", "pl:setup", "pl:shutdown"]),
          "S the new / changed Java methods: %s" % sorted(names))
    bad = []
    for k, v, t in new_j:
        code = re.sub(r'"(?:[^"\\]|\\.)*"', '""', t)
        code = re.sub(r"'(?:[^'\\]|\\.)'", "''", code)
        code = re.sub(r"//[^\n]*", "", code)
        for what, rx in (("lambda", r"->"), ("generics", r"\b[A-Z]\w*<[A-Z?]\w*[\w\[\], ?]*>"), ("enhanced for", r"for\s*\([^;)]*:[^;)]*\)"),
                         ("try-with-resources", r"\btry\s*\("), ("switch", r"\bswitch\s*\("), ("varargs", r"\.\.\.\s*\w+\s*[,)]"),
                         ("inner class", r"new\s+[\w.]+\s*\([^)]*\)\s*\{")):
            if re.search(rx, code):
                bad.append("%s %s: %s" % (v, t.strip().split("(")[0].split()[-1], what))
    check(not bad, "S the new Java keeps the javassist limits: %s" % bad)
    i = g.index
    check(i("public static int[] tops(String v, int max)") < i("public static void bosses(String key)") < i("public static boolean isBoss(String role)")
          < i("public static synchronized void apply(java.util.Properties c") < i("public static String checkZoneTops(")
          < i("public synchronized Object[] shares()") < i("public static Object[] sharesOf(") < i("public MobBossFn()")
          < i("public static int zoneOf(int lv") < i("public static int bandHi(") < i("public static int npcLevel(") < i("public static int zoneAt(")
          < i("public static Object[] answer(") < i("if (a.length < 6 || !(a[0] instanceof String)") < i("public void setup() {"),
          "S methods before callers (MobCfg -> MobHooks -> MobCredit -> MobBossFn -> the plugin)")
    check(i("public static Object[] at(@WLD@ w") < i("public static int bandHi(") and "@PKG@.MobLevelAtFn.at(w, x, y, z, @PKG@.MobLevelAtFn.onThread(w))" in g
          and "new @PKG@.MobLevelFn().apply(new Object[] { wn, u })" in g and "T.remove" not in g[i("public static Object[] sharesOf("):i("public static void prune(")],
          "S the zone reuses mob:fn:levelAt's core + the mob:fn:level path; the credit list never removes the entry")
    # the Python mirrors (boss_tops / boss_zone) on the ladder, run on their own
    fns = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ("boss_tops", "boss_zone")]
    ns = {"re": re}
    exec(compile(ast.Module(body=fns, type_ignores=[]), GEN, "exec"), ns)
    tops = ns["boss_tops"]("20 30 45 60 75", 100)
    check(tops == [20, 30, 45, 60, 75] and [ns["boss_zone"](h, tops) for h in (20, 21, 75, 90)] == [1, 2, 5, 5]
          and ns["boss_zone"](25, ns["boss_tops"]("10, 50", 100)) == 2 and ns["boss_zone"](0, tops) == 0 and ns["boss_tops"]("30 20", 100) is None,
          "S the Python mirrors: band hi 20 / 21 / 75 / 90 -> zone 1 / 2 / 5 / 5, custom tops, unknown 0, a bad value refused")
    # determinism: the patch again, into a scratch copy
    sc = os.path.join(os.path.abspath(HK_arg("--dir", SCRATCH_DEF)), "static")
    shutil.rmtree(sc, ignore_errors=True)
    os.makedirs(sc)
    try:
        cp = os.path.join(sc, "build_skyymobs_0.1.10.py")
        p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
        check(p.returncode == 0 and "wrote" in p.stdout, "S the patch re-runs: %s %s" % (p.stdout.strip(), p.stderr.strip()[-300:]))
        check(os.path.isfile(cp) and open(cp, "rb").read() == open(GEN, "rb").read(), "S deterministic: the re-run gives identical bytes")
        crlf_old, crlf_new = b"\r\n" in open(GEN_OLD, "rb").read(), b"\r\n" in open(GEN, "rb").read()
        check(crlf_old == crlf_new, "S line endings kept (CRLF %s -> %s)" % (crlf_old, crlf_new))
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(sc, ignore_errors=True)
    print("SkyyMobs %s static checks: %d ok, %d fail(s)" % (VERSION, ok[0], len(fails)))
    for f in fails:
        print("FAIL:", f)
    sys.exit(1 if fails else 0)


if "--static" in sys.argv:
    run_static()

# ================================================================================================================ the jar harness
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", SCRATCH_DEF]
import skyybuild as B
import harness_kit as HK

# the 0.1.9 harness's own phase code (it loads 0.1.8's; its file runs HK.run at the end - executed here without that last call)
_T19 = os.path.join(HERE, "test_skyymobs_0.1.9.py")
_src = open(_T19, encoding="utf-8").read()
_src = _src[:_src.rindex("HK.run(")]
T19 = {"__file__": _T19, "__name__": "test_skyymobs_0_1_9"}
exec(compile(_src, _T19, "exec"), T19)

JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMobs-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMobs-0.1.9.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.mobs."
T19["T18"]["OLD_JAR"] = OLD_JAR   # the 0.1.8 live phase compares the OLD jar (now 0.1.9) with this one
EXPECT = {   # local rebuild 2026-10-17: checked on the real jars (+ the review fix's MobCredit DEAD copy, CfgFile = the kit's fresh file text)
    "MobCfg": ["+f BOSS_ROLES_DEF", "+f BOSS_TOPS_DEF", "+f BOSS_ROLES", "+f BOSS_TOPS", "+f P_BOSS", "+f BOSS_TOP",
               "+m tops", "+m bosses", "+m isBoss", "+m bossText", "~<clinit>", "~m apply", "~m load", "~m reloadAll", "~m useDefaults"],
    "MobCredit": ["+f DEAD", "+f DEAD_MS", "+m shares", "+m sharesOf", "~<clinit>", "~m read"],
    "MobHooks": ["+m checkZoneTops"],
    "SkyyMobsPlugin": ["~m setup", "~m shutdown"],
    "CfgFn": ["~m opExport"],
    "CfgRows": ["~<clinit>", "~m header"],
    "CfgFile": ["~<clinit>"],
}
ADDED = ["MobBossFn"]


def run_exec(out, jar, scratch, home):
    T19["run_exec"](out, jar, scratch, home)        # starts the JVM; every 0.1.9 (+ 0.1.8) exec check
    import json, zipfile
    from jpype import JClass, JArray, JObject, JString, JInt, JDouble
    K = HK.Child(out + ".0110.json")
    Fn, Cfg, Cr, Hk, Lv, Mi = (JClass(PKG + n) for n in ("MobBossFn", "MobCfg", "MobCredit", "MobHooks", "MobLevel", "MobInfo"))
    UUID = JClass("java.util.UUID")
    A = lambda *xs: JArray(JObject)(list(xs))
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)

    def jf(c, n):
        k = c.class_ if hasattr(c, "class_") else c
        while k is not None:
            try:
                f = k.getDeclaredField(n)
                f.setAccessible(True)
                return f
            except Exception:
                k = k.getSuperclass()
        raise KeyError(n)
    WLD = JClass("com.hypixel.hytale.server.core.universe.world.World")
    w = us.allocateInstance(WLD.class_)
    jf(WLD, "name").set(w, "Default")
    Cfg.useDefaults()
    Cfg.ON = True
    Cfg.MAX_LEVEL = 100
    # ---- loader + rows
    K.check("bosses.roles=Goblin_Duke*, Trork_Chieftain, Dragon_*, Skeleton_Elite*, *_Boss*\n" in str(Cfg.DEF_CFG)
            and "bosses.zoneTops=20 30 45 60 75\n" in str(Cfg.DEF_CFG), "B10 LOAD the fresh default file carries both lines")
    K.check(str(Cfg.BOSS_ROLES) == str(Cfg.BOSS_ROLES_DEF) and list(Cfg.BOSS_TOP) == [20, 30, 45, 60, 75], "B10 LOAD defaults after useDefaults")
    pc, pb = Cfg.props(Cfg.DEF_CFG), Cfg.props(Cfg.DEF_BANDS)
    pc.remove("bosses.roles")
    pc.remove("bosses.zoneTops")
    Cfg.apply(pc, pb)
    K.check(str(Cfg.BOSS_ROLES) == str(Cfg.BOSS_ROLES_DEF) and str(Cfg.BOSS_TOPS) == "20 30 45 60 75" and bool(Cfg.isBoss("Goblin_Duke")),
            "B10 LOAD a config without the boss lines = the defaults (no update step)")
    pc.setProperty("bosses.roles", "")
    pc.setProperty("bosses.zoneTops", "30 20")
    Cfg.apply(pc, pb)
    K.check(not bool(Cfg.isBoss("Goblin_Duke")) and Fn().apply(A("Default", None, "Goblin_Duke", JInt(1), JInt(64), JInt(1))) is None,
            "B10 LOAD an empty Boss roles = no bosses (mob:fn:boss null)")
    K.check(str(Cfg.BOSS_TOPS) == "20 30 45 60 75" and list(Cfg.BOSS_TOP) == [20, 30, 45, 60, 75], "B10 LOAD a bad Zone top levels -> WARN + the default")
    Cfg.useDefaults()
    Cfg.ON = True
    K.check(Hk.checkZoneTops("bosses.zoneTops", "20 30 45 60 75") is None and Hk.checkZoneTops("bosses.zoneTops", None) is None
            and Hk.checkZoneTops("bosses.zoneTops", "30 20") is not None and Hk.checkZoneTops("bosses.zoneTops", "20 30 45 60 101") is not None
            and Hk.checkZoneTops("bosses.zoneTops", " ".join(str(10 * i) for i in range(1, 12))) is not None,
            "B10 CHECK Zone top levels: ascending whole numbers 1..levels.max, 1-10 of them")
    # ---- classification
    yes = ["Goblin_Duke", "GOBLIN_DUKE", "Trork_Chieftain", "Dragon_Fire", "Skeleton_Elite_Knight", "Dungeon_Crypt_Boss", "Trork_Boss_Warlord"]
    no = ["Trork_Chieftain_Guard", "Trork_Warrior", "Skeleton_Fighter", "Goblin_Scrapper", "Cow"]
    K.check(all(bool(Cfg.isBoss(n)) for n in yes) and not any(bool(Cfg.isBoss(n)) for n in no), "B10 BOSS the default list + the *_Boss* guard, any case")
    u = UUID.fromString("00000000-0000-4000-8000-000000001010")
    K.check(Fn.answer(w, "Default", u, "Trork_Warrior", 1.0, 64.0, 1.0) is None, "B10 BOSS a non-boss -> null")
    # ---- zone: the REAL lookupAt with bands.default as the band (no generator on a stand-in world)
    got = []
    for hi in (20, 21, 75, 90):
        Cfg.DEF_A, Cfg.DEF_B = 1, hi
        got.append(int(Fn.answer(w, "Default", u, "Goblin_Duke", 10.5, 70.0, -3.2)[0]))
    K.eq(got, [1, 2, 5, 5], "B10 ZONE band hi 20 / 21 / 75 / 90 -> zone")
    Cfg.DEF_A, Cfg.DEF_B = 1, 25
    Cfg.BOSS_TOP = JArray(JInt)([10, 50])
    K.eq(int(Fn.answer(w, "Default", u, "Goblin_Duke", 10.5, 70.0, -3.2)[0]), 2, "B10 ZONE custom tops 10 50, band 1-25")
    Cfg.bosses(None)
    K.eq([int(Fn.zoneOf(h, Cfg.BOSS_TOP)) for h in (1, 20, 21, 45, 46, 75, 76)], [1, 1, 2, 3, 4, 5, 5], "B10 ZONE zoneOf ladder")
    Cfg.DEF_A, Cfg.DEF_B = 0, 0
    K.eq(int(Fn.answer(w, "Default", u, "Goblin_Duke", 10.5, 70.0, -3.2)[0]), 0, "B10 ZONE no band, no NPC level -> 0 (unknown)")
    mi = Mi()
    mi.world, mi.level = "Default", 33
    Lv.MOBS.put(u, mi)
    K.eq(int(Fn.answer(w, "Default", u, "Goblin_Duke", 10.5, 70.0, -3.2)[0]), 3, "B10 ZONE no band -> the NPC's own level 33 (MOBS)")
    K.eq(int(Fn.answer(w, "Elsewhere", u, "Goblin_Duke", 10.5, 70.0, -3.2)[0]), 0, "B10 ZONE the NPC level of another world does not count")
    Cfg.DEF_A, Cfg.DEF_B = 1, 70
    K.eq(int(Fn.answer(w, "Default", u, "Goblin_Duke", 10.5, 70.0, -3.2)[0]), 5, "B10 ZONE the band wins over the NPC level")
    Lv.MOBS.remove(u)
    # ---- credit (read only)
    r = Fn.answer(w, "Default", u, "Goblin_Duke", 10.5, 70.0, -3.2)
    K.check(len(r[2]) == 0 and len(r[3]) == 0 and str(r[1]) == "Goblin_Duke", "B10 CREDIT nobody credited -> empty arrays")
    mob = str(u)
    for p, d in (("p-a", 10.0), ("p-b", 30.0), ("p-c", 30.0), ("p-a", 5.0), ("p-d", 25.0)):
        Cr.hit(mob, p, d, 500.0, 0.0, 1000.0, 1000)
    r = Fn.answer(w, "Default", u, "Goblin_Duke", 10.5, 70.0, -3.2)
    pl, sh = [str(x) for x in r[2]], [float(x) for x in r[3]]
    K.eq(pl, ["p-b", "p-c", "p-d", "p-a"], "B10 CREDIT top damager first, a tie keeps the first hitter on top")
    K.check(abs(sum(sh) - 1.0) < 1e-9 and abs(sh[0] - 0.3) < 1e-9 and abs(sh[3] - 0.15) < 1e-9, "B10 CREDIT shares = credited / total, sum 1: %s" % sh)
    K.check(Cr.T.get(mob) is not None and Cr.read(mob, False) is not None, "B10 CREDIT the MobCredit entry is still there after the call")
    K.check(len(Fn.answer(w, "Default", None, "Goblin_Duke", 10.5, 70.0, -3.2)[2]) == 0, "B10 CREDIT npc null -> empty arrays")
    # ---- apply: bad arguments
    f = Fn()
    bad = [None, JString("x"), A("w", u, "Goblin_Duke", JInt(1), JInt(2)), A(JInt(1), u, "Goblin_Duke", JInt(1), JInt(2), JInt(3)),
           A("w", JString("u"), "Goblin_Duke", JInt(1), JInt(2), JInt(3)), A("w", u, None, JInt(1), JInt(2), JInt(3)),
           A("w", u, "Goblin_Duke", JString("1"), JInt(2), JInt(3)), A("", u, "Goblin_Duke", JInt(1), JInt(2), JInt(3)),
           A("w", u, "Goblin_Duke", JDouble(float("nan")), JInt(2), JInt(3)), A("w", u, "Goblin_Duke", JDouble(5e9), JInt(2), JInt(3))]
    K.check(all(f.apply(b) is None for b in bad), "B10 ARGS bad / missing arguments -> null (no throw)")
    g = f.apply(A("Nowhere", u, "Goblin_Duke", JInt(1), JInt(64), JInt(1)))
    K.check(g is not None and int(g[0]) == 0 and [str(x) for x in g[2]] == pl and Cr.T.get(mob) is not None,
            "B10 ARGS a boss in an unknown world -> zone 0 + the credit list, the entry kept")
    Cr.T.remove(mob)
    # ---- DEAD: taken entries stay readable; over 512 the OLDEST go, never all at once (critic fix, local rebuild)
    Cr.DEAD.clear()
    for k_ in range(520):
        mk_ = "dead-%d" % k_
        Cr.hit(mk_, "p-a", 5.0, 500.0, 0.0, 1000.0, 1000)
        Cr.read(mk_, True)
    K.check(512 <= int(Cr.DEAD.size()) <= 513 and Cr.DEAD.get("dead-519") is not None and Cr.sharesOf("dead-519") is not None
            and Cr.T.get("dead-519") is None,
            "B10 DEAD 520 taken entries: 512-513 kept (oldest evicted one by one, never all), the newest still readable (%d)" % int(Cr.DEAD.size()))
    Cr.DEAD.clear()
    # ---- the bridge put / remove, by the class-file bytes
    pb_ = zipfile.ZipFile(jar).read("com/skyy/mobs/SkyyMobsPlugin.class")
    K.check(b"mob:fn:boss" in pb_ and b"MobBossFn" in pb_, "B10 BRIDGE SkyyMobsPlugin.class names mob:fn:boss + MobBossFn")
    pool = JClass("javassist.ClassPool")(True)
    pool.appendClassPath(jar)
    pool.appendClassPath(B.SERVER_JAR)
    IP, PS, BOS = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")

    def code(cn, mn):
        bos = BOS()
        for mm in pool.get(PKG + cn).getDeclaredMethods():
            if str(mm.getName()) == mn:
                IP(PS(bos)).print_(mm)
        return str(bos.toString())
    su, sd = code("SkyyMobsPlugin", "setup"), code("SkyyMobsPlugin", "shutdown")
    K.check('"mob:fn:boss"' in su and "MobBossFn.<init>" in su and su.find('"mob:fn:setLevel"') < su.find('"mob:fn:boss"'),
            "B10 BRIDGE setup puts mob:fn:boss (after mob:fn:setLevel)")
    K.check('"mob:fn:boss"' in sd and "Map.remove" in sd, "B10 BRIDGE shutdown removes mob:fn:boss")
    K.check("MobLevelAtFn.at" in code("MobBossFn", "bandHi") and "MobLevelFn.apply" in code("MobBossFn", "npcLevel")
            and "remove" not in code("MobCredit", "sharesOf"), "B10 SHAPE the zone reuses levelAt's core + the mob:fn:level path; the credit read never removes")
    K.save()
    d = json.load(open(out + ".0110.json"))
    e = json.load(open(out))
    e["ok"] += d["ok"]
    e["fails"] += d["fails"]
    json.dump(e, open(out, "w"), indent=1)


HK.run("SkyyMobs", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("exec", run_exec), ("live", T19["T18"]["run_live"])], __file__, live=(T19["T18"]["LIVE_DIR"], "Skyy_SkyyMobs"))
