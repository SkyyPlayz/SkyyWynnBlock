"""Bare-JVM check for SkyyCooking 0.1.3 (campfire XP share 0.5 -> 0.25 + the one-time cooking.properties update), kept next to the build
so the build report's claims can be re-run.

    python SkyyCooking/test_skyycooking_0.1.3.py [--jar <0.1.3 jar>] [--old <0.1.2 jar>] [--live <cooking.properties>] [--dir <scratch>] [--keep]

Build first (python SkyyCooking/build_skyycooking_0.1.3.py). The parent copies the live cooking.properties (READ ONLY; default: the
"HUD mod" world's mods/Skyy_SkyyCooking/cooking.properties) into the scratch folder and starts a child: a fresh JVM (the game's JRE,
-Xverify:all, -XX:-UsePerfData, HytaleServer.jar + the 0.1.3 jar + tools/javassist.jar, java.io.tmpdir / TEMP / TMP in the scratch folder).
Checks:
  A  every 0.1.3 class loads and verifies (-Xverify:all)
  B  the default: row campfire.xpFactor ("Campfire XP share", dec 0-1, default 0.25, help "0.25 = a quarter"), CookCfg.DEF_CAMP_XP /
     CAMP_XP, the generated default text (campfire.xpFactor=0.25 with the marker right above its help line) and the block a 0.1 file gets
     appended; the loader: missing line / junk -> 0.25, 0.6 kept, 1.5 clamped to 1 (as before), the buff share untouched (0.75)
  C  XP maths through the COMPILED campfire path (Cook.campfire and the bridge Function cook:fn:campfire, with a fake Campfire recipe in
     the CraftingRecipe asset map, fake skill:fn:level / skill:fn:addxp): Cooked Wildmeat 1 -> 400 (1,600 x 0.25), 2 -> 800, 64 ->
     25,600, Grilled Fish 1 -> 500, Roast Vegetable 1 -> 300; preview pays nothing; the 0.1.2 share 0.5 on the same (byte-identical, see F)
     code pays 800 = twice as much; share 1.0 -> 1,600; xpMultiplier 2 -> 800; the bench XP table is unchanged (1,600); /cooking-style
     percent text "25%", the Skills Stats line "25% of the XP", cook:fn:campfactors -> [0.75, 0.25, true]
  D  the one-time update CookMig.migrate on scratch COPIES: (a) the live file (exact bytes: one value line + the marker, History copy = the
     old bytes + index line, one config-changes.log line in the kit format, the INFO line printed, the loader reads 0.25), (b) a second
     start changes nothing, (c) a hand-edited value (0.35) kept + noted, marker added, no change-log line, (d) CRLF kept, (e) no file ->
     nothing written, the loader's fresh 0.1.3 file is marked + 0.25 and never updates, (f) a 0.1 file without campfire lines is left
     to the loader (marked 0.1.3 block appended, 0.25), (g) no xpFactor line but a buffFactor line -> marker only, (h) already 0.25 ->
     marker only, silent, (i) History blocked -> WARN, file untouched, then updated once it can be kept; a folder in place of the file ->
     nothing written, (j) the whole start with the config kit (migrate -> load -> CfgPub.start): config:fn get = 0.25, the log op lists
     the update line (status ok = Undo offered), versions lists the History copy, restore preview of it shows the value going back,
     a set back to 0.5 (the Undo / Server Setup path) writes the line, keeps the marker, reaches the running field, and survives the
     next start (no second update)
  E  the pure text step CookMig.update on 3000 random files checked against java.util.Properties (only campfire.xpFactor may change,
     only from a 0.5 one-line last entry to 0.25; every other line byte for byte incl. CR; the marker is a comment; runs once)
  F  class byte-compare 0.1.2 vs 0.1.3 (normalised per-member disassembly + constant values): only CookCfg (the default + the default
     text), the new CookMig, the plugin's setup (the migrate call + version) and the config kit classes (kit 1.0 -> 1.1) differ; assets
     differ only in manifest.json; setup() order CookMig.migrate -> CookCfg.load -> CfgPub.start (bytecode)
Not testable without the game (UNVERIFIED): the chat lines on a client, SkyySkills adding the XP (its Wisdom bonus on top), the Server
Setup page drawing the Changes / History rows (SkyyMenu), a real Undo click (the harness sends the same set op with via console, because
the bare JVM has no permission module for a player UUID).
Nothing is deployed and nothing under AppData is written. Default scratch folder tools/dev/scratch/campxp/cook (deleted unless --keep).
Exit code 1 on any failure.
"""
import os, sys, re, shutil, subprocess, zipfile, json, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD = "0.1.3", "0.1.2"
PKG = "com.skyy.cooking."
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE_DEFAULT = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyCooking", "cooking.properties")
DEPLOYED = os.path.join(APPDATA, "Hytale", "UserData", "Mods", "SkyyCooking.jar")


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "campxp", "cook")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyCooking-%s.jar" % VERSION)))
OLDJAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyCooking-%s.jar" % OLD)))
LIVE = os.path.abspath(arg("--live", LIVE_DEFAULT))
KEEP = "--keep" in sys.argv

FAILS = []
OKS = [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


MARK = ("# SkyyCooking 0.1.3 campfire XP (Skyy 2026-10-01): campfire accessory dishes pay a quarter of the Cooking Bench XP - "
        "campfire.xpFactor default 0.25, was 0.5")
XP_HELP = "# campfire.xpFactor = share of the Cooking XP the same dish pays at a Cooking Bench (its xp.<dish> line). 0..1"
INFO_LIVE = ("cooking.properties updated to the 0.1.3 campfire XP share: campfire.xpFactor 0.5 -> 0.25 (Skyy 2026-10-01: campfire cooking "
             "pays half the XP it did; the old file is in config-history; Server Setup -> Changes can undo it)")
CAMP = {"Food_Wildmeat_Cooked": 1600, "Food_Fish_Grilled": 2000, "Food_Vegetable_Cooked": 1200}


def expected_update(text, new_value="0.25"):
    """the live shape: the marker on its own line right above the xpFactor help comment, the 0.5 value line -> 0.25, endings kept"""
    nl = "\r\n" if "\r\n" in text else "\n"
    out = text
    if new_value is not None:
        a_ = nl + "campfire.xpFactor=0.5" + nl
        assert out.count(a_) == 1
        out = out.replace(a_, nl + "campfire.xpFactor=" + new_value + nl)
    assert out.count(nl + XP_HELP + nl) == 1
    return out.replace(nl + XP_HELP + nl, nl + MARK + nl + XP_HELP + nl)


# ============================================================================================================== child
def run():
    import jpype
    import skyybuild as B
    from jpype import JClass, JArray, JObject, JImplements, JOverride, JString
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, JAR, B.JAVASSIST], convertStrings=True)
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()

    # ---------------- A. load + verify
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(JAR).namelist() if n.endswith(".class")]
    for n in names:
        try:
            Cls.forName(n, True, loader)
            OKS[0] += 1
        except Exception as e:
            FAILS.append("load " + n + ": " + str(e))
            print("LOAD FAIL", n, e)
    print("A. loaded + verified %d classes (-Xverify:all)" % len(names))
    if FAILS:
        return

    J = lambda n: JClass(PKG + n)
    Cfg, Cook, Mig, Rows, CfgPub = J("CookCfg"), J("Cook"), J("CookMig"), J("CfgRows"), J("CfgPub")
    Paths, Props, Integer, Long = JClass("java.nio.file.Paths"), JClass("java.util.Properties"), JClass("java.lang.Integer"), JClass("java.lang.Long")
    UUID, HashMap, CHM, System = JClass("java.util.UUID"), JClass("java.util.HashMap"), JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.lang.System")
    BAIS = JClass("java.io.ByteArrayInputStream")
    Bool = JClass("java.lang.Boolean")
    OA = JArray(JObject)
    bridge = CHM()
    System.getProperties().put("skyy.bridge", bridge)

    def jfield(cls, name):
        c = cls
        while c is not None:
            try:
                f = c.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                c = c.getSuperclass()
        raise KeyError(name)

    # ---------------- B. the default
    keys = [str(k) for k in Rows.KEYS]
    xi = keys.index("campfire.xpFactor") if "campfire.xpFactor" in keys else -1
    check(xi >= 0, "B: row campfire.xpFactor exists")
    if xi >= 0:
        check(str(Rows.LABELS[xi]) == "Campfire XP share" and str(Rows.TYPES[xi]) == "dec" and str(Rows.DEFS[xi]) == "0.25"
              and str(Rows.MINS[xi]) == "0" and str(Rows.MAXS[xi]) == "1" and str(Rows.CATS[xi]) == "campfire"
              and "live" in str(Rows.FLAGS[xi]).split(","), "B: row = Campfire XP share, dec 0-1, default 0.25, live, Campfire tab")
        check(str(Rows.HELPS[xi]) == "Share of the Cooking XP a campfire-accessory dish pays (0.25 = a quarter)." and len(str(Rows.HELPS[xi])) <= 100,
              "B: row help: " + str(Rows.HELPS[xi]))
        bi = keys.index("campfire.buffFactor")
        check(str(Rows.DEFS[bi]) == "0.75", "B: Campfire Grade share stays 0.75")
    check(str(Rows.VERSION) == VERSION and int(Rows.KEEP) == 20 and str(Rows.KIT) == "1.1", "B: kit version 1.1, KEEP 20, VERSION 0.1.3")
    check(abs(float(Cfg.DEF_CAMP_XP) - 0.25) < 1e-12 and abs(float(Cfg.CAMP_XP) - 0.25) < 1e-12 and abs(float(Cfg.DEF_CAMP_BUFF) - 0.75) < 1e-12,
          "B: CookCfg.DEF_CAMP_XP / CAMP_XP = 0.25, DEF_CAMP_BUFF 0.75")
    dflt = str(Cfg.DEFAULTS)
    check(dflt.startswith("# SkyyCooking 0.1.3 - cooking.properties") and dflt.count("\ncampfire.xpFactor=0.25\n") == 1
          and dflt.count("\n" + MARK + "\n" + XP_HELP + "\ncampfire.xpFactor=0.25\n") == 1 and "campfire.xpFactor=0.5" not in dflt,
          "B: default file: campfire.xpFactor=0.25 with the marker above its help line")
    blk = str(Cfg.CAMP_BLOCK)
    check(blk.startswith("\n# Campfire ACCESSORY") and blk.endswith("\n" + MARK + "\n" + XP_HELP + "\ncampfire.xpFactor=0.25\n"),
          "B: the 0.1 append block carries the marker + 0.25")
    bdir = os.path.join(SCRATCH, "work", "b-loader")
    os.makedirs(bdir)
    bf = os.path.join(bdir, "cooking.properties")
    Cfg.FILE = Paths.get(bf)
    base_txt = dflt.replace("campfire.xpFactor=0.25\n", "")
    for line, want, name in (("", 0.25, "missing line"), ("campfire.xpFactor=abc\n", 0.25, "junk"), ("campfire.xpFactor=0.6\n", 0.6, "0.6"),
                             ("campfire.xpFactor=1.5\n", 1.0, "1.5 clamped"), ("campfire.xpFactor=0.5\n", 0.5, "0.5 (a kept value)")):
        open(bf, "w", encoding="latin-1", newline="").write(base_txt + line)
        Cfg.load()
        check(abs(float(Cfg.CAMP_XP) - want) < 1e-12 and abs(float(Cfg.CAMP_BUFF) - 0.75) < 1e-12,
              "B: loader %s -> CAMP_XP %s (got %s), buff 0.75" % (name, want, float(Cfg.CAMP_XP)))
    print("B. default 0.25: row, fields, default text, append block, loader checked")

    # ---------------- C. XP maths through the compiled campfire path
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    DAM = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyTestFakeStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fake.addConstructor(JClass("javassist.CtNewConstructor").make(
        "public SkyyTestFakeStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
    FakeStore = fake.toClass(AS.class_)
    am_field = jfield(AS.class_, "assetMap")
    dam_field = jfield(DAM.class_, "assetMap")

    def fake_store(asset_cls, mapping):
        """asset_cls.ASSET_STORE = a never-constructed store whose DefaultAssetMap reads this java.util.HashMap"""
        st = us.allocateInstance(FakeStore)
        dm = DAM()
        hm = HashMap()
        for k_, v_ in mapping.items():
            hm.put(k_, v_)
        dam_field.set(dm, hm)
        am_field.set(st, dm)
        jfield(asset_cls.class_, "ASSET_STORE").set(None, st)

    CRR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    MQ = JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
    BRQ = JClass("com.hypixel.hytale.protocol.BenchRequirement")
    BTP = JClass("com.hypixel.hytale.protocol.BenchType")
    ITM = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    id_field = jfield(CRR.class_, "id")

    def recipe(rid, out, bench):
        r_ = CRR(JArray(MQ)([MQ("Food_Wildmeat_Raw", None, None, 1, None)]), MQ(out, None, None, 1, None), JArray(MQ)([MQ(out, None, None, 1, None)]),
                 1, JArray(BRQ)([BRQ(BTP.Crafting, bench, None, 0, None)]), 1.0, False, 0)
        id_field.set(r_, rid)
        return r_

    RID = dict((d, d + "_Recipe_Generated_0") for d in CAMP)
    recs = dict((RID[d], recipe(RID[d], d, "Campfire")) for d in CAMP)
    recs["Skyy_Cook_Recipe_Wildmeat"] = recipe("Skyy_Cook_Recipe_Wildmeat", "Food_Wildmeat_Cooked", "Cookingbench")
    fake_store(CRR, recs)
    items = {}
    for d in CAMP:
        for g in range(1, 13):
            items["Skyy_Cook_%s_G%d" % (d, g)] = us.allocateInstance(ITM.class_)
    fake_store(ITM, items)
    check(CRR.getAssetMap().getAsset(RID["Food_Wildmeat_Cooked"]) is not None and str(Cook.outId(CRR.getAssetMap().getAsset(RID["Food_Wildmeat_Cooked"]))) == "Food_Wildmeat_Cooked"
          and bool(Cook.isCampfire(CRR.getAssetMap().getAsset(RID["Food_Wildmeat_Cooked"]))), "C: fake Campfire recipe is in the asset map")

    calls = []

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, a):
            return self.f(a)

    level = [50]
    bridge.put("skill:fn:level", Fn(lambda a: Integer(level[0])))

    def addxp(a):
        calls.append((str(a[0]), str(a[1]), int(a[2].longValue()), str(a[3])))
        return Bool.TRUE
    bridge.put("skill:fn:addxp", Fn(addxp))
    cdir = os.path.join(SCRATCH, "work", "c-xp")
    os.makedirs(cdir)
    Cfg.FILE = Paths.get(os.path.join(cdir, "cooking.properties"))
    Cfg.load()                                   # a fresh 0.1.3 file: the XP table, graded dishes, CAMP_XP 0.25
    check(abs(float(Cfg.CAMP_XP) - 0.25) < 1e-12 and int(Cfg.xpFor("Food_Wildmeat_Cooked")) == 1600 and int(Cfg.xpFor("Food_Fish_Grilled")) == 2000
          and int(Cfg.xpFor("Food_Vegetable_Cooked")) == 1200, "C: fresh file: share 0.25, bench XP table unchanged (1,600 / 2,000 / 1,200)")
    U = UUID.fromString("00000000-0000-0000-0000-00000000c00c")

    def camp(dish, n, rid=None):
        del calls[:]
        r_ = Cook.campfire(U, rid or RID[dish], n, None, Bool.FALSE)
        Cook.RATE.clear()
        return r_, sum(c[2] for c in calls)

    for dish, n, want in (("Food_Wildmeat_Cooked", 1, 400), ("Food_Wildmeat_Cooked", 2, 800), ("Food_Wildmeat_Cooked", 64, 25600),
                          ("Food_Fish_Grilled", 1, 500), ("Food_Fish_Grilled", 3, 1500), ("Food_Vegetable_Cooked", 1, 300)):
        r_, sent = camp(dish, n)
        check(r_ is not None and int(r_[3]) == want and sent == want and calls and calls[0][1] == "Cooking"
              and calls[0][3] == "cook:campfire:" + dish,
              "C: %d x %s through the accessory pays %d Cooking XP (got %s / addxp %d)" % (n, dish, want, None if r_ is None else int(r_[3]), sent))
    r_, sent = camp("Food_Wildmeat_Cooked", 1)
    check(str(r_[0]) == "Skyy_Cook_Food_Wildmeat_Cooked_G4" and int(r_[1]) == 5 and int(r_[2]) == 4,
          "C: the Grade share is unchanged: Cooking 50 = bench Grade 5 -> campfire Grade 4 (%s)" % str(r_[0]))
    r_, sent = camp("Food_Wildmeat_Cooked", 0)
    check(r_ is not None and int(r_[3]) == 0 and sent == 0, "C: preview (0 crafts) pays nothing")
    del calls[:]
    got = bridge.get("cook:fn:campfire")
    check(got is None, "C: (cook:fn:campfire is only published by setup(); the harness calls the Function class directly)")
    fnc = J("CookCampFn")()
    gid = fnc.apply(OA([U, RID["Food_Wildmeat_Cooked"], Integer(1), None, Bool.FALSE]))
    Cook.RATE.clear()
    check(str(gid) == "Skyy_Cook_Food_Wildmeat_Cooked_G4" and sum(c[2] for c in calls) == 400,
          "C: the bridge Function cook:fn:campfire (SkyySacks' call) gives the graded dish and 400 XP for one wildmeat")
    r_, sent = camp("Food_Wildmeat_Cooked", 1, rid="Skyy_Cook_Recipe_Wildmeat")
    check(r_ is None and sent == 0, "C: a Cooking Bench recipe is still refused by the campfire path (full Grade + XP at the bench)")
    Cfg.CAMP_XP = 0.5
    r_, sent = camp("Food_Wildmeat_Cooked", 1)
    check(sent == 800, "C: the 0.1.2 share 0.5 on the same code pays 800 for one wildmeat - 0.1.3 pays half (400)")
    Cfg.CAMP_XP = 1.0
    r_, sent = camp("Food_Wildmeat_Cooked", 1)
    check(sent == 1600, "C: share 1.0 pays the full bench XP (1,600)")
    Cfg.CAMP_XP = 0.25
    Cfg.XP_MULT = 2.0
    r_, sent = camp("Food_Wildmeat_Cooked", 1)
    check(sent == 800, "C: xpMultiplier 2 doubles the quarter share (800)")
    Cfg.XP_MULT = 1.0
    check(str(Cook.pc(Cfg.CAMP_XP)) == "25%", "C: /cooking, the hint and /cookadmin campfire print 25%")
    st = J("CookStatsFn")().apply(OA([U, Integer(50), Bool.FALSE]))
    lines = [str(x) for x in st]
    check(any(l.startswith("Campfire accessory quick cook - Grade 4 food") and l.endswith(" - 25% of the XP") for l in lines),
          "C: Skills Stats line says 25%% of the XP: %s" % lines)
    cf = J("CookCampInfoFn")().apply(None)
    check(abs(float(cf[0]) - 0.75) < 1e-12 and abs(float(cf[1]) - 0.25) < 1e-12 and bool(cf[2]), "C: cook:fn:campfactors -> [0.75, 0.25, true]")
    print("C. XP maths: Cooked Wildmeat 1,600 -> 400 per campfire dish (0.1.2 share: 800), fish 500, vegetable 300, Grade share unchanged")

    # ---------------- D. the one-time update on scratch copies
    XD = os.path.join(SCRATCH, "work", "d-mig")

    def case(name, data):
        """<XD>/<name>/mods/Skyy_SkyyCooking/cooking.properties with these bytes (None = no file); CookCfg.FILE points there"""
        d_ = os.path.join(XD, name, "mods", "Skyy_SkyyCooking")
        os.makedirs(d_)
        f_ = os.path.join(d_, "cooking.properties")
        if data is not None:
            open(f_, "wb").write(data)
        Cfg.FILE = Paths.get(f_)
        return d_, f_

    def rb(p):
        return open(p, "rb").read()

    def baks(d_):
        hd = os.path.join(d_, "config-history")
        return sorted(x for x in os.listdir(hd) if x.endswith(".bak")) if os.path.isdir(hd) else []

    def lines_of(p):
        return [l for l in open(p, encoding="utf-8").read().split("\n") if l.strip()] if os.path.isfile(p) else []

    def idx(d_):
        return lines_of(os.path.join(d_, "config-history", "index.log"))

    def clog(d_):
        return lines_of(os.path.join(d_, "config-changes.log"))

    live_path = os.path.join(SCRATCH, "live", "cooking.properties")
    live = rb(live_path) if os.path.isfile(live_path) else None
    check(live is not None, "D: a scratch copy of the live cooking.properties exists (%s)" % LIVE)
    if live is not None:
        lt = live.decode("latin-1")
        check("\ncampfire.xpFactor=0.5\n" in lt and MARK not in lt, "D: the live file still holds campfire.xpFactor=0.5 (0.1.1 block, no marker)")
        # (a) the live file
        d, f = case("a-live", live)
        exp = expected_update(lt)
        res = str(Mig.migrate())
        got = rb(f)
        check(got == exp.encode("latin-1"), "D(a): live file -> exactly one value line 0.5 -> 0.25 + the marker above its help line, every other byte kept")
        check(res.split("\n") == [INFO_LIVE], "D(a): one INFO line: %r" % res)
        print("D. INFO line the live file produces: [SkyyCooking] " + res)
        b = baks(d)
        check(len(b) == 1 and b[0].startswith("Skyy_SkyyCooking~cooking.properties.") and rb(os.path.join(d, "config-history", b[0])) == live,
              "D(a): History keeps the old file (one .bak = the old bytes): %s" % b)
        ix = idx(d)
        check(len(ix) == 1 and ix[0].split("\t")[1] == "Skyy_SkyyCooking/cooking.properties"
              and ix[0].split("\t")[3:] == ["SkyyCooking 0.1.3", "before the 0.1.3 campfire XP update"], "D(a): index.log names the update: %s" % ix)
        cl = clog(d)
        check(len(cl) == 1 and cl[0].split("\t")[1:] == ["SkyyCooking 0.1.3", "-", "update", "campfire.xpFactor", "0.5", "0.25", "ok"]
              and re.match(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d$", cl[0].split("\t")[0]) is not None,
              "D(a): one config-changes.log line in the kit's format (an Undo-able ok line): %s" % cl)
        check(not os.path.exists(f + ".tmp"), "D(a): no temp file left")
        Cfg.load()
        check(abs(float(Cfg.CAMP_XP) - 0.25) < 1e-12 and abs(float(Cfg.CAMP_BUFF) - 0.75) < 1e-12, "D(a): the loader reads 0.25 (buff 0.75)")
        pl_old, pl_new = Props(), Props()
        pl_old.load(BAIS(live))
        pl_new.load(BAIS(got))
        diffk = sorted(str(k) for k in set(list(pl_old.stringPropertyNames()) + list(pl_new.stringPropertyNames()))
                       if pl_old.getProperty(k) != pl_new.getProperty(k))
        check(diffk == ["campfire.xpFactor"] and str(pl_new.getProperty("campfire.xpFactor")) == "0.25",
              "D(a): java.util.Properties sees exactly one changed key: %s" % diffk)
        # (b) a second start
        check(str(Mig.migrate()) == "" and rb(f) == got and len(baks(d)) == 1 and len(idx(d)) == 1 and len(clog(d)) == 1,
              "D(b): a second start changes nothing (file, History, change log)")
        # (c) a hand-edited value
        hand = lt.replace("\ncampfire.xpFactor=0.5\n", "\ncampfire.xpFactor=0.35\n")
        d, f = case("c-hand", hand.encode("latin-1"))
        res = str(Mig.migrate())
        check(rb(f) == expected_update(hand, None).encode("latin-1"), "D(c): hand-edited 0.35 kept, only the marker added")
        check(res.split("\n") == ["cooking.properties: campfire.xpFactor was changed by hand - kept, nothing changed (0.1.3 campfire XP marker added)",
                                  "campfire.xpFactor=0.35 kept (custom) - the 0.1.3 default is 0.25"], "D(c): INFO + kept note: %r" % res)
        check(len(baks(d)) == 1 and clog(d) == [], "D(c): History copy made, no change-log line (no value changed)")
        Cfg.load()
        check(abs(float(Cfg.CAMP_XP) - 0.35) < 1e-12, "D(c): the loader keeps 0.35")
        check(str(Mig.migrate()) == "" and len(baks(d)) == 1, "D(c): second start: nothing")
        for v in ("0.50", "1", " 0.5\\\n  ", "0.3"):
            hv = lt.replace("\ncampfire.xpFactor=0.5\n", "\ncampfire.xpFactor=%s\n" % v)
            r_ = Mig.update(hv)
            check(r_ is not None and str(r_[1]) == "" and str(r_[0]) == expected_update(hv, None), "D(c): value %r is kept (marker only)" % v)
        # (d) CRLF
        crlf = lt.replace("\n", "\r\n")
        d, f = case("d-crlf", crlf.encode("latin-1"))
        res = str(Mig.migrate())
        check(rb(f) == expected_update(crlf).encode("latin-1") and res == INFO_LIVE, "D(d): CRLF file -> same update, every CRLF kept")
        check(b"\n" not in rb(f).replace(b"\r\n", b""), "D(d): no bare LF introduced")
        # (e) no file
        d, f = case("e-nofile", None)
        check(str(Mig.migrate()) == "" and not os.path.exists(f) and not os.path.exists(os.path.join(d, "config-history")),
              "D(e): no file -> nothing written")
        Cfg.load()
        fresh = rb(f).decode("latin-1")
        check(MARK in fresh and "\ncampfire.xpFactor=0.25\n" in fresh and abs(float(Cfg.CAMP_XP) - 0.25) < 1e-12,
              "D(e): the loader's fresh 0.1.3 file is marked, 0.25")
        check(str(Mig.migrate()) == "" and rb(f).decode("latin-1") == fresh and not os.path.exists(os.path.join(d, "config-history")),
              "D(e): the fresh file never updates")
        # (f) a 0.1 file without campfire lines
        cut = lt.index("\n\n# Campfire ACCESSORY")
        v01 = lt[:cut + 1]
        d, f = case("f-v01", v01.encode("latin-1"))
        check(str(Mig.migrate()) == "" and rb(f) == v01.encode("latin-1") and baks(d) == [], "D(f): 0.1 file (no campfire line) left to the loader")
        Cfg.load()
        t1 = rb(f).decode("latin-1")
        check(t1 == v01 + str(Cfg.CAMP_BLOCK) and abs(float(Cfg.CAMP_XP) - 0.25) < 1e-12, "D(f): the loader appended the marked 0.1.3 block (0.25)")
        check(str(Mig.migrate()) == "" and rb(f).decode("latin-1") == t1, "D(f): then nothing to update")
        # (g) no xpFactor line, buffFactor present
        nox = lt.replace(XP_HELP + "\ncampfire.xpFactor=0.5\n", "")
        d, f = case("g-noxp", nox.encode("latin-1"))
        res = str(Mig.migrate())
        bh = "# <= 1 + buffFactor x"
        bline = [l for l in nox.split("\n") if l.startswith(bh)][0]
        check(rb(f).decode("latin-1") == nox.replace("\n" + bline + "\n", "\n" + MARK + "\n" + bline + "\n")
              and res == "cooking.properties: no campfire.xpFactor line (the default 0.25 applies) - nothing changed (0.1.3 campfire XP marker added)"
              and clog(d) == [], "D(g): no xpFactor line -> marker above the buffFactor help line, nothing else: %r" % res)
        Cfg.load()
        check(abs(float(Cfg.CAMP_XP) - 0.25) < 1e-12, "D(g): fallback 0.25")
        # (h) already 0.25 without the marker
        al = lt.replace("\ncampfire.xpFactor=0.5\n", "\ncampfire.xpFactor=0.25\n")
        d, f = case("h-already", al.encode("latin-1"))
        res = str(Mig.migrate())
        check(rb(f) == expected_update(al, None).encode("latin-1") and res == "cooking.properties: campfire.xpFactor is already 0.25 - nothing changed (0.1.3 campfire XP marker added)"
              and clog(d) == [], "D(h): already 0.25 -> marker only, silent: %r" % res)
        # (i) History blocked, then free; a folder in place of the file
        d, f = case("i-blocked", live)
        open(os.path.join(d, "config-history"), "w").write("not a folder")
        check(str(Mig.migrate()) == "" and rb(f) == live and clog(d) == [], "D(i): History cannot be kept -> WARN, file untouched, no log line")
        os.remove(os.path.join(d, "config-history"))
        check(str(Mig.migrate()) == INFO_LIVE and rb(f) == exp.encode("latin-1") and len(baks(d)) == 1 and len(clog(d)) == 1,
              "D(i): the next start updates once History can keep the old file")
        d, f = case("i-folder", None)
        os.makedirs(f)
        check(str(Mig.migrate()) == "" and os.path.isdir(f) and not os.path.exists(os.path.join(d, "config-history")),
              "D(i): a folder in place of the file -> nothing written")
        # (j) the whole start with the config kit
        d, f = case("j-kit", live)
        mods = os.path.dirname(d)
        res = str(Mig.migrate())
        Cfg.load()
        CfgPub.start(Paths.get(mods), None)
        fn = bridge.get("config:fn:SkyyCooking")
        check(fn is not None and str(fn.apply(OA(["get", "campfire.xpFactor"]))) == "0.25" and str(fn.apply(OA(["get", "campfire.buffFactor"]))) == "0.75",
              "D(j): config:fn:SkyyCooking get campfire.xpFactor = 0.25 after the start")
        st_ = fn.apply(OA(["status"]))
        check(st_ is not None and str(st_[0]) == "ok", "D(j): kit status ok (no hand edit seen: the update ran before the kit's first read): %s"
              % (None if st_ is None else [str(x) for x in st_]))
        lg = [str(x) for x in fn.apply(OA(["log", Integer(20)]))]
        check(len(lg) == 1 and lg[0].split("\t")[1:] == ["SkyyCooking 0.1.3", "-", "update", "campfire.xpFactor", "0.5", "0.25", "ok"],
              "D(j): the kit's log op (Server Setup -> Changes) lists the update line with status ok (Undo offered): %s" % lg)
        vs = [str(x) for x in fn.apply(OA(["versions"]))]
        check(len(vs) == 1 and vs[0].split("\t")[3:] == ["SkyyCooking 0.1.3", "before the 0.1.3 campfire XP update"],
              "D(j): the kit's versions op (Server Setup -> History) lists the copy: %s" % vs)
        pv = fn.apply(OA(["restore", vs[0].split("\t")[0], None, "console", "preview"])) if vs else None
        pvt = "" if pv is None else " | ".join(str(x) for x in pv)
        check(pv is not None and str(pv[0]) == "ok" and "Campfire XP share: 0.25 -> 0.5" in pvt,
              "D(j): restore preview of that copy = the value going back (values, through the kit's normal path): %s" % pvt.split("\n")[:2])
        r1 = fn.apply(OA(["set", "campfire.xpFactor", "0.5", None, "console", "yes", "console"]))
        CfgPub.flush()
        t2 = rb(f).decode("latin-1")
        check(r1 is not None and str(r1[0]) == "ok" and "\ncampfire.xpFactor=0.5\n" in t2 and MARK in t2 and abs(float(Cfg.CAMP_XP) - 0.5) < 1e-12,
              "D(j): set back to 0.5 (the Undo path): ok, line written, marker kept, the running share is 0.5 (%s)" % (None if r1 is None else str(r1[2])))
        check(t2 == exp.replace("\ncampfire.xpFactor=0.25\n", "\ncampfire.xpFactor=0.5\n"), "D(j): only the value line changed back")
        lg2 = [str(x) for x in fn.apply(OA(["log", Integer(20)]))]
        check(len(lg2) == 2 and lg2[0].split("\t")[4:] == ["campfire.xpFactor", "0.25", "0.5", "ok"], "D(j): the set back is logged: %s" % lg2[:1])
        try:
            CfgPub.shutdown()
        except Exception:
            pass
        check(str(Mig.migrate()) == "" and rb(f).decode("latin-1") == t2, "D(j): next start: no second update (0.5 set back is kept)")
        Cfg.load()
        check(abs(float(Cfg.CAMP_XP) - 0.5) < 1e-12, "D(j): next start reads 0.5")
    print("D. one-time update on scratch copies checked")

    # ---------------- E. random files vs java.util.Properties
    rnd = random.Random(20261001)
    KEYS = ["campfire.xpFactor"] * 5 + ["campfire.buffFactor"] * 2 + ["xp.default", "enabled", "campfire.xpFactorX", "Campfire.xpFactor",
                                                                      "campfire\\.xpFactor", " campfire.xpFactor"]
    SEPS = ["=", ":", " ", " = ", "\t=", "  :  ", "=  "]
    VALS = ["0.5"] * 6 + ["0.50", " 0.5", "0.5 ", "0.25", "0.3", "", "0.\\5", "abc", "0.5\\\\", "1"]
    COMS = ["# x", "!bang", "   # indented", "#campfire.xpFactor=0.5", "# campfire.xpFactor = share", "", "   ", "#", "\t! t"]
    stats = {"mig": 0, "kept": 0, "none": 0}
    for it_ in range(3000):
        lines_ = []
        for _n in range(rnd.randint(0, 9)):
            r0 = rnd.random()
            if r0 < 0.35:
                lines_.append(rnd.choice(COMS))
            else:
                k_ = rnd.choice(KEYS)
                v_ = rnd.choice(VALS)
                ln = rnd.choice(["", "  ", "\t"]) + k_ + rnd.choice(SEPS) + v_
                if rnd.random() < 0.12:
                    ln = ln + "\\"                                    # a continued entry
                    lines_.append(ln)
                    ln = rnd.choice(["  5", "  ", "0.5", "  # not a comment"])
                lines_.append(ln)
        if rnd.random() < 0.02:
            lines_.insert(rnd.randint(0, len(lines_)), "# SkyyCooking 0.1.3 campfire XP marker")
        eol = rnd.choice(["\n", "\r\n", "mix"])
        text = ""
        for i_, ln in enumerate(lines_):
            e_ = ("\n" if rnd.random() < 0.5 else "\r\n") if eol == "mix" else eol
            text += ln + (e_ if (i_ < len(lines_) - 1 or rnd.random() < 0.7) else "")
        r_ = Mig.update(text)
        po = Props()
        po.load(BAIS(text.encode("latin-1")))
        if r_ is None:
            stats["none"] += 1
            continue
        new = str(r_[0])
        pn = Props()
        pn.load(BAIS(new.encode("latin-1")))
        ko = sorted(str(k) for k in po.stringPropertyNames())
        kn = sorted(str(k) for k in pn.stringPropertyNames())
        others_same = ko == kn and all(str(po.getProperty(k)) == str(pn.getProperty(k)) for k in ko if k != "campfire.xpFactor")
        ov, nv = po.getProperty("campfire.xpFactor"), pn.getProperty("campfire.xpFactor")
        ov = None if ov is None else str(ov)
        nv = None if nv is None else str(nv)
        if str(r_[1]):
            stats["mig"] += 1
            ok = others_same and ov is not None and ov.strip() == "0.5" and nv == "0.25"
        else:
            stats["kept" if r_[2] is not None else "none"] += 1
            ok = others_same and ov == nv
        check(ok, "E%d: Properties: only campfire.xpFactor may change, 0.5 -> 0.25 (%r -> %r, chg %r)\n%r" % (it_, ov, nv, str(r_[1]), text))
        # byte for byte: drop the one marker line, then only xpFactor value lines may differ (CR kept)
        nl_ = new.split("\n")
        mi = [i for i, l in enumerate(nl_) if l.rstrip("\r") == MARK]
        check(len(mi) == 1, "E%d: exactly one marker line" % it_)
        if len(mi) == 1:
            rest = nl_[:mi[0]] + nl_[mi[0] + 1:]
            ol_ = text.split("\n")
            same_n = len(rest) == len(ol_)
            dif = [(a, b_) for a, b_ in zip(ol_, rest) if a != b_] if same_n else [("len", "len")]
            ok2 = same_n and all(a.endswith("\r") == b_.endswith("\r") and b_.rstrip("\r").endswith("0.25")
                                 and re.match(r"^[ \t]*campfire\\?\.xpFactor", a) is not None for a, b_ in dif)
            check(ok2, "E%d: only campfire.xpFactor value lines differ, CR kept: %r" % (it_, dif[:3]))
        check(Mig.update(new) is None, "E%d: runs once (the new text is never updated again)" % it_)
        if len(FAILS) > 20:
            break
    check(stats["mig"] > 300 and stats["kept"] > 100 and stats["none"] > 100, "E: the random set covers update / kept / untouched: %s" % stats)
    print("E. 3000 random files vs java.util.Properties: %s" % stats)

    # ---------------- F. class byte-compare 0.1.2 vs 0.1.3
    CP = JClass("javassist.ClassPool")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def members(jar, cname):
        cp = CP(False)
        cp.appendClassPath(jar)
        cp.appendClassPath(B.SERVER_JAR)
        cp.appendSystemPath()
        cc = cp.get(cname)
        cf = cc.getClassFile()
        out = {}
        for mi in cf.getMethods():
            key = str(mi.getName()) + str(mi.getDescriptor())
            code = mi.getCodeAttribute()
            lines = []
            if code is not None:
                it = code.iterator()
                while it.hasNext():
                    pos = it.next()
                    lines.append(re.sub(r"#\d+ = ", "", str(IP.instructionString(it, pos, cf.getConstPool()))))
            out["m " + key] = "\n".join(lines)
        for fi in cf.getFields():
            cv = int(fi.getConstantValue())
            val = str(cf.getConstPool().getLdcValue(cv)) if cv else ""
            out["f " + str(fi.getName())] = str(fi.getDescriptor()) + " " + str(fi.getAccessFlags()) + " " + val
            out["v " + str(fi.getName())] = val
        return out

    z2, z3 = zipfile.ZipFile(OLDJAR), zipfile.ZipFile(JAR)
    c2 = dict((n, z2.read(n)) for n in z2.namelist() if n.endswith(".class"))
    c3 = dict((n, z3.read(n)) for n in z3.namelist() if n.endswith(".class"))
    check(sorted(set(c3) - set(c2)) == ["com/skyy/cooking/CookMig.class"] and sorted(set(c2) - set(c3)) == [],
          "F: the class list gains only CookMig: %s / %s" % (sorted(set(c3) - set(c2)), sorted(set(c2) - set(c3))))
    same = sorted(n for n in c3 if c2.get(n) == c3[n])
    diff = sorted(n for n in c3 if n in c2 and c2[n] != c3[n])
    # CookCfg.load() reads DEF_CAMP_XP, a static final double the compiler inlines as a constant: its bytecode differs only in that
    # constant (checked below)
    EXPECT = {"CookCfg": {"f DEF_CAMP_XP", "f DEFAULTS", "f CAMP_BLOCK", "m <clinit>()V", "m load()Ljava/lang/String;"},
              "SkyyCookingPlugin": {"m setup()V"}}
    report = []
    for n in diff:
        cname = n[:-6].replace("/", ".")
        short = cname.rsplit(".", 1)[1]
        m2, m3 = members(OLDJAR, cname), members(JAR, cname)
        changed = sorted(kk for kk in set(m2) | set(m3) if m2.get(kk) != m3.get(kk) and not kk.startswith("v "))
        report.append("%s: %s" % (short, ", ".join(c.split("(")[0] for c in changed) or "(constant pool only)"))
        if short.startswith("Cfg"):
            continue                        # the config kit classes: kit 1.0 -> 1.1, VERSION + the row table
        allowed = EXPECT.get(short)
        check(allowed is not None and set(changed) <= allowed, "F: class %s differs only in the expected members: %s" % (short, changed))
    check(all(("com/skyy/cooking/%s.class" % c) in diff for c in EXPECT), "F: every patched class really changed")
    must_same = ["Cook", "CookXpTask", "CookSys", "CookGradeFn", "CookOutFn", "CookStatsFn", "CookCampFn", "CookCampInfoFn", "CookHooks",
                 "CookGiveCmd", "CookReloadCmd", "CookCampCmd", "CookAdminCmd", "CookingCmd"]
    check(all(("com/skyy/cooking/%s.class" % c) in same for c in must_same), "F: gameplay / bridge / command classes are byte-identical: %s"
          % [c for c in must_same if ("com/skyy/cooking/%s.class" % c) not in same])
    m3 = members(JAR, PKG + "CookCfg")
    m2 = members(OLDJAR, PKG + "CookCfg")
    check(m2["f DEF_CAMP_XP"].endswith(" 0.5") and m3["f DEF_CAMP_XP"].endswith(" 0.25"), "F: DEF_CAMP_XP 0.5 -> 0.25 (%s / %s)"
          % (m2["f DEF_CAMP_XP"], m3["f DEF_CAMP_XP"]))
    d2 = set(m2["v DEFAULTS"].split("\n"))
    d3 = set(m3["v DEFAULTS"].split("\n"))
    # load() also inlines the DEFAULTS and CAMP_BLOCK strings (ldc): put placeholders in, then only DEF_CAMP_XP may differ
    def norm_load(m_):
        t_ = m_["m load()Ljava/lang/String;"]
        assert t_.count(m_["v DEFAULTS"]) == 1
        t_ = t_.replace(m_["v DEFAULTS"], "<DEFAULTS>")          # first: the default text contains the campfire block
        assert t_.count(m_["v CAMP_BLOCK"]) == 1
        return t_.replace(m_["v CAMP_BLOCK"], "<CAMP_BLOCK>").split("\n")
    l2, l3 = norm_load(m2), norm_load(m3)
    ld = [(a, b_) for a, b_ in zip(l2, l3) if a != b_]
    check(len(l2) == len(l3) and ld and all(a.replace("0.5", "0.25") == b_ for a, b_ in ld),
          "F: CookCfg.load differs only in the inlined constants (DEFAULTS, CAMP_BLOCK, DEF_CAMP_XP 0.5 -> 0.25): %s" % ld)
    print("   CookCfg.load: only inlined constants differ (DEFAULTS, CAMP_BLOCK, %s)" % "; ".join("%s -> %s" % (a.strip(), b_.strip()) for a, b_ in ld))
    c2_, c3_ = m2["m <clinit>()V"].split("\n"), m3["m <clinit>()V"].split("\n")
    cd_ = [(a, b_) for a, b_ in zip(c2_, c3_) if a != b_]
    check(len(c2_) == len(c3_) and all(a.replace("0.5", "0.25") == b_ for a, b_ in cd_),
          "F: CookCfg.<clinit> differs only in the CAMP_XP start value 0.5 -> 0.25: %s" % cd_)
    check(sorted(d3 - d2) == sorted([MARK, "campfire.xpFactor=0.25", "# SkyyCooking 0.1.3 - cooking.properties (written on first run; comments must stay on their own lines)"])
          and sorted(d2 - d3) == sorted(["campfire.xpFactor=0.5", "# SkyyCooking 0.1.2 - cooking.properties (written on first run; comments must stay on their own lines)"]),
          "F: the default text differs only in the version line, the marker and the 0.25 line: +%s -%s" % (sorted(d3 - d2), sorted(d2 - d3)))
    print("F. classes byte-identical: %d (%s)" % (len(same), ", ".join(x.rsplit("/", 1)[1][:-6] for x in same)))
    print("   classes that differ: %d + new CookMig" % len(diff))
    for r in report:
        print("     " + r)
    a2 = dict((n, z2.read(n)) for n in z2.namelist() if not n.endswith(".class"))
    a3 = dict((n, z3.read(n)) for n in z3.namelist() if not n.endswith(".class"))
    check(sorted(a2) == sorted(a3), "F: same asset list (%d)" % len(a3))
    adiff = sorted(n for n in a3 if a2.get(n) != a3[n])
    check(adiff == ["manifest.json"], "F: assets that differ: %s" % adiff)
    mf2, mf3 = json.loads(a2["manifest.json"]), json.loads(a3["manifest.json"])
    check(mf3["Version"] == VERSION and mf3["Name"] == "0.1.3 SkyyCooking" and "25% of the XP" in mf3["Description"]
          and dict(mf2, Version=0, Name=0, Description=0) == dict(mf3, Version=0, Name=0, Description=0)
          and mf2["Description"].replace("50% of the XP", "25% of the XP") == mf3["Description"],
          "F: manifest: Name / Version 0.1.3, description 50% -> 25% of the XP")
    # setup() order: CookMig.migrate -> CookCfg.load -> CfgPub.start
    sm = members(JAR, PKG + "SkyyCookingPlugin")["m setup()V"]
    pos = [sm.find(x) for x in ("com.skyy.cooking.CookMig.migrate(", "com.skyy.cooking.CookCfg.load(", "com.skyy.cooking.CfgPub.start(")]
    check(all(p >= 0 for p in pos) and pos[0] < pos[1] < pos[2] and sm.count("CookMig.migrate(") == 1,
          "F: setup() calls CookMig.migrate before CookCfg.load before CfgPub.start (bytecode)")
    if os.path.isfile(DEPLOYED):
        print("   the 0.1.2 jar compared %s the deployed Mods/SkyyCooking.jar" % ("IS" if open(DEPLOYED, "rb").read() == open(OLDJAR, "rb").read() else "is NOT"))


# ============================================================================================================== parent
def main():
    if "--child" in sys.argv:
        try:
            run()
        except Exception as e:
            import traceback
            traceback.print_exc()
            FAILS.append("child crashed: %s" % e)
        print("%d ok, %d failed" % (OKS[0], len(FAILS)))
        for f in FAILS[:40]:
            print("  FAILED:", f[:300])
        sys.exit(1 if FAILS else 0)
    for p in (JAR, OLDJAR):
        if not os.path.isfile(p):
            raise SystemExit("missing " + p + " (build it first)")
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"))
    os.makedirs(os.path.join(SCRATCH, "live"))
    if os.path.isfile(LIVE):
        shutil.copyfile(LIVE, os.path.join(SCRATCH, "live", "cooking.properties"))      # READ ONLY copy of the live file
        print("copied the live cooking.properties (read only): %s" % LIVE)
    else:
        print("note: live cooking.properties not found: %s" % LIVE)
    env = dict(os.environ, TEMP=os.path.join(SCRATCH, "tmp"), TMP=os.path.join(SCRATCH, "tmp"))
    env.pop("JAVA_TOOL_OPTIONS", None)
    args = [sys.executable, os.path.abspath(__file__), "--child", "--dir", SCRATCH, "--jar", JAR, "--old", OLDJAR]
    rc = subprocess.call(args, env=env, cwd=ROOT)
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyCooking %s bare-JVM check: %s%s" % (VERSION, "PASS" if rc == 0 else "FAIL", "" if KEEP else " (scratch folder removed)"))
    sys.exit(rc)


if __name__ == "__main__":
    main()
