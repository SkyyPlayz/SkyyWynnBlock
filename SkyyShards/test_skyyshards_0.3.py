"""Harness for SkyyShards 0.3 (Gathering phase 7: the other five shards, Auto-Compactor, Time Compressor, Soul Cages, the /shardadmin fix).
Build first: python SkyyShards/build_skyyshards_0.3.py

    python SkyyShards/test_skyyshards_0.3.py [--keep]

0.3 adds (every new code path): X17 = the five shards per kind - ShKind tables, starters (Copper / Oak / Chicken / Apple / Skeleton +
their worker I = 1 / min), RATE MATH per shard (15 cases: workers only in their shards, supports, rare-find / smelt totems, the Time
Compressor), rare finds (chance, Rare Finder, seeded rolls), 500 random CONSERVATION sequences over the five shards, the LAYOUT per shard
(own chunks, own stand, style, regrow list = its gatherables, pads free, Small in Medium in Large), PROTECTION (ore nodes / trunks /
apples yes, leaves / hay / stone no), placement + pick up per kind (one portal per kind, Farming untouched), COLLECT per shard on real
containers (Mining XP + Emerald finds, Auto-Smelt + Auto-Compactor I, Foraging + Tree Sap, Ranching, Orchard, COMBAT = NO XP, owed XP per
skill, what does not fit goes back to its island), compactor / compressor purchases (refunds, tiers, storage x2, the clock split), Grow
per shard, totems across shards (refused in the wrong shard, uid unique over every shard, pick up / modifiers / booster on a Mining
island), crafting (Soul Cage gate on armory:fn:soulcage, a shard per kind from rebirth 2), shard:fn:totem prices per shard, THE PAGE per
shard (6 x 6 builds, icons, Upgrades buttons, the Shards tab + switching), the tick mask, /shardadmin text paths. N = the game's own
command parser on /shardadmin (every 0.3 line parses; 0.2 refuses them = the CONTROL). C02 = class compare 0.2 -> 0.3. X1 - X16 are
0.2's checks, unchanged except the 6th tab, the 32 recipes (5 craft pages) and the Mining totem's price (they run on 0.3's Farming paths).

0.2's text follows.

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

VERSION = "0.3"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)))
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "shards03", "h")))
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
        _k3 = [(x, 100) for x in ("Ore_Copper", "Ingredient_Bar_Copper", "Skyy_Ench_Copper", "Skyy_Ench_Oak", "Skyy_Ench_Cobblestone", "Wood_Oak_Trunk",
                                  "Ingredient_Tree_Sap", "Rock_Gem_Emerald", "Food_Chicken_Raw", "Plant_Fruit_Apple", "Plant_Sapling_Apple", "Ingredient_Bone_Fragment",
                                  "Ingredient_Fabric_Scrap_Linen")] + [("Weapon_Wand_SoulOrb", 1)] + [("Skyy_Shard_" + x, 1) for x in ("Mining", "Foraging", "Ranching", "Orchard", "Combat")]
        item_store([("Plant_Crop_Wheat_Item", 100), ("Skyy_Ench_Wheat", 100), ("Plant_Seeds_Wheat_Eternal", 100), ("Skyy_Shard_Farming", 1), ("Rock_Stone", 100)]
                   + _tot_ids + _mod_ids + _ess + _k3)
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
        for tab in range(6):   # 0.3: + the Shards tab
            for sel in (range(6) if tab == 2 else (0,)):
                pg, cmds, evs, sets, apps, mk, binds = build(ou, wn, tab, sel)
                views[vname] = int(pg.view)
                size = int(CP("SkyySh", True, True, LIFE.CanDismiss, cmds, evs).computeSize())
                sizes.append(size)
                for bnd in binds:
                    if ("#" + bnd.lstrip("#") + " ") not in mk.replace("{", " ").replace(";", " ") and (bnd.lstrip("#") + " {") not in mk:
                        unbound.append((vname, tab, bnd))
    K.eq(views, {"portal": 0, "hub": 1, "menu": 2}, "X13 the view: portal on the owner's island, hub in the shard world, menu elsewhere")
    K.check(max(sizes) < int(CP.MAX_SIZE), "X13 every build (3 views x 6 tabs x 6 slots) is one CustomPage packet: max %d bytes of %d" % (max(sizes), int(CP.MAX_SIZE)))
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
        K.check(r_.startswith("-That slot has no island") or "Mining Shard" in r_, "X16 refused: %s" % r_)
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
                and str(tf.apply(A_("cost", "Skyy_Totem_QuarrySpirit", ""))) == "Skyy_Ench_Cobblestone:1,Ingredient_Life_Essence:10" and str(tf.apply(A_("up", "Skyy_Totem_Rain", js))).startswith("err:the document is another")
                and "Harvest Spirit I" in str(tf.apply(A_("describe", "Skyy_Totem_HarvestSpirit", js))) and str(tf.apply("x")).startswith("err:"),
                "X16 shard:fn:totem refuses: max tier, not a totem, a mismatched document, bad arguments (0.3: a Mining totem is priced in Enchanted Cobblestone)")
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
        for a_ in ("knext", "knext"):
            pg.act(a_, None, None)
        b, ev = UCB(), UEB(); pg.build(None, b, ev, None)
        pg.act("ksel3", None, None)
        b, ev = UCB(), UEB(); pg.build(None, b, ev, None)
        K.check(int(pg.kPage) == 2 and int(pg.kSel) == 17 and str(pg.kTitle) == "Farming Shard" and int(pg.kN) == 7,
                "X16 Craft paging: page 3 of 5 (0.3: 32 recipes), the Farming Shard recipe selected: %s / %s" % (pg.kTitle, list(pg.kTx)[:3]))
        for a_ in ("knext", "knext", "knext", "knext"):
            pg.act(a_, None, None)
        b, ev = UCB(), UEB(); pg.build(None, b, ev, None)
        K.check(int(pg.kPage) == 4 and int(pg.kN) == 4, "X16 Craft paging clamps at page 5 of 5 (4 rows)")
        pg.act("kprev", None, None); pg.act("kprev", None, None)
        r_ = str(pg.act("kcraft", None, None))
        K.check(r_[0] in "+-", "X16 the Craft button crafts (or says why): %s" % r_)
        pg.act("kprev", None, None)
        K.check(int(pg.kPage) == 1, "X16 Previous")
        # the totem-block page factory: tab 3 + nearest
        pf_ = P("ShPageFn")(True).apply(None)
        K.check(bool(pf_.fromTotem) and bool(pf_.near) and int(pf_.tab) == 3, "X16 a totem block opens the menu on the Totems tab (nearest totem)")
        Page.TEST_INV = TI
    # ---------------- X17 (0.3) THE OTHER FIVE SHARDS - every new code path per kind: tables, starters, rate math, rare finds, Auto-Smelt,
    # Time Compressor, Auto-Compactor, layouts + protection, placement / pick up, Collect (skill XP / no XP for Combat, credits), Grow,
    # totems across shards, crafting (Soul Cage gate, a shard per kind), shard:fn:totem prices, the page per shard + the Shards tab
    if INVOK:
        Kd = P("ShKind")
        Tot = P("ShTotem")
        Bool = JClass("java.lang.Boolean")
        Cfg.KEY_TEST = PyFn(lambda u: str(u))
        Role.WORLDKEY_TEST = None
        Role.WORLD_TEST = None
        Cfg.COOP_COLLECT = False
        open(os.path.join(base, "config.properties"), "w", encoding="utf-8").write(str(Cfg.DEFAULT_TEXT))
        Cfg.loadCfg(False)
        KN = ["Mining", "Foraging", "Farming", "Ranching", "Orchard", "Combat"]
        MI, FO, FA, RA, OR, CO = range(6)

        def soul_fn(ess):
            """the armory:fn:soulcage stand-in: Object[]{"essence", tier} -> ess; an item id -> its ladder place (Soul Orb 0, else -1)"""
            def ans(a):
                try:
                    nm = str(a.getClass().getName())
                except Exception:
                    nm = "java.lang.String"
                if nm.startswith("["):
                    return JString(ess)
                return JClass("java.lang.Integer")(0 if str(a) == "Weapon_Wand_SoulOrb" else -1)
            return PyFn(ans)
        # ---- X17a the tables
        K.check(list(Kd.KEYS) == [k.lower() for k in KN] and int(Kd.FARM) == 2 and [int(Kd.ofShard("Skyy_Shard_" + k)) for k in KN] == list(range(6))
                and int(Kd.ofShard("Skyy_Shard_Nope")) == -1 and [int(Kd.ofPage("SkyyShard" + k)) for k in KN] == list(range(6))
                and int(Kd.ofKey(" Combat ")) == 5 and int(Kd.ofKey("x")) == -1,
                "X17 ShKind: six keys / shard ids / page ids, Farming = 2 (0.2's index)")
        K.eq([int(Kd.ofX(x)) for x in (0.0, 511.0, 513.0, 1024.0, 2048.5, 5120.0, -9999.0, 99999.0)], [0, 0, 1, 1, 2, 5, 0, 5], "X17 ofX: the region of a world x")
        K.eq([str(Kd.bonusCredit(k)) for k in (MI, FO, FA, CO)], ["Rock_Gem_Emerald", "Ingredient_Tree_Sap", "Plant_Crop_Wheat_Item", "Ingredient_Fabric_Scrap_Linen"],
             "X17 the rare find's collection credit (Farming: Enchanted Wheat counts as Wheat)")
        K.eq([int(Cfg.xpOf(k)) for k in range(6)], [5, 6, 4, 2, 5, 0], "X17 XP per item per shard (Combat 0 = drops only)")
        K.eq([list(map(str, Cfg.growOf(k))) for k in (MI, FA, OR)], [["Skyy_Ench_Cobblestone", "2", "5"], ["Plant_Seeds_Wheat_Eternal", "8", "24"], ["Plant_Sapling_Apple", "8", "24"]],
             "X17 growOf: each shard's grow item (Farming = 0.2's rows)")
        _g = Cfg.GROWK
        _g[MI] = "broken"
        _gb = list(map(str, Cfg.growOf(MI)))
        _g[MI] = "Rock_Stone:3:7"
        _gc = list(map(str, Cfg.growOf(MI)))
        _g[MI] = str(Cfg.DEF_GROWK[MI])
        K.check(_gb == ["Skyy_Ench_Cobblestone", "2", "5"] and _gc == ["Rock_Stone", "3", "7"] and Cfg.parseGrow("a:1") is None and Cfg.parseGrow("a:-1:2") is None,
                "X17 a broken grow.<shard> row = the default (+ one WARN); a good one is used; parseGrow refuses bad text")
        # ---- X17b starters + rate math per kind
        starters = []
        for k in range(6):
            q_ = Props(); Mth.starter(k, q_, JLong(T0))
            kk = KN[k].lower()
            starters.append((str(q_.getProperty(kk + ".i0.type")), str(q_.getProperty(kk + ".i0.totems")), round(float(Mth.rate(k, q_, 0, JLong(T0))), 9)))
        K.eq(starters, [("copper", "quarry_spirit:1", 1.0), ("oak", "lumber_spirit:1", 1.0), ("wheat", "harvest_spirit:1", 1.0), ("chicken", "harvest_spirit:1", 1.0),
                        ("apple", "harvest_spirit:1", 1.0), ("skeleton", "soul_cage:1", 1.0)], "X17 every shard's starter: its island type + its worker I = 1 / min")

        def krate(k, ents, size=1, comp=0):
            q_ = Props(); Mth.starter(k, q_, JLong(T0)); kk = KN[k].lower()
            q_.setProperty(kk + ".i0.size", str(size)); q_.setProperty(kk + ".i0.totems", ents)
            if comp:
                q_.setProperty(kk + ".compressor", str(comp))
            return float(Mth.rate(k, q_, 0, JLong(T0)))
        kcases = [(MI, "quarry_spirit:1,geode_pole:3", 1, 0, 1.0, "a Geode Pole adds no percent (rare finds only)"),
                  (MI, "harvest_spirit:5", 1, 0, 0.0, "a Farming worker makes nothing in the Mining Shard"),
                  (MI, "quarry_spirit:1,autosmelt_pole:1", 1, 0, 1.0, "the Auto-Smelt Pole changes the item, not the rate"),
                  (MI, "quarry_spirit:1", 1, 1, 1.25, "Time Compressor I x1.25"),
                  (MI, "quarry_spirit:1", 1, 3, 2.0, "Time Compressor III x2"),
                  (FO, "lumber_spirit:2,fertilizer:1", 1, 0, 1.25 * 72 / 20 * 1.05, "Lumber Spirit II + Fertilizer I"),
                  (FO, "lumber_spirit:1,sap_tap:5", 1, 0, 1.0, "a Sap Tap adds no percent"),
                  (FO, "quarry_spirit:1", 1, 0, 0.0, "a Mining worker makes nothing in the Foraging Shard"),
                  (RA, "harvest_spirit:1,herd_pole:2,scarecrow:1", 1, 0, 1.15, "Ranching: Herd Pole II +10 % + Scarecrow I +5 %"),
                  (RA, "harvest_spirit:1,rain:5", 1, 0, 1.0, "Rain does not work in the Ranching Shard"),
                  (OR, "harvest_spirit:1,pollinator:5,season_ward:1", 1, 0, 1.30, "Orchard: Pollinator V +25 % + Season Ward I +5 %"),
                  (OR, "harvest_spirit:1,sun_blessing:5", 1, 0, 1.0, "the Blessing of the Sun is Farming-only"),
                  (CO, "soul_cage:1,lure_pole:1", 1, 0, 1.05, "Combat: Soul Cage I + Lure Pole I"),
                  (CO, "soul_cage:3", 2, 0, 1.5 * 140 / 20, "Soul Cage III on a Medium arena: range 7 = 140 spots"),
                  (CO, "harvest_spirit:1,trophy_pole:2", 1, 0, 0.0, "no Combat worker = nothing")]
        kbad = [(KN[k], e, round(krate(k, e, s, c), 6), round(w, 6), why) for (k, e, s, c, w, why) in kcases if abs(krate(k, e, s, c) - w) > 1e-9]
        K.check(not kbad, "X17 RATE MATH per shard: %d cases (workers only in their shards, supports, rare-find / smelt totems, Time Compressor) %s" % (len(kcases), kbad[:3]))
        # rare finds: chance + Rare Finders + the roll (seeded, never re-rolled; the shard's own numbers)
        qm = Props(); Mth.starter(MI, qm, JLong(T0)); qm.setProperty("pkey", OWNER); qm.setProperty("mining.storage", "5")
        qm.setProperty("mining.i0.totems", "quarry_spirit:5,geode_pole:3:rare::0:g1")
        K.check(abs(float(Tot.enchChance(MI, qm, 0)) - 0.015 * 2) < 1e-12 and float(Tot.enchChance(RA, qm, 0)) == 0.0 and not Tot.smelts(MI, qm, 0),
                "X17 Geode Pole III = 1.5 %% per ore x (1 + 1 Rare Finder); Ranching has no rare find; no smelt pole = no smelting")
        _bn = Cfg.BONUS
        _bn[2] = 50.0
        snap = Props(); snap.putAll(qm)
        mm = int(Mth.settle(MI, qm, 0, JLong(T0 + 300 * 60000)))
        e1 = int(Mth.ench(MI, qm, 0))
        snap2 = Props(); snap2.putAll(snap)
        Mth.settle(MI, snap2, 0, JLong(T0 + 300 * 60000))
        e2 = int(Mth.ench(MI, snap2, 0))
        # the same file as Farming keys rolls Farming's own numbers (0.2's seed) - a Mining roll differs from it
        qf = Props(); qf.putAll(snap)
        _bn[2] = 1.5
        K.check(mm > 0 and e1 == e2 and e1 == mm, "X17 Geode rolls (chance raised to 100 %% for the test): %d Emeralds of %d ores, the same when settled again (seeded)" % (e1, mm))
        _bn[1] = 25.0
        qh = Props(); Mth.starter(MI, qh, JLong(T0)); qh.setProperty("pkey", OWNER); qh.setProperty("mining.storage", "5"); qh.setProperty("mining.i0.totems", "quarry_spirit:5,geode_pole:2")
        qh2 = Props(); qh2.putAll(qh)
        mh = int(Mth.settle(MI, qh, 0, JLong(T0 + 600 * 60000)))
        eh = int(Mth.ench(MI, qh, 0))
        Mth.settle(MI, qh2, 0, JLong(T0 + 600 * 60000))
        _bn[1] = 1.0
        K.check(mh > 0 and 0 < eh < mh and eh == int(Mth.ench(MI, qh2, 0)) and abs(eh / float(mh) - 0.25) < 0.06,
                "X17 ... at 25 %%: %d of %d (seeded, the same again)" % (eh, mh))
        qs = Props(); Mth.starter(MI, qs, JLong(T0)); qs.setProperty("mining.i0.totems", "quarry_spirit:1,autosmelt_pole:1")
        K.check(bool(Tot.smelts(MI, qs, 0)) and not Tot.smelts(FO, qs, 0) and not Tot.smelts(FA, qs, 0), "X17 smelts(): an Auto-Smelt Pole on a Mining island")
        # conservation per kind (random sequences, boosters, compressors, bonus totems)
        rnd = random.Random(17)
        worst = 0
        workers = {MI: "quarry_spirit", FO: "lumber_spirit", RA: "harvest_spirit", OR: "harvest_spirit", CO: "soul_cage"}
        extras = {MI: ("geode_pole:2", "autosmelt_pole:1"), FO: ("sap_tap:1", "fertilizer:2"), RA: ("herd_pole:1", "scarecrow:3"),
                  OR: ("rain:1", "pollinator:2"), CO: ("lure_pole:2", "trophy_pole:1")}
        for case in range(500):
            k = rnd.choice((MI, FO, RA, OR, CO))
            kk = KN[k].lower()
            r_ = Props(); Mth.starter(k, r_, JLong(T0)); r_.setProperty(kk + ".storage", "5")
            r_.setProperty(kk + ".i0.size", str(rnd.choice((1, 2, 3))))
            r_.setProperty(kk + ".compressor", str(rnd.choice((0, 1, 2, 3))))
            ends = sorted(T0 + rnd.randint(1, 200) * 60000 + rnd.randint(0, 59999) for _ in range(rnd.randint(0, 3)))
            ents = ["%s:%d:%s::%d:x%d" % (workers[k], rnd.randint(1, 5), rnd.choice(("", "wider", "faster")), e_, i_) for i_, e_ in enumerate(ends)] or [workers[k] + ":1"]
            ents += [rnd.choice(extras[k])]
            r_.setProperty(kk + ".i0.totems", ",".join(ents))
            t = T0
            made = 0
            for step in range(rnd.randint(1, 25)):
                t += rnd.randint(0, 15 * 60000)
                made += int(Mth.settle(k, r_, 0, JLong(t)))
            integ = 0.0
            tt = T0
            for b_ in sorted(set([x for x in ends if T0 < x < t] + [t])):
                integ += (b_ - tt) * float(Mth.rate(k, r_, 0, JLong(tt))) / 60000.0
                tt = b_
            exp_ = min(int(Mth.capOf(k, r_, 0)), int(integ + 1e-9))
            worst = max(worst, abs(made - exp_))
            if int(Mth.stored(k, r_, 0)) != made:
                worst = 999
        K.check(worst <= 1, "X17 CONSERVATION: 500 random sequences over the five shards (boosters ending mid-way, Time Compressors, rare-find totems): items = floor(the integral) (off by %d at most; stored = made)" % worst)
        # ---- X17c layouts per kind + protection
        ids = list(Geo.IDS)
        allin, stand_ok, style_ok, regrow_ok, grow_ok, pad_ok = True, True, True, True, True, True
        why = []
        for k in range(6):
            kk = KN[k].lower()
            r_ = Props(); Mth.starter(k, r_, JLong(T0))
            for slot in range(6):
                r_.setProperty("%s.i%d.type" % (kk, slot), "x"); r_.setProperty("%s.i%d.size" % (kk, slot), "3")
                r_.setProperty("%s.i%d.totems" % (kk, slot), "%s:1,%s:1,%s:1,%s:1,%s:1" % ((workers.get(k, "harvest_spirit"),) * 5))
            reg = [tuple(int(v) for v in x) for x in Geo.region(r_, k)]
            ch = set((int(Geo.chunkX(k, i)), int(Geo.CZ[i])) for i in range(len(list(Geo.CX))))
            if not all(((x >> 5), (z >> 5)) in ch and 96 <= y <= 127 for (x, y, z, b) in reg):
                allin = False; why.append("chunks %s" % KN[k])
            if (1024 * k, Y + 1, -3, int(Geo.STANDS[k])) not in reg or str(ids[int(Geo.STANDS[k])]) != "Skyy_Shard_" + KN[k]:
                stand_ok = False; why.append("stand %s" % KN[k])
            kinds = set(b for (x, y, z, b) in reg)
            want = {MI: {int(Geo.ORE), int(Geo.STONE), int(Geo.COBBLE)}, FO: {int(Geo.OTRUNK), int(Geo.OLEAF)}, FA: {int(Geo.CROP), int(Geo.TILL)},
                    RA: {int(Geo.HAY)}, OR: {int(Geo.ATRUNK), int(Geo.ALEAF), int(Geo.APPLE)}, CO: {int(Geo.MOSSY)}}[k]
            forb = {int(Geo.CROP), int(Geo.ORE), int(Geo.OTRUNK), int(Geo.ATRUNK), int(Geo.HAY), int(Geo.MOSSY)} - want - ({int(Geo.TILL)} if k == FA else set())
            if not want <= kinds or (kinds & forb):
                style_ok = False; why.append("style %s %s" % (KN[k], sorted(kinds)))
            cl_ = Geo.crops(r_, k)
            cset = sorted(tuple(int(v) for v in cl_.get(i)) for i in range(cl_.size()))
            resl = sorted(b_ for b_ in reg if bool(Geo.res(b_[3])))
            if cset != resl or (not cset and k in (MI, FO, FA, OR)):
                regrow_ok = False; why.append("regrow %s" % KN[k])
            # every pad and the pillar stay free of trees / nodes / bales (the totems stand there)
            padpos = set()
            for slot in range(6):
                for pd in range(5):
                    padpos.add(tuple(int(v) for v in Geo.padPos(k, slot, pd)))
            occ = [b_ for b_ in reg if (b_[0], b_[1], b_[2]) in padpos and b_[3] < int(Geo.TOTEM)]
            if occ:
                pad_ok = False; why.append("pads %s %s" % (KN[k], occ[:2]))
            # Small in Medium in Large, per kind
            for slot in (0, 3):
                sets_ = []
                for size in (1, 2, 3):
                    L = JClass("java.util.ArrayList")(); Geo.island(L, k, slot, size)
                    sets_.append(set((int(L.get(i)[0]), int(L.get(i)[1]), int(L.get(i)[2])) for i in range(L.size())))
                if not (sets_[0] < sets_[1] < sets_[2]):
                    grow_ok = False; why.append("grow %s %d" % (KN[k], slot))
        K.check(allin and stand_ok and style_ok and regrow_ok and grow_ok and pad_ok,
                "X17 LAYOUT per shard (6 Large islands each): inside its own chunks (Farming's + 32 x (kind - 2)), its stand at (1024 x kind, -3), its style "
                "(ore nodes on stone, oak / apple trees with apples, hay, an arena), the regrow list = exactly its gatherables, pads + pillar free, "
                "Small in Medium in Large %s" % why[:4])
        rS = Props(); Mth.starter(MI, rS, JLong(T0))
        regS = [tuple(int(v) for v in x) for x in Geo.region(rS, MI)]
        floor_ = set((x, z) for (x, y, z, b) in regS if b == int(Geo.STONE) and y == Y)
        nodes = [(x, y, z) for (x, y, z, b) in regS if b == int(Geo.ORE)]
        K.check(nodes and all(y == Y + 1 and (x, z) in floor_ for (x, y, z) in nodes), "X17 every copper node sits on the stone floor (%d nodes on the Small island)" % len(nodes))
        rF = Props(); Mth.starter(FO, rF, JLong(T0))
        regF = [tuple(int(v) for v in x) for x in Geo.region(rF, FO)]
        trunks = set((x, z) for (x, y, z, b) in regF if b == int(Geo.OTRUNK))
        K.check(len(trunks) == 8 and all(sum(1 for (x2, y2, z2, b2) in regF if (x2, z2) == t_ and b2 == int(Geo.OTRUNK)) == 3 for t_ in trunks),
                "X17 the Small oak grove: 8 trees, 3 trunk blocks each")
        g17 = Gate()
        W17 = "skyy-shard-" + OWNER

        def allow(a_, b_):
            return bool(g17.apply(JArray(JObject)([JString(W17), JString(a_), JString(b_), ou])))
        prot = [allow("break", "Ore_Copper_Stone"), allow("damage", "Ore_Copper_Stone"), allow("break", "Wood_Oak_Trunk"), allow("break", "Wood_Apple_Trunk"),
                allow("break", "Plant_Crop_Apple_Block"), allow("use", "Plant_Crop_Apple_Block"), allow("break", "Plant_Leaves_Oak"), allow("break", "Plant_Hay_Bundle"),
                allow("break", "Rock_Stone"), allow("break", "Rock_Stone_Cobble"), allow("use", "Skyy_Shard_Mining"), allow("use", "Skyy_Shard_Combat"),
                allow("break", "Skyy_Shard_Mining"), allow("place", "Ore_Copper_Stone"), allow("use", "Ore_Copper_Stone")]
        K.eq(prot, [True, True, True, True, True, True, False, False, False, False, True, True, False, False, False],
             "X17 PROTECTION: ore nodes, trunks and apples may be gathered; leaves, hay, stone, cobble stay; every shard stand opens its menu; nothing is placed")
        # ---- X17d placement + pick up per kind (one portal per kind, independent of Farming's)
        Place.PENDING.clear()
        Role.OWNER_TEST = PyFn(lambda w: (str(w)[len("skyy-island-"):] if str(w).startswith("skyy-island-") else None))
        P3 = "0c1c2c3c-1111-2222-3333-000000000003"
        p3u = UUID.fromString(P3)
        Core.NOW_TEST = T0
        K.check(Place.decide(p3u, MI, "skyy-island-" + P3, 1, 129, 1, JLong(T0)) is None and Place.decide(p3u, FA, "skyy-island-" + P3, 3, 129, 3, JLong(T0)) is None,
                "X17 a Mining and a Farming Shard placed on the same island")
        f3 = St.readNow(P3)
        K.check(str(f3.getProperty("mining.placed")) == "skyy-island-%s|1|129|1" % P3 and str(f3.getProperty("mining.i0.type")) == "copper"
                and str(f3.getProperty("mining.i0.totems")) == "quarry_spirit:1" and str(f3.getProperty("farming.placed")).endswith("|3|129|3")
                and Place.PENDING.containsKey(P3 + "#0") and Place.PENDING.containsKey(P3), "X17 each kind its own record + starter island; pending checks per kind (owner#0 / owner)")
        K.check("Mining Shard is already placed" in str(Place.decide(p3u, MI, "skyy-island-" + P3, 5, 129, 5, JLong(T0))), "X17 a second Mining Shard: refused")
        Place.BLOCK_TEST = PyFn(lambda a: Bool.FALSE if int(a[7]) == 0 else Bool.TRUE)
        K.eq(int(Place.verify(JLong(T0 + 1500))), 1, "X17 the Mining block is not there: only the Mining record is undone")
        f3 = St.readNow(P3)
        K.check(f3.getProperty("mining.placed") is None and str(f3.getProperty("mining.paused")) == "1" and str(f3.getProperty("farming.placed")).endswith("|3|129|3")
                and f3.getProperty("farming.paused") is None, "X17 ... Farming's portal untouched (file)")
        Place.BLOCK_TEST = PyFn(lambda a: Bool.TRUE)
        K.check(Place.decide(p3u, MI, "skyy-island-" + P3, 1, 129, 1, JLong(T0 + 2000)) is None and int(Place.verify(JLong(T0 + 4000))) == 0
                and str(St.readNow(P3).getProperty("mining.placed")).endswith("|1|129|1"), "X17 placed again, the block is there: kept")
        Place.PENDING.clear()
        K.eq((str(Place.pendKey("o", 2)), str(Place.pendKey("o", 0)), str(Place.ownerOfKey("o#3")), str(Place.ownerOfKey("o")),
              int(Place.kindOf(JArray(JObject)([JString("w")]))), int(Place.kindOf(JArray(JObject)([JString("w")] * 7 + [JClass("java.lang.Integer")(4)])))),
             ("o", "o#0", "o", "o", 2, 4), "X17 pendKey / ownerOfKey / kindOf (an old 7-field entry = Farming)")
        TP3 = inv(2, 1, 1)
        rp_ = str(Core.pickup(p3u, P3, MI, None, TP3))
        K.check(rp_.startswith("-Stand by your shard portal"), "X17 pick up of the Mining portal away from it: refused")
        Role.WORLDKEY_TEST = PyFn(lambda k: JString("skyy-island-" + P3 + "-r2") if str(k) == P3 else None)
        rp_ = str(Core.pickup(p3u, P3, MI, None, TP3))
        f3 = St.readNow(P3)
        K.check(rp_.startswith("+Your island was reset - your Mining Shard") and int(Inv.count(TP3, "Skyy_Shard_Mining")) == 1 and int(Inv.count(TP3, "Skyy_Shard_Farming")) == 0
                and f3.getProperty("mining.placed") is None and str(f3.getProperty("mining.paused")) == "1" and f3.getProperty("farming.placed") is not None,
                "X17 a reset island: Pick up gives the MINING shard back (1 item), only its record cleared (file): %s" % rp_)
        e_ = str(W2.enter(None, None, p3u, P3, MI, None))
        K.check(e_.startswith("-No Mining Shard is placed"), "X17 Enter needs that shard placed: %s" % e_)
        Role.WORLDKEY_TEST = None
        K.check(Place.decide(p3u, MI, "skyy-island-" + P3, 2, 129, 2, JLong(T0 + 5000)) is None and St.readNow(P3).getProperty("mining.paused") is None, "X17 placed again: not paused")
        Place.PENDING.clear()
        _lv = str(W2.leave(None, None, p3u, P3, MI))
        K.check(_lv[:1] in "+-", "X17 leave(kind) runs (no Universe here): %s" % _lv)
        _a0 = W2.arrival(MI).getPosition(); _a5 = W2.arrival(CO).getPosition()
        K.check(abs(float(_a0.x()) - 0.5) < 1e-9 and abs(float(_a5.x()) - 5120.5) < 1e-9 and abs(float(_a5.z()) - 3.5) < 1e-9, "X17 each shard's arrival = its hub plaza (x 0.5 / 5120.5)")
        # ---- X17e COLLECT per kind (real containers): items, Auto-Smelt, the compactor, rare finds, XP per skill (Combat none), credits
        coins["bal"] = 10000000
        collect_ok[0] = True
        xp_ok[0] = True
        Core.NOW_TEST = T0 + 10000
        f3 = St.get(P3)
        for k in (FO, RA, OR, CO):
            Mth.starter(k, f3, JLong(T0 + 10000))
            f3.setProperty(KN[k].lower() + ".placed", "skyy-island-%s|%d|129|1" % (P3, 10 + k))
        St.save(P3, f3)

        def setst(k, stored, ench=0, ents=None):
            kk = KN[k].lower()
            f3.setProperty(kk + ".i0.stored", str(stored)); f3.setProperty(kk + ".i0.ench", str(ench)); f3.setProperty(kk + ".i0.last", str(T0 + 10000))
            if ents is not None:
                f3.setProperty(kk + ".i0.totems", ents)
            St.save(P3, f3)
        f3.setProperty("mining.storage", "5"); f3.setProperty("foraging.storage", "5")
        setst(MI, 250, 3)
        TC3 = inv(30, 9, 9)
        nx, nc = len(xp_calls), len(coll_calls)
        r_ = str(Core.collect(p3u, P3, MI, -1, TC3))
        K.check(r_.startswith("+Collected 250 Copper Ore + 3 Emerald (rare finds) +685 Mining XP") and int(Inv.count(TC3, "Ore_Copper")) == 250 and int(Inv.count(TC3, "Rock_Gem_Emerald")) == 3
                and xp_calls[nx:] == [(P3, "Mining", 685, "shard:mining", P3)] and [c[1:3] for c in coll_calls[nc:]] == [("Ore_Copper", 250), ("Rock_Gem_Emerald", 3)]
                and int(Mth.stored(MI, St.readNow(P3), 0)) == 0 and int(Mth.ench(MI, St.readNow(P3), 0)) == 0,
                "X17 Mining Collect: 250 ore + 3 Emeralds; Mining XP (250 x 5 + 3 x 40) x 50 %% = 685 (source shard:mining); credits Copper 250 + Emerald 3; file debited: %s" % r_)
        # Auto-Smelt + Auto-Compactor I: 2 Enchanted Copper Ingots + 50 ingots, credited as 250 ore
        f3.setProperty("mining.compactor", "1")
        setst(MI, 250, 0, "quarry_spirit:1,autosmelt_pole:1")
        nx, nc = len(xp_calls), len(coll_calls)
        r_ = str(Core.collect(p3u, P3, MI, -1, TC3))
        K.check(r_.startswith("+Collected 50 Copper Ingot + 2 Enchanted (compacted)") and int(Inv.count(TC3, "Ingredient_Bar_Copper")) == 50 and int(Inv.count(TC3, "Skyy_Ench_Copper")) == 2
                and xp_calls[nx][2] == 625 and [c[1:3] for c in coll_calls[nc:]] == [("Ore_Copper", 250)],
                "X17 Auto-Smelt + Auto-Compactor I: 250 ore -> 2 Enchanted Copper Ingots + 50 ingots; credited as 250 Copper ore, 625 XP: %s" % r_)
        # Foraging: compactor I on oak (no smelting) + Tree Sap rare finds
        f3.setProperty("foraging.compactor", "1")
        setst(FO, 230, 4)
        nx, nc = len(xp_calls), len(coll_calls)
        r_ = str(Core.collect(p3u, P3, FO, -1, TC3))
        K.check(r_.startswith("+Collected 30 Oak Log + 2 Enchanted (compacted) + 4 Tree Sap (rare finds)") and int(Inv.count(TC3, "Skyy_Ench_Oak")) == 2
                and int(Inv.count(TC3, "Wood_Oak_Trunk")) == 30 and int(Inv.count(TC3, "Ingredient_Tree_Sap")) == 4 and xp_calls[nx][1:3] == ("Foraging", 692)
                and [c[1:3] for c in coll_calls[nc:]] == [("Wood_Oak_Trunk", 230), ("Ingredient_Tree_Sap", 4)],
                "X17 Foraging: 230 logs -> 2 Enchanted Oak + 30 logs, 4 Tree Sap; Foraging XP (230 x 6 + 4) x 50 %% = 692; credits 230 + 4: %s" % r_)
        setst(RA, 40)
        nx = len(xp_calls)
        r_ = str(Core.collect(p3u, P3, RA, -1, TC3))
        K.check(r_.startswith("+Collected 40 Raw Chicken +40 Ranching XP") and xp_calls[nx][1:4] == ("Ranching", 40, "shard:ranching"), "X17 Ranching: 40 Raw Chicken, 40 Ranching XP: %s" % r_)
        setst(OR, 20)
        nx = len(xp_calls)
        r_ = str(Core.collect(p3u, P3, OR, -1, TC3))
        K.check(r_.startswith("+Collected 20 Apple +50 Orchard XP") and xp_calls[nx][1:4] == ("Orchard", 50, "shard:orchard"), "X17 Orchard: 20 apples, 50 Orchard XP: %s" % r_)
        setst(CO, 30, 2)
        nx, nc = len(xp_calls), len(coll_calls)
        r_ = str(Core.collect(p3u, P3, CO, -1, TC3))
        K.check(r_.startswith("+Collected 30 Bone Fragment + 2 Linen Scraps (rare finds)") and "XP" not in r_ and len(xp_calls) == nx
                and [c[1:3] for c in coll_calls[nc:]] == [("Ingredient_Bone_Fragment", 30), ("Ingredient_Fabric_Scrap_Linen", 2)] and int(Inv.count(TC3, "Ingredient_Bone_Fragment")) == 30,
                "X17 COMBAT = DROPS ONLY: 30 bones + 2 Linen, NO XP call at all, collections credited: %s" % r_)
        # a refused XP source waits per skill (owed.xp.Mining), Farming keeps owed.xp
        xp_ok[0] = False
        setst(MI, 10, 0, "quarry_spirit:1")
        r_ = str(Core.collect(p3u, P3, MI, -1, TC3))
        xp_ok[0] = True
        K.check("Mining XP waits" in r_ and int(St.lng(St.readNow(P3), "owed.xp.Mining", JLong(0))) == 25 and St.readNow(P3).getProperty("owed.xp") is None,
                "X17 unpaid Mining XP waits under owed.xp.Mining (25), not Farming's owed.xp: %s" % r_)
        setst(MI, 2)
        nx = len(xp_calls)
        Core.collect(p3u, P3, MI, -1, TC3)
        K.check(xp_calls[nx][1:3] == ("Mining", 30) and St.readNow(P3).getProperty("owed.xp.Mining") is None, "X17 ... paid with the next Mining Collect (5 + 25)")
        # what does not fit goes back to ITS island
        TF3 = inv(1)
        Inv.give(TF3, "Rock_Stone", JLong(50))
        setst(OR, 120)
        r_ = str(Core.collect(p3u, P3, OR, -1, TF3))
        K.check(int(Inv.count(TF3, "Plant_Fruit_Apple")) == 0 and r_.startswith("-Your inventory is full") and int(Mth.stored(OR, St.readNow(P3), 0)) == 120,
                "X17 nothing fits: the Orchard island keeps its 120 apples (file)")
        TF4 = inv(1, 1)
        Inv.give(TF4, "Rock_Stone", JLong(100))
        r_ = str(Core.collect(p3u, P3, OR, -1, TF4))
        K.check(int(Inv.count(TF4, "Plant_Fruit_Apple")) == 100 and int(Mth.stored(OR, St.readNow(P3), 0)) == 20 and "did not fit" in r_, "X17 100 fit, 20 back on the Orchard island: %s" % r_)
        K.check(str(Core.collect(p3u, P3 + "x", MI, -1, TC3)).startswith("-This shard's file") and str(Core.collect(ou, OWNER, MI, -1, TC3)).startswith("-No Mining Shard yet"),
                "X17 a profile without a Mining Shard cannot collect one")
        # ---- X17f Auto-Compactor + Time Compressor purchases (items first, coins after, refunds)
        TU = inv(6, 1, 1)
        r_ = str(Core.buyCompactor(p3u, P3, RA, TU))
        K.check(r_.startswith("-Nothing this shard makes has an Enchanted form"), "X17 Ranching has no Auto-Compactor: %s" % r_)
        f3.remove("foraging.compactor"); St.save(P3, f3)
        r_ = str(Core.buyCompactor(p3u, P3, FO, TU))
        K.check(r_.startswith("-You need 8 Enchanted Oak (you have 0)"), "X17 the compactor costs 8 Enchanted Oak: %s" % r_)
        Inv.give(TU, "Skyy_Ench_Oak", JLong(50))
        St.FAIL_TEST = True
        c0 = coins["bal"]
        r_ = str(Core.buyCompactor(p3u, P3, FO, TU))
        St.FAIL_TEST = False
        K.check(r_.startswith("-The upgrade could not be saved") and int(Inv.count(TU, "Skyy_Ench_Oak")) == 50 and coins["bal"] == c0 and St.get(P3).getProperty("foraging.compactor") is None,
                "X17 a refused save: compactor not bought, 50 / 50 Enchanted Oak, coins back: %s" % r_)
        r_ = str(Core.buyCompactor(p3u, P3, FO, TU))
        r2_ = str(Core.buyCompactor(p3u, P3, FO, TU))
        r3_ = str(Core.buyCompactor(p3u, P3, FO, TU))
        K.check(r_.startswith("+Auto-Compactor I") and r2_.startswith("+Auto-Compactor II") and r3_.startswith("=The Auto-Compactor is at its highest")
                and int(Inv.count(TU, "Skyy_Ench_Oak")) == 10 and coins["bal"] == c0 - 300000 and str(St.readNow(P3).getProperty("foraging.compactor")) == "2"
                and int(Mth.cap(FO, St.get(P3))) == 2 * 2400, "X17 compactor I (8 oak + 50,000) and II (32 + 250,000), II doubles storage (file 2)")
        r_ = str(Core.buyCompressor(p3u, P3, MI, TU))
        K.check(r_.startswith("-You need 8 Void Essence"), "X17 the Time Compressor costs Void Essence: %s" % r_)
        Inv.give(TU, "Ingredient_Void_Essence", JLong(168))
        f3 = St.get(P3)
        setst(MI, 0, 0, "quarry_spirit:1")
        Core.NOW_TEST = T0 + 10000 + 30 * 60000
        r_ = str(Core.buyCompressor(p3u, P3, MI, TU))
        st_ = int(Mth.stored(MI, St.readNow(P3), 0))
        Core.NOW_TEST = T0 + 10000 + 60 * 60000
        Mth.settle(MI, St.get(P3), 0, JLong(T0 + 10000 + 60 * 60000))
        st2_ = int(Mth.stored(MI, St.get(P3), 0))
        K.check(r_.startswith("+Time Compressor I") and st_ == 30 and st2_ == 30 + int(30 * 1.25) and str(St.readNow(P3).getProperty("mining.compressor")) == "1",
                "X17 Time Compressor I: the 30 minutes before were settled at x1 (30), the next 30 at x1.25 (+37) (file 1): %s" % r_)
        Core.buyCompressor(p3u, P3, MI, TU); Core.buyCompressor(p3u, P3, MI, TU)
        K.check(str(Core.buyCompressor(p3u, P3, MI, TU)).startswith("=The Time Compressor is at its highest") and int(Inv.count(TU, "Ingredient_Void_Essence")) == 0
                and int(Mth.compressor(MI, St.get(P3))) == 3, "X17 compressors II and III bought (8 + 32 + 128 Void Essence), then nothing left to buy")
        K.check(str(Core.buyCompressor(mu, P3, MI, TU)).startswith("-Only the island owner and co-op") or str(Core.buyCompressor(mu, P3, MI, TU)).startswith("-Only the island owner"),
                "X17 not the owner: refused")
        # ---- X17g GROW per kind
        TG = inv(6, 1, 1)
        tiers["t"] = 2
        r_ = str(Core.grow(p3u, P3, OR, 0, TG))
        K.check(r_.startswith("-Needs Apple collection 4 (you: 2)"), "X17 Orchard Grow checks the Apple collection: %s" % r_)
        tiers["t"] = 9
        r_ = str(Core.grow(p3u, P3, OR, 0, TG))
        K.check(r_.startswith("-You need 8 Apple Sapling"), "X17 Orchard Grow costs 8 Apple Saplings: %s" % r_)
        Inv.give(TG, "Plant_Sapling_Apple", JLong(40)); Inv.give(TG, "Skyy_Ench_Cobblestone", JLong(7))
        r_ = str(Core.grow(p3u, P3, OR, 0, TG))
        r2_ = str(Core.grow(p3u, P3, MI, 0, TG))
        r3_ = str(Core.grow(p3u, P3, MI, 0, TG))
        K.check(r_.startswith("+The Apple island grew to Medium") and int(Inv.count(TG, "Plant_Sapling_Apple")) == 32 and r2_.startswith("+The Copper island grew to Medium")
                and r3_.startswith("+The Copper island grew to Large") and int(Inv.count(TG, "Skyy_Ench_Cobblestone")) == 0
                and int(Mth.size(MI, St.readNow(P3), 0)) == 3 and int(Mth.size(OR, St.readNow(P3), 0)) == 2,
                "X17 Grow per shard: Apple 8 saplings; Copper 2 then 5 Enchanted Cobblestone (file sizes 3 / 2)")
        # ---- X17h totems across shards: placement rules, uid unique over every shard, pick up / modifiers on a Mining island
        TT3 = inv(4, 1, 1)
        Inv.giveStack(TT3, Tot.stack(JArray(JString)(["harvest_spirit", "1", "", "", "0", "hs3"]), JLong(T0)))
        Inv.giveStack(TT3, Tot.stack(JArray(JString)(["geode_pole", "2", "", "", "0", "ge3"]), JLong(T0)))
        lt_ = Inv.totems(TT3)
        hs_ = [x for x in lt_ if str(x[2]) == "Skyy_Totem_HarvestSpirit"][0]
        r_ = str(Core.placeTotem(p3u, P3, MI, 0, int(hs_[0]), int(hs_[1]), TT3))
        K.check(r_.startswith("-The Harvest Spirit works in the Farming, Ranching, Orchard Shard - not in this one") and int(Inv.count(TT3, "Skyy_Totem_HarvestSpirit")) == 1,
                "X17 a Harvest Spirit on a Mining island: refused, kept: %s" % r_)
        r_ = str(Core.placeTotem(p3u, P3, RA, 0, int(hs_[0]), int(hs_[1]), TT3))
        K.check(r_.startswith("+Placed Harvest Spirit I on island 1") and "harvest_spirit:1:::0:hs3" in str(St.readNow(P3).getProperty("ranching.i0.totems")),
                "X17 ... on the Ranching island: placed (file): %s" % r_)
        ge_ = [x for x in Inv.totems(TT3) if str(x[2]) == "Skyy_Totem_GeodePole"][0]
        r_ = str(Core.placeTotem(p3u, P3, MI, 0, int(ge_[0]), int(ge_[1]), TT3))
        K.check(r_.startswith("+Placed Geode Pole II") and float(Tot.enchChance(MI, St.get(P3), 0)) == 0.01, "X17 a Geode Pole II on the Mining island: 1 %% rare finds: %s" % r_)
        # a crash copy of the Ranching Harvest Spirit (same uid) offered to Farming: refused + removed (uid unique over every shard)
        Mth.starter(FA, St.get(P3), JLong(T0))
        TD3 = inv(2, 1, 1)
        Inv.giveStack(TD3, Tot.stack(JArray(JString)(["harvest_spirit", "1", "", "", "0", "hs3"]), JLong(T0)))
        ld3 = Inv.totems(TD3)
        St.get(P3).setProperty("farming.i0.totems", "")
        r_ = str(Core.placeTotem(p3u, P3, FA, 0, int(ld3.get(0)[0]), int(ld3.get(0)[1]), TD3))
        K.check(r_.startswith("-This totem is already placed on island 1") and Inv.totems(TD3).size() == 0 and list(Core.uidAt(St.get(P3), "hs3")) == [0, 1, RA],
                "X17 uid unique over every shard: the copy is refused + removed; uidAt says Ranching island 1 pad 2: %s" % r_)
        # pick up from the Mining island returns the exact document; modifiers + booster work there
        Inv.give(TT3, "Skyy_TotemMod_RareFinder", JLong(1)); Inv.give(TT3, "Ingredient_Life_Essence", JLong(1))
        ra_ = str(Core.addMod(p3u, P3, MI, 0, 1, 5, TT3))
        rb_ = str(Core.addBooster(p3u, P3, MI, 0, 1, TT3))
        K.check(ra_.startswith("+Rare Finder added to Geode Pole II") and rb_.startswith("+Booster burning") and abs(float(Tot.enchChance(MI, St.get(P3), 0)) - 0.02) < 1e-12,
                "X17 a Rare Finder doubles the Geode chance (2 %%), a booster burns on the Mining island")
        rp_ = str(Core.pickTotem(p3u, P3, MI, 0, 1, TT3))
        gd_ = [x for x in Inv.totems(TT3) if str(x[2]) == "Skyy_Totem_GeodePole"]
        K.check(rp_.startswith("+Geode Pole II is in your inventory") and len(gd_) == 1 and str(Tot.dstr(gd_[0][3], "uid")) == "ge3" and str(Tot.dstr(gd_[0][3], "m1")) == "rare"
                and int(Tot.dlong(gd_[0][3], "bst")) > 0 and len(list(Tot.entries(MI, St.readNow(P3), 0))) == 1,
                "X17 pick up from the Mining island: the exact document (uid ge3, Rare Finder, booster time)")
        K.check(str(Core.showRange(P3, MI, 0, 0)).startswith("=Range 3") and abs(Core.RANGE.get("skyy-shard-" + P3)[0] - (0 + int(Geo.SX[0]) + 0.5)) < 1e-9,
                "X17 Show range on the Mining island draws at its own region")
        _nr = Core.nearest(St.get(P3), MI, float(Geo.padPos(MI, 0, 0)[0]) + 0.3, float(Geo.padPos(MI, 0, 0)[2]) + 0.3)
        K.check(_nr is not None and list(_nr) == [0, 0] and Core.nearest(St.get(P3), FA, float(Geo.padPos(MI, 0, 0)[0]), 0.0) is None,
                "X17 nearest(kind): the Mining region's totem, none of another region")
        # ---- X17i crafting: the other totems, the Soul Cage gate, a shard per kind
        TK3 = inv(6, 1, 1)
        CID = list(Cfg.CRAFT_ID)
        ri_q, ri_sc, ri_ms = CID.index("Skyy_Totem_QuarrySpirit"), CID.index("Skyy_Totem_SoulCage"), CID.index("Skyy_Shard_Mining")
        Inv.give(TK3, "Ore_Copper", JLong(200)); Inv.give(TK3, "Ingredient_Life_Essence", JLong(80))
        r_ = str(Core.craft(p3u, ri_q, TK3))
        K.check(r_.startswith("+Crafted Quarry Spirit I") and int(Inv.count(TK3, "Ore_Copper")) == 72, "X17 craft a Quarry Spirit (128 Copper Ore + 8 Life Essence + 500): %s" % r_)
        g_ = str(Core.craftGate(p3u, ri_sc))
        Inv.give(TK3, "Ingredient_Bone_Fragment", JLong(200)); Inv.give(TK3, "Ingredient_Void_Essence", JLong(20)); Inv.give(TK3, "Weapon_Wand_SoulOrb", JLong(1))
        Tot.SOUL_TEST = soul_fn("Ingredient_Fire_Essence")
        g2_ = Core.craftGate(p3u, ri_sc)
        _cr = Cfg.CRAFT
        _sv = str(_cr[ri_sc])
        _cr[ri_sc] = "Ingredient_Bone_Fragment:1;0"
        g3_ = str(Core.craftGate(p3u, ri_sc))
        _cr[ri_sc] = _sv
        r_ = str(Core.craft(p3u, ri_sc, TK3))
        K.check(g_.startswith("The Soul Cage needs SkyyArmory 0.1.25") and g2_ is None and g3_.startswith("The Soul Cage recipe must name a Soul Orb")
                and r_.startswith("+Crafted Soul Cage Totem I") and int(Inv.count(TK3, "Weapon_Wand_SoulOrb")) == 0,
                "X17 SOUL CAGE: no armory:fn:soulcage = refused; a recipe without a Soul Orb / Cage = refused; with the ladder it crafts and takes the Soul Orb: %s / %s" % (g3_, r_))
        # shard:fn:totem prices per shard (Combat: the Soul Orb ladder's essence; the same id adds up)
        tf = P("ShTotemFn")()
        A_ = lambda *a: JArray(JObject)([JString(x) if isinstance(x, str) else x for x in a])
        c1_ = str(tf.apply(A_("cost", "Skyy_Totem_SoulCage", "")))
        Tot.SOUL_TEST = soul_fn("Ingredient_Void_Essence")
        c2_ = str(tf.apply(A_("cost", "Skyy_Totem_LurePole", "")))
        Tot.SOUL_TEST = None
        c3_ = str(tf.apply(A_("cost", "Skyy_Totem_SoulCage", "")))
        K.eq([c1_, c2_, c3_, str(tf.apply(A_("cost", "Skyy_Totem_LumberSpirit", ""))), str(tf.apply(A_("cost", "Skyy_Totem_HerdPole", "")))],
             ["Ingredient_Void_Essence:1,Ingredient_Fire_Essence:10", "Ingredient_Void_Essence:11", "Ingredient_Void_Essence:1,Ingredient_Life_Essence:10",
              "Skyy_Ench_Oak:1,Ingredient_Life_Essence:10", "Skyy_Ench_Wheat:1,Ingredient_Life_Essence:10"],
             "X17 shard:fn:totem cost per shard (Combat: Void + the Soul Orb ladder essence; the same id adds up; no SkyyArmory = Life Essence)")
        # a shard per kind: rebirth 2, one of each per profile (Farming had = still free to craft Mining)
        fns.put("rebirth:fn:count", PyFn(lambda k: JInt(2)))
        Inv.give(TK3, "Skyy_Ench_Cobblestone", JLong(32)); Inv.give(TK3, "Ingredient_Life_Essence", JLong(64))
        coins["bal"] = 1000000
        g_o = Core.craftGate(ou, ri_ms)
        r_ = str(Core.craft(ou, ri_ms, TK3))
        g_o2 = str(Core.craftGate(ou, ri_ms))
        g_p3 = str(Core.craftGate(p3u, ri_ms))
        K.check(g_o is None and r_.startswith("+Crafted Mining Shard") and int(Inv.count(TK3, "Skyy_Shard_Mining")) == 1 and str(St.readNow(OWNER).getProperty("mining.crafted")) == "1"
                and g_o2.startswith("You already have your Mining Shard") and g_p3.startswith("You already have your Mining Shard")
                and St.readNow(OWNER).getProperty("farming.crafted") is None,
                "X17 shard crafting per kind: the owner (who has a Farming Shard) crafts a Mining Shard once (mining.crafted); P3 (placed one) refused: %s" % r_)
        # ---- shards03fix (critic 1): a Soul Orb WITH data (SkyyGear's GearData stamp) is never taken while a plain one exists; with data
        # only, the hotbar (the weapon in hand) goes last; a refused craft gives the EXACT stack back (document intact)
        BDc = JClass("org.bson.BsonDocument")
        Tot.SOUL_TEST = soul_fn("Ingredient_Fire_Essence")

        def orb(lv):
            return IS("Weapon_Wand_SoulOrb", 1).withMetadata("SkyyGear", BDc.parse('{"lvl": %d}' % lv))

        def ojs(lv):
            return str(BDc.parse('{"SkyyGear": {"lvl": %d}}' % lv).toJson())

        def orbs(c_):
            out_ = []
            for ci_ in range(len(c_)):
                for sl_ in range(int(c_[ci_].getCapacity())):
                    it_ = c_[ci_].getItemStack(JClass("java.lang.Short")(sl_).shortValue())
                    if it_ is not None and not it_.isEmpty() and str(it_.getItemId()) == "Weapon_Wand_SoulOrb":
                        md_ = it_.getMetadata()
                        out_.append((ci_, None if md_ is None or md_.isEmpty() else str(md_.toJson())))
            return out_

        def mats(c_):
            Inv.give(c_, "Ingredient_Bone_Fragment", JLong(300)); Inv.give(c_, "Ingredient_Void_Essence", JLong(30))
        coins["bal"] = 1000000
        TK4 = inv(8, 2, 2)
        TK4[1].addItemStack(orb(9))
        Inv.give(TK4, "Weapon_Wand_SoulOrb", JLong(1))
        mats(TK4)
        o0 = orbs(TK4)
        ra_ = str(Core.craft(p3u, ri_sc, TK4))
        o1 = orbs(TK4)
        K.check(o0 == [(0, None), (1, ojs(9))] and ra_.startswith("+Crafted Soul Cage Totem I") and o1 == [(1, ojs(9))],
                "X17 fix (critic 1): the PLAIN Soul Orb is taken, the stamped one in the hotbar is untouched: %s -> %s / %s" % (o0, o1, ra_))
        TK5 = inv(8, 2, 2)
        TK5[1].addItemStack(orb(7))
        TK5[2].addItemStack(orb(3))
        mats(TK5)
        _b5, _c5 = int(Inv.count(TK5, "Ingredient_Bone_Fragment")), coins["bal"]
        coins_fail[0] = True
        rf_ = str(Core.craft(p3u, ri_sc, TK5))
        coins_fail[0] = False
        o2 = sorted((str(x[1]) for x in orbs(TK5)))
        K.check(rf_.startswith("-The items or coins could not be taken") and o2 == sorted([ojs(7), ojs(3)]) and int(Inv.count(TK5, "Ingredient_Bone_Fragment")) == _b5
                and coins["bal"] == _c5,
                "X17 fix (critic 1): a refused craft gives the taken Soul Orb back WITH its document (no plain copy): %s / %s" % (rf_, o2))
        rs_ = str(Core.craft(p3u, ri_sc, TK5))
        o3 = orbs(TK5)
        K.check(rs_.startswith("+Crafted Soul Cage Totem I") and [x[1] for x in o3] == [ojs(7)] and o3[0][0] == 1,
                "X17 fix (critic 1): only stamped Soul Orbs = one from storage / backpack first, the hotbar's (in hand) last: %s / %s" % (rs_, o3))
        Tot.SOUL_TEST = None
        # a purchase refunds the exact stacks too (take2 + giveBack on an upgrade item that carries data)
        TK7 = inv(4)
        TK7[0].addItemStack(IS("Ingredient_Void_Essence", 3).withMetadata("Tag", BDc.parse('{"a": 1}')))
        Inv.give(TK7, "Ingredient_Void_Essence", JLong(5))
        kept_ = JClass("java.util.ArrayList")()
        tk_ = int(Inv.take2(TK7, "Ingredient_Void_Essence", JLong(7), kept_))
        kp_ = [(str(x.getItemId()), int(x.getQuantity())) for x in kept_]
        bk_ = int(Inv.giveBack(TK7, "Ingredient_Void_Essence", JLong(tk_), kept_))
        tagged_ = sum(int(TK7[0].getItemStack(JClass("java.lang.Short")(i).shortValue()).getQuantity()) for i in range(4)
                      if TK7[0].getItemStack(JClass("java.lang.Short")(i).shortValue()) is not None and not TK7[0].getItemStack(JClass("java.lang.Short")(i).shortValue()).isEmpty()
                      and TK7[0].getItemStack(JClass("java.lang.Short")(i).shortValue()).getMetadata() is not None)
        K.check(tk_ == 7 and kp_ == [("Ingredient_Void_Essence", 2)] and bk_ == 7 and int(Inv.count(TK7, "Ingredient_Void_Essence")) == 8 and tagged_ >= 3
                and int(Inv.take(TK7, "Ingredient_Void_Essence", JLong(8))) == 5,
                "X17 fix (critic 1): take2 = plain first (5) then 2 with data (kept), giveBack restores them with data; take() never touches data stacks: %s / %s" % (kp_, tagged_))
        # ---- shards03fix (critic 2): /shardadmin give marks <kind>.crafted BEFORE the shard exists (a stashed given shard = had)
        gk = "0e0e0e0e-9999-2222-3333-00000000000a"
        TG = inv(2)
        rg_ = Adm.giveShard(gk, MI, TG)
        mk1 = St.readNow(gk).getProperty("mining.crafted")
        Inv.take(TG, "Skyy_Shard_Mining", JLong(1))   # stashed in a chest, never placed
        gg_ = str(Core.craftGate(UUID.fromString(gk), ri_ms))
        K.check(rg_ is None and str(mk1) == "1" and gg_.startswith("You already have your Mining Shard"),
                "X17 fix (critic 2): /shardadmin give = mining.crafted 1 on disk; the stashed shard blocks a second craft at rebirth 2: %s" % gg_)
        gk2 = "0e0e0e0e-9999-2222-3333-00000000000b"
        TF = inv(1)
        Inv.give(TF, "Rock_Stone", JLong(100))
        rf2 = str(Adm.giveShard(gk2, FO, TF))
        St.get(gk2).setProperty("ranching.crafted", "1"); St.save(gk2, St.get(gk2))
        rf3 = str(Adm.giveShard(gk2, RA, TF))
        St.FAIL_TEST = True
        rf4 = str(Adm.giveShard(gk2, OR, inv(2)))
        St.FAIL_TEST = False
        d2 = St.readNow(gk2)
        K.check(rf2 == "-Their inventory is full." and d2.getProperty("foraging.crafted") is None and str(d2.getProperty("ranching.crafted")) == "1"
                and rf3 == "-Their inventory is full." and rf4.startswith("-Their shard file could not be saved") and d2.getProperty("orchard.crafted") is None,
                "X17 fix (critic 2): inventory full = the mark this call set is taken back (an older mark stays); a refused save = nothing given: %s / %s / %s" % (rf2, rf3, rf4))
        # ---- shards03fix2 (2nd critic round #1): a recipe naming one id twice = ONE row; giveBack hands each kept stack back once, at most n
        OID = "Weapon_Wand_SoulOrb"
        rcm = Core.recipe(OID + ":2,Ingredient_Void_Essence:3, " + OID + ":2;100")
        K.check(rcm is not None and [str(x) for x in rcm[0]] == [OID, "Ingredient_Void_Essence"] and [int(x) for x in rcm[1]] == [4, 3] and int(rcm[2]) == 100
                and Core.recipe("Rock_Stone:60000,Rock_Stone:60000") is None and Core.recipe("Rock_Stone:1,Rock_Stone:1") is not None,
                "X17 fix2: recipe() merges a repeated id into one row (2 + 2 = 4, first place kept); the merged row keeps the 100,000 cap")
        TB = inv(6, 2, 2)
        for lv_ in (1, 2, 3):
            TB[0].addItemStack(orb(lv_))
        kb_ = JClass("java.util.ArrayList")()
        tb_ = int(Inv.take2(TB, OID, JLong(3), kb_))
        b1_ = int(Inv.giveBack(TB, OID, JLong(2), kb_))
        kt1_ = str(Inv.keptText(kb_))
        b2_ = int(Inv.giveBack(TB, OID, JLong(1), kb_))
        b3_ = int(Inv.giveBack(TB, OID, JLong(1), kb_))   # nothing kept left = a plain one (the caller's own count is the limit)
        ob_ = orbs(TB)
        K.check(tb_ == 3 and b1_ == 2 and b2_ == 1 and b3_ == 1 and len(ob_) == 4 and sorted(str(x[1]) for x in ob_ if x[1] is not None) == sorted([ojs(1), ojs(2), ojs(3)])
                and kt1_.count(";") == 1 and str(Inv.keptText(kb_)) == "",
                "X17 fix2: giveBack(2) then giveBack(1) = the 3 stamped orbs back ONCE each (a third call = plain only); keptText skips returned stacks: %s / %s" % (ob_, kt1_))
        Tot.SOUL_TEST = soul_fn("Ingredient_Fire_Essence")
        _sv2 = str(_cr[ri_sc])
        _cr[ri_sc] = OID + ":2," + OID + ":2,Ingredient_Bone_Fragment:1;10"
        TD = inv(8, 2, 2)
        for lv_ in (4, 5, 6):
            TD[0].addItemStack(orb(lv_))
        mats(TD)
        rd1_ = str(Core.craft(p3u, ri_sc, TD))
        od1_ = sorted(str(x[1]) for x in orbs(TD))
        TD[2].addItemStack(orb(8))
        coins_fail[0] = True
        rd2_ = str(Core.craft(p3u, ri_sc, TD))
        coins_fail[0] = False
        od2_ = sorted(str(x[1]) for x in orbs(TD))
        _cr[ri_sc] = _sv2
        Tot.SOUL_TEST = None
        K.check(rd1_.startswith("-You need 4 ") and od1_ == sorted([ojs(4), ojs(5), ojs(6)])
                and rd2_.startswith("-The items or coins could not be taken") and od2_ == sorted([ojs(4), ojs(5), ojs(6), ojs(8)]),
                "X17 fix2 (the critic's dupe): 'orb:2,orb:2' with 3 stamped orbs = refused (needs 4), nothing taken; with 4 and the coins failing = the SAME 4 back, no copy: %s / %s / %s" % (rd1_, rd2_, od2_))
        # ---- shards03fix2 (2nd critic round #2): VOID RESCUE - below y 80 a member goes to the hub of a placed + owned shard (painted first)
        Sw = P("ShSweep")
        rk1 = "0e0e0e0e-9999-2222-3333-00000000000c"
        q1_ = St.get(rk1); Mth.starter(MI, q1_, JLong(T0)); q1_.setProperty("mining.placed", "w|1|2|3")
        ru1 = UUID.fromString(rk1)
        Sw.RESCUED.clear()
        v1 = int(Sw.rescueKind(rk1, 2048.5, 50.0, ru1, JLong(10000)))       # respawned at the (unpainted) Farming hub, fell
        v2 = int(Sw.rescueKind(rk1, 2048.5, 40.0, ru1, JLong(12000)))       # 2 s later: still on its way
        v3 = int(Sw.rescueKind(rk1, 2048.5, 40.0, ru1, JLong(14500)))       # 4.5 s later: again
        v4 = int(Sw.rescueKind(rk1, 0.5, 101.0, None, JLong(0)))            # standing on the Mining hub
        v5 = int(Sw.rescueKind(rk1, 0.5, 79.9, None, JLong(0)))             # fell off a Mining island
        Mth.starter(OR, q1_, JLong(T0)); q1_.setProperty("orchard.placed", "w|1|2|4")
        v6 = int(Sw.rescueKind(rk1, 4096.5, 10.0, None, JLong(0)))          # fell off the Orchard
        v7 = int(Sw.rescueKind(rk1, 5120.5, 10.0, None, JLong(0)))          # over Combat (not owned) = the first placed (Mining)
        q1_.remove("orchard.placed")
        v8 = int(Sw.rescueKind(rk1, 4096.5, 10.0, None, JLong(0)))          # Orchard owned but not placed = Mining
        Mth.starter(FA, q1_, JLong(T0)); q1_.setProperty("farming.placed", "w|1|2|5")
        v9 = int(Sw.rescueKind(rk1, 5120.5, 10.0, None, JLong(0)))          # Farming placed = Farming first
        v10 = int(Sw.rescueKind("0e0e0e0e-9999-2222-3333-00000000000d", 2048.5, 10.0, None, JLong(0)))   # nothing placed = the island hub
        v11 = int(Sw.rescueKind(None, 2048.5, 10.0, None, JLong(0)))
        K.eq([float(Sw.RESCUE_Y), v1, v2, v3, v4, v5, v6, v7, v8, v9, v10, v11], [80.0, MI, -1, MI, -1, MI, OR, MI, MI, FA, -2, -1],
             "X17 fix2 VOID RESCUE: below y 80 -> the region's hub if placed + owned, else Farming, else the first placed; nothing placed = the island hub; once per 4 s")
        a_m = P("ShWorld2").arrival(MI).getPosition()
        K.check(abs(float(a_m.x()) - 0.5) < 1e-9 and float(a_m.y()) > float(Sw.RESCUE_Y), "X17 fix2: the rescue target (Mining arrival x 0.5) is above the rescue line")
        # ---- shards03fix2 (2nd critic round, critic 3 #1): shard:fn:give, the quest bridge - never a second shard of a kind
        Gf = P("ShGiveFn")
        gfo = Gf()
        Gf.PLAYER_TEST = PyFn(lambda u: None)
        fu = "0e0e0e0e-9999-2222-3333-00000000000e"
        OA = lambda *a: JArray(JObject)(list(a))
        z1 = str(gfo.apply(JString("x")))
        z2 = str(gfo.apply(OA(UUID.fromString(fu), JString("nope"))))
        z3 = str(gfo.apply(OA(UUID.fromString(gk), JString("Mining"))))    # given by /shardadmin give above = had
        z4 = str(gfo.apply(OA(UUID.fromString(fu), JString("combat"))))
        br.put("profile:busy:" + fu, Bool.TRUE)
        z5 = str(gfo.apply(OA(UUID.fromString(fu), JString("combat"))))
        br.remove("profile:busy:" + fu)
        z6 = str(gfo.apply(OA(UUID.fromString(rk1), JString("orchard"))))   # an Orchard island exists (owned) = had
        Gf.PLAYER_TEST = None
        K.check(z1.startswith("-Bad call") and z2.startswith("-Unknown shard nope") and z3.startswith("=You already have your Mining Shard")
                and z4 == "-That player is not online." and z5.startswith("-The profile is switching") and z6.startswith("=You already have your Orchard Shard")
                and St.get(fu).getProperty("combat.crafted") is None,
                "X17 fix2 shard:fn:give: bad call / unknown shard / already had (given or owned) = '=' and nothing given / offline / profile busy: %s | %s | %s | %s | %s" % (z2, z3, z4, z5, z6))
        fns.remove("rebirth:fn:count")
        # ---- X17j the page per shard: title / icons / every tab one packet, the Shards tab + switching, Upgrades buttons
        Page.TEST_INV = TU
        Role.OWNER_TEST = PyFn(lambda w: (str(w)[len("skyy-island-"):] if str(w).startswith("skyy-island-") else None))
        Role.ROLE_TEST = PyFn(lambda a: "owner" if str(a[1]) == "skyy-island-" + P3 and str(a[0]) == P3 else None)
        Role.ROLEKEY_TEST = PyFn(lambda a: "owner" if str(a[1]) == P3 and str(a[0]) == P3 else None)
        sizes17, miss = [], []
        for k in range(6):
            for tab in range(6):
                pg = Page(p3u, "default")
                pg.kind = k
                pg.tab = tab
                b, ev = UCB(), UEB()
                pg.build(None, b, ev, None)
                sizes17.append(int(CP("SkyySh", True, True, LIFE.CanDismiss, b.getCommands(), ev.getEvents()).computeSize()))
                txt = "\n".join(str(c.text) for c in b.getCommands() if c.text is not None)
                if str(pg.title) != KN[k] + " Shard" or ('ItemId: "Skyy_Shard_%s"' % KN[k]) not in txt:
                    miss.append((k, tab, str(pg.title)))
                if tab == 0 and int(pg.cN) > 0 and ('ItemId: "%s"' % str(Kd.PROD[k])) not in txt:
                    miss.append((k, "prod icon"))
                bnd = [str(e.selector) for e in ev.getEvents()]
                if tab == 1 and (("#SkyyShUCBuy" in bnd) != (k in (MI, FO, FA) and int(Mth.compactor(k, St.get(P3))) < 2) or ("#SkyyShUTBuy" in bnd) != (int(Mth.compressor(k, St.get(P3))) < 3)):
                    miss.append((k, "upgrade buttons", [x for x in bnd if "UCBuy" in x or "UTBuy" in x]))
                if tab == 5 and not all(("#SkyyShORow%dBtn" % i) in bnd for i in range(6)):
                    miss.append((k, "shards tab"))
        K.check(not miss and max(sizes17) < int(CP.MAX_SIZE), "X17 THE PAGE per shard: 6 shards x 6 tabs, the shard's title + portal icon + item icon, Upgrades buy buttons only "
                "where something is left to buy (no compactor in Ranching / Orchard / Combat), the Shards tab rows; one packet each (max %d bytes) %s" % (max(sizes17), miss[:3]))
        pg = Page(p3u, "default")
        pg.kind = MI
        pg.tab = 5
        b, ev = UCB(), UEB(); pg.build(None, b, ev, None)
        K.check(str(pg.oSt[MI]) == "Open now" and str(pg.oSub[MI]).startswith("Placed - 1 island") and "Not yours yet" not in str(pg.oSub[CO])
                and str(pg.oSub[FA]).startswith("Placed") and int(pg.oN) == 6, "X17 the Shards tab: the open shard marked, each with placed / islands / per hour: %s" % list(pg.oSub)[:2])
        seq = [str(pg.act(a_, None, None)) for a_ in ("kind3", "kind9", "kindx")]
        K.check(int(pg.kind) == RA and int(pg.tab) == 0 and seq == ["", "", ""], "X17 Open (kind3) switches the page to the Ranching Shard (Collect tab); bad ones ignored")
        b, ev = UCB(), UEB(); pg.build(None, b, ev, None)
        K.check(str(pg.title) == "Ranching Shard" and str(pg.cName[0]).startswith("Chicken Island 1") and "Ranching XP" in str(pg.cAll[1]), "X17 ... its texts: %s / %s" % (pg.cName[0], pg.cAll[1]))
        pg.kind = CO
        b, ev = UCB(), UEB(); pg.build(None, b, ev, None)
        K.check("No XP" in str(pg.cAll[1]) and str(pg.cAll[2]).startswith("Bone Fragments collection"), "X17 the Combat Collect tab says drops only: %s" % pg.cAll[1])
        pg.kind = FO
        pg.tab = 1
        b, ev = UCB(), UEB(); pg.build(None, b, ev, None)
        K.check(str(pg.cmTx[0]) == "Tier 2 of 2" and "Fully upgraded" in str(pg.cmTx[2]) and str(pg.uTx[6]).find("Enchanted Oak") >= 0 or str(pg.uTx[2]) == "Fully upgraded",
                "X17 Foraging Upgrades: compactor II shown fully upgraded, storage priced in Enchanted Oak: %s / %s" % (pg.cmTx[2], pg.uTx[6]))
        pg.kind = CO
        b, ev = UCB(), UEB(); pg.build(None, b, ev, None)
        K.check("Enchanted form" in str(pg.cmTx[1]) and not bool(pg.cmCan) and bool(pg.tcCan) and "Void Essence" in str(pg.tcTx[5]), "X17 Combat Upgrades: no compactor, a compressor for Void Essence")
        # shards03fix2 (critic 3 #4): Mining's Compactor I says it needs an Auto-Smelt Pole; Foraging's does not
        _pm = St.get(P3); _cmo = _pm.getProperty("mining.compactor"); _cfo = _pm.getProperty("foraging.compactor")
        _pm.remove("mining.compactor"); _pm.remove("foraging.compactor")
        pg.kind = MI
        b, ev = UCB(), UEB(); pg.build(None, b, ev, None)
        _mtx = str(pg.cmTx[2])
        pg.kind = FO
        b, ev = UCB(), UEB(); pg.build(None, b, ev, None)
        _ftx = str(pg.cmTx[2])
        if _cmo is not None: _pm.setProperty("mining.compactor", _cmo)
        if _cfo is not None: _pm.setProperty("foraging.compactor", _cfo)
        K.check(_mtx == "Next: Compactor I - needs an Auto-Smelt Pole" and _ftx == "Next: Auto-Compactor I",
                "X17 fix2: Mining's Compactor I warns it needs an Auto-Smelt Pole (Foraging's does not): %s / %s" % (_mtx, _ftx))
        # shards03fix2 (critic 3 #3): the Craft tab says which Soul Orb a recipe takes (a weapon); a recipe without a weapon says nothing
        pg.kind = CO
        pg.kSel = CID.index("Skyy_Totem_SoulCage")
        pg.fillCraft(TU)
        _ksc = [str(x) for x in pg.kTx]
        pg.kSel = CID.index("Skyy_Totem_QuarrySpirit")
        pg.fillCraft(TU)
        _kqs = [str(x) for x in pg.kTx]
        K.check(any(x.startswith("Takes a plain ") and x.endswith("first, the one in your hotbar last.") for x in _ksc) and not any("hotbar" in x for x in _kqs),
                "X17 fix2: the Soul Cage's Craft panel warns which Soul Orb is taken: %s" % [x for x in _ksc if "hotbar" in x])
        r1_ = str(pg.act("tcbuy", None, None))
        r2_ = str(pg.act("cmpbuy", None, None))
        K.check(r1_[0] in "+-=" and r2_.startswith("-Nothing this shard makes"), "X17 the Upgrades buy clicks (compressor / compactor): %s / %s" % (r1_, r2_))
        # the portal view of a non-Farming shard: P3's Mining portal on P3's island
        pgv = Page(p3u, "skyy-island-" + P3)
        pgv.kind = MI
        b, ev = UCB(), UEB(); pgv.build(None, b, ev, None)
        K.check(int(pgv.view) == 0 and "#SkyyShPick" in [str(e.selector) for e in ev.getEvents()], "X17 the Mining portal on its island = the portal view (Pick up)")
        _opl = str(St.get(P3).getProperty("orchard.placed"))
        St.get(P3).setProperty("orchard.placed", "skyy-island-elsewhere|1|1|1")
        pgv.kind = OR
        b, ev = UCB(), UEB(); pgv.build(None, b, ev, None)
        St.get(P3).setProperty("orchard.placed", _opl)
        K.check(int(pgv.view) == 2, "X17 a shard whose portal is not on this island, opened from here = the menu view")
        K.check(int(P("ShPageFn")(JInt(3)).apply(None).kind) == 3 and int(P("ShPageFn")().apply(None).kind) == 2 and int(P("ShPageFn")(True).apply(None).kind) == 2,
                "X17 each portal page id opens its own shard (ShPageFn(kind)); 0.2's = Farming")
        K.eq([int(Fn.firstKind(P3)), int(Fn.firstKind("0e0e0e0e-9999-2222-3333-000000000001"))], [2, 2], "X17 the SkyWynn Menu tile: Farming when placed / nothing owned")
        f9 = "0e0e0e0e-9999-2222-3333-000000000009"
        q9 = St.get(f9); Mth.starter(OR, q9, JLong(T0)); q9.setProperty("orchard.placed", "w|1|2|3")
        K.eq(int(Fn.firstKind(f9)), OR, "X17 ... else the first placed shard (Orchard)")
        # the tick: the regions players stand in (unknown = every owned shard)
        Tk = P("ShTick")
        Tk.PRESENT.clear()
        K.eq(int(Tk.mask("skyy-shard-" + P3, St.get(P3))), (1 << MI) | (1 << FO) | (1 << FA) | (1 << RA) | (1 << OR) | (1 << CO), "X17 tick mask: nobody seen yet = every owned shard")
        Tk.PRESENT.put("skyy-shard-" + P3, JClass("java.lang.Integer")(1 << OR))
        K.eq(int(Tk.mask("skyy-shard-" + P3, St.get(P3))), 1 << OR, "X17 tick mask: the regions the sweep saw players in")
        Tk.PRESENT.clear()
        # /shardadmin text paths without a player (the parser phase N checks the sub-commands themselves)
        Adm.PLAYER_TEST = PyFn(lambda n: None)
        K.check(str(Adm.run("").get(0)).startswith("-Usage: /shardadmin give <player> [shard]") and str(Adm.run("bogus Tester").get(0)).startswith("-Unknown: bogus")
                and str(Adm.run("give Tester mining").get(0)) == "-That player is not online." and str(Adm.run("info Nobody").get(0)) == "-That player is not online.",
                "X17 /shardadmin run: usage, unknown sub-command, an offline player")
        Adm.PLAYER_TEST = None
        K.eq([int(Adm.kindArg(JArray(JString)(["give", "x"]), 2)), int(Adm.kindArg(JArray(JString)(["give", "x", "Combat"]), 2)),
              int(Adm.kindArg(JArray(JString)(["give", "x", "nope"]), 2))], [2, 5, -1], "X17 the shard word (none = Farming)")
        Role.ROLE_TEST = PyFn(lambda a: None)
        Page.TEST_INV = TI
        Core.NOW_TEST = 0

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


# ====================================================================================================== N: the /shardadmin parser (0.3 fix)
def run_parse(out, jar, scratch, _home):
    """the game's own command parser on the real command objects (the SkyyRebirth 0.3.1 harness pattern): every 0.3 line parses and reaches
    the player command (a console sender gets playerOrArg = past the parser); 0.2's greedy variant refuses the same lines (the CONTROL)"""
    from jpype import JClass, JArray, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST], verify=True)
    URL, File = JClass("java.net.URL"), JClass("java.io.File")

    def loader(jars):
        return JClass("java.net.URLClassLoader")(JArray(URL)([File(j).toURI().toURL() for j in jars]),
                                                 JClass("java.lang.ClassLoader").getSystemClassLoader())
    PM = JClass("com.hypixel.hytale.server.core.permissions.PermissionsModule")
    HS = JClass("java.util.HashSet")
    Tok = JClass("com.hypixel.hytale.server.core.command.system.Tokenizer")
    PCx = JClass("com.hypixel.hytale.server.core.command.system.ParserContext")
    PRs = JClass("com.hypixel.hytale.server.core.command.system.ParseResult")
    MSGS = []

    def sender(nodes):
        ns = HS()
        for n_ in nodes:
            ns.add(n_)

        @JImplements("com.hypixel.hytale.server.core.command.system.CommandSender")
        class Snd(object):
            @JOverride
            def getUsername(self):
                return "Tester"

            @JOverride
            def getUuid(self):
                return JClass("java.util.UUID")(1, 2)

            @JOverride
            def sendMessage(self, m):
                MSGS.append(str(m.getMessageId() or m.getRawText()))

            @JOverride
            def hasPermission(self, q, *rest):
                if isinstance(q, str) or str(q.getClass().getName()) == "java.lang.String":
                    r = PM.hasPermission(ns, str(q))
                else:
                    r = PM.hasPermission(ns, q)
                return bool(r) if r is not None else False
        return Snd()

    @JImplements("com.hypixel.hytale.server.core.command.system.CommandOwner")
    class Owner(object):
        @JOverride
        def getName(self):
            return "SkyyHarness"
    owner = Owner()

    def root_of(j):
        L = loader([j])
        c = JClass(PKG + "ShAdminCmd", loader=L)()
        c.setOwner(owner)
        try:
            c.completeRegistration()
        except Exception as e:
            K.notes.append("completeRegistration: %s" % str(e)[:100])
        return c, L

    def parse(root, line, snd):
        del MSGS[:]
        res = PRs()
        toks = Tok.parseArguments(line, res)
        if res.failed():
            return False, ["tokenizer"]
        ctx = PCx.of(toks, line, res)
        try:
            root.acceptCall(snd, ctx, res)
        except Exception as e:
            MSGS.append("EXC " + str(e)[:300])
        if res.failed():
            res.sendMessages(snd)
            return False, list(MSGS)
        return True, list(MSGS)
    admin, nobody = sender(["skyyshards.admin"]), sender([])
    new_root, _Ln = root_of(jar)
    old_root, _Lo = root_of(OLD02)
    subs = sorted(str(x) for x in new_root.getSubCommands().keySet())
    K.eq(subs, ["give", "info", "totem", "unload", "unplace"], "N parser: /shardadmin has the sub-commands give / info / totem / unload / unplace")
    good = ("shardadmin give Tester", "shardadmin give Tester mining", "shardadmin give Tester combat", "shardadmin info Tester", "shardadmin unplace Tester",
            "shardadmin unplace Tester orchard", "shardadmin unload Tester", "shardadmin totem Tester rain", "shardadmin totem Tester soul_cage 3", "shardadmin")
    for line in good:
        ok, msgs = parse(new_root, line, admin)
        K.check(ok and "server.commands.errors.playerOrArg" in msgs, "N parser: /%s parses and reaches the player command (%s)" % (line, msgs[:2]))
    for line in ("shardadmin give", "shardadmin give a b c", "shardadmin totem Tester", "shardadmin info a b", "shardadmin totem a b 3 4"):
        ok, msgs = parse(new_root, line, admin)
        K.check(not ok, "N parser: /%s is refused by the engine (%s)" % (line, msgs[:1]))
    for line in ("shardadmin give Tester", "shardadmin totem Tester rain 3", "shardadmin info Tester"):
        ok, msgs = parse(old_root, line, admin)
        K.check(not ok, "N parser CONTROL: 0.2 refuses /%s (the bug): %s" % (line, msgs[:1]))
    for line in ("shardadmin give Tester", "shardadmin info Tester", "shardadmin unload Tester"):
        ok, msgs = parse(new_root, line, nobody)
        K.check(not ok or "server.commands.errors.playerOrArg" not in msgs, "N parser: /%s without skyyshards.admin is refused (%s)" % (line, msgs[:1]))
    gen = open(os.path.join(HERE, "build_skyyshards_%s.py" % VERSION), encoding="utf8").read()
    K.check(gen.count('requirePermission("skyyshards.admin");') >= 9 and '@PKG@.ShAdmin.exec(pr, "give " + a1 + " " + a2);' in gen
            and '@PKG@.ShAdmin.exec(pr, "totem " + a1 + " " + a2 + " " + a3);' in gen and '@PKG@.ShAdmin.exec(pr, "unplace " + a1);' in gen
            and "addUsageVariant(new @PKG@.ShAdmGiveKindCmd());" in gen and 'mk("ShAdminArgsCmd"' not in gen,
            "N static: each sub-command needs skyyshards.admin and hands ShAdmin.run the same text line")
    K.save()


# ====================================================================================================== C02: class compare 0.2 -> 0.3
OLD02 = os.path.join(HERE, "SkyyShards-0.2.jar")
GONE02 = {"ShAdminArgsCmd"}            # 0.2's greedy usage variant (the parser bug) - replaced by the sub-commands
NEW03 = {"ShKind", "ShGiveFn", "ShAdmGiveCmd", "ShAdmGiveKindCmd", "ShAdmInfoCmd", "ShAdmUnplaceCmd", "ShAdmUnplaceKindCmd", "ShAdmUnloadCmd", "ShAdmTotemCmd",
         "ShAdmTotemTierCmd"}
# members 0.3 replaces on purpose: two INTERNAL helpers that now take the kind (only ShCore / ShGeo call them; no bridge, no other mod).
# Every other 0.2 signature stays - the kind-aware methods are overloads beside them (0.2's signatures = Farming)
GONE02_MEMBERS = {"ShCore": {"m start(Ljava/util/UUID;Ljava/lang/String;[Lcom/hypixel/hytale/server/core/inventory/container/ItemContainer;[Ljava/lang/Object;)Ljava/lang/String;"},
                  "ShGeo": {"m pads(Ljava/util/ArrayList;Ljava/util/Properties;I)V"}}


def run_cmp02(out, jar, scratch, _home):
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
    a, b = classes(OLD02), classes(jar)
    pa, pb = pool_of(OLD02), pool_of(jar)
    K.eq(sorted(x[len(PKG):] for x in a if x not in b), sorted(GONE02), "C02: the only 0.2 class gone = ShAdminArgsCmd (the greedy /shardadmin variant)")
    K.eq(sorted(x[len(PKG):] for x in b if x not in a), sorted(NEW03), "C02: the new classes = ShKind + the 8 /shardadmin sub-command classes + ShGiveFn (shard:fn:give, fix2)")

    def sigs(p_, cn):
        c_ = p_.get(cn)
        out_ = set()
        for f_ in c_.getDeclaredFields():
            out_.add("f " + str(f_.getName()) + " " + str(f_.getSignature()))
        for m_ in c_.getDeclaredMethods():
            out_.add("m " + str(m_.getName()) + str(m_.getSignature()))
        for m_ in c_.getDeclaredConstructors():
            out_.add("c " + str(m_.getSignature()))
        return out_
    lost, changed, added = {}, [], 0
    for cn in a:
        if cn not in b:
            continue
        sa, sb = sigs(pa, cn), sigs(pb, cn)
        short = cn[len(PKG):]
        gone = sorted(x for x in sa - sb if x not in GONE02_MEMBERS.get(short, set()))
        if gone:
            lost[short] = gone
        if sa != sb:
            changed.append(short)
            added += len(sb - sa)
    K.check(not lost, "C02: every 0.2 field / method / constructor signature is still there but the two internal helpers ShCore.start / ShGeo.pads (now with the kind); the kind-aware code adds overloads: %s" % lost)
    K.notes.append("C02: %d of %d 0.2 classes gained members (%d new members): %s" % (len(changed), len(a), added, ", ".join(changed)))
    print("C02. class compare SkyyShards-0.2.jar -> 0.3: %d classes, %d gained members, new %s, gone %s" % (len(a), len(changed), sorted(NEW03), sorted(GONE02)))
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
           phases=[("exec", run_exec), ("parse", run_parse), ("cmp02", run_cmp02), ("live", run_live)], script=__file__,
           live=(os.path.join(LIVE_DIR, "Skyy_SkyyIslands"), "mods/Skyy_SkyyIslands"))
