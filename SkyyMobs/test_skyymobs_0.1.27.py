"""Harness for SkyyMobs 0.1.27 (round rar3 = colour-coded chat lines, looks only: MobCoin.seg / plainOf / msgOf / coinLine / partyLine,
MobEgg.eggLine; tools/mobs_0_1_27_patch.py).
Build first:
    python tools/mobs_0_1_27_patch.py && python SkyyMobs/build_skyymobs_0.1.27.py
    python SkyyMobs/test_skyymobs_0.1.27.py [--keep] [--expect-dump]

Phases (fresh child JVMs, tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes, line endings kept, no class / system / command; no jar entry added / removed, only
                 the manifest changes among the non-class entries (no lang / role / spawn file); the before / after chat texts -> <scratch>/../dumps/mobs.txt
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.1.26 -> 0.1.27 (EXPECT below)
  X     exec     EXECUTES the new paths: seg / plainOf (joints stripped, a cut joint, null), msgOf (one Message, each piece its colour, the text
                 before the first joint in c0, a cut joint ends it), coinLine / partyLine / eggLine (the words = 0.1.26's, the colours: coins
                 green, level gold, name soft white, party note dim, egg Legendary, action yellow, note dim), MobCoin.tell + MobEgg.tell
                 through the TELL_API seam (the plain words)
  EX126 0.1.26's exec + wire (kill coins: every message check compares the plain words) + 0.1.25's exec + wire + 0.1.24 / 0.1.23 exec +
        CreditSys, EXECUTED on this jar
  D     live     start twice on a scratch COPY of Skyy's live Skyy_SkyyMobs (0.1.26's live phase): bytes untouched, no migration
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): the client drawing the coloured chat pieces (Message.insert of coloured raw pieces is the SkyyFishing /
SkyyGear pattern).
Scratch: tools/dev/scratch/rar3fix/mobs (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.1.27"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "rar3fix", "mobs")]
import skyybuild as B
import harness_kit as HK
import skyyui as SUI

_run0 = HK.run
HK.run = lambda *a, **k: None          # import 0.1.26's harness (and through it 0.1.25's ...) for its phases without running it
_s = importlib.util.spec_from_file_location("test_skyymobs_0_1_26", os.path.join(HERE, "test_skyymobs_0.1.26.py"))
T26 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(T26)
HK.run = _run0
T25, T24, T23, T22 = T26.T25, T26.T24, T26.T23, T26.T22

GEN = os.path.join(HERE, "build_skyymobs_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyymobs_0.1.26.py")
PATCH = os.path.join(ROOT, "tools", "mobs_0_1_27_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMobs-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMobs-0.1.26.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.mobs."
ADDED = []
EXPECT = {"MobCoin": ["+m coinLine", "+m msgOf", "+m partyLine", "+m plainOf", "+m seg", "~m core", "~m shareOne", "~m tell"],
          "MobEgg": ["+m eggLine", "~m dropped", "~m tell"],
          "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "SkyyMobsPlugin": ["~m setup"],
          "MobCfg": ["~m load", "~m reloadAll", "~m useDefaults"]}          # CfgRows / MobCfg / CfgFn / plugin: the version texts only (identical after a version swap)
if "--expect-dump" in sys.argv:
    EXPECT = {}
GOLD, GOOD, PROG, NAME, DIM, ACT, EGG = (SUI.COLOR["gold"], "#7ee08a", "#e8c25a", "#d6e4ee", "#7f93a6", "#ffcc00", SUI.QUALITY["Legendary"])


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyMobs 0.1.27 - build script') and g.count('VERSION = "0.1.27"') == 1, "S header + VERSION")
    K.eq([g.count(w) - o.count(w) for w in ("registerSystem(", "registerCommand(", "makeClass(")], [0, 0, 0], "S no class / system / command")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), ([], []), "S no jar entry added or removed")
    K.eq(sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n)), ["manifest.json"], "S only the manifest changes (no lang / role / spawn file)")
    K.check(g.count("sendMessage(@MSG@.raw(chat)") == 0 and g.count("sendMessage(msgOf(chat, @GOLDC@))") == 1 and g.count("@PKG@.MobCoin.msgOf(text, @GOLDC@)") == 1,
            "S both coloured lines go out as one Message (msgOf)")
    dd = os.path.join(os.path.dirname(scratch), "dumps")
    os.makedirs(dd, exist_ok=True)
    with open(os.path.join(dd, "mobs.txt"), "w", encoding="utf8") as fh:
        fh.write("MobCoin kill chat line\n  before: [Mobs] +25 coins (Lv 12 Trork Warrior)   (all kit gold %s)\n"
                 "  after:  [Mobs] gold / +25 coins %s / ( gold / Lv 12 %s / Trork Warrior %s / ) gold\n" % (GOLD, GOOD, PROG, NAME))
        fh.write("MobCoin party chat line\n  before: [Mobs] +13 coins (party kill by Skyy)   (all gold)\n  after:  [Mobs] gold / +13 coins %s / (party kill by Skyy) %s\n" % (GOOD, DIM))
        fh.write("MobEgg boss egg line\n  before: [Mobs] The boss dropped a Fire Dragon Egg! Hatch it in /pets > Hatchery (one dragon per profile).   (all gold)\n"
                 "  after:  [Mobs] gold / words %s / Fire Dragon Egg %s (Legendary) / words %s / /pets > Hatchery %s / (one dragon per profile). %s\n" % (NAME, EGG, NAME, ACT, DIM))
    K.save()


def flat(m, acc=None):
    if acc is None:
        acc = []
    t = m.getRawText()
    if t is not None and len(str(t)) > 0:
        acc.append((str(t), None if m.getColor() is None else str(m.getColor())))
    ch = m.getChildren()
    if ch is not None:
        for i in range(ch.size()):
            flat(ch.get(i), acc)
    return acc


def run_exec27(out, jar, scratch, home):
    from jpype import JClass, JImplements, JOverride, JString, JLong, JInt
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    C, Co, Egg = JClass(PKG + "MobCfg"), JClass(PKG + "MobCoin"), JClass(PKG + "MobEgg")
    UUID = JClass("java.util.UUID")
    C.useDefaults()
    J1 = chr(1)
    # ---- seg / plainOf
    K.eq(str(Co.seg("#112233", "ab")), J1 + "#112233ab", "X seg = joint + colour + text")
    K.eq(str(Co.seg("#112233", None)), J1 + "#112233", "X seg(null text) = the joint alone")
    K.eq(str(Co.plainOf("x" + J1 + "#112233ab" + J1 + "#445566cd")), "xabcd", "X plainOf strips every joint")
    K.check(Co.plainOf(None) is None and str(Co.plainOf("plain")) == "plain" and str(Co.plainOf("ab" + J1 + "#12")) == "ab", "X plainOf: null, no joint, a cut joint")
    # ---- msgOf
    m = Co.msgOf("lead " + J1 + "#112233ab" + J1 + "#445566" + J1 + "#778899cd", GOLD)
    K.eq(flat(m), [("lead ", GOLD), ("ab", "#112233"), ("cd", "#778899")], "X msgOf: the lead text in c0, each piece its colour, an empty piece skipped")
    K.eq(flat(Co.msgOf("ab" + J1 + "#12", GOLD)), [("ab", GOLD)], "X msgOf: a cut joint ends the line (no throw)")
    K.eq(flat(Co.msgOf(None, GOLD)), [], "X msgOf(null) = an empty Message")
    # ---- the three lines: the 0.1.26 words, the colours
    for g_, L, role in ((25, 12, "Trork_Warrior"), (1234567, 87, "Skeleton_Fighter_SkyyVeteran1"), (3, 1, None)):
        ln = str(Co.coinLine(JLong(g_), JInt(L), role))
        want = "[Mobs] +" + str(Co.fmt(JLong(g_))) + " coins (Lv " + str(L) + " " + str(Co.name(role)) + ")"
        K.eq(str(Co.plainOf(ln)), want, "X coinLine(%s, %s, %s) = the 0.1.26 words" % (g_, L, role))
        K.eq([c for _t, c in flat(Co.msgOf(ln, GOLD))], [GOLD, GOOD, GOLD, PROG, NAME, GOLD], "X coinLine colours: coins green, level gold, name soft white")
    for kn, want in (("Skyy", "[Mobs] +13 coins (party kill by Skyy)"), (None, "[Mobs] +13 coins (party kill)")):
        ln = str(Co.partyLine(JLong(13), kn))
        K.eq(str(Co.plainOf(ln)), want, "X partyLine(%s) = the 0.1.26 words" % kn)
        K.eq([c for _t, c in flat(Co.msgOf(ln, GOLD))], [GOLD, GOOD, DIM], "X partyLine colours: coins green, the note dim")
    ids = [str(x) for x in Egg.IDS]
    K.check(len(ids) == 3, "X the three boss eggs: %s" % ids)
    for iid in ids + ["Skyy_Not_An_Egg"]:
        ln = str(Egg.eggLine(iid))
        want = "[Mobs] The boss dropped a " + str(Egg.nameOf(iid)) + "! Hatch it in /pets > Hatchery (one dragon per profile)."
        K.eq(str(Co.plainOf(ln)), want, "X eggLine(%s) = the 0.1.26 words" % iid)
        K.eq(flat(Co.msgOf(ln, GOLD)), [("[Mobs] ", GOLD), ("The boss dropped a ", NAME), (str(Egg.nameOf(iid)), EGG), ("! Hatch it in ", NAME), ("/pets > Hatchery", ACT),
                                       (" (one dragon per profile).", DIM)], "X eggLine(%s) pieces: [Mobs] gold, the words soft white (fix 3), the egg Legendary, the action yellow, the note dim" % iid)
    # ---- the seams get the plain words
    GOT = []

    @JImplements("java.util.function.BiConsumer")
    class Tell(object):
        @JOverride
        def accept(self, u, t):
            GOT.append(str(t))
    u = UUID.fromString("00000000-0000-0000-0000-000000000127")
    Egg.TELL_API = Tell()
    Co.TELL_API = Tell()
    try:
        Egg.tell(u, Egg.eggLine(ids[0]))
        r = str(Co.tell(u, Co.coinLine(JLong(25), JInt(10), "Trork_Warrior"), "+25 coins  Lv 10 Trork Warrior"))
        K.eq((GOT, r), (["[Mobs] The boss dropped a %s! Hatch it in /pets > Hatchery (one dragon per profile)." % str(Egg.nameOf(ids[0])),
                         "[Mobs] +25 coins (Lv 10 Trork Warrior)"], "chat"), "X MobEgg.tell / MobCoin.tell hand the seam the plain words (no joints)")
        K.check(Egg.dropped(u, ids[0], 1) and GOT[-1].startswith("[Mobs] The boss dropped a ") and J1 not in GOT[-1], "X MobEgg.dropped -> eggLine -> tell (plain words)")
    finally:
        Egg.TELL_API = None
        Co.TELL_API = None
    K.save()


HK.run_compare = T22._cmp
if __name__ == "__main__":
    HK.run("SkyyMobs", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("static", run_static), ("exec27", run_exec27), ("ex126", T26.run_exec), ("wi126", T26.run_wire), ("ex125", T25.run_exec), ("wi125", T25.run_wire),
            ("ex124", T24.run_exec), ("ex123", T23.run_exec), ("cs123", T23.run_cs), ("live", T26.run_live)], __file__, live=(T22.LIVE_DIR, "Skyy_SkyyMobs"))
