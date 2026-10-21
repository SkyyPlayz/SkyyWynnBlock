"""Harness for SkyyExploration 0.3.2 (tools/exploration_0_3_2_patch.py): Balance P3 - Exploration XP x k on the new level list, zone
factors 1 / 4.91 / 12.15 / 22.59 / 36.23, ExpP3Mig. Build first: python tools/exploration_0_3_2_patch.py && python SkyyExploration/build_skyyexploration_0.3.2.py

    python SkyyExploration/test_skyyexploration_0.3.2.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.1 -> 0.3.2: + ExpP3Mig; ExpCfg's code defaults / five-zone check; the plugin's setup; version texts
  P3   EXECUTED ExpCfg.load on a fresh file: chestXp (Zone1 T3 = 51 x 1 x 2, Zone4 T4 = 51 x 22.59 x 3), chunkMult zones 1-5 + oceans 1,
       zoneXp rows, luggage / airdrop / spots; the zone multiplier check takes 5 numbers (4 refused); a file without the lines = the same
       (code defaults); ExpP3Mig.plan: the 0.3.1 default file -> the 0.3.2 one, admin values kept, CRLF, marker once; migrate end to end
       (History, change-log rows, start 2 nothing)
  LIVE ExpP3Mig.migrate + ExpCfg.load on a scratch COPY of the live Skyy_SkyyExploration (NewBetaTest), twice: start 1 changes only the
       config + History + change log, start 2 nothing
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import skyybuild as B

VERSION, OLD = "0.3.2", "0.3.1"
JAR = os.path.join(HERE, "SkyyExploration-%s.jar" % VERSION)
OLD_JAR = os.path.join(HERE, "SkyyExploration-%s.jar" % OLD)
PKG = "com.skyy.explore."
SCRATCH = HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "balp3", "expl"))
LIVE = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyExploration")
EXPECT = {"CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],
          "ExpCfg": ["~<clinit>", "~m apply", "~m check", "~m load"],   # the P3 code defaults, the five-zone check, the default text
          "ExpLgMig": ["~m logLine", "~m migrate"], "ExpNcMig": ["~m logLine", "~m migrate"],   # the version text (WHO) only
          "SkyyExplorationPlugin": ["~m setup"]}


def snapd(d):
    return dict((os.path.relpath(os.path.join(r, f), d).replace(os.sep, "/"), open(os.path.join(r, f), "rb").read()) for r, ds, fs in os.walk(d) for f in fs)


def old_text():
    from jpype import JClass, JArray
    arr = JArray(JClass("java.net.URL"))(2)
    arr[0] = JClass("java.io.File")(OLD_JAR).toURI().toURL()
    arr[1] = JClass("java.io.File")(B.SERVER_JAR).toURI().toURL()
    ld = JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getPlatformClassLoader())
    return str(JClass(PKG + "ExpCfg", loader=ld).DEFAULTS)


def reset(J):
    J("CfgHist").DIR = None
    J("CfgRows").HOME = None
    J("CfgLog").FILE = None
    J("CfgLog").Q.clear()


def run_p3(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    Cfg, M = J("ExpCfg"), J("ExpP3Mig")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyExpTest")
    Paths = JClass("java.nio.file.Paths")
    d = os.path.join(scratch, "p3", "fresh")
    os.makedirs(d)
    Cfg.FILE = Paths.get(os.path.join(d, "config.properties"))
    r = str(Cfg.load())
    K.check(int(Cfg.CHEST_BASE) == 51 and [float(x) for x in Cfg.CHEST_ZM] == [1.0, 4.91, 12.15, 22.59, 36.23] and int(Cfg.CHUNK_XP) == 8,
            "P3 a fresh file: chests.base 51, the five zone factors, chunks.xp 8")
    K.eq(int(Cfg.chestXp("Zone1_Encounters_Tier3")), 102, "P3 chestXp Zone1 T3 = 51 x 1 x 2")
    K.eq(int(Cfg.chestXp("Zone4_Encounters_Tier4")), round(51 * 22.59 * 3), "P3 chestXp Zone4 T4 = 51 x 22.59 x 3")
    K.eq([float(Cfg.chunkMult(x)) for x in ("Zone1_Tier1", "Zone2_Tier1", "Zone3_Tier2", "Zone4_Tier4", "Oceans")], [1.0, 4.91, 12.15, 22.59, 1.0],
         "P3 chunkMult by zone, oceans 1")
    K.check(int(Cfg.zoneXp("Zone1_Tier1")) == 64 and int(Cfg.zoneXp("Zone2_Tier1")) == 314 and int(Cfg.zoneXp("Zone4_Tier5")) == 21810,
            "P3 zone.xp rows: Zone1_Tier1 64, Zone2_Tier1 = 64 x 4.91, Zone4_Tier5 21810")
    K.check([float(x) for x in Cfg.LG_XP] == [19.0, 39.0, 77.0, 129.0] and int(Cfg.AIR_XP) == 193 and int(Cfg.SPOT_XP) == 64 and int(Cfg.SECRET_XP) == 193,
            "P3 luggage / airdrop / spot XP x k")
    K.check(Cfg.check("chests.zoneMult", "1,2,3,4,5") is None and Cfg.check("chests.zoneMult", "1,2,4,8") is not None, "P3 the zone multiplier check takes five numbers")
    t = open(os.path.join(d, "config.properties"), encoding="latin-1").read()
    K.check(str(M.MARK) in t and M.plan(JString(t)) is None, "P3 a fresh file carries the marker")
    # a file without the lines = the code defaults
    d2 = os.path.join(scratch, "p3", "bare")
    os.makedirs(d2)
    open(os.path.join(d2, "config.properties"), "w").write("chests.enabled=true\n")
    Cfg.FILE = Paths.get(os.path.join(d2, "config.properties"))
    Cfg.load()
    K.check(int(Cfg.CHEST_BASE) == 51 and int(Cfg.CHUNK_XP) == 8 and [float(x) for x in Cfg.CHUNK_ZM] == [1.0, 4.91, 12.15, 22.59, 36.23] and int(Cfg.ZONE_DEF) == 129,
            "P3 a file without the lines reads the P3 code defaults")
    # the update
    OLDT = old_text()
    NEWT = str(Cfg.DEFAULTS)
    pr = M.plan(JString(OLDT))
    got = str(pr[0]).replace("# SkyyExploration 0.3.1 - change", "# SkyyExploration 0.3.2 - change", 1)
    K.check(got == NEWT, "P3 ExpP3Mig.plan(the 0.3.1 default file) = the 0.3.2 default file (header aside)")
    K.check(len(pr[1]) // 3 == len(M.KEYS), "P3 one change-log row per key (%d)" % (len(pr[1]) // 3))
    hand = OLDT.replace("\nchunks.xp=60\n", "\nchunks.xp=75\n")
    pr2 = M.plan(JString(hand))
    K.check("\nchunks.xp=75\n" in str(pr2[0]) and "kept" in str(pr2[3]) and "\nchests.base=51\n" in str(pr2[0]), "P3 an admin's chunks.xp 75 kept (INFO), the rest moved")
    pr3 = M.plan(JString(OLDT.replace("\n", "\r\n")))
    K.check(str(pr3[0]) == str(pr[0]).replace("\n", "\r\n"), "P3 CRLF kept")
    for tag, txt in (("lf", OLDT), ("crlf", OLDT.replace("\n", "\r\n"))):
        dm = os.path.join(scratch, "p3", tag)
        os.makedirs(dm)
        open(os.path.join(dm, "config.properties"), "wb").write(txt.encode("latin-1"))
        Cfg.FILE = Paths.get(os.path.join(dm, "config.properties"))
        reset(J)
        s0 = snapd(dm)
        r1 = str(M.migrate())
        s1 = snapd(dm)
        K.check(s1["config.properties"].decode("latin-1") == (str(pr[0]) if tag == "lf" else str(pr3[0])), "P3 migrate %s: the planned file" % tag)
        K.check(sum(1 for k in s1 if k.startswith("config-history/") and s1[k] == s0["config.properties"]) == 1, "P3 migrate %s: History" % tag)
        lg = s1.get("config-changes.log", b"").decode("latin-1")
        K.check(lg.count("SkyyExploration 0.3.2") == len(M.KEYS) and "\tzone.xp[Zone1_Tier1]\t500\t64\tok" in lg, "P3 migrate %s: change-log rows" % tag)
        reset(J)
        K.check(str(M.migrate()) == "" and snapd(dm) == s1, "P3 migrate %s: start 2 nothing" % tag)
        Cfg.load()
        K.check(int(Cfg.chestXp("Zone1_Encounters_Tier3")) == 102, "P3 migrate %s: the migrated file pays the P3 numbers" % tag)
        K.check("0.3.2" in r1, "P3 migrate %s INFO: %s" % (tag, r1[:120]))
    K.notes.append("P3 load: %s" % r[:200])
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    Cfg = J("ExpCfg")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyExpTest")
    Cfg.FILE = JClass("java.nio.file.Paths").get(os.path.join(home, "config.properties"))

    def start():
        reset(J)
        rs = [str(J(m).migrate()) for m in ("ExpLgMig", "ExpNcMig", "ExpP3Mig")]
        Cfg.load()
        return rs
    s0 = snapd(home)
    r1 = start()
    s1 = snapd(home)
    r2 = start()
    s2 = snapd(home)
    ch = sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k))
    K.check(all(k == "config.properties" or k == "config-changes.log" or k.startswith("config-history/") for k in ch), "LIVE start 1 changes only the config + History: %s" % ch)
    K.check(s1 == s2 and r2[2] == "", "LIVE start 2 changes nothing")
    K.check(int(Cfg.chestXp("Zone1_Encounters_Tier3")) == 102 or "kept" in r1[2], "LIVE the live config pays the P3 chest XP (or an admin value was kept): %s" % r1[2][:200])
    K.notes.append("LIVE: %s" % r1[2][:300])
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyExploration", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["ExpP3Mig"],
           phases=[("p3", run_p3), ("live", run_live)], script=__file__, live=(LIVE, "Skyy_SkyyExploration"))
