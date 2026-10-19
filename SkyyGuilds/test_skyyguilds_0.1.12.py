"""Harness for SkyyGuilds 0.1.12 (tools/guilds_0_1_12_patch.py): NO XP CAPS - xpMaxPerCheck default 10,000,000 -> 0 (0 = no cap, new) +
the one-time GNcMig update of an existing config.properties. Skyy 2026-10-18 (docs/answered/skills.md 'NO XP CAPS'): "is there a cap on
acrobatics xp gain? or any other xp gain? if so remove all caps".
Build first: python tools/guilds_0_1_12_patch.py && python SkyyGuilds/build_skyyguilds_0.1.12.py

    python SkyyGuilds/test_skyyguilds_0.1.12.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.1.11 -> 0.1.12: only the expected members differ (GCfg default + loader clamp, the kit row, XpTask.check, the plugin's
                setup + version texts), GNcMig added, non-class entries: manifest.json only
  MIG  GNcMig.update (pure text step) on every shape (old default LF / CRLF / spaced, hand-set kept + noted, already 0 silent, no line ->
       marker at the end, empty file, duplicates, the last entry decides, a continued entry, a commented-out line, a file ending inside a
       continued entry, a marked file); migrate() on real scratch files: the old default -> 0 (CRLF kept), a verified config-history copy,
       one config-changes.log update line, second start = nothing; a hand edit kept; GCfg.load then reads 0 (the old jar clamped 0 to 1)
  CAP  the real XpTask.check (a guild of one, skill:fn:xp stand-in on the bridge): +50,000,000 skill XP in one check -> +5,000,000 guild
       XP (10 %) with the default 0; a cap set by hand (10,000,000) still limits to +1,000,000
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import skyybuild as B

VERSION, OLD = "0.1.12", "0.1.11"
JAR = os.path.join(HERE, "SkyyGuilds-%s.jar" % VERSION)
OLD_JAR = os.path.join(HERE, "SkyyGuilds-%s.jar" % OLD)
PKG = "com.skyy.guilds."
SCRATCH = HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "xpc", "guilds"))
# every diff checked by hand 2026-10-19: the version texts (CfgFn / CfgRows.header / the default file head / the ready line - which also
# carries the shared kit's current id), the 10000000 -> 0 default and the 1 -> 0 floor (GCfg field + parse, the kit row default + min,
# the default file + its marker line), XpTask.check's "MAX_DELTA > 0 &&" and setup()'s GNcMig.migrate call
EXPECT = {
    "CfgFn": ["~m opExport"],
    "CfgRows": ["~<clinit>", "~m header"],
    "GCfg": ["~<clinit>", "~m load", "~m parse"],
    "SkyyGuildsPlugin": ["~m setup"],
    "XpTask": ["~m check"],
}


def run_mig(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar])
    Paths = JClass("java.nio.file.Paths")
    Cfg, GS, Mig = JClass(PKG + "GCfg"), JClass(PKG + "GuildStore"), JClass(PKG + "GNcMig")
    GS.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyGuildsTest")
    MK = str(Mig.MARK)
    K.eq((str(Mig.KEY), str(Mig.OLD), str(Mig.NEW), str(Mig.WHO)), ("xpMaxPerCheck", "10000000", "0", "SkyyGuilds 0.1.12"), "MIG: key / old / new / who")

    def upd(t):
        r = Mig.update(t)
        return None if r is None else (str(r[0]), str(r[1]), None if r[2] is None else str(r[2]), [str(x) for x in r[3]], None if r[4] is None else str(r[4]))
    KY = "xpMaxPerCheck"
    CH = [KY, "10000000", "0"]
    CHG = KY + " 10000000 -> 0"
    KEPT = KY + "=%s kept (custom) - the 0.1.12 default is 0 (no cap)"
    cases = []
    for nl in ("\n", "\r\n"):
        src = ("a=1\n# help\n" + KY + "=10000000\nb=2\n").replace("\n", nl)
        exp = ("a=1\n# help\n" + MK + "\n" + KY + "=0\nb=2\n").replace("\n", nl)
        cases.append(("old default %r" % nl, upd(src), (exp, CHG, None, CH, "10000000")))
    cases.append(("spaced separator", upd(KY + " = 10000000\n"), (MK + "\n" + KY + " = 0\n", CHG, None, CH, "10000000")))
    for v in ("2000000", "1", "10000001"):
        cases.append(("custom %s kept" % v, upd("x=1\n%s=%s\n" % (KY, v)), ("x=1\n" + MK + "\n%s=%s\n" % (KY, v), "", KEPT % v, [], v)))
    cases.append(("already 0 silent", upd(KY + "=0\n"), (MK + "\n" + KY + "=0\n", "", None, [], "0")))
    cases.append(("no line -> marker at the end", upd("a=1\nb=2\n"), ("a=1\nb=2\n" + MK + "\n", "", None, [], None)))
    cases.append(("no line, CRLF, no final break", upd("a=1\r\nb=2"), ("a=1\r\nb=2\r\n" + MK + "\r\n", "", None, [], None)))
    cases.append(("empty file", upd(""), (MK + "\n", "", None, [], None)))
    cases.append(("two old lines", upd("%s=10000000\n%s=10000000\n" % (KY, KY)), (MK + "\n%s=0\n%s=0\n" % (KY, KY), CHG, None, CH, "10000000")))
    cases.append(("last entry custom wins", upd("%s=10000000\n%s=9\n" % (KY, KY)), (MK + "\n%s=10000000\n%s=9\n" % (KY, KY), "", KEPT % "9", [], "9")))
    cases.append(("continued entry kept", upd(KY + "=1000\\\n0000\n"), (MK + "\n" + KY + "=1000\\\n0000\n", "", KEPT % "10000000", [], "10000000")))
    cases.append(("commented-out line is no entry", upd("#%s=10000000\n" % KY), ("#%s=10000000\n" % KY + MK + "\n", "", None, [], None)))
    cases.append(("dangling continuation at the end -> marker on top", upd("a=1\nb=2\\\n"), (MK + "\na=1\nb=2\\\n", "", None, [], None)))
    cases.append(("marked file untouched", upd("x=1\n" + MK + "\n" + KY + "=10000000\n"), None))
    bad = [(n, g, e) for n, g, e in cases if g != e]
    for b in bad[:4]:
        print("   MIG", b[0], "got", repr(b[1])[:300], "want", repr(b[2])[:300])
    K.check(not bad, "MIG: GNcMig.update, %d cases: wrong %s" % (len(cases), [b[0] for b in bad]))

    def run_file(tag, data):
        d = os.path.join(scratch, "mig-" + tag)
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        p = os.path.join(d, "config.properties")
        open(p, "wb").write(data)
        Cfg.FILE = Paths.get(p)
        return d, p, str(Mig.migrate())
    old_b = ("# SkyyGuilds 0.1.11 settings.\r\nxpSharePercent=10\r\n# Most skill XP one member can add in one check (guards against admin XP "
             "commands); the rest of that jump is ignored.\r\nxpMaxPerCheck=10000000\r\nlevelBase=100\r\n").encode("latin-1")
    d, p, m1 = run_file("old", old_b)
    new_b = open(p, "rb").read()
    want_b = old_b.replace(b"xpMaxPerCheck=10000000", MK.encode("ascii") + b"\r\nxpMaxPerCheck=0")
    K.check(new_b == want_b, "MIG file: old default -> 0, marker above it, CRLF and every other byte kept: %r" % new_b[:400])
    K.check(CHG in m1, "MIG file: INFO line names the change: %s" % m1)
    hist = []
    for r_, ds_, fs_ in os.walk(d):
        for f_ in fs_:
            if f_.endswith(".bak") and "config-history" in r_:
                hist.append(open(os.path.join(r_, f_), "rb").read())
    K.check(hist == [old_b], "MIG file: config-history holds exactly one copy = the old bytes (%d copies)" % len(hist))
    lp = os.path.join(d, "config-changes.log")
    log = open(lp, encoding="latin-1").read() if os.path.isfile(lp) else ""
    K.check(log.count("\tupdate\txpMaxPerCheck\t10000000\t0\tok") == 1 and "SkyyGuilds 0.1.12" in log, "MIG file: one Undo-able change-log line: %r" % log[-300:])
    m2 = str(Mig.migrate())
    K.check(m2 == "" and open(p, "rb").read() == new_b, "MIG file: second start changes nothing (run-once marker): %r" % m2)
    Cfg.load()
    K.eq(int(Cfg.MAX_DELTA), 0, "MIG file: GCfg.load reads the migrated 0 (no longer clamped to 1)")
    d, p, m3 = run_file("custom", b"xpSharePercent=10\nxpMaxPerCheck=2500000\n")
    K.check(open(p, "rb").read() == ("xpSharePercent=10\n" + MK + "\nxpMaxPerCheck=2500000\n").encode("ascii") and "changed by hand" in m3 and "kept (custom)" in m3,
            "MIG file: a hand-set 2500000 is kept, only the marker added, and logged: %r" % m3)
    Cfg.load()
    K.eq(int(Cfg.MAX_DELTA), 2500000, "MIG file: the hand-set cap stays in force")
    # a fresh file (GCfg.load writes the defaults): 0 + the marker, so the update never rewrites it
    d = os.path.join(scratch, "fresh")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    Cfg.FILE = Paths.get(os.path.join(d, "config.properties"))
    K.eq(str(Mig.migrate()), "", "MIG fresh: no file = nothing")
    Cfg.load()
    t = open(os.path.join(d, "config.properties"), "rb").read()
    K.check(b"\nxpMaxPerCheck=0\n" in t and MK.encode("ascii") in t and int(Cfg.MAX_DELTA) == 0, "MIG fresh: the default file says xpMaxPerCheck=0 with the marker")
    K.check(str(Mig.migrate()) == "" and open(os.path.join(d, "config.properties"), "rb").read() == t, "MIG fresh: the next start leaves it alone")
    K.save()


def run_cap(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar])
    Paths, UUID, Long = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("java.lang.Long")
    System, CHM = JClass("java.lang.System"), JClass("java.util.concurrent.ConcurrentHashMap")
    GS, Cfg, X = JClass(PKG + "GuildStore"), JClass(PKG + "GCfg"), JClass(PKG + "XpTask")
    GS.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyGuildsTest")
    BR = CHM()
    System.getProperties().put("skyy.bridge", BR)
    XP = {}

    @JImplements("java.util.function.Function")
    class SkillXp:
        @JOverride
        def apply(self, a):
            return Long.valueOf(XP.get(str(a[1]).strip().lower(), 0))
    fn = SkillXp()
    BR.put("skill:fn:xp", fn)
    d = os.path.join(scratch, "cap")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(os.path.join(d, "guilds"))
    GS.DIR, GS.GDIR = Paths.get(d), Paths.get(os.path.join(d, "guilds"))
    Cfg.FILE = Paths.get(os.path.join(d, "config.properties"))
    Cfg.load()
    K.eq((int(Cfg.MAX_DELTA), int(Cfg.SHARE)), (0, 10), "CAP: defaults xpMaxPerCheck 0, xpSharePercent 10")
    u = UUID(0x6d11d, 1)
    g = JClass(PKG + "Guild")()
    g.id, g.name, g.tag, g.created = "g1", "Cap Guild", "CAP", int(System.currentTimeMillis())
    m = JClass(PKG + "GMember")()
    m.uuid, m.uid, m.name, m.rank, m.joined = str(u), u, "Steve", 2, int(System.currentTimeMillis())
    g.members.put(m.uuid, m)
    GS.GUILDS.put("g1", g)
    GS.BYNAME.put("cap guild", "g1")
    GS.BYPLAYER.put(str(u), "g1")
    XP["mining"] = 1000
    first = int(X.check(u))
    XP["mining"] = 1000 + 50000000
    gain = int(X.check(u))
    K.eq((first, gain, int(g.xp)), (0, 5000000, 5000000), "CAP: first check = baseline, +50M skill XP -> +5M guild XP (no cap)")
    Cfg.MAX_DELTA = 10000000
    XP["mining"] = XP["mining"] + 50000000
    K.eq(int(X.check(u)), 1000000, "CAP: a cap set by hand (10M) still limits the jump to +1M guild XP")
    K.save()


HK.run(name="SkyyGuilds", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["GNcMig"],
       phases=[("mig", run_mig), ("cap", run_cap)], script=__file__)
