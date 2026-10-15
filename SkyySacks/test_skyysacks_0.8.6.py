"""Harness for SkyySacks 0.8.6 (FELLED LOG MISSED BY AUTO-PICKUP: one late felledBy retry, PickLate; tools/sacks_0_8_6_patch.py).
Build first: python tools/sacks_0_8_6_patch.py && python SkyySacks/build_skyysacks_0.8.6.py

    python SkyySacks/test_skyysacks_0.8.6.py [--keep] [--dir <scratch>]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.8.5 -> 0.8.6: + PickLate; PickBook (+ EXEC, + late), PickItemSys.onEntityAdded, the version texts only
  X  exec     REGRESSION: the 0.8.4 harness's run_exec, unchanged, on the 0.8.6 jar (every 0.8.3 / 0.8.4 no-dupe proof: SPLIT, BLOCK,
              MOB, CFG, SAVED, PET, HARV in a REAL engine Store; its felled-log case with no record now also passes through late())
  L  late     NEW: the same REAL Store fixture (the 0.8.4 run_exec source up to its BLOCK section, reused verbatim), PickBook.EXEC = a
              FIFO list standing in for World.execute, skill:fn:felledBy = a stand-in answering null until a fake BreakTask (queued
              FIRST, like SkyySkills' handler does) commits the tree:
                a break at (x, y, z) -> the hit block's drop at (x+.5, y, z+.5) delivered at once (claim) and queues nothing; the
                physics log at (x+.5, y+1, z+.5) stays, ONE PickLate queued behind the BreakTask; the queue run in order -> the log
                delivered exactly once (Void +2, no item left), felled counter +1; the queue run again -> nothing more
              negatives: felledBy still null after the BreakTask -> stays on the ground, counters unchanged; the item removed before
                the retry (ref invalid) -> no delivery, no exception; no felledBy key / not a block spot / pickup.blocks off / a
                contested claim at the spot -> nothing queued; World.execute throwing -> nothing queued, the item stays; static: the
                game path uses World.execute (EXEC is null in the game)
              CRAFT (same phase + fixture): a CraftRecipeEvent$Pre listener (SkyyGear GearCraftPreSys stand-in, cancels pickaxe outputs)
                on the real REGISTRY: CraftPage.preCraft refuses a pickaxe recipe / allows a plain one / allows all with the listener
                off / refuses when the check throws; the REAL CraftingManager.craftItem (pocket + bench path) refuses with no input taken
                (if the bare JVM can run it, else a note) + its bytecode order; static: PocketCraftWindow -> craftItem, /craft calls
                preCraft before its one removeMaterials and before any output
  SND + D     the 0.8.5 harness's sound + live phases on the 0.8.6 jar
  AA engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.8.6"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-0.8.5.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sacks086", "sacks")))
PKG = "com.skyy.sacks."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyySacks")
EXPECT = {
    "PickBook": ["+f EXEC", "+m late"],
    "PickItemSys": ["~m onEntityAdded"],
    "CraftPage": ["+m preCraft", "~m handleDataEvent"],
    "SkyySacksPlugin": ["~m setup"],    # the ready line's version
    "CfgFn": ["~m opExport"],
    "CfgRows": ["~m header"],
}
ADDED = ["PickLate"]
T084 = os.path.join(HERE, "test_skyysacks_0.8.4.py")
BLOCK_MARK = "    # ------------------------------------------------------------------ BLOCK\n"


def ns084():
    """the 0.8.4 harness as a namespace WITHOUT its module-level HK.run call (that file runs it on import)"""
    src = open(T084, encoding="utf8").read()
    tail = src.rindex("\nHK.run(")
    ns = {"__file__": T084, "__name__": "t084"}
    exec(compile(src[:tail], T084, "exec"), ns)
    return ns, src


def run_exec(out, jar, scratch, home):
    ns, _ = ns084()
    ns["run_exec"](out, jar, scratch, home)


def run_late(out, jar, scratch, home):
    ns, src = ns084()
    a = src.index("def run_exec(")
    b = src.index(BLOCK_MARK, a)
    body = src[a:b].replace("def run_exec(", "def run_late_fixture(", 1) + "    _LATE(locals())\n    _CRAFT(locals())\n    K.save()\n"
    mark = "    st = REG.addStore("
    assert body.count(mark) == 1
    body = body.replace(mark, "    _PRE(locals())\n" + mark, 1)   # the CraftRecipeEvent$Pre stand-in registers before the stores exist
    ns["_LATE"], ns["_PRE"], ns["_CRAFT"] = late_cases, pre_system, craft_cases
    exec(compile(body, T084 + " (fixture slice)", "exec"), ns)
    ns["run_late_fixture"](out, jar, scratch, home)


def late_cases(L):
    from jpype import JClass, JImplements, JOverride, JArray, JString
    K, Book, Cfg, st, bridge, Fn = L["K"], L["Book"], L["Cfg"], L["st"], L["bridge"], L["Fn"]
    player, drop, break_block, items, pc, cnt, inv_of = L["player"], L["drop"], L["break_block"], L["items"], L["pc"], L["cnt"], L["inv_of"]
    gone, alive, TOT, RR, Long_, System = L["gone"], L["alive"], L["TOT"], L["RR"], L["Long_"], L["System"]
    Late = JClass(PKG + "PickLate")
    Obj = JClass("java.lang.Object")
    QUEUE = []

    @JImplements("java.util.function.Consumer")
    class Exec(object):
        @JOverride
        def accept(self, t):
            QUEUE.append(t)

    def run_queue():
        """World.consumeTaskQueue: poll the FIFO head until empty"""
        ran = []
        while QUEUE:
            t = QUEUE.pop(0)
            if callable(t) and not hasattr(t, "run"):
                t()
                ran.append("BreakTask")
            else:
                t.run()
                ran.append("PickLate")
        return ran

    FELL = {}
    bridge.put("skill:fn:felledBy", Fn(lambda o: FELL.get("%s|%d|%d|%d" % (o[0], int(o[1]), int(o[2]), int(o[3])))))
    Book.EXEC = Exec()
    UL, RL = player(st, "Lia", (60.5, 64.0, 60.5))
    kL = str(UL)
    TOT[kL + "|Mining"] = 0

    def commit(x, y, z):
        """the fake SkyySkills BreakTask: Fell.commit puts the tree's claims -> felledBy answers 'falling' from now on"""
        def f():
            for dy in (1, 2, 3):
                FELL["skyytest|%d|%d|%d" % (x, y + dy, z)] = JArray(Obj)([UL, JString(kL), Long_(System.currentTimeMillis()), JString("falling")])
        return f

    def n10():
        return int(Book.N.get(10))

    # ---- POSITIVE: the hit block's drop (claim) at once; the physics log above after the BreakTask
    p0, f0 = pc(kL).get("Rock_Stone_Cobble", 0), n10()
    break_block(st, RL, (40, 90, 40))
    QUEUE.append(commit(40, 90, 40))            # SkyySkills' handler queued its BreakTask during the break
    hit = drop(st, "Rock_Stone_Cobble", 3, (40.5, 90.0, 40.5))
    K.check(gone(hit) and pc(kL).get("Rock_Stone_Cobble", 0) == p0 + 3 and len(QUEUE) == 1,
            "LATE: the hit block's drop is claimed and delivered inside the add; it queues NO retry (queue %d)" % len(QUEUE))
    log = drop(st, "Rock_Stone_Cobble", 2, (40.5, 91.0, 40.5))
    K.check(alive(log) and pc(kL).get("Rock_Stone_Cobble", 0) == p0 + 3 and len(QUEUE) == 2 and isinstance(QUEUE[1], Late),
            "LATE: the physics log at (x+.5, y+1, z+.5) - felledBy still null - stays for now, ONE PickLate queued BEHIND the BreakTask")
    late_t = QUEUE[1]
    ran = run_queue()
    K.eq(ran, ["BreakTask", "PickLate"], "LATE: the queue runs FIFO - BreakTask first, then the retry")
    K.check(gone(log) and items(st) == [] and pc(kL).get("Rock_Stone_Cobble", 0) == p0 + 5 and cnt(inv_of(RL)) == {},
            "LATE: the retry delivers the log exactly once (Void +2, no item entity left): %s / %s" % (pc(kL), items(st)))
    K.eq((n10() - f0, int(late_t.result)), (1, 1), "LATE: felled counter +1, PickLate.result 1 (all delivered)")
    late_t.run()
    K.check(run_queue() == [] and pc(kL).get("Rock_Stone_Cobble", 0) == p0 + 5 and n10() - f0 == 1 and int(late_t.result) == -2,
            "LATE: the same task run again (ref gone) -> nothing more, no second felled count")
    # ---- NEGATIVE: felledBy still null after the BreakTask -> the item stays exactly as before
    p1, f1 = pc(kL).get("Rock_Stone_Cobble", 0), n10()
    break_block(st, RL, (44, 90, 44))
    QUEUE.append(lambda: None)                  # a BreakTask that commits nothing (no tree / snapshot dropped)
    drop(st, "Rock_Stone_Cobble", 3, (44.5, 90.0, 44.5))
    lone = drop(st, "Rock_Stone_Cobble", 2, (44.5, 91.0, 44.5))
    t2 = QUEUE[-1]
    K.eq(run_queue(), ["BreakTask", "PickLate"], "LATE-: the retry ran after the BreakTask")
    K.check(alive(lone) and items(st) == [("Rock_Stone_Cobble", 2, 44.5, 91.0, 44.5)] and pc(kL).get("Rock_Stone_Cobble", 0) == p1 + 3
            and n10() == f1 and int(t2.result) == -4, "LATE-: felledBy still null -> the log stays on the ground, Void / counters unchanged")
    st.removeEntity(lone, RR.REMOVE)
    # ---- NEGATIVE: the item gone before the retry (ref invalid) -> no delivery, no exception
    p2, f2 = pc(kL).get("Rock_Stone_Cobble", 0), n10()
    QUEUE.append(commit(48, 90, 48))
    gonelog = drop(st, "Rock_Stone_Cobble", 2, (48.5, 91.0, 48.5))
    t3 = QUEUE[-1]
    st.removeEntity(gonelog, RR.REMOVE)
    err = None
    try:
        run_queue()
    except Exception as e:   # noqa
        err = e
    K.check(err is None and int(t3.result) == -2 and pc(kL).get("Rock_Stone_Cobble", 0) == p2 and n10() == f2,
            "LATE-: the item removed before the retry -> no delivery, no exception (%s)" % err)
    # ---- nothing queued: not a block spot / pickup.blocks off / no felledBy key / a contested claim at the spot
    r_ = drop(st, "Rock_Stone_Cobble", 1, (50.3, 91.0, 50.5))
    K.check(alive(r_) and QUEUE == [], "LATE0: not a block drop spot -> nothing queued")
    st.removeEntity(r_, RR.REMOVE)
    Cfg.PICK_BLOCKS = False
    r_ = drop(st, "Rock_Stone_Cobble", 1, (51.5, 91.0, 51.5))
    Cfg.PICK_BLOCKS = True
    K.check(alive(r_) and QUEUE == [], "LATE0: pickup.blocks off -> nothing queued")
    st.removeEntity(r_, RR.REMOVE)
    fb = bridge.remove("skill:fn:felledBy")
    r_ = drop(st, "Rock_Stone_Cobble", 1, (52.5, 91.0, 52.5))
    K.check(alive(r_) and QUEUE == [], "LATE0: no SkyySkills (no felledBy key) -> nothing queued (no extra cost)")
    st.removeEntity(r_, RR.REMOVE)
    bridge.put("skill:fn:felledBy", fb)
    UM, RM = player(st, "Moe", (70.5, 64.0, 70.5))
    now_ = System.nanoTime()
    Book.claim("skyytest", 54.5, 91.0, 54.5, UL, 3, now_)   # two players' share claims at one spot = contested (owner null);
    Book.claim("skyytest", 54.5, 91.0, 54.5, UM, 3, now_)   # (block claims never contest - the newest wins)
    r_ = drop(st, "Rock_Stone_Cobble", 1, (54.5, 91.0, 54.5))
    K.check(alive(r_) and QUEUE == [], "LATE0: a contested claim at the spot -> match() decided, nothing queued")
    st.removeEntity(r_, RR.REMOVE)
    # ---- World.execute throwing (world shutting down) -> caught, nothing queued, the item stays
    @JImplements("java.util.function.Consumer")
    class Boom(object):
        @JOverride
        def accept(self, t):
            raise JClass("java.lang.IllegalThreadStateException")("world closing")
    Book.EXEC = Boom()
    r_ = drop(st, "Rock_Stone_Cobble", 1, (56.5, 91.0, 56.5))
    K.check(alive(r_) and "late felled-log check" in str(Book.LAST), "LATE0: World.execute throws -> caught (one WARN), the item stays: %s" % Book.LAST)
    st.removeEntity(r_, RR.REMOVE)
    Book.EXEC = None
    # ---- static: the game path (EXEC null) is World.execute, behind the BreakTask SkyySkills queued with World.execute
    gen = open(os.path.join(HERE, "build_skyysacks_%s.py" % VERSION), encoding="utf8").read()
    lt = gen[gen.index("public static boolean late("):]
    lt = lt[:lt.index("}'''")]
    K.check("getWorld().execute(t)" in lt and "ex.accept(t)" in lt, "STATIC: late() queues with World.execute (EXEC only in the harness)")
    L["_late_player"] = RL


PRE = {}


def pre_system(L):
    """a CraftRecipeEvent$Pre listener standing in for SkyyGear's GearCraftPreSys (EntityEventSystem, Archetype.empty() query, cancels a
    recipe whose primary output is a pickaxe while ON) - registered on the real EntityStore.REGISTRY like any plugin system"""
    jp, CtF, CtM, CtC, REG = L["jp"], L["CtF"], L["CtM"], L["CtC"], L["REG"]
    from jpype import JClass
    EES = "com.hypixel.hytale.component.system.EntityEventSystem"
    PREC = "com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent$Pre"
    cc = jp.makeClass("com.hypixel.hytale.component.system.SkyyHkPreC", jp.get(EES))
    cc.addField(CtF.make("public static boolean ON = false;", cc))
    cc.addField(CtF.make("public static int SEEN = 0;", cc))
    cc.addConstructor(CtC.make("public SkyyHkPreC() { super(%s.class); }" % PREC, cc))
    cc.addMethod(CtM.make("public com.hypixel.hytale.component.query.Query getQuery() { return com.hypixel.hytale.component.Archetype.empty(); }", cc))
    cc.addMethod(CtM.make(
        "public void handle(int idx, com.hypixel.hytale.component.ArchetypeChunk chunk, com.hypixel.hytale.component.Store st, "
        "com.hypixel.hytale.component.CommandBuffer buf, com.hypixel.hytale.component.system.EcsEvent ev) { SEEN++; if (!ON) return; "
        "%s e = (%s) ev; if (e.isCancelled()) return; "
        "com.hypixel.hytale.server.core.inventory.MaterialQuantity po = e.getCraftedRecipe() == null ? null : e.getCraftedRecipe().getPrimaryOutput(); "
        "if (po != null && po.getItemId() != null && po.getItemId().indexOf(\"Pickaxe\") >= 0) e.setCancelled(true); }" % (PREC, PREC), cc))
    C = JClass(cc.toClass(JClass(EES).class_))
    REG.registerSystem(C())
    PRE["C"] = C


def craft_cases(L):
    from jpype import JClass, JArray, JString, JShort, JInt, JFloat
    K, st, jfield, ItemC, KMap, IS, SIC, cnt = L["K"], L["st"], L["jfield"], L["ItemC"], L["KMap"], L["IS"], L["SIC"], L["cnt"]
    RL = L["_late_player"]
    C = PRE["C"]
    Page = JClass(PKG + "CraftPage")
    MQ = JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
    CR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    BR = JClass("com.hypixel.hytale.protocol.BenchRequirement")
    it_ = ItemC(JString("Tool_Pickaxe_Copper"))
    jfield(ItemC.class_, "maxStack").setInt(it_, 1)
    KMap.CUSTOM.put(JString("Tool_Pickaxe_Copper"), it_)

    def recipe(rid, out, inputs):
        ins = JArray(MQ)([MQ(JString(i), None, None, JInt(q), None) for i, q in inputs])
        po = MQ(JString(out), None, None, JInt(1), None)
        r = CR(ins, po, JArray(MQ)([po]), JInt(1), JArray(BR)(0), JFloat(0.0), False, JInt(0))
        jfield(CR.class_, "id").set(r, JString(rid))
        return r
    pick = recipe("Tool_Pickaxe_Copper", "Tool_Pickaxe_Copper", [("Ore_Copper", 3)])
    plain = recipe("Skyy_Test_Cobble", "Rock_Stone_Cobble", [("Ore_Copper", 1)])
    # ---- /craft: CraftPage.preCraft = the event exactly as craftItem fires it, on the REAL store (every Pre listener sees it)
    C.ON, C.SEEN = True, 0
    K.check(not bool(Page.preCraft(st, RL, pick, 2)) and int(C.SEEN) == 1,
            "CRAFT /craft: preCraft(a pickaxe recipe) with a cancelling Pre listener -> refused (listener saw it once, seen %d)" % int(C.SEEN))
    K.check(bool(Page.preCraft(st, RL, plain, 2)) and int(C.SEEN) == 2, "CRAFT /craft: preCraft(a non-tool recipe) -> allowed")
    C.ON = False
    K.check(bool(Page.preCraft(st, RL, pick, 1)), "CRAFT /craft: no listener vetoes (SkyyGear rule off / absent) -> allowed as before")
    K.check(not bool(Page.preCraft(st, None, pick, 1)), "CRAFT /craft: the check throwing (no ref) counts as refused - nothing paid")
    # ---- pocket crafting / benches: the REAL CraftingManager.craftItem (PocketCraftWindow.handleAction calls it) honours the cancel
    C.ON, C.SEEN = True, 0
    CM = JClass("com.hypixel.hytale.builtin.crafting.component.CraftingManager")
    cont = SIC(JShort(9))
    cont.addItemStack(IS("Ore_Copper", 10))
    try:
        ok = bool(CM().craftItem(RL, st, pick, 1, cont))
        K.check(not ok and int(C.SEEN) == 1 and cnt(cont) == {"Ore_Copper": 10},
                "CRAFT pocket: the real CraftingManager.craftItem fires Pre, the cancel stops it - false, 10 Ore_Copper untouched (%s, seen %d, %s)"
                % (ok, int(C.SEEN), cnt(cont)))
    except Exception as e:   # noqa - the bare JVM may lack a piece craftItem reads; the bytecode check below carries the proof then
        K.notes.append("CRAFT pocket: real craftItem not runnable in the bare JVM (%s) - bytecode order checked instead" % str(e)[:160])
    C.ON = False
    # ---- static: the engine's craftItem refuses a cancelled Pre BEFORE removing inputs; our two paths reach the event before paying
    IP, PS, BOS = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")
    mm = L["jp"].get("com.hypixel.hytale.builtin.crafting.component.CraftingManager").getDeclaredMethod("craftItem")
    bos = BOS()
    IP(PS(bos)).print_(mm)
    bc = str(bos.toString())
    ia, ib, iz = bc.find("CraftRecipeEvent$Pre.<init>"), bc.find("CraftRecipeEvent$Pre.isCancelled"), bc.find("removeInputFromInventory")
    K.check(0 <= ia < ib < iz, "CRAFT engine: CraftingManager.craftItem fires Pre + checks the cancel before removeInputFromInventory")
    import perfworld_kit as PW
    g = PW.calls(L["jar"])
    K.check("com.hypixel.hytale.builtin.crafting.component.CraftingManager.craftItem" in g.get("PocketCraftWindow.handleAction", set()),
            "CRAFT pocket: PocketCraftWindow.handleAction crafts through CraftingManager.craftItem (vanilla FieldCraftingWindow too)")
    K.check(PKG + "CraftPage.preCraft" in g.get("CraftPage.handleDataEvent", set()), "CRAFT /craft: handleDataEvent calls preCraft")
    gen = open(os.path.join(HERE, "build_skyysacks_%s.py" % VERSION), encoding="utf8").read()
    h = gen[gen.index("public void handleDataEvent({REF} ref, {ST} st, String data) {{"):]
    h = h[:h.index('}}""", cpg))')]
    K.check(h.index("if (!preCraft(st, ref, r, qty))") < h.index("Object tx = mats.removeMaterials(inputs);") < h.index("gearRoll(u, gid"),
            "CRAFT /craft: the event comes before the materials are removed and before any output is given (refused = nothing paid)")
    K.check(h.count("removeMaterials(") == 1, "CRAFT /craft: the instant craft has ONE material removal (after the event)")
    L["Pool"].WRITER.shutdownNow()   # the fixture's writer thread (the 0.8.4 run_exec stops it at its end, past the slice) - else the JVM never exits


def _t085():
    sp = importlib.util.spec_from_file_location("t085", os.path.join(HERE, "test_skyysacks_0.8.5.py"))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    m.VERSION = VERSION   # its static checks read the 0.8.6 generated script
    return m


def run_snd(out, jar, scratch, home):
    _t085().run_snd(out, jar, os.path.join(scratch, "snd"), home)


def run_live(out, jar, scratch, home):
    m = _t085()
    if os.path.isfile(os.path.join(home, "sounds.properties")):
        # 0.8.5 is live: sounds.properties is already there, so the start adds nothing (0.8.6 writes no new file) - same strictness otherwise
        def live_twice(K, before, after1, after2, pfx="DS", also=()):
            new = sorted(set(after1) - set(before))
            changed = sorted(k for k in before if after1.get(k) != before[k])
            K.check(all(n.startswith(("config-history", "config-changes")) for n in new) and not changed,
                    "%s (0.8.5 live) the first start adds no file but kit history, no existing file changes: new %s changed %s" % (pfx, new, changed))
            K.check(after1 == after2, "%s the second start changes nothing" % pfx)
        m.G.live_twice = live_twice
    m.run_live(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("exec", run_exec), ("late", run_late), ("snd", run_snd), ("live", run_live)], __file__,
           live=(LIVE_DIR, "Skyy_SkyySacks"))
