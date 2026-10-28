"""Harness for SkyySacks 0.8.32 (round sacks32 - tools/sacks_0_8_32_patch.py: Greater Essence opens, sacks:fn:takeOpen, the ticker thread).
Build first:
    python tools/sacks_0_8_32_patch.py && python SkyySacks/build_skyysacks_0.8.32.py

    python SkyySacks/test_skyysacks_0.8.32.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A / C   verify (-Xverify:all) + compare 0.8.31 -> 0.8.32 (only the classes the patch touches)
  0.8.30 + 0.8.31 phases re-run on the 0.8.32 jar: cmp30, sweephook, rbw + rbr (the reader is the 0.8.31 jar now = the rollback), cmp31,
        live + live2 + live31 (start twice on a live copy). (0.8.31's tick phase is replaced by tick32: SackTick moved to the ticker.)
  CMP32 on the 0.8.9 Void stand-ins: (1) the vanilla pair in the id maps; a craft needing Essence of Life opens Greater Essence (the
        fewest, change loose, value conserved, crafts.log); a refused craft packs back; Unpack Greater Essence -> 100 Essence each; the bag
        upgrade helpers (openFor / unopen / encHave); the per-recipe marker. (2) sacks:fn:takeOpen through the published SackFn(19): loose
        first, the fewest opened, all or nothing (short = nothing moved), loose only (enough loose / bags.craftOpen off), the vanilla pair,
        bad arguments, no player on this thread (= off the world thread) = 0; put packs back (all at once, partial puts, a put off the world
        thread = loose), commit clears the pack-back ledger; whole fish (checked take). (3) the dispatchers: each run() executes and is
        timed (SackBeat.took / maxText), a slow run WARNs once a minute; a micro-measure of the per-player checks (200 players x 8 benches).
  TICK32 bytecode: SackTick / CraftTick / ProcTick scheduled on SackPool.TICKER (none on the shared scheduler), the saver on the writer,
        AccSettle's hop via TICKER, SackBeat.check still on the shared scheduler, setup publishes sacks:fn:takeOpen, shutdown stops TICKER
  LIVE32 on a scratch COPY of NewBetaTest's Skyy_SkyySacks: the p3 profile's Essence of Life / Greater Essence pool through takeOpen's pool
        step and back (value conserved, all or nothing at the live numbers)
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
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_31", os.path.join(HERE, "test_skyysacks_0.8.31.py"))
T31 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T31)
sys.argv = _argv
HK.run_compare = _RC
T30 = T31.T30
T089 = T31.T089

VERSION = "0.8.32"
OLD_VERSION = "0.8.31"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-%s.jar" % OLD_VERSION)
T30.OLD_JAR = OLD_JAR          # the rollback reader (run_rbr) = 0.8.31 now
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sacks32", "h")))
PKG = "com.skyy.sacks."
BETA = T30.BETA
EXPECT = {"SkyySacksPlugin": ["~m setup", "~m shutdown"],
          "VoidCompact": ["~m init", "~m markers", "~m repack"],
          "VoidStore": ["~m encHave", "~m openFor", "~m unopen"],
          "SacksPage": ["~m unpack"],
          "BagMirror": ["~m virtuals"],
          "SackBridge": ["+f OPN", "+f TAKEOPENS", "+m oweOpen", "+m unoweOpen", "+m openDone", "+m onThread", "+m packBack",
                         "+m takeOpen0", "+m takeOpenL", "+m takeOpen", "~<clinit>", "~m commit", "~m put"],
          "SackFn": ["~m apply"],
          "SackPool": ["+f TICKER"],
          "SackThreads": ["+c ", "+f nm", "~c ", "~m newThread"],   # + the named constructor; the default one sets nm
          "SackBeat": ["+f MAXNS", "+f RUNS", "+f SLOWS", "+f SLOW_NS", "+f LASTSLOW", "+m bump", "+m maxAt", "+m took", "+m maxText",
                       "~<clinit>"],
          "SackTick": ["~m run"], "CraftTick": ["~m run"], "ProcTick": ["~m run"],
          "AccLink": ["~m benchPre"],
          # the config kit's export / header carry the version text
          "CfgRows": ["~m header"], "CfgFn": ["~m opExport"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
LE, LEC = "Ingredient_Life_Essence", "Ingredient_Life_Essence_Concentrated"
IRON, EIRON = "Ingredient_Bar_Iron", "Skyy_Ench_Iron"
FISH = "SkyyFishing_Fish_Test32"


def cases32(K, L, scratch):
    from jpype import JClass, JString, JArray, JInt, JFloat, JLong
    VS, Defs, Cfg, Pool, SPage, Swp, Mirror = L["VS"], L["Defs"], L["Cfg"], L["Pool"], L["SPage"], L["Swp"], L["Mirror"]
    fresh, write_pool, player, pc, inv_counts, custom_item, drain = (L[n] for n in (
        "fresh", "write_pool", "player", "pc", "inv_counts", "custom_item", "drain"))
    UUID, us, jfield, bridge = L["UUID"], L["us"], L["jfield"], L["bridge"]
    VC, CP, SB, Fn, Beat = (JClass(PKG + n) for n in ("VoidCompact", "CraftPage", "SackBridge", "SackFn", "SackBeat"))
    MQ = JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
    CRc = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    BR = JClass("com.hypixel.hytale.protocol.BenchRequirement")
    CRM = JClass("com.hypixel.hytale.builtin.crafting.component.CraftingManager")
    HS, HM, OA = JClass("java.util.HashSet"), JClass("java.util.HashMap"), JClass("java.lang.Object")
    for i_ in (LE, LEC, IRON, EIRON, FISH, "Skyy_Test_Out32"):
        custom_item(i_, 100)
    drain()
    base = os.path.join(scratch, "cmp32")
    U = UUID.fromString("00000000-0000-0000-0000-0000000c0832")
    k = str(U)

    def mk(pool):
        drain()
        fresh(base)
        bridge.put(JString("coll:recipes:" + k), JString(""))
        write_pool(os.path.join(base, "pools"), k, pool)
        VS.st(k).first = 1

    def val(d, b, e):
        return d.get(b, 0) + 100 * d.get(e, 0)

    def clog():
        JClass(PKG + "CraftLog").drain()
        p_ = os.path.join(base, "crafts.log")
        return open(p_, encoding="utf8").read() if os.path.isfile(p_) else ""

    def recipe(rid, ins):
        mi = JArray(MQ)([MQ(JString(i), None, None, JInt(q), None) for i, q in ins])
        po = MQ(JString("Skyy_Test_Out32"), None, None, JInt(1), None)
        r = CRc(mi, po, JArray(MQ)([po]), JInt(1), JArray(BR)(0), JFloat(0.0), False, JInt(0))
        f = CRc.class_.getDeclaredField("id")
        f.setAccessible(True)
        f.set(r, JString(rid))
        return r

    # ================= 1. the vanilla pair opens
    K.check(int(VC.idxBase(JString(LE))) == 110 and int(VC.idxEnch(JString(LEC))) == 110 and str(VC.baseAt(110)) == LE
            and str(VC.enchAt(110)) == LEC and int(VC.idxBase(JString(LEC))) == -1 and int(VC.idxEnch(JString(LE))) == -1
            and int(VC.idxBase(JString(IRON))) >= 0 and int(VC.idxBase(JString(EIRON))) == -1 and len(VC.BASE) == 110
            and int(VC.pairOf(JString(LE))) == 110,
            "VP32 the vanilla pair is in the id maps (Essence of Life = pair 110, Greater Essence its Enchanted item); the 110 rows unchanged")
    mk({LE: 30, LEC: 3})
    p = player(storage=[])
    r150 = recipe("Skyy_Test_LE150", [(LE, 150)])
    mats = CP.materialsFor(p, k, CP.wantedOne(r150))
    m = Mirror.of(k)
    K.check(int(mats.countRemovableMaterial(MQ(JString(LE), None, None, JInt(1), None))) == 330 and int(CP.limit(r150, mats)) == 2
            and str(m.vpair.get(JString(LE))) == LEC,
            "OPEN32 a craft needing Essence of Life counts 30 loose + 3 x 100 inside Greater Essence = 330 (twice the 150 recipe)")
    b0 = pc(k)
    m.broke.clear()
    mats.removeMaterials(CRM.getInputMaterials(r150, 1))
    m.sync()
    a = pc(k)
    brk = HM(m.broke)
    K.check(a.get(LE) == 80 and a.get(LEC) == 1 and int(m.broke.get(JString(LE)).longValue()) == 2 and val(b0, LE, LEC) - val(a, LE, LEC) == 150,
            "OPEN32 150 Essence of Life from 30 + 3 Greater: 2 Greater Essence opened, 1 left, 80 loose back in the bag (exactly 150 used): %s" % a)
    K.check("CRAFT-OPEN %s 2 -> %s 200" % (LEC, LE) in clog(), "OPEN32 crafts.log CRAFT-OPEN line names Greater Essence of Life")
    Pool.add(k, LE, JLong(150))   # the refused craft: the bag part credited back, then repack
    VC.repack(k, brk)
    K.check(pc(k) == b0 and "CRAFT-OPEN-UNDO %s 2 of 2" % LEC in clog(),
            "OPEN32 a refused / refunded craft packs the 2 Greater Essence back = exactly 30 + 3: %s" % pc(k))
    mk_ = HS()
    Mirror.addInputs(mk_, JArray(MQ)([MQ(JString(LEC), None, None, JInt(1), None), MQ(JString(LE), None, None, JInt(5), None)]))
    K.check(("!e:" + LE) in [str(x) for x in mk_] and ("!nv:" + LE) in [str(x) for x in mk_],
            "OPEN32 a recipe using Greater Essence AND Essence of Life gets the per-recipe markers (!e: + !nv:) - no virtual Essence there")
    # unpack
    mk({LEC: 2, LE: 5})
    p3 = player(storage=[])
    r_ = str(SPage.unpack(p3, k, LEC, 1))
    a, inv = pc(k), inv_counts(p3)
    K.check(r_.startswith("+Unpacked 100") and inv.get(LE) == 100 and a.get(LEC) == 1 and a.get(LE) == 5,
            "UNPACK32 1 Greater Essence of Life -> 100 Essence of Life in the storage: %s %s %s" % (r_, a, inv))
    K.check(str(SPage.unpack(p3, k, LE, 1)).startswith("-That item does not unpack"), "UNPACK32 Essence of Life itself does not unpack")
    # bag upgrade helpers
    mk({LE: 10, LEC: 3})
    op = HM()
    n_ = int(VS.openFor(k, LE, JLong(250), op))
    a = pc(k)
    K.check(n_ == 3 and a.get(LE) == 310 and a.get(LEC, 0) == 0, "UPG32 openFor 250 Essence of Life with 10 + 3 Greater: 3 opened (310): %s" % a)
    VS.unopen(k, op)
    K.check(pc(k) == {LE: 10, LEC: 3}, "UPG32 unopen packs them back: %s" % pc(k))
    if int(len(list(Defs.members(JString(LE))))) == 1:
        K.eq(int(VS.encHave(k, LE)), 300, "UPG32 encHave counts 100 x each Greater Essence for an Essence of Life cost line")
    else:
        K.notes.append("UPG32 encHave: Essence of Life is in a tier line (%s) - counted per member" % list(Defs.members(JString(LE))))

    # ================= 2. sacks:fn:takeOpen
    TP = L["TPlayers"]
    SB.PLAYERS = TP()
    fn = Fn(JInt(19))

    def to(id_, n):
        return int(fn.apply(JArray(OA)([U, JString(id_), JLong(n)])).longValue())

    def put(id_, n):
        return int(SB.put(U, JString(id_), JLong(n)))
    mk({IRON: 30, EIRON: 4})
    TP.P = player(storage=[])
    sk = Pool.settledKey(U)
    K.check(sk is not None and str(sk) == k, "TO the stand-in player's settled key is the test key (%s)" % sk)
    b0 = pc(k)
    t_ = to(IRON, 250)
    a = pc(k)
    K.check(t_ == 250 and a.get(IRON) == 80 and a.get(EIRON) == 1 and val(b0, IRON, EIRON) - val(a, IRON, EIRON) == 250,
            "TO takeOpen 250 Iron from 30 loose + 4 Enchanted: 250 taken, the FEWEST (3) opened, 1 left, change 80 loose: %s" % a)
    K.check("BAG-TAKEOPEN %s 250 (opened 3 %s" % (IRON, EIRON) in clog(), "TO crafts.log BAG-TAKEOPEN line")
    t2 = to(IRON, 181)
    K.check(t2 == 0 and pc(k) == a, "TO ALL OR NOTHING: 181 asked, 80 + 100 = 180 there -> 0 and nothing moved: %s" % pc(k))
    K.eq(put(IRON, 250), 250, "TO put 250 back (the refund path)")
    K.check(pc(k) == b0 and "BAG-TAKEOPEN-UNDO %s 3 of 3" % EIRON in clog(),
            "TO the refund packs the 3 opened back = exactly 30 + 4 Enchanted: %s" % pc(k))
    # partial puts
    to(IRON, 250)
    K.eq(put(IRON, 100), 100, "TO partial put 100")
    a1 = pc(k)
    K.eq(put(IRON, 150), 150, "TO partial put 150 (the rest)")
    K.check(a1.get(EIRON) == 2 and a1.get(IRON) == 80 and pc(k) == b0,
            "TO partial puts: 100 back packs 1 (floor 100 / 100), the last 150 packs the other 2 = exactly as before: %s -> %s" % (a1, pc(k)))
    # commit
    to(IRON, 250)
    K.eq(int(SB.commit(U, JString(IRON), JLong(250))), 250, "TO commit 250 (the caller paid)")
    K.check(put(IRON, 250) == 0 and (k + "|" + IRON) not in [str(x) for x in SB.OPN.keySet()] and pc(k).get(IRON) == 80,
            "TO after commit: put gives nothing back, the pack-back ledger is cleared, 80 stay")
    # loose only (enough loose: nothing opened)
    mk({IRON: 300, EIRON: 2})
    TP.P = player(storage=[])
    K.check(to(IRON, 250) == 250 and pc(k) == {IRON: 50, EIRON: 2}, "TO 300 loose: 250 taken loose, no Enchanted opened: %s" % pc(k))
    # bags.craftOpen off: loose only, all or nothing
    mk({IRON: 30, EIRON: 4})
    TP.P = player(storage=[])
    Cfg.CRAFT_OPEN = False
    t3 = to(IRON, 250)
    t4 = to(IRON, 20)
    Cfg.CRAFT_OPEN = True
    K.check(t3 == 0 and t4 == 20 and pc(k) == {IRON: 10, EIRON: 4},
            "TO Server Setup bags.craftOpen=false: 250 = 0 (Enchanted do not count, nothing moved), 20 loose taken: %s" % pc(k))
    # the vanilla pair
    mk({LE: 50, LEC: 2})
    TP.P = player(storage=[])
    K.check(to(LE, 120) == 120 and pc(k) == {LE: 30, LEC: 1}, "TO the vanilla pair: 120 Essence of Life from 50 + 2 Greater -> 1 opened, 30 loose, 1 Greater left: %s" % pc(k))
    put(LE, 120)
    K.check(pc(k) == {LE: 50, LEC: 2}, "TO the vanilla pair's refund packs the Greater Essence back: %s" % pc(k))
    # a put off the world thread: the items come back loose, nothing packed
    mk({IRON: 30, EIRON: 4})
    TP.P = player(storage=[])
    to(IRON, 250)
    TP.P = None
    K.check(put(IRON, 250) == 250 and pc(k) == {IRON: 330, EIRON: 1} and "0 of 3 packed back - the put came off the world thread" in clog(),
            "TO a put off the world thread: 250 back LOOSE (value kept: 330 + 1 Enchanted), nothing packed, logged: %s" % pc(k))
    # off the world thread / no player / bad arguments
    mk({IRON: 300})
    TP.P = None
    K.check(to(IRON, 10) == 0 and pc(k) == {IRON: 300}, "TO no player on this thread (= called off the world thread): 0, nothing moved")
    TP.P = player(storage=[])
    bad = [fn.apply(JString("x")), fn.apply(JArray(OA)([U, JString(IRON)])), fn.apply(JArray(OA)([JString(k), JString(IRON), JLong(5)])),
           fn.apply(JArray(OA)([U, JString(IRON), JString("5")])), fn.apply(None)]
    K.check(all(int(x.longValue()) == 0 for x in bad) and to(IRON, 0) == 0 and to(IRON, -5) == 0 and to("Skyy_Sack_Pocket", 1) == 0
            and pc(k) == {IRON: 300}, "TO bad arguments / 0 / negative / a bag id: 0, nothing moved, never throws")
    # whole fish
    mk({FISH: 5})
    TP.P = player(storage=[])
    K.check(to(FISH, 6) == 0 and pc(k) == {FISH: 5}, "TO fish: 6 asked, 5 there -> 0, nothing moved")
    K.check(to(FISH, 3) == 3 and pc(k) == {FISH: 2} and put(FISH, 3) == 3 and pc(k) == {FISH: 5},
            "TO fish: 3 taken through the fish ledger and put back: %s" % pc(k))
    SB.PLAYERS = None
    TP.P = None

    # ================= 3. the dispatchers: executed, timed; the slow warning; a micro-measure
    Beat.QUEUED = True   # the watchdog's beat is "out" already: run() does not touch the shared scheduler here
    Beat.SENT = JClass("java.lang.System").currentTimeMillis()
    r0 = [int(Beat.RUNS[i]) for i in range(3)]
    JClass(PKG + "SackTick")().run()
    JClass(PKG + "CraftTick")().run()
    JClass(PKG + "ProcTick")().run()
    r1 = [int(Beat.RUNS[i]) for i in range(3)]
    K.check(r1 == [r0[0] + 1, r0[1] + 1, r0[2] + 1], "TICK32 SackTick / CraftTick / ProcTick run() each time themselves (SackBeat.took): %s -> %s" % (r0, r1))
    s0 = int(Beat.SLOWS.get())
    Beat.LASTSLOW = 0
    Beat.took(1, JLong(2000000000))
    l1 = int(Beat.LASTSLOW)
    Beat.LASTSLOW = l1 - 1000   # 1 s later
    Beat.took(1, JLong(1500000000))
    l2 = int(Beat.LASTSLOW)
    K.check(int(Beat.SLOWS.get()) == s0 + 2 and l1 > 0 and l2 == l1 - 1000 and "craft link 2000 ms" in str(Beat.maxText()),
            "TICK32 a 2 s and a 1.5 s crafting-link run: both counted, ONE warning a minute, the max in the shutdown text: %s" % Beat.maxText())
    Beat.took(5, JLong(1))   # out of range: ignored
    # micro-measure: the per-player checks of the two moved dispatchers (200 players, 8 benches each, no queue = the full bench walk)
    PT, PS, PB, BL = (JClass(PKG + n) for n in ("ProcTask", "ProcStore", "ProcBench", "BenchLink"))
    us_ = us
    us32 = [UUID.fromString("00000000-0000-0000-0001-%012d" % i) for i in range(200)]
    for i, u_ in enumerate(us32):
        kk = "m32-%d" % i
        PT.LASTK.put(u_, JString(kk))
        PT.EPOCH.remove(u_)
        mp = HM()
        for j in range(8):
            pb = us_.allocateInstance(PB.class_)
            jfield(PB.class_, "queue").set(pb, JClass("java.util.ArrayList")())
            jfield(PB.class_, "xpDone").set(pb, JClass("java.util.LinkedHashMap")())
            mp.put(JString("b%d" % j), pb)
        PS.STATES.put(JString(kk), mp)
    Sys = JClass("java.lang.System")
    for _w in range(3):   # warm up (JIT)
        for u_ in us32:
            PT.needs(u_)
            BL.needsLink(u_)
    t0 = int(Sys.nanoTime())
    hits = 0
    for _r in range(5):
        for u_ in us32:
            if bool(PT.needs(u_)):
                hits += 1
            BL.needsLink(u_)
    dt = (int(Sys.nanoTime()) - t0) / 5.0
    K.check(hits == 0, "MEASURE ProcTask.needs walks every bench of an idle player and answers false (no queue, no XP): %d hits" % hits)
    K.notes.append("MEASURE one dispatcher pass of the per-player checks (ProcTask.needs over 8 benches + BenchLink.needsLink) for 200 "
                   "players = %.2f ms incl. the Python->Java call cost per call (an upper bound; the in-jar loop is cheaper)" % (dt / 1e6))
    K.check(dt < 1e9, "MEASURE a 200-player pass stays far below a second (%.2f ms)" % (dt / 1e6))
    for i, u_ in enumerate(us32):
        PT.LASTK.remove(u_)
        PS.STATES.remove(JString("m32-%d" % i))
    drain()


def run_cmp32(out, jar, scratch, home):
    T089.void_cases = cases32
    T089.run_void(out, jar, scratch, home)


def run_tick32(out, jar, scratch, _home):
    """bytecode: the dispatchers on SackPool.TICKER, the saver on the writer, AccSettle via TICKER, setup publishes takeOpen"""
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(True)
    cp.appendClassPath(JString(jar))
    Mn = JClass("javassist.bytecode.Mnemonic")

    def ops(m):
        seen = []
        ci = m.getMethodInfo().getCodeAttribute().iterator()
        cpool = m.getMethodInfo().getConstPool()
        while ci.hasNext():
            i = ci.next()
            op = str(Mn.OPCODE[ci.byteAt(i)])
            if op in ("getstatic", "putstatic"):
                idx = ci.u16bitAt(i + 1)
                seen.append(op + " " + str(cpool.getFieldrefClassName(idx)).split(".")[-1] + "." + str(cpool.getFieldrefName(idx)))
            elif op == "new":
                seen.append("new " + str(cpool.getClassInfo(ci.u16bitAt(i + 1))).split(".")[-1])
            elif op in ("ldc", "ldc_w"):
                idx = ci.byteAt(i + 1) if op == "ldc" else ci.u16bitAt(i + 1)
                try:
                    seen.append("ldc " + str(cpool.getLdcValue(idx)))
                except Exception:
                    seen.append("ldc ?")
            elif op in ("invokestatic", "invokevirtual", "invokeinterface", "invokespecial"):
                idx = ci.u16bitAt(i + 1)
                if op == "invokeinterface":
                    seen.append(str(cpool.getInterfaceMethodrefClassName(idx)).split(".")[-1] + "." + str(cpool.getInterfaceMethodrefName(idx)))
                else:
                    seen.append(str(cpool.getMethodrefClassName(idx)).split(".")[-1] + "." + str(cpool.getMethodrefName(idx)))
        return seen
    pl = cp.get(PKG + "SkyySacksPlugin")
    setup = ops(pl.getDeclaredMethod("setup"))
    sched = {}
    for j in range(len(setup) - 1):
        for t in ("SackTick", "CraftTick", "ProcTick", "SackSaver"):
            if setup[j + 1] == "new " + t and setup[j].startswith("getstatic "):
                sched[t] = setup[j].split(" ")[1]
    K.check(sched == {"SackTick": "SackPool.TICKER", "CraftTick": "SackPool.TICKER", "ProcTick": "SackPool.TICKER", "SackSaver": "SackPool.WRITER"},
            "TICK32 the three dispatchers on SackPool.TICKER, the 10 s saver on the writer: %s" % sched)
    allm = [(str(c), str(m.getName()), ops(m)) for c in ("SkyySacksPlugin", "SackTick", "CraftTick", "ProcTick", "SackPool", "AccLink")
            for m in cp.get(PKG + c).getDeclaredMethods() if m.getMethodInfo().getCodeAttribute() is not None]
    shared = [(c, n) for c, n, s in allm if any(s[j] == "getstatic HytaleServer.SCHEDULED_EXECUTOR" and j + 1 < len(s)
                                                  and s[j + 1] in ("new SackTick", "new CraftTick", "new ProcTick") for j in range(len(s)))]
    K.check(not shared, "TICK32 no dispatcher on HytaleServer.SCHEDULED_EXECUTOR any more: %s" % shared)
    K.check(setup.index("getstatic SackPool.WRITER") >= 0 and "putstatic SackPool.TICKER" in setup and "ldc SkyySacks-ticker" in setup,
            "TICK32 setup makes SackPool.TICKER with the SackThreads factory named SkyySacks-ticker")
    K.check("ldc sacks:fn:takeOpen" in setup, "TICK32 setup publishes sacks:fn:takeOpen")
    sd = ops(pl.getDeclaredMethod("shutdown"))
    K.check("getstatic SackPool.TICKER" in sd and "putstatic SackPool.TICKER" in sd and "SackBeat.maxText" in sd,
            "TICK32 shutdown stops TICKER and logs the tick max times")
    for t, w in (("SackTick", 0), ("CraftTick", 1), ("ProcTick", 2)):
        s = ops(cp.get(PKG + t).getDeclaredMethod("run"))
        K.check(s.count("SackBeat.took") == 1 and s.count("System.nanoTime") == 2 and s.index("System.nanoTime") < 3,
                "TICK32 %s.run times itself (System.nanoTime -> SackBeat.took)" % t)
    acc = [s for c, n, s in allm if c == "AccLink" and "new AccSettle" in s]
    K.check(acc and "getstatic SackPool.TICKER" in acc[0], "TICK32 the AccSettle 250 ms hop is scheduled on SackPool.TICKER")
    sb = ops(cp.get(PKG + "SackBeat").getDeclaredMethod("check"))
    K.check("getstatic HytaleServer.SCHEDULED_EXECUTOR" in sb and "new SackBeat" in sb,
            "TICK32 SackBeat.check still puts its beat on the shared scheduler (the 0.8.31 WARN kept)")
    s = ops(cp.get(PKG + "SweepTask").getDeclaredMethod("run"))
    a, b_, c = (s.index(x) if x in s else -1 for x in ("SweepTask.items", "VoidCompact.run", "SweepTask.sigOf"))
    K.check(0 <= a < b_ < c, "TICK32 SweepTask.run: items -> VoidCompact.run -> sigOf (unchanged)")
    K.check(str(JClass(PKG + "SackThreads")(JString("SkyySacks-ticker")).newThread(None).getName()) == "SkyySacks-ticker"
            and str(JClass(PKG + "SackThreads")().newThread(None).getName()) == "SkyySacks-writer"
            and bool(JClass(PKG + "SackThreads")().newThread(None).isDaemon()),
            "TICK32 SackThreads names: SkyySacks-writer (default) / SkyySacks-ticker, both daemon")
    K.save()


def run_live31b(out, jar, scratch, home):
    """0.8.31's live phase on a copy where the p3 profile's paused bags are switched back on (Skyy paused Farming / Foraging / Mining after
    the 0.8.31 test - comp.off.* lines; only in OUR scratch copy) so the compactor still runs against the live numbers"""
    p_ = os.path.join(home, "pd", "d8ddde89-98b2-4739-983e-a39773d582b6-p3.properties")
    if os.path.isfile(p_):
        raw = open(p_, "rb").read()
        nl = b"\r\n" if b"\r\n" in raw else b"\n"
        kept = [ln for ln in raw.split(nl) if not ln.startswith(b"comp.off.")]
        open(p_, "wb").write(nl.join(kept))
    T31.run_live31(out, jar, scratch, home)


def run_live32(out, jar, scratch, home):
    from jpype import JClass, JString, JLong
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    Paths = JClass("java.nio.file.Paths")
    VS, Pool, SB, Cfg = JClass(PKG + "VoidStore"), JClass(PKG + "SackPool"), JClass(PKG + "SackBridge"), JClass(PKG + "SackCfg")
    Pool.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySacks")
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
    Cfg.MTIME = -1
    Cfg.reload()
    VS.DIR = Paths.get(os.path.join(home, "pd"))
    Pool.DIR = Paths.get(os.path.join(home, "pools"))
    key = "d8ddde89-98b2-4739-983e-a39773d582b6-p3"
    if not os.path.isfile(os.path.join(home, "pools", key + ".properties")) and not os.path.isdir(os.path.join(home, "pools")):
        K.notes.append("LIVE32 no pools folder in the live copy - skipped")
        K.save()
        return

    def snap():
        return dict((str(e.getKey()), int(e.getValue().longValue())) for e in Pool.pool(key).entrySet())
    b0 = snap()
    le, lec = b0.get(LE, 0), b0.get(LEC, 0)
    have = le + 100 * lec
    K.notes.append("LIVE32 the live p3 pool: %d Essence of Life + %d Greater Essence of Life (= %d)" % (le, lec, have))
    r = SB.takeOpenL(key, JString(LE), JString(LEC), JLong(have + 1))
    K.check(int(r[0]) == 0 and snap() == b0, "LIVE32 one more than loose + 100 x Greater (%d): nothing taken, the live pool unchanged" % (have + 1))
    if have > 0:
        want = min(have, le + 150) if lec > 0 else le
        r = SB.takeOpenL(key, JString(LE), JString(LEC), JLong(want))
        a = snap()
        need = max(0, want - le)
        op = (need + 99) // 100
        K.check(int(r[0]) == want and int(r[1]) == op and a.get(LE, 0) == le + op * 100 - want and a.get(LEC, 0) == lec - op,
                "LIVE32 takeOpen %d Essence of Life at the live numbers: %d Greater opened (the fewest), change loose: %s -> %s"
                % (want, op, {LE: le, LEC: lec}, {LE: a.get(LE, 0), LEC: a.get(LEC, 0)}))
        Pool.add(key, JString(LE), JLong(want))
        VC = JClass(PKG + "VoidCompact")
        VC.pack(key, JString(LE), JString(LEC), JLong(op))
        K.check(snap() == b0, "LIVE32 put back + pack back: the live pool exactly as before")
    else:
        K.notes.append("LIVE32 the live copy holds no Essence of Life - only the refusal was checked")
    K.save()


if __name__ == "__main__":
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, [],
           [("cmp30", T30.run_cmp30), ("sweephook", T30.run_sweephook), ("rbw", T30.run_rbw), ("rbr", T30.run_rbr),
            ("cmp31", T31.run_cmp31), ("cmp32", run_cmp32), ("tick32", run_tick32),
            ("live", T30.T0827.run_live27), ("live2", T30.T0827.T0810.run_live10), ("live31", run_live31b), ("live32", run_live32)],
           __file__, live=(BETA, "Skyy_SkyySacks"))
