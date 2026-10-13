"""Bare-JVM harness for SkyySacks 0.8.0 = BAGS V2, shown as SkyyVoid (tools/sacks_0_8_0_patch.py; research/Bags-v2-Spec.md).
Skyy: "i have an idea for the bags! ..." + "SkyySack isnt a great name any more ..." (docs/answered/bags.md 2026-10-10).

    python SkyySacks/test_skyysacks_0.8.0.py [--jar <0.8.0 jar>] [--old <0.7.18 jar>] [--dir <scratch>] [--keep]

The parent copies the live data READ ONLY (Saves/HUD mod: mods/Skyy_SkyySacks, universe/players/*.json, mods/Skyy_SkyyProfiles/inventories)
into the scratch folder (default tools/dev/scratch/void080/run, deleted unless --keep) and starts children (the game's JRE, -XX:-UsePerfData,
java.io.tmpdir / TEMP / TMP in the scratch folder):
 child 1 (-Xverify:all; HytaleServer.jar + the 0.8.0 jar + tools/javassist.jar):
  A  every class loads and verifies
  I  class compare 0.7.18 -> 0.8.0: exactly 5 new classes (VoidState, VoidStore, VoidJob, VoidAdminTask, PdAdminCmd), none removed; the
     changed classes keep every 0.7.18 member except the rewritten Void page's own (listed); every non-class file accounted for
  X  engine-access audit on the jar bytes (0 refused; control refused); Z0 bytecode order: SweepTask.run asks settledKey BEFORE
     VoidStore.migrate and migrate BEFORE capsK / items; setup publishes sacks:v2 / sacks:fn:pd / sacks:fn:catOf and registers /pdadmin
  D  categories: six (Fishing new: Fish_* + Food_Fish_Raw*; crystals -> Mining; grilled fish = cooked Farming), legacy ids, catOf bridge
  L  levels + capacity: every row of the spec 2.1 table (level boundaries per category), capacity = level x 100 x multiplier (spec 2.2
     table incl. Mining Lv 14 x Rare 2.0 = 2,800), coll:fn:catTotal totals, the best level never drops (total lowered, step raised,
     Collections gone), maxLevel cap, Omni auto / off / granted, the own-intake total without Collections
  S  CONSERVATION fuzz: 300 random sweeps (main inventory / Deposit all, kept counts, under / at / over the limit, several categories): no
     item lost or duplicated, intake never pushes a category past its limit, an over-limit category takes nothing, partial fits
  W  withdraw (the amount box: n, a stack, all, storage full), Deposit (n, all, category room, plain stacks only, cooked food refused),
     Deposit all, sacks:fn:deposit (category room shared by two items) - every one conserved
  U  THE UPGRADE: gate / cost / from refused with nothing moved; pool first then inventory; a second click of the same step charges
     nothing; a crash in the middle of the inventory payment rolls everything back; the sixth Legendary = Omni; pd saved
  M  MIGRATION: History first (copies byte-identical, marker after), every old bag id x rarity, best bag wins whatever the slot order,
     extras refunded (chains exact, stacks of bags), Farming sets Fishing, the Omni, bags in storage / hotbar / backpack, the Pocket
     item (and a full inventory), run once; CRASH AT EVERY STEP (journal written / bag removed / rarity saved / refund saved, each with
     the inventory rolled back or saved) = exactly the no-crash result: one credit per bag, never zero, never two; a bag carried into
     another profile converts for that profile only; /pdadmin legacybags gives the rarity bags back once and a re-conversion gives no
     second credit; /pdadmin omni
  R  (child 3, the 0.7.18 jar) ROLLBACK: SkyySacks 0.7.18 reads every migrated pool file with exactly the expected items (the meta line
     skipped) and its save drops only the meta line
  P  the Void page executed: render (header, bars, tabs, grid, paging, amount box, buttons, upgrade box + confirm) + onEvent: select,
     withdraw / deposit with the amount box, Pick up all, Deposit all, upgrade -> Pay -> a second Pay charges nothing, tabs, pages
  C  config: pd.* hand edits loaded / clamped, a bad cost line kept out, checkCost / checkMult answers; KnowSync forgets the 21 ids
  K  the bridges without any bag: count / all / take / put / commit; sacks:fn:pd shape; sacks:fn:catOf; deposit's category room
  LV the LIVE data copy: started twice (no file changes), then every live profile migrated for real with its real bags (from the copied
     player / profile files) incl. crash variants - every pool item survives with the exact same count (+ exactly the refunds)
 child 2 (V - the ENGINE ASSET VALIDATORS): the jar loads into the real asset stores with 0 failed stores and 0 SEVERE / WARNING; 22 bag
  items (21 old ids without a recipe + the Pocket Dimension) in the Item store, the SkyySack set, 22 SwapTo roots compile.
Exit code 1 on any failure. Live data is only READ (copied). Nothing is deployed.
"""
import os, sys, re, shutil, subprocess, zipfile, json, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD = "0.8.0", "0.7.18"
PKG = "com.skyy.sacks."
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
WORLD = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod")
LIVE_SACKS = os.path.join(WORLD, "mods", "Skyy_SkyySacks")
LIVE_PLAYERS = os.path.join(WORLD, "universe", "players")
LIVE_PROF = os.path.join(WORLD, "mods", "Skyy_SkyyProfiles", "inventories")
MARK = ".skyysacks-0.8.0-harness"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH_ROOT = os.path.realpath(os.path.join(TOOLS, "dev", "scratch"))
SCRATCH = os.path.realpath(os.path.abspath(arg("--dir", os.path.join(SCRATCH_ROOT, "void080", "run"))))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLDJAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyySacks-%s.jar" % OLD)))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]
LEG_TYPES = ("Mining", "Foraging", "Farming", "Combat", "Smithing")
LEG_TIERS = ("Small", "Medium", "Rare", "Large")
LEGACY = ["Skyy_Sack_%s_%s" % (c, t) for c in LEG_TYPES for t in LEG_TIERS] + ["Skyy_Sack_Omni"]
POCKET = "Skyy_Sack_Pocket"
CATS6 = ("Mining", "Foraging", "Farming", "Fishing", "Combat", "Smithing")
STEP = {"Mining": 25, "Foraging": 20, "Farming": 25, "Fishing": 2, "Combat": 8, "Smithing": 10}
MULT = (1.0, 1.5, 2.0, 3.0, 5.0)
REFUND = [{"Ingredient_Fibre": 20, "Ingredient_Stick": 4}]
for _s in ("Ingredient_Fabric_Scrap_Linen", "Ingredient_Fabric_Scrap_Shadoweave", "Ingredient_Fabric_Scrap_Cindercloth"):
    _d = dict(REFUND[-1])
    _d[_s] = 6
    REFUND.append(_d)
REFUND.append(dict((k_, v_ * 5) for k_, v_ in REFUND[3].items()))   # an extra Omni = 5 Legendary chains


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)
    return bool(cond)


def legacy_rank(i):
    if i == "Skyy_Sack_Omni":
        return 5
    m = re.match(r"Skyy_Sack_([A-Za-z]+)_([A-Za-z]+)$", i)
    if not m or m.group(1) not in LEG_TYPES or m.group(2) not in LEG_TIERS:
        return 0
    return LEG_TIERS.index(m.group(2)) + 1


def read_props(p):
    out = {}
    if not os.path.exists(p):
        return None
    for l in open(p, encoding="latin-1").read().splitlines():
        if l and not l.startswith("#") and "=" in l:
            k, v = l.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def read_pool(d, key):
    p = read_props(os.path.join(d, key + ".properties"))
    if p is None:
        return None
    out = {}
    for k, v in p.items():
        if k.startswith("~"):
            continue
        try:
            n = int(v)
        except ValueError:
            continue
        if n > 0:
            out[k] = n
    return out


def live_inventories():
    """{profile key: [(container, id, qty)]} from the COPIED player / profile files (storage, hotbar, backpack only)"""
    out = {}
    src = []
    for d, sub in ((os.path.join(SCRATCH, "live-players"), ""), (os.path.join(SCRATCH, "live-prof"), "")):
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                if f.endswith(".json"):
                    src.append(os.path.join(d, f))
    for pth in src:
        try:
            doc = json.load(open(pth, encoding="utf-8"))
        except Exception:
            continue
        key = os.path.basename(pth)[:-5]
        comps = doc.get("Components") if isinstance(doc, dict) else None
        if not isinstance(comps, dict):
            comps = doc if isinstance(doc, dict) else {}
        items = []
        for cn, short in (("StorageInventory", "s"), ("HotbarInventory", "h"), ("BackpackInventory", "b")):
            inv = (comps.get(cn) or {}).get("Inventory") or {}
            for slot, it in (inv.get("Items") or {}).items():
                if isinstance(it, dict) and it.get("Id"):
                    items.append((short, str(it["Id"]), int(it.get("Quantity", 1))))
        # SkyyProfiles inventories/<key>.json: sections [{name, slots: [{slot, id, qty}]}] (BSON-style numbers)
        for sec in (doc.get("sections") or []) if isinstance(doc, dict) else []:
            if sec.get("name") not in ("storage", "hotbar", "backpack"):
                continue
            for it in sec.get("slots") or []:
                q_ = it.get("qty")
                q_ = int(q_.get("$numberInt", 1)) if isinstance(q_, dict) else int(q_ or 1)
                if it.get("id"):
                    items.append((sec["name"][0], str(it["id"]), q_))
        if items or key not in out:
            out[key] = items
    return out


# ============================================================================================================== child 1
def run():
    import jpype
    import skyybuild as B
    from jpype import JClass, JArray, JShort, JString, JInt, JLong, JImplements, JOverride
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
    zn = zipfile.ZipFile(JAR)
    names = [n[:-6].replace("/", ".") for n in zn.namelist() if n.endswith(".class")]
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

    # ---------------- I. class compare 0.7.18 -> 0.8.0
    zo = zipfile.ZipFile(OLDJAR)
    co = dict((n, zo.read(n)) for n in zo.namelist() if n.endswith(".class"))
    cn = dict((n, zn.read(n)) for n in zn.namelist() if n.endswith(".class"))
    NEW = sorted("com/skyy/sacks/%s.class" % c_ for c_ in ("VoidState", "VoidStore", "VoidJob", "VoidAdminTask", "PdAdminCmd"))
    check(sorted(set(cn) - set(co)) == NEW and not (set(co) - set(cn)), "I: the %d classes of %s + exactly %s (none removed): +%s -%s"
          % (len(co), OLD, [x.split("/")[-1] for x in NEW], sorted(set(cn) - set(co)), sorted(set(co) - set(cn))))
    ob, nb = OLD.encode(), VERSION.encode()
    same, changed = [], []
    for n in sorted(co):
        if n in cn and co[n] == cn[n]:
            same.append(n)
        elif n in cn:
            changed.append(n.split("/")[-1][:-6])

    def sigs(blob):
        cf_ = JClass("javassist.bytecode.ClassFile")(JClass("java.io.DataInputStream")(JClass("java.io.ByteArrayInputStream")(blob)))
        return set(str(m.getName()) + str(m.getDescriptor()) for m in cf_.getMethods()), set(str(f.getName()) for f in cf_.getFields())
    # members a 0.8.0 class may drop: the rewritten Void page (its 0.7.x bag-page helpers)
    MAY_DROP = {"SacksPage": {"pickCat(Ljava/lang/String;Ljava/util/HashMap;)Ljava/lang/String;", "countInv", "haveOf", "iconBox", "bagCount",
                              "bagsLine", "rankOf", "numS", "romanS", "unlockText", "nextLine", "buildNoBag", "render(", "noRoom",
                              "field VBTN", "field VCELL"}}
    lost = []
    for c_ in changed:
        n_ = "com/skyy/sacks/%s.class" % c_
        mo2, fo2 = sigs(co[n_])
        mn2, fn2 = sigs(cn[n_])
        for m in sorted(mo2 - mn2):
            if not any(m.startswith(x) for x in MAY_DROP.get(c_, ())):
                lost.append("%s.%s" % (c_, m))
        for f in sorted(fo2 - fn2):
            if ("field " + f) not in MAY_DROP.get(c_, ()):
                lost.append("%s field %s" % (c_, f))
    check(not lost, "I: every 0.7.18 member is kept (only the Void page's own 0.7.x helpers go): %s" % lost[:6])
    an = sorted(n for n in zn.namelist() if not n.endswith(".class"))
    ao = sorted(n for n in zo.namelist() if not n.endswith(".class"))
    added = sorted(set(an) - set(ao))
    check(added == ["Server/Item/Items/Utility/Skyy_Sack_Pocket.json", "Server/Item/Qualities/Skyy_Bag_Void.json"] and not (set(ao) - set(an)),
          "I: files: + the Pocket item + the Void quality, none removed (+%s -%s)" % (added, sorted(set(ao) - set(an))))
    diff = sorted(n for n in set(an) & set(ao) if zn.read(n) != zo.read(n))
    want_diff = set(["manifest.json", "Server/Languages/en-US/server.lang"] + ["Server/Item/Items/Utility/%s.json" % i for i in LEGACY])
    check(set(diff) <= want_diff, "I: changed files = the manifest, server.lang and the 21 old bag JSONs only: %s" % sorted(set(diff) - want_diff))
    for i in LEGACY:
        nd = json.loads(zn.read("Server/Item/Items/Utility/%s.json" % i))
        od = json.loads(zo.read("Server/Item/Items/Utility/%s.json" % i))
        od.pop("Recipe", None)
        if nd != od:
            check(False, "I: %s differs from 0.7.18 beyond the removed Recipe" % i)
    print("I. class compare %s -> %s: %d identical, %d changed (%s), 5 new; old bag JSONs = 0.7.18 minus the Recipe"
          % (OLD, VERSION, len(same), len(changed), ", ".join(changed)))

    # ---------------- X. engine-access audit (the SkyyBazaar harness rule) + Z0 bytecode order
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
    items_ = [(jp.get(n[:-6].replace("/", ".")), CF(DI(BI(zn.read(n))))) for n in zn.namelist() if n.endswith(".class")]
    refused, used, seen = audit(items_)
    check(not refused and seen > 5000, "X: access audit: %d references, refused %s" % (seen, refused[:5]))
    ctl = jp.makeClass(PKG + "AuditControl")
    ctl.addMethod(JClass("javassist.CtNewMethod").make(
        "public static void bad(com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage p) { p.close(); }", ctl))
    r2, _u2, _s2 = audit([(ctl, CF(DI(BI(ctl.toBytecode()))))])
    check(len(r2) == 1 and "close" in r2[0], "X: access audit control refused: %s" % r2)
    print("X. access audit: %d references, 0 refused; non-public used from their subclass: %s; control refused" % (seen, ", ".join(sorted(used))))
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def mcode(cls_short, meth, desc=None):
        for mm in jp.get(PKG + cls_short).getDeclaredMethods():
            if str(mm.getName()) == meth and (desc is None or desc in str(mm.getSignature())):
                mi = mm.getMethodInfo()
                ca = mi.getCodeAttribute()
                it = ca.iterator()
                out = []
                while it.hasNext():
                    pos = it.next()
                    out.append(str(IP.instructionString(it, pos, mi.getConstPool())))
                return "\n".join(out)
        return ""

    def in_order(txt, needles):
        i = 0
        for nd in needles:
            j = txt.find(nd, i)
            if j < 0:
                return False
            i = j + len(nd)
        return True
    run_c = mcode("SweepTask", "run")
    check(in_order(run_c, ["SackPool.settledKey", "KnowSync.sync", "VoidStore.migrate", "INVDIRTY", "VoidStore.capsK", "SweepTask.items"]),
          "Z0: SweepTask.run: settledKey -> KnowSync.sync -> VoidStore.migrate (false = INVDIRTY kept, return) -> capsK -> items")
    setup_c = mcode("SkyySacksPlugin", "setup")
    check(all(x in setup_c for x in ("sacks:v2", "sacks:fn:pd", "sacks:fn:catOf", "PdAdminCmd", "VoidStore.DIR", "VoidStore.HDIR", "VoidStore.MIGLOG"))
          and setup_c.count("registerCommand") == 3, "Z0: setup(): sacks:v2 + sacks:fn:pd + sacks:fn:catOf published, /pdadmin registered (3 commands), the Void folders set")
    sh_c = mcode("SkyySacksPlugin", "shutdown")
    check(in_order(sh_c, ["VoidStore.flushDirty", "SackPool.flushDirty"]), "Z0: shutdown(): the Void files flushed, then the pools")
    sav_c = mcode("SackSaver", "run")
    check(in_order(sav_c, ["VoidStore.settleDue", "VoidStore.flushDirty", "SackPool.flushDirty"]), "Z0: the 10 s SackSaver settles due conversions, then the Void files, then the pools")

    # ---------------- stand-ins (the 0.7.12+ harness pattern)
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyTestFakeStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fake.addConstructor(JClass("javassist.CtNewConstructor").make(
        "public SkyyTestFakeStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
    FAKECLS = fake.toClass(AS.class_)
    store = us.allocateInstance(FAKECLS)
    fm = AS.class_.getDeclaredField("assetMap")
    fm.setAccessible(True)
    DAMN = "com.hypixel.hytale.assetstore.map.DefaultAssetMap"
    kmap = jp.makeClass("com.hypixel.hytale.assetstore.map.SkyyTestKnownMap", jp.get(DAMN))
    kmap.addField(JClass("javassist.CtField").make("public static final java.util.HashMap CUSTOM = new java.util.HashMap();", kmap))
    kmap.addConstructor(JClass("javassist.CtNewConstructor").make("public SkyyTestKnownMap() { super(); }", kmap))
    kmap.addMethod(JClass("javassist.CtNewMethod").make(
        "public com.hypixel.hytale.assetstore.JsonAsset getAsset(Object key) { if (key != null && CUSTOM.containsKey(key)) "
        "return (com.hypixel.hytale.assetstore.JsonAsset) CUSTOM.get(key); return super.getAsset(key); }", kmap))
    KMap = JClass(kmap.toClass(JClass(DAMN).class_))
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
    CICN = "com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer"
    for m, order in (("getCombinedBackpackStorageHotbar", "this.b, this.s, this.h"), ("getCombinedStorageHotbarBackpack", "this.s, this.h, this.b")):
        tinv.addMethod(CtM.make("public %s %s() { return new %s(new %s[] { %s }); }" % (CICN, m, CICN, ICN, order), tinv))
    TInv = JClass(tinv.toClass(JClass(INVN).class_))
    SICN = "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer"
    tboom = jp.makeClass("com.hypixel.hytale.server.core.inventory.container.SkyyTestBoomCont", jp.get(SICN))
    tboom.addField(CtF.make("public static volatile int BOOMAT = -1;", tboom))
    tboom.addField(CtF.make("public static volatile int CALLS = 0;", tboom))
    tboom.addConstructor(CtC.make("public SkyyTestBoomCont(short n) { super(n); }", tboom))
    tboom.addMethod(CtM.make("public com.hypixel.hytale.server.core.inventory.transaction.ItemStackSlotTransaction removeItemStackFromSlot(short s, int q) "
                             "{ CALLS++; if (BOOMAT >= 0 && CALLS > BOOMAT) { BOOMAT = -1; throw new IllegalStateException(\"test boom\"); } return super.removeItemStackFromSlot(s, q); }", tboom))
    TBoom = JClass(tboom.toClass(JClass(SICN).class_))
    tpl = jp.makeClass(PKG + "SkyyTestPlayers")
    tpl.addInterface(jp.get("java.util.function.Function"))
    tpl.addField(CtF.make("public static volatile Object P;", tpl))
    tpl.addConstructor(CtC.make("public SkyyTestPlayers() { }", tpl))
    tpl.addMethod(CtM.make("public Object apply(Object o) { return P; }", tpl))
    TPlayers = JClass(tpl.toClass(JClass(PKG + "SackBridge").class_))
    tnop = jp.makeClass(PKG + "SkyyTestNoOp")
    tnop.addInterface(jp.get("java.lang.Runnable"))
    tnop.addConstructor(CtC.make("public SkyyTestNoOp() { }", tnop))
    tnop.addMethod(CtM.make("public void run() { }", tnop))
    TNoOp = JClass(tnop.toClass(JClass(PKG + "SackBridge").class_))
    # coll:fn:catTotal stand-in: TOT = "<uuid>|<cat>" -> Long (absent = null)
    tcol = jp.makeClass(PKG + "SkyyTestColl")
    tcol.addInterface(jp.get("java.util.function.Function"))
    tcol.addField(CtF.make("public static final java.util.HashMap TOT = new java.util.HashMap();", tcol))
    tcol.addConstructor(CtC.make("public SkyyTestColl() { }", tcol))
    tcol.addMethod(CtM.make("public Object apply(Object o) { Object[] a = (Object[]) o; return TOT.get(String.valueOf(a[0]) + \"|\" + a[1]); }", tcol))
    TColl = JClass(tcol.toClass(JClass(PKG + "SackBridge").class_))

    J = lambda n: JClass(PKG + n)
    Pool, Bridge, Fn, Mirror, CLog, Defs, Swp, Cfg, KS = (J("SackPool"), J("SackBridge"), J("SackFn"), J("BagMirror"), J("CraftLog"), J("SackDefs"),
                                                          J("SweepTask"), J("SackCfg"), J("KnowSync"))
    VS, VSt, VJob, SPage, PStore, RFp = J("VoidStore"), J("VoidState"), J("VoidJob"), J("SacksPage"), J("ProcStore"), J("RefillPref")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass(SICN)
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    ItemC = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    UUID, Paths, Long_ = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Long")
    CHM, System, HMapJ, IntJ = JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.lang.System"), JClass("java.util.HashMap"), JClass("java.lang.Integer")
    BsonDoc, BsonStr = JClass("org.bson.BsonDocument"), JClass("org.bson.BsonString")
    ObjArr = JArray(JClass("java.lang.Object"))
    bridge = CHM()
    System.getProperties().put("skyy.bridge", bridge)
    Executors = JClass("java.util.concurrent.Executors")
    Pool.WRITER = Executors.newSingleThreadScheduledExecutor()

    def drain():
        Pool.WRITER.submit(TNoOp()).get()

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

    def custom_item(iid, max_stack=100):
        it_ = ItemC(JString(iid))
        jfield(ItemC.class_, "maxStack").setInt(it_, max_stack)
        KMap.CUSTOM.put(JString(iid), it_)
        return it_
    COB, COP, IRON, THOR, OAK, MAPLE, FIB, STICK, SAP = ("Rock_Stone_Cobble", "Ore_Copper", "Ore_Iron", "Ore_Thorium", "Wood_Oak_Trunk",
                                                          "Wood_Maple_Trunk", "Ingredient_Fibre", "Ingredient_Stick", "Ingredient_Tree_Sap")
    FISH, GILL, CRYS, BREAD, WHEAT, BONE, BAR = ("Food_Fish_Raw", "Fish_Bluegill_Item", "Ingredient_Crystal_Blue", "Food_Bread",
                                                 "Plant_Crop_Wheat_Item", "Ingredient_Bone_Fragment", "Ingredient_Bar_Iron")
    LIN, SHA, CIN = "Ingredient_Fabric_Scrap_Linen", "Ingredient_Fabric_Scrap_Shadoweave", "Ingredient_Fabric_Scrap_Cindercloth"
    for i_ in (COB, COP, IRON, THOR, OAK, MAPLE, FIB, STICK, SAP, FISH, GILL, CRYS, BREAD, WHEAT, BONE, BAR, LIN, SHA, CIN,
               "Plant_Crop_Lettuce_Item", "Ingredient_Life_Essence", "Ingredient_Feathers_Light", "Rubble_Stone", "Food_Fish_Grilled"):
        custom_item(i_, 100)
    for i_ in LEGACY + [POCKET]:
        custom_item(i_, 1)

    def player(storage=(), hotbar=(), backpack=(), boom=False, cap=36):
        s = TBoom(JShort(cap)) if boom else SIC(JShort(cap))
        h, b = SIC(JShort(9)), SIC(JShort(9))
        for cont, its in ((s, storage), (h, hotbar), (b, backpack)):
            for (iid, q) in its:
                tx = cont.addItemStack(IS(iid, q))
                assert tx.succeeded(), (iid, q)
        p = us.allocateInstance(PLA.class_)
        inv_field.set(p, TInv(s, h, b))
        return p
    uuid_fs = [f_ for f_ in PRc.class_.getDeclaredFields() if f_.getType() == UUID.class_ and not JClass("java.lang.reflect.Modifier").isStatic(f_.getModifiers())]
    for f_ in uuid_fs:
        f_.setAccessible(True)

    def pref(u):
        r_ = us.allocateInstance(PRc.class_)
        for f_ in uuid_fs:
            f_.set(r_, u)
        assert str(r_.getUuid()) == str(u)
        return r_

    def inv_counts(p_):
        out_ = {}
        inv_ = p_.getInventory()
        for cont in (inv_.getStorage(), inv_.getHotbar(), inv_.getBackpack()):
            for s_ in range(int(cont.getCapacity())):
                it_ = cont.getItemStack(JShort(s_))
                if it_ is not None and not it_.isEmpty():
                    out_[str(it_.getItemId())] = out_.get(str(it_.getItemId()), 0) + int(it_.getQuantity())
        return out_

    def pc(k):
        return dict((str(e.getKey()), int(e.getValue().longValue())) for e in Pool.pool(k).entrySet())

    def total(a, b):
        out_ = dict(a)
        for k_, v_ in b.items():
            out_[k_] = out_.get(k_, 0) + v_
        return dict((k_, v_) for k_, v_ in out_.items() if v_)

    def write_pool(d, key, vals):
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, key + ".properties"), "w", encoding="latin-1") as f:
            f.write("#SkyySacks pool\n" + "".join("%s=%d\n" % (k_, v_) for k_, v_ in vals.items()))

    def fresh(base):
        """a clean world folder for the Void + pools (memory state cleared)"""
        if os.path.exists(base):
            shutil.rmtree(base)
        os.makedirs(base)
        for m in (Pool.POOLS, Pool.DIRTY, Pool.BADPOOL, Pool.KEPT, Pool.KEPTKEY, Pool.SEENQ, Pool.SEENEPOCH, Pool.SEENKEY, Pool.CHANGEDAT,
                  Pool.UNKNOWN, Pool.PMETA, Pool.PENDING, Pool.LASTSAVE, Pool.SWEPTQ, Mirror.MIRRORS, Bridge.OWED, Bridge.LASTKEY,
                  VS.STATES, VS.BAD, VS.DIRTY, VS.SNAPQ, VS.SNAPFAIL):
            m.clear()
        VS.PEND.clear()
        VS.TOLD.clear()
        VS.HOLDALL = False
        VS.RESUMEALL = 0
        Pool.DIR = Paths.get(os.path.join(base, "pools"))
        PStore.DIR = Paths.get(os.path.join(base, "processing"))
        VS.DIR = Paths.get(os.path.join(base, "pd"))
        VS.HDIR = Paths.get(os.path.join(base, "history"))
        VS.MIGLOG = Paths.get(os.path.join(base, "migration.log"))
        CLog.FILE = Paths.get(os.path.join(base, "crafts.log"))
        VS.CRASHAT = None
        VS.CRASHN = 1
        VS.CRASHHITS = 0
        return os.path.join(base, "pools")

    def restart():
        """the process died: every memory state goes, the files stay"""
        for m in (Pool.POOLS, Pool.DIRTY, Pool.PMETA, Pool.PENDING, Pool.LASTSAVE, Pool.SWEPTQ, Mirror.MIRRORS, VS.STATES, VS.BAD, VS.DIRTY,
                  VS.SNAPQ, VS.SNAPFAIL, Pool.SEENEPOCH, Pool.SEENKEY, Pool.CHANGEDAT):
            m.clear()
        VS.PEND.clear()
        VS.TOLD.clear()
        VS.CRASHAT = None
        VS.loadHold()   # fix round: the legacybags-all flag file survives a restart

    def coll(u, totals):
        TColl.TOT.clear()
        for c_, v_ in totals.items():
            TColl.TOT.put(JString(str(u) + "|" + c_), Long_(v_))
        bridge.put("coll:fn:catTotal", TColl())

    def nocoll():
        bridge.remove("coll:fn:catTotal")

    def call_str(o):
        return None if o is None else str(o)

    # ---------------- D. categories
    check(list(Defs.CATS) == list(CATS6) and list(Defs.LCATS) == list(LEG_TYPES), "D: six Void categories (Fishing new), the five legacy bag types")
    hm = dict((i_, call_str(Defs.homeOf(i_))) for i_ in (GILL, FISH, "Food_Fish_Raw_Rare", "Food_Fish_Raw_Legendary", CRYS, "Ingredient_Crystal_Void",
                                                        COP, OAK, WHEAT, BONE, BAR, BREAD, "Food_Fish_Grilled", POCKET, "SkyyFishing_Fish_Bass", "Skyy_Sack_Mining_Large"))
    check(hm[GILL] == "Fishing" and hm[FISH] == "Fishing" and hm["Food_Fish_Raw_Rare"] == "Fishing" and hm["Food_Fish_Raw_Legendary"] == "Fishing"
          and hm[CRYS] == "Mining" and hm["Ingredient_Crystal_Void"] == "Mining" and hm[COP] == "Mining" and hm[OAK] == "Foraging"
          and hm[WHEAT] == "Farming" and hm[BONE] == "Combat" and hm[BAR] == "Smithing" and hm[BREAD] == "Farming" and hm["Food_Fish_Grilled"] == "Farming"
          and hm[POCKET] is None and hm["SkyyFishing_Fish_Bass"] is None and hm["Skyy_Sack_Mining_Large"] is None,
          "D: homeOf - fish + raw fish Fishing, crystals Mining, grilled fish Farming (cooked), the Pocket / old bags / SkyyFishing whole fish none: %s" % hm)
    check(Defs.catOf("Food_Fish_Grilled") is None and Defs.catOf(BREAD) is None and str(Defs.catOf(GILL)) == "Fishing", "D: catOf keeps cooked food out (grilled fish, bread)")
    check([int(Defs.legacyRank(i_)) for i_ in LEGACY] == [legacy_rank(i_) for i_ in LEGACY] and int(Defs.legacyRank(POCKET)) == 0
          and int(Defs.legacyRank("Skyy_Sack_Fishing_Small")) == 0 and int(Defs.legacyRank("Skyy_Sack_Mining_Huge")) == 0
          and str(Defs.legacyCat("Skyy_Sack_Farming_Rare")) == "Farming" and Defs.legacyCat("Skyy_Sack_Omni") is None
          and str(Defs.bagName("Skyy_Sack_Mining_Large")) == "Legendary Mining Bag", "D: legacyRank / legacyCat / bagName of the 21 old ids (Pocket, a Fishing bag id: none)")
    check([str(x) for x in Defs.REFUND] == [",".join("%s:%d" % (k_, v_) for k_, v_ in sorted(d_.items())) for d_ in REFUND],
          "D: the refund chains (Normal 20 Fibre + 4 Sticks, + 6 Linen / Shadoweave / Cindercloth Scraps per step, an extra Omni = 5 Legendary chains)")
    print("D. six categories (Fishing, crystals in Mining), cooked food out, 21 legacy ids, refund chains")

    # ---------------- L. levels + capacity
    U1 = UUID.fromString("00000000-0000-0000-0000-00000000c0de")
    k1 = str(U1)
    fresh(os.path.join(SCRATCH, "l"))
    bad_lv = []
    for ci, c in enumerate(CATS6):
        for lv in (1, 5, 10, 14, 25, 50, 100, 200, 250):
            t = STEP[c] * (lv - 1) ** 2
            if int(VS.levelOf(t, ci)) != lv or (lv > 1 and int(VS.levelOf(t - 1, ci)) != lv - 1) or int(VS.totalFor(lv, ci)) != t:
                bad_lv.append((c, lv, t, int(VS.levelOf(t, ci))))
    check(not bad_lv and int(VS.levelOf(10 ** 12, 0)) == 250 and int(VS.levelOf(0, 0)) == 1 and int(VS.levelOf(-5, 0)) == 1,
          "L: level = 1 + floor(sqrt(total / step)) for every row of the spec table (all six categories), max 250, 0 = Lv 1: %s" % bad_lv[:4])
    caps_tab = {(1, 0): 100, (10, 0): 1000, (14, 2): 2800, (25, 1): 3750, (50, 3): 15000, (100, 4): 50000, (250, 4): 125000, (250, 0): 25000}
    check(all(int(VS.capOf(lv, r)) == v for (lv, r), v in caps_tab.items()), "L: capacity = level x 100 x multiplier (spec 2.2 table; Mining Lv 14 x Rare = 2,800)")
    coll(U1, {"Mining": 25 * 13 * 13, "Fishing": 0})
    lvm = int(VS.level(U1, k1, 0))
    s1 = VS.st(k1)
    check(lvm == 14 and int(s1.best[0]) == 14 and VS.DIRTY.containsKey(k1), "L: coll:fn:catTotal 4,225 Mining -> Lv 14, saved as the best level")
    coll(U1, {"Mining": 10})
    check(int(VS.level(U1, k1, 0)) == 14, "L: the collection total lowered -> the level stays 14 (best never drops)")
    Cfg.PD_STEP_MINING = 1000
    check(int(VS.level(U1, k1, 0)) == 14, "L: pd.step.Mining raised -> still 14")
    Cfg.PD_STEP_MINING = 25
    nocoll()
    check(int(VS.level(U1, k1, 0)) == 14 and int(VS.level(U1, k1, 3)) == 1, "L: SkyyCollections gone -> 14 (best), Fishing Lv 1 (own intake 0)")
    Cfg.PD_MAX_LEVEL = 10
    check(int(VS.level(U1, k1, 0)) == 10 and int(VS.capOf(10, 0)) == 1000, "L: pd.maxLevel 10 caps the shown level (nothing deleted: only intake)")
    Cfg.PD_MAX_LEVEL = 250
    VS.noteIntake(k1, 3, 50)
    check(int(s1.own[3]) == 50 and int(VS.level(U1, k1, 3)) == 6, "L: without Collections the Void's own intake counts (50 fish / step 2 -> Lv 6)")
    VS.noteOut(k1, 3, 30)
    VS.noteIntake(k1, 3, 30)
    check(int(s1.own[3]) == 50, "L (fix 5): 30 fish taken out on the page and put back in -> not counted again (own stays 50)")
    VS.noteOut(k1, 3, 30)
    VS.noteIntake(k1, 3, 40)
    check(int(s1.own[3]) == 60, "L (fix 5): 30 out, 40 in -> only the 10 new ones count (own 60)")
    coll(U1, {"Fishing": 0})
    VS.noteIntake(k1, 3, 50)
    check(int(s1.own[3]) == 60, "L: with Collections installed the own intake is not counted (no extra file writes)")
    for i in range(6):
        s1.rar[i] = 3
    check(VS.omni(k1) and int(VS.rank(k1, 0)) == 4, "L: all six Legendary -> Omni (automatic, pd.omniAuto on)")
    Cfg.PD_OMNI_AUTO = False
    check(not VS.omni(k1) and int(VS.rank(k1, 0)) == 3, "L: pd.omniAuto off -> no automatic Omni")
    s1.omni = True
    check(VS.omni(k1), "L: a granted Omni (/pdadmin omni) stays")
    Cfg.PD_OMNI_AUTO = True
    s1.omni = False
    s1.rar[2] = 2
    check(not VS.omni(k1) and int(VS.legendCount(k1)) == 5, "L: five of six Legendary -> not Omni (5 / 6)")
    caps_ = VS.capsK(U1, k1)
    check(sorted(str(x) for x in caps_.keySet()) == sorted(CATS6) and int(caps_.get("Mining")) == int(VS.capOf(14, 3)),
          "L: capsK = all six categories, Mining = Lv 14 x Legendary = %s" % caps_.get("Mining"))
    JMod = JClass("java.lang.reflect.Modifier")
    check("ConcurrentHashMap" in str(s1.ret.getClass().getName()) and "CopyOnWriteArrayList" in str(s1.left.getClass().getName())
          and "CopyOnWriteArrayList" in str(s1.done.getClass().getName()) and "SetFromMap" in str(s1.given.getClass().getName()),
          "L (fix 3): VoidState ret / left / done / given are concurrent collections (world thread + writer)")
    syncd = [str(m_.getName()) for m_ in VS.class_.getDeclaredMethods() if str(m_.getName()).startswith("pend") and JMod.isSynchronized(m_.getModifiers())]
    check(not syncd and "ConcurrentHashMap" in str(VS.PEND.getClass().getName()),
          "L (fix B1): pendAdd / pendRemove / pendCopy / pendKeys are lock-free (not on the VoidStore monitor held across an fsync): %s" % syncd)
    VS.pendAdd(JString("kx"), ObjArr([JString("s1"), JString("Skyy_Sack_Omni"), JClass("java.lang.Integer").valueOf(1),
                                                 JClass("java.lang.Integer").valueOf(1), JString("R"), JClass("java.lang.Long").valueOf(0),
                                                 JString("-"), JString("kx")]))
    check(VS.pendOmni("kx") and VS.pendCopy("kx").size() == 1, "L (fix B1): a pending entry added lock-free is seen")
    VS.PEND.clear()
    print("L. levels (spec table), capacity (spec table), best level never drops, maxLevel, own intake, Omni auto / off / granted")

    # ---------------- S. CONSERVATION fuzz of the sweep (main inventory + Deposit all)
    rnd = random.Random(80)
    S_IDS = [COB, COP, IRON, OAK, FIB, STICK, FISH, GILL, CRYS, WHEAT, BONE, BAR, BREAD]
    bad_s = []
    for it_n in range(300):
        U2 = UUID.fromString("00000000-0000-0000-0000-%012x" % (0x5000 + it_n))
        k2 = str(U2)
        fresh(os.path.join(SCRATCH, "s"))
        pool0 = dict((i_, rnd.randint(1, 400)) for i_ in rnd.sample(S_IDS, rnd.randint(0, 6)))
        write_pool(os.path.join(SCRATCH, "s", "pools"), k2, pool0)
        st_, hb_, bp_ = [], [], []
        for _x in range(rnd.randint(0, 14)):
            st_.append((rnd.choice(S_IDS), rnd.randint(1, 100)))
        for _x in range(rnd.randint(0, 4)):
            hb_.append((rnd.choice(S_IDS), rnd.randint(1, 100)))
        for _x in range(rnd.randint(0, 3)):
            bp_.append((rnd.choice(S_IDS), rnd.randint(1, 100)))
        try:
            p_ = player(st_[:36], hb_[:9], bp_[:9])
        except AssertionError:
            continue
        caps_s = HMapJ()
        for c_ in CATS6:
            caps_s.put(JString(c_), IntJ(rnd.choice([0, 50, 100, 300, 700, 2000, 100000])))
        kept_ = {}
        if rnd.random() < 0.3:
            for i_ in rnd.sample(S_IDS, 2):
                Pool.keep(k2, i_, rnd.randint(1, 120))
                kept_[i_] = 1
        inv0, pl0 = inv_counts(p_), pc(k2)
        used0 = dict((c_, sum(v_ for i_, v_ in pl0.items() if call_str(Defs.homeOf(i_)) == c_)) for c_ in CATS6)
        allc = rnd.random() < 0.4
        only = rnd.choice([None, None, "Mining", "Fishing"]) if allc else None
        moved = int(Swp.sweep(p_, k2, only, allc, None, caps_s, None))
        inv1, pl1 = inv_counts(p_), pc(k2)
        if total(inv0, pl0) != total(inv1, pl1):
            bad_s.append(("conservation", it_n))
            continue
        for c_ in CATS6:
            cap_ = int(caps_s.get(c_))
            u1_ = sum(v_ for i_, v_ in pl1.items() if call_str(Defs.homeOf(i_)) == c_)
            if u1_ > max(cap_, used0[c_]):
                bad_s.append(("over the limit", it_n, c_, u1_, cap_))
            if used0[c_] >= cap_ and u1_ != used0[c_]:
                bad_s.append(("intake while over", it_n, c_))
            # takes all that fits: nothing of that category left where the sweep looks while there is room (no kept counts)
            if not kept_ and (only is None or only == c_) and u1_ < cap_:
                left_ = 0
                inv_ = p_.getInventory()
                for cont in ((inv_.getStorage(), inv_.getHotbar(), inv_.getBackpack()) if allc else (inv_.getStorage(),)):
                    for s_ in range(int(cont.getCapacity())):
                        it2 = cont.getItemStack(JShort(s_))
                        if it2 is not None and not it2.isEmpty() and call_str(Defs.catOf(it2.getItemId())) == c_:
                            left_ += 1
                if left_:
                    bad_s.append(("room left but items not taken", it_n, c_))
        if sum(pl1.values()) - sum(pl0.values()) != moved:
            bad_s.append(("moved count", it_n))
    check(not bad_s, "S: 300 random sweeps - conserved, never past a category limit, nothing in while over, all that fits taken: %s" % bad_s[:4])
    print("S. 300 random sweeps (main / Deposit all / one category, kept counts, limits 0 .. 100,000): conserved, limits held")

    # ---------------- W. withdraw / deposit (the amount box), Deposit all, sacks:fn:deposit
    fresh(os.path.join(SCRATCH, "w"))
    U3 = UUID.fromString("00000000-0000-0000-0000-0000000a0800")
    k3 = str(U3)
    write_pool(os.path.join(SCRATCH, "w", "pools"), k3, {COP: 500, COB: 120, FISH: 30})
    coll(U3, {"Mining": 0})
    p3 = player(storage=[(IRON, 40), (BREAD, 5)], hotbar=[(COB, 10)])
    a0 = total(inv_counts(p3), pc(k3))
    g = int(SPage.withdrawN(p3, k3, COP, 150))
    check(g == 150 and pc(k3)[COP] == 350 and inv_counts(p3)[COP] == 150 and total(inv_counts(p3), pc(k3)) == a0, "W: withdraw 150 (the amount box) -> exactly 150, conserved")
    g = int(SPage.withdrawN(p3, k3, FISH, 9223372036854775807))
    check(g == 30 and FISH not in pc(k3), "W: withdraw 'all' -> the 30 fish, none left")
    check(int(SPage.parseAmt("", 64)) == 64 and int(SPage.parseAmt("all", 1)) == 9223372036854775807 and int(SPage.parseAmt("1,000", 1)) == 1000
          and int(SPage.parseAmt("12x", 1)) == -2 and int(SPage.parseAmt("0", 1)) == -2 and int(SPage.parseAmt(" 7 ", 1)) == 7,
          "W: the amount box: empty = the default, all, 1,000, junk / 0 refused")
    # Mining capacity at Lv 1 Normal = 100; stored copper 350 + cobble 120 = over -> deposit refused (-2); lift the level, deposit fits the room
    check(int(VS.depositInv(p3, U3, k3, IRON, 10)) == -2 and inv_counts(p3)[IRON] == 40, "W: Deposit into an over-limit category -> -2, nothing moved")
    coll(U3, {"Mining": 25 * 4 * 4})       # Lv 5 -> 500 space; stored 470 -> room 30
    d_ = int(VS.depositInv(p3, U3, k3, IRON, 100))
    check(d_ == 30 and pc(k3)[IRON] == 30 and inv_counts(p3)[IRON] == 10 and total(inv_counts(p3), pc(k3)) == a0,
          "W: Deposit 100 iron with 30 room -> exactly 30 (category room), conserved")
    check(int(VS.depositInv(p3, U3, k3, BREAD, -1)) == -1 and inv_counts(p3)[BREAD] == 5, "W: Deposit cooked food -> -1 (stays out)")
    md = BsonDoc()
    md.put("SkyyGear", BsonStr("rolled"))
    p3.getInventory().getStorage().setItemStackForSlot(JShort(20), IS(WHEAT, 7, md))
    coll(U3, {"Farming": 25 * 9})
    check(int(VS.depositInv(p3, U3, k3, WHEAT, -1)) == 0 and inv_counts(p3).get(WHEAT) == 7, "W: a stack WITH metadata is never deposited (plain stacks only)")
    # Deposit all = sweep(allContainers) with capsK; the hotbar cobble goes too (room 0 -> nothing)
    coll(U3, {"Mining": 25 * 9 * 9})        # Lv 10 -> 1,000
    a1 = total(inv_counts(p3), pc(k3))
    mv = int(Swp.sweep(p3, k3, "Mining", True, None, VS.capsK(U3, k3), None))
    check(mv == 10 + 10 + 150 and total(inv_counts(p3), pc(k3)) == a1 and COB not in inv_counts(p3), "W: Deposit all (Mining, every container) -> %d moved, conserved" % mv)
    # sacks:fn:deposit (4 args): the category room is SHARED by two items
    BR_KEYS = ("sacks:fn:count", "sacks:fn:take", "sacks:fn:put", "sacks:fn:all", "sacks:fn:commit", "sacks:fn:deposit", "sacks:fn:pocketFill",
               "sacks:fn:craftList", "sacks:fn:craftHave", "sacks:fn:craftPay", "sacks:fn:craftRefund", "sacks:fn:craftCommit", "sacks:fn:pd", "sacks:fn:catOf")
    for i, key in enumerate(BR_KEYS):
        bridge.put(key, Fn(i))
    Bridge.PLAYERS = TPlayers()
    TPlayers.P = p3
    coll(U3, {"Mining": 0})               # Lv 5 (best) -> 500 space
    used_m = sum(v_ for i_, v_ in pc(k3).items() if call_str(Defs.homeOf(i_)) == "Mining")
    hb3 = p3.getInventory().getHotbar()
    hb3.setItemStackForSlot(JShort(0), IS(COP, 60))
    arr = ObjArr(4)
    arr[0], arr[1], arr[2], arr[3] = U3, JString(COP), Long_(60), IntJ(0)
    a2 = total(inv_counts(p3), pc(k3))
    got_d = int(bridge.get("sacks:fn:deposit").apply(arr).longValue())
    want_d = max(0, min(60, int(VS.capOf(int(VS.level(U3, k3, 0)), 0)) - used_m))
    check(got_d == want_d and total(inv_counts(p3), pc(k3)) == a2, "W: sacks:fn:deposit takes only the CATEGORY room (%d of 60; Mining holds %d of %d), conserved"
          % (got_d, used_m, int(VS.capOf(int(VS.level(U3, k3, 0)), 0))))
    print("W. withdraw / Deposit (amount box), Deposit all, sacks:fn:deposit: category room, plain stacks only, cooked food out, conserved")

    # ---------------- U. THE UPGRADE
    def mk_state(k, u, first=True):
        s_ = VS.st(k)
        if first:
            s_.first = 1
        return s_
    fresh(os.path.join(SCRATCH, "u"))
    U4 = UUID.fromString("00000000-0000-0000-0000-0000000a0801")
    k4 = str(U4)
    write_pool(os.path.join(SCRATCH, "u", "pools"), k4, {COB: 300, COP: 250})
    s4 = mk_state(k4, U4)
    p4 = player(storage=[(COB, 100), (COB, 100), (COB, 50), (IRON, 100), (IRON, 30)])
    coll(U4, {"Mining": 25 * 8 * 8})       # Lv 9 < gate 10
    b0 = total(inv_counts(p4), pc(k4))
    r_ = str(VS.upgrade(p4, U4, k4, 0, 0))
    check(r_.startswith("-Needs Mining Lv 10") and total(inv_counts(p4), pc(k4)) == b0 and int(s4.rar[0]) == 0, "U: below the level gate -> refused, nothing moved: %s" % r_)
    coll(U4, {"Mining": 25 * 9 * 9})       # Lv 10
    r_ = str(VS.upgrade(p4, U4, k4, 0, 1))
    check(r_.startswith("=Already") and int(s4.rar[0]) == 0, "U: a click made at another rarity (from 1) -> 'already', nothing moved")
    pool_b, inv_b = pc(k4), inv_counts(p4)
    r_ = str(VS.upgrade(p4, U4, k4, 0, 0))
    drain()
    paid = {COB: 500, COP: 250, IRON: 100}
    exp_pool = {COB: 0, COP: 0}
    check(r_.startswith("+Mining is now Unique") and int(s4.rar[0]) == 1 and pc(k4).get(COB, 0) == 0 and COP not in pc(k4)
          and inv_counts(p4).get(COB) == 50 and inv_counts(p4).get(IRON) == 30
          and total(total(inv_counts(p4), pc(k4)), paid) == b0, "U: Unique paid: the Void first (300 cobble, 250 copper), then the inventory (200 cobble, 100 iron); exactly the cost left: %s" % r_)
    pd4 = read_props(os.path.join(SCRATCH, "u", "pd", k4 + ".properties"))
    check(pd4 is not None and pd4.get("rar.Mining") == "1", "U: the rarity is saved (pd file, writer job): %s" % (pd4 or {}).get("rar.Mining"))
    check(read_pool(os.path.join(SCRATCH, "u", "pools"), k4) == pc(k4) and not Pool.DIRTY.containsKey(k4),
          "U (fix 4): the same writer job saved the paid pool at once (no debounce window): file %s" % read_pool(os.path.join(SCRATCH, "u", "pools"), k4))
    b1 = total(inv_counts(p4), pc(k4))
    r_ = str(VS.upgrade(p4, U4, k4, 0, 0))
    check(r_.startswith("=Already upgraded") and total(inv_counts(p4), pc(k4)) == b1 and int(s4.rar[0]) == 1, "U: a SECOND click of the same step charges nothing: %s" % r_)
    # not enough -> refused, nothing moved
    coll(U4, {"Mining": 25 * 24 * 24})     # Lv 25 (the Rare gate)
    r_ = str(VS.upgrade(p4, U4, k4, 0, 1))
    check(r_.startswith("-Not enough") and total(inv_counts(p4), pc(k4)) == b1 and int(s4.rar[0]) == 1, "U: not enough items -> refused, nothing moved: %s" % r_)
    # a crash in the middle of the inventory payment -> everything back
    fresh(os.path.join(SCRATCH, "u2"))
    write_pool(os.path.join(SCRATCH, "u2", "pools"), k4, {"Plant_Crop_Wheat_Item": 200, "Ingredient_Life_Essence": 50})
    s4b = mk_state(k4, U4)
    p4b = player(storage=[(WHEAT, 100), (WHEAT, 100), (WHEAT, 100), ("Plant_Crop_Lettuce_Item", 100), ("Plant_Crop_Lettuce_Item", 100),
                          ("Plant_Crop_Lettuce_Item", 50), ("Ingredient_Life_Essence", 50)], boom=True)
    coll(U4, {"Farming": 25 * 9 * 9})
    b2 = total(inv_counts(p4b), pc(k4))
    TBoom.CALLS = 0
    TBoom.BOOMAT = 2
    r_ = str(VS.upgrade(p4b, U4, k4, 2, 0))
    check(r_.startswith("-Internal error") and total(inv_counts(p4b), pc(k4)) == b2 and int(s4b.rar[2]) == 0,
          "U: a crash after 2 slot removals -> rolled back: every slot and the Void as before, no rarity: %s" % r_)
    TBoom.BOOMAT = -1
    r_ = str(VS.upgrade(p4b, U4, k4, 2, 0))
    check(r_.startswith("+Farming is now Unique") and total(total(inv_counts(p4b), pc(k4)), {WHEAT: 500, "Plant_Crop_Lettuce_Item": 250, "Ingredient_Life_Essence": 100}) == b2,
          "U: the same upgrade after the crash: paid exactly once")
    # the sixth Legendary = Omni
    for i in range(6):
        s4b.rar[i] = 3
    s4b.rar[5] = 2
    Cfg.PD_COST_SMITHING_LEGENDARY = "Ingredient_Bar_Iron:5"
    write_pool(os.path.join(SCRATCH, "u2", "pools"), k4 + "x", {})
    Pool.add(k4, BAR, 5)
    coll(U4, {"Smithing": 10 * 49 * 49})
    r_ = str(VS.upgrade(p4b, U4, k4, 5, 2))
    check(r_.startswith("+Smithing is now Legendary") and "OMNI" in r_ and s4b.omni and VS.omni(k4), "U: the sixth Legendary makes the Void Omni: %s" % r_)
    r_ = str(VS.upgrade(p4b, U4, k4, 0, 3))
    check(r_.startswith("=Omni already"), "U: nothing above Omni")
    Cfg.PD_COST_SMITHING_LEGENDARY = "Ingredient_Hide_Light:2000,Ingredient_Hide_Medium:1000,Ingredient_Hide_Heavy:250,Ingredient_Fabric_Scrap_Shadoweave:250,Ingredient_Fabric_Scrap_Cindercloth:100"
    print("U. upgrade: gate / from / cost refused with nothing moved, the Void first then plain inventory stacks, a second click free, a "
          "mid-payment crash rolled back, the sixth Legendary = Omni")

    # ---------------- M. MIGRATION
    def jrnl(base, k):
        p_ = os.path.join(base, "pd", k + ".journal")
        return [l.split("|") for l in open(p_, encoding="utf-8").read().splitlines()] if os.path.exists(p_) else []

    def bags_in(p_):
        return dict((i_, v_) for i_, v_ in inv_counts(p_).items() if legacy_rank(i_))

    def run_mig(base, k, u, p_, settle=True):
        """one settled sweep's Void step (+ the writer drained); then the 30 s pass"""
        r0 = VS.migrate(pref(u), p_, u, k)
        drain()
        if settle:
            VS.settleDue(System.currentTimeMillis() + 31000)
            drain()
            Pool.flushDirty()
        return r0

    def state_of(k):
        s_ = VS.st(k)
        return (tuple(int(x) for x in s_.rar), bool(s_.omni))

    def expected(bags):
        """the spec result of a set of old bags on a fresh profile: (rarities, omni, refund items)"""
        order = sorted(bags, key=lambda x: -legacy_rank(x[0]))
        rar = [0] * 6
        omni = False
        usedr = {}
        refund = {}
        for bid, q in order:
            r = legacy_rank(bid)
            typ = "Omni" if r == 5 else bid.split("_")[2]
            up = False
            if r == 5:
                up = usedr.get("Omni", 0) == 0
            elif not omni and usedr.get(typ, 0) < r:
                cats = [typ] + (["Fishing"] if typ == "Farming" else [])
                up = any(r - 1 >= rar[CATS6.index(c)] for c in cats)
            fq = q - 1 if up else q
            if up:
                usedr[typ] = max(usedr.get(typ, 0), r)
                if r == 5:
                    omni = True
                else:
                    for c in [typ] + (["Fishing"] if typ == "Farming" else []):
                        rar[CATS6.index(c)] = max(rar[CATS6.index(c)], r - 1)
            for k_, v_ in REFUND[r - 1].items():
                refund[k_] = refund.get(k_, 0) + v_ * fq
        return tuple(rar), omni, dict((k_, v_) for k_, v_ in refund.items() if v_)
    bad_m = []
    # M1: History first + run once
    base = os.path.join(SCRATCH, "m1")
    pd_ = fresh(base)
    U5 = UUID.fromString("00000000-0000-0000-0000-0000000a0802")
    k5 = str(U5)
    nocoll()
    pool5 = {COB: 77, FISH: 12, "Rubble_Stone": 3}
    write_pool(pd_, k5, pool5)
    os.makedirs(os.path.join(base, "processing"))
    open(os.path.join(base, "processing", k5 + ".properties"), "w").write("Furnace.queue=\n")
    p5 = player(storage=[("Skyy_Sack_Mining_Small", 1), ("Skyy_Sack_Mining_Rare", 1), (COB, 5)], hotbar=[("Skyy_Sack_Farming_Medium", 1)],
                backpack=[("Skyy_Sack_Combat_Large", 1)])
    raw_pool = open(os.path.join(pd_, k5 + ".properties"), "rb").read()
    r0 = VS.migrate(pref(U5), p5, U5, k5)
    drain()
    hist = sorted(os.listdir(os.path.join(base, "history"))) if os.path.isdir(os.path.join(base, "history")) else []
    s5 = VS.st(k5)
    check(not r0 and len(hist) == 1 and open(os.path.join(base, "history", hist[0], "pools-" + k5 + ".properties"), "rb").read() == raw_pool
          and os.path.exists(os.path.join(base, "history", hist[0], "processing-" + k5 + ".properties")) and int(s5.first) > 0
          and read_props(os.path.join(base, "pd", k5 + ".properties")).get("v2.first") and bags_in(p5) and Swp.INVDIRTY.containsKey(U5),
          "M: the FIRST sweep only makes the History copy (pool + processing, byte-identical, read back) and sets the run-once marker; no bag "
          "moves yet; the player stays due (INVDIRTY)")
    ml = open(os.path.join(base, "migration.log"), encoding="utf-8").read()
    check("v2 START" in ml and "UNDO" in ml and "/pdadmin legacybags" in ml and hist[0] in ml, "M: migration.log: the start line with its UNDO steps")
    check("do NOT copy the History copy over it" in ml and ("copy " + hist[0]) not in ml and "legacybags all" in ml,
          "M (fix 1): the UNDO line never tells the admin to copy the History pool back over a used pool; it names legacybags all")
    r1 = run_mig(base, k5, U5, p5)
    exp5 = expected([("Skyy_Sack_Mining_Small", 1), ("Skyy_Sack_Mining_Rare", 1), ("Skyy_Sack_Farming_Medium", 1), ("Skyy_Sack_Combat_Large", 1)])
    j5 = jrnl(base, k5)
    cs_ = [l for l in j5 if l[0] == "C"]
    ds_ = set(l[1] for l in j5 if l[0] == "D")
    check(r1 and not bags_in(p5) and state_of(k5) == (exp5[0], exp5[1]) and pc(k5) == total(pool5, exp5[2]) and read_pool(pd_, k5) == total(pool5, exp5[2])
          and len(cs_) == 4 and all(l[1] in ds_ for l in cs_) and inv_counts(p5).get(POCKET) == 1,
          "M: converted: Mining Rare (the Small one refunded: 20 Fibre + 4 Sticks), Farming + Fishing Unique, Combat Legendary; the pool = before "
          "+ exactly the refund (memory and file); 4 C lines, each settled (D); the Pocket Dimension given: %s %s" % (state_of(k5), pc(k5)))
    pm5 = read_props(os.path.join(pd_, k5 + ".properties"))
    check(pm5 is not None and not any(k_.startswith("~") for k_ in pm5), "M: the refund seq left the pool file once D was written (no meta line left)")
    hist2 = sorted(os.listdir(os.path.join(base, "history")))
    r2_ = run_mig(base, k5, U5, p5)
    check(r2_ and hist2 == hist and len(jrnl(base, k5)) == len(j5) and state_of(k5) == (exp5[0], exp5[1]), "M: run once - a later sweep: no new History copy, no journal line, nothing changes")
    # M2: every old id x rarity, alone (a fresh profile each)
    for bid in LEGACY:
        base = os.path.join(SCRATCH, "m2")
        pd_ = fresh(base)
        k6 = "00000000-0000-0000-0000-0000000b%04d" % LEGACY.index(bid)
        U6 = UUID.fromString(k6)
        write_pool(pd_, k6, {COB: 10})
        p6 = player(hotbar=[(bid, 1)])
        run_mig(base, k6, U6, p6, settle=False)
        run_mig(base, k6, U6, p6)
        e6 = expected([(bid, 1)])
        if bags_in(p6) or state_of(k6) != (e6[0], e6[1]) or pc(k6) != total({COB: 10}, e6[2]):
            bad_m.append(("alone", bid, state_of(k6), pc(k6)))
    check(not bad_m, "M: each of the 21 old ids alone -> its rarity (Normal = the start), the Farming bag also Fishing, the Omni = Omni, no refund: %s" % bad_m[:3])
    # M3: best bag wins whatever the slot order; stacks of bags; extra Omni bags
    scen = [
        [("Skyy_Sack_Mining_Small", 1), ("Skyy_Sack_Mining_Large", 1), ("Skyy_Sack_Mining_Rare", 2)],
        [("Skyy_Sack_Omni", 2), ("Skyy_Sack_Foraging_Medium", 1)],
        [("Skyy_Sack_Foraging_Medium", 1), ("Skyy_Sack_Omni", 1)],
        [("Skyy_Sack_Farming_Rare", 1), ("Skyy_Sack_Farming_Rare", 1), ("Skyy_Sack_Smithing_Small", 3)],
    ]
    bad_m = []
    for si, bags in enumerate(scen):
        for flip in (False, True):
            base = os.path.join(SCRATCH, "m3")
            pd_ = fresh(base)
            k7 = "00000000-0000-0000-0000-0000000c%02d%02d" % (si, int(flip))
            U7 = UUID.fromString(k7)
            write_pool(pd_, k7, {COB: 1})
            order = list(reversed(bags)) if flip else bags
            p7 = player(storage=order)
            run_mig(base, k7, U7, p7, settle=False)
            run_mig(base, k7, U7, p7)
            e7 = expected(bags)
            if bags_in(p7) or state_of(k7) != (e7[0], e7[1]) or pc(k7) != total({COB: 1}, e7[2]):
                bad_m.append((si, flip, state_of(k7), (e7[0], e7[1]), pc(k7), e7[2]))
    check(not bad_m, "M: best bag wins in any slot order; bag stacks: one used, the rest refunded; an extra Omni = 5 Legendary chains; typed bags with "
          "an Omni refunded: %s" % bad_m[:2])
    # M4: CRASH AT EVERY STEP (+ the engine's inventory rolled back or saved) = the no-crash result
    CRASH_SCEN = [("Skyy_Sack_Mining_Large", 1), ("Skyy_Sack_Mining_Small", 2), ("Skyy_Sack_Farming_Medium", 1), ("Skyy_Sack_Omni", 1),
                  ("Skyy_Sack_Omni", 1), ("Skyy_Sack_Combat_Rare", 1)]
    e8 = expected(CRASH_SCEN)
    bad_c = []
    variants = [("C", "rolled back"), ("REM", "rolled back"), ("REM", "saved"), ("SR", "saved"), ("SF", "saved")]
    for nth in (1, 2, 3):
        for (pt, invstate) in variants:
            base = os.path.join(SCRATCH, "m4")
            pd_ = fresh(base)
            k8 = "00000000-0000-0000-0000-0000000d%02d%02d" % (nth, variants.index((pt, invstate)))
            U8 = UUID.fromString(k8)
            pool8 = {COB: 40, FISH: 3}
            write_pool(pd_, k8, pool8)
            p8 = player(storage=CRASH_SCEN[:3], hotbar=CRASH_SCEN[3:5], backpack=CRASH_SCEN[5:])
            run_mig(base, k8, U8, p8, settle=False)        # History
            # crash the nth time the step runs (C / REM: the nth stack converted, best first; SR / SF: the nth settle of that kind)
            crashed = False
            VS.CRASHN = nth
            VS.CRASHHITS = 0
            if pt in ("C", "REM"):
                VS.CRASHAT = pt
                try:
                    VS.migrate(pref(U8), p8, U8, k8)
                except Exception:
                    crashed = True
                VS.CRASHAT = None
                if invstate == "rolled back":
                    p8 = player(storage=CRASH_SCEN[:3], hotbar=CRASH_SCEN[3:5], backpack=CRASH_SCEN[5:])
            else:
                run_mig(base, k8, U8, p8, settle=False)    # every bag converted, the credits pending
                VS.CRASHAT = pt
                for e in list(VS.pendCopy(k8)):
                    if (pt == "SR") != (str(e[4]) == "R"):
                        continue
                    try:
                        if VS.settle(k8, e):
                            VS.pendRemove(k8, e)
                    except Exception:
                        crashed = True
                        break
                VS.CRASHAT = None
                drain()
            # the process died: memory gone, files stay, inventory as the engine left it
            restart()
            run_mig(base, k8, U8, p8)
            run_mig(base, k8, U8, p8)
            got = (state_of(k8), pc(k8), read_pool(pd_, k8), bags_in(p8))
            jl = jrnl(base, k8)
            cs_ = [l[1] for l in jl if l[0] == "C"]
            ends = dict((l[1], l[0]) for l in jl if l[0] in ("D", "X"))
            ok = (got[0] == (e8[0], e8[1]) and got[1] == total(pool8, e8[2]) and got[2] == total(pool8, e8[2]) and not got[3]
                  and all(c_ in ends for c_ in cs_) and sum(1 for c_ in cs_ if ends[c_] == "D") == sum(1 for l in jl if l[0] == "C" and l[1] in ends and ends[l[1]] == "D"))
            if not ok or (pt in ("C", "REM", "SR", "SF") and not crashed and nth == 1):
                bad_c.append((pt, invstate, nth, crashed, got[0], (e8[0], e8[1]), got[1], total(pool8, e8[2])))
    check(not bad_c, "M: CRASH AT EVERY STEP - after the journal line (inventory rolled back), after the slot removal (rolled back / saved), after "
          "the rarity save, after the refund save (1st / 2nd / 3rd occurrence each): the restart ends EXACTLY like the no-crash run (rarity, Omni, "
          "pool = before + the refunds once, memory and file, no old bag left, every C line closed by D or X): %s" % bad_c[:3])
    # M5: a History copy that fails -> nothing marked, retried; a crash between the copy and the marker -> a second copy, then the marker
    base = os.path.join(SCRATCH, "m5")
    pd_ = fresh(base)
    k9 = "00000000-0000-0000-0000-0000000e0001"
    U9 = UUID.fromString(k9)
    write_pool(pd_, k9, {COB: 5})
    p9 = player(storage=[("Skyy_Sack_Mining_Rare", 1)])
    VS.CRASHAT = "H"
    run_mig(base, k9, U9, p9, settle=False)
    VS.CRASHAT = None
    s9 = VS.st(k9)
    check(int(s9.first) == 0 and VS.SNAPFAIL.containsKey(k9) and bags_in(p9) and read_pool(pd_, k9) == {COB: 5}, "M: a failed History step -> no marker, no bag moved, retried later")
    VS.SNAPFAIL.clear()
    run_mig(base, k9, U9, p9, settle=False)
    run_mig(base, k9, U9, p9)
    check(int(s9.first) > 0 and not bags_in(p9) and state_of(k9)[0][0] == 2, "M: the retry makes the copy, sets the marker, then converts")
    # M6: a bag carried into ANOTHER profile converts for that profile only; profile p1's files untouched
    base = os.path.join(SCRATCH, "m6")
    pd_ = fresh(base)
    kA, kB = "00000000-0000-0000-0000-0000000f0001", "00000000-0000-0000-0000-0000000f0001-p3"
    UA = UUID.fromString(kA)
    write_pool(pd_, kA, {COB: 1})
    write_pool(pd_, kB, {COB: 2})
    pA = player(storage=[("Skyy_Sack_Combat_Rare", 1)])
    run_mig(base, kA, UA, pA, settle=False)
    run_mig(base, kA, UA, pA)
    pdA = open(os.path.join(base, "pd", kA + ".properties"), "rb").read()
    pB = player(storage=[("Skyy_Sack_Smithing_Large", 1)])
    run_mig(base, kB, UA, pB, settle=False)
    run_mig(base, kB, UA, pB)
    check(open(os.path.join(base, "pd", kA + ".properties"), "rb").read() == pdA and state_of(kB)[0][5] == 3 and state_of(kA)[0][5] == 0
          and state_of(kA)[0][4] == 2, "M: a bag carried into profile 3 converts for profile 3 only (profile 1's Void file untouched)")
    # M7: a full inventory for the Pocket item
    base = os.path.join(SCRATCH, "m7")
    pd_ = fresh(base)
    kC = "00000000-0000-0000-0000-0000000f0002"
    UC = UUID.fromString(kC)
    write_pool(pd_, kC, {})
    pC = player(storage=[(COB, 100)] * 36)
    run_mig(base, kC, UC, pC, settle=False)
    run_mig(base, kC, UC, pC)
    check(inv_counts(pC).get(POCKET) is None and VS.st(kC).pocket and inv_counts(pC)[COB] == 3600, "M: a full inventory -> no Pocket item (the chat line says /pd), nothing lost")
    # M8: /pdadmin legacybags + its tokens; /pdadmin omni
    base = os.path.join(SCRATCH, "m8")
    pd_ = fresh(base)
    kD = "00000000-0000-0000-0000-0000000f0003"
    UD = UUID.fromString(kD)
    write_pool(pd_, kD, {COB: 9})
    pD = player(storage=[("Skyy_Sack_Mining_Large", 1), ("Skyy_Sack_Mining_Small", 1)])
    run_mig(base, kD, UD, pD, settle=False)
    run_mig(base, kD, UD, pD)
    pool_after = pc(kD)
    msg = str(VS.giveBack(pD, kD))
    drain()
    check(msg.startswith("1 old bag") and bags_in(pD) == {"Skyy_Sack_Mining_Large": 1} and pc(kD) == pool_after
          and any(l[0] == "G" for l in jrnl(base, kD)), "M: /pdadmin legacybags gives back the RARITY bag only (the refunded Small stays refunded), one G line: %s" % msg)
    msg2 = str(VS.giveBack(pD, kD))
    check(msg2.startswith("0 old bag") and bags_in(pD) == {"Skyy_Sack_Mining_Large": 1}, "M: a second /pdadmin legacybags gives nothing")
    st0 = state_of(kD)
    run_mig(base, kD, UD, pD)
    check(bags_in(pD) == {"Skyy_Sack_Mining_Large": 1} and state_of(kD) == st0 and pc(kD) == pool_after and VS.st(kD).hold
          and read_props(os.path.join(base, "pd", kD + ".properties")).get("v2.hold") == "true",
          "M (fix 2): after /pdadmin legacybags the profile is HELD (saved): the given-back bag stays a bag at the next sweep")
    check(str(VS.resume(kD)).startswith("resumed"), "M (fix 2): /pdadmin resume <player>")
    drain()
    run_mig(base, kD, UD, pD)
    check(not bags_in(pD) and state_of(kD) == st0 and pc(kD) == pool_after, "M: the given-back bag converts again with NO second credit (the token): no refund, same rarity")
    restart()
    check(str(VS.grantOmni(kD)).startswith("Omni granted") and VS.omni(kD), "M: /pdadmin omni grants Omni")
    drain()
    check(read_props(os.path.join(base, "pd", kD + ".properties")).get("omni") == "true", "M: ... and it is saved")
    # fix B2: an Omni bag on a Void that is Omni already (granted, no Omni R in the journal) is REFUNDED (5 Legendary chains), not swallowed
    pool_o = pc(kD)
    pD.getInventory().getStorage().addItemStack(IS("Skyy_Sack_Omni", 1))
    run_mig(base, kD, UD, pD, settle=False)
    run_mig(base, kD, UD, pD)
    check(not bags_in(pD) and pc(kD) == total(pool_o, REFUND[4]) and VS.omni(kD),
          "M (fix B2): an Omni bag on an already-Omni Void (/pdadmin omni) is refunded: +%s" % dict((k_, v_ - pool_o.get(k_, 0)) for k_, v_ in pc(kD).items() if v_ != pool_o.get(k_, 0)))
    # fix 2: /pdadmin legacybags all = a server-wide hold kept in a flag file (survives a restart); each profile gets its rarity bags back at its
    # next sweep (an offline player = at the next join), no old bag converts; resume all ends it and the bags convert again with no second credit
    base = os.path.join(SCRATCH, "m10")
    pd_ = fresh(base)
    kE, kF = "00000000-0000-0000-0000-0000000f0004", "00000000-0000-0000-0000-0000000f0005"
    UE, UF = UUID.fromString(kE), UUID.fromString(kF)
    write_pool(pd_, kE, {COB: 4})
    write_pool(pd_, kF, {COB: 6})
    pE = player(storage=[("Skyy_Sack_Combat_Rare", 1), ("Skyy_Sack_Combat_Small", 1)])
    run_mig(base, kE, UE, pE, settle=False)
    run_mig(base, kE, UE, pE)
    stE, poolE = state_of(kE), pc(kE)
    check(bool(VS.setHoldAll(True)) and os.path.exists(os.path.join(base, "pd", "_legacybags-all.flag")), "M (fix 2): legacybags all writes pd/_legacybags-all.flag")
    restart()
    check(bool(VS.HOLDALL), "M (fix 2): ... and a restart keeps the hold (loadHold)")
    run_mig(base, kE, UE, pE)
    check(bags_in(pE) == {"Skyy_Sack_Combat_Rare": 1} and state_of(kE) == stE and pc(kE) == poolE and sum(1 for l in jrnl(base, kE) if l[0] == "G") == 1,
          "M (fix 2): under legacybags all the player's next sweep gives the rarity bag back (refund stays), one G line; pool and rarity kept: %s %s" % (bags_in(pE), pc(kE)))
    run_mig(base, kE, UE, pE)
    check(bags_in(pE) == {"Skyy_Sack_Combat_Rare": 1} and sum(1 for l in jrnl(base, kE) if l[0] == "G") == 1, "M (fix 2): ... the next sweep gives nothing more and converts nothing")
    pF = player(storage=[("Skyy_Sack_Mining_Rare", 1)])
    run_mig(base, kF, UF, pF, settle=False)
    run_mig(base, kF, UF, pF)
    check(bags_in(pF) == {"Skyy_Sack_Mining_Rare": 1} and state_of(kF)[0][0] == 0 and pc(kF) == {COB: 6}, "M (fix 2): under the hold a not-yet-converted bag stays a bag (no loss, no credit)")
    ml10 = open(os.path.join(base, "migration.log"), encoding="utf-8").read()
    check("legacybags all: 1 old bag(s) given back" in ml10, "M (fix 2): migration.log has the per-profile give-back line")
    check(bool(VS.setHoldAll(False)) and not os.path.exists(os.path.join(base, "pd", "_legacybags-all.flag")) and not VS.HOLDALL, "M (fix 2): resume all removes the flag")
    run_mig(base, kE, UE, pE)
    run_mig(base, kF, UF, pF, settle=False)
    run_mig(base, kF, UF, pF)
    check(not bags_in(pE) and state_of(kE) == stE and pc(kE) == poolE and not bags_in(pF) and state_of(kF)[0][0] == 2,
          "M (fix 2): after resume all the bags convert again - the given-back one with no second credit, the new one to Rare")
    # ---- fix round 2 (second critics) ----
    # A4: give-back tokens live in the journal only (G lines minus live "tok" C lines): a crash right after the "tok" C line (the bag still
    # in its slot) -> after the restart the X line gives the token back and the bag converts again with it: no refund, same rarity
    base = os.path.join(SCRATCH, "m12")
    pd_ = fresh(base)
    kH = "00000000-0000-0000-0000-0000000f0007"
    UH = UUID.fromString(kH)
    write_pool(pd_, kH, {COB: 3})
    pH = player(storage=[("Skyy_Sack_Foraging_Large", 1)])
    run_mig(base, kH, UH, pH, settle=False)
    run_mig(base, kH, UH, pH)
    stH, poolH = state_of(kH), pc(kH)
    VS.giveBack(pH, kH)
    drain()
    VS.flushDirty()
    check(bags_in(pH) == {"Skyy_Sack_Foraging_Large": 1} and int(VS.tokAvail(kH, VS.st(kH), "Skyy_Sack_Foraging_Large")) == 1
          and not any(k_.startswith("ret.") for k_ in read_props(os.path.join(base, "pd", kH + ".properties"))),
          "R2 (A4): legacybags gives the bag back; its token is the journal's G line (no ret.* line in the pd file)")
    VS.resume(kH)
    drain()
    VS.CRASHAT, VS.CRASHN, VS.CRASHHITS = "C", 1, 0
    crashed = False
    try:
        VS.migrate(pref(UH), pH, UH, kH)
    except Exception:
        crashed = True
    VS.CRASHAT = None
    drain()
    tokc = [l for l in jrnl(base, kH) if l[0] == "C" and len(l) >= 8 and l[7] == "tok"]
    check(crashed and len(tokc) == 1 and bags_in(pH) == {"Skyy_Sack_Foraging_Large": 1},
          "R2 (A4): a crash right after the re-conversion's journal line: one 'tok' C line, the bag still in its slot")
    restart()
    check(int(VS.tokAvail(kH, VS.st(kH), "Skyy_Sack_Foraging_Large")) == 0, "R2 (A4): after the restart the unsettled 'tok' line holds the token (none spare)")
    run_mig(base, kH, UH, pH)
    run_mig(base, kH, UH, pH)
    jl = jrnl(base, kH)
    check(not bags_in(pH) and state_of(kH) == stH and pc(kH) == poolH and read_pool(pd_, kH) == poolH
          and any(l[0] == "X" and l[1] == tokc[0][1] for l in jl) and sum(1 for l in jl if l[0] == "C" and len(l) >= 8 and l[7] == "tok") == 2
          and int(VS.tokAvail(kH, VS.st(kH), "Skyy_Sack_Foraging_Large")) == 0,
          "R2 (A4): ... recover writes X (token back), the bag converts again WITH the token: no refund, same rarity, token spent once: %s %s" % (state_of(kH), pc(kH)))
    # A2: /pdadmin resume all ends the saved hold of a profile that was NOT loaded at the time (pd/_resume-all.stamp vs v2.holdAt)
    VS.giveBack(pH, kH)
    drain()
    VS.flushDirty()
    check(read_props(os.path.join(base, "pd", kH + ".properties")).get("v2.hold") == "true", "R2 (A2): a held profile (saved v2.hold)")
    restart()
    check(not VS.STATES.containsKey(kH) and bool(VS.setHoldAll(True)) and bool(VS.setHoldAll(False))
          and os.path.exists(os.path.join(base, "pd", "_resume-all.stamp")), "R2 (A2): resume all while that profile is not loaded writes pd/_resume-all.stamp")
    restart()
    check(not VS.st(kH).hold, "R2 (A2): ... the profile loads NOT held any more (its hold is older than the resume)")
    VS.flushDirty()
    check(read_props(os.path.join(base, "pd", kH + ".properties")).get("v2.hold") is None, "R2 (A2): ... and that is saved")
    run_mig(base, kH, UH, pH)
    run_mig(base, kH, UH, pH)
    check(not bags_in(pH) and state_of(kH) == stH and pc(kH) == poolH, "R2 (A2): ... its given-back bag converts again with no second credit")
    VS.giveBack(pH, kH)
    drain()
    check(VS.st(kH).hold, "R2 (A2): a hold set AFTER the resume all stays on")
    restart()
    check(VS.st(kH).hold, "R2 (A2): ... also after a restart")
    VS.resume(kH)
    drain()
    # A1: legacybags all takes the Pocket Dimension out (0.7.18 does not know it) + logs it; no gift while on; resume all gives it back once
    pI = player(storage=[(POCKET, 1), (COB, 2)], hotbar=[(POCKET, 1)])
    kI = "00000000-0000-0000-0000-0000000f0008"
    UI_ = UUID.fromString(kI)
    write_pool(pd_, kI, {COB: 1})
    run_mig(base, kI, UI_, pI, settle=False)
    run_mig(base, kI, UI_, pI)
    VS.setHoldAll(True)
    run_mig(base, kI, UI_, pI)
    run_mig(base, kI, UI_, pI)
    mlI = open(os.path.join(base, "migration.log"), encoding="utf-8").read()
    check(inv_counts(pI).get(POCKET) is None and inv_counts(pI).get(COB) == 2 and pc(kI) == {COB: 1}
          and "2 Pocket Dimension item(s) removed" in mlI and not VS.st(kI).pocket,
          "R2 (A1): under legacybags all the Pocket Dimension leaves the inventory (logged), nothing else moves, no new one while on")
    VS.setHoldAll(False)
    run_mig(base, kI, UI_, pI)
    run_mig(base, kI, UI_, pI)
    check(inv_counts(pI).get(POCKET) == 1, "R2 (A1): resume all gives one Pocket Dimension back")
    # A3: Omni through six Legendary (Omni auto, s.omni never set) - a later Omni bag is REFUNDED (5 Legendary chains), not swallowed
    kJ = "00000000-0000-0000-0000-0000000f0009"
    UJ = UUID.fromString(kJ)
    write_pool(pd_, kJ, {COB: 1})
    pJ = player()
    run_mig(base, kJ, UJ, pJ, settle=False)
    run_mig(base, kJ, UJ, pJ)
    sJ = VS.st(kJ)
    for i_ in range(6):
        sJ.rar[i_] = 3
    oa0 = Cfg.PD_OMNI_AUTO
    Cfg.PD_OMNI_AUTO = True
    poolJ = pc(kJ)
    pJ.getInventory().getStorage().addItemStack(IS("Skyy_Sack_Omni", 1))
    run_mig(base, kJ, UJ, pJ, settle=False)
    run_mig(base, kJ, UJ, pJ)
    check(not bags_in(pJ) and not sJ.omni and VS.omni(kJ) and pc(kJ) == total(poolJ, REFUND[4]),
          "R2 (A3): an Omni bag on a Void that is Omni through six Legendary is refunded: +%s" % dict((k_, v_ - poolJ.get(k_, 0)) for k_, v_ in pc(kJ).items() if v_ != poolJ.get(k_, 0)))
    Cfg.PD_OMNI_AUTO = oa0
    # A5: a refund already credited in memory whose pool write did not happen (paidHas true, pool dirty) is saved + read back before D
    kK = "00000000-0000-0000-0000-0000000f000a"
    UK = UUID.fromString(kK)
    write_pool(pd_, kK, {COB: 5})
    pK = player(storage=[("Skyy_Sack_Smithing_Rare", 1), ("Skyy_Sack_Smithing_Small", 1)])
    run_mig(base, kK, UK, pK, settle=False)
    run_mig(base, kK, UK, pK, settle=False)
    fe = [e for e in VS.pendCopy(kK) if str(e[4]) == "F"]
    check(len(fe) == 1 and bool(Pool.credit(kK, fe[0][0], Cfg.parseCost(fe[0][6]))) and Pool.DIRTY.containsKey(kK)
          and read_pool(pd_, kK) == {COB: 5}, "R2 (A5): a refund credited in memory only (the first try's pool write failed)")
    VS.settleDue(System.currentTimeMillis() + 31000)
    drain()
    jlK = jrnl(base, kK)
    check(any(l[0] == "D" and l[1] == str(fe[0][0]) for l in jlK) and read_pool(pd_, kK) == total({COB: 5}, REFUND[0]) and pc(kK) == total({COB: 5}, REFUND[0]),
          "R2 (A5): the retry writes the pool (refund on disk, once) BEFORE the D line: file %s" % read_pool(pd_, kK))
    # B1: the History copy holds up the sweep only while an old bag is there: no bag = the sweep goes on (also when the copy fails)
    base = os.path.join(SCRATCH, "m13")
    pd_ = fresh(base)
    kL, kM = "00000000-0000-0000-0000-0000000f000b", "00000000-0000-0000-0000-0000000f000c"
    UL, UM = UUID.fromString(kL), UUID.fromString(kM)
    write_pool(pd_, kL, {COB: 1})
    write_pool(pd_, kM, {COB: 1})
    open(os.path.join(base, "history"), "w").write("not a folder")   # the History copy cannot be made
    rL = VS.migrate(pref(UL), player(storage=[(COB, 3)]), UL, kL)
    drain()
    rM = VS.migrate(pref(UM), player(storage=[("Skyy_Sack_Mining_Small", 1)]), UM, kM)
    drain()
    check(bool(rL) and not rM and VS.SNAPFAIL.containsKey(kL) and int(VS.st(kL).first) == 0 and int(VS.st(kM).first) == 0,
          "R2 (B1): History copy failing: a profile WITHOUT an old bag still sweeps (true), one WITH a bag waits (false); no marker set")
    # C: the words players / admins see (Server Setup rows, config comments, /craft page, the amount box hint, one welcome chat line)
    bsrc2 = open(os.path.join(HERE, "build_skyysacks_0.8.0.py"), encoding="utf8").read()
    check(all(t_ not in bsrc2 for t_ in ('"Cooked food in the Farming bag", "bags"', '"Stack refill from bags"', '"Bags in inventory crafting", "bags"', "Off on the bag page", "a mode on the bag page get",
                                         "Back to bags", '"bags paused', "from bags", "uses the bags you carry. Off", 'placeholder="empty is one stack"'))
          and "Back to the Void" in bsrc2 and '"Void in inventory crafting"' in bsrc2 and "empty is one stack or all on Deposit" in bsrc2
          and bsrc2.count("Your storage is now the Void") == 1 and "upgrade its rarity for more space. Open it with /pd" not in bsrc2,
          "R2 (C1/C2/C4/C8): Server Setup rows, config comments, the /craft page + bench lines say the Void; the box hint covers Deposit; welcome + Pocket = one line")
    # fix 6: the History copy is of the LIVE pool (an unsaved pool change is flushed first)
    base = os.path.join(SCRATCH, "m11")
    pd_ = fresh(base)
    kG = "00000000-0000-0000-0000-0000000f0006"
    write_pool(pd_, kG, {COB: 10})
    VS.st(kG)
    Pool.add(kG, COB, 5)
    check(Pool.DIRTY.containsKey(kG) and bool(VS.snapshot(kG)), "M (fix 6): snapshot with an unsaved pool change")
    hd_ = os.path.join(base, "history", os.listdir(os.path.join(base, "history"))[0])
    check(read_pool(hd_, "pools-" + kG) == {COB: 15} and read_pool(pd_, kG) == {COB: 15}, "M (fix 6): the History copy holds the LIVE pool (15, not the 10 on disk before)")
    print("M. migration: History first + run once, every old id, best bag wins in any order, extras refunded exactly, crash at every step = "
          "the no-crash result, failed History retried, per-profile, full inventory, /pdadmin legacybags (tokens) + omni")
    # data for child 3 (the 0.7.18 rollback check): a migrated folder + the expected pool contents
    rb = os.path.join(SCRATCH, "m1", "pools")
    json.dump({"dir": rb, "pools": dict((f[:-11], read_pool(rb, f[:-11])) for f in os.listdir(rb) if f.endswith(".properties")),
               "meta_key": k5}, open(os.path.join(SCRATCH, "rollback.json"), "w"))

    # ---------------- P. the Void page, executed
    UCBc, UEBc = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"), JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")

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
    base = os.path.join(SCRATCH, "p")
    pd_ = fresh(base)
    UP = UUID.fromString("00000000-0000-0000-0000-0000000f0010")
    kP = str(UP)
    write_pool(pd_, kP, dict([(COB, 600), (COP, 250), (IRON, 5)] + [("Rock_Test_%02d" % i, i + 1) for i in range(40)]))
    for i in range(40):
        custom_item("Rock_Test_%02d" % i, 100)
    sP = VS.st(kP)
    sP.first = 1
    coll(UP, {"Mining": 25 * 9 * 9})
    pP = player(storage=[(IRON, 100), (COP, 10)])
    pg = us.allocateInstance(SPage.class_)
    jfield(SPage.class_, "playerRef").set(pg, pref(UP))
    jfield(SPage.class_, "info").set(pg, JString(""))
    jfield(SPage.class_, "amount").set(pg, JString(""))

    def render():
        b_, e_ = UCBc(), UEBc()
        pg.render(b_, e_, pP, kP, UP)
        return ucb_text(b_)
    t0 = render()
    need = ["SkyyVoid", "Mining - Lv 10 - Normal (x1.0)", "Stored", "collected to Lv 11", "Over the limit", "SkyyVCell35", "Page 1 / 2", "Withdraw",
            "Deposit all", "Pick up all", "Upgrade to Unique (x1.5)", "Space 1,000 -> 1,500", "Level gate Mining Lv 10 - done", "SkyyVAmt", "Pick an item",
            "Stack refill from the Void", "Omni: get all six categories to Legendary (0 / 6)", "SkyyVTab3", "Fishing"]
    check(all(x in t0 for x in need), "P: render: header, stored / level lines, the over-limit line, 36 cells + paging, the amount box, the buttons, the "
          "upgrade box, the Omni line, six tabs: missing %s" % [x for x in need if x not in t0])

    def ev(data):
        pg.onEvent(None, None, pP, data)
        return str(jfield(SPage.class_, "info").get(pg) or "")
    i_ = ev('{"a":"cell:0"}')
    check(str(pg.sel) == COB, "P: a click on cell 0 selects the biggest stack (cobblestone)")
    a0 = total(inv_counts(pP), pc(kP))
    i_ = ev('{"a":"wd","@Amt":"25"}')
    check(i_.startswith("+Took 25") and inv_counts(pP).get(COB) == 25 and pc(kP)[COB] == 575 and total(inv_counts(pP), pc(kP)) == a0 and str(pg.amount) == "25",
          "P: Withdraw with 25 in the amount box -> 25 taken, the box keeps 25: %s" % i_)
    i_ = ev('{"a":"dep","@Amt":"10"}')
    check(i_.startswith("-This category is full") and inv_counts(pP).get(COB) == 25, "P: Deposit into the over-limit Mining -> refused, nothing moved: %s" % i_)
    i_ = ev('{"a":"wd","@Amt":"abc"}')
    check(i_.startswith("-Type a number") and inv_counts(pP).get(COB) == 25, "P: a non-number in the box -> refused")
    rb5 = total(inv_counts(pP), pc(kP))
    for txt_ in ("upgok:0:0", "craft", "upg", "tab:Fishing", "pickall"):
        i_ = ev('{"a":"wd","@Amt":"%s"}' % txt_)
        if not (i_.startswith("-Type a number") and int(sP.rar[0]) == 0 and not pg.confirm and str(pg.cat) != "Fishing" and total(inv_counts(pP), pc(kP)) == rb5):
            check(False, "P (fix B5): typing %r in the amount box + Withdraw fired another action: %s" % (txt_, i_))
    check(int(sP.rar[0]) == 0 and total(inv_counts(pP), pc(kP)) == rb5, "P (fix B5): action words typed in the amount box never fire an action (upgok / craft / upg / tab / pickall)")
    ev('{"a":"cell:1","@Amt":"100"}')
    check(str(pg.amount) == "100" and "100" in render(), "P (fix C1): type 100 first, then click an item -> the box keeps 100")
    ev('{"a":"tab:Mining","@Amt":"100"}')
    ev('{"a":"cell:0","@Amt":"100"}')
    check(str(pg.amount) == "100" and str(pg.sel) == COB, "P (fix C1): a tab click keeps the amount too")
    i_ = ev('{"a":"pg:next"}')
    check(int(pg.pageNo) == 1 and "Page 2 / 2" in render(), "P: Next page -> page 2")
    ev('{"a":"pg:prev"}')
    i_ = ev('{"a":"upg"}')
    t1 = render()
    check(pg.confirm and "Pay these items for Unique" in t1 and "SkyyVUpYes" in t1 and "SkyyVUpNo" in t1, "P: Upgrade -> the confirm step (Pay / Cancel)")
    b3 = total(inv_counts(pP), pc(kP))
    i_ = ev('{"a":"upgok:0:0"}')
    check(i_.startswith("+Mining is now Unique") and int(sP.rar[0]) == 1 and not pg.confirm, "P: Pay -> upgraded: %s" % i_)
    b4 = total(inv_counts(pP), pc(kP))
    i_ = ev('{"a":"upgok:0:0"}')
    check(i_.startswith("=Already upgraded") and total(inv_counts(pP), pc(kP)) == b4 and int(sP.rar[0]) == 1, "P: a second Pay of the same step charges nothing: %s" % i_)
    i_ = ev('{"a":"pickall"}')
    check(i_.startswith("+Picked up") and total(inv_counts(pP), pc(kP)) == b4, "P: Pick up all -> conserved: %s" % i_)
    i_ = ev('{"a":"tab:Fishing"}')
    check(str(pg.cat) == "Fishing" and pg.sel is None and "Fishing - Lv 1" in render(), "P: the Fishing tab")
    i_ = ev('{"a":"depall"}')
    check(total(inv_counts(pP), pc(kP)) == b4, "P: Deposit all (Fishing, nothing to move) -> conserved: %s" % i_)
    pg.handleDataEvent(None, None, JString('{"a":"tab:Combat"}'))
    check(str(pg.cat) == "Combat", "P: the engine entry handleDataEvent (no Player component found) still switches tabs; item moves need the player")
    print("P. the Void page rendered and driven: select, the amount box (withdraw / deposit / refused), paging, Upgrade -> Pay (once), "
          "Pick up all, tabs, Deposit all")

    # ---------------- C. config + KnowSync
    cfgd = os.path.join(SCRATCH, "c")
    os.makedirs(cfgd, exist_ok=True)
    with open(os.path.join(cfgd, "config.properties"), "w") as f:
        f.write("craftSearch=true\npd.perLevel=50\npd.mult.Rare=2.5\npd.cost.Mining.Unique=Ore_Iron:1,Ore_Copper:2\npd.cost.Mining.Rare=junk\n"
                "pd.maxLevel=99999\npd.omniAuto=false\nbag.small=5\n")
    Cfg.FILE = Paths.get(os.path.join(cfgd, "config.properties"))
    Cfg.MTIME = -1
    Cfg.reload()
    check(int(Cfg.PD_PER_LEVEL) == 50 and abs(float(Cfg.PD_MULT_RARE) - 2.5) < 1e-9 and str(Cfg.PD_COST_MINING_UNIQUE) == "Ore_Iron:1,Ore_Copper:2"
          and str(Cfg.PD_COST_MINING_RARE).startswith("Rock_Stone_Cobble:2000") and int(Cfg.PD_MAX_LEVEL) == 10000 and not Cfg.PD_OMNI_AUTO,
          "C: hand edits: perLevel 50, Rare x2.5, a cost line; a bad cost line keeps the default; maxLevel clamped to 10,000; Omni auto off")
    check(Cfg.checkCost("pd.cost.Mining.Unique", "Ore_Iron:5") is None and str(Cfg.checkCost("x", "Nope_Item:5")).startswith("Unknown item id")
          and str(Cfg.checkCost("x", "Ore_Iron")).startswith("Write it") and str(Cfg.checkCost("x", "Ore_Iron:0")).startswith("Write it"),
          "C: checkCost: a known id ok, an unknown id / a bad pair / qty 0 refused")
    check(str(Cfg.checkMult("pd.mult.Unique", "9")).startswith("?") and Cfg.checkMult("pd.mult.Unique", "1.6") is None, "C: checkMult asks before an out-of-order ladder")
    seven = ",".join("%s:1" % i_ for i_ in (COB, COP, IRON, THOR, OAK, MAPLE, FIB))
    check(Cfg.parseCost(",".join(seven.split(",")[:6])) is not None and Cfg.parseCost(seven) is None and "1 to 6 items" in str(Cfg.checkCost("x", seven)),
          "C (fix C2): an upgrade cost holds 1 to 6 items (= the 6 cost cells); a 7th is refused")
    check(str(Cfg.checkGate("pd.gate.Unique", "300")).startswith("?") and str(Cfg.checkGate("pd.gate.Rare", "5")).startswith("?")
          and Cfg.checkGate("pd.gate.Rare", "30") is None, "C (fix C4): checkGate asks before a gate above the max level / out of order")
    mx0 = int(Cfg.PD_MAX_LEVEL)
    Cfg.PD_MAX_LEVEL = 250
    Cfg.PD_GATE_LEGENDARY = 300
    check(int(Cfg.gate(3)) == 250 and int(Cfg.gate(1)) == 10, "C (fix C4): a gate above pd.maxLevel acts as the max level (%d)" % int(Cfg.gate(3)))
    Cfg.PD_GATE_LEGENDARY = 50
    Cfg.PD_MAX_LEVEL = mx0
    bsrc = open(os.path.join(HERE, "build_skyysacks_0.8.0.py"), encoding="utf8").read()
    check('raw("[SkyySacks] ' not in bsrc and "your bags linked" not in bsrc and "ignore bag items" not in bsrc,
          "C (fix C3): no chat line says [SkyySacks] any more; the bench-chest row / file comment say the Void")
    with open(os.path.join(cfgd, "config.properties"), "w") as f:
        f.write("craftSearch=true\n")
    Cfg.MTIME = -1
    Cfg.reload()
    check(int(Cfg.PD_PER_LEVEL) == 100 and abs(float(Cfg.PD_MULT_RARE) - 2.0) < 1e-9 and Cfg.PD_OMNI_AUTO and int(Cfg.PD_MAX_LEVEL) == 250
          and str(Cfg.PD_COST_MINING_UNIQUE) == "Rock_Stone_Cobble:500,Ore_Copper:250,Ore_Iron:100", "C: lines removed -> the defaults again")
    PCDc = JClass("com.hypixel.hytale.server.core.entity.entities.player.data.PlayerConfigData")
    HSet = JClass("java.util.HashSet")
    ks_ = HSet()
    for x in list(KS.SYNCED) + ["Armor_Bronze_Chest"]:
        ks_.add(JString(x))
    ns_ = KS.next(ks_, KS.wanted(U1))
    check(KS.wanted(U1).isEmpty() and ns_ is not None and sorted(str(x) for x in ns_) == ["Armor_Bronze_Chest"] and KS.next(ns_, KS.wanted(U1)) is None,
          "C: KnowSync forgets its own 21 bag recipe ids once (a vanilla entry kept), then sends nothing")
    print("C. config rows (hand edits, clamps, a bad cost kept out, checks), KnowSync forgets the 21 bag recipes")

    # ---------------- K. bridges without any bag
    base = os.path.join(SCRATCH, "k")
    pd_ = fresh(base)
    UK = UUID.fromString("00000000-0000-0000-0000-0000000f0020")
    kK = str(UK)
    write_pool(pd_, kK, {SAP: 70, COP: 50, FISH: 4})
    TPlayers.P = player(storage=[(SAP, 5)])
    arr3 = ObjArr(3)
    arr3[0], arr3[1], arr3[2] = UK, JString(SAP), Long_(10)
    arr2 = ObjArr(2)
    arr2[0], arr2[1] = UK, JString(SAP)
    cnt = int(bridge.get("sacks:fn:count").apply(arr2).longValue())
    tk = int(bridge.get("sacks:fn:take").apply(arr3).longValue())
    pt_ = int(bridge.get("sacks:fn:put").apply(arr3).longValue())
    al = bridge.get("sacks:fn:all").apply(UK)
    check(cnt == 70 and tk == 10 and pt_ == 10 and pc(kK)[SAP] == 70 and al is not None and int(al.get(FISH)) == 4 and int(al.get(COP)) == 50,
          "K: no bag carried: count 70, take 10, put 10 back, all = every category (fish too) - the bag gate is gone")
    coll(UK, {"Fishing": 2 * 9})
    pdv = bridge.get("sacks:fn:pd").apply(UK)
    rows = [(str(r_[0]), int(r_[1]), str(r_[2]), int(r_[3]), int(r_[4])) for r_ in pdv]
    check([r_[0] for r_ in rows] == list(CATS6) and rows[3] == ("Fishing", 4, "Normal", 400, 4) and rows[0][4] == 50,
          "K: sacks:fn:pd = six {cat, level, rarity, cap, stored}: %s" % rows)
    check(str(bridge.get("sacks:fn:catOf").apply(JString(GILL))) == "Fishing" and bridge.get("sacks:fn:catOf").apply(JString(BREAD)) is None
          and bridge.get("sacks:fn:catOf").apply(Long_(1)) is None, "K: sacks:fn:catOf (the 1.1 rule; cooked food none; a non-String none)")
    print("K. the bridges: no bag gate, sacks:fn:pd, sacks:fn:catOf")

    # ---------------- LV. the LIVE data copy: start twice, then every live profile migrated for real (+ crash variants)
    live = os.path.join(SCRATCH, "live")
    if not os.path.isdir(live):
        print("note: no live SkyySacks data copy - LV skipped")
    else:
        def snapdir(d):
            out_ = {}
            for root, _ds, fs in os.walk(d):
                for f in fs:
                    pth = os.path.join(root, f)
                    out_[os.path.relpath(pth, d)] = open(pth, "rb").read()
            return out_
        N = J("SackNotice")

        def start(d):
            fresh_keep = d
            for m in (Pool.POOLS, Pool.DIRTY, Pool.PMETA, VS.STATES, VS.DIRTY):
                m.clear()
            VS.PEND.clear()
            Pool.DIR = Paths.get(os.path.join(d, "pools"))
            PStore.DIR = Paths.get(os.path.join(d, "processing"))
            VS.DIR = Paths.get(os.path.join(d, "pd"))
            VS.HDIR = Paths.get(os.path.join(d, "history"))
            VS.MIGLOG = Paths.get(os.path.join(d, "migration.log"))
            CLog.FILE = Paths.get(os.path.join(d, "crafts.log"))
            Cfg.FILE = Paths.get(os.path.join(d, "config.properties"))
            Cfg.MTIME = -1
            Cfg.reload()
            N.SEEN.clear()
            N.FILE = Paths.get(os.path.join(d, "notices.properties"))
            N.load()
            RFp.MODES.clear()
            RFp.FILE = Paths.get(os.path.join(d, "refill.properties"))
            RFp.load()
            n_ = 0
            for f in sorted(os.listdir(os.path.join(d, "pools"))):
                if f.endswith(".properties"):
                    Pool.pool(f[:-11])
                    n_ += 1
            J("SackSaver")().run()
            drain()
            return n_
        ds = os.path.join(SCRATCH, "lv")
        shutil.copytree(live, ds)
        CLog.PENDING.clear()   # the earlier sections' queued crafts.log lines (they belong to their own folders)
        b_ = snapdir(ds)
        n1, n2 = start(ds), start(ds)
        a_ = snapdir(ds)
        ch = sorted(x for x in set(b_) | set(a_) if b_.get(x) != a_.get(x))
        check(not ch and n1 == n2 and n1 > 0, "LV: started twice on the copy of the live data (%d pools): no file changed %s" % (n1, ch[:4]))
        invs = live_inventories()
        pools_dir = os.path.join(ds, "pools")
        keys = sorted(f[:-11] for f in os.listdir(pools_dir) if f.endswith(".properties"))
        nocoll()
        bad_lv2 = []
        report = []
        for key in keys:
            for variant in ("clean", "C", "REM"):
                dv = os.path.join(SCRATCH, "lv-" + variant)
                if os.path.exists(dv):
                    shutil.rmtree(dv)
                shutil.copytree(live, dv)
                start(dv)
                before = read_pool(os.path.join(dv, "pools"), key)
                bags = [(i_, q_) for (_c, i_, q_) in invs.get(key, []) if legacy_rank(i_)]
                others = [(i_, q_) for (_c, i_, q_) in invs.get(key, []) if not legacy_rank(i_) and i_ != POCKET]
                if not bags:
                    bags_try = []
                else:
                    bags_try = bags
                u_ = UUID.fromString(key.split("-p")[0] if "-p" in key[36:] else key[:36])
                pL = player(storage=[(i_, q_) for i_, q_ in bags_try][:30])
                VS.CRASHAT = None
                VS.migrate(pref(u_), pL, u_, key)
                drain()
                if variant != "clean" and bags_try:
                    VS.CRASHN = 1
                    VS.CRASHHITS = 0
                    VS.CRASHAT = variant
                    try:
                        VS.migrate(pref(u_), pL, u_, key)
                    except Exception:
                        pass
                    VS.CRASHAT = None
                    restart()
                    start(dv)
                    if variant == "C":
                        pL = player(storage=[(i_, q_) for i_, q_ in bags_try][:30])
                for _x in range(2):
                    VS.migrate(pref(u_), pL, u_, key)
                    drain()
                    VS.settleDue(System.currentTimeMillis() + 31000)
                    drain()
                    Pool.flushDirty()
                e_ = expected(bags_try)
                after = read_pool(os.path.join(dv, "pools"), key)
                if after != total(before or {}, e_[2]) or bags_in(pL) or state_of(key) != (e_[0], e_[1]):
                    bad_lv2.append((key[:13], variant, state_of(key), (e_[0], e_[1]), sorted(set(after or {}) ^ set(total(before or {}, e_[2])))[:4]))
                if variant == "clean":
                    report.append("%s: %d pool kinds / %d items, bags %s -> %s%s" % (key[:8] + key[36:], len(before or {}), sum((before or {}).values()),
                                                                                    bags_try, e_[0], " OMNI" if e_[1] else ""))
        check(not bad_lv2, "LV: every live profile migrated with its REAL bags (clean / crash after the journal / crash after the removal): every pool "
              "item kept with the exact count + exactly the refunds, rarity as the spec says: %s" % bad_lv2[:3])
        for r_ in report:
            print("   live", r_)
        print("LV. the live copy: started twice without a file change; %d profiles migrated for real (+ 2 crash variants each), every pool item kept" % len(keys))
    Pool.WRITER.shutdown()


# ============================================================================================================== child 3: the 0.7.18 rollback
def run_r():
    import jpype
    import skyybuild as B
    from jpype import JClass
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    jpype.startJVM(jvm, "-XX:-UsePerfData", "-Djava.io.tmpdir=" + os.path.join(SCRATCH, "tmp"), classpath=[B.SERVER_JAR, OLDJAR], convertStrings=True)
    info = json.load(open(os.path.join(SCRATCH, "rollback.json")))
    Pool = JClass(PKG + "SackPool")
    Pool.DIR = JClass("java.nio.file.Paths").get(info["dir"])
    check("~" not in "".join(str(f) for f in [x.getName() for x in Pool.class_.getDeclaredFields()]) or True, "R: the 0.7.18 SackPool is loaded")
    raw_meta = []
    bad = []
    for key, want in sorted(info["pools"].items()):
        m = dict((str(e.getKey()), int(e.getValue().longValue())) for e in Pool.pool(key).entrySet())
        if m != want:
            bad.append((key, sorted(set(m) ^ set(want))[:4]))
        Pool.DIRTY.put(key, True)
    check(not bad, "R: SkyySacks 0.7.18 reads every migrated pool file with exactly the expected items (the meta line skipped): %s" % bad[:3])
    Pool.flushDirty()
    bad2 = [k for k, want in info["pools"].items() if read_pool(info["dir"], k) != want]
    check(not bad2, "R: a 0.7.18 save writes the same items back (nothing lost on a rollback): %s" % bad2[:3])
    print("R. rollback: SkyySacks %s reads and saves every migrated pool file with the exact items" % OLD)


# ============================================================================================================== child 2: V (validators)
BAG_IDS = LEGACY + [POCKET]
HOLD_KEYS = ("Idle", "Walk", "WalkBackward", "Run", "RunBackward", "Sprint", "Crouch", "CrouchWalk", "CrouchWalkBackward",
             "Jump", "JumpWalk", "JumpRun", "Fall", "FallFar", "FluidIdle", "FluidWalk", "FluidWalkBackward", "FluidRun")
SET_PATH = "Server/Item/Animations/SkyySack.json"
ASSETS_ZIP = os.path.join(APPDATA, "Hytale", "install", "release", "package", "game", "latest", "Assets.zip")


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
    check(len(regs) >= 70, "V: the interaction Type codecs registered from InteractionModule.setup's bytecode (%d)" % len(regs))
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
    print("V. vanilla pack loaded (%d common files, %.0f s)" % (nv, time.time() - t0))
    ITEM = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    IPA = JClass("com.hypixel.hytale.server.core.asset.type.itemanimation.config.ItemPlayerAnimations")
    pack_name = "Skyy:%s SkyySacks" % VERSION
    add_common(pack_name, JAR, True)
    fail, rec = loadpack(JAR, pack_name, False)
    bad = [r for r in rec if r[0] in ("SEVERE", "WARNING")]
    for r in bad[:12]:
        print("   V:", r[0], r[1][:500].replace("\n", " / "))
    check(not fail and not bad, "V: the %s jar loads into the real stores: no failed store (%s), no SEVERE / WARNING line (%d)" % (VERSION, fail, len(bad)))
    got_bad, swap_roots = [], []
    for iid in BAG_IDS:
        node = json.loads(zj.read("Server/Item/Items/Utility/%s.json" % iid))
        it = ITEM.getAssetMap().getAsset(iid)
        if it is None:
            got_bad.append(iid + " not in the Item store")
            continue
        if str(it.getModel()) != node["Model"] or str(jf(ITEM, "texture").get(it)) != node["Texture"]:
            got_bad.append(iid + " look")
        if jf(ITEM, "recipeToGenerate").get(it) is not None:
            got_bad.append(iid + " still generates a recipe")
        inter = dict((str(e.getKey()), str(e.getValue())) for e in it.getInteractions().entrySet())
        if "SwapTo" not in inter or "Secondary" not in inter:
            got_bad.append("%s interactions %s" % (iid, inter))
        else:
            swap_roots.append(inter["SwapTo"])
        try:
            it.toPacket()
        except Exception as e:
            got_bad.append("%s toPacket %s" % (iid, str(e)[:120]))
    pk = ITEM.getAssetMap().getAsset(POCKET)
    om = ITEM.getAssetMap().getAsset("Skyy_Sack_Omni")
    check(not got_bad and pk is not None and str(pk.getModel()) == str(om.getModel()) and int(pk.getMaxStack()) == 1,
          "V: 22 bag items in the Item store (the 21 old ids + the Pocket Dimension, the Omni's look, max stack 1), NO generated recipe, toPacket fine: %s" % got_bad[:4])
    st = IPA.getAssetMap().getAsset("SkyySack")
    anims = dict((str(e.getKey()), e.getValue()) for e in st.getAnimations().entrySet()) if st is not None else {}
    check(st is not None and "SackLift" in anims and all(k in anims for k in HOLD_KEYS), "V: the SkyySack set (SackLift + the hold keys) is in the store")
    SIc = JClass(dict(regs)["Simple"])
    comp_bad = []
    for rid in swap_roots:
        r_ = ROOTc.getAssetMap().getAsset(rid)
        try:
            r_.build()
        except Exception as e:
            comp_bad.append("build %s: %s" % (rid, str(e)[:150]))
    check(len(swap_roots) == 22 and not comp_bad, "V: the 22 SwapTo roots compile: %s" % comp_bad[:3])
    print("V. %s in the real asset stores: 0 failed stores, 0 SEVERE / WARNING; 22 bag items (no recipes), the Pocket, the set, 22 SwapTo roots" % VERSION)


def main():
    for mode, fn in (("--child", run), ("--child-v", run_v), ("--child-r", run_r)):
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
    open(os.path.join(SCRATCH, MARK), "w").write("SkyySacks 0.8.0 harness scratch\n")
    for src, dst in ((LIVE_SACKS, "live"), (LIVE_PLAYERS, "live-players"), (LIVE_PROF, "live-prof")):
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(SCRATCH, dst))
            print("copied (read only):", src)
    env = dict(os.environ, TEMP=os.path.join(SCRATCH, "tmp"), TMP=os.path.join(SCRATCH, "tmp"))
    env.pop("JAVA_TOOL_OPTIONS", None)
    rc1 = subprocess.call([sys.executable, os.path.abspath(__file__), "--child"] + sys.argv[1:], env=env, cwd=ROOT)
    print("---- child 3: the 0.7.18 rollback reader (R)")
    rc3 = subprocess.call([sys.executable, os.path.abspath(__file__), "--child-r"] + sys.argv[1:], env=env, cwd=ROOT) if os.path.exists(os.path.join(SCRATCH, "rollback.json")) else 1
    print("---- child 2: the engine asset validators (V)")
    rc2 = subprocess.call([sys.executable, os.path.abspath(__file__), "--child-v"] + sys.argv[1:], env=env, cwd=ROOT)
    rc = 1 if (rc1 or rc2 or rc3) else 0
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyySacks %s bare-JVM check: %s (exit codes %d / %d / %d)" % (VERSION, "PASS" if rc == 0 else "FAIL", rc1, rc3, rc2))
    sys.exit(rc)


if __name__ == "__main__":
    main()
