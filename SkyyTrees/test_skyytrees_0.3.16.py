"""SkyyTrees 0.3.16 - harness for "the Class tab opens the class tree" (tree:fn:classPage + Class tab mode; tools/trees_0_3_16_patch.py;
with SkyyClasses 0.1.28). Build first: python tools/trees_0_3_16_patch.py && python SkyyTrees/build_skyytrees_0.3.16.py

    python SkyyTrees/test_skyytrees_0.3.16.py [--dir <empty folder inside tools/dev/scratch/>] [--no-old]

Every JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch. The live save data is only READ and copied (old harnesses).
  OLD15  the WHOLE 0.3.15 harness on the 0.3.16 jar (it runs the whole 0.3.14 + 0.3.13 harnesses itself, on this jar): every hub / page /
         click check of 0.3.15 must pass (without Class tab mode nothing changed); its compare / manifest lines pin 0.3.14 -> 0.3.15 and
         are expected to differ (EXPECTED15, each with its reason; ours: C + MF below)
  X13    the 0.3.13 harness's X child (the class tab click paths + the layout model, with the REAL SkyyClasses 0.1.26 and 0.1.28) and its RP
         child run again on THIS jar (the nested run starts them without --jar: see NESTED_OK13)
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.15 -> 0.3.16: + TreeClassHub; TreePage (+ chub, + hubSel, <init>, buildClass, handleDataEvent), the plugin's setup /
                shutdown, the version texts; non-class entries: manifest.json only
  CT   EXECUTED (tools/hub_tab_kit.py engine stand-ins, the REAL PageManager, -Xverify:all):
       REG   TreeClassHub.register() puts tree:fn:classPage (a Function); unregister() removes only ours; setup / shutdown call them
       OPEN  not a UUID / an offline player / class trees off / no class / a class without a tree = FALSE; a Mage = TRUE and the open
             page is the tree page on the CLASS TAB in Class tab mode; TreePage.LASTTREE untouched
       PAGE  Class tab mode built into a REAL builder and checked as a hub page with the CLASS tab selected (1600 x 980); the page's own
             tree tabs: a skill tree shows Trees selected, the class tab Class again; without Class tab mode the class tab shows Trees
       CLICK in Class tab mode: the Class tab keeps the page (result line cleared, Respec disarmed); other tabs / < Menu / X as the
             contract; the Trees tab switches in place to the last skill tree (LASTTREE; Mining for the class tree or none)
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, json, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW
import hub_tab_kit as HT

VERSION = "0.3.16"
PKG = "com.skyy.trees."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyTrees-0.3.15.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "class0128", "tr")))
ADDED = ["TreeClassHub"]
EXPECT = {"TreePage": ["+f chub", "+m hubSel", "~c ", "~m buildClass", "~m handleDataEvent"], "SkyyTreesPlugin": ["~m setup", "~m shutdown"],
          "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "TreeCfg": ["~m load"]}       # the version texts
FAIL_TEXT = "That tab could not open right now - try again."
EXPECTED15 = [
    ("compare: C: classes added", "its compare is 0.3.14 -> 0.3.15 against our jar: + TreeClassHub (ours: phase C)"),
    ("compare: C: TreePage members", "0.3.16 adds TreePage.chub / hubSel and changes its constructor (ours: phase C)"),
    ("MF: the manifest = 0.3.14's but Name / Version", "it pins version 0.3.15"),
    ("OLD14: no failure outside the listed differences", "its nested 0.3.14 harness sees the 0.3.16 compare set (+ TreeClassHub): CC lines (ours: C)"),
    ("OLD13: no failure outside the listed differences", "its nested 0.3.13 harness sees the 0.3.16 compare set: CC lines (ours: C)"),
]
NESTED_OK = ("CC: ",)      # the nested 0.3.14 / 0.3.13 harnesses' unexpected lines that may differ: their class compares only
# + the nested 0.3.13 harness's X / LV / RP children: they are started WITHOUT --jar, so they load the default SkyyTrees-0.3.13.jar, which
# tools/tidy_local.py has packed away - "Class com.skyy.trees.TreeClass is not found" (the same on the 0.3.15 jar). X13 below runs its X
# (the class tab click paths + the layout model of every page) and RP children again ON THIS JAR, with the real SkyyClasses 0.1.26 and 0.1.28
NESTED_OK13 = ("X ran", "LV ran", "RP ran")


def run_ct(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JArray, JObject
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    J = lambda n: JClass(PKG + n)
    Sto, Cfg, Defs, HO, CH, Page = J("TreeStore"), J("TreeCfg"), J("TreeDefs"), J("TreesHubOpen"), J("TreeClassHub"), J("TreePage")
    Sto.DIR = E.Paths.get(scratch, "ct-mods", "Skyy_SkyyTrees", "players")
    os.makedirs(os.path.join(scratch, "ct-mods", "Skyy_SkyyTrees", "players"), exist_ok=True)
    P = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-0000000000b4"), "ClassTab")
    u = P.pr.getUuid()
    us = str(u)
    Int = JClass("java.lang.Integer")
    NT = int(Defs.NT)
    Fn = JClass("java.util.function.Function")
    # ---------------------------------------------------------------- REG
    K.eq(str(CH.register()), "on", "REG: register() puts tree:fn:classPage")
    f0 = E.bridge.get("tree:fn:classPage")
    K.check(f0 is not None and Fn.class_.isInstance(f0) and str(f0.getClass().getName()) == PKG + "TreeClassHub", "REG: tree:fn:classPage = a TreeClassHub Function")
    CH.unregister()
    K.check(E.bridge.get("tree:fn:classPage") is None, "REG: unregister() removes it")
    CH.register()
    other = JClass("java.lang.Object")()
    E.bridge.put("tree:fn:classPage", other)
    CH.unregister()
    K.check(E.same(E.bridge.get("tree:fn:classPage"), other), "REG: unregister() leaves another jar's value under the key")
    E.bridge.remove("tree:fn:classPage")
    CH.register()
    HO.register()
    g = PW.calls(jar)
    K.check(PKG + "TreeClassHub.register" in g.get("SkyyTreesPlugin.setup", set()), "REG: setup() calls TreeClassHub.register (bytecode)")
    K.check(PKG + "TreeClassHub.unregister" in g.get("SkyyTreesPlugin.shutdown", set()), "REG: shutdown() calls TreeClassHub.unregister (bytecode)")
    K.check(PKG + "TreePage.hubSel" in g.get("TreePage.buildClass", set()) and PKG + "TreePage.hubSel" in g.get("TreePage.handleDataEvent", set()),
            "REG: the class view's bar and the click handler use hubSel() (bytecode)")
    # a stand-in for SkyyClasses' Class tab (its row of the contract), so the strip shows Class
    @JImplements("java.util.function.Function")
    class Stub:
        def __init__(self):
            self.calls = []

        @JOverride
        def apply(self, o):
            self.calls.append(str(o))
            return E.TRUE
    stub = Stub()
    S = JClass("java.lang.String")
    E.bridge.put("hub:tab:character:class", JArray(JObject)([S("SkyyClasses"), S("Class"), Int.valueOf(40), S("class"), stub, None]))
    # ---------------------------------------------------------------- OPEN
    fn = CH()
    Page.LASTTREE.put(u, Int.valueOf(2))
    Cfg.CLASS_ON = True
    K.check(fn.apply("not a uuid") == E.FALSE and fn.apply(E.UUID.randomUUID()) == E.FALSE, "OPEN: not a UUID / an offline player = FALSE")
    K.check(fn.apply(u) == E.FALSE and E.pg(P) is None, "OPEN: no class = FALSE, nothing opens (SkyyClasses shows its list)")
    E.bridge.put("class:" + us, "Mage")
    Cfg.CLASS_ON = False
    K.check(fn.apply(u) == E.FALSE and E.pg(P) is None, "OPEN: class trees off = FALSE")
    Cfg.CLASS_ON = True
    E.bridge.put("class:" + us, "Necromancer")     # (Shaman is an alias of Monk)
    K.check(fn.apply(u) == E.FALSE and E.pg(P) is None, "OPEN: a class without a tree = FALSE")
    E.bridge.put("class:" + us, "Mage")

    def open_chub():
        r = fn.apply(u)
        E.pump(P)
        pg = E.pg(P)
        return pg if (r == E.TRUE and pg is not None and str(pg.getClass().getName()) == PKG + "TreePage") else None
    pg = open_chub()
    K.check(pg is not None and int(pg.tree) == NT and bool(pg.chub) and int(CH.OPENED) >= 1, "OPEN: a Mage = TRUE, the tree page on the CLASS TAB in Class tab mode")
    K.check(int(Page.LASTTREE.get(u)) == 2, "OPEN: TreePage.LASTTREE untouched (the Trees tab keeps the last skill tree)")
    K.eq(str(pg.hubSel()), "class", "OPEN: hubSel() = class")

    def click(p_, a):
        p_.handleDataEvent(P.ref, P.st, '{"a":"%s"}' % a)
        E.pump(P)
        return E.pg(P)
    # ---------------------------------------------------------------- PAGE
    built = HT.build(pg, P)
    w, h, sets, evs = HT.page_check(K, E, P, built, "SkyyTrF", "character", "class", "Class", "PAGE class tree (Class tab mode)", idp="SkyyTr")
    K.eq((w, h), (1600, 980), "PAGE class tree: 0.3.15's class tab window 1600 x 980")
    marks = " ".join(t for ty, s_, t, d in built[0] if t)
    K.check("#SkyyTrNoClass" not in marks or "Choose a class" not in " ".join(str(d) for ty, s_, t, d in built[0] if d),
            "PAGE class tree: the Mage's tree (not the 'choose a class' text)")
    cur = click(pg, "trtab0")
    K.check(E.same(cur, pg) and int(pg.tree) == 0 and str(pg.hubSel()) == "trees", "PAGE own tree tab Mining: hubSel() = trees")
    HT.page_check(K, E, P, HT.build(pg, P), "SkyyTrF", "character", "trees", "Trees", "PAGE Mining (from Class tab mode)", idp="SkyyTr")
    cur = click(pg, "trtab%d" % NT)
    K.check(E.same(cur, pg) and int(pg.tree) == NT and str(pg.hubSel()) == "class", "PAGE own class tab again: hubSel() = class")
    HT.page_check(K, E, P, HT.build(pg, P), "SkyyTrF", "character", "class", "Class", "PAGE class tree again", idp="SkyyTr")
    # without Class tab mode (/tree, the Trees tab) the class tab keeps Trees selected
    Page.LASTTREE.put(u, Int.valueOf(NT))
    r = HO().apply(u)
    E.pump(P)
    tp = E.pg(P)
    K.check(r == E.TRUE and tp is not None and int(tp.tree) == NT and not bool(tp.chub) and str(tp.hubSel()) == "trees",
            "PAGE the Trees tab on the class tree: not Class tab mode, hubSel() = trees")
    HT.page_check(K, E, P, HT.build(tp, P), "SkyyTrF", "character", "trees", "Trees", "PAGE class tree via the Trees tab", idp="SkyyTr")
    # ---------------------------------------------------------------- CLICK (Class tab mode)
    fakes = HT.Fakes(E, "character")

    def open_armed():
        p_ = open_chub()
        p_.msg = "x"
        p_.armT = 2
        return p_
    HT.clicks(K, E, P, open_armed, "character", "class", "CLICK class mode", fakes,
              self_check=lambda p_: str(p_.msg) == "" and int(p_.armT) == -1 and bool(p_.chub) and int(p_.tree) == NT, fail_text=FAIL_TEXT)
    for last, want, why in ((2, 2, "Farming (the last skill tree)"), (NT, 0, "Mining (the last tree was the class tree)"), (None, 0, "Mining (no last tree)")):
        if last is None:
            Page.LASTTREE.remove(u)
        else:
            Page.LASTTREE.put(u, Int.valueOf(last))
        p_ = open_chub()
        n0 = len(E.CM.lines)
        cur = click(p_, "hub:trees")
        K.check(E.same(cur, p_) and int(p_.tree) == want and not bool(p_.chub) and str(p_.hubSel()) == "trees" and len(E.CM.lines) == n0
                and int(Page.LASTTREE.get(u)) == want, "CLICK class mode: the Trees tab switches in place to %s" % why)
    HT.page_check(K, E, P, HT.build(p_, P), "SkyyTrF", "character", "trees", "Trees", "CLICK ... then the page is the Trees tab", idp="SkyyTr")
    # review fix: Class tab -> the page's own Farming tab -> its own Class tab -> the hub Trees tab = Farming (LASTTREE kept on the skill tree)
    Page.LASTTREE.put(u, Int.valueOf(0))
    p_ = open_chub()
    cur = click(p_, "trtab2")
    K.check(E.same(cur, p_) and int(p_.tree) == 2 and int(Page.LASTTREE.get(u)) == 2, "CLICK class mode: the own Farming tab records LASTTREE = Farming")
    cur = click(p_, "trtab%d" % NT)
    K.check(E.same(cur, p_) and int(p_.tree) == NT and bool(p_.chub) and int(Page.LASTTREE.get(u)) == 2,
            "CLICK class mode: the own Class tab keeps LASTTREE on Farming (%s)" % Page.LASTTREE.get(u))
    cur = click(p_, "hub:trees")
    K.check(E.same(cur, p_) and int(p_.tree) == 2 and not bool(p_.chub), "CLICK class mode: ... then the hub Trees tab lands on Farming (the last skill tree)")
    tp = HO()
    Page.LASTTREE.put(u, Int.valueOf(2))
    tp.apply(u)
    E.pump(P)
    tq = E.pg(P)
    cur = click(tq, "trtab%d" % NT)
    K.check(not bool(tq.chub) and int(Page.LASTTREE.get(u)) == NT, "CLICK without Class tab mode the own Class tab still records LASTTREE (as 0.3.15)")
    fakes.remove()
    E.bridge.remove("hub:tab:character:class")
    E.bridge.remove("class:" + us)
    K.save()


def run_old():
    sc = os.path.join(os.path.dirname(SCRATCH), "tr-old")
    p = subprocess.run([sys.executable, os.path.join(HERE, "test_skyytrees_0.3.15.py"), "--jar", JAR, "--dir", sc],
                       env=dict(os.environ), capture_output=True, text=True, encoding="utf-8", errors="replace")
    open(os.path.join(os.path.dirname(SCRATCH), "tr-old.log"), "w", encoding="utf-8").write(p.stdout + "\n" + p.stderr)
    lines = p.stdout.splitlines()
    oks = [l for l in lines if l.endswith("fail(s)") and " ok, " in l]
    failed = [l.strip()[len("FAIL: "):] for l in lines if l.strip().startswith("FAIL: ")]
    nested = [l.strip() for l in lines if re.match(r"\s+OLD1[34] unexpected: ", l)]
    exp, bad = [], []
    for f in failed:
        (exp if [e for e in EXPECTED15 if f.startswith(e[0])] else bad).append(f)
    for x in nested:
        body = x.split("unexpected: ", 1)[1]
        if not body.startswith(NESTED_OK) and not (x.startswith("OLD13 ") and body in NESTED_OK13):
            bad.append("nested: " + x)
    print("OLD15. test_skyytrees_0.3.15.py on the 0.3.16 jar: %s; %d expected differences, %d other failure(s)" % (oks[-1:] or "no summary", len(exp), len(bad)))
    for e in exp:
        print("  note (OLD15): expected on 0.3.16: %s" % e[:240])
    for x in nested:
        print("  note (OLD15 nested): %s" % x[:240])
    for b in bad:
        print("  OLD15 unexpected: %s" % b[:400])
    HK.check(bool(oks), "OLD15: test_skyytrees_0.3.15.py ran to its summary")
    HK.check(not bad, "OLD15: no failure outside the listed differences: %s" % bad[:5])


def run_x13():
    """the 0.3.13 harness's X child (with the real SkyyClasses 0.1.26, then 0.1.28) and RP child, on THIS jar (see NESTED_OK13)"""
    for tag, args, need in (("X13-cls0126", ["--x"], 90), ("X13-cls0128", ["--x", "--classes", os.path.join(ROOT, "SkyyClasses", "SkyyClasses-0.1.28.jar")], 90),
                            ("RP13", ["--rp"], 65)):
        sc = os.path.join(os.path.dirname(SCRATCH), tag.lower())
        import shutil
        shutil.rmtree(sc, ignore_errors=True)
        os.makedirs(os.path.join(sc, "tmp"), exist_ok=True)
        env = dict(os.environ, TEMP=os.path.join(sc, "tmp"), TMP=os.path.join(sc, "tmp"), JAVA_TOOL_OPTIONS="-XX:-UsePerfData")
        out = os.path.join(sc, "out.json")
        with open(os.path.join(sc, "out.log"), "wb") as lf:
            subprocess.run([sys.executable, os.path.join(HERE, "test_skyytrees_0.3.13.py")] + args + ["--out", out, "--dir", sc, "--jar", JAR, "--prev", OLD_JAR],
                           env=env, stdout=lf, stderr=subprocess.STDOUT, cwd=sc)
        x = json.load(open(out)) if os.path.isfile(out) else {}
        ch = x.get("checks", [])
        bad = [w for ok, w in ch if not ok] + ["%s: %s" % (t_, p_["err"]) for t_, p_ in x.get("pages", {}).items() if p_.get("err")]
        print("%s. %d executed checks, %d page(s) built, %d failure(s)" % (tag, len(ch), len(x.get("pages", {})), len(bad)))
        for b in bad:
            print("  %s: %s" % (tag, b[:300]))
        HK.check(len(ch) >= need and not bad, "%s: the 0.3.13 harness's %s child on the 0.3.16 jar: %d checks, no failure %s" % (tag, args[0], len(ch), bad[:3]))
        shutil.rmtree(sc, ignore_errors=True)


def check_manifest():
    import zipfile
    a = json.loads(zipfile.ZipFile(OLD_JAR).read("manifest.json"))
    b = json.loads(zipfile.ZipFile(JAR).read("manifest.json"))
    d = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
    HK.check(d == ["Name", "Version"] and b["Version"] == VERSION and b["Name"] == VERSION + " SkyyTrees" and b.get("IncludesAssetPack") is True,
             "MF: the manifest = 0.3.15's but Name / Version (%s)" % d)


if __name__ == "__main__":
    if "--phase" not in sys.argv:
        check_manifest()
    if "--phase" not in sys.argv and "--no-old" not in sys.argv:
        run_old()
        run_x13()
    HK.run(name="SkyyTrees", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("ct", run_ct)], script=__file__)
