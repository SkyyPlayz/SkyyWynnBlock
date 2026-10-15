"""SkyyClasses 0.1.27 - harness for HUBS H3a (the Character hub's Class tab: /class + its Abilities page in the Sky Window hub shell;
tools/classes_0_1_27_patch.py). Build first: python tools/classes_0_1_27_patch.py && python SkyyClasses/build_skyyclasses_0.1.27.py

    python SkyyClasses/test_skyyclasses_0.1.27.py [--dir <empty folder inside tools/dev/scratch/>] [--keep] [--no-old]

Every JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in scratch. Live save data is only READ / copied.
  OLD  the WHOLE 0.1.26 harness (test_skyyclasses_0.1.26.py: its OLD 0.1.19 L + START TWICE on a scratch COPY of the live
       Skyy_SkyyClasses, the huge X exec phase X1-X70 on the engine stand-ins, the config write proof CW, the audit) on the 0.1.27 jar. Its
       compare is 0.1.25 -> 0.1.26 (ours: C below), so its C lines that name the 0.1.27 classes are expected to differ (EXPECTED_OLD,
       each with its reason); any other failure fails this harness.
  A    verify   every class loads + initialises with -Xverify:all (tools/harness_kit.py)
  C    compare  0.1.26 -> 0.1.27: + HubBar, ClassHubOpen; ClassPage + AbilPage build / handleDataEvent, the plugin's setup / shutdown, the
                inlined version in CfgFn / CfgRows / KitMigrate; non-class entries: manifest.json + the 59 Sky Window kit files
  HUB  EXECUTED (tools/hub_tab_kit.py: the SkyyMenu 0.3.19 harness's engine stand-ins, the REAL PageManager, -Xverify:all):
       REG   ClassHubOpen.register() = hub:tab:character:class {"SkyyClasses", "Class", 40, "class", ClassHubOpen, null} (the contract
             row SUI.HUB_TABS); unregister() removes it, never another jar's array; setup / shutdown call them (bytecode)
       OPEN  the open Function: not a UUID / an offline player = FALSE; a player = TRUE and /class is the open page; openOn
       PAGE  the class page (no class yet, then a Mage: the Abilities button) and the Abilities page built into REAL builders and checked
             as hub pages (hub_tab_kit.page_check: Sky Window shell, <= 1080p, every contract tab fits, the body content under the strip,
             one tab per visible tab, Class selected, bindings, every set / binding names an element); the class page = 1114 x 980 with
             the 8 cards in a SCROLLING list well (740 high, cards 12 px narrower); the Abilities page = 1114 x 728
       CLICK the bar on both pages: the Class tab on the class page clears a pending pick (the page stays), on the Abilities page = the
             class page; another tab through its Function / the command fallback; a hidden / missing tab = the page stays and says so;
             < Menu with / without SkyyMenu; the X closes; the pages' own buttons still work after the bar (pick, Abilities, Close)
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

VERSION = "0.1.27"
PKG = "com.skyy.classes."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyClasses-0.1.26.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "hubsH3a", "cls")))
ADDED = ["HubBar", "ClassHubOpen"]
EXPECT = {"ClassPage": ["~m build", "~m handleDataEvent"], "AbilPage": ["~m build", "~m handleDataEvent"],
          "SkyyClassesPlugin": ["~m setup", "~m shutdown"],
          "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "KitMigrate": ["~m runOnce"]}      # the inlined version constant only (the kit flag file text)
if HK.arg("--phase") == "compare":
    HT.allow_kit_entries()
FAIL_TEXT = "That tab could not open right now - try again."
# the 0.1.26 harness's checks that pin the 0.1.26 identity (prefix of the FAIL line) - expected on 0.1.27, with why
EXPECTED_OLD = [
    ("compare: C: the new class = AbilMigFn (class:fn:migInfo): got ['com.skyy.classes.AbilMigFn', 'com.skyy.classes.ClassHubOpen', 'com.skyy.classes.HubBar']",
     "its compare is 0.1.25 -> 0.1.26: + HubBar, ClassHubOpen (0.1.27; ours: phase C)"),
    ("compare: C: only the planned classes change (unplanned: ['ClassPage'])", "0.1.27 changes ClassPage (the hub shell; ours: phase C)"),
    ("compare: C: the config kit's classes are byte-code identical but for the version string (no settings row changed): {'CfgFn': ['opExport(",
     "it allows the 0.1.26 version text only - 0.1.27's differs in the version constant alone (checked: the constant pools of CfgFn / CfgRows / KitMigrate 0.1.26 vs 0.1.27 differ only in '0.1.26' -> '0.1.27')"),
    ("compare: C: no non-class entry added or removed: got ['Common/UI/Custom/SkyyKit/", "+ the 59 Sky Window kit files (ours: phase C + the build's check_jar_kit)"),
    ("compare: C: manifest IncludesAssetPack + version 0.1.27", "it pins version 0.1.26"),
]


def run_hub(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    P_ = lambda n: JClass(PKG + n)
    Cfg, Store, AS, Defs, HO, HB = P_("ClassCfg"), P_("ClassStore"), P_("AbilStore"), P_("ClassDefs"), P_("ClassHubOpen"), P_("HubBar")
    base = os.path.join(scratch, "hub-mods", "Skyy_SkyyClasses")
    os.makedirs(base, exist_ok=True)
    Cfg.FILE = E.Paths.get(base, "config.properties")
    Store.DIR = E.Paths.get(base, "players")
    AS.DIR = E.Paths.get(base, "abilities")
    P = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-0000000000d7"), "ClassHub")
    u = P.pr.getUuid()
    K.check(E.same(HB.map(), E.bridge), "the kit HubBar and the harness share ONE bridge map (skyy.bridge)")
    # ---------------------------------------------------------------- REG
    K.eq(str(HO.register()), "character:class", "REG: register() answers the tab it put")
    HT.reg_check(K, E, "character", "class", "SkyyClasses", "Class", 40, "class", PKG + "ClassHubOpen")
    K.eq(int(HO.unregister()), 1, "REG: unregister() removes our 1 key")
    K.check(E.bridge.get("hub:tab:character:class") is None, "REG: the tab is gone after unregister()")
    HO.register()
    other = JClass("java.lang.Object")()
    E.bridge.put("hub:tab:character:class", other)
    K.eq(int(HO.unregister()), 0, "REG: unregister() leaves another jar's value under the same key")
    K.check(E.same(E.bridge.get("hub:tab:character:class"), other), "REG: ... and it is still there")
    E.bridge.remove("hub:tab:character:class")
    HO.register()
    g = PW.calls(jar)
    K.check(PKG + "ClassHubOpen.register" in g.get("SkyyClassesPlugin.setup", set()), "REG: setup() calls ClassHubOpen.register (bytecode)")
    K.check(PKG + "ClassHubOpen.unregister" in g.get("SkyyClassesPlugin.shutdown", set()), "REG: shutdown() calls ClassHubOpen.unregister (bytecode)")
    for pc in ("ClassPage", "AbilPage"):
        K.check(PKG + "HubBar.handle" in g.get(pc + ".handleDataEvent", set()) and PKG + "HubBar.build" in g.get(pc + ".build", set()),
                "REG: %s's build() draws the bar, handleDataEvent asks HubBar.handle (bytecode)" % pc)
    K.check(PKG + "ClassHubOpen.openOn" in g.get("AbilPage.handleDataEvent", set()), "REG: the Abilities page's Class tab goes through ClassHubOpen.openOn")
    # ---------------------------------------------------------------- OPEN
    fn = HO()
    K.check(fn.apply("not a uuid") == E.FALSE and fn.apply(E.UUID.randomUUID()) == E.FALSE, "OPEN: not a UUID / an offline player = FALSE")
    K.check(not bool(HO.openOn(None, P.ref, P.st)) and not bool(HO.openOn(P.pr, None, P.st)), "OPEN: openOn without a player / ref = false")

    def cls_page():
        r = fn.apply(u)
        E.pump(P)
        pg = E.pg(P)
        return pg if (r == E.TRUE and pg is not None and str(pg.getClass().getName()) == PKG + "ClassPage") else None
    pg = cls_page()
    K.check(pg is not None and int(HO.OPENED) >= 1, "OPEN: a player = TRUE, the /class page is open")
    # ---------------------------------------------------------------- PAGE: the class page (no class), then a Mage + the Abilities page
    built = HT.build(pg, P)
    w, h, sets, evs = HT.page_check(K, E, P, built, "SkyyClsF", "character", "class", "Class", "PAGE class (no class yet)", idp="SkyyCls")
    K.eq((w, h), (1114, 980), "PAGE class: the window 1114 x 980 (0.1.26's 1100 x 950 + the strip + the sky padding would be 1016: capped)")
    lst = [t for ty, s_, t, d in built[0] if t and "#SkyyClsList " in t]
    K.check(len(lst) == 1 and "LayoutMode: TopScrolling" in lst[0] and "Height: 740" in lst[0] and "ScrollbarStyle" in lst[0],
            "PAGE class: the card list is a SCROLLING well 740 high (%s)" % (lst[0][:160] if lst else None))
    cards = [t for ty, s_, t, d in built[0] if t and re.match(r"Group #SkyyClsCard\d+ ", t)]
    K.check(len(cards) == len(list(Defs.NAMES)) == 8 and all("Height: 92" in c for c in cards), "PAGE class: 8 class cards, 92 high (%d)" % len(cards))
    picks = [s_ for s_, _t in evs if s_ and s_.startswith("#SkyyClsPick")]
    K.check(len(picks) >= 6, "PAGE class: the Choose buttons are bound (%d)" % len(picks))
    mage = [str(x) for x in Defs.NAMES].index("Mage")
    pg.handleDataEvent(P.ref, P.st, '{"a":"clspick%d"}' % mage)
    E.pump(P)
    K.check(int(pg.pending) == mage, "PAGE the page's own click still works: a pick waits for Confirm")
    pg.handleDataEvent(P.ref, P.st, '{"a":"clsyes"}')
    E.pump(P)
    K.check(int(Store.classIndex(u)) == mage, "PAGE ... Confirm: the player is a Mage (%s)" % pg.info)
    built = HT.build(pg, P)
    HT.page_check(K, E, P, built, "SkyyClsF", "character", "class", "Class", "PAGE class (a Mage)", idp="SkyyCls")
    K.check("#SkyyClsAbil" in [s_ for s_, _t in built[1]], "PAGE class (a Mage): the Abilities button is bound")
    pg.handleDataEvent(P.ref, P.st, '{"a":"clsabil"}')
    E.pump(P)
    ab = E.pg(P)
    K.check(ab is not None and str(ab.getClass().getName()) == PKG + "AbilPage", "PAGE the Abilities button opens the Abilities page")
    if ab is not None:
        w2, h2, sets2, evs2 = HT.page_check(K, E, P, HT.build(ab, P), "SkyyAbF", "character", "class", "Class", "PAGE abilities", idp="SkyyAb")
        K.eq((w2, h2), (1114, 728), "PAGE abilities: the window 1114 x 728 (0.1.26's 1100 x 662 + the strip + the sky padding)")
        K.check(len([s_ for s_, _t in evs2 if s_ and s_.startswith("#SkyyAbMove")]) >= 1, "PAGE abilities: the card buttons are bound")
    # ---------------------------------------------------------------- CLICK
    fakes = HT.Fakes(E, "character")

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
    p_ = abil_page()
    n0 = len(E.sent(P))
    p_.handleDataEvent(None, None, '{"a":"hub:class"}')     # the class page cannot open (no store): the Abilities page says so
    E.pump(P)
    K.check(E.same(E.pg(P), p_) and str(p_.info) == "The class page could not open right now - try /class." and len(E.sent(P)) > n0,
            "CLICK abilities: the Class tab when the class page cannot open -> the page stays, says so, redraws (%s)" % p_.info)
    p_ = cls_page()
    p_.handleDataEvent(P.ref, P.st, '{"a":"clsclose"}')
    E.pump(P)
    K.check(E.pg(P) is None, "CLICK the class page's own Close still closes")
    p_ = abil_page()
    p_.handleDataEvent(P.ref, P.st, '{"a":"abclose"}')
    E.pump(P)
    K.check(E.pg(P) is None, "CLICK the Abilities page's own Close still closes")
    fakes.remove()
    K.save()


def run_old():
    sc = os.path.join(os.path.dirname(SCRATCH), "cls-old")
    p = subprocess.run([sys.executable, os.path.join(HERE, "test_skyyclasses_0.1.26.py"), "--jar", JAR, "--dir", sc],
                       env=dict(os.environ), capture_output=True, text=True, encoding="utf-8", errors="replace")
    open(os.path.join(os.path.dirname(SCRATCH), "cls-old.log"), "w", encoding="utf-8").write(p.stdout + "\n" + p.stderr)
    lines = p.stdout.splitlines()
    oks = [l for l in lines if l.endswith("fail(s)") and " ok, " in l]
    failed = [l.strip()[len("FAIL: "):] for l in lines if l.strip().startswith("FAIL: ")]
    exp, bad = [], []
    for f in failed:
        (exp if [e for e in EXPECTED_OLD if f.startswith(e[0])] else bad).append(f)
    return oks, bad, exp, p.returncode


if __name__ == "__main__":
    if "--phase" not in sys.argv and "--no-old" not in sys.argv:
        oks, bad, exp, rc = run_old()
        print("OLD. the 0.1.26 harness on the 0.1.27 jar: %s; %d expected identity checks differ, %d other failure(s)" % (oks[-1:] or "no summary", len(exp), len(bad)))
        for e in exp:
            print("  note (old): expected on 0.1.27: %s" % e[:240])
        for b in bad:
            print("  OLD unexpected: %s" % b[:400])
        HK.check(bool(oks), "OLD: the 0.1.26 harness ran to its summary")
        HK.check(not bad, "OLD: no failure outside the listed identity checks: %s" % bad[:5])
    HK.run(name="SkyyClasses", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("hub", run_hub)], script=__file__)
