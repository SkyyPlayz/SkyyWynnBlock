"""Harness for SkyyGear 0.3.13 (tools/gear_0_3_13_patch.py header) = the 0.3.12 harness's children run on the 0.3.13 jar + H313 + LIVE313:
    python tools/gear_0_3_13_patch.py && python SkyyGear/build_skyygear_0.3.13.py
    python SkyyGear/test_skyygear_0.3.13.py [--keep] [--only assets,h313,live313,h312,live,h311,h310,h39,verify,h38,h37,g36,snd,till,life,audit]

  S313 the jar 0.3.12 -> 0.3.13: only the 5 new classes are new, nothing gone, changed non-class files = manifest.json only; class compare printed
  H313 ONE booted engine (the 0.3.5 life setup) + SkyyFishing 0.1.7 + SkyyCollections 0.2.20 (the Enchanted Stick; 0.2.19 + a seam when absent)
       + vanilla drop lists + vanilla longswords + SkyyArmory 0.1.29 (the great shields):
       A  THE RULE: normKind / normal(stack) / noCraft - pickaxes, hatchets, hoes, sickles (Wood / Scrap / Rusty too), rods, cans yes; shovels,
          the multitool, the Harvester, weapons no; a lifelong stamp / unreadable gear data = never normal; normal.extraIds; the rows
       B  RECIPES: every normal tool recipe leaves the CraftingRecipe store (shovels / the multitool / SkyyFishing's rods stay); idempotent
       C  DROPS: every vanilla list that can yield a normal tool is filtered (GearNormDrop, inside a GearStick when it has one); 3000 rolls of
          the Goblin Miner list never give the Scrap pickaxe but still give the rest; getAllDrops filtered; normal.off off = the raw containers back
       D  CHESTS: GearNorm.strip takes the plain tools out of a container, keeps the stamped / shovel / multitool / unreadable ones, logs each
       E  THE ONE-TIME REMOVAL: kits first (a fresh profile's plain pickaxe becomes its lifelong one), then every normal stack of the inventory +
          the bags (stand-in sacks:fn:*) + Requip (stand-in wardrobe:fn:list / fetch / gone; a Requip-stamped OUT one reported gone) goes,
          recorded + logged, History copy of the registry first, markers normOff / normOffRq; run twice = no second removal; a crash mid-pass
          resumes from the journal; no room for a Requip item = asked again; the stamped tools survive; UNDO gives every recorded stack back
          once (stamp dropped, durability kept) and the profile is never cleaned again
       F  ENCHANTED STICKS: GearUp.cost adds 2 / 4 / 8 / 16 / 32 sticks INTO Thorium .. Onyxium for every lifelong kind (pickaxe, hatchet, hoe,
          can, Harvester, multitool), never the pole / gathering armor / Copper / Iron steps; the row check; no item = no sticks; a real can
          tier-up Iron -> Thorium is short without the sticks and takes exactly 2 with them
       G  GREAT SHIELD TWIN (coordinator): Weapon_GreatShield_<Metal> scales like Weapon_Longsword_<Metal> (kunaiTwin, K, the level multiplier)
  LIVE313 start twice on a scratch copy of the live NewBetaTest data: config bytes untouched, the 4 rows at their defaults, registries read
       not rewritten; the live player files (read only) are counted: normal stacks that the first look would remove
  The older children run with -Dskyy.harness.noNormOff=true (normal.off / removeOwned off, no stick cost = the 0.3.12 flow they were written for).
Scratch: tools/dev/scratch/gear0313/harness (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re, glob, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


VERSION = "0.3.13"
V312 = "0.3.12"
SCR_ROOT = os.path.abspath(arg("--root", os.path.join(TOOLS, "dev", "scratch", "gear0313")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
J312 = os.path.abspath(os.path.join(HERE, "SkyyGear-%s.jar" % V312))                       # read only
PKG = "com.skyy.gear."
NEW_CLASSES = ["GearNorm", "GearNormDrop", "GearNormL", "GearNormFn", "GearNormCmd"]
CO20 = os.path.join(ROOT, "SkyyCollections", "SkyyCollections-0.2.20.jar")              # read only (the Enchanted Stick), copied
AR29 = os.path.join(ROOT, "SkyyArmory", "SkyyArmory-0.1.29.jar")                        # read only (the great shields), copied

# ---- the 0.3.12 harness as a library (it loads the older ones); its children run on THIS jar in THIS scratch folder
_H312 = os.path.join(HERE, "test_skyygear_0.3.12.py")
_T312 = open(_H312, encoding="utf-8").read()
_cut = _T312.rindex('if __name__ == "__main__":')
_argv = sys.argv
sys.argv = [_H312, "--jar", JAR, "--root", SCR_ROOT, "--dir", SCRATCH]
H312 = {"__name__": "skyygear_h312", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
exec(compile(_T312[:_cut], _H312 + " (library)", "exec"), H312)
sys.argv = _argv
H311, H310, H39, H38, H37, H36, H35, H = (H312["H311"], H312["H310"], H312["H39"], H312["H38"], H312["H37"], H312["H36"], H312["H35"], H312["H"])
FAKE_DIR = H312["FAKE_DIR"]
FI7_SRC = H312["FI7_SRC"]
LIVE_GEAR = H312["LIVE_GEAR"]
LIVE_PLAYERS_NB = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "universe", "players")
FAILS, OKS = [], [0]
WAIVE = list(H312["WAIVE"])
WAIVED = []


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def entries(j):
    z = zipfile.ZipFile(j)
    return dict((n, z.read(n)) for n in z.namelist())


# ====================================================================================================== S313
def run_assets313():
    ea, eb = entries(J312), entries(JAR)
    added = sorted(set(eb) - set(ea))
    gone = sorted(set(ea) - set(eb))
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n] and not n.endswith(".class"))
    want_add = set("com/skyy/gear/%s.class" % c for c in NEW_CLASSES)
    check(set(added) == want_add and not gone and changed == ["manifest.json"],
          "S313: 0.3.12 -> 0.3.13 adds exactly the 5 classes, removes nothing, changes only the manifest among non-class files: extra %s, missing %s, gone %s, changed %s"
          % (sorted(set(added) - want_add)[:4], sorted(want_add - set(added))[:4], gone[:3], changed))
    man = eb["manifest.json"].decode("utf-8")
    check('"0.3.13"' in man and "NORMAL TOOLS ARE OFF" in man and "Enchanted Sticks" in man, "S313: the manifest names the round")
    ca = set(n for n in ea if n.endswith(".class"))
    cb = set(n for n in eb if n.endswith(".class"))
    chg = sorted(n.rsplit("/", 1)[1][:-6] for n in ca & cb if ea[n] != eb[n])
    print("  class compare 0.3.12 -> 0.3.13: %d classes, %d changed (%s), new %s, gone %s"
          % (len(cb), len(chg), ", ".join(chg), sorted(n.rsplit("/", 1)[1][:-6] for n in cb - ca), sorted(ca - cb)))
    want_chg = {"GearLL", "GearCfg", "GearUp", "GearBase", "GearCmd", "GearChestOpenSys", "GearChestBreakSys", "GearCraftPreSys", "GearChestOpen",
                "GearLife", "GearSickle", "GearBoxL", "SkyyGearPlugin", "GearBye", "CfgRows"}
    check(set(chg) <= want_chg | set(n for n in chg if n.startswith("Cfg")), "S313: only the expected classes changed: unexpected %s" % sorted(set(chg) - want_chg))


# ====================================================================================================== H313
def run_h313(out):
    fi7 = os.path.join(SCRATCH, "packs", "SkyyFishing-0.1.7.jar")
    shutil.copyfile(FI7_SRC, fi7)
    H35["FI_JAR"] = fi7
    if os.path.isfile(CO20):
        co = os.path.join(SCRATCH, "packs", "SkyyCollections-0.2.20.jar")
        shutil.copyfile(CO20, co)
        H36["CO_JAR"] = co
    L = H35["g36_setup"](out)
    K = L["K"]
    try:
        _h313(L, K)
    except Exception:
        import traceback
        traceback.print_exc()
        K.check(False, "H313: the phase raised: %s" % traceback.format_exc()[-1800:])
    K.save()


def _h313(L, K):
    from jpype import JClass, JInt, JShort, JLong, JDouble, JObject, JArray, JString, JImplements, JOverride, JBoolean
    br, Gear, Cfg, LL, Life, Up, Data, Stamp = L["br"], L["Gear"], L["Cfg"], L["LL"], L["Life"], L["Up"], L["Data"], L["Stamp"]
    mkinv, PR1, U1, stack, doc, skills, apply, logs, lls, ids = (L["mkinv"], L["PR1"], L["U1"], L["stack"], L["doc"], L["skills"], L["apply"], L["logs"],
                                                                 L["lls"], L["ids"])
    ITEM, E, afs, HOME = L["ITEM"], L["E"], L["afs"], L["HOME"]
    P = lambda n: JClass(PKG + n)
    Norm, NDrop, Stick, Base, Lvl = P("GearNorm"), P("GearNormDrop"), P("GearStick"), P("GearBase"), P("GearLevel")
    CRR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    IDL = JClass("com.hypixel.hytale.server.core.asset.type.item.config.ItemDropList")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    BD, BS = JClass("org.bson.BsonDocument"), JClass("org.bson.BsonString")
    HAL = JClass("java.util.ArrayList")
    Long_, Bool_ = JClass("java.lang.Long"), JClass("java.lang.Boolean")

    def kc(cond, what):
        K.check(bool(cond), what)

    def eq(got, want, what):
        K.check(got == want, "%s: got %s, want %s" % (what, got, want))
    apply()

    # ============================================================== A: the rule
    yes = ["Tool_Pickaxe_Crude", "Tool_Pickaxe_Iron", "Tool_Pickaxe_Wood", "Tool_Pickaxe_Scrap", "Tool_Hatchet_Onyxium", "Tool_Hoe_Thorium", "Tool_Sickle_Steel_Rusty",
           "Tool_Sickle_Copper", "SkyyFishing_Rod_Bamboo", "SkyyFishing_Rod_Iron", "Tool_Watering_Can", "Tool_WaterCan_Iron"]
    no = ["Tool_Shovel_Iron", "Tool_Hatchet_Pickaxe_Multitool_Iron", "Tool_Sickle_Harvester_Iron", "Weapon_Sword_Iron", "Ingredient_Stick", "Tool_Hammer_Iron",
          "Tool_Bark_Scraper", "Tool_Shears_Basic", "Hepta_Axe", None, ""]
    kc(all(bool(LL.normKind(i)) for i in yes) and not any(bool(LL.normKind(i)) for i in no),
       "A: normKind = pickaxes / hatchets / hoes / sickles of every metal, rods, cans; never shovels, the multitool, the Harvester, weapons: yes-misses %s, no-hits %s"
       % ([i for i in yes if not LL.normKind(i)], [i for i in no if LL.normKind(i)]))
    kc(all(bool(LL.noCraft(i)) for i in yes) and not bool(LL.noCraft("Tool_Shovel_Iron")) and not bool(LL.noCraft("Tool_Hatchet_Pickaxe_Multitool_Iron")),
       "A: noCraft refuses every normal tool, never the shovel / multitool")
    apply(normal__extraIds="Hepta_Ax, ab")
    kc(bool(LL.normKind("Hepta_Axe")) and not bool(LL.normKind("ab_x")) and bool(LL.noCraft("Hepta_Axe")), "A: normal.extraIds adds pack ids by their start (min 3 letters)")
    apply()
    kc(not bool(LL.normKind("Hepta_Axe")), "A: normal.extraIds is live")
    plain = stack("Tool_Pickaxe_Iron")
    bad = IS("Tool_Pickaxe_Iron", JInt(1)).withMetadata(JString(str(P("GearDefs").DOC_KEY)), BS("garbage"))
    kc(bool(Norm.normal(plain)) and not bool(Norm.normal(bad)) and not bool(Norm.normal(stack("Tool_Shovel_Iron"))) and not bool(Norm.normal(None)),
       "A: normal(stack): a plain pickaxe yes, unreadable gear data never (it could be a lifelong tool), a shovel no")
    CRows = P("CfgRows")
    keys = ["normal.off", "normal.removeOwned", "normal.extraIds", "lifelong.stickCost"]
    kc(all(int(CRows.index(k)) >= 0 and bool(CRows.flag(int(CRows.index(k)), "danger")) for k in keys), "A: the 4 Server Setup rows exist (danger rows)")
    FRESH = L["FRESH"]
    kc("# ---- normal tools off, Enchanted Sticks in the later tier-ups (SkyyGear 0.3.13) ----" in FRESH and "\nnormal.off=true\n" in FRESH
       and "\nlifelong.stickCost=0,0,0,2,4,8,16,32\n" in FRESH and "\nnormal.extraIds=\n" in FRESH, "A: a fresh config.properties lists the 0.3.13 block")
    apply(normal__off="false")
    apply(normal__off="false", normal__extraIds="Hepta_Ax")
    kc(not bool(Norm.on()) and not bool(LL.noCraft("Hepta_Axe")) and bool(LL.noCraft("Tool_Pickaxe_Iron")) and bool(LL.noCraft("Tool_Watering_Can")),
       "A: normal.off off = the 0.3.12 rules (an extra id crafts again; lifelong.noCraft / can.noVanilla still refuse theirs)")
    apply()
    FN = P("GearNormFn")()
    kc(bool(FN.apply(JString("Tool_Hoe_Iron"))) and not bool(FN.apply(JString("Tool_Shovel_Iron"))) and bool(FN.apply(plain)) and not bool(FN.apply(None)),
       "A: gear:fn:normalTool answers by id and by stack")

    # ============================================================== B: the recipes
    def outs():
        m = CRR.getAssetMap().getAssetMap()
        res = {}
        for o in list(m.values()):
            po = o.getPrimaryOutput()
            if po is not None and po.getItemId() is not None:
                res.setdefault(str(po.getItemId()), []).append(str(o.getId()))
        return res
    b0 = outs()
    Norm.STARTED = True
    norm0 = sorted(i for i in b0 if bool(LL.normKind(i)) and not i.startswith("SkyyFishing_Rod_"))
    rods0 = sorted(i for i in b0 if i.startswith("SkyyFishing_Rod_"))
    kc(len(norm0) >= 10 and "Tool_Pickaxe_Copper" in norm0, "B: before: %d normal tools have recipes (%s ...)" % (len(norm0), norm0[:5]))
    Norm.ensure()
    b1 = outs()
    left = sorted(i for i in b1 if bool(LL.normKind(i)) and not i.startswith("SkyyFishing_Rod_"))
    kc(not left and int(Norm.GONE.size()) >= len(norm0), "B: after: no recipe makes a normal tool (%s left), %d removed: %s" % (left, int(Norm.GONE.size()), str(Norm.RCP)))
    kc(("Tool_Shovel_Iron" in b1) == ("Tool_Shovel_Iron" in b0) and sorted(i for i in b1 if i.startswith("SkyyFishing_Rod_")) == rods0
       and all(i in b1 for i in b0 if i.startswith("Tool_Hatchet_Pickaxe_Multitool_")),
       "B: the shovel / SkyyFishing rods (%s) / multitool recipes stay" % rods0)
    n0 = int(Norm.N[0])
    Norm.ensure()
    eq(int(Norm.N[0]), n0, "B: a second run removes nothing (idempotent)")

    # ============================================================== C: the drop lists
    names = []
    with zipfile.ZipFile(L["AZP"]) as az_:
        for n in az_.namelist():
            if n.startswith("Server/Drops/") and n.endswith(".json"):
                names.append(n)
    tl = HAL()
    for n in names:
        tl.add(afs.getPath("/" + n))
    try:
        IDL.getAssetStore().loadAssetsFromPaths("Hytale:Hytale", tl)
    except Exception as e:
        K.notes.append("C: loading the vanilla drop lists raised %s" % str(e)[:200])
    nl = int(IDL.getAssetMap().getAssetMap().size())
    kc(nl > 100 and IDL.getAssetMap().getAsset("Drop_Goblin_Miner") is not None, "C: %d vanilla drop lists loaded (Drop_Goblin_Miner there)" % nl)
    raw = IDL.getAssetMap().getAsset("Drop_Goblin_Miner").getContainer()
    Norm.ensure()
    gm = IDL.getAssetMap().getAsset("Drop_Goblin_Miner")
    c1 = gm.getContainer()
    kc(str(c1.getClass().getName()) == PKG + "GearNormDrop" and c1.inner == raw, "C: Drop_Goblin_Miner's container is a GearNormDrop around the original: %s" % c1.getClass().getName())
    kc(int(Norm.WR.size()) >= 20, "C: %d drop lists filtered (chest loot lists + NPC lists)" % int(Norm.WR.size()))
    rnd = random.Random(7)

    @JImplements("java.util.function.DoubleSupplier")
    class DS(object):
        @JOverride
        def getAsDouble(self):
            return rnd.random()
    ds = DS()

    def roll(lst, n):
        got = {}
        for _ in range(n):
            out_ = HAL()
            lst.getContainer().populateDrops(out_, ds, JString(str(lst.getId())))
            for d in out_:
                got[str(d.getItemId())] = got.get(str(d.getItemId()), 0) + 1
        return got
    rawgot = {}
    for _ in range(3000):
        o_ = HAL()
        raw.populateDrops(o_, ds, JString("Drop_Goblin_Miner"))
        for d in o_:
            rawgot[str(d.getItemId())] = rawgot.get(str(d.getItemId()), 0) + 1
    g1 = roll(gm, 3000)
    kc(rawgot.get("Tool_Pickaxe_Scrap", 0) > 0 and "Tool_Pickaxe_Scrap" not in g1 and len(g1) >= 1 and sum(g1.values()) > 0,
       "C: 3000 rolls: the raw list gives the Scrap pickaxe %d x, the filtered one never, the rest still drops: %s" % (rawgot.get("Tool_Pickaxe_Scrap", 0), sorted(g1)[:6]))
    alld = [str(x.getItemId()) for x in c1.getAllDrops(HAL())]
    kc("Tool_Pickaxe_Scrap" not in alld and len(alld) >= 1, "C: getAllDrops of the filtered list lists no normal tool")
    chestlists = [str(k) for k in Norm.WR.keySet() if str(k).startswith("Drop_") is False or "Chest" in str(k) or "Prefab" in str(k)]
    bad_rolls = []
    for lid in list(Norm.WR.keySet())[:40]:
        g = roll(IDL.getAssetMap().getAsset(lid), 200)
        if any(bool(LL.normKind(i)) for i in g):
            bad_rolls.append(lid)
    kc(not bad_rolls, "C: 200 rolls of each of 40 filtered lists: no normal tool ever (%s)" % bad_rolls[:4])
    # a list that also gets the stick cut: the GearStick goes OUTSIDE, ours stays inside; the stick cut leaving keeps ours
    apply(sticks__lists="Drop_Goblin_Miner")
    Stk = P("GearSickle")
    Stk.ENS = 0
    Stk.WR_SRC = None
    Stk.ensure()
    Norm.ensure()
    c2 = gm.getContainer()
    kc(str(c2.getClass().getName()) == PKG + "GearStick" and str(c2.inner.getClass().getName()) == PKG + "GearNormDrop" and "Tool_Pickaxe_Scrap" not in roll(gm, 1500),
       "C: with the stick cut too: GearStick(GearNormDrop(list)), still no Scrap pickaxe")
    apply()
    Stk.ENS = 0
    Stk.WR_SRC = None
    Stk.ensure()
    Norm.ensure()
    c3 = gm.getContainer()
    kc(str(c3.getClass().getName()) == PKG + "GearNormDrop" and c3.inner == raw, "C: the stick cut leaves -> GearNormDrop(list) again")
    apply(normal__off="false")
    Norm.ensure()
    kc(gm.getContainer() == raw and int(Norm.WR.size()) == 0, "C: normal.off off = every list has its own container back")
    apply()
    Norm.ensure()
    kc(str(gm.getContainer().getClass().getName()) == PKG + "GearNormDrop", "C: on again = filtered again")
    tk = int(Norm.ENS)
    Norm.tick()
    kc(int(Norm.ENS) == tk, "C: tick within 30 s does nothing")

    # ============================================================== D: chests
    logs()
    box = SIC(JShort(12))
    L["wipe_home"]()
    skills(Mining=4, Foraging=4, Farming=4, Fishing=4)
    invD, csD = mkinv()
    Life.sweep(PR1, invD, True)
    pk = str(Gear.pkey(U1))
    llp = [x for x in lls(csD, pk) if x[2] == 0][0][6]
    box.setItemStackForSlot(JShort(0), stack("Tool_Pickaxe_Iron"))
    box.setItemStackForSlot(JShort(1), llp)
    box.setItemStackForSlot(JShort(2), stack("Tool_Shovel_Iron"))
    box.setItemStackForSlot(JShort(3), stack("Tool_Hatchet_Pickaxe_Multitool_Iron") if ITEM.getAssetMap().getAsset("Tool_Hatchet_Pickaxe_Multitool_Iron") is not None else stack("Tool_Shovel_Crude"))
    box.setItemStackForSlot(JShort(4), bad)
    box.setItemStackForSlot(JShort(5), stack("Tool_Watering_Can"))
    box.setItemStackForSlot(JShort(6), stack("Ingredient_Stick", 20))
    recD = os.path.join(SCRATCH, "chestrec.log")
    n = int(Norm.strip(box, JString("test chest"), JClass("java.nio.file.Paths").get(recD)))
    left = [str(box.getItemStack(JShort(i)).getItemId()) if box.getItemStack(JShort(i)) is not None and not box.getItemStack(JShort(i)).isEmpty() else None for i in range(7)]
    lg = [l_ for l_ in logs() if "NORMOFF-CHEST" in l_]
    kc(n == 2 and left[0] is None and left[5] is None and left[1] == "Tool_Pickaxe_Crude" and left[2] == "Tool_Shovel_Iron" and left[4] == "Tool_Pickaxe_Iron"
       and left[6] == "Ingredient_Stick" and len(lg) == 2
       and len([l_ for l_ in open(recD, encoding="utf-8").read().split(chr(10)) if l_.startswith("REMOVED")]) == 2, "D (critic A2: + the opener's record): strip: the plain pickaxe + the vanilla can go (2 logged), the lifelong pickaxe / shovel / multitool / unreadable one / sticks stay: %s" % left)
    eq(int(Norm.chestAt(None, JInt(0), JInt(0), JInt(0), None, JString("x"), JString("open"))), 0, "D: chestAt with no world answers 0")

    # ============================================================== E: the one-time removal
    RQ = {"rows": [], "fetch": [], "gone": [], "room": True}
    BAG = {"Tool_Pickaxe_Copper": 2, "Ingredient_Stick": 50, "Tool_Shovel_Iron": 1}
    TAKEN = []
    CUR = {}

    @JImplements("java.util.function.Function")
    class RqList(object):
        @JOverride
        def apply(self, o):
            rows = RQ["rows"]
            arr = JArray(JObject)(len(rows))
            for i_, r_ in enumerate(rows):
                arr[i_] = JArray(JObject)([JString(r_[0]), JString(r_[1]), r_[2]])
            return arr

    @JImplements("java.util.function.Function")
    class RqFetch(object):
        @JOverride
        def apply(self, o):
            eid = str(o[1])
            if not RQ["room"]:
                return JString("no room")
            row = [r_ for r_ in RQ["rows"] if r_[0] == eid][0]
            md = BD() if row[2] is None else row[2].clone()
            md.put(str(Data.stampKey()), BD("e", BS(eid)))
            cs_ = CUR["cs"]
            for i_ in range(int(cs_["storage"].getCapacity())):
                x_ = cs_["storage"].getItemStack(JShort(i_))
                if x_ is None or x_.isEmpty():
                    cs_["storage"].setItemStackForSlot(JShort(i_), IS(row[1], JInt(1), md))
                    break
            RQ["rows"] = [r_ for r_ in RQ["rows"] if r_[0] != eid]
            RQ["fetch"].append(eid)
            return JString("ok")

    @JImplements("java.util.function.Function")
    class RqGone(object):
        @JOverride
        def apply(self, o):
            RQ["gone"].append((str(o[1]), str(o[2])))
            return JObject(True, Bool_)

    @JImplements("java.util.function.Function")
    class BagAll(object):
        @JOverride
        def apply(self, o):
            m = JClass("java.util.HashMap")()
            for k_, v_ in BAG.items():
                m.put(JString(k_), JObject(JLong(v_), Long_))
            return m

    @JImplements("java.util.function.Function")
    class BagTake(object):
        @JOverride
        def apply(self, o):
            k_, n_ = str(o[1]), int(o[2])
            have = BAG.get(k_, 0)
            got = min(have, n_)
            BAG[k_] = have - got
            TAKEN.append((k_, got))
            return JObject(JLong(got), Long_)

    @JImplements("java.util.function.Function")
    class BagCommit(object):
        @JOverride
        def apply(self, o):
            return JObject(JLong(0), Long_)
    old_list = br.get("wardrobe:fn:list")
    br.put("wardrobe:fn:list", RqList())
    br.put("wardrobe:fn:fetch", RqFetch())
    br.put("wardrobe:fn:gone", RqGone())
    br.put("sacks:fn:all", BagAll())
    br.put("sacks:fn:take", BagTake())
    br.put("sacks:fn:commit", BagCommit())
    try:
        # E1 a fresh profile with a plain Iron pickaxe: the kits first -> it IS the lifelong pickaxe, nothing removed
        L["wipe_home"]()
        Norm.LASTRUN.clear()
        BAG.update({"Tool_Pickaxe_Copper": 0})
        inv1, cs1 = mkinv()
        CUR["cs"] = cs1
        cs1["storage"].setItemStackForSlot(JShort(5), stack("Tool_Pickaxe_Iron"))
        Life.sweep(PR1, inv1, True)
        R = LL.reg(pk)
        pick = [x for x in lls(cs1, pk) if x[2] == 0]
        kc(len(pick) == 1 and str(pick[0][6].getItemId()) == "Tool_Pickaxe_Iron" and str(R.getProperty("normOff")) == "1" and str(R.getProperty("normOffRq")) == "1"
           and str(R.getProperty("normOffN")) == "0", "E1: a fresh profile's plain Iron pickaxe became its lifelong pickaxe (kits first); the pass ran: nothing to remove")
        # E2 an existing profile from 0.3.12 with plain extras: inventory + bags + Requip
        R.remove("normOff")
        R.remove("normOffRq")
        R.remove("normOffN")
        LL.save(pk, R)
        regbytes = open(os.path.join(HOME, "lifelong", pk + ".properties"), "rb").read()
        before_ll = sorted((x[2], x[3]) for x in lls(cs1, pk))
        put = [("hotbar", 7, stack("Tool_Hoe_Copper")), ("storage", 10, stack("Tool_Sickle_Iron")), ("storage", 11, stack("Tool_Watering_Can")),
               ("backpack", 1, stack("SkyyFishing_Rod_Copper")), ("storage", 12, stack("Tool_Shovel_Iron")), ("storage", 13, bad),
               ("storage", 14, IS("Tool_Hatchet_Iron", JInt(1)).withMetadata(JString(str(Data.stampKey())), BD("e", BS("eOUT1")))),
               ("backpack", 2, stack("Tool_Pickaxe_Scrap"))]
        if ITEM.getAssetMap().getAsset("Tool_Hatchet_Pickaxe_Multitool_Iron") is not None:
            put.append(("storage", 15, stack("Tool_Hatchet_Pickaxe_Multitool_Iron")))
        for sec, i_, s_ in put:
            cs1[sec].setItemStackForSlot(JShort(i_), s_)
        hoe_dur = float(cs1["hotbar"].getItemStack(JShort(7)).getDurability())
        BAG.update({"Tool_Pickaxe_Copper": 2, "Ingredient_Stick": 50, "Tool_Shovel_Iron": 1})
        RQ["rows"] = [("eIN1", "Tool_Hatchet_Copper", None), ("eIN2", "Tool_Shovel_Iron", None), ("eIN3", "Tool_Pickaxe_Iron", llp.getMetadata())]
        RQ["room"] = False
        logs()
        Norm.LASTRUN.clear()
        LL.LAST.clear()
        Life.sweep(PR1, inv1, True)
        R = LL.reg(pk)
        now = ids(cs1)
        gone_ids = ["Tool_Hoe_Copper", "Tool_Sickle_Iron", "Tool_Watering_Can", "SkyyFishing_Rod_Copper", "Tool_Pickaxe_Scrap", "Tool_Hatchet_Iron"]
        kc(not any(now.get(i, 0) for i in ("Tool_Hoe_Copper", "Tool_Watering_Can", "SkyyFishing_Rod_Copper", "Tool_Pickaxe_Scrap", "Tool_Hatchet_Iron"))
           and now.get("Tool_Shovel_Iron") == 1 and sorted((x[2], x[3]) for x in lls(cs1, pk)) == before_ll and now.get("Tool_Pickaxe_Iron", 0) >= 2,
           "E2: the plain hoe / sickle / vanilla can / rod / Scrap pickaxe / Requip-OUT hatchet are gone; the shovel, the unreadable pickaxe and EVERY lifelong tool stay: %s" % now)
        kc(now.get("Tool_Sickle_Iron", 0) == 0 or any(x[6].getItemId() == "Tool_Sickle_Iron" for x in lls(cs1, pk)), "E2: the plain Iron sickle went (a Crude lifelong sickle stays)")
        kc(TAKEN == [("Tool_Pickaxe_Copper", 2)] and BAG["Ingredient_Stick"] == 50 and BAG["Tool_Shovel_Iron"] == 1, "E2: the bags: only the 2 Copper pickaxes taken: %s" % TAKEN)
        kc(("eOUT1", "normal tool removed (SkyyGear 0.3.13)") in RQ["gone"], "E2: the Requip-stamped OUT hatchet is reported used up (wardrobe:fn:gone): %s" % RQ["gone"])
        kc(str(R.getProperty("normOff")) == "1" and R.getProperty("normOff.pend") is None and R.getProperty("normOffRq") is None,
           "E2: marker normOff=1, the journal gone; Requip waits (no room)")
        hist = glob.glob(os.path.join(HOME, "normoff", "history", "*.bak"))
        hist = sorted(hist)
        kc(len(hist) >= 1 and open(hist[-1], "rb").read() == regbytes, "E2: the History copy of the registry = its bytes before (%s)" % [os.path.basename(h) for h in hist])
        recf = os.path.join(HOME, "normoff", pk + ".log")
        rec = [l_.split("\t") for l_ in open(recf, encoding="utf-8").read().split("\n") if l_.startswith("REMOVED")]
        kc(len(rec) == 8 and sorted(r_[3] for r_ in rec if r_[2] != "bag") == sorted(gone_ids) and len([r_ for r_ in rec if r_[2] == "bag"]) == 2,
           "E2: the undo record has every removed stack (6 inventory + 2 bag lines): %s" % [(r_[2], r_[3]) for r_ in rec])
        lg = logs()
        kc(len([l_ for l_ in lg if "NORMOFF-REMOVE" in l_]) == 7 and any("NORMOFF-DONE" in l_ and "UNDO: /gear normoff undo" in l_ for l_ in lg),
           "E2: gear.log: a NORMOFF-REMOVE per stack + NORMOFF-DONE with the undo command")
        kc(int(Norm.N[12]) >= 1 and "eIN1" not in RQ["fetch"], "E2: Requip: no room -> nothing taken, asked again later")
        # E3 Requip with room
        RQ["room"] = True
        Norm.LASTRUN.clear()
        LL.LAST.clear()
        Life.sweep(PR1, inv1, True)
        R = LL.reg(pk)
        kc(RQ["fetch"] == ["eIN1"] and ("eIN1", "normal tool removed (SkyyGear 0.3.13)") in RQ["gone"] and ids(cs1).get("Tool_Hatchet_Copper", 0) == 0
           and str(R.getProperty("normOffRq")) == "1" and [r_[0] for r_ in RQ["rows"]] == ["eIN2", "eIN3"],
           "E3: Requip: the plain Copper hatchet fetched, removed, reported gone; the shovel + the lifelong pickaxe entries untouched; normOffRq=1")
        # E4 run twice: a new plain tool is NOT removed (once per profile)
        cs1["storage"].setItemStackForSlot(JShort(20), stack("Tool_Hoe_Iron"))
        Norm.LASTRUN.clear()
        LL.LAST.clear()
        Life.sweep(PR1, inv1, True)
        LL.REG.clear()
        Norm.LASTRUN.clear()
        LL.LAST.clear()
        Life.sweep(PR1, inv1, True)
        hist2 = glob.glob(os.path.join(HOME, "normoff", "history", "*.bak"))
        recs4 = [l_ for l_ in open(recf, encoding="utf-8").read().split(chr(10)) if l_.startswith("REMOVED")]
        kc(ids(cs1).get("Tool_Hoe_Iron", 0) == 0 and len(hist2) == len(hist) and any("straggler:" in l_ and "Tool_Hoe_Iron" in l_ for l_ in recs4)
           and str(LL.reg(pk).getProperty("normOff")) == "1" and int(Norm.N[14]) >= 1,
           "E4 (critic B2): the one-time pass does not run again (no new History copy), but a normal tool that turns up later is a STRAGGLER: removed + recorded")
        cs1["storage"].setItemStackForSlot(JShort(21), stack("Tool_Shovel_Iron"))
        Norm.LASTRUN.clear()
        LL.LAST.clear()
        Life.sweep(PR1, inv1, True)
        kc(ids(cs1).get("Tool_Shovel_Iron", 0) >= 1, "E4: a shovel that turns up stays")
        # E5 a crash right after the first removal: the journal resumes it
        L["wipe_home"]()
        Norm.LASTRUN.clear()
        inv5, cs5 = mkinv()
        CUR["cs"] = cs5
        Life.sweep(PR1, inv5, True)
        R5 = LL.reg(pk)
        R5.remove("normOff")
        R5.remove("normOffRq")
        LL.save(pk, R5)
        cs5["storage"].setItemStackForSlot(JShort(10), stack("Tool_Hoe_Copper"))
        cs5["storage"].setItemStackForSlot(JShort(11), stack("Tool_Sickle_Copper"))
        BAG.update({"Tool_Pickaxe_Copper": 0})
        Norm.CRASH_AT = 1
        Norm.LASTRUN.clear()
        LL.LAST.clear()
        Life.sweep(PR1, inv5, True)
        Norm.CRASH_AT = 0
        mid = ids(cs5)
        LL.REG.clear()
        R5 = LL.reg(pk)
        kc(R5.getProperty("normOff.pend") is not None and R5.getProperty("normOff") is None and (mid.get("Tool_Hoe_Copper", 0) + mid.get("Tool_Sickle_Copper", 0)) == 1,
           "E5: a crash after the first removal: one gone, the journal normOff.pend on disk, no marker")
        Norm.LASTRUN.clear()
        LL.LAST.clear()
        Life.sweep(PR1, inv5, True)
        R5 = LL.reg(pk)
        fin = ids(cs5)
        kc(fin.get("Tool_Hoe_Copper", 0) == 0 and fin.get("Tool_Sickle_Copper", 0) == 0 and str(R5.getProperty("normOff")) == "1" and R5.getProperty("normOff.pend") is None,
           "E5: the next look resumes (RESUME) and finishes: both gone, marker set")
        # E6 UNDO on the E2 profile's record (the same pk): every recorded stack back once, stamp dropped, durability kept
        recs = [l_.split("\t") for l_ in open(recf, encoding="utf-8").read().split("\n") if l_.startswith("REMOVED")]
        invU, csU = mkinv()
        CUR["cs"] = csU
        kc(int(Norm.pending(pk)) >= 8, "E6 (critic A1): pending() counts the recorded stacks not given back: %d" % int(Norm.pending(pk)))
        Norm.UNDO.put(U1, JString("Admin"))
        Norm.LASTRUN.clear()
        LL.LAST.clear()
        Life.sweep(PR1, invU, True)
        got = ids(csU)
        eq(int(Norm.pending(pk)), 0, "E6 (critic A1): after the undo nothing is pending (the admin command then says 'no record')")
        RU = LL.reg(pk)
        back = {}
        for r_ in recs:
            back[r_[3]] = back.get(r_[3], 0) + int(r_[4])
        stamped = []
        for k_ in ("hotbar", "storage", "backpack"):
            for i_ in range(int(csU[k_].getCapacity())):
                x_ = csU[k_].getItemStack(JShort(i_))
                if x_ is not None and not x_.isEmpty() and x_.getMetadata() is not None and x_.getMetadata().containsKey(str(Data.stampKey())):
                    stamped.append(str(x_.getItemId()))
        hoe_back = [csU[k_].getItemStack(JShort(i_)) for k_ in ("hotbar", "storage", "backpack") for i_ in range(int(csU[k_].getCapacity()))
                    if csU[k_].getItemStack(JShort(i_)) is not None and str(csU[k_].getItemStack(JShort(i_)).getItemId()) == "Tool_Hoe_Copper"]
        kc(all(got.get(k_, 0) >= v_ for k_, v_ in back.items()) and str(RU.getProperty("normOff")) == "undone" and str(RU.getProperty("normOffRq")) == "undone"
           and not Norm.UNDO.containsKey(U1) and not stamped, "E6: UNDO gave every recorded stack back (%s), no Requip stamp on them, markers 'undone': %s" % (back, got))
        kc(len(hoe_back) >= 1 and abs(float(hoe_back[0].getDurability()) - hoe_dur) < 1e-6, "E6: the durability came back with the stack")
        Norm.UNDO.put(U1, JString("Admin"))
        Norm.LASTRUN.clear()
        Life.sweep(PR1, invU, True)
        eq(ids(csU), got, "E6: a second undo gives nothing twice (GIVEN lines)")
        csU["storage"].setItemStackForSlot(JShort(30), stack("Tool_Pickaxe_Thorium"))
        Norm.LASTRUN.clear()
        LL.LAST.clear()
        Life.sweep(PR1, invU, True)
        kc(ids(csU).get("Tool_Pickaxe_Thorium") == 1, "E6: an undone profile is never cleaned again")
        apply(normal__removeOwned="false")
        L["wipe_home"]()
        Norm.LASTRUN.clear()
        inv7, cs7 = mkinv()
        CUR["cs"] = cs7
        Life.sweep(PR1, inv7, True)
        kc(LL.reg(pk).getProperty("normOff") is None, "E7: normal.removeOwned off = no pass, no marker (it runs once switched on)")
        apply()
    finally:
        br.put("wardrobe:fn:list", old_list)
        for k_ in ("wardrobe:fn:fetch", "wardrobe:fn:gone", "sacks:fn:all", "sacks:fn:take", "sacks:fn:commit"):
            br.remove(k_)

    # ============================================================== A3 / A4 / B3 (critic fixes)
    L["wipe_home"]()
    skills(Mining=4, Foraging=4, Farming=4, Fishing=4)
    invA, csA = mkinv()
    Life.sweep(PR1, invA, True)
    pa = [x for x in lls(csA, pk) if x[2] == 0][0]
    secs = {"hotbar": 0, "storage": 1, "backpack": 2, "armor": 3, "utility": 4, "tools": 5}
    okd = bool(Life.demote(csA[pa[0]], JInt(pa[1]), pa[6], doc(pa[6]), U1))
    dd = doc(csA[pa[0]].getItemStack(JShort(pa[1])))
    kc(okd and bool(LL.isLL(dd)) and bool(LL.isRt(dd)) and not bool(Norm.normal(csA[pa[0]].getItemStack(JShort(pa[1])))),
       "A3: /lifelong's demote RETIRES the re-picked-away tool (still lifelong, lrt=1) - never a plain tool")
    apply(lifelong__canKit="false")
    kc(not bool(LL.normKind("Tool_Watering_Can")) and not bool(LL.normKind("Tool_WaterCan_Iron")) and bool(LL.normKind("Tool_Hoe_Iron")),
       "A4: with the can kit off, watering cans are not normal tools (nobody is left without a can)")
    apply(lifelong__poleKit="false")
    kc(not bool(LL.normKind("SkyyFishing_Rod_Iron")) and bool(LL.normKind("Tool_Watering_Can")), "A4: with the pole kit off, rods are not normal tools")
    apply()
    Norm.ensure()
    sz = int(CRR.getAssetMap().getAssetMap().size())
    eq(int(Norm.RCP_N), sz, "B3: the recipe run remembers the store size")
    r0 = int(Norm.N[11])
    Norm.ENS = 0
    Norm.tick()
    eq(int(Norm.N[11]), r0, "B3: tick with the same store size = drop lists only")
    Norm.RCP_N = -5
    Norm.ENS = 0
    Norm.tick()
    eq(int(Norm.N[11]), r0 + 1, "B3: tick after a store-size change (a reload missed while BUSY) runs the recipes again")

    # ============================================================== F: Enchanted Sticks
    have_stick = ITEM.getAssetMap().getAsset("Skyy_Ench_Stick") is not None
    if not have_stick:
        Up.STICK_ID = "Skyy_Ench_Iron"
        K.notes.append("F: SkyyCollections 0.2.20 not built - the stick checks use the seam GearUp.STICK_ID = Skyy_Ench_Iron")
    SID = str(Up.STICK_ID)

    def cmap(a, b):
        c = Up.cost(a, b)
        return None if c is None else dict((str(i), int(q)) for i, q in zip(c[0], c[1]))
    kc(have_stick, "F: the Enchanted Stick item (SkyyCollections 0.2.20) loads in the engine")
    exp = [("Tool_Pickaxe_Crude", "Tool_Pickaxe_Copper", 0), ("Tool_Pickaxe_Copper", "Tool_Pickaxe_Iron", 0), ("Tool_Pickaxe_Iron", "Tool_Pickaxe_Thorium", 2),
           ("Tool_Pickaxe_Thorium", "Tool_Pickaxe_Cobalt", 4), ("Tool_Pickaxe_Cobalt", "Tool_Pickaxe_Adamantite", 8), ("Tool_Hatchet_Iron", "Tool_Hatchet_Thorium", 2),
           ("Tool_Hoe_Iron", "Tool_Hoe_Thorium", 2), ("Tool_WaterCan_Iron", "Tool_WaterCan_Thorium", 2), ("Tool_WaterCan_Cobalt", "Tool_WaterCan_Adamantite", 8),
           ("Tool_Sickle_Harvester_Iron", "Tool_Sickle_Harvester_Thorium", 2)]
    badc = []
    for a, b, n in exp:
        m = cmap(a, b)
        if m is None or m.get(SID, 0) != n:
            badc.append((a, b, m))
    kc(not badc, "F: tier-ups INTO Thorium 2 / Cobalt 4 / Adamantite 8 sticks for pickaxe / hatchet / hoe / can / Harvester, none for Copper / Iron: %s" % badc[:3])
    m_th = cmap("Tool_Pickaxe_Iron", "Tool_Pickaxe_Thorium")
    kc(m_th is not None and m_th.get("Skyy_Ench_Thorium") == (1 if SID != "Skyy_Ench_Thorium" else 3), "F: ... on top of the ladder's own cost: %s" % m_th)
    eq(int(Up.stickFor("SkyyFishing_Rod_Copper", "SkyyFishing_Rod_Iron")) + int(Up.stickFor("Armor_Iron_Head", "Armor_Thorium_Head")), 0, "F: never the pole or gathering armor")
    eq([int(Up.stickFor("Tool_Pickaxe_Adamantite", "Tool_Pickaxe_Mithril")), int(Up.stickFor("Tool_Pickaxe_Mithril", "Tool_Pickaxe_Onyxium")),
        int(Up.stickFor("Tool_Hatchet_Pickaxe_Multitool_Iron", "Tool_Hatchet_Pickaxe_Multitool_Thorium"))], [16, 32, 2], "F: Mithril 16, Onyxium 32, the multitool too")
    kc(Up.checkSticks("x", "1,2,3") is not None and Up.checkSticks("x", "0,0,0,1,1,1,1,1000") is not None and Up.checkSticks("x", "0,0,0,1,1,1,1,1") is None, "F: the row check")
    apply(lifelong__stickCost="0,0,0,0,0,0,0,0")
    eq(cmap("Tool_Pickaxe_Iron", "Tool_Pickaxe_Thorium").get(SID, 0) if SID != "Skyy_Ench_Thorium" else 0, 0, "F: all zero = no sticks")
    apply(lifelong__stickCost="nonsense")
    eq(int(Up.stickFor("Tool_Pickaxe_Iron", "Tool_Pickaxe_Thorium")), 2, "F: a bad row = the default (one WARN)")
    apply()
    Up.STICK_ID = "Nope_No_Item"
    sn1 = int(Up.SN[1])
    kc(SID not in (cmap("Tool_Pickaxe_Iron", "Tool_Pickaxe_Thorium") or {}) or SID == "Skyy_Ench_Thorium", "F: no stick item loaded = no stick asked")
    kc(int(Up.SN[1]) == sn1 + 1, "F: ... counted (SN[1])")
    Up.STICK_ID = SID
    # a real can tier-up Iron -> Thorium (Farming high enough), short without sticks, exactly 2 taken with them
    if have_stick:
        L["wipe_home"]()
        skills(Mining=4, Foraging=4, Farming=40, Fishing=4)
        invG, csG = mkinv()
        Life.sweep(PR1, invG, True)
        SCANS = [int(x) for x in Stamp.SCAN]
        names_ = ["hotbar", "armor", "tools", "utility", "storage", "backpack"]
        csG["storage"].setItemStackForSlot(JShort(20), stack("Ingredient_Bar_Copper", 25))
        csG["storage"].setItemStackForSlot(JShort(21), stack("Skyy_Ench_Carrot", 1))
        csG["storage"].setItemStackForSlot(JShort(22), stack("Skyy_Ench_Cauliflower", 1))
        for want in ("Tool_WaterCan_Copper", "Tool_WaterCan_Iron"):
            cg = [x for x in lls(csG, pk) if x[2] == 5][0]
            r_ = Up.upgrade(invG, JInt(SCANS[names_.index(cg[0])]), JInt(cg[1]), JString(str(cg[6].getItemId())), P("GearForge").fp(cg[6]), U1, JString("Tester"))
        cg = [x for x in lls(csG, pk) if x[2] == 5][0]
        ch = Up.check(cg[6], U1)
        short = str(Up.shortOfU(invG, U1, ch[2]))
        kc(str(cg[6].getItemId()) == "Tool_WaterCan_Iron" and "Stick" in short, "F: the Iron can's tier-up to Thorium is short of Enchanted Sticks: %s" % short)
        csG["storage"].setItemStackForSlot(JShort(23), stack("Skyy_Ench_Stick", 5))
        r_ = Up.upgrade(invG, JInt(SCANS[names_.index(cg[0])]), JInt(cg[1]), JString(str(cg[6].getItemId())), P("GearForge").fp(cg[6]), U1, JString("Tester"))
        cg2 = [x for x in lls(csG, pk) if x[2] == 5][0]
        kc(int(r_[0]) == 1 and str(cg2[6].getItemId()) == "Tool_WaterCan_Thorium" and ids(csG).get("Skyy_Ench_Stick") == 3 and ids(csG).get("Skyy_Ench_Cauliflower", 0) == 0
           and cg2[3] == cg[3], "F: with 5 sticks: the can is Thorium (same uid), exactly 2 sticks + the Cauliflower used: %s" % ids(csG))

    # ============================================================== G: the great shield twin
    with zipfile.ZipFile(L["AZP"]) as az_:
        ln = [n for n in az_.namelist() if n.startswith("Server/Item/Items/Weapon/Longsword/") and n.endswith(".json")]
    tl2 = HAL()
    for n in ln:
        tl2.add(afs.getPath("/" + n))
    try:
        ITEM.getAssetStore().loadAssetsFromPaths("Hytale:Hytale", tl2)
    except Exception as e:
        K.notes.append("G: loading the vanilla longswords raised %s" % str(e)[:200])
    if os.path.isfile(AR29):
        ar = os.path.join(SCRATCH, "packs", "SkyyArmory-0.1.29.jar")
        shutil.copyfile(AR29, ar)
        L["addpack"](ar, "Skyy:SkyyArmory")
    mets = ["Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"]
    tw = [str(Base.kunaiTwin("Weapon_GreatShield_" + m)) for m in mets]
    kc(tw == ["Weapon_Longsword_" + m for m in mets], "G: kunaiTwin(Weapon_GreatShield_<Metal>) = Weapon_Longsword_<Metal>: %s" % tw)
    kc(str(Base.kunaiTwin("Weapon_Longsword_Iron")) == "Weapon_Longsword_Iron" and str(Base.kunaiTwin("Weapon_GreatShield_Bogus")) == "Weapon_GreatShield_Bogus",
       "G: other ids / a metal without a longsword stay themselves")
    kd = [(float(Base.kOf("Weapon_GreatShield_" + m, False)), float(Base.kOf("Weapon_Longsword_" + m, False))) for m in mets]
    kc(all(abs(a - b) < 1e-12 for a, b in kd), "G: K of each great shield = K of its same-metal longsword: %s" % kd[:3])
    gi = ITEM.getAssetMap().getAsset("Weapon_GreatShield_Iron")
    if gi is not None:
        lv = [int(Lvl.band("Weapon_GreatShield_" + m)[0]) for m in mets]
        ll_ = [int(Lvl.band("Weapon_Longsword_" + m)[0]) for m in mets]
        d0 = None
        ms = float(Base.mult("Weapon_GreatShield_Iron", d0, False))
        ml = float(Base.mult("Weapon_Longsword_Iron", d0, False))
        K.notes.append("G: band starts shields %s / longswords %s; mult at the band start shield %.4f longsword %.4f" % (lv, ll_, ms, ml))
        kc(lv == ll_ and abs(ms - ml) < 1e-9, "G: same level band and the same level multiplier at the same level (the shield's own 0.7 / 1.0 H come from SkyyArmory)")
    else:
        K.notes.append("G: SkyyArmory 0.1.29 jar not loaded - band / mult equality not checked (K + twin are)")

    K.notes.append("H313 counters: %s" % str(Norm.statusText()))


# ====================================================================================================== LIVE313
def run_live313(out):
    from jpype import JClass
    K = H["Child"](out)
    H["_jvm"]([B.SERVER_JAR, JAR], verify=True)
    home = os.path.join(SCRATCH, "live313", "Skyy_SkyyGear")
    shutil.rmtree(os.path.dirname(home), ignore_errors=True)
    os.makedirs(home)
    for f_ in ("config.properties", "quality.properties"):
        if os.path.isfile(os.path.join(LIVE_GEAR, f_)):
            shutil.copyfile(os.path.join(LIVE_GEAR, f_), os.path.join(home, f_))
    shutil.copytree(os.path.join(LIVE_GEAR, "lifelong"), os.path.join(home, "lifelong"))
    Cfg = JClass(PKG + "GearCfg")
    LL = JClass(PKG + "GearLL")
    Norm = JClass(PKG + "GearNorm")
    Paths = JClass("java.nio.file.Paths")
    Cfg.DIR = Paths.get(home)
    Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
    JClass(PKG + "GearLog").FILE = Paths.get(os.path.join(home, "gear.log"))
    JClass(PKG + "GearQual").load(Paths.get(os.path.join(home, "quality.properties")))
    before = open(os.path.join(home, "config.properties"), "rb").read()
    regs0 = dict((f_, open(os.path.join(home, "lifelong", f_), "rb").read()) for f_ in os.listdir(os.path.join(home, "lifelong")))
    for step in (1, 2):
        Cfg.importRolls(Cfg.FILE, Paths.get(os.path.join(home, "no-SkyyRolls", "reforge.properties")))
        for m in ("migrate011", "migrateStat011", "migrate012", "migrate013", "migrate02", "migrate021", "migrate023", "migrate025", "migrate0214",
                  "migrate0215", "migrate0216", "migrate0217", "migrate0218", "migrate031"):
            getattr(Cfg, m)()
        Cfg.load()
        Norm.STARTED = True
        Norm.ensure()
        after = open(os.path.join(home, "config.properties"), "rb").read()
        K.check(after == before, "LIVE313 start %d: the live config.properties copy is byte-identical (the 0.3.13 rows need no one-time update)" % step)
        K.check(bool(Cfg.NORM_ON) and bool(Cfg.NORM_OWNED) and str(Cfg.NORM_EXTRA) == "" and str(Cfg.LL_STICKS) == "0,0,0,2,4,8,16,32" and bool(Norm.on()),
                "LIVE313 start %d: the new rows read their defaults (normal tools off, owned ones removed, sticks 2/4/8/16/32)" % step)
    txt = before.decode("utf-8", "replace")
    K.check("normal." not in txt and "stickCost" not in txt, "LIVE313: the live file has none of the new keys (defaults apply)")
    K.check(all(open(os.path.join(home, "lifelong", f_), "rb").read() == b_ for f_, b_ in regs0.items()), "LIVE313: the registries were read, not rewritten")
    # the live players (read only): what each one's first look would remove (unstamped normal stacks in the inventory sections)
    pat = re.compile(r"^(Tool_(Pickaxe|Hatchet|Hoe|Sickle)_|SkyyFishing_Rod_|Tool_Watering_Can|Tool_WaterCan_)")
    rep_ = []
    for f_ in sorted(glob.glob(os.path.join(LIVE_PLAYERS_NB, "*.json"))):
        try:
            d = json.load(open(f_, encoding="utf-8"))
        except Exception:
            continue
        comps = d.get("Components", {})
        n_norm, n_ll = [], 0
        for sec, c in comps.items():
            if not sec.endswith("Inventory") or not isinstance(c, dict):
                continue
            items = (c.get("Inventory") or {}).get("Items") or {}
            for slot, it in (items.items() if isinstance(items, dict) else enumerate(items)):
                if not isinstance(it, dict):
                    continue
                iid = str(it.get("Id", ""))
                if not pat.match(iid) or "Multitool" in iid or "Harvester" in iid:
                    continue
                g = (it.get("Metadata") or {}).get("SkyyGear")
                if isinstance(g, dict) and g.get("ll") == 1:
                    n_ll += 1
                else:
                    n_norm.append("%s:%s" % (sec, iid))
        rep_.append((os.path.basename(f_)[:8], n_ll, n_norm))
    K.notes.append("LIVE313 players (file, lifelong stacks, normal stacks the first look removes): %s" % rep_)
    K.check(len(rep_) >= 1, "LIVE313: the live player files were read (%d)" % len(rep_))
    K.save()


# ====================================================================================================== main
def child(env, *args):
    cmd = [sys.executable, os.path.abspath(__file__)] + list(args) + ["--dir", SCRATCH, "--jar", JAR, "--root", SCR_ROOT]
    return subprocess.run(cmd, env=env)


def take(path, label):
    if not os.path.isfile(path):
        check(False, "%s: the child wrote no result" % label)
        return None
    d = json.load(open(path))
    OKS[0] += d["ok"]
    for f in d["fails"]:
        w = [why for pre, why in WAIVE if str(f).startswith(pre)]
        if w:
            WAIVED.append("%s: %s (%s)" % (label, str(f)[:140], w[0]))
            continue
        FAILS.append("%s: %s" % (label, f))
    for n in d.get("notes", []):
        print("  note (%s): %s" % (label, str(n)[:700]))
    return d


def main():
    for flag, fn in (("--mkfake", lambda: H310["run_mkfake10"](arg("--mkfake"))), ("--h313", lambda: run_h313(arg("--out"))),
                     ("--live313", lambda: run_live313(arg("--out"))),
                     ("--h312", lambda: H312["run_h312"](arg("--out"))), ("--live312", lambda: H312["run_live312"](arg("--out"))),
                     ("--h311", lambda: H311["run_h311"](arg("--out"))), ("--h310", lambda: H310["run_h310"](arg("--out"))),
                     ("--life", lambda: H35["run_life"](arg("--out"))),
                     ("--verify", lambda: H["run_verify"](arg("--out"))), ("--h39", lambda: H39["run_h39"](arg("--out"))),
                     ("--h38", lambda: H38["run_h38"](arg("--out"))), ("--h37", lambda: H37["run_h37"](arg("--out"))),
                     ("--g36", lambda: H36["run_g36"](arg("--out"))), ("--snd", lambda: H36["run_snd"](arg("--out"))),
                     ("--till", lambda: H35["run_till"](arg("--out"))), ("--audit", lambda: H["run_audit"](arg("--out")))):
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
    _known = {"--only", "--keep", "--dir", "--jar", "--root", "--out"}
    _unk = [a for a in sys.argv[1:] if a.startswith("--") and a not in _known]
    if _unk:
        print("unknown child flag(s) %s - nothing run" % _unk)
        sys.exit(2)
    for f_ in (JAR, J312, FI7_SRC, H38["AR26"], H36["FI6_SRC"], H35["CO_SRC"]):
        assert os.path.isfile(f_), f_
    sc = os.path.realpath(SCRATCH)
    assert sc.startswith(os.path.realpath(SCR_ROOT) + os.sep), "the scratch folder must be inside " + SCR_ROOT
    shutil.rmtree(SCRATCH, ignore_errors=True)
    for sub in ("tmp", "packs", "players"):
        os.makedirs(os.path.join(SCRATCH, sub), exist_ok=True)
    shutil.copyfile(H35["CO_SRC"], H36["CO_JAR"])
    shutil.copyfile(H36["FI6_SRC"], H36["FI_JAR"])
    for f_ in glob.glob(os.path.join(H35["LIVE_PLAYERS"], "*.json")):
        shutil.copyfile(f_, os.path.join(SCRATCH, "players", os.path.basename(f_)))
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.environ["TEMP"] = os.environ["TMP"] = env["TEMP"]
    env_312 = dict(env)
    env_312["JAVA_TOOL_OPTIONS"] = env["JAVA_TOOL_OPTIONS"] + " -Dskyy.harness.noNormOff=true"
    env_311 = dict(env_312)
    env_311["JAVA_TOOL_OPTIONS"] = env_312["JAVA_TOOL_OPTIONS"] + " -Dskyy.harness.noCanKit=true"
    env_old = dict(env_311)
    env_old["JAVA_TOOL_OPTIONS"] = env_311["JAVA_TOOL_OPTIONS"] + " -Dskyy.harness.noPoleKit=true"
    only = arg("--only")
    want = (lambda x: not only or x in only.split(","))
    try:
        if want("assets"):
            run_assets313()
        p = child(env, "--mkfake", FAKE_DIR)
        check(p.returncode == 0, "F: the stand-ins were generated")
        # the 0.3.12 order (the children share the scratch gear home): the old ones, L35, then h311 / h312 / live, then ours
        def run_children(lst):
            for label, flag, ev in lst:
                if not want(label):
                    continue
                out = os.path.join(SCRATCH, "%s.json" % label)
                pr = child(ev, flag, "--out", out)
                check(pr.returncode == 0, "%s: the child exited cleanly (%s)" % (label, pr.returncode))
                take(out, label)
        run_children((("h310", "--h310", env_old), ("h39", "--h39", env_old), ("verify", "--verify", env_old), ("h38", "--h38", env_old),
                      ("h37", "--h37", env_old), ("g36", "--g36", env_old), ("snd", "--snd", env_old), ("till", "--till", env_old)))
        if want("life"):
            _why39 = "0.3.9 by design: Identify moved to the Identify tab; the 0.3.5 check clicks it on the Anvil tab (H39 I covers the reveal)"
            H37["L37_EXTRA"].extend([("G35 R1:", _why39), ("G35 R2:", _why39), ("G35 R3:", _why39), ("G35 R4", _why39), ("G35 R5:", _why39)])
            H37["L37_EXTRA"].append(("G35 P6:", "0.3.11 fix round by design: with the kit off /pole says 'You have no lifelong fishing pole - this server hands none out (lifelong.poleKit is off). A pole a quest gave you: hold it and type /lifelong.' (no Marlow pole since SkyyQuests 0.3.4); the exact-copy half is unchanged"))
            H37["L37_EXTRA"].append(("G35 P7 FIX 2", "0.3.11 fix round by design: the refusal reads 'Only a fishing pole a quest gave you can become your lifelong pole' (no Marlow pole since SkyyQuests 0.3.4); still refused, nothing written"))
            H37["L37_EXTRA"].append(("M: a NEW profile's first join", "0.3.12 by design: GearLL.KCRUDE has 6 kinds (+ the watering can); the four Crude Common tools still land in storage 0-3 exactly as checked (the can comes from the kit, off here: noCanKit)"))
            n0 = len(H37["FAILS"])
            H37["run_l35"](env_old)
            for f_ in H37["FAILS"][n0:]:
                w = [why for pre, why in WAIVE if str(f_).startswith(pre)]
                if w:
                    WAIVED.append("L35: %s (%s)" % (str(f_)[:140], w[0]))
                else:
                    FAILS.append("L35: " + f_)
            OKS[0] += H37["OKS"][0]
        run_children((("h311", "--h311", env_311), ("h312", "--h312", env_312), ("live", "--live312", env_312), ("h313", "--h313", env),
                      ("live313", "--live313", env)))
        if want("audit"):
            outa = os.path.join(SCRATCH, "audit.json")
            pa = child(env_old, "--audit", "--out", outa)
            check(pa.returncode == 0 and os.path.isfile(outa), "AA: the engine-access audit child ran")
            if os.path.isfile(outa):
                a = json.load(open(outa))
                check(not a["refused"] and a["refs"] > 10000, "AA: engine-access audit: %d references in %d classes, refused %s" % (a["refs"], a["classes"], a["refused"][:5]))
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyGear %s harness: %d ok, %d fail(s), %d waived (by design)" % (VERSION, OKS[0], len(FAILS), len(WAIVED)))
    for w in WAIVED:
        print("WAIVED:", w)
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
