"""Harness for SkyyPets 0.4.2 (MENU PATTERN sweep S1: /pets and the hatch reel page on the kit 1.7 hub page; tools/pets_0_4_2_patch.py).
Build first: python tools/pets_0_4_2_patch.py; python SkyyPets/build_skyypets_0.4.2.py

    python SkyyPets/test_skyypets_0.4.2.py [--dir <folder inside tools/dev/scratch/>]

  A / C / AA  (tools/harness_kit.py, fresh child JVMs, -Xverify:all) verify, class compare 0.4.1 -> 0.4.2 (exactly the planned members: the
              kit 1.7 HubBar members, PetsPage's scrolling grid / clicks / build, PetHatchPage's build / clicks; non-class entries = the
              manifest only), engine audit
  HATCH       0.4.1's HATCH phase EXECUTED on this jar (crafting, the Hatchery place / wait / hatch / take out / fuse, every crash point,
              right-click) - the logic is untouched, every check must pass
  PAGES       EXECUTED in the hub stage (tools/hub_tab_kit.py: the REAL PageManager, Universe, inventories): EVERY view the mod draws -
              the Pets view, the starter view, Eggs, Hatchery, the hatch reel page (reels, result) - BUILT through the real build() and
              checked as a kit 1.7 page on its real commands: check_page, the kit's texture paths (+ the hub tab art), every b.set /
              binding names an element, SUI.assert_menu_page (1600 x 980, row 1 + row 2, ONE sub row, no back / menu button, no pager)
              + the old features: the sub-tab row (PETS | EGGS | HATCHERY, the active one Primary, tab0 - tab2 and 0.4.1's tab + i),
              row 2's Pets / row 1's Character = back to the pets view, the scrolling grid (20 x 6 at least, 120 cells, Show more past
              200), Eggs rows + Craft, the Hatchery: the growing slot rows, place by a grid click, Take out (two presses), Hatch -> the
              reel page (rows 1 + 2, PETS | EGGS | HATCHERY | HATCHING), the reels run to the result + ONE reveal, the sub-tabs back to
              the Pets page tabs, a row 2 click mid-reel = the result at once + the Pets page, the fuse modes, Close / the X
  LIVE        0.4.1's LIVE phase: start twice on a scratch COPY of the live Skyy_SkyyPets folder - nothing written, no cut-off move
Exit code 1 on any failure.
"""
import os, sys, re, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import skyyui as SUI

_cmp0 = HK.run_compare
_s41 = importlib.util.spec_from_file_location("test_skyypets_0_4_1", os.path.join(HERE, "test_skyypets_0.4.1.py"))
T41 = importlib.util.module_from_spec(_s41)
_s41.loader.exec_module(T41)
HK.run_compare = _cmp0          # the 0.4.1 harness swaps the compare for its egg JSON - 0.4.2 changes only the manifest

VERSION = "0.4.2"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.4.1.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "menuS1", "pets", "test")))
_HB_ROW = ["+<clinit>", "+f ROW_IDS", "+f ROW_TITLES", "+m build2", "+m buildRow", "+m def4", "+m defOf", "+m defTab", "+m goHub", "+m hostOf",
           "+m hostShown", "+m hostTab", "+m hubs", "+m iconOf", "+m okIcon", "+m okItem", "+m openSub", "+m pickTab", "+m putIcon", "+m putSub",
           "+m route", "+m rowLab", "+m rowStyle", "+m rowWidth", "+m selOf", "+m subIcon", "+m subTabs", "+m tabBStyle", "+m tabLab", "+m titleOf"]
_HB_17 = ["+m bigLab", "+m bigRow", "+m bigRowFill", "+m bigTabLab", "+m bigTabsFill", "+m growSize", "+m hasArt", "+m page17", "+m subTab"]
EXPECT = {
    # the kit's HubBar with row=True (kit 1.6 row 1 + merged tabs + route) and page=True (kit 1.7: big rows, page17, subTab, growSize, hasArt)
    "HubBar": sorted(_HB_ROW + _HB_17),
    # the scrolling grid (fillGrid takes the event builder now: + / -), no pages (PER_PAGE, turnPage), EG_CELLS 48 -> 60 (fillEggGrid inlines it)
    "PetsPage": sorted(["-f PER_PAGE", "+f GRID_COLS", "+f GRID_ROWS", "+f GRID_MAX", "-m turnPage", "-m fillGrid", "+m fillGrid", "~m fillEggGrid",
                        "~m build", "~m handleDataEvent"]),
    "PetHatchPage": ["~m build", "~m handleDataEvent"],
    # the version text only (config header / export / Server Setup header, the ready line + the page id)
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "PetsCfg": ["~m applyAll", "~m seed"], "SkyyPetsPlugin": ["~m setup"],
}
ADDED = []
DECL_RE = re.compile(r"\b([A-Za-z]+) #([A-Za-z0-9]+) \{")


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


def menu_page(K, built, what):
    """the kit 1.7 checks of one REAL built page: markup rules / parents / ids, the kit texture paths (+ tab art), every b.set and binding
    names an element, SUI.assert_menu_page on the real commands (and the b.set texts)"""
    cmds, evs = built
    apps = SUI.Appends([(None if s is None else s.lstrip("#"), t) for ty, s, t, d in cmds if t is not None and ty and "Append" in ty])
    sets = [(s, unq(d)) for ty, s, t, d in cmds if ty == "Set"]
    try:
        SUI.check_page(apps, "Skyy")
        K.check(True, "%s: check_page (markup rules, parents, no duplicate id; %d appends)" % (what, len(apps)))
    except Exception as e:
        K.check(False, "%s: check_page: %s" % (what, e))
    try:
        SUI.check_sky_paths(apps, tab_icons=True)
        allp = [m.group(0) for mk in apps.markups() for m in SUI._SKY_PATH_RE.finditer(SUI.render(mk))]
        K.check(not [p for p in allp if p.startswith('"../')], "%s: no texture path leaves Common/UI/Custom (%d)" % (what, len(allp)))
    except Exception as e:
        K.check(False, "%s: sky paths: %s" % (what, e))
    ids = set()
    for _p, mk in apps:
        ids |= set(x.group(2) for x in DECL_RE.finditer(SUI.render(mk)))
    bs = [s for s, _t in evs]
    bad = [s for s, _d in sets if s.lstrip("#").split(".")[0] not in ids] + [s for s in bs if s.lstrip("#") not in ids]
    K.check(not bad, "%s: every b.set / binding names an element that exists (%d sets, %d bindings): %s" % (what, len(sets), len(bs), bad[:4]))
    try:
        info = SUI.assert_menu_page(apps, hub="character", what=what, sets=sets)
        K.check(info["rows"] == 2 and info["subs"] == 1, "%s: assert_menu_page (1600 x 980, rows %d, sub rows %d, no back button, no pager)" % (what, info["rows"], info["subs"]))
    except Exception as ex:
        K.check(False, "%s: assert_menu_page: %s" % (what, ex))
    return apps, dict(sets), evs


def run_pages(out, jar, scratch, _home):
    from jpype import JClass, JProxy, JShort, JByte
    import hub_tab_kit as HT
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    P_ = lambda n: JClass(PKG + n)
    Cfg, Store, Ops, Log, Egg, Page, HPage, Reel, Hy, Eng = (P_("PetsCfg"), P_("PetStore"), P_("PetOps"), P_("PetsLog"), P_("PetEgg"), P_("PetsPage"),
                                                            P_("PetHatchPage"), P_("PetReel"), P_("PetHatchery"), P_("PetsEng"))
    Paths, UUID, IS = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    Log.LINES = JClass("java.util.ArrayList")()
    mods = os.path.join(scratch, "stage-mods")
    os.makedirs(mods, exist_ok=True)
    Cfg.load(Paths.get(mods))
    Store.ROOT = Paths.get(mods, "Skyy_SkyyPets")
    Store.DIR = Store.ROOT.resolve("pets")
    K.eq(str(P_("PetsHubOpen").register()), "character:pets", "REG the Pets hub tab is registered")
    Hy.OPENER = P_("PetHatchOpen")()
    P1 = E.mkp(UUID.fromString("00000000-0000-0000-0000-000000000612"), "Keeper")
    u1 = P1.pr.getUuid()
    k1 = str(Store.pkey(u1))
    Store.KEYOF.put(u1, k1)
    r1 = Store.get(k1)
    r1.set("starter", "123")
    for _ in range(4):
        Ops.createR(r1, None, "Rabbit", 1, 3, 0, 0, "test", "harness", False)
    told = []
    Eng.API = JProxy(PKG + "PetsApi", dict={"online": lambda: T41._uarr(JClass, [str(u1)]), "byName": lambda n: u1, "nameOf": lambda u: "Keeper",
                                            "tell": lambda u, t, c: told.append(str(t))})

    def click(page, P, a, i=None, extra=None, tok=True):
        Hy.CLICK.clear()
        d = '{"a":"%s"' % a + (',"i":"%s"' % i if i is not None else "") + (',"t":"%s"' % page.tok if tok else "") + (extra or "") + "}"
        page.handleDataEvent(P.ref, P.st, d)
        E.pump(P)
        return str(page.info)

    def subs(cmds, prefix):
        return [t for ty, s_, t, d in cmds if t and ("TextButton #%sSub" % prefix) in t]

    def grid_h(cmds):
        g = [t for ty, s_, t, d in cmds if t and t.startswith("ItemGrid #SkyyPtGrid ")]
        m = re.search(r"Height: (\d+)", g[0]) if g else None
        return int(m.group(1)) if m else None

    # ================================================================ the Pets view
    pg = Page(P1.pr)
    P1.pm.openCustomPage(P1.ref, P1.st, pg)
    E.pump(P1)
    b0 = HT.build(pg, P1)
    _a0, s0, e0 = menu_page(K, b0, "PAGE Pets view")
    sel = [s for s, _t in e0]
    sb = subs(b0[0], "SkyyPt")
    K.check(len(sb) == 3 and "Primary" in sb[0] and "Primary" not in sb[1] + sb[2] and 'Text: "Hatchery"' in sb[2],
            "PETS the ONE sub-tab row: PETS (Primary) | EGGS | HATCHERY")
    K.check(all(("#SkyyPtSub%d" % i) in sel for i in range(3)) and any("tab1" in t for s_, t in e0 if s_ == "#SkyyPtSub1"),
            "PETS the sub-tabs are bound (tab0 / tab1 / tab2)")
    K.check(not any(s_.startswith("#SkyyPtT") or s_.startswith("#SkyyPtPg") for s_ in sel) and not any(t and ("SkyyPtTabs" in t or "SkyyPtPg" in t) for _ty, _s, t, _d in b0[0]),
            "PETS 0.4.1's inner tab row and the pager are gone")
    K.check("#SkyyPtBigRow" in [s_ for ty, s_, t, d in b0[0] if s_] or any(t and "#SkyyPtBigRow " in t for _ty, _s, t, _d in b0[0]), "PETS row 1 is there")
    K.check(any(s_ == "#SkyyPtBigT%d" % i and "hub:pets" in t for s_, t in e0 for i in range(8)), "PETS row 2 holds the Pets tab (hub:pets)")
    K.check(int(pg.cells) == 120 and grid_h(b0[0]) == 6 * 74 + 5 * 2 and "#SkyyPtGrid" in sel and "#SkyyPtMore" not in sel,
            "PETS one scrolling grid: 20 x 6 = 120 cells (%s), %s px high, no Show more for 4 pets" % (pg.cells, grid_h(b0[0])))
    K.check(any(t and t.startswith("Group #SkyyPtGridL ") and "TopScrolling" in t for _ty, _s, t, _d in b0[0]), "PETS the grid sits in a scroll list (TopScrolling)")
    K.check(any(t and "TextButton #SkyyPtClose" in t and "Height: 48" in t for _ty, _s, t, _d in b0[0]) and "#SkyyPtClose" in sel and "#SkyyPtStatus.Text" in s0,
            "PETS the footer: the status line + Close (48 px)")
    K.check("Pet slot" in str(s0.get("#SkyyPtS1Nm.Text")) or "Rabbit" in str(s0.get("#SkyyPtS1Nm.Text")), "PETS the slot rows: %s / %s" % (s0.get("#SkyyPtS1Nm.Text"), s0.get("#SkyyPtS2Nm.Text")))
    g1 = click(pg, P1, "g", extra=',"SlotIndex":0')
    K.check(g1.startswith("+") or g1.startswith("="), "PETS a grid click still acts (the pet slot): %s" % g1)
    # ================================================================ Eggs (sub-tab tab1)
    click(pg, P1, "tab1", tok=False)
    b1 = HT.build(pg, P1)
    _a1, s1, e1 = menu_page(K, b1, "PAGE Eggs")
    sb1 = subs(b1[0], "SkyyPt")
    K.check(int(pg.tab) == 1 and "Primary" in sb1[1] and "Primary" not in sb1[0] and "#SkyyPtGrid" not in [s for s, _t in e1]
            and "Common Combat Egg" in str(s1.get("#SkyyPtE0Nm.Text")) and "Uncommon Mining Egg" in str(s1.get("#SkyyPtE9Nm.Text")) and "#SkyyPtE10Nm.Text" not in s1,
            "EGGS the sub-tab tab1 opens Eggs (EGGS Primary): 10 rows, tier then name: %s / %s" % (s1.get("#SkyyPtE0Nm.Text"), s1.get("#SkyyPtE9Nm.Text")))
    K.check(not any(s.startswith("#SkyyPtE") and s.endswith("Act") for s, _t in e1) and "Missing" in str(s1.get("#SkyyPtE0Tg.Text")), "EGGS nothing craftable = no Craft bound")
    st_ = P1.slots["storage"].getInventory()
    st_.addItemStackToSlot(JShort(0), IS("Food_Egg", 2))
    st_.addItemStackToSlot(JShort(1), IS("Skyy_Ench_Cobblestone", 12))
    b1 = HT.build(pg, P1)
    ci = [str(x) for x in Hy.CRAFT].index("Skyy_PetEgg_Mining_Common")
    s1 = dict((s_, d) for ty, s_, t, d in b1[0] if ty == "Set")
    K.check(("#SkyyPtE%dAct" % ci) in [s for s, _t in b1[1]] and "Ready" in str(s1.get("#SkyyPtE%dTg.Text" % ci)), "EGGS with the materials: Ready + Craft bound")
    # 0.4.1's own tab click (a = tab + i) still works
    click(pg, P1, "tab", 0, tok=False)
    K.eq(int(pg.tab), 0, "EGGS 0.4.1's tab + i click still switches (back to Pets)")
    # ================================================================ the Hatchery (sub-tab tab2)
    iv = P_("PetInvReal").of(P1.st, P1.ref)
    hb = P1.slots["hotbar"].getInventory()
    EID = "Skyy_PetEgg_Combat_Common"
    hb.addItemStackToSlot(JShort(2), IS(EID, 3))
    click(pg, P1, "tab2", tok=False)
    b2 = HT.build(pg, P1)
    _a2, s2, e2 = menu_page(K, b2, "PAGE Hatchery")
    sel2 = [s for s, _t in e2]
    rows2 = [t for ty, s_, t, d in b2[0] if t and t.startswith("Group #SkyyPtH1 ")]
    K.check(int(pg.tab) == 2 and "#SkyyPtEg" in sel2 and all(("#SkyyPtX%d" % i) in sel2 for i in range(3)) and "0 / 2 slots in use" in str(s2.get("#SkyyPtHsH.Text"))
            and "Slot 1 - empty" in str(s2.get("#SkyyPtH1Nm.Text")) and len(list(pg.eids)) == 1 and str(pg.eids[0]) == EID,
            "HATCHERY 2 empty slots, the egg grid holds the egg you carry, the modes bound: %s" % s2.get("#SkyyPtHsH.Text"))
    K.check(rows2 and "Height: 112" in rows2[0], "HATCHERY 2 slots = the big rows (Skyy rule 7, growSize): %s" % (rows2[0][:70] if rows2 else None))
    egrid = [t for ty, s_, t, d in b2[0] if t and "ItemGrid #SkyyPtEg " in t]
    K.check(egrid and "SlotsPerRow: 20" in egrid[0] and int(Page.EG_CELLS) == 60, "HATCHERY the egg grid is 20 x 3 = 60 cells")
    g0 = click(pg, P1, "eg", extra=',"SlotIndex":0')
    K.check(g0.startswith("+Common Combat Egg is in Hatchery slot 1") and int(iv.count(EID)) == 2 and r1.get("hatchery.1") is not None, "HATCHERY a grid click puts the egg in slot 1: %s" % g0)
    Egg.NOFORCE.clear()
    Egg.debts(u1, r1, iv, int(JClass("java.lang.System").currentTimeMillis()) + 31000)
    o1 = click(pg, P1, "slot", 1, extra=',"m":"o"')
    K.check(o1.startswith("=Take the Common Combat Egg out of slot 1?"), "HATCHERY Take out press 1 asks (the two-press pattern): %s" % o1)
    pg.confirm = ""
    Hy.CLOCK_OFF = 3 * 60 * 1000
    HT.build(pg, P1)
    n0 = int(r1.count())
    click(pg, P1, "slot", 1, extra=',"m":"h"')
    cur = E.pg(P1)
    K.check(int(r1.count()) == n0 + 1 and r1.get("hatchery.1") is None and cur is not None and str(cur.getClass().getName()) == PKG + "PetHatchPage" and int(cur.view) == 1,
            "HATCHERY READY + Hatch: the pet saved FIRST, then the reel page opens (view %s)" % (cur.view if cur is not None else None))
    Hy.CLOCK_OFF = 0
    # ================================================================ the hatch reel page
    bh1 = HT.build(cur, P1)
    _ah, sh1, eh1 = menu_page(K, bh1, "PAGE hatch reels")
    hs_ = subs(bh1[0], "SkyyHtP")
    selh = dict((s_, t) for s_, t in eh1)
    K.check(len(hs_) == 4 and "Primary" in hs_[3] and "Primary" not in hs_[0] + hs_[1] + hs_[2] and 'Text: "Hatching"' in hs_[3]
            and all(("#SkyyHtPSub%d" % i) in selh for i in range(3)) and "#SkyyHtPSub3" not in selh
            and all(w_ in selh.get("#SkyyHtPSub%d" % i, "") for i, w_ in enumerate(("pets", "eggs", "hatchery")))
            and "hatchery" not in selh.get("#SkyyHtPSub0", ""),
            "HPAGE the sub-tab row PETS | EGGS | HATCHERY | HATCHING (this view, unbound)")
    K.check(any(s_.startswith("#SkyyHtPBigT") and "hub:pets" in t for s_, t in eh1) and "#SkyyHtPHubClose" in selh, "HPAGE rows 1 + 2 and the X are bound")
    K.check(any(t and t.startswith("Group #SkyyHtA2") or (t and "ItemGrid #SkyyHtA2" in t) for _ty, _s, t, _d in bh1[0]) and "#SkyyHtSkip" in selh, "HPAGE view 1: the reels + Skip")
    told.clear()
    frames = 0
    for _ in range(80):
        if int(cur.view) != 1:
            break
        cur.tick(Reel(cur, cur.gen, 0))
        frames += 1
        E.pump(P1)
    K.check(int(cur.view) == 2 and frames >= 20 and len([t for t in told if "You hatched a" in t]) == 1, "HPAGE the two reels run to the result + ONE reveal line (%d steps)" % frames)
    bh2 = HT.build(cur, P1)
    _ah2, sh2, eh2 = menu_page(K, bh2, "PAGE hatch result")
    sel_r = [s for s, _t in eh2]
    K.check("#SkyyHtAgain" not in sel_r and "#SkyyHtPets" not in sel_r and "#SkyyHtGo" not in sel_r and "#SkyyHtClose" in sel_r
            and "You hatched" in str(sh2.get("#SkyyHtStatus.Text")) and "#SkyyHtResN.Text" in sh2,
            "HPAGE the result: no Hatchery / Open pets buttons any more (the sub-tabs lead there), Close stays")
    click(cur, P1, "hatchery", tok=False)
    back = E.pg(P1)
    K.check(back is not None and str(back.getClass().getName()) == PKG + "PetsPage" and int(back.tab) == 2, "HPAGE the sub-tab HATCHERY opens the Pets page on its Hatchery tab")
    # a second egg: row 2's Pets mid-reel = the result at once (the pet is saved) + the Pets page
    pg = back
    click(pg, P1, "eg", extra=',"SlotIndex":0')
    Egg.NOFORCE.clear()
    Egg.debts(u1, r1, iv, int(JClass("java.lang.System").currentTimeMillis()) + 31000)
    Hy.CLOCK_OFF = 3 * 60 * 1000
    HT.build(pg, P1)
    n1 = int(r1.count())
    click(pg, P1, "slot", 1, extra=',"m":"h"')
    cur = E.pg(P1)
    Hy.CLOCK_OFF = 0
    told.clear()
    ok_mid = cur is not None and str(cur.getClass().getName()) == PKG + "PetHatchPage" and int(cur.view) == 1
    click(cur, P1, "hub:pets", tok=False)
    now = E.pg(P1)
    K.check(ok_mid and int(r1.count()) == n1 + 1 and now is not None and str(now.getClass().getName()) == PKG + "PetsPage" and int(now.tab) == 0
            and len([t for t in told if "You hatched a" in t]) == 1,
            "HPAGE row 2's Pets mid-reel: the result line at once (one), the Pets page opens on its pets view")
    # the sub-tab Eggs of the reel page (a page built straight away)
    hp2 = HPage(P1.pr)
    P1.pm.openCustomPage(P1.ref, P1.st, hp2)
    E.pump(P1)
    bh0 = HT.build(hp2, P1)
    menu_page(K, bh0, "PAGE hatch view 0")
    click(hp2, P1, "eggs", tok=False)
    ep = E.pg(P1)
    K.check(ep is not None and str(ep.getClass().getName()) == PKG + "PetsPage" and int(ep.tab) == 1, "HPAGE the sub-tab EGGS opens the Pets page on Eggs")
    hp3 = HPage(P1.pr)
    P1.pm.openCustomPage(P1.ref, P1.st, hp3)
    E.pump(P1)
    HT.build(hp3, P1)
    click(hp3, P1, "hub:close", tok=False)
    K.check(E.pg(P1) is None, "HPAGE the X (hub:close) closes the reel page")
    # ================================================================ row 2 / row 1 on the Pets page = back to the pets view
    pg = Page(P1.pr)
    P1.pm.openCustomPage(P1.ref, P1.st, pg)
    E.pump(P1)
    click(pg, P1, "tab2", tok=False)
    K.eq(int(pg.tab), 2, "SELF the Hatchery tab is open")
    click(pg, P1, "hub:pets", tok=False)
    K.check(int(pg.tab) == 0 and E.same(E.pg(P1), pg), "SELF row 2's Pets on the Hatchery = back to the pets view (same page)")
    click(pg, P1, "tab1", tok=False)
    click(pg, P1, "hub:h:character", tok=False)
    K.check(int(pg.tab) == 0 and E.same(E.pg(P1), pg), "SELF row 1's Character = back to the pets view")
    # ================================================================ the fuse modes (Hatchery)
    click(pg, P1, "tab2", tok=False)
    click(pg, P1, "emode", 2, tok=False)
    HT.build(pg, P1)
    rab = [str(x) for x in pg.eids if str(r1.kindOf(x)) == "Rabbit"]
    K.check(len(rab) == 1, "FUSE Fuse pets: one Rabbit cell (%s)" % [str(r1.kindOf(x)) for x in pg.eids])
    ri = [str(x) for x in pg.eids].index(rab[0]) if rab else 0
    f1 = click(pg, P1, "eg", extra=',"SlotIndex":%d' % ri)
    HT.build(pg, P1)
    f2 = click(pg, P1, "eg", extra=',"SlotIndex":%d' % ri)
    K.check(f1.startswith("=Fuse 4") and f2.startswith("+Fused 4"), "FUSE Fuse pets: press 1 asks, press 2 fuses: %s / %s" % (f1, f2))
    # ================================================================ a big collection: the grid grows + Show more past 200
    Cfg.OWNED_MAX = 400
    while int(r1.count()) < 230:
        Ops.createR(r1, None, "Mouse", 1, 1, 0, 0, "test", "harness", False)
    click(pg, P1, "tab0", tok=False)
    bg = HT.build(pg, P1)
    _ag, sg, eg_ = menu_page(K, bg, "PAGE Pets view, 230 pets")
    K.check(int(pg.cells) == 200 and grid_h(bg[0]) == 10 * 74 + 9 * 2 and "#SkyyPtMore" in [s for s, _t in eg_] and "the first 200" in str(sg.get("#SkyyPtLowH.Text")),
            "GRID 230 pets: 200 cells (10 rows, %s px, scrolls) + Show more: %s" % (grid_h(bg[0]), sg.get("#SkyyPtLowH.Text")))
    click(pg, P1, "more", tok=False)
    bg2 = HT.build(pg, P1)
    K.check(int(pg.cells) == 240 and len(list(pg.ids)) == 230 and "#SkyyPtMore" not in [s for s, _t in bg2[1]], "GRID Show more: every pet (230 of 12 rows = 240 cells)")
    click(pg, P1, "role", 0, tok=False)
    HT.build(pg, P1)
    K.check(int(pg.cells) == 200 and int(pg.pg) == 0, "GRID a filter click starts again at 200")
    n_ = len(E.sent(P1))
    click(pg, P1, "close", tok=False)
    K.check(len(E.sent(P1)) > n_ and E.pg(P1) is None, "CLOSE one update empties the grid first, then the page closes")
    K.save()


def run_hatch(out, jar, scratch, home):
    T41.run_hatch(out, jar, scratch, home)


def run_live(out, jar, scratch, home):
    T41.run_live(out, jar, scratch, home)


if __name__ == "__main__":
    phases = [("hatch", run_hatch), ("pages", run_pages), ("live", run_live)]
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=phases, script=__file__, live=(T41.LIVE, "Skyy_SkyyPets"))
