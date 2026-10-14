"""Harness for SkyySacks 0.8.2 (/pdadmin rarity <player> <category|all> <rarity>; tools/sacks_0_8_2_patch.py).
Build first: python tools/sacks_0_8_2_patch.py && python SkyySacks/build_skyysacks_0.8.2.py

    python SkyySacks/test_skyysacks_0.8.2.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.8.1 -> 0.8.2: exactly VoidStore (+ rarityArgs, setRarity), VoidAdminTask (+ ci, rar, answer, ~ run), PdAdminCmd
              (~ constructor text, ~ execute) and the version constants differ; non-class files: manifest only
  X  exec     EXECUTED on the compiled classes:
              ARGS   rarityArgs: the six categories + all (any case), Normal / Common / Unique / Rare / Legendary / Omni / Mythic (any
                     case), unknown words -> the reason
              SET    setRarity on a Void with stored items (Mining far over every lower space): Omni + Legendary -> all Normal (Skyy's
                     test), one category from Omni (the other five become Legendary), all -> Omni, Omni on one category, the pd.omniAuto
                     note (still Omni), a bag conversion still settling (the "raises again" note), an unreadable Void (NOREAD); the
                     reply's over-space line; migration.log + crafts.log lines
              NOLOSS the pool (memory AND pools/<key>.properties bytes) is identical after every change, after the writer saved
                     pd/<key>.properties, and after a restart (every memory state dropped, files re-read) - the rarity is what was set;
                     the REAL sweep with an inventory stand-in: an over-space category takes nothing (inventory + pool unchanged), a
                     category with room still takes items (conserved: inventory + pool totals equal)
              TASK   VoidAdminTask.answer: mode 4 = setRarity, not in a world, profile loading, modes 2 (omni) and 3 (resume) unchanged
  D  live     a scratch COPY of the live Skyy_SkyySacks: every pool loads with 0.8.1 and 0.8.2 into the same map, twice; then EVERY live
              profile with a Void file is set to all Normal with setRarity (= /pdadmin rarity <you> all Normal): every pool file stays
              byte-identical, every pool loads the same items after a restart, the pd files hold rar.* = 0 + omni=false and nothing
              else changed
  AA engine-access audit
Scratch: tools/dev/scratch/prof012/sacks (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, shutil, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.8.2"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-0.8.1.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "prof012", "sacks")))
PKG = "com.skyy.sacks."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyySacks")
EXPECT = {
    "VoidStore": ["+m rarityArgs", "+m setRarity"],
    "VoidAdminTask": ["+f ci", "+f rar", "+m answer", "~m run"],
    "PdAdminCmd": ["~c ", "~m execute"],
    "SkyySacksPlugin": ["~m setup"],          # the ready line's version text
    "CfgFn": ["~m opExport"],                 # the config kit's version text
    "CfgRows": ["~m header"],
}
ADDED = []
CATS = ["Mining", "Foraging", "Farming", "Fishing", "Combat", "Smithing"]


def sha(p):
    return hashlib.sha1(open(p, "rb").read()).hexdigest() if os.path.isfile(p) else None


def props(path):
    out = {}
    if os.path.isfile(path):
        for ln in open(path, encoding="latin-1").read().splitlines():
            if ln and not ln.startswith("#") and "=" in ln:
                k, v = ln.split("=", 1)
                out[k.strip()] = v.strip()
    return out


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray, JShort, JString, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    J = lambda n: JClass(PKG + n)
    Pool, VS, Defs, Cfg, Swp, CLog, VAT, PStore, Mirror, Bridge = (J("SackPool"), J("VoidStore"), J("SackDefs"), J("SackCfg"), J("SweepTask"),
                                                                  J("CraftLog"), J("VoidAdminTask"), J("ProcStore"), J("BagMirror"), J("SackBridge"))
    UUID, Paths, Long_, System = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Long"), JClass("java.lang.System")
    bridge = JClass("java.util.concurrent.ConcurrentHashMap")()
    System.getProperties().put("skyy.bridge", bridge)
    Pool.WRITER = JClass("java.util.concurrent.Executors").newSingleThreadScheduledExecutor()

    @JImplements("java.lang.Runnable")
    class NoOp(object):
        @JOverride
        def run(self): pass

    def drain():
        Pool.WRITER.submit(NoOp()).get()

    # coll:fn:catTotal stand-in: "<uuid>|<cat>" -> Long
    TOT = {}

    @JImplements("java.util.function.Function")
    class Coll(object):
        @JOverride
        def apply(self, o):
            v = TOT.get(str(o[0]) + "|" + str(o[1]))
            return None if v is None else Long_(v)
    bridge.put("coll:fn:catTotal", Coll())

    base = os.path.join(scratch, "x")

    def fresh():
        if os.path.exists(base):
            shutil.rmtree(base)
        os.makedirs(os.path.join(base, "pools"))
        for m in (Pool.POOLS, Pool.DIRTY, Pool.PMETA, Pool.PENDING, Pool.LASTSAVE, VS.STATES, VS.BAD, VS.DIRTY, VS.SNAPQ, VS.SNAPFAIL):
            m.clear()
        VS.PEND.clear()
        Pool.DIR = Paths.get(os.path.join(base, "pools"))
        PStore.DIR = Paths.get(os.path.join(base, "processing"))
        VS.DIR = Paths.get(os.path.join(base, "pd"))
        VS.HDIR = Paths.get(os.path.join(base, "history"))
        VS.MIGLOG = Paths.get(os.path.join(base, "migration.log"))
        CLog.FILE = Paths.get(os.path.join(base, "crafts.log"))

    def restart():
        for m in (Pool.POOLS, Pool.DIRTY, Pool.PMETA, Pool.PENDING, Pool.LASTSAVE, VS.STATES, VS.BAD, VS.DIRTY, VS.SNAPQ, VS.SNAPFAIL):
            m.clear()
        VS.PEND.clear()

    def pc(k):
        return dict((str(e.getKey()), int(e.getValue().longValue())) for e in Pool.pool(k).entrySet())

    # ------------------------------------------------------------------ ARGS
    bad = []
    for c_ in CATS + ["all"]:
        for w in (c_, c_.upper(), c_.lower()):
            for r_, want in (("Normal", 0), ("common", 0), ("UNIQUE", 1), ("Rare", 2), ("legendary", 3), ("Omni", 4), ("mythic", 4)):
                got = VS.rarityArgs(w, r_)
                exp = (-1 if c_ == "all" else CATS.index(c_), want)
                if not (hasattr(got, "__len__") and not isinstance(got, str) and (int(got[0]), int(got[1])) == exp):
                    bad.append((w, r_, str(got)))
    K.eq(bad, [], "ARGS: 7 targets x 3 spellings x 7 rarity words")
    K.check(str(VS.rarityArgs("Minning", "Normal")).startswith("unknown category 'Minning'"), "ARGS: unknown category")
    K.check(str(VS.rarityArgs("Mining", "Epic")).startswith("unknown rarity 'Epic'"), "ARGS: unknown rarity")
    K.check(str(VS.rarityArgs("", "")).startswith("unknown category"), "ARGS: missing words")
    K.check(str(VS.rarityArgs(None, None)).startswith("unknown category"), "ARGS: null")

    # ------------------------------------------------------------------ SET + NOLOSS
    fresh()
    U = UUID.fromString("00000000-0000-0000-0000-00000000aa01")
    k = str(U)
    # Mining Lv 10 (25 x 9^2 collected), Foraging Lv 4, the rest Lv 1
    TOT.update({str(U) + "|Mining": 25 * 81, str(U) + "|Foraging": 20 * 9})
    items = {"Rock_Stone_Cobble": 4000, "Ore_Copper": 500, "Wood_Oak_Trunk": 300, "Ingredient_Bone_Fragment": 40}
    with open(os.path.join(base, "pools", k + ".properties"), "w", encoding="latin-1") as f:
        f.write("#SkyySacks pool\n" + "".join("%s=%d\n" % kv for kv in items.items()))
    pool_sha = sha(os.path.join(base, "pools", k + ".properties"))
    s = VS.st(k)
    s.first = 1
    for i in range(6):
        s.rar[i] = 3
    s.omni = True
    K.eq(int(VS.rank(k, 0)), 4, "SET: start = Omni")
    caps0 = VS.capsK(U, k)
    K.eq(int(caps0.get("Mining")), 5000, "SET: Mining Lv 10 x Omni 5 = 5,000 (4,500 stored fits)")
    before = pc(k)
    K.eq(before, items, "SET: the pool loads")
    r = str(VS.setRarity(U, k, -1, 0, "Skyy"))
    K.check(r.startswith("Void rarity set: Mining Normal, Foraging Normal, Farming Normal, Fishing Normal, Combat Normal, Smithing Normal. Before: Mining Omni,"),
            "SET: all Normal (Skyy's test) - reply: %s" % r[:160])
    K.check("Over the space now: Mining 4500 / 1000, Foraging 300 / 400" not in r and "Over the space now: Mining 4500 / 1000" in r
            and "nothing was removed" in r, "SET: the reply names the over-space categories: %s" % r[r.find("Over"):r.find("Over") + 140])
    K.check(not s.omni and [int(x) for x in s.rar] == [0] * 6 and [int(VS.rank(k, i)) for i in range(6)] == [0] * 6, "SET: omni flag off, six Normal")
    K.eq(pc(k), before, "NOLOSS: the pool in memory is unchanged")
    K.eq(int(VS.capsK(U, k).get("Mining")), 1000, "NOLOSS: Mining space is 1,000 now (4,500 stored stay)")
    drain()
    pd = props(os.path.join(base, "pd", k + ".properties"))
    K.eq(([pd.get("rar." + c_) for c_ in CATS], pd.get("omni")), (["0"] * 6, "false"), "SET: pd/<key>.properties saved by the writer")
    K.eq(sha(os.path.join(base, "pools", k + ".properties")), pool_sha, "NOLOSS: pools/<key>.properties is byte-identical")
    restart()
    K.eq(pc(k), before, "NOLOSS: after a restart the pool loads the same items")
    s = VS.st(k)
    K.check(not s.omni and [int(x) for x in s.rar] == [0] * 6, "SET: after a restart the rarity is still six Normal")
    ml = open(os.path.join(base, "migration.log"), encoding="utf8").read()
    K.check("/pdadmin rarity: Mining Omni" in ml and "by Skyy (items stored 4840, unchanged: 4840)" in ml, "SET: migration.log line")
    # one category from Omni: the other five become Legendary
    s.omni = True
    r = str(VS.setRarity(U, k, 0, 2, "Skyy"))
    K.check("(it was Omni: the other categories are Legendary now)" in r and [int(VS.rank(k, i)) for i in range(6)] == [2, 3, 3, 3, 3, 3] and not s.omni,
            "SET: Mining Rare from Omni -> the other five Legendary: %s" % r[:120])
    # one category from plain rarities: only that one changes
    r = str(VS.setRarity(U, k, 4, 1, "Skyy"))
    K.eq([int(VS.rank(k, i)) for i in range(6)], [2, 3, 3, 3, 1, 3], "SET: Combat Unique - only Combat changes")
    # all -> Omni; Omni on one category
    r = str(VS.setRarity(U, k, -1, 4, "Skyy"))
    K.check(s.omni and [int(VS.rank(k, i)) for i in range(6)] == [4] * 6 and "Every stored item still fits." in r, "SET: all Omni: %s" % r[-60:])
    s.omni = False
    r = str(VS.setRarity(U, k, 3, 4, "Skyy"))
    K.check(s.omni and "(Omni is the whole Void - all six categories)" in r, "SET: Omni on one category = the whole Void")
    # pd.omniAuto: all six Legendary is Omni anyway
    Cfg.PD_OMNI_AUTO = True
    VS.setRarity(U, k, -1, 3, "Skyy")
    r = str(VS.setRarity(U, k, 0, 3, "Skyy"))
    K.check("It is STILL Omni: all six are Legendary and Server Setup gives Omni automatically (pd.omniAuto)." in r, "SET: the omniAuto note")
    Cfg.PD_OMNI_AUTO = False
    r = str(VS.setRarity(U, k, 0, 3, "Skyy"))
    K.check("STILL Omni" not in r and int(VS.rank(k, 0)) == 3, "SET: omniAuto off -> Legendary")
    Cfg.PD_OMNI_AUTO = True
    # a bag conversion still settling (an R journal entry of a Legendary Mining bag)
    e = JArray(JClass("java.lang.Object"))([JString("9"), JString("Skyy_Sack_Mining_Large"), JClass("java.lang.Integer")(1),
                                            JClass("java.lang.Integer")(0), JString("R"), Long_(System.currentTimeMillis()), JString(""), JString(k)])
    VS.pendAdd(k, e)
    r = str(VS.setRarity(U, k, 0, 0, "Skyy"))
    K.check("A bag conversion still settling raises Mining again within 30 s." in r, "SET: the settling note: %s" % r[-120:])
    VS.pendRemove(k, e)
    VS.setRarity(U, k, -1, 0, "Skyy")
    # NOREAD
    VS.BAD.put("nokey", Long_(System.currentTimeMillis()))
    K.eq(str(VS.setRarity(U, "nokey", -1, 0, "Skyy")), str(VS.NOREAD), "SET: an unreadable Void -> NOREAD, nothing changed")
    K.eq(str(VS.setRarity(U, k, 6, 0, "Skyy")), "unknown category or rarity", "SET: a bad index")
    K.eq(str(VS.setRarity(U, k, -1, 5, "Skyy")), "unknown category or rarity", "SET: a bad rarity")
    K.eq(pc(k), before, "NOLOSS: the pool after every change")
    drain()
    K.eq(sha(os.path.join(base, "pools", k + ".properties")), pool_sha, "NOLOSS: pools/<key>.properties still byte-identical")
    cl = open(os.path.join(base, "crafts.log"), encoding="utf8").read() if os.path.isfile(os.path.join(base, "crafts.log")) else ""
    K.notes.append("SET: crafts.log %s" % ("has VOID-RARITY lines" if "VOID-RARITY" in cl else "(written later by its own flush)"))

    # ------------------------------------------------------------------ NOLOSS: the REAL sweep after lowering
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    jp.appendClassPath(jar)
    CtF, CtM, CtC = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyTestFakeStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fake.addConstructor(CtC.make("public SkyyTestFakeStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
    store = us.allocateInstance(fake.toClass(AS.class_))
    fm = AS.class_.getDeclaredField("assetMap")
    fm.setAccessible(True)
    DAMN = "com.hypixel.hytale.assetstore.map.DefaultAssetMap"
    kmap = jp.makeClass("com.hypixel.hytale.assetstore.map.SkyyTestKnownMap", jp.get(DAMN))
    kmap.addField(CtF.make("public static final java.util.HashMap CUSTOM = new java.util.HashMap();", kmap))
    kmap.addConstructor(CtC.make("public SkyyTestKnownMap() { super(); }", kmap))
    kmap.addMethod(CtM.make("public com.hypixel.hytale.assetstore.JsonAsset getAsset(Object key) { if (key != null && CUSTOM.containsKey(key)) "
                            "return (com.hypixel.hytale.assetstore.JsonAsset) CUSTOM.get(key); return super.getAsset(key); }", kmap))
    KMap = JClass(kmap.toClass(JClass(DAMN).class_))
    fm.set(store, KMap())
    ItemC = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    fi_ = ItemC.class_.getDeclaredField("ASSET_STORE")
    fi_.setAccessible(True)
    fi_.set(None, store)

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
    for iid in list(items) + ["Plant_Crop_Wheat_Item"]:
        it_ = ItemC(JString(iid))
        jfield(ItemC.class_, "maxStack").setInt(it_, 100)
        KMap.CUSTOM.put(JString(iid), it_)
    INVN = "com.hypixel.hytale.server.core.inventory.Inventory"
    ICN = "com.hypixel.hytale.server.core.inventory.container.ItemContainer"
    tinv = jp.makeClass("com.hypixel.hytale.server.core.inventory.SkyyTestInv", jp.get(INVN))
    for f in ("s", "h", "b"):
        tinv.addField(CtF.make("public %s %s;" % (ICN, f), tinv))
    tinv.addConstructor(CtC.make("public SkyyTestInv(%s s, %s h, %s b) { super(); this.s = s; this.h = h; this.b = b; }" % (ICN, ICN, ICN), tinv))
    for m, f in (("getStorage", "s"), ("getHotbar", "h"), ("getBackpack", "b")):
        tinv.addMethod(CtM.make("public %s %s() { return this.%s; }" % (ICN, m, f), tinv))
    TInv = JClass(tinv.toClass(JClass(INVN).class_))
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")

    def player(storage):
        s_, h_, b_ = SIC(JShort(36)), SIC(JShort(9)), SIC(JShort(9))
        for iid, q in storage:
            K.check(bool(s_.addItemStack(IS(iid, q)).succeeded()), "NOLOSS: stand-in inventory takes %s x%d" % (iid, q))
        p_ = us.allocateInstance(PLA.class_)
        jfield(PLA.class_, "inventory").set(p_, TInv(s_, h_, b_))
        return p_

    def inv_counts(p_):
        o = {}
        st_ = p_.getInventory().getStorage()
        for i in range(int(st_.getCapacity())):
            it_ = st_.getItemStack(JShort(i))
            if it_ is not None and not it_.isEmpty():
                o[str(it_.getItemId())] = o.get(str(it_.getItemId()), 0) + int(it_.getQuantity())
        return o
    P = player([("Rock_Stone_Cobble", 100), ("Ore_Copper", 50), ("Plant_Crop_Wheat_Item", 60)])
    inv0, pool0 = inv_counts(P), pc(k)
    moved = int(Swp.sweep(P, k, None, True, None, VS.capsK(U, k), None))
    inv1, pool1 = inv_counts(P), pc(k)
    K.eq((inv1.get("Rock_Stone_Cobble"), inv1.get("Ore_Copper")), (100, 50), "NOLOSS: the over-space Mining takes nothing from the inventory")
    K.eq((pool1.get("Rock_Stone_Cobble"), pool1.get("Ore_Copper")), (4000, 500), "NOLOSS: ... and nothing leaves the Void")
    K.eq((moved, inv1.get("Plant_Crop_Wheat_Item", 0), pool1.get("Plant_Crop_Wheat_Item")), (60, 0, 60), "NOLOSS: Farming (room 100) still takes the wheat")
    tot = lambda a, b: dict((x, a.get(x, 0) + b.get(x, 0)) for x in set(a) | set(b))
    K.eq(tot(inv1, pool1), tot(inv0, pool0), "NOLOSS: inventory + Void totals are conserved")

    # ------------------------------------------------------------------ TASK: VoidAdminTask.answer
    p_any = us.allocateInstance(PLA.class_)
    r = str(VAT.answer(4, p_any, k, U, 1, 2, "Admin"))
    K.check(r.startswith("Void rarity set: Mining Normal, Foraging Rare,"), "TASK: mode 4 = setRarity (%s)" % r[:80])
    K.eq(str(VAT.answer(4, None, k, U, 1, 2, "Admin")), "that player is not in a world right now", "TASK: no Player component")
    K.eq(str(VAT.answer(4, p_any, None, U, 1, 2, "Admin")), "that player's profile is loading or switching - try again in a few seconds", "TASK: no settled key")
    K.check(str(VAT.answer(2, p_any, k, U, 0, 0, "Admin")).startswith("Omni granted"), "TASK: mode 2 = /pdadmin omni (unchanged)")
    K.check(len(str(VAT.answer(3, p_any, k, U, 0, 0, "Admin"))) > 0, "TASK: mode 3 = /pdadmin resume (unchanged)")
    t = VAT(4, None, None)
    t.ci, t.rar = 2, 1
    K.eq((int(t.mode), int(t.ci), int(t.rar)), (4, 2, 1), "TASK: the task carries the category + rarity")
    K.eq(pc(k), tot(pool1, {}), "NOLOSS: the pool after the task answers")
    drain()
    Pool.WRITER.shutdownNow()     # the writer thread is not a daemon: the child JVM must be able to exit
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
                m = SP.pool(k)
                got[k] = dict((str(e.getKey()), int(e.getValue().longValue())) for e in m.entrySet())
            if seen is None:
                seen = got
            K.check(got == seen, "D start %d %s: every pool loads the same items" % (start, os.path.basename(j)))
    K.eq(HK.tree_hash(home), before, "D the live copy's bytes are unchanged by the starts")
    # every live Void -> all Normal (= /pdadmin rarity <you> all Normal), on the copy
    L = loader_for(jar)
    c = lambda n: JClass(PKG + n, loader=L)
    SP, VS = c("SackPool"), c("VoidStore")
    System = JClass("java.lang.System")
    System.getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    SP.DIR, VS.DIR = P.get(pools), P.get(os.path.join(home, "pd"))
    VS.HDIR, VS.MIGLOG = P.get(os.path.join(home, "history")), P.get(os.path.join(home, "migration.log"))
    c("CraftLog").FILE = P.get(os.path.join(home, "crafts.log"))
    SP.WRITER = JClass("java.util.concurrent.Executors").newSingleThreadScheduledExecutor()
    pdk = sorted(f[:-11] for f in os.listdir(os.path.join(home, "pd")) if f.endswith(".properties")) if os.path.isdir(os.path.join(home, "pd")) else []
    pool_sha = dict((k, sha(os.path.join(pools, k + ".properties"))) for k in keys)
    pd_before = dict((k, props(os.path.join(home, "pd", k + ".properties"))) for k in pdk)
    replies = []
    for k in pdk:
        u = JClass("java.util.UUID").fromString(k[:36])
        replies.append(str(VS.setRarity(u, k, -1, 0, "harness"))[:90])
    SP.WRITER.submit(JClass("java.util.concurrent.Executors").callable(JClass("java.lang.Thread")())).get()
    for k in keys:
        K.eq(sha(os.path.join(pools, k + ".properties")), pool_sha[k], "D live %s: pool file byte-identical after the rarity change" % k[-12:])
    for k in pdk:
        a = props(os.path.join(home, "pd", k + ".properties"))
        want = dict(pd_before[k])
        want.update(dict(("rar." + c_, "0") for c_ in CATS))
        want["omni"] = "false"
        K.eq(a, want, "D live %s: pd file = before + six rar 0 + omni=false (was omni=%s)" % (k[-12:], pd_before[k].get("omni")))
    SP2 = JClass(PKG + "SackPool", loader=loader_for(jar))
    SP2.DIR = P.get(pools)
    got = dict((k, dict((str(e.getKey()), int(e.getValue().longValue())) for e in SP2.pool(k).entrySet())) for k in keys)
    K.check(got == seen, "D live: after the change + a restart every pool loads exactly the same items")
    K.notes.append("D: %d profile pools (%d item lines, %d items), %d Voids set to Normal: %s" % (
        len(keys), sum(len(v) for v in (seen or {}).values()), sum(sum(v.values()) for v in (seen or {}).values()), len(pdk), replies))
    SP.WRITER.shutdownNow()
    K.save()


HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("exec", run_exec), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyySacks"))
