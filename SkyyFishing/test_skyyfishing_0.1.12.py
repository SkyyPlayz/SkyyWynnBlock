"""Harness for SkyyFishing 0.1.12 (Balance P3 LIGHT: fish.xp.mult 1 -> 6 + FishP3Mig; tools/fishing_0_1_12_patch.py).
Build first: python tools/fishing_0_1_12_patch.py && python SkyyFishing/build_skyyfishing_0.1.12.py

    python SkyyFishing/test_skyyfishing_0.1.12.py [--dir <folder inside tools/dev/scratch/>] [--keep]

  A / C / AA  verify (-Xverify:all), class compare 0.1.11 -> 0.1.12 (+ FishP3Mig; the row default + version texts), engine-access audit
  P3    FishP3Mig.plan (old 1 / 1.0 -> 6, admin value kept, LAST entry decides, continued entry never rewritten, CRLF kept, marker = once,
        the fresh file carries it) and FishP3Mig.run end to end on scratch copies of the 0.1.11 default file (History copy, one change-log row,
        start 2 nothing, admin file only the marker, fresh file untouched, no file nothing); FishCfg.load then reads x6
  LIVE  FishP3Mig.run + FishCfg.load on a scratch COPY of the live Skyy_SkyyFishing (NewBetaTest), twice: start 1 changes only
        config.properties / History / change log, start 2 nothing; XP_MULT 6 unless the live file holds an admin value
Exit code 1 on any failure.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.12"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyFishing-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyFishing-0.1.11.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "balp3", "fish")))
PKG = "com.skyy.fishing."
EXPECT = {"CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "FishCfg": ["~<clinit>", "~m applyAll", "~m applyScalars", "~m seed"],
          "FishCmds": ["~m admin"], "SkyyFishingPlugin": ["~m setup"]}   # the x6 default (field init + loader fallback), the seeded text, the version texts
ADDED = ["FishP3Mig"]
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyFishing")


def snapd(d):
    return dict((os.path.relpath(os.path.join(r, f), d).replace(os.sep, "/"), open(os.path.join(r, f), "rb").read()) for r, ds, fs in os.walk(d) for f in fs)


def old_text():
    from jpype import JClass, JArray
    arr = JArray(JClass("java.net.URL"))(2)
    arr[0] = JClass("java.io.File")(OLD_JAR).toURI().toURL()
    arr[1] = JClass("java.io.File")(B.SERVER_JAR).toURI().toURL()
    ld = JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getPlatformClassLoader())
    return str(JClass(PKG + "FishCfg", loader=ld).DEFAULT_TEXT)


def boot():
    from jpype import JClass
    J = lambda n: JClass(PKG + n)
    J("FishLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyFishTest")
    return J


def reset(J):
    J("CfgHist").DIR = None
    J("CfgRows").HOME = None
    J("CfgLog").FILE = None
    J("CfgLog").Q.clear()


def run_p3(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    J = boot()
    M, Cfg = J("FishP3Mig"), J("FishCfg")
    S = lambda x: JString(x)
    MARK = str(M.MARK)
    OLDT, NEWT = old_text(), str(Cfg.DEFAULT_TEXT)
    K.check("\nfish.xp.mult=1\n" in OLDT and "\nfish.xp.mult=6\n" in NEWT and MARK in NEWT and M.plan(S(NEWT)) is None, "P3 the default files: 0.1.11 x1, 0.1.12 x6 + marker")
    for old in ("1", "1.0"):
        r = M.plan(S("a=1\nfish.xp.mult=%s\nb=2\n" % old))
        K.check(str(r[0]) == "a=1\nfish.xp.mult=6\nb=2\n" + MARK + "\n" and str(r[1]) == old, "P3 plan: %s -> 6, marker at the end" % old)
    r = M.plan(S("fish.xp.mult=2.5\n"))
    K.check(str(r[0]) == "fish.xp.mult=2.5\n" + MARK + "\n" and r[1] is None and "kept" in str(r[2]), "P3 plan: an admin's 2.5 kept (INFO)")
    r = M.plan(S("fish.xp.mult=1\nfish.xp.mult=3\n"))
    K.check(r[1] is None, "P3 plan: the LAST entry decides")
    r = M.plan(S("fish.xp.mult=1\\\n.0\n"))
    K.check(r[1] is None and "fish.xp.mult=1\\\n.0\n" in str(r[0]), "P3 plan: a continued entry is never rewritten")
    r = M.plan(S("x=1\r\nfish.xp.mult=1\r\n"))
    K.check(str(r[0]) == "x=1\r\nfish.xp.mult=6\r\n" + MARK + "\r\n", "P3 plan: CRLF kept")
    K.check(str(M.plan(S("x=1"))[0]) == "x=1\n" + MARK + "\n", "P3 plan: no line, no final newline -> only the marker")
    for tag, txt in (("lf", OLDT), ("crlf", OLDT.replace("\n", "\r\n"))):
        mods = os.path.join(scratch, "p3", tag)
        d = os.path.join(mods, "Skyy_SkyyFishing")
        os.makedirs(d)
        open(os.path.join(d, "config.properties"), "wb").write(txt.encode("latin-1"))
        reset(J)
        s0 = snapd(d)
        r1 = str(M.run(JClass("java.nio.file.Paths").get(mods)))
        s1 = snapd(d)
        nl = "\r\n" if tag == "crlf" else "\n"
        want = txt.replace("fish.xp.mult=1" + nl, "fish.xp.mult=6" + nl)
        want = want + ("" if want.endswith(nl) else nl) + MARK + nl
        K.check(s1["config.properties"].decode("latin-1") == want, "P3 run %s: x6 + the marker, every other byte kept" % tag)
        K.check(sum(1 for k in s1 if k.startswith("config-history/") and s1[k] == s0["config.properties"]) == 1, "P3 run %s: History holds the old file" % tag)
        lg = s1.get("config-changes.log", b"").decode("latin-1")
        K.check(lg.count("\tfish.xp.mult\t1\t6\tok") == 1, "P3 run %s: one change-log row: %r" % (tag, lg.strip()[-120:]))
        K.check("1 -> 6" in r1, "P3 run %s INFO: %s" % (tag, r1))
        reset(J)
        K.check(str(M.run(JClass("java.nio.file.Paths").get(mods))) == "" and snapd(d) == s1, "P3 run %s: start 2 changes nothing" % tag)
        Cfg.load(JClass("java.nio.file.Paths").get(mods))
        K.check(float(Cfg.XP_MULT) == 6.0, "P3 run %s: FishCfg.load reads x6" % tag)
    mods = os.path.join(scratch, "p3", "fresh")
    os.makedirs(mods)
    reset(J)
    Paths = JClass("java.nio.file.Paths")
    K.check(str(M.run(Paths.get(mods))) == "" and snapd(mods) == {}, "P3 run: no file -> nothing")
    Cfg.load(Paths.get(mods))
    t = open(os.path.join(mods, "Skyy_SkyyFishing", "config.properties"), "rb").read()
    reset(J)
    K.check(str(M.run(Paths.get(mods))) == "" and open(os.path.join(mods, "Skyy_SkyyFishing", "config.properties"), "rb").read() == t and float(Cfg.XP_MULT) == 6.0,
            "P3 a fresh 0.1.12 file (seeded by FishCfg.load) is never migrated, x6")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    J = boot()
    Paths = JClass("java.nio.file.Paths")
    mods = os.path.dirname(home)
    t0 = open(os.path.join(home, "config.properties"), encoding="latin-1").read()

    def start():
        reset(J)
        r = str(J("FishP3Mig").run(Paths.get(mods)))
        J("FishCfg").load(Paths.get(mods))
        return r
    s0 = snapd(home)
    r1 = start()
    s1 = snapd(home)
    r2 = start()
    s2 = snapd(home)
    ch = sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k))
    K.check(all(k == "config.properties" or k == "config-changes.log" or k.startswith("config-history/") for k in ch), "LIVE start 1 changes only the config + History: %s" % ch)
    K.check(s1 == s2 and r2 == "", "LIVE start 2 changes nothing")
    hand = "\nfish.xp.mult=1\n" not in t0.replace("\r\n", "\n") and "\nfish.xp.mult=1.0\n" not in t0.replace("\r\n", "\n") and "fish.xp.mult=" in t0
    K.check(float(J("FishCfg").XP_MULT) == 6.0 or hand, "LIVE x%s (an admin's value kept: %s)" % (J("FishCfg").XP_MULT, hand))
    K.notes.append("LIVE: %s" % r1[:300])
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyFishing", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("p3", run_p3), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyFishing"))
