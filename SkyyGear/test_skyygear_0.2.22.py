"""Harness for SkyyGear 0.2.22 (UPGRADE INSIDE THE REFORGE PAGE + THE LEVEL IN ITEM NAMES; tools/gear_0_2_22_patch.py header).
Build first:
    python tools/gear_0_2_22_patch.py && python SkyyGear/build_skyygear_0.2.22.py

    python SkyyGear/test_skyygear_0.2.22.py [--jar <SkyyGear-0.2.22.jar>] [--old <SkyyGear-0.2.21.jar>] [--armory <SkyyArmory-0.1.20.jar>]
                                            [--mt <Multitools-1.2.9.jar>] [--root <scratch root>] [--keep]

The 0.2.11 harness's helpers (stand-ins, verify A, the bare-server boot, the engine-access audit AA) are loaded from
SkyyGear/test_skyygear_0.2.11.py (as the 0.2.12 - 0.2.21 harnesses do); this harness adds MergeFail (a container that refuses / throws on
demand), FakeReforgePage / FakeMultiPage (rebuild / close counted) and FakePR (a PlayerRef that records messages). SkyyArmory 0.1.20 (repo
jar) and Multitools 1.2.9 (UserData/Mods, read-only) are COPIED into the scratch folder and loaded from there as their own packs - the Soul
Cage recipes the upgrade reads are SkyyArmory's REAL recipes.
  S  non-class entries 0.2.21 -> 0.2.22: only the manifest changed; classes added = GearUp, UpCmd (no new page class)
  A  every class of the jar loads + verifies (-Xverify:all)
  T  THE LADDER TABLE EXECUTED: okId / parseCost / parse (chains, written costs, convert rows refused, a cost on the first item, bad ids,
     two ladders, a loop, bad amounts, a missing ")") / cur (WARN + skip; a loop drops all) / row / next / written / steps / writtenSteps /
     checkLadders (unknown item / material)
  R  THE COSTS from SkyyArmory 0.1.20's real recipes: fromRecipe / cost = each step's OTHER inputs, equal to the jar's JSON for all 7 cage
     steps; costText; a written cost wins; a step no recipe makes = refused; the cache follows the store size
  U  GearUp EXECUTED: check (every refusal), capOf / relevel / docI (same rarity + lines, re-levelled, kind, lvU / box dropped, notes) /
     lossText / preview / rows / have / shortOf / usable / matSecs / where; upgrade(): EVERY Soul Cage tier, rolled AND plain (the whole
     ladder Orb -> Onyxium on one rolled item + one plain item), exact material use storage-first, partial stacks, documented stacks never
     used, short materials, full inventory, a second click, a crash between the steps (no dupe), failure at (a) / (b), restore failing
     (loss logged, never a copy), the bookkeeping throwing, Mythic / UT / unidentified refused with nothing moved; gear.log lines; no XP
  N  LEVEL IN NAMES: nameMsg / lvTag per family (weapon, armor, tool, multitool, wand), reforge prefix + colour kept, unidentified item,
     bag range (A-B and A), the switch off, sig changes with the switch, GearUnid.reView via stampStack (once, then stable)
  P  THE REFORGE PAGE EXECUTED: the tab row (3 / 2 / 1 tabs), Reforge -> Upgrade -> Reforge keeps the item when it fits and the REFORGE
     still works (a real reforge after switching back), the Upgrade list / anvil / materials / preview / made state / refusals / guards
     (profile:busy, double click, epoch, nothing picked), stale clicks swallowed, refresh / prev / next / back, the Multitool tab, upgrading
     off, the 1080p height budget of the right column; the /multitool page's tab row + tab clicks; /upgrade (off, open, permission group)
  C  CLASS COMPARE 0.2.21 -> 0.2.22 (javassist members)
  D  START TWICE on a scratch COPY of the live Skyy_SkyyGear folder with each jar: the 2nd start changes nothing; 0.2.22 writes the same
     config.properties as 0.2.21 (absent rows = defaults, no one-time update)
  AA THE ENGINE-ACCESS AUDIT
Scratch: tools/dev/scratch/gear0222b/harness (or --root) (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B

VERSION = "0.2.22"
OLD_VERSION = "0.2.21"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCR_ROOT = os.path.abspath(arg("--root", os.path.join(TOOLS, "dev", "scratch", "gear0222b")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyGear-%s.jar" % OLD_VERSION)))      # read only
AR_SRC = os.path.abspath(arg("--armory", os.path.join(ROOT, "SkyyArmory", "SkyyArmory-0.1.20.jar")))   # read only - copied
MT_SRC = os.path.abspath(arg("--mt", os.path.join(B.MODS_DIR, "Multitools-1.2.9.jar")))           # read only - copied
AR_JAR = os.path.join(SCRATCH, "packs", "SkyyArmory-0.1.20.jar")
MT_JAR = os.path.join(SCRATCH, "packs", "Multitools-1.2.9.jar")
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyGear")
PKG = "com.skyy.gear."
SOUL = ["Weapon_Wand_SoulOrb"] + ["Weapon_Wand_SoulCage_%s" % m for m in ("Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")]
NEW_CLASSES = {"GearUp", "UpCmd"}
MULTI_PRE = "Tool_Hatchet_Pickaxe_Multitool_"

_H211 = os.path.join(HERE, "test_skyygear_0.2.11.py")
_t = open(_H211, encoding="utf-8").read()
_cut = _t.rindex('if __name__ == "__main__":')
H = {"__name__": "skyygear_h211", "__file__": _H211, "__builtins__": __builtins__}
exec(compile(_t[:_cut], _H211 + " (helpers)", "exec"), H)
H.update({"JAR": JAR, "OLD_JAR": OLD_JAR, "SCRATCH": SCRATCH, "FAKE_DIR": os.path.join(SCRATCH, "fake"), "VERSION": VERSION})
FAKE_DIR = H["FAKE_DIR"]
FAKE_PKG = H["FAKE_PKG"]
Child, _jvm, jar_classes = H["Child"], H["_jvm"], H["jar_classes"]
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def soul_recipes():
    """the 7 cage steps of the SkyyArmory 0.1.20 jar: [(from, to, {material: qty})]"""
    out = []
    with zipfile.ZipFile(AR_SRC) as z:
        js = {}
        for n in z.namelist():
            b = os.path.basename(n)[:-5]
            if n.startswith("Server/Item/Items/") and n.endswith(".json") and b in SOUL:
                js[b] = json.loads(z.read(n).decode("utf-8"))["Recipe"]
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
    check(not added and not (set(ea) - set(eb)) and changed == ["manifest.json"] and b'"0.2.22"' in eb["manifest.json"]
          and b"Upgrade tab (/upgrade)" in eb["manifest.json"] and b"item names end with their level" in eb["manifest.json"],
          "S: 0.2.21 -> 0.2.22: no file added / removed, only the manifest changed (version + the upgrade / name words): + %s ~ %s" % (added[:3], changed[:3]))
    ca = set(n for n in zo.namelist() if n.endswith(".class"))
    cb = set(n for n in zn.namelist() if n.endswith(".class"))
    check(not (ca - cb) and set(n.split("/")[-1][:-6] for n in cb - ca) == NEW_CLASSES,
          "S: classes added = GearUp, UpCmd (no separate page); none removed: + %s - %s" % (sorted(cb - ca), sorted(ca - cb)))
    names = set(zn.namelist())
    check(not [n for n in names if "SoulCage" in n or "SoulOrb" in n or "inkblindcat" in n.lower()],
          "S: no SkyyArmory / Multitools file is shipped or overridden (runtime ids only)")


# ====================================================================================================== F+: this round's stand-ins
def run_mkfake2(out_dir):
    H["run_mkfake"](out_dir)
    from jpype import JClass
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(JAR)
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    P = FAKE_PKG
    IS = "com.hypixel.hytale.server.core.inventory.ItemStack"
    mf = cp.makeClass(P + ".MergeFail")
    mf.setSuperclass(cp.get("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer"))
    mf.addField(CtField.make("public int rm;", mf))               # 1 = removeItemStackFromSlot throws, 2 = removes, then throws
    mf.addField(CtField.make("public String refuseId;", mf))      # setItemStackForSlot of this id throws
    mf.addField(CtField.make("public int refuseQty;", mf))        # > 0: setItemStackForSlot of a stack with this quantity throws
    mf.addField(CtField.make("public boolean sticky;", mf))       # after one refusal every later set throws too
    mf.addField(CtField.make("public boolean tripped;", mf))
    mf.addConstructor(CtNewConstructor.make("public MergeFail(short n) { super(n); }", mf))
    mf.addMethod(CtNewMethod.make(
        "public com.hypixel.hytale.server.core.inventory.transaction.ItemStackSlotTransaction setItemStackForSlot(short s, %s i) {\n"
        "  if (this.tripped && this.sticky) throw new java.lang.IllegalStateException(\"test: the container refuses everything now\");\n"
        "  if (this.refuseId != null && i != null && this.refuseId.equals(i.getItemId())) { this.tripped = true; throw new java.lang.IllegalStateException(\"test: the slot refuses \" + this.refuseId); }\n"
        "  if (this.refuseQty > 0 && i != null && i.getQuantity() == this.refuseQty) { this.tripped = true; throw new java.lang.IllegalStateException(\"test: the slot refuses a stack of \" + this.refuseQty); }\n"
        "  return super.setItemStackForSlot(s, i);\n}" % IS, mf))
    mf.addMethod(CtNewMethod.make(
        "public com.hypixel.hytale.server.core.inventory.transaction.SlotTransaction removeItemStackFromSlot(short s) {\n"
        "  if (this.rm == 1) throw new java.lang.IllegalStateException(\"test: remove refused\");\n"
        "  if (this.rm == 2) { super.removeItemStackFromSlot(s); throw new java.lang.IllegalStateException(\"test: removed, then failed\"); }\n"
        "  return super.removeItemStackFromSlot(s);\n}", mf))
    mf.writeFile(out_dir)
    for cls, base in (("FakeReforgePage", "ReforgePage"), ("FakeMultiPage", "MultiPage")):
        fp = cp.makeClass(P + "." + cls)
        fp.setSuperclass(cp.get(PKG + base))
        fp.addField(CtField.make("public int rebuilds;", fp))
        fp.addField(CtField.make("public int closes;", fp))
        fp.addConstructor(CtNewConstructor.make("public %s(com.hypixel.hytale.server.core.universe.PlayerRef pr) { super(pr); }" % cls, fp))
        fp.addMethod(CtNewMethod.make("public void rebuild() { this.rebuilds = this.rebuilds + 1; }", fp))
        fp.addMethod(CtNewMethod.make("public void close() { this.closes = this.closes + 1; }", fp))
        fp.writeFile(out_dir)
    PRc = cp.get("com.hypixel.hytale.server.core.universe.PlayerRef")
    if not JClass("javassist.Modifier").isFinal(PRc.getModifiers()):
        fr = cp.makeClass(P + ".FakePR")
        fr.setSuperclass(PRc)
        fr.addField(CtField.make("public java.util.ArrayList said;", fr))
        ctor = [c for c in PRc.getDeclaredConstructors()][0]
        fr.addConstructor(CtNewConstructor.make("public FakePR() { super(%s); }" % ", ".join(
            ("null" if not t.isPrimitive() else ("false" if t.getName() == "boolean" else "0")) for t in ctor.getParameterTypes()), fr))
        fr.addMethod(CtNewMethod.make("public void sendMessage(com.hypixel.hytale.server.core.Message m) { if (this.said == null) this.said = new java.util.ArrayList(); this.said.add(m == null ? \"null\" : String.valueOf(m.getRawText())); }", fr))
        fr.writeFile(out_dir)
    print("F+. MergeFail, FakeReforgePage, FakeMultiPage, FakePR written")


# ====================================================================================================== T + R + U + N + P (one booted engine)
def run_up(out):
    from jpype import JClass, JInt, JShort, JLong, JByte, JImplements, JOverride, JObject
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
    K.check(all(x is not None for x in souls) and n_gen >= 8, "E: SkyyArmory 0.1.20 (scratch copy) loaded as its own pack: the Soul Orb + 7 cages are "
            "real items, %d recipes generated (failed stores %s)" % (n_gen, afail))
    have_mt = os.path.isfile(MT_JAR)
    if have_mt:
        addpack(MT_JAR, "IBC:Multitools")
        gen_recipes([ITEM.getAssetMap().getAsset(MULTI_PRE + t) for t in ("Crude", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")])
    P = lambda n: JClass(PKG + n)
    Cfg, Gear, Up, Merge, Data, Roll, Forge, Stamp, Lvl, Defs, Log, View, Unid, Ui = (
        P("GearCfg"), P("Gear"), P("GearUp"), P("GearMerge"), P("GearData"), P("GearRoll"), P("GearForge"), P("GearStamp"), P("GearLevel"),
        P("GearDefs"), P("GearLog"), P("GearView"), P("GearUnid"), P("GearUi"))
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
    LADDER_DEF = str(Cfg.UP_LADDERS)
    K.check(LADDER_DEF == ">".join(SOUL) and bool(Cfg.UP_ON) and bool(Cfg.NAME_LV) and "upgrade.ladders=" + LADDER_DEF in FRESH
            and "part.upgrade=true" in FRESH and "view.levelInName=true" in FRESH,
            "E: the fresh config has part.upgrade=true, view.levelInName=true and the Soul Cage ladder (%s)" % LADDER_DEF[:80])
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    U1 = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-0000000000a1")
    BA = JClass("org.bson.BsonArray")
    BS, BI32, BB = JClass("org.bson.BsonString"), JClass("org.bson.BsonInt32"), JClass("org.bson.BsonBoolean")
    XP = [0]

    @JImplements("java.util.function.Function")
    class AddXp(object):
        @JOverride
        def apply(self, o):
            XP[0] += 1
            return JObject(JLong(1), JClass("java.lang.Long"))
    COINS = [10 ** 9]

    @JImplements("java.util.function.Function")
    class CoinGet(object):
        @JOverride
        def apply(self, o):
            return JObject(JLong(COINS[0]), JClass("java.lang.Long"))

    @JImplements("java.util.function.Function")
    class CoinTake(object):
        @JOverride
        def apply(self, o):
            COINS[0] -= int(o[1])
            return JObject(True, JClass("java.lang.Boolean"))

    @JImplements("java.util.function.Function")
    class CoinAdd(object):
        @JOverride
        def apply(self, o):
            COINS[0] += int(o[1])
            return JObject(JLong(COINS[0]), JClass("java.lang.Long"))
    br = Gear.bridge()
    br.put("skill:fn:addxp", AddXp())
    br.put("coins:fn:get", CoinGet())
    br.put("coins:fn:take", CoinTake())
    br.put("coins:fn:add", CoinAdd())

    def stack(iid, q=1):
        return IS(iid, JInt(q))

    def rolled(iid, r, lvl=None):
        L_ = int(Roll.craftLevel(iid, U1)) if lvl is None else lvl
        return Roll.newDoc(iid, JInt(r), True, "craft", JInt(L_))

    def gear(iid, d, q=1):
        s_ = stack(iid, q)
        return s_ if d is None else Data.put(s_, d, None)

    def mods_of(d):
        return [(str(m.asDocument().getString("s").getValue()), int(m.asDocument().getInt32("v").getValue())) for m in Data.mods(d)]

    def rid_of(d):
        return str(Defs.R_ID[int(Data.rarity(d))])

    # ============================================================================ T: the ladder table
    K.check(bool(Up.okId("Weapon_Wand_SoulOrb")) and bool(Up.okId("a-b_9")) and not bool(Up.okId("a b")) and not bool(Up.okId(""))
            and not bool(Up.okId(None)) and not bool(Up.okId("x" * 121)) and not bool(Up.okId("a(b")), "T: okId")
    pc1 = Up.parseCost("Ingredient_Bar_Iron*6 + Ingredient_Fire_Essence*15+Ingredient_Bar_Iron", "A", "B")
    pc_bad = [str(Up.parseCost(c_, "A", "B")) for c_ in ("", "X*", "X*0", "X*10000", "a b*2", "A*2", "X*2++Y")]
    K.check(list(pc1[0]) == ["Ingredient_Bar_Iron", "Ingredient_Fire_Essence"] and list(pc1[1]) == [7, 15] and str(pc1[2]) == "row"
            and "empty material" in pc_bad[0] and "whole number" in pc_bad[1] and "1 to 9999" in pc_bad[2] and "1 to 9999" in pc_bad[3]
            and "not an item id" in pc_bad[4] and "its own upgrade" in pc_bad[5] and "empty material" in pc_bad[6],
            "T: parseCost: 'Bar_Iron*6 + Fire*15 + Bar_Iron' = Bar_Iron 7, Fire 15; refusals %s" % pc_bad)
    pd = Up.parse(LADDER_DEF)
    K.check(len(pd[0]) == 7 and list(pd[0]) == SOUL[:-1] and list(pd[1]) == SOUL[1:] and pd[2] is None and all(x is None for x in pd[3])
            and list(pd[4]) == ["up"] * 7, "T: parse(default) = 7 'up' steps Orb -> Copper -> ... -> Onyxium, every cost read from the recipes")
    pw = Up.parse(" A>B(Ing_X*2+Ing_Y) > C , D>E ")
    K.check(list(pw[0]) == ["A", "B", "D"] and list(pw[1]) == ["B", "C", "E"] and pw[2] is None and list(pw[3][0][0]) == ["Ing_X", "Ing_Y"]
            and list(pw[3][0][1]) == [2, 1] and pw[3][1] is None and pw[3][2] is None,
            "T: parse: 'A>B(Ing_X*2+Ing_Y)>C, D>E' = 3 steps; the written cost belongs to A -> B only")
    bads = {
        "convert": ("A~B", "convert row"), "first": ("A(X*1)>B", "starts its row"), "badid": ("A>B c>D", "not an item id"),
        "single": ("A", "at least two"), "twice": ("A>B,A>C", "two ladders"), "loop": ("A>B>A", "a loop"), "self": ("A>A", "into itself"),
        "paren": ("A>B(X*1", "closing )"), "amount": ("A>B(X*0)", "1 to 9999"),
    }
    got = {}
    for k_, (txt, want) in bads.items():
        r_ = Up.parse(txt)
        got[k_] = (str(r_[2]), [str(x) for x in r_[0]])
    bad_t = [(k_, got[k_]) for k_, (txt, want) in bads.items() if want not in got[k_][0]]
    K.check(not bad_t and got["twice"][1] == ["A"] and got["badid"][1] == [] and got["amount"][1] == [] and got["convert"][1] == [],
            "T: parse refuses (first problem named, the bad part skipped, the rest kept): %s" % bad_t)
    K.notes.append("table refusals: " + " | ".join("%s: %s" % (k_, got[k_][0]) for k_ in sorted(got)))
    # cur(): a bad part = one WARN + skipped; a loop drops the whole text
    apply(upgrade__ladders="Weapon_Wand_SoulOrb>Weapon_Wand_SoulCage_Copper, Bad id>X")
    c1 = (int(Up.steps()), str(Up.next("Weapon_Wand_SoulOrb")))
    apply(upgrade__ladders="A>B>A")
    c2 = int(Up.steps())
    apply(upgrade__ladders="Weapon_Wand_SoulOrb>Weapon_Wand_SoulCage_Copper(Ingredient_Bar_Copper*2)")
    c3 = (int(Up.writtenSteps()), Up.written("Weapon_Wand_SoulOrb", "Weapon_Wand_SoulCage_Copper"), Up.written("Weapon_Wand_SoulOrb", "X"),
          Up.written("Nope", "X"), int(Up.row("Weapon_Wand_SoulOrb")), int(Up.row(None)), Up.next(None), str(Up.kind("Weapon_Wand_SoulOrb")))
    apply()
    K.check(c1 == (1, SOUL[1]) and c2 == 0 and c3[0] == 1 and list(c3[1][1]) == [2] and c3[2] is None and c3[3] is None and c3[4] == 0
            and c3[5] == -1 and c3[6] is None and c3[7] == "up" and int(Up.steps()) == 7 and int(Up.writtenSteps()) == 0,
            "T: tab(): a bad part skipped (1 step left), a loop drops all (0), a written step is found by written(), row / next / kind")
    # fix round (critic 2): the table is ONE immutable snapshot behind ONE volatile field - unchanged text = the same snapshot; a change
    # publishes a NEW array and never touches the old one (a reader holding the old snapshot keeps a consistent from / to / cost)
    tb0 = Up.tab()
    tb0b = Up.tab()
    old_from, old_to = [str(x) for x in tb0[0]], [str(x) for x in tb0[1]]
    apply(upgrade__ladders="Weapon_Wand_SoulOrb>Weapon_Wand_SoulCage_Iron(Ingredient_Bar_Iron*2)")
    tb1 = Up.tab()
    snap_ok = (tb0.equals(tb0b) and len(tb0) == 5 and not tb1.equals(tb0) and [str(x) for x in tb0[0]] == old_from
               and [str(x) for x in tb0[1]] == old_to and len(old_from) == 7 and [str(x) for x in tb1[1]] == [SOUL[2]]
               and str(Up.next(SOUL[0])) == SOUL[2] and Up.written(SOUL[0], SOUL[1]) is None and Up.written(SOUL[0], SOUL[2]) is not None
               and int(Up.rowIn(tb0, SOUL[3])) == 3 and int(Up.rowIn(tb1, SOUL[3])) == -1 and Up.kind("Nope") is None)
    apply()
    K.check(snap_ok and not bool(Up.TAB.equals(tb0)) and int(Up.steps()) == 7,
            "T: fix (critic 2): one snapshot - same text = same array; a live edit publishes a new one and leaves the old one whole")
    ck = [Up.checkLadders("upgrade.ladders", v_) for v_ in (LADDER_DEF, "Weapon_Wand_SoulOrb>Nope_Item", "Nope_Item>Weapon_Wand_SoulOrb",
                                                             "Weapon_Wand_SoulOrb>Weapon_Wand_SoulCage_Copper(Nope_Mat*2)", "A~B",
                                                             "Weapon_Wand_SoulOrb>Weapon_Wand_SoulCage_Copper(Ingredient_Bar_Copper*3)")]
    K.check(ck[0] is None and "no item Nope_Item" in str(ck[1]) and "no item Nope_Item" in str(ck[2]) and "Nope_Mat" in str(ck[3])
            and "a material of" in str(ck[3]) and "convert" in str(ck[4]) and ck[5] is None,
            "T: checkLadders (Server Setup): the default is fine; unknown items / materials and convert rows are refused: %s" % [str(x) for x in ck[1:5]])

    # ============================================================================ R: the costs from SkyyArmory's real recipes
    steps = soul_recipes()
    rbad = []
    for fr_, to_, mats in steps:
        c_ = Up.cost(fr_, to_)
        got_ = None if c_ is None else dict((str(a), int(b)) for a, b in zip(c_[0], c_[1]))
        if got_ != mats or c_ is None or not str(c_[2]):
            rbad.append((to_, got_, mats))
    K.check(not rbad and len(steps) == 7, "R: cost() = the OTHER inputs of SkyyArmory 0.1.20's recipe for each of the 7 cage steps (read from the "
            "live CraftingRecipe store, equal to the jar's JSON): %s" % rbad)
    K.notes.append("cage costs: " + "; ".join("%s %s" % (t_.rsplit("_", 1)[1], str(Up.costText(Up.cost(f_, t_)))) for f_, t_, _m in steps))
    rid0 = str(Up.cost(SOUL[0], SOUL[1])[2])
    K.check(Up.cost(SOUL[1], SOUL[0]) is None and Up.cost("Tool_Pickaxe_Copper", "Tool_Pickaxe_Iron") is None and Up.cost(None, "x") is None
            and str(Up.costText(None)) == "no recipe" and SOUL[1] in rid0,
            "R: no recipe makes the Orb from a cage / an Iron pickaxe from a Copper one (null); recipe id %s" % rid0)
    rc0 = CRR.getAssetMap().getAsset(rid0)
    K.check(Up.fromRecipe(rc0, SOUL[0], SOUL[2]) is None and Up.fromRecipe(rc0, "Weapon_Wand_SoulCage_Iron", SOUL[1]) is None
            and Up.fromRecipe(None, SOUL[0], SOUL[1]) is None and Up.fromRecipe(rc0, SOUL[0], SOUL[1]) is not None,
            "R: fromRecipe: only the recipe's own output + an input of the item counts")
    apply(upgrade__ladders=LADDER_DEF.replace(SOUL[1], SOUL[1] + "(Ingredient_Bar_Iron*3+Ingredient_Stick)", 1))
    cw = Up.cost(SOUL[0], SOUL[1])
    cr = Up.cost(SOUL[1], SOUL[2])
    apply()
    K.check(list(cw[0]) == ["Ingredient_Bar_Iron", "Ingredient_Stick"] and list(cw[1]) == [3, 1] and str(cw[2]) == "row"
            and dict(zip([str(x) for x in cr[0]], [int(x) for x in cr[1]])) == steps[1][2],
            "R: a written cost wins over the recipe for its step only (Orb -> Copper = Bar_Iron 3 + Stick 1; Copper -> Iron still the recipe)")
    n0 = int(Up.COST_N)
    K.check(n0 == int(CRR.getAssetMap().getAssetMap().size()) and Up.COST.size() > 0, "R: the cost cache is keyed to the recipe store size (%d)" % n0)

    # ============================================================================ U: check / docI / preview / upgrade
    WAND = SOUL[1]
    Lc = int(Roll.craftLevel(SOUL[2], U1))
    unread = stack(WAND).withMetadata(JClass("org.bson.BsonDocument")(str(Defs.DOC_KEY), BS("broken")))
    newer = rolled(WAND, 2)
    newer.put("v", BI32(JInt(99)))
    unid = rolled(WAND, 2)
    unid.put("id", BB(False))
    myth = rolled(WAND, 2)
    myth.put("r", BS("mythic"))
    utd = rolled(WAND, 2)
    utd.put("r", BS("untiered"))
    setd = rolled(WAND, 2)
    setd.put("set", BS("mining_copper"))
    cases = [
        ("no next tier", Up.check(gear(SOUL[-1], rolled(SOUL[-1], 2)), U1), "has no next tier"),
        ("not on a ladder", Up.check(stack("Tool_Pickaxe_Iron"), U1), "has no next tier"),
        ("stack", Up.check(stack(WAND, 2), U1), "stack of 2"),
        ("mythic", Up.check(gear(WAND, myth), U1), "special item"),
        ("untiered", Up.check(gear(WAND, utd), U1), "special item"),
        ("set", Up.check(gear(WAND, setd), U1), "special item"),
        ("unidentified", Up.check(gear(WAND, unid), U1), "Identify that item first"),
        ("unreadable", Up.check(unread, U1), "unreadable"),
        ("newer", Up.check(gear(WAND, newer), U1), "newer SkyyGear"),
        ("nothing", Up.check(None, U1), "Pick an item"),
    ]
    apply(part__upgrade="false")
    cases.append(("off", Up.check(stack(WAND), U1), "switched off"))
    apply(gear__mythicItems=WAND)
    cases.append(("mythicItems", Up.check(stack(WAND), U1), "special item"))
    apply(gear__mythicItems=SOUL[2])
    cases.append(("next is mythic", Up.check(stack(WAND), U1), "nothing upgrades into it"))
    apply(upgrade__ladders=WAND + ">Nope_Item")
    cases.append(("next not loaded", Up.check(stack(WAND), U1), "no Nope_Item on this server"))
    apply(upgrade__ladders="Tool_Pickaxe_Copper>Tool_Pickaxe_Iron")
    cases.append(("no recipe", Up.check(stack("Tool_Pickaxe_Copper"), U1), "No recipe makes"))
    apply(upgrade__ladders=WAND + ">" + SOUL[2] + "(Nope_Mat*2)")
    cases.append(("material not loaded", Up.check(stack(WAND), U1), "There is no Nope_Mat"))
    apply()
    bad_c = [(n_, str(c_[0])) for n_, c_, want in cases if c_[0] is None or want not in str(c_[0])]
    ok_r = Up.check(gear(WAND, rolled(WAND, 2)), U1)
    ok_p = Up.check(stack(WAND), U1)
    K.check(not bad_c and ok_r[0] is None and str(ok_r[1]) == SOUL[2] and ok_r[2] is not None and ok_p[0] is None,
            "U: check() refuses every listed case with its words (nothing else); a rolled and a plain cage are fine: %s" % bad_c)
    K.notes.append("refusal words: " + " | ".join("%s: %s" % (n_, str(c_[0])[:70]) for n_, c_, _w in cases))
    # docI: the same rarity + lines, re-levelled
    src_lvl = int(Lvl.clamp(JInt(max(1, Lc - 6))))
    d_src = rolled(WAND, 3, src_lvl)
    d_src.put("rf", BS("Keen"))
    d_src.put("rfN", BI32(JInt(3)))
    d_src.put("lvU", BI32(JInt(2)))
    d_src.put("box", BS("bag"))
    import jpype
    info = jpype.JArray(jpype.JInt)(5)
    nd = Up.docI(gear(WAND, d_src), SOUL[2], U1, JInt(Lc), info)
    a_l, b_l = int(Lvl.level(WAND, d_src)), int(Lvl.level(SOUL[2], nd))
    mo, mn = mods_of(d_src), mods_of(nd)
    fa, fb = float(Lvl.factor(JInt(a_l))), float(Lvl.factor(JInt(b_l)))
    rel_ok = len(mo) == len(mn) and all(k1 == k2 and v2 >= v1 for (k1, v1), (k2, v2) in zip(mo, mn))
    caps_ok = all(v2 <= max(v1, int(Up.capOf(Defs.sIndex(k2), SOUL[2], JInt(3), JInt(b_l)))) for (k1, v1), (k2, v2) in zip(mo, mn))
    K.check(rid_of(nd) == "legendary" and rel_ok and caps_ok and b_l == Lc and str(Data.str(nd, "rf", "")) == "Keen" and int(Data.num(nd, "rfN", 0)) == 3
            and not nd.containsKey("lvU") and not nd.containsKey("box") and str(Data.str(nd, "kind", "")) == str(Data.kindFor(SOUL[2]))
            and int(info[2]) == a_l and int(info[3]) == b_l and int(info[4]) == 2,
            "U: docI: Legendary Lv %d -> Legendary Lv %d (the next tier's craft level), lines %s -> %s (each >= old, <= the cap; factor %.3f -> %.3f), "
            "reforge name + count kept, lvU / box dropped, kind = the next tier's" % (a_l, b_l, mo, mn, fa, fb))
    lt = str(Up.lossText(info))
    K.check("2 bought level ups do not carry over" in lt and str(Up.lossText(jpype.JArray(jpype.JInt)(5))) == "",
            "U: lossText: '%s'; nothing lost = ''" % lt)
    hi_doc = rolled(WAND, 3, int(Lvl.clamp(JInt(Lc + 12))))
    info2 = jpype.JArray(jpype.JInt)(5)
    Up.docI(gear(WAND, hi_doc), SOUL[2], U1, JInt(Lc), info2)
    lt2 = str(Up.lossText(info2))
    cap_v = int(Up.capOf(Defs.sIndex(mo[0][0]), SOUL[2], JInt(3), JInt(Lc)))
    rv = int(Up.relevel(JInt(cap_v + 40), Defs.sIndex(mo[0][0]), SOUL[2], JInt(3), JInt(a_l), JInt(b_l), info2))
    K.check((int(info2[3]) >= int(info2[2]) or "it becomes Lv" in lt2) and rv == cap_v + 40,
            "U: a higher-level item made at a lower level is warned ('%s'); a line already above the cap keeps its value (%d)" % (lt2, rv))
    # plain -> the craft roll
    seen = {}
    for _i in range(200):
        dd = Up.docI(stack(WAND), SOUL[2], U1, JInt(Lc), jpype.JArray(jpype.JInt)(5))
        k_ = rid_of(dd)
        if int(Data.rarity(dd)) > 4 or not bool(Data.identified(dd)) or int(Lvl.level(SOUL[2], dd)) != Lc:
            k_ = "bad"
        seen[k_] = seen.get(k_, 0) + 1
    K.check("bad" not in seen and len(seen) >= 2 and seen.get("normal", 0) > 50,
            "U: a PLAIN cage upgrades to the normal craft roll of the next tier (GearRoll.craftDoc: never Mythic/Set/UT, Lv %d), 200 rolls: %s" % (Lc, seen))
    K.notes.append("plain upgrade rarity spread (200): %s" % seen)
    pv_r = Up.preview(gear(WAND, d_src), U1)
    pv_p = Up.preview(stack(WAND), U1)
    pv_x = Up.preview(gear(WAND, myth), U1)
    K.check(pv_r[0] is None and str(pv_r[1]) == SOUL[2] and pv_r[2] is not None and not bool(pv_r[3]) and int(pv_r[4]) == Lc and "bought level up" in str(pv_r[5])
            and pv_p[0] is None and pv_p[2] is None and bool(pv_p[3]) and str(pv_p[5]) == "" and "special" in str(pv_x[0]) and pv_r[6] is not None,
            "U: preview(): rolled = the new document + the note; plain = 'rolls'; refused = the words")

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

    def disk():
        if not os.path.isfile(GLF):
            return []
        with open(GLF, encoding="utf-8") as f_:
            t_ = f_.read()
        os.remove(GLF)
        return [l_ for l_ in t_.split("\n") if l_.strip()]

    def logs():
        return disk() + [l_ for l_ in str(Log.take()).split("\n") if l_.strip()]
    Log.FILE = JClass("java.nio.file.Paths").get(GLF)
    logs()
    # fix round (critic 1, inherited 0.2.21): GearLog.flush waits for a write in flight. A stand-in "scheduler" thread takes the queue
    # under WLOCK (as run() -> flush() now does) and writes it 0.4 s later; the world thread's flush() must not return before the line is
    # on disk (0.2.21's flush found the queue empty and returned at once)
    import threading, time
    from jpype import synchronized as _jsync
    took = threading.Event()

    def sched_():
        with _jsync(Log.WLOCK):
            t_ = Log.take()
            took.set()
            time.sleep(0.4)
            Log.write(Log.FILE, t_)
    Log.line("FLUSHTEST in flight")
    th_ = threading.Thread(target=sched_)
    th_.start()
    took.wait(5)
    t0_ = time.time()
    Log.flush()
    dt_ = time.time() - t0_
    on_disk = os.path.isfile(GLF) and "FLUSHTEST in flight" in open(GLF, encoding="utf-8").read()
    th_.join(5)
    Log.line("FLUSHTEST direct")
    Log.flush()
    direct = os.path.isfile(GLF) and "FLUSHTEST direct" in open(GLF, encoding="utf-8").read()
    K.check(on_disk and direct and dt_ >= 0.3, "U: fix (critic 1): GearLog.flush() returned only after the line another thread had taken was "
            "on disk (waited %.2f s); a plain line + flush is on disk at once" % dt_)
    logs()

    def put_mats(cs_, mats, sec="storage", start=0):
        i_ = start
        for m_, q_ in mats.items():
            cs_[sec].setItemStackForSlot(JShort(i_), stack(m_, q_))
            i_ += 1

    # U1: EVERY Soul Cage tier, rolled and plain, the whole ladder on ONE item each (it stays in hotbar 0)
    xp0 = XP[0]
    for kind_ in ("rolled", "plain"):
        inv, cs = mkinv()
        first = gear(SOUL[0], rolled(SOUL[0], 2)) if kind_ == "rolled" else stack(SOUL[0])
        cs["hotbar"].setItemStackForSlot(JShort(0), first)
        r0 = None if kind_ == "plain" else rid_of(Data.effective(first.getItemId(), first.getMetadata()))
        prev_mods = None
        tier_bad = []
        for k_, (fr_, to_, mats) in enumerate(steps):
            # fresh material containers each step: exactly the cost + one extra of the first material in a second stack
            st_ = SIC(JShort(36))
            jf(INV, "storage").set(inv, comp("Storage", st_))
            cs["storage"] = st_
            put_mats(cs, mats)
            m0 = list(mats)[0]
            cs["storage"].setItemStackForSlot(JShort(10), stack(m0, 1))
            it = at(cs, "hotbar", 0)
            fp = str(Forge.fp(it))
            b_ = cnt(inv, [fr_, to_] + list(mats))
            res = Up.upgrade(inv, JInt(0), JInt(0), fr_, fp, U1, "Tester")
            a_ = cnt(inv, [fr_, to_] + list(mats))
            ll = logs()
            nw = at(cs, "hotbar", 0)
            nd_ = Data.effective(nw.getItemId(), nw.getMetadata()) if nw is not None else None
            exp = dict(b_)
            exp[fr_] -= 1
            exp[to_] += 1
            for m_, q_ in mats.items():
                exp[m_] -= q_
            okk = (int(res[0]) == 1 and nw is not None and str(nw.getItemId()) == to_ and int(nw.getQuantity()) == 1 and a_ == exp and nd_ is not None
                   and any(" UPGRADE-BEGIN " in l_ for l_ in ll) and any(" UPGRADE Tester " in l_ for l_ in ll)
                   and not any("UPGRADE-COUNT" in l_ or "UPGRADE-FAILED" in l_ for l_ in ll)
                   and int(Lvl.level(to_, nd_)) == int(Roll.craftLevel(to_, U1)) and at(cs, "storage", 10) is not None)
            if kind_ == "rolled" and nd_ is not None:
                okk = okk and rid_of(nd_) == r0 and len(mods_of(nd_)) == len(prev_mods or mods_of(nd_))
                prev_mods = mods_of(nd_)
            if not okk:
                tier_bad.append((to_, int(res[0]), str(res[1]), b_, a_))
            # the second click with the old fingerprint
            res2 = Up.upgrade(inv, JInt(0), JInt(0), fr_, fp, U1, "Tester")
            if int(res2[0]) != 0 or "moved or changed" not in str(res2[1]) or cnt(inv, [fr_, to_] + list(mats)) != a_:
                tier_bad.append((to_, "second click", str(res2[1])))
            logs()
        final = at(cs, "hotbar", 0)
        K.check(not tier_bad and final is not None and str(final.getItemId()) == SOUL[-1],
                "U: %s: the WHOLE ladder Orb -> Copper -> ... -> Onyxium on ONE item in hotbar 1: every step takes exactly its recipe's "
                "materials (the extra stack stays), the item changes in place (one item, never a copy)%s, Lv = the next tier's craft level, a "
                "second click is refused: %s" % (kind_, ", rarity %s and the line count kept" % r0 if r0 else "", tier_bad[:3]))
    K.check(XP[0] == xp0, "U: no upgrade paid Smithing XP (skill:fn:addxp calls %d)" % (XP[0] - xp0))

    # U2: storage first, then backpack, then hotbar; partial stacks; documented stacks never used; the item's own slot never a material
    fr_, to_, mats = steps[1]
    bar, ess = [m for m in mats if "Bar" in m][0], [m for m in mats if "Bar" not in m][0]
    inv, cs = mkinv()
    d2 = rolled(fr_, 1)
    cs["hotbar"].setItemStackForSlot(JShort(4), gear(fr_, d2))
    cs["hotbar"].setItemStackForSlot(JShort(0), stack(bar, 50))
    cs["backpack"].setItemStackForSlot(JShort(2), stack(bar, mats[bar] - 2))
    cs["storage"].setItemStackForSlot(JShort(7), stack(bar, 1))
    doc_bar = stack(bar, 5).withMetadata(JClass("org.bson.BsonDocument")(str(Defs.DOC_KEY), BS("x")))
    cs["storage"].setItemStackForSlot(JShort(1), doc_bar)
    cs["storage"].setItemStackForSlot(JShort(3), stack(ess, mats[ess] + 4))
    hv = int(Up.have(inv, bar))
    K.check(hv == 50 + mats[bar] - 2 + 1 and not bool(Up.usable(doc_bar, bar)) and bool(Up.usable(stack(bar), bar)) and len(Up.matSecs(inv)) == 3
            and len(Up.matSecs(None)) == 0, "U: have() counts storage + backpack + hotbar, never a stack with a document (%d)" % hv)
    res = Up.upgrade(inv, JInt(0), JInt(4), fr_, str(Forge.fp(at(cs, "hotbar", 4))), U1, "Tester")
    ll = logs()
    K.check(int(res[0]) == 1 and at(cs, "storage", 7) is None and at(cs, "backpack", 2) is None and int(at(cs, "hotbar", 0).getQuantity()) == 49
            and int(at(cs, "storage", 1).getQuantity()) == 5 and int(at(cs, "storage", 3).getQuantity()) == 4 and str(at(cs, "hotbar", 4).getItemId()) == to_
            and any("@Inventory 8" in l_ and "@Backpack 3" in l_ and "@Hotbar 1" in l_ for l_ in ll if " UPGRADE-BEGIN " in l_),
            "U: storage first: Inventory 8 (1) -> Backpack 3 (%d) -> Hotbar 1 (1 of 50); the documented bar stack and the rest stay; the "
            "plan is in UPGRADE-BEGIN" % (mats[bar] - 2))
    # U3: short materials + where / rows
    inv, cs = mkinv()
    cs["hotbar"].setItemStackForSlot(JShort(0), gear(fr_, rolled(fr_, 1)))
    cs["storage"].setItemStackForSlot(JShort(0), stack(bar, mats[bar] - 3))
    cs["storage"].setItemStackForSlot(JShort(1), stack(ess, mats[ess]))
    cs["backpack"].setItemStackForSlot(JShort(5), stack(SOUL[0]))
    cs["armor"].setItemStackForSlot(JShort(0), stack("Armor_Iron_Head"))
    b3 = cnt(inv, [fr_, to_, bar, ess])
    sh = str(Up.shortOf(inv, Up.cost(fr_, to_)))
    res = Up.upgrade(inv, JInt(0), JInt(0), fr_, str(Forge.fp(at(cs, "hotbar", 0))), U1, "Tester")
    rws = sorted(tuple(x) for x in Up.rows(inv))
    K.check(int(res[0]) == 0 and ("You need 3 more" in str(res[1])) and ("(you have %d of %d)" % (mats[bar] - 3, mats[bar])) in sh
            and cnt(inv, [fr_, to_, bar, ess]) == b3 and not logs() and rws == [(0, 0), (2, 5)] and Up.shortOf(inv, None) is not None
            and len(Up.rows(None)) == 0, "U: short materials: '%s' - nothing moved, nothing logged; rows() = every item with a next tier (%s)" % (sh, rws))
    # U4: a FULL inventory (every slot filled) - nothing new needs a free slot
    inv, cs = mkinv()
    for sec_, n_ in (("hotbar", 9), ("storage", 36), ("backpack", 9)):
        for i_ in range(n_):
            cs[sec_].setItemStackForSlot(JShort(i_), stack("Ingredient_Stick", 3))
    cs["hotbar"].setItemStackForSlot(JShort(2), gear(fr_, rolled(fr_, 2)))
    cs["storage"].setItemStackForSlot(JShort(20), stack(bar, mats[bar]))
    cs["storage"].setItemStackForSlot(JShort(21), stack(ess, mats[ess]))
    b4 = cnt(inv, [fr_, to_, bar, ess, "Ingredient_Stick"])
    res = Up.upgrade(inv, JInt(0), JInt(2), fr_, str(Forge.fp(at(cs, "hotbar", 2))), U1, "Tester")
    a4 = cnt(inv, [fr_, to_, bar, ess, "Ingredient_Stick"])
    logs()
    K.check(int(res[0]) == 1 and a4 == {fr_: b4[fr_] - 1, to_: b4[to_] + 1, bar: 0, ess: 0, "Ingredient_Stick": b4["Ingredient_Stick"]},
            "U: a FULL inventory (all 54 slots taken): the upgrade works in place, counts %s -> %s" % (b4, a4))

    def setup(fail=(), item_sec="hotbar", mat_sec="storage", doc=None):
        inv_, cs_ = mkinv(fail)
        cs_[item_sec].setItemStackForSlot(JShort(0), gear(fr_, doc if doc is not None else rolled(fr_, 2)))
        cs_[mat_sec].setItemStackForSlot(JShort(3), stack(bar, mats[bar]))
        cs_[mat_sec].setItemStackForSlot(JShort(4), stack(ess, mats[ess]))
        return inv_, cs_
    sec_i = {"hotbar": 0, "storage": 1}
    ids4 = [fr_, to_, bar, ess]
    # U5: a CRASH between (a) materials taken and (b) the item written: the item is the OLD one, the materials are gone (logged), no copy
    inv, cs = setup()
    fp5 = str(Forge.fp(at(cs, "hotbar", 0)))
    b5 = cnt(inv, ids4)
    Up.CRASH_AT = 1
    crashed = False
    try:
        Up.upgrade(inv, JInt(0), JInt(0), fr_, fp5, U1, "Tester")
    except Exception as ex:
        crashed = "a crash right after the materials left" in str(ex)
    finally:
        Up.CRASH_AT = 0
    a5 = cnt(inv, ids4)
    l5 = disk()
    K.check(crashed and a5 == {fr_: 1, to_: 0, bar: 0, ess: 0} and str(Forge.fp(at(cs, "hotbar", 0))) == fp5
            and any(" UPGRADE-BEGIN " in l_ and bar in l_ and ess in l_ for l_ in l5),
            "U: a CRASH between the steps: the old item stays (same fingerprint), no next-tier item appears (no dupe), the materials are "
            "lost but UPGRADE-BEGIN on disk lists them (%s -> %s)" % (b5, a5))
    Log.take()
    # U6: failure at (b): the item's slot refuses the next tier -> every material back, nothing used
    inv, cs = setup(fail=("hotbar",))
    cs["hotbar"].refuseId = to_
    b6 = cnt(inv, ids4)
    fp6 = str(Forge.fp(at(cs, "hotbar", 0)))
    res = Up.upgrade(inv, JInt(0), JInt(0), fr_, fp6, U1, "Tester")
    l6 = logs()
    K.check(int(res[0]) == -1 and "nothing was used" in str(res[1]) and cnt(inv, ids4) == b6 and str(Forge.fp(at(cs, "hotbar", 0))) == fp6
            and any("UPGRADE-FAILED" in l_ and "RESTORED" in l_ for l_ in l6), "U: failure at (b): the materials are put back, the item stays, UPGRADE-FAILED ... RESTORED")
    # U7: failure at (a): a remove that throws (slot unchanged), and a remove that empties then throws (put back)
    inv, cs = setup(fail=("storage",))
    cs["storage"].rm = 1
    b7 = cnt(inv, ids4)
    r7a = Up.upgrade(inv, JInt(0), JInt(0), fr_, str(Forge.fp(at(cs, "hotbar", 0))), U1, "Tester")
    l7a = logs()
    cs["storage"].rm = 2
    r7b = Up.upgrade(inv, JInt(0), JInt(0), fr_, str(Forge.fp(at(cs, "hotbar", 0))), U1, "Tester")
    l7b = logs()
    K.check(int(r7a[0]) == -1 and int(r7b[0]) == -1 and cnt(inv, ids4) == b7 and any("materials not taken" in l_ for l_ in l7a)
            and any("materials not taken" in l_ for l_ in l7b), "U: failure at (a) both ways: everything back, counts %s" % (cnt(inv, ids4),))
    # U7b: a partial stack whose rest cannot be written (setItemStackForSlot of the rest throws) -> put back
    inv, cs = setup(fail=("storage",))
    cs["storage"].setItemStackForSlot(JShort(3), stack(bar, mats[bar] + 5))
    cs["storage"].refuseQty = 5
    b7c = cnt(inv, ids4)
    r7c = Up.upgrade(inv, JInt(0), JInt(0), fr_, str(Forge.fp(at(cs, "hotbar", 0))), U1, "Tester")
    logs()
    K.check(int(r7c[0]) == -1 and cnt(inv, ids4) == b7c, "U: a partial material stack that cannot be written: refused, nothing used")
    # U8: the restore fails too -> the materials are LOST but logged, the item stays, never a copy
    inv, cs = setup(fail=("storage",), item_sec="storage", mat_sec="storage")
    cs["storage"].refuseId = to_
    cs["storage"].sticky = True
    r8 = Up.upgrade(inv, JInt(1), JInt(0), fr_, str(Forge.fp(at(cs, "storage", 0))), U1, "Tester")
    l8 = logs()
    c8 = cnt(inv, ids4)
    K.check(int(r8[0]) == -1 and "admin can find" in str(r8[1]) and c8[to_] == 0 and c8[fr_] == 1
            and any(" UPGRADE-RESTORE-FAILED " in l_ for l_ in l8) and any(" UPGRADE-BEGIN " in l_ for l_ in l8),
            "U: the worst case (restore refused): materials lost but logged twice (UPGRADE-BEGIN + UPGRADE-RESTORE-FAILED), no copy: %s" % c8)
    # U8b: failure at (a) with the restore refused
    inv, cs = setup(fail=("storage",))
    cs["storage"].rm = 2
    cs["storage"].refuseId = bar
    r8b = Up.upgrade(inv, JInt(0), JInt(0), fr_, str(Forge.fp(at(cs, "hotbar", 0))), U1, "Tester")
    l8b = logs()
    K.check(int(r8b[0]) == -1 and "could not be put back" in str(r8b[1]) and cnt(inv, ids4)[to_] == 0 and cnt(inv, ids4)[fr_] == 1
            and any(" UPGRADE-RESTORE-FAILED " in l_ for l_ in l8b), "U: failure at (a) + restore refused: logged, the item stays, no copy")
    # U9: the bookkeeping throws -> still made, moved exactly once
    inv, cs = setup()
    b9 = cnt(inv, ids4)
    Up.AFTER_THROWS = True
    try:
        r9 = Up.upgrade(inv, JInt(0), JInt(0), fr_, str(Forge.fp(at(cs, "hotbar", 0))), U1, "Tester")
    finally:
        Up.AFTER_THROWS = False
    l9 = logs()
    K.check(int(r9[0]) == 1 and cnt(inv, ids4) == {fr_: b9[fr_] - 1, to_: b9[to_] + 1, bar: 0, ess: 0} and not any(" UPGRADE Tester " in l_ for l_ in l9),
            "U: after() throws -> made (1), moved once, no UPGRADE line")
    # U10: refused through upgrade(): Mythic / UT / unidentified / bad section / changed item - nothing moves
    rf_bad = []
    for nm_, dd in (("mythic", myth), ("untiered", utd), ("unidentified", unid)):
        dd2 = dd.clone()
        inv, cs = setup(doc=dd2)
        bq = cnt(inv, ids4)
        rr = Up.upgrade(inv, JInt(0), JInt(0), fr_, str(Forge.fp(at(cs, "hotbar", 0))), U1, "Tester")
        if int(rr[0]) != 0 or cnt(inv, ids4) != bq:
            rf_bad.append((nm_, str(rr[1])))
    inv, cs = setup()
    bq = cnt(inv, ids4)
    rs = Up.upgrade(inv, JInt(9), JInt(0), fr_, "x", U1, "Tester")
    rc = Up.upgrade(inv, JInt(0), JInt(0), fr_, "wrong-fp", U1, "Tester")
    K.check(not rf_bad and int(rs[0]) == 0 and int(rc[0]) == 0 and "moved or changed" in str(rc[1]) and cnt(inv, ids4) == bq and not logs(),
            "U: upgrade() refuses Mythic / Untiered / unidentified, a bad section and a changed item - nothing moves, nothing logged: %s" % rf_bad)
    # U11: a written-cost row (a boss-drop upgrade later) works the same
    apply(upgrade__ladders=fr_ + ">" + to_ + "(Ingredient_Stick*2)")
    inv, cs = mkinv()
    cs["hotbar"].setItemStackForSlot(JShort(0), gear(fr_, rolled(fr_, 2)))
    cs["storage"].setItemStackForSlot(JShort(0), stack("Ingredient_Stick", 3))
    r11 = Up.upgrade(inv, JInt(0), JInt(0), fr_, str(Forge.fp(at(cs, "hotbar", 0))), U1, "Tester")
    st11 = str(Up.statusText())
    apply()
    logs()
    K.check(int(r11[0]) == 1 and int(at(cs, "storage", 0).getQuantity()) == 1 and "1 written" in st11,
            "U: a written-cost row: 2 sticks taken, the cage upgraded; statusText '%s'" % st11)
    st0 = str(Up.statusText())
    apply(part__upgrade="false")
    st_off = str(Up.statusText())
    apply()
    K.check("7 step(s): 7 cost(s) from the recipes, 0 written" in st0 and "end with [Lv N]" in st0 and "OFF (part.upgrade)" in st_off,
            "U: statusText: '%s' / off '%s'" % (st0, st_off))
    K.check(str(Up.where(Up.matSecs(inv), Up.matSecs(inv)[0], JInt(2))) == "Inventory 3" and "special item" in str(Up.special(WAND))
            and str(Up.restore(HAL(), JInt(0), Up.matSecs(inv))) == "", "U: where / special / restore() of nothing")

    # ============================================================================ N: the level in names
    def flat(msg):
        segs = []

        def walk(fm, col):
            c = str(fm.color) if fm.color is not None else col
            if fm.rawText is not None:
                segs.append((str(fm.rawText), c))
            elif fm.messageId is not None:
                segs.append(("<%s>" % fm.messageId, c))
            if fm.children is not None:
                for ch in fm.children:
                    walk(ch, c)
        walk(msg.getFormattedMessage(), None)
        return segs

    def name_of(iid, d):
        return "".join(t_ for t_, c_ in flat(View.nameMsg(iid, d, "#abcdef"))), set(c_ for t_, c_ in flat(View.nameMsg(iid, d, "#abcdef")) if t_.strip())
    fams = [("weapon", "Weapon_Sword_Iron"), ("armor", "Armor_Iron_Chest"), ("tool", "Tool_Pickaxe_Iron"), ("wand", SOUL[2])]
    if have_mt:
        fams.append(("multitool", MULTI_PRE + "Iron"))
    nbad = []
    for fam, iid in fams:
        d_ = rolled(iid, 2)
        d_.put("rf", BS("Keen"))
        nm, cols = name_of(iid, d_)
        lv = int(Lvl.level(iid, d_))
        if not nm.endswith(" [Lv %d]" % lv) or not nm.startswith("Keen ") or cols != {"#abcdef"} or str(View.lvTag(iid, d_)) != " [Lv %d]" % lv:
            nbad.append((fam, nm, cols))
    K.check(not nbad, "N: every family's name ends with ' [Lv N]', keeps the reforge prefix and the rarity colour (%s): %s" % ([f for f, _i in fams], nbad))
    du = rolled("Weapon_Sword_Iron", 2)
    du.put("id", BB(False))
    nu, _c = name_of("Weapon_Sword_Iron", du)
    K.check(nu.startswith("Unidentified ") and nu.endswith(" [Lv %d]" % int(Lvl.level("Weapon_Sword_Iron", du))) and str(View.lvTag(None, du)) == "" and str(View.lvTag("x", None)) == "",
            "N: an unidentified ITEM shows its one fixed level: '%s'" % nu)
    bag = Unid.make(JInt(0), JInt(0), JInt(2), JInt(5), JInt(9), "test", "test", JInt(1))
    bag1 = Unid.make(JInt(0), JInt(0), JInt(2), JInt(7), JInt(7), "test", "test", JInt(1))

    def disp_name(s_):
        md = s_.getMetadata()
        return str(md.toJson()) if md is not None else ""
    bt, bt1 = disp_name(bag), disp_name(bag1)
    K.check("[Lv 5-9]" in bt and "[Lv 7]" in bt1 and "[Lv 7-7]" not in bt1 and str(Unid.lvTag(Unid.doc(bag))) == " [Lv 5-9]" and str(Unid.lvTag(None)) == "",
            "N: a mystery bag shows its range ' [Lv 5-9]' (' [Lv 7]' when lo = hi)")
    d_sw = rolled("Weapon_Sword_Iron", 2)
    T1, C1 = HAL(), HAL()
    View.statLines("Weapon_Sword_Iron", d_sw, T1, C1)
    sig_on = str(View.sig("Weapon_Sword_Iron", JInt(0), d_sw, T1, C1))
    apply(view__levelInName="false")
    nm_off, _c = name_of("Weapon_Sword_Iron", d_sw)
    sig_off = str(View.sig("Weapon_Sword_Iron", JInt(0), d_sw, T1, C1))
    bag_off = Unid.view(bag, Unid.doc(bag))
    re_off = Unid.reView(bag)
    re_off2 = Unid.reView(re_off)
    apply()
    re_on = Unid.reView(re_off)
    re_on2 = Unid.reView(re_on)
    via_stamp = Stamp.stampStack(re_off, U1, None)
    K.check("[Lv" not in nm_off and sig_on != sig_off and sig_on.endswith(":n1") and sig_off.endswith(":n0") and "[Lv" not in disp_name(bag_off)
            and "[Lv" not in disp_name(re_off) and re_off2.equals(re_off) and "[Lv 5-9]" in disp_name(re_on) and re_on2.equals(re_on)
            and "[Lv 5-9]" in disp_name(via_stamp) and str(Unid.doc(re_on).toJson()) == str(Unid.doc(bag).toJson()),
            "N: view.levelInName off = no suffix + another sig (every stack re-renders once); a bag re-renders through stampStack "
            "(GearUnid.reView) to the new name ONCE (a second pass returns the same stack) and its bag data never changes")

    # ============================================================================ P: the Reforge page (tabs + Upgrade mode) and /upgrade
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

    def anvil_h(ub_):
        """the summed Anchor heights of the right column's own rows (#SkyyGAnvil children)"""
        tot = 0
        for c_ in ub_.getCommands():
            vals = {}
            for f_ in ("selector", "data", "text"):
                try:
                    v_ = getattr(c_, f_)
                    vals[f_] = None if v_ is None else str(v_)
                except Exception:
                    vals[f_] = None
            sel_ = vals["selector"]
            dat = vals["text"] if vals["text"] and "Anchor" in vals["text"] else (vals["data"] or "")
            if sel_ != "#SkyyGAnvil":
                continue
            m_ = re.match(r"^\s*\w+[^{]*\{\s*Anchor: \(([^)]*)\)", dat)
            if m_:
                h_ = re.search(r"Height: (\d+)", m_.group(1))
                tot += int(h_.group(1)) if h_ else 0
        if tot == 0:
            smp = []
            for c_ in ub_.getCommands():
                smp.append(dict((f_, str(getattr(c_, f_, None))[:90]) for f_ in ("type", "selector", "data", "text")))
            K.notes.append("anvil_h found no rows: %s" % smp[5:9])
        return tot
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

    def render(pg_, ref_, st_):
        ub_, ue_ = UCB(), UEB()
        pg_.build(ref_, ub_, ue_, st_)
        return uitext(ub_) + chr(10) + evtext(ue_), anvil_h(ub_)
    fr_, to_, mats = steps[1]          # Copper cage -> Iron cage
    inv, cs = mkinv()
    cage = gear(fr_, rolled(fr_, 2))
    cs["hotbar"].setItemStackForSlot(JShort(0), cage)
    cs["hotbar"].setItemStackForSlot(JShort(1), gear("Weapon_Sword_Iron", rolled("Weapon_Sword_Iron", 1)))
    cs["storage"].setItemStackForSlot(JShort(0), stack(bar, mats[bar] * 2))
    cs["storage"].setItemStackForSlot(JShort(1), stack(ess, mats[ess] * 2))
    cs["backpack"].setItemStackForSlot(JShort(0), stack(SOUL[0]))
    ref, st = world(inv)
    pg = FRP(prx)
    pg.preselect(inv)
    s0, h0 = render(pg, ref, st)
    tabs3 = "SkyyGTab0" in s0 and "SkyyGTab1" in s0 and ("SkyyGTab2" in s0) == have_mt and "mode:1" in s0 and "Reforge" in s0 and "Upgrade" in s0
    K.check(int(pg.mode) == 0 and tabs3 and "Your gear (3)" in s0 and "Current modifiers" in s0 and "SkyyGAnvilT" not in s0 and h0 <= 674,
            "P: /reforge opens on the Reforge tab (Reforge | Upgrade%s), the held cage on the anvil, 'Your gear (3)'; the right column "
            "uses %d of 674 px %s" % (" | Multitool" if have_mt else "", h0, (int(pg.mode), tabs3, "Your gear (3)" in s0, "Current modifiers" in s0,
                                          "SkyyGAnvilT" not in s0, 0)))
    pg.handleDataEvent(ref, st, '{"a":"mode:1"}')
    s1, h1 = render(pg, ref, st)
    K.check(int(pg.mode) == 1 and int(pg.selSec) == 0 and int(pg.selSlot) == 0 and "Upgradable items (2)" in s1 and "Next tier: " in s1
            and "It will have" in s1 and "SkyyGBtnUp" in s1 and "Cannot upgrade" not in s1 and ("%d / %d" % (mats[bar] * 2, mats[bar])) in s1
            and "SkyyGMat1" in s1 and h1 <= 674 and "(on the anvil)" in s1,
            "P: the Upgrade tab keeps the cage on the anvil: 'Upgradable items (2)', 'Next tier: ...', have / need '%d / %d', the lines it will "
            "have, 'Upgrade' on; right column %d of 674 px" % (mats[bar] * 2, mats[bar], h1))
    # stale reforge clicks in Upgrade mode do nothing
    fp_before = str(Forge.fp(at(cs, "hotbar", 0)))
    c_before = COINS[0]
    pg.lastForge = JLong(0)
    pg.handleDataEvent(ref, st, '{"a":"forge"}')
    pg.handleDataEvent(ref, st, '{"a":"lvl"}')
    K.check(str(Forge.fp(at(cs, "hotbar", 0))) == fp_before and COINS[0] == c_before, "P: a stale Reforge / Level up click in Upgrade mode does nothing")
    # guards
    br.put("profile:busy:" + str(U1), True)
    pg.lastForge = JLong(0)
    pg.handleDataEvent(ref, st, '{"a":"up"}')
    g_busy = "still loading" in str(pg.info)
    br.remove("profile:busy:" + str(U1))
    pg.lastForge = JLong(JClass("java.lang.System").currentTimeMillis())
    inf0 = str(pg.info)
    pg.upDo(inv)
    g_dbl = str(pg.info) == inf0
    K.check(g_busy and g_dbl and str(at(cs, "hotbar", 0).getItemId()) == fr_, "P: guards: profile:busy refuses, a double click inside 400 ms does nothing")
    # the Upgrade click
    b_p = cnt(inv, [fr_, to_, bar, ess])
    pg.lastForge = JLong(0)
    rb0 = int(pg.rebuilds)
    pg.handleDataEvent(ref, st, '{"a":"up"}')
    s2, h2 = render(pg, ref, st)
    K.check(str(pg.info).startswith("+Upgraded to a Rare ") and str(at(cs, "hotbar", 0).getItemId()) == to_ and int(pg.rebuilds) == rb0 + 1
            and cnt(inv, [fr_, to_, bar, ess]) == {fr_: b_p[fr_] - 1, to_: b_p[to_] + 1, bar: mats[bar], ess: mats[ess]}
            and "Upgraded - it is in the same slot." in s2 and "Its lines" in s2 and "Materials: used up" in s2 and "Click it in the list" in s2
            and str(pg.selId) == to_ and h2 <= 674 and "Cannot upgrade" not in s2,
            "P: 'Upgrade' -> '%s'; the Iron cage is in hotbar 1 and stays on the anvil (Made state: its lines, button 'Upgraded')" % str(pg.info)[:70])
    logs()
    K.notes.append("right column heights (of 674): reforge %d, upgrade preview %d, upgrade made %d" % (h0, h1, h2))
    # fix round (critic 1): a second / late click on the 'Upgraded' state never upgrades again, even with the next step's materials there
    _f2, _t2, mats2 = steps[2]
    for j_, (m_, q_) in enumerate(mats2.items()):
        cs["storage"].setItemStackForSlot(JShort(20 + j_), stack(m_, q_ * 3))
    b_2 = cnt(inv, [to_, _t2] + list(mats2))
    for _k in range(2):
        pg.lastForge = JLong(0)
        pg.handleDataEvent(ref, st, '{"a":"up"}')
    s2b, _h = render(pg, ref, st)
    K.check(str(at(cs, "hotbar", 0).getItemId()) == to_ and cnt(inv, [to_, _t2] + list(mats2)) == b_2 and "Already upgraded" in str(pg.info)
            and pg.upMade is not None and "Upgraded - it is in the same slot." in s2b and not [l_ for l_ in logs() if "UPGRADE" in l_],
            "P: fix (critic 1): two more clicks on the 'Upgraded' state (lastForge cleared, the next step's materials in the bag) change "
            "nothing, log nothing: '%s'" % str(pg.info))
    for j_ in range(len(mats2)):
        cs["storage"].removeItemStackFromSlot(JShort(20 + j_))
    # click it in the list -> its next step (Thorium) preview; the materials are short now
    rws = [tuple(x) for x in pg.rows]
    pg.handleDataEvent(ref, st, '{"a":"sel:%d"}' % rws.index((0, 0)))
    s3, _h = render(pg, ref, st)
    K.check(pg.upMade is None and "Next tier: " in s3 and "You need " in s3 and "Cannot upgrade" in s3, "P: clicking the upgraded cage shows its next tier; short materials -> 'You need ...', 'Cannot upgrade'")
    # a plain Orb from the backpack
    pg.handleDataEvent(ref, st, '{"a":"sel:%d"}' % [tuple(x) for x in pg.rows].index((2, 0)))
    s4, _h = render(pg, ref, st)
    K.check("rolls a rarity" in s4 and "PLAIN" in s4 and "It rolls new lines" in s4, "P: a plain Orb: 'rolls a rarity', 'It rolls new lines for its rarity'")
    # epoch / nothing picked / bad events / refresh / prev / next
    pg.epoch = "old-epoch"
    pg.lastForge = JLong(0)
    pg.upDo(inv)
    g_ep = "profile changed" in str(pg.info) and int(pg.selSec) == -1
    pg.lastForge = JLong(0)
    pg.upDo(inv)
    g_miss = "Pick an item from the list first" in str(pg.info)
    for ev_ in ('{"a":"sel:99"}', '{"a":"sel:x"}', '{"a":""}', '{"a":"prev"}', '{"a":"next"}', '{"a":"mode:x"}', '{"a":"mode:7"}'):
        pg.handleDataEvent(ref, st, ev_)
    pg.handleDataEvent(ref, st, None)
    pg.upMade = JClass("org.bson.BsonDocument")()
    pg.handleDataEvent(ref, st, '{"a":"refresh"}')
    K.check(g_ep and g_miss and pg.upMade is None and int(pg.mode) == 1, "P: a profile change clears the pick; Upgrade without a pick refused; bad / paging / refresh events handled")
    s5, _h = render(pg, ref, st)
    K.check("The anvil is empty" in s5 and "Tip: hold the item when you type /upgrade" in s5, "P: the empty Upgrade anvil explains the tab")
    # back to Reforge: pick the sword in Upgrade mode is impossible (no next tier) -> switch, pick + a REAL reforge still works
    pg.handleDataEvent(ref, st, '{"a":"sel:%d"}' % [tuple(x) for x in pg.rows].index((0, 0)))
    pg.handleDataEvent(ref, st, '{"a":"mode:0"}')
    s6, _h = render(pg, ref, st)
    K.check(int(pg.mode) == 0 and int(pg.selSec) == 0 and int(pg.selSlot) == 0 and "Your gear" in s6 and "Current modifiers" in s6,
            "P: back to the Reforge tab: the cage stays on the anvil (it can be reforged), the gear list is back")
    fp_r = str(Forge.fp(at(cs, "hotbar", 0)))
    pg.lastForge = JLong(0)
    c_r = COINS[0]
    pg.handleDataEvent(ref, st, '{"a":"forge"}')
    s7, _h = render(pg, ref, st)
    K.check(str(pg.info).startswith("+Reforged!") and str(Forge.fp(at(cs, "hotbar", 0))) != fp_r and COINS[0] < c_r and "Before" in s7 and "After" in s7,
            "P: the REFORGE still works after the tab switches: '%s' (coins %d -> %d)" % (str(pg.info)[:60], c_r, COINS[0]))
    logs()
    pg.handleDataEvent(ref, st, '{"a":"up"}')
    K.check(str(at(cs, "hotbar", 0).getItemId()) == to_, "P: a stale Upgrade click in Reforge mode does nothing")
    # switching to Upgrade with the sword on the anvil drops it (no next tier), and the Multitool tab
    pg.handleDataEvent(ref, st, '{"a":"sel:%d"}' % [tuple(x) for x in pg.rows].index((0, 1)))
    pg.handleDataEvent(ref, st, '{"a":"mode:1"}')
    m_sw = int(pg.mode) == 1 and int(pg.selSec) == -1 and "has no next tier" in str(pg.info)
    pg.handleDataEvent(ref, st, '{"a":"mode:2"}')
    K.check(m_sw and int(pg.mode) == 1, "P: a sword cannot go to the Upgrade tab ('%s'); the Multitool tab opens /multitool through the command "
            "(no command manager here - the page stays)" % str(pg.info))
    pg.setMode(JInt(1), inv)
    # upgrading off: the tab is gone, Upgrade mode falls back to the Reforge build; one tab left = the old 'Anvil' title
    apply(part__upgrade="false")
    s8, _h = render(pg, ref, st)
    pg.handleDataEvent(ref, st, '{"a":"mode:1"}')
    apply(part__upgrade="false", part__multitool="false")
    s9, _h = render(pg, ref, st)
    apply()
    K.check(int(pg.mode) == 0 and "Your gear" in s8 and "SkyyGTab1" not in s8 and "switched off" in str(pg.info) and "SkyyGAnvilT" in s9 and "SkyyGTabs" not in s9,
            "P: part.upgrade off: Upgrade mode falls back to the Reforge page, no Upgrade tab; with one tab left the 'Anvil' title is back")
    K.check(int(Ui.tabs(UCB(), UEB(), "#X", JInt(0), JInt(562), "T")) == (3 if have_mt else 2) and bool(Ui.multiTab()) == have_mt,
            "P: GearUi.tabs / multiTab (%s)" % have_mt)
    # the pager (frames off) in Upgrade mode + the empty list
    inv9, cs9 = mkinv()
    for i_ in range(14):
        cs9["storage"].setItemStackForSlot(JShort(i_), stack(SOUL[0]))
    ref9, st9 = world(inv9)
    pg9 = FRP(prx)
    pg9.mode = 1
    pg9.upPreselect(inv9)
    apply(ui__frames="false")
    s10, _h = render(pg9, ref9, st9)
    apply()
    inv10, _cs10 = mkinv()
    ref10, st10 = world(inv10)
    pg10 = FRP(prx)
    pg10.mode = 1
    s11, _h = render(pg10, ref10, st10)
    K.check("Page 1 / 2" in s10 and "SkyyGBtnNext" in s10 and "Nothing on you has a next tier." in s11 and not bool(pg10.upPick(inv10, JInt(0), JInt(0))),
            "P: without frames the Upgrade list pages (12 a page); the empty list; upPick of an empty slot = false")
    # a moved item is dropped at the next build
    pg11 = FRP(prx)
    pg11.mode = 1
    pg11.upPick(inv9, JInt(1), JInt(3))
    cs9["storage"].setItemStackForSlot(JShort(3), stack("Ingredient_Stick"))
    render(pg11, ref9, st9)
    K.check("moved or changed" in str(pg11.info) and int(pg11.selSec) == -1, "P: an item that moved is taken off the anvil at the next build")
    # the /multitool page: the same tab row (Multitool active) + tab clicks
    if have_mt:
        mp = FMP(prx)
        ub_, ue_ = UCB(), UEB()
        mp.build(ref, ub_, ue_, st)
        sm = uitext(ub_)
        hm = anvil_h(ub_)
        K.check("SkyyGTab0" in sm and "SkyyGTab2" in sm and "SkyyGAnvilT" not in sm and hm <= 674,
                "P: the /multitool page shows the same tab row (right column %d of 674 px)" % hm)
        K.check(bool(mp.tabEvent('{"a":"mode:0"}')) and bool(mp.tabEvent('{"a":"mode:1"}')) and bool(mp.tabEvent('{"a":"mode:2"}'))
                and not bool(mp.tabEvent('{"a":"merge"}')) and not bool(mp.tabEvent(None)),
                "P: the /multitool page's tab clicks are handled (Reforge / Upgrade open through the commands), other clicks fall through")
        mp.handleDataEvent(ref, st, '{"a":"mode:0"}')
    # /upgrade
    UC = P("UpCmd")
    cmd = UC()
    pg_groups = None
    k_ = cmd.getClass()
    while k_ is not None and pg_groups is None:
        for f_ in k_.getDeclaredFields():
            if "ermissionGroups" in str(f_.getName()):
                f_.setAccessible(True)
                pg_groups = f_.get(cmd)
        k_ = k_.getSuperclass()
    K.check(str(cmd.getName()) == "upgrade" and pg_groups is not None and "hytale:Adventurer" in [str(x) for x in pg_groups],
            "P: /upgrade: name 'upgrade', permission group hytale:Adventurer (COMMAND RULES)")
    exe = [m_ for m_ in UC.class_.getDeclaredMethods() if str(m_.getName()) == "execute"][0]
    exe.setAccessible(True)
    said = []
    if FPR is not None:
        apply(part__upgrade="false")
        exe.invoke(cmd, None, st, ref, prx, None)
        apply()
        exe.invoke(cmd, None, st, ref, prx, None)
        said = [str(x) for x in (prx.said or [])]
    K.check(FPR is None or (len(said) >= 2 and "switched off" in said[-2] and "could not open the Reforge page" in said[-1]),
            "P: /upgrade executed: off -> 'switched off'; on -> stamp scan, the Reforge page made on the Upgrade tab + preselected, open "
            "(the stand-in player has no page manager -> the 'could not open' line): %s" % said[-2:])
    pg12 = FRP(prx)
    pg12.mode = 1
    pg12.upPreselect(inv)
    K.check(int(pg12.selSec) == 0 and int(pg12.selSlot) == 0 and str(pg12.selId) == to_, "P: upPreselect puts the held cage on the anvil")
    # fix round (critic 3): a held item that is not on any ladder -> the empty anvil + the reason in the gold info line
    mys = rolled("Weapon_Sword_Iron", 2)
    mys.put("r", BS("mythic"))
    held = [("sword", stack("Weapon_Sword_Iron"), "has no next tier"), ("mythic sword", gear("Weapon_Sword_Iron", mys), "special item"),
            ("bag", Unid.make(JInt(0), JInt(0), JInt(2), JInt(5), JInt(9), "test", "test", JInt(1)), "unidentified loot"), ("empty hand", None, None)]
    why_bad = []
    for nm_, it_, want_ in held:
        invh, csh = mkinv()
        if it_ is not None:
            csh["hotbar"].setItemStackForSlot(JShort(0), it_)
        refh, sth = world(invh)
        pgh = FRP(prx)
        pgh.mode = 1
        pgh.upPreselect(invh)
        sh_, _h = render(pgh, refh, sth)
        inf_ = str(pgh.info)
        ok_ = int(pgh.selSec) == -1 and "The anvil is empty" in sh_ and (inf_ == "" if want_ is None else (inf_.startswith("-") and want_ in inf_ and inf_[1:] in sh_))
        if not ok_:
            why_bad.append((nm_, inf_))
    K.check(not why_bad, "P: fix (critic 3): /upgrade holding a sword / a Mythic sword / a mystery bag opens the empty anvil WITH the reason "
            "(gold info line); an empty hand says nothing: %s" % why_bad)
    K.save(L=Lc)


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
    K.check(set(add) == NEW_CLASSES and not gone, "C: added exactly GearUp / UpCmd, none removed: + %s - %s" % (add, gone))
    want = {
        "GearView": {"+m lvTag", "~m nameMsg", "~m sig"},
        "GearUnid": {"+m lvTag", "~m view", "+m reView"},
        "GearStamp": {"~m stampStack"},
        "GearUi": {"+m multiTab", "+m tabs"},
        "ReforgePage": {"+f mode", "+f upMade", "+f upMadeId", "+m upCol", "+m upPick", "+m upPreselect", "+m setMode", "+m upMats",
                        "+m upAnvil", "+m upList", "+m upBuild", "+m upDo", "+m upEvent", "~m anvil", "~m build", "~m handleDataEvent",
                        "+m upWhyNot"},
        "GearLog": {"+m flushLocked", "~m flush"},          # fix round: take + write under WLOCK
        "MultiPage": {"~m bench", "+m tabEvent", "~m handleDataEvent"},
        "SkyyGearPlugin": {"~m setup"},
    }
    bad = {}
    for k in set(want) | set(diffs):
        if k.startswith("GearCfg") or k.startswith("Cfg") or k == "GearDefs":
            continue          # the config rows (3 new rows: fields, apply, the kit tables) - checked by the start test D and E
        got = set(diffs.get(k, []))
        if got != want.get(k, set()):
            bad[k] = (sorted(want.get(k, set()) - got), sorted(got - want.get(k, set())))
    K.check(not bad, "C: changed exactly the listed members outside the config classes (missing / extra): %s" % bad)
    cfgd = dict((k, v) for k, v in diffs.items() if k.startswith("GearCfg") or k.startswith("Cfg") or k == "GearDefs")
    K.check(all(any(x in " ".join(v) for x in ("UP_ON", "UP_LADDERS", "NAME_LV", "apply", "<clinit>", "defaultsText", "ROW", "check", "KEY", "LBL",
                                                 "HELP", "DEF", "MIN", "MAX", "CAT", "OPTS", "TYPE", "FLAGS", "UNIT", "TARGET", "~m", "+f"))
                for v in cfgd.values()), "C: the config classes changed only for the 3 new rows: %s" % cfgd)
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
        K.check(bool(Cfg.UP_ON) and str(Cfg.UP_LADDERS).startswith("Weapon_Wand_SoulOrb>") and bool(Cfg.NAME_LV),
                "D/new: the live file has no 0.2.22 rows -> the defaults apply (upgrade on, the Soul Cage ladder, level in names)")
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
    for flag, fn in (("--mkfake", lambda: run_mkfake2(arg("--mkfake"))), ("--verify", lambda: H["run_verify"](arg("--out"))),
                     ("--up", lambda: run_up(arg("--out"))),
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
    if os.path.isfile(MT_SRC):
        shutil.copyfile(MT_SRC, MT_JAR)
    else:
        print("note: no Multitools jar - the multitool name / tab checks are skipped")
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.environ["TEMP"] = os.environ["TMP"] = env["TEMP"]
    try:
        run_assets()
        p = child(env, "--mkfake", FAKE_DIR)
        check(p.returncode == 0, "F: the stand-ins were generated")
        for label, flag in (("verify", "--verify"), ("compare", "--compare"), ("up", "--up")):
            out = os.path.join(SCRATCH, "%s.json" % label)
            pr = child(env, flag, "--out", out)
            check(pr.returncode == 0, "%s: the child exited cleanly (%s)" % (label, pr.returncode))
            r = take(out, label)
            if label == "up" and r:
                print("U. Iron Soul Cage craft level %s" % r.get("L"))
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
            check(res["old"]["cfg"] == res["new"]["cfg"], "D: 0.2.22 starts the live copy to exactly the config.properties 0.2.21 writes")
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
