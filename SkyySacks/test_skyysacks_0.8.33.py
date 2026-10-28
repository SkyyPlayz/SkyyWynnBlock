"""Harness for SkyySacks 0.8.33 (round sacks33 - tools/sacks_0_8_33_patch.py: pocket crafting ALL / x10 - Skyy "the craft all doesnt work, it crafts 1").
Build first:
    python tools/sacks_0_8_33_patch.py && python SkyySacks/build_skyysacks_0.8.33.py

    python SkyySacks/test_skyysacks_0.8.33.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A / C   verify (-Xverify:all) + compare 0.8.32 -> 0.8.33 (only the classes the patch touches)
  0.8.30 / 0.8.31 / 0.8.32 phases re-run on the 0.8.33 jar (rbr's reader = the 0.8.32 jar = the rollback)
  POCKET33 on the 0.8.9 Void stand-ins: a Fieldcraft set of ~230 recipes (111 forward 100 -> 1 Enchanted, 111 reverse, normal ones):
        (0) the 0.8.32 set (addInputs for all) reproduces Skyy's bug: Wheat 859 in the Pocket -> 100 offered, ALL = 1, low piles starved;
        (1) fieldRecipe sorts the recipes; (2) no focus: every real ingredient + every Enchanted item keeps its slot; (3) focus via
        BenchLink.focus + union: 859 Wheat all offered, x10 refused (nothing moved), ALL = 8 crafts take exactly 800, pool + inventory
        exact, then short = 0, the inventory part counts; 2500 Wheat -> 1200 offered, x10 works; (4) a bench open at the same time keeps
        W 1 + W 4 (every bench id its 4 stacks); (5) no virtual Wheat; (6) same inputs = same layout + version (no refresh loop), a focus
        change moves it once; a non-pocket set keeps the 0.8.32 order.
  BC33 bytecode: fieldWanted -> BagMirror.fieldRecipe (no addInputs), PocketCraftWindow.handleAction -> BenchLink.focus before craftItem,
        start() clears PFOCUS
Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_argv = list(sys.argv)
_RC = HK.run_compare
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_32", os.path.join(HERE, "test_skyysacks_0.8.32.py"))
T32 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T32)
sys.argv = _argv
HK.run_compare = _RC
T31, T30, T089 = T32.T31, T32.T30, T32.T089

VERSION = "0.8.33"
OLD_VERSION = "0.8.32"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-%s.jar" % OLD_VERSION)
T30.OLD_JAR = OLD_JAR          # the rollback reader (run_rbr) = 0.8.32 now
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sacks33", "h")))
PKG = "com.skyy.sacks."
BETA = T32.BETA
EXPECT = {"SkyySacksPlugin": ["~m setup"],
          "BagMirror": ["+f CAP", "+m fieldRecipe", "+m marked", "~c ", "~m empty", "~m fit0", "~m holds", "~m quantities", "~m rebuild",
                        "~m sync"],
          "BenchLink": ["+f PFOCUS", "+m focus", "~m fieldWanted", "~m union", "~m start", "~<clinit>"],
          "PocketCraftWindow": ["~m handleAction"],
          "CfgRows": ["~m header"], "CfgFn": ["~m opExport"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
WHEAT = "Plant_Crop_Wheat_Item"
LE, LEC = "Ingredient_Life_Essence", "Ingredient_Life_Essence_Concentrated"


def cases33(K, L, scratch):
    from jpype import JClass, JString, JArray, JInt, JFloat, JLong
    VS, Defs, Pool, Mirror, Swp = L["VS"], L["Defs"], L["Pool"], L["Mirror"], L["Swp"]
    fresh, write_pool, player, pc, inv_counts, custom_item, drain = (L[n] for n in (
        "fresh", "write_pool", "player", "pc", "inv_counts", "custom_item", "drain"))
    UUID, bridge = L["UUID"], L["bridge"]
    VC, CP, BL, LR = (JClass(PKG + n) for n in ("VoidCompact", "CraftPage", "BenchLink", "LinkRec"))
    MQ = JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
    CRc = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    BR = JClass("com.hypixel.hytale.protocol.BenchRequirement")
    CRM = JClass("com.hypixel.hytale.builtin.crafting.component.CraftingManager")
    CIC = JClass("com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer")
    ICa = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
    HS, AL, OA = JClass("java.util.HashSet"), JClass("java.util.ArrayList"), JClass("java.lang.Object")
    np = int(VC.np())
    bases = [str(VC.baseAt(i)) for i in range(np)]
    enchs = [str(VC.enchAt(i)) for i in range(np)]
    for i_ in bases + enchs + ["Skyy_Test_Out33"]:
        custom_item(i_, 100)
    drain()
    base = os.path.join(scratch, "pocket33")
    U = UUID.fromString("00000000-0000-0000-0000-0000000c0833")
    k = str(U)

    def mk(pool):
        drain()
        fresh(base)
        bridge.put(JString("coll:recipes:" + k), JString(""))
        write_pool(os.path.join(base, "pools"), k, pool)
        VS.st(k).first = 1

    def recipe(rid, ins, out="Skyy_Test_Out33"):
        mi = JArray(MQ)([MQ(JString(i), None, None, JInt(q), None) for i, q in ins])
        po = MQ(JString(out), None, None, JInt(1), None)
        r = CRc(mi, po, JArray(MQ)([po]), JInt(1), JArray(BR)(0), JFloat(0.0), False, JInt(0))
        f = CRc.class_.getDeclaredField("id")
        f.setAccessible(True)
        f.set(r, JString(rid))
        return r

    def offered(m, iid):
        return sum(int(m.slotQty[i]) for i in range(len(m.slotIds)) if m.slotIds[i] is not None and str(m.slotIds[i]) == iid)

    def stacks(m, iid):
        return sum(1 for i in range(len(m.slotIds)) if m.slotIds[i] is not None and str(m.slotIds[i]) == iid)

    def used(m):
        return sum(1 for i in range(len(m.slotIds)) if m.slotIds[i] is not None)

    # ---- the Fieldcraft set: forward (100 base -> 1 Enchanted, + Essence of Life -> Greater), reverse, normal recipes
    homed = [b for b in bases if Defs.homeOf(JString(b)) is not None and Defs.homeOf(JString(enchs[bases.index(b)])) is not None]
    K.check(WHEAT in homed and len(homed) >= 60, "POCKET33 stand-ins: %d of %d pairs have bag homes (Wheat among them)" % (len(homed), np))
    fwd = [recipe("Skyy_Test_F33_%d" % i, [(bases[i], 100)], enchs[i]) for i in range(np)]
    rev = [recipe("Skyy_Test_R33_%d" % i, [(enchs[i], 1)], bases[i]) for i in range(np)]
    # the real Fieldcraft ingredients: the bases NOT used here as piles (the last 12 homed) stand in for fibre / sticks / sap ...
    normal_ids = homed[-12:]
    piles = [b for b in homed if b not in normal_ids and b != WHEAT][:60]
    norm = [recipe("Skyy_Test_N33_%d" % j, [(normal_ids[j], 2), (normal_ids[(j + 1) % 12], 1)]) for j in range(12)]
    allr = fwd + rev + norm
    S = HS()
    nfalse = sum(1 for r in allr if not bool(Mirror.fieldRecipe(S, r)))
    S.add(JString("!pocket"))
    S0 = HS()   # the 0.8.32 fieldWanted: addInputs for every recipe
    for r in allr:
        Mirror.addInputs(S0, r.getInput())
    S0.add(JString("!pocket"))
    sl = [str(x) for x in S]
    K.check(len(allr) >= 230 and nfalse == np and ("!cb:" + WHEAT) in sl and WHEAT not in sl and ("!cb:" + LE) in sl
            and enchs[bases.index(WHEAT)] in sl and normal_ids[0] in sl and ("!e:" + WHEAT) in sl and "!open" in sl,
            "POCKET33 fieldRecipe: %d recipes; the %d compress ones (Skyy_Ench_* + Greater Essence) mark their base '!cb:' only, the reverse "
            "+ normal ones add their inputs (Enchanted Wheat, the ingredients, !e: / !open markers)" % (len(allr), nfalse))

    # Skyy's pool: 859 Wheat, 60 bigger piles, 12 small real ingredients, a few Enchanted items
    pool0 = {WHEAT: 859}
    for j, b in enumerate(piles):
        pool0[b] = 900 + 37 * j
    for j, b in enumerate(normal_ids):
        pool0[b] = 3 + j
    ench_have = [enchs[bases.index(b)] for b in piles[:5]] + [enchs[bases.index(WHEAT)]]
    for e in ench_have:
        pool0[e] = 2
    rW = fwd[bases.index(WHEAT)]
    TP = L["TPlayers"]

    def comb(p, m):
        return CIC(JArray(ICa)([p.getInventory().getCombinedBackpackStorageHotbar(), m.cont]))

    # ---- (0) the 0.8.32 set reproduces the bug
    mk(pool0)
    p = player(storage=[])
    caps = Swp.caps(p.getInventory())
    m = Mirror.of(k)
    S0.remove(JString("!pocket"))   # 0.8.32's rebuild read "!pocket" only in virtuals: without it = the 0.8.32 layout (36 slots, W 1 / W 4 / O 4)
    m.rebuild(caps, S0)
    S0.add(JString("!pocket"))
    starved = [b for b in normal_ids if offered(m, b) == 0]
    K.notes.append("POCKET33 (0) 0.8.32 layout: %d wanted ids, Wheat 859 -> %d offered, ALL = %d, %d of 12 small real ingredients starved"
                   % (S0.size(), offered(m, WHEAT), int(CP.limit(rW, comb(p, m))), len(starved)))
    K.check(offered(m, WHEAT) <= 100 and int(CP.limit(rW, comb(p, m))) <= 1 and len(starved) > 0,
            "POCKET33 (0) ROOT CAUSE: with the 0.8.32 set (~%d wanted ids) Wheat 859 -> %d offered, ALL = %d; %d of 12 real Fieldcraft "
            "ingredients get no slot at all" % (S0.size(), offered(m, WHEAT), int(CP.limit(rW, comb(p, m))), len(starved)))

    # ---- (2) the new set, no focus yet
    BL.PFOCUS.clear()
    m.sync()
    m.rebuild(caps, S)
    okn = all(offered(m, b) == pool0[b] for b in normal_ids) and all(offered(m, e) == 2 for e in ench_have)
    lowp = min(offered(m, b) for b in piles)
    K.notes.append("POCKET33 (2) 0.8.33 first look: Wheat %d offered (ALL %d), lowest pile %d, %d of %d slots used"
                   % (offered(m, WHEAT), int(CP.limit(rW, comb(p, m))), lowp, used(m), len(m.slotIds)))
    K.check(okn and offered(m, WHEAT) >= 400 and lowp >= 400 and int(CP.limit(rW, comb(p, m))) >= 4 and len(m.slotIds) == 512,
            "POCKET33 (2) no focus (512 slots): all 12 small real ingredients + the %d Enchanted items fully offered, every one of the 61 "
            "piles at least 4 stacks (lowest %d), Wheat %d -> ALL %d on the first look; %d slots used"
            % (len(ench_have), lowp, offered(m, WHEAT), int(CP.limit(rW, comb(p, m))), used(m)))

    # ---- (3) focus through BenchLink.focus + union (the pocket record attached)
    rec = LR(OA())
    rec.attached = True
    rec.key = JString(k)
    rec.wanted = S
    l_ = AL()
    l_.add(rec)
    BL.RECS.put(U, l_)
    BL.focus(U, rW)
    un = BL.union(U, JString(k))
    us_ = [str(x) for x in un]
    K.check(("!f:" + WHEAT) in us_ and "!bench" not in us_ and "!pocket" in us_,
            "POCKET33 (3) BenchLink.focus(Enchanted Wheat) -> union carries '!f:%s', no '!bench' (pocket alone)" % WHEAT)
    m.sync()
    m.rebuild(caps, un)
    okn = all(offered(m, b) == pool0[b] for b in normal_ids) and all(offered(m, e) == 2 for e in ench_have)
    K.check(offered(m, WHEAT) == 859 and stacks(m, WHEAT) == 9 and int(CP.limit(rW, comb(p, m))) == 8 and okn and not m.vpair.containsKey(JString(WHEAT)),
            "POCKET33 (3) focus: all 859 Wheat offered (9 stacks), ALL = 8; the small ingredients + Enchanted items keep their slots; "
            "no virtual Wheat (got %d, ALL %d)" % (offered(m, WHEAT), int(CP.limit(rW, comb(p, m)))))
    b0 = pc(k)
    c = comb(p, m)
    lim = int(CP.limit(rW, c))
    x10 = lim >= 10
    if x10:
        c.removeMaterials(CRM.getInputMaterials(rW, 10))
    m.sync()
    K.check(not x10 and pc(k) == b0, "POCKET33 (3) x10 with 859: refused by the all-or-nothing check (limit %d) - nothing moved" % lim)
    c.removeMaterials(CRM.getInputMaterials(rW, lim))
    took = m.sync()
    a = pc(k)
    exp = dict(b0)
    exp[WHEAT] = 59
    K.check(took == 800 and a == exp and inv_counts(p) == {},
            "POCKET33 (3) ALL = 8 crafts take exactly 800 Wheat (sync booked %d): pool Wheat 859 -> %d, every other id unchanged, inventory empty"
            % (took, a.get(WHEAT, 0)))
    m.rebuild(caps, BL.union(U, JString(k)))
    K.check(offered(m, WHEAT) == 59 and int(CP.limit(rW, comb(p, m))) == 0, "POCKET33 (3) then 59 left: offered 59, ALL = 0 (stops when short)")
    p2 = player(storage=[(WHEAT, 41)])
    m.sync()
    m.rebuild(caps, BL.union(U, JString(k)))
    c2 = comb(p2, m)
    K.check(int(CP.limit(rW, c2)) == 1, "POCKET33 (3) 41 Wheat on you + 59 in the Pocket: ALL = 1")
    c2.removeMaterials(CRM.getInputMaterials(rW, 1))
    took = m.sync()
    a = pc(k)
    K.check(inv_counts(p2).get(WHEAT, 0) == 0 and a.get(WHEAT, 0) == 0 and took == 59,
            "POCKET33 (3) that craft takes the 41 carried first, then 59 from the Pocket (exactly 100): pool %s, inventory %s"
            % (a.get(WHEAT, 0), inv_counts(p2)))
    # 2500 Wheat: 12 stacks = 1200, x10 works
    pool2 = dict(pool0)
    pool2[WHEAT] = 2500
    mk(pool2)
    m = Mirror.of(k)
    m.rebuild(caps, BL.union(U, JString(k)))
    c = comb(p, m)
    K.check(offered(m, WHEAT) == 1200 and int(CP.limit(rW, c)) == 12, "POCKET33 (3) 2500 Wheat: 12 stacks = 1200 offered, ALL = 12 (got %d)" % offered(m, WHEAT))
    c.removeMaterials(CRM.getInputMaterials(rW, 10))
    took = m.sync()
    K.check(took == 1000 and pc(k).get(WHEAT) == 1500, "POCKET33 (3) x10 works: exactly 1000 taken, 1500 left")
    m.rebuild(caps, BL.union(U, JString(k)))
    K.check(offered(m, WHEAT) == 1200, "POCKET33 (3) the next rebuild offers 1200 again (12 more crafts)")
    # every id in the mirror never exceeds the pool (fit trims)
    over = [str(m.slotIds[i]) for i in range(len(m.slotIds)) if m.slotIds[i] is not None and offered(m, str(m.slotIds[i])) > pc(k).get(str(m.slotIds[i]), 0)]
    K.check(not over, "POCKET33 (3) nothing offered beyond the pool: %s" % over)

    # ---- (4) a bench open at the same time keeps its slots (W 1 + W 4 before the pocket extras)
    bench_ids = piles[5:10]   # no Enchanted of these in the pool: no 0.8.30 virtual stacks in the bench-alone check
    Bset = HS()
    Mirror.addInputs(Bset, JArray(MQ)([MQ(JString(b), None, None, JInt(1), None) for b in bench_ids]))
    brec = LR(OA())
    brec.attached = True
    brec.key = JString(k)
    brec.wanted = Bset
    l_.add(brec)
    mk(pool0)
    m = Mirror.of(k)
    un = BL.union(U, JString(k))
    m.rebuild(caps, un)
    bst = [stacks(m, b) for b in bench_ids]
    K.check("!bench" in [str(x) for x in un] and bst == [4] * 5 and all(offered(m, b) == pool0[b] for b in normal_ids)
            and stacks(m, WHEAT) == 9,
            "POCKET33 (4) bench + pocket: every bench id keeps its 4 stacks %s, the small ingredients theirs, Wheat gets the rest (%d stacks)"
            % (bst, stacks(m, WHEAT)))
    l_.remove(brec)

    # ---- (5) Enchanted Wheat in the pool: still no virtual Wheat in the pocket
    pool3 = dict(pool0)
    pool3[enchs[bases.index(WHEAT)]] = 9
    mk(pool3)
    m = Mirror.of(k)
    m.rebuild(caps, BL.union(U, JString(k)))
    K.check(not m.vpair.containsKey(JString(WHEAT)) and offered(m, WHEAT) == 859, "POCKET33 (5) 9 Enchanted Wheat in the Pocket: no virtual Wheat (859 real only)")

    # ---- (6) no refresh loop; a focus change moves the version once; the non-pocket order unchanged
    un = BL.union(U, JString(k))
    s1 = str(m.rebuild(caps, un))
    v1 = int(m.ver)
    s2 = str(m.rebuild(caps, BL.union(U, JString(k))))
    K.check(s1 == s2 and int(m.ver) == v1, "POCKET33 (6) same pool + same union: the same layout, the version stays (no refresh loop)")
    BL.focus(U, fwd[bases.index(piles[-1])])
    m.rebuild(caps, BL.union(U, JString(k)))
    v2 = int(m.ver)
    m.rebuild(caps, BL.union(U, JString(k)))
    K.check(v2 == v1 + 1 and int(m.ver) == v2 and stacks(m, piles[-1]) == 12 and stacks(m, WHEAT) <= 4,
            "POCKET33 (6) a craft of another recipe moves the focus: the version moves once, then stays; its base (%d) gets 12 stacks (%d), "
            "Wheat back to its share (%d)" % (pool0[piles[-1]], stacks(m, piles[-1]), stacks(m, WHEAT)))
    # a bench set alone (no "!pocket"): the old W 1 / W 4 / O 4 order - all piles of 900+ -> the bench ids 4 stacks, the rest by count
    m.rebuild(caps, Bset)
    K.check([stacks(m, b) for b in bench_ids] == [4] * 5 and used(m) == 36 and stacks(m, WHEAT) == 0
            and all(m.slotIds[i] is None for i in range(36, len(m.slotIds))),
            "POCKET33 (6) a bench set without '!pocket': the 0.8.32 order (bench ids 4 stacks each, then the biggest piles - Wheat 859 not among them)")
    BL.RECS.remove(U)
    BL.PFOCUS.clear()
    drain()


def run_pocket33(out, jar, scratch, home):
    T089.void_cases = cases33
    T089.run_void(out, jar, scratch, home)


def run_bc33(out, jar, scratch, _home):
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
            elif op == "invokeinterface":
                idx = ci.u16bitAt(i + 1)
                seen.append(str(cpool.getInterfaceMethodrefClassName(idx)).split(".")[-1] + "." + str(cpool.getInterfaceMethodrefName(idx)))
        return seen
    fw = calls(cp.get(PKG + "BenchLink").getDeclaredMethod("fieldWanted"))
    K.check("BagMirror.fieldRecipe" in fw and "BagMirror.addInputs" not in fw, "BC33 fieldWanted sorts each recipe with BagMirror.fieldRecipe (no addInputs)")
    ha = calls(cp.get(PKG + "PocketCraftWindow").getDeclaredMethod("handleAction"))
    K.check("BenchLink.focus" in ha and "CraftingManager.craftItem" in ha and ha.index("BenchLink.focus") < ha.index("CraftingManager.craftItem"),
            "BC33 PocketCraftWindow.handleAction sets the focus before CraftingManager.craftItem")
    st = calls(cp.get(PKG + "BenchLink").getDeclaredMethod("start"))
    K.check("ConcurrentHashMap.clear" in st, "BC33 BenchLink.start clears PFOCUS (with WARNED)")
    K.save()


if __name__ == "__main__":
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, [],
           [("cmp30", T30.run_cmp30), ("sweephook", T30.run_sweephook), ("rbw", T30.run_rbw), ("rbr", T30.run_rbr),
            ("cmp31", T31.run_cmp31), ("cmp32", T32.run_cmp32), ("tick32", T32.run_tick32), ("pocket33", run_pocket33), ("bc33", run_bc33),
            ("live", T30.T0827.run_live27), ("live2", T30.T0827.T0810.run_live10), ("live31", T32.run_live31b), ("live32", T32.run_live32)],
           __file__, live=(BETA, "Skyy_SkyySacks"))
