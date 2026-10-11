"""Harness for SkyyGear 0.2.23 (THE /smithing HUB; tools/gear_0_2_23_patch.py header). Build first:
    python tools/gear_0_2_23_patch.py && python SkyyGear/build_skyygear_0.2.23.py

    python SkyyGear/test_skyygear_0.2.23.py [--jar <SkyyGear-0.2.23.jar>] [--old <SkyyGear-0.2.22.jar>] [--armory <SkyyArmory-0.1.20.jar>]
                                            [--acc <SkyyAccessories-0.5.11.jar>] [--mt <Multitools-1.2.9.jar>] [--sacks <SkyySacks-0.7.17.jar>]
                                            [--root <scratch root>] [--keep]

The 0.2.11 harness's helpers (verify A, the bare-server boot, the audit AA) and the 0.2.22 stand-ins (MergeFail, FakeReforgePage,
FakeMultiPage, FakePR) are loaded from their files; this harness adds FakeSmithPage and the CONTRACT STAND-INS of research/Requip-Smithing-
Spec.md section 5 (SkyySacks 0.7.17 craftList / craftHave / craftPay / craftRefund / craftCommit + count / take / put / commit; SkyyWardrobe
0.2 canDeposit / depositSlot / deposit / list / fetch / gone) written in Python against the REAL inventory containers. SkyyArmory 0.1.20,
SkyyAccessories 0.5.11 (repo jars) and Multitools 1.2.9 (UserData/Mods, read-only) are COPIED into scratch and loaded as their own packs, so
the recipe list is read from the real store (vanilla + Armory + SkyyGear recipes) with the real bench accessory items present. When the
SkyySacks 0.7.17 jar is on disk its REAL craft bridge is driven too (R: SackBridge with the harness player seam, a scratch pool file).
  S  non-class entries 0.2.22 -> 0.2.23: only the manifest changed; classes added = GearSmith, SmithPage, SmithCmd, SmithFn
  A  every class loads + verifies (-Xverify:all)
  H  THE HUB EXECUTED (one booted engine): recipes() vs an independent pass over the live store AND the Assets.zip / Armory JSON; categories /
     sets / families / names / figure; the class filter vs SkyyClasses 0.1.19's live prefixes + armor types (gear:fn:classShow); the craft
     transaction (room first, pay, deliver inventory / Requip depositSlot / Requip deposit, refunds on every failure path, crash = only
     materials lost, XP once, rarity like a bench craft, plain when part.craft is off, gates); Craft every missing piece; F1 key copy on
     Upgrade + Merge (+ wardrobe:fn:gone); Upgrade materials from the bags (take / put back / commit); the pages (Craft tab cards + piece
     page + left column + 1080p budget via the skyyui kit, every click; the Reforge / Upgrade lists' Requip rows, fetch, Return to Requip,
     the Craft tab click on the Reforge / Multitool pages); /smithing (+ /smith), gear:fn:smithing; bridges ABSENT and PRESENT
  R  (when SkyySacks-0.7.17.jar exists) the REAL SkyySacks craft bridge: craftList / craftHave / craftPay / refund through GearSmith.craft
  C  CLASS COMPARE 0.2.22 -> 0.2.23 (javassist members)
  D  START TWICE on a scratch COPY of the live Skyy_SkyyGear folder with each jar: the 2nd start changes nothing; 0.2.23 writes the same
     config.properties as 0.2.22 (absent rows = defaults, no one-time update)
  AA THE ENGINE-ACCESS AUDIT
Scratch: tools/dev/scratch/smithing/harness (or --root) (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B

VERSION = "0.2.23"
OLD_VERSION = "0.2.22"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCR_ROOT = os.path.abspath(arg("--root", os.path.join(TOOLS, "dev", "scratch", "smithing")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyGear-%s.jar" % OLD_VERSION)))      # read only
AR_SRC = os.path.abspath(arg("--armory", os.path.join(ROOT, "SkyyArmory", "SkyyArmory-0.1.20.jar")))
AC_SRC = os.path.abspath(arg("--acc", os.path.join(ROOT, "SkyyAccessories", "SkyyAccessories-0.5.11.jar")))
MT_SRC = os.path.abspath(arg("--mt", os.path.join(B.MODS_DIR, "Multitools-1.2.9.jar")))
SK_SRC = os.path.abspath(arg("--sacks", os.path.join(ROOT, "SkyySacks", "SkyySacks-0.7.17.jar")))
WD_SRC = os.path.join(ROOT, "SkyyWardrobe", "SkyyWardrobe-0.2.jar")
AR_JAR = os.path.join(SCRATCH, "packs", "SkyyArmory-0.1.20.jar")
AC_JAR = os.path.join(SCRATCH, "packs", "SkyyAccessories-0.5.11.jar")
MT_JAR = os.path.join(SCRATCH, "packs", "Multitools-1.2.9.jar")
SK_JAR = os.path.join(SCRATCH, "packs", "SkyySacks-0.7.17.jar")
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyGear")
PKG = "com.skyy.gear."
SOUL = ["Weapon_Wand_SoulOrb"] + ["Weapon_Wand_SoulCage_%s" % m for m in ("Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")]
NEW_CLASSES = {"GearSmith", "SmithPage", "SmithCmd", "SmithFn"}
MULTI_PRE = "Tool_Hatchet_Pickaxe_Multitool_"
# SkyyClasses 0.1.19 CLASSES (build_skyyclasses_0.1.19.py, read at harness time) -> the bridge values it publishes
CLS_PY = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.19.py")

_H211 = os.path.join(HERE, "test_skyygear_0.2.11.py")
_t = open(_H211, encoding="utf-8").read()
_cut = _t.rindex('if __name__ == "__main__":')
H = {"__name__": "skyygear_h211", "__file__": _H211, "__builtins__": __builtins__}
exec(compile(_t[:_cut], _H211 + " (helpers)", "exec"), H)
H.update({"JAR": JAR, "OLD_JAR": OLD_JAR, "SCRATCH": SCRATCH, "FAKE_DIR": os.path.join(SCRATCH, "fake"), "VERSION": VERSION})
FAKE_DIR = H["FAKE_DIR"]
FAKE_PKG = H["FAKE_PKG"]
Child, _jvm, jar_classes = H["Child"], H["_jvm"], H["jar_classes"]
_H222 = os.path.join(HERE, "test_skyygear_0.2.22.py")
_t2 = open(_H222, encoding="utf-8").read()
_c2 = _t2.index("# ====================================================================================================== F+: this round's stand-ins")
_e2 = _t2.index("# ====================================================================================================== T + R + U + N + P")
H22 = {"__name__": "skyygear_h222", "__builtins__": __builtins__, "H": H, "FAKE_PKG": FAKE_PKG, "PKG": PKG, "JAR": JAR, "B": B, "os": os}
exec(compile(_t2[_c2:_e2], _H222 + " (stand-ins)", "exec"), H22)
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def classes_py():
    """SkyyClasses 0.1.19's CLASSES table (name, enabled, weapon prefixes) - read from its build script text (never run)"""
    t = open(CLS_PY, encoding="utf-8").read()
    i = t.index("CLASSES = [")
    out = []
    for m in re.finditer(r'\{"name": "(\w+)", "skill": "(\w+)".*?"enabled": (True|False).*?"weapons": \[(.*?)\]\s*,', t[i:i + 20000], re.S):
        pre = re.findall(r'\("([A-Za-z_]+)", "', m.group(4))
        out.append((m.group(1), m.group(2), m.group(3) == "True", pre))
    free = re.findall(r'\("([A-Za-z_]+)", "', t[t.index("FREE_WEAPONS = ["):t.index("]", t.index("FREE_WEAPONS = ["))])
    return out, free


# ====================================================================================================== S: non-class entries
def run_assets():
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    ea = dict((n, zo.read(n)) for n in zo.namelist() if not n.endswith(".class"))
    eb = dict((n, zn.read(n)) for n in zn.namelist() if not n.endswith(".class"))
    added = sorted(set(eb) - set(ea))
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n])
    check(not added and not (set(ea) - set(eb)) and changed == ["manifest.json"] and b'"0.2.23"' in eb["manifest.json"]
          and b"/smithing = one page" in eb["manifest.json"],
          "S: 0.2.22 -> 0.2.23: no file added / removed, only the manifest changed (version + the smithing words): + %s ~ %s" % (added[:3], changed[:3]))
    ca = set(n for n in zo.namelist() if n.endswith(".class"))
    cb = set(n for n in zn.namelist() if n.endswith(".class"))
    check(not (ca - cb) and set(n.split("/")[-1][:-6] for n in cb - ca) == NEW_CLASSES,
          "S: classes added = GearSmith, SmithPage, SmithCmd, SmithFn; none removed: + %s - %s" % (sorted(cb - ca), sorted(ca - cb)))
    names = set(zn.namelist())
    check(not [n for n in names if "SoulCage" in n or "inkblindcat" in n.lower() or "Skyy_Accessory" in n or n.endswith(".ui")],
          "S: no pack mod / SkyyAccessories file is shipped or overridden (runtime ids only), no .ui file")


# ====================================================================================================== F+: this round's stand-ins
def run_mkfake3(out_dir):
    H22["run_mkfake2"](out_dir)
    from jpype import JClass
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(JAR)
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    fp = cp.makeClass(FAKE_PKG + ".FakeSmithPage")
    fp.setSuperclass(cp.get(PKG + "SmithPage"))
    fp.addField(CtField.make("public int rebuilds;", fp))
    fp.addField(CtField.make("public int closes;", fp))
    fp.addConstructor(CtNewConstructor.make("public FakeSmithPage(com.hypixel.hytale.server.core.universe.PlayerRef pr) { super(pr); }", fp))
    fp.addMethod(CtNewMethod.make("public void rebuild() { this.rebuilds = this.rebuilds + 1; }", fp))
    fp.addMethod(CtNewMethod.make("public void close() { this.closes = this.closes + 1; }", fp))
    fp.writeFile(out_dir)
    print("F+. FakeSmithPage written")


# ====================================================================================================== H: the hub (one booted engine)
def run_hub(out):
    from jpype import JClass, JInt, JShort, JLong, JByte, JImplements, JOverride, JObject, JArray, JString
    import jpype
    K = Child(out)
    cp_ = [B.SERVER_JAR, B.JAVASSIST, JAR, FAKE_DIR]
    _jvm(cp_, verify=True, big=True)
    E = H["engine_boot"](K)
    ITEM, us, jf = E["ITEM"], E["us"], E["jf"]
    K.check(set(E["fail"]) <= set(E["vfail"]), "E: the jar as its own pack: no failed store of its own (%s vs vanilla %s)" % (E["fail"], E["vfail"]))
    CRR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    HAL = JClass("java.util.ArrayList")
    AZP = os.path.join(os.path.dirname(os.path.dirname(B.SERVER_JAR)), "Assets.zip")
    afs = JClass("java.nio.file.FileSystems").newFileSystem(JClass("java.nio.file.Paths").get(AZP), JClass("java.util.HashMap")())
    with zipfile.ZipFile(AZP) as az_:
        tnames = [n for n in az_.namelist() if n.startswith("Server/Item/Items/Tool/") and n.endswith(".json")]
    tl_ = HAL()
    for n in tnames:
        tl_.add(afs.getPath("/" + n))
    ITEM.getAssetStore().loadAssetsFromPaths("Hytale:Hytale", tl_)

    def gen_recipes(items):
        lst = HAL()
        for it in items:
            if it is not None and it.hasRecipesToGenerate():
                it.collectRecipesToGenerate(lst)
        if lst.size() > 0:
            CRR.getAssetStore().loadAssets("Hytale:Hytale", lst)
        return int(lst.size())
    gen_recipes(list(ITEM.getAssetMap().getAssetMap().values()))
    CAR = JClass("com.hypixel.hytale.server.core.asset.common.CommonAssetRegistry")
    FCA = JClass("com.hypixel.hytale.server.core.asset.common.asset.FileCommonAsset")

    def addpack(jar, name):
        fs_ = JClass("java.nio.file.FileSystems").newFileSystem(JClass("java.nio.file.Paths").get(jar), JClass("java.util.HashMap")())
        with zipfile.ZipFile(jar) as z_:
            for nm in z_.namelist():
                if nm.startswith("Common/") and not nm.endswith("/"):
                    CAR.addCommonAsset(name, FCA(fs_.getPath("/" + nm), nm[len("Common/"):], hashlib.sha256(z_.read(nm)).hexdigest(), None))
        return E["loadpack"](jar, name, False)
    afail, _arec = addpack(AR_JAR, "Skyy:SkyyArmory")
    with zipfile.ZipFile(AR_JAR) as z_:
        ar_ids = [os.path.basename(n)[:-5] for n in z_.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json")]
    n_ar = gen_recipes([ITEM.getAssetMap().getAsset(i) for i in ar_ids])
    K.check(ITEM.getAssetMap().getAsset(SOUL[1]) is not None and n_ar >= 20, "E: SkyyArmory 0.1.20 (scratch copy) loaded as its own pack: %d recipes (failed %s)" % (n_ar, afail))
    have_acc = os.path.isfile(AC_JAR)
    if have_acc:
        cfail, _crec = addpack(AC_JAR, "Skyy:SkyyAccessories")
        with zipfile.ZipFile(AC_JAR) as z_:
            ac_ids = [os.path.basename(n)[:-5] for n in z_.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json")]
        gen_recipes([ITEM.getAssetMap().getAsset(i) for i in ac_ids])
        have_acc = ITEM.getAssetMap().getAsset("Skyy_Accessory_Workbench_T1") is not None
        K.notes.append("SkyyAccessories 0.5.11 pack: %d item files, failed stores %s, accessory items %s" % (len(ac_ids), cfail, have_acc))
    have_mt = os.path.isfile(MT_JAR)
    if have_mt:
        addpack(MT_JAR, "IBC:Multitools")
        gen_recipes([ITEM.getAssetMap().getAsset(MULTI_PRE + t) for t in ("Crude", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")])
    P = lambda n: JClass(PKG + n)
    Cfg, Gear, Up, Merge, Data, Roll, Forge, Stamp, Lvl, Defs, Log, View, Ui, Sm, Gate = (
        P("GearCfg"), P("Gear"), P("GearUp"), P("GearMerge"), P("GearData"), P("GearRoll"), P("GearForge"), P("GearStamp"), P("GearLevel"),
        P("GearDefs"), P("GearLog"), P("GearView"), P("GearUi"), P("GearSmith"), P("GearGate"))
    Props = JClass("java.util.Properties")
    SR = JClass("java.io.StringReader")
    FRESH = str(Cfg.defaultsText())

    def apply(**kv):
        p = Props()
        p.load(SR(FRESH))
        for k, v in kv.items():
            p.setProperty(k.replace("__", "."), v)
        Cfg.apply(p, False)
    apply()
    K.check(bool(Cfg.SMITH_ON) and "part.smithing=true" in FRESH and ("smith.classArmor=" + str(Cfg.SMITH_ARM)) in FRESH
            and str(Cfg.SMITH_ARM).startswith("Warrior:Heavy,Berserker:Heavy,Archer:Light"),
            "E: the fresh config has part.smithing=true and smith.classArmor=%s" % str(Cfg.SMITH_ARM))
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    BD = JClass("org.bson.BsonDocument")
    BS, BI32 = JClass("org.bson.BsonString"), JClass("org.bson.BsonInt32")
    UUID = JClass("java.util.UUID")
    U1 = UUID.fromString("00000000-0000-0000-0000-0000000000a1")
    Long_, Int_, Bool_ = JClass("java.lang.Long"), JClass("java.lang.Integer"), JClass("java.lang.Boolean")
    ObjArr = JArray(JClass("java.lang.Object"))
    XP = []

    @JImplements("java.util.function.Function")
    class AddXp(object):
        @JOverride
        def apply(self, o):
            XP.append((str(o[1]), int(o[2].longValue()), str(o[3])))
            return JObject(True, Bool_)
    br = Gear.bridge()
    br.put("skill:fn:addxp", AddXp())

    def stack(iid, q=1):
        return IS(iid, JInt(q))

    def rolled(iid, r, lvl=None):
        L_ = int(Roll.craftLevel(iid, U1)) if lvl is None else lvl
        return Roll.newDoc(iid, JInt(r), True, "craft", JInt(L_))

    def gear(iid, d, q=1):
        s_ = stack(iid, q)
        return s_ if d is None else Data.put(s_, d, None)

    def rid_of(d):
        return str(Defs.R_ID[int(Data.rarity(d))])

    def stamp(s_, eid):
        md = s_.getMetadata()
        md = BD() if md is None else md.clone()
        md.put("SkyyRequip", BD("e", BS(eid)))
        return s_.withMetadata(md)

    # ---- the inventory (the 0.2.11 stand-in shape)
    INV = JClass("com.hypixel.hytale.server.core.inventory.Inventory")
    ICOMP = "com.hypixel.hytale.server.core.inventory.InventoryComponent$"
    MF = JClass(FAKE_PKG + ".MergeFail")

    def comp(kind, cont):
        Cc = JClass(ICOMP + kind)
        for args in ((cont, JByte(0)), (cont,)):
            try:
                return Cc(*args)
            except Exception:
                pass
        o_ = us.allocateInstance(Cc.class_)
        jf(Cc, "inventory").set(o_, cont)
        return o_
    SEC = {"hotbar": 0, "storage": 1, "backpack": 2, "armor": 3, "utility": 4, "tools": 5}

    def mkinv(fail=()):
        inv_ = INV()
        sz = {"hotbar": 9, "storage": 36, "backpack": 9, "armor": 4, "utility": 4, "tools": 4}
        cs_ = dict((k_, MF(JShort(n_)) if k_ in fail else SIC(JShort(n_))) for k_, n_ in sz.items())
        for f_, kind in (("hotbar", "Hotbar"), ("storage", "Storage"), ("backpack", "Backpack"), ("armor", "Armor"), ("utility", "Utility"), ("tools", "Tool")):
            jf(INV, f_).set(inv_, comp(kind, cs_[f_]))
        return inv_, cs_

    def at(cs_, sec, i):
        s_ = cs_[sec].getItemStack(JShort(i))
        return None if s_ is None or s_.isEmpty() else s_

    def cnt(inv_, ids):
        all_ = Stamp.allOf(inv_)
        return dict((x, int(Stamp.countId(all_, x))) for x in ids)

    def fill(cs_, sec, n, iid="Ingredient_Stick"):
        for i_ in range(n):
            cs_[sec].setItemStackForSlot(JShort(i_), stack(iid, 3))

    GLF = os.path.join(SCRATCH, "gear.log")

    def disk():
        if not os.path.isfile(GLF):
            return []
        with open(GLF, encoding="utf-8") as f_:
            t_ = f_.read()
        os.remove(GLF)
        return [l_ for l_ in t_.split("\n") if l_.strip()]

    def logs():
        # flush (take + write under WLOCK) first: a scheduler write racing a plain take() could hide a line from both reads
        Log.flush()
        return disk() + [l_ for l_ in str(Log.take()).split("\n") if l_.strip()]
    Log.FILE = JClass("java.nio.file.Paths").get(GLF)
    logs()

    # ================================================================ CONTRACT STAND-INS (spec section 5, the SkyySacks 0.7.17 shapes)
    class SackState(object):
        inv = None
        bag = {}
        allowed = None            # None = everything usable; else a set of recipe ids
        receipts = {}
        log = []
        pay_fail = None           # a reason -> craftPay refuses
        take_short = 0            # take() gives this much less
        surplus = None            # review fix FX1: an item id -> craftPay takes 1 extra of it and puts it back into the first free storage slot (giveSurplus)
        haves = []                # review fix FX2: every craftHave rid
        seq = [0]

    S = SackState

    def recipe(rid):
        o_ = CRR.getAssetMap().getAsset(rid)
        return o_

    def inputs(rid):
        out_ = []
        for q in recipe(rid).getInput():
            if q is None or q.getQuantity() < 1:
                continue
            out_.append((str(q.getItemId()) if q.getItemId() is not None else "res:" + str(q.getResourceTypeId()), int(q.getQuantity())))
        return out_

    def inv_have(iid):
        return int(Up.have(S.inv, iid)) if S.inv is not None and not iid.startswith("res:") else 0

    def inv_take(iid, n):
        """the inventory part, storage / backpack / hotbar, undocumented stacks only; returns taken"""
        left = n
        for c_ in Up.matSecs(S.inv):
            for i_ in range(int(c_.getCapacity())):
                if left <= 0:
                    return n
                x = c_.getItemStack(JShort(i_))
                if not bool(Up.usable(x, iid)):
                    continue
                q = int(x.getQuantity())
                t_ = min(q, left)
                if t_ >= q:
                    c_.removeItemStackFromSlot(JShort(i_))
                else:
                    c_.setItemStackForSlot(JShort(i_), x.withQuantity(JInt(q - t_)))
                left -= t_
        return n - left

    def inv_give(iid, n):
        S.inv.getStorage().addItemStack(stack(iid, n))

    @JImplements("java.util.function.Function")
    class FList(object):
        @JOverride
        def apply(self, o):
            S.log.append(("list", str(o[1])))
            ids = []
            for r_ in Sm.recipes():
                rid = str(r_[0])
                if S.allowed is None or rid in S.allowed:
                    ids.append(rid)
            a_ = JArray(JString)(len(ids))
            for i_, x in enumerate(ids):
                a_[i_] = x
            return a_

    @JImplements("java.util.function.Function")
    class FHave(object):
        @JOverride
        def apply(self, o):
            rid = str(o[1])
            S.haves.append(rid)
            ins = inputs(rid)
            ids = JArray(JString)(len(ins))
            hv = JArray(Long_)(len(ins))
            nd = JArray(Long_)(len(ins))
            times = 10 ** 9
            for i_, (iid, q) in enumerate(ins):
                h_ = inv_have(iid) + S.bag.get(iid, 0)
                ids[i_], hv[i_], nd[i_] = iid, Long_(h_), Long_(q)
                times = min(times, h_ // q)
            return JArray(JClass("java.lang.Object"))([Long_(times if ins else 0), ids, hv, nd])

    @JImplements("java.util.function.Function")
    class FPay(object):
        @JOverride
        def apply(self, o):
            rid, times = str(o[1]), int(o[2])
            S.log.append(("pay", rid))
            if S.pay_fail:
                return JArray(JClass("java.lang.Object"))([Long_(0), None, S.pay_fail])
            ins = inputs(rid)
            for iid, q in ins:
                if inv_have(iid) + S.bag.get(iid, 0) < q * times:
                    return JArray(JClass("java.lang.Object"))([Long_(0), None, "not enough materials"])
            took_i, took_b = {}, {}
            for iid, q in ins:
                need = q * times
                ti = inv_take(iid, min(need, inv_have(iid)))
                tb = need - ti
                S.bag[iid] = S.bag.get(iid, 0) - tb
                took_i[iid], took_b[iid] = ti, tb
            if S.surplus is not None:          # SkyySacks giveSurplus: whole items worth more than needed -> the extra back via addItemStack
                if inv_take(S.surplus, 1) == 1:
                    fs_ = int(Sm.freeSlot(S.inv.getStorage()))
                    S.inv.getStorage().setItemStackForSlot(JShort(fs_), stack(S.surplus, 1))
                    S.log.append(("surplus", fs_))
            S.seq[0] += 1
            rc = "rc%d" % S.seq[0]
            S.receipts[rc] = {"inv": took_i, "bag": took_b, "state": "open", "rid": rid}
            return JArray(JClass("java.lang.Object"))([Long_(times), rc, None])

    @JImplements("java.util.function.Function")
    class FRefund(object):
        @JOverride
        def apply(self, o):
            rc = None if o[1] is None else str(o[1])
            S.log.append(("refund", rc))
            e_ = S.receipts.get(rc)
            if e_ is None or e_["state"] != "open":
                return Long_(0)
            e_["state"] = "refunded"
            tot = 0
            for iid, n_ in e_["inv"].items():
                if n_ > 0:
                    inv_give(iid, n_)
                    tot += n_
            for iid, n_ in e_["bag"].items():
                S.bag[iid] = S.bag.get(iid, 0) + n_
                tot += n_
            return Long_(tot)

    @JImplements("java.util.function.Function")
    class FCommit(object):
        @JOverride
        def apply(self, o):
            rc = str(o[1])
            S.log.append(("commit", rc))
            e_ = S.receipts.get(rc)
            if e_ is None or e_["state"] != "open":
                return JObject(False, Bool_)
            e_["state"] = "committed"
            return JObject(True, Bool_)

    @JImplements("java.util.function.Function")
    class FCount(object):
        @JOverride
        def apply(self, o):
            return Long_(S.bag.get(str(o[1]), 0))

    @JImplements("java.util.function.Function")
    class FTake(object):
        @JOverride
        def apply(self, o):
            iid, n_ = str(o[1]), int(o[2])
            S.log.append(("take", iid, n_))
            t_ = max(0, min(n_ - S.take_short, S.bag.get(iid, 0)))
            S.bag[iid] = S.bag.get(iid, 0) - t_
            return Long_(t_)

    @JImplements("java.util.function.Function")
    class FPut(object):
        @JOverride
        def apply(self, o):
            iid, n_ = str(o[1]), int(o[2])
            S.log.append(("put", iid, n_))
            S.bag[iid] = S.bag.get(iid, 0) + n_
            return Long_(n_)

    @JImplements("java.util.function.Function")
    class FBagCommit(object):
        @JOverride
        def apply(self, o):
            S.log.append(("bagcommit", str(o[1]), int(o[2])))
            return Long_(int(o[2]))
    @JImplements("java.util.function.Function")
    class FAll(object):          # FIXER 2: sacks:fn:all UUID -> HashMap itemId -> Long (the deposit evidence diff)
        @JOverride
        def apply(self, o):
            m_ = JClass("java.util.HashMap")()
            for k_, v_ in S.bag.items():
                m_.put(JString(k_), Long_(v_))
            return m_
    SACKS = {"sacks:fn:craftList": FList(), "sacks:fn:craftHave": FHave(), "sacks:fn:craftPay": FPay(), "sacks:fn:craftRefund": FRefund(),
             "sacks:fn:craftCommit": FCommit(), "sacks:fn:count": FCount(), "sacks:fn:take": FTake(), "sacks:fn:put": FPut(),
             "sacks:fn:commit": FBagCommit(), "sacks:fn:all": FAll()}

    class WdState(object):
        inv = None
        pool = {}                 # eid -> (space, stack)
        out = {}                  # eid -> True (OUT)
        full = None               # canDeposit reason
        slot_refuse = None        # depositSlot refusal reason
        dep_refuse = None         # deposit refusal reason
        lists = [0]               # review fix FX2: wardrobe:fn:list calls
        log = []
        seq = [0]
    W = WdState

    def wd_space(iid):
        return "armor" if int(Data.slotOf(iid)) == 2 else "items"

    def wd_new():
        W.seq[0] += 1
        return "%08x" % W.seq[0]

    @JImplements("java.util.function.Function")
    class WCan(object):
        @JOverride
        def apply(self, o):
            W.log.append(("can", str(o[1])))
            return W.full

    @JImplements("java.util.function.Function")
    class WSlot(object):
        @JOverride
        def apply(self, o):
            sec, sl = str(o[1]), int(o[2])
            W.log.append(("slot", sec, sl))
            if W.slot_refuse:
                return "refused:" + W.slot_refuse
            c_ = Stamp.section(W.inv, JInt(SEC[sec]))
            x = c_.getItemStack(JShort(sl))
            if x is None or x.isEmpty():
                return "refused:empty slot"
            e_ = Data.eidOf(x)
            eid = str(e_) if e_ is not None else wd_new()
            c_.removeItemStackFromSlot(JShort(sl))
            W.pool[eid] = (wd_space(str(x.getItemId())), stamp(x, eid))
            W.out.pop(eid, None)
            return "eid:" + eid

    @JImplements("java.util.function.Function")
    class WDep(object):
        @JOverride
        def apply(self, o):
            x, src, ev = o[1], str(o[2]), str(o[3])
            W.log.append(("dep", src, ev))
            if W.dep_refuse:
                return "refused:" + W.dep_refuse
            eid = wd_new()
            W.pool[eid] = (wd_space(str(x.getItemId())), stamp(x, eid))
            return "eid:" + eid

    @JImplements("java.util.function.Function")
    class WList(object):
        @JOverride
        def apply(self, o):
            sp = str(o[1])
            W.lists[0] += 1
            rows = [(e_, s_) for e_, (spc, s_) in sorted(W.pool.items()) if sp in ("all", spc)]
            a_ = ObjArr(len(rows))
            for i_, (e_, s_) in enumerate(rows):
                md = s_.getMetadata()
                a_[i_] = ObjArr([JString(e_), JString(str(s_.getItemId())), None if md is None else md.clone()])
            return a_

    @JImplements("java.util.function.Function")
    class WFetch(object):
        @JOverride
        def apply(self, o):
            eid = str(o[1])
            W.log.append(("fetch", eid))
            if eid not in W.pool:
                return "That item is not in Requip."
            c_ = W.inv.getStorage()
            fs = int(Sm.freeSlot(c_))
            if fs < 0:
                return "Inventory full"
            spc, s_ = W.pool.pop(eid)
            c_.setItemStackForSlot(JShort(fs), s_)
            W.out[eid] = True
            return "ok"

    @JImplements("java.util.function.Function")
    class WGone(object):
        @JOverride
        def apply(self, o):
            W.log.append(("gone", str(o[1]), str(o[2])))
            return JObject(True, Bool_)
    WARD = {"wardrobe:fn:canDeposit": WCan(), "wardrobe:fn:depositSlot": WSlot(), "wardrobe:fn:deposit": WDep(), "wardrobe:fn:list": WList(),
            "wardrobe:fn:fetch": WFetch(), "wardrobe:fn:gone": WGone()}

    def sacks_on(on=True):
        for k_, f_ in SACKS.items():
            if on:
                br.put(k_, f_)
            else:
                br.remove(k_)

    def ward_on(on=True):
        for k_, f_ in WARD.items():
            if on:
                br.put(k_, f_)
            else:
                br.remove(k_)

    def reset(inv_):
        S.inv, S.bag, S.allowed, S.receipts, S.log, S.pay_fail, S.take_short = inv_, {}, None, {}, [], None, 0
        S.surplus, S.haves = None, []
        W.inv, W.pool, W.out, W.full, W.slot_refuse, W.dep_refuse, W.log = inv_, {}, {}, None, None, None, []
        Sm.LAST.clear()
        del XP[:]
        logs()

    # ================================================================ R1: the recipe list
    rows = [(str(r_[0]), str(r_[1])) for r_ in Sm.recipes()]
    outs = dict((o_, r_) for r_, o_ in rows)
    # (a) an independent pass over the live store (the header 3 rule, written again here)
    RETIRED = {"alchemybench", "cookingbench", "campfire"}
    exp = {}
    for rc in list(CRR.getAssetMap().getAssetMap().values()):
        po = rc.getPrimaryOutput()
        if po is None or po.getItemId() is None or int(po.getQuantity()) != 1:
            continue
        oid = str(po.getItemId())
        if not bool(Roll.craftable(oid)) or int(Sm.cat(oid)) < 0 or bool(JClass(PKG + "GearUtFx").mythicId(oid)):
            continue
        ins = rc.getInput()
        if ins is None or len(ins) == 0 or any(q is not None and q.getItemId() is not None and bool(Data.isGear(q.getItemId())) for q in ins):
            continue
        brs = rc.getBenchRequirement()
        ok_ = False
        for b_ in (brs or []):
            if b_ is None or b_.id is None or str(b_.type) != "Crafting" or str(b_.id).lower() in RETIRED:
                continue
            bid = str(b_.id)
            acc = bid.lower() == "fieldcraft" or not have_acc or ITEM.getAssetMap().getAsset("Skyy_Accessory_%s_T1" % bid) is not None \
                or ITEM.getAssetMap().getAsset("Skyy_Accessory_%s" % bid) is not None
            ok_ = ok_ or acc
        if not ok_:
            continue
        rid = str(rc.getId())
        if oid not in exp or rid < exp[oid]:
            exp[oid] = rid
    K.check(outs == dict((o_, r_) for o_, r_ in exp.items()) and len(outs) > 100,
            "R1: recipes() = an independent pass over the live CraftingRecipe store (%d outputs; missing %s extra %s)"
            % (len(outs), sorted(set(exp) - set(outs))[:5], sorted(set(outs) - set(exp))[:5]))
    # (b) the Assets.zip + SkyyArmory JSON (pure Python) -> the gear outputs that have a Crafting bench a Skyy accessory exists for
    acc_benches = set()
    if have_acc:
        with zipfile.ZipFile(AC_JAR) as z_:
            for n in z_.namelist():
                m_ = re.match(r"Server/Item/Items/.*Skyy_Accessory_(\w+?)(_T\d+)?\.json$", n)
                if m_:
                    acc_benches.add(m_.group(1).lower())
    json_outs, json_bad = set(), []
    for src in (AZP, AR_SRC):
        with zipfile.ZipFile(src) as z_:
            for n in z_.namelist():
                if not (n.startswith("Server/Item/Items/") and n.endswith(".json")):
                    continue
                try:
                    d_ = json.loads(z_.read(n).decode("utf-8-sig"))
                except Exception:
                    continue
                r_ = d_.get("Recipe") if isinstance(d_, dict) else None
                if not isinstance(r_, dict):
                    continue
                oid = os.path.basename(n)[:-5]
                if oid not in outs and oid not in exp:
                    continue
                brs = [b_ for b_ in (r_.get("BenchRequirement") or []) if isinstance(b_, dict)]
                tb = [b_ for b_ in brs if b_.get("Type", "Crafting") == "Crafting" and str(b_.get("Id", "")).lower() not in RETIRED]
                if not tb:
                    json_bad.append(oid)
                    continue
                if have_acc and not any(str(b_.get("Id")).lower() == "fieldcraft" or str(b_.get("Id")).lower() in acc_benches for b_ in tb):
                    json_bad.append(oid)
                    continue
                json_outs.add(oid)
    K.check(not json_bad and json_outs <= set(outs),
            "R1: every listed output's JSON recipe (Assets.zip / SkyyArmory) has a Crafting bench with a Skyy accessory (none table-only / "
            "timed / Diagram): bad %s, JSON-listed but not shown %s" % (json_bad[:5], sorted(json_outs - set(outs))[:5]))
    soul_in = [o_ for o_ in outs if o_.startswith("Weapon_Wand_SoulCage_")]
    tables = []
    for o_, r_ in outs.items():
        for b_ in (recipe(r_).getBenchRequirement() or []):
            if str(b_.type) != "Crafting":
                pass
        if all(b_ is None or str(b_.type) != "Crafting" for b_ in (recipe(r_).getBenchRequirement() or [])):
            tables.append(o_)
    cats = {}
    for o_ in outs:
        cats.setdefault(int(Sm.cat(o_)), []).append(o_)
    K.check(not soul_in and not tables and set(cats) <= {0, 1, 2, 3, 4} and all(len(cats.get(c_, [])) > 0 for c_ in (1, 2, 3))
            and (4 in cats) == have_mt and "Armor_Iron_Chest" in outs and "Weapon_Sword_Iron" in outs and "Tool_Pickaxe_Iron" in outs,
            "R1: no Soul Cage tier-up (gear input = the Upgrade tab), no table-only recipe; categories %s (multitools %s)"
            % (dict((c_, len(v_)) for c_, v_ in sorted(cats.items())), have_mt))
    K.notes.append("recipes: %d outputs; per category %s; SkyyAccessories %s" % (len(outs), dict((c_, len(v_)) for c_, v_ in sorted(cats.items())), have_acc))
    n0 = len(rows)
    K.check(Sm.recipes() is Sm.recipes() or Sm.recipes().equals(Sm.recipes()), "R1: recipes() is cached (same list while the store and config stay)")
    apply(part__smithing="false")
    K.check(int(Sm.recipes().size()) == n0, "R1: a config change rebuilds the cache (same list)")
    apply()

    # ================================================================ G: categories, sets, families, names, figure
    K.check(int(Sm.slotIx("Armor_Iron_Head")) == 0 and int(Sm.slotIx("Armor_Iron_Legs")) == 3 and int(Sm.slotIx("Weapon_Sword_Iron")) == -1
            and str(Sm.setKey("Armor_Cloth_Cotton_Chest")) == "Armor_Cloth_Cotton" and str(Sm.setKey("Weapon_X")) == "Weapon_X"
            and str(Sm.famKey("Weapon_Sword_Iron")) == "Weapon_Sword" and str(Sm.famKey("Weapon_Fist_Wraps_Linen")) == "Weapon_Fist_Wraps"
            and str(Sm.famKey("Tool_Pickaxe_Iron")) == "Tool_Pickaxe_" and str(Sm.famKey(None)) == ""
            and (not have_mt or str(Sm.famKey(MULTI_PRE + "Iron")) == "Multitool"),
            "G: slotIx / setKey / famKey")
    K.check(int(Sm.cat("Armor_Iron_Chest")) == 1 and int(Sm.cat("Armor_Cloth_Cotton_Chest")) == 0 and int(Sm.cat("Weapon_Sword_Iron")) == 2
            and int(Sm.cat("Tool_Pickaxe_Iron")) == 3 and int(Sm.cat("Ingredient_Bar_Iron")) == -1 and int(Sm.cat(None)) == -1
            and (not have_mt or int(Sm.cat(MULTI_PRE + "Iron")) == 4),
            "G: cat: metal armor = Gathering (Mining Set), cloth = Combat, sword = Weapons, pickaxe = Tools, multitool = Multitools, a bar none")
    at_ = dict((i_, int(Sm.armorType(i_))) for i_ in ("Armor_Cloth_Cotton_Chest", "Armor_Leather_Light_Chest", "Armor_Iron_Chest", "Armor_Nope"))
    K.check(at_["Armor_Cloth_Cotton_Chest"] == 3 and at_["Armor_Iron_Chest"] == 1 and at_["Armor_Nope"] == 1 and at_.get("Armor_Leather_Light_Chest") in (2, 1),
            "G: armorType by the vanilla sound set: %s" % at_)
    K.notes.append("armor types: %s" % at_)
    gs = {}
    for c_ in range(5):
        gs[c_] = [(str(g_[0]), [str(x) for x in g_[1]], [str(x) for x in g_[2]], int(g_[3]), int(g_[4]), int(g_[5])) for g_ in Sm.groups(U1, JInt(c_), True)]
    iron = [g_ for g_ in gs[1] if g_[0] == "Armor_Iron"]
    swords = [g_ for g_ in gs[2] if g_[0] == "Weapon_Sword"]
    K.check(iron and iron[0][1] == ["Armor_Iron_Head", "Armor_Iron_Chest", "Armor_Iron_Hands", "Armor_Iron_Legs"]
            and all(outs[o_] == r_ for o_, r_ in zip(iron[0][1], iron[0][2])) and swords and len(swords[0][1]) >= 6
            and [int(Lvl.band(o_)[0]) for o_ in swords[0][1]] == sorted(int(Lvl.band(o_)[0]) for o_ in swords[0][1])
            and all(len(g_[1]) == len(set(g_[1])) for c_ in gs for g_ in gs[c_])
            and sorted(o_ for c_ in gs for g_ in gs[c_] for o_ in g_[1]) == sorted(outs),
            "G: groups: the Iron set = Head, Chest, Hands, Legs (its recipes), Swords sorted by level (%d tiers), every shown output in exactly "
            "one card" % (len(swords[0][1]) if swords else 0))
    los = [g_[3] for g_ in gs[0]]
    K.check(los == sorted(los), "G: cards sorted by their lowest level")
    K.check(str(Sm.groupName("Armor_Iron", JInt(1))) == "Iron Set" and str(Sm.groupName("Weapon_Sword", JInt(2))) == "Swords"
            and str(Sm.groupName("Tool_Pickaxe_", JInt(3))) == "Pickaxes" and str(Sm.groupName("Weapon_Fist_Wraps", JInt(2))) == "Fist Wraps"
            and str(Sm.groupName("Multitool", JInt(4))) == "Multitools" and str(Sm.benchName("Armor_Bench")) == "Armor Bench"
            and str(Sm.benchName("Farmingbench")) == "Farming Bench" and str(Sm.benchName("Workbench")) == "Workbench" and str(Sm.roman(JInt(2))) == "II",
            "G: groupName / benchName / roman")
    st_iron = str(Sm.setStats(JArray(JString)(iron[0][1]), U1))
    bo_iron = str(Sm.setBonus(JArray(JString)(iron[0][1])))
    K.check(st_iron.startswith("Health +") and "Resist +" in st_iron and bo_iron.startswith("Full set (4): ") and "Mining" in bo_iron
            and str(Sm.setBonus(JArray(JString)(["Armor_Cloth_Cotton_Chest"]))) == "" and str(Sm.typeWord(JArray(JString)(["Armor_Cloth_Cotton_Chest"]), JInt(0))) == "Cloth"
            and str(Sm.typeWord(JArray(JString)(["Armor_Iron_Chest"]), JInt(1))) == "Mining",
            "G: the Iron card: '%s' / '%s'; a combat set has no bonus" % (st_iron, bo_iron))
    K.notes.append("Iron card: %s | %s" % (st_iron, bo_iron))

    # ================================================================ CF: the class filter (SkyyClasses 0.1.19 live prefixes + armor types)
    CL, FREE = classes_py()
    K.check(len(CL) >= 7 and ("Warrior", "Swordsmanship") in [(c_[0], c_[1]) for c_ in CL], "CF: SkyyClasses 0.1.19 CLASSES read: %s" % [c_[0] for c_ in CL])
    br.put("class:list", ",".join("%s:%s" % (c_[0], c_[1]) for c_ in CL if c_[2]))
    for c_ in CL:
        br.put("class:weapons:" + c_[0], ",".join(c_[3]))
    br.put("class:weapons:free", ",".join(FREE))
    U2 = UUID.fromString("00000000-0000-0000-0000-0000000000b2")
    want_at = {"Warrior": 1, "Berserker": 1, "Archer": 2, "Assassin": 2, "Monk": 2, "Mage": 3, "Priest": 3}
    bad_cf = []
    wpn = [o_ for o_ in outs if int(Sm.cat(o_)) == 2]
    arm = [o_ for o_ in outs if int(Sm.cat(o_)) == 0]
    oth = [o_ for o_ in outs if int(Sm.cat(o_)) in (1, 3, 4)]
    for c_ in CL:
        if not c_[2]:
            continue
        br.put("class:" + str(U2), c_[0])
        for o_ in wpn:
            # the longest matching prefix over every class (+ free) decides; shown = it is this class's or free
            best, own = -1, False
            for c2 in CL:
                if not c2[2]:
                    continue
                for p_ in c2[3]:
                    if o_.startswith(p_) and len(p_) > best:
                        best, own = len(p_), (c2[0] == c_[0])
                    elif o_.startswith(p_) and len(p_) == best and c2[0] == c_[0]:
                        own = True
            for p_ in FREE:
                if o_.startswith(p_) and len(p_) >= best:
                    best, own = len(p_), True
            if bool(Sm.shows(U2, o_, False)) != own:
                bad_cf.append((c_[0], o_, own))
        for o_ in arm:
            w_ = want_at.get(c_[0], 0)
            if bool(Sm.shows(U2, o_, False)) != (w_ == 0 or int(Sm.armorType(o_)) == w_):
                bad_cf.append((c_[0], o_, "armor"))
        for o_ in oth:
            if not bool(Sm.shows(U2, o_, False)):
                bad_cf.append((c_[0], o_, "gathering"))
    K.check(not bad_cf, "CF: every enabled class sees exactly its weapons (the longest prefix wins: Bo staffs = Monk, not Mage) + free ones, its "
            "armor type, and every gathering armor / tool / multitool: %s" % bad_cf[:6])
    br.put("class:" + str(U2), "Monk")
    bo_ = [o_ for o_ in wpn if o_.startswith("Weapon_Staff_Bo_") or o_.startswith("Weapon_Bo_")]
    br.put("class:" + str(U2), "Mage")
    mage_bo = [o_ for o_ in bo_ if bool(Sm.shows(U2, o_, False))]
    br.put("class:" + str(U2), "Warrior")
    w_cards = len(Sm.groups(U2, JInt(2), False))
    a_cards = len(Sm.groups(U2, JInt(2), True))
    br.put("class:" + str(U2), "Nobody")
    none_all = all(bool(Sm.shows(U2, o_, False)) for o_ in wpn + arm)
    br.remove("class:" + str(U2))
    K.check(not mage_bo and 0 < w_cards < a_cards and none_all and bool(Sm.shows(U2, "Weapon_Sword_Iron", False)),
            "CF: a Mage never sees Bo staffs (%d Monk ones); Warrior weapon families %d < Show all %d; a class not in class:list / no class = "
            "everything" % (len(bo_), w_cards, a_cards))
    ck = [Sm.checkClassArmor("smith.classArmor", v_) for v_ in (str(Cfg.SMITH_ARM), "Warrior:Plate", "Warrior", "War rior:Heavy", "", None)]
    apply(smith__classArmor="Warrior:Cloth")
    br.put("class:" + str(U2), "Warrior")
    wc = [bool(Sm.shows(U2, o_, False)) for o_ in ("Armor_Cloth_Cotton_Chest",)]
    K.check(int(Sm.armorFor("Warrior")) == 3 and int(Sm.armorFor("Archer")) == 0 and wc == [True], "CF: smith.classArmor is live (Warrior:Cloth)")
    apply()
    K.check(ck[0] is None and "Heavy, Light or Cloth" in str(ck[1]) and "Class:Heavy" in str(ck[2]) and "not a class name" in str(ck[3])
            and ck[4] is None and ck[5] is None and int(Sm.armorFor(None)) == 0 and int(Sm.typeIx("cloth")) == 3 and int(Sm.typeIx("x")) == -1,
            "CF: checkClassArmor (Server Setup) refuses bad rows: %s" % [str(x) for x in ck[1:4]])
    # gear:fn:classShow (SkyySacks 0.7.17's /craft Smithing tab) = the same rule + the player's Show all switch
    SF = P("SmithFn")
    cs_fn = SF(JInt(1))
    br.put("class:" + str(U2), "Mage")
    r_cs = [cs_fn.apply(ObjArr([U2, JString(x)])) for x in ("Weapon_Sword_Iron", "Weapon_Staff_Iron", "Tool_Pickaxe_Iron")]
    Sm.setPref(U2, "gear.smithShowAll", True)
    r_all = cs_fn.apply(ObjArr([U2, JString("Weapon_Sword_Iron")]))
    Sm.setPref(U2, "gear.smithShowAll", False)
    K.check([bool(x) for x in r_cs] == [False, True, True] and bool(r_all) and cs_fn.apply(None) is None and cs_fn.apply(ObjArr([U2])) is None
            and bool(cs_fn.apply(ObjArr([None, JString("Weapon_Sword_Iron")]))),
            "CF: gear:fn:classShow = the filter (Mage: sword no, staff yes, pickaxe yes) + Show all; bad input -> null; no player -> shown")
    br.remove("class:" + str(U2))

    # ================================================================ X: the craft transaction
    sacks_on(True)
    ward_on(True)
    IRONC = "Armor_Iron_Chest"
    RC = outs[IRONC]
    mats = dict(inputs(RC))
    K.notes.append("Iron Chestplate recipe %s: %s" % (RC, mats))

    def give_mats(cs_, m_, sec="storage", start=20, mult=1):
        i_ = start
        for k_, v_ in m_.items():
            cs_[sec].setItemStackForSlot(JShort(i_), stack(k_, v_ * mult))
            i_ += 1

    def total(inv_, ids):
        c_ = cnt(inv_, ids)
        return dict((k_, c_[k_] + S.bag.get(k_, 0)) for k_ in ids)
    ids_ = list(mats) + [IRONC]
    # X1: into Requip (FIXER 2: wardrobe:fn:deposit + the evidence of what the payment took - never a slot + depositSlot)
    inv, cs = mkinv()
    reset(inv)
    give_mats(cs, mats)
    b1 = total(inv, ids_)
    bi1 = cnt(inv, list(mats))
    r1 = Sm.craft(inv, U1, "Tester", RC, True)
    l1 = logs()
    a1 = total(inv, ids_)
    pooled = [s_ for e_, (spc, s_) in W.pool.items() if str(s_.getItemId()) == IRONC]
    d1 = Data.effective(IRONC, pooled[0].getMetadata()) if pooled else None
    K.check(int(r1[0]) == 1 and str(r1[4]) == "Requip" and "-> Requip" in str(r1[1]) and a1[IRONC] == 0 and len(pooled) == 1
            and all(a1[k_] == b1[k_] - v_ for k_, v_ in mats.items()) and d1 is not None and bool(Data.identified(d1))
            and int(Lvl.level(IRONC, d1)) == int(Roll.craftLevel(IRONC, U1)) and [x for x in S.log if x[0] == "commit"]
            and any(" CRAFT-BEGIN " in l_ and RC in l_ for l_ in l1) and any(" CRAFT-DONE " in l_ and "-> Requip" in l_ for l_ in l1)
            and not [x for x in W.log if x[0] == "slot"] and [x for x in W.log if x[0] == "dep"] and len(XP) <= 1,
            "X1: Craft into Requip: room checked, CRAFT-BEGIN, paid once (%s), the item straight into Requip (wardrobe:fn:deposit, no "
            "depositSlot), commit, CRAFT-DONE; '%s'; XP calls %s" % (mats, str(r1[1]), XP))
    ev1 = json.loads([x for x in W.log if x[0] == "dep"][0][2])
    K.check(ev1.get("paid") is True and ev1.get("recipe") == RC and ev1.get("bags") == {}
            and ev1.get("inv") == dict((k_, bi1[k_]) for k_ in mats if bi1[k_] > 0),
            "X1: the deposit evidence = every id the payment lowered with its count BEFORE (inventory paid -> the inventory part only): %s" % ev1)
    # the order: CRAFT-BEGIN is on disk before the pay; canDeposit before the pay
    order = [x[0] for x in S.log]
    K.check(order.index("pay") < order.index("commit") and W.log[0][0] == "can", "X1: order: canDeposit -> pay -> deliver -> commit (%s / %s)" % (order, [x[0] for x in W.log]))
    # X1b: XP is the bench path's: payCraft once per item with the rolled rarity (rolling tools: the 0.2.17 anti-loop table)
    xp_exp = int(Roll.craftXp(IRONC, Data.rarity(d1)))
    K.check((xp_exp == 0 and not XP) or (len(XP) == 1 and XP[0][0] == "Smithing" and XP[0][1] == xp_exp and XP[0][2] == "gear:craft"),
            "X1: Smithing XP = GearRoll.craftXp of the rolled rarity, paid once through skill:fn:addxp (%s, want %d)" % (XP, xp_exp))
    # X2: inventory delivery (switch off), Requip absent, Requip refusing the slot
    for name_, setup_ in (("switch off", lambda: None), ("Requip absent", lambda: ward_on(False)), ("Requip refuses", None)):
        inv, cs = mkinv()
        reset(inv)
        give_mats(cs, mats)
        to_rq = name_ != "switch off"
        if name_ == "Requip absent":
            ward_on(False)
        if name_ == "Requip refuses":
            W.dep_refuse = "Armor space full (1000)"
        r2 = Sm.craft(inv, U1, "Tester", RC, to_rq)
        ward_on(True)
        c2 = cnt(inv, [IRONC])
        logs()
        K.check(int(r2[0]) == 1 and str(r2[4]) == "inventory" and c2[IRONC] == 1 and not W.pool
                and ((name_ != "Requip refuses") or "Armor space full" in str(r2[1])),
                "X2: %s -> the item stays in the inventory: '%s'" % (name_, str(r2[1])))
    # X3: no free slot -> Requip straight in (wardrobe:fn:deposit with the evidence); evidence = the Requip shape
    inv, cs = mkinv()
    reset(inv)
    for sec_, n_ in (("storage", 36), ("backpack", 9)):
        fill(cs, sec_, n_)
    for j_, (k_, v_) in enumerate(mats.items()):
        cs["storage"].setItemStackForSlot(JShort(j_), stack(k_, v_))
    b3 = total(inv, ids_)
    r3 = Sm.craft(inv, U1, "Tester", RC, True)
    dep = [x for x in W.log if x[0] == "dep"]
    ev = json.loads(dep[0][2]) if dep else {}
    logs()
    K.check(int(r3[0]) == 1 and str(r3[4]) == "Requip" and len(W.pool) == 1 and dep and dep[0][1] == "smithing" and ev.get("recipe") == RC
            and set(ev.get("inv", {})) == set(k_ for k_ in mats if not k_.startswith("res:")) and all(ev["inv"][k_] == b3[k_] for k_ in ev["inv"])
            and "bags" in ev, "X3: a FULL inventory + Requip: deposited straight in (wardrobe:fn:deposit) with the evidence %s" % ev)
    # X4: no free slot + Requip absent / refusing canDeposit -> No room, NOTHING paid
    for name_ in ("absent", "full"):
        inv, cs = mkinv()
        reset(inv)
        for sec_, n_ in (("storage", 36), ("backpack", 9)):
            fill(cs, sec_, n_)
        if name_ == "absent":
            ward_on(False)
        else:
            W.full = "Armor space full (1000)"
        r4 = Sm.craft(inv, U1, "Tester", RC, True)
        ward_on(True)
        K.check(int(r4[0]) == 0 and "No room" in str(r4[1]) and not [x for x in S.log if x[0] == "pay"] and not logs(),
                "X4: no room (Requip %s): refused BEFORE any payment, nothing logged: '%s'" % (name_, str(r4[1])))
    # X5: materials short -> refused by the pay, nothing moved
    inv, cs = mkinv()
    reset(inv)
    b5 = total(inv, ids_)
    r5 = Sm.craft(inv, U1, "Tester", RC, True)
    l5 = logs()
    K.check(int(r5[0]) == 0 and "materials" in str(r5[1]) and total(inv, ids_) == b5 and not W.pool and any("CRAFT-REFUSED" in l_ for l_ in l5)
            and not [x for x in S.log if x[0] == "commit"], "X5: materials short -> '%s', nothing moved, CRAFT-REFUSED" % str(r5[1]))
    S.pay_fail = "a stack with extra data (rolled gear or a named item) would be used - nothing was taken"
    give_mats(cs, mats)
    r5b = Sm.craft(inv, U1, "Tester", RC, True)
    S.pay_fail = None
    logs()
    K.check(int(r5b[0]) == 0 and "Not crafted: a stack with extra data" in str(r5b[1]), "X5: a pay refusal reason is shown: '%s'" % str(r5b[1]))
    # X6: materials half from the bags (inventory first), and the deliver FAILS -> refund (inventory + bags back). FIXER 2: Requip takes
    # the item straight in now, so the slot path runs with the switch off (a) and with Requip refusing the deposit (b)
    for v6, to6 in (("a", False), ("b", True)):
        inv, cs = mkinv(fail=("storage",))
        reset(inv)
        k0 = list(mats)[0]
        cs["storage"].setItemStackForSlot(JShort(30), stack(k0, 1))
        S.bag = dict((k_, v_) for k_, v_ in mats.items())
        S.bag[k0] = mats[k0] - 1
        cs["storage"].refuseId = IRONC
        if to6:
            W.dep_refuse = "Requip shut"
        b6 = total(inv, ids_)
        r6 = Sm.craft(inv, U1, "Tester", RC, to6)
        l6 = logs()
        rf6 = [x for x in S.log if x[0] == "refund"]
        K.check(int(r6[0]) == -1 and "materials were given back" in str(r6[1]) and total(inv, ids_) == b6 and rf6 and not W.pool
                and any("CRAFT-FAILED" in l_ and (not to6 or "Requip shut" in l_) for l_ in l6) and not [x for x in S.log if x[0] == "commit"]
                and not XP and (not to6 or [x for x in W.log if x[0] == "dep"]),
                "X6%s: %sthe slot refuses the item -> refund (inventory 1 + bags back), CRAFT-FAILED, no XP: '%s'"
                % (v6, "Requip refuses the deposit, then " if to6 else "", str(r6[1])))
    # X7: full inventory + Requip's deposit refuses -> refund
    inv, cs = mkinv()
    reset(inv)
    for sec_, n_ in (("storage", 36), ("backpack", 9)):
        fill(cs, sec_, n_)
    S.bag = dict(mats)
    W.dep_refuse = "Requip shut"
    b7 = total(inv, ids_)
    r7 = Sm.craft(inv, U1, "Tester", RC, True)
    l7 = logs()
    K.check(int(r7[0]) == -1 and total(inv, ids_) == b7 and any("CRAFT-FAILED" in l_ and "Requip shut" in l_ for l_ in l7),
            "X7: inventory full + Requip refuses the deposit -> materials refunded, CRAFT-FAILED, nothing given")
    # FX1 (review fix): SkyySacks' craftPay puts SURPLUS materials back into the very slot the craft reserved -> never written over
    k_sp = [k_ for k_ in mats if not k_.startswith("res:")][0]
    # (a) another free slot exists -> the item goes there, the surplus stays, CRAFT-SLOT logged
    inv, cs = mkinv()
    reset(inv)
    give_mats(cs, mats, mult=3)
    fs_a = int(Sm.freeSlot(cs["storage"]))
    S.surplus = k_sp
    ba = total(inv, ids_ + [k_sp])
    ra = Sm.craft(inv, U1, "Tester", RC, False)
    la = logs()
    aa = total(inv, ids_ + [k_sp])
    xa = at(cs, "storage", fs_a)
    K.check(int(ra[0]) == 1 and ("surplus", fs_a) in S.log and xa is not None and str(xa.getItemId()) == k_sp and aa[IRONC] == 1
            and all(aa[k_] == ba[k_] - v_ for k_, v_ in mats.items()) and any(" CRAFT-SLOT " in l_ for l_ in la),
            "FX1a: the payment's surplus filled the reserved slot %d -> the item went to another slot, the surplus %s kept, totals exact" % (fs_a, k_sp))
    # (b)/(c) the reserved slot was the LAST free one: Requip on -> deposited straight in; Requip off -> refund, nothing lost
    for name_, to_ in (("Requip", True), ("inventory", False)):
        inv, cs = mkinv()
        reset(inv)
        fill(cs, "storage", 36)
        fill(cs, "backpack", 9)
        cs["storage"].removeItemStackFromSlot(JShort(35))
        for j_, (k_, v_) in enumerate(mats.items()):
            cs["storage"].setItemStackForSlot(JShort(j_), stack(k_, v_ * 3))
        S.surplus = k_sp
        bb = total(inv, ids_ + [k_sp])
        rb = Sm.craft(inv, U1, "Tester", RC, to_)
        lb = logs()
        ab = total(inv, ids_ + [k_sp])
        x35 = at(cs, "storage", 35)
        kept = x35 is not None and str(x35.getItemId()) == k_sp
        if to_:
            ok_ = int(rb[0]) == 1 and str(rb[4]) == "Requip" and len(W.pool) == 1 and kept and [x for x in W.log if x[0] == "dep"] \
                and all(ab[k_] == bb[k_] - v_ for k_, v_ in mats.items()) and not any(" CRAFT-SLOT " in l_ for l_ in lb)
        else:
            ok_ = int(rb[0]) == -1 and "given back" in str(rb[1]) and ab == bb and not W.pool and kept and any("CRAFT-FAILED" in l_ for l_ in lb) \
                and not [x for x in S.log if x[0] == "commit"]
        K.check(ok_, "FX1%s: the last free slot taken by the surplus, crafted to %s -> %s ('%s')"
                % ("b" if to_ else "c", name_, "Requip deposit, surplus kept" if to_ else "refund, nothing lost, surplus kept", str(rb[1])))
    S.surplus = None

    # FX5 (FIXER 2, critic 2 finding 1): SkyyWardrobe 0.2's crash repair (WdTx.matsBack, written again here: every listed inventory id
    # counted over Hotbar + Storage + Backpack + Armor >= its count, every listed bag id sacks:fn:count >= its count, at least one listed)
    def mats_back(ev_, inv_):
        d_ = json.loads(ev_)
        n_ = 0
        for k_, v_ in d_.get("inv", {}).items():
            n_ += 1
            have_ = sum(int(x.getQuantity()) for c_ in (Stamp.section(inv_, JInt(s_)) for s_ in (0, 1, 2, 3)) if c_ is not None
                        for x in (c_.getItemStack(JShort(i_)) for i_ in range(int(c_.getCapacity()))) if x is not None and not x.isEmpty()
                        and str(x.getItemId()) == k_)
            if have_ < v_:
                return False
        for k_, v_ in d_.get("bags", {}).items():
            n_ += 1
            if S.bag.get(k_, 0) < v_:
                return False
        return n_ > 0
    # (a) inventory-paid craft into Requip: no rollback -> Requip keeps the item; the engine rolls the inventory back (the materials
    #     return) -> Requip's repair UNDOES the craft. Never the item AND the materials.
    inv, cs = mkinv()
    reset(inv)
    give_mats(cs, mats)
    ra5 = Sm.craft(inv, U1, "Tester", RC, True)
    logs()
    ev5 = [x for x in W.log if x[0] == "dep"]
    kept5 = bool(ev5) and not mats_back(ev5[0][2], inv)
    give_mats(cs, mats)                       # the engine's save from before the craft: the materials are back
    undo5 = bool(ev5) and mats_back(ev5[0][2], inv)
    K.check(int(ra5[0]) == 1 and str(ra5[4]) == "Requip" and kept5 and undo5 and not [x for x in W.log if x[0] == "slot"],
            "FX5a: crash model - Requip keeps the craft while the materials stay spent; an inventory rollback (materials back) makes "
            "matsBack true -> the craft is undone (never item + materials)")
    # (b) bag-paid craft (the inventory paid nothing): the evidence = the bag counts before
    inv, cs = mkinv()
    reset(inv)
    S.bag = dict((k_, v_ + 2) for k_, v_ in mats.items())
    bag0 = dict(S.bag)
    rb5 = Sm.craft(inv, U1, "Tester", RC, True)
    logs()
    eb5 = [x for x in W.log if x[0] == "dep"]
    evb = json.loads(eb5[0][2]) if eb5 else {}
    keptb = bool(eb5) and not mats_back(eb5[0][2], inv)
    S.bag = dict(bag0)
    undob = bool(eb5) and mats_back(eb5[0][2], inv)
    K.check(int(rb5[0]) == 1 and str(rb5[4]) == "Requip" and evb.get("inv") == {} and evb.get("bags") == dict((k_, bag0[k_]) for k_ in mats)
            and keptb and undob, "FX5b: a craft paid from the bags only: evidence = the bag counts before %s; kept / undone like (a)" % evb.get("bags"))
    # (c) paidEvidence direct: a resource-type input is covered (ids found by DIFF, not by the recipe's item ids); nothing changed = null
    inv, cs = mkinv()
    reset(inv)
    k0 = list(mats)[0]
    cs["storage"].setItemStackForSlot(JShort(3), stack(k0, 5))
    cs["backpack"].setItemStackForSlot(JShort(0), stack(k0, 2))
    ib_ = Sm.invCounts(inv)
    bb_ = Sm.bagAll(U1)
    same_ = Sm.paidEvidence(RC, U1, inv, ib_, bb_)
    cs["storage"].setItemStackForSlot(JShort(3), stack(k0, 2))
    pe_ = json.loads(str(Sm.paidEvidence(RC, U1, inv, ib_, bb_)))
    K.check(same_ is None and pe_["inv"] == {k0: 7} and pe_["bags"] == {} and Sm.paidEvidence(RC, U1, inv, None, bb_) is None,
            "FX5c: paidEvidence = the ids the payment lowered (before count %s over every section Requip counts); nothing lowered / no "
            "snapshot = null" % pe_["inv"])
    # (d) nothing provable (no sacks:fn:all, bag-paid) -> no Requip for this craft: the inventory, CRAFT-NOPROOF, said so
    inv, cs = mkinv()
    reset(inv)
    S.bag = dict(mats)
    br.remove("sacks:fn:all")
    rd5 = Sm.craft(inv, U1, "Tester", RC, True)
    br.put("sacks:fn:all", SACKS["sacks:fn:all"])
    ld5 = logs()
    K.check(int(rd5[0]) == 1 and str(rd5[4]) == "inventory" and cnt(inv, [IRONC])[IRONC] == 1 and not W.pool
            and not [x for x in W.log if x[0] in ("dep", "slot")] and "could not be proven" in str(rd5[1]) and any("CRAFT-NOPROOF" in l_ for l_ in ld5),
            "FX5d: nothing provable -> the item stays in the inventory (no Requip deposit): '%s'" % str(rd5[1]))
    # (e) full inventory + Requip refuses the deposit, but the payment emptied a slot -> the item lands there (no needless refund)
    inv, cs = mkinv()
    reset(inv)
    for sec_, n_ in (("storage", 36), ("backpack", 9)):
        fill(cs, sec_, n_)
    for j_, (k_, v_) in enumerate(mats.items()):
        cs["storage"].setItemStackForSlot(JShort(j_), stack(k_, v_))
    W.dep_refuse = "Armor space full (1000)"
    be5 = total(inv, ids_)
    re5 = Sm.craft(inv, U1, "Tester", RC, True)
    logs()
    ae5 = total(inv, ids_)
    K.check(int(re5[0]) == 1 and str(re5[4]) == "inventory" and ae5[IRONC] == 1 and all(ae5[k_] == be5[k_] - v_ for k_, v_ in mats.items())
            and "Armor space full" in str(re5[1]) and not W.pool,
            "FX5e: Requip refuses, the payment freed a slot -> delivered there: '%s'" % str(re5[1]))
    # FX6 (critic 2 finding 2): RE-IDENTIFY keeps the SkyyRequip stamp + other mods' keys (GearData.carry)
    Pool, Unid, Ident = P("GearPool"), P("GearUnid"), P("GearIdent")
    ti6 = dict((str(k_), i_) for i_, k_ in enumerate(Pool.T_KEY))

    @JImplements("java.util.function.Function")
    class CoinsOk(object):
        @JOverride
        def apply(self, o):
            return JObject(True, Bool_)
    br.put("coins:fn:take", CoinsOk())
    br.put("coins:fn:add", CoinsOk())
    try:
        first6 = Unid.open(Unid.doc(Unid.make(JInt(ti6["Weapon_Shortbow"]), JInt(0), JInt(3), JInt(30), JInt(34), "t", "t", JInt(0))), U1)[3]
        st6 = stamp(first6, "0000r3r0")
        md6 = st6.getMetadata().clone()
        md6.put("OtherMod", BD("x", BI32(JInt(7))))
        st6 = st6.withMetadata(md6)
        rc6 = SIC(JShort(4))
        rc6.setItemStackForSlot(JShort(2), st6)
        rr6 = Ident.reroll(rc6, JInt(2), st6.getItemId(), Forge.fp(st6), U1, "Tester")
        nw6 = rc6.getItemStack(JShort(2))
        nd6 = Data.effective(nw6.getItemId(), nw6.getMetadata())
        K.check(int(rr6[0]) == 1 and str(Data.eidOf(nw6)) == "0000r3r0" and nw6.getMetadata().containsKey("OtherMod")
                and int(Unid.rerolls(Unid.boxOf(nd6))) == 1 and str(Data.eidOf(rr6[2])) == "0000r3r0",
                "FX6: re-identify keeps the SkyyRequip stamp (0000r3r0) and another mod's key; the gear document is the new roll")
    finally:
        br.remove("coins:fn:take")
        br.remove("coins:fn:add")
        logs()
    # FX7 (critic 3): Refresh drops the shared recipe cache at most once per 5 s for the whole server
    Sm.recipes()
    Sm.REC_FORCED = 0
    t7 = 10 ** 7
    f1 = bool(Sm.forceRecipes(Long_(t7)))
    n1_ = Sm.REC is None
    Sm.recipes()
    f2 = bool(Sm.forceRecipes(Long_(t7 + 1000)))
    n2_ = Sm.REC is None
    f3 = bool(Sm.forceRecipes(Long_(t7 + 6000)))
    Sm.recipes()
    K.check(f1 and n1_ and not f2 and not n2_ and f3 and Sm.REC is not None,
            "FX7: Refresh forces a recipe re-read once, a second Refresh within 5 s (any player) keeps the cache, after 5 s again")
    # X8: a CRASH between the pay and the delivery -> the materials are gone (CRAFT-BEGIN on disk lists them), never an item
    inv, cs = mkinv()
    reset(inv)
    give_mats(cs, mats)
    b8 = total(inv, ids_)
    Sm.CRASH_AT = 1
    crashed = False
    try:
        Sm.craft(inv, U1, "Tester", RC, True)
    except Exception as ex:
        crashed = "right after the materials were paid" in str(ex)
    finally:
        Sm.CRASH_AT = 0
    l8 = disk()
    a8 = total(inv, ids_)
    K.check(crashed and a8[IRONC] == 0 and not W.pool and all(a8[k_] == b8[k_] - v_ for k_, v_ in mats.items())
            and any(" CRAFT-BEGIN " in l_ and '"inv":{' in l_ for l_ in l8),
            "X8: a crash after the pay: materials lost (listed in CRAFT-BEGIN, on disk), NO item anywhere (no dupe)")
    Log.take()
    # X9: gates - not allowed (lockWhy), SkyySacks absent, part.smithing off, level gate, unknown recipe; nothing paid
    inv, cs = mkinv()
    reset(inv)
    give_mats(cs, mats)
    S.allowed = set()
    r9a = Sm.craft(inv, U1, "Tester", RC, True)
    S.allowed = None
    sacks_on(False)
    r9b = Sm.craft(inv, U1, "Tester", RC, True)
    sacks_on(True)
    apply(part__smithing="false")
    r9c = Sm.craft(inv, U1, "Tester", RC, True)
    apply()
    r9d = Sm.craft(inv, U1, "Tester", "Nope_Recipe", True)
    r9e = Sm.craft(None, U1, "Tester", RC, True)
    # the level gate: craft.belowBand=block + a skill below the band (the gate cache seeded like a SkyySkills answer)
    hi_w = sorted((int(Lvl.band(o_)[0]), o_) for o_ in outs if int(Sm.cat(o_)) == 2 and bool(JClass(PKG + "GearDefs").enforcedKind(Data.kindFor(o_))))[-1][1]
    apply(craft__belowBand="block", craft__levelFrom="gate")
    sk = Roll.craftSkill(hi_w, U1)
    if sk is not None:
        Gate.entry(U1)[2].put(sk, Int_(1))
    bw = Roll.blockWhy(hi_w, U1)
    r9f = Sm.craft(inv, U1, "Tester", outs[hi_w], True) if bw is not None else None
    apply()
    K.check(int(r9a[0]) == 0 and "accessory" in str(r9a[1]) and int(r9b[0]) == 0 and "SkyySacks 0.7.17" in str(r9b[1]) and int(r9c[0]) == 0
            and "switched off" in str(r9c[1]) and int(r9d[0]) == 0 and "Refresh" in str(r9d[1]) and int(r9e[0]) == 0
            and not [x for x in S.log if x[0] == "pay"] and not logs(),
            "X9: refused with nothing paid: not allowed '%s' / no SkyySacks / part.smithing off / unknown recipe / no inventory" % str(r9a[1]))
    K.check(bw is not None and r9f is not None and int(r9f[0]) == 0 and str(r9f[1]) == str(bw) and not [x for x in S.log if x[0] == "pay"],
            "X9: the bench's level gate (craft.belowBand=block): %s refused '%s'" % (hi_w, str(bw)[:80]))
    Gate.entry(U1)[2].clear()
    # X10: the rarity roll = the bench roll; part.craft off = plain (no XP); 40 crafts
    seen = {}
    lv_ok = True
    for _i in range(40):
        inv, cs = mkinv()
        reset(inv)
        give_mats(cs, mats)
        rr = Sm.craft(inv, U1, "Tester", RC, False)
        d_ = rr[3]
        k_ = rid_of(d_) if d_ is not None else "none"
        seen[k_] = seen.get(k_, 0) + 1
        lv_ok = lv_ok and d_ is not None and int(Lvl.level(IRONC, d_)) == int(Roll.craftLevel(IRONC, U1))
    logs()
    exp_r = rid_of(Roll.craftDoc(IRONC, U1))
    K.check(lv_ok and set(seen) == {exp_r},
            "X10: 40 crafts roll like the bench (GearRoll.craftDoc: Mining pieces are Set, gear rolls the craft odds), made at the craft "
            "level: %s" % seen)
    WS = "Weapon_Sword_Iron"
    mw = dict(inputs(outs[WS]))
    seen_w = {}
    for _i in range(60):
        inv, cs = mkinv()
        reset(inv)
        give_mats(cs, mw)
        rr = Sm.craft(inv, U1, "Tester", outs[WS], False)
        k_ = rid_of(rr[3])
        seen_w[k_] = seen_w.get(k_, 0) + 1
    logs()
    K.check(len(seen_w) >= 2 and "set" not in seen_w and "untiered" not in seen_w and "mythic" not in seen_w,
            "X10: an Iron sword rolls a rarity per craft (60 crafts): %s" % seen_w)
    K.notes.append("sword rarity spread (60): %s" % seen_w)
    apply(part__craft="false")
    inv, cs = mkinv()
    reset(inv)
    give_mats(cs, mw)
    rp = Sm.craft(inv, U1, "Tester", outs[WS], False)
    apply()
    sp_ = at(cs, "storage", 0)
    logs()
    K.check(int(rp[0]) == 1 and rp[3] is None and sp_ is not None and str(sp_.getItemId()) == WS and not bool(Data.hasAnyDoc(sp_.getMetadata())) and not XP,
            "X10: part.craft off -> a PLAIN item (as a bench gives), no XP")
    # X11: multitool (0 XP: its tools already paid) when Multitools is loaded
    if have_mt and (MULTI_PRE + "Iron") in outs:
        mm = dict(inputs(outs[MULTI_PRE + "Iron"]))
        inv, cs = mkinv()
        reset(inv)
        give_mats(cs, mm)
        rm = Sm.craft(inv, U1, "Tester", outs[MULTI_PRE + "Iron"], False)
        logs()
        xm = int(Roll.craftXp(MULTI_PRE + "Iron", Data.rarity(rm[3]))) if rm[3] is not None else -1
        K.check(int(rm[0]) == 1 and rm[3] is not None and ((xm == 0 and not XP) or (len(XP) == 1 and XP[0][1] == xm)),
                "X11: a multitool crafts (inputs %s); its XP = GearRoll.craftXp (%d: 0 once the 0.2.18 recipe swap ran at start): %s" % (mm, xm, XP))
    # X12: Craft every missing piece: Head already in the inventory, Hands in Requip -> Chest + Legs crafted; stops at the first refusal
    io_ = iron[0][1]
    ir_ = iron[0][2]
    inv, cs = mkinv()
    reset(inv)
    cs["hotbar"].setItemStackForSlot(JShort(0), stack(io_[0]))
    W.pool["0000aaaa"] = ("armor", stamp(stack(io_[2]), "0000aaaa"))
    for j_, o_ in enumerate(io_):
        give_mats(cs, dict(inputs(ir_[j_])), start=10 + 4 * j_)
    dbg = [(o_, int(Sm.have(U1, inv, ir_[j_], recipe(ir_[j_]))[0]), Roll.blockWhy(o_, U1)) for j_, o_ in enumerate(io_)]
    K.notes.append("X12 before: %s owned %s" % (dbg, sorted(str(x) for x in Sm.owned(U1, inv))))
    ra = Sm.craftAll(inv, U1, "Tester", JArray(JString)(ir_), JArray(JString)(io_), False)
    c12 = cnt(inv, io_)
    logs()
    K.check(int(ra[0]) == 2 and c12[io_[1]] == 1 and c12[io_[3]] == 1 and c12[io_[0]] == 1 and c12[io_[2]] == 0 and "Made 2" in str(ra[1]),
            "X12: Craft every missing piece: owned Head (inventory) + Hands (Requip) skipped, Chest + Legs made: '%s'" % str(ra[1]))
    ra2 = Sm.craftAll(inv, U1, "Tester", JArray(JString)(ir_), JArray(JString)(io_), False)
    inv, cs = mkinv()
    reset(inv)
    ra3 = Sm.craftAll(inv, U1, "Tester", JArray(JString)(ir_), JArray(JString)(io_), False)
    for j_, o_ in enumerate(io_):
        give_mats(cs, dict(inputs(ir_[j_])), start=10 + 4 * j_, mult=2)          # no material stack runs empty (it would free a slot)
    cs["storage"].setItemStackForSlot(JShort(0), stack("Ingredient_Stick"))
    fill(cs, "backpack", 9)
    for i_ in range(36):
        if at(cs, "storage", i_) is None:
            cs["storage"].setItemStackForSlot(JShort(i_), stack("Ingredient_Stick"))
            break
    # exactly one free slot left anywhere -> the first piece is made, the second stops at "No room"
    free_ = [i_ for i_ in range(36) if at(cs, "storage", i_) is None]
    for i_ in free_[1:]:
        cs["storage"].setItemStackForSlot(JShort(i_), stack("Ingredient_Stick"))
    ward_on(False)
    ra4 = Sm.craftAll(inv, U1, "Tester", JArray(JString)(ir_), JArray(JString)(io_), False)
    ward_on(True)
    sacks_on(False)
    ra5 = Sm.craftAll(inv, U1, "Tester", JArray(JString)(ir_), JArray(JString)(io_), False)
    sacks_on(True)
    logs()
    K.check(int(ra2[0]) == 0 and "already have every piece" in str(ra2[1]) and int(ra3[0]) == 0 and "lack their materials" in str(ra3[1])
            and int(ra4[0]) == 1 and "then stopped: No room" in str(ra4[1]) and int(ra5[0]) == 0 and "SkyySacks" in str(ra5[1]),
            "X12: nothing missing / nothing affordable / stops at the first refusal ('%s') / no SkyySacks" % str(ra4[1]))
    # X13: the 1 s gap per player, owned / due / statusText / lockWhy / allowed / have (bridge + local)
    Sm.LAST.put(U1, Long_(JClass("java.lang.System").currentTimeMillis()))
    due_now = bool(Sm.due(U1, JLong(JClass("java.lang.System").currentTimeMillis())))
    Sm.LAST.clear()
    inv, cs = mkinv()
    reset(inv)
    give_mats(cs, mats)
    S.bag = {list(mats)[0]: 7}
    hv_b = Sm.have(U1, inv, RC, recipe(RC))
    sacks_on(False)
    hv_l = Sm.have(U1, inv, RC, recipe(RC))
    al_none = Sm.allowed(U1)
    st_off = str(Sm.liveText())
    sacks_on(True)
    st_on = str(Sm.liveText()) + " | " + str(Sm.statusText())
    lk = str(Sm.lockWhy(recipe(RC), False))
    lks = str(Sm.lockWhy(recipe(RC), True))
    K.check(not due_now and int(hv_b[0]) >= 1 and int(hv_b[2][0]) == mats[list(mats)[0]] + 7 and int(hv_l[2][0]) == mats[list(mats)[0]]
            and al_none is None and "waits for SkyySacks" in st_off and "via SkyySacks" in st_on and "Requip on" in st_on and "/smithing Craft tab" in st_on
            and "Armor Bench" in lk and "accessory" in lk and lks.startswith("Locked - needs"),
            "X13: 1 s gap; have = bridge (inventory + bags) / local (inventory); allowed null without SkyySacks; statusText '%s'; lockWhy '%s'" % (st_on, lk))
    K.notes.append("lockWhy: %s | %s" % (lk, lks))

    # ================================================================ F1: Upgrade + Merge keep foreign keys; the hatchet is reported gone
    steps = []
    for i_ in range(1, len(SOUL)):
        c_ = Up.cost(SOUL[i_ - 1], SOUL[i_])
        steps.append((SOUL[i_ - 1], SOUL[i_], dict((str(a), int(b)) for a, b in zip(c_[0], c_[1]))))
    fr_, to_, um = steps[1]
    inv, cs = mkinv()
    reset(inv)
    src_ = stamp(gear(fr_, rolled(fr_, 2)), "0000beef")
    md_ = src_.getMetadata().clone()
    md_.put("OtherMod", BD("x", BI32(JInt(7))))
    src_ = src_.withMetadata(md_)
    cs["hotbar"].setItemStackForSlot(JShort(0), src_)
    for j_, (k_, v_) in enumerate(um.items()):
        cs["storage"].setItemStackForSlot(JShort(j_), stack(k_, v_))
    ru = Up.upgrade(inv, JInt(0), JInt(0), fr_, str(Forge.fp(at(cs, "hotbar", 0))), U1, "Tester")
    nw = at(cs, "hotbar", 0)
    md_n = nw.getMetadata() if nw is not None else None
    logs()
    K.check(int(ru[0]) == 1 and str(nw.getItemId()) == to_ and str(Data.eidOf(nw)) == "0000beef" and md_n.containsKey("OtherMod")
            and md_n.getDocument("OtherMod").getInt32("x").getValue() == 7 and Data.effective(to_, md_n) is not None
            and str(Data.str(Data.effective(to_, md_n), "kind", "")) == str(Data.kindFor(to_)),
            "F1: /upgrade keeps the SkyyRequip stamp (eid 0000beef) and another mod's key; the SkyyGear document is the new tier's")
    # carry(): our keys never copied, the fresh stack's own keys win, nothing to copy = the same stack
    fresh_ = Data.put(stack(to_), rolled(to_, 1), None)
    cc_ = Data.carry(fresh_, src_)
    K.check(Data.eidOf(cc_) is not None and str(Data.effective(to_, cc_.getMetadata()).toJson()) == str(Data.effective(to_, fresh_.getMetadata()).toJson())
            and Data.carry(fresh_, stack(fr_)).equals(fresh_) and Data.carry(None, src_) is None and Data.carry(fresh_, None).equals(fresh_)
            and str(Data.stampKey()) == "SkyyRequip" and Data.eidOf(stack(fr_)) is None and Data.eidOf(None) is None,
            "F1: carry: the fresh document wins (ours never copied), a plain source = the same stack; stampKey / eidOf")
    if have_mt:
        inv, cs = mkinv()
        reset(inv)
        pk = stamp(gear("Tool_Pickaxe_Iron", rolled("Tool_Pickaxe_Iron", 1)), "0000p1c0")
        ht = stamp(gear("Tool_Hatchet_Iron", rolled("Tool_Hatchet_Iron", 2)), "0000ha7c")
        cs["hotbar"].setItemStackForSlot(JShort(1), pk)
        cs["storage"].setItemStackForSlot(JShort(4), ht)
        rm_ = Merge.merge(inv, JInt(0), JInt(1), "Tool_Pickaxe_Iron", str(Forge.fp(pk)), JInt(1), JInt(4), "Tool_Hatchet_Iron", str(Forge.fp(ht)), U1, "Tester")
        mt_ = at(cs, "hotbar", 1)
        lm = logs()
        K.check(int(rm_[0]) == 1 and str(mt_.getItemId()) == MULTI_PRE + "Iron" and str(Data.eidOf(mt_)) == "0000p1c0" and at(cs, "storage", 4) is None
                and ("gone", "0000ha7c", "merged") in W.log and any("MERGE-REQUIP-GONE" in l_ for l_ in lm),
                "F1: the merge keeps the PICKAXE's Requip entry on the multitool; the hatchet's (0000ha7c) is reported used up (wardrobe:fn:gone)")
        inv, cs = mkinv()
        reset(inv)
        pk2 = gear("Tool_Pickaxe_Iron", rolled("Tool_Pickaxe_Iron", 1))
        ht2 = gear("Tool_Hatchet_Iron", rolled("Tool_Hatchet_Iron", 1))
        cs["hotbar"].setItemStackForSlot(JShort(1), pk2)
        cs["hotbar"].setItemStackForSlot(JShort(2), ht2)
        Merge.merge(inv, JInt(0), JInt(1), "Tool_Pickaxe_Iron", str(Forge.fp(pk2)), JInt(0), JInt(2), "Tool_Hatchet_Iron", str(Forge.fp(ht2)), U1, "Tester")
        logs()
        K.check(not [x for x in W.log if x[0] == "gone"] and Data.eidOf(at(cs, "hotbar", 1)) is None, "F1: unstamped tools -> no wardrobe:fn:gone call")

    # ================================================================ UB: Upgrade materials from the bags
    bar = [m_ for m_ in um if "Bar" in m_][0]
    ess = [m_ for m_ in um if m_ != bar][0]
    inv, cs = mkinv()
    reset(inv)
    cs["hotbar"].setItemStackForSlot(JShort(0), gear(fr_, rolled(fr_, 2)))
    cs["storage"].setItemStackForSlot(JShort(0), stack(bar, um[bar] - 2))
    cs["storage"].setItemStackForSlot(JShort(1), stack(ess, um[ess]))
    S.bag = {bar: 5}
    sh_ = str(Up.shortOfU(inv, U1, Up.cost(fr_, to_)))
    rb = Up.upgrade(inv, JInt(0), JInt(0), fr_, str(Forge.fp(at(cs, "hotbar", 0))), U1, "Tester")
    lb = logs()
    K.check(sh_ == "None" and int(rb[0]) == 1 and str(at(cs, "hotbar", 0).getItemId()) == to_ and S.bag[bar] == 3 and cnt(inv, [bar])[bar] == 0
            and ("take", bar, 2) in S.log and ("bagcommit", bar, 2) in S.log and not [x for x in S.log if x[0] == "put"]
            and any(" UPGRADE-BEGIN " in l_ and "@bags" in l_ for l_ in lb) and not any("UPGRADE-COUNT" in l_ for l_ in lb),
            "UB: inventory short by 2 bars -> the rest from the bags (take 2, commit 2), the plan lists '@bags', the count check passes")
    # short even with the bags
    inv, cs = mkinv()
    reset(inv)
    cs["hotbar"].setItemStackForSlot(JShort(0), gear(fr_, rolled(fr_, 2)))
    cs["storage"].setItemStackForSlot(JShort(0), stack(bar, um[bar] - 3))
    cs["storage"].setItemStackForSlot(JShort(1), stack(ess, um[ess]))
    S.bag = {bar: 1}
    sh2 = str(Up.shortOfU(inv, U1, Up.cost(fr_, to_)))
    rb2 = Up.upgrade(inv, JInt(0), JInt(0), fr_, str(Forge.fp(at(cs, "hotbar", 0))), U1, "Tester")
    K.check(int(rb2[0]) == 0 and "You need 2 more" in sh2 and "inventory + bags" in sh2 and not [x for x in S.log if x[0] == "take"] and not logs(),
            "UB: still short with the bags -> '%s', nothing taken" % sh2)
    # the bags give less than counted -> inventory part restored, the bag part put back
    inv, cs = mkinv()
    reset(inv)
    cs["hotbar"].setItemStackForSlot(JShort(0), gear(fr_, rolled(fr_, 2)))
    cs["storage"].setItemStackForSlot(JShort(0), stack(bar, um[bar] - 2))
    cs["storage"].setItemStackForSlot(JShort(1), stack(ess, um[ess]))
    S.bag = {bar: 5}
    S.take_short = 1
    b_ub = (cnt(inv, [bar, ess, fr_]), dict(S.bag))
    rb3 = Up.upgrade(inv, JInt(0), JInt(0), fr_, str(Forge.fp(at(cs, "hotbar", 0))), U1, "Tester")
    S.take_short = 0
    l3 = logs()
    K.check(int(rb3[0]) == -1 and "bags could not give" in str(rb3[1]) and (cnt(inv, [bar, ess, fr_]), dict(S.bag)) == b_ub
            and ("put", bar, 1) in S.log and any("UPGRADE-FAILED" in l_ and "RESTORED" in l_ for l_ in l3),
            "UB: the bags give 1 of 2 -> the inventory part restored, that 1 put back: nothing used")
    # (b) fails after the bag take -> the bag part goes back too
    inv, cs = mkinv(fail=("hotbar",))
    reset(inv)
    cs["hotbar"].setItemStackForSlot(JShort(0), gear(fr_, rolled(fr_, 2)))
    cs["storage"].setItemStackForSlot(JShort(0), stack(bar, um[bar] - 2))
    cs["storage"].setItemStackForSlot(JShort(1), stack(ess, um[ess]))
    cs["hotbar"].refuseId = to_
    S.bag = {bar: 5}
    b_ub4 = (cnt(inv, [bar, ess, fr_]), dict(S.bag))
    rb4 = Up.upgrade(inv, JInt(0), JInt(0), fr_, str(Forge.fp(at(cs, "hotbar", 0))), U1, "Tester")
    logs()
    K.check(int(rb4[0]) == -1 and (cnt(inv, [bar, ess, fr_]), dict(S.bag)) == b_ub4 and ("put", bar, 2) in S.log,
            "UB: the item's slot refuses the next tier after the bag take -> inventory + bags both back")
    sacks_on(False)
    K.check(int(Up.bagHave(U1, bar)) == 0 and str(Up.bagBack(U1, JArray(JString)([bar]), JArray(JLong)([2]))) == bar + " x2 @bags",
            "UB: no SkyySacks: bagHave 0; bagBack reports what could not go back")
    sacks_on(True)

    # ================================================================ P: the pages
    def uitext(ub_):
        out_ = []
        for c_ in ub_.getCommands():
            for f_ in ("selector", "data", "text"):
                try:
                    v_ = getattr(c_, f_)
                    if v_ is not None:
                        out_.append(str(v_))
                except Exception:
                    pass
        return chr(10).join(out_)

    def cmds(ub_):
        out_ = []
        for c_ in ub_.getCommands():
            vals = {}
            for f_ in ("selector", "data", "text"):
                try:
                    v_ = getattr(c_, f_)
                    vals[f_] = None if v_ is None else str(v_)
                except Exception:
                    vals[f_] = None
            out_.append(vals)
        return out_

    def child_sum(ub_, parent, key="Height"):
        """the summed Anchor <key> of the elements appended straight into parent"""
        tot = 0
        for v_ in cmds(ub_):
            if v_["selector"] != parent:
                continue
            dat = v_["text"] if v_["text"] and "Anchor" in v_["text"] else (v_["data"] or "")
            m_ = re.match(r"^\s*\w+[^{]*\{\s*Anchor: \(([^)]*)\)", dat)
            if m_:
                h_ = re.search(key + r": (\d+)", m_.group(1))
                tot += int(h_.group(1)) if h_ else 0
        return tot

    def evtext(ue_):
        out_ = []
        for e_ in ue_.getEvents():
            for f_ in ("selector", "data", "eventData"):
                try:
                    v_ = getattr(e_, f_)
                    if v_ is not None:
                        out_.append(str(v_))
                except Exception:
                    pass
            try:
                out_.append(str(e_.getData()))
            except Exception:
                pass
        return chr(10).join(out_)
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    try:
        FPR = JClass(FAKE_PKG + ".FakePR")
        prx = us.allocateInstance(FPR.class_)
    except Exception:
        FPR = None
        prx = us.allocateInstance(PR.class_)
    jf(PR, "uuid").set(prx, U1)
    jf(PR, "username").set(prx, "Tester")
    FSP = JClass(FAKE_PKG + ".FakeSmithPage")
    FRP = JClass(FAKE_PKG + ".FakeReforgePage")
    FMP = JClass(FAKE_PKG + ".FakeMultiPage")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    for cn in ("com.hypixel.hytale.server.core.modules.entity.EntityModule", "com.hypixel.hytale.server.core.modules.entity.damage.DamageModule",
               "com.hypixel.hytale.server.core.modules.block.BlockModule", "com.hypixel.hytale.server.core.universe.Universe"):
        JClass(FAKE_PKG + ".FakeUtil").single(cn)
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    REFc = JClass("com.hypixel.hytale.component.Ref")
    FS = JClass(FAKE_PKG + ".FakeStore")
    IHM = JClass("java.util.IdentityHashMap")

    def world(inv_):
        pl = us.allocateInstance(PLA.class_)
        jf(PLA, "inventory").set(pl, inv_)
        ref = us.allocateInstance(REFc.class_)
        jf(REFc, "index").setInt(ref, JInt(7))
        st = us.allocateInstance(FS.class_)
        st.comps = JClass("java.util.HashMap")()
        pm = IHM()
        pm.put(PLA.getComponentType(), pl)
        pm.put(PR.getComponentType(), prx)
        st.comps.put(ref, pm)
        jf(REFc, "store").set(ref, st)
        return ref, st

    def render(pg_, ref_, st_):
        ub_, ue_ = UCB(), UEB()
        pg_.build(ref_, ub_, ue_, st_)
        return uitext(ub_) + chr(10) + evtext(ue_), ub_

    import skyyui as SUI
    SUI.verify(quiet=True)
    SUI.assert_page_size(1100, 880)

    # ---- the Craft tab (review fix FX2: click coalescing / the Requip row cache are tested on their own below)
    Sm.NAV_MS = JLong(0)
    Sm.RQ_MS = JLong(0)
    inv, cs = mkinv()
    reset(inv)
    give_mats(cs, mats, mult=3)
    br.put("class:" + str(U1), "Warrior")
    ref, st = world(inv)
    pg = FSP(prx)
    s0, ub0 = render(pg, ref, st)
    tab_ok = all(("SkyyGTab%d" % m_) in s0 for m_ in (3, 0, 1)) and ("SkyyGTab2" in s0) == have_mt and s0.index("SkyyGTab3") < s0.index("SkyyGTab0")
    body_h = child_sum(ub0, "#SkyyGBody")
    left_h = child_sum(ub0, "#SkyyGLeft")
    cards_h = child_sum(ub0, "#SkyyGCards")
    card_h = child_sum(ub0, "#SkyyGCard0")
    fig_h = child_sum(ub0, "#SkyyGCard0F")
    row_w = child_sum(ub0, "#SkyyGCardRow0", "Width")
    main_w = child_sum(ub0, "#SkyyGMain", "Width")
    n_cards = len(re.findall(r"Button #SkyyGCard\d+ ", s0))
    first_c = [c_ for c_ in range(5) if len(Sm.groups(U1, JInt(c_), False)) > 0][0]
    K.check(tab_ok and int(pg.cat) == first_c and n_cards == min(6, len(Sm.groups(U1, JInt(first_c), False))) and "Class: Warrior" in s0
            and body_h <= 808 and left_h <= 656 and cards_h <= 656 and card_h + 12 == 300 and fig_h == 192 and row_w == 830 and main_w == 1066
            and "ItemGridSlot" not in s0 and "Crafted gear goes to: Requip" in s0 and "ItemIcon" in s0,
            "P: /smithing opens on Craft (tabs Craft | Reforge | Upgrade%s, Craft first), %d set cards; 1080p: body %d/808, left %d/656, cards %d/656, "
            "card %d+12 = 300, figure %d = 3 x 64, row width %d = 830, main %d = 1066; no ItemGridSlot"
            % (" | Multitool" if have_mt else "", n_cards, body_h, left_h, cards_h, card_h, fig_h, row_w, main_w))
    K.notes.append("Craft tab heights: body %d/808, left %d/656, cards %d/656" % (body_h, left_h, cards_h))
    # the kit's own font tables: every static text fits its box
    fits = [("Craft every missing piece", 330, 17), ("Combat armor", 220, 17), ("Gathering armor", 220, 17), ("Multitools", 220, 17),
            ("Show all", 220, 17), ("Inventory", 220, 17), ("Return to Requip", 470, 17), ("No SkyySacks", 160, 17), ("Level too low", 160, 17), ("No materials", 160, 17),
            ("Locked", 160, 17), ("Multitool", 136, 17)]
    nofit = [(t_, w_, round(SUI.text_width(t_, s_, bold=True, upper=True))) for t_, w_, s_ in fits if SUI.text_width(t_, s_, bold=True, upper=True) > w_ - 16]
    K.check(not nofit, "P: skyyui text_width: every static button text fits its button (bold upper 17 px, 8 px padding a side): %s" % nofit)
    # Show all / My class, categories, a card, the piece page
    ev0 = int(pg.rebuilds)
    pg.handleDataEvent(ref, st, '{"a":"flt:1"}')
    sa, _u = render(pg, ref, st)
    n_all = len(re.findall(r"Button #SkyyGCard\d+ ", sa))
    showall = bool(Sm.showAll(U1))
    pg.handleDataEvent(ref, st, '{"a":"flt:0"}')
    K.check(showall and not bool(Sm.showAll(U1)) and int(pg.rebuilds) == ev0 + 2 and n_all >= n_cards,
            "P: Show all / My class switch the player's gear.smithShowAll (memory without SkyyMenu) and rebuild")
    pg.handleDataEvent(ref, st, '{"a":"cat:1"}')
    s1, ub1 = render(pg, ref, st)
    ci = [str(g_[0]) for g_ in pg.cards].index("Armor_Iron")
    pg.pageNo = JInt(ci // 6)
    s1, ub1 = render(pg, ref, st)
    K.check(int(pg.cat) == 1 and "Iron Set" in s1 and "Full set (4)" in s1 and "Mining" in s1 and "craftable" in s1,
            "P: Gathering armor shows the Iron Set card with its Mining bonus and state")
    pg.handleDataEvent(ref, st, '{"a":"card:%d"}' % ci)
    s2, ub2 = render(pg, ref, st)
    pieces_h = child_sum(ub2, "#SkyyGPieces")
    rows_h = child_sum(ub2, "#SkyyGRows")
    right_h = child_sum(ub2, "#SkyyGPRight")
    fig2 = child_sum(ub2, "#SkyyGPFig")
    tok = int(pg.token)
    K.check(int(pg.view) == 1 and str(pg.gkey) == "Armor_Iron" and "Back" in s2 and all(("#SkyyGPc%d" % i_) in s2 for i_ in range(4))
            and ('craft:0:%d' % tok) in s2 and ("craftall:%d" % tok) in s2 and pieces_h <= 656 and rows_h <= 444 and right_h <= 594 and fig2 <= 594
            and "Mining Set piece" in s2 and "Craft every missing piece" in s2,
            "P: a card click opens the piece page: 4 rows with Craft + the click token, Craft every missing piece; heights pieces %d/656, rows "
            "%d/444, right %d, figure column %d" % (pieces_h, rows_h, right_h, fig2))
    # have / need colours: enough = white, short = gold
    K.check(re.search(r"#SkyyGPc1M0L0 \{[^}]*TextColor: #ffffff", s2) is not None, "P: materials you have show white (have / need)")
    # craft from the page (into Requip); the old token is refused; a quick second click is refused
    b_pg = len(W.pool)
    pg.handleDataEvent(ref, st, '{"a":"craft:1:%d"}' % tok)
    i1 = str(pg.info)
    pg.handleDataEvent(ref, st, '{"a":"craft:1:%d"}' % tok)
    i2 = str(pg.info)
    pg.lastClick = JLong(0)
    Sm.LAST.clear()
    pg.handleDataEvent(ref, st, '{"a":"craft:1:%d"}' % tok)
    i3 = str(pg.info)
    logs()
    K.check(i1.startswith("+Made: ") and "Requip" in i1 and len(W.pool) == b_pg + 1 and i2.startswith("-Wait a moment") and "page changed" in i3,
            "P: Craft -> '%s'; a quick second click: '%s'; the old token: '%s'" % (i1[:70], i2, i3))
    # guards: profile busy, profile changed
    s3, _u = render(pg, ref, st)
    tok = int(pg.token)
    pg.lastClick = JLong(0)
    Sm.LAST.clear()
    br.put("profile:busy:" + str(U1), True)
    pg.handleDataEvent(ref, st, '{"a":"craft:3:%d"}' % tok)
    g_busy = "still loading" in str(pg.info)
    br.remove("profile:busy:" + str(U1))
    pg.epoch = "old"
    pg.handleDataEvent(ref, st, '{"a":"craft:3:%d"}' % tok)
    g_ep = "profile changed" in str(pg.info) and int(pg.view) == 0
    K.check(g_busy and g_ep, "P: profile:busy and a profile change refuse the craft (the page goes back to the cards)")
    # Craft every missing piece from the page
    pg.handleDataEvent(ref, st, '{"a":"card:%d"}' % ci)
    render(pg, ref, st)
    tok = int(pg.token)
    pg.lastClick = JLong(0)
    Sm.LAST.clear()
    pg.handleDataEvent(ref, st, '{"a":"craftall:%d"}' % tok)
    ia = str(pg.info)
    logs()
    K.check(ia.startswith("+Made ") or ia.startswith("-"), "P: Craft every missing piece from the page: '%s'" % ia[:90])
    # dest switch, back, refresh, paging, bad events, the other tabs (no command manager here: nothing breaks)
    pg.handleDataEvent(ref, st, '{"a":"dest:0"}')
    d0 = bool(Sm.toRequip(U1))
    s4, _u = render(pg, ref, st)
    pg.handleDataEvent(ref, st, '{"a":"dest:1"}')
    d1_ = bool(Sm.toRequip(U1))
    ward_on(False)
    pg.handleDataEvent(ref, st, '{"a":"dest:1"}')
    nrq = str(pg.info)
    s5, _u = render(pg, ref, st)
    ward_on(True)
    K.check(not d0 and d1_ and "Crafted gear goes to: your inventory" in s4 and "Requip is not loaded" in nrq and "Requip is not loaded" in s5,
            "P: Crafted gear to: Requip / Inventory (gear.smithToRequip); without SkyyWardrobe the Requip button is off and says so")
    for ev_ in ('{"a":"pback"}', '{"a":"prev"}', '{"a":"next"}', '{"a":"rprev"}', '{"a":"rnext"}', '{"a":"cat:9"}', '{"a":"cat:x"}',
                '{"a":"card:99"}', '{"a":"craft:x:1"}', '{"a":"craft:99:1"}', '{"a":"craftall:1"}', '{"a":"mode:0"}', '{"a":"mode:1"}',
                '{"a":"mode:2"}', '{"a":"mode:3"}', '{"a":""}'):
        pg.handleDataEvent(ref, st, ev_)
    pg.handleDataEvent(ref, st, None)
    pg.handleDataEvent(ref, st, '{"a":"refresh"}')
    cl0 = int(pg.closes)
    pg.handleDataEvent(ref, st, '{"a":"back"}')
    K.check(int(pg.closes) == cl0 + 1, "P: back closes the page (no SkyyMenu); refresh / paging / bad events / the other tab clicks handled without an error")
    # every category renders (and the empty state with the filter)
    cat_bad = []
    for c_ in range(5):
        if c_ == 4 and not have_mt:
            continue
        pg.handleDataEvent(ref, st, '{"a":"cat:%d"}' % c_)
        sc, ubc = render(pg, ref, st)
        empty_ok = len(Sm.groups(U1, JInt(c_), True)) == 0 and "can be crafted on this server yet" in sc
        if int(pg.cat) != c_ or child_sum(ubc, "#SkyyGBody") > 808 or not (re.search(r"Button #SkyyGCard0 ", sc) or empty_ok):
            cat_bad.append(c_)
        if c_ >= 2 and len(pg.cards) > 0:
            pg.handleDataEvent(ref, st, '{"a":"card:0"}')
            sp2, ubp = render(pg, ref, st)
            if child_sum(ubp, "#SkyyGRows") > 444 or "#SkyyGPc0" not in sp2 or "Craft every missing piece" in sp2 or "rolls a rarity like a bench craft" not in sp2:
                cat_bad.append((c_, "pieces"))
            pg.handleDataEvent(ref, st, '{"a":"craftall:%d"}' % int(pg.token))
            if "only for armor sets" not in str(pg.info) and "for armor sets" not in str(pg.info):
                cat_bad.append((c_, "craftall"))
            pg.handleDataEvent(ref, st, '{"a":"pback"}')
    br.put("class:" + str(U1), "Mage")
    pg.handleDataEvent(ref, st, '{"a":"cat:2"}')
    sm_, _u = render(pg, ref, st)
    br.remove("class:" + str(U1))
    K.check(not cat_bad and "Staffs" in sm_ and "Swords" not in sm_, "P: every category renders inside 808 px with cards + piece page; a Mage's Weapons show staffs, no swords: %s" % cat_bad)
    # SkyySacks absent: the page browses, Craft refuses with the note
    sacks_on(False)
    pg2 = FSP(prx)
    pg2.handleDataEvent(ref, st, '{"a":"cat:1"}')
    render(pg2, ref, st)
    pg2.handleDataEvent(ref, st, '{"a":"card:0"}')
    s6, _u = render(pg2, ref, st)
    tok2 = int(pg2.token)
    pg2.lastClick = JLong(0)
    Sm.LAST.clear()
    pg2.handleDataEvent(ref, st, '{"a":"craft:0:%d"}' % tok2)
    s7, _u = render(FSP(prx), ref, st)
    K.check("Browse only - needs SkyySacks 0.7.17" in s7 and "crafting waits for SkyySacks 0.7.17" in s6 and '"No SkyySacks"' in s6
            and "Crafting here needs SkyySacks 0.7.17" in s6 and "SkyySacks 0.7.17" in str(pg2.info),
            "FX3/P: without SkyySacks 0.7.17 the cards say 'Browse only', the buttons 'No SkyySacks', the gold line the full note; a click: '%s'" % str(pg2.info))
    sacks_on(True)
    # FX3 (review fix, spec 4.3 "greyed with the reason"): locked -> 'Locked' buttons + the accessory sentence; no materials -> 'No materials'
    pg3 = FSP(prx)
    pg3.handleDataEvent(ref, st, '{"a":"cat:1"}')
    render(pg3, ref, st)
    iron_i = [i_ for i_, g_ in enumerate(pg3.cards) if IRONC in [str(x) for x in g_[1]]]
    pg3.handleDataEvent(ref, st, '{"a":"card:%d"}' % (iron_i[0] if iron_i else 0))
    S.allowed = set()
    s8, ub8 = render(pg3, ref, st)
    S.allowed = None
    _l8 = s8.split(chr(10))
    why8 = [_l8[i_ + 1] for i_ in range(len(_l8) - 1) if "SkyyGPWhy.Text" in _l8[i_]]
    inv9, cs9 = mkinv()
    reset(inv9)
    ref9, st9 = world(inv9)
    s9, ub9 = render(pg3, ref9, st9)
    K.check('"Locked"' in s8 and "Cannot craft" not in s8 and why8 and "accessory" in why8[0] and child_sum(ub8, "#SkyyGPRight") <= 594
            and '"No materials"' in s9 and child_sum(ub9, "#SkyyGPRight") <= 594,
            "FX3: a piece row names its reason: Locked (+ the gold line '%s'), No materials; the piece page still fits (%d/594)"
            % (why8[0][-90:] if why8 else None, child_sum(ub8, "#SkyyGPRight")))
    # FX4 (review fix): a recipe with 5+ materials -> the 4th line lists every remaining material, gold when one is short
    g4 = pg3.grp
    rid4, out4 = str(g4[2][0]), str(g4[1][0])
    fids = JArray(JString)(["Ingredient_Bar_Iron", "Ingredient_Stick", "Ingredient_Fibre", "Ingredient_Leather_Light", "Ingredient_Bar_Gold"])
    pg3.hc = JClass("java.util.HashMap")()
    pg3.hc.put(rid4, JArray(JClass("java.lang.Object"))([Long_(0), fids, JArray(JLong)([5, 5, 5, 9, 1]), JArray(JLong)([1, 1, 1, 2, 3])]))
    pg3.al = None
    ub4, ue4 = UCB(), UEB()
    ub4.appendInline("#X", "Group #SkyyGRows { }")
    pg3.why1 = None
    pg3.pieceRow(ub4, ue4, JInt(0), rid4, out4, U1, inv9)
    s4 = uitext(ub4)
    K.check("see Refresh" not in s4 and "Leather" in s4 and "9/2" in s4 and "Gold" in s4 and "1/3" in s4,
            "FX4: 5 materials -> the 4th line lists the rest with have / need (no '+N more (see Refresh)')")
    # FX2 (review fix): one craftHave per recipe per page build; navigation clicks within NAV_MS dropped; Requip rows read once a second
    del S.haves[:]
    pg3.handleDataEvent(ref, st, '{"a":"pback"}')
    render(pg3, ref, st)
    h_cards = list(S.haves)
    del S.haves[:]
    pg3.handleDataEvent(ref, st, '{"a":"card:0"}')
    render(pg3, ref, st)
    h_rows = list(S.haves)
    K.check(h_cards and len(h_cards) == len(set(h_cards)) and h_rows and len(h_rows) == len(set(h_rows)),
            "FX2: craftHave once per recipe per build (cards: %d calls / %d recipes; piece page: %d / %d)"
            % (len(h_cards), len(set(h_cards)), len(h_rows), len(set(h_rows))))
    Sm.NAV_MS = JLong(150)
    pg5 = FSP(prx)
    r5_0 = int(pg5.rebuilds)
    pg5.handleDataEvent(ref, st, '{"a":"cat:2"}')
    pg5.handleDataEvent(ref, st, '{"a":"cat:3"}')
    pg5.handleDataEvent(ref, st, '{"a":"next"}')
    r5_1 = int(pg5.rebuilds)
    c5 = int(pg5.cat)
    pg5.lastNav = JLong(0)
    pg5.handleDataEvent(ref, st, '{"a":"cat:3"}')
    Sm.NAV_MS = JLong(0)
    K.check(r5_1 - r5_0 == 1 and c5 == 2 and int(pg5.cat) == 3 and int(pg5.rebuilds) - r5_0 == 2,
            "FX2: three navigation clicks inside 150 ms -> 1 rebuild (the later two dropped, page unchanged); after the gap the click works")
    # ---- the Reforge / Upgrade pages: Craft tab first, the Requip rows, fetch, Return to Requip
    inv, cs = mkinv()
    reset(inv)
    cs["hotbar"].setItemStackForSlot(JShort(0), gear("Weapon_Sword_Iron", rolled("Weapon_Sword_Iron", 1)))
    W.pool["0000c0de"] = ("items", stamp(gear(SOUL[1], rolled(SOUL[1], 2)), "0000c0de"))
    W.pool["0000f00d"] = ("armor", stamp(gear("Armor_Cloth_Cotton_Chest", rolled("Armor_Cloth_Cotton_Chest", 1)), "0000f00d"))
    W.pool["00000bad"] = ("items", stamp(stack("Ingredient_Stick"), "00000bad"))
    ref, st = world(inv)
    rp = FRP(prx)
    rp.preselect(inv)
    r0, ur0 = render(rp, ref, st)
    K.check("SkyyGTab3" in r0 and r0.index("SkyyGTab3") < r0.index("SkyyGTab0") and "In Requip (2)" in r0 and "rq:0" in r0 and "rq:1" in r0
            and "rq:2" not in r0 and "Requip - Lv" in r0 and child_sum(ur0, "#SkyyGAnvil") <= 674 and '"SMITHING"' not in r0,
            "P: the Reforge page: Craft | Reforge | ... tab row; 'In Requip (2)' rows (forgeable only, never the stick)")
    rq_ids = [str(e_[1]) for e_ in rp.rq]
    rp.handleDataEvent(ref, st, '{"a":"rq:%d"}' % rq_ids.index("Armor_Cloth_Cotton_Chest"))
    on_ = rp.selId is not None and str(rp.selId) == "Armor_Cloth_Cotton_Chest"
    r1_, _u = render(rp, ref, st)
    K.check(on_ and "0000f00d" not in W.pool and W.out.get("0000f00d") and "taken out of Requip" in str(rp.info) and "Return to Requip" in r1_,
            "P: a Requip row click fetches it (wardrobe:fn:fetch: OUT, stamp kept) and puts it on the anvil; 'Return to Requip' shows")
    rp.handleDataEvent(ref, st, '{"a":"rqback"}')
    K.check("0000f00d" in W.pool and rp.selSec == -1 and "went back into Requip" in str(rp.info), "P: Return to Requip deposits it back (depositSlot)")
    rp.handleDataEvent(ref, st, '{"a":"rqback"}')
    K.check("Nothing from Requip" in str(rp.info), "P: Return to Requip with nothing stamped on the anvil refused")
    # Upgrade mode: only items with a next tier (the cage), fetch -> on the Upgrade anvil
    rp.handleDataEvent(ref, st, '{"a":"mode:1"}')
    u0, uu0 = render(rp, ref, st)
    rq_u = [str(e_[1]) for e_ in rp.rq]
    K.check(int(rp.mode) == 1 and rq_u == [SOUL[1]] and "In Requip (1)" in u0,
            "P: the Upgrade list's Requip rows = items with a next tier only (%s)" % rq_u)
    rp.handleDataEvent(ref, st, '{"a":"rq:0"}')
    u1, uu1 = render(rp, ref, st)
    K.check(str(rp.selId) == SOUL[1] and "Next tier: " in u1 and "Materials - have / need (inventory, then bags)" in u1 and child_sum(uu1, "#SkyyGAnvil") <= 674,
            "P: a Requip cage fetched onto the Upgrade anvil; the materials line counts the bags")
    ward_on(False)
    u2, _u = render(rp, ref, st)
    rp.handleDataEvent(ref, st, '{"a":"rq:0"}')
    ward_on(True)
    K.check("In Requip" not in u2, "P: without SkyyWardrobe 0.2 the lists have no Requip rows")
    # FX2: the Requip rows are read at most once per RQ_MS per page (2 spaces = 2 list calls), again right after a fetch
    Sm.RQ_MS = JLong(1000)
    rp6 = FRP(prx)
    rp6.preselect(inv)
    W.lists[0] = 0
    render(rp6, ref, st)
    render(rp6, ref, st)
    render(rp6, ref, st)
    l6a = W.lists[0]
    rp6.handleDataEvent(ref, st, '{"a":"rq:0"}')
    render(rp6, ref, st)
    l6b = W.lists[0]
    Sm.RQ_MS = JLong(0)
    K.check(l6a == 2 and l6b == 4, "FX2: Reforge list: 3 rebuilds inside 1 s -> wardrobe:fn:list x%d (want 2); a fetch re-reads (x%d, want 4)" % (l6a, l6b))
    K.check(bool(rp.rqEvent(ref, st, '{"a":"mode:3"}')) and not bool(rp.rqEvent(ref, st, '{"a":"forge"}')) and not bool(rp.rqEvent(ref, st, None)),
            "P: the Reforge page's Craft tab click (mode:3) is handled (opens /smithing through the command)")
    if have_mt:
        mp = FMP(prx)
        ubm, uem = UCB(), UEB()
        mp.build(ref, ubm, uem, st)
        sm2 = uitext(ubm)
        mp.handleDataEvent(ref, st, '{"a":"mode:3"}')
        K.check("SkyyGTab3" in sm2 and "Smithing" in sm2, "P: the /multitool page (titled Smithing) shows the Craft tab; its click is handled")
    # tab counts: 4 / without Craft / only Reforge
    n4 = int(Ui.tabs(UCB(), UEB(), "#X", JInt(0), JInt(562), "T"))
    apply(part__smithing="false")
    n3 = int(Ui.tabs(UCB(), UEB(), "#X", JInt(0), JInt(562), "T"))
    apply(part__smithing="false", part__upgrade="false", part__multitool="false")
    n1 = int(Ui.tabs(UCB(), UEB(), "#X", JInt(0), JInt(562), "T"))
    apply()
    K.check(n4 == (4 if have_mt else 3) and n3 == n4 - 1 and n1 == 1, "P: tabs: %d with Craft, %d without, 1 = the old title" % (n4, n3))
    # /smithing (+ /smith) and gear:fn:smithing
    SC = P("SmithCmd")
    cmd = SC()
    groups_ = None
    k_ = cmd.getClass()
    while k_ is not None and groups_ is None:
        for f_ in k_.getDeclaredFields():
            if "ermissionGroups" in str(f_.getName()):
                f_.setAccessible(True)
                groups_ = f_.get(cmd)
        k_ = k_.getSuperclass()
    K.check(str(cmd.getName()) == "smithing" and "smith" in [str(x) for x in cmd.getAliases()] and groups_ is not None
            and "hytale:Adventurer" in [str(x) for x in groups_], "P: /smithing (alias /smith), permission group hytale:Adventurer (COMMAND RULES)")
    exe = [m_ for m_ in SC.class_.getDeclaredMethods() if str(m_.getName()) == "execute"][0]
    exe.setAccessible(True)
    said = []
    if FPR is not None:
        prx.said = None
        apply(part__smithing="false")
        exe.invoke(cmd, None, st, ref, prx, None)
        apply()
        exe.invoke(cmd, None, st, ref, prx, None)
        said = [str(x) for x in (prx.said or [])]
    K.check(FPR is None or (len(said) >= 2 and "switched off" in said[0] and "could not open the Smithing page" in said[-1]),
            "P: /smithing executed: off -> 'switched off - opening Reforge'; on -> the page made + opened (the stand-in has no page manager): %s" % said)
    so = SF(JInt(0))
    so_r = so.apply(ObjArr([U1, JString("reforge")]))
    K.check(so_r is not None and not bool(so_r) and so.apply(None) is None and so.apply(ObjArr([JString("x")])) is None,
            "P: gear:fn:smithing: no online player here -> FALSE (never throws); bad input -> null")
    K.save(n=len(outs))


# ====================================================================================================== R: the REAL SkyySacks 0.7.17 bridge
def run_real(out):
    """SkyySacks 0.7.17's real craftList / craftHave / craftPay / craftRefund / craftCommit (its own classes, the harness player seam
    SackBridge.PLAYERS, a scratch pool file) driven by GearSmith.craft on the booted engine's real recipes."""
    from jpype import JClass, JInt, JShort, JLong, JByte, JImplements, JOverride, JObject, JArray, JString
    K = Child(out)
    _jvm([B.SERVER_JAR, B.JAVASSIST, JAR, SK_JAR, FAKE_DIR], verify=True, big=True)
    E = H["engine_boot"](K)
    ITEM, us, jf = E["ITEM"], E["us"], E["jf"]
    CRR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    HAL = JClass("java.util.ArrayList")
    lst = HAL()
    for it in list(ITEM.getAssetMap().getAssetMap().values()):
        if it is not None and it.hasRecipesToGenerate():
            it.collectRecipesToGenerate(lst)
    if lst.size() > 0:
        CRR.getAssetStore().loadAssets("Hytale:Hytale", lst)
    P = lambda n: JClass(PKG + n)
    Sm, Gear, Stamp, Cfg, Data = P("GearSmith"), P("Gear"), P("GearStamp"), P("GearCfg"), P("GearData")
    Props, SR = JClass("java.util.Properties"), JClass("java.io.StringReader")
    p_ = Props()
    p_.load(SR(str(Cfg.defaultsText())))
    Cfg.apply(p_, False)
    SB = JClass("com.skyy.sacks.SackBridge")
    SP = JClass("com.skyy.sacks.SackPool")
    SFn = JClass("com.skyy.sacks.SackFn")
    FCC = JClass("com.hypixel.hytale.server.core.asset.type.item.config.FieldcraftCategory")
    try:
        DAM = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
        f_ = FCC.class_.getDeclaredField("ASSET_MAP")
        f_.setAccessible(True)
        if f_.get(None) is None:
            f_.set(None, DAM(JClass("java.util.HashMap")()))
    except Exception as ex:
        K.notes.append("FieldcraftCategory map not set: %s" % ex)
    INV = JClass("com.hypixel.hytale.server.core.inventory.Inventory")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    ICOMP = "com.hypixel.hytale.server.core.inventory.InventoryComponent$"

    def comp(kind, cont):
        Cc = JClass(ICOMP + kind)
        for args in ((cont, JByte(0)), (cont,)):
            try:
                return Cc(*args)
            except Exception:
                pass
        o_ = us.allocateInstance(Cc.class_)
        jf(Cc, "inventory").set(o_, cont)
        return o_
    inv = INV()
    cs = {}
    for f_, kind, n_ in (("hotbar", "Hotbar", 9), ("storage", "Storage", 36), ("backpack", "Backpack", 9), ("armor", "Armor", 4), ("utility", "Utility", 4), ("tools", "Tool", 4)):
        cs[f_] = SIC(JShort(n_))
        jf(INV, f_).set(inv, comp(kind, cs[f_]))
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    pl = us.allocateInstance(PLA.class_)
    jf(PLA, "inventory").set(pl, inv)
    U = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-0000000c0723")

    @JImplements("java.util.function.Function")
    class Players(object):
        @JOverride
        def apply(self, o):
            return pl
    SB.PLAYERS = Players()
    pd = os.path.join(SCRATCH, "real", "pools")
    os.makedirs(pd, exist_ok=True)
    SP.DIR = JClass("java.nio.file.Paths").get(pd)
    br = Gear.bridge()
    for i_, key in enumerate(("sacks:fn:count", "sacks:fn:take", "sacks:fn:put", "sacks:fn:all", "sacks:fn:commit", "sacks:fn:deposit",
                              "sacks:fn:pocketFill", "sacks:fn:craftList", "sacks:fn:craftHave", "sacks:fn:craftPay", "sacks:fn:craftRefund",
                              "sacks:fn:craftCommit")):
        br.put(key, SFn(JInt(i_)))
    rows = dict((str(r_[1]), str(r_[0])) for r_ in Sm.recipes())
    rc = rows.get("Armor_Iron_Chest")
    ins = [(str(q.getItemId()), int(q.getQuantity())) for q in CRR.getAssetMap().getAsset(rc).getInput() if q is not None and q.getItemId() is not None]
    benches = [(str(b_.id), int(b_.requiredTierLevel)) for b_ in CRR.getAssetMap().getAsset(rc).getBenchRequirement()]
    acc = ",".join("Skyy_Accessory_%s_T3" % b_ for b_, _t in benches)
    br.put("acc:has:" + str(U), acc)
    al0 = Sm.allowed(U)
    for j_, (k_, v_) in enumerate(ins):
        cs["storage"].setItemStackForSlot(JShort(j_), IS(k_, JInt(v_)))
    hv = None
    try:
        hv = Sm.have(U, inv, rc, CRR.getAssetMap().getAsset(rc))
    except Exception as ex:
        K.notes.append("real craftHave threw: %s" % ex)
    r_ = None
    try:
        r_ = Sm.craft(inv, U, "Tester", rc, False)
    except Exception as ex:
        K.notes.append("real craft threw: %s" % ex)
    made = [cs["storage"].getItemStack(JShort(i_)) for i_ in range(36)]
    made = [x for x in made if x is not None and not x.isEmpty() and str(x.getItemId()) == "Armor_Iron_Chest"]
    left = dict((k_, sum(int(x.getQuantity()) for x in [cs["storage"].getItemStack(JShort(i_)) for i_ in range(36)] if x is not None and not x.isEmpty() and str(x.getItemId()) == k_)) for k_, _v in ins)
    K.notes.append("REAL SkyySacks: allowed %s, have %s, craft %s" % (None if al0 is None else (rc in [str(x) for x in al0]),
                                                                   None if hv is None else int(hv[0]), None if r_ is None else (int(r_[0]), str(r_[1]))))
    K.check(al0 is not None and rc in [str(x) for x in al0] and hv is not None and int(hv[0]) >= 1 and r_ is not None and int(r_[0]) == 1
            and len(made) == 1 and Data.effective("Armor_Iron_Chest", made[0].getMetadata()) is not None and all(v_ == 0 for v_ in left.values()),
            "R: the REAL SkyySacks 0.7.17 bridge: craftList allows %s with the %s accessory, craftHave counts it, GearSmith.craft pays through "
            "craftPay (the materials gone: %s), the rolled item is delivered, craftCommit" % (rc, acc, left))
    # refused by the real rule: no accessory -> GearSmith refuses before any payment
    br.put("acc:has:" + str(U), "")
    for j_, (k_, v_) in enumerate(ins):
        cs["storage"].setItemStackForSlot(JShort(j_), IS(k_, JInt(v_)))
    r2 = Sm.craft(inv, U, "Tester", rc, False)
    K.check(int(r2[0]) == 0 and "accessory" in str(r2[1]), "R: the real rule without the accessory: refused '%s'" % str(r2[1]))
    K.save()


# ====================================================================================================== C: class compare
def run_compare(out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.JAVASSIST], verify=False)
    CPc = JClass("javassist.ClassPool")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def pool_of(j):
        p_ = CPc(False)
        p_.appendSystemPath()
        p_.appendClassPath(B.SERVER_JAR)
        p_.appendClassPath(j)
        return p_

    def members(p_, cn, vers):
        c_ = p_.get(cn)
        d_ = {}
        for f_ in c_.getDeclaredFields():
            d_["f " + str(f_.getName())] = str(f_.getSignature())

        def code(b_):
            mi_ = b_.getMethodInfo()
            ca_ = mi_.getCodeAttribute()
            if ca_ is None:
                return ""
            it_ = ca_.iterator()
            cpl_ = mi_.getConstPool()
            lines_ = []
            while it_.hasNext():
                pos_ = it_.next()
                t_ = re.sub(r"#\d+ = ", "", str(IP.instructionString(it_, pos_, cpl_))).replace("ldc_w ", "ldc ")
                t_ = re.sub(r"^((if\w*|goto|goto_w|jsr|jsr_w) )\d+$", r"\1N", t_)
                for v_ in vers:
                    t_ = t_.replace(v_, "VER")
                lines_.append(t_)
            return "\n".join(lines_)
        for m_ in c_.getDeclaredMethods():
            d_["m " + str(m_.getName()) + str(m_.getSignature())] = code(m_)
        for m_ in c_.getDeclaredConstructors():
            d_["c " + str(m_.getSignature())] = code(m_)
        ci = c_.getClassInitializer()
        if ci is not None:
            d_["<clinit>"] = code(ci)
        return d_

    pa, pb = pool_of(OLD_JAR), pool_of(JAR)
    na, nb = jar_classes(OLD_JAR), jar_classes(JAR)
    diffs = {}
    for cn in sorted(set(na) & set(nb)):
        ma, mb = members(pa, cn, (OLD_VERSION, VERSION)), members(pb, cn, (OLD_VERSION, VERSION))
        dd = sorted(k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k))
        if dd:
            diffs[cn.split(".")[-1]] = [("+" if k not in ma else ("-" if k not in mb else "~")) + k.split("(")[0] for k in dd]
    add = sorted(x.split(".")[-1] for x in set(nb) - set(na))
    gone = sorted(set(na) - set(nb))
    print("C. class compare %s -> %s: + %s - %s" % (OLD_VERSION, VERSION, add, gone))
    for k in sorted(diffs):
        print("   %-16s %s" % (k, ", ".join(diffs[k])[:1500]))
    K.check(set(add) == NEW_CLASSES and not gone, "C: added exactly GearSmith / SmithPage / SmithCmd / SmithFn, none removed: + %s - %s" % (add, gone))
    want = {
        "GearData": {"+m carry", "+m stampKey", "+m eidOf"},
        "GearMerge": {"+m rqGone", "~m merge"},
        "GearUp": {"+m bagHave", "+m bagBack", "+m bagCommit", "+m shortOfU", "~m upgrade"},
        "GearUi": {"~m tabs", "+m cardStyle", "+m cell", "+m gap"},
        "ReforgePage": {"+f rq", "+f rqAt", "+f rqMode", "+m rqRows", "+m rqBackable", "+m rqAppend", "+m rqEvent", "~m list", "~m upList", "~m handleDataEvent",
                        "~m build", "~m upBuild", "~m upMats", "~m upAnvil"},
        "MultiPage": {"~m build", "~m handleDataEvent"},
        "GearIdent": {"~m reroll"},          # FIXER 2: re-identify carries foreign keys
        "SkyyGearPlugin": {"~m setup"},
    }
    bad = {}
    for k in set(want) | set(diffs):
        if k.startswith("GearCfg") or k.startswith("Cfg") or k == "GearDefs":
            continue
        got = set(diffs.get(k, []))
        if got != want.get(k, set()):
            bad[k] = (sorted(want.get(k, set()) - got), sorted(got - want.get(k, set())))
    K.check(not bad, "C: changed exactly the listed members outside the config classes (missing / extra): %s" % bad)
    cfgd = dict((k, v) for k, v in diffs.items() if k.startswith("GearCfg") or k.startswith("Cfg") or k == "GearDefs")
    K.check(all(any(x in " ".join(v) for x in ("SMITH_ON", "SMITH_ARM", "apply", "<clinit>", "defaultsText", "ROW", "check", "KEY", "LBL",
                                                 "HELP", "DEF", "MIN", "MAX", "CAT", "OPTS", "TYPE", "FLAGS", "UNIT", "TARGET", "~m", "+f"))
                for v in cfgd.values()), "C: the config classes changed only for the 2 new rows: %s" % cfgd)
    K.save(diffs=diffs)


# ====================================================================================================== D: start twice on a scratch copy
def run_start(out, home, which):
    from jpype import JClass
    K = Child(out)
    jar = JAR if which == "new" else OLD_JAR
    _jvm([B.SERVER_JAR, jar], verify=(which == "new"))
    Cfg = JClass(PKG + "GearCfg")
    Path = JClass("java.nio.file.Paths")
    Cfg.DIR = Path.get(home)
    Cfg.FILE = Path.get(os.path.join(home, "config.properties"))
    JClass(PKG + "GearLog").FILE = Path.get(os.path.join(home, "gear.log"))
    snaps = []
    for step in (1, 2):
        for m in ("migrate011", "migrateStat011", "migrate012", "migrate013", "migrate02", "migrate021", "migrate023", "migrate025", "migrate0214",
                  "migrate0215", "migrate0216", "migrate0217", "migrate0218"):
            getattr(Cfg, m)()
        Cfg.load()
        snaps.append(open(os.path.join(home, "config.properties"), "rb").read())
    K.check(snaps[1] == snaps[0], "D/%s: the 2nd start changes nothing" % which)
    if which == "new":
        K.check(bool(Cfg.SMITH_ON) and str(Cfg.SMITH_ARM).startswith("Warrior:Heavy"), "D/new: the live file has no 0.2.23 rows -> the defaults apply")
    K.save(cfg=snaps[0].decode("latin-1"))


# ====================================================================================================== parent
def child(env, *args):
    return subprocess.run([sys.executable, os.path.abspath(__file__)] + list(args) + ["--dir", SCRATCH, "--jar", JAR, "--old", OLD_JAR], env=env)


def take(path, label):
    if not os.path.isfile(path):
        check(False, "%s: the child wrote no result" % label)
        return None
    d = json.load(open(path))
    OKS[0] += d["ok"]
    for f in d["fails"]:
        FAILS.append("%s: %s" % (label, f))
    for n in d.get("notes", []):
        print("  note (%s): %s" % (label, n))
    return d


def main():
    for flag, fn in (("--mkfake", lambda: run_mkfake3(arg("--mkfake"))), ("--verify", lambda: H["run_verify"](arg("--out"))),
                     ("--hub", lambda: run_hub(arg("--out"))), ("--real", lambda: run_real(arg("--out"))),
                     ("--compare", lambda: run_compare(arg("--out"))),
                     ("--start", lambda: run_start(arg("--out"), arg("--start"), arg("--which"))), ("--audit", lambda: H["run_audit"](arg("--out")))):
        if flag in sys.argv:
            try:
                fn()
            except SystemExit:
                raise
            except Exception:
                import traceback
                traceback.print_exc()
                sys.exit(1)
            return
    assert os.path.isfile(JAR) and os.path.isfile(OLD_JAR) and os.path.isfile(AR_SRC), (JAR, OLD_JAR, AR_SRC)
    sc = os.path.realpath(SCRATCH)
    assert sc.startswith(os.path.realpath(SCR_ROOT) + os.sep), "the scratch folder must be inside " + SCR_ROOT
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"), exist_ok=True)
    os.makedirs(os.path.join(SCRATCH, "packs"), exist_ok=True)
    with zipfile.ZipFile(OLD_JAR) as z_:
        assert '"Version": "%s"' % OLD_VERSION in z_.read("manifest.json").decode("utf-8"), "the old jar is not " + OLD_VERSION
    shutil.copyfile(AR_SRC, AR_JAR)              # read-only sources; the children load the scratch copies
    for src, dst, what in ((AC_SRC, AC_JAR, "SkyyAccessories 0.5.11"), (MT_SRC, MT_JAR, "Multitools 1.2.9"), (SK_SRC, SK_JAR, "SkyySacks 0.7.17")):
        if os.path.isfile(src):
            shutil.copyfile(src, dst)
        else:
            print("note: no %s jar - its part runs without it" % what)
    print("note: SkyyWardrobe 0.2 jar %s - Requip is the contract stand-in" % ("FOUND (not wired: R4 integration)" if os.path.isfile(WD_SRC) else "not on disk"))
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.environ["TEMP"] = os.environ["TMP"] = env["TEMP"]
    try:
        run_assets()
        p = child(env, "--mkfake", FAKE_DIR)
        check(p.returncode == 0, "F: the stand-ins were generated")
        runs = [("verify", "--verify"), ("compare", "--compare"), ("hub", "--hub")]
        if os.path.isfile(SK_JAR):
            runs.append(("real", "--real"))
        for label, flag in runs:
            out = os.path.join(SCRATCH, "%s.json" % label)
            pr = child(env, flag, "--out", out)
            check(pr.returncode == 0, "%s: the child exited cleanly (%s)" % (label, pr.returncode))
            take(out, label)
        res = {}
        for which in ("old", "new"):
            home = os.path.join(SCRATCH, "live-" + which)
            shutil.copytree(LIVE_DIR, home)
            out = os.path.join(SCRATCH, "start-%s.json" % which)
            pr = child(env, "--start", home, "--which", which, "--out", out)
            check(pr.returncode == 0, "D/%s: the child exited cleanly" % which)
            res[which] = take(out, "start-" + which)
        print("D. live Skyy_SkyyGear copied twice (read-only source %s)" % LIVE_DIR)
        if res.get("old") and res.get("new"):
            check(res["old"]["cfg"] == res["new"]["cfg"], "D: 0.2.23 starts the live copy to exactly the config.properties 0.2.22 writes")
            fo = sorted(f for f in os.listdir(os.path.join(SCRATCH, "live-old")) if not f.startswith("config-history"))
            fn_ = sorted(f for f in os.listdir(os.path.join(SCRATCH, "live-new")) if not f.startswith("config-history"))
            check(fo == fn_, "D: the same files after the starts: %s / %s" % (fo, fn_))
        outa = os.path.join(SCRATCH, "audit.json")
        pa = child(env, "--audit", "--out", outa)
        check(pa.returncode == 0 and os.path.isfile(outa), "AA: the engine-access audit child ran")
        if os.path.isfile(outa):
            a = json.load(open(outa))
            check(not a["refused"] and a["refs"] > 10000, "AA: engine-access audit: %d references in %d classes, refused %s" % (a["refs"], a["classes"], a["refused"][:5]))
            check(len(a["control"]) == 1 and "sendUpdate" in a["control"][0], "AA: the control is refused: %s" % a["control"])
            print("AA. engine-access audit: %d references in %d classes, 0 refused, control refused" % (a["refs"], a["classes"]))
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyGear %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
