"""Harness for SkyyCollections 0.2.29 (beta bugs 16 + 13: placed-Furnace charcoal counts for the Charcoal collection; the grid / recipe /
tier texts wrap instead of being cut; tools/collections_0_2_29_patch.py). Build first:
    python tools/collections_0_2_29_patch.py && python SkyyCollections/build_skyycollections_0.2.29.py

    python SkyyCollections/test_skyycollections_0.2.29.py [--jar <SkyyCollections-0.2.29.jar>] [--dir <scratch>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.2.28 -> 0.2.29: exactly the listed members differ (+ the new class CollSmeltSys); non-class entries: only manifest.json
  SM   smelt    CollSmeltSys on REAL engine transactions (SlotTransaction / MoveTransaction / ListTransaction / CombinedItemContainer of 3
                parts): charcoal moved out of the OUTPUT part counts (the add side), from the input / fuel part 0, another item 0, a
                failed move 0, MOVE_FROM_SELF 0, a ListTransaction sums its moves, a move split over 2 slots counts both; registerSystem once
  FIT  fit      the REAL registry + default rewards (stage_player): every collection x every tier - the card's Next text fits two lines
                (CDNEXT2), the rank-gift split keeps the progress line on one (CDTEXT), every tier rewards text fits its 1 / 2 / 4-line row
                whole (none loses a part), every recipe name fits two lines (RPNAME2); a built category page: no "..." on any card, the Next
                labels wrap; a collection page with a long recipe name gets the 46 px rows
  M    pages    the 0.2.23 page phase on this jar (row sizes asked for the 0.2.29 card rows 104 / 150 / 208)
  X    exec     the 0.2.28 harness's exec phase on this jar (the unlock ladder unchanged)
  AA   audit    the engine-access audit
Not testable without the game (UNVERIFIED): the client's word wrap of the new two / four-line labels (sizes from the kit's font
tables), the real Furnace window move (same transaction path as SkyySkills' verified SmeltSys). Exit code 1 on any failure.
"""
import os, sys, re, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "ci"))
import skyybuild as B
import harness_kit as HK
import skyyui as SUI

VERSION = "0.2.29"
OLD_VERSION = "0.2.28"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCollections-%s.jar" % OLD_VERSION)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "bsc", "coll29")))
PKG = "com.skyy.collections."
EXPECT = {"CollPage": ["+f CDNEXT2", "+f CDTEXT", "+f RPNAME2", "+f TIERREW3", "~<clinit>", "~m buildCat", "~m buildDetail", "~m card",
                       "~m recipePanel"],
          "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"],      # the Count furnace charcoal help text; the kit version texts
          "SkyyCollectionsPlugin": ["~m setup"]}                                # + registerSystem(CollSmeltSys), the ready line
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = ["CollSmeltSys"]
OLD_GROW, NEW_GROW = [88, 127, 176], [104, 150, 208]


def _mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    _a = list(sys.argv)
    spec.loader.exec_module(m)
    sys.argv[:] = _a
    return m


def T23():
    return _mod("t23", os.path.join(HERE, "test_skyycollections_0.2.23.py"))


def T28():
    return _mod("t28", os.path.join(HERE, "test_skyycollections_0.2.28.py"))


def P(n):
    from jpype import JClass
    return JClass(PKG + n)


# ------------------------------------------------------------------------------------------------------------------- SM: smelt
def run_smelt(out, jar, scratch, _home):
    from jpype import JClass, JArray, JShort
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    S = P("CollSmeltSys")
    T = "com.hypixel.hytale.server.core.inventory."
    IS, SIC, CIC, IC = JClass(T + "ItemStack"), JClass(T + "container.SimpleItemContainer"), JClass(T + "container.CombinedItemContainer"), JClass(T + "container.ItemContainer")
    SLT, MVT, LTX = JClass(T + "transaction.SlotTransaction"), JClass(T + "transaction.MoveTransaction"), JClass(T + "transaction.ListTransaction")
    AT, MY = JClass(T + "transaction.ActionType"), JClass(T + "transaction.MoveType")
    AL = JClass("java.util.ArrayList")
    # a bare JVM has no item assets (new ItemStack throws): a stand-in stack = the class allocated without its constructor + itemId / quantity
    # (the SkyySkills 0.4.34 harness pattern) - the REAL getItemId / getQuantity / isEmpty run on it
    Cls = JClass("java.lang.Class")
    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)
    IS0 = IS

    def IS(iid, q):
        st = U.allocateInstance(IS0.class_)
        for f in IS0.class_.getDeclaredFields():
            if str(f.getName()) == "itemId":
                f.setAccessible(True)
                f.set(st, iid)
            elif str(f.getName()) == "quantity":
                f.setAccessible(True)
                f.setInt(st, q)
        return st
    inp, fuel, outp = SIC(JShort(2)), SIC(JShort(1)), SIC(JShort(4))
    bench = CIC(JArray(IC)([inp, fuel, outp]))
    player = SIC(JShort(9))
    CH = "Ingredient_Charcoal"
    K.eq(str(S.ITEM), CH, "SM the counted item = Ingredient_Charcoal")

    def slot(act, s, before, after):
        return SLT(True, act, JShort(s), before, after, None, False, False, False)

    def move(src_slot, item, n, before_q=None, typ=None, ok=True, add=None, other=bench):
        rm = slot(AT.REMOVE, src_slot, IS(item, before_q or n), None)
        ad = add if add is not None else slot(AT.ADD, 0, None, IS(item, n))
        return MVT(ok, rm, typ or MY.MOVE_TO_SELF, other, ad)

    def count(tx):
        mv = AL()
        S.moves(tx, mv)
        return sum(int(S.fromOutput(m, CH)) for m in mv), int(mv.size())
    out_slot = 2 + 1 + 1          # input 0-1, fuel 2, output 3-6
    K.check(bench.getContainerForSlot(JShort(out_slot)) == outp and bench.getContainerForSlot(JShort(0)) == inp, "SM the stand-in Furnace container: input 0-1, fuel 2, output 3-6")
    K.eq(count(move(out_slot, CH, 5)), (5, 1), "SM 5 charcoal taken out of the OUTPUT part count 5")
    K.eq(count(move(0, CH, 5)), (0, 1), "SM charcoal taken back out of the INPUT part counts 0")
    K.eq(count(move(2, CH, 5)), (0, 1), "SM charcoal taken back out of the FUEL part counts 0")
    K.eq(count(move(out_slot, "Ingredient_Bar_Iron", 5)), (0, 1), "SM an iron bar from the output counts 0 (only charcoal)")
    K.eq(count(move(out_slot, CH, 5, ok=False)), (0, 0), "SM a failed move counts 0")
    K.eq(count(move(out_slot, CH, 5, typ=MY.MOVE_FROM_SELF)), (0, 0), "SM MOVE_FROM_SELF (the player putting items in) counts 0")
    K.eq(count(move(out_slot, CH, 5, other=player)), (0, 0), "SM a move from a plain (non-bench) container counts 0")
    split = LTX(True, JClass("java.util.Arrays").asList([slot(AT.ADD, 0, IS(CH, 60), IS(CH, 64)), slot(AT.ADD, 1, None, IS(CH, 6))]))
    K.eq(count(move(out_slot, CH, 10, add=split)), (10, 1), "SM a take landing in two slots (4 on a stack + 6 new) counts the 10 that landed")
    part = slot(AT.ADD, 0, IS(CH, 62), IS(CH, 64))
    K.eq(count(move(out_slot, CH, 2, before_q=8, add=part)), (2, 1), "SM a partial take (2 of 8 fit) counts the 2 that landed, not the 8")
    lst = LTX(True, JClass("java.util.Arrays").asList([move(out_slot, CH, 3), move(out_slot + 1, CH, 4), move(0, CH, 9)]))
    K.eq(count(lst), (7, 3), "SM a ListTransaction (take all) sums its output moves (3 + 4), not the input one")
    K.check(S.benchOf(None, bench) is None and S.benchOf(AL(), bench) is None, "SM no open processing window = no bench (never counted)")
    src = open(os.path.join(HERE, "build_skyycollections_%s.py" % VERSION), encoding="utf8").read()
    K.eq(src.count("registerSystem(new @PKG@.CollSmeltSys())"), 1, "SM CollSmeltSys registered once (one registerSystem per class)")
    K.check('if (!@PKG@.CollReg.ADD_SOURCES.contains("sacks:furnace")) return;' in src and "new @PKG@.CollAddTask(u, @PKG@.CollUtil.pkey(u), ITEM, got)" in src
            and '"Furnace".equalsIgnoreCase(bench)' in src,
            "SM the hook: the Count furnace charcoal switch first; Furnace windows only; the credit = CollAddTask (creative / profile / caps)")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- FIT
def run_fit(out, jar, scratch, _home):
    from jpype import JClass, JString, JArray
    K = HK.Child(out)
    t23 = T23()
    E, Reg, Store, Pl = t23.stage_player(K, scratch, jar, "fit", "00000000-0000-0000-0000-0000000029f1")
    R = Reg.D
    Page, Craft, Util, Rb = P("CollPage"), P("CollCraft"), P("CollUtil"), P("CollRebirth")
    HM, Long = JClass("java.util.HashMap"), JClass("java.lang.Long")
    W = lambda x: int(Craft.width(JString(x)))
    CDT, CDN, RW, RW2, RW3, RN, RN2 = (int(Page.CDTEXT), int(Page.CDNEXT2), int(Page.TIERREW), int(Page.TIERREW2), int(Page.TIERREW3),
                                       int(Page.RPNAME), int(Page.RPNAME2))
    K.check(CDT >= 359 and CDN > CDT and RW3 > RW2 > RW and RN2 > RN, "FIT the widths: card %d / %d (2 lines), tier %d / %d / %d, recipe %d / %d" % (CDT, CDN, RW, RW2, RW3, RN, RN2))
    # the default recipe unlocks (the 0.2.22 FIT set-up: every "recipe:" token of the default rewards)
    rec = HM()
    for c in range(int(R.n)):
        for t in range(1, int(Reg.maxTier(R, c)) + 1):
            toks = Reg.REWARDS.get(str(R.id[c]).lower() + "." + str(t))
            rs = [str(x)[7:] for x in (toks or []) if str(x).startswith("recipe:")]
            if rs:
                rec.put("%d.%d" % (c, t), JArray(JString)(rs))
    Reg.RECIPES = rec
    widest_t = (0, "")
    n_next, bad_next, widest, n_tier, cut_tier, lines, names, bad_names = 0, [], (0, ""), 0, [], {1: 0, 2: 0, 3: 0}, set(), []
    for c in range(int(R.n)):
        if bool(R.hidden[c]):
            continue
        for t in range(1, int(Reg.maxTier(R, c)) + 1):
            nx = Reg.rewardLines(R, c, t)
            nr = Reg.recipesAt(c, t)
            n1 = (str(Util.prettyRecipe(nr[0])) + " recipe") if len(nr) > 0 else ("" if nx is None or nx.isEmpty() else str(nx.get(0)))
            nt = ("Next: tier " + str(Util.roman(t))) if (nx is None or nx.isEmpty()) else "Next: " + n1
            n_next += 1
            widest = max(widest, (W(nt), nt))
            if W(nt) > CDN * 1000 or str(Craft.fitPx(JString(nt), CDN)) != nt:
                bad_next.append(nt)
            tx = str(Reg.rewardTextP(R, c, t, False))
            n_tier += 1
            widest_t = max(widest_t, (W(tx), tx))
            k = 1 if W(tx) <= RW * 1000 else (2 if W(tx) <= RW2 * 1000 else 3)
            lines[k] += 1
            lim = (RW, RW2, RW3)[k - 1]
            if str(Craft.fitPx(JString(tx), lim)) != tx:
                cut_tier.append("%s %d (%d px): %s" % (R.id[c], t, W(tx) // 1000, tx))
            for rid in nr:
                names.add(str(Util.prettyRecipe(rid)))
    K.check(n_next > 500 and not bad_next, "FIT every card Next text of the default rewards fits two lines whole (%d texts; widest %.0f px of %d: %s): %s"
            % (n_next, widest[0] / 1000.0, CDN, widest[1], bad_next[:3]))
    K.check(n_tier > 500 and not cut_tier, "FIT every tier rewards text fits its 1 / 2 / 4-line row whole (%d texts: %s; widest %.0f px of %d): %s" % (
        n_tier, lines, widest_t[0] / 1000.0, RW3, cut_tier[:3]))
    for nm in sorted(names):
        for shown in (nm, "NEW  " + nm):
            if str(Craft.fitPx(JString(shown), RN2)) != shown:
                bad_names.append(shown)
    K.check(len(names) > 50 and not bad_names, "FIT every unlockable recipe name (+ the NEW mark) fits two lines (%d names; %d wider than one line): %s"
            % (len(names), sum(1 for x in names if W(x) > RN * 1000), bad_names[:3]))
    # the progress line of a maxed collection with rebirth ranks: the gift split off keeps it on one line (worst case numbers)
    prog = "Tier XX    Rebirth rank 10: 9,999,999 / 99,999,999"
    K.check(W(prog) <= CDT * 1000, "FIT the longest rebirth progress line fits one line (%.0f of %d px)" % (W(prog) / 1000.0, CDT))
    # ---- a built category page: no card text cut, the Next labels wrap
    u = Pl.pr.getUuid()
    d = Store.data(u)
    for c in range(int(R.n)):
        if int(R.cat[c]) == 1 and not bool(R.hidden[c]):
            d.items.put(str(R.items[c][0]), Long.valueOf(int(Reg.threshold(R, c, 2))))
    pg = t23.open_coll(E, Pl, -1)
    t23.click(E, Pl, pg, "ccat1")
    built = t23.HT.build(pg, Pl)
    sets = t23.sets_of(built[0])
    nxt = [t23.txt(sets, k_) for k_ in sorted(sets) if k_.startswith("#SkyyCCdNext")]
    prg = [t23.txt(sets, k_) for k_ in sorted(sets) if k_.startswith("#SkyyCCdProg")]
    K.check(len(nxt) > 8 and all(x and not str(x).endswith("...") for x in nxt + prg), "FIT the Mining list: %d cards, no Next / progress text cut: %s" % (len(nxt), nxt[:3]))
    lab = [t for ty, s, t, dd in built[0] if t and t.startswith("Label #SkyyCCdNext")]
    K.check(lab and all("Wrap: true" in x and "Height: 42" in x for x in lab), "FIT the Next labels wrap (two lines, 42 px)")
    K.check(any(t and t.startswith("Group #SkyyCCd0 ") and "Height: 104" in t for ty, s, t, dd in built[0]), "FIT the cards are 104 px rows")
    # ---- a collection whose recipe list holds a long name: the 46 px rows; the name is whole
    c = int(R.byId.get("wheat"))
    m = HM()
    long_id = "Skyy_Test_Ceremonial_Harvest_Lantern_Recipe_Generated_0"
    m.put("%d.1" % c, JArray(JString)([long_id] + ["Zz_Item%02d_Recipe_Generated_0" % i for i in range(20)]))
    Reg.RECIPES = m
    pg = t23.open_coll(E, Pl, c)
    built = t23.HT.build(pg, Pl)
    sets = t23.sets_of(built[0])
    nm = str(Util.prettyRecipe(long_id))
    shown = [t23.txt(sets, "#SkyyCPr%dN.Text" % i) for i in range(21)]
    K.check(RN * 1000 < W(nm) <= RN2 * 1000 and int(pg.gk) >= 1 and any(x and str(x).endswith(nm) for x in shown),
            "FIT a %d px recipe name (wider than the %d px cell) shows whole on the 46 px rows (gk %d): %s / %s" % (W(nm) // 1000, RN, int(pg.gk), nm, shown[:3]))
    mk = [t for ty, s, t, dd in built[0] if t and "Label #SkyyCPr0N " in t]
    K.check(bool(mk) and "Wrap: true" in mk[0][mk[0].index("Label #SkyyCPr0N "):][:400], "FIT the recipe name label wraps")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- M: pages
def run_pages(out, jar, scratch, home):
    """the 0.2.23 page phase; its version check asks for 0.2.29, its row-size checks for the 0.2.29 card rows (88 / 127 / 176 -> 104 / 150 / 208)"""
    ck0, eq0 = HK.Child.check, HK.Child.eq
    plug = zipfile.ZipFile(jar).read("com/skyy/collections/SkyyCollectionsPlugin.class")
    TAGS = ["", "Armor_Copper_Chest", "Armor_Copper_Head", "Ingredient_Bar_Iron", "Tool_Pickaxe_Mithril"]
    cap = {}

    def ck(self, cond, what):
        if what == "PAGE the ready line names 0.2.23":
            return ck0(self, re.search(rb"\[SkyyCollections\] 0\.2\.29 ready", plug) is not None, "PAGE the ready line names 0.2.29")
        if what.startswith("PAGE the jar's page id (ready line) = COLL_PAGE_CHECKED"):   # 0.2.23's check reads ITS build script: ask this one's
            gen = open(os.path.join(HERE, "build_skyycollections_%s.py" % VERSION), encoding="utf8").read()
            mm_ = re.search(r'COLL_PAGE_CHECKED = "([0-9a-z]+)"', gen)
            pid = re.search(rb", page ([0-9a-f]{12})", plug)
            return ck0(self, mm_ is not None and pid is not None and pid.group(1).decode() == mm_.group(1),
                       "PAGE the jar's page id (ready line) = the 0.2.29 COLL_PAGE_CHECKED: %s vs %s" % (pid.group(1) if pid else None, mm_.group(1) if mm_ else None))
        if what == "GROW the lines and the cards are 176 px (2x)":
            b = cap.get("built")
            return ck0(self, b is not None and any(t and t.startswith("Group #SkyyCGRow0 ") and "Height: 208" in t for ty, s, t, dd in b[0])
                       and any(t and t.startswith("Group #SkyyCCd0 ") and "Height: 208" in t for ty, s, t, dd in b[0]), "GROW the lines and the cards are 208 px (2x)")
        if what == "GROW the 127 px lines":
            b = cap.get("built")
            return ck0(self, b is not None and any(t and t.startswith("Group #SkyyCGRow0 ") and "Height: 150" in t for ty, s, t, dd in b[0]), "GROW the 150 px lines")
        if what.startswith("LIST ") and what.endswith(" rows: the normal 88 px rows"):
            b = cap.get("built")
            return ck0(self, b is not None and not any(t and "#SkyyCGRow" in t and "Height: 150" in t for ty, s, t, dd in b[0]),
                       what.replace("88 px", "104 px"))
        return ck0(self, cond, what)

    def eq(self, got, want, what):
        if what == "GROW the category row tiers = SUI.grow_row_sizes(630, 88)":
            return eq0(self, [int(x) for x in got], NEW_GROW, "GROW the category row tiers = SUI.grow_row_sizes(630, 104) = %s" % NEW_GROW)
        if what.startswith("GROW HubBar.growSize(") and what.endswith("rows) = grow_pick"):
            n_ = int(what[len("GROW HubBar.growSize("):].split(" ")[0])
            return eq0(self, got, SUI.grow_pick(n_, 630, NEW_GROW), what + " (104 px rows)")
        if what == "GROW 3 collections = 2 lines: the biggest tier":
            return eq0(self, got, SUI.grow_pick(2, 630, NEW_GROW), what + " (104 px rows)")
        if what == "LIST the tier tags" and want == ["", "T2", "T2", "T3", "T7"]:
            from jpype import JClass
            w2 = [""] + [str(JClass(PKG + "CollTier").tierText(i)) for i in TAGS[1:]]
            eq0(self, w2, ["", "T1", "T1", "T2", "T13"], "LIST the rows' tags on the 15-step ladder (Copper T1, Iron T2, Mithril T13)")
            return eq0(self, got, w2, "LIST the tier tags (15-step ladder)")
        return eq0(self, got, want, what)
    HK.Child.check, HK.Child.eq = ck, eq
    t23 = T23()
    b0 = t23.HT.build

    def build(pg, p):
        r = b0(pg, p)
        cap["built"] = r
        return r
    t23.HT.build = build
    t23.run_pages(out, jar, scratch, home)


def run_exec(out, jar, scratch, home):
    T28().run_exec(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run("SkyyCollections", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("smelt", run_smelt), ("fit", run_fit), ("pages", run_pages), ("exec", run_exec)], __file__)
