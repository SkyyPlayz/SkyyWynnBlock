"""Harness for SkyyGear 0.2.20 (MULTITOOL RECIPE WITHOUT THE SHOVEL: every tier = 1 pickaxe + 1 hatchet; tools/gear_0_2_20_patch.py header).
Build first:
    python tools/gear_0_2_20_patch.py && python SkyyGear/build_skyygear_0.2.20.py

    python SkyyGear/test_skyygear_0.2.20.py [--jar <SkyyGear-0.2.20.jar>] [--old <SkyyGear-0.2.19.jar>] [--mt <Multitools-1.2.9.jar>] [--dir <scratch>] [--keep]

The 0.2.11 harness's helpers (stand-ins F, verify A, the bare-server boot, the engine-access audit AA) are loaded from
SkyyGear/test_skyygear_0.2.11.py (as the 0.2.12 - 0.2.19 harnesses do). The Multitools jar is COPIED into the scratch folder (read-only source:
UserData/Mods/Multitools-1.2.9.jar) and loaded from there as its own pack.
  S  non-class entries 0.2.19 -> 0.2.20: only the manifest changed (no shovel words); the same class files; nothing of the Multitools mod shipped
  A  every class of the jar loads + verifies (-Xverify:all)
  M  MULTITOOLS, twice: one child per jar (0.2.19, then 0.2.20 with -Xverify:all) boots the bare server (vanilla pack + the jar as its own pack,
     the vanilla tools reloaded once the block sets are in, every item recipe generated like CraftingPlugin.onItemAssetLoad, the Multitools jar
     as pack IBC:Multitools) and EXECUTES every changed GearMulti path: replaceAll -> one(i, list) -> want(i) for all 8 tiers (Iron = pickaxe +
     hatchet in 0.2.20, + the Iron shovel in 0.2.19), same id / bench / time / knowledge / output; the start line words; a second run is
     idempotent; the engine's own input check (CraftingManager.removeInputFromInventory) takes a plain Iron pickaxe + hatchet (no shovel) and
     leaves a shovel alone; salvage(all) on the REAL Multitools salvage (Iron stays as it is - under its pickaxe + hatchet salvage; Onyxium is
     removed); a synthetic over-cap Iron salvage is clamped to the pickaxe + hatchet salvage (4 ore - 0.2.19 allowed 6 with the shovel); a
     reloaded Iron multitool (LoadedAssetsEvent(Item) through GearBoxL) gets pickaxe + hatchet back; part.multitool off = no recipe work;
     the fresh config text (heading, marker, help) has no shovel words
  C  CLASS COMPARE 0.2.19 -> 0.2.20 (javassist members): only GearMulti (want / one / salvage / replaceAll, made gone), GearCfg (the MT_HEAD /
     MT_MARK constants, inlined into defaultsText / mtUpdate) and CfgRows (the help text) differ; GearBoxL's change is a comment only
  D  START TWICE on a scratch COPY of the live Skyy_SkyyGear folder with each jar: the 2nd start changes nothing; 0.2.20 writes the same bytes as
     0.2.19 except the 3 multitool comment lines of the block migrate0218 appends (heading, marker, help) - no key, no value differs
  AA THE ENGINE-ACCESS AUDIT
Scratch: tools/dev/scratch/gear0220/harness (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B

VERSION = "0.2.20"
OLD_VERSION = "0.2.19"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCR_ROOT = os.path.abspath(arg("--root", os.path.join(TOOLS, "dev", "scratch", "gear0220")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyGear-%s.jar" % OLD_VERSION)))      # read only
MT_SRC = os.path.abspath(arg("--mt", os.path.join(B.MODS_DIR, "Multitools-1.2.9.jar")))           # read only - copied into the scratch folder
MT_JAR = os.path.join(SCRATCH, "mt", "Multitools-1.2.9.jar")
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyGear")
PKG = "com.skyy.gear."
MULTI_PRE = "Tool_Hatchet_Pickaxe_Multitool_"
MULTI_TIERS = ["Crude", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"]
OLD_HEAD = "# ---- Multitools: the Multitools mod's multitools cost a pickaxe + hatchet (+ shovel) and count as both (SkyyGear 0.2.18) ----"
NEW_HEAD = "# ---- Multitools: the Multitools mod's multitools cost a pickaxe + hatchet of their tier and count as both (SkyyGear 0.2.18) ----"
NEW_HELP = "# Multitools: Cost a pickaxe + hatchet of their tier, both tools. Off: hatchet stats; recipe at restart."
EXPECT_CHANGED = {"GearMulti", "GearCfg", "CfgRows"}

_H211 = os.path.join(HERE, "test_skyygear_0.2.11.py")
_t = open(_H211, encoding="utf-8").read()
_cut = _t.rindex('if __name__ == "__main__":')
H = {"__name__": "skyygear_h211", "__file__": _H211, "__builtins__": __builtins__}
exec(compile(_t[:_cut], _H211 + " (helpers)", "exec"), H)
H.update({"JAR": JAR, "OLD_JAR": OLD_JAR, "SCRATCH": SCRATCH, "FAKE_DIR": os.path.join(SCRATCH, "fake"), "VERSION": VERSION})
FAKE_DIR = H["FAKE_DIR"]
Child, _jvm, jar_classes = H["Child"], H["_jvm"], H["jar_classes"]
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


# ====================================================================================================== S: non-class entries
def run_assets():
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    ea = dict((n, zo.read(n)) for n in zo.namelist() if not n.endswith(".class"))
    eb = dict((n, zn.read(n)) for n in zn.namelist() if not n.endswith(".class"))
    added = sorted(set(eb) - set(ea))
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n])
    check(not added and not (set(ea) - set(eb)) and changed == ["manifest.json"] and b'"0.2.20"' in eb["manifest.json"]
          and b"cost a pickaxe + hatchet of their tier" in eb["manifest.json"] and b"(+ shovel)" not in eb["manifest.json"],
          "S: 0.2.19 -> 0.2.20: no file added / removed, only the manifest changed (version + no shovel words): + %s ~ %s" % (added[:3], changed[:3]))
    check(sorted(n for n in zn.namelist() if n.endswith(".class")) == sorted(n for n in zo.namelist() if n.endswith(".class")),
          "S: the same class files (no class added or removed)")
    if os.path.isfile(MT_JAR):
        mz = zipfile.ZipFile(MT_JAR)
        theirs = set(n for n in mz.namelist() if not n.endswith("/") and n not in ("META-INF/MANIFEST.MF", "manifest.json") and not n.endswith(".lang"))
        check(not (set(zn.namelist()) & theirs) and not [n for n in zn.namelist() if "Multitool" in n or "inkblindcat" in n.lower()],
              "S: the Multitools mod is never shipped or overridden (no path of its jar, no Multitool path)")


# ====================================================================================================== M: the multitool recipe (one jar)
def run_multi(out, which):
    from jpype import JClass, JArray, JInt, JShort, JFloat
    K = Child(out)
    new = which == "new"
    jar = JAR if new else OLD_JAR
    H["JAR"] = jar
    H["VERSION"] = VERSION if new else OLD_VERSION
    _jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=new, big=True)
    E = H["engine_boot"](K)
    ITEM = E["ITEM"]
    K.check(set(E["fail"]) <= set(E["vfail"]), "M/%s: the jar as its own pack: no failed store of its own (%s vs vanilla %s)" % (which, E["fail"], E["vfail"]))
    CRR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    HAL = JClass("java.util.ArrayList")
    # the bare boot decodes the Item store before the BlockSet store - load the vanilla Tool_* files again (as the 0.2.18 harness does)
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
    ng = gen_recipes(list(ITEM.getAssetMap().getAssetMap().values()))
    gid = lambda i: str(CRR.generateIdFromItemRecipe(ITEM.getAssetMap().getAsset(i), JInt(0)))
    rmap = CRR.getAssetMap().getAssetMap()
    K.check(ng > 300 and rmap.get(gid("Tool_Shovel_Iron")) is not None,
            "M/%s: %d item recipes generated like the engine (the Iron shovel has one - the case 0.2.19 asked for)" % (which, ng))
    P = lambda n: JClass(PKG + n)
    Cfg, Gear, GM, BoxL = P("GearCfg"), P("Gear"), P("GearMulti"), P("GearBoxL")
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
    # the fresh config text
    blk = FRESH[FRESH.index("# ---- Multitools:"):]
    if new:
        K.check(NEW_HEAD in FRESH and NEW_HELP in FRESH and "shovel" not in blk and "# SkyyGear 0.2.18 multitools (Skyy 2026-10-10)" in blk
                and "part.multitool=true" in blk, "M/new: the fresh file's multitool block has no shovel words (heading, marker, help), the "
                "marker id kept (migrate0218 finds older blocks): %s" % blk[:300])
    else:
        K.check(OLD_HEAD in FRESH and "shovel" in blk, "M/old: 0.2.19's fresh block still names the shovel")
    # part.multitool off: no recipe work
    apply(part__multitool="false")
    roff = str(GM.replaceAll())
    apply()
    K.check("OFF (part.multitool)" in roff and GM.DONE.size() == 0, "M/%s: part.multitool off -> no recipe work: %s" % (which, roff))
    # the Multitools jar (scratch copy) as pack IBC:Multitools (its Common files first)
    if not os.path.isfile(MT_JAR):
        K.notes.append("M: no Multitools jar - the recipe part is skipped")
        K.check(False, "M/%s: the Multitools jar is needed for the recipe checks" % which)
        K.save()
        return
    CAR = JClass("com.hypixel.hytale.server.core.asset.common.CommonAssetRegistry")
    FCA = JClass("com.hypixel.hytale.server.core.asset.common.asset.FileCommonAsset")
    mfs = JClass("java.nio.file.FileSystems").newFileSystem(JClass("java.nio.file.Paths").get(MT_JAR), JClass("java.util.HashMap")())
    with zipfile.ZipFile(MT_JAR) as mz_:
        for nm in mz_.namelist():
            if nm.startswith("Common/") and not nm.endswith("/"):
                CAR.addCommonAsset("IBC:Multitools", FCA(mfs.getPath("/" + nm), nm[len("Common/"):], hashlib.sha256(mz_.read(nm)).hexdigest(), None))
    mfail, mrec = E["loadpack"](MT_JAR, "IBC:Multitools", False)
    mitems = [ITEM.getAssetMap().getAsset(MULTI_PRE + t) for t in MULTI_TIERS]
    K.check(all(x is not None for x in mitems), "M/%s: the Multitools jar loaded as pack IBC:Multitools - its 8 items are in the Item store (%s)" % (which, mfail))
    ngm = gen_recipes(mitems)
    rid = lambda t: gid(MULTI_PRE + t)

    def inputs(r):
        return [(str(m.getItemId()) if m.getItemId() is not None else "res:" + str(m.getResourceTypeId()), int(m.getQuantity())) for m in r.getInput()]

    def outs(r):
        return [(str(m.getItemId()), int(m.getQuantity())) for m in (r.getOutputs() or [])]

    def sid(t):
        hits_ = [str(r.getId()) for r in list(CRR.getAssetMap().getAssetMap().values()) if r.getInput() is not None and len(r.getInput()) == 1
                 and r.getInput()[0] is not None and str(r.getInput()[0].getItemId()) == MULTI_PRE + t]
        return hits_[0] if len(hits_) == 1 else "none:%d" % len(hits_)
    SID = dict((t, sid(t)) for t in MULTI_TIERS)
    before = dict((t, CRR.getAssetMap().getAsset(rid(t))) for t in MULTI_TIERS)
    sal0 = dict((t, CRR.getAssetMap().getAsset(SID[t])) for t in MULTI_TIERS)
    K.check(ngm == 8 and all(before[t] is not None for t in MULTI_TIERS) and all(sal0[t] is not None for t in MULTI_TIERS),
            "M/%s: before - the Multitools mod's own 8 recipes (Iron: %s) and its 8 salvage recipes are live" % (which, inputs(before["Iron"])))
    res1 = str(GM.replaceAll())
    after = dict((t, CRR.getAssetMap().getAsset(rid(t))) for t in MULTI_TIERS)
    OBJ = JClass("java.util.Objects")
    badr = []
    for t in MULTI_TIERS:
        want = [("Tool_Pickaxe_" + t, 1), ("Tool_Hatchet_" + t, 1)] + ([("Tool_Shovel_Iron", 1)] if t == "Iron" and not new else [])
        a, b = after[t], before[t]
        if not (a is not None and inputs(a) == want and str(a.getId()) == rid(t) and OBJ.equals(a.getBenchRequirement(), b.getBenchRequirement())
                and float(a.getTimeSeconds()) == float(b.getTimeSeconds()) and bool(a.isKnowledgeRequired()) == bool(b.isKnowledgeRequired())
                and int(a.getRequiredMemoriesLevel()) == int(b.getRequiredMemoriesLevel()) and str(a.getPrimaryOutput().getItemId()) == MULTI_PRE + t
                and outs(a) == outs(b) and not a.equals(b)):
            badr.append((t, inputs(a) if a is not None else None))
    K.save_iron = inputs(after["Iron"])
    if new:
        K.check(not badr and "8 found, 8 recipe(s) set to pickaxe + hatchet of their tier" in res1 and "shovel" not in res1,
                "M/new: EVERY multitool recipe = 1 pickaxe + 1 hatchet of its tier - Iron too (no shovel); same id, bench, time, knowledge, output; "
                "the start line has no shovel words: %s | %s" % (badr[:2], res1))
        K.check([str(x) for x in GM.want(JInt(2))] == ["Tool_Pickaxe_Iron", "Tool_Hatchet_Iron"]
                and str(GM.DONE.get(rid("Iron"))) == "Tool_Pickaxe_Iron + Tool_Hatchet_Iron",
                "M/new: want(Iron) = pickaxe + hatchet, DONE says so: %s" % GM.DONE.get(rid("Iron")))
    else:
        K.check(not badr and "no craftable shovel for Crude, Copper, Thorium, Cobalt, Adamantite, Mithril, Onyxium" in res1,
                "M/old: 0.2.19 (contrast): Iron = pickaxe + hatchet + the Iron shovel, the others pickaxe + hatchet: %s | %s" % (badr[:2], res1))
    # the engine's own input check against the new Iron recipe: plain Iron pickaxe + hatchet (no shovel)
    CMG = JClass("com.hypixel.hytale.builtin.crafting.component.CraftingManager")
    rmi = [m_ for m_ in CMG.class_.getDeclaredMethods() if str(m_.getName()) == "removeInputFromInventory" and len(m_.getParameterTypes()) == 3][0]
    rmi.setAccessible(True)
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    rc_ = CRR.getAssetMap().getAsset(rid("Iron"))

    def craft_try(ids):
        c_ = SIC(JShort(9))
        for i_, id_ in enumerate(ids):
            c_.setItemStackForSlot(JShort(i_), IS(id_, JInt(1)))
        ok_ = bool(rmi.invoke(None, c_, rc_, JInt(1)))
        left = [str(c_.getItemStack(JShort(i_)).getItemId()) for i_ in range(9)
                if c_.getItemStack(JShort(i_)) is not None and not c_.getItemStack(JShort(i_)).isEmpty()]
        return ok_, left
    two = craft_try(["Tool_Pickaxe_Iron", "Tool_Hatchet_Iron"])
    three = craft_try(["Tool_Pickaxe_Iron", "Tool_Hatchet_Iron", "Tool_Shovel_Iron"])
    if new:
        K.check(two == (True, []) and three == (True, ["Tool_Shovel_Iron"]),
                "M/new: the engine's input check (CraftingManager.removeInputFromInventory) crafts the Iron multitool from a plain Iron pickaxe + "
                "hatchet; a shovel in the inventory is left alone: %s | %s" % (two, three))
    else:
        K.check(not two[0] and three == (True, []), "M/old: 0.2.19 (contrast) needed the shovel: %s | %s" % (two, three))
    res2 = str(GM.replaceAll())
    K.check("0 recipe(s) set" in res2 and "8 already set" in res2 and all(CRR.getAssetMap().getAsset(rid(t)).equals(after[t]) for t in MULTI_TIERS),
            "M/%s: a second run changes nothing (idempotent): %s" % (which, res2[:120]))
    # the salvage cap on the real Multitools salvage
    byin = {}
    for r in list(CRR.getAssetMap().getAssetMap().values()):
        ins = r.getInput()
        if ins is not None and len(ins) == 1 and ins[0] is not None and ins[0].getItemId() is not None:
            byin.setdefault(str(ins[0].getItemId()), []).append(r)

    def allow(tools, item):
        return sum(max([0] + [sum(q for i_, q in outs(r) if i_ == item) for r in byin.get(tl, [])]) for tl in tools)
    over, rows = [], []
    for t in MULTI_TIERS[:-1]:
        tl = ["Tool_Pickaxe_" + t, "Tool_Hatchet_" + t]
        s_ = CRR.getAssetMap().getAsset(SID[t])
        rows.append("%s %s <= %s" % (t, outs(s_) if s_ is not None else None, [(it_, allow(tl, it_)) for it_, q0 in outs(sal0[t])]))
        if s_ is None or not s_.equals(sal0[t]) or any(sum(q for i_, q in outs(s_) if i_ == it_) > allow(tl, it_) for it_, q0 in outs(s_)):
            over.append((t, outs(s_) if s_ is not None else None))
    K.check(not over and CRR.getAssetMap().getAsset(SID["Onyxium"]) is None and str(GM.SALV.get(SID["Onyxium"])) == "removed"
            and SID["Iron"] not in GM.SALV,
            "M/%s: the salvage cap on the REAL Multitools salvage against the PICKAXE + HATCHET salvage: Crude..Mithril (Iron %s vs pickaxe + "
            "hatchet %d ore) give back no more and stay as they are; Onyxium is removed: %s" % (which, outs(sal0["Iron"]), allow(["Tool_Pickaxe_Iron", "Tool_Hatchet_Iron"], "Ore_Iron"), over))
    K.notes.append("salvage rows (%s): %s" % (which, " | ".join(rows)))
    # a synthetic over-cap Iron salvage: 0.2.20 clamps to the pickaxe + hatchet salvage, 0.2.19 allowed the shovel's share too
    MQc = JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
    MQA = JArray(MQc)
    fid = CRR.class_.getDeclaredField("id")
    fid.setAccessible(True)
    MI = MULTI_PRE + "Iron"
    fake = CRR(MQA([MQc(MI, None, None, JInt(1), None)]), MQc("Ore_Iron", None, None, JInt(9), None),
               MQA([MQc("Ore_Iron", None, None, JInt(9), None), MQc("Ingredient_Hide_Light", None, None, JInt(9), None),
                    MQc("Ingredient_Bar_Gold", None, None, JInt(5), None)]), JInt(1), sal0["Iron"].getBenchRequirement(), JFloat(4.0), False, JInt(0))
    fid.set(fake, "SkyyTest_Salvage_Multi_Iron")
    lst = HAL()
    lst.add(fake)
    CRR.getAssetStore().loadAssets("Hytale:Hytale", lst)
    GM.replaceAll()
    fk = CRR.getAssetMap().getAsset("SkyyTest_Salvage_Multi_Iron")
    fko = outs(fk) if fk is not None else None
    GM.replaceAll()
    fk2 = CRR.getAssetMap().getAsset("SkyyTest_Salvage_Multi_Iron")
    exp = [("Ore_Iron", 4), ("Ingredient_Hide_Light", 2)] if new else [("Ore_Iron", 6), ("Ingredient_Hide_Light", 3)]
    K.check(fko == exp and str(fk.getPrimaryOutput().getItemId()) == "Ore_Iron" and int(fk.getPrimaryOutput().getQuantity()) == exp[0][1]
            and str(GM.SALV.get("SkyyTest_Salvage_Multi_Iron")) == "capped" and fk2.equals(fk),
            "M/%s: a synthetic over-cap Iron multitool salvage (9 ore, 9 hide, 5 gold bars) is CLAMPED to %s (%s); a second run keeps it: %s"
            % (which, exp, "pickaxe + hatchet" if new else "0.2.19: pickaxe + hatchet + shovel", fko))
    # a reloaded Iron multitool: the engine regenerates the mod's recipe, then GearBoxL (LoadedAssetsEvent(Item), LAST)
    gen_recipes([ITEM.getAssetMap().getAsset(MI)])
    back = inputs(CRR.getAssetMap().getAsset(rid("Iron")))
    LAE = JClass("com.hypixel.hytale.assetstore.event.LoadedAssetsEvent")
    AUQ = JClass("com.hypixel.hytale.assetstore.AssetUpdateQuery")
    lm = JClass("java.util.HashMap")()
    lm.put(MI, ITEM.getAssetMap().getAsset(MI))
    BoxL().accept(LAE(ITEM.class_, ITEM.getAssetMap(), lm, False, AUQ.DEFAULT))
    rel = inputs(CRR.getAssetMap().getAsset(rid("Iron")))
    K.check(back != rel and rel == ([("Tool_Pickaxe_Iron", 1), ("Tool_Hatchet_Iron", 1)] + ([] if new else [("Tool_Shovel_Iron", 1)])),
            "M/%s: a reloaded Iron multitool (the engine regenerated the mod's recipe %s) gets our recipe again through GearBoxL: %s" % (which, back[:2], rel))
    K.save(iron=K.save_iron, res1=res1)


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
    add = sorted(set(nb) - set(na))
    gone = sorted(set(na) - set(nb))
    print("C. class compare %s -> %s: + %s - %s" % (OLD_VERSION, VERSION, add, gone))
    for k in sorted(diffs):
        print("   %-16s %s" % (k, ", ".join(diffs[k])[:1200]))
    K.check(not add and not gone, "C: no class added or removed: + %s - %s" % (add, gone))
    K.check(set(diffs) == EXPECT_CHANGED, "C: exactly GearMulti / GearCfg / CfgRows changed (the version string is normalised): %s" % sorted(diffs))
    want = {"GearMulti": {"-m made", "-m want", "+m want", "-m one", "+m one", "-m salvage", "+m salvage", "~m replaceAll"},
            "GearCfg": {"~<clinit>", "~m defaultsText", "~m mtUpdate"}, "CfgRows": {"~<clinit>"}}       # MT_HEAD / MT_MARK are inlined constants
    bad = {}
    for k, v in want.items():
        got = set(diffs.get(k, []))
        if got != v:
            bad[k] = (sorted(v - got), sorted(got - v))
    K.check(not bad, "C: the classes changed exactly where the patch says (missing / extra): %s" % bad)
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
    for flag, fn in (("--mkfake", lambda: H["run_mkfake"](arg("--mkfake"))), ("--verify", lambda: H["run_verify"](arg("--out"))),
                     ("--multi", lambda: run_multi(arg("--out"), arg("--multi"))),
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
    assert os.path.isfile(JAR) and os.path.isfile(OLD_JAR), (JAR, OLD_JAR)
    sc = os.path.realpath(SCRATCH)
    assert sc.startswith(os.path.realpath(SCR_ROOT) + os.sep), "the scratch folder must be inside " + SCR_ROOT
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"), exist_ok=True)
    with zipfile.ZipFile(OLD_JAR) as z_:
        assert '"Version": "%s"' % OLD_VERSION in z_.read("manifest.json").decode("utf-8"), "the old jar is not " + OLD_VERSION
    if os.path.isfile(MT_SRC):
        os.makedirs(os.path.dirname(MT_JAR), exist_ok=True)
        shutil.copyfile(MT_SRC, MT_JAR)          # read-only source; the children load the scratch copy
    else:
        print("note: no Multitools jar - the recipe checks cannot run")
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.environ["TEMP"] = os.environ["TMP"] = env["TEMP"]
    try:
        run_assets()
        p = child(env, "--mkfake", FAKE_DIR)
        check(p.returncode == 0, "F: the stand-ins were generated")
        for label, flag in (("verify", "--verify"), ("compare", "--compare")):
            out = os.path.join(SCRATCH, "%s.json" % label)
            pr = child(env, flag, "--out", out)
            check(pr.returncode == 0, "%s: the child exited cleanly (%s)" % (label, pr.returncode))
            take(out, label)
        mres = {}
        for which in ("old", "new"):
            out = os.path.join(SCRATCH, "multi-%s.json" % which)
            pr = child(env, "--multi", which, "--out", out)
            check(pr.returncode == 0, "multi-%s: the child exited cleanly (%s)" % (which, pr.returncode))
            mres[which] = take(out, "multi-" + which)
        if mres.get("old") and mres.get("new"):
            print("M. Iron multitool recipe: 0.2.19 %s -> 0.2.20 %s" % (mres["old"].get("iron"), mres["new"].get("iron")))
            print("M. 0.2.20 start line: %s" % mres["new"].get("res1"))
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
            lo, ln = res["old"]["cfg"].splitlines(), res["new"]["cfg"].splitlines()
            dif = [(a, b) for a, b in zip(lo, ln) if a != b]
            ok_d = len(lo) == len(ln) and all(a.startswith("#") and b.startswith("#") and "shovel" in a and "shovel" not in b for a, b in dif) \
                and len(dif) in (0, 3)
            check(ok_d, "D: 0.2.20 starts the live copy to the same config.properties as 0.2.19 except the multitool comment lines (heading, "
                  "marker, help - no key / value differs): %d differing line(s) %s" % (len(dif), dif[:3]))
            print("D. config.properties old vs new: %d line(s) differ (comments only): %s" % (len(dif), [b for a, b in dif]))
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
