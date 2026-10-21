"""Harness for SkyyCooking 0.1.15 (tools/cooking_0_1_15_patch.py): Balance Pass P3 - Cooking XP x the tier factor + CookP3Mig.
Build first: python tools/cooking_0_1_15_patch.py && python SkyyCooking/build_skyycooking_0.1.15.py

    python SkyyCooking/test_skyycooking_0.1.15.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.1.14 -> 0.1.15: + CookP3Mig; CookCfg's table constants; the plugin's setup; the kit's version texts
  P3   EXECUTED CookCfg.load on a fresh file: CookCfg.xpFor = the P3 table (the build's numbers, read back from the generated
       build script's print), xp.default kept, Food_Pie_Pumpkin (T7 Pumpkin) pays more than Food_Pie_Meat; an hand-edited line is read as is
  PM   CookP3Mig.migrate end to end on scratch copies of the 0.1.14 default file (LF + CRLF): every xp line on its 0.1.14 default -> P3,
       the help line reworded, the marker, History copy, one change-log row per line, start 2 nothing, a hand-set line kept, a fresh 0.1.15
       file untouched, no file = nothing
  LIVE every one-time update in setup() order + CookCfg.load on a scratch COPY of the live Skyy_SkyyCooking (NewBetaTest), twice: start 1
       moves the xp lines still on 0.1.14 defaults (custom ones kept), start 2 writes nothing
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import skyybuild as B

VERSION, OLD = "0.1.15", "0.1.14"
JAR = os.path.join(HERE, "SkyyCooking-%s.jar" % VERSION)
OLD_JAR = os.path.join(HERE, "SkyyCooking-%s.jar" % OLD)
PKG = "com.skyy.cooking."
SCRATCH = HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "balp3", "cook"))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyCooking")
EXPECT = {
    "CfgFn": ["~m opExport"],
    "CfgRows": ["~<clinit>", "~m header"],
    "CookCfg": ["~<clinit>", "~m load"],   # the P3 table constants + the version text in load's INFO
    "CookIngMig": ["~m migrate"], "CookMig": ["~m logLine", "~m migrate"], "CookTblMig": ["~m migrate"], "CookXpMig": ["~m migrate"],
    "CookNcMig": ["~m migrate"],   # the version text (WHO) only, as in every round
    "SkyyCookingPlugin": ["~m setup"],
    "SupCfg": ["~m load"],
}
MIGS = ("CookMig", "CookXpMig", "CookTblMig", "CookIngMig", "CookNcMig", "CookP3Mig")


def p3_table():
    """the P3 table as the build printed it: parsed from the default text constant of the jar (one source)"""
    from jpype import JClass
    t = str(JClass(PKG + "CookCfg").DEFAULTS)
    return dict((m.group(1), int(m.group(2))) for m in re.finditer(r"^xp\.(\w+)=(\d+)$", t, re.M) if m.group(1) != "default")


def old_text():
    from jpype import JClass, JArray
    arr = JArray(JClass("java.net.URL"))(2)
    arr[0] = JClass("java.io.File")(OLD_JAR).toURI().toURL()
    arr[1] = JClass("java.io.File")(B.SERVER_JAR).toURI().toURL()
    ld = JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getPlatformClassLoader())
    return str(JClass(PKG + "CookCfg", loader=ld).DEFAULTS)


def snapd(d):
    return dict((os.path.relpath(os.path.join(r, f), d).replace(os.sep, "/"), open(os.path.join(r, f), "rb").read()) for r, ds, fs in os.walk(d) for f in fs)


def run_p3(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Paths = JClass("java.nio.file.Paths")
    Cfg = JClass(PKG + "CookCfg")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyCookTest")
    d = os.path.join(scratch, "p3")
    os.makedirs(d, exist_ok=True)
    Cfg.FILE = Paths.get(os.path.join(d, "cooking.properties"))
    r = str(Cfg.load())
    tab = p3_table()
    ids = [str(x) for x in Cfg.XP_IDS]
    vals = [int(x) for x in Cfg.XP_VALS]
    K.check(dict(zip(ids, vals)) == tab and len(tab) == 44, "P3 compiled XP_IDS / XP_VALS = the default file's xp lines (%d)" % len(tab))
    K.check(all(int(Cfg.xpFor(k)) == v for k, v in tab.items()), "P3 CookCfg.xpFor pays the P3 table on a fresh file")
    K.check(tab["Food_Kebab_Vegetable"] == 100 and tab["Food_Pie_Meat"] == 2750 and tab["Food_Pie_Pumpkin"] > tab["Food_Pie_Meat"]
            and tab["Food_Skyy_Fisherman_Pie"] > tab["Food_Pie_Pumpkin"], "P3 the tier factor: Pumpkin (T7) / Onion pies pay more than the meat pie")
    K.check(int(Cfg.xpFor("Food_Skyy_No_Such_Dish")) == int(Cfg.XP_DEFAULT) == 1000, "P3 an unknown output pays xp.default 1000")
    K.check(float(Cfg.XP_MULT) == 0.5 and int(Cfg.MAX_PER_MIN) == 0, "P3 xpMultiplier 0.5, maxXpPerMinute 0 unchanged")
    t = open(os.path.join(d, "cooking.properties"), encoding="latin-1").read()
    K.check(str(JClass(PKG + "CookP3Mig").MARK) in t, "P3 a fresh file carries the P3 marker")
    open(os.path.join(d, "cooking.properties"), "w", encoding="latin-1", newline="\n").write(t.replace("\nxp.Food_Pie_Meat=2750\n", "\nxp.Food_Pie_Meat=7\n"))
    Cfg.load()
    K.check(int(Cfg.xpFor("Food_Pie_Meat")) == 7, "P3 a hand-edited xp line is read as it is")
    K.notes.append("P3 load: %s" % r[:200])
    K.save()


def run_pm(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Paths = JClass("java.nio.file.Paths")
    Cfg, M = JClass(PKG + "CookCfg"), JClass(PKG + "CookP3Mig")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyCookTest")
    OLDT = old_text()
    NEWT = str(Cfg.DEFAULTS)
    tab = p3_table()
    K.check("xp.Food_Pie_Meat=25900" in OLDT and "xp.Food_Pie_Meat=2750" in NEWT, "PM the 0.1.14 / 0.1.15 default files read from their jars")

    def start(d):
        Cfg.FILE = Paths.get(os.path.join(d, "cooking.properties"))
        JClass(PKG + "CfgHist").DIR = None
        JClass(PKG + "CfgRows").HOME = None
        JClass(PKG + "CfgLog").FILE = None
        JClass(PKG + "CfgLog").Q.clear()
        return str(M.migrate())
    for tag, nl in (("lf", "\n"), ("crlf", "\r\n")):
        d = os.path.join(scratch, "pm", tag)
        os.makedirs(d)
        open(os.path.join(d, "cooking.properties"), "wb").write(OLDT.replace("\n", nl).encode("latin-1"))
        s0 = snapd(d)
        r1 = start(d)
        s1 = snapd(d)
        got = s1["cooking.properties"].decode("latin-1")
        want = NEWT.replace("# SkyyCooking 0.1.15 - cooking.properties", "# SkyyCooking 0.1.14 - cooking.properties", 1).replace("\n", nl)
        K.check(got == want, "PM %s: the 0.1.14 default file -> the 0.1.15 one (header line aside)" % tag)
        K.check(sum(1 for k in s1 if k.startswith("config-history/") and s1[k] == s0["cooking.properties"]) == 1, "PM %s: History holds the old file" % tag)
        lg = s1.get("config-changes.log", b"").decode("latin-1")
        K.check(lg.count("\txp[") == 44 and "Undo" not in lg[:0], "PM %s: 44 change-log rows (%d)" % (tag, lg.count("\txp[")))
        K.check("0.1.15 Balance P3" in r1, "PM %s INFO: %s" % (tag, r1[:160]))
        K.check(start(d) == "" and snapd(d) == s1, "PM %s: start 2 writes nothing" % tag)
        Cfg.load()
        K.check(all(int(Cfg.xpFor(k)) == v for k, v in tab.items()), "PM %s: the migrated file pays the P3 table" % tag)
    d = os.path.join(scratch, "pm", "hand")
    os.makedirs(d)
    open(os.path.join(d, "cooking.properties"), "wb").write(OLDT.replace("\nxp.Food_Bread=9100\n", "\nxp.Food_Bread=12345\n").encode("latin-1"))
    r = start(d)
    t = open(os.path.join(d, "cooking.properties"), encoding="latin-1").read()
    K.check("\nxp.Food_Bread=12345\n" in t and "\nxp.Food_Pie_Meat=2750\n" in t and "kept (custom)" in r, "PM a hand-set line kept + noted, the rest moved")
    d = os.path.join(scratch, "pm", "fresh")
    os.makedirs(d)
    open(os.path.join(d, "cooking.properties"), "wb").write(NEWT.encode("latin-1"))
    s0 = snapd(d)
    K.check(start(d) == "" and snapd(d) == s0, "PM a fresh 0.1.15 file is untouched")
    d = os.path.join(scratch, "pm", "none")
    os.makedirs(d)
    K.check(start(d) == "" and snapd(d) == {}, "PM no file -> nothing")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Paths = JClass("java.nio.file.Paths")
    Cfg = JClass(PKG + "CookCfg")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyCookTest")
    tab = p3_table()

    def start():
        Cfg.FILE = Paths.get(os.path.join(home, "cooking.properties"))
        rs = dict((m, str(JClass(PKG + m).migrate())) for m in MIGS)
        rs["load"] = str(Cfg.load())
        return rs
    t0 = open(os.path.join(home, "cooking.properties"), encoding="latin-1").read()
    old = dict((m.group(1), m.group(2)) for m in re.finditer(r"^xp\.(\w+)=(\S+)\s*$", t0, re.M))
    s0 = snapd(home)
    r1 = start()
    s1 = snapd(home)
    r2 = start()
    s2 = snapd(home)
    ch1 = sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k))
    K.check(all(k == "cooking.properties" or k == "config-changes.log" or k.startswith("config-history/") for k in ch1), "LIVE start 1 changes only the config + History: %s" % ch1)
    M = JClass(PKG + "CookP3Mig")
    olds = dict((str(k)[3:], str(v)) for k, v in zip(M.KEYS, M.OLDS))
    moved = [k for k, v in old.items() if k in olds and v == olds[k]]
    kept = [k for k, v in old.items() if k in olds and v != olds[k] and k in tab and v != str(tab[k])]
    K.check(all(int(Cfg.xpFor(k)) == tab[k] for k in moved) and all(str(Cfg.xpFor(k)) == old[k] for k in kept),
            "LIVE every xp line on its 0.1.14 default now pays P3 (%d), every custom line kept (%d: %s)" % (len(moved), len(kept), kept[:6]))
    K.check(s1 == s2 and r2["CookP3Mig"] == "", "LIVE start 2 writes nothing")
    K.notes.append("LIVE CookP3Mig: %s" % r1["CookP3Mig"][:400])
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyCooking", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["CookP3Mig"],
           phases=[("p3", run_p3), ("pm", run_pm), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyCooking"))
