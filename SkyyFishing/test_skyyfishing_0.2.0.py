"""Harness for SkyyFishing 0.2.0 (Fishing stage 2, Builder A: research/cloud/Fishing-Stage2-Build.md section 10; tools/fishing_0_2_0_patch.py).
Build first: python tools/fishing_0_2_0_patch.py && python SkyyFishing/build_skyyfishing_0.2.0.py

    python SkyyFishing/test_skyyfishing_0.2.0.py [--dir <folder inside tools/dev/scratch/>] [--keep]

  A / C / AA  verify (-Xverify:all), class compare 0.1.12 -> 0.2.0 (exactly the planned members; the non-class entries: the new / re-tinted
              art + lang + item files listed, no file removed, the Zone 1 fish JSON and the T0-T4 rod art byte-identical), engine-access audit
  LOGIC  H2 zone tables + junk sums, H3 the 12 % length rule on all 27, H4 income (Z2 Thorium 35,135 / Z3 Azurvane 254,460 +-1 %), H5 every
         rod T3-T6 opens a species or a full-size ceiling, H6 zone pick on a stand-in mob:fn:levelAt (15 -> 1, 25 -> 2, 45 -> 3, 70 -> 3,
         none -> fish.zone.default, broken tops -> defaults + WARN once), H7 season / time lean + Zone 3 winter bite (FishCore.roll), H8 the
         roll never gives a fish heavier than the rod or from another zone (10,000 seeded rolls per rod x zone), H9 recipes (tier-sorted, one
         per output, the tier below consumed, no bamboo / coin, the zone fish gates, the alloy rule both ways, real crafts on a real
         container incl. the lifelong pole's SkyyGear document), H10 tier tags (lang + rod / fish tooltip lines, old rods redrawn), H11 saved
         data (a 0.1.12 players file loads 0 / 0, round trip, fishing:fn:pond = pond + dune + frost), H12 a 0.1.12 config loads every new row
         at its default with no line rewritten, H13 37 tackle models + 10 part III icons, H14 zone prices + Lost Property by zone
  SEED   FishZ2Seed.plan / run (PROJECT-RULES 4): the 6 tables appended once, CRLF kept, a family already there left alone, the marker once,
         History copy + one change-log row per entry, start 2 nothing, a fresh file never touched, no file nothing; FishCfg.load then reads them
  LIVE   FishP3Mig + FishZ2Seed + FishCfg.load + FishStore on a scratch COPY of the live Skyy_SkyyFishing (NewBetaTest), twice
Not testable without the game (UNVERIFIED): mob:fn:levelAt in the zone world, Dynamic Seasons' live answer, the client look of the new items.
Exit code 1 on any failure.
"""
import os, sys, json, re, zipfile, importlib.util, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import tier_tags as TT

VERSION = "0.2.0"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "fish2", "h020")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyFishing-%s.jar" % VERSION)]
_spec = importlib.util.spec_from_file_location("test_skyyfishing_0_1_9", os.path.join(HERE, "test_skyyfishing_0.1.9.py"))
T19 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T19)
T15 = T19.T15
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyFishing-0.1.12.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.fishing."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyFishing")
ADDED = ["FishZone", "FishZ2Seed"]
EXPECT = {          # the members 0.2.0 changes on purpose (reviewed: zones, tags, recipes, counts, admin texts, the kit's new rows / tables)
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'FishAdminArg2Cmd': ['~c '],
    'FishAdminArgCmd': ['~c '],
    'FishAdminCmd': ['~c '],
    'FishBench': ['+f STICK_ID', '+m countsLine', '+m gateShort', '+m inEnd', '+m inId', '+m inQ', '+m sticks', '~<clinit>', '~m craft', '~m gate', '~m gateText', '~m lockTag', '~m needText', '~m priceG', '~m priceOf', '~m state'],
    'FishCfg': ['+f DAWN_HI', '+f DAWN_LO', '+f DAWN_TEXT', '+f DUNE', '+f DUNE_TEXT', '+f DUSK_HI', '+f DUSK_LO', '+f DUSK_TEXT', '+f FROST', '+f FROST_TEXT', '+f JUNK2', '+f JUNK2_W', '+f JUNK3', '+f JUNK3_W', '+f PART_C', '+f PRICE_KG2', '+f PRICE_KG3', '+f REEL_P_3', '+f REEL_P_4', '+f REEL_P_5', '+f REEL_P_6', '+f SEASON_IN', '+f SEASON_ON', '+f SEASON_OUT', '+f SP_SEAS', '+f SP_TIME', '+f STK', '+f STK_TEXT', '+f TIME_IN', '+f TIME_ON', '+f TIME_OUT', '+f TZM', '+f TZM_TEXT', '+f Z3_WINTER', '+f ZONE_DEF', '+f ZONE_MAX', '+f ZONE_TEXT', '+f ZTOPS', '+m counts8', '+m junkIds', '+m junkOf', '+m junkW', '+m maskOf', '+m multsOf', '+m priceKg', '+m rising', '+m spPre', '+m sticks8', '+m tiersOf', '+m tzm', '+m whenOf', '~<clinit>', '~m applyAll', '~m applyScalars', '~m applyTables', '~m derive', '~m partValue', '~m seed'],
    'FishCmds': ['~m admin', '~m status'],
    'FishCore': ['~m cast', '~m land', '~m roll'],
    'FishData': ['+f dune', '+f frost'],
    'FishDefs': ['+f JUNK2', '+f JUNK2_W', '+f JUNK3', '+f JUNK3_W', '+f PART_V2', '+f ROD_TAG', '+f R_COLL2', '+f R_COLLT2', '+f R_FZ', '+f SEASONS', '+f SP_SEAS0', '+f SP_TAG', '+f SP_TIME0', '+f SP_ZONE', '+f TIMES', '+f TR_ENCH', '+f TR_ENCH_ROW', '+f TR_SWAP2', '+f TR_SWAP3', '+f TR_SWAP_FROM', '+f TZM0', '+f ZONES', '+f ZONE_COLL', '+f ZONE_SHORT', '+f ZONE_TOPS0', '+m rodTag', '+m zoneOf', '~<clinit>'],
    'FishPage': ['~m build'],
    'FishQuestFn': ['~m apply', '~m starterG'],
    'FishRig': ['+f TIP_DIM', '+f TIP_GOOD', '+f TIP_NAME', '+m tipLines', '~m makeFish', '~m rodLines', '~m stale', '~m starter', '~m withRigG'],
    'FishState': ['+f season', '+f tod', '+f zone', '~c '],
    'FishStore': ['+m count', '+m setCount', '+m total', '~<clinit>', '~m fill', '~m heal', '~m onCatch', '~m text'],
    'SkyyFishingPlugin': ['~m setup'],
}
U1S = "00000000-0000-4000-8000-0000000020f2"
# catalog max lengths (cm) for H3 (Fish-Species-Catalog 3.1 + Fishing-Stage2-Build 3.1)
MAXCM = {"OverdueMinnow": 35, "Bluegill": 46, "RustbackTrout": 79, "QueuePerch": 61, "MisfiledCarp": 86, "StampedCatfish": 110, "MirebridgeEel": 100,
         "PonderingPike": 131, "GoldenKoi": 79, "Goldfish": 44, "OasisCarp": 83, "Sandskipper": 74, "DunePiranha": 82, "MirageEel": 133,
         "TarPitGudgeon": 100, "LostLuggageGrouper": 136, "MirageSturgeon": 162, "Sandsalmon": 117, "FrostCod": 114, "WhisperChar": 100,
         "SnowmeltTrout": 106, "IceboundSalmon": 134, "PermitLamprey": 159, "GlassPike": 182, "WhisperSturgeon": 188, "BlizzardHalibut": 140,
         "SleeperAisle9": 188}


# ------------------------------------------------------------------------------------------------ C: the class compare with this round's assets
def run_compare2(out, jar, old_jar, pkg, expect, added, removed=()):
    """harness_kit.run_compare, but the non-class entries may change (new items / art / lang): checked here instead of 'only manifest.json'"""
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.JAVASSIST], verify=False)
    CPc = JClass("javassist.ClassPool")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def pool_of(j):
        p_ = CPc(False)
        p_.appendSystemPath()
        p_.appendClassPath(B.SERVER_JAR)
        p_.appendClassPath(j)
        return p_
    pa, pb = pool_of(old_jar), pool_of(jar)

    def members(p_, cn):
        c_ = p_.get(cn)
        d_ = {}
        for f_ in c_.getDeclaredFields():
            d_["f " + str(f_.getName())] = str(f_.getSignature()) + " " + str(f_.getModifiers())

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
                ln_ = re.sub(r"^ldc_w ", "ldc ", re.sub(r"#\d+ = ", "", str(IP.instructionString(it_, pos_, cpl_))))
                lines_.append(re.sub(r"^((?:if\w*|goto(?:_w)?|jsr(?:_w)?)) -?\d+$", r"\1", ln_))
            return str(b_.getModifiers()) + "\n" + "\n".join(lines_)
        for m_ in c_.getDeclaredMethods():
            d_["m " + str(m_.getName()) + str(m_.getSignature())] = code(m_)
        for m_ in c_.getDeclaredConstructors():
            d_["c " + str(m_.getSignature())] = code(m_)
        ci = c_.getClassInitializer()
        if ci is not None:
            d_["<clinit>"] = code(ci)
        return d_
    na, nb = HK.jar_classes(old_jar), HK.jar_classes(jar)
    K.eq(sorted(set(nb) - set(na)), sorted(pkg + a for a in added), "C: classes added")
    K.eq(sorted(set(na) - set(nb)), sorted(pkg + r for r in removed), "C: classes removed")
    diffs, same = {}, 0
    for cn in sorted(set(na) & set(nb)):
        ma, mb = members(pa, cn), members(pb, cn)
        dd = sorted(k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k))
        if dd:
            diffs[cn[len(pkg):] if cn.startswith(pkg) else cn] = sorted(("+" if k not in ma else ("-" if k not in mb else "~")) + k for k in dd)
        else:
            same += 1
    got = dict((k, sorted(x.split("(")[0] if not x[1:].startswith("c ") else x[:3] for x in v)) for k, v in diffs.items())
    print("C. class compare %s -> %s: %d classes identical, %d differ" % (os.path.basename(old_jar), os.path.basename(jar), same, len(diffs)))
    for k in sorted(got):
        print("   %-22s %s" % (k, ", ".join(got[k])))
    if expect is None:
        json.dump(got, open(os.path.join(os.path.dirname(out), "expect.json"), "w"), indent=1, sort_keys=True)
        K.check(False, "C: no expect file yet - the diff is in expect.json (review it, then save it as test_skyyfishing_0.2.0.expect.json)")
    else:
        K.eq(sorted(got), sorted(expect), "C: the classes that differ")
        for k in sorted(expect):
            K.eq(got.get(k, []), sorted(expect[k]), "C: %s members" % k)
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    ea = set(n for n in za.namelist() if not n.endswith(".class"))
    eb = set(n for n in zb.namelist() if not n.endswith(".class"))
    K.eq(sorted(ea - eb), [], "C: no non-class entry removed")
    changed = sorted(n for n in ea & eb if za.read(n) != zb.read(n))
    new = sorted(eb - ea)
    # changes allowed: the manifest, the lang file, the T5 / T6 re-tint (any file naming Adamantite / Mithril), the reels / parts whose look
    # changed nothing else; every Zone 1 fish JSON and the T0-T4 + Onyxium rod art identical
    bad = [n for n in changed if n not in ("manifest.json", "Server/Languages/en-US/server.lang") and "Adamantite" not in n and "Mithril" not in n]
    K.eq(bad, [], "C: changed non-class entries outside the lang / manifest / T5-T6 re-tint")
    K.check(all(("SkyyFishing_Fish_" + k) not in "".join(changed) for k in list(MAXCM)[:10]), "C: the Zone 1 fish files are byte-identical")
    K.check(all(("_Fish_" + k) in "".join(new) for k in list(MAXCM)[10:]), "C: the 17 new species' files are new")
    K.notes.append("C: %d identical classes; non-class: %d changed (%s ...), %d new" % (same, len(changed), changed[:6], len(new)))
    K.save()


HK.run_compare = run_compare2


# ------------------------------------------------------------------------------------------------ shared setup (the 0.1.10 harness's)
def setup(K, scratch, tag, load=True):
    from jpype import JClass
    T19.JAR_NOW[0] = JAR
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, JAR], verify=True)
    P = lambda n: JClass(PKG + n)
    Defs = P("FishDefs")
    ids = set(["Rock_Stone"])
    Mod = JClass("java.lang.reflect.Modifier")
    for f in Defs.class_.getDeclaredFields():
        if not Mod.isStatic(f.getModifiers()):
            continue
        f.setAccessible(True)
        v = f.get(None)
        vals = [v] if isinstance(v, str) else (list(v) if v is not None and str(f.getType().getName()) == "[Ljava.lang.String;" else [])
        for x in vals:
            if x is not None and re.match(r"\A[A-Z][A-Za-z]+_[A-Za-z0-9_]+\Z", str(x)):
                ids.add(str(x))
    T15.item_store(sorted(ids))
    mods = os.path.join(scratch, "mods-" + tag)
    os.makedirs(mods, exist_ok=True)
    P("FishLog").SINK = JClass("java.util.ArrayList")()
    if load:
        Paths = JClass("java.nio.file.Paths")
        P("FishCfg").load(Paths.get(mods))
        P("FishStore").start(Paths.get(mods))
    return P, mods


def fn_proxy(f):
    from jpype import JImplements, JOverride

    @JImplements("java.util.function.Function")
    class Fn(object):
        @JOverride
        def apply(self, o):
            return f(o)
    return Fn()


def old_text():
    from jpype import JClass, JArray
    arr = JArray(JClass("java.net.URL"))(2)
    arr[0] = JClass("java.io.File")(OLD_JAR).toURI().toURL()
    arr[1] = JClass("java.io.File")(B.SERVER_JAR).toURI().toURL()
    ld = JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getPlatformClassLoader())
    return str(JClass(PKG + "FishCfg", loader=ld).DEFAULT_TEXT)


def income(Cfg, Defs, zone, ri):
    rodkg = float(Cfg.ROD_KG[ri])
    tot = w = 0.0
    for i in range(len(Defs.SP_KEY)):
        if int(Defs.SP_ZONE[i]) != zone or float(Cfg.SP_MIN[i]) > rodkg or float(Cfg.SP_W[i]) <= 0:
            continue
        mn, mx = float(Cfg.SP_MIN[i]), min(float(Cfg.SP_MAX[i]), rodkg)
        tot += float(Cfg.SP_W[i]) * (mn + (mx - mn) / 3.0) * float(Cfg.priceKg(zone)) * float(Cfg.PRICE_M[int(Defs.SP_RAR[i])])
        w += float(Cfg.SP_W[i])
    return 134.0 * tot / w


# ------------------------------------------------------------------------------------------------ LOGIC (H2-H14)
def run_logic(out, jar, scratch, _home):
    from jpype import JClass, JString, JArray
    K = HK.Child(out)
    P, mods = setup(K, scratch, "logic")
    Defs, Cfg, Zone, Core, Rig, Store, Bench, Brg, Math_, Sta, Eng, QFn = (P("FishDefs"), P("FishCfg"), P("FishZone"), P("FishCore"), P("FishRig"),
                                                                          P("FishStore"), P("FishBench"), P("FishBridge"), P("FishMath"),
                                                                          P("FishState"), P("FishEng"), P("FishQuestFn"))
    UUID, Rnd, IS, SIC, SH, Integer, Long = (JClass("java.util.UUID"), JClass("java.util.Random"), JClass("com.hypixel.hytale.server.core.inventory.ItemStack"),
                                             JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer"), JClass("java.lang.Short"),
                                             JClass("java.lang.Integer"), JClass("java.lang.Long"))
    keys = [str(k) for k in Defs.SP_KEY]
    zone = [int(z) for z in Defs.SP_ZONE]
    sp = dict((k, i) for i, k in enumerate(keys))
    # ---- H1 / H2
    K.check(len(keys) == 27 and len(set(keys)) == 27 and [zone.count(z) for z in (1, 2, 3)] == [10, 8, 9], "H1 27 species: 10 / 8 / 9 by zone")
    K.check(round(sum(float(Cfg.SP_W[i]) for i in range(27) if zone[i] == 2), 2) == 83.65 and round(sum(float(Cfg.SP_W[i]) for i in range(27) if zone[i] == 3), 2) == 86.86
            and all(float(Cfg.SP_W[i]) > 0 for i in range(27)), "H2 zone spawn weights > 0, sums 83.65 / 86.86")
    K.check(sum(int(x) for x in Cfg.JUNK_W) == 100 and sum(int(x) for x in Cfg.JUNK2_W) == 100 and sum(int(x) for x in Cfg.JUNK3_W) == 100, "H2 junk tables sum to 100")
    # ---- H3
    bad = []
    for i, k in enumerate(keys):
        l = float(Math_.lengthCm(float(Defs.SP_MAX0[i]), float(Defs.SP_K[i]), 0.5))
        if abs(l - MAXCM[k]) / MAXCM[k] >= 0.12:
            bad.append((k, l))
    K.check(not bad, "H3 the 12 %% max-length rule on all 27: %s" % bad)
    # ---- H4
    z2, z3 = income(Cfg, Defs, 2, 3), income(Cfg, Defs, 3, 6)
    K.check(abs(z2 - 35135) / 35135 < 0.01 and abs(z3 - 254460) / 254460 < 0.01, "H4 income Z2 Thorium %.0f (35,135), Z3 Azurvane %.0f (254,460)" % (z2, z3))
    K.notes.append("H4 income per h: Z1 Copper %.0f / Iron %.0f, Z2 Iron %.0f / Thorium %.0f / Cobalt %.0f, Z3 Cobalt %.0f / Chromium %.0f / Azurvane %.0f" % tuple(
        income(Cfg, Defs, z, r) for z, r in ((1, 1), (1, 2), (2, 2), (2, 3), (2, 4), (3, 4), (3, 5), (3, 6))))
    # ---- H5
    def reach(z, ri):
        kg = float(Cfg.ROD_KG[ri])
        return dict((i, min(float(Cfg.SP_MAX[i]), kg)) for i in range(27) if zone[i] == z and float(Cfg.SP_MIN[i]) <= kg)
    for ri in (3, 4, 5, 6):
        gain = any(set(reach(z, ri)) - set(reach(z, ri - 1)) or any(reach(z, ri)[i] > reach(z, ri - 1).get(i, 0) for i in reach(z, ri)) for z in (2, 3))
        K.check(gain, "H5 rod %s opens a species or a full-size ceiling" % Defs.TIER_SHOWN[ri])
    K.check([len(reach(2, r)) for r in (2, 3, 4)] == [6, 7, 8] and [len(reach(3, r)) for r in (3, 4, 5, 6)] == [5, 5, 7, 9], "H5 species counts by rod (spec 7)")
    # ---- H6 zone pick (a stand-in mob:fn:levelAt by world name)
    bands = {"w15": (8, 15), "w25": (21, 25), "w45": (41, 45), "w70": (61, 70)}
    Brg.bridge().put("mob:fn:levelAt", fn_proxy(lambda o: (None if str(o[0]) not in bands else JArray(JClass("java.lang.Object"))([Integer(bands[str(o[0])][0]), Integer(bands[str(o[0])][1]), "s", "k"]))))
    K.eq([int(Zone.zoneAt(w, 1.0, 64.0, 1.0)) for w in ("w15", "w25", "w45", "w70", "island")], [1, 2, 3, 3, 1], "H6 zone pick 15 / 25 / 45 / 70 (maxBuilt) / none")
    Cfg.ZONE_DEF = 2
    K.eq(int(Zone.zoneAt(None, 0.0, 0.0, 0.0)), 2, "H6 no level known -> fish.zone.default")
    Cfg.ZONE_DEF = 1
    Cfg.ZONE_MAX = 2
    K.eq(int(Zone.zoneAt("w45", 0.0, 0.0, 0.0)), 2, "H6 fish.zone.maxBuilt 2 -> Zone 3 water fishes Zone 2")
    Cfg.ZONE_MAX, Cfg.ZONE_DEF = 5, 5          # FIX2: the rows take 1-5 (spec 6); only Zones 1-3 have fish -> clamped to 3
    K.eq([int(Zone.maxBuilt()), int(Zone.zoneAt(None, 0.0, 0.0, 0.0)), int(Zone.zoneAt("w70", 0.0, 0.0, 0.0))], [3, 3, 3],
         "H6 fish.zone.maxBuilt 5 / fish.zone.default 5 clamp to the highest built zone 3")
    Cfg.ZONE_DEF = 1
    Cfg.ZONE_MAX = 3
    Cfg.ZONE_TEXT = "40,20,x"
    Cfg.derive()
    sink = [str(x) for x in P("FishLog").SINK]
    K.check(list(Cfg.ZTOPS) == [20, 40, 60, 80, 100] and sum(1 for x in sink if x.startswith("W|fish.zone.tops")) == 1, "H6 broken fish.zone.tops -> the defaults + one WARN")
    Cfg.derive()
    K.check(sum(1 for x in [str(y) for y in P("FishLog").SINK] if x.startswith("W|fish.zone.tops")) == 1, "H6 the WARN is logged once")
    Cfg.ZONE_TEXT = "20,40,60,80,100"
    Cfg.derive()
    # ---- H7 lean + time + season
    oc, ss, om = sp["OasisCarp"], sp["Sandskipper"], sp["OverdueMinnow"]
    K.eq([round(float(Zone.lean(oc, s, 0)), 3) for s in (0, 1, 2, 3, 4)], [1.0, 0.5, 1.5, 0.5, 0.5], "H7 Oasis Carp (summer): season lean")
    K.eq([round(float(Zone.lean(ss, 0, t)), 3) for t in (0, 1, 2, 3, 4)], [1.0, 0.5, 1.5, 0.5, 0.5], "H7 Sandskipper (day): time lean")
    K.eq([round(float(Zone.lean(om, s, t)), 3) for s, t in ((2, 2), (4, 4))], [1.0, 1.0], "H7 any / any = x1")
    Cfg.SEASON_ON = False
    K.eq(round(float(Zone.lean(oc, 2, 0)), 3), 1.0, "H7 seasons off = x1")
    K.eq(int(Zone.seasonNow(1000)), 0, "H7 seasons off -> season 0")
    Cfg.SEASON_ON = True
    Zone.SEASON_TEST = JString("Winter")
    K.eq(int(Zone.seasonNow(1000)), 4, "H7 a stand-in season source: Winter = 4")
    Zone.SEASON_TEST = None
    Zone.SEASON_AT = 0
    K.eq(int(Zone.seasonNow(5000)), 0, "H7 no Dynamic Seasons -> no season (0)")
    K.check(any("Dynamic Seasons: no readable season" in str(x) for x in P("FishLog").SINK), "H7 one INFO line when Dynamic Seasons is missing")
    tod = []
    for h in (5, 6, 7, 8, 12, 17, 18, 20, 21, 0):
        Zone.HOUR_TEST = h
        tod.append(int(Zone.tod(None)))
    K.eq(tod, [1, 1, 1, 2, 2, 2, 3, 3, 4, 4], "H7 the hour -> dawn / day / dusk / night")
    Zone.HOUR_TEST = -2
    Zone.SUN_TEST = 0.6
    a1 = int(Zone.tod(None))
    Zone.SUN_TEST = 0.1
    a2 = int(Zone.tod(None))
    Zone.SUN_TEST = -1.0
    a3 = int(Zone.tod(None))
    K.eq([a1, a2, a3], [2, 4, 0], "H7 no clock: daylight >= 0.25 day, else night; none = unknown")
    Zone.HOUR_TEST = -1
    K.eq(int(Zone.tod(None)), 0, "H7 no world = unknown")
    K.eq([round(float(Zone.biteMult(z, s)), 2) for z, s in ((3, 4), (3, 2), (2, 4), (1, 4))], [0.67, 1.0, 1.0, 1.0], "H7 Zone 3 winter bite x0.67 only")
    Cfg.SEASON_IN = 1.0
    Cfg.SEASON_OUT = 1.0
    st = Sta(UUID.fromString(U1S))
    st.stat = Rig.stats(6, ["0", "", "", ""])
    st.zone = 3
    waits = []
    for se in (2, 4):
        st.season = se
        Core.roll(st, Rnd(77), 1000000)
        waits.append(int(st.biteAt) - 1000000)
    K.check(abs(waits[1] / float(waits[0]) - 0.67) < 0.01, "H7 FishCore.roll: Zone 3 winter bite = summer x0.67 (%s)" % waits)
    Cfg.SEASON_IN = 1.5
    Cfg.SEASON_OUT = 0.5
    # season lean in the roll: Zone 2 summer vs winter, Oasis Carp share
    Cfg.KIND_FISH, Cfg.KIND_JUNK, Cfg.KIND_TREASURE = 100, 0, 0
    st.zone = 2
    st.stat = Rig.stats(4, ["0", "", "", ""])
    shares = []
    for se in (2, 4):
        st.season, st.tod = se, 0
        r = Rnd(5)
        n = 0
        for _ in range(4000):
            Core.roll(st, r, 1000000)
            n += int(st.sp) == oc
        shares.append(n / 4000.0)
    K.check(shares[0] > shares[1] * 2.2, "H7 the roll leans: Oasis Carp summer %.3f vs winter %.3f" % tuple(shares))
    # ---- H8 never heavier than the rod, never another zone (10,000 seeded rolls per rod x zone)
    worst = []
    for z in (1, 2, 3):
        for ri in range(7):
            st.zone, st.season, st.tod = z, 0, 0
            st.stat = Rig.stats(ri, ["0", "", "", ""])
            r = Rnd(1000 * z + ri)
            kgmax = float(Cfg.ROD_KG[ri])
            hi = 0.0
            for _ in range(10000):
                Core.roll(st, r, 1000000)
                if int(st.kind) != 0:
                    continue
                if zone[int(st.sp)] != z:
                    worst.append(("zone", z, ri, keys[int(st.sp)]))
                    break
                hi = max(hi, float(st.kg))
            if hi > kgmax + 1e-9:
                worst.append(("kg", z, ri, hi, kgmax))
    K.check(not worst, "H8 70,000 x 3 rolls: no fish over the rod / from another zone: %s" % worst[:4])
    Cfg.KIND_FISH, Cfg.KIND_JUNK, Cfg.KIND_TREASURE = 85, 10, 5
    # ---- H9 recipes
    outs = [str(x) for x in Defs.R_OUT]
    def rt(o):
        return TT.tier(o) if TT.tier(o) else {"I": 1, "II": 2, "III": 7}[o.rsplit("_", 1)[1]]
    K.check(len(outs) == len(set(outs)) == 43 and outs == sorted(outs, key=lambda o: (rt(o), str(Bench.name(o)))), "H9 43 recipes, one per output, sorted by tier then name")
    rin = [str(x) for x in Defs.R_IN]
    K.check(not [i for i in rin if "Bamboo" in i or "oin" in i.split("_")[-1]], "H9 no bamboo, no coin input")
    prev = dict((outs[i], str(Defs.R_PREV[i])) for i in range(len(outs)))
    K.check(all(prev["SkyyFishing_Rod_%s" % b] == "SkyyFishing_Rod_%s" % a for a, b in zip(TT.LADDER[:0] or ("Iron", "Thorium", "Cobalt", "Adamantite"), ("Thorium", "Cobalt", "Adamantite", "Mithril"))),
            "H9 every rod consumes the one below")
    u = UUID.fromString(U1S)
    key = str(Brg.pkey(u))
    coll = {"Thorium": 0, "Cobalt": 0, "Chromium": 0, "Copper": 2, "Iron": 2}
    Brg.bridge().put("coll:fn:tier", fn_proxy(lambda o: Integer(coll.get(str(o[1]), 0))))
    r_th, r_mi, r_cu = outs.index("SkyyFishing_Rod_Thorium"), outs.index("SkyyFishing_Rod_Mithril"), outs.index("SkyyFishing_Rod_Copper")
    Store.setCount(key, 2, 99)
    g1 = int(Bench.gate(u, key, r_th))
    Store.setCount(key, 2, 100)
    g2 = int(Bench.gate(u, key, r_th))
    coll["Thorium"] = 2
    g3 = int(Bench.gate(u, key, r_th))
    K.eq([g1, g2, g3], [1, 2, 0], "H9 Thorium rod: Dune III (99 -> locked, 100 -> metal), Thorium II -> open")
    Store.setCount(key, 3, 1000)
    coll["Cobalt"], coll["Chromium"] = 5, 4
    a = int(Bench.gate(u, key, r_mi))
    coll["Cobalt"], coll["Chromium"] = 4, 5
    b = int(Bench.gate(u, key, r_mi))
    coll["Cobalt"], coll["Chromium"] = 5, 5
    c = int(Bench.gate(u, key, r_mi))
    K.eq([a, b, c], [2, 2, 0], "H9 Azurvane rod: Cobalt V AND Chromium V (the alloy rule)")
    K.check(str(Bench.gateText(r_mi)) == "Frost Fish VI + Cobalt V + Chromium V" and str(Bench.lockTag(u, key, outs.index("SkyyFishing_Reel_Mithril"))).startswith("Needs Frost VII"),
            "H9 gate texts: %s / %s" % (Bench.gateText(r_mi), Bench.lockTag(u, key, outs.index("SkyyFishing_Reel_Mithril"))))
    Store.setPond(key, 100)
    K.eq(int(Bench.gate(u, key, r_cu)), 0, "H9 Copper rod: metal collection II now opens it (was IV)")
    # real crafts on a real container: Iron rod (a lifelong pole + a rig) -> Thorium -> ... -> Azurvane
    W = {"inv": SIC(SH(36).shortValue()), "t": 1000000}
    Eng.API = T19._api(W)
    inv = W["inv"]
    BD, BI = JClass("org.bson.BsonDocument"), JClass("org.bson.BsonInt32")
    gd = BD()
    gd.append("ll", BI(1))
    gd.append("lvl", BI(25))
    iron = Rig.withRig(IS("SkyyFishing_Rod_Iron", 1).withMetadata("SkyyGear", gd), ["3", "SkyyFishing_Hook_Barbed_II", "", ""])
    inv.addItemStack(iron)
    for i_, q_ in (("Ingredient_Bar_Thorium", 75), ("Ingredient_Fabric_Scrap_Linen", 8), ("Skyy_Ench_Cobalt", 2), ("Ingredient_Bolt_Silk", 18),
                   ("Skyy_Ench_Chromium", 2), ("Ingredient_Bar_Azurvane_SkyWynn", 128)):
        while q_ > 0:
            inv.addItemStack(IS(i_, min(q_, 50)))
            q_ -= min(q_, 50)
    # FIX2 (docs/answered/gear.md ENCHANTED STICKS): the T4+ rod crafts also cost 2 / 4 / 8 / 16 Enchanted Sticks (fish.stickCost)
    K.eq([int(Bench.sticks(outs.index("SkyyFishing_Rod_%s" % t))) for t in ("Bamboo", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril")]
         + [int(Bench.sticks(outs.index("SkyyFishing_Reel_Thorium")))], [0, 0, 0, 2, 4, 8, 16, 0], "H9 sticks per rod tier-up (Gear's lifelong.stickCost), none for reels")
    nt = str(Bench.needText(inv, u, r_th))
    K.check("2 Enchanted Stick (0/2)" in nt, "H9 the Thorium rod's needs list the sticks: %s" % nt)
    K.eq(int(Bench.state(inv, u, key, r_th)), 2, "H9 no sticks -> missing items")
    Cfg.STK_TEXT = "0,0,0,0,0,0,0,0"
    Cfg.derive()
    K.check(int(Bench.sticks(r_th)) == 0 and "Enchanted Stick" not in str(Bench.needText(inv, u, r_th)), "H9 fish.stickCost all 0 -> no sticks asked")
    Cfg.STK_TEXT = "1,2,x"
    Cfg.derive()
    K.check(list(Cfg.STK) == [0, 0, 0, 2, 4, 8, 16, 32] and any("fish.stickCost '1,2,x'" in str(x) for x in P("FishLog").SINK), "H9 a broken fish.stickCost -> defaults + WARN")
    Cfg.STK_TEXT = "0,0,0,2,4,8,16,32"
    Cfg.derive()
    inv.addItemStack(IS("Skyy_Ench_Stick", 30))

    coll.update({"Thorium": 2, "Cobalt": 5, "Chromium": 5})
    res = [str(Bench.craft(inv, u, key, outs.index("SkyyFishing_Rod_%s" % t))) for t in ("Thorium", "Cobalt", "Adamantite", "Mithril")]
    rods = [inv.getItemStack(SH(s_).shortValue()) for s_ in range(36)]
    rods = [x for x in rods if x is not None and not x.isEmpty() and int(Defs.rodIndex(x.getItemId())) >= 0]
    K.check(all(r_.startswith("+Crafted") for r_ in res) and len(rods) == 1 and str(rods[0].getItemId()) == "SkyyFishing_Rod_Mithril", "H9 crafts Iron -> Azurvane: %s" % res)
    left = sum(int(x.getQuantity()) for x in [inv.getItemStack(SH(s_).shortValue()) for s_ in range(36)] if x is not None and not x.isEmpty() and int(Defs.rodIndex(x.getItemId())) < 0)
    K.eq(left, 0, "H9 every input used exactly (75 Thorium, 8 linen, 2 + 2 Enchanted, 18 silk, 128 Azurvane, 2 + 4 + 8 + 16 Enchanted Sticks)")
    if rods:
        m = str(rods[0].getMetadata().toJson())
        K.check(list(Rig.rigOf(rods[0])) == ["3", "SkyyFishing_Hook_Barbed_II", "", ""] and '"ll": 1' in m and '"lvl": 25' in m and '"T9 Azurvane - "' in m and '"Max fish weight: "' in m
                and "Azurvane Fishing Rod" in m, "H9 the lifelong pole keeps its SkyyGear document + rig, tooltip T9 Azurvane: %s" % m[:300])
    r4 = str(Bench.craft(inv, u, key, outs.index("SkyyFishing_Rod_Mithril")))
    K.check(r4.startswith("-Missing items"), "H9 nothing left: %s" % r4)
    # ---- H10 tags (tooltips)
    f = Rig.makeFish(sp["GlassPike"], 30000, 1600, "Skyy")
    fj = str(f.getMetadata().toJson())
    K.check('"T8 Fish - "' in fj and '"Rare fish from Zone 3 - 30 kg, 160 cm"' in fj, "H10 the fish tooltip starts with its tag")
    # ---- FIX (critic Style Guide 15): colour coded tooltips + lang
    rj = str(Rig.withRig(IS("SkyyFishing_Rod_Thorium", 1), ["4", "SkyyFishing_Hook_Barbed_III", "", ""]).getMetadata().toJson())
    K.check('"T4 Thorium - "' in rj and '"#96a9be"' in rj and '"Max fish weight: "' in rj and '"#d6e4ee"' in rj and '"#7ee08a"' in rj and '"#7f93a6"' in rj
            and '"Bold": true' in rj, "FIX H10c the rod tooltip: tag bold label, stat name soft white, value green bold, empty slot dim: %s" % rj[:600])
    K.check("#96a9be" in fj, "FIX H10c the fish tooltip tag in the label colour")
    old_r = IS("SkyyFishing_Rod_Thorium", 1)
    K.check(not bool(Rig.stale(Rig.restampOne(Rig.withRig(old_r, ["0", "", "", ""])))), "FIX H10c a colour-coded rod is not redrawn again (stale finds the tag)")
    lang = zipfile.ZipFile(jar).read("Server/Languages/en-US/server.lang").decode("utf8")
    lr = [l_ for l_ in lang.splitlines() if l_.startswith("items.SkyyFishing_Rod_Thorium.description=") or l_.startswith("items.SkyyFishing_Reel_Cobalt.description=")
          or l_.startswith("items.SkyyFishing_Hook_Barbed_III.description=") or l_.startswith("items.SkyyFishing_Fish_GlassPike.description=")]
    K.check(len(lr) == 4 and all('<color is="' in l_ and "</color>" in l_ for l_ in lr) and lr and all(l_.split("=", 1)[1].startswith("T") or "Hook_" in l_ for l_ in lr)
            and any('T4 Thorium - Max fish weight <color is="#7ee08a">16 kg</color>' in l_ for l_ in lr), "FIX H10c lang: stat values in <color> spans, tag still first: %s" % lr)
    K.check(all(str(Rig.rodLines(ri, ["0", "", "", ""]).get(0)).startswith(TT.tag_for("SkyyFishing_Rod_" + str(Defs.TIERS[ri])) + " - ") for ri in range(8)), "H10 rod tooltips start with the tag")
    old = IS("SkyyFishing_Rod_Copper", 1)
    bd = BD()
    bd.append("v", BI(1))
    bd.append("reel", BI(2))
    old = old.withMetadata("SkyyFishing", bd)
    K.check(bool(Rig.stale(old)) and not bool(Rig.stale(Rig.restampOne(old))), "H10 a rod drawn without the tag is redrawn once (stale -> restamp -> fresh)")
    # ---- H11 saved data
    pdir = os.path.join(mods, "Skyy_SkyyFishing", "players")
    os.makedirs(pdir, exist_ok=True)
    k2 = "00000000-0000-4000-8000-00000000a011"
    open(os.path.join(pdir, k2 + ".properties"), "w").write("# 0.1.12\npond=30\nsp.Bluegill.n=3\nsp.Bluegill.g=900\nsp.Bluegill.mm=400\nclaims=0\n")
    Paths = JClass("java.nio.file.Paths")
    Store.flush()
    Store.start(Paths.get(mods))
    K.eq([int(Store.count(k2, z)) for z in (1, 2, 3)], [30, 0, 0], "H11 a 0.1.12 players file: pond 30, dune / frost 0")
    Store.onCatch(k2, sp["OasisCarp"], 2000, 500)
    Store.onCatch(k2, sp["FrostCod"], 3000, 700)
    Store.onCatch(k2, sp["FrostCod"], 3100, 710)
    K.eq([int(Store.count(k2, z)) for z in (1, 2, 3)], [30, 1, 2], "H11 a Zone 2 / 3 catch counts its zone")
    K.eq(int(QFn("pond").apply(UUID.fromString(k2))), 33, "H11 fishing:fn:pond = pond + dune + frost")
    Store.flush()
    txt = open(os.path.join(pdir, k2 + ".properties")).read()
    K.check("pond=30\n" in txt and "dune=1\n" in txt and "frost=2\n" in txt and "sp.FrostCod.n=2" in txt and "sp.Bluegill.n=3" in txt, "H11 the file: %s" % txt.replace("\n", " ")[:200])
    Store.start(Paths.get(mods))
    K.eq([int(Store.count(k2, z)) for z in (1, 2, 3)], [30, 1, 2], "H11 round trip")
    # ---- H12 a 0.1.12 config: every new row at its default, nothing rewritten
    om_ = os.path.join(scratch, "mods-old")
    os.makedirs(os.path.join(om_, "Skyy_SkyyFishing"))
    ot = old_text()
    open(os.path.join(om_, "Skyy_SkyyFishing", "config.properties"), "wb").write(ot.encode("latin-1"))
    Cfg.load(Paths.get(om_))
    K.check(open(os.path.join(om_, "Skyy_SkyyFishing", "config.properties"), "rb").read() == ot.encode("latin-1"), "H12 FishCfg.load rewrites no line of a 0.1.12 file")
    K.check(list(Cfg.ZTOPS) == [20, 40, 60, 80, 100] and int(Cfg.ZONE_DEF) == 1 and int(Cfg.ZONE_MAX) == 3 and list(Cfg.DUNE) == [25, 50, 100, 250, 500, 1000, 2500, 5000]
            and float(Cfg.PRICE_KG2) == 41.0 and float(Cfg.PRICE_KG3) == 82.0 and list(Cfg.TZM) == [1.0, 4.0, 20.0] and list(Cfg.REEL_P) == [4.0, 4.9, 5.7, 6.6, 7.6, 8.7, 9.8]
            and float(Cfg.Z3_WINTER) == 0.67 and bool(Cfg.SEASON_ON) and [int(Cfg.DAWN_LO), int(Cfg.DAWN_HI), int(Cfg.DUSK_LO), int(Cfg.DUSK_HI)] == [5, 7, 18, 20],
            "H12 the new scalar rows at their defaults")
    K.check(list(Cfg.JUNK2) == list(Defs.JUNK2) and list(Cfg.JUNK3) == list(Defs.JUNK3) and list(Cfg.PART_C) == list(Defs.PART_V2)
            and float(Cfg.SP_W[sp["SleeperAisle9"]]) == 0.06 and int(Cfg.SP_SEAS[sp["GlassPike"]]) == 8 and int(Cfg.SP_TIME[sp["GlassPike"]]) == 8,
            "H12 the new tables at their defaults (a wholly missing family = the built-in rows)")
    K.check(int(Cfg.SP_TIME[sp["RustbackTrout"]]) == 5 and int(Cfg.SP_SEAS[sp["OverdueMinnow"]]) == 0, "H12 fish.when masks (dawn + dusk = 5, any = 0)")
    Cfg.load(Paths.get(mods))
    # ---- H14 prices by zone, Lost Property by zone
    now = 1000
    p1, p2, p3 = (int(Bench.priceG(sp[k_], 2000, now)) for k_ in ("Bluegill", "OasisCarp", "FrostCod"))
    K.eq([p1, p2, p3], [52, 82, 164], "H14 a 2 kg Normal fish: Zone 1 x26, Zone 2 x41, Zone 3 x82")
    K.eq(int(Bench.priceG(sp["MirageEel"], 2000, now)), 123, "H14 Unique Zone 2: 2 x 41 x 1.5")
    st.stat = Rig.stats(6, ["0", "", "", ""])
    seen = {1: set(), 2: set(), 3: set()}
    coins = {1: [], 2: [], 3: []}
    for z in (1, 2, 3):
        st.zone = z
        r = Rnd(9 + z)
        for _ in range(3000):
            Core.FORCE.put(st.uuid, Integer(1))
            Core.roll(st, r, 1000000)
            if int(st.coins) > 0:
                coins[z].append(int(st.coins))
            elif st.item is not None:
                seen[z].add(str(st.item))
    K.check(coins[1] and min(coins[1]) >= 300 and max(coins[1]) <= 700 and min(coins[2]) >= 1200 and max(coins[2]) <= 2800 and min(coins[3]) >= 6000 and max(coins[3]) <= 14000,
            "H14 Great purses x1 / x4 / x20: %s %s %s" % tuple((min(coins[z]), max(coins[z])) for z in (1, 2, 3)))
    K.check("Ore_Copper" not in seen[2] | seen[3] and "Ore_Iron" not in seen[2] | seen[3] and "Skyy_Ench_Cobalt" in seen[3] and "Skyy_Ench_Cobalt" not in seen[1] | seen[2],
            "H14 Zone 2 / 3 Lost Property swaps the Zone 1 ores; Zone 3 Great bars give Enchanted Cobalt now and then: %s" % sorted(seen[3]))
    Cfg.FIL_KG = 0.5
    K.notes.append("LOGIC: zone lookups %s" % Zone.LOOKUPS)
    K.save()


# ------------------------------------------------------------------------------------------------ SEED (FishZ2Seed)
def snapd(d):
    return dict((os.path.relpath(os.path.join(r, f), d).replace(os.sep, "/"), open(os.path.join(r, f), "rb").read()) for r, ds, fs in os.walk(d) for f in fs)


def reset(P):
    P("CfgHist").DIR = None
    P("CfgRows").HOME = None
    P("CfgLog").FILE = None
    P("CfgLog").Q.clear()


def run_seed(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    P, _m = setup(K, scratch, "seed", load=False)
    S, Cfg = P("FishZ2Seed"), P("FishCfg")
    Paths = JClass("java.nio.file.Paths")
    MARK = str(S.MARK)
    OLDT, NEWT = old_text(), str(Cfg.DEFAULT_TEXT)
    n = len(S.E_KEY)
    K.check(n == 78 and S.plan(JString(NEWT)) is None and MARK in NEWT and MARK not in OLDT, "SEED 78 entries (8 + 9 + 27 + 13 + 11 + 10); a fresh 0.2.0 file carries the marker (plan = nothing)")
    r = S.plan(JString("a=1\n"))
    t = str(r[0])
    K.check(t.startswith("a=1\n# Zone 2 species") and t.endswith(MARK + "\n") and len(r[1]) == 78 and "fish.z2.junk.Rock_Salt=16\n" in t and "fish.when.GlassPike=winter,night\n" in t,
            "SEED plan appends the 6 blocks + the marker")
    K.check(str(r[3][0]) == "fish.z2.species[OasisCarp]" and str(r[4][0]) == "20|1|8", "SEED log key / value = tableKey[entry], columns joined by |")
    r = S.plan(JString("x=1\r\nfish.z2.junk.Rock_Salt=3\r\n"))
    t = str(r[0])
    K.check("\r\n" in t and "\n" not in t.replace("\r\n", "") and "fish.z2.junk.Deco_Trash" not in t and len(r[1]) == 78 - 13 and t.startswith("x=1\r\nfish.z2.junk.Rock_Salt=3\r\n"),
            "SEED CRLF kept; a family already there (one hand line) is left alone")
    K.check(str(S.plan(JString("x=1"))[0]).startswith("x=1\n# Zone 2"), "SEED no final newline -> one added first")
    for tag, txt in (("lf", OLDT), ("crlf", OLDT.replace("\n", "\r\n"))):
        mods = os.path.join(scratch, "seed", tag)
        d = os.path.join(mods, "Skyy_SkyyFishing")
        os.makedirs(d)
        open(os.path.join(d, "config.properties"), "wb").write(txt.encode("latin-1"))
        reset(P)
        s0 = snapd(d)
        r1 = str(S.run(Paths.get(mods)))
        s1 = snapd(d)
        new = s1["config.properties"].decode("latin-1")
        nl = "\r\n" if tag == "crlf" else "\n"
        K.check(new.startswith(txt) and new.endswith(MARK + nl) and len(re.findall(r"(?m)^fish\.z3\.species\.\w+=", new)) == 9, "SEED run %s: the old bytes untouched, the blocks + marker appended" % tag)
        K.check(sum(1 for k in s1 if k.startswith("config-history/") and s1[k] == s0["config.properties"]) == 1, "SEED run %s: History holds the old file" % tag)
        lg = s1.get("config-changes.log", b"").decode("latin-1")
        K.check(lg.count("\t(none)\t") == 78 and "\tfish.parts3[clean]\t(none)\t75\tok" in lg, "SEED run %s: one change-log row per entry" % tag)
        K.check("78 default lines" in r1, "SEED run %s INFO: %s" % (tag, r1))
        reset(P)
        K.check(str(S.run(Paths.get(mods))) == "" and snapd(d) == s1, "SEED run %s: start 2 changes nothing" % tag)
        Cfg.load(Paths.get(mods))
        K.check(float(Cfg.PART_C[0]) == 15.0 and len(Cfg.JUNK2) == 13, "SEED run %s: FishCfg.load reads the tables" % tag)
    mods = os.path.join(scratch, "seed", "fresh")
    os.makedirs(mods)
    reset(P)
    K.check(str(S.run(Paths.get(mods))) == "" and snapd(mods) == {}, "SEED no file -> nothing")
    Cfg.load(Paths.get(mods))
    t0 = open(os.path.join(mods, "Skyy_SkyyFishing", "config.properties"), "rb").read()
    reset(P)
    K.check(str(S.run(Paths.get(mods))) == "" and open(os.path.join(mods, "Skyy_SkyyFishing", "config.properties"), "rb").read() == t0, "SEED a fresh 0.2.0 file is never touched")
    K.save()


# ------------------------------------------------------------------------------------------------ LIVE (a scratch COPY of the live folder, twice)
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    P, _m = setup(K, scratch, "live", load=False)
    Paths = JClass("java.nio.file.Paths")
    mods = os.path.dirname(home)

    def start():
        reset(P)
        r = str(P("FishP3Mig").run(Paths.get(mods))) + " | " + str(P("FishZ2Seed").run(Paths.get(mods)))
        P("FishCfg").load(Paths.get(mods))
        P("FishStore").start(Paths.get(mods))
        for f in os.listdir(os.path.join(home, "players")) if os.path.isdir(os.path.join(home, "players")) else []:
            if f.endswith(".properties"):
                P("FishStore").data(f[:-11])
        P("FishStore").flush()
        return r
    s0 = snapd(home)
    r1 = start()
    s1 = snapd(home)
    r2 = start()
    s2 = snapd(home)
    ch = sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k))
    K.check(all(k == "config.properties" or k == "config-changes.log" or k.startswith("config-history/") for k in ch), "LIVE start 1 changes only the config + History + log: %s" % ch)
    K.check(s1 == s2 and r2.strip() == "|", "LIVE start 2 changes nothing (%s)" % r2)
    t1 = s1["config.properties"].decode("latin-1")
    K.check(t1.startswith(s0["config.properties"].decode("latin-1")) and str(P("FishZ2Seed").MARK) in t1, "LIVE the old file is a prefix of the new one (append only)")
    cnt = [int(P("FishStore").count(f[:-11], z)) for f in os.listdir(os.path.join(home, "players")) for z in (1, 2, 3)] if os.path.isdir(os.path.join(home, "players")) else []
    K.notes.append("LIVE: %s ; counts %s" % (r1[:300], cnt))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyFishing", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("logic", run_logic), ("seed", run_seed), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyFishing"))
