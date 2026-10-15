"""Harness for SkyyCollections 0.2.17 (HUBS H3a: the Character hub's Collections tab, /collections in the Sky Window hub shell;
tools/collections_0_2_17_patch.py). Build first:
    python tools/collections_0_2_17_patch.py && python SkyyCollections/build_skyycollections_0.2.17.py

    python SkyyCollections/test_skyycollections_0.2.17.py [--jar <SkyyCollections-0.2.17.jar>] [--dir <scratch>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.2.16 -> 0.2.17: + HubBar, CollHubOpen; CollPage build + handleDataEvent, the plugin's setup / shutdown, the kit's version
                texts only; non-class entries: manifest.json + the 59 Sky Window kit files
  HUB  EXECUTED (tools/hub_tab_kit.py: the SkyyMenu 0.3.19 harness's engine stand-ins, the REAL PageManager, -Xverify:all) on a REAL
       registry (CollReg.loadAll on a scratch folder) and a real counts file:
       REG   CollHubOpen.register() = hub:tab:character:collections {"SkyyCollections", "Collections", 70, "collections", CollHubOpen, null}
             (the contract row SUI.HUB_TABS); unregister() removes it, never another jar's array; setup / shutdown call them (bytecode)
       OPEN  the open Function: not a UUID / an offline player = FALSE; a player = TRUE, /collections Home is the open page
       PAGE  every view built into REAL builders and checked as a hub page (hub_tab_kit.page_check: Sky Window shell, 1134 x 892 <= 1080p,
             every contract tab fits, the body content under the strip, one tab per visible tab, Collections selected, bindings, every
             set / binding names an element): Home, a category (the page's own ccat click), a collection (ccard), the recipe lists
       CLICK the bar: the Collections tab from a collection's page = Home; another tab through its Function / the command fallback; a
             hidden / missing tab = the page stays and says so; < Menu with / without SkyyMenu; the X closes; the page's own Close and
             Back still work after the bar; the page id the build prints = COLL_PAGE_CHECKED
  D    live     0.2.16's live phase (= 0.2.15's start twice on a scratch COPY of the live Skyy_SkyyCollections + the sound file + the kit
                TWICE): the first adds only what 0.2.16 adds, the second nothing
  AA   audit    the engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW
import hub_tab_kit as HT

_spec = importlib.util.spec_from_file_location("tc0216", os.path.join(HERE, "test_skyycollections_0.2.16.py"))
T16 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T16)

VERSION = "0.2.17"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCollections-0.2.16.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "hubsH3a", "coll")))
PKG = "com.skyy.collections."
LIVE_DIR = T16.LIVE_DIR
EXPECT = {"CfgFn": ["~m opExport"], "CfgRows": ["~m header"],      # the kit's version texts
          "CollPage": ["~m build", "~m handleDataEvent"], "SkyyCollectionsPlugin": ["~m setup", "~m shutdown"]}
ADDED = ["HubBar", "CollHubOpen"]
if HK.arg("--phase") == "compare":
    HT.allow_kit_entries()
FAIL_TEXT = "That tab could not open right now - try again."


def run_hub(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    P_ = lambda n: JClass(PKG + n)
    Reg, Store, HO, HB = P_("CollReg"), P_("CollStore"), P_("CollHubOpen"), P_("HubBar")
    base = os.path.join(scratch, "hub-mods", "Skyy_SkyyCollections")
    os.makedirs(base, exist_ok=True)
    Reg.BASE = E.Paths.get(base)
    Store.DIR = Reg.BASE.resolve("counts")
    Reg.loadAll()
    K.check(Reg.D is not None and int(Reg.D.n) > 50, "the registry loaded (%s collections)" % (None if Reg.D is None else int(Reg.D.n)))
    P = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-0000000000c7"), "CollHub")
    u = P.pr.getUuid()
    K.check(E.same(HB.map(), E.bridge), "the kit HubBar and the harness share ONE bridge map (skyy.bridge)")
    # ---------------------------------------------------------------- REG
    K.eq(str(HO.register()), "character:collections", "REG: register() answers the tab it put")
    HT.reg_check(K, E, "character", "collections", "SkyyCollections", "Collections", 70, "collections", PKG + "CollHubOpen")
    K.eq(int(HO.unregister()), 1, "REG: unregister() removes our 1 key")
    K.check(E.bridge.get("hub:tab:character:collections") is None, "REG: the tab is gone after unregister()")
    HO.register()
    other = JClass("java.lang.Object")()
    E.bridge.put("hub:tab:character:collections", other)
    K.eq(int(HO.unregister()), 0, "REG: unregister() leaves another jar's value under the same key")
    K.check(E.same(E.bridge.get("hub:tab:character:collections"), other), "REG: ... and it is still there")
    E.bridge.remove("hub:tab:character:collections")
    HO.register()
    g = PW.calls(jar)
    K.check(PKG + "CollHubOpen.register" in g.get("SkyyCollectionsPlugin.setup", set()), "REG: setup() calls CollHubOpen.register (bytecode)")
    K.check(PKG + "CollHubOpen.unregister" in g.get("SkyyCollectionsPlugin.shutdown", set()), "REG: shutdown() calls CollHubOpen.unregister (bytecode)")
    K.check(PKG + "HubBar.handle" in g.get("CollPage.handleDataEvent", set()) and PKG + "HubBar.build" in g.get("CollPage.build", set()),
            "REG: the page's build() draws the bar, handleDataEvent asks HubBar.handle (bytecode)")
    # ---------------------------------------------------------------- OPEN
    fn = HO()
    K.check(fn.apply("not a uuid") == E.FALSE and fn.apply(E.UUID.randomUUID()) == E.FALSE, "OPEN: not a UUID / an offline player = FALSE")

    def open_page():
        r = fn.apply(u)
        E.pump(P)
        pg = E.pg(P)
        return pg if (r == E.TRUE and pg is not None and str(pg.getClass().getName()) == PKG + "CollPage") else None
    pg = open_page()
    K.check(pg is not None and int(pg.view) == 0 and int(HO.OPENED) >= 1, "OPEN: a player = TRUE, /collections Home is open")
    # ---------------------------------------------------------------- PAGE: every view
    # a counts file with something in it (so a category shows cards and a collection page has numbers)
    d = Store.data(u)
    K.check(d is not None, "PAGE the player's counts data")
    R = Reg.D
    got = []
    for c in range(int(R.n)):
        if int(R.cat[c]) == 0 and not bool(R.hidden[c]) and len(got) < 3:
            it = str(R.items[c][0])
            d.items.put(it, JClass("java.lang.Long").valueOf(500))
            got.append(it)
    K.check(len(got) == 3, "PAGE 500 of 3 category-0 items in the counts (%s)" % got)

    def click(p_, word):
        p_.handleDataEvent(P.ref, P.st, '{"a":"%s"}' % word)
        E.pump(P)
        return E.pg(P)
    sizes = []
    w, h, sets, _ev = HT.page_check(K, E, P, HT.build(pg, P), "SkyyCollF", "character", "collections", "Collections", "PAGE home", idp="SkyyC")
    sizes.append((w, h))
    cur = click(pg, "ccat0")
    K.check(E.same(cur, pg) and int(pg.view) == 1 and int(pg.cat) == 0, "PAGE the page's own click still works: category 0 (view 1)")
    w, h, sets, _ev = HT.page_check(K, E, P, HT.build(pg, P), "SkyyCollF", "character", "collections", "Collections", "PAGE category", idp="SkyyC")
    sizes.append((w, h))
    HT.build(pg, P)
    cards = [int(x) for x in pg.cards] if pg.cards is not None else []
    K.check(any(c >= 0 for c in cards), "PAGE the category shows cards (%s)" % cards[:4])
    first = [i for i, c in enumerate(cards) if c >= 0][:1]
    if first:
        cur = click(pg, "ccard%d" % first[0])
        K.check(int(pg.view) == 2 and int(pg.coll) == cards[first[0]], "PAGE a card opens its collection (view 2)")
        w, h, sets, _ev = HT.page_check(K, E, P, HT.build(pg, P), "SkyyCollF", "character", "collections", "Collections", "PAGE collection", idp="SkyyC")
        sizes.append((w, h))
        cur = click(pg, "cback")
        K.check(int(pg.view) == 1, "PAGE Back from a collection = its category")
    cur = click(pg, "crecipes")
    K.check(int(pg.view) == 3, "PAGE the recipe list (view 3)")
    w, h, sets, _ev = HT.page_check(K, E, P, HT.build(pg, P), "SkyyCollF", "character", "collections", "Collections", "PAGE recipes", idp="SkyyC")
    sizes.append((w, h))
    K.check(sizes and all(x == (1134, 892) for x in sizes), "PAGE every view is the 1134 x 892 hub window (0.2.16's 1120 x 826 + strip + padding): %s" % sizes)
    # ---------------------------------------------------------------- CLICK
    fakes = HT.Fakes(E, "character")

    def open_cat():
        p_ = open_page()
        click(p_, "ccat1")
        return p_
    HT.clicks(K, E, P, open_cat, "character", "collections", "CLICK", fakes,
              self_check=lambda p_: int(p_.view) == 0 and str(p_.status) == "", fail_text=FAIL_TEXT)
    pg = open_page()
    K.check(click(pg, "cclose") is None, "CLICK the page's own Close still closes")
    fakes.remove()
    # ---------------------------------------------------------------- the page id the build checked
    gen = open(os.path.join(HERE, "build_skyycollections_%s.py" % VERSION), encoding="utf8").read()
    m = re.search(r'COLL_PAGE_CHECKED = "([0-9a-f]{12})"', gen)
    import zipfile
    plug = zipfile.ZipFile(jar).read("com/skyy/collections/SkyyCollectionsPlugin.class")
    K.check(m is not None and (b", page " + m.group(1).encode()) in plug, "PAGE the jar's page id (ready line) = COLL_PAGE_CHECKED %s (the page this harness passed on)" % (m.group(1) if m else None))
    K.save()


def run_live(out, jar, scratch, home):
    """0.2.16's live phase; its first-start check expects sounds.properties to APPEAR - the live world runs 0.2.16 now, so the copy
    already has it and the first start writes nothing at all (checked here instead: the file was in the live copy before the start)"""
    import json
    had = os.path.isfile(os.path.join(home, "sounds.properties"))
    T16.run_live(out, jar, scratch, home)
    d = json.load(open(out))
    stale = "DS the first start adds sounds.properties (and only kit files), no existing file changes: new [] changed []"
    if had and stale in d["fails"]:
        d["fails"].remove(stale)
        d["ok"] += 1
        d["notes"].append("D: the live copy already has sounds.properties (0.2.16 is live): the first start wrote nothing (new [] changed [])")
    elif not had:
        d["notes"].append("D: the live copy had no sounds.properties: 0.2.16's own first-start check applied")
    json.dump(d, open(out, "w"), indent=1)


if __name__ == "__main__":
    HK.run("SkyyCollections", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("hub", run_hub), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyCollections"))
