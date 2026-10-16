"""Harness for SkyyBazaar 0.1.15 (round bz0115: the FARMING tab order + saplings to FORAGING, every price x4.5 except the Eternal seeds +
its one-time update; tools/bazaar_0_1_15_patch.py). Build first:
python tools/bazaar_0_1_15_patch.py && python SkyyBazaar/build_skyybazaar_0.1.15.py

    python SkyyBazaar/test_skyybazaar_0.1.15.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.14 -> 0.1.15: exactly the listed members differ
  X   exec14   the 0.1.14 harness's exec phase (PRICES + CONFIRM over the engine stand-ins) on the 0.1.15 jar - ONE of its checks is
               about 0.1.14's prices ("products sit under the floor value": at x4.5 none does any more) and is answered by S instead
  M   mig14    the 0.1.14 harness's migrate phase (0.1.13 -> this jar without migrate115: the tier update, a fresh install) - its
               "P:" checks compare a FRESH install with 0.1.13 prices and are answered by S / M15 instead (listed as expected)
  S   scale    0.1.14 and 0.1.15 jars on fresh folders: SCALE = 4.5; every fixed price x4.5 exactly, every processed good x4.5 within
               its 0.01 price step, the 14 Eternal seed bags unchanged (buy quote too); the sell caps x4.5; with the floor OFF every
               product but the Eternal seeds sells 1 for >= 2; buy > sell; buy 1 / 64 then sell straight back never pays; the demand
               step per unit = 0.1.14's (impactCoins x4.5); the jar's own loop guard (loopingEdges / warnLoops) finds no paying recipe;
               the bridge publishes the new quotes; 20 sample products old -> new (buy 1 / sell 1)
  M15 mig15    the one-time update: 0.1.14 jar then 0.1.15 jar on the same folder (LF and CRLF): every 0.1.14 default -> x4.5 (the price
               text only; every other byte + line ending stays), an admin's price KEPT + logged, the Eternal seeds untouched, impactCoins
               10000 -> 45000 (market.properties' other lines stay), both config-history copies = the old bytes, the marker (survives
               writeModes), a second start changes nothing; an admin's impactCoins KEPT + logged; a lost marker re-runs as a no-op;
               0.1.13 -> 0.1.15 (migrate114 then migrate115) ends on the 0.1.15 defaults; a fresh install logs no PRICE / KEPT line
  O   order    0.1.14 and 0.1.15 jars on fresh folders: Farming = the crop groups (crop, Enchanted crop, seeds, Eternal seeds) by the crop's
               tier then name, then the rest by tier then name - worked out HERE from tools/tier_tags.py over the 0.1.14 jar's Farming tab;
               no sapling in Farming; every sapling in Foraging right after its log (or after the last log); every other tab = 0.1.14's
               order; every product still in a tab (the search walks the tabs); the seeded products.properties = 0.1.14's with only
               the prices x4.5; an admin's own line still lists (after the table's products)
  D   live     a scratch COPY of the live Skyy_SkyyBazaar (NewBetaTest): 0.1.14 quotes (on a second copy) -> the 0.1.15 start (what moved
               / was kept), samples old -> new, the Farming order + Foraging's saplings; a SECOND 0.1.15 start changes nothing
  SL  sell     (E) SELL <open tab> / SELL ALL TABS: Trader.sellInventory(<tab>) sells only that tab's products for each tab (preview =
               the sale; coins = each product's own quote), null = every tab; on the page: the labels (SELL FARMING / SELL MINING,
               SELL ALL TABS, no Sell inventory), two clicks with the gold Confirm sell, the 0.3 s double-click rule, the other button /
               Next / the 10 s timeout disarm, a market:veto walled (stamped) stack is never sold, demand moves, one trades.log SELL line
               per product, profile:busy refuses, nothing-to-sell texts
  AA  engine-access audit
Scratch: tools/dev/scratch/bz0115/harness (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, re, shutil, json, math, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.15"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBazaar-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyBazaar-0.1.14.jar")
JAR13 = os.path.join(HERE, "SkyyBazaar-0.1.13.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "bz0115", "harness")))
PKG = "com.skyy.bazaar."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyBazaar")
ADDED = []
EXPECT = {
    "Catalog": ["+f DSP", "+f DSP_KEY", "+f IMP_NEW", "+f IMP_OLD", "+f IMP_TXT", "+f M115_ID", "+f M115_IX", "+f M115_LOG", "+f M115_NEW",
                "+f M115_OLD", "+f M115_OTXT", "+f M115_TXT", "+f MIGRATED115", "+f MOVE", "+f MV_ID", "+f MV_SPEC", "+f SCALE", "+m histCopy",
                "+m m115", "+m m115now", "+m migrate115", "~<clinit>", "~m inCat", "~m init", "~m loadModes", "~m m114now", "~m migrate114",
                "~m migrate14", "~m tabsOf", "~m writeModes"],
    "CfgFn": ["~m opExport"],                      # the version text
    "CfgRows": ["~<clinit>", "~m header"],         # the version text + (fixer 2) the floor row's help: a floor change never rescales
    "Market": ["~<clinit>", "~m load"],            # the impactCoins default 10000 -> 45000
    "SkyyBazaarPlugin": ["~m setup"],              # the version text + migrate115
    # E: SELL <tab> + SELL ALL TABS - preview0 / preview / sellInventory take the tab (null = every tab), + pick; the page's sell buttons
    "Trader": ["+m pick", "+m preview", "+m preview0", "+m sellInventory", "-m preview", "-m preview0", "-m sellInventory"],
    "BzPage": ["+f confirmCat", "+f confirmWhat", "~m handleDataEvent", "~m render"],
}
SAMPLES = ["Rubble_Stone", "Rock_Stone_Cobble", "Ore_Copper", "Ingredient_Bar_Copper", "Ore_Iron", "Ingredient_Bar_Iron", "Ore_Adamantite",
           "Wood_Oak_Trunk", "Plant_Sapling_Oak", "Ingredient_Tree_Sap", "Plant_Crop_Wheat_Item", "Skyy_Ench_Wheat", "Plant_Seeds_Wheat",
           "Plant_Seeds_Wheat_Eternal", "Plant_Crop_Potato_Item", "Plant_Seeds_Potato_Eternal", "Ingredient_Fibre", "Ingredient_Leather_Light",
           "Ingredient_Life_Essence", "Food_Fish_Raw", "Ingredient_Crystal_Blue"]

# the 0.1.14 harness (its Bz helper, exec + migrate phases) - loaded as a module, never edited
_spec = importlib.util.spec_from_file_location("bz014test", os.path.join(HERE, "test_skyybazaar_0.1.14.py"))
T14 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T14)
Bz, rb = T14.Bz, T14.rb


class Bz15(object):
    """the 0.1.15 jar's data classes in their own loader, started on folder d exactly like SkyyBazaarPlugin.setup() (its data steps,
    migrate115 included)"""

    def __init__(self, jar, d):
        from jpype import JClass
        self.L = T14.loader_for(jar)
        g = lambda n: JClass(PKG + n, loader=self.L)
        self.M, self.C, self.Cfg, self.U = g("Market"), g("Catalog"), g("BzCfg"), g("BzUtil")
        self.U.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyBazaar")
        P = JClass("java.nio.file.Paths")
        dp = P.get(d)
        os.makedirs(d, exist_ok=True)
        self.C.FILE = dp.resolve("products.properties")
        self.C.PFILE = dp.resolve("pricing.properties")
        self.M.FILE = dp.resolve("market.properties")
        self.M.LOGFILE = dp.resolve("trades.log")
        self.Cfg.load(dp)
        self.mig = [self.C.migrate(), self.C.migrate14(), self.C.migrate19(), self.C.migrate110()]
        self.m14log = [str(x) for x in self.C.M14_LOG]
        self.m114 = self.C.migrate114()
        self.m114log = [str(x) for x in self.C.M114_LOG]
        self.m115 = self.C.migrate115()
        self.m115log = [str(x) for x in self.C.M115_LOG]
        self.n = int(self.C.load())
        self.M.load()
        self.C.reprice()
        self.M.publishAll()
        self.C.flushIfDirty()
        self.M.flush()
        self.ids = [str(p.id) for p in self.C.all()]

    def q(self, i, n=1, buy=True):
        return int(self.M.quote(i, n, buy))


def tabs(b):
    return dict((str(c), [str(p.id) for p in b.C.inCat(c)]) for c in b.C.categories())


def eternal(i):
    return i.startswith("Plant_Seeds_") and i.endswith("_Eternal")


PRICE_RE = re.compile(rb"^([A-Za-z0-9_]+)=([^,]*),([^,]*)(,.*)?$")


def price_of(line):
    m = PRICE_RE.match(line.rstrip(b"\r"))
    return (m.group(1).decode(), float(m.group(3))) if m else (None, None)


def without_price(line):
    return re.sub(rb"^([^=]*=[^,]*,)[^,]*", rb"\1#", line)


# ------------------------------------------------------------------------------------------------------------------- X: exec14
def run_exec14(out, jar, scratch, home):
    """the 0.1.14 exec phase; its one check that needs a product UNDER the floor value cannot hold at x4.5 (none is) - it is listed
    here as expected and S checks the floor itself (with the floor off every product already sells for >= 2)"""
    T14.run_exec(out, jar, scratch, home)
    d = json.load(open(out))
    exp = [f for f in d["fails"] if f.startswith("PRICES: 0 products sit under the floor value")]
    d["fails"] = [f for f in d["fails"] if f not in exp]
    d["notes"].append("X: expected at x4.5 (answered by S): %s" % exp)
    d["ok"] += len(exp)
    json.dump(d, open(out, "w"), indent=1)


def run_mig14(out, jar, scratch, home):
    """the 0.1.14 migrate phase on this jar (T14.Bz never calls migrate115, so its 0.1.13 -> 0.1.14 part is exactly 0.1.14's update);
    its 'P:' block compares a FRESH 0.1.15 install (x4.5 prices) with 0.1.13's quotes - expected to differ, answered by S / M15"""
    T14.run_mig(out, jar, scratch, home)
    d = json.load(open(out))
    exp = [f for f in d["fails"] if f.startswith("P: ")]
    d["fails"] = [f for f in d["fails"] if f not in exp]
    d["notes"].append("M14: expected at x4.5 (answered by S / M15): %s" % [e[:160] for e in exp])
    d["ok"] += len(exp)
    json.dump(d, open(out, "w"), indent=1)


# ------------------------------------------------------------------------------------------------------------------- S: scale
def run_scale(out, jar, scratch, _home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    bo = Bz(OLD_JAR, os.path.join(scratch, "s14"), True)
    bn = Bz15(jar, os.path.join(scratch, "s15"))
    X = float(bn.C.SCALE)
    K.eq(X, 4.5, "S: SCALE = 4.5 (floor 2 / the cheapest 0.1.14 sale 0.45, up to 0.5)")
    K.eq(sorted(bn.ids), sorted(bo.ids), "S: the same %d products" % len(bn.ids))
    keep = [i for i in bn.ids if eternal(i)]
    K.eq(len(keep), 14, "S: 14 Eternal seed bags")
    bad, proc = [], 0
    for i in bn.ids:
        b14, b15 = float(bo.C.get(i).base), float(bn.C.get(i).base)
        if i in keep:
            ok = b15 == b14
        elif bool(bn.C.isProc(i)) and bool(bn.C.isAuto(i)):
            proc += 1
            ok = abs(b15 - b14 * X) <= 0.01 * X + 1e-9
        else:
            ok = abs(b15 - b14 * X) < 1e-9
        if not ok:
            bad.append((i, b14, b15))
    K.eq(bad[:10], [], "S: every fixed price x4.5 exactly, the %d processed goods x4.5 (0.01 step), the Eternal seeds unchanged" % proc)
    sc14 = dict((str(i), float(v)) for i, v in zip(bo.C.SC_ID, bo.C.SC_V))
    sc15 = dict((str(i), float(v)) for i, v in zip(bn.C.SC_ID, bn.C.SC_V))
    both = sorted(set(sc14) & set(sc15))
    K.eq([(i, sc14[i], sc15[i]) for i in both if abs(sc15[i] - sc14[i] * X) > 1e-9], [], "S: the %d sell caps x4.5 (crafting value)" % len(both))
    K.notes.append("S: sell caps only in 0.1.14: %s; only in 0.1.15: %s" % (sorted(set(sc14) - set(sc15)), sorted(set(sc15) - set(sc14))))
    # the Eternal seeds: the 2026-10-15 buy prices stay
    K.eq([(i, bo.q(i), bn.q(i)) for i in keep if bo.q(i) != bn.q(i)], [], "S: every Eternal seed bag buys exactly as on 0.1.14 (Wheat %d)" % bn.q("Plant_Seeds_Wheat_Eternal"))
    K.eq(bn.q("Plant_Seeds_Wheat_Eternal"), 880, "S: Wheat Seed Bag (Eternal) still buys for 880 (800 base)")
    # the scale alone lifts every sale to >= 2 (floor OFF), and with the floor ON nothing sells under it
    for fl in (0, 2):
        bn.Cfg.MINSELL = fl
        low = [(i, bn.q(i, 1, False)) for i in bn.ids if not eternal(i) and bn.q(i, 1, False) < 2]
        K.eq(low[:10], [], "S: floor %d: every product but the Eternal seeds sells 1 for >= 2 at demand 1.0" % fl)
    bn.Cfg.MINSELL = 2
    cheapest = sorted((bn.q(i, 1, False), i) for i in bn.ids)[:5]
    K.notes.append("S: the cheapest instant sales now: %s (0.1.14: %s)" % (cheapest, sorted((bo.q(i, 1, False), i) for i in bo.ids)[:5]))
    K.eq([(i, bn.q(i), bn.q(i, 1, False)) for i in bn.ids if bn.q(i) <= bn.q(i, 1, False)], [], "S: buy > sell for every product (1 unit)")
    # the demand step per unit is 0.1.14's for every scaled product (impactCoins x4.5)
    K.eq(float(bn.M.IMPACT), 45000.0, "S: impactCoins defaults to 45000 (10000 x4.5)")
    st = [(i, float(bo.M.step(bo.C.get(i))), float(bn.M.step(bn.C.get(i)))) for i in bn.ids if not eternal(i)]
    K.eq([x for x in st if abs(x[1] - x[2]) > 1e-6 * x[1]][:8], [], "S: the demand step per unit = 0.1.14's for all %d scaled products" % len(st))
    K.notes.append("S: Eternal seed steps 0.1.14 -> 0.1.15 (their price stays, the impact grew): %s" % ", ".join(
        "%s %.4f->%.4f" % (i.replace("Plant_Seeds_", ""), float(bo.M.step(bo.C.get(i))), float(bn.M.step(bn.C.get(i)))) for i in keep[:4]))
    # the samples (before the round trips below move any demand)
    rows = []
    for i in SAMPLES:
        if i in bn.ids:
            rows.append("%s %d/%d -> %d/%d" % (i, bo.q(i), bo.q(i, 1, False), bn.q(i), bn.q(i, 1, False)))
    # fixer bz0115fix (critic finding 2): the confirm default stays Skyy's 3,000 - a small buy (1 Iron Bar) still goes through on the
    # first click, 64 Iron Ore (and 1 Mithril Ore) now ask CONFIRM
    from jpype import JClass as _JC
    Cf = _JC(PKG + "BzConfirm", loader=bn.L)
    U = _JC("java.util.UUID").randomUUID()
    K.eq(int(bn.Cfg.CONFIRM), 3000, "F2: confirm.default stays 3000 (Skyy 2026-10-15 'default like 3,000')")
    bar1, ore64 = bn.q("Ingredient_Bar_Iron"), bn.q("Ore_Iron", 64)
    K.check(not bool(Cf.needs(U, bar1)), "F2: 1 Iron Bar (%d coins) buys on the first click" % bar1)
    K.check(bool(Cf.needs(U, ore64)), "F2: 64 Iron Ore (%d coins) asks CONFIRM" % ore64)
    if "Ore_Mithril" in bn.ids:
        K.notes.append("F2: 1 Mithril Ore buys for %d (0.1.14: %d) -> confirm %s" % (bn.q("Ore_Mithril"), bo.q("Ore_Mithril"),
                       "YES" if bool(Cf.needs(U, bn.q("Ore_Mithril"))) else "no"))
    # fixer bz0115fix (critic finding 3): the Eternal seeds' SELL side follows its crafting value (cap x4.5), the buy stays; buying 5
    # only nudges the price
    we = "Plant_Seeds_Wheat_Eternal"
    ws_old, ws_new = bo.q(we, 1, False), bn.q(we, 1, False)
    K.check(ws_new < bn.q(we) and abs(ws_new - ws_old * 4.5) <= 5, "F3: Wheat Eternal sells for %d (0.1.14: %d, x4.5), buys for %d"
            % (ws_new, ws_old, bn.q(we)))
    b0 = bn.q(we)
    bn.M.apply(we, 5, True)
    b5 = bn.q(we)
    bn.M.F.remove(we)
    K.check(b0 <= b5 <= b0 * 1.6, "F3: buying 5 Wheat Eternal moves its price only %d -> %d" % (b0, b5))
    K.notes.append("F3: Eternal sells 0.1.14 -> 0.1.15: %s" % ", ".join("%s %d->%d" % (i.replace("Plant_Seeds_", ""), bo.q(i, 1, False),
                   bn.q(i, 1, False)) for i in keep[:6]))
    # fixer 2 (critic: the factor is fixed at build time): the floor row's help says a floor change never rescales the prices
    import zipfile as _zf
    _hz = _zf.ZipFile(jar)
    _txt = b"Never rescales prices."
    _hit = [n for n in _hz.namelist() if _txt in _hz.read(n)]
    _hz.close()
    K.check(len(_hit) >= 1, "F4: the 'Minimum instant sell price' help tells admins a floor change never rescales the prices (%s)" % _hit[:2])
    # buy then sell straight back never pays (1 and 64 units; the demand is put back to 1.0 after each product)
    rt = []
    for i in bn.ids:
        for n in (1, 64):
            b1 = bn.q(i, n)
            bn.M.apply(i, n, True)
            s1 = bn.q(i, n, False)
            bn.M.apply(i, n, False)
            if s1 >= b1:
                rt.append((i, n, b1, s1))
            bn.M.F.remove(i)
    K.eq(rt[:8], [], "S: buy 1 / 64 then sell them straight back never pays, for all %d products" % len(bn.ids))
    # the jar's own recipe loop guard (the admin guard: every recipe whose inputs are all products) at these prices
    sp = float(bn.M.SPREAD)
    le = bn.C.loopingEdges(sp)
    K.eq(int(le.size()), 0, "S: Catalog.loopingEdges finds no paying recipe at the x4.5 prices")
    K.eq(int(bn.C.warnLoops(sp)), 0, "S: Catalog.warnLoops = 0")
    # the bridge (shared map: the 0.1.15 jar published last)
    bn.M.publishAll()
    from jpype import JClass
    br = JClass("java.lang.System").getProperties().get("skyy.bridge")
    K.eq([i for i in SAMPLES if i in bn.ids and (int(br.get("bazaar:buy:" + i)) != bn.q(i) or int(br.get("bazaar:sell:" + i)) != bn.q(i, 1, False))], [],
         "S: the bridge publishes the new quotes (bazaar:buy / bazaar:sell)")
    K.notes.append("S: samples buy 1 / sell 1 at demand 1.0, 0.1.14 -> 0.1.15: " + "; ".join(rows))
    K.save(samples=rows)


# ------------------------------------------------------------------------------------------------------------------- M15: mig15
def run_mig15(out, jar, scratch, _home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    fresh = Bz15(jar, os.path.join(scratch, "m15_fresh"))
    seed = dict((str(p.id), float(p.base)) for p in fresh.C.all())
    m115 = dict((str(i), (float(o), float(n), str(t))) for i, o, n, t in zip(fresh.C.M115_ID, fresh.C.M115_OLD, fresh.C.M115_NEW, fresh.C.M115_TXT))
    K.check(not [x for x in fresh.m14log + fresh.m114log + fresh.m115log if " KEPT " in x or " PRICE " in x],
            "M15 fresh: migrate14 / 114 / 115 log no PRICE / KEPT line on the 0.1.15 seed (%s)" % [x for x in fresh.m115log if "KEPT" in x][:3])
    K.check(str(fresh.m115).startswith("MIGRATE-0.1.15 x4.5 rewrote 0 kept 0 already %d impact default" % len(m115)), "M15 fresh: %s" % fresh.m115)
    K.check(not [i for i in seed if eternal(i) and i in m115], "M15: no Eternal seed bag is in the update table")
    for nl in ("\n", "\r\n"):
        tag = "crlf" if nl == "\r\n" else "lf"
        d = os.path.join(scratch, "m15_" + tag)
        Bz(OLD_JAR, d, True)
        pf, mf, prf = os.path.join(d, "products.properties"), os.path.join(d, "market.properties"), os.path.join(d, "pricing.properties")
        lines = open(pf, "rb").read().decode("utf8").replace("\r\n", "\n").split("\n")
        lines = [re.sub(r"^(Ore_Copper=[^,]*,)[^,]*(,.*)$", r"\g<1>7\g<2>", ln) for ln in lines]
        open(pf, "wb").write(nl.join(lines).encode("utf8"))
        mt = open(mf, "rb").read().decode("latin-1").replace("\r\n", "\n")
        K.check("impactCoins=10000.0" in mt, "M15 %s: 0.1.14 wrote impactCoins=10000.0" % tag)
        open(mf, "wb").write(mt.replace("\n", nl).encode("latin-1"))
        before, mbefore = rb(pf), rb(mf)
        b = Bz15(jar, d)
        after = rb(pf)
        K.check(str(b.m115).startswith("MIGRATE-0.1.15 x4.5 rewrote") and " kept 1 " in str(b.m115) and "impact moved" in str(b.m115), "M15 %s: %s" % (tag, b.m115))
        bl, al = before.split(b"\n"), after.split(b"\n")
        K.eq(len(bl), len(al), "M15 %s: same number of lines" % tag)
        bad, moved = [], 0
        for x, y in zip(bl, al):
            i, _v = price_of(x)
            if i is not None and bool(b.C.isProc(i)) and bool(b.C.isAuto(i)):
                if without_price(x) != without_price(y):
                    bad.append(i)        # a processed good follows its inputs (the reprice writes its new price) - nothing else moves
            elif i in m115 and i != "Ore_Copper":
                yi, yv = price_of(y)
                if without_price(x) != without_price(y) or abs(yv - m115[i][1]) > 1e-9:
                    bad.append(i)
                moved += 1
            elif x != y:
                bad.append(i or x[:30])
        K.eq(bad[:8], [], "M15 %s: %d lines moved x4.5 (price text only); every other byte stays (Eternal seeds, Ore_Copper 7)" % (tag, moved))
        K.check((b"\r\n" in after) == (nl == "\r\n") and after.count(b"\r\n") == before.count(b"\r\n"), "M15 %s: the file keeps its line endings" % tag)
        kc = [x for x in b.m115log if "KEPT Ore_Copper " in x]
        K.check(len(kc) == 1 and re.search(r"KEPT Ore_Copper 7(\.0)? \(your price; the 0\.1\.14 default was 5, the 0\.1\.15 default is 22\.5\)", kc[0]),
                "M15 %s: the admin's 7 for Copper Ore is KEPT + logged (%s)" % (tag, kc))
        K.check(any("PRICE Ore_Iron 16 -> 72 (undo: /bazaaradmin price Ore_Iron 16)" in x for x in b.m115log), "M15 %s: a moved price logs its undo" % tag)
        K.check(any("IMPACT impactCoins 10000.0 -> 45000.0 (undo: set impactCoins=10000.0 in market.properties, then /bazaaradmin reload)" in x
                    for x in b.m115log), "M15 %s: impactCoins 10000 -> 45000 logged with its undo" % tag)
        K.eq(float(b.C.get("Ore_Copper").base), 7.0, "M15 %s: the kept price is what the catalogue uses" % tag)
        K.eq(float(b.C.get("Plant_Seeds_Wheat_Eternal").base), 800.0, "M15 %s: Wheat Eternal stays 800" % tag)
        K.eq(float(b.M.IMPACT), 45000.0, "M15 %s: the market runs at impactCoins 45000" % tag)
        hd = os.path.join(d, "config-history")
        baks = sorted(os.listdir(hd)) if os.path.isdir(hd) else []
        pb_ = [f for f in baks if "~products.properties." in f]
        mb_ = [f for f in baks if "~market.properties." in f]
        K.check(len(pb_) == 1 and rb(os.path.join(hd, pb_[0])) == before, "M15 %s: the products config-history copy = the old bytes (%s)" % (tag, baks))
        K.check(len(mb_) == 1 and rb(os.path.join(hd, mb_[0])) == mbefore, "M15 %s: the market config-history copy = the old bytes" % tag)
        # market.properties as migrate115 left it (before the market's own flush): only the impactCoins value moved - checked on a copy run
        pr = rb(prf)
        K.check(pr.count(b"migrated.0.1.15=") == 1, "M15 %s: the marker is written" % tag)
        b.C.writeModes(b.C.MIGRATED)
        K.check(b"migrated.0.1.15=" in rb(prf) and b"migrated.0.1.14=" in rb(prf), "M15 %s: writeModes keeps both markers" % tag)
        snap = (rb(pf), rb(prf))
        b2 = Bz15(jar, d)
        K.check(b2.m115 is None and (rb(pf), rb(prf)) == snap, "M15 %s: a second start changes nothing (%s)" % (tag, b2.m115))
        K.eq(float(b2.M.IMPACT), 45000.0, "M15 %s: impactCoins reads back 45000" % tag)
    # market.properties byte rule on its own (migrate115 alone, before the market flushes): only the value text of the impactCoins line
    d = os.path.join(scratch, "m15_bytes")
    Bz(OLD_JAR, d, True)
    mf = os.path.join(d, "market.properties")
    mt = rb(mf).replace(b"\r\n", b"\n").replace(b"impactCoins=10000.0", b"impactCoins = 10000")
    open(mf, "wb").write(mt.replace(b"\n", b"\r\n"))
    mbefore = rb(mf)
    from jpype import JClass
    c = Bz15.__new__(Bz15)
    c.L = T14.loader_for(jar)
    C_ = JClass(PKG + "Catalog", loader=c.L)
    M_ = JClass(PKG + "Market", loader=c.L)
    JClass(PKG + "BzUtil", loader=c.L).LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyBazaar")
    dp = JClass("java.nio.file.Paths").get(d)
    C_.FILE, C_.PFILE, M_.FILE = dp.resolve("products.properties"), dp.resolve("pricing.properties"), dp.resolve("market.properties")
    h = str(C_.migrate115())
    K.eq(rb(mf), mbefore.replace(b"impactCoins = 10000\r\n", b"impactCoins = 45000.0\r\n"), "M15 bytes: 'impactCoins = 10000' (CRLF) -> "
         "'impactCoins = 45000.0', every other byte of market.properties stays (%s)" % h)
    # an admin's impactCoins is kept; a lost marker re-runs as a no-op
    d = os.path.join(scratch, "m15_admin")
    Bz(OLD_JAR, d, True)
    mf, prf = os.path.join(d, "market.properties"), os.path.join(d, "pricing.properties")
    mt = rb(mf)
    open(mf, "wb").write(mt.replace(b"impactCoins=10000.0", b"impactCoins=20000"))
    b = Bz15(jar, d)
    K.check("impact kept" in str(b.m115) and any("KEPT impactCoins 20000 (your value" in x for x in b.m115log) and float(b.M.IMPACT) == 20000.0,
            "M15 admin: impactCoins 20000 is KEPT + logged (%s)" % b.m115)
    txt = rb(prf).decode("latin-1")
    open(prf, "wb").write("".join(ln for ln in txt.splitlines(True) if "0.1.15" not in ln).encode("latin-1"))
    pbefore = rb(os.path.join(d, "products.properties"))
    b = Bz15(jar, d)
    K.check(str(b.m115).startswith("MIGRATE-0.1.15 x4.5 rewrote 0 kept 0 already ") and "impact kept" in str(b.m115)
            and rb(os.path.join(d, "products.properties")) == pbefore, "M15 rerun: a lost marker re-runs as a no-op (%s)" % b.m115)
    # 0.1.13 -> 0.1.15: migrate114 then migrate115 end on the 0.1.15 defaults
    if os.path.isfile(JAR13):
        d = os.path.join(scratch, "m15_from13")
        Bz(JAR13, d, False)
        b = Bz15(jar, d)
        K.check(str(b.m114).startswith("MIGRATE-0.1.14 rewrote") and str(b.m115).startswith("MIGRATE-0.1.15 x4.5 rewrote"), "M15 13: both updates ran (%s | %s)" % (b.m114, b.m115))
        off = [(i, float(b.C.get(i).base), seed[i]) for i in b.ids if i in seed and abs(float(b.C.get(i).base) - seed[i]) > (0.01 * 4.5 + 1e-9 if bool(b.C.isProc(i)) else 1e-9)]
        K.eq(off[:8], [], "M15 13: every product of a 0.1.13 file ends on its 0.1.15 default (%d products)" % len(b.ids))
        K.check(not [x for x in b.m114log + b.m115log if " KEPT " in x], "M15 13: nothing is kept on an untouched 0.1.13 file")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- O: order
def run_order(out, jar, scratch, _home):
    import tier_tags as TT
    import skyyench as EN
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    bo = Bz(OLD_JAR, os.path.join(scratch, "ord14"), True)
    bn = Bz15(jar, os.path.join(scratch, "ord15"))
    to, tn = tabs(bo), tabs(bn)
    K.eq(list(tn), list(to), "O: the same tabs in the same order (%s)" % ", ".join(tn))
    name = dict((str(p.id), str(p.name)) for p in bn.C.all())
    sap = [i for i in to["Farming"] if i.startswith("Plant_Sapling_")]
    K.check(len(sap) == 33, "O: 0.1.14 listed %d saplings in Farming" % len(sap))
    # Farming, worked out independently from the tier table
    farm = [i for i in to["Farming"] if i not in sap]
    groups = []
    for c, t in TT.CROPS:
        crop = "Plant_Crop_%s_Item" % c
        mem = [m for m in (crop, EN.PREFIX + c, "Plant_Seeds_" + c, "Plant_Seeds_%s_Eternal" % c) if m in farm]
        K.check(mem and mem[0] == crop, "O: %s leads its group %s" % (crop, mem))
        groups.append(((TT.tier(crop), name[crop].lower(), crop), mem))
    groups.sort()
    done = set(m for _k, g in groups for m in g)
    want = [m for _k, g in groups for m in g] + sorted((i for i in farm if i not in done), key=lambda i: (TT.tier(i) or 0, name[i].lower(), i))
    K.eq(tn["Farming"], want, "O: Farming = %d crop groups (crop, Enchanted, seeds, Eternal) by tier then name, then %d others by tier / name"
         % (len(groups), len(farm) - len(done)))
    tiers = [TT.tier(g[0]) for _k, g in groups]
    K.check(tiers == sorted(tiers), "O: the groups climb by tier %s" % tiers)
    K.check(not [i for i in tn["Farming"] if "Sapling_" in i], "O: no sapling left in Farming")
    K.notes.append("O: Farming first 24: " + ", ".join("%s" % name[i] for i in tn["Farming"][:24]))
    fo = tn["Foraging"]
    K.eq(sorted(fo), sorted(to["Foraging"] + sap), "O: Foraging = 0.1.14's Foraging + the %d saplings" % len(sap))
    K.eq([i for i in fo if i not in sap], to["Foraging"], "O: Foraging keeps 0.1.14's order for its own products")
    logs = [i for i in to["Foraging"] if i.startswith("Wood_") and i.endswith("_Trunk")]
    bad = []
    for s_ in sap:
        k = fo.index(s_)
        j = k - 1
        while j >= 0 and fo[j].startswith("Plant_Sapling_"):
            j -= 1
        lg = "Wood_%s_Trunk" % s_[len("Plant_Sapling_"):]
        if fo[j] != (lg if lg in logs else logs[-1]):
            bad.append((s_, fo[j]))
    K.eq(bad, [], "O: every sapling sits right after its tree's log (no log listed: after the last log)")
    for t in tn:
        if t not in ("Farming", "Foraging"):
            K.eq(tn[t], to[t], "O: %s keeps its 0.1.14 order (%d)" % (t, len(tn[t])))
    allo = set(i for v in to.values() for i in v)
    alln = set(i for v in tn.values() for i in v)
    K.eq((sorted(allo - alln), sorted(alln - allo)), ([], []), "O: every one of the %d products is still in a tab (the search walks the tabs)" % len(alln))
    K.eq(sorted(bn.ids), sorted(bo.ids), "O: the same %d products" % len(bn.ids))
    # the seeded products.properties = 0.1.14's with only the prices x4.5 (the Eternal seeds the same)
    a, b_ = rb(os.path.join(scratch, "ord14", "products.properties")), rb(os.path.join(scratch, "ord15", "products.properties"))
    al, bl = a.split(b"\n"), b_.split(b"\n")
    diff = []
    for x, y in zip(al, bl):
        i, xv = price_of(x)
        _j, yv = price_of(y)
        if i is None:
            if x != y:
                diff.append(x[:40])
            continue
        tol = 0.01 * 4.5 + 1e-9 if bool(bn.C.isProc(i)) else 1e-9
        if without_price(x) != without_price(y) or abs(yv - (xv if eternal(i) else xv * 4.5)) > tol:
            diff.append((i, xv, yv))
    K.check(len(al) == len(bl) and not diff, "O: the seeded products.properties = 0.1.14's, only the prices x4.5 (Eternal seeds the same) %s" % diff[:5])
    pa, pb = [re.sub(rb"(migrated\.[0-9.]+)=[0-9TZ:.-]+", rb"\1=T", x or b"") for x in (rb(os.path.join(scratch, "ord14", "pricing.properties")),
                                                                                     rb(os.path.join(scratch, "ord15", "pricing.properties")))]
    pb = b"".join(ln for ln in pb.splitlines(True) if b"0.1.15" not in ln)
    K.check(pa == pb, "O: the seeded pricing.properties = 0.1.14's + the 0.1.15 marker")
    # an admin's own line (not in the seed) still lists, after the table's products
    pf = os.path.join(scratch, "ord15", "products.properties")
    open(pf, "ab").write(b"Rock_Stone_Custom=Farming,5,Custom Thing\n")
    bn.C.load()
    fa = [str(p.id) for p in bn.C.inCat("Farming")]
    K.check(fa[-1] == "Rock_Stone_Custom" and fa[:-1] == want, "O: an admin-added Farming line lists last (%s)" % fa[-3:])
    sp = bn.C.get("Plant_Sapling_Oak")
    K.eq([str(x) for x in bn.C.tabsOf(sp)], ["Foraging"], "O: tabsOf(Oak Sapling) = Foraging only")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- D: live
def run_live(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    files = ("products.properties", "pricing.properties", "market.properties", "config.properties")
    h14 = home + "-014"
    shutil.copytree(home, h14)
    bo = Bz(OLD_JAR, h14, True)          # the 0.1.14 quotes of the same data (a second scratch copy)
    before = dict((f, rb(os.path.join(home, f))) for f in files)
    b = Bz15(jar, home)
    K.check(b.n > 400, "D: %d live products load" % b.n)
    K.check(str(b.m115).startswith("MIGRATE-0.1.15 x4.5 rewrote"), "D: the one-time update ran: %s" % b.m115)
    K.notes.append("D: %s" % b.m115)
    K.notes.append("D: kept (live prices that are not the 0.1.14 default): %s" % [x for x in b.m115log if " KEPT " in x][:12])
    rows = ["%s %d/%d -> %d/%d" % (i, bo.q(i), bo.q(i, 1, False), b.q(i), b.q(i, 1, False)) for i in SAMPLES if i in b.ids]
    K.notes.append("D: live samples buy 1 / sell 1 (at the live demand), 0.1.14 -> 0.1.15: " + "; ".join(rows))
    K.eq([i for i in b.ids if eternal(i) and b.q(i) != bo.q(i)], [], "D: every Eternal seed bag quotes as on 0.1.14")
    K.check(b.q("Rubble_Stone", 1, False) >= 2 and b.q("Plant_Crop_Wheat_Item", 1, False) >= 2, "D: Stone Rubble sells for %d, Wheat for %d"
            % (b.q("Rubble_Stone", 1, False), b.q("Plant_Crop_Wheat_Item", 1, False)))
    t = tabs(b)
    nm = dict((str(p.id), str(p.name)) for p in b.C.all())
    K.notes.append("D: live Farming (%d) first 20: %s" % (len(t["Farming"]), ", ".join(nm[i] for i in t["Farming"][:20])))
    K.check(not [i for i in t["Farming"] if i.startswith("Plant_Sapling_")], "D: no sapling in the live Farming tab")
    K.check(len([i for i in t["Foraging"] if i.startswith("Plant_Sapling_")]) == 33, "D: 33 saplings in the live Foraging tab")
    K.check(t["Farming"][0] == "Plant_Crop_Lettuce_Item" and "Plant_Crop_Wheat_Item" in t["Farming"][:8], "D: the crops lead the live Farming tab")
    K.check(before["config.properties"] == rb(os.path.join(home, "config.properties")), "D: config.properties untouched")
    snap = dict((f, rb(os.path.join(home, f))) for f in ("products.properties", "pricing.properties", "config.properties"))
    b2 = Bz15(jar, home)
    K.check(b2.m115 is None, "D2: the update does not run twice")
    K.eq([f for f in snap if rb(os.path.join(home, f)) != snap[f]], [], "D2: the second start changes no products / pricing / config file")
    K.save(samples=rows)


# ------------------------------------------------------------------------------------------------------------------- SL: sell <tab> / all
def run_sell(out, jar, scratch, _home):
    """0.1.15 E: SELL <open tab> sells only that tab's products, SELL ALL TABS every product; both two clicks (gold Confirm sell),
    the other button / any click disarms, the 0.3 s rule, the timeout, profile:busy; walled (market:veto) stacks are never sold
    (equipped slots: Inv.conts = storage + hotbar + backpack, unchanged - the stand-in's equipped containers take no test items);
    coins = the sum of each product's own quote (price impact per product); trades.log one SELL line per product"""
    import jpype
    from jpype import JClass, JImplements, JOverride, JLong, JBoolean, JShort
    import hub_tab_harness as H
    K = HK.Child(out)
    W = H.boot(scratch, jar, "sl")
    E = W.E
    J = lambda n: JClass(PKG + n)
    # the 0.1.14 exec phase's Item asset store stand-in (every product id answers Item.UNKNOWN, so stacks really move)
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    CtF, CtM, CtC = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyBzFakeStore15s", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fake.addConstructor(CtC.make("public SkyyBzFakeStore15s() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
    store = us.allocateInstance(fake.toClass(AS.class_))
    fm = AS.class_.getDeclaredField("assetMap")
    fm.setAccessible(True)
    DAMN = "com.hypixel.hytale.assetstore.map.DefaultAssetMap"
    ITMN = "com.hypixel.hytale.server.core.asset.type.item.config.Item"
    kmap = jp.makeClass("com.hypixel.hytale.assetstore.map.SkyyBzKnownMap15s", jp.get(DAMN))
    kmap.addField(CtF.make("public static final java.util.HashSet KNOWN = new java.util.HashSet();", kmap))
    kmap.addConstructor(CtC.make("public SkyyBzKnownMap15s() { super(); }", kmap))
    kmap.addMethod(CtM.make("public com.hypixel.hytale.assetstore.JsonAsset getAsset(Object key) { if (key != null && KNOWN.contains(key)) return "
                            "%s.UNKNOWN; return super.getAsset(key); }" % ITMN, kmap))
    KMap = JClass(kmap.toClass(JClass(DAMN).class_))
    fm.set(store, KMap())
    fi_ = JClass(ITMN).class_.getDeclaredField("ASSET_STORE")
    fi_.setAccessible(True)
    fi_.set(None, store)
    home = os.path.join(scratch, "home_sl")
    shutil.rmtree(home, ignore_errors=True)       # a fresh folder every run (trades.log is counted below)
    os.makedirs(home, exist_ok=True)
    J("BzUtil").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyBazaar")
    d = E.Paths.get(home)
    C, M, Cfg, Cf, T = J("Catalog"), J("Market"), J("BzCfg"), J("BzConfirm"), J("Trader")
    C.FILE = d.resolve("products.properties")
    C.PFILE = d.resolve("pricing.properties")
    M.FILE = d.resolve("market.properties")
    M.LOGFILE = d.resolve("trades.log")
    Cfg.load(d)
    Cf.load(d)
    for m in ("migrate", "migrate14", "migrate19", "migrate110", "migrate114", "migrate115"):
        getattr(C, m)()
    C.load()
    M.load()
    C.reprice()
    M.publishAll()
    br = J("BzUtil").bridge()
    purse = {}

    @JImplements("java.util.function.Function")
    class CGet:
        @JOverride
        def apply(self, o):
            return JLong(purse.get(str(o), 0))

    @JImplements("java.util.function.Function")
    class CTake:
        @JOverride
        def apply(self, o):
            u_, n_ = str(o[0]), int(o[1])
            if purse.get(u_, 0) < n_:
                return JBoolean(False)
            purse[u_] = purse.get(u_, 0) - n_
            return JBoolean(True)

    @JImplements("java.util.function.Function")
    class CAdd:
        @JOverride
        def apply(self, o):
            u_, n_ = str(o[0]), int(o[1])
            purse[u_] = purse.get(u_, 0) + n_
            return JLong(purse[u_])
    br.put("coins:fn:get", CGet())
    br.put("coins:fn:take", CTake())
    br.put("coins:fn:add", CAdd())
    # the market wall stand-in: a stack carrying the metadata key SkyyStamp is walled (like SkyyGear's Mythic / stamped gear)

    @JImplements("java.util.function.Function")
    class Wall:
        @JOverride
        def apply(self, s):
            md = s.getMetadata()
            return "stamped items stay off the market" if (md is not None and md.containsKey("SkyyStamp")) else None
    vmap = JClass("java.util.concurrent.ConcurrentHashMap")()
    vmap.put("SkyyHarness", Wall())
    br.put("market:veto", vmap)
    ids = [str(p.id) for p in C.all()]
    for i in ids:
        KMap.KNOWN.add(i)
    cats = [str(c) for c in C.categories()]
    tabs = dict((c, [str(p.id) for p in C.inCat(c)]) for c in cats)
    tabs_of = {}
    for c in cats:
        for i in tabs[c]:
            tabs_of.setdefault(i, set()).add(c)
    K.check(set(["Mining", "Foraging", "Farming", "Fishing", "Combat", "Smithing"]) <= set(cats), "SL: the six bag tabs are there: %s" % cats)
    one = dict((c, [i for i in tabs[c] if tabs_of[i] == {c} and bool(C.usable(i)) and not i.endswith("_Eternal")]) for c in cats)
    K.check(all(len(one[c]) >= 2 for c in cats), "SL: every tab has 2+ products listed in that tab only")
    P = W.P
    u = P.pr.getUuid()
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    BD, BS = JClass("org.bson.BsonDocument"), JClass("org.bson.BsonString")

    def put(slot, iid, n, stamp=False):
        st_ = IS(iid, n)
        if stamp:
            st_ = st_.withMetadata(BD("SkyyStamp", BS("harness")))
        ic = P.slots[slot].getInventory()
        if slot in ("utility", "tools", "armor"):        # equipped slots filter by item kind: put the stack straight into slot 0
            ic.setItemStackForSlot(JShort(0), st_)
        else:
            ic.addItemStack(st_)

    def clear():
        for c_ in P.slots.values():
            ic = c_.getInventory()
            for i in range(int(ic.getCapacity())):
                ic.setItemStackForSlot(JShort(i), None)

    cnt = lambda i: int(E.count(P, i))
    sq = lambda i, n: int(M.quote(i, n, False))
    pu = lambda: purse.get(str(u), 0)
    purse[str(u)] = 1000

    # ---- 1. Trader level, every tab: sellInventory(tab) sells exactly that tab's products (2 of every tab in the inventory)
    bad = []
    for c in cats:
        clear()
        for k in cats:
            put("storage", one[k][0], 3)
            put("hotbar", one[k][1], 2)
        want = sq(one[c][0], 3) + sq(one[c][1], 2)
        pv = [int(x) for x in T.preview(P.pl, u, c)]
        p0 = pu()
        r = T.sellInventory(P.pl, u, "Tester", c)
        left = dict((k, (cnt(one[k][0]), cnt(one[k][1]))) for k in cats)
        okc = (bool(r.ok) and int(r.qty) == 5 and int(r.coins) == want == pu() - p0 and pv == [5, want, 0]
               and left[c] == (0, 0) and all(left[k] == (3, 2) for k in cats if k != c)
               and str(r.msg).startswith("sold 5 %s items of 2 kinds for %d coins" % (c, want)))
        if not okc:
            bad.append((c, bool(r.ok), int(r.qty), int(r.coins), want, pv, left, str(r.msg)))
    K.eq(bad, [], "SL: Trader.sellInventory(<tab>) sells ONLY that tab's products, for each of the %d tabs (preview = the sale)" % len(cats))
    clear()
    for k in cats:
        put("storage", one[k][0], 3)
    want = sum(sq(one[k][0], 3) for k in cats)
    p0 = pu()
    r = T.sellInventory(P.pl, u, "Tester", None)
    K.check(bool(r.ok) and int(r.qty) == 3 * len(cats) and int(r.coins) == want == pu() - p0 and all(cnt(one[k][0]) == 0 for k in cats)
            and str(r.msg).startswith("sold %d items of %d kinds" % (3 * len(cats), len(cats))),
            "SL: Trader.sellInventory(null) = every tab (%s)" % r.msg)
    r = T.sellInventory(P.pl, u, "Tester", "Farming")
    K.check(not bool(r.ok) and str(r.msg) == "nothing to sell - no Farming items in your inventory or the Void", "SL: an empty tab says so (%s)" % r.msg)

    # ---- 2. the page: SELL FARMING / SELL ALL TABS, two clicks, protections
    WH, PO, CU, OAK = "Plant_Crop_Wheat_Item", "Plant_Crop_Potato_Item", "Ore_Copper", "Wood_Oak_Trunk"
    K.check(WH in tabs["Farming"] and PO in tabs["Farming"] and CU in tabs["Mining"] and OAK in tabs["Foraging"]
            and not ({CU, OAK} & set(tabs["Farming"])) and WH not in tabs["Mining"] + tabs["Foraging"],
            "SL: wheat + potato in Farming only, copper in Mining, oak in Foraging")
    clear()
    put("storage", WH, 20)
    put("hotbar", WH, 5)
    put("storage", PO, 10)
    put("storage", CU, 15)
    put("hotbar", OAK, 8)
    put("storage", WH, 4, stamp=True)     # a walled (stamped) stack: never counted, never taken
    K.eq((cnt(WH), cnt(PO), cnt(CU), cnt(OAK)), (29, 10, 15, 8), "SL: the test inventory (wheat 20 + 5 hotbar + 4 stamped)")
    page = J("BzPage")(P.pr, None)
    page.cat = "Farming"
    P.pm.openCustomPage(P.ref, P.st, page)
    E.pump(P)
    first = E.strs_of(P, 0)
    unanswered = []

    def click(a, soon=False):
        if not soon:
            page.cfShown = JLong(0)
        dd = {"a": a, "@BzFind": "", "@BzCf": ""}
        n0 = len(E.sent(P))
        P.pm.handleLegacyCustomPageEvent(P.ref, P.st, E.CPE(E.CPT.Data, json.dumps(dd)))
        E.pump(P)
        if len(E.sent(P)) <= n0:
            unanswered.append((a, str(page.info)))
        return E.strs_of(P, n0)
    GOLD = "#E8A93B"
    K.check("Sell Farming" in first and "Sell all tabs" in first and "#SkyyBzSellInv" in first and "#SkyyBzSellAllTabs" in first
            and "Sell inventory" not in first, "SL: the tab row shows SELL FARMING, the search row SELL ALL TABS (no Sell inventory)")
    wf = sq(WH, 25) + sq(PO, 10)
    p0 = pu()
    t1 = click("sellinv")
    K.check((cnt(WH), cnt(PO), pu()) == (29, 10, p0) and str(page.confirmWhat) == "sellinv" and str(page.confirmCat) == "Farming"
            and str(page.info) == "sell 35 Farming items for about %d coins - click Confirm sell within 10 seconds" % wf,
            "SL: 1st SELL FARMING click only prices it: %s" % page.info)
    K.check("Confirm sell" in t1 and GOLD in t1 and "Sell all tabs" in t1, "SL: ... SELL FARMING turns into the gold Confirm sell, SELL ALL TABS stays")
    click("sellinv", soon=True)
    K.check((cnt(WH), cnt(PO), pu()) == (29, 10, p0), "SL: a double-click (< 0.3 s after Confirm sell appeared) sells nothing")
    f0 = float(M.factor(WH))
    t2 = click("sellinv")
    K.check(pu() - p0 == wf and cnt(PO) == 0 and cnt(WH) == 4 and (cnt(CU), cnt(OAK)) == (15, 8)
            and str(page.info).startswith("sold 35 Farming items of 2 kinds for %d coins" % wf),
            "SL: Confirm sell sold the 35 Farming items for exactly %d (the sum of each product's own quote); copper + oak untouched: %s" % (wf, page.info))
    K.check(float(M.factor(WH)) < f0, "SL: the sale moved wheat's demand down (%.4f -> %.4f)" % (f0, float(M.factor(WH))))
    st_ = P.slots["storage"].getInventory()
    stamped = [st_.getItemStack(JShort(i)) for i in range(int(st_.getCapacity()))]
    stamped = [s for s in stamped if s is not None and not s.isEmpty() and str(s.getItemId()) == WH]
    K.check(len(stamped) == 1 and int(stamped[0].getQuantity()) == 4 and stamped[0].getMetadata() is not None,
            "SL: the stamped (market:veto walled) wheat stack (4, metadata kept) is untouched")
    K.check("Confirm sell" not in t2 and "Sell Farming" in t2, "SL: after the sale the button reads SELL FARMING again")
    M.flushLog()
    lg = [ln for ln in open(os.path.join(home, "trades.log"), encoding="latin-1").read().splitlines() if ln.split(" ")[1:2] == ["SELL"]]
    K.check(len([ln for ln in lg if (" %s 25 " % WH) in ln]) == 1 and len([ln for ln in lg if (" %s 10 " % PO) in ln]) == 1,
            "SL: trades.log has one SELL line per product (wheat 25, potato 10)")
    # the other sell button disarms; SELL ALL TABS = every tab
    click("sellinv")
    K.check(str(page.info) == "nothing to sell - no Farming items in your inventory or the Void" and page.confirmUntil == 0,
            "SL: SELL FARMING with only protected wheat left: nothing to sell, nothing armed (%s)" % page.info)
    ab = sq(CU, 15) + sq(OAK, 8)
    click("tab:%d" % [str(x) for x in page.tabs].index("Mining"))
    t3 = click("sellinv")
    K.check("Sell Mining" in t3 or "Confirm sell" in t3, "SL: the Mining tab's button is SELL MINING")
    t4 = click("sellalltabs")
    K.check((cnt(CU), cnt(OAK)) == (15, 8) and str(page.confirmWhat) == "sellalltabs"
            and str(page.info) == "sell 23 bazaar items for about %d coins - click Confirm sell within 10 seconds" % ab and "Sell Mining" in t4,
            "SL: SELL ALL TABS right after an armed SELL MINING disarms it and only prices every tab: %s" % page.info)
    click("next")
    p0 = pu()
    click("sellalltabs")
    K.check((cnt(CU), cnt(OAK)) == (15, 8) and pu() == p0 and str(page.info).startswith("sell 23"),
            "SL: another click (Next) disarmed it - the next SELL ALL TABS click asks again")
    # the timeout
    page.confirmUntil = JLong(int(JClass("java.lang.System").currentTimeMillis()) - 1)
    click("sellalltabs")
    K.check((cnt(CU), cnt(OAK)) == (15, 8) and pu() == p0 and str(page.info).startswith("sell 23"), "SL: a click after the 10 s asks again (no sale)")
    t5 = click("sellalltabs")
    K.check(pu() - p0 == ab and (cnt(CU), cnt(OAK)) == (0, 0) and cnt(WH) == 4 and str(page.info).startswith("sold 23 items of 2 kinds for %d coins" % ab),
            "SL: Confirm sell on SELL ALL TABS sold copper + oak (Mining + Foraging) for exactly %d; the protected wheat stays: %s" % (ab, page.info))
    click("sellalltabs")
    K.check(str(page.info) == "nothing to sell - no bazaar items in your inventory or the Void", "SL: SELL ALL TABS with nothing sellable says so")
    # profile busy: neither button prices or sells
    put("storage", CU, 5)
    br.put("profile:busy:" + str(u), JBoolean(True))
    click("sellalltabs")
    K.check(cnt(CU) == 5 and "still loading" in str(page.info) and page.confirmUntil == 0, "SL: profile:busy -> SELL ALL TABS refuses (%s)" % page.info)
    br.remove("profile:busy:" + str(u))
    K.eq(unanswered, [], "SL: every click was answered with a packet")
    K.check(not [x for x in E.sent(P) if "Error" in str(x.getClass().getSimpleName())], "SL: no error packet")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyBazaar", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec14", run_exec14), ("mig14", run_mig14), ("scale", run_scale), ("mig15", run_mig15), ("order", run_order),
                   ("sell", run_sell), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyBazaar"))
