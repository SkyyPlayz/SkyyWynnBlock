"""Harness for SkyyBazaar 0.2.2 (round E1: the reverse recipes 1 Enchanted -> 100 base in every money-loop check and in the jar's admin
price guard; tools/bazaar_0_2_2_patch.py). Build first:
    python tools/bazaar_0_2_2_patch.py && python SkyyBazaar/build_skyybazaar_0.2.2.py --with SkyyCollections/SkyyCollections-0.2.34.jar
    python SkyyBazaar/test_skyybazaar_0.2.2.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, -Xverify:all, tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes; line endings kept; no new command / system; the E1 recipes join the models AFTER the
                 price builder (PROC, the P7 table) and BEFORE the sweep / every loop check / the guard edges
  A     verify   every class loads + initialises
  C     compare  0.2.1 -> 0.2.2 (EXPECT below)
  K     catalog  the jar's Catalog tables vs 0.2.1: the guard EDGES gain exactly the reverse / pocket recipe edges (one per Enchanted product
                 whose base is listed, + the vanilla pair both ways), every 0.2.1 edge kept; the product table (SEED) identical; the sweep's
                 sell caps / buy-side raises only grow (0.2.1's kept exactly; the additions named in the notes); the floor exemptions
                 (NF_ID) are 0.2.1's EXACTLY and the E1 additions are floor CAPS (NFC_ID) instead (ench1fix)
  G     guard    EXECUTED on a fresh folder through the jar's own setup steps: no edge pays at the defaults (warnLoops 0); an admin price
                 that makes UNPACK pay (Enchanted Copper fixed at 1) is REFUSED naming Enchanted Copper -> 100 Copper Ingot, the old price
                 kept; the 0.2.1 jar takes the same price (its guard did not know the reverse)
  Q     quote    every product's instant buy > instant sell; for every Enchanted product with a listed base: buy 1 Enchanted > sell 100 base
                 and buy 100 base > sell 1 Enchanted at the jar's own quotes (demand 1)
  F     floor    EXECUTED Market.quote on the 0.2.1 and 0.2.2 jars (ench1fix): at the default minimum sell 2 every capped product
                 (NFC_ID) quotes exactly as in 0.2.1 at demand 0.25 / 0.5 / 1 / 2, buy and sell (no 0-coin sale); at minimum sell 3-5 a
                 capped product still sells for at least 2 at demand 0.25, a normal product for at least the minimum, and buy 1
                 Enchanted -> sell the 100 base never pays for any listed pair (0.2.1 at minimum sell 5 does: shown in the notes)
  D     live     scratch COPIES of the live NewBetaTest Skyy_SkyyBazaar: the 0.2.2 jar's start = the 0.2.1 jar's start byte-for-byte (no data
                 change), and a second 0.2.2 start writes nothing
  AA    audit    engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, subprocess, importlib.util, json, shutil, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyench as EN

VERSION = "0.2.2"
PKG = "com.skyy.bazaar."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBazaar-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyBazaar-0.2.1.jar")
GEN = os.path.join(HERE, "build_skyybazaar_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyybazaar_0.2.1.py")
PATCH = os.path.join(ROOT, "tools", "bazaar_0_2_2_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "ench1", "bz")))
LIVE = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyBazaar")
# BzMarket.tiers: its TIER_SPEC literal is the committed tools/tier_tags.py, which gained rows after 0.2.1 was built (fish rows, Pets dragon
# eggs) - sort only, not this round
EXPECT = {"BzMarket": ["~m tiers"], "Catalog": ["+f NFC_ID", "+f NOFLOORCAP", "~<clinit>", "~m floorBase", "~m init"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "SkyyBazaarPlugin": ["~m setup"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = []


def tmod(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    old = sys.argv
    sys.argv = [old[0]]
    try:
        spec.loader.exec_module(m)
    finally:
        sys.argv = old
    return m


T21 = None


def t21():
    global T21
    if T21 is None:
        T21 = tmod(os.path.join(HERE, "test_skyybazaar_0.2.1.py"), "tbz021")
    return T21


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.count('VERSION = "0.2.2"') == 1 and g.startswith('"""SkyyBazaar 0.2.2'), "S version + header")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    i = g.index
    K.check(i("PROC = processed_table(MODEL, set(ids))") < i("SET_MODEL, SET_SCAN = set_model(MODEL, DATA)")
            < i("SET_MODEL[\"recipes\"] = [r for r in SET_MODEL[\"recipes\"] if r not in _e1jar]") < i("_rec_out = collections.defaultdict(list)") < i("for _round in range(40):")
            < i("\nMODEL[\"recipes\"].extend(E1_RECS)") < i("SET_MODEL[\"recipes\"].extend(E1_SET)") < i("for _round2 in range(40):")
            < i("_selftest = loop_check_selftest()") < i("EDGES = edge_table(MODEL, set(ids), CHARCOAL)"),
            "S order: SET scan (the jar's reverse copies out) -> price builder (PROC, P7) -> the 0.2.1 sweep -> E1 recipes join -> second sweep -> loop checks -> guard edges")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    # ench1fix2: the minimum-sell row's help is the only CfgRows change (CfgRows <clinit> in EXPECT); the jar carries it, not the old text
    cr = zipfile.ZipFile(jar).read([n for n in zipfile.ZipFile(jar).namelist() if n.endswith("/CfgRows.class")][0])
    K.check(b"some cheap bulk items stop at 2" in cr and b"No instant sale pays less per item" not in cr and g.count("No instant sale pays less per item") == 0
            and o.count("No instant sale pays less per item") == 1, "S Server Setup minimum-sell help: says some cheap bulk items stop at 2 (ench1fix2)")
    K.check(g.count("0.2.2 E1 lower-spread report") == 1, "S the E1 lower-spread report is built (report only, ench1fix2)")
    K.save()


def _consts(J):
    C = J("Catalog")
    out = {}
    for f in C.class_.getDeclaredFields():
        m = f.getModifiers()
        if not (JClassMod().isStatic(m) and JClassMod().isFinal(m)):
            continue
        f.setAccessible(True)
        v = f.get(None)
        t = str(f.getType().getName())
        if t == "[Ljava.lang.String;":
            out[str(f.getName())] = [str(x) for x in v]
        elif t == "[D":
            out[str(f.getName())] = [float(x) for x in v]
        elif t == "java.lang.String":
            out[str(f.getName())] = str(v)
    return out


def JClassMod():
    from jpype import JClass
    return JClass("java.lang.reflect.Modifier")


def _dump_consts(jar_path, dst):
    """child helper: write the Catalog constants of one jar to dst (json)"""
    from jpype import JClass
    HK.jvm([jar_path, B.SERVER_JAR], verify=True)
    J = lambda n: JClass(PKG + n)
    json.dump(_consts(J), open(dst, "w"))


def run_catalog(out, jar, scratch, home):
    K = HK.Child(out)
    env = dict(os.environ)
    res = {}
    for tag, jp in (("old", OLD_JAR), ("new", jar)):
        dst = os.path.join(scratch, "consts_%s.json" % tag)
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--dump-consts", jp, dst], env=env, capture_output=True, text=True)
        K.check(p.returncode == 0 and os.path.isfile(dst), "K constants of %s read: %s" % (os.path.basename(jp), p.stderr[-300:]))
        res[tag] = json.load(open(dst)) if os.path.isfile(dst) else {}
    a, b = res["old"], res["new"]
    diff = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
    K.notes.append("K Catalog constants that differ: %s" % diff)
    K.check(set(diff) <= set(["EDGES", "SC_ID", "SC_V", "NFC_ID", "BX_ID", "BX_V"]), "K only the guard edges / sell caps / floor caps differ: %s" % diff)
    K.check(a.get("NF_ID") == b.get("NF_ID") and len(b.get("NF_ID", [])) == 30, "K ench1fix: the floor exemptions (NF_ID) = 0.2.1's exactly (%d)" % len(b.get("NF_ID", [])))
    K.eq(sorted(b.get("NFC_ID", [])), sorted(["Ingredient_Charcoal", "Ingredient_Fibre", "Ingredient_Stick", "Plant_Crop_Corn_Item", "Plant_Crop_Wheat_Item",
                                             "Plant_Fruit_Berries_Red", "Plant_Petals_Blood", "Rock_Ice", "Soil_Clay", "Soil_Sand"]),
         "K ench1fix: the ten base items get a floor CAP at the default (not an exemption)")
    ea, eb = a.get("EDGES", []), b.get("EDGES", [])
    K.check(all(e in eb for e in ea), "K every 0.2.1 guard edge kept (%d)" % len(ea))
    new = [e for e in eb if e not in ea]
    seed = b.get("SEED", [])
    listed = set(l.split("=", 1)[0] for l in seed if "=" in l and not l.startswith("#"))
    want = []
    for rid, inp, outp, q, kr, fw in EN.reverse_rows(list(EN.TABLE) + list(EN.TABLE_ALLOYS)):
        if inp in listed and outp in listed:
            want.append((inp, outp, q))
    got = []
    for e in eb:
        m_ = re.match(r"^[0-9.e-]+\|([0-9.]+):([A-Za-z0-9_]+)>([0-9.]+):([A-Za-z0-9_]+)$", e)
        if m_:
            got.append((m_.group(2), m_.group(4), int(float(m_.group(3)))))
    K.check(all(re.match(r"^[0-9.e-]+\|[0-9.]+:[A-Za-z0-9_]+>[0-9.]+:[A-Za-z0-9_]+$", e) for e in new), "K every new edge is a one-input one-output recipe: %s" % [e for e in new if not re.match(r"^[0-9.e-]+\|[0-9.]+:[A-Za-z0-9_]+>[0-9.]+:[A-Za-z0-9_]+$", e)][:3])
    miss = sorted(set(want) - set(got))
    K.check(not miss, "K every listed reverse / pocket recipe is a guard edge (%d of %d): missing %s" % (len(set(want) & set(got)), len(want), miss[:4]))
    K.check(("Skyy_Ench_Copper", "Ingredient_Bar_Copper", 100) in got and ("Ingredient_Life_Essence_Concentrated", "Ingredient_Life_Essence", 100) in got,
            "K the Copper unpack + the vanilla pair unpack are edges")
    K.check(a.get("SEED") == b.get("SEED"), "K the product table (SEED) is identical - no price default moved")
    sa, sb = dict(zip(a.get("SC_ID", []), a.get("SC_V", []))), dict(zip(b.get("SC_ID", []), b.get("SC_V", [])))
    ba, bb = dict(zip(a.get("BX_ID", []), a.get("BX_V", []))), dict(zip(b.get("BX_ID", []), b.get("BX_V", [])))
    K.check(all(sb.get(k) == v for k, v in sa.items()) and set(a.get("NF_ID", [])) <= set(b.get("NF_ID", [])) and all(bb.get(k, 0) >= v for k, v in ba.items()),
            "K every 0.2.1 sell cap / floor exemption / buy-side raise kept as it was")
    K.notes.append("K buy-side raises added / changed %s" % sorted((k, v) for k, v in bb.items() if ba.get(k) != v))
    K.notes.append("K sell caps added %s, changed %s, removed %s; floor exemptions added %s, removed %s" % (
        sorted(set(sb) - set(sa)), sorted(k for k in sa if k in sb and sa[k] != sb[k]), sorted(set(sa) - set(sb)),
        sorted(set(b.get("NF_ID", [])) - set(a.get("NF_ID", []))), sorted(set(a.get("NF_ID", [])) - set(b.get("NF_ID", [])))))
    K.save()


def run_guard(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    J = lambda n: JClass(PKG + n)
    d = os.path.join(scratch, "guard_%s" % os.path.basename(jar)[:-4], "Skyy_SkyyBazaar")
    t21().bz_prep(J, d)
    C, M = J("Catalog"), J("Market")
    K.eq(int(C.warnLoops(float(M.SPREAD))), 0, "G no guard edge pays at the default prices")
    cu = C.get("Skyy_Ench_Copper")
    old = float(cu.base)
    r = C.setGuarded("Skyy_Ench_Copper", 1.0, False)
    is_new = os.path.basename(jar) == os.path.basename(JAR)
    if is_new:
        K.check(r is not None and "Enchanted Copper" in str(r) and "Copper Ingot" in str(r) and abs(float(C.get("Skyy_Ench_Copper").base) - old) < 1e-9,
                "G UNPACK: Enchanted Copper fixed at 1 coin is refused, the old price %g kept: %s" % (old, r))
    else:
        K.check(r is None, "G (0.2.1 jar) the same price is taken - its guard does not know the reverse recipe: %s" % r)
        C.setGuarded("Skyy_Ench_Copper", old, False)
    K.save()


def run_guard_old(out, jar, scratch, home):
    """the same steps on the 0.2.1 jar (a child of its own: one JVM per jar)"""
    run_guard(out, OLD_JAR, scratch, home)


def run_quote(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    J = lambda n: JClass(PKG + n)
    d = os.path.join(scratch, "fresh", "Skyy_SkyyBazaar")
    t21().bz_prep(J, d)
    C, M = J("Catalog"), J("Market")
    ids = set(str(p.id) for p in C.all())
    bad = [i for i in ids if int(M.quote(i, 1, True)) <= int(M.quote(i, 1, False))]
    K.check(not bad and len(ids) >= 540, "Q every product (%d): instant buy > instant sell (%s)" % (len(ids), bad[:4]))
    pairs = [(inp, outp) for rid, inp, outp, q, kr, fw in EN.reverse_rows(list(EN.TABLE) + list(EN.TABLE_ALLOYS)) if q == 100 and inp in ids and outp in ids]
    worst_u = worst_p = (0.0, None)
    for e, b in pairs:
        be, se = float(M.quote(e, 1, True)), float(M.quote(e, 1, False))
        bb, sb = float(M.quote(b, 100, True)), float(M.quote(b, 100, False))
        u, p_ = sb / be, se / bb
        worst_u = max(worst_u, (u, e))
        worst_p = max(worst_p, (p_, e))
    K.check(len(pairs) >= 100 and worst_u[0] < 1.0 and worst_p[0] < 1.0,
            "Q %d pairs at the jar's own quotes: worst unpack return %.3f (%s), worst pack return %.3f (%s) - neither pays" % (len(pairs), worst_u[0], worst_u[1], worst_p[0], worst_p[1]))
    K.notes.append("Q worst unpack %.3f %s; worst pack %.3f %s" % (worst_u + worst_p))
    K.save()


DEMANDS = (0.25, 0.5, 1.0, 2.0)
CAPPED10 = ["Ingredient_Charcoal", "Ingredient_Fibre", "Ingredient_Stick", "Plant_Crop_Corn_Item", "Plant_Crop_Wheat_Item", "Plant_Fruit_Berries_Red",
            "Plant_Petals_Blood", "Rock_Ice", "Soil_Clay", "Soil_Sand"]          # ench1fix: the floors the E1 sweep caps at the default


def _floor_quotes(jar_path, home, dst):
    """child helper (ench1fix): {minsell: {id: {demand: [buy1, sell1]}}} for every NFC_ID product + Stick / Copper; plus the unpack trip
    (buy 1 Enchanted, sell 100 base at demand 1) for every listed pair, at minimum sell 0..5"""
    from jpype import JClass
    HK.jvm([jar_path, B.SERVER_JAR], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    J = lambda n: JClass(PKG + n)
    t21().bz_prep(J, home)
    C, M, Cfg = J("Catalog"), J("Market"), J("BzCfg")
    Dbl = JClass("java.lang.Double")
    cap = [str(x) for x in getattr(C, "NFC_ID", [])] if any(str(f.getName()) == "NFC_ID" for f in C.class_.getDeclaredFields()) else []
    ids = set(str(p.id) for p in C.all())
    look = sorted(set(cap + CAPPED10 + ["Ingredient_Stick", "Soil_Sand", "Ingredient_Bar_Copper", "Ingredient_Fibre", "Plant_Crop_Wheat_Item"]) & ids)
    pairs = [(inp, outp) for rid, inp, outp, q, kr, fw in EN.reverse_rows(list(EN.TABLE) + list(EN.TABLE_ALLOYS)) if q == 100 and inp in ids and outp in ids]
    res = {"cap": cap, "q": {}, "unpack": {}}
    for ms in range(0, 6):
        Cfg.MINSELL = ms
        qm = {}
        for i in look:
            qd = {}
            for d in DEMANDS:
                M.F.put(i, Dbl(d))
                qd[str(d)] = [int(M.quote(i, 1, True)), int(M.quote(i, 1, False))]
            M.F.remove(i)
            qm[i] = qd
        res["q"][str(ms)] = qm
        worst = (0.0, None)
        for e, b in pairs:
            r = float(M.quote(b, 100, False)) / float(M.quote(e, 1, True))
            worst = max(worst, (r, e))
        res["unpack"][str(ms)] = list(worst)
    Cfg.MINSELL = 2
    json.dump(res, open(dst, "w"))


def run_floor(out, jar, scratch, home):
    K = HK.Child(out)
    env = dict(os.environ)
    res = {}
    for tag, jp in (("old", OLD_JAR), ("new", jar)):
        dst = os.path.join(scratch, "floor_%s.json" % tag)
        h = os.path.join(scratch, "floor_%s" % tag, "Skyy_SkyyBazaar")
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--floor-quotes", jp, h, dst], env=env, capture_output=True, text=True)
        K.check(p.returncode == 0 and os.path.isfile(dst), "F quotes of %s read: %s" % (os.path.basename(jp), p.stderr[-400:]))
        res[tag] = json.load(open(dst)) if os.path.isfile(dst) else {"cap": [], "q": {}, "unpack": {}}
    a, b = res["old"], res["new"]
    cap = b["cap"]
    K.check(sorted(cap) == sorted(CAPPED10) and not a["cap"], "F the 0.2.2 jar caps the 10 floors, 0.2.1 none")
    for ms in ("0", "1", "2"):
        same = [i for i in cap if a["q"].get(ms, {}).get(i) != b["q"].get(ms, {}).get(i)]
        K.check(not same, "F minimum sell %s: every capped product quotes exactly as in 0.2.1 at demand %s, buy and sell (differ: %s)" % (ms, "/".join(str(d) for d in DEMANDS), same[:4]))
    zero = [(i, b["q"]["2"][i]["0.25"]) for i in cap if b["q"]["2"][i]["0.25"][1] < 2]
    K.check(not zero, "F minimum sell 2 (default), demand 0.25: no capped product sells for under 2 coins (critic: Stick / Sand sold for 0): %s" % zero)
    for ms in ("3", "4", "5"):
        low = [(i, b["q"][ms][i]["0.25"][1]) for i in cap if b["q"][ms][i]["0.25"][1] < 2]
        K.check(not low, "F minimum sell %s: a capped product still sells for at least 2 at demand 0.25: %s" % (ms, low))
        cu = b["q"][ms].get("Ingredient_Bar_Copper", {}).get("0.25", [0, 0])[1]
        K.check(cu >= int(ms), "F minimum sell %s: a normal product (Copper Ingot) sells for at least %s at demand 0.25 (%d)" % (ms, ms, cu))
    worst_new = max(float(b["unpack"][ms][0]) for ms in b["unpack"])
    K.check(worst_new < 1.0, "F 0.2.2: buy 1 Enchanted -> sell the 100 never pays at minimum sell 0-5 (worst %.3f)" % worst_new)
    K.notes.append("F 0.2.2 worst unpack per minimum sell: %s" % dict((ms, "%.3f %s" % tuple(v)) for ms, v in sorted(b["unpack"].items())))
    K.notes.append("F 0.2.1 worst unpack per minimum sell (with the reverse recipes - why 0.2.1 must not run with Collections 0.2.34 at minimum sell 3+): %s"
                   % dict((ms, "%.3f %s" % tuple(v)) for ms, v in sorted(a["unpack"].items())))
    K.notes.append("F Stick at minimum sell 2, demand 0.25: 0.2.1 %s, 0.2.2 %s (buy, sell)" % (a["q"]["2"].get("Ingredient_Stick", {}).get("0.25"), b["q"]["2"].get("Ingredient_Stick", {}).get("0.25")))
    K.save()


def _start(jar_path, home, dst):
    """child helper: one start of a jar's data steps on home, then a tree hash to dst"""
    from jpype import JClass
    HK.jvm([jar_path, B.SERVER_JAR], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    J = lambda n: JClass(PKG + n)
    t21().bz_prep(J, home)
    json.dump(dict((k, v) for k, v in HK.tree_hash(home).items()), open(dst, "w"))


def run_live(out, jar, scratch, home):
    K = HK.Child(out)
    other = home.rstrip("\\/") + "_old"
    shutil.copytree(home, other)
    env = dict(os.environ)
    hs = {}
    for tag, jp, h in (("old", OLD_JAR, other), ("new1", jar, home), ("new2", jar, home)):
        dst = os.path.join(scratch, "live_%s.json" % tag)
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--start", jp, h, dst], env=env, capture_output=True, text=True)
        K.check(p.returncode == 0, "D %s start ran: %s" % (tag, p.stderr[-300:]))
        hs[tag] = json.load(open(dst)) if os.path.isfile(dst) else {}

    def strip(t):
        return dict((k, v) for k, v in t.items() if not k.startswith("config-history"))
    da = sorted(k for k in set(strip(hs["old"])) | set(strip(hs["new1"])) if strip(hs["old"]).get(k) != strip(hs["new1"]).get(k))
    tl = [k for k in da if k == "trades.log"]
    K.check(not [k for k in da if k != "trades.log"], "D the 0.2.2 start = the 0.2.1 start on the live data (files that differ: %s)" % da)
    if tl:
        a_ = open(os.path.join(other, "trades.log"), "rb").read()
        b_ = open(os.path.join(home, "trades.log"), "rb").read()
        K.notes.append("D trades.log differs (timestamps?): old %d bytes, new %d bytes" % (len(a_), len(b_)))
    K.check(hs["new1"] == hs["new2"], "D a second 0.2.2 start writes nothing (%s)" % sorted(k for k in set(hs["new1"]) | set(hs["new2"]) if hs["new1"].get(k) != hs["new2"].get(k))[:5])
    K.save()


if __name__ == "__main__":
    if "--dump-consts" in sys.argv:
        k = sys.argv.index("--dump-consts")
        _dump_consts(sys.argv[k + 1], sys.argv[k + 2])
        sys.exit(0)
    if "--floor-quotes" in sys.argv:
        k = sys.argv.index("--floor-quotes")
        _floor_quotes(sys.argv[k + 1], sys.argv[k + 2], sys.argv[k + 3])
        sys.exit(0)
    if "--start" in sys.argv:
        k = sys.argv.index("--start")
        _start(sys.argv[k + 1], sys.argv[k + 2], sys.argv[k + 3])
        sys.exit(0)
    HK.run(name="SkyyBazaar", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("catalog", run_catalog), ("guard", run_guard), ("guardold", run_guard_old), ("quote", run_quote),
                   ("floor", run_floor), ("live", run_live)], live=(LIVE, "Skyy_SkyyBazaar"), script=__file__)
