"""Harness for SkyyCollections 0.2.22 (round hubcoll: Collections + Recipes = one Character hub tab - recipes shown inside each collection;
tools/collections_0_2_22_patch.py). Build first:
    python tools/collections_0_2_22_patch.py && python SkyyCollections/build_skyycollections_0.2.22.py

    python SkyyCollections/test_skyycollections_0.2.22.py [--jar <SkyyCollections-0.2.22.jar>] [--dir <scratch>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py; the hub phases on tools/hub_tab_kit.py's engine stand-ins - the REAL PageManager,
UICommandBuilder / UIEventBuilder, a CommandManager that records lines - with -Xverify:all):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.2.21 -> 0.2.22: exactly the listed members differ (+ CollTier, CollRecipesCmd); non-class entries: only manifest.json
  M    merge    EXECUTED on a REAL registry (CollReg.loadAll on a scratch folder) + a real counts file, recipe unlocks injected (CollReg.RECIPES)
               for one collection at tiers 1 / 2 / 3 / 5 (a tiered ingot, an untiered item, two Copper armor pieces, a Mithril pickaxe, the
               ingot again at tier 3 = shown once):
       HOME  every view a valid hub page (hub_tab_kit.page_check); Home has no Unlocked / Locked recipes buttons; an old "crecipes" /
             "clocked" click changes nothing
       LIST  the collection page (tier 2): the recipe list next to the tier table, sorted tier then name (untiered first), the tags, locked
             rows grey with "Tier III" / "Tier V", unlocked rows CRAFT (with /craft) or "Known" (without), NEW before the names while the
             tier's NEW marker is up (cleared after the page showed it), the tier cells say "N recipes" and fit their width
       CRAFT a CRAFT click runs "craft <words>" as the player (the recorded command line); a forged click on a locked row / a stale row /
             no /craft = the page stays with a red result line; Back = the category
       NONE  a collection with no recipe = the one grey line
       CMD   /recipes: name, no alias, the Adventurer group, extra words allowed; execute() EXECUTED with a real CommandContext:
             /recipes = Home, /recipes <name> = that collection, /recipes <unknown> = Home + one chat line; setup registers it (bytecode)
       FIT   on the shipped default rewards (every visible collection x tier, the recipe tokens as the recipe unlocks): every tier cell
             text fitted to the 560 px cell (CollCraft.fitPx); at most 6 lose their last parts (the two-armor tier-up tiers)
  D    live     the setup's file steps TWICE on a scratch COPY of the live Skyy_SkyyCollections (no file changes: 0.2.21 is live), then the recipe
               unlocks rebuilt from the live rewards + every live profile's every visible collection page built (the recipe list sorted,
               every b.set / binding names an element)
  AA   audit    the engine-access audit
  FIX  (fix round) B1 the crop families inside a tier (crop, Enchanted, seeds, Eternal seeds, then the rest; the Omni accessory last);
       B3 a list over PRMAX ends with "+N more", exactly PRMAX has none, no live collection exceeds PRMAX
Scratch: tools/dev/scratch/hubcoll/coll (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, re, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "ci"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW
import hub_tab_kit as HT
import skyyui as SUI

VERSION = "0.2.22"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCollections-0.2.21.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "hubcoll", "coll")))
PKG = "com.skyy.collections."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyCollections")
EXPECT = {
    "CollPage": ["+f PRMAX", "+f RPNAME", "+f TIERREW", "+f TIERREW2", "+f prid", "+m recipeCraft", "+m recipePanel", "+m recipeRows",
                 "-f CRAFTREW", "-f LISTBACK", "-f RLROWS", "-f back", "-f fcol", "-f ftier", "-f rcol", "-f rpage", "-f rrid",
                 "-m buildRecipes", "-m craftClick", "-m lockCmp", "-m lockedRows", "-m rowCraft", "-m rowOpen", "-m unlockedRows",
                 "~m build", "~m buildCat", "~m buildDetail", "~m buildHome", "~m card", "~m catCard", "~m handleDataEvent"],   # + the 130 px wider body
    "CollReg": ["+m rewardTextP"],
    "SkyyCollectionsPlugin": ["~m setup"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],      # the kit's version texts
}
ADDED = ["CollTier", "CollRecipesCmd"]
FAIL_TEXT = "That tab could not open right now - try again."


def P_(n):
    from jpype import JClass
    return JClass(PKG + n)


def jstrs(xs):
    from jpype import JArray, JString
    return JArray(JString)(list(xs))


def ids_of(cmds):
    out = set()
    for ty, s, t, d in cmds:
        if t:
            out |= set(m.group(2) for m in HT.DECL_RE.finditer(t))
    return out


def sets_of(cmds):
    return dict((s, d) for ty, s, t, d in cmds if ty == "Set")


def txt(sets, sel):
    """the text a b.set line sends: the builder's data is JSON {"0": <value>}"""
    import json
    v = sets.get(sel)
    if v is None:
        return None
    try:
        j = json.loads(str(v))
        return j.get("0") if isinstance(j, dict) else j
    except ValueError:
        return str(v)


def binds(evs):
    return dict((s, t) for s, t in evs)


def stage_player(K, scratch, jar, sub, uid):
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    Reg, Store = P_("CollReg"), P_("CollStore")
    base = os.path.join(scratch, sub, "Skyy_SkyyCollections")
    os.makedirs(base, exist_ok=True)
    Reg.BASE = E.Paths.get(base)
    Store.DIR = Reg.BASE.resolve("counts")
    Reg.loadAll()
    K.check(Reg.D is not None and int(Reg.D.n) > 50, "the registry loaded (%s collections)" % (None if Reg.D is None else int(Reg.D.n)))
    P = E.mkp(E.UUID.fromString(uid), "CollMerge")
    P_("CollHubOpen").register()
    return E, Reg, Store, P


def open_coll(E, P, c):
    P_("CollPage").openFor(P.pr, P.st, P.ref, c)
    E.pump(P)
    return E.pg(P)


def click(E, P, pg, word):
    pg.handleDataEvent(P.ref, P.st, '{"a":"%s"}' % word)
    E.pump(P)
    return E.pg(P)


# ------------------------------------------------------------------------------------------------------------------- M: the merge
def run_merge(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    E, Reg, Store, P = stage_player(K, scratch, jar, "merge", "00000000-0000-0000-0000-0000000000d2")
    u = P.pr.getUuid()
    R = Reg.D
    Tier, Page, New, Unl, Craft = P_("CollTier"), P_("CollPage"), P_("CollNew"), P_("CollUnlocks"), P_("CollCraft")
    HM, Long = JClass("java.util.HashMap"), JClass("java.lang.Long")
    # ---------------------------------------------------------------- CollTier on its own (tools/tier_tags.py + the metal words)
    K.eq([int(Tier.tierKey(i)) for i in ("Ingredient_Bar_Iron", "Armor_Copper_Head", "Tool_Pickaxe_Mithril", "Zzz_Thing", "Skyy_Acc_Lucky_T4", "Skyy_X_Rare")],
         [3, 2, 7, 0, 4, 3], "TIER tierKey: table / metal word / metal word / untiered / own _T4 / rarity word")
    K.eq([str(Tier.tierText(i)) for i in ("Ingredient_Bar_Iron", "Armor_Copper_Head", "Zzz_Thing", "Skyy_Acc_Lucky_T4", "Skyy_X_Rare")],
         ["T3", "T2", "", "T4", ""], "TIER tierText: T3 / T2 / none / T4 / none (a rarity word is no ladder tier)")
    K.eq(str(Tier.itemOf("Armor_Copper_Head_Recipe_Generated_0")), "Armor_Copper_Head", "TIER itemOf strips _Recipe_Generated_<n>")
    # ---------------------------------------------------------------- the collection + its injected recipe unlocks
    c = int(R.byId.get("wheat"))
    none_c = int(R.byId.get("oaklog"))
    rc = {1: ["Ingredient_Bar_Iron_Recipe_Generated_0", "Zzz_Thing_Recipe_Generated_0"],
          2: ["Armor_Copper_Head_Recipe_Generated_0", "Armor_Copper_Chest_Recipe_Generated_0"],
          3: ["Ingredient_Bar_Iron_Recipe_Generated_0"], 5: ["Tool_Pickaxe_Mithril_Recipe_Generated_0"]}
    m = HM()
    for t, rs in rc.items():
        m.put("%d.%d" % (c, t), jstrs(rs))
    Reg.RECIPES = m
    d = Store.data(u)
    it = str(R.items[c][0])
    d.items.put(it, Long.valueOf(int(Reg.threshold(R, c, 2))))
    K.eq(int(Reg.tierOf(R, c, Store.sum(d, R, c))), 2, "M the player is at Wheat tier 2")
    un = Unl.compute(d)
    K.check(un.contains("Armor_Copper_Head_Recipe_Generated_0") and un.contains("Zzz_Thing_Recipe_Generated_0") and not un.contains("Tool_Pickaxe_Mithril_Recipe_Generated_0"),
            "M coll:recipes (CollUnlocks.compute) = the tier 1 + 2 recipes, not tier 5's")
    key = str(P_("CollUtil").pkey(u))
    New.mark(d, key, R, c, 1, 2)
    rows = Page.recipeRows(d, R, c, 2, un)
    got = [(str(e[0]).replace("_Recipe_Generated_0", ""), str(e[2]), int(e[3]), bool(e[5]), int(e[6])) for e in rows]
    want = [("Zzz_Thing", "", 0, True, 1), ("Armor_Copper_Chest", "T2", 2, True, 2), ("Armor_Copper_Head", "T2", 2, True, 2),
            ("Ingredient_Bar_Iron", "T3", 3, True, 1), ("Tool_Pickaxe_Mithril", "T7", 7, False, 5)]
    K.eq(got, want, "LIST recipeRows: tier then name (untiered first), each recipe once at its lowest tier, unlocked = in coll:recipes")
    K.check(all(str(e[1]).startswith("NEW  ") for e in rows if int(e[6]) <= 2) and not str(rows[4][1]).startswith("NEW"),
            "LIST the NEW marker of tiers 1-2 shows before those names (%s)" % [str(e[1]) for e in rows])
    for tt, n_r in ((1, 2), (2, 2), (3, 1), (4, 0)):
        tx = str(Reg.rewardTextP(R, c, tt, False))
        full = str(Reg.rewardTextB(R, c, tt, False))
        parts = full.split(" - ")
        tail = " - ".join(parts[n_r:]) if n_r else full
        exp = (("%d recipe%s" % (n_r, "" if n_r == 1 else "s")) + ((" - " + tail) if tail else "")) if n_r else full
        K.eq(tx, exp, "LIST rewardTextP tier %d = the recipes by count + rewardTextB's other parts word for word" % tt)
    # ---------------------------------------------------------------- FIX B1: the crop families inside a tier (RecipeCmp's order)
    K.eq(int(Tier.tierKey("Skyy_Acc_Lucky_Omni")), 99, "FIXB1 the Omni accessory sorts after every tier (RecipeCmp.tierKey)")
    fam = ["Ore_Copper", "Plant_Seeds_Wheat_Eternal", "Ingredient_Bar_Copper", "Skyy_Ench_Wheat", "Plant_Crop_Carrot_Item",
           "Plant_Seeds_Wheat", "Plant_Crop_Wheat_Item"]
    m3 = HM()
    m3.put("%d.1" % c, jstrs([x + "_Recipe_Generated_0" for x in fam]))
    Reg.RECIPES = m3
    frows = Page.recipeRows(d, R, c, 2, JClass("java.util.TreeSet")())
    fgot = [str(e[0]).replace("_Recipe_Generated_0", "") for e in frows]
    rest = sorted(["Ore_Copper", "Ingredient_Bar_Copper"], key=lambda x: (str(P_("CollUtil").prettyRecipe(x + "_Recipe_Generated_0")).lower() + " " + x))
    K.eq(fgot, ["Plant_Crop_Wheat_Item", "Skyy_Ench_Wheat", "Plant_Seeds_Wheat", "Plant_Seeds_Wheat_Eternal"] + rest + ["Plant_Crop_Carrot_Item"],
         "FIXB1 Wheat-like list: inside T2 the crop family first (crop, Enchanted, seeds, Eternal seeds), then the rest by name; T3 Carrot after")
    K.eq([str(e[2]) for e in frows], ["T2"] * 6 + ["T3"], "FIXB1 the tags of the crop-family rows")
    Reg.RECIPES = m
    # ---------------------------------------------------------------- HOME / views as hub pages
    E.CM.cmds.put("craft", E.U.allocateInstance(JClass("skyymenu19.Cmd").class_))
    E.CM.lines.clear()
    pg = open_coll(E, P, -1)
    K.check(pg is not None and int(pg.view) == 0, "HOME /collections opens Home")
    built = HT.build(pg, P)
    HT.page_check(K, E, P, built, "SkyyCollF", "character", "collections", "Collections", "HOME", idp="SkyyC")
    hid = ids_of(built[0])
    K.check("SkyyCRecipes" not in hid and "SkyyCLocked" not in hid and "SkyyCRefresh" in hid and "SkyyCClose" in hid,
            "HOME no Unlocked / Locked recipes buttons (Refresh + Close stay)")
    K.check("Open one to see its tiers and the recipes it unlocks." in str(txt(sets_of(built[0]), "#SkyyCHint.Text") or ""),
            "HOME the hint names the recipes inside each collection")
    for old in ("crecipes", "clocked", "crgo0", "crcraft0", "ccraft1", "crprev"):
        cur = click(E, P, pg, old)
        K.check(E.same(cur, pg) and int(pg.view) == 0, "HOME an old 0.2.8 click '%s' changes nothing" % old)
    click(E, P, pg, "ccat0")
    K.check(int(pg.view) == 1, "HOME the category opens (view 1)")
    HT.page_check(K, E, P, HT.build(pg, P), "SkyyCollF", "character", "collections", "Collections", "CATEGORY", idp="SkyyC")
    # ---------------------------------------------------------------- LIST: the collection page
    pg = open_coll(E, P, c)
    K.check(pg is not None and int(pg.view) == 2 and int(pg.coll) == c, "LIST /collections wheat = the Wheat page (view 2)")
    New.mark(d, key, R, c, 1, 2)          # opening built the page once (that showing cleared them): up again for this build
    built = HT.build(pg, P)
    w, h, sets, evs = HT.page_check(K, E, P, built, "SkyyCollF", "character", "collections", "Collections", "LIST", idp="SkyyC")
    K.eq((w, h), (1264, 892), "LIST the 1264 x 892 hub window (0.2.21: 1134; the heights unchanged)")
    sets = sets_of(built[0])
    bd = binds(evs)
    names = [txt(sets, "#SkyyCPr%dN.Text" % i) for i in range(5)]
    K.eq([n[5:] if n and n.startswith("NEW  ") else n for n in names],
         [str(P_("CollUtil").prettyRecipe(r)) for r in ("Zzz_Thing_Recipe_Generated_0", "Armor_Copper_Chest_Recipe_Generated_0", "Armor_Copper_Head_Recipe_Generated_0",
                                                          "Ingredient_Bar_Iron_Recipe_Generated_0", "Tool_Pickaxe_Mithril_Recipe_Generated_0")],
         "LIST the 5 rows in tier-then-name order (%s)" % names)
    K.check(all(n.startswith("NEW  ") for n in names[:4]), "LIST NEW before the 4 unlocked names (their tiers were just reached)")
    K.eq([txt(sets, "#SkyyCPr%dG.Text" % i) for i in range(5)], ["", "T2", "T2", "T3", "T7"], "LIST the tier tags")
    K.check(all(("#SkyyCPr%dGo" % i) in bd and "cpk%d" % i in bd["#SkyyCPr%dGo" % i] for i in range(4)) and "#SkyyCPr4Go" not in bd,
            "LIST the 4 unlocked rows have CRAFT (cpk<i>), the locked one none")
    K.eq(txt(sets, "#SkyyCPr4S.Text"), "Tier V", "LIST the locked Mithril pickaxe: 'Tier V'")
    rowmk = [t for ty, s, t, dd in built[0] if t and "#SkyyCPr4 " in t][:1]
    K.check(bool(rowmk) and rowmk[0].count(SUI.COLOR["disabled"]) >= 3, "LIST the locked row is greyed (tag, name, state in the disabled grey)")
    tiers = int(Reg.maxTier(R, c))
    rew = [txt(sets, "#SkyyCRew%d.Text" % t) for t in range(1, tiers + 1)]
    K.check(rew[0].startswith("2 recipes") and rew[1].startswith("2 recipes") and rew[2].startswith("1 recipe") and not rew[3].startswith("1 recipe")
            and all(int(Craft.width(x)) <= int(Page.TIERREW2) * 1000 and not x.endswith("...") for x in rew), "LIST the tier cells: recipes by count, none cut (%s)" % (rew[:3],))
    tallrows = [t for t in range(1, tiers + 1) if any(tx_ and ("#SkyyCTr%d { Anchor: (Height: 46," % t) in tx_ for ty_, s_, tx_, d_ in built[0])]
    widen = [t for t in range(1, tiers + 1) if int(Craft.width(rew[t - 1])) > int(Page.TIERREW) * 1000]
    K.check(bool(widen) and tallrows == widen, "FIXB4 a tier text wider than %d px gets the two-line row, the others one line (wide %s, tall rows %s)" % (int(Page.TIERREW), widen, tallrows))
    K.check(all(rew[t - 1] == str(Reg.rewardTextP(R, c, t, False)) for t in widen), "FIXB4 the two-line rows show their whole text (%s)" % [rew[t - 1] for t in widen])
    K.check("#SkyyCTr1Go" not in bd and not any("ccraft" in t for t in bd.values()), "LIST the tier rows have no CRAFT button any more")
    K.check(int(P_("CollStore").meta(d, New.mkey(R, c))) == 0, "LIST the NEW markers are cleared once the page showed them")
    built2 = HT.build(pg, P)
    K.check(not str(txt(sets_of(built2[0]), "#SkyyCPr1N.Text")).startswith("NEW"), "LIST the next build shows no NEW")
    # ---------------------------------------------------------------- CRAFT
    E.CM.lines.clear()
    q0 = str(Craft.query(jstrs(["Armor_Copper_Chest_Recipe_Generated_0"]), un))
    cur = click(E, P, pg, "cpk1")
    K.eq([str(x) for x in E.CM.lines], ["craft " + q0], "CRAFT row 1 (Copper chest) runs /craft searching for it as the player")
    pg = open_coll(E, P, c)
    HT.build(pg, P)
    E.CM.lines.clear()
    cur = click(E, P, pg, "cpk4")
    K.check(E.same(cur, pg) and not list(E.CM.lines) and str(pg.status) == "That recipe is not unlocked yet."
            and str(pg.statusColor(pg.status)) == SUI.COLOR["error"], "CRAFT a forged click on the locked row: nothing runs, a red 'not unlocked yet'")
    cur = click(E, P, pg, "cpk9")
    K.check(E.same(cur, pg) and not list(E.CM.lines) and str(pg.status) == "That recipe is not on this page any more.", "CRAFT a stale row: the page says so")
    cur = click(E, P, pg, "cback")
    K.check(int(pg.view) == 1, "CRAFT Back from the collection = its category")
    E.CM.cmds.remove("craft")
    pg = open_coll(E, P, c)
    built = HT.build(pg, P)
    sets, bd = sets_of(built[0]), binds(built[1])
    K.check([txt(sets, "#SkyyCPr%dS.Text" % i) for i in range(5)] == ["Known"] * 4 + ["Tier V"] and not any(k.endswith("Go") and "SkyyCPr" in k for k in bd),
            "CRAFT no /craft on the server: the unlocked rows say 'Known', no CRAFT button")
    HT.page_check(K, E, P, built, "SkyyCollF", "character", "collections", "Collections", "LIST (no /craft)", idp="SkyyC")
    E.CM.lines.clear()
    cur = click(E, P, pg, "cpk0")
    K.check(not list(E.CM.lines) and str(pg.status) == "Crafting (/craft) is not on this server.", "CRAFT a forged click without /craft: the page says so (%s)" % pg.status)
    E.CM.cmds.put("craft", E.U.allocateInstance(JClass("skyymenu19.Cmd").class_))
    # ---------------------------------------------------------------- NONE
    pg = open_coll(E, P, none_c)
    built = HT.build(pg, P)
    HT.page_check(K, E, P, built, "SkyyCollF", "character", "collections", "Collections", "NONE", idp="SkyyC")
    sets = sets_of(built[0])
    K.check("SkyyCPrNone" in ids_of(built[0]) and "unlocks no recipes" in str(txt(sets, "#SkyyCPrNone.Text")) and int(len(pg.prid)) == 0,
            "NONE a collection without recipes: the one grey line, no rows")
    # 40+ recipes: the list stops at PRMAX rows, the click loop's bound
    m2 = HM()
    m2.put("%d.1" % c, jstrs(["Zz_Item%02d_Recipe_Generated_0" % i for i in range(45)]))
    Reg.RECIPES = m2
    pg = open_coll(E, P, c)
    built = HT.build(pg, P)
    HT.page_check(K, E, P, built, "SkyyCollF", "character", "collections", "Collections", "LIST 45", idp="SkyyC")
    K.check(int(len(pg.prid)) == int(Page.PRMAX) == 40 and "SkyyCPr39" in ids_of(built[0]) and "SkyyCPr40" not in ids_of(built[0]),
            "LIST 45 recipes: 40 rows (PRMAX), scrolling")
    K.eq(txt(sets_of(built[0]), "#SkyyCPrMore.Text"), "+5 more - /craft lists every recipe", "FIXB3 45 recipes: the list ends with '+5 more' (no silent cut)")
    m2.put("%d.1" % c, jstrs(["Zz_Item%02d_Recipe_Generated_0" % i for i in range(40)]))
    pg = open_coll(E, P, c)
    built = HT.build(pg, P)
    HT.page_check(K, E, P, built, "SkyyCollF", "character", "collections", "Collections", "LIST 40", idp="SkyyC")
    K.check(int(len(pg.prid)) == 40 and "SkyyCPrMore" not in ids_of(built[0]), "FIXB3 exactly 40 recipes: 40 rows, no '+N more' line")
    Reg.RECIPES = m
    # ---------------------------------------------------------------- CMD: /recipes
    Cmd = P_("CollRecipesCmd")
    rcmd = Cmd()
    K.eq((str(rcmd.getName()), sorted(str(a) for a in (rcmd.getAliases() or []))), ("recipes", []), "CMD /recipes, no alias")
    try:
        K.eq(sorted(str(g) for g in rcmd.getPermissionGroups()), ["hytale:Adventurer"], "CMD the Adventurer group")
    except AttributeError:
        K.notes.append("CMD no permission-group getter on this engine (lint perm rules + the bytecode below)")
    K.eq([str(Cmd.words(x)) for x in ("/recipes", "recipes", "/recipes wheat", "recipes  oak log ", "/RECIPES Wheat")],
         ["", "", "wheat", "oak log", "Wheat"], "CMD words(): the command word dropped")
    Ctx = JClass("com.hypixel.hytale.server.core.command.system.CommandContext")
    ex = [mm for mm in Cmd.class_.getDeclaredMethods() if str(mm.getName()) == "execute" and len(mm.getParameterTypes()) == 5][0]
    ex.setAccessible(True)
    for line, view, coll, chat in (("recipes", 0, None, False), ("recipes wheat", 2, c, False), ("recipes nosuchthing", 0, None, True)):
        n0 = len(E.sent(P))
        ex.invoke(rcmd, Ctx(rcmd, P.pr, line), P.st, P.ref, P.pr, None)
        E.pump(P)
        pg = E.pg(P)
        said = "no collection matches nosuchthing" in E.strs_of(P, n0)
        K.check(pg is not None and str(pg.getClass().getName()) == PKG + "CollPage" and int(pg.view) == view and (coll is None or int(pg.coll) == coll) and said == chat,
                "CMD execute '/%s': the Collections page, view %d%s%s" % (line, view, "" if coll is None else " (Wheat)", ", one chat line" if chat else ""))
    g = PW.calls(jar)
    K.check(PKG + "CollRecipesCmd.<init>" in g.get("SkyyCollectionsPlugin.setup", set()), "CMD setup() registers /recipes (bytecode)")
    cc = g.get("CollRecipesCmd.<init>", set())
    K.check(any(x.endswith(".setPermissionGroups") for x in cc) and any(x.endswith(".setAllowsExtraArguments") for x in cc) and not any(x.endswith(".addAliases") for x in cc),
            "CMD the constructor: setPermissionGroups + setAllowsExtraArguments, no alias (bytecode)")
    # ---------------------------------------------------------------- FIT: the shipped defaults
    Reg.RECIPES = HM()
    out_ = HM()
    for cc_ in range(int(R.n)):
        for t in range(1, int(Reg.maxTier(R, cc_)) + 1):
            toks = Reg.REWARDS.get(str(R.id[cc_]).lower() + "." + str(t))
            rs = [str(x)[7:] for x in (toks or []) if str(x).startswith("recipe:")]
            if rs:
                out_.put("%d.%d" % (cc_, t), jstrs(rs))
    try:
        P_("CollEnch").merge(out_, R, P_("CollEnch").present())
    except Exception as e:
        K.notes.append("FIT: CollEnch.merge on the stand-in engine: %s" % e)
    Reg.RECIPES = out_
    lim = int(Page.TIERREW) * 1000
    n_all, cut, widest = 0, [], (0, "")
    HIST = []
    for cc_ in range(int(R.n)):
        if bool(R.hidden[cc_]):
            continue
        for t in range(1, int(Reg.maxTier(R, cc_)) + 1):
            tx = str(Reg.rewardTextP(R, cc_, t, False))
            n_all += 1
            wpx = int(Craft.width(tx))
            widest = max(widest, (wpx, tx))
            HIST.append((wpx, int(Craft.width(" - ".join(x_ for x_ in tx.split(" - ") if not x_.endswith("tier-up"))))))
            f = str(Craft.fitPx(tx, int(Page.TIERREW)))
            K.check(int(Craft.width(f)) <= lim, "FIT %s %d fitted (%s)" % (R.id[cc_], t, f))
            if f != tx:
                cut.append("%s %d: %s" % (R.id[cc_], t, tx))
                print("FIT CUT %s %d (%.0f px): %s  ->  %s" % (R.id[cc_], t, wpx / 1000.0, tx, f))
    K.check(n_all > 500, "FIT %d tier texts of the default rewards measured" % n_all)
    K.check(len(cut) <= 6 and all("tier-up - " in x for x in cut), "FIT at most 6 default tier texts are too wide for one line, each a two-tier-up tier (%s)" % cut[:6])
    cut2 = [x for x in cut if str(Craft.fitPx(x.split(": ", 1)[1], int(Page.TIERREW2))) != x.split(": ", 1)[1]]
    K.check(not cut2, "FIXB4 every default tier text fits its row whole (the wide ones in two lines, %d px): %s" % (int(Page.TIERREW2), cut2[:3]))
    K.notes.append("FIT: %d of %d default tier texts are cut to fit %d px (whole ' - ' parts from the end); widest %.0f px: %s; e.g. %s" % (
        len(cut), n_all, int(Page.TIERREW), widest[0] / 1000.0, widest[1], cut[:3]))
    print("FIT: %d of %d cut; widest %.0f px" % (len(cut), n_all, widest[0] / 1000.0))
    for lim_ in (430, 480, 520, 560, 600, 650, 700):
        print("FIT HIST >%d px: %d (without tier-ups %d)" % (lim_, sum(1 for a, b in HIST if a > lim_ * 1000), sum(1 for a, b in HIST if b > lim_ * 1000)))
    # ---------------------------------------------------------------- the page id the build checked
    gen = open(os.path.join(HERE, "build_skyycollections_%s.py" % VERSION), encoding="utf8").read()
    mm_ = re.search(r'COLL_PAGE_CHECKED = "([0-9a-z]+)"', gen)
    plug = zipfile.ZipFile(jar).read("com/skyy/collections/SkyyCollectionsPlugin.class")
    pid = re.search(rb", page ([0-9a-f]{12})", plug)
    K.notes.append("PAGE id in the jar: %s; COLL_PAGE_CHECKED: %s" % (pid.group(1).decode() if pid else None, mm_.group(1) if mm_ else None))
    K.check(mm_ is not None and pid is not None and pid.group(1).decode() == mm_.group(1),
            "PAGE the jar's page id (ready line) = COLL_PAGE_CHECKED (the page this harness passed on): %s vs %s" % (pid.group(1) if pid else None, mm_.group(1) if mm_ else None))
    K.save()


# ------------------------------------------------------------------------------------------------------------------- D: live copy, twice
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    Reg, Store = P_("CollReg"), P_("CollStore")
    b_ = E.Paths.get(home)
    h0 = HK.tree_hash(home)
    msgs, hs = [], []
    for start in (1, 2):
        Reg.BASE = b_
        Store.DIR = b_.resolve("counts")
        r = [str(P_("CollBagMigrate").run(b_)), str(P_("CollBypassMig").run(b_)), str(P_("CollCoinMig").run(b_))]
        Reg.loadAll()
        r += [str(P_("CollCobMig").run(b_)), str(P_("CollSigMig").run(b_)), str(P_("CollShardMig").run(b_)), str(P_("CollToolMig").run(b_)),
              str(P_("CollRw21Mig").run(b_))]
        msgs.append(r)
        hs.append(HK.tree_hash(home))
    K.check(hs[0] == h0 and hs[1] == h0, "D both starts change no file of the live copy (%d files; 0.2.21 is live - nothing to migrate)" % len(h0))
    K.check(all(x in ("", "None") or "nothing" in x.lower() or "already" in x.lower() for x in msgs[1]), "D the 2nd start: every step says nothing (%s)" % [x[:60] for x in msgs[1] if x])
    R = Reg.D
    # the recipe unlocks as the start-up check makes them in game (no recipe asset store here): the live rewards' recipe tokens + the
    # Enchanted merge (CollEnch.merge)
    out_ = JClass("java.util.HashMap")()
    for cc_ in range(int(R.n)):
        for t in range(1, int(Reg.maxTier(R, cc_)) + 1):
            toks = Reg.REWARDS.get(str(R.id[cc_]).lower() + "." + str(t))
            rs = [str(x)[7:] for x in (toks or []) if str(x).startswith("recipe:")]
            if rs:
                out_.put("%d.%d" % (cc_, t), jstrs(rs))
    P_("CollEnch").merge(out_, R, P_("CollEnch").present())
    Reg.RECIPES = out_
    K.check(int(out_.size()) > 20, "D the live recipe unlocks rebuilt from the live rewards.properties (%d collection tiers)" % int(out_.size()))
    keys = sorted(f[:-11] for f in os.listdir(os.path.join(home, "counts")) if f.endswith(".properties")) if os.path.isdir(os.path.join(home, "counts")) else []
    UU = JClass("java.util.UUID")
    pages, bad, unsorted, nrows, maxrows = 0, [], [], 0, (0, "")
    vis = [cc for cc in range(int(R.n)) if not bool(R.hidden[cc])]
    for k in keys:
        try:
            u = UU.fromString(k[:36])
        except Exception:
            continue
        if str(P_("CollUtil").pkey(u)) != k:
            continue
        P = E.mkp(u, "Live" + k[:4])
        d = Store.data(u)
        un = P_("CollUnlocks").compute(d)
        for i, cc in enumerate(vis):
            ct = int(Reg.tierOf(R, cc, Store.sum(d, R, cc)))
            rows = P_("CollPage").recipeRows(d, R, cc, ct, un)
            ks = [(int(e[3]), str(e[4])) for e in rows]
            nrows += int(rows.size())
            maxrows = max(maxrows, (int(rows.size()), str(R.id[cc])))
            if ks != sorted(ks):
                unsorted.append("%s %s" % (k[:8], R.id[cc]))
            if True:
                pg = open_coll(E, P, cc)
                cmds, evs = HT.build(pg, P)
                ids = ids_of(cmds)
                miss = [s for s in sets_of(cmds) if s.lstrip("#").split(".")[0] not in ids] + [s for s, _t in evs if s.lstrip("#") not in ids]
                if miss or int(pg.view) != 2:
                    bad.append("%s %s %s" % (k[:8], R.id[cc], miss[:2]))
                pages += 1
    K.check(not bad and not unsorted, "D every live profile's collection pages build (%d pages, %d profiles): every b.set / binding names an element, the recipe lists sorted (%s %s)" % (
        pages, len(keys), bad[:3], unsorted[:3]))
    K.notes.append("D: %d live profile(s), %d collection pages built (%d recipe rows), %d visible collections" % (len(keys), pages, nrows, len(vis)))
    K.check(nrows > 40, "D the live pages show recipe rows (%d)" % nrows)
    K.check(maxrows[0] <= int(P_("CollPage").PRMAX), "FIXB3 D no live collection unlocks more than PRMAX (%d) recipes: the most is %d (%s)" % (
        int(P_("CollPage").PRMAX), maxrows[0], maxrows[1]))
    print("D most recipes in one live collection: %d (%s)" % maxrows)
    ch = sorted(k_ for k_, v_ in HK.tree_hash(home).items() if h0.get(k_) != v_)
    K.check(all(x.startswith("counts") for x in ch), "D the page builds changed no file but counts files (a shown NEW marker is cleared and saved): %s" % ch[:4])
    K.notes.append("D: %d counts file(s) saved by the page builds (NEW markers cleared once shown)" % len(ch))
    K.save()


if __name__ == "__main__":
    HK.run("SkyyCollections", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("merge", run_merge), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyCollections"))
