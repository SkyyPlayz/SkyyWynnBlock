"""Harness for SkyyProfiles 0.1.14 (HUBS H3a: the Character hub's Profiles tab, /profiles in the Sky Window hub shell;
tools/profiles_0_1_14_patch.py). Build first: python tools/profiles_0_1_14_patch.py && python SkyyProfiles/build_skyyprofiles_0.1.14.py

    python SkyyProfiles/test_skyyprofiles_0.1.14.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.1.13 -> 0.1.14: + HubBar, ProfHubOpen; ProfilePage buildList / buildCreate / handleDataEvent, the plugin's setup /
                shutdown, the version texts only; non-class entries: manifest.json + the 59 Sky Window kit files
  HUB  EXECUTED (tools/hub_tab_kit.py: the SkyyMenu 0.3.19 harness's engine stand-ins, the REAL PageManager, -Xverify:all):
       REG   ProfHubOpen.register() = hub:tab:character:profiles {"SkyyProfiles", "Profiles", 80, "profiles", ProfHubOpen, null} (the
             contract row SUI.HUB_TABS); unregister() removes it, never another jar's array; setup / shutdown call them (bytecode)
       OPEN  the open Function: not a UUID / an offline player = FALSE; a player with no profile = TRUE and the Create Profile view (first);
             a player with profiles = the list; an unreadable profile file = FALSE (LAST = the refusal; the bar then runs /profiles)
       PAGE  both views built into REAL builders and checked as hub pages (hub_tab_kit.page_check: Sky Window shell, 1114 x 980 <= 1080p,
             every contract tab fits, the body content under the strip, one tab per visible tab, Profiles selected, bindings, every set /
             binding names an element); the profile list well 710 high and the class list 614 high, both TopScrolling
       CLICK the bar: the Profiles tab on Create new (or a pending switch) = the list; with NO profile it stays on Create; another tab
             through its Function / the command fallback; a hidden / missing tab = the page stays and says so; < Menu with / without
             SkyyMenu; the X closes (a first-profile page reminds in chat as its Close does); the page's own clicks still work after the
             bar (Create new, Back, a switch question, Close)
  FIRST (review fix) a player with NO profile: with other Character tabs registered the Create view's bar still shows ONLY the
       Profiles tab (selected, bound to hub:profiles), the title is set to "Create your first profile", < Menu / X bound; < Menu runs
       /skymenu AND gives the first-profile reminder; with a profile the Create view draws the whole bar and keeps the hub title
  RB   test_skyyprofiles_0.1.13.py's rebirth-busy phase on the 0.1.14 jar
  X, D test_skyyprofiles_0.1.12.py's exec + live phases on the 0.1.14 jar (START TWICE on a scratch COPY of the live Skyy_SkyyProfiles)
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW
import hub_tab_kit as HT
import skyyui as SUI


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T12 = tmod("test_skyyprofiles_0.1.12.py", "tp0112")
T13 = tmod("test_skyyprofiles_0.1.13.py", "tp0113")

VERSION = "0.1.14"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyProfiles-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyProfiles-0.1.13.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "hubsH3a", "profiles")))
PKG = "com.skyy.profiles."
LIVE_DIR = T12.LIVE_DIR
EXPECT = {"ProfilePage": ["~m buildList", "~m buildCreate", "~m handleDataEvent"], "SkyyProfilesPlugin": ["~m setup", "~m shutdown"],
          "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "ProfCfg": ["~m capMigrate"], "ProfDel": ["~m archiveLocked"]}   # the version texts only (constant pools checked)
ADDED = ["HubBar", "ProfHubOpen"]
if HK.arg("--phase") == "compare":
    HT.allow_kit_entries()
FAIL_TEXT = "That tab could not open right now - try again."


def run_hub(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    P_ = lambda n: JClass(PKG + n)
    Cfg, S, Del, HO, HB = P_("ProfCfg"), P_("ProfStore"), P_("ProfDel"), P_("ProfHubOpen"), P_("HubBar")
    home = os.path.join(scratch, "hub-mods", "Skyy_SkyyProfiles")
    os.makedirs(os.path.join(home, "players"), exist_ok=True)
    Paths = E.Paths
    Cfg.FILE = Paths.get(home, "config.properties")
    S.DIR, S.SWDIR, S.INVDIR, S.LOGF = Paths.get(home, "players"), Paths.get(home, "switching"), Paths.get(home, "inventories"), Paths.get(home, "switches.log")
    Del.ARCDIR = Paths.get(home, "archive")
    P = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-0000000000e7"), "ProfHub")
    u = P.pr.getUuid()
    K.check(E.same(HB.map(), E.bridge), "the kit HubBar and the harness share ONE bridge map (skyy.bridge)")
    # ---------------------------------------------------------------- REG
    K.eq(str(HO.register()), "character:profiles", "REG: register() answers the tab it put")
    HT.reg_check(K, E, "character", "profiles", "SkyyProfiles", "Profiles", 80, "profiles", PKG + "ProfHubOpen")
    K.eq(int(HO.unregister()), 1, "REG: unregister() removes our 1 key")
    K.check(E.bridge.get("hub:tab:character:profiles") is None, "REG: the tab is gone after unregister()")
    HO.register()
    other = JClass("java.lang.Object")()
    E.bridge.put("hub:tab:character:profiles", other)
    K.eq(int(HO.unregister()), 0, "REG: unregister() leaves another jar's value under the same key")
    K.check(E.same(E.bridge.get("hub:tab:character:profiles"), other), "REG: ... and it is still there")
    E.bridge.remove("hub:tab:character:profiles")
    HO.register()
    g = PW.calls(jar)
    K.check(PKG + "ProfHubOpen.register" in g.get("SkyyProfilesPlugin.setup", set()), "REG: setup() calls ProfHubOpen.register (bytecode)")
    K.check(PKG + "ProfHubOpen.unregister" in g.get("SkyyProfilesPlugin.shutdown", set()), "REG: shutdown() calls ProfHubOpen.unregister (bytecode)")
    K.check(PKG + "HubBar.handle" in g.get("ProfilePage.handleDataEvent", set()) and PKG + "HubBar.build" in g.get("ProfilePage.buildList", set())
            and PKG + "HubBar.build" in g.get("ProfilePage.buildCreate", set()), "REG: both views draw the bar, handleDataEvent asks HubBar.handle (bytecode)")
    K.check(PKG + "ProfilePage.open" in g.get("ProfHubOpen.apply", set()), "REG: the open Function goes through ProfilePage.open (the command's open)")
    # ---------------------------------------------------------------- OPEN + PAGE (no profile -> Create)
    fn = HO()
    K.check(fn.apply("not a uuid") == E.FALSE and fn.apply(E.UUID.randomUUID()) == E.FALSE, "OPEN: not a UUID / an offline player = FALSE")

    def open_page():
        r = fn.apply(u)
        E.pump(P)
        pg = E.pg(P)
        return pg if (r == E.TRUE and pg is not None and str(pg.getClass().getName()) == PKG + "ProfilePage") else None
    pg = open_page()
    K.check(pg is not None and int(pg.view) == 1 and bool(pg.first), "OPEN: no profile yet = TRUE, the Create Profile view (first)")

    def lists(built):
        return [t for ty, s_, t, d in built[0] if t and "#SkyyPfList " in t]
    built = HT.build(pg, P)
    HT.page_check(K, E, P, built, "SkyyPfF", "character", "profiles", "Profiles", "PAGE create (first)", idp="SkyyPf")
    ls = lists(built)
    K.check(len(ls) == 1 and "TopScrolling" in ls[0] and "Height: 614" in ls[0], "PAGE create: the class list scrolls, 614 high (%s)" % (ls[0][:120] if ls else None))
    cur = HT.build(pg, P)
    pg.handleDataEvent(P.ref, P.st, '{"a":"hub:profiles"}')
    E.pump(P)
    K.check(E.same(E.pg(P), pg) and int(pg.view) == 1, "CLICK no profile: the Profiles tab stays on Create Profile")
    n0 = len(list(E.sent(P)))
    pg.handleDataEvent(P.ref, P.st, '{"a":"hub:close"}')
    E.pump(P)
    txt = E.strs_of(P, n0)
    K.check(E.pg(P) is None and "You have no profile yet" in txt, "CLICK no profile: the X closes + the first-profile reminder in chat")
    # ---------------------------------------------------------------- FIRST (review fix: the forced first-profile page)
    def bar_of(built):
        cmds, evs = built
        tabs = [t for ty, s_, t, d in cmds if s_ == "#SkyyPfFHubTabs" and t and t.startswith("TextButton")]
        titles = [str(d) for ty, s_, t, d in cmds if ty == "Set" and s_ == "#SkyyPfFTitle.Text"]
        return tabs, titles, evs
    fk = HT.Fakes(E, "character")
    vis = HT.hub_tabs(E, "character", u)
    K.eq(sorted(vis), ["fnno", "fnok", "profiles"], "FIRST: 3 Character tabs are registered and visible")
    pg = open_page()
    K.check(pg is not None and bool(pg.first) and int(pg.view) == 1, "FIRST: no profile = the Create view (first)")
    tabs, titles, evs = bar_of(HT.build(pg, P))
    K.check(len(tabs) == 1 and "#SkyyPfFHubT0 " in tabs[0] and "Tab_Selected" in tabs[0] and 'Text: "Profiles"' in tabs[0],
            "FIRST: the bar shows ONLY the Profiles tab, selected (%s)" % [t[:60] for t in tabs])
    tw = SUI.hub_tab_width(1114 - 2 * SUI.THEME_PAD["sky"], 1)
    K.check(bool(tabs) and ("Width: %d, Height: 44" % tw) in tabs[0], "FIRST: the one tab is the kit's full-strip tab (%d px)" % tw)
    K.check(len(titles) == 1 and "Create your first profile" in titles[0], "FIRST: the title says Create your first profile (%s)" % titles)
    bound = [(s_, t) for s_, t in evs if s_ and s_.startswith("#SkyyPfFHub")]
    K.check(sorted(s_ for s_, _t in bound) == ["#SkyyPfFHubClose", "#SkyyPfFHubMenu", "#SkyyPfFHubT0"]
            and all(w in t for s_, t in bound for k, w in (("#SkyyPfFHubT0", "hub:profiles"), ("#SkyyPfFHubMenu", "hub:back"),
                                                         ("#SkyyPfFHubClose", "hub:close")) if s_ == k),
            "FIRST: bound = the Profiles tab (hub:profiles), < Menu (hub:back), the X (hub:close) - no other tab (%s)" % [s_ for s_, _t in bound])
    pg.handleDataEvent(P.ref, P.st, '{"a":"hub:profiles"}')
    E.pump(P)
    K.check(E.same(E.pg(P), pg) and int(pg.view) == 1 and bool(pg.first), "FIRST: the Profiles tab keeps the Create view")
    E.bridge.put("config:def:SkyyMenu", "stand-in")
    E.CM.lines.clear()
    n0 = len(list(E.sent(P)))
    pg.handleDataEvent(P.ref, P.st, '{"a":"hub:back"}')
    E.pump(P)
    txt = E.strs_of(P, n0)
    K.check([str(x) for x in E.CM.lines] == ["skymenu"] and "You have no profile yet" in txt,
            "FIRST: < Menu runs /skymenu + the first-profile reminder (%s)" % list(E.CM.lines))
    E.bridge.remove("config:def:SkyyMenu")
    E.CM.lines.clear()
    P2 = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-0000000000e8"), "ProfHub2")     # another player WITH a profile
    S.create(P2.pr.getUuid(), "1", "Fig", "Priest", True)
    K.check(fn.apply(P2.pr.getUuid()) == E.TRUE, "FIRST: the open Function opens a player with a profile")
    E.pump(P2)
    pg2 = E.pg(P2)
    pg2.handleDataEvent(P2.ref, P2.st, '{"a":"pfnew"}')
    E.pump(P2)
    tabs, titles, _evs = bar_of(HT.build(pg2, P2))
    K.check(int(pg2.view) == 1 and not bool(pg2.first) and len(tabs) == 3 and not titles,
            "FIRST: with a profile the Create view draws the whole bar (3 tabs) and keeps the hub title (%d tabs, %s)" % (len(tabs), titles))
    fk.remove()
    # ---------------------------------------------------------------- profiles -> the list
    S.create(u, "1", "Banana", "Priest", True)
    S.create(u, "2", "Kiwi", "Mage", False)
    pg = open_page()
    K.check(pg is not None and int(pg.view) == 0, "OPEN: a player with profiles = the profile list")
    built = HT.build(pg, P)
    HT.page_check(K, E, P, built, "SkyyPfF", "character", "profiles", "Profiles", "PAGE list", idp="SkyyPf")
    ls = lists(built)
    K.check(len(ls) == 1 and "TopScrolling" in ls[0] and "Height: 710" in ls[0], "PAGE list: the profile list scrolls, 710 high (%s)" % (ls[0][:120] if ls else None))
    K.check(any("Priest Banana - ACTIVE" in (t or "") + (d or "") for ty, s_, t, d in built[0]), "PAGE list: the active profile card")
    pg.handleDataEvent(P.ref, P.st, '{"a":"pfnew"}')
    E.pump(P)
    K.check(E.same(E.pg(P), pg) and int(pg.view) == 1 and not bool(pg.first), "PAGE the page's own click still works: Create new (view 1)")
    HT.page_check(K, E, P, HT.build(pg, P), "SkyyPfF", "character", "profiles", "Profiles", "PAGE create (new)", idp="SkyyPf")
    pg.handleDataEvent(P.ref, P.st, '{"a":"pfback"}')
    E.pump(P)
    K.check(int(pg.view) == 0, "PAGE Back = the list")
    # ---------------------------------------------------------------- CLICK
    fakes = HT.Fakes(E, "character")

    def open_new():
        p_ = open_page()
        p_.handleDataEvent(P.ref, P.st, '{"a":"pfnew"}')
        E.pump(P)
        return p_
    HT.clicks(K, E, P, open_new, "character", "profiles", "CLICK create new", fakes,
              self_check=lambda p_: int(p_.view) == 0 and str(p_.info) == "", fail_text=FAIL_TEXT)

    def open_ask():
        p_ = open_page()
        p_.handleDataEvent(P.ref, P.st, '{"a":"pfsw2"}')
        E.pump(P)
        return p_
    p_ = open_ask()
    K.check(str(p_.pending) == "2", "CLICK a switch question is open (pending 2)")
    p_.handleDataEvent(P.ref, P.st, '{"a":"hub:profiles"}')
    E.pump(P)
    K.check(p_.pending is None and int(p_.view) == 0, "CLICK the Profiles tab clears a pending switch question")
    p_ = open_page()
    p_.handleDataEvent(P.ref, P.st, '{"a":"pfclose"}')
    E.pump(P)
    K.check(E.pg(P) is None, "CLICK the page's own Close still closes")
    # an unreadable profile file: the open Function refuses (LAST = the text), the bar then runs /profiles
    S.BROKEN.put(u, "x")
    K.check(fn.apply(u) == E.FALSE and "could not be read" in str(HO.LAST), "OPEN: an unreadable profile file = FALSE (%s)" % HO.LAST)
    S.BROKEN.remove(u)
    fakes.remove()
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyProfiles", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("hub", run_hub), ("rb", T13.run_rb), ("exec", T12.run_exec), ("live", T12.run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyProfiles"))
