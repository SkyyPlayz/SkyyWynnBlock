"""Harness for SkyySacks 0.8.10 (FISH INTO THE FISHING BAG; tools/sacks_0_8_10_patch.py) = the 0.8.9 harness's phases on the 0.8.10 jar + FISH.
Build first: python tools/sacks_0_8_10_patch.py && python SkyySacks/build_skyysacks_0.8.10.py
             (and SkyyFishing 0.1.8: python tools/fishing_0_1_8_patch.py && python SkyyFishing/build_skyyfishing_0.1.8.py)

    python SkyySacks/test_skyysacks_0.8.10.py [--keep] [--dir <scratch>]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.8.9 -> 0.8.10: exactly the planned members (SackDefs CATCH / isCatch / homeOf, SackPool fish entries, SweepTask fish stack
              side + sweep + withdraw, VoidStore landed / total / depositInv); no asset changed
  FISH NEW - the 0.8.0 harness's Void stand-ins (real SimpleItemContainers, a stand-in Item store, a scratch pool folder) WITH THE REAL
              SkyyFishing 0.1.8 jar on the class path (its FishBridge.questInit puts the real fishing:fn:fishOf / fishDoc / pond, its
              FishRig.makeFish makes the caught fish):
       F1 every SkyyFishing fish id (FishDefs.FISH) -> Fishing (catOf / homeOf / isCatch); vanilla fish + raw fish still Fishing; a tackle
          id (SkyyFishing_Hook_*) and other Skyy ids still no category
       F2 Deposit all (Fishing tab) with caught fish in storage + hotbar + backpack: every fish goes in, the pool count = the fish, the
          entries = their exact grams / mm / catcher; a fish with OTHER metadata stays; conserved
       F3 the automatic sweep: fish in the HOTBAR / backpack are taken, raw fish / stone in the hotbar are NOT (storage only, as before),
          storage raw fish are; kept: a fish taken out stays with you
       F4 take out (SweepTask.withdraw = the page / Pick up all): the newest fish comes back with the SAME metadata (BsonDocument equal),
          one per slot; storage full = it stays in the Void (count + entry unchanged); no SkyyFishing 0.1.8 = it stays; plain fish (no
          entry) come out plain
       F5 the page's Deposit (VoidStore.depositInv): fish with entries; the category room is respected (Fishing space 2 -> 2 of 3 go in)
       F6 the pool FILE keeps the entries (a ~fish line next to the count) and a restart (memory cleared) reads them back - the fish
          taken out after the restart is the same fish
       F7 another mod takes a fish by id (SackBridge.debit): the next move drops the OLDEST entry (count = entries again), never a dupe;
          plain fish added by id (a refund) come out plain
       F8 without SkyyFishing 0.1.8 (no fishing:fn:fishOf): fish with metadata stay in the inventory (nothing lost), plain fish go in
       F9 the Fishing level: total = SkyyCollections' total + the fish LANDED (fishing:fn:pond, the real one on a scratch FishStore);
          other categories unchanged; no pond function = + 0; no SkyyCollections = the old own-intake total (no double count)
  X / L / ART / FUEL / LOGS / SND / MIG / VOID   the 0.8.9 harness's phases on the 0.8.10 jar (SND needs the deleted 0.8.6 jar and MIG beta
              expects the NewBetaTest config BEFORE the 0.8.9 update that is deployed now - both fail the same way on the 0.8.9 jar itself)
  D  START TWICE on a scratch COPY of NewBetaTest's Skyy_SkyySacks (run_live10)
  AA engine-access audit
Not testable without the game (UNVERIFIED): the Fishing tab look with fish, a real catch arriving in the hotbar and the 2 s sweep taking it.
Exit code 1 on any failure.
"""
import os, sys, json, shutil, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

VERSION = "0.8.10"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-0.8.9.jar")
FISH_JAR = os.path.join(ROOT, "SkyyFishing", "SkyyFishing-0.1.8.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "fish018", "sacks")))
PKG = "com.skyy.sacks."
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_9", os.path.join(HERE, "test_skyysacks_0.8.9.py"))
T089 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T089)
T089.VERSION = VERSION          # its older phases' static checks read the 0.8.10 generated script
EXPECT = {
    "SackDefs": ["+f CATCH", "+m isCatch", "~m homeOf"],
    "SackCfg": ["+f FISH_SWEEP", "~<clinit>", "~m linkKeys"],          # review fix: bags.fishSweep
    "SackPool": ["+m fishList", "+m fishSet", "+m fishFit", "+m fishIn", "+m fishOut", "+m fishBack"],
    "SweepTask": ["+m fishEntry", "+m fishStack", "+m fishHave", "+m fishTake", "+m fishWithdraw", "~m sweep", "~m withdraw", "~m cfgSig"],
    "VoidStore": ["+m landed", "~m total", "~m depositInv"],
    "SkyySacksPlugin": ["~m setup"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CfgFile": ["~<clinit>"],          # the version text
}
BETA = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyySacks")
ADDED = []


def run_fish(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST, FISH_JAR], verify=True)
    src = open(T089.T080, encoding="utf8").read()
    a = src.index("    # ---------------- stand-ins (the 0.7.12+ harness pattern)\n")
    b = src.index("    # ---------------- D. categories\n", a)
    head = ("def run_void_fixture():\n    import jpype\n    import skyybuild as B\n"
            "    from jpype import JClass, JArray, JShort, JString, JInt, JLong, JImplements, JOverride\n"
            "    jp = JClass(\"javassist.ClassPool\")(True)\n    jp.appendClassPath(B.SERVER_JAR)\n    jp.appendClassPath(JAR)\n")
    body = head + src[a:b] + "    _VOID(locals())\n"
    ns = {"__file__": T089.T080, "__name__": "t080"}
    exec(compile(src[:src.index("def run():")], T089.T080, "exec"), ns)
    ns.update(JAR=jar, SCRATCH=os.path.join(scratch, "fish"), _VOID=lambda L: fish_cases(K, L, scratch))
    exec(compile(body, T089.T080 + " (stand-in slice)", "exec"), ns)
    try:
        ns["run_void_fixture"]()
    finally:
        for f in ns["FAILS"]:
            K.check(False, "FISH fixture: " + f)
        K.save()
        try:
            __import__("jpype").JClass(PKG + "SackPool").WRITER.shutdownNow()
        except Exception:
            pass


def fish_cases(K, L, scratch):
    from jpype import JClass, JString, JShort, JArray
    VS, Defs, Cfg, Pool, Swp, Bridge = L["VS"], L["Defs"], L["Cfg"], L["Pool"], L["Swp"], L["Bridge"]
    fresh, write_pool, player, coll, nocoll, pc, inv_counts, custom_item, drain, restart = (L[n] for n in (
        "fresh", "write_pool", "player", "coll", "nocoll", "pc", "inv_counts", "custom_item", "drain", "restart"))
    UUID, IS, bridge = L["UUID"], L["IS"], L["bridge"]
    FP = lambda n: JClass("com.skyy.fishing." + n)
    FDefs, FRig, FBrg, FStore = FP("FishDefs"), FP("FishRig"), FP("FishBridge"), FP("FishStore")
    FBrg.BRIDGE = None
    FBrg.questInit()
    K.check(bridge.get("fishing:fn:fishOf") is not None and bridge.get("fishing:fn:fishDoc") is not None and bridge.get("fishing:fn:pond") is not None,
            "FISH: the real SkyyFishing 0.1.8 questInit put its fish bridge into the same skyy.bridge map")
    keep_fn = dict((k_, bridge.get(k_)) for k_ in ("fishing:fn:fishOf", "fishing:fn:fishDoc", "fishing:fn:pond"))
    FISH = [str(x) for x in FDefs.FISH]
    RAW, STONE, BONE = "Food_Fish_Raw", "Rock_Stone_Cobble", "Ingredient_Bone_Fragment"
    for i_ in FISH:
        custom_item(i_, 1)
    for i_ in ("SkyyFishing_Hook_Barbed_I", "Skyy_Totem_Rain"):
        custom_item(i_, 16)
    BD = JClass("org.bson.BsonDocument")
    BI = JClass("org.bson.BsonInt32")
    cs = lambda i: None if Defs.catOf(JString(i)) is None else str(Defs.catOf(JString(i)))
    hs = lambda i: None if Defs.homeOf(JString(i)) is None else str(Defs.homeOf(JString(i)))
    # ---- F1
    K.check(len(FISH) == 10 and all(cs(i) == "Fishing" and hs(i) == "Fishing" and bool(Defs.isCatch(i)) for i in FISH),
            "F1: every SkyyFishing fish id (FishDefs.FISH, %d) -> Fishing (catOf, homeOf, isCatch)" % len(FISH))
    K.eq([cs(i) for i in ("Fish_Bluegill_Item", RAW, "SkyyFishing_Hook_Barbed_I", "SkyyFishing_Rod_Bamboo", "Skyy_Totem_Rain")],
         ["Fishing", "Fishing", None, None, None], "F1: vanilla fish / raw fish still Fishing; tackle, rods and other Skyy ids no category")
    K.check(not bool(Defs.isCatch("Fish_Bluegill_Item")) and not bool(Defs.isCatch(None)), "F1: isCatch = SkyyFishing whole fish only")
    fi = int(Defs.catIndex("Fishing"))

    def fish(sp, g, mm, by="SkyLordPlayz"):
        return FRig.makeFish(sp, g, mm, by)

    def meta_list(p_):
        out_ = []
        inv_ = p_.getInventory()
        for cont in (inv_.getStorage(), inv_.getHotbar(), inv_.getBackpack()):
            for s_ in range(int(cont.getCapacity())):
                it_ = cont.getItemStack(JShort(s_))
                if it_ is not None and not it_.isEmpty() and str(it_.getItemId()) in FISH:
                    out_.append((str(it_.getItemId()), int(FRig.grams(it_)), int(FRig.mm(it_)), str(FRig.str(FRig.doc(it_), "by"))))
        return sorted(out_)
    U = UUID.fromString("00000000-0000-0000-0000-0000000f1810")
    k = str(U)
    base = os.path.join(scratch, "fish")
    # ---- F2 Deposit all with fish everywhere + one with foreign metadata
    drain()
    fresh(base)
    coll(U, {"Fishing": 0})
    p = player(storage=[(RAW, 5)])
    inv = p.getInventory()
    perch = FISH.index("SkyyFishing_Fish_QueuePerch")
    f_a, f_b, f_c = fish(perch, 1780, 520), fish(perch, 630, 390), fish(0, 120, 210, "Bob")
    inv.getHotbar().addItemStack(f_a)
    inv.getStorage().addItemStack(f_b)
    inv.getBackpack().addItemStack(f_c)
    md = f_a.getMetadata().clone()
    md.put("SkyyGear", BD())
    odd = IS(FISH[perch], 1, md)
    inv.getStorage().addItemStack(odd)
    caps = VS.capsK(U, k)
    moved = int(Swp.sweep(p, k, "Fishing", True, None, caps, None))
    drain()
    after = pc(k)
    ent = sorted(str(x) for x in Pool.fishList(k, FISH[perch]))
    K.check(moved == 8 and after.get(FISH[perch]) == 2 and after.get(FISH[0]) == 1 and after.get(RAW) == 5 and ent == ["1780,520,SkyLordPlayz", "630,390,SkyLordPlayz"]
            and [str(x) for x in Pool.fishList(k, FISH[0])] == ["120,210,Bob"] and inv_counts(p) == {FISH[perch]: 1},
            "F2: Deposit all takes the 3 caught fish (hotbar, storage, backpack) + 5 raw fish; entries = their exact weight / length / catcher; "
            "the fish with OTHER metadata stays: moved %d pool %s entries %s inv %s" % (moved, after, ent, inv_counts(p)))
    # ---- F4 take out: the newest perch back with the same metadata, then the older one; storage full = stays
    # Deposit all reads storage, hotbar, backpack in that order: the 630 g perch (storage) went in first, the 1780 g one (hotbar) last
    got = int(Swp.withdraw(p, k, FISH[perch], 1))
    ml = meta_list(p)
    K.check(got == 1 and ml == [(FISH[perch], 1780, 520, "SkyLordPlayz")] * 2 and int(Pool.get(k, FISH[perch])) == 1
            and [str(x) for x in Pool.fishList(k, FISH[perch])] == ["630,390,SkyLordPlayz"],
            "F4: take out = the NEWEST perch (1780 g) back as itself (+ the odd one that never went in), one left in the Void with its entry: %s" % ml)
    st_ = inv.getStorage()
    back = None
    for s_ in range(int(st_.getCapacity())):
        it_ = st_.getItemStack(JShort(s_))
        if it_ is not None and not it_.isEmpty() and str(it_.getItemId()) == FISH[perch] and it_.getMetadata().get("SkyyGear") is None:
            back = it_
    K.check(back is not None and back.getMetadata().equals(f_a.getMetadata()), "F4: the fish taken out has the SAME metadata (document + tooltip) as when it went in")
    full = player(storage=[(STONE, 100)] * 36)   # 36 FULL stacks (max 100 in the stand-in store)
    g0 = int(Swp.withdraw(full, k, FISH[perch], 1))
    K.check(g0 == 0 and int(Pool.get(k, FISH[perch])) == 1 and [str(x) for x in Pool.fishList(k, FISH[perch])] == ["630,390,SkyLordPlayz"],
            "F4: a full storage = the fish stays in the Void (count + entry unchanged): got %d pool %d entries %s inv %s"
            % (g0, int(Pool.get(k, FISH[perch])), [str(x) for x in Pool.fishList(k, FISH[perch])], inv_counts(full)))
    bridge.remove("fishing:fn:fishDoc")
    g1 = int(Swp.withdraw(p, k, FISH[perch], 1))
    K.check(g1 == 0 and int(Pool.get(k, FISH[perch])) == 1 and len(list(Pool.fishList(k, FISH[perch]))) == 1,
            "F4: without SkyyFishing 0.1.8 (no fishing:fn:fishDoc) the fish stays in the Void - never a plain copy of a weighed fish")
    bridge.put("fishing:fn:fishDoc", keep_fn["fishing:fn:fishDoc"])
    # ---- F3 the automatic sweep: hotbar fish yes, hotbar raw fish / stone no; kept
    drain()
    fresh(base)
    coll(U, {"Fishing": 0, "Mining": 0})
    p = player(storage=[(RAW, 3)], hotbar=[(RAW, 4), (STONE, 10)])
    inv = p.getInventory()
    inv.getHotbar().addItemStack(fish(perch, 900, 450))
    inv.getBackpack().addItemStack(fish(1, 300, 300))
    Swp.sweep(p, k, None, False, None, VS.capsK(U, k), None)
    drain()
    K.check(pc(k) == {RAW: 3, FISH[perch]: 1, FISH[1]: 1} and inv_counts(p) == {RAW: 4, STONE: 10},
            "F3: the automatic sweep takes the fish from the hotbar + backpack and the storage raw fish; hotbar raw fish / stone stay (storage-only "
            "rule for everything else): pool %s inv %s" % (pc(k), inv_counts(p)))
    Swp.withdraw(p, k, FISH[perch], 1)
    Swp.sweep(p, k, None, False, None, VS.capsK(U, k), None)
    K.check(int(Pool.get(k, FISH[perch])) == 0 and inv_counts(p).get(FISH[perch]) == 1, "F3: kept - a fish you took out is not swept back in")
    inv.getHotbar().addItemStack(fish(perch, 1111, 480))
    Swp.sweep(p, k, None, False, None, VS.capsK(U, k), None)
    K.check(int(Pool.get(k, FISH[perch])) == 1 and inv_counts(p).get(FISH[perch]) == 1 and [str(x) for x in Pool.fishList(k, FISH[perch])] == ["1111,480,SkyLordPlayz"],
            "F3: a NEW catch above the kept one goes in (the kept fish stays with you)")
    # ---- FIX (fish018fix) kept: taking 1 fish out while 2 fresh catches sit in the hotbar keeps only the 1 taken - the 2 are still swept
    drain()
    fresh(base)
    coll(U, {"Fishing": 0})
    p = player()
    inv = p.getInventory()
    inv.getHotbar().addItemStack(fish(perch, 800, 400))
    Swp.sweep(p, k, None, False, None, VS.capsK(U, k), None)
    inv.getHotbar().addItemStack(fish(perch, 810, 401))
    inv.getHotbar().addItemStack(fish(perch, 820, 402))
    gk = int(Swp.withdraw(p, k, FISH[perch], 1))
    kept_k = int(Pool.kept(k, FISH[perch]))
    Swp.sweep(p, k, None, False, None, VS.capsK(U, k), None)
    K.check(gk == 1 and kept_k == 1 and int(Pool.get(k, FISH[perch])) == 2 and inv_counts(p).get(FISH[perch]) == 1
            and sorted(str(x) for x in Pool.fishList(k, FISH[perch])) == ["810,401,SkyLordPlayz", "820,402,SkyLordPlayz"]
            and [x[1] for x in meta_list(p)] == [800],
            "FIX kept: take 1 out with 2 fresh catches in the hotbar -> kept = 1 (was 3), the 2 catches are swept in, the taken fish stays: "
            "kept %d pool %d inv %s" % (kept_k, int(Pool.get(k, FISH[perch])), meta_list(p)))
    # ---- FIX (fish018fix) bags.fishSweep off: hotbar / backpack fish stay (0.8.9 rule), storage fish + Deposit all still go in; sig changes
    drain()
    fresh(base)
    coll(U, {"Fishing": 0})
    sig_on = str(Swp.cfgSig())
    Cfg.FISH_SWEEP = False
    sig_off = str(Swp.cfgSig())
    p = player()
    inv = p.getInventory()
    inv.getHotbar().addItemStack(fish(perch, 700, 350))
    inv.getBackpack().addItemStack(fish(1, 300, 300))
    inv.getStorage().addItemStack(fish(2, 500, 320))
    Swp.sweep(p, k, None, False, None, VS.capsK(U, k), None)
    off_pool, off_inv = pc(k), inv_counts(p)
    m_all = int(Swp.sweep(p, k, "Fishing", True, None, VS.capsK(U, k), None))
    Cfg.FISH_SWEEP = True
    K.check(sig_on != sig_off and off_pool == {FISH[2]: 1} and off_inv == {FISH[perch]: 1, FISH[1]: 1} and m_all == 2 and inv_counts(p) == {}
            and int(Pool.get(k, FISH[perch])) == 1 and int(Pool.get(k, FISH[1])) == 1,
            "FIX switch: bags.fishSweep off -> the 2 s sweep leaves hotbar / backpack fish (storage fish still go in), Deposit all still takes "
            "them; the switch is in cfgSig (a change re-sweeps): pool %s inv %s all %d" % (off_pool, off_inv, m_all))
    cfgf = os.path.join(base, "cfg-fish.properties")
    for txt_, want_ in (("bags.fishSweep=false" + chr(10), False), (chr(10), True), ("bags.fishSweep=true" + chr(10), True)):
        with open(cfgf, "w", encoding="latin-1") as f_:
            f_.write(txt_)
        P_ = JClass("java.util.Properties")()
        ins_ = JClass("java.io.FileInputStream")(cfgf)
        P_.load(ins_)
        ins_.close()
        Cfg.linkKeys(P_, False)
        K.check(bool(Cfg.FISH_SWEEP) == want_, "FIX switch: config.properties %r -> FISH_SWEEP %s (SackCfg.linkKeys = the reload)" % (txt_.strip(), want_))
    # ---- FIX (fish018fix) take-out: the storage THROWS while the fish is added -> back in the Void unless the storage really got it
    from jpype import JClass as JC_
    SICN = "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer"
    ISTN = str(JC_(SICN).class_.getMethod("addItemStack", IS.class_).getReturnType().getName())
    jp_, CtF_, CtC_, CtM_ = L["jp"], L["CtF"], L["CtC"], L["CtM"]
    ab = jp_.makeClass("com.hypixel.hytale.server.core.inventory.container.SkyyTestAddBoom", jp_.get(SICN))
    ab.addField(CtF_.make("public static volatile int MODE = 0;", ab))
    ab.addConstructor(CtC_.make("public SkyyTestAddBoom(short n) { super(n); }", ab))
    ab.addMethod(CtM_.make(("public %s addItemStack(%s st) { int m = MODE; MODE = 0; if (m == 1) throw new IllegalStateException(\"add boom\"); "
                            "%s r = super.addItemStack(st); if (m == 2) throw new IllegalStateException(\"boom after add\"); return r; }")
                           % (ISTN, IS.class_.getName(), ISTN), ab))
    AB = JC_(ab.toClass(JC_(SICN).class_))
    drain()
    fresh(base)
    coll(U, {"Fishing": 0})
    pb = player()
    pb.getInventory().getHotbar().addItemStack(fish(perch, 1500, 500))
    pb.getInventory().getHotbar().addItemStack(fish(perch, 1600, 510))
    Swp.sweep(pb, k, None, False, None, VS.capsK(U, k), None)
    SIC_ = JC_(SICN)
    p_b = L["us"].allocateInstance(L["PLA"].class_)
    L["inv_field"].set(p_b, L["TInv"](AB(JShort(36)), SIC_(JShort(9)), SIC_(JShort(9))))
    AB.MODE = 1
    try:
        g1 = int(Swp.withdraw(p_b, k, FISH[perch], 1))
        thr1 = None
    except Exception as ex_:
        g1, thr1 = -1, str(ex_)[:120]
    K.check(thr1 is None and g1 == 0 and int(Pool.get(k, FISH[perch])) == 2 and len(list(Pool.fishList(k, FISH[perch]))) == 2 and meta_list(p_b) == [],
            "FIX take-out: the storage throws BEFORE adding -> nothing thrown out of withdraw, the fish + its entry are back in the Void (no loss): "
            "got %d pool %d thrown %s" % (g1, int(Pool.get(k, FISH[perch])), thr1))
    AB.MODE = 2
    try:
        g2 = int(Swp.withdraw(p_b, k, FISH[perch], 1))
        thr2 = None
    except Exception as ex_:
        g2, thr2 = -1, str(ex_)[:120]
    K.check(thr2 is None and g2 == 1 and int(Pool.get(k, FISH[perch])) == 1 and len(list(Pool.fishList(k, FISH[perch]))) == 1
            and meta_list(p_b) == [(FISH[perch], 1600, 510, "SkyLordPlayz")],
            "FIX take-out: the storage throws AFTER adding -> the fish counts as out (it is in the storage), the Void holds 1 - never doubled: "
            "got %d pool %d inv %s" % (g2, int(Pool.get(k, FISH[perch])), meta_list(p_b)))
    # ---- F5 the page's Deposit + the category room
    drain()
    fresh(base)
    coll(U, {"Fishing": 0})
    p = player()
    inv = p.getInventory()
    for g_ in (500, 600, 700):
        inv.getHotbar().addItemStack(fish(perch, g_, 400))
    old_pl = int(Cfg.PD_PER_LEVEL)
    Cfg.PD_PER_LEVEL = 2
    r5 = int(VS.depositInv(p, U, k, FISH[perch], -1))
    Cfg.PD_PER_LEVEL = old_pl
    K.check(r5 == 2 and int(Pool.get(k, FISH[perch])) == 2 and len(list(Pool.fishList(k, FISH[perch]))) == 2 and inv_counts(p).get(FISH[perch]) == 1,
            "F5: the page's Deposit takes fish with their entries and respects the Fishing space (2 of 3): %d" % r5)
    r5b = int(VS.depositInv(p, U, k, FISH[perch], -1))
    K.check(r5b == 1 and int(Pool.get(k, FISH[perch])) == 3, "F5: with room again the third fish goes in")
    # ---- F6 the file keeps the entries; a restart reads them back
    ent6 = [str(x) for x in Pool.fishList(k, FISH[perch])]
    Pool.saveNow(k)
    txt = open(os.path.join(base, "pools", k + ".properties"), encoding="latin-1").read()
    restart()
    ent6b = [str(x) for x in Pool.fishList(k, FISH[perch])]
    K.check("~fish\\:" + FISH[perch] in txt and (FISH[perch] + "=3") in txt and ent6b == ent6 and int(Pool.get(k, FISH[perch])) == 3,
            "F6: the pool file holds the count + a ~fish line with the entries; a restart reads the same entries back: %s" % ent6b)
    p6 = player()
    Swp.withdraw(p6, k, FISH[perch], 1)
    K.check(meta_list(p6) == [(FISH[perch], int(ent6[-1].split(",")[0]), 400, "SkyLordPlayz")], "F6: after the restart the newest fish comes out as itself")
    # ---- F7 another mod takes one by id: the oldest entry goes; a refund by id comes out plain
    left7 = [str(x) for x in Pool.fishList(k, FISH[perch])]
    Bridge.debit(k, FISH[perch], 1)
    p7 = player()
    Swp.withdraw(p7, k, FISH[perch], 1)
    K.check(int(Pool.get(k, FISH[perch])) == 0 and len(list(Pool.fishList(k, FISH[perch]))) == 0 and meta_list(p7) == [(FISH[perch], int(left7[-1].split(",")[0]), 400, "SkyLordPlayz")],
            "F7: 2 fish + 2 entries, another mod debits 1 by id -> the next take drops the OLDEST entry and gives the newest fish; nothing left, no dupe")
    Pool.add(k, FISH[perch], 1)
    p7b = player()
    Swp.withdraw(p7b, k, FISH[perch], 1)
    it7 = p7b.getInventory().getStorage().getItemStack(JShort(0))
    K.check(int(Pool.get(k, FISH[perch])) == 0 and it7 is not None and str(it7.getItemId()) == FISH[perch] and (it7.getMetadata() is None or it7.getMetadata().isEmpty()),
            "F7: a fish added by id without an entry (a refund) comes out plain")
    # ---- F8 no SkyyFishing 0.1.8
    drain()
    fresh(base)
    coll(U, {"Fishing": 0})
    for k_ in keep_fn:
        bridge.remove(k_)
    p = player()
    p.getInventory().getHotbar().addItemStack(fish(perch, 1500, 500))
    p.getInventory().getHotbar().addItemStack(IS(FISH[2], 1))
    m8 = int(Swp.sweep(p, k, "Fishing", True, None, VS.capsK(U, k), None))
    K.check(m8 == 1 and pc(k) == {FISH[2]: 1} and [x[1] for x in meta_list(p)] == [1500],
            "F8: without fishing:fn:fishOf a weighed fish stays in the inventory (nothing lost), a plain fish goes in")
    for k_, v_ in keep_fn.items():
        bridge.put(k_, v_)
    # ---- F9 the Fishing level: + the fish you landed
    FStore.start(JClass("java.nio.file.Paths").get(os.path.join(base, "fmods")))
    FStore.setPond(k, 40)
    coll(U, {"Fishing": 10, "Mining": 25})
    t9 = [int(VS.total(U, k, ci_)) for ci_ in range(6)]
    K.check(t9[fi] == 50 and t9[int(Defs.catIndex("Mining"))] == 25, "F9: Fishing total = SkyyCollections' 10 + 40 landed; Mining unchanged: %s" % t9)
    lv = int(VS.level(U, k, fi))
    K.check(lv == int(VS.levelOf(50, fi)) and lv > int(VS.levelOf(10, fi)), "F9: the Fishing level counts the landed fish (Lv %d)" % lv)
    bridge.remove("fishing:fn:pond")
    K.check(int(VS.total(U, k, fi)) == 10 and int(VS.landed(U, fi)) == 0, "F9: no fishing:fn:pond = + 0")
    bridge.put("fishing:fn:pond", keep_fn["fishing:fn:pond"])
    nocoll()
    s9 = VS.st(k)
    own = int(s9.own[fi]) if s9 is not None else 0
    K.check(int(VS.total(U, k, fi)) == own, "F9: without SkyyCollections the old own-intake total (no pond added - the deposits already count)")
    drain()


def run_live10(out, jar, scratch, home):
    """D: START TWICE on a scratch COPY of the deployed world's Skyy_SkyySacks (NewBetaTest; the 0.8.8 harness's live chain needs the
    deleted 0.8.6 / 0.8.7 jars): every pool file reads with 0.8.10 (counts + "~" meta lines), a save + a fresh read (start 2) give the
    same Properties, every whole fish id in it is Fishing now, the config file reads twice without a byte changed"""
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    Pool, Cfg, Defs = JClass(PKG + "SackPool"), JClass(PKG + "SackCfg"), JClass(PKG + "SackDefs")
    Paths = JClass("java.nio.file.Paths")
    Pool.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySacks")
    pdir = os.path.join(home, "pools")
    keys = sorted(f[:-11] for f in os.listdir(pdir) if f.endswith(".properties")) if os.path.isdir(pdir) else []
    K.check(len(keys) > 0, "D: the live copy has pool files (%d)" % len(keys))

    def props(f):
        P_ = JClass("java.util.Properties")()
        ins = JClass("java.io.FileInputStream")(f)
        P_.load(ins)
        ins.close()
        return dict((str(k_), str(P_.getProperty(k_))) for k_ in P_.stringPropertyNames())
    before = dict((k_, props(os.path.join(pdir, k_ + ".properties"))) for k_ in keys)
    cfg0 = open(os.path.join(home, "config.properties"), "rb").read()
    for start in (1, 2):
        Pool.POOLS.clear()
        Pool.PMETA.clear()
        Pool.DIR = Paths.get(pdir)
        Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
        Cfg.MTIME = -1
        Cfg.reload()
        bad = []
        for k_ in keys:
            m = Pool.pool(k_)
            got = dict((str(e.getKey()), str(e.getValue())) for e in m.entrySet())
            meta = Pool.PMETA.get(k_)
            if meta is not None:
                got.update(dict((str(e.getKey()), str(e.getValue())) for e in meta.entrySet()))
            want = dict((kk, vv.strip()) for kk, vv in before[k_].items() if kk.startswith("~") or int(vv.strip() or 0) > 0)
            if got != want:
                bad.append((k_, sorted(set(got.items()) ^ set(want.items()))[:4]))
            Pool.saveNow(k_)
        K.check(not bad, "D start %d: every live pool file reads with 0.8.10 (counts + meta lines) and is saved back: %s" % (start, bad[:2]))
    after = dict((k_, props(os.path.join(pdir, k_ + ".properties"))) for k_ in keys)
    K.check(all(dict((kk, vv.strip()) for kk, vv in after[k_].items()) == dict((kk, vv.strip()) for kk, vv in before[k_].items()
                if kk.startswith("~") or int(vv.strip() or 0) > 0) for k_ in keys),
            "D: after two starts + saves the pool files hold the same lines (Properties equal)")
    K.check(open(os.path.join(home, "config.properties"), "rb").read() == cfg0, "D: the config file is byte-identical after two reads")
    fish = sorted(set(kk for k_ in keys for kk in before[k_] if kk.startswith("SkyyFishing_Fish_")))
    K.check(all(str(Defs.homeOf(f_)) == "Fishing" for f_ in fish), "D: whole fish already in a live pool (%s) are Fishing now" % fish)
    K.notes.append("D: %d live pool files, %d lines" % (len(keys), sum(len(v) for v in before.values())))
    K.save()


if __name__ == "__main__":
    print("kit:", T089.KIT_NOTE)
    assert os.path.isfile(FISH_JAR), "build SkyyFishing 0.1.8 first: " + FISH_JAR
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("fish", run_fish),
            ("exec", T089._phase("exec", True)), ("late", T089._phase("late", True)), ("art", T089._phase("art", True)), ("fuel", T089._phase("fuel")),
            ("logs", T089._phase("logs", True)), ("snd", T089._phase("snd")), ("mig", T089.run_mig), ("void", T089.run_void),
            ("live", run_live10)],
           __file__, live=(BETA, "Skyy_SkyySacks"))
