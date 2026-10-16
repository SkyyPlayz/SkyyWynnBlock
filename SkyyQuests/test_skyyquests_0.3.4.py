"""SkyyQuests 0.3.4 harness (MARLOW TEACHES TACKLE - the pole is in the starting kit; tools/quests_0_3_4_patch.py) on top of the 0.3.3 harness
(test_skyyquests_0.3.3.py -> 0.3.2 -> 0.3.1 -> 0.3: every older phase runs again on the 0.3.4 jar). tools/harness_kit.py phases, fresh child
JVMs (-Xverify:all).

    python SkyyQuests/test_skyyquests_0.3.4.py [--jar SkyyQuests-0.3.4.jar] [--keep]

  A / C / AA  verify, class compare 0.3.3 -> 0.3.4, engine-access audit
  MF    mig34   the ONE-TIME update of quests/fishing_intro.properties + dialogue/marlow.properties EXECUTED: the 0.3 shipped bytes -> the
                0.3.4 text + <file>.0.3.bak (= the old bytes); a second start does nothing (the marker); an edited file KEPT + <file>.0.3.4.new
                once (the owner's change to the .new survives); a backup that cannot be written = the file is NOT changed
  FL    fish34  Marlow's 0.3.4 line with the REAL SkyyFishing 0.1.7 (FishBridge in this JVM): 4 tasks (take_pole, catch_fish, show_marlow,
                fit_tackle); the offer pages say he gives a hook (no "old pole"), accept = "Take the hook"; Accept completes take_pole and
                pays coins + ONE Barbed Hook I item claim and NO pole claim; FishBridge.questRig(u, hook) (what the Rig tab sends) counts
                fit_tackle EARLY; catch + show finish the line with fit_tackle done by the cascade; every reward once; the reward parser still
                takes pole:starter (an owner's kept file)
  OLD   every 0.3.3 phase (merge chain migt isl snd defs engine life pay crash static npc board fish) on the 0.3.4 jar with the 0.3 Marlow
                files EDITED by the owner (= kept: the 0.3.3 behaviour); the 0.3.3 waivers stay
  ST    live34  START TWICE on a scratch COPY of the live Skyy_SkyyQuests of the deploy world (NewBetaTest): start 1 changes ONLY
                fishing_intro.properties + marlow.properties (both are the untouched 0.3 texts) and writes their .0.3.bak (= the old bytes);
                start 2 writes nothing; every live profile loads and keeps every key; the live folder itself is only read
Scratch: tools/dev/scratch/gear0311/quests (deleted unless --keep). Exit 1 on any failure.
"""
import os, sys, shutil, subprocess, importlib.util, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "gear0311", "quests")]
VERSION = "0.3.4"
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyQuests-%s.jar" % VERSION)]
_spec = importlib.util.spec_from_file_location("test_skyyquests_0_3_3", os.path.join(HERE, "test_skyyquests_0.3.3.py"))
T033 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T033)
T032, T031, T03 = T033.T032, T033.T031, T033.T03

JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyQuests-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyQuests-0.3.3.jar")
FISH17 = os.path.join(ROOT, "SkyyFishing", "SkyyFishing-0.1.7.jar")
SCRATCH = T03.SCRATCH
FAKE_DIR = T03.FAKE_DIR
PKG = T03.PKG
TB = T03.TB
LIVE_Q34 = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyQuests")
EXPECT = {
    "QDefs": ["+f FISH03", "+m migrate034", "~<clinit>", "~m load"],
    "QNpc": ["+f MARLOW_DLG03", "~m loadDialogues"],          # MARLOW_DLG03 is a compile-time constant (no <clinit> change)
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyQuestsPlugin": ["~m setup"],          # the version string in the kit header / ready line
}
ADDED = []

# the 0.3 static phase lists every method that touches files: QDefs.migrate034 is the new one-time update (the migrateTut pattern) - waived by name
_chk033 = HK.Child.check


def _check34(self, cond, what):
    if not cond and str(what).startswith("S2 the file calls live in these methods only") and "QDefs.migrate034" in str(what):
        self.notes.append("WAIVED (0.3.4 adds QDefs.migrate034, the one-time update of the two Marlow files): %s" % str(what)[:120])
        return cond
    return _chk033(self, cond, what)


HK.Child.check = _check34

# ---------------------------------------------------------------------------------------------------- the older phases: the owner kept 0.3's Marlow files
_orig_start = T03.Env.start


def _start(self):
    if T033.LEGACY[0]:
        P = self.P
        for rel, txt in ((os.path.join("quests", "fishing_intro.properties"), str(P("QDefs").FISH03)),
                         (os.path.join("dialogue", "marlow.properties"), str(P("QNpc").MARLOW_DLG03))):
            f = os.path.join(self.base, rel)
            if not os.path.isfile(f):
                os.makedirs(os.path.dirname(f), exist_ok=True)
                open(f, "wb").write((txt + "# kept by the server owner (an edited 0.3 file - the 0.3.4 harness)\n").encode("utf-8"))
    return _orig_start(self)


T03.Env.start = _start


# ---------------------------------------------------------------------------------------------------- MF: the one-time update of the two files
def run_mig34(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, FAKE_DIR, B.JAVASSIST], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Paths = JClass("java.nio.file.Paths")
    X = T03.scene3(K, scratch, "mf")
    Defs, Npc = X.Defs, X.Npc
    f03, f34 = str(Defs.FISH03), str(Defs.LINE_TEXTS[len(Defs.LINE_TEXTS) - 1])
    d03, d34 = str(Npc.MARLOW_DLG03), str(Npc.MARLOW_DLG)
    K.check("updated by 0.3.4" in f34 and "updated by 0.3.4" not in f03 and "fit_tackle" in f34 and "pole:starter" in f03 and "pole:starter" not in f34.split("line=")[1],
            "MF the two Marlow line texts (0.3 / 0.3.4)")
    K.check("updated by 0.3.4" in d34.split("\n")[0] and "pole of mine" in d03 and "Take the hook" in d34, "MF the two dialogue texts")
    for nm, old, new in (("fishing_intro.properties", f03, f34), ("marlow.properties", d03, d34)):
        d = os.path.join(scratch, "mf-" + nm.split(".")[0])
        os.makedirs(d, exist_ok=True)
        tp = os.path.join(d, nm)
        open(tp, "wb").write(old.encode("utf-8"))
        m = str(Defs.migrate034(Paths.get(tp), old, new, "test"))
        K.check(open(tp, "rb").read() == new.encode("utf-8") and open(tp + ".0.3.bak", "rb").read() == old.encode("utf-8") and "0.3.4" in m,
                "MF the untouched 0.3 %s -> the 0.3.4 text; the old bytes kept as %s.0.3.bak" % (nm, nm))
        K.eq(str(Defs.migrate034(Paths.get(tp), old, new, "test")), "", "MF ... a second start does nothing (the marker)")
        K.check(not os.path.isfile(tp + ".0.3.4.new"), "MF ... no .new beside an updated file")
        tp2 = os.path.join(d, "ed-" + nm)
        ed = (old + "# my own line\n").encode("utf-8")
        open(tp2, "wb").write(ed)
        m2 = str(Defs.migrate034(Paths.get(tp2), old, new, "test"))
        K.check(open(tp2, "rb").read() == ed and open(tp2 + ".0.3.4.new", "rb").read() == new.encode("utf-8") and "KEPT" in m2,
                "MF an edited %s is KEPT + the 0.3.4 text beside it" % nm)
        open(tp2 + ".0.3.4.new", "ab").write(b"# the owner's note\n")
        K.eq(str(Defs.migrate034(Paths.get(tp2), old, new, "test")), "", "MF ... the .new is written ONCE (a second start leaves it)")
        K.check(open(tp2 + ".0.3.4.new", "rb").read().endswith(b"# the owner's note\n"), "MF ... and keeps the owner's change to it")
        d3 = os.path.join(scratch, "mf-nobak-" + nm.split(".")[0])
        os.makedirs(os.path.join(d3, nm + ".0.3.bak"), exist_ok=True)          # a folder where the backup file should go
        tp3 = os.path.join(d3, nm)
        open(tp3, "wb").write(old.encode("utf-8"))
        m3 = str(Defs.migrate034(Paths.get(tp3), old, new, "test"))
        K.check(open(tp3, "rb").read() == old.encode("utf-8") and m3 == "", "MF a backup that cannot be written = %s NOT changed" % nm)
    # the loaders call it: a server with the untouched 0.3 files gets both updated on its next load
    q = os.path.join(X.base, "quests", "fishing_intro.properties")
    g = os.path.join(X.base, "dialogue", "marlow.properties")
    open(q, "wb").write(f03.encode("utf-8"))
    open(g, "wb").write(d03.encode("utf-8"))
    Defs.load()
    errs = JClass("java.util.ArrayList")()
    Npc.loadDialogues(errs)
    K.check(open(q, "rb").read() == f34.encode("utf-8") and open(g, "rb").read() == d34.encode("utf-8") and os.path.isfile(q + ".0.3.bak") and os.path.isfile(g + ".0.3.bak"),
            "MF QDefs.load + QNpc.loadDialogues update both untouched files (and keep .0.3.bak)")
    FL = Defs.line("fishing_intro")
    K.eq([str(t.id) for t in FL.tasks], ["take_pole", "catch_fish", "show_marlow", "fit_tackle"], "MF the loaded line has the 4 tasks")
    K.check(not list(Defs.PROBLEMS) and not [str(e) for e in errs], "MF no problems: %s %s" % ([str(x) for x in Defs.PROBLEMS], [str(e) for e in errs]))
    K.save()


# ---------------------------------------------------------------------------------------------------- FL: the new line end to end
def run_fish34(out, jar, scratch, home):
    from jpype import JClass, JObject, JArray, JLong
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, FISH17, FAKE_DIR, B.JAVASSIST], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    PyFn = T03.fn_class()
    Boolean, Long = JClass("java.lang.Boolean"), JClass("java.lang.Long")
    X = T03.scene3(K, scratch, "f34")
    Npc, Eng, Defs, Sto, Talk = X.Npc, X.Eng, X.Defs, X.Sto, X.Talk
    Npc.API = T03.npc_api(T03.api_state())
    Sto.STOPPED = True
    br.put("coins:fn:add", PyFn(lambda a: Long(1000)))
    br.put("profile:fn:key", PyFn(lambda a: str(a)))
    FL = Defs.line("fishing_intro")
    K.eq([str(t.id) for t in FL.tasks], ["take_pole", "catch_fish", "show_marlow", "fit_tackle"], "FL a fresh server ships the 0.3.4 line: 4 tasks, fit_tackle last")
    t0 = FL.tasks[0]
    K.check(str(t0.name) == "Meet Marlow at the pier" and "SkyyFishing_Hook_Barbed_I" in str(t0.reward) and "pole:" not in str(t0.reward),
            "FL take_pole = 'Meet Marlow at the pier', reward coins + the Barbed Hook, no pole: %s" % t0.reward)
    t3 = FL.tasks[3]
    K.check(str(t3.parts[0].tname) == "event" and str(t3.parts[0].match) == "fishing:rig" and str(t3.parts[0].caller) == "fishingrig",
            "FL fit_tackle = event fishing:rig, caller fishingrig (fix round: only SkyyFishing 0.1.7 sets quest:caller:fishingrig)")
    br.put("quest:caller:fishing", Boolean.TRUE)          # what SkyyFishing 0.1.4 - 0.1.6 put (no fishingrig)
    K.check(bool(Eng.partSoon(t3.parts[0])) and not bool(Eng.partSoon(FL.tasks[1].parts[0])),
            "FL (fix round) with an older SkyyFishing (quest:caller:fishing only) fit_tackle is 'coming soon' (skipped, never stuck), catch_fish is live")
    K.eq(Defs.rewardProblem("pole:starter,coins:5"), None, "FL the reward parser still takes pole:starter (an owner's kept file)")
    u, p, s = X.player(71, T03.HUB)
    pr = T03.pref_of(u, "Fin")
    p.pr = pr
    FB = JClass("com.skyy.fishing.FishBridge")
    FB.questInit()
    K.check(not bool(Eng.partSoon(t3.parts[0])), "FL (fix round) with SkyyFishing 0.1.7 (quest:caller:fishingrig) fit_tackle is live")
    pg = Talk.pageFor(pr, "marlow")
    K.check(int(pg.mode) == 1 and len(pg.pages) == 3 and "Barbed Hook" in str(pg.pages[1]) and "pole of mine" not in "".join(str(x) for x in pg.pages)
            and "starting tools" in str(pg.pages[0]) and "I see you carry" not in str(pg.pages[0]),
            "FL the offer pages: he gives a hook, no 'old pole': %s" % [str(x)[:60] for x in pg.pages])
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    for _ in range(2):
        try:
            pg.handleDataEvent(None, None, '{"a":"next"}')
        except Exception:
            pass
    b, ev = UCB(), UEB()
    pg.build(None, b, ev, None)
    mk = T03.markup(b)
    dl = Npc.DLG.get("marlow")
    K.check("SkyyQdYes" in mk and dl is not None and str(dl.getProperty("accept")) == "Take the hook", "FL the last offer page: Accept = 'Take the hook' (dialogue/marlow.properties)")
    try:
        pg.handleDataEvent(None, None, '{"a":"yes"}')
    except Exception:
        pass
    cl = [str(c) for c in s.claims]
    K.check(bool(s.isDone("fishing_intro.take_pole")) and not [c for c in cl if c.startswith("pole|")] and len([c for c in cl if "SkyyFishing_Hook_Barbed_I" in c]) == 1,
            "FL Accept: take_pole done, ONE Barbed Hook item claim, NO pole claim: %s" % cl)
    # the Rig tab's event (the REAL SkyyFishing 0.1.7 FishBridge.questRig) -> quest:fn:event; publish the engine's event fn the plugin would
    W = T03.HUB
    got = []

    def qev(a):
        got.append([str(x) for x in a])
        return Boolean.valueOf(bool(Eng.count(a[0], TB["event"], str(a[1]), int(a[3]), W, False)))
    br.put("quest:fn:event", PyFn(qev))
    K.check(bool(FB.questRig(u, "SkyyFishing_Hook_Barbed_I")) or got, "FL FishBridge.questRig sends quest:fn:event: %s" % got)
    K.eq(got[:1], [[str(u), "fishing:rig", "SkyyFishing_Hook_Barbed_I", "1"]], "FL ... {UUID, fishing:rig, the part, 1}")
    K.check(not bool(s.isDone("fishing_intro.fit_tackle")) and bool(s.pdone.contains("fishing_intro.fit_tackle.0")),
            "FL fit_tackle (not active yet) counted EARLY, not done")
    Eng.count(u, TB["event"], "fishing:catch", 1, W, False)
    K.check(bool(s.isDone("fishing_intro.catch_fish")), "FL a catch finishes catch_fish")
    Eng.rebuild(u, s)
    Eng.count(u, TB["talk"], "marlow", 1, W, False)
    K.check(bool(s.isDone("fishing_intro.show_marlow")) and bool(s.isDone("fishing_intro.fit_tackle")),
            "FL showing Marlow finishes show_marlow and the already-met fit_tackle AT ONCE (the cascade)")
    lg = T03.logtext(X.base)
    cl2 = [str(c) for c in s.claims]
    allc = lg + " ".join(cl2)
    K.check("fishing_intro.fit_tackle" in allc and "Food_Fish_Grilled:2" in allc and "Food_Fish_Grilled:3" in allc, "FL fit_tackle's + show_marlow's rewards were claimed: %s" % cl2)
    K.eq(len([c for c in cl2 if "SkyyFishing_Hook_Barbed_I" in c]), 1, "FL still ONE hook claim at the end")
    K.save()


# ---------------------------------------------------------------------------------------------------- ST: start twice on the live copy
def run_live34(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    mods = os.path.join(scratch, "live34mods")
    base = os.path.join(mods, "Skyy_SkyyQuests")
    if not os.path.isdir(LIVE_Q34):
        K.check(False, "ST no live Skyy_SkyyQuests at %s" % LIVE_Q34)
        K.save()
        return
    shutil.rmtree(mods, ignore_errors=True)
    os.makedirs(mods)
    shutil.copytree(LIVE_Q34, base)                  # a scratch COPY (the source is only read)
    q0 = HK.tree_hash(LIVE_Q34)
    fq = os.path.join(base, "quests", "fishing_intro.properties")
    fd = os.path.join(base, "dialogue", "marlow.properties")
    oq, od = open(fq, "rb").read(), open(fd, "rb").read()
    players0 = dict((f, open(os.path.join(base, "players", f), "rb").read()) for f in os.listdir(os.path.join(base, "players")))
    Paths = JClass("java.nio.file.Paths")
    res = []
    E = None
    for n in range(2):
        b0 = HK.tree_hash(mods)
        E = T03.Env(base)
        E.P("QDefs").BOARD_FILE = Paths.get(os.path.join(base, "board.properties"))
        Npc = E.P("QNpc")
        Npc.FILE = Paths.get(os.path.join(base, "npcs.tsv"))
        Npc.DLG_DIR = Paths.get(os.path.join(base, "dialogue"))
        E.P("QMig").migrate02()
        lines = E.start()
        errs = JClass("java.util.ArrayList")()
        Npc.load(errs)
        Npc.loadDialogues(errs)
        res.append((lines, [str(x) for x in E.P("QDefs").PROBLEMS] + [str(x) for x in errs], HK.tree_hash(mods), b0))
    K.check(res[0][0] >= 7 and not res[0][1], "ST start 1: %d lines, no problems: %s" % (res[0][0], res[0][1]))
    ch = sorted(k for k in set(res[0][2]) | set(res[0][3]) if res[0][2].get(k) != res[0][3].get(k))
    want = sorted(os.path.join("Skyy_SkyyQuests", *p) for p in (("quests", "fishing_intro.properties"), ("quests", "fishing_intro.properties.0.3.bak"),
                                                                  ("dialogue", "marlow.properties"), ("dialogue", "marlow.properties.0.3.bak")))
    K.eq(ch, want, "ST start 1 changes ONLY the two Marlow files (the live ones are the untouched 0.3 texts) + writes their .0.3.bak")
    K.check(open(fq + ".0.3.bak", "rb").read() == oq and open(fd + ".0.3.bak", "rb").read() == od, "ST the .0.3.bak files = the old bytes")
    K.check(b"updated by 0.3.4" in open(fq, "rb").read() and b"updated by 0.3.4" in open(fd, "rb").read(), "ST the new files carry the marker")
    K.check(res[1][2] == res[1][3], "ST start 2 writes nothing")
    K.eq(HK.tree_hash(LIVE_Q34), q0, "ST the LIVE folder itself was only read")
    Sto = E.P("QStore")
    Sto.DIR = Paths.get(os.path.join(base, "players"))
    U = JClass("java.util.UUID")
    for f, raw in sorted(players0.items()):
        pk = f[:-len(".properties")]
        s = Sto.read(pk, U.randomUUID())
        P2 = JClass("java.util.Properties")()
        P2.load(JClass("java.io.StringReader")(raw.decode("utf-8")))
        want_ = dict((str(k), str(P2.getProperty(k))) for k in P2.stringPropertyNames())
        P3 = JClass("java.util.Properties")()
        P3.load(JClass("java.io.StringReader")(str(s.textU())))
        got = dict((str(k), str(P3.getProperty(k))) for k in P3.stringPropertyNames())
        lost = sorted(k for k in want_ if k not in got)
        K.check(not bool(s.frozen) and not lost, "ST live profile %s loads, keeps every key (%d keys; lost %s)" % (f, len(want_), lost))
        K.check(open(os.path.join(base, "players", f), "rb").read() == raw, "ST ... and the start did not rewrite it")
    K.notes.append("ST live profiles: %s" % sorted(players0))
    shutil.rmtree(mods, ignore_errors=True)
    K.save()


if __name__ == "__main__":
    if "--mkfake" in sys.argv:
        T03.mkfake(HK.arg("--mkfake"), JAR)
        sys.exit(0)
    if "--phase" not in sys.argv:
        shutil.rmtree(FAKE_DIR, ignore_errors=True)
        os.makedirs(FAKE_DIR, exist_ok=True)
        env = dict(os.environ)
        env["TEMP"] = env["TMP"] = os.path.join(FAKE_DIR, "tmp")
        os.makedirs(env["TEMP"], exist_ok=True)
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--mkfake", FAKE_DIR, "--jar", JAR, "--dir", SCRATCH], env=env)
        if r.returncode != 0:
            sys.exit("the stand-in classes were not compiled")
    lg = T033.legacy
    try:
        HK.run("SkyyQuests", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
               [("mig34", run_mig34), ("fish34", run_fish34),
                ("merge", T033.run_merge), ("chain", T033.run_chain), ("migt", T033.run_migt),
                ("isl", lg(T032.run_isl)), ("snd", lg(T031.run_snd)), ("defs", lg(T03.run_defs)), ("engine", lg(T03.run_engine)),
                ("life", lg(T03.run_life)), ("pay", lg(T03.run_pay)), ("crash", lg(T03.run_crash)), ("static", lg(T03.run_static)),
                ("npc", lg(T03.run_npc)), ("board", lg(T03.run_board)), ("fish", lg(T03.run_fish)), ("live34", run_live34)],
               os.path.abspath(__file__), live=(LIVE_Q34, "Skyy_SkyyQuests"))
    finally:
        if "--phase" not in sys.argv and "--keep" not in sys.argv:
            shutil.rmtree(FAKE_DIR, ignore_errors=True)
