"""Harness for SkyyCooking 0.1.16 (tools/cooking_0_1_16_patch.py): ING_TIER v3 - every raw ingredient has a tier (tier_tags ladder) + CookV3Mig.
Build first: python tools/cooking_0_1_16_patch.py && python SkyyCooking/build_skyycooking_0.1.16.py

    python SkyyCooking/test_skyycooking_0.1.16.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.1.15 -> 0.1.16: + CookV3Mig; CookCfg's table constants; the plugin's setup; the kit's version texts
  IT   EXECUTED the build's own table code (the generated script up to the v3 table, Assets.zip read): every raw ingredient of every
       Cooking Bench recipe resolves to a tier, the documented rows, the Tropical Smoothie's chain = T13 (Mango), its XP the jar's
  V3   EXECUTED CookCfg.load on a fresh file: CookCfg.xpFor = the v3 table; exactly CookV3Mig's keys moved vs the 0.1.15 jar's default file,
       every other line the same; the Tropical Smoothie / fruit / milk dishes pay more; a hand-edited line is read as is
  VM   CookV3Mig.migrate end to end on scratch copies of the 0.1.15 default file (LF + CRLF): every moved xp line on its 0.1.15 default -> v3,
       the help line reworded, the marker, History copy, one change-log row per line, start 2 nothing, a hand-set line kept, a fresh 0.1.16
       file untouched, no file = nothing
  LIVE every one-time update in setup() order + CookCfg.load on a scratch COPY of the live Skyy_SkyyCooking (NewBetaTest), twice
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import skyybuild as B

VERSION, OLD = "0.1.16", "0.1.15"
JAR = os.path.join(HERE, "SkyyCooking-%s.jar" % VERSION)
OLD_JAR = os.path.join(HERE, "SkyyCooking-%s.jar" % OLD)
PKG = "com.skyy.cooking."
SCRATCH = HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "cook016", "h"))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyCooking")
EXPECT = {
    "CfgFn": ["~m opExport"],
    "CfgRows": ["~<clinit>", "~m header"],
    "CookCfg": ["~<clinit>", "~m load"],   # the v3 table constants + the version text in load's INFO
    "CookIngMig": ["~m migrate"], "CookMig": ["~m logLine", "~m migrate"], "CookTblMig": ["~m migrate"], "CookXpMig": ["~m migrate"],
    "CookNcMig": ["~m migrate"], "CookP3Mig": ["~m migrate"],   # the version text (WHO) only, as in every round
    "SkyyCookingPlugin": ["~m setup"],
    "SupCfg": ["~m load"],
}
MIGS = ("CookMig", "CookXpMig", "CookTblMig", "CookIngMig", "CookNcMig", "CookP3Mig", "CookV3Mig")
SMOOTHIE = "Food_Skyy_Tropical_Smoothie"


def table(t):
    return dict((m.group(1), int(m.group(2))) for m in re.finditer(r"^xp\.(\w+)=(\d+)\r?$", t, re.M) if m.group(1) != "default")


def new_text():
    from jpype import JClass
    return str(JClass(PKG + "CookCfg").DEFAULTS)


def old_text():
    from jpype import JClass, JArray
    arr = JArray(JClass("java.net.URL"))(2)
    arr[0] = JClass("java.io.File")(OLD_JAR).toURI().toURL()
    arr[1] = JClass("java.io.File")(B.SERVER_JAR).toURI().toURL()
    ld = JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getPlatformClassLoader())
    return str(JClass(PKG + "CookCfg", loader=ld).DEFAULTS)


def snapd(d):
    return dict((os.path.relpath(os.path.join(r, f), d).replace(os.sep, "/"), open(os.path.join(r, f), "rb").read()) for r, ds, fs in os.walk(d) for f in fs)


def run_it(out, jar, scratch, _home):
    """the build's own table code, executed (no JVM): the generated script up to the section after the v3 table"""
    K = HK.Child(out)
    src = open(os.path.join(HERE, "build_skyycooking_%s.py" % VERSION), encoding="utf-8").read()
    cut = src.index("# 0.1.1 CAMPFIRE ACCESSORY")
    cut = src.rindex("# =====", 0, cut)
    g = {"__name__": "skyycook_it", "__file__": os.path.join(HERE, "build_skyycooking_%s.py" % VERSION)}
    cwd, argv = os.getcwd(), sys.argv
    os.chdir(HERE)
    sys.argv = ["build"]
    try:
        exec(compile(src[:cut], "build_skyycooking_%s.py" % VERSION, "exec"), g)
    finally:
        os.chdir(cwd)
        sys.argv = argv
    COOK, T, XP3, XPV = g["COOK"], g["ING_TIER_V3"], g["XP_P3"], g["XP_V3"]
    raw = set(i for o in COOK for k, i, n in COOK[o][0] if not (k == "I" and i in COOK))
    K.check(raw == set(T) and all(isinstance(T[i], int) and 1 <= T[i] <= 15 for i in raw), "IT every raw ingredient of every recipe has a tier (%d)" % len(raw))
    own = g["OWN_IDS"]
    K.check(len(own) == 23 and all(i in T for o in own for k, i, n in COOK[o][0] if not (k == "I" and i in COOK)), "IT every own dish ingredient resolves (23 dishes)")
    import tier_tags as TT
    K.check(all(T[i] == TT.tier(i) for i in raw if TT.tier(i)), "IT every tier_tags row is used as it is (the one tier table)")
    K.check((T["Plant_Fruit_Mango"], T["Plant_Fruit_Coconut"], T["Plant_Crop_Tomato_Item"], T["Plant_Crop_Turnip_Item"], T["Plant_Fruit_Apple"],
             T["Plant_Fruit_Pinkberry"], T["Plant_Fruit_Berries_Red"], T["Milk_Bucket"]) == (13, 4, 9, 6, 2, 13, 1, 2),
            "IT Mango 13 / Coconut 4 / Tomato 9 / Turnip 6 / Apple 2 / Pinkberry 13 / Red Berries 1 / Milk 2")
    K.check(g["V3_T"][SMOOTHIE] == 13 and g["P3_T"][SMOOTHIE] == 1 and XP3[SMOOTHIE] == 200 and XPV[SMOOTHIE] == 11400,
            "IT Tropical Smoothie: chain tier T1 -> T13, XP 200 -> %d" % XPV[SMOOTHIE])
    K.check(XPV["Food_Kebab_Vegetable"] == XP3["Food_Kebab_Vegetable"] == 100 and XPV["Food_Pie_Meat"] == XP3["Food_Pie_Meat"] == 2750,
            "IT K's rate routes unchanged (skewer 100, meat pie 2750)")
    moved = sorted(k for k in XPV if XPV[k] != XP3[k])
    K.check(moved == sorted(g["V3_KEYS"]) and len(moved) == 17, "IT 17 crafts moved: %s" % moved)
    K.notes.append("IT moved: " + ", ".join("%s %d->%d" % (k, XP3[k], XPV[k]) for k in moved))
    K.save()


def run_v3(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Paths = JClass("java.nio.file.Paths")
    Cfg, M = JClass(PKG + "CookCfg"), JClass(PKG + "CookV3Mig")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyCookTest")
    d = os.path.join(scratch, "v3")
    os.makedirs(d, exist_ok=True)
    Cfg.FILE = Paths.get(os.path.join(d, "cooking.properties"))
    r = str(Cfg.load())
    tab, old = table(new_text()), table(old_text())
    ids = [str(x) for x in Cfg.XP_IDS]
    vals = [int(x) for x in Cfg.XP_VALS]
    K.check(dict(zip(ids, vals)) == tab and len(tab) == 44 and sorted(old) == sorted(tab), "V3 compiled XP_IDS / XP_VALS = the default file's xp lines (%d)" % len(tab))
    K.check(all(int(Cfg.xpFor(k)) == v for k, v in tab.items()), "V3 CookCfg.xpFor pays the v3 table on a fresh file")
    keys = [str(x)[3:] for x in M.KEYS]
    K.check(sorted(k for k in tab if tab[k] != old[k]) == sorted(keys) and [str(x) for x in M.OLDS] == [str(old[k]) for k in keys]
            and [str(x) for x in M.NEWS] == [str(tab[k]) for k in keys], "V3 exactly CookV3Mig's %d keys moved vs the 0.1.15 jar" % len(keys))
    K.check(old[SMOOTHIE] == 200 and tab[SMOOTHIE] == 11400 and tab["Food_Skyy_Pinkberry_Milkshake"] > old["Food_Skyy_Pinkberry_Milkshake"]
            and tab["Food_Skyy_Coconut_Cream_Pie"] > old["Food_Skyy_Coconut_Cream_Pie"] and tab["Food_Pie_Apple"] > old["Food_Pie_Apple"]
            and tab["Food_Skyy_Butter"] > old["Food_Skyy_Butter"], "V3 fruit / milk dishes pay their tier (Smoothie 200 -> %d)" % tab[SMOOTHIE])
    K.check(int(Cfg.xpFor("Food_Skyy_No_Such_Dish")) == int(Cfg.XP_DEFAULT) == 1000, "V3 an unknown output pays xp.default 1000")
    K.check(float(Cfg.XP_MULT) == 0.5 and int(Cfg.MAX_PER_MIN) == 0, "V3 xpMultiplier 0.5, maxXpPerMinute 0 unchanged")
    t = open(os.path.join(d, "cooking.properties"), encoding="latin-1").read()
    K.check(str(M.MARK) in t and str(JClass(PKG + "CookP3Mig").MARK) in t and "5% per zone above 1" in t, "V3 a fresh file carries both markers + the new help line")
    open(os.path.join(d, "cooking.properties"), "w", encoding="latin-1", newline="\n").write(t.replace("\nxp.%s=11400\n" % SMOOTHIE, "\nxp.%s=7\n" % SMOOTHIE))
    Cfg.load()
    K.check(int(Cfg.xpFor(SMOOTHIE)) == 7, "V3 a hand-edited xp line is read as it is")
    K.notes.append("V3 load: %s" % r[:200])
    K.save()


def run_vm(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Paths = JClass("java.nio.file.Paths")
    Cfg, M = JClass(PKG + "CookCfg"), JClass(PKG + "CookV3Mig")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyCookTest")
    OLDT, NEWT = old_text(), new_text()
    tab = table(NEWT)
    n = len(M.KEYS)
    K.check(("xp.%s=200" % SMOOTHIE) in OLDT and ("xp.%s=11400" % SMOOTHIE) in NEWT and n == 17, "VM the 0.1.15 / 0.1.16 default files read from their jars")

    def start(d):
        Cfg.FILE = Paths.get(os.path.join(d, "cooking.properties"))
        JClass(PKG + "CfgHist").DIR = None
        JClass(PKG + "CfgRows").HOME = None
        JClass(PKG + "CfgLog").FILE = None
        JClass(PKG + "CfgLog").Q.clear()
        return str(M.migrate())
    for tag, nl in (("lf", "\n"), ("crlf", "\r\n")):
        d = os.path.join(scratch, "vm", tag)
        os.makedirs(d)
        open(os.path.join(d, "cooking.properties"), "wb").write(OLDT.replace("\n", nl).encode("latin-1"))
        s0 = snapd(d)
        r1 = start(d)
        s1 = snapd(d)
        got = s1["cooking.properties"].decode("latin-1")
        want = NEWT.replace("# SkyyCooking 0.1.16 - cooking.properties", "# SkyyCooking 0.1.15 - cooking.properties", 1).replace("\n", nl)
        K.check(got == want, "VM %s: the 0.1.15 default file -> the 0.1.16 one (header line aside)" % tag)
        K.check(sum(1 for k in s1 if k.startswith("config-history/") and s1[k] == s0["cooking.properties"]) == 1, "VM %s: History holds the old file" % tag)
        lg = s1.get("config-changes.log", b"").decode("latin-1")
        K.check(lg.count("\txp[") == n, "VM %s: %d change-log rows (%d)" % (tag, n, lg.count("\txp[")))
        K.check("0.1.16 ingredient tiers v3" in r1, "VM %s INFO: %s" % (tag, r1[:160]))
        K.check(start(d) == "" and snapd(d) == s1, "VM %s: start 2 writes nothing" % tag)
        Cfg.load()
        K.check(all(int(Cfg.xpFor(k)) == v for k, v in tab.items()), "VM %s: the migrated file pays the v3 table" % tag)
    d = os.path.join(scratch, "vm", "hand")
    os.makedirs(d)
    open(os.path.join(d, "cooking.properties"), "wb").write(OLDT.replace("\nxp.%s=200\n" % SMOOTHIE, "\nxp.%s=12345\n" % SMOOTHIE).encode("latin-1"))
    r = start(d)
    t = open(os.path.join(d, "cooking.properties"), encoding="latin-1").read()
    K.check(("\nxp.%s=12345\n" % SMOOTHIE) in t and "\nxp.Food_Pie_Apple=%d\n" % tab["Food_Pie_Apple"] in t and "kept (custom)" in r, "VM a hand-set line kept + noted, the rest moved")
    d = os.path.join(scratch, "vm", "fresh")
    os.makedirs(d)
    open(os.path.join(d, "cooking.properties"), "wb").write(NEWT.encode("latin-1"))
    s0 = snapd(d)
    K.check(start(d) == "" and snapd(d) == s0, "VM a fresh 0.1.16 file is untouched")
    d = os.path.join(scratch, "vm", "none")
    os.makedirs(d)
    K.check(start(d) == "" and snapd(d) == {}, "VM no file -> nothing")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Paths = JClass("java.nio.file.Paths")
    Cfg = JClass(PKG + "CookCfg")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyCookTest")
    tab = table(new_text())

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
    M, P3 = JClass(PKG + "CookV3Mig"), JClass(PKG + "CookP3Mig")
    p3 = dict((str(k)[3:], (str(o), str(n))) for k, o, n in zip(P3.KEYS, P3.OLDS, P3.NEWS))
    eff = dict((k, p3[k][1] if k in p3 and v == p3[k][0] else v) for k, v in old.items())   # a line still on 0.1.14 = CookP3Mig moves it first
    olds = dict((str(k)[3:], str(v)) for k, v in zip(M.KEYS, M.OLDS))
    moved = [k for k, v in eff.items() if k in olds and v == olds[k]]
    kept = [k for k, v in eff.items() if k in olds and v != olds[k] and k in tab and v != str(tab[k])]
    old = eff
    K.check(all(int(Cfg.xpFor(k)) == tab[k] for k in moved) and all(str(Cfg.xpFor(k)) == old[k] for k in kept),
            "LIVE every xp line on its 0.1.15 default now pays v3 (%d), every custom line kept (%d: %s)" % (len(moved), len(kept), kept[:6]))
    t1 = s1["cooking.properties"].decode("latin-1")
    K.check(str(M.MARK) in t1 and ("\r\n" in t0) == ("\r\n" in t1), "LIVE the marker is in, line endings kept")
    K.check(s1 == s2 and r2["CookV3Mig"] == "" and r2["CookP3Mig"] == "", "LIVE start 2 writes nothing")
    K.notes.append("LIVE CookV3Mig: %s" % r1["CookV3Mig"][:400])
    K.notes.append("LIVE moved %d, kept %d" % (len(moved), len(kept)))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyCooking", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["CookV3Mig"],
           phases=[("it", run_it), ("v3", run_v3), ("vm", run_vm), ("live", run_live), ("live2", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyCooking"))
