"""SkyyTrees 0.3.21 - harness for round trees21 (tools/trees_0_3_21_patch.py: the 8-number Tree Feller table + its one-time update, Sap
Tapper sap in Collections, the Breaking Speed readers (SkyyGear gear:swing + SkyyAccessories swing.<skill>), LLCAP 10, the Siphon Health
part + the Elemental Bubble line; the kit 1.7 page of 0.3.20 kept). Build first:
    python tools/trees_0_3_21_patch.py && python SkyyTrees/build_skyytrees_0.3.21.py
    python SkyyTrees/test_skyytrees_0.3.21.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Every JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch (tools/harness_kit.py).
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.20 -> 0.3.21: exactly the planned members (EXPECT) + TreeMig321
  T21  EXECUTED the round's rules: the Feller table (levels 1-10), LLCAP 10 (llTotal), gear:perk:readers + skill:bonus:reads:swing (present,
       absent, another mod's words kept), TreeSwing parts (tool / accessories present + absent + junk, the +40 % cap, mining vs foraging),
       Sap Tapper (sapNatural + the Collections credit, placed / unknown / no SkyySkills), TreeMig321's text step (old default, spaced,
       CRLF, edited, doubled, missing, new value, marker = runs once), Siphon's Health percent (CHP, pctHp), the bytecode wiring
  CT   (0.3.20's page checks, unchanged) EXECUTED (tools/hub_tab_kit.py engine stand-ins, the REAL PageManager, -Xverify:all), with a stand-in of SkyyClasses' Class tab:
       PAGES   every view BUILT through the real builder - the class tree (Class tab mode and /tree class), Mining, Fishing, Exploration,
               Respec armed: check_page, the kit paths (tab art allowed), every b.set / binding has its element, SUI.assert_menu_page
               (1600 x 980, row 1 + row 2, one sub row, no back / < Menu / pager text); row 2 + the sub row BYTE-compared with the kit
               previews (hub_big_tabs_preview: TREES selected; sub_tabs_preview: Class + the 9 trees in the Skills order, the open one
               Primary); no '< Skills' / SkyyTrBack / old tab row anywhere; the class tree's focus button is "All abilities" (class file)
       CLICKS  the sub row switches trees in place (trtab<n>: Fishing, Exploration, the class tree again - Trees selected on all);
               Respec: the first click arms ("Click again to respec Mining" in the footer), the selected Trees tab disarms it; row 1:
               Character = self, Home runs /skymenu, a hub that is not there says so; row 2 / X / the old events as the contract
               (hub_tab_kit.clicks); OLD (SkyyClasses 0.1.33-: Class a tab of its own) still Class selected + the 0.3.16 rule
  ST1/ST2 start twice on a scratch COPY of the live Skyy_SkyyTrees folder (setup's order: TreeCfg.load, the one-time updates, the tab /
       classPage registration): start 1 writes ONLY the 0.3.21 Feller update (trees.properties value + marker, its History version, one
       Undo line) when the live line holds the old default; start 2 writes nothing; the live folder is only read
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

VERSION = "0.3.21"
PKG = "com.skyy.trees."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyTrees-0.3.20.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "trees21", "tr")))
LIVE = os.path.join(B.HYTALE, "UserData", "Saves", DS.WORLD, "mods", "Skyy_SkyyTrees")
ADDED = ["TreeMig321"]
EXPECT21 = {"CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],            # the version texts
            "SkyyTreesPlugin": ["~m setup"],                                           # TreeMig321.run + the version text
            "TreeAbil": ["~m llEntry", "~m llTotal", "~m readers", "~m readersWith"],  # LLCAP 10 (inlined), + swing, skill:bonus:reads:swing
            "TreeCfg": ["~<clinit>", "~m apply", "~m load", "~m logs", "~m upgrade"],  # the 8-number default (inlined) + DEFAULTS
            "TreeClass": ["+f CHP", "+m hpPct", "~<clinit>"],                          # Siphon's -5 % max Health
            "TreeDefs": ["~<clinit>"],                                                 # the Sap Tapper how text
            "TreeFx": ["+m pctHp", "~m stats"],
            "TreeGather": ["+m sapNatural", "+m sapTap", "~m felled", "~m run"],
            "TreeKit": ["~m checkFellerLogs"],                                         # the default CSV in its texts
            "TreePage": ["~m buildClass"],                                             # the Elemental Bubble line (panel o[129])
            "TreeSwing": ["+m accSwing", "+m apply", "+m gearSwing", "+m total", "-m apply", "~m report"],   # apply(cb, ref, v, u)
            "TreeTick": ["~m tick"]}
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


OLD_FELLER, NEW_FELLER = "1,2,4,5,6,10", "1,2,4,5,6,10,12,14"
MK321 = "skyytrees-0.3.21-feller"


def live_feller():
    f = os.path.join(LIVE, "trees.properties")
    if not os.path.isfile(f):
        return None
    t = open(f, "rb").read().decode("latin-1")
    if MK321 in t:
        return "marked"
    v = [l.split("=", 1)[1].strip() for l in t.replace("\r\n", "\n").split("\n") if l.startswith("feller.logs=")]
    return v[0].replace(" ", "") if len(v) == 1 else "?"


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
    JClass(PKG + "TreeStore").DIR = Paths.get(os.path.join(base, "players"))
    lo, mg = None, {}
    try:
        lo = str(Cfg.load())
        bp = Paths.get(base)
        for m_ in ("TreeMig", "TreeMig32", "TreeMig33", "TreeMig317", "TreeMig321"):   # setup()'s order
            mg[m_] = str(JClass(PKG + m_).run(bp))
    except Exception as e:
        lo = "load: %s" % e
    r1, r2 = str(HO.register()), str(CH.register())
    HO.unregister()
    CH.unregister()
    after = tree_hash(base)
    ch = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    lf = live_feller()
    if step == "1":
        okset = all(k in ("trees.properties", "config-changes.log") or k.startswith("config-history/") for k in ch)
        others = dict((k, v) for k, v in mg.items() if k != "TreeMig321" and v)
        if lf == OLD_FELLER:
            t = open(os.path.join(base, "trees.properties"), "rb").read().decode("latin-1")
            log = open(os.path.join(base, "config-changes.log"), encoding="utf8").read().split("\n")
            rows = [l.split("\t") for l in log if "\tSkyyTrees 0.3.21\t" in l]
            K.check(okset and "trees.properties" in ch and any(k.startswith("config-history/") for k in ch) and not others,
                    "ST start 1 on a scratch COPY of the live data: only the 0.3.21 Feller update is written %s (others %s)" % (ch, others))
            K.check(("\nfeller.logs=" + NEW_FELLER) in t.replace("\r\n", "\n") and t.count(MK321) == 1 and float(Cfg.fellerLogs(8)) == 14.0,
                    "ST start 1: feller.logs = %s + the marker; load() reads level 8 = 14" % NEW_FELLER)
            K.check(len(rows) == 1 and rows[0][2:8] == ["-", "update", "feller.logs", OLD_FELLER, NEW_FELLER, "ok"], "ST start 1: one Undo line: %s" % rows)
            K.check("feller.logs " + OLD_FELLER + " -> " + NEW_FELLER in mg["TreeMig321"], "ST start 1: the INFO line (%s)" % mg["TreeMig321"][:160])
        else:
            K.check(okset and not others, "ST start 1: the live feller.logs is %s (not the old default) - only the marker may be written %s" % (lf, ch))
    else:
        K.check(bool(f) and not ch and mg.get("TreeMig321") == "", "ST start 2: nothing written %s (load %s; tab %s, classPage %s)" % (ch, (lo or "")[:60], r1, r2))
        K.check(tree_hash(LIVE) == json.load(open(os.path.join(scratch, "st-live.json"))), "ST: the live Skyy_SkyyTrees folder was only read")
    K.save()
    sys.stdout.flush()
    os._exit(0)


def run_t21(out, jar, scratch, _home):
    from jpype import JClass, JArray, JDouble, JObject, JString, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    Cfg, Abil, Swg, Gat, Mig, Defs, Cls, Fx, Sto = (J("TreeCfg"), J("TreeAbil"), J("TreeSwing"), J("TreeGather"), J("TreeMig321"), J("TreeDefs"),
                                                    J("TreeClass"), J("TreeFx"), J("TreeStore"))
    UUID, CHM, HashMap = JClass("java.util.UUID"), JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.util.HashMap")
    Bool, Dbl = JClass("java.lang.Boolean"), JClass("java.lang.Double")
    br = Sto.bridge()
    # ---- 1. the Feller table (the built-in default; the loader rule: a level above the list = its last number)
    K.eq([int(x) for x in Cfg.FELLER_LOGS], [1, 2, 4, 5, 6, 10, 12, 14], "T21 Feller: the built-in table has 8 numbers")
    K.eq([int(Cfg.fellerLogs(lv)) for lv in range(0, 11)], [0, 1, 2, 4, 5, 6, 10, 12, 14, 14, 14], "T21 Feller: levels 0-10 (9-10 repeat 14)")
    K.eq([int(x) for x in Cfg.logs("")], [1, 2, 4, 5, 6, 10, 12, 14], "T21 Feller: an empty / bad feller.logs falls back to the 8 numbers")
    K.eq([int(x) for x in Cfg.logs(OLD_FELLER)], [1, 2, 4, 5, 6, 10], "T21 Feller: a hand-kept 6-number table is read as it is")
    K.check(NEW_FELLER in str(Cfg.DEFAULTS) and ("feller.logs=" + NEW_FELLER + "\n") in str(Cfg.DEFAULTS) and str(Cfg.DEFAULTS).count(MK321) == 1,
            "T21 Feller: the default file writes the new table + the run-once marker")
    # ---- 2. LLCAP 10
    K.eq(int(Abil.LLCAP), 10, "T21 LLCAP: tree + tool levels stack to 10 (was 8)")
    K.eq([int(Abil.llTotal(e, p)) for e, p in ((6, 6), (4, 6), (6, 3), (2, 3), (0, 6), (12, 3), (5, 0))], [10, 10, 9, 5, 6, 12, 5],
         "T21 LLCAP: llTotal (6+6=10, 4+6=10, 6+3=9, 2+3=5, 0+6=6, an admin tree level 12 kept, no tool = the tree)")
    # ---- 3. the readers
    rw = lambda cur, add: str(Abil.readersWith(None if cur is None else JString(cur), add))
    K.eq([rw(None, True), rw("", True), rw("fort,vein,fell", True), rw("swing,x", True), rw("vein,fell,swing,fort", False), rw(None, False)],
         ["vein,fell,swing", "vein,fell,swing", "fort,vein,fell,swing", "x,vein,fell,swing", "fort", ""],
         "T21 readers: readersWith adds vein,fell,swing once and takes back only ours")
    br.remove("gear:perk:readers")
    br.remove("skill:bonus:reads:swing")
    br.put("gear:perk:readers", "fort")
    Abil.readers(True)
    K.check(str(br.get("gear:perk:readers")) == "fort,vein,fell,swing" and Bool.TRUE.equals(br.get("skill:bonus:reads:swing")),
            "T21 readers PRESENT: gear:perk:readers = %s, skill:bonus:reads:swing = TRUE" % br.get("gear:perk:readers"))
    Abil.readers(False)
    K.check(str(br.get("gear:perk:readers")) == "fort" and br.get("skill:bonus:reads:swing") is None, "T21 readers ABSENT (shutdown): both taken back, another mod's word kept")
    br.put("skill:bonus:reads:swing", "someone-else")
    Abil.readers(False)
    K.check(str(br.get("skill:bonus:reads:swing")) == "someone-else", "T21 readers: shutdown never removes another value of skill:bonus:reads:swing")
    br.remove("skill:bonus:reads:swing")
    br.put("gear:perk:readers", JClass("java.lang.Integer").valueOf(3))
    Abil.readers(True)
    K.check(str(br.get("gear:perk:readers")) == "3" and br.get("skill:bonus:reads:swing") is None, "T21 readers: a non-text gear:perk:readers is left alone (warned)")
    br.remove("gear:perk:readers")
    # ---- 4. the swing parts
    u = UUID.fromString("00000000-0000-0000-0000-0000000021aa")
    N = int(Defs.N)
    ids = [str(x) for x in Defs.ID]
    v = JArray(JDouble)([0.0] * N)
    K.check(float(Swg.gearSwing(u)) == 0.0 and float(Swg.accSwing(u, "mining")) == 0.0 and float(Swg.total(u, v, 0)) == 0.0,
            "T21 swing ABSENT: no gear:swing / no accessories source = 0")
    br.put("gear:swing:" + str(u), Dbl.valueOf(9.0))
    K.check(abs(float(Swg.gearSwing(u)) - 0.09) < 1e-12, "T21 swing: gear:swing 9.0 (percent) = 0.09")
    for junk in (JString("12"), Dbl.valueOf(-5.0), Dbl.valueOf(float("nan"))):
        br.put("gear:swing:" + str(u), junk)
        K.check(float(Swg.gearSwing(u)) == 0.0, "T21 swing: junk gear:swing %s = 0" % junk)
    br.put("gear:swing:" + str(u), Dbl.valueOf(9.0))
    src = CHM()
    acc = HashMap()
    acc.put("swing.mining", Dbl.valueOf(0.14))
    acc.put("swing.foraging", Dbl.valueOf(0.05))
    src.put("accessories", acc)
    src.put("trees", HashMap())
    br.put("skill:bonus:" + str(u), src)
    K.check(abs(float(Swg.accSwing(u, "mining")) - 0.14) < 1e-12 and abs(float(Swg.accSwing(u, "foraging")) - 0.05) < 1e-12 and float(Swg.accSwing(u, "farming")) == 0.0,
            "T21 swing PRESENT: swing.mining 0.14 / swing.foraging 0.05 from the accessories source")
    vv = [0.0] * N
    vv[ids.index("MSpeed")] = 0.10
    vv[ids.index("FSpeed")] = 0.20
    v2 = JArray(JDouble)(vv)
    K.eq([int(Swg.tier(Swg.total(u, v2, 0))), int(Swg.tier(Swg.total(u, v2, 1)))], [33, 34],
         "T21 swing: pickaxe = tree 10 + tool 9 + acc 14 = 33 %, hatchet = tree 20 + tool 9 + acc 5 = 34 %")
    br.put("gear:swing:" + str(u), Dbl.valueOf(30.0))
    K.eq([int(Swg.tier(Swg.total(u, v2, 0))), int(Swg.tier(Swg.total(u, v2, 1)))], [40, 40], "T21 swing: the total is capped at +40 % (the engine ceiling)")
    acc.put("swing.mining", Dbl.valueOf(-0.5))
    br.remove("gear:swing:" + str(u))
    K.eq(int(Swg.tier(Swg.total(u, v2, 0))), 0, "T21 swing: a debuff can lower it, never below vanilla (tier 0)")
    br.remove("skill:bonus:" + str(u))
    # ---- 5. Sap Tapper: natural logs count
    calls = []

    @JImplements("java.util.function.Function")
    class Fn:
        def __init__(self, f): self.f = f

        @JOverride
        def apply(self, o): return self.f(o)
    placed = {"v": Bool.FALSE}
    br.put("skill:fn:placed", Fn(lambda o: placed["v"]))
    br.put("coll:fn:add", Fn(lambda o: (calls.append([str(x) for x in o]), Bool.TRUE)[1]))
    K.check(bool(Gat.sapNatural("w", 1, 64, 1, "Wood_Oak_Trunk")) and not bool(Gat.sapNatural("w", 1, 64, 1, "Wood_Oak_Planks"))
            and not bool(Gat.sapNatural(None, 1, 64, 1, "Wood_Oak_Trunk")), "T21 Sap Tapper: a natural trunk counts; a non-trunk / no world never")
    placed["v"] = Bool.TRUE
    K.check(not bool(Gat.sapNatural("w", 1, 64, 1, "Wood_Oak_Trunk")), "T21 Sap Tapper: a PLACED trunk never counts")
    placed["v"] = None
    K.check(not bool(Gat.sapNatural("w", 1, 64, 1, "Wood_Oak_Trunk")), "T21 Sap Tapper: unknown (no answer) = not natural")
    br.remove("skill:fn:placed")
    K.check(not bool(Gat.sapNatural("w", 1, 64, 1, "Wood_Oak_Trunk")), "T21 Sap Tapper: no SkyySkills placed tracker = not natural")
    K.check(bool(Gat.sapCredit(u)) and len(calls) == 1 and calls[0][1:4] == ["Ingredient_Tree_Sap", "1", "skills:felled"],
            "T21 Sap Tapper: the credit = coll:fn:add {UUID, Ingredient_Tree_Sap, 1, skills:felled, profile key}: %s" % calls)
    K.check(not bool(Gat.sapTap(None, "w", 1, 64, 1, "Wood_Oak_Trunk", "Ingredient_Tree_Sap")) and len(calls) == 1,
            "T21 Sap Tapper: no player = nothing given, nothing credited")
    br.remove("coll:fn:add")
    g = PW.calls(jar)
    K.check(PKG + "TreeGather.sapTap" in g.get("TreeGather.run", set()) and PKG + "TreeGather.sapTap" in g.get("TreeGather.felled", set()),
            "T21 Sap Tapper: hand-chopped (run) and felled logs roll through sapTap (bytecode)")
    K.check({PKG + "TreeGather.giveItem", PKG + "TreeGather.sapNatural", PKG + "TreeGather.sapCredit"} <= g.get("TreeGather.sapTap", set()),
            "T21 Sap Tapper: sapTap gives the item, checks natural, credits Collections (bytecode)")
    # ---- 6. TreeMig321's text step
    mk = str(Mig.MARK_LINE)

    def upd(t):
        r = Mig.m321Update(t)
        return None if r is None else [str(r[0]), [str(x) for x in r[1]], [str(x) for x in r[2]], [str(x) for x in r[3]]]
    base_t = "# SkyyTrees\nvein.cooldownSec=40\nfeller.logs=%s\nfeller.cooldownSec=3\n" % OLD_FELLER
    r = upd(base_t)
    K.check(r is not None and r[0] == base_t.replace("feller.logs=" + OLD_FELLER, "feller.logs=" + NEW_FELLER) + mk + "\n" and r[1] == ["feller.logs", OLD_FELLER, NEW_FELLER]
            and r[3] == ["feller.logs"] and r[2] == [], "MG321 LF: the old default -> the 8 numbers, the marker appended, every other byte kept")
    crlf = base_t.replace("\n", "\r\n")
    r = upd(crlf)
    K.check(r is not None and r[0] == crlf.replace(OLD_FELLER + "\r\n", NEW_FELLER + "\r\n") + mk + "\r\n", "MG321 CRLF: line endings kept")
    sp = base_t.replace(OLD_FELLER, "1, 2, 4, 5, 6, 10")
    r = upd(sp)
    K.check(r is not None and "feller.logs=" + NEW_FELLER + "\n" in r[0] and r[1][1] == "1, 2, 4, 5, 6, 10", "MG321: the default written with spaces counts as untouched")
    nofl = base_t.rstrip("\n")
    r = upd(nofl)
    K.check(r is not None and r[0] == nofl.replace(OLD_FELLER, NEW_FELLER) + "\n" + mk + "\n", "MG321: a missing final newline is added first")
    ed = base_t.replace(OLD_FELLER, "1,3,5")
    r = upd(ed)
    K.check(r is not None and r[0] == ed + mk + "\n" and r[1] == [] and len(r[2]) == 1 and "an admin changed it" in r[2][0], "MG321: a hand-edited table is kept (marker only) and noted")
    db = base_t + "feller.logs=%s\n" % OLD_FELLER
    r = upd(db)
    K.check(r is not None and r[1] == [] and "doubled" in r[2][0], "MG321: a doubled line is kept and noted")
    cont = base_t.replace("feller.logs=" + OLD_FELLER, "feller.logs=1,2,4,\\\n  5,6,10")
    r = upd(cont)
    K.check(r is not None and r[1] == [] and "continues" in r[2][0], "MG321: a continued line is kept and noted")
    miss = "# SkyyTrees\nvein.cooldownSec=40\n"
    r = upd(miss)
    K.check(r is not None and r[0] == miss + mk + "\n" and r[1] == [] and r[2] == [], "MG321: no feller.logs line (the new built-in value) - the marker only")
    nw = base_t.replace(OLD_FELLER, NEW_FELLER)
    r = upd(nw)
    K.check(r is not None and r[0] == nw + mk + "\n" and r[1] == [], "MG321: already the new table - the marker only")
    K.check(upd(base_t + mk + "\n") is None and upd("# x " + MK321 + "\n" + base_t) is None, "MG321: the marker in a comment line = nothing to do (runs once)")
    K.check(upd(base_t + "x.y=" + MK321 + "\n") is not None, "MG321: the marker id inside a VALUE does not count")
    K.check(bool(Mig.sameAfter(base_t.encode("latin-1"), r_bytes(upd(base_t)[0]), JArray(JString)(["feller.logs"])))
            and not bool(Mig.sameAfter(base_t.encode("latin-1"), r_bytes(upd(base_t)[0] + "extra=1\n"), JArray(JString)(["feller.logs"]))),
            "MG321: sameAfter - only feller.logs may change (an added key is refused)")
    # ---- 7. Siphon's Health part + the Elemental Bubble line
    CL = [str(x) for x in Cls.CLASSES] if hasattr(Cls, "CLASSES") else None
    chp = [int(x) for x in Cls.CHP]
    K.check(sum(1 for x in chp if x) == 1 and min(chp) == -5, "T21 Siphon: CHP holds exactly one -5 (Mage PC2)")
    K.check(float(Fx.pctHp(None, -5.0)) == 0.0 and float(Cls.hpPct(None)) == 0.0, "T21 Siphon: no stat map / no player = 0 (never throws)")
    K.check(PKG + "TreeClass.hpPct" in g.get("TreeFx.stats", set()) and PKG + "TreeFx.pctHp" in g.get("TreeFx.stats", set()),
            "T21 Siphon: TreeFx.stats adds the class Health percent (bytecode)")
    K.check(PKG + "TreeSwing.total" in g.get("TreeSwing.apply", set()) and PKG + "TreeSwing.apply" in g.get("TreeTick.tick", set())
            and PKG + "TreeSwing.total" in g.get("TreeSwing.report", set()), "T21 swing: the tick and /tree swing use TreeSwing.total (bytecode)")
    K.check(PKG + "TreeMig321.run" in g.get("SkyyTreesPlugin.setup", set()), "T21 MG321: setup runs the update (bytecode)")
    K.save()


def r_bytes(t):
    return t.encode("latin-1")


def run_st1(out, jar, scratch, _home):
    run_st(out, jar, scratch, "1")


def run_st2(out, jar, scratch, _home):
    run_st(out, jar, scratch, "2")


if __name__ == "__main__":
    HK.run(name="SkyyTrees", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT21, added=ADDED,
           phases=[("t21", run_t21), ("ct", run_ct), ("st1", run_st1), ("st2", run_st2)], script=__file__)
