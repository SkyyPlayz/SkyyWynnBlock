"""Harness for SkyyExploration 0.3.0 (tools/exploration_0_3_0_patch.py): PER-PROFILE WORLD LOOT CHESTS (round expchest; spec
research/Per-Player-Loot-Survey.md section 4 + docs/answered/project.md 2026-10-18 PER-PROFILE CHESTS: refill "Never", sparkles "Yes").
Build first: python tools/exploration_0_3_0_patch.py && python SkyyExploration/build_skyyexploration_0.3.0.py

    python SkyyExploration/test_skyyexploration_0.3.0.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.2.15 -> 0.3.0: only the expected members differ, the 12 Pc* classes added, non-class entries: manifest.json + the sparkle
  PC   the REAL PcCore / PcStore / PcBox code on the engine's own ItemStack / SimpleItemContainer / ItemStack.CODEC (stand-in Item asset
       map), the engine seam PcApi as a stand-in (the chest block, the window, the particles) and stand-in bridge functions (profile:fn:key,
       mob:fn:levelAt, gear:fn:box): intercept (world chest / player-placed / unregistered / placed over / excluded world / off); OPEN
       (fresh roll: gear -> a bag at the zone level, the extra bag, the shared container emptied, record written before the window), the
       take-only copy (a put-in is refused), TAKES (every take -> the record), CLOSE, REOPEN (leftovers, no new roll), a live window ->
       'already open', a stale window -> dead (never writes again), window refused, no container, busy, a SECOND PROFILE (own roll, the
       first untouched), the PROFILE SWITCH close, SPARKLES (unloaded -> async load; unopened only; range; player-placed never; at most 8;
       refill due), REFILL (0 never; above 0 re-roll), BREAK / DAMAGE rule, RESTART (files -> memory -> the same leftovers), a BAD file
       (open refused, never written over), an unreadable record, the dupe ledger (items out of one profile's copy <= items rolled)
       FIX ROUND: the shared pile is MOVED into the first copy (never deleted; stamped gear untouched), stray shared stacks / a Creative
       break -> the recovery file, a take after a profile switch closes the copy, the nearest 8 sparkle, the index is built on the IO
       thread (stale entries filtered), idle records leave memory (never pending / open ones; reopen = the same leftovers), the load
       fast path does not wait for a write lock, a failing write keeps retrying (30 s), chest-luck gear -> a bag (ExpAward.luckStack),
       the break / damage guards check for a block entity first (class bytes)
  LIVE start twice on a scratch COPY of the live Skyy_SkyyExploration folder: migrations + config + chest registry load as 0.2.15 did, no
       existing file changes; a real live world chest opened for a real live profile key writes chestloot/; the second start reads it
       back (reopen = the same leftovers); every pre-existing file byte-identical at the end
  AA   engine-access audit
Not executable without a running server (UNVERIFIED, Skyy's in-game test): PcUseSys / PcBreakSys / PcDmgSys handle(), PcCore.engOpen /
engClose / live (engine) / spark (engine) / PcCloseTask - the vanilla chest page drawing our window, the lid animation, the sparkles.
Exit code 1 on any failure.
"""
import os, sys, shutil, time, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import skyybuild as B

VERSION, OLD = "0.3.0", "0.2.15"
JAR = os.path.join(HERE, "SkyyExploration-%s.jar" % VERSION)
OLD_JAR = os.path.join(HERE, "SkyyExploration-%s.jar" % OLD)
PKG = "com.skyy.explore."
SCRATCH = HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "expchest", "harness"))
LIVE = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyExploration")   # the deploy world (read-only source)
ADDED = ["PcBox", "PcWin", "PcApi", "PcStore", "PcJob", "PcCore", "PcChange", "PcOpenTask", "PcCloseTask", "PcUseSys", "PcBreakSys", "PcDmgSys", "PcBagFn"]
# every diff checked by hand 2026-10-20: the version texts (CfgFn.opExport / CfgRows.header / the default file head in CfgFile + CfgRows /
# ExpLgMig + ExpNcMig's WHO), the six chests.* keys (ExpCfg fields, apply / load / live, the kit rows), ExpTick.second's PcCore.second call,
# setup (chestloot dir, 3 systems, the explore.sparkles setting, the ready line) + shutdown (PcStore.flushAll)
EXPECT = {
    "CfgFile": ["~<clinit>"],
    "CfgFn": ["~m opExport"],
    "CfgRows": ["~<clinit>", "~m header"],
    "ExpAward": ["+f PCBAG", "+f PCLV", "+m luckStack", "~<clinit>", "~m luck"],   # fix round: chest-luck gear -> a bag on a per-profile open
    "ExpCfg": ["+f PC_EXTRA", "+f PC_NOBREAK", "+f PC_ON", "+f PC_REFILL_S", "+f PC_SPARK", "+f PC_SPARK_R", "~<clinit>", "~m apply", "~m live", "~m load"],
    "ExpLgMig": ["~m logLine", "~m migrate"],
    "ExpNcMig": ["~m logLine", "~m migrate"],
    "ExpTick": ["~m second"],
    "SkyyExplorationPlugin": ["~m setup", "~m shutdown"],
}
SPARK = "Server/Particles/SkyyExploration/Skyy_Explore_Chest_Sparkle.particlesystem"
_eq0 = HK.Child.eq


def _eq(self, got, want, what):
    """the compare allows manifest.json + the new sparkle particle system (checked: our name, a LifeSpan, only vanilla spawner ids)"""
    if what == "C: non-class entries changed" and want == ["manifest.json"]:
        import zipfile
        j = json.loads(zipfile.ZipFile(JAR).read(SPARK).decode("utf-8"))
        ok = sorted(got) == sorted(["manifest.json", SPARK]) and j.get("LifeSpan") == 1.2 and [x["SpawnerId"] for x in j["Spawners"]] == ["Block_Treasure_Spark", "Block_Treasure_Star"]
        return self.check(ok, "C: non-class entries changed = manifest.json + the sparkle (LifeSpan 1.2, vanilla Spark + Star spawners): %s %s" % (got, j))
    return _eq0(self, got, want, what)
HK.Child.eq = _eq


def engine(scratch):
    """the engine bits a bare JVM needs for ItemStack / containers (SkyyArmory 0.1.38's harness setup): server options, a stand-in
    HytaleServer with an EventBus, the asset registry, stand-in Items in the Item asset map"""
    from jpype import JClass, JString, JArray
    JClass("com.hypixel.hytale.server.core.Options").parse(JArray(JString)(["--universe", os.path.join(scratch, "universe")]))
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)
    HS = JClass("com.hypixel.hytale.server.core.HytaleServer")
    hs = U.allocateInstance(HS.class_)
    f_ = HS.class_.getDeclaredField("eventBus")
    f_.setAccessible(True)
    f_.set(hs, JClass("com.hypixel.hytale.event.EventBus")(False))
    f_ = HS.class_.getDeclaredField("instance")
    f_.setAccessible(True)
    f_.set(None, hs)
    JClass("com.hypixel.hytale.server.core.asset.AssetRegistryLoader").init()
    ITM = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    fm = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap").class_.getDeclaredField("assetMap")
    fm.setAccessible(True)
    mp = fm.get(ITM.getAssetMap())
    for i in ("Weapon_Sword_Iron", "Ingredient_Stick", "Rock_Gem_Ruby", "Skyy_Unid_Test", "Armor_Iron_Chest"):
        it_ = ITM(JString(i))
        g = ITM.class_.getDeclaredField("maxStack")
        g.setAccessible(True)
        g.setInt(it_, 100)
        mp.put(JString(i), it_)
    return U


def world(U, name):
    from jpype import JClass
    W = JClass("com.hypixel.hytale.server.core.universe.world.World")
    w = U.allocateInstance(W.class_)
    f_ = W.class_.getDeclaredField("name")
    f_.setAccessible(True)
    f_.set(w, name)
    return w


def run_pc(out, jar, scratch, _home):
    from jpype import JClass, JString, JInt, JShort, JImplements, JOverride, JObject, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar])
    U = engine(scratch)
    Paths, Executors, UUID, Integer = JClass("java.nio.file.Paths"), JClass("java.util.concurrent.Executors"), JClass("java.util.UUID"), JClass("java.lang.Integer")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    BD = JClass("org.bson.BsonDocument")
    ArrayList = JClass("java.util.ArrayList")
    Cfg, Reg, EIO = JClass(PKG + "ExpCfg"), JClass(PKG + "ChestReg"), JClass(PKG + "ExpIO")
    Core, Sto, Box = JClass(PKG + "PcCore"), JClass(PKG + "PcStore"), JClass(PKG + "PcBox")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyExpTest")
    d = os.path.join(scratch, "pc")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(os.path.join(d, "chests"))
    Cfg.FILE = Paths.get(os.path.join(d, "config.properties"))
    Cfg.load()
    K.check(bool(Cfg.PC_ON) and int(Cfg.PC_REFILL_S) == 0 and bool(Cfg.PC_SPARK) and int(Cfg.PC_SPARK_R) == 24 and int(Cfg.PC_EXTRA) == 33 and bool(Cfg.PC_NOBREAK),
            "PC: defaults - on, refill 0 (never), sparkles on, range 24, extra bag 33 %, can't break")
    cfgt = open(os.path.join(d, "config.properties"), encoding="latin-1").read()
    K.check(all(l in cfgt for l in ("chests.perProfile=true", "chests.refillSeconds=0", "chests.sparkles=true", "chests.sparkleRange=24", "chests.extraBagChance=33", "chests.noBreak=true")),
            "PC: a fresh config.properties carries the six 0.3.0 lines")
    Reg.DIR = Paths.get(os.path.join(d, "chests"))
    Sto.DIR = Paths.get(os.path.join(d, "chestloot"))
    EIO.STOPPING = False
    EIO.EXEC = Executors.newSingleThreadScheduledExecutor()

    def settle():
        EIO.stop()
        EIO.STOPPING = False
        EIO.EXEC = Executors.newSingleThreadScheduledExecutor()
        Sto.flushAll()

    br = EIO.bridge()
    KEY = {}
    GEARCALLS = []

    @JImplements("java.util.function.Function")
    class KeyFn:
        @JOverride
        def apply(self, u):
            return KEY.get(str(u), str(u))

    @JImplements("java.util.function.Function")
    class LevelFn:
        @JOverride
        def apply(self, a):
            return JArray(JObject)([Integer.valueOf(10), Integer.valueOf(12)])

    @JImplements("java.util.function.Function")
    class BoxFn:
        @JOverride
        def apply(self, a):
            src = a[0]
            lv = int(a[1])
            GEARCALLS.append((None if src is None else str(src.getItemId()), lv, str(a[2])))
            md = BD.parse(JString('{"SkyyUnid": {"lv": %d, "from": "%s"}}' % (lv, "extra" if src is None else str(src.getItemId()))))
            return IS(JString("Skyy_Unid_Test"), JInt(1), md)
    br.put("profile:fn:key", KeyFn())
    br.put("mob:fn:levelAt", LevelFn())
    br.put("gear:fn:box", BoxFn())

    ST = {"cap": 18, "shared": {}, "placed": {}, "rolls": 0, "opened": [], "live": True, "openok": True, "closed": [], "sparks": [], "cleared": 0}

    def drops():
        return [IS(JString("Weapon_Sword_Iron"), JInt(1)), IS(JString("Ingredient_Stick"), JInt(5)), IS(JString("Rock_Gem_Ruby"), JInt(2))]

    @JImplements(PKG + "PcApi")
    class Api:
        @JOverride
        def cap(self, w, x, y, z): return ST["cap"]

        @JOverride
        def takeShared(self, w, x, y, z):
            l = ArrayList()
            for sl, st_ in ST["shared"].pop((x, y, z), []):
                l.add(JArray(JObject)([Integer.valueOf(sl), st_]))
            ST["cleared"] += int(l.size())
            return l

        @JOverride
        def placedBy(self, w, x, y, z): return ST["placed"].get((x, y, z))

        @JOverride
        def roll(self, dl):
            ST["rolls"] += 1
            l = ArrayList()
            for s in drops():
                l.add(s)
            return l

        @JOverride
        def open(self, u, w, x, y, z, box):
            ST["opened"].append(box)
            return ST["openok"]

        @JOverride
        def live(self, u, box): return ST["live"]

        @JOverride
        def close(self, u, box): ST["closed"].append(box)

        @JOverride
        def spark(self, u, x, y, z): ST["sparks"].append((str(u), x, y, z))
    Core.API = Api()
    W1 = world(U, "w1")
    wf = str(Reg.wf("w1"))
    C1, C2, CP = (10, 64, 10), (20, 64, 20), (30, 64, 30)
    Reg.put("w1", wf, *C1, "Zone1_Kweebec_Tier1", "-")
    Reg.put("w1", wf, *C2, "Zone2_Trork_Tier2", "-")
    Reg.put("w1", wf, *CP, "Zone1_Kweebec_Tier1", "d8ddde89-98b2-4739-983e-a39773d582b6")
    # the shared container of chest 1 still holds its world roll (a never-opened chest): sticks slot 0, the sword slot 2, rubies slot 7
    ST["shared"][C1] = [(0, IS(JString("Ingredient_Stick"), JInt(5))), (2, IS(JString("Weapon_Sword_Iron"), JInt(1))), (7, IS(JString("Rock_Gem_Ruby"), JInt(2)))]
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    pr = U.allocateInstance(PRef.class_)
    u1, u2, u3 = UUID.fromString("11111111-1111-1111-1111-111111111111"), UUID.fromString("22222222-2222-2222-2222-222222222222"), UUID.fromString("33333333-3333-3333-3333-333333333333")
    KA, KB = str(u1), str(u1) + "-p2"
    KEY[str(u1)] = KA

    # ---------------- intercept
    K.check(bool(Core.intercept(pr, W1, *C1)), "PC intercept: a world-generated loot chest -> the vanilla open is cancelled")
    K.check(not bool(Core.intercept(pr, W1, *CP)), "PC intercept: a chest recorded with a placer (player-placed / /stash set) stays vanilla")
    K.check(not bool(Core.intercept(pr, W1, 1, 2, 3)), "PC intercept: an unregistered block stays vanilla")
    ST["placed"][C2] = "someone"
    K.check(not bool(Core.intercept(pr, W1, *C2)), "PC intercept: a chest a player placed at an old world chest spot stays vanilla")
    del ST["placed"][C2]
    K.check(not bool(Core.intercept(pr, world(U, "skyy-island-abc"), *C1)) and not bool(Core.intercept(None, W1, *C1)), "PC intercept: an excluded world (islands) / no player -> vanilla")
    Cfg.PC_ON = False
    K.check(not bool(Core.intercept(pr, W1, *C1)) and str(Core.open(None, u1, W1, "w1", wf, *C1, 1000)) == "off", "PC intercept + open: chests.perProfile off -> vanilla")
    Cfg.PC_ON = True
    K.eq(str(Core.open(None, u1, W1, "w1", wf, 1, 2, 3, 1000)), "not a world loot chest", "PC open: an unregistered spot")
    K.eq(str(Core.open(None, u1, W1, "w1", wf, *CP, 1000)), "not a world loot chest", "PC open: a player-placed record")

    # ---------------- open profile A (fresh roll)
    Cfg.PC_EXTRA = 100
    t0 = 1_000_000
    r = str(Core.open(None, u1, W1, "w1", wf, *C1, t0))
    K.eq(r, "inherited 4", "PC open A: the first open takes over the shared container's 3 stacks (no roll) + the extra bag")
    box = ST["opened"][-1]

    def items(c):
        out = []
        for s in range(int(c.getCapacity())):
            it = c.getItemStack(JShort(s))
            if it is not None and not it.isEmpty():
                out.append((str(it.getItemId()), int(it.getQuantity()), None if it.getMetadata() is None else str(it.getMetadata().toJson())))
        return sorted(out, key=lambda t: (t[0], t[1], t[2] or ""))
    got = items(box)
    K.check([g[0] for g in got] == ["Ingredient_Stick", "Rock_Gem_Ruby", "Skyy_Unid_Test", "Skyy_Unid_Test"] and int(box.getCapacity()) == 18,
            "PC open A: the copy = sticks, rubies, the sword as a mystery bag + the extra bag, in an 18-slot copy: %s" % got)
    K.check(len(GEARCALLS) == 2 and GEARCALLS[0][0] == "Weapon_Sword_Iron" and 10 <= GEARCALLS[0][1] <= 12 and GEARCALLS[1][0] is None and GEARCALLS[1][2] == "chest",
            "PC open A: gear:fn:box got the sword at the chest's zone level (mob:fn:levelAt 10-12) and the extra bag: %s" % GEARCALLS)
    K.check(ST["cleared"] == 3 and ST["rolls"] == 0 and C1 not in ST["shared"], "PC open A: the shared container's 3 stacks were taken out (emptied), no roll")
    K.check(str(box.getItemStack(JShort(0)).getItemId()) == "Ingredient_Stick" and str(box.getItemStack(JShort(7)).getItemId()) == "Rock_Gem_Ruby"
            and str(box.getItemStack(JShort(2)).getItemId()) == "Skyy_Unid_Test", "PC open A: the shared stacks keep their slots (the sword -> a bag in slot 2)")
    rec = Sto.get(KA, wf, *C1)
    K.check(rec is not None and str(rec[0]) == str(t0) and str(rec[1]).count('"slot"') == 4, "PC open A: the record (4 stacks) exists BEFORE any take")
    K.check(str(box.key) == KA and not bool(box.dead) and Core.OPEN.get(u1) == box, "PC open A: the box belongs to profile A and is the open one")
    inv = SIC(JShort(9))
    inv.setItemStackForSlot(JShort(0), IS(JString("Armor_Iron_Chest"), JInt(1)))
    t = inv.moveItemStackFromSlot(JShort(0), box)
    K.check(not bool(t.succeeded()) and len(items(box)) == 4 and inv.getItemStack(JShort(0)) is not None, "PC take-only: putting an item into the copy is refused (it stays in the inventory)")
    K.eq(str(Core.open(None, u1, W1, "w1", wf, *C1, t0 + 5)), "already open", "PC open A again while the window is live -> already open (one copy window)")

    # ---------------- takes
    def slot_of(c, iid):
        for s in range(int(c.getCapacity())):
            it = c.getItemStack(JShort(s))
            if it is not None and not it.isEmpty() and str(it.getItemId()) == iid:
                return s
        return -1
    inv2 = SIC(JShort(9))
    taken = []
    for iid in ("Ingredient_Stick", "Skyy_Unid_Test"):
        s = slot_of(box, iid)
        t = box.moveItemStackFromSlot(JShort(s), inv2)
        K.check(bool(t.succeeded()), "PC take: %s moved out of the copy" % iid)
        taken.append(iid)
    rec = Sto.get(KA, wf, *C1)
    K.check(str(rec[1]).count('"slot"') == 2, "PC take: every take updates the record at once (2 stacks left)")
    Core.closedBox(box)
    K.check(bool(box.dead) and Core.SESS.isEmpty() and Core.OPEN.get(u1) is None, "PC close: the box is dead, no session left")
    left = items(box)

    # ---------------- reopen A: the leftovers, no new roll
    r = str(Core.open(None, u1, W1, "w1", wf, *C1, t0 + 10))
    box2 = ST["opened"][-1]
    K.check(r == "reopened" and items(box2) == left and ST["rolls"] == 0 and len(GEARCALLS) == 2,
            "PC reopen A: the same leftovers (ids, counts, metadata), no second roll: %s %s" % (r, items(box2)))
    # stale window (the window went away without a close): the old box dies and never writes again
    ST["live"] = False
    r = str(Core.open(None, u1, W1, "w1", wf, *C1, t0 + 20))
    box3 = ST["opened"][-1]
    K.check(r == "reopened" and bool(box2.dead) and not bool(box3.dead), "PC stale window: the old copy is marked dead, a new one opens from the record")
    s = slot_of(box2, "Rock_Gem_Ruby")
    box2.moveItemStackFromSlot(JShort(s), SIC(JShort(9)))     # (a dead copy has no window in game; here only its record is watched)
    K.check(str(Sto.get(KA, wf, *C1)[1]).count('"slot"') == 2, "PC stale window: a take from the dead copy never touches the record (no dupe)")
    ST["live"] = True
    # take everything from the live copy -> an empty record that stays (looted on this profile)
    for s in range(18):
        it = box3.getItemStack(JShort(s))
        if it is not None and not it.isEmpty():
            box3.moveItemStackFromSlot(JShort(s), inv2)
    Core.closedBox(box3)
    rec = Sto.get(KA, wf, *C1)
    K.check(rec is not None and '"slot"' not in str(rec[1]), "PC looted: an emptied copy keeps an empty record (looted on this profile)")
    r = str(Core.open(None, u1, W1, "w1", wf, *C1, t0 + 30))
    K.check(r == "reopened" and items(ST["opened"][-1]) == [] and ST["rolls"] == 0, "PC looted: the next open is empty, still no new roll")
    Core.closedBox(ST["opened"][-1])
    # dupe ledger: what profile A ever took out of chest 1 (inv2) <= what was rolled for it
    led = {}
    for i in items(inv2):
        led[i[0]] = led.get(i[0], 0) + i[1]
    K.check(led == {"Ingredient_Stick": 5, "Rock_Gem_Ruby": 2, "Skyy_Unid_Test": 2},
            "PC ledger: everything profile A took out of chest 1 over 4 opens = exactly what was rolled once (5 sticks, 2 rubies, 2 bags): %s" % led)

    # ---------------- second profile of the same account: its own roll, A untouched
    recA = list(Sto.get(KA, wf, *C1))
    KEY[str(u1)] = KB
    r = str(Core.open(None, u1, W1, "w1", wf, *C1, t0 + 40))
    boxB = ST["opened"][-1]
    K.check(r == "rolled 4" and ST["rolls"] == 1 and str(boxB.key) == KB and ST["cleared"] == 3, "PC profile B: its own fresh roll of the same chest (the shared one stays empty)")
    K.check([str(x) for x in Sto.get(KA, wf, *C1)] == [str(x) for x in recA], "PC profile B: profile A's record is untouched")
    # the profile switch while B's copy is open: the tick closes it
    KEY[str(u1)] = KA
    Cfg.PC_SPARK = False
    Core.second(None, None, None, u1, W1, "w1", wf, KA, t0 + 41)
    K.check(len(ST["closed"]) == 1 and ST["closed"][0] == boxB, "PC switch: the copy opened under profile B closes when the key changes")
    Core.closedBox(boxB)
    Cfg.PC_SPARK = True
    # fix round: a TAKE after the profile switched closes the copy at once (the take is recorded against the copy's own profile B)
    KEY[str(u1)] = KB
    r = str(Core.open(None, u1, W1, "w1", wf, *C1, t0 + 42))
    boxB2 = ST["opened"][-1]
    nB = str(Sto.get(KB, wf, *C1)[1]).count('"slot"')
    KEY[str(u1)] = KA
    ncl = len(ST["closed"])
    t = boxB2.moveItemStackFromSlot(JShort(slot_of(boxB2, "Ingredient_Stick")), SIC(JShort(9)))
    K.check(r == "reopened" and bool(t.succeeded()) and len(ST["closed"]) == ncl + 1 and ST["closed"][-1] == boxB2
            and str(Sto.get(KB, wf, *C1)[1]).count('"slot"') == nB - 1,
            "PC switch (fix): a take after the key changed closes the copy at once and is recorded against profile B (no dupe)")
    Core.closedBox(boxB2)
    KEY[str(u1)] = KA
    br.put("profile:busy:" + str(u1), JClass("java.lang.Boolean").TRUE)
    K.eq(str(Core.open(None, u1, W1, "w1", wf, *C2, t0 + 50)), "busy", "PC busy: no open while profile:busy")
    br.remove("profile:busy:" + str(u1))
    # window refused -> the roll stays recorded (exactly once), next open shows it
    ST["openok"] = False
    r = str(Core.open(None, u1, W1, "w1", wf, *C2, t0 + 60))
    ST["openok"] = True
    K.check(r == "rolled 4, window refused" and Core.SESS.isEmpty() and Sto.get(KA, wf, *C2) is not None, "PC window refused: the roll is recorded, nothing stays open")
    r = str(Core.open(None, u1, W1, "w1", wf, *C2, t0 + 70))
    K.check(r == "reopened" and ST["rolls"] == 2, "PC window refused: the next open shows that roll (no second roll)")
    Core.closedBox(ST["opened"][-1])
    ST["cap"] = -1
    Reg.put("w1", wf, 40, 64, 40, "Zone1_Kweebec_Tier1", "-")
    K.eq(str(Core.open(None, u1, W1, "w1", wf, 40, 64, 40, t0 + 80)), "no container", "PC open: no container at the spot -> nothing")
    ST["cap"] = 18
    Reg.remove(wf, 40, 64, 40)

    # ---------------- fix round: a chest opened before 0.3.0 that players stored things in - nothing is deleted
    u4 = UUID.fromString("44444444-4444-4444-4444-444444444444")
    K4 = str(u4)
    KEY[K4] = K4
    C3 = (50, 64, 50)
    Reg.put("w1", wf, *C3, "Zone1_Kweebec_Tier1", "-")
    stamped = IS(JString("Armor_Iron_Chest"), JInt(1), BD.parse(JString('{"SkyyGear": {"stamp": "kept"}}')))
    ST["shared"][C3] = [(0, stamped), (1, IS(JString("Ingredient_Stick"), JInt(7)))]
    ng, nr = len(GEARCALLS), ST["rolls"]
    r = str(Core.open(None, u4, W1, "w1", wf, *C3, t0 + 85))
    b4 = ST["opened"][-1]
    got = items(b4)
    K.check(r == "inherited 3" and ST["rolls"] == nr and C3 not in ST["shared"]
            and ("Armor_Iron_Chest", 1, '{"SkyyGear": {"stamp": "kept"}}') in got and ("Ingredient_Stick", 7, None) in got
            and len(GEARCALLS) == ng + 1 and GEARCALLS[-1][0] is None,
            "PC deposits (fix): a stored stamped armour piece + 7 sticks move into the first copy unchanged (no bag for stamped gear) + the extra bag: %s %s" % (r, got))
    K.check(str(Sto.get(K4, wf, *C3)[1]).count('"slot"') == 3, "PC deposits (fix): the moved stacks are in that profile's record before the window opens")
    Core.closedBox(b4)
    # stacks found in the shared container at a REOPEN (a bypass) -> the recovery file, never deleted, never into the copy
    ST["shared"][C3] = [(5, IS(JString("Rock_Gem_Ruby"), JInt(3)))]
    r = str(Core.open(None, u4, W1, "w1", wf, *C3, t0 + 86))
    Core.closedBox(ST["opened"][-1])
    EIO.drain()
    rf = os.path.join(d, "chestloot", "_cleared", wf + ".txt")
    rt = open(rf, encoding="utf8").read() if os.path.isfile(rf) else ""
    K.check(r == "reopened" and len(items(ST["opened"][-1])) == 3 and C3 not in ST["shared"] and rt.count("\nC ") + rt.startswith("C ") == 1
            and rt.startswith("C 50 64 50 ") and " found-at-reopen " in rt and '"Rock_Gem_Ruby"' in rt and int(Sto.RECOVERED.get()) == 1,
            "PC recovery (fix): shared stacks found at a reopen go to chestloot/_cleared/<world>.txt (C x y z ms why json), the copy is unchanged: %r" % rt[:160])
    Reg.remove(wf, *C3)

    # ---------------- sparkles
    KEY[str(u2)] = str(u2)
    ST["sparks"].clear()
    n = int(Core.sparkAround(u2, None, None, str(u2), wf, "w1", 12, 64, 12, t0 + 100))
    K.check(n == 0 and not ST["sparks"], "PC sparkles: profile not in memory yet -> nothing this second (loaded on SkyyExploration-IO)")
    settle()
    K.check(bool(Sto.loaded(str(u2), wf)), "PC sparkles: the async load ran")
    Sto.IDX.clear()
    i0 = Sto.index(wf, t0 + 100)
    K.check(int(i0.size()) == 0, "PC index (fix): the first call returns at once (empty) and queues the build on SkyyExploration-IO")
    settle()
    K.check(Sto.IDX.get(wf) is not None and Sto.IDXBUSY.get(wf) is None and int(Sto.index(wf, t0 + 100).size()) > 0, "PC index (fix): built on the IO thread")
    n = int(Core.sparkAround(u2, None, None, str(u2), wf, "w1", 12, 64, 12, t0 + 101))
    K.check(n == 2 and sorted(s[1:] for s in ST["sparks"]) == [C1, C2], "PC sparkles: a fresh profile sees both world chests (never the player-placed one): %s" % ST["sparks"])
    ST["sparks"].clear()
    n = int(Core.sparkAround(u1, None, None, KA, wf, "w1", 12, 64, 12, t0 + 102))
    K.check(n == 0, "PC sparkles: profile A opened both -> no sparkles")
    n = int(Core.sparkAround(u2, None, None, str(u2), wf, "w1", 200, 64, 200, t0 + 103))
    K.check(n == 0, "PC sparkles: out of range -> none")
    for i in range(12):
        Reg.put("w1", wf, 100 + i, 70, 100, "Zone1_Kweebec_Tier1", "-")
    Sto.index(wf, t0 + 10000)
    settle()
    ST["sparks"].clear()
    n = int(Core.sparkAround(u2, None, None, str(u2), wf, "w1", 105, 70, 100, t0 + 10000))
    xs = sorted(s_[1] for s_ in ST["sparks"])
    K.check(n == 8 and len(ST["sparks"]) == 8, "PC sparkles: at most 8 at once (12 near)")
    K.check(set(range(102, 109)) <= set(xs) and set(xs) <= set(range(101, 110)), "PC sparkles (fix): the NEAREST 8 (x 101-109 around 105, never 100 / 110 / 111): %s" % xs)
    for i in range(12):
        Reg.remove(wf, 100 + i, 70, 100)

    # ---------------- refill
    Cfg.PC_REFILL_S = 60
    ST["sparks"].clear()
    n = int(Core.sparkAround(u1, None, None, KA, wf, "w1", 12, 64, 12, t0 + 60030))
    K.check(n == 1 and ST["sparks"][0][1:] == C1, "PC refill 60 s: chest 1 (rolled at t0) sparkles again after 60 s, chest 2 (rolled 60 ms later) not yet: %s" % ST["sparks"])
    ST["sparks"].clear()
    n = int(Core.sparkAround(u2, None, None, str(u2), wf, "w1", 105, 70, 100, t0 + 60031))
    K.check(n == 0, "PC sparkles (fix): chests gone from the registry never sparkle from an older index")
    r = str(Core.open(None, u1, W1, "w1", wf, *C1, t0 + 60040))
    K.check(r == "rolled 4" and len(items(ST["opened"][-1])) == 4, "PC refill: the due chest is rolled again for that profile")
    Core.closedBox(ST["opened"][-1])
    Cfg.PC_REFILL_S = 0
    K.check(not bool(Core.refillDue(Sto.get(KA, wf, *C1), t0 + 10 ** 12)), "PC refill 0: never due")

    # ---------------- break / damage
    K.eq(int(Core.breakRule(W1, *C1, False, False)), 1, "PC break: outside Creative a world loot chest can't be broken")
    ST["shared"][C1] = [(3, IS(JString("Rock_Gem_Ruby"), JInt(1))), (4, IS(JString("Ingredient_Stick"), JInt(1)))]
    K.eq(int(Core.breakRule(W1, *C1, True, False)), 2, "PC break: Creative may break it")
    EIO.drain()
    rt = open(rf, encoding="utf8").read()
    K.check(C1 not in ST["shared"] and "\nC 10 64 10 " in rt and " chest-broken " in rt and int(Sto.RECOVERED.get()) == 3,
            "PC break: ... the shared container was emptied first (drops the chest only) and its 2 stacks went to the recovery file (fix)")
    K.eq(int(Core.breakRule(W1, *C1, False, True)), 1, "PC damage: no break progress outside Creative")
    ST["shared"][C1] = [(3, IS(JString("Rock_Gem_Ruby"), JInt(1)))]
    K.check(int(Core.breakRule(W1, *C1, True, True)) == 2 and len(ST["shared"].get(C1)) == 1, "PC damage: Creative damage is allowed and empties nothing yet")
    Cfg.PC_NOBREAK = False
    K.check(int(Core.breakRule(W1, *C1, False, False)) == 2 and C1 not in ST["shared"] and int(Sto.RECOVERED.get()) == 4, "PC break: noBreak off -> allowed, shared emptied first (recovery file)")
    Cfg.PC_NOBREAK = True
    K.check(int(Core.breakRule(W1, *CP, False, False)) == 0 and int(Core.breakRule(W1, 1, 2, 3, False, False)) == 0, "PC break: player chests / other blocks untouched")

    # ---------------- restart: files -> memory -> the same leftovers
    settle()
    fA = os.path.join(d, "chestloot", KA, wf + ".txt")
    fB = os.path.join(d, "chestloot", KB, wf + ".txt")
    tA = open(fA, encoding="utf8").read() if os.path.isfile(fA) else ""
    K.check(tA.startswith("# SkyyExploration per-profile world loot chests - profile %s, world w1\n" % KA) and tA.count("\nC ") == 2
            and ("\nC 10 64 10 " in tA) and ("\nC 20 64 20 " in tA) and os.path.isfile(fB),
            "PC files: chestloot/<pkey>/<world>.txt per profile, one 'C x y z at items' line per rolled chest")
    K.check(not [n_ for r_, _d, fs in os.walk(os.path.join(d, "chestloot")) for n_ in fs if n_.endswith(".tmp")], "PC files: no .tmp left (atomic writes)")
    before = {}
    for k_ in (KA, KB):
        for c_ in (C1, C2):
            v = Sto.get(k_, wf, *c_)
            before[(k_, c_)] = None if v is None else (str(v[0]), str(v[1]))
    Sto.M.clear()
    Sto.WN.clear()
    Core.SESS.clear()
    Core.OPEN.clear()
    after = {}
    for k_ in (KA, KB):
        Sto.load(k_, wf, "w1")
        for c_ in (C1, C2):
            v = Sto.get(k_, wf, *c_)
            after[(k_, c_)] = None if v is None else (str(v[0]), str(v[1]))
    K.check(before == after, "PC restart: every record reads back identically")
    KEY[str(u1)] = KB
    r = str(Core.open(None, u1, W1, "w1", wf, *C1, t0 + 70000))
    K.check(r == "reopened" and len(items(ST["opened"][-1])) == 3, "PC restart: profile B's copy reopens with its 3 stacks (4 rolled, the sticks taken after the switch)")
    Core.closedBox(ST["opened"][-1])
    KEY[str(u1)] = KA

    # ---------------- fix round: idle records leave memory (never pending / open ones); a reopen reads the same leftovers back
    settle()
    import time as _t
    real = int(_t.time() * 1000)
    fkA, fkB = str(Sto.fkey(KA, wf)), str(Sto.fkey(KB, wf))
    leftA = [str(x) for x in Sto.get(KA, wf, *C1)]
    rr0 = ST["rolls"]
    K.eq(int(Core.evict(wf, real, 600000)), 0, "PC evict (fix): nothing idle yet -> nothing leaves memory")
    Sto.PEND.put(fkB, JClass("java.lang.Boolean").TRUE)
    KEY[str(u1)] = KA
    r = str(Core.open(None, u1, W1, "w1", wf, *C1, t0 + 75000))
    boxE = ST["opened"][-1]
    ne = int(Core.evict(wf, real + 11 * 60000, 600000))
    K.check(Sto.M.get(fkA) is not None and Sto.M.get(fkB) is not None, "PC evict (fix): a record with an open copy (A) or a write pending (B) stays in memory")
    Core.closedBox(boxE)
    Sto.PEND.remove(fkB)
    settle()
    ne = int(Core.evict(wf, real + 11 * 60000, 600000))
    K.check(ne >= 2 and Sto.M.get(fkA) is None and Sto.M.get(fkB) is None and Sto.LAST.get(fkA) is None, "PC evict (fix): idle 10 min -> left memory (%d)" % ne)
    r = str(Core.open(None, u1, W1, "w1", wf, *C1, t0 + 75100))
    K.check(r == "reopened" and [str(x) for x in Sto.get(KA, wf, *C1)][1] == leftA[1] and ST["rolls"] == rr0,
            "PC evict (fix): the next open reads the record back from disk - the same leftovers, no new roll (%s)" % r)
    Core.closedBox(ST["opened"][-1])
    settle()
    # the world thread never waits for a write: another thread holds the write lock 3 s while a loaded + an unloaded load run
    import jpype as _jp
    Thread, Runnable = JClass("java.lang.Thread"), None
    held = {"in": False}

    @JImplements("java.lang.Runnable")
    class Hold:
        @JOverride
        def run(self):
            with _jp.synchronized(Sto.WLOCK):
                held["in"] = True
                JClass("java.lang.Thread").sleep(3000)
    th = Thread(Hold())
    th.start()
    while not held["in"]:
        _t.sleep(0.01)
    t1 = _t.time()
    l1 = int(Sto.load(KA, wf, "w1"))
    Sto.M.remove(fkB)
    l2 = int(Sto.load(KB, wf, "w1"))
    dt = _t.time() - t1
    th.join()
    Mod = JClass("java.lang.reflect.Modifier")
    syn = [str(m_.getName()) for m_ in Sto.class_.getDeclaredMethods() if Mod.isSynchronized(m_.getModifiers())]
    K.check(l1 == 1 and l2 == 1 and dt < 1.0 and not syn, "PC locks (fix): load (in memory + from disk) ran in %.3f s while a write held its lock; no synchronized PcStore method: %s" % (dt, syn))
    # a failing write keeps retrying (after 30 tries every 30 s) and its pending mark stays, so the shutdown flush still writes it
    STPE = JClass("java.util.concurrent.ScheduledThreadPoolExecutor")(1)
    EIO.stop()
    EIO.STOPPING = False
    EIO.EXEC = STPE
    blk = os.path.join(d, "blocked")
    open(blk, "w").write("a file where the folder should be")
    Sto.DIR = Paths.get(blk)
    Sto.put(KA, wf, *C2, t0, '{"s": []}')
    STPE.getQueue().clear()
    JClass(PKG + "PcJob")(JString(KA), JString(wf), None, 0, 30).run()
    q = list(STPE.getQueue())
    dl_ = int(q[0].getDelay(JClass("java.util.concurrent.TimeUnit").SECONDS)) if len(q) == 1 else -1
    K.check(len(q) == 1 and 25 <= dl_ <= 30 and Sto.PEND.get(fkA) is not None, "PC write retry (fix): after 30 failed tries the write is tried again in 30 s, the pending mark stays (%d queued, %d s)" % (len(q), dl_))
    STPE.shutdownNow()
    Sto.DIR = Paths.get(os.path.join(d, "chestloot"))
    EIO.EXEC = Executors.newSingleThreadScheduledExecutor()
    K.check(int(Sto.flushAll()) >= 1 and '\nC 20 64 20 %d {"s": []}' % t0 in open(fA, encoding="utf8").read(), "PC write retry (fix): once the disk works the flush writes the waiting record")
    # chest-luck gear on a per-profile open -> a mystery bag at the chest's level (ExpAward.luckStack via PcBagFn), other items unchanged
    Awd = JClass(PKG + "ExpAward")
    Awd.PCBAG = JClass(PKG + "PcBagFn")()
    sw = IS(JString("Weapon_Sword_Iron"), JInt(1))
    a0 = Awd.luckStack(sw, u1)
    Awd.PCLV.set(Integer.valueOf(17))
    a1, a2, a3 = Awd.luckStack(sw, u1), Awd.luckStack(IS(JString("Ingredient_Stick"), JInt(2)), u1), Awd.luckStack(stamped, u1)
    Awd.PCLV.remove()
    K.check(str(a0.getItemId()) == "Weapon_Sword_Iron" and str(a1.getItemId()) == "Skyy_Unid_Test" and GEARCALLS[-1][:2] == ("Weapon_Sword_Iron", 17)
            and str(a2.getItemId()) == "Ingredient_Stick" and str(a3.getItemId()) == "Armor_Iron_Chest",
            "PC chest luck (fix): gear -> a bag at the chest's level only during a per-profile open; sticks / stamped gear unchanged")
    # the break / damage guards return at once for blocks without a block entity (handle() needs a live server: class bytes checked)
    import zipfile as _zf
    zb = _zf.ZipFile(jar)
    K.check(all(b"getBlockEntity" in zb.read("com/skyy/explore/%s.class" % c_) and b"getBlockType" in zb.read("com/skyy/explore/%s.class" % c_) for c_ in ("PcBreakSys", "PcDmgSys")),
            "PC break / damage guards (fix): getBlockType().getBlockEntity() checked first (class bytes)")

    # ---------------- a bad file / an unreadable record
    KEY[str(u3)] = str(u3)
    fb = os.path.join(d, "chestloot", str(u3), wf + ".txt")
    os.makedirs(os.path.dirname(fb), exist_ok=True)
    open(fb, "wb").write(b"# hand edit\nC 10 64 ten 0 {}\n")
    r = str(Core.open(None, u3, W1, "w1", wf, *C1, t0 + 80000))
    K.check(r == "bad file" and not bool(Sto.loaded(str(u3), wf)), "PC bad file: the open is refused (nothing rolled over an unreadable file)")
    Sto.loadSoon(str(u3), wf, "w1")
    settle()
    K.check(open(fb, "rb").read() == b"# hand edit\nC 10 64 ten 0 {}\n", "PC bad file: never written over, the tick does not retry it")
    Sto.put(KA, wf, *C2, t0, '{"s": [{"slot": 99, "id": "Ingredient_Stick", "qty": 1}]}')
    K.eq(str(Core.open(None, u1, W1, "w1", wf, *C2, t0 + 90000)), "unreadable record", "PC unreadable record: refused, the record stays as it is")
    K.check(str(Sto.get(KA, wf, *C2)[1]).startswith('{"s": [{"slot": 99'), "PC unreadable record: untouched")
    settle()
    K.save(notes=["rolls %d, shared stacks taken out %d, statusText: %s" % (ST["rolls"], ST["cleared"], str(Core.statusText()))])


def run_live(out, jar, scratch, home):
    from jpype import JClass, JString, JInt, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar])
    U = engine(scratch)
    Paths, Executors, UUID = JClass("java.nio.file.Paths"), JClass("java.util.concurrent.Executors"), JClass("java.util.UUID")
    IS, ArrayList = JClass("com.hypixel.hytale.server.core.inventory.ItemStack"), JClass("java.util.ArrayList")
    Cfg, Reg, EIO = JClass(PKG + "ExpCfg"), JClass(PKG + "ChestReg"), JClass(PKG + "ExpIO")
    Core, Sto = JClass(PKG + "PcCore"), JClass(PKG + "PcStore")
    Lg, Nc = JClass(PKG + "ExpLgMig"), JClass(PKG + "ExpNcMig")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyExpTest")
    h0 = HK.tree_hash(home)
    CFG0 = open(os.path.join(home, "config.properties"), "rb").read()
    pd = os.path.join(home, "players")
    keys = sorted(n[:-11] for n in os.listdir(pd) if n.endswith(".properties")) if os.path.isdir(pd) else []
    K.check(len(keys) > 0, "LIVE: the copy has profile records (%d)" % len(keys))
    KEY = {}

    @JImplements("java.util.function.Function")
    class KeyFn:
        @JOverride
        def apply(self, u):
            return KEY.get(str(u), str(u))
    EIO.bridge().put("profile:fn:key", KeyFn())

    @JImplements(PKG + "PcApi")
    class Api:
        @JOverride
        def cap(self, w, x, y, z): return 27

        @JOverride
        def takeShared(self, w, x, y, z): return ArrayList()

        @JOverride
        def placedBy(self, w, x, y, z): return None

        @JOverride
        def roll(self, dl):
            l = ArrayList()
            l.add(IS(JString("Ingredient_Stick"), JInt(3)))
            l.add(IS(JString("Rock_Gem_Ruby"), JInt(1)))
            return l

        @JOverride
        def open(self, u, w, x, y, z, box):
            OPENED.append(box)
            return True

        @JOverride
        def live(self, u, box): return False

        @JOverride
        def close(self, u, box): pass

        @JOverride
        def spark(self, u, x, y, z): pass
    OPENED = []
    Core.API = Api()
    pick = None
    for start in (1, 2):
        before = HK.tree_hash(home)
        Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
        Lg.migrate()
        Nc.migrate()
        Cfg.load()
        Reg.W.clear()
        Reg.DIR = Paths.get(os.path.join(home, "chests"))
        n = int(Reg.loadAll())
        Sto.M.clear()
        Sto.DIR = Paths.get(os.path.join(home, "chestloot"))
        EIO.STOPPING = False
        EIO.EXEC = Executors.newSingleThreadScheduledExecutor()
        now_h = HK.tree_hash(home)
        changed = sorted(k_ for k_ in before if now_h.get(k_) != before[k_])
        if start == 1:
            # the live copy has not run 0.2.15 yet (its ExpNcMig one-time update is 0.2.15's own first start): config.properties may change
            # exactly as 0.2.15's text step says, plus the kit's history / change-log files - nothing else
            want = str(Nc.update(JString(CFG0.decode("latin-1")))[0]) if Nc.update(JString(CFG0.decode("latin-1"))) is not None else CFG0.decode("latin-1")
            cfg1 = open(os.path.join(home, "config.properties"), "rb").read().decode("latin-1")
            K.check(all(c_ in ("config.properties", "config-changes.log") or c_.startswith("config-history") for c_ in changed) and cfg1 == want,
                    "LIVE start 1: only 0.2.15's own one-time config update ran (config.properties = ExpNcMig's text step; history / change log): %s" % changed)
        else:
            K.check(not changed, "LIVE start 2: loading changes no existing file (%s)" % changed[:5])
        K.check(n > 0 and bool(Cfg.PC_ON) and int(Cfg.PC_REFILL_S) == 0 and bool(Cfg.PC_SPARK), "LIVE start %d: %d live loot chests in the registry, the 0.3.0 defaults (no lines in the live file)" % (start, n))
        if pick is None:
            for wf_ in Reg.W.keySet():
                m = Reg.W.get(wf_)
                for k_ in m.keySet():
                    if str(m.get(k_)).endswith("|-"):
                        pick = (str(wf_), str(Reg.NAMES.get(wf_)), int(JClass(PKG + "ExpDefs").unX(k_)), int(JClass(PKG + "ExpDefs").unY(k_)), int(JClass(PKG + "ExpDefs").unZ(k_)))
                        break
                if pick:
                    break
        K.check(pick is not None, "LIVE: a real world loot chest in the copy: %s" % (pick,))
        pk = keys[0]
        u = UUID.fromString(pk[:36])
        KEY[str(u)] = pk
        w = world(U, pick[1])
        r = str(Core.open(None, u, w, pick[1], pick[0], pick[2], pick[3], pick[4], 1000 + start))
        K.eq(r, "rolled 2" if start == 1 else "reopened", "LIVE start %d: a real live chest for live profile %s" % (start, pk))
        if start == 1:
            box = OPENED[-1]
            box.moveItemStackFromSlot(JClass("java.lang.Short")(next(s for s in range(27) if box.getItemStack(s) is not None and not box.getItemStack(s).isEmpty())), JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")(JClass("java.lang.Short")(9)))
            first = sorted(str(box.getItemStack(s).getItemId()) for s in range(27) if box.getItemStack(s) is not None and not box.getItemStack(s).isEmpty())
        else:
            again = sorted(str(OPENED[-1].getItemStack(s).getItemId()) for s in range(27) if OPENED[-1].getItemStack(s) is not None and not OPENED[-1].getItemStack(s).isEmpty())
            K.check(again == first and len(first) == 1, "LIVE start 2: the copy read back from chestloot/ = the leftovers after the take (%s)" % again)
        Core.closedBox(OPENED[-1])
        EIO.stop()
        Sto.flushAll()
        f = os.path.join(home, "chestloot", pk, pick[0] + ".txt")
        K.check(os.path.isfile(f), "LIVE start %d: chestloot/%s/%s.txt written" % (start, pk, pick[0]))
    h1 = HK.tree_hash(home)
    diff = sorted(k_ for k_ in set(h0) | set(h1) if h0.get(k_) != h1.get(k_) and not k_.replace("\\", "/").startswith(("chestloot/", "config-history/"))
                  and k_ not in ("config.properties", "config-changes.log"))
    K.check(not diff, "LIVE: every other pre-existing file byte-identical after two starts (players, chests, luggage, worlds; only chestloot/ is new): %s" % diff[:8])
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyExploration", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("pc", run_pc), ("live", run_live)], script=__file__, live=(LIVE, "Skyy_SkyyExploration"))
