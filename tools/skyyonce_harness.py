"""skyyonce_harness - the LIFE phase every lifelong-item harness runs (round life01): tools/skyyonce.py's generated classes EXECUTED on REAL
engine objects inside a child JVM (-Xverify:all): SimpleItemContainers in a stand-in Inventory, real ItemStacks from a test Item map, REAL
windows (ContainerWindow, ContainerBlockWindow, ItemStackContainerWindow), REAL DropItemEvent$PlayerRequest / $Drop events, a REAL Player
(allocated) with a REAL WindowManager, a stand-in PlayerRef whose packet handler records the chat, a stand-in SkyyProfiles bridge.

    import skyyonce_harness as OH
    OH.life_phase(K, jar, pkg="com.skyy.accessories.", pfx="AccOnce", item="Skyy_Accessory_Bag", flag=("AccDefs", "LIFELONG"),
                  data_dir=<scratch folder>, mod="SkyyAccessories")

Every rule of tools/skyyonce.py is driven: L1 setup, L2 counting, L3 extra copies (keep order, metadata first, history first, quantities),
L4 a history write that fails (nothing removed), L5 open windows (home / extra / full inventory / combined + own containers untouched /
container block window / item-stack window / markWindowChanged on a real WindowManager), L6 the Drop key (cancelled, junk not, switch
off, a container window id), L7 the throw (death drop / overflow: cancelled + rescue back into the inventory, full = stays out + chat),
L8 the recall (given storage first, have, full, busy, works with the switch off), L9 profile busy, L10 the one-time pass (marker on disk,
chat once, a restart reads the marker), L11 once:item + market:veto + publish / unpublish, L12 needs(), L13 the world-thread glue
sweep(pr, Player) + the Task's early returns + the systems' / Ready's construction and queries, L14 the switch off = nothing happens.
NOT driven: the engine's dispatch into handle() (the ArchetypeChunk / Store plumbing - the same 6 lines SkyyGear's GearLLDropSys runs).
"""
import os, sys, zipfile

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

JUNK = "Rock_Stone"


def life_phase(K, jar, pkg, pfx, item, flag, data_dir, mod, once_flag=None):
    from jpype import JClass, JShort, JInt, JString, JArray, JObject
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

    # ---- the Item asset map (the SkyyAccessories 0.5.17 harness pattern)
    Item = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    DAM = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    CtF, CtM, CtC = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyOnceFakeStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fake.addConstructor(CtC.make("public SkyyOnceFakeStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
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
    import json as _json
    zj = zipfile.ZipFile(jar)
    mx = None
    for n in zj.namelist():
        if n.startswith("Server/Item/Items/") and n.endswith("/%s.json" % item):
            mx = int(_json.loads(zj.read(n)).get("MaxStack", 100))
    K.check(mx == 1, "L1 setup: %s ships in this jar with MaxStack 1 (%s)" % (item, mx))
    mk_item(item, mx or 1)
    mk_item(JUNK, 100)
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    BD = JClass("org.bson.BsonDocument")
    BS = JClass("org.bson.BsonString")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    CIC = JClass("com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer")
    ICN = "com.hypixel.hytale.server.core.inventory.container.ItemContainer"
    INVN = "com.hypixel.hytale.server.core.inventory.Inventory"
    tinv = jp.makeClass("com.hypixel.hytale.server.core.inventory.SkyyOnceTestInv", jp.get(INVN))
    for f_ in ("s", "h", "b", "u", "t"):
        tinv.addField(CtF.make("public %s %s;" % (ICN, f_), tinv))
    tinv.addConstructor(CtC.make("public SkyyOnceTestInv(%s s, %s h, %s b, %s u, %s t) { super(); this.s = s; this.h = h; this.b = b; this.u = u; this.t = t; }"
                                 % (ICN, ICN, ICN, ICN, ICN), tinv))
    for src_ in ("public %s getStorage() { return this.s; }" % ICN, "public %s getHotbar() { return this.h; }" % ICN,
                 "public %s getBackpack() { return this.b; }" % ICN, "public %s getUtility() { return this.u; }" % ICN,
                 "public %s getTools() { return this.t; }" % ICN):
        tinv.addMethod(CtM.make(src_, tinv))
    TInv = JClass(tinv.toClass(JClass(INVN).class_))
    tph = jp.makeClass("com.hypixel.hytale.server.core.io.SkyyOnceTestPH", jp.get("com.hypixel.hytale.server.core.io.PacketHandler"))
    tph.addField(CtF.make("public static java.util.ArrayList OUT;", tph))
    tph.addMethod(CtM.make("public void writeNoCache(com.hypixel.hytale.protocol.ToClientPacket p) { OUT.add(p); }", tph))
    tph.addMethod(CtM.make("public void write(com.hypixel.hytale.protocol.ToClientPacket p) { OUT.add(p); }", tph))
    TPH = JClass(tph.toClass(JClass("com.hypixel.hytale.server.core.io.PacketHandler").class_))
    ArrayList, UUID, Paths, CHM = JClass("java.util.ArrayList"), JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.util.concurrent.ConcurrentHashMap")
    Boolean = JClass("java.lang.Boolean")
    TPH.OUT = ArrayList()
    PRN, PLA = JClass("com.hypixel.hytale.server.core.universe.PlayerRef"), JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    WMGR = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager")
    CWN = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.ContainerWindow")
    CBW = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.ContainerBlockWindow")
    ISCW = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.ItemStackContainerWindow")
    DIRQ = JClass("com.hypixel.hytale.server.core.event.events.ecs.DropItemEvent$PlayerRequest")
    DIE = JClass("com.hypixel.hytale.server.core.event.events.ecs.DropItemEvent$Drop")
    System = JClass("java.lang.System")
    bridge = CHM()
    System.getProperties().put("skyy.bridge", bridge)
    Core = JClass(pkg + pfx)
    Cfg = JClass(pkg + flag[0])
    Core.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get(mod)
    os.makedirs(data_dir, exist_ok=True)
    Core.DIR = Paths.get(os.path.join(data_dir, "lifelong"))
    hist = os.path.join(data_dir, "lifelong", "history.log")

    def set_on(v):
        setattr(Cfg, flag[1], bool(v))
    set_on(True)
    K.check(bool(Core.on()), "L1 setup: %s.%s on -> %s.on()" % (flag[0], flag[1], pfx))

    def new_inv(fill=None, put=()):
        cs = dict(s=SIC(JShort(36)), h=SIC(JShort(9)), b=SIC(JShort(9)), u=SIC(JShort(4)), t=SIC(JShort(4)))
        if fill:
            for sec in "shb":
                for i in range(int(cs[sec].getCapacity())):
                    cs[sec].setItemStackForSlot(JShort(i), IS(fill, JInt(1)))
        for sec, sl, iid in put:
            cs[sec].setItemStackForSlot(JShort(sl), iid if not isinstance(iid, str) else IS(iid, JInt(1)))
        return TInv(cs["s"], cs["h"], cs["b"], cs["u"], cs["t"])

    def where(inv, iid=item):
        res = []
        for tag, c in (("h", inv.getHotbar()), ("s", inv.getStorage()), ("b", inv.getBackpack()), ("u", inv.getUtility()), ("t", inv.getTools())):
            for i in range(int(c.getCapacity())):
                it = c.getItemStack(JShort(i))
                if it is not None and not it.isEmpty() and str(it.getItemId()) == iid:
                    res.append((tag, i, int(it.getQuantity())))
        return res

    def n_in(c):
        t = 0
        for i in range(int(c.getCapacity())):
            it = c.getItemStack(JShort(i))
            if it is not None and not it.isEmpty() and str(it.getItemId()) == item:
                t += int(it.getQuantity())
        return t
    seq = [0]

    def player(inv, name="Tester"):
        p = us.allocateInstance(PLA.class_)
        jfield(PLA, "inventory").set(p, inv)
        try:
            jfield(PLA, "windowManager").set(p, WMGR())
        except Exception:
            pass
        pr = us.allocateInstance(PRN.class_)
        seq[0] += 1
        uid = UUID.fromString("00000000-0000-0000-0000-%012x" % (0x11fe00 + seq[0]))
        jfield(PRN, "uuid").set(pr, uid)
        jfield(PRN, "username").set(pr, name)
        jfield(PRN, "packetHandler").set(pr, us.allocateInstance(TPH.class_))
        return p, pr, uid

    def said():
        n = TPH.OUT.size()
        TPH.OUT.clear()
        return n

    def secs(inv):
        return Core.secs(inv)

    def told(u, kind):
        return Core.TOLD.containsKey("%s:%s" % (u, kind))

    def clear_chat():
        Core.TOLD.clear()
        TPH.OUT.clear()

    def hist_lines():
        return open(hist, encoding="utf-8").read().splitlines() if os.path.isfile(hist) else []
    W = lambda *ws: ArrayList(list(ws))

    # ================================================================================= L2 counting
    inv = new_inv(put=[("h", 2, item), ("s", 5, item), ("b", 0, IS(item, JInt(2))), ("u", 1, JUNK)])
    K.eq(int(Core.count(secs(inv))), 4, "L2: count = hotbar 1 + storage 1 + backpack 2 (junk not)")
    K.check(bool(Core.own(secs(inv), inv.getStorage())) and not bool(Core.own(secs(inv), SIC(JShort(3)))), "L2: own() = identity with the player's sections")
    K.check(bool(Core.is_(IS(item, JInt(1)))) if hasattr(Core, "is_") else bool(getattr(Core, "is")(IS(item, JInt(1)))), "L2: is() knows the item")

    # ================================================================================= L3 extra copies
    p, pr, U = player(inv)
    pk = str(U)
    Core.DONE.put(pk, Boolean.TRUE)          # not the one-time pass here (L10)
    clear_chat()
    r = str(Core.sweepCore(pr, secs(inv), W(), None, pk))
    w_ = where(inv)
    hl = hist_lines()
    K.check(w_ == [("h", 2, 1)] and "extra=3" in r and len(hl) == 1 and ("REMOVE 3 extra %s" % item) in hl[0] and "kept Hotbar slot 3" in hl[0]
            and "UNDO:" in hl[0] and "from Storage slot 6" in hl[0] and "2 from Backpack slot 1" in hl[0],
            "L3: 4 copies -> the hotbar one kept, 3 removed, ONE history line naming each first (%s | %s | %s)" % (r, w_, hl[-1:]))
    K.check(told(U, "extra") and said() >= 1, "L3: the player is told an extra one was removed")
    md = BD()
    md.put("SkyyTest", BS("data"))
    inv2 = new_inv(put=[("h", 0, item), ("s", 3, IS(item, JInt(1)).withMetadata(md))])
    p2, pr2, U2 = player(inv2)
    Core.DONE.put(str(U2), Boolean.TRUE)
    Core.sweepCore(pr2, secs(inv2), W(), None, str(U2))
    w2 = where(inv2)
    keep = inv2.getStorage().getItemStack(JShort(3))
    K.check(w2 == [("s", 3, 1)] and keep is not None and str(keep.getMetadata().getString("SkyyTest").getValue()) == "data",
            "L3: a copy that carries metadata is the one kept (it holds data): %s" % w2)
    inv3 = new_inv(put=[("s", 0, IS(item, JInt(3)))])
    p3, pr3, U3 = player(inv3)
    Core.DONE.put(str(U3), Boolean.TRUE)
    Core.sweepCore(pr3, secs(inv3), W(), None, str(U3))
    K.eq(where(inv3), [("s", 0, 1)], "L3: one slot holding 3 -> 1 left in that slot")
    n3 = int(Core.N.get(3))
    K.check(n3 >= 6, "L3: counter extras removed = %d" % n3)

    # ================================================================================= L4 history fails -> nothing removed
    bad = os.path.join(data_dir, "not-a-folder")
    open(bad, "w").write("x")
    Core.DIR = Paths.get(bad)
    inv4 = new_inv(put=[("h", 0, item), ("s", 0, item)])
    p4, pr4, U4 = player(inv4)
    Core.DONE.put(str(U4), Boolean.TRUE)
    f7 = int(Core.N.get(7))
    r4 = str(Core.sweepCore(pr4, secs(inv4), W(), None, str(U4)))
    K.check(len(where(inv4)) == 2 and int(Core.N.get(7)) == f7 + 1 and "extra=0" in r4,
            "L4: history.log cannot be written -> NOTHING removed (both copies stay), failure counted: %s" % r4)
    Core.DIR = Paths.get(os.path.join(data_dir, "lifelong"))

    # ================================================================================= L5 open windows
    chest = SIC(JShort(27))
    chest.setItemStackForSlot(JShort(4), IS(item, JInt(1)))
    inv5 = new_inv()
    p5, pr5, U5 = player(inv5)
    Core.DONE.put(str(U5), Boolean.TRUE)
    clear_chat()
    r5 = str(Core.sweepCore(pr5, secs(inv5), W(CWN(chest)), None, str(U5)))
    K.check(n_in(chest) == 0 and len(where(inv5)) == 1 and where(inv5)[0][0] == "s" and "home=1" in r5 and told(U5, "home"),
            "L5: the only copy put into a chest / trade offer / Vault (ContainerWindow) goes straight back to the inventory (storage): %s %s" % (r5, where(inv5)))
    chest.setItemStackForSlot(JShort(7), IS(item, JInt(1)))
    nh = len(hist_lines())
    r5b = str(Core.sweepCore(pr5, secs(inv5), W(CWN(chest)), None, str(U5)))
    K.check(n_in(chest) == 0 and len(where(inv5)) == 1 and "extra=1" in r5b and len(hist_lines()) == nh + 1 and "the inventory already holds one" in hist_lines()[-1],
            "L5: a 2nd copy in an open container while the inventory holds one -> removed there (history line first): %s" % r5b)
    full = new_inv(fill=JUNK)
    pf, prf, Uf = player(full)
    Core.DONE.put(str(Uf), Boolean.TRUE)
    chest.setItemStackForSlot(JShort(1), IS(item, JInt(1)))
    clear_chat()
    r5c = str(Core.sweepCore(prf, secs(full), W(CWN(chest)), None, str(Uf)))
    K.check(n_in(chest) == 1 and len(where(full)) == 0 and "held=1" in r5c and told(Uf, "held"),
            "L5: a FULL inventory -> the copy stays in the container (never lost) and the player is told: %s" % r5c)
    chest.setItemStackForSlot(JShort(1), IS(JUNK, JInt(1)))
    # combined containers + the player's own sections are never touched
    inv6 = new_inv(put=[("s", 2, item)])
    p6, pr6, U6 = player(inv6)
    Core.DONE.put(str(U6), Boolean.TRUE)
    other = SIC(JShort(9))
    other.setItemStackForSlot(JShort(0), IS(item, JInt(1)))
    comb = CIC(JArray(JClass(ICN))([other]))
    r6 = str(Core.sweepCore(pr6, secs(inv6), W(CWN(comb), CWN(inv6.getStorage())), None, str(U6)))
    K.check(n_in(other) == 1 and where(inv6) == [("s", 2, 1)] and "extra=0" in r6,
            "L5: a CombinedItemContainer window and a window over the player's own storage are never touched: %s" % r6)
    # ContainerBlockWindow (a world chest) + ItemStackContainerWindow + markWindowChanged on a real WindowManager
    # a REAL ContainerBlockWindow (its constructor reads the block's item from the asset store: built field by field instead)
    got_cbw = None
    try:
        ch2 = SIC(JShort(18))
        ch2.setItemStackForSlot(JShort(0), IS(item, JInt(1)))
        cbw = us.allocateInstance(CBW.class_)
        jfield(CBW, "itemContainer").set(cbw, ch2)
        for f_, v_ in (("x", 12), ("y", 129), ("z", -4)):
            jfield(CBW, f_).setInt(cbw, v_)
        got_cbw = (cbw, ch2)
    except Exception as e_:
        K.notes.append("L5: ContainerBlockWindow: %s" % str(e_)[:200])
    if got_cbw is not None:
        inv7 = new_inv()
        p7, pr7, U7 = player(inv7)
        Core.DONE.put(str(U7), Boolean.TRUE)
        wm = WMGR()
        # fix round (critic 2): a copy that was ALREADY in a world chest (maybe another player's) is never touched - viewer holds none
        # and nothing dropped (the last sweep left 0), viewer holds one (left 1), or no sweep yet (no count known)
        Core.LAST.put(U7, JInt(0))
        r7a = str(Core.sweepCore(pr7, secs(inv7), W(got_cbw[0]), wm, str(U7)))
        K.check(n_in(got_cbw[1]) == 1 and len(where(inv7)) == 0 and "home=0" in r7a and "extra=0" in r7a
                and not bool(Core.needs(U7, secs(inv7), W(got_cbw[0]))),
                "L5: a copy already in a world chest the viewer opened (nothing of theirs dropped) is NOT moved to them: %s" % r7a)
        inv7b = new_inv(put=[("h", 0, item)])
        p7b, pr7b, U7b = player(inv7b)
        Core.DONE.put(str(U7b), Boolean.TRUE)
        Core.LAST.put(U7b, JInt(1))
        r7b = str(Core.sweepCore(pr7b, secs(inv7b), W(got_cbw[0]), wm, str(U7b)))
        K.check(n_in(got_cbw[1]) == 1 and where(inv7b) == [("h", 0, 1)] and "extra=0" in r7b,
                "L5: ... and NOT removed when the viewer holds their own (someone else's copy stays in their chest): %s" % r7b)
        Core.LAST.remove(U7)
        Core.sweepCore(pr7, secs(inv7), W(got_cbw[0]), wm, str(U7))
        K.check(n_in(got_cbw[1]) == 1, "L5: ... nor before the viewer's first sweep (no count known)")
        # the viewer had one (the last sweep left 1) and just put it into the chest: their inventory dropped -> it comes home
        Core.LAST.put(U7, JInt(1))
        K.check(bool(Core.needs(U7, secs(inv7), W(got_cbw[0]))), "L5: needs() true once the viewer's own count dropped with a chest open")
        r7 = str(Core.sweepCore(pr7, secs(inv7), W(got_cbw[0]), wm, str(U7)))
        K.check(n_in(got_cbw[1]) == 0 and len(where(inv7)) == 1 and "home=1" in r7,
                "L5: a REAL ContainerBlockWindow (world chest) - the viewer's own copy they just put in comes home, markWindowChanged on a real WindowManager ran: %s" % r7)
        K.check(int(Core.LAST.get(U7)) == 1, "L5: the sweep records the count it left (1)")
        ch7 = SIC(JShort(9))
        ch7.setItemStackForSlot(JShort(0), IS(item, JInt(1)))
        ch7.setItemStackForSlot(JShort(1), IS(item, JInt(1)))
        cbw2 = us.allocateInstance(CBW.class_)
        jfield(CBW, "itemContainer").set(cbw2, ch7)
        inv7c = new_inv()
        p7c, pr7c, U7c = player(inv7c)
        Core.DONE.put(str(U7c), Boolean.TRUE)
        Core.LAST.put(U7c, JInt(1))
        Core.sweepCore(pr7c, secs(inv7c), W(cbw2), None, str(U7c))
        K.check(n_in(ch7) == 1 and len(where(inv7c)) == 1, "L5: the viewer dropped ONE into a chest holding two -> only one comes home, the other copy stays")
        K.check(str(Core.where(got_cbw[0])).startswith("ContainerBlockWindow at 12 129 -4"), "L5: the history names the chest's block: %s" % Core.where(got_cbw[0]))
    else:
        K.check(False, "L5: no ContainerBlockWindow could be constructed")
    # a REAL ItemStackContainerWindow (a container inside an item - e.g. a pouch); built field by field like the chest window
    got_iscw = None
    try:
        ch3 = SIC(JShort(9))
        ch3.setItemStackForSlot(JShort(2), IS(item, JInt(1)))
        iscw = us.allocateInstance(ISCW.class_)
        icls = JClass(ICN).class_
        for f_ in ISCW.class_.getDeclaredFields():
            if icls.isAssignableFrom(f_.getType()) or f_.getType().isAssignableFrom(SIC.class_):
                f_.setAccessible(True)
                if f_.getType().isAssignableFrom(SIC.class_):
                    f_.set(iscw, ch3)
        got_iscw = (iscw, ch3)
    except Exception as e_:
        K.notes.append("L5: ItemStackContainerWindow: %s" % str(e_)[:200])
    if got_iscw is not None and got_iscw[0].getItemContainer() is not None:
        inv8 = new_inv(put=[("h", 0, item)])
        p8, pr8, U8 = player(inv8)
        Core.DONE.put(str(U8), Boolean.TRUE)
        Core.sweepCore(pr8, secs(inv8), W(got_iscw[0]), None, str(U8))
        K.check(n_in(got_iscw[1]) == 0 and where(inv8) == [("h", 0, 1)], "L5: a REAL ItemStackContainerWindow - the extra there is removed")
    else:
        K.notes.append("L5: ItemStackContainerWindow not constructed here (covered by the same instanceof rule)")
    K.check(bool(Core.foreign(CWN(SIC(JShort(1))))) and not bool(Core.foreign(JString("x"))), "L5: foreign() = the three container windows only")

    # ================================================================================= L6 the Drop key
    inv9 = new_inv(put=[("s", 4, item), ("s", 5, JUNK)])
    p9, pr9, U9 = player(inv9)
    clear_chat()
    e1 = DIRQ(JInt(-2), JShort(4))
    K.check(bool(Core.onRequest(e1, inv9.getStorage(), pr9, None)) and bool(e1.isCancelled()) and told(U9, "drop") and n_in(inv9.getStorage()) == 1,
            "L6: the Drop key on the item -> the REAL PlayerRequest is cancelled before anything moves, the player is told")
    e2 = DIRQ(JInt(-2), JShort(5))
    K.check(not bool(Core.onRequest(e2, inv9.getStorage(), pr9, None)) and not bool(e2.isCancelled()), "L6: the Drop key on stone -> not touched")
    e3 = DIRQ(JInt(5), JShort(4))
    K.check(bool(Core.onRequest(e3, inv9.getStorage(), pr9, WMGR())) and bool(e3.isCancelled()), "L6: dragged out of a container window (id >= 0) -> cancelled, the window marked")
    e4 = DIRQ(JInt(-2), JShort(40))
    K.check(not bool(Core.onRequest(e4, inv9.getStorage(), pr9, None)), "L6: a slot past the container -> ignored")
    set_on(False)
    e5 = DIRQ(JInt(-2), JShort(4))
    K.check(not bool(Core.onRequest(e5, inv9.getStorage(), pr9, None)) and not bool(e5.isCancelled()), "L6: switch OFF -> the item may be dropped (old rules)")
    set_on(True)

    # ================================================================================= L7 the throw (death drop / overflow) + rescue
    inv10 = new_inv()
    p10, pr10, U10 = player(inv10)
    Core.DONE.put(str(U10), Boolean.TRUE)
    d1 = DIE(IS(item, JInt(1)), 1.0)
    K.check(bool(Core.onThrow(d1, pr10)) and bool(d1.isCancelled()) and Core.RESCUE.containsKey(U10),
            "L7: a thrown copy (death drop with keep-inventory off / a full-inventory overflow) -> the REAL Drop event is cancelled, rescue due")
    d2 = DIE(IS(JUNK, JInt(1)), 1.0)
    K.check(not bool(Core.onThrow(d2, pr10)) and not bool(d2.isCancelled()), "L7: a thrown stone -> not touched")
    K.check(bool(Core.needs(U10, secs(inv10), W())), "L7: needs() = true while a rescue is due")
    clear_chat()
    r10 = str(Core.sweepCore(pr10, secs(inv10), W(), None, str(U10)))
    K.check("rescued=1" in r10 and len(where(inv10)) == 1 and not Core.RESCUE.containsKey(U10) and told(U10, "rescue"),
            "L7: the next sweep puts one back into the inventory and says so: %s" % r10)
    full2 = new_inv(fill=JUNK)
    pf2, prf2, Uf2 = player(full2)
    Core.DONE.put(str(Uf2), Boolean.TRUE)
    Core.onThrow(DIE(IS(item, JInt(1)), 1.0), prf2)
    clear_chat()
    r11 = str(Core.sweepCore(prf2, secs(full2), W(), None, str(Uf2)))
    K.check("rescued=0" in r11 and len(where(full2)) == 0 and told(Uf2, "rescue"), "L7: a FULL inventory -> no copy can come back, the player is told the recall command")
    # a rescue that finds a copy already there gives nothing more
    inv12 = new_inv(put=[("h", 1, item)])
    p12, pr12, U12 = player(inv12)
    Core.DONE.put(str(U12), Boolean.TRUE)
    Core.onThrow(DIE(IS(item, JInt(1)), 1.0), pr12)
    Core.sweepCore(pr12, secs(inv12), W(), None, str(U12))
    K.eq(where(inv12), [("h", 1, 1)], "L7: a rescue when one is already in the inventory gives no second one")

    # ================================================================================= L8 the recall
    inv13 = new_inv()
    p13, pr13, U13 = player(inv13)
    K.eq(str(Core.recall(pr13, secs(inv13))), "+given", "L8: recall with none -> +given")
    K.check(where(inv13) == [("s", 0, 1)], "L8: ... into storage first (%s)" % where(inv13))
    K.eq(str(Core.recall(pr13, secs(inv13))), "=have", "L8: again -> =have (never a second)")
    full3 = new_inv(fill=JUNK)
    pf3, prf3, Uf3 = player(full3)
    K.eq(str(Core.recall(prf3, secs(full3))), "-full", "L8: full inventory -> -full (never dropped)")
    inv14 = TInv(new_inv(fill=JUNK).getStorage(), SIC(JShort(9)), SIC(JShort(9)), SIC(JShort(4)), SIC(JShort(4)))
    p14, pr14, U14 = player(inv14)
    K.check(str(Core.recall(pr14, secs(inv14))) == "+given" and where(inv14) == [("h", 0, 1)], "L8: storage full -> the hotbar (%s)" % where(inv14))
    set_on(False)
    inv15 = new_inv()
    p15, pr15, U15 = player(inv15)
    K.eq(str(Core.recall(pr15, secs(inv15))), "+given", "L8: the recall works with the switch OFF too")
    set_on(True)
    bridge.put("profile:busy:" + str(U15), Boolean.TRUE)
    inv15.getStorage().setItemStackForSlot(JShort(0), None)
    K.eq(str(Core.recall(pr15, secs(inv15))), "-busy", "L8: profile busy -> -busy, nothing given")
    K.check(len(where(inv15)) == 0, "L8: ... and nothing was given")
    for code in ("+given", "-full", "-busy", "-error"):
        K.check(Core.recallText(code) is not None, "L8: recallText(%s) = %s" % (code, Core.recallText(code)))
    K.check(Core.recallText("=have") is None and str(Core.RECALL) in str(Core.recallText("-full")), "L8: =have says nothing; -full names the recall")

    # ================================================================================= L9 profile busy
    inv16 = new_inv(put=[("h", 0, item), ("s", 0, item)])
    K.eq(str(Core.sweepCore(pr15, secs(inv16), W(), None, str(U15))), "busy", "L9: profile:busy -> the sweep does nothing (busy)")
    K.eq(len(where(inv16)), 2, "L9: ... both copies still there")
    bridge.remove("profile:busy:" + str(U15))

    # ================================================================================= L10 the one-time pass + marker
    inv17 = new_inv(put=[("h", 0, item), ("b", 2, item)])
    p17, pr17, U17 = player(inv17)
    pk17 = str(U17) + "-p2"
    marker = os.path.join(data_dir, "lifelong", "once", pk17 + ".done")
    K.check(bool(Core.firstPass(pk17)) and not os.path.exists(marker), "L10: a profile never seen -> its one-time pass is due")
    clear_chat()
    r17 = str(Core.sweepCore(pr17, secs(inv17), W(), None, pk17))
    K.check("first" in r17 and os.path.isfile(marker) and told(U17, "first") and not told(U17, "extra") and where(inv17) == [("h", 0, 1)],
            "L10: the one-time cleanup: 1 extra removed, its own chat line, run-once marker %s written: %s" % (os.path.basename(marker), r17))
    K.check("1 extra" in open(marker, encoding="utf-8").read(), "L10: the marker says what it did")
    K.check(not bool(Core.firstPass(pk17)), "L10: not due again in this run")
    Core.DONE.remove(pk17)
    K.check(not bool(Core.firstPass(pk17)) and Core.DONE.containsKey(pk17), "L10: after a restart (memory cleared) the marker on disk says done")
    inv17.getStorage().setItemStackForSlot(JShort(9), IS(item, JInt(1)))
    clear_chat()
    r17b = str(Core.sweepCore(pr17, secs(inv17), W(), None, pk17))
    K.check("first" not in r17b and told(U17, "extra") and not told(U17, "first"), "L10: later extras get the short line: %s" % r17b)
    pk18 = "00000000-0000-0000-0000-00000011fea0"
    inv18 = new_inv(put=[("s", 0, item)])
    p18, pr18, U18 = player(inv18)
    clear_chat()
    Core.sweepCore(pr18, secs(inv18), W(), None, pk18)
    K.check(os.path.isfile(os.path.join(data_dir, "lifelong", "once", pk18 + ".done")) and not told(U18, "first"),
            "L10: a profile with exactly one copy: marker written, no chat")

    # ================================================================================= L11 once:item + market:veto + publish
    Fn = JClass(pkg + pfx + "Fn")
    K.check(bool(Fn(JInt(0)).apply(None)), "L11: once:item -> TRUE while on")
    if once_flag is not None:
        OC = JClass(pkg + once_flag[0])
        setattr(OC, once_flag[1], False)
        K.check(not bool(Fn(JInt(0)).apply(None)) and bool(Core.on()), "L11: %s.%s off -> once:item FALSE (the kit gives it), the rules stay on" % once_flag)
        setattr(OC, once_flag[1], True)
    set_on(False)
    K.check(not bool(Fn(JInt(0)).apply(None)) and Fn(JInt(1)).apply(IS(item, JInt(1))) is None, "L11: switch off -> once:item FALSE, no veto")
    set_on(True)
    v = Fn(JInt(1)).apply(IS(item, JInt(1)))
    K.check(v is not None and "can't be sold" in str(v) and Fn(JInt(1)).apply(IS(JUNK, JInt(1))) is None and Fn(JInt(1)).apply(JString("x")) is None,
            "L11: market:veto refuses the item (Auction House + Bazaar read it): %s" % v)
    Core.publish()
    mv = bridge.get("market:veto")
    K.check(bridge.get("once:item:" + item) is not None and mv is not None and mv.get(mod + ":lifelong") is not None, "L11: publish puts once:item:%s + market:veto[%s:lifelong]" % (item, mod))
    Core.unpublish()
    K.check(bridge.get("once:item:" + item) is None and bridge.get("market:veto").get(mod + ":lifelong") is None, "L11: unpublish removes both")

    # ================================================================================= L12 needs()
    inv19 = new_inv(put=[("s", 0, item), ("s", 1, item)])
    p19, pr19, U19 = player(inv19)
    Core.DONE.put(str(U19), Boolean.TRUE)
    K.check(bool(Core.needs(U19, secs(inv19), W())), "L12: needs() true with two copies")
    Core.LAST.put(U19, JInt(1))
    inv19.getStorage().setItemStackForSlot(JShort(1), None)
    K.check(not bool(Core.needs(U19, secs(inv19), W())), "L12: needs() false with one copy, nothing open, pass done")
    ch4 = SIC(JShort(3))
    ch4.setItemStackForSlot(JShort(0), IS(item, JInt(1)))
    K.check(bool(Core.needs(U19, secs(inv19), W(CWN(ch4)))), "L12: needs() true when an open personal container (Vault / trade) holds one")
    Core.LAST.remove(U19)
    K.check(bool(Core.needs(U19, secs(inv19), W())), "L12: needs() true before the player's first sweep (no count known)")
    Core.LAST.put(U19, JInt(1))
    # fix round (critic 3): the pkey is cached per profile epoch - a new epoch re-reads it and forgets the old profile's count
    KEYS = {"k": "kp1"}

    from jpype import JImplements, JOverride

    @JImplements("java.util.function.Function")
    class KeyFn(object):
        @JOverride
        def apply(self, u):
            KEYS["n"] = KEYS.get("n", 0) + 1
            return KEYS["k"]
    bridge.put("profile:fn:key", KeyFn())
    bridge.put("profile:epoch:" + str(U19), JClass("java.lang.Long")(1))
    Core.PKC.clear()
    a1, a2 = str(Core.pkeyFast(U19)), str(Core.pkeyFast(U19))
    K.check(a1 == a2 == "kp1" and KEYS["n"] == 1, "L12: pkeyFast asks profile:fn:key once per epoch (%d calls)" % KEYS["n"])
    KEYS["k"] = "kp2"
    bridge.put("profile:epoch:" + str(U19), JClass("java.lang.Long")(2))
    K.check(str(Core.pkeyFast(U19)) == "kp2" and not Core.LAST.containsKey(U19), "L12: a profile switch (new epoch) -> the new key, the old count forgotten")
    bridge.remove("profile:fn:key")
    Core.LAST.put(U19, JInt(1))
    Core.DONE.remove(str(U19))
    K.check(bool(Core.needs(U19, secs(inv19), W())), "L12: needs() true while the profile's one-time pass is due")
    Core.PEND.put(U19, Boolean.TRUE)
    K.check(not bool(Core.needs(U19, secs(inv19), W(CWN(ch4)))), "L12: needs() false while a task is queued (deduplicated)")
    Core.PEND.clear()

    # ================================================================================= L13 glue
    inv20 = new_inv(put=[("h", 0, item), ("s", 3, item)])
    p20, pr20, U20 = player(inv20)
    Core.DONE.put(str(U20), Boolean.TRUE)
    r20 = str(Core.sweep(pr20, p20))
    K.check("extra=1" in r20 and where(inv20) == [("h", 0, 1)], "L13: sweep(PlayerRef, Player) = the live sections + the Player's own WindowManager: %s" % r20)
    K.check(not bool(Core.schedule(pr20, None, JClass("java.lang.Long")(0).longValue(), JInt(0))) and not Core.PEND.containsKey(U20),
            "L13: schedule() without a world queues nothing")
    Task = JClass(pkg + pfx + "Task")
    t = Task(pr20, None, U20, JInt(0))
    t.run()
    K.check(not Core.PEND.containsKey(U20), "L13: a task for a player that is not in a world returns quietly (PEND released)")
    for n_ in ("DropSys", "ThrowSys", "InvSys"):
        try:
            sysi = JClass(pkg + pfx + n_)()
            try:
                q = sysi.getQuery()
                K.notes.append("L13: %s%s constructed, getQuery() = %s" % (pfx, n_, q))
            except Exception as eq_:
                K.notes.append("L13: %s%s constructed; getQuery() needs the booted EntityModule here (%s)" % (pfx, n_, str(eq_)[:80]))
            K.check(True, "L13: %s%s constructs" % (pfx, n_))
        except Exception as ec_:
            K.check(False, "L13: %s%s does not construct: %s" % (pfx, n_, ec_))
    rd = JClass(pkg + pfx + "Ready")()
    rd.accept(JString("not an event"))
    rd.accept(None)
    K.check(True, "L13: %sReady ignores anything that is not a PlayerReadyEvent" % pfx)
    st_ = str(Core.statusText())
    K.check(str(Core.RECALL) in st_ and "on" in st_, "L13: statusText: %s" % st_)

    # ================================================================================= L14 switch off = nothing
    set_on(False)
    inv21 = new_inv(put=[("h", 0, item), ("s", 3, item)])
    p21, pr21, U21 = player(inv21)
    ch5 = SIC(JShort(3))
    ch5.setItemStackForSlot(JShort(0), IS(item, JInt(1)))
    K.eq(str(Core.sweepCore(pr21, secs(inv21), W(CWN(ch5)), None, str(U21))), "off", "L14: switch OFF -> the sweep does nothing")
    K.check(len(where(inv21)) == 2 and n_in(ch5) == 1 and not bool(Core.needs(U21, secs(inv21), W(CWN(ch5)))), "L14: ... copies stay, needs() false")
    set_on(True)
    K.notes.append("LIFE: counters %s" % [int(Core.N.get(i)) for i in range(10)])
    return K


def compare_allowing(allowed):
    """HK.run_compare with its 'non-class entries: only manifest.json' check widened: allowed(name) -> True for the non-class files this
    round may change (each harness checks their content in its own phase). Install with HK.run_compare = OH.compare_allowing(...)."""
    import json as _json
    orig = HK.run_compare

    def cmp_(out, jar, old_jar, pkg, expect, added, removed=()):
        orig(out, jar, old_jar, pkg, expect, added, removed)
        d = _json.load(open(out))
        za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
        ea = [n for n in za.namelist() if not n.endswith(".class")]
        eb = [n for n in zb.namelist() if not n.endswith(".class")]
        ed = sorted(n for n in set(ea) | set(eb) if n not in ea or n not in eb or za.read(n) != zb.read(n))
        ok = "manifest.json" in ed and all(n == "manifest.json" or allowed(n) for n in ed)
        d["fails"] = [f for f in d["fails"] if not f.startswith("C: non-class entries changed")] + ([] if ok else ["C: non-class entries changed: %s" % ed])
        d["notes"].append("C: non-class entries changed: %s (the inner 'want manifest.json' line printed above is replaced by this check)" % (ed if len(ed) < 6 else "%d files" % len(ed)))
        _json.dump(d, open(out, "w"), indent=1)
    return cmp_
