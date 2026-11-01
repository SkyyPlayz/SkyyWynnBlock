"""Harness for SkyyArmory 0.1.51 (lean round crescent: Crescent Rush + the sword guard stay Spellblade-only; tools/armory_0_1_51_patch.py).
Build first:
    python tools/armory_0_1_51_patch.py && python SkyyArmory/build_skyyarmory_0.1.51.py
    python SkyyArmory/test_skyyarmory_0.1.51.py [--keep]
Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  S   static   the patch re-runs to identical bytes, line endings kept; no new class / system / command; the jar vs 0.1.50: added = the 2
               interaction files (SkyyArmory_Longsword_Rush_Release = the 0.1.50 Longsword_Stab_Charged byte for byte as JSON,
               SkyyArmory_Longsword_Stab_Charged_Vanilla = the Assets.zip charged stab); changed non-class = manifest + Longsword_Stab_Charged
               (now the Replace) + the Katana item (+ exactly the one InteractionVars entry); lang unchanged; no other longsword item touched
  X   exec     EXECUTED in the JVM: the REAL engine codecs (Interaction / RootInteraction / Item stores, the 76 interaction types read from
               InteractionModule.setup) decode the jar's Longsword_Stab_Charged = ReplaceInteraction (variable SkyyArmory_Rush_Release,
               defaultOk true, a default root), the release + vanilla copies, and the jar's Katana file (its var = a generated root); then
               Rush.optOut / Rush.guardItem on those decoded Items (Katana: opted out, no guard; the same file without the var: guarded),
               Rush.sword through the loaded Item store (Katana false, a plain longsword true, unknown false), Rush.guardAll over the loaded
               store (the "left vanilla for their class" count), Rush.onLoaded skip, optOut(null) / a hand-built Item / a broken map
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.50 -> 0.1.51: exactly the planned members (EXPECT)
  D   live     START TWICE on a scratch COPY of the live Skyy_SkyyArmory: 0.1.51 writes nothing; start 2 = start 1
  AA  audit    the engine-access audit
Not executed here (UNVERIFIED until the game): the client playing the Katana's vanilla charged stab through the Replace (the server side is the
engine's own ReplaceInteraction.doReplace reading the held item's InteractionVars - read from its bytecode, not run with a live player).
"""
import os, sys, json, subprocess, zipfile, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "crescent", "arm")]
import skyybuild as B
import harness_kit as HK

VERSION, OLD = "0.1.51", "0.1.50"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyarmory_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyarmory_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "armory_0_1_51_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.armory."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyArmory")
AZP = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")          # read-only
VAR, REL, VAN = "SkyyArmory_Rush_Release", "SkyyArmory_Longsword_Rush_Release", "SkyyArmory_Longsword_Stab_Charged_Vanilla"
P_VIA = "Server/Item/Interactions/Weapons/Longsword/Attacks/Stab_Charged/Longsword_Stab_Charged.json"
P_KAT = "Server/Item/Items/Weapon/Longsword/Weapon_Longsword_Katana.json"
P_REL = "Server/Item/Interactions/Weapons/Longsword/SkyyArmory/%s.json" % REL
P_VAN = "Server/Item/Interactions/Weapons/Longsword/SkyyArmory/%s.json" % VAN
EXPECT = {
    "Rush": ["+f OPT_VAR", "+m optOut", "~m sword", "~m guardItem", "~m guardAll"],
    "CfgRows2": ["~<clinit>"],          # the read-only row fixed.blade.items names the Katana
    # the version text only (0.1.50 -> 0.1.51), as every Armory round
    "SkyyArmoryPlugin": ["~m setup", "~m start"], "ArmoryCfg": ["~m load", "~m reloadAll", "~m useDefaults"], "ArmoryCheck": ["~m packCheck", "~m packOf"],
    "ArmoryDefs": ["~<clinit>"], "ArmoryHooks": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
MIGS = ("migrate012", "migrate013", "migrate014", "migrate016", "migrate017", "migrate018", "migrate021", "migrate035", "migrate036", "migrate040",
        "migrateP5")

_ORIG_COMPARE = HK.run_compare


def compare_with_assets(out, jar, old_jar, pkg, expect, added, removed=()):
    _ORIG_COMPARE(out, jar, old_jar, pkg, expect, added, removed)
    d = json.load(open(out))
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    ea = set(n for n in za.namelist() if not n.endswith(".class"))
    eb = set(n for n in zb.namelist() if not n.endswith(".class"))
    ed = sorted(n for n in ea | eb if n not in ea or n not in eb or za.read(n) != zb.read(n))
    kept = [f for f in d["fails"] if not f.startswith("C: non-class entries changed")]
    if ed == sorted(["manifest.json", P_VIA, P_KAT, P_REL, P_VAN]):
        d["ok"] += 1
    else:
        kept.append("C: non-class entries changed = manifest + the charged release + the Katana + 2 new interactions: got %s" % ed[:10])
    d["fails"] = kept
    d["notes"].append("C: non-class entries changed = manifest + Longsword_Stab_Charged + Katana + 2 new interactions (the kit's manifest-only check replaced)")
    json.dump(d, open(out, "w"), indent=1)


HK.run_compare = compare_with_assets


# ---------------------------------------------------------------------------------------------------------------- S: static
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyArmory 0.1.51 - build script') and g.count('VERSION = "0.1.51"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("), g.count("makeClass(") - o.count("makeClass(")),
         (0, 0, 0), "S no new system / command / class")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb, vz = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar), zipfile.ZipFile(AZP)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), (sorted([P_REL, P_VAN]), []), "S added = the 2 interaction files; nothing removed")
    nc = sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n))
    K.eq(nc, sorted(["manifest.json", P_VIA, P_KAT]), "S changed non-class = manifest + the charged release + the Katana (every other file byte-identical, lang too)")
    ma, mb = json.loads(za.read("manifest.json")), json.loads(zb.read("manifest.json"))
    K.check(mb["Version"] == VERSION and dict(ma, Version=VERSION, Name=ma["Name"].replace(OLD, VERSION)) == mb, "S manifest: only the Version changed")
    via_old, via = json.loads(za.read(P_VIA).decode("utf-8")), json.loads(zb.read(P_VIA).decode("utf-8"))
    K.eq(via, {"Type": "Replace", "Var": VAR, "DefaultOk": True, "DefaultValue": {"Interactions": [REL]}},
         "S Longsword_Stab_Charged = a Replace on the item var (default = the release; DefaultOk = no log line for the other longswords)")
    K.eq(json.loads(zb.read(P_REL).decode("utf-8")), via_old, "S the release = the 0.1.50 Longsword_Stab_Charged, every field (marker + the hidden vanilla stab)")
    K.eq(json.loads(zb.read(P_VAN).decode("utf-8")), json.loads(vz.read(P_VIA).decode("utf-8-sig")), "S the vanilla copy = the Assets.zip charged stab, every field")
    ko, kn = json.loads(za.read(P_KAT).decode("utf-8")), json.loads(zb.read(P_KAT).decode("utf-8"))
    kv = dict(kn["InteractionVars"])
    kv.pop(VAR)
    K.eq((dict(kn, InteractionVars=kv), kn["InteractionVars"][VAR]), (ko, {"Interactions": [VAN]}),
         "S the Katana = its 0.1.50 file + exactly InteractionVars %s -> %s (Primary, Meridian Cut, meter kept)" % (VAR, VAN))
    K.check("Secondary" not in kn["Interactions"] and kn["Interactions"]["Primary"] == "Longsword_Attack", "S the Katana file has no right click (vanilla) and the vanilla attack root")
    others = [n for n in nb if n.startswith("Server/Item/Items/") and n != P_KAT and VAR.encode() in zb.read(n)]
    K.eq(others, [], "S no other item carries the var (every other longsword keeps Crescent Rush + the guard)")
    K.check(not [n for n in vz.namelist() if n.startswith("Server/") and n.endswith(".json") and VAR.encode() in vz.read(n)], "S the var name is ours (not in Assets.zip)")
    gear = os.path.join(ROOT, "SkyyGear", "SkyyGear-0.3.54.jar")
    if os.path.isfile(gear):
        with zipfile.ZipFile(gear) as gz:
            gn = gz.namelist()
            K.check(not [n for n in gn if os.path.basename(n) in ("Longsword_Stab_Charged.json", "Weapon_Longsword_Katana.json", REL + ".json", VAN + ".json")],
                    "S SkyyGear 0.3.54 ships none of the 4 files (one writer)")
            ch = [json.loads(gz.read(n).decode("utf-8-sig")) for n in gn if n.endswith("_Longsword_Longsword_Attack.json")]
            K.check(len(ch) >= 10 and all(c_["Next"]["1.565"] == "Longsword_Stab_Charged" for c_ in ch),
                    "S SkyyGear's %d longsword speed chains still charge into Longsword_Stab_Charged (-> the Replace, so a Katana with a speed roll stays vanilla too)" % len(ch))
    K.save()


# ---------------------------------------------------------------------------------------------------------------- X: executed
def run_exec(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JString, JArray, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    JClass(PKG + "ArmoryLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyArmory")
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    # ---- the engine stores (the 0.1.1 harness's minimal setup: Options, a bare HytaleServer with an EventBus, the asset registry)
    JClass("com.hypixel.hytale.server.core.Options").parse(JArray(JString)(["--universe", os.path.join(scratch, "universe")]))
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)
    HS = JClass("com.hypixel.hytale.server.core.HytaleServer")
    hs = U.allocateInstance(HS.class_)

    def setf(obj, cls, name, v):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, v)
    setf(hs, HS, "eventBus", JClass("com.hypixel.hytale.event.EventBus")(False))
    setf(None, HS, "instance", hs)
    CHM = JClass("java.util.concurrent.ConcurrentHashMap")
    UNI = JClass("com.hypixel.hytale.server.core.universe.Universe")
    uni = U.allocateInstance(UNI.class_)
    pbu, wmap = CHM(), CHM()
    setf(uni, UNI, "playersByUuid", pbu)
    setf(uni, UNI, "players", JClass("java.util.Collections").unmodifiableCollection(pbu.values()))
    setf(uni, UNI, "worlds", wmap)
    setf(uni, UNI, "worldsByUuid", CHM())
    setf(uni, UNI, "unmodifiableWorlds", JClass("java.util.Collections").unmodifiableMap(wmap))
    setf(None, UNI, "instance", uni)
    AR = JClass("com.hypixel.hytale.assetstore.AssetRegistry")
    JClass("com.hypixel.hytale.server.core.asset.AssetRegistryLoader").init()
    HAS = JClass("com.hypixel.hytale.server.core.asset.HytaleAssetStore")
    ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
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
    INTc, ROOTc, ITMc = JClass(PI + "Interaction"), JClass(PI + "RootInteraction"), JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    UIc = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.UnarmedInteractions")
    for c_, path_, unk_ in ((INTc, "Item/Interactions", True), (ROOTc, "Item/RootInteractions", False)):
        b_ = HAS.builder(c_.class_, ILT(ArrOf(c_))).setPath(path_).setCodec(c_.CODEC).setKeyFunction(GetId()).setReplaceOnRemove(NoRep())
        if unk_:
            b_ = b_.setIsUnknown(IsUnknown())
        AR.register(b_.build())
    AR.register(HAS.builder(UIc.class_, JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")()).setPath("Item/Unarmed/Interactions")
                .setCodec(UIc.CODEC).setKeyFunction(GetId()).build())
    CP = JClass("javassist.ClassPool")(True)
    CP.appendClassPath(B.SERVER_JAR)
    CPool = JClass("javassist.bytecode.ConstPool")
    ms_ = [x for x in CP.get("com.hypixel.hytale.server.core.modules.interaction.InteractionModule").getDeclaredMethods() if str(x.getName()) == "setup"][0]
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
        f_ = C_.class_.getDeclaredField("CODEC")
        f_.setAccessible(True)
        INTc.CODEC.register(nm_, C_.class_, f_.get(None))
    K.check(len(regs) >= 70 and ("Replace", PI + "none.ReplaceInteraction") in regs, "X the interaction type codecs from InteractionModule.setup (%d, Replace among them)" % len(regs))
    AEI = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo")
    ADT = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo$Data")
    RJR = JClass("com.hypixel.hytale.codec.util.RawJsonReader")
    Paths = JClass("java.nio.file.Paths")
    ArrayList = JClass("java.util.ArrayList")

    def dec(c, key, text):
        ei = AEI(Paths.get(key + ".json"), ADT(c.class_, key, None))
        try:
            o = AR.getAssetStore(c.class_).getCodec().decodeJsonAsset(RJR.fromJsonString(text), ei)
        except Exception as e:
            return None, "exception " + str(e)[:300]
        prob = []
        vr = ei.getValidationResults()
        if vr is not None and vr.hasFailed():
            prob.append("validation failed")
        uk = [str(x) for x in ei.getUnknownKeys()]
        if uk:
            prob.append("unknown keys %s" % uk)
        return o, "; ".join(prob)

    def fget(o, name):
        f = o.getClass().getDeclaredField(name)
        f.setAccessible(True)
        return f.get(o)
    z = zipfile.ZipFile(jar)
    # ---- the three interactions through the engine codec
    rv, why = dec(INTc, "Longsword_Stab_Charged", z.read(P_VIA).decode("utf-8"))
    K.check(rv is not None and not why and rv.getClass().getName() == PI + "none.ReplaceInteraction", "X Longsword_Stab_Charged decodes as the engine's ReplaceInteraction (%s)" % why)
    if rv is not None:
        K.eq((str(fget(rv, "variable")), bool(fget(rv, "defaultOk")), fget(rv, "defaultValue") is not None), (VAR, True, True),
             "X the Replace: variable %s, defaultOk true (no SEVERE line for longswords without it), a default root" % VAR)
        K.notes.append("X default root id: %s" % fget(rv, "defaultValue"))
    for key_, p_ in ((REL, P_REL), (VAN, P_VAN)):
        o_, w_ = dec(INTc, key_, z.read(p_).decode("utf-8"))
        K.check(o_ is not None and not w_ and o_.getClass().getSimpleName() == "SimpleInteraction", "X %s decodes (Simple, no unknown key): %s" % (key_, w_))
    # ---- the Katana item through the engine codec (Weapon / looks dropped: their stat-type store is not loaded here - not this round's change)
    kj = json.loads(z.read(P_KAT).decode("utf-8"))
    kj.pop("Weapon")
    kj.pop("ItemAppearanceConditions", None)
    kat, kw = dec(ITMc, "Weapon_Longsword_Katana", json.dumps(kj))
    K.check(kat is not None and not kw, "X the jar's Katana file decodes through the engine Item codec: %s" % kw)
    pj = json.loads(json.dumps(kj))
    pj["InteractionVars"].pop(VAR)
    plain, pw = dec(ITMc, "Weapon_Longsword_HarnessPlain", json.dumps(pj))
    K.check(plain is not None and not pw, "X the same file without the var decodes (a stand-in for every other longsword): %s" % pw)
    R = JClass(PKG + "Rush")
    Cfg = JClass(PKG + "ArmoryCfg")
    Cfg.useDefaults()
    IT = JClass("com.hypixel.hytale.protocol.InteractionType")
    if kat is not None and plain is not None:
        kv = kat.getInteractionVars()
        K.check(kv is not None and kv.get(VAR) is not None and str(kv.get(VAR)).startswith("*"), "X the Katana's var = a generated root: %s" % (kv and kv.get(VAR)))
        K.eq((bool(R.optOut(kat)), bool(R.optOut(plain)), bool(R.optOut(None))), (True, False, False), "X Rush.optOut: Katana yes, a plain longsword no, null no")
        g0 = int(R.GUARDS)
        gk = bool(R.guardItem(kat))
        gp = bool(R.guardItem(plain))
        K.eq((gk, kat.getInteractions().get(IT.Secondary), gp, str(plain.getInteractions().get(IT.Secondary)), int(R.GUARDS) - g0),
             (False, None, True, "SkyyArmory_Longsword_Guard", 1), "X Rush.guardItem: the decoded Katana keeps NO right click; the plain longsword gets the guard")
        K.eq(str(kat.getInteractions().get(IT.Primary)), "Longsword_Attack", "X the Katana keeps the vanilla attack root (SkyyGear's speed chains, the vanilla swings)")
        # ---- through the loaded Item store: sword() + guardAll()
        # the store copies carry only our var (the vanilla swing vars need the vanilla parent interactions, not loaded in this bare store)
        kj2 = dict(kj, InteractionVars={VAR: kj["InteractionVars"][VAR]})
        pj2 = dict(pj, InteractionVars={})
        plain2, _w2 = dec(ITMc, "Weapon_Longsword_HarnessPlain2", json.dumps(pj2))
        kat2, _w3 = dec(ITMc, "Weapon_Longsword_Katana", json.dumps(kj2))

        lst = ArrayList()
        for x_ in (kat2, plain2):
            if x_ is not None:
                lst.add(x_)
        loaded = None
        try:
            r_ = AR.getAssetStore(ITMc.class_).loadAssets("Hytale:Hytale", lst)
            loaded = not r_.hasFailed()
        except Exception as e:
            K.notes.append("X Item store load: %s" % str(e)[:200])
        if loaded and ITMc.getAssetMap().getAsset("Weapon_Longsword_Katana") is not None:
            R.SWORD.clear()
            K.eq((bool(R.sword("Weapon_Longsword_Katana")), bool(R.sword("Weapon_Longsword_HarnessPlain2")), bool(R.sword("Weapon_Nope")), bool(R.sword(None))),
                 (False, True, False, False), "X Rush.sword through the loaded store: Katana false (no rush, no Spellblade bonus), a plain longsword true")
            ga = str(R.guardAll())
            K.check("1 left vanilla for their class (the Warrior's Katana)" in ga and ga.startswith("1 two-handed swords got the right-click guard"),
                    "X Rush.guardAll over the loaded store: the plain one guarded, the Katana left vanilla: %s" % ga)
            K.check(ITMc.getAssetMap().getAsset("Weapon_Longsword_Katana").getInteractions().get(IT.Secondary) is None, "X after guardAll the stored Katana has no right click")
            K.check(str(R.statusText()).find("left vanilla for their class") >= 0, "X /armory status carries the guard line")
        else:
            K.check(False, "X the decoded items could not be loaded into the Item store (loaded=%s)" % loaded)
    # ---- a hand-built Item (the 0.1.28 X7 way) + a broken var map
    ITM = ITMc
    fi = ITM.class_.getDeclaredField("interactions")
    fi.setAccessible(True)
    fv = ITM.class_.getDeclaredField("interactionVars")
    fv.setAccessible(True)
    EM, HM = JClass("java.util.EnumMap"), JClass("java.util.HashMap")
    m = EM(IT.class_)
    m.put(IT.Primary, JString("Longsword_Attack"))
    hb = ITM(JString("Weapon_Longsword_HarnessHand"))
    fi.set(hb, EM(m))
    vm = HM()
    vm.put(JString(VAR), JString("*x"))
    fv.set(hb, vm)
    hb2 = ITM(JString("Weapon_Longsword_HarnessHand2"))
    fi.set(hb2, EM(m))
    fv.set(hb2, None)
    K.eq((bool(R.optOut(hb)), bool(R.guardItem(hb)), bool(R.optOut(hb2)), bool(R.guardItem(hb2))), (True, False, False, True),
         "X hand-built Items: the var = no guard; no var map at all (null) = guarded as before")
    Cfg.GUARD_ON = False
    K.check("off" in str(R.guardAll()), "X blade.guard.enabled off: guardAll says off (unchanged)")
    Cfg.GUARD_ON = True
    K.eq([int(R.onLoaded(None))], [0], "X onLoaded ignores a non-event (unchanged)")
    K.save()


# ---------------------------------------------------------------------------------------------------------------- D: live
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    JClass(PKG + "ArmoryLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyArmory")
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg = JClass(PKG + "ArmoryCfg")
    Paths = JClass("java.nio.file.Paths")
    Cfg.DIR = Paths.get(home)
    Cfg.FILE = Paths.get(home).resolve("config.properties")
    fp = os.path.join(home, "config.properties")
    b0 = open(fp, "rb").read()
    hashes = [HK.tree_hash(home)]
    for start in (1, 2):
        rs = [str(getattr(Cfg, m)()) for m in MIGS]
        Cfg.load()
        hashes.append(HK.tree_hash(home))
        if start == 1:
            K.notes.append("D start 1 migrations: %s" % [x[:120] for x in rs if x])
    K.check(hashes[1] == hashes[2], "D start 2 changes nothing")
    K.check(hashes[0] == hashes[1], "D start 1 changes nothing either (0.1.51 has no row / migration)")
    t1 = open(fp, "rb").read()
    K.check(b"0.1.51" not in t1 and (b"\r\n" in b0) == (b"\r\n" in t1), "D 0.1.51 writes nothing of its own; line endings kept")
    K.check(bool(Cfg.GUARD_ON) == (b"blade.guard.enabled=false" not in b0) and bool(Cfg.RUSH_ON) == (b"blade.rush.enabled=false" not in b0),
            "D the live guard / rush switches read as before (%s / %s)" % (bool(Cfg.GUARD_ON), bool(Cfg.RUSH_ON)))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyArmory", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("exec", run_exec), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyArmory"))
