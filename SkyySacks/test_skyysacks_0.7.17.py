"""Bare-JVM check for SkyySacks 0.7.17 (tools/sacks_0_7_17_patch.py; research/Requip-Smithing-Spec.md round R2; Skyy: "then also let it
pull from the pocket dimension for blocks in the hot bar. (so they auto refill.)" + "we should give this, and the crafting thing a filter by
class. so it only shows things your class can use").

    python SkyySacks/test_skyysacks_0.7.17.py [--jar <0.7.17 jar>] [--old <0.7.16 jar>] [--live <Skyy_SkyySacks folder>] [--dir <scratch>] [--keep]

The parent copies the live data folder (read only; default: the "HUD mod" world's mods/Skyy_SkyySacks) into the scratch folder (default
tools/dev/scratch/sacks0717/sacks-run, deleted at the end unless --keep) and starts two children (the game's JRE, -XX:-UsePerfData,
java.io.tmpdir / TEMP / TMP in the scratch folder):
 child 1 (-Xverify:all; HytaleServer.jar + the 0.7.17 jar + tools/javassist.jar):
  A  every 0.7.17 class loads and verifies (-Xverify:all)
  G / H  the 0.7.14 art + 0.7.16 hold-pose checks again (regression: the art is untouched)
  I  class compare 0.7.16 -> 0.7.17: the same classes; changed beyond the version text = exactly SackBridge, SackFn, SweepTask, CraftPage,
     SkyySacksPlugin; every non-class file byte-identical except manifest.json (Version / Name)
  X  engine-access audit on the jar bytes - 0 refused; control refused
  K  the 0.7.13 bag take bridge, executed again (regression) + the 7 new keys published
  R  REQUIP HOTBAR BLOCK SLOTS (requip:pocket:<uuid>), executed: an empty reserved slot fills to a full stack; a partial plain stack tops
     up; the pool short = what the pool has; another item / a metadata stack / an unreserved empty slot / a non-stacking item / a bag id /
     bad map entries are never touched; no bag / other bag type / master switch off / profile settling -> nothing; the player's own refill
     mode Off still fills (decision); the 2 s tick path (SweepTask.items) and sacks:fn:pocketFill both run it; conservation pool + live;
     review fix 3: the target = requip:pocketN per slot, else SkyyWardrobe pocket.target (config:fn:SkyyWardrobe get), else max stack;
     review fix 2: a damaged partial stack is never topped up
  D  sacks:fn:deposit, executed (review fix 1): the hotbar slot (4th argument) is required - the 3-argument form moves nothing; only that
     slot, bag room (caps) respected, the rest stays in the slot; metadata / damaged / other item / empty slot never; no bag / a bag id /
     cooked food / paused / bad arguments -> 0; the SkyyWardrobe 0.2 giveBack pattern (stack lifted, 3 arguments, rest put back) loses
     nothing; the fixed pattern (4 arguments) moves exactly the slot; conservation; saved pool file + crafts.log lines
  C  THE CRAFT BRIDGES on a stand-in recipe store with the engine's own CraftingRecipe / MaterialQuantity / removeMaterials: craftList
     (bench accessory tier, knowledge, table-only, collections, groups); craftHave (inventory + bags); craftPay inventory first then bags,
     resource-type inputs, all or nothing, never a metadata stack, refused = nothing moved; craftRefund only what the receipt took, once,
     within 60 s, never after commit, never by another player, never after a profile switch; inventory full -> bags; conservation; profile
     isolation (p3 pays from p3 only); review fix 2: a damaged stack is never paid with (refund = fresh stack, no free repair);
     review fix 4: a throw after the bag debit (a real slot removal) rolls back fully and the next payment is exact
  F  THE /craft SMITHING CLASS FILTER: recipesFor("A:smith") with a fake gear:fn:classShow hides exactly the FALSE answers, counts them,
     the note text is set on the page builder; no key / null / non-Boolean / an exception = everything shown; other tabs never filtered
  L  start twice on a scratch COPY of the live data (the 12 bridge keys published each time): no file changes; a real take on the copy
     changes exactly the taken line; a real pocket refill + deposit on the copy change exactly their lines
  O / T / P  the 0.7.15 Omni knowledge, T1 recipe and page-guard checks, executed again (regression)
 child 2 (V - the ENGINE ASSET VALIDATORS, as 0.7.16): the jar loads into the real asset stores with 0 failed stores and 0 SEVERE /
  WARNING lines; the SkyySack set keeps its hold keys.
Exit code 1 on any failure. Live data is only READ (copied). Nothing is deployed.
"""
import os, sys, re, shutil, subprocess, zipfile, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD = "0.7.17", "0.7.16"
PKG = "com.skyy.sacks."
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE_DEFAULT = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyySacks")
MARK = ".skyysacks-0.7.17-harness"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH_ROOT = os.path.realpath(os.path.join(TOOLS, "dev", "scratch"))
SCRATCH = os.path.realpath(os.path.abspath(arg("--dir", os.path.join(SCRATCH_ROOT, "sacks0717", "sacks-run"))))
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

    # ---------------- H. the hold pose (pure Python; hold_checks below)
    H = hold_checks(zn, G)

    # ---------------- I. class compare 0.7.16 -> 0.7.17
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
    WANT_CHANGED = ["CraftPage", "SackBridge", "SackFn", "SkyySacksPlugin", "SweepTask"]
    check(sorted(other) == WANT_CHANGED, "I: changed beyond the version text = exactly %s (got %s)" % (WANT_CHANGED, sorted(other)))
    ao = dict((n, zo.read(n)) for n in zo.namelist() if not n.endswith(".class"))
    an = dict((n, zn.read(n)) for n in zn.namelist() if not n.endswith(".class"))
    changed = sorted(n for n in set(ao) & set(an) if ao[n] != an[n])
    check(sorted(ao) == sorted(an) and changed == ["manifest.json"],
          "I: every non-class file byte-identical to %s except manifest.json (added %s removed %s changed %s)"
          % (OLD, sorted(set(an) - set(ao))[:3], sorted(set(ao) - set(an))[:3], changed[:4]))
    mo_, mn_ = json.loads(ao["manifest.json"]), json.loads(an["manifest.json"])
    check(mn_.pop("Version") == VERSION and mo_.pop("Version") == OLD and mo_.pop("Name") == OLD + " SkyySacks" and mn_.pop("Name") == VERSION + " SkyySacks"
          and mo_ == mn_, "I: manifest.json differs only in Version / Name")
    # the changed classes: old methods kept with the same signatures (nothing removed), the new ones listed
    CPc = JClass("javassist.ClassPool")(False)
    CPc.appendClassPath(B.SERVER_JAR)
    CPc.appendClassPath(B.JAVASSIST)

    def sigs(blob, name):
        cf_ = JClass("javassist.bytecode.ClassFile")(JClass("java.io.DataInputStream")(JClass("java.io.ByteArrayInputStream")(blob)))
        return set(str(m.getName()) + str(m.getDescriptor()) for m in cf_.getMethods()), set(str(f.getName()) for f in cf_.getFields())
    added_m = {}
    for c_ in WANT_CHANGED:
        n_ = "com/skyy/sacks/%s.class" % c_
        mo2, fo2 = sigs(co[n_], c_)
        mn2, fn2 = sigs(cn[n_], c_)
        check(mo2 <= mn2 and fo2 <= fn2, "I: %s keeps every 0.7.16 method + field (missing %s %s)" % (c_, sorted(mo2 - mn2)[:3], sorted(fo2 - fn2)[:3]))
        added_m[c_] = sorted(x.split("(")[0] for x in mn2 - mo2) + sorted("field " + x for x in fn2 - fo2)
    want_new = {"SweepTask": ["plainFresh", "pocketFill", "wardrobeTarget"], "CraftPage": ["classShow", "field CLASSWARN", "field classHidden", "smithNote", "smithNoteText"],
                "SackFn": [], "SkyySacksPlugin": [],
                "SackBridge": sorted(["addCount", "call2", "claim", "craftCommit", "craftHave", "craftList", "craftPay", "craftRefund",
                                      "craftWhy", "creditBags", "deposit", "dflt", "giveSurplus", "inGroup", "metaTouched", "nextReceipt", "payConts",
                                      "payFail", "payView", "plainCopy", "applyCopy", "pocketNow", "purgeReceipts", "refuse", "sameStack", "slotRestore", "slotSnap", "smithOut",
                                      "spill"]) + ["field RECEIPTS", "field RECEIPT_MS", "field RSEQ"]}
    check(dict((k_, sorted(v_)) for k_, v_ in added_m.items()) == dict((k_, sorted(v_)) for k_, v_ in want_new.items()),
          "I: the new members are exactly the 0.7.17 ones: %s" % added_m)
    print("I. class compare %s -> %s: %d identical, %d version-text only, %d changed (%s) with only added members; files identical but manifest"
          % (OLD, VERSION, len(same), len(vers), len(other), ", ".join(sorted(other))))

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
    FAKECLS = fake.toClass(AS.class_)   # 0.7.17: kept - the CraftingRecipe stand-in store is a second instance
    store = us.allocateInstance(FAKECLS)
    fm = AS.class_.getDeclaredField("assetMap")
    fm.setAccessible(True)
    DAMN = "com.hypixel.hytale.assetstore.map.DefaultAssetMap"
    kmap = jp.makeClass("com.hypixel.hytale.assetstore.map.SkyyTestKnownMap", jp.get(DAMN))
    kmap.addField(JClass("javassist.CtField").make("public static final java.util.HashSet KNOWN = new java.util.HashSet();", kmap))
    # 0.7.17: CUSTOM = id -> our own Item stand-ins (a non-stacking item, an item with a resource type) for R / C
    kmap.addField(JClass("javassist.CtField").make("public static final java.util.HashMap CUSTOM = new java.util.HashMap();", kmap))
    kmap.addConstructor(JClass("javassist.CtNewConstructor").make("public SkyyTestKnownMap() { super(); }", kmap))
    kmap.addMethod(JClass("javassist.CtNewMethod").make(
        "public com.hypixel.hytale.assetstore.JsonAsset getAsset(Object key) { if (key != null && CUSTOM.containsKey(key)) "
        "return (com.hypixel.hytale.assetstore.JsonAsset) CUSTOM.get(key); if (key != null && KNOWN.contains(key)) "
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
    # 0.7.17: the two combined views the craft bridges / refunds use (the engine builds them from its own fields; ours are the three above)
    CICN = "com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer"
    for m, order in (("getCombinedBackpackStorageHotbar", "this.b, this.s, this.h"), ("getCombinedStorageHotbarBackpack", "this.s, this.h, this.b")):
        tinv.addMethod(CtM.make("public %s %s() { return new %s(new %s[] { %s }); }" % (CICN, m, CICN, ICN, order), tinv))
    TInv = JClass(tinv.toClass(JClass(INVN).class_))
    # review fix 4: a SimpleItemContainer whose next removeItemStackFromSlot(short, int) throws once (BOOM) - craftPay's applyCopy runs it
    # on the real slots AFTER the bag debit
    SICN = "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer"
    tboom = jp.makeClass("com.hypixel.hytale.server.core.inventory.container.SkyyTestBoomCont", jp.get(SICN))
    tboom.addField(CtF.make("public static volatile boolean BOOM;", tboom))
    tboom.addConstructor(CtC.make("public SkyyTestBoomCont(short n) { super(n); }", tboom))
    tboom.addMethod(CtM.make("public com.hypixel.hytale.server.core.inventory.transaction.ItemStackSlotTransaction removeItemStackFromSlot(short s, int q) "
                             "{ if (BOOM) { BOOM = false; throw new IllegalStateException(\"test boom\"); } return super.removeItemStackFromSlot(s, q); }", tboom))
    TBoom = JClass(tboom.toClass(JClass(SICN).class_))
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

    BRIDGE_KEYS = ("sacks:fn:count", "sacks:fn:take", "sacks:fn:put", "sacks:fn:all", "sacks:fn:commit",
                   # 0.7.17 (modes 5-11, the plugin's setup() order)
                   "sacks:fn:deposit", "sacks:fn:pocketFill", "sacks:fn:craftList", "sacks:fn:craftHave", "sacks:fn:craftPay",
                   "sacks:fn:craftRefund", "sacks:fn:craftCommit")

    def publish():
        for i, key in enumerate(BRIDGE_KEYS):
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
            # 0.7.17: a real Requip pocket refill + a real deposit on the copy change exactly the Tree Sap line, and give it back exactly
            plv = player(backpack=[(OMNI, 1)])   # the Omni: room for any live pool size
            TPlayers.P = plv
            pm0 = JClass("java.util.HashMap")()
            pm0.put(JClass("java.lang.Integer")(0), JString(SAP))
            bridge.put("requip:pocket:" + target, pm0)
            b2 = dict((kk, read_pool(pd, kk)) for kk in keys)
            got_l = int(bridge.get("sacks:fn:pocketFill").apply(Ut).longValue())
            Pool.flushDirty()
            a2 = dict((kk, read_pool(pd, kk)) for kk in keys)
            changed = sorted(kk for kk in keys if a2[kk] != b2[kk])
            hb_l = plv.getInventory().getHotbar().getItemStack(JShort(0))
            check(got_l == min(100, b2[target][SAP]) and changed == [target] and a2[target].get(SAP, 0) == b2[target][SAP] - got_l
                  and hb_l is not None and int(hb_l.getQuantity()) == got_l
                  and sorted(i for i in set(a2[target]) | set(b2[target]) if a2[target].get(i) != b2[target].get(i)) == [SAP],
                  "L: a real pocket refill on the copy: hotbar slot 0 gets %d Tree Sap, exactly that line of that pool file changes" % got_l)
            bridge.remove("requip:pocket:" + target)
            arr_l = JArray(JClass("java.lang.Object"))(4)
            arr_l[0], arr_l[1], arr_l[2], arr_l[3] = Ut, JString(SAP), Long_(got_l), JClass("java.lang.Integer")(0)
            back_l = int(bridge.get("sacks:fn:deposit").apply(arr_l).longValue())
            Pool.flushDirty()
            a3 = dict((kk, read_pool(pd, kk)) for kk in keys)
            e0_ = plv.getInventory().getHotbar().getItemStack(JShort(0))
            check(back_l == got_l and a3 == b2 and (e0_ is None or e0_.isEmpty()),
                  "L: sacks:fn:deposit of hotbar slot 0 puts the %d back: every pool file holds the same values as before" % back_l)
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
        print("L. start twice on the live copy (%d pools): no file changed; a real take, a real pocket refill and its deposit back on the copy change exactly the Tree Sap line of that profile pool file" % n1)


    # ================================================================================================ 0.7.15 sections (O, T, P)
    KS, SPage, PT, CPage = J("KnowSync"), J("SacksPage"), J("ProcTask"), J("CraftPage")
    HSet, HMap, UCBc = JClass("java.util.HashSet"), JClass("java.util.HashMap"), JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    LEG = ["Skyy_Sack_%s_Large" % c for c in BAG_CATS]
    SMALL = ["Skyy_Sack_%s_Small" % c for c in BAG_CATS]
    RID = lambda i: i + "_Recipe_Generated_0"
    U2 = UUID.fromString("00000000-0000-0000-0000-0000000b0715")

    def jset(xs):
        s_ = HSet()
        for x in xs:
            s_.add(JString(x))
        return s_

    def pyset(s_):
        return None if s_ is None else set(str(x) for x in s_)

    def publish_coll(u, recipe_ids):
        bridge.put("coll:recipes:" + str(u), JString(",".join(recipe_ids)))

    def ucb_text(b_):
        out_ = []
        for c_ in b_.getCommands():
            k_ = c_.getClass()
            while k_ is not None:
                for f_ in k_.getDeclaredFields():
                    if JClass("java.lang.reflect.Modifier").isStatic(f_.getModifiers()):
                        continue
                    f_.setAccessible(True)
                    v_ = f_.get(c_)
                    if v_ is not None:
                        out_.append(str(v_))
                k_ = k_.getSuperclass()
        return "\n".join(out_)

    # ---------------- O. the Omni recipe needs knowledge: KnowSync teaches it exactly with all five Legendary bag recipes
    Cfg.FREE_RECIPES = False
    KS.SEENCOLL = False
    bridge.put("coll:fn:tier", kfn)                     # SkyyCollections installed (any Function under coll:fn:tier)
    check(not Cfg.effFree() and list(KS.LEGEND) == LEG and list(KS.SYNCED) == list(KS.MANAGED) + [OMNI] and len(KS.SYNCED) == 21,
          "O: collection mode; LEGEND = the five Legendary bags; SYNCED = the 20 bags + the Omni")
    for n in range(0, 6):
        coll = [RID(i) for i in SMALL] + [RID(i) for i in LEG[:n]]
        publish_coll(U2, coll)
        cs = KS.collSet(U2)
        w = pyset(KS.wanted(U2))
        st_ = str(KS.omniStatus(cs, 2))
        lt_ = str(KS.omniLockText(cs, 2))
        nl_ = str(SPage.nextLine(None, U2, "Mining", 4))
        if n < 5:
            check(OMNI not in w and w == set(SMALL + LEG[:n]) and int(KS.legendKnown(cs)) == n and int(KS.legendIn(KS.wanted(U2))) == n
                  and not KS.omniUnlocked(cs) and not KS.unlocked(U2, OMNI, cs)
                  and not KS.allowedOut(True, OMNI, RID(OMNI), jset([OMNI]), cs)
                  and st_ == "unlocks with all 5 Legendary bags unlocked (%d of 5)" % n
                  and lt_ == "The Mythic Omni Bag unlocks when you have unlocked all 5 Legendary bags (%d of 5)" % n
                  and nl_ == "Next: the Mythic Omni Bag - " + st_,
                  "O: %d of 5 Legendary recipes -> the Omni is NOT wanted / unlocked / allowed in /craft (even if the known set has it); page: %r; /craft: %r"
                  % (n, st_, lt_))
        else:
            check(OMNI in w and w == set(SMALL + LEG + [OMNI]) and int(KS.legendKnown(cs)) == 5 and KS.omniUnlocked(cs) and KS.unlocked(U2, OMNI, cs)
                  and KS.allowedOut(True, OMNI, RID(OMNI), None, cs)
                  and st_ == "UNLOCKED - one Legendary bag of each type (you carry 2 of 5)"
                  and lt_ == "The Mythic Omni Bag needs one Legendary bag of each type (you carry 2 of 5)",
                  "O: 5 of 5 Legendary recipes -> the Omni is wanted (taught), unlocked, allowed in /craft; page %r; /craft %r" % (st_, lt_))
        # fixer 0.7.15: the Mythic ladder row (bold 15, 26 px, no wrap, 1000 px page) uses the short omniRow and stays within the 0.7.14 row
        # length (105 characters: "... every bag type - one Legendary bag of each type (you carry 5 of 5)")
        rw_ = str(KS.omniRow(cs, 2))
        row_ = str(Defs.bagName(Defs.OMNI)) + " - " + str(SPage.num(Defs.CAP_OMNI)) + " of each item, every bag type - " + rw_
        want_rw = ("needs all 5 Legendary bags unlocked (%d of 5)" % n) if n < 5 else "UNLOCKED - you carry 2 of 5 Legendary bag types"
        check(rw_ == want_rw and len(row_) <= 106, "O fix: %d of 5 -> ladder row %r (%d chars, <= 106 = 0.7.14)" % (n, row_, len(row_)))
    # allowedOut keeps the old rules for everything else
    cs5 = KS.collSet(U2)
    check(KS.allowedOut(False, "Anything", "x", None, None) and not KS.allowedOut(True, None, "x", None, cs5)
          and KS.allowedOut(True, LEG[0], RID(LEG[0]), None, cs5) and not KS.allowedOut(True, "Skyy_Sack_Mining_Rare", RID("Skyy_Sack_Mining_Rare"), None, cs5)
          and KS.allowedOut(True, "Armor_Bronze_Chest", "r", jset(["Armor_Bronze_Chest"]), cs5) and not KS.allowedOut(True, "Armor_Bronze_Chest", "r", jset([]), cs5),
          "O: allowedOut: no-knowledge recipes always, a bag by its recipe id, vanilla knowledge recipes by the known set (unchanged rules)")
    # next(): only SYNCED entries change, null = nothing to send
    want5 = KS.wanted(U2)
    k0 = jset(["Armor_Bronze_Chest", "Skyy_Sack_Mining_Rare"])
    ns = KS.next(k0, want5)
    check(ns is not None and pyset(ns) == set(SMALL + LEG + [OMNI, "Armor_Bronze_Chest"]) and KS.next(ns, want5) is None,
          "O: next(): adds the bags + the Omni, drops the not-unlocked Rare, keeps a vanilla entry; a second sweep sends nothing (null)")
    publish_coll(U2, [RID(i) for i in SMALL] + [RID(i) for i in LEG[:4]])   # a Legendary recipe LOST (admin / collection reset)
    want4 = KS.wanted(U2)
    ns4 = KS.next(ns, want4)
    check(ns4 is not None and OMNI not in pyset(ns4) and LEG[4] not in pyset(ns4) and "Armor_Bronze_Chest" in pyset(ns4) and KS.next(ns4, want4) is None,
          "O: losing a Legendary recipe -> the next sweep removes the Legendary AND the Omni from the known set (one update), nothing else")
    # sync() on a stand-in player: the known set changes, the inventory (an owned Omni) is never touched
    PCDc = JClass("com.hypixel.hytale.server.core.entity.entities.player.data.PlayerConfigData")
    pcd = PCDc()   # the public no-arg constructor (markChanged needs its fields)
    pcd.setKnownRecipes(jset(SMALL + LEG + [OMNI, "Armor_Bronze_Chest"]))   # a player who knew the Omni + a vanilla knowledge recipe
    po = player(backpack=[(OMNI, 1)], hotbar=[(LEG[0], 1)])
    pcd_f = None
    for f_ in PLA.class_.getDeclaredFields():
        if f_.getType() == PCDc.class_:
            pcd_f = f_
    k_ = PLA.class_.getSuperclass()
    while pcd_f is None and k_ is not None:
        for f_ in k_.getDeclaredFields():
            if f_.getType() == PCDc.class_:
                pcd_f = f_
        k_ = k_.getSuperclass()
    pcd_f.setAccessible(True)
    pcd_f.set(po, pcd)
    STc = JClass("com.hypixel.hytale.component.Store")
    REFc = JClass("com.hypixel.hytale.component.Ref")
    fst = us.allocateInstance(STc.class_)
    fref = REFc(fst, JInt(0))

    def inv_snap(p_):
        out_ = []
        inv_ = p_.getInventory()
        for cont in (inv_.getStorage(), inv_.getHotbar(), inv_.getBackpack()):
            for s_ in range(int(cont.getCapacity())):
                it_ = cont.getItemStack(JShort(s_))
                out_.append(None if it_ is None or it_.isEmpty() else (str(it_.getItemId()), int(it_.getQuantity())))
        return out_
    inv0 = inv_snap(po)
    sent = "no"
    try:
        r_ = KS.sync(fref, fst, po, U2)
        sent = "returned %s" % r_
    except Exception as e:
        sent = "sendKnownRecipes reached (%s)" % str(e)[:60]       # the bare JVM has no network: the send itself throws after the set
    kn = pyset(po.getPlayerConfigData().getKnownRecipes())
    check(kn is not None and OMNI not in kn and LEG[4] not in kn and "Armor_Bronze_Chest" in kn and inv_snap(po) == inv0 and inv0.count((OMNI, 1)) == 1,
          "O: sync() (4 of 5 Legendary) sets the known set without the Omni (%s); the carried Omni item is untouched (known %s)" % (sent, sorted(kn or [])[:30]))
    check(not KS.sync(fref, fst, po, U2), "O: sync() again -> no change, nothing sent (false)")
    publish_coll(U2, [RID(i) for i in SMALL] + [RID(i) for i in LEG])
    try:
        KS.sync(fref, fst, po, U2)
    except Exception:
        pass
    check(OMNI in pyset(po.getPlayerConfigData().getKnownRecipes()) and not KS.sync(fref, fst, po, U2),
          "O: sync() with all five Legendary recipes teaches the Omni (one update), then nothing")
    # free-recipes mode and no SkyyCollections = known like every bag
    Cfg.FREE_RECIPES = True
    w = pyset(KS.wanted(U2))
    check(Cfg.effFree() and w == set(list(KS.MANAGED) + [OMNI]) and int(KS.legendKnown(None)) == 5 and KS.omniUnlocked(None)
          and KS.unlocked(U2, OMNI, None) and str(KS.omniStatus(None, 1)) == "free on this server - one Legendary bag of each type (you carry 1 of 5)",
          "O: free-recipes mode -> every bag AND the Omni wanted; page says free")
    Cfg.FREE_RECIPES = True
    rwf_ = str(Defs.bagName(Defs.OMNI)) + " - " + str(SPage.num(Defs.CAP_OMNI)) + " of each item, every bag type - " + str(KS.omniRow(None, 5))
    old_ = str(Defs.bagName(Defs.OMNI)) + " - " + str(SPage.num(Defs.CAP_OMNI)) + " of each item, every bag type - one Legendary bag of each type (you carry 5 of 5)"
    check(str(KS.omniRow(None, 5)) == "free here - you carry 5 of 5 Legendary bag types" and len(rwf_) <= len(old_),
          "O fix: free mode ladder row %r (%d chars) no longer than the 0.7.14 row (%d)" % (rwf_, len(rwf_), len(old_)))
    Cfg.FREE_RECIPES = False
    bridge.remove("coll:fn:tier")
    KS.SEENCOLL = False
    w = pyset(KS.wanted(U2))
    check(Cfg.effFree() and w is not None and OMNI in w, "O: no SkyyCollections (never seen) -> free -> the Omni is known like every bag")
    KS.SEENCOLL = True
    check(KS.wanted(U2) is None, "O: SkyyCollections seen then gone (reload) -> change nothing (null), the Omni too")
    bridge.put("coll:fn:tier", kfn)
    # the not-carried bag page (buildNoBag) executed: the Mythic ladder row + the Normal recipe sentence
    publish_coll(U2, [RID(i) for i in SMALL] + [RID(i) for i in LEG[:3]])
    pgn = us.allocateInstance(SPage.class_)
    jfield(SPage.class_, "cat").set(pgn, JString("Foraging"))
    b_ = UCBc()
    pgn.buildNoBag(b_, None, str(U2), HMap(), U2)
    txt = ucb_text(b_)
    check("Mythic Omni Bag - 100,000 of each item, every bag type - needs all 5 Legendary bags unlocked (3 of 5)" in txt and "every bag type - unlocks with all" not in txt,   # fixer: omniRow
          "O: bag page (not carried, buildNoBag executed): the Mythic ladder row is the short omniRow 'needs all 5 Legendary bags unlocked (3 of 5)'")
    print("O. the Omni: hidden (not taught, not allowed, page + /craft say k of 5) at 0-4 Legendary recipes, taught at 5, removed again when one is "
          "lost; sync() sends only on a change and never touches items; free mode / no SkyyCollections = known; reload window = no change")

    # ---------------- T. T1 bags from Plant Fiber + Sticks (the page sentence executed above + the item JSONs)
    check(str(Defs.BOLT[0]) == "Ingredient_Fibre" and int(Defs.BOLTQ) == 20 and str(Defs.BOLTN[0]) == "Plant Fiber" and int(Defs.MATQ) == 4
          and all(str(x) == "Ingredient_Stick" for x in Defs.MAT) and all(str(x) == "Sticks" for x in Defs.MATN) and len(Defs.MAT) == 5,
          "T: SackDefs: BOLT[0] Ingredient_Fibre x20 'Plant Fiber', MAT Ingredient_Stick x4 'Sticks' for all five types")
    check("Normal Foraging Bag = 20 Plant Fiber + 4 Sticks at a Workbench. You have 0 / 20 Plant Fiber and 0 / 4 Sticks." in txt
          and "Ingredient_Fibre" in txt and "Ingredient_Stick" in txt and "Wool" not in txt and "Copper" not in txt,
          "T: bag page 'how to get one': 20 Plant Fiber + 4 Sticks (icons Ingredient_Fibre / Ingredient_Stick), no wool, no copper")
    pg2 = us.allocateInstance(SPage.class_)
    jfield(SPage.class_, "cat").set(pg2, JString("Mining"))
    b2 = UCBc()
    pg2.buildNoBag(b2, player(storage=[("Ingredient_Fibre", 25), ("Ingredient_Stick", 4)]), str(U2), HMap(), U2)
    check("You have 25 / 20 Plant Fiber and 4 / 4 Sticks - ready to craft." in ucb_text(b2), "T: with 25 fiber + 4 sticks carried the page says ready to craft")
    with zipfile.ZipFile(ASSETS_ZIP) as az:
        vids = set(os.path.basename(n_)[:-5] for n_ in az.namelist() if n_.startswith("Server/Item/Items/") and n_.endswith(".json"))
        vlang = az.read("Server/Languages/en-US/server.lang").decode("utf-8-sig")
    bad_t1 = []
    for i in SMALL:
        rin = json.loads(zn.read("Server/Item/Items/Utility/%s.json" % i))["Recipe"]["Input"]
        if sorted((x["ItemId"], x["Quantity"]) for x in rin) != [("Ingredient_Fibre", 20), ("Ingredient_Stick", 4)]:
            bad_t1.append((i, rin))
    check(not bad_t1 and "Ingredient_Fibre" in vids and "Ingredient_Stick" in vids and "items.Ingredient_Fibre.name = Plant Fiber" in vlang
          and "items.Ingredient_Stick.name = Stick" in vlang, "T: the five Normal recipes = 20 Ingredient_Fibre + 4 Ingredient_Stick; both ids are in Assets.zip "
          "(server.lang 'Plant Fiber' / 'Stick'): %s" % bad_t1[:2])
    print("T. Normal bags: 20 Plant Fiber + 4 Sticks in all five item recipes and on the page (ids verified in Assets.zip)")

    # ---------------- P. the page guard: ProcTask.notice / sameEntry
    r_now = REFc(fst, JInt(3))
    r_old = REFc(fst, JInt(3))
    inv_m = None
    for m_ in REFc.class_.getDeclaredMethods():
        if str(m_.getName()) == "invalidate" and len(m_.getParameterTypes()) == 0:
            inv_m = m_
    inv_m.setAccessible(True)
    inv_m.invoke(r_old)
    check(PT.sameEntry(r_now, r_now) and PT.sameEntry(REFc(fst, JInt(3)), r_now) and not PT.sameEntry(r_old, r_now)
          and not PT.sameEntry(REFc(fst, JInt(4)), r_now) and not PT.sameEntry(None, r_now) and not PT.sameEntry(r_now, None)
          and not PT.sameEntry(REFc(us.allocateInstance(STc.class_), JInt(3)), r_now) and not r_old.isValid(),
          "P: sameEntry: same Ref / same store + index -> true; an invalidated Ref (world move), another index or store, null -> false")
    res = {}
    for cls_, nm_ in ((SPage, "SacksPage"), (CPage, "CraftPage")):
        pg_ = us.allocateInstance(cls_.class_)
        jfield(cls_.class_, "key").set(pg_, JString("k-old"))
        check(int(PT.notice(pg_, "k-old", r_now)) == 0, "P: %s: same key -> 0 (no notice due)" % nm_)
        jfield(cls_.class_, "builtRef").set(pg_, r_old)
        a_ = int(PT.notice(pg_, "k-new", r_now))
        nk_ = jfield(cls_.class_, "noticeKey").get(pg_)
        check(a_ == 2 and nk_ is None, "P: %s built for the Ref lost in a world move -> 2 (skipped), profileNotice NOT called" % nm_)
        jfield(cls_.class_, "builtRef").set(pg_, r_now)
        try:
            a_ = int(PT.notice(pg_, "k-new", r_now))
        except Exception as e:
            a_ = "sendUpdate reached (%s)" % str(e)[:40]           # no client in a bare JVM: the send throws after noticeKey is set
        nk_ = jfield(cls_.class_, "noticeKey").get(pg_)
        check(nk_ is not None and str(nk_) == "k-new", "P: %s built for the current Ref -> profileNotice runs (%s)" % (nm_, a_))
        jfield(cls_.class_, "key").set(pg_, None)
        res[nm_] = int(PT.notice(pg_, "k-new", r_now))
        check(res[nm_] == 0, "P: %s with no key -> 0" % nm_)
    check(int(PT.notice(None, "k", r_now)) == 0 and int(PT.notice(JString("other page"), "k", r_now)) == 0, "P: no page / another mod's page -> 0")
    print("P. page guard: profileNotice only for a page built for the player's current entity Ref; a page lost in a world move is skipped")

    # ================================================================================================ 0.7.17 sections (R, D, C, F)
    Swp, Cfg0, RF0, CPg = J("SweepTask"), J("SackCfg"), J("RefillPref"), J("CraftPage")
    HMapJ, IntJ, BoolJ = JClass("java.util.HashMap"), JClass("java.lang.Integer"), JClass("java.lang.Boolean")
    LHM = JClass("java.util.LinkedHashMap")
    BsonDoc, BsonStr = JClass("org.bson.BsonDocument"), JClass("org.bson.BsonString")
    ItemC = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    IRTc = JClass("com.hypixel.hytale.protocol.ItemResourceType")
    UCBc = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    IRON, BIRCH, GEM = "Ore_Iron", "Wood_Birch_Trunk", "Skyy_Test_Trinket"
    for kid_ in (IRON, BIRCH, GEM):
        KMap.KNOWN.add(kid_)

    def custom_item(iid, max_stack=100, rts=None):
        it_ = ItemC(JString(iid))
        jfield(ItemC.class_, "maxStack").setInt(it_, max_stack)
        if rts:
            arr_ = JArray(IRTc)(len(rts))
            for i_, (rt_, q_) in enumerate(rts):
                arr_[i_] = IRTc(JString(rt_), JInt(q_))
            jfield(ItemC.class_, "resourceTypes").set(it_, arr_)
        KMap.CUSTOM.put(JString(iid), it_)
        return it_

    def fn(key, *a):
        arr = ObjArr(len(a))
        for i, v in enumerate(a):
            arr[i] = Long_(v) if isinstance(v, int) and not isinstance(v, bool) else v
        return bridge.get(key).apply(arr)

    def meta():
        d_ = BsonDoc()
        d_.put("SkyyGear", BsonStr("rolled"))
        return d_

    def setslot(cont, s_, iid, q=0, md=None):
        if iid is None:
            cont.removeItemStackFromSlot(JShort(s_))
        else:
            cont.setItemStackForSlot(JShort(s_), IS(iid, q, md) if md is not None else IS(iid, q))

    def slots(cont):
        out_ = []
        for s_ in range(int(cont.getCapacity())):
            it_ = cont.getItemStack(JShort(s_))
            if it_ is None or it_.isEmpty():
                out_.append(None)
            else:
                md_ = it_.getMetadata()
                out_.append((str(it_.getItemId()), int(it_.getQuantity())) + (("meta",) if md_ is not None and not md_.isEmpty() else ()))
        return out_

    def snap_inv(p_):
        inv_ = p_.getInventory()
        return [slots(c_) for c_ in (inv_.getStorage(), inv_.getHotbar(), inv_.getBackpack())]

    def live(p_, iid):
        v_ = Swp.carried(p_.getInventory()).get(iid)
        return 0 if v_ is None else int(v_.longValue())

    def settle(u_):
        Pool.CHANGEDAT.put(u_, Long_(int(System.currentTimeMillis()) - 7000))

    def pocket_now(u_):
        return int(bridge.get("sacks:fn:pocketFill").apply(u_).longValue())

    custom_item(IRON, max_stack=1)
    check(str(Defs.homeOf(IRON)) == "Mining" and str(Defs.homeOf(COP)) == "Mining" and str(Defs.homeOf(SAP)) == "Foraging"
          and int(ItemC.getAssetMap().getAsset(IRON).getMaxStack()) == 1 and int(ItemC.getAssetMap().getAsset(COP).getMaxStack()) == 100
          and Defs.homeOf(GEM) is None and str(Defs.homeOf(BIRCH)) == "Foraging",
          "R: stand-ins: Ore_Iron (Mining) does not stack (max 1), Ore_Copper (Mining) max 100, Tree Sap + Birch Foraging, the test trinket has no bag")

    # ---------------- R. Requip hotbar block slots (requip:pocket:<uuid>)
    U3 = UUID.fromString("00000000-0000-0000-0000-0000000a0717")
    k3 = str(U3)
    rd = os.path.join(SCRATCH, "r", "pools")
    fresh_pools(rd)
    write_pool(rd, k3, {COP: 250, SAP: 30, IRON: 5})
    publish()
    Bridge.PLAYERS = TPlayers()
    pr_ = player(backpack=[(MIN_S, 1)])
    TPlayers.P = pr_
    hb = pr_.getInventory().getHotbar()
    setslot(hb, 2, COP, 40)
    setslot(hb, 3, SAP, 5)                  # reserved for copper, holds another item
    setslot(hb, 4, COP, 10, meta())         # reserved for copper, holds copper WITH metadata
    pmap = HMapJ()
    for s_, iid in ((0, COP), (2, COP), (3, COP), (4, COP), (6, IRON), (7, MIN_S), (8, "Nope_Not_An_Item")):
        pmap.put(IntJ(s_), JString(iid))
    pmap.put(JString("1"), JString(COP))      # bad key type
    pmap.put(IntJ(99), JString(COP))          # outside the hotbar
    pmap.put(IntJ(5), Long_(3))               # bad value type
    hb0 = slots(hb)
    check(Swp.pocketFill(pr_, k3, U3) == 0 and slots(hb) == hb0 and pc(k3)[COP] == 250, "R: no requip:pocket key -> nothing")
    bridge.put("requip:pocket:" + k3, JString("not a map"))
    check(Swp.pocketFill(pr_, k3, U3) == 0 and slots(hb) == hb0, "R: a requip:pocket value that is not a Map -> nothing")
    bridge.put("requip:pocket:" + k3, pmap)
    Cfg0.REFILL_ON = False
    check(Swp.pocketFill(pr_, k3, U3) == 0 and slots(hb) == hb0 and pc(k3)[COP] == 250, "R: Server Setup bags.refill OFF -> nothing")
    Cfg0.REFILL_ON = True
    RF0.set(U3, 2)                            # the player's own stack refill mode: Off
    check(int(RF0.mode(U3)) == 2, "R: the player's refill mode is Off")
    tot0 = pc(k3)[COP] + live(pr_, COP)
    n_ = Swp.pocketFill(pr_, k3, U3)
    hb1 = slots(hb)
    check(n_ == 160 and hb1[0] == (COP, 100) and hb1[2] == (COP, 100) and hb1[3] == (SAP, 5) and hb1[4] == (COP, 10, "meta")
          and hb1[1] is None and hb1[5] is None and hb1[6] is None and hb1[7] is None and hb1[8] is None and pc(k3)[COP] == 90
          and pc(k3)[IRON] == 5 and pc(k3)[SAP] == 30,
          "R: (mode Off - the pick is the opt-in) empty reserved slot 0 -> 100 (a full stack), partial 40 -> 100; another item, a metadata "
          "stack, a non-stacking item, a bag id, an unknown id, bad keys / values / slots and unreserved slots untouched; pool 250 -> 90: %s" % hb1)
    check(pc(k3)[COP] + live(pr_, COP) == tot0 and int(Pool.kept(k3, COP)) == 160, "R: conservation (pool + live copper unchanged) and the 160 are KEPT")
    check(Swp.pocketFill(pr_, k3, U3) == 0 and slots(hb) == hb1, "R: a second run with full slots moves nothing")
    RF0.set(U3, 0)
    # the pool shorter than the slots need: exactly what the pool has
    setslot(hb, 0, None)
    setslot(hb, 2, COP, 1)
    Pool.pool(k3).put(JString(COP), Long_(50))
    n_ = Swp.pocketFill(pr_, k3, U3)
    hb2 = slots(hb)
    check(n_ == 50 and COP not in pc(k3) and ((hb2[0] == (COP, 50) and hb2[2] == (COP, 1)) or (hb2[0] is None and hb2[2] == (COP, 51))),
          "R: pool 50 < need -> exactly 50 move, the pool entry is gone, never below zero: %s" % hb2[:3])
    # bag gates: no bag / a Foraging bag only (copper is Mining -> nothing; a reserved Tree Sap slot fills)
    write_pool(rd, k3, {COP: 250, SAP: 30})
    Pool.POOLS.clear()
    pn = player()
    check(Swp.pocketFill(pn, k3, U3) == 0 and all(x is None for x in slots(pn.getInventory().getHotbar())), "R: no bag carried -> nothing")
    pf_ = player(backpack=[(FOR_S, 1)])
    hbf = pf_.getInventory().getHotbar()
    pmap.put(IntJ(1), JString(SAP))
    n_ = Swp.pocketFill(pf_, k3, U3)
    check(n_ == 30 and slots(hbf)[1] == (SAP, 30) and slots(hbf)[0] is None and pc(k3)[COP] == 250 and SAP not in pc(k3),
          "R: a Foraging bag only -> the reserved Tree Sap slot fills (30), the copper slots stay empty (no Mining bag)")
    pmap.remove(IntJ(1))
    # the 2 s tick path (SweepTask.items) and sacks:fn:pocketFill (the settle gate)
    write_pool(rd, k3, {COP: 450})
    Pool.POOLS.clear()
    pt_ = player(backpack=[(MIN_S, 1)])
    TPlayers.P = pt_
    out_ = Swp.items(pt_, k3, U3)
    ht_ = slots(pt_.getInventory().getHotbar())
    check(int(out_[1]) == 400 and ht_[0] == ht_[2] == ht_[3] == ht_[4] == (COP, 100) and pc(k3)[COP] == 50,
          "R: the 2 s tick path (SweepTask.items) fills the 4 reserved empty copper slots (0, 2, 3, 4) -> %s / %s" % (list(out_), ht_[:5]))
    pt2 = player(backpack=[(MIN_S, 1)])
    TPlayers.P = pt2
    Pool.CHANGEDAT.put(U3, Long_(int(System.currentTimeMillis())))
    check(pocket_now(U3) == 0 and all(x is None for x in slots(pt2.getInventory().getHotbar())), "R: sacks:fn:pocketFill while the profile settles -> 0")
    settle(U3)
    check(pocket_now(U3) == 50 and pc(k3).get(COP) is None, "R: sacks:fn:pocketFill settled -> fills now (50 = the rest of the pool)")
    check(int(bridge.get("sacks:fn:pocketFill").apply(JString("x")).longValue()) == 0, "R: sacks:fn:pocketFill bad argument -> 0")
    TPlayers.P = None
    check(pocket_now(U3) == 0, "R: sacks:fn:pocketFill with no player on this thread -> 0")
    # profile isolation: profile 3 active -> only the -p3 pool pays
    write_pool(rd, k3, {COP: 250})
    write_pool(rd, k3 + "-p3", {COP: 7})
    Pool.POOLS.clear()
    bridge.put("profile:fn:key", kfn)
    KeyFn.key = k3 + "-p3"
    bridge.put("profile:epoch:" + k3, Long_(5))
    pi_ = player(backpack=[(MIN_S, 1)])
    TPlayers.P = pi_
    first_ = pocket_now(U3)
    settle(U3)
    r_ = pocket_now(U3)
    Pool.flushDirty()
    check(first_ == 0 and r_ == 7 and read_pool(rd, k3 + "-p3") == {} and read_pool(rd, k3) == {COP: 250},
          "R: profile 3 active -> the switch settles first (0), then 7 from the p3 pool only; profile 1's file untouched")
    bridge.remove("profile:fn:key")
    bridge.remove("profile:epoch:" + k3)
    settle(U3)
    # review fix 3: the target - SkyyWardrobe's Server Setup pocket.target (config:fn:SkyyWardrobe "get") and per slot requip:pocketN

    @JImplements("java.util.function.Function")
    class WdCfgFn:
        val = "64"

        @JOverride
        def apply(self, o):
            if o is not None and len(o) == 2 and str(o[0]) == "get" and str(o[1]) == "pocket.target":
                return None if WdCfgFn.val is None else JString(WdCfgFn.val)
            return None
    write_pool(rd, k3, {COP: 1000})
    Pool.POOLS.clear()
    pmT = HMapJ()
    for s_ in (0, 1, 2):
        pmT.put(IntJ(s_), JString(COP))
    bridge.put("requip:pocket:" + k3, pmT)
    bridge.put("config:fn:SkyyWardrobe", WdCfgFn())
    ptg = player(backpack=[(MIN_S, 1)])
    TPlayers.P = ptg
    hbt = ptg.getInventory().getHotbar()
    setslot(hbt, 2, COP, 70)
    tot_t = pc(k3)[COP] + live(ptg, COP)
    n_ = Swp.pocketFill(ptg, k3, U3)
    check(n_ == 128 and slots(hbt)[0] == (COP, 64) and slots(hbt)[1] == (COP, 64) and slots(hbt)[2] == (COP, 70) and pc(k3)[COP] == 872
          and int(Swp.wardrobeTarget()) == 64,
          "R fix 3: SkyyWardrobe pocket.target 64 -> the empty reserved slots fill to 64 (not the max stack 100); a slot already at 70 untouched: %s" % slots(hbt)[:3])
    check(Swp.pocketFill(ptg, k3, U3) == 0, "R fix 3: at the target -> the next tick moves nothing (no top-up past 64)")
    pnm = HMapJ()
    pnm.put(IntJ(0), IntJ(20))
    pnm.put(IntJ(1), IntJ(0))
    bridge.put("requip:pocketN:" + k3, pnm)
    gone_t = 0   # what the test itself takes out of the slots (for the conservation check)
    gone_t += 64 - 10
    setslot(hbt, 0, COP, 10)
    gone_t += 64 - 5
    setslot(hbt, 1, COP, 5)
    n_ = Swp.pocketFill(ptg, k3, U3)
    check(n_ == 69 and slots(hbt)[0] == (COP, 20) and slots(hbt)[1] == (COP, 64),
          "R fix 3: requip:pocketN slot 0 = 20 -> 10 tops up to 20; slot 1 = 0 -> the Server Setup target 64: %s" % slots(hbt)[:2])
    pnm.put(IntJ(0), IntJ(500))
    gone_t += 20
    setslot(hbt, 0, None)
    n_ = Swp.pocketFill(ptg, k3, U3)
    check(n_ == 100 and slots(hbt)[0] == (COP, 100), "R fix 3: a target above the max stack (500) -> a full stack (100), never more")
    bridge.remove("requip:pocketN:" + k3)
    for v_, what_ in (("0", "0"), ("abc", "not a number"), (None, "no answer")):
        WdCfgFn.val = v_
        gone_t += int(hbt.getItemStack(JShort(1)).getQuantity())
        setslot(hbt, 1, None)
        n_ = Swp.pocketFill(ptg, k3, U3)
        want_ = 130 if v_ == "0" else 100   # the first run also tops slot 2 up from 70 (the 64 target held it) to 100
        check(n_ == want_ and slots(hbt)[1] == (COP, 100) and slots(hbt)[2] == (COP, 100),
              "R fix 3: pocket.target %s -> the item's max stack (100): moved %d" % (what_, n_))
    bridge.remove("config:fn:SkyyWardrobe")
    check(int(Swp.wardrobeTarget()) == 0, "R fix 3: no SkyyWardrobe config function -> 0 (= the max stack)")
    check(pc(k3).get(COP, 0) + live(ptg, COP) + gone_t == tot_t, "R fix 3: conservation through the target runs (pool + live copper unchanged)")
    # review fix 2: a damaged partial stack of the reserved item is never topped up
    hbt.setItemStackForSlot(JShort(2), IS(COP, 10, 5.0, 100.0, None))
    p0_ = pc(k3).get(COP, 0)
    n_ = Swp.pocketFill(ptg, k3, U3)
    d2_ = hbt.getItemStack(JShort(2))
    check(n_ == 0 and int(d2_.getQuantity()) == 10 and float(d2_.getDurability()) == 5.0 and pc(k3).get(COP, 0) == p0_
          and not bool(Swp.plainFresh(d2_)) and bool(Swp.plainFresh(IS(COP, 10))),
          "R fix 2: a damaged stack (durability 5 / 100) in a reserved slot is never topped up; plainFresh: damaged false, fresh true")
    bridge.remove("requip:pocket:" + k3)
    print("R. Requip hotbar block slots: empty + partial reserved slots fill to a full stack; another item / metadata / non-stacking / bag id / "
          "unknown / bad entries / unreserved never; no bag, other bag type, bags.refill off, settling -> nothing; mode Off still fills; "
          "tick path + sacks:fn:pocketFill; per profile; conserved + KEPT; fix 3 target (pocketN / pocket.target / max stack); fix 2 damaged never")

    # ---------------- D. sacks:fn:deposit
    U4 = UUID.fromString("00000000-0000-0000-0000-0000000d0717")
    k4 = str(U4)
    dd = os.path.join(SCRATCH, "d", "pools")
    fresh_pools(dd)
    CLog.PENDING.clear()
    CLog.FILE = Paths.get(os.path.join(SCRATCH, "d", "crafts.log"))
    write_pool(dd, k4, {COP: 630})
    pd_ = player(storage=[(COP, 30)], hotbar=[(COP, 20)], backpack=[(MIN_S, 1)])
    TPlayers.P = pd_
    st_, hb_, bp_ = pd_.getInventory().getStorage(), pd_.getInventory().getHotbar(), pd_.getInventory().getBackpack()
    setslot(bp_, 3, COP, 5)
    setslot(st_, 9, COP, 10, meta())
    inv_d0 = snap_inv(pd_)
    check(int(fn("sacks:fn:deposit", U4, COP, 100).longValue()) == 0 and snap_inv(pd_) == inv_d0 and pc(k4)[COP] == 630,
          "D fix 1: the 3-argument form (no hotbar slot) -> 0, nothing moved (it could take other stacks than the caller's)")
    check(int(fn("sacks:fn:deposit", U4, COP, 100, IntJ(0)).longValue()) == 10 and pc(k4)[COP] == 640 and slots(hb_)[0] == (COP, 10)
          and slots(st_)[0] == (COP, 30) and slots(bp_)[3] == (COP, 5),
          "D: bag room 10 (Normal Mining bag 640, pool 630) -> 10 from hotbar slot 0 only, the rest stays in the slot; storage / backpack untouched")
    check(int(fn("sacks:fn:deposit", U4, COP, 5, IntJ(0)).longValue()) == 0 and slots(hb_)[0] == (COP, 10), "D: the bag full -> 0, the slot keeps its stack")
    Pool.pool(k4).put(JString(COP), Long_(500))
    setslot(hb_, 4, COP, 9)
    tot = pc(k4)[COP] + live(pd_, COP)
    r_ = int(fn("sacks:fn:deposit", U4, COP, 50, IntJ(4)).longValue())
    check(r_ == 9 and slots(hb_)[0] == (COP, 10) and slots(hb_)[4] is None and pc(k4)[COP] == 509, "D: hotbar slot 4 (9 copper, 50 asked) -> 9; slot 0 kept")
    r_ = int(fn("sacks:fn:deposit", U4, COP, 4, IntJ(0)).longValue())
    check(r_ == 4 and slots(hb_)[0] == (COP, 6) and pc(k4)[COP] == 513, "D: 4 asked of slot 0's 10 -> 4, 6 stay")
    check(pc(k4)[COP] + live(pd_, COP) == tot, "D: conservation (pool + live)")
    setslot(hb_, 5, COP, 10, meta())
    hb_.setItemStackForSlot(JShort(6), IS(COP, 8, 5.0, 100.0, None))
    setslot(hb_, 7, SAP, 3)
    hb5 = slots(hb_)
    check(int(fn("sacks:fn:deposit", U4, COP, 5, IntJ(5)).longValue()) == 0 and int(fn("sacks:fn:deposit", U4, COP, 5, IntJ(6)).longValue()) == 0
          and int(fn("sacks:fn:deposit", U4, COP, 5, IntJ(7)).longValue()) == 0 and int(fn("sacks:fn:deposit", U4, COP, 5, IntJ(8)).longValue()) == 0
          and slots(hb_) == hb5 and float(hb_.getItemStack(JShort(6)).getDurability()) == 5.0 and pc(k4)[COP] == 513,
          "D: a metadata stack / a damaged stack (fix 2) / another item / an empty slot -> 0, untouched")
    check(int(fn("sacks:fn:deposit", U4, COP, 50, IntJ(99)).longValue()) == 0 and int(fn("sacks:fn:deposit", U4, COP, 5, JString("x")).longValue()) == 0
          and int(fn("sacks:fn:deposit", U4, COP, 5, IntJ(-1)).longValue()) == 0, "D: a slot outside the hotbar / a non-number slot / -1 -> 0")
    check(int(fn("sacks:fn:deposit", U4, SAP, 5, IntJ(7)).longValue()) == 0 and slots(hb_)[7] == (SAP, 3), "D: no bag of the item's type (Tree Sap, Foraging) -> 0")
    setslot(hb_, 8, MIN_S, 1)
    check(int(fn("sacks:fn:deposit", U4, MIN_S, 1, IntJ(8)).longValue()) == 0 and slots(hb_)[8] == (MIN_S, 1), "D: a Magic Bag id -> 0 (the bag stays)")
    setslot(hb_, 8, None)
    if Defs.catOf(BREAD) is None:
        pb_ = player(hotbar=[(BREAD, 4)], backpack=[(OMNI, 1)])
        TPlayers.P = pb_
        check(int(fn("sacks:fn:deposit", U4, BREAD, 4, IntJ(0)).longValue()) == 0 and live(pb_, BREAD) == 4, "D: cooked food (catOf null, bags.cookedFood off) -> 0")
        TPlayers.P = pd_
    else:
        print("note: Food_Bread is not cooked food in SackDefs - the cooked-food deposit check skipped")
    check(int(fn("sacks:fn:deposit", U4, COP, -3, IntJ(0)).longValue()) == 0 and int(fn("sacks:fn:deposit", U4, COP, JString("5"), IntJ(0)).longValue()) == 0
          and int(bridge.get("sacks:fn:deposit").apply(JString("x")).longValue()) == 0, "D: bad arguments -> 0")
    Pool.CLOSED = True
    check(int(fn("sacks:fn:deposit", U4, COP, 5, IntJ(0)).longValue()) == 0, "D: shutting down (paused) -> 0")
    Pool.CLOSED = False
    TPlayers.P = None
    check(int(fn("sacks:fn:deposit", U4, COP, 5, IntJ(0)).longValue()) == 0, "D: no player on this thread -> 0")
    # the SkyyWardrobe 0.2 giveBack pattern (WdOps.giveBack: takeOff the slot, deposit {u, id, qty}, put back qty - accepted) with 40 more
    # copper in the storage: the review's loss case - now nothing is lost (the deposit refuses, the whole stack goes back)
    pw_ = player(storage=[(COP, 40)], hotbar=[(COP, 64)], backpack=[(MIN_S, 1)])
    TPlayers.P = pw_
    Pool.pool(k4).put(JString(COP), Long_(500))
    tot_w = pc(k4)[COP] + live(pw_, COP)
    hbw = pw_.getInventory().getHotbar()
    x_ = hbw.getItemStack(JShort(0))
    hbw.removeItemStackFromSlot(JShort(0))
    acc_ = int(fn("sacks:fn:deposit", U4, COP, 64).longValue())
    if acc_ < 64:
        hbw.setItemStackForSlot(JShort(0), x_.withQuantity(JInt(64 - acc_)))
    check(acc_ == 0 and pc(k4)[COP] + live(pw_, COP) == tot_w and slots(pw_.getInventory().getStorage())[0] == (COP, 40) and slots(hbw)[0] == (COP, 64),
          "D fix 1: SkyyWardrobe 0.2's giveBack pattern (lift, 3 arguments, put back) -> 0 accepted, the storage 40 untouched, slot 64 back: nothing lost")
    # the same pattern WITH the slot (stack still lifted): the empty slot gives nothing -> 0, everything put back
    hbw.removeItemStackFromSlot(JShort(0))
    acc_ = int(fn("sacks:fn:deposit", U4, COP, 64, IntJ(0)).longValue())
    if acc_ < 64:
        hbw.setItemStackForSlot(JShort(0), x_.withQuantity(JInt(64 - acc_)))
    check(acc_ == 0 and pc(k4)[COP] + live(pw_, COP) == tot_w and slots(hbw)[0] == (COP, 64), "D fix 1: lifted first + the slot -> 0, nothing lost")
    # the fixed pattern: nothing lifted, {u, id, qty, slot} -> exactly that slot into the bags
    acc_ = int(fn("sacks:fn:deposit", U4, COP, 64, IntJ(0)).longValue())
    check(acc_ == 64 and pc(k4)[COP] == 564 and slots(hbw)[0] is None and slots(pw_.getInventory().getStorage())[0] == (COP, 40)
          and pc(k4)[COP] + live(pw_, COP) == tot_w, "D fix 1: the fixed pattern {u, id, 64, slot 0} -> 64 from slot 0 only; storage 40 untouched; conserved")
    TPlayers.P = pd_
    Pool.flushDirty()
    CLog.drain()
    lines_ = open(os.path.join(SCRATCH, "d", "crafts.log"), encoding="utf8").read().splitlines()
    check(read_pool(dd, k4) == {COP: 564} and any(l.endswith("BAG-DEPOSIT %s 9 (sacks:fn:deposit hotbar slot 4)" % COP) for l in lines_)
          and len([l for l in lines_ if "BAG-DEPOSIT" in l]) == 4, "D: the saved pool file says 564; crafts.log has the 4 BAG-DEPOSIT lines: %s" % lines_[-1:])
    print("D. sacks:fn:deposit: the hotbar slot is required (3 arguments -> 0), only that slot, bag room respected, metadata / damaged / other "
          "item / empty never, bag ids / other type / cooked food / paused / bad arguments -> 0; Wardrobe 0.2's pattern loses nothing; conserved; saved + logged")

    # ---------------- C. the craft bridges (stand-in recipe store; the engine's own CraftingRecipe / MaterialQuantity / removeMaterials)
    CRRc = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    MQc = JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
    BRc = JClass("com.hypixel.hytale.protocol.BenchRequirement")
    BTc = JClass("com.hypixel.hytale.protocol.BenchType")
    DAMc = JClass(DAMN)
    rmap = HMapJ()
    rstore = us.allocateInstance(FAKECLS)
    fm.set(rstore, DAMc(rmap))
    f_ = CRRc.class_.getDeclaredField("ASSET_STORE")
    f_.setAccessible(True)
    f_.set(None, rstore)
    FCCc = JClass("com.hypixel.hytale.server.core.asset.type.item.config.FieldcraftCategory")
    f_ = FCCc.class_.getDeclaredField("ASSET_MAP")
    f_.setAccessible(True)
    f_.set(None, DAMc(HMapJ()))
    MQArr, BRArr = JArray(MQc), JArray(BRc)
    WOOD_RT = "SkyyTestWood"
    custom_item(OAK, rts=[(WOOD_RT, 1)])
    custom_item(BIRCH, rts=[(WOOD_RT, 2)])
    custom_item(GEM)

    def mq(iid, q, rt=None):
        return MQc(JString(iid) if iid else None, JString(rt) if rt else None, None, JInt(q), None)

    def recipe(rid, out, ins, bench=None, tier=1, btype="Crafting", know=False):
        ia = MQArr(len(ins))
        for i_, x in enumerate(ins):
            ia[i_] = x
        po = mq(out, 1)
        oa = MQArr(1)
        oa[0] = po
        br = None
        if bench:
            br = BRArr(1)
            br[0] = BRc(BTc.valueOf(btype), JString(bench), None, JInt(tier), None)
        r_ = CRRc(ia, po, oa, JInt(1), br, JClass("java.lang.Float")(0.0).floatValue(), know, JInt(0))
        jfield(CRRc.class_, "id").set(r_, JString(rid))
        rmap.put(JString(rid), r_)
        return r_
    recipe("T_Sword", "Weapon_Sword_Copper", [mq(COP, 3), mq(SAP, 1)], "Weaponbench", 1)
    recipe("T_Sword2", "Weapon_Sword_Iron", [mq(COP, 5)], "Weaponbench", 2)
    recipe("T_Mace", "Weapon_Mace_Test", [mq(COP, 2)], "Furnace", 1, "Processing")
    recipe("T_Know", "Armor_Test_Chest", [mq(COP, 2)], "Weaponbench", 1, know=True)
    recipe("T_Plank", "Ingredient_Test_Plank", [mq(OAK, 2)], "Workbench", 1)
    recipe("T_Coll", "Armor_Coll_Head", [mq(COP, 1)], "Armorbench", 3)
    # 4 units: the engine pays a resource type greedily in slot order and needs the EXACT amount (3 units from 2-unit birch first = refused -
    # an engine rule benches and /craft share; noted in the round report)
    recipe("T_Pick", "Tool_Pickaxe_Test", [mq(None, 4, WOOD_RT), mq(COP, 1)], "Weaponbench", 1)
    recipe("T_Gem", "Weapon_Staff_Gem", [mq(GEM, 2)], "Weaponbench", 1)
    CPg.BENCHIDS = None
    U5 = UUID.fromString("00000000-0000-0000-0000-0000000c0717")
    k5 = str(U5)
    cd = os.path.join(SCRATCH, "c", "pools")
    fresh_pools(cd)
    CLog.PENDING.clear()
    CLog.FILE = Paths.get(os.path.join(SCRATCH, "c", "crafts.log"))
    write_pool(cd, k5, {COP: 10, SAP: 5, OAK: 2, BIRCH: 3})
    ACC1 = "Skyy_Accessory_Weaponbench_T1,Skyy_Accessory_Workbench_T1"
    bridge.put("acc:has:" + k5, JString(ACC1))
    bridge.put("coll:recipes:" + k5, JString("T_Coll"))
    pc_ = player(storage=[(COP, 4), (SAP, 1)], backpack=[(OMNI, 1)])
    TPlayers.P = pc_

    def jl(o_):
        return None if o_ is None else [str(x) for x in o_]
    sm_ = jl(fn("sacks:fn:craftList", U5, JString("smith")))
    check(sm_ == ["T_Coll", "T_Gem", "T_Pick", "T_Sword"],
          "C: craftList smith = Weaponbench T1 gear (sword, pickaxe, staff) + the collection recipe; not T2, not table-only, not unknown "
          "knowledge, not the plank: %s" % sm_)
    check(jl(fn("sacks:fn:craftList", U5, JString("craft"))) == ["T_Plank"] and jl(fn("sacks:fn:craftList", U5, None)) == ["T_Coll", "T_Gem", "T_Pick", "T_Plank", "T_Sword"]
          and jl(fn("sacks:fn:craftList", U5, JString("all"))) == jl(fn("sacks:fn:craftList", U5, None)) and jl(fn("sacks:fn:craftList", U5, JString("zzz"))) == [],
          "C: groups craft / all / null / unknown")
    bridge.put("acc:has:" + k5, JString("Skyy_Accessory_Weaponbench_T2,Skyy_Accessory_Workbench_T1"))
    check(jl(fn("sacks:fn:craftList", U5, JString("smith"))) == ["T_Coll", "T_Gem", "T_Pick", "T_Sword", "T_Sword2"], "C: the Weapon Bench II accessory -> + the tier-2 sword")
    bridge.put("acc:has:" + k5, JString("Skyy_Accessory_Workbench_T1"))
    check(jl(fn("sacks:fn:craftList", U5, JString("smith"))) == ["T_Coll"], "C: no Weapon Bench accessory -> only the collection recipe")
    bridge.put("acc:has:" + k5, JString(ACC1))
    TPlayers.P = None
    check(fn("sacks:fn:craftList", U5, JString("smith")) is None and fn("sacks:fn:craftHave", U5, JString("T_Sword")) is None, "C: no player on this thread -> null")
    TPlayers.P = pc_
    h_ = fn("sacks:fn:craftHave", U5, JString("T_Sword"))
    check(int(h_[0].longValue()) == 4 and jl(h_[1]) == [COP, SAP] and [int(x.longValue()) for x in h_[2]] == [14, 6] and [int(x.longValue()) for x in h_[3]] == [3, 1],
          "C: craftHave T_Sword: copper 14 (4 inventory + 10 bags) / 3, sap 6 / 1 -> 4 times: %s" % [str(x) for x in h_])
    h_ = fn("sacks:fn:craftHave", U5, JString("T_Pick"))
    check(jl(h_[1]) == ["res:" + WOOD_RT, COP] and int(h_[2][0].longValue()) == 8, "C: craftHave resource type: res:SkyyTestWood = 2 oak + 3 birch x2 = 8 units (%s)" % h_[2][0])
    check(fn("sacks:fn:craftHave", U5, JString("Nope")) is None, "C: craftHave unknown recipe -> null")
    Pool.CHANGEDAT.put(U5, Long_(int(System.currentTimeMillis())))
    h_ = fn("sacks:fn:craftHave", U5, JString("T_Sword"))
    check(int(h_[0].longValue()) == 1 and [int(x.longValue()) for x in h_[2]] == [4, 1], "C: craftHave while the profile settles -> the inventory only (copper 4, sap 1)")
    settle(U5)
    # pay: the inventory FIRST, then the bags
    tot_c, tot_s = live(pc_, COP) + pc(k5)[COP], live(pc_, SAP) + pc(k5)[SAP]
    r_ = fn("sacks:fn:craftPay", U5, JString("T_Sword"), IntJ(2))
    rc1 = str(r_[1])
    check(int(r_[0].longValue()) == 2 and r_[2] is None and live(pc_, COP) == 0 and pc(k5)[COP] == 8 and live(pc_, SAP) == 0 and pc(k5)[SAP] == 4,
          "C: craftPay 2 x sword (6 copper, 2 sap): the inventory's 4 copper + 1 sap first, then 2 copper + 1 sap from the bags: inv %d/%d pool %s (%s)"
          % (live(pc_, COP), live(pc_, SAP), pc(k5), r_[2]))
    check(live(pc_, COP) + pc(k5)[COP] == tot_c - 6 and live(pc_, SAP) + pc(k5)[SAP] == tot_s - 2, "C: paid == exactly 2 crafts (no more, no less)")
    e_ = Bridge.RECEIPTS.get(rc1)
    jm = lambda m_: dict((str(x.getKey()), int(x.getValue())) for x in m_.entrySet())
    check(e_ is not None and jm(e_[2]) == {COP: 4, SAP: 1} and jm(e_[3]) == {COP: 2, SAP: 1},
          "C: the receipt records inventory {copper 4, sap 1} and bags {copper 2, sap 1}")
    U6 = UUID.fromString("00000000-0000-0000-0000-0000000c0718")
    check(int(fn("sacks:fn:craftRefund", U6, JString(rc1)).longValue()) == 0 and int(fn("sacks:fn:craftRefund", U5, JString("r-nope")).longValue()) == 0
          and not bool(fn("sacks:fn:craftCommit", U6, JString(rc1))), "C: another player / an unknown receipt -> refund 0, commit false")
    r_ = int(fn("sacks:fn:craftRefund", U5, JString(rc1)).longValue())
    check(r_ == 8 and live(pc_, COP) == 4 and live(pc_, SAP) == 1 and pc(k5)[COP] == 10 and pc(k5)[SAP] == 5, "C: craftRefund -> exactly the receipt back (inventory 4 + 1, bags 2 + 1)")
    check(int(fn("sacks:fn:craftRefund", U5, JString(rc1)).longValue()) == 0 and pc(k5)[COP] == 10 and not bool(fn("sacks:fn:craftCommit", U5, JString(rc1))),
          "C: a second refund -> 0; commit after the refund -> false")
    r_ = fn("sacks:fn:craftPay", U5, JString("T_Sword"), IntJ(1))
    rc2 = str(r_[1])
    check(bool(fn("sacks:fn:craftCommit", U5, JString(rc2))) and int(fn("sacks:fn:craftRefund", U5, JString(rc2)).longValue()) == 0 and live(pc_, COP) == 1,
          "C: commit -> true; a refund after the commit -> 0 (inventory copper stays 1)")
    r_ = fn("sacks:fn:craftPay", U5, JString("T_Sword"), IntJ(1))
    rc3 = str(r_[1])
    Bridge.RECEIPTS.get(rc3)[4][0] = Bridge.RECEIPTS.get(rc3)[4][0] - 61000
    c0 = pc(k5).get(COP, 0) + live(pc_, COP)
    check(int(fn("sacks:fn:craftRefund", U5, JString(rc3)).longValue()) == 0 and pc(k5).get(COP, 0) + live(pc_, COP) == c0, "C: a refund 61 s after the payment -> 0")
    # refused payments move nothing
    write_pool(cd, k5, {COP: 10, SAP: 5, OAK: 2, BIRCH: 3})
    Pool.POOLS.clear()
    pc_ = player(storage=[(COP, 4), (SAP, 1)], backpack=[(OMNI, 1)])
    TPlayers.P = pc_
    inv0 = snap_inv(pc_)
    pool0 = pc(k5)
    for rid_, n_, why_ in (("T_Sword", 5, "not enough materials"), ("T_Sword2", 1, "needs its bench accessory"), ("T_Mace", 1, "only at its table"),
                           ("T_Know", 1, "not unlocked"), ("Nope", 1, "unknown recipe"), ("T_Sword", 0, "bad arguments"), ("T_Sword", 5000, "bad arguments")):
        r_ = fn("sacks:fn:craftPay", U5, JString(rid_), IntJ(n_))
        check(int(r_[0].longValue()) == 0 and r_[1] is None and why_ in str(r_[2]) and snap_inv(pc_) == inv0 and pc(k5) == pool0,
              "C: craftPay %s x%d refused (%s) - nothing moved" % (rid_, n_, r_[2]))
    r_ = bridge.get("sacks:fn:craftPay").apply(JString("x"))
    check(int(r_[0].longValue()) == 0 and r_[1] is None, "C: craftPay bad argument -> {0, null, reason}")
    Pool.CHANGEDAT.put(U5, Long_(int(System.currentTimeMillis())))
    r_ = fn("sacks:fn:craftPay", U5, JString("T_Sword"), IntJ(1))
    check(int(r_[0].longValue()) == 0 and "paused" in str(r_[2]) and snap_inv(pc_) == inv0, "C: craftPay while the profile settles -> paused, nothing moved")
    settle(U5)
    r_ = fn("sacks:fn:craftPay", U5, JString("T_Coll"), IntJ(1))
    check(int(r_[0].longValue()) == 1 and int(fn("sacks:fn:craftRefund", U5, JString(str(r_[1]))).longValue()) == 1 and snap_inv(pc_) == inv0 and pc(k5) == pool0,
          "C: a Collections recipe pays without its bench accessory (the /craft Collections tab rule); refunded exactly")
    # a resource-type input + metadata stacks of the same items never used
    setslot(pc_.getInventory().getStorage(), 10, COP, 20, meta())
    setslot(pc_.getInventory().getStorage(), 11, OAK, 5, meta())
    inv1 = snap_inv(pc_)
    r_ = fn("sacks:fn:craftPay", U5, JString("T_Pick"), IntJ(1))
    sl_ = slots(pc_.getInventory().getStorage())
    wood_units = pc(k5).get(OAK, 0) + 2 * pc(k5).get(BIRCH, 0)
    check(int(r_[0].longValue()) == 1 and sl_[10] == (COP, 20, "meta") and sl_[11] == (OAK, 5, "meta") and wood_units == 4 and live(pc_, COP) == 23,
          "C: T_Pick (4 wood units + 1 copper): the wood from the bags' oak / birch (units 8 -> %d), the copper from the plain inventory stack; "
          "the two metadata stacks (copper 20, oak 5) untouched: %s %s" % (wood_units, r_[2], sl_[:12]))
    rp_ = int(fn("sacks:fn:craftRefund", U5, JString(str(r_[1]))).longValue()) if r_[1] is not None else -1
    check(snap_inv(pc_) == inv1 and pc(k5) == pool0, "C: its refund -> inventory and bags exactly as before (%d items back)" % rp_)
    # ENGINE FACT behind plainCopy: the raw inventory offers the metadata oak (5) for a resource-type input; the plain copy does not
    raw_c = pc_.getInventory().getCombinedBackpackStorageHotbar()
    wood_mq = mq(None, 1, WOOD_RT)
    pcp_ = Bridge.plainCopy(Bridge.payConts(pc_.getInventory()))
    check(int(raw_c.countRemovableMaterial(wood_mq)) == 5 and int(pcp_[0].countRemovableMaterial(wood_mq)) == 0
          and int(pcp_[0].countRemovableMaterial(mq(COP, 1))) == 4,
          "C: ENGINE FACT: the raw inventory offers the metadata oak (5) for a resource-type input; the plain copy offers 0 (plain copper 4 kept)")
    # applyCopy: the copy's losses land on the real slots; a real slot that changed after the copy -> the reason, nothing more taken
    pa_ = player(storage=[(COP, 7), (SAP, 3)], backpack=[(OMNI, 1)])
    csa = Bridge.payConts(pa_.getInventory())
    pca = Bridge.plainCopy(csa)
    pca[0].removeItemStackFromSlot(JShort(9 + 0), JInt(5))     # backpack (9 slots) first, then storage slot 0 = copper
    check(Bridge.applyCopy(pca, csa) is None and slots(pa_.getInventory().getStorage())[0] == (COP, 2) and slots(pa_.getInventory().getStorage())[1] == (SAP, 3),
          "C: applyCopy: 5 copper the copy lost -> taken from the real storage slot 0 (7 -> 2), nothing else")
    pcb = Bridge.plainCopy(csa)
    pcb[0].removeItemStackFromSlot(JShort(9 + 1), JInt(3))
    pa_.getInventory().getStorage().removeItemStackFromSlot(JShort(1), JInt(2))   # the real slot changed after the copy
    check("changed" in str(Bridge.applyCopy(pcb, csa)) and slots(pa_.getInventory().getStorage())[1] == (SAP, 1),
          "C: applyCopy refuses when a real slot holds less than the copy lost (the caller then rolls back)")
    # the only copper is a metadata stack and the bags hold none -> refused, untouched
    write_pool(cd, k5, {SAP: 5})
    Pool.POOLS.clear()
    pm_ = player(storage=[(SAP, 1)], backpack=[(OMNI, 1)])
    setslot(pm_.getInventory().getStorage(), 5, COP, 30, meta())
    TPlayers.P = pm_
    invm = snap_inv(pm_)
    r_ = fn("sacks:fn:craftPay", U5, JString("T_Sword"), IntJ(1))
    check(int(r_[0].longValue()) == 0 and snap_inv(pm_) == invm and pc(k5) == {SAP: 5},
          "C: the only copper is a metadata stack -> refused (%s), the stack untouched (the engine never offers it)" % r_[2])
    # refuse(): an inventory changed after the snapshot is restored slot by slot, the bag part credited back
    pr2 = player(storage=[(COP, 6), (SAP, 2)], backpack=[(OMNI, 1)])
    write_pool(cd, k5, {COP: 3})
    Pool.POOLS.clear()
    cs_ = Bridge.payConts(pr2.getInventory())
    sn_ = Bridge.slotSnap(cs_)
    inv2 = snap_inv(pr2)
    pr2.getInventory().getStorage().removeItemStackFromSlot(JShort(0), JInt(4))
    setslot(pr2.getInventory().getStorage(), 7, GEM, 1)
    Pool.add(k5, COP, -2)
    bt_ = LHM()
    bt_.put(JString(COP), IntJ(2))
    r_ = Bridge.refuse(k5, "T_Sword", 1, "test", cs_, sn_, bt_)
    check(snap_inv(pr2) == inv2 and pc(k5) == {COP: 3} and int(r_[0].longValue()) == 0 and str(r_[2]) == "test",
          "C: refuse(): every slot back to the snapshot (a shrunk stack + an added one), the bag part credited back")
    # metaTouched: a plain stack changed -> false; a metadata stack changed -> true
    pr3 = player(storage=[(COP, 6)], backpack=[(OMNI, 1)])
    setslot(pr3.getInventory().getStorage(), 4, COP, 8, meta())
    cs3 = Bridge.payConts(pr3.getInventory())
    sn3 = Bridge.slotSnap(cs3)
    pr3.getInventory().getStorage().removeItemStackFromSlot(JShort(0), JInt(2))
    a3 = bool(Bridge.metaTouched(cs3, sn3))
    pr3.getInventory().getStorage().removeItemStackFromSlot(JShort(4), JInt(1))
    check(not a3 and bool(Bridge.metaTouched(cs3, sn3)), "C: metaTouched: a plain stack changed -> false; the metadata stack changed -> true")
    # giveSurplus: the bags first (up to the bag part), then the inventory; a surplus that does not fit -> the reason
    write_pool(cd, k5, {COP: 1})
    Pool.POOLS.clear()
    pg_ = player(backpack=[(OMNI, 1)])
    lf_, it_, bt2 = LHM(), LHM(), LHM()
    lf_.put(JString(COP), IntJ(5))
    it_.put(JString(COP), IntJ(4))
    bt2.put(JString(COP), IntJ(2))
    g_ = Bridge.giveSurplus(k5, pg_.getInventory().getCombinedBackpackStorageHotbar(), lf_, it_, bt2)
    check(g_ is None and pc(k5)[COP] == 3 and live(pg_, COP) == 3 and bt2.get(COP) is None and int(it_.get(COP)) == 1,
          "C: giveSurplus 5: 2 back to the bags (the whole bag part), 3 into the inventory; the receipt parts shrink to inventory 1 / bags 0")
    pfull = player(storage=[(GEM, 100)] * 36, hotbar=[(GEM, 100)] * 9, backpack=[(OMNI, 1)] + [(GEM, 100)] * 8)
    lf2 = LHM()
    lf2.put(JString(SAP), IntJ(3))
    g2 = Bridge.giveSurplus(k5, pfull.getInventory().getCombinedBackpackStorageHotbar(), lf2, LHM(), LHM())
    check(g2 is not None and "did not fit" in str(g2), "C: giveSurplus into a full inventory -> the reason (craftPay then refuses and rolls back)")
    # a refund into a FULL inventory: bag-home items spill into the bags; a non-bag item takes the drop path
    write_pool(cd, k5, {COP: 10, SAP: 5})
    Pool.POOLS.clear()
    pf2 = player(storage=[(COP, 3), (SAP, 1), (GEM, 2)], backpack=[(OMNI, 1)])
    TPlayers.P = pf2
    r_ = fn("sacks:fn:craftPay", U5, JString("T_Gem"), IntJ(1))
    r2_ = fn("sacks:fn:craftPay", U5, JString("T_Sword"), IntJ(1))
    check(int(r_[0].longValue()) == 1 and int(r2_[0].longValue()) == 1 and live(pf2, GEM) == 0 and live(pf2, COP) == 0, "C: paid a gem staff + a sword")
    for cont_ in (pf2.getInventory().getStorage(), pf2.getInventory().getHotbar(), pf2.getInventory().getBackpack()):
        for s_ in range(int(cont_.getCapacity())):
            if cont_.getItemStack(JShort(s_)) is None or cont_.getItemStack(JShort(s_)).isEmpty():
                setslot(cont_, s_, FOR_S, 1)
    pool_b = pc(k5)
    rr_ = int(fn("sacks:fn:craftRefund", U5, JString(str(r2_[1]))).longValue())
    check(rr_ == 4 and pc(k5)[COP] == pool_b[COP] + 3 and pc(k5)[SAP] == pool_b.get(SAP, 0) + 1 and live(pf2, COP) == 0,
          "C: a refund into a full inventory: copper 3 + sap 1 spill into the bags (never lost): %s -> %s" % (pool_b, pc(k5)))
    rg_ = int(fn("sacks:fn:craftRefund", U5, JString(str(r_[1]))).longValue())
    check(rg_ == 2 and live(pf2, GEM) == 0, "C: a non-bag item (gem) into a full inventory -> the drop path ran (bare JVM: no world -> logged, UNVERIFIED in game)")
    # review fix 2: a damaged stack is never paid with - the refund is a fresh stack, so paying with a damaged one would repair it for free
    write_pool(cd, k5, {COP: 10})
    Pool.POOLS.clear()
    pdm = player(backpack=[(OMNI, 1)])
    TPlayers.P = pdm
    std = pdm.getInventory().getStorage()
    std.setItemStackForSlot(JShort(0), IS(GEM, 2, 5.0, 100.0, None))
    r_ = fn("sacks:fn:craftPay", U5, JString("T_Gem"), IntJ(1))
    d0_ = std.getItemStack(JShort(0))
    check(int(r_[0].longValue()) == 0 and int(d0_.getQuantity()) == 2 and float(d0_.getDurability()) == 5.0,
          "C fix 2: only a damaged gem stack (durability 5 / 100) -> refused (%s), untouched" % r_[2])
    h_ = fn("sacks:fn:craftHave", U5, JString("T_Gem"))
    check(int(h_[0].longValue()) == 0 and int(h_[2][0].longValue()) == 0, "C fix 2: craftHave does not count the damaged stack")
    setslot(std, 1, GEM, 2)
    r_ = fn("sacks:fn:craftPay", U5, JString("T_Gem"), IntJ(1))
    d0_ = std.getItemStack(JShort(0))
    check(int(r_[0].longValue()) == 1 and int(d0_.getQuantity()) == 2 and float(d0_.getDurability()) == 5.0 and slots(std)[1] is None,
          "C fix 2: a fresh gem stack next to it -> paid from the fresh one; the damaged stack untouched")
    rr_ = int(fn("sacks:fn:craftRefund", U5, JString(str(r_[1]))).longValue())
    fresh_n = sum(int(std.getItemStack(JShort(s_)).getQuantity()) for s_ in range(36)
                  if std.getItemStack(JShort(s_)) is not None and not std.getItemStack(JShort(s_)).isEmpty() and bool(Swp.plainFresh(std.getItemStack(JShort(s_)))))
    check(rr_ == 2 and fresh_n == 2 and float(std.getItemStack(JShort(0)).getDurability()) == 5.0, "C fix 2: its refund -> 2 fresh gems back, the damaged stack still damaged")
    # review fix 4: a throw after the bag debit (applyCopy's removal from a real slot) -> refused, every slot + the bag part back; the next
    # payment is exact (the mirror never debits twice)
    write_pool(cd, k5, {COP: 10, SAP: 5})
    Pool.POOLS.clear()
    pbm = player(backpack=[(OMNI, 1)])
    boomS = TBoom(JShort(36))
    boomS.addItemStack(IS(COP, 4))
    boomS.addItemStack(IS(SAP, 1))
    jfield(TInv.class_, "s").set(pbm.getInventory(), boomS)
    TPlayers.P = pbm
    invb, poolb = snap_inv(pbm), pc(k5)
    TBoom.BOOM = True
    r_ = fn("sacks:fn:craftPay", U5, JString("T_Sword"), IntJ(2))
    check(not bool(TBoom.BOOM) and int(r_[0].longValue()) == 0 and r_[1] is None and "internal error" in str(r_[2]) and snap_inv(pbm) == invb and pc(k5) == poolb,
          "C fix 4: applyCopy throws after the bag debit -> refused (%s), inventory and bags exactly as before (%s)" % (r_[2], pc(k5)))
    r_ = fn("sacks:fn:craftPay", U5, JString("T_Sword"), IntJ(2))
    check(int(r_[0].longValue()) == 2 and live(pbm, COP) == 0 and live(pbm, SAP) == 0 and pc(k5) == {COP: 8, SAP: 4},
          "C fix 4: the next payment is exact (inventory 4 + 1 first, then 2 + 1 from the bags; pool %s)" % pc(k5))
    rf4 = int(fn("sacks:fn:craftRefund", U5, JString(str(r_[1]))).longValue())
    check(rf4 == 8 and live(pbm, COP) == 4 and live(pbm, SAP) == 1 and pc(k5) == poolb,
          "C fix 4: refunded exactly (%d back: inventory copper %d sap %d, pool %s)" % (rf4, live(pbm, COP), live(pbm, SAP), pc(k5)))
    # profile isolation: a receipt paid on profile 1 is refused after a switch to profile 3; a payment on p3 debits only p3
    write_pool(cd, k5, {COP: 10, SAP: 5})
    write_pool(cd, k5 + "-p3", {COP: 9, SAP: 2})
    Pool.POOLS.clear()
    pp_ = player(storage=[(SAP, 1)], backpack=[(OMNI, 1)])
    TPlayers.P = pp_
    r_ = fn("sacks:fn:craftPay", U5, JString("T_Sword"), IntJ(1))
    check(int(r_[0].longValue()) == 1, "C: profile 1 paid a sword (%s)" % r_[2])
    bridge.put("profile:fn:key", kfn)
    KeyFn.key = k5 + "-p3"
    bridge.put("profile:epoch:" + k5, Long_(9))
    r0_ = fn("sacks:fn:craftPay", U5, JString("T_Sword"), IntJ(1))
    check(int(r0_[0].longValue()) == 0 and "paused" in str(r0_[2]), "C: right after the switch to profile 3 -> paused")
    settle(U5)
    p1b = pc(k5)
    check(int(fn("sacks:fn:craftRefund", U5, JString(str(r_[1]))).longValue()) == 0 and pc(k5) == p1b, "C: a profile 1 receipt after the switch to profile 3 -> refused (0)")
    pp3 = player(storage=[(SAP, 1)], backpack=[(OMNI, 1)])
    TPlayers.P = pp3
    r3_ = fn("sacks:fn:craftPay", U5, JString("T_Sword"), IntJ(1))
    Pool.flushDirty()
    check(int(r3_[0].longValue()) == 1 and read_pool(cd, k5 + "-p3") == {COP: 6, SAP: 2} and read_pool(cd, k5) == {COP: 7, SAP: 5},
          "C: profile 3 pays from the p3 pool only (copper 9 -> 6; its sap from the inventory); profile 1's file keeps its own payment (7 / 5): %s %s"
          % (read_pool(cd, k5 + "-p3"), read_pool(cd, k5)))
    bridge.remove("profile:fn:key")
    bridge.remove("profile:epoch:" + k5)
    settle(U5)
    CLog.drain()
    clines = open(os.path.join(SCRATCH, "c", "crafts.log"), encoding="utf8").read().splitlines()
    check(any("CRAFT-PAY T_Sword x2" in l and "receipt " + rc1 in l for l in clines) and any("CRAFT-REFUND receipt " + rc1 in l for l in clines)
          and any("CRAFT-COMMIT receipt " + rc2 in l for l in clines) and any("CRAFT-REFUND-SPILL " + COP + " 3 into the bags" in l for l in clines)
          and any("CRAFT-PAY-REFUSED T_Sword x1 (test)" in l for l in clines),
          "C: crafts.log: CRAFT-PAY / CRAFT-REFUND / CRAFT-COMMIT / CRAFT-REFUND-SPILL / CRAFT-PAY-REFUSED lines")
    check(bridge.get("sacks:fn:craftList").apply(JString("x")) is None and bridge.get("sacks:fn:craftHave").apply(None) is None
          and int(bridge.get("sacks:fn:craftRefund").apply(JString("x")).longValue()) == 0 and not bool(bridge.get("sacks:fn:craftCommit").apply(JString("x")))
          and int(fn("sacks:fn:craftRefund", U5, Long_(3)).longValue()) == 0, "C: bad arguments -> null / 0 / false, nothing thrown")
    print("C. craft bridges: craftList (bench tier, knowledge, table-only, collections, groups), craftHave (inventory + bags, resource types), "
          "craftPay (inventory first, all or nothing, metadata never, refused = nothing moved), refund once / 60 s / never after commit / "
          "same player + profile, full inventory -> bags, conserved, per profile; refuse / metaTouched / giveSurplus executed; fix 2 damaged never; fix 4 throw rolls back")

    # ---------------- F. the /craft Smithing tab class filter (gear:fn:classShow)
    TPlayers.P = pc_
    cpg_ = us.allocateInstance(CPg.class_)
    jfield(CPg.class_, "known").set(cpg_, None)
    jfield(CPg.class_, "coll").set(cpg_, CPg.collectionRecipes(U5))
    bridge.put("acc:has:" + k5, JString(ACC1))

    def outs(lst):
        return sorted(str(r.getPrimaryOutput().getItemId()) for r in lst)
    all_smith = outs(cpg_.recipesFor("A:smith", U5))
    check(all_smith == ["Tool_Pickaxe_Test", "Weapon_Staff_Gem", "Weapon_Sword_Copper"] and int(cpg_.classHidden) == 0,
          "F: no gear:fn:classShow -> the Smithing tab shows everything: %s" % all_smith)

    @JImplements("java.util.function.Function")
    class ClassFn:
        mode = "hide-weapons"
        seen = []

        @JOverride
        def apply(self, o):
            iid = str(o[1])
            ClassFn.seen.append((str(o[0]), iid))
            if ClassFn.mode == "hide-weapons":
                return BoolJ.valueOf(not iid.startswith("Weapon_"))
            if ClassFn.mode == "null":
                return None
            if ClassFn.mode == "string":
                return JString("false")
            raise RuntimeError("boom")
    bridge.put("gear:fn:classShow", ClassFn())
    got_ = outs(cpg_.recipesFor("A:smith", U5))
    check(got_ == ["Tool_Pickaxe_Test"] and int(cpg_.classHidden) == 2 and (k5, "Weapon_Sword_Copper") in ClassFn.seen,
          "F: classShow FALSE for the two weapons -> hidden, classHidden 2, called with {UUID, output id}: %s" % got_)
    jfield(CPg.class_, "tab").set(cpg_, JString("A:smith"))
    b_ = UCBc()
    cpg_.smithNote(b_, False)
    check(str(CPg.smithNoteText(2)) in ucb_text(b_) and "2 hidden" in ucb_text(b_), "F: smithNote sets the materials line: %r" % str(CPg.smithNoteText(2)))
    b_ = UCBc()
    cpg_.smithNote(b_, True)
    b2_ = UCBc()
    jfield(CPg.class_, "tab").set(cpg_, JString("A:craft"))
    cpg_.smithNote(b2_, False)
    check("hidden" not in ucb_text(b_) and "hidden" not in ucb_text(b2_), "F: no note while searching or on another tab")
    n0 = len(ClassFn.seen)
    check(outs(cpg_.recipesFor("A:craft", U5)) == ["Ingredient_Test_Plank"] and int(cpg_.classHidden) == 0 and len(ClassFn.seen) == n0,
          "F: the Crafting tab is never filtered (classShow not even asked)")
    check(len(cpg_.searchRecipes(U5, "sword")) == 1, "F: search is not filtered (decision)")
    for m_ in ("null", "string", "throw"):
        ClassFn.mode = m_
        check(outs(cpg_.recipesFor("A:smith", U5)) == all_smith and int(cpg_.classHidden) == 0, "F: classShow answers %s -> everything shown" % m_)
    bridge.remove("gear:fn:classShow")
    # the build script's setup() publishes the 12 keys with the harness's mode numbers
    bsrc = open(os.path.join(HERE, "build_skyysacks_%s.py" % VERSION), encoding="utf8").read()
    pubs = re.findall(r'sbr0\.put\("(sacks:fn:[A-Za-z]+)", new \{PKG\}\.SackFn\((\d+)\)\)', bsrc)
    check([(k_, int(v_)) for k_, v_ in pubs] == [(k_, i_) for i_, k_ in enumerate(BRIDGE_KEYS)], "K: setup() publishes the 12 keys with these modes: %s" % pubs)
    print("F. /craft Smithing class filter: hides exactly classShow FALSE, counts them, note on the page builder; absent / null / non-Boolean / "
          "exception = shown; other tabs and search never filtered")


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
    ship_all = sorted(n for n in names if n.startswith(SHIP_PREFIX) or n == SET_PATH)
    hold_files = sorted(n for n in ship_all if n.startswith("Common/" + HOLD_DIR + "/"))
    ship = [n for n in ship_all if n not in hold_files]
    want = sorted(r for r in gen if r.startswith(SHIP_PREFIX) or r == SET_PATH)
    check(ship == want and len(ship) == 53, "G: besides the hold files the jar ships exactly the generator's %d sack art files (got %d): %s"
          % (len(want), len(ship), sorted(set(ship) ^ set(want))[:4]))
    touched = [SET_PATH, man["animations"]["player_lift_3p"], man["animations"]["player_lift_fps"]]
    bad = [n for n in ship if n not in touched and zn.read(n) != gen.get(n)]
    check(len([t for t in touched if t in ship]) == 3 and not bad,
          "G: every shipped art file the hold change does not touch is byte-identical to a fresh tools/art/make_bags.py run: %s" % bad[:4])
    check(not any("SkyyAccessories" in n for n in names if n.startswith("Common/")), "G: none of the Accessory Bag's files")
    ml = os.path.join(ROOT, "models-local", "art", "bags")
    if os.path.isdir(ml):
        dif = [r for r in ship if r not in touched and not os.path.isfile(os.path.join(ml, *r.split("/"))) or open(os.path.join(ml, *r.split("/")), "rb").read() != gen[r]]
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
    check(st["Parent"] == "Block" and "Common/" + a3 == man["animations"]["player_lift_3p"] and "Common/" + af == man["animations"]["player_lift_fps"]
          and ("Common/" + a3) in names and ("Common/" + af) in names and st["Animations"][lk]["Looping"] is False,
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
    return {"ship": ship_all, "man": man, "gen": gen, "hold_files": hold_files, "lift3": a3, "liftf": af}


# ============================================================================================================== H (0.7.16)
HOLD_KEYS = ("Idle", "Walk", "WalkBackward", "Run", "RunBackward", "Sprint", "Crouch", "CrouchWalk", "CrouchWalkBackward",
             "Jump", "JumpWalk", "JumpRun", "Fall", "FallFar", "FluidIdle", "FluidWalk", "FluidWalkBackward", "FluidRun")
HOLD_DIR = "Characters/Animations/Items/SkyySacks/Hold"
FPS_SHIFT = (12.0, 10.0, 0.0)     # tools/sacks_0_7_16_patch.py HOLD_FPS_ARM_SHIFT - restated here on purpose (independent check)
ARM_PITCH = -12.0                 # HOLD_3P_ARM_PITCH


def _q(d):
    import math
    q = (d["x"], d["y"], d["z"], d["w"])
    n = math.sqrt(sum(c * c for c in q))
    return tuple(c / n for c in q)


def _qmul(a, b):
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz)


def _qclose(a, b, tol=2e-4):
    return min(max(abs(a[i] - b[i]) for i in range(4)), max(abs(a[i] + b[i]) for i in range(4))) <= tol


def _strip(anim, node, chan_):
    d = json.loads(json.dumps(anim))
    (d["nodeAnimations"].get(node) or {}).pop(chan_, None)
    return d


def hold_checks(zn, G):
    import math
    names = set(zn.namelist())
    st = json.loads(zn.read(SET_PATH))
    with zipfile.ZipFile(ASSETS_ZIP) as az:
        blk = json.loads(az.read("Server/Item/Animations/Block.json").decode("utf-8-sig"))["Animations"]

        def van(p):
            return json.loads(az.read("Common/" + p).decode("utf-8-sig"))
        ent_bad, file_bad, seen = [], [], {}
        rx = (math.sin(math.radians(ARM_PITCH) / 2), 0.0, 0.0, math.cos(math.radians(ARM_PITCH) / 2))
        for k in HOLD_KEYS:
            e, v = st["Animations"].get(k), blk[k]
            if e is None or set(e) != set(v) or any(e[f] != v[f] for f in v if f not in ("FirstPerson", "ThirdPerson")):
                ent_bad.append(k + " entry")
                continue
            for side in ("FirstPerson", "ThirdPerson"):
                if side not in v:
                    continue
                want = HOLD_DIR + "/SkyySack_Hold_" + v[side].split("/")[-1]
                if e[side] != want or ("Common/" + want) not in names:
                    ent_bad.append("%s %s -> %s" % (k, side, e[side]))
                    continue
                if want in seen:
                    continue
                seen[want] = v[side]
                ours, orig = json.loads(zn.read("Common/" + want)), van(v[side])
                if side == "FirstPerson":
                    po, pn = orig["nodeAnimations"]["R-Arm"]["position"], ours["nodeAnimations"]["R-Arm"]["position"]
                    ok = len(po) == len(pn) and len(po) > 0 and all(
                        a_["time"] == b_["time"] and a_.get("interpolationType") == b_.get("interpolationType")
                        and all(abs(b_["delta"][c] - (a_["delta"][c] + FPS_SHIFT[i])) < 1e-3 for i, c in enumerate("xyz")) for a_, b_ in zip(po, pn))
                    if not ok or _strip(orig, "R-Arm", "position") != _strip(ours, "R-Arm", "position"):
                        file_bad.append(want)
                else:
                    ok = True
                    o2, n2 = orig, ours
                    for node in ("R-Arm", "L-Arm"):
                        ko, kn = orig["nodeAnimations"][node]["orientation"], ours["nodeAnimations"][node]["orientation"]
                        ok = ok and len(ko) == len(kn) and len(ko) > 0 and all(
                            a_["time"] == b_["time"] and a_.get("interpolationType") == b_.get("interpolationType")
                            and _qclose(_qmul(_q(a_["delta"]), rx), _q(b_["delta"])) for a_, b_ in zip(ko, kn))
                        o2, n2 = _strip(o2, node, "orientation"), _strip(n2, node, "orientation")
                    if not ok or o2 != n2:
                        file_bad.append(want)
        check(not ent_bad, "H: the 18 hold keys = Block's entries (Speed / Looping / Blending / KeepPrevious) with our hold paths: %s" % ent_bad[:4])
        check(len(seen) == 22 and sorted("Common/" + p for p in seen) == G["hold_files"],
              "H: 22 hold files, every one named by the set (no stray file): %d" % len(seen))
        check(not file_bad, "H: first person = vanilla + R-Arm position (12, 10, 0) only; third person = vanilla + both upper arms 12 deg up "
              "only (independent re-derivation from Assets.zip): %s" % file_bad[:4])
        # the first-person idle moved by a clear amount, next to where the vanilla Rifle sits
        bi = van(blk["Idle"]["FirstPerson"])["nodeAnimations"]["R-Arm"]["position"][0]["delta"]
        hi = json.loads(zn.read("Common/" + st["Animations"]["Idle"]["FirstPerson"]))["nodeAnimations"]["R-Arm"]["position"][0]["delta"]
        rif = van("Characters/Animations/Items/Dual_Handed/Rifle/Idle_FPS.blockyanim")["nodeAnimations"]["R-Arm"]["position"][0]["delta"]
        check(hi["x"] - bi["x"] >= 10 and hi["y"] - bi["y"] >= 8 and abs(hi["x"] - rif["x"]) < 5,
              "H: first-person idle R-Arm moved toward the centre and up, next to the vanilla Rifle's x: %s -> %s (Rifle %s)" % (bi, hi, rif))
        # SackLift: starts on the vanilla Item idle, ends exactly on the hold idle (no jump when the set's Idle takes over)
        lift_bad = []
        for lp, sa, hb in ((G["lift3"], "Characters/Animations/Items/Main_Handed/Item/Idle.blockyanim", st["Animations"]["Idle"]["ThirdPerson"]),
                           (G["liftf"], "Characters/Animations/Items/Main_Handed/Item/Idle_FPS.blockyanim", st["Animations"]["Idle"]["FirstPerson"])):
            la = json.loads(zn.read("Common/" + lp))
            A = van(sa)["nodeAnimations"]
            Bn = json.loads(zn.read("Common/" + hb))["nodeAnimations"]
            if not la["holdLastKeyframe"]:
                lift_bad.append(lp + " holdLastKeyframe")
            for node, ch in la["nodeAnimations"].items():
                for chn in ("position", "orientation"):
                    ks = ch.get(chn) or []
                    if not ks:
                        continue
                    ident = {"x": 0, "y": 0, "z": 0} if chn == "position" else {"x": 0, "y": 0, "z": 0, "w": 1}
                    a0 = ((A.get(node) or {}).get(chn) or [{"delta": ident}])[0]["delta"]
                    b0 = ((Bn.get(node) or {}).get(chn) or [{"delta": ident}])[0]["delta"]
                    first, last = ks[0]["delta"], ks[-1]["delta"]
                    if chn == "position":
                        okf = all(abs(first[c] - a0[c]) < 1e-3 for c in "xyz")
                        okl = all(abs(last[c] - b0[c]) < 1e-3 for c in "xyz")
                    else:
                        okf, okl = _qclose(_q(first), _q(a0), 1e-3), _qclose(_q(last), _q(b0), 1e-3)
                    if ks[0]["time"] != 0 or not okf:
                        lift_bad.append("%s %s %s start" % (lp.split("/")[-1], node, chn))
                    if ks[-1]["time"] != la["duration"] or not okl:
                        lift_bad.append("%s %s %s end" % (lp.split("/")[-1], node, chn))
        check(not lift_bad, "H: SackLift starts on the vanilla Item idle and ends exactly on the new hold idle (3rd + 1st person): %s" % lift_bad[:4])
        fl = json.loads(zn.read("Common/" + G["liftf"]))["nodeAnimations"]["R-Arm"]["position"]
        check(abs(fl[-1]["delta"]["y"] - hi["y"]) < 1e-3 and abs(fl[0]["delta"]["y"] - bi["y"]) < 1e-3,
              "H: first-person lift R-Arm y %s -> %s" % (fl[0]["delta"]["y"], fl[-1]["delta"]["y"]))
    op = "Common/Items/SkyySacks/SkyySacks_Bag_Open.blockyanim"
    check(zn.read(op) == G["gen"][op], "H: the open animation (SkyySacks_Bag_Open) is unchanged")
    print("H. hold pose: 18 keys -> 22 files re-derived from Assets.zip (1st person R-Arm %s -> %s; 3rd person arms %g deg up), SackLift ends on the "
          "new idle, open animation unchanged" % ((bi["x"], bi["y"], bi["z"]), (hi["x"], hi["y"], hi["z"]), -ARM_PITCH))
    return {"st": st}


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
    rbad = []
    for iid in BAG_IDS:
        it = ITEM.getAssetMap().getAsset(iid)
        rc = jf(ITEM, "recipeToGenerate").get(it) if it is not None else None
        if rc is None:
            rbad.append(iid + " no recipeToGenerate")
            continue
        if not rc.isKnowledgeRequired():
            rbad.append(iid + " KnowledgeRequired false")
        ins = sorted((str(x.getItemId()), int(x.getQuantity())) for x in rc.getInput())
        if iid.endswith("_Small") and ins != [("Ingredient_Fibre", 20), ("Ingredient_Stick", 4)]:
            rbad.append("%s inputs %s" % (iid, ins))
    check(not rbad, "V: the Item store's recipes: all 21 KnowledgeRequired (the Omni too), the Normal bags 20 Ingredient_Fibre + 4 Ingredient_Stick: %s" % rbad[:4])
    print("V. Item store recipes: 21 knowledge-gated (Omni included); 5 Normal = 20 fiber + 4 sticks")
    check(not got_bad, "V: the 21 items in the Item store carry the jar's Model / Texture / Icon / Animation / PlayerAnimationsId / Particles / "
          "FirstPersonParticles / SwapTo, toPacket() works: %s" % got_bad[:4])
    st = IPA.getAssetMap().getAsset("SkyySack")
    anims = dict((str(e.getKey()), e.getValue()) for e in st.getAnimations().entrySet()) if st is not None else {}
    check(st is not None and "SackLift" in anims and "Idle" in anims, "V: the SkyySack set is in the store with SackLift + the inherited Block keys (%d keys)" % len(anims))
    def _strs(o_):
        out_, k_ = [], o_.getClass()
        while k_ is not None:
            for f_ in k_.getDeclaredFields():
                if JClass("java.lang.reflect.Modifier").isStatic(f_.getModifiers()):
                    continue
                f_.setAccessible(True)
                v_ = f_.get(o_)
                if v_ is not None:
                    out_.append(str(v_))
            k_ = k_.getSuperclass()
        return out_
    hb_ = []
    jset_ = json.loads(zj.read(SET_PATH))
    for k in HOLD_KEYS:
        if k not in anims:
            hb_.append(k + " missing")
            continue
        got_ = _strs(anims[k])
        for side in ("FirstPerson", "ThirdPerson"):
            p_ = jset_["Animations"][k].get(side)
            if p_ and not any(p_ in g_ for g_ in got_):
                hb_.append("%s %s %s" % (k, side, got_[:3]))
    lift_ = _strs(anims["SackLift"]) if "SackLift" in anims else []
    check(not hb_ and any("SkyySack_Lift_FPS.blockyanim" in g_ for g_ in lift_) and "Swim" in anims,
          "V: the store's SkyySack set names our hold file for every hold key (1st + 3rd person), keeps SackLift and the inherited Block keys: %s" % hb_[:4])
    print("V. the SkyySack set in the store: %d hold keys on our SkyySacks/Hold files, SackLift kept, %d keys in all" % (len(HOLD_KEYS), len(anims)))
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
        ("hold file missing", "Server/Item/Animations/SkyyTestCtl_HoldFile.json",
         json.dumps({"Parent": "Block", "Animations": {"Idle": {"FirstPerson": "Characters/Animations/Items/SkyySacks/Hold/SkyyTestCtl_NoSuch_FPS.blockyanim",
                                                                "ThirdPerson": "Characters/Animations/Items/SkyySacks/Hold/SkyyTestCtl_NoSuch.blockyanim", "Looping": True}}}),
         "SkyyTestCtl_NoSuch", True),
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
    open(os.path.join(SCRATCH, MARK), "w").write("SkyySacks 0.7.17 harness scratch\n")
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
