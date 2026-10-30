"""Harness for SkyyCollections 0.2.36 (rarity pass, looks only: a rarity square #SkyyCPr<i>Q on every recipe row of a collection's page;
tools/collections_0_2_36_patch.py). Build first:
    python tools/collections_0_2_36_patch.py && python SkyyCollections/build_skyycollections_0.2.36.py
      (SkyyGear/SkyyGear-0.3.29.jar gone? set SKYY_GEAR_0329_JAR to a copy extracted from backups/archive/old-jars-20261022.tar.xz)
    python SkyyCollections/test_skyycollections_0.2.36.py [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  S    static   the patch re-runs to identical bytes; line endings kept; no new class / command / system; jar: no class added or removed,
                the only non-class change is the manifest (items, recipes, lang, art byte-identical)
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.2.35 -> 0.2.36 (EXPECT below: CollPage + the version texts only)
  Q    rbg      CollPage.rbg EXECUTED: a rarity hex -> that colour at (0.4) (Epic, Legendary, the Mythic swap #CC66CC); locked = the faint
                grey whatever the colour; rarityHex's no-quality fallback #c8f0a0 / null / a malformed value = the faint grey
  M    page     EXECUTED through the real builders (tools/hub_tab_kit.py stand-ins, the REAL UICommandBuilder): a collection page with 4
                unlocked + 1 locked recipe (64 px rows) and one with 21 (46 px rows, a long name): every row has exactly one Group
                #SkyyCPr<i>Q, after its tier tag (34 px, the row's first cell: under the Tier head) and before the name, 10 x 10, vertically
                centred, its Background = rbg(rarityHex(the row's recipe), ok) (the
                locked row: the faint grey); the name keeps the row white (never the rarity colour); the row keeps its 8 px padding;
                the Tier head spans tag + square (48 px), the Recipe head 200; the 0.2.23 page check (check_page: no duplicate id; every b.set names an element; assert_menu_page: the content fits)
  FIT  fit      the 0.2.29 FIT phase on this jar: every recipe name of the default rewards (+ NEW) still fits its two-line cell (RPNAME2
                now 340), a long name gets the 46 px rows and shows whole
  LIVE the 0.2.35 live phase: every setup migration + CollReg.loadAll on a scratch COPY of the live Skyy_SkyyCollections, twice: no file changes
  AA   audit    the engine-access audit
NOT COVERED (UNVERIFIED in game): the real rarity colours (a bare JVM has no Item / ItemQuality assets, so rarityHex answers its fallback
and every page row here is the faint grey - rarityHex itself is live since 0.2.12's rank-up card); the client's look of a 40 % square.
Exit code 1 on any failure.
"""
import os, sys, re, zipfile, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "ci"))
import skyybuild as B
import harness_kit as HK
import skyyui as SUI

VERSION, OLD_VERSION = "0.2.36", "0.2.35"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCollections-%s.jar" % OLD_VERSION)
GEN = os.path.join(HERE, "build_skyycollections_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyycollections_%s.py" % OLD_VERSION)
PATCH = os.path.join(ROOT, "tools", "collections_0_2_36_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "rar_collections", "h")))
PKG = "com.skyy.collections."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyCollections")
EXPECT = {"CollPage": ["+m rbg", "~m buildDetail", "~m recipePanel"],   # buildDetail: the column heads (Tier 40 -> 48, Recipe 208 -> 200)
          "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],                # the kit's version texts
          "SkyyCollectionsPlugin": ["~m setup"]}                                                     # the ready line (version, page id)
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = []
NONE = SUI.COLOR["disabled"] + "(0.15)"
ROW_H = {0: 32, 1: 46, 2: 64}


def tmod(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    old, cmp0 = list(sys.argv), HK.run_compare
    sys.argv[:] = [old[0]]
    try:
        spec.loader.exec_module(m)
    finally:
        sys.argv[:] = old
        HK.run_compare = cmp0
    return m


def T(v):
    return tmod(os.path.join(HERE, "test_skyycollections_%s.py" % v), "tco" + v.replace(".", ""))


def P_(n):
    from jpype import JClass
    return JClass(PKG + n)


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.count('VERSION = "0.2.36"') == 1 and '[SkyyCollections] 0.2.36 ready (' in g, "S version + ready line")
    for w in ("registerSystem(", "registerCommand(", ' = K("'):
        K.eq(g.count(w), o.count(w), "S no new %s" % w.strip())
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), ([], []), "S no jar entry added or removed")
    K.eq(sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n)), ["manifest.json"], "S the only non-class change is the manifest")
    K.check("_secret.crystal" in g and g.count("setMeta(") == o.count("setMeta(") and g.count("saveKeySoon(") == o.count("saveKeySoon("),
            "S no saved-data write added")
    K.save()


def run_rbg(out, jar, scratch, _home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Page, Msg = P_("CollPage"), P_("CollMsg")
    for h, ok, want in (("#a335ee", True, "#a335ee(0.4)"), ("#bb8a2c", True, "#bb8a2c(0.4)"), ("#CC66CC", True, "#CC66CC(0.4)"),
                        ("#2770b7", False, NONE), ("#c8f0a0", True, NONE), ("#C8F0A0", True, NONE), (None, True, NONE), (None, False, NONE),
                        ("#12345", True, NONE), ("#1234567", True, NONE)):
        K.eq(str(Page.rbg(h, ok)), want, "Q rbg(%r, %s)" % (h, ok))
    K.eq(str(Msg.rarityHex("No_Such_Item_Recipe_Generated_0")), "#c8f0a0", "Q rarityHex in a bare JVM = its fallback (so every page row here is grey)")
    K.eq(str(Page.rbg(Msg.rarityHex("No_Such_Item_Recipe_Generated_0"), True)), NONE, "Q an output with no quality = the faint grey")
    K.save()


def rec_rows(cmds):
    """{i: the row markup} of every appended recipe row #SkyyCPr<i>"""
    out = {}
    for ty, s, t, d in cmds:
        if t and s == "#SkyyCRecs":
            m = re.match(r"Group #SkyyCPr(\d+) ", t)
            if m:
                out[int(m.group(1))] = t
    return out


def row_checks(K, E, P, pg, built, t23, what, locked):
    Page, Msg = P_("CollPage"), P_("CollMsg")
    rows = rec_rows(built[0])
    n = len(pg.prid)
    gk = int(pg.gk)
    K.check(n > 0 and sorted(rows) == list(range(n)), "%s: %d recipe rows appended (%s)" % (what, n, sorted(rows)[:6]))
    bad, cols = [], []
    for i in range(n):
        mk = rows.get(i, "")
        rid = str(pg.prid[i])
        ok = i not in locked
        want = str(Page.rbg(Msg.rarityHex(rid) if ok else None, ok))
        cols.append(want)
        qa = mk.count("Group #SkyyCPr%dQ " % i)
        qm = re.search(r"Group #SkyyCPr%dQ \{([^{}]*)\}" % i, mk)
        q = qm.group(1) if qm else ""
        rh = ROW_H[gk]
        cg, cq, cn = mk.find("#SkyyCPr%dG " % i), mk.find("#SkyyCPr%dQ " % i), mk.find("#SkyyCPr%dN " % i)
        first = re.search(r"#(SkyyCPr%d[A-Z]\w*) " % i, mk)
        if qa != 1 or not (0 <= cg < cq < cn):
            bad.append((i, "tag, then one square, then the name"))
        elif not first or first.group(1) !="SkyyCPr%dG" % i:   # fix round: the tag is the row's FIRST cell = under the Tier head
            bad.append((i, "the tag first", first.group(1) if first else None))
        elif ("Background: %s;" % want) not in q:
            bad.append((i, "colour", q))
        elif not ("Width: 10" in q and "Height: 10" in q and ("Top: %d" % ((rh - 10) // 2)) in q and "Right: 4" in q):
            bad.append((i, "size / place", q))
        nm = re.search(r"Label #SkyyCPr%dN \{.*?TextColor: (#[0-9a-fA-F]{6})" % i, mk)
        if not nm or nm.group(1).lower() != (SUI.COLOR["disabled"] if not ok else SUI.COLOR["rowName"]).lower():
            bad.append((i, "name colour", nm.group(1) if nm else None))
        if "Padding: (Left: 8)" not in mk[:mk.find("#SkyyCPr%dQ " % i)]:
            bad.append((i, "row padding 8"))
        gm = re.search(r"Label #SkyyCPr%dG \{ Anchor: \(Width: (\d+)" % i, mk)
        if not gm or int(gm.group(1)) != 34:
            bad.append((i, "tag 34 px", gm.group(1) if gm else None))
    K.check(not bad, "%s: every row = its 34 px tag first (under the Tier head), then one 10 x 10 square (Top %d, 4 px before the name) in rbg(rarityHex(recipe), ok), the name white / grey, padding 8: %s"
            % (what, (ROW_H[gk] - 10) // 2, bad[:3]))
    if locked:
        K.check(all(cols[i] == NONE for i in locked), "%s: the locked row(s) %s = the faint grey %s" % (what, sorted(locked), NONE))
    t23.pcheck(K, built, what)
    return rows


def run_page(out, jar, scratch, _home):
    from jpype import JClass, JString, JArray
    K = HK.Child(out)
    t23 = T("0.2.23")
    E, Reg, Store, P = t23.stage_player(K, scratch, jar, "rar", "00000000-0000-0000-0000-0000000036d1")
    u = P.pr.getUuid()
    R = Reg.D
    HM, Long = JClass("java.util.HashMap"), JClass("java.lang.Long")
    Page = P_("CollPage")
    K.eq((int(Page.RPNAME), int(Page.RPNAME2)), (200, 340), "M the name cell 208 -> 200 px (two lines 340)")
    c = int(R.byId.get("wheat"))
    rc = {1: ["Ingredient_Bar_Iron_Recipe_Generated_0", "Zzz_Thing_Recipe_Generated_0"],
          2: ["Armor_Copper_Head_Recipe_Generated_0", "Armor_Copper_Chest_Recipe_Generated_0"],
          3: ["Ingredient_Bar_Iron_Recipe_Generated_0"], 5: ["Tool_Pickaxe_Mithril_Recipe_Generated_0"]}
    m = HM()
    for t, rs in rc.items():
        m.put("%d.%d" % (c, t), t23.jstrs(rs))
    Reg.RECIPES = m
    d = Store.data(u)
    d.items.put(str(R.items[c][0]), Long.valueOf(int(Reg.threshold(R, c, 2))))
    E.CM.cmds.put("craft", E.U.allocateInstance(JClass("skyymenu19.Cmd").class_))
    pg = t23.open_coll(E, P, c)
    built = t23.HT.build(pg, P)
    sets = t23.sets_of(built[0])
    K.eq(t23.txt(sets, "#SkyyCPr4S.Text"), "Tier V", "M row 4 = the locked Mithril pickaxe")
    K.eq(int(pg.gk), 2, "M 5 recipes = the 64 px rows")
    row_checks(K, E, P, pg, built, t23, "M Wheat (4 CRAFT rows + 1 locked, 64 px)", {4})
    # without /craft: the "Known" rows (the other row template) carry the square too
    E.CM.cmds.remove("craft")
    pg = t23.open_coll(E, P, c)
    built = t23.HT.build(pg, P)
    K.eq([t23.txt(t23.sets_of(built[0]), "#SkyyCPr%dS.Text" % i) for i in range(5)], ["Known"] * 4 + ["Tier V"], "M no /craft: Known x 4 + Tier V")
    row_checks(K, E, P, pg, built, t23, "M Wheat (Known rows)", {4})
    # 21 rows, a long name: the 46 px rows (the 0.2.29 two-line rule on the 192 px cell)
    E.CM.cmds.put("craft", E.U.allocateInstance(JClass("skyymenu19.Cmd").class_))
    m = HM()
    long_id = "Skyy_Test_Ceremonial_Harvest_Lantern_Recipe_Generated_0"
    m.put("%d.1" % c, JArray(JString)([long_id] + ["Zz_Item%02d_Recipe_Generated_0" % i for i in range(20)]))
    Reg.RECIPES = m
    pg = t23.open_coll(E, P, c)
    built = t23.HT.build(pg, P)
    K.eq(int(pg.gk), 1, "M a long name: the 46 px rows")
    rows = row_checks(K, E, P, pg, built, t23, "M Wheat (21 rows, 46 px)", set())
    nm = str(P_("CollUtil").prettyRecipe(long_id))
    shown = [t23.txt(t23.sets_of(built[0]), "#SkyyCPr%dN.Text" % i) for i in range(21)]
    K.check(any(x and str(x).endswith(nm) for x in shown), "M the long name shows whole: %s" % nm)
    hd = [t for ty, s, t, dd in built[0] if t and s == "#SkyyCDRight" and "SkyyCPHead" in t]
    K.check(bool(hd) and "Padding: (Left: 12)" in hd[0] and re.search(r"Width: 48, Height: 30\); Text: \"Tier\"", hd[0]) is not None
            and re.search(r"Width: 200, Height: 30\); Text: \"Recipe\"", hd[0]) is not None,
            "M the column heads: Tier 48 px (tag + square), Recipe 200, padding unchanged: %s" % (hd[0][:260] if hd else None))
    # fix round (critic 1): the Tier head text starts where every tag starts = head padding 12 == well pad + row pad, tag = first cell
    K.eq(int(SUI.WELL_LIST_PAD) + 8, 12, "M fix: the Tier head (Padding Left 12) and the tag (well pad %d + row pad 8) share one left edge" % SUI.WELL_LIST_PAD)
    K.save()


def run_fit(out, jar, scratch, home):
    T("0.2.29").run_fit(out, jar, scratch, home)


def run_live(out, jar, scratch, home):
    T("0.2.35").run_live(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run(name="SkyyCollections", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("rbg", run_rbg), ("page", run_page), ("fit", run_fit), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyCollections"))
