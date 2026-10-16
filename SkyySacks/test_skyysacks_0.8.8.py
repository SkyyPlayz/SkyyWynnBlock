"""Harness for SkyySacks 0.8.8 (FURNACE FUEL + TIER LOGS + /craft TIER ORDER AND NAMES; tools/sacks_0_8_8_patch.py).
Build first: python tools/sacks_0_8_8_patch.py && python SkyySacks/build_skyysacks_0.8.8.py

    python SkyySacks/test_skyysacks_0.8.8.py [--keep] [--dir <scratch>]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.8.7 -> 0.8.8: ProcBench (+ benchScore, config, outName), SackDefs (+ LOGT_IDS / LOGT_TIER / LOGT_KEY, logTier,
              members, unitName, unitKey, DNAMES, tr, dname, rtName), VoidStore (+ haveOf, takeOrder, upgrade), SacksPage (upgradeBox),
              RecipeCmp (+ tierKey, level, sortKey, sortName), CraftPage (build, buildProc, pretty), the cost rows' help line and the
              version texts only
  X / L / ART / SND / D   the 0.8.7 harness's exec, late, artifacts, sound and live phases on the 0.8.8 jar
  FUEL NEW, on the REAL asset stores (the 0.7.14 harness's V loader: the vanilla pack of Assets.zip loaded store by store, + the bench
              type codecs BlockTypeModule.setup registers and the crafting interaction types CraftingPlugin.setup registers) and a
              scratch pack that adds a Processing bench "Furnace" WITHOUT fuel (the Dynamic Seasons Bench_Lightning_Rod case):
                ProcBench.config("Furnace") = Bench_Furnace's bench (Fuel slot, ExtraOutput charcoal, tier 2 = 30 percent faster), the
                pack's no-fuel "Furnace" scores lower (benchScore), one INFO line names the skipped block; benchNeedsFuel: Furnace and
                Campfire yes, Tannery and Salvagebench no (vanilla); a queue that was smelting fuel-free (needsFuel false, as 0.8.7 left
                it): advance() -> needsFuel true, paused, "OUT OF FUEL - load fuel to continue", nothing lost; fuel loaded -> it runs
  LOGS NEW, on the 0.8.0 harness's Void stand-ins (fixture slice): the tier table (members / unitName / logTier); the Foraging Unique
              upgrade with MIXED tier-1 logs (Void + inventory) reaches the 500 Oak line; Maple / Apple (other tier / no tier) never
              count; too few -> refused with the tier total, nothing moved; take order = the log the player has most of first, the Void
              before the inventory, exactly the cost, conserved; two lines of one tier add up; a crash part-way through the inventory
              take -> every slot and the Void as before, no rarity; the same upgrade afterwards pays exactly once; the page's upgrade
              box shows "Oak-tier logs" and the tier count; Mining (no logs) unchanged; (review fix) two lines of one group: the page shows
              the running sum and disables Upgrade exactly when the upgrade check refuses
  ORDER / NAMES (same child): RecipeCmp.tierKey (_T<n>, rarity words, Omni last, material ladder), sortKey (tier + ItemLevel); the Artifacts
              rows of Skyy's screenshot sort Bag, T1 .. T4 by SkyyAccessories' ItemLevel, Omni; craftable first kept; Crafting tools by
              the material ladder; a stand-in I18nModule: translated item names (key with / without server.), CraftPage.pretty uses
              them, resource types by their group name (Any Tree Log), echoed keys / unknown ids fall back, same-tier rows by shown name
  AA engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.8.8"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-0.8.7.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sacks088", "sacks")))
PKG = "com.skyy.sacks."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyySacks")
EXPECT = {
    "ProcBench": ["+m benchScore", "~m config", "~m outName"],
    "SackDefs": ["+f LOGT_IDS", "+f LOGT_TIER", "+f LOGT_KEY", "+m logTier", "+m members", "+m unitName", "+m unitKey", "~<clinit>",
                 "+f DNAMES", "+m tr", "+m dname", "+m rtName"],
    "RecipeCmp": ["+m tierKey", "+m level", "+m sortKey", "+m sortName"],
    "CraftPage": ["~m build", "~m buildProc", "~m pretty"],   # the two row builders (sort + ingredient names), the real names
    "VoidStore": ["+m haveOf", "+m takeOrder", "~m upgrade"],
    "SacksPage": ["~m upgradeBox"],
    "SkyySacksPlugin": ["~m setup"],    # the ready line's version
    "CfgFn": ["~m opExport"],
    "CfgRows": ["~m header", "~<clinit>"],   # the version + the cost rows' help line
}
ADDED = []
T080 = os.path.join(HERE, "test_skyysacks_0.8.0.py")
T0714 = os.path.join(HERE, "test_skyysacks_0.7.14.py")
LOG_T1 = ["Wood_Oak_Trunk", "Wood_Birch_Trunk", "Wood_Beech_Trunk", "Wood_Ash_Trunk", "Wood_Aspen_Trunk"]


def _t087():
    sp = importlib.util.spec_from_file_location("t087", os.path.join(HERE, "test_skyysacks_0.8.7.py"))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    m.VERSION = VERSION   # its static checks (and the modules it loads) read the 0.8.8 generated script
    return m


def run_exec(out, jar, scratch, home):
    _t087().run_exec(out, jar, scratch, home)


def run_late(out, jar, scratch, home):
    _t087().run_late(out, jar, scratch, home)


def run_art(out, jar, scratch, home):
    _t087().run_art(out, jar, scratch, home)


def _t086_old(fallback):
    """the 0.8.6 module (as the 0.8.7 harness loads it) whose 0.8.5 snd / live phases use `fallback` when their SkyySacks-0.8.4.jar is
    gone (the old jars were archived 2026-10-15: backups/archive/old-jars-20261015.tar.xz holds only 0.8.1 / 0.8.3)"""
    m86 = _t087()._t086()
    orig = m86._t085

    def patched():
        m = orig()
        if not os.path.isfile(m.OLD_JAR):
            print("note: %s is gone - the 0.8.5 phase uses %s as its old jar" % (os.path.basename(m.OLD_JAR), os.path.basename(fallback)))
            m.OLD_JAR = fallback
            eq0 = HK.Child.eq

            def eq(self, got, want, what):   # the one 0.8.4-only control (the 0.8.4 page played the craft click itself) cannot run
                if what.startswith("STATIC (control) 0.8.4"):
                    self.notes.append("SND: control '%s' skipped - SkyySacks-0.8.4.jar no longer exists" % what[:60])
                    return True
                return eq0(self, got, want, what)
            HK.Child.eq = eq
        return m
    m86._t085 = patched
    return m86


def run_snd(out, jar, scratch, home):
    _t086_old(os.path.join(HERE, "SkyySacks-0.8.6.jar")).run_snd(out, jar, scratch, home)


def run_live(out, jar, scratch, home):
    _t086_old(OLD_JAR).run_live(out, jar, scratch, home)   # live data: the 0.8.7 SET pin and 0.8.8 start on the same copy


# ======================================================================================================== FUEL (real asset stores)
FUEL_PRE = '''
    # 0.8.8 harness: what BlockTypeModule.setup / CraftingPlugin.setup register in the game (the Processing benches need both)
    _BP = "com.hypixel.hytale.server.core.asset.type.blocktype.config.bench."
    _BT = JClass("com.hypixel.hytale.protocol.BenchType")
    for _t, _c in (("Crafting", "CraftingBench"), ("Processing", "ProcessingBench"), ("DiagramCrafting", "DiagramCraftingBench"),
                   ("StructuralCrafting", "StructuralCraftingBench")):
        _C = JClass(_BP + _c)
        JClass(_BP + "Bench").CODEC.register(getattr(_BT, _t), _C.class_, _C.CODEC)
    for _n, _c in (("OpenBenchPage", "OpenBenchPageInteraction"), ("OpenProcessingBench", "OpenProcessingBenchInteraction"),
                   ("LearnRecipe", "LearnRecipeInteraction")):
        _C = JClass("com.hypixel.hytale.builtin.crafting.interaction." + _c)
        INTc.CODEC.register(_n, _C.class_, _C.CODEC)
'''
FUEL_TAIL = '''
    # the bare loader validates a block's Use interaction before the RootInteraction store has loaded: load the Item store once more
    _pack = AP(Paths.get(ASSETS_ZIP), "Hytale:Hytale", zfs(ASSETS_ZIP).getPath("/"), zfs(ASSETS_ZIP), True, None, None)
    for _st in store_order():
        if str(_st.getAssetClass().getSimpleName()) == "Item":
            _st.loadAssetsFromDirectory("Hytale:Hytale", _pack.getRoot().resolve("Server").resolve(_st.getPath()))
    _fail, _rec = loadpack(FAKE_PACK, "Test:FakeSeasons", False)
    _FUEL(locals())
'''


def run_fuel(out, jar, scratch, home):
    import serverjar
    K = HK.Child(out)
    os.makedirs(scratch, exist_ok=True)
    assets = serverjar.assets_zip()
    # the scratch pack: Bench_Furnace.json's bench, renamed, WITHOUT Fuel / ExtraOutput, 0.0 tier speed (the Lightning Rod shape)
    with zipfile.ZipFile(assets) as z:
        node = json.loads(z.read("Server/Item/Items/Bench/Bench_Furnace.json").decode("utf-8-sig"))
    node.pop("Recipe", None)
    bench = node["BlockType"]["Bench"]
    assert bench["Id"] == "Furnace" and bench.get("Fuel")
    bench.pop("Fuel")
    bench.pop("ExtraOutput", None)
    for tl in bench.get("TierLevels", []):
        tl["CraftingTimeReductionModifier"] = 0.0
    fake = os.path.join(scratch, "fakeseasons.zip")
    with zipfile.ZipFile(fake, "w") as z:
        z.writestr("manifest.json", json.dumps({"Group": "Test", "Name": "FakeSeasons", "Version": "1.0.0"}))
        z.writestr("Server/Item/Items/Bench/Test_Lightning_Rod.json", json.dumps(node, indent=1))
    src = open(T0714, encoding="utf8").read()
    a = src.index("def run_v():")
    b = src.index('    ITEM = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")', a)
    t0 = "    t0 = time.time()\n"
    body = src[a:b].replace("def run_v():", "def run_fuel_fixture():", 1)
    assert body.count(t0) == 1
    body = body.replace(t0, FUEL_PRE + t0, 1) + FUEL_TAIL
    # the 0.7.14 loader on THIS jar + the server jar (its child-2 class path) - jpype is started inside the slice
    body = body.replace("classpath=[B.SERVER_JAR, B.JAVASSIST]", "classpath=[B.SERVER_JAR, JAR, B.JAVASSIST]", 1)
    assert "classpath=[B.SERVER_JAR, JAR, B.JAVASSIST]" in body
    ns = {"__file__": T0714, "__name__": "t0714"}
    exec(compile(src[:src.index("def run():")], T0714, "exec"), ns)
    ns.update(SCRATCH=os.path.join(scratch, "v"), ASSETS_ZIP=assets, JAR=jar, FAKE_PACK=fake, _FUEL=lambda L: fuel_cases(K, L))
    os.makedirs(ns["SCRATCH"], exist_ok=True)
    exec(compile(body, T0714 + " (V loader slice)", "exec"), ns)
    ns["run_fuel_fixture"]()
    for f in ns["FAILS"]:
        K.check(False, "FUEL loader: " + f)
    K.save()


def fuel_cases(K, L):
    from jpype import JClass, JString
    records, CAPLOG = L["records"], L["CAPLOG"]
    K.check(not L["_fail"], "FUEL: the scratch pack (a no-fuel Processing bench 'Furnace') loads into the real stores: failed %s" % L["_fail"])
    BLT = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType")
    PBc = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.ProcessingBench")
    PB = JClass(PKG + "ProcBench")
    Pool = JClass(PKG + "SackPool")
    Pool.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySacks")
    cands, first = {}, None
    for o in BLT.getAssetMap().getAssetMap().values():
        bn = o.getBench()
        if bn is not None and isinstance(bn, PBc) and str(bn.getId()).lower() == "furnace":
            cands[str(o.getId())] = o
            if first is None:
                first = str(o.getId())   # what 0.8.7 took (the first match in the map's order)
    K.check("Bench_Furnace" in cands and "Test_Lightning_Rod" in cands,
            "FUEL: the store holds two blocks whose Processing bench id is Furnace: %s" % sorted(c for c in cands if not c.startswith("*")))
    rod, furn = cands.get("Test_Lightning_Rod"), cands.get("Bench_Furnace")
    K.check(rod is not None and rod.getBench().getFuel() is None and furn is not None and len(furn.getBench().getFuel()) == 1,
            "FUEL: Bench_Furnace has 1 Fuel slot, the pack's 'Furnace' none")
    K.notes.append("FUEL: 0.8.7's first-match lookup would have taken %s here (map order)" % first)
    K.check(int(PB.benchScore(JString("Furnace"), furn)) > int(PB.benchScore(JString("Furnace"), rod)) and
            all(int(PB.benchScore(JString("Furnace"), furn)) > int(PB.benchScore(JString("Furnace"), cands[c])) for c in cands if c != "Bench_Furnace"),
            "FUEL: benchScore ranks Bench_Furnace above the pack's block and every state variant: %s" %
            dict((c, int(PB.benchScore(JString("Furnace"), cands[c]))) for c in sorted(cands)))
    n0 = len(CAPLOG)
    c = PB.config(JString("Furnace"))
    K.check(c is not None and c.equals(furn.getBench()) and len(c.getFuel()) == 1 and c.getExtraOutput() is not None,
            "FUEL: ProcBench.config(Furnace) = Bench_Furnace's bench (Fuel slot + charcoal ExtraOutput)")
    K.check(bool(PB.benchNeedsFuel(JString("Furnace"))), "FUEL: benchNeedsFuel(Furnace) = true (the Load fuel row and Unload fuel button come back)")
    K.check(abs(float(PB.reduction(JString("Furnace"), 2)) - 0.3) < 1e-6 and float(PB.reduction(JString("Furnace"), 1)) == 0.0,
            "FUEL: Furnace tier speed from the vanilla block: tier 1 0, tier 2 30 percent (got %s)" % float(PB.reduction(JString("Furnace"), 2)))
    info = [m for lv, m in records(n0) if "processing: Furnace settings from Bench_Furnace" in m]
    K.check(len(info) == 1 and "Test_Lightning_Rod" in info[0] and "*" not in info[0],
            "FUEL: one INFO line names the block used and the skipped one: %s" % info[:1])
    PB.config(JString("Furnace"))
    K.check(len([m for lv, m in records(n0) if "processing: Furnace settings" in m]) == 1, "FUEL: the line is written once (the hit is cached)")
    for bn, want in (("Campfire", True), ("Tannery", False), ("Salvagebench", False)):
        K.eq(bool(PB.benchNeedsFuel(JString(bn))), want, "FUEL: benchNeedsFuel(%s) (vanilla)" % bn)
    K.check(PB.config(JString("Tannery")) is not None, "FUEL: the Tannery config is found (it just has no Fuel list)")
    # ---- a queue that was smelting fuel-free under 0.8.7 (needsFuel is not saved; 0.8.7 had it false)
    CRR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    rid = None
    for e in CRR.getAssetMap().getAssetMap().entrySet():
        po = e.getValue().getPrimaryOutput()
        if po is not None and str(po.getItemId()) == "Ingredient_Bar_Copper":
            rid = str(e.getKey())
            break
    if rid is None:   # the bare loader has no CraftingPlugin to turn item Recipe blocks into CraftingRecipe assets
        K.notes.append("FUEL: no copper bar CraftingRecipe in the bare stores - the paused queue uses a stand-in recipe id (its inputs come out)")
        rid = "Test_Missing_Recipe"
    pb = PB(JString("Furnace"))
    K.check(bool(pb.needsFuel), "FUEL: a new Furnace ProcBench needs fuel")
    pb.needsFuel = False
    t = 1000000
    pb.addJob(JString(rid), 3, 5000, JString("Ore_Copper*1"), t)
    pb.progress = 2000   # 2 s into the first bar when the update lands
    done = int(pb.advance(t + 60000))
    d = [str(x) for x in pb.describe(1, True)]
    K.check(bool(pb.needsFuel) and done == 0 and int(pb.queued()) == 3 and int(pb.progress) == 2000 and int(pb.outTotal()) == 0,
            "FUEL: the old fuel-free queue PAUSES (needsFuel re-read true, 0 done, 3 queued, progress kept, nothing out): done %d queued %d progress %d"
            % (done, int(pb.queued()), int(pb.progress)))
    K.check("OUT OF FUEL - load fuel to continue" in d[1] and "fuel 0s (0 items loaded)" in d[0] and "needs no fuel" not in d[0],
            "FUEL: the page says OUT OF FUEL and shows the fuel line: %r / %r" % (d[0], d[1]))
    K.check(bool(pb.fuelWarnOnce()) and not bool(pb.fuelWarnOnce()), "FUEL: the out-of-fuel warning fires once")
    fl = [str(x) for x in PB.fuels()]
    fid = "Wood_Oak_Trunk" if "Wood_Oak_Trunk" in fl else (fl[0] if fl else None)
    K.check(fid is not None and float(PB.fuelQuality(JString(fid))) > 0, "FUEL: a real fuel item from the Item store (%s, %d fuels)" % (fid, len(fl)))
    pb.addFuel(JString(fid), 20)
    done = int(pb.advance(t + 120000))
    K.check(done == 3 and int(pb.queued()) == 0 and int(pb.outTotal()) >= 3,
            "FUEL: fuel loaded -> the paused queue finishes (3 bars), nothing lost: done %d out %d" % (done, int(pb.outTotal())))


# ======================================================================================================== LOGS (Void stand-ins)
def run_logs(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    src = open(T080, encoding="utf8").read()
    a = src.index("    # ---------------- stand-ins (the 0.7.12+ harness pattern)\n")
    b = src.index("    # ---------------- D. categories\n", a)
    head = ("def run_logs_fixture():\n    import jpype\n    import skyybuild as B\n"
            "    from jpype import JClass, JArray, JShort, JString, JInt, JLong, JImplements, JOverride\n"
            "    jp = JClass(\"javassist.ClassPool\")(True)\n    jp.appendClassPath(B.SERVER_JAR)\n    jp.appendClassPath(JAR)\n")
    body = head + src[a:b] + "    _LOGS(locals())\n"
    ns = {"__file__": T080, "__name__": "t080"}
    exec(compile(src[:src.index("def run():")], T080, "exec"), ns)
    ns.update(JAR=jar, SCRATCH=os.path.join(scratch, "logs"), _LOGS=lambda L: logs_cases(K, L))
    exec(compile(body, T080 + " (stand-in slice)", "exec"), ns)
    try:
        ns["run_logs_fixture"]()
    finally:
        for f in ns["FAILS"]:
            K.check(False, "LOGS fixture: " + f)
        K.save()
        try:
            JClass_ = __import__("jpype").JClass
            JClass_(PKG + "SackPool").WRITER.shutdownNow()   # the fixture's writer thread - else the JVM never exits
        except Exception:
            pass


def logs_cases(K, L):
    from jpype import JClass, JString, JShort
    VS, Defs, Cfg, Pool, SPage = L["VS"], L["Defs"], L["Cfg"], L["Pool"], L["SPage"]
    fresh, write_pool, player, coll, pc, inv_counts, total, custom_item, drain = (L[n] for n in (
        "fresh", "write_pool", "player", "coll", "pc", "inv_counts", "total", "custom_item", "drain"))
    TBoom, UUID, us, jfield, pref = L["TBoom"], L["UUID"], L["us"], L["jfield"], L["pref"]
    base = os.path.join(SCRATCH, "logs")
    MAPLE, AZURE, APPLE, FIB, SAP = "Wood_Maple_Trunk", "Wood_Azure_Trunk", "Wood_Apple_Trunk", "Ingredient_Fibre", "Ingredient_Tree_Sap"
    for i_ in LOG_T1 + [MAPLE, AZURE, APPLE, "Wood_Sallow_Trunk", "Wood_Fig_Blue_Trunk"]:
        custom_item(i_, 100)
    # ---- the tier table
    mem = lambda i: [str(x) for x in Defs.members(JString(i))]
    K.eq(mem("Wood_Oak_Trunk"), LOG_T1, "LOGS: Oak's group = the tier-1 logs (Gathering-Progression-Spec 2.2), key log first")
    K.eq(mem(MAPLE), [MAPLE, AZURE], "LOGS: Maple's group = Maple + Azure")
    K.eq(mem(APPLE), [APPLE], "LOGS: an Orchard log (no tier) counts only as itself")
    K.eq(mem("Ore_Iron"), ["Ore_Iron"], "LOGS: a non-log counts only as itself (Mining etc. unchanged)")
    K.eq([int(Defs.logTier(JString(i))) for i in ("Wood_Oak_Trunk", "Wood_Gumboab_Trunk", "Wood_Redwood_Trunk", "Wood_Fig_Blue_Trunk", APPLE)],
         [1, 3, 4, 5, 0], "LOGS: logTier")
    K.eq([str(Defs.unitName(JString(i))) for i in ("Wood_Ash_Trunk", AZURE, "Wood_Palo_Trunk", "Wood_Spiral_Trunk", "Wood_Fig_Blue_Trunk")],
         ["Oak-tier logs", "Maple-tier logs", "Gumboab-tier logs", "Redwood-tier logs", "Sallow-tier logs"],
         "LOGS: the line label names the group's first wood (no tier number)")
    K.check(Defs.unitName(JString("Ore_Iron")) is None and Defs.unitName(JString(APPLE)) is None, "LOGS: no label for a non-tier id")
    K.eq(len(Defs.LOGT_IDS), 26, "LOGS: 26 tier logs")
    # ---- the Foraging Unique upgrade (cost Wood_Oak_Trunk:500, Ingredient_Fibre:500, Ingredient_Tree_Sap:100)
    K.eq(str(Cfg.PD_COST_FORAGING_UNIQUE), "Wood_Oak_Trunk:500,Ingredient_Fibre:500,Ingredient_Tree_Sap:100", "LOGS: the default Foraging Unique cost")
    drain()
    fresh(base)
    U = UUID.fromString("00000000-0000-0000-0000-0000000a0881")
    k = str(U)
    write_pool(os.path.join(base, "pools"), k, {"Wood_Oak_Trunk": 100, "Wood_Birch_Trunk": 150, FIB: 500, MAPLE: 300, APPLE: 300})
    s = VS.st(k)
    s.first = 1
    coll(U, {"Foraging": 20 * 9 * 9})   # Lv 10 = the Unique gate
    p = player(storage=[("Wood_Ash_Trunk", 100), ("Wood_Ash_Trunk", 50), (SAP, 100), (MAPLE, 100)])
    b0 = total(inv_counts(p), pc(k))
    K.eq(int(VS.haveOf(k, p.getInventory(), JString("Wood_Oak_Trunk"))), 400, "LOGS: haveOf(Oak line) = 100 Oak + 150 Birch (Void) + 150 Ash (inventory); Maple / Apple not")
    r_ = str(VS.upgrade(p, U, k, 1, 0))
    K.check(r_ == "-Not enough Oak-tier logs (400 / 500)" and total(inv_counts(p), pc(k)) == b0 and int(s.rar[1]) == 0,
            "LOGS: 400 of 500 tier-1 logs -> refused with the tier total, nothing moved: %s" % r_)
    p.getInventory().getStorage().addItemStack(L["IS"]("Wood_Aspen_Trunk", 60))
    p.getInventory().getHotbar().addItemStack(L["IS"]("Wood_Ash_Trunk", 50))
    b1 = total(inv_counts(p), pc(k))
    # held now: Ash 200 (inventory), Birch 150 (Void), Oak 100 (Void), Aspen 60 (inventory) = 510
    K.eq([str(x) for x in VS.takeOrder(k, p.getInventory(), JString("Wood_Oak_Trunk"))],
         ["Wood_Ash_Trunk", "Wood_Birch_Trunk", "Wood_Oak_Trunk", "Wood_Aspen_Trunk", "Wood_Beech_Trunk"],
         "LOGS: take order = most held first (Ash 200, Birch 150, Oak 100, Aspen 60, Beech 0)")
    r_ = str(VS.upgrade(p, U, k, 1, 0))
    drain()
    paid = {"Wood_Ash_Trunk": 200, "Wood_Birch_Trunk": 150, "Wood_Oak_Trunk": 100, "Wood_Aspen_Trunk": 50, FIB: 500, SAP: 100}
    after = total(inv_counts(p), pc(k))
    K.check(r_.startswith("+Foraging is now Unique") and int(s.rar[1]) == 1 and total(after, paid) == b1,
            "LOGS: mixed tier-1 logs (Void + inventory) pay the 500 Oak line; exactly the cost left, conserved: %s" % r_)
    K.check(after.get("Wood_Aspen_Trunk") == 10 and after.get(MAPLE) == 400 and after.get(APPLE) == 300 and "Wood_Ash_Trunk" not in after
            and "Wood_Birch_Trunk" not in after and "Wood_Oak_Trunk" not in after,
            "LOGS: taken most-held first - Ash, Birch, Oak all used, Aspen only the last 50 (10 kept); Maple + Apple untouched: %s" % after)
    # two lines of one tier add up
    drain()
    fresh(base)
    write_pool(os.path.join(base, "pools"), k, {"Wood_Oak_Trunk": 300, "Wood_Birch_Trunk": 200})
    s = VS.st(k)
    s.first = 1
    p = player(storage=[])
    old = str(Cfg.PD_COST_FORAGING_UNIQUE)
    Cfg.PD_COST_FORAGING_UNIQUE = "Wood_Oak_Trunk:300,Wood_Birch_Trunk:300"
    r_ = str(VS.upgrade(p, U, k, 1, 0))
    K.check(r_ == "-Not enough Oak-tier logs (500 / 600)" and pc(k) == {"Wood_Oak_Trunk": 300, "Wood_Birch_Trunk": 200} and int(s.rar[1]) == 0,
            "LOGS: two lines of one tier need their SUM (500 held < 600) -> refused, nothing moved: %s" % r_)
    Cfg.PD_COST_FORAGING_UNIQUE = "Wood_Oak_Trunk:250,Wood_Birch_Trunk:250"
    r_ = str(VS.upgrade(p, U, k, 1, 0))
    K.check(r_.startswith("+Foraging is now Unique") and pc(k) == {}, "LOGS: two tier-1 lines summing to 500 take all 500 once: %s / %s" % (r_, pc(k)))
    Cfg.PD_COST_FORAGING_UNIQUE = old
    # a crash part-way through the inventory take -> everything back
    drain()
    fresh(base)
    write_pool(os.path.join(base, "pools"), k, {FIB: 500, SAP: 100, "Wood_Oak_Trunk": 20})
    s = VS.st(k)
    s.first = 1
    p = player(storage=[("Wood_Ash_Trunk", 100), ("Wood_Beech_Trunk", 100), ("Wood_Birch_Trunk", 100), ("Wood_Ash_Trunk", 100),
                        ("Wood_Aspen_Trunk", 100)], boom=True)
    b2 = total(inv_counts(p), pc(k))
    TBoom.CALLS = 0
    TBoom.BOOMAT = 3
    r_ = str(VS.upgrade(p, U, k, 1, 0))
    K.check(r_.startswith("-Internal error") and total(inv_counts(p), pc(k)) == b2 and int(s.rar[1]) == 0 and pc(k).get("Wood_Oak_Trunk") == 20,
            "LOGS: a crash after 3 slot removals of the log take -> rolled back: every slot and the Void (20 Oak) as before, no rarity: %s" % r_)
    TBoom.BOOMAT = -1
    r_ = str(VS.upgrade(p, U, k, 1, 0))
    drain()
    after = total(inv_counts(p), pc(k))
    K.check(r_.startswith("+Foraging is now Unique") and total(after, {"Wood_Ash_Trunk": 200, "Wood_Birch_Trunk": 100, "Wood_Beech_Trunk": 100,
                                                                         "Wood_Aspen_Trunk": 100, FIB: 500, SAP: 100}) == b2
            and pc(k).get("Wood_Oak_Trunk") == 20,
            "LOGS: the same upgrade after the crash pays exactly once (Ash 200, then Birch / Beech / Aspen 100 each in table order; the "
            "20 Oak, the least held, kept): %s / %s" % (r_, after))
    # ---- the page's upgrade box
    UCBc = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEBc = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")

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
    drain()
    fresh(base)
    write_pool(os.path.join(base, "pools"), k, {"Wood_Oak_Trunk": 38, "Wood_Birch_Trunk": 50, FIB: 20})
    s = VS.st(k)
    s.first = 1
    p = player(storage=[("Wood_Ash_Trunk", 50), (MAPLE, 100)])
    pg = us.allocateInstance(SPage.class_)
    jfield(SPage.class_, "playerRef").set(pg, pref(U))
    jfield(SPage.class_, "info").set(pg, JString(""))
    jfield(SPage.class_, "amount").set(pg, JString(""))
    pg.cat = "Foraging"
    b_, e_ = UCBc(), UEBc()
    pg.render(b_, e_, p, k, U)
    t0 = ucb_text(b_)
    K.check("Oak-tier logs" in t0 and "138 / 500" in t0 and "20 / 500" in t0 and "SkyyVCostG0" in t0 and "SkyyVCostN0" in t0
            and "SkyyVCostT1" in t0 and "SkyyVCostG1" not in t0 and "Tier 1" not in t0,
            "LOGS: the upgrade box shows 'Oak-tier logs' over 138 / 500 (38 Oak + 50 Birch + 50 Ash; Maple not), the Fibre cell as before (20 / 500)")
    # Mining unchanged: the plain cells, no tier label
    pg.cat = "Mining"
    b_, e_ = UCBc(), UEBc()
    pg.render(b_, e_, p, k, U)
    t1 = ucb_text(b_)
    K.check("-tier logs" not in t1 and "SkyyVCostG" not in t1 and "SkyyVCostT0" in t1, "LOGS: the Mining upgrade box keeps its plain cells")
    # ---- review fix: the page sums same-group lines exactly like VoidStore.upgrade (a hand-edited cost with two tier-1 lines)
    def upbtn(t_):
        i_ = t_.index("#SkyyVUpBtn ")
        return t_[max(0, t_.rfind("\n", 0, i_)):t_.find("\n", i_)]
    drain()
    fresh(base)
    write_pool(os.path.join(base, "pools"), k, {"Wood_Oak_Trunk": 300, "Wood_Birch_Trunk": 200, FIB: 600})
    s = VS.st(k)
    s.first = 1
    p = player(storage=[(SAP, 100)])
    pg.cat = "Foraging"
    old = str(Cfg.PD_COST_FORAGING_UNIQUE)
    coll(U, {"Foraging": 20 * 8 * 8})     # Lv 9 < the gate 10: the disabled Upgrade button for reference
    b_, e_ = UCBc(), UEBc()
    pg.render(b_, e_, p, k, U)
    off = upbtn(ucb_text(b_))
    coll(U, {"Foraging": 20 * 9 * 9})
    Cfg.PD_COST_FORAGING_UNIQUE = "Wood_Oak_Trunk:250,Wood_Birch_Trunk:250,Ingredient_Fibre:500"
    b_, e_ = UCBc(), UEBc()
    pg.render(b_, e_, p, k, U)
    t2 = ucb_text(b_)
    on = upbtn(t2)
    K.check("500 / 250" in t2 and "500 / 500" in t2 and on != off, "LOGS: 250 + 250 tier-1 lines with 500 held: the cells show 500 / 250 then the "
            "running sum 500 / 500, Upgrade enabled")
    Cfg.PD_COST_FORAGING_UNIQUE = "Wood_Oak_Trunk:300,Wood_Birch_Trunk:300,Ingredient_Fibre:500"
    b_, e_ = UCBc(), UEBc()
    pg.render(b_, e_, p, k, U)
    t3 = ucb_text(b_)
    r_ = str(VS.upgrade(p, U, k, 1, 0))
    K.check("500 / 300" in t3 and "500 / 600" in t3 and upbtn(t3) == off and r_ == "-Not enough Oak-tier logs (500 / 600)",
            "LOGS (review fix): 300 + 300 tier-1 lines with 500 held: the second cell shows the sum 500 / 600, Upgrade DISABLED - the page "
            "agrees with the upgrade check (%s)" % r_)
    Cfg.PD_COST_FORAGING_UNIQUE = old

    # ---- /craft order (Skyy "make sure this is sorted by tier too") + real names
    from jpype import JArray, JInt
    RC = JClass(PKG + "RecipeCmp")
    ItemC, KMap, jp = L["ItemC"], L["KMap"], L["jp"]
    lv = {"Skyy_Accessory_Bag": 18, "Skyy_Accessory_Workbench_T1": 1, "Skyy_Talisman_Speed_Common": 4, "Skyy_Accessory_Armor_Bench_T1": 13,
          "Skyy_Accessory_Arcanebench_T1": 17, "Skyy_Talisman_Speed_Uncommon": 21, "Skyy_Accessory_Armor_Bench_T2": 30,
          "Skyy_Accessory_Armor_Bench_T3": 38, "Skyy_Accessory_Farmingbench_T4": 46, "Skyy_Talisman_Speed_Epic": 47, "Skyy_Accessory_Omni": 51}
    for i_, l_ in lv.items():
        it_ = custom_item(i_, 1)
        jfield(ItemC.class_, "itemLevel").setInt(it_, l_)
    K.eq([int(RC.tierKey(JString(i))) for i in ("Skyy_Accessory_Bag", "Skyy_Accessory_Workbench_T1", "Skyy_Talisman_Speed_Common",
                                                "Skyy_Talisman_Speed_Uncommon", "Skyy_Accessory_Farmingbench_T7", "Skyy_Talisman_Speed_Epic",
                                                "Skyy_Accessory_Omni", "Tool_Pickaxe_Iron", "Weapon_Sword_Copper", "Bench_Arcane")],
         [0, 1, 1, 2, 7, 4, 99, 3, 1, 0], "ORDER: tierKey - _T<n>, rarity words, the Omni last, else the material ladder")
    K.eq(int(RC.sortKey(JString("Skyy_Accessory_Armor_Bench_T2"))), 2 * 1000000 + 30, "ORDER: sortKey = tier x 1,000,000 + ItemLevel")
    alpha = sorted(lv)   # what 0.8.7 showed (tierOf 0 for all, then the id)
    ObjA = JArray(JClass("java.lang.Object"))

    def ent(i_, can=0):
        a_ = ObjA(4)
        a_[0], a_[1], a_[2], a_[3] = JString(i_), JClass("java.lang.Integer").valueOf(JInt(can)), JClass("java.lang.Integer").valueOf(JInt(int(RC.sortKey(JString(i_))))), RC.sortName(JString(i_))
        return a_

    def order(ids, can=()):
        lst = JClass("java.util.ArrayList")()
        for i_ in ids:
            lst.add(ent(i_, 1 if i_ in can else 0))
        JClass("java.util.Collections").sort(lst, RC())
        return [str(x[0]) for x in lst]
    want = ["Skyy_Accessory_Bag", "Skyy_Accessory_Workbench_T1", "Skyy_Talisman_Speed_Common", "Skyy_Accessory_Armor_Bench_T1",
            "Skyy_Accessory_Arcanebench_T1", "Skyy_Talisman_Speed_Uncommon", "Skyy_Accessory_Armor_Bench_T2", "Skyy_Accessory_Armor_Bench_T3",
            "Skyy_Accessory_Farmingbench_T4", "Skyy_Talisman_Speed_Epic", "Skyy_Accessory_Omni"]
    K.eq(order(alpha), want, "ORDER: the Artifacts rows (given alphabetically) sort no-tier first (the Accessory Bag), then T1 .. T4 - inside a tier "
         "by SkyyAccessories' ItemLevel (its Workbench tab order) - the Omni last")
    K.eq(order(alpha, can=("Skyy_Accessory_Armor_Bench_T3",))[0], "Skyy_Accessory_Armor_Bench_T3", "ORDER: craftable rows still come first")
    for i_ in ("Tool_Pickaxe_Iron", "Tool_Pickaxe_Copper", "Tool_Pickaxe_Crude", "Tool_Hatchet_Copper"):
        custom_item(i_, 1)
    K.eq(order(["Tool_Pickaxe_Iron", "Tool_Hatchet_Copper", "Tool_Pickaxe_Crude", "Tool_Pickaxe_Copper"]),
         ["Tool_Pickaxe_Crude", "Tool_Hatchet_Copper", "Tool_Pickaxe_Copper", "Tool_Pickaxe_Iron"],
         "ORDER: Crafting / Smithing keep the material ladder (Crude, Copper, Iron), names inside a tier")
    # real names through a stand-in I18nModule (getMessage from a table; the server's keys with and without "server.")
    I18N = "com.hypixel.hytale.server.core.modules.i18n.I18nModule"
    ti = jp.makeClass("com.hypixel.hytale.server.core.modules.i18n.SkyyTestI18n", jp.get(I18N))
    ti.addField(JClass("javassist.CtField").make("public static final java.util.HashMap M = new java.util.HashMap();", ti))
    ti.addMethod(JClass("javassist.CtNewMethod").make("public String getMessage(String l, String k) { return (String) M.get(k); }", ti))
    TI = JClass(ti.toClass(JClass(I18N).class_))
    for k_, v_ in (("server.items.Skyy_Accessory_Arcanebench_T1.name", "Arcane Bench Accessory"), ("items.Ingredient_Bar_Copper.name", "Copper Ingot"),
                   ("server.items.Skyy_Accessory_Bag.name", "Accessory Bag"), ("resourceType.Wood_Trunk.name", "Any Tree Log"),
                   ("server.items.Skyy_Talisman_Speed_Common.name", "server.items.Skyy_Talisman_Speed_Common.name")):
        TI.M.put(JString(k_), JString(v_))
    custom_item("Ingredient_Bar_Copper", 100)
    Defs.DNAMES.clear()
    K.check(Defs.dname(JString("Skyy_Accessory_Arcanebench_T1")) is None and str(Defs.rtName(JString("Wood_Trunk"))) == "Wood Trunk",
            "NAMES: no I18nModule -> no name (the prettified id stays), resource type 'Wood Trunk'")
    jfield(JClass(I18N).class_, "instance").set(None, us.allocateInstance(TI.class_))
    Defs.DNAMES.clear()
    CP = JClass(PKG + "CraftPage")
    K.eq([str(Defs.dname(JString("Skyy_Accessory_Arcanebench_T1"))), str(Defs.dname(JString("Ingredient_Bar_Copper"))),
          str(CP.pretty(JString("Skyy_Accessory_Arcanebench_T1"))), str(CP.pretty(JString("Ingredient_Bar_Copper"))),
          str(Defs.rtName(JString("Wood_Trunk"))), str(Defs.rtName(JString("Fuel")))],
         ["Arcane Bench Accessory", "Copper Ingot", "Arcane Bench Accessory", "Copper Ingot", "Any Tree Log", "Fuel"],
         "NAMES: the translated item names (key with / without server.), CraftPage.pretty uses them, resource type -> its group name")
    K.check(Defs.dname(JString("Skyy_Talisman_Speed_Common")) is None and str(CP.pretty(JString("Skyy_Talisman_Speed_Common"))) == "Skyy Talisman Speed Common"
            and Defs.dname(JString("Not_An_Item")) is None,
            "NAMES: a key the module echoes back / an unknown item -> the old prettified id")
    for i_, n_ in (("Zz_Test_Thing", "Alpha Thing"), ("Aa_Test_Thing", "Zulu Thing")):
        custom_item(i_, 1)
        TI.M.put(JString("server.items.%s.name" % i_), JString(n_))
    K.eq(order(["Aa_Test_Thing", "Zz_Test_Thing"]), ["Zz_Test_Thing", "Aa_Test_Thing"],
         "NAMES: rows of one tier and level sort by the SHOWN name (Alpha Thing before Zulu Thing), not the id")
    jfield(JClass(I18N).class_, "instance").set(None, None)
    Defs.DNAMES.clear()
    gen = open(os.path.join(HERE, "build_skyysacks_%s.py" % VERSION), encoding="utf8").read()
    K.check(gen.count("{PKG}.RecipeCmp.sortKey(id0)), {PKG}.RecipeCmp.sortName(id0)") == 2 and "RecipeCmp.tierOf(id0)" not in gen
            and gen.count("{PKG}.SackDefs.rtName(in[k].getResourceTypeId())") == 2 and "String dn = {PKG}.SackDefs.dname(q.getItemId());" in gen,
            "STATIC: both /craft row builders sort by sortKey / sortName and show resource types by name; the queue text uses the real name")
    Pool.WRITER.shutdownNow()


if __name__ == "__main__":
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("exec", run_exec), ("late", run_late), ("art", run_art), ("fuel", run_fuel), ("logs", run_logs), ("snd", run_snd), ("live", run_live)],
           __file__, live=(LIVE_DIR, "Skyy_SkyySacks"))
