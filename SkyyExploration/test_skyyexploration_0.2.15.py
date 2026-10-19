"""Harness for SkyyExploration 0.2.15 (tools/exploration_0_2_15_patch.py): NO XP CAPS - chunks.maxPaidPerWorld default 25,000 -> 0 (0 = no
cap, new meaning) + the one-time ExpNcMig update of an existing config.properties. Skyy 2026-10-18 (docs/answered/skills.md 'NO XP CAPS'):
"is there a cap on acrobatics xp gain? or any other xp gain? if so remove all caps".
Build first: python tools/exploration_0_2_15_patch.py && python SkyyExploration/build_skyyexploration_0.2.15.py

    python SkyyExploration/test_skyyexploration_0.2.15.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.2.14 -> 0.2.15: only the expected members differ (ExpCfg default + loader, the kit row, ExpStore.addChunk, the /explore
                card line, the plugin's setup + version texts), ExpNcMig added, non-class entries: manifest.json only
  MIG  ExpNcMig.update (pure text step) on every shape (old default LF / CRLF / spaced, hand-set kept + noted, a hand-set 0 kept with the
       'meaning changed' note, no line -> marker at the end, empty file, duplicates, the last entry decides, a continued entry, a
       commented-out line, a file ending inside a continued entry, a marked file); migrate() on real scratch files: the old default -> 0
       (CRLF kept), a verified config-history copy, one config-changes.log update line, second start = nothing; a hand edit kept;
       ExpCfg.load then reads 0; a fresh default file carries 0 + the marker (left alone)
  CAP  the real ExpStore.addChunk: 30,000 new chunks in one world all pay with the default 0 (the old cap stopped at 25,000); a cap set by
       hand (5) still stops paying after 5 (later chunks recorded, paid 0)
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import skyybuild as B

VERSION, OLD = "0.2.15", "0.2.14"
JAR = os.path.join(HERE, "SkyyExploration-%s.jar" % VERSION)
OLD_JAR = os.path.join(HERE, "SkyyExploration-%s.jar" % OLD)
PKG = "com.skyy.explore."
SCRATCH = HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "xpc", "expl"))
# every diff checked by hand 2026-10-19: the version texts (CfgFn / CfgRows.header / the default file head / ExpLgMig's WHO), the
# 25000 -> 0 default (ExpCfg field + apply, the kit row default + help, the default file + its marker line), addChunk's "CHUNK_CAP <= 0 ||",
# the /explore card's "every new chunk pays here", setup()'s ExpNcMig.migrate call - and LgReveal's hub tab list, which the rebuild takes
# from the shared kit (skyyui now lists the Storage and Supplies hubs; not this round's change)
EXPECT = {
    "CfgFn": ["~m opExport"],
    "CfgRows": ["~<clinit>", "~m header"],
    "ExpCfg": ["~<clinit>", "~m apply", "~m load"],
    "ExpLgMig": ["~m logLine", "~m migrate"],
    "ExpStore": ["~m addChunk"],
    "ExplorePage": ["~m overview"],
    "LgReveal": ["~<clinit>"],
    "SkyyExplorationPlugin": ["~m setup"],
}


def run_mig(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar])
    Paths = JClass("java.nio.file.Paths")
    Cfg, Mig = JClass(PKG + "ExpCfg"), JClass(PKG + "ExpNcMig")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyExpTest")
    MK = str(Mig.MARK)
    KY = "chunks.maxPaidPerWorld"
    K.eq((str(Mig.KEY), str(Mig.OLD), str(Mig.NEW), str(Mig.WHO)), (KY, "25000", "0", "SkyyExploration 0.2.15"), "MIG: key / old / new / who")

    def upd(t):
        r = Mig.update(t)
        return None if r is None else (str(r[0]), str(r[1]), None if r[2] is None else str(r[2]), [str(x) for x in r[3]], None if r[4] is None else str(r[4]))
    CH = [KY, "25000", "0"]
    CHG = KY + " 25000 -> 0"
    KEPT = KY + "=%s kept (custom) - the 0.2.15 default is 0 (no cap)"
    ZERO = KY + "=0 kept (custom) - it meant 'no chunk pays XP' before 0.2.15; 0 now means NO cap (set chunks.xp=0 to switch chunk XP off)"
    cases = []
    for nl in ("\n", "\r\n"):
        src = ("chunks.xp=60\n" + KY + "=25000\nchunks.payWhileGliding=true\n").replace("\n", nl)
        exp = ("chunks.xp=60\n" + MK + "\n" + KY + "=0\nchunks.payWhileGliding=true\n").replace("\n", nl)
        cases.append(("old default %r" % nl, upd(src), (exp, CHG, None, CH, "25000")))
    cases.append(("spaced separator", upd(KY + " = 25000\n"), (MK + "\n" + KY + " = 0\n", CHG, None, CH, "25000")))
    for v in ("50000", "1", "25001"):
        cases.append(("custom %s kept" % v, upd("x=1\n%s=%s\n" % (KY, v)), ("x=1\n" + MK + "\n%s=%s\n" % (KY, v), "", KEPT % v, [], v)))
    cases.append(("hand-set 0 kept with the meaning note", upd(KY + "=0\n"), (MK + "\n" + KY + "=0\n", "", ZERO, [], "0")))
    cases.append(("no line -> marker at the end", upd("a=1\nb=2\n"), ("a=1\nb=2\n" + MK + "\n", "", None, [], None)))
    cases.append(("no line, CRLF, no final break", upd("a=1\r\nb=2"), ("a=1\r\nb=2\r\n" + MK + "\r\n", "", None, [], None)))
    cases.append(("empty file", upd(""), (MK + "\n", "", None, [], None)))
    cases.append(("two old lines", upd("%s=25000\n%s=25000\n" % (KY, KY)), (MK + "\n%s=0\n%s=0\n" % (KY, KY), CHG, None, CH, "25000")))
    cases.append(("last entry custom wins", upd("%s=25000\n%s=9\n" % (KY, KY)), (MK + "\n%s=25000\n%s=9\n" % (KY, KY), "", KEPT % "9", [], "9")))
    cases.append(("continued entry kept", upd(KY + "=250\\\n00\n"), (MK + "\n" + KY + "=250\\\n00\n", "", KEPT % "25000", [], "25000")))
    cases.append(("commented-out line is no entry", upd("#%s=25000\n" % KY), ("#%s=25000\n" % KY + MK + "\n", "", None, [], None)))
    cases.append(("dangling continuation at the end -> marker on top", upd("a=1\nb=2\\\n"), (MK + "\na=1\nb=2\\\n", "", None, [], None)))
    cases.append(("marked file untouched", upd("x=1\n" + MK + "\n" + KY + "=25000\n"), None))
    bad = [(n, g, e) for n, g, e in cases if g != e]
    for b in bad[:4]:
        print("   MIG", b[0], "got", repr(b[1])[:300], "want", repr(b[2])[:300])
    K.check(not bad, "MIG: ExpNcMig.update, %d cases: wrong %s" % (len(cases), [b[0] for b in bad]))

    def run_file(tag, data):
        d = os.path.join(scratch, "mig-" + tag)
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        p = os.path.join(d, "config.properties")
        open(p, "wb").write(data)
        Cfg.FILE = Paths.get(p)
        return d, p, str(Mig.migrate())
    old_b = ("# head\r\nchunks.enabled=true\r\nchunks.xp=60\r\nchunks.zoneMult=1,1.5,2,3\r\n" + KY + "=25000\r\nchunks.payWhileGliding=true\r\n").encode("latin-1")
    d, p, m1 = run_file("old", old_b)
    new_b = open(p, "rb").read()
    want_b = old_b.replace((KY + "=25000").encode("ascii"), MK.encode("ascii") + b"\r\n" + (KY + "=0").encode("ascii"))
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
    K.check(log.count("\tupdate\t%s\t25000\t0\tok" % KY) == 1 and "SkyyExploration 0.2.15" in log, "MIG file: one Undo-able change-log line: %r" % log[-300:])
    m2 = str(Mig.migrate())
    K.check(m2 == "" and open(p, "rb").read() == new_b, "MIG file: second start changes nothing (run-once marker): %r" % m2)
    Cfg.load()
    K.eq(int(Cfg.CHUNK_CAP), 0, "MIG file: ExpCfg.load reads the migrated 0")
    d, p, m3 = run_file("custom", ("chunks.xp=60\n%s=40000\n" % KY).encode("ascii"))
    K.check(open(p, "rb").read() == ("chunks.xp=60\n" + MK + "\n%s=40000\n" % KY).encode("ascii") and "changed by hand" in m3 and "kept (custom)" in m3,
            "MIG file: a hand-set 40000 is kept, only the marker added, and logged: %r" % m3)
    Cfg.load()
    K.eq(int(Cfg.CHUNK_CAP), 40000, "MIG file: the hand-set cap stays in force")
    d, p, m4 = run_file("zero", ("chunks.xp=60\n%s=0\n" % KY).encode("ascii"))
    K.check(open(p, "rb").read() == ("chunks.xp=60\n" + MK + "\n%s=0\n" % KY).encode("ascii") and ZERO in m4,
            "MIG file: a hand-set 0 is kept and the changed meaning is logged: %r" % m4)
    # a fresh file (ExpCfg.load writes the defaults): 0 + the marker, so the update never rewrites it
    d = os.path.join(scratch, "fresh")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    Cfg.FILE = Paths.get(os.path.join(d, "config.properties"))
    K.eq(str(Mig.migrate()), "", "MIG fresh: no file = nothing")
    Cfg.load()
    fp = os.path.join(d, "config.properties")
    t = open(fp, "rb").read() if os.path.isfile(fp) else b""
    K.check((KY + "=0").encode("ascii") in t and MK.encode("ascii") in t and int(Cfg.CHUNK_CAP) == 0, "MIG fresh: the default file says %s=0 with the marker" % KY)
    K.check(str(Mig.migrate()) == "" and open(fp, "rb").read() == t, "MIG fresh: the next start leaves it alone")
    K.save()


def run_cap(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar])
    Paths = JClass("java.nio.file.Paths")
    Cfg, Sto = JClass(PKG + "ExpCfg"), JClass(PKG + "ExpStore")
    LOS = JClass("it.unimi.dsi.fastutil.longs.LongOpenHashSet")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyExpTest")
    d = os.path.join(scratch, "cap")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(os.path.join(d, "players"))
    Cfg.FILE = Paths.get(os.path.join(d, "config.properties"))
    Cfg.load()
    Sto.DIR = Paths.get(os.path.join(d, "players"))
    K.eq(int(Cfg.CHUNK_CAP), 0, "CAP: default chunks.maxPaidPerWorld 0")

    def data(key):
        x = JClass(PKG + "ExpData")()
        x.key = key
        x.chunks.put("w1", LOS())
        return x
    x = data("p1")
    paid = [int(Sto.addChunk(x, "w1", i, 60)) for i in range(30000)]
    K.check(all(v == 60 for v in paid) and int(x.owed) == 30000 * 60 and int(Sto.paidHere(x, "w1")) == 30000,
            "CAP: 30,000 new chunks all pay 60 XP with no cap (owed %d, paid here %d)" % (int(x.owed), int(Sto.paidHere(x, "w1"))))
    K.eq(int(Sto.addChunk(x, "w1", 5, 60)), -1, "CAP: a known chunk still pays nothing (-1)")
    Cfg.CHUNK_CAP = 5
    y = data("p2")
    got = [int(Sto.addChunk(y, "w1", i, 60)) for i in range(8)]
    K.eq(got, [60] * 5 + [0] * 3, "CAP: a cap set by hand (5) still stops paying (later chunks recorded, paid 0)")
    K.save()


HK.run(name="SkyyExploration", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["ExpNcMig"],
       phases=[("mig", run_mig), ("cap", run_cap)], script=__file__)
