"""Harness for SkyyMobs 0.1.14 (Balance P4 combat - tools/mobs_0_1_14_patch.py). Build first:
    python tools/mobs_0_1_14_patch.py && python SkyyMobs/build_skyymobs_0.1.14.py
    python SkyyMobs/test_skyymobs_0.1.14.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  S  static   the patch re-runs to identical bytes (--out), line endings kept, one new class, the generated tables = tools/balance_model.py
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.13 -> 0.1.14 (EXPECT below); added MobMigP4
  X  exec     EXECUTES the new paths: hpMult / dmgMult at every level 1-100 for Easy / Normal / Hard / Custom = balance_model's tables (straight
              lines), Lv 1-20 Normal Health = 0.1.13's, floor 70, the gap rows, the rank maths (elite roll fixed per UUID, chance 0 / 100,
              Elite / Mini / Boss factors, the boss base, RANKFIX), scale.role's 3rd column, mob:fn:info (rank, dmg x, xpMult x rank capped at
              10, the P3 kill-XP share kept on Normal), mob:fn:setLevel's rank argument, checkScaleRole, LevelDamage reads MobInfo.dx before
              the gap and the cap (bytecode), MobMigP4.plan on a fresh file (nothing), a hand-edited file (kept + noted), a half-migrated one,
              CRLF line endings
  D  live     MobMigP4.run on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyMobs: every planned key moves, nothing else (Properties),
              the History copy holds the old bytes, one change-log line per change, then MobCfg.load = the P4 numbers; a SECOND start
              changes nothing (start twice)
  AA engine-access audit
Scratch: tools/dev/scratch/balp4b/mobs (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, subprocess, uuid as _uuid

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.1.14"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "balp4b", "mobs")]
import skyybuild as B
import harness_kit as HK
import balance_model as BM

GEN = os.path.join(HERE, "build_skyymobs_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyymobs_0.1.13.py")
PATCH = os.path.join(ROOT, "tools", "mobs_0_1_14_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMobs-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMobs-0.1.13.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.mobs."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyMobs")
EXPECT = {
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],   # the version + the new rows / default file
    "LevelDamage": ["~m handle"],
    "MobCfg": ["+f P_ELITE", "+f P_MINI", "+f RANKFIX", "+f RANK_BOSS_BASE", "+f RANK_BOSS_DMG", "+f RANK_ELITE_CHANCE", "+f RANK_ELITE_DMG",
               "+f RANK_ELITE_HP", "+f RANK_ELITE_LEVELS", "+f RANK_ELITE_ROLES", "+f RANK_MINI_DMG", "+f RANK_MINI_HP", "+f RANK_MINI_ROLES",
               "+f REF_N", "+f REF_PTS", "+f SHARE_H", "+f SHARE_N", "+m eliteRoll", "+m factors", "+m mix64", "+m rankDmg", "+m rankHp",
               "+m rankOf", "+m rankPut", "+m rankWord", "+m refCurve", "+m roleDx", "~<clinit>", "~m apply", "~m derive", "~m hardRef", "~m load",
               "~m reloadAll", "~m roles", "~m useDefaults", "~m van"],   # van: the built-in list constant (+ the elite skeletons)
    "MobHooks": ["~m checkScaleRole"], "MobInfo": ["+f dx", "+f rank", "+f rolled", "~c "], "MobInfoFn": ["~m apply"],
    "MobLevel": ["~m apply", "~m forget", "~m onAdd", "~m refreshWorld"],
    "MobMig14": ["~<clinit>", "~m update"],   # its curve / gap / role-doc constants are the 0.1.14 defaults (a pre-0.1.4 file gets them)
    "MobSetLevelFn": ["+m rankArg", "~m apply"], "SkyyMobsPlugin": ["~m setup"],
}
ADDED = ["MobMigP4"]
KINDS = [("hp", "easy"), ("hp", "normal"), ("hp", "hard"), ("hp", "custom"), ("dmg", "easy"), ("dmg", "normal"), ("dmg", "hard"), ("dmg", "custom")]


def _props(txt):
    from jpype import JClass
    out = {}
    p = JClass("java.util.Properties")()
    p.load(JClass("java.io.StringReader")(txt))
    for k in p.stringPropertyNames():
        out[str(k)] = str(p.getProperty(k))
    return out


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyMobs 0.1.14 - build script') and g.count('VERSION = "0.1.14"') == 1 and "0.1.13 (the base," in g, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand(", "bridge().put("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check(g.count("makeClass(") == o.count("makeClass(") + 1 and ", m11, m12, mp4]" in g, "S exactly one new class (MobMigP4), in ALL")
    su = g[g.index("public void setup() {"):]
    K.check(su.index("MobMig12.run(dir)") < su.index("MobMigP4.run(dir)") < su.index("@PKG@.MobCfg.load();"), "S setup: MobMig12 -> MobMigP4 -> MobCfg.load")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build_skyymobs_0.1.14.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and os.path.isfile(cp) and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.check(not BM.p4_table_problems(), "S balance_model: the P4 tables hold the RULE")
    K.save()


def run_exec(out, jar, scratch, home):
    from jpype import JClass, JArray, JString, JObject
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    Cfg, Lvl, Info, InfoFn, SetFn, Hooks, MP4 = (JClass(PKG + n) for n in ("MobCfg", "MobLevel", "MobInfo", "MobInfoFn", "MobSetLevelFn", "MobHooks", "MobMigP4"))
    Props, UUID = JClass("java.util.Properties"), JClass("java.util.UUID")
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg.useDefaults()
    # ---- the curve tables at every level (the runtime path: MobCfg.curveMult = hpMult / dmgMult)
    worst = 0.0
    for i, (k, d) in enumerate(KINDS):
        pts = BM.p4_table(k, d)
        for L in range(1, 101):
            want = BM.p4_interp(pts, L)
            got = float(Cfg.curveMult(i, L))
            worst = max(worst, abs(got - want) / want)
    K.check(worst < 1e-6, "X1 curveMult at Lv 1-100 x 8 tables = balance_model P4_TABLES (straight lines): worst %.2e" % worst)
    for name, di in (("easy", 0), ("normal", 1), ("hard", 2), ("custom", 3)):
        Cfg.DIFFICULTY = name
        Cfg.derive(None)
        K.check(abs(float(Cfg.hpMult(60)) - BM.p4_interp(BM.p4_table("hp", name), 60)) < 1e-5 and abs(float(Cfg.dmgMult(60)) - BM.p4_interp(BM.p4_table("dmg", name), 60)) < 1e-5,
                "X1 %s: hpMult / dmgMult(60) = x%.2f / x%.2f" % (name, float(Cfg.hpMult(60)), float(Cfg.dmgMult(60))))
    Cfg.useDefaults()
    old_n = [(1, 1.0), (20, 2.14), (30, 3.03), (40, 4.62), (47, 6.97), (53, 10.69), (60, 15.63), (65, 19.66), (73, 21.48), (80, 23.0), (100, 27.56)]
    K.check(all(abs(float(Cfg.hpMult(L)) - BM.p4_interp(old_n, L)) <= 0.0051 for L in range(1, 21)), "X1 Lv 1-20 Normal Health = 0.1.13's")
    K.check(all(float(Cfg.hpMult(L)) < float(Cfg.hpMult(L + 1)) for L in range(1, 100)) and all(float(Cfg.dmgMult(L)) < float(Cfg.dmgMult(L + 1)) for L in range(1, 100)),
            "X1 Normal Health + damage rise at every level 1-100")
    # ---- floor + gap
    K.eq((int(Cfg.HP_FLOOR), int(Cfg.GAP_FREE), float(Cfg.GAP_DSTEP), float(Cfg.GAP_DMIN), float(Cfg.GAP_TSTEP), float(Cfg.GAP_TMAX)), (70, 3, 5.0, 40.0, 3.0, 1.5),
         "X2 defaults: floor 70, gap 3 / 5 / 40 / 3 / 1.5")
    K.check(abs(float(Cfg.hpAmount(1, 36.0)) - 70.0 / 36.0) < 1e-5 and float(Cfg.hpAmount(1, 200.0)) == 1.0, "X2 the floor lifts a 36-HP mob to 70 at Lv 1, a 200-HP one keeps 200")
    Gap = JClass(PKG + "MobGap")
    try:
        meth = [str(m.getName()) for m in Gap.class_.getDeclaredMethods()]
        K.notes.append("MobGap methods: %s" % sorted(set(meth)))
        if "taken" in meth and "dealt" in meth:
            K.check(abs(float(Gap.taken(5)) - 1.06) < 1e-6 and abs(float(Gap.dealt(5)) - 0.90) < 1e-6 and abs(float(Gap.taken(10)) - 1.21) < 1e-6 and abs(float(Gap.dealt(10)) - 0.65) < 1e-6,
                    "X2 MobGap: +5 -> you deal x0.90 / take x1.06; +10 -> x0.65 / x1.21 (balance_model p4_gap %s / %s)" % (BM.p4_gap(5), BM.p4_gap(10)))
    except Exception as e:
        K.check(False, "X2 MobGap: %s" % e)
    # ---- ranks
    u = [UUID.fromString(str(_uuid.UUID(int=(i * 0x9E3779B97F4A7C15 + 12345) % (1 << 128)))) for i in range(4000)]
    el = [bool(Cfg.eliteRoll(x)) for x in u]
    K.check(80 <= sum(el) <= 160, "X3 elite roll at 3 %%: %d of 4000 mobs (expect ~120)" % sum(el))
    K.check([bool(Cfg.eliteRoll(x)) for x in u[:200]] == el[:200], "X3 the roll is fixed per UUID (a reload keeps it)")
    Cfg.RANK_ELITE_CHANCE = 0.0
    K.check(not any(bool(Cfg.eliteRoll(x)) for x in u[:500]), "X3 chance 0 = no rolled elite")
    Cfg.RANK_ELITE_CHANCE = 100.0
    K.check(all(bool(Cfg.eliteRoll(x)) for x in u[:500]), "X3 chance 100 = every band mob")
    Cfg.useDefaults()
    plain = next(x for x, e in zip(u, el) if not e)
    rolled = next(x for x, e in zip(u, el) if e)
    K.eq(int(Cfg.rankOf("Skeleton_Fighter", plain, True)), 0, "X3 a plain band mob: no rank")
    K.eq(int(Cfg.rankOf("Skeleton_Fighter", rolled, True)), 1, "X3 a rolled band mob: elite")
    K.eq(int(Cfg.rankOf("Skeleton_Fighter", rolled, False)), 0, "X3 the same mob with a fixed / set level: no roll")
    K.eq([int(Cfg.rankOf(r, plain, True)) for r in ("Skeleton_Elite", "Outlander_Brute", "Skeleton_Pirate_Captain", "Trork_Chieftain", "Goblin_Duke_Phase_2", "Dragon_Fire")],
         [1, 1, 1, 3, 3, 3], "X3 Elite roles (*_Elite*, *Brute*, *Captain*) = elite; Boss roles = boss")
    f = list(Cfg.factors("Skeleton_Elite", plain, 60.0, True))
    K.check(abs(f[0] - 3.0) < 1e-9 and abs(f[1] - 1.5) < 1e-9 and int(f[2]) == 1, "X3 elite factors x3 Health / x1.5 damage: %s" % f)
    f = list(Cfg.factors("Trork_Chieftain", plain, 300.0, False))
    K.check(abs(f[0] - 4500.0 / 300.0) < 1e-9 and abs(f[1] - 2.0) < 1e-9 and int(f[2]) == 3, "X3 boss: base 300 -> Health x15 (= 4500 before the curve), damage x2: %s" % f)
    f = list(Cfg.factors("Trork_Chieftain", plain, 40.0, False))
    K.check(abs(f[0] - 4500.0 / 70.0) < 1e-9, "X3 boss under the floor: 4500 / 70 (the floor counted like hpAmount): %s" % f)
    Cfg.RANKFIX.put(plain, JClass("java.lang.Integer")(2))
    f = list(Cfg.factors("Skeleton_Fighter", plain, 60.0, True))
    K.check(abs(f[0] - 10.0) < 1e-9 and abs(f[1] - 2.0) < 1e-9 and int(f[2]) == 2, "X3 RANKFIX mini boss x10 / x2: %s" % f)
    Cfg.RANKFIX.clear()
    # fix2: rankPut keeps at most 2000 and drops ONE entry when full (never every live mob's rank)
    UU = JClass("java.util.UUID")
    for _k in range(2000):
        Cfg.rankPut(UU.randomUUID(), 1)
    K.eq(int(Cfg.RANKFIX.size()), 2000, "X3 rankPut: 2000 asked ranks held")
    nu = UU.randomUUID()
    Cfg.rankPut(nu, 2)
    K.check(int(Cfg.RANKFIX.size()) == 2000 and int(Cfg.RANKFIX.get(nu)) == 2, "X3 rankPut on a full map: one old entry dropped, the new rank kept (size %d)" % int(Cfg.RANKFIX.size()))
    Cfg.rankPut(nu, 3)
    K.check(int(Cfg.RANKFIX.size()) == 2000 and int(Cfg.RANKFIX.get(nu)) == 3, "X3 rankPut on a key already held: nothing dropped")
    Cfg.rankPut(nu, 0)
    K.eq(int(Cfg.RANKFIX.get(nu)), 3, "X3 rankPut with no rank: ignored")
    Cfg.RANKFIX.clear()
    pr = Props()
    pr.setProperty("rank.mini.roles", "Golem_*")
    pr.setProperty("rank.elite.hp", "4")
    Cfg.apply(pr, Props())
    K.check(int(Cfg.rankOf("Golem_Crystal_Sand", plain, True)) == 2 and abs(float(Cfg.rankHp(1, 60.0)) - 4.0) < 1e-9, "X3 the Ranks rows read from the file (mini roles, elite Health x)")
    # ---- scale.role 3rd column
    pr = Props()
    pr.setProperty("scale.role.Test_Role", "20,2,3")
    pr.setProperty("scale.role.Old_Role", "15,1.5")
    Cfg.apply(pr, Props())
    K.check(int(Cfg.roleLevel("Test_Role")) == 20 and abs(float(Cfg.roleX("Test_Role")) - 2.0) < 1e-9 and abs(float(Cfg.roleDx("Test_Role")) - 3.0) < 1e-9
            and abs(float(Cfg.roleDx("Old_Role")) - 1.0) < 1e-9 and abs(float(Cfg.roleX("Old_Role")) - 1.5) < 1e-9, "X4 scale.role: 3 columns read, an old 2-column line = damage x1")
    K.check(Hooks.checkScaleRole("scale.role[X]", "20|2|3") is None and Hooks.checkScaleRole("scale.role[X]", "20|2|300") is not None
            and Hooks.checkScaleRole("scale.role[X]", "20|2") is None, "X4 checkScaleRole: the Damage x column (0.1-100)")
    Cfg.useDefaults()
    K.eq([int(Cfg.roleLevel(r)) for r in ("Trork_Chieftain", "Goblin_Duke", "Goblin_Duke_Phase_3_Slow", "Dragon_Frost", "Dragon_Fire")], [18, 38, 38, 78, 98],
         "X4 the default boss rows (fresh file)")
    K.check("Skeleton_Elite*" not in str(Cfg.EXCLUDE) and "*_Boss*" in str(Cfg.EXCLUDE) and bool(Cfg.builtIn("Skeleton_Elite")), "X4 levels.exclude without the vanilla bosses; Skeleton_Elite built in")
    K.check(Cfg.whyNotRole("HOSTILE", "Trork_Chieftain") is None and Cfg.whyNot("HOSTILE", "Dungeon_Crypt_Boss") is not None, "X4 a boss with a row gets a level; another mod's *_Boss* never")
    # ---- mob:fn:info
    i0 = Info()
    i0.world, i0.uuid, i0.role, i0.level, i0.base = "w", plain, "Skeleton_Fighter", 40, 60.0
    i0.rx, i0.dx, i0.rank = 3.0, 1.5, 1
    Lvl.MOBS.put(plain, i0)
    a = list(InfoFn().apply(JObject(JArray(JClass("java.lang.Object"))([JString("w"), plain]))))
    hm = BM.p4_interp(BM.p4_table("hp", "normal"), 40)
    share = BM.p4_interp(old_n, 40) / BM.p4_interp([(1, 1.0), (20, 2.52), (30, 3.62), (40, 5.6), (47, 8.53), (53, 13.18), (60, 19.41), (65, 24.52), (73, 26.95), (80, 28.98), (100, 35.07)], 40)
    K.check(int(a[0]) == 40 and abs(float(a[3]) - hm * 3.0) < 1e-4 and abs(float(a[4]) - BM.p4_interp(BM.p4_table("dmg", "normal"), 40) * 1.5) < 1e-4
            and abs(float(a[5]) - share * 3.0) < 1e-4 and str(a[6]) == "elite",
            "X5 mob:fn:info elite Lv 40: hpMult x3, dmgMult x1.5, xpMult = 0.1.13's Normal share %.3f x3, rank 'elite': %s" % (share, a))
    i0.rank, i0.rx, i0.dx, i0.role = 3, 75.0, 2.0, "Trork_Chieftain"
    a = list(InfoFn().apply(plain))
    K.check(abs(float(a[5]) - share * 10.0) < 1e-4 and str(a[6]) == "boss", "X5 a boss pays at most x10: xpMult %.3f" % float(a[5]))
    i0.rank, i0.rx, i0.dx, i0.role = 0, 1.0, 1.0, "Skeleton_Fighter"
    a = list(InfoFn().apply(plain))
    K.check(abs(float(a[5]) - share) < 1e-4 and str(a[6]) == "", "X5 unranked Normal: xpMult = 0.1.13's share (P3 kill XP kept): %.4f" % float(a[5]))
    Cfg.DIFFICULTY = "hard"
    Cfg.derive(None)
    K.check(abs(float(InfoFn().apply(plain)[5]) - 1.0) < 1e-9, "X5 Hard pays the full share (1)")
    Cfg.useDefaults()
    Lvl.MOBS.clear()
    K.eq(int(SetFn.rankArg(JArray(JClass("java.lang.Object"))([JString("w"), plain, JClass("java.lang.Integer")(5), None, JString("mini")]))), 2, "X5 mob:fn:setLevel rank argument 'mini' = 2")
    K.eq(int(SetFn.rankArg(JArray(JClass("java.lang.Object"))([JString("w"), plain, JClass("java.lang.Integer")(5)]))), 0, "X5 no 5th argument = no rank")
    # ---- LevelDamage bytecode: MobInfo.dx before the gap and the cap
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
    hd = code("LevelDamage", "handle")
    K.check("MobInfo.dx" in hd and hd.index("MobCfg.dmgMult") < hd.index("MobInfo.dx", hd.index("MobCfg.dmgMult")) < hd.index("MobGap.gapOf") < hd.rindex("MobCfg.capHit"),
            "X6 LevelDamage: level curve x MobInfo.dx, then the gap, then One hit at most")
    K.check(hd.index("MobInfo.dx") < hd.index("MobCfg.HIT_CAP") and hd.index("MobInfo.level") < hd.index("MobInfo.dx"),
            "X6 LevelDamage (fix2): a Lv 1 mob with a Damage x != 1 takes the levelled path (dx read in the lvd test, before the cap-only branch)")
    rp = code("MobSetLevelFn", "apply")
    K.check("MobCfg.rankPut" in rp and "RANKFIX.clear" not in rp, "X6 mob:fn:setLevel stores the rank through MobCfg.rankPut (no clear-all)")
    ap = code("MobLevel", "apply")
    K.check("MobCfg.factors" in ap and "MobInfo.dx" in ap and "MobInfo.rank" in ap, "X6 MobLevel.apply stores the rank factors")
    # ---- MobMigP4.plan (pure text)
    dc = str(Cfg.DEF_CFG)
    K.check(MP4.plan(dc) is None, "X7 the fresh default file carries the marker: plan = null")
    old_jar_cfg = None
    try:
        from jpype import JClass as _J
        import zipfile
        # the 0.1.13 default file text = the old jar's MobCfg.DEF_CFG (read through its own loader)
        URL = JClass("java.net.URL")
        arr = JArray(URL)(2)
        arr[0] = JClass("java.io.File")(OLD_JAR).toURI().toURL()
        arr[1] = JClass("java.io.File")(B.SERVER_JAR).toURI().toURL()
        ld = JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getPlatformClassLoader())   # NOT the system loader (it holds the new jar)
        old_jar_cfg = str(JClass(PKG + "MobCfg", loader=ld).DEF_CFG)
    except Exception as e:
        K.check(False, "X7 the 0.1.13 default file: %s" % e)
    if old_jar_cfg:
        r = MP4.plan(old_jar_cfg)
        po, pn, pd = _props(old_jar_cfg), _props(str(r[0])), _props(dc)
        K.eq(pn, pd, "X7 a 0.1.13 default file updates to exactly the 0.1.14 defaults (Properties)")
        K.check(int(r[1]) == 5 + 8 and int(r[5]) == 8 and len(r[2]) == 0, "X7 13 settings moved (5 rows + 8 tables), nothing kept")
        logs = [str(x) for x in r[3]]
        K.check(logs[:3] == ["strength.floor", "50", "70"] and "curve.hp.normal[25]" in logs and "scale.role[Dragon_Fire]" in logs and "rank.boss.base" in logs,
                "X7 change-log rows: %s ..." % logs[:9])
        K.check(MP4.plan(str(r[0])) is None, "X7 a second plan on the result = null (the marker)")
        crlf = old_jar_cfg.replace("\n", "\r\n")
        rc = MP4.plan(crlf)
        K.check(_props(str(rc[0])) == pd and "\n" not in str(rc[0]).replace("\r\n", ""), "X7 CRLF file: same result, every line ending CRLF")
        hand = old_jar_cfg.replace("\nstrength.floor=50\n", "\nstrength.floor=55\n").replace("\ncurve.hp.normal.40=4.62\n", "\ncurve.hp.normal.40=5\n").replace("\ngap.free=5\n", "\ngap.free=4\n")
        hand = hand.replace("\nscale.role.x=1\n", "\n") + "scale.role.trork_chieftain=10,1\n"
        rh = MP4.plan(hand)
        ph = _props(str(rh[0]))
        kept = " | ".join(str(x) for x in rh[2])
        K.check(ph["strength.floor"] == "55" and ph["gap.free"] == "4" and ph["curve.hp.normal.40"] == "5" and "curve.hp.normal.25" not in ph
                and ph["curve.hp.hard.25"] == "4.31" and ph["gap.dealtStep"] == "5" and "scale.role.Trork_Chieftain" not in ph and ph["scale.role.Dragon_Fire"] == "98,1,1",
                "X7 hand-edited: floor 55 / gap.free 4 / a Normal Health point / a lower-case Trork row kept, the rest moved")
        K.check("strength.floor=55 kept" in kept and "gap.free=4 kept" in kept and "curve.hp.normal kept" in kept, "X7 hand-edited: each kept value noted: %s" % kept[:300])
        half = str(r[0]).replace(str(MP4.MARK) + "\n", "")
        rh2 = MP4.plan(half)
        K.check(rh2 is not None and _props(str(rh2[0])) == pd and int(rh2[1]) == 0, "X7 half-migrated (marker lost): nothing moves twice, the block is not duplicated")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg, MP4, M12 = JClass(PKG + "MobCfg"), JClass(PKG + "MobMigP4"), JClass(PKG + "MobMig12")
    P = JClass("java.nio.file.Paths")
    fc = os.path.join(home, "config.properties")
    oc = open(fc, "rb").read()
    log0 = open(os.path.join(home, "config-changes.log"), "rb").read() if os.path.isfile(os.path.join(home, "config-changes.log")) else b""
    M12.run(P.get(home))      # setup's order (a no-op on NewBetaTest: its marker is there)
    K.check(open(fc, "rb").read() == oc, "D MobMig12 is a no-op on the live copy")
    msg = str(MP4.run(P.get(home)))
    nc = open(fc, "rb").read()
    K.check("updated for 0.1.14" in msg, "D start 1: %s" % msg[:240].replace("\n", " | "))
    po, pn = _props(oc.decode("latin-1")), _props(nc.decode("latin-1"))
    changed = sorted(k for k in set(po) | set(pn) if po.get(k) != pn.get(k))
    plan = set(["strength.floor", "levels.exclude", "gap.free", "gap.dealtStep", "gap.takenStep"]) | set(k for k in set(po) | set(pn) if k.startswith("curve."))
    plan |= set(str(x) for x in MP4.R_KEY) | set(str(x) for x in MP4.A_KEY)
    K.check(set(changed) <= plan, "D only the planned keys changed: %s" % sorted(set(changed) - plan)[:10])
    K.eq((pn.get("strength.floor"), pn.get("gap.free"), pn.get("gap.dealtStep"), pn.get("gap.takenStep"), pn.get("curve.hp.normal.100"), pn.get("scale.role.Dragon_Fire")),
         ("70", "3", "5", "3", "102.45", "98,1,1"), "D the live file holds the P4 numbers")
    K.check(nc.count(str(MP4.MARK_ID).encode()) == 1, "D the marker once")
    found = False
    for r_, _d, fs in os.walk(os.path.join(home, "config-history")):
        for fn in fs:
            if open(os.path.join(r_, fn), "rb").read() == oc:
                found = True
    K.check(found, "D the config-history copy holds the old bytes")
    lg = open(os.path.join(home, "config-changes.log"), "rb").read()[len(log0):].decode("utf-8")
    K.eq(lg.count("\tSkyyMobs 0.1.14\t-\tupdate\t"), len(MP4.plan(oc.decode("latin-1"))[3]) // 3, "D one change-log line per change")
    ch = set(changed)
    rd_old, rd_new = str(MP4.C_DOLD[0]).encode(), str(MP4.C_DNEW[0]).encode()

    def keep(ln):
        k = ln.split(b"=")[0].strip().decode("latin-1")
        return not (k in ch or ln.rstrip(b"\r") in (rd_old, rd_new))
    body_n = nc[:nc.rindex(str(MP4.MARK).encode())]
    lo = [ln for ln in oc.split(b"\n") if keep(ln)]
    ln_ = [ln for ln in body_n.split(b"\n") if keep(ln)]
    K.check(lo[:-1] == ln_[:len(lo) - 1] and all(not x.strip() or x.startswith(b"#") for x in ln_[len(lo) - 1:]),
            "D every other line byte-identical, in order (line endings kept); new lines only at the moved rows + the end block")
    Cfg.DIR = P.get(home)
    Cfg.FILE = P.get(fc)
    Cfg.BANDS = P.get(os.path.join(home, "bands.properties"))
    Cfg.load()
    K.check(abs(float(Cfg.hpMult(80)) - 39.17) < 1e-5 and int(Cfg.HP_FLOOR) == 70 and int(Cfg.GAP_FREE) == 3 and int(Cfg.roleLevel("Trork_Chieftain")) == 18,
            "D MobCfg.load of the migrated live copy: Lv 80 Health x39.17, floor 70, gap 3, Trork Chieftain Lv 18")
    K.check(open(fc, "rb").read() == nc, "D MobCfg.load writes nothing")
    msg2 = str(MP4.run(P.get(home)))
    Cfg.load()
    K.check(msg2 == "" and open(fc, "rb").read() == nc, "D start 2: nothing changes")
    K.save()


HK.run("SkyyMobs", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("exec", run_exec), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyMobs"))
