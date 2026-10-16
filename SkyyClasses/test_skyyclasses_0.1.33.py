"""Harness for SkyyClasses 0.1.33 (round hubchar: the Class tab is part of the Trees tab - a MERGED tab, kit skyyui HUB_MERGED;
tools/classes_0_1_33_patch.py). Build first:
    python tools/classes_0_1_33_patch.py && python SkyyClasses/build_skyyclasses_0.1.33.py
    python SkyyClasses/test_skyyclasses_0.1.33.py [--keep]
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in tools/dev/scratch/hubchar/cls):
  A   verify   every class loads + initialises
  C   compare  0.1.32 -> 0.1.33: exactly the planned members (EXPECT), + HubHide; non-class entries: manifest.json only
  HUB EXECUTED (tools/hub_tab_kit.py: the SkyyMenu 0.3.19 harness's engine stand-ins, the REAL PageManager, -Xverify:all), with a stand-in
      SkyyTrees Trees tab (its row of the contract) on the bridge:
      REG   ClassHubOpen.register() = hub:tab:character:class {"SkyyClasses", "Class", 40, "class", ClassHubOpen, HubHide, "character_class",
            "trees"} (8 elements); HubHide answers FALSE while the Trees tab is published, TRUE without it; HubBar.tabs leaves Class out
            (with Trees) / keeps it (without Trees); hostOf / hostTab / selOf; unregister() removes ours only
      OPEN  HubBar.openSub opens the Class page although its hide Function says FALSE (HubBar.open says "hidden" - the 0.1.32 kit rule)
      PAGE  the class list (no class) and the Abilities page built into REAL builders and checked as hub pages with TREES selected
            (hub_tab_kit.page_check), no Class tab in their strip; without SkyyTrees: Class selected again (a tab of its own)
      CLICK the bar on both pages (hub_tab_kit.clicks with the stand-in tabs): the Trees tab opens the tree page through ITS Function
  ST1 / ST2  START TWICE on a scratch COPY of the live Skyy_SkyyClasses folder (setup's order: migrations, load, CfgPub, the Class tab):
      neither start writes a file; the live folder is only read
  AA  engine-access audit
"""
import os, sys, json, shutil, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW
import hub_tab_kit as HT
import deploy_set as DS

VERSION, OLD = "0.1.33", "0.1.32"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % OLD)
PKG = "com.skyy.classes."
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "hubchar", "cls")))
LIVE = os.path.join(B.HYTALE, "UserData", "Saves", DS.WORLD, "mods", "Skyy_SkyyClasses")
FAIL_TEXT = "That tab could not open right now - try again."
ADDED = ["HubHide"]
SUBM = ["+m hostOf", "+m hostShown", "+m hostTab", "+m openSub", "+m putSub", "+m selOf", "+m subIcon", "+m subTabs"]
EXPECT = {
    "HubBar": SUBM,                                             # the kit's MERGED TABS methods
    "ClassHubOpen": ["~m register"],                            # putSub (merged into Trees)
    "ClassPage": ["~m build"], "AbilPage": ["~m build"],        # the strip: HubBar.selOf("character", "class")
    "SkyyClassesPlugin": ["~m setup"],                          # the version text
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "KitMigrate": ["~m runOnce"],          # the version text only
}


def tree_hash(root):
    o = {}
    for d, _x, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            o[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return o


def run_hub(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JArray, JObject
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    P_ = lambda n: JClass(PKG + n)
    Cfg, Store, AS, Defs, HO, HB, Hide = P_("ClassCfg"), P_("ClassStore"), P_("AbilStore"), P_("ClassDefs"), P_("ClassHubOpen"), P_("HubBar"), P_("HubHide")
    base = os.path.join(scratch, "hub-mods", "Skyy_SkyyClasses")
    os.makedirs(base, exist_ok=True)
    Cfg.FILE = E.Paths.get(base, "config.properties")
    Store.DIR = E.Paths.get(base, "players")
    AS.DIR = E.Paths.get(base, "abilities")
    P = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-0000000001c3"), "ClassMerge")
    u = P.pr.getUuid()
    S, Int = JClass("java.lang.String"), JClass("java.lang.Integer")
    Fn = JClass("java.util.function.Function")
    K.check(E.same(HB.map(), E.bridge), "the kit HubBar and the harness share ONE bridge map (skyy.bridge)")

    @JImplements("java.util.function.Function")
    class TreesFn:
        def __init__(self):
            self.calls = []

        @JOverride
        def apply(self, o):
            self.calls.append(str(o))
            return E.TRUE
    tfn = TreesFn()
    trees = JArray(JObject)([S("SkyyTrees"), S("Trees"), Int.valueOf(30), S("tree"), tfn, None])

    def trees_on():
        E.bridge.put("hub:tab:character:trees", trees)

    def trees_off():
        E.bridge.remove("hub:tab:character:trees")
    trees_on()
    # ---------------------------------------------------------------- REG
    K.eq(str(HO.register()), "character:class", "REG: register() answers the tab it put")
    e = E.bridge.get("hub:tab:character:class")
    ok = e is not None and len(e) == 8 and [str(x) for x in (e[0], e[1], e[3], e[6], e[7])] == ["SkyyClasses", "Class", "class", "character_class", "trees"] \
        and int(e[2]) == 40 and Fn.class_.isInstance(e[4]) and str(e[4].getClass().getName()) == PKG + "ClassHubOpen" \
        and e[5] is not None and str(e[5].getClass().getName()) == PKG + "HubHide"
    K.check(ok, "REG: hub:tab:character:class = {SkyyClasses, Class, 40, class, ClassHubOpen, HubHide, character_class, trees} (%s)" % (None if e is None else [str(x) for x in e]))
    K.check(e[5].apply(u) == E.FALSE, "REG: HubHide answers FALSE while the Trees tab is published")
    K.check([str(x) for x in HT.hub_tabs(E, "character", u)] == ["trees"], "REG: HubBar.tabs(character) leaves Class out (%s)" % HT.hub_tabs(E, "character", u))
    K.eq((str(HB.hostOf(e)), str(HB.hostTab("character", "class")), str(HB.selOf("character", "class")), str(HB.selOf("character", "trees"))),
         ("trees", "trees", "trees", "trees"), "REG: hostOf / hostTab / selOf (Trees selected while merged)")
    K.check(not bool(HB.visible(e, u)), "REG: the kit's visible() (every older HubBar copy) says hidden")
    trees_off()
    K.check(e[5].apply(u) == E.TRUE and [str(x) for x in HT.hub_tabs(E, "character", u)] == ["class"] and str(HB.selOf("character", "class")) == "class",
            "REG: without SkyyTrees' tab: HubHide = TRUE, Class is a tab of its own, selOf = class")
    # FIX (critic 1): an INVISIBLE Trees tab (e.g. SkyyMenu's stand-in while /tree is missing) is not a host
    @JImplements("java.util.function.Function")
    class Vis(object):
        def __init__(self, ans):
            self.ans = ans

        @JOverride
        def apply(self, o):
            return self.ans
    E.bridge.put("hub:tab:character:trees", JArray(JObject)([S("SkyyMenu"), S("Trees"), Int.valueOf(30), S("tree"), None, Vis(E.FALSE)]))
    K.check(e[5].apply(u) == E.TRUE and [str(x) for x in HT.hub_tabs(E, "character", u)] == ["class"] and str(HB.selOf("character", "class")) == "class",
            "REG FIX1: an invisible Trees tab: HubHide = TRUE, Class is a tab of its own, selOf = class")
    E.bridge.put("hub:tab:character:trees", JArray(JObject)([S("SkyyMenu"), S("Trees"), Int.valueOf(30), S("tree"), None, Vis(E.TRUE)]))
    K.check(e[5].apply(u) == E.FALSE and [str(x) for x in HT.hub_tabs(E, "character", u)] == ["trees"] and str(HB.selOf("character", "class")) == "trees",
            "REG FIX1: a visible stand-in Trees tab: Class hidden, selOf = trees")
    trees_on()
    K.check(HB.putSub("character", "x", "M", "X", 1, "x", None, None, None, "trees") is None and HB.putSub("character", "x", "M", "X", 1, "x", None, e[5], None, "x") is None
            and E.bridge.get("hub:tab:character:x") is None, "REG: putSub refuses a missing hide Function / a host = itself")
    K.eq(int(HO.unregister()), 1, "REG: unregister() removes our 1 key")
    K.check(E.bridge.get("hub:tab:character:class") is None, "REG: the tab is gone after unregister()")
    HO.register()
    other = JClass("java.lang.Object")()
    E.bridge.put("hub:tab:character:class", other)
    K.eq(int(HO.unregister()), 0, "REG: unregister() leaves another jar's value under the same key")
    E.bridge.remove("hub:tab:character:class")
    HO.register()
    g = PW.calls(jar)
    K.check(PKG + "HubBar.putSub" in g.get("ClassHubOpen.register", set()) and PKG + "HubHide.<init>" in g.get("ClassHubOpen.register", set()),
            "REG: register() puts the merged tab (HubBar.putSub + new HubHide) (bytecode)")
    for pc in ("ClassPage", "AbilPage"):
        K.check(PKG + "HubBar.selOf" in g.get(pc + ".build", set()), "REG: %s's strip asks HubBar.selOf (bytecode)" % pc)
    # ---------------------------------------------------------------- OPEN
    K.eq(str(HB.open(P.pr, u, "character", "class")), "hidden", "OPEN: the kit 1.5 open() (any older jar) says hidden for the merged tab")
    E.pump(P)
    r = str(HB.openSub(P.pr, u, "character", "class"))
    E.pump(P)
    pg = E.pg(P)
    K.check(r == "bridge" and pg is not None and str(pg.getClass().getName()) == PKG + "ClassPage", "OPEN: HubBar.openSub opens the class page (no class yet: the list) (%s)" % r)
    fn = HO()

    def cls_page():
        r_ = fn.apply(u)
        E.pump(P)
        p_ = E.pg(P)
        return p_ if (r_ == E.TRUE and p_ is not None and str(p_.getClass().getName()) == PKG + "ClassPage") else None
    # ---------------------------------------------------------------- PAGE
    pg = cls_page()
    built = HT.build(pg, P)
    w, h, sets, evs = HT.page_check(K, E, P, built, "SkyyClsF", "character", "trees", "Trees", "PAGE class list (merged: Trees selected)", idp="SkyyCls")
    K.eq((w, h), (1114, 980), "PAGE class list: 1114 x 980 as 0.1.32")
    K.check(not [t for ty, s_, t, d in built[0] if t and s_ == "#SkyyClsFHubTabs" and '"Class"' in t], "PAGE class list: no Class tab in its strip")
    trees_off()
    built2 = HT.build(pg, P)
    HT.page_check(K, E, P, built2, "SkyyClsF", "character", "class", "Class", "PAGE class list without SkyyTrees (Class a tab of its own)", idp="SkyyCls")
    trees_on()
    mage = [str(x) for x in Defs.NAMES].index("Mage")
    pg.handleDataEvent(P.ref, P.st, '{"a":"clspick%d"}' % mage)
    E.pump(P)
    pg.handleDataEvent(P.ref, P.st, '{"a":"clsyes"}')
    E.pump(P)
    K.check(int(Store.classIndex(u)) == mage, "PAGE the page's own pick + Confirm still work: a Mage (%s)" % pg.info)
    pg.handleDataEvent(P.ref, P.st, '{"a":"clsabil"}')
    E.pump(P)
    ab = E.pg(P)
    K.check(ab is not None and str(ab.getClass().getName()) == PKG + "AbilPage", "PAGE the Abilities button opens the Abilities page")
    if ab is not None:
        w2, h2, _s2, _e2 = HT.page_check(K, E, P, HT.build(ab, P), "SkyyAbF", "character", "trees", "Trees", "PAGE abilities (merged: Trees selected)", idp="SkyyAb")
        K.eq((w2, h2), (1114, 728), "PAGE abilities: 1114 x 728 as 0.1.32")
    # ---------------------------------------------------------------- CLICK
    fakes = HT.Fakes(E, "character")
    del tfn.calls[:]
    pg = cls_page()
    pg.handleDataEvent(P.ref, P.st, '{"a":"hub:trees"}')
    E.pump(P)
    K.check(tfn.calls == [str(u)] and not list(E.CM.lines), "CLICK class list: the Trees tab opens the tree page through its Function (%s)" % tfn.calls)

    def cls_pending():
        p_ = cls_page()
        p_.pending = 2
        p_.info = "x"
        return p_
    HT.clicks(K, E, P, cls_pending, "character", "class", "CLICK class", fakes,
              self_check=lambda p_: int(p_.pending) == -1 and str(p_.info) == "", fail_text=FAIL_TEXT)

    def abil_page():
        p_ = cls_page()
        p_.handleDataEvent(P.ref, P.st, '{"a":"clsabil"}')
        E.pump(P)
        return E.pg(P)
    HT.clicks(K, E, P, abil_page, "character", "class", "CLICK abilities", fakes, fail_text=FAIL_TEXT,
              self_new=lambda cur: str(cur.getClass().getName()) == PKG + "ClassPage")
    del tfn.calls[:]
    p_ = abil_page()
    p_.handleDataEvent(P.ref, P.st, '{"a":"hub:trees"}')
    E.pump(P)
    K.check(tfn.calls == [str(u)], "CLICK abilities: the Trees tab opens the tree page through its Function")
    fakes.remove()
    trees_off()
    K.save()


def run_st(out, jar, scratch, step):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Cfg, Pub, AS, HO = JClass(PKG + "ClassCfg"), JClass(PKG + "CfgPub"), JClass(PKG + "AbilStore"), JClass(PKG + "ClassHubOpen")
    Paths = JClass("java.nio.file.Paths")
    home = os.path.join(scratch, "st", "mods")
    base = os.path.join(home, "Skyy_SkyyClasses")
    if step == "1":
        shutil.rmtree(os.path.join(scratch, "st"), ignore_errors=True)
        shutil.copytree(LIVE, base)
        json.dump(tree_hash(LIVE), open(os.path.join(scratch, "st-live.json"), "w"))
    before = tree_hash(base)
    Cfg.FILE = Paths.get(os.path.join(base, "config.properties"))
    o = {"m10": str(Cfg.migrate0110()), "m29": str(Cfg.migrate0129()), "m32": str(Cfg.migrate0132()), "load": str(Cfg.load())}
    AS.DIR = Paths.get(os.path.join(base, "abilities"))
    Pub.start(Paths.get(home), None)
    reg = str(HO.register())
    Pub.flush()
    Pub.shutdown()
    HO.unregister()
    after = tree_hash(base)
    ch = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    K.check(not ch and reg == "character:class", "ST start %s on a scratch COPY of the live data (%d files): nothing written (%s), the Class tab put (%s) %s"
            % (step, len(before), ch, reg, o["m32"][:80]))
    if step == "2":
        K.check(tree_hash(LIVE) == json.load(open(os.path.join(scratch, "st-live.json"))), "ST: the live Skyy_SkyyClasses folder was only read")
    K.save()
    sys.stdout.flush()
    os._exit(0)


def run_st1(out, jar, scratch, _home):
    run_st(out, jar, scratch, "1")


def run_st2(out, jar, scratch, _home):
    run_st(out, jar, scratch, "2")


if __name__ == "__main__":
    HK.run(name="SkyyClasses", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("hub", run_hub), ("st1", run_st1), ("st2", run_st2)], script=__file__)
