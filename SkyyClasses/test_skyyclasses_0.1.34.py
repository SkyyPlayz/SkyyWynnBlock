"""Harness for SkyyClasses 0.1.34 (MENU PATTERN sweep S1: the class list + the Abilities page on the kit 1.7 hub_page, the ONE sub-tab row
of the Trees tab; tools/classes_0_1_34_patch.py). Derived from the 0.1.33 harness (same REG / OPEN / CLICK / ST phases). Build first:
    python tools/classes_0_1_34_patch.py && python SkyyClasses/build_skyyclasses_0.1.34.py
    python SkyyClasses/test_skyyclasses_0.1.34.py [--dir <folder inside tools/dev/scratch/>] [--keep]
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A   verify   every class loads + initialises
  C   compare  0.1.33 -> 0.1.34: exactly the planned members (EXPECT: the kit 1.7 HubBar members, ClassPage / AbilPage build +
               handleDataEvent, the version texts); non-class entries: manifest.json only
  HUB EXECUTED (tools/hub_tab_kit.py: the SkyyMenu 0.3.19 harness's engine stand-ins, the REAL PageManager, -Xverify:all), with a stand-in
      SkyyTrees Trees tab (its row of the contract) on the bridge:
      REG   ClassHubOpen.register() = hub:tab:character:class {"SkyyClasses", "Class", 40, "class", ClassHubOpen, HubHide, "character_class",
            "trees"} (8 elements); HubHide answers FALSE while the Trees tab is published, TRUE without it; HubBar.tabs leaves Class out
            (with Trees) / keeps it (without Trees); hostOf / hostTab / selOf; unregister() removes ours only
      OPEN  HubBar.openSub opens the Class page although its hide Function says FALSE (HubBar.open says "hidden" - the 0.1.32 kit rule)
      PAGE  the class list (no class, a Mage) and the Abilities page BUILT through the real builders: check_page, kit paths, every
            b.set / binding has its element, SUI.assert_menu_page (1600 x 980, rows 1 + 2, ONE sub row, no back / < Menu / pager text),
            row 2 (TREES selected) + the sub row (Class Primary + the 9 trees) byte-compared with the kit previews; without SkyyTrees:
            Class selected in row 2 and the sub row holds Class only
      CLICK the sub row: a tree runs /tree <tree> as the player, Class on the list = its own view (pending / result cleared), Class on
            the Abilities page = the class page; row 1: Character = self, Home runs /skymenu; the page's own pick + Confirm and the
            Abilities button still work; the bar on both pages (hub_tab_kit.clicks): the Trees tab opens the tree page through ITS Function
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
import skyyui as SUI
import re

VERSION, OLD = "0.1.34", "0.1.33"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % OLD)
PKG = "com.skyy.classes."
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "menuS1", "trees", "cls")))
LIVE = os.path.join(B.HYTALE, "UserData", "Saves", DS.WORLD, "mods", "Skyy_SkyyClasses")
FAIL_TEXT = "That tab could not open right now - try again."
ADDED = []
KIT17 = ['+<clinit>', '+f ROW_IDS', '+f ROW_TITLES', '+m bigLab', '+m bigRow', '+m bigRowFill', '+m bigTabLab', '+m bigTabsFill', '+m build2',
         '+m buildRow', '+m def4', '+m defOf', '+m defTab', '+m goHub', '+m growSize', '+m hasArt', '+m hubs', '+m iconOf', '+m okIcon', '+m okItem',
         '+m page17', '+m pickTab', '+m putIcon', '+m route', '+m rowLab', '+m rowStyle', '+m rowWidth', '+m subTab', '+m tabBStyle', '+m tabLab',
         '+m titleOf']   # install_hub_bar(row=True, page=True) over 0.1.33's (sub=True)
EXPECT = {
    "HubBar": KIT17,
    "ClassPage": ["~m build", "~m handleDataEvent"], "AbilPage": ["~m build", "~m handleDataEvent"],   # the kit 1.7 page + the sub row
    "SkyyClassesPlugin": ["~m setup"],                          # the version text
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "KitMigrate": ["~m runOnce"],          # the version text only
}
DECL_RE = re.compile(r"(?:^|[;{}\s])([A-Z][A-Za-z]*)\s+#([A-Za-z0-9]+)\s*\{")
SUB_LABELS = ["Class", "Mining", "Foraging", "Farming", "Fishing", "Alchemy", "Smithing", "Cooking", "Acrobatics", "Exploration"]


def tree_hash(root):
    o = {}
    for d, _x, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            o[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return o


def unq(d):
    if d is None:
        return ""
    d = str(d)
    try:
        v = json.loads(d)
    except Exception:
        return d
    if isinstance(v, dict) and len(v) == 1:
        v = list(v.values())[0]
    return v if isinstance(v, str) else d


def page17(K, E, P, built, what, prefix, idp, sel_tab_label, sub_labels, sub_sel, sub_acts):
    """a BUILT kit 1.7 page: markup rules, kit paths, every b.set / binding has its element, assert_menu_page, row 2 + the sub row
    byte-compared with the kit previews, the bindings of rows 1 / 2, the X and every sub-tab. Returns (apps, sets, evs)."""
    cmds, evs = built
    apps = SUI.Appends([(None if s is None else s.lstrip("#"), t) for ty, s, t, d in cmds if t is not None and ty and "Append" in ty])
    sets = [(s, unq(d)) for ty, s, t, d in cmds if ty == "Set"]
    try:
        SUI.check_page(apps, idp)
        K.check(True, "%s: check_page (markup rules, parents, no duplicate id)" % what)
    except Exception as e:
        K.check(False, "%s: check_page: %s" % (what, e))
    try:
        SUI.check_sky_paths(apps, tab_icons=True)
        allp = [m.group(0) for mk in apps.markups() for m in SUI._SKY_PATH_RE.finditer(SUI.render(mk))]
        K.check(not [p for p in allp if p.startswith('"../')], "%s: no texture path leaves Common/UI/Custom (%d)" % (what, len(allp)))
    except Exception as e:
        K.check(False, "%s: sky paths: %s" % (what, e))
    try:
        info = SUI.assert_menu_page(apps, hub="character", what=what, sets=sets)
        K.check(info["rows"] == 2 and info["subs"] == 1, "%s: assert_menu_page (1600 x 980, rows 1 + 2, ONE sub row, no back / < Menu / pager)" % what)
    except Exception as e:
        K.check(False, "%s: assert_menu_page: %s" % (what, e))
    ids = set()
    for _p, mk in apps:
        ids |= set(x.group(2) for x in DECL_RE.finditer(SUI.render(mk)))
    bs = [s for s, _t in evs]
    bad = [s for s, _d in sets if s.lstrip("#").split(".")[0] not in ids] + [s for s in bs if s.lstrip("#") not in ids]
    K.check(not bad, "%s: every b.set / binding names an element that exists (%d sets, %d bindings): %s" % (what, len(sets), len(bs), bad[:4]))
    u = P.pr.getUuid()
    tabs = [(t, str(E.bridge.get("hub:tab:character:" + t)[1])) for t in HT.hub_tabs(E, "character", u)]
    sel = [t for t, l in tabs if l == sel_tab_label]
    ents = dict((t, E.bridge.get("hub:tab:character:" + t)) for t, _l in tabs)
    icons = dict((t, str(e[6])) for t, e in ents.items() if len(e) >= 7 and e[6] is not None)   # a putSub / putIcon icon (HubBar.iconOf)
    want = SUI.hub_big_tabs_preview(prefix, "character", tabs, sel[0] if sel else None, icons=icons)
    got = [(p, mk) for p, mk in apps if p == prefix + "BigTabs" or (p or "").startswith(prefix + "BigT")]
    K.check(bool(sel) and [SUI.render(m) for _p, m in want] == [m for _p, m in got], "%s: row 2 = the kit's big tabs, %s selected (%d tabs)" % (what, sel_tab_label, len(tabs)))
    for i, (t, _l) in enumerate(tabs):
        K.check(any(("hub:" + t) in tx for s, tx in evs if s == "#%sBigT%d" % (prefix, i)), "%s: row 2 tab %d bound to hub:%s" % (what, i, t))
    subw = SUI.sub_tabs_preview(prefix, sub_labels, sub_sel)
    subg = [(p, mk) for p, mk in apps if p == prefix + "Sub"]
    K.check([SUI.render(m) for _p, m in subw] == [m for _p, m in subg], "%s: the sub row = %s, %s Primary (byte compare)" % (what, sub_labels, sub_labels[sub_sel]))
    for i, a in enumerate(sub_acts):
        K.check(any(a in tx for s, tx in evs if s == "#%sSub%d" % (prefix, i)),
                "%s: sub-tab %d (%s) bound to %s" % (what, i, sub_labels[i], a))
    K.check(any("hub:close" in t for s, t in evs if s == "#%sHubClose" % prefix), "%s: the X = hub:close" % what)
    r1 = [p for p, mk in apps if p == prefix + "BigRow"]
    K.check(bool(r1) and (any("hub:h:" in t for s, t in evs if s.startswith("#%sBigR" % prefix)) or ("#%sBigRowT " % prefix) in " ".join(m for p, m in apps if p == prefix + "BigRow")),
            "%s: row 1 drawn by bigRowFill (the hubs bound hub:h:<id>, or the hub title without hub:def)" % what)
    txt = " ".join(t for _ty, _s, t, _d in cmds if t) + " ".join(str(v) for _s, v in sets)
    K.check("< Skills" not in txt and "< Back" not in txt and "< Menu" not in txt and ("#%sHubTabs " % prefix) not in txt, "%s: no '< Skills' / '< Back' / '< Menu', no kit 1.5 strip" % what)
    return apps, sets, evs


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
    for pc in ("ClassPage", "AbilPage"):
        K.check(PKG + "HubBar.page17" in g.get(pc + ".build", set()) and PKG + "HubBar.subTab" in g.get(pc + ".build", set())
                and PKG + "HubBar.route" in g.get(pc + ".handleDataEvent", set()) and PKG + "HubBar.run" in g.get(pc + ".handleDataEvent", set()),
                "REG: %s draws the kit 1.7 page (page17 + subTab) and asks HubBar.route first; its tree sub-tabs run /tree (bytecode)" % pc)
    # ---------------------------------------------------------------- PAGE
    acts = ["clssub"] + ["clstr%d" % j for j in range(9)]
    pg = cls_page()
    built = HT.build(pg, P)
    page17(K, E, P, built, "PAGE class list (merged: Trees selected)", "SkyyClsF", "SkyyCls", "Trees", SUB_LABELS, 0, acts)
    K.check(not [t for ty, s_, t, d in built[0] if t and s_ == "#SkyyClsFBigTabs" and '"Class"' in t], "PAGE class list: no Class tab in row 2")
    trees_off()
    page17(K, E, P, HT.build(pg, P), "PAGE class list without SkyyTrees (Class a tab of its own, the sub row = Class)", "SkyyClsF", "SkyyCls", "Class",
           SUB_LABELS[:1], 0, acts[:1])
    trees_on()
    # the sub row's clicks on the class list
    pg.pending = 2
    pg.info = "x"
    pg.handleDataEvent(P.ref, P.st, '{"a":"clssub"}')
    E.pump(P)
    K.check(E.same(E.pg(P), pg) and int(pg.pending) == -1 and str(pg.info) == "", "CLICK class list: the Class sub-tab = its own view (pending / result cleared)")
    for j, w_ in ((0, "mining"), (3, "fishing"), (8, "exploration")):
        E.CM.lines.clear()
        pg.handleDataEvent(P.ref, P.st, '{"a":"clstr%d"}' % j)
        E.pump(P)
        K.check([str(x) for x in E.CM.lines] == ["tree " + w_], "CLICK class list: the %s sub-tab runs /tree %s as the player (%s)" % (SUB_LABELS[j + 1], w_, list(E.CM.lines)))
    E.CM.lines.clear()
    pg = cls_page()
    pg.pending = 2
    pg.info = "x"
    pg.handleDataEvent(P.ref, P.st, '{"a":"hub:h:character"}')
    E.pump(P)
    K.check(int(pg.pending) == -1 and str(pg.info) == "", "CLICK class list: row 1 Character (this hub) = self")
    E.bridge.put("config:def:SkyyMenu", "stand-in")
    pg.handleDataEvent(P.ref, P.st, '{"a":"hub:h:home"}')
    E.pump(P)
    K.check([str(x) for x in E.CM.lines] == ["skymenu"], "CLICK class list: row 1 Home runs /skymenu (%s)" % list(E.CM.lines))
    E.bridge.remove("config:def:SkyyMenu")
    E.CM.lines.clear()
    pg = cls_page()
    mage = [str(x) for x in Defs.NAMES].index("Mage")
    pg.handleDataEvent(P.ref, P.st, '{"a":"clspick%d"}' % mage)
    E.pump(P)
    pg.handleDataEvent(P.ref, P.st, '{"a":"clsyes"}')
    E.pump(P)
    K.check(int(Store.classIndex(u)) == mage, "PAGE the page's own pick + Confirm still work: a Mage (%s)" % pg.info)
    page17(K, E, P, HT.build(pg, P), "PAGE class list (a Mage: the Abilities button)", "SkyyClsF", "SkyyCls", "Trees", SUB_LABELS, 0, acts)
    pg.handleDataEvent(P.ref, P.st, '{"a":"clsabil"}')
    E.pump(P)
    ab = E.pg(P)
    K.check(ab is not None and str(ab.getClass().getName()) == PKG + "AbilPage", "PAGE the Abilities button opens the Abilities page")
    if ab is not None:
        page17(K, E, P, HT.build(ab, P), "PAGE abilities (merged: Trees selected)", "SkyyAbF", "SkyyAb", "Trees", SUB_LABELS, 0,
               ["absub"] + acts[1:])
        E.CM.lines.clear()
        ab.handleDataEvent(P.ref, P.st, '{"a":"clstr1"}')
        E.pump(P)
        K.check([str(x) for x in E.CM.lines] == ["tree foraging"], "CLICK abilities: the Foraging sub-tab runs /tree foraging (%s)" % list(E.CM.lines))
        E.CM.lines.clear()
        ab.handleDataEvent(P.ref, P.st, '{"a":"absub"}')
        E.pump(P)
        cur = E.pg(P)
        K.check(cur is not None and str(cur.getClass().getName()) == PKG + "ClassPage", "CLICK abilities: the Class sub-tab opens the class page")
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
