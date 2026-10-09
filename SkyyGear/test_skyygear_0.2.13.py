"""Harness for SkyyGear 0.2.13 (speed tiers for the Crude / Scrap weapons - Skyy 2026-10-09 "the copper axe shows attack speed. my crude one
doesnt" - and the 18 mace 'Missing interaction ..._StaminaCondition_Next_Next' load warnings). Build first:
    python tools/gear_0_2_13_patch.py && python SkyyGear/build_skyygear_0.2.13.py

    python SkyyGear/test_skyygear_0.2.13.py [--jar <SkyyGear-0.2.13.jar>] [--old <SkyyGear-0.2.12.jar>] [--dir <scratch>] [--keep]

The 0.2.11 harness's helpers (stand-ins F, verify A, the bare-server boot of V, the engine-access audit AA) are loaded from
SkyyGear/test_skyygear_0.2.11.py and run on the 0.2.13 jar (the 0.2.12 harness does the same).
  S  THE SPEED ASSETS (python, both jars): every 0.2.12 speed file is in 0.2.13; with the 18 named Charging children put back inline and
     the SkyyGear_Spd_ variable names put back, every 0.2.13 speed file equals 0.2.12's (JSON) - maces (and every family) swing exactly as
     before; the only new files are the 18 named mace children; no one-entry Parallel anywhere in the jar; no inline child of an inline
     Charging; the 5 Crude / Scrap weapons' overrides are cosmetic (sound / trail) only
  A  every class of the jar loads + verifies (-Xverify:all)
  E  THE ENGINE ASSET VALIDATORS + THE LOAD WARNINGS (fresh JVM per jar, the real InteractionPacketGenerator with a setup packet consumer =
     the server's startup): the vanilla stats + interactions, then the jar's speed interactions in ONE batch like a pack: 0.2.12 logs the
     18 'Missing interaction **SkyyGear_Spd.._StaminaCondition_Next_Next..' lines (the control), 0.2.13 logs NONE; the engine validators
     (decode, validate, logOrThrowValidatorExceptions, contained assets) pass on the 9 changed StaminaCondition files + the 18 new ones;
     RootInteraction.build() of the 3 mace tier walks resolves only real interactions, the named children among them
  V  the vanilla pack store by store + THE JAR as its own pack (the 0.2.11 boot): no failed store of its own
  X  EVERY CODE PATH EXECUTED on the real Item store (-Xverify:all): X1 famOf / okVar (the 5 Crude / Scrap weapons in their family, other
     items with those variables refused, animation-set items still none); X2 a tier on every creation / identify path (newDoc identified,
     craftDoc, identify of an unidentified one, the mystery-bag open, the craft bridge doc + GearData.put safety net, a class kit / legacy
     stamp) and never on an unidentified one; X3 THE LAZY HEAL: an identified Crude battleaxe from 0.2.12 (no "spd") gets exactly "spd" on
     the stamp scan (stampStack), every other field equal, a second scan writes nothing, an unidentified one stays without, swing.tiers off
     = no roll; X4 the tooltip lines "Attack Speed" / "Charged at" for the Crude battleaxe
  C  CLASS COMPARE 0.2.12 -> 0.2.13 (javassist members): no class added / removed, only GearSpeed (okVar added, famCalc, clinit) changed;
     non-class entries: manifest.json + the speed interactions
  D  START TWICE on a scratch COPY of the live Skyy_SkyyGear folder: the file is byte-identical, nothing added
  AA THE ENGINE-ACCESS AUDIT
Scratch: tools/dev/scratch/gear0213/gear (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B

VERSION = "0.2.13"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCR_ROOT = os.path.join(TOOLS, "dev", "scratch", "gear0213")
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "gear")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(SCR_ROOT, "SkyyGear-0.2.12.jar")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyGear")
PKG = "com.skyy.gear."
EXPECT_CHANGED = {"GearSpeed"}
SPD_DIR = "Server/Item/Interactions/SkyyGear/Speed/"
COSM = {"Weapon_Battleaxe_Crude": "Battleaxe", "Weapon_Daggers_Crude": "Daggers", "Weapon_Mace_Crude": "Mace", "Weapon_Sword_Crude": "Sword",
        "Weapon_Sword_Scrap": "Sword"}
NOTIER = ["Weapon_Battleaxe_Doomed", "Weapon_Club_Zombie_Arm", "Weapon_Club_Zombie_Leg", "Weapon_Longsword_Praetorian_NPC", "Weapon_Mace_Scrap_NPC"]
ASSETS = os.path.join(os.path.dirname(B.SERVER_JAR), "..", "Assets.zip")

# ---- the 0.2.11 harness's helpers, run on THIS jar (its module text without its main call)
_H211 = os.path.join(HERE, "test_skyygear_0.2.11.py")
_t = open(_H211, encoding="utf-8").read()
_cut = _t.rindex('if __name__ == "__main__":')
H = {"__name__": "skyygear_h211", "__file__": _H211, "__builtins__": __builtins__}
exec(compile(_t[:_cut], _H211 + " (helpers)", "exec"), H)
H.update({"JAR": JAR, "OLD_JAR": OLD_JAR, "SCRATCH": SCRATCH, "FAKE_DIR": os.path.join(SCRATCH, "fake"), "VERSION": VERSION})
FAKE_DIR, FAKE_PKG = H["FAKE_DIR"], H["FAKE_PKG"]
Child, _jvm, jar_classes = H["Child"], H["_jvm"], H["jar_classes"]
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


# ====================================================================================================== S: the speed assets (python)
def _walk(x, fn, top=True):
    if isinstance(x, dict):
        fn(x, top)
        for v in x.values():
            _walk(v, fn, False)
    elif isinstance(x, list):
        for v in x:
            _walk(v, fn, False)


def _unname(x, files):
    """0.2.13 -> 0.2.12 form: named Charging children inline again, SkyyGear_Spd_<Var> -> <Var>"""
    if isinstance(x, list):
        return [_unname(v, files) for v in x]
    if not isinstance(x, dict):
        return x
    y = {}
    for k, v in x.items():
        y[k] = _unname(v, files)
    if y.get("Type") == "Replace" and isinstance(y.get("Var"), str) and y["Var"].startswith("SkyyGear_Spd_"):
        y["Var"] = y["Var"][len("SkyyGear_Spd_"):]
    if y.get("Type") == "Charging" and isinstance(y.get("Next"), dict):
        nx = {}
        for k, v in y["Next"].items():
            if isinstance(v, str) and v in files and "_Hold" in v:
                v = _unname(files[v], files)
            nx[k] = v
        y["Next"] = nx
    return y


def run_speed_assets():
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    oi = dict((n, json.loads(zo.read(n))) for n in zo.namelist() if n.startswith("Server/") and n.endswith(".json") and "/SkyyGear/Speed/" in n)
    ni = dict((n, json.loads(zn.read(n))) for n in zn.namelist() if n.startswith("Server/") and n.endswith(".json") and "/SkyyGear/Speed/" in n)
    new = sorted(set(ni) - set(oi))
    gone = sorted(set(oi) - set(ni))
    check(not gone and len(new) == 18 and all(n.startswith(SPD_DIR + "SkyyGear_Spd") and "_Mace_" in n and re.search(r"_StaminaCondition_Hold0(p2)?\.json$", n)
                                              for n in new),
          "S1: every 0.2.12 speed file is in 0.2.13; the only new ones are the 18 named mace Charging children (<file>_Hold0 / _Hold0p2): new %s gone %s" % (new[:4], gone[:4]))
    named = dict((os.path.basename(n)[:-5], ni[n]) for n in ni if n.startswith(SPD_DIR))
    diff = []
    for n in sorted(oi):
        a = oi[n]
        b = _unname(ni[n], named)
        if a != b:
            diff.append(n)
    check(not diff, "S2: every speed asset (interactions, walk roots, decision trees, animation sets, effects) put back in 0.2.12 form equals 0.2.12's "
          "exactly - the swings (maces too) are unchanged for every item that had a tier: differ %s" % diff[:4])
    rv = sum(1 for n in ni for _ in [0] if '"SkyyGear_Spd_' in json.dumps(ni[n]))
    check(rv > 0, "S2: the renamed variables are really used (%d files)" % rv)
    # S3 the jar-wide shape checks
    par, inl, oldv = [], [], []
    for n in zn.namelist():
        if not n.endswith(".json") or not n.startswith("Server/"):
            continue
        j = json.loads(zn.read(n))
        _walk(j, lambda x, top: par.append(n) if x.get("Type") == "Parallel" and len(x.get("Interactions") or []) < 2 else None)
        if n.startswith(SPD_DIR):
            _walk(j, lambda x, top: inl.append(n) if (not top and x.get("Type") == "Charging"
                                                     and any(isinstance(c, dict) for c in (x.get("Next") or {}).values())) else None)
    check(not par, "S3: no Parallel with fewer than 2 entries in any JSON of the jar: %s" % par[:3])
    check(not inl, "S3: no inline child of an inline Charging step in any speed file: %s" % inl[:3])
    # the 9 mace StaminaCondition files of 0.2.13 name their children; those children are the 0.2.12 inline objects
    sc = [n for n in ni if n.endswith("_Charged_StaminaCondition.json")]
    okc = 0
    for n in sc:
        ch = ni[n]["Next"]
        if ch.get("Type") == "Charging" and all(isinstance(v, str) and v.startswith(os.path.basename(n)[:-5] + "_Hold") for v in ch["Next"].values()):
            okc += 1
    check(len(sc) == 9 and okc == 9, "S3: the 9 mace StaminaCondition copies (3 tiers x 3 swings) point their Charging at the named children (%d / %d)" % (okc, len(sc)))
    # S4 the 5 cosmetic weapons' overrides vs the vanilla defaults (Assets.zip read in memory)
    az = zipfile.ZipFile(ASSETS)
    idx = {}
    for n in az.namelist():
        if n.startswith("Server/Item/Items/") and n.endswith(".json"):
            idx[os.path.basename(n)[:-5]] = n
    bad = []
    for iid in COSM:
        vv = json.loads(az.read(idx[iid]).decode("utf-8-sig")).get("InteractionVars") or {}
        for k, o in vv.items():
            x = (o.get("Interactions") or [None])[0] if isinstance(o, dict) else None
            if not isinstance(x, dict) or not x.get("Parent", "").startswith("Weapon_"):
                continue
            eff = x.get("Effects") or {}
            if "Primary_" in x["Parent"] and k in ("Swing_Down", "Swing_Left", "Swing_Right", "Swing_Down_Left", "Swing_Down_Right", "Swing_Left_Start",
                                                    "Swing_Right_Start", "Swing_Up_Left_Start", "Stab_Left_Selector", "Stab_Right_Selector",
                                                    "Swing_Left_Selector", "Swing_Right_Selector", "Swing_Down_Selector"):
                if set(x) - {"Parent", "Effects", "$Comment"} or set(eff) - {"WorldSoundEventId", "LocalSoundEventId", "Trails"}:
                    bad.append((iid, k))
    check(not bad, "S4: the Crude / Scrap swing-step overrides change only sounds / trails (else no tier): %s" % bad)
    print("S. speed assets: %d files in 0.2.12, %d in 0.2.13 (+%d named mace children); equal after un-naming; %d use renamed variables"
          % (len(oi), len(ni), len(new), rv))


# ====================================================================================================== E: the load warnings (engine)
def run_warn(out, which):
    """the SkyySkills 0.4.23 E2 way: real stores with the InteractionPacketGenerator + a setup packet consumer, the jar's speed interactions
    in ONE batch like a pack load"""
    from jpype import JClass, JArray, JString, JImplements, JOverride
    K = Child(out)
    jar = OLD_JAR if which == "old" else JAR
    _jvm([B.SERVER_JAR, B.JAVASSIST], verify=True, big=True)
    Paths, ArrayList, CHM = JClass("java.nio.file.Paths"), JClass("java.util.ArrayList"), JClass("java.util.concurrent.ConcurrentHashMap")
    U = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    U.setAccessible(True)
    U = U.get(None)

    def jfield(cls, name):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        return f
    Options = JClass("com.hypixel.hytale.server.core.Options")
    Options.parse(JArray(JString)(["--universe", os.path.join(SCRATCH, "universe-" + which)]))
    HS = JClass("com.hypixel.hytale.server.core.HytaleServer")
    hs = U.allocateInstance(HS.class_)
    jfield(HS, "eventBus").set(hs, JClass("com.hypixel.hytale.event.EventBus")(False))
    jfield(HS, "instance").set(None, hs)
    UNI = JClass("com.hypixel.hytale.server.core.universe.Universe")
    uni = U.allocateInstance(UNI.class_)
    pbu, wmap = CHM(), CHM()
    jfield(UNI, "playersByUuid").set(uni, pbu)
    jfield(UNI, "players").set(uni, JClass("java.util.Collections").unmodifiableCollection(pbu.values()))
    jfield(UNI, "worlds").set(uni, wmap)
    jfield(UNI, "worldsByUuid").set(uni, CHM())
    jfield(UNI, "unmodifiableWorlds").set(uni, JClass("java.util.Collections").unmodifiableMap(wmap))
    jfield(UNI, "instance").set(None, uni)
    CAP = JClass("java.util.concurrent.CopyOnWriteArrayList")()
    JClass("com.hypixel.hytale.logger.backend.HytaleLoggerBackend").subscribe(CAP)

    def records():
        o_ = []
        for r in list(CAP):
            msg = str(r.getMessage())
            ps = r.getParameters()
            if ps is not None and len(ps) > 0:
                try:
                    msg = str(JClass("java.lang.String").format(msg, ps))
                except Exception:
                    msg = msg + " " + " ".join(str(p) for p in ps)
            o_.append((str(r.getLevel()), msg))
        return o_
    JClass("com.hypixel.hytale.server.core.asset.AssetRegistryLoader").init()
    AR = JClass("com.hypixel.hytale.assetstore.AssetRegistry")
    HAS = JClass("com.hypixel.hytale.server.core.asset.HytaleAssetStore")
    ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
    ARR = JClass("java.lang.reflect.Array")
    PI = "com.hypixel.hytale.server.core.modules.interaction.interaction.config."
    INTc, ROOTc = JClass(PI + "Interaction"), JClass(PI + "RootInteraction")
    SMI = JClass(PI + "none.simple.SendMessageInteraction")

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
    class Rep:
        def __init__(self, root=False): self.root = root

        @JOverride
        def apply(self, k):
            if self.root:
                return ROOTc(str(k), JArray(JString)([]))
            return SMI(str(k), "removed " + str(k))

    @JImplements("java.util.function.Predicate")
    class IsUnknown:
        @JOverride
        def test(self, o): return bool(o.isUnknown())

    @JImplements("java.util.function.Consumer")
    class Sink:
        def __init__(self): self.n = 0

        @JOverride
        def accept(self, p): self.n += 1
    IPG = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.InteractionPacketGenerator")
    AR.register(HAS.builder(INTc.class_, ILT(ArrOf(INTc))).setPath("Item/Interactions").setCodec(INTc.CODEC).setKeyFunction(GetId())
                .setReplaceOnRemove(Rep()).setIsUnknown(IsUnknown()).setPacketGenerator(IPG()).build())
    AR.register(HAS.builder(ROOTc.class_, ILT(ArrOf(ROOTc))).setPath("Item/RootInteractions").setCodec(ROOTc.CODEC).setKeyFunction(GetId())
                .setReplaceOnRemove(Rep(True)).build())
    ESTc = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")
    AR.register(HAS.builder(ESTc.class_, ILT(ArrOf(ESTc))).setPath("Entity/Stats").setCodec(ESTc.CODEC).setKeyFunction(GetId())
                .setReplaceOnRemove(Rep()).build())
    sink = Sink()
    HAS.SETUP_PACKET_CONSUMERS.add(sink)
    CPool = JClass("javassist.bytecode.ConstPool")
    CPj = JClass("javassist.ClassPool")(True)
    CPj.appendClassPath(B.SERVER_JAR)
    imc = CPj.get("com.hypixel.hytale.server.core.modules.interaction.InteractionModule")
    ms_ = [x for x in imc.getDeclaredMethods() if str(x.getName()) == "setup"][0]
    cp_, it_ = ms_.getMethodInfo().getConstPool(), ms_.getMethodInfo().getCodeAttribute().iterator()
    last_s, last_c, regs = None, None, []
    while it_.hasNext():
        p_ = it_.next()
        op_ = it_.byteAt(p_)
        if op_ in (0x12, 0x13):
            ix = it_.byteAt(p_ + 1) if op_ == 0x12 else it_.u16bitAt(p_ + 1)
            t_ = cp_.getTag(ix)
            if t_ == CPool.CONST_String:
                last_s = str(cp_.getStringInfo(ix))
            elif t_ == CPool.CONST_Class:
                last_c = str(cp_.getClassInfo(ix))
        elif op_ == 0xb6:
            ix = it_.u16bitAt(p_ + 1)
            if str(cp_.getMethodrefClassName(ix)).endswith("AssetCodecMapCodec") and str(cp_.getMethodrefName(ix)) == "register":
                regs.append((last_s, last_c))
    for nm_, cl_ in regs:
        C_ = JClass(cl_)
        INTc.CODEC.register(nm_, C_.class_, jfield(C_, "CODEC").get(None))
    AEI, ADT = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo"), JClass("com.hypixel.hytale.assetstore.AssetExtraInfo$Data")
    RJR = JClass("com.hypixel.hytale.codec.util.RawJsonReader")
    az = zipfile.ZipFile(ASSETS)
    jz = zipfile.ZipFile(jar)
    work = os.path.join(SCRATCH, "eng-" + which)

    def put(sub, name, text):
        d = os.path.join(work, sub)
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        return Paths.get(p)

    def loadp(cls, pack, paths):
        l_ = ArrayList()
        for p in paths:
            l_.add(p)
        return not AR.getAssetStore(cls.class_).loadAssetsFromPaths(pack, l_).hasFailed()
    # the vanilla stat types (Stamina / StaminaRegenDelay ...), their effect hooks left out
    stl = ArrayList()
    for n in az.namelist():
        if n.startswith("Server/Entity/Stats/") and n.endswith(".json"):
            d = json.loads(az.read(n).decode("utf-8-sig"))
            for x_ in ("Regenerating", "MinValueEffects", "MaxValueEffects"):
                d.pop(x_, None)
            k = os.path.basename(n)[:-5]
            try:
                stl.add(AR.getAssetStore(ESTc.class_).getCodec().decodeJsonAsset(RJR.fromJsonString(json.dumps(d)), AEI(Paths.get(k + ".json"), ADT(ESTc.class_, k, None))))
            except Exception:
                pass
    AR.getAssetStore(ESTc.class_).loadAssets("Hytale:Hytale", stl)
    # every vanilla interaction + root interaction (the speed copies name vanilla steps), one batch each
    van = [n for n in az.namelist() if n.startswith("Server/Item/Interactions/") and n.endswith(".json")]
    vr = [n for n in az.namelist() if n.startswith("Server/Item/RootInteractions/") and n.endswith(".json")]
    K.notes.append("vanilla interactions load ok: %s" % loadp(INTc, "Hytale:Hytale", [put("van/i/" + str(i % 40), os.path.basename(n), az.read(n).decode("utf-8-sig"))
                                                                                    for i, n in enumerate(van)]))
    loadp(ROOTc, "Hytale:Hytale", [put("van/r/" + str(i % 40), os.path.basename(n), az.read(n).decode("utf-8-sig")) for i, n in enumerate(vr)])
    # the jar's speed interactions in ONE batch (the pack load), then its speed roots
    ints = sorted(n for n in jz.namelist() if n.startswith(SPD_DIR) and n.endswith(".json"))
    n0, s0 = len(records()), sink.n
    ld = loadp(INTc, "Skyy:%s SkyyGear" % which, [put("jar/i", os.path.basename(n), jz.read(n).decode("utf-8")) for n in ints])
    rec = records()[n0:]
    miss = [m for lv, m in rec if "Missing interaction" in m and "SkyyGear_Spd" in m]
    kind = [m for m in miss if re.search(r"\*\*SkyyGear_Spd[FSX]_Mace_Weapon_Mace_Primary_Swing_(Left|Right|Up_Left)_Charged_StaminaCondition_Next_Next_0(\.2)?\b", m)]
    roots = sorted(n for n in jz.namelist() if n.startswith("Server/Item/RootInteractions/SkyyGear/Speed/") and n.endswith(".json"))
    loadp(ROOTc, "Skyy:%s SkyyGear" % which, [put("jar/r", os.path.basename(n), jz.read(n).decode("utf-8")) for n in roots])
    # the engine validators on the 9 StaminaCondition files + the named children (0.2.13), each decoded on its own
    HLOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyGearHarness")
    KNOWN = set(os.path.basename(n).rsplit(".", 1)[0] for n in list(az.namelist()) + list(jz.namelist()))

    def validate(key, text):
        m0 = len(records())
        st = AR.getAssetStore(INTc.class_)
        ei = AEI(Paths.get(key + ".json"), ADT(INTc.class_, key, None))
        try:
            o = st.getCodec().decodeJsonAsset(RJR.fromJsonString(text), ei)
        except Exception as e:
            return ["decode: " + str(e)[:300]]
        prob = []
        uk = [str(x) for x in ei.getUnknownKeys()]
        if uk:
            prob.append("unknown keys %s" % uk)
        try:
            st.getCodec().validate(o, ei)
        except Exception as e:
            prob.append("validate threw %s" % str(e)[:300])
        try:
            vr_ = ei.getValidationResults()
            if vr_ is not None:
                vr_.logOrThrowValidatorExceptions(HLOG)
        except Exception as e:
            for ln in re.findall(r"FAIL: ([^\n]*)", str(e)):
                m_ = re.search(r"'([^']+)'", ln)
                if not (m_ and m_.group(1) in KNOWN and ("doesn't exist" in ln or "does not exist" in ln)):
                    prob.append(ln[:300])
        try:
            ei.getData().loadContainedAssets(False)
        except Exception as e:
            prob.append("contained assets: %s" % str(e)[:300])
        for lv, m_ in records()[m0:]:
            for ln in re.findall(r"FAIL: ([^\n]*)", m_):
                m2_ = re.search(r"'([^']+)'", ln)
                if not (m2_ and m2_.group(1) in KNOWN and ("doesn't exist" in ln or "does not exist" in ln)):
                    prob.append(ln[:300])
        return prob
    vset = [n for n in ints if n.endswith("_Charged_StaminaCondition.json") or "_StaminaCondition_Hold" in n]
    val = {}
    for n in vset:
        p_ = validate(os.path.basename(n)[:-5], jz.read(n).decode("utf-8"))
        if p_:
            val[os.path.basename(n)] = p_[:2]
    # the 3 mace tier walks compile on the real stores
    ops, badops = [], []
    for t in "SFX":
        rid = "SkyyGear_SpdWalk%s_Mace" % t
        r = ROOTc.getAssetMap().getAsset(rid)
        if r is None:
            badops.append(rid + " missing")
            continue
        try:
            r.build()
            for i in range(int(r.getOperationMax())):
                inner = r.getOperation(i).getInnerOperation()
                if inner is not None and INTc.class_.isInstance(inner):
                    ops.append(str(inner.getId()))
        except Exception as e:
            badops.append("%s: %s" % (rid, str(e)[:200]))
    held = [o for o in ops if "_Hold" in o]
    inl = [o for o in ops if o.startswith("**SkyyGear") and "StaminaCondition_Next_Next" in o]
    K.save(load=ld, missing=miss, nmiss=len(miss), kind=len(kind), packets=sink.n - s0, val=val, nval=len(vset), ops=len(ops), held=held[:40],
           nheld=len(held), inl=len(inl), badops=badops, other=[m for lv, m in rec if lv in ("SEVERE",) and "SkyyGear_Spd" in m and "Mace" in m][:10])


# ====================================================================================================== X (the engine child)
def run_engine(out):
    from jpype import JClass, JInt
    K = Child(out)
    _jvm([B.SERVER_JAR, B.JAVASSIST, JAR, FAKE_DIR], verify=True, big=True)
    E = H["engine_boot"](K)
    ITEM = E["ITEM"]
    K.check(set(E["fail"]) <= set(E["vfail"]), "V: the jar as its own pack: no failed store of its own (%s vs vanilla %s)" % (E["fail"], E["vfail"]))
    # the bare-JVM gap the 0.2.11 harness lists (kind 'stamina'): V's boot has no StaminaRegenDelay stat, so the charge step (a ChangeStat on
    # it) fails validation HERE exactly like vanilla's own copy of it; E (stats loaded) runs the validators on the same files clean
    gap = re.compile(r"Asset '(Stamina|StaminaRegenDelay)' of type \S*EntityStatType doesn't exist")
    hold = [r for r in E["rec"] if r[0] in ("SEVERE", "WARNING") and "_Hold" in r[1]]
    bad = [r for r in hold if not ((gap.search(r[1]) and "_Hold0p2" in r[1] and len(re.findall(r"FAIL: ", r[1])) == len(gap.findall(r[1])))
                                   or re.match(r"Removing child asset '(\S+_Hold0p2)' of removed asset '\1'$", r[1]))]
    vgap = [r for r in E["vrec"] if r[0] == "SEVERE" and "StaminaRegenDelay" in r[1] and "Mace" in r[1]]
    K.check(not bad and (not hold or vgap), "V: nothing SEVERE / WARNING about the 18 named mace children except the bare-JVM StaminaRegenDelay gap "
            "vanilla's own mace steps hit too (%d ours, %d vanilla): %s" % (len(hold), len(vgap), bad[:2]))
    P = lambda n: JClass(PKG + n)
    Cfg, Spd, Roll, Data, Defs, Stamp, View, Unid, Pool = (P("GearCfg"), P("GearSpeed"), P("GearRoll"), P("GearData"), P("GearDefs"), P("GearStamp"),
                                                           P("GearView"), P("GearUnid"), P("GearPool"))
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    BD = JClass("org.bson.BsonDocument")
    Props = JClass("java.util.Properties")
    UUID = JClass("java.util.UUID")
    CHM = JClass("java.util.concurrent.ConcurrentHashMap")
    JClass("java.lang.System").getProperties().put("skyy.bridge", CHM())
    Cfg.apply(Props(), False)
    U1 = UUID.fromString("00000000-0000-0000-0000-00000000c013")
    fams = [str(x) for x in Spd.F_NAME]
    # ============================================================================ X1 famOf / okVar
    got = dict((i, int(Spd.famOf(i))) for i in COSM)
    K.check(all(got[i] >= 0 and fams[got[i]] == COSM[i] for i in COSM), "X1: the 5 Crude / Scrap weapons are tier weapons of their family: %s" % got)
    K.check(bool(Spd.okVar("Weapon_Battleaxe_Crude", "Swing_Down")) and not Spd.okVar("Weapon_Battleaxe_Crude", "Swing_Down_Selector")
            and not Spd.okVar("Weapon_Sword_Iron", "Swing_Down") and not Spd.okVar("Weapon_Battleaxe_Crude_X", "Swing_Down")
            and not Spd.okVar(None, "Swing_Down") and bool(Spd.okVar("Weapon_Daggers_Crude", "Stab_Left_Selector")),
            "X1: okVar: only the listed item + exactly its listed variables")
    nt = dict((i, int(Spd.famOf(i))) for i in NOTIER if ITEM.getAssetMap().getAsset(i) is not None)
    K.check(len(nt) >= 4 and all(v < 0 for v in nt.values()), "X1: items on another animation set still get no tier: %s" % nt)
    allw = [str(k) for k in ITEM.getAssetMap().getAssetMap().keySet() if str(k).startswith("Weapon_")]
    tierw = sorted(i for i in allw if int(Spd.famOf(i)) >= 0)
    K.check(len(tierw) == 123 and all(i in tierw for i in COSM) and all(i in tierw for i in ("Weapon_Battleaxe_Copper", "Weapon_Mace_Iron", "Weapon_Sword_Iron")),
            "X1: 123 vanilla tier weapons (0.2.12: 118 + the 5): %d" % len(tierw))
    K.check(int(Spd.famOf("Tool_Hatchet_Crude")) < 0 and int(Spd.famOf("Weapon_Shortbow_Crude")) < 0, "X1: tools / bows still never")
    # ============================================================================ X2 every creation / identify path rolls a tier
    CA = "Weapon_Battleaxe_Crude"

    def spd(d):
        return int(Spd.tierOf(d)) if d is not None else -9
    s0 = int(Spd.ROLLS.get())
    paths = {}
    for i in COSM:
        paths[i + " newDoc ident"] = spd(Roll.newDoc(i, JInt(2), True, "drop"))
        paths[i + " craftDoc"] = spd(Roll.craftDoc(i, U1))
        un = Roll.newDoc(i, JInt(2), False, "drop")
        paths[i + " unid stays without"] = spd(un)
        paths[i + " identify"] = spd(Roll.identify(i, un, U1))
        paths[i + " put safety net"] = spd(Data.gearDoc(Data.put(IS(i, JInt(1)), Data.legacy(i), U1).getMetadata()))
        ks = Stamp.stampStack(IS(i, JInt(1)), U1, None)       # a class kit / legacy item: no document
        paths[i + " kit stamp"] = spd(Data.gearDoc(ks.getMetadata()))
    okp = [k for k, v in paths.items() if ("stays without" in k and v == -1) or ("stays without" not in k and 0 <= v <= 3)]
    K.check(len(okp) == len(paths), "X2: a tier on every creation / identify path of the 5 weapons, none on the unidentified doc: %s"
            % dict((k, v) for k, v in paths.items() if k not in okp))
    K.check(int(Spd.ROLLS.get()) - s0 >= 25, "X2: the rolls are counted (%d)" % (int(Spd.ROLLS.get()) - s0))
    # the mystery bag: pick() for the battleaxe type - every picked tier weapon carries a tier
    ty = int(Pool.typeIdx("Weapon_Battleaxe"))
    bp = []
    for k in range(30):
        r = Unid.pick(JInt(ty), JInt(0), JInt(2), JInt(1), JInt(12), JInt(0), U1)
        if r is not None:
            bp.append((str(r[0]), spd(r[2]), spd(Data.gearDoc(r[3].getMetadata()))))
    K.check(len(bp) >= 20 and all(a >= 0 and a == b for _i, a, b in bp if int(Spd.famOf(_i)) >= 0) and any(int(Spd.famOf(_i)) >= 0 for _i, a, b in bp),
            "X2: the mystery-bag open (GearUnid.pick, Lv 1-12 battleaxe): every tier weapon it makes has a tier, the stack's doc too: %s"
            % sorted(set(bp))[:6])
    # ============================================================================ X3 the lazy heal (an identified Crude battleaxe from 0.2.12)
    old = Roll.newDoc(CA, JInt(2), True, "craft")
    old.remove("spd")
    md = BD()
    md.put(str(Defs.DOC_KEY), old)
    st = IS(CA, JInt(1)).withMetadata(md)
    K.check(spd(Data.gearDoc(st.getMetadata())) == -1 and bool(Data.identified(old)), "X3: set-up: an identified Rare Crude battleaxe without a tier")
    h1 = Stamp.stampStack(st, U1, None)
    d1 = Data.gearDoc(h1.getMetadata())
    a_ = json.loads(str(old.toJson()))
    b_ = json.loads(str(d1.toJson()))
    tb = b_.pop("spd", None)
    K.check(h1 is not st and tb is not None and 0 <= int(tb if not isinstance(tb, dict) else list(tb.values())[0]) <= 3 and a_ == b_,
            "X3: the stamp scan (first touch) adds exactly 'spd' - every other field (rarity, modifiers, level, ...) equal: %s" % sorted(set(a_) ^ set(b_)))
    h2 = Stamp.stampStack(h1, U1, None)
    K.check(h2 is h1 or str(Data.gearDoc(h2.getMetadata()).toJson()) == str(d1.toJson()), "X3: a second scan changes nothing (the tier is kept)")
    t1 = spd(d1)
    same = all(spd(Data.gearDoc(Stamp.stampStack(h1, U1, None).getMetadata())) == t1 for _ in range(10))
    K.check(same, "X3: the tier never re-rolls on later scans")
    un = Roll.newDoc(CA, JInt(2), False, "drop")
    md2 = BD()
    md2.put(str(Defs.DOC_KEY), un)
    hu = Stamp.stampStack(IS(CA, JInt(1)).withMetadata(md2), U1, None)
    K.check(spd(Data.gearDoc(hu.getMetadata())) == -1, "X3: an unidentified Crude battleaxe gets no tier on the scan")
    Cfg.SWING_ON = False
    ho = Stamp.stampStack(IS(CA, JInt(1)).withMetadata(md), U1, None)
    K.check(spd(Data.gearDoc(ho.getMetadata())) == -1, "X3: swing.tiers off = no roll on the scan")
    Cfg.SWING_ON = True
    # ============================================================================ X4 the tooltip lines
    shows = bool(Spd.shows(CA, d1))
    tl = Spd.tipLines(CA, d1)
    tl = [str(x) for x in tl if x is not None] if tl is not None else []
    cu = Data.gearDoc(Stamp.stampStack(IS("Weapon_Battleaxe_Copper", JInt(1)), U1, None).getMetadata())
    tc = Spd.tipLines("Weapon_Battleaxe_Copper", cu)
    tc = [str(x) for x in tc if x is not None] if tc is not None else []
    K.check(shows and tl and tl[0].startswith("Attack Speed: ") and len(tl) == len(tc) and any(x.startswith("Charged") for x in tl) == any(x.startswith("Charged") for x in tc),
            "X4: the Crude battleaxe's tooltip has the same speed lines as the Copper one: %s | Copper %s" % (tl, tc))
    for i in COSM:
        d_ = Roll.newDoc(i, JInt(1), True, "craft")
        K.check(bool(Spd.shows(i, d_)), "X4: %s shows its speed tier" % i)
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
    pa, pb = pool_of(OLD_JAR), pool_of(JAR)

    def members(p_, cn):
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
                # constant-pool shifts (ldc -> ldc_w) and the version string are not code changes
                lines_.append(re.sub(r"#\d+ = ", "", str(IP.instructionString(it_, pos_, cpl_))).replace("ldc_w ", "ldc ")
                              .replace("0.2.12", "VER").replace("0.2.13", "VER"))
            return "\n".join(lines_)
        for m_ in c_.getDeclaredMethods():
            d_["m " + str(m_.getName()) + str(m_.getSignature())] = code(m_)
        for m_ in c_.getDeclaredConstructors():
            d_["c " + str(m_.getSignature())] = code(m_)
        ci = c_.getClassInitializer()
        if ci is not None:
            d_["<clinit>"] = code(ci)
        return d_
    na, nb = jar_classes(OLD_JAR), jar_classes(JAR)
    K.check(na == nb, "C: no class added or removed: +%s -%s" % (sorted(set(nb) - set(na)), sorted(set(na) - set(nb))))
    diffs = {}
    for cn in sorted(set(na) & set(nb)):
        ma, mb = members(pa, cn), members(pb, cn)
        dd = sorted(k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k))
        if dd:
            diffs[cn[len(PKG):]] = [("+" if k not in ma else ("-" if k not in mb else "~")) + k.split("(")[0] for k in dd]
    print("C. class compare 0.2.12 -> 0.2.13:")
    for k in sorted(diffs):
        print("   %-16s %s" % (k, ", ".join(diffs[k])[:300]))
    unexpected = sorted(set(diffs) - EXPECT_CHANGED)
    K.check(not unexpected, "C: only GearSpeed differs (unexpected: %s)" % {k: diffs[k] for k in unexpected})
    K.check(sorted(diffs.get("GearSpeed", [])) == ["+f F_OKID", "+m okVar", "~<clinit>", "~m famCalc"],
            "C: GearSpeed: + F_OKID, + okVar, famCalc + the static init changed: %s" % diffs.get("GearSpeed"))
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    ea = [n for n in za.namelist() if not n.endswith(".class")]
    eb = [n for n in zb.namelist() if not n.endswith(".class")]
    ed = sorted(n for n in set(ea) | set(eb) if n not in ea or n not in eb or za.read(n) != zb.read(n))
    K.check(all(n == "manifest.json" or n.startswith(SPD_DIR) for n in ed) and "manifest.json" in ed,
            "C: non-class entries changed = manifest.json + speed interactions only: %s" % [n for n in ed if n != "manifest.json" and not n.startswith(SPD_DIR)])
    K.notes.append("non-class entries changed: manifest.json + %d speed interaction files" % (len(ed) - 1))
    K.save(diffs=diffs)


# ====================================================================================================== D: start twice on a live copy
def run_live(out, home):
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR], verify=True)
    Cfg = JClass(PKG + "GearCfg")
    Path = JClass("java.nio.file.Paths")
    Cfg.DIR = Path.get(home)
    Cfg.FILE = Path.get(os.path.join(home, "config.properties"))
    JClass(PKG + "GearLog").FILE = Path.get(os.path.join(home, "gear.log"))
    before = open(os.path.join(home, "config.properties"), "rb").read()
    files0 = sorted(os.path.relpath(os.path.join(r, f), home) for r, d, fs in os.walk(home) for f in fs)
    for step in (1, 2):
        for m in ("migrate011", "migrateStat011", "migrate012", "migrate013", "migrate02", "migrate021", "migrate023", "migrate025"):
            getattr(Cfg, m)()
        Cfg.load()
        after = open(os.path.join(home, "config.properties"), "rb").read()
        K.check(after == before, "D start %d: the live config.properties copy is byte-identical (0.2.13 has no config change)" % step)
        K.check(bool(Cfg.SWING_ON), "D start %d: swing.tiers reads on" % step)
    files1 = sorted(os.path.relpath(os.path.join(r, f), home) for r, d, fs in os.walk(home) for f in fs)
    K.check(files0 == files1, "D: no file added or removed by two starts (%d files)" % len(files0))
    K.save()


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
                     ("--engine", lambda: run_engine(arg("--out"))), ("--compare", lambda: run_compare(arg("--out"))),
                     ("--warn", lambda: run_warn(arg("--out"), arg("--warn"))),
                     ("--live", lambda: run_live(arg("--out"), arg("--live"))), ("--audit", lambda: H["run_audit"](arg("--out")))):
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
    assert os.path.isfile(JAR), JAR
    sc = os.path.realpath(SCRATCH)
    assert sc.startswith(os.path.realpath(SCR_ROOT) + os.sep), "the scratch folder must be inside tools/dev/scratch/gear0213"
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"), exist_ok=True)
    if not os.path.isfile(OLD_JAR):
        shutil.copyfile(os.path.join(HERE, "SkyyGear-0.2.12.jar"), OLD_JAR)
    with zipfile.ZipFile(OLD_JAR) as z_:
        assert '"Version": "0.2.12"' in z_.read("manifest.json").decode("utf-8"), "the old jar is not 0.2.12"
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.environ["TEMP"] = os.environ["TMP"] = env["TEMP"]
    try:
        run_speed_assets()
        p = child(env, "--mkfake", FAKE_DIR)
        check(p.returncode == 0, "F: the stand-ins were generated")
        W = {}
        for which in ("old", "new"):
            out = os.path.join(SCRATCH, "warn-%s.json" % which)
            pr = child(env, "--warn", which, "--out", out)
            check(pr.returncode == 0, "E %s: the child exited cleanly (%s)" % (which, pr.returncode))
            W[which] = take(out, "E-" + which) or {}
        o, n = W.get("old", {}), W.get("new", {})
        om, nm = sorted(o.get("missing") or []), sorted(n.get("missing") or [])
        okind = [m for m in om if re.search(r"\*\*SkyyGear_Spd[FSX]_Mace_Weapon_Mace_Primary_Swing_(Left|Right|Up_Left)_Charged_StaminaCondition_Next_Next_0", m)]
        rest = list(om)
        for m in okind:
            rest.remove(m)
        check(o.get("kind") == 18 and len(okind) == 18,
              "E: 0.2.12 control - the speed files loaded in ONE batch log the 18 'Missing interaction **SkyyGear_Spd{F,S,X}_Mace_..._Charged_"
              "StaminaCondition_Next_Next(_0/_0.2)' lines Skyy's log had: %d of the kind (%d SkyyGear_Spd lines in all in the bare JVM): %s"
              % (o.get("kind", -1), o.get("nmiss", -1), okind[:2]))
        check(n.get("kind") == 0 and nm == sorted(rest) and n.get("packets", 0) >= 1,
              "E: 0.2.13 - the same load logs NONE of the 18 (packet generator on, %s packets); its other bare-JVM lines (vanilla steps the bare JVM "
              "cannot load - none of them in Skyy's log) are exactly 0.2.12's minus the 18 (%d = %d - 18): extra %s" % (
                  n.get("packets"), len(nm), len(om), sorted(set(nm) - set(rest))[:3]))
        check(not n.get("val") and n.get("nval") == 27,
              "E: the ENGINE ASSET VALIDATORS pass on the 9 changed StaminaCondition files + the 18 named children (%s): %s" % (n.get("nval"), n.get("val")))
        check(not n.get("badops") and not o.get("badops") and n.get("ops", 0) > 0 and n.get("ops") == o.get("ops"),
              "E: RootInteraction.build() of the 3 mace tier walks compiles on the real stores, the same number of operations as 0.2.12 (%s / %s): %s"
              % (n.get("ops"), o.get("ops"), n.get("badops")))
        print("E. load warnings: 0.2.12 %s SkyyGear_Spd missing-interaction lines (%s of the mace kind), 0.2.13 %s; validators %s / %s files clean; "
              "mace walks: %s ops (0.2.12 %s)" % (o.get("nmiss"), o.get("kind"), n.get("nmiss"), n.get("nval", 0) - len(n.get("val") or {}),
                                                   n.get("nval"), n.get("ops"), o.get("ops")))
        for label, flag in (("verify", "--verify"), ("engine", "--engine"), ("compare", "--compare")):
            out = os.path.join(SCRATCH, "%s.json" % label)
            pr = child(env, flag, "--out", out)
            check(pr.returncode == 0, "%s: the child exited cleanly (%s)" % (label, pr.returncode))
            take(out, label)
        home = os.path.join(SCRATCH, "live")
        shutil.copytree(LIVE_DIR, home)
        print("D. live Skyy_SkyyGear copied (read-only source %s)" % LIVE_DIR)
        out = os.path.join(SCRATCH, "live.json")
        pr = child(env, "--live", home, "--out", out)
        check(pr.returncode == 0, "D: the child exited cleanly")
        take(out, "live")
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
