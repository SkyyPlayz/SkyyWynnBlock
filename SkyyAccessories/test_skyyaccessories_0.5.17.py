"""Harness for SkyyAccessories 0.5.17 (THE STARTER ACCESSORY BAG: every profile gets ONE Accessory Bag item in its inventory, once;
Server Setup "Starter Accessory Bag" = starter.bag; tools/accessories_0_5_17_patch.py).
Build first: python tools/accessories_0_5_17_patch.py && python SkyyAccessories/build_skyyaccessories_0.5.17.py

    python SkyyAccessories/test_skyyaccessories_0.5.17.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.5.16 -> 0.5.17: exactly AccStarter added; AccDefs / AccCfg / AccTick / the plugin / the kit rows changed; no asset changed
  ST  the starter bag, EXECUTED on the jar's own AccStarter with REAL engine containers (SimpleItemContainer storage 36 / hotbar 9 /
      backpack 9 / utility 4 / tools 4 inside a stand-in Inventory, real ItemStacks from a test Item map, a stand-in PlayerRef whose packet
      handler records the chat lines) and a stand-in SkyyProfiles bridge (profile:fn:key / profile:<uuid> / profile:epoch / profile:busy):
        new profile -> given (storage first, 1 chat line); its marker is NOT on disk yet (DUE ~35 s; an early flush writes nothing; a
        re-login inside the window -> nothing, the answer stays in memory while due); a CRASH inside the window (memory gone, no marker):
        bag saved -> owned-inventory, bag rolled back -> given again (one bag either way); flush(all) (= shutdown) writes it; then
        again / re-login / drop + re-login -> nothing (marker);
        PROFILE SWITCH (key + inventory swapped like SkyyProfiles): profile 2 gets its own one, back to 1 -> nothing, back to 2 -> nothing
        (each profile exactly 1); busy / no profile yet / no epoch -> nothing, no marker; FULL inventory -> no item, no marker, one chat
        line; inside 60 s -> waits; after 60 s -> retried SILENTLY (no 2nd line); a new session tells once more; a freed slot gets it at
        the next retry; ALREADY OWNED in hotbar / utility / tools / backpack / the Void (catOf + count; paused Void waits; no catOf home =
        ignored) -> marker, nothing added; the bag's saved DATA alone (main or .more file) does NOT count -> given; an unreachable
        inventory (no combined container) -> "error": no chat, no wait, no marker, given once it works;
        unreadable marker -> nothing (warned once); marker write failing -> the bag once, kept in memory, flush writes it later;
        switch off -> nothing recorded; prune keeps a pending marker's answer
  CF  config: a first start writes starter.bag=true; a file without the key = on and its bytes untouched; starter.bag=false -> off (the
      load summary says so); the kit's console edit (= an in-game Server Setup edit) sets the field live and writes the file line; the
      config:def header carries the row
  AA  engine-access audit
NOT driven here: AccStarter.run()'s world-thread gates (a live world: ready, alive, same world - the AccRestampTask pattern) and the 5 s
AccTick dispatch (SkyyProfiles' real inventory swap is simulated by swapping the stand-in inventory). Exit code 1 on any failure.
"""
import os, sys, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.5.17"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAccessories-0.5.16.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "acc0517", "harness")))
PKG = "com.skyy.accessories."
BAG = "Skyy_Accessory_Bag"
JUNK = "Ingredient_Stick"
EXPECT = {
    "SkyyAccessoriesPlugin": ["~m setup", "~m shutdown"],
    "AccDefs": ["+f STARTER", "~<clinit>"],
    "AccCfg": ["+f STARTER_KEY", "~m load", "~m writeDefaults"],   # writeDefaults: the DEFAULT_TEXT constant (+ the starter.bag lines) is inlined
    "AccTick": ["~m run"],
    "CfgFile": ["~<clinit>"],          # the kit's copy of the default file text (+ the starter.bag lines)
    "CfgRows": ["~<clinit>", "~m header"],   # the rows table (+ starter.bag) and the version text
    "CfgFn": ["~m opExport"],          # the version text
}
ADDED = ["AccStarter"]


def run_starter(out, jar, scratch, _home):
    from jpype import JClass, JShort, JImplements, JOverride, JObject
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    Mod = JClass("java.lang.reflect.Modifier")
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)

    def jfield(cls, name):
        c = cls.class_ if hasattr(cls, "class_") else cls
        while c is not None:
            try:
                f = c.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                c = c.getSuperclass()
        raise KeyError(name)

    # ---- the Item asset map (the SkyyClasses / SkyyGear harness fake store + real Item objects)
    Item = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    DAM = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    CtF, CtM, CtC = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyTestFakeStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fake.addConstructor(CtC.make("public SkyyTestFakeStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
    astore = us.allocateInstance(fake.toClass(AS.class_))
    dam = DAM()
    jfield(AS, "assetMap").set(astore, dam)
    jfield(Item, "ASSET_STORE").set(None, astore)
    amap = jfield(DAM, "assetMap").get(dam)
    unknown = Item.UNKNOWN

    def mk_item(iid, stack):
        it = us.allocateInstance(Item.class_)
        for f in Item.class_.getDeclaredFields():
            if Mod.isStatic(f.getModifiers()):
                continue
            f.setAccessible(True)
            f.set(it, f.get(unknown))
        jfield(Item, "id").set(it, iid)
        jfield(Item, "maxStack").setInt(it, int(stack))
        amap.put(iid, it)
    mk_item(BAG, 1)
    mk_item(JUNK, 1)
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    K.check(int(IS(BAG, 1).getItem().getMaxStack()) == 1, "ST setup: the test items are in the Item map")

    # ---- a stand-in Inventory with REAL containers
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    INVN = "com.hypixel.hytale.server.core.inventory.Inventory"
    ICN = "com.hypixel.hytale.server.core.inventory.container.ItemContainer"
    CICN = "com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer"
    tinv = jp.makeClass("com.hypixel.hytale.server.core.inventory.SkyyAccTestInv", jp.get(INVN))
    for f_ in ("s", "h", "b", "u", "t"):
        tinv.addField(CtF.make("public %s %s;" % (ICN, f_), tinv))
    tinv.addField(CtF.make("public boolean x;", tinv))   # x = the combined container is missing (ST10)
    tinv.addConstructor(CtC.make("public SkyyAccTestInv(%s s, %s h, %s b, %s u, %s t) { super(); this.s = s; this.h = h; this.b = b; this.u = u; this.t = t; }"
                                 % (ICN, ICN, ICN, ICN, ICN), tinv))
    for src_ in ("public %s getStorage() { return this.s; }" % ICN, "public %s getHotbar() { return this.h; }" % ICN,
                 "public %s getBackpack() { return this.b; }" % ICN, "public %s getUtility() { return this.u; }" % ICN,
                 "public %s getTools() { return this.t; }" % ICN,
                 "public %s getCombinedStorageHotbarBackpack() { if (this.x) return null; return new %s(new %s[] { this.s, this.h, this.b }); }" % (CICN, CICN, ICN)):
        tinv.addMethod(CtM.make(src_, tinv))
    TInv = JClass(tinv.toClass(JClass(INVN).class_))
    tph = jp.makeClass("com.hypixel.hytale.server.core.io.SkyyAccTestPH", jp.get("com.hypixel.hytale.server.core.io.PacketHandler"))
    tph.addField(CtF.make("public static java.util.ArrayList OUT;", tph))
    tph.addMethod(CtM.make("public void writeNoCache(com.hypixel.hytale.protocol.ToClientPacket p) { OUT.add(p); }", tph))
    tph.addMethod(CtM.make("public void write(com.hypixel.hytale.protocol.ToClientPacket p) { OUT.add(p); }", tph))
    TPH = JClass(tph.toClass(JClass("com.hypixel.hytale.server.core.io.PacketHandler").class_))
    ArrayList, UUID, Paths, CHM = JClass("java.util.ArrayList"), JClass("java.util.UUID"), JClass("java.nio.file.Paths"), \
        JClass("java.util.concurrent.ConcurrentHashMap")
    TPH.OUT = ArrayList()
    PRN, PLA = JClass("com.hypixel.hytale.server.core.universe.PlayerRef"), JClass("com.hypixel.hytale.server.core.entity.entities.Player")

    def new_inv(fill=None, put=()):
        """storage 36, hotbar 9, backpack 9, utility 4, tools 4; fill = an id to fill storage + hotbar + backpack with; put = [(section, slot, id)]"""
        cs = dict(s=SIC(JShort(36)), h=SIC(JShort(9)), b=SIC(JShort(9)), u=SIC(JShort(4)), t=SIC(JShort(4)))
        if fill:
            for sec in "shb":
                for i in range(int(cs[sec].getCapacity())):
                    assert cs[sec].setItemStackForSlot(JShort(i), IS(fill, 1)).succeeded()
        for sec, sl, iid in put:
            assert cs[sec].setItemStackForSlot(JShort(sl), IS(iid, 1)).succeeded()
        return TInv(cs["s"], cs["h"], cs["b"], cs["u"], cs["t"])

    def where(inv, iid=BAG):
        res = []
        for tag, c in (("s", inv.getStorage()), ("h", inv.getHotbar()), ("b", inv.getBackpack()), ("u", inv.getUtility()), ("t", inv.getTools())):
            for i in range(int(c.getCapacity())):
                it = c.getItemStack(JShort(i))
                if it is not None and not it.isEmpty() and str(it.getItemId()) == iid:
                    res.append((tag, i, int(it.getQuantity())))
        return res

    def bags(inv):
        return sum(q for _t, _i, q in where(inv))
    seq = [0]

    def player(inv, name):
        p = us.allocateInstance(PLA.class_)
        jfield(PLA, "inventory").set(p, inv)
        pr = us.allocateInstance(PRN.class_)
        seq[0] += 1
        uid = UUID.fromString("00000000-0000-0000-0000-%012x" % (0xacc000 + seq[0]))
        jfield(PRN, "uuid").set(pr, uid)
        jfield(PRN, "username").set(pr, name)
        jfield(PRN, "packetHandler").set(pr, us.allocateInstance(TPH.class_))
        return p, pr, uid

    def swap(p, inv):   # SkyyProfiles' switch swaps the vanilla inventory
        jfield(PLA, "inventory").set(p, inv)

    # ---- the stand-in SkyyProfiles bridge
    bridge = CHM()
    JClass("java.lang.System").getProperties().put("skyy.bridge", bridge)
    KEYS = {}

    @JImplements("java.util.function.Function")
    class KeyFn(object):
        @JOverride
        def apply(self, u):
            return KEYS.get(str(u), str(u))

    bridge.put("profile:fn:key", KeyFn())
    J = lambda n: JClass(PKG + n)
    St, Acc, Defs = J("AccStarter"), J("AccStore"), J("AccDefs")
    for d in ("bags", "starter"):
        os.makedirs(os.path.join(scratch, "st", d), exist_ok=True)
    Acc.DIR = Paths.get(os.path.join(scratch, "st", "bags"))
    SDIR = os.path.join(scratch, "st", "starter")
    St.DIR = Paths.get(SDIR)
    K.check(bool(Defs.STARTER), "ST the switch is on by default")

    def online(uid, key, prof="1", epoch=1):
        KEYS[str(uid)] = key
        bridge.put("profile:%s" % uid, prof)
        bridge.put("profile:epoch:%s" % uid, JObject(epoch, "java.lang.Long"))

    def marker(key):   # AccTick's flush (the due markers) first, then the file on disk
        St.flush(False)
        f = os.path.join(SDIR, key + ".properties")
        if not os.path.exists(f):
            return None
        for ln in open(f, encoding="latin-1"):
            if ln.startswith("starterBag="):
                return ln.strip().split("=", 1)[1]
        return "file"

    def chats():
        return int(TPH.OUT.size())

    def step(pr, p):
        return str(St.step(pr, p))

    def relog():   # every player left (AccTick prune with nobody online) - the marker on disk answers next time
        St.prune(JClass("java.util.HashSet")())

    # ===== 1. a new profile gets one, storage first
    inv1 = new_inv()
    p, pr, U = player(inv1, "Alice")
    online(U, str(U))
    c0 = chats()
    K.eq(step(pr, p), "given", "ST1 new profile: the bag is given")
    K.eq(where(inv1), [("s", 0, 1)], "ST1 ... exactly one, in storage slot 0 (storage first)")
    K.eq(chats() - c0, 1, "ST1 ... one chat line")
    now = int(JClass("java.lang.System").currentTimeMillis())
    due = St.DUE.get(str(U))
    K.check(due is not None and 30000 <= int(due[1]) - now <= 36000 and str(due[0]) == "given", "ST1 ... its marker is due ~35 s later")
    K.eq(marker(str(U)), None, "ST1 ... not on disk yet (AccTick's flush writes nothing before it is due)")
    K.eq(step(pr, p), "done", "ST1 again in the same session: nothing")
    relog()
    K.eq(step(pr, p), "done", "ST1 re-login inside the window: nothing (the answer stays in memory while its marker is due)")
    St.DONE.clear()
    St.DUE.clear()
    K.eq(step(pr, p), "owned-inventory", "ST1 CRASH inside the window, the inventory was saved with the bag: owned-inventory")
    K.eq(bags(inv1), 1, "ST1 ... nothing added (one bag)")
    St.DONE.clear()
    St.DUE.clear()
    inv1.getStorage().removeItemStackFromSlot(JShort(0))   # the crash rolled the inventory back to before the give
    K.eq(step(pr, p), "given", "ST1 CRASH inside the window, the inventory rolled back without it: given again (never lost)")
    K.eq(bags(inv1), 1, "ST1 ... one bag")
    St.flush(True)
    K.eq(marker(str(U)), "given", "ST1 flush(all) (= shutdown) writes it at once: given")
    K.check(St.DUE.isEmpty(), "ST1 ... nothing pending")
    St.DELAY_MS = 0   # from here on markers are due at once (marker() runs AccTick's flush first)
    K.eq(step(pr, p), "done", "ST1 again in the same session: nothing")
    K.eq(bags(inv1), 1, "ST1 ... still one bag")
    relog()
    K.eq(step(pr, p), "marker", "ST1 re-login: the marker answers")
    K.eq(bags(inv1), 1, "ST1 ... still one bag")
    # ===== 2. drop it + re-login -> never a second one
    inv1.getStorage().removeItemStackFromSlot(JShort(0))
    K.eq(bags(inv1), 0, "ST2 the bag was dropped (taken out of the inventory)")
    relog()
    c0 = chats()
    K.eq(step(pr, p), "marker", "ST2 drop + re-login: nothing (the marker)")
    K.eq((bags(inv1), chats() - c0), (0, 0), "ST2 ... no bag, no chat")
    assert inv1.getStorage().setItemStackForSlot(JShort(0), IS(BAG, 1)).succeeded()   # picked it back up
    # ===== 3. PROFILE SWITCH: profile 2 gets its own one, never two in one profile
    inv2 = new_inv()
    swap(p, inv2)
    online(U, str(U) + "-p2", "2", 2)
    K.eq(step(pr, p), "given", "ST3 switch to a new profile 2: its own bag")
    K.eq((bags(inv1), bags(inv2)), (1, 1), "ST3 ... profile 1 keeps its one, profile 2 has one")
    K.eq(marker(str(U) + "-p2"), "given", "ST3 ... profile 2's own marker")
    swap(p, inv1)
    online(U, str(U), "1", 3)
    K.eq(step(pr, p), "done", "ST3 back to profile 1: nothing (its answer from earlier this session)")
    relog()
    K.eq(step(pr, p), "marker", "ST3 ... after a re-login: nothing (the marker)")
    swap(p, inv2)
    online(U, str(U) + "-p2", "2", 4)
    K.eq(step(pr, p), "marker", "ST3 back to profile 2 (after that re-login): nothing (its marker)")
    K.eq(step(pr, p), "done", "ST3 ... again: nothing")
    relog()
    K.eq(step(pr, p), "marker", "ST3 profile 2 after a re-login: nothing")
    K.eq((bags(inv1), bags(inv2)), (1, 1), "ST3 ... every profile exactly one bag")
    # ===== 4. the gates: busy, no profile yet, no epoch -> nothing, no marker
    inv3 = new_inv()
    swap(p, inv3)
    online(U, str(U) + "-p3", "3", 5)
    bridge.put("profile:busy:%s" % U, JObject(True, "java.lang.Boolean"))
    K.eq(step(pr, p), "blocked", "ST4 profile:busy (switch / crash recovery): nothing")
    bridge.remove("profile:busy:%s" % U)
    bridge.remove("profile:%s" % U)
    K.eq(step(pr, p), "noprofile", "ST4 no profile yet (first-join create page): nothing")
    bridge.put("profile:%s" % U, "3")
    bridge.remove("profile:epoch:%s" % U)
    K.eq(step(pr, p), "blocked", "ST4 SkyyProfiles present but no epoch (players file unreadable): nothing")
    K.eq((bags(inv3), marker(str(U) + "-p3")), (0, None), "ST4 ... no bag, no marker")
    online(U, str(U) + "-p3", "3", 6)
    K.eq(step(pr, p), "given", "ST4 gates clear: given")
    # ===== 5. FULL inventory
    invF = new_inv(fill=JUNK)
    pF, prF, UF = player(invF, "Fullo")
    online(UF, str(UF))
    c0 = chats()
    K.eq(step(prF, pF), "full", "ST5 full inventory: no bag")
    K.eq((bags(invF), marker(str(UF)), chats() - c0), (0, None, 1), "ST5 ... no item, no marker, one chat line")
    K.check(sum(q for _t, _i, q in where(invF, JUNK)) == 54, "ST5 ... nothing else moved (54 sticks)")
    K.eq(step(prF, pF), "waiting", "ST5 again inside 60 s: waits")
    K.eq(chats() - c0, 1, "ST5 ... not told twice")
    now = int(JClass("java.lang.System").currentTimeMillis())
    K.check(55000 <= int(St.WAIT.get(str(UF))) - now <= 61000, "ST5 ... the next silent retry is ~60 s away (dispatch skips it until then)")
    St.WAIT.put(str(UF), JObject(0, "java.lang.Long"))   # 60 s passed
    K.eq(step(prF, pF), "full-quiet", "ST5 after 60 s: tried again SILENTLY (still full)")
    K.eq((chats() - c0, bags(invF), marker(str(UF))), (1, 0, None), "ST5 ... no second chat line, no item, no marker")
    HS = JClass("java.util.HashSet")()
    HS.add(U)
    St.prune(HS)
    K.check(not bool(St.WAIT.containsKey(str(UF))), "ST5 the player left: the wait ends")
    c1 = chats()
    K.eq(step(prF, pF), "full", "ST5 next session, still full: told once more")
    K.eq(chats() - c1, 1, "ST5 ... one chat line")
    invF.getHotbar().removeItemStackFromSlot(JShort(5))
    K.eq(step(prF, pF), "waiting", "ST5 a slot freed inside the 60 s: waits for the retry")
    St.WAIT.put(str(UF), JObject(0, "java.lang.Long"))
    K.eq(step(prF, pF), "given", "ST5 the silent retry: given")
    K.eq(where(invF), [("h", 5, 1)], "ST5 ... into that slot (storage is full)")
    K.eq((marker(str(UF)), bool(St.WAIT.containsKey(str(UF))), chats() - c1), ("given", False, 2), "ST5 ... marker given, the wait gone, the given line")
    # ===== 6. ALREADY OWNED
    for sec, sl, label in (("h", 4, "hotbar"), ("u", 1, "utility"), ("t", 2, "tools"), ("b", 7, "backpack")):
        invO = new_inv(put=[(sec, sl, BAG)])
        pO, prO, UO = player(invO, "Owner")
        online(UO, str(UO))
        c0 = chats()
        K.eq(step(prO, pO), "owned-inventory", "ST6 a bag in the %s: counts as given" % label)
        K.eq((bags(invO), marker(str(UO)), chats() - c0), (1, "owned-inventory", 0), "ST6 ... nothing added, marker owned-inventory, no chat")
    for fname, label in (("%s.properties", "main"), ("%s.more.properties", ".more")):
        invD = new_inv()
        pD, prD, UD = player(invD, "Bagger")
        key = str(UD) + "-p4"
        online(UD, key, "4")
        open(os.path.join(scratch, "st", "bags", fname % key), "w").write("#SkyyAccessories bag\nslot0=Skyy_Accessory_Workbench_T1\n")
        K.eq(step(prD, pD), "given", "ST6 only the bag's saved data (%s file, /accessories used without the item): does NOT count - given" % label)
        K.eq((bags(invD), marker(key)), (1, "given"), "ST6 ... one bag, marker given")
    VOID = {"cat": None, "n": 0}

    @JImplements("java.util.function.Function")
    class CatFn(object):
        @JOverride
        def apply(self, iid):
            return VOID["cat"] if str(iid) == BAG else None

    @JImplements("java.util.function.Function")
    class CountFn(object):
        @JOverride
        def apply(self, a):
            return JObject(VOID["n"], "java.lang.Long")

    bridge.put("sacks:fn:catOf", CatFn())
    bridge.put("sacks:fn:count", CountFn())
    VOID.update(cat="Combat", n=1)
    invV = new_inv()
    pV, prV, UV = player(invV, "Voider")
    online(UV, str(UV))
    K.eq(step(prV, pV), "owned-void", "ST6 a bag in the Void (catOf gives it a home, count 1): counts as given")
    K.eq((bags(invV), marker(str(UV))), (0, "owned-void"), "ST6 ... nothing added, marker owned-void")
    VOID.update(n=-1)
    invV2 = new_inv()
    pV2, prV2, UV2 = player(invV2, "Paused")
    online(UV2, str(UV2))
    K.eq(step(prV2, pV2), "waitvoid", "ST6 the Void is paused (-1): waits")
    K.eq((bags(invV2), marker(str(UV2))), (0, None), "ST6 ... nothing added, no marker")
    VOID.update(cat=None, n=1)
    K.eq(step(prV2, pV2), "given", "ST6 no Void home for the bag (SkyySacks 0.8.x): the count is not asked - given")
    bridge.remove("sacks:fn:catOf")
    bridge.remove("sacks:fn:count")
    # ===== 7. an unreadable marker -> nothing, warned once
    invB = new_inv()
    pB, prB, UB = player(invB, "Broken")
    online(UB, str(UB))
    os.makedirs(os.path.join(SDIR, str(UB) + ".properties"))   # a folder where the file should be = cannot be read
    K.eq(step(prB, pB), "badmarker", "ST7 unreadable marker: nothing")
    K.eq(step(prB, pB), "badmarker", "ST7 ... again: nothing (one WARN only)")
    K.eq(bags(invB), 0, "ST7 ... no bag")
    # ===== 8. the marker cannot be written -> one bag, remembered, written later
    blocker = os.path.join(scratch, "st", "notadir")
    open(blocker, "w").write("x")
    St.DIR = Paths.get(os.path.join(blocker, "starter"))   # under a FILE: createDirectories fails
    invW = new_inv()
    pW, prW, UW = player(invW, "Writer")
    online(UW, str(UW))
    K.eq(step(prW, pW), "given", "ST8 marker write fails: the bag is given")
    St.flush(False)
    K.check(bool(St.DUE.containsKey(str(UW))) and bool(St.DONE.containsKey(str(UW))), "ST8 ... the write failed: the answer is kept in memory + still pending")
    St.prune(JClass("java.util.HashSet")())
    K.eq(step(prW, pW), "done", "ST8 ... even after the player left: no second bag (prune keeps a pending answer)")
    K.eq(bags(invW), 1, "ST8 ... one bag")
    St.flush(False)
    K.check(bool(St.DUE.containsKey(str(UW))), "ST8 flush while the folder is still broken: still pending")
    St.DIR = Paths.get(SDIR)
    K.check(marker(str(UW)) == "given" and not bool(St.DUE.containsKey(str(UW))), "ST8 flush once it works: the marker is written")
    # ===== 9. switched off -> nothing at all
    Defs.STARTER = False
    invX = new_inv()
    pX, prX, UX = player(invX, "Offy")
    online(UX, str(UX))
    K.eq(step(prX, pX), "off", "ST9 switch off: nothing")
    K.eq((bags(invX), marker(str(UX)), bool(St.DONE.containsKey(str(UX)))), (0, None, False), "ST9 ... no bag, no marker, nothing remembered")
    Defs.STARTER = True
    K.eq(step(prX, pX), "given", "ST9 switched on again: given")
    K.eq(bags(invX), 1, "ST9 ... one bag")
    # ===== 10. the inventory cannot be reached -> an error, not "full"
    invE = new_inv()
    invE.x = True
    pE, prE, UE = player(invE, "Erry")
    online(UE, str(UE))
    c0 = chats()
    K.eq(step(prE, pE), "error", "ST10 no combined container: an error, not full")
    K.eq((chats() - c0, bool(St.WAIT.containsKey(str(UE))), bool(St.DONE.containsKey(str(UE))), marker(str(UE)), bags(invE)),
         (0, False, False, None, 0), "ST10 ... no chat line, no wait, nothing remembered, no marker, no bag")
    K.check(bool(St.ADDWARNED), "ST10 ... warned (once)")
    K.eq(step(prE, pE), "error", "ST10 the next tick: tried again")
    invE.x = False
    K.eq(step(prE, pE), "given", "ST10 once it works: given")
    K.eq(bags(invE), 1, "ST10 ... one bag")
    K.eq(int(St.GIVEN), 11, "ST GIVEN counts the bags handed out (11: ST1 x2 incl. the crash re-give, ST3, ST4, ST5, ST6 data x2 + no Void home, ST8, ST9, ST10)")
    K.save()


def run_cfg(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Paths = JClass("java.nio.file.Paths")
    J = lambda n: JClass(PKG + n)
    Cfg, Defs = J("AccCfg"), J("AccDefs")
    mods = os.path.join(scratch, "cf", "mods")
    d = os.path.join(mods, "Skyy_SkyyAccessories")
    os.makedirs(d, exist_ok=True)
    f = os.path.join(d, "config.properties")
    Cfg.FILE = Paths.get(f)
    r = str(Cfg.load(True))
    t = open(f, encoding="latin-1").read()
    K.check("starter.bag=true" in t and bool(Defs.STARTER), "CF a first start writes starter.bag=true (on)")
    K.check("starter Accessory Bag" not in r, "CF ... the summary does not mention it while on: " + r[:120])
    old = b"slots=18\r\nregenEverySeconds=5\r\n"
    open(f, "wb").write(old)
    Defs.STARTER = False
    Cfg.reload()
    K.check(bool(Defs.STARTER) and open(f, "rb").read() == old, "CF a file without the key = on, its bytes untouched")
    open(f, "wb").write(old + b"starter.bag=false\r\n")
    r = str(Cfg.reload())
    K.check(not bool(Defs.STARTER) and "starter Accessory Bag switched off" in r, "CF starter.bag=false -> off, the summary says so")
    CP, Fn = J("CfgPub"), J("CfgFn")
    CP.start(Paths.get(mods), JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyAccessories"))
    m = str(Fn.cmdSetConsole("starter.bag", "true"))
    K.check(bool(Defs.STARTER), "CF the Server Setup edit sets the field live: " + m[:120])
    CP.shutdown()
    t = open(f, encoding="latin-1").read()
    K.check("starter.bag=true" in t and "starter.bag=false" not in t, "CF ... and writes the file line")
    br = JClass("java.lang.System").getProperties().get("skyy.bridge")
    hdr = br.get("config:def:SkyyAccessories") if br is not None else None
    rows = [[str(v) for v in r_] for r_ in hdr[7]] if hdr is not None else []
    row = [r_ for r_ in rows if r_[0] == "starter.bag"]
    K.check(len(row) == 1 and row[0][1:5] == ["Starter Accessory Bag", "bag", "bool", "true"] and row[0][9] == "live",
            "CF the config:def header carries the row: %s" % (row[0][:10] if row else rows[:1]))
    K.check([r_[0] for r_ in rows if r_[2] == "bag"] == ["slots", "notice.boosters", "starter.bag"], "CF ... in the Accessory Bag section, last")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyAccessories", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("starter", run_starter), ("cfg", run_cfg)], script=__file__)
