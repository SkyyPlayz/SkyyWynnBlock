"""Bare-JVM check for SkyySacks 0.7.14 (THE NEW BAG LOOK - tools/sacks_0_7_14_patch.py; Skyy 2026-10-08 "as drawn, violet. start the bag
round"). 0.7.14 is art wiring only: every class is 0.7.13's apart from the version text (section I proves it), so the 0.7.13 proofs (K, L)
run again unchanged; the new sections prove the art (G) and - today's SkyyArmory lesson - that the ENGINE'S OWN ASSET VALIDATORS accept
every new or changed asset (V), in a second JVM that loads the jar into the real asset stores the way the server does.

    python SkyySacks/test_skyysacks_0.7.14.py [--jar <0.7.14 jar>] [--old <0.7.13 jar>] [--live <Skyy_SkyySacks folder>] [--dir <scratch>] [--keep]

The parent copies the live data folder (read only; default: the "HUD mod" world's mods/Skyy_SkyySacks) into the scratch folder (default
tools/dev/scratch/bags01/sacks-run, deleted at the end unless --keep) and starts two children (the game's JRE, -XX:-UsePerfData,
java.io.tmpdir / TEMP / TMP in the scratch folder):
 child 1 (-Xverify:all; HytaleServer.jar + the 0.7.14 jar + tools/javassist.jar), the 0.7.13 harness stand-ins:
  A  every 0.7.14 class loads and verifies (-Xverify:all)
  G  THE ART: tools/art/make_bags.py run fresh in memory -> every art file in the jar is byte-identical to it (the build ships exactly
     the generator's output), and to models-local/art/bags (the sheet Skyy approved) when that folder exists; the jar ships exactly the
     sack files (none of the Accessory Bag's); each of the 21 bag JSONs carries exactly its manifest look (model per rarity, texture + icon
     per type x rarity, IconProperties, Animation, PlayerAnimationsId SkyySack, Particles + FirstPersonParticles on node Portal, the SwapTo
     lift); every file a look names ships; icons 64 x 64 RGBA, textures the manifest size; every sack model has the Portal node; the open
     animation only animates nodes every sack model has; the set's lift key names both shipped lift animations; P0: no Parallel with fewer
     than 2 entries anywhere in the jar; no art path is a vanilla Assets.zip path
  I  class compare 0.7.13 -> 0.7.14: the same classes, each byte-identical or the version text only; the jar files: the generated art
     added, exactly the 21 bag JSONs + manifest.json changed - each bag JSON = 0.7.13's + ONLY the look keys and Interactions.SwapTo
  X  engine-access audit on the jar bytes (a protected engine member only from its subclass) - 0 refused; control refused
  K  the 0.7.13 bag take bridge, executed again (unchanged code - regression)
  L  start twice on a scratch COPY of the live data: no file changes; a real take on the copy changes exactly the taken line
 child 2 (V - the ENGINE ASSET VALIDATORS; HytaleServer.jar + tools/javassist.jar): the real asset stores (AssetRegistryLoader.init + the
  Interaction / RootInteraction / UnarmedInteractions stores and every interaction Type codec InteractionModule.setup registers, read from
  its bytecode), the CommonAssetRegistry filled with every Common/ file of Assets.zip + the jar, the vanilla pack loaded store by store in
  dependency order (AssetStore.loadAssetsFromDirectory - the server's AssetRegistryLoader.loadAssets0 path, which runs the codec
  validators: CommonAssetValidator, ArraySizeRangeValidator, asset-reference validators), the bag pages registered like the plugin's
  setup() does (OpenCustomUIInteraction.PAGE_CODEC), then THE JAR as its own pack:
  V  no store fails, not one SEVERE or WARNING line for the pack ("Failed to validate asset", "Array size is invalid", missing asset,
     unknown key); the 21 items, the SkyySack set (with SackLift), the particle system + spawner and every SwapTo root are in the stores
     with the jar's values; every SwapTo root compiles (RootInteraction.build) to one Simple step playing SackLift, no placeholder;
     toPacket() of every item / the set / the particles works (what the server sends a joining client)
  NEGATIVE CONTROLS (each a one-file pack in scratch): a one-entry Parallel MUST be refused ("Array size is invalid" - the SkyyArmory 0.1.9
     failure) and an item whose Model file does not exist MUST be refused - proving the validators really run; the other controls (bogus
     PlayerAnimationsId / particle SystemId / Animation path / ItemAnimationId / set animation path / spawner texture / an unknown key)
     print whether the engine catches them, so the report can say which references the offline check proves.
Exit code 1 on any failure. Live data is only READ (copied). Nothing is deployed.
"""
import os, sys, re, shutil, subprocess, zipfile, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD = "0.7.14", "0.7.13"
PKG = "com.skyy.sacks."
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE_DEFAULT = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyySacks")
MARK = ".skyysacks-0.7.14-harness"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH_ROOT = os.path.realpath(os.path.join(TOOLS, "dev", "scratch"))
SCRATCH = os.path.realpath(os.path.abspath(arg("--dir", os.path.join(SCRATCH_ROOT, "bags01", "sacks-run"))))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLDJAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyySacks-%s.jar" % OLD)))
LIVE = os.path.abspath(arg("--live", LIVE_DEFAULT))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)
    return bool(cond)


# ============================================================================================================== child
def run():
    import jpype
    import skyybuild as B
    from jpype import JClass, JArray, JShort, JString, JInt, JImplements, JOverride
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, JAR, B.JAVASSIST], convertStrings=True)
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()

    # ---------------- A. load + verify
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(JAR).namelist() if n.endswith(".class")]
    for n in names:
        try:
            Cls.forName(n, True, loader)
            OKS[0] += 1
        except Exception as e:
            FAILS.append("load " + n + ": " + str(e))
            print("LOAD FAIL", n, e)
    print("A. loaded + verified %d classes of %s (-Xverify:all)" % (len(names), VERSION))
    if FAILS:
        return

    # ---------------- G. the art (pure Python; gen_checks below)
    zn = zipfile.ZipFile(JAR)
    G = gen_checks(zn)

    # ---------------- I. class compare 0.7.13 -> 0.7.14 (art wiring only: no class changes beyond the version text)
    zo = zipfile.ZipFile(OLDJAR)
    co = dict((n, zo.read(n)) for n in zo.namelist() if n.endswith(".class"))
    cn = dict((n, zn.read(n)) for n in zn.namelist() if n.endswith(".class"))
    check(sorted(cn) == sorted(co), "I: the same %d classes as %s" % (len(cn), OLD))
    same, vers, other = [], [], []
    ob, nb = OLD.encode(), VERSION.encode()
    for n in sorted(co):
        if n not in cn:
            continue
        if co[n] == cn[n]:
            same.append(n)
        elif len(ob) == len(nb) and co[n].replace(ob, nb) == cn[n]:
            vers.append(n.split("/")[-1][:-6])
        else:
            other.append(n.split("/")[-1][:-6])
    check(not other and vers, "I: every class byte-identical or the version text only (others: %s)" % other)
    ao = dict((n, zo.read(n)) for n in zo.namelist() if not n.endswith(".class"))
    an = dict((n, zn.read(n)) for n in zn.namelist() if not n.endswith(".class"))
    added = sorted(set(an) - set(ao))
    removed = sorted(set(ao) - set(an))
    changed = sorted(n for n in set(ao) & set(an) if ao[n] != an[n])
    bag_json = sorted("Server/Item/Items/Utility/%s.json" % i for i in BAG_IDS)
    check(not removed and changed == sorted(bag_json + ["manifest.json"]), "I: changed = the 21 bag JSONs + manifest.json, none removed: %s / %s"
          % ([c for c in changed if c not in bag_json][:4], removed[:4]))
    check(added == G["ship"], "I: added = exactly the generated sack art (%d files): %s" % (len(G["ship"]), sorted(set(added) ^ set(G["ship"]))[:4]))
    only_look = []
    for p in bag_json:
        o_, n_ = json.loads(ao[p]), json.loads(an[p])
        sw = n_["Interactions"].pop("SwapTo", None)
        for k in LOOKK:
            o_.pop(k, None)
            n_.pop(k, None)
        if o_ != n_ or sw is None:
            only_look.append(p)
    check(not only_look, "I: each bag JSON = 0.7.13's + only the look keys and Interactions.SwapTo: %s" % only_look[:3])
    mo_, mn_ = json.loads(ao["manifest.json"]), json.loads(an["manifest.json"])
    check(mn_.pop("Version") == VERSION and mo_.pop("Version") == OLD and mo_.pop("Name") == OLD + " SkyySacks" and mn_.pop("Name") == VERSION + " SkyySacks"
          and mo_ == mn_, "I: manifest.json differs only in Version / Name")
    print("I. class compare %s -> %s: %d identical, %d version-text only (%s); files: +%d generated art, 21 bag JSONs (look + SwapTo only), manifest"
          % (OLD, VERSION, len(same), len(vers), ", ".join(vers), len(added)))

    # ---------------- X. engine-access audit (the SkyyBazaar harness rule)
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    jp.appendClassPath(JAR)
    Mod = JClass("javassist.Modifier")
    CPo = JClass("javassist.bytecode.ConstPool")
    CF, DI, BI = JClass("javassist.bytecode.ClassFile"), JClass("java.io.DataInputStream"), JClass("java.io.ByteArrayInputStream")
    AOPS = {0xb2, 0xb3, 0xb4, 0xb5, 0xb6, 0xb7, 0xb8, 0xb9, 0xba, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5, 0x12, 0x13}
    pkgof = lambda n: n.rsplit(".", 1)[0] if "." in n else ""

    def elem(n):
        n2 = n.replace("/", ".").lstrip("[")
        if n2.startswith("L") and n2.endswith(";"):
            return n2[1:-1]
        return None if len(n2) == 1 and n.startswith("[") else n2

    def audit(items):
        refused, used, seen = [], set(), 0
        for D, cf in items:
            dn = str(D.getName())
            for mi in cf.getMethods():
                ca_ = mi.getCodeAttribute()
                if ca_ is None:
                    continue
                cp, it = mi.getConstPool(), ca_.iterator()
                while it.hasNext():
                    pos = it.next()
                    op = it.byteAt(pos)
                    if op not in AOPS:
                        continue
                    if op == 0xba:
                        refused.append("invokedynamic in " + dn)
                        continue
                    idx = it.byteAt(pos + 1) if op == 0x12 else it.u16bitAt(pos + 1)
                    tag = cp.getTag(idx)
                    if op in (0x12, 0x13) and tag != CPo.CONST_Class:
                        continue
                    if op in (0x12, 0x13, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5):
                        cname, member = str(cp.getClassInfo(idx)), None
                    elif op in (0xb2, 0xb3, 0xb4, 0xb5):
                        cname, member = str(cp.getFieldrefClassName(idx)), ("field", str(cp.getFieldrefName(idx)), str(cp.getFieldrefType(idx)))
                    elif tag == CPo.CONST_InterfaceMethodref:
                        cname, member = str(cp.getInterfaceMethodrefClassName(idx)), ("method", str(cp.getInterfaceMethodrefName(idx)), str(cp.getInterfaceMethodrefType(idx)))
                    else:
                        cname, member = str(cp.getMethodrefClassName(idx)), ("method", str(cp.getMethodrefName(idx)), str(cp.getMethodrefType(idx)))
                    seen += 1
                    try:
                        en = elem(cname)
                        if en is not None and pkgof(en) != pkgof(dn) and not Mod.isPublic(jp.get(en).getModifiers()):
                            refused.append("%s: class %s not public" % (dn, en))
                        if member is None:
                            continue
                        kind, name, desc = member
                        Cc = jp.get("java.lang.Object" if cname.startswith("[") else cname)
                        x = Cc.getField(name, desc) if kind == "field" else (Cc.getConstructor(desc) if name == "<init>" else Cc.getMethod(name, desc))
                        md, decl = x.getModifiers(), x.getDeclaringClass()
                        dcn = str(decl.getName())
                        if Mod.isPublic(md) or (pkgof(dcn) == pkgof(dn) and not Mod.isPrivate(md)):
                            continue
                        ok = (dcn == dn) if Mod.isPrivate(md) else (bool(D.subclassOf(decl)) if Mod.isProtected(md) else False)
                        if ok:
                            used.add("%s.%s" % (dcn.rsplit(".", 1)[-1], name))
                        else:
                            refused.append("%s: %s %s.%s%s" % (dn, Mod.toString(md), dcn, name, desc))
                    except Exception as e:
                        refused.append("%s: %s %s does not resolve: %s" % (dn, cname, member, e))
        return refused, used, seen
    items = [(jp.get(n[:-6].replace("/", ".")), CF(DI(BI(zn.read(n))))) for n in zn.namelist() if n.endswith(".class")]
    refused, used, seen = audit(items)
    check(not refused and seen > 5000, "X: access audit: %d references, refused %s" % (seen, refused[:5]))
    ctl = jp.makeClass(PKG + "AuditControl")
    ctl.addMethod(JClass("javassist.CtNewMethod").make(
        "public static void bad(com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage p) { p.close(); }", ctl))
    r2, _u2, _s2 = audit([(ctl, CF(DI(BI(ctl.toBytecode()))))])
    check(len(r2) == 1 and "close" in r2[0], "X: access audit control refused: %s" % r2)
    print("X. access audit: %d references, 0 refused; non-public used from their subclass: %s; control refused"
          % (seen, ", ".join(sorted(used))))

    # ---------------- stand-ins (the 0.7.12 harness pattern)
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyTestFakeStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fake.addConstructor(JClass("javassist.CtNewConstructor").make(
        "public SkyyTestFakeStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
    store = us.allocateInstance(fake.toClass(AS.class_))
    fm = AS.class_.getDeclaredField("assetMap")
    fm.setAccessible(True)
    DAMN = "com.hypixel.hytale.assetstore.map.DefaultAssetMap"
    kmap = jp.makeClass("com.hypixel.hytale.assetstore.map.SkyyTestKnownMap", jp.get(DAMN))
    kmap.addField(JClass("javassist.CtField").make("public static final java.util.HashSet KNOWN = new java.util.HashSet();", kmap))
    kmap.addConstructor(JClass("javassist.CtNewConstructor").make("public SkyyTestKnownMap() { super(); }", kmap))
    kmap.addMethod(JClass("javassist.CtNewMethod").make(
        "public com.hypixel.hytale.assetstore.JsonAsset getAsset(Object key) { if (key != null && KNOWN.contains(key)) "
        "return com.hypixel.hytale.server.core.asset.type.item.config.Item.UNKNOWN; return super.getAsset(key); }", kmap))
    KMap = JClass(kmap.toClass(JClass(DAMN).class_))
    for kid_ in ("Ingredient_Tree_Sap", "Wood_Oak_Trunk", "Ore_Copper", "Food_Bread", "Ingredient_Stick"):
        KMap.KNOWN.add(kid_)
    fm.set(store, KMap())
    fi_ = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item").class_.getDeclaredField("ASSET_STORE")
    fi_.setAccessible(True)
    fi_.set(None, store)
    INVN = "com.hypixel.hytale.server.core.inventory.Inventory"
    ICN = "com.hypixel.hytale.server.core.inventory.container.ItemContainer"
    CtF, CtM, CtC = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    tinv = jp.makeClass("com.hypixel.hytale.server.core.inventory.SkyyTestInv", jp.get(INVN))
    for f in ("s", "h", "b"):
        tinv.addField(CtF.make("public %s %s;" % (ICN, f), tinv))
    tinv.addConstructor(CtC.make("public SkyyTestInv(%s s, %s h, %s b) { super(); this.s = s; this.h = h; this.b = b; }" % (ICN, ICN, ICN), tinv))
    for m, f in (("getStorage", "s"), ("getHotbar", "h"), ("getBackpack", "b")):
        tinv.addMethod(CtM.make("public %s %s() { return this.%s; }" % (ICN, m, f), tinv))
    TInv = JClass(tinv.toClass(JClass(INVN).class_))
    # the harness's player lookup + a taker thread, both plain Java (no Python callbacks on other threads)
    tpl = jp.makeClass(PKG + "SkyyTestPlayers")
    tpl.addInterface(jp.get("java.util.function.Function"))
    tpl.addField(CtF.make("public static volatile Object P;", tpl))
    tpl.addField(CtF.make("public static volatile int CALLS;", tpl))
    tpl.addConstructor(CtC.make("public SkyyTestPlayers() { }", tpl))
    tpl.addMethod(CtM.make("public Object apply(Object o) { CALLS++; return P; }", tpl))
    TPlayers = JClass(tpl.toClass(JClass(PKG + "SackBridge").class_))
    ttk = jp.makeClass(PKG + "SkyyTestTaker")
    ttk.addInterface(jp.get("java.lang.Runnable"))
    for fdecl in ("public java.util.function.Function f;", "public java.util.UUID u;", "public String id;", "public int loops;",
                  "public long got;", "public long min = 0L;", "public java.util.concurrent.CountDownLatch go;"):
        ttk.addField(CtF.make(fdecl, ttk))
    ttk.addConstructor(CtC.make("public SkyyTestTaker() { }", ttk))
    ttk.addMethod(CtM.make("""public void run() {
  try { this.go.await(); } catch (Throwable t) { }
  for (int i = 0; i < this.loops; i++) {
    long r = ((Long) this.f.apply(new Object[] { this.u, this.id, Long.valueOf(1L) })).longValue();
    this.got += r;
    long now = com.skyy.sacks.SackPool.get(com.skyy.sacks.SackPool.pkey(this.u), this.id);
    if (now < this.min) this.min = now;
  }
}""", ttk))
    TTaker = JClass(ttk.toClass(JClass(PKG + "SackBridge").class_))

    J = lambda n: JClass(PKG + n)
    Pool, Bridge, Fn, Mirror, CLog, Defs = J("SackPool"), J("SackBridge"), J("SackFn"), J("BagMirror"), J("CraftLog"), J("SackDefs")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    UUID, Paths, Long_ = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Long")
    CHM, System, Thread, Latch = JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.lang.System"), JClass("java.lang.Thread"), \
        JClass("java.util.concurrent.CountDownLatch")
    ObjArr = JArray(JClass("java.lang.Object"))
    bridge = CHM()
    System.getProperties().put("skyy.bridge", bridge)
    U1 = UUID.fromString("00000000-0000-0000-0000-00000000cafe")

    def jfield(cls, name):
        c = cls
        while c is not None:
            try:
                f = c.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                c = c.getSuperclass()
        raise KeyError(name)
    inv_field = jfield(PLA.class_, "inventory")

    def player(storage=(), hotbar=(), backpack=()):
        s, h, b = SIC(JShort(36)), SIC(JShort(9)), SIC(JShort(9))
        for cont, its in ((s, storage), (h, hotbar), (b, backpack)):
            for (iid, q) in its:
                tx = cont.addItemStack(IS(iid, q))
                assert tx.succeeded(), (iid, q)
        p = us.allocateInstance(PLA.class_)
        inv_field.set(p, TInv(s, h, b))
        return p

    def fresh_pools(d):
        for m in (Pool.POOLS, Pool.DIRTY, Pool.BADPOOL, Pool.KEPT, Pool.KEPTKEY, Pool.SEENQ, Pool.SEENEPOCH, Pool.SEENKEY, Pool.CHANGEDAT,
                  Pool.UNKNOWN, Mirror.MIRRORS, Bridge.OWED, Bridge.LASTKEY):
            m.clear()
        Pool.DIR = Paths.get(d)
        os.makedirs(d, exist_ok=True)

    def write_pool(d, key, vals):
        with open(os.path.join(d, key + ".properties"), "w", encoding="latin-1") as f:
            f.write("#SkyySacks pool\n" + "".join("%s=%d\n" % (k, v) for k, v in vals.items()))

    def read_pool(d, key):
        out = {}
        pth = os.path.join(d, key + ".properties")
        if not os.path.exists(pth):
            return None
        for l in open(pth, encoding="latin-1").read().splitlines():
            if l and not l.startswith("#") and "=" in l:
                k, v = l.split("=", 1)
                out[k.strip()] = int(v)
        return out

    def pc(k):
        return dict((str(e.getKey()), int(e.getValue().longValue())) for e in Pool.pool(k).entrySet())

    def publish():
        for i, key in enumerate(("sacks:fn:count", "sacks:fn:take", "sacks:fn:put", "sacks:fn:all", "sacks:fn:commit")):
            bridge.put(key, Fn(i))

    def call(key, *a):
        f = bridge.get(key)
        if key == "sacks:fn:all":
            return f.apply(a[0])
        arr = ObjArr(len(a))
        for i, v in enumerate(a):
            arr[i] = Long_(v) if isinstance(v, int) else v
        r = f.apply(arr)
        return None if r is None else int(r.longValue())

    def amap(u):
        r = bridge.get("sacks:fn:all").apply(u)
        return None if r is None else dict((str(e.getKey()), int(e.getValue().longValue())) for e in r.entrySet())

    SAP, OAK, COP, BREAD = "Ingredient_Tree_Sap", "Wood_Oak_Trunk", "Ore_Copper", "Food_Bread"
    FOR_S, MIN_S, OMNI = "Skyy_Sack_Foraging_Small", "Skyy_Sack_Mining_Small", "Skyy_Sack_Omni"
    check(str(Defs.homeOf(SAP)) == "Foraging" and str(Defs.homeOf(OAK)) == "Foraging" and str(Defs.homeOf(COP)) == "Mining"
          and Defs.homeOf(FOR_S) is None and Defs.homeOf(OMNI) is None, "K: homeOf: sap / oak Foraging, copper Mining, a bag id none")

    # ---------------- K. the bridge, executed
    kd = os.path.join(SCRATCH, "k", "pools")
    fresh_pools(kd)
    k1 = str(U1)
    write_pool(kd, k1, {SAP: 70, OAK: 12, COP: 50, BREAD: 3})
    publish()
    Bridge.PLAYERS = TPlayers()
    # no bag carried
    TPlayers.P = player(storage=[(SAP, 5)])
    check(call("sacks:fn:count", U1, SAP) == 0 and call("sacks:fn:take", U1, SAP, 10) == 0 and amap(U1) == {} and pc(k1)[SAP] == 70,
          "K: no bag carried -> count 0, take 0, all {} , pool untouched")
    # a Foraging bag in the hotbar
    TPlayers.P = player(storage=[(SAP, 5)], hotbar=[(FOR_S, 1)])
    check(call("sacks:fn:count", U1, SAP) == 70 and call("sacks:fn:count", U1, OAK) == 12 and call("sacks:fn:count", U1, COP) == 0,
          "K: a Foraging bag -> count sap 70, oak 12; copper (Mining) 0")
    check(amap(U1) == {SAP: 70, OAK: 12}, "K: all() = only the carried bag type's items: %s" % amap(U1))
    CLog.PENDING.clear()
    CLog.FILE = Paths.get(os.path.join(SCRATCH, "k", "crafts.log"))
    Pool.DIRTY.clear()
    r = call("sacks:fn:take", U1, SAP, 30)
    Pool.flushDirty()
    CLog.drain()
    check(r == 30 and pc(k1)[SAP] == 40 and read_pool(kd, k1).get(SAP) == 40 and read_pool(kd, k1).get(OAK) == 12,
          "K: take 30 of 70 -> 30, pool 40, the saved file says 40 (oak 12 kept): %s %s" % (r, read_pool(kd, k1)))
    pend = open(os.path.join(SCRATCH, "k", "crafts.log"), encoding="utf8").read().splitlines()
    check(len(pend) == 1 and pend[0].endswith(k1 + " BAG-TAKE " + SAP + " 30 (sacks:fn:take)"), "K: one crafts.log line (queued, written by the saver): %s" % pend)
    r = call("sacks:fn:take", U1, SAP, 100)
    check(r == 40 and SAP not in pc(k1) and call("sacks:fn:count", U1, SAP) == 0, "K: take 100 of 40 -> 40 (partial), the entry is gone")
    check(call("sacks:fn:take", U1, SAP, 5) == 0 and SAP not in pc(k1), "K: take from an empty entry -> 0, never below zero")
    check(call("sacks:fn:count", U1, FOR_S) == 0 and call("sacks:fn:take", U1, FOR_S, 1) == 0 and call("sacks:fn:put", U1, FOR_S, 1) == 0,
          "K: a Magic Bag id -> 0 everywhere (bags are never in a bag, never sold)")
    # put: only what takes removed (70 taken in the window)
    r = call("sacks:fn:put", U1, SAP, 100)
    check(r == 70 and pc(k1)[SAP] == 70, "K: put 100 after taking 70 -> 70 back (owed ledger), pool 70")
    check(call("sacks:fn:put", U1, SAP, 5) == 0 and pc(k1)[SAP] == 70, "K: a second put -> 0: put can never create items")
    check(call("sacks:fn:put", U1, OAK, 5) == 0 and pc(k1)[OAK] == 12, "K: put without a take -> 0")
    call("sacks:fn:take", U1, SAP, 10)
    o = Bridge.OWED.get(k1 + "|" + SAP)
    o[1] = o[1] - 61000
    check(call("sacks:fn:put", U1, SAP, 10) == 0 and pc(k1)[SAP] == 60 and Bridge.OWED.get(k1 + "|" + SAP) is None,
          "K: put more than 60 s after the take -> 0 (and the stale entry is dropped)")
    # REVIEW FIX 1: a PAID take is committed -> a later put returns nothing (before the fix: put within 60 s re-added paid items)
    check(call("sacks:fn:take", U1, SAP, 30) == 30 and pc(k1)[SAP] == 30, "FIX1: take 30 of 60 -> pool 30")
    check(call("sacks:fn:commit", U1, SAP, 30) == 30 and Bridge.OWED.get(k1 + "|" + SAP) is None, "FIX1: commit 30 (paid) clears the ledger")
    check(call("sacks:fn:put", U1, SAP, 30) == 0 and pc(k1)[SAP] == 30, "FIX1: put 30 after a committed (paid) take -> 0, pool stays 30 (no free items)")
    check(call("sacks:fn:take", U1, SAP, 20) == 20 and call("sacks:fn:commit", U1, SAP, 15) == 15 and call("sacks:fn:put", U1, SAP, 20) == 5
          and pc(k1)[SAP] == 15, "FIX1: take 20, commit 15 -> put returns only the unpaid 5 (pool 15)")
    check(call("sacks:fn:commit", U1, SAP, 5) == 0 and call("sacks:fn:commit", U1, OAK, 5) == 0, "FIX1: commit with nothing owed -> 0")
    # REVIEW FIX 3: a pause that starts between the take and the put no longer strands the items - put returns into the debited pool
    check(call("sacks:fn:take", U1, SAP, 10) == 10 and pc(k1)[SAP] == 5, "FIX3: take 10 -> pool 5")
    bridge.put("profile:busy:" + k1, JString("x"))
    check(call("sacks:fn:count", U1, SAP) == -1, "FIX3: profile:busy set mid-sale -> moves paused")
    check(call("sacks:fn:put", U1, SAP, 10) == 10 and pc(k1)[SAP] == 15, "FIX3: put while busy -> 10 back into the pool they left (15)")
    bridge.remove("profile:busy:" + k1)
    check(call("sacks:fn:take", U1, SAP, 4) == 4 and pc(k1)[SAP] == 11, "FIX3: take 4 -> 11")
    Pool.CLOSED = True
    check(call("sacks:fn:put", U1, SAP, 4) == 0 and pc(k1)[SAP] == 11, "FIX3: the shutdown latch still refuses a put (pools being flushed)")
    Pool.CLOSED = False
    check(call("sacks:fn:put", U1, SAP, 4) == 4 and pc(k1)[SAP] == 15, "FIX3: after the latch opens the owed 4 still go back (15)")
    Pool.pool(k1).put(JString(SAP), Long_(60))   # back to the 60 the next checks expect, saved like a bag change
    Pool.DIRTY.put(JString(k1), JClass("java.lang.Boolean").TRUE)
    Pool.flushDirty()
    Bridge.OWED.clear()
    # the Omni reaches every type
    TPlayers.P = player(backpack=[(OMNI, 1)])
    check(call("sacks:fn:count", U1, COP) == 50 and call("sacks:fn:count", U1, SAP) == 60 and amap(U1) == {SAP: 60, OAK: 12, COP: 50, BREAD: 3},
          "K: the Omni bag reaches every type (all = the whole pool): %s" % amap(U1))
    # bad arguments
    f0, f1, f3 = bridge.get("sacks:fn:count"), bridge.get("sacks:fn:take"), bridge.get("sacks:fn:all")
    bad1 = ObjArr(2)
    bad1[0], bad1[1] = JString("not a uuid"), JString(SAP)
    bad2 = ObjArr(3)
    bad2[0], bad2[1], bad2[2] = U1, JString(SAP), JString("10")
    check(int(f0.apply(JString("x")).longValue()) == -1 and int(f1.apply(JString("x")).longValue()) == 0 and int(f0.apply(bad1).longValue()) == -1
          and int(f1.apply(bad2).longValue()) == 0 and f3.apply(JString("x")) is None and int(f1.apply(None).longValue()) == 0 and pc(k1)[SAP] == 60,
          "K: bad arguments answer -1 / 0 / null and move nothing")
    neg = call("sacks:fn:take", U1, SAP, -5)
    check(neg == 0 and pc(k1)[SAP] == 60, "K: a negative / zero amount takes nothing")
    # paused states
    TPlayers.P = player(hotbar=[(FOR_S, 1)])
    Pool.CLOSED = True
    check(call("sacks:fn:count", U1, SAP) == -1 and call("sacks:fn:take", U1, SAP, 5) == 0 and amap(U1) is None and pc(k1)[SAP] == 60,
          "K: the shutdown latch -> count -1, take 0, all null")
    Pool.CLOSED = False
    bridge.put("profile:busy:" + k1, JString("x"))
    check(call("sacks:fn:count", U1, SAP) == -1 and call("sacks:fn:take", U1, SAP, 5) == 0 and pc(k1)[SAP] == 60, "K: profile:busy -> paused")
    bridge.remove("profile:busy:" + k1)

    @JImplements("java.util.function.Function")
    class KeyFn:
        key = None

        @JOverride
        def apply(self, u):
            return JString(KeyFn.key) if KeyFn.key else JString(str(u))
    kfn = KeyFn()
    bridge.put("profile:fn:key", kfn)
    check(call("sacks:fn:count", U1, SAP) == -1 and call("sacks:fn:take", U1, SAP, 5) == 0, "K: SkyyProfiles installed but no epoch -> paused")
    bridge.put("profile:epoch:" + k1, Long_(1))
    KeyFn.key = k1 + "-p3"
    write_pool(kd, k1 + "-p3", {SAP: 9})
    check(call("sacks:fn:count", U1, SAP) == -1 and call("sacks:fn:take", U1, SAP, 1) == 0, "K: the switch to profile 3 settles first (paused)")
    Pool.CHANGEDAT.put(U1, Long_(int(System.currentTimeMillis()) - 7000))
    check(call("sacks:fn:count", U1, SAP) == 9, "K: profile 3 active (profile:fn:key -> <uuid>-p3) -> its own pool: 9")
    check(call("sacks:fn:take", U1, SAP, 4) == 4 and pc(k1 + "-p3")[SAP] == 5 and pc(k1)[SAP] == 60, "K: a take on profile 3 debits only p3 (5 left; profile 1 still 60)")
    Pool.flushDirty()
    check(read_pool(kd, k1 + "-p3") == {SAP: 5} and read_pool(kd, k1)[SAP] == 60, "K: only the p3 file changed on disk")
    KeyFn.key = k1 + "-p5"
    bridge.put("profile:epoch:" + k1, Long_(2))
    check(call("sacks:fn:count", U1, SAP) == -1 and call("sacks:fn:take", U1, SAP, 1) == 0, "K: right after a profile switch (settle window) -> paused")
    Pool.CHANGEDAT.put(U1, Long_(int(System.currentTimeMillis()) - 7000))
    check(call("sacks:fn:count", U1, SAP) == 0, "K: settled on profile 5 (no pool file) -> 0")
    check(call("sacks:fn:put", U1, SAP, 4) == 4 and pc(k1 + "-p3")[SAP] == 9 and pc(k1)[SAP] == 60 and call("sacks:fn:count", U1, SAP) == 0,
          "FIX3: a refund after a switch p3 -> p5 goes back into p3 (the pool the take debited: 9), never into p1 / p5")
    bridge.remove("profile:fn:key")
    bridge.remove("profile:epoch:" + k1)
    check(call("sacks:fn:count", U1, SAP) == -1, "K: SkyyProfiles gone -> the key changes back to profile 1 and settles first")
    Pool.CHANGEDAT.put(U1, Long_(int(System.currentTimeMillis()) - 7000))
    check(call("sacks:fn:count", U1, SAP) == 60, "K: SkyyProfiles gone -> profile 1 again (60)")
    # unreadable pool file (a folder where the file should be)
    kbad = "00000000-0000-0000-0000-0000000000bd"
    Ubad = UUID.fromString(kbad)
    os.makedirs(os.path.join(kd, kbad + ".properties"), exist_ok=True)
    check(call("sacks:fn:count", Ubad, SAP) == -1 and call("sacks:fn:take", Ubad, SAP, 1) == 0 and amap(Ubad) is None, "K: an unreadable pool file -> paused")
    # no player found for the uuid (the game: offline, or called off the player's world thread) -> paused, nothing moved
    TPlayers.P = None
    check(call("sacks:fn:count", U1, SAP) == -1 and call("sacks:fn:take", U1, SAP, 1) == 0 and amap(U1) is None and pc(k1)[SAP] == 60,
          "K: no player on this thread -> count -1, take 0, all null")
    Bridge.PLAYERS = None   # the game path: Universe.get() is not running in a bare JVM -> caught -> no player
    check(call("sacks:fn:count", U1, SAP) == -1 and call("sacks:fn:take", U1, SAP, 1) == 0 and pc(k1)[SAP] == 60,
          "K: the real lookup (Universe.getPlayer) without a universe -> refused, nothing moved")
    Bridge.PLAYERS = TPlayers()
    # the live-mirror rule: a bench used 20 of the 50 the mirror offered (not booked yet) -> the take books it first
    fresh_pools(kd)
    write_pool(kd, k1, {SAP: 50})
    TPlayers.P = player(hotbar=[(FOR_S, 1)])
    m = Mirror.of(k1)
    tx = m.cont.addItemStack(IS(SAP, 50))
    m.slotIds[0] = SAP
    m.slotQty[0] = 50
    m.cont.removeItemStackFromSlot(JShort(0), JInt(20))          # the bench took 20 through the guard (unbooked until a sync)
    r = call("sacks:fn:take", U1, SAP, 50)
    left = m.cont.getItemStack(JShort(0))
    check(r == 30 and SAP not in pc(k1) and int(m.slotQty[0]) == 0 and (left is None or left.isEmpty()),
          "K: live-mirror rule: the bench's 20 are booked first, the take gets 30 (never the used ones), the mirror is trimmed to 0: %s %s" % (r, pc(k1)))
    write_pool(kd, k1, {SAP: 50})
    Pool.POOLS.clear()
    Mirror.MIRRORS.clear()
    m2 = Mirror.of(k1)
    m2.cont.addItemStack(IS(SAP, 40))
    m2.slotIds[0] = SAP
    m2.slotQty[0] = 40
    m2.cont.removeItemStackFromSlot(JShort(0), JInt(15))
    check(call("sacks:fn:count", U1, SAP) == 35 and pc(k1)[SAP] == 35, "K: count books the bench use too (50 - 15 = 35)")
    r = call("sacks:fn:take", U1, SAP, 10)
    left = m2.cont.getItemStack(JShort(0))
    check(r == 10 and pc(k1)[SAP] == 25 and int(m2.slotQty[0]) == 25 and left is not None and int(left.getQuantity()) == 25,
          "K: a take below the mirror amount trims the mirror to the pool (25), books nothing twice")
    Mirror.MIRRORS.clear()
    # two threads, 1,000 takes of 1 each, from a pool of 1,500
    fresh_pools(kd)
    write_pool(kd, k1, {SAP: 1500})
    TPlayers.P = player(hotbar=[(FOR_S, 1)])
    latch = Latch(1)
    ts, ws = [], []
    for _i in range(2):
        w = TTaker()
        w.f, w.u, w.id, w.loops, w.go, w.min = bridge.get("sacks:fn:take"), U1, SAP, 1000, latch, 1 << 40
        ws.append(w)
        t = Thread(w)
        t.start()
        ts.append(t)
    latch.countDown()
    for t in ts:
        t.join(120000)
    got = [int(w.got) for w in ws]
    check(sum(got) == 1500 and SAP not in pc(k1) and all(int(w.min) >= 0 for w in ws) and min(got) > 0,
          "K: two threads x 1,000 takes of 1 from 1,500 -> exactly 1,500 taken (%s), pool 0, never negative" % got)
    o = Bridge.OWED.get(k1 + "|" + SAP)
    check(o is not None and int(o[0]) == 1500, "K: the owed ledger holds the 1,500 the takes removed")
    Pool.flushDirty()
    check(read_pool(kd, k1) == {}, "K: the saved pool file is empty after the threads: %s" % read_pool(kd, k1))
    print("K. the bridge executed: count / all / take / put, partial takes, the bag gates, the Omni, a bag id, bad arguments, 6 paused states, "
          "per profile, the live-mirror rule (bench use booked first, mirror trimmed), 2 threads x 1,000 takes conserve 1,500")

    # ---------------- L. start twice on a copy of the live data, then a real take on the copy
    live_s = os.path.join(SCRATCH, "live")
    Cfg = J("SackCfg")

    def snap(d):
        out_ = {}
        for root, _ds, fs in os.walk(d):
            for f in fs:
                pth = os.path.join(root, f)
                out_[os.path.relpath(pth, d)] = open(pth, "rb").read()
        return out_

    def start_sacks(d):
        Cfg.FILE = Paths.get(os.path.join(d, "config.properties"))
        Cfg.MTIME = -1
        Cfg.reload()
        N = J("SackNotice")
        N.SEEN.clear()
        N.BROKEN = False
        N.DIRTY = False
        N.FILE = Paths.get(os.path.join(d, "notices.properties"))
        N.load()
        RF = J("RefillPref")
        RF.MODES.clear()
        RF.BROKEN = False
        RF.DIRTY = False
        RF.FILE = Paths.get(os.path.join(d, "refill.properties"))
        RF.load()
        pd = os.path.join(d, "pools")
        fresh_pools(pd)
        n = 0
        for f in sorted(os.listdir(pd)) if os.path.isdir(pd) else []:
            if f.endswith(".properties"):
                Pool.pool(f[:-11])
                n += 1
        publish()                                     # 0.7.13: the four bridge puts (setup)
        J("WbTab").start()
        J("BenchLink").start()
        J("BenchLink").stop()
        Pool.flushDirty()
        N.save()
        RF.save()
        return n

    if not os.path.isdir(live_s):
        print("note: no live SkyySacks data copy - L skipped")
    else:
        ds = os.path.join(SCRATCH, "l-run")
        shutil.copytree(live_s, ds)
        before = snap(ds)
        n1 = start_sacks(ds)
        n2 = start_sacks(ds)
        after = snap(ds)
        ch = sorted(k_ for k_ in set(before) | set(after) if before.get(k_) != after.get(k_))
        check(not ch and n1 == n2, "L: started twice on the copy of the live data (%d pools): no file changed %s" % (n1, ch[:4]))
        pd = os.path.join(ds, "pools")
        keys = sorted(f[:-11] for f in os.listdir(pd) if f.endswith(".properties"))
        target = None
        for kk in keys:
            vals = read_pool(pd, kk)
            if "-p" not in kk and vals.get(SAP, 0) >= 10:
                target = kk
                break
        if target is None:
            print("note: no profile-1 pool with Tree Sap in the live copy - L take skipped")
        else:
            Ut = UUID.fromString(target)
            TPlayers.P = player(hotbar=[(FOR_S, 1)])
            Bridge.PLAYERS = TPlayers()
            b0 = dict((kk, read_pool(pd, kk)) for kk in keys)
            r = call("sacks:fn:take", Ut, SAP, 7)
            Pool.flushDirty()
            a0 = dict((kk, read_pool(pd, kk)) for kk in keys)
            changed = sorted(kk for kk in keys if a0[kk] != b0[kk])
            diffk = sorted(i for i in set(a0[target]) | set(b0[target]) if a0[target].get(i) != b0[target].get(i))
            check(r == 7 and changed == [target] and diffk == [SAP] and a0[target][SAP] == b0[target][SAP] - 7,
                  "L: a take of 7 Tree Sap on the copy changes exactly that line of exactly that pool file (%s: %d -> %d)"
                  % (target[:8], b0[target][SAP], a0[target].get(SAP, 0)))
            p3 = target + "-p3"
            if p3 in keys and read_pool(pd, p3).get(SAP, 0) >= 3:
                bridge.put("profile:fn:key", kfn)
                KeyFn.key = p3
                bridge.put("profile:epoch:" + target, Long_(3))
                b1 = dict((kk, read_pool(pd, kk)) for kk in keys)
                r = call("sacks:fn:take", Ut, SAP, 3)
                Pool.flushDirty()
                a1 = dict((kk, read_pool(pd, kk)) for kk in keys)
                changed = sorted(kk for kk in keys if a1[kk] != b1[kk])
                check(r == 3 and changed == [p3] and a1[p3][SAP] == b1[p3][SAP] - 3, "L: profile 3 active -> only the -p3 pool file changes (%s)" % changed)
                bridge.remove("profile:fn:key")
        print("L. start twice on the live copy (%d pools): no file changed; a real take on the copy changes exactly the taken line of that profile's pool file" % n1)


# ============================================================================================================== G + V (0.7.14)
BAG_CATS = ("Mining", "Foraging", "Farming", "Combat", "Smithing")
BAG_TIERS = ("Small", "Medium", "Rare", "Large")
BAG_IDS = ["Skyy_Sack_%s_%s" % (c, t) for c in BAG_CATS for t in BAG_TIERS] + ["Skyy_Sack_Omni"]
LOOKK = ("Model", "Texture", "Icon", "IconProperties", "Animation", "PlayerAnimationsId", "Particles", "FirstPersonParticles")
SHIP_PREFIX = ("Common/Items/SkyySacks/", "Common/Icons/ItemsGenerated/SkyySacks_Bag_", "Common/Characters/Animations/Items/SkyySacks/",
               "Server/Particles/SkyySacks/")
SET_PATH = "Server/Item/Animations/SkyySack.json"
ASSETS_ZIP = os.path.join(os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming"), "Hytale", "install", "release", "package", "game",
                          "latest", "Assets.zip")


def make_bags_in_memory():
    """tools/art/make_bags.py run exactly like the build runs it: write() into a dict, clean_old() a no-op (nothing written to disk)"""
    import importlib.util
    spec = importlib.util.spec_from_file_location("make_bags_harness", os.path.join(TOOLS, "art", "make_bags.py"))
    mb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mb)
    got = {}

    def _w(rel, data):
        got[rel] = bytes(data)
        return rel
    mb.write = _w
    mb.clean_old = lambda: None
    mb.main()
    return got


def _png_info(b):
    import struct
    if b[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    w, h = struct.unpack(">II", b[16:24])
    return w, h, b[24], b[25]


def _node_names(nodes, out):
    for x in nodes or []:
        out.add(x.get("name"))
        _node_names(x.get("children"), out)
    return out


def gen_checks(zn):
    gen = make_bags_in_memory()
    man = json.loads(gen["manifest.json"].decode("utf-8"))
    names = set(zn.namelist())
    ship = sorted(n for n in names if n.startswith(SHIP_PREFIX) or n == SET_PATH)
    want = sorted(r for r in gen if r.startswith(SHIP_PREFIX) or r == SET_PATH)
    check(ship == want and len(ship) == 53, "G: the jar ships exactly the generator's %d sack art files (got %d): %s"
          % (len(want), len(ship), sorted(set(ship) ^ set(want))[:4]))
    bad = [n for n in ship if zn.read(n) != gen.get(n)]
    check(not bad, "G: every shipped art file is byte-identical to a fresh tools/art/make_bags.py run: %s" % bad[:4])
    check(not any("SkyyAccessories" in n for n in names if n.startswith("Common/")), "G: none of the Accessory Bag's files")
    ml = os.path.join(ROOT, "models-local", "art", "bags")
    if os.path.isdir(ml):
        dif = [r for r in ship if not os.path.isfile(os.path.join(ml, *r.split("/"))) or open(os.path.join(ml, *r.split("/")), "rb").read() != gen[r]]
        check(not dif, "G: the shipped art = models-local/art/bags (the sheet Skyy approved), byte for byte: %s" % dif[:4])
        print("G. the jar's %d art files = a fresh make_bags run = models-local/art/bags" % len(ship))
    else:
        print("note: models-local/art/bags is not here - the shipped art was compared with a fresh generator run only")
    items = dict((i, json.loads(zn.read("Server/Item/Items/Utility/%s.json" % i))) for i in BAG_IDS)
    mapped, wrong = [], []
    part = man["particles"]["item_fields"]
    for e in man["sacks"]:
        for it in e["items"]:
            n = items.get(it["item"])
            mapped.append(it["item"])
            if n is None:
                wrong.append(it["item"] + " missing")
                continue
            exp = {"Model": e["model_path"][7:], "Texture": it["texture_path"][7:], "Icon": it["icon_path"][7:], "IconProperties": e["icon_properties"],
                   "Animation": e["animation_path"][7:], "PlayerAnimationsId": e["player_animations_id"],
                   "Particles": part["Particles"], "FirstPersonParticles": part["FirstPersonParticles"]}
            for k, v in exp.items():
                if n.get(k) != v:
                    wrong.append("%s %s" % (it["item"], k))
            if n["Interactions"].get("SwapTo") != {"Interactions": [{"Type": "Simple", "RunTime": 0.5, "Effects": {"ItemAnimationId": man["animations"]["lift_key"]}}]}:
                wrong.append(it["item"] + " SwapTo")
            if n["Interactions"]["Secondary"]["Interactions"][0]["Type"] != "OpenCustomUI":
                wrong.append(it["item"] + " Secondary")
            for k in ("Model", "Texture", "Icon", "Animation"):
                if ("Common/" + n[k]) not in names:
                    wrong.append("%s %s file not shipped" % (it["item"], k))
            ti = _png_info(zn.read("Common/" + n["Texture"]))
            ii = _png_info(zn.read("Common/" + n["Icon"]))
            if ti is None or [ti[0], ti[1]] != e["texture_size"] or ii is None or ii[:4] != (64, 64, 8, 6):
                wrong.append("%s png %s %s" % (it["item"], ti, ii))
    check(sorted(mapped) == sorted(BAG_IDS) and not wrong, "G: the 21 bag JSONs carry exactly their manifest look + the SwapTo lift: %s" % wrong[:5])
    check(len(set(items[i]["Texture"] for i in BAG_IDS)) == 21 and len(set(items[i]["Icon"] for i in BAG_IDS)) == 21
          and len(set(items[i]["Model"] for i in BAG_IDS)) == 5, "G: 21 textures, 21 icons, 5 models (one per rarity)")
    oa = json.loads(zn.read("Common/Items/SkyySacks/SkyySacks_Bag_Open.blockyanim"))
    mods = sorted(set(items[i]["Model"] for i in BAG_IDS))
    miss = []
    for m in mods:
        nn = _node_names(json.loads(zn.read("Common/" + m))["nodes"], set())
        if "Portal" not in nn:
            miss.append(m + " has no Portal node")
        miss += ["%s lacks %s" % (m, k) for k in oa["nodeAnimations"] if k not in nn]
    check(oa["duration"] == 1200 and not miss, "G: every sack model has the Portal node (the particle target) and every node the open animation moves: %s" % miss[:4])
    st = json.loads(zn.read(SET_PATH))
    lk = man["animations"]["lift_key"]
    a3, af = st["Animations"][lk]["ThirdPerson"], st["Animations"][lk]["FirstPerson"]
    check(st["Parent"] == "Block" and ("Common/" + a3) in names and ("Common/" + af) in names and st["Animations"][lk]["Looping"] is False,
          "G: the SkyySack set = Parent Block + %s (both lift animations shipped, not looping)" % lk)
    import zipfile as _zf
    with _zf.ZipFile(ASSETS_ZIP) as az:
        van = set(az.namelist())
        pnodes = _node_names(json.loads(az.read("Common/Characters/Player.blockymodel").decode("utf-8-sig"))["nodes"], set())
        for vp in ("Common/Characters/Animations/Items/Main_Handed/Item/Idle.blockyanim", "Common/Characters/Animations/Items/Dual_Handed/Block/Idle.blockyanim",
                   "Common/Characters/Animations/Items/Main_Handed/Item/Idle_FPS.blockyanim", "Common/Characters/Animations/Items/Dual_Handed/Block/Idle_FPS.blockyanim"):
            pnodes |= set(json.loads(az.read(vp).decode("utf-8-sig"))["nodeAnimations"])   # + the cape nodes the vanilla idles move
    lift_extra = []
    for ap in (a3, af):
        la = json.loads(zn.read("Common/" + ap))
        lift_extra += [k for k in la["nodeAnimations"] if k not in pnodes]
    check(pnodes and not lift_extra, "G: the lift animations only move nodes of the vanilla player model or nodes the vanilla Item / Block idles move: %s" % lift_extra[:4])
    psys = json.loads(zn.read("Server/Particles/SkyySacks/SkyySack_PortalSparkle.particlesystem"))
    pspn = json.loads(zn.read("Server/Particles/SkyySacks/SkyySack_PortalSparkle.particlespawner"))
    check([x["SpawnerId"] for x in psys["Spawners"]] == ["SkyySack_PortalSparkle"] and ("Common/" + pspn["Particle"]["Texture"]) in van
          and pspn["MaxConcurrentParticles"] <= 12, "G: the sparkle system names our spawner; its texture is the vanilla %s" % pspn["Particle"]["Texture"])
    clash = sorted(n for n in ship if n in van)
    check(not clash, "G: no art path replaces a vanilla Assets.zip file: %s" % clash[:3])
    shortp, nj = [], [0]

    def walk(p, x):
        if isinstance(x, dict):
            if x.get("Type") == "Parallel" and len(x.get("Interactions") or []) < 2:
                shortp.append(p)
            for v in x.values():
                walk(p, v)
        elif isinstance(x, list):
            for v in x:
                walk(p, v)
    for n in names:
        if n.startswith("Server/") and n.endswith((".json", ".particlesystem", ".particlespawner")):
            walk(n, json.loads(zn.read(n)))
            nj[0] += 1
    check(not shortp and nj[0] > 25, "G (P0): no Parallel with fewer than 2 entries in the jar's %d server JSON files: %s" % (nj[0], shortp[:3]))
    print("G. art: %d generated files shipped (= the generator), 21 looks from the manifest, 5 models with Portal, set Block + %s, P0 clean (%d files)"
          % (len(ship), lk, nj[0]))
    return {"ship": ship, "man": man}


# -------------------------------------------------------------------------------------------------------------- V (child 2)
def run_v():
    import time, hashlib
    import jpype
    import skyybuild as B
    from jpype import JClass, JArray, JString, JImplements, JOverride
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jpype.startJVM(jvm, "-XX:-UsePerfData", "-Xmx6g", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, B.JAVASSIST], convertStrings=True)
    Options = JClass("com.hypixel.hytale.server.core.Options")
    Options.parse(JArray(JString)(["--universe", os.path.join(SCRATCH, "v-universe")]))
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)

    def jf(c, n):
        k = c.class_ if hasattr(c, "class_") else c
        while k is not None:
            try:
                f = k.getDeclaredField(n)
                f.setAccessible(True)
                return f
            except Exception:
                k = k.getSuperclass()
        raise KeyError(n)
    # a bare server + universe (the stores ask HytaleServer.get() / Universe.get())
    HS = JClass("com.hypixel.hytale.server.core.HytaleServer")
    hs = us.allocateInstance(HS.class_)
    jf(HS, "eventBus").set(hs, JClass("com.hypixel.hytale.event.EventBus")(False))
    jf(HS, "shutdown").set(hs, JClass("java.util.concurrent.atomic.AtomicReference")())
    jf(HS, "instance").set(None, hs)
    CHM = JClass("java.util.concurrent.ConcurrentHashMap")
    UNI = JClass("com.hypixel.hytale.server.core.universe.Universe")
    uni = us.allocateInstance(UNI.class_)
    pbu, wmap = CHM(), CHM()
    jf(UNI, "playersByUuid").set(uni, pbu)
    jf(UNI, "players").set(uni, JClass("java.util.Collections").unmodifiableCollection(pbu.values()))
    jf(UNI, "worlds").set(uni, wmap)
    jf(UNI, "worldsByUuid").set(uni, CHM())
    jf(UNI, "unmodifiableWorlds").set(uni, JClass("java.util.Collections").unmodifiableMap(wmap))
    jf(UNI, "instance").set(None, uni)
    HLB = JClass("com.hypixel.hytale.logger.backend.HytaleLoggerBackend")
    CAPLOG = JClass("java.util.concurrent.CopyOnWriteArrayList")()
    HLB.subscribe(CAPLOG)

    def records(start=0):
        out = []
        for r in list(CAPLOG)[start:]:
            try:
                msg = str(r.getMessage())
                ps = r.getParameters()
                if ps is not None and len(ps) > 0:
                    try:
                        msg = str(JClass("java.lang.String").format(msg, ps))
                    except Exception:
                        msg = msg + " " + " ".join(str(p) for p in ps)
                th = r.getThrown()
                if th is not None:
                    msg += " | " + str(th)[:300]
                out.append((str(r.getLevel()), msg))
            except Exception as e:
                out.append(("?", str(e)))
        return out
    JClass("com.hypixel.hytale.server.core.asset.AssetRegistryLoader").init()
    AR = JClass("com.hypixel.hytale.assetstore.AssetRegistry")
    HAS = JClass("com.hypixel.hytale.server.core.asset.HytaleAssetStore")
    ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
    DAMc = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
    ARR = JClass("java.lang.reflect.Array")

    @JImplements("java.util.function.Function")
    class GetId:
        @JOverride
        def apply(self, o): return o.getId()

    @JImplements("java.util.function.IntFunction")
    class ArrOf:
        def __init__(self, c): self.c = c

        @JOverride
        def apply(self, n): return ARR.newInstance(self.c.class_, n)

    @JImplements("java.util.function.Function")
    class NoRep:
        @JOverride
        def apply(self, k): return None

    @JImplements("java.util.function.Predicate")
    class IsUnknown:
        @JOverride
        def test(self, o): return bool(o.isUnknown())
    PI = "com.hypixel.hytale.server.core.modules.interaction.interaction.config."
    INTc, ROOTc = JClass(PI + "Interaction"), JClass(PI + "RootInteraction")
    UIc = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.UnarmedInteractions")

    def reg_ilt(c, path, codec, unknown=False):
        b_ = HAS.builder(c.class_, ILT(ArrOf(c))).setPath(path).setCodec(codec).setKeyFunction(GetId()).setReplaceOnRemove(NoRep())
        if unknown:
            b_ = b_.setIsUnknown(IsUnknown())
        AR.register(b_.build())
    # the stores InteractionModule registers in the game (the SkyyArmory 0.1.10 harness pattern)
    reg_ilt(INTc, "Item/Interactions", INTc.CODEC, True)
    reg_ilt(ROOTc, "Item/RootInteractions", ROOTc.CODEC)
    AR.register(HAS.builder(UIc.class_, DAMc()).setPath("Item/Unarmed/Interactions").setCodec(UIc.CODEC).setKeyFunction(GetId()).build())
    CPj = JClass("javassist.ClassPool")(True)
    CPj.appendClassPath(B.SERVER_JAR)
    CPool = JClass("javassist.bytecode.ConstPool")
    imc = CPj.get("com.hypixel.hytale.server.core.modules.interaction.InteractionModule")
    ms_ = [x for x in imc.getDeclaredMethods() if str(x.getName()) == "setup"][0]
    cp_, it_ = ms_.getMethodInfo().getConstPool(), ms_.getMethodInfo().getCodeAttribute().iterator()
    last_s, last_c, regs = None, None, []
    while it_.hasNext():
        p_ = it_.next()
        op_ = it_.byteAt(p_)
        if op_ in (0x12, 0x13):
            idx = it_.byteAt(p_ + 1) if op_ == 0x12 else it_.u16bitAt(p_ + 1)
            t_ = cp_.getTag(idx)
            if t_ == CPool.CONST_String:
                last_s = str(cp_.getStringInfo(idx))
            elif t_ == CPool.CONST_Class:
                last_c = str(cp_.getClassInfo(idx))
        elif op_ == 0xb6:
            idx = it_.u16bitAt(p_ + 1)
            if str(cp_.getMethodrefClassName(idx)).endswith("AssetCodecMapCodec") and str(cp_.getMethodrefName(idx)) == "register":
                regs.append((last_s, last_c))
    for nm_, cl_ in regs:
        C_ = JClass(cl_)
        INTc.CODEC.register(nm_, C_.class_, jf(C_, "CODEC").get(None))
    PRJIc = JClass("com.hypixel.hytale.server.core.modules.projectile.interaction.ProjectileInteraction")
    INTc.CODEC.register("Projectile", PRJIc.class_, PRJIc.CODEC)
    SPCc = JClass("com.hypixel.hytale.server.core.modules.projectile.config.StandardPhysicsConfig")
    JClass("com.hypixel.hytale.server.core.modules.projectile.config.PhysicsConfig").CODEC.register("Standard", SPCc.class_, SPCc.CODEC)
    check(len(regs) >= 70 and "Simple" in [a for a, b in regs] and "Parallel" in [a for a, b in regs],
          "V: the interaction Type codecs registered from InteractionModule.setup's bytecode (%d)" % len(regs))
    # the bag pages, the way the plugin's setup() registers them (OpenCustomUIInteraction.registerSimple -> PAGE_CODEC) before assets load
    OCUc = JClass(PI + "server.OpenCustomUIInteraction")
    CPSn = PI + "server.OpenCustomUIInteraction$CustomPageSupplier"
    CPSc = JClass(CPSn)
    BCc = JClass("com.hypixel.hytale.codec.builder.BuilderCodec")

    @JImplements(CPSn)
    class PageSup:
        @JOverride
        def tryCreate(self, a, b, c, d): return None

    @JImplements("java.util.function.Supplier")
    class SupOf:
        @JOverride
        def get(self): return PageSup()
    zj = zipfile.ZipFile(JAR)
    pages = set()
    for n in zj.namelist():
        if n.startswith("Server/Item/Items/") and n.endswith(".json"):
            for x in json.loads(zj.read(n))["Interactions"]["Secondary"]["Interactions"]:
                if x.get("Type") == "OpenCustomUI":
                    pages.add(x["Page"]["Id"])
    for pid in sorted(pages):
        OCUc.PAGE_CODEC.register(pid, CPSc.class_, BCc.builder(CPSc.class_, SupOf()).build())
    # the common assets (the CommonAssetModule's job in the game): every Common/ file of Assets.zip and of the jar, at its zip path
    CAR = JClass("com.hypixel.hytale.server.core.asset.common.CommonAssetRegistry")
    FCA = JClass("com.hypixel.hytale.server.core.asset.common.asset.FileCommonAsset")
    Paths, FSs, HashMap = JClass("java.nio.file.Paths"), JClass("java.nio.file.FileSystems"), JClass("java.util.HashMap")
    ZFS = {}

    def zfs(zpath):
        if zpath not in ZFS:
            ZFS[zpath] = FSs.newFileSystem(Paths.get(zpath), HashMap())
        return ZFS[zpath]

    def add_common(pack, zpath, real):
        n = 0
        fs = zfs(zpath)
        with zipfile.ZipFile(zpath) as z:
            for nm in z.namelist():
                if nm.startswith("Common/") and not nm.endswith("/"):
                    h = hashlib.sha256(z.read(nm)).hexdigest() if real else "0" * 64
                    CAR.addCommonAsset(pack, FCA(fs.getPath("/" + nm), nm[len("Common/"):], h, None))
                    n += 1
        return n
    AP = JClass("com.hypixel.hytale.assetstore.AssetPack")
    Files, LinkOption = JClass("java.nio.file.Files"), JClass("java.nio.file.LinkOption")

    def store_order():
        stores = dict((st.getAssetClass(), st) for st in AR.getStoreMap().values())
        done, order = set(), []

        def visit(c, stack):
            if c in done or c not in stores or c in stack:
                return
            stack.add(c)
            for d in stores[c].getLoadsAfter():
                visit(d, stack)
            done.add(c)
            order.append(stores[c])
        for c in list(stores):
            visit(c, set())
        return order

    def loadpack(zpath, name, immutable):
        """AssetRegistryLoader.loadAssets0's per-store step: loadAssetsFromDirectory(pack, <root>/Server/<store path>) in dependency order"""
        n0 = len(CAPLOG)
        pack = AP(Paths.get(zpath), name, zfs(zpath).getPath("/"), zfs(zpath), immutable, None, None)
        srv = pack.getRoot().resolve("Server")
        failed = []
        for st in store_order():
            d = srv.resolve(st.getPath())
            if not Files.isDirectory(d, JArray(LinkOption)(0)):
                continue
            try:
                if st.loadAssetsFromDirectory(name, d).hasFailed():
                    failed.append(str(st.getAssetClass().getSimpleName()))
            except Exception as e:
                failed.append("%s EXC %s" % (st.getAssetClass().getSimpleName(), str(e)[:200]))
        return failed, records(n0)
    t0 = time.time()
    nv = add_common("Hytale:Hytale", ASSETS_ZIP, False)
    vfail, vrec = loadpack(ASSETS_ZIP, "Hytale:Hytale", True)
    print("V. vanilla pack loaded (%d common files, %.0f s; %d SEVERE lines from stores a bare JVM lacks codecs for - not ours)"
          % (nv, time.time() - t0, len([r for r in vrec if r[0] == "SEVERE"])))
    ITEM = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    IPA = JClass("com.hypixel.hytale.server.core.asset.type.itemanimation.config.ItemPlayerAnimations")
    PSY = JClass("com.hypixel.hytale.server.core.asset.type.particle.config.ParticleSystem")
    PSP = JClass("com.hypixel.hytale.server.core.asset.type.particle.config.ParticleSpawner")
    check(IPA.getAssetMap().getAsset("Block") is not None and ITEM.getAssetMap().getAssetMap().size() > 1000,
          "V: the vanilla Block set and the vanilla items (%d) are in the real stores" % ITEM.getAssetMap().getAssetMap().size())
    # ---- THE JAR
    pack_name = "Skyy:%s SkyySacks" % VERSION
    nc = add_common(pack_name, JAR, True)
    fail, rec = loadpack(JAR, pack_name, False)
    bad = [r for r in rec if r[0] in ("SEVERE", "WARNING")]
    for r in bad[:12]:
        print("   V:", r[0], r[1][:500].replace("\n", " / "))
    check(not fail and not bad, "V: the %s jar loads into the real stores: no failed store (%s), no SEVERE / WARNING line (%d)" % (VERSION, fail, len(bad)))
    # the stores hold what the jar says
    got_bad = []
    swap_roots = []
    for iid in BAG_IDS:
        node = json.loads(zj.read("Server/Item/Items/Utility/%s.json" % iid))
        it = ITEM.getAssetMap().getAsset(iid)
        if it is None:
            got_bad.append(iid + " not in the Item store")
            continue
        vals = {"Model": str(it.getModel()), "Texture": str(jf(ITEM, "texture").get(it)), "Icon": str(jf(ITEM, "icon").get(it)),
                "Animation": str(jf(ITEM, "animation").get(it)), "PlayerAnimationsId": str(it.getPlayerAnimationsId())}
        for k, v in vals.items():
            if v != node[k]:
                got_bad.append("%s %s %s" % (iid, k, v))
        for fld, key in (("particles", "Particles"), ("firstPersonParticles", "FirstPersonParticles")):
            arr = jf(ITEM, fld).get(it)
            if arr is None or len(arr) != 1 or str(arr[0].getSystemId()) != node[key][0]["SystemId"] or str(arr[0].getTargetNodeName()) != "Portal":
                got_bad.append("%s %s" % (iid, fld))
        inter = dict((str(e.getKey()), str(e.getValue())) for e in it.getInteractions().entrySet())
        if "SwapTo" not in inter or "Secondary" not in inter:
            got_bad.append("%s interactions %s" % (iid, inter))
        else:
            swap_roots.append(inter["SwapTo"])
        try:
            it.toPacket()
        except Exception as e:
            got_bad.append("%s toPacket %s" % (iid, str(e)[:120]))
    check(not got_bad, "V: the 21 items in the Item store carry the jar's Model / Texture / Icon / Animation / PlayerAnimationsId / Particles / "
          "FirstPersonParticles / SwapTo, toPacket() works: %s" % got_bad[:4])
    st = IPA.getAssetMap().getAsset("SkyySack")
    anims = dict((str(e.getKey()), e.getValue()) for e in st.getAnimations().entrySet()) if st is not None else {}
    check(st is not None and "SackLift" in anims and "Idle" in anims, "V: the SkyySack set is in the store with SackLift + the inherited Block keys (%d keys)" % len(anims))
    try:
        st.toPacket()
        pk = True
    except Exception as e:
        pk = str(e)[:150]
    ps, sp = PSY.getAssetMap().getAsset("SkyySack_PortalSparkle"), PSP.getAssetMap().getAsset("SkyySack_PortalSparkle")
    try:
        ps.toPacket()
        sp.toPacket()
        pk2 = True
    except Exception as e:
        pk2 = str(e)[:150]
    check(pk is True and ps is not None and sp is not None and pk2 is True, "V: the particle system + spawner are in the stores; set / particle toPacket(): %s %s" % (pk, pk2))
    # every SwapTo root compiles to one Simple step that plays SackLift (RootInteraction.build - the SkyyArmory C check)
    SMIc = JClass(PI + "none.simple.SendMessageInteraction")
    SIc = JClass(dict(regs)["Simple"])
    comp_bad = []
    for rid in swap_roots:
        r_ = ROOTc.getAssetMap().getAsset(rid)
        if r_ is None:
            comp_bad.append(rid + " not in the RootInteraction store")
            continue
        try:
            r_.build()
        except Exception as e:
            comp_bad.append("build %s: %s" % (rid, str(e)[:150]))
            continue
        ops = []
        for i_ in range(int(r_.getOperationMax())):
            inner = r_.getOperation(i_).getInnerOperation()
            if inner is not None and INTc.class_.isInstance(inner):
                ops.append(inner)
        if len(ops) != 1 or SMIc.class_.isInstance(ops[0]) or not SIc.class_.isInstance(ops[0]):
            comp_bad.append("%s ops %s" % (rid, [str(o.getClass().getSimpleName()) for o in ops]))
            continue
        eff = jf(INTc, "effects").get(ops[0])
        if eff is None or str(eff.getItemAnimationId()) != "SackLift" or abs(float(jf(INTc, "runTime").get(ops[0])) - 0.5) > 1e-6:
            comp_bad.append("%s effects %s" % (rid, eff))
    check(len(swap_roots) == 21 and not comp_bad, "V: the 21 SwapTo roots compile (RootInteraction.build) to one Simple step, RunTime 0.5, "
          "ItemAnimationId SackLift, no placeholder: %s" % comp_bad[:3])
    print("V. %s loaded into the real asset stores: 0 failed stores, 0 SEVERE / WARNING; 21 items, the SkyySack set (%d keys), the sparkle "
          "system + spawner, 21 SwapTo roots compiled; toPacket() fine" % (VERSION, len(anims)))
    # ---- NEGATIVE CONTROLS: one-file packs in scratch
    base = json.loads(zj.read("Server/Item/Items/Utility/Skyy_Sack_Mining_Small.json"))
    base.pop("Recipe", None)
    base["Interactions"] = {}

    def item_with(**kv):
        d = json.loads(json.dumps(base))
        for k, v in kv.items():
            d[k] = v
        return json.dumps(d)
    ctl = [
        ("one-entry Parallel", "Server/Item/Interactions/SkyyTestCtl/SkyyTestCtl_Parallel.json",
         json.dumps({"Type": "Simple", "RunTime": 0.1, "Next": {"Type": "Parallel", "Interactions": [{"Interactions": [{"Type": "Simple", "RunTime": 0.1}]}]}}),
         "Array size is invalid", True),
        ("Model file missing", "Server/Item/Items/SkyyTestCtl/SkyyTestCtl_Model.json", item_with(Model="Items/SkyySacks/SkyyTestCtl_NoSuch.blockymodel"),
         "SkyyTestCtl_NoSuch.blockymodel", True),
        ("PlayerAnimationsId unknown", "Server/Item/Items/SkyyTestCtl/SkyyTestCtl_Set.json", item_with(PlayerAnimationsId="SkyyTestCtl_NoSuchSet"),
         "SkyyTestCtl_NoSuchSet", False),
        ("particle SystemId unknown", "Server/Item/Items/SkyyTestCtl/SkyyTestCtl_Part.json",
         item_with(Particles=[{"SystemId": "SkyyTestCtl_NoSuchSystem", "TargetNodeName": "Portal"}]), "SkyyTestCtl_NoSuchSystem", False),
        ("Animation file missing", "Server/Item/Items/SkyyTestCtl/SkyyTestCtl_Anim.json", item_with(Animation="Items/SkyySacks/SkyyTestCtl_NoSuch.blockyanim"),
         "SkyyTestCtl_NoSuch.blockyanim", False),
        ("ItemAnimationId unknown", "Server/Item/Items/SkyyTestCtl/SkyyTestCtl_Lift.json",
         item_with(Interactions={"SwapTo": {"Interactions": [{"Type": "Simple", "RunTime": 0.5, "Effects": {"ItemAnimationId": "SkyyTestCtl_NoSuchKey"}}]}}),
         "SkyyTestCtl_NoSuchKey", False),
        ("set animation file missing", "Server/Item/Animations/SkyyTestCtl_SetFile.json",
         json.dumps({"Parent": "Block", "Animations": {"SackLift": {"ThirdPerson": "Characters/Animations/Items/SkyySacks/SkyyTestCtl_NoSuch.blockyanim"}}}),
         "SkyyTestCtl_NoSuch.blockyanim", False),
        ("spawner texture missing", "Server/Particles/SkyyTestCtl/SkyyTestCtl_Spawner.particlespawner",
         json.dumps({"Particle": {"Texture": "Particles/Textures/Basic/SkyyTestCtl_NoSuch.png"}}), "SkyyTestCtl_NoSuch.png", False),
        ("unknown item key", "Server/Item/Items/SkyyTestCtl/SkyyTestCtl_Key.json", item_with(SkyyTestCtlBogusKey=1), "SkyyTestCtlBogusKey", False),
    ]
    caught = {}
    for i, (what, path, text, needle, must) in enumerate(ctl):
        zp = os.path.join(SCRATCH, "v-ctl%d.jar" % i)
        with zipfile.ZipFile(zp, "w") as z:
            z.writestr(path, text)
        f_, r_ = loadpack(zp, "Skyy:test ctl%d" % i, False)
        hit = [r for r in r_ if r[0] in ("SEVERE", "WARNING") and needle in r[1]]
        caught[what] = ("refused (SEVERE)" if any(r[0] == "SEVERE" for r in hit) else "warned" if hit else "NOT caught") + (" + store failed" if f_ else "")
        if must:
            check(hit and any(r[0] == "SEVERE" for r in hit), "V CONTROL: %s must be refused by the engine validator: %s" % (what, caught[what]))
    print("V. negative controls (what the offline engine check catches): " + "; ".join("%s -> %s" % (k, v) for k, v in caught.items()))


def main():
    for mode, fn in (("--child", run), ("--child-v", run_v)):
        if mode in sys.argv:
            try:
                fn()
            except Exception as e:
                import traceback
                traceback.print_exc()
                FAILS.append("crash: %s" % e)
            print("%d ok, %d fail" % (OKS[0], len(FAILS)))
            sys.exit(1 if FAILS else 0)
    if not (SCRATCH + os.sep).startswith(SCRATCH_ROOT + os.sep) or SCRATCH == SCRATCH_ROOT:
        raise SystemExit("--dir must be inside tools/dev/scratch")
    if os.path.exists(SCRATCH) and os.listdir(SCRATCH) and not os.path.exists(os.path.join(SCRATCH, MARK)):
        raise SystemExit("%s is not empty and not an earlier run of this harness - refusing to use it" % SCRATCH)
    if os.path.exists(SCRATCH):
        shutil.rmtree(SCRATCH)
    os.makedirs(os.path.join(SCRATCH, "tmp"))
    open(os.path.join(SCRATCH, MARK), "w").write("SkyySacks 0.7.14 harness scratch\n")
    if os.path.isdir(LIVE):
        shutil.copytree(LIVE, os.path.join(SCRATCH, "live"))
        print("copied the live data folder (read only):", LIVE)
    env = dict(os.environ, TEMP=os.path.join(SCRATCH, "tmp"), TMP=os.path.join(SCRATCH, "tmp"))
    env.pop("JAVA_TOOL_OPTIONS", None)
    rc1 = subprocess.call([sys.executable, os.path.abspath(__file__), "--child"] + sys.argv[1:], env=env, cwd=ROOT)
    print("---- child 2: the engine asset validators (V)")
    rc2 = subprocess.call([sys.executable, os.path.abspath(__file__), "--child-v"] + sys.argv[1:], env=env, cwd=ROOT)
    rc = 1 if (rc1 or rc2) else 0
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyySacks %s bare-JVM check: %s (exit codes %d / %d)" % (VERSION, "PASS" if rc == 0 else "FAIL", rc1, rc2))
    sys.exit(rc)


if __name__ == "__main__":
    main()
