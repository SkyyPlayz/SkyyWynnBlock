"""Harness for SkyyMenu 0.3.33 (round hubchar: Stats is part of the Skills tab - a MERGED tab, kit skyyui HUB_MERGED; the Stats page's
sub-tabs; + Add / shortcuts keep the merged pages; tools/menu_0_3_33_patch.py). Build first:
    python tools/menu_0_3_33_patch.py && python SkyyMenu/build_skyymenu_0.3.33.py

    python SkyyMenu/test_skyymenu_0.3.33.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -XX:-UsePerfData, TEMP / TMP in the scratch folder; -Xverify:all over the
SkyyMenu 0.3.19 harness's engine stand-ins: the REAL PageManager / WindowManager, a command manager that records lines, players):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.32 -> 0.3.33: exactly the listed members differ, + HubHide; non-class entries: manifest.json only
  M    EXECUTED, with stand-ins of SkyySkills' Skills tab and SkyyTrees' Trees tab + SkyyClasses 0.1.33's merged Class tab:
       REG    hub:tab:character:stats = {SkyyMenu, Stats, 10, stats, MenuHubOpen, HubHide, character_stats, skills} (8 elements); HubHide
              FALSE with the Skills tab, TRUE without it; the Character strip = Skills, Trees (no Stats, no Class); no Class stand-in tab
       STATS  /stats (the Stats page) built into a REAL builder: 1114 x 974; the strip shows SKILLS selected, no Stats tab; the sub-tab row
              first in the body (YOUR STATS active = hub:stats, SKILLS = hub:skills, the caption beside them = the old sub line);
              every set / binding names an element; YOUR STATS = the page stays (status cleared); SKILLS = the Skills tab's Function
              ran; without SkyySkills the strip shows Stats again (a tab of its own)
       SHORT  + Add lists tab:character:stats right after Skills and tab:character:class right after Trees, every page once; their
              looks are "ok" (never locked) and say "part of the Skills / Trees tab"; a shortcut click on them opens the Stats page /
              runs the merged Class tab's Function (HubBar.openSub; HubBar.open says "hidden" for them)
       HUB    /character (MenuHub.run) still opens on Skills
  D    live     two starts on a scratch COPY of the live Skyy_SkyyMenu (NewBetaTest): the registry, the Stats page built both times;
                nothing written by either start
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, time, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyui as SUI

_s29 = importlib.util.spec_from_file_location("test_skyymenu_0_3_29", os.path.join(HERE, "test_skyymenu_0.3.29.py"))
T29 = importlib.util.module_from_spec(_s29)
_s29.loader.exec_module(T29)
T19 = T29.T19
build_page, jf, DECL_RE, WH_RE = T29.build_page, T29.jf, T29.DECL_RE, T29.WH_RE

VERSION = "0.3.33"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.32.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "hubchar", "menu")))
PKG = "com.skyy.menu."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyMenu")
SKYY = "d8ddde89-98b2-4739-983e-a39773d582b6"
ADDED = ["HubHide"]
SUBM = ["+m hostOf", "+m hostShown", "+m hostTab", "+m openSub", "+m putSub", "+m selOf", "+m subIcon", "+m subTabs"]
EXPECT = {
    "HubBar": SUBM,
    "MenuData": ["+f HT_HOST", "~<clinit>"],
    "MenuHub": ["~m register"],
    "MenuPage": ["~m candidates", "~m look", "~m openTab"],
    "StatsPage": ["~m build"],
    "SkyyMenuPlugin": ["~m setup"],
    "CfgRows": ["~m header"], "CfgFn": ["~m opExport"], "OpsPage": ["~<clinit>"],
}


def page_rules(K, cmds, evs, what, prefix_ok="Skyy"):
    """T29.page_rules + the tab icon hook path (SkyyHubTabs/) allowed (the 0.3.30 harness's twin)"""
    apps = SUI.Appends([(None if s is None else s.lstrip("#"), t) for ty, s, t, d in cmds if t is not None and ty and "Append" in ty])
    sets = [(s, d) for ty, s, t, d in cmds if ty == "Set"]
    try:
        SUI.check_page(apps, prefix_ok)
        K.check(True, "%s: check_page" % what)
    except Exception as e:
        K.check(False, "%s: check_page: %s" % (what, e))
    try:
        SUI.check_sky_paths(apps, tab_icons=True)
        K.check(True, "%s: sky paths" % what)
    except Exception as e:
        K.check(False, "%s: sky paths: %s" % (what, e))
    try:
        SUI.assert_proven(apps, what=what)
        K.check(True, "%s: proven properties only" % what)
    except Exception as e:
        K.check(False, "%s: assert_proven: %s" % (what, e))
    ids = set()
    for _p, mk in apps:
        ids |= set(x.group(2) for x in DECL_RE.finditer(SUI.render(mk)))
    bs = [s for s, _t in evs]
    bad = [s for s, _d in sets if s.lstrip("#").split(".")[0] not in ids] + [s for s in bs if s.lstrip("#") not in ids]
    K.check(not bad, "%s: every b.set / binding names an element that exists (%d sets, %d bindings): %s" % (what, len(sets), len(bs), bad[:4]))
    return apps, dict(sets)


def run_m(out, jar, scratch, _home):
    from jpype import JClass, JArray, JImplements, JOverride, JObject
    K = HK.Child(out)
    hcls = os.path.join(scratch, "hcls_m")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, jar], verify=True)
    E = T19.engine(scratch, hcls)
    JV = lambda n: JClass(PKG + n)
    Paths = E.Paths
    home = os.path.join(scratch, "home_m")
    os.makedirs(os.path.join(home, "layouts"), exist_ok=True)
    JV("PageGuard").STOP = False
    JV("PageGuard").EXEC = None
    ML = JV("MenuLayout")
    ML.DIR = Paths.get(os.path.join(home, "layouts"))
    ML.DEF_FILE = Paths.get(os.path.join(home, "layout-default.properties"))
    JV("SetStore").DIR = Paths.get(os.path.join(home, "settings"))
    JV("SetReg").ADMIN_FILE = Paths.get(os.path.join(home, "settings-defaults.properties"))
    JV("SetReg").registerOwn()
    JV("MenuIO").begin()
    HB, MH = JV("HubBar"), JV("MenuHub")
    br = JV("MenuUtil").bridge()
    UniC = JClass("com.hypixel.hytale.server.core.universe.Universe")
    byU = jf(UniC.class_, "playersByUuid").get(UniC.get())
    TRUE, FALSE = JClass("java.lang.Boolean").TRUE, JClass("java.lang.Boolean").FALSE
    S, Int = JClass("java.lang.String"), JClass("java.lang.Integer")
    SysC = JClass("java.lang.System")
    same = lambda a, b_: (a is None and b_ is None) or (a is not None and b_ is not None and int(SysC.identityHashCode(a)) == int(SysC.identityHashCode(b_)))

    @JImplements("java.util.function.Function")
    class Stub(object):
        def __init__(self, ans):
            self.calls, self.ans = [], ans

        @JOverride
        def apply(self, x):
            self.calls.append(str(x))
            return self.ans

    def mkp(uid, name):
        P = E.player(uid, name=name)
        byU.put(uid, P.pr)
        E.UniH.PL.add(P.pr)
        E.PLAYERS.add(P.pr)
        return P
    P = mkp(E.PLAIN, "SkyyPlain")
    u = P.pr.getUuid()
    PGM = lambda X: X.pm.getCustomPage()

    def click(X, pg, a):
        pg.handleDataEvent(X.ref, X.st, '{"a":"%s"}' % a)
        E.pump(X)
        return PGM(X)
    for n_ in ("skills", "tree", "class", "stats"):
        E.CM.cmds.put(n_, E.U.allocateInstance(JClass("skyymenu19.Cmd").class_))
    skf, trf, clf, clh = Stub(TRUE), Stub(TRUE), Stub(TRUE), Stub(FALSE)
    skills = JArray(JObject)([S("SkyySkills"), S("Skills"), Int.valueOf(20), S("skills"), skf, None])
    trees = JArray(JObject)([S("SkyyTrees"), S("Trees"), Int.valueOf(30), S("tree"), trf, None])
    klass = JArray(JObject)([S("SkyyClasses"), S("Class"), Int.valueOf(40), S("class"), clf, clh, S("character_class"), S("trees")])
    # ================================================================ REG
    n = int(MH.register())
    K.eq(n, 7, "REG: Menu's 7 own tabs put")
    K.check(br.get("hub:tab:character:class") is None, "REG: no Class stand-in tab (Class is merged into Trees; SkyyClasses puts its own)")
    e = br.get("hub:tab:character:stats")
    ok = e is not None and len(e) == 8 and [str(x) for x in (e[0], e[1], e[3], e[6], e[7])] == ["SkyyMenu", "Stats", "stats", "character_stats", "skills"] \
        and int(e[2]) == 10 and str(e[4].getClass().getName()) == PKG + "MenuHubOpen" and str(e[5].getClass().getName()) == PKG + "HubHide"
    K.check(ok, "REG: hub:tab:character:stats = {SkyyMenu, Stats, 10, stats, MenuHubOpen, HubHide, character_stats, skills} (%s)" % (None if e is None else [str(x) for x in e]))
    # FIX (critic 1): the REAL no-SkyySkills state - Menu's own stand-in Skills tab holds the key, invisible while /skills is missing
    _sk = br.get("hub:tab:character:skills")
    K.check(_sk is not None and str(_sk[0]) == "SkyyMenu" and str(_sk[5].getClass().getName()) == PKG + "MenuVtVis",
            "REG: Menu put its stand-in Skills tab (MenuVtVis)")
    _skc = E.CM.cmds.remove("skills")
    _ct0 = [str(t[0]) for t in HB.tabs("character", u)]
    K.check(e[5].apply(u) == TRUE and "stats" in _ct0 and "skills" not in _ct0,
            "REG FIX1: no /skills (invisible stand-in Skills) -> Stats is a tab of its own (%s)" % _ct0)
    K.eq(str(HB.selOf("character", "stats")), "stats", "REG FIX1: selOf(stats) = stats while the Skills stand-in is invisible")
    K.check(not bool(HB.hostShown("character", "skills", u)), "REG FIX1: hostShown(skills) false")
    E.CM.cmds.put("skills", _skc)
    K.check(e[5].apply(u) == FALSE and str(HB.selOf("character", "stats")) == "skills",
            "REG FIX1: /skills back (visible stand-in Skills) -> Stats hidden, selOf = skills")
    br.remove("hub:tab:character:skills")      # (the stand-in Menu put for /skills - the harness's command manager has it)
    K.check(e[5].apply(u) == TRUE and "stats" in [str(t[0]) for t in HB.tabs("character", u)], "REG: without a Skills tab Stats is a tab of its own")
    # FIX (critic 1): a published but player-hidden host = not a host
    _hid = JArray(JObject)([S("SkyySkills"), S("Skills"), Int.valueOf(20), S("skills"), skf, Stub(FALSE)])
    br.put("hub:tab:character:skills", _hid)
    K.check(e[5].apply(u) == TRUE and str(HB.selOf("character", "stats")) == "stats", "REG FIX1: a Skills tab hidden from the player -> Stats shown")
    br.remove("hub:tab:character:skills")
    br.put("hub:tab:character:skills", skills)
    br.put("hub:tab:character:trees", trees)
    br.put("hub:tab:character:class", klass)
    K.check(e[5].apply(u) == FALSE, "REG: HubHide FALSE while the Skills tab is published")
    _ct = [str(t[0]) for t in HB.tabs("character", u)]
    K.check(_ct[:2] == ["skills", "trees"] and "stats" not in _ct and "class" not in _ct, "REG: the Character strip starts Skills, Trees - no Stats, no Class (%s)" % _ct)
    K.eq([(str(x[0]), str(x[2])) for x in HB.subTabs("character", u)], [("stats", "skills"), ("class", "trees")], "REG: subTabs = Stats in Skills, Class in Trees")
    K.eq(str(HB.selOf("character", "stats")), "skills", "REG: selOf(stats) = skills")
    # ================================================================ STATS
    sp = JV("StatsPage")(P.pr, 0)
    P.pm.openCustomPage(P.ref, P.st, sp)
    E.pump(P)
    c, ev = build_page(sp, P)
    apps, sets = page_rules(K, c, ev, "STATS", "SkyyStat")
    K.eq(tuple(map(int, WH_RE.search(apps[0][1]).groups())), (1114, 974), "STATS: root 1114 x 974 (0.3.32 966 + the sub-tab row)")
    tabs = [mk for p_, mk in apps if p_ == "SkyyStatFHubTabs"]
    tb = [mk for mk in tabs if mk.startswith(("TextButton", "Button"))]
    labs = [mk for p_, mk in apps if (p_ or "").startswith("SkyyStatFHubT") and mk.startswith("Label")]
    K.check(len(tb) == len(_ct) and "Tab_Selected" in tb[0] and not [mk for mk in tb[1:] if "Tab_Selected" in mk] and '"Skills"' in tb[0]
            and not any('"Stats"' in mk for mk in labs + tb), "STATS: the strip = Skills (selected, first) + the others, no Stats tab (%d tabs)" % len(tb))
    body = [mk for p_, mk in apps if p_ == "SkyyStat"]
    K.check(len(body) > 3 and body[0].startswith("Group #SkyyStatFHubTabs") and body[1].startswith("Group #SkyyStatSubRow "),
            "STATS: the sub-tab row is the body's first row under the strip (%s)" % [mk[:28] for mk in body[:3]])
    sub = [mk for p_, mk in apps if p_ == "SkyyStatSubRow"]
    K.check(len(sub) == 3 and "#SkyyStatSubMe " in sub[0] and "Primary" in sub[0] and "#SkyyStatSubSk " in sub[1] and "Primary" not in sub[1] and "#SkyyStatSub " in sub[2],
            "STATS: YOUR STATS (active) | SKILLS | the caption (%s)" % [mk[:50] for mk in sub])
    K.check(any(s_ == "#SkyyStatSubMe" and "hub:stats" in t for s_, t in ev) and any(s_ == "#SkyyStatSubSk" and "hub:skills" in t for s_, t in ev),
            "STATS: YOUR STATS = hub:stats, SKILLS = hub:skills")
    K.check("What applies to you" in str(sets.get("#SkyyStatSub.Text")), "STATS: the old sub line sits beside the sub-tabs")
    sp.status = "x"
    cur = click(P, sp, "hub:stats")
    K.check(same(cur, sp) and str(sp.status) == "", "STATS: YOUR STATS = the page stays (status cleared)")
    del skf.calls[:]
    cur = click(P, sp, "hub:skills")
    K.check(skf.calls == [str(u)], "STATS: SKILLS = the Skills tab's Function ran (%s)" % skf.calls)
    br.remove("hub:tab:character:skills")
    sp2 = JV("StatsPage")(P.pr, 0)
    P.pm.openCustomPage(P.ref, P.st, sp2)
    E.pump(P)
    c2, ev2 = build_page(sp2, P)
    a2, _s2 = page_rules(K, c2, ev2, "STATS without SkyySkills", "SkyyStat")
    tb2 = [mk for p_, mk in a2 if p_ == "SkyyStatFHubTabs" and mk.startswith(("TextButton", "Button"))]
    lab2 = [mk for p_, mk in a2 if (p_ or "").startswith("SkyyStatFHubT") and mk.startswith("Label")]
    K.check(len(tb2) == len(_ct) and "Tab_Selected" in tb2[0] and ('"Stats"' in tb2[0] or any('"Stats"' in mk for p_, mk in a2 if p_ == "SkyyStatFHubT0")), "STATS without SkyySkills: Stats is a tab of its own again, selected")
    br.put("hub:tab:character:skills", skills)
    # ================================================================ SHORT
    hm = JV("MenuPage")(P.pr, "main")
    P.pm.openCustomPage(P.ref, P.st, hm)
    E.pump(P)
    cand = [str(k) for k in hm.candidates(True, True)]
    K.check("tab:character:stats" in cand and "tab:character:class" in cand, "SHORT: + Add still lists Stats and Class")
    if "tab:character:stats" in cand and "tab:character:class" in cand:
        K.check(cand.index("tab:character:stats") == cand.index("tab:character:skills") + 1 and cand.index("tab:character:class") == cand.index("tab:character:trees") + 1,
                "SHORT: Stats right after Skills, Class right after Trees")
    K.check(len(cand) == len(set(cand)), "SHORT: every entry once (%d)" % len(cand))
    for k, host in (("tab:character:stats", "Skills"), ("tab:character:class", "Trees")):
        lk = hm.look(k, False)
        K.check(lk is not None and str(lk[5]) == "ok" and ("part of the %s tab" % host) in str(lk[2]), "SHORT: %s looks ok (never locked): %s" % (k, None if lk is None else str(lk[2]).replace("\n", " | ")))
    K.check(str(HB.open(P.pr, u, "character", "class")) == "hidden", "SHORT: the kit's open() says hidden for the merged Class tab (why openSub)")
    del clf.calls[:]
    hm.openTab(P.ref, P.st, "character", "class")
    E.pump(P)
    K.check(clf.calls == [str(u)], "SHORT: the Class shortcut opens the merged Class tab through its Function (%s)" % clf.calls)
    hm = JV("MenuPage")(P.pr, "main")
    P.pm.openCustomPage(P.ref, P.st, hm)
    E.pump(P)
    hm.openTab(P.ref, P.st, "character", "stats")
    E.pump(P)
    K.check(str(PGM(P).getClass().getSimpleName()) == "StatsPage", "SHORT: the Stats shortcut opens the Stats page")
    # ================================================================ HUB
    del skf.calls[:]
    r = str(MH.run(P.pr, "character"))
    K.check(r == "bridge" and skf.calls == [str(u)], "HUB: /character opens on Skills (%s)" % r)
    for k_ in ("skills", "trees", "class"):
        br.remove("hub:tab:character:" + k_)
    MH.clearAll()
    JV("MenuIO").stop(2000)
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    hcls = os.path.join(scratch, "hclasses_live")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, jar], verify=True)
    E = T19.engine(scratch, hcls)
    JV = lambda n: JClass(PKG + n)
    Paths = E.Paths
    JV("PageGuard").STOP = False
    JV("PageGuard").EXEC = None
    ML = JV("MenuLayout")
    ML.DIR = Paths.get(os.path.join(home, "layouts"))
    ML.DEF_FILE = Paths.get(os.path.join(home, "layout-default.properties"))
    JV("SetStore").DIR = Paths.get(os.path.join(home, "settings"))
    JV("Given").DIR = Paths.get(os.path.join(home, "given-profile"))
    JV("Given").LEGACY = Paths.get(os.path.join(home, "given"))
    JV("SetReg").ADMIN_FILE = Paths.get(os.path.join(home, "settings-defaults.properties"))
    Cfg = JV("MenuCfg")
    Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
    UniC = JClass("com.hypixel.hytale.server.core.universe.Universe")
    byU = jf(UniC.class_, "playersByUuid").get(UniC.get())
    snaps = [T19.snap(home)]
    res = []
    for n_ in range(2):
        ML.OWN.clear()
        ML.MIGRATED.clear()
        JV("MenuIO").begin()
        Cfg.init()
        Cfg.load()
        ML.loadDefault()
        JV("SetReg").loadAdmin(True)
        JV("SetReg").registerOwn()
        JV("SetReg").drain()
        P = E.player(E.UUID.fromString(SKYY))
        byU.put(P.pr.getUuid(), P.pr)
        n = int(JV("MenuHub").register())
        JV("SetLoadTask").preload(P.pr)
        ML.preload(P.pr.getUuid())
        r = str(JV("HubBar").openSub(P.pr, P.pr.getUuid(), "character", "stats"))
        E.pump(P)
        pg = P.pm.getCustomPage()
        c, _e = build_page(pg, P)
        ok = r == "bridge" and str(pg.getClass().getSimpleName()) == "StatsPage" and len(c) > 10
        time.sleep(0.8)
        ML.flushAll()
        JV("SetStore").flushAll()
        JV("MenuIO").stop(2000)
        JV("MenuHub").clearAll()
        snaps.append(T19.snap(home))
        res.append([n == 7, ok])
    K.eq(res, [[True, True], [True, True]], "D: two starts on a COPY of the live Skyy_SkyyMenu: registry + the Stats page (openSub) built")
    a, b1, b2 = snaps
    K.check(a == b1 == b2, "D: neither start wrote a file (changed: %s)" % sorted(set(k for k in set(a) | set(b2) if a.get(k) != b2.get(k))))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("m", run_m), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyMenu"))
