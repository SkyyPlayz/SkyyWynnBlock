"""Harness for SkyyMerchants 0.1.10 (the Market tab's merchants bridge: merchants:fn:tab read + merchants:fn:tabact buy;
tools/merchants_0_1_10_patch.py). Build first:
    python tools/merchants_0_1_10_patch.py && python SkyyMerchants/build_skyymerchants_0.1.10.py
    python SkyyMerchants/test_skyymerchants_0.1.10.py [--dir <folder inside tools/dev/scratch/>] [--keep] [--expect-dump]

Phases (fresh child JVMs, -Xverify:all, tools/harness_kit.py):
  S   static   the patch re-runs to identical bytes; one new class (MerchTabFn), no new system / command / setting; the tier table = tools/
               tier_tags.py (rows, else the metal / level band) for every stock / fallback / augment id; setup puts + shutdown removes both keys;
               buy() calls inRange (one range test)
  A   verify   every class loads + initialises
  C   compare  0.1.9 -> 0.1.10 (EXPECT below)
  X   exec     the 0.1.9 exec phase re-run on the 0.1.10 jar (augments, restock, the page, the buy refund path - unchanged)
  M   market   EXECUTES every new path through MerchTabFn.apply (the TEST_CTX seam = the player's world-thread context) on REAL
               SimpleItemContainers with stand-in Item assets (items really arrive) + stand-in coins: the READ (header, 4 tabs, every zone of
               the world, out / moved / switched off, near = inRange (from afar: no npc / x|y|z / distance / stock - mkt1 fix), the offers SORTED BY TIER then name with price / left / the
               page's rarity square, another world = x|); the BUY on TWINS - Alice by the bridge (two presses), Bob by the shop page's own
               handleDataEvent (two clicks) - the same coins, the same item, the same stock left, word for word; EVERY refusal moves nothing
               (the first press, a double click, a changed price, a stale profile key, a profile switch between presses, profile busy,
               server stopping, too far away, not enough coins, a full inventory, sold out, the merchant moved on, an expired ask, another op
               in between, junk / unknown ops); the give-failed refund through the bridge; coins + items + stock CONSERVED
  D   live     a scratch COPY of the live NewBetaTest Skyy_SkyyMerchants started TWICE (0.1.8's live phase) + the read on the live registry
               (every tab) writes nothing
  AA  engine-access audit
NOT COVERED (UNVERIFIED in game): Universe.getPlayer / Store.isInThread / the world name in the real ctx() (the harness uses TEST_CTX);
the real inventory give of the engine with real item assets (stand-in Item.UNKNOWN assets here).
Exit code 1 on any failure.
"""
import os, sys, re, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import tier_tags as TT

VERSION = "0.1.10"
PKG = "com.skyy.merchants."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMerchants-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMerchants-0.1.9.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "mkt1", "me")))
GEN = os.path.join(HERE, "build_skyymerchants_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyymerchants_0.1.9.py")
PATCH = os.path.join(ROOT, "tools", "merchants_0_1_10_patch.py")
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyMerchants")
EXPECT = {"CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "MerchCfg": ["~m applyAll", "~m seed"],     # the version in the file header text
          "MerchShop": ["+f TIERS", "+f TIER_SPEC", "+m inRange", "+m tier", "~<clinit>", "~m buy"],
          "SkyyMerchantsPlugin": ["~m setup", "~m shutdown"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = ["MerchTabFn"]


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


T09 = tmod(os.path.join(HERE, "test_skyymerchants_0.1.9.py"), "tme019")
T08 = T09.T08


# ------------------------------------------------------------------------------------------------------------------- S
def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.count('VERSION = "0.1.10"') == 1, "S VERSION")
    K.eq([g.count(w) - o.count(w) for w in ("registerSystem(", "registerCommand(", "= cls(", "CFG.row(")], [0, 0, 1, 0], "S one new class, no system / command / setting row")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    bu = g[g.index("public static String buy(java.util.UUID u"):g.index("# MerchCore: the per-world second")]
    K.check("if (!inRange(s, pos))" in bu and "dx * dx" not in bu, "S buy() uses inRange (one range test, no second copy)")
    ta = g[g.index('tabf = cls("MerchTabFn")'):g.index("# MerchOpen: opens the page next tick")]
    K.check(ta.count("@PKG@.MerchShop.buy(") == 1 and "MerchCoins.take" not in ta and "MerchShop.give" not in ta and "adjust(" not in ta,
            "S MerchTabFn moves coins / items / stock ONLY through MerchShop.buy")
    K.check('bridge().put("merchants:fn:tab"' in g and 'bridge().put("merchants:fn:tabact"' in g and 'bridge().remove("merchants:fn:tab")' in g
            and 'bridge().remove("merchants:fn:tabact")' in g, "S setup puts both keys, shutdown removes them")
    spec = re.search(r'\nMERCH_TIER_SPEC = ', g)
    K.check(spec is not None, "S the tier table is built in the script")
    K.save()


def run_exec(out, jar, scratch, home):
    T09.run_exec(out, jar, scratch, home)


# ------------------------------------------------------------------------------------------------------------------- stand-ins
_FAKE = [0]


def fake_items(ids):
    """an Item asset store that answers Item.UNKNOWN for every id given (= tools' Bazaar 0.1.20 harness stand-in): those ids really fit and
    stack in SimpleItemContainers, so a buy really moves an item"""
    from jpype import JClass
    _FAKE[0] += 1
    sfx = "Me%d" % _FAKE[0]
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    CtF, CtM, CtC = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyMcFakeStore" + sfx, jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fake.addConstructor(CtC.make("public SkyyMcFakeStore%s() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }" % sfx, fake))
    FAKEC = fake.toClass(AS.class_)
    store = us.allocateInstance(FAKEC)
    fm = AS.class_.getDeclaredField("assetMap")
    fm.setAccessible(True)
    DAMN = "com.hypixel.hytale.assetstore.map.DefaultAssetMap"
    ITMN = "com.hypixel.hytale.server.core.asset.type.item.config.Item"
    kmap = jp.makeClass("com.hypixel.hytale.assetstore.map.SkyyMcKnownMap" + sfx, jp.get(DAMN))
    kmap.addField(CtF.make("public static final java.util.HashSet KNOWN = new java.util.HashSet();", kmap))
    kmap.addConstructor(CtC.make("public SkyyMcKnownMap%s() { super(); }" % sfx, kmap))
    kmap.addMethod(CtM.make("public com.hypixel.hytale.assetstore.JsonAsset getAsset(Object key) { if (key != null && KNOWN.contains(key)) return "
                            "%s.UNKNOWN; return super.getAsset(key); }" % ITMN, kmap))
    KMap = JClass(kmap.toClass(JClass(DAMN).class_))
    fm.set(store, KMap())
    fi_ = JClass(ITMN).class_.getDeclaredField("ASSET_STORE")
    fi_.setAccessible(True)
    fi_.set(None, store)
    for i in ids:
        KMap.KNOWN.add(i)
    return KMap.KNOWN


# ------------------------------------------------------------------------------------------------------------------- M
def run_market(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString, JLong, JBoolean, JDouble, JImplements, JOverride, JObject
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST], verify=True)
    L = T08.loader(jar)
    J = lambda n: JClass(PKG + n, loader=L)
    Page, Cfg, Reg, Eng, Shop, Core, Site, TF = (J("MerchPage"), J("MerchCfg"), J("MerchReg"), J("MerchEng"), J("MerchShop"), J("MerchCore"),
                                                 J("MerchSite"), J("MerchTabFn"))
    sysp = JClass("java.lang.System").getProperties()
    if sysp.get("skyy.bridge") is None:
        sysp.put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    br = sysp.get("skyy.bridge")
    Paths = JClass("java.nio.file.Paths")
    P = lambda p_: Paths.get(p_, JArray(JClass("java.lang.String"))([]))
    mods = os.path.join(scratch, "m1", "mods")
    os.makedirs(os.path.join(mods, "Skyy_SkyyMerchants"), exist_ok=True)
    Cfg.load(P(mods))
    dt = open(os.path.join(mods, "Skyy_SkyyMerchants", "config.properties"), encoding="latin-1").read()
    weapons = re.findall(r"\nweapon\.(\w+)=", dt)
    T1 = [str(x) for x in Shop.AUG_IDS]
    z1 = Cfg.zone("zone1")
    wn = str(z1.world)
    others = [z for z in Cfg.ZONES if str(z.world) == wn and str(z.key) != "zone1"]
    # ---- the tier table
    K.eq([int(Shop.tier(a)) for a in T1], [1] * len(T1), "M tier: every T1 augment = 1")
    rowed = [w for w in weapons if w in TT.ROWS]
    K.check(all(int(Shop.tier(w)) == TT.tier(w) for w in rowed), "M tier: a stock weapon with a tools/tier_tags.py row = its row (%d of %d)" % (len(rowed), len(weapons)))
    K.check(all(1 <= int(Shop.tier(w)) < 99 for w in weapons) and int(Shop.tier("Weapon_Not_A_Thing")) == 99 and int(Shop.tier(None)) == 99,
            "M tier: every default stock weapon is tiered; an unknown id / null = 99 (last)")
    by_t = {}
    for w in weapons:
        by_t.setdefault(int(Shop.tier(w)), []).append(w)
    pick = []
    for t_ in sorted(by_t, reverse=True):
        pick += by_t[t_][:2]
    pick = pick[:5]
    K.check(len(set(int(Shop.tier(w)) for w in pick)) >= 2, "M the test stock spans %d tiers: %s" % (len(set(int(Shop.tier(w)) for w in pick)), pick))
    known = fake_items(pick + T1 + ["Skyy_Filler_Block"])
    ex = JClass("java.util.HashSet")()
    for i in pick + T1 + ["Skyy_Not_Known_Here"]:
        ex.add(i)
    Eng.EXTRA = ex
    # ---- the world: zone1's merchant at (10, 64, 10)
    site = Site()
    site.zone, site.uuid, site.x, site.y, site.z = "zone1", "npc-mkt1", 10, 64, 10
    site.placedAt = int(JClass("java.lang.System").currentTimeMillis())
    site.rumour = "near the old well"
    stock0 = ",".join(["0:%s:%d:%d" % (w, 500 + 100 * k, 2) for k, w in enumerate(pick)] + ["0:Skyy_Not_Known_Here:300:3", "3:%s:190:3" % T1[3], "3:%s:150:1" % T1[0]])
    site.stock = stock0
    lst = JClass("java.util.ArrayList")()
    lst.add(site)
    Reg.W.put(Reg.wf(wn), lst)
    Shop.LOGF = Paths.get(os.path.join(mods, "Skyy_SkyyMerchants", "sales.log"))
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    IC = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    inv = {"A": SIC(8), "B": SIC(8)}
    UU = JClass("java.util.UUID")
    ua, ub = UU.randomUUID(), UU.randomUUID()
    ST = {"purse": {str(ua): 100000, str(ub): 100000}, "prof": {}, "pos": {"A": [10.5, 64.0, 10.5], "B": [10.5, 64.0, 10.5]}}
    R = int(Cfg.USE_RANGE)

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

    @JImplements("java.util.function.Function")
    class PKey(object):
        @JOverride
        def apply(self, u):
            return JString(ST["prof"].get(str(u), str(u) + "-main"))
    br.put("coins:fn:get", Get())
    br.put("coins:fn:take", Take())
    br.put("coins:fn:add", Add())
    br.put("profile:fn:key", PKey())

    def who_of(player):
        return "B" if player is None else str(player)

    @JImplements(J("MerchApi"))
    class Api(object):
        @JOverride
        def worlds(self): return JArray(JString)([])
        @JOverride
        def exec(self, w_, r): return False
        @JOverride
        def height(self, w_, x, z): return -1
        @JOverride
        def block(self, w_, x, y, z): return None
        @JOverride
        def fluid(self, w_, x, y, z): return False
        @JOverride
        def env(self, w_, x, y, z): return None
        @JOverride
        def players(self, w_): return JArray(JDouble)([])
        @JOverride
        def spawnPoint(self, w_): return None
        @JOverride
        def roleOk(self, role): return True
        @JOverride
        def spawn(self, w_, role, x, y, z, yaw, name): return None
        @JOverride
        def present(self, w_, uuid, x, z, name): return 0
        @JOverride
        def remove(self, w_, uuid): return 0
        @JOverride
        def tell(self, w_, text, color): pass
        @JOverride
        def tellPlayer(self, u, text, color): pass
        @JOverride
        def conts(self, player):
            if ST.get("fail") and who_of(player) == "A":
                ST["calls"] = ST.get("calls", 0) + 1
                if ST["calls"] >= 3:          # room + the count before see the container; the give + the count after see none = a failed give
                    return JArray(IC)(0)
            a = JArray(IC)(1)
            a[0] = inv[who_of(player)]
            return a
        @JOverride
        def pos(self, ref, st): return JArray(JDouble)(ST["pos"]["B"])
        @JOverride
        def open(self, ref, pr_, pg): return False
    Eng.API = Api()

    @JImplements("java.util.function.Function")
    class Ctx(object):
        @JOverride
        def apply(self, u):
            if str(u) != str(ua):
                return None
            a = JArray(JObject)(4)
            a[0], a[1], a[2], a[3] = JString("Alice"), JString("A"), JArray(JDouble)(ST["pos"]["A"]), JString(wn)
            return a
    RD, AC = TF(0), TF(1)
    OA = JClass("java.lang.Object[]")
    Int = JClass("java.lang.Integer")

    def read(cat=0):
        a = OA(2)
        a[0], a[1] = ua, Int.valueOf(cat)
        r = RD.apply(a)
        return None if r is None else str(r)

    def act(op, arg, tok=None, clear=True):
        if clear:
            TF.LASTOP.clear()
        a = OA(4)
        a[0], a[1], a[2], a[3] = ua, JString(tok if tok is not None else tokA()), JString(op), JString(arg)
        r = AC.apply(a)
        return None if r is None else str(r)

    def tokA():
        return str(TF.pkey(ua))

    def lines(s, k):
        return [l.split("|") for l in s.split("\n") if l.startswith(k + "|")]

    def count(who, i):
        return int(Shop.countIn(inv[who], i))

    def left(cat, i):
        of = Shop.offers(site, cat)
        return dict(zip([str(x) for x in of[0]], [int(str(x)) for x in of[2]])).get(i)

    ALLI = pick + T1 + ["Skyy_Not_Known_Here"]

    def snap():
        return (dict(ST["purse"]), dict((w_, [count(w_, i) for i in ALLI]) for w_ in ("A", "B")), str(site.stock))
    # ---- not the world thread / junk
    TF.TEST_CTX = None
    K.check(read() is None and act("buy", "x") is None, "M no player context (not on the world thread / no Universe) = null, nothing read or done")
    TF.TEST_CTX = Ctx()
    K.check(RD.apply(JString("junk")) is None and AC.apply(OA(1)) is None, "M junk / an action without its arguments = null")
    a2 = OA(2)
    a2[0], a2[1] = ub, Int.valueOf(0)
    K.check(RD.apply(a2) is None, "M a player with no context = null")
    # ---- READ
    s = read(0)
    hd = s.split("\n")[0].split("|")
    K.check(hd[0] == "ok" and hd[1] == tokA() and hd[2:6] == ["1", "1", "100000", "0"] and hd[6] == wn and hd[7] == str(R),
            "M READ header: the profile key, on, coins ready, the purse, tab 0, the world, the use range (%s)" % hd)
    K.eq([f[1:] for f in lines(s, "k")], [["0", "Weapons"], ["1", "Mounts"], ["2", "Pet eggs"], ["3", "Augments"]], "M READ the 4 shop tabs")
    zl = dict((f[1], f) for f in lines(s, "z"))
    K.check(set(zl) == set(["zone1"] + [str(z.key) for z in others]), "M READ every merchant zone of the world (%s)" % sorted(zl))
    z = zl["zone1"]
    K.check(z[2] == str(z1.name) and z[3] == str(z1.band()) and z[4] == "1" and z[5] == "npc-mkt1" and z[6:9] == ["10", "64", "10"]
            and 0 < int(z[9]) <= int(Cfg.MOVE_S) * 1000 and z[10] == "0" and z[11] == "1" and z[12] == "near the old well",
            "M READ zone1: name, band, out, the npc, where, moves in, 0 blocks away, NEAR, the rumour (%s)" % z)
    K.check(all(f[4] == "0" and f[5] == "" for k_, f in zl.items() if k_ != "zone1"), "M READ the other zones: no merchant out yet")
    sl = lines(s, "s")
    offers = Shop.offers(site, 0)
    exp = sorted(range(len(offers[0])), key=lambda i: (int(Shop.tier(str(offers[0][i]))), str(Shop.rowName(str(offers[0][i]))).lower() + "\x01" + str(offers[0][i])))
    K.eq([f[3] for f in sl], [str(offers[0][i]) for i in exp], "M READ the Weapons offers SORTED BY TIER, then name (Shop.tier + rowName)")
    K.check([int(f[6]) for f in sl] == sorted(int(f[6]) for f in sl) and len(set(f[6] for f in sl)) >= 2, "M ... the tier column rises (%s)" % [f[6] for f in sl])
    K.check(all(f[1] == "zone1" and f[2] == "0" and f[4] == str(Shop.rowName(f[3])) and f[5] == str(Page.rbg(f[3])) and int(f[7]) == int(str(offers[1][list(map(str, offers[0])).index(f[3])]))
                and int(f[8]) == left(0, f[3]) for f in sl), "M ... each row: name (rowName), the page's rarity square (rbg), price + left = offers()")
    K.check("Skyy_Not_Known_Here" in [f[3] for f in sl] and [f for f in sl if f[3] == "Skyy_Not_Known_Here"][0][6] == "99" and sl[-1][3] == "Skyy_Not_Known_Here",
            "M ... an untiered (admin-added) offer sorts last (tier 99)")
    s3 = read(3)
    want3 = sorted([T1[0], T1[3]], key=lambda i: str(Shop.rowName(i)).lower())
    K.eq([f[3] for f in lines(s3, "s")], want3, "M READ the Augments tab (tier 1 each, then by name: %s)" % want3)
    K.eq(lines(read(1), "s"), [], "M READ the Mounts tab: no offers")
    K.check(read(9).split("\n")[0].split("|")[5] == "0", "M READ a tab out of range = tab 0")
    ST["pos"]["A"] = [10.5 + R + 3, 64.0, 10.5]
    z = dict((f[1], f) for f in lines(read(0), "z"))["zone1"]
    K.check(z[11] == "0", "M READ %d blocks away = NOT near (inRange) (%s)" % (R + 3, z[10:12]))
    # mkt1 fix (critic finding 1, docs/answered/economy.md LOCKED 2026-10-09 "so you have to find them" / rumours "no coordinates"):
    # from afar the read gives out, moves-in and the rumour ONLY - no npc uuid, no x|y|z, no distance, no stock
    K.check(z[4] == "1" and z[5] == "" and z[6:9] == ["0", "0", "0"] and z[10] == "-1" and z[12] == "near the old well" and 0 < int(z[9]),
            "M FAR READ hides where the merchant is: no npc, no x|y|z, no distance; out + moves in + the rumour stay (%s)" % z)
    st0 = str(site.stock)
    far = [read(c) for c in range(4)]
    K.check(all(not lines(f_, "s") for f_ in far) and str(site.stock) == st0,
            "M FAR READ shows no merchant stock or prices on any of the 4 tabs (stock untouched: no augment top-up from afar)")
    far_arg = "zone1|npc-mkt1|0|%s|%s" % (sl[0][3], sl[0][7])
    s0 = snap()
    fa1, fa2 = act("buy", far_arg), act("buy", far_arg)
    K.check(snap() == s0 and not (fa1 or "").startswith("+") and not (fa2 or "").startswith("+"),
            "M FAR BUY (an arg kept from a near read) buys nothing, pays nothing (%s / %s)" % (fa1, fa2))
    ST["pos"]["A"] = [10.5, 64.0 + R + 4, 10.5]
    K.check(dict((f[1], f) for f in lines(read(0), "z"))["zone1"][11] == "0", "M READ above the range (y) = not near")
    ST["pos"]["A"] = [10.5, 64.0, 10.5]
    Cfg.ON = False
    s_off = read(0)
    K.check(s_off.split("\n")[0].split("|")[2] == "0" and dict((f[1], f) for f in lines(s_off, "z"))["zone1"][4] == "0" and not lines(s_off, "s"),
            "M READ switched off: nothing out, no offers")
    Cfg.ON = True
    old_ctx = TF.TEST_CTX

    @JImplements("java.util.function.Function")
    class Ctx2(object):
        @JOverride
        def apply(self, u):
            a = JArray(JObject)(4)
            a[0], a[1], a[2], a[3] = JString("Alice"), JString("A"), None, JString("Some_Other_World")
            return a
    TF.TEST_CTX = Ctx2()
    so = read(0)
    K.check(lines(so, "x") == [["x", "No traveling merchants roam this world."]] and not lines(so, "z"), "M READ a world without merchant zones = the x| line")
    TF.TEST_CTX = old_ctx
    K.eq(str(site.stock), stock0, "M READS change no stock")
    # ---- BUY twins: Alice by the bridge, Bob by the shop page's own clicks
    w0 = [f for f in lines(read(0), "s") if f[3] != "Skyy_Not_Known_Here"][0]
    wid, wpr = w0[3], int(w0[7])
    arg = "zone1|npc-mkt1|0|%s|%d" % (wid, wpr)
    s0 = snap()
    r1 = act("buy", arg)
    K.check(r1.startswith("=Buy ") and "Press Buy again within 10 s" in r1 and snap() == s0, "M BUY: the first press asks, nothing moves (%s)" % r1)
    r2 = act("buy", arg)
    K.check(r2 == "+Bought %s for %s coins." % (str(Shop.name(wid)), str(J("MerchLog").grp(wpr))) and ST["purse"][str(ua)] == s0[0][str(ua)] - wpr
            and count("A", wid) == 1 and left(0, wid) == 1, "M ... the same press again buys: paid %d, the item arrived, 1 left (%s)" % (wpr, r2))
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    pr = uf.get(None).allocateInstance(PR.class_)
    for f in PR.class_.getDeclaredFields():
        if str(f.getType().getName()) == "java.util.UUID":
            f.setAccessible(True)
            f.set(pr, ub)
    page = Page(pr, wn, "zone1", "npc-mkt1")
    UCB, UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"), JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    page.tab = 0
    page.build(None, UCB(), UEB(), None)
    pi = [str(x) for x in page.ids].index(wid)

    def pclick():
        try:
            page.handleDataEvent(None, None, JString('{"a":"buy","i":"%d","t":"%s"}' % (pi, str(page.tok))))
        except Exception:
            pass          # rebuild() needs a live page manager; the purchase ran before it
        return str(page.info)
    pb0 = ST["purse"][str(ub)]
    i1 = pclick()
    i2 = pclick()
    K.check(i1.startswith("=Buy ") and i2 == r2 and ST["purse"][str(ub)] == pb0 - wpr and count("B", wid) == 1 and left(0, wid) == 0,
            "M TWIN: Bob's page (two clicks) = the same: paid %d, the item, the stock now 0, word for word (%s)" % (wpr, i2))
    log = open(os.path.join(mods, "Skyy_SkyyMerchants", "sales.log"), encoding="utf8").read()
    K.check(log.count("BUY Alice %s " % ua) == 1 and log.count(" %s %s %d" % ("zone1", wid, wpr)) == 2, "M ... both sales logged once (BUY lines)")
    s0 = snap()
    r = act("buy", arg)
    r = act("buy", arg)
    K.check(r == "-Sold out - the merchant restocks when it moves." and snap() == s0, "M SOLD OUT through the bridge = the page's words, nothing moves (%s)" % r)

    def nothing(what, r_, prefix, s_=None):
        K.check(r_ is not None and r_.startswith(prefix) and snap() == (s_ or s0), "M %s = refused, nothing moved: %s" % (what, r_))
    w1 = [f for f in lines(read(0), "s") if f[3] not in (wid, "Skyy_Not_Known_Here")][0]
    arg1 = "zone1|npc-mkt1|0|%s|%s" % (w1[3], w1[7])
    s0 = snap()
    # a double click: the confirm press twice within 350 ms buys once
    act("buy", arg1)
    a_ = OA(4)
    a_[0], a_[1], a_[2], a_[3] = ua, JString(tokA()), JString("buy"), JString(arg1)
    TF.LASTOP.clear()
    d1, d2 = str(AC.apply(a_)), str(AC.apply(a_))
    K.check(d1.startswith("+Bought") and d2 == "=One moment." and count("A", w1[3]) == 1 and ST["purse"][str(ua)] == s0[0][str(ua)] - int(w1[7]),
            "M a DOUBLE CLICK on the confirm buys once (%s / %s)" % (d1[:30], d2))
    s0 = snap()
    w2 = [f for f in lines(read(0), "s") if int(f[8]) > 0 and f[3] != "Skyy_Not_Known_Here"][0]
    arg2 = "zone1|npc-mkt1|0|%s|%s" % (w2[3], w2[7])
    nothing("a changed price (shown 1 less)", act("buy", "zone1|npc-mkt1|0|%s|%d" % (w2[3], int(w2[7]) - 1)), "=The price changed")
    nothing("a stale profile key", act("buy", arg2, tok="someone-else"), "=Your profile changed")
    act("buy", arg2)
    ST["prof"][str(ua)] = str(ua) + "-p2"
    nothing("a profile switch between the presses (asks again)", act("buy", arg2), "=Buy ")
    del ST["prof"][str(ua)]
    nothing("... and back (asks again)", act("buy", arg2), "=Buy ")
    TF.ARM.put(ua, JString(str(TF.ARM.get(ua)).rsplit("#", 1)[0] + "#" + str(int(JClass("java.lang.System").currentTimeMillis()) - 1)))
    nothing("an EXPIRED ask (over 10 s)", act("buy", arg2), "=Buy ")
    nothing("another op in between", act("sell", "x|y|0|z|1"), "-Unknown merchant action")
    nothing("... drops the ask", act("buy", arg2), "=Buy ")
    act("sell", "x")
    br.put("profile:busy:" + str(ua), JBoolean(True))
    nothing("profile:busy", act("buy", arg2), "-Your profile is still loading")
    br.remove("profile:busy:" + str(ua))
    Reg.STOPPING = True
    nothing("a stopping server", act("buy", arg2), "-The merchants are packing up")
    Reg.STOPPING = False
    for j_ in ("zone1|npc-mkt1|0|%s" % w2[3], "zone1|npc-mkt1|x|%s|5" % w2[3], "zone1|npc-mkt1|7|%s|5" % w2[3], "|npc-mkt1|0|%s|5" % w2[3], ""):
        nothing("junk %r" % j_, act("buy", j_), "-Unknown merchant action")
    # refusals of MerchShop.buy itself (after the two presses): too far, too poor, full, moved on
    ST["pos"]["A"] = [10.5 + R + 3, 64.0, 10.5]
    act("buy", arg2)
    nothing("too far away (after the confirm)", act("buy", arg2), "-Walk back to the merchant to buy (within %d blocks)" % R)
    ST["pos"]["A"] = [10.5, 64.0, 10.5]
    keep = ST["purse"][str(ua)]
    ST["purse"][str(ua)] = int(w2[7]) - 1
    s0 = snap()
    act("buy", arg2)
    nothing("not enough coins", act("buy", arg2), "-You need ")
    ST["purse"][str(ua)] = keep
    s0 = snap()
    for k in range(8):
        if inv["A"].getItemStack(JClass("java.lang.Short")(k)) is None:
            inv["A"].setItemStackForSlot(JClass("java.lang.Short")(k), IS("Skyy_Filler_Block", 1))
    s0 = snap()
    argf = "zone1|npc-mkt1|3|%s|190" % T1[3]
    act("buy", argf)
    nothing("a full inventory", act("buy", argf), "-Your inventory is full")
    for k in range(8):
        it = inv["A"].getItemStack(JClass("java.lang.Short")(k))
        if it is not None and str(it.getItemId()) == "Skyy_Filler_Block":
            inv["A"].setItemStackForSlot(JClass("java.lang.Short")(k), None)
    s0 = snap()
    act("buy", "zone1|npc-old|0|%s|%s" % (w2[3], w2[7]))
    nothing("the merchant moved on (another npc)", act("buy", "zone1|npc-old|0|%s|%s" % (w2[3], w2[7])), "-The merchant has moved on")
    act("buy", "zone1|npc-mkt1|1|%s|%s" % (w2[3], w2[7]))
    nothing("the right id in the wrong tab", act("buy", "zone1|npc-mkt1|1|%s|%s" % (w2[3], w2[7])), "-The merchant does not sell that this visit")
    # the give-failed refund through the bridge (the item never arrives): coins back, stock back
    s0 = snap()
    lk = left(0, "Skyy_Not_Known_Here")
    act("buy", "zone1|npc-mkt1|0|Skyy_Not_Known_Here|300")
    ST["fail"], ST["calls"] = True, 0
    rr = act("buy", "zone1|npc-mkt1|0|Skyy_Not_Known_Here|300")
    ST["fail"] = False
    K.check(rr == "-The item could not be given - your 300 coins were refunded." and snap() == s0 and left(0, "Skyy_Not_Known_Here") == lk,
            "M a failed give through the bridge: coins refunded, the stock back, nothing lost (%s)" % rr)
    # the augments tab: a buy through the bridge
    s0 = snap()
    act("buy", "zone1|npc-mkt1|3|%s|150" % T1[0])
    ra = act("buy", "zone1|npc-mkt1|3|%s|150" % T1[0])
    K.check(ra.startswith("+Bought") and count("A", T1[0]) == 1 and ST["purse"][str(ua)] == s0[0][str(ua)] - 150 and left(3, T1[0]) == 0,
            "M an augment through the bridge (tab 3): paid 150, it arrived, sold out now (%s)" % ra)
    # merchants switched off
    Cfg.ON = False
    s0 = snap()
    act("buy", arg2)
    nothing("merchants switched off", act("buy", arg2), "-The merchants are away")
    Cfg.ON = True
    # moved: the site has a new npc -> the read shows the new one, the old arg is refused
    site.uuid = "npc-next"
    zz = dict((f[1], f) for f in lines(read(0), "z"))["zone1"]
    K.check(zz[5] == "npc-next", "M READ after a move shows the new merchant")
    s0 = snap()
    act("buy", arg2)
    nothing("the old merchant's offer after a move", act("buy", arg2), "-The merchant has moved on")
    # conservation over the whole phase: coins out of the purses = coins logged as sales; items in = sales
    total_paid = (100000 * 2) - (ST["purse"][str(ua)] + ST["purse"][str(ub)])
    logged = sum(int(l.split(" ")[-1]) for l in open(os.path.join(mods, "Skyy_SkyyMerchants", "sales.log"), encoding="utf8").read().splitlines() if "\tBUY " in l)
    items = sum(count(w_, i) for w_ in ("A", "B") for i in ALLI)
    nbuys = sum(1 for l in open(os.path.join(mods, "Skyy_SkyyMerchants", "sales.log"), encoding="utf8").read().splitlines() if "\tBUY " in l)
    K.check(total_paid == logged and items == nbuys, "M CONSERVED: coins paid %d = the BUY lines %d; items held %d = %d sales" % (total_paid, logged, items, nbuys))
    K.check(int(TF.READS) > 10 and int(TF.ACTS) > 20, "M counters: %d reads, %d actions" % (int(TF.READS), int(TF.ACTS)))
    TF.TEST_CTX = None
    Eng.API = None
    Eng.EXTRA = None
    K.save()


# ------------------------------------------------------------------------------------------------------------------- D
def run_live(out, jar, scratch, home):
    T08.run_live(out + ".t08", jar, scratch, home)
    import json
    from jpype import JClass, JArray, JImplements, JOverride, JObject, JString
    K = HK.Child(out)
    try:
        prev = json.load(open(out + ".t08"))
        for c in prev.get("checks", []) if isinstance(prev, dict) else []:
            pass
    except Exception:
        prev = None
    K.check(prev is not None, "D 0.1.8's live phase (two starts, no file changes) ran on the 0.1.10 jar")
    if isinstance(prev, dict):
        for f_ in prev.get("fails", []):
            K.check(False, "D (start twice) %s" % f_)
    Paths = JClass("java.nio.file.Paths")
    P = lambda p_: Paths.get(p_, JArray(JClass("java.lang.String"))([]))
    mods = os.path.dirname(home)
    h0 = HK.tree_hash(home)
    L = T08.loader(jar)
    J = lambda n: JClass(PKG + n, loader=L)
    J("MerchLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyMerchants")
    J("MerchCfg").load(P(mods))
    J("MerchReg").DIR = P(os.path.join(home, "merchants"))
    worlds = sorted(set(str(z.world) for z in J("MerchCfg").ZONES))
    TF = J("MerchTabFn")
    OA = JClass("java.lang.Object[]")
    got = []
    for wn in worlds:
        @JImplements("java.util.function.Function")
        class Ctx(object):
            @JOverride
            def apply(self, u):
                a = JArray(JObject)(4)
                a[0], a[1], a[2], a[3] = JString("Live"), None, None, JString(wn)
                return a
        TF.TEST_CTX = Ctx()
        for cat in range(4):
            a = OA(2)
            a[0], a[1] = JClass("java.util.UUID").randomUUID(), JClass("java.lang.Integer").valueOf(cat)
            r = TF(0).apply(a)
            got.append((wn, cat, None if r is None else str(r)))
    TF.TEST_CTX = None
    K.check(got and all(r is not None and r.startswith("ok|") for _w, _c, r in got), "D the read answers on the live registry for %s x 4 tabs" % worlds)
    nz = sum(1 for _w, c, r in got if c == 0 for l in r.split("\n") if l.startswith("z|"))
    ns = sum(1 for _w, _c, r in got for l in r.split("\n") if l.startswith("s|"))
    K.notes.append("D live read: %d zone lines, %d offer lines over %d worlds" % (nz, ns, len(worlds)))
    K.check(HK.tree_hash(home) == h0, "D the reads on the live copy write NOTHING (registry + config untouched)")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyMerchants", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("exec", run_exec), ("market", run_market), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyMerchants"))
