"""Harness for SkyyShards 0.2 (0.1 + phase 6 TOTEMS + the Rebirth R9 shard crafting gate). Build first: python SkyyShards/build_skyyshards_0.2.py

    python SkyyShards/test_skyyshards_0.2.py [--keep]

0.2 adds X16 (every new code path): the totem defaults, entry parsing (a 0.1 "harvest_spirit:1" = Harvest Spirit I), crops in range = the
island geometry, RATE MATH vs RANGE (18 cases), boosters split the settle (600 random sequences conserve items), Harvest Moon chance / Rare
Finder / Moon Blade / seeded rolls, Storage modifiers, the pad layout + nearest totem + the totem block guard, place / pick up on real
containers (PICK UP RETURNS THE EXACT DOCUMENT; refused saves give / take the same uid back; pads full; a Mining totem refused), modifiers,
booster, range circle, Upgrade (gear:fn:anvil:open), Collect of Enchanted crops (x 100), crafting (refunds, no room) + the REBIRTH R9 GATE
(rebirth:fn:count: none / loading / 1 refused, 2 crafts), shard:fn:totem (key / cost / up / describe / refusals), the Totems + Craft tabs
(builds, packets, every new click). X1 / X3 / X5 / X13 / X15 follow 0.2's numbers (no island size factor; 5 tabs).

Phases (each a fresh child JVM, the game's JRE, TEMP / TMP in scratch; tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all on the 0.7 server jar
  C  compare  a new mod: the jar against itself (nothing to compare; kept so the kit's phases all run)
  X  exec     EVERY NEW CODE PATH in a bare JVM (-Xverify:all):
              config (first start writes the defaults, a second start writes nothing, clamps), store (keys, read, save, an unreadable
              file is never overwritten, a refused write), production maths (starter island, settle, the part-item carry, cap = full stops,
              the 3-day offline cap, size factors, no totem = nothing, 2,000 random settle sequences conserve items exactly), the region
              layout (hub + stand, bridges, Small / Medium / Large grow in place = supersets, inside the loaded chunks, no slot overlap),
              protection matrix (shard:fn:allowed every action x block kind, non-shard worlds untouched), roles (owner / co-op / admin /
              visitor, island:shardguard), inventory give / take / count on real SimpleItemContainers (a stand-in Item store),
              COLLECT CONSERVATION (items before / after = given; stored before - after = given; what did not fit is back; the file is
              debited first; a refused write takes nothing; XP and collection credit; a refused collection source waits in the
              collector's file and is paid later; profile switch = the collector's current profile), storage upgrade (items taken
              first, coins after, items back when the coins fail), grow (collection tier, seeds, coins), placement rules + the 1 s
              block check, the world cap + queue + idle unload, the page (every tab / view / slot built into a real CustomPage packet,
              every click), the bridge Functions, /shardadmin text
  D  live     START TWICE on a scratch COPY of the live mods folder (Skyy_SkyyIslands copied; Skyy_SkyyShards is new): the first start
              writes only Skyy_SkyyShards/config.properties, the second writes nothing; the copied island files byte-identical
  AA engine-access audit
REVIEW FIXES (shards01fix) each have an X check marked "fix:": role re-check on every action (mayBeIn / mayManage, shard.coopCollect),
a deleted / archived owner profile closed to co-op (profile:fn:state), the reset-island portal (island:world:key:fn: stale record dropped,
no placing in a backup world, Pick up from the menu, Enter / Back refuse the old world), Enter needs a placed shard, a picked-up shard is
paused (no production), refunds on a refused save (buy storage / grow), owed Farming XP, at most 2 unloads a tick, Pick up only for the owner.
REVIEW FIXES 2 (shards01fix2) are checked in X15 ("fix2:"): the world template's Death rule (no item loss), totem.particle checked before it
reaches clients, island:fn:hub first (the /sethub hub), profile:busy refuses Collect / buy / Grow / Pick up with nothing moved, lastCollect
written, a stale (reset-island) record pauses production at the first look, owed XP / counts kept in memory when the collector file cannot
be read, Pick up refuses an unloaded portal spot, the placement check retries an unloaded chunk (10 tries, never overwrites a newer one).
Scratch: tools/dev/scratch/shards01/h (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, random, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyui as SUI

VERSION = "0.2"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)))
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "shards02", "h")))
PKG = "com.skyy.shards."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods")
OWNER = "0f0f0f0f-1111-2222-3333-444444444444"
MEMBER = "0e0e0e0e-1111-2222-3333-555555555555"
VISITOR = "0d0d0d0d-1111-2222-3333-666666666666"
ADMIN = "0c0c0c0c-1111-2222-3333-777777777777"


def fn_class():
    from jpype import JImplements, JOverride

    @JImplements("java.util.function.Function")
    class PyFn(object):
        def __init__(self, ans):
            self.ans = ans
            self.calls = []

        @JOverride
        def apply(self, a):
            self.calls.append(a)
            return self.ans(a)
    return PyFn


def unsafe():
    from jpype import JClass
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    return uf.get(None)


def setf(obj, k, name, val):
    while k is not None:
        try:
            f = k.getDeclaredField(name)
            f.setAccessible(True)
            f.set(obj, val)
            return True
        except Exception:
            k = k.getSuperclass()
    return False


def item_store(ids):
    """a bare JVM has no Item asset store: an empty one with these ids (the SkyyQuests 0.2 / SkyyHud harness pattern)"""
    from jpype import JClass
    U = unsafe()
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyShTestStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fake.addConstructor(JClass("javassist.CtNewConstructor").make(
        "public SkyyShTestStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
    store = U.allocateInstance(fake.toClass(AS.class_))
    amap = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")()
    fa = AS.class_.getDeclaredField("assetMap")
    fa.setAccessible(True)
    fa.set(store, amap)
    ItemC = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    fs = ItemC.class_.getDeclaredField("ASSET_STORE")
    fs.setAccessible(True)
    fs.set(None, store)
    mf = amap.getClass().getDeclaredField("assetMap")
    mf.setAccessible(True)
    for iid, mx in ids:
        it_ = U.allocateInstance(ItemC.class_)
        setf(it_, ItemC.class_, "maxStack", JClass("java.lang.Integer")(mx).intValue())
        setf(it_, ItemC.class_, "id", iid)
        mf.get(amap).put(iid, it_)


# ====================================================================================================== X: every new code path
def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray, JLong, JInt, JString, JObject
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    Sys = JClass("java.lang.System")
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    Sys.getProperties().put("skyy.bridge", br)
    P = lambda n: JClass(PKG + n)
    Cfg, St, Mth, Geo, Gate, Role, Inv, Pay, Core, Wld, Place, Page, Fn, Adm, W2 = (P(n) for n in (
        "ShCfg", "ShStore", "ShMath", "ShGeo", "ShGate", "ShRole", "ShInv", "ShPay", "ShCore", "ShWorlds", "ShPlace", "ShPage", "ShFn",
        "ShAdmin", "ShWorld2"))
    Paths, UUID, Props = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("java.util.Properties")
    PyFn = fn_class()
    base = os.path.join(scratch, "x")
    os.makedirs(base, exist_ok=True)
    ou, mu, vu, au = UUID.fromString(OWNER), UUID.fromString(MEMBER), UUID.fromString(VISITOR), UUID.fromString(ADMIN)

    # ---------------- X1 config
    Cfg.DIR = Paths.get(base)
    Cfg.FILE = Paths.get(os.path.join(base, "config.properties"))
    r1 = str(Cfg.loadCfg(True))
    txt = open(os.path.join(base, "config.properties"), encoding="utf-8").read()
    K.check(r1.startswith("default config.properties written") and txt == str(Cfg.DEFAULT_TEXT), "X1 first start writes the default config")
    K.check(bool(Cfg.ON) and int(Cfg.MAX_LOADED) == 20 and int(Cfg.UNLOAD_SEC) == 120 and int(Cfg.MAX_OFF_SEC) == 259200 and int(Cfg.XP_PCT) == 50
            and float(Cfg.RATE1) == 1.0 and list(Cfg.RATES)[0] == 1.0 and int(Cfg.ST5) == 24 and int(Cfg.SC2) == 5000
            and int(Cfg.SE5) == 64 and int(Cfg.GM_SEEDS) == 8 and int(Cfg.GL_COLL) == 6 and str(Cfg.PARTICLE) == "Dust_Sparkles_Fine",
            "X1 defaults (shards ON for the test world, cap 20, unload 120 s, 3 days, 50 %%, rates, ladders)")
    K.check(not bool(Cfg.COOP_COLLECT) and "shard.coopCollect=false" in txt, "X1 fix: shard.coopCollect defaults off (co-op may enter, not collect / upgrade)")
    m0 = os.path.getmtime(os.path.join(base, "config.properties"))
    r2 = str(Cfg.loadCfg(True))
    K.check(not r2.startswith("default") and os.path.getmtime(os.path.join(base, "config.properties")) == m0, "X1 a second start writes nothing")
    open(os.path.join(base, "config.properties"), "a", encoding="utf-8").write("\nshard.maxLoaded=99999\nshard.xpPercent=-5\nshards.on=off\n")
    Cfg.loadCfg(False)
    K.check(int(Cfg.MAX_LOADED) == 500 and int(Cfg.XP_PCT) == 0 and not bool(Cfg.ON), "X1 hand edits are clamped (500, 0) and off is read")
    open(os.path.join(base, "config.properties"), "w", encoding="utf-8").write(str(Cfg.DEFAULT_TEXT))
    Cfg.loadCfg(False)
    K.eq([int(Cfg.stacks(i)) for i in range(0, 7)], [1, 1, 3, 6, 12, 24, 24], "X1 stacks per tier")
    K.eq([int(Cfg.storeCoins(i)) for i in range(1, 6)], [0, 5000, 25000, 100000, 400000], "X1 storage coins")
    K.eq([int(Cfg.storeEnch(i)) for i in range(1, 6)], [0, 1, 4, 16, 64], "X1 storage Enchanted Wheat")
    K.eq([str(Cfg.num(JLong(n))) for n in (0, 999, 1000, 1234567, -2500)], ["0", "999", "1,000", "1,234,567", "-2,500"], "X1 num()")
    K.eq([str(Cfg.dec(x)) for x in (1.0, 1.6, 2.45, 0.125)], ["1", "1.6", "2.45", "0.13"], "X1 dec()")

    # ---------------- X2 store
    sd = os.path.join(base, "shards")
    St.DIR = Paths.get(sd)
    K.check(bool(St.validKey(OWNER)) and bool(St.validKey(OWNER + "-p3")) and not St.validKey("../x") and not St.validKey(None)
            and not St.validKey(OWNER + "-p99999"), "X2 validKey: uuid and uuid-pN only")
    p = St.get(OWNER)
    K.check(p is not None and p.size() == 1 and str(p.getProperty("pkey")) == OWNER and Sys.identityHashCode(St.get(OWNER)) == Sys.identityHashCode(p),
            "X2 a missing file = an empty profile (0.2: it knows its key), cached")
    p.setProperty("v", "1")
    K.check(St.save(OWNER, p) is None and os.path.isfile(os.path.join(sd, OWNER + ".properties")) and int(St.WRITES.get()) == 1, "X2 save writes the file")
    bad = "0b0b0b0b-1111-2222-3333-888888888888"
    os.makedirs(os.path.join(sd, bad + ".properties"))          # a directory in place of the file = unreadable
    K.check(St.get(bad) is None and St.BAD.containsKey(bad), "X2 an unreadable file -> no profile, marked BAD")
    K.check("not overwritten" in str(St.save(bad, Props())), "X2 an unreadable file is never overwritten")
    K.check(St.save("nope", Props()) is not None, "X2 a bad key is refused")
    St.FAIL_TEST = True
    K.check("refused" in str(St.save(OWNER, p)), "X2 a refused write is reported")
    St.FAIL_TEST = False
    K.eq((int(St.lng(p, "v", JLong(7))), int(St.lng(p, "zz", JLong(7))), int(St.intv(p, "v", 3, 2, 9)), str(St.str(p, "none"))), (1, 7, 2, ""),
         "X2 lng / intv clamp / str")
    St.log("harness line")
    K.check("harness line" in open(os.path.join(base, "collect.log"), encoding="utf-8").read(), "X2 collect.log")

    # ---------------- X3 production maths
    T0 = 1790000000000
    q = Props()
    Mth.starter(q, JLong(T0))
    K.check(str(q.getProperty("farming.i0.type")) == "wheat" and int(Mth.size(q, 0)) == 1 and str(q.getProperty("farming.i0.totems")) == "harvest_spirit:1"
            and int(Mth.storageTier(q)) == 1 and int(Mth.cap(q)) == 100 and not Mth.hasIsland(q, 1), "X3 starter: Wheat Small + one Harvest Spirit I, storage tier 1 (100)")
    q2 = Props(); q2.putAll(q); q2.setProperty("farming.i0.type", "wheat"); Mth.starter(q2, JLong(T0 + 5))
    K.check(str(q2.getProperty("farming.i0.last")) == str(T0), "X3 starter never touches an existing island")
    K.eq(float(Mth.rate(q, 0, JLong(T0))), 1.0, "X3 rate Small = 1 / min")
    K.eq(int(Mth.settle(q, 0, JLong(T0 + 60000))), 1, "X3 settle +60 s = 1 item")
    K.eq(int(Mth.settle(q, 0, JLong(T0 + 90000))), 0, "X3 settle +30 s more = 0 (the half item waits)")
    K.eq(int(Mth.settle(q, 0, JLong(T0 + 120000))), 1, "X3 settle +30 s more = the waiting item")
    K.eq(int(Mth.stored(q, 0)), 2, "X3 stored = 2")
    K.eq(int(Mth.settle(q, 0, JLong(T0 + 120000 + 200 * 60000))), 98, "X3 200 minutes later the store is full at 100 (only 98 more)")
    K.eq((int(Mth.stored(q, 0)), str(q.getProperty("farming.i0.last"))), (100, str(T0 + 120000 + 200 * 60000)), "X3 full: last = now (production stops)")
    K.eq(int(Mth.settle(q, 0, JLong(T0 + 500 * 60000))), 0, "X3 a full store makes nothing")
    K.eq(int(Mth.msToFull(q, 0, JLong(T0))), -1, "X3 msToFull of a full store = -1")
    q.setProperty("farming.i0.stored", "0"); q.setProperty("farming.i0.last", str(T0))
    q.setProperty("farming.storage", "5")
    _rt = Cfg.RATES
    _rt[0] = 0.1
    K.eq(int(Mth.settle(q, 0, JLong(T0 + 10 * 86400000))), 432, "X3 10 days away = at most 3 days counted (0.1 / min -> 432)")
    _rt[0] = 1.0
    q.setProperty("farming.i0.size", "2"); K.check(abs(float(Mth.rate(q, 0, JLong(T0))) - 1.0) < 1e-9, "X3 0.2: Medium with a Harvest Spirit I = 1 (its range reaches the same 20 crops)")
    q.setProperty("farming.i0.size", "3"); K.check(abs(float(Mth.rate(q, 0, JLong(T0))) - 1.0) < 1e-9, "X3 0.2: Large with a Harvest Spirit I = 1")
    q.setProperty("farming.i0.totems", "")
    lst = str(q.getProperty("farming.i0.last"))
    K.check(int(Mth.settle(q, 0, JLong(T0 + 11 * 86400000))) == 0 and str(q.getProperty("farming.i0.last")) == str(T0 + 11 * 86400000), "X3 no totem = nothing made, last moves on")
    K.eq(int(Mth.totems(q, 0)), 0, "X3 totems() of an empty list")
    K.eq([str(Mth.fmtMs(JLong(x))) for x in (-1, 1, 59 * 60000, 61 * 60000, 49 * 3600000)], ["-", "1 m", "59 m", "1 h 1 m", "2 d 1 h"], "X3 fmtMs")
    # conservation: random settle times never make more (or fewer) items than the elapsed time allows
    rnd = random.Random(14)
    worst = 0
    for case in range(2000):
        r = Props()
        Mth.starter(r, JLong(T0))
        r.setProperty("farming.storage", "5")
        r.setProperty("farming.i0.size", str(rnd.choice((1, 2, 3))))
        rate = float(Mth.rate(r, 0, JLong(T0)))
        t = T0
        made = 0
        for step in range(rnd.randint(1, 30)):
            t += rnd.randint(0, 9 * 60000)
            made += int(Mth.settle(r, 0, JLong(t)))
        cap = int(Mth.cap(r))
        expect = min(cap, int((t - T0) * rate / 60000.0))
        worst = max(worst, abs(made - expect))
        if int(Mth.stored(r, 0)) != made:
            worst = 999
    K.check(worst <= 1, "X3 2,000 random settle sequences: items made = floor(elapsed x rate) (off by %d at most; stored = made)" % worst)

    # ---------------- X4 region layout
    def blocks(pp):
        lst_ = Geo.region(pp)
        return [tuple(int(v) for v in lst_.get(i)) for i in range(lst_.size())]
    r = Props(); Mth.starter(r, JLong(T0))
    bl = blocks(r)
    ids = list(Geo.IDS)
    OX, OZ, Y = int(Geo.OX), int(Geo.OZ), int(Geo.Y)
    K.check((OX, Y + 1, OZ - 3, int(Geo.STAND)) in bl and str(ids[int(Geo.STAND)]) == "Skyy_Shard_Farming", "X4 the hub stand = the shard block at (0, -3)")
    K.check((OX, Y, OZ + 3, int(Geo.BRICK)) in bl, "X4 the arrival point stands on the hub plaza")
    chunks = set(zip([int(x) for x in Geo.CX], [int(z) for z in Geo.CZ]))
    allin = True
    for size in (1, 2, 3):
        for slot in range(6):
            r.setProperty("farming.i%d.type" % slot, "wheat"); r.setProperty("farming.i%d.size" % slot, str(size))
        for (x, y, z, k) in blocks(r):
            if (x >> 5, z >> 5) not in chunks or not (96 <= y <= 127):
                allin = False
    K.check(allin, "X4 every block of 6 Large islands + bridges lies in the loaded chunks, section y 96-127")

    def island(slot, size):
        L = JClass("java.util.ArrayList")()
        Geo.island(L, slot, size)
        return set((int(L.get(i)[0]), int(L.get(i)[1]), int(L.get(i)[2])) for i in range(L.size()))
    for slot in range(6):
        s1, s2, s3 = island(slot, 1), island(slot, 2), island(slot, 3)
        K.check(s1 < s2 < s3, "X4 slot %d grows in place: Small (%d) in Medium (%d) in Large (%d)" % (slot + 1, len(s1), len(s2), len(s3)))
    foot = [set((x, z) for (x, y, z) in island(s, 3)) for s in range(6)]
    K.check(all(not (foot[a] & foot[b]) for a in range(6) for b in range(a + 1, 6)), "X4 no two Large islands overlap")
    hub = JClass("java.util.ArrayList")(); Geo.hub(hub)
    hubxz = set((int(hub.get(i)[0]), int(hub.get(i)[2])) for i in range(hub.size()))
    for slot in range(6):
        br_ = JClass("java.util.ArrayList")(); Geo.bridge(br_, slot)
        bxz = set((int(br_.get(i)[0]), int(br_.get(i)[2])) for i in range(br_.size()))
        small = set((x, z) for (x, y, z) in island(slot, 1))
        K.check(bool(bxz & hubxz) and bool(bxz & small) and len(bxz) >= 3 * 30, "X4 slot %d bridge touches the hub and the Small island (%d planks)" % (slot + 1, len(bxz)))
    w1 = blocks(r)
    crops = [b for b in w1 if b[3] == int(Geo.CROP)]
    tills = set((b[0], b[2]) for b in w1 if b[3] == int(Geo.TILL))
    K.check(all((c[0], c[2]) in tills and c[1] == Y + 1 for c in crops) and len(crops) > 0, "X4 every crop sits on tilled soil (%d crops)" % len(crops))
    cl_ = Geo.crops(r)
    cset = [tuple(int(v) for v in cl_.get(i)) for i in range(cl_.size())]
    K.check(len(cset) == len(crops) and all(c in w1 for c in cset) and all(c[3] == int(Geo.CROP) for c in cset),
            "X4 the periodic regrow list = exactly the crops of the region (%d)" % len(cset))
    t1 = JArray(JClass("double"))(Geo.totemSpot(0))
    K.check(abs(t1[0] - (OX + int(Geo.SX[0]) + 0.5)) < 1e-9 and t1[1] > Y + 2, "X4 totem particles above the slot 1 pillar")

    # ---------------- X5 protection matrix (shard:fn:allowed)
    g = Gate()
    W = "skyy-shard-" + OWNER
    blocks_ = {"crop": "Plant_Crop_Wheat_Block_Eternal", "cropState": "*Plant_Crop_Wheat_Block_Eternal_State_Definitions_StageFinal",
               "soil": "Soil_Dirt_Tilled", "grass": "Soil_Grass", "stand": "Skyy_Shard_Farming", "plank": "Wood_Softwood_Planks", "none": "",
               "totem": "Skyy_TotemBlock_HarvestSpirit"}
    want = {"damage": {"crop", "cropState"}, "break": {"crop", "cropState"}, "use": {"crop", "cropState", "stand", "totem"},
            "pickup": set(blocks_), "drop": set(blocks_), "place": set(), "useentity": set(), "hurt": set(), "other": set(), "": set()}
    wrong = []
    for a_, ok in want.items():
        for bk, bid in blocks_.items():
            got = g.apply(JArray(JObject)([JString(W), JString(a_), JString(bid), ou]))
            if bool(got) != (bk in ok):
                wrong.append((a_, bk, got))
    K.check(not wrong, "X5 the protection matrix: %d actions x %d block kinds (crops harvest / break / damage / use, the stand = menu, pickup + drop ok, everything else refused) %s" % (len(want), len(blocks_), wrong[:4]))
    K.check(g.apply(JArray(JObject)([JString("skyy-island-" + OWNER), JString("break"), JString("Soil_Grass"), ou])) is None
            and g.apply(JArray(JObject)([JString("default"), JString("place"), JString(""), ou])) is None, "X5 non-shard worlds: null (not ours)")
    K.check(g.apply("x") is None and g.apply(JArray(JObject)([JString(W)])) is None, "X5 bad arguments: null")
    K.check(int(Gate.ASKED.get()) >= len(want) * len(blocks_), "X5 every shard question counted")

    # ---------------- X6 roles
    roles = {OWNER: "owner", MEMBER: "member", VISITOR: "visitor", ADMIN: "visitor"}
    Role.ROLEKEY_TEST = PyFn(lambda a: roles.get(str(a[0])) if str(a[1]) == OWNER else None)
    Role.ROLE_TEST = PyFn(lambda a: roles.get(str(a[0])) if str(a[1]) == "skyy-island-" + OWNER else None)
    Role.OWNER_TEST = PyFn(lambda w: OWNER if str(w) == "skyy-island-" + OWNER else None)
    Cfg.PERM_TEST = PyFn(lambda u: str(u) == ADMIN)
    K.eq([bool(Role.mayBeIn(u, OWNER)) for u in (ou, mu, vu, au)], [True, True, False, True], "X6 mayBeIn: owner, co-op member, admin yes; visitor no")
    K.eq([bool(Role.coop(x)) for x in ("owner", "admin", "member", "trusted", "visitor", None)], [True, True, True, False, False, False], "X6 coop words")
    K.eq((str(Role.islandOwner("skyy-island-" + OWNER)), Role.islandOwner("hub")), (OWNER, None), "X6 island owner via island:owner:fn")
    # fix: a deleted (pending) / archived owner profile is closed to co-op (owner profile + server admin still pass)
    pstate = {"s": "pending"}
    Role.STATE_TEST = PyFn(lambda k: JString(pstate["s"]) if str(k) == OWNER else None)
    K.eq([bool(Role.mayBeIn(u, OWNER)) for u in (ou, mu, vu, au)], [True, False, False, True], "X6 fix: owner profile pending -> co-op member refused (owner / admin yes)")
    pstate["s"] = "archived"
    K.check(not Role.mayBeIn(mu, OWNER) and bool(Role.closed(OWNER)), "X6 fix: archived -> closed")
    pstate["s"] = "active"
    K.check(bool(Role.mayBeIn(mu, OWNER)) and not Role.closed(OWNER), "X6 fix: active -> co-op member back in")
    Role.STATE_TEST = None
    K.check(not Role.closed(OWNER), "X6 fix: no SkyyProfiles (no profile:fn:state) = open")
    # fix: Collect / buy / Grow = the owner profile; co-op only with shard.coopCollect
    K.eq([bool(Role.mayManage(u, OWNER)) for u in (ou, mu, vu, au)], [True, False, False, False], "X6 fix: mayManage with coopCollect off: owner only")
    Cfg.COOP_COLLECT = True
    K.eq([bool(Role.mayManage(u, OWNER)) for u in (ou, mu, vu, au)], [True, True, False, False], "X6 fix: mayManage with coopCollect on: owner + co-op")
    Cfg.COOP_COLLECT = False
    # fix: a placed record is stale when its world is not the owner's current island (a reset keeps the old world as a backup)
    Role.WORLDKEY_TEST = PyFn(lambda k: JString("skyy-island-" + OWNER + "-r2") if str(k) == OWNER else None)
    K.eq((bool(Role.stale("skyy-island-%s|1|2|3" % OWNER, OWNER)), bool(Role.stale("skyy-island-%s-r2|1|2|3" % OWNER, OWNER)),
          bool(Role.stale("", OWNER)), str(Role.currentWorld(OWNER)), Role.currentWorld(MEMBER)),
         (True, False, False, "skyy-island-" + OWNER + "-r2", None), "X6 fix: stale = placed world is not the current island (island:world:key:fn)")
    Role.WORLDKEY_TEST = None
    Role.WORLD_TEST = PyFn(lambda w: JClass("java.lang.Boolean").FALSE if str(w) == "gone" else JClass("java.lang.Boolean").TRUE)
    K.check(bool(Role.stale("gone|1|2|3", OWNER)) and not Role.stale("there|1|2|3", OWNER), "X6 fix: without the bridge, stale = the world is gone")
    Role.WORLD_TEST = None
    K.check(not Role.guarded(), "X6 no island:shardguard = not guarded")
    br.put("island:shardguard", "1")
    K.check(bool(Role.guarded()), "X6 island:shardguard 1 = guarded")

    # ---------------- X7 inventory on real containers
    try:
        _tot_ids = [("Skyy_Totem_" + x, 1) for x in ("HarvestSpirit", "Rain", "Fertilizer", "SunBlessing", "FairyGrove", "SeasonWard", "Scarecrow", "Pollinator",
                    "HarvestMoon", "Compost", "MushroomShade", "HerdPole", "LumberSpirit", "SapTap", "QuarrySpirit", "AutoSmeltPole", "GeodePole", "SoulCage",
                    "LurePole", "TrophyPole")]
        _mod_ids = [("Skyy_TotemMod_" + x, 16) for x in ("Wider", "Faster", "Replant", "Compost", "Storage", "RareFinder")]
        _ess = [(x, 100) for x in ("Ingredient_Life_Essence", "Ingredient_Water_Essence", "Ingredient_Void_Essence", "Ingredient_Fire_Essence", "Ingredient_Ice_Essence",
                                   "Ingredient_Lightning_Essence", "Wood_Softwood_Planks")]
        item_store([("Plant_Crop_Wheat_Item", 100), ("Skyy_Ench_Wheat", 100), ("Plant_Seeds_Wheat_Eternal", 100), ("Skyy_Shard_Farming", 1), ("Rock_Stone", 100)]
                   + _tot_ids + _mod_ids + _ess)
        SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
        IC = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
        IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")

        def inv(*caps):
            return JArray(IC)([SIC(JClass("java.lang.Short")(c).shortValue()) for c in caps])
        cs = inv(2, 1, 1)
        got = int(Inv.give(cs, "Plant_Crop_Wheat_Item", JLong(250)))
        K.check(got == 250 and int(Inv.countIn(cs[0], "Plant_Crop_Wheat_Item")) == 200 and int(Inv.count(cs, "Plant_Crop_Wheat_Item")) == 250,
                "X7 give 250 in stacks of 100: storage first (200), then the hotbar (50)")
        got2 = int(Inv.give(cs, "Plant_Crop_Wheat_Item", JLong(500)))
        K.check(got2 == 150 and int(Inv.count(cs, "Plant_Crop_Wheat_Item")) == 400, "X7 give into a nearly full inventory = what landed (150 of 500)")
        tk = int(Inv.take(cs, "Plant_Crop_Wheat_Item", JLong(130)))
        K.check(tk == 130 and int(Inv.count(cs, "Plant_Crop_Wheat_Item")) == 270, "X7 take 130 (counted)")
        K.check(int(Inv.take(cs, "Rock_Stone", JLong(5))) == 0 and int(Inv.give(None, "Rock_Stone", JLong(5))) == 0 and int(Inv.count(None, "x")) == 0, "X7 nothing to take / no inventory")
        Page.TEST_INV = inv(3, 1, 1)
        TI = Page.TEST_INV
        INVOK = True
    except Exception as ex:
        K.check(False, "X7 the containers could not run on the stand-in item store: %s" % str(ex)[:300])
        INVOK = False

    # ---------------- X8 COLLECT conservation
    Cfg.KEY_TEST = PyFn(lambda u: str(u))
    St.CACHE.clear()
    T1 = T0 + 50 * 60000
    Core.NOW_TEST = T1
    po = St.get(OWNER)
    po.clear()
    Mth.starter(po, JLong(T0))
    po.setProperty("farming.placed", "skyy-island-%s|3|129|3" % OWNER)
    St.save(OWNER, po)
    coins = {"bal": 1000000}
    xp_calls, coll_calls, take_calls = [], [], []

    def coll_add(a):
        coll_calls.append((str(a[0]), str(a[1]), int(a[2]), str(a[3]), str(a[4])))
        return JClass("java.lang.Boolean").valueOf(collect_ok[0])
    collect_ok = [False]

    def take_coins(a):
        n = int(a[1])
        take_calls.append(n)
        if coins_fail[0] or coins["bal"] < n:
            return JClass("java.lang.Boolean").FALSE
        coins["bal"] -= n
        return JClass("java.lang.Boolean").TRUE
    coins_fail = [False]
    tiers = {"t": 2}
    fns = JClass("java.util.HashMap")()
    xp_ok = [True]
    fns.put("skill:fn:addxp", PyFn(lambda a: (xp_calls.append((str(a[0]), str(a[1]), int(a[2]), str(a[3]), str(a[4]))), JClass("java.lang.Boolean").valueOf(xp_ok[0]))[1]))
    fns.put("coll:fn:add", PyFn(coll_add))
    fns.put("coins:fn:get", PyFn(lambda u: JLong(coins["bal"])))
    fns.put("coins:fn:take", PyFn(take_coins))
    add_calls = []

    def add_coins(a):
        add_calls.append(int(a[1]))
        coins["bal"] += int(a[1])
        return JLong(coins["bal"])
    fns.put("coins:fn:add", PyFn(add_coins))
    fns.put("coll:fn:tier", PyFn(lambda a: JInt(tiers["t"])))
    Pay.TEST_FNS = fns
    if INVOK:
        st0 = int(Mth.stored(po, 0))
        inv0 = int(Inv.count(TI, "Plant_Crop_Wheat_Item"))
        r = str(Core.collect(ou, OWNER, -1, TI))
        pf = St.readNow(OWNER)
        st1 = int(St.lng(pf, "farming.i0.stored", JLong(-1)))
        inv1 = int(Inv.count(TI, "Plant_Crop_Wheat_Item"))
        K.check(r.startswith("+Collected 50 Wheat") and inv1 - inv0 == 50 and st1 == 0, "X8 Collect: 50 made in 50 minutes -> 50 in the inventory, 0 left (file): %s" % r)
        K.eq(xp_calls[-1], (OWNER, "Farming", 100, "shard:farming", OWNER), "X8 Farming XP = 50 x 4 x 50 %% = 100, source shard:farming, expect key")
        K.check(coll_calls and coll_calls[-1] == (OWNER, "Plant_Crop_Wheat_Item", 50, "shard", OWNER), "X8 collection credit asked for 50 (source shard)")
        K.check(int(St.lng(St.get(OWNER), "owed.coll.Plant_Crop_Wheat_Item", JLong(0))) == 50 and "collection count waiting" in r,
                "X8 a refused collection source: 50 wait in the collector's file")
        # the next Collect pays the waiting count first (chunks of 256)
        collect_ok[0] = True
        Core.NOW_TEST = T1 + 300 * 60000          # full again: 100
        n0 = len(coll_calls)
        r2 = str(Core.collect(ou, OWNER, 0, TI))
        K.check(r2.startswith("+Collected 100 Wheat") and [c[2] for c in coll_calls[n0:]] == [150] and St.get(OWNER).getProperty("owed.coll.Plant_Crop_Wheat_Item") is None,
                "X8 the next Collect credits 100 + the 50 waiting (one 150 call), nothing waits any more")
        # a full inventory: what does not fit stays in the shard
        Inv.give(TI, "Rock_Stone", JLong(100000))
        free_ = 0
        for c_ in TI:
            for s_ in range(int(c_.getCapacity())):
                it_ = c_.getItemStack(JClass("java.lang.Short")(s_).shortValue())
                if it_ is not None and not it_.isEmpty() and str(it_.getItemId()) == "Plant_Crop_Wheat_Item":
                    free_ += 100 - int(it_.getQuantity())
        Core.NOW_TEST = T1 + 700 * 60000
        inv0 = int(Inv.count(TI, "Plant_Crop_Wheat_Item"))
        r3 = str(Core.collect(ou, OWNER, -1, TI))
        inv1 = int(Inv.count(TI, "Plant_Crop_Wheat_Item"))
        st3 = int(St.lng(St.readNow(OWNER), "farming.i0.stored", JLong(-1)))
        K.check(inv1 - inv0 == free_ and st3 == 100 - free_ and ("did not fit" in r3 or free_ == 100),
                "X8 a nearly full inventory: %d fit, %d stay in the shard (file), items before / after match: %s" % (free_, 100 - free_, r3))
        # nothing fits at all
        for c_ in TI:
            Inv.give(JArray(JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer"))([c_]), "Plant_Crop_Wheat_Item", JLong(100000))
        before = int(St.lng(St.readNow(OWNER), "farming.i0.stored", JLong(-1)))
        r4 = str(Core.collect(ou, OWNER, -1, TI))
        K.check(r4.startswith("-Your inventory is full") and int(St.lng(St.readNow(OWNER), "farming.i0.stored", JLong(-1))) == before,
                "X8 a full inventory: nothing collected, the shard keeps every item (file)")
        # the debit write refused: nothing taken
        Page.TEST_INV = inv(3, 1, 1); TI = Page.TEST_INV
        St.FAIL_TEST = True
        r5 = str(Core.collect(ou, OWNER, -1, TI))
        St.FAIL_TEST = False
        K.check(r5.startswith("-Collect failed") and int(Inv.count(TI, "Plant_Crop_Wheat_Item")) == 0 and int(Mth.stored(St.get(OWNER), 0)) == before,
                "X8 the debit could not be written: nothing given, memory unchanged")
        # fix: a co-op member may not collect while shard.coopCollect is off; a visitor never (the role is re-checked at every action)
        st_b = int(Mth.stored(St.get(OWNER), 0))
        r6a = str(Core.collect(mu, OWNER, -1, TI))
        r6v = str(Core.collect(vu, OWNER, -1, TI))
        K.check(r6a.startswith("-Only the island owner can collect") and r6v.startswith("-Only the island owner and co-op") and int(Mth.stored(St.get(OWNER), 0)) == st_b,
                "X8 fix: co-op (coopCollect off) and visitor Collect refused, nothing taken: %s / %s" % (r6a, r6v))
        nos = "0b0b0b0b-1111-2222-3333-121212121212"
        K.check(str(Core.collect(UUID.fromString(nos), nos, -1, TI)).startswith("-No Farming Shard yet"), "X8 fix: a profile without a shard cannot collect")
        # a co-op member collects the owner's shard (shard.coopCollect on): items + XP + collections to the MEMBER
        Cfg.COOP_COLLECT = True
        n0 = len(xp_calls)
        r6 = str(Core.collect(mu, OWNER, -1, TI))
        K.check(r6.startswith("+Collected") and xp_calls[n0][0] == MEMBER and xp_calls[n0][4] == MEMBER, "X8 a co-op member's Collect pays the member (coopCollect on)")
        # profile switch: the collector's CURRENT profile key gets the waiting count
        collect_ok[0] = False
        Cfg.KEY_TEST = PyFn(lambda u: str(u) + "-p2")
        Core.NOW_TEST = T1 + 900 * 60000
        Core.collect(ou, OWNER + "-p2", -1, TI) if False else None
        St.get(OWNER).setProperty("farming.i0.stored", "10")
        r7 = str(Core.collect(ou, OWNER, -1, TI))
        K.check(int(St.lng(St.get(OWNER + "-p2"), "owed.coll.Plant_Crop_Wheat_Item", JLong(0))) > 0 and St.get(OWNER).getProperty("owed.coll.Plant_Crop_Wheat_Item") is None,
                "X8 after a profile switch the waiting collection count goes to the collector's current profile (-p2)")
        Cfg.KEY_TEST = PyFn(lambda u: str(u))
        Cfg.COOP_COLLECT = False
        collect_ok[0] = True
        # fix: Farming XP that could not be paid waits in the collector's file and is paid on the next Collect
        xp_ok[0] = False
        St.get(OWNER).setProperty("farming.i0.stored", "10")
        r8 = str(Core.collect(ou, OWNER, -1, TI))
        owed_xp = int(St.lng(St.readNow(OWNER), "owed.xp", JLong(0)))
        K.check(owed_xp == 20 and "Farming XP waits" in r8, "X8 fix: unpaid XP (10 wheat = 20 XP) waits in the collector's file: %s" % r8)
        xp_ok[0] = True
        St.get(OWNER).setProperty("farming.i0.stored", "5")
        n0 = len(xp_calls)
        r9 = str(Core.collect(ou, OWNER, -1, TI))
        K.check(xp_calls[n0][2] == 30 and St.get(OWNER).getProperty("owed.xp") is None and St.readNow(OWNER).getProperty("owed.xp") is None,
                "X8 fix: the next Collect pays 10 + the 20 waiting in one call, nothing waits any more (file): %s" % r9)
        Cfg.ON = False
        K.check(str(Core.collect(ou, OWNER, -1, TI)).startswith("-Shards are switched off"), "X8 shards off: Collect refused")
        Cfg.ON = True
        K.check(str(Core.collect(ou, OWNER, -1, None)).startswith("-Your inventory"), "X8 no inventory: refused")
        St.get(OWNER).setProperty("farming.i0.stored", "0"); St.get(OWNER).setProperty("farming.i0.last", str(T1 + 900 * 60000))
        K.check(str(Core.collect(ou, OWNER, -1, TI)).startswith("=Nothing is stored"), "X8 nothing stored: an info line")
        K.check(str(Core.collect(ou, bad, -1, TI)).startswith("-This shard's file could not be read"), "X8 an unreadable shard: refused")
        lines = open(os.path.join(base, "collect.log"), encoding="utf-8").read()
        K.check(lines.count(" debit ") >= 6, "X8 every Collect logged in collect.log")

        # ---------------- X9 storage upgrade
        TI2 = inv(3, 1, 1)
        coins["bal"] = 4000
        r = str(Core.buyStorage(ou, OWNER, TI2))
        K.check(r.startswith("-You need 1 Enchanted Wheat"), "X9 no Enchanted Wheat: refused, nothing taken")
        Inv.give(TI2, "Skyy_Ench_Wheat", JLong(3))
        r = str(Core.buyStorage(ou, OWNER, TI2))
        K.check(r.startswith("-You need 5,000 coins") and int(Inv.count(TI2, "Skyy_Ench_Wheat")) == 3, "X9 too few coins: refused, nothing taken")
        coins["bal"] = 100000
        coins_fail[0] = True
        r = str(Core.buyStorage(ou, OWNER, TI2))
        K.check(r.startswith("-The coins could not be taken") and int(Inv.count(TI2, "Skyy_Ench_Wheat")) == 3 and int(Mth.storageTier(St.get(OWNER))) == 1,
                "X9 the coins fail after the items: the Enchanted Wheat is back (3 before / 3 after), tier unchanged")
        coins_fail[0] = False
        # fix: the new tier could not be saved -> undone, the Enchanted Wheat and the coins go back
        St.FAIL_TEST = True
        bal0 = coins["bal"]
        r = str(Core.buyStorage(ou, OWNER, TI2))
        St.FAIL_TEST = False
        K.check(r.startswith("-The upgrade could not be saved") and int(Inv.count(TI2, "Skyy_Ench_Wheat")) == 3 and coins["bal"] == bal0
                and add_calls[-1] == 5000 and int(Mth.storageTier(St.get(OWNER))) == 1,
                "X9 fix: a refused save: tier 1 kept, 3 / 3 Enchanted Wheat, coins refunded (%d): %s" % (coins["bal"], r))
        K.check(str(Core.buyStorage(mu, OWNER, TI2)).startswith("-Only the island owner can collect"), "X9 fix: a co-op member cannot buy (coopCollect off)")
        r = str(Core.buyStorage(ou, OWNER, TI2))
        K.check(r.startswith("+Storage is now tier 2") and int(Inv.count(TI2, "Skyy_Ench_Wheat")) == 2 and coins["bal"] == 95000
                and int(St.lng(St.readNow(OWNER), "farming.storage", JLong(0))) == 2, "X9 tier 2 bought: 1 Enchanted Wheat + 5,000 coins, saved")
        St.get(OWNER).setProperty("farming.storage", "5")
        K.check(str(Core.buyStorage(ou, OWNER, TI2)).startswith("=Storage is at the highest"), "X9 tier 5 = nothing left to buy")
        St.get(OWNER).setProperty("farming.storage", "2")

        # ---------------- X10 grow
        TI3 = inv(3, 1, 1)
        tiers["t"] = 2
        r = str(Core.grow(ou, OWNER, 0, TI3))
        K.check(r.startswith("-Needs Wheat collection 4 (you: 2)"), "X10 the collection tier is checked first")
        tiers["t"] = 4
        K.check(str(Core.grow(ou, OWNER, 0, TI3)).startswith("-You need 8 Eternal Wheat Seeds"), "X10 seeds missing: refused")
        Inv.give(TI3, "Plant_Seeds_Wheat_Eternal", JLong(40))
        coins["bal"] = 100
        K.check(str(Core.grow(ou, OWNER, 0, TI3)).startswith("-You need 5,000 coins") and int(Inv.count(TI3, "Plant_Seeds_Wheat_Eternal")) == 40, "X10 coins missing: nothing taken")
        coins["bal"] = 100000
        coins_fail[0] = True
        K.check(str(Core.grow(ou, OWNER, 0, TI3)).startswith("-The coins could not be taken") and int(Inv.count(TI3, "Plant_Seeds_Wheat_Eternal")) == 40,
                "X10 the coins fail: the seeds are back (40 / 40)")
        coins_fail[0] = False
        St.FAIL_TEST = True
        bal0 = coins["bal"]
        r = str(Core.grow(ou, OWNER, 0, TI3))
        St.FAIL_TEST = False
        K.check(r.startswith("-The island could not be saved") and int(Inv.count(TI3, "Plant_Seeds_Wheat_Eternal")) == 40 and coins["bal"] == bal0
                and int(Mth.size(St.get(OWNER), 0)) == 1, "X10 fix: a refused save: Small kept, 40 / 40 seeds, coins refunded: %s" % r)
        K.check(str(Core.grow(vu, OWNER, 0, TI3)).startswith("-Only the island owner and co-op"), "X10 fix: a visitor cannot grow")
        r = str(Core.grow(ou, OWNER, 0, TI3))
        K.check(r.startswith("+The Wheat island grew to Medium") and int(Mth.size(St.readNow(OWNER), 0)) == 2 and int(Inv.count(TI3, "Plant_Seeds_Wheat_Eternal")) == 32,
                "X10 grow to Medium: 8 seeds + 5,000 coins, saved (the paste waits for a loaded shard world)")
        tiers["t"] = 6
        K.check(str(Core.grow(ou, OWNER, 0, TI3)).startswith("+The Wheat island grew to Large") and int(Inv.count(TI3, "Plant_Seeds_Wheat_Eternal")) == 8, "X10 grow to Large: 24 seeds")
        K.check(str(Core.grow(ou, OWNER, 0, TI3)).startswith("=That island is fully grown"), "X10 Large = fully grown")
        K.check(str(Core.grow(ou, OWNER, 3, TI3)).startswith("-That slot has no island") and str(Core.grow(ou, OWNER, 9, TI3)).startswith("-Pick an island"), "X10 empty / bad slot")

    # ---------------- X11 placement
    Place.PENDING.clear()
    pk = "0a0a0a0a-1111-2222-3333-999999999999"
    pku = UUID.fromString(pk)
    Role.OWNER_TEST = PyFn(lambda w: (str(w)[len("skyy-island-"):] if str(w).startswith("skyy-island-") else None))
    Cfg.ON = False
    K.check("switched off" in str(Place.decide(pku, "skyy-island-" + pk, 1, 129, 2, JLong(T0))), "X11 off: refused")
    Cfg.ON = True
    K.check("not inside a shard" in str(Place.decide(pku, "skyy-shard-" + pk, 1, 1, 1, JLong(T0))), "X11 inside a shard: refused")
    K.check("own island" in str(Place.decide(pku, "default", 1, 1, 1, JLong(T0))), "X11 the hub / any non-island world: refused")
    K.check("Only the island owner" in str(Place.decide(mu, "skyy-island-" + pk, 1, 1, 1, JLong(T0))), "X11 a co-op member / visitor cannot place it")
    K.check(Place.decide(pku, "skyy-island-" + pk, 1, 129, 2, JLong(T0)) is None, "X11 the owner places it on their island")
    pp = St.readNow(pk)
    K.check(str(pp.getProperty("farming.placed")) == "skyy-island-%s|1|129|2" % pk and str(pp.getProperty("farming.i0.type")) == "wheat"
            and Place.PENDING.containsKey(pk), "X11 placed + the starter island saved, a 1 s block check pending")
    K.check("already placed" in str(Place.decide(pku, "skyy-island-" + pk, 5, 129, 5, JLong(T0))), "X11 a second shard: refused (one per profile)")
    Place.BLOCK_TEST = PyFn(lambda a: JClass("java.lang.Boolean").FALSE)
    K.eq(int(Place.verify(JLong(T0 + 500))), 0, "X11 the check waits 1 s")
    K.eq(int(Place.verify(JLong(T0 + 1500))), 1, "X11 the block is not there (another rule cancelled): the record is undone")
    K.check(St.readNow(pk).getProperty("farming.placed") is None and St.readNow(pk).getProperty("farming.i0.type") is not None, "X11 ... islands kept, placed cleared")
    Place.decide(pku, "skyy-island-" + pk, 1, 129, 2, JLong(T0 + 2000))
    Place.BLOCK_TEST = PyFn(lambda a: JClass("java.lang.Boolean").TRUE)
    K.eq(int(Place.verify(JLong(T0 + 4000))), 0, "X11 the block is there: kept")
    K.check(str(St.readNow(pk).getProperty("farming.placed")).endswith("|1|129|2"), "X11 ... still placed")
    K.check(not Place.unplace(pk, "elsewhere|0|0|0"), "X11 unplace of another position does nothing")
    # an island reset: the old portal's world no longer exists -> the record is dropped and a new placement works
    St.get(pk).setProperty("farming.placed", "skyy-island-old|1|1|1")
    K.check("already placed" in str(Place.decide(pku, "skyy-island-" + pk, 7, 129, 7, JLong(T0 + 8000))), "X11 an old record whose world may exist still blocks")
    Role.WORLD_TEST = PyFn(lambda w: JClass("java.lang.Boolean").FALSE if str(w) == "skyy-island-old" else JClass("java.lang.Boolean").TRUE)
    K.check(Place.decide(pku, "skyy-island-" + pk, 7, 129, 7, JLong(T0 + 9000)) is None
            and str(St.readNow(pk).getProperty("farming.placed")) == "skyy-island-%s|7|129|7" % pk, "X11 the old portal's world is gone (island reset): placing again works")
    Role.WORLD_TEST = None
    K.check(bool(Place.worldExists("anything")), "X11 worldExists with no Universe = assume it exists (never drops a record by doubt)")
    # fix: an island RESET keeps the old world on disk (a backup) - island:world:key:fn says which world is current
    cur = {"w": "skyy-island-%s-r2" % pk}
    Role.WORLDKEY_TEST = PyFn(lambda k: JString(cur["w"]) if str(k) == pk else None)
    Role.OWNER_TEST = PyFn(lambda w: (pk if str(w).startswith("skyy-island-" + pk) else None))
    K.check("current island" in str(Place.decide(pku, "skyy-island-" + pk, 2, 129, 2, JLong(T0 + 9500))), "X11 fix: no placing in a reset island's old (backup) world")
    Place.PENDING.clear()
    Cfg.KEY_TEST = PyFn(lambda u: str(u))
    if INVOK:
        TIp = inv(2, 1, 1)
        e_ = str(W2.enter(None, None, pku, pk, None))
        K.check(e_.startswith("-Your island was reset"), "X11 fix: Enter refused while the portal sits in the old island: %s" % e_)
        l_ = str(W2.leave(None, None, pku, pk))
        K.check(l_.startswith("-Could not leave") or l_.startswith("+Your island is not loaded"), "X11 fix: Back to Island skips the old world (no Universe here: %s)" % l_)
        rp = str(Core.pickup(pku, pk, None, TIp))
        pq = St.readNow(pk)
        K.check(rp.startswith("+Your island was reset") and int(Inv.count(TIp, "Skyy_Shard_Farming")) == 1 and pq.getProperty("farming.placed") is None
                and str(pq.getProperty("farming.paused")) == "1", "X11 fix: Pick up from anywhere after a reset: the shard is back (1 item), record cleared, paused (file): %s" % rp)
        K.check(str(Core.pickup(pku, pk, None, TIp)).startswith("-Your shard is not placed"), "X11 fix: ... a second Pick up gives nothing")
        K.check(str(W2.enter(None, None, pku, pk, None)).startswith("-No Farming Shard is placed"), "X11 fix: Enter needs a placed shard")
        # paused: no production while picked up
        pq2 = St.get(pk)
        s0 = int(Mth.stored(pq2, 0))
        K.eq(int(Mth.settle(pq2, 0, JLong(T0 + 9 * 3600000))), 0, "X11 fix: a picked-up (paused) shard makes nothing")
        K.check(Place.decide(pku, "skyy-island-%s-r2" % pk, 4, 129, 4, JLong(T0 + 10 * 3600000)) is None, "X11 fix: placed again on the current island")
        pq3 = St.readNow(pk)
        K.check(pq3.getProperty("farming.paused") is None and str(pq3.getProperty("farming.i0.last")) == str(T0 + 10 * 3600000) and int(Mth.stored(pq3, 0)) == s0,
                "X11 fix: placing clears paused and restarts the clock (nothing made for the paused hours)")
        # a stale record left by a reset (never picked up) is dropped when placing on the current island
        St.get(pk).setProperty("farming.placed", "skyy-island-%s|1|1|1" % pk)
        K.check(Place.decide(pku, "skyy-island-%s-r2" % pk, 6, 129, 6, JLong(T0 + 10 * 3600000 + 5)) is None, "X11 fix: a reset-island record is dropped, placing works")
        Place.PENDING.clear()
        # the 1 s check undoes a placement -> paused
        K.check(bool(Place.unplace(pk, "skyy-island-%s-r2|6|129|6" % pk)) and str(St.readNow(pk).getProperty("farming.paused")) == "1", "X11 fix: an undone placement pauses production")
        St.get(pk).remove("farming.paused")
        St.get(pk).setProperty("farming.placed", "skyy-island-%s-r2|6|129|6" % pk)
    Role.WORLDKEY_TEST = None
    Role.OWNER_TEST = PyFn(lambda w: (str(w)[len("skyy-island-"):] if str(w).startswith("skyy-island-") else None))
    Place.PENDING.clear()
    K.check(str(Core.pickup(mu, pk, None, inv(1))).startswith("-Only the island owner"), "X11 pick up: owner only")
    K.check(str(Core.pickup(pku, pk, None, inv(1))).startswith("-Stand by your shard portal"), "X11 pick up away from the portal: refused")
    K.check(str(Core.pickup(pku, pk, None, None)).startswith("-Your inventory"), "X11 pick up with no inventory: refused")

    # ---------------- X12 worlds: cap, queue, idle unload
    K.eq((str(Wld.name(OWNER)), bool(Wld.isShard("skyy-shard-" + OWNER)), bool(Wld.isShard("skyy-shard-")), bool(Wld.isShard("skyy-island-x")),
          str(Wld.ownerOf("skyy-shard-" + OWNER)), Wld.ownerOf("hub")), ("skyy-shard-" + OWNER, True, False, False, OWNER, None), "X12 names")
    TW = JClass("java.util.ArrayList")()
    for i in range(3):
        TW.add("skyy-shard-k%d" % i)
    Wld.TEST_WORLDS = TW
    Cfg.MAX_LOADED = 3
    K.check(not Wld.room("skyy-shard-new") and bool(Wld.room("skyy-shard-k1")), "X12 the cap: 3 of 3 loaded = no room for a new one, a loaded one is fine")
    K.eq((int(Wld.enqueue(ou)), int(Wld.enqueue(mu)), int(Wld.enqueue(ou)), int(Wld.queuePos(vu))), (1, 2, 1, -1), "X12 the queue (no doubles)")
    Cfg.UNLOAD_SEC = 120
    K.eq(int(Wld.idle(JLong(T0))), 0, "X12 idle: first sight of 3 empty worlds")
    K.eq(int(Wld.idle(JLong(T0 + 119000))), 0, "X12 idle: 119 s empty = still loaded")
    K.eq(int(Wld.idle(JLong(T0 + 120000))), 2, "X12 fix: idle: 120 s empty = unloaded - at most 2 a tick")
    K.check(Wld.QUEUE.size() == 1 and str(Wld.QUEUE.peek()) == MEMBER and TW.size() == 1, "X12 room again: the first queued player was told (and left the queue); one world still due")
    K.eq(int(Wld.idle(JLong(T0 + 121000))), 1, "X12 fix: ... the third on the next tick (it stayed due)")
    K.check(TW.isEmpty() and int(Wld.UNLOADS.get()) == 3 and Wld.EMPTY_SINCE.isEmpty(), "X12 ... gone from the loaded list, counted")
    K.check(Wld.QUEUE.isEmpty(), "X12 the next tick tells the next queued player")
    Wld.QUEUE.clear()
    Cfg.MAX_LOADED = 20
    Wld.TEST_WORLDS = None

    # ---------------- X13 the page: every tab / view / slot built into a real CustomPage packet + every click
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    CP = JClass("com.hypixel.hytale.protocol.packets.interface_.CustomPage")
    LIFE = JClass("com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime")
    St.CACHE.clear()
    pg_owner = St.get(OWNER)
    pg_owner.setProperty("farming.placed", "skyy-island-%s|3|129|3" % OWNER)
    St.save(OWNER, pg_owner)

    def build(u, world, tab, sel):
        pg = Page(u, world)
        pg.tab = tab
        pg.sel = sel
        b, ev = UCB(), UEB()
        pg.build(None, b, ev, None)
        cmds = b.getCommands()
        evs = ev.getEvents()
        sets, apps, appended = {}, 0, []
        for c in cmds:
            t_ = str(c.type)
            if "Append" in t_:
                apps += 1
                appended.append(str(c.text) if c.text is not None else "")
            if c.selector is not None and c.data is not None and t_ == "Set":
                sets[str(c.selector)] = str(c.data)
        binds = [str(e.selector) for e in evs]
        return pg, cmds, evs, sets, apps, "\n".join(appended), binds
    worlds = {"portal": "skyy-island-" + OWNER, "hub": "skyy-shard-" + OWNER, "menu": "default"}
    sizes, unbound, views = [], [], {}
    for vname, wn in worlds.items():
        for tab in range(5):
            for sel in (range(6) if tab == 2 else (0,)):
                pg, cmds, evs, sets, apps, mk, binds = build(ou, wn, tab, sel)
                views[vname] = int(pg.view)
                size = int(CP("SkyySh", True, True, LIFE.CanDismiss, cmds, evs).computeSize())
                sizes.append(size)
                for bnd in binds:
                    if ("#" + bnd.lstrip("#") + " ") not in mk.replace("{", " ").replace(";", " ") and (bnd.lstrip("#") + " {") not in mk:
                        unbound.append((vname, tab, bnd))
    K.eq(views, {"portal": 0, "hub": 1, "menu": 2}, "X13 the view: portal on the owner's island, hub in the shard world, menu elsewhere")
    K.check(max(sizes) < int(CP.MAX_SIZE), "X13 every build (3 views x 5 tabs x 6 slots) is one CustomPage packet: max %d bytes of %d" % (max(sizes), int(CP.MAX_SIZE)))
    K.check(not unbound, "X13 every event binding targets an element of the same build: %s" % unbound[:3])
    pg, cmds, evs, sets, apps, mk, binds = build(ou, worlds["portal"], 0, 0)
    K.check("#SkyyShPick" in binds and "#SkyyShEnter" in binds and "#SkyyShBack" not in binds and "#SkyyShCRow0Btn" in binds and "#SkyyShCAll" in binds,
            "X13 portal view: Enter Shard + Pick up Shard + Collect buttons")
    K.check(str(sets.get("#SkyyShSum1.Text", "")).startswith("1 island - 1 totem - 60 items / hour") or "items / hour" in str(sets.get("#SkyyShSum1.Text", "")),
            "X13 the summary line: %s" % sets.get("#SkyyShSum1.Text"))
    pg, cmds, evs, sets, apps, mk, binds = build(ou, worlds["hub"], 1, 0)
    K.check("#SkyyShBack" in binds and "#SkyyShPick" not in binds and "#SkyyShUBuy" in binds, "X13 hub view: Back to Island, no Pick up; Upgrades has Buy")
    pg, cmds, evs, sets, apps, mk, binds = build(ou, worlds["menu"], 2, 1)
    K.check(all(("#SkyyShISl%dSel" % i) in binds for i in range(6)) and "#SkyyShIGrow" not in binds and "empty" in str(sets.get("#SkyyShIRT.Text", "")),
            "X13 Islands tab: 6 slot buttons; an empty slot has no Grow button")
    pg, cmds, evs, sets, apps, mk, binds = build(vu, worlds["portal"], 0, 0)
    K.check("co-op" in str(pg.stText) and int(pg.view) == 2, "X13 a visitor at someone's portal: refused line, own (menu) view")
    # fix: Pick up only for the owner; a co-op member at the portal sees Enter but no Pick up
    pg, cmds, evs, sets, apps, mk, binds = build(mu, worlds["portal"], 0, 0)
    K.check(int(pg.view) == 0 and "#SkyyShEnter" in binds and "#SkyyShPick" not in binds and str(pg.act("pick", None, None)).startswith("-Only the island owner"),
            "X13 fix: a co-op member at the portal: Enter, no Pick up (a forced click is refused)")
    # fix: inside a shard world the role is re-checked at every build / click (a visitor / removed member / other profile)
    pg, cmds, evs, sets, apps, mk, binds = build(vu, worlds["hub"], 0, 0)
    K.check("co-op" in str(pg.stText) and str(pg.act("colall", None, None)).startswith("-Only the island owner and co-op"),
            "X13 fix: a visitor inside someone's shard: refused on build and on Collect")
    # fix: after an island reset the owner gets Pick up in the menu view (the old portal is out of reach)
    Role.WORLDKEY_TEST = PyFn(lambda k: JString("skyy-island-" + OWNER + "-r2") if str(k) == OWNER else None)
    pg, cmds, evs, sets, apps, mk, binds = build(ou, worlds["menu"], 0, 0)
    K.check(bool(pg.stale) and "#SkyyShPick" in binds and "reset" in str(sets.get("#SkyyShSum2.Text", pg.sum2)),
            "X13 fix: reset island: the menu view shows Pick up Shard + the reason")
    Role.WORLDKEY_TEST = None
    pg, cmds, evs, sets, apps, mk, binds = build(ou, worlds["menu"], 0, 0)
    K.check(not pg.stale and "#SkyyShPick" not in binds, "X13 fix: normal menu view: no Pick up")
    # texts fit their labels (the real ones at the widest numbers)
    K.notes.append("X13 page packet sizes %d .. %d bytes" % (min(sizes), max(sizes)))
    # clicks
    pg = Page(ou, worlds["portal"])
    seq = []
    for a_ in ("tab2", "slot4", "tab9", "slotx", "enter", "back", "pick", "pick", "colall", "col0", "col5", "buy", "grow", "zzz"):
        seq.append(str(pg.act(a_, None, None)))
    K.check(int(pg.tab) == 2 and int(pg.sel) == 4, "X13 clicks: tab / slot (bad ones ignored)")
    K.eq(seq[4:8], ["=test: enter", "=test: back", "=Click Pick up Shard again to pick it up. Its islands and storage are kept.", "=test: pick"],
         "X13 clicks: enter, back, pick asks twice")
    K.check(seq[8][0] in "+-=" and seq[9][0] in "+-=" and seq[10].startswith("-That island is gone") and seq[11][0] in "+-=" and seq[12][0] in "+-=" and seq[13] == "",
            "X13 clicks: collect all / one / a gone row / buy / grow / unknown: %s" % seq[8:])
    pg.handleDataEvent(None, None, '{"a":"tab1"}')
    K.check(int(pg.tab) == 1, "X13 handleDataEvent reads the click")
    pg.handleDataEvent(None, None, '{"a":"col0"}')
    K.check(len(str(pg.stText)) > 0, "X13 the status line after a click: %s" % pg.stText)
    K.eq([str(Page.jsonA(x)) for x in ('{"a":"tab0"}', '{"a" : "colall"}', '{}', None, '{"a":5}')], ["tab0", "colall", "", "", ""], "X13 jsonA")
    mv = Page(ou, worlds["portal"])
    mv.fromMenu = True
    K.check(mv.resolve(None) == OWNER and int(mv.view) == 2, "X13 the SkyWynn Menu tile on your own island = menu view (no Pick up)")
    hv = Page(ou, worlds["hub"])
    K.check(str(hv.act("pick", None, None)).startswith("-Pick up the shard at its portal"), "X13 pick up from the hub view: refused")

    # ---------------- X14 bridge Functions + /shardadmin text
    K.eq((str(Fn(1).apply("skyy-shard-" + OWNER)), Fn(1).apply("default"), bool(Fn(0).apply("not-a-uuid")), bool(Fn(0).apply(ou))),
         (OWNER, None, False, False), "X14 shard:fn:world / shard:fn:open (no player in a bare JVM = FALSE, never throws)")
    K.check("Usage" in str(Adm.run("").get(0)) and "Usage" in str(Adm.run("give").get(0)), "X14 /shardadmin usage")
    _ap = W2.arrival().getPosition()
    K.check(abs(float(_ap.x()) - 2048.5) < 1e-9 and abs(float(_ap.y()) - 101.0) < 1e-9 and abs(float(_ap.z()) - 3.5) < 1e-9, "X14 the arrival point (2048.5, 101, 3.5)")

    # ---------------- X15 review fixes 2 (fix2:)
    Bool = JClass("java.lang.Boolean")
    import zipfile as _zf
    with _zf.ZipFile(jar) as _z:
        _tpl = json.loads(_z.read("Server/Instances/SkyyShard/instance.bson").decode("utf-8"))
    K.check(_tpl.get("Death") == {"ItemsLossMode": "None"} and _tpl.get("GameplayConfig") == "Default",
            "X15 fix2: the shard world template keeps items on death (Death.ItemsLossMode None over Default's 50 %%)")
    # totem.particle: only a particle system the game has reaches the clients
    _p0 = str(Cfg.PARTICLE)
    K.eq(str(Cfg.particle()), "Dust_Sparkles_Fine", "X15 fix2: the default particle is used as is")
    Cfg.PART_TEST = PyFn(lambda n: Bool.TRUE if str(n) == "Good_Particle" else Bool.FALSE)
    Cfg.PARTICLE = "Typo_Particle"
    _a = str(Cfg.particle())
    Cfg.PARTICLE = "Good_Particle"
    _b = str(Cfg.particle())
    Cfg.PART_TEST = None
    Cfg.PARTICLE = "No_Asset_Map_Here"
    _c = str(Cfg.particle())
    Cfg.PARTICLE = _p0
    K.eq((_a, _b, _c), ("Dust_Sparkles_Fine", "Good_Particle", "Dust_Sparkles_Fine"),
         "X15 fix2: totem.particle - unknown = the default (+ one WARN), a known one is used, no asset map = the default (never a throw)")
    # the real hub first (SkyyIslands 0.5.8 island:fn:hub), the default world spawn only as a fallback
    _hub = []
    _hub_ok = [True]
    br.put("island:fn:hub", PyFn(lambda u: (_hub.append(str(u)), Bool.valueOf(_hub_ok[0]))[1]))
    _h1 = bool(W2.hub(None, None, ou))
    _hub_ok[0] = False
    _h2 = bool(W2.hub(None, None, ou))
    br.remove("island:fn:hub")
    K.check(_h1 and not _h2 and _hub == [OWNER, OWNER], "X15 fix2: hub asks island:fn:hub first (TRUE = sent); FALSE = the default-world fallback (none in a bare JVM)")
    if INVOK:
        Cfg.KEY_TEST = PyFn(lambda u: str(u))
        Role.WORLDKEY_TEST = None
        Cfg.COOP_COLLECT = False
        tiers["t"] = 9
        coins["bal"] = 1000000
        Core.NOW_TEST = T0 + 30 * 3600000
        po = St.get(OWNER)
        po.remove("farming.paused")
        po.setProperty("farming.placed", "skyy-island-%s|3|129|3" % OWNER)
        po.setProperty("farming.i0.stored", "10")
        po.setProperty("farming.i0.last", str(T0 + 30 * 3600000))
        po.setProperty("farming.storage", "1")
        po.setProperty("farming.i0.size", "1")
        St.save(OWNER, po)
        # profile:busy (PROFILES-CONTRACT rule 5): nothing moves between the live inventory and the shard
        TB = inv(3, 1, 1)
        Inv.give(TB, "Skyy_Ench_Wheat", JLong(5)); Inv.give(TB, "Plant_Seeds_Wheat_Eternal", JLong(50))
        br.put("profile:busy:" + OWNER, Bool.TRUE)
        _rs = [str(Core.collect(ou, OWNER, -1, TB)), str(Core.buyStorage(ou, OWNER, TB)), str(Core.grow(ou, OWNER, 0, TB)), str(Core.pickup(ou, OWNER, None, TB))]
        br.remove("profile:busy:" + OWNER)
        _pf = St.readNow(OWNER)
        K.check(all(x.startswith("-Your profile is still loading") for x in _rs) and int(Inv.count(TB, "Plant_Crop_Wheat_Item")) == 0
                and int(Inv.count(TB, "Skyy_Ench_Wheat")) == 5 and int(Inv.count(TB, "Plant_Seeds_Wheat_Eternal")) == 50
                and int(Inv.count(TB, "Skyy_Shard_Farming")) == 0 and coins["bal"] == 1000000 and str(_pf.getProperty("farming.i0.stored")) == "10"
                and str(_pf.getProperty("farming.storage")) == "1" and _pf.getProperty("farming.placed") is not None,
                "X15 fix2: profile:busy = Collect / buy / Grow / Pick up refused, items / coins / file unchanged: %s" % _rs)
        # lastCollect is written with the debit (the Collect tab's "Last collected ... ago")
        _rc = str(Core.collect(ou, OWNER, -1, TB))
        K.check(_rc.startswith("+Collected 10 Wheat") and str(St.readNow(OWNER).getProperty("lastCollect")) == str(T0 + 30 * 3600000)
                and int(Inv.count(TB, "Plant_Crop_Wheat_Item")) == 10, "X15 fix2: Collect writes lastCollect (file): %s" % _rc)
        pgx = Page(ou, "skyy-island-" + OWNER)
        Core.NOW_TEST = T0 + 30 * 3600000 + 5 * 60000
        pgx.fill(OWNER, TB)
        K.check("Last collected 5m" in str(pgx.cAll[3]) or ("Last collected" in str(pgx.cAll[3]) and "ago" in str(pgx.cAll[3])),
                "X15 fix2: the Collect tab shows the last Collect: %s" % pgx.cAll[3])
        K.check(all("whole island" not in str(x) for x in pgx.tSub) and str(pgx.tSub[0]).startswith("Worker - range 3 - 1 / min"), "X15 fix2 / 0.2: the totem row: %s" % pgx.tSub[0])
        # a stale record (the island was reset, the portal sits in the old backup world) pauses production at the first look
        Core.NOW_TEST = T0 + 31 * 3600000
        po = St.get(OWNER)
        po.setProperty("farming.i0.stored", "0"); po.setProperty("farming.i0.last", str(T0 + 30 * 3600000))
        St.save(OWNER, po)
        Role.WORLDKEY_TEST = PyFn(lambda k: JString("skyy-island-" + OWNER + "-r9") if str(k) == OWNER else None)
        _ps = bool(Core.pauseStale(OWNER, St.get(OWNER)))
        _pf = St.readNow(OWNER)
        _made = int(St.lng(_pf, "farming.i0.stored", JLong(-1)))
        _later = int(Mth.settle(St.get(OWNER), 0, JLong(T0 + 40 * 3600000)))
        _again = bool(Core.pauseStale(OWNER, St.get(OWNER)))
        K.check(_ps and str(_pf.getProperty("farming.paused")) == "1" and _made == 60 and _later == 0 and not _again,
                "X15 fix2: stale record = settled up to now (60 made in the hour before), then paused (file), nothing more; once only")
        Role.WORLDKEY_TEST = None
        po = St.get(OWNER); po.remove("farming.paused"); St.save(OWNER, po)
        K.check(not Core.pauseStale(OWNER, St.get(OWNER)) and St.readNow(OWNER).getProperty("farming.paused") is None, "X15 fix2: a current record is never paused")
        # the collector's file cannot be read: unpaid XP waits in memory (never dropped), paid on the next Collect
        Cfg.KEY_TEST = PyFn(lambda u: bad)
        xp_ok[0] = False
        _l1 = int(Core.owedXp(ou, JLong(20)))
        _mem = Core.MEM_OWED.get(bad + "|owed.xp")
        xp_ok[0] = True
        n0 = len(xp_calls)
        _l2 = int(Core.owedXp(ou, JLong(5)))
        collect_ok[0] = False
        _c1 = int(Core.owed(ou, JLong(7)))
        collect_ok[0] = True
        n1 = len(coll_calls)
        _c2 = int(Core.owed(ou, JLong(3)))
        Cfg.KEY_TEST = PyFn(lambda u: str(u))
        K.check(_l1 == 20 and _mem is not None and int(_mem) == 20 and _l2 == 0 and xp_calls[n0][2] == 25 and Core.MEM_OWED.get(bad + "|owed.xp") is None,
                "X15 fix2: unreadable collector file: 20 XP waits in memory, the next call pays 5 + 20 = 25 and clears it")
        K.check(_c1 == 7 and _c2 == 0 and coll_calls[n1][2] == 10 and Core.MEM_OWED.isEmpty(), "X15 fix2: ... the collection count too (7 waits, then 3 + 7 = 10)")
        # Pick up at the portal while its spot is not loaded: refused, nothing moves (no second portal block left behind)
        WC = JClass("com.hypixel.hytale.server.core.universe.world.World")
        _w = unsafe().allocateInstance(WC.class_)
        setf(_w, WC.class_, "name", JString("skyy-island-" + OWNER))
        _rp = str(Core.pickup(ou, OWNER, _w, TB))
        K.check(_rp.startswith("-Your shard portal's spot is not loaded") and int(Inv.count(TB, "Skyy_Shard_Farming")) == 0
                and St.readNow(OWNER).getProperty("farming.placed") is not None, "X15 fix2: Pick up with the portal's chunk not loaded: refused, record kept: %s" % _rp)
        # the 1 s placement check: a chunk not loaded is checked again (10 tries), a newer placement is never overwritten
        Place.PENDING.clear()
        Role.OWNER_TEST = PyFn(lambda w: (str(w)[len("skyy-island-"):] if str(w).startswith("skyy-island-") else None))
        St.get(pk).remove("farming.placed"); St.save(pk, St.get(pk))
        K.check(Place.decide(pku, "skyy-island-" + pk, 9, 129, 9, JLong(T0 + 50 * 3600000)) is None, "X15 fix2: placed (the check is pending)")
        _bt = Place.BLOCK_TEST
        Place.BLOCK_TEST = PyFn(lambda a: None)
        _t = T0 + 50 * 3600000
        _tries = []
        for _i in range(12):
            _t += 1500
            Place.verify(JLong(_t))
            _e = Place.PENDING.get(pk)
            _tries.append(int(_e[6]) if _e is not None else -1)
        K.eq(_tries, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, -1, -1], "X15 fix2: a chunk not loaded is checked again, 10 tries, then left")
        K.check(str(St.readNow(pk).getProperty("farming.placed")).endswith("|9|129|9"), "X15 fix2: ... the record stays (Pick up recovers a missing block)")
        Place.BLOCK_TEST = PyFn(lambda a: Bool.FALSE)
        St.get(pk).remove("farming.placed"); St.save(pk, St.get(pk))
        Place.decide(pku, "skyy-island-" + pk, 9, 129, 9, JLong(_t))
        _e0 = Place.PENDING.get(pk)
        K.check(not bool(Place.again(pk, _e0, JLong(_t))) and Place.PENDING.get(pk) is _e0 or Place.PENDING.get(pk) == _e0,
                "X15 fix2: a retry never overwrites a newer pending placement")
        K.eq(int(Place.verify(JLong(_t + 1500))), 1, "X15 fix2: the block is not there: undone (and the player is told; no Universe here, no throw)")
        Place.BLOCK_TEST = _bt
        Place.PENDING.clear()

    # ---------------- X16 TOTEMS (0.2): rate math vs range, support / day / night / moon, boosts, rolls, place / pick up exact document,
    # modifiers, booster, crafting + the rebirth gate, shard:fn:totem, the Totems / Craft tabs (every new code path)
    if INVOK:
        Tot, TFn = P("ShTotem"), P("ShTotemFn")
        Bool = JClass("java.lang.Boolean")
        Cfg.KEY_TEST = PyFn(lambda u: str(u))
        Role.WORLDKEY_TEST = None
        Cfg.COOP_COLLECT = False
        open(os.path.join(base, "config.properties"), "w", encoding="utf-8").write(str(Cfg.DEFAULT_TEXT))
        Cfg.loadCfg(False)
        K.eq((list(Cfg.RATES), list(Cfg.RANGES), list(Cfg.SUPPORT), list(Cfg.PADS), int(Cfg.BOOST_SEC), int(Cfg.BOOST_PCT), float(Cfg.NIGHT),
              int(Cfg.MOON_BONUS), float(Cfg.ENCH_CH), int(Cfg.SHARD_RB), str(Cfg.UP_COST)),
             ([1.0, 1.25, 1.5, 1.75, 2.0], [3, 5, 7, 9, 11], [5, 10, 15, 20, 25], [3, 4, 5], 3600, 25, 0.4, 25, 0.05, 2, "1:10,2:25,3:50,5:100"),
             "X16 the totem defaults (rates, ranges 3/5/7/9/11, support %, pads 3/4/5, booster 1 h +25 %, night 0.4, moon +25 % / 0.05 %, shard craft rebirth 2)")
        K.eq(list(Tot.parse("harvest_spirit:1")), ["harvest_spirit", "1", "", "", "0", ""], "X16 a 0.1 entry reads as a Harvest Spirit I")
        K.eq(list(Tot.parse("rain:9:wider:bogus:-5:ab:c")), ["rain", "5", "wider", "", "0", "ab"], "X16 parse clamps the tier, drops an unknown modifier / a negative clock")
        K.eq(str(Tot.fmt(Tot.parse("rain:2:faster:wider:77:u1"))), "rain:2:faster:wider:77:u1", "X16 fmt(parse(x)) = x")

        def crop_tiles(size):
            h = [6, 10, 14][size - 1]
            out = []
            for dx in range(-h, h + 1):
                for dz in range(-h, h + 1):
                    ax, az = abs(dx), abs(dz)
                    if (ax == h and az == h) or ax == h or az == h or (ax <= 1 and az <= 1):
                        continue
                    out.append((dx, dz))
            return out
        cov_ok = all(int(Tot.cov(s, r)) == sum(1 for (x, z) in crop_tiles(s) if x * x + z * z <= r * r) for s in (1, 2, 3) for r in range(0, 41))
        K.check(cov_ok and int(Tot.cov(1, 3)) == 20 and int(Tot.cov(1, 99)) == 112 and int(Tot.cov(3, 99)) == 720,
                "X16 crops in range = the island geometry (Small 112 / Medium 352 / Large 720 crops; range 3 reaches 20)")
        # the island's crop tiles = the layout's crop blocks (one source of truth)
        rr = Props(); Mth.starter(rr, JLong(T0))
        _cl = Geo.crops(rr)
        K.eq(_cl.size(), 112, "X16 the Small island has 112 crop blocks = cov(1, all)")

        def rate_of(entries, size=1, t=T0):
            q_ = Props(); Mth.starter(q_, JLong(T0)); q_.setProperty("farming.i0.size", str(size)); q_.setProperty("farming.i0.totems", entries)
            return float(Mth.rate(q_, 0, JLong(t)))
        cases = [("harvest_spirit:1", 1, 1.0, "T1 Small = 0.1's 1 / min"),
                 ("harvest_spirit:1", 2, 1.0, "T1 on a Medium island: the range still reaches 20 crops"),
                 ("harvest_spirit:1", 3, 1.0, "T1 on a Large island: the same"),
                 ("harvest_spirit:2", 1, 1.25 * 72 / 20, "T2 Small: range 5 = 72 crops x 1.25"),
                 ("harvest_spirit:3", 1, 1.5 * 108 / 20, "T3 Small: range 7 reaches 108 of the 112 crops (the corners stay for you)"),
                 ("harvest_spirit:3", 2, 1.5 * 140 / 20, "T3 Medium: 140 crops in range 7"),
                 ("harvest_spirit:5", 3, 12.0, "fix4: T5 Large: range 11 = 368 crops x 2 = 36.8, capped at totem.workerMax 12"),
                 ("harvest_spirit:5:faster::0:", 3, 12.0 * 1.2, "fix4: the cap comes before the totem's own modifiers (12 x Faster 1.2)"),
                 ("harvest_spirit:4", 2, 12.0, "fix4: T4 Medium 21.4 -> 12"),
                 ("harvest_spirit:1:wider::0:", 1, 72 / 20, "Wider Area +2 range"),
                 ("harvest_spirit:1:faster:replant:0:", 1, 1.3, "Faster + Auto-Replant x1.3"),
                 ("harvest_spirit:1,harvest_spirit:1", 1, 2.0, "two workers add up"),
                 ("harvest_spirit:1,rain:1", 1, 1.05, "Rain I +5 %"),
                 ("harvest_spirit:1,fertilizer:5", 1, 1.25, "Fertilizer V +25 %"),
                 ("harvest_spirit:1,sun_blessing:1", 1, 1.0 + 0.05 * 0.6, "Sun by day (x 0.6)"),
                 ("harvest_spirit:1,mushroom_shade:1", 1, 1.0 + 0.05 * 0.4, "Mushroom Shade by night (x 0.4)"),
                 ("harvest_spirit:1,harvest_moon:1", 1, 1.0 + 0.25 * 0.4, "Harvest Moon +25 % at night (x 0.4)"),
                 ("rain:5,fertilizer:5", 1, 0.0, "no worker = nothing"),
                 ("quarry_spirit:5", 1, 0.0, "a Mining worker makes nothing on a Farming island"),
                 ("harvest_spirit:1,herd_pole:5", 1, 1.0, "a Ranching support does nothing here")]
        bad_ = [(e, s, round(rate_of(e, s), 6), round(w, 6), why) for (e, s, w, why) in cases if abs(rate_of(e, s) - w) > 1e-9]
        K.check(float(Cfg.WORKER_MAX) == 12.0 and "totem.workerMax=12" in str(Cfg.DEFAULT_TEXT), "X16 fix4: totem.workerMax defaults to 12 (spec 9.2 / 9.3 ceiling)")
        Cfg.WORKER_MAX = 0.0
        _unc = rate_of("harvest_spirit:5", 3)
        Cfg.WORKER_MAX = 12.0
        K.check(abs(_unc - 2.0 * 368 / 20) < 1e-9, "X16 fix4: totem.workerMax 0 = no cap (T5 Large 36.8 again): %.3f" % _unc)
        K.check(not bad_, "X16 RATE MATH vs RANGE: %d cases (T1 keeps 0.1's 1 / min; growing pays only where a range reaches) %s" % (len(cases), bad_[:3]))
        # boosts: the settle splits time at the booster end
        qb = Props(); Mth.starter(qb, JLong(T0)); qb.setProperty("farming.storage", "5")
        qb.setProperty("farming.i0.totems", "harvest_spirit:2:::%d:b1" % (T0 + 30 * 60000))
        _boosted = float(Mth.rate(qb, 0, JLong(T0)))
        _after = float(Mth.rate(qb, 0, JLong(T0 + 31 * 60000)))
        _m = int(Mth.settle(qb, 0, JLong(T0 + 60 * 60000)))
        K.check(abs(_boosted - 1.25 * 1.25 * 108 / 20) < 1e-9 and abs(_after - 4.5) < 1e-9 and _m == int(30 * _boosted + 30 * _after + 1e-9),
                "X16 a booster (+2 range, +25 %%) until minute 30: %.4f / min boosted, %.2f after, 60 min = %d items" % (_boosted, _after, _m))
        # conservation with boosts: random settle sequences = floor(the integral) (+-1)
        rnd = random.Random(16)
        worst = 0
        for case in range(600):
            r_ = Props(); Mth.starter(r_, JLong(T0)); r_.setProperty("farming.storage", "5")
            sz = rnd.choice((1, 2, 3))
            r_.setProperty("farming.i0.size", str(sz))
            ends = sorted(T0 + rnd.randint(1, 200) * 60000 + rnd.randint(0, 59999) for _ in range(rnd.randint(0, 3)))
            ents = ["harvest_spirit:%d:%s::%d:x%d" % (rnd.randint(1, 5), rnd.choice(("", "wider", "faster")), e_, i_) for i_, e_ in enumerate(ends)] or ["harvest_spirit:1"]
            ents += [rnd.choice(("rain:2", "sun_blessing:3", "harvest_moon:1", "compost:1"))]
            r_.setProperty("farming.i0.totems", ",".join(ents))
            t = T0
            made = 0
            for step in range(rnd.randint(1, 25)):
                t += rnd.randint(0, 15 * 60000)
                made += int(Mth.settle(r_, 0, JLong(t)))
            integ = 0.0
            tt = T0
            pts = sorted(set([x for x in ends if T0 < x < t] + [t]))
            for b_ in pts:
                integ += (b_ - tt) * float(Mth.rate(r_, 0, JLong(tt))) / 60000.0
                tt = b_
            exp_ = min(int(Mth.capOf(r_, 0)), int(integ + 1e-9))
            worst = max(worst, abs(made - exp_))
        K.check(worst <= 1, "X16 600 random sequences with boosters ending mid-way: items = floor(the integral of the rate) (off by %d at most)" % worst)
        # Harvest Moon rolls: chance, Rare Finder, Moon Blade, never re-rolled
        qm = Props(); Mth.starter(qm, JLong(T0)); qm.setProperty("farming.storage", "5"); qm.setProperty("pkey", OWNER)
        qm.setProperty("farming.i0.totems", "harvest_spirit:5,harvest_moon:1:rare:rare:0:m1")
        K.check(abs(float(Tot.enchChance(qm, 0)) - 0.0005 * 0.4 * 3) < 1e-12, "X16 the Enchanted chance = 0.05 %% x night 0.4 x (1 + 2 Rare Finders)")
        Tot.MOON_TEST = PyFn(lambda k: JClass("java.lang.Double")(4.0))
        Tot.MOON_CACHE.clear()
        K.check(abs(float(Tot.enchChance(qm, 0)) - 0.0005 * 0.4 * 3 * 4) < 1e-12, "X16 ... x the owner's Moon Blade (gear:fn:moonblade, here 4)")
        Tot.MOON_TEST = PyFn(lambda k: JClass("java.lang.Double")(99.0)); Tot.MOON_CACHE.clear()
        K.check(abs(float(Tot.moonBlade(OWNER)) - 5.0) < 1e-12, "X16 the Moon Blade factor is clamped to 5")
        Tot.MOON_TEST = None; Tot.MOON_CACHE.clear()
        K.check(abs(float(Tot.moonBlade("nobody")) - 1.0) < 1e-12, "X16 no SkyyGear Moon Blade = x1")
        # fix4: under ShStore.LOCK only the cache is read (no bridge call); warmed outside the lock, the value is used under it
        _mc = []
        Tot.MOON_TEST = PyFn(lambda k: (_mc.append(str(k)), JClass("java.lang.Double")(3.0))[1]); Tot.MOON_CACHE.clear()
        St.LOCK.lock()
        try:
            _m1 = float(Tot.moonBlade("mb1"))
        finally:
            St.LOCK.unlock()
        _n1 = len(_mc)
        _m2 = float(Tot.moonBlade("mb1"))
        St.LOCK.lock()
        try:
            _m3 = float(Tot.moonBlade("mb1"))
        finally:
            St.LOCK.unlock()
        Tot.MOON_TEST = None; Tot.MOON_CACHE.clear()
        K.check(_m1 == 1.0 and _n1 == 0 and _m2 == 3.0 and _m3 == 3.0 and len(_mc) == 1,
                "X16 fix4: Moon Blade under ShStore.LOCK = cache only (cold = x1, no bridge call); warmed outside = x3 under the lock: %s" % [_m1, _n1, _m2, _m3, len(_mc)])
        Cfg.ENCH_CH = 50.0
        snap = Props(); snap.putAll(qm)
        mm = int(Mth.settle(qm, 0, JLong(T0 + 600 * 60000)))
        e1 = int(Mth.ench(qm, 0))
        snap2 = Props(); snap2.putAll(snap)
        Mth.settle(snap2, 0, JLong(T0 + 600 * 60000))
        e2 = int(Mth.ench(snap2, 0))
        K.check(mm > 0 and 0 < e1 < mm and e1 == e2 and abs(e1 / float(mm) - 0.6) < 0.1,
                "X16 Harvest Moon rolls (chance raised to 60 %% for the test): %d Enchanted of %d, the same %d when settled again from the same file (seeded)" % (e1, mm, e2))
        Cfg.ENCH_CH = 0.05
        # the storage modifier: +3 stacks for its island
        qs = Props(); Mth.starter(qs, JLong(T0)); qs.setProperty("farming.i0.totems", "harvest_spirit:1:storage:storage:0:s")
        K.eq((int(Mth.cap(qs)), int(Mth.capOf(qs, 0))), (100, 700), "X16 Storage modifiers: 100 + 2 x 300 for that island")
        # the layout: totem blocks on the pads, the rest cleared
        rl = Props(); Mth.starter(rl, JLong(T0)); rl.setProperty("farming.i0.totems", "harvest_spirit:1,rain:2")
        _bl = [tuple(int(v) for v in rlx) for rlx in Geo.region(rl)]
        p0 = tuple(int(v) for v in Geo.padPos(0, 0)); p1 = tuple(int(v) for v in Geo.padPos(0, 1)); p2 = tuple(int(v) for v in Geo.padPos(0, 2))
        K.check(p0 + (int(Geo.TOTEM) + 0,) in _bl and p1 + (int(Geo.TOTEM) + 1,) in _bl and p2 + (int(Geo.AIR),) in _bl
                and str(list(Geo.IDS)[int(Geo.TOTEM) + 1]) == "Skyy_TotemBlock_Rain", "X16 the layout: Harvest Spirit on pad 1, Rain on pad 2, the other pads AIR")
        K.eq(list(Core.nearest(rl, float(p1[0]) + 0.2, float(p1[2]) + 0.6)), [0, 1], "X16 the totem page selects the nearest totem (pad 2)")
        K.check(Core.nearest(rl, 0.0, 0.0) is None, "X16 ... none within 6 blocks = none")
        # protection: a totem block opens its page; nothing else about it is allowed
        g16 = Gate()
        _ga = [bool(g16.apply(JArray(JObject)([JString("skyy-shard-" + OWNER), JString(a_), JString("Skyy_TotemBlock_Rain"), ou]))) for a_ in ("use", "break", "damage", "place")]
        K.eq(_ga, [True, False, False, False], "X16 a totem block: use = its page; break / damage / place refused")

        # ---- place / pick up / modifiers / booster on real containers (the item first or the record first, never a copy)
        TT = inv(4, 1, 1)
        coins["bal"] = 1000000
        tiers["t"] = 1
        Core.NOW_TEST = T0 + 1000 * 60000
        NOW = T0 + 1000 * 60000
        po = St.get(OWNER)
        po.clear(); po.setProperty("pkey", OWNER)
        Mth.starter(po, JLong(NOW))
        po.setProperty("farming.placed", "skyy-island-%s|3|129|3" % OWNER)
        St.save(OWNER, po)
        f_rain = JArray(JString)(["rain", "3", "wider", "faster", str(NOW + 600000), "uid123"])
        K.check(bool(Inv.giveStack(TT, Tot.stack(f_rain, JLong(NOW)))), "X16 a Rain Totem III (Wider, Faster, 10 min booster) is in the inventory")
        lt = Inv.totems(TT)
        d0 = lt.get(0)[3]
        K.check(lt.size() == 1 and str(Tot.dstr(d0, "uid")) == "uid123" and int(Tot.dlong(d0, "tier")) == 3 and int(Tot.dlong(d0, "bst")) == 600000,
                "X16 the item carries its document (key SkyyTotem: tier 3, uid, 600,000 ms booster left)")
        Core.NOW_TEST = NOW + 60000
        ci_, si_ = int(lt.get(0)[0]), int(lt.get(0)[1])
        n_t = int(Inv.count(TT, "Skyy_Totem_Rain"))
        St.FAIL_TEST = True
        r_ = str(Core.placeTotem(ou, OWNER, 0, ci_, si_, TT))
        St.FAIL_TEST = False
        lt2 = Inv.totems(TT)
        K.check(r_.startswith("-The totem could not be saved") and int(Inv.count(TT, "Skyy_Totem_Rain")) == n_t and lt2.size() == 1
                and str(Tot.dstr(lt2.get(0)[3], "uid")) == "uid123" and len(list(Tot.entries(St.get(OWNER), 0))) == 1,
                "X16 place with a refused save: the SAME totem (uid123) is back, the island unchanged: %s" % r_)
        ci_, si_ = int(lt2.get(0)[0]), int(lt2.get(0)[1])
        r_ = str(Core.placeTotem(ou, OWNER, 0, ci_, si_, TT))
        ents = list(Tot.entries(St.readNow(OWNER), 0))
        K.check(r_.startswith("+Placed Rain Totem III") and int(Inv.count(TT, "Skyy_Totem_Rain")) == n_t - 1 and len(ents) == 2
                and str(ents[1]) == "rain:3:wider:faster:%d:uid123" % (NOW + 60000 + 600000), "X16 placed: 1 item less, the entry on pad 2 keeps tier / modifiers / uid / the 10 booster minutes (they burn from now; file): %s" % ents)
        # pick up the starter (no uid yet) and the Rain Totem: the exact documents come back
        St.FAIL_TEST = True
        r_ = str(Core.pickTotem(ou, OWNER, 0, 1, TT))
        St.FAIL_TEST = False
        K.check(r_.startswith("-The totem could not be saved") and int(Inv.count(TT, "Skyy_Totem_Rain")) == 0 and len(list(Tot.entries(St.get(OWNER), 0))) == 2,
                "X16 pick up with a refused save: the item is taken back by uid, the record stays: %s" % r_)
        Core.NOW_TEST = NOW + 120000
        r_ = str(Core.pickTotem(ou, OWNER, 0, 1, TT))
        lt3 = Inv.totems(TT)
        d3 = lt3.get(0)[3] if lt3.size() == 1 else None
        K.check(r_.startswith("+Rain Totem III is in your inventory") and d3 is not None and str(Tot.dstr(d3, "t")) == "rain" and int(Tot.dlong(d3, "tier")) == 3
                and str(Tot.dstr(d3, "m1")) == "wider" and str(Tot.dstr(d3, "m2")) == "faster" and str(Tot.dstr(d3, "uid")) == "uid123"
                and int(Tot.dlong(d3, "bst")) == 540000 and len(list(Tot.entries(St.readNow(OWNER), 0))) == 1,
                "X16 PICK UP RETURNS THE EXACT DOCUMENT: rain, tier 3, Wider + Faster, uid123, 540,000 ms booster left (1 min burned); the record is gone (file)")
        r_ = str(Core.pickTotem(ou, OWNER, 0, 0, TT))
        lt4 = Inv.totems(TT)
        hs = [x for x in lt4 if str(x[2]) == "Skyy_Totem_HarvestSpirit"]
        K.check(r_.startswith("+Harvest Spirit I") and len(hs) == 1 and len(str(Tot.dstr(hs[0][3], "uid"))) == 12 and len(list(Tot.entries(St.readNow(OWNER), 0))) == 0,
                "X16 the 0.1 starter totem (no uid) gets one when picked up: %s" % r_)
        K.check(str(Core.pickTotem(ou, OWNER, 0, 0, TT)).startswith("-That totem is gone"), "X16 nothing on that pad any more")
        # place back up to the pad limit (Small = 3 pads)
        for i_ in range(3):
            Inv.giveStack(TT, Tot.stack(JArray(JString)(["fertilizer", "1", "", "", "0", "f%d" % i_]), JLong(NOW)))
        res_ = []
        for i_ in range(5):
            l_ = [x for x in Inv.totems(TT)]
            if not l_:
                break
            res_.append(str(Core.placeTotem(ou, OWNER, 0, int(l_[0][0]), int(l_[0][1]), TT))[:1])
        K.check(res_[:3] == ["+", "+", "+"] and res_[3] == "-" and len(list(Tot.entries(St.readNow(OWNER), 0))) == 3,
                "X16 a Small island takes 3 totems; the 4th is refused (pads full): %s" % res_)
        # a Mining totem cannot be placed on a Farming island
        TQ = inv(2, 1, 1)
        Inv.giveStack(TQ, Tot.stack(JArray(JString)(["quarry_spirit", "1", "", "", "0", "q1"]), JLong(NOW)))
        lq = Inv.totems(TQ)
        r_ = str(Core.placeTotem(ou, OWNER, 1, int(lq.get(0)[0]), int(lq.get(0)[1]), TQ))
        K.check(r_.startswith("-That slot has no island") or "later update" in r_, "X16 refused: %s" % r_)
        r_ = str(Core.placeTotem(ou, OWNER, 0, int(lq.get(0)[0]), int(lq.get(0)[1]), TQ))
        K.check("Mining Shard" in r_ and int(Inv.count(TQ, "Skyy_Totem_QuarrySpirit")) == 1, "X16 a Mining totem on the Farming island: refused, kept: %s" % r_)
        K.check(str(Core.placeTotem(vu, OWNER, 0, 0, 0, TT)).startswith("-Only the island owner and co-op"), "X16 a visitor cannot place")
        # fix3: a co-op member (even with shard.coopCollect on) cannot place / pick up / add or remove modifiers / boost; nothing moves
        Cfg.COOP_COLLECT = True
        TM = inv(4, 1, 1)
        Inv.giveStack(TM, Tot.stack(JArray(JString)(["rain", "1", "", "", "0", "mx1"]), JLong(NOW)))
        Inv.give(TM, "Skyy_TotemMod_Wider", JLong(1)); Inv.give(TM, "Ingredient_Water_Essence", JLong(1))
        _f0 = Tot.parse(list(Tot.entries(St.get(OWNER), 0))[0]); _f0[2] = "wider"
        Core.put(St.get(OWNER), 0, 0, _f0)
        St.save(OWNER, St.get(OWNER))
        _bt = str(St.readNow(OWNER).getProperty("farming.i0.totems"))
        lm_ = Inv.totems(TM)
        _rc = [str(Core.placeTotem(mu, OWNER, 0, int(lm_.get(0)[0]), int(lm_.get(0)[1]), TM)), str(Core.pickTotem(mu, OWNER, 0, 0, TM)),
               str(Core.addMod(mu, OWNER, 0, 1, 0, TM)), str(Core.removeMod(mu, OWNER, 0, 0, 1, TM)), str(Core.addBooster(mu, OWNER, 0, 0, TM))]
        Cfg.COOP_COLLECT = False
        K.check(all(x_.startswith("-Only the island owner can place, pick up or change totems") for x_ in _rc)
                and str(St.readNow(OWNER).getProperty("farming.i0.totems")) == _bt and ":wider:" in _bt and Inv.totems(TM).size() == 1
                and int(Inv.count(TM, "Skyy_TotemMod_Wider")) == 1 and int(Inv.count(TM, "Ingredient_Water_Essence")) == 1,
                "X16 fix3: co-op with coopCollect ON refused on place / pick up / add mod / remove mod / booster, file + inventory unchanged: %s" % [x_[:40] for x_ in _rc])
        # fix3: a crash copy (the uid of a placed totem) is refused and removed - never placed twice
        _e3 = list(Tot.entries(St.readNow(OWNER), 0))
        _u1 = str(Tot.parse(_e3[1])[5])
        r_ = str(Core.pickTotem(ou, OWNER, 0, 0, TT))   # frees a pad, so only the uid check can refuse
        TD = inv(2, 1, 1)
        Inv.giveStack(TD, Tot.stack(JArray(JString)(["fertilizer", "1", "", "", "0", _u1]), JLong(NOW)))
        ld_ = Inv.totems(TD)
        r2_ = str(Core.placeTotem(ou, OWNER, 0, int(ld_.get(0)[0]), int(ld_.get(0)[1]), TD))
        _e4 = list(Tot.entries(St.readNow(OWNER), 0))
        K.check(r_.startswith("+") and r2_.startswith("-This totem is already placed on island 1") and "removed" in r2_ and Inv.totems(TD).size() == 0
                and len(_e4) == 2 and sum(1 for x_ in _e4 if str(Tot.parse(x_)[5]) == _u1) == 1,
                "X16 fix3: the duplicate uid %s is refused and the copy removed; still exactly one on the island: %s" % (_u1, r2_))
        # modifiers: counted, two slots, back on removal
        St.get(OWNER).setProperty("farming.i0.totems", "harvest_spirit:1::::w")
        Inv.give(TT, "Skyy_TotemMod_Wider", JLong(3))
        r1_ = str(Core.addMod(ou, OWNER, 0, 0, 0, TT))
        r2_ = str(Core.addMod(ou, OWNER, 0, 0, 0, TT))
        r3_ = str(Core.addMod(ou, OWNER, 0, 0, 0, TT))
        ent_ = str(list(Tot.entries(St.readNow(OWNER), 0))[0])
        K.check(r1_.startswith("+Wider Area added") and r2_.startswith("+Wider Area added") and r3_.startswith("-Both modifier slots are full")
                and int(Inv.count(TT, "Skyy_TotemMod_Wider")) == 1 and ent_.startswith("harvest_spirit:1:wider:wider:"),
                "X16 modifiers: 2 added (3 -> 1 in the inventory), the third refused (file %s)" % ent_)
        _rw = float(Mth.rate(St.get(OWNER), 0, JLong(NOW)))
        K.check(abs(_rw - 108.0 / 20) < 1e-9, "X16 two Wider Areas: range 3 + 4 = 7 reaches 108 crops of the Small island = 5.4 / min")
        St.FAIL_TEST = True
        r4_ = str(Core.removeMod(ou, OWNER, 0, 0, 1, TT))
        St.FAIL_TEST = False
        K.check(r4_.startswith("-Could not be saved") and int(Inv.count(TT, "Skyy_TotemMod_Wider")) == 1, "X16 remove with a refused save: the modifier is taken back")
        r5_ = str(Core.removeMod(ou, OWNER, 0, 0, 1, TT))
        K.check(r5_.startswith("+Wider Area is back") and int(Inv.count(TT, "Skyy_TotemMod_Wider")) == 2 and str(list(Tot.entries(St.readNow(OWNER), 0))[0]).startswith("harvest_spirit:1::wider:"),
                "X16 remove modifier 1: the item is back (file)")
        K.check(str(Core.removeMod(ou, OWNER, 0, 0, 1, TT)).startswith("=That modifier slot is empty"), "X16 an empty slot")
        K.check(str(Core.addMod(ou, OWNER, 0, 0, 3, TT)).startswith("-You have no Compost"), "X16 a modifier you do not have")
        # booster
        r6_ = str(Core.addBooster(ou, OWNER, 0, 0, TT))
        Inv.give(TT, "Ingredient_Water_Essence", JLong(2))
        r7_ = str(Core.addBooster(ou, OWNER, 0, 0, TT))
        r8_ = str(Core.addBooster(ou, OWNER, 0, 0, TT))
        f_ = list(Tot.parse(list(Tot.entries(St.readNow(OWNER), 0))[0]))
        K.check(r6_.startswith("-A booster is 1 Life, Water or Void Essence") and r7_.startswith("+Booster burning for 60 min") and r8_.startswith("=A booster is already burning")
                and int(Inv.count(TT, "Ingredient_Water_Essence")) == 1 and int(f_[4]) == NOW + 120000 + 3600000,
                "X16 booster: none = refused; 1 essence burns 1 h (file); a second is refused (1 of 2 left)")
        # range circle + upgrade line
        K.check(str(Core.showRange(OWNER, 0, 0)).startswith("=Range 7 blocks") and Core.RANGE.containsKey("skyy-shard-" + OWNER), "X16 Show range: 10 s of sparkles (range 3 + 2 Wider + 2 booster)")
        K.check("next SkyyGear update" in str(Core.upgrade(ou)), "X16 Upgrade without SkyyGear's Anvil: says so")
        _anv = []
        fns.put("gear:fn:anvil:open", PyFn(lambda u: (_anv.append(str(u)), Bool.TRUE)[1]))
        K.check(str(Core.upgrade(ou)).startswith("+Opening the Anvil") and _anv == [OWNER], "X16 ... with gear:fn:anvil:open: the Anvil opens")
        fns.remove("gear:fn:anvil:open")

        # ---- Collect pays the bonus Enchanted crops (x 100 as wheat for XP + collections)
        po = St.get(OWNER)
        po.setProperty("farming.i0.stored", "10"); po.setProperty("farming.i0.ench", "2"); po.setProperty("farming.i0.last", str(NOW + 120000))
        St.save(OWNER, po)
        TC = inv(3, 1, 1)
        n0x, n0c = len(xp_calls), len(coll_calls)
        collect_ok[0] = True
        r_ = str(Core.collect(ou, OWNER, -1, TC))
        K.check(r_.startswith("+Collected 10 Wheat + 2 Enchanted Wheat") and int(Inv.count(TC, "Plant_Crop_Wheat_Item")) == 10 and int(Inv.count(TC, "Skyy_Ench_Wheat")) == 2
                and xp_calls[n0x][2] == 420 and [c[2] for c in coll_calls[n0c:]] == [210] and int(Mth.ench(St.readNow(OWNER), 0)) == 0,
                "X16 Collect gives the Enchanted crops too: XP (10 + 200) x 4 x 50 %% = 420, collection 210 (file ench 0): %s" % r_)

        # ---- crafting (the menu) + the Rebirth R9 gate
        TK = inv(4, 1, 1)
        ri_hs = list(Cfg.CRAFT_ID).index("Skyy_Totem_HarvestSpirit")
        ri_sh = list(Cfg.CRAFT_ID).index("Skyy_Shard_Farming")
        ri_wd = list(Cfg.CRAFT_ID).index("Skyy_TotemMod_Wider")
        K.check(str(Core.craft(ou, ri_hs, TK)).startswith("-You need 128 Wheat"), "X16 craft: missing items = refused")
        Inv.give(TK, "Plant_Crop_Wheat_Item", JLong(200)); Inv.give(TK, "Ingredient_Life_Essence", JLong(20))
        coins["bal"] = 100
        K.check(str(Core.craft(ou, ri_hs, TK)).startswith("-You need 500 coins") and int(Inv.count(TK, "Plant_Crop_Wheat_Item")) == 200, "X16 craft: too few coins, nothing taken")
        coins["bal"] = 10000
        coins_fail[0] = True
        r_ = str(Core.craft(ou, ri_hs, TK))
        coins_fail[0] = False
        K.check(r_.startswith("-The items or coins could not be taken") and int(Inv.count(TK, "Plant_Crop_Wheat_Item")) == 200 and int(Inv.count(TK, "Ingredient_Life_Essence")) == 20,
                "X16 craft: the coins fail after the items - every item is back (200 / 20)")
        r_ = str(Core.craft(ou, ri_hs, TK))
        lk = [x for x in Inv.totems(TK) if str(x[2]) == "Skyy_Totem_HarvestSpirit"]
        K.check(r_.startswith("+Crafted Harvest Spirit I") and int(Inv.count(TK, "Plant_Crop_Wheat_Item")) == 72 and int(Inv.count(TK, "Ingredient_Life_Essence")) == 12
                and coins["bal"] == 9500 and len(lk) == 1 and int(Tot.dlong(lk[0][3], "tier")) == 1 and len(str(Tot.dstr(lk[0][3], "uid"))) == 12,
                "X16 crafted: 128 Wheat + 8 Life Essence + 500 coins -> a Harvest Spirit I with its own document")
        # no room for the output: everything back
        TK2 = inv(3)
        Inv.give(TK2, "Skyy_Ench_Wheat", JLong(4)); Inv.give(TK2, "Ingredient_Life_Essence", JLong(32)); Inv.give(TK2, "Rock_Stone", JLong(100))
        r_ = str(Core.craft(ou, ri_wd, TK2))
        K.check(r_.startswith("-Make room") and int(Inv.count(TK2, "Skyy_Ench_Wheat")) == 4 and int(Inv.count(TK2, "Ingredient_Life_Essence")) == 32 and coins["bal"] == 9500,
                "X16 craft with no room for the output: items and coins back: %s" % r_)
        # R9: an extra shard only from rebirth 2 (rebirth:fn:count)
        Inv.give(TK, "Skyy_Ench_Wheat", JLong(40)); Inv.give(TK, "Ingredient_Life_Essence", JLong(70))
        coins["bal"] = 500000
        _pl = str(St.get(OWNER).getProperty("farming.placed"))
        St.get(OWNER).remove("farming.placed")   # the owner's shard picked up (and stored somewhere): its islands stay = it HAD one
        nu = UUID.fromString("0d0d0d0d-1111-2222-3333-666666666666")   # fix4: a profile that never had a Farming Shard
        g0 = str(Core.craftGate(nu, ri_sh))
        rb = {"n": None}
        fns.put("rebirth:fn:count", PyFn(lambda k: None if rb["n"] is None else JInt(rb["n"])))
        g1 = str(Core.craftGate(nu, ri_sh))
        rb["n"] = 1
        r1s = str(Core.craft(nu, ri_sh, TK))
        rb["n"] = 2
        sh0 = int(Inv.count(TK, "Skyy_Shard_Farming"))
        g_own = str(Core.craftGate(ou, ri_sh))
        K.check(g_own.startswith("You already have your Farming Shard"),
                "X16 fix4: a picked-up shard (in a chest / vault / auction, not in the inventory) = the profile HAD one = refused: %s" % g_own)
        _w0, _l0, _c00 = int(Inv.count(TK, "Skyy_Ench_Wheat")), int(Inv.count(TK, "Ingredient_Life_Essence")), coins["bal"]
        St.FAIL_TEST = True
        rfs = str(Core.craft(nu, ri_sh, TK))
        St.FAIL_TEST = False
        K.check(rfs.startswith("-Your shard file could not be saved - everything is back") and int(Inv.count(TK, "Skyy_Shard_Farming")) == sh0
                and int(Inv.count(TK, "Skyy_Ench_Wheat")) == _w0 and int(Inv.count(TK, "Ingredient_Life_Essence")) == _l0 and coins["bal"] == _c00
                and St.get(str(nu)).getProperty("farming.crafted") is None,
                "X16 fix4: the crafted mark could not be saved = no shard, items + coins back, no mark: %s" % rfs)
        r2s = str(Core.craft(nu, ri_sh, TK))
        _mk = St.readNow(str(nu)).getProperty("farming.crafted")
        K.check("needs rebirth 2 (you: 0)" in g0 and "still loading" in g1 and r1s.startswith("-Crafting a shard needs rebirth 2 (you: 1)")
                and r2s.startswith("+Crafted Farming Shard") and int(Inv.count(TK, "Skyy_Shard_Farming")) == sh0 + 1 and coins["bal"] == 400000,
                "X16 REBIRTH R9 GATE: no SkyyRebirth = 0 refused, loading = refused, rebirth 1 refused, rebirth 2 crafts a shard (100,000 coins)")
        K.eq(str(_mk), "1", "X16 fix4: the crafted mark farming.crafted = 1 is on disk")
        _c0 = coins["bal"]
        r3s = str(Core.craft(nu, ri_sh, TK))
        Inv.take(TK, "Skyy_Shard_Farming", JLong(1))   # the crafted shard goes into a chest / to a friend
        g4 = str(Core.craftGate(nu, ri_sh))
        St.get(OWNER).setProperty("farming.placed", _pl)
        g3 = str(Core.craftGate(ou, ri_sh))
        K.check(r3s.startswith("-You already have your Farming Shard") and int(Inv.count(TK, "Skyy_Shard_Farming")) == sh0 and coins["bal"] == _c0
                and g3.startswith("You already have your Farming Shard") and g4.startswith("You already have your Farming Shard"),
                "X16 fix4: one Farming Shard per profile, ever - in the inventory, stored away after crafting, or placed = refused, nothing taken: %s / %s / %s" % (r3s, g4, g3))
        Cfg.SHARD_RB = 0
        St.get(str(nu)).remove("farming.crafted")
        K.check(Core.craftGate(nu, ri_sh) is None, "X16 craft.shardRebirth 0 = any profile that never had a shard")
        Cfg.SHARD_RB = 2
        St.get(OWNER).setProperty("farming.placed", _pl)
        # fix3: no page rebuild after another mod's page (the Anvil) took the screen
        K.eq([bool(Page.handedOff("tup", "+Opening the Anvil")), bool(Page.handedOff("tup", "=Totems tier up on the Anvil")), bool(Page.handedOff("tpick", "+x"))],
             [True, False, False], "X16 fix3: handedOff only after the Anvil opened (no rebuild / close then)")
        # fix3: /shardadmin give / totem touch an inventory only on its own world thread
        Adm.THREAD_TEST = PyFn(lambda r: Bool.FALSE)
        _st1 = bool(Adm.sameThread(None))
        Adm.THREAD_TEST = PyFn(lambda r: Bool.TRUE)
        _st2 = bool(Adm.sameThread(None))
        Adm.THREAD_TEST = None
        K.eq([_st1, _st2, bool(Adm.sameThread(None))], [False, True, False], "X16 fix3: sameThread (another world = refused; no store = refused)")
        Adm.THREAD_TEST = PyFn(lambda r: Bool.TRUE)
        _ga = Adm.giveGate(ou, "Tester", None)
        br.put("profile:busy:" + OWNER, Bool.TRUE)
        _gb = str(Adm.giveGate(ou, "Tester", None))
        br.remove("profile:busy:" + OWNER)
        Adm.THREAD_TEST = PyFn(lambda r: Bool.FALSE)
        _gc = str(Adm.giveGate(ou, "Tester", None))
        Adm.THREAD_TEST = None
        K.check(_ga is None and "is switching profile" in _gb and "is in another world" in _gc,
                "X16 fix4: /shardadmin give / totem gate: same world = go on, profile:busy = refused, another world = refused: %s / %s" % (_gb, _gc))
        # fix4: right-click selects the statue looked at (its block origin), the player's own spot only without one
        _ap = list(Page.aimPoint(JClass("org.joml.Vector3i")(10, 64, -3), 99.0, 99.0))
        _af = list(Page.aimPoint(None, 7.25, -1.5))
        K.eq([_ap, _af], [[10.5, -2.5], [7.25, -1.5]], "X16 fix4: aimPoint = the looked-at block's centre, else the player's x / z")
        _cr = Cfg.CRAFT
        _cr[ri_hs] = ""
        K.check("switched off" in str(Core.craftGate(ou, ri_hs)), "X16 an empty recipe = switched off")
        _cr[ri_hs] = "Plant_Crop_Wheat_Item:128,Ingredient_Life_Essence:8;500"
        K.check(Core.recipe("a:1,b:x;5") is None and Core.recipe("") is None and Core.recipe(";0") is None and Core.recipe("a:1;-5") is None
                and list(Core.recipe("a:2;7")[1]) == [2], "X16 recipe parsing (bad text = off)")
        K.check(str(Core.craft(ou, 99, TK)).startswith("-Pick a recipe"), "X16 a bad recipe index")
        # ---- shard:fn:totem (SkyyGear's Anvil, later)
        tf = TFn()
        A_ = lambda *a: JArray(JObject)([JString(x) if isinstance(x, str) else x for x in a])
        js = str(Tot.doc(JArray(JString)(["harvest_spirit", "1", "wider", "", "0", "zz9"]), JLong(0)).toJson())
        up_ = str(tf.apply(A_("up", "Skyy_Totem_HarvestSpirit", js)))
        upd = JClass("org.bson.BsonDocument").parse(up_)
        K.check(str(tf.apply(A_("key"))) == "SkyyTotem" and str(tf.apply(A_("cost", "Skyy_Totem_HarvestSpirit", js))) == "Skyy_Ench_Wheat:1,Ingredient_Life_Essence:10"
                and int(Tot.dlong(upd, "tier")) == 2 and str(Tot.dstr(upd, "uid")) == "zz9" and str(Tot.dstr(upd, "m1")) == "wider",
                "X16 shard:fn:totem: key, cost I->II (1 Enchanted Wheat + 10 Life Essence), up = tier 2 with the same uid / modifiers")
        js5 = str(Tot.doc(JArray(JString)(["rain", "5", "", "", "0", "r5"]), JLong(0)).toJson())
        K.check(str(tf.apply(A_("cost", "Skyy_Totem_Rain", js5))) == "err:max tier" and str(tf.apply(A_("up", "Rock_Stone", js))).startswith("err:not a totem")
                and str(tf.apply(A_("cost", "Skyy_Totem_QuarrySpirit", ""))).startswith("err:its shard") and str(tf.apply(A_("up", "Skyy_Totem_Rain", js))).startswith("err:the document is another")
                and "Harvest Spirit I" in str(tf.apply(A_("describe", "Skyy_Totem_HarvestSpirit", js))) and str(tf.apply("x")).startswith("err:"),
                "X16 shard:fn:totem refuses: max tier, not a totem, a later shard, a mismatched document, bad arguments")
        K.eq([list(Tot.upCost(t_)) if Tot.upCost(t_) is not None else None for t_ in range(0, 6)], [None, [1, 10], [2, 25], [3, 50], [5, 100], None], "X16 tier-up costs I->II .. IV->V")
        # ---- the Totems / Craft tabs: builds + clicks
        Page.TEST_INV = TT
        St.get(OWNER).setProperty("farming.i0.totems", "harvest_spirit:2:wider::0:aa,rain:1::::bb")
        pg = Page(ou, worlds["hub"])
        pg.tab = 3
        b, ev = UCB(), UEB()
        pg.build(None, b, ev, None)
        bnd = [str(e.selector) for e in ev.getEvents()]
        K.check(all(x in bnd for x in ("#SkyyShTRow0Btn", "#SkyyShTRow1Btn", "#SkyyShTModAdd", "#SkyyShTPick", "#SkyyShTBoost", "#SkyyShTUp", "#SkyyShTab4"))
                and int(pg.tN) == 2 and str(pg.dTitle).startswith("Harvest Spirit II") and int(CP("SkyySh", True, True, LIFE.CanDismiss, b.getCommands(), ev.getEvents()).computeSize()) < int(CP.MAX_SIZE),
                "X16 the Totems tab: 2 totem rows, the selected totem's page + its buttons (one packet)")
        seq = [str(pg.act(a_, None, None)) for a_ in ("tsel1", "trange", "tup", "tmodnext", "tpick", "tpick")]
        K.check(seq[1].startswith("=Range") and seq[2] == "=test: anvil" and seq[4].startswith("=Click Pick up again") and seq[5].startswith("+Rain Totem I"),
                "X16 Totems clicks: select, range, upgrade, pick up asks twice then picks: %s" % seq)
        pg.tab = 3
        b, ev = UCB(), UEB(); pg.build(None, b, ev, None)
        pl_ = int(pg.pN)
        r_ = str(pg.act("tplace0", None, None)) if pl_ > 0 else "-none"
        K.check(pl_ > 0 and r_[0] in "+-", "X16 Place from the inventory row: %s" % r_)
        pg.tab = 4
        b, ev = UCB(), UEB(); pg.build(None, b, ev, None)
        bnd = [str(e.selector) for e in ev.getEvents()]
        K.check(all(("#SkyyShKRow%dBtn" % i) in bnd for i in range(7)) and "#SkyyShKCraft" in bnd and "#SkyyShKNext" in bnd and int(pg.kN) == 7
                and int(CP("SkyySh", True, True, LIFE.CanDismiss, b.getCommands(), ev.getEvents()).computeSize()) < int(CP.MAX_SIZE),
                "X16 the Craft tab: 7 recipe rows, Previous / Next, Craft (one packet)")
        for a_ in ("knext", "knext", "knext"):
            pg.act(a_, None, None)
        b, ev = UCB(), UEB(); pg.build(None, b, ev, None)
        pg.act("ksel3", None, None)
        b, ev = UCB(), UEB(); pg.build(None, b, ev, None)
        K.check(int(pg.kPage) == 2 and int(pg.kSel) == 17 and str(pg.kTitle) == "Farming Shard" and int(pg.kN) == 4,
                "X16 Craft paging: page 3 of 3 (clamped), the shard recipe selected: %s / %s" % (pg.kTitle, list(pg.kTx)[:3]))
        r_ = str(pg.act("kcraft", None, None))
        K.check(r_[0] in "+-", "X16 the Craft button crafts (or says why): %s" % r_)
        pg.act("kprev", None, None)
        K.check(int(pg.kPage) == 1, "X16 Previous")
        # the totem-block page factory: tab 3 + nearest
        pf_ = P("ShPageFn")(True).apply(None)
        K.check(bool(pf_.fromTotem) and bool(pf_.near) and int(pf_.tab) == 3, "X16 a totem block opens the menu on the Totems tab (nearest totem)")
        Page.TEST_INV = TI
    K.save()


# ====================================================================================================== D: start twice on live data
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Cfg, St = JClass(PKG + "ShCfg"), JClass(PKG + "ShStore")
    Paths = JClass("java.nio.file.Paths")
    mods = os.path.dirname(home)
    isl = os.path.join(mods, "Skyy_SkyyIslands")
    h0 = HK.tree_hash(isl) if os.path.isdir(isl) else None
    sh = os.path.join(mods, "Skyy_SkyyShards")
    K.check(not os.path.exists(sh), "D the live data has no Skyy_SkyyShards yet (a new mod)")
    for start in (1, 2):
        Cfg.DIR = Paths.get(sh)
        Cfg.FILE = Paths.get(os.path.join(sh, "config.properties"))
        r = str(Cfg.loadCfg(True))
        St.DIR = Paths.get(os.path.join(sh, "shards"))
        St.CACHE.clear()
        files = sorted(os.listdir(sh))
        if start == 1:
            K.check(r.startswith("default config.properties written") and files == ["config.properties"], "D start 1 writes only config.properties: %s" % files)
            m1 = os.path.getmtime(os.path.join(sh, "config.properties"))
        else:
            K.check(not r.startswith("default") and files == ["config.properties"] and os.path.getmtime(os.path.join(sh, "config.properties")) == m1,
                    "D start 2 writes nothing")
    if h0 is not None:
        K.check(HK.tree_hash(isl) == h0, "D the copied Skyy_SkyyIslands is byte-identical")
    K.save()


# ====================================================================================================== C01: class compare 0.1 -> 0.2
OLD01 = os.path.join(HERE, "SkyyShards-0.1.jar")
# every 0.1 member 0.2 drops on purpose: the size-factor maths (the totem range decides) and its config fields
GONE_OK = {"ShCfg": {"f F_MED", "f F_LARGE"}, "ShMath": {"m totemRate", "m factor", "m rate", "m msToFull"}}
NEW_CLASSES = {"ShTotem", "ShTotemFn", "ShRange"}


def run_cmp01(out, jar, scratch, _home):
    from jpype import JClass
    import zipfile
    K = HK.Child(out)
    HK.jvm([B.JAVASSIST], verify=False)
    CPc = JClass("javassist.ClassPool")

    def pool_of(j):
        p_ = CPc(False)
        p_.appendSystemPath()
        p_.appendClassPath(B.SERVER_JAR)
        p_.appendClassPath(j)
        return p_

    def classes(j):
        with zipfile.ZipFile(j) as z:
            return sorted(n[:-6].replace("/", ".") for n in z.namelist() if n.endswith(".class") and n.startswith("com/skyy/shards/"))
    a, b = classes(OLD01), classes(jar)
    pa, pb = pool_of(OLD01), pool_of(jar)
    K.eq(sorted(x for x in a if x not in b), [], "C01: no 0.1 class is gone")
    K.eq(sorted(x[len(PKG):] for x in b if x not in a), sorted(NEW_CLASSES), "C01: the new classes = ShTotem, ShTotemFn, ShRange")

    def sigs(p_, cn):
        c_ = p_.get(cn)
        out_ = set()
        for f_ in c_.getDeclaredFields():
            out_.add("f " + str(f_.getName()))
        for m_ in c_.getDeclaredMethods():
            out_.add("m " + str(m_.getName()) + str(m_.getSignature()))
        return out_
    lost, changed = {}, 0
    for cn in a:
        if cn not in b:
            continue
        sa, sb = sigs(pa, cn), sigs(pb, cn)
        short = cn[len(PKG):]
        gone = sorted(x for x in sa - sb)
        bad = [x for x in gone if x.split("(")[0] not in GONE_OK.get(short, set())]
        if bad:
            lost[short] = bad
        if sa != sb:
            changed += 1
    K.check(not lost, "C01: every 0.1 field / method signature is still there, except the size-factor maths 0.2 replaces on purpose: %s" % lost)
    K.notes.append("C01: %d of %d 0.1 classes changed members (totems), %d new" % (changed, len(a), len(b) - len(a)))
    print("C01. class compare SkyyShards-0.1.jar -> 0.2: %d classes, %d with changed members, new %s" % (len(a), changed, sorted(NEW_CLASSES)))
    K.save()


def old_jar():
    """a new mod has no older jar: the harness kit's class compare runs against a copy of this jar whose manifest says 0.0 (so exactly
    manifest.json differs and every class must be identical) - kept OUTSIDE the scratch folder the kit empties"""
    import zipfile
    d = os.path.join(os.path.dirname(SCRATCH), "oldjar")
    os.makedirs(d, exist_ok=True)
    o = os.path.join(d, "SkyyShards-0.0.jar")
    with zipfile.ZipFile(JAR) as zi, zipfile.ZipFile(o, "w", zipfile.ZIP_DEFLATED) as zo:
        for n in zi.namelist():
            data = zi.read(n)
            if n == "manifest.json":
                m = json.loads(data.decode("utf-8"))
                m["Version"] = "0.0"
                data = json.dumps(m, indent=2).encode("utf-8")
            zo.writestr(n, data)
    return o


if __name__ == "__main__":
    _old = old_jar() if "--phase" not in sys.argv else os.path.join(os.path.dirname(SCRATCH), "oldjar", "SkyyShards-0.0.jar")
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=_old, pkg=PKG, scratch=SCRATCH, expect={}, added=[],
           phases=[("exec", run_exec), ("cmp01", run_cmp01), ("live", run_live)], script=__file__,
           live=(os.path.join(LIVE_DIR, "Skyy_SkyyIslands"), "mods/Skyy_SkyyIslands"))
