"""Harness for SkyyGear 0.3.53 (gear lane round 1 = gl1: the Bronze rung + spear recipes, 10 vanilla-look Untiered weapons, the Void Scythe Mythic,
Crude Diving out of the bags, the ELEMENT POWER tooltip note - tools/gear_0_3_53_patch.py header).
Build first:
    python tools/gear_0_3_53_patch.py && python SkyyGear/build_skyygear_0.3.53.py
    python SkyyGear/test_skyygear_0.3.53.py [--keep]

Phases (fresh child processes / JVMs, tools/harness_kit.py; the 0.3.52 jar is the compare base):
  S  static   the patch re-runs to identical bytes, line endings kept, no new class / command / system; the jar's non-class files = 0.3.52's +
              the 9 UT copies + 18 art files + 11 recipes, only manifest.json + server.lang changed; every copy (Untiered quality, band start,
              the vanilla model by path, no recipe), every recipe (Bronze Ingots, the bench), the lang (zone alloy tag first), tools/ut_vanilla.py
              + tools/tier_tags.py rows, the fresh config text (30 rows, the new Mythic list, both markers)
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.3.52 -> 0.3.53 (EXPECT below)
  E  engine   the 0.2.11 harness's bare server boot (vanilla pack + THIS jar) - every new path EXECUTED:
              V  the 9 copies in the real Item store (Untiered quality, packets), the 11 recipes in the real CraftingRecipe store, no SEVERE /
                 WARNING about our files
              B  the Bronze rung + spears: GearPack.combatId, GearLevel.band (Bronze 15-23), the pool table (crafted, not drop-only), the bench
                 veto text, the Smithing > Weapons cards (sorted by tier, Bronze between Iron and Thorium), a future SkyyArmory
                 Weapon_Axe_Bronze_SkyWynn id read as a plain Bronze piece
              U  the UT rows: GearUt.has / band (zone end), GearUtFx.row (the trick values), GearUt.rowsOf + pickItem (the orange-bag pick at the
                 zone levels), the Armory row unusable (no item), a REAL tooltip (orange trade-off line, the T3 Bronze tag)
              P  the pool: the 10 looks + Crude Diving out of P_ID, Wool / dev-bow rules unchanged; the Void Scythe: GearUtFx.mythicId, legacy =
                 Mythic, never a pool candidate
              T  the ELEMENT POWER line = GearAug.power() (socketed + rolled lines) + the Imbue note under it; none on a weapon without power
              M  the two one-time updates as text (u53Update / h53Update): a 0.3.52 file gets exactly the 30 rows / the new Mythic line; a second run
                 = null; an admin Mythic list kept + noted; an admin utline.power = no utpow rows; CRLF kept; then migrateUt53 / migrateMy53 on a
                 REAL scratch file (History snapshot first, change-log rows, the second start changes nothing)
  D  live     start twice on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyGear: every one-time update + load() twice; the second start
              changes nothing; only the gl1 block, the Mythic line and the markers (plus the older 0.3.5x updates) may change the file
  AA engine-access audit
NOT COVERED (UNVERIFIED in game): the client drawing the 9 copies (placeholder art), the Smithing tab crafting a Bronze weapon end to end with
SkyySacks, an orange bag really dropping one from an elite, the Void Scythe from a boss (no source until the boss round).
Scratch: tools/dev/scratch/gl1/harness (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, zipfile, re, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.3.53"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "gl1", "harness")]
import skyybuild as B
import harness_kit as HK
import ut_vanilla as UTV

GEN = os.path.join(HERE, "build_skyygear_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyygear_0.3.52.py")
PATCH = os.path.join(ROOT, "tools", "gear_0_3_53_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyGear-0.3.52.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.gear."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyGear")
ADDED = []
EXPECT = {          # the first run's dump, reviewed: the version + the Mythic default (CfgRows / CfgFn / GearCfg.apply), the two one-time updates + their
          # tables (GearCfg), the tooltip note (GearAug.tipLines), the pool tables (GearPool: P_N0 is inlined - 4 Diving + 7 looks out), SMC_IDS /
          # LOOT_IDS (GearPack), CRAFTED (GearUt), BASE_FROM / BASE_TO (GearUtFx), the setup calls
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~m header'],
    'CfgRows1': ['~<clinit>'],
    'CfgRows2': ['~<clinit>'],
    'GearAug': ['~m tipLines'],
    'GearCfg': ['+f H53_KEYS', '+f H53_MARK', '+f H53_MARK_ID', '+f H53_NEW', '+f H53_OLD', '+f H53_WHO', '+f U53_GC', '+f U53_GK', '+f U53_GL', '+f U53_GS', '+f U53_HEAD', '+f U53_LK', '+f U53_LV', '+f U53_MARK', '+f U53_MARK_ID', '+f U53_WHO', '+m h53Log', '+m h53Old', '+m h53Update', '+m migrateMy53', '+m migrateUt53', '+m u53Log', '+m u53Update', '~<clinit>', '~m apply', '~m defaultsText'],
    'GearPack': ['~<clinit>'],
    'GearPool': ['~<clinit>', '~m candM', '~m idIdx', '~m levelsM', '~m liveType', '~m matchM', '~m packText', '~m pickItemM', '~m table', '~m typeOfId', '~m w'],
    'GearUt': ['~<clinit>'],
    'GearUtFx': ['~<clinit>'],
    'SkyyGearPlugin': ['~m setup'],
}
U = "00000000-0000-0000-0000-000000000353"
BZ = ["Weapon_Sword_Bronze", "Weapon_Spear_Bronze", "Weapon_Shortbow_Bronze", "Weapon_Staff_Bronze", "Weapon_Daggers_Bronze"]
SPEARS = ["Weapon_Spear_" + m for m in ("Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril")]
OUTS = BZ + SPEARS
RIDS = ["SkyyGear_Recipe_" + o for o in OUTS]
COPIES = list(UTV.GEAR_IDS)
SCYTHE = "Weapon_Battleaxe_Scythe_Void"
MYTH_OLD = "Weapon_Shortbow_Vampire,Weapon_Shortbow_Bomb,Weapon_Shortbow_Pull"
MYTH_NEW = MYTH_OLD + "," + SCYTHE
ALLOY_TAG = {1: "T3 Bronze", 2: "T6 Dusk", 3: "T9 Azurvane", 4: "T12 Cinder"}


def gl1_name(n):
    return (n.startswith("Server/Item/Items/SkyyGear/UT/") and os.path.basename(n)[:-5] in COPIES) \
        or (n.startswith("Common/Items/SkyyGear/UT/") and os.path.basename(n)[:-4] in COPIES) \
        or (n.startswith("Common/Icons/ItemsGenerated/") and os.path.basename(n)[:-4] in COPIES) \
        or (n.startswith("Server/Item/Recipes/SkyyGear/") and os.path.basename(n)[:-5] in RIDS)


def expected_nonclass(za, zb):
    ea = set(n for n in za.namelist() if not n.endswith(".class"))
    eb = set(n for n in zb.namelist() if not n.endswith(".class"))
    return sorted(eb - ea), sorted(n for n in ea & eb if za.read(n) != zb.read(n)), sorted(ea - eb)


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyGear 0.3.53 - build script') and g.count('VERSION = "0.3.53"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("), g.count('mk("') - o.count('mk("')),
         (0, 0, 0), "S no new class / system / command")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.check(not UTV.check(), "S tools/ut_vanilla.py check(): %s" % UTV.check())
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    added, changed, gone = expected_nonclass(za, zb)
    K.eq(gone, [], "S no file removed")
    K.eq(changed, ["Server/Languages/en-US/server.lang", "manifest.json"], "S changed = manifest.json + server.lang")
    K.check(added and all(gl1_name(n) for n in added), "S every added file is a gl1 file: %s" % [n for n in added if not gl1_name(n)][:5])
    K.eq(len(added), 9 + 18 + 11, "S 9 copies + 18 art files + 11 recipes")
    A = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))          # read only
    an = A.namelist()

    def vj(i):
        h = [n for n in an if n.startswith("Server/Item/Items/") and n.endswith("/" + i + ".json")]
        return json.loads(A.read(h[0]).decode("utf-8-sig")) if len(h) == 1 else None
    bad = []
    q28 = json.loads(zb.read("Server/Item/Items/SkyyGear/UT/Weapon_Daggers_UT_DeepcaveShadow.json"))["Quality"]          # the 0.3.47 copies' Untiered quality
    for r in UTV.rows():
        if r[4] != "gear":
            K.check(("Server/Item/Items/SkyyGear/UT/%s.json" % r[0]) not in zb.namelist(), "S the SkyyArmory row %s has no SkyyGear copy" % r[0])
            continue
        j = json.loads(zb.read("Server/Item/Items/SkyyGear/UT/%s.json" % r[0]))
        v = vj(r[5])
        if j.get("Quality") != q28 or j.get("ItemLevel") != UTV.ZONE_BAND[r[3]][0] or j.get("Model") != v.get("Model") or "Recipe" in j \
                or j.get("Texture") != "Items/SkyyGear/UT/%s.png" % r[0] or j.get("Icon") != "Icons/ItemsGenerated/%s.png" % r[0] \
                or j.get("Interactions") != v.get("Interactions") or j.get("Parent") != v.get("Parent"):
            bad.append((r[0], j.get("Quality"), j.get("ItemLevel"), j.get("Model"), v.get("Model")))
        if ("Common/Items/SkyyGear/UT/%s.png" % r[0]) not in zb.namelist() or ("Common/Icons/ItemsGenerated/%s.png" % r[0]) not in zb.namelist():
            bad.append((r[0], "art"))
    K.check(not bad, "S every copy: Untiered quality, ItemLevel = the zone band start, the vanilla model by path + its interactions + Parent, no recipe, "
            "our texture + icon: %s" % bad[:3])
    shared = [(r[0], q[0]) for r in UTV.rows() if r[4] == "gear" for q in __import__("ut28").rows() if q[4] == "gear" and q[6] == r[6]]
    K.check(len(shared) == 3 and all(zb.read("Common/Items/SkyyGear/UT/%s.png" % a) != zb.read("Common/Items/SkyyGear/UT/%s.png" % b) for a, b in shared),
            "S the 3 looks a 0.3.47 UT already wears get a different (darker) map: %s" % shared)
    rb = []
    for o_, rid in zip(OUTS, RIDS):
        r = json.loads(zb.read("Server/Item/Recipes/SkyyGear/%s.json" % rid))
        ins = dict(((x.get("ItemId") or x.get("ResourceTypeId")), x["Quantity"]) for x in r["Input"])
        met = o_.split("_")[2]
        bars = [k for k in ins if k.startswith("Ingredient_Bar_")]
        b0 = r["BenchRequirement"]
        if r["PrimaryOutput"] != {"ItemId": o_, "Quantity": 1} or bars != ["Ingredient_Bar_" + met] or [b["Id"] for b in b0] != ["Weapon_Bench"] \
                or (o_.startswith("Weapon_Spear_") and b0[0]["Categories"] != ["Weapon_Sword"]) or "Armory" in json.dumps(r):
            rb.append((rid, ins, b0))
    sb = json.loads(zb.read("Server/Item/Recipes/SkyyGear/SkyyGear_Recipe_Weapon_Sword_Bronze.json"))
    si = json.loads(zb.read("Server/Item/Recipes/SkyyGear/SkyyGear_Recipe_Weapon_Spear_Thorium.json"))
    K.check(not rb and dict((x["ItemId"], x["Quantity"]) for x in sb["Input"]) == {"Ingredient_Bar_Bronze": 6, "Ingredient_Leather_Light": 3, "Ingredient_Fabric_Scrap_Linen": 3}
            and si["BenchRequirement"][0].get("RequiredTierLevel") == 2, "S the 11 recipes: own metal's bars only (Bronze for the rung), the Weapon Bench (spears: "
            "Sword tab), no Armory entry; Bronze sword = Iron's amounts; Thorium spear = the Thorium sword's tier 2: %s" % rb[:3])
    lang = zb.read("Server/Languages/en-US/server.lang").decode("utf-8")
    lb = []
    for r in UTV.rows():
        if r[4] != "gear":
            if ("items.%s." % r[0]) in lang:
                lb.append((r[0], "armory row written"))
            continue
        nm = [l for l in lang.splitlines() if l.startswith("items.%s.name = " % r[0])]
        ds = [l for l in lang.splitlines() if l.startswith("items.%s.description = " % r[0])]
        if nm != ["items.%s.name = %s" % (r[0], r[1])] or len(ds) != 1 or not ds[0].split(" = ", 1)[1].startswith(ALLOY_TAG[r[3]] + " - "):
            lb.append((r[0], nm, ds))
    K.check(not lb, "S lang: the 9 names, each description starts with the zone's alloy tag; no line for the SkyyArmory row: %s" % lb[:3])
    import importlib
    TT = importlib.import_module("tier_tags")
    K.check(all(TT.family(i) == "ut" and TT.tag_for(i) == ALLOY_TAG[UTV.rows()[UTV.IDS.index(i)][3]] for i in UTV.IDS)
            and TT.owner("Weapon_Staff_UT_Doomcaller") == "SkyyArmory" and all(TT.owner(i) == "SkyyGear" for i in COPIES) and len(TT.UT_IDS) == 74
            and [TT.combat_tag(i, 15) for i in BZ] == ["T3 Bronze"] * 5 and TT.combat_tag("Weapon_Axe_Bronze_SkyWynn", 15) == "T3 Bronze",
            "S tools/tier_tags.py: 10 ut rows (alloy tags, owners), the Bronze weapons tag T3 Bronze by their metal word")
    K.check(g.count("migrateUt53();") == 1 and g.count("migrateMy53();") == 1 and 'MYTHIC_ITEMS_DEF52 = "%s"' % MYTH_OLD in g, "S the two one-time updates are called once; the old Mythic default kept as MYTHIC_ITEMS_DEF52")
    K.notes.append("S %d files added; jar %d -> %d bytes" % (len(added), os.path.getsize(OLD_JAR), os.path.getsize(jar)))
    K.save()


def run_compare53(out, jar, old_jar, pkg, expect, added, removed=()):
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
    print("C. class compare %s -> %s: %d classes identical, %d differ" % (os.path.basename(old_jar), os.path.basename(jar), same, len(diffs)))
    got = dict((k, sorted(set(x.split("(")[0] for x in v))) for k, v in diffs.items())
    for k in sorted(got):
        print("   %-22s %s" % (k, ", ".join(got[k])))
    if expect is None:
        json.dump(got, open(os.path.join(os.path.dirname(SCRATCH), "expect53.dump.json"), "w"), indent=1, sort_keys=True)
        K.check(False, "C: no EXPECT yet - wrote expect53.dump.json next to the harness scratch (review it, then paste it as EXPECT)")
    else:
        K.eq(sorted(got), sorted(expect), "C: the classes that differ")
        for k in sorted(expect):
            K.eq(got.get(k, []), sorted(expect[k]), "C: %s members" % k)
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    a_, c_, g_ = expected_nonclass(za, zb)
    K.check(not g_ and all(gl1_name(n) for n in a_) and c_ == ["Server/Languages/en-US/server.lang", "manifest.json"],
            "C: non-class entries: only gl1 files added (%d), manifest.json + server.lang changed" % len(a_))
    K.notes.append("C: %d identical, changed: %s" % (same, got))
    K.save()


HK.run_compare = run_compare53


# ====================================================================================================== E: engine
def run_engine(out, jar, scratch, home):
    from jpype import JClass, JInt, JString, JImplements, JOverride, JObject, JArray, JLong, JDouble, JBoolean
    K = HK.Child(out)
    h211 = os.path.join(HERE, "test_skyygear_0.2.11.py")
    t = open(h211, encoding="utf-8").read()
    t = t[:t.index("def run_engine(out):")]
    esc = os.path.join(scratch, "eng")
    os.makedirs(esc, exist_ok=True)
    argv0 = sys.argv
    sys.argv = [h211, "--jar", jar, "--dir", esc]
    H = {"__name__": "skyygear_h211_lib", "__file__": h211, "__builtins__": __builtins__}
    exec(compile(t, h211 + " (engine boot, library)", "exec"), H)
    sys.argv = argv0
    H.update({"JAR": jar, "SCRATCH": esc, "VERSION": VERSION})
    H["_jvm"]([B.SERVER_JAR, B.JAVASSIST, jar], verify=True, big=True)

    class KC(object):
        def __init__(self, k):
            self.k = k
            self.notes = k.notes

        def check(self, c, w):
            return self.k.check(c, "E boot: " + w)
    E = H["engine_boot"](KC(K))
    ITEM = E["ITEM"]
    CRR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    AL = JClass("java.util.ArrayList")
    lst = AL()
    for it in list(ITEM.getAssetMap().getAssetMap().values()):
        if it is not None and it.hasRecipesToGenerate():
            it.collectRecipesToGenerate(lst)
    if lst.size() > 0:
        CRR.getAssetStore().loadAssets("Hytale:Hytale", lst)
    P = lambda n: JClass(PKG + n)
    Cfg, Gear, Data, Roll, View, Defs, Aug, Ut, UtFx, Pool, Pack, Lvl, Sm = (P("GearCfg"), P("Gear"), P("GearData"), P("GearRoll"), P("GearView"),
                                                                           P("GearDefs"), P("GearAug"), P("GearUt"), P("GearUtFx"), P("GearPool"),
                                                                           P("GearPack"), P("GearLevel"), P("GearSmith"))
    Props = JClass("java.util.Properties")
    UUID = JClass("java.util.UUID")
    Paths = JClass("java.nio.file.Paths")
    BA = JClass("org.bson.BsonArray")
    BS = JClass("org.bson.BsonString")
    SysJ = JClass("java.lang.System")
    u = UUID.fromString(U)
    sysp = SysJ.getProperties()
    br = sysp.get("skyy.bridge")
    if br is None:
        br = JClass("java.util.concurrent.ConcurrentHashMap")()
        sysp.put("skyy.bridge", br)
    data = os.path.join(scratch, "data")
    os.makedirs(data, exist_ok=True)
    Cfg.DIR = Paths.get(data)
    fresh = str(Cfg.defaultsText())

    def apply(**kv):
        p = Props()
        p.load(JClass("java.io.StringReader")(fresh))
        for k, v in kv.items():
            p.setProperty(k.replace("__", "."), v)
        Cfg.apply(p, False)
    BASE = {"part__gate": "false"}
    apply(**BASE)

    # ================================================================================== V the items + recipes in the real stores
    miss = [i for i in COPIES if Gear.item(JString(i)) is None]
    K.check(not miss, "V the 9 copies are in the real Item store: missing %s" % miss)
    pk = []
    for i in COPIES:
        it = ITEM.getAssetMap().getAsset(JString(i))
        try:
            pk.append(it.toPacket() is not None and int(it.getMaxStack()) == 1)
        except Exception as ex:
            pk.append(str(ex)[:120])
    K.check(all(x is True for x in pk), "V every copy makes a packet (MaxStack 1): %s" % pk)
    K.check(Gear.item(JString("Weapon_Staff_UT_Doomcaller")) is None, "V the SkyyArmory row has no item in this jar (SkyyArmory builds it)")
    rmiss = []
    for o_, rid in zip(OUTS, RIDS):
        rc = CRR.getAssetMap().getAsset(JString(rid))
        if rc is None or str(rc.getPrimaryOutput().getItemId()) != o_:
            rmiss.append(rid)
    K.check(not rmiss, "V the 11 recipes are in the real CraftingRecipe store with their output: missing %s" % rmiss)
    oth = []
    for rc in list(CRR.getAssetMap().getAssetMap().values()):
        po = rc.getPrimaryOutput() if rc is not None else None
        if po is not None and str(po.getItemId()) in OUTS and not str(rc.getId()).startswith("SkyyGear_Recipe_"):
            oth.append(str(rc.getId()))
    K.check(not oth, "V no other recipe makes a Bronze weapon / plain spear (one recipe each): %s" % oth)
    ours = [m for lv, m in E["rec"] if lv in ("SEVERE", "WARNING") and (any(i in m for i in COPIES) or any(r in m for r in RIDS) or "SkyyGear/UT/" in m)]
    allm = set(m for lv, m in E["rec"]) | set(r_[1] for r_ in E.get("vrec", []))          # vrec = the vanilla pack's own load
    base = dict((r[0], r[5]) for r in UTV.rows())
    same = [m for m in ours if any(i in m and m.replace(i, base[i]) in allm for i in COPIES)]          # the bare boot's own noise: the vanilla base says the same
    K.notes.append("V %d SEVERE / WARNING lines name a copy; %d of them are said word for word for its vanilla base too (the bare boot's missing parents)" % (len(ours), len(same)))
    ours = [m for m in ours if m not in same]
    K.check(not ours and set(E["fail"]) <= set(E["vfail"]), "V no SEVERE / WARNING about the gl1 files (failed stores %s, vanilla's %s): %s" % (list(E["fail"]), list(E["vfail"]), ours[:3]))

    # ================================================================================== B the Bronze rung + spears
    bb = []
    for o_ in OUTS:
        if not bool(Pack.combatId(JString(o_))):
            bb.append((o_, "combatId"))
    bands = dict((o_, [int(x) for x in Lvl.band(JString(o_))][:2]) for o_ in BZ)
    if any(v != [15, 23] for v in bands.values()):
        bb.append(("Bronze band", bands))
    fut = "Weapon_Axe_Bronze_SkyWynn"
    if not bool(Pack.combatId(JString(fut))):
        bb.append((fut, "combatId"))
    pid = [str(x) for x in Pool.P_ID]
    pdrop = [bool(x) for x in Pool.P_DROP]
    for o_ in OUTS:
        if o_ not in pid or pdrop[pid.index(o_)]:
            bb.append((o_, "pool: present and crafted (not drop-only)", o_ in pid))
    if not bool(Ut.crafted(JString("Weapon_Sword_Bronze"))) or not bool(Ut.crafted(JString("Weapon_Spear_Iron"))):
        bb.append("GearUt.crafted: the rung is craftable (never Untiered)")
    why = Pack.benchWhy(CRR.getAssetMap().getAsset(JString(RIDS[0])), JString(BZ[0]))
    K.notes.append("B bench veto without SkyySacks' craft bridges: %r; offBench %s" % (None if why is None else str(why), bool(Pack.offBench(JString(BZ[0])))))
    lv = {"Smithing": 50, "Swordsmanship": 30}

    @JImplements("java.util.function.Function")
    class Skill(object):
        @JOverride
        def apply(self, a):
            return JInt(lv.get(str(a[1]), 0))
    br.put("skill:fn:level", Skill())
    br.put("class:list", "Warrior:Swordsmanship,Mage:Arcana,Archer:Archery,Assassin:Stealth")
    br.put("class:skill:" + U, "Swordsmanship")
    cats = {}
    for c in range(0, 8):
        try:
            gs = Sm.groups(u, JInt(c), True)
        except Exception:
            continue
        for gr in gs:
            for x in gr[1]:
                if str(x) in OUTS:
                    cats.setdefault(str(x), (c, str(gr[0]), int(gr[3])))
    K.notes.append("B Smithing cards of the rung: %s" % cats)
    if sorted(cats) != sorted(OUTS):
        bb.append(("Smithing lists every rung piece", sorted(set(OUTS) - set(cats))))
    wc = [cats[o_][0] for o_ in OUTS if o_ in cats]
    if len(set(wc)) != 1:
        bb.append(("one Smithing category (Weapons)", set(wc)))
    else:
        gs = Sm.groups(u, JInt(wc[0]), True)
        los = [int(gr[3]) for gr in gs]
        if los != sorted(los):
            bb.append(("Weapons cards sorted by tier", los))
        sw = [(int(gr[3]), [str(x) for x in gr[1]]) for gr in gs if any(str(x) in ("Weapon_Sword_Iron", "Weapon_Sword_Bronze", "Weapon_Sword_Thorium") for x in gr[1])]
        K.notes.append("B sword cards (level, pieces): %s" % sw)
    K.check(not bb, "B the Bronze rung + spears: combatId, Bronze band 15-23, in the pool as crafted pieces (CRAFTED, never Untiered), every piece on ONE "
            "Smithing category sorted by tier; a future SkyyArmory Weapon_Axe_Bronze_SkyWynn is a plain piece too: %s" % bb)

    # ================================================================================== U the Untiered rows
    ubad = []
    for r in UTV.rows():
        b_ = Ut.band(JString(r[0]))
        if r[4] == "gear":
            if not bool(Ut.has(JString(r[0]))) or b_ is None or [int(x) for x in b_] != list(UTV.ZONE_BAND[r[3]]) or str(Ut.note(JString(r[0]))) != r[9]:
                ubad.append((r[0], "has / band / note", None if b_ is None else list(b_)))
    rw = UtFx.row(JString("Weapon_Daggers_UT_BarrowFangs"))
    tk = [float(x) for x in rw[2]] if rw is not None else None
    if tk is None or tk[int(UtFx.T_TGTFULL)] != 40.0 or tk[int(UtFx.T_TGTLOW)] != -20.0:
        ubad.append(("utfx row of Barrow Fangs", tk))
    rw2 = UtFx.row(JString("Weapon_Sword_UT_Silverbrand"))
    tk2 = [float(x) for x in rw2[2]] if rw2 is not None else None
    if tk2 is None or tk2[int(UtFx.T_FRONT)] != 25.0 or tk2[int(UtFx.T_BACK)] != -20.0:
        ubad.append(("utfx row of Silverbrand", tk2))
    tyk = [str(x) for x in Pool.T_KEY]
    seen = {}
    for r in UTV.rows():
        if r[4] != "gear":
            continue
        ty = tyk.index(r[0].split("_UT_")[0])
        L = UTV.ZONE_BAND[r[3]][1] - 1
        n_ = int(Ut.rowsOf(JInt(ty), JInt(L)))
        got = set(str(Ut.pickItem(JInt(ty), JInt(L))) for _x in range(200))
        seen[r[0]] = (n_, r[0] in got)
        if n_ < 1 or r[0] not in got:
            ubad.append((r[0], "orange bag pick at Lv %d" % L, n_, sorted(got)[:4]))
    K.notes.append("U orange-bag picks (rows at the level, picked in 200 tries): %s" % seen)
    dc = Roll.newDoc(JString("Weapon_Daggers_UT_BarrowFangs"), JInt(int(Defs.R_UT)), True, JString("admin"), JInt(15))
    txt, col = AL(), AL()
    View.lines(JString("Weapon_Daggers_UT_BarrowFangs"), dc, u, txt, col)
    tl = [str(x) for x in txt]
    K.notes.append("U Barrow Fangs tooltip: %s" % [x.replace(chr(2), "|") for x in tl])
    zl = zipfile.ZipFile(jar).read("Server/Languages/en-US/server.lang").decode("utf-8")
    tags = []
    for r in UTV.rows():
        if r[4] != "gear":
            continue
        ds = [l.split(" = ", 1)[1] for l in zl.splitlines() if l.startswith("items.%s.description = " % r[0])][0]
        tags.append(str(View.topTag(JString(r[0]), JInt(0), JString(ds))) == ALLOY_TAG[r[3]])
    if not all(tags):
        ubad.append(("the header tag with the real description = the zone alloy", tags))
    if not any(UTV.rows()[0][9][:30] in x.replace(chr(2), " ") for x in tl):
        ubad.append(("tooltip: the orange trade-off line", tl))
    if str(dc.get("r").asString().getValue()) != str(Defs.R_ID[int(Defs.R_UT)]):
        ubad.append(("the document is Untiered", str(dc.get("r"))))
    K.check(not ubad, "U the 9 copies: GearUt.has / band (zone end) / note (the orange trade-off line), the utfx tricks (Barrow Fangs tgtfull +40 / tgtlow -20, "
            "Silverbrand front +25 / back -20), the orange-bag pick at the zone levels, a REAL tooltip: %s" % ubad)

    # ================================================================================== P the pool + the Void Scythe
    pbad = []
    for i in UTV.LOOKS:
        if i in pid:
            pbad.append((i, "a UT look in the pool"))
    if UTV.ARMORY_LOOKS != ["Weapon_Staff_Doomed"] or [i for i in UTV.ARMORY_LOOKS if i not in pid]:          # gl1fix: no copy yet = still drops
        pbad.append(("an armory-row look (Doomed staff) left the pool before SkyyArmory ships its copy", UTV.ARMORY_LOOKS))
    dv = [i for i in pid if i.startswith("Armor_Diving_Crude_")]
    if dv:
        pbad.append(("Crude Diving in the pool", dv))
    if not [i for i in pid if i.startswith("Armor_Wool_")]:
        pbad.append("Armor_Wool_* left the pool (should stay)")
    if [i for i in pid if i.startswith("Weapon_Shortbow_") and i.split("_", 2)[2] in ("Combat", "Bomb", "Pull", "Ricochet", "Vampire", "Test_Zoom")]:
        pbad.append("a dev bow is in the pool")
    if not bool(UtFx.mythicId(JString(SCYTHE))) or str(Cfg.MYTH_IDS) != MYTH_NEW:
        pbad.append(("mythicId / the default list", str(Cfg.MYTH_IDS)))
    lg = Data.legacy(JString(SCYTHE))
    if str(lg.get("r").asString().getValue()) != str(Defs.R_ID[int(Defs.R_MY)]):
        pbad.append(("legacy Void Scythe = Mythic", str(lg.get("r"))))
    tb = Pool.table()
    if SCYTHE in pid and bool(tb[2][pid.index(SCYTHE)]):
        pbad.append("the Void Scythe is a live pool candidate")
    apply(gear__mythicItems=MYTH_OLD, **BASE)
    m_old = bool(UtFx.mythicId(JString(SCYTHE)))
    apply(**BASE)
    if m_old:
        pbad.append("an admin list without it = not Mythic")
    K.check(not pbad, "P the 10 looks + Crude Diving out of the bags (Wool + the dev-bow rule unchanged); the Void Scythe: in gear.mythicItems, legacy Mythic, "
            "never a pool candidate, follows an admin list: %s" % pbad)

    # ================================================================================== T the ELEMENT POWER line = power()
    tbad = []
    sw = "Weapon_Sword_Iron"

    def doc(iid, r=0, lv_=15, aug=None, mods=()):
        d_ = Roll.newDoc(JString(iid), JInt(r), True, JString("admin"), JInt(lv_))
        d_.put("r", BS(Defs.R_ID[r]))
        ar_ = BA()
        for k_, v_ in mods:
            ar_.add(Data.mod(JString(k_), JInt(v_)))
        d_.put("mods", ar_)
        if aug is not None:
            a_ = BA()
            for x_ in aug:
                a_.add(BS(JString(x_)))
            d_.put("aug", a_)
        return d_
    cases = [doc(sw, r=4, aug=["E:Fire:7", "E:Earth:2"], mods=[("fFire", 2)]), doc(sw, r=5, aug=["E:Air:4"], mods=[("rElem", 1), ("fWater", 1)]),
             doc(sw, r=2, aug=[""], mods=[("fThunder", 3)])]
    ELN = ["Earth", "Thunder", "Water", "Fire", "Air"]
    for d_ in cases:
        txt, col = AL(), AL()
        View.lines(JString(sw), d_, u, txt, col)
        tl = [str(x) for x in txt]
        pw = [int(x) for x in Aug.power(JString(sw), d_, Aug.weap(JString(sw), d_), JInt(-1))]
        want = "ELEMENT POWER" + "".join(chr(2) + "  " + ELN[x] + " " + str(pw[x]) for x in range(5) if pw[x] > 0)
        ep = [x for x in tl if x.startswith("ELEMENT POWER")]
        if ep != [want] or tl[tl.index(ep[0]) + 1] != "Imbue adds +5 Power to its element while it runs.":
            tbad.append((pw, ep, tl[tl.index(ep[0]) + 1] if ep else None))
    txt, col = AL(), AL()
    View.lines(JString(sw), doc(sw, r=4, aug=["S:Brute:3"]), u, txt, col)
    tl0 = [str(x) for x in txt]
    if [x for x in tl0 if x.startswith("ELEMENT POWER") or x.startswith("Imbue adds")]:
        tbad.append(("no power = no line, no note", tl0[-5:]))
    K.notes.append("T ELEMENT POWER lines: %s" % [(int(Aug.power(JString(sw), d_, Aug.weap(JString(sw), d_), JInt(-1))[3])) for d_ in cases])
    K.check(not tbad, "T the ELEMENT POWER line = GearAug.power() exactly (socketed tiers + 3 a rolled line, Raw Elemental on every element) with the Imbue note "
            "under it; no power = neither: %s" % tbad)

    # ================================================================================== M the two one-time updates
    mb = []
    lines = fresh.split("\n")
    u53_head = str(Cfg.U53_HEAD)
    i0 = lines.index(u53_head)
    n53 = 2 + 3 + 30
    old_lines = lines[:i0 - 1] + lines[i0 + n53:]
    old_lines = [l for l in old_lines if str(Cfg.H53_MARK_ID) not in l]
    old_lines = [("gear.mythicItems=" + MYTH_OLD) if l.startswith("gear.mythicItems=") else l for l in old_lines]
    old = "\n".join(old_lines)
    if str(Cfg.U53_MARK_ID) in old or str(Cfg.H53_MARK_ID) in old or "ut.Weapon_Daggers_UT_BarrowFangs" in old:
        mb.append("the simulated 0.3.52 file still holds 0.3.53 lines")
    r1 = Cfg.u53Update(JString(old))
    t1 = str(r1[0])
    rows1 = [str(x) for x in r1[3]]
    p1 = Props()
    p1.load(JClass("java.io.StringReader")(t1))
    if len(rows1) != 60 or str(r1[2]).count(",") != 29 or any(str(p1.getProperty("ut." + r[0])) != "%d,%d,%s" % (UTV.ZONE_BAND[r[3]] + (r[9],)) for r in UTV.rows()) \
            or not t1.startswith(old) or Cfg.u53Update(JString(t1)) is not None:
        mb.append(("u53Update: 30 rows appended once, second run null", len(rows1)))
    p3 = old.replace("\nutline.power=70", "\nutline.power=80")
    r3 = Cfg.u53Update(JString(p3)) if p3 != old else None
    if r3 is None or len([x for x in r3[3]]) != 40 or not any("kept (an admin's value)" in str(x) for x in r3[1]) or "utpow.Weapon_Daggers_UT_BarrowFangs" in str(r3[0]):
        mb.append(("an admin utline.power: no utpow rows + a note", None if r3 is None else len(list(r3[3]))))
    old_with = old.replace("ut.Weapon_Shortbow_UT_Bonewhistle=", "ut.Weapon_Daggers_UT_BarrowFangs=1,9,admin line\nut.Weapon_Shortbow_UT_Bonewhistle=")
    r4 = Cfg.u53Update(JString(old_with))
    if r4 is None or not any("ut.Weapon_Daggers_UT_BarrowFangs is already in the file - kept" in str(x) for x in r4[1]) or str(r4[0]).count("ut.Weapon_Daggers_UT_BarrowFangs=") != 1:
        mb.append("u53Update keeps a row an admin already added (never doubled)")
    crlf = old.replace("\n", "\r\n")
    r5 = Cfg.u53Update(JString(crlf))
    if r5 is None or "\n" in str(r5[0]).replace("\r\n", ""):
        mb.append("u53Update keeps CRLF")
    h1 = Cfg.h53Update(JString(old))
    p2 = Props()
    p2.load(JClass("java.io.StringReader")(str(h1[0])))
    if str(p2.getProperty("gear.mythicItems")) != MYTH_NEW or [str(x) for x in h1[3]] != ["gear.mythicItems", MYTH_OLD, MYTH_NEW] or Cfg.h53Update(JString(str(h1[0]))) is not None \
            or str(h1[0]).count(str(Cfg.H53_MARK_ID)) != 1:
        mb.append(("h53Update: the untouched line rewritten + the marker, second run null", [str(x) for x in h1[3]]))
    adm = old.replace("gear.mythicItems=" + MYTH_OLD, "gear.mythicItems=Weapon_Shortbow_Vampire")
    h2 = Cfg.h53Update(JString(adm))
    p4 = Props()
    p4.load(JClass("java.io.StringReader")(str(h2[0])))
    if str(p4.getProperty("gear.mythicItems")) != "Weapon_Shortbow_Vampire" or list(h2[3]) or not any("kept" in str(x) for x in h2[2]):
        mb.append(("an admin Mythic list kept + noted", [str(x) for x in h2[2]]))
    hf = Cfg.h53Update(JString(fresh))
    uf = Cfg.u53Update(JString(fresh))
    if hf is not None or uf is not None:
        mb.append("a fresh 0.3.53 file carries both markers (no update)")
    # on a REAL scratch file: the History copy first, the change log, the second start
    mdir = os.path.join(scratch, "mig", "Skyy_SkyyGear")
    os.makedirs(mdir, exist_ok=True)
    fpath = os.path.join(mdir, "config.properties")
    open(fpath, "wb").write(old.encode("latin-1"))
    Cfg.FILE = Paths.get(fpath)
    Cfg.DIR = Paths.get(mdir)
    s1 = str(Cfg.migrateUt53()) + "\n" + str(Cfg.migrateMy53())
    b1 = open(fpath, "rb").read()
    s2 = str(Cfg.migrateUt53()) + str(Cfg.migrateMy53())
    b2 = open(fpath, "rb").read()
    hist = []
    for dp, dn, fn in os.walk(mdir):
        hist += [os.path.join(dp, f) for f in fn if f != "config.properties"]
    tx = b1.decode("latin-1")
    if "ut.Weapon_Sword_UT_Silverbrand=52,60," not in tx or ("gear.mythicItems=" + MYTH_NEW) not in tx or s2 != "" or b1 != b2 or not hist \
            or not any(old.encode("latin-1") == open(h, "rb").read() for h in hist if os.path.getsize(h) == len(old.encode("latin-1"))):
        mb.append(("migrateUt53 / migrateMy53 on a real file", s1[:200], s2[:80], [os.path.relpath(h, mdir) for h in hist][:6]))
    K.notes.append("M real file: %s; history / log files %s" % (s1.replace("\n", " | ")[:500], [os.path.relpath(h, mdir) for h in hist][:8]))
    K.check(not mb, "M the one-time updates: u53Update (30 rows once, admin utline.power = no utpow, an admin row kept, CRLF kept), h53Update (only the untouched "
            "0.3.52 line, an admin list kept + noted), a fresh file untouched; on a real file: the old file in config-history first, the second start "
            "changes nothing: %s" % mb)
    Cfg.FILE = None
    K.save()


# ====================================================================================================== D: start twice on the live copy
def run_live(out, jar, scratch, home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg = JClass(PKG + "GearCfg")
    fc = os.path.join(home, "config.properties")
    c0 = open(fc, "rb").read() if os.path.isfile(fc) else None
    K.check(c0 is not None, "D the live copy has a config.properties")
    Paths = JClass("java.nio.file.Paths")
    Cfg.FILE = Paths.get(fc)
    Cfg.DIR = Paths.get(home)
    MIG = ["migrate0326", "migrate0330", "migrateP4", "migrateP5", "migrateP6", "migrateP7", "migrate39", "migrateUt28", "migrateCan2", "migrateAs51",
           "migrateUt53", "migrateMy53"]
    m0 = "\n".join(str(getattr(Cfg, x)()) for x in MIG if hasattr(Cfg, x))
    Cfg.load()
    c1 = open(fc, "rb").read()
    m1 = "".join(str(getattr(Cfg, x)()) for x in MIG if hasattr(Cfg, x))
    Cfg.load()
    K.notes.append("D start 1: one-time updates said %r" % m0[:900])
    K.check(open(fc, "rb").read() == c1 and m1 == "", "D start 2 changes nothing")
    t1 = c1.decode("latin-1")
    K.check(all(("ut.%s=%d,%d," % ((r[0],) + UTV.ZONE_BAND[r[3]])) in t1 and ("utfx.%s=" % r[0]) in t1 for r in UTV.rows()) and str(Cfg.U53_MARK_ID) in t1,
            "D the live copy got the 10 ut / utfx rows + the gl1 marker")
    myl = [l for l in t1.splitlines() if l.startswith("gear.mythicItems=")]
    K.check((myl == ["gear.mythicItems=" + MYTH_NEW] or (myl and myl[-1] != "gear.mythicItems=" + MYTH_OLD)) and str(Cfg.H53_MARK_ID) in t1,
            "D gear.mythicItems: the untouched line now holds the Void Scythe (an admin list would be kept): %s" % myl)
    K.check(bool(JClass(PKG + "GearUtFx").mythicId(JString(SCYTHE))) == (myl == ["gear.mythicItems=" + MYTH_NEW]), "D the loaded config reads the Mythic list")
    dl = c0.decode("latin-1").splitlines()
    dn = t1.splitlines()
    extra = [l for l in dn if l not in dl]
    allowed = lambda l: (l.strip() == "" or l.startswith(("ut.", "utfx.", "utpow.", "gear.mythicItems=", "stats.as=", "# ---- ")) or "SkyyGear 0.3.5" in l)
    K.check(all(allowed(l) for l in extra), "D only the gl1 rows, the Mythic line, the markers (and the older 0.3.5x updates) touch the file: %s" % [l for l in extra if not allowed(l)][:5])
    gone = [l for l in dl if l not in dn and not l.startswith(("gear.mythicItems=", "stats.as="))]
    K.check(not gone, "D no other line changed or vanished: %s" % gone[:5])
    K.save()


HK.run("SkyyGear", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("engine", run_engine), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyGear"))
