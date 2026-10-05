"""Bare-JVM check for SkyyCooking 0.1.5 (Cooking XP by craft DIFFICULTY + the one-time XP-per-craft update CookTblMig), extending the 0.1.4
harness (SkyyCooking/test_skyycooking_0.1.4.py: same parent / child layout, same fakes), kept next to the build so the build report's claims
can be re-run.

    python SkyyCooking/test_skyycooking_0.1.5.py [--jar <0.1.5 jar>] [--old <0.1.4 jar>] [--live <Skyy_SkyyCooking folder>] [--dir <scratch>] [--keep]

Build first (python SkyyCooking/build_skyycooking_0.1.5.py). The parent copies the live Skyy_SkyyCooking folder (READ ONLY; default: the
"HUD mod" world's mods/Skyy_SkyyCooking) into the scratch folder and starts a child: a fresh JVM (the game's JRE, -Xverify:all,
-XX:-UsePerfData, HytaleServer.jar + the 0.1.5 jar + tools/javassist.jar, java.io.tmpdir / TEMP / TMP in the scratch folder).
Checks:
  C  (pure Python, independent of the build) the difficulty table re-derived from Assets.zip: chain raw x 950 x (20% + 15% per extra
     distinct craft + 25% knowledge + Campfire 0 / Prepared 5 / Baked 10% + 5% per ingredient tier above 1), rounded to 50 = the
     documented table; Skyy's rule (easy < multi-step; skewers <= 65% of the 2026-10-04 stopgap rows); skewers-per-level estimates
  A  every 0.1.5 class loads and verifies (-Xverify:all)
  B  CookCfg.XP_IDS / XP_VALS = the table; the default text (marker + the new help lines right above xp.default, the new xp lines, no old
     help line); the rows (xpMultiplier 0.5, maxXpPerMinute 1,500,000, XP per craft unchanged); the loader (xpFor per dish; a hand line wins)
  D  XP through the compiled paths with fakes (skill:fn:addxp / skill:fn:level / tree:fn:level, fake recipe asset store): the Campfire
     accessory (Cook.campfire) pays round(400 x 0.25) x xpMultiplier; the bench bridge cook:fn:out (CookOutFn) pays xp x xpMultiplier for a
     Vegetable Skewer and a Meat Pie at 0.5 and at the live 0.15
  F  CookTblMig.migrate on scratch COPIES of the live cooking.properties: (a) the live file (exact bytes: the 15 dish lines 0.1.4 -> 0.1.5,
     the 3 help lines replaced, the marker above them; History copy = the old bytes + index line; 15 Undo-able change-log lines; the INFO
     line; the loader reads the new values; java.util.Properties sees exactly the 15 keys change), (a2) Skyy's 2026-10-04 live rows
     (xpMultiplier 0.15 + the 4 stopgap kebab values, as the kit writes them) -> kebabs move, 0.15 is NOT touched, (b) second start:
     nothing, (c) hand-set values kept + noted, (c2) a continued entry / 1050.0 / duplicate lines, (d) CRLF kept, (e) no file -> nothing; the
     fresh 0.1.5 file never updates, (f) no xp lines -> marker only, (g) a 0.1.3-era file gets all three updates in setup()'s order,
     (h) History blocked -> WARN, file untouched, then updated; a folder in place of the file, (i) the whole start with the config kit: the
     log op lists the 15 lines (ok = Undo offered), versions lists the copy, a tset back to 3650 (the Undo path) is written, kept on the
     next start and read by the loader
  G  the pure text step CookTblMig.update on 2500 random files checked against java.util.Properties
  H  start twice on a scratch COPY of the live data folder in setup()'s order: the first start updates once, the second changes nothing
  I  class compare 0.1.4 vs 0.1.5 (normalised per-member disassembly) and asset compare; setup() order (bytecode)
Not testable without the game (UNVERIFIED): SkyySkills adding the XP / levelling, the Server Setup page drawing Changes / History, a real Undo
click (the harness sends the same tset op with via console), the bench's CraftRecipeEvent path (CookSys; byte-identical to 0.1.4).
Nothing is deployed and nothing under AppData is written. Default scratch folder tools/dev/scratch/cook015/harness (deleted unless --keep).
Exit code 1 on any failure.
"""
import os, sys, re, shutil, subprocess, zipfile, json, random, time, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD = "0.1.5", "0.1.4"
PKG = "com.skyy.cooking."
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE_DEFAULT = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyCooking")
DEPLOYED = os.path.join(APPDATA, "Hytale", "UserData", "Mods", "SkyyCooking.jar")


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "cook015", "harness")))
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


# the numbers Skyy / the round fixed (independent of the build script)
XP_014 = {"Food_Bread": 12900, "Food_Cheese": 430, "Food_Fish_Grilled": 2000, "Food_Fish_Raw": 285, "Food_Kebab_Fruit": 3650,
          "Food_Kebab_Meat": 5250, "Food_Kebab_Mushroom": 2850, "Food_Kebab_Vegetable": 3650, "Food_Pie_Apple": 25250,
          "Food_Pie_Meat": 23900, "Food_Pie_Pumpkin": 23200, "Food_Popcorn": 3000, "Food_Salad_Berry": 4850, "Food_Salad_Caesar": 11800,
          "Food_Salad_Mushroom": 3250, "Food_Vegetable_Cooked": 1200, "Food_Wildmeat_Cooked": 1600, "Ingredient_Dough": 640,
          "Ingredient_Flour": 1425, "Ingredient_Salt": 140, "Ingredient_Spices": 855}
XP_015 = dict(XP_014, Food_Vegetable_Cooked=300, Food_Wildmeat_Cooked=400, Food_Fish_Grilled=850, Food_Kebab_Mushroom=850,
              Food_Salad_Mushroom=950, Food_Kebab_Fruit=1050, Food_Kebab_Vegetable=1050, Food_Salad_Berry=1400, Food_Kebab_Meat=1550,
              Food_Popcorn=1750, Food_Bread=9100, Food_Salad_Caesar=11100, Food_Pie_Apple=24950, Food_Pie_Pumpkin=25150, Food_Pie_Meat=25900)
STOPGAP = {"Food_Kebab_Vegetable": 1800, "Food_Kebab_Fruit": 1800, "Food_Kebab_Mushroom": 1400, "Food_Kebab_Meat": 2600}
DISHES = ["Food_Wildmeat_Cooked", "Food_Fish_Grilled", "Food_Vegetable_Cooked", "Food_Bread", "Food_Kebab_Fruit", "Food_Kebab_Meat",
          "Food_Kebab_Mushroom", "Food_Kebab_Vegetable", "Food_Salad_Berry", "Food_Salad_Mushroom", "Food_Popcorn", "Food_Pie_Apple",
          "Food_Pie_Meat", "Food_Pie_Pumpkin", "Food_Salad_Caesar"]
TBL = sorted(d for d in DISHES if XP_015[d] != XP_014[d])
HELP_OLD = [
    "# Base XP per finished craft at the Cooking Bench, keyed by the craft's primary OUTPUT item id (0 = no XP). Pace (decision 2):",
    "# the meat-pie route reaches Cooking 50 in about 27 focused hours, like Alchemy 50. A dish pays 85% of the raw gathering in its",
    "# whole ingredient chain x 950 per item (x1.25 for pies and Caesar salad, which need recipe knowledge); an ingredient craft pays 15% of its own inputs.",
]
HELP_NEW = [
    "# Base XP per finished craft at the Cooking Bench, keyed by the craft's primary OUTPUT item id (0 = no XP). By difficulty (0.1.5): a dish",
    "# pays the raw gathering in its whole ingredient chain x 950 per item x a share - 20% + 15% per extra crafting step + 25% recipe",
    "# knowledge + 5% Prepared / 10% Baked at the Cooking Bench + 5% per ingredient tier above 1. An ingredient craft pays 15% of its own inputs.",
]
MARK_ID = "SkyyCooking 0.1.5 Cooking XP by difficulty"
MARK = ("# SkyyCooking 0.1.5 Cooking XP by difficulty (Skyy 2026-10-04): easier dishes pay less XP, multi-step dishes more - the xp lines "
        "still on the old defaults were updated once")
XP_MARK014 = ("# SkyyCooking 0.1.4 Cooking XP (Skyy 2026-10-02): cooking levelled too fast - every Cooking XP award is halved - "
              "xpMultiplier default 0.5, was 1")
CHG_ALL = ", ".join("xp.%s %d -> %d" % (d, XP_014[d], XP_015[d]) for d in TBL)
INFO_TAIL = " (Skyy 2026-10-04: easier dishes pay less XP, multi-step dishes more; the old file is in config-history; Server Setup -> Changes can undo each line)"


def info_for(chg, n):
    return "cooking.properties updated to the 0.1.5 Cooking XP by difficulty (%d XP per craft line(s) on old defaults): %s%s" % (n, chg, INFO_TAIL)


INFO_LIVE = info_for(CHG_ALL, len(TBL))


def expected_update(text, tab_from=None):
    """independent model of the update for the simple shapes (one-line entries, no duplicates): every xp.<dish> line still on its
    0.1.4 default or stopgap value -> 0.1.5, the 3 old help lines -> new, the marker above the comment run on top of the first xp. line"""
    nl = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(nl)
    first = None
    for i, l in enumerate(lines):
        st = l.strip()
        if st and not st.startswith("#") and not st.startswith("!"):
            if l.lstrip().startswith("xp.") and first is None:
                first = i
            k, _, v = l.partition("=")
            k = k.strip()
            if k.startswith("xp.") and k[3:] in TBL and v.strip() in (str(XP_014[k[3:]]), str(STOPGAP.get(k[3:], "-"))):
                lines[i] = k + "=" + str(XP_015[k[3:]])
        elif st in HELP_OLD:
            lines[i] = HELP_NEW[HELP_OLD.index(st)]
    at = first
    while at is not None and at > 0 and lines[at - 1].strip() and lines[at - 1].lstrip()[:1] in ("#", "!"):
        at -= 1
    lines.insert(at, MARK)
    return nl.join(lines)


# ============================================================================================================== C (pure Python)
def section_c():
    import skyybuild as B
    az = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
    items = {}
    for n in az.namelist():
        if n.startswith("Server/Item/Items/") and n.endswith(".json"):
            items[os.path.basename(n)[:-5]] = n

    def rd(n):
        return json.loads(az.read(n).decode("utf-8-sig"))
    cook, cat = {}, {}
    for iid, p in items.items():
        try:
            r = rd(p).get("Recipe")
        except Exception:
            continue
        if not r:
            continue
        cb = [b for b in (r.get("BenchRequirement") or []) if b.get("Id") == "Cookingbench"]
        if not cb:
            continue
        po = r.get("PrimaryOutput")
        outs = r.get("Output") or []
        out = po["ItemId"] if isinstance(po, dict) and po.get("ItemId") else (outs[0]["ItemId"] if outs else iid)
        q = int(po.get("Quantity", r.get("OutputQuantity", 1)) or 1) if isinstance(po, dict) and po.get("ItemId") else (
            int(outs[0].get("Quantity", r.get("OutputQuantity", 1)) or 1) if outs else int(r.get("OutputQuantity", 1) or 1))
        if out in cook and out != iid:
            continue
        cook[out] = ([(("R", i["ResourceTypeId"]) if i.get("ResourceTypeId") else ("I", i["ItemId"])) + (int(i.get("Quantity", 1) or 1),)
                      for i in r.get("Input", [])], q, bool(r.get("KnowledgeRequired", False)))
        cat[out] = cb[0].get("Categories", [None])[0]
    for d, ins in (("Food_Wildmeat_Cooked", [("R", "Meats", 1), ("R", "Fuel", 1)]), ("Food_Fish_Grilled", [("I", "Food_Fish_Raw", 1), ("R", "Fuel", 1)]),
                   ("Food_Vegetable_Cooked", [("R", "Vegetables", 1), ("R", "Fuel", 1)])):
        check([b.get("Id") for b in rd(items[d])["Recipe"]["BenchRequirement"]] == ["Campfire"], "C: %s is a vanilla Campfire recipe" % d)
        cook[d], cat[d] = (ins, 1, False), "Campfire"
    w_item = {"Ingredient_Stick": 0.5, "*Deco_Tankard_State_Filled_Water": 0.5, "Food_Egg": 2.0}
    w_rt = {"Fuel": 0.5, "Meats": 1.5, "Milk_Bucket": 3.0, "Fish": 2.0}
    tier = {"Plant_Crop_Corn_Item": 2, "Plant_Crop_Pumpkin_Item": 4, "Plant_Fruit_Apple": 2, "Milk_Bucket": 2}

    def sub(k, i, o):
        return k == "I" and i in cook and i != o

    def raw(o):
        ins, q, _ = cook[o]
        return sum((raw(i) if sub(k, i, o) else (w_rt.get(i, 1.0) if k == "R" else w_item.get(i, 1.0))) * n for k, i, n in ins) / q

    def crafts(o):
        s = {o}
        for k, i, n in cook[o][0]:
            if sub(k, i, o):
                s |= crafts(i)
        return s

    def tr(o):
        return max([1] + [tr(i) if sub(k, i, o) else tier.get(i, 1) for k, i, n in cook[o][0]])
    got = {}
    rows = []
    for d in DISHES:
        sh = 20 + 15 * (len(crafts(d)) - 1) + (25 if cook[d][2] else 0) + {"Campfire": 0, "Prepared": 5, "Baked": 10}[cat[d]] + 5 * (tr(d) - 1)
        got[d] = int(50 * round(950.0 * sh * raw(d) / 100.0 / 50))
        rows.append((got[d], d, sh, len(crafts(d)), cook[d][2], cat[d], tr(d), raw(d)))
    check(got == dict((d, XP_015[d]) for d in DISHES), "C: the difficulty table re-derived from Assets.zip = the documented table: %s" % got)
    easy = [d for d in DISHES if len(crafts(d)) == 1 and not cook[d][2]]
    hard = [d for d in DISHES if len(crafts(d)) >= 3]
    check(max(got[d] for d in easy) < min(got[d] for d in hard), "C: every one-step dish pays less than every 3+-step dish")
    check(all(got[d] <= 0.65 * STOPGAP[d] for d in STOPGAP), "C: skewers pay clearly less than the 2026-10-04 stopgap rows")
    check(all(got[d] < XP_014[d] for d in easy) and all(got[d] > got[e] for d in ("Food_Pie_Meat", "Food_Pie_Pumpkin", "Food_Pie_Apple", "Food_Salad_Caesar", "Food_Bread") for e in easy),
          "C: easy dishes pay less than 0.1.4; pies / Caesar / bread pay more than any easy dish")
    print("C. difficulty table re-derived from Assets.zip (share = 20 + 15/step + 25 knowledge + bench + 5/tier):")
    for x in sorted(rows):
        print("     %-22s %6d -> %6d  share %3d%%  crafts %d  knowledge %-5s  %-8s  T%d  raw %.1f" % (x[1], XP_014[x[1]], x[0], x[2], x[3], x[4], x[5], x[6], x[7]))
    for mult in (0.5, 0.15):
        print("   skewers per level at Cooking 10 / 11 / 12 (5,000 / 7,500 / 10,000 XP), xpMultiplier %s: %s" % (mult, "; ".join(
            "%s %s" % (d[11:], " / ".join("%.1f" % (c / (got[d] * mult)) for c in (5000, 7500, 10000))) for d in
            ("Food_Kebab_Vegetable", "Food_Kebab_Mushroom", "Food_Kebab_Meat"))))


# ============================================================================================================== child
def run():
    import jpype
    import skyybuild as B
    from jpype import JClass, JArray, JObject, JImplements, JOverride
    section_c()
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
    Cfg, Cook, Mig, XMig, TMig, Rows, CfgPub = J("CookCfg"), J("Cook"), J("CookMig"), J("CookXpMig"), J("CookTblMig"), J("CfgRows"), J("CfgPub")
    Paths, Props, Integer = JClass("java.nio.file.Paths"), JClass("java.util.Properties"), JClass("java.lang.Integer")
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

    # ---------------- B. compiled table, default text, rows, loader
    comp = dict(zip([str(x) for x in Cfg.XP_IDS], [int(x) for x in Cfg.XP_VALS]))
    check(comp == XP_015, "B: CookCfg.XP_IDS / XP_VALS = the 0.1.5 table: %s" % comp)
    check([str(x) for x in TMig.KEYS] == ["xp." + d for d in TBL] and [str(x) for x in TMig.OLDS] == [str(XP_014[d]) for d in TBL]
          and [str(x) for x in TMig.NEWS] == [str(XP_015[d]) for d in TBL]
          and [str(x) for x in TMig.STOPS] == [str(STOPGAP.get(d, "")) for d in TBL]
          and [str(x) for x in TMig.LOGKEYS] == ["xp[%s]" % d for d in TBL], "B: CookTblMig KEYS / OLDS / NEWS / STOPS / LOGKEYS")
    check([str(x) for x in TMig.HELP_OLD] == HELP_OLD and [str(x) for x in TMig.HELP_NEW] == HELP_NEW and str(TMig.MARK) == MARK
          and str(TMig.MARK_ID) == MARK_ID and str(Mig.WHO) == "SkyyCooking 0.1.5", "B: CookTblMig help lines / marker; CookMig.WHO = SkyyCooking 0.1.5")
    dflt = str(Cfg.DEFAULTS)
    check(dflt.startswith("# SkyyCooking 0.1.5 - cooking.properties") and dflt.count("\n" + MARK + "\n" + "\n".join(HELP_NEW) + "\nxp.default=1000\n") == 1
          and not any(h in dflt for h in HELP_OLD) and all(dflt.count("\nxp.%s=%d\n" % (k, v)) == 1 for k, v in XP_015.items())
          and dflt.count("\nxpMultiplier=0.5\n") == 1 and dflt.count("\nmaxXpPerMinute=1500000\n") == 1 and dflt.count("\n" + XP_MARK014 + "\n") == 1,
          "B: default file: the 0.1.5 marker + new help right above xp.default, every 0.1.5 xp line, xpMultiplier 0.5, maxXpPerMinute 1500000, the 0.1.4 marker")
    keys = [str(k) for k in Rows.KEYS]
    for k_, d_ in (("xpMultiplier", "0.5"), ("maxXpPerMinute", "1500000"), ("campfire.xpFactor", "0.25"), ("campfire.buffFactor", "0.75")):
        check(str(Rows.DEFS[keys.index(k_)]) == d_, "B: row %s default %s" % (k_, d_))
    xi = keys.index("xp")
    check(str(Rows.LABELS[xi]) == "XP per craft" and str(Rows.TYPES[xi]) == "table" and str(Rows.MAXS[xi]) == "1000000"
          and str(Rows.HELPS[xi]) == "Base XP per finished craft by output item id. default = any other output. Remove = built-in value.",
          "B: the XP per craft table row is unchanged")
    check(str(Rows.VERSION) == VERSION, "B: kit VERSION 0.1.5")
    bdir = os.path.join(SCRATCH, "work", "b-loader")
    os.makedirs(bdir)
    bf = os.path.join(bdir, "cooking.properties")
    Cfg.FILE = Paths.get(bf)
    Cfg.load()                                          # writes the fresh default file
    check(open(bf, "rb").read().decode("latin-1") == dflt, "B: the loader's fresh file = the default text")
    check(all(int(Cfg.xpFor(d)) == XP_015[d] for d in XP_015) and int(Cfg.xpFor("Some_Modded_Dish")) == 1000,
          "B: CookCfg.xpFor = the 0.1.5 table, xp.default 1000 for anything else")
    open(bf, "w", encoding="latin-1", newline="").write(dflt.replace("\nxp.Food_Pie_Meat=25900\n", "\nxp.Food_Pie_Meat=30000\n")
                                                        .replace("\nxp.Food_Kebab_Meat=1550\n", "\n"))
    Cfg.load()
    check(int(Cfg.xpFor("Food_Pie_Meat")) == 30000 and int(Cfg.xpFor("Food_Kebab_Meat")) == 1550, "B: a hand line wins; a removed line = the built-in 0.1.5 value")
    print("B. compiled XP table, CookTblMig constants, default text, rows, loader checked")

    # ---------------- D. XP through the compiled paths (fakes, as in the 0.1.4 harness)
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
    RW = "Food_Wildmeat_Cooked_Recipe_Generated_0"
    recs = {RW: recipe(RW, "Food_Wildmeat_Cooked", "Campfire"), "Food_Kebab_Vegetable": recipe("Food_Kebab_Vegetable", "Food_Kebab_Vegetable", "Cookingbench"),
            "Food_Pie_Meat": recipe("Food_Pie_Meat", "Food_Pie_Meat", "Cookingbench")}
    fake_store(CRR, recs)
    fitems = dict(("Skyy_Cook_%s_G%d" % (d, g), us.allocateInstance(ITM.class_)) for d in DISHES for g in range(1, 13))
    fitems.update(dict((d, us.allocateInstance(ITM.class_)) for d in XP_015))      # the plain outputs (the XP per craft check hook looks them up)
    fake_store(ITM, fitems)
    calls = []

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, a):
            return self.f(a)
    bridge.put("skill:fn:level", Fn(lambda a: Integer(10)))
    bridge.put("tree:fn:level", Fn(lambda a: Integer(0)))

    def addxp(a):
        calls.append((str(a[0]), str(a[1]), int(a[2].longValue()), str(a[3])))
        return Bool.TRUE
    bridge.put("skill:fn:addxp", Fn(addxp))
    cdir = os.path.join(SCRATCH, "work", "d-xp")
    os.makedirs(cdir)
    Cfg.FILE = Paths.get(os.path.join(cdir, "cooking.properties"))
    Cfg.load()
    U = UUID.fromString("00000000-0000-0000-0000-00000000c015")
    del calls[:]
    r_ = Cook.campfire(U, RW, 1, None, Bool.FALSE)
    Cook.RATE.clear()
    check(r_ is not None and sum(c[2] for c in calls) == 50, "D: Campfire accessory Cooked Wildmeat at Cooking 10: round(400 x 0.25) x 0.5 = 50 XP (got %s)" % sum(c[2] for c in calls))
    ofn = J("CookOutFn")()
    res = {}
    for mult in (0.5, 0.15):
        Cfg.XP_MULT = mult
        for d in ("Food_Kebab_Vegetable", "Food_Pie_Meat"):
            del calls[:]
            out_ = ofn.apply(OA([U, d, Integer(1), None, Bool.FALSE]))
            Cook.RATE.clear()
            sent = sum(c[2] for c in calls)
            res[(mult, d)] = sent
            want = int(math.floor(XP_015[d] * mult + 0.5))
            check(out_ is not None and sent == want and all(c[1] == "Cooking" for c in calls),
                  "D: bench bridge cook:fn:out, one %s at xpMultiplier %s sends %d XP (got %s, out %s)" % (d, mult, want, sent, out_))
    Cfg.XP_MULT = 0.5
    print("D. XP sent through the compiled code: campfire wildmeat 50; cook:fn:out Vegetable Skewer %s (x0.5) / %s (x0.15), Meat Pie %s / %s"
          % (res.get((0.5, "Food_Kebab_Vegetable")), res.get((0.15, "Food_Kebab_Vegetable")), res.get((0.5, "Food_Pie_Meat")), res.get((0.15, "Food_Pie_Meat"))))

    # ---------------- F. the one-time update on scratch copies
    XD = os.path.join(SCRATCH, "work", "f-mig")

    def case(name, data):
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

    def tm(t):
        r = TMig.update(t)
        return None if r is None else (str(r[0]), str(r[1]), None if r[2] is None else str(r[2]), [str(x) for x in r[3]])
    LOGROWS = [["xp[%s]" % d, str(XP_014[d]), str(XP_015[d]), "ok"] for d in TBL]
    live_path = os.path.join(SCRATCH, "live", "Skyy_SkyyCooking", "cooking.properties")
    live = rb(live_path) if os.path.isfile(live_path) else None
    check(live is not None, "F: a scratch copy of the live cooking.properties exists (%s)" % LIVE)
    if live is not None:
        lt = live.decode("latin-1")
        on_old = [d for d in TBL if "\nxp.%s=%d\n" % (d, XP_014[d]) in lt]
        on_stop = [d for d in STOPGAP if "\nxp.%s=%d\n" % (d, STOPGAP[d]) in lt]
        print("F. live file: %d of %d dish lines on the 0.1.4 default, stopgap kebab rows present: %s, xpMultiplier line: %s" % (
            len(on_old), len(TBL), on_stop or "none", re.findall(r"\nxpMultiplier=([^\r\n]*)", lt)))
        check(MARK_ID not in lt and all(h in lt for h in HELP_OLD) and XP_MARK014 in lt, "F: the live file has the old help lines, the 0.1.4 marker, no 0.1.5 marker")
        if len(on_old) != len(TBL):
            # the live file was hand-edited since this harness was written: rebuild the 0.1.4-default shape from it for the exact checks
            base = lt
            for d in TBL:
                base = re.sub(r"\nxp\.%s=[^\n]*\n" % d, "\nxp.%s=%d\n" % (d, XP_014[d]), base)
            print("   (live file differs from the 0.1.4 defaults - the exact checks run on a copy with the dish lines set back to them)")
        else:
            base = lt
        base_b = base.encode("latin-1")
        # (a) the live file
        d, f = case("a-live", base_b)
        exp = expected_update(base)
        check(str(Mig.migrate()) == "" and str(XMig.migrate()) == "" and rb(f) == base_b, "F(a): the 0.1.3 / 0.1.4 updates do nothing on the live file")
        res = str(TMig.migrate())
        got = rb(f)
        check(got == exp.encode("latin-1"), "F(a): live file -> the 15 dish lines 0.1.4 -> 0.1.5, the 3 help lines, the marker above them; every other byte kept")
        check(res.split("\n") == [INFO_LIVE], "F(a): one INFO line: %r" % res[:300])
        print("F. INFO line the live file produces: [SkyyCooking] " + res)
        b = baks(d)
        check(len(b) == 1 and rb(os.path.join(d, "config-history", b[0])) == base_b, "F(a): History keeps the old file (one .bak = the old bytes): %s" % b)
        ix = idx(d)
        check(len(ix) == 1 and ix[0].split("\t")[1] == "Skyy_SkyyCooking/cooking.properties"
              and ix[0].split("\t")[3:] == ["SkyyCooking 0.1.5", "before the 0.1.5 Cooking XP by difficulty update"], "F(a): index.log names the update: %s" % ix)
        cl = clog(d)
        check([l.split("\t")[1:4] for l in cl] == [["SkyyCooking 0.1.5", "-", "update"]] * len(TBL) and [l.split("\t")[4:] for l in cl] == LOGROWS
              and all(re.match(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d$", l.split("\t")[0]) for l in cl),
              "F(a): one Undo-able config-changes.log line per changed entry in the kit's table form xp[<id>]: %s" % cl[:2])
        print("F. change-log lines (first 2 of %d): %s" % (len(cl), cl[:2]))
        check(not os.path.exists(f + ".tmp"), "F(a): no temp file left")
        Cfg.load()
        check(all(int(Cfg.xpFor(dd)) == XP_015[dd] for dd in XP_015) and abs(float(Cfg.XP_MULT) - 0.5) < 1e-12, "F(a): the loader reads the 0.1.5 table, xpMultiplier untouched")
        po, pn = Props(), Props()
        po.load(BAIS(base_b))
        pn.load(BAIS(got))
        diffk = sorted(str(k) for k in set(list(po.stringPropertyNames()) + list(pn.stringPropertyNames())) if po.getProperty(k) != pn.getProperty(k))
        check(diffk == ["xp." + dd for dd in TBL], "F(a): java.util.Properties sees exactly the 15 dish keys change: %s" % diffk)
        check(base.count("\n") == got.decode("latin-1").count("\n") - 1, "F(a): one line added (the marker), every other line kept")
        # (b) a second start
        check(str(Mig.migrate()) == "" and str(XMig.migrate()) == "" and str(TMig.migrate()) == "" and rb(f) == got and len(baks(d)) == 1
              and len(clog(d)) == len(TBL), "F(b): a second start changes nothing (file, History, change log)")
        # (a2) Skyy's 2026-10-04 live rows: xpMultiplier 0.15 + the stopgap kebab values (the kit writes canonical ints / decimals)
        sk = base.replace("\nxpMultiplier=0.5\n", "\nxpMultiplier=0.15\n")
        for dd, v in STOPGAP.items():
            sk = sk.replace("\nxp.%s=%d\n" % (dd, XP_014[dd]), "\nxp.%s=%d\n" % (dd, v))
        d, f = case("a2-stopgap", sk.encode("latin-1"))
        res = str(TMig.migrate())
        want = expected_update(sk)
        check(rb(f) == want.encode("latin-1") and "\nxpMultiplier=0.15\n" in want, "F(a2): stopgap kebabs 1800 / 1800 / 1400 / 2600 -> 0.1.5; xpMultiplier 0.15 NOT touched")
        chg2 = ", ".join("xp.%s %d -> %d" % (dd, STOPGAP.get(dd, XP_014[dd]), XP_015[dd]) for dd in TBL)
        check(res == info_for(chg2, len(TBL)), "F(a2): INFO names the stopgap values: %r" % res[:300])
        check([l.split("\t")[4:] for l in clog(d)] == [["xp[%s]" % dd, str(STOPGAP.get(dd, XP_014[dd])), str(XP_015[dd]), "ok"] for dd in TBL],
              "F(a2): the Undo lines hold the stopgap values as old")
        Cfg.load()
        check(abs(float(Cfg.XP_MULT) - 0.15) < 1e-12 and int(Cfg.xpFor("Food_Kebab_Vegetable")) == 1050, "F(a2): loader: multiplier 0.15 kept, skewer 1050")
        # (c) hand-set values kept + noted
        hand = base.replace("\nxp.Food_Pie_Meat=23900\n", "\nxp.Food_Pie_Meat=30000\n").replace("\nxp.Food_Kebab_Vegetable=3650\n", "\nxp.Food_Kebab_Vegetable=1700\n") \
                   .replace("\nxp.Food_Bread=12900\n", "\nxp.Food_Bread=9100\n")
        d, f = case("c-hand", hand.encode("latin-1"))
        res = str(TMig.migrate())
        want = expected_update(hand)
        check(rb(f) == want.encode("latin-1") and "\nxp.Food_Pie_Meat=30000\n" in want and "\nxp.Food_Kebab_Vegetable=1700\n" in want,
              "F(c): hand-set 30000 / 1700 kept, a value already at 9100 kept silently, the rest updated")
        notes = ["xp.Food_Kebab_Vegetable=1700 kept (custom) - the 0.1.5 default is 1050", "xp.Food_Pie_Meat=30000 kept (custom) - the 0.1.5 default is 25900"]
        rest = [dd for dd in TBL if dd not in ("Food_Pie_Meat", "Food_Kebab_Vegetable", "Food_Bread")]
        check(res.split("\n") == [info_for(", ".join("xp.%s %d -> %d" % (dd, XP_014[dd], XP_015[dd]) for dd in rest), len(rest))] + notes,
              "F(c): INFO + one note per kept value: %r" % res.split("\n")[1:])
        check(len(clog(d)) == len(rest), "F(c): change-log lines only for the changed entries")
        allc = base
        for dd in TBL:
            allc = allc.replace("\nxp.%s=%d\n" % (dd, XP_014[dd]), "\nxp.%s=%d\n" % (dd, XP_014[dd] + 1))
        d, f = case("c-allhand", allc.encode("latin-1"))
        res = str(TMig.migrate())
        check(res.split("\n")[0] == "cooking.properties: the XP per craft lines were changed by hand - kept, nothing changed (0.1.5 Cooking XP by difficulty marker added)"
              and len(res.split("\n")) == 1 + len(TBL) and clog(d) == [] and len(baks(d)) == 1 and rb(f) == expected_update(allc).encode("latin-1"),
              "F(c): every dish line hand-set -> marker + help only, a note each, no change-log line")
        # (c2) shapes: a continued entry, 3650.0, " 3650 " spacing, separators, a duplicate (last decides)
        for v, mig in (("3650.0", False), ("03650", False), ("3650\\\n  ", False), (" 3650  ", True)):
            t_ = base.replace("\nxp.Food_Kebab_Vegetable=3650\n", "\nxp.Food_Kebab_Vegetable=%s\n" % v)
            r_ = tm(t_)
            ok = r_ is not None and (("xp.Food_Kebab_Vegetable 3650 -> 1050" in r_[1]) == mig) and ((r_[2] is not None and "xp.Food_Kebab_Vegetable=" in r_[2]) == (not mig))
            check(ok, "F(c2): value %r -> %s" % (v, "updated" if mig else "kept + noted"))
        for sep in (":", " = ", "\t", " "):
            t_ = base.replace("\nxp.Food_Kebab_Vegetable=3650\n", "\nxp.Food_Kebab_Vegetable%s3650\n" % sep)
            r_ = tm(t_)
            check(r_ is not None and "\nxp.Food_Kebab_Vegetable%s1050\n" % sep in r_[0], "F(c2): separator %r kept, value replaced" % sep)
        t_ = base.replace("\nxp.Food_Kebab_Vegetable=3650\n", "\nxp.Food_Kebab_Vegetable=3650\nxp.Food_Kebab_Vegetable=2000\n")
        r_ = tm(t_)
        check(r_ is not None and "\nxp.Food_Kebab_Vegetable=3650\nxp.Food_Kebab_Vegetable=2000\n" in r_[0] and "xp.Food_Kebab_Vegetable=2000 kept (custom)" in (r_[2] or ""),
              "F(c2): duplicate lines, last = 2000 -> both kept (the last entry decides)")
        t_ = base.replace("\nxp.Food_Kebab_Vegetable=3650\n", "\nxp.Food_Kebab_Vegetable=2000\nxp.Food_Kebab_Vegetable=1800\n")
        r_ = tm(t_)
        check(r_ is not None and "\nxp.Food_Kebab_Vegetable=2000\nxp.Food_Kebab_Vegetable=1050\n" in r_[0], "F(c2): duplicate lines, last = the stopgap 1800 -> that line moves, 2000 stays")
        # (d) CRLF
        crlf = base.replace("\n", "\r\n")
        d, f = case("d-crlf", crlf.encode("latin-1"))
        res = str(TMig.migrate())
        check(rb(f) == expected_update(crlf).encode("latin-1") and res == INFO_LIVE and b"\n" not in rb(f).replace(b"\r\n", b""),
              "F(d): CRLF file -> same update, every CRLF kept, no bare LF")
        # (e) no file; the fresh 0.1.5 file never updates
        d, f = case("e-nofile", None)
        check(str(TMig.migrate()) == "" and not os.path.exists(f), "F(e): no file -> nothing written")
        Cfg.load()
        fresh = rb(f).decode("latin-1")
        check(fresh == str(Cfg.DEFAULTS) and str(Mig.migrate()) == "" and str(XMig.migrate()) == "" and str(TMig.migrate()) == ""
              and rb(f).decode("latin-1") == fresh and not os.path.exists(os.path.join(d, "config-history")), "F(e): the fresh 0.1.5 file never updates")
        # (f) no xp lines
        nox = "\n".join(l for l in base.split("\n") if not l.startswith("xp.") and l not in HELP_OLD)
        d, f = case("f-noxp", nox.encode("latin-1"))
        res = str(TMig.migrate())
        nl_ = nox.split("\n")
        first = [i for i, l in enumerate(nl_) if l.strip() and not l.lstrip().startswith("#")][0]
        at = first
        while at > 0 and nl_[at - 1].strip() and nl_[at - 1].lstrip().startswith("#"):
            at -= 1
        check(rb(f).decode("latin-1") == "\n".join(nl_[:at] + [MARK] + nl_[at:])
              and res == "cooking.properties: no XP per craft line on an old default - nothing changed (0.1.5 Cooking XP by difficulty marker added)"
              and clog(d) == [], "F(f): no xp lines -> the marker above the comment run on top of the first entry, nothing else: %r" % res)
        check(tm("enabled=true\n") == (MARK + "\nenabled=true\n", "", None, []) and tm("") == (MARK + "\n", "", None, []), "F(f): tiny files -> marker only")
        # (g) a 0.1.3-era file: all three updates in setup()'s order
        CAMP_MARK = [l for l in base.split("\n") if l.startswith("# SkyyCooking 0.1.3 campfire XP")]
        v013 = base.replace(XP_MARK014 + "\n", "").replace("\nxpMultiplier=0.5\n", "\nxpMultiplier=1.0\n")
        d, f = case("g-v013", v013.encode("latin-1"))
        r0, r1 = str(Mig.migrate()), str(XMig.migrate())
        mid = rb(f)
        r2 = str(TMig.migrate())
        check(r0 == "" and r1.startswith("cooking.properties updated to the 0.1.4 Cooking XP default: xpMultiplier 1.0 -> 0.5") and r2 == INFO_LIVE
              and rb(f) == exp.encode("latin-1"), "F(g): a 0.1.3 file gets the 0.1.4 XP update then the 0.1.5 table update -> the same text as (a) (%d campfire marker)" % len(CAMP_MARK))
        b = baks(d)
        check(len(b) == 2 and rb(os.path.join(d, "config-history", b[0])) == v013.encode("latin-1") and rb(os.path.join(d, "config-history", b[1])) == mid,
              "F(g): two History copies (the 0.1.3 file, then the file between the two updates): %s" % b)
        check([l.split("\t")[4:] for l in clog(d)] == [["xpMultiplier", "1.0", "0.5", "ok"]] + LOGROWS, "F(g): 1 + 15 Undo-able change-log lines")
        # (h) History blocked, then free; a folder in place of the file
        d, f = case("h-blocked", base_b)
        open(os.path.join(d, "config-history"), "w").write("not a folder")
        check(str(TMig.migrate()) == "" and rb(f) == base_b and clog(d) == [], "F(h): History cannot be kept -> WARN, file untouched, no log line")
        os.remove(os.path.join(d, "config-history"))
        check(str(TMig.migrate()) == INFO_LIVE and rb(f) == exp.encode("latin-1") and len(baks(d)) == 1 and len(clog(d)) == len(TBL),
              "F(h): the next start updates once History can keep the old file")
        d, f = case("h-folder", None)
        os.makedirs(f)
        check(str(TMig.migrate()) == "" and os.path.isdir(f) and not os.path.exists(os.path.join(d, "config-history")), "F(h): a folder in place of the file -> nothing written")
        # (i) the whole start with the config kit; Undo of one line = tset back
        d, f = case("i-kit", base_b)
        mods = os.path.dirname(d)
        Mig.migrate()
        XMig.migrate()
        TMig.migrate()
        Cfg.load()
        CfgPub.start(Paths.get(mods), None)
        fn = bridge.get("config:fn:SkyyCooking")
        st_ = fn.apply(OA(["status"])) if fn is not None else None
        check(st_ is not None and str(st_[0]) == "ok", "F(i): kit status ok (the update ran before the kit's first read): %s" % (None if st_ is None else [str(x) for x in st_]))
        lg = [str(x) for x in fn.apply(OA(["log", Integer(40)]))]
        check(len(lg) == len(TBL) and sorted(l.split("\t")[4:] for l in lg) == sorted(LOGROWS) and all(l.split("\t")[1:4] == ["SkyyCooking 0.1.5", "-", "update"] for l in lg),
              "F(i): the kit's log op (Server Setup -> Changes) lists the 15 lines with status ok (Undo offered): %s" % lg[:2])
        vs = [str(x) for x in fn.apply(OA(["versions"]))]
        check(len(vs) == 1 and vs[0].split("\t")[3:] == ["SkyyCooking 0.1.5", "before the 0.1.5 Cooking XP by difficulty update"], "F(i): versions lists the copy: %s" % vs)
        r1 = fn.apply(OA(["tset", "xp", "Food_Kebab_Vegetable", "3650", None, "console", "yes", "console"]))
        CfgPub.flush()
        t2 = rb(f).decode("latin-1")
        check(r1 is not None and str(r1[0]) == "ok" and "\nxp.Food_Kebab_Vegetable=3650\n" in t2 and MARK in t2 and int(Cfg.xpFor("Food_Kebab_Vegetable")) == 3650,
              "F(i): tset xp Food_Kebab_Vegetable back to 3650 (the Undo path): ok, written, marker kept, running value 3650 (%s)" % (None if r1 is None else [str(x) for x in r1]))
        check(t2 == exp.replace("\nxp.Food_Kebab_Vegetable=1050\n", "\nxp.Food_Kebab_Vegetable=3650\n"), "F(i): only that line changed back")
        lg2 = [str(x) for x in fn.apply(OA(["log", Integer(40)]))]
        check(len(lg2) == len(TBL) + 1 and lg2[0].split("\t")[4:] == ["xp[Food_Kebab_Vegetable]", "1050", "3650", "ok"], "F(i): the set back is logged: %s" % lg2[:1])
        try:
            CfgPub.shutdown()
        except Exception:
            pass
        check(str(Mig.migrate()) == "" and str(XMig.migrate()) == "" and str(TMig.migrate()) == "" and rb(f).decode("latin-1") == t2, "F(i): next start: no second update (3650 kept)")
        Cfg.load()
        check(int(Cfg.xpFor("Food_Kebab_Vegetable")) == 3650, "F(i): next start reads 3650")
    print("F. one-time update on scratch copies checked")

    # ---------------- G. random files vs java.util.Properties
    rnd = random.Random(20261005)
    KEYS = ["xp.Food_Kebab_Vegetable"] * 4 + ["xp.Food_Pie_Meat"] * 3 + ["xp.Food_Bread", "xp.Ingredient_Flour", "xp.default", "xpMultiplier",
                                                                          "xp.Food_Kebab_VegetableX", " xp.Food_Kebab_Meat", "xp.Food_Kebab_Mush\\room"]
    SEPS = ["=", ":", " ", " = ", "\t=", "  :  "]
    VALS = {"xp.Food_Kebab_Vegetable": ["3650", "3650", "1800", "1050", "3650.0", "17", " 3650", "1800 "], "xp.Food_Pie_Meat": ["23900", "23900", "25900", "30000"],
            "xp.Food_Bread": ["12900", "9100", "1"], " xp.Food_Kebab_Meat": ["5250", "2600", "x"], "xp.Food_Kebab_Mush\\room": ["2850", "1400"]}
    COMS = ["# x", "!bang", "   # indented", "#xp.Food_Bread=12900", HELP_OLD[0], HELP_OLD[1], HELP_OLD[2], "", "   ", "#", XP_MARK014]
    stats = {"mig": 0, "kept": 0, "none": 0}
    for it_ in range(2500):
        lines_ = []
        for _n in range(rnd.randint(0, 10)):
            if rnd.random() < 0.35:
                lines_.append(rnd.choice(COMS))
            else:
                k_ = rnd.choice(KEYS)
                ln = rnd.choice(["", "  ", "\t"]) + k_ + rnd.choice(SEPS) + rnd.choice(VALS.get(k_, ["1", "abc", "3650"]))
                if rnd.random() < 0.1:
                    lines_.append(ln + "\\")
                    ln = rnd.choice(["  5", "  ", "3650", "  # not a comment"])
                lines_.append(ln)
        if rnd.random() < 0.02:
            lines_.insert(rnd.randint(0, len(lines_)), "# " + MARK_ID + " marker")
        eol = rnd.choice(["\n", "\r\n", "mix"])
        text = ""
        for i_, ln in enumerate(lines_):
            e_ = ("\n" if rnd.random() < 0.5 else "\r\n") if eol == "mix" else eol
            text += ln + (e_ if (i_ < len(lines_) - 1 or rnd.random() < 0.7) else "")
        r_ = TMig.update(text)
        po = Props()
        po.load(BAIS(text.encode("latin-1")))
        if r_ is None:
            stats["none"] += 1
            check(MARK_ID in text, "G%d: only a marked file is left alone" % it_)
            continue
        new = str(r_[0])
        pn = Props()
        pn.load(BAIS(new.encode("latin-1")))
        ko = sorted(str(k) for k in po.stringPropertyNames())
        kn = sorted(str(k) for k in pn.stringPropertyNames())
        chgd = [k for k in ko if str(po.getProperty(k)) != str(pn.getProperty(k))]
        ok = ko == kn
        for k in chgd:
            dd = k[3:]
            ok = ok and k.startswith("xp.") and dd in TBL and str(po.getProperty(k)).strip() in (str(XP_014[dd]), str(STOPGAP.get(dd, "-"))) \
                and str(pn.getProperty(k)) == str(XP_015[dd]) and ("xp.%s " % dd) in str(r_[1])
        for dd in TBL:      # a key whose last value is an old / stopgap one-line value must move
            k = "xp." + dd
            if po.getProperty(k) is not None and str(po.getProperty(k)).strip() in (str(XP_014[dd]), str(STOPGAP.get(dd, "-"))) and k not in chgd:
                ok = ok and r_[2] is not None and ("xp.%s=" % dd) in str(r_[2])        # only a continued entry may stay (noted)
        if chgd:
            stats["mig"] += 1
        else:
            stats["kept" if r_[2] is not None else "none"] += 1
        check(ok, "G%d: Properties: only xp.<dish> lines on old / stopgap values may change, to the 0.1.5 value (%s)\n%r" % (it_, chgd, text))
        nl_ = new.split("\n")
        mi = [i for i, l in enumerate(nl_) if l.rstrip("\r") == MARK]
        check(len(mi) == 1, "G%d: exactly one marker line" % it_)
        if len(mi) == 1:
            rest = nl_[:mi[0]] + nl_[mi[0] + 1:]
            ol_ = text.split("\n")
            dif = [(a, b_) for a, b_ in zip(ol_, rest) if a != b_] if len(rest) == len(ol_) else [("len", "len")]
            ok2 = len(rest) == len(ol_) and all(a.endswith("\r") == b_.endswith("\r") and (a.rstrip("\r") in HELP_OLD and b_.rstrip("\r") == HELP_NEW[HELP_OLD.index(a.rstrip("\r"))]
                                                                                         or re.match(r"^[ \t]*xp\.", a) is not None) for a, b_ in dif)
            check(ok2, "G%d: only xp value lines / old help lines differ, CR kept: %r" % (it_, dif[:3]))
        check(TMig.update(new) is None, "G%d: runs once" % it_)
        if len(FAILS) > 20:
            break
    check(stats["mig"] > 200 and stats["kept"] > 100 and stats["none"] > 100, "G: the random set covers update / kept / untouched: %s" % stats)
    print("G. 2500 random files vs java.util.Properties: %s" % stats)

    # ---------------- H. start twice on a scratch COPY of the live data folder
    src_live = os.path.join(SCRATCH, "live", "Skyy_SkyyCooking")
    sd = os.path.join(SCRATCH, "twice", "mods")
    sh = os.path.join(sd, "Skyy_SkyyCooking")
    if os.path.isdir(src_live):
        shutil.copytree(src_live, sh)
        H_MG = []

        def start():        # setup()'s order: CookMig, CookXpMig, CookTblMig, CookCfg.load, CfgPub.start
            Cfg.FILE = Paths.get(os.path.join(sh, "cooking.properties"))
            H_MG.append((str(Mig.migrate()), str(XMig.migrate()), str(TMig.migrate())))
            Cfg.load()
            CfgPub.start(Paths.get(sd), None)
            CfgPub.flush()
            time.sleep(0.6)
            CfgPub.shutdown()

        def snap():
            out = {}
            for dp, _dn, fns in os.walk(sd):
                for f_ in fns:
                    p_ = os.path.join(dp, f_)
                    out[os.path.relpath(p_, sd)] = (open(p_, "rb").read(), os.path.getmtime(p_))
            return out
        s0 = snap()
        start()
        s1 = snap()
        cp = os.path.join("Skyy_SkyyCooking", "cooking.properties")
        hl = os.path.join("Skyy_SkyyCooking", "config-changes.log")
        lt0 = s0[cp][0].decode("latin-1")
        n_mov = len([dd for dd in TBL if re.search(r"\nxp\.%s=(%d|%s)\n" % (dd, XP_014[dd], STOPGAP.get(dd, "x")), lt0)])
        check(H_MG[0][:2] == ("", "") and H_MG[0][2].startswith("cooking.properties updated to the 0.1.5 Cooking XP by difficulty (%d " % n_mov),
              "H: first start: only the 0.1.5 table update runs (%d lines): %s" % (n_mov, H_MG[0][2][:160]))
        check(s1[cp][0] == expected_update(lt0).encode("latin-1"), "H: first start: cooking.properties = the live file updated (model)")
        new_baks = sorted(set(k for k in s1 if k.endswith(".bak")) - set(k for k in s0 if k.endswith(".bak")))
        check(len(new_baks) == 1 and s1[new_baks[0]][0] == s0[cp][0] and all(s1[k] == s0[k] for k in s0 if k.endswith(".bak")),
              "H: first start: one new History copy = the live bytes, the old copies untouched: %s" % new_baks)
        oldlog = s0.get(hl, (b"", 0))[0].decode("utf-8")
        newlog = s1[hl][0].decode("utf-8")
        added = newlog[len(oldlog):].strip().split("\n") if newlog.startswith(oldlog) else ["(rewritten)"]
        check(len(added) == n_mov and all(a.split("\t")[1:4] == ["SkyyCooking 0.1.5", "-", "update"] for a in added),
              "H: first start: the change log keeps its old lines and gains %d: %s" % (n_mov, added[:1]))
        time.sleep(1.1)
        start()
        s2 = snap()
        check(H_MG[1] == ("", "", ""), "H: second start: no update runs: %s" % (H_MG[1],))
        check(sorted(s1) == sorted(s2) and all(s1[k] == s2[k] for k in s1), "H: the second start changes nothing (files + modified times): %s"
              % sorted(k for k in set(s1) | set(s2) if s1.get(k) != s2.get(k)))
        print("H. start twice on a copy of the live data folder: first start updates %d lines once, second: no churn" % n_mov)
    else:
        check(False, "H: no scratch copy of the live data folder (%s)" % LIVE)

    # ---------------- I. class compare 0.1.4 vs 0.1.5
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

    def ver_only(a_, b_):
        la, lb = (a_ or "").split("\n"), (b_ or "").split("\n")
        return len(la) == len(lb) and all(x == y or x.replace("0.1.4", "0.1.5") == y or x.replace('"SkyyCooking 0.1.4"', '"SkyyCooking 0.1.5"') == y
                                          for x, y in zip(la, lb))
    z4, z5 = zipfile.ZipFile(OLDJAR), zipfile.ZipFile(JAR)
    c4 = dict((n, z4.read(n)) for n in z4.namelist() if n.endswith(".class"))
    c5 = dict((n, z5.read(n)) for n in z5.namelist() if n.endswith(".class"))
    check(sorted(set(c5) - set(c4)) == ["com/skyy/cooking/CookTblMig.class"] and sorted(set(c4) - set(c5)) == [],
          "I: the class list gains only CookTblMig: %s / %s" % (sorted(set(c5) - set(c4)), sorted(set(c4) - set(c5))))
    same = sorted(n for n in c5 if c4.get(n) == c5[n])
    diff = sorted(n for n in c5 if n in c4 and c4[n] != c5[n])
    report = []
    for n in diff:
        cname = n[:-6].replace("/", ".")
        short = cname.rsplit(".", 1)[1]
        m4, m5 = members(OLDJAR, cname), members(JAR, cname)
        changed = sorted(kk for kk in set(m4) | set(m5) if m4.get(kk) != m5.get(kk) and not kk.startswith("v "))
        real = [kk for kk in changed if not ver_only(m4.get(kk), m5.get(kk))]
        report.append("%s: %s%s" % (short, ", ".join(c.split("(")[0] for c in changed) or "(constant pool only)",
                                    "" if not real else "   [beyond the version text: %s]" % ", ".join(c.split("(")[0] for c in real)))
        if short == "CookCfg":
            check(set(real) <= {"f DEFAULTS", "m <clinit>()V", "m load()Ljava/lang/String;"}, "I: CookCfg differs only in DEFAULTS / the XP_VALS table / the inlined defaults: %s" % real)
        elif short == "CfgRows":       # the kit's copy of the default file lines (+1 line: the marker) and VERSION
            check(set(real) <= {"m <clinit>()V"} and ('"%s"' % MARK) in m5.get("m <clinit>()V", "") and ('"%s"' % HELP_OLD[1]) not in m5.get("m <clinit>()V", ""),
                  "I: CfgRows differs only in VERSION and its copy of the default file lines (marker + new help + new xp lines): %s" % real)
        elif short == "SkyyCookingPlugin":
            check(set(real) <= {"m setup()V"}, "I: the plugin differs only in setup(): %s" % real)
        else:
            check(not real, "I: class %s differs only in the version text 0.1.4 -> 0.1.5: %s" % (short, real))
    c4c, c5c = members(OLDJAR, PKG + "CookCfg"), members(JAR, PKG + "CookCfg")
    l4 = c4c["m load()Ljava/lang/String;"].replace(c4c["v DEFAULTS"], "<D>").split("\n")
    l5 = c5c["m load()Ljava/lang/String;"].replace(c5c["v DEFAULTS"], "<D>").split("\n")
    check(l4 == l5 or ver_only("\n".join(l4), "\n".join(l5)), "I: CookCfg.load is the same code (only the inlined default text differs)")
    ci4, ci5 = c4c["m <clinit>()V"].split("\n"), c5c["m <clinit>()V"].split("\n")
    cd_ = [(a, b_) for a, b_ in zip(ci4, ci5) if a != b_]
    check(len(ci4) == len(ci5) and all(a.split()[0] == b_.split()[0] for a, b_ in cd_)
          and all(("long %d" % XP_015[d]) in c5c["m <clinit>()V"] for d in TBL),
          "I: CookCfg.<clinit> differs only in constants (the XP_VALS table and inlined texts): %d lines" % len(cd_))
    must_same = ["CookXpTask", "CookSys", "CookGradeFn", "CookOutFn", "CookCampFn", "CookHooks", "Cook", "CookingCmd", "CookStatsFn"]
    check(all(("com/skyy/cooking/%s.class" % c) in same for c in must_same), "I: grading / XP / bridge / command classes are byte-identical "
          "(CookMig / CookXpMig differ only by the inlined WHO 'SkyyCooking 0.1.5', checked above): %s"
          % [c for c in must_same if ("com/skyy/cooking/%s.class" % c) not in same])
    sm = members(JAR, PKG + "SkyyCookingPlugin")["m setup()V"]
    pos = [sm.find(x) for x in ("com.skyy.cooking.CookMig.migrate(", "com.skyy.cooking.CookXpMig.migrate(", "com.skyy.cooking.CookTblMig.migrate(",
                                "com.skyy.cooking.CookCfg.load(", "com.skyy.cooking.CfgPub.start(")]
    check(all(p >= 0 for p in pos) and pos == sorted(pos) and sm.count("CookTblMig.migrate(") == 1,
          "I: setup() calls CookMig -> CookXpMig -> CookTblMig -> CookCfg.load -> CfgPub.start (bytecode)")
    print("I. classes byte-identical: %d (%s)" % (len(same), ", ".join(x.rsplit("/", 1)[1][:-6] for x in same)))
    print("   classes that differ: %d + new CookTblMig" % len(diff))
    for r in report:
        print("     " + r)
    a4 = dict((n, z4.read(n)) for n in z4.namelist() if not n.endswith(".class"))
    a5 = dict((n, z5.read(n)) for n in z5.namelist() if not n.endswith(".class"))
    adiff = sorted(n for n in a5 if a4.get(n) != a5[n])
    check(sorted(a4) == sorted(a5) and adiff == ["manifest.json"], "I: every asset (effects, checks, dishes, recipes, server.lang) identical; only manifest.json differs: %s" % adiff)
    mf4, mf5 = json.loads(a4["manifest.json"]), json.loads(a5["manifest.json"])
    check(mf5["Version"] == VERSION and dict(mf4, Version=0, Name=0) == dict(mf5, Version=0, Name=0), "I: manifest: only Name / Version")
    if os.path.isfile(DEPLOYED):
        print("   the 0.1.4 jar compared %s the deployed Mods/SkyyCooking.jar" % ("IS" if open(DEPLOYED, "rb").read() == open(OLDJAR, "rb").read() else "is NOT"))


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
            print("  FAILED:", f[:400])
        sys.exit(1 if FAILS else 0)
    for p in (JAR, OLDJAR):
        if not os.path.isfile(p):
            raise SystemExit("missing " + p + " (build it first)")
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"))
    os.makedirs(os.path.join(SCRATCH, "live"))
    if os.path.isdir(LIVE):
        shutil.copytree(LIVE, os.path.join(SCRATCH, "live", "Skyy_SkyyCooking"))      # READ ONLY copy of the live data folder
        print("copied the live Skyy_SkyyCooking folder (read only): %s" % LIVE)
    else:
        print("note: live Skyy_SkyyCooking folder not found: %s" % LIVE)
    env = dict(os.environ, TEMP=os.path.join(SCRATCH, "tmp"), TMP=os.path.join(SCRATCH, "tmp"))
    env.pop("JAVA_TOOL_OPTIONS", None)
    args = [sys.executable, os.path.abspath(__file__), "--child", "--dir", SCRATCH, "--jar", JAR, "--old", OLDJAR, "--live", LIVE]
    rc = subprocess.call(args, env=env, cwd=ROOT)
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyCooking %s bare-JVM check: %s%s" % (VERSION, "PASS" if rc == 0 else "FAIL", "" if KEEP else " (scratch folder removed)"))
    sys.exit(rc)


if __name__ == "__main__":
    main()
