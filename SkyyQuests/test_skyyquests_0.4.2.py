"""SkyyQuests 0.4.2 harness (Void Charms in the tutorial hint, lean round, triage bug 15; tools/quests_0_4_2_patch.py) on top of the 0.4.1
harness (test_skyyquests_0.4.1.py -> 0.4.0 -> ... -> 0.3: every older phase runs again on the 0.4.2 jar; 0.4.0's one check that pinned
the 0.4.0 hint text is waived by name - its replacement is ACC42).

    python SkyyQuests/test_skyyquests_0.4.2.py [--jar SkyyQuests-0.4.2.jar] [--keep] [--only acc42,...]

  A / C / AA  verify, class compare 0.4.1 -> 0.4.2 (non-class entries: manifest.json only), engine-access audit
  ACC42 acc42  a fresh tutorial file (the 0.3 shipped hint on disk) loads first_accessory as "Craft one in your Void Charms' Craft tab";
               a copy holding 0.4.0's "Craft one in your Accessory Bag's Craft tab" loads with it too; the file on disk is unchanged;
               an owner's own hint is kept; no task of any shipped line names the "Accessory Bag" any more
  OLD   every 0.4.1 phase (gear41 page40 claim40 mig34 fish34 merge chain migt isl snd defs engine life pay crash static npc board fish
        live40 live41)
Scratch: tools/dev/scratch/mq-bugs/q (deleted unless --keep). Exit 1 on any failure.
"""
import os, sys, shutil, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION = "0.4.2"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "mq-bugs", "q")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyQuests-%s.jar" % VERSION)]
import harness_kit as HK

_spec = importlib.util.spec_from_file_location("test_skyyquests_0_4_1", os.path.join(HERE, "test_skyyquests_0.4.1.py"))
T041 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T041)
T040, T034, T033, T03 = T041.T040, T041.T034, T041.T033, T041.T03

JAR = T041.JAR
OLD_JAR = os.path.join(HERE, "SkyyQuests-0.4.1.jar")
SCRATCH, FAKE_DIR, PKG = T03.SCRATCH, T03.FAKE_DIR, T03.PKG
HINT03 = "Craft one at a bench, then put it in your Accessory Bag"
HINT40 = "Craft one in your Accessory Bag's Craft tab"
HINT42 = "Craft one in your Void Charms' Craft tab"
EXPECT = {
    "QDefs": ["~m parse"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],     # the version texts (no config row changed)
    "SkyyQuestsPlugin": ["~m setup"],                                # the ready line's version
}
ADDED, REMOVED = [], []

WAIVE42 = (("ACC: the shipped first_accessory hint now reads: " + HINT40, "ACC42 (the hint names Void Charms now; triage bug 15)"),)
_chk041 = HK.Child.check


def _check42(self, cond, what):
    if not cond:
        for w, why in WAIVE42:
            if str(what).startswith(w):
                self.notes.append("WAIVED (0.4.2, on purpose; covered by %s): %s" % (why, str(what)[:140]))
                return cond
    return _chk041(self, cond, what)


HK.Child.check = _check42      # 0.4.1's eq wrapper goes through check for its waivers; a direct eq below is waived the same way
_eq041 = HK.Child.eq


def _eq42(self, got, want, what):
    if got != want:
        for w, why in WAIVE42:
            if str(what).startswith(w):
                self.notes.append("WAIVED (0.4.2, on purpose; covered by %s): %s (got %r)" % (why, str(what)[:120], got))
                return False
    return _eq041(self, got, want, what)


HK.Child.eq = _eq42


def run_acc42(out, jar, scratch, home):
    K = HK.Child(out)
    X = T040.QStage(K, scratch, "acc42")
    Defs = X.Defs

    def hint():
        return str([t for t in Defs.line("tutorial").tasks if str(t.id) == "first_accessory"][0].hint)
    K.eq(hint(), HINT42, "ACC42 a fresh tutorial file loads first_accessory as: " + HINT42)
    tf = os.path.join(X.base, "quests", "tutorial.properties")
    txt = open(tf, encoding="utf-8").read()
    K.check(HINT03 in txt, "ACC42 the fresh file on disk keeps the 0.3 shipped words (rewritten at load only)")
    for words, want, what in ((HINT40, HINT42, "a copy with 0.4.0's Accessory Bag Craft tab hint loads with Void Charms"),
                              ("My own words for the accessory", "My own words for the accessory", "an owner's own hint is kept")):
        open(tf, "w", encoding="utf-8").write(txt.replace(HINT03, words))
        b0 = open(tf, "rb").read()
        Defs.load()
        K.eq(hint(), want, "ACC42 " + what)
        K.check(open(tf, "rb").read() == b0, "ACC42 loading wrote nothing (%s)" % what)
    open(tf, "w", encoding="utf-8").write(txt)
    Defs.load()
    bad = []
    for ln in ("tutorial",):
        L = Defs.line(ln)
        for t in L.tasks:
            for f in (t.name, t.hint):
                if f is not None and "accessory bag" in str(f).lower():
                    bad.append((ln, str(t.id), str(f)))
    K.check(not bad, "ACC42 no tutorial task names the Accessory Bag: %s" % bad)
    zf = __import__("zipfile").ZipFile(jar)
    hits = [n for n in zf.namelist() if not n.endswith(".class") and b"Accessory Bag" in zf.read(n)]
    K.check(not hits, "ACC42 no jar resource (lang / ui / defaults) says Accessory Bag: %s" % hits)
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
        env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
        os.makedirs(env["TEMP"], exist_ok=True)
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--mkfake", FAKE_DIR, "--jar", JAR, "--dir", SCRATCH], env=env)
        if r.returncode != 0:
            sys.exit("the stand-in classes were not compiled")
    lg = T033.legacy
    phases = [("acc42", run_acc42), ("gear41", T041.run_gear41), ("page40", T040.run_page40), ("claim40", T040.run_claim40),
              ("mig34", T034.run_mig34), ("fish34", T034.run_fish34),
              ("merge", T033.run_merge), ("chain", T033.run_chain), ("migt", T033.run_migt),
              ("isl", lg(T040.T032.run_isl)), ("snd", lg(T040.T031.run_snd)), ("defs", lg(T03.run_defs)), ("engine", lg(T03.run_engine)),
              ("life", lg(T03.run_life)), ("pay", lg(T03.run_pay)), ("crash", lg(T03.run_crash)), ("static", lg(T03.run_static)),
              ("npc", lg(T03.run_npc)), ("board", lg(T03.run_board)), ("fish", lg(T03.run_fish)), ("live40", T040.run_live40),
              ("live41", T041.run_live41)]
    only = HK.arg("--only")
    if only:
        phases = [ph for ph in phases if ph[0] in only.split(",")]
    try:
        HK.run("SkyyQuests", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED, phases, os.path.abspath(__file__), live=(T040.LIVE_Q, "Skyy_SkyyQuests"),
               removed=REMOVED)
    finally:
        if "--phase" not in sys.argv and "--keep" not in sys.argv:
            shutil.rmtree(FAKE_DIR, ignore_errors=True)
    sys.exit(1 if HK.FAILS else 0)
