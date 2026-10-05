"""Bare-JVM check for SkyyCooking 0.1.6 (INGREDIENT XP by difficulty + the one-time ingredient XP update CookIngMig), extending the 0.1.5
harness (SkyyCooking/test_skyycooking_0.1.5.py: imported for its pure-Python dish-table check C and its 0.1.5 update model; same parent /
child layout).

    python SkyyCooking/test_skyycooking_0.1.6.py [--jar <0.1.6 jar>] [--old <0.1.5 jar>] [--live <Skyy_SkyyCooking folder>] [--dir <scratch>] [--keep]

Build first (python SkyyCooking/build_skyycooking_0.1.6.py). The parent copies the live Skyy_SkyyCooking folder (READ ONLY) into the scratch
folder and starts a child JVM (the game's JRE, -Xverify:all, -XX:-UsePerfData, tmpdir / TEMP / TMP in the scratch folder).
Checks:
  C  (pure Python, independent of the build) the 0.1.5 dish table again (unchanged) + the ingredient table re-derived from Assets.zip:
     direct raw x 950 x (15 + 15 per earlier craft + 5 per extra input + 15 per tier above 1) per mille, rounded to 5 = the documented
     table; Skyy's rule (flour 10-20% of a Vegetable Skewer, every ingredient below the cheapest multi-step dish); route check (no
     ingredient spam beats any dish; meat-pie route 25-30 h to Cooking 50)
  A  every 0.1.6 class loads and verifies (-Xverify:all)
  B  CookCfg.XP_IDS / XP_VALS = the 0.1.6 table; CookIngMig constants; the default text (both markers + the 0.1.6 help above xp.default);
     the loader
  F  the one-time updates on scratch COPIES of the live cooking.properties in setup()'s order: (a) the live file (exact bytes vs the model,
     History copies, Undo-able change-log lines, INFO line, loader, java.util.Properties diff), (b) second start: nothing, (c) hand-set
     ingredient values kept + noted, (c2) shapes, (d) CRLF, (e) no file / fresh 0.1.6 file never updates, (f) no xp lines -> marker only,
     (h) History blocked -> WARN, file untouched, then updated, (i) the config kit: log op lists the lines, tset back to 1425 (Undo path)
     is written and survives the next start
  G  CookIngMig.update on 2000 random files checked against java.util.Properties
  H  start twice on a scratch COPY of the live data folder: first start updates once, second changes nothing
  I  class compare 0.1.5 vs 0.1.6 (normalised per-member disassembly), asset compare, setup() order (bytecode)
Not testable without the game (UNVERIFIED): SkyySkills adding the XP, the Server Setup page drawing Changes / History, a real Undo click.
Nothing is deployed and nothing under AppData is written. Default scratch folder tools/dev/scratch/cook016/harness (deleted unless --keep).
Exit code 1 on any failure.
"""
import os, sys, re, shutil, subprocess, zipfile, json, random, time, math, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD = "0.1.6", "0.1.5"
PKG = "com.skyy.cooking."
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE_DEFAULT = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyCooking")


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "cook016", "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyCooking-%s.jar" % VERSION)))
OLDJAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyCooking-%s.jar" % OLD)))
LIVE = os.path.abspath(arg("--live", LIVE_DEFAULT))
KEEP = "--keep" in sys.argv

_sp = importlib.util.spec_from_file_location("t015", os.path.join(HERE, "test_skyycooking_0.1.5.py"))
T15 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T15)
FAILS = T15.FAILS          # one shared result list (T15.check appends here too)
OKS = T15.OKS
check = T15.check

XP_014, XP_015, DISHES = T15.XP_014, T15.XP_015, T15.DISHES
XP_016 = dict(XP_015, Food_Cheese=85, Food_Fish_Raw=30, Ingredient_Dough=170, Ingredient_Flour=140, Ingredient_Salt=15, Ingredient_Spices=115)
ING = sorted(k for k in XP_016 if XP_016[k] != XP_015[k])
HELP_015 = T15.HELP_NEW
HELP_016 = [
    "# Base XP per finished craft at the Cooking Bench, keyed by the craft's primary OUTPUT item id (0 = no XP). By difficulty (0.1.6): a dish",
    "# pays the raw gathering in its whole ingredient chain x 950 per item x 20% + 15% per extra crafting step + 25% recipe knowledge + 5% Prepared",
    "# / 10% Baked + 5% per tier above 1. An ingredient craft pays only 1.5% of its own inputs (+1.5% per earlier step or tier, +0.5% per extra input).",
]
MARK_ID = "SkyyCooking 0.1.6 ingredient Cooking XP"
MARK = ("# SkyyCooking 0.1.6 ingredient Cooking XP (Skyy 2026-10-05): early, easy ingredients like flour pay little XP - the ingredient xp "
        "lines still on the old defaults were updated once")
MARK15 = T15.MARK
INFO_TAIL = " (Skyy 2026-10-05: early, easy ingredients like flour pay little XP; the old file is in config-history; Server Setup -> Changes can undo each line)"
CHG_ALL = ", ".join("xp.%s %d -> %d" % (i, XP_015[i], XP_016[i]) for i in ING)
LOGROWS = [["xp[%s]" % i, str(XP_015[i]), str(XP_016[i]), "ok"] for i in ING]


def info_for(chg, n):
    return "cooking.properties updated to the 0.1.6 ingredient Cooking XP (%d ingredient XP line(s) on old defaults): %s%s" % (n, chg, INFO_TAIL)


INFO_LIVE = info_for(CHG_ALL, len(ING))


def expected_016(text):
    """independent model of CookIngMig for simple shapes: xp.<ingredient> lines on the 0.1.5 default -> 0.1.6, the 3 0.1.5 help lines ->
    0.1.6, the marker above the comment run on top of the first xp. line (else the first entry, else on top)"""
    nl = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(nl)
    first = firstany = None
    for i, l in enumerate(lines):
        st = l.strip()
        if st and not st.startswith("#") and not st.startswith("!"):
            if firstany is None:
                firstany = i
            if l.lstrip().startswith("xp.") and first is None:
                first = i
            k, _, v = l.partition("=")
            k = k.strip()
            if k.startswith("xp.") and k[3:] in ING and v.strip() == str(XP_015[k[3:]]):
                lines[i] = k + "=" + str(XP_016[k[3:]])
        elif st in HELP_015:
            lines[i] = HELP_016[HELP_015.index(st)]
    at = first if first is not None else firstany
    if at is None:
        at = 0
    while at > 0 and lines[at - 1].strip() and lines[at - 1].lstrip()[:1] in ("#", "!"):
        at -= 1
    lines.insert(at, MARK)
    return nl.join(lines)


def expected_start(text):
    """setup()'s order on a file: the 0.1.5 table update (unless marked), then the 0.1.6 ingredient update (unless marked)"""
    if T15.MARK_ID not in text:
        text = T15.expected_update(text)
    if MARK_ID not in text:
        text = expected_016(text)
    return text


# ============================================================================================================== C (pure Python)
def section_c():
    import skyybuild as B
    T15.section_c()            # the dish table (unchanged in 0.1.6) re-derived exactly as in 0.1.5
    az = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
    items = dict((os.path.basename(n)[:-5], n) for n in az.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))

    def rd(n):
        return json.loads(az.read(n).decode("utf-8-sig"))
    cook = {}
    for iid, p in items.items():
        try:
            r = rd(p).get("Recipe")
        except Exception:
            continue
        if not r or not any(b.get("Id") == "Cookingbench" for b in (r.get("BenchRequirement") or [])):
            continue
        po = r.get("PrimaryOutput")
        outs = r.get("Output") or []
        out = po["ItemId"] if isinstance(po, dict) and po.get("ItemId") else (outs[0]["ItemId"] if outs else iid)
        q = int(po.get("Quantity", r.get("OutputQuantity", 1)) or 1) if isinstance(po, dict) and po.get("ItemId") else (
            int(outs[0].get("Quantity", r.get("OutputQuantity", 1)) or 1) if outs else int(r.get("OutputQuantity", 1) or 1))
        if out in cook and out != iid:
            continue
        cook[out] = ([(("R", i["ResourceTypeId"]) if i.get("ResourceTypeId") else ("I", i["ItemId"])) + (int(i.get("Quantity", 1) or 1),)
                      for i in r.get("Input", [])], q)
    for d, ins in (("Food_Wildmeat_Cooked", [("R", "Meats", 1), ("R", "Fuel", 1)]), ("Food_Fish_Grilled", [("I", "Food_Fish_Raw", 1), ("R", "Fuel", 1)]),
                   ("Food_Vegetable_Cooked", [("R", "Vegetables", 1), ("R", "Fuel", 1)])):
        cook[d] = (ins, 1)
    w_item = {"Ingredient_Stick": 0.5, "*Deco_Tankard_State_Filled_Water": 0.5, "Food_Egg": 2.0}
    w_rt = {"Fuel": 0.5, "Meats": 1.5, "Milk_Bucket": 3.0, "Fish": 2.0}
    tier = {"Plant_Crop_Corn_Item": 2, "Plant_Crop_Pumpkin_Item": 4, "Plant_Fruit_Apple": 2, "Milk_Bucket": 2}

    def sub(k, i, o):
        return k == "I" and i in cook and i != o

    def w(k, i):
        return w_rt.get(i, 1.0) if k == "R" else w_item.get(i, 1.0)

    def raw(o):
        return sum((raw(i) if sub(k, i, o) else w(k, i)) * n for k, i, n in cook[o][0]) / cook[o][1]

    def direct(o):
        return sum(w(k, i) * n for k, i, n in cook[o][0] if not sub(k, i, o))

    def crafts(o):
        s_ = {o}
        for k, i, n in cook[o][0]:
            if sub(k, i, o):
                s_ |= crafts(i)
        return s_

    def tr(o):
        return max([1] + [tr(i) if sub(k, i, o) else tier.get(i, 1) for k, i, n in cook[o][0]])
    ings = sorted(o for o in cook if o not in DISHES)
    check(ings == ING, "C: the ingredient crafts in Assets.zip are the six of the table: %s" % ings)
    got, pm = {}, {}
    for o in ings:
        pm[o] = 15 + 15 * (len(crafts(o)) - 1) + 5 * (len(set((k, i) for k, i, n in cook[o][0])) - 1) + 15 * (tr(o) - 1)
        got[o] = int(5 * round(950.0 * pm[o] * direct(o) / 1000.0 / 5))
    check(got == dict((i, XP_016[i]) for i in ING), "C: the ingredient table re-derived from Assets.zip = the documented table: %s" % got)
    multi = [d for d in DISHES if len(crafts(d)) >= 2]
    check(max(got.values()) < min(XP_016[d] for d in multi), "C: every ingredient pays less than the cheapest multi-step dish (%d)" % min(XP_016[d] for d in multi))
    check(0.10 * XP_016["Food_Kebab_Vegetable"] <= got["Ingredient_Flour"] <= 0.20 * XP_016["Food_Kebab_Vegetable"], "C: flour = 10-20% of a Vegetable Skewer")
    check(all(got[i] < XP_015[i] for i in ING), "C: every ingredient pays less than in 0.1.5")
    full = dict(XP_016)

    def cxp(o):
        return full[o] / float(cook[o][1]) + sum(cxp(i) * n for k, i, n in cook[o][0] if sub(k, i, o))
    rate = dict((o, 1800.0 / raw(o) * cxp(o)) for o in cook if o in full)
    best = max(rate, key=lambda o: rate[o])
    check(best in DISHES and max(rate[i] for i in ING) < min(rate[d] for d in DISHES), "C: route: the fastest route is a dish (%s) and no ingredient spam beats any dish" % best)
    h50 = 55172425 / rate["Food_Pie_Meat"]
    check(25.0 <= h50 <= 30.0, "C: meat-pie route to Cooking 50 = %.1f h (25-30)" % h50)
    print("C. ingredient table re-derived from Assets.zip (per mille = 15 + 15/earlier craft + 5/extra input + 15/tier):")
    for i in sorted(ING, key=lambda i: got[i]):
        print("     %-18s %5d -> %4d  (%d per mille, direct raw %.1f, %.0f XP/h if spammed)" % (i, XP_015[i], got[i], pm[i], direct(i), rate[i]))
    print("   route: best %s %.0f XP/h, slowest dish %s %.0f, fastest ingredient %s %.0f; meat pie -> Cooking 50 in %.1f h"
          % (best, rate[best], min(DISHES, key=lambda d: rate[d]), min(rate[d] for d in DISHES), max(ING, key=lambda i: rate[i]), max(rate[i] for i in ING), h50))


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
    Cfg, Cook, Mig, XMig, TMig, IMig, Rows, CfgPub = (J("CookCfg"), J("Cook"), J("CookMig"), J("CookXpMig"), J("CookTblMig"), J("CookIngMig"),
                                                      J("CfgRows"), J("CfgPub"))
    Paths, Props, Integer = JClass("java.nio.file.Paths"), JClass("java.util.Properties"), JClass("java.lang.Integer")
    UUID, CHM, System = JClass("java.util.UUID"), JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.lang.System")
    BAIS = JClass("java.io.ByteArrayInputStream")
    Bool = JClass("java.lang.Boolean")
    OA = JArray(JObject)
    bridge = CHM()
    System.getProperties().put("skyy.bridge", bridge)

    # ---------------- B. compiled table, constants, default text, loader
    comp = dict(zip([str(x) for x in Cfg.XP_IDS], [int(x) for x in Cfg.XP_VALS]))
    check(comp == XP_016, "B: CookCfg.XP_IDS / XP_VALS = the 0.1.6 table: %s" % comp)
    check([str(x) for x in IMig.KEYS] == ["xp." + i for i in ING] and [str(x) for x in IMig.OLDS] == [str(XP_015[i]) for i in ING]
          and [str(x) for x in IMig.NEWS] == [str(XP_016[i]) for i in ING] and [str(x) for x in IMig.STOPS] == [""] * len(ING)
          and [str(x) for x in IMig.LOGKEYS] == ["xp[%s]" % i for i in ING], "B: CookIngMig KEYS / OLDS / NEWS / STOPS / LOGKEYS")
    check([str(x) for x in IMig.HELP_OLD] == HELP_015 and [str(x) for x in IMig.HELP_NEW] == HELP_016 and str(IMig.MARK) == MARK
          and str(IMig.MARK_ID) == MARK_ID and str(IMig.WHAT) == "before the 0.1.6 ingredient Cooking XP update" and str(Mig.WHO) == "SkyyCooking 0.1.6",
          "B: CookIngMig help lines / marker / WHAT; CookMig.WHO = SkyyCooking 0.1.6")
    check([str(x) for x in TMig.HELP_NEW] == HELP_015 and str(TMig.MARK) == MARK15 and [str(x) for x in TMig.NEWS] == [str(XP_015[d]) for d in T15.TBL],
          "B: CookTblMig unchanged (still writes the 0.1.5 dish values + help)")
    dflt = str(Cfg.DEFAULTS)
    check(dflt.startswith("# SkyyCooking 0.1.6 - cooking.properties") and dflt.count("\n" + MARK + "\n" + MARK15 + "\n" + "\n".join(HELP_016) + "\nxp.default=1000\n") == 1
          and not any(h in dflt for h in HELP_015 + T15.HELP_OLD) and all(dflt.count("\nxp.%s=%d\n" % (k, v)) == 1 for k, v in XP_016.items())
          and dflt.count("\nxpMultiplier=0.5\n") == 1 and dflt.count("\nmaxXpPerMinute=1500000\n") == 1,
          "B: default file: 0.1.6 + 0.1.5 markers + 0.1.6 help right above xp.default, every 0.1.6 xp line, xpMultiplier 0.5, maxXpPerMinute 1500000")
    check(str(Rows.VERSION) == VERSION, "B: kit VERSION 0.1.6")
    bdir = os.path.join(SCRATCH, "work", "b-loader")
    os.makedirs(bdir)
    bf = os.path.join(bdir, "cooking.properties")
    Cfg.FILE = Paths.get(bf)
    Cfg.load()
    check(open(bf, "rb").read().decode("latin-1") == dflt, "B: the loader's fresh file = the default text")
    check(all(int(Cfg.xpFor(d)) == XP_016[d] for d in XP_016), "B: CookCfg.xpFor = the 0.1.6 table")
    open(bf, "w", encoding="latin-1", newline="").write(dflt.replace("\nxp.Ingredient_Flour=140\n", "\nxp.Ingredient_Flour=900\n").replace("\nxp.Ingredient_Salt=15\n", "\n"))
    Cfg.load()
    check(int(Cfg.xpFor("Ingredient_Flour")) == 900 and int(Cfg.xpFor("Ingredient_Salt")) == 15, "B: a hand line wins; a removed line = the built-in 0.1.6 value")
    print("B. compiled XP table, CookIngMig constants, default text, loader checked")

    # fake item asset store (as in the 0.1.5 harness): the kit's XP-per-craft hook checks a tset item id against it
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    DAM = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
    HashMap = JClass("java.util.HashMap")

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
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyTestFakeStore16", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fake.addConstructor(JClass("javassist.CtNewConstructor").make(
        "public SkyyTestFakeStore16() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
    FakeStore = fake.toClass(AS.class_)
    ITM = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    st = us.allocateInstance(FakeStore)
    dm = DAM()
    hm = HashMap()
    for k_ in XP_016:
        hm.put(k_, us.allocateInstance(ITM.class_))
    jfield(DAM.class_, "assetMap").set(dm, hm)
    jfield(AS.class_, "assetMap").set(st, dm)
    jfield(ITM.class_, "ASSET_STORE").set(None, st)

    # ---------------- F. the one-time updates on scratch copies, in setup()'s order
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

    def im(t):
        r = IMig.update(t)
        return None if r is None else (str(r[0]), str(r[1]), None if r[2] is None else str(r[2]), [str(x) for x in r[3]])

    def all_mig():
        return [str(Mig.migrate()), str(XMig.migrate()), str(TMig.migrate()), str(IMig.migrate())]
    live_path = os.path.join(SCRATCH, "live", "Skyy_SkyyCooking", "cooking.properties")
    live = rb(live_path) if os.path.isfile(live_path) else None
    check(live is not None, "F: a scratch copy of the live cooking.properties exists (%s)" % LIVE)
    if live is not None:
        lt = live.decode("latin-1")
        print("F. live file: 0.1.5 marker %s, ingredient lines on the 0.1.5 default: %s" % (
            "present" if T15.MARK_ID in lt else "absent (0.1.5 not started yet: both updates run)",
            [i for i in ING if "\nxp.%s=%d\n" % (i, XP_015[i]) in lt]))
        check(MARK_ID not in lt, "F: the live file has no 0.1.6 marker")
        base = lt
        for i in ING:
            base = re.sub(r"\nxp\.%s=[^\n]*\n" % i, "\nxp.%s=%d\n" % (i, XP_015[i]), base)
        if base != lt:
            print("   (live ingredient lines differ from the 0.1.5 defaults - the exact checks run on a copy with them set back)")
        base_b = base.encode("latin-1")
        n15 = 0 if T15.MARK_ID in base else 1
        # (a) the live file, full start order
        d, f = case("a-live", base_b)
        exp = expected_start(base)
        mid15 = T15.expected_update(base) if n15 else base
        res = all_mig()
        got = rb(f)
        check(res[:2] == ["", ""] and got == exp.encode("latin-1"), "F(a): live file -> (0.1.5 table update) + the 6 ingredient lines 0.1.5 -> 0.1.6, the 3 help lines, the 0.1.6 marker; every other byte kept")
        check(res[3].split("\n") == [INFO_LIVE], "F(a): one 0.1.6 INFO line: %r" % res[3][:300])
        print("F. INFO line the live file produces: [SkyyCooking] " + res[3])
        b = baks(d)
        check(len(b) == 1 + n15 and rb(os.path.join(d, "config-history", b[-1])) == mid15.encode("latin-1") and (not n15 or rb(os.path.join(d, "config-history", b[0])) == base_b),
              "F(a): History keeps the file before each update: %s" % b)
        ix = idx(d)
        check(len(ix) == 1 + n15 and ix[-1].split("\t")[3:] == ["SkyyCooking 0.1.6", "before the 0.1.6 ingredient Cooking XP update"], "F(a): index.log names the update: %s" % ix[-1:])
        cl = clog(d)
        check([l.split("\t")[1:4] for l in cl[-len(ING):]] == [["SkyyCooking 0.1.6", "-", "update"]] * len(ING) and [l.split("\t")[4:] for l in cl[-len(ING):]] == LOGROWS
              and len(cl) == len(ING) + n15 * len(T15.TBL), "F(a): one Undo-able change-log line per changed ingredient entry (xp[<id>]): %s" % cl[-1:])
        print("F. change-log lines (last 2 of %d): %s" % (len(cl), cl[-2:]))
        Cfg.load()
        check(all(int(Cfg.xpFor(dd)) == XP_016[dd] for dd in XP_016), "F(a): the loader reads the 0.1.6 table")
        po, pn = Props(), Props()
        po.load(BAIS(mid15.encode("latin-1")))
        pn.load(BAIS(got))
        diffk = sorted(str(k) for k in set(list(po.stringPropertyNames()) + list(pn.stringPropertyNames())) if po.getProperty(k) != pn.getProperty(k))
        check(diffk == ["xp." + i for i in ING], "F(a): java.util.Properties sees exactly the 6 ingredient keys change in the 0.1.6 step: %s" % diffk)
        # (b) second start
        check(all_mig() == ["", "", "", ""] and rb(f) == got and len(baks(d)) == 1 + n15, "F(b): a second start changes nothing")
        # work on a 0.1.5-shaped file from here on
        b15 = mid15
        # (c) hand-set values kept + noted, a value already 0.1.6 kept silently
        hand = b15.replace("\nxp.Ingredient_Flour=1425\n", "\nxp.Ingredient_Flour=500\n").replace("\nxp.Food_Cheese=430\n", "\nxp.Food_Cheese=85\n")
        d, f = case("c-hand", hand.encode("latin-1"))
        res = str(IMig.migrate())
        rest = [i for i in ING if i not in ("Ingredient_Flour", "Food_Cheese")]
        check(rb(f) == expected_016(hand).encode("latin-1") and "\nxp.Ingredient_Flour=500\n" in expected_016(hand)
              and res.split("\n") == [info_for(", ".join("xp.%s %d -> %d" % (i, XP_015[i], XP_016[i]) for i in rest), len(rest)),
                                      "xp.Ingredient_Flour=500 kept (custom) - the 0.1.6 default is 140"] and len(clog(d)) == len(rest),
              "F(c): hand-set flour 500 kept + noted, cheese already 85 kept silently, the rest updated: %r" % res.split("\n")[1:])
        allc = b15
        for i in ING:
            allc = allc.replace("\nxp.%s=%d\n" % (i, XP_015[i]), "\nxp.%s=%d\n" % (i, XP_015[i] + 1))
        d, f = case("c-allhand", allc.encode("latin-1"))
        res = str(IMig.migrate())
        check(res.split("\n")[0] == "cooking.properties: the ingredient XP lines were changed by hand - kept, nothing changed (0.1.6 ingredient Cooking XP marker added)"
              and len(res.split("\n")) == 1 + len(ING) and clog(d) == [] and rb(f) == expected_016(allc).encode("latin-1"),
              "F(c): every ingredient line hand-set -> marker + help only, a note each, no change-log line")
        # (c2) shapes
        for v, mig in (("1425.0", False), ("01425", False), ("1425\\\n  ", False), (" 1425  ", True)):
            r_ = im(b15.replace("\nxp.Ingredient_Flour=1425\n", "\nxp.Ingredient_Flour=%s\n" % v))
            check(r_ is not None and (("xp.Ingredient_Flour 1425 -> 140" in r_[1]) == mig) and ((r_[2] is not None and "xp.Ingredient_Flour=" in r_[2]) == (not mig)),
                  "F(c2): value %r -> %s" % (v, "updated" if mig else "kept + noted"))
        for sep in (":", " = ", "\t", " "):
            r_ = im(b15.replace("\nxp.Ingredient_Flour=1425\n", "\nxp.Ingredient_Flour%s1425\n" % sep))
            check(r_ is not None and "\nxp.Ingredient_Flour%s140\n" % sep in r_[0], "F(c2): separator %r kept, value replaced" % sep)
        r_ = im(b15.replace("\nxp.Ingredient_Flour=1425\n", "\nxp.Ingredient_Flour=1425\nxp.Ingredient_Flour=300\n"))
        check(r_ is not None and "\nxp.Ingredient_Flour=1425\nxp.Ingredient_Flour=300\n" in r_[0] and "xp.Ingredient_Flour=300 kept (custom)" in (r_[2] or ""),
              "F(c2): duplicate lines, last = 300 -> both kept (the last entry decides)")
        r_ = im(b15.replace("\nxp.Food_Bread=9100\n", "\nxp.Food_Bread=1425\n"))
        check(r_ is not None and "\nxp.Food_Bread=1425\n" in r_[0], "F(c2): a dish line is never touched by the ingredient update")
        # (d) CRLF
        crlf = b15.replace("\n", "\r\n")
        d, f = case("d-crlf", crlf.encode("latin-1"))
        res = str(IMig.migrate())
        check(rb(f) == expected_016(crlf).encode("latin-1") and res == INFO_LIVE and b"\n" not in rb(f).replace(b"\r\n", b""), "F(d): CRLF file -> same update, every CRLF kept")
        # (e) no file; the fresh 0.1.6 file never updates
        d, f = case("e-nofile", None)
        check(str(IMig.migrate()) == "" and not os.path.exists(f), "F(e): no file -> nothing written")
        Cfg.load()
        fresh = rb(f).decode("latin-1")
        check(fresh == dflt and all_mig() == ["", "", "", ""] and rb(f).decode("latin-1") == fresh and not os.path.exists(os.path.join(d, "config-history")),
              "F(e): the fresh 0.1.6 file never updates")
        # (f) no xp lines
        nox = "\n".join(l for l in b15.split("\n") if not l.startswith("xp.") and l not in HELP_015)
        d, f = case("f-noxp", nox.encode("latin-1"))
        res = str(IMig.migrate())
        check(rb(f).decode("latin-1") == expected_016(nox) and res == "cooking.properties: no ingredient XP line on an old default - nothing changed (0.1.6 ingredient Cooking XP marker added)"
              and clog(d) == [], "F(f): no xp lines -> the marker only: %r" % res)
        check(im("enabled=true\n") == (MARK + "\nenabled=true\n", "", None, []) and im("") == (MARK + "\n", "", None, []), "F(f): tiny files -> marker only")
        # (h) History blocked, then free; a folder in place of the file
        d, f = case("h-blocked", b15.encode("latin-1"))
        open(os.path.join(d, "config-history"), "w").write("not a folder")
        check(str(IMig.migrate()) == "" and rb(f) == b15.encode("latin-1") and clog(d) == [], "F(h): History cannot be kept -> WARN, file untouched, no log line")
        os.remove(os.path.join(d, "config-history"))
        check(str(IMig.migrate()) == INFO_LIVE and rb(f) == expected_016(b15).encode("latin-1") and len(baks(d)) == 1 and len(clog(d)) == len(ING),
              "F(h): the next start updates once History can keep the old file")
        d, f = case("h-folder", None)
        os.makedirs(f)
        check(str(IMig.migrate()) == "" and os.path.isdir(f), "F(h): a folder in place of the file -> nothing written")
        # (i) the whole start with the config kit; Undo of one line = tset back
        d, f = case("i-kit", base_b)
        mods = os.path.dirname(d)
        all_mig()
        Cfg.load()
        CfgPub.start(Paths.get(mods), None)
        fn = bridge.get("config:fn:SkyyCooking")
        lg = [str(x) for x in fn.apply(OA(["log", Integer(60)]))]
        mine = [l for l in lg if l.split("\t")[1] == "SkyyCooking 0.1.6" and l.split("\t")[4].startswith("xp[Ingredient") or l.split("\t")[4] in ("xp[Food_Cheese]", "xp[Food_Fish_Raw]")]
        check(len(mine) == len(ING) and sorted(l.split("\t")[4:] for l in mine) == sorted(LOGROWS), "F(i): the kit's log op lists the 6 ingredient lines with status ok (Undo offered): %s" % mine[:1])
        vs = [str(x) for x in fn.apply(OA(["versions"]))]
        check(any(v.split("\t")[3:] == ["SkyyCooking 0.1.6", "before the 0.1.6 ingredient Cooking XP update"] for v in vs), "F(i): versions lists the copy: %s" % vs)
        r1 = fn.apply(OA(["tset", "xp", "Ingredient_Flour", "1425", None, "console", "yes", "console"]))
        CfgPub.flush()
        t2 = rb(f).decode("latin-1")
        check(r1 is not None and str(r1[0]) == "ok" and "\nxp.Ingredient_Flour=1425\n" in t2 and MARK in t2 and int(Cfg.xpFor("Ingredient_Flour")) == 1425
              and t2 == exp.replace("\nxp.Ingredient_Flour=140\n", "\nxp.Ingredient_Flour=1425\n"),
              "F(i): tset xp Ingredient_Flour back to 1425 (the Undo path): only that line changed, marker kept, running value 1425: %s %s %s"
              % (None if r1 is None else [str(x) for x in r1], int(Cfg.xpFor("Ingredient_Flour")), [(a, b_) for a, b_ in zip(t2.split(chr(10)), exp.split(chr(10))) if a != b_][:3]))
        try:
            CfgPub.shutdown()
        except Exception:
            pass
        check(all_mig() == ["", "", "", ""] and rb(f).decode("latin-1") == t2, "F(i): next start: no second update (1425 kept)")
    print("F. one-time updates on scratch copies checked")

    # ---------------- G. random files vs java.util.Properties
    rnd = random.Random(20261006)
    KEYS = ["xp.Ingredient_Flour"] * 4 + ["xp.Food_Cheese"] * 3 + ["xp.Food_Bread", "xp.Ingredient_Salt", "xp.default", "xpMultiplier",
                                                                   "xp.Ingredient_FlourX", " xp.Ingredient_Spices", "xp.Ingredient_Dou\\gh"]
    SEPS = ["=", ":", " ", " = ", "\t=", "  :  "]
    VALS = {"xp.Ingredient_Flour": ["1425", "1425", "140", "1425.0", "17", " 1425", "1425 "], "xp.Food_Cheese": ["430", "430", "85", "1000"],
            "xp.Food_Bread": ["9100", "1425"], " xp.Ingredient_Spices": ["855", "115", "x"], "xp.Ingredient_Dou\\gh": ["640", "170"], "xp.Ingredient_Salt": ["140", "15"]}
    COMS = ["# x", "!bang", "   # indented", "#xp.Ingredient_Flour=1425", HELP_015[0], HELP_015[1], HELP_015[2], "", "   ", "#", MARK15]
    stats = {"mig": 0, "kept": 0, "none": 0}
    for it_ in range(2000):
        lines_ = []
        for _n in range(rnd.randint(0, 10)):
            if rnd.random() < 0.35:
                lines_.append(rnd.choice(COMS))
            else:
                k_ = rnd.choice(KEYS)
                ln = rnd.choice(["", "  ", "\t"]) + k_ + rnd.choice(SEPS) + rnd.choice(VALS.get(k_, ["1", "abc", "1425"]))
                if rnd.random() < 0.1:
                    lines_.append(ln + "\\")
                    ln = rnd.choice(["  5", "  ", "1425", "  # not a comment"])
                lines_.append(ln)
        if rnd.random() < 0.02:
            lines_.insert(rnd.randint(0, len(lines_)), "# " + MARK_ID + " marker")
        eol = rnd.choice(["\n", "\r\n", "mix"])
        text = ""
        for i_, ln in enumerate(lines_):
            e_ = ("\n" if rnd.random() < 0.5 else "\r\n") if eol == "mix" else eol
            text += ln + (e_ if (i_ < len(lines_) - 1 or rnd.random() < 0.7) else "")
        r_ = IMig.update(text)
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
        chgd = [k for k in ko if str(po.getProperty(k)) != str(pn.getProperty(k))]
        ok = ko == sorted(str(k) for k in pn.stringPropertyNames())
        for k in chgd:
            dd = k[3:]
            ok = ok and k.startswith("xp.") and dd in ING and str(po.getProperty(k)).strip() == str(XP_015[dd]) and str(pn.getProperty(k)) == str(XP_016[dd])
        for dd in ING:
            k = "xp." + dd
            if po.getProperty(k) is not None and str(po.getProperty(k)).strip() == str(XP_015[dd]) and k not in chgd:
                ok = ok and r_[2] is not None and ("xp.%s=" % dd) in str(r_[2])
        stats["mig" if chgd else ("kept" if r_[2] is not None else "none")] += 1
        check(ok, "G%d: Properties: only xp.<ingredient> lines on 0.1.5 defaults may change, to the 0.1.6 value (%s)\n%r" % (it_, chgd, text))
        nl_ = new.split("\n")
        mi = [i for i, l in enumerate(nl_) if l.rstrip("\r") == MARK]
        check(len(mi) == 1, "G%d: exactly one marker line" % it_)
        if len(mi) == 1:
            rest = nl_[:mi[0]] + nl_[mi[0] + 1:]
            ol_ = text.split("\n")
            dif = [(a, b_) for a, b_ in zip(ol_, rest) if a != b_] if len(rest) == len(ol_) else [("len", "len")]
            check(len(rest) == len(ol_) and all(a.endswith("\r") == b_.endswith("\r") and (a.rstrip("\r") in HELP_015 and b_.rstrip("\r") == HELP_016[HELP_015.index(a.rstrip("\r"))]
                                                                                       or re.match(r"^[ \t]*xp\.", a) is not None) for a, b_ in dif),
                  "G%d: only xp value lines / 0.1.5 help lines differ, CR kept: %r" % (it_, dif[:3]))
        check(IMig.update(new) is None, "G%d: runs once" % it_)
        if len(FAILS) > 20:
            break
    check(stats["mig"] > 150 and stats["kept"] > 80 and stats["none"] > 80, "G: the random set covers update / kept / untouched: %s" % stats)
    print("G. 2000 random files vs java.util.Properties: %s" % stats)

    # ---------------- H. start twice on a scratch COPY of the live data folder
    src_live = os.path.join(SCRATCH, "live", "Skyy_SkyyCooking")
    sd = os.path.join(SCRATCH, "twice", "mods")
    sh = os.path.join(sd, "Skyy_SkyyCooking")
    if os.path.isdir(src_live):
        shutil.copytree(src_live, sh)
        H_MG = []

        def start():
            Cfg.FILE = Paths.get(os.path.join(sh, "cooking.properties"))
            H_MG.append(all_mig())
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
        lt0 = s0[cp][0].decode("latin-1")
        n_mov = len([i for i in ING if re.search(r"\nxp\.%s=%d\r?\n" % (i, XP_015[i]), T15.expected_update(lt0) if T15.MARK_ID not in lt0 else lt0)])
        check(H_MG[0][3].startswith("cooking.properties updated to the 0.1.6 ingredient Cooking XP (%d " % n_mov), "H: first start: the 0.1.6 update runs (%d lines): %s" % (n_mov, H_MG[0][3][:120]))
        check(s1[cp][0] == expected_start(lt0).encode("latin-1"), "H: first start: cooking.properties = the live file updated (model)")
        check(all(s1[k] == s0[k] for k in s0 if k.endswith(".bak")), "H: the old History copies untouched")
        time.sleep(1.1)
        start()
        s2 = snap()
        check(H_MG[1] == ["", "", "", ""], "H: second start: no update runs: %s" % (H_MG[1],))
        check(sorted(s1) == sorted(s2) and all(s1[k] == s2[k] for k in s1), "H: the second start changes nothing (files + modified times): %s"
              % sorted(k for k in set(s1) | set(s2) if s1.get(k) != s2.get(k)))
        print("H. start twice on a copy of the live data folder: first start: %s; second: no churn" % [x.split(" (")[0][:70] for x in H_MG[0] if x])
    else:
        check(False, "H: no scratch copy of the live data folder (%s)" % LIVE)

    # ---------------- I. class compare 0.1.5 vs 0.1.6
    CP = JClass("javassist.ClassPool")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def members(jar, cname):
        cp = CP(False)
        cp.appendClassPath(jar)
        cp.appendClassPath(B.SERVER_JAR)
        cp.appendSystemPath()
        cf = cp.get(cname).getClassFile()
        out = {}
        for mi in cf.getMethods():
            code = mi.getCodeAttribute()
            lines = []
            if code is not None:
                it = code.iterator()
                while it.hasNext():
                    pos = it.next()
                    lines.append(re.sub(r"#\d+ = ", "", str(IP.instructionString(it, pos, cf.getConstPool()))))
            out["m " + str(mi.getName()) + str(mi.getDescriptor())] = "\n".join(lines)
        for fi in cf.getFields():
            cv = int(fi.getConstantValue())
            val = str(cf.getConstPool().getLdcValue(cv)) if cv else ""
            out["f " + str(fi.getName())] = str(fi.getDescriptor()) + " " + str(fi.getAccessFlags()) + " " + val
            out["v " + str(fi.getName())] = val
        return out

    def ver_only(a_, b_):
        la, lb = (a_ or "").split("\n"), (b_ or "").split("\n")
        return len(la) == len(lb) and all(x == y or x.replace("0.1.5", "0.1.6") == y for x, y in zip(la, lb))
    z5, z6 = zipfile.ZipFile(OLDJAR), zipfile.ZipFile(JAR)
    c5 = dict((n, z5.read(n)) for n in z5.namelist() if n.endswith(".class"))
    c6 = dict((n, z6.read(n)) for n in z6.namelist() if n.endswith(".class"))
    check(sorted(set(c6) - set(c5)) == ["com/skyy/cooking/CookIngMig.class"] and sorted(set(c5) - set(c6)) == [],
          "I: the class list gains only CookIngMig: %s / %s" % (sorted(set(c6) - set(c5)), sorted(set(c5) - set(c6))))
    same = sorted(n for n in c6 if c5.get(n) == c6[n])
    diff = sorted(n for n in c6 if n in c5 and c5[n] != c6[n])
    report = []
    for n in diff:
        cname = n[:-6].replace("/", ".")
        short = cname.rsplit(".", 1)[1]
        m5, m6 = members(OLDJAR, cname), members(JAR, cname)
        changed = sorted(kk for kk in set(m5) | set(m6) if m5.get(kk) != m6.get(kk) and not kk.startswith("v "))
        real = [kk for kk in changed if not ver_only(m5.get(kk), m6.get(kk))]
        report.append("%s: %s%s" % (short, ", ".join(c.split("(")[0] for c in changed) or "(constant pool only)",
                                    "" if not real else "   [beyond the version text: %s]" % ", ".join(c.split("(")[0] for c in real)))
        if short == "CookCfg":
            check(set(real) <= {"f DEFAULTS", "m <clinit>()V", "m load()Ljava/lang/String;"}, "I: CookCfg differs only in DEFAULTS / XP_VALS / the inlined defaults: %s" % real)
        elif short == "CfgRows":
            check(set(real) <= {"m <clinit>()V"} and ('"%s"' % MARK) in m6.get("m <clinit>()V", ""), "I: CfgRows differs only in VERSION + its copy of the default lines: %s" % real)
        elif short == "SkyyCookingPlugin":
            check(set(real) <= {"m setup()V"}, "I: the plugin differs only in setup(): %s" % real)
        else:
            check(not real, "I: class %s differs only in the version text 0.1.5 -> 0.1.6: %s" % (short, real))
    c5c, c6c = members(OLDJAR, PKG + "CookCfg"), members(JAR, PKG + "CookCfg")
    ci5, ci6 = c5c["m <clinit>()V"].split("\n"), c6c["m <clinit>()V"].split("\n")
    check(len(ci5) == len(ci6) and all(a.split()[0] == b_.split()[0] for a, b_ in zip(ci5, ci6) if a != b_)
          and all(("long %d" % XP_016[i]) in c6c["m <clinit>()V"] for i in ING if XP_016[i] > 5),
          "I: CookCfg.<clinit> differs only in constants (the XP_VALS table and inlined texts)")
    must_same = ["CookXpTask", "CookSys", "CookGradeFn", "CookOutFn", "CookCampFn", "CookHooks", "Cook", "CookingCmd", "CookStatsFn"]
    check(all(("com/skyy/cooking/%s.class" % c) in same for c in must_same), "I: grading / XP / bridge / command classes are byte-identical: %s"
          % [c for c in must_same if ("com/skyy/cooking/%s.class" % c) not in same])
    sm = members(JAR, PKG + "SkyyCookingPlugin")["m setup()V"]
    pos = [sm.find(x) for x in ("CookMig.migrate(", "CookXpMig.migrate(", "CookTblMig.migrate(", "CookIngMig.migrate(", "CookCfg.load(", "CfgPub.start(")]
    check(all(p >= 0 for p in pos) and pos == sorted(pos) and sm.count("CookIngMig.migrate(") == 1,
          "I: setup() calls CookMig -> CookXpMig -> CookTblMig -> CookIngMig -> CookCfg.load -> CfgPub.start (bytecode)")
    print("I. classes byte-identical: %d; differ: %d + new CookIngMig" % (len(same), len(diff)))
    for r in report:
        print("     " + r)
    a5 = dict((n, z5.read(n)) for n in z5.namelist() if not n.endswith(".class"))
    a6 = dict((n, z6.read(n)) for n in z6.namelist() if not n.endswith(".class"))
    adiff = sorted(n for n in a6 if a5.get(n) != a6[n])
    check(sorted(a5) == sorted(a6) and adiff == ["manifest.json"], "I: every asset identical; only manifest.json differs: %s" % adiff)


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
