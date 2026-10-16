"""SkyyClasses 0.1.28 - harness for "the Class tab opens the class tree" (tools/classes_0_1_28_patch.py; with SkyyTrees 0.3.16's
tree:fn:classPage). Build first: python tools/classes_0_1_28_patch.py && python SkyyClasses/build_skyyclasses_0.1.28.py

    python SkyyClasses/test_skyyclasses_0.1.28.py [--dir <empty folder inside tools/dev/scratch/>] [--no-old]

Every JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch. Live save data is only READ / copied (by the old harness).
  OLD  the WHOLE 0.1.27 harness (test_skyyclasses_0.1.27.py, which runs the whole 0.1.26 harness itself) on the 0.1.28 jar. Its compare
       lines pin 0.1.26 -> 0.1.27 (ours: C below), so those are expected to differ (EXPECTED_OLD, each with its reason); every hub / page /
       click check of 0.1.27 must still pass (no tree:fn:classPage on its bridge = the class list as before).
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.1.27 -> 0.1.28: ClassPage (+ treeOpen, handleDataEvent), ClassHubOpen.openOn, ClassCmd (description + execute), the
                weapon refusal text, the inlined version texts; no class added / removed; non-class entries: manifest.json only
  TREE EXECUTED (tools/hub_tab_kit.py engine stand-ins, the REAL PageManager, -Xverify:all) with a stand-in tree:fn:classPage:
       no class on the profile -> the class list (the Function is never asked); a class on the profile (profile:class:<uuid>) -> the
       Function is asked with the UUID and nothing else opens; it answers FALSE / throws / is missing -> the class list; the Class tab on
       the class list and on the Abilities page go to the tree; /class goes through ClassHubOpen.openOn (bytecode); the refusal text
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, json, subprocess, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW
import hub_tab_kit as HT

VERSION = "0.1.28"
PKG = "com.skyy.classes."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyClasses-0.1.27.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "class0128", "cls")))
ADDED = []
EXPECT = {"ClassPage": ["+m treeOpen", "~m handleDataEvent"], "ClassHubOpen": ["~m openOn"], "ClassCmd": ["~c ", "~m execute"],
          "ClassRules": ["~m blockText"],
          "SkyyClassesPlugin": ["~m setup"],
          "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "KitMigrate": ["~m runOnce"]}      # the inlined version constant only
# the 0.1.27 harness's checks that pin the 0.1.26 -> 0.1.27 identity (prefix of the FAIL line) - expected on 0.1.28, with why
EXPECTED_OLD = [
    ("compare: C: classes added", "its compare is 0.1.26 -> 0.1.27 (+ HubBar, ClassHubOpen) against our jar (ours: phase C)"),
    ("compare: C: the classes that differ", "0.1.28 also changes ClassCmd + ClassRules (ours: phase C)"),
    ("compare: C: ", "its member lists pin 0.1.26 -> 0.1.27; 0.1.28 adds ClassPage.treeOpen, changes ClassHubOpen.openOn, ClassCmd, ClassRules.blockText (ours: phase C)"),
    ("OLD: no failure outside the listed identity checks", "its nested 0.1.26 harness's compare (0.1.25 -> 0.1.26) also sees the 0.1.28 changes"),
]
CLS_FAIL = "That tab could not open right now - try again."


def run_tree(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    P_ = lambda n: JClass(PKG + n)
    Cfg, Store, AS, Defs, HO, Page = P_("ClassCfg"), P_("ClassStore"), P_("AbilStore"), P_("ClassDefs"), P_("ClassHubOpen"), P_("ClassPage")
    base = os.path.join(scratch, "tree-mods", "Skyy_SkyyClasses")
    os.makedirs(base, exist_ok=True)
    Cfg.FILE = E.Paths.get(base, "config.properties")
    Store.DIR = E.Paths.get(base, "players")
    AS.DIR = E.Paths.get(base, "abilities")
    P = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-0000000000e8"), "ClassTree")
    u = P.pr.getUuid()
    us = str(u)
    HO.register()

    @JImplements("java.util.function.Function")
    class TreeFn:
        def __init__(self):
            self.calls, self.ans, self.boom = [], E.TRUE, False

        @JOverride
        def apply(self, o):
            self.calls.append(str(o))
            if self.boom:
                raise JClass("java.lang.IllegalStateException")("stand-in boom")
            return self.ans
    tf = TreeFn()

    def is_cls(pg):
        return pg is not None and str(pg.getClass().getName()) == PKG + "ClassPage"

    def click(pg, a):
        pg.handleDataEvent(P.ref, P.st, '{"a":"%s"}' % a)
        E.pump(P)
        return E.pg(P)

    def close_all():
        pg = E.pg(P)
        if pg is not None:
            pg.handleDataEvent(P.ref, P.st, '{"a":"clsclose"}' if is_cls(pg) else '{"a":"abclose"}')
            E.pump(P)
        return E.pg(P) is None
    fn = HO()
    # ---------------------------------------------------------------- no class on the profile: the class list, the Function never asked
    E.bridge.put("tree:fn:classPage", tf)
    K.check(not bool(Page.treeOpen(None)) and not bool(Page.treeOpen(u)) and tf.calls == [], "TREE: no class on the profile -> treeOpen = false, the Function is not asked")
    r = fn.apply(u)
    E.pump(P)
    K.check(r == E.TRUE and is_cls(E.pg(P)) and tf.calls == [], "TREE: no class -> the Class tab opens the class LIST (where a class is picked)")
    w, h, _s, _e = HT.page_check(K, E, P, HT.build(E.pg(P), P), "SkyyClsF", "character", "class", "Class", "TREE class list (no class)", idp="SkyyCls")
    K.eq((w, h), (1114, 980), "TREE class list: 0.1.27's window")
    K.check(close_all(), "TREE the list's Close still closes")
    # ---------------------------------------------------------------- a class on the profile: the class tree
    mage = [str(x) for x in Defs.NAMES].index("Mage")
    E.bridge.put("profile:class:" + us, "Mage")
    K.check(bool(Store.locked(u)) and int(Store.classIndex(u)) == mage, "TREE: profile:class = Mage -> the class is locked to the profile")
    r = fn.apply(u)
    E.pump(P)
    K.check(r == E.TRUE and tf.calls == [us] and E.pg(P) is None, "TREE: a class on the profile -> tree:fn:classPage(UUID) opens the class tree; no class list (%s)" % tf.calls)
    K.check(bool(HO.openOn(P.pr, P.ref, P.st)) and tf.calls == [us, us] and E.pg(P) is None, "TREE: openOn (the /class open) -> the class tree too")
    for what, setup in (("answers FALSE", lambda: setattr(tf, "ans", E.FALSE)), ("throws", lambda: setattr(tf, "boom", True)),
                        ("is missing (no SkyyTrees 0.3.16)", lambda: E.bridge.remove("tree:fn:classPage")),
                        ("is not a Function", lambda: E.bridge.put("tree:fn:classPage", "not a function"))):
        tf.calls, tf.ans, tf.boom = [], E.TRUE, False
        E.bridge.put("tree:fn:classPage", tf)
        setup()
        r = fn.apply(u)
        E.pump(P)
        K.check(r == E.TRUE and is_cls(E.pg(P)), "TREE: the Function %s -> the class list as before (the page always answers)" % what)
        close_all()
    tf.calls, tf.ans, tf.boom = [], E.TRUE, False
    E.bridge.put("tree:fn:classPage", tf)
    # ---------------------------------------------------------------- the Class tab on the class list / the Abilities page
    E.bridge.remove("tree:fn:classPage")
    r = fn.apply(u)
    E.pump(P)
    lst = E.pg(P)
    K.check(is_cls(lst), "TREE: (class trees unavailable) the class list is open")
    E.bridge.put("tree:fn:classPage", tf)
    cur = click(lst, "hub:class")
    K.check(tf.calls == [us], "TREE: the Class tab on the class list -> the class tree once it can open (%s)" % tf.calls)
    E.bridge.remove("tree:fn:classPage")
    lst = E.pg(P) if is_cls(E.pg(P)) else None
    if lst is None:
        fn.apply(u)
        E.pump(P)
        lst = E.pg(P)
    lst.pending = 2
    lst.info = "x"
    cur = click(lst, "hub:class")
    K.check(E.same(cur, lst) and int(lst.pending) == -1 and str(lst.info) == "", "TREE: ... and while it cannot, the Class tab keeps the list (pending pick cleared, as 0.1.27)")
    cur = click(lst, "clsabil")
    K.check(cur is not None and str(cur.getClass().getName()) == PKG + "AbilPage", "TREE: the list's Abilities button still opens the Abilities page")
    E.bridge.put("tree:fn:classPage", tf)
    tf.calls = []
    ab = cur
    cur = click(ab, "hub:class")
    K.check(tf.calls == [us] and E.same(cur, ab), "TREE: the Class tab on the Abilities page -> the class tree (%s)" % tf.calls)
    tf.ans = E.FALSE
    cur = click(ab, "hub:class")
    K.check(is_cls(cur), "TREE: ... the Function answers FALSE -> the class list (0.1.27's way)")
    close_all()
    # other tabs and < Menu still work from the list (the 0.1.27 rules) while the profile has a class
    E.bridge.remove("tree:fn:classPage")
    fakes = HT.Fakes(E, "character")

    def lst_page():
        fn.apply(u)
        E.pump(P)
        return E.pg(P)
    HT.clicks(K, E, P, lst_page, "character", "class", "TREE list clicks", fakes, fail_text=CLS_FAIL)
    fakes.remove()
    # ---------------------------------------------------------------- /class + the texts (bytecode / constant pool)
    g = PW.calls(jar)
    K.check(PKG + "ClassHubOpen.openOn" in g.get("ClassCmd.execute", set()), "TREE: /class opens through ClassHubOpen.openOn (bytecode)")
    K.check(PKG + "ClassPage.treeOpen" in g.get("ClassHubOpen.openOn", set()) and PKG + "ClassPage.treeOpen" in g.get("ClassPage.handleDataEvent", set()),
            "TREE: openOn and the class list's Class tab ask ClassPage.treeOpen (bytecode)")
    z = zipfile.ZipFile(jar)
    allb = b"".join(z.read(n) for n in z.namelist() if n.endswith(".class"))
    K.check(b"/class shows your weapons" not in allb and b" - your weapons: " in allb, "TREE: the weapon refusal names the weapons itself (no '/class shows your weapons')")
    K.check(b"open /tree, class tab" in allb, "TREE: the 'open /tree, class tab' line is kept (still right)")
    E.bridge.remove("profile:class:" + us)
    K.save()


def run_old():
    sc = os.path.join(os.path.dirname(SCRATCH), "cls-old")
    p = subprocess.run([sys.executable, os.path.join(HERE, "test_skyyclasses_0.1.27.py"), "--jar", JAR, "--dir", sc],
                       env=dict(os.environ), capture_output=True, text=True, encoding="utf-8", errors="replace")
    open(os.path.join(os.path.dirname(SCRATCH), "cls-old.log"), "w", encoding="utf-8").write(p.stdout + "\n" + p.stderr)
    lines = p.stdout.splitlines()
    oks = [l for l in lines if l.endswith("fail(s)") and " ok, " in l]
    failed = [l.strip()[len("FAIL: "):] for l in lines if l.strip().startswith("FAIL: ")]
    unexp = [l.strip()[len("OLD unexpected: "):] for l in lines if l.strip().startswith("OLD unexpected: ")]
    exp, bad = [], []
    for f in failed:
        (exp if [e for e in EXPECTED_OLD if f.startswith(e[0])] else bad).append(f)
    # the nested 0.1.26 harness's unexpected lines: only its compare phase may differ - it compares 0.1.25 -> 0.1.26 against our jar, and
    # its own run_compare26 no longer fits harness_kit's run_compare call (SkyyCore 2026-10-15 added the removed= argument: "takes 6
    # positional arguments but 7 were given" - the same on the 0.1.27 jar, checked 2026-10-15), so its compare child exits 1
    bad += ["nested 0.1.26: " + x for x in unexp if not x.startswith("compare: ")]
    return oks, bad, exp, unexp, p.returncode


if __name__ == "__main__":
    if "--phase" not in sys.argv and "--no-old" not in sys.argv:
        oks, bad, exp, unexp, rc = run_old()
        print("OLD. the 0.1.27 harness on the 0.1.28 jar: %s; %d expected identity checks differ, %d other failure(s)" % (oks[-1:] or "no summary", len(exp), len(bad)))
        for e in exp:
            print("  note (old): expected on 0.1.28: %s" % e[:240])
        for x in unexp:
            print("  note (old, nested 0.1.26): %s" % x[:240])
        for b in bad:
            print("  OLD unexpected: %s" % b[:400])
        HK.check(bool(oks), "OLD: the 0.1.27 harness ran to its summary")
        HK.check(not bad, "OLD: no failure outside the listed identity checks: %s" % bad[:5])
    HK.run(name="SkyyClasses", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("tree", run_tree)], script=__file__)
