"""Harness for SkyyGuilds 0.1.13 (tools/guilds_0_1_13_patch.py): BALANCE P5 - the guild level curve x20 (levelBase 100 -> 2000, levelStep
150 -> 3000) + the one-time GP5Mig update + the level report / one chat line per member of a re-scaled guild.
Build first: python tools/guilds_0_1_13_patch.py && python SkyyGuilds/build_skyyguilds_0.1.13.py

    python SkyyGuilds/test_skyyguilds_0.1.13.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  S    static   the patch re-runs to identical bytes, line endings kept, one class added, no new command / system
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.1.12 -> 0.1.13: only the expected members differ, GP5Mig added
  MIG  GP5Mig.update (pure text) on every shape: both old defaults LF / CRLF, one hand-set (kept + noted, the other moves), both custom,
       already new (silent), no lines (marker at the end), empty file, a continued entry, a commented-out line, a marked file;
       migrate() on real files: config-history copy, one change-log line per key, second start = nothing, GCfg.load reads 2000 / 3000;
       a fresh file carries the marker
  LVL  report() + tell() EXECUTED: a guild of 28,564 XP = level 20 on the old curve -> 5 on the new; INFO text; the member's one line
       goes out once (second touchN = nothing); a guild that keeps its level gets no notice; no update this start = no report
  live D  setup's order on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyGuilds: GNcMig -> GP5Mig -> GCfg.load -> loadAll -> report,
       only the planned keys change (Properties), each guild's old / new level printed; START TWICE: the second start changes nothing
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, shutil, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "balp5", "guilds")]
import harness_kit as HK
import skyybuild as B

VERSION, OLD = "0.1.13", "0.1.12"
JAR = os.path.join(HERE, "SkyyGuilds-%s.jar" % VERSION)
OLD_JAR = os.path.join(HERE, "SkyyGuilds-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyguilds_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyguilds_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "guilds_0_1_13_patch.py")
PKG = "com.skyy.guilds."
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyGuilds")
EXPECT = {
    "CfgFn": ["~m opExport"],
    "CfgRows": ["~<clinit>", "~m header"],
    "GCfg": ["~<clinit>", "~m load", "~m parse"],
    "GNcMig": ["~m logLine", "~m migrate"],   # its WHO = "SkyyGuilds " + VERSION (the version text inlined)
    "GuildStore": ["~m touchN"],
    "SkyyGuildsPlugin": ["~m setup"],
}


def _props(b):
    from jpype import JClass
    p = JClass("java.util.Properties")()
    p.load(JClass("java.io.ByteArrayInputStream")(b))
    return {str(k): str(p.getProperty(k)) for k in p.stringPropertyNames()}


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyGuilds 0.1.13 - build script') and g.count('VERSION = "0.1.13"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.eq(g.count("makeClass(") - o.count("makeClass("), 1, "S one class added (GP5Mig)")
    su = g[g.index("public void setup() {"):]
    K.check(su.index("GNcMig.migrate();") < su.index("GP5Mig.migrate();") < su.index("GCfg.load();") < su.index("loadAll();") < su.index("GP5Mig.report();"),
            "S setup order: GNcMig -> GP5Mig -> load -> loadAll -> report")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_mig(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar])
    Paths = JClass("java.nio.file.Paths")
    Cfg, GS, Mig = JClass(PKG + "GCfg"), JClass(PKG + "GuildStore"), JClass(PKG + "GP5Mig")
    GS.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyGuildsTest")
    MK = str(Mig.MARK)
    K.eq(([str(x) for x in Mig.KEYS], [str(x) for x in Mig.OLD], [str(x) for x in Mig.NEW], str(Mig.WHO)),
         (["levelBase", "levelStep"], ["100", "150"], ["2000", "3000"], "SkyyGuilds 0.1.13"), "MIG: keys / old / new / who")
    K.eq((int(Cfg.BASE), int(Cfg.STEP)), (2000, 3000), "MIG: field defaults 2000 / 3000")

    def upd(t):
        r = Mig.update(t)
        return None if r is None else (str(r[0]), str(r[1]), [str(x) for x in r[2]], [str(x) for x in r[3]])
    BOTH = "levelBase 100 -> 2000, levelStep 150 -> 3000"
    RB = ["levelBase", "100", "2000", "levelStep", "150", "3000"]
    cases = []
    for nl in ("\n", "\r\n"):
        src = ("a=1\n# curve\nlevelBase=100\nlevelStep=150\nb=2\n").replace("\n", nl)
        exp = ("a=1\n# curve\n" + MK + "\nlevelBase=2000\nlevelStep=3000\nb=2\n").replace("\n", nl)
        cases.append(("both old %r" % nl, upd(src), (exp, BOTH, [], RB)))
    cases.append(("base hand-set, step moves", upd("levelBase=500\nlevelStep=150\n"),
                  (MK + "\nlevelBase=500\nlevelStep=3000\n", "levelStep 150 -> 3000", ["levelBase=500 kept (custom) - the 0.1.13 (Balance P5) default is 2000"], ["levelStep", "150", "3000"])))
    cases.append(("both custom", upd("levelBase=1\nlevelStep=0\n"), (MK + "\nlevelBase=1\nlevelStep=0\n", "",
                  ["levelBase=1 kept (custom) - the 0.1.13 (Balance P5) default is 2000", "levelStep=0 kept (custom) - the 0.1.13 (Balance P5) default is 3000"], [])))
    cases.append(("already new silent", upd("levelBase=2000\nlevelStep=3000\n"), (MK + "\nlevelBase=2000\nlevelStep=3000\n", "", [], [])))
    cases.append(("spaced separator", upd("levelBase = 100\n"), (MK + "\nlevelBase = 2000\n", "levelBase 100 -> 2000", [], ["levelBase", "100", "2000"])))
    cases.append(("no lines -> marker at the end", upd("a=1\n"), ("a=1\n" + MK + "\n", "", [], [])))
    cases.append(("no final break CRLF", upd("a=1\r\nb=2"), ("a=1\r\nb=2\r\n" + MK + "\r\n", "", [], [])))
    cases.append(("empty file", upd(""), (MK + "\n", "", [], [])))
    cases.append(("last entry decides", upd("levelBase=100\nlevelBase=7\n"), (MK + "\nlevelBase=100\nlevelBase=7\n", "", ["levelBase=7 kept (custom) - the 0.1.13 (Balance P5) default is 2000"], [])))
    cases.append(("continued entry kept", upd("levelStep=1\\\n50\n"), (MK + "\nlevelStep=1\\\n50\n", "", ["levelStep=150 kept (custom) - the 0.1.13 (Balance P5) default is 3000"], [])))
    cases.append(("commented-out line", upd("#levelBase=100\n"), ("#levelBase=100\n" + MK + "\n", "", [], [])))
    cases.append(("marked file untouched", upd(MK + "\nlevelBase=100\n"), None))
    bad = [(n, g, e) for n, g, e in cases if g != e]
    for b in bad[:4]:
        print("   MIG", b[0], "got", repr(b[1])[:300], "want", repr(b[2])[:300])
    K.check(not bad, "MIG: GP5Mig.update, %d cases: wrong %s" % (len(cases), [b[0] for b in bad]))

    def run_file(tag, data):
        d = os.path.join(scratch, "mig-" + tag)
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        p = os.path.join(d, "config.properties")
        open(p, "wb").write(data)
        Cfg.FILE = Paths.get(p)
        Mig.OLD_BASE, Mig.OLD_STEP = -1, -1
        return d, p, str(Mig.migrate())
    old_b = b"# SkyyGuilds 0.1.12 settings.\r\nxpSharePercent=10\r\n# Guild level curve.\r\nlevelBase=100\r\nlevelStep=150\r\nmaxMembers=25\r\n"
    d, p, m1 = run_file("old", old_b)
    new_b = open(p, "rb").read()
    want_b = old_b.replace(b"levelBase=100\r\nlevelStep=150", MK.encode("ascii") + b"\r\nlevelBase=2000\r\nlevelStep=3000")
    K.check(new_b == want_b, "MIG file: both move, marker above, CRLF + every other byte kept: %r" % new_b[:300])
    K.check(BOTH in m1 and (int(Mig.OLD_BASE), int(Mig.OLD_STEP)) == (100, 150), "MIG file: INFO + OLD_BASE / OLD_STEP recorded: %s" % m1)
    hist = [open(os.path.join(r_, f_), "rb").read() for r_, _d, fs_ in os.walk(d) for f_ in fs_ if f_.endswith(".bak") and "config-history" in r_]
    K.check(hist == [old_b], "MIG file: config-history holds exactly the old bytes (%d copies)" % len(hist))
    log = open(os.path.join(d, "config-changes.log"), encoding="latin-1").read()
    K.check(log.count("\tupdate\tlevelBase\t100\t2000\tok") == 1 and log.count("\tupdate\tlevelStep\t150\t3000\tok") == 1 and "SkyyGuilds 0.1.13" in log,
            "MIG file: one Undo-able change-log line per key: %r" % log[-300:])
    K.check(str(Mig.migrate()) == "" and open(p, "rb").read() == new_b, "MIG file: second start changes nothing")
    Cfg.load()
    K.eq((int(Cfg.BASE), int(Cfg.STEP)), (2000, 3000), "MIG file: GCfg.load reads 2000 / 3000")
    d, p, m3 = run_file("custom", b"levelBase=500\nlevelStep=700\n")
    K.check(open(p, "rb").read() == (MK + "\nlevelBase=500\nlevelStep=700\n").encode("ascii") and "kept (custom)" in m3 and int(Mig.OLD_BASE) == -1,
            "MIG file: both hand-set kept, marker only, no report: %r" % m3)
    d = os.path.join(scratch, "fresh")
    os.makedirs(d, exist_ok=True)
    Cfg.FILE = Paths.get(os.path.join(d, "config.properties"))
    K.eq(str(Mig.migrate()), "", "MIG fresh: no file = nothing")
    Cfg.load()
    t = open(os.path.join(d, "config.properties"), "rb").read()
    K.check(b"\nlevelBase=2000\n" in t and b"\nlevelStep=3000\n" in t and MK.encode("ascii") in t, "MIG fresh: the default file says 2000 / 3000 with the marker")
    K.check(str(Mig.migrate()) == "" and open(os.path.join(d, "config.properties"), "rb").read() == t, "MIG fresh: the next start leaves it alone")
    K.save()


def run_lvl(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar])
    System, CHM, UUID = JClass("java.lang.System"), JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.util.UUID")
    System.getProperties().put("skyy.bridge", CHM())
    GS, Cfg, Mig = JClass(PKG + "GuildStore"), JClass(PKG + "GCfg"), JClass(PKG + "GP5Mig")
    GS.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyGuildsTest")
    K.eq((int(Mig.levelOn(28564, 100, 150)), int(Mig.levelOn(28564, 2000, 3000)), int(GS.levelInfo(28564)[0])), (20, 5, 5),
         "LVL: 28,564 guild XP = level 20 on the old curve, 5 on the new (GuildStore.levelInfo agrees)")
    K.eq([int(Mig.levelOn(x, 2000, 3000)) for x in (0, 1999, 2000, 26000, 126000)], [1, 1, 2, 5, 10], "LVL: new curve level 2 at 2,000, 5 at 26,000, 10 at 126,000")
    K.eq(str(Mig.report()), "", "LVL: no update this start = no report")
    now = int(System.currentTimeMillis())
    gs_ = []
    for gid, name, xp in (("g1", "GodSquad", 28564), ("g2", "Tiny", 50)):
        g = JClass(PKG + "Guild")()
        g.id, g.name, g.tag, g.created, g.xp = gid, name, "", now, xp
        GS.GUILDS.put(gid, g)
        gs_.append(g)
    u = UUID(0x6d11d, 7)
    m = JClass(PKG + "GMember")()
    m.uuid, m.uid, m.name, m.rank, m.joined = str(u), u, "Steve", 2, now
    gs_[0].members.put(m.uuid, m)
    GS.BYPLAYER.put(str(u), "g1")
    Mig.OLD_BASE, Mig.OLD_STEP = 100, 150
    rep = str(Mig.report())
    K.check("guild g1 'GodSquad' (28564 guild XP): level 20 -> 5" in rep and "guild g2 'Tiny' (50 guild XP): level 1 -> 1" in rep, "LVL: report lines: %r" % rep)
    K.check(Mig.NOTICE.containsKey("g1") and not Mig.NOTICE.containsKey("g2"), "LVL: only the guild that dropped levels gets a notice")
    K.check("is guild level 5 now (was 20)" in str(Mig.NOTE_TEXT.get("g1")), "LVL: the chat text: %s" % Mig.NOTE_TEXT.get("g1"))
    K.check(bool(Mig.tell(gs_[0], u)) and not bool(Mig.tell(gs_[0], u)), "LVL: tell() sends the member's line once")
    u2 = UUID(0x6d11d, 8)
    K.check(not bool(Mig.tell(gs_[1], u2)), "LVL: a guild without a notice: nothing")
    GS.touchN(u, "Steve", 1)    # touchN EXECUTES its new tell() call (already told -> no second line, no throw)
    K.check(Mig.NOTICE.get("g1").contains(str(u)), "LVL: touchN path ran (member recorded as told)")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar])
    System, CHM, Paths = JClass("java.lang.System"), JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.nio.file.Paths")
    System.getProperties().put("skyy.bridge", CHM())
    GS, Cfg, Mig, Nc = JClass(PKG + "GuildStore"), JClass(PKG + "GCfg"), JClass(PKG + "GP5Mig"), JClass(PKG + "GNcMig")
    GS.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyGuildsTest")
    fc = os.path.join(home, "config.properties")
    GS.DIR, GS.GDIR, Cfg.FILE = Paths.get(home), Paths.get(os.path.join(home, "guilds")), Paths.get(fc)
    lp = os.path.join(home, "config-changes.log")
    log0 = open(lp, "rb").read() if os.path.isfile(lp) else b""
    o0 = open(fc, "rb").read()

    def start():
        a = str(Nc.migrate())
        mid = open(fc, "rb").read()
        b = str(Mig.migrate())
        Cfg.load()
        GS.GUILDS.clear()
        GS.loadAll()
        return a, mid, b, str(Mig.report())
    a1, mid, b1, r1 = start()
    n1 = open(fc, "rb").read()
    print("   live start 1: GNcMig: %s | GP5Mig: %s" % (a1[:120], b1[:160]))
    for line in r1.split("\n"):
        print("   live guild level:", line)
    po, pn = _props(mid), _props(n1)
    changed = sorted(k for k in set(po) | set(pn) if po.get(k) != pn.get(k))
    K.eq(changed, ["levelBase", "levelStep"], "D GP5Mig changed only levelBase / levelStep (Properties)")
    K.eq((pn["levelBase"], pn["levelStep"], int(Cfg.BASE), int(Cfg.STEP)), ("2000", "3000", 2000, 3000), "D the live file + loader hold 2000 / 3000")
    K.check("GodSquad" in r1 and "level 20 -> 5" in r1, "D GodSquad: level 20 -> 5 (%s)" % r1[:200])
    lines_o = [x for x in mid.split(b"\n") if not x.startswith((b"levelBase=", b"levelStep="))]
    lines_n = [x for x in n1.split(b"\n") if not x.startswith((b"levelBase=", b"levelStep=")) and str(Mig.MARK_ID).encode() not in x]
    K.check(lines_o == lines_n, "D every other line byte-identical, in order; the marker the only new line")
    found = any(open(os.path.join(r_, f_), "rb").read() == mid for r_, _d, fs in os.walk(os.path.join(home, "config-history")) for f_ in fs)
    K.check(found, "D the config-history copy holds the bytes before the P5 update")
    lg = open(lp, "rb").read()[len(log0):].decode("utf-8")
    K.eq((lg.count("\tSkyyGuilds 0.1.13\t-\tupdate\tlevelBase\t100\t2000\tok"), lg.count("\tSkyyGuilds 0.1.13\t-\tupdate\tlevelStep\t150\t3000\tok")), (1, 1),
         "D one change-log line per moved row (GNcMig adds its own xpMaxPerCheck line: the live file never started 0.1.12)")
    g_files0 = {f: open(os.path.join(home, "guilds", f), "rb").read() for f in os.listdir(os.path.join(home, "guilds"))}
    Mig.OLD_BASE, Mig.OLD_STEP = -1, -1
    a2, _m, b2, r2 = start()
    K.check(b2 == "" and r2 == "" and open(fc, "rb").read() == n1, "D start 2: nothing changes, no second report")
    K.check(g_files0 == {f: open(os.path.join(home, "guilds", f), "rb").read() for f in os.listdir(os.path.join(home, "guilds"))}, "D the guild files are untouched (XP kept)")
    K.check(o0 != n1, "D the live copy was updated (sanity)")
    K.save()


HK.run(name="SkyyGuilds", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["GP5Mig"],
       phases=[("static", run_static), ("mig", run_mig), ("lvl", run_lvl), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyGuilds"))
