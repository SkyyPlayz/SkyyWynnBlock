"""Bare-JVM harness for SkyyTrees 0.3.4 (tools/trees_0_3_4_patch.py) - the LOG FIX: every SkyyTrees interaction file ships as NAMED files
(no inline step), so the engine never logs 'Missing interaction **Skyy_Tree_Chop_Wood_Next_Next' / '_Next_Failed' (Skyy's 2026-10-09 server
log). The SET pin 0.3.3 is the control everywhere; the live save data is only ever READ and copied into scratch.

    python SkyyTrees/test_skyytrees_0.3.4.py --dir <empty folder inside tools/dev/scratch/> [--jar <SkyyTrees-0.3.4.jar>]
                                             [--prev <SkyyTrees-0.3.3.jar>] [--live <Skyy_SkyyTrees folder>] [--keep] [--no33]

  A   every class of both jars loads, verifies and initialises (-Xverify:all, the game's own JRE)
  F   CLASS COMPARE 0.3.3 -> 0.3.4: the same class files; a changed class differs ONLY in the version text (its bytes with "0.3.4" put back
      to "0.3.3" are 0.3.3's bytes exactly); the method-by-method compare (the 0.3.1 helper) reports constant-only changes
  J   THE JAR: effects + the 2 root overrides byte-identical; manifest = version only; the 5 interaction files of 0.3.3 + 167 new named
      steps; no inline interaction left; every name a step uses = a jar file or a vanilla interaction; no new id is a vanilla id; no
      Parallel under 2 branches; RE-INLINED (an independent re-implementation here) every file = 0.3.3's file text exactly
  E   THE ENGINE (real asset stores, the real InteractionPacketGenerator, a setup packet consumer present = every batch builds its client
      packet - stricter than a live start), both jars, in separate JVMs:
      E1 the jar's interaction + root files loaded in ONE batch per store like a pack: 'Missing interaction' lines naming our steps
         (0.3.3: the inline-step kind incl. the **Skyy_Tree_Chop_Wood_Next_Next / _Next_Failed Skyy saw; 0.3.4: NONE). 'Missing root
         interaction' lines (inline ROOTS of the vanilla Hatchet_Chop copy) are compared with a TEST-BED CONTROL (a top-level Parallel with
         inline roots - the shape of 14 vanilla Parallel + 54 vanilla Selector files; 0 such lines in all 71 live server logs)
      E2 after the load every step of ours is the real interaction class (no Hytale:Hytale SendMessage placeholder left)
      E3 BEHAVIOUR: RootInteraction.build() of the jar's Pickaxe_Attack + Hatchet_Attack roots and of a root per top file - the op-class
         sequence, and a NAME-FREE fingerprint of the whole reachable graph (every field of every step, every reference replaced by the
         fingerprint of what it names: interactions AND roots) - equal in 0.3.3 and 0.3.4
      E4 the ENGINE ASSET VALIDATORS on every interaction / root file of the jar (decode, the codec's full validate,
         logOrThrowValidatorExceptions, contained assets) + the NEGATIVE CONTROL (a one-entry Parallel fails the same function, a
         two-entry one passes); a 'does not exist' for a name that IS in Assets.zip = the bare JVM's empty stores (a NOTE, same in 0.3.3)
  S   START TWICE on a scratch COPY of the live Skyy_SkyyTrees folder (the plugin's start order load -> TreeMig -> TreeMig32 -> TreeMig33
      -> CfgPub.start, each start in a fresh loader): 0.3.4 changes exactly what 0.3.3 changes (control) and the 2nd start writes nothing
  H33 the 0.3.3 harness run on the 0.3.4 jar (prev = 0.3.2, as it was written) next to the control run on the 0.3.3 jar: every check that
      passes for 0.3.3 passes for 0.3.4 except the jar-shape checks of its section E (the new interaction files); its M / P sections =
      the migrations + START TWICE on copies of the live data, its Z = the access audit
  Z   the engine-access audit of the 0.3.4 jar (every reference looked up with the JVM's own rules: 0 refused; the control is refused)
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util, copy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.3.4", "0.3.3"
PKG = "com.skyy.trees."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "skyytrees-034")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyTrees-%s.jar" % PREV_VERSION)))
JAR032 = os.path.join(HERE, "SkyyTrees-0.3.2.jar")
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE_DIR = os.path.abspath(arg("--live", os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyTrees")))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]
IDIR = "Server/Item/Interactions/"
RDIR = "Server/Item/RootInteractions/"
TOPS = ["Skyy_Tree_Chop", "Skyy_Tree_Chop_Chain", "Skyy_Tree_Chop_Wood", "Skyy_Tree_Swing_Chop", "Skyy_Tree_Swing_Mine"]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def t33():
    """the 0.3.3 harness module (its run_load child; it imports the 0.3.1 helpers as H) - imported, never run"""
    spec = importlib.util.spec_from_file_location("t033", os.path.join(HERE, "test_skyytrees_0.3.3.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.SCRATCH = SCRATCH
    m.H.SCRATCH = SCRATCH
    return m


# ================================================================================================ J: the jar's interaction files (python)
# an INDEPENDENT re-implementation of "where an interaction can sit" (not read from the build): Next / Failed (a Chaining's Next is a list),
# the interactions inside the inline roots of a Parallel branch, a Replace default, a Selector's HitEntity / HitBlock / rule Next
def islots(x):
    out = []
    for k in ("Next", "Failed"):
        v = x.get(k)
        if isinstance(v, list):
            out += [(v, i) for i in range(len(v))]
        elif v is not None:
            out.append((x, k))
    roots = []
    t = x.get("Type")
    if t == "Parallel":
        roots += [(x["Interactions"], j) for j in range(len(x["Interactions"]))]
    if t == "Replace" and "DefaultValue" in x:
        roots.append((x, "DefaultValue"))
    if t == "Selector":
        roots += [(x, k) for k in ("HitEntity", "HitBlock") if k in x]
        roots += [(r, "Next") for r in (x.get("HitEntityRules") or []) if "Next" in r]
    for c, k in roots:
        if isinstance(c[k], dict):
            l_ = c[k].get("Interactions") or []
            out += [(l_, i) for i in range(len(l_))]
    return out


def reinline(body, named):
    b = copy.deepcopy(body)
    for c, k in islots(b):
        if isinstance(c[k], str) and c[k] in named:
            c[k] = reinline(named[c[k]], named)
    return b


def has_inline(x, top=True):
    if isinstance(x, dict):
        if not top and "Type" in x:
            return True
        return any(has_inline(v, False) for v in x.values())
    if isinstance(x, list):
        return any(has_inline(v, False) for v in x)
    return False


def section_j(zp, zn, vanilla_ids, vanilla_int):
    np_, nn = set(zp.namelist()), set(zn.namelist())
    other = sorted(n for n in np_ | nn if not n.endswith(".class") and not n.startswith(IDIR) and n != "manifest.json" and not n.endswith("/"))
    check(all(n in np_ and n in nn and zp.read(n) == zn.read(n) for n in other) and len(other) == 82,
          "J: the 80 effect files + 2 root overrides byte-identical (%d other files)" % len(other))
    mp, mn = json.loads(zp.read("manifest.json")), json.loads(zn.read("manifest.json"))
    check(mp.get("Version") == PREV_VERSION and mn.get("Version") == VERSION and dict(mn, Version=PREV_VERSION, Name=mp.get("Name")) == mp
          and mn.get("Name") == mp.get("Name").replace(PREV_VERSION, VERSION), "J: manifest.json differs only in Version / Name (the version)")
    ip = dict((os.path.basename(n)[:-5], zp.read(n).decode("utf-8")) for n in np_ if n.startswith(IDIR) and n.endswith(".json"))
    inn = dict((os.path.basename(n)[:-5], zn.read(n).decode("utf-8")) for n in nn if n.startswith(IDIR) and n.endswith(".json"))
    check(sorted(ip) == TOPS and set(ip) <= set(inn) and len(inn) == 173, "J: 0.3.3's 5 interaction files + %d new = %d" % (len(inn) - len(ip), len(inn)))
    check(all(n.startswith(IDIR + "SkyyTrees/") for n in nn if n.startswith(IDIR) and n.endswith(".json")), "J: every interaction file in one folder (one batch)")
    bodies = dict((k, json.loads(v)) for k, v in inn.items())
    named = dict((k, v) for k, v in bodies.items() if k not in ip)
    check(all(json.dumps(reinline(bodies[t], named), indent=2) == ip[t] for t in TOPS),
          "J: every 0.3.4 file re-inlined = 0.3.3's file text exactly: %s" % [t for t in TOPS if json.dumps(reinline(bodies[t], named), indent=2) != ip[t]])
    check(not [k for k, b in bodies.items() if has_inline(b)], "J: no inline interaction left in any file")
    bad = []
    for k, b in bodies.items():
        for c, kk in islots(b):
            if not (isinstance(c[kk], str) and (c[kk] in bodies or c[kk] in vanilla_int)):
                bad.append((k, c[kk]))
    check(not bad, "J: every name a step uses is a jar file or a vanilla interaction: %s" % bad[:4])
    check(not [k for k in named if k in vanilla_ids] and all(re.match(r"^Skyy_Tree_\w+$", k) for k in named), "J: no new id is a vanilla id")
    check(not [k for k, b in bodies.items() if b.get("Type") == "Parallel" and len(b["Interactions"]) < 2], "J: no Parallel with < 2 branches")
    # the old files had inline steps (the 0.3.3 kind), the new ones none - the count of inline steps moved = the named steps
    def n_inline(x, top=True):
        if isinstance(x, dict):
            return (0 if top or "Type" not in x else 1) + sum(n_inline(v, False) for v in x.values())
        if isinstance(x, list):
            return sum(n_inline(v, False) for v in x)
        return 0
    old_inline = sum(n_inline(json.loads(v)) for v in ip.values())
    check(old_inline == len(named), "J: 0.3.3 had %d inline steps, 0.3.4 names %d (one file each, none shared)" % (old_inline, len(named)))
    tiers = [json.loads(inn["Skyy_Tree_Chop_Wood_Tier_%02d" % k])["Cooldown"]["Cooldown"] for k in range(41)]
    check(all(tiers[k] > tiers[k + 1] for k in range(40)) and tiers[0] == 0.217, "J: Chop_Wood tier 0 = the vanilla rest 0.217 s, faster each tier")
    print("J: %d interaction files (5 + %d named), 0.3.3 inline steps %d; every file re-inlined = 0.3.3" % (len(inn), len(named), old_inline))
    return sorted(inn)


# ================================================================================================ F: class compare
def section_f(zp, zn):
    cp = sorted(n for n in zp.namelist() if n.endswith(".class"))
    cn = sorted(n for n in zn.namelist() if n.endswith(".class"))
    check(cp == cn and len(cn) > 30, "F: the same %d class files" % len(cn))
    changed, other = [], []
    for n in cn:
        a, b = zp.read(n), zn.read(n)
        if a == b:
            continue
        changed.append(n.split("/")[-1][:-6])
        if b"0.3.4" in a or b.replace(b"0.3.4", b"0.3.3") != a:
            other.append(n)
    check(not other, "F: changed classes differ ONLY in the version text (0.3.4 -> 0.3.3 gives 0.3.3's bytes): %s" % other)
    print("F: %d classes, %d changed (version text only): %s" % (len(cn), len(changed), ", ".join(changed)))
    return changed


# ================================================================================================ child: the engine (one jar)
def run_engine(jar, out, mode):
    import jpype
    from jpype import JClass, JArray, JString, JImplements, JOverride
    import skyybuild as SB
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jpype.startJVM(SB._jvm(), "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[SB.SERVER_JAR, jar, SB.JAVASSIST], convertStrings=True)
    R = {"mode": mode}
    Uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    Uf.setAccessible(True)
    U = Uf.get(None)
    CHM, ArrayList, Paths = JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.util.ArrayList"), JClass("java.nio.file.Paths")
    Mod = JClass("java.lang.reflect.Modifier")

    def jfield(cls, name):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        return f
    # the server singletons the stores read (the SkyySkills 0.4.23 harness way)
    JClass("com.hypixel.hytale.server.core.Options").parse(JArray(JString)(["--universe", os.path.join(SCRATCH, "universe-" + mode)]))
    HS = JClass("com.hypixel.hytale.server.core.HytaleServer")
    hs = U.allocateInstance(HS.class_)
    jfield(HS, "eventBus").set(hs, JClass("com.hypixel.hytale.event.EventBus")(False))
    jfield(HS, "instance").set(None, hs)
    UNI = JClass("com.hypixel.hytale.server.core.universe.Universe")
    uni = U.allocateInstance(UNI.class_)
    pbu = CHM()
    jfield(UNI, "playersByUuid").set(uni, pbu)
    jfield(UNI, "players").set(uni, JClass("java.util.Collections").unmodifiableCollection(pbu.values()))
    wmap = CHM()
    jfield(UNI, "worlds").set(uni, wmap)
    jfield(UNI, "worldsByUuid").set(uni, CHM())
    jfield(UNI, "unmodifiableWorlds").set(uni, JClass("java.util.Collections").unmodifiableMap(wmap))
    jfield(UNI, "instance").set(None, uni)
    CAP = JClass("java.util.concurrent.CopyOnWriteArrayList")()
    JClass("com.hypixel.hytale.logger.backend.HytaleLoggerBackend").subscribe(CAP)

    def records():
        out_ = []
        for r in list(CAP):
            msg = str(r.getMessage())
            ps = r.getParameters()
            if ps is not None and len(ps) > 0:
                try:
                    msg = str(JClass("java.lang.String").format(msg, ps))
                except Exception:
                    msg = msg + " " + " ".join(str(p) for p in ps)
            out_.append((str(r.getLevel()), msg))
        return out_
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
    sink = Sink()
    HAS.SETUP_PACKET_CONSUMERS.add(sink)          # every loaded batch builds its client packet (stricter than a live start)
    # the interaction Type codecs and the Selector types exactly as InteractionModule.setup registers them (read from its bytecode)
    CPool = JClass("javassist.bytecode.ConstPool")
    CPj = JClass("javassist.ClassPool")(True)
    CPj.appendClassPath(SB.SERVER_JAR)
    ms_ = [x for x in CPj.get("com.hypixel.hytale.server.core.modules.interaction.InteractionModule").getDeclaredMethods() if str(x.getName()) == "setup"][0]
    cp_, it_ = ms_.getMethodInfo().getConstPool(), ms_.getMethodInfo().getCodeAttribute().iterator()
    last_s, last_c, regs, ev = None, None, [], []
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
        elif op_ == 0xb2:
            idx = it_.u16bitAt(p_ + 1)
            ev.append(("get", str(cp_.getFieldrefClassName(idx)), str(cp_.getFieldrefName(idx)), last_s))
        elif op_ == 0xb6:
            idx = it_.u16bitAt(p_ + 1)
            cn_, mn_ = str(cp_.getMethodrefClassName(idx)), str(cp_.getMethodrefName(idx))
            if cn_.endswith("AssetCodecMapCodec") and mn_ == "register":
                regs.append((last_s, last_c))
            elif cn_ == "com.hypixel.hytale.codec.lookup.CodecMapCodec" and mn_ == "register":
                ev.append(("reg",))
    for nm_, cl_ in regs:
        C_ = JClass(cl_)
        INTc.CODEC.register(nm_, C_.class_, jfield(C_, "CODEC").get(None))
    STc = JClass(PI + "selector.SelectorType")
    sels = []
    for i, e in enumerate(ev):
        if e[0] == "reg" and i >= 2 and ev[i - 1][0] == "get" and ev[i - 1][2] == "CODEC" and ev[i - 2][0] == "get" and ev[i - 2][1].endswith(".SelectorType"):
            C_ = JClass(ev[i - 1][1])
            STc.CODEC.register(ev[i - 1][3], C_.class_, jfield(C_, "CODEC").get(None))
            sels.append(ev[i - 1][3])
    R["codecs"], R["selectors"] = len(regs), sels
    AEI, ADT = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo"), JClass("com.hypixel.hytale.assetstore.AssetExtraInfo$Data")
    RJR = JClass("com.hypixel.hytale.codec.util.RawJsonReader")
    az = zipfile.ZipFile(os.path.join(os.path.dirname(SB.SERVER_JAR), "..", "Assets.zip"))
    jz = zipfile.ZipFile(jar)
    work = os.path.join(SCRATCH, "eng-" + mode)

    def put(sub, name, text):
        p = os.path.join(work, sub, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        return Paths.get(p)

    def jlist(xs):
        l_ = ArrayList()
        for x_ in xs:
            l_.add(x_)
        return l_

    def loadp(cls, pack, paths):
        r = AR.getAssetStore(cls.class_).loadAssetsFromPaths(pack, jlist(paths))
        return not r.hasFailed()
    # the vanilla interactions our steps name: stand-ins (a SendMessage under the vanilla id; only the ids matter for name resolution)
    jnames = [n for n in jz.namelist() if n.startswith(IDIR) and n.endswith(".json")]
    jbodies = dict((os.path.basename(n)[:-5], json.loads(jz.read(n).decode("utf-8"))) for n in jnames)
    vint = set(os.path.basename(n)[:-5] for n in az.namelist() if n.startswith(IDIR) and n.endswith(".json"))

    def strings(x):
        if isinstance(x, dict):
            return [s2 for v in x.values() for s2 in strings(v)]
        if isinstance(x, list):
            return [s2 for v in x for s2 in strings(v)]
        return [x] if isinstance(x, str) else []
    vnames = sorted(set(s_ for b in jbodies.values() for s_ in strings(b) if s_ in vint))   # every vanilla interaction id a file names
    R["vanilla_names"] = vnames
    AR.getAssetStore(INTc.class_).loadAssets("Hytale:Hytale", jlist([SMI(v, "stand-in " + v) for v in vnames]))
    # ---- E1 the test-bed control: a top-level Parallel with inline roots (the vanilla shape) in its own batch
    n0 = len(records())
    R["ctl_load"] = loadp(INTc, "Test:Control", [put("ctl", "SkyyHarness_TopParallel.json", json.dumps(
        {"Type": "Parallel", "Interactions": [{"Interactions": ["Block_Break"]}, {"Interactions": ["Block_Break"]}]}))])
    R["ctl_lines"] = [m_ for lv, m_ in records()[n0:] if "Missing" in m_]
    # ---- E1 the jar: interactions in ONE batch, then the roots (RootInteraction loadsAfter Interaction), real file paths
    n0, s0 = len(records()), sink.n
    R["load"] = loadp(INTc, "Skyy:%s SkyyTrees" % mode, [put("S/" + os.path.dirname(n), os.path.basename(n), jz.read(n).decode("utf-8")) for n in sorted(jnames)])
    lines = [m_ for lv, m_ in records()[n0:]]
    rnames = sorted(n for n in jz.namelist() if n.startswith(RDIR) and n.endswith(".json"))
    R["root_load"] = loadp(ROOTc, "Skyy:%s SkyyTrees" % mode, [put("S/" + os.path.dirname(n), os.path.basename(n), jz.read(n).decode("utf-8")) for n in rnames])
    lines += [m_ for lv, m_ in records()[n0 + len(lines):]]
    R["missing_int"] = [m_ for m_ in lines if m_.startswith("Missing interaction") and "Skyy_Tree" in m_]
    R["missing_root"] = [m_ for m_ in lines if m_.startswith("Missing root interaction") and "Skyy_Tree" in m_]
    R["missing_other"] = [m_ for m_ in lines if "Missing" in m_ and "Skyy_Tree" not in m_]
    R["severe"] = [m_[:300] for m_ in lines if "Failed to" in m_ or "Exception" in m_]
    R["packets"] = sink.n - s0
    # ---- E2 every step of ours is real (no placeholder)
    imap = INTc.getAssetMap()
    ours = sorted(str(k) for k in imap.getAssetMap().keySet() if "Skyy_Tree" in str(k))
    R["ours"] = len(ours)
    R["placeholders"] = [k for k in ours if SMI.class_.isInstance(imap.getAsset(k))]
    R["classes"] = sorted(set(str(imap.getAsset(k).getClass().getSimpleName()) for k in ours))
    # ---- E3 behaviour: a NAME-FREE fingerprint of everything reachable + the compiled op sequence of the roots
    rmap = ROOTc.getAssetMap()
    SKIP = {"id", "data", "cachedPacket", "operations", "operationMax"}
    memo = {}

    def is_ref(s_):
        return s_ in vnames or imap.getAsset(s_) is not None or rmap.getAsset(s_) is not None

    def fp_root(rid, depth):
        a = rmap.getAsset(rid)
        return "R[" + ",".join(fp_ref(str(x_), depth + 1) for x_ in a.getInteractionIds()) + "]" + fp_obj(a, depth + 1, root=True)

    def fp_ref(s_, depth):
        """what a name stands for, by meaning: a vanilla stand-in by its name, ours (an interaction, else a root) by its fingerprint"""
        if s_ in vnames:
            return "vanilla:" + s_
        if s_ in memo:
            return memo[s_]
        if depth > 80:
            return "too-deep"
        if imap.getAsset(s_) is not None:
            v = "I" + fp_obj(imap.getAsset(s_), depth + 1)
        else:
            v = fp_root(s_, depth)
        memo[s_] = v
        return v

    def fp_val(v, depth):
        if v is None:
            return "null"
        if isinstance(v, (bool, int, float)) and not isinstance(v, str):
            return repr(v)
        c = v.getClass() if not isinstance(v, str) else None
        cn = str(c.getName()) if c is not None else "java.lang.String"
        if cn == "java.lang.String":
            v = str(v)
            return ("->" + fp_ref(v, depth)) if is_ref(v) else repr(v)
        if c.isArray():
            return "[" + ",".join(fp_val(ARR.get(v, i), depth) for i in range(ARR.getLength(v))) + "]"
        if c.isEnum() or cn.startswith("java.lang.") and not cn.startswith("java.lang.ref."):
            return str(v)
        if JClass("java.util.Map").class_.isInstance(v):
            return "{" + ",".join(sorted("%s:%s" % (fp_val(e.getKey(), depth), fp_val(e.getValue(), depth)) for e in v.entrySet())) + "}"
        if JClass("java.util.Collection").class_.isInstance(v):
            return "[" + ",".join(fp_val(x_, depth) for x_ in v) + "]"
        if cn.startswith("com.hypixel.") and depth < 80:
            return fp_obj(v, depth + 1)
        return cn

    def fp_obj(o, depth, root=False):
        """every instance field of the object and its super classes (the name fields left out), references by meaning"""
        parts = [str(o.getClass().getSimpleName())]
        c = o.getClass()
        while c is not None and str(c.getName()) != "java.lang.Object":
            for f in c.getDeclaredFields():
                fn = str(f.getName())
                if Mod.isStatic(f.getModifiers()) or fn in SKIP or (root and fn == "interactionIds") or str(f.getType().getName()).startswith("java.lang.ref."):
                    continue
                f.setAccessible(True)
                parts.append("%s=%s" % (fn, fp_val(f.get(o), depth)))
            c = c.getSuperclass()
        return "(" + ";".join(parts) + ")"
    fps, opsq = {}, {}
    for rid in ["Pickaxe_Attack", "Hatchet_Attack"]:
        try:
            fps[rid] = fp_root(rid, 0) if rmap.getAsset(rid) is not None else "missing"
        except Exception as e:
            fps[rid] = "fingerprint failed: %s" % str(e)[:300]
    tmp_roots = []
    for t in TOPS:
        tmp_roots.append(ROOTc("SkyyHarness_" + t, JArray(JString)([t])))
    AR.getAssetStore(ROOTc.class_).loadAssets("Test:Pack", jlist(tmp_roots))
    for rid in ["Pickaxe_Attack", "Hatchet_Attack"] + ["SkyyHarness_" + t for t in TOPS]:
        r = rmap.getAsset(rid)
        seq = []
        try:
            r.build()
            for i in range(int(r.getOperationMax())):
                op = r.getOperation(i)
                inner = op.getInnerOperation()
                if inner is not None and INTc.class_.isInstance(inner):
                    nm_ = str(inner.getId())
                    seq.append(str(inner.getClass().getSimpleName()) + ("(" + nm_ + ")" if nm_ in vnames else ""))
                else:
                    seq.append(str(op.getClass().getSimpleName()) + (":" + str(op) if "Jump" in str(op.getClass().getSimpleName()) else ""))
        except Exception as e:
            seq.append("build failed: %s" % str(e)[:300])
        opsq[rid] = seq
        if rid.startswith("SkyyHarness_"):
            try:
                fps[rid] = fp_ref(rid[len("SkyyHarness_"):], 0)
            except Exception as e:
                fps[rid] = "fingerprint failed: %s" % str(e)[:300]
    R["fp"], R["ops"] = fps, opsq
    # ---- E4 the validators (after E1-E3: the validators' loadContainedAssets puts inline children into the store)
    HLOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyTreesHarness")
    KNOWN = set(os.path.basename(n).rsplit(".", 1)[0] for n in list(az.namelist()) + list(jz.namelist()))

    def validate(cls, key, text):
        n0_ = len(records())
        st = AR.getAssetStore(cls.class_)
        ei = AEI(Paths.get(key + ".json"), ADT(cls.class_, key, None))
        try:
            o = st.getCodec().decodeJsonAsset(RJR.fromJsonString(text), ei)
        except Exception as e:
            return None, ["decode: " + str(e)[:300]], []
        prob, env = [], []
        uk = [str(x) for x in ei.getUnknownKeys()]
        if uk:
            prob.append("unknown keys %s" % uk)
        try:
            st.getCodec().validate(o, ei)
        except Exception as e:
            prob.append("validate threw %s" % str(e)[:300])
        vr = ei.getValidationResults()
        msgs = []
        try:
            if vr is not None:
                vr.logOrThrowValidatorExceptions(HLOG)
        except Exception as e:
            msgs.append(str(e))
        try:
            ei.getData().loadContainedAssets(False)
        except Exception as e:
            prob.append("contained assets: %s" % str(e)[:300])
        msgs += [m_ for lv, m_ in records()[n0_:]]
        for m_ in msgs:
            for ln in re.findall(r"FAIL: ([^\n]*)", m_):
                m2_ = re.search(r"'([^']+)'", ln)
                (env if (m2_ and m2_.group(1) in KNOWN and ("doesn't exist" in ln or "does not exist" in ln)) else prob).append(ln[:300])
        return o, prob, env
    neg = validate(INTc, "SkyyTreesHarness_OneParallel", json.dumps({"Type": "Simple", "RunTime": 0.1, "Next": {"Type": "Parallel", "Interactions": [{"Interactions": ["Block_Break"]}]}}))
    pos = validate(INTc, "SkyyTreesHarness_TwoParallel", json.dumps({"Type": "Simple", "RunTime": 0.1, "Next": {"Type": "Parallel", "Interactions": [{"Interactions": ["Block_Break"]}, {"Interactions": ["Block_Break"]}]}}))
    R["neg"] = [neg[0] is not None, neg[1][:2], pos[0] is not None, pos[1][:2]]
    val = {}
    for n in sorted(jnames) + rnames:
        cls = ROOTc if n.startswith(RDIR) else INTc
        o, p, e = validate(cls, os.path.basename(n)[:-5], jz.read(n).decode("utf-8"))
        val[n] = {"ok": o is not None, "prob": p, "env": sorted(set(e))}
    R["val"] = val
    json.dump(R, open(out, "w"), indent=1)
    os._exit(0)


# ================================================================================================ child: start twice on a copy of the live data
def run_start(jar, fake, live, out, tag):
    from jpype import JClass, JArray
    T = t33()
    T.H._jvm_start([], [fake])
    URL, URLCL, File, Paths = JClass("java.net.URL"), JClass("java.net.URLClassLoader"), JClass("java.io.File"), JClass("java.nio.file.Paths")
    sysl = JClass("java.lang.ClassLoader").getSystemClassLoader()
    T.H._stand_ins()

    def loader(j):
        urls = JArray(URL)(1)
        urls[0] = File(j).toURI().toURL()
        return URLCL(urls, sysl)

    def snap(d):
        o = {}
        for r, _ds, fs in os.walk(d):
            for f in fs:
                p = os.path.join(r, f)
                o[os.path.relpath(p, d).replace(os.sep, "/")] = open(p, "rb").read()
        return o
    base = os.path.join(SCRATCH, "start-" + tag, "mods", "Skyy_SkyyTrees")
    shutil.copytree(live, base)
    s0 = snap(os.path.dirname(base))
    res = {"starts": []}
    for i in range(2):
        ld = loader(jar)
        C = lambda n: JClass(PKG + n, loader=ld)
        b = Paths.get(base)
        C("TreeCfg").FILE = b.resolve("trees.properties")
        C("TreeStore").DIR = b.resolve("players")
        st = {"sum": str(C("TreeCfg").load()), "mig": str(C("TreeMig").run(b)), "m32": str(C("TreeMig32").run(b)), "m33": str(C("TreeMig33").run(b))}
        C("CfgPub").start(b.getParent(), None)
        st["on"] = bool(C("TreeCfg").CLASS_ON)
        s1 = snap(os.path.dirname(base))
        st["changed"] = sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k))
        # what a changed file holds (text files: the lines that differ), for the 0.3.3 / 0.3.4 comparison
        st["diff"] = dict((k, sorted(set((s1.get(k) or b"").decode("latin-1").splitlines()) ^ set((s0.get(k) or b"").decode("latin-1").splitlines()))[:20])
                          for k in st["changed"])
        res["starts"].append(st)
        s0 = s1
    json.dump(res, open(out, "w"), indent=1)
    os._exit(0)


def norm_start(r):
    """a start result with the version text and time stamps neutral (0.3.3 vs 0.3.4)"""
    t = json.dumps(r, sort_keys=True).replace("0.3.4", "0.3.X").replace("0.3.3", "0.3.X")
    return re.sub(r"\d{8}-\d{6}|\d{4}-\d\d-\d\d[ T]\d\d:\d\d(:\d\d)?", "<time>", t)


# ================================================================================================ main
def main():
    if "--load" in sys.argv:
        t33().run_load(arg("--load"), arg("--out"))
        return
    if "--engine" in sys.argv:
        run_engine(arg("--engine"), arg("--out"), arg("--mode"))
        return
    if "--mkfake" in sys.argv:
        t33().H.run_mkfake(arg("--mkfake"))
        return
    if "--start" in sys.argv:
        run_start(arg("--start"), arg("--fake"), arg("--live"), arg("--out"), arg("--tag"))
        return
    if "--audit" in sys.argv:
        t33().H.run_audit(arg("--audit"), arg("--fake"), arg("--out"))
        return
    if "--bytecode" in sys.argv:
        t33().H.run_bytecode(arg("--bytecode"), arg("--new"), arg("--out"))
        return
    for j in (JAR, PREV_JAR, JAR032):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first (without --deploy)" % j)
    root = os.path.join(TOOLS, "dev", "scratch").replace("\\", "/").lower().rstrip("/")
    here = SCRATCH.replace("\\", "/").lower().rstrip("/")
    if here == root or not here.startswith(root + "/"):
        sys.exit("--dir must be a folder INSIDE tools/dev/scratch/, not %s" % SCRATCH)
    if os.path.exists(SCRATCH) and os.listdir(SCRATCH):
        sys.exit("%s is not empty - pass an empty --dir" % SCRATCH)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    me = os.path.abspath(__file__)
    live_snap = dict((os.path.relpath(os.path.join(r, f), LIVE_DIR), open(os.path.join(r, f), "rb").read()) for r, _d, fs in os.walk(LIVE_DIR) for f in fs)

    def child(args_, out_):
        p = subprocess.run([sys.executable, me] + args_ + ["--out", out_, "--dir", SCRATCH], env=env, stderr=subprocess.PIPE, encoding="utf8", errors="replace")
        err = "".join(l + "\n" for l in (p.stderr or "").splitlines() if "Picked up JAVA_TOOL_OPTIONS" not in l and "WARNING" not in l)
        if p.returncode != 0 and err.strip():
            sys.stderr.write(err[-4000:])
        return p.returncode == 0 and os.path.isfile(out_)
    try:
        import skyybuild as SB
        az = zipfile.ZipFile(os.path.join(os.path.dirname(SB.SERVER_JAR), "..", "Assets.zip"))
        vanilla_ids = set(os.path.basename(n)[:-5] for n in az.namelist() if n.startswith("Server/") and n.endswith(".json"))
        vanilla_int = set(os.path.basename(n)[:-5] for n in az.namelist() if n.startswith(IDIR) and n.endswith(".json"))
        zp, zn = zipfile.ZipFile(PREV_JAR), zipfile.ZipFile(JAR)
        # ---- A
        for tag, j in (("new", JAR), ("prev", PREV_JAR)):
            o = os.path.join(SCRATCH, "load-%s.json" % tag)
            r = json.load(open(o)) if child(["--load", j], o) else {"classes": 0, "fails": ["child failed"]}
            check(not r["fails"] and r["classes"] > 30, "A: %s: %d classes load, verify and initialise %s" % (os.path.basename(j), r["classes"], r["fails"][:3]))
            print("A: %s: %d classes under -Xverify:all" % (os.path.basename(j), r["classes"]))
        # ---- F
        changed = section_f(zp, zn)
        bc = os.path.join(SCRATCH, "bytecode.json")
        p = subprocess.run([sys.executable, me, "--bytecode", PREV_JAR, "--new", JAR, "--out", bc, "--dir", SCRATCH], env=env, stderr=subprocess.DEVNULL)
        if p.returncode == 0 and os.path.isfile(bc):
            res = json.load(open(bc))
            for n, v in sorted(res.items()):
                print("F: %s: methods changed %s (constant-only: %s), new %s, gone %s" % (n.split("/")[-1][:-6], [m.split("(")[0] for m in v.get("changed", [])][:6],
                                                                                        v.get("const_only", "?"), v.get("new"), v.get("gone")))
                check(not v.get("new") and not v.get("gone") and not v.get("fields_new") and not v.get("fields_gone"),
                      "F: %s: no method / field added or removed" % n)
        # ---- J
        section_j(zp, zn, vanilla_ids, vanilla_int)
        # ---- E
        eng = {}
        for tag, j in (("new", JAR), ("prev", PREV_JAR)):
            o = os.path.join(SCRATCH, "engine-%s.json" % tag)
            ok = child(["--engine", j, "--mode", tag], o)
            check(ok, "E: the engine child ran (%s)" % tag)
            eng[tag] = json.load(open(o)) if ok else None
        if eng["new"] and eng["prev"]:
            a, b = eng["new"], eng["prev"]
            check(a["codecs"] > 60 and "Horizontal" in a["selectors"], "E: %d interaction types + %d selector types registered as InteractionModule.setup does" % (a["codecs"], len(a["selectors"])))
            check(a["load"] and a["root_load"] and b["load"] and b["root_load"], "E1: both jars' files load (interactions %s / %s, roots %s / %s)" % (a["load"], b["load"], a["root_load"], b["root_load"]))
            check(not a["severe"] and not b["severe"], "E1: no load failure: %s %s" % (a["severe"][:2], b["severe"][:2]))
            skyy_saw = [m for m in b["missing_int"] if m in ("Missing interaction **Skyy_Tree_Chop_Wood_Next_Next", "Missing interaction **Skyy_Tree_Chop_Wood_Next_Failed")]
            check(len(b["missing_int"]) > 50 and len(skyy_saw) == 2, "E1: 0.3.3 (control) logs the inline-step kind: %d 'Missing interaction ..Skyy_Tree..' lines incl. Skyy's 2 (%s)" % (len(b["missing_int"]), skyy_saw))
            check(a["missing_int"] == [], "E1: 0.3.4 logs NO 'Missing interaction' line for our steps: %s" % a["missing_int"][:4])
            ctl_ok = a["ctl_lines"] == ["Missing root interaction *SkyyHarness_TopParallel_Interactions_0", "Missing root interaction *SkyyHarness_TopParallel_Interactions_1"]
            check(ctl_ok and all(re.match(r"^Missing root interaction \*Skyy_Tree_Chop_N\w*$", m) for m in a["missing_root"]),
                  "E1: 'Missing root interaction' lines only of the TEST-BED kind (the inline roots of the vanilla Hatchet_Chop copy; the control "
                  "top-level Parallel - 14 vanilla files have that shape - logs the same here; 0 such lines in 71 live logs): new %d %s, control %s"
                  % (len(a["missing_root"]), a["missing_root"][:6], a["ctl_lines"]))
            check(len(a["missing_root"]) <= len(b["missing_root"]), "E1: no more test-bed root lines than 0.3.3 (%d vs %d)" % (len(a["missing_root"]), len(b["missing_root"])))
            print("E1: missing interaction lines 0.3.3 %d -> 0.3.4 %d; test-bed root lines 0.3.3 %d / 0.3.4 %d (control: %d); packets %d / %d"
                  % (len(b["missing_int"]), len(a["missing_int"]), len(b["missing_root"]), len(a["missing_root"]), len(a["ctl_lines"]), b["packets"], a["packets"]))
            check(a["ours"] == 173 and not a["placeholders"] and not b["placeholders"], "E2: 0.3.4: %d steps of ours in the store, placeholders left: %s / 0.3.3: %s"
                  % (a["ours"], a["placeholders"][:4], b["placeholders"][:4]))
            check(set(a["classes"]) == set(b["classes"]) and "SendMessageInteraction" not in a["classes"], "E2: the same interaction classes: %s" % a["classes"])
            for rid in sorted(a["ops"]):
                check(a["ops"][rid] == b["ops"].get(rid) and len(a["ops"][rid]) > 0 and not [x for x in a["ops"][rid] if "failed" in x],
                      "E3: %s compiles to the same %d ops in both jars" % (rid, len(a["ops"][rid])))
            for rid in sorted(a["fp"]):
                check(a["fp"][rid] == b["fp"].get(rid) and "fingerprint failed" not in a["fp"][rid] and "too-deep" not in a["fp"][rid] and len(a["fp"][rid]) > 20000,
                      "E3: %s: the name-free fingerprint of everything it reaches is the same in both jars (%d chars)" % (rid, len(a["fp"][rid])))
            fp = a["fp"].get("Hatchet_Attack", "")
            want = ["BlockConditionInteraction", "TriggerCooldownInteraction", "SelectInteraction", "ParallelInteraction", "ChainingInteraction",
                    "EffectConditionInteraction", "ReplaceInteraction", "vanilla:Block_Break", "vanilla:Hatchet_Attack", "vanilla:Hatchet_Chop_Damage"]
            check(not [w for w in want if w not in fp], "E3: the Hatchet_Attack fingerprint reaches the tier check, the reset, the chain, the swing copy (Parallel, "
                  "Selector, Replace) and the wood check: missing %s" % [w for w in want if w not in fp])
            cds = dict((r_, sorted(set(re.findall(r"InteractionCooldown;cooldownId=[^;]*;cooldown=([0-9.]+)", a["fp"][r_])))) for r_ in ("Hatchet_Attack", "Pickaxe_Attack"))
            check(len(cds["Hatchet_Attack"]) == 42 and len(cds["Pickaxe_Attack"]) == 40, "E3: the cooldowns reached: hatchet %d (the 0.35 reset + wood tiers 0-40), pickaxe %d (tiers 1-40)"
                  % (len(cds["Hatchet_Attack"]), len(cds["Pickaxe_Attack"])))
            print("E3: %d roots compiled + fingerprinted; Hatchet_Attack %d ops, fingerprint %d chars" % (len(a["ops"]), len(a["ops"]["Hatchet_Attack"]), len(fp)))
            check(a["neg"][0] is not None and any("Array size" in x or "size" in x.lower() for x in a["neg"][1]) and a["neg"][2] and not a["neg"][3],
                  "E4: NEGATIVE CONTROL: a one-entry Parallel fails the validator function, a two-entry one passes: %s" % a["neg"])
            bad = dict((n, v["prob"]) for n, v in a["val"].items() if not v["ok"] or v["prob"])
            check(len(a["val"]) == 175 and not bad, "E4: the engine validators pass on all %d interaction / root files of 0.3.4: %s" % (len(a["val"]), list(bad.items())[:3]))
            envs = sorted(set(x for v in a["val"].values() for x in v["env"]))
            envs_old = sorted(set(x for v in b["val"].values() for x in v["env"]))
            check(set(envs) <= set(envs_old), "E4: test-bed notes (names in Assets.zip the bare JVM has not loaded) are the same kind as 0.3.3's: new %s" % sorted(set(envs) - set(envs_old))[:3])
            print("E4: validators: %d files pass (0.3.3: %d files, problems %d); test-bed notes %d: %s" % (len(a["val"]), len(b["val"]),
                                                                                                          sum(1 for v in b["val"].values() if v["prob"]), len(envs), envs[:3]))
        # ---- S + Z
        fake = os.path.join(SCRATCH, "fake")
        p = subprocess.run([sys.executable, me, "--mkfake", fake, "--dir", SCRATCH], env=env, stderr=subprocess.DEVNULL)
        check(p.returncode == 0, "stand-in classes generated")
        st = {}
        for tag, j in (("new", JAR), ("prev", PREV_JAR)):
            o = os.path.join(SCRATCH, "start-%s.json" % tag)
            p = subprocess.run([sys.executable, me, "--start", j, "--fake", fake, "--live", LIVE_DIR, "--tag", tag, "--out", o, "--dir", SCRATCH], env=env, stderr=subprocess.PIPE, encoding="utf8", errors="replace")
            check(p.returncode == 0 and os.path.isfile(o), "S: the start child ran (%s) %s" % (tag, (p.stderr or "")[-600:] if p.returncode else ""))
            st[tag] = json.load(open(o)) if os.path.isfile(o) else None
        if st["new"] and st["prev"]:
            s1, s2 = st["new"]["starts"]
            check(s2["changed"] == [], "S: START TWICE (0.3.4): the 2nd start writes nothing: %s" % s2["changed"])
            check(norm_start(st["new"]) == norm_start(st["prev"]), "S: 0.3.4 changes exactly what 0.3.3 changes on the same copy (start 1: %s)" % s1["changed"][:6])
            check(not [k for k in s1["changed"] if k.startswith("mods/Skyy_SkyyTrees/players/") or k == "mods/Skyy_SkyyTrees/trees.properties"],
                  "S: start 1 on the live copy leaves trees.properties and every player file as they are: %s" % s1["changed"][:6])
            print("S: start 1 %s; start 2 %s; summary %s" % (s1["changed"][:6], s2["changed"], s1["sum"][:160]))
        au = os.path.join(SCRATCH, "audit.json")
        p = subprocess.run([sys.executable, me, "--audit", JAR, "--fake", fake, "--out", au, "--dir", SCRATCH], env=env, stderr=subprocess.DEVNULL)
        check(p.returncode == 0 and os.path.isfile(au), "Z: audit child ran")
        if os.path.isfile(au):
            z = json.load(open(au))
            check(not z["refused"] and z["refs"] > 10000 and z["control"], "Z: %d references in %d classes, refused %s; control refused %s" % (z["refs"], z["classes"], z["refused"][:3], bool(z["control"])))
            print("Z: %d references in %d classes, %d refused (control refused: %s)" % (z["refs"], z["classes"], len(z["refused"]), bool(z["control"])))
        # ---- H33: the 0.3.3 harness on the 0.3.4 jar next to its control run on the 0.3.3 jar
        if "--no33" not in sys.argv:
            h = {}
            for tag, j in (("new", JAR), ("prev", PREV_JAR)):
                d = os.path.join(SCRATCH, "h33-" + tag)
                p = subprocess.run([sys.executable, os.path.join(HERE, "test_skyytrees_0.3.3.py"), "--jar", j, "--prev", JAR032, "--dir", d, "--live", LIVE_DIR],
                                   env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf8", errors="replace")
                out_ = p.stdout or ""
                m = re.search(r"(\d+) checks passed, (\d+) failed", out_)
                h[tag] = {"passed": int(m.group(1)) if m else 0, "failed": [l.strip()[len("FAILED:"):].strip() for l in out_.splitlines() if l.strip().startswith("FAILED:")],
                          "fails": [l[5:].strip() for l in out_.splitlines() if l.startswith("FAIL ")]}
                open(os.path.join(SCRATCH, "h33-%s.log" % tag), "w", encoding="utf8").write(out_)
            nf = set(re.sub(r"0\.3\.[34]", "0.3.X", x) for x in h["new"]["failed"])
            pf = set(re.sub(r"0\.3\.[34]", "0.3.X", x) for x in h["prev"]["failed"])
            extra = sorted(nf - pf)
            # the jar-shape checks of the 0.3.3 harness's section E (they list the files 0.3.2 -> 0.3.3 added / changed)
            shape = [x for x in extra if x.startswith("E: added exactly TreeMig33") or x.startswith("E: changed classes")]
            # the control's own failures: its section M was written for a 0.3.2 live trees.properties - the live file was updated by the 0.3.3
            # deploy (marker skyytrees-0.3.3-paths), so the one-time append it expects has nothing left to do (environment, not the jar)
            env_m = sorted(x for x in pf if re.match(r"^M[: ]", x))
            check(h["prev"]["passed"] > 400000 and not [x for x in pf if x not in env_m] and "skyytrees-0.3.3-paths" in open(os.path.join(LIVE_DIR, "trees.properties"), encoding="latin-1").read(),
                  "H33 control: the 0.3.3 harness on the 0.3.3 jar: %d passed; it fails only its section M (the live file is no longer a 0.3.2 file): %s"
                  % (h["prev"]["passed"], [x for x in pf if x not in env_m][:3]))
            check(h["new"]["passed"] >= h["prev"]["passed"] - len(shape) and not [x for x in extra if x not in shape] and len(shape) == 2 and nf >= pf,
                  "H33: the 0.3.3 harness on the 0.3.4 jar: %d passed; beyond the control only its 2 jar-shape checks fail: %s (shape: %s)"
                  % (h["new"]["passed"], [x for x in extra if x not in shape][:4], [x[:90] for x in shape]))
            print("H33: 0.3.3 harness on 0.3.4: %d passed, %d failed (%d = jar shape, %d = the control's section-M environment lines); control on 0.3.3: %d passed, %d failed"
                  % (h["new"]["passed"], len(nf), len(shape), len(env_m), h["prev"]["passed"], len(pf)))
        live_after = dict((os.path.relpath(os.path.join(r, f), LIVE_DIR), open(os.path.join(r, f), "rb").read()) for r, _d, fs in os.walk(LIVE_DIR) for f in fs)
        check(live_after == live_snap, "the live Skyy_SkyyTrees folder is unchanged (read-only)")
    finally:
        if not KEEP:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyTrees %s vs %s: %d checks passed, %d failed" % (VERSION, PREV_VERSION, OKS[0], len(FAILS)))
    for f in FAILS[:60]:
        print("  FAILED:", f)
    print("SkyyTrees %s bare-JVM harness:" % VERSION, "PASS" if not FAILS else "FAIL")
    sys.exit(0 if not FAILS else 1)


if __name__ == "__main__":
    main()
