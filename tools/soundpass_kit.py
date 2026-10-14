"""soundpass_kit - shared bare-JVM stand-ins for the Sound pass round 1 harnesses (research/Sound-Pass-Plan.md; SkyyQuests 0.3.1,
SkyyExploration 0.2.9, SkyyBank 0.1.12, SkyyIslands 0.5.9, SkyyPets 0.2.6, SkyyMenu 0.3.24 /soundtest). Used inside a harness_kit child
JVM that has javassist on its class path (HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar, ...])).

  Stage(unsafe=None)        sets everything up once per child JVM:
    .ids                    {sound event id: index} = EVERY Server/Audio/SoundEvents/**/<id>.json of the cached Assets.zip (read only),
                            installed into the engine's own SoundEvent asset store (an IndexedLookupTableAssetMap, the indices 1..n), so
                            SoundEvent.getAssetMap().getIndex(id) answers exactly what the live server's map holds for "is it there"
    .player(name, uuid)     a stand-in PlayerRef (holder set = isValid) whose packet handler is a REAL GamePacketHandler (allocated) with
                            capture ChannelConnections: every packet the ENGINE writes for it (PacketHandler.write -> ChannelConnection)
                            lands in .sent - nothing is mocked between SoundUtil and the "network"
    .universe()             a stand-in Universe.instance whose playersByUuid / players hold the players made so far (Universe.getPlayer)
    .sounds(name=None)      [(player name, sound id, category name, "2d" | "3d")] of every PlaySoundEvent2D / 3D packet sent so far
    .clear()                forget the captured packets
    .accessor(refs)         a ComponentAccessor proxy for SoundUtil.playSoundEvent3d: its player spatial resource collects the given
                            (Ref, PlayerRef) pairs (EntityModule.get() stands in when the bare JVM has none)
  bad_id                    an id that is NOT a sound event (the check= hooks must refuse it)
"""
import os, zipfile

import skyybuild as B

ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
BAD_ID = "SFX_Skyy_No_Such_Sound"


def sound_ids():
    z = zipfile.ZipFile(ASSETS)
    return sorted(set(os.path.basename(n)[:-5] for n in z.namelist() if n.startswith("Server/Audio/SoundEvents/") and n.endswith(".json")))


class Stage(object):
    def __init__(self):
        from jpype import JClass, JArray, JImplements, JOverride, JObject, JString, JInt
        self.J = JClass
        uf = JClass("java.lang.Class").forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
        uf.setAccessible(True)
        self.us = uf.get(None)
        US = self.us
        # ---------------- the SoundEvent asset store: every id of Assets.zip, indices 1..n (0 = the engine's "no sound")
        SEV = JClass("com.hypixel.hytale.server.core.asset.type.soundevent.config.SoundEvent")
        AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
        ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
        jp = JClass("javassist.ClassPool")(True)
        jp.appendClassPath(B.SERVER_JAR)
        try:
            FKC = JClass("java.lang.Class").forName("com.hypixel.hytale.assetstore.SkyySoundTestStore", True, AS.class_.getClassLoader())
        except Exception:
            fk = jp.makeClass("com.hypixel.hytale.assetstore.SkyySoundTestStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
            fk.addConstructor(JClass("javassist.CtNewConstructor").make(
                "public SkyySoundTestStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fk))
            FKC = fk.toClass(AS.class_)

        def fld(c, n):
            k = c
            while k is not None:
                try:
                    f = k.getDeclaredField(n)
                    f.setAccessible(True)
                    return f
                except Exception:
                    k = k.getSuperclass()
            raise KeyError(n)
        self.fld = fld

        @JImplements("java.util.function.IntFunction")
        class Arr(object):
            @JOverride
            def apply(self, n):
                return JClass("java.lang.reflect.Array").newInstance(SEV.class_, int(n))
        self._arr = Arr()
        m = ILT(self._arr)
        am = fld(JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap").class_, "assetMap").get(m)
        kti = fld(ILT.class_, "keyToIndex").get(m)
        self.ids = {}
        for i, k in enumerate(sound_ids()):
            am.put(k, US.allocateInstance(SEV.class_))
            kti.put(JObject(JString(k), JClass("java.lang.Object")), JInt(i + 1))
            self.ids[k] = i + 1
        # SoundUtil.playSoundEvent3d asks getAsset(index): the index -> asset array the real map keeps
        try:
            arrf = fld(ILT.class_, "array")
            arr = JClass("java.lang.reflect.Array").newInstance(SEV.class_, len(self.ids) + 1)
            for k, i in self.ids.items():
                arr[i] = am.get(k)
            arrf.set(m, arr)
        except KeyError:
            pass
        self.byidx = dict((v, k) for k, v in self.ids.items())
        st = US.allocateInstance(FKC)
        fld(AS.class_, "tClass").set(st, SEV.class_)
        fld(AS.class_, "assetMap").set(st, m)
        fld(SEV.class_, "ASSET_STORE").set(None, st)
        JClass("com.hypixel.hytale.assetstore.AssetRegistry")
        try:
            fld(JClass("com.hypixel.hytale.assetstore.AssetRegistry").class_, "storeMap").get(None).put(SEV.class_, st)
        except Exception:
            pass
        assert SEV.getAssetMap().getIndex("SFX_Coins_Land") == self.ids["SFX_Coins_Land"], "the stand-in sound store answers"
        assert SEV.getAssetMap().getIndex(BAD_ID) == -2147483648, "a missing id answers Integer.MIN_VALUE"
        # ---------------- players on REAL GamePacketHandler objects, capture connections (the SkyyEssentials 0.1.9 harness pattern)
        self.sent = []
        sent = self.sent
        Integer, Boolean = JClass("java.lang.Integer"), JClass("java.lang.Boolean")

        @JImplements("java.lang.reflect.InvocationHandler")
        class Conn(object):
            def __init__(self, name):
                self.name = name

            @JOverride
            def invoke(self, proxy, method, args):
                n = str(method.getName())
                if n in ("write", "writeAndFlush"):
                    a = args[0]
                    if a is not None and str(a.getClass().getName()).startswith("["):
                        for x in a:
                            sent.append((self.name, x))
                    else:
                        sent.append((self.name, a))
                    return None
                if n == "hashCode":
                    return Integer(id(self) & 0xffff)
                if n == "equals":
                    return Boolean(False)
                if n == "toString":
                    return "capture:" + self.name
                if n in ("isActive", "isWritable"):
                    return Boolean(True)
                return None
        self._Conn = Conn
        self.PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
        self.GPH = JClass("com.hypixel.hytale.server.core.io.handlers.game.GamePacketHandler")
        self.PH = JClass("com.hypixel.hytale.server.core.io.PacketHandler")
        self.CC = JClass("com.hypixel.hytale.protocol.io.ChannelConnection")
        self.NC = JClass("com.hypixel.hytale.protocol.NetworkChannel")
        self.players = {}
        self.conns = []

    def player(self, name, uid):
        J, US, fld = self.J, self.us, self.fld
        from jpype import JArray
        p = US.allocateInstance(self.PRc.class_)
        fld(self.PRc.class_, "uuid").set(p, J("java.util.UUID").fromString(uid))
        fld(self.PRc.class_, "username").set(p, name)
        fld(self.PRc.class_, "holder").set(p, US.allocateInstance(J("com.hypixel.hytale.component.Holder").class_))
        h = US.allocateInstance(self.GPH.class_)
        k = self.GPH.class_
        done = False
        while k is not None and not done:
            for f in k.getDeclaredFields():
                if f.getType() == self.PRc.class_:
                    f.setAccessible(True)
                    f.set(h, p)
                    done = True
                    break
            k = k.getSuperclass()
        cn = self._Conn(name)
        self.conns.append(cn)
        prox = J("java.lang.reflect.Proxy").newProxyInstance(J("java.lang.ClassLoader").getSystemClassLoader(),
                                                             JArray(J("java.lang.Class"))([self.CC.class_]), cn)
        nch = max(int(x.getValue()) for x in self.NC.values()) + 1
        arr = JArray(self.CC)(nch)
        for i in range(nch):
            arr[i] = prox
        fld(self.PH.class_, "channels").set(h, arr)
        fld(self.PRc.class_, "packetHandler").set(p, h)
        self.players[name] = p
        return p

    def universe(self):
        J, US, fld = self.J, self.us, self.fld
        Uni = J("com.hypixel.hytale.server.core.universe.Universe")
        uni = US.allocateInstance(Uni.class_)
        byu = J("java.util.concurrent.ConcurrentHashMap")()
        pl = J("java.util.concurrent.CopyOnWriteArrayList")()
        for p in self.players.values():
            byu.put(p.getUuid(), p)
            pl.add(p)
        fld(Uni.class_, "playersByUuid").set(uni, byu)
        fld(Uni.class_, "players").set(uni, pl)
        fld(Uni.class_, "instance").set(None, uni)
        self.uni = uni
        return uni

    def packet(self, pk):
        """the packet itself: a CachedPacket (PacketHandler.write caches) is decoded with its own class's toObject"""
        J = self.J
        if str(pk.getClass().getName()) != "com.hypixel.hytale.protocol.CachedPacket":
            return pk
        n = int(pk.getCachedSize())
        seg = J("java.lang.foreign.Arena").ofAuto().allocate(n + 16)
        pk.serialize(seg, 0)
        return pk.getPacketType().getMethod("toObject", J("java.lang.foreign.MemorySegment").class_).invoke(None, seg)

    def packets(self, name=None):
        return [(who, self.packet(pk)) for who, pk in list(self.sent) if name is None or who == name]

    def sounds(self, name=None):
        out = []
        for who, pk in self.packets(name):
            cn = str(pk.getClass().getSimpleName())
            if cn not in ("PlaySoundEvent2D", "PlaySoundEvent3D"):
                continue
            idx = int(self.fld(pk.getClass(), "soundEventIndex").get(pk))
            cat = self.fld(pk.getClass(), "category").get(pk)
            out.append((who, self.byidx.get(idx, "#%d" % idx), str(cat.name()) if cat is not None else None, "2d" if cn.endswith("2D") else "3d"))
        return out

    def chats(self, name=None):
        out = []
        for who, pk in self.packets(name):
            if str(pk.getClass().getSimpleName()) != "ServerMessage":
                continue
            try:
                m = self.fld(pk.getClass(), "message").get(pk)
                out.append((who, str(self.fld(m.getClass(), "rawText").get(m))))
            except Exception as e:
                out.append((who, "?%s" % e))
        return out

    def clear(self):
        del self.sent[:]

    def accessor(self, pairs):
        """a ComponentAccessor for SoundUtil.playSoundEvent3d: the player spatial resource collects every (Ref, PlayerRef) of pairs,
        getComponent(ref, PlayerRef type) answers that PlayerRef. EntityModule.get() stands in (allocated) when the JVM has none."""
        from jpype import JImplements, JOverride, JArray
        J, US, fld = self.J, self.us, self.fld
        EM = J("com.hypixel.hytale.server.core.modules.entity.EntityModule")
        em = EM.get()
        if em is None:
            em = US.allocateInstance(EM.class_)
            for f in EM.class_.getDeclaredFields():
                if str(f.getType().getName()) == str(EM.class_.getName()) and J("java.lang.reflect.Modifier").isStatic(f.getModifiers()):
                    f.setAccessible(True)
                    f.set(None, em)
        if em.getPlayerSpatialResourceType() is None:
            fld(EM.class_, "playerSpatialResourceType").set(em, US.allocateInstance(J("com.hypixel.hytale.component.ResourceType").class_))
        rlist = list(pairs)
        Proxy, CL = J("java.lang.reflect.Proxy"), J("java.lang.ClassLoader").getSystemClassLoader()
        Integer, Boolean = J("java.lang.Integer"), J("java.lang.Boolean")

        @JImplements("java.lang.reflect.InvocationHandler")
        class SSH(object):
            @JOverride
            def invoke(self, proxy, method, args):
                n = str(method.getName())
                if n == "collect":
                    lst = args[len(args) - 1]
                    for r, _p in rlist:
                        lst.add(r)
                    return None
                if n == "size":
                    return Integer(len(rlist))
                if n == "hashCode":
                    return Integer(7)
                if n == "equals":
                    return Boolean(False)
                if n == "toString":
                    return "spatial-standin"
                return None

        @JImplements("java.lang.reflect.InvocationHandler")
        class AH(object):
            @JOverride
            def invoke(self, proxy, method, args):
                n = str(method.getName())
                if n == "getResource":
                    return sr
                if n == "getComponent":
                    for r, p in rlist:
                        if r.equals(args[0]):
                            return p
                    return None
                if n == "hashCode":
                    return Integer(9)
                if n == "equals":
                    return Boolean(False)
                if n == "toString":
                    return "accessor-standin"
                return None
        SSI = J("com.hypixel.hytale.component.spatial.SpatialStructure")
        ss = Proxy.newProxyInstance(CL, JArray(J("java.lang.Class"))([SSI.class_]), SSH())
        SR = J("com.hypixel.hytale.component.spatial.SpatialResource")
        sr = US.allocateInstance(SR.class_)
        k = SR.class_
        while k is not None:
            for f in k.getDeclaredFields():
                if str(f.getType().getName()) == "com.hypixel.hytale.component.spatial.SpatialStructure":
                    f.setAccessible(True)
                    f.set(sr, ss)
            k = k.getSuperclass()
        ACI = J("com.hypixel.hytale.component.ComponentAccessor")
        self._keep = (SSH, AH, ss)
        return Proxy.newProxyInstance(CL, JArray(J("java.lang.Class"))([ACI.class_]), AH())

    def ref(self):
        """a valid stand-in Ref (a fresh allocated Ref; Ref.isValid reads its index)"""
        J, US, fld = self.J, self.us, self.fld
        R = J("com.hypixel.hytale.component.Ref")
        r = US.allocateInstance(R.class_)
        try:
            fld(R.class_, "index").setInt(r, 0)
        except Exception:
            pass
        return r


def kit_rows(rows_cls):
    """{row key: [the 11 published strings]} from the mod's own CfgRows.header() (what SkyyMenu's Server Setup reads)"""
    h = rows_cls.header()
    return dict((str(r[0]), [str(x) for x in list(r)[:11]]) for r in h[7])


def kit_check(fn_cls, rows_cls, key, value):
    """the kit's own check= hook call for row `key` (CfgFn.checkHook - what a Server Setup edit runs before it saves)"""
    keys = [str(r[0]) for r in rows_cls.header()[7]]
    r = fn_cls.checkHook(keys.index(key), key, value)
    return None if r is None else str(r)


def sound_rows(K, rows, master, per, prefix=""):
    """the Server Setup rows of one mod's sounds: master bool on, per sound a bool row (true) + an id row (text, the default id, live,
    max 120); per = [(on row key, id row key, default id)]"""
    r = rows.get(master)
    K.check(r is not None and r[3] == "bool" and r[4] == "true" and "live" in r[9], "%sROW %s = a live bool, default on: %s" % (prefix, master, r))
    for on, idk, did in per:
        a, b = rows.get(on), rows.get(idk)
        K.check(a is not None and a[3] == "bool" and a[4] == "true" and "live" in a[9], "%sROW %s = a live bool, default on: %s" % (prefix, on, a))
        K.check(b is not None and b[3] == "text" and b[4] == did and b[6] == "120" and "live" in b[9] and "/soundtest" in b[10],
                "%sROW %s = a live text row, default %s, max 120, help names /soundtest: %s" % (prefix, idk, did, b))
