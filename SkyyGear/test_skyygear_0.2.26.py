"""Harness for SkyyGear 0.2.26 (THE ONE ANVIL TAB; tools/gear_0_2_26_patch.py header). Build first:
    python tools/gear_0_2_26_patch.py && python SkyyGear/build_skyygear_0.2.26.py

    python SkyyGear/test_skyygear_0.2.26.py [--jar <SkyyGear-0.2.26.jar>] [--old <SkyyGear-0.2.25.jar>] [--j24 <SkyyGear-0.2.24.jar>]
                                            [--armory <SkyyArmory-0.1.23.jar>] [--mt <Multitools-1.2.9.jar>] [--root <scratch root>] [--keep]

The 0.2.11 harness's helpers (verify A, the bare-server boot, the engine-access audit AA, FakeStore / FakeUtil / FakeIdPage) and the
0.2.22 stand-ins (MergeFail, FakeReforgePage, FakeMultiPage, FakePR) are loaded from their files; this harness adds FakePM (a PageManager
that records the page a command opens) and the contract stand-ins it needs (coins, acc:fn:has, wardrobe:fn:list / fetch / depositSlot).
SkyyArmory 0.1.23 (the SET pin, repo jar) and Multitools 1.2.9 (UserData/Mods, read-only) are COPIED into scratch and loaded as their own
packs - the Soul Cage upgrade costs are SkyyArmory's REAL recipes.
  S   non-class entries 0.2.25 -> 0.2.26: only the manifest changed; class added = GearAnvil (no new page class)
  A   every class loads + verifies (-Xverify:all)
  C   CLASS COMPARE 0.2.25 -> 0.2.26: exactly the listed members differ (javassist members + resolved bytecode)
  N   THE ANVIL EXECUTED (one booted engine): config rows + checkIdTools; the tab row (on / off); GearAnvil.rows == the union of the
      Reforge / Upgrade / Identify lists; rowSub / names; the page with an item of every kind on it (cards, have / need, the layout
      budget of every column + card, unique ids without underscores, no ItemGridSlot); REFORGE + LEVEL UP (exact coins, Before / After);
      UPGRADE (exact materials, rarity + lines kept, the Made state, a 2nd click does nothing, the next tier); IDENTIFY (gear + bag, exact
      coins, the item stays on the anvil, Revealed); RE-IDENTIFY (two clicks); IDENTIFY ALL; THE APPRAISAL TOOL RULE (off / no
      SkyyAccessories / no tool / tool II / identify.command off); guards (busy, epoch, double click); FAILURES AT EVERY STEP (reforge /
      identify write refused -> refund; upgrade: materials refused, the new item refused, a CRASH right after the materials left, the
      bookkeeping throwing, coins unavailable) - never a copy; the Requip rows (list, fetch, Return to Requip); every click (tabs, back,
      paging, bad events); /reforge, /upgrade, /identify EXECUTED through FakePM (on and off); part.anvil off = the 0.2.25 pages;
      ui.frames off (paged list, the kit's well cards); the empty anvil; an item that moved
  X   THE 0.2.25 HARNESS'S RANDOMISED OLD-VS-NEW STATS COMPARISON (test_skyygear_0.2.25.py --phase exec) with this jar against 0.2.24: the
      lag-fix snapshot numbers are unchanged (its one config-text check is expected to see the 3 new rows - checked exactly in D)
  D   START TWICE on a scratch COPY of the live Skyy_SkyyGear folder with each jar: the 2nd start changes nothing; 0.2.26 writes the same
      config.properties as 0.2.25 (absent rows = defaults, no one-time update); the fresh default file differs only by the Anvil block
  AA  THE ENGINE-ACCESS AUDIT
Scratch: tools/dev/scratch/gear0226/harness (or --root) (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B

VERSION = "0.2.26"
OLD_VERSION = "0.2.25"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCR_ROOT = os.path.abspath(arg("--root", os.path.join(TOOLS, "dev", "scratch", "gear0226")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyGear-%s.jar" % OLD_VERSION)))      # read only
J24 = os.path.abspath(arg("--j24", os.path.join(HERE, "SkyyGear-0.2.24.jar")))                   # read only (X)
AR_SRC = os.path.abspath(arg("--armory", os.path.join(ROOT, "SkyyArmory", "SkyyArmory-0.1.23.jar")))   # read only - copied
MT_SRC = os.path.abspath(arg("--mt", os.path.join(B.MODS_DIR, "Multitools-1.2.9.jar")))           # read only - copied
AR_JAR = os.path.join(SCRATCH, "packs", "SkyyArmory-0.1.23.jar")
MT_JAR = os.path.join(SCRATCH, "packs", "Multitools-1.2.9.jar")
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyGear")
PKG = "com.skyy.gear."
SOUL = ["Weapon_Wand_SoulOrb"] + ["Weapon_Wand_SoulCage_%s" % m for m in ("Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")]
NEW_CLASSES = {"GearAnvil"}
T1, T2, T3 = "Skyy_Accessory_Appraisal_T1", "Skyy_Accessory_Appraisal_T2", "Skyy_Accessory_Appraisal_T3"

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


def soul_recipes():
    """the 7 cage steps of the SkyyArmory jar: [(from, to, {material: qty})]"""
    out = []
    with zipfile.ZipFile(AR_SRC) as z:
        js = {}
        for n in z.namelist():
            b = os.path.basename(n)[:-5]
            if n.startswith("Server/Item/Items/") and n.endswith(".json") and b in SOUL:
                js[b] = json.loads(z.read(n).decode("utf-8-sig"))["Recipe"]
    for i in range(1, len(SOUL)):
        inp = js[SOUL[i]]["Input"]
        out.append((SOUL[i - 1], SOUL[i], dict((x["ItemId"], int(x["Quantity"])) for x in inp if x["ItemId"] != SOUL[i - 1])))
    return out


# ====================================================================================================== S: non-class entries
def run_assets():
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    ea = dict((n, zo.read(n)) for n in zo.namelist() if not n.endswith(".class"))
    eb = dict((n, zn.read(n)) for n in zn.namelist() if not n.endswith(".class"))
    added = sorted(set(eb) - set(ea))
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n])
    check(not added and not (set(ea) - set(eb)) and changed == ["manifest.json"] and b'"0.2.26"' in eb["manifest.json"]
          and b"Anvil (pick an item: Reforge, Level up, Upgrade or Identify it in one panel" in eb["manifest.json"],
          "S: 0.2.25 -> 0.2.26: no file added / removed, only the manifest changed (version + the Anvil words): + %s ~ %s" % (added[:3], changed[:3]))
    ca = set(n for n in zo.namelist() if n.endswith(".class"))
    cb = set(n for n in zn.namelist() if n.endswith(".class"))
    check(not (ca - cb) and set(n.split("/")[-1][:-6] for n in cb - ca) == NEW_CLASSES,
          "S: class added = GearAnvil (no new page class); none removed: + %s - %s" % (sorted(cb - ca), sorted(ca - cb)))
    names = set(zn.namelist())
    check(not [n for n in names if "SoulCage" in n or "inkblindcat" in n.lower() or "Skyy_Accessory" in n or n.endswith(".ui")],
          "S: no pack mod / SkyyAccessories file is shipped or overridden (runtime ids only), no .ui file")


# ====================================================================================================== F+: this round's stand-ins
def run_mkfake4(out_dir):
    H22["run_mkfake2"](out_dir)
    from jpype import JClass
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(JAR)
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    PMc = "com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager"
    pm = cp.makeClass(FAKE_PKG + ".FakePM")
    pm.setSuperclass(cp.get(PMc))
    pm.addField(CtField.make("public static java.lang.Object last;", pm))
    pm.addField(CtField.make("public static int opens;", pm))
    pm.addConstructor(CtNewConstructor.make("public FakePM() { super(); }", pm))
    pm.addMethod(CtNewMethod.make("public void openCustomPage(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.Store s, "
                                  "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage p) { last = p; opens = opens + 1; }", pm))
    pm.writeFile(out_dir)
    print("F+. FakePM written")


# ====================================================================================================== N: the Anvil (one booted engine)
def run_anvil(out):
    from jpype import JClass, JInt, JShort, JLong, JByte, JImplements, JOverride, JObject, JArray, JString
    K = Child(out)
    _jvm([B.SERVER_JAR, B.JAVASSIST, JAR, FAKE_DIR], verify=True, big=True)
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
    souls = [ITEM.getAssetMap().getAsset(i) for i in SOUL]
    n_gen = gen_recipes(souls)
    K.check(all(x is not None for x in souls) and n_gen >= 8, "E: SkyyArmory 0.1.23 (scratch copy) loaded as its own pack: the Soul Orb + 7 cages "
            "are real items, %d recipes generated (failed stores %s)" % (n_gen, afail))
    have_mt = os.path.isfile(MT_JAR)
    if have_mt:
        addpack(MT_JAR, "IBC:Multitools")
        gen_recipes([ITEM.getAssetMap().getAsset("Tool_Hatchet_Pickaxe_Multitool_" + t) for t in ("Crude", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")])
    P = lambda n: JClass(PKG + n)
    Cfg, Gear, Up, Merge, Data, Roll, Forge, Stamp, Lvl, Defs, Log, View, Unid, Ui, Ident, Anv = (
        P("GearCfg"), P("Gear"), P("GearUp"), P("GearMerge"), P("GearData"), P("GearRoll"), P("GearForge"), P("GearStamp"), P("GearLevel"),
        P("GearDefs"), P("GearLog"), P("GearView"), P("GearUnid"), P("GearUi"), P("GearIdent"), P("GearAnvil"))
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
    # ============================================================================ N1: the rows
    K.check(bool(Cfg.ANVIL_ON) and not bool(Cfg.ID_TOOL) and str(Cfg.ID_TOOLS) == ",".join((T1, T2, T3)) and "part.anvil=true" in FRESH
            and "anvil.appraisal=false" in FRESH and ("anvil.appraisalIds=" + ",".join((T1, T2, T3))) in FRESH,
            "N1: the fresh config: part.anvil=true, anvil.appraisal=false, anvil.appraisalIds=T1,T2,T3")
    CRows, CFn = JClass(PKG + "CfgRows"), JClass(PKG + "CfgFn")
    ia_, ip_ = int(CRows.index("anvil.appraisal")), int(CRows.index("part.anvil"))
    q_on, q_off = CFn.needConfirm(ia_, "false", "true", None), CFn.needConfirm(ia_, "true", "false", None)
    K.check(ia_ >= 0 and bool(CRows.flag(ia_, "danger")) and q_on is not None and q_off is None and "nobody can identify" in str(q_on)
            and bool(CRows.flag(ip_, "danger")) and CFn.needConfirm(ip_, "true", "false", None) is not None,
            "N1 (fix round): anvil.appraisal is a danger row - switching it ON asks first and the question says nobody can identify; OFF does not ask: %s" % str(q_on)[:140])
    ck = [Cfg.checkIdTools("k", v) for v in ("A_b,C1", " A , B ,", "bad id", "a-b", ",".join("X%d" % i for i in range(9)), None)]
    K.check(ck[0] is None and ck[1] is None and "not an item id" in str(ck[2]) and "not an item id" in str(ck[3]) and "At most 8" in str(ck[4]) and ck[5] is None,
            "N1: checkIdTools: ids of letters / digits / _ pass, a space / dash refused, at most 8: %s" % [str(x) for x in ck])
    apply(anvil__appraisalIds=" %s , ,%s " % (T1, T2))
    K.check([str(x) for x in Anv.tools()] == [T1, T2], "N1: GearAnvil.tools() trims and skips empty parts")
    apply()
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    BD = JClass("org.bson.BsonDocument")
    BS = JClass("org.bson.BsonString")
    UUID = JClass("java.util.UUID")
    U1 = UUID.fromString("00000000-0000-0000-0000-0000000000a1")
    Long_, Bool_ = JClass("java.lang.Long"), JClass("java.lang.Boolean")
    XP = []

    @JImplements("java.util.function.Function")
    class AddXp(object):
        @JOverride
        def apply(self, o):
            XP.append(str(o[1]))
            return JObject(True, Bool_)
    COINS = [10 ** 7]

    @JImplements("java.util.function.Function")
    class CoinGet(object):
        @JOverride
        def apply(self, o):
            return JObject(JLong(COINS[0]), Long_)

    @JImplements("java.util.function.Function")
    class CoinTake(object):
        @JOverride
        def apply(self, o):
            n_ = int(o[1])
            if n_ > COINS[0]:
                return JObject(False, Bool_)
            COINS[0] -= n_
            return JObject(True, Bool_)

    @JImplements("java.util.function.Function")
    class CoinAdd(object):
        @JOverride
        def apply(self, o):
            COINS[0] += int(o[1])
            return JObject(JLong(COINS[0]), Long_)
    ACC = set()
    ACC_CALLS = []

    @JImplements("java.util.function.Function")
    class AccHas(object):
        @JOverride
        def apply(self, o):
            ACC_CALLS.append(str(o[1]))
            return JObject(str(o[1]) in ACC, Bool_)
    br = Gear.bridge()
    br.put("skill:fn:addxp", AddXp())

    def coins_on():
        br.put("coins:fn:get", CoinGet())
        br.put("coins:fn:take", CoinTake())
        br.put("coins:fn:add", CoinAdd())

    def coins_off():
        for k_ in ("coins:fn:get", "coins:fn:take", "coins:fn:add"):
            br.remove(k_)
    coins_on()

    def stack(iid, q=1):
        return IS(iid, JInt(q))

    def rolled(iid, r, lvl=None, ident=True):
        L_ = int(Roll.craftLevel(iid, U1)) if lvl is None else lvl
        return Roll.newDoc(iid, JInt(r), ident, "craft" if ident else "drop", JInt(L_))

    def gear(iid, d, q=1):
        s_ = stack(iid, q)
        return s_ if d is None else Data.put(s_, d, None)

    def doc(s_):
        return Data.effective(s_.getItemId(), s_.getMetadata())

    def stats_of(d):
        return sorted(str(m.asDocument().getString("s").getValue()) for m in Data.mods(d))

    def mkbag(lo=5, hi=9, r=2):
        return Unid.make(JInt(0), JInt(0), JInt(r), JInt(lo), JInt(hi), "test", "test", JInt(1))

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

    GLF = os.path.join(SCRATCH, "gear.log")

    def logs():
        Log.flush()
        out_ = []
        if os.path.isfile(GLF):
            with open(GLF, encoding="utf-8") as f_:
                out_ = [l_ for l_ in f_.read().split("\n") if l_.strip()]
            os.remove(GLF)
        return out_ + [l_ for l_ in str(Log.take()).split("\n") if l_.strip()]
    Log.FILE = JClass("java.nio.file.Paths").get(GLF)
    logs()
    steps = soul_recipes()

    # ---- the page world (the 0.2.22 shape) + a page manager that records the page a command opens
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    try:
        FPR = JClass(FAKE_PKG + ".FakePR")
        prx = us.allocateInstance(FPR.class_)
    except Exception:
        FPR = None
        prx = us.allocateInstance(PR.class_)
    jf(PR, "uuid").set(prx, U1)
    jf(PR, "username").set(prx, "Tester")
    FRP = JClass(FAKE_PKG + ".FakeReforgePage")
    FPM = JClass(FAKE_PKG + ".FakePM")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    for cn in ("com.hypixel.hytale.server.core.modules.entity.EntityModule", "com.hypixel.hytale.server.core.modules.entity.damage.DamageModule",
               "com.hypixel.hytale.server.core.modules.block.BlockModule", "com.hypixel.hytale.server.core.universe.Universe"):
        JClass(FAKE_PKG + ".FakeUtil").single(cn)
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    PMC = JClass("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager")
    REFc = JClass("com.hypixel.hytale.component.Ref")
    FS = JClass(FAKE_PKG + ".FakeStore")
    IHM = JClass("java.util.IdentityHashMap")
    pm_field = None
    k_ = PLA.class_
    while k_ is not None and pm_field is None:
        for f_ in k_.getDeclaredFields():
            if f_.getType() == PMC.class_:
                f_.setAccessible(True)
                pm_field = f_
        k_ = k_.getSuperclass()

    def world(inv_):
        pl = us.allocateInstance(PLA.class_)
        jf(PLA, "inventory").set(pl, inv_)
        if pm_field is not None:
            pm_field.set(pl, us.allocateInstance(FPM.class_))
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

    TOPS = ("#SkyyGBody", "#SkyyGAnvil", "#SkyyGListBox", "#SkyyGCardR", "#SkyyGCardU", "#SkyyGCardI")
    LEFTS = ("#SkyyGMain", "#SkyyGActs", "#SkyyGRe", "#SkyyGIdAll", "#SkyyGIGo")

    def layout(cl):
        """sum of the top elements' Anchor heights per Top-layout parent, widths per Left-layout parent; every declared #id"""
        hs, ws, ids = {}, {}, []
        for v in cl:
            sel_ = v["selector"]
            dat = v["text"] if v["text"] and "{" in v["text"] else (v["data"] or "")
            if "{" not in dat:
                continue
            ids += re.findall(r"#([A-Za-z0-9_]+)\s*\{", dat)
            m_ = re.match(r"^\s*\w+[^{]*\{\s*Anchor: \(([^)]*)\)", dat)
            if not m_:
                continue
            h_ = re.search(r"Height: (\d+)", m_.group(1))
            w_ = re.search(r"Width: (\d+)", m_.group(1))
            hs[sel_] = hs.get(sel_, 0) + (int(h_.group(1)) if h_ else 0)
            mf_ = re.match(r"^\s*Group #SkyyGList \{ Anchor: \(Height: (\d+)\); LayoutMode: Top;", dat)      # fix round: a fixed list
            if mf_:
                hs["decl#SkyyGList"] = int(mf_.group(1))
            ws[sel_] = ws.get(sel_, 0) + (int(w_.group(1)) if w_ else 0)
        return hs, ws, ids

    def render(pg_, ref_, st_):
        ub_, ue_ = UCB(), UEB()
        pg_.build(ref_, ub_, ue_, st_)
        cl = cmds(ub_)
        txt = chr(10).join("%s|%s|%s" % (v["selector"], v["data"], v["text"]) for v in cl) + chr(10) + evtext(ue_)
        TXT_ALL.append(txt)          # fix round: every rendered page (the card-line length check)
        return txt, layout(cl)

    LAYOUT_BAD = []
    TXT_ALL = []

    def budget(name, lay, card_in=202):
        hs, ws, ids = lay
        bad = []
        lim = {"#SkyyGBody": 808, "#SkyyGAnvil": 656, "#SkyyGListBox": 656, "#SkyyGCardR": card_in, "#SkyyGCardU": card_in, "#SkyyGCardI": card_in}
        for k2, v2 in lim.items():
            if hs.get(k2, 0) > v2:
                bad.append("%s height %d > %d" % (k2, hs[k2], v2))
        if "decl#SkyyGList" in hs and hs.get("#SkyyGList", 0) > hs["decl#SkyyGList"]:          # fix round: rows + Requip block fit the fixed list
            bad.append("#SkyyGList content %d > its fixed height %d" % (hs["#SkyyGList"], hs["decl#SkyyGList"]))
        wl = {"#SkyyGMain": 1066, "#SkyyGActs": 562, "#SkyyGRe": 562, "#SkyyGIdAll": 470, "#SkyyGIGo": 538}
        for k2, v2 in wl.items():
            if ws.get(k2, 0) > v2:
                bad.append("%s width %d > %d" % (k2, ws[k2], v2))
        dup = sorted(set(x for x in ids if ids.count(x) > 1))
        und = sorted(set(x for x in ids if "_" in x))
        if dup:
            bad.append("duplicate ids %s" % dup[:5])
        if und:
            bad.append("ids with _ %s" % und[:5])
        if bad:
            LAYOUT_BAD.append((name, bad))
        return hs

    # ============================================================================ N2: the tab row
    inv0, cs0 = mkinv()
    ref0, st0 = world(inv0)
    pg0 = FRP(prx)
    t_on, _l = render(pg0, ref0, st0)
    apply(part__anvil="false")
    pgo = FRP(prx)
    t_off, _l = render(pgo, ref0, st0)
    apply()
    K.check("#SkyyGTab0" in t_on and "Anvil" in t_on and "#SkyyGTab1" not in t_on and ("#SkyyGTab2" in t_on) == have_mt and "#SkyyGTab3" in t_on
            and "#SkyyGTab1" in t_off and "Text: \"Reforge\"" in t_off and "Text: \"Upgrade\"" in t_off and "#SkyyGCardR" not in t_off,
            "N2: the tab row: Craft | Anvil%s (no Upgrade tab) with part.anvil on; Craft | Reforge | Upgrade%s with it off (the 0.2.25 page)"
            % (" | Multitool" if have_mt else "", " | Multitool" if have_mt else ""))
    K.check("The anvil is empty" in t_on and "Tip: hold an item when you type /reforge, /upgrade or /identify." in t_on
            and "Untiered: never reforged" in t_on and "Normal: " in t_on and "Identify: open to everyone" in t_on
            and "Turns an item into its next tier" in t_on and "Reveals unidentified gear" in t_on,
            "N2: the empty anvil explains Reforge (cost by rarity), Upgrade, Identify and the tip")
    budget("empty", render(pg0, ref0, st0)[1])

    # ============================================================================ N3: an item of every kind
    fr_, to_, mats = steps[1]          # Copper cage -> Iron cage
    bar, ess = list(mats)
    SW = "Weapon_Sword_Iron"
    UNID = "Weapon_Sword_Copper"
    inv, cs = mkinv()
    cage_d = rolled(fr_, 2)
    cs["hotbar"].setItemStackForSlot(JShort(0), gear(fr_, cage_d))
    cs["hotbar"].setItemStackForSlot(JShort(1), gear(SW, rolled(SW, 1)))
    cs["hotbar"].setItemStackForSlot(JShort(2), gear(UNID, rolled(UNID, 2, ident=False)))
    cs["hotbar"].setItemStackForSlot(JShort(3), mkbag())
    cs["storage"].setItemStackForSlot(JShort(0), stack(bar, mats[bar] * 2))
    cs["storage"].setItemStackForSlot(JShort(1), stack(ess, mats[ess] * 2))
    cs["storage"].setItemStackForSlot(JShort(5), stack("Ingredient_Stick", 3))
    cs["backpack"].setItemStackForSlot(JShort(0), stack(SOUL[0]))
    rows = [tuple(x) for x in Anv.rows(inv)]
    union = set(tuple(x) for x in Forge.rows(inv)) | set(tuple(x) for x in Up.rows(inv)) | set(tuple(x) for x in Ident.rows(inv))
    K.check(set(rows) == union == {(0, 0), (0, 1), (0, 2), (0, 3), (2, 0)} and len(rows) == len(set(rows)),
            "N3: GearAnvil.rows = the union of the Reforge, Upgrade and Identify lists (cage, sword, unidentified sword, bag, plain Orb), each "
            "once, never the materials / a stick: %s" % rows)
    subs = dict((r_, str(Anv.rowSub(at(cs, ("hotbar", "storage", "backpack")[r_[0]], r_[1])))) for r_ in rows)
    K.check(subs[(0, 2)] == "Unidentified" and subs[(0, 3)].startswith("Rare - Lv 5-9") and subs[(2, 0)].startswith("Normal - Lv ")
            and subs[(0, 0)].startswith("Rare - Lv ") and subs[(0, 1)].startswith("Unique - Lv "),
            "N3: the row sub texts: %s" % subs)
    K.check(not bool(Anv.fits(None)) and not bool(Anv.fits(stack("Ingredient_Stick"))) and bool(Anv.fits(stack(SOUL[0])))
            and bool(Anv.unid(at(cs, "hotbar", 3), None)) and not bool(Anv.unid(at(cs, "hotbar", 1), doc(at(cs, "hotbar", 1)))),
            "N3: fits / unid")
    ref, st = world(inv)
    pg = FRP(prx)
    pg.preselect(inv)
    s0, l0 = render(pg, ref, st)
    h0 = budget("cage", l0)
    K.check(int(pg.selSec) == 0 and int(pg.selSlot) == 0 and "#SkyyGCardR" in s0 and "#SkyyGCardU" in s0 and "#SkyyGCardI" not in s0
            and "Your gear (5)" in s0 and "Identify all 2" in s0 and "Next: " in s0 and ("%d / %d" % (mats[bar] * 2, mats[bar])) in s0
            and "#SkyyGBtnForge" in s0 and "#SkyyGBtnLevel" in s0 and "#SkyyGBtnUp" in s0 and "Current modifiers" in s0
            and "(on the anvil)" in s0 and "ItemGridSlot" not in s0 and "ContainerPanelPatch" in s0 and "Common/Buttons/Primary.png" in s0,
            "N3: /reforge with the cage held: the Anvil shows BOTH cards (Reforge + Upgrade with its have / need), 'Your gear (5)', "
            "'Identify all 2' above the list; kit panels; no ItemGridSlot")
    K.check(h0.get("#SkyyGAnvil", 0) == 656 and h0.get("#SkyyGBody", 0) <= 808 and h0.get("#SkyyGCardR", 0) <= 202 and h0.get("#SkyyGCardU", 0) <= 202,
            "N3: 1080p budget: right column %d of 656, body %d of 808, Reforge card %d / Upgrade card %d of 202"
            % (h0.get("#SkyyGAnvil", 0), h0.get("#SkyyGBody", 0), h0.get("#SkyyGCardR", 0), h0.get("#SkyyGCardU", 0)))
    K.notes.append("layout (cage): %s" % dict((k2, h0.get(k2)) for k2 in TOPS))

    # ============================================================================ N4: REFORGE + LEVEL UP on the Anvil
    def click(pg_, ref_, st_, a_):
        pg_.lastForge = JLong(0)
        pg_.handleDataEvent(ref_, st_, '{"a":"%s"}' % a_)
    d0 = doc(at(cs, "hotbar", 0))
    r0, lv0 = int(Data.rarity(d0)), int(Lvl.level(fr_, d0))
    cost = int(Cfg.costReforge(JInt(r0), JInt(lv0)))
    c0, fp0 = COINS[0], str(Forge.fp(at(cs, "hotbar", 0)))
    rb0 = int(pg.rebuilds)
    click(pg, ref, st, "forge")
    s1, l1 = render(pg, ref, st)
    budget("reforged", l1)
    d1 = doc(at(cs, "hotbar", 0))
    K.check(str(pg.info).startswith("+Reforged!") and COINS[0] == c0 - cost and str(Forge.fp(at(cs, "hotbar", 0))) != fp0 and int(Data.rarity(d1)) == r0
            and "Before" in s1 and "After" in s1 and int(pg.rebuilds) == rb0 + 1 and str(at(cs, "hotbar", 0).getItemId()) == fr_,
            "N4: Reforge on the Anvil: -%d coins exactly, a new roll, the same rarity, Before + After, one rebuild: '%s'" % (cost, str(pg.info)[:60]))
    lg = logs()
    K.check(any("TAKE" in l_ and str(cost) in l_ for l_ in lg) or any("reforge" in l_.lower() for l_ in lg), "N4: gear.log has the reforge: %s" % lg[-2:])
    li = Forge.lvlInfo(U1, fr_, d1)
    c1, lv1 = COINS[0], int(Lvl.level(fr_, d1))
    click(pg, ref, st, "lvl")
    d2 = doc(at(cs, "hotbar", 0))
    if int(li[0]) == 0:
        lc = int(Cfg.costLevelUp(JInt(r0), li[2]))
        K.check(str(pg.info).startswith("+Levelled up!") and int(Lvl.level(fr_, d2)) == int(li[2]) and COINS[0] == c1 - lc,
                "N4: Level up on the Anvil: Lv %d -> %d, -%d coins exactly" % (lv1, int(li[2]), lc))
    else:
        K.check(str(pg.info).startswith("-") and int(Lvl.level(fr_, d2)) == lv1 and COINS[0] == c1, "N4: Level up refused (%s) - nothing changed" % str(li[5]))
    logs()

    # ============================================================================ N5: UPGRADE on the Anvil (materials, rarity + lines kept)
    sel_fp = str(Forge.fp(at(cs, "hotbar", 0)))
    pg.anPick(inv, JInt(0), JInt(0))
    dpre = doc(at(cs, "hotbar", 0))
    b_p = cnt(inv, [fr_, to_, bar, ess])
    c2 = COINS[0]
    click(pg, ref, st, "up")
    s2, l2 = render(pg, ref, st)
    budget("upgraded", l2)
    dup_ = doc(at(cs, "hotbar", 0))
    K.check(str(pg.info).startswith("+Upgraded to a ") and str(at(cs, "hotbar", 0).getItemId()) == to_ and COINS[0] == c2
            and cnt(inv, [fr_, to_, bar, ess]) == {fr_: b_p[fr_] - 1, to_: b_p[to_] + 1, bar: b_p[bar] - mats[bar], ess: b_p[ess] - mats[ess]}
            and int(Data.rarity(dup_)) == int(Data.rarity(dpre)) and stats_of(dup_) == stats_of(dpre)
            and "Upgraded - its lines" in s2 and "Materials: used up" in s2 and "Text: \"Upgraded\"" in s2 and "#SkyyGCardR" in s2,
            "N5: Upgrade on the Anvil: Copper -> Iron cage in the same slot, exactly the recipe's materials (%s), no coins, the SAME rarity "
            "and lines, the Made state; the Reforge card stays for the new item: '%s'" % (mats, str(pg.info)[:70]))
    lg = logs()
    K.check(any(l_.startswith("UPGRADE-BEGIN") or " UPGRADE-BEGIN " in l_ for l_ in lg) and any("UPGRADE " in l_ for l_ in lg), "N5: gear.log UPGRADE-BEGIN + UPGRADE")
    _f2, _t2, mats2 = steps[2]
    for j_, (m_, q_) in enumerate(mats2.items()):
        cs["storage"].setItemStackForSlot(JShort(20 + j_), stack(m_, q_ * 3))
    b_2 = cnt(inv, [to_, _t2] + list(mats2))
    for _k in range(2):
        click(pg, ref, st, "up")
    K.check(str(at(cs, "hotbar", 0).getItemId()) == to_ and cnt(inv, [to_, _t2] + list(mats2)) == b_2 and "Already upgraded" in str(pg.info),
            "N5: two more Upgrade clicks on the Made state (the next step's materials there) change nothing: '%s'" % str(pg.info))
    # the Made item can be reforged straight away (the Reforge card works on the new item)
    c3 = COINS[0]
    click(pg, ref, st, "forge")
    s3, _l = render(pg, ref, st)
    K.check(str(pg.info).startswith("+Reforged!") and COINS[0] < c3 and pg.upMade is None and "Before" in s3,
            "N5: the upgraded item is reforged from the same panel (the Made state ends, Before / After shown)")
    # click it in the list -> its next tier with the materials there
    pg.handleDataEvent(ref, st, '{"a":"sel:%d"}' % [tuple(x) for x in pg.rows].index((0, 0)))
    s4, _l = render(pg, ref, st)
    K.check("Next: " + str(Gear.itemName(_t2)) in s4 and "Cannot upgrade" not in s4, "N5: the list click shows the next step (%s)" % _t2)
    for j_ in range(len(mats2)):
        cs["storage"].removeItemStackFromSlot(JShort(20 + j_))
    s5, _l = render(pg, ref, st)
    K.check("You need " in s5 and "Cannot upgrade" in s5, "N5: short materials -> 'You need ...', 'Cannot upgrade'")
    b_5 = cnt(inv, [to_, _t2])
    click(pg, ref, st, "up")
    K.check(cnt(inv, [to_, _t2]) == b_5 and str(pg.info).startswith("-You need"), "N5: an Upgrade click without the materials changes nothing")
    # a sword has no next tier: the Upgrade card says why, the Reforge card works
    pg.handleDataEvent(ref, st, '{"a":"sel:%d"}' % [tuple(x) for x in pg.rows].index((0, 1)))
    s6, l6 = render(pg, ref, st)
    budget("sword", l6)
    K.check("No next tier" in s6 and "Cannot upgrade" in s6 and "#SkyyGBtnForge" in s6 and "Text: \"Reforge\"" in s6, "N5: a sword: 'No next tier', Reforge on")
    b_6 = cnt(inv, [SW])
    fp6 = str(Forge.fp(at(cs, "hotbar", 1)))
    click(pg, ref, st, "up")
    K.check(cnt(inv, [SW]) == b_6 and str(Forge.fp(at(cs, "hotbar", 1))) == fp6, "N5: an Upgrade click on a sword changes nothing ('%s')" % str(pg.info))
    # the plain Orb: rolls a rarity; part.upgrade off
    pg.handleDataEvent(ref, st, '{"a":"sel:%d"}' % [tuple(x) for x in pg.rows].index((2, 0)))
    s7, _l = render(pg, ref, st)
    apply(part__upgrade="false")
    s8, _l = render(pg, ref, st)
    click(pg, ref, st, "up")
    up_off = str(pg.info)
    apply()
    K.check(("Plain: rolls a rarity." in s7 or "You need " in s7) and "Upgrading is switched off" in s8 and "switched off" in up_off,
            "N5: a plain Orb 'rolls a rarity'; part.upgrade off: the card says so and a click is refused: %s" % ([
            "Plain: rolls a rarity." in s7, "Upgrading is switched off" in s8, up_off] + [l_ for l_ in s7.split(chr(10)) if "SkyyGU" in l_][:6]))
    _cl = [l_.split("|", 1)[1] for s_ in TXT_ALL for l_ in s_.split(chr(10)) if l_.startswith("#SkyyGUNext.Text|") or l_.startswith("#SkyyGRLvl.Text|")]
    _bsrc = open(os.path.join(HERE, "build_skyygear_0.2.26.py"), encoding="utf8").read()
    K.check(any("Next: " in x for x in _cl) and '"Level up to Lv " + lnext + ": "' in _bsrc and '" (max Lv "' not in _bsrc and all("max Lv" not in x for x in _cl)
            and not any(("(%s," % str(n_)) in x for x in _cl for n_ in Defs.R_NAME) and "rolls a rarity)" not in chr(10).join(_cl),
            "N5 (fix round): the Upgrade 'Next' / Level up card lines are short (no '(Rarity, Lv', 'max Lv', '(rolls a rarity'): %s" % sorted(set(_cl))[:6])

    # ============================================================================ N6: IDENTIFY gear + a bag, RE-IDENTIFY, the Revealed lines
    pg.handleDataEvent(ref, st, '{"a":"sel:%d"}' % [tuple(x) for x in pg.rows].index((0, 2)))
    s9, l9 = render(pg, ref, st)
    budget("unid", l9)
    du = doc(at(cs, "hotbar", 2))
    icost = int(Ident.costOf(at(cs, "hotbar", 2)))
    K.check("#SkyyGCardI" in s9 and "#SkyyGCardR" not in s9 and "#SkyyGCardU" not in s9 and ("Cost: %s coins" % str(Gear.fmt(JLong(icost)))) in s9
            and "Unidentified" in s9 and "Identify: open to everyone" in s9 and "#SkyyGBtnId" in s9 and l9[0].get("#SkyyGCardI", 0) <= 202,
            "N6: an unidentified sword: ONE Identify card (cost %d, the open rule), no Reforge / Upgrade card" % icost)
    c9 = COINS[0]
    click(pg, ref, st, "forge")
    K.check(COINS[0] == c9 and not bool(Data.identified(doc(at(cs, "hotbar", 2)))), "N6: a stale Reforge click on an unidentified item is refused, nothing moves")
    click(pg, ref, st, "id")
    s10, l10 = render(pg, ref, st)
    budget("identified", l10)
    di = doc(at(cs, "hotbar", 2))
    K.check(str(pg.info).startswith("+Identified your ") and COINS[0] == c9 - icost and bool(Data.identified(di)) and int(Data.rarity(di)) == int(Data.rarity(du))
            and int(pg.selSec) == 0 and int(pg.selSlot) == 2 and "Revealed" in s10 and "#SkyyGCardR" in s10 and "#SkyyGCardU" in s10,
            "N6: Identify on the Anvil: -%d coins exactly, the rarity kept, the item stays on the anvil with its Revealed lines and now "
            "shows Reforge + Upgrade: '%s'" % (icost, str(pg.info)[:70]))
    logs()
    pg.handleDataEvent(ref, st, '{"a":"sel:%d"}' % [tuple(x) for x in pg.rows].index((0, 3)))
    s11, l11 = render(pg, ref, st)
    budget("bag", l11)
    bcost = int(Ident.costOf(at(cs, "hotbar", 3)))
    K.check("#SkyyGCardI" in s11 and "Mystery bag" in s11 and "Which item is inside is picked the moment you pay." in s11, "N6: a bag: the Identify card + the bag text")
    c11 = COINS[0]
    click(pg, ref, st, "id")
    got = at(cs, "hotbar", 3)
    s12, l12 = render(pg, ref, st)
    budget("bag opened", l12)
    K.check(str(pg.info).startswith("+It was ") and COINS[0] == c11 - bcost and got is not None and not bool(Unid.isBox(got.getItemId()))
            and str(pg.selId) == str(got.getItemId()) and bool(Unid.rerollable(got)) and "#SkyyGRe" in s12 and "Text: \"Re-identify\"" in s12
            and l12[0].get("#SkyyGAnvil", 0) == 656,
            "N6: the bag becomes its item in the same slot (-%d coins), it stays on the anvil with the RE-IDENTIFY strip; column %d of 656"
            % (bcost, l12[0].get("#SkyyGAnvil", 0)))
    fpb = str(Forge.fp(got))
    c12 = COINS[0]
    click(pg, ref, st, "rr")
    s13, _l = render(pg, ref, st)
    armed = "Confirm re-identify" in s13 and COINS[0] == c12 and str(Forge.fp(at(cs, "hotbar", 3))) == fpb
    rrc = int(Unid.rerollCostOf(Unid.rerollDoc(at(cs, "hotbar", 3))))
    click(pg, ref, st, "rr")
    K.check(armed and str(pg.info).startswith("+It is now ") and COINS[0] == c12 - rrc and str(Forge.fp(at(cs, "hotbar", 3))) != fpb,
            "N6: Re-identify: the 1st click arms ('Confirm re-identify', nothing paid), the 2nd re-rolls it (-%d coins)" % rrc)
    logs()

    # ============================================================================ N7: IDENTIFY ALL + the Revealed list
    invA, csA = mkinv()
    for i_ in range(3):
        csA["storage"].setItemStackForSlot(JShort(i_), gear(UNID, rolled(UNID, 1, ident=False)))
    csA["hotbar"].setItemStackForSlot(JShort(4), mkbag(3, 3, 0))
    refA, stA = world(invA)
    pgA = FRP(prx)
    sA0, _l = render(pgA, refA, stA)
    want = int(Anv.idTotal(invA, Ident.rows(invA)))
    cA = COINS[0]
    click(pgA, refA, stA, "idall")
    sA1, lA1 = render(pgA, refA, stA)
    budget("revealed list", lA1)
    K.check("Identify all 4" in sA0 and str(pgA.info).startswith("+Identified 4 items") and COINS[0] == cA - want and len(pgA.anRec()) == 4
            and "Revealed" in sA1 and Ident.rows(invA).size() == 0 and "Identify all" not in sA1,
            "N7: Identify all 4 (3 swords + a bag): -%d coins = the shown total, 4 Revealed lines, nothing unidentified left" % want)
    logs()

    # ============================================================================ N8: THE APPRAISAL TOOL RULE
    invT, csT = mkinv()
    csT["hotbar"].setItemStackForSlot(JShort(0), gear(UNID, rolled(UNID, 2, ident=False)))
    refT, stT = world(invT)
    pgT = FRP(prx)
    pgT.preselect(invT)
    apply(anvil__appraisal="true")
    g_none = str(Anv.idGate(U1))
    sT0, _l = render(pgT, refT, stT)
    cT = COINS[0]
    click(pgT, refT, stT, "id")
    r_none = str(pgT.info)
    br.put("acc:fn:has", AccHas())
    g_no = str(Anv.idGate(U1))
    n_acc0 = len(ACC_CALLS)
    sT1, _l = render(pgT, refT, stT)
    n_acc1 = len(ACC_CALLS) - n_acc0
    click(pgT, refT, stT, "idall")
    r_no = str(pgT.info)
    still = not bool(Data.identified(doc(at(csT, "hotbar", 0)))) and COINS[0] == cT
    K.check("not loaded" in g_none and "not loaded" in r_none and "accessory in your Accessory Bag" in g_no and "Appraisal Tool" in r_no and still
            and "Needs an Appraisal Tool" in sT0 and "Needs an Appraisal Tool" in sT1 and int(Anv.toolTier(U1)) == 0,
            "N8: anvil.appraisal ON: no SkyyAccessories -> refused ('%s'); no tool in the bag -> refused, Identify all too; nothing paid" % g_no[:60])
    K.check(all("Appraiser" not in x for x in (g_none, g_no, r_none, r_no, sT0, sT1, str(Anv.toolLine(U1)))),
            "N8 (fix round): no text points at an Appraiser NPC (none exists yet)")
    ACC.add(T2)
    tier = int(Anv.toolTier(U1))
    sT2, _l = render(pgT, refT, stT)
    click(pgT, refT, stT, "id")
    K.check(tier == 2 and "Appraisal Tool II" in str(Anv.toolLine(U1)) and Anv.idGate(U1) is None and "Appraisal Tool II" in sT2
            and str(pgT.info).startswith("+Identified") and bool(Data.identified(doc(at(csT, "hotbar", 0)))) and ACC_CALLS[-1] == T2,
            "N8: with the Appraisal Tool II in the bag (the highest id asked first) identifying works")
    K.check(n_acc1 == 3, "N8 (fix round 2): one page build with an unidentified item on the anvil asks acc:fn:has once per id (3 calls, was 12): %d" % n_acc1)
    # fix round 2: part.anvil off = the 0.2.25 Identify page; the Appraisal Tool rule holds there too (one / all; reroll has the same hook)
    _acc = set(ACC)
    ACC.clear()
    apply(anvil__appraisal="true", part__anvil="false")
    invI, csI = mkinv()
    csI["hotbar"].setItemStackForSlot(JShort(0), gear(UNID, rolled(UNID, 2, ident=False)))
    ip_ = P("IdentifyPage")(prx)
    ip_.preselect(invI)
    cI0 = COINS[0]
    ip_.lastClick = JLong(0)
    ip_.one(invI)
    i1_ = str(ip_.info)
    ip_.lastClick = JLong(0)
    ip_.all(invI)
    i2_ = str(ip_.info)
    stillI = not bool(Data.identified(doc(at(csI, "hotbar", 0)))) and COINS[0] == cI0
    ACC.add(T1)
    ip_.lastClick = JLong(0)
    ip_.one(invI)
    i3_ = str(ip_.info)
    K.check("Appraisal Tool" in i1_ and "Appraisal Tool" in i2_ and stillI and i3_.startswith("+") and bool(Data.identified(doc(at(csI, "hotbar", 0)))),
            "N8 (fix round 2): part.anvil off - the old Identify page refuses Identify + Identify all without a tool (nothing paid), works with "
            "the Appraisal Tool I: %s | %s | %s" % (i1_[:50], i2_[:50], i3_[:50]))
    ACC.clear()
    ACC.update(_acc)
    apply(anvil__appraisal="true", identify__command="false")
    csT["hotbar"].setItemStackForSlot(JShort(1), gear(UNID, rolled(UNID, 2, ident=False)))
    pgT.anPick(invT, JInt(0), JInt(1))
    sT3, _l = render(pgT, refT, stT)
    cT3 = COINS[0]
    click(pgT, refT, stT, "id")
    K.check("identifier" in str(pgT.info) and "Not on the Anvil" in sT3 and COINS[0] == cT3 and not bool(Data.identified(doc(at(csT, "hotbar", 1)))),
            "N8: identify.command off = identify at the identifier, never on the Anvil (even with a tool)")
    apply()
    br.remove("acc:fn:has")
    ACC.clear()
    logs()

    # ============================================================================ N9: guards
    invG, csG = mkinv()
    csG["hotbar"].setItemStackForSlot(JShort(0), gear(SW, rolled(SW, 1)))
    csG["hotbar"].setItemStackForSlot(JShort(1), gear(UNID, rolled(UNID, 1, ident=False)))
    refG, stG = world(invG)
    pgG = FRP(prx)
    pgG.preselect(invG)
    fpG, cG = str(Forge.fp(at(csG, "hotbar", 0))), COINS[0]
    br.put("profile:busy:" + str(U1), True)
    click(pgG, refG, stG, "forge")
    g1 = str(pgG.info)
    pgG.anPick(invG, JInt(0), JInt(1))
    click(pgG, refG, stG, "id")
    g2 = str(pgG.info)
    br.remove("profile:busy:" + str(U1))
    pgG.lastForge = JLong(JClass("java.lang.System").currentTimeMillis())
    inf_ = str(pgG.info)
    pgG.handleDataEvent(refG, stG, '{"a":"id"}')
    g3 = str(pgG.info) == inf_
    pgG.epoch = "old-epoch"
    click(pgG, refG, stG, "id")
    g4 = "profile changed" in str(pgG.info) and int(pgG.selSec) == -1
    pgG.lastForge = JLong(0)
    pgG.anId(invG)
    g5 = "Pick an unidentified item" in str(pgG.info)
    K.check("still loading" in g1 and "still loading" in g2 and g3 and g4 and g5 and COINS[0] == cG and str(Forge.fp(at(csG, "hotbar", 0))) == fpG
            and not bool(Data.identified(doc(at(csG, "hotbar", 1)))),
            "N9: guards: profile:busy refuses reforge + identify, a double click within 400 ms does nothing, a profile change clears the anvil, "
            "Identify without an item is refused - nothing paid, nothing changed")
    # fix round 2: after Identify the Level up / Upgrade buttons sit where Identify was - a click 450 ms later does nothing, 1.3 s later works
    pgG.anPick(invG, JInt(0), JInt(1))
    click(pgG, refG, stG, "id")
    idok = str(pgG.info).startswith("+Identified") and bool(Data.identified(doc(at(csG, "hotbar", 1))))
    now_ = int(JClass("java.lang.System").currentTimeMillis())
    pgG.anIdAt = JLong(now_ - 450)
    fpI, cI = str(Forge.fp(at(csG, "hotbar", 1))), COINS[0]
    late = []
    for a_ in ("forge", "lvl", "up"):
        click(pgG, refG, stG, a_)
        late.append("Just identified" in str(pgG.info))
    same_ = str(Forge.fp(at(csG, "hotbar", 1))) == fpI and COINS[0] == cI
    pgG.anIdAt = JLong(now_ - 1300)
    click(pgG, refG, stG, "forge")
    K.check(idok and all(late) and same_ and str(pgG.info).startswith("+") and str(Forge.fp(at(csG, "hotbar", 1))) != fpI,
            "N9 (fix round 2): Reforge / Level up / Upgrade clicked 450 ms after Identify change nothing ('Just identified'); 1.3 s later Reforge "
            "works: %s / %s" % (late, str(pgG.info)[:60]))

    # ============================================================================ N10: FAILURES at every step - never a copy, refunds
    # (a) reforge: the slot refuses the new stack -> refunded, the item unchanged
    invF, csF = mkinv(fail=("hotbar",))
    csF["hotbar"].setItemStackForSlot(JShort(0), gear(SW, rolled(SW, 2)))
    csF["hotbar"].setItemStackForSlot(JShort(1), gear(UNID, rolled(UNID, 2, ident=False)))
    refF, stF = world(invF)
    pgF = FRP(prx)
    pgF.preselect(invF)
    fpF, cF = str(Forge.fp(at(csF, "hotbar", 0))), COINS[0]
    csF["hotbar"].refuseId = SW
    click(pgF, refF, stF, "forge")
    a_ok = COINS[0] == cF and str(Forge.fp(at(csF, "hotbar", 0))) == fpF and cnt(invF, [SW])[SW] == 1 and "refunded" in str(pgF.info).lower()
    # (b) identify: the slot refuses -> refunded, still unidentified
    csF["hotbar"].refuseId = UNID
    csF["hotbar"].tripped = False
    pgF.anPick(invF, JInt(0), JInt(1))
    click(pgF, refF, stF, "id")
    b_ok = COINS[0] == cF and not bool(Data.identified(doc(at(csF, "hotbar", 1)))) and cnt(invF, [UNID])[UNID] == 1 and "refunded" in str(pgF.info).lower()
    csF["hotbar"].refuseId = None
    lgF = logs()
    K.check(a_ok and b_ok and any("REFUND" in l_ for l_ in lgF),
            "N10: a refused write: reforge + identify refund the coins, the item is unchanged, REFUND logged ('%s')" % str(pgF.info)[:70])
    # (c) coins unavailable: refused before anything moves
    coins_off()
    pgF.anPick(invF, JInt(0), JInt(0))
    click(pgF, refF, stF, "forge")
    c_ok = "Coins are not available" in str(pgF.info) and str(Forge.fp(at(csF, "hotbar", 0))) == fpF
    coins_on()
    K.check(c_ok, "N10: SkyyCoins missing: the reforge is refused, nothing changed")

    def up_world(fail=()):
        iv, cz = mkinv(fail=fail)
        cz["hotbar"].setItemStackForSlot(JShort(0), gear(fr_, rolled(fr_, 3)))
        cz["storage"].setItemStackForSlot(JShort(0), stack(bar, mats[bar]))
        cz["storage"].setItemStackForSlot(JShort(1), stack(ess, mats[ess] + 1))
        rf, sf = world(iv)
        pq = FRP(prx)
        pq.preselect(iv)
        return iv, cz, rf, sf, pq
    # (d) the materials' slot refuses -> restored, nothing used
    iv, cz, rf, sf, pq = up_world(fail=("storage",))
    b_d = cnt(iv, [fr_, to_, bar, ess])
    cz["storage"].rm = 1
    click(pq, rf, sf, "up")
    d_ok = cnt(iv, [fr_, to_, bar, ess]) == b_d and "nothing was used" in str(pq.info)
    # (e) the item's slot refuses the upgraded item -> the item + materials back
    iv, cz, rf, sf, pq = up_world(fail=("hotbar",))
    b_e = cnt(iv, [fr_, to_, bar, ess])
    cz["hotbar"].refuseId = to_
    click(pq, rf, sf, "up")
    e_ok = cnt(iv, [fr_, to_, bar, ess]) == b_e and "nothing was used" in str(pq.info)
    # (f) a CRASH right after the materials left: never a copy (the cage stays, no Iron cage); UPGRADE-BEGIN is on disk for an admin
    iv, cz, rf, sf, pq = up_world()
    b_f = cnt(iv, [fr_, to_, bar, ess])
    logs()
    Up.CRASH_AT = 1
    click(pq, rf, sf, "up")
    Up.CRASH_AT = 0
    a_f = cnt(iv, [fr_, to_, bar, ess])
    lgf = logs()
    f_ok = a_f[fr_] == b_f[fr_] and a_f[to_] == b_f[to_] == 0 and a_f[bar] == b_f[bar] - mats[bar] and any("UPGRADE-BEGIN" in l_ for l_ in lgf) and pq.upMade is None
    # (g) the bookkeeping throwing after the swap: the upgrade stands, exactly once
    iv, cz, rf, sf, pq = up_world()
    b_g = cnt(iv, [fr_, to_, bar, ess])
    Up.AFTER_THROWS = True
    click(pq, rf, sf, "up")
    Up.AFTER_THROWS = False
    g_ok = cnt(iv, [fr_, to_, bar, ess]) == {fr_: b_g[fr_] - 1, to_: b_g[to_] + 1, bar: b_g[bar] - mats[bar], ess: b_g[ess] - mats[ess]} and str(pq.info).startswith("+Upgraded")
    logs()
    K.check(d_ok and e_ok and f_ok and g_ok, "N10: Upgrade failures through the Anvil: materials refused -> restored (%s); the new item refused -> item + materials "
            "back (%s); a crash right after the materials left -> the cage is still there and NO Iron cage (only the logged materials gone) (%s); "
            "the bookkeeping throwing -> one upgrade (%s)" % (d_ok, e_ok, f_ok, g_ok))

    # ============================================================================ N11: the Requip rows (fetch, Return to Requip)
    store = {"e1": gear(fr_, rolled(fr_, 1))}
    RQ = []

    def stamped(s_, eid):
        md = s_.getMetadata()
        md = BD() if md is None else md.clone()
        md.put("SkyyRequip", BD("e", BS(eid)))
        return s_.withMetadata(md)

    @JImplements("java.util.function.Function")
    class WList(object):
        @JOverride
        def apply(self, o):
            rows_ = []
            if str(o[1]) == "items":
                for e_, s_ in store.items():
                    rows_.append(JArray(JClass("java.lang.Object"))([e_, s_.getItemId(), s_.getMetadata()]))
            return JArray(JClass("java.lang.Object"))(rows_)

    @JImplements("java.util.function.Function")
    class WFetch(object):
        @JOverride
        def apply(self, o):
            e_ = str(o[1])
            RQ.append(("fetch", e_))
            s_ = store.pop(e_, None)
            if s_ is None:
                return "gone"
            RQ_INV[0].getStorage().addItemStack(stamped(s_, e_))
            return "ok"

    @JImplements("java.util.function.Function")
    class WDep(object):
        @JOverride
        def apply(self, o):
            sec, sl = str(o[1]), int(o[2])
            c_ = {"hotbar": RQ_CS[0]["hotbar"], "storage": RQ_CS[0]["storage"], "backpack": RQ_CS[0]["backpack"]}.get(sec)
            s_ = c_.getItemStack(JShort(sl))
            RQ.append(("dep", sec, sl))
            c_.removeItemStackFromSlot(JShort(sl))
            store[str(Data.eidOf(s_))] = s_
            return "eid:" + str(Data.eidOf(s_))

    @JImplements("java.util.function.Function")
    class WCan(object):
        @JOverride
        def apply(self, o):
            return None
    invR, csR = mkinv()
    csR["hotbar"].setItemStackForSlot(JShort(0), gear(SW, rolled(SW, 1)))
    RQ_INV, RQ_CS = [invR], [csR]
    for k2, f2 in (("wardrobe:fn:list", WList()), ("wardrobe:fn:fetch", WFetch()), ("wardrobe:fn:depositSlot", WDep()), ("wardrobe:fn:canDeposit", WCan())):
        br.put(k2, f2)
    refR, stR = world(invR)
    pgR = FRP(prx)
    sR0, lR0 = render(pgR, refR, stR)
    budget("requip", lR0)
    pgR.handleDataEvent(refR, stR, '{"a":"rq:0"}')
    atR = Stamp.at(invR, JInt(int(pgR.selSec)), JInt(int(pgR.selSlot))) if int(pgR.selSec) >= 0 else None
    sR1, _l = render(pgR, refR, stR)
    ok_fetch = ("fetch", "e1") in RQ and atR is not None and str(atR.getItemId()) == fr_ and "on the anvil" in str(pgR.info) and "Return to Requip" in sR1
    pgR.handleDataEvent(refR, stR, '{"a":"rqback"}')
    ok_back = any(x[0] == "dep" for x in RQ) and "went back into Requip" in str(pgR.info) and int(pgR.selSec) == -1 and "e1" in store
    K.check("In Requip (1)" in sR0 and ok_fetch and ok_back,
            "N11: the Anvil lists IN-Requip gear (a cage: forgeable or a next tier); a click fetches it ONTO the anvil; Return to Requip puts it back")
    # fix round: ui.frames off (a fixed list) with the Requip block: 8 gear rows a page (6 with Identify all on top), everything fits
    for i_ in range(14):
        csR["storage"].setItemStackForSlot(JShort(i_), gear(SW, rolled(SW, 0)))
    apply(ui__frames="false")
    pgF = FRP(prx)
    sF0, lF0 = render(pgF, refR, stR)
    budget("frames off + requip", lF0, card_in=210)
    csR["storage"].setItemStackForSlot(JShort(20), gear(UNID, rolled(UNID, 2, ident=False)))
    pgF2 = FRP(prx)
    sF1, lF1 = render(pgF2, refR, stR)
    budget("frames off + requip + identify all", lF1, card_in=210)
    apply()
    K.check("In Requip (1)" in sF0 and "#SkyyGRow7 " in sF0 and "#SkyyGRow8 " not in sF0 and "Page 1 / 2" in sF0 and lF0[0]["decl#SkyyGList"] == 8 * 46 + 212
            and "Identify 1 item" in sF1 and "#SkyyGRow5 " in sF1 and "#SkyyGRow6 " not in sF1 and lF1[0]["decl#SkyyGList"] == 6 * 46 + 212
            and lF0[0]["#SkyyGListBox"] <= 656 and lF1[0]["#SkyyGListBox"] <= 656,
            "N11 (fix round): ui.frames off + Requip rows: 8 gear rows a page (6 under Identify all) + the Requip block inside the fixed list, column <= 656 (%d / %d)"
            % (lF0[0].get("#SkyyGListBox", -1), lF1[0].get("#SkyyGListBox", -1)))
    for k2 in ("wardrobe:fn:list", "wardrobe:fn:fetch", "wardrobe:fn:depositSlot", "wardrobe:fn:canDeposit"):
        br.remove(k2)

    # ============================================================================ N12: every other click
    invE, csE = mkinv()
    csE["hotbar"].setItemStackForSlot(JShort(0), gear(SW, rolled(SW, 1)))
    for i_ in range(14):
        csE["storage"].setItemStackForSlot(JShort(i_), gear(SW, rolled(SW, 0)))
    refE, stE = world(invE)
    pgE = FRP(prx)
    pgE.preselect(invE)
    rb = int(pgE.rebuilds)
    for ev_ in ('{"a":"mode:0"}', '{"a":"mode:1"}', '{"a":"mode:2"}', '{"a":"mode:3"}', '{"a":"mode:x"}', '{"a":"sel:99"}', '{"a":"sel:x"}', '{"a":""}',
                '{"a":"nothing"}', '{"a":"prev"}', '{"a":"next"}'):
        pgE.handleDataEvent(refE, stE, ev_)
    pgE.handleDataEvent(refE, stE, None)
    rb2 = int(pgE.rebuilds)
    pgE.upMade = BD()
    pgE.anRev = BD()
    pgE.handleDataEvent(refE, stE, '{"a":"refresh"}')
    cl0 = int(pgE.closes)
    pgE.handleDataEvent(refE, stE, '{"a":"back"}')
    K.check(int(pgE.selSec) == 0 and rb2 == rb + 2 and pgE.upMade is None and pgE.anRev is None and int(pgE.closes) == cl0 + 1 and int(pgE.mode) == 0,
            "N12: tab clicks (mode:0-3) keep the Anvil (Craft / Multitool open through their commands - no command manager here), bad / stale "
            "events are swallowed, prev / next rebuild, refresh clears the Made / Revealed state, Back closes (no SkyyMenu)")
    # fix round: Refresh after a profile switch clears the anvil (the old pick is never re-pinned to the new profile)
    pgE.preselect(invE)
    ep_real = str(pgE.epoch)
    pgE.epoch = "stale-profile"
    pgE.handleDataEvent(refE, stE, '{"a":"refresh"}')
    K.check(int(pgE.selSec) == -1 and "profile changed" in str(pgE.info) and str(pgE.epoch) == ep_real,
            "N12 (fix round): Refresh after a profile switch clears the anvil + says so, then takes the new profile ('%s')" % str(pgE.info))
    pgE.preselect(invE)
    pgE.handleDataEvent(refE, stE, '{"a":"refresh"}')
    K.check(int(pgE.selSec) == 0 and "profile changed" not in str(pgE.info), "N12 (fix round): Refresh on the same profile keeps the item on the anvil")
    apply(ui__frames="false")
    sE, lE = render(pgE, refE, stE)
    budget("frames off", lE, card_in=210)
    apply()
    K.check("Page 1 / 2" in sE and "#SkyyGBtnNext" in sE and "#000000(0.15)" in sE and "ContainerPanelPatch" not in sE,
            "N12: ui.frames off: the list pages (12 a page), the cards are the kit's plain well")
    # an item that moved is dropped at the next build
    csE["hotbar"].setItemStackForSlot(JShort(0), stack("Ingredient_Stick"))
    sM, _l = render(pgE, refE, stE)
    K.check("moved or changed" in str(pgE.info) and int(pgE.selSec) == -1 and "The anvil is empty" in sM, "N12: an item that moved leaves the anvil at the next build")

    # ============================================================================ N13: the commands open the Anvil (FakePM records the page)
    exe_ok = []
    if pm_field is not None:
        invC, csC = mkinv()
        csC["hotbar"].setItemStackForSlot(JShort(0), gear(fr_, rolled(fr_, 1)))
        csC["storage"].setItemStackForSlot(JShort(3), gear(UNID, rolled(UNID, 1, ident=False)))
        refC, stC = world(invC)
        invC2, csC2 = mkinv()
        csC2["storage"].setItemStackForSlot(JShort(3), gear(UNID, rolled(UNID, 1, ident=False)))
        refC2, stC2 = world(invC2)

        def run_cmd(cls, ref_, st_):
            cmd = P(cls)()
            exe = [m_ for m_ in P(cls).class_.getDeclaredMethods() if str(m_.getName()) == "execute"][0]
            exe.setAccessible(True)
            FPM.last = None
            exe.invoke(cmd, None, st_, ref_, prx, None)
            return FPM.last
        RP = P("ReforgePage")
        p1 = run_cmd("ReforgeCmd", refC, stC)
        p2 = run_cmd("UpCmd", refC, stC)
        p3 = run_cmd("IdentifyCmd", refC2, stC2)
        p4 = run_cmd("IdentifyCmd", refC, stC)
        exe_ok.append(p1 is not None and RP.class_.isInstance(p1) and int(p1.selSec) == 0 and int(p1.selSlot) == 0)
        exe_ok.append(p2 is not None and RP.class_.isInstance(p2) and int(p2.mode) == 0 and int(p2.selSec) == 0)
        exe_ok.append(p3 is not None and RP.class_.isInstance(p3) and int(p3.selSec) == 1 and int(p3.selSlot) == 3)
        exe_ok.append(p4 is not None and RP.class_.isInstance(p4) and int(p4.selSec) == 0)
        apply(part__anvil="false")
        p5 = run_cmd("IdentifyCmd", refC2, stC2)
        p6 = run_cmd("UpCmd", refC, stC)
        apply(identify__command="false")
        p7 = run_cmd("IdentifyCmd", refC2, stC2)
        apply()
        exe_ok.append(p5 is not None and P("IdentifyPage").class_.isInstance(p5))
        exe_ok.append(p6 is not None and RP.class_.isInstance(p6) and int(p6.mode) == 1)
        exe_ok.append(p7 is None and FPR is not None and "switched off" in str(prx.said[-1]))
        groups = []
        for cls in ("ReforgeCmd", "UpCmd", "IdentifyCmd"):
            cmd = P(cls)()
            g_ = None
            kk = cmd.getClass()
            while kk is not None and g_ is None:
                for f_ in kk.getDeclaredFields():
                    if "ermissionGroups" in str(f_.getName()):
                        f_.setAccessible(True)
                        g_ = f_.get(cmd)
                kk = kk.getSuperclass()
            groups.append(g_ is not None and "hytale:Adventurer" in [str(x) for x in g_])
        exe_ok.append(all(groups))
    K.check(pm_field is not None and all(exe_ok), "N13: EXECUTED: /reforge and /upgrade open the Anvil (ReforgePage, mode 0) with the held cage on it; /identify "
            "opens the Anvil on the held item, or with nothing anvil-able held on the FIRST unidentified item (storage 4); part.anvil off: "
            "/identify = the Identify page, /upgrade = the Upgrade mode; identify.command off: refused; all three hytale:Adventurer: %s" % exe_ok)
    # fix round 2: the Level up reasons on the 275 px card; the ready line names the Anvil tab
    Int_ = JClass("java.lang.Integer")
    li_ = JArray(JObject)([Int_.valueOf(5), Int_.valueOf(9), Int_.valueOf(10), Int_.valueOf(12), Int_.valueOf(5), JString("x" * 90)])
    shorts = [str(P("ReforgePage").anLvShort(JInt(c_), li_)) for c_ in range(1, 8)] + [str(P("ReforgePage").anLvShort(JInt(7), None))]
    st_on = str(P("GearUp").statusText())
    apply(part__anvil="false")
    st_off = str(P("GearUp").statusText())
    apply()
    K.check(all(len(x) <= 38 for x in shorts) and shorts[4] == "Level up: needs your level 10." and len(set(shorts[:7])) == 7
            and "Anvil tab + /upgrade" in st_on and "Reforge page Upgrade tab" in st_off,
            "N (fix round 2): the card's Level up reasons are at most 38 characters (%s); the ready line says 'Anvil tab' (part.anvil off: the "
            "old words)" % max(len(x) for x in shorts))
    K.check(not LAYOUT_BAD, "N: every rendered Anvil fits its budget (body 808, columns 656, cards 202 / 210, widths) with unique ids and no '_': %s" % LAYOUT_BAD)
    K.save()


# ====================================================================================================== X: the 0.2.25 stats comparison
def run_x25(env):
    d = os.path.join(SCRATCH, "x25")
    os.makedirs(os.path.join(d, "tmp"), exist_ok=True)
    os.makedirs(os.path.join(d, "fake"), exist_ok=True)
    out = os.path.join(d, "exec.json")
    e2 = dict(env)
    e2["TEMP"] = e2["TMP"] = os.path.join(d, "tmp")
    p = subprocess.run([sys.executable, os.path.join(HERE, "test_skyygear_0.2.25.py"), "--phase", "exec", "--out", out, "--dir", d, "--jar", JAR,
                        "--old", J24], env=e2, capture_output=True, text=True)
    check(p.returncode == 0 and os.path.isfile(out), "X: the 0.2.25 harness's exec phase ran with the 0.2.26 jar (rc %s)" % p.returncode)
    if not os.path.isfile(out):
        print(p.stdout[-2000:], p.stderr[-2000:])
        return
    r = json.load(open(out))
    expected = [f for f in r["fails"] if "fresh config text" in f]
    other = [f for f in r["fails"] if "fresh config text" not in f]
    OKS[0] += r["ok"]
    check(not other and r["ok"] >= 20, "X: the randomised 0.2.24-vs-new stats comparison (snapshot, tick, hits, gate, stamp scan, chest file, bridge): "
          "%d ok, no other fail: %s" % (r["ok"], other))
    check(len(expected) <= 1, "X: its only expected deviation is the fresh config text (the 3 new Anvil rows - checked exactly in D): %s" % expected)
    for n in r.get("notes", [])[:6]:
        print("  note (X): %s" % str(n)[:200])


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
    K.check(set(add) == NEW_CLASSES and not gone, "C: added exactly GearAnvil, none removed: + %s - %s" % (add, gone))
    want = {
        "GearUi": {"~m tabs"},
        "ReforgePage": {"+f anRecent", "+f anRev", "+f anArm", "+f anArmFp", "+m anRec", "+m anClear", "+m anPick", "+m anPreselect", "+m anText",
                        "+m anHead", "+m anLines", "+m anReforge", "+m anUpgrade", "+m anIdentify", "+m anReid", "+m anHelp", "+m anPanel",
                        "+m anList", "+m anBuild", "+m anGuard", "+m anId", "+m anReroll", "+m anIdAll", "+m anEvent", "~m rqRows",
                        "~m build", "~m handleDataEvent", "~m pick", "~m upPick",
                        # fix round 2: the Appraisal Tool tier cache, the late-click guard, the short Level up reasons
                        "+f anTierV", "+f anTierOk", "+f anIdAt", "+m anTier", "+m anLvShort"},
        # fix round 2: the Appraisal Tool rule on the old Identify page (part.anvil off); the ready line names the Anvil tab
        "IdentifyPage": {"~m one", "~m all", "~m reroll"},
        "GearUp": {"~m statusText"},
        "UpCmd": {"~m execute"},
        "IdentifyCmd": {"~m execute"},
        "SmithFn": {"~m open"},
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
    K.check(set(cfgd.get("GearCfg", [])) >= {"+f ANVIL_ON", "+f ID_TOOL", "+f ID_TOOLS", "+m checkIdTools"} and "GearDefs" not in cfgd
            and all(x.startswith("+f ") or x.startswith("~m ") or x.startswith("+m ") or x == "~<clinit>" for v in cfgd.values() for x in v),
            "C: the config classes gained the 3 rows (fields, checkIdTools, the kit's row tables) and nothing else: %s" % cfgd)
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
        K.check(bool(Cfg.ANVIL_ON) and not bool(Cfg.ID_TOOL) and str(Cfg.ID_TOOLS).startswith("Skyy_Accessory_Appraisal_T1"),
                "D/new: the live file has no 0.2.26 rows -> the defaults apply (Anvil on, the Appraisal rule off)")
    K.save(cfg=snaps[0].decode("latin-1"), fresh=str(Cfg.defaultsText()))


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
    for flag, fn in (("--mkfake", lambda: run_mkfake4(arg("--mkfake"))), ("--verify", lambda: H["run_verify"](arg("--out"))),
                     ("--anvil", lambda: run_anvil(arg("--out"))), ("--compare", lambda: run_compare(arg("--out"))),
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
    assert os.path.isfile(JAR) and os.path.isfile(OLD_JAR) and os.path.isfile(AR_SRC) and os.path.isfile(J24), (JAR, OLD_JAR, AR_SRC, J24)
    sc = os.path.realpath(SCRATCH)
    assert sc.startswith(os.path.realpath(SCR_ROOT) + os.sep), "the scratch folder must be inside " + SCR_ROOT
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"), exist_ok=True)
    os.makedirs(os.path.join(SCRATCH, "packs"), exist_ok=True)
    with zipfile.ZipFile(OLD_JAR) as z_:
        assert '"Version": "%s"' % OLD_VERSION in z_.read("manifest.json").decode("utf-8"), "the old jar is not " + OLD_VERSION
    shutil.copyfile(AR_SRC, AR_JAR)              # read-only sources; the children load the scratch copies
    if os.path.isfile(MT_SRC):
        shutil.copyfile(MT_SRC, MT_JAR)
    else:
        print("note: no Multitools 1.2.9 jar - the Multitool tab part runs without it")
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.environ["TEMP"] = os.environ["TMP"] = env["TEMP"]
    try:
        run_assets()
        p = child(env, "--mkfake", FAKE_DIR)
        check(p.returncode == 0, "F: the stand-ins were generated")
        for label, flag in (("verify", "--verify"), ("compare", "--compare"), ("anvil", "--anvil")):
            out = os.path.join(SCRATCH, "%s.json" % label)
            pr = child(env, flag, "--out", out)
            check(pr.returncode == 0, "%s: the child exited cleanly (%s)" % (label, pr.returncode))
            take(out, label)
        run_x25(env)
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
            check(res["old"]["cfg"] == res["new"]["cfg"], "D: 0.2.26 starts the live copy to exactly the config.properties 0.2.25 writes")
            fo = sorted(f for f in os.listdir(os.path.join(SCRATCH, "live-old")) if not f.startswith("config-history"))
            fn_ = sorted(f for f in os.listdir(os.path.join(SCRATCH, "live-new")) if not f.startswith("config-history"))
            check(fo == fn_, "D: the same files after the starts: %s / %s" % (fo, fn_))
            a_ = res["old"]["fresh"].replace("0.2.25", "VER").split("\n")
            b_ = res["new"]["fresh"].replace("0.2.26", "VER").split("\n")
            extra = [l_ for l_ in b_ if l_ not in a_]
            keys = [l_ for l_ in extra if not l_.startswith("#")]
            check([l_ for l_ in a_ if l_ not in b_] == [] and extra[0] == "# ---- the one Anvil tab + the Appraisal Tool rule (SkyyGear VER) ----"
                  and keys == ["part.anvil=true", "anvil.appraisal=false", "anvil.appraisalIds=" + ",".join((T1, T2, T3))] and len(extra) == 7,
                  "D: a FRESH default file differs from 0.2.25's only by the Anvil block: %s" % extra)
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
