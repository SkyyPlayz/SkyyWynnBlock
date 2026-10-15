"""SkyySkills 0.4.41 - harness for HUBS H3a (the Character hub's Skills tab: /skills, a skill's Stats page and the Overall page in the Sky
Window hub shell; tools/skills_0_4_41_patch.py).
Build first: python tools/skills_0_4_41_patch.py && python SkyySkills/build_skyyskills_0.4.41.py
             (+ the jars the inherited 0.4.40 phases read: SkyyTrees/SkyyTrees-0.3.11.jar, SkyyRebirth/SkyyRebirth-0.3.3.jar - read only)

    python SkyySkills/test_skyyskills_0.4.41.py [--dir <empty folder inside tools/dev/scratch/>] [--keep] [--no-old]

Phases (each a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.4.40 -> 0.4.41: + HubBar, SkillsHubOpen; SkillsPage / StatsPage / OverallPage build + handleDataEvent, the plugin's setup /
               shutdown, the version texts only; non-class entries: manifest.json + the 59 Sky Window kit files
  HUB EXECUTED (tools/hub_tab_kit.py: the SkyyMenu 0.3.19 harness's engine stand-ins, the REAL PageManager, -Xverify:all):
      REG   SkillsHubOpen.register() = hub:tab:character:skills {"SkyySkills", "Skills", 20, "skills", SkillsHubOpen, null} (the contract
            row SUI.HUB_TABS); unregister() removes it, never another jar's array; setup / shutdown call them (bytecode)
      OPEN  the open Function: not a UUID / an offline player = FALSE; a player = TRUE and /skills is the open page
      PAGE  /skills (974 x 980: the 12 skill rows in a SCROLLING well 749 high, rows 906 wide), the Top 10 view, a skill's Stats page
            (974 x 914) and the Overall page (974 x 755) built into REAL builders and checked as hub pages (hub_tab_kit.page_check:
            Sky Window shell, <= 1080p, every contract tab fits, the body content under the strip, one tab per visible tab, Skills
            selected, bindings, every set / binding names an element); each reached through the pages' OWN buttons (STATS, TOP 10,
            OVERALL)
      CLICK the bar on all three pages: the Skills tab = the skill list (Top 10 view -> the list in place; Stats / Overall -> /skills);
            another tab through its Function / the command fallback; a hidden / missing tab = the page stays and says so (one chat line);
            < Menu with / without SkyyMenu; the X closes
  0.4.40's phases on the 0.4.41 jar (G40 with the real SkyyTrees tree names + the REAL SkillsPage / StatsPage builds, G39, G38, F fakes,
      G37, R3, RS, RB, D live = 0.4.38's livemig: START TWICE on a scratch COPY of the live Skyy_SkyySkills with every one-time update in
      setup() order) - the checks pinning 0.4.40's version text or the 0.4.40 page window are expected to differ (EXPECTED41 below, each
      with its reason; HUB re-checks the pages). Its route / exec / old live chains need the tidied 0.4.31 / 0.4.33 jars (they fail on
      the 0.4.40 jar the same way) and are left out.
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW
import hub_tab_kit as HT

VERSION = "0.4.41"
PKG = "com.skyy.skills."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.40.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "hubsH3a", "sk")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyySkills")
os.environ.setdefault("SKYYROUTE_SESSION", os.path.join(SCRATCH, "routesession"))
EXPECT = {
    "SkillsPage": ["~m build", "~m handleDataEvent"], "StatsPage": ["~m build", "~m handleDataEvent"],
    "OverallPage": ["~m build", "~m handleDataEvent"], "SkyySkillsPlugin": ["~m setup", "~m shutdown"],
    # version texts (filled from C, each checked: only the version constant differs)
    "SkillCfg": ["~m load"], "ManaGuard": ["~m armReport2", "~m intReport", "~m packReport"], "CfgRows": ["~<clinit>", "~m header"],
    "CfgFn": ["~m opExport"],
}
ADDED = ["HubBar", "SkillsHubOpen"]
if HK.arg("--phase") == "compare":
    HT.allow_kit_entries()
FAIL_TEXT = "That tab could not open right now - try again."


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T40 = tmod("test_skyyskills_0.4.40.py", "t0440")
T39, T38 = T40.T39, T40.T38


def run_hub(out, jar, scratch, _home):
    from jpype import JClass, JArray, JLong
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    J = lambda n: JClass(PKG + n)
    Cfg, Sto, Defs, HO, HB = J("SkillCfg"), J("SkillStore"), J("SkillDefs"), J("SkillsHubOpen"), J("HubBar")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    P = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-0000000000f7"), "SkillHub")
    u = P.pr.getUuid()
    N = int(Defs.N)
    dd = [0] * (2 * N)
    for sl in (0, 1, 2, 4):
        dd[sl] = 4000
    Sto.DATA.put(str(u), JArray(JLong)(dd))
    K.check(E.same(HB.map(), E.bridge), "the kit HubBar and the harness share ONE bridge map (skyy.bridge)")
    # ---------------------------------------------------------------- REG
    K.eq(str(HO.register()), "character:skills", "REG: register() answers the tab it put")
    HT.reg_check(K, E, "character", "skills", "SkyySkills", "Skills", 20, "skills", PKG + "SkillsHubOpen")
    K.eq(int(HO.unregister()), 1, "REG: unregister() removes our 1 key")
    K.check(E.bridge.get("hub:tab:character:skills") is None, "REG: the tab is gone after unregister()")
    HO.register()
    other = JClass("java.lang.Object")()
    E.bridge.put("hub:tab:character:skills", other)
    K.eq(int(HO.unregister()), 0, "REG: unregister() leaves another jar's value under the same key")
    K.check(E.same(E.bridge.get("hub:tab:character:skills"), other), "REG: ... and it is still there")
    E.bridge.remove("hub:tab:character:skills")
    HO.register()
    g = PW.calls(jar)
    K.check(PKG + "SkillsHubOpen.register" in g.get("SkyySkillsPlugin.setup", set()), "REG: setup() calls SkillsHubOpen.register (bytecode)")
    K.check(PKG + "SkillsHubOpen.unregister" in g.get("SkyySkillsPlugin.shutdown", set()), "REG: shutdown() calls SkillsHubOpen.unregister (bytecode)")
    for pc in ("SkillsPage", "StatsPage", "OverallPage"):
        K.check(PKG + "HubBar.handle" in g.get(pc + ".handleDataEvent", set()) and PKG + "HubBar.build" in g.get(pc + ".build", set()),
                "REG: %s's build() draws the bar, handleDataEvent asks HubBar.handle (bytecode)" % pc)
    # ---------------------------------------------------------------- OPEN
    fn = HO()
    K.check(fn.apply("not a uuid") == E.FALSE and fn.apply(E.UUID.randomUUID()) == E.FALSE, "OPEN: not a UUID / an offline player = FALSE")

    def open_page():
        r = fn.apply(u)
        E.pump(P)
        pg = E.pg(P)
        return pg if (r == E.TRUE and pg is not None and str(pg.getClass().getName()) == PKG + "SkillsPage") else None
    pg = open_page()
    K.check(pg is not None and int(pg.view) == -1 and int(HO.OPENED) >= 1, "OPEN: a player = TRUE, /skills (the skill list) is open")

    def click(p_, word):
        p_.handleDataEvent(P.ref, P.st, '{"a":"%s"}' % word)
        E.pump(P)
        return E.pg(P)
    # ---------------------------------------------------------------- PAGE /skills
    built = HT.build(pg, P)
    w, h, sets, evs = HT.page_check(K, E, P, built, "SkyySkF", "character", "skills", "Skills", "PAGE /skills", idp="SkyySk")
    K.eq((w, h), (974, 980), "PAGE /skills: 974 x 980 (0.4.40's 960 x 973 + the strip + the sky padding would be 1039: capped)")
    ls = [t for ty, s_, t, d in built[0] if t and "#SkyySkList " in t]
    K.check(len(ls) == 1 and "LayoutMode: TopScrolling" in ls[0] and "Height: 749" in ls[0] and "ScrollbarStyle" in ls[0],
            "PAGE /skills: the skill list is a SCROLLING well 749 high (%s)" % (ls[0][:140] if ls else None))
    rows = [t for ty, s_, t, d in built[0] if s_ == "#SkyySkList" and t and t.startswith("Group #SkyySkRow")]
    K.check(len(rows) == len(list(Defs.ROW_SLOTS)) == 12, "PAGE /skills: the 12 skill rows are in the list (%d)" % len(rows))
    panels = [t for ty, s_, t, d in built[0] if t and t.startswith("Group #SkyySkRow") and "P {" in t.split("Anchor")[0]]
    K.check(panels and all("Width: 810" in t or "Width: 714" in t for t in panels), "PAGE /skills: every row panel is 12 px narrower (810 / 714)")
    # the Stats page through the row's own STATS button, then TOP 10, the Overall page through OVERALL
    st = click(pg, "skstat0")
    K.check(st is not None and str(st.getClass().getName()) == PKG + "StatsPage", "PAGE the row's own STATS button opens the Stats page")
    if st is not None:
        w2, h2, sets2, ev2 = HT.page_check(K, E, P, HT.build(st, P), "SkyyStF", "character", "skills", "Skills", "PAGE stats", idp="SkyyS")
        K.eq((w2, h2), (974, 914), "PAGE stats: 974 x 914 (0.4.40's 960 x 848 + the strip + the sky padding)")
        K.check(any("Mining - level" in str(d) for s_, d in sets2.items() if s_ == "#SkyyStTitle.Text"), "PAGE stats: the skill name line in the body")
        top = click(st, "sttop")
        K.check(top is not None and str(top.getClass().getName()) == PKG + "SkillsPage" and int(top.view) == 0, "PAGE Stats' own TOP 10 opens the Top 10 view")
        if top is not None:
            w3, h3, sets3, ev3 = HT.page_check(K, E, P, HT.build(top, P), "SkyySkF", "character", "skills", "Skills", "PAGE top 10", idp="SkyySk")
            K.check("Character - Top 10 - Mining" in str(sets3.get("#SkyySkFTitle.Text")), "PAGE top 10: the hub title bar names the skill (%s)" % sets3.get("#SkyySkFTitle.Text"))
            tl = [t for ty, s_, t, d in HT.build(top, P)[0] if t and "#SkyySkTop " in t]
            K.check(len(tl) == 1 and "Height: 722" in tl[0] and "TopScrolling" not in tl[0], "PAGE top 10: the fixed list 722 high (10 rows)")
            cur = click(top, "hub:skills")
            K.check(E.same(cur, top) and int(top.view) == -1, "CLICK top 10: the Skills tab = the skill list, in place")
    pg = open_page()
    ov = click(pg, "skstatov")
    K.check(ov is not None and str(ov.getClass().getName()) == PKG + "OverallPage", "PAGE the OVERALL button opens the Overall page")
    if ov is not None:
        w4, h4, sets4, ev4 = HT.page_check(K, E, P, HT.build(ov, P), "SkyyOvPage", "character", "skills", "Skills", "PAGE overall", idp="SkyyOv")
        K.eq((w4, h4), (974, 755), "PAGE overall: 974 x 755 (0.4.40's 960 x 689 + the strip + the sky padding)")
    # ---------------------------------------------------------------- CLICK
    fakes = HT.Fakes(E, "character")

    def open_top():
        p_ = J("SkillsPage")(P.pr)
        p_.view = 0
        P.pm.openCustomPage(P.ref, P.st, p_)
        E.pump(P)
        return p_
    HT.clicks(K, E, P, open_top, "character", "skills", "CLICK /skills (top 10)", fakes, self_check=lambda p_: int(p_.view) == -1, fail_text=FAIL_TEXT)

    def open_stats():
        return click(open_page(), "skstat1")
    HT.clicks(K, E, P, open_stats, "character", "skills", "CLICK stats", fakes, fail_text=FAIL_TEXT,
              self_new=lambda cur: str(cur.getClass().getName()) == PKG + "SkillsPage" and int(cur.view) == -1)

    def open_ov():
        return click(open_page(), "skstatov")
    HT.clicks(K, E, P, open_ov, "character", "skills", "CLICK overall", fakes, fail_text=FAIL_TEXT,
              self_new=lambda cur: str(cur.getClass().getName()) == PKG + "SkillsPage")
    st = open_stats()
    K.check(str(click(st, "stback").getClass().getName()) == PKG + "SkillsPage", "CLICK Stats' own < Back still opens /skills")
    fakes.remove()
    Sto.DATA.remove(str(u))
    K.save()


# 0.4.40's phases on this jar: the checks that pin 0.4.40's version text / page window (prefix of the FAIL line) - with why
EXPECTED41 = [
    ("G config: the fresh xp.properties ends with the 0.4.39 block", "0.4.40 already listed it (version text)"),
    ("G page (trees True): TREE buttons only where SkyyTrees has a tree", "0.4.40 already listed it"),
    ("G page (trees False): the window is 960 x 973 (fits 1080)", "the hub window is 974 x 980 (HUB re-checks it: assert_hub_page, <= 1080p)"),
    ("G page (trees True): the window is 960 x 973 (fits 1080)", "the hub window is 974 x 980 (HUB re-checks it: assert_hub_page, <= 1080p)"),
]


def wrap41(fn):
    def run(out, jar, scratch, home):
        tmp = out + ".i41.json"
        fn(tmp, jar, scratch, home)
        d = json.load(open(tmp))
        K = HK.Child(out)
        K.ok, K.notes = d["ok"], d["notes"]
        for f in d["fails"]:
            hit = [e for e in EXPECTED41 if f.startswith(e[0])]
            if hit:
                K.ok += 1
                K.notes.append("expected in 0.4.41 (%s): %s" % (hit[0][1], f[:160]))
            else:
                K.fails.append(f)
        K.save()
    return run


# the inherited route / exec / live chains end in the 0.4.32 / 0.4.34 harnesses, which load the 0.4.31 / 0.4.33 jars as their controls -
# those jars were tidied away (tools/tidy_local.py), so those phases fail with ClassNotFoundException on the 0.4.40 jar too (checked
# 2026-10-15: test_skyyskills_0.4.40.py --phase route on SkyySkills-0.4.40.jar). They are left out; START TWICE on a scratch COPY of
# the live data runs through 0.4.38's livemig (every one-time update in setup() order, 0.4.37 vs this jar - both jars present).
OLD_PHASES = [("g40", T40.run_g40), ("g39", T40.wrap(T39.run_g39)), ("g38", T40.wrap(T39.wrap(T38.run_g38))), ("fake15", T38.run_fake15),
              ("fake25", T38.run_fake25), ("g37", T40.wrap(T39.wrap(T38.run_g37))), ("r3", T40.wrap(T39.wrap(T38.run_r3))),
              ("restart", T38.run_restart), ("r1", T38.run_r1), ("live", T38.run_livemig)]

if __name__ == "__main__":
    phases = [("hub", run_hub)]
    if "--no-old" not in sys.argv:
        phases += [(k, wrap41(f)) for k, f in OLD_PHASES]
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=phases, script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
