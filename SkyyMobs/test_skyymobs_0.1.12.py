"""Harness for SkyyMobs 0.1.12 (20 levels per zone: zone tops 20 40 60 80 100 from tools/tier_tags.py, every default band row mapped, the
one-time MobMig12 update of config.properties + bands.properties; tools/mobs_0_1_12_patch.py). Every 0.1.11 check (run from
test_skyymobs_0.1.11.py's own code, which runs 0.1.10's, 0.1.9's and 0.1.8's) on the 0.1.12 jar - with 0.1.10's zone-top expectations
swapped for 0.1.12's (same rules, the new tops) - + B12.
Build first: python tools/mobs_0_1_12_patch.py && python SkyyMobs/build_skyymobs_0.1.12.py

    python SkyyMobs/test_skyymobs_0.1.12.py [--keep] [--dir <scratch>]
    python SkyyMobs/test_skyymobs_0.1.12.py --static      (no jars: the text checks only)

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.11 -> 0.1.12 (EXPECT below); added MobMig12
  X  exec     every 0.1.11 exec check, then EXECUTED B12:
              defaults: bosses.zoneTops 20 40 60 80 100 (useDefaults + a file without the line), the fresh file carries the MobMig12
              marker + plate.colors 1 / 20 / 40 / 60 / 81; the loaded biome table: each zone's rows inside its new band and its hardest
              row at the new top (Zone 1 1-20, 2 -40, 3 -60, 4 -80: MobCfg.ZTOP_B); Zone 1 + portal rows byte-identical to the 0.1.11 file;
              mob:fn:boss zones = tools/tier_tags.py zone_of_level for every level 1-150
              CURVES: every difficulty x strength shape, Lv 1-100: finite, >= 1, never falling, Per level never above its cap, the Level
              curve (stretched, Skyy "Stretch to Lv 100") rising at every point up to Lv 100 and Lv 40 = the old Lv 30; the floored health of a 36-HP mob and a 5000-HP boss at Lv 100 finite; One hit at
              most (35 %) holds for a Lv 100 Hard hit (curve + linear) and for a 1e30 hit; the health / damage at Lv 100 printed
              MobMig12.cfgUpdate / bandsUpdate (pure text): untouched rows move (value only), colour keys renamed, a colour whose new key
              exists kept + noted, admin values kept + noted, multi-line entries kept, CRLF kept, the comment lines swapped, the marker =
              null, the fresh default file = null
              MobMig12.run on scratch COPIES of Skyy's live Skyy_SkyyMobs folders (NewBetaTest = the deployed 0.1.11 files; HUD mod = an
              older world: MobMig11 first, as setup does): every default band row moves, nothing else changes (Properties + bytes), Zone 1
              lines byte-identical, the 3 colour rows renamed, History copies of BOTH old files, one config-changes.log line per change, a
              second run changes nothing, MobCfg.load of the migrated folder = the fresh 0.1.12 defaults
  D  live     the 0.1.8 live check (the live Skyy_SkyyMobs copy loads the same settings with 0.1.11 and 0.1.12, twice; bytes unchanged)
  AA engine-access audit
Scratch: tools/dev/scratch/mobauc/mobs (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, re, subprocess, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.1.12"
GEN = os.path.join(HERE, "build_skyymobs_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyymobs_0.1.11.py")
PATCH = os.path.join(ROOT, "tools", "mobs_0_1_12_patch.py")
SCRATCH_DEF = os.path.join(ROOT, "tools", "dev", "scratch", "mobauc", "mobs")
OLD_TOPS, NEW_TOPS = "20 30 45 60 75", "20 40 60 80 100"
CURVE_LV = [1, 20, 30, 40, 47, 53, 60, 65, 73, 80, 100]
OLD_AT30 = {"easy": (3.65, 2.22), "normal": (4.62, 2.62), "hard": (5.6, 3.03), "custom": (5.6, 3.03)}   # the 0.1.11 points at Lv 30 (hp, dmg)


def _arg(name, default=None):
    if name in sys.argv and sys.argv.index(name) + 1 < len(sys.argv):
        return sys.argv[sys.argv.index(name) + 1]
    return default


def run_static():
    fails, ok = [], [0]

    def check(c, what):
        if c:
            ok[0] += 1
        else:
            fails.append(what)
            print("FAIL", what)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    check(g.startswith('"""SkyyMobs 0.1.12 - build script') and g.count('VERSION = "0.1.12"') == 1 and "0.1.11 (the base," in g,
          "S header + VERSION 0.1.12 (the 0.1.11 notes kept as the base)")
    check("ROLLBACK 0.1.12 -> 0.1.11: safe" in g and "MIGRATION MobMig12" in g, "S the 0.1.12 notes are in the generated docstring")
    try:
        compile(g, GEN, "exec")
        check(True, "")
    except SyntaxError as e:
        check(False, "S the generated script compiles as Python: %s" % e)
    for w in ("registerSystem(", "registerCommand(", "bridge().put(", "bridge().remove("):
        check(g.count(w) == o.count(w), "S no new %s vs 0.1.11" % w)
    check(g.count("makeClass(") == o.count("makeClass(") + 1 and ", m11, m12]" in g, "S exactly one new class (MobMig12), in ALL")
    check('BOSS_TOPS_DEF = " ".join(str(_t) for _t in TT.ZONE_TOPS)' in g and 'assert TT.TT_VERSION == "3"' in g,
          "S the zone tops come from tools/tier_tags.py (TT_VERSION 3)")
    su = g[g.index("public void setup() {"):]
    check(su.index("MobMig11.run(dir)") < su.index("MobMig12.run(dir)") < su.index("@PKG@.MobCfg.load();"), "S setup: MobMig11 -> MobMig12 -> MobCfg.load")
    check("like 20 40 60 80 100." in g and "like 20 30 45 60 75." not in g, "S the Server Setup hint names the new tops")
    sc = os.path.join(os.path.abspath(_arg("--dir", SCRATCH_DEF)), "static")
    shutil.rmtree(sc, ignore_errors=True)
    os.makedirs(sc)
    try:
        cp = os.path.join(sc, "build_skyymobs_0.1.12.py")
        p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
        check(p.returncode == 0 and "wrote" in p.stdout, "S the patch re-runs: %s %s" % (p.stdout.strip(), p.stderr.strip()[-300:]))
        check(os.path.isfile(cp) and open(cp, "rb").read() == open(GEN, "rb").read(), "S deterministic: the re-run gives identical bytes")
        check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
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
import tier_tags as TT

# 0.1.10's zone-top expectations (run through the 0.1.11 harness) swapped for 0.1.12's: the same rules on the new tops
EXTRA12 = (
    ('"bosses.zoneTops=20 30 45 60 75\\n" in str(Cfg.DEF_CFG)', '"bosses.zoneTops=20 40 60 80 100\\n" in str(Cfg.DEF_CFG)'),
    ('list(Cfg.BOSS_TOP) == [20, 30, 45, 60, 75], "B10 LOAD defaults after useDefaults")', 'list(Cfg.BOSS_TOP) == [20, 40, 60, 80, 100], "B10 LOAD defaults after useDefaults")'),
    ('str(Cfg.BOSS_TOPS) == "20 30 45 60 75" and bool(Cfg.isBoss("Goblin_Duke"))', 'str(Cfg.BOSS_TOPS) == "20 40 60 80 100" and bool(Cfg.isBoss("Goblin_Duke"))'),
    ('K.check(str(Cfg.BOSS_TOPS) == "20 30 45 60 75" and list(Cfg.BOSS_TOP) == [20, 30, 45, 60, 75], "B10 LOAD a bad',
     'K.check(str(Cfg.BOSS_TOPS) == "20 40 60 80 100" and list(Cfg.BOSS_TOP) == [20, 40, 60, 80, 100], "B10 LOAD a bad'),
    ('for hi in (20, 21, 75, 90):', 'for hi in (20, 21, 100, 120):'),
    ('[int(Fn.zoneOf(h, Cfg.BOSS_TOP)) for h in (1, 20, 21, 45, 46, 75, 76)]', '[int(Fn.zoneOf(h, Cfg.BOSS_TOP)) for h in (1, 20, 21, 60, 61, 100, 101)]'),
    ('mi.world, mi.level = "Default", 33', 'mi.world, mi.level = "Default", 45'),
    ('"B10 ZONE no band -> the NPC\'s own level 33 (MOBS)"', '"B10 ZONE no band -> the NPC\'s own level 45 (MOBS)"'),
    ('''    Cfg.DEF_A, Cfg.DEF_B = 1, 70
    K.eq(int(Fn.answer(w, "Default", u, "Goblin_Duke", 10.5, 70.0, -3.2)[0]), 5, "B10 ZONE the band wins over the NPC level")''',
     '''    Cfg.DEF_A, Cfg.DEF_B = 1, 90
    K.eq(int(Fn.answer(w, "Default", u, "Goblin_Duke", 10.5, 70.0, -3.2)[0]), 5, "B10 ZONE the band wins over the NPC level")'''),
)
_T111 = os.path.join(HERE, "test_skyymobs_0.1.11.py")
_src = open(_T111, encoding="utf-8").read()
_src = _src[:_src.rindex("HK.run(")]
_a = '''('"Goblin_Scrapper", "Cow"]', '"Goblin_Scrapper", "Cow", "Skeleton_Elite_Knight"]')):'''
assert _src.count(_a) == 1, "0.1.11 harness anchor"
_src = _src.replace(_a, _a[:-1] + " + EXTRA12:")
_t10 = open(os.path.join(HERE, "test_skyymobs_0.1.10.py"), encoding="utf-8").read()
for _o, _n in EXTRA12:
    assert _t10.count(_o) == 1, "0.1.10 harness anchor: " + _o
T111 = {"__file__": _T111, "__name__": "test_skyymobs_0_1_11", "EXTRA12": EXTRA12}
exec(compile(_src, _T111, "exec"), T111)

JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMobs-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMobs-0.1.11.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.mobs."
T18 = T111["T110"]["T19"]["T18"]
T18["OLD_JAR"] = OLD_JAR       # the 0.1.8 live phase compares the OLD jar (now 0.1.11) with this one
LIVE_DIR = T18["LIVE_DIR"]     # Saves/HUD mod (the older world)
LIVE_NEW = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyMobs")   # tools/deploy_set.py WORLD (0.1.11 deployed)
EXPECT = {
    "MobCfg": ["~<clinit>", "~m apply", "~m bosses", "~m load", "~m reloadAll", "~m useDefaults"],   # the inlined default texts / zone tops
    "MobHooks": ["~m checkZoneTops"],
    "MobMig14": ["~<clinit>"],      # its curve block (pre-0.1.4 files) = the stretched points
    "SkyyMobsPlugin": ["~m setup"],
    "CfgFn": ["~m opExport"],
    "CfgRows": ["~<clinit>", "~m header"],
}
ADDED = ["MobMig12"]


def _props(txt):
    out = {}
    from jpype import JClass
    p = JClass("java.util.Properties")()
    p.load(JClass("java.io.StringReader")(txt))
    for k in p.stringPropertyNames():
        out[str(k)] = str(p.getProperty(k))
    return out


def run_exec(out, jar, scratch, home):
    T111["run_exec"](out, jar, scratch, home)        # starts the JVM; every 0.1.11 (+ 0.1.10, 0.1.9, 0.1.8) exec check
    import json
    from jpype import JClass
    K = HK.Child(out + ".0112.json")
    Cfg, Mig, Mig11, Bfn = JClass(PKG + "MobCfg"), JClass(PKG + "MobMig12"), JClass(PKG + "MobMig11"), JClass(PKG + "MobBossFn")
    P = JClass("java.nio.file.Paths")
    Cfg.useDefaults()
    # ---- defaults
    dc, db = str(Cfg.DEF_CFG), str(Cfg.DEF_BANDS)
    K.check("\nbosses.zoneTops=%s\n" % NEW_TOPS in dc and dc.count(str(Mig.MARK_ID)) == 1 and str(Mig.MARK) in dc,
            "B12 LOAD the fresh default file: bosses.zoneTops=20 40 60 80 100 + the MobMig12 marker")
    K.eq(re.findall(r"\nplate\.colors\.(\d+)=", dc), ["1", "20", "40", "60", "81"], "B12 LOAD the level colours at the new band starts")
    K.eq(list(Cfg.BOSS_TOP), list(TT.ZONE_TOPS), "B12 LOAD the zone tops = tools/tier_tags.py ZONE_TOPS")
    pc, pb = Cfg.props(Cfg.DEF_CFG), Cfg.props(Cfg.DEF_BANDS)
    pc.remove("bosses.zoneTops")
    Cfg.apply(pc, pb)
    K.eq(str(Cfg.BOSS_TOPS), NEW_TOPS, "B12 LOAD a file without the zoneTops line = the new tops")
    Cfg.useDefaults()
    t = Cfg.BIOME
    rows = [(str(t.raw[i]), int(t.a[i]), int(t.b[i])) for i in range(int(t.n))]
    lo = {1: 1, 2: 20, 3: 40, 4: 60}
    bad = [r for r in rows if r[0].startswith("Zone") and not (lo[int(r[0][4])] <= r[1] <= r[2] <= TT.ZONE_TOPS[int(r[0][4]) - 1])]
    K.eq(bad, [], "B12 BANDS every biome row inside its zone's new band (Zone 1 1-20, 2 20-40, 3 40-60, 4 60-80)")
    K.eq([int(x) for x in Cfg.ZTOP_B][1:5], [20, 40, 60, 80], "B12 BANDS each zone's hardest biome row tops at the zone top (lava caves use it)")
    K.eq(dict((z, max(r[2] for r in rows if r[0].startswith("Zone%d" % z))) for z in (1, 2, 3, 4)), {1: 20, 2: 40, 3: 60, 4: 80}, "B12 BANDS zone maxima")
    zt = [int(Bfn.zoneOf(h, Cfg.BOSS_TOP)) for h in range(1, 151)]
    K.eq(zt, [TT.zone_of_level(h) for h in range(1, 151)], "B12 ZONE mob:fn:boss zoneOf = tools/tier_tags.py zone_of_level, Lv 1-150")
    if os.path.isfile(os.path.join(LIVE_NEW, "bands.properties")):
        old = open(os.path.join(LIVE_NEW, "bands.properties"), encoding="latin-1").read().replace("\r\n", "\n")
        z1o = [l for l in old.split("\n") if re.match(r"(biome\.Zone1|env\.Env_Zone1|env\.Env_Portal|zone\.Zone1)", l)]
        z1n = [l for l in db.split("\n") if re.match(r"(biome\.Zone1|env\.Env_Zone1|env\.Env_Portal|zone\.Zone1)", l)]
        K.check(z1o == z1n and len(z1n) > 40, "B12 BANDS Zone 1 + goblin portal rows = the deployed 0.1.11 file, line for line (%d)" % len(z1n))
    # ---- the strength curves at the new top levels
    probs, shown = [], []
    for sh in ("curve", "linear"):
        for d in ("easy", "normal", "hard", "custom"):
            pc, pb = Cfg.props(Cfg.DEF_CFG), Cfg.props(Cfg.DEF_BANDS)
            pc.setProperty("strength.shape", sh)
            pc.setProperty("strength.difficulty", d)
            Cfg.apply(pc, pb)
            hp = [float(Cfg.hpMult(L)) for L in range(1, 101)]
            dm = [float(Cfg.dmgMult(L)) for L in range(1, 101)]
            for nm, v in (("hp", hp), ("dmg", dm)):
                if not all(x == x and x != float("inf") and x >= 1.0 for x in v):
                    probs.append("%s %s %s not finite / below 1" % (sh, d, nm))
                if any(v[i + 1] < v[i] for i in range(99)):
                    probs.append("%s %s %s falls" % (sh, d, nm))
            if sh == "linear" and (max(hp) > float(Cfg.HP_CAP) + 1e-6 or max(dm) > float(Cfg.DMG_CAP) + 1e-6):
                probs.append("linear %s above its cap" % d)
            if sh == "curve":       # Skyy "Stretch to Lv 100": rising at every curve point up to Lv 100, a Zone 2 Lv 40 mob = the old Lv 30
                for L0, L1 in zip(CURVE_LV, CURVE_LV[1:]):
                    if not (hp[L1 - 1] > hp[L0 - 1] and dm[L1 - 1] > dm[L0 - 1]):
                        probs.append("curve %s not rising from Lv %d to %d" % (d, L0, L1))
                o30 = OLD_AT30[d]
                if abs(hp[39] - o30[0]) > 1e-4 or abs(dm[39] - o30[1]) > 1e-4:
                    probs.append("curve %s Lv 40 = x%.3f / x%.3f, old Lv 30 x%s / x%s" % (d, hp[39], dm[39], o30[0], o30[1]))
            h1, h2 = float(Cfg.hpAmount(100, 36.0)), float(Cfg.hpAmount(100, 5000.0))
            if not (h1 == h1 and h2 == h2 and h1 < 1e6 and h2 < 1e6):
                probs.append("%s %s floored health at Lv 100 not finite" % (sh, d))
            raw = 30.0 * dm[99]
            Cfg.HIT_CAP = 35
            if float(Cfg.capHit(raw, 100.0)) > 35.0 + 1e-9 or float(Cfg.capHit(1e30, 100.0)) != 35.0:
                probs.append("%s %s hit cap does not hold at Lv 100" % (sh, d))
            shown.append("%s/%s Lv100 hp x%.2f dmg x%.2f (Lv 40 x%.2f / x%.2f, Lv 60 x%.2f / x%.2f)" % (sh, d, hp[99], dm[99], hp[39], dm[39], hp[59], dm[59]))
    K.eq(probs, [], "B12 CURVE every difficulty x shape, Lv 1-100: finite, >= 1, never falling, Per level caps, the Level curve rising to Lv 100 + Lv 40 = the old Lv 30, floored health, One hit at most 35 %")
    K.eq([int(x) for x in Cfg.curveOf(2)[0]], CURVE_LV, "B12 CURVE the default points: 1 20 30 40 47 53 60 65 73 80 100")
    K.notes.append("B12 CURVE " + "; ".join(shown))
    Cfg.useDefaults()
    # ---- MobMig12 pure text
    mark = str(Mig.MARK)
    tdo = str(Mig.C_DOLD[0])
    tdn = str(Mig.C_DNEW[0])
    t1 = "a=1\n# c1\n" + tdo + "\nbosses.zoneTops=" + OLD_TOPS + "\nplate.colors.1=#d6e4ee\nplate.colors.30=#E8A93B\nplate.colors.45=#ff6b6b\nplate.colors.61=#CC66CC\nz=2\n"
    r = Mig.cfgUpdate(t1)
    K.eq(str(r[0]), "a=1\n" + mark + "\n# c1\n" + tdn + "\nbosses.zoneTops=" + NEW_TOPS + "\nplate.colors.1=#d6e4ee\nplate.colors.40=#E8A93B\nplate.colors.60=#ff6b6b\nplate.colors.81=#CC66CC\nz=2\n",
         "B12 MIG cfg: zoneTops moves, colour keys renamed, the comment swapped, the marker above the comment run")
    K.eq(list(map(str, r[3]))[:9], ["bosses.zoneTops", OLD_TOPS, NEW_TOPS, "plate.colors[30]", "#E8A93B", "(none)", "plate.colors[40]", "(none)", "#E8A93B"],
         "B12 MIG cfg: change-log rows in the kit's table format (a rename = remove + add)")
    r = Mig.cfgUpdate("bosses.zoneTops=10 50\nplate.colors.30=#123456\nplate.colors.45=#ff6b6b\nplate.colors.60=#000000\n")
    K.check(str(r[0]) == mark + "\nbosses.zoneTops=10 50\nplate.colors.30=#123456\nplate.colors.45=#ff6b6b\nplate.colors.60=#000000\n"
            and len(r[3]) == 0 and len(r[2]) == 3, "B12 MIG cfg: admin values kept + noted; a colour whose new key is set is kept + noted (%s)" % [str(x) for x in r[2]])
    r = Mig.cfgUpdate("x=1\r\nbosses.zoneTops=" + OLD_TOPS + "\r\n")
    K.eq(str(r[0]), "x=1\r\n" + mark + "\r\nbosses.zoneTops=" + NEW_TOPS + "\r\n", "B12 MIG cfg: CRLF kept (the marker above the first moved key)")
    K.check(Mig.cfgUpdate(t1 + mark + "\n") is None and Mig.cfgUpdate(dc) is None, "B12 MIG cfg: the marker (or the fresh default file) = nothing to do")
    r = Mig.cfgUpdate("bosses.zoneTops=20 30 \\\n  45 60 75\n")
    K.check(len(r[3]) == 0 and "bosses.zoneTops=20 30 \\\n  45 60 75\n" in str(r[0]), "B12 MIG cfg: a continued (multi-line) entry is kept")
    # curve tables: a table exactly at its 0.1.11 points is replaced whole (at its first line), an edited one kept + noted, a new one untouched
    old_h = "".join("curve.hp.hard.%s\n" % x for x in str(Mig.K_OLD[2]).split("|"))
    new_h = "".join(x + "\n" for x in str(Mig.K_LINES[2]).split("|"))
    old_e = "".join("curve.hp.easy.%s\n" % x for x in str(Mig.K_OLD[0]).split("|")).replace("curve.hp.easy.20=1.76", "curve.hp.easy.20=1.9")
    r = Mig.cfgUpdate("bosses.zoneTops=" + OLD_TOPS + "\n# h\n" + old_h + "x=1\n" + old_e)
    K.eq(str(r[0]), mark + "\nbosses.zoneTops=" + NEW_TOPS + "\n# h\n" + new_h + "x=1\n" + old_e, "B12 MIG curve: the default Hard health table stretched to Lv 100, the edited Easy one kept")
    K.check(int(r[5]) == 1 and any("curve.hp.easy kept" in str(x) for x in r[2]) and "curve.hp.hard[25]" in list(map(str, r[3])) and "curve.hp.hard[100]" in list(map(str, r[3])),
            "B12 MIG curve: 1 table moved, the edited one noted, log rows curve.hp.hard[25] (gone) ... [100] (new)")
    r = Mig.cfgUpdate("bosses.zoneTops=" + NEW_TOPS + "\n" + new_h.replace("\n", "\r\n"))
    K.check(int(r[5]) == 0 and len(r[2]) == 0 and str(r[0]).endswith(new_h.replace("\n", "\r\n")), "B12 MIG curve: a table already at the 0.1.12 points = nothing (CRLF)")
    r = Mig.cfgUpdate(old_h.replace("\n", "\r\n"))
    K.check(new_h.replace("\n", "\r\n") in str(r[0]), "B12 MIG curve: CRLF kept on the new lines")
    b1 = "# Zone 2 Howling Sands: Lv 20-30\nbiome.Zone1_Tier1=1,7\nbiome.Zone2_Tier1=20,24\nbiome.Zone3_Tier1=31,34\nenv.Env_Zone4_Wastes=45,50,0\r\nzone.Zone2=20,24\nzone.Zone2=20,24\n"
    r = Mig.bandsUpdate(b1)
    K.eq(str(r[0]), "# Zone 2 Howling Sands: Lv 20-40\nbiome.Zone1_Tier1=1,7\nbiome.Zone2_Tier1=20,28\nbiome.Zone3_Tier1=31,34\nenv.Env_Zone4_Wastes=60,67,0\r\nzone.Zone2=20,28\nzone.Zone2=20,28\n",
         "B12 MIG bands: untouched rows move (value only, CR kept), Zone 1 + the admin's 31,34 kept, the heading swapped, no marker in bands")
    K.check(int(r[1]) == 3 and len(r[2]) == 1 and "biome.Zone3_Tier1=31,34 kept" in str(r[2][0]) and list(map(str, r[3]))[:3] == ["bands.biome[Zone2_Tier1]", "20|24", "20|28"],
            "B12 MIG bands: 3 rows moved, 1 kept + noted, log rows bands.biome[...] a|b")
    K.check(Mig.bandsUpdate(db) is not None and int(Mig.bandsUpdate(db)[1]) == 0 and str(Mig.bandsUpdate(db)[0]) == db, "B12 MIG bands: the fresh default file changes nothing")
    # ---- MobMig12.run on scratch COPIES of the live folders
    for tag, src in (("NewBetaTest", LIVE_NEW), ("HUD mod", LIVE_DIR)):
        if not os.path.isdir(src):
            K.check(True, "B12 RUN %s skipped (no live folder)" % tag)
            continue
        d = os.path.join(scratch, "mig12", tag.replace(" ", "_"), "Skyy_SkyyMobs")
        shutil.rmtree(os.path.dirname(d), ignore_errors=True)
        shutil.copytree(src, d)
        fc, fb = os.path.join(d, "config.properties"), os.path.join(d, "bands.properties")
        Mig11.run(P.get(d))                    # setup's order: MobMig11 first (a no-op on NewBetaTest, which has its marker)
        oc, ob = open(fc, "rb").read(), open(fb, "rb").read()
        log0 = open(os.path.join(d, "config-changes.log"), "rb").read() if os.path.isfile(os.path.join(d, "config-changes.log")) else b""
        msg = str(Mig.run(P.get(d)))
        nc, nb = open(fc, "rb").read(), open(fb, "rb").read()
        K.check("updated for 0.1.12" in msg and "%d band rows" % len(Mig.B_KEY) in msg, "B12 RUN %s: %s" % (tag, msg[:220].replace("\n", " | ")))
        po, pn = _props(ob.decode("latin-1")), _props(nb.decode("latin-1"))
        want = dict(po)
        for k, o_, n_ in zip(map(str, Mig.B_KEY), map(str, Mig.B_OLD), map(str, Mig.B_NEW)):
            if want.get(k) == o_:
                want[k] = n_
        K.check(pn == want and pn != po, "B12 RUN %s bands: every untouched default row moved, nothing else (Properties)" % tag)
        K.eq(pn, _props(str(Cfg.DEF_BANDS)), "B12 RUN %s bands: the migrated file = the fresh 0.1.12 defaults (Properties)" % tag)
        lo_, ln_ = ob.split(b"\n"), nb.split(b"\n")
        K.check(len(lo_) == len(ln_) and all(a == b for a, b in zip(lo_, ln_) if not re.match(rb"(biome\.Zone[234]|env\.Env_Zone[234]|zone\.Zone[234]|# Zone [234] )", a)),
                "B12 RUN %s bands: every other line byte-identical (Zone 1, portals, comments, line endings)" % tag)
        pco, pcn = _props(oc.decode("latin-1")), _props(nc.decode("latin-1"))
        wc = dict(pco)
        for k0, k1 in (("plate.colors.30", "plate.colors.40"), ("plate.colors.45", "plate.colors.60"), ("plate.colors.61", "plate.colors.81")):
            if k0 in wc:
                wc[k1] = wc.pop(k0)
        if wc.get("bosses.zoneTops") == OLD_TOPS:
            wc["bosses.zoneTops"] = NEW_TOPS
        ntab, oc_exp = 0, oc.decode("latin-1")
        for t_ in range(8):
            pf = str(Mig.K_PFX[t_])
            om = dict(x.split("=") for x in str(Mig.K_OLD[t_]).split("|"))
            if dict((k[len(pf):], v) for k, v in pco.items() if k.startswith(pf)) == om:
                ntab += 1
                for k in list(wc):
                    if k.startswith(pf):
                        del wc[k]
                for x in str(Mig.K_NEW[t_]).split("|"):
                    wc[pf + x.split("=")[0]] = x.split("=")[1]
                for crn in ("\r\n", "\n"):
                    ob_ = "".join(pf + x + crn for x in str(Mig.K_OLD[t_]).split("|"))
                    if ob_ in oc_exp:
                        oc_exp = oc_exp.replace(ob_, "".join(x + crn for x in str(Mig.K_LINES[t_]).split("|")))
        K.notes.append("B12 RUN %s: %d of 8 curve tables at their 0.1.11 points (stretched)" % (tag, ntab))
        K.eq(pcn, wc, "B12 RUN %s config: only the colour keys renamed / zoneTops moved (Properties)" % tag)
        K.check(nc.replace((mark + "\r\n").encode("latin-1"), b"").replace((mark + "\n").encode("latin-1"), b"").replace(b"plate.colors.40=", b"plate.colors.30=")
                .replace(b"plate.colors.60=", b"plate.colors.45=").replace(b"plate.colors.81=", b"plate.colors.61=") == oc_exp.encode("latin-1"),
                "B12 RUN %s config: bytes = the old file + the marker line, the 3 colour keys renamed, the default curve tables stretched" % tag)
        hist = os.path.join(d, "config-history")
        found = set()
        for root_, _ds, fs in os.walk(hist):
            for fn in fs:
                b_ = open(os.path.join(root_, fn), "rb").read()
                if b_ == oc:
                    found.add("config")
                if b_ == ob:
                    found.add("bands")
        K.eq(sorted(found), ["bands", "config"], "B12 RUN %s History copies of both old files" % tag)
        lg = open(os.path.join(d, "config-changes.log"), "rb").read()[len(log0):].decode("utf-8")
        n12 = lg.count("\tSkyyMobs 0.1.12\t-\tupdate\t")
        K.eq(n12, len(Mig.B_KEY) + 6 + 14 * ntab + (1 if pco.get("bosses.zoneTops") == OLD_TOPS else 0), "B12 RUN %s config-changes.log: one line per change (Undo)" % tag)
        K.check("\tbands.biome[Zone2_Tier1]\t20|24\t20|28\tok" in lg and "\tplate.colors[30]\t#E8A93B\t(none)\tok" in lg and "\tplate.colors[40]\t(none)\t#E8A93B\tok" in lg,
                "B12 RUN %s log lines in the kit's table format" % tag)
        msg2 = str(Mig.run(P.get(d)))
        K.check(msg2 == "" and open(fc, "rb").read() == nc and open(fb, "rb").read() == nb, "B12 RUN %s a second run changes nothing" % tag)
        try:
            Cfg.FILE = P.get(fc)
            Cfg.BANDS = P.get(fb)
            Cfg.load()
            K.eq(list(Cfg.BOSS_TOP), list(TT.ZONE_TOPS), "B12 RUN %s MobCfg.load of the migrated folder: the new zone tops" % tag)
            K.eq([int(x) for x in Cfg.ZTOP_B][1:5], [20, 40, 60, 80], "B12 RUN %s MobCfg.load of the migrated folder: the new zone bands" % tag)
            if ntab == 8:
                K.eq([[int(x) for x in Cfg.curveOf(i_)[0]] for i_ in range(8)], [CURVE_LV] * 8, "B12 RUN %s MobCfg.load: every curve table on the stretched points" % tag)
            K.check(open(fc, "rb").read() == nc and open(fb, "rb").read() == nb, "B12 RUN %s MobCfg.load writes nothing" % tag)
        except Exception as e:
            K.check(False, "B12 RUN %s MobCfg.load: %s" % (tag, e))
        Cfg.useDefaults()
        if "--keep" not in sys.argv:
            shutil.rmtree(os.path.dirname(d), ignore_errors=True)
    K.save()
    dd = json.load(open(out + ".0112.json"))
    e = json.load(open(out))
    e["ok"] += dd["ok"]
    e["fails"] += dd["fails"]
    e["notes"] = e.get("notes", []) + dd.get("notes", [])
    json.dump(e, open(out, "w"), indent=1)


HK.run("SkyyMobs", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("exec", run_exec), ("live", T18["run_live"])], __file__, live=(LIVE_DIR, "Skyy_SkyyMobs"))
