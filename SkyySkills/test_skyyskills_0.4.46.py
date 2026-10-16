"""SkyySkills 0.4.46 - harness for round logfix (the asset-pack checks WARN only after the last try; tools/skills_0_4_46_patch.py).
Build first: python tools/skills_0_4_46_patch.py && python SkyySkills/build_skyyskills_0.4.46.py

    python SkyySkills/test_skyyskills_0.4.46.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (each a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.4.45 -> 0.4.46: ManaGuard packTick -> packStep + the 4 *_PEND fields; the version texts; non-class entries: manifest.json only
  PK  EXECUTED on the real ManaGuard (the real packReport / intReport / manaReport / armReport2 make the answers; the log is captured
      through HytaleLoggerBackend.subscribe):
      P1 vanilla first, then Skyy: tries 1-2 read "Hytale:Hytale wins" / the vanilla Mana stat / staffs from Hytale -> NO log line, not
         done; try 3 reads Skyy's packs -> 4 INFO "active" lines, no WARN, the check is done (a later call logs nothing)
      P2 never turns: tries 1-5 log nothing; try 6 (PACK_MAX) -> exactly 4 WARNs (the same texts 0.4.45 logged at once), then nothing
      P3 mixed: items turn good at try 2 (INFO then), the Mana stat stays wrong (WARN at try 6), the interactions read wrong once then
         become unreadable (the remembered WARN at try 6), no staff to check ("skip": no line)
      P4 packTick in a bare JVM (nothing readable): the old 4 "not checked" INFO lines after PACK_MAX tries, no WARN
Exit code 1 on any failure.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

VERSION = "0.4.46"
PKG = "com.skyy.skills."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.45.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "logfix", "sk")))
ADDED = []
EXPECT = {"ManaGuard": ["+f ARM_PEND", "+f INT_PEND", "+f MANA_PEND", "+f PACK_PEND", "+m packStep", "~<clinit>", "~m packTick",
                        "~m armReport2", "~m intReport", "~m packReport"],
          # version texts (each checked by the compare: only the version constant differs)
          "SkillCfg": ["~m load"], "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"], "SkyySkillsPlugin": ["~m setup"]}


def run_pack(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString, JFloat
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    BK = JClass("com.hypixel.hytale.logger.backend.HytaleLoggerBackend")
    cap = JClass("java.util.concurrent.CopyOnWriteArrayList")()
    BK.subscribe(cap)
    Cfg, MG, MC = JClass(PKG + "SkillCfg"), JClass(PKG + "ManaGuard"), JClass(PKG + "ManaCost")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    MINE = str(MG.PACK)
    VAN = "Hytale:Hytale"
    ARMP = "Skyy:0.1.30 SkyyArmory"

    def logs():
        o = []
        for r in cap:
            m = str(r.getMessage())
            if "[SkyySkills]" in m:
                o.append((str(r.getLevel()), m))
        cap.clear()
        return o

    def reset():
        MG.PACK_TRIES = 0
        for f in ("PACK_DONE", "ITEMS_DONE", "INT_DONE", "MANA_DONE", "ARM_DONE"):
            setattr(MG, f, False)
        for f in ("PACK_LAST", "INT_LAST", "MANA_LAST", "ARM_LAST", "PACK_PEND", "INT_PEND", "MANA_PEND", "ARM_PEND"):
            setattr(MG, f, "")
        logs()

    S = lambda xs: JArray(JString)(xs)
    nI, nT, nA = len(MC.IDS), len(MC.INT_IDS), len(MC.ARM_IDS)
    goodLive = JArray(JFloat)([float(x) for x in MC.INT_NEW])

    def items(p):
        return MG.packReport(S([p] * nI))

    def ints(p):
        return MG.intReport(S([p] * nT), goodLive)

    def mana(ok):
        if ok:
            return MG.manaReport(JArray(JFloat)([float(MG.MANA_MAX), 0.0, float(MG.MANA_PS), 1.0 if MG.MANA_PAUSE else 0.0]), MINE)
        return MG.manaReport(JArray(JFloat)([100.0, 100.0, 0.0, 0.0]), VAN)   # the vanilla Mana stat (the live 2026-10-16 WARN)

    def arm(p):
        return MG.armReport2(S([p] * nA), S([None] * nA))

    bad = [items(VAN), ints(VAN), mana(False), arm(VAN)]
    good = [items(MINE), ints(MINE), mana(True), arm(ARMP)]
    K.check([str(x[0]) for x in bad] == ["warn"] * 4 and [str(x[0]) for x in good] == ["info"] * 4,
            "the real reports: vanilla winners = 4 x warn, Skyy's packs = 4 x info (%s / %s)" % ([str(x[0]) for x in bad], [str(x[0]) for x in good]))
    K.eq(int(MG.PACK_MAX), 6, "PACK_MAX unchanged")
    K.eq(int(MG.START_S), 10, "START_S unchanged")

    # ============================================================================ P1 vanilla first, then Skyy
    reset()
    for t in (1, 2):
        MG.packStep(*bad)
        lg = logs()
        K.check(not lg and not bool(MG.PACK_DONE) and not bool(MG.ITEMS_DONE) and not bool(MG.MANA_DONE),
                "P1 try %d: vanilla still wins (packs loading) -> no log line, not done: %s" % (t, lg))
    K.check(str(MG.PACK_PEND).startswith("Spell costs") and "NOT active" in str(MG.PACK_PEND) and "NOT the one in effect" in str(MG.MANA_PEND),
            "P1 the WARN texts are only remembered")
    MG.packStep(*good)
    lg = logs()
    K.check(len(lg) == 4 and all(l == "INFO" for l, _m in lg) and sum("active" in m for _l, m in lg) >= 3 and "come from " + ARMP in lg[3][1],
            "P1 try 3: Skyy's packs won -> 4 INFO lines (active), no WARN: %s" % [(l, m[:70]) for l, m in lg])
    K.check(bool(MG.PACK_DONE) and "item overrides are active" in str(MG.PACK_LAST) and "interaction overrides are active" in str(MG.INT_LAST),
            "P1 done; *_LAST = the INFO texts")
    MG.packStep(*bad)
    K.eq(logs(), [], "P1 a stray later call logs nothing")

    # ============================================================================ P2 never turns
    reset()
    for t in range(1, 6):
        MG.packStep(*bad)
        lg = logs()
        K.check(not lg and not bool(MG.PACK_DONE), "P2 try %d of %d: no log line yet: %s" % (t, int(MG.PACK_MAX), lg))
    MG.packStep(*bad)
    lg = logs()
    want = sorted([str(bad[0][1]), str(bad[1][1]), str(bad[2][1]), str(bad[3][1])])
    K.check(len(lg) == 4 and all(l == "WARNING" for l, _m in lg) and sorted(m.replace("[SkyySkills] ", "", 1) for _l, m in lg) == want,
            "P2 try 6 (the last): exactly 4 WARNs, the same texts 0.4.45 logged at once: %s" % [(l, m[:70]) for l, m in lg])
    K.check(bool(MG.PACK_DONE) and str(MG.PACK_LAST) == str(bad[0][1]) and str(MG.MANA_LAST) == str(bad[2][1]), "P2 done; *_LAST = the WARN texts")
    MG.packStep(*bad)
    K.eq(logs(), [], "P2 nothing after the last try")

    # ============================================================================ P3 mixed
    reset()
    unread = MG.intReport(S([None] * nT), goodLive)
    skip = ["skip", ""]
    K.eq(str(unread[0]), "", "P3 an unreadable interaction map = '' (try again)")
    MG.packStep(bad[0], bad[1], bad[2], S(skip))
    K.eq(logs(), [], "P3 try 1: nothing logged (the staff check 'skip' is silent, as before)")
    K.check(bool(MG.ARM_DONE), "P3 'skip' = the staff check is done")
    MG.packStep(good[0], unread, bad[2], None)
    lg = logs()
    K.check(len(lg) == 1 and lg[0][0] == "INFO" and "item overrides are active" in lg[0][1] and bool(MG.ITEMS_DONE),
            "P3 try 2: the items turned good -> 1 INFO, done: %s" % [(l, m[:70]) for l, m in lg])
    for t in (3, 4, 5):
        MG.packStep(None, unread, bad[2], None)
        K.eq(logs(), [], "P3 try %d: nothing" % t)
    MG.packStep(None, unread, bad[2], None)
    lg = logs()
    K.check(len(lg) == 2 and all(l == "WARNING" for l, _m in lg) and any("NOT the one in effect" in m for _l, m in lg)
            and any("interaction overrides are NOT active" in m for _l, m in lg),
            "P3 try 6: the Mana WARN + the remembered interaction WARN (its later reads were unreadable): %s" % [(l, m[:70]) for l, m in lg])

    # ============================================================================ P4 packTick, nothing readable (a bare JVM)
    reset()
    for t in range(6):
        MG.packTick()
    lg = logs()
    K.check(len(lg) == 4 and all(l == "INFO" and "not checked" in m for l, m in lg) and bool(MG.PACK_DONE),
            "P4 packTick in a bare JVM: the old 4 'not checked' INFO lines after 6 tries, no WARN: %s" % [(l, m[:60]) for l, m in lg])
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("pack", run_pack)], script=__file__)
