"""Harness for SkyySacks 0.8.4 (AUTO-PICKUP follow-ups: pet kills -> owner, F-harvest -> Void first; tools/sacks_0_8_4_patch.py) + its
pair SkyyMobs 0.1.8. Every 0.8.3 no-dupe proof below is kept unchanged; the 0.8.4 sections PET and HARV are added.
Build first: python tools/sacks_0_8_4_patch.py && python SkyySacks/build_skyysacks_0.8.4.py   (+ tools/mobs_0_1_8_patch.py + its build)

    python SkyySacks/test_skyysacks_0.8.4.py [--keep] [--dir <scratch>]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.8.3 -> 0.8.4: exactly PickBook (+ petOwner, + HARV_OK / DROP_OK, ~ state / stats), PickDeathMark (~ killer), the
              plugin (~ setup, ~ shutdown) and the config kit's version text differ; PickHarv, PickHarvTask, PickHarvSys, PickDropSys
              are new; non-class files: manifest only
  X  exec     EXECUTED on the compiled classes in a REAL engine Store (EntityStore.REGISTRY, real Refs, real CommandBuffers, real
              ItemComponent / TransformComponent, the real Store.addEntity -> RefSystem -> CommandBuffer.consume path; the killer's
              share spawns through the PickBook.SPAWN seam = generateItemDrop's ItemComponent + TransformComponent at the given
              position, because the real call needs the world's GameplayConfig asset, which a bare JVM cannot load) with the real
              SkyyMobs 0.1.7 MobCredit as mob:fn:credit:
              SPLIT  PickGive.split on a real SimpleItemContainer + the real Void pool: Void room > / < / = 0, inventory full, both full,
                     a non-Void item, a stack with metadata, no settled profile, faults 1 + 2 (rolled back) - every case conserves
              BLOCK  PickBreakSys.handle claims block + (0.5, 0, 0.5); the item spawned there is delivered INSIDE the add (gone from the
                     store, never ticked): Void first, inventory next, both full -> the SAME entity moved to the player's feet with every
                     item; partial; a cancelled break, a PickupItemComponent animation, a LOAD, an unclaimed spot, an expired claim, another
                     world, pickup.blocks / pickup.on off -> untouched; felled logs (skill:fn:felledBy); island:perm:fn FALSE -> stays;
                     fault 3 (entity update) -> rolled back; a converter RefSystem registered BEFORE and one AFTER ours (SkyyGear's
                     GearDropSys pattern) -> the converted stack is what arrives; feed card / msgroute off / chat routes
              MOB    PickDeathMark.tick + PickShareSys.tick on real dying NPC chunks (DeathComponent with the killer's Damage, NPCEntity +
                     Role): top damager (real MobCredit hits, overkill capped) gets the whole drop + the drop that arrived BEFORE the mark
                     (the ring); the killer gets the share roll (50 % of the stand-in roll), spawned by the real generateItemDrops and
                     converted by the converter; same player = no share; no credit -> killer; top in another world -> killer; nobody ->
                     vanilla; pickup.mobs off; share 0; the condition (instant / corpse timer / already dropped / not ALL)
              CFG    pickKeys with and without the new keys (the live file: phase D)
              SAVED  after a delivery + the writer: a restart reloads the Void with the items and no item entity is left (exactly once)
              PET    (0.8.4) a mob killed by a pet (pets:fn:ownerOf stand-in): owner here -> the owner gets the drop; pet + owner credit
                     (SkyyMobs 0.1.8 MobCredit) = one player, no share; another player top + pet kill -> top gets the drop, the OWNER
                     the share roll; owner OFFLINE / in ANOTHER WORLD / no key / junk key -> the drop stays (vanilla), nobody gains
              HARV   (0.8.4) the engine's interactivelyPickupItem replayed step by step (InteractivelyPickupItemEvent -> PickHarvSys,
                     giveItem into the pickup container, the remainder -> DropItemEvent$Drop -> PickDropSys, then the queued
                     PickHarvTask): Void room / part / FULL; inventory full + Void room / part / full (throw cancelled / shrunk /
                     untouched); several stacks in one tick; a later listener cancels; existing stacks of the item untouched; a
                     non-Void item; faults 4 / 5 / 6 rolled back; paused profile; pickup.blocks off; a Q-drop with no window / an expired
                     window / another item; island rules on the overflow; the event (stack + cancelled flag) never changed
              Every case checks the exact Void / inventory / item-entity counts (nothing lost, nothing doubled).
  D  live     a scratch COPY of the live Skyy_SkyySacks: every pool loads with 0.8.2 and 0.8.3 into the same map, twice; the live
              config.properties loads with 0.8.3 (auto-pickup defaults: on / on / on / 50) and stays byte-identical
  AA engine-access audit
Scratch: tools/dev/scratch/pickup2/sacks (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, shutil, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.8.4"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-0.8.3.jar")
MOBS_JAR = os.path.abspath(HK.arg("--mobs", os.path.join(ROOT, "SkyyMobs", "SkyyMobs-0.1.8.jar")))
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "pickup2", "sacks")))
PKG = "com.skyy.sacks."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyySacks")
EXPECT = {
    "PickBook": ["+f HARV_OK", "+f DROP_OK", "+m petOwner", "~<clinit>", "~m state", "~m stats"],
    "PickDeathMark": ["~m killer"],
    "SkyySacksPlugin": ["~m setup", "~m shutdown"],
    "CfgFn": ["~m opExport"],          # the kit's version text
    "CfgRows": ["~<clinit>", "~m header"],   # fix round: the pickup.blocks help text (row table) + the version text
}
ADDED = ["PickHarv", "PickHarvTask", "PickHarvSys", "PickDropSys"]


def sha(p):
    return hashlib.sha1(open(p, "rb").read()).hexdigest() if os.path.isfile(p) else None


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JShort, JString, JFloat, JImplements, JOverride, JArray, JInt, JLong
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, MOBS_JAR, B.JAVASSIST], verify=True)
    J = lambda n: JClass(PKG + n)
    Pool, VS, Cfg, CLog, PStore, Book, Give, Ring = (J("SackPool"), J("VoidStore"), J("SackCfg"), J("CraftLog"), J("ProcStore"),
                                                     J("PickBook"), J("PickGive"), J("PickRing"))
    ItemSys, BreakSys, DeathMark, ShareSys, Deliver = J("PickItemSys"), J("PickBreakSys"), J("PickDeathMark"), J("PickShareSys"), J("PickDeliver")
    Harv, HarvSys, DropSys = J("PickHarv"), J("PickHarvSys"), J("PickDropSys")     # 0.8.4
    MCredit, MCreditFn = JClass("com.skyy.mobs.MobCredit"), JClass("com.skyy.mobs.MobCreditFn")
    UUID, Paths, Long_, System = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Long"), JClass("java.lang.System")
    Boolean_ = JClass("java.lang.Boolean")
    bridge = JClass("java.util.concurrent.ConcurrentHashMap")()
    System.getProperties().put("skyy.bridge", bridge)
    Pool.WRITER = JClass("java.util.concurrent.Executors").newSingleThreadScheduledExecutor()
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)

    def jfield(cls, name):
        c = cls
        while c is not None:
            try:
                f_ = c.getDeclaredField(name)
                f_.setAccessible(True)
                return f_
            except Exception:
                c = c.getSuperclass()
        raise KeyError(name)

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, o):
            return self.f(o)

    @JImplements("java.util.function.Supplier")
    class Sup(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def get(self):
            return self.f()

    # ------------------------------------------------------------------ Void pool on scratch (the 0.8.2 harness's fresh())
    TOT = {}
    bridge.put("coll:fn:catTotal", Fn(lambda o: None if TOT.get(str(o[0]) + "|" + str(o[1])) is None else Long_(TOT[str(o[0]) + "|" + str(o[1])])))
    base = os.path.join(scratch, "x")
    if os.path.exists(base):
        shutil.rmtree(base)
    os.makedirs(os.path.join(base, "pools"))
    Pool.DIR = Paths.get(os.path.join(base, "pools"))
    PStore.DIR = Paths.get(os.path.join(base, "processing"))
    VS.DIR = Paths.get(os.path.join(base, "pd"))
    VS.HDIR = Paths.get(os.path.join(base, "history"))
    VS.MIGLOG = Paths.get(os.path.join(base, "migration.log"))
    CLog.FILE = Paths.get(os.path.join(base, "crafts.log"))

    def pc(k):
        return dict((str(e.getKey()), int(e.getValue().longValue())) for e in Pool.pool(k).entrySet())

    # ------------------------------------------------------------------ the item asset store (the 0.8.2 harness's fake store)
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    jp.appendClassPath(jar)
    CtF, CtM, CtC = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyTestFakeStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fake.addConstructor(CtC.make("public SkyyTestFakeStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
    astore = us.allocateInstance(fake.toClass(AS.class_))
    fm = AS.class_.getDeclaredField("assetMap")
    fm.setAccessible(True)
    DAMN = "com.hypixel.hytale.assetstore.map.DefaultAssetMap"
    kmap = jp.makeClass("com.hypixel.hytale.assetstore.map.SkyyTestKnownMap", jp.get(DAMN))
    kmap.addField(CtF.make("public static final java.util.HashMap CUSTOM = new java.util.HashMap();", kmap))
    kmap.addConstructor(CtC.make("public SkyyTestKnownMap() { super(); }", kmap))
    kmap.addMethod(CtM.make("public com.hypixel.hytale.assetstore.JsonAsset getAsset(Object key) { if (key != null && CUSTOM.containsKey(key)) "
                            "return (com.hypixel.hytale.assetstore.JsonAsset) CUSTOM.get(key); return super.getAsset(key); }", kmap))
    KMap = JClass(kmap.toClass(JClass(DAMN).class_))
    fm.set(astore, KMap())
    ItemC = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    fi_ = ItemC.class_.getDeclaredField("ASSET_STORE")
    fi_.setAccessible(True)
    fi_.set(None, astore)
    IEC = JClass("com.hypixel.hytale.server.core.asset.type.item.config.ItemEntityConfig")
    iec = us.allocateInstance(IEC.class_)
    jfield(IEC.class_, "ttl").set(iec, JClass("java.lang.Float")(120.0))
    IDS = {"Rock_Stone_Cobble": 100, "Ore_Copper": 100, "Plant_Crop_Wheat_Item": 100, "Weapon_Sword_Iron": 1, "Skyy_Unid_Sword": 1,
           "Food_Bread": 25}
    for iid, mx in IDS.items():
        it_ = ItemC(JString(iid))
        jfield(ItemC.class_, "maxStack").setInt(it_, mx)
        try:
            jfield(ItemC.class_, "itemEntityConfig").set(it_, iec)
        except KeyError:
            pass
        KMap.CUSTOM.put(JString(iid), it_)
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")

    def cnt(c):
        o = {}
        if c is None:
            return o
        for i in range(int(c.getCapacity())):
            it_ = c.getItemStack(JShort(i))
            if it_ is not None and not it_.isEmpty():
                o[str(it_.getItemId())] = o.get(str(it_.getItemId()), 0) + int(it_.getQuantity())
        return o

    def fill(c, iid="Food_Bread"):
        """fill every slot of c with full stacks of a non-Void item"""
        for i in range(int(c.getCapacity())):
            c.addItemStack(IS(iid, IDS[iid]))

    add = lambda a, b: dict((x, a.get(x, 0) + b.get(x, 0)) for x in set(a) | set(b) if a.get(x, 0) + b.get(x, 0))

    # ------------------------------------------------------------------ SPLIT (pure Void / inventory core)
    U1 = UUID.fromString("00000000-0000-0000-0000-0000000b0001")
    k1 = str(U1)
    TOT[k1 + "|Mining"] = 0          # Mining Lv 1, Normal = 100 items of space
    Pool.pool(k1)
    space = int(VS.capsK(U1, k1).get("Mining"))
    K.eq(space, 100, "SPLIT: Mining Lv 1 Normal = 100 items of space")
    inv = SIC(JShort(9))
    r = Give.split(U1, k1, IS("Rock_Stone_Cobble", 30), inv)
    K.eq(([int(x) for x in r], pc(k1), cnt(inv)), ([30, 0, 0], {"Rock_Stone_Cobble": 30}, {}), "SPLIT: room > stack -> all into the Void")
    Pool.add(k1, "Rock_Stone_Cobble", Long_(60))      # 90 stored, 10 room
    r = Give.split(U1, k1, IS("Rock_Stone_Cobble", 25), inv)
    K.eq(([int(x) for x in r], pc(k1).get("Rock_Stone_Cobble"), cnt(inv)), ([10, 15, 0], 100, {"Rock_Stone_Cobble": 15}),
         "SPLIT: 10 room -> 10 Void, 15 inventory")
    r = Give.split(U1, k1, IS("Ore_Copper", 7), inv)
    K.eq(([int(x) for x in r], cnt(inv).get("Ore_Copper")), ([0, 7, 0], 7), "SPLIT: Void full (Mining 100/100) -> all to the inventory")
    full = SIC(JShort(2))
    fill(full)
    r = Give.split(U1, k1, IS("Ore_Copper", 7), full)
    K.eq(([int(x) for x in r], pc(k1).get("Ore_Copper", 0), cnt(full)), ([0, 0, 7], 0, {"Food_Bread": 50}), "SPLIT: both full -> 7 left over, nothing moved")
    part = SIC(JShort(2))
    part.addItemStack(IS("Food_Bread", 25))
    part.addItemStack(IS("Ore_Copper", 95))
    r = Give.split(U1, k1, IS("Ore_Copper", 9), part)
    K.eq(([int(x) for x in r], cnt(part)), ([0, 5, 4], {"Food_Bread": 25, "Ore_Copper": 100}), "SPLIT: 5 fit the last stack, 4 left over")
    r = Give.split(U1, k1, IS("Weapon_Sword_Iron", 1), inv)
    K.eq(([int(x) for x in r], cnt(inv).get("Weapon_Sword_Iron")), ([0, 1, 0], 1), "SPLIT: a non-Void item -> inventory")
    BD = JClass("org.bson.BsonDocument")
    md = BD()
    md.put("x", JClass("org.bson.BsonString")("y"))
    mstack = IS("Plant_Crop_Wheat_Item", 3).withMetadata(md) if hasattr(IS("Plant_Crop_Wheat_Item", 3), "withMetadata") else None
    if mstack is not None:
        before = pc(k1)
        r = Give.split(U1, k1, mstack, inv)
        K.eq(([int(x) for x in r], pc(k1)), ([0, 3, 0], before), "SPLIT: a stack with metadata never goes into the Void")
    else:
        K.notes.append("SPLIT: ItemStack.withMetadata not found - metadata case not run")
    r = Give.split(U1, None, IS("Plant_Crop_Wheat_Item", 4), inv)
    K.eq([int(x) for x in r], [0, 4, 0], "SPLIT: no settled profile key -> inventory only")
    for f, what in ((1, "after the Void booking"), (2, "after the inventory add")):
        Pool.add(k1, "Rock_Stone_Cobble", Long_(-50))          # 50 room again
        p0, i0 = pc(k1), cnt(inv)
        Give.FAULT = f
        r = Give.split(U1, k1, IS("Rock_Stone_Cobble", 70), inv)
        Give.FAULT = 0
        K.check(r is None and pc(k1) == p0 and cnt(inv) == i0, "SPLIT: fault %d (%s) -> null, Void %s and inventory %s unchanged (got %s / %s)"
                % (f, what, p0, i0, pc(k1), cnt(inv)))

    # ------------------------------------------------------------------ the REAL Store fixture
    ES = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    ERS, AR, RR = JClass("com.hypixel.hytale.component.EmptyResourceStorage"), JClass("com.hypixel.hytale.component.AddReason"), JClass("com.hypixel.hytale.component.RemoveReason")
    TC = JClass("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
    ITC = JClass("com.hypixel.hytale.server.core.modules.entity.item.ItemComponent")
    PIC = JClass("com.hypixel.hytale.server.core.modules.entity.item.PickupItemComponent")
    UUIDC = JClass("com.hypixel.hytale.server.core.entity.UUIDComponent")
    PRF = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    NPCE = JClass("com.hypixel.hytale.server.npc.entities.NPCEntity")
    ROLE = JClass("com.hypixel.hytale.server.npc.role.Role")
    DTHC = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent")
    DCR = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DeferredCorpseRemoval")
    DMG = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage")
    DENT = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource")
    ILM = JClass("com.hypixel.hytale.server.core.asset.type.gameplay.DeathConfig$ItemsLossMode")
    VEL = JClass("com.hypixel.hytale.server.core.modules.physics.component.Velocity")
    PHV = JClass("com.hypixel.hytale.server.core.modules.physics.component.PhysicsValues")
    INTC = JClass("com.hypixel.hytale.server.core.modules.entity.component.Intangible")
    DESC = JClass("com.hypixel.hytale.server.core.modules.entity.DespawnComponent")
    TRC = JClass("com.hypixel.hytale.server.core.modules.time.TimeResource")
    BBE = JClass("com.hypixel.hytale.server.core.event.events.ecs.BreakBlockEvent")
    V3, V3I = JClass("org.joml.Vector3d"), JClass("org.joml.Vector3i")
    EMc, TMc, DMc, UNc = (JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule"), JClass("com.hypixel.hytale.server.core.modules.time.TimeModule"),
                          JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageModule"), JClass("com.hypixel.hytale.server.core.universe.Universe"))
    WLDc = JClass("com.hypixel.hytale.server.core.universe.world.World")
    REG = ES.REGISTRY
    T_TC = REG.registerComponent(TC, "Transform", TC.CODEC)
    T_ITC = REG.registerComponent(ITC, Sup(lambda: ITC()))
    T_PIC = REG.registerComponent(PIC, Sup(lambda: None))
    T_UU = REG.registerComponent(UUIDC, Sup(lambda: None))
    T_PR = REG.registerComponent(PRF, Sup(lambda: None))
    T_PLA = REG.registerComponent(PLA, Sup(lambda: None))
    T_NPC = REG.registerComponent(NPCE, Sup(lambda: None))
    T_DTH = REG.registerComponent(DTHC, Sup(lambda: None))
    T_DCR = REG.registerComponent(DCR, Sup(lambda: None))
    T_VEL = REG.registerComponent(VEL, Sup(lambda: VEL()))
    T_PHV = REG.registerComponent(PHV, Sup(lambda: None))
    T_INT = REG.registerComponent(INTC, "Intangible", INTC.CODEC)
    T_DES = REG.registerComponent(DESC, "Despawn", DESC.CODEC)
    R_TIME = REG.registerResource(TRC, "Time", TRC.CODEC)
    em = us.allocateInstance(EMc.class_)
    for name_, v_ in (("transformComponentType", T_TC), ("itemComponentType", T_ITC), ("pickupItemComponentType", T_PIC),
                      ("uuidComponentType", T_UU), ("playerComponentType", T_PLA), ("velocityComponentType", T_VEL),
                      ("physicsValuesComponentType", T_PHV), ("intangibleComponentType", T_INT), ("despawnComponentComponentType", T_DES)):
        try:
            jfield(EMc.class_, name_).set(em, v_)
        except KeyError:
            K.notes.append("fixture: EntityModule has no field %s" % name_)
    ctm = JClass("java.util.HashMap")()
    ctm.put(NPCE.class_, T_NPC)
    jfield(EMc.class_, "classToComponentType").set(em, ctm)
    jfield(EMc.class_, "instance").set(None, em)
    tm = us.allocateInstance(TMc.class_)
    jfield(TMc.class_, "timeResourceType").set(tm, R_TIME)
    jfield(TMc.class_, "instance").set(None, tm)
    dm = us.allocateInstance(DMc.class_)
    jfield(DMc.class_, "deathComponentType").set(dm, T_DTH)
    jfield(DMc.class_, "deferredCorpseRemovalComponentType").set(dm, T_DCR)
    jfield(DMc.class_, "instance").set(None, dm)
    un = us.allocateInstance(UNc.class_)
    jfield(UNc.class_, "playerRefComponentType").set(un, T_PR)
    jfield(UNc.class_, "instance").set(None, un)
    # the converter RefSystems (SkyyGear GearDropSys pattern: setItemStack inside onEntityAdded) - one before ours, one after
    RS = "com.hypixel.hytale.component.system.RefSystem"
    conv = {}
    for nm in ("SkyyHkConvA", "SkyyHkConvB"):
        cc = jp.makeClass("com.hypixel.hytale.component.system." + nm, jp.get(RS))
        cc.addField(CtF.make("public static boolean ON = false;", cc))
        cc.addField(CtF.make("public static int SEEN = 0;", cc))
        cc.addConstructor(CtC.make("public %s() { super(); }" % nm, cc))
        cc.addMethod(CtM.make("public com.hypixel.hytale.component.query.Query getQuery() { return (com.hypixel.hytale.component.query.Query) "
                              "com.hypixel.hytale.server.core.modules.entity.item.ItemComponent.getComponentType(); }", cc))
        cc.addMethod(CtM.make(
            "public void onEntityAdded(com.hypixel.hytale.component.Ref ref, com.hypixel.hytale.component.AddReason r, com.hypixel.hytale.component.Store st, "
            "com.hypixel.hytale.component.CommandBuffer cb) { SEEN++; if (!ON) return; "
            "com.hypixel.hytale.server.core.modules.entity.item.ItemComponent ic = (com.hypixel.hytale.server.core.modules.entity.item.ItemComponent) "
            "st.getComponent(ref, com.hypixel.hytale.server.core.modules.entity.item.ItemComponent.getComponentType()); "
            "if (ic != null && \"Weapon_Sword_Iron\".equals(ic.getItemStack().getItemId())) "
            "ic.setItemStack(new com.hypixel.hytale.server.core.inventory.ItemStack(\"Skyy_Unid_Sword\", 1)); }", cc))
        cc.addMethod(CtM.make("public void onEntityRemove(com.hypixel.hytale.component.Ref ref, com.hypixel.hytale.component.RemoveReason r, "
                              "com.hypixel.hytale.component.Store st, com.hypixel.hytale.component.CommandBuffer cb) { }", cc))
        conv[nm] = JClass(cc.toClass(JClass(RS).class_))
    # a system AFTER ours that queues an operation on the new item's ref (a component put) - it must run before our removal
    cc = jp.makeClass("com.hypixel.hytale.component.system.SkyyHkPutC", jp.get(RS))
    cc.addField(CtF.make("public static boolean ON = false;", cc))
    cc.addField(CtF.make("public static com.hypixel.hytale.component.ComponentType T = null;", cc))
    cc.addConstructor(CtC.make("public SkyyHkPutC() { super(); }", cc))
    cc.addMethod(CtM.make("public com.hypixel.hytale.component.query.Query getQuery() { return (com.hypixel.hytale.component.query.Query) "
                          "com.hypixel.hytale.server.core.modules.entity.item.ItemComponent.getComponentType(); }", cc))
    cc.addMethod(CtM.make(
        "public void onEntityAdded(com.hypixel.hytale.component.Ref ref, com.hypixel.hytale.component.AddReason r, com.hypixel.hytale.component.Store st, "
        "com.hypixel.hytale.component.CommandBuffer cb) { if (ON) cb.putComponent(ref, T, new com.hypixel.hytale.server.core.modules.physics.component.Velocity()); }", cc))
    cc.addMethod(CtM.make("public void onEntityRemove(com.hypixel.hytale.component.Ref ref, com.hypixel.hytale.component.RemoveReason r, "
                          "com.hypixel.hytale.component.Store st, com.hypixel.hytale.component.CommandBuffer cb) { }", cc))
    PutC = JClass(cc.toClass(JClass(RS).class_))
    PutC.T = T_VEL
    REG.registerSystem(conv["SkyyHkConvA"]())
    REG.registerSystem(ItemSys())
    Book.ITEM_OK = True     # the plugin sets it after this register (review fix 2 gates the claims on it)
    REG.registerSystem(conv["SkyyHkConvB"]())
    REG.registerSystem(PutC())

    def world(name):
        w_ = us.allocateInstance(WLDc.class_)
        jfield(WLDc.class_, "name").set(w_, JString(name))
        return w_
    st = REG.addStore(ES(world("skyytest")), ERS.get())
    st2 = REG.addStore(ES(world("other")), ERS.get())
    K.eq(str(Book.world(st.getExternalData())), "skyytest", "fixture: PickBook.world names the store's world")

    def ent(store, pos, comps):
        h = REG.newHolder()
        t_ = TC()
        t_.setPosition(V3(*pos))
        h.addComponent(T_TC, t_)
        for ty, c in comps:
            h.addComponent(ty, c)
        return h

    PLAYERS, INVS = {}, {}

    def player(store, name, pos, slots=9):
        u = UUID.nameUUIDFromBytes(("pick-" + name).encode())
        r_ = store.addEntity(ent(store, pos, [(T_PR, PRF(None, u, name, "en-US", None, None)), (T_UU, UUIDC(u)), (T_PLA, us.allocateInstance(PLA.class_))]), AR.SPAWN)
        PLAYERS[str(u)] = r_
        INVS[str(r_)] = SIC(JShort(slots))
        Pool.pool(str(u))
        return u, r_
    Book.PLAYERS = Fn(lambda u: PLAYERS.get(str(u)))
    Book.INVS = Fn(lambda r_: INVS.get(str(r_)))
    inv_of = lambda r_: INVS[str(r_)]

    def items(store):
        """every item entity still in the store: (id, qty, x, y, z)"""
        out_ = []

        @JImplements("java.util.function.BiConsumer")
        class C(object):
            @JOverride
            def accept(self, chunk, cb):
                for i_ in range(int(chunk.size())):
                    ic = chunk.getComponent(i_, T_ITC)
                    p_ = chunk.getComponent(i_, T_TC).getPosition()
                    out_.append((str(ic.getItemStack().getItemId()), int(ic.getItemStack().getQuantity()), float(p_.x()), float(p_.y()), float(p_.z())))
        store.forEachChunk(ItemSys().getQuery(), C())
        return sorted(out_)

    gone = lambda r_: r_ is None or not r_.isValid()
    alive = lambda r_: r_ is not None and bool(r_.isValid())

    def drop(store, iid, q, pos, reason=None, pickup=False):
        comps = [(T_ITC, ITC(IS(iid, q)))]
        if pickup:
            comps.append((T_PIC, us.allocateInstance(PIC.class_)))
        return store.addEntity(ent(store, pos, comps), reason or AR.SPAWN)

    CARDS = []
    ROUTE = {"v": "feed"}
    bridge.put("feed:fn:push", Fn(lambda o: (CARDS.append((str(o[0]), str(o[1]), str(o[2]), str(o[3]), int(o[4].longValue()))), Boolean_.TRUE)[1]))
    bridge.put("msgroute:fn:get", Fn(lambda o: JString(ROUTE["v"])))

    def chunk_of(store, ref, query):
        """run f(chunk, idx, cb) for the chunk holding ref (the system's own iteration, real CommandBuffer consumed after)"""
        hold = []

        @JImplements("java.util.function.BiConsumer")
        class C(object):
            def __init__(self, f):
                self.f = f

            @JOverride
            def accept(self, chunk, cb):
                for i_ in range(int(chunk.size())):
                    if chunk.getReferenceTo(i_).equals(ref):
                        self.f(chunk, i_, cb)
        return C

    def break_block(store, pref, b, cancel=False):
        ev = BBE(None, V3I(*b), None)
        if cancel:
            ev.setCancelled(True)
        sysb = BreakSys()

        def f(chunk, i_, cb):
            sysb.handle(JInt(i_), chunk, store, cb, ev)
        store.forEachChunk(sysb.getQuery(), chunk_of(store, pref, None)(f))

    # ------------------------------------------------------------------ BLOCK
    UA, RA = player(st, "Ava", (10.5, 64.0, 10.5))
    kA = str(UA)
    TOT[kA + "|Mining"] = 0
    p0 = pc(kA)
    break_block(st, RA, (3, 70, -4))
    ref = drop(st, "Rock_Stone_Cobble", 12, (3.5, 70.0, -3.5))
    K.check(gone(ref) and items(st) == [], "BLOCK: the drop at the broken block is gone from the store inside the add (valid=%s, left %s)"
            % (alive(ref), items(st)))
    K.eq((pc(kA), cnt(inv_of(RA))), ({"Rock_Stone_Cobble": 12}, {}), "BLOCK: Void first (Mining has room)")
    K.check(CARDS and CARDS[-1][:3] == (str(UA), "pickup", "Rock_Stone_Cobble") and CARDS[-1][3].endswith("> Void") and CARDS[-1][4] == 12,
            "BLOCK: one feed card, kind pickup, item id, '... > Void', count 12: %s" % (CARDS[-1:],))
    # Void nearly full -> inventory; then both full -> the same entity at the player's feet
    Pool.add(kA, "Rock_Stone_Cobble", Long_(83))   # 95 / 100
    break_block(st, RA, (3, 71, -4))
    drop(st, "Rock_Stone_Cobble", 12, (3.5, 71.0, -3.5))
    K.eq((pc(kA).get("Rock_Stone_Cobble"), cnt(inv_of(RA))), (100, {"Rock_Stone_Cobble": 7}), "BLOCK: 5 into the Void (now full), 7 into the inventory")
    fill(inv_of(RA))
    break_block(st, RA, (3, 72, -4))
    ref = drop(st, "Ore_Copper", 6, (3.5, 72.0, -3.5))
    left = items(st)
    K.check(alive(ref) and left == [("Ore_Copper", 6, 10.5, 64.0, 10.5)],
            "BLOCK: Void + inventory full -> the SAME entity, all 6 items, moved to the player's feet: %s" % left)
    K.check(CARDS[-1][3].endswith("at your feet"), "BLOCK: the card says 'full, at your feet': %s" % CARDS[-1][3])
    st.removeEntity(ref, RR.REMOVE)
    # partial: room for 2 in the inventory
    inv_of(RA).removeItemStack(IS("Food_Bread", 25))
    inv_of(RA).addItemStack(IS("Ore_Copper", 98))
    break_block(st, RA, (3, 73, -4))
    ref = drop(st, "Ore_Copper", 6, (3.5, 73.0, -3.5))
    K.check(alive(ref) and items(st) == [("Ore_Copper", 4, 10.5, 64.0, 10.5)] and cnt(inv_of(RA)).get("Ore_Copper") == 100,
            "BLOCK: 2 fit -> 2 in the inventory, the entity keeps 4 at the feet: %s" % items(st))
    st.removeEntity(ref, RR.REMOVE)
    INVS[str(RA)] = SIC(JShort(9))
    Pool.add(kA, "Rock_Stone_Cobble", Long_(-100))
    # untouched cases
    n_before = cnt(inv_of(RA)), pc(kA)
    break_block(st, RA, (5, 70, 5), cancel=True)
    r1 = drop(st, "Rock_Stone_Cobble", 3, (5.5, 70.0, 5.5))
    break_block(st, RA, (6, 70, 6))
    r2 = drop(st, "Rock_Stone_Cobble", 3, (6.5, 70.0, 6.5), pickup=True)
    r3 = drop(st, "Rock_Stone_Cobble", 3, (6.5, 70.0, 6.5), reason=AR.LOAD)
    r4 = drop(st, "Rock_Stone_Cobble", 3, (7.5, 70.0, 7.5))
    r5 = drop(st2, "Rock_Stone_Cobble", 3, (6.5, 70.0, 6.5))
    K.check(all(alive(x) for x in (r1, r2, r3, r4, r5)) and (cnt(inv_of(RA)), pc(kA)) == n_before,
            "BLOCK: a cancelled break, a PickupItemComponent animation, a LOAD, an unclaimed spot, another world -> untouched")
    for x in (r1, r2, r3, r4):
        st.removeEntity(x, RR.REMOVE)
    st2.removeEntity(r5, RR.REMOVE)
    now = System.nanoTime()
    Book.claim("skyytest", 1.5, 2.0, 3.5, UA, 1, now)
    K.check(Book.find("skyytest", 1.5, 2.0, 3.5, now + 1000000000) is not None and Book.find("skyytest", 1.5, 2.0, 3.5, now + 2000000000) is None,
            "BLOCK: a claim lives 1.5 s (found at +1 s, gone at +2 s)")
    for flag in ("PICK_BLOCKS", "PICK_ON"):
        setattr(Cfg, flag, False)
        break_block(st, RA, (8, 70, 8))
        rx = drop(st, "Rock_Stone_Cobble", 3, (8.5, 70.0, 8.5))
        K.check(alive(rx), "BLOCK: %s off -> the drop stays" % flag)
        st.removeEntity(rx, RR.REMOVE)
        setattr(Cfg, flag, True)
    # felled logs
    FELL = {}
    bridge.put("skill:fn:felledBy", Fn(lambda o: FELL.get("%s|%d|%d|%d" % (o[0], int(o[1]), int(o[2]), int(o[3])))))
    FELL["skyytest|20|80|20"] = JArray(JClass("java.lang.Object"))([UA, JString(kA), Long_(System.currentTimeMillis()), JString("falling")])
    rf = drop(st, "Rock_Stone_Cobble", 2, (20.5, 80.0, 20.5))
    rg = drop(st, "Rock_Stone_Cobble", 2, (21.5, 80.0, 20.5))
    K.check(gone(rf) and alive(rg) and pc(kA).get("Rock_Stone_Cobble") == 2,
            "BLOCK: a felled-log drop (skill:fn:felledBy) goes to the feller; the block next to it (no record) stays")
    st.removeEntity(rg, RR.REMOVE)
    # island rules
    UC, RC = player(st, "Cid", (0.5, 64.0, 0.5))
    bridge.put("island:perm:fn", Fn(lambda o: Boolean_.FALSE if str(o[0]) == str(UC) and str(o[2]) == "pickup" else None))
    break_block(st, RC, (9, 70, 9))
    rc = drop(st, "Rock_Stone_Cobble", 3, (9.5, 70.0, 9.5))
    K.check(alive(rc) and items(st) == [("Rock_Stone_Cobble", 3, 9.5, 70.0, 9.5)] and pc(str(UC)) == {},
            "BLOCK: island:perm:fn FALSE (a visitor) -> the drop stays where it fell: %s" % items(st))
    st.removeEntity(rc, RR.REMOVE)
    bridge.remove("island:perm:fn")
    # fault 3: the entity update fails -> rolled back
    Give.FAULT = 3
    p_, i_ = pc(kA), cnt(inv_of(RA))
    break_block(st, RA, (11, 70, 11))
    r3 = drop(st, "Rock_Stone_Cobble", 4, (11.5, 70.0, 11.5))
    Give.FAULT = 0
    K.check(alive(r3) and items(st) == [("Rock_Stone_Cobble", 4, 11.5, 70.0, 11.5)] and pc(kA) == p_ and cnt(inv_of(RA)) == i_,
            "BLOCK: fault 3 (entity update) -> Void + inventory rolled back, the drop stays whole where it fell")
    st.removeEntity(r3, RR.REMOVE)
    # converters before / after ours: the converted stack arrives
    for nm in ("SkyyHkConvA", "SkyyHkConvB"):
        conv[nm].ON = True
        break_block(st, RA, (12, 70, 12))
        drop(st, "Weapon_Sword_Iron", 1, (12.5, 70.0, 12.5))
        got = cnt(inv_of(RA))
        K.check(got.get("Skyy_Unid_Sword") == 1 and "Weapon_Sword_Iron" not in got and items(st) == [],
                "BLOCK: a converter registered %s ours (GearDropSys pattern) -> the CONVERTED stack is delivered: %s" % (
                    "before" if nm.endswith("A") else "after", got))
        inv_of(RA).removeItemStack(IS("Skyy_Unid_Sword", 1))
        conv[nm].ON = False
    # a later system queues a component put on the item's ref during the add: our job re-queues itself, so the put runs first, no error
    PutC.ON = True
    Book.LAST = None
    d0 = int(Book.N.get(3))
    break_block(st, RA, (16, 70, 16))
    rp = drop(st, "Rock_Stone_Cobble", 2, (16.5, 70.0, 16.5))
    PutC.ON = False
    K.check(gone(rp) and items(st) == [] and int(Book.N.get(3)) == d0 + 1 and Book.LAST is None,
            "BLOCK: a system after ours queues a put on the item's ref -> it runs before our removal (re-queued job), delivered, no error (%s)" % Book.LAST)
    # routes: off = no card, chat = no card (chat line; no packet handler in the harness)
    for route in ("off", "chat"):
        ROUTE["v"] = route
        c0 = len(CARDS)
        break_block(st, RA, (13, 70, 13))
        drop(st, "Rock_Stone_Cobble", 1, (13.5, 70.0, 13.5))
        K.check(len(CARDS) == c0 and items(st) == [], "BLOCK: msgroute %s -> delivered, no feed card" % route)
    ROUTE["v"] = "feed"
    # review fix 4: route off = no pickup sound; feed route with no feed (SkyyHud missing) = the rate-limited chat line
    Give.SND.clear()
    Give.CHAT.clear()
    ROUTE["v"] = "off"
    break_block(st, RA, (13, 71, 13))
    drop(st, "Rock_Stone_Cobble", 1, (13.5, 71.0, 13.5))
    K.check(Give.SND.get(UA) is None and items(st) == [], "FIX4: route off -> delivered, NO pickup sound")
    ROUTE["v"] = "feed"
    break_block(st, RA, (13, 72, 13))
    drop(st, "Rock_Stone_Cobble", 1, (13.5, 72.0, 13.5))
    K.check(Give.SND.get(UA) is not None and Give.CHAT.get(UA) is None, "FIX4: route feed with SkyyHud -> card + sound, no chat line")
    feedfn = bridge.remove("feed:fn:push")
    c0 = len(CARDS)
    break_block(st, RA, (13, 73, 13))
    drop(st, "Rock_Stone_Cobble", 1, (13.5, 73.0, 13.5))
    bridge.put("feed:fn:push", feedfn)
    K.check(len(CARDS) == c0 and Give.CHAT.get(UA) is not None and items(st) == [],
            "FIX4: route feed but no feed:fn:push (no SkyyHud) -> falls back to the chat line (never silent)")
    K.eq([str(Give.text("Cobblestone", JArray(JLong)(v), 30)) for v in ([30, 0, 0], [10, 20, 0], [0, 30, 0], [10, 15, 5])],
         ["Cobblestone > Void", "Cobblestone > Void + inventory", "Cobblestone", "Cobblestone - full, at your feet"],
         "FIX4: card text names all-Void / split / inventory / feet")
    # review fix 1: no settled profile (switch settling / crash recovery pending / shutdown) -> NOTHING moves, the drop stays where it fell
    Pool.CLOSED = True
    i0, p0_, n13 = cnt(inv_of(RA)), pc(kA), int(Book.N.get(13))
    break_block(st, RA, (14, 70, 14))
    r14 = drop(st, "Rock_Stone_Cobble", 5, (14.5, 70.0, 14.5))
    Pool.CLOSED = False
    K.check(alive(r14) and items(st) == [("Rock_Stone_Cobble", 5, 14.5, 70.0, 14.5)] and cnt(inv_of(RA)) == i0 and pc(kA) == p0_
            and int(Book.N.get(13)) == n13 + 1,
            "FIX1: no settled profile -> nothing moved (inventory %s, Void %s), the whole drop stays where it fell: %s" % (cnt(inv_of(RA)), pc(kA), items(st)))
    st.removeEntity(r14, RR.REMOVE)
    BUSY = "profile:busy:" + kA
    bridge.put(BUSY, Boolean_.TRUE)
    break_block(st, RA, (14, 71, 14))
    r14 = drop(st, "Rock_Stone_Cobble", 5, (14.5, 71.0, 14.5))
    bridge.remove(BUSY)
    K.check(alive(r14) and items(st) == [("Rock_Stone_Cobble", 5, 14.5, 71.0, 14.5)] and cnt(inv_of(RA)) == i0 and pc(kA) == p0_,
            "FIX1: profile:busy (crash recovery pending) -> nothing moved, the drop stays")
    st.removeEntity(r14, RR.REMOVE)
    # review fix 2: the item hook failed to register (ITEM_OK false) -> no block claim
    Book.ITEM_OK = False
    n0 = int(Book.N.get(0))
    break_block(st, RA, (14, 72, 14))
    Book.ITEM_OK = True
    K.eq(int(Book.N.get(0)), n0, "FIX2: ITEM_OK false -> the break claims nothing")

    # ------------------------------------------------------------------ SAVED: delivered once, persisted once
    Pool.pool(kA).clear()
    Pool.saveSoon(kA)
    Pool.WRITER.submit(JClass("java.util.concurrent.Executors").callable(JClass("java.lang.Thread")())).get()
    break_block(st, RA, (15, 70, 15))
    drop(st, "Rock_Stone_Cobble", 9, (15.5, 70.0, 15.5))
    import time as _t
    _t.sleep(1.5)
    Pool.WRITER.submit(JClass("java.util.concurrent.Executors").callable(JClass("java.lang.Thread")())).get()
    Pool.POOLS.clear()
    K.check(pc(kA) == {"Rock_Stone_Cobble": 9} and items(st) == [],
            "SAVED: after the writer, a restart reloads the Void with the 9 items and no item entity is left: %s %s" % (pc(kA), items(st)))

    # ------------------------------------------------------------------ MOB
    bridge.put("mob:fn:credit", MCreditFn())
    UB, RB = player(st, "Ben", (30.5, 64.0, 30.5))
    UD, RD = player(st2, "Dee", (0.5, 64.0, 0.5))      # another world
    ROLL = {"v": None}
    Book.ROLLS = Fn(lambda dl: ROLL["v"])
    SPAWNED = []

    @JImplements("java.util.function.BiFunction")
    class Spawn(object):
        @JOverride
        def apply(self, lst, pos):
            # generateItemDrop's holder, minus the parts that need the world's GameplayConfig asset (Velocity / Despawn): ItemComponent +
            # TransformComponent at EXACTLY pos (VERIFIED bytecode: every holder of generateItemDrops gets the position it was given)
            hs_ = JArray(JClass("com.hypixel.hytale.component.Holder"))(int(lst.size()))
            for i_ in range(int(lst.size())):
                SPAWNED.append((str(lst.get(i_).getItemId()), int(lst.get(i_).getQuantity()), float(pos.x()), float(pos.y()), float(pos.z())))
                hs_[i_] = ent(None, (pos.x(), pos.y(), pos.z()), [(T_ITC, ITC(lst.get(i_)))])
            return hs_
    Book.SPAWN = Spawn()
    sysm, syss = DeathMark(), ShareSys()

    def mob(store, pos, killer_ref, instantly=True, dropped=False, mode=None, corpse=None):
        u = UUID.randomUUID()
        role = us.allocateInstance(ROLE.class_)
        jfield(ROLE.class_, "dropListId").set(role, JString("Drop_Test"))
        if instantly:
            jfield(ROLE.class_, "dropDeathItemsInstantly").setBoolean(role, True)
        if dropped:
            jfield(ROLE.class_, "deathItemsDropped").setBoolean(role, True)
        npc = us.allocateInstance(NPCE.class_)
        jfield(NPCE.class_, "role").set(npc, role)
        src = DENT(killer_ref) if killer_ref is not None else None
        dc = us.allocateInstance(DTHC.class_)
        jfield(DTHC.class_, "deathInfo").set(dc, DMG(src, JInt(0), JFloat(5.0)))
        dc.setItemsLossMode(mode or ILM.ALL)
        comps = [(T_NPC, npc), (T_DTH, dc), (T_UU, UUIDC(u))]
        if corpse is not None:
            comps.append((T_DCR, corpse))
        r_ = store.addEntity(ent(store, pos, comps), AR.SPAWN)
        return u, r_

    def die(store, mref, which):
        f_ = sysm if which == "mark" else syss

        def f(chunk, i_, cb):
            f_.tick(JFloat(0.033), JInt(i_), chunk, store, cb)
        store.forEachChunk(f_.getQuery(), chunk_of(store, mref, None)(f))

    def hit(mu, pu, amt, after, mx=100.0):
        MCredit.hit(str(mu), str(pu), float(amt), float(after), 0.0, float(mx), System.currentTimeMillis())

    # 1. Ava did most damage, Ben dealt the killing blow (overkill: 50 hit on 10 hp left counts 10)
    for k_ in (kA, str(UB)):
        Pool.pool(k_).clear()
    INVS[str(RA)], INVS[str(RB)] = SIC(JShort(9)), SIC(JShort(9))
    mu, mr = mob(st, (40.0, 65.0, 40.0), RB)
    hit(mu, UA, 30, 70)
    hit(mu, UB, 20, 50)
    hit(mu, UA, 40, 10)
    hit(mu, UB, 50, 0)
    snap = MCreditFn().apply(JString(str(mu)))
    K.check(snap is not None and str(snap[0]) == str(UA) and float(snap[1]) == 70.0 and float(snap[2]) == 100.0 and str(snap[3]) == str(UB),
            "MOB: SkyyMobs credit: Ava 70 top, total 100 (Ben's 50 overkill counts the 10 left), killing blow Ben: %s" % (list(snap) if snap else None))
    conv["SkyyHkConvA"].ON = True
    early = drop(st, "Weapon_Sword_Iron", 1, (40.0, 66.0, 40.0))     # SkyyGear's extra roll arriving BEFORE the mark
    K.check(alive(early), "MOB: a drop before the death mark waits (unclaimed)")
    die(st, mr, "mark")
    K.check(gone(early) and cnt(inv_of(RA)).get("Skyy_Unid_Sword") == 1, "MOB: the death mark takes the early drop from the ring -> top damager")
    drop(st, "Ore_Copper", 3, (40.0, 66.0, 40.0))                  # DropDeathItems
    drop(st, "Weapon_Sword_Iron", 1, (40.0, 66.0, 40.0))
    K.check(pc(kA).get("Ore_Copper") == 3 and cnt(inv_of(RA)).get("Skyy_Unid_Sword") == 2 and items(st) == [],
            "MOB: the mob's drops -> the top damager (Void first; gear converted): Void %s inv %s" % (pc(kA), cnt(inv_of(RA))))
    K.check(MCreditFn().apply(JString(str(mu))) is None, "MOB: the credit entry was taken at the death")
    ROLL["v"] = JClass("java.util.ArrayList")()
    ROLL["v"].add(IS("Ore_Copper", 8))
    ROLL["v"].add(IS("Weapon_Sword_Iron", 1))
    die(st, mr, "share")
    K.check(SPAWNED and all(abs(t_[3] - 66.015625) < 1e-12 and t_[2] == 40.0 and t_[4] == 40.0 for t_ in SPAWNED),
            "MOB: the share spawns at the mob + (0, 1 + 1/64, 0): %s" % SPAWNED)
    gb = add(cnt(inv_of(RB)), pc(str(UB)))
    K.check(gb.get("Ore_Copper") == 4 and gb.get("Skyy_Unid_Sword", 0) + gb.get("Weapon_Sword_Iron", 0) <= 1 and items(st) == []
            and "Weapon_Sword_Iron" not in gb,
            "MOB: the killer's share = 50 %% of a second roll (8 copper -> 4; the sword's 0.5 rounds by chance), spawned "
            "at +1/64 and converted: %s" % gb)
    die(st, mr, "mark")
    K.check(int(Book.N.get(1)) == 1, "MOB: one death = one mark (DONE)")
    st.removeEntity(mr, RR.REMOVE)
    # 2. same player top + killer -> no share
    mu, mr = mob(st, (41.0, 65.0, 41.0), RA)
    hit(mu, UA, 100, 0)
    die(st, mr, "mark")
    K.check(Book.SHARE.isEmpty(), "MOB: top damager = killer -> no share")
    st.removeEntity(mr, RR.REMOVE)
    # 3. no credit -> the killer; 4. top in another world -> the killer; 5. nobody -> vanilla
    for ci_, (case, killer_, hitter) in enumerate((("no credit", RB, None), ("top in another world", RB, UD), ("no player", None, None))):
        mx_ = 42.0 + 3 * ci_
        mu, mr = mob(st, (mx_, 65.0, 42.0), killer_)
        if hitter is not None:
            hit(mu, hitter, 100, 0)
        die(st, mr, "mark")
        rx = drop(st, "Plant_Crop_Wheat_Item", 2, (mx_, 66.0, 42.0))
        if killer_ is None:
            K.check(alive(rx), "MOB: %s -> the drop stays (vanilla)" % case)
            st.removeEntity(rx, RR.REMOVE)
        else:
            K.check(gone(rx), "MOB: %s -> the killer gets it" % case)
        Book.DONE.clear()
        st.removeEntity(mr, RR.REMOVE)
    # 6. the drop condition
    for case, kw in (("already dropped", {"dropped": True}), ("loss mode NONE", {"mode": ILM.NONE}),
                     ("corpse timer not due", {"instantly": False, "corpse": DCR(5.0, None)})):
        n1 = int(Book.N.get(1))
        try:
            mu, mr = mob(st, (43.0, 65.0, 43.0), RA, **kw)
        except Exception as e:
            K.notes.append("MOB condition %s: fixture could not build it (%s)" % (case, e))
            continue
        die(st, mr, "mark")
        K.eq(int(Book.N.get(1)), n1, "MOB: %s -> no mark" % case)
        st.removeEntity(mr, RR.REMOVE)
    Cfg.PICK_MOBS = False
    mu, mr = mob(st, (44.0, 65.0, 44.0), RA)
    die(st, mr, "mark")
    rx = drop(st, "Ore_Copper", 1, (44.0, 66.0, 44.0))
    K.check(alive(rx), "MOB: pickup.mobs off -> drops stay")
    Cfg.PICK_MOBS = True
    st.removeEntity(rx, RR.REMOVE)
    st.removeEntity(mr, RR.REMOVE)
    # review fix 2: ITEM_OK false -> no death mark, no credit taken, no killer share spawned
    Book.ITEM_OK = False
    n1, s0 = int(Book.N.get(1)), len(SPAWNED)
    mu, mr = mob(st, (45.0, 65.0, 45.0), RB)
    hit(mu, UA, 90, 10)
    hit(mu, UB, 10, 0)
    die(st, mr, "mark")
    die(st, mr, "share")
    K.check(int(Book.N.get(1)) == n1 and Book.SHARE.isEmpty() and len(SPAWNED) == s0 and MCreditFn().apply(JString(str(mu))) is not None,
            "FIX2: ITEM_OK false -> no mark, no share roll spawned, the credit is left alone")
    Book.ITEM_OK = True
    st.removeEntity(mr, RR.REMOVE)
    # review fix 3: two mobs dying in ONE tick at the SAME spot for different players -> contested: nobody gets those drops (no misattribution)
    for k_ in (kA, str(UB)):
        Pool.pool(k_).clear()
    INVS[str(RA)], INVS[str(RB)] = SIC(JShort(9)), SIC(JShort(9))
    gA0, gB0, n12 = add(cnt(inv_of(RA)), pc(kA)), add(cnt(inv_of(RB)), pc(str(UB))), int(Book.N.get(12))
    m1, r1_ = mob(st, (50.0, 65.0, 50.0), RA)
    m2, r2_ = mob(st, (50.0, 65.0, 50.0), RB)
    hit(m1, UA, 100, 0)
    hit(m2, UB, 100, 0)
    die(st, r1_, "mark")
    die(st, r2_, "mark")
    dx = drop(st, "Ore_Copper", 2, (50.0, 66.0, 50.0))
    K.check(alive(dx) and add(cnt(inv_of(RA)), pc(kA)) == gA0 and add(cnt(inv_of(RB)), pc(str(UB))) == gB0 and int(Book.N.get(12)) >= n12 + 1,
            "FIX3: same spot, same tick, different owners -> contested, the drop stays on the ground (nobody gets the wrong loot)")
    st.removeEntity(dx, RR.REMOVE)
    st.removeEntity(r1_, RR.REMOVE)
    st.removeEntity(r2_, RR.REMOVE)
    # a USED claim (its drops already arrived) is replaced: mob 1 drops -> Ava, then mob 2 at the same spot -> Ben
    m1, r1_ = mob(st, (52.0, 65.0, 52.0), RA)
    hit(m1, UA, 100, 0)
    die(st, r1_, "mark")
    d1 = drop(st, "Ore_Copper", 2, (52.0, 66.0, 52.0))
    m2, r2_ = mob(st, (52.0, 65.0, 52.0), RB)
    hit(m2, UB, 100, 0)
    die(st, r2_, "mark")
    d2 = drop(st, "Ore_Copper", 3, (52.0, 66.0, 52.0))
    gA, gB = add(cnt(inv_of(RA)), pc(kA)), add(cnt(inv_of(RB)), pc(str(UB)))
    K.check(gone(d1) and gone(d2) and gA.get("Ore_Copper", 0) - gA0.get("Ore_Copper", 0) == 2 and gB.get("Ore_Copper", 0) - gB0.get("Ore_Copper", 0) == 3,
            "FIX3: a used claim is replaced -> mob 1's 2 copper to Ava, mob 2's 3 copper to Ben: %s / %s" % (gA, gB))
    st.removeEntity(r1_, RR.REMOVE)
    st.removeEntity(r2_, RR.REMOVE)
    Cfg.PICK_SHARE = 0
    K.check(Book.split(UB, UA, 0)[1] is None and str(Book.split(UB, UA, 50)[1]) == str(UB) and str(Book.split(UB, None, 50)[0]) == str(UB)
            and Book.split(None, None, 50) is None, "MOB: the rule (pure): share 0 = none; top != killer = share; no top = killer; nobody = null")
    Cfg.PICK_SHARE = 50
    rnd = JClass("java.util.Random")(7)
    rolled = JClass("java.util.ArrayList")()
    rolled.add(IS("Ore_Copper", 1))
    tot_ = sum(int(Book.scale(rolled, 50, rnd).size()) for _ in range(4000))
    K.check(1850 <= tot_ <= 2150, "MOB: 50 %% of a single item = a coin flip (%d of 4000)" % tot_)

    # ------------------------------------------------------------------ 0.8.4 PET: a mob killed by a pet / summon -> its OWNER
    @JImplements("java.util.function.Function")
    class Own(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, o):
            return self.f(o)
    for k_ in (kA, str(UB)):
        Pool.pool(k_).clear()
    INVS[str(RA)], INVS[str(RB)] = SIC(JShort(9)), SIC(JShort(9))
    PETS = {}
    bridge.put("pets:fn:ownerOf", Own(lambda o: PETS.get(str(o))))

    def pet(store, owner_u, pos):
        pu_ = UUID.randomUUID()
        r_ = store.addEntity(ent(store, pos, [(T_UU, UUIDC(pu_))]), AR.SPAWN)
        if owner_u is not None:
            PETS[str(pu_)] = owner_u
        return pu_, r_
    ROLL["v"] = JClass("java.util.ArrayList")()
    ROLL["v"].add(IS("Ore_Copper", 8))
    # a) Ava's pet kills, nobody else hit it -> Ava gets the whole drop
    _pu, pr_a = pet(st, UA, (60.0, 64.0, 60.0))
    K.check(str(Book.petOwner(st, pr_a)) == str(UA), "PET: petOwner names the owner (pets:fn:ownerOf)")
    mu, mr = mob(st, (60.0, 65.0, 61.0), pr_a)
    hit(mu, UA, 100, 0)            # SkyyMobs 0.1.8 credits the pet's damage to its owner
    die(st, mr, "mark")
    dx = drop(st, "Ore_Copper", 3, (60.0, 66.0, 61.0))
    K.check(gone(dx) and add(cnt(inv_of(RA)), pc(kA)).get("Ore_Copper") == 3 and Book.SHARE.isEmpty(),
            "PET: Ava's pet's kill -> Ava gets the drop (owner = top = killer: no share): %s" % add(cnt(inv_of(RA)), pc(kA)))
    st.removeEntity(mr, RR.REMOVE)
    # b) Ben did most damage, Ava's pet landed the killing blow -> Ben the drop, Ava (the pet's owner) the killer's share
    gA0 = add(cnt(inv_of(RA)), pc(kA))
    mu, mr = mob(st, (62.0, 65.0, 62.0), pr_a)
    hit(mu, UB, 80, 20)
    hit(mu, UA, 20, 0)
    die(st, mr, "mark")
    dx = drop(st, "Ore_Copper", 5, (62.0, 66.0, 62.0))
    die(st, mr, "share")
    gA, gB = add(cnt(inv_of(RA)), pc(kA)), add(cnt(inv_of(RB)), pc(str(UB)))
    K.check(gone(dx) and gB.get("Ore_Copper") == 5 and gA.get("Ore_Copper", 0) - gA0.get("Ore_Copper", 0) == 4 and items(st) == [],
            "PET: Ben top damager -> the drop (5); Ava's pet's killing blow -> Ava the killer's share (8 x 50 %% = 4): %s / %s" % (gA, gB))
    st.removeEntity(mr, RR.REMOVE)
    # c) owner OFFLINE, d) owner in ANOTHER WORLD, e) no key, f) junk key -> the drop stays where it fell (vanilla); nobody gains
    OFF = UUID.nameUUIDFromBytes(b"pick-offline")
    _pu, pr_off = pet(st, OFF, (64.0, 64.0, 64.0))
    _pu, pr_far = pet(st, UD, (65.0, 64.0, 65.0))
    _pu, pr_none = pet(st, None, (66.0, 64.0, 66.0))
    for case, pref_, credit, setup in (("owner offline", pr_off, OFF, None), ("owner in another world", pr_far, UD, None),
                                       ("no pets:fn:ownerOf", pr_a, None, "nokey"), ("a junk key answer", pr_a, None, "junk"),
                                       ("an unknown creature", pr_none, None, None)):
        if setup == "nokey":
            keep = bridge.remove("pets:fn:ownerOf")
        elif setup == "junk":
            keep = bridge.put("pets:fn:ownerOf", Own(lambda o: JString("nope")))
        before = [add(cnt(inv_of(x)), pc(str(y))) for x, y in ((RA, UA), (RB, UB), (RD, UD))]
        mu, mr = mob(st, (67.0, 65.0, 67.0), pref_)
        if credit is not None:
            hit(mu, credit, 100, 0)
        die(st, mr, "mark")
        die(st, mr, "share")
        dx = drop(st, "Ore_Copper", 2, (67.0, 66.0, 67.0))
        after = [add(cnt(inv_of(x)), pc(str(y))) for x, y in ((RA, UA), (RB, UB), (RD, UD))]
        K.check(alive(dx) and before == after and items(st) == [("Ore_Copper", 2, 67.0, 66.0, 67.0)],
                "PET: %s -> the drop stays on the ground (vanilla), nobody gains, nothing doubled: %s" % (case, items(st)))
        st.removeEntity(dx, RR.REMOVE)
        st.removeEntity(mr, RR.REMOVE)
        Book.DONE.clear()
        if setup is not None:
            bridge.put("pets:fn:ownerOf", keep if setup == "nokey" else Own(lambda o: PETS.get(str(o))))
    bridge.put("pets:fn:ownerOf", Own(lambda o: PETS.get(str(o))))
    K.check("pets count for their owner" in str(Book.state()), "PET: the state line names the pet path: %s" % Book.state())
    bridge.remove("pets:fn:ownerOf")

    # ------------------------------------------------------------------ 0.8.4 HARV: F-harvest -> the Void first
    IPE = JClass("com.hypixel.hytale.server.core.event.events.ecs.InteractivelyPickupItemEvent")
    DIE = JClass("com.hypixel.hytale.server.core.event.events.ecs.DropItemEvent$Drop")
    TASKS = []

    @JImplements("java.util.function.Consumer")
    class Ex(object):
        @JOverride
        def accept(self, t):
            TASKS.append(t)
    Harv.EXEC = Ex()
    Book.HARV_OK = Book.DROP_OK = True     # the plugin sets them after the two registers
    hsys, dsys = HarvSys(), DropSys()

    def on_player(store, pref, sysx, ev):
        def f(chunk, i_, cb):
            sysx.handle(JInt(i_), chunk, store, cb, ev)
        store.forEachChunk(sysx.getQuery(), chunk_of(store, pref, None)(f))

    def harvest(store, pref, stacks, cancel_after=False):
        """ItemUtils.interactivelyPickupItem per stack (VERIFIED order), then the queued World.execute tasks. Returns (events, thrown)."""
        evs, thrown = [], []
        for iid, q in stacks:
            e = IPE(IS(iid, q))
            on_player(store, pref, hsys, e)
            if cancel_after:
                e.setCancelled(True)      # a listener after ours (island guard) cancels -> the engine gives nothing
            evs.append(e)
            if e.isCancelled():
                continue
            given = e.getItemStack()
            tx = inv_of(pref).addItemStack(given)                 # Player.giveItem -> the pickup container
            rem = tx.getRemainder()
            if rem is not None and not rem.isEmpty():
                d = DIE(rem, JFloat(1.0))                         # ItemUtils.dropItem -> throwItem -> DropItemEvent$Drop
                on_player(store, pref, dsys, d)
                if not d.isCancelled():
                    thrown.append((str(d.getItemStack().getItemId()), int(d.getItemStack().getQuantity())))
        while TASKS:
            TASKS.pop(0).run()
        return evs, thrown

    UH, RH = player(st, "Hal", (70.5, 64.0, 70.5))
    kH = str(UH)
    TOT[kH + "|Farming"] = 0
    fspace = int(VS.capsK(UH, kH).get("Farming"))
    K.eq(fspace, 100, "HARV: Farming Lv 1 Normal = 100 items of space")
    WH = "Plant_Crop_Wheat_Item"
    evs, thrown = harvest(st, RH, [(WH, 5)])
    K.eq((pc(kH), cnt(inv_of(RH)), thrown), ({WH: 5}, {}, []), "HARV: Void room -> all 5 wheat into the Void, inventory empty")
    K.check(not evs[0].isCancelled() and int(evs[0].getItemStack().getQuantity()) == 5,
            "HARV: the pickup event is never cancelled or changed (SkyySkills / SkyyCollections / SkyyQuests still count it)")
    K.check(CARDS and CARDS[-1][1:3] == ("pickup", WH) and CARDS[-1][3].endswith("> Void"), "HARV: feed card '... > Void': %s" % (CARDS[-1:],))
    Pool.add(kH, WH, Long_(92))                       # 97 / 100: room 3
    evs, thrown = harvest(st, RH, [(WH, 5)])
    K.eq((pc(kH).get(WH), cnt(inv_of(RH)), thrown), (100, {WH: 2}, []), "HARV: room 3 -> 3 into the Void, 2 stay in the inventory")
    evs, thrown = harvest(st, RH, [(WH, 4)])
    K.eq((pc(kH).get(WH), cnt(inv_of(RH)), thrown), (100, {WH: 6}, []), "HARV: Void FULL -> all 4 stay in the inventory (vanilla), nothing lost")
    # inventory full: the overflow is caught before the throw
    Pool.add(kH, WH, Long_(-100))
    INVS[str(RH)] = SIC(JShort(2))
    fill(inv_of(RH))
    evs, thrown = harvest(st, RH, [(WH, 5)])
    K.eq((pc(kH).get(WH), thrown, int(Book.N.get(15)) >= 5), (5, [], True), "HARV: inventory full + Void room -> the throw is CANCELLED, all 5 in the Void")
    Pool.add(kH, WH, Long_(93))                       # 98 / 100
    evs, thrown = harvest(st, RH, [(WH, 5)])
    K.eq((pc(kH).get(WH), thrown), (100, [(WH, 3)]), "HARV: inventory full + room 2 -> 2 into the Void, the thrown stack shrinks to 3 (at the feet)")
    evs, thrown = harvest(st, RH, [(WH, 4)])
    K.eq((pc(kH).get(WH), thrown), (100, [(WH, 4)]), "HARV: inventory AND Void full -> thrown whole as vanilla (4)")
    bridge.put("island:perm:fn", Fn(lambda o: Boolean_.FALSE if str(o[0]) == kH and str(o[2]) == "pickup" else None))
    Give.PERM.clear()
    Pool.add(kH, WH, Long_(-100))
    evs, thrown = harvest(st, RH, [(WH, 3)])
    K.eq((pc(kH).get(WH, 0), thrown), (0, [(WH, 3)]), "HARV: island:perm:fn FALSE -> the overflow is thrown as vanilla, Void untouched")
    bridge.remove("island:perm:fn")
    Give.PERM.clear()
    # several stacks in one tick, an existing stack of the item, a non-Void item
    INVS[str(RH)] = SIC(JShort(9))
    Pool.pool(kH).clear()
    inv_of(RH).addItemStack(IS(WH, 10))               # the player's own 10 wheat - never taken
    evs, thrown = harvest(st, RH, [(WH, 3), ("Weapon_Sword_Iron", 1), (WH, 4)])
    K.eq((pc(kH), cnt(inv_of(RH))), ({WH: 7}, {WH: 10, "Weapon_Sword_Iron": 1}),
         "HARV: two wheat stacks in one tick -> 7 into the Void; the player's own 10 wheat stay; a sword (no Void category) stays")
    # a later listener cancels -> the engine gave nothing; the task moves nothing
    p0, i0 = pc(kH), cnt(inv_of(RH))
    evs, thrown = harvest(st, RH, [(WH, 6)], cancel_after=True)
    K.eq((pc(kH), cnt(inv_of(RH))), (p0, i0), "HARV: a pickup cancelled after ours (island guard) -> nothing given, nothing moved")
    # faults
    for f_, what in ((4, "after the booking"), (5, "after the removal")):
        p0, i0 = pc(kH), cnt(inv_of(RH))
        Give.FAULT = f_
        harvest(st, RH, [(WH, 2)])
        Give.FAULT = 0
        K.eq((pc(kH), cnt(inv_of(RH))), (p0, add(i0, {WH: 2})), "HARV: fault %d (%s) -> rolled back: the 2 stay in the inventory, Void unchanged" % (f_, what))
    INVS[str(RH)] = SIC(JShort(1))
    fill(inv_of(RH))
    p0 = pc(kH)
    Give.FAULT = 6
    evs, thrown = harvest(st, RH, [(WH, 3)])
    Give.FAULT = 0
    K.eq((pc(kH), thrown), (p0, [(WH, 3)]), "HARV: fault 6 (before the throw update) -> Void unchanged, thrown whole as vanilla")
    INVS[str(RH)] = SIC(JShort(9))
    # paused profile / pickup.blocks off -> vanilla (the inventory keeps them)
    Pool.CLOSED = True
    p0 = pc(kH)
    harvest(st, RH, [(WH, 2)])
    Pool.CLOSED = False
    K.eq((pc(kH), cnt(inv_of(RH))), (p0, {WH: 2}), "HARV: item moves paused (profile settling) -> nothing moved, the 2 stay in the inventory")
    Cfg.PICK_BLOCKS = False
    harvest(st, RH, [(WH, 2)])
    Cfg.PICK_BLOCKS = True
    K.eq((pc(kH), cnt(inv_of(RH))), (p0, {WH: 4}), "HARV: pickup.blocks off -> harvests stay in the inventory")
    # a Q-drop with no window / an expired window / another item -> untouched
    def qdrop(iid, q):
        d = DIE(IS(iid, q), JFloat(1.0))
        on_player(st, RH, dsys, d)
        return d
    p0 = pc(kH)
    d = qdrop(WH, 2)
    K.check(not d.isCancelled() and int(d.getItemStack().getQuantity()) == 2 and pc(kH) == p0, "HARV: a Q-drop with no pickup window -> untouched")
    Harv.HCUR.put(UH, JArray(JClass("java.lang.Object"))([JString(WH), Long_(5), Long_(System.nanoTime() - 500000000), inv_of(RH)]))
    d = qdrop(WH, 2)
    K.check(not d.isCancelled() and pc(kH) == p0 and Harv.HCUR.get(UH) is None, "HARV: an expired window (> 100 ms) -> untouched (and closed)")
    Harv.HCUR.put(UH, JArray(JClass("java.lang.Object"))([JString(WH), Long_(5), Long_(System.nanoTime()), inv_of(RH)]))
    d = qdrop("Ore_Copper", 2)
    d2 = qdrop(WH, 9)
    K.check(not d.isCancelled() and not d2.isCancelled() and pc(kH) == p0, "HARV: another item / more than was harvested -> untouched")
    # FIX (critic 2.1): a Q-drop of the harvested item inside the open window, before the task ran -> NOT taken (the inventory has room)
    Harv.HCUR.clear()
    Pool.pool(kH).clear()
    INVS[str(RH)] = SIC(JShort(9))
    e = IPE(IS(WH, 5))
    on_player(st, RH, hsys, e)                                     # note: window open, task queued
    inv_of(RH).addItemStack(e.getItemStack())                      # giveItem: all 5 fit, no remainder (no throw)
    K.check(Harv.HCUR.get(UH) is not None and len(TASKS) == 1, "HARV fix: the window is open and the task queued after a pickup that fit")
    inv_of(RH).removeItemStack(IS(WH, 2))                          # InventoryPacketHandler: remove from the slot FIRST ...
    d = qdrop(WH, 2)                                               # ... then throwItem -> DropItemEvent$Drop
    K.check(not d.isCancelled() and int(d.getItemStack().getQuantity()) == 2 and pc(kH).get(WH, 0) == 0,
            "HARV fix: a Q-drop of the just-harvested item inside the window (inventory has room) -> thrown as vanilla, Void untouched")
    while TASKS:
        TASKS.pop(0).run()
    K.eq((pc(kH).get(WH, 0), cnt(inv_of(RH)).get(WH, 0)), (3, 0),
         "HARV fix: then the task moves only what is still there (3) - 2 thrown + 3 Void = the 5 harvested, no dupe")
    # the overflow of a FULL container still matches inside the same window (canAddItemStack(1) false)
    INVS[str(RH)] = SIC(JShort(2))
    fill(inv_of(RH))
    Pool.pool(kH).clear()
    evs, thrown = harvest(st, RH, [(WH, 4)])
    K.eq((pc(kH).get(WH, 0), thrown), (4, []), "HARV fix: full inventory overflow is still caught (container full -> canAdd false)")
    INVS[str(RH)] = SIC(JShort(9))
    # FIX (critic 1.1): a pending list whose task never ran (world torn down) must not block later harvests
    AL = JClass("java.util.ArrayList")
    Harv.HCUR.clear()
    Pool.pool(kH).clear()
    stale = AL()
    stale.add(JArray(JClass("java.lang.Object"))([IPE(IS(WH, 1)), JString(WH), Long_(0), inv_of(RH)]))
    Harv.HPEND.put(UH, stale)
    Harv.HPT.put(UH, Long_(System.nanoTime() - 6000000000))       # queued 6 s ago, never ran
    evs, thrown = harvest(st, RH, [(WH, 4)])
    K.eq((pc(kH).get(WH, 0), cnt(inv_of(RH)).get(WH, 0), Harv.HPEND.get(UH), Harv.HPT.get(UH)), (4, 0, None, None),
         "HARV fix: a stale pending list (> 5 s, task never ran) is dropped, a fresh task is queued -> the 4 go to the Void, maps cleaned")
    # a pending list WITHOUT a timestamp (any leftover) is treated as stale too
    Harv.HPEND.put(UH, AL())
    evs, thrown = harvest(st, RH, [(WH, 2)])
    K.eq((pc(kH).get(WH, 0), Harv.HPEND.get(UH)), (6, None), "HARV fix: a pending list with no queue time -> fresh task, 2 more into the Void")
    # a fresh pending list (< 5 s) is still appended to (one task per player per tick)
    TASKS.clear()
    e1, e2 = IPE(IS(WH, 1)), IPE(IS(WH, 1))
    on_player(st, RH, hsys, e1)
    on_player(st, RH, hsys, e2)
    K.eq(len(TASKS), 1, "HARV fix: two pickups in the same tick still share ONE queued task")
    while TASKS:
        TASKS.pop(0).run()
    # FIX (critic 3.3): the Server Setup help of pickup.blocks names the harvest Off behaviour
    _gen = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_skyysacks_0.8.4.py"), encoding="utf8").read()
    K.check("Off: blocks drop on the ground, harvests go to the inventory." in _gen and "felled trees too. Off: they drop on the ground." not in _gen,
            "HARV fix: pickup.blocks help says harvests stay in the inventory when Off")
    Harv.HCUR.clear()
    K.check(int(Book.N.get(14)) > 0 and "F-harvest Void first" in str(Book.state()),
            "HARV: counters + state: %s" % Book.state())
    Harv.EXEC = None

    # ------------------------------------------------------------------ CFG
    P = JClass("java.util.Properties")
    p = P()
    Cfg.pickKeys(p, True)
    K.eq((bool(Cfg.PICK_ON), bool(Cfg.PICK_BLOCKS), bool(Cfg.PICK_MOBS), int(Cfg.PICK_SHARE)), (True, True, True, 50), "CFG: defaults")
    p.setProperty("pickup.on", "false")
    p.setProperty("pickup.killerShare", "250")
    Cfg.pickKeys(p, False)
    K.eq((bool(Cfg.PICK_ON), int(Cfg.PICK_SHARE)), (False, 100), "CFG: hand edit read, share clamped to 100")
    Cfg.pickKeys(P(), False)
    K.check(str(Book.state()).startswith("on ("), "CFG: state line: %s" % Book.state())
    K.notes.append("stats: " + str(Book.stats()))
    Pool.WRITER.shutdownNow()
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)

    def loader_for(j):
        URL = JClass("java.net.URL")
        arr = JArray(URL)(1)
        arr[0] = JClass("java.io.File")(j).toURI().toURL()
        return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())
    before = HK.tree_hash(home)
    pools = os.path.join(home, "pools")
    keys = sorted(f[:-11] for f in os.listdir(pools) if f.endswith(".properties")) if os.path.isdir(pools) else []
    P = JClass("java.nio.file.Paths")
    seen = None
    for start in (1, 2):
        for j in (OLD_JAR, jar):
            SP = JClass(PKG + "SackPool", loader=loader_for(j))
            SP.DIR = P.get(pools)
            got = {}
            for k in keys:
                got[k] = dict((str(e.getKey()), int(e.getValue().longValue())) for e in SP.pool(k).entrySet())
            if seen is None:
                seen = got
            K.check(got == seen, "D start %d %s: every pool loads the same items" % (start, os.path.basename(j)))
    cfgf = os.path.join(home, "config.properties")
    if os.path.isfile(cfgf):
        h0 = sha(cfgf)
        L = loader_for(jar)
        Cfg = JClass(PKG + "SackCfg", loader=L)
        JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
        Cfg.FILE = P.get(cfgf)
        for _ in (1, 2):
            Cfg.MTIME = -1
            Cfg.reload()
        K.eq((bool(Cfg.PICK_ON), bool(Cfg.PICK_BLOCKS), bool(Cfg.PICK_MOBS), int(Cfg.PICK_SHARE)), (True, True, True, 50),
             "D live config.properties (no pickup lines yet) -> the defaults")
        K.eq(sha(cfgf), h0, "D live config.properties byte-identical after two loads")
    K.eq(HK.tree_hash(home), before, "D the live copy's bytes are unchanged by the starts")
    K.notes.append("D: %d profile pools (%d item lines)" % (len(keys), sum(len(v) for v in (seen or {}).values())))
    K.save()


HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("exec", run_exec), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyySacks"))
