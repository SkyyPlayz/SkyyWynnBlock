"""Harness for SkyyGear 0.2.21 (MERGE THE ROLLS: /multitool merges a rolled pickaxe + hatchet; tools/gear_0_2_21_patch.py header).
Build first:
    python tools/gear_0_2_21_patch.py && python SkyyGear/build_skyygear_0.2.21.py

    python SkyyGear/test_skyygear_0.2.21.py [--jar <SkyyGear-0.2.21.jar>] [--old <SkyyGear-0.2.20.jar>] [--mt <Multitools-1.2.9.jar>] [--dir <scratch>] [--keep]

The 0.2.11 harness's helpers (stand-ins F, verify A, the bare-server boot, the engine-access audit AA) are loaded from
SkyyGear/test_skyygear_0.2.11.py (as the 0.2.12 - 0.2.20 harnesses do); this harness adds its own stand-ins (MergeFail - a container that
refuses / throws on demand, FakeMultiPage - rebuild / close counted, FakePR - a PlayerRef that records messages). The Multitools jar is
COPIED into the scratch folder (read-only source: UserData/Mods/Multitools-1.2.9.jar) and loaded from there as its own pack.
  S  non-class entries 0.2.20 -> 0.2.21: only the manifest changed; classes added = GearMerge, MultiPage, MultiCmd; nothing of the Multitools
     mod shipped
  A  every class of the jar loads + verifies (-Xverify:all)
  E  THE BENCH RULE on the REAL CraftingManager (bare server + Multitools pack, our Iron recipe live): removeInputFromInventory never takes a
     stack with a SkyyGear document (a rolled pickaxe beside a plain one: the plain one goes; two rolled tools: refused, nothing taken; a
     Mythic pickaxe: refused); the engine takes the FIRST matching slot (consumption order = slot order); getMaterialCraftLimit counts 0 for
     rolled-only tools (craftItem / queueCraft return before CraftRecipeEvent$Pre)
  G  GearMerge EXECUTED: tierOf / famOf / loaded / plain / why (every refusal) / check / capOf / addLines / doc (Legendary + plain = the
     pickaxe's lines; Rare + Unique = the strongest 3 merged lines; the caps; dropped keys; same key = the higher; two plain = the craft roll;
     rfN / rf) / preview / rows / merge (made; only the picked stacks used; a second click refused; failure at (b) = restored; failure at (a)
     both ways; restore failing = loss logged, never a copy; same slot) + gear.log lines + item counts; no Smithing XP (skill:fn:addxp count 0)
  P  MultiPage + MultiCmd EXECUTED through the stand-in store: build / list / bench / slotLine (none, picked, preview, both plain, refused,
     made), pick (pickaxe, hatchet, put back, epoch), preselect, handleDataEvent (sel, merge, refresh, prev, next, back, bad), doMerge guards
     (double click, profile:busy, missing pick, epoch); /multitool (off, mod missing, open)
  C  CLASS COMPARE 0.2.20 -> 0.2.21 (javassist members): added GearMerge / MultiPage / MultiCmd; changed exactly GearMulti.replaceAll (start line)
     and SkyyGearPlugin.setup (the command + the ready line)
  D  START TWICE on a scratch COPY of the live Skyy_SkyyGear folder with each jar: the 2nd start changes nothing; 0.2.21 writes the same
     config.properties as 0.2.20 (no config change in this round)
  AA THE ENGINE-ACCESS AUDIT
Fix round checks: FIX 1 (multitool caps), FIX 2 (loss warnings on the page), FIX 3 (MERGE-BEGIN on disk first), FIX 4 (post-swap
bookkeeping cannot throw), FIX C3 (the button after a merge). Run with --root tools/dev/scratch/<your folder> to use another scratch folder.
Scratch: tools/dev/scratch/gear0221/harness (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B

VERSION = "0.2.21"
OLD_VERSION = "0.2.20"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCR_ROOT = os.path.abspath(arg("--root", os.path.join(TOOLS, "dev", "scratch", "gear0221")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyGear-%s.jar" % OLD_VERSION)))      # read only
MT_SRC = os.path.abspath(arg("--mt", os.path.join(B.MODS_DIR, "Multitools-1.2.9.jar")))           # read only - copied into the scratch folder
MT_JAR = os.path.join(SCRATCH, "mt", "Multitools-1.2.9.jar")
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyGear")
PKG = "com.skyy.gear."
MULTI_PRE = "Tool_Hatchet_Pickaxe_Multitool_"
MULTI_TIERS = ["Crude", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"]
NEW_CLASSES = {"GearMerge", "MultiPage", "MultiCmd"}
MKEYS = ["mpow", "cpow", "mfort", "ffort", "mwis", "fwis"]

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


# ====================================================================================================== S: non-class entries
def run_assets():
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    ea = dict((n, zo.read(n)) for n in zo.namelist() if not n.endswith(".class"))
    eb = dict((n, zn.read(n)) for n in zn.namelist() if not n.endswith(".class"))
    added = sorted(set(eb) - set(ea))
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n])
    check(not added and not (set(ea) - set(eb)) and changed == ["manifest.json"] and b'"0.2.21"' in eb["manifest.json"]
          and b"/multitool merges rolled ones" in eb["manifest.json"],
          "S: 0.2.20 -> 0.2.21: no file added / removed, only the manifest changed (version + the /multitool words): + %s ~ %s" % (added[:3], changed[:3]))
    ca = set(n for n in zo.namelist() if n.endswith(".class"))
    cb = set(n for n in zn.namelist() if n.endswith(".class"))
    check(not (ca - cb) and set(n.split("/")[-1][:-6] for n in cb - ca) == NEW_CLASSES,
          "S: classes added = GearMerge, MultiPage, MultiCmd; none removed: + %s - %s" % (sorted(cb - ca), sorted(ca - cb)))
    if os.path.isfile(MT_JAR):
        mz = zipfile.ZipFile(MT_JAR)
        theirs = set(n for n in mz.namelist() if not n.endswith("/") and n not in ("META-INF/MANIFEST.MF", "manifest.json") and not n.endswith(".lang"))
        check(not (set(zn.namelist()) & theirs) and not [n for n in zn.namelist() if "inkblindcat" in n.lower() or "/Multitool" in n],
              "S: the Multitools mod is never shipped or overridden (no path of its jar)")


# ====================================================================================================== F+: this round's stand-ins
def run_mkfake2(out_dir):
    H["run_mkfake"](out_dir)          # starts the JVM (javassist + server jar + JAR) and writes the 0.2.11 stand-ins
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
    mf.addField(CtField.make("public boolean sticky;", mf))       # after one refusal every later set throws too
    mf.addField(CtField.make("public boolean tripped;", mf))
    mf.addConstructor(CtNewConstructor.make("public MergeFail(short n) { super(n); }", mf))
    mf.addMethod(CtNewMethod.make(
        "public com.hypixel.hytale.server.core.inventory.transaction.ItemStackSlotTransaction setItemStackForSlot(short s, %s i) {\n"
        "  if (this.tripped && this.sticky) throw new java.lang.IllegalStateException(\"test: the container refuses everything now\");\n"
        "  if (this.refuseId != null && i != null && this.refuseId.equals(i.getItemId())) { this.tripped = true; throw new java.lang.IllegalStateException(\"test: the slot refuses \" + this.refuseId); }\n"
        "  return super.setItemStackForSlot(s, i);\n}" % IS, mf))
    mf.addMethod(CtNewMethod.make(
        "public com.hypixel.hytale.server.core.inventory.transaction.SlotTransaction removeItemStackFromSlot(short s) {\n"
        "  if (this.rm == 1) throw new java.lang.IllegalStateException(\"test: remove refused\");\n"
        "  if (this.rm == 2) { super.removeItemStackFromSlot(s); throw new java.lang.IllegalStateException(\"test: removed, then failed\"); }\n"
        "  return super.removeItemStackFromSlot(s);\n}", mf))
    mf.writeFile(out_dir)
    fp = cp.makeClass(P + ".FakeMultiPage")
    fp.setSuperclass(cp.get(PKG + "MultiPage"))
    fp.addField(CtField.make("public int rebuilds;", fp))
    fp.addField(CtField.make("public int closes;", fp))
    fp.addConstructor(CtNewConstructor.make("public FakeMultiPage(com.hypixel.hytale.server.core.universe.PlayerRef pr) { super(pr); }", fp))
    fp.addMethod(CtNewMethod.make("public void rebuild() { this.rebuilds = this.rebuilds + 1; }", fp))
    fp.addMethod(CtNewMethod.make("public void close() { this.closes = this.closes + 1; }", fp))
    fp.writeFile(out_dir)
    PRc = cp.get("com.hypixel.hytale.server.core.universe.PlayerRef")
    if not JClass("javassist.Modifier").isFinal(PRc.getModifiers()):
        fr = cp.makeClass(P + ".FakePR")
        fr.setSuperclass(PRc)
        fr.addField(CtField.make("public java.util.ArrayList said;", fr))
        ctor = [c for c in PRc.getDeclaredConstructors()][0]
        n = len(ctor.getParameterTypes())
        fr.addConstructor(CtNewConstructor.make("public FakePR() { super(%s); }" % ", ".join(
            ("null" if not t.isPrimitive() else ("false" if t.getName() == "boolean" else "0")) for t in ctor.getParameterTypes()), fr))
        fr.addMethod(CtNewMethod.make("public void sendMessage(com.hypixel.hytale.server.core.Message m) { if (this.said == null) this.said = new java.util.ArrayList(); this.said.add(m == null ? \"null\" : String.valueOf(m.getRawText())); }", fr))
        fr.writeFile(out_dir)
    print("F+. MergeFail, FakeMultiPage%s written" % ("" if JClass("javassist.Modifier").isFinal(PRc.getModifiers()) else ", FakePR"))


# ====================================================================================================== E + G + P (one booted engine)
def run_merge(out):
    from jpype import JClass, JArray, JInt, JShort, JLong, JByte, JImplements, JOverride, JObject
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
    gid = lambda i: str(CRR.generateIdFromItemRecipe(ITEM.getAssetMap().getAsset(i), JInt(0)))
    P = lambda n: JClass(PKG + n)
    Cfg, Gear, GM, Merge, Data, Roll, Forge, Stamp, Lvl, Defs, Log = (P("GearCfg"), P("Gear"), P("GearMulti"), P("GearMerge"), P("GearData"),
                                                                     P("GearRoll"), P("GearForge"), P("GearStamp"), P("GearLevel"),
                                                                     P("GearDefs"), P("GearLog"))
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
    if not os.path.isfile(MT_JAR):
        K.check(False, "E: the Multitools jar is needed (UserData/Mods/Multitools-1.2.9.jar, copied to scratch)")
        K.save()
        return
    CAR = JClass("com.hypixel.hytale.server.core.asset.common.CommonAssetRegistry")
    FCA = JClass("com.hypixel.hytale.server.core.asset.common.asset.FileCommonAsset")
    mfs = JClass("java.nio.file.FileSystems").newFileSystem(JClass("java.nio.file.Paths").get(MT_JAR), JClass("java.util.HashMap")())
    with zipfile.ZipFile(MT_JAR) as mz_:
        for nm in mz_.namelist():
            if nm.startswith("Common/") and not nm.endswith("/"):
                CAR.addCommonAsset("IBC:Multitools", FCA(mfs.getPath("/" + nm), nm[len("Common/"):], hashlib.sha256(mz_.read(nm)).hexdigest(), None))
    E["loadpack"](MT_JAR, "IBC:Multitools", False)
    mitems = [ITEM.getAssetMap().getAsset(MULTI_PRE + t) for t in MULTI_TIERS]
    gen_recipes(mitems)
    res1 = str(GM.replaceAll())
    K.check(all(x is not None for x in mitems) and "8 found, 8 recipe(s) set to pickaxe + hatchet of their tier" in res1
            and res1.endswith("; rolled pickaxes / hatchets merge on /multitool"),
            "E: the Multitools pack is in, our 8 recipes are live, the start line names /multitool: %s" % res1[-160:])
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    U1 = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-0000000000a1")
    MID = MULTI_PRE + "Iron"
    PI, HI = "Tool_Pickaxe_Iron", "Tool_Hatchet_Iron"
    L = int(Roll.craftLevel(MID, U1))
    BA = JClass("org.bson.BsonArray")
    BS, BI32, BB = JClass("org.bson.BsonString"), JClass("org.bson.BsonInt32"), JClass("org.bson.BsonBoolean")

    def stack(iid, q=1):
        return IS(iid, JInt(q))

    def hand(iid, r, mods, lvl=None, extra=None):
        """a hand-made rolled tool document: rarity index r, mods = [(key, value)], lvl (default the multitool's craft level)"""
        d = Data.base(Data.kindFor(iid), JInt(r), True, "craft")
        d.put("tr", BI32(JInt(1)))
        d.put("lvl", BI32(JInt(L if lvl is None else lvl)))
        a = BA()
        for k_, v_ in mods:
            a.add(Data.mod(k_, JInt(v_)))
        d.put("mods", a)
        for k_, v_ in (extra or {}).items():
            d.put(k_, v_)
        return d

    def tool(iid, d, q=1):
        s_ = stack(iid, q)
        return s_ if d is None else Data.put(s_, d, None)

    def mods_of(d):
        return [(str(m.asDocument().getString("s").getValue()), int(m.asDocument().getInt32("v").getValue())) for m in Data.mods(d)]

    def rid_of(d):
        return str(Defs.R_ID[int(Data.rarity(d))])

    # ============================================================================ E: the bench rule on the REAL CraftingManager
    CMG = JClass("com.hypixel.hytale.builtin.crafting.component.CraftingManager")
    rmi = [m_ for m_ in CMG.class_.getDeclaredMethods() if str(m_.getName()) == "removeInputFromInventory" and len(m_.getParameterTypes()) == 3][0]
    rmi.setAccessible(True)
    gml = [m_ for m_ in CMG.class_.getDeclaredMethods() if str(m_.getName()) == "getMaterialCraftLimit"]
    rc_ = CRR.getAssetMap().getAsset(gid(MID))
    rolledP = tool(PI, Roll.newDoc(PI, JInt(3), True, "craft", JInt(L)))
    rolledH = tool(HI, Roll.newDoc(HI, JInt(1), True, "craft", JInt(L)))
    mythP = tool(PI, hand(PI, 5, [("mpow", 9)]))

    def bench(slots):
        c_ = SIC(JShort(9))
        for i_, s_ in slots.items():
            c_.setItemStackForSlot(JShort(i_), s_)
        lim = None
        if gml:
            gml[0].setAccessible(True)
            try:
                lim = int(gml[0].invoke(None, rc_, c_))
            except Exception as ex:
                lim = "err %s" % str(ex)[:60]
        ok_ = bool(rmi.invoke(None, c_, rc_, JInt(1)))
        left = dict((i_, (str(c_.getItemStack(JShort(i_)).getItemId()), str(Forge.fp(c_.getItemStack(JShort(i_))))))
                    for i_ in range(9) if c_.getItemStack(JShort(i_)) is not None and not c_.getItemStack(JShort(i_)).isEmpty())
        return ok_, left, lim
    a = bench({0: rolledP, 1: stack(PI), 2: stack(HI)})
    b = bench({0: rolledP, 1: rolledH})
    c = bench({0: stack(PI), 1: stack(HI), 5: stack(PI)})
    d = bench({0: mythP, 1: stack(HI)})
    K.check(a[0] and list(a[1].keys()) == [0] and a[1][0][1] == str(Forge.fp(rolledP)),
            "E: a rolled Iron pickaxe beside a plain one: the bench takes the PLAIN one + the plain hatchet; the rolled one stays untouched: %s" % (a[:2],))
    K.check(not b[0] and sorted(b[1].keys()) == [0, 1] and b[2] in (0, None),
            "E: a rolled pickaxe + a rolled hatchet: the bench refuses and takes NOTHING (getMaterialCraftLimit = %s -> craftItem / queueCraft "
            "return before CraftRecipeEvent$Pre): %s" % (b[2], b[:2]))
    K.check(c[0] and sorted(c[1].keys()) == [5], "E: consumption order = slot order: two plain pickaxes in slots 0 and 5 -> slot 0 is taken: %s" % (c[:2],))
    K.check(not d[0] and sorted(d[1].keys()) == [0, 1], "E: a Mythic pickaxe is never eaten by the bench (refused, nothing taken): %s" % (d[:2],))
    K.notes.append("bench rule: rolled+plain %s | rolled only %s (limit %s) | order %s | mythic %s" % (a[:2], b[:2], b[2], c[:2], d[:2]))

    # ============================================================================ G: GearMerge
    # XP counter (skill:fn:addxp) - a merge must never call it
    XP = [0]

    @JImplements("java.util.function.Function")
    class AddXp(object):
        @JOverride
        def apply(self, o):
            XP[0] += 1
            return JObject(JLong(1), JClass("java.lang.Long"))
    br = Gear.bridge()
    br.put("skill:fn:addxp", AddXp())
    K.check(int(Merge.tierOf(PI)) == 2 and int(Merge.tierOf("Tool_Hatchet_Onyxium")) == 7 and int(Merge.tierOf("Tool_Shovel_Iron")) == -1
            and int(Merge.tierOf(None)) == -1 and int(Merge.famOf(PI)) == 1 and int(Merge.famOf(HI)) == 3 and int(Merge.famOf("Tool_Pickaxe_Wood")) == 0
            and bool(Merge.loaded()), "G: tierOf / famOf / loaded (Iron = 2, Onyxium hatchet = 7, shovels and non-tier picks = none)")
    # T1 Legendary pickaxe + plain hatchet -> Legendary multitool with the pickaxe lines
    lp_doc = Roll.newDoc(PI, JInt(3), True, "craft", JInt(L))
    lp = tool(PI, lp_doc)
    ph = stack(HI)
    d1 = Merge.doc(MID, lp, ph, U1, JInt(L))
    lp_exp = [(k_, min(v_, int(Merge.capOf(Defs.sIndex(k_), MID, JInt(3), JInt(L))))) for k_, v_ in mods_of(lp_doc)]
    K.check(rid_of(d1) == "legendary" and int(Data.num(d1, "tr", 0)) == 1 and mods_of(d1) == lp_exp and len(mods_of(d1)) >= 3
            and int(Lvl.level(MID, d1)) == L and str(Data.str(d1, "src", "")) == "merge" and bool(Data.identified(d1)),
            "G: Legendary pickaxe + plain hatchet -> a LEGENDARY multitool with the pickaxe's lines %s at most the multitool cap -> %s (Lv %d, "
            "tr, src merge): %s" % (mods_of(lp_doc), lp_exp, L, mods_of(d1)))
    # FIX 1 (critic 1): the cap is the FRESH MULTITOOL's (6-key pool, no spare-slot boost), not the pickaxe's boosted single-tool cap
    sp_p = float(Roll.spare(JInt(3), JInt(3), JInt(len(Roll.pool(JInt(3), PI)))))
    sp_m = float(Roll.spare(JInt(3), JInt(3), JInt(len(Roll.pool(JInt(3), MID)))))
    c_pk = int(Merge.capOf(Defs.sIndex("mpow"), PI, JInt(3), JInt(L)))
    c_mt = int(Merge.capOf(Defs.sIndex("mpow"), MID, JInt(3), JInt(L)))
    c_bd = int(Roll.bounds(Defs.sIndex("mpow"), JInt(3), JInt(L))[1])
    d_f1 = Merge.doc(MID, tool(PI, hand(PI, 3, [("mpow", c_pk)])), stack(HI), U1, JInt(L))
    fresh_hi = 0
    for _i in range(400):
        for k_, v_ in mods_of(Roll.newDoc(MID, JInt(3), True, "craft", JInt(L))):
            if k_ == "mpow" and v_ > fresh_hi:
                fresh_hi = v_
    K.check(len(Roll.pool(JInt(3), MID)) == 6 and sp_m == 0.0 and c_mt == c_bd and mods_of(d_f1) == [("mpow", c_mt)] and fresh_hi <= c_mt
            and (sp_p == 0.0 or c_pk > c_mt),
            "FIX 1: Legendary caps at Lv %d: the pickaxe's boosted single-tool cap %d (boost %.1f%%) vs the multitool cap %d (boost %.1f%% = "
            "GearRoll.bounds %d); a pickaxe line at %d merges to %s; 400 fresh Legendary multitools never rolled mpow above %d (max seen %d)"
            % (L, c_pk, sp_p, c_mt, sp_m, c_bd, c_pk, mods_of(d_f1), c_mt, fresh_hi))
    K.notes.append("FIX 1: Legendary mpow cap Lv %d: pickaxe (boost %.1f%%) %d, multitool %d, merged %s, fresh max %d" % (L, sp_p, c_pk, c_mt, mods_of(d_f1), fresh_hi))
    # T2 Rare pickaxe (3 lines) + Unique hatchet (2 lines) -> Rare, the strongest 3 by value / cap
    rp_d = hand(PI, 2, [("mpow", 5), ("mfort", 3), ("mwis", 2)], extra={"rfN": BI32(JInt(4)), "rf": BS("Keen")})
    uh_d = hand(HI, 1, [("cpow", 6), ("ffort", 1)], extra={"rfN": BI32(JInt(7)), "rf": BS("Sturdy")})
    d2 = Merge.doc(MID, tool(PI, rp_d), tool(HI, uh_d), U1, JInt(L))
    caps = {}
    for k_, src in (("mpow", PI), ("mfort", PI), ("mwis", PI), ("cpow", HI), ("ffort", HI)):
        caps[k_] = int(Merge.capOf(Defs.sIndex(k_), MID, JInt(2), JInt(L)))
    vals = {"mpow": 5, "mfort": 3, "mwis": 2, "cpow": 6, "ffort": 1}
    capped = dict((k_, min(v_, caps[k_])) for k_, v_ in vals.items())
    order = [str(x) for x in Defs.S_KEY]
    exp = sorted(capped, key=lambda k_: (-capped[k_] / float(max(1, caps[k_])), order.index(k_)))[:int(Cfg.R_MODS[2])]
    exp2 = [(k_, capped[k_]) for k_ in order if k_ in exp]
    K.check(rid_of(d2) == "rare" and mods_of(d2) == exp2 and int(Data.num(d2, "rfN", 0)) == 7 and str(Data.str(d2, "rf", "")) == "Keen"
            and int(Cfg.R_MODS[2]) == 3, "G: Rare pickaxe + Unique hatchet -> RARE with the strongest %d of the 5 merged lines by value / cap "
            "(caps %s): %s; rfN = the higher (7), rf = the better tool's (Keen)" % (int(Cfg.R_MODS[2]), caps, mods_of(d2)))
    # T2b the better tool is the hatchet -> its reforge name
    d2b = Merge.doc(MID, tool(PI, hand(PI, 1, [("mpow", 2)], extra={"rf": BS("Keen")})), tool(HI, hand(HI, 3, [("cpow", 2)], extra={"rf": BS("Sturdy")})), U1, JInt(L))
    K.check(rid_of(d2b) == "legendary" and str(Data.str(d2b, "rf", "")) == "Sturdy" and not d2b.containsKey("rfN"),
            "G: Unique pickaxe + Legendary hatchet -> Legendary, the hatchet's reforge name, no rfN when neither had one")
    # T3 caps, dropped keys, the same key twice
    cap_mp = int(Merge.capOf(Defs.sIndex("mpow"), MID, JInt(3), JInt(L)))
    d3 = Merge.doc(MID, tool(PI, hand(PI, 3, [("mpow", 999), ("dpow", 5), ("str", 7), ("mwis", 0)])), tool(HI, hand(HI, 0, [("mpow", 3), ("cpow", 4)])), U1, JInt(L))
    K.check(mods_of(d3) == [("mpow", cap_mp), ("cpow", min(4, int(Merge.capOf(Defs.sIndex("cpow"), MID, JInt(3), JInt(L)))))]
            and int(Merge.LAST_DROPPED) == 3 and cap_mp < 999,
            "G: caps: mpow 999 -> %d (the most a fresh Legendary multitool rolls at Lv %d), dpow / str / a zero line dropped (3), the same key twice "
            "keeps the higher: %s" % (cap_mp, L, mods_of(d3)))
    # T3b a lower multitool level trims a line to the lower cap
    lo_cap = int(Merge.capOf(Defs.sIndex("mpow"), MID, JInt(3), JInt(1)))
    hi_line = int(Merge.capOf(Defs.sIndex("mpow"), MID, JInt(3), JInt(L)))
    d3b = Merge.doc(MID, tool(PI, hand(PI, 3, [("mpow", hi_line)])), stack(HI), U1, JInt(1))
    K.check(mods_of(d3b) == [("mpow", min(hi_line, lo_cap))] and int(Lvl.level(MID, d3b)) == int(Lvl.clamp(JInt(1))),
            "G: made at a lower level -> each line at most that level's cap (%d -> %d): %s" % (hi_line, lo_cap, mods_of(d3b)))
    # T3c over the count: a Normal + Normal merge keeps the 1 strongest line
    d3c = Merge.doc(MID, tool(PI, hand(PI, 0, [("mpow", 1)])), tool(HI, hand(HI, 0, [("cpow", 2)])), U1, JInt(L))
    K.check(rid_of(d3c) == "normal" and len(mods_of(d3c)) == int(Cfg.R_MODS[0]) == 1,
            "G: Normal (1 line) + Normal (1 line) -> Normal multitool, at most %d line (the strongest): %s" % (int(Cfg.R_MODS[0]), mods_of(d3c)))
    # T4 two plain tools -> the craft roll (like the bench)
    seen = {}
    for _i in range(300):
        dd = Merge.doc(MID, stack(PI), stack(HI), U1, JInt(L))
        seen[rid_of(dd)] = seen.get(rid_of(dd), 0) + 1
        if int(Data.num(dd, "tr", 0)) != 1 or str(Data.str(dd, "src", "")) != "craft" or int(Data.rarity(dd)) > 4:
            seen["bad"] = seen.get("bad", 0) + 1
    K.check("bad" not in seen and len(seen) >= 2 and seen.get("normal", 0) > 100,
            "G: two plain tools -> the normal craft roll (GearRoll.craftDoc: src craft, tr, never Mythic/Set/UT), 300 rolls: %s" % seen)
    # an old 0.2.16 tool document (no "tr", Normal, no lines) counts as plain
    old_doc = Data.base(Data.kindFor(PI), JInt(0), True, "legacy")
    K.check(bool(Merge.plain(None)) and bool(Merge.plain(old_doc)) and not bool(Merge.plain(lp_doc)),
            "G: plain = no document or an old document without tr / rarity / lines")
    # T5 refusals (why / check)
    mk_unread = stack(PI).withMetadata(JClass("org.bson.BsonDocument")(str(Defs.DOC_KEY), BS("broken")))
    newer = hand(PI, 2, [("mpow", 2)])
    newer.put("v", BI32(JInt(2)))
    unid = hand(HI, 2, [])
    unid.put("id", BB(False))
    setd = hand(PI, 0, [])
    setd.put("set", BS("mining_copper"))
    cases = [
        ("Mythic pickaxe", Merge.why(tool(PI, hand(PI, 5, [("mpow", 9)])), JInt(1)), "special tool"),
        ("Set pickaxe", Merge.why(tool(PI, hand(PI, 6, [])), JInt(1)), "special tool"),
        ("Untiered hatchet", Merge.why(tool(HI, hand(HI, 7, [])), JInt(3)), "special tool"),
        ("a set field", Merge.why(tool(PI, setd), JInt(1)), "special tool"),
        ("unidentified", Merge.why(tool(HI, unid), JInt(3)), "Identify that hatchet first"),
        ("unreadable", Merge.why(mk_unread, JInt(1)), "unreadable"),
        ("newer", Merge.why(tool(PI, newer), JInt(1)), "newer SkyyGear"),
        ("stack", Merge.why(stack(PI, 2), JInt(1)), "stack of 2"),
        ("wrong kind", Merge.why(stack("Tool_Shovel_Iron"), JInt(1)), "is not a pickaxe"),
        ("hatchet as pickaxe", Merge.why(stack(HI), JInt(1)), "is not a pickaxe"),
        ("nothing", Merge.why(None, JInt(3)), "Pick a hatchet"),
    ]
    bad = [(n_, str(w_)) for n_, w_, want in cases if w_ is None or want not in str(w_)]
    K.check(not bad and Merge.why(lp, JInt(1)) is None and Merge.why(ph, JInt(3)) is None,
            "G: why() refuses Mythic / Set / Untiered / a set field (special tools are never merged), unidentified, unreadable, newer data, "
            "stacks, wrong kinds, nothing picked; a rolled or plain tool is fine: %s" % bad)
    K.notes.append("refusal words: " + " | ".join("%s: %s" % (n_, str(w_)) for n_, w_, _w in cases[:5]))
    c_tier = Merge.check(stack("Tool_Pickaxe_Copper"), stack(HI), U1)
    apply(part__multitool="false")
    c_off = Merge.check(stack(PI), stack(HI), U1)
    apply(part__toolRarity="false")
    c_tr = Merge.check(stack(PI), stack(HI), U1)
    apply(**{"craft__belowBand": "block", "craft__levelFrom": "gate"})
    c_blk = Merge.check(stack(PI), stack(HI), U1)
    apply()
    c_ok = Merge.check(stack(PI), stack(HI), U1)
    K.check("same tier" in str(c_tier[0]) and "switched off" in str(c_off[0]) and "Tool rarity is off" in str(c_tr[0])
            and c_ok[0] is None and str(c_ok[2]) == MID and int(c_ok[1]) == 2,
            "G: check(): tiers must match; part.multitool off / part.toolRarity off refuse; OK = (None, 2, %s); belowBand block (tools never "
            "enforced) = %s" % (MID, c_blk[0]))
    # a tier whose multitool is missing (mod not loaded for that id): remove the Onyxium item from the map view through a fake id check
    pv_ok = Merge.preview(lp, ph, U1)
    pv_plain = Merge.preview(stack(PI), stack(HI), U1)
    pv_bad = Merge.preview(tool(PI, hand(PI, 5, [])), ph, U1)
    K.check(pv_ok[0] is None and str(pv_ok[1]) == MID and mods_of(pv_ok[2]) == lp_exp and not bool(pv_ok[3]) and int(pv_ok[4]) == L
            and pv_plain[0] is None and pv_plain[2] is None and bool(pv_plain[3]) and "special" in str(pv_bad[0]),
            "G: preview(): the merged document (no roll), both plain = 'rolls on merge', a refusal = its words")
    # FIX 2 (critics 2 + C2): the page is told what the merge loses BEFORE the click
    pv_rp = Merge.preview(tool(PI, rp_d), tool(HI, uh_d), U1)
    hiL = int(Lvl.clamp(JInt(L + 8)))
    pv_lv = Merge.preview(tool(PI, hand(PI, 2, [("mpow", 1)], lvl=hiL)), ph, U1)
    pv_cap = Merge.preview(tool(PI, hand(PI, 3, [("mpow", c_pk + 50)])), ph, U1)
    pv_clean = Merge.preview(tool(PI, hand(PI, 2, [("mpow", 1)])), ph, U1)
    K.check("2 lines do not fit and will be lost" in str(pv_rp[5]) and (hiL <= L or ("made at Lv %d (your tool is Lv %d)" % (L, hiL)) in str(pv_lv[5]))
            and "1 line is lowered to the multitool's limit" in str(pv_cap[5]) and str(pv_clean[5]) == "" and str(pv_plain[5]) == "" and str(pv_bad[5]) == "",
            "FIX 2: preview warnings: Rare + Unique '%s' | a Lv %d tool made at Lv %d '%s' | over the cap '%s' | nothing lost '' | plain '' | refused ''"
            % (pv_rp[5], hiL, L, pv_lv[5], pv_cap[5]))
    K.notes.append("FIX 2: '%s' | '%s' | '%s'" % (pv_rp[5], pv_lv[5], pv_cap[5]))

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

    def mkinv(fail_hot=False, fail_sto=False):
        inv_ = INV()
        cs_ = {"hotbar": MF(JShort(9)) if fail_hot else SIC(JShort(9)), "storage": MF(JShort(36)) if fail_sto else SIC(JShort(36)),
               "backpack": SIC(JShort(9)), "armor": SIC(JShort(4)), "utility": SIC(JShort(4)), "tools": SIC(JShort(4))}
        for f_, kind in (("hotbar", "Hotbar"), ("storage", "Storage"), ("backpack", "Backpack"), ("armor", "Armor"), ("utility", "Utility"), ("tools", "Tool")):
            jf(INV, f_).set(inv_, comp(kind, cs_[f_]))
        return inv_, cs_

    def at(cs_, sec, i):
        s_ = cs_[sec].getItemStack(JShort(i))
        return None if s_ is None or s_.isEmpty() else s_

    def counts(inv_):
        all_ = Stamp.allOf(inv_)
        return tuple(int(Stamp.countId(all_, x)) for x in (PI, HI, MID))

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
    Log.FILE = JClass("java.nio.file.Paths").get(os.path.join(SCRATCH, "gear.log"))
    logs()
    # T6 the merge: Legendary pickaxe hotbar 0 + plain hatchet storage 3 (+ a second plain hatchet in storage 4 and a plain pickaxe in
    # backpack 0 that must stay)
    inv, cs = mkinv()
    cs["hotbar"].setItemStackForSlot(JShort(0), lp)
    cs["storage"].setItemStackForSlot(JShort(3), ph)
    cs["storage"].setItemStackForSlot(JShort(4), stack(HI))
    cs["backpack"].setItemStackForSlot(JShort(0), stack(PI))
    rows = [tuple(x) for x in Merge.rows(inv)]
    K.check(sorted(rows) == sorted([(0, 0), (1, 3), (1, 4), (2, 0)]), "G: rows() = every pickaxe / hatchet of a multitool tier on you: %s" % rows)
    b0 = counts(inv)
    xp0 = XP[0]
    fpP, fpH = str(Forge.fp(lp)), str(Forge.fp(ph))
    r6 = Merge.merge(inv, JInt(0), JInt(0), PI, fpP, JInt(1), JInt(3), HI, fpH, U1, "Tester")
    on_disk = disk()
    in_q = [l_ for l_ in str(Log.take()).split("\n") if l_.strip()]
    K.check(any(" MERGE-BEGIN " in l_ for l_ in on_disk) and not any(" MERGE-BEGIN " in l_ for l_ in in_q) and any(" MERGE Tester " in l_ for l_ in in_q),
            "FIX 3 (critic 3): MERGE-BEGIN is ON DISK when merge() returns (flushed before the hatchet moved); only the MERGE line is still "
            "queued: disk %d line(s), queue %d" % (len(on_disk), len(in_q)))
    made = at(cs, "hotbar", 0)
    md = Data.effective(made.getItemId(), made.getMetadata()) if made is not None else None
    ll = on_disk + in_q
    K.check(int(r6[0]) == 1 and made is not None and str(made.getItemId()) == MID and md is not None and mods_of(md) == lp_exp
            and rid_of(md) == "legendary" and at(cs, "storage", 3) is None and at(cs, "storage", 4) is not None and at(cs, "backpack", 0) is not None
            and counts(inv) == (b0[0] - 1, b0[1] - 1, b0[2] + 1) and int(made.getQuantity()) == 1,
            "G: merge(): the multitool is in the pickaxe's slot (Legendary, the pickaxe's lines), ONLY the picked hatchet is gone (the other "
            "hatchet and the backpack pickaxe stay), counts %s -> %s" % (b0, counts(inv)))
    beg = [l_ for l_ in ll if " MERGE-BEGIN " in l_]
    K.check(len(beg) == 1 and str(Data.gearDoc(lp.getMetadata()).toJson()) in beg[0] and HI + " @Inventory 4 plain -> " in beg[0] and any(" MERGE Tester " in l_ and " legendary " in l_ for l_ in ll)
            and not [l_ for l_ in ll if "MERGE-COUNT" in l_ or "MERGE-FAILED" in l_],
            "G: gear.log: MERGE-BEGIN carries both input documents, then MERGE; no count / failure line: %s" % [l_[:400] for l_ in ll])
    r6b = Merge.merge(inv, JInt(0), JInt(0), PI, fpP, JInt(1), JInt(3), HI, fpH, U1, "Tester")
    K.check(int(r6b[0]) == 0 and "moved or changed" in str(r6b[1]) and counts(inv) == (b0[0] - 1, b0[1] - 1, b0[2] + 1) and XP[0] == xp0,
            "G: a second click with the old fingerprints is refused - inputs used exactly once, one multitool; no Smithing XP (skill:fn:addxp "
            "calls %d)" % (XP[0] - xp0))
    # contrast: the counter works (a bench craft of an Iron pickaxe pays)
    Roll.payCraft(U1, PI, " rare", "Tester")
    K.check(XP[0] == xp0 + 1, "G: (contrast) the XP counter sees a bench pickaxe craft pay: %d call(s)" % (XP[0] - xp0))
    # FIX 4 (critic 4): the post-swap bookkeeping throws -> the merge still reports made, items moved exactly once
    inv_a, cs_a = mkinv()
    cs_a["hotbar"].setItemStackForSlot(JShort(0), lp)
    cs_a["storage"].setItemStackForSlot(JShort(3), ph)
    b_a = counts(inv_a)
    Merge.AFTER_THROWS = True
    try:
        r_a = Merge.merge(inv_a, JInt(0), JInt(0), PI, fpP, JInt(1), JInt(3), HI, fpH, U1, "Tester")
    finally:
        Merge.AFTER_THROWS = False
    l_a = logs()
    K.check(int(r_a[0]) == 1 and r_a[2] is not None and counts(inv_a) == (b_a[0] - 1, b_a[1] - 1, b_a[2] + 1) and at(cs_a, "storage", 3) is None
            and not any(" MERGE Tester " in l_ for l_ in l_a) and any(" MERGE-BEGIN " in l_ for l_ in l_a),
            "FIX 4: after() throws -> merge() still returns made (1), counts %s -> %s, no MERGE line (the bookkeeping was skipped, nothing else)"
            % (b_a, counts(inv_a)))
    # T6b the same slot / a bad section
    inv2, cs2 = mkinv()
    cs2["hotbar"].setItemStackForSlot(JShort(1), lp)
    r_same = Merge.merge(inv2, JInt(0), JInt(1), PI, fpP, JInt(0), JInt(1), PI, fpP, U1, "Tester")
    r_sec = Merge.merge(inv2, JInt(9), JInt(1), PI, fpP, JInt(0), JInt(1), HI, fpH, U1, "Tester")
    r_ref = Merge.merge(inv2, JInt(0), JInt(1), PI, fpP, JInt(0), JInt(2), HI, fpH, U1, "Tester")
    cs2["hotbar"].setItemStackForSlot(JShort(2), tool(HI, hand(HI, 7, [])))
    fpU = str(Forge.fp(at(cs2, "hotbar", 2)))
    r_ut = Merge.merge(inv2, JInt(0), JInt(1), PI, fpP, JInt(0), JInt(2), HI, fpU, U1, "Tester")
    K.check(int(r_same[0]) == 0 and "two different slots" in str(r_same[1]) and int(r_sec[0]) == 0 and int(r_ref[0]) == 0
            and int(r_ut[0]) == 0 and "special" in str(r_ut[1]) and at(cs2, "hotbar", 1) is not None and at(cs2, "hotbar", 2) is not None,
            "G: refused before anything moves: the same slot, a bad section, an empty hatchet slot, an Untiered hatchet ('%s')" % str(r_ut[1])[:60])
    logs()
    # T7 failure at (b): the pickaxe's container refuses the multitool -> the hatchet goes back, nothing used
    inv3, cs3 = mkinv(fail_hot=True)
    cs3["hotbar"].setItemStackForSlot(JShort(0), lp)
    cs3["storage"].setItemStackForSlot(JShort(3), ph)
    cs3["hotbar"].refuseId = MID
    b3 = counts(inv3)
    r7 = Merge.merge(inv3, JInt(0), JInt(0), PI, fpP, JInt(1), JInt(3), HI, fpH, U1, "Tester")
    l7 = logs()
    K.check(int(r7[0]) == -1 and "nothing was used" in str(r7[1]) and counts(inv3) == b3 and str(Forge.fp(at(cs3, "hotbar", 0))) == fpP
            and str(Forge.fp(at(cs3, "storage", 3))) == fpH and any("MERGE-FAILED" in l_ and "RESTORED" in l_ for l_ in l7),
            "G: failure at (b) (the multitool cannot be written): the hatchet is put back in its slot, the pickaxe stays, counts %s; "
            "MERGE-FAILED ... RESTORED" % (counts(inv3),))
    # T8 failure at (a): the hatchet cannot be removed (throws, slot unchanged)
    inv4, cs4 = mkinv(fail_sto=True)
    cs4["hotbar"].setItemStackForSlot(JShort(0), lp)
    cs4["storage"].setItemStackForSlot(JShort(3), ph)
    cs4["storage"].rm = 1
    b4 = counts(inv4)
    r8 = Merge.merge(inv4, JInt(0), JInt(0), PI, fpP, JInt(1), JInt(3), HI, fpH, U1, "Tester")
    l8 = logs()
    # T9 failure at (a), the other way: removed, then the call failed -> the hatchet is put back
    cs4["storage"].rm = 2
    r9 = Merge.merge(inv4, JInt(0), JInt(0), PI, fpP, JInt(1), JInt(3), HI, fpH, U1, "Tester")
    l9 = logs()
    K.check(int(r8[0]) == -1 and counts(inv4) == b4 and any("hatchet not taken" in l_ for l_ in l8)
            and int(r9[0]) == -1 and counts(inv4) == b4 and str(Forge.fp(at(cs4, "storage", 3))) == fpH and any("hatchet not taken" in l_ for l_ in l9),
            "G: failure at (a): a remove that throws leaves everything; a remove that empties the slot and then throws gets the hatchet put "
            "back - counts %s both times" % (counts(inv4),))
    # T10 the restore fails too: pickaxe + hatchet in one container that refuses the multitool and then everything -> the hatchet is LOST
    # (logged with its document), never a copy
    inv5, cs5 = mkinv(fail_sto=True)
    cs5["storage"].setItemStackForSlot(JShort(0), lp)
    cs5["storage"].setItemStackForSlot(JShort(3), ph)
    cs5["storage"].refuseId = MID
    cs5["storage"].sticky = True
    r10 = Merge.merge(inv5, JInt(1), JInt(0), PI, fpP, JInt(1), JInt(3), HI, fpH, U1, "Tester")
    l10 = logs()
    K.check(int(r10[0]) == -1 and "admin can find" in str(r10[1]) and counts(inv5) == (1, 0, 0)
            and any(" MERGE-RESTORE-FAILED " in l_ and HI in l_ and "{" in l_ for l_ in l10) and any(" MERGE-BEGIN " in l_ for l_ in l10),
            "G: the worst case (restore refused too): the hatchet is lost but logged twice with its document (MERGE-BEGIN, MERGE-RESTORE-FAILED), "
            "no multitool appears - never a copy: counts %s" % (counts(inv5),))
    # T10b failure at (a) AND its restore: removed, then the call failed, and the slot refuses the hatchet back -> lost but logged, no copy
    inv5b, cs5b = mkinv(fail_sto=True)
    cs5b["hotbar"].setItemStackForSlot(JShort(0), lp)
    cs5b["storage"].setItemStackForSlot(JShort(3), ph)
    cs5b["storage"].rm = 2
    cs5b["storage"].refuseId = HI
    r10b = Merge.merge(inv5b, JInt(0), JInt(0), PI, fpP, JInt(1), JInt(3), HI, fpH, U1, "Tester")
    l10b = logs()
    K.check(int(r10b[0]) == -1 and "could not be put back" in str(r10b[1]) and counts(inv5b) == (1, 0, 0)
            and any(" MERGE-RESTORE-FAILED " in l_ and HI in l_ for l_ in l10b) and any(" MERGE-BEGIN " in l_ for l_ in l10b),
            "G: failure at (a) with the restore refused: the hatchet is lost but logged (MERGE-BEGIN + MERGE-RESTORE-FAILED), the pickaxe "
            "stays, no multitool: counts %s" % (counts(inv5b),))
    # gear.mythicItems: a listed tool id is special too
    apply(gear__mythicItems=PI)
    w_my = Merge.why(stack(PI), JInt(1))
    apply()
    K.check(w_my is not None and "special tool" in str(w_my), "G: a gear.mythicItems id is a special tool: %s" % w_my)
    K.check(XP[0] == xp0 + 1, "G: no merge path paid Smithing XP")
    # json / empty
    K.check(str(Merge.json(None)) == "none" and str(Merge.json(ph)) == "plain" and str(Merge.json(lp)).startswith("{")
            and bool(Merge.empty(cs5["storage"], JInt(3))), "G: json() / empty()")

    # ============================================================================ P: MultiPage + MultiCmd
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
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    try:
        FPR = JClass(FAKE_PKG + ".FakePR")
        prx = us.allocateInstance(FPR.class_)
    except Exception:
        FPR = None
        prx = us.allocateInstance(PR.class_)
    jf(PR, "uuid").set(prx, U1)
    jf(PR, "username").set(prx, "Tester")
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
        return uitext(ub_)
    inv6, cs6 = mkinv()
    rp6 = tool(PI, rp_d)
    uh6 = tool(HI, uh_d)
    cs6["hotbar"].setItemStackForSlot(JShort(0), rp6)
    cs6["storage"].setItemStackForSlot(JShort(2), uh6)
    cs6["storage"].setItemStackForSlot(JShort(5), tool(PI, hand(PI, 5, [("mpow", 9)])))
    cs6["backpack"].setItemStackForSlot(JShort(1), stack("Tool_Hatchet_Copper"))
    ref6, st6 = world(inv6)
    pg = FMP(prx)
    pg.preselect(inv6)
    t_pre = (int(pg.pSec), int(pg.pSlot), str(pg.info))
    s0 = render(pg, ref6, st6)
    K.check(t_pre[:2] == (0, 0) and "is the pickaxe" in t_pre[2] and "Pickaxes + hatchets (4)" in s0 and "Hatchet: none picked" in s0
            and "Cannot merge" in s0 and "Pick a hatchet" in s0 and "SkyyGRow3" in s0 and "Multitool" in s0,
            "P: /multitool opens with the held pickaxe picked (preselect); the list shows the 4 tools; no hatchet = 'Cannot merge'")
    rws = [tuple(x) for x in pg.rows]
    ih = rws.index((1, 2))
    pg.handleDataEvent(ref6, st6, '{"a":"sel:%d"}' % ih)
    s1 = render(pg, ref6, st6)
    K.check(int(pg.hSec) == 1 and int(pg.hSlot) == 2 and "It will have" in s1 and "Make multitool" in s1 and "RARE MULTITOOL" in s1
            and "(picked)" in s1 and "Warning: 2 lines do not fit and will be lost" in s1,
            "P: sel the Unique hatchet -> the preview (RARE MULTITOOL, 'It will have' + the lines), 'Make multitool' on, and the gold "
            "'Warning: 2 lines do not fit and will be lost' line (FIX 2)")
    # a Mythic pickaxe picked -> refused words
    im = rws.index((1, 5))
    pg.handleDataEvent(ref6, st6, '{"a":"sel:%d"}' % im)
    s2 = render(pg, ref6, st6)
    K.check("special tool" in s2 and "Cannot merge" in s2 and int(pg.pSlot) == 5, "P: a Mythic pickaxe picked -> 'special tool ... never merged', 'Cannot merge'")
    # put back (sel the same row again) + a tier mismatch
    pg.handleDataEvent(ref6, st6, '{"a":"sel:%d"}' % im)
    put_back = int(pg.pSec) == -1 and "put back" in str(pg.info)
    ic = rws.index((2, 1))
    pg.handleDataEvent(ref6, st6, '{"a":"sel:%d"}' % rws.index((0, 0)))
    pg.handleDataEvent(ref6, st6, '{"a":"sel:%d"}' % ic)
    s3 = render(pg, ref6, st6)
    K.check(put_back and "same tier" in s3, "P: clicking the picked tool puts it back; a Copper hatchet with an Iron pickaxe -> 'same tier'")
    pg.handleDataEvent(ref6, st6, '{"a":"sel:%d"}' % ih)
    # guards: profile:busy, missing pick, double click, epoch
    br.put("profile:busy:" + str(U1), True)
    pg.lastClick = JLong(0)
    pg.handleDataEvent(ref6, st6, '{"a":"merge"}')
    g_busy = "still loading" in str(pg.info)
    br.remove("profile:busy:" + str(U1))
    pg.lastClick = JLong(JClass("java.lang.System").currentTimeMillis())
    inf0 = str(pg.info)
    pg.doMerge(inv6)
    g_dbl = str(pg.info) == inf0
    K.check(g_busy and g_dbl and at(cs6, "hotbar", 0) is not None and str(at(cs6, "hotbar", 0).getItemId()) == PI,
            "P: guards: profile:busy refuses, a double click inside 400 ms does nothing")
    # the merge click
    b6 = counts(inv6)
    pg.lastClick = JLong(0)
    rb0 = int(pg.rebuilds)
    pg.handleDataEvent(ref6, st6, '{"a":"merge"}')
    s4 = render(pg, ref6, st6)
    m6 = at(cs6, "hotbar", 0)
    K.check(str(pg.info).startswith("+Made a Rare ") and m6 is not None and str(m6.getItemId()) == MID and at(cs6, "storage", 2) is None
            and counts(inv6) == (b6[0] - 1, b6[1] - 1, b6[2] + 1) and "Made: " in s4 and "Its lines" in s4 and int(pg.pSec) == -1 and int(pg.hSec) == -1
            and int(pg.rebuilds) == rb0 + 1 and XP[0] == xp0 + 1 and "Merged" in s4 and "Cannot merge" not in s4,
            "P: 'Make multitool' -> '%s'; the multitool in hotbar 1, the hatchet gone, the page shows Made + its lines, picks cleared, no XP; the button reads 'Merged' (FIX C3), never 'Cannot merge'" % str(pg.info)[:60])
    # epoch change + refresh / prev / next / back / bad
    pg.handleDataEvent(ref6, st6, '{"a":"refresh"}')
    pg.handleDataEvent(ref6, st6, '{"a":"sel:%d"}' % 0)
    pg.epoch = "old-epoch"
    pg.pSec, pg.hSec = JInt(0), JInt(1)
    pg.lastClick = JLong(0)
    pg.doMerge(inv6)
    g_ep = "profile changed" in str(pg.info) and int(pg.pSec) == -1
    pg.lastClick = JLong(0)
    pg.doMerge(inv6)
    g_miss = "Pick a pickaxe and a hatchet first" in str(pg.info)
    pg.handleDataEvent(ref6, st6, '{"a":"prev"}')
    pg.handleDataEvent(ref6, st6, '{"a":"next"}')
    pg.handleDataEvent(ref6, st6, '{"a":"sel:99"}')
    pg.handleDataEvent(ref6, st6, '{"a":""}')
    pg.handleDataEvent(ref6, st6, None)
    cl0 = int(pg.closes)
    pg.handleDataEvent(ref6, st6, '{"a":"back"}')
    K.check(g_ep and g_miss and int(pg.closes) == cl0 + 1, "P: a profile change clears the picks; merge without picks refused; back closes (no SkyyMenu)")
    # a pick of something that is not a pickaxe / hatchet, and a moved tool
    pg2 = FMP(prx)
    K.check(not bool(pg2.pick(inv6, JInt(3), JInt(0))) and not bool(pg2.pick(inv6, JInt(1), JInt(30))), "P: pick() of an empty / non-tool slot = false")
    pg2.pick(inv6, JInt(1), JInt(5))
    cs6["storage"].setItemStackForSlot(JShort(5), stack(PI))
    s5 = render(pg2, ref6, st6)
    K.check("moved or changed" in str(pg2.info) and int(pg2.pSec) == -1, "P: a picked tool that changed is dropped at the next build")
    # both plain -> 'rolls a rarity'; the unpaged list (frames off) + the empty list
    inv7, cs7 = mkinv()
    cs7["hotbar"].setItemStackForSlot(JShort(0), stack(PI))
    cs7["hotbar"].setItemStackForSlot(JShort(1), stack(HI))
    for i_ in range(14):
        cs7["storage"].setItemStackForSlot(JShort(i_), stack(PI))
    ref7, st7 = world(inv7)
    pg3 = FMP(prx)
    pg3.pick(inv7, JInt(0), JInt(0))
    pg3.pick(inv7, JInt(0), JInt(1))
    apply(**{"ui__frames": "false"})
    s6 = render(pg3, ref7, st7)
    apply()
    K.check("Both tools are plain: it rolls a rarity" in s6 and "Page 1 / 2" in s6 and "SkyyGBtnNext" in s6,
            "P: two plain tools -> 'rolls a rarity like a crafted multitool'; without frames the list pages (12 a page)")
    inv8, cs8 = mkinv()
    ref8, st8 = world(inv8)
    s7 = render(FMP(prx), ref8, st8)
    K.check("No pickaxes or hatchets on you" in s7, "P: the empty list")
    # /multitool
    MC = P("MultiCmd")
    cmd = MC()
    pg_groups = None
    k_ = cmd.getClass()
    while k_ is not None and pg_groups is None:
        for f_ in k_.getDeclaredFields():
            if "ermissionGroups" in str(f_.getName()):
                f_.setAccessible(True)
                pg_groups = f_.get(cmd)
        k_ = k_.getSuperclass()
    K.check(str(cmd.getName()) == "multitool" and pg_groups is not None and "hytale:Adventurer" in [str(x) for x in pg_groups],
            "P: /multitool: name 'multitool', permission group hytale:Adventurer (COMMAND RULES): %s" % (list(pg_groups) if pg_groups is not None else None))
    exe = [m_ for m_ in MC.class_.getDeclaredMethods() if str(m_.getName()) == "execute"][0]
    exe.setAccessible(True)
    said = []
    if FPR is not None:
        apply(part__multitool="false")
        exe.invoke(cmd, None, st6, ref6, prx, None)
        apply()
        exe.invoke(cmd, None, st6, ref6, prx, None)
        said = [str(x) for x in (prx.said or [])]
    K.check(FPR is None or (len(said) >= 2 and "switched off" in said[0] and "could not open" in said[-1]),
            "P: /multitool executed: off -> 'switched off'; on -> stamp scan, page made + preselected, open (the stand-in player has no page "
            "manager -> the 'could not open' line): %s" % said)
    if FPR is None:
        K.notes.append("PlayerRef is final - /multitool execute() was not run (UNVERIFIED: in game)")
    # a tier whose multitool item is gone, then none at all (the Multitools mod not loaded): check() / loaded() / /multitool
    ITEM.getAssetStore().removeAssets(JClass("java.util.Arrays").asList([MULTI_PRE + "Onyxium"]))
    c_none = Merge.check(stack("Tool_Pickaxe_Onyxium"), stack("Tool_Hatchet_Onyxium"), U1)
    K.check(ITEM.getAssetMap().getAsset(MULTI_PRE + "Onyxium") is None and "no Onyxium multitool" in str(c_none[0]) and bool(Merge.loaded()),
            "G: a tier without its multitool item: '%s'; loaded() still true (7 left)" % c_none[0])
    # no multitool item at all (the Multitools mod not loaded): the tier words point at ids no pack has (GearMulti.TW is read live)
    tw0 = [str(x) for x in GM.TW]
    for i_ in range(len(tw0)):
        GM.TW[i_] = "NotLoaded%d" % i_
    said0 = len(prx.said or []) if FPR is not None else 0
    if FPR is not None:
        exe.invoke(cmd, None, st6, ref6, prx, None)
    nl = bool(Merge.loaded())
    for i_ in range(len(tw0)):
        GM.TW[i_] = tw0[i_]
    K.check(not nl and (FPR is None or "not loaded" in str(list(prx.said)[said0])),
            "G/P: no multitool item at all -> loaded() false, /multitool says the Multitools mod is not loaded")
    K.save(res1=res1, L=L)


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
        print("   %-16s %s" % (k, ", ".join(diffs[k])[:1200]))
    K.check(set(add) == NEW_CLASSES and not gone, "C: added exactly GearMerge / MultiPage / MultiCmd, none removed: + %s - %s" % (add, gone))
    want = {"GearMulti": {"~m replaceAll"}, "SkyyGearPlugin": {"~m setup"}}
    bad = {}
    for k in set(want) | set(diffs):
        got = set(diffs.get(k, []))
        if got != want.get(k, set()):
            bad[k] = (sorted(want.get(k, set()) - got), sorted(got - want.get(k, set())))
    K.check(not bad, "C: changed exactly GearMulti.replaceAll (start line) and SkyyGearPlugin.setup (command + ready line) (missing / extra): %s" % bad)
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
    for flag, fn in (("--mkfake", lambda: run_mkfake2(arg("--mkfake"))), ("--verify", lambda: H["run_verify"](arg("--out"))),
                     ("--merge", lambda: run_merge(arg("--out"))),
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
        print("note: no Multitools jar - the merge checks cannot run")
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.environ["TEMP"] = os.environ["TMP"] = env["TEMP"]
    try:
        run_assets()
        p = child(env, "--mkfake", FAKE_DIR)
        check(p.returncode == 0, "F: the stand-ins were generated")
        for label, flag in (("verify", "--verify"), ("compare", "--compare"), ("merge", "--merge")):
            out = os.path.join(SCRATCH, "%s.json" % label)
            pr = child(env, flag, "--out", out)
            check(pr.returncode == 0, "%s: the child exited cleanly (%s)" % (label, pr.returncode))
            r = take(out, label)
            if label == "merge" and r:
                print("E/G. Iron multitool craft level %s; start line: ...%s" % (r.get("L"), str(r.get("res1"))[-90:]))
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
            check(res["old"]["cfg"] == res["new"]["cfg"], "D: 0.2.21 starts the live copy to exactly the config.properties 0.2.20 writes (no config change)")
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
