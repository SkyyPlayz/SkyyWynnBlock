"""Harness for SkyyCooking 0.1.13 (tools/cooking_0_1_13_patch.py): NO XP CAPS - maxXpPerMinute default 1,500,000 -> 0 (= no cap) + the
one-time CookNcMig update of an existing cooking.properties. Skyy 2026-10-18 (docs/answered/skills.md 'NO XP CAPS'): "is there a cap on
acrobatics xp gain? or any other xp gain? if so remove all caps".
Build first: python tools/cooking_0_1_13_patch.py && python SkyyCooking/build_skyycooking_0.1.13.py

    python SkyyCooking/test_skyycooking_0.1.13.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.1.12 -> 0.1.13: only the expected members differ (CookCfg defaults, the kit row default, the plugin's setup + version
                texts), CookNcMig added, non-class entries: manifest.json only
  MIG  CookNcMig.update (pure text step) on every shape: old default LF / CRLF / spaced separator, marker above the help comment, hand-set
       values kept + noted, already 0 silent, no line -> marker only, duplicates, the last entry decides, a continued entry, a commented-out
       line, a marked file untouched; migrate() on real scratch files: the old default -> 0 with the marker (CRLF kept byte for byte), a
       verified config-history copy of the old bytes, one config-changes.log update line, second start = nothing; a hand edit kept
       (only the marker added); CookCfg.load then reads 0
  CAP  a fresh default file -> CookCfg.MAX_PER_MIN 0; allowXp / allowXpPart pay every amount (several 100M batches in one minute); a cap
       set by hand (1000) still limits (the window logic is unchanged)
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import skyybuild as B

VERSION, OLD = "0.1.13", "0.1.12"
JAR = os.path.join(HERE, "SkyyCooking-%s.jar" % VERSION)
OLD_JAR = os.path.join(HERE, "SkyyCooking-%s.jar" % OLD)
PKG = "com.skyy.cooking."
SCRATCH = HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "xpc", "cook"))
# every diff checked by hand 2026-10-19: the version texts ("0.1.12" -> "0.1.13" in CfgFn / CfgRows.header / the *Mig WHO / SupCfg's
# file head / the ready line), the 1500000 -> 0 default (CookCfg field + loader fallback, the kit row, the default file + its marker
# line) and setup()'s CookNcMig.migrate call
EXPECT = {
    "CfgFn": ["~m opExport"],
    "CfgRows": ["~<clinit>", "~m header"],
    "CookCfg": ["~<clinit>", "~m load"],
    "CookIngMig": ["~m migrate"],
    "CookMig": ["~m logLine", "~m migrate"],
    "CookTblMig": ["~m migrate"],
    "CookXpMig": ["~m migrate"],
    "SkyyCookingPlugin": ["~m setup"],
    "SupCfg": ["~m load"],
}


def run_mig(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar])
    Paths = JClass("java.nio.file.Paths")
    Cfg, Mig = JClass(PKG + "CookCfg"), JClass(PKG + "CookNcMig")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyCookTest")
    MK = str(Mig.MARK)
    K.eq((str(Mig.KEY), str(Mig.OLD), str(Mig.NEW)), ("maxXpPerMinute", "1500000", "0"), "MIG: key / old / new")

    def upd(t):
        r = Mig.update(t)
        return None if r is None else (str(r[0]), str(r[1]), None if r[2] is None else str(r[2]), [str(x) for x in r[3]], None if r[4] is None else str(r[4]))
    CH = ["maxXpPerMinute", "1500000", "0"]
    KEPT = "maxXpPerMinute=%s kept (custom) - the 0.1.13 default is 0 (no cap)"
    cases = []
    for nl in ("\n", "\r\n"):
        src = "a=1\n# help\nmaxXpPerMinute=1500000\nb=2\n".replace("\n", nl)
        exp = ("a=1\n" + MK + "\n# help\nmaxXpPerMinute=0\nb=2\n").replace("\n", nl)
        cases.append(("old default %r" % nl, upd(src), (exp, "maxXpPerMinute 1500000 -> 0", None, CH, "1500000")))
    cases.append(("spaced separator", upd("maxXpPerMinute = 1500000\n"), (MK + "\nmaxXpPerMinute = 0\n", "maxXpPerMinute 1500000 -> 0", None, CH, "1500000")))
    for v in ("2000000", "1", "1500001"):
        cases.append(("custom %s kept" % v, upd("x=1\nmaxXpPerMinute=%s\n" % v), ("x=1\n" + MK + "\nmaxXpPerMinute=%s\n" % v, "", KEPT % v, [], v)))
    cases.append(("already 0 silent", upd("maxXpPerMinute=0\n"), (MK + "\nmaxXpPerMinute=0\n", "", None, [], "0")))
    cases.append(("no line -> marker above the first entry", upd("a=1\nb=2\n"), (MK + "\na=1\nb=2\n", "", None, [], None)))
    cases.append(("empty file", upd(""), (MK + "\n", "", None, [], None)))
    cases.append(("two old lines", upd("maxXpPerMinute=1500000\nmaxXpPerMinute=1500000\n"),
                  (MK + "\nmaxXpPerMinute=0\nmaxXpPerMinute=0\n", "maxXpPerMinute 1500000 -> 0", None, CH, "1500000")))
    cases.append(("last entry custom wins", upd("maxXpPerMinute=1500000\nmaxXpPerMinute=9\n"),
                  (MK + "\nmaxXpPerMinute=1500000\nmaxXpPerMinute=9\n", "", KEPT % "9", [], "9")))
    cases.append(("continued entry kept", upd("maxXpPerMinute=15\\\n00000\n"), (MK + "\nmaxXpPerMinute=15\\\n00000\n", "", KEPT % "1500000", [], "1500000")))
    cases.append(("commented-out line is no entry (marker above the comment on top of the first entry)", upd("#maxXpPerMinute=1500000\na=1\n"),
                  (MK + "\n#maxXpPerMinute=1500000\na=1\n", "", None, [], None)))
    cases.append(("marked file untouched", upd("x=1\n" + MK + "\nmaxXpPerMinute=1500000\n"), None))
    bad = [(n, g, e) for n, g, e in cases if g != e]
    for b in bad[:4]:
        print("   MIG", b[0], "got", repr(b[1])[:300], "want", repr(b[2])[:300])
    K.check(not bad, "MIG: CookNcMig.update, %d cases: wrong %s" % (len(cases), [b[0] for b in bad]))

    # migrate() on real files (the kit's History + change log in the file's folder)
    def run_file(tag, data):
        d = os.path.join(scratch, "mig-" + tag)
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        p = os.path.join(d, "cooking.properties")
        open(p, "wb").write(data)
        Cfg.FILE = Paths.get(p)
        m = str(Mig.migrate())
        return d, p, m
    old_b = ("# SkyyCooking 0.1.12 - cooking.properties\r\nenabled=true\r\nxpMultiplier=0.5\r\n"
             "# safety net: base Cooking XP per player per minute (counted before xpMultiplier); 0 = off. The dish is always given.\r\n"
             "maxXpPerMinute=1500000\r\nmessages=true\r\n").encode("latin-1")
    d, p, m1 = run_file("old", old_b)
    new_b = open(p, "rb").read()
    want_b = old_b.replace(b"# safety net:", MK.encode("ascii") + b"\r\n# safety net:").replace(b"maxXpPerMinute=1500000", b"maxXpPerMinute=0")
    K.check(new_b == want_b, "MIG file: old default -> 0, marker above the help line, CRLF and every other byte kept: %r" % new_b[:400])
    K.check("maxXpPerMinute 1500000 -> 0" in m1, "MIG file: INFO line names the change: %s" % m1)
    hist = []
    for r_, ds_, fs_ in os.walk(d):
        for f_ in fs_:
            if f_.endswith(".bak") and "config-history" in r_:
                hist.append(open(os.path.join(r_, f_), "rb").read())
    K.check(hist == [old_b], "MIG file: config-history holds exactly one copy = the old bytes (%d copies)" % len(hist))
    lp = os.path.join(d, "config-changes.log")
    log = open(lp, encoding="latin-1").read() if os.path.isfile(lp) else ""
    K.check(log.count("\tupdate\tmaxXpPerMinute\t1500000\t0\tok") == 1 and "SkyyCooking 0.1.13" in log, "MIG file: one Undo-able change-log line: %r" % log[-300:])
    m2 = str(Mig.migrate())
    K.check(m2 == "" and open(p, "rb").read() == new_b, "MIG file: second start changes nothing (run-once marker): %r" % m2)
    s = str(Cfg.load())
    K.eq(int(Cfg.MAX_PER_MIN), 0, "MIG file: CookCfg.load reads the migrated 0 (%s)" % s[:80])
    d, p, m3 = run_file("custom", b"enabled=true\nmaxXpPerMinute=2500000\n")
    K.check(open(p, "rb").read() == ("enabled=true\n" + MK + "\nmaxXpPerMinute=2500000\n").encode("ascii") and "changed by hand" in m3 and "kept (custom)" in m3,
            "MIG file: a hand-set 2500000 is kept, only the marker added, and logged: %r" % m3)
    lp = os.path.join(d, "config-changes.log")
    K.check(not os.path.isfile(lp) or "maxXpPerMinute" not in open(lp, encoding="latin-1").read(), "MIG file: a kept value writes no change-log line")
    Cfg.load()
    K.eq(int(Cfg.MAX_PER_MIN), 2500000, "MIG file: the hand-set cap stays in force")
    K.save()


def run_cap(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar])
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    Cfg, Cook = JClass(PKG + "CookCfg"), JClass(PKG + "Cook")
    d = os.path.join(scratch, "cap")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    Cfg.FILE = Paths.get(os.path.join(d, "cooking.properties"))
    Cfg.load()
    t = open(os.path.join(d, "cooking.properties"), encoding="latin-1").read()
    K.check("\nmaxXpPerMinute=0\n" in t and str(JClass(PKG + "CookNcMig").MARK) in t, "CAP: a fresh cooking.properties says maxXpPerMinute=0 and carries the marker")
    K.eq((int(Cfg.MAX_PER_MIN), int(Cfg.DEF_MAX_PER_MIN)), (0, 0), "CAP: field + loader fallback 0")
    u = UUID.randomUUID()
    K.check(all(bool(Cook.allowXp(u, 300000000)) for _ in range(5)), "CAP: 5 dishes of 300M base XP in one minute are all paid")
    K.eq([int(Cook.allowXpPart(u, 200000000)) for _ in range(3)], [200000000] * 3, "CAP: Campfire batches pay in full")
    Cfg.MAX_PER_MIN = 1000
    u2 = UUID.randomUUID()
    K.eq((bool(Cook.allowXp(u2, 900)), bool(Cook.allowXp(u2, 200)), int(Cook.allowXpPart(u2, 500))), (True, False, 100), "CAP: a cap set by hand still limits")
    K.save()


HK.run(name="SkyyCooking", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["CookNcMig"],
       phases=[("mig", run_mig), ("cap", run_cap)], script=__file__)
