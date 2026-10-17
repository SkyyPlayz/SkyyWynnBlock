"""Harness for SkyyExploration 0.2.14 (the /exploreadmin editor on the kit 1.7 hub page: Settings hub, row 2 = Server Setup selected, the
ONE sub-tab row Spots | Checklist | Island, the Spots / Checklist / player lists as scroll lists with grow rows and 'Show 200 more', no
pager, no back button; tools/exploration_0_2_14_patch.py).
Build first: python tools/exploration_0_2_14_patch.py && python SkyyExploration/build_skyyexploration_0.2.14.py

    python SkyyExploration/test_skyyexploration_0.2.14.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.2.13 -> 0.2.14: AdminPage only (+ the version texts); non-class entries: manifest.json
  PAGES test_skyyexploration_0.2.13.py's PAGES phase on the 0.2.14 jar (World > Explore, the checklist, titles, the reveal page)
  ADMIN (tools/hub_tab_kit.stage, the REAL PageManager / UICommandBuilder, a stand-in PermissionsModule: the admin has
        skyyexploration.admin): EVERY admin view built through its real build() - Spots (empty, rows, a selected spot, Sure - Remove),
        Checklist (none selected, a custom entry with Tick / Untick, a spot entry), Island (+ the player scroll list), a world that never
        pays exploration (Spots + Island) - each: SUI.check_page, the Sky paths, every b.set / binding names an element,
        SUI.assert_menu_page (1600 x 980, row 1 + row 2 = Settings with Server Setup selected, ONE sub row, no back / pager text);
        the sub row = SPOTS | CHECKLIST | ISLAND (sub_tab_markup byte for byte, the selected one unbound); the lists are scroll lists, few
        rows grow (= SUI.grow_pick), 230 entries -> 200 rows + 'Show 200 more' -> 230 rows; the old xprev / xnext only answer; the kit
        clicks (row 1 Home -> /skymenu, row 2 Server Setup -> /modconfig, the X closes) also for a player who lost the permission
  SAVES the SAME edit script (every editor: add / rename / radius + XP / secret / checklist / move / remove spots; custom / count /
        region / chest entries, entry text, tick / untick, take off the checklist, remove; island name / checklist / rewards / default XP;
        the two server-wide switches) clicked on the 0.2.13 page (child SAVES-OLD, the 0.2.13 jar) and on the 0.2.14 page: the result
        line after every click and every saved byte (worlds/*.properties, config.properties, players/, chests/; admin.log without its
        time stamps) are identical
  RN, CAP, X, D   the 0.2.13 harness's phases on the 0.2.14 jar (D: 0.2.13 vs 0.2.14 records equal)
  AA    engine-access audit
Not testable without the game (UNVERIFIED): the client drawing the 1600 x 980 admin page, the grown rows, the scroll lists.
Exit code 1 on any failure.
"""
import os, sys, re, json, importlib.util, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import hub_tab_kit as HT
import skyyui as SUI

VERSION = "0.2.14"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyExploration-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyExploration-0.2.13.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "explore14", "harness")))
PKG = "com.skyy.explore."


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


_rc = HK.run_compare
T13 = tmod("test_skyyexploration_0.2.13.py", "test_skyyexploration_0_2_13")
HK.run_compare = _rc
T12, T28 = T13.T12, T13.T28
T28.OLD_JAR = OLD_JAR                    # RN: jar entry names = 0.2.13's; D: 0.2.13 vs 0.2.14 records

EXPECT = {"AdminPage": ["+<clinit>", "+f HS", "+f lim", "~c ", "~m build", "~m checkTab", "~m clip", "~m handleDataEvent", "+m hubClick",
                        "~m islandTab", "~m lists", "+m more", "-m pager", "+m sortButton", "~m spotsTab"],   # lists: the 1046 px list column
          # the kit's SUI.HUB_TABS row Character > Accessories now runs /charms ('Void Charms', SkyyMenu 0.3.36 - after 0.2.13 was built):
          # the reveal page's back-command map (MAP_CMD) is rebuilt from it - the constant pool differs by the string 'charms' only
          "LgReveal": ["~<clinit>"],
          # the version texts only (constant pools checked)
          "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "ExpCfg": ["~m load"], "ExpLgMig": ["~m logLine", "~m migrate"],
          "SkyyExplorationPlugin": ["~m setup"]}
ADDED = []
XA_TABS = ("Spots", "Checklist", "Island")
UUID0 = "00000000-0000-0000-0000-0000000000e2"
UUID1 = "00000000-0000-0000-0000-0000000000e3"
PERM = "skyyexploration.admin"
FAIL_TEXT = "-That page could not open right now - try again."


def stage_admin(scratch, jar, label):
    """the hub_tab_kit stage + a stand-in PermissionsModule (the admin has skyyexploration.admin, the other player nothing) + the
    admin standing at 5 64 5 + the mod's folders in scratch"""
    from jpype import JClass, JArray, JObject, JImplements, JOverride
    import shutil
    shutil.rmtree(os.path.join(scratch, label, "mods"), ignore_errors=True)     # a fresh mod folder every run
    E = HT.stage(os.path.join(scratch, label), jar)
    E.HB = PKG + "HubBar"
    J = lambda n: JClass(PKG + n)
    home = os.path.join(scratch, label, "mods", "Skyy_SkyyExploration")
    os.makedirs(os.path.join(home, "worlds"), exist_ok=True)
    T13.prep(E, J, home)
    Str = JClass("java.lang.String")
    for hid in SUI.HUB_ROW_IDS:
        title = "Home" if hid == SUI.HUB_HOME else SUI.hub_title_now(hid)
        cmd = "skymenu" if hid == SUI.HUB_HOME else SUI.HUB_DEFS[hid][1]
        E.bridge.put("hub:def:" + hid, JArray(JObject)([Str(title), Str(cmd), Str("Skyy_Menu")]))
    # Settings > Server Setup as SkyyMenu puts it (no open Function: the bar runs /modconfig)
    E.bridge.put("hub:tab:settings:setup", JArray(JObject)([Str("SkyyMenu"), Str("Server Setup"), JClass("java.lang.Integer").valueOf(50), Str("modconfig"), None, None]))
    J("CfgPub").start(E.Paths.get(os.path.dirname(home)), J("ExpCfg").LOG)    # the config kit (Server Setup + the switches) on scratch
    HashSet = JClass("java.util.HashSet")
    USERS = {UUID0: [PERM], UUID1: []}

    def jset(xs):
        h_ = HashSet()
        for x_ in xs:
            h_.add(x_)
        return h_

    @JImplements("com.hypixel.hytale.server.core.permissions.provider.PermissionProvider")
    class Prov:
        @JOverride
        def getName(self): return "explore-test"
        @JOverride
        def getUserPermissions(self, u): return jset(USERS.get(str(u), []))
        @JOverride
        def getGroupsForUser(self, u): return jset([])
        @JOverride
        def getGroupPermissions(self, g): return jset([])
        @JOverride
        def getEffectiveGroupPermissions(self, g): return jset([])
        @JOverride
        def getGroupParent(self, g): return None
        @JOverride
        def getAllRegisteredGroups(self): return jset([])
        @JOverride
        def getUsersWithPermission(self, n): return HashSet()
        @JOverride
        def addUserPermissions(self, *a): return None
        @JOverride
        def removeUserPermissions(self, *a): return None
        @JOverride
        def addUserToGroup(self, *a): return None
        @JOverride
        def addGroupPermissions(self, *a): return None
        @JOverride
        def removeGroupPermissions(self, *a): return None
        @JOverride
        def removeUserFromGroup(self, *a): return None
        @JOverride
        def setUserGroup(self, *a): return None
    E._prov = Prov()
    PM = JClass("com.hypixel.hytale.server.core.permissions.PermissionsModule")
    pm = E.U.allocateInstance(PM.class_)
    provs = JClass("java.util.ArrayList")()
    provs.add(E._prov)
    HT.jf(PM.class_, "providers").set(pm, provs)
    HT.jf(PM.class_, "virtualGroups").set(pm, JClass("java.util.HashMap")())
    HT.jf(PM.class_, "instance").set(None, pm)
    E.USERS = USERS
    P = E.mkp(JClass("java.util.UUID").fromString(UUID0), "XaAdmin")
    Q = E.mkp(JClass("java.util.UUID").fromString(UUID1), "XaPlayer")
    E.bridge.put("hub:last:" + UUID0, JClass("java.util.concurrent.ConcurrentHashMap")())
    TRC = JClass("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
    V3 = JClass("com.hypixel.hytale.math.vector.Vector3d") if _has("com.hypixel.hytale.math.vector.Vector3d") else JClass("org.joml.Vector3d")
    tc = E.U.allocateInstance(TRC.class_)
    HT.jf(TRC.class_, "position").set(tc, V3(5.5, 64.0, 5.5))
    P.st.row(P.ref).put(TRC.getComponentType(), tc)
    E.TC = tc
    return E, J, home, P, Q


def _has(cn):
    from jpype import JClass
    try:
        JClass(cn)
        return True
    except Exception:
        return False


def click(E, P, pg, a, extra=None):
    """one click on the admin page (past its 1 s guard); extra = the field values the EventData carries"""
    d = {"a": a}
    d.update(extra or {})
    pg.lastBuild = 0
    pg.handleDataEvent(P.ref, P.st, json.dumps(d))
    E.pump(P)
    return E.pg(P)


# ---------------------------------------------------------------------------------------------------------------- SAVES: one edit script
def edit_script(E, J, P, Q, pg, log):
    """every editor of the admin page, clicked the same way on both jars; log gets (step, result line) after each click"""
    def c(a, **kw):
        cur = click(E, P, pg, a, kw)
        log.append([a, str(pg.msg), bool(E.same(cur, pg))])
        return cur

    def pick(want_spot, nth=0):
        ids = [str(x) for x in pg.rowIds if x is not None]
        hits = [i for i, x in enumerate(ids) if x.startswith("s") == want_spot]
        return hits[nth] if len(hits) > nth else -1
    # Spots
    c("xadd", **{"@XNName": "Old Well", "@XNRad": "", "@XNXp": ""})
    c("xnsec", **{"@XNName": "Hidden Grotto", "@XNRad": "6", "@XNXp": "250"})
    c("xadd", **{"@XNName": "Hidden Grotto", "@XNRad": "6", "@XNXp": "250"})
    c("xadd", **{"@XNName": "Sky Pillar", "@XNRad": "10", "@XNXp": "120"})
    c("xadd", **{"@XNName": "Old Well", "@XNRad": "", "@XNXp": ""})            # a refusal (the same name)
    c("xadd", **{"@XNName": "Lantern Rock", "@XNRad": "abc", "@XNXp": "5"})    # a refusal (a bad radius)
    c("xsort")
    c("xsort")
    c("xedit0")
    c("xren", **{"@XEName": "Sky Pillar Top"})
    c("xsave", **{"@XERad": "12", "@XEXp": "300"})
    c("xsave", **{"@XERad": "-4", "@XEXp": "300"})                             # a refusal
    c("xesec", **{"@XEName": "Sky Pillar Top", "@XERad": "12", "@XEXp": "300"})
    c("xechk", **{"@XEName": "Sky Pillar Top", "@XERad": "12", "@XEXp": "300"})
    c("xechk", **{"@XEName": "Sky Pillar Top", "@XERad": "12", "@XEXp": "300"})
    c("xmove")
    c("xedit1")
    c("xrm")
    c("xrm")                                                                  # Sure - Remove
    # Checklist
    c("xtab1")
    c("xccustom", **{"@XCText": "Ring the old bell"})
    c("xccustom", **{"@XCText": ""})                                          # a refusal
    c("xccount", **{"@XCNum": "5"})
    c("xccount", **{"@XCNum": "x"})                                           # a refusal
    c("xczone")
    c("xczall")
    c("xcchest")
    pg.lastBuild = 0
    E.pump(P)
    i = pick(False)
    c("xcedit%d" % i)
    c("xcsave", **{"@XCEText": "Ring the bell twice"})
    c("xctick", **{"@XCPlayer": "XaPlayer"})
    c("xcuntick", **{"@XCPlayer": "XaPlayer"})
    c("xctick", **{"@XCPlayer": "XaPlayer"})
    c("xctick", **{"@XCPlayer": "Nobody"})                                    # a refusal
    i = pick(False, 1)
    c("xcedit%d" % i)
    c("xcrm")
    c("xcrm")
    i = pick(True)
    c("xcedit%d" % i)
    c("xcoff")
    c("xcoff")
    # Island
    c("xtab2")
    c("xiname", **{"@XIName": "Home Isle"})
    c("xichk")
    c("xichk")
    c("xirw", **{"@XIRwXp": "500", "@XIRwCo": "25"})
    c("xirw", **{"@XIRwXp": "-1", "@XIRwCo": "25"})                         # a refusal
    c("xidef", **{"@XIDefSp": "80", "@XIDefSe": "160"})
    c("xidef", **{"@XIDefSp": "", "@XIDefSe": "-1"})
    c("xispots")
    c("xichecks")
    c("xispots")
    c("xrefresh")


def snapshot(home):
    """every saved byte under the mod folder (the *.log files: the time stamps cut; config history snapshots: by content; the default
    config.properties header names the jar version - 'SkyyExploration 0.2.13' / '0.2.14' -> '<version>', the only allowed difference)"""
    out = {}
    for dp, _dn, fns in os.walk(home):
        for fn in fns:
            p = os.path.join(dp, fn)
            rel = os.path.relpath(p, home).replace(os.sep, "/")
            data = re.sub(rb"SkyyExploration 0\.2\.1[34]\b", b"SkyyExploration <version>", open(p, "rb").read())
            data = re.sub(rb"\d{8}-\d{6}-\d{3}", b"<stamp>", data)      # the config history's snapshot stamps (file names + index.log)
            if rel.endswith(".log"):
                data = re.sub(rb"\d{4}-?\d\d-?\d\d[ T_-]?\d\d:?\d\d(:?\d\d([.,]\d+)?)?", b"<time>", data)
            if "/" in rel and "history" in rel.split("/")[0].lower():
                rel = rel.split("/")[0] + "/<snapshot " + hashlib.sha1(data).hexdigest()[:12] + ">"
            out[rel] = hashlib.sha1(data).hexdigest() + " " + str(len(data))
    return out


def run_saves(out, jar, scratch, _home, old=False):
    K = HK.Child(out)
    use = OLD_JAR if old else jar
    label = "saves-old" if old else "saves-new"
    E, J, home, P, Q = stage_admin(scratch, use, label)
    pg = J("AdminPage")(P.pr, 0)
    P.pm.openCustomPage(P.ref, P.st, pg)
    E.pump(P)
    K.check(E.same(E.pg(P), pg) and bool(J("ExAdminOps").perm(P.pr)), "%s: the admin page is open, the admin has %s" % (label, PERM))
    log = []
    edit_script(E, J, P, Q, pg, log)
    E.pump(P)
    sv = J("ExpSaver")()
    for _k in range(5):
        sv.run()                                  # the 2 s saver: the append queue, the world files, the player files
    J("CfgPub").flush()                           # the config kit's pending saves + log lines
    snap = snapshot(home)
    worlds = sorted(k for k in snap if k.startswith("worlds/"))
    K.check(worlds and "config.properties" in snap, "%s: the edits saved files (%s)" % (label, worlds))
    K.check(sum(1 for _a, m, _s in log if m.startswith("+")) >= 20, "%s: most edits succeeded (%d of %d)" % (label, sum(1 for _a, m, _s in log if m.startswith("+")), len(log)))
    files = {}
    for k in worlds + ["config.properties"]:
        files[k] = open(os.path.join(home, k), encoding="utf8", errors="replace").read()
    rec = {"log": log, "snap": snap, "files": files}
    with open(os.path.join(scratch, label + ".rec.json"), "w") as f:
        json.dump(rec, f, indent=1)
    if not old:
        oldp = os.path.join(scratch, "saves-old.rec.json")
        if not os.path.isfile(oldp):
            K.check(False, "SAVES: the 0.2.13 run left no record")
        else:
            o = json.load(open(oldp))
            for i, (a, b_) in enumerate(zip(o["log"], log)):
                if a[:2] != b_[:2]:
                    K.check(False, "SAVES step %d %s: 0.2.13 said %r, 0.2.14 says %r" % (i, a[0], a[1], b_[1]))
            K.eq(len(log), len(o["log"]), "SAVES: the same number of clicks")
            K.check(all(a[:2] == b_[:2] for a, b_ in zip(o["log"], log)),
                    "SAVES: the result line after every one of the %d clicks is the same as 0.2.13's" % len(log))
            diff = sorted(k for k in set(o["snap"]) | set(snap) if o["snap"].get(k) != snap.get(k))
            K.check(not diff, "SAVES: every saved byte equals 0.2.13's (the version in the config header aside; %d files: %s) - differ: %s" % (len(snap), ", ".join(sorted(snap)[:8]), diff))
            for k in diff:
                if k in o["files"] and k in files:
                    import difflib
                    print("\n".join(list(difflib.unified_diff(o["files"][k].splitlines(), files[k].splitlines(), "0.2.13 " + k, "0.2.14 " + k, lineterm=""))[:40]))
            K.notes.append("SAVES: %d clicks, %d ok results, files %s" % (len(log), sum(1 for _a, m, _s in log if m.startswith("+")), sorted(snap)))
    K.save()


def run_saves_old(out, jar, scratch, home):
    run_saves(out, jar, scratch, home, old=True)


# ---------------------------------------------------------------------------------------------------------------- ADMIN: every view
def run_admin(out, jar, scratch, _home):
    from jpype import JClass, JArray, JInt, JString
    K = HK.Child(out)
    E, J, home, P, Q = stage_admin(scratch, jar, "admin")
    XP, HB = J("AdminPage"), J("HubBar")
    WF = J("ChestReg").wf
    wn = str(P.st.getExternalData().getWorld().getName())
    hs = [int(x) for x in XP.HS]
    LIST_IN = 600 - 44 - 8
    K.eq(hs, SUI.grow_row_sizes(LIST_IN, 66, gap=3), "GROW: AdminPage.HS = the kit's grow_row_sizes for the %d px list room (%s)" % (LIST_IN, hs))
    set_tabs = [(r[0], SUI.hub_tab_label("settings", r[0])) for r in SUI.hub_page_tabs("settings") if r[0] == "setup"]

    def built(pg, what):
        cmds, evs = HT.build(pg, P)
        apps = SUI.Appends([(None if s_ is None else s_.lstrip("#"), t) for ty, s_, t, d_ in cmds if t is not None and ty and "Append" in ty])
        sets = [(s_, T13.unq(d_)) for ty, s_, t, d_ in cmds if ty == "Set"]
        K.check(len(apps) > 8 and len(apps) + len(sets) == len(cmds), "%s: %d appends + %d sets" % (what, len(apps), len(sets)))
        try:
            SUI.check_page(apps, "SkyyXa")
            K.check(True, "%s: check_page (markup rules, parents, no duplicate id)" % what)
        except Exception as e:
            K.check(False, "%s: check_page: %s" % (what, e))
        try:
            SUI.assert_proven(apps, what=what)
            K.check(True, "%s: assert_proven (only properties the game is known to draw)" % what)
        except Exception as e:
            K.check(False, "%s: assert_proven: %s" % (what, e))
        try:
            els = SUI.check_sky_paths(apps, tab_icons=True)
            K.check({"Header", "HeaderOrnament", SUI.HUB_FRAME["settings"], "Close"} <= set(els), "%s: the Sky Window paths (settings frame)" % what)
        except Exception as e:
            K.check(False, "%s: sky paths: %s" % (what, e))
        ids = set()
        for _p, mk in apps:
            ids |= set(x.group(2) for x in HT.DECL_RE.finditer(SUI.render(mk)))
        bs = [s_ for s_, _t in evs]
        bad = [s_ for s_, _d in sets if s_.lstrip("#").split(".")[0] not in ids] + [s_ for s_ in bs if s_.lstrip("#") not in ids]
        K.check(not bad, "%s: every b.set / binding names an element that exists (%d sets, %d bindings): %s" % (what, len(sets), len(bs), bad[:4]))
        try:
            info = SUI.assert_menu_page(apps, hub="settings", what=what, sets=sets)
            K.check(info["rows"] == 2 and info["subs"] == 1, "%s: assert_menu_page (1600 x 980, rows 1 + 2, ONE sub row, no back button, no pager)" % what)
        except Exception as ex:
            K.check(False, "%s: assert_menu_page: %s" % (what, ex))
        root = apps[0][1] if apps else ""
        K.check(apps and apps[0][0] is None and root.startswith("Group #SkyyXaF { Anchor: (Width: 1600, Height: 980)"), "%s: the root #SkyyXaF 1600 x 980" % what)
        txt = " ".join(str(t) for _ty, _s, t, _d in cmds if t) + " " + " ".join(v for _s, v in sets)
        K.check(not re.search(r'Text: "(< ?Prev|Next >|< ?Back|Close|< ?Menu|< Server Setup)"', txt) and " - page " not in txt,
                "%s: no '< Prev' / 'Next >' / Back / Close / '< Menu' / 'page x of y'" % what)
        sr = [mk for _p, mk in apps if _p == "SkyyXaFSub" and mk.startswith("TextButton")]
        t = int(pg.tab)
        K.check(sr == [SUI.sub_tab_markup("SkyyXaF", i, XA_TABS[i], i == t) for i in range(3)],
                "%s: the sub row = SPOTS | CHECKLIST | ISLAND (sub_tab_markup, %s selected)" % (what, XA_TABS[t]))
        K.check(not [x for s_, x in evs if s_ == "#SkyyXaFSub%d" % t]
                and all(any(("xtab%d" % i) in x for s_, x in evs if s_ == "#SkyyXaFSub%d" % i) for i in range(3) if i != t),
                "%s: the selected sub-tab unbound, the others xtab<i>" % what)
        want = SUI.hub_big_tabs_preview("SkyyXaF", "settings", set_tabs, "setup")
        got = [(p, mk) for p, mk in apps if p == "SkyyXaFBigTabs" or (p or "").startswith("SkyyXaFBigT")]
        K.check(got == list(want), "%s: row 2 = the Settings tabs registered, Server Setup selected (hub_big_tabs_preview byte for byte)" % what)
        K.check(str(dict(sets).get("#SkyyXaTitle.Text", "")).startswith("Exploration admin - "), "%s: the heading at the right of the sub row (%s)" % (what, dict(sets).get("#SkyyXaTitle.Text")))
        return cmds, evs, apps, dict(sets)

    def hgt(apps, ident):
        mk = [m_ for _p, m_ in apps if re.match(r"(Group|Label|Button|TextButton) #%s " % ident, m_)]
        m = re.search(r"Height: (\d+)", mk[0]) if mk else None
        return int(m.group(1)) if m else None

    def is_scroll(apps, ident):
        return any("TopScrolling" in mk for _p, mk in apps if mk.startswith("Group #%s " % ident))

    def opn(tab):
        pg = XP(P.pr, tab)
        P.pm.openCustomPage(P.ref, P.st, pg)
        E.pump(P)
        return pg
    # ---- Spots, empty
    pg = opn(0)
    c, e, apps, sets = built(pg, "SPOTS (no spots yet)")
    K.check(is_scroll(apps, "SkyyXaRows") and "#SkyyXaEmpty.Text" in sets and "#SkyyXaSort" in " ".join(mk for _p, mk in apps),
            "SPOTS empty: the scroll list with the empty text, the order toggle in the head")
    K.check(str(sets.get("#SkyyXaHint.Text", "")).startswith("Changes save at once to ") and any(s_ == "#SkyyXaRefresh" for s_, _x in e),
            "SPOTS: the hint line, Refresh bound in the footer")
    # ---- Spots with rows (3 spots via the page)
    for nm in ("Old Well", "Hidden Grotto", "Sky Pillar"):
        click(E, P, pg, "xadd", {"@XNName": nm, "@XNRad": "", "@XNXp": ""})
    K.eq(len(J("SpotReg").byWf(WF(wn)).spots), 3, "SPOTS: Add here x3 made 3 spots (%s)" % pg.msg)
    click(E, P, pg, "xedit0")
    c, e, apps, sets = built(pg, "SPOTS (3 spots, the newest selected)")
    k3 = SUI.grow_pick(3, LIST_IN, hs, gap=3)
    K.eq(hgt(apps, "SkyyXaRow0"), hs[k3], "SPOTS GROW: 3 rows at %d px (= grow_pick)" % hs[k3])
    K.eq([sets.get("#SkyyXaRowN%d.Text" % i) for i in range(3)], ["Sky Pillar", "Hidden Grotto", "Old Well"], "SPOTS: newest first")
    K.check("#SkyyXaRowE0.Text" in sets and "#SkyyXaEdit1" in [s_ for s_, _x in e], "SPOTS: the selected row says Editing, the others have Edit")
    K.check("#SkyyXaEName" in " ".join(mk for _p, mk in apps) and "#SkyyXaRen" in [s_ for s_, _x in e], "SPOTS: the editor (Rename ...) in-page on the right")
    click(E, P, pg, "xedit1")
    click(E, P, pg, "xrm")
    c, e, apps, sets = built(pg, "SPOTS (Sure - Remove)")
    K.check('Text: "Sure - Remove"' in " ".join(mk for _p, mk in apps), "SPOTS: the second-click confirm shows Sure - Remove")
    cur = click(E, P, pg, "xsort")
    c, e, apps, sets = built(pg, "SPOTS (order - nearest)")
    K.check('Text: "Order - nearest"' in " ".join(mk for _p, mk in apps), "SPOTS: xsort flips the order toggle")
    for a in ("xprev", "xnext"):
        sel0 = str(pg.selSpot)
        cur = click(E, P, pg, a)
        K.check(E.same(cur, pg) and str(pg.selSpot) == sel0, "SPOTS: the old pager click %s only answers" % a)
    # ---- Checklist: none selected, a custom entry, a spot entry; 230 entries -> 200 + Show 200 more
    cur = click(E, P, pg, "xtab1")
    click(E, P, pg, "xccustom", {"@XCText": "Ring the old bell"})
    click(E, P, pg, "xccount", {"@XCNum": "3"})
    pg2 = opn(1)
    c, e, apps, sets = built(pg2, "CHECKLIST (none selected)")
    K.check(is_scroll(apps, "SkyyXaRows") and sets.get("#SkyyXaCSelH.Text") == "Click Edit on an entry", "CHECKLIST: the scroll list, 'Click Edit on an entry'")
    ids = [str(x) for x in pg2.rowIds]
    ie = [i for i, x in enumerate(ids) if not x.startswith("s")]
    isp = [i for i, x in enumerate(ids) if x.startswith("s")]
    click(E, P, pg2, "xcedit%d" % ie[0])
    c, e, apps, sets = built(pg2, "CHECKLIST (a custom entry selected)")
    K.check("#SkyyXaCTick" in [s_ for s_, _x in e] and "#SkyyXaCUntick" in [s_ for s_, _x in e], "CHECKLIST: a custom entry has Tick / Untick")
    click(E, P, pg2, "xcedit%d" % isp[0])
    c, e, apps, sets = built(pg2, "CHECKLIST (a spot entry selected)")
    K.check("#SkyyXaCOff" in [s_ for s_, _x in e], "CHECKLIST: a spot entry has Take off the checklist")
    for i in range(228):
        J("ExAdminOps").ckAddCustom(P.pr, P.ref, P.st, P.st.getExternalData().getWorld(), JString("Task number %d" % i))
    pg2 = opn(1)
    c, e, apps, sets = built(pg2, "CHECKLIST (230+ entries)")
    nrow = len([1 for _p, mk in apps if re.match(r"Group #SkyyXaCRow\d+ ", mk)])
    ntot = len(J("SpotReg").byWf(WF(wn)).entries) + sum(1 for s_ in J("SpotReg").byWf(WF(wn)).spots if s_.check)
    K.check(nrow == 200 and "#SkyyXaMore" in [s_ for s_, _x in e] and hgt(apps, "SkyyXaCRow0") == 66,
            "CHECKLIST: %d entries = 200 rows of 66 px + 'Show 200 more' (%d rows)" % (ntot, nrow))
    click(E, P, pg2, "xmore")
    c, e, apps, sets = built(pg2, "CHECKLIST (Show 200 more)")
    nrow = len([1 for _p, mk in apps if re.match(r"Group #SkyyXaCRow\d+ ", mk)])
    K.check(nrow == ntot and "#SkyyXaMore" not in [s_ for s_, _x in e] and len(pg2.rowIds) == ntot, "CHECKLIST: Show 200 more shows all %d rows (%d)" % (ntot, nrow))
    click(E, P, pg2, "xcedit%d" % (ntot - 1))
    K.check(pg2.selEntry is not None and str(pg2.selEntry) == ids_last(pg2), "CHECKLIST: Edit on row %d (past the first 200) selects it" % (ntot - 1))
    # ---- Island
    pg3 = opn(2)
    c, e, apps, sets = built(pg3, "ISLAND")
    K.check(is_scroll(apps, "SkyyXaPl") and str(sets.get("#SkyyXaIP0.Text", "")).startswith("Xa") and "#SkyyXaISaveName" in [s_ for s_, _x in e],
            "ISLAND: the player lines in a scroll list (%s), the island editor" % sets.get("#SkyyXaIP0.Text"))
    # ---- a world that never pays exploration
    cfg = J("ExpCfg")
    old_ex = cfg.EX_WORLDS
    cfg.EX_WORLDS = JArray(JString)([wn])
    for t, nm in ((0, "EXCLUDED WORLD (Spots)"), (2, "EXCLUDED WORLD (Island, the switches)")):
        pgx = opn(t)
        c, e, apps, sets = built(pgx, nm)
        K.check("#SkyyXaExT.Text" in sets and (t != 2 or "#SkyyXaISpots" in [s_ for s_, _x in e]), "%s: the never-pays text%s" % (nm, " + the switches" if t == 2 else ""))
    cfg.EX_WORLDS = old_ex
    # ---- the kit clicks (also for a player who lost the permission)
    pg = opn(0)
    E.CM.lines.clear()
    cur = click(E, P, pg, "hub:h:home")
    K.check("skymenu" in [str(x) for x in E.CM.lines], "CLICK row 1 Home runs /skymenu (%s)" % list(E.CM.lines))
    pg = opn(0)
    E.CM.lines.clear()
    cur = click(E, P, pg, "hub:setup")
    K.check("modconfig" in [str(x) for x in E.CM.lines] or not E.same(cur, pg), "CLICK row 2 Server Setup opens Server Setup (%s)" % list(E.CM.lines))
    pg = opn(0)
    cur = click(E, P, pg, "hub:nosuchtab")
    K.check(E.same(cur, pg) and str(pg.msg) == FAIL_TEXT, "CLICK a missing tab says so on the result line (%s)" % pg.msg)
    E.USERS[UUID0] = []
    K.check(not bool(J("ExAdminOps").perm(P.pr)), "the admin lost %s" % PERM)
    cur = click(E, P, pg, "xtab1")
    K.check(str(pg.msg).startswith("-You are no longer an admin"), "a click without the permission is refused (%s)" % pg.msg)
    cur = click(E, P, pg, "hub:close")
    K.check(cur is None, "CLICK the X closes the page - also without the permission")
    E.USERS[UUID0] = [PERM]
    # ---- CALLS
    from perfworld_kit import calls
    g = calls(jar)
    K.check(PKG + "HubBar.page17" in g.get("AdminPage.build", set()) and PKG + "HubBar.subTab" in g.get("AdminPage.build", set()), "CALLS: AdminPage.build -> HubBar.page17 + subTab")
    K.check(all(PKG + "HubBar.growSize" in g.get(m, set()) for m in ("AdminPage.spotsTab", "AdminPage.checkTab")), "CALLS: spotsTab / checkTab -> HubBar.growSize")
    K.check(PKG + "HubBar.route" in g.get("AdminPage.hubClick", set()) and PKG + "AdminPage.hubClick" in g.get("AdminPage.handleDataEvent", set()),
            "CALLS: AdminPage.handleDataEvent asks hubClick (HubBar.route) first")
    K.check(PKG + "AdminPage.<init>" in " ".join(" ".join(v) for k, v in g.items() if "Cmd" in k or "Admin" in k), "CALLS: /exploreadmin still opens the AdminPage")
    HB.removeAll()
    K.save()


def ids_last(pg):
    return str(pg.rowIds[len(pg.rowIds) - 1])


if __name__ == "__main__":
    HK.run(name="SkyyExploration", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("admin", run_admin), ("savesold", run_saves_old), ("saves", run_saves), ("pages", T13.run_pages), ("names", T12.run_names),
                   ("cap", T12.run_cap), ("exec", T13.run_exec), ("live", T28.run_live)],
           script=__file__, live=(T13.LIVE, "Skyy_SkyyExploration"))
