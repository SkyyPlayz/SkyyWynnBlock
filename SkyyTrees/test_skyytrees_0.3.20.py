"""SkyyTrees 0.3.20 - harness for MENU PATTERN sweep S1 (the tree page on the kit 1.7 hub_page, ONE sub-tab row M6, no back buttons;
tools/trees_0_3_20_patch.py). Build first:
    python tools/trees_0_3_20_patch.py && python SkyyTrees/build_skyytrees_0.3.20.py
    python SkyyTrees/test_skyytrees_0.3.20.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Every JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch (tools/harness_kit.py).
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.19 -> 0.3.20: HubBar + the kit 1.7 members (row 1, row 2, sub row, route); TreePage.build / buildClass / handleDataEvent;
                the version texts; non-class entries: manifest.json only
  CT   EXECUTED (tools/hub_tab_kit.py engine stand-ins, the REAL PageManager, -Xverify:all), with a stand-in of SkyyClasses' Class tab:
       PAGES   every view BUILT through the real builder - the class tree (Class tab mode and /tree class), Mining, Fishing, Exploration,
               Respec armed: check_page, the kit paths (tab art allowed), every b.set / binding has its element, SUI.assert_menu_page
               (1600 x 980, row 1 + row 2, one sub row, no back / < Menu / pager text); row 2 + the sub row BYTE-compared with the kit
               previews (hub_big_tabs_preview: TREES selected; sub_tabs_preview: Class + the 9 trees in the Skills order, the open one
               Primary); no '< Skills' / SkyyTrBack / old tab row anywhere; the class tree's focus button is "All abilities" (class file)
       CLICKS  the sub row switches trees in place (trtab<n>: Fishing, Exploration, the class tree again - Trees selected on all);
               Respec: the first click arms ("Click again to respec Mining" in the footer), the selected Trees tab disarms it; row 1:
               Character = self, Home runs /skymenu, a hub that is not there says so; row 2 / X / the old events as the contract
               (hub_tab_kit.clicks); OLD (SkyyClasses 0.1.33-: Class a tab of its own) still Class selected + the 0.3.16 rule
  ST1/ST2 start twice on a scratch COPY of the live Skyy_SkyyTrees folder (TreeCfg.load + the tab / classPage registration): nothing written
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, hashlib, zipfile

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

VERSION = "0.3.20"
PKG = "com.skyy.trees."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyTrees-0.3.19.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "menuS1", "trees", "tr")))
LIVE = os.path.join(B.HYTALE, "UserData", "Saves", DS.WORLD, "mods", "Skyy_SkyyTrees")
ADDED = []
KIT17 = ['+<clinit>', '+f ROW_IDS', '+f ROW_TITLES', '+m bigLab', '+m bigRow', '+m bigRowFill', '+m bigTabLab', '+m bigTabsFill', '+m build2',
         '+m buildRow', '+m def4', '+m defOf', '+m defTab', '+m goHub', '+m growSize', '+m hasArt', '+m hubs', '+m iconOf', '+m okIcon', '+m okItem',
         '+m page17', '+m pickTab', '+m putIcon', '+m route', '+m rowLab', '+m rowStyle', '+m rowWidth', '+m subTab', '+m tabBStyle', '+m tabLab',
         '+m titleOf']   # install_hub_bar(row=True, page=True) over 0.3.19's (sub=True): the kit 1.6 row + big row + kit 1.7 members
EXPECT = {"HubBar": KIT17, "TreePage": ["~m build", "~m buildClass", "~m handleDataEvent"], "SkyyTreesPlugin": ["~m setup"],
          "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "TreeCfg": ["~m load"]}       # + the version texts
FAIL_TEXT = "That tab could not open right now - try again."
TREES = ["Mining", "Foraging", "Farming", "Cooking", "Acrobatics", "Exploration", "Alchemy", "Smithing", "Fishing"]
SUB_ORDER = [TREES.index(n) for n in ("Mining", "Foraging", "Farming", "Fishing", "Alchemy", "Smithing", "Cooking", "Acrobatics", "Exploration")]
SUB_LABELS = ["Class"] + [TREES[n] for n in SUB_ORDER]
DECL_RE = re.compile(r"(?:^|[;{}\s])([A-Z][A-Za-z]*)\s+#([A-Za-z0-9]+)\s*\{")


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
    K.check("< Skills" not in txt and "< Back" not in txt and "< Menu" not in txt and "SkyyTrBack" not in txt and "SkyyTrHead" not in txt
            and ("#%sHubTabs " % prefix) not in txt, "%s: no '< Skills' / '< Back' / '< Menu', no old tab row / kit 1.5 strip" % what)
    return apps, sets, evs


def run_ct(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JArray, JObject
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    J = lambda n: JClass(PKG + n)
    Sto, Cfg, Defs, HO, CH, Page, HB = J("TreeStore"), J("TreeCfg"), J("TreeDefs"), J("TreesHubOpen"), J("TreeClassHub"), J("TreePage"), J("HubBar")
    Sto.DIR = E.Paths.get(scratch, "ct-mods", "Skyy_SkyyTrees", "players")
    os.makedirs(os.path.join(scratch, "ct-mods", "Skyy_SkyyTrees", "players"), exist_ok=True)
    P = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-0000000001ba"), "TreeSweep")
    u = P.pr.getUuid()
    us = str(u)
    Int = JClass("java.lang.Integer")
    S = JClass("java.lang.String")
    NT = int(Defs.NT)
    K.eq([str(x) for x in Defs.TREES], TREES, "the 9 trees (TreeDefs.TREES)")
    CH.register()
    HO.register()
    acts = ["trtab%d" % NT] + ["trtab%d" % n for n in SUB_ORDER]

    @JImplements("java.util.function.Function")
    class Stub:
        def __init__(self, ans):
            self.calls, self.ans = [], ans

        @JOverride
        def apply(self, o):
            self.calls.append(str(o))
            return self.ans
    copen, hide = Stub(E.TRUE), Stub(E.FALSE)
    merged = JArray(JObject)([S("SkyyClasses"), S("Class"), Int.valueOf(40), S("class"), copen, hide, S("character_class"), S("trees")])
    old = JArray(JObject)([S("SkyyClasses"), S("Class"), Int.valueOf(40), S("class"), copen, None])
    E.bridge.put("class:" + us, "Mage")
    Cfg.CLASS_ON = True
    fn = CH()

    def open_chub():
        r = fn.apply(u)
        E.pump(P)
        pg = E.pg(P)
        return pg if (r == E.TRUE and pg is not None and str(pg.getClass().getName()) == PKG + "TreePage") else None

    def click(p_, a):
        p_.handleDataEvent(P.ref, P.st, '{"a":"%s"}' % a)
        E.pump(P)
        return E.pg(P)
    g = PW.calls(jar)
    K.check(PKG + "HubBar.page17" in g.get("TreePage.build", set()) and PKG + "HubBar.page17" in g.get("TreePage.buildClass", set())
            and PKG + "HubBar.subTab" in g.get("TreePage.build", set()) and PKG + "HubBar.subTab" in g.get("TreePage.buildClass", set()),
            "REG: both views draw the kit 1.7 page (HubBar.page17 + HubBar.subTab, bytecode)")
    K.check(PKG + "HubBar.route" in g.get("TreePage.handleDataEvent", set()) and PKG + "HubBar.selOf" in g.get("TreePage.hubSel", set()),
            "REG: handleDataEvent asks HubBar.route first; hubSel() asks HubBar.selOf (bytecode)")
    zf = zipfile.ZipFile(jar)
    tp = zf.read("com/skyy/trees/TreePage.class")
    K.check(b"All abilities" in tp and b"< Back" not in tp and b"< Skills" not in tp and b"SkyyTrBack" not in tp,
            "PAGES class tree: the focus view's button is 'All abilities' - no '< Back' / '< Skills' in TreePage (class file)")
    # ---------------------------------------------------------------- MERGED (SkyyClasses 0.1.33+)
    E.bridge.put("hub:tab:character:class", merged)
    K.check([str(x) for x in HT.hub_tabs(E, "character", u)] == ["trees"], "MERGED: the Character strip has no Class tab (%s)" % HT.hub_tabs(E, "character", u))
    Page.LASTTREE.put(u, Int.valueOf(2))
    pg = open_chub()
    K.check(pg is not None and int(pg.tree) == NT and bool(pg.chub), "MERGED: /class (tree:fn:classPage) = the class tree in Class tab mode")
    K.eq(str(pg.hubSel()), "trees", "MERGED: hubSel() = trees (Class is part of the Trees tab)")
    page17(K, E, P, HT.build(pg, P), "PAGES class tree (Class tab mode)", "SkyyTrF", "SkyyTr", "Trees", SUB_LABELS, 0, acts)
    pg.msg = "x"
    pg.armT = 2
    cur = click(pg, "hub:trees")
    K.check(E.same(cur, pg) and int(pg.tree) == NT and str(pg.msg) == "" and int(pg.armT) == -1 and int(Page.LASTTREE.get(u)) == 2,
            "CLICKS merged: the selected Trees tab = self (the class tree stays, result line cleared, Respec disarmed)")
    for a, n_, lab in (("trtab0", 0, "Mining"), ("trtab8", 8, "Fishing"), ("trtab5", 5, "Exploration")):
        cur = click(pg, a)
        K.check(E.same(cur, pg) and int(pg.tree) == n_ and str(pg.hubSel()) == "trees" and int(Page.LASTTREE.get(u)) == n_,
                "CLICKS the sub row's %s switches in place (%s), Trees selected" % (lab, a))
        page17(K, E, P, HT.build(pg, P), "PAGES %s" % lab, "SkyyTrF", "SkyyTr", "Trees", SUB_LABELS, SUB_LABELS.index(lab), acts)
    cur = click(pg, "trtab0")
    cur = click(pg, "trrespec")
    K.check(E.same(cur, pg) and int(pg.armT) == 0, "CLICKS Respec on Mining: the first click arms it (%s)" % pg.msg)
    _a, sets, _e = page17(K, E, P, HT.build(pg, P), "PAGES Mining (Respec armed)", "SkyyTrF", "SkyyTr", "Trees", SUB_LABELS, 1, acts)
    cmds, _ev = HT.build(pg, P)
    foot = [t for ty, s, t, d in cmds if s == "#SkyyTrFFoot" and t]
    K.check(any('Text: "Click again to respec Mining"' in t for t in foot) and any("#SkyyTrMsg " in t for t in foot),
            "PAGES Mining armed: the footer holds the result line + 'Click again to respec Mining' (the click-again pattern)")
    cur = click(pg, "hub:trees")
    K.check(E.same(cur, pg) and int(pg.armT) == -1 and str(pg.msg) == "", "CLICKS the selected Trees tab disarms Respec + clears the result line")
    cur = click(pg, "trtab%d" % NT)
    K.check(E.same(cur, pg) and int(pg.tree) == NT and str(pg.hubSel()) == "trees", "CLICKS the Class sub-tab: the class tree again, Trees selected")
    # row 1 (kit 1.7: hub:h:<id> through HubBar.route)
    pg.msg = "x"
    pg.armT = 2
    cur = click(pg, "hub:h:character")
    K.check(E.same(cur, pg) and str(pg.msg) == "" and int(pg.armT) == -1, "CLICKS row 1 Character (this hub) = self")
    n0 = len(E.sent(P))
    cur = click(pg, "hub:h:storage")
    K.check(E.same(cur, pg) and FAIL_TEXT in E.strs_of(P, n0), "CLICKS row 1 a hub with nothing in it: the page stays and says it could not open")
    E.bridge.put("config:def:SkyyMenu", "stand-in")
    E.CM.lines.clear()
    cur = click(pg, "hub:h:home")
    K.check([str(x) for x in E.CM.lines] == ["skymenu"], "CLICKS row 1 Home runs /skymenu as the player (%s)" % list(E.CM.lines))
    E.bridge.remove("config:def:SkyyMenu")
    E.CM.lines.clear()
    fakes = HT.Fakes(E, "character")

    def open_armed():
        p_ = open_chub()
        p_.msg = "x"
        p_.armT = 2
        return p_
    HT.clicks(K, E, P, open_armed, "character", "trees", "CLICK merged class mode", fakes,
              self_check=lambda p_: str(p_.msg) == "" and int(p_.armT) == -1 and int(p_.tree) == NT, fail_text=FAIL_TEXT)
    fakes.remove()
    # /tree mining (the command's own page) = the same page
    pm = Page(P.pr, 0)
    P.pm.openCustomPage(P.ref, P.st, pm)
    E.pump(P)
    page17(K, E, P, HT.build(pm, P), "PAGES /tree mining", "SkyyTrF", "SkyyTr", "Trees", SUB_LABELS, 1, acts)
    Cfg.CLASS_ON = False
    page17(K, E, P, HT.build(pm, P), "PAGES Mining with class trees off (no Class sub-tab)", "SkyyTrF", "SkyyTr", "Trees", SUB_LABELS[1:], 0,
           ["trtab%d" % n for n in SUB_ORDER])
    Cfg.CLASS_ON = True
    # ---------------------------------------------------------------- OLD (SkyyClasses 0.1.32: a Class tab of its own)
    E.bridge.put("hub:tab:character:class", old)
    K.check([str(x) for x in HT.hub_tabs(E, "character", u)] == ["trees", "class"], "OLD: Trees + Class tabs (0.1.32)")
    pg = open_chub()
    K.eq(str(pg.hubSel()), "class", "OLD: hubSel() = class in Class tab mode (as 0.3.19)")
    page17(K, E, P, HT.build(pg, P), "PAGES OLD class tree (Class selected)", "SkyyTrF", "SkyyTr", "Class", SUB_LABELS, 0, acts)
    Page.LASTTREE.put(u, Int.valueOf(2))
    cur = click(pg, "hub:trees")
    K.check(E.same(cur, pg) and int(pg.tree) == 2 and not bool(pg.chub) and str(pg.hubSel()) == "trees", "OLD: the Trees tab switches to the last skill tree (the 0.3.16 rule)")
    E.bridge.remove("hub:tab:character:class")
    E.bridge.remove("class:" + us)
    K.save()


def run_st(out, jar, scratch, step):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Cfg, HO, CH = JClass(PKG + "TreeCfg"), JClass(PKG + "TreesHubOpen"), JClass(PKG + "TreeClassHub")
    Paths = JClass("java.nio.file.Paths")
    base = os.path.join(scratch, "st", "mods", "Skyy_SkyyTrees")
    if step == "1":
        shutil.rmtree(os.path.join(scratch, "st"), ignore_errors=True)
        shutil.copytree(LIVE, base)
        json.dump(tree_hash(LIVE), open(os.path.join(scratch, "st-live.json"), "w"))
    before = tree_hash(base)
    f = [x for x in Cfg.class_.getDeclaredFields() if str(x.getName()) == "FILE"]
    if f:
        Cfg.FILE = Paths.get(os.path.join(base, "trees.properties"))
    lo = None
    try:
        lo = str(Cfg.load())
    except Exception as e:
        lo = "load: %s" % e
    r1, r2 = str(HO.register()), str(CH.register())
    HO.unregister()
    CH.unregister()
    after = tree_hash(base)
    ch = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    K.check(bool(f) and not ch, "ST start %s on a scratch COPY of the live data (%d files): nothing written %s (load %s; tab %s, classPage %s)"
            % (step, len(before), ch, (lo or "")[:60], r1, r2))
    if step == "2":
        K.check(tree_hash(LIVE) == json.load(open(os.path.join(scratch, "st-live.json"))), "ST: the live Skyy_SkyyTrees folder was only read")
    K.save()
    sys.stdout.flush()
    os._exit(0)


def run_st1(out, jar, scratch, _home):
    run_st(out, jar, scratch, "1")


def run_st2(out, jar, scratch, _home):
    run_st(out, jar, scratch, "2")


if __name__ == "__main__":
    HK.run(name="SkyyTrees", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("ct", run_ct), ("st1", run_st1), ("st2", run_st2)], script=__file__)
