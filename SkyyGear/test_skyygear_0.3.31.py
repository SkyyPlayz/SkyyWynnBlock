"""Harness for SkyyGear 0.3.31 (tools/gear_0_3_31_patch.py header = our own Infinite Water Bucket)
    python tools/gear_0_3_31_patch.py && python SkyyGear/build_skyygear_0.3.31.py
    python SkyyGear/test_skyygear_0.3.31.py [--keep]          (S331 + H329 + H330 + H331 on one booted engine)
    python SkyyGear/test_skyygear_0.3.31.py --static [--keep]  (no jar)

  The 0.3.30 harness is loaded as a library (it loads 0.3.29's: the engine boot + H329 + H330, which still hold on this jar: 0.3.31 changes no
  band, ore, bag or migration behaviour); H331 runs right after them on the same booted engine.
  STATIC (--static)
       G  the patch run TWICE in a scratch tree -> byte-identical, = SkyyGear/build_skyygear_0.3.31.py, compiles, line endings kept
       A  anchors: VERSION; no new system / command; exactly 3 new classes; the craft gate sits in GearCraftPreSys before the lifelong veto;
          GearBucket before its callers; the 4 Server Setup rows + the fresh-file block; the jar item list names the bucket
  S331 the jar 0.3.30 -> 0.3.31: added = the bucket item + its interaction + its icon + the 3 classes; nothing removed; only class files, the
       manifest and server.lang change otherwise; the item JSON (no durability, PlaceFluid step by our type, the recipe), the tagged lang line
  H331 (the h319 child) - real code:
       A  the item in the engine's Item store (packet, MaxStack 1, no durability); SkyyGear_Bucket_Place decodes as a GearBucketPlace
          (vanilla's keys: Water_Source, RemoveItemInHand false); the Server Setup defaults (on, 1 s, 0, 4)
       B  GearBucket.canT / tierWhy: Crude 1, Iron 2, Thorium 4, Lead 5, none 0; Iron refused (names T4 Thorium), Thorium / Lead / Mithril allowed
       C  craftWhy on a real profile: the registry's can (Iron = refused, Thorium = allowed, put back after); bucket.enabled off = refused;
          bucket.canTier 0 = allowed; part.can off = the Farming level path
       D  allow / placed with the clock seam: cooldown 1 s (silent ""), per-minute cap 3 (a red sentence, the window resets), cooldown 0, off
       E  the REAL GearBucketPlace.interactWithBlock (seams CTX / SUPER): placed once (vanilla's placement ran, counted); a click inside the
          cooldown fails the interaction and never reaches vanilla; a failed vanilla placement is not counted; bucket.enabled off = failed
Scratch: tools/dev/scratch/iwb/h331 (deleted at the end unless --keep). Exit code 1 on any failure (--static: 0 = PASS).
"""
import os, sys, shutil, zipfile, json, subprocess, atexit

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
STATIC = "--static" in sys.argv
if STATIC:
    sys.dont_write_bytecode = True


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


VERSION = "0.3.31"
V330 = "0.3.30"
SCR_BASE = os.path.join(TOOLS, "dev", "scratch", "iwb", "h331")
SCR_ROOT = os.path.abspath(arg("--root", os.path.join(SCR_BASE, "gear")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
J330 = os.path.abspath(os.path.join(HERE, "SkyyGear-%s.jar" % V330))                       # read only
PKG = "com.skyy.gear."
PATCH = os.path.join(TOOLS, "gear_0_3_31_patch.py")
GEN = os.path.join(HERE, "build_skyygear_0.3.31.py")
GEN330 = os.path.join(HERE, "build_skyygear_0.3.30.py")
LIVE_DIR = os.path.join(SCR_BASE, "live")
IWB = "Tool_SkyyInfiniteWaterBucket"

if not STATIC:
    _H330 = os.path.join(HERE, "test_skyygear_0.3.30.py")
    _T330 = open(_H330, encoding="utf-8").read()
    _T330 = _T330[:_T330.rindex('if __name__ == "__main__":')]
    _argv = sys.argv
    sys.argv = [_H330, "--jar", JAR, "--root", SCR_ROOT, "--dir", SCRATCH] + [a for a in _argv[1:] if a in ("--keep", "--h319")] + \
        (["--out", arg("--out")] if arg("--out") else [])
    H330 = {"__name__": "skyygear_h330", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
    exec(compile(_T330, _H330 + " (library, 0.3.31)", "exec"), H330)
    sys.argv = _argv
    H329 = H330["H329"]
    H328 = H329["H328"]
    H319, H320, H316 = H329["H319"], H329["H320"], H329["H316"]
    for _h in (H330, H329, H328, H328["H327"], H328["H326"], H328["H325"], H320, H319):
        _h["VERSION"] = VERSION
    FAILS, OKS = H316["FAILS"], H316["OKS"]
    # every engine boot also registers SkyyGearBucket (what the plugin's setup() does in the game; without it the jar's SkyyGear_Bucket_Place
    # is an unknown Type in a bare boot) - the 0.3.14 wrapper (SkyyGearHarvest, inside it 0.3.12's SkyyGearCan) runs inside
    _HB = H316["H"]
    _BOOT_314 = _HB["engine_boot"]

    def engine_boot_331(K):
        from jpype import JClass
        try:
            INTc = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.Interaction")
            GBP = JClass(PKG + "GearBucketPlace")
            INTc.CODEC.register("SkyyGearBucket", GBP.class_, GBP.codec())
            JClass(PKG + "GearBucket").REG = True
            JClass(PKG + "GearBucket").REG_WHY = "registered (harness, like setup())"
        except Exception as e:
            K.notes.append("engine_boot_331: the SkyyGearBucket type could not be registered: %s" % str(e)[:200])
        return _BOOT_314(K)
    for _d in (_HB, H316["H35"].get("H"), H316["H36"].get("H"), H316["H37"].get("H"), H316["H38"].get("H")):
        if isinstance(_d, dict) and _d.get("engine_boot") is _BOOT_314:
            _d["engine_boot"] = engine_boot_331
else:
    FAILS, OKS = [], [0]


def check(cond, what):
    if STATIC:
        if cond:
            OKS[0] += 1
        else:
            FAILS.append(what)
            print("FAIL", what)
        return
    H316["check"](cond, what)


def entries(j):
    z = zipfile.ZipFile(j)
    return dict((n, z.read(n)) for n in z.namelist())


# ====================================================================================================== S331 (the parent, no engine)
def run_assets331():
    ea, eb = entries(J330), entries(JAR)
    add, gone = sorted(set(eb) - set(ea)), sorted(set(ea) - set(eb))
    want = sorted(["Server/Item/Items/SkyyGear/%s.json" % IWB, "Server/Item/Interactions/SkyyGear/Bucket/SkyyGear_Bucket_Place.json",
                   "Common/Icons/ItemsGenerated/%s.png" % IWB] + ["com/skyy/gear/%s.class" % c for c in ("GearBucket", "GearBucketPlace", "GearBucketSup")])
    check(add == want and not gone, "S331: added = the bucket item, interaction, icon + 3 classes; nothing removed: + %s - %s" % (add, gone))
    diff = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n])
    other = [n for n in diff if not n.endswith(".class") and n not in ("manifest.json", "Server/Languages/en-US/server.lang")]
    check(not other, "S331: only class files, the manifest and server.lang change (%d changed): other %s" % (len(diff), other[:6]))
    it = json.loads(eb.get("Server/Item/Items/SkyyGear/%s.json" % IWB, b"{}").decode("utf-8"))
    ia = json.loads(eb.get("Server/Item/Interactions/SkyyGear/Bucket/SkyyGear_Bucket_Place.json", b"{}").decode("utf-8"))
    rc = it.get("Recipe") or {}
    check("MaxDurability" not in it and "Consumable" not in it and it.get("MaxStack") == 1 and it.get("Quality") == "Legendary"
          and it.get("Interactions") == {"Secondary": {"Interactions": ["SkyyGear_Bucket_Place"]}}
          and it.get("BlockType", {}).get("CustomModel") == "Blocks/Decorative_Sets/Village/Bucket_Full.blockymodel",
          "S331: the item = no durability, never consumed, stack 1, Legendary, Secondary = our interaction, vanilla's filled-bucket model by path")
    check(ia.get("Type") == "SkyyGearBucket" and ia.get("FluidToPlace") == "Water_Source" and ia.get("RemoveItemInHand") is False and "Next" not in ia,
          "S331: the interaction = type SkyyGearBucket, Water_Source, RemoveItemInHand false, no durability / BrokenItem step: %s" % ia)
    check([(i["ItemId"], i["Quantity"]) for i in rc.get("Input", [])] == [("Container_Bucket", 4), ("Ingredient_Bar_Thorium", 10), ("Skyy_Ench_Cauliflower", 2)]
          and rc.get("BenchRequirement") == [{"Id": "Farmingbench", "Type": "Crafting", "Categories": ["Farming"], "RequiredTierLevel": 3}],
          "S331: the recipe (4 buckets, 10 Thorium bars, 2 Enchanted Cauliflower at Farmingbench tier 3): %s" % rc)
    lb = eb["Server/Languages/en-US/server.lang"].decode("utf-8").split("\n")
    la = ea["Server/Languages/en-US/server.lang"].decode("utf-8").split("\n")
    new = [x for x in lb if x not in la]
    check(len(new) == 2 and new[0] == "items.%s.name = Infinite Water Bucket" % IWB and new[1].startswith("items.%s.description = T4 Thorium - <color is=" % IWB)
          and all(x in lb for x in la), "S331: server.lang = the old lines + the name + the tagged description: %s" % new)
    for c in ("GearBucket", "GearBucketPlace", "GearBucketSup"):
        b_ = eb.get("com/skyy/gear/%s.class" % c, b"")
        check(b_[:4] == b"\xca\xfe\xba\xbe", "S331: %s.class is a class file" % c)


# ====================================================================================================== H331 (the h319 child, real code)
def _h331(L, K):
    from jpype import JClass, JString, JInt, JLong, JObject, JBoolean, JImplements, JOverride
    P = lambda n: JClass(PKG + n)
    Cfg, apply, ITEM, jf, Gear = L["Cfg"], L["apply"], L["ITEM"], L["jf"], L["Gear"]
    U1, PR1 = L["U1"], L["PR1"]
    LL, Bk, Can, GBP = P("GearLL"), P("GearBucket"), P("GearCan"), P("GearBucketPlace")
    Props, SR, UUID = JClass("java.util.Properties"), JClass("java.io.StringReader"), JClass("java.util.UUID")
    E = L.get("E") or {}

    def kc(cond, what):
        K.check(bool(cond), "H331 " + what)
    apply()
    # ============================================================== A: assets + defaults
    it = ITEM.getAssetMap().getAsset(IWB)
    okp = None
    if it is not None:
        try:
            it.toPacket()
            okp = (int(it.getMaxStack()), float(it.getMaxDurability()))
        except Exception as e:
            okp = str(e)[:160]
    kc(it is not None and okp == (1, 0.0), "A: the bucket is in the Item store, makes its packet, MaxStack 1, no durability: %s" % (okp,))
    AR = E.get("AR") if hasattr(E, "get") else None
    if AR is not None:
        INTc = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.Interaction")
        PF = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.client.PlaceFluidInteraction")
        ist = AR.getAssetStore(INTc.class_)
        ia = ist.getAssetMap().getAsset("SkyyGear_Bucket_Place") if ist is not None else None
        kc(ia is not None and str(ia.getClass().getName()) == PKG + "GearBucketPlace" and str(jf(PF, "fluidKey").get(ia)) == "Water_Source"
           and not bool(jf(PF, "removeItemInHand").getBoolean(ia)),
           "A: SkyyGear_Bucket_Place decodes as a GearBucketPlace (Water_Source, RemoveItemInHand false): %s" % (None if ia is None else ia.getClass().getName()))
    else:
        K.notes.append("H331 A: no asset registry handle (E['AR']) - the interaction decode was not checked")
    fresh = str(Cfg.defaultsText())
    pf = Props()
    pf.load(SR(fresh))
    kc([str(pf.getProperty(k)) for k in ("bucket.enabled", "bucket.cooldownSec", "bucket.maxPerMinute", "bucket.canTier")] == ["true", "1", "0", "4"]
       and bool(Cfg.BUCKET_ON) and float(Cfg.BUCKET_CD) == 1.0 and int(Cfg.BUCKET_PM) == 0 and int(Cfg.BUCKET_TIER) == 4,
       "A: the fresh file + GearCfg: bucket.enabled true, cooldownSec 1, maxPerMinute 0, canTier 4")
    kc(str(Bk.ID) == IWB and str(Bk.statusText()).startswith("Infinite Water Bucket on"), "A: GearBucket.ID + statusText: %s" % Bk.statusText())
    # ============================================================== B: the tier words
    ts = dict((i, int(Bk.canT(JString(i)))) for i in ("Tool_WaterCan_Crude", "Tool_WaterCan_Iron", "Tool_WaterCan_Thorium", "Tool_WaterCan_Lead_SkyWynn", "Tool_WaterCan_Mithril"))
    kc(ts == {"Tool_WaterCan_Crude": 1, "Tool_WaterCan_Iron": 2, "Tool_WaterCan_Thorium": 4, "Tool_WaterCan_Lead_SkyWynn": 5, "Tool_WaterCan_Mithril": 13}
       and int(Bk.canT(None)) == 0, "B: canT = the ladder tier: %s" % ts)
    wi = Bk.tierWhy(JString("Tool_WaterCan_Iron"), JInt(4))
    wn = Bk.tierWhy(None, JInt(4))
    kc(wi is not None and "T4 Thorium watering can" in str(wi) and "yours: T2 Iron" in str(wi) and wn is not None and "yours: none" in str(wn)
       and Bk.tierWhy(JString("Tool_WaterCan_Thorium"), JInt(4)) is None and Bk.tierWhy(JString("Tool_WaterCan_Lead_SkyWynn"), JInt(4)) is None
       and Bk.tierWhy(JString("Tool_WaterCan_Crude"), JInt(0)) is None, "B: Iron refused (%s), no can refused, Thorium / Lead allowed, tier 0 = no gate" % wi)
    # ============================================================== C: craftWhy on a real profile
    pk = Gear.pkey(U1)
    REG = LL.reg(pk)
    key = str(LL.KIND[int(LL.CAN)]) + ".id"
    had = REG.getProperty(key)
    try:
        REG.setProperty(key, "Tool_WaterCan_Iron")
        c1 = Bk.craftWhy(U1)
        REG.setProperty(key, "Tool_WaterCan_Thorium")
        c2 = Bk.craftWhy(U1)
        apply(bucket__enabled="false")
        c3 = Bk.craftWhy(U1)
        apply(bucket__canTier="0")
        REG.setProperty(key, "Tool_WaterCan_Iron")
        c4 = Bk.craftWhy(U1)
        apply(part__can="false")
        c5 = Bk.craftWhy(U1)
        h = int(P("GearGate").have(U1, JString(str(LL.KSKILL[int(LL.CAN)]))))
    finally:
        if had is None:
            REG.remove(key)
        else:
            REG.setProperty(key, had)
        apply()
    kc(c1 is not None and "T4 Thorium" in str(c1) and c2 is None and c3 is not None and "switched off" in str(c3) and c4 is None,
       "C: the registry's can: Iron refused (%s), Thorium allowed; bucket.enabled off refused; bucket.canTier 0 allowed" % c1)
    kc((c5 is None) == (h == -2 or h >= 20) and (c5 is None or "Farming 20" in str(c5)),
       "C: part.can off = the Farming level path (Farming %d -> %s)" % (h, c5))
    # ============================================================== D: allow / placed with the clock
    u = UUID.randomUUID()
    apply(bucket__cooldownSec="1", bucket__maxPerMinute="3")
    seq = []
    for t, place in ((1000, True), (1500, False), (2000, True), (3000, True), (4500, False), (61001, True)):
        w = Bk.allow(u, JLong(t))
        seq.append(None if w is None else str(w))
        if w is None and place:
            Bk.placed(u, JLong(t))
    kc(seq[0] is None and seq[1] == "" and seq[2] is None and seq[3] is None and seq[4] is not None and "3 water sources a minute" in seq[4]
       and seq[5] is None, "D: cooldown 1 s silent, the 4th source in a minute refused with a sentence, a new minute opens: %s" % seq)
    apply(bucket__cooldownSec="0", bucket__maxPerMinute="0")
    w0 = Bk.allow(u, JLong(61002))
    apply(bucket__enabled="false")
    w1 = Bk.allow(u, JLong(99999))
    apply()
    Bk.forget(u)
    kc(w0 is None and w1 is not None and "switched off" in str(w1) and Bk.LAST.get(u) is None and Bk.allow(None, JLong(5)) is None,
       "D: cooldown 0 + no cap = every click; off = refused; forget drops the memory; no player = allowed")
    # ============================================================== E: the real interactWithBlock
    ST = {"failed": False, "super": [], "superFail": False}

    @JImplements("java.util.function.Function")
    class CtxFn(object):
        @JOverride
        def apply(self, o):
            op = str(o[0])
            if op == "pr":
                return PR1
            if op == "fail":
                ST["failed"] = True
                return None
            if op == "failed":
                return JBoolean(ST["failed"])
            return None

    @JImplements("java.util.function.Function")
    class SuperFn(object):
        @JOverride
        def apply(self, o):
            ST["super"].append(o[0])
            if ST["superFail"]:
                ST["failed"] = True
            return None
    oc, os_ = Can.CTX, Bk.SUPER
    Can.CTX = CtxFn()
    Bk.SUPER = SuperFn()
    Bk.forget(PR1.getUuid())
    m = [x for x in GBP.class_.getDeclaredMethods() if str(x.getName()) == "interactWithBlock"][0]
    m.setAccessible(True)
    inst = GBP()
    V3 = JClass("org.joml.Vector3i")
    n0 = int(Bk.N[0])

    def click(t):
        ST["failed"] = False
        Bk.CLOCK = JLong(t)
        m.invoke(inst, None, None, None, None, None, V3(1, 2, 3), None)
        return ST["failed"]
    res = []
    try:
        apply()
        res.append((click(10000), len(ST["super"])))          # placed
        res.append((click(10400), len(ST["super"])))          # cooldown: failed, vanilla not run
        ST["superFail"] = True
        res.append((click(12000), len(ST["super"])))          # vanilla failed (e.g. placement off) -> not counted
        ST["superFail"] = False
        res.append((click(12100), len(ST["super"])))          # not counted above, so no cooldown: placed
        apply(bucket__enabled="false")
        res.append((click(20000), len(ST["super"])))          # off: failed
    finally:
        apply()
        Can.CTX, Bk.SUPER, Bk.CLOCK = oc, os_, JLong(-1)
        Bk.forget(PR1.getUuid())
    kc(res == [(False, 1), (True, 1), (True, 2), (False, 3), (True, 3)] and int(Bk.N[0]) - n0 == 2,
       "E: the real click - placed, cooldown refused before vanilla, a failed vanilla placement uncounted, placed again, off refused: %s (placed +%d)"
       % (res, int(Bk.N[0]) - n0))
    kc(bool(Bk.REG), "E: SkyyGearBucket registered (the harness boot, the way setup() does): %s" % Bk.REG_WHY)
    print("  note (h331): A-E ran")


if not STATIC:
    _H330_PHASE = H319["_h319"]          # the 0.3.30 lib's wrapper (H329 + H330)

    def _h319_h331(L, K):
        _H330_PHASE(L, K)
        try:
            _h331(L, K)
        except Exception:
            import traceback
            traceback.print_exc()
            K.check(False, "H331: the phase raised: %s" % traceback.format_exc()[-1800:])
    H319["_h319"] = _h319_h331


# ====================================================================================================== STATIC (no jars)
def run_static():
    base = os.path.join(SCR_BASE, "static")
    shutil.rmtree(base, ignore_errors=True)
    outs = []
    try:
        for k in range(2):
            r = os.path.join(base, "run%d" % k)
            os.makedirs(os.path.join(r, "tools"))
            os.makedirs(os.path.join(r, "SkyyGear"))
            shutil.copyfile(PATCH, os.path.join(r, "tools", os.path.basename(PATCH)))
            shutil.copyfile(os.path.join(TOOLS, "deploy_set.py"), os.path.join(r, "tools", "deploy_set.py"))
            shutil.copyfile(GEN330, os.path.join(r, "SkyyGear", os.path.basename(GEN330)))
            p = os.path.join(r, "tools", os.path.basename(PATCH))
            pr = subprocess.run([sys.executable, "-B", "-c",
                                 "import sys\nsys.dont_write_bytecode = True\np = sys.argv[1]\n"
                                 "g = {'__name__': '__main__', '__file__': p}\nexec(compile(open(p, encoding='utf8').read(), p, 'exec'), g)\n", p],
                                capture_output=True, text=True)
            check(pr.returncode == 0, "G: the patch runs in a scratch tree (run %d): %s" % (k, (pr.stderr or "")[-600:]))
            f = os.path.join(r, "SkyyGear", "build_skyygear_0.3.31.py")
            outs.append(open(f, "rb").read() if os.path.isfile(f) else b"")
        check(outs[0] and outs[0] == outs[1], "G: two runs give byte-identical scripts (deterministic)")
        if os.path.isfile(GEN):
            check(outs[0] == open(GEN, "rb").read(), "G: = SkyyGear/build_skyygear_0.3.31.py (the committed file is the patch's output)")
        src = open(GEN330, "rb").read()
        check((b"\r\n" in src) == (b"\r\n" in outs[0]), "G: the source's line endings are kept")
        s = outs[0].decode("utf8").replace("\r\n", "\n")
        try:
            compile(s, "build_skyygear_0.3.31.py", "exec")
            check(True, "G")
        except SyntaxError as e:
            check(False, "G: the generated script compiles: %s" % e)
        s0 = src.decode("utf8").replace("\r\n", "\n")
        check('VERSION = "0.3.31"\n' in s and "GENERATED by tools/gear_0_3_31_patch.py" in s, "A: VERSION 0.3.31 + the GENERATED header")
        check(s.count("registerSystem(") == s0.count("registerSystem(") and s.count("registerCommand(") == s0.count("registerCommand(")
              and s.count(' = mk("') == s0.count(' = mk("') + 3, "A: no new system or command; 3 new classes")
        i = s.index
        g = s[i('event_system(gcrp, "GearCraftPreSys"'):]
        g = g[:g.index('""")')]
        check(0 <= g.index("id0.equals(@PKG@.GearBucket.ID)") < g.index("@PKG@.GearLL.noCraft(id0)") and "e.setCancelled(true);" in g[g.index("GearBucket.craftWhy("):g.index("@PKG@.GearLL.noCraft(id0)")]
              and "@GM@.Creative" in g[g.index("id0.equals(@PKG@.GearBucket.ID)"):g.index("GearBucket.craftWhy(")],
              "A: the bucket gate sits in GearCraftPreSys before the lifelong veto, cancels the Pre event, Creative skips it")
        check(i('gbk = mk("GearBucket")') < i('event_system(gcrp, "GearCraftPreSys"') and i('gbk = mk("GearBucket")') < i("@PKG@.GearBucket.forget(u);")
              and i("public static boolean failed(@ICTX@ ctx) {") < i('gbp = mk("GearBucketPlace"'), "A: GearBucket / GearBucketPlace placed before their callers")
        for row in ('("bucket.enabled", "Infinite Water Bucket", "lifelong", "bool", "true"', '("bucket.cooldownSec", "Infinite bucket cooldown", "lifelong", "dec", "1", "0", "60"',
                    '("bucket.maxPerMinute", "Infinite bucket sources per minute", "lifelong", "int", "0", "0", "600"',
                    '("bucket.canTier", "Infinite bucket: watering can tier", "lifelong", "int", "4", "0", "16"'):
            check(s.count(row) == 1, "A: the Server Setup row %s" % row[:40])
        check('L += ["", G331_HEAD]' in s and 'register("SkyyGearBucket", @PKG@.GearBucketPlace.class' in s and "list(IWB_ITEMS)), \"SkyyGear 0.3.31" in s,
              "A: the fresh-file block, the type registration in setup(), the jar item list")
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(base, ignore_errors=True)
    print("STATIC %s: %d ok, %d failed" % ("PASS" if not FAILS else "FAIL", OKS[0], len(FAILS)))
    return 0 if not FAILS else 1


# ====================================================================================================== main
def _live_copy():
    """a scratch COPY of the test world's config.properties (UserData is read only) for the H329 / H330 live checks"""
    try:
        import deploy_set
        w = deploy_set.WORLD
    except Exception:
        w = "NewBetaTest"
    src = os.path.join(os.environ.get("APPDATA", ""), "Hytale", "UserData", "Saves", w, "mods", "Skyy_SkyyGear", "config.properties")
    if not os.path.isfile(src):
        print("  note: no live config at %s - H329 / H330 L skipped" % src)
        return
    os.makedirs(LIVE_DIR, exist_ok=True)
    dst = os.path.join(LIVE_DIR, "config.properties")
    shutil.copyfile(src, dst)
    os.environ["SKYY_G330_LIVE"] = dst
    os.environ["SKYY_G329_LIVE"] = dst


def main():
    if STATIC:
        sys.exit(run_static())
    if "--h319" in sys.argv:
        H319["run_h319"](arg("--out"))
        return
    if any(a.startswith("--") and a not in ("--keep", "--dir", "--jar", "--root", "--out", "--only") for a in sys.argv[1:]):
        H320["main"]()          # an older child flag (--mkfake ...) - the chain dispatches it; never the full run again
        return
    assert os.path.isfile(J330) and os.path.isfile(JAR), (J330, JAR)
    if "--keep" not in sys.argv:
        atexit.register(lambda: shutil.rmtree(SCR_BASE, ignore_errors=True))
    run_assets331()
    _live_copy()
    H320["run_fallback"](lambda x: x == "h319", [])


if __name__ == "__main__":
    main()
