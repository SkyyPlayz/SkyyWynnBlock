"""Harness for SkyyMerchants 0.1.9 (augments round A3 = aug3: T1 augments at the Traveling Merchant - a 4th shop tab, rotating offers, prices
from the Bazaar inputs; tools/merchants_0_1_9_patch.py). Build first:
    python tools/merchants_0_1_9_patch.py && python SkyyMerchants/build_skyymerchants_0.1.9.py
    python SkyyMerchants/test_skyymerchants_0.1.9.py [--dir <folder inside tools/dev/scratch/>] [--keep] [--expect-dump]

Phases (fresh child JVMs, -Xverify:all, tools/harness_kit.py):
  S   static   the patch re-runs to identical bytes; no new class / system / command; the generated data = tools/tier_tags.py's 18 T1 kinds in
               kind order (no Poison), their prices = the SET pins' SkyyGear recipes x SkyyBazaar base prices x 3 on the P7 rounding; kit art 59 files
  A   verify   every class loads + initialises
  C   compare  0.1.8 -> 0.1.9 (EXPECT below)
  X   exec     EXECUTES: the 3 new rows (defaults, a real scratch file, clamps); augPrice for all 18; MerchShop.restock on 300 visits (4 distinct
               T1 augments a visit in kind order, price + stock, every kind seen, never T2+), merchant.augOffers 0 / 30, augStock, price.augX live,
               unknown ids / walled ids skipped; offers(site, 3) + adjust; MerchPage.augRbg / rbg for all 120 augment ids (spec 2.3 rarities)
               and the 0.1.8 gear / egg squares unchanged; MerchPage.build on a real UICommandBuilder: tab 3 rows (names, Common squares, Buy
               bindings + 5 base bindings: the 4 tabs + Close), the empty text, a tab click to 3; MerchShop.buy of an augment END TO END on a
               real SimpleItemContainer with stand-in coins (paid exactly the price, the item arrives, stock 3 -> 2, a BUY line in sales.log),
               too poor = nothing moves;
               aug3fix: a 0.1.8 visit (no "3:" entries) gets its augments on the first Augments look, once (MerchShop.augTop)
  D   live     a scratch COPY of the live NewBetaTest Skyy_SkyyMerchants started TWICE (0.1.8's live phase): no file changes, nothing migrates
  AA  engine-access audit
NOT COVERED (UNVERIFIED in game): the 4-tab row look in the client; SkyyGear's augment ids loaded on the live server (itemOk); the real
inventory give path of the engine (the harness uses the engine's own SimpleItemContainer).
Exit code 1 on any failure.
"""
import os, sys, re, ast, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import tier_tags as TT

VERSION = "0.1.9"
PKG = "com.skyy.merchants."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMerchants-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMerchants-0.1.8.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "aug3", "me")))
GEN = os.path.join(HERE, "build_skyymerchants_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyymerchants_0.1.8.py")
PATCH = os.path.join(ROOT, "tools", "merchants_0_1_9_patch.py")
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyMerchants")
EXPECT = {"CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],
          "MerchCore": ["~m listText"],
          "MerchCfg": ["+f AUG_OFFERS", "+f AUG_STOCK", "+f AUG_X", "~<clinit>", "~m applyAll", "~m applyScalars", "~m seed"],
          "MerchPage": ["+m augRbg", "~m build", "~m handleDataEvent", "~m rbg"],
          "MerchShop": ["+f AUG_IDS", "+f AUG_IN", "+f AUG_PICKS", "+f AUG_TOPUPS", "+m augPrice", "+m augTop", "+m augs", "~<clinit>", "~m offers", "~m restock"],
          "SkyyMerchantsPlugin": ["~m setup"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = []
STAT = [k for k in TT.AUG_KINDS if TT.AUG_TIERS[k] == 5 and k != "Poison"]
ELEM = ["Earth", "Thunder", "Water", "Fire", "Air"]
T1 = ["Skyy_Aug_%s_1" % k for k in STAT + ELEM]

_run0 = HK.run
HK.run = lambda *a, **k: None          # 0.1.8's harness for its live phase
_s = importlib.util.spec_from_file_location("test_skyymerchants_0_1_8", os.path.join(HERE, "test_skyymerchants_0.1.8.py"))
T08 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(T08)
HK.run = _run0


def gen_data():
    g = open(GEN, encoding="utf8").read()
    vals = {}
    for k in ("AUG_T1", "AUG_IN", "AUG_NAMES"):
        m = re.search(r"\n%s = (.*)\n" % k, g)
        vals[k] = ast.literal_eval(m.group(1))
    return g, vals


def p7round(x):
    st = 10 if x < 1000 else (100 if x < 10000 else (500 if x < 100000 else 5000))
    return int(st * int(x / st + 0.5))


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g, v = gen_data()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check('VERSION = "0.1.9"' in g and g.count('VERSION = "0.1.9"') == 1, "S VERSION")
    K.eq([g.count(w) - o.count(w) for w in ("registerSystem(", "registerCommand(", "= cls(")], [0, 0, 0], "S no new class / system / command")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.eq(v["AUG_T1"], T1, "S the 18 T1 augments = tools/tier_tags.py kinds in kind order (13 stat + 5 elements, no Poison)")
    K.check(all(i in TT.AUG_IDS for i in v["AUG_T1"]), "S every id is one of SkyyGear's AUG_IDS")
    # the prices from the SET pins' own tables (independent re-read)
    S_ = open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf8").read()
    i0 = S_.index("\nSET = [")
    pin = dict(re.findall(r'\("(Skyy\w+)", "([0-9.]+)"\)', S_[i0:S_.index("\n]", i0)]))
    gear = open(os.path.join(ROOT, "SkyyGear", "build_skyygear_%s.py" % pin["SkyyGear"]), encoding="utf8").read()
    bz = open(os.path.join(ROOT, "SkyyBazaar", "build_skyybazaar_%s.py" % pin["SkyyBazaar"]), encoding="utf8").read()
    price = lambda it: float(re.search(r'\("%s",\s+(\d+(?:\.\d+)?),' % re.escape(it), bz).group(1))
    gems = dict(re.findall(r'\("(\w+)", "[wsmat]", "\w+", [0-9.]+, "\w+", [0-9.]+, "(Rock_Gem_\w+)"\)', gear))
    elems = dict(re.findall(r'\("(Earth|Thunder|Water|Fire|Air)", "(Ingredient_\w+)"\)', gear))
    bar = price("Ore_Copper") * 1.2
    want = [price(gems[k]) + 4 * bar for k in STAT] + [2 * price(elems[k]) for k in ELEM]
    K.eq([round(x, 6) for x in v["AUG_IN"]], [round(x, 6) for x in want], "S the inputs = gem + 4 Copper Ingots (ore x 1.2) / 2 essences at SkyyBazaar %s prices" % pin["SkyyBazaar"])
    K.notes.append("S prices x3: %s" % dict(zip([i[9:-2] for i in T1], [max(10, p7round(x * 3.0)) for x in want])))
    K.eq(v["AUG_NAMES"], dict((i, "%s Augment I" % i[9:-2]) for i in T1), "S the names = SkyyGear's '<Kind> Augment I'")
    K.check('TAB_NAMES = ["Weapons", "Mounts", "Pet eggs", "Augments"]' in g and '"#SkyyMcTab3"' in g, "S the shop window gets the 4th tab")
    SUI = T08.sui()
    need = ("Header", "HeaderOrnament", "Tab", "Tab_Selected", "Close", SUI.HUB_FRAME["market"], "Tertiary")
    K.eq(SUI.check_jar_kit(jar, need=need), 59, "S the jar's kit art = 59 kit files (byte for byte)")
    K.save()


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString, JLong, JBoolean, JDouble, JImplements, JOverride
    K = HK.Child(out)
    SUI, gear, egg, NONE = T08.colours()
    g, v = gen_data()
    HK.jvm([B.SERVER_JAR], verify=True)
    L = T08.loader(jar)
    J = lambda n: JClass(PKG + n, loader=L)
    Page, Cfg, Reg, Eng, Shop, Wall, Zone = J("MerchPage"), J("MerchCfg"), J("MerchReg"), J("MerchEng"), J("MerchShop"), J("MerchWall"), J("MerchZone")
    sysp = JClass("java.lang.System").getProperties()
    if sysp.get("skyy.bridge") is None:
        sysp.put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    br = sysp.get("skyy.bridge")
    Paths = JClass("java.nio.file.Paths")
    P = lambda p_: Paths.get(p_, JArray(JClass("java.lang.String"))([]))
    mods = os.path.join(scratch, "x1", "mods")
    os.makedirs(os.path.join(mods, "Skyy_SkyyMerchants"), exist_ok=True)
    Cfg.load(P(mods))
    K.eq((int(Cfg.AUG_OFFERS), int(Cfg.AUG_STOCK), float(Cfg.AUG_X)), (4, 3, 3.0), "X the row defaults (4 a visit, 3 each, price x3)")
    dt = open(os.path.join(mods, "Skyy_SkyyMerchants", "config.properties"), encoding="latin-1").read()
    K.check("\nmerchant.augOffers=4\n" in dt and "\nmerchant.augStock=3\n" in dt and "\nprice.augX=3\n" in dt, "X a fresh default file lists the three new lines")
    # ---- prices
    want = [max(10, p7round(x * 3.0)) for x in v["AUG_IN"]]
    K.eq([int(Shop.augPrice(i)) for i in range(18)], want, "X augPrice = inputs x 3 on the P7 rounding: %s" % want)
    K.eq((int(Shop.augPrice(-1)), int(Shop.augPrice(18))), (-1, -1), "X augPrice out of range = -1")
    # ---- restock (ids known through the harness hook; weapons from the default table)
    ex = JClass("java.util.HashSet")()
    for i in T1:
        ex.add(i)
    for w in re.findall(r"\nweapon\.(\w+)=", dt):
        ex.add(w)
    Eng.EXTRA = ex
    z1 = Cfg.zone("zone1")
    K.check(z1 is not None, "X zone1 from the default file")

    def augs_of(stock):
        es = [e.split(":") for e in str(stock).split(",") if e]
        return [(e[1], int(e[2]), int(e[3])) for e in es if e[0] == "3"]
    seen, bad = {}, []
    for _ in range(300):
        a = augs_of(Shop.restock(z1))
        ids = [x[0] for x in a]
        if len(a) != 4 or len(set(ids)) != 4 or ids != sorted(ids, key=T1.index) or any(x[1] != want[T1.index(x[0])] or x[2] != 3 for x in a):
            bad.append(a)
        for i in ids:
            seen[i] = seen.get(i, 0) + 1
    K.check(not bad, "X 300 restocks: 4 distinct T1 augments a visit, in kind order, each at its price with stock 3 (bad: %s)" % bad[:2])
    K.eq(sorted(seen, key=T1.index), T1, "X every one of the 18 kinds is offered over 300 visits (rotating)")
    K.notes.append("X offers per kind over 300 visits: %s" % dict((k[9:-2], seen[k]) for k in T1))
    Cfg.AUG_OFFERS = 30
    a = augs_of(Shop.restock(z1))
    K.eq([x[0] for x in a], T1, "X merchant.augOffers above 18 = all 18 in kind order")
    Cfg.AUG_OFFERS, Cfg.AUG_STOCK, Cfg.AUG_X = 2, 7, 10.0
    a = augs_of(Shop.restock(z1))
    K.check(len(a) == 2 and all(x[2] == 7 and x[1] == max(10, p7round(v["AUG_IN"][T1.index(x[0])] * 10.0)) for x in a), "X 2 offers, stock 7, price x10 - live: %s" % a)
    Cfg.AUG_OFFERS = 0
    K.eq(augs_of(Shop.restock(z1)), [], "X merchant.augOffers 0 = no augments")
    Cfg.AUG_OFFERS, Cfg.AUG_STOCK, Cfg.AUG_X = 4, 3, 3.0
    z4 = Cfg.zone("zone4")
    K.check(len(augs_of(Shop.restock(z4))) == 4 and all(x[0].endswith("_1") for x in augs_of(Shop.restock(z4))), "X the Zone 4 merchant sells T1 augments too (T1 only)")
    ex2 = JClass("java.util.HashSet")()
    for w in re.findall(r"\nweapon\.(\w+)=", dt):
        ex2.add(w)
    Eng.EXTRA = ex2
    K.eq(augs_of(Shop.restock(z1)), [], "X augment ids the server does not know (no SkyyGear) are never offered")
    Eng.EXTRA = ex
    nv = str(Cfg.NEVER)
    Cfg.NEVER = nv + ",Skyy_Aug_*"
    K.eq(augs_of(Shop.restock(z1)), [], "X walled (never-sell Skyy_Aug_*) = never offered")
    Cfg.NEVER = nv
    # ---- the squares: every augment id
    q = dict((r, SUI.QUALITY[r] + "(0.4)") for r in ("Common", "Uncommon", "Rare", "Epic", "Legendary"))
    QN = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]
    got = dict((i, str(Page.rbg(i))) for i in TT.AUG_IDS)
    wanted = {}
    for i in TT.AUG_IDS:
        k, t = i[9:].rsplit("_", 1)
        t = int(t)
        wanted[i] = q[QN[((t + 1) // 2 if k in ELEM else t) - 1]]
    K.eq(got, wanted, "X rbg: all 120 augments = their spec 2.3 rarity (stat / Poison T1-T5 Common..Legendary, elements T1-2 .. T9-10)")
    K.eq([str(Page.augRbg(x)) for x in ("Skyy_Aug_Fire_11", "Skyy_Aug_Brute_6", "Skyy_Aug_Brute_x", "Skyy_Aug_", None, "Weapon_Sword_Frost")], [NONE] * 6,
         "X augRbg: a tier out of range / junk / null / not an augment = the faint grey")
    for k_ in ("gear:fn:rarity",):
        br.remove(k_)
    K.eq((str(Page.rbg("Skyy_PetEgg_Mining_Legendary")), str(Page.rbg("Weapon_Sword_Frost"))), (egg["Legendary"], NONE), "X the 0.1.8 egg square unchanged; no SkyyGear = grey")
    # ---- a stand-in site + the page on a real UICommandBuilder
    site = J("MerchSite")()
    site.zone, site.uuid, site.x, site.y, site.z = "zone1", "npc-0109", 0, 64, 0
    site.placedAt = int(JClass("java.lang.System").currentTimeMillis())
    site.stock = "0:Weapon_Sword_Frost:1000:1,3:Skyy_Aug_Brute_1:190:3,3:Skyy_Aug_Earth_1:150:0,3:Skyy_Aug_Air_1:150:2"
    lst = JClass("java.util.ArrayList")()
    lst.add(site)
    Reg.W.put(Reg.wf("default"), lst)
    of = Shop.offers(site, 3)
    K.eq([[str(x) for x in r] for r in of], [["Skyy_Aug_Brute_1", "Skyy_Aug_Earth_1", "Skyy_Aug_Air_1"], ["190", "150", "150"], ["3", "0", "2"]], "X offers(site, 3) = the augment entries")
    K.eq((int(Shop.adjust(site, 3, "Skyy_Aug_Air_1", -1)), int(Shop.adjust(site, 3, "Skyy_Aug_Earth_1", -1)), int(Shop.adjust(site, 0, "Skyy_Aug_Air_1", -1))), (1, -1, -1),
         "X adjust on category 3 (one taken; sold out refused; the wrong category refused)")
    Shop.adjust(site, 3, "Skyy_Aug_Air_1", 1)
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    pr = U.allocateInstance(PR.class_)
    buyer = JClass("java.util.UUID").randomUUID()
    for f in PR.class_.getDeclaredFields():
        if str(f.getType().getName()) == "java.util.UUID":
            f.setAccessible(True)
            f.set(pr, buyer)
    UCB, UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"), JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    page = Page(pr, "default", "zone1", "npc-0109")

    def build(tab):
        page.tab = tab
        b_, e_ = UCB(), UEB()
        page.build(None, b_, e_, None)
        return " | ".join("%s=%s/%s" % (x.selector, x.data, x.text) for x in b_.getCommands()), len(e_.getEvents())

    def squares(txt):
        return dict((int(a), b) for a, b in re.findall(r"Group #SkyyMcR(\d+)If \{ Anchor: \(Width: 44, Height: 44, Left: 0, Top: \d+\); Background: ([^;]+); \}", txt))
    t3, n3 = build(3)
    K.eq(squares(t3), {0: q["Common"], 1: NONE, 2: q["Common"]}, "X Augments tab: T1 rows = Common squares; the sold-out row = grey")
    K.check("Brute Augment I" in t3 and "Earth Augment I" in t3 and "Air Augment I" in t3 and "190 coins" in t3 and "Sold out - restocks when it moves" in t3,
            "X Augments tab: the names, prices and the sold-out text")
    K.eq(n3, 2 + 5, "X Augments tab: 2 Buy bindings (the sold-out row has none) + 5 base bindings (4 tabs + Close)")
    t0, n0 = build(0)
    K.eq(n0, 1 + 5, "X Weapons tab: 1 Buy + 5 base bindings")
    K.check("#SkyyMcTab3" in t0 and "Augments" in t0, "X the tab row shows the 4th tab 'Augments'")
    site.stock = "0:Weapon_Sword_Frost:1000:1"
    Cfg.AUG_OFFERS = 0
    t3e, n3e = build(3)
    K.check("No augments left this visit - the merchant restocks when it moves." in t3e and n3e == 5 and str(site.stock) == "0:Weapon_Sword_Frost:1000:1",
            "X Augments tab with nothing (augOffers 0) = its empty text, the stock line untouched")
    Cfg.AUG_OFFERS = 4
    # aug3fix: a visit placed by 0.1.8 (no "3:" entries) gets its augments on the FIRST look at the Augments tab, once
    tp0 = int(Shop.AUG_TOPUPS)
    t3t, n3t = build(3)
    a = augs_of(site.stock)
    K.check(len(a) == 4 and str(site.stock).startswith("0:Weapon_Sword_Frost:1000:1,3:") and all(x[2] == 3 and x[1] == want[T1.index(x[0])] for x in a)
            and int(Shop.AUG_TOPUPS) == tp0 + 1 and n3t == 4 + 5 and "No augments left" not in t3t,
            "X FIX a 0.1.8 visit: the first Augments look adds 4 T1 augments (price, stock 3) to its stock line, 4 Buy rows: %s" % a)
    st1 = str(site.stock)
    of2 = Shop.offers(site, 3)
    K.check(str(site.stock) == st1 and len(of2[0]) == 4 and int(Shop.AUG_TOPUPS) == tp0 + 1, "X FIX ... only once (the second look keeps the same offers)")
    K.eq([len(Shop.offers(site, c)[0]) for c in (0, 1, 2)], [1, 0, 0], "X FIX ... the other tabs do not top up / change")
    lt = str(J("MerchCore").listText("default", int(JClass("java.lang.System").currentTimeMillis())))
    K.check("stock 5 offers" in lt and str(site.stock) == st1, "X FIX2 /merchantadmin list counts the Augments offers too (1 weapon + 4 augments = 5): %s" % lt[-160:])
    site.stock = "0:Weapon_Sword_Frost:1000:1,3:Skyy_Aug_Earth_1:150:0"
    Shop.offers(site, 3)
    K.check(str(site.stock) == "0:Weapon_Sword_Frost:1000:1,3:Skyy_Aug_Earth_1:150:0" and int(Shop.AUG_TOPUPS) == tp0 + 1, "X FIX a sold-out augment visit is never refilled")
    s2 = J("MerchSite")()
    s2.stock = "0:Weapon_Sword_Frost:1000:1"
    Shop.offers(s2, 3)
    s3 = J("MerchSite")()
    s3.uuid = "npc-x"
    Shop.offers(s3, 3)
    K.check(str(s2.stock) == "0:Weapon_Sword_Frost:1000:1" and str(s3.stock) == "" and not bool(Shop.augTop(None)) and int(Shop.AUG_TOPUPS) == tp0 + 1,
            "X FIX an unplaced site (no merchant) / an empty stock line / null = no top-up")
    site.stock = "0:Weapon_Sword_Frost:1000:1,3:Skyy_Aug_Brute_1:190:3,3:Skyy_Aug_Earth_1:150:0,3:Skyy_Aug_Air_1:150:2"
    page.tab = 0
    try:
        page.handleDataEvent(None, None, JString('{"a":"tab","i":"3"}'))
    except Exception:
        pass          # rebuild() needs a live page manager; the field is what the click changes
    K.eq(int(page.tab), 3, "X a click on the 4th tab selects it (0.1.8 refused i = 3)")
    # ---- the buy, end to end (real container, stand-in coins + engine seam)
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    inv = SIC(4)
    ST = {"purse": {str(buyer): 1000}}

    @JImplements("java.util.function.Function")
    class Get(object):
        @JOverride
        def apply(self, a):
            return JLong(ST["purse"].get(str(a), 0))

    @JImplements("java.util.function.Function")
    class Take(object):
        @JOverride
        def apply(self, a):
            u, n = str(a[0]), int(a[1])
            if ST["purse"].get(u, 0) < n:
                return JBoolean(False)
            ST["purse"][u] -= n
            return JBoolean(True)

    @JImplements("java.util.function.Function")
    class Add(object):
        @JOverride
        def apply(self, a):
            u, n = str(a[0]), int(a[1])
            ST["purse"][u] = ST["purse"].get(u, 0) + n
            return JLong(ST["purse"][u])
    br.put("coins:fn:get", Get())
    br.put("coins:fn:take", Take())
    br.put("coins:fn:add", Add())
    IC = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")

    @JImplements(J("MerchApi"))
    class Api(object):
        @JOverride
        def worlds(self): return JArray(JString)([])
        @JOverride
        def exec(self, wn, r): return False
        @JOverride
        def height(self, wn, x, z): return -1
        @JOverride
        def block(self, wn, x, y, z): return None
        @JOverride
        def fluid(self, wn, x, y, z): return False
        @JOverride
        def env(self, wn, x, y, z): return None
        @JOverride
        def players(self, wn): return JArray(JDouble)([])
        @JOverride
        def spawnPoint(self, wn): return None
        @JOverride
        def roleOk(self, role): return True
        @JOverride
        def spawn(self, wn, role, x, y, z, yaw, name): return None
        @JOverride
        def present(self, wn, uuid, x, z, name): return 0
        @JOverride
        def remove(self, wn, uuid): return 0
        @JOverride
        def tell(self, wn, text, color): pass
        @JOverride
        def tellPlayer(self, u, text, color): pass
        @JOverride
        def conts(self, player):
            a = JArray(IC)(1)
            a[0] = inv
            return a
        @JOverride
        def pos(self, ref, st): return None
        @JOverride
        def open(self, ref, pr_, pg): return False
    Eng.API = Api()
    Shop.LOGF = Paths.get(os.path.join(mods, "Skyy_SkyyMerchants", "sales.log"))
    pos = JArray(JDouble)([0.5, 64.0, 0.5])
    # a bare JVM has no Item assets: the engine's container cannot take an id it does not know, so this runs the cat-3 buy up to the give and
    # its refund branch (coins taken, nothing arrived -> coins back, stock back). The give itself is 0.1.1's proven path (vanilla items, booted assets).
    r0 = str(Shop.buy(buyer, "Tester", JString("p"), pos, "default", "zone1", "npc-0109", 3, "Skyy_Aug_Brute_1"))
    K.check(r0 == "-The item could not be given - your 190 coins were refunded." and ST["purse"][str(buyer)] == 1000 and int(Shop.countIn(inv, "Skyy_Aug_Brute_1")) == 0,
            "X buy an augment (category 3): the price 190 is taken, the give runs, nothing arrived -> 190 refunded (purse %d): %s" % (ST["purse"][str(buyer)], r0))
    K.eq([str(x) for x in Shop.offers(site, 3)[2]], ["3", "0", "2"], "X ... the reserved stock went back (3)")
    log = open(os.path.join(mods, "Skyy_SkyyMerchants", "sales.log"), encoding="utf8").read()
    K.check("REFUND Tester " in log and " Skyy_Aug_Brute_1 190" in log, "X ... and sales.log has the REFUND line with the augment price")
    ST["purse"][str(buyer)] = 100
    r1 = str(Shop.buy(buyer, "Tester", JString("p"), pos, "default", "zone1", "npc-0109", 3, "Skyy_Aug_Air_1"))
    K.check(r1.startswith("-You need 150 coins - you have 100") and ST["purse"][str(buyer)] == 100 and [str(x) for x in Shop.offers(site, 3)[2]] == ["3", "0", "2"],
            "X too poor for an augment: refused before anything moves: %s" % r1)
    K.check("Sold out" in str(Shop.buy(buyer, "Tester", JString("p"), pos, "default", "zone1", "npc-0109", 3, "Skyy_Aug_Earth_1")), "X a sold-out augment = Sold out")
    ex.add("Skyy_Aug_Brute_2")
    K.check("does not sell" in str(Shop.buy(buyer, "Tester", JString("p"), pos, "default", "zone1", "npc-0109", 3, "Skyy_Aug_Brute_2")), "X a T2 augment is not on offer")
    K.check("does not sell" in str(Shop.buy(buyer, "Tester", JString("p"), pos, "default", "zone1", "npc-0109", 0, "Skyy_Aug_Brute_1")), "X the right id in the wrong tab is not on offer")
    Eng.API = None
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyMerchants", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("exec", run_exec), ("live", T08.run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyMerchants"))
