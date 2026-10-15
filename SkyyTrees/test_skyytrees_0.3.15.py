"""SkyyTrees 0.3.15 - harness for HUBS H3a (the Character hub's Trees tab: /tree - the template trees and the class tab - in the Sky
Window hub shell; tools/trees_0_3_15_patch.py). Build first: python tools/trees_0_3_15_patch.py && python SkyyTrees/build_skyytrees_0.3.15.py

    python SkyyTrees/test_skyytrees_0.3.15.py [--dir <empty folder inside tools/dev/scratch/>] [--keep] [--no-old]

Every JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch. The live save data is only READ and copied.
  OLD14  the WHOLE 0.3.14 harness on the 0.3.15 jar (--prev 0.3.14): load + verify, the base-sap scenarios SP, every 0.3.11 replant
         scenario RP, START TWICE on a scratch COPY of the live Skyy_SkyyTrees (= 0.3.14's start), the audit. Its CC / JT lines pin the
         0.3.13 -> 0.3.14 change set and are expected to differ (EXPECTED14, each with its reason; ours: C below)
  OLD13  the WHOLE 0.3.13 harness on the 0.3.15 jar (--prev 0.3.14) with the REAL SkyyClasses 0.1.26: X1-X5 + the fuzz + LY (THE CLASS TAB
         PAGE on the real classes: every click path, the layout model of every rendered page) + its start twice. Its CC / JT lines and the
         checks that pin the 0.3.14 window (the class tab 1600 wide, its gaps) are expected to differ (EXPECTED13)
  A    verify   every class loads + initialises with -Xverify:all (tools/harness_kit.py)
  C    compare  0.3.14 -> 0.3.15: + HubBar, TreesHubOpen; TreePage build / buildClass / handleDataEvent, the plugin's setup / shutdown, the
                version texts; non-class entries: manifest.json + the 59 Sky Window kit files
  HUB  EXECUTED (tools/hub_tab_kit.py: the SkyyMenu 0.3.19 harness's engine stand-ins, the REAL PageManager, -Xverify:all):
       REG   TreesHubOpen.register() = hub:tab:character:trees {"SkyyTrees", "Trees", 30, "tree", TreesHubOpen, null} (the contract row
             SUI.HUB_TABS); unregister() removes it, never another jar's array; setup / shutdown call them (bytecode)
       OPEN  the open Function: not a UUID / an offline player = FALSE; a player = TRUE, /tree on the LAST tree (TreePage.LASTTREE)
       PAGE  the template trees (1454 x 980) and the class tab (1600 x 980, class trees on) built into REAL builders and checked as hub pages
             (hub_tab_kit.page_check: Sky Window shell, <= 1600 x 980, every contract tab fits, the body content under the strip, one tab
             per visible tab, Trees selected, bindings, every set / binding names an element); the page's own tree tabs still switch
       CLICK the bar: the Trees tab clears the result line + disarms a pending Respec (the page stays); another tab through its Function /
             the command fallback; a hidden / missing tab = the page stays and says so; < Menu with / without SkyyMenu; the X closes
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

VERSION = "0.3.15"
PKG = "com.skyy.trees."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyTrees-0.3.14.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "hubsH3a", "tr")))
ADDED = ["HubBar", "TreesHubOpen"]
EXPECT = {"TreePage": ["~m build", "~m buildClass", "~m handleDataEvent"], "SkyyTreesPlugin": ["~m setup", "~m shutdown"],
          "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "TreeCfg": ["~m load"]}       # the version texts (constant pools checked)
if HK.arg("--phase") == "compare":
    HT.allow_kit_entries()
FAIL_TEXT = "That tab could not open right now - try again."
EXPECTED14 = [
    ("CC: no class added or removed: ['HubBar', 'TreesHubOpen'] []", "+ HubBar, TreesHubOpen (0.3.15; ours: phase C)"),
    ("CC: structural changes only in TreeGather + TreeCfg (+ the ready line in SkyyTreesPlugin.setup):", "0.3.15 changes TreePage + the plugin (ours: C)"),
    ("CC: the only new field is TreeCfg.SAP_BASE (double):", "it compares 0.3.14 -> 0.3.15, which has no new field in TreeCfg (ours: C)"),
    ("JT: every asset is byte for byte 0.3.13's: ['Common/UI/Custom/SkyyKit/", "+ the 59 Sky Window kit files (ours: C + the build's check_jar_kit)"),
    ("JT: manifest = 0.3.13's but the version (+ description)", "it maps 0.3.13 -> 0.3.14 in the text; ours (MF below): 0.3.14 -> 0.3.15 differ in Name / Version only"),
]
EXPECTED13 = [
    ("CC: ", "its compare is 0.3.12 -> 0.3.13 (ours: phase C)"),
    ("JT: ", "+ the 59 Sky Window kit files (ours: C)"),
]


def run_hub(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    J = lambda n: JClass(PKG + n)
    Sto, Cfg, Defs, HO, HB, Page = J("TreeStore"), J("TreeCfg"), J("TreeDefs"), J("TreesHubOpen"), J("HubBar"), J("TreePage")
    Sto.DIR = E.Paths.get(scratch, "hub-mods", "Skyy_SkyyTrees", "players")
    os.makedirs(os.path.join(scratch, "hub-mods", "Skyy_SkyyTrees", "players"), exist_ok=True)
    P = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-0000000000a9"), "TreeHub")
    u = P.pr.getUuid()
    K.check(E.same(HB.map(), E.bridge), "the kit HubBar and the harness share ONE bridge map (skyy.bridge)")
    # ---------------------------------------------------------------- REG
    K.eq(str(HO.register()), "character:trees", "REG: register() answers the tab it put")
    HT.reg_check(K, E, "character", "trees", "SkyyTrees", "Trees", 30, "tree", PKG + "TreesHubOpen")
    K.eq(int(HO.unregister()), 1, "REG: unregister() removes our 1 key")
    K.check(E.bridge.get("hub:tab:character:trees") is None, "REG: the tab is gone after unregister()")
    HO.register()
    other = JClass("java.lang.Object")()
    E.bridge.put("hub:tab:character:trees", other)
    K.eq(int(HO.unregister()), 0, "REG: unregister() leaves another jar's value under the same key")
    K.check(E.same(E.bridge.get("hub:tab:character:trees"), other), "REG: ... and it is still there")
    E.bridge.remove("hub:tab:character:trees")
    HO.register()
    g = PW.calls(jar)
    K.check(PKG + "TreesHubOpen.register" in g.get("SkyyTreesPlugin.setup", set()), "REG: setup() calls TreesHubOpen.register (bytecode)")
    K.check(PKG + "TreesHubOpen.unregister" in g.get("SkyyTreesPlugin.shutdown", set()), "REG: shutdown() calls TreesHubOpen.unregister (bytecode)")
    K.check(PKG + "HubBar.handle" in g.get("TreePage.handleDataEvent", set()) and PKG + "HubBar.build" in g.get("TreePage.build", set())
            and PKG + "HubBar.build" in g.get("TreePage.buildClass", set()), "REG: both views draw the bar, handleDataEvent asks HubBar.handle (bytecode)")
    # ---------------------------------------------------------------- OPEN
    fn = HO()
    K.check(fn.apply("not a uuid") == E.FALSE and fn.apply(E.UUID.randomUUID()) == E.FALSE, "OPEN: not a UUID / an offline player = FALSE")

    def open_page():
        r = fn.apply(u)
        E.pump(P)
        pg = E.pg(P)
        return pg if (r == E.TRUE and pg is not None and str(pg.getClass().getName()) == PKG + "TreePage") else None
    Page.LASTTREE.put(u, JClass("java.lang.Integer").valueOf(2))
    pg = open_page()
    K.check(pg is not None and int(pg.tree) == 2 and int(HO.OPENED) >= 1, "OPEN: a player = TRUE, /tree on the last tree (Farming, 2)")

    def click(p_, a):
        p_.handleDataEvent(P.ref, P.st, '{"a":"%s"}' % a)
        E.pump(P)
        return E.pg(P)
    # ---------------------------------------------------------------- PAGE: a template tree, the class tab
    built = HT.build(pg, P)
    w, h, sets, evs = HT.page_check(K, E, P, built, "SkyyTrF", "character", "trees", "Trees", "PAGE tree", idp="SkyyTr")
    K.eq((w, h), (1454, 980), "PAGE tree: 1454 x 980 (0.3.14's 1440 x 941 + the strip + the sky padding, 27 px of margins given up)")
    seps = [t for ty, s_, t, d in built[0] if t and t.startswith("Group { Anchor: (Height: 1") and "Top: 3, Bottom: 3" in t]
    K.check(len(seps) == 1, "PAGE tree: the separator above the grid keeps 3 + 3 px (%d)" % len(seps))
    cur = click(pg, "trtab0")
    K.check(E.same(cur, pg) and int(pg.tree) == 0, "PAGE the page's own tree tab still switches (Mining)")
    Cfg.CLASS_ON = True
    pg.tree = int(Defs.NT)
    built = HT.build(pg, P)
    w2, h2, sets2, evs2 = HT.page_check(K, E, P, built, "SkyyTrF", "character", "trees", "Trees", "PAGE class tab", idp="SkyyTr")
    K.eq((w2, h2), (1600, 980), "PAGE class tab: 1600 x 980 (0.3.14's 1600 x 941; its gaps 12 / 16 -> 5 / 9 make room for the sky padding)")
    det = [t for ty, s_, t, d in built[0] if t and t.startswith("Group #SkyyTrDet ")]
    ap = [t for ty, s_, t, d in built[0] if t and t.startswith("Group #SkyyTrAp ")]
    K.check(det and "Left: 9" in det[0] and ap and "Left: 5" in ap[0], "PAGE class tab: the detail well 9 px, the Abilities well 5 px from their left neighbours")
    pg.tree = 0
    # ---------------------------------------------------------------- CLICK
    fakes = HT.Fakes(E, "character")

    def open_armed():
        p_ = open_page()
        p_.msg = "x"
        p_.armT = 2
        return p_
    HT.clicks(K, E, P, open_armed, "character", "trees", "CLICK", fakes,
              self_check=lambda p_: str(p_.msg) == "" and int(p_.armT) == -1, fail_text=FAIL_TEXT)
    p_ = open_page()
    E.CM.lines.clear()
    click(p_, "trback")
    K.check([str(x) for x in E.CM.lines] in ([], ["skills"]), "CLICK the page's own < Skills still works (%s)" % list(E.CM.lines))
    fakes.remove()
    K.save()


def run_old(script, prev, expected, tag):
    sc = os.path.join(os.path.dirname(SCRATCH), "tr-" + tag)
    p = subprocess.run([sys.executable, os.path.join(HERE, script), "--jar", JAR, "--prev", prev, "--dir", sc],
                       env=dict(os.environ), capture_output=True, text=True, encoding="utf-8", errors="replace")
    open(os.path.join(os.path.dirname(SCRATCH), "tr-%s.log" % tag), "w", encoding="utf-8").write(p.stdout + "\n" + p.stderr)
    lines = p.stdout.splitlines()
    oks = [l for l in lines if l.endswith("fail(s)") and " ok, " in l]
    failed = [l.strip()[len("FAIL: "):] for l in lines if l.strip().startswith("FAIL: ")]
    exp, bad = [], []
    for f in failed:
        (exp if [e for e in expected if f.startswith(e[0])] else bad).append(f)
    print("%s. %s on the 0.3.15 jar: %s; %d expected differences, %d other failure(s)" % (tag, script, oks[-1:] or "no summary", len(exp), len(bad)))
    for e in exp:
        print("  note (%s): expected on 0.3.15: %s" % (tag, e[:240]))
    for b in bad:
        print("  %s unexpected: %s" % (tag, b[:400]))
    HK.check(bool(oks), "%s: %s ran to its summary" % (tag, script))
    HK.check(not bad, "%s: no failure outside the listed differences: %s" % (tag, bad[:5]))


def check_manifest():
    import zipfile
    a = json.loads(zipfile.ZipFile(OLD_JAR).read("manifest.json"))
    b = json.loads(zipfile.ZipFile(JAR).read("manifest.json"))
    d = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
    HK.check(d == ["Name", "Version"] and b["Version"] == VERSION and b["Name"] == VERSION + " SkyyTrees" and b.get("IncludesAssetPack") is True,
             "MF: the manifest = 0.3.14's but Name / Version (%s)" % d)


if __name__ == "__main__":
    if "--phase" not in sys.argv:
        check_manifest()
    if "--phase" not in sys.argv and "--no-old" not in sys.argv:
        run_old("test_skyytrees_0.3.14.py", OLD_JAR, EXPECTED14, "OLD14")
        run_old("test_skyytrees_0.3.13.py", OLD_JAR, EXPECTED13, "OLD13")
    HK.run(name="SkyyTrees", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("hub", run_hub)], script=__file__)
