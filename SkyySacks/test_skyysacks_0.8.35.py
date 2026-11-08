"""Harness for SkyySacks 0.8.35 (round furnall - tools/sacks_0_8_35_patch.py: the All button really adds all + sacks:fn:openFurnace; Skyy 2026-11-08
"make the all button actually add all, and put the furnace icon in  smithing and upgrade too so you can open it anywhere you need it.").
Build first:
    python tools/sacks_0_8_35_patch.py && python SkyySacks/build_skyysacks_0.8.35.py

    python SkyySacks/test_skyysacks_0.8.35.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A / C   verify (-Xverify:all) + compare 0.8.34 -> 0.8.35 (only what the patch touches)
  ALL35   on the 0.8.9 Void stand-ins (a 25-stack ore, 1,792 of them in the bag): the mirror's old numbers reproduced (All 25 / a click of 100), then the real code:
          label (viewMats + limit + drawRow) and click (procQueue) with materials only in the bags / only in the inventory / split / more than the room (Skyy's 190 used)
          / zero room / several inputs / the Tannery / a resource-type input / x10 needing more than the mirror offers / Enchanted items opening;
          craftAll (the instant tabs): bags only, All limited by the inventory room, x10, a full inventory, gear outputs, the Void Charms counted; debit == queued in every case
  BC35    bytecode: craftAll's and procQueue's calls, CraftHubOpen's Furnace branch
  D       start twice on a scratch COPY of NewBetaTest's Skyy_SkyySacks: no migration, no byte changed
NOT COVERED (UNVERIFIED in game): the client drawing the numbers; CraftHubOpen.apply with a real PlayerRef / PageManager (its gate benchShown and the refusal are executed here).
Exit code 1 on any failure.
"""
import os, sys, time, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_argv = list(sys.argv)
_RC = HK.run_compare
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_33", os.path.join(HERE, "test_skyysacks_0.8.33.py"))
T33 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T33)
sys.argv = _argv
HK.run_compare = _RC
T30, T089 = T33.T30, T33.T089

VERSION = "0.8.35"
OLD_VERSION = "0.8.34"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-%s.jar" % OLD_VERSION)
T30.OLD_JAR = OLD_JAR
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "furnall", "sacks")))
PKG = "com.skyy.sacks."
BETA = T33.BETA
EXPECT = {"SkyySacksPlugin": ["~m setup"], "CfgRows": ["~m header"], "CfgFn": ["~m opExport"],
          "RecipeCmp": ["~<clinit>"],          # the /craft tier table is re-baked from tools/tier_tags.py at build time
          "BagMirror": ["+f COUNT_MAX", "+m counts"],
          "CraftHubOpen": ["+f bench", "+c ", "~m apply"],
          "CraftPage": ["+f lastDone", "+f lastQty", "+f lastVoid", "+m benchShown", "+m countMats", "+m craftAll", "+m fitN", "+m fits",
                        "~m craftOne", "~m handleDataEvent", "~m procQueue", "~m renderPage", "~m viewMats"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
COP, IRON = "Ore_Copper", "Ore_Iron"
OUT, GEAR = "Skyy_Test_Bar35", "Skyy_Test_Gear35"


def cases35(K, L, scratch):
    from jpype import JClass, JString, JArray, JInt, JFloat, JLong, JShort
    VS, Defs, Pool, Mirror, Swp = L["VS"], L["Defs"], L["Pool"], L["Mirror"], L["Swp"]
    fresh, write_pool, player, pc, inv_counts, custom_item, drain = (L[n] for n in ("fresh", "write_pool", "player", "pc", "inv_counts", "custom_item", "drain"))
    UUID, bridge, us, jfield, jp, pref, ItemC, IS = (L[n] for n in ("UUID", "bridge", "us", "jfield", "jp", "pref", "ItemC", "IS"))
    CtF, CtM, CtC = L["CtF"], L["CtM"], L["CtC"]
    J = lambda n: JClass(PKG + n)
    VC, CP, PB, PS, AL, CHO = J("VoidCompact"), J("CraftPage"), J("ProcBench"), J("ProcStore"), J("AccLink"), J("CraftHubOpen")
    MQ = JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
    CRc = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    BR = JClass("com.hypixel.hytale.protocol.BenchRequirement")
    CIC = JClass("com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer")
    ICa = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
    IRT = JClass("com.hypixel.hytale.protocol.ItemResourceType")
    UCBc, UEBc = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"), JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    HS, Paths = JClass("java.util.HashSet"), JClass("java.nio.file.Paths")
    st_c = jp.makeClass("com.hypixel.hytale.component.SkyyTestCraftStore35", jp.get("com.hypixel.hytale.component.Store"))
    st_c.addConstructor(CtC.make("public SkyyTestCraftStore35() { super((com.hypixel.hytale.component.ComponentRegistry) null, 0, (Object) null, "
                                 "(com.hypixel.hytale.component.IResourceStorage) null); }", st_c))
    st_c.addMethod(CtM.make("public void invoke(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.system.EcsEvent e) { }", st_c))
    st = us.allocateInstance(JClass(st_c.toClass(JClass("com.hypixel.hytale.component.Store").class_)).class_)
    RT = "Skyy_Test_RT35"
    RA, RB = "Skyy_Test_RtA35", "Skyy_Test_RtB35"
    for i_, m_ in ((COP, 25), (IRON, 25), (OUT, 100)):
        custom_item(i_, m_)
    custom_item(GEAR, 1)
    # the resource-type items: they need a bag home, so they borrow a real Mining-bag id each
    for i_ in ("Ore_Thorium", "Rubble_Stone"):
        it_ = custom_item(i_, 25)
        jfield(ItemC.class_, "resourceTypes").set(it_, JArray(IRT)([IRT(JString(RT), JInt(1))]))
    RA, RB = "Ore_Thorium", "Rubble_Stone"
    K.check(Defs.homeOf(JString(COP)) is not None and Defs.homeOf(JString(IRON)) is not None and Defs.homeOf(JString(RA)) is not None and Defs.homeOf(JString(RB)) is not None,
            "ALL35 stand-ins: ore and rock ids have a bag home")
    np_ = int(VC.np())
    bases = [str(VC.baseAt(i)) for i in range(np_)]
    enchs = [str(VC.enchAt(i)) for i in range(np_)]
    EB = next(b for b, e in zip(bases, enchs) if Defs.homeOf(JString(b)) is not None and Defs.homeOf(JString(e)) is not None)
    EE = enchs[bases.index(EB)]
    custom_item(EB, 25)
    custom_item(EE, 25)
    base = os.path.join(scratch, "all35")
    U = UUID.fromString("00000000-0000-0000-0000-0000000f0835")
    k = str(U)
    d = os.path.join(scratch, "all35proc")
    os.makedirs(d, exist_ok=True)
    PS.DIR = Paths.get(d)

    def mk(pool):
        drain()
        fresh(base)
        PS.DIR = Paths.get(d)
        PS.CACHE.clear() if hasattr(PS, "CACHE") else None
        bridge.put(JString("coll:recipes:" + k), JString(""))
        write_pool(os.path.join(base, "pools"), k, pool)
        VS.st(k).first = 1

    def recipe(rid, ins, out=OUT, qty=1):
        mi = JArray(MQ)([MQ(JString(i), None, None, JInt(q), None) for i, q in ins])
        po = MQ(JString(out), None, None, JInt(qty), None)
        r = CRc(mi, po, JArray(MQ)([po]), JInt(1), JArray(BR)(0), JFloat(0.0), False, JInt(0))
        jfield(CRc.class_, "id").set(r, JString(rid))
        return r

    def recipe_rt(rid, rt, q):
        mi = JArray(MQ)([MQ(None, JString(rt), None, JInt(q), None)])
        po = MQ(JString(OUT), None, None, JInt(1), None)
        r = CRc(mi, po, JArray(MQ)([po]), JInt(1), JArray(BR)(0), JFloat(0.0), False, JInt(0))
        jfield(CRc.class_, "id").set(r, JString(rid))
        return r

    def page(tab):
        pg = us.allocateInstance(CP.class_)
        jfield(CP.class_, "playerRef").set(pg, pref(U))
        jfield(CP.class_, "info").set(pg, JString(""))
        jfield(CP.class_, "query").set(pg, JString(""))
        jfield(CP.class_, "tab").set(pg, JString(tab))
        return pg

    def ucb_text(b_):
        out_ = []
        for c_ in b_.getCommands():
            k_ = c_.getClass()
            while k_ is not None:
                for f_ in k_.getDeclaredFields():
                    if JClass("java.lang.reflect.Modifier").isStatic(f_.getModifiers()):
                        continue
                    f_.setAccessible(True)
                    v_ = f_.get(c_)
                    if v_ is not None:
                        out_.append(str(v_))
                k_ = k_.getSuperclass()
        return "\n".join(out_)

    def bench(b_="Furnace"):
        pb_ = PS.of(JString(k), JString(b_))
        pb_.queue.clear()
        pb_.progress = 0
        return pb_

    def rows_of(pb_):
        return [(str(j.recipe), int(j.count), str(j.inputs)) for j in list(pb_.queue)]

    def queue(pb_, p, r, want=0, b_="Furnace"):
        t0 = time.time()
        msg = str(CP.procQueue(p, None, None, JString(k), JString(b_), 1, r, want))
        ms = (time.time() - t0) * 1000.0
        drain()
        return msg, ms

    def view(p, w):
        pg = page("P:Furnace")
        return pg.viewMats(p, JString(k), w)

    def wanted(*rs):
        s = HS()
        s.add(JString("!view"))
        for r in rs:
            Mirror.addInputs(s, r.getInput())
        return s

    rCu = recipe("Skyy_Test_Cu35", [(COP, 1)])
    # ---- 0. Skyy's report reproduced: the mirror offers one stack per wanted id on a full page, four for one recipe
    fill = ["Ingredient_Bar_Iron", "Ingredient_Stick", "Ingredient_Fibre", "Food_Bread", "Plant_Crop_Wheat_Item", "Rock_Stone_Cobble", "Wood_Oak_Trunk", "Wood_Maple_Trunk", "Ore_Thorium",
            "Ingredient_Tree_Sap", "Ingredient_Crystal_Blue", "Ingredient_Bone_Fragment", "Fish_Bluegill_Item", "Food_Fish_Raw", "Ingredient_Fabric_Scrap_Linen",
            "Ingredient_Fabric_Scrap_Shadoweave", "Ingredient_Fabric_Scrap_Cindercloth", "Plant_Crop_Lettuce_Item", "Ingredient_Life_Essence", "Ingredient_Feathers_Light", "Rubble_Stone",
            "Food_Fish_Grilled"]
    fill = [f for f in fill if Defs.homeOf(JString(f)) is not None and f not in (RA, RB)] + [b for b in bases if Defs.homeOf(JString(b)) is not None][:30]
    for f in fill:
        custom_item(f, 25)
    mk(dict([(COP, 1792), (IRON, 1262)] + [(f, 400) for f in fill]))
    p = player(storage=[])
    rs = [rCu, recipe("Skyy_Test_Fe35", [(IRON, 1)])] + [recipe("Skyy_Test_F%d" % i, [(f, 1)]) for i, f in enumerate(fill)]
    rs = rs + [recipe("Skyy_Test_G%d" % i, [(f, 1)]) for i, f in enumerate(fill)]
    wv = wanted(*rs)
    caps = Swp.caps(p.getInventory())
    m = Mirror.of(k)
    m.sync()
    m.rebuild(caps, wv)
    old_page = int(CP.limit(rCu, CIC(JArray(ICa)([p.getInventory().getCombinedBackpackStorageHotbar(), m.cont]))))
    m.sync()
    m.rebuild(caps, wanted(rCu))
    old_one = int(CP.limit(rCu, CIC(JArray(ICa)([p.getInventory().getCombinedBackpackStorageHotbar(), m.cont]))))
    K.notes.append("ALL35 root cause: the mirror with %d wanted ids offers %d Copper Ore (the label), one recipe %d (the click) - the bag holds 1,792" % (int(wv.size()), old_page, old_one))
    K.check(old_page == 25, "ALL35 (0) ROOT CAUSE the page mirror's %d-id layout counts %d of 1,792 ore" % (int(wv.size()), old_page))
    K.eq(old_one, 100, "ALL35 (0) ROOT CAUSE one recipe's mirror = 4 stacks of 25 = 100 (crafts.log requested=100)")
    # ---- 1. the label + a click: bags only
    w1 = view(p, wv)
    K.eq(int(CP.limit(rCu, w1)), 1792, "ALL35 (1) the label: viewMats counts every Void stack: 1,792")
    pgv = page("P:Furnace")
    br_, er_ = UCBc(), UEBc()
    jfield(CP.class_, "rowSz").setInt(pgv, 0)
    pgv.drawRow(br_, er_, 0, rCu, w1, 1792, "", 1000, True, "2 s each")
    t_ = ucb_text(br_)
    K.check("All 1000" in t_ and "1,792/1" in t_ or ("All 1000" in t_ and "1.8K/1" in t_ or "All 1000" in t_ and "1792/1" in t_), "ALL35 (1) drawRow: 'All 1000' and the true have / need on the row")
    pb = bench()
    msg, ms = queue(pb, p, rCu)
    pc1 = pc(k)
    K.check(int(pb.queued()) == 1000 and pc1.get(COP) == 792 and sum(c for _r, c, _i in rows_of(pb)) == 1000 and rows_of(pb)[0][2] == "Ore_Copper*1" and inv_counts(p) == {},
            "ALL35 (1) All, bags only, 1,792 ore: exactly 1,000 queued, 1,000 left the bag: %s (%.1f ms) pool %s" % (msg, ms, pc1.get(COP)))
    K.check("queued 1000 x" in msg and "queue is full (1000 units)" in msg, "ALL35 (1) the status says how many and that the queue is full: %s" % msg)
    K.check(ms < 500.0, "ALL35 (1) a 1,000-unit debit is quick (%.1f ms)" % ms)
    # ---- 2. inventory only
    mk({})
    p = player(storage=[(COP, 25), (COP, 25), (COP, 25)], hotbar=[(COP, 20)])
    pb = bench()
    K.eq(int(CP.limit(rCu, view(p, wanted(rCu)))), 95, "ALL35 (2) the label: inventory only")
    msg, ms = queue(pb, p, rCu)
    K.check(int(pb.queued()) == 95 and inv_counts(p).get(COP, 0) == 0 and "queued 95" in msg and "full" not in msg, "ALL35 (2) All, inventory only: 95 queued, 95 gone: %s" % msg)
    # ---- 3. split
    mk({COP: 70})
    p = player(storage=[(COP, 25), (COP, 5)])
    pb = bench()
    K.eq(int(CP.limit(rCu, view(p, wanted(rCu)))), 100, "ALL35 (3) the label: 30 inventory + 70 Void")
    msg, ms = queue(pb, p, rCu)
    K.check(int(pb.queued()) == 100 and inv_counts(p).get(COP, 0) == 0 and pc(k).get(COP, 0) == 0 and "70 from the Void" in msg, "ALL35 (3) split: all 100, nothing left, 70 from the Void: %s" % msg)
    # ---- 4. Skyy's case: 190 used, more ore than room
    mk({COP: 1792})
    p = player(storage=[])
    pb = bench()

    pb.addJob(JString("Skyy_Test_Old"), 190, JLong(1000), JString("Ore_Copper*1"), JLong(int(JClass("java.lang.System").currentTimeMillis())))
    msg, ms = queue(pb, p, rCu)
    K.check(int(pb.queued()) == 1000 and pc(k).get(COP) == 982 and "queued 810 x" in msg and "queue is full" in msg, "ALL35 (4) 190 of 1,000 used, 1,792 ore: 810 queued, 810 paid: %s pool %s" % (msg, pc(k).get(COP)))
    # ---- 5. zero room
    p = player(storage=[(COP, 10)])
    before = (pc(k).get(COP), inv_counts(p).get(COP))
    msg, ms = queue(pb, p, rCu)
    K.check("queue is full" in msg and (pc(k).get(COP), inv_counts(p).get(COP)) == before and int(pb.queued()) == 1000, "ALL35 (5) no room: nothing moves: %s" % msg)
    # ---- 6. several inputs
    rM = recipe("Skyy_Test_Alloy35", [(COP, 3), (IRON, 2)])
    mk({COP: 3000, IRON: 700})
    p = player(storage=[(COP, 5)])
    pb = bench()
    K.eq(int(CP.limit(rM, view(p, wanted(rM)))), 350, "ALL35 (6) the label: the scarcest input decides (700 iron / 2)")
    msg, ms = queue(pb, p, rM)
    cc = pc(k).get(COP, 0) + inv_counts(p).get(COP, 0)
    K.check(int(pb.queued()) == 350 and cc == 3005 - 1050 and pc(k).get(IRON, 0) == 0 and "queued 350" in msg, "ALL35 (6) two inputs: 350 queued, exactly 1,050 copper + 700 iron paid: %s; copper left %d" % (msg, cc))
    K.check(rows_of(pb)[0][2] in ("Ore_Copper*3;Ore_Iron*2",), "ALL35 (6) the job records the inputs per unit: %s" % rows_of(pb)[0][2])
    # ---- 7. the Tannery
    mk({COP: 500})
    p = player(storage=[])
    pb2 = bench("Tannery")
    msg, ms = queue(pb2, p, rCu, b_="Tannery")
    K.check(int(pb2.queued()) == 500 and pc(k).get(COP, 0) == 0 and "in the Tannery" in msg, "ALL35 (7) the Tannery: all 500: %s" % msg)
    # ---- 8. a resource-type input: one unit a time, more units than the old 400-pass guard
    rR = recipe_rt("Skyy_Test_Rt35", RT, 2)
    mk({RA: 900, RB: 700})
    p = player(storage=[(RA, 10)])
    pb = bench()
    K.eq(int(CP.limit(rR, view(p, wanted(rR)))), 805, "ALL35 (8) the label: a resource type sums all its items (1,610 / 2)")
    t0 = time.time()
    msg, ms = queue(pb, p, rR)
    total_left = pc(k).get(RA, 0) + pc(k).get(RB, 0) + inv_counts(p).get(RA, 0)
    K.check(int(pb.queued()) == 805 and total_left == 0 and "queued 805" in msg, "ALL35 (8) resource type: 805 units (over the old 400 guard), everything paid exactly: %s; left %d" % (msg, total_left))
    K.notes.append("ALL35 (8) 805 resource-type units took %.0f ms" % ms)
    K.check(ms < 2000.0, "ALL35 (8) one unit at a time stays quick for 805 units (%.0f ms)" % ms)
    # ---- 9. x10 needing more than the mirror offers (50 ore each = 500 > 4 stacks)
    rB = recipe("Skyy_Test_Big35", [(COP, 50)])
    mk({COP: 1000})
    p = player(storage=[])
    pb = bench()
    msg, ms = queue(pb, p, rB, want=10)
    K.check(int(pb.queued()) == 10 and pc(k).get(COP, 0) == 500 and "queued 10 x" in msg, "ALL35 (9) x10 of a 50-ore recipe: 10 queued, 500 paid: %s" % msg)
    # ---- 10. Enchanted items open for a big click
    rE = recipe("Skyy_Test_E35", [(EB, 1)])
    mk({EB: 30, EE: 5})
    p = player(storage=[])
    pb = bench()
    K.eq(int(CP.limit(rE, view(p, wanted(rE)))), 530, "ALL35 (10) the label: the loose 30 + 5 Enchanted x 100")
    msg, ms = queue(pb, p, rE)
    a = pc(k)
    K.check(int(pb.queued()) == 530 and a.get(EB, 0) == 0 and a.get(EE, 0) == 0, "ALL35 (10) All opens Enchanted items, debit = queued: %s pool %s" % (msg, a))
    # ---- 11. the instant tabs: craftAll
    custom_item(OUT, 100)
    mk({COP: 1000})
    p = player(storage=[])
    pg = page("X:test")

    t0 = time.time()
    msg = str(pg.craftAll(None, st, p, U, JString(k), rCu, 0, False))
    ms = (time.time() - t0) * 1000.0
    drain()
    K.check(inv_counts(p).get(OUT) == 1000 and pc(k).get(COP, 0) == 0 and "1000" in msg and "from the Void" in msg, "ALL35 (11) craftAll, bags only: 1,000 crafted over rounds, paid exactly: %s (%.0f ms) inv %s" % (msg, ms, inv_counts(p)))
    # ---- 12. All stops at what fits
    mk({COP: 9000})
    p = player(storage=[])
    K.eq(int(CP.fitN(p, rCu, 9000)), 5400, "ALL35 (12) fitN: 54 empty slots x 100 = 5,400 outputs")
    pg = page("X:test")
    msg = str(pg.craftAll(None, st, p, U, JString(k), rCu, 0, False))
    drain()
    K.check(inv_counts(p).get(OUT) == 5400 and pc(k).get(COP) == 3600 and "inventory is full" in msg and "3600 more" in msg, "ALL35 (12) All fills the inventory, says so, pays only that: %s" % msg)
    K.eq(int(CP.fitN(p, rCu, 3600)), 1, "ALL35 (12) a full inventory: All still offers 1 (the buttons stay live, as before)")
    # ---- 13. x10 + gear outputs + multi-output stack fit
    mk({COP: 1000})
    p = player(storage=[])
    pg = page("X:test")
    msg = str(pg.craftAll(None, st, p, U, JString(k), rCu, 10, False))
    drain()
    K.check(inv_counts(p).get(OUT) == 10 and pc(k).get(COP) == 990, "ALL35 (13) x10 = 10: %s" % msg)
    rG = recipe("Skyy_Test_Gr35", [(COP, 1)], GEAR)
    p = player(storage=[])
    K.eq(int(CP.fitN(p, rG, 5000)), 54, "ALL35 (13) a 1-stack output: All = the 54 free slots")
    # ---- 14. the Void Charms count, and the page's accessory container still adds up
    T1 = "Skyy_Accessory_Furnace_T1"
    custom_item(T1, 1)
    rA = recipe("Skyy_Test_A35", [(T1, 1), (COP, 1)])
    K.eq(int(CP.limit(rA, AL.cont(JArray(JString)([T1, T1]), wanted(rA)) if False else view(player(storage=[(T1, 1), (COP, 5)]), wanted(rA)))), 1, "ALL35 (14) an accessory in the inventory counts")
    c_ = AL.cont(JArray(JString)([T1]), wanted(rA))
    K.check(c_ is not None and int(c_.countRemovableMaterial(MQ(JString(T1), None, None, JInt(1), None))) == 1, "ALL35 (14) the Void Charms copy container holds the charm (craftAll / viewMatsAcc join it)")
    # ---- 15. the bridge gate + the page tab
    bridge.remove("acc:has:" + k)
    pb = bench()
    pb.out.clear()
    K.check(not bool(PS.pending(JString(k), JString("Furnace"))) and not bool(CP.benchShown(p, U, JString("Furnace"))), "ALL35 (15) no Furnace accessory and no Furnace work: the sub-tab's rule says no")
    K.check(not bool(CHO(JString("Furnace")).apply(UUID.fromString("00000000-0000-0000-0000-000000000abc"))), "ALL35 (15) sacks:fn:openFurnace for nobody online = FALSE (nothing opened)")
    bridge.put("acc:has:" + k, "Skyy_Accessory_Furnace_T1")
    K.check(bool(CP.benchShown(p, U, JString("Furnace"))), "ALL35 (15) a Furnace accessory in the Void Charms: the sub-tab's rule says yes")
    bridge.remove("acc:has:" + k)
    pb = bench()
    pb.addJob(JString("Skyy_Test_Old"), 1, JLong(1000), JString("Ore_Copper*1"), JLong(int(JClass("java.lang.System").currentTimeMillis())))
    K.check(bool(CP.benchShown(p, U, JString("Furnace"))), "ALL35 (15) no charm but work in the Furnace: the sub-tab's rule still shows it")
    # ---- 16. a click cannot dupe under a second look: view + queue + view
    mk({COP: 26})
    p = player(storage=[])
    pb = bench()
    K.eq(int(CP.limit(rCu, view(p, wanted(rCu)))), 26, "ALL35 (16) label 26 (just over one stack)")
    msg, ms = queue(pb, p, rCu)
    K.check(int(pb.queued()) == 26 and pc(k).get(COP, 0) == 0, "ALL35 (16) the second round after one stack: exact: %s" % msg)
    K.eq(int(CP.limit(rCu, view(p, wanted(rCu)))), 0, "ALL35 (16) label 0 after the click")
    # the count container is never the paying one: nothing in it can be removed from the pool
    mk({COP: 100})
    p = player(storage=[])
    v = view(p, wanted(rCu))

    K.eq(pc(k).get(COP), 100, "ALL35 (16) looking at the page moves nothing")
    # ---- 17. the page build's cost: every recipe on a big tab counted against the true container
    mk(dict((f, 400) for f in fill))
    p = player(storage=[(COP, 25)] * 30)
    v = view(p, wanted(*rs))
    many = rs * 40
    t0 = time.time()
    n_ = sum(int(CP.limit(r_, v)) for r_ in many)
    ms = (time.time() - t0) * 1000.0
    K.notes.append("ALL35 (17) %d limit() calls over the true container (%d wanted ids): %.0f ms" % (len(many), int(wanted(*rs).size()), ms))
    K.check(n_ > 0 and ms < 800.0, "ALL35 (17) a %d-recipe page counts in %.0f ms" % (len(many), ms))


def run_all35(out, jar, scratch, home):
    T089.void_cases = cases35
    T089.run_void(out, jar, scratch, home)


def run_bc35(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(True)
    cp.appendClassPath(JString(jar))
    Mn = JClass("javassist.bytecode.Mnemonic")

    def calls(m):
        seen = []
        ci = m.getMethodInfo().getCodeAttribute().iterator()
        cpool = m.getMethodInfo().getConstPool()
        while ci.hasNext():
            i = ci.next()
            op = str(Mn.OPCODE[ci.byteAt(i)])
            if op in ("invokestatic", "invokevirtual", "invokespecial"):
                idx = ci.u16bitAt(i + 1)
                seen.append(str(cpool.getMethodrefClassName(idx)).split(".")[-1] + "." + str(cpool.getMethodrefName(idx)))
        return seen

    def one(cl, n):
        return cp.get(PKG + cl).getDeclaredMethod(n)
    pq = calls(one("CraftPage", "procQueue"))
    K.check("CraftPage.countMats" in pq and "BagMirror.sync" in pq and pq.count("CraftPage.materialsFor") >= 2, "BC35 procQueue: the true count, the rounds refill the mirror (sync, materialsFor)")
    ca = calls(one("CraftPage", "craftAll"))
    K.check("CraftPage.countMats" in ca and "CraftPage.fitN" in ca and "CraftPage.craftOne" in ca, "BC35 craftAll: countMats, fitN, craftOne")
    ap = calls(one("CraftHubOpen", "apply"))
    K.check("CraftPage.benchShown" in ap and "PageManager.openCustomPage" in ap and ap.index("CraftPage.benchShown") < ap.index("PageManager.openCustomPage"), "BC35 CraftHubOpen.apply: the gate before the page opens")
    hd = calls(one("CraftPage", "handleDataEvent"))
    K.check("CraftPage.craftAll" in hd and "CraftPage.craftOne" not in hd, "BC35 the craft click goes through craftAll")
    K.save()


if __name__ == "__main__":
    os.makedirs(SCRATCH, exist_ok=True)
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, [],
           [("all35", run_all35), ("bc35", run_bc35), ("live", T30.T0827.run_live27), ("live2", T30.T0827.T0810.run_live10)],
           __file__, live=(BETA, "Skyy_SkyySacks"))
