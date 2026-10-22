"""Harness for SkyyGear 0.3.34 (Balance P4 combat - tools/gear_0_3_34_patch.py). Build first:
    python tools/gear_0_3_34_patch.py && python SkyyGear/build_skyygear_0.3.34.py
    python SkyyGear/test_skyygear_0.3.34.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  S  static   the patch re-runs to identical bytes, line endings kept, no new class / command / system
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.3.33 -> 0.3.34 (EXPECT below)
  X  exec     EXECUTES the new paths: GearCfg.curvePts + GearBase.eval of the new F / H / S defaults at item levels 0-100 (Lv 0-20 bit for bit
              0.3.33's; Lv 21-100 = balance_model's P4 rule within the straight-line chord; every point <= 100), gear:fn:weight (GearLLFn mode
              6: a String id -> Integer 1-3, junk -> null), hp4Update on a 0.3.33 default file (the four rows move, the marker, Properties),
              a hand-edited file (kept + noted), CRLF, a second update = null (marker)
  D  live     migrate0330 + migrateP4 on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyGear/config.properties: the four rows move,
              nothing else (Properties), config-history copy, one change-log line each; a SECOND start changes nothing
  AA engine-access audit
Scratch: tools/dev/scratch/balp4b/gear (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.3.34"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "balp4b", "gear")]
import skyybuild as B
import harness_kit as HK
import balance_model as BM

GEN = os.path.join(HERE, "build_skyygear_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyygear_0.3.33.py")
PATCH = os.path.join(ROOT, "tools", "gear_0_3_34_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyGear-0.3.33.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.gear."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyGear")
OLD_F = "1:1.0,4:1.6,10:2.0,20:2.3333333333333335,25:3.1,30:4.5,35:6.5,40:9.6,45:13.6,50:17.5,60:22.5,70:36.0,80:57.0,90:90.0"
OLD_H = "1:1.0,4:1.6,10:2.0,20:2.3333333333333335,25:3.7,30:5.4,35:7.3,40:9.6,45:12.8,50:16.3,60:21.0,70:30.0,80:43.0,90:62.0,100:88.0"
OLD_S = "1:1.0,4:1.6,10:2.0,40:3.0,100:5.0"
EXPECT = {"CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "CfgRows1": ["~<clinit>"], "CfgRows2": ["~<clinit>"],   # version + row defaults
          "GearBase": ["~m reF", "~m reH", "~m reS"],          # the default curve constants inlined
          "GearCfg": ["+f HP4_KEYS", "+f HP4_MARK", "+f HP4_MARK_ID", "+f HP4_NEW", "+f HP4_OLD", "+f HP4_WHO", "+m hp4Log", "+m hp4Update",
                      "+m migrateP4", "+m p4Same", "~<clinit>", "~m apply", "~m defaultsText", "~m gcUpdate"],
          "GearLLFn": ["~m apply"], "SkyyGearPlugin": ["~m setup", "~m shutdown"]}
ADDED = []


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
    K.check(g.startswith('"""SkyyGear 0.3.34 - build script') and g.count('VERSION = "0.3.34"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand(", "makeClass("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    su = g[g.index("@PKG@.GearCfg.migrate02();"):]
    K.check(su.index("migrate0330();") < su.index("migrateP4();") < su.index("@PKG@.GearCfg.load();"), "S setup: migrate0330 -> migrateP4 -> load")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_exec(out, jar, scratch, home):
    from jpype import JClass, JString, JObject
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg, Base, LLFn = JClass(PKG + "GearCfg"), JClass(PKG + "GearBase"), JClass(PKG + "GearLLFn")
    F, H, S = str(Cfg.CURVE_DEF), str(Cfg.HP_DEF), str(Cfg.SPELL_DEF)
    K.check(F == H and F.startswith("1:1.0,4:1.6,10:2.0,20:2.3333333333333335,30:3.624,") and F.endswith(",100:78.937"), "X1 F = H = the P4 points: %s" % F)
    K.eq(S, "1:1.0,8:1.67,20:2.3333333333333335,40:4.67,60:6.07,80:10.99,100:28.75", "X1 S = the P4 spell points")
    pF, pH, pS, oF, oH, oS = (Cfg.curvePts(x) for x in (F, H, S, OLD_F, OLD_H, OLD_S))
    K.check(all(p is not None for p in (pF, pH, pS)), "X1 GearCfg.curvePts reads all three (factors <= 100)")
    same = [L for L in range(0, 21) if float(Base.eval(pF, float(L))) == float(Base.eval(oF, float(L))) and float(Base.eval(pH, float(L))) == float(Base.eval(oH, float(L)))]
    K.eq(len(same), 21, "X1 F and H at item level 0-20 = 0.3.33's bit for bit (every Lv 1-20 tooltip number unchanged)")
    worst = max(abs(float(Base.eval(pF, float(L))) - BM.p4_F(L)) / BM.p4_F(L) for L in range(21, 101))
    K.check(worst <= 0.025, "X1 F at Lv 21-100 = the P4 rule (+4.5 %% a level) within the straight-line chord: worst %.2f %%" % (100 * worst))
    K.check(all(float(Base.eval(pF, float(L))) < float(Base.eval(pF, float(L + 1))) for L in range(1, 100)), "X1 F rises at every level 1-100")
    K.eq([round(float(Base.eval(pF, float(L))) / float(Base.eval(oF, float(L))), 3) for L in (40, 80, 90)], [round(5.627 / 9.6, 3), round(32.731 / 57.0, 3), round(50.83 / 90.0, 3)],
         "X1 a Lv 40 / 80 / 90 item hits x0.586 / x0.574 / x0.565 of 0.3.33 (spec: -41 % at Lv 40)")
    K.check(abs(float(Base.eval(pS, 20.0)) - float(Base.eval(oS, 20.0))) < 1e-9 and float(Base.eval(pS, 40.0)) / float(Base.eval(oS, 40.0)) > 1.5,
            "X1 S: Thorium (Lv 20) spells unchanged, Cobalt (Lv 40) x%.2f" % (float(Base.eval(pS, 40.0)) / float(Base.eval(oS, 40.0))))
    # gear:fn:weight
    fn = LLFn(6)
    r1 = fn.apply(JString("Armor_Iron_Chest"))
    K.check(r1 is not None and int(r1) in (1, 2, 3), "X2 gear:fn:weight answers 1-3 for an armor id (bare JVM: %s)" % r1)
    K.check(fn.apply(JObject(JClass("java.lang.Integer")(5))) is None and fn.apply(JString("")) is None and fn.apply(None) is None, "X2 junk / empty / null -> null (never throws)")
    # hp4Update (pure text)
    dt = str(Cfg.DEFAULT_TEXT) if hasattr(Cfg, "DEFAULT_TEXT") else None
    try:
        from jpype import JArray
        URL = JClass("java.net.URL")
        arr = JArray(URL)(2)
        arr[0] = JClass("java.io.File")(OLD_JAR).toURI().toURL()
        arr[1] = JClass("java.io.File")(B.SERVER_JAR).toURI().toURL()
        ld = JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getPlatformClassLoader())
        OldCfg = JClass(PKG + "GearCfg", loader=ld)
        names = [str(f.getName()) for f in OldCfg.class_.getDeclaredFields()]
        K.notes.append("old GearCfg default fields: %s" % [n for n in names if "DEF" in n.upper() and "TEXT" in n.upper()][:8])
    except Exception as e:
        K.notes.append("old jar loader: %s" % e)
    old_text = "\n".join(["# test", "base.curve=" + OLD_F, "base.hpCurve=" + OLD_H, "base.spellCurve=" + OLD_S,
                          "smith.classArmor=Warrior:Heavy,Berserker:Heavy,Archer:Light,Assassin:Light,Monk:Light,Mage:Cloth,Priest:Cloth", "other.key=5", ""])
    r = Cfg.hp4Update(old_text)
    po, pn = _props(old_text), _props(str(r[0]))
    want = dict(po)
    want.update({"base.curve": F, "base.hpCurve": H, "base.spellCurve": S, "smith.classArmor": po["smith.classArmor"] + ",Spellblade:Light"})
    K.eq(pn, want, "X3 hp4Update: the four untouched rows move (Properties), other.key kept")
    K.check(str(Cfg.HP4_MARK_ID) in str(r[0]) and len(r[3]) == 12 and len(r[2]) == 0, "X3 the marker + 4 change-log rows, no notes")
    K.check(Cfg.hp4Update(str(r[0])) is None, "X3 a second update = null (marker)")
    K.check(bool(Cfg.p4Same(JClass("java.lang.String")(old_text).getBytes("ISO-8859-1"), JClass("java.lang.String")(str(r[0])).getBytes("ISO-8859-1"), r[3])),
            "X3 p4Same: only the planned keys differ")
    crlf = old_text.replace("\n", "\r\n")
    rc = Cfg.hp4Update(crlf)
    K.check(_props(str(rc[0])) == want and "\n" not in str(rc[0]).replace("\r\n", ""), "X3 CRLF kept")
    hand = old_text.replace("base.hpCurve=" + OLD_H, "base.hpCurve=1:1,100:50")
    rh = Cfg.hp4Update(hand)
    ph = _props(str(rh[0]))
    K.check(ph["base.hpCurve"] == "1:1,100:50" and ph["base.curve"] == F and len(rh[2]) == 1 and "base.hpCurve=1:1,100:50 kept" in str(rh[2][0]), "X3 hand-edited H kept + noted: %s" % list(rh[2]))
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg = JClass(PKG + "GearCfg")
    P = JClass("java.nio.file.Paths")
    fc = os.path.join(home, "config.properties")
    Cfg.FILE = P.get(fc)
    log0 = open(os.path.join(home, "config-changes.log"), "rb").read() if os.path.isfile(os.path.join(home, "config-changes.log")) else b""
    for m in ("migrate0330",):
        getattr(Cfg, m)()          # setup's order: the 0.3.30 update first (the live file never started 0.3.30+)
    oc = open(fc, "rb").read()
    msg = str(Cfg.migrateP4())
    nc = open(fc, "rb").read()
    K.check("updated to the 0.3.34" in msg and "4 rows" in msg, "D start 1: %s" % msg[:200].replace("\n", " | "))
    po, pn = _props(oc.decode("latin-1")), _props(nc.decode("latin-1"))
    changed = sorted(k for k in set(po) | set(pn) if po.get(k) != pn.get(k))
    K.eq(changed, ["base.curve", "base.hpCurve", "base.spellCurve", "smith.classArmor"], "D only the four rows changed (Properties)")
    K.eq((pn["base.curve"], pn["base.spellCurve"]), (str(Cfg.CURVE_DEF), str(Cfg.SPELL_DEF)), "D the live file holds the P4 curves")
    skip = (b"base.curve=", b"base.hpCurve=", b"base.spellCurve=", b"smith.classArmor=")
    lo = [x for x in oc.split(b"\n") if not x.startswith(skip)]
    ln_ = [x for x in nc.split(b"\n") if not x.startswith(skip) and str(Cfg.HP4_MARK_ID).encode() not in x]
    K.check(lo == ln_, "D every other line byte-identical, in order (line endings kept); the marker the only new line")
    found = any(open(os.path.join(r_, f_), "rb").read() == oc for r_, _d, fs in os.walk(os.path.join(home, "config-history")) for f_ in fs)
    K.check(found, "D the config-history copy holds the old bytes")
    lg = open(os.path.join(home, "config-changes.log"), "rb").read()[len(log0):].decode("utf-8")
    K.eq(lg.count("\tSkyyGear 0.3.34\t-\tupdate\t"), 4, "D one change-log line per moved row")
    msg2 = str(Cfg.migrateP4())
    K.check(msg2 == "" and open(fc, "rb").read() == nc, "D start 2: nothing changes")
    K.save()


HK.run("SkyyGear", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("exec", run_exec), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyGear"))
