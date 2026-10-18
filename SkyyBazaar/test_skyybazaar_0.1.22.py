"""Harness for SkyyBazaar 0.1.22 (round baz22: alloys give 2 bars - each alloy priced per bar of a 2-bar smelt, the Bronze sell cap halved;
the six Enchanted alloys listed + migrate122; the sort on tools/tier_tags.py TT_VERSION 3 with the prices kept; tools/bazaar_0_1_22_patch.py).
Deploys with SkyyWorldGen 0.7.5, SkyyCollections 0.2.28 and SkyyGear 0.3.29 (the level-bands batch).
Build first: python tools/bazaar_0_1_22_patch.py && python SkyyBazaar/build_skyybazaar_0.1.22.py --with SkyyWorldGen/SkyyWorldGen-0.7.5.jar
             --with SkyyCollections/SkyyCollections-0.2.28.jar --with SkyyGear/SkyyGear-0.3.29.jar

    python SkyyBazaar/test_skyybazaar_0.1.22.py [--jar <0.1.22 jar>] [--wg <SkyyWorldGen 0.7.5 jar>] [--coll <SkyyCollections 0.2.28 jar>]
                                                [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py + tools/hub_tab_harness.py engine stand-ins; -Xverify:all everywhere):
  A     verify   every class loads + initialises
  C     compare  0.1.21 -> 0.1.22: Catalog (NEW0122 / migrate122 / its marker + the inlined PROC_SPEC / EDGES / sell caps / seed lines),
                 BzMarket (TIER_SPEC + lvTier on TT_VERSION 3) + the version texts / setup differ
  TT    BzMarket.TIER_SPEC = tools/tier_tags.py TT_VERSION 3 ROWS exactly; BzMarket.lvTier / tier = TT.tier_for_level for every level 0-119
  OLD   the 0.1.21 jar (the SET pin) on a fresh folder: every product's buy / sell quote (1 unit, demand 1.0) at premium 0 / 20 / 22 x
        minimum sell 0 / 2 / 5 -> prices_0121.json
  ALLOY the 0.1.22 jar, same grid:
        (1) every zone alloy = AUTO, 2 bars from 1 + 1 ingots, price = (the two ingots' RAW values + fuel) / 2 x (1 + premium);
        (2) per alloy (Bronze included): buy the two ingots -> 2 bars -> sell LOSES; buying 2 bars costs more than the two ingots sell;
        (3) the six Enchanted alloys: listed (Mining), AUTO, 2 from 1 + 1 Enchanted parents on SkyyAlloy, price = (the parents' RAW values +
            fuel) / 2 x (1 + premium) (premium ONCE - Enchanted Bronze 5,670 at 20 %, not 100 x 180); BOTH routes lose at every grid point:
            buy the two Enchanted parents -> 2 -> sell, and buy 100 alloys -> compress -> sell 1; 2 never buy below the parents' sale;
        (4) Catalog.EDGES: every alloy + Enchanted alloy smelt at 2; loopingEdges finds NO paying recipe at any grid point;
        (5) SkyyWorldGen 0.7.5: the 12 Alloy_*.json give 2 of the ids priced here; SkyyCollections 0.2.28: the six items' 100 -> 1 recipes;
        (6) THE PRICE DIFF vs prices_0121.json: the moved products = the re-price rows (Catalog.M122P_*: crops / seeds / Eternal seeds / logs /
            saplings on the TT_VERSION 3 tiers + Bronze 180 -> 57; OLD = the 0.1.21 default, NEW = the 0.1.22 one, a fresh start holds NEW),
            the 6 alloys, and the AUTO goods made from them (Enchanted crops / logs, bolts ...) - anything else fails; + the 6 new Enchanted
            alloys. The full table goes to tools/dev/scratch/baz22/price_table.txt
  LIVE  the 0.1.22 jar on a scratch COPY of the live Skyy_SkyyBazaar (read-only source), started twice like setup(): migrate122 appends
        exactly the six NEW0122 seed lines at the end (every old line + line ending kept, only the AUTO zone alloy price fields move), the
        history snapshot = the old bytes, trades.log only APPENDED (MIGRATE-0.1.22 lines with the undo), pricing.properties only APPENDED
        (the marker), market.properties (demand, counters) + config.properties byte-identical; start 2 writes nothing
        + migrate122p: every old line still at its 0.1.21 default moves to the 0.1.22 one (a MIGRATE-0.1.22 PRICE line with the undo each),
        every other old line moves only as an AUTO good following its inputs; the first history snapshot = the old bytes
  LIVE2 the same with an admin's hand-made Enchanted Bronze line already in the file (kept, one line for that id, the other 5 appended) and an
        admin's own Lettuce price 11 (a re-priced product): KEPT byte for byte + a MIGRATE-0.1.22 KEPT line
  AA    engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import hub_tab_harness as H
import skyyench as EN

_argv = list(sys.argv)
_sp = importlib.util.spec_from_file_location("bz0120test", os.path.join(HERE, "test_skyybazaar_0.1.20.py"))
T20 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T20)       # LIVE_SAVES
sys.argv = _argv

VERSION = "0.1.22"
OLD_VERSION = "0.1.21"
PKG = "com.skyy.bazaar."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBazaar-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyBazaar-%s.jar" % OLD_VERSION)          # the SET pin
WG_JAR = os.path.abspath(HK.arg("--wg", os.path.join(ROOT, "SkyyWorldGen", "SkyyWorldGen-0.7.5.jar")))
COLL_JAR = os.path.abspath(HK.arg("--coll", os.path.join(ROOT, "SkyyCollections", "SkyyCollections-0.2.28.jar")))
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "baz22", "t")))
LIVE = os.path.join(T20.LIVE_SAVES, "Skyy_SkyyBazaar")
EXPECT = {"Catalog": ["+f NEW0122", "+f MIGRATED122", "+f M122_LOG", "+m migrate122", "~m writeModes", "~m loadModes", "~m init", "~<clinit>",
                      "+f M122P_ID", "+f M122P_OLD", "+f M122P_NEW", "+f M122P_TXT", "+f M122P_OTXT", "+f MIGRATED122P", "+f M122P_LOG",
                      "+m migrate122p", "+m m122p", "+m m122now", "~m m115now", "~m migrate115"],   # 0.1.22 re-price
          "BzMarket": ["~m tiers", "~m lvTier"],                 # TIER_SPEC + the level bands of TT_VERSION 3 (TT phase)
          "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],    # the version texts
          "SkyyBazaarPlugin": ["~m setup"]}                      # the ready line's version + migrate122
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = []
SPREAD = 0.10
ALLOY_OUT = 2
PREMS, FLOORS = (0, 20, 22), (0, 2, 5)
BRONZE = ("Ingredient_Bar_Bronze", "Ingredient_Bar_Copper", "Ingredient_Bar_Iron")
ZONE = [("Ingredient_Bar_Dusk_SkyWynn", "Ingredient_Bar_Thorium", "Ingredient_Bar_Lead_SkyWynn"),
        ("Ingredient_Bar_Azurvane_SkyWynn", "Ingredient_Bar_Cobalt", "Ingredient_Bar_Chromium_SkyWynn"),
        ("Ingredient_Bar_Cinder_SkyWynn", "Ingredient_Bar_Adamantite", "Ingredient_Bar_Slag_SkyWynn"),
        ("Ingredient_Bar_Lumen_SkyWynn", "Ingredient_Bar_Mithril", "Ingredient_Bar_Titanium_SkyWynn"),
        ("Ingredient_Bar_Electrum_SkyWynn", "Ingredient_Bar_Gold", "Ingredient_Bar_Silver")]
ALLOYS = [BRONZE] + ZONE
ALLOY_IDS = [a for a, x, y in ALLOYS]
# the Enchanted alloys: (id, Enchanted parent A, Enchanted parent B, the alloy ingot 100 of which compress into one)
EALLOYS = [(EN.PREFIX + t[0], EN.PREFIX + EN.ALLOY_PARENTS[t[0]][0], EN.PREFIX + EN.ALLOY_PARENTS[t[0]][1], t[2]) for t in EN.TABLE_ALLOYS]
EALLOY_IDS = [e[0] for e in EALLOYS]
ESTIMATE = {"Skyy_Ench_Bronze": 5670, "Skyy_Ench_Dusk": 25920, "Skyy_Ench_Azurvane": 77760, "Skyy_Ench_Cinder": 259200,
            "Skyy_Ench_Lumen": 777600, "Skyy_Ench_Electrum": 9180}       # the SkyyCollections 0.2.28 builder's estimates (premium 20)
MIGS = ("migrate", "migrate14", "migrate19", "migrate110", "migrate114", "migrate115", "migrate116", "migrate119", "migrate120", "migrate122p", "migrate122")


def bz_prep(E, J, home, migs=MIGS):
    """the jar's data steps exactly as SkyyBazaarPlugin.setup() runs them (every one-time update, load, reprice, publish)"""
    from jpype import JClass
    J("BzUtil").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyBazaar")
    d = JClass("java.nio.file.Paths").get(home)
    os.makedirs(home, exist_ok=True)
    C = J("Catalog")
    C.FILE = d.resolve("products.properties")
    C.PFILE = d.resolve("pricing.properties")
    J("Market").FILE = d.resolve("market.properties")
    J("Market").LOGFILE = d.resolve("trades.log")
    J("BzCfg").load(d)
    logs = []
    for m in migs:
        r = getattr(C, m)()
        if m == "migrate122p":
            logs += [str(x) for x in list(C.M122P_LOG)] if r is not None else []
        if m == "migrate122":
            logs += [str(x) for x in list(C.M122_LOG)] if r is not None else []
    C.load()
    J("Market").load()
    C.reprice()
    J("Market").publishAll()
    C.flushIfDirty()
    for x in logs:                # setup() logs the migration lines after the start; the BzTick writes the queue - flushed here at once
        J("Market").log(x)
    C.M122_LOG.clear()
    C.M122P_LOG.clear()
    J("Market").flushLog()
    J("BzConfirm").load(d)
    return logs


def grid(J, fn):
    """fn(premium, floor) at every grid point (BzCfg.PREMIUM + MINSELL set, Catalog.reprice); the defaults put back"""
    Cfg, C = J("BzCfg"), J("Catalog")
    p0, f0 = int(Cfg.PREMIUM), int(Cfg.MINSELL)
    out = {}
    for pr in PREMS:
        for fl in FLOORS:
            Cfg.PREMIUM = pr
            Cfg.MINSELL = fl
            C.reprice()
            out["%d/%d" % (pr, fl)] = fn(pr, fl)
    Cfg.PREMIUM, Cfg.MINSELL = p0, f0
    C.reprice()
    return out


def quotes(J):
    C, M = J("Catalog"), J("Market")
    ids = sorted(str(p.id) for p in C.all())
    return grid(J, lambda pr, fl: dict((i, [int(M.quote(i, 1, True)), int(M.quote(i, 1, False)), round(float(C.get(i).base), 4)]) for i in ids))


def boot(scratch, jar, label):
    from jpype import JClass
    W = H.boot(scratch, jar, label)
    J = lambda n: JClass(PKG + n)
    W.E.br = J("HubBar").map()
    return W, J


def run_tt(out, jar, scratch, _home):
    import tier_tags as TT
    K = HK.Child(out)
    sp = importlib.util.spec_from_file_location("ah0113test", os.path.join(ROOT, "SkyyAuctions", "test_skyyauctions_0.1.13.py"))
    argv = list(sys.argv)
    A = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(A)
    sys.argv[:] = argv
    n = A.spec_in(jar, "com/skyy/bazaar/BzMarket.class")
    K.eq(TT.TT_VERSION, "3", "TT: built against tools/tier_tags.py TT_VERSION 3 (the level-bands batch)")
    K.eq(sorted(n.items()), sorted((i, TT.tier(i)) for i in TT.ROWS), "TT: BzMarket.TIER_SPEC = every tools/tier_tags.py row at its tier (%d rows)" % len(n))
    K.check(all(n.get(i) == TT.tier(i) for i in EALLOY_IDS + ["Plant_Crop_Mushroom_Cap_Brown", "Plant_Seeds_Mushroom"]),
            "TT: the Enchanted alloys + the Mushroom rows sort at their tier (%s)" % [(i, n.get(i)) for i in EALLOY_IDS])
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    from jpype import JClass
    M = JClass(PKG + "BzMarket")
    bad = [(l, x) for l in range(0, 120) for x in ("Weapon_Sword_Iron", "Armor_Onyxium_Chest", "Weapon_Sword_Lumen_SkyWynn", "Armor_Copper_Head")
           if int(M.lvTier(x, l)) != TT.tier_for_level(l, x)]
    K.eq(bad, [], "TT: BzMarket.lvTier = tools/tier_tags.py tier_for_level (TT_VERSION 3 bands) for every level 0-119")
    K.save()


def run_old(out, _jar, scratch, _home):
    K = HK.Child(out)
    W, J = boot(scratch, OLD_JAR, "old")
    T20.bz_prep(W.E, J, os.path.join(scratch, "home_old"))
    q = quotes(J)
    json.dump(q, open(os.path.join(scratch, "prices_0121.json"), "w"))
    K.check(len(q["20/2"]) > 500, "OLD: %d products quoted on 0.1.21 at %d grid points" % (len(q["20/2"]), len(q)))
    K.save()


def raw_of(C, i, pr):
    """the raw (premium-free) value of a product: an AUTO processed good's base / (1 + premium), a fixed one its base"""
    return float(C.get(i).base) / ((1 + pr / 100.0) if C.isProc(i) else 1.0)


def run_alloy(out, jar, scratch, _home):
    K = HK.Child(out)
    W, J = boot(scratch, jar, "alloy")
    bz_prep(W.E, J, os.path.join(scratch, "home_alloy"))
    C, M, Cfg = J("Catalog"), J("Market"), J("BzCfg")
    K.eq(int(Cfg.PREMIUM), 20, "ALLOY: the processed goods premium default stays 20")
    # (1) the zone alloys + (3) the Enchanted alloys: AUTO, 2 from 1 + 1
    for a, x, y in ZONE + [(e, pa, pb) for e, pa, pb, _b in EALLOYS]:
        pe = C.PROC_BY.get(a)
        ins = [[str(c) for c in list(z)] for z in list(pe[5])] if pe is not None else None
        K.check(pe is not None and bool(C.isAuto(a)) and str(pe[3]) == "SkyyAlloy" and float(pe[1]) == ALLOY_OUT and ins == [[x], [y]]
                and [float(v) for v in list(pe[4])] == [1.0, 1.0], "ALLOY: %s = AUTO, %d from 1 %s + 1 %s (outq %s)" % (a, ALLOY_OUT, x, y, None if pe is None else float(pe[1])))
    K.check(not bool(C.isAuto(BRONZE[0])) and C.PROC_BY.get(BRONZE[0]) is None, "ALLOY: Bronze stays a FIXED product (not processed)")
    K.eq([(e, str(C.get(e).cat) if C.get(e) else None) for e in EALLOY_IDS], [(e, "Mining") for e in EALLOY_IDS], "ALLOY: the six Enchanted alloys are listed in Mining")
    mi = [str(p.id) for p in C.inCat("Mining")]
    K.check(all(mi.index(e) == mi.index(pb) + 1 for e, pa, pb, _b in EALLOYS), "ALLOY: each Enchanted alloy sits right after its second parent in Mining")
    K.eq(dict((e, round(float(C.get(e).base), 2)) for e in EALLOY_IDS), dict((e, float(v)) for e, v in ESTIMATE.items()),
         "ALLOY: the Enchanted alloys' default prices = the SkyyCollections builder's estimates (half the two Enchanted parents, premium once)")
    K.check(abs(float(C.get("Skyy_Ench_Bronze").base) - 100 * 180.0) > 10000, "ALLOY: Enchanted Bronze is NOT 100 x the old fixed Bronze 180")
    # the price rule (fuel included): base x 2 / (1 + p) - (raw A + raw B) = the fuel share >= 0, the same at every premium
    g = grid(J, lambda pr, fl: dict((a, float(C.get(a).base) * ALLOY_OUT / (1 + pr / 100.0) - raw_of(C, x, pr) - raw_of(C, y, pr))
                                    for a, x, y in ZONE + [(e, pa, pb) for e, pa, pb, _b in EALLOYS]))
    for a in [z[0] for z in ZONE] + EALLOY_IDS:
        vs = [g[k][a] for k in g]
        K.check(min(vs) > -0.1 and max(vs) - min(vs) < 0.2 + 1e-5 * max(abs(v) for v in vs) + 0.05 * abs(vs[0]),
                "ALLOY: %s x2 = its two parents' raw value + fuel %.2f (every premium; spread %.3f)" % (a, vs[0], max(vs) - min(vs)))
    # (2) + (3) no buy-smelt-sell / buy-compress-sell loop
    bad = []

    def loops(pr, fl):
        r = []
        for a, x, y in ALLOYS + [(e, pa, pb) for e, pa, pb, _b in EALLOYS]:
            buy_in = int(M.quote(x, 1, True)) + int(M.quote(y, 1, True))
            sell_in = int(M.quote(x, 1, False)) + int(M.quote(y, 1, False))
            sell2, buy2 = int(M.quote(a, ALLOY_OUT, False)), int(M.quote(a, ALLOY_OUT, True))
            r.append((a, buy_in, sell2, sell_in, buy2))
            if not sell2 < buy_in:
                bad.append((pr, fl, a, "sell 2 %d >= buy the parents %d" % (sell2, buy_in)))
            if not buy2 > sell_in:
                bad.append((pr, fl, a, "buy 2 %d <= sell the parents %d" % (buy2, sell_in)))
        for e, pa, pb, base in EALLOYS:
            b100, s1 = int(M.quote(base, EN.RATIO, True)), int(M.quote(e, 1, False))
            r.append((e + " (compress)", b100, s1, 0, 0))
            if not s1 < b100:
                bad.append((pr, fl, e, "sell 1 %d >= buy %d %s %d" % (s1, EN.RATIO, base, b100)))
        return r
    lg = grid(J, loops)
    K.eq(bad, [], "ALLOY: every alloy (6) + Enchanted alloy (6) at premium %s x floor %s: buy the parents -> 2 -> sell LOSES, 2 cost more than the parents "
                  "sell, buy 100 alloys -> compress -> sell 1 LOSES" % (PREMS, FLOORS))
    print("ALLOY table (coins, demand 1.0; buy in = buy 1 + 1 parents (compress: 100 alloys), sell = the 2 it makes (compress: 1); ratio = sell / buy in):")
    for k in ("0/0", "20/2", "22/5"):
        print("  premium/floor %s" % k)
        for a, bi, s2, si, b2 in lg[k]:
            print("   %-40s buy in %9d  sell %9d  (x%.3f)   sell parents %9d  buy 2 %9d" % (a, bi, s2, s2 / float(bi), si, b2))
    K.notes.append("ALLOY worst ratio sell / buy in: %.3f" % max(s2 / float(bi) for k in lg for a, bi, s2, si, b2 in lg[k]))
    # (4) the price guard's edges
    edges = [str(e) for e in list(C.EDGES)]
    # an edge = "secs|q:cand,cand;q:cand>q:out;q:out"; the smelts = the 2-input edges that make an alloy / Enchanted alloy
    sm_e = [e for e in edges if ">" in e and len(e.split("|", 1)[1].split(">")[0].split(";")) == 2
            and any(o.split(":")[1] in ALLOY_IDS + EALLOY_IDS for o in e.split(">")[1].split(";"))]
    K.check(len(sm_e) >= len(ZONE) + len(EALLOYS) and all(all(o.split(":")[0] in ("2", "2.0") for o in e.split(">")[1].split(";")) for e in sm_e),
            "ALLOY: the price guard's alloy + Enchanted alloy smelt edges make %d (%d: %s)" % (ALLOY_OUT, len(sm_e), sm_e[:2]))
    lp = grid(J, lambda pr, fl: int(C.loopingEdges(SPREAD).size()))
    K.eq(dict((k, v) for k, v in lp.items() if v), {}, "ALLOY: Catalog.loopingEdges finds no paying recipe at any grid point (%d edges)" % len(edges))
    # (5) the SET jars' recipes = the ones priced here
    z = zipfile.ZipFile(WG_JAR)
    wg = {}
    for n in z.namelist():
        if n.startswith("Server/Item/Recipes/") and "/Alloy_" in n and n.endswith(".json"):
            d = json.loads(z.read(n).decode("utf-8-sig"))
            o = (d.get("Output") or [{}])[0]
            wg[o.get("ItemId")] = (o.get("Quantity"), sorted(i.get("ItemId") for i in d.get("Input") or []), [b.get("Id") for b in d.get("BenchRequirement") or []])
    want = dict((a, (ALLOY_OUT, sorted([x, y]), ["SkyyAlloy"])) for a, x, y in ALLOYS + [(e, pa, pb) for e, pa, pb, _b in EALLOYS])
    K.eq(dict((a, wg.get(a)) for a in want), want, "ALLOY: %s's 12 alloy recipes give %d from the same two parents on SkyyAlloy" % (os.path.basename(WG_JAR), ALLOY_OUT))
    zc = zipfile.ZipFile(COLL_JAR)
    have = dict((n.rsplit("/", 1)[-1][:-5], n) for n in zc.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    got = dict((e, (json.loads(zc.read(have[e]).decode("utf-8-sig")).get("Recipe") or {}).get("Input")) if e in have else None for e, pa, pb, b in EALLOYS)
    K.eq(got, dict((e, [{"ItemId": b, "Quantity": EN.RATIO}]) for e, pa, pb, b in EALLOYS), "ALLOY: %s ships the six with their 100 -> 1 recipes" % os.path.basename(COLL_JAR))
    sc = dict((str(i), float(v)) for i, v in zip(C.SC_ID, C.SC_V))
    K.check(abs(sc.get(BRONZE[0], 0) - 56.59) < 0.005, "ALLOY: Bronze sell cap %.2f (0.1.21: 113.19)" % sc.get(BRONZE[0], 0))
    # (6) THE PRICE DIFF vs 0.1.21
    old = json.load(open(os.path.join(scratch, "prices_0121.json")))
    new = quotes(J)
    moved, gone = {}, []
    for k in old:
        for i, v in old[k].items():
            if i not in new[k]:
                gone.append(i)
            elif new[k][i][:2] != v[:2]:
                moved.setdefault(i, []).append((k, v[:2], new[k][i][:2]))
    K.eq(sorted(set(gone)), [], "PRICE: every 0.1.21 product is still listed")
    K.eq(sorted(set(new["20/2"]) - set(old["20/2"])), sorted(EALLOY_IDS), "PRICE: the only new products are the six Enchanted alloys")
    rep_ids = set(str(x) for x in C.M122P_ID)
    rp = dict((str(i), (float(o), float(n))) for i, o, n in zip(C.M122P_ID, C.M122P_OLD, C.M122P_NEW))
    K.eq(dict((i, round(float(old["20/2"][i][2]), 4)) for i in rp), dict((i, round(o, 4)) for i, (o, n) in rp.items()), "PRICE: every re-price row's OLD value = the 0.1.21 default")
    K.eq(dict((i, round(float(new["20/2"][i][2]), 4)) for i in rp), dict((i, round(n, 4)) for i, (o, n) in rp.items()), "PRICE: every re-price row's NEW value = the 0.1.22 default")
    fed = set(rep_ids) | set(ALLOY_IDS)
    for _r in range(10):            # AUTO processed goods follow their inputs (Enchanted crops / logs, planks ...)
        for i in list(new["20/2"]):
            pe = C.PROC_BY.get(i)
            if pe is not None and any(str(c) in fed for x in list(pe[5]) for c in list(x)):
                fed.add(i)
    other = sorted(i for i in moved if i not in fed)
    K.eq(other, [], "PRICE: only the re-priced rows (%d), the 6 alloys and the AUTO goods made from them move (%d products x %d points)"
         % (len(rep_ids), len(old["20/2"]), len(new)))
    K.check(new["20/2"][BRONZE[0]][2] == 57.0 and 55 <= new["20/2"][BRONZE[0]][0] <= 66 and new["20/2"][BRONZE[0]][1] == int(56.59 * (1 - SPREAD)),
            "PRICE: Bronze base 180 -> 57, buys for ~60 now, sells from its cap 56.59 (%s; 0.1.21 %s)" % (new["20/2"][BRONZE[0]], old["20/2"][BRONZE[0]]))
    K.check(sorted(i for i in moved if i in ALLOY_IDS) == sorted(ALLOY_IDS), "PRICE: all 6 alloys moved: %s" % sorted(i for i in moved if i in ALLOY_IDS))
    K.check(all(float(C.get(i).base) == rp[i][1] for i in rp), "PRICE: a FRESH 0.1.22 start holds every re-priced default (no older update moved one back)")
    tab = []
    for i in sorted(moved, key=lambda i: (str(C.get(i).cat), i)):
        o, n = old["20/2"][i], new["20/2"][i]
        tab.append("%s|%s|%g|%g|%d|%d|%d|%d" % (i, str(C.get(i).cat), o[2], n[2], o[0], n[0], o[1], n[1]))
    open(os.path.join(ROOT, "tools", "dev", "scratch", "baz22", "price_table.txt"), "w").write("\n".join(tab) + "\n")
    K.notes.append("PRICE: %d products moved (table id|tab|base old|base new|buy old|buy new|sell old|sell new at premium 20 / floor 2)" % len(tab))
    print("PRICE old -> new (1 unit, demand 1.0; buy / sell; base) at premium 20 / floor 2 (the defaults) and premium 0 / floor 0:")
    for a in ALLOY_IDS:
        for k in ("20/2", "0/0"):
            o, n = old[k][a], new[k][a]
            print("   %-34s %-5s buy %7d -> %7d   sell %7d -> %7d   base %10.2f -> %10.2f" % (a, k, o[0], n[0], o[1], n[1], o[2], n[2]))
    print("PRICE new Enchanted alloys (buy / sell; base) at 20/2 and 0/0:")
    for e in EALLOY_IDS:
        print("   %-34s 20/2 buy %8d sell %8d base %10.2f | 0/0 buy %8d sell %8d base %10.2f" % ((e,) + tuple(new["20/2"][e]) + tuple(new["0/0"][e])))
    K.notes.append("PRICE moved: %s" % ", ".join("%s %s->%s" % (a, old["20/2"][a][:2], new["20/2"][a][:2]) for a in ALLOY_IDS))
    K.save()


def live_run(K, jar, scratch, home, label, hand=None):
    W, J = boot(scratch, jar, label)
    C, M = J("Catalog"), J("Market")
    fp = os.path.join(home, "products.properties")
    if hand is not None:
        raw = open(fp, "rb").read()
        nl0 = b"\r\n" if b"\r\n" in raw else b"\n"
        open(fp, "wb").write(raw + (b"" if raw.endswith(b"\n") else nl0) + hand + nl0)
    names = ("products.properties", "pricing.properties", "market.properties", "trades.log", "config.properties")
    before = dict((n, open(os.path.join(home, n), "rb").read()) for n in names if os.path.isfile(os.path.join(home, n)))
    hd = os.path.join(home, "config-history")
    bak0 = set(os.listdir(hd)) if os.path.isdir(hd) else set()
    K.check(b"migrated.0.1.20=" in before["pricing.properties"] and b"migrated.0.1.22=" not in before["pricing.properties"], "%s: the live copy is a 0.1.20 / 0.1.21 folder" % label)
    logs = bz_prep(W.E, J, home)
    after = dict((n, open(os.path.join(home, n), "rb").read()) for n in names if os.path.isfile(os.path.join(home, n)))
    for n in ("market.properties", "config.properties"):
        if n in before:
            K.check(after.get(n) == before[n], "%s: %s byte-identical (player demand / counters / settings untouched)" % (label, n))
    for n in ("pricing.properties", "trades.log"):
        K.check(after[n].startswith(before[n]), "%s: %s only appended to (%d -> %d bytes)" % (label, n, len(before[n]), len(after[n])))
    K.check(b"migrated.0.1.22=" in after["pricing.properties"], "%s: the migrated.0.1.22 marker is written" % label)
    tl = after["trades.log"][len(before["trades.log"]):].decode("utf-8", "replace")
    want_new = [e for e in EALLOY_IDS if hand is None or not hand.startswith(e.encode() + b"=")]
    K.check(tl.count("MIGRATE-0.1.22 ADDED ") == len(want_new) and ("MIGRATE-0.1.22 added %d already %d" % (len(want_new), len(EALLOY_IDS) - len(want_new))) in tl
            and "undo" in tl, "%s: trades.log has the MIGRATE-0.1.22 head + %d ADDED lines with the undo" % (label, len(want_new)))
    b, a = before["products.properties"], after["products.properties"]
    nl = b"\r\n" if b"\r\n" in b else b"\n"
    bl, al = b.rstrip(nl).split(nl), a.rstrip(nl).split(nl)
    K.eq([x.split(b"=")[0].decode() for x in al[len(bl):]], want_new, "%s: exactly the new Enchanted alloy seed lines appended at the end, in NEW0122 order" % label)
    K.check(a.endswith(nl) and (nl == b"\n" or b"\n" not in a.replace(b"\r\n", b"")), "%s: line endings kept (%r)" % (label, nl))
    diff = [(x, y) for x, y in zip(bl, al[:len(bl)]) if x != y]
    ids = [x.split(b"=")[0].decode("latin-1") for x, y in diff]
    rp = dict((str(i), (float(o), float(n), str(t))) for i, o, n, t in zip(C.M122P_ID, C.M122P_OLD, C.M122P_NEW, C.M122P_TXT))
    K.check(all(x.rsplit(b",", 1)[1] == y.rsplit(b",", 1)[1] and x.split(b",")[0] == y.split(b",")[0] for x, y in diff),
            "%s: of the old lines only price fields move (id, tab, name, line endings kept)" % label)
    badd = []
    for x, y in diff:
        i = x.split(b"=")[0].decode("latin-1")
        po, pn = float(x.split(b",")[1]), float(y.split(b",")[1])
        if i in rp and abs(po - rp[i][0]) < 1e-9 and abs(pn - rp[i][1]) < 1e-9:
            continue                     # migrate122p: a 0.1.21 default -> the 0.1.22 default
        if bool(C.isAuto(i)):
            continue                     # an AUTO processed good follows its inputs (the reprice tick writes it)
        badd.append((i, po, pn))
    K.eq(badd, [], "%s: every moved old line is a re-priced default (0.1.21 -> 0.1.22) or an AUTO good following its inputs" % label)
    keptl = []
    for x in bl:
        i = x.split(b"=")[0].decode("latin-1")
        if i in rp and x.count(b",") >= 2:
            po = float(x.split(b",")[1])
            if abs(po - rp[i][0]) > 1e-9 and abs(po - rp[i][1]) > 1e-9:
                keptl.append(i)
                K.check(x in al, "%s: %s's hand-set price %g is KEPT" % (label, i, po))
    K.check(all(("MIGRATE-0.1.22 KEPT " + i + " ") in tl for i in keptl), "%s: each kept hand-set price is logged (%s)" % (label, keptl))
    moved22 = [x.split(b"=")[0].decode() for x, y in diff if x.split(b"=")[0].decode() in rp]
    K.check(all(("MIGRATE-0.1.22 PRICE %s %s -> %s (undo: /bazaaradmin price %s " % (i, "%g" % rp[i][0], rp[i][2], i)) in tl for i in moved22),
            "%s: each re-priced line has its MIGRATE-0.1.22 PRICE line with the undo (%d)" % (label, len(moved22)))
    K.notes.append("%s: %d re-priced lines moved, %d hand-set kept (%s)" % (label, len(moved22), len(keptl), keptl))
    K.notes.append("%s products.properties: %d old lines moved: %s" % (label, len(diff), "; ".join("%s -> %s" % (x.decode("latin-1"), y.split(b",")[1].decode("latin-1")) for x, y in diff)))
    K.eq(sum(1 for l in al for e in EALLOY_IDS if l.startswith(e.encode() + b"=")), len(EALLOY_IDS), "%s: one line per Enchanted alloy" % label)
    new_bak = sorted(set(os.listdir(hd)) - bak0)
    K.check(len(new_bak) == 2 and open(os.path.join(hd, new_bak[0]), "rb").read() == b,
            "%s: history snapshots first (migrate122p's = the old products.properties bytes; then migrate122's) (%s)" % (label, new_bak))
    K.check(all(str(C.get(e).cat) == "Mining" for e in EALLOY_IDS), "%s: the six are listed (Mining)" % label)
    bz = [l for l in bl if l.startswith(BRONZE[0].encode() + b"=")]
    K.check(len(bz) == 1 and (bz[0] in al if b",180," not in bz[0] else (bz[0].replace(b",180,", b",57,") in al)),
            "%s: Bronze's line 180 -> 57 (the 0.1.22 default; a hand-set price kept) (%s)" % (label, bz[0].decode("latin-1") if bz else None))
    K.check(abs(float(C.sellBase(C.get(BRONZE[0]))) - 56.59) < 0.005, "%s: Bronze sells from its cap 56.59 (base %.2f)" % (label, float(C.get(BRONZE[0]).base)))
    for x, y, z in ALLOYS + [(e, pa, pb) for e, pa, pb, _b in EALLOYS]:
        bi = int(M.quote(y, 1, True)) + int(M.quote(z, 1, True))
        s2 = int(M.quote(x, ALLOY_OUT, False))
        K.check(s2 < bi, "%s (saved demand factors): %s buy the 2 parents %d -> sell 2 %d loses" % (label, x, bi, s2))
    h0 = HK.tree_hash(home)
    bz_prep(W.E, J, home)
    K.eq(HK.tree_hash(home), h0, "%s: a second start writes nothing" % label)
    return logs


def run_live(out, jar, scratch, home):
    K = HK.Child(out)
    live_run(K, jar, scratch, home, "LIVE")
    K.save()


def run_live2(out, jar, scratch, home):
    K = HK.Child(out)
    fp = os.path.join(home, "products.properties")
    raw = open(fp, "rb").read()
    nl0 = b"\r\n" if b"\r\n" in raw else b"\n"
    old_l, new_l = nl0 + b"Plant_Crop_Lettuce_Item=Farming,9,Lettuce" + nl0, nl0 + b"Plant_Crop_Lettuce_Item=Farming,11,Lettuce" + nl0
    assert raw.count(old_l) == 1
    open(fp, "wb").write(raw.replace(old_l, new_l))      # an admin's own price on a re-priced product: kept + logged
    live_run(K, jar, scratch, home, "LIVE2", hand=b"Skyy_Ench_Bronze=Mining,4321,Enchanted Bronze Ingot")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyBazaar", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("tt", run_tt), ("old", run_old), ("alloy", run_alloy), ("live", run_live), ("live2", run_live2)],
           live=(LIVE, "Skyy_SkyyBazaar"), script=__file__)
