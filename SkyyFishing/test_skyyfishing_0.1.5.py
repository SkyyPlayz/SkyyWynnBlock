"""Harness for SkyyFishing 0.1.5 (THE LIFELONG FISHING POLE: Marlow's pole asks SkyyGear's gear:fn:pole, the bench upgrade keeps the SkyyGear
document, the lifelong tooltip line; tools/fishing_0_1_5_patch.py) = the 0.1.4 harness (every check kept) + phase P.
Build first: python tools/fishing_0_1_5_patch.py && python SkyyFishing/build_skyyfishing_0.1.5.py

    python SkyyFishing/test_skyyfishing_0.1.5.py [--keep]

0.1.5 NEW: C compares 0.1.4 -> 0.1.5; fix round 2: P8 = FishRig.llWhy + FishCore.cast refusing another profile's / a retired lifelong pole; P = every new code path: llPole (a SkyyGear ll document only), carryGear (only the SkyyGear key, never
from a plain rod), withRigG's lifelong line, FishQuestFn.starterG with a gear:fn:pole stand-in (stamped -> the lifelong + gift lines, the grant
kept; absent / throws / returns the same stack / another item / an unstamped rod / a stack of 2 -> the 0.1.4 rod exactly), FishBench.craft
calls carryGear before withRigG (static call order). The end-to-end run with the REAL SkyyGear 0.3.5 is in SkyyGear/test_skyygear_0.3.5.py (G35 P8).

--- the 0.1.4 harness header ---

Phases (each a fresh child JVM, the game's JRE, TEMP / TMP in scratch; tools/harness_kit.py + tools/perfworld_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.3 -> 0.1.4: exactly the planned members differ (+ FishQuestFn); every non-class entry identical but manifest.json
  X  exec     the 0.1.3 tick checks on this jar (no behaviour change there)
  Q  quest    EVERY NEW CODE PATH: FishBridge.questInit publishes fishing:fn:starter / fishing:fn:grantOf / quest:caller:fishing; the starter
              pole (a real ItemStack on a stand-in Item store): SkyyFishing_Rod_Bamboo x1, the bench's fresh rig (Wooden Reel), the grant in
              OUR rod document, the tooltip; grantOf reads it back (not a rod / no grant / a bench re-rig = null); bad arguments = null;
              questCatch sends {uuid, "fishing:catch", item, Long n} to quest:fn:event and is a single map read without SkyyQuests; static:
              FishCore.land calls questCatch ONLY in the fish branch, after the XP offer; the plugin's setup calls questInit
  ST live     start twice (FishCfg.load + FishStore.start + questInit) on a scratch COPY of the live Skyy_SkyyFishing: nothing written,
              every live profile reads back
  AA engine-access audit
Behaviour regression (the 0.1.2 engine child, a real catch through land(), on this jar):
  python SkyyFishing/test_skyyfishing_0.1.2.py --mkfake <scratch>/fake --dir <scratch> --jar SkyyFishing/SkyyFishing-0.1.4.jar
  python SkyyFishing/test_skyyfishing_0.1.2.py --engine --out <scratch>/engine.json --dir <scratch> --jar SkyyFishing/SkyyFishing-0.1.4.jar
(never run that harness without --dir: its default scratch is another round's folder and it deletes it first).
Scratch: tools/dev/scratch/quests3/fishing (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW

VERSION = "0.1.5"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyFishing-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyFishing-0.1.4.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "gear5", "fishing")))
PKG = "com.skyy.fishing."

EXPECT = {     # 0.1.5 (tools/fishing_0_1_5_patch.py): the lifelong pole members + the version text the kit / admin line carries
    "FishRig": ["+f GEAR_KEY", "+f LL_LINE", "+m llPole", "+m carryGear", "~m withRigG",     # C: the lifelong line; B: the bench carry
                "+m restampOne", "~m stale",      # D (fix round): the redraw after SkyyGear's rebirth reset
                "+m llWhy"],                      # E (fix round 2): a lifelong pole casts only for its owner
    "FishCore": ["~<clinit>", "+f LLNO", "~m cast"],     # E (fix round 2): cast asks llWhy first
    "FishBridge": ["~m questInit"],             # D (fix round): + fishing:fn:restamp
    "FishBench": ["~m craft"],                 # B: the upgraded rod takes the old rod's SkyyGear document
    "FishQuestFn": ["~<clinit>", "+f STAMPED", "+m starterG", "~m apply"],     # A: Marlow's pole asks gear:fn:pole
    "CfgRows": ["~<clinit>", "~m header"],      # the config kit re-emitted: version / export header text
    "CfgFn": ["~m opExport"],
    "FishCfg": ["~m applyAll", "~m seed"],      # the kit's default config text (a constant naming the version)
    "FishCmds": ["~m admin"],                   # the /fishadmin stats line names the version
    "SkyyFishingPlugin": ["~m setup"],          # the ready line names the version (no code change)
}
ADDED = []


def make_api(st):
    from jpype import JImplements, JOverride

    @JImplements(PKG + "FishApi")
    class Api(object):
        def _n(self, k):
            st["calls"][k] = st["calls"].get(k, 0) + 1
        @JOverride
        def eye(self, c): self._n("eye"); return None
        @JOverride
        def feet(self, c): self._n("feet"); return None
        @JOverride
        def heldSlot(self, c): self._n("heldSlot"); return st["slot"]
        @JOverride
        def held(self, c): self._n("held"); return st["held"]
        @JOverride
        def clicked(self, c): self._n("clicked"); return False
        @JOverride
        def block(self, c, x, y, z): self._n("block"); return -1
        @JOverride
        def getReel(self, c): self._n("getReel"); return st["reel"]
        @JOverride
        def setReel(self, c, v): self._n("setReel"); st["reel"] = int(v)
        @JOverride
        def spawnBobber(self, c, s): self._n("spawnBobber")
        @JOverride
        def moveBobber(self, c, s, x, y, z): self._n("moveBobber")
        @JOverride
        def tagBobber(self, c, s, t): self._n("tagBobber")
        @JOverride
        def removeBobber(self, s): self._n("removeBobber")
        @JOverride
        def particle(self, c, i, x, y, z): self._n("particle")
        @JOverride
        def drawLine(self, c, pts, n, secs): self._n("drawLine")
        @JOverride
        def sound(self, c, i, x, y, z): self._n("sound")
        @JOverride
        def hudState(self, c, s, state, txt): self._n("hudState")
        @JOverride
        def hudSet(self, c, s, bar, t, cps): self._n("hudSet")
        @JOverride
        def hudHide(self, c, s): self._n("hudHide")
        @JOverride
        def tell(self, c, text, col): self._n("tell")
        @JOverride
        def inv(self, c): self._n("inv"); return None
        @JOverride
        def later(self, c, r): self._n("later")
        @JOverride
        def fresh(self, c): self._n("fresh"); return None
        @JOverride
        def now(self): self._n("now"); st["t"] += 50; return st["t"]
    return Api()


# ====================================================================================================== X: every new code path
def run_exec(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    Brg, Core, Eng, Defs, Ctx, Store, FIO, State = P("FishBridge"), P("FishCore"), P("FishEng"), P("FishDefs"), P("FishCtx"), P("FishStore"), P("FishIO"), P("FishState")
    Sys, UUID, IS = JClass("java.lang.System"), JClass("java.util.UUID"), JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    # ---- A: bridge
    K.check(Brg.BRIDGE is None, "X bridge: BRIDGE empty before the first call")
    m1 = Brg.bridge()
    K.check(Sys.identityHashCode(Sys.getProperties().get("skyy.bridge")) == Sys.identityHashCode(m1) and Sys.identityHashCode(Brg.BRIDGE) == Sys.identityHashCode(m1)
            and Sys.identityHashCode(Brg.bridge()) == Sys.identityHashCode(m1) and Sys.identityHashCode(Brg.bridge0()) == Sys.identityHashCode(m1),
            "X bridge: created once, cached in BRIDGE, the same map")
    PW.bridge_static(K, jar)
    g = PW.calls(jar)
    K.check(PKG + "FishCtx.<init>" not in g["FishTick.tick"] and PKG + "FishCore.ctxOf" in g["FishTick.tick"], "X static: FishTick.tick makes no FishCtx (ctxOf)")
    K.check(PKG + "FishCtx.<init>" in g["FishCore.kick"], "X static: kick hands FishGiveTask a copy of the context")
    t = FIO().newThread(None)
    K.check(str(t.getName()) == "SkyyFishing-IO" and t.isDaemon(), "X FishIO.newThread: SkyyFishing-IO, daemon")
    # ---- ctxOf
    u = UUID.fromString("00000000-0000-4000-8000-000000000007")
    c1 = Core.ctxOf(u, "Tester", None, None, None, None, None)
    c2 = Core.ctxOf(u, "Tester2", None, None, None, None, None)
    K.check(Sys.identityHashCode(c1) == Sys.identityHashCode(c2) and str(c2.name) == "Tester2", "X ctxOf: the player's ONE context, refilled")
    # ---- the tick through the seam
    st = {"calls": {}, "held": None, "slot": 0, "reel": 3, "t": 1000000}
    Eng.API = make_api(st)
    idle0 = Core.IDLE
    for i in range(200):
        Core.tickPlayer(c1)
    cl = st["calls"]
    K.check(cl.get("held") == 200 and cl.get("clicked", 0) == 0 and cl.get("heldSlot", 0) == 0 and cl.get("getReel") == 1 and cl.get("setReel") == 1
            and st["reel"] == 0 and cl.get("later", 0) == 0 and Core.IDLE == idle0 + 200,
            "X IDLE (no rod, no line) x200: 200 held() reads, no click / slot read, the reel read ONCE and reset to 0, no later() hop: %s" % cl)
    seen = Core.SEEN.get(u)
    K.check(seen is not None and seen.ticks == 199 and seen.reel == 0, "X FishSeen: the tick counter as an int (199), reel known 0")
    # epoch watch while idle
    br = Brg.bridge()
    br.put("profile:epoch:" + str(u), JClass("java.lang.Long")(5))
    for i in range(10):
        Core.tickPlayer(c1)
    br.put("profile:epoch:" + str(u), JClass("java.lang.Long")(6))
    for i in range(10):
        Core.tickPlayer(c1)
    K.check(Core.EPOCH_AT.get(u) is not None and int(Core.EPOCHS.get(u)) == 6, "X idle: the profile-epoch watch still runs (a switch is recorded)")
    # rod in hand: real ItemStack objects, allocated without the Item asset store (a bare JVM has none) - item id + quantity set
    Uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    Uf.setAccessible(True)
    U = Uf.get(None)
    Mod = JClass("java.lang.reflect.Modifier")

    def mkstack(id_):
        o = U.allocateInstance(IS.class_)
        for fl in IS.class_.getDeclaredFields():
            if Mod.isStatic(fl.getModifiers()):
                continue
            n = str(fl.getName()).lower()
            fl.setAccessible(True)
            if str(fl.getType().getName()) == "java.lang.String" and "id" in n:
                fl.set(o, id_)
            elif str(fl.getType().getName()) == "int" and "quant" in n:
                fl.setInt(o, 1)
        return o
    rods = list(Defs.RODS)
    rod = mkstack(str(rods[0]))
    K.check(str(rod.getItemId()) == str(rods[0]) and not rod.isEmpty(), "X the stand-in rod stack reads as %s" % rods[0])
    st["held"], st["calls"], st["slot"] = rod, {}, 2
    rigs0 = Core.RIGS
    for i in range(200):
        Core.tickPlayer(c1)
    cl = st["calls"]
    want = int(Core.SEEN.get(u).rigReel)
    K.check(Core.RIGS == rigs0 + 1 and cl.get("clicked") == 200 and cl.get("heldSlot") == 200 and st["reel"] == want
            and 9 <= cl.get("getReel", 0) <= 12 and cl.get("setReel", 0) == (1 if want != 0 else 0),
            "X ROD x200: the rig parsed ONCE, the reel set once (%d) and checked every 20 ticks: %s" % (want, cl))
    st["held"] = mkstack(str(rods[0]))
    Core.tickPlayer(c1)
    K.check(Core.RIGS == rigs0 + 2, "X a new stack object (a rig change) is parsed again")
    st["slot"] = 3
    Core.tickPlayer(c1)
    K.check(Core.RIGS == rigs0 + 3, "X another slot is parsed again")
    st["reel"] = 5
    st["held"], st["calls"] = None, {}
    Core.tickPlayer(c1)
    Core.SEEN.get(u).reel = 5
    Core.tickPlayer(c1)
    K.check(st["reel"] == 0 and st["calls"].get("setReel") == 1, "X rod put away: the reel look reset to 0: %s" % st["calls"])
    # a line out = the full path (clicked() every tick) even with no rod in hand -> the line is cancelled like 0.1.2
    s = State(u)
    s.phase = 5
    s.hudUntil = 0
    Core.STATES.put(u, s)
    st["calls"] = {}
    Core.tickPlayer(c1)
    K.check(st["calls"].get("clicked") == 1 and Core.STATES.get(u) is None, "X a result card (phase 5) takes the full path (and ends as 0.1.2)")
    # the save thread
    Store.IOX = JClass("java.util.concurrent.Executors").newSingleThreadScheduledExecutor(FIO())
    Store.stopIO()
    K.check(Store.IOX is None, "X FishStore.stopIO stops the writer")
    K.save()


# ====================================================================================================== Q: the quest hooks (0.1.4)
def item_store(ids):
    """a bare JVM has no Item asset store: an empty one holding these ids (the SkyyQuests / SkyyHud harness pattern) - new ItemStack works"""
    from jpype import JClass
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyF4TestStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fake.addConstructor(JClass("javassist.CtNewConstructor").make("public SkyyF4TestStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
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
    for i in ids:
        it_ = U.allocateInstance(ItemC.class_)
        k = ItemC.class_
        f = k.getDeclaredField("maxStack")
        f.setAccessible(True)
        f.setInt(it_, 1 if "Rod" in i else 64)
        mf.get(amap).put(i, it_)


def run_quest(out, jar, scratch, _home):
    from jpype import JClass, JArray, JObject, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    Brg, Rig, QFn, Defs = P("FishBridge"), P("FishRig"), P("FishQuestFn"), P("FishDefs")
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    UUID = JClass("java.util.UUID")
    u = UUID.fromString("00000000-0000-4000-8000-000000000044")
    # Q1 questCatch without SkyyQuests: one map read, false
    K.check(not bool(Brg.questCatch(u, "SkyyFishing_Fish_Bluegill", 1)), "Q1 questCatch without SkyyQuests = false (nothing else)")
    got = []

    @JImplements("java.util.function.Function")
    class Ev(object):
        @JOverride
        def apply(self, a):
            got.append((str(a[0]), str(a[1]), str(a[2]), int(a[3]), str(a[3].getClass().getName())))
            return JClass("java.lang.Boolean").TRUE
    br.put("quest:fn:event", Ev())
    K.check(bool(Brg.questCatch(u, "SkyyFishing_Fish_Bluegill", 2)) and got == [(str(u), "fishing:catch", "SkyyFishing_Fish_Bluegill", 2, "java.lang.Long")],
            "Q1 questCatch = quest:fn:event {uuid, fishing:catch, the fish item, Long n}: %s" % got)
    K.check(not bool(Brg.questCatch(u, "x", 0)) and not bool(Brg.questCatch(None, "x", 1)) and len(got) == 1, "Q1 n 0 / no player = no call")
    # Q2 questInit
    Brg.questInit()
    K.check(br.get("fishing:fn:starter") is not None and br.get("fishing:fn:grantOf") is not None and bool(br.get("quest:caller:fishing"))
            and br.get("fishing:fn:restamp") is not None,
            "Q2 questInit publishes fishing:fn:starter, fishing:fn:grantOf, quest:caller:fishing (+ fix round: fishing:fn:restamp)")
    # Q3 the starter pole (a real ItemStack on a stand-in Item store)
    rods = [str(x) for x in Defs.RODS]
    item_store(rods + ["Rock_Stone"])
    st = br.get("fishing:fn:starter").apply(JArray(JObject)([u, "pk1:fishing_intro.take_pole:1"]))
    K.check(st is not None and str(st.getItemId()) == "SkyyFishing_Rod_Bamboo" and int(st.getQuantity()) == 1, "Q3 the starter pole = the Wooden Fishing Rod x1")
    rig = [str(x) for x in Rig.rigOf(st)]
    K.eq(rig, [str(x) for x in Rig.freshRig("SkyyFishing_Rod_Bamboo")], "Q3 ... with the bench's fresh rig for that rod (the Wooden Reel, no parts)")
    K.eq(rig[0], "1", "Q3 ... the reel is the Wooden Reel (1)")
    K.eq(str(br.get("fishing:fn:grantOf").apply(st)), "pk1:fishing_intro.take_pole:1", "Q3 the claim's grant id rides in OUR rod document")
    js = str(st.getMetadata().toJson())
    K.check("A gift from Marlow" in js and "Wooden" in js, "Q3 the tooltip names the rod and the gift")
    K.eq(int(QFn.MADE), 1, "Q3 one pole made")
    # Q4 grantOf / starter refusals
    K.check(br.get("fishing:fn:grantOf").apply(JClass("com.hypixel.hytale.server.core.inventory.ItemStack")("Rock_Stone", 1)) is None, "Q4 grantOf: not a rod = null")
    plain = Rig.withRig(JClass("com.hypixel.hytale.server.core.inventory.ItemStack")("SkyyFishing_Rod_Bamboo", 1), Rig.freshRig("SkyyFishing_Rod_Bamboo"))
    K.check(br.get("fishing:fn:grantOf").apply(plain) is None, "Q4 grantOf: a rod rigged at the bench (no grant field) = null")
    K.check(br.get("fishing:fn:grantOf").apply(None) is None and br.get("fishing:fn:grantOf").apply("x") is None, "Q4 grantOf: bad arguments = null")
    sf = br.get("fishing:fn:starter")
    K.check(sf.apply(JArray(JObject)([u, ""])) is None and sf.apply(JArray(JObject)(["not a uuid", "g"])) is None and sf.apply("x") is None
            and sf.apply(JArray(JObject)([u])) is None and int(QFn.MADE) == 1, "Q4 starter: no grant / no player / bad arguments = null, nothing made")
    # FIX-A3 (critic): SkyyQuests retries a pole claim while the bags are full - each retry builds a stack, the log line comes once per grant
    sink = JClass("java.util.ArrayList")()
    P("FishLog").SINK = sink
    sf.apply(JArray(JObject)([u, "pk1:fishing_intro.take_pole:1"]))
    sf.apply(JArray(JObject)([u, "pk1:fishing_intro.take_pole:1"]))
    made = [str(x) for x in sink if "starter pole made" in str(x)]
    K.check(int(QFn.MADE) == 3 and made == [], "FIX-A3 two retries of the same grant: stacks built (MADE 3), no new 'starter pole made' line: %s" % made)
    sf.apply(JArray(JObject)([u, "pk2:fishing_intro.take_pole:7"]))
    made = [str(x) for x in sink if "starter pole made" in str(x)]
    K.check(len(made) == 1 and "pk2:fishing_intro.take_pole:7" in made[0] and str(QFn.LOGGED) == "pk2:fishing_intro.take_pole:7",
            "FIX-A3 a new grant logs once: %s" % made)
    P("FishLog").SINK = None
    # FIX2 (critic): the grant stamp survives a re-rig / re-stamp at the bench and a craft upgrade (the dupe guard still sees the pole)
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    g0 = "pk1:fishing_intro.take_pole:1"
    rr = Rig.withRig(st, Rig.rigOf(st))
    K.eq(str(br.get("fishing:fn:grantOf").apply(rr)), g0, "FIX2 a re-stamp of Marlow's pole (withRig with its own rig) keeps the grant")
    rr2 = Rig.withRig(st, JArray(JClass("java.lang.String"))(["0", "", "", ""]))
    K.check(str(br.get("fishing:fn:grantOf").apply(rr2)) == g0 and [str(x) for x in Rig.rigOf(rr2)] == ["0", "", "", ""],
            "FIX2 a re-rig at the bench (the reel taken off) keeps the grant and takes the new rig")
    up = Rig.withRigG(IS("SkyyFishing_Rod_Copper", 1), Rig.rigOf(st), Rig.str(Rig.doc(st), "grant"))
    K.check(str(br.get("fishing:fn:grantOf").apply(up)) == g0 and str(up.getItemId()) == "SkyyFishing_Rod_Copper",
            "FIX2 the upgrade path (craft: withRigG(new rod, old rig, old grant)) carries the grant to the Copper rod")
    K.check(br.get("fishing:fn:grantOf").apply(Rig.withRigG(IS("SkyyFishing_Rod_Copper", 1), Rig.rigOf(st), "")) is None
            and br.get("fishing:fn:grantOf").apply(Rig.withRig(plain, Rig.rigOf(plain))) is None, "FIX2 no grant in = no grant out (a plain rod stays plain)")
    K.check("A gift from Marlow" not in str(rr.getMetadata().toJson()), "FIX2 only the stamp moves (the gift tooltip line is the starter's own)")
    # Q5 static: land() calls questCatch only for fish, after the XP offer; setup calls questInit
    g = PW.calls(jar)
    land = g.get("FishCore.land", ())
    K.check(PKG + "FishBridge.questCatch" in land, "Q5 FishCore.land calls questCatch")
    cr = g.get("FishBench.craft", ())
    K.check(PKG + "FishRig.withRigG" in cr and PKG + "FishRig.withRig" not in cr and PKG + "FishRig.str" in cr,
            "FIX2 FishBench.craft makes the new rod with withRigG + the old rod's grant (str(doc(old), grant)): %s" % sorted(x for x in cr if "FishRig" in x))
    cl = JClass("javassist.ClassPool")(False)
    cl.appendSystemPath()
    cl.appendClassPath(jar)
    cl.appendClassPath(B.SERVER_JAR)
    mi = cl.get(PKG + "FishCore").getDeclaredMethod("land").getMethodInfo()
    ca = mi.getCodeAttribute()
    it = ca.iterator()
    cp = mi.getConstPool()
    seq = []
    while it.hasNext():
        pos = it.next()
        op = it.byteAt(pos)
        if op in (0xb6, 0xb8, 0xb9):
            idx = it.u16bitAt(pos + 1)
            try:
                seq.append(str(cp.getMethodrefClassName(idx)).rsplit(".", 1)[-1] + "." + str(cp.getMethodrefName(idx)))
            except Exception:
                pass
    xs = [i for i, n in enumerate(seq) if n == "FishBridge.skillXp"]
    qs = [i for i, n in enumerate(seq) if n == "FishBridge.questCatch"]
    mk = [i for i, n in enumerate(seq) if n == "FishRig.makeFish"]
    K.check(len(qs) == 1 and len(xs) == 2 and xs[0] < qs[0] < xs[1] and mk and mk[0] < qs[0],
            "Q5 ONE questCatch in land(): after the fish's XP offer, before the junk / treasure branch's XP (%s)" % [n for n in seq if "Bridge" in n])
    K.check(PKG + "FishBridge.questInit" in g.get("SkyyFishingPlugin.setup", ()), "Q5 the plugin's setup calls questInit")
    # ================================================================ P (0.1.5): THE LIFELONG POLE (every new code path)
    BD = JClass("org.bson.BsonDocument")

    def gdoc(ll_):
        return BD.parse('{"ll": %d, "lu": "abcdef0123456789", "lo": "pk1"}' % ll_)
    plainR = IS("SkyyFishing_Rod_Copper", 1)
    llR = plainR.withMetadata("SkyyGear", gdoc(1))
    K.check(not bool(Rig.llPole(plainR)) and bool(Rig.llPole(llR)) and not bool(Rig.llPole(plainR.withMetadata("SkyyGear", gdoc(0))))
            and not bool(Rig.llPole(None)) and not bool(Rig.llPole(plainR.withMetadata("SkyyGear", JClass("org.bson.BsonString")("x")))),
            "P1 llPole: only a rod whose SkyyGear document says ll 1 (none / ll 0 / not a document / no stack = false)")
    cg1 = Rig.carryGear(IS("SkyyFishing_Rod_Iron", 1), llR)
    cg2 = Rig.carryGear(IS("SkyyFishing_Rod_Iron", 1), plainR)
    K.check(str(cg1.getMetadata().get("SkyyGear").asDocument().getString("lu").getValue()) == "abcdef0123456789" and str(cg1.getItemId()) == "SkyyFishing_Rod_Iron"
            and (cg2.getMetadata() is None or not cg2.getMetadata().containsKey("SkyyGear")) and Rig.carryGear(None, llR) is None
            and Rig.carryGear(IS("SkyyFishing_Rod_Iron", 1), None) is not None,
            "P2 carryGear: the new rod takes ONLY the old rod's SkyyGear key (the same lifelong uid); a plain rod carries nothing; nulls are safe")
    t_ll = str(Rig.withRigG(llR, Rig.freshRig("SkyyFishing_Rod_Copper"), "").getMetadata().toJson())
    t_pl = str(Rig.withRigG(plainR, Rig.freshRig("SkyyFishing_Rod_Copper"), "").getMetadata().toJson())
    K.check(str(Rig.LL_LINE) in t_ll and str(Rig.LL_LINE) not in t_pl and "abcdef0123456789" in t_ll,
            "P3 withRigG: a lifelong pole lists the lifelong line (and keeps its SkyyGear key); a plain rod does not")
    K.check(str(Rig.LL_LINE) == "Lifelong fishing pole - can't be dropped. Lost it? /pole" and "levels with" not in str(Rig.LL_LINE),
            "P3 FIX 3.3: the lifelong line promises no Fishing levels yet: %s" % Rig.LL_LINE)
    # P7 (fix round, critic 3.2): SkyyGear's rebirth reset hands back the Wooden rod with our rig document + its SkyyGear key but NO tooltip
    baseW = Rig.withRigG(IS("SkyyFishing_Rod_Bamboo", 1), Rig.freshRig("SkyyFishing_Rod_Bamboo"), "pk1:g")
    stripW = IS("SkyyFishing_Rod_Bamboo", 1).withMetadata(str(Defs.META), Rig.doc(baseW)).withMetadata("SkyyGear", gdoc(1))
    fnR = br.get("fishing:fn:restamp")
    rW = fnR.apply(stripW)
    jW = str(rW.getMetadata().toJson())
    noDoc = IS("SkyyFishing_Rod_Copper", 1).withMetadata("SkyyGear", gdoc(1))
    K.check(bool(Rig.stale(stripW)) and not bool(Rig.stale(baseW)) and not bool(Rig.stale(Rig.withRigG(llR, Rig.freshRig("SkyyFishing_Rod_Copper"), "")))
            and str(Rig.LL_LINE) in jW and "abcdef0123456789" in jW and str(rW.getItemId()) == "SkyyFishing_Rod_Bamboo" and int(rW.getQuantity()) == 1
            and str(Rig.grantOf(rW)) == "pk1:g" and not bool(Rig.stale(rW))
            and fnR.apply(noDoc) == noDoc and str(fnR.apply(JClass("java.lang.String")("x"))) == "x" and Rig.restampOne(None) is None,
            "P7 FIX 3.2: fishing:fn:restamp redraws a lifelong pole that lost its tooltip (rig lines + the lifelong line, SkyyGear key + grant kept); "
            "stale() sees such a pole (the Fishing page redraws it too) but not a drawn rod; a rod without our document / not a stack = unchanged: %s" % jW[:240])
    GP = {"m": "stamp", "calls": []}

    @JImplements("java.util.function.Function")
    class GPole(object):
        @JOverride
        def apply(self, a):
            GP["calls"].append((str(a[0]), str(a[1].getItemId()), str(a[2])))
            m_ = GP["m"]
            if m_ == "stamp":
                return a[1].withMetadata("SkyyGear", gdoc(1))
            if m_ == "same":
                return a[1]
            if m_ == "throw":
                raise RuntimeError("gear refuses")
            if m_ == "other":
                return IS("Rock_Stone", 1)
            if m_ == "unstamped":
                return IS("SkyyFishing_Rod_Bamboo", 1)
            return None
    br.put("gear:fn:pole", GPole())
    st0 = int(QFn.STAMPED)
    stP = sf.apply(JArray(JObject)([u, "pk1:fishing_intro.take_pole:5"]))
    jsP = str(stP.getMetadata().toJson())
    K.check(bool(Rig.llPole(stP)) and str(Rig.LL_LINE) in jsP and "A gift from Marlow" in jsP and str(br.get("fishing:fn:grantOf").apply(stP)) == "pk1:fishing_intro.take_pole:5"
            and GP["calls"] == [(str(u), "SkyyFishing_Rod_Bamboo", "pk1:fishing_intro.take_pole:5")] and int(QFn.STAMPED) == st0 + 1
            and str(stP.getItemId()) == "SkyyFishing_Rod_Bamboo" and [str(x) for x in Rig.rigOf(stP)] == [str(x) for x in Rig.freshRig("SkyyFishing_Rod_Bamboo")],
            "P4 starterG: with SkyyGear the maker asks gear:fn:pole {uuid, the rod, the grant}: the stamped rod comes back with the lifelong + gift lines, "
            "the same fresh rig, the grant still in OUR document (SkyyQuests' guard): %s" % GP["calls"])
    outs = []
    for m_ in ("same", "throw", "other", "unstamped", "null"):
        GP["m"] = m_
        r_ = sf.apply(JArray(JObject)([u, "pk1:fishing_intro.take_pole:6"]))
        outs.append((m_, str(r_.getItemId()), bool(Rig.llPole(r_)), str(Rig.LL_LINE) in str(r_.getMetadata().toJson()), str(br.get("fishing:fn:grantOf").apply(r_))))
    br.remove("gear:fn:pole")
    r0_ = sf.apply(JArray(JObject)([u, "pk1:fishing_intro.take_pole:7"]))
    K.check(all(o_[1] == "SkyyFishing_Rod_Bamboo" and not o_[2] and not o_[3] and o_[4] == "pk1:fishing_intro.take_pole:6" for o_ in outs)
            and not bool(Rig.llPole(r0_)) and int(QFn.STAMPED) == st0 + 1,
            "P5 starterG: gear:fn:pole returning the same stack / throwing / another item / an unstamped rod / null, or no SkyyGear = the 0.1.4 rod exactly: %s" % outs)
    cr2 = []
    mi2 = cl.get(PKG + "FishBench").getDeclaredMethod("craft").getMethodInfo()
    it2 = mi2.getCodeAttribute().iterator()
    cp2 = mi2.getConstPool()
    while it2.hasNext():
        pos = it2.next()
        if it2.byteAt(pos) in (0xb6, 0xb8, 0xb9):
            try:
                cr2.append(str(cp2.getMethodrefClassName(it2.u16bitAt(pos + 1))).rsplit(".", 1)[-1] + "." + str(cp2.getMethodrefName(it2.u16bitAt(pos + 1))))
            except Exception:
                pass
    ic_ = [i for i, n in enumerate(cr2) if n == "FishRig.carryGear"]
    iw_ = [i for i, n in enumerate(cr2) if n == "FishRig.withRigG"]
    K.check(len(ic_) == 1 and len(iw_) == 1 and ic_[0] < iw_[0], "P6 FishBench.craft: carryGear (the old rod's SkyyGear document) BEFORE withRigG (the tooltip reads it)")
    # P8 (fix round 2, critic A1): a LIFELONG pole casts only for its owner (another profile's / a retired pole = refused); only with SkyyGear
    def gd2(lo_, rt_=False):
        return BD.parse('{"ll": 1, "lu": "abcdef0123456789", "lo": "%s"%s}' % (lo_, ', "lrt": 1' if rt_ else ''))
    mine_ = plainR.withMetadata("SkyyGear", gd2(str(u)))
    other_ = plainR.withMetadata("SkyyGear", gd2("someone-else"))
    ret_ = plainR.withMetadata("SkyyGear", gd2(str(u), True))
    wNo = Rig.llWhy(other_, u)          # gear:fn:pole was removed above = no SkyyGear 0.3.5
    br.put("gear:fn:pole", GPole())
    wMine, wOther, wRet, wPlain, wNull = Rig.llWhy(mine_, u), Rig.llWhy(other_, u), Rig.llWhy(ret_, u), Rig.llWhy(plainR, u), Rig.llWhy(None, u)
    K.check(wNo is None and wMine is None and wPlain is None and wNull is None and Rig.llWhy(other_, None) is None
            and "someone else's lifelong fishing pole" in str(wOther) and "retired" in str(wRet) and "/lifelong" in str(wRet),
            "P8 FIX 2 (critic A1): FishRig.llWhy: your own pole / a plain rod / no SkyyGear = may cast; another profile's pole or a retired one = "
            "refused: %s | %s" % (wOther, wRet))
    # ... and FishCore.cast EXECUTES it first (a stand-in FishApi counts the calls): refused = one chat line, no aim / bobber; your own = goes on
    Core_, Eng_ = P("FishCore"), P("FishEng")
    P("FishCfg").ON = True
    st2 = {"calls": {}, "slot": 0, "held": None, "reel": 0, "t": 0}
    Eng_.API = make_api(st2)
    c_ = Core_.ctxOf(u, "Tester", None, None, None, None, None)
    n0_ = int(Core_.LLNO)
    Core_.cast(c_, "SkyyFishing_Rod_Copper", 0, other_, None, 1000)
    a1_ = dict(st2["calls"])
    st2["calls"] = {}
    Core_.cast(c_, "SkyyFishing_Rod_Copper", 0, ret_, None, 1000)
    a2_ = dict(st2["calls"])
    st2["calls"] = {}
    Core_.cast(c_, "SkyyFishing_Rod_Copper", 0, mine_, None, 1000)
    n2_ = int(Core_.LLNO)
    br.remove("gear:fn:pole")
    K.check(a1_ == {"tell": 1} and a2_ == {"tell": 1} and n2_ == n0_ + 2 and Core_.STATES.get(u) is None,
            "P8 FIX 2: FishCore.cast refuses another profile's / a retired pole BEFORE anything else (one 'tell', no aim, no bobber, LLNO +2); your "
            "own pole passes the gate (LLNO unchanged): %s %s" % (a1_, a2_))
    Eng_.API = None
    K.save()


# ====================================================================================================== ST: start twice on a scratch COPY of live data
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyFishing")


def run_live(out, jar, scratch, home):
    """what setup runs (FishCfg.load, FishStore.start, FishBridge.questInit) twice on a scratch COPY of the live Skyy_SkyyFishing: 0.1.4
    has no saved-data change, so neither start writes anything; every live profile's progress reads back"""
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    P = lambda n: JClass(PKG + n)
    Cfg, Store_, Brg, Log = P("FishCfg"), P("FishStore"), P("FishBridge"), P("FishLog")
    Log.SINK = JClass("java.util.ArrayList")()
    Paths = JClass("java.nio.file.Paths")
    mods = os.path.dirname(home)
    h0 = HK.tree_hash(mods)
    q0 = HK.tree_hash(LIVE_DIR)
    hashes = []
    for n in range(2):
        Cfg.load(Paths.get(mods))
        Store_.start(Paths.get(mods))
        Brg.questInit()
        hashes.append(HK.tree_hash(mods))
    K.eq(hashes[0], h0, "ST start 1 on the live copy writes nothing (no saved-data change in 0.1.4)")
    K.eq(hashes[1], h0, "ST start 2 writes nothing")
    K.eq(HK.tree_hash(LIVE_DIR), q0, "ST the LIVE Skyy_SkyyFishing folder itself was only read")
    pl = os.path.join(home, "players")
    keys = sorted(f[:-len(".properties")] for f in os.listdir(pl) if f.endswith(".properties")) if os.path.isdir(pl) else []
    for k in keys:
        try:
            Store_.pond(k)
            K.check(True, "ST live profile %s reads (Pond Fish %d)" % (k, int(Store_.pond(k))))
        except Exception as ex:
            K.check(False, "ST live profile %s: %s" % (k, str(ex)[:160]))
    K.check(JClass("java.lang.System").getProperties().get("skyy.bridge").get("fishing:fn:starter") is not None, "ST questInit on a real start")
    K.notes.append("ST live profiles: %d" % len(keys))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyFishing", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("quest", run_quest), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyFishing"))
