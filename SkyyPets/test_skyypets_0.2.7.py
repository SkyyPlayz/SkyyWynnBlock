"""Harness for SkyyPets 0.2.7 (HUBS H3a: the Character hub's Pets tab, /pets in the Sky Window hub shell; tools/pets_0_2_7_patch.py).
Build first: python tools/pets_0_2_7_patch.py; python SkyyPets/build_skyypets_0.2.7.py

    python SkyyPets/test_skyypets_0.2.7.py [--dir <folder inside tools/dev/scratch/>] [--keep] [--no-old]

  A / C / AA  (tools/harness_kit.py, fresh child JVMs, -Xverify:all) verify, class compare 0.2.6 -> 0.2.7 (+ HubBar, PetsHubOpen; PetsPage
              build + handleDataEvent, the plugin's setup / shutdown, the kit's version texts; non-class entries: manifest.json + the 59
              Sky Window kit files), engine-access audit
  HUB         EXECUTED (tools/hub_tab_kit.py: the SkyyMenu 0.3.19 harness's engine stand-ins, the REAL PageManager, -Xverify:all):
              REG    PetsHubOpen.register() = hub:tab:character:pets {"SkyyPets", "Pets", 50, "pets", PetsHubOpen, PetsHubOpen(true)}
                     (the contract row SUI.HUB_TABS); unregister() removes it, never another jar's array under the same key; setup /
                     shutdown call them (bytecode)
              VIS    (review fix) the visible Function = PetsCfg.ON: pets.enabled off = the Pets tab is not in the bar and a click on it
                     (HubBar.open) answers "hidden"; on again = shown
              OPEN   the open Function: not a UUID / an offline player = FALSE; a player = TRUE and the /pets page is the open page
              PAGE   the page built into REAL builders and checked as a hub page (hub_tab_kit.page_check: Sky Window shell, 974 x 946 <=
                     1080p, every contract tab fits, the body = 0.2.6's 926 x 808 under the strip, one tab per visible tab, Pets selected,
                     bindings, every set / binding names an element); the list view and a pet's detail view (a real Wolf record)
              CLICK  the bar: the Pets tab on the detail view = back to the list; another tab through its Function / the command fallback;
                     a hidden / missing tab = the page stays and says so; < Menu with / without SkyyMenu; the X closes; the page's own
                     clicks still work after the bar (open a pet, Back, Close)
  SND         the 0.2.6 harness's sound phase on the 0.2.7 jar (the /pets slot clicks still play their sounds)
  OLD         the WHOLE 0.2.5 harness (test_skyypets_0.2.5.py) on the 0.2.7 jar with --old 0.2.6 (ECS, perm, bytecode, mobs, restarts, START
              TWICE on a scratch COPY of the live mods folder, rollbacks, audit). Its checks that pin the 0.2.5 identity or the 0.2.6 page
              window (title "Pets", 960 x 880) are expected to differ (EXPECTED_OLD, each with its reason); any other failure fails.
Exit code 1 on any failure.
"""
import os, sys, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW
import hub_tab_kit as HT

VERSION = "0.2.7"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.2.6.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "hubsH3a", "pets")))
PKG = "com.skyy.pets."
EXPECT = {
    "PetsPage": ["~m build", "~m handleDataEvent"],
    "SkyyPetsPlugin": ["~m setup", "~m shutdown"],
    "CfgFn": ["~m opExport"],          # the kit's version text
    "CfgRows": ["~<clinit>", "~m header"],      # the kit's version text (+ the config.properties template header)
    "PetsCfg": ["~m applyAll", "~m seed"],     # the config.properties template header names the version (DEFAULT_TEXT) - nothing else
}
ADDED = ["HubBar", "PetsHubOpen"]
if HK.arg("--phase") == "compare":
    HT.allow_kit_entries()
_s6 = importlib.util.spec_from_file_location("test_skyypets_0_2_6", os.path.join(HERE, "test_skyypets_0.2.6.py"))
T26 = importlib.util.module_from_spec(_s6)
_s6.loader.exec_module(T26)
T26.PKG = PKG
FAIL_TEXT = "That tab could not open right now - try again."
# the 0.2.5 harness's checks that pin the 0.2.5 identity / the 0.2.6 page window (prefix of the FAILED line) - expected on 0.2.7, with why
EXPECTED_OLD = [
    ("J: manifest Main / IncludesAssetPack TRUE (0.2: the two roles) / Version / Name", "the version is 0.2.7"),
    ("J/C: exactly the 47 expected classes: extra ['com.skyy.pets.HubBar', 'com.skyy.pets.PetSnd', 'com.skyy.pets.PetsHubOpen'] missing []", "+ PetSnd (0.2.6) + HubBar + PetsHubOpen"),
    ("compare: C 0.2.5: the classes of 0.2.4 + PetOwnerFn only: +['HubBar', 'PetsHubOpen'] -[]", "its compare is 0.2.4 -> 0.2.5 (ours: phase C)"),
    ("J: 0.2 ships exactly the two NPC role files (no lang / .ui / model / texture): ['Common/UI/Custom/SkyyKit/", "+ the 59 Sky Window kit textures (0.2.7; ours: phase C + the build's check_jar_kit)"),
    # the hub bar adds exactly 2 bindings (< Menu + the X; that harness registers no hub tab, so the strip draws none) to every page build
    ("core: X: list view: slot 1 Open + 8 rows + prev / next + close = 14 events,", "12 + the bar's 2 bindings"),
    ("core: X 0.2.2: details of a Mouse (pet only): the Summon slot button is NOT bound (+ slot 1 Open + close): 7", "5 + the bar's 2 bindings"),
    ("core: X 0.2.2: now the Summon slot button is bound and enabled", "its count 6 + the bar's 2 bindings"),
    ("core: X: details with slot 2 filled: slot 2 Open + 4 buttons + close", "its count 6 + the bar's 2 bindings"),
    ("core: X: a bad file: an empty list (prev / next / close only)", "its count 3 + the bar's 2 bindings"),
    ("compare: C 0.2.5: records, store, buffs, XP, ops, the tick, timers, commands, the views (LIVE upkeep), the world calls, F, the sweep, the loadout bridge, the page: byte-for-byte 0.2.4 (changed: ['PetsPage'])", "PetsPage = the 0.2.6 sound sites + the 0.2.7 hub shell"),
    ("compare: C 0.2.5: every change is one of the planned ones:", "0.2.6 + 0.2.7's planned changes (ours: phase C)"),
    ("compare: C 0.2.5: the plugin's setup + shutdown changed: ['~setup']", "the ready line names the sounds"),
    ("compare: C 0.2.5: PetsCfg.<clinit> differs from 0.2.4 only in its constants (strings / table sizes): [", "the 0.2.6 sound fields"),
    ("compare: C 0.2.5: shutdown = 0.2.4's + one more instanceof (PetOwnerFn) guarding the pets:fn:ownerOf remove (never another mod's entry)", "0.2.7 shutdown + PetsHubOpen.unregister"),
    ("rollback 0.2.4: R 0.2.5: rollback - the 0.2.4 jar reads the live copy after 0.2.5", "the old jar is 0.2.6 here (its text says 0.2.6)"),
    ("AA: engine-access audit: ", "+ PetSnd, HubBar, PetsHubOpen; ours: phase AA (refused must stay [])"),
]


def run_hub(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    P_ = lambda n: JClass(PKG + n)
    Cfg, Store, Ops, Log, HO, HB, Page = P_("PetsCfg"), P_("PetStore"), P_("PetOps"), P_("PetsLog"), P_("PetsHubOpen"), P_("HubBar"), P_("PetsPage")
    Log.LINES = JClass("java.util.ArrayList")()
    mods = os.path.join(scratch, "hub-mods")
    os.makedirs(mods, exist_ok=True)
    Cfg.load(E.Paths.get(mods))
    Store.ROOT = E.Paths.get(mods, "Skyy_SkyyPets")
    Store.DIR = Store.ROOT.resolve("pets")
    P = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-0000000000b7"), "PetHub")
    u = P.pr.getUuid()
    K.check(E.same(HB.map(), E.bridge), "the kit HubBar and the harness share ONE bridge map (skyy.bridge)")
    # ---------------------------------------------------------------- REG
    K.eq(str(HO.register()), "character:pets", "REG: register() answers the tab it put")
    e = HT.reg_check(K, E, "character", "pets", "SkyyPets", "Pets", 50, "pets", PKG + "PetsHubOpen", PKG + "PetsHubOpen")
    # ---------------------------------------------------------------- VIS (review fix: the tab follows pets.enabled)
    on0 = bool(Cfg.ON)
    K.check(on0 and e is not None and bool(e[5].vis) and not bool(e[4].vis), "VIS: the entry's visible Function is PetsHubOpen(true), its open Function PetsHubOpen()")
    K.check(e is not None and e[5].apply(u) == E.TRUE and e[5].apply(None) == E.TRUE and "pets" in HT.hub_tabs(E, "character", u),
            "VIS: pets.enabled on = the visible Function answers TRUE (any caller) and the tab is in the bar")
    o0 = int(HO.OPENED)
    Cfg.ON = False
    K.check(e is not None and e[5].apply(u) == E.FALSE and "pets" not in HT.hub_tabs(E, "character", u),
            "VIS: pets.enabled OFF = the visible Function answers FALSE and the bar leaves the Pets tab out (%s)" % HT.hub_tabs(E, "character", u))
    K.eq(str(HB.open(P.pr, u, "character", "pets")), "hidden", "VIS: pets.enabled OFF = a (forged) Pets tab click answers hidden")
    K.check(int(HO.OPENED) == o0, "VIS: ... and the open Function never ran")
    Cfg.ON = on0
    K.check("pets" in HT.hub_tabs(E, "character", u), "VIS: pets.enabled on again = the tab is back")
    K.eq(int(HO.unregister()), 1, "REG: unregister() removes our 1 key")
    K.check(E.bridge.get("hub:tab:character:pets") is None, "REG: the tab is gone after unregister()")
    HO.register()
    other = JClass("java.lang.Object")()
    E.bridge.put("hub:tab:character:pets", other)
    K.eq(int(HO.unregister()), 0, "REG: unregister() leaves another jar's value under the same key")
    K.check(E.same(E.bridge.get("hub:tab:character:pets"), other), "REG: ... and it is still there")
    E.bridge.remove("hub:tab:character:pets")
    HO.register()
    g = PW.calls(jar)
    K.check(PKG + "PetsHubOpen.register" in g.get("SkyyPetsPlugin.setup", set()), "REG: setup() calls PetsHubOpen.register (bytecode)")
    K.check(PKG + "PetsHubOpen.unregister" in g.get("SkyyPetsPlugin.shutdown", set()), "REG: shutdown() calls PetsHubOpen.unregister (bytecode)")
    K.check(PKG + "HubBar.handle" in g.get("PetsPage.handleDataEvent", set()) and PKG + "HubBar.build" in g.get("PetsPage.build", set()),
            "REG: the page's build() draws the bar, handleDataEvent asks HubBar.handle (bytecode)")
    # ---------------------------------------------------------------- OPEN
    fn = HO()
    K.check(fn.apply("not a uuid") == E.FALSE and fn.apply(E.UUID.randomUUID()) == E.FALSE, "OPEN: not a UUID / an offline player = FALSE")

    def open_page():
        r = fn.apply(u)
        E.pump(P)
        pg = E.pg(P)
        return pg if (r == E.TRUE and pg is not None and str(pg.getClass().getName()) == PKG + "PetsPage") else None
    pg = open_page()
    K.check(pg is not None and int(HO.OPENED) >= 1, "OPEN: a player = TRUE, the /pets page is open")
    # ---------------------------------------------------------------- PAGE (list view, then a pet's detail view)
    w, h, sets, evs = HT.page_check(K, E, P, HT.build(pg, P), "SkyyPt", "character", "pets", "Pets", "PAGE list")
    K.eq((w, h), (974, 946), "PAGE list: the window 974 x 946 (0.2.6's 960 x 880 + the strip + the sky padding)")
    K.check(any("Your pets (0 / " in str(d) for s_, d in sets.items() if s_ == "#SkyyPtLowH.Text"), "PAGE list: the list head (no pets yet)")
    r = Store.get(str(Store.pkey(u)))
    pid = str(Ops.create(r, None, "Wolf", 3, 5, 0, "test", "t", True))
    K.check(not pid.startswith("-") and r.has(pid), "PAGE a Wolf pet record (%s)" % pid)
    pg = open_page()
    HT.build(pg, P)
    pg.handleDataEvent(P.ref, P.st, '{"a":"open","i":"0","t":"%s"}' % pg.tok)
    E.pump(P)
    K.check(int(pg.view) == 1 and str(pg.sel) == pid, "PAGE the page's own click still works: a pet opened (detail view)")
    w2, h2, sets2, _e2 = HT.page_check(K, E, P, HT.build(pg, P), "SkyyPt", "character", "pets", "Pets", "PAGE detail")
    K.check(pid in str(sets2.get("#SkyyPtD10V.Text")) and "#SkyyPtB4" in [s for s, _t in _e2], "PAGE detail: the 11 detail rows + Back")
    # ---------------------------------------------------------------- CLICK
    fakes = HT.Fakes(E, "character")

    def open_detail():
        p_ = open_page()
        HT.build(p_, P)
        p_.handleDataEvent(P.ref, P.st, '{"a":"open","i":"0","t":"%s"}' % p_.tok)
        E.pump(P)
        return p_
    HT.clicks(K, E, P, open_detail, "character", "pets", "CLICK", fakes, self_check=lambda p_: int(p_.view) == 0 and str(p_.info) == "",
              fail_text=FAIL_TEXT)
    pg = open_page()
    K.eq(len(HT.hub_tabs(E, "character", u)), 3, "CLICK the bar shows Pets + the 2 visible stand-in tabs (the hidden one is left out)")
    pg.handleDataEvent(P.ref, P.st, '{"a":"close"}')
    E.pump(P)
    K.check(E.pg(P) is None, "CLICK the page's own Close still closes")
    fakes.remove()
    # the OLD harness's event counts: with NO tab registered the bar adds exactly its 2 bindings (< Menu + the X) to a page build
    HO.unregister()
    r2 = Store.get(str(Store.pkey(E.UUID.fromString("00000000-0000-0000-0000-0000000000b8"))))
    P2 = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-0000000000b8"), "PetHub2")
    p2 = Page(P2.pr)
    _c2, ev2 = HT.build(p2, P2)
    K.eq(sorted(s for s, _t in ev2), ["#SkyyPtClose", "#SkyyPtHubClose", "#SkyyPtHubMenu", "#SkyyPtPgNext", "#SkyyPtPgPrev"],
         "OLD counts: an empty list with no tab registered = prev / next / close + the bar's 2 bindings (3 + 2)")
    K.check(r2.count() == 0, "OLD counts: that player has no pets")
    K.save()


def run_snd(out, jar, scratch, home):
    T26.run_snd(out, jar, scratch, home)


def run_old():
    """the whole 0.2.5 harness on the 0.2.7 jar (--old 0.2.6); returns (summary lines, unexpected failures, expected ones, rc)"""
    sc = os.path.join(os.path.dirname(SCRATCH), "pets-old")
    p = subprocess.run([sys.executable, os.path.join(HERE, "test_skyypets_0.2.5.py"), "--jar", JAR, "--old", OLD_JAR, "--dir", sc],
                       env=dict(os.environ), capture_output=True, text=True, encoding="utf-8", errors="replace")
    lines = p.stdout.splitlines()
    open(os.path.join(os.path.dirname(SCRATCH), "pets-old.log"), "w", encoding="utf-8").write(p.stdout + "\n" + p.stderr)
    oks = [l for l in lines if l.endswith("fail(s)") and " ok, " in l]
    failed = [l.strip()[len("FAILED: "):] for l in lines if l.strip().startswith("FAILED: ")]
    exp, bad = [], []
    for f in failed:
        (exp if [e for e in EXPECTED_OLD if f.startswith(e[0])] else bad).append(f)
    return oks, bad, exp, p.returncode


if __name__ == "__main__":
    if "--phase" not in sys.argv and "--no-old" not in sys.argv:
        oks, bad, exp, rc = run_old()
        print("OLD. the 0.2.5 harness on the 0.2.7 jar: %s; %d expected identity checks differ, %d other failure(s)" % (oks[-1:] or "no summary", len(exp), len(bad)))
        for e in exp:
            print("  note (old): expected on 0.2.7: %s" % e[:200])
        for b in bad:
            print("  OLD unexpected: %s" % b[:400])
        HK.check(bool(oks), "OLD: the 0.2.5 harness ran to its summary")
        HK.check(not bad, "OLD: no failure outside the listed identity checks: %s" % bad[:5])
        HK.check(len(exp) <= len(EXPECTED_OLD), "OLD: at most the listed identity checks differ (%d)" % len(exp))
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("hub", run_hub), ("snd", run_snd)], script=__file__)
