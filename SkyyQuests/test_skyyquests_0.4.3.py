"""SkyyQuests 0.4.3 harness (/quests widget hide | show | fold -> SkyyHud's hud:fn:questFold; UI round R1 part A; tools/quests_0_4_3_patch.py)
on top of the 0.4.2 harness (test_skyyquests_0.4.2.py -> 0.4.1 -> ... -> 0.3: every older phase runs again on the 0.4.3 jar).

    python SkyyQuests/test_skyyquests_0.4.3.py [--jar SkyyQuests-0.4.3.jar] [--keep] [--only wid43,...]

  A / C / AA  verify, class compare 0.4.2 -> 0.4.3 (the new class QuestsWidgetCmd), engine-access audit
  WID43 wid43  QCmdUtil.widget EXECUTED against a stand-in hud:fn:questFold: hide / show / fold call it with "hide" / "show" / "toggle"
               (case and spaces ignored) and answer "+..."; fold names the state it is in now (folded / open); FALSE / a throwing
               function = "-could not change"; no function (an older SkyyHud) = "-needs SkyyHud 0.3.35"; any other word / empty = the usage
               line and NO call; the real QuestsWidgetCmd ("widget", one required argument, the Adventurer group) is a sub-command of the
               real QuestsCmd
  OLD   every 0.4.2 phase (acc42 gear41 page40 claim40 mig34 fish34 merge chain migt isl snd defs engine life pay crash static npc board fish
        live40 live41)
Scratch: tools/dev/scratch/uir1a/q (deleted unless --keep). Exit 1 on any failure.
"""
import os, sys, shutil, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION = "0.4.3"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "uir1a", "q")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyQuests-%s.jar" % VERSION)]
import harness_kit as HK
import skyybuild as B

_spec = importlib.util.spec_from_file_location("test_skyyquests_0_4_2", os.path.join(HERE, "test_skyyquests_0.4.2.py"))
T042 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T042)
T041, T040, T034, T033, T03 = T042.T041, T042.T040, T042.T034, T042.T033, T042.T03

JAR = T042.JAR
OLD_JAR = os.path.join(HERE, "SkyyQuests-0.4.2.jar")
SCRATCH, FAKE_DIR, PKG = T03.SCRATCH, T03.FAKE_DIR, T03.PKG
EXPECT = {
    "QCmdUtil": ["+m widget"],
    "QuestsCmd": ["~c "],                                            # + addSubCommand(new QuestsWidgetCmd())
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],              # the version texts (no config row changed)
    "SkyyQuestsPlugin": ["~m setup"],                                # the ready line's version
}
ADDED, REMOVED = ["QuestsWidgetCmd"], []


def run_wid43(out, jar, scratch, home):
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    CHM, System, UUID = JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.lang.System"), JClass("java.util.UUID")
    Boolean = JClass("java.lang.Boolean")
    br = CHM()
    System.getProperties().put("skyy.bridge", br)
    CU = JClass(PKG + "QCmdUtil")
    JClass(PKG + "QLog").BRIDGE = br
    u = UUID.fromString("00000000-0000-0000-0000-000000000643")

    @JImplements("java.util.function.Function")
    class Fold(object):
        def __init__(self):
            self.calls, self.ans, self.state, self.boom = [], True, "folded", False

        @JOverride
        def apply(self, a):
            self.calls.append([str(x) for x in a])
            if self.boom:
                raise RuntimeError("boom")
            if str(a[1]) == "state":
                return Boolean.FALSE if self.state is None else self.state
            return Boolean.TRUE if self.ans else Boolean.FALSE
    w = lambda a: str(CU.widget(u, a))
    K.check(w("hide").startswith("-") and "SkyyHud 0.3.35" in w("fold"), "WID43 no hud:fn:questFold (an older SkyyHud): '-...needs SkyyHud 0.3.35'")
    f = Fold()
    br.put("hud:fn:questFold", f)
    K.eq(w("hide"), "+Quest widget hidden. /quests widget show brings it back.", "WID43 hide")
    K.eq(f.calls[-1], [str(u), "hide"], "WID43 ... called with hide")
    K.eq(w(" SHOW "), "+Quest widget shown.", "WID43 show (case + spaces ignored)")
    K.eq(f.calls[-1], [str(u), "show"], "WID43 ... called with show")
    n = len(f.calls)
    K.eq(w("fold"), "+Quest widget folded. /quests widget fold opens it again.", "WID43 fold -> folded")
    K.eq(f.calls[n:], [[str(u), "state"], [str(u), "toggle"], [str(u), "state"]], "WID43 ... state, toggle, then state (fix 2)")
    f.state = "open"
    K.eq(w("Fold"), "+Quest widget open.", "WID43 fold again -> open")
    f.ans = False
    K.eq(w("hide"), "-Your quest widget could not change right now.", "WID43 the function says FALSE")
    K.eq(w("fold"), "-No quest is on your tracker to fold right now.", "FIX1: fold refused by SkyyHud (no quest showing) -> the no-quest line")
    f.state = None
    n = len(f.calls)
    K.eq(w("fold"), "-Your quest widget could not change right now.", "FIX2c: SkyyHud cannot say the state (stopping / no layout) -> could not change")
    K.eq(f.calls[n:], [[str(u), "state"]], "FIX2c: ... and no toggle sent")
    f.state, f.ans = "hidden", True
    n = len(f.calls)
    K.eq(w("fold"), "+Quest widget shown.", "FIX2b: fold on a hidden tracker -> shown (open)")
    K.eq(f.calls[n:], [[str(u), "state"], [str(u), "show"]], "FIX2b: ... state, then show (SkyyHud's toggle no longer re-enables)")
    f.state, f.ans = "open", False
    f.ans, f.boom = True, True
    K.eq(w("show"), "-Your quest widget could not change right now.", "WID43 a throwing function")
    f.boom = False
    n = len(f.calls)
    for bad in ("", "open", "toggle", None, "hidee"):
        K.eq(w(bad), "-Use /quests widget hide, /quests widget show or /quests widget fold.", "WID43 %r -> the usage line" % bad)
    K.eq(len(f.calls), n, "WID43 ... and no call")
    # the real command objects
    WC, QC = JClass(PKG + "QuestsWidgetCmd"), JClass(PKG + "QuestsCmd")
    wc = WC()
    K.eq(str(wc.getName()), "widget", "WID43 QuestsWidgetCmd is 'widget'")
    groups = None
    k = wc.getClass()
    while k is not None and groups is None:
        for fld in k.getDeclaredFields():
            if "ermissionGroup" in str(fld.getName()):
                fld.setAccessible(True)
                groups = fld.get(wc)
                break
        k = k.getSuperclass()
    gl = [] if groups is None else [str(x) for x in (groups if not hasattr(groups, "toArray") else groups.toArray())]
    K.check("hytale:Adventurer" in gl, "WID43 ... in the Adventurer group (HANDOFF 3): %s" % gl)
    qc = QC()
    subs = None
    k = qc.getClass()
    while k is not None and subs is None:
        for fld in k.getDeclaredFields():
            if "ubCommand" in str(fld.getName()):
                fld.setAccessible(True)
                subs = fld.get(qc)
                break
        k = k.getSuperclass()
    names = []
    if subs is not None:
        vals = subs.values() if hasattr(subs, "values") else subs
        for x in (vals.toArray() if hasattr(vals, "toArray") else vals):
            try:
                names.append(str(x.getName()))
            except Exception:
                names.append(str(x))
        if hasattr(subs, "keySet"):
            names += [str(x) for x in subs.keySet().toArray()]
    K.check("widget" in names and "hide" in names and "show" in names, "WID43 /quests has the widget sub-command next to hide / show: %s" % sorted(set(names)))
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
    phases = [("wid43", run_wid43), ("acc42", T042.run_acc42), ("gear41", T041.run_gear41), ("page40", T040.run_page40),
              ("claim40", T040.run_claim40), ("mig34", T034.run_mig34), ("fish34", T034.run_fish34),
              ("merge", T033.run_merge), ("chain", T033.run_chain), ("migt", T033.run_migt),
              ("isl", lg(T040.T032.run_isl)), ("snd", lg(T040.T031.run_snd)), ("defs", lg(T03.run_defs)), ("engine", lg(T03.run_engine)),
              ("life", lg(T03.run_life)), ("pay", lg(T03.run_pay)), ("crash", lg(T03.run_crash)), ("static", lg(T03.run_static)),
              ("npc", lg(T03.run_npc)), ("board", lg(T03.run_board)), ("fish", lg(T03.run_fish)), ("live40", T040.run_live40),
              ("live41", T041.run_live41)]
    if not os.path.isfile(T034.FISH17):     # the two phases that load the REAL SkyyFishing 0.1.7 jar (built jars are not kept in git)
        print("NOTE: %s is not built here - phases fish34 + fish skipped (they fail the same way on the 0.4.2 harness; nothing in 0.4.3 touches fishing)" % T034.FISH17)
        phases = [ph for ph in phases if ph[0] not in ("fish34", "fish")]
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
