"""Harness for SkyySacks 0.8.30 (Auto-compact = a per-bag coin upgrade + crafting opens Enchanted items - tools/sacks_0_8_30_patch.py).
Build first:
    python tools/sacks_0_8_30_patch.py && python SkyySacks/build_skyysacks_0.8.30.py

    python SkyySacks/test_skyysacks_0.8.30.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.8.29 -> 0.8.30: the classes the patch touches (EXPECT) + the new VoidCompact; non-class files: manifest
  CMP   on the 0.8.9 Void stand-ins (real 0.8.30 classes): the 110 pairs; the price (2,000 x the coin curve; 0 = free); BUY with too few
        coins (refused, nothing taken), enough (paid, pd line, saved by VoidJob 5 then coins:fn:flush, survives a restart), again (=),
        Fishing (nothing to compact), a crash after the take (coins refunded), a crash with a failing refund (said so, logged);
        COMPACT only bought + on bags, only unlocked Enchanted recipes, 100:1 with the remainder kept, the Enchanted item's own bag needs
        room, paused / master switch off = nothing, values conserved; CRAFT OPENS: Skyy's 180-ingot example EXACTLY through the real
        /craft materials path (CraftPage.materialsFor + wantedOne + the engine's removeMaterials + BagMirror.sync), loose first then the
        fewest Enchanted, change back in the bag; the per-recipe rule (a recipe using Iron AND Enchanted Iron gets no virtual stacks), the
        bench rule, fuel sets and bags.craftOpen off; the live-mirror rule (a bridge take of the Enchanted item trims the virtual stacks);
        CANCELLED CRAFT = full rollback (credit + repack -> the pool exactly as before); UNPACK (all fit / storage full / part fits);
        the Void page's Auto-compact box texts (price, Buy, On, Pause, Fishing) and the Unpack button; SweepTask.run calls the compactor
  RBW / RBR  ROLLBACK: a profile with comp.Mining=1 written by 0.8.30, then read + saved by the 0.8.29 jar: the line is kept, the pool is
        untouched (0.8.29 does nothing with it)
  D     START TWICE on a scratch COPY of NewBetaTest's Skyy_SkyySacks (0.8.27's live phase) + 0.8.10's run_live10; LIVE30: every live
        profile reads "not bought" in all six bags and the compactor - with EVERY Enchanted recipe unlocked - makes nothing (no byte changes)
  BZSEED  on a scratch copy of the live SkyyBazaar products.properties: no Enchanted item is cheap enough that buying it, opening it
        (Unpack / crafting) and selling 100 base beats the spread
  FIX2-* (compact1fix2): the price floor (never free when priced); no purchase without coll:recipes; the bag's rarity upgrade paid with
        Enchanted items (refused one short / paid with the fewest opened + change / bags.craftOpen off); openFor + unopen conserve; the
        pocket rule (!pocket + !e:<base> = no virtual stacks)
  FIX-* (compact1fix): the pd line on disk before the coin take; busy / changed-price / failed-save refusals; no early pool save after an
        unsaved sweep; the SkyyAlloy bench offers virtual bars + the trim after a booking; CRAFT-OPEN-SHORT; Mining's Rubble/Sand/Crystal note
  AA    engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_argv = list(sys.argv)
_RC = HK.run_compare
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_27", os.path.join(HERE, "test_skyysacks_0.8.27.py"))
T0827 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T0827)
sys.argv = _argv
HK.run_compare = _RC
T089 = T0827.T0810.T089

VERSION = "0.8.30"
OLD_VERSION = "0.8.29"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-%s.jar" % OLD_VERSION)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "compact1", "h")))
PKG = "com.skyy.sacks."
BETA = T0827.BETA
# the classes the patch changes (RecipeCmp ~<clinit> = its /craft tier sort table re-baked from tools/tier_tags.py, which holds another
# round's uncommitted rows - sort order only)
EXPECT = {"CfgFn": ["~m opExport"], "CfgRows": ["~m header", "~<clinit>"], "CfgFile": ["~<clinit>"],   # + the 9 new rows / template lines
          "SkyySacksPlugin": ["~m setup", "~m shutdown"],
          "SackCfg": ["+f CMP_ON", "+f CRAFT_OPEN", "+f CMP_LEVEL"] + ["+f CMP_COINS_" + c.upper() for c in
                                                                         ("Mining", "Foraging", "Farming", "Fishing", "Combat", "Smithing")]
          + ["~m pdKeys", "~m pdSig", "~m reload", "~<clinit>"],
          "BagMirror": ["+f vpair", "+f broke", "+m book", "+m virtuals", "+m fit0", "+m trimV", "~m sync", "~m addInputs", "~m rebuild", "~m empty",
                        "~m fit", "~c "],
          "SacksPage": ["+f cconfirm", "+m compactBox", "+m unpack", "~m render", "~m onEvent", "~m upgradeBox"],   # fixer 2: + upgradeBox
          "VoidStore": ["+m encHave", "+m openFor", "+m unopen", "~m upgrade"],   # fixer 2: the bag upgrade opens Enchanted items
          "BenchLink": ["~m fieldWanted"],   # fixer 2: the pocket window's "!pocket" marker
          "CraftPage": ["~m wantedOf", "~m wantedOne", "~m renderPage"],
          "SackBridge": ["~m craftPay", "~m craftRefund"], "VoidJob": ["~m run"], "SweepTask": ["~m run"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
IRON, EIRON, COB, ECOB, OAK, EOAK = ("Ingredient_Bar_Iron", "Skyy_Ench_Iron", "Rock_Stone_Cobble", "Skyy_Ench_Cobblestone", "Wood_Oak_Trunk",
                                     "Skyy_Ench_Oak")
RS = "_Recipe_Generated_0"
COP, ECOP = "Ingredient_Bar_Copper", "Skyy_Ench_Copper"   # fixer: the SkyyAlloy bench case


def coins_fixture(L):
    """a SkyyCoins stand-in: coins:fn:get / take / add / flush / curve on one static purse"""
    from jpype import JClass, JString
    jp = L["jp"]
    CtF, CtM, CtC = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    tc = jp.makeClass(PKG + "SkyyTestCoins30")
    tc.addInterface(jp.get("java.util.function.Function"))
    for f in ("public static volatile long BAL = 0L;", "public static volatile boolean ADDFAIL = false;", "public static volatile int FLUSHES = 0;",
              "public static volatile double CURVE = 1.0;", "public static volatile int TAKES = 0;", "public String kind;",
              # fixer: BUSY = a refused take with enough coins (a rebirth running); PDF = a file the take reads first (SEEN = its text then)
              "public static volatile boolean BUSY = false;", "public static volatile String PDF = null;",
              "public static volatile String SEEN = null;"):
        tc.addField(CtF.make(f, tc))
    tc.addConstructor(CtC.make("public SkyyTestCoins30(String k) { this.kind = k; }", tc))
    tc.addMethod(CtM.make("""public Object apply(Object o) {
  if (kind.equals("get")) return Long.valueOf(BAL);
  if (kind.equals("take")) {
    Object[] a = (Object[]) o; long n = ((Long) a[1]).longValue(); TAKES++;
    if (PDF != null) { try { SEEN = new String(java.nio.file.Files.readAllBytes(java.nio.file.Paths.get(PDF, new String[0])), "ISO-8859-1"); } catch (Throwable t) { SEEN = "ERR " + t; } }
    if (BUSY || BAL < n) return Boolean.FALSE; BAL = BAL - n; return Boolean.TRUE;
  }
  if (kind.equals("add")) { if (ADDFAIL) return null; Object[] a = (Object[]) o; BAL = BAL + ((Long) a[1]).longValue(); return Long.valueOf(BAL); }
  if (kind.equals("flush")) { FLUSHES++; return Integer.valueOf(1); }
  if (kind.equals("curve")) return Double.valueOf(CURVE);
  return null;
}""", tc))
    TC = JClass(tc.toClass(JClass(PKG + "SackBridge").class_))
    for kd in ("get", "take", "add", "flush"):
        L["bridge"].put(JString("coins:fn:" + kd), TC(JString(kd)))
    return TC


def cases30(K, L, scratch):
    from jpype import JClass, JString, JArray, JInt, JFloat, JShort, JLong
    VS, Defs, Cfg, Pool, SPage, Swp, Mirror = L["VS"], L["Defs"], L["Cfg"], L["Pool"], L["SPage"], L["Swp"], L["Mirror"]
    fresh, write_pool, player, coll, pc, inv_counts, total, custom_item, drain, restart = (L[n] for n in (
        "fresh", "write_pool", "player", "coll", "pc", "inv_counts", "total", "custom_item", "drain", "restart"))
    UUID, us, jfield, pref, bridge = L["UUID"], L["us"], L["jfield"], L["pref"], L["bridge"]
    VC, CP, SB = JClass(PKG + "VoidCompact"), JClass(PKG + "CraftPage"), JClass(PKG + "SackBridge")
    MQ = JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
    CRc = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    BR = JClass("com.hypixel.hytale.protocol.BenchRequirement")
    CRM = JClass("com.hypixel.hytale.builtin.crafting.component.CraftingManager")
    CIC = JClass("com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer")
    IC = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
    HS, HM = JClass("java.util.HashSet"), JClass("java.util.HashMap")
    Int = JClass("java.lang.Integer")
    for i_ in (IRON, EIRON, COB, ECOB, OAK, EOAK, "Ingredient_Stick", "Skyy_Ench_Stick", COP, ECOP):
        custom_item(i_, 100)
    drain()
    TC = coins_fixture(L)
    CATS = [str(c) for c in Defs.CATS]
    MI, FO, FI, SM = CATS.index("Mining"), CATS.index("Foraging"), CATS.index("Fishing"), CATS.index("Smithing")
    base = os.path.join(scratch, "cmp30")

    def mk():
        drain()   # fixer: no pool save of the last case still writing while fresh() deletes the folder
        fresh(base)
        U = UUID.fromString("00000000-0000-0000-0000-0000000c0830")
        k = str(U)
        bridge.put(JString("coll:recipes:" + k), JString(""))   # fixer 2: SkyyCollections published (nothing unlocked) - buyAt needs it
        return U, k

    def recipes(U, ids):
        bridge.put(JString("coll:recipes:" + str(U)), JString(",".join(ids)))

    def value(d, b, e):
        return d.get(b, 0) + 100 * d.get(e, 0)

    # ---- pairs + price
    pairs = dict((str(b), str(e)) for b, e in zip(VC.BASE, VC.ENCH))
    K.check(len(pairs) == 110 and pairs[IRON] == EIRON and pairs[COB] == ECOB and pairs["Ingredient_Bar_Bronze"] == "Skyy_Ench_Bronze"
            and int(VC.idxEnch(JString(EIRON))) >= 0 and int(VC.idxBase(JString(EIRON))) == -1 and int(VC.RATIO) == 100,
            "CMP pairs: 110 base -> Enchanted (Iron, Cobblestone, the Bronze alloy), lookups both ways, ratio 100")
    K.eq([int(VC.pairsIn(i, None)) > 0 for i in range(6)], [c != "Fishing" for c in CATS], "CMP every bag but Fishing holds Enchanted-able items")
    bridge.remove(JString("coins:fn:curve"))
    K.eq([int(VC.price(i)) for i in range(6)], [2000] * 6, "CMP price: 2,000 coins each (no coin curve = x1.0)")
    bridge.put(JString("coins:fn:curve"), TC(JString("curve")))
    TC.CURVE = 2.37
    K.eq(int(VC.price(MI)), 4700, "CMP price x the coin curve (2.37) rounded like SkyyShards: 4,740 -> 4,700")
    TC.CURVE = 1.0
    Cfg.CMP_COINS_FISHING = 0
    K.eq(int(VC.price(FI)), 0, "CMP price row 0 = free")
    Cfg.CMP_COINS_FISHING = 2000

    # ---- BUY
    U, k = mk()
    write_pool(os.path.join(base, "pools"), k, {COB: 250, IRON: 350})
    s = VS.st(k)
    s.first = 1
    TC.BAL = 1500
    r_ = str(VC.buy(U, k, MI))
    pdpath = os.path.join(base, "pd", k + ".properties")

    def pdtext():
        return open(pdpath, encoding="latin-1").read() if os.path.isfile(pdpath) else ""
    drain()
    K.check(r_.startswith("-Not enough coins (1,500 / 2,000)") and int(TC.BAL) == 1500 and not bool(VC.bought(k, MI))
            and "comp.Mining" not in pdtext(),
            "BUY with 1,500 coins: refused, nothing taken, not bought, the pd line undone on disk too: %s" % r_)
    TC.BAL = 5000
    f0 = int(TC.FLUSHES)
    TC.PDF = JString(pdpath)
    TC.SEEN = None
    r_ = str(VC.buy(U, k, MI))
    seen = str(TC.SEEN)
    TC.PDF = None
    drain()
    pdf = pdtext()
    K.check(r_.startswith("+Mining now has Auto-compact") and int(TC.BAL) == 3000 and bool(VC.bought(k, MI)) and "comp.Mining=1" in pdf
            and int(TC.FLUSHES) == f0 + 1 and bool(Swp.INVDIRTY.containsKey(U)),
            "BUY with 5,000: 2,000 paid, comp.Mining=1 saved, then SkyyCoins flushed, the sweep is due: %s" % r_)
    K.check("comp.Mining=1" in seen, "FIX-BUY the pd line is ON DISK before coins:fn:take runs (a crash can no longer take the coins without "
            "the upgrade): the take saw %s" % ("comp.Mining=1" if "comp.Mining=1" in seen else seen[:80]))
    K.check("bag upgrades open Enchanted items" in r_ and "other mods' shop costs use loose items" in r_,
            "FIX2-BUY the purchase line: crafts + bag upgrades open Enchanted items, other mods' shop costs use loose items: %s" % r_)
    r_ = str(VC.buy(U, k, MI))
    K.check(r_.startswith("=Mining already") and int(TC.BAL) == 3000, "BUY again: = already, nothing taken")
    r_ = str(VC.buy(U, k, FI))
    K.check(r_.startswith("=Nothing in Fishing") and int(TC.BAL) == 3000, "BUY Fishing: nothing to compact there, nothing taken")
    # fixer: a refused take with enough coins (rebirth running), a changed price, a failed pd save
    TC.BUSY = True
    r_ = str(VC.buy(U, k, SM))
    TC.BUSY = False
    drain()
    K.check(r_.startswith("-Coins are busy") and int(TC.BAL) == 3000 and not bool(VC.bought(k, SM)) and "comp.Smithing" not in pdtext(),
            "FIX-BUY a refused take with 3,000 coins: 'Coins are busy', nothing taken, not bought (line undone on disk): %s" % r_)
    r_ = str(VC.buyAt(U, k, SM, 1999))
    K.check(r_.startswith("=The price is now 2,000 coins") and int(TC.BAL) == 3000 and not bool(VC.bought(k, SM)),
            "FIX-BUY the Pay button showed 1,999 but the price is 2,000: refused, nothing taken: %s" % r_)
    t0 = int(TC.TAKES)
    VS.CRASHAT = "cmpsave"
    r_ = str(VC.buy(U, k, SM))
    K.check(r_.startswith("-The Void data could not be saved") and int(TC.TAKES) == t0 and int(TC.BAL) == 3000 and not bool(VC.bought(k, SM)),
            "FIX-BUY the pd save fails: no coin take was even tried, not bought: %s" % r_)
    VS.CRASHAT = "cmpbuy"
    r_ = str(VC.buy(U, k, SM))
    K.check("given back" in r_ and int(TC.BAL) == 3000 and not bool(VC.bought(k, SM)), "BUY crash after the take: the coins come back, not bought: %s" % r_)
    VS.CRASHAT = "cmpbuy"
    TC.ADDFAIL = True
    r_ = str(VC.buy(U, k, SM))
    drain()
    clog = open(os.path.join(base, "crafts.log"), encoding="utf8").read() if os.path.isfile(os.path.join(base, "crafts.log")) else ""
    K.check("could not be given back" in r_ and int(TC.BAL) == 1000 and not bool(VC.bought(k, SM)),
            "BUY crash + a failing refund: said so (tell an admin), not bought: %s" % r_)
    TC.ADDFAIL = False
    TC.BAL = 3000
    restart()
    K.check(bool(VC.bought(k, MI)) and not bool(VC.bought(k, SM)), "BUY survives a restart (read back from pd/<key>.properties)")
    JClass(PKG + "CraftLog").drain()
    clog = open(os.path.join(base, "crafts.log"), encoding="utf8").read()
    K.check("VOID-COMPACT-BUY Mining paid 2000 coins" in clog and "VOID-COMPACT-REFUND Smithing" in clog and "VOID-COMPACT-REFUND-FAILED Smithing" in clog,
            "BUY crafts.log: the purchase, the refund and the failed refund")

    # ---- FIX2 (compact1fix2): price floor, no sale without Collections, the bag upgrade opens Enchanted items, the pocket rule
    Cfg.CMP_COINS_FISHING = 4
    K.eq(int(VC.price(FI)), 10, "FIX2-PRICE a priced row of 4 coins rounds to 10, never to free")
    Cfg.CMP_COINS_FISHING = 2000
    bridge.put(JString("coins:fn:curve"), TC(JString("curve")))
    TC.CURVE = 0.001
    K.eq(int(VC.price(MI)), 10, "FIX2-PRICE 2,000 x a tiny curve value (0.001) = 2 -> 10 coins, never free")
    TC.CURVE = 1.0
    bridge.remove(JString("coins:fn:curve"))
    U, k = mk()
    VS.st(k).first = 1
    bridge.remove(JString("coll:recipes:" + k))
    TC.BAL = 5000
    t0 = int(TC.TAKES)
    r_ = str(VC.buy(U, k, SM))
    drain()
    K.check(r_.startswith("-Collections is not ready") and int(TC.BAL) == 5000 and int(TC.TAKES) == t0 and not bool(VC.bought(k, SM)),
            "FIX2-BUY SkyyCollections not published (coll:recipes missing): refused, no take tried, not bought: %s" % r_)
    bridge.put(JString("coll:recipes:" + k), JString(""))
    # the bag's rarity upgrade pays a line with Enchanted items (loose first, the fewest opened, change loose in the bag)
    up_ci, up_cost = None, None
    for ci_ in range(6):
        c_ = Cfg.parseCost(Cfg.cost(ci_, 1))
        if c_ is None:
            continue
        d_ = [(str(e.getKey()), int(e.getValue())) for e in c_.entrySet()]
        if any(int(VC.idxBase(JString(i_))) >= 0 and len(list(Defs.members(JString(i_)))) == 1 and n_ > 137 for i_, n_ in d_):
            up_ci, up_cost = ci_, d_
            break
    K.check(up_ci is not None, "FIX2-UPG a bag whose first rarity upgrade costs an Enchanted-able item: %s %s"
            % (CATS[up_ci] if up_ci is not None else None, up_cost))
    if up_ci is not None:
        def single(i_):
            return int(VC.idxBase(JString(i_))) >= 0 and len(list(Defs.members(JString(i_)))) == 1

        def up_pool(spare):
            d_ = {}
            for i_, n_ in up_cost:
                if single(i_):
                    d_[i_] = d_.get(i_, 0) + 37
                    e_ = str(VC.ENCH[int(VC.idxBase(JString(i_)))])
                    d_[e_] = d_.get(e_, 0) + (n_ - 37 + 99) // 100 + spare
                else:
                    d_[i_] = d_.get(i_, 0) + n_
            return d_
        U, k = mk()
        write_pool(os.path.join(base, "pools"), k, up_pool(-1))
        VS.st(k).first = 1
        pe = player(storage=[])
        b_ = pc(k)
        r_ = str(VS.upgrade(pe, U, k, up_ci, 0))
        K.check(r_.startswith("-Not enough") and pc(k) == b_ and int(VS.st(k).rar[up_ci]) == 0,
                "FIX2-UPG one Enchanted item short: refused, the pool untouched, no rarity change: %s" % r_)
        U, k = mk()
        write_pool(os.path.join(base, "pools"), k, up_pool(1))
        VS.st(k).first = 1
        b_ = pc(k)
        r_ = str(VS.upgrade(pe, U, k, up_ci, 0))
        drain()
        a = pc(k)
        ok_ = r_.startswith("+") and int(VS.st(k).rar[up_ci]) == 1
        for i_, n_ in up_cost:
            if single(i_):
                e_ = str(VC.ENCH[int(VC.idxBase(JString(i_)))])
                op_ = (n_ - 37 + 99) // 100
                ok_ = ok_ and a.get(e_, 0) == 1 and a.get(i_, 0) == 37 + op_ * 100 - n_ and value(b_, i_, e_) - value(a, i_, e_) == n_
            else:
                ok_ = ok_ and a.get(i_, 0) == 0
        K.check(ok_, "FIX2-UPG %s's upgrade with 37 loose + Enchanted items only: paid, the fewest Enchanted opened (1 spare left), the "
                "change loose in the bag, exactly the cost used: %s -> %s (%s)" % (CATS[up_ci], b_, a, r_))
        JClass(PKG + "CraftLog").drain()
        K.check("opened Enchanted" in open(os.path.join(base, "crafts.log"), encoding="utf8").read(),
                "FIX2-UPG crafts.log VOID-UPGRADE names the opened Enchanted items")
        Cfg.CRAFT_OPEN = False
        U, k = mk()
        write_pool(os.path.join(base, "pools"), k, up_pool(1))
        VS.st(k).first = 1
        b_ = pc(k)
        r_ = str(VS.upgrade(pe, U, k, up_ci, 0))
        Cfg.CRAFT_OPEN = True
        K.check(r_.startswith("-Not enough") and pc(k) == b_, "FIX2-UPG bags.craftOpen=false: Enchanted items do not count, refused, untouched: %s" % r_)
    # openFor + unopen (the upgrade's rollback): opened, then packed back = the pool exactly as before
    U, k = mk()
    write_pool(os.path.join(base, "pools"), k, {IRON: 10, EIRON: 3})
    VS.st(k).first = 1
    op = HM()
    n_ = int(VS.openFor(k, IRON, JLong(250), op))
    a = pc(k)
    K.check(n_ == 3 and a.get(IRON) == 310 and a.get(EIRON, 0) == 0 and int(op.get(JString(IRON)).longValue()) == 3,
            "FIX2-UPG openFor 250 with 10 loose + 3 Enchanted: 3 opened (310 loose): %s" % a)
    K.eq(int(VS.openFor(k, IRON, JLong(250), op)), 0, "FIX2-UPG openFor with enough loose already: opens nothing")
    VS.unopen(k, op)
    K.check(pc(k) == {IRON: 10, EIRON: 3}, "FIX2-UPG unopen (a refused upgrade): packed back, exactly 10 + 3 Enchanted: %s" % pc(k))
    # the pocket rule: while inventory crafting shares the mirror, no virtual stacks for a base whose Enchanted item an attached recipe uses
    mk_ = HS()
    Mirror.addInputs(mk_, JArray(MQ)([MQ(JString(EIRON), None, None, JInt(1), None), MQ(JString(COP), None, None, JInt(1), None)]))
    K.check(("!e:" + IRON) in [str(x) for x in mk_] and ("!nv:" + IRON) not in [str(x) for x in mk_],
            "FIX2-POCKET a recipe using Enchanted Iron marks !e:Iron (and no !nv: it does not use bars)")
    U, k = mk()
    write_pool(os.path.join(base, "pools"), k, {IRON: 10, EIRON: 3})
    VS.st(k).first = 1
    pcaps = Swp.caps(player(storage=[]).getInventory())
    w_ = HS()
    for x_ in ("!open", IRON, "!e:" + IRON):
        w_.add(JString(x_))
    v1 = [str(o[0]) for o in Mirror.virtuals(k, pcaps, w_)]
    w_.add(JString("!pocket"))
    v2 = [str(o[0]) for o in Mirror.virtuals(k, pcaps, w_)]
    K.check(IRON in v1 and IRON not in v2, "FIX2-POCKET benches only: virtual Iron offered (%s); + the pocket window attached: none (%s)" % (v1, v2))
    fw = JClass(PKG + "BenchLink").fieldWanted()
    if fw.isEmpty():
        K.notes.append("FIX2-POCKET the Fieldcraft recipes are not loaded here (fieldWanted empty) - the !pocket marker was checked through virtuals only")
    else:
        K.check(fw.contains(JString("!pocket")), "FIX2-POCKET the pocket window's wanted set carries !pocket")
    drain()

    # ---- COMPACT
    U, k = mk()
    write_pool(os.path.join(base, "pools"), k, {COB: 250, IRON: 350, OAK: 120})
    s = VS.st(k)
    s.first = 1
    recipes(U, [ECOB + RS])
    caps = VS.capsK(U, k)
    K.eq(int(VC.run(U, k, caps)), 0, "COMPACT nothing bought: nothing compacts (Cobblestone unlocked, 250 stored)")
    TC.BAL = 100000
    VC.buy(U, k, MI)
    v0 = pc(k)
    drain()
    poolf = os.path.join(base, "pools", k + ".properties")
    pb0 = open(poolf, "rb").read()
    Pool.SWEPTQ.put(JString(k), JClass("java.lang.Boolean").TRUE)   # this sweep's additions are not in the pool file yet
    made = int(VC.run(U, k, caps))
    drain()
    K.check(made == 2 and open(poolf, "rb").read() == pb0 and bool(Pool.DIRTY.containsKey(JString(k))),
            "FIX-SAVE the compactor after an unsaved sweep: the pool file is NOT written early (the crash-window rule), the pool stays dirty "
            "for the 10 s SackSaver")
    Pool.SWEPTQ.remove(JString(k))
    a = pc(k)
    K.check(made == 2 and a.get(COB) == 50 and a.get(ECOB) == 2 and a.get(IRON) == 350 and a.get(OAK) == 120,
            "COMPACT Mining bought: 250 Cobblestone -> 2 Enchanted + 50; Iron (Smithing, not bought) and Oak untouched: %s" % a)
    VC.buy(U, k, SM)
    VC.buy(U, k, FO)
    K.eq(int(VC.run(U, k, caps)), 0, "COMPACT Smithing + Foraging bought but their Enchanted recipes are not unlocked: nothing")
    recipes(U, [ECOB + RS, EIRON + RS, EOAK + RS])
    made = int(VC.run(U, k, caps))
    a = pc(k)
    K.check(made == 4 and a.get(IRON) == 50 and a.get(EIRON) == 3 and a.get(OAK) == 20 and a.get(EOAK) == 1
            and value(a, IRON, EIRON) == 350 and value(a, OAK, EOAK) == 120 and value(a, COB, ECOB) == 250,
            "COMPACT unlocked: 350 Iron bars -> 3 Enchanted Iron (+50), 120 Oak -> 1 (+20); every value conserved: %s" % a)
    K.check(str(Defs.homeOf(JString(EIRON))) == "Mining" and str(Defs.homeOf(JString(IRON))) == "Smithing",
            "COMPACT (the bars live in Smithing, Enchanted Iron in Mining)")
    Pool.add(k, IRON, JLong(250))
    full = HM(caps)
    full.put(JString("Mining"), Int(int(VS.usedAll(k)[MI])))
    K.eq(int(VC.run(U, k, full)), 0, "COMPACT the Mining bag is full: no Enchanted Iron is made (it would live there)")
    VC.toggle(U, k, SM)
    K.check(bool(VC.paused(k, SM)) and int(VC.run(U, k, caps)) == 0 and pc(k).get(IRON) == 300, "COMPACT Smithing paused: 300 Iron bars stay loose")
    VC.toggle(U, k, SM)
    Cfg.CMP_ON = False
    K.eq(int(VC.run(U, k, caps)), 0, "COMPACT Server Setup pd.compact.on=false: nothing")
    Cfg.CMP_ON = True
    K.eq(int(VC.run(U, k, caps)), 3, "COMPACT back on: the 300 bars -> 3 more Enchanted Iron")
    a = pc(k)
    K.check(a.get(EIRON) == 6 and IRON not in a, "COMPACT exact 100s leave no loose bars: %s" % a)
    drain()

    # ---- CRAFT OPENS (Skyy's example) through the real /craft materials path
    def recipe(rid, ins):
        mi = JArray(MQ)([MQ(JString(i), None, None, JInt(q), None) for i, q in ins])
        po = MQ(JString("Skyy_Test_Out30"), None, None, JInt(1), None)
        r = CRc(mi, po, JArray(MQ)([po]), JInt(1), JArray(BR)(0), JFloat(0.0), False, JInt(0))
        f = CRc.class_.getDeclaredField("id")
        f.setAccessible(True)
        f.set(r, JString(rid))
        return r
    custom_item("Skyy_Test_Out30", 100)
    U, k = mk()
    write_pool(os.path.join(base, "pools"), k, {IRON: 10, EIRON: 3})
    s = VS.st(k)
    s.first = 1
    p = player(storage=[])
    r180 = recipe("Skyy_Test_Iron180", [(IRON, 180)])
    mats = CP.materialsFor(p, k, CP.wantedOne(r180))
    m = Mirror.of(k)
    K.check(int(mats.countRemovableMaterial(MQ(JString(IRON), None, None, JInt(1), None))) == 310 and int(CP.limit(r180, mats)) == 1
            and m.vpair.containsKey(JString(IRON)),
            "OPEN the craft view counts 10 bars + 3 x 100 inside the Enchanted ones = 310 -> the 180-bar craft can be made once")
    ins = CRM.getInputMaterials(r180, 1)
    b0 = pc(k)
    m.broke.clear()
    mats.removeMaterials(ins)
    m.sync()
    a = pc(k)
    K.check(a.get(IRON) == 30 and a.get(EIRON) == 1 and int(m.broke.get(JString(IRON)).longValue()) == 2
            and value(b0, IRON, EIRON) - value(a, IRON, EIRON) == 180,
            "OPEN Skyy's example: 180 bars from 10 + 3 Enchanted -> 2 Enchanted opened, 1 left, 30 bars back in the bag (exactly 180 used): %s" % a)
    JClass(PKG + "CraftLog").drain()
    K.check("CRAFT-OPEN Skyy_Ench_Iron 2 -> Ingredient_Bar_Iron 200 (a craft used 180" in open(os.path.join(base, "crafts.log"), encoding="utf8").read(),
            "OPEN crafts.log CRAFT-OPEN line")
    # loose first: 150 loose + 2 Enchanted, a 120-bar craft opens nothing
    U, k = mk()
    write_pool(os.path.join(base, "pools"), k, {IRON: 150, EIRON: 2})
    VS.st(k).first = 1
    r120 = recipe("Skyy_Test_Iron120", [(IRON, 120)])
    mats = CP.materialsFor(p, k, CP.wantedOne(r120))
    m = Mirror.of(k)
    m.broke.clear()
    mats.removeMaterials(CRM.getInputMaterials(r120, 1))
    m.sync()
    a = pc(k)
    K.check(a.get(IRON) == 30 and a.get(EIRON) == 2 and m.broke.isEmpty(), "OPEN loose first: 150 bars + 2 Enchanted, 120 used -> 30 bars, both Enchanted kept: %s" % a)
    # the inventory pays before the bag (the combined container's order)
    U, k = mk()
    write_pool(os.path.join(base, "pools"), k, {EIRON: 2})
    VS.st(k).first = 1
    p2 = player(storage=[(IRON, 50)])
    mats = CP.materialsFor(p2, k, CP.wantedOne(r120))
    m = Mirror.of(k)
    mats.removeMaterials(CRM.getInputMaterials(r120, 1))
    m.sync()
    a, inv = pc(k), inv_counts(p2)
    K.check(inv.get(IRON, 0) == 0 and a.get(EIRON) == 1 and a.get(IRON) == 30, "OPEN 50 bars on you + 2 Enchanted, 120 used: the 50 carried, 1 Enchanted opened, 30 back: %s / %s" % (a, inv))
    # fixer: the clamp (an accounting error - the pool lost its Enchanted items behind the mirror's back) is logged loudly
    U, k = mk()
    write_pool(os.path.join(base, "pools"), k, {EIRON: 2})
    VS.st(k).first = 1
    mats = CP.materialsFor(p, k, CP.wantedOne(r120))
    m = Mirror.of(k)
    Pool.add(k, EIRON, JLong(-2))   # e.g. a pool reset that skipped afterTake
    mats.removeMaterials(CRM.getInputMaterials(r120, 1))
    m.sync()
    JClass(PKG + "CraftLog").drain()
    K.check("CRAFT-OPEN-SHORT Ingredient_Bar_Iron used 120 had 0 loose + 0 Skyy_Ench_Iron short 120" in open(os.path.join(base, "crafts.log"), encoding="utf8").read(),
            "FIX-SHORT open0's clamp writes CRAFT-OPEN-SHORT with the shortfall to crafts.log")
    # the rules: one recipe with Iron AND Enchanted Iron; a bench set using the Enchanted item; a fuel set; bags.craftOpen off
    U, k = mk()
    write_pool(os.path.join(base, "pools"), k, {IRON: 10, EIRON: 3})
    VS.st(k).first = 1
    both = recipe("Skyy_Test_Both30", [(IRON, 50), (EIRON, 1)])
    mats = CP.materialsFor(p, k, CP.wantedOne(both))
    K.check(int(mats.countRemovableMaterial(MQ(JString(IRON), None, None, JInt(1), None))) == 10 and not Mirror.of(k).vpair.containsKey(JString(IRON)),
            "OPEN a recipe paying Iron AND Enchanted Iron gets no virtual stacks (it could pay one Enchanted twice): 10 bars only")
    def offered(mm, iid):
        return sum(int(mm.slotQty[i]) for i in range(36) if mm.slotIds[i] is not None and str(mm.slotIds[i]) == iid)
    # fixer: the SkyyAlloy bench - Alloy_Ench_Bronze (Enchanted Iron + Enchanted Copper) next to Alloy_Bronze (Iron bars + Copper bars):
    # the per-recipe rule offers BOTH the virtual bars and the real Enchanted Iron; a 180-bar craft opens 2 and the offer is trimmed after
    bench = HS()
    Mirror.addInputs(bench, JArray(MQ)([MQ(JString(ECOP), None, None, JInt(1), None), MQ(JString(EIRON), None, None, JInt(1), None)]))
    Mirror.addInputs(bench, JArray(MQ)([MQ(JString(COP), None, None, JInt(1), None), MQ(JString(IRON), None, None, JInt(1), None)]))
    bmats = CP.materialsFor(p, k, bench)
    m = Mirror.of(k)
    K.check(m.vpair.containsKey(JString(IRON)) and offered(m, IRON) == 310 and offered(m, EIRON) == 3 and "!nv:" + IRON not in [str(x) for x in bench],
            "FIX-BENCH the SkyyAlloy bench (one recipe uses Enchanted Iron, another Iron bars): virtual Iron offered (310) AND the 3 Enchanted Iron")
    m.broke.clear()
    bmats.removeMaterials(CRM.getInputMaterials(r180, 1))
    m.sync()
    a = pc(k)
    K.check(a.get(IRON) == 30 and a.get(EIRON) == 1 and offered(m, EIRON) <= 1 and offered(m, IRON) <= 130,
            "FIX-BENCH a 180-bar craft there: 2 Enchanted opened, 30 bars + 1 left, and the same mirror now offers at most 1 Enchanted Iron "
            "and 130 bars (trimmed after the booking - no second craft can pay with an opened one): %s offered %d / %d"
            % (a, offered(m, EIRON), offered(m, IRON)))
    bmats.removeMaterials(CRM.getInputMaterials(recipe("Skyy_Test_EIron1", [(EIRON, 1)]), 1))
    m.sync()
    a = pc(k)
    K.check(a.get(EIRON, 0) == 0 and a.get(IRON) == 30 and offered(m, IRON) <= 30,
            "FIX-BENCH then the last Enchanted Iron taken itself: 0 left, 30 bars, the bar offer trimmed to 30: %s" % a)
    Pool.add(k, IRON, JLong(-30))
    Pool.add(k, EIRON, JLong(3))
    Pool.add(k, IRON, JLong(10))
    both2 = HS()
    Mirror.addInputs(both2, JArray(MQ)([MQ(JString(IRON), None, None, JInt(5), None), MQ(JString(EIRON), None, None, JInt(1), None)]))
    Mirror.of(k).rebuild(Swp.caps(p.getInventory()), both2)
    K.check(not Mirror.of(k).vpair.containsKey(JString(IRON)), "FIX-BENCH a bench recipe using Iron AND Enchanted Iron: no virtual Iron there (per-recipe rule)")
    bench2 = HS()
    Mirror.addInputs(bench2, JArray(MQ)([MQ(JString(IRON), None, None, JInt(5), None)]))
    Mirror.of(k).rebuild(Swp.caps(p.getInventory()), bench2)
    K.check(Mirror.of(k).vpair.containsKey(JString(IRON)) and "!open" in [str(x) for x in bench2], "OPEN a bench using only Iron: virtual Iron offered")
    fuel = HS()
    fuel.add(JString(IRON))
    Mirror.of(k).rebuild(Swp.caps(p.getInventory()), fuel)
    K.check(not Mirror.of(k).vpair.containsKey(JString(IRON)), "OPEN a fuel / single-id set (no recipe): nothing opens")
    Cfg.CRAFT_OPEN = False
    Mirror.of(k).rebuild(Swp.caps(p.getInventory()), bench2)
    K.check(not Mirror.of(k).vpair.containsKey(JString(IRON)), "OPEN Server Setup bags.craftOpen=false: nothing opens")
    Cfg.CRAFT_OPEN = True
    # the live-mirror rule: a bridge take of Enchanted Iron while the mirror offers virtual bars trims them
    m = Mirror.of(k)
    m.rebuild(Swp.caps(p.getInventory()), bench2)
    o1 = offered(m, IRON)
    Bridge = SB
    Bridge.PLAYERS = None
    Pool.add(k, EIRON, JLong(-2))   # what a bridge take does: beforeTake, the debit, afterTake(Enchanted)
    Mirror.afterTake(k, EIRON)
    o2 = offered(m, IRON)
    K.check(o1 == 310 and o2 == 110, "OPEN the live-mirror rule: 2 Enchanted Iron taken elsewhere -> the offer drops 310 -> 110 (never more than the bag holds)")

    # ---- CANCELLED CRAFT (craftPay's refusal / refund: the bag part credited back + the opened Enchanted packed back)
    U, k = mk()
    write_pool(os.path.join(base, "pools"), k, {IRON: 10, EIRON: 3})
    VS.st(k).first = 1
    b0 = pc(k)
    mats = CP.materialsFor(p, k, CP.wantedOne(r180))
    m = Mirror.of(k)
    bagB = CP.snapshot(m.cont)
    m.broke.clear()
    mats.removeMaterials(CRM.getInputMaterials(r180, 1))
    bagT = CP.removedItems(bagB, CP.snapshot(m.cont))
    m.sync()
    brk = HM(m.broke)
    mid = pc(k)
    SB.creditBags(k, bagT)
    VC.repack(k, brk)
    a = pc(k)
    K.check(mid.get(EIRON) == 1 and a == b0, "ROLLBACK a refused / refunded craft: the 180 bars credited back + the 2 opened Enchanted packed again = "
            "exactly 10 bars + 3 Enchanted (%s -> %s -> %s)" % (b0, mid, a))

    # ---- the REAL sacks:fn:craftPay / craftRefund (SkyyGear's Smithing / Anvil path) on a stand-in recipe store
    DAMc = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
    rmap = HM()
    rstore = us.allocateInstance(L["FAKECLS"])
    L["fm"].set(rstore, DAMc(rmap))
    f_ = CRc.class_.getDeclaredField("ASSET_STORE")
    f_.setAccessible(True)
    f_.set(None, rstore)
    rmap.put(JString("Skyy_Test_Iron180"), r180)
    U, k = mk()
    write_pool(os.path.join(base, "pools"), k, {IRON: 10, EIRON: 3})
    VS.st(k).first = 1
    pp = player(storage=[])
    SB.PLAYERS = L["TPlayers"]()
    L["TPlayers"].P = pp
    b0 = pc(k)
    recipes(U, ["Skyy_Test_Iron180"])   # craftWhy: a collection recipe of this player = allowed (no engine bench lists needed)
    pay = SB.craftPay(U, JString("Skyy_Test_Iron180"), 1)
    a = pc(k)
    K.check(int(pay[0].longValue()) == 1, "PAY sacks:fn:craftPay runs on the stand-in store: %s" % (pay[2],))
    if int(pay[0].longValue()) == 1:
        rc = pay[1]
        K.check(a.get(IRON) == 30 and a.get(EIRON) == 1, "PAY sacks:fn:craftPay of the 180-bar recipe: 2 Enchanted opened, 30 bars + 1 Enchanted left: %s" % a)
        rec = SB.RECEIPTS.get(rc)
        K.check(rec is not None and len(rec) > 7 and int(rec[7].get(JString(IRON)).longValue()) == 2, "PAY the receipt records the 2 opened Enchanted (slot 7)")
        back = int(SB.craftRefund(U, rc))
        K.check(back == 180 and pc(k) == b0, "PAY sacks:fn:craftRefund: 180 back + the 2 Enchanted packed again = exactly 10 bars + 3 Enchanted: %s" % pc(k))
        pay2 = SB.craftPay(U, JString("Skyy_Test_Iron180"), 1)
        K.check(int(pay2[0].longValue()) == 1 and bool(SB.craftCommit(U, pay2[1])) and pc(k).get(EIRON) == 1, "PAY then commit: the craft stays paid (1 Enchanted left)")
    SB.PLAYERS = None

    # ---- UNPACK
    U, k = mk()
    write_pool(os.path.join(base, "pools"), k, {EIRON: 3, IRON: 5})
    VS.st(k).first = 1
    p3 = player(storage=[])
    r_ = str(SPage.unpack(p3, k, EIRON, 2))
    a, inv = pc(k), inv_counts(p3)
    K.check(r_.startswith("+Unpacked 200") and inv.get(IRON) == 200 and a.get(EIRON) == 1 and a.get(IRON) == 5, "UNPACK 2 Enchanted Iron -> 200 bars in the storage: %s %s %s" % (r_, a, inv))
    p4 = player(storage=[("Ingredient_Stick", 100)], cap=1)
    r_ = str(SPage.unpack(p4, k, EIRON, 1))
    a = pc(k)
    K.check(r_.startswith("-Your storage is full") and a.get(EIRON) == 1 and a.get(IRON) == 5, "UNPACK storage full: nothing unpacked, the Enchanted item packed back: %s %s" % (r_, a))
    Pool.add(k, EIRON, JLong(1))
    p5 = player(storage=[("Ingredient_Stick", 100), (IRON, 50)], cap=3)
    r_ = str(SPage.unpack(p5, k, EIRON, 2))
    a, inv = pc(k), inv_counts(p5)
    K.check(inv.get(IRON) == 200 and a.get(EIRON, 0) == 0 and a.get(IRON) == 55 and value(a, IRON, EIRON) + inv.get(IRON) == 5 + 200 + 50,
            "UNPACK 2 with room for 150: 150 bars out, the other 50 stay loose in the bag (under 100: not packed back), conserved: %s %s %s" % (r_, a, inv))
    # part fits with 100+ left over: one slot of room (100) for 3 Enchanted -> 100 out, 2 packed back
    Pool.add(k, EIRON, JLong(3))
    p6 = player(storage=[("Ingredient_Stick", 100)], cap=2)
    b6 = pc(k)
    r_ = str(SPage.unpack(p6, k, EIRON, 3))
    a, inv = pc(k), inv_counts(p6)
    K.check(inv.get(IRON) == 100 and a.get(EIRON) == 2 and a.get(IRON) == b6.get(IRON), "UNPACK 3 with room for 100: 100 out, 2 Enchanted packed back, the loose bars unchanged: %s %s %s" % (r_, a, inv))
    K.check(str(SPage.unpack(p3, k, IRON, 1)).startswith("-That item does not unpack"), "UNPACK a base item: refused")

    # ---- the page (the Auto-compact box + Unpack)
    UCBc = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEBc = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")

    def ucb_text(b_):
        out_ = []
        for c_ in b_.getCommands():
            k_ = c_.getClass()
            while k_ is not None:
                for f_ in k_.getDeclaredFields():
                    if JClass("java.lang.reflect.Modifier").isStatic(f_.getModifiers()):
                        continue
                    f_.setAccessible(True)
                    v_ = f_.get(c_)
                    if v_ is not None:
                        out_.append(str(v_))
                k_ = k_.getSuperclass()
        return "\n".join(out_)

    def page():
        pg = us.allocateInstance(SPage.class_)
        jfield(SPage.class_, "playerRef").set(pg, pref(U))
        jfield(SPage.class_, "info").set(pg, JString(""))
        jfield(SPage.class_, "amount").set(pg, JString(""))
        return pg

    def dump(o_, depth=0):
        """every non-static field value under o_ (lists / arrays / maps walked) - the event bindings' data strings"""
        if o_ is None or depth > 5:
            return []
        s_ = str(o_)
        try:
            if isinstance(o_, str) or o_.getClass().getName().startswith(("java.lang.", "java.util.UUID")):
                return [s_]
        except Exception:
            return [s_]
        out_ = [s_]
        try:
            for x_ in (list(o_) if hasattr(o_, "__iter__") else []):
                out_ += dump(x_, depth + 1)
        except Exception:
            pass
        k_ = o_.getClass()
        while k_ is not None and not str(k_.getName()).startswith("java."):
            for f_ in k_.getDeclaredFields():
                if JClass("java.lang.reflect.Modifier").isStatic(f_.getModifiers()):
                    continue
                try:
                    f_.setAccessible(True)
                    out_ += dump(f_.get(o_), depth + 1)
                except Exception:
                    pass
            k_ = k_.getSuperclass()
        return out_
    LASTEV = []

    def render(pg, cat, sel=None):
        pg.cat = cat
        pg.sel = None if sel is None else JString(sel)
        b_, e_ = UCBc(), UEBc()
        pg.render(b_, e_, p3, k, U)
        LASTEV[:] = dump(e_)
        return ucb_text(b_)
    TC.BAL = 500
    pg = page()
    t = render(pg, "Smithing")
    K.check("Auto-compact - 2,000 coins" in t and "SkyyVCmpBuy" in t and "SkyyVUnpack" not in t, "PAGE Smithing not bought: 'Auto-compact - 2,000 coins', Buy (greyed: 500 coins)")
    TC.BAL = 9000
    t = render(pg, "Mining")
    K.check("Not yet: Rubble, Sand, Crystal." in t, "FIX-PAGE Mining's box says Rubble, Sand and Crystal cannot auto-compact yet")
    pg.cconfirm = True
    t = render(pg, "Smithing")
    K.check("Pay 2,000 coins for Auto-compact?" in t and "SkyyVCmpYes" in t and "SkyyVCmpNo" in t, "PAGE after Buy: 'Pay 2,000 coins for Auto-compact?' with Pay / Cancel")
    K.check(any("cmpok:%d:2000" % SM in x for x in LASTEV), "FIX-PAGE the Pay button sends the price it shows (cmpok:<bag>:2000)")
    VC.buy(U, k, SM)
    t = render(pg, "Smithing")
    K.check("Auto-compact: On" in t and "SkyyVCmpTog" in t, "PAGE bought: 'Auto-compact: On' + Pause")
    VC.toggle(U, k, SM)
    t = render(pg, "Smithing")
    K.check("Auto-compact: Paused" in t, "PAGE paused: 'Auto-compact: Paused' + Turn on")
    t = render(pg, "Fishing")
    K.check("Nothing in Fishing has an Enchanted form yet." in t and "SkyyVCmpBuy" not in t, "PAGE Fishing: nothing to compact, no button")
    t = render(pg, "Mining", EIRON)
    K.check("SkyyVUnpack" in t and "(100 each)" in t, "PAGE an Enchanted item picked: '(100 each)' + Unpack to inventory")
    pg.cconfirm = True
    pg.onEvent(None, None, p3, JString('{"a":"tab:Farming","@Amt":""}'))
    K.check(not bool(pg.cconfirm), "PAGE a tab click ends the Pay step")
    # the clicks themselves (onEvent; its rebuild() has no client here - the state and the result line are what count)
    pg.onEvent(None, None, p3, JString('{"a":"cmpbuy","@Amt":""}'))
    K.check(bool(pg.cconfirm) and "Pay" in str(pg.info), "PAGE Buy click -> the Pay / Cancel step: %s" % pg.info)
    pg.onEvent(None, None, p3, JString('{"a":"cmpno","@Amt":""}'))
    K.check(not bool(pg.cconfirm), "PAGE Cancel click ends it, nothing bought")
    sk = Pool.settledKey(U)
    if sk is not None and str(sk) == k:
        pg.key = JString(k)
        TC.BAL = 9000
        pg.onEvent(None, None, p3, JString('{"a":"cmpok:%d:1500","@Amt":""}' % FO))
        K.check(str(pg.info).startswith("=The price is now 2,000") and not bool(VC.bought(k, FO)) and int(TC.BAL) == 9000,
                "FIX-PAGE a Pay click carrying an old price (1,500): refused, nothing taken: %s" % pg.info)
        pg.onEvent(None, None, p3, JString('{"a":"cmpok:%d:2000","@Amt":""}' % FO))
        K.check(str(pg.info).startswith("+Foraging now has Auto-compact") and bool(VC.bought(k, FO)) and int(TC.BAL) == 7000,
                "PAGE Pay click buys Foraging (2,000 coins): %s" % pg.info)
        pg.onEvent(None, None, p3, JString('{"a":"cmptog:%d","@Amt":""}' % FO))
        K.check(bool(VC.paused(k, FO)), "PAGE Pause click pauses it: %s" % pg.info)
        Pool.add(k, EIRON, JLong(1))
        pg.sel = JString(EIRON)
        n0 = inv_counts(p3).get(IRON, 0)
        pg.onEvent(None, None, p3, JString('{"a":"unpack","@Amt":""}'))
        K.check(str(pg.info).startswith("+Unpacked 100") and inv_counts(p3).get(IRON, 0) == n0 + 100, "PAGE Unpack click (empty amount = 1): %s" % pg.info)
        pg.onEvent(None, None, p3, JString('{"a":"unpack","@Amt":"x"}'))
        K.check(str(pg.info).startswith("-Type a number"), "PAGE Unpack with a bad amount: %s" % pg.info)
    else:
        K.notes.append("PAGE the click tests need settledKey(U) == k here (got %s) - buy / toggle / unpack were run directly above" % sk)

    Pool.WRITER.shutdownNow()


def run_cmp30(out, jar, scratch, home):
    T089.void_cases = cases30
    T089.run_void(out, jar, scratch, home)


def run_sweephook(out, jar, scratch, _home):
    """SweepTask.run: items() -> VoidCompact.run -> SIG.put (bytecode order)"""
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(True)
    cp.appendClassPath(JString(jar))
    m = cp.get(PKG + "SweepTask").getDeclaredMethod("run")
    seen = []
    ci = m.getMethodInfo().getCodeAttribute().iterator()
    cpool = m.getMethodInfo().getConstPool()
    Mn = JClass("javassist.bytecode.Mnemonic")
    while ci.hasNext():
        i = ci.next()
        op = ci.byteAt(i)
        if str(Mn.OPCODE[op]) in ("invokestatic", "invokevirtual", "invokeinterface"):
            idx = ci.u16bitAt(i + 1)
            seen.append(str(cpool.getMethodrefClassName(idx)).split(".")[-1] + "." + str(cpool.getMethodrefName(idx)) if str(Mn.OPCODE[op]) != "invokeinterface"
                        else str(cpool.getInterfaceMethodrefClassName(idx)).split(".")[-1] + "." + str(cpool.getInterfaceMethodrefName(idx)))
    a, b_, c = (seen.index(x) if x in seen else -1 for x in ("SweepTask.items", "VoidCompact.run", "SweepTask.sigOf"))
    K.check(0 <= a < b_ < c, "SWEEP SweepTask.run: items -> VoidCompact.run -> sigOf / SIG (%d / %d / %d)" % (a, b_, c))
    K.save()


def run_rbw(out, jar, scratch, _home):
    """0.8.30 writes a bought profile (pd line + pool) for the rollback reader"""
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    Paths = JClass("java.nio.file.Paths")
    VS, Pool = JClass(PKG + "VoidStore"), JClass(PKG + "SackPool")
    Pool.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySacks")
    d = os.path.join(scratch, "rb")
    os.makedirs(os.path.join(d, "pd"), exist_ok=True)
    os.makedirs(os.path.join(d, "pools"), exist_ok=True)
    VS.DIR = Paths.get(os.path.join(d, "pd"))
    k = "00000000-0000-0000-0000-0000000b0830"
    open(os.path.join(d, "pools", k + ".properties"), "w", encoding="latin-1").write("#t\n%s=40\n%s=7\n" % (IRON, EIRON))
    s = VS.st(k)
    s.first = 1
    s.extra.setProperty(JString("comp.Mining"), JString("1"))
    s.extra.setProperty(JString("comp.off.Smithing"), JString("1"))
    K.check(bool(VS.saveNow(k)), "RBW 0.8.30 saved comp.Mining=1 + comp.off.Smithing=1")
    K.save()


def run_rbr(out, _jar, scratch, _home):
    """the 0.8.29 jar reads + saves that profile: the comp lines stay, the pool file is not touched"""
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, OLD_JAR, B.JAVASSIST], verify=True)
    Paths = JClass("java.nio.file.Paths")
    VS, Pool = JClass(PKG + "VoidStore"), JClass(PKG + "SackPool")
    Pool.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySacks")
    d = os.path.join(scratch, "rb")
    VS.DIR = Paths.get(os.path.join(d, "pd"))
    Pool.DIR = Paths.get(os.path.join(d, "pools"))
    k = "00000000-0000-0000-0000-0000000b0830"
    pool0 = open(os.path.join(d, "pools", k + ".properties"), "rb").read()
    s = VS.st(k)
    K.check(s is not None and int(s.first) == 1, "RBR 0.8.29 reads the 0.8.30 Void file")
    VS.markDirty(k)
    K.check(bool(VS.saveNow(k)), "RBR 0.8.29 saves it")
    t = open(os.path.join(d, "pd", k + ".properties"), encoding="latin-1").read()
    K.check("comp.Mining=1" in t and "comp.off.Smithing=1" in t, "RBR the comp lines are kept by 0.8.29 (unknown keys), so 0.8.30+ finds them again")
    K.check(open(os.path.join(d, "pools", k + ".properties"), "rb").read() == pool0 and
            dict((str(e.getKey()), int(e.getValue().longValue())) for e in Pool.pool(k).entrySet()) == {IRON: 40, EIRON: 7},
            "RBR the pool (40 bars + 7 Enchanted Iron) is untouched by 0.8.29")
    K.save()


def run_live30(out, jar, scratch, home):
    """every live profile: not bought in any bag; the compactor with EVERY Enchanted recipe unlocked makes nothing; no byte changes"""
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    Paths = JClass("java.nio.file.Paths")
    VS, Pool, VC, Cfg = JClass(PKG + "VoidStore"), JClass(PKG + "SackPool"), JClass(PKG + "VoidCompact"), JClass(PKG + "SackCfg")
    Pool.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySacks")
    bridge = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", bridge)

    def snap():
        d = {}
        for root, _ds, fs in os.walk(home):
            for n in fs:
                p = os.path.join(root, n)
                d[os.path.relpath(p, home)] = open(p, "rb").read()
        return d
    s0 = snap()
    Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
    Cfg.MTIME = -1
    Cfg.reload()
    K.check(bool(Cfg.CMP_ON) and bool(Cfg.CRAFT_OPEN) and int(Cfg.CMP_COINS_MINING) == 2000 and int(Cfg.CMP_LEVEL) == 10,
            "LIVE30 the live config (no new lines) reads the defaults: on, crafting opens, 2,000 coins, level 10")
    VS.DIR = Paths.get(os.path.join(home, "pd"))
    Pool.DIR = Paths.get(os.path.join(home, "pools"))
    keys = sorted(n[:-11] for n in os.listdir(os.path.join(home, "pd")) if n.endswith(".properties"))
    allr = ",".join(str(e) + "_Recipe_Generated_0" for e in VC.ENCH)
    bought, made, ench = [], 0, 0
    U = JClass("java.util.UUID")
    for k in keys:
        u = U.fromString(JString(k[:36]))
        bridge.put(JString("coll:recipes:" + k[:36]), JString(allr))
        bought += [(k, c) for c in range(6) if bool(VC.bought(k, c))]
        made += int(VC.run(u, k, VS.capsK(u, k)))
        ench += sum(int(e.getValue().longValue()) for e in Pool.pool(k).entrySet() if str(e.getKey()).startswith("Skyy_Ench_"))
    K.check(len(keys) >= 1 and not bought and made == 0,
            "LIVE30 %d live profiles: none has Auto-compact in any bag (the migration rule: off for everyone, no free unlock); with every "
            "Enchanted recipe unlocked nothing compacts" % len(keys))
    K.check(ench > 0, "LIVE30 the Enchanted items already stored stay (%d across the profiles)" % ench)
    K.check(snap() == s0, "LIVE30 no byte changed in the live copy (%d files)" % len(s0))
    K.save()


def run_bzseed(out, _jar, scratch, _home):
    """fixer (critic 1 finding 1, Unpack = a reverse route): on a scratch COPY of the live SkyyBazaar 0.2.1 products.properties, every
    Enchanted item is priced at least 100 x its base - buy Enchanted -> Unpack / craft-open -> sell 100 base never beats the spread"""
    import shutil
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import skyyench as EN
    K = HK.Child(out)
    src = os.path.join(os.path.dirname(BETA), "Skyy_SkyyBazaar", "products.properties") if BETA else None
    if not src or not os.path.isfile(src):
        K.notes.append("BZSEED no live SkyyBazaar products.properties next to %s - skipped" % BETA)
        K.save()
        return
    d = os.path.join(scratch, "bz")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "products.properties")
    shutil.copyfile(src, cp)
    pr = {}
    for ln in open(cp, encoding="latin-1"):
        if "=" in ln and not ln.startswith("#"):
            kk, vv = ln.split("=", 1)
            try:
                pr[kk.strip()] = float(vv.split(",")[1])
            except (IndexError, ValueError):
                pass
    pairs = ([(t[2], EN.PREFIX + t[0]) for t in EN.TABLE if t[1] == "I"] + [(t[2], EN.PREFIX + t[0]) for t in EN.TABLE_ALLOYS if t[1] == "I"])
    rs = sorted(((100.0 * pr[b] / pr[e], b, e) for b, e in pairs if b in pr and e in pr and pr[e] > 0), reverse=True)
    unpriced = [e for b, e in pairs if not (b in pr and e in pr)]
    sp = 0.10   # SkyyBazaar SPREAD: bought at price x (1 + 0.10), sold at price x (1 - 0.10)
    K.check(len(rs) >= 100 and rs[0][0] * (1.0 - sp) < 1.0 + sp,
            "BZSEED %d of %d pairs priced on the live Bazaar: 100 x base / Enchanted is at most %.4f (%s); a loop (buy Enchanted -> Unpack / "
            "craft-open -> sell 100 base) needs more than %.3f - none pays; unpriced (not sellable): %s"
            % (len(rs), len(pairs), rs[0][0], rs[0][2], (1.0 + sp) / (1.0 - sp), unpriced))
    K.save()


if __name__ == "__main__":
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ["VoidCompact"],
           [("cmp30", run_cmp30), ("sweephook", run_sweephook), ("rbw", run_rbw), ("rbr", run_rbr),
            ("live", T0827.run_live27), ("live2", T0827.T0810.run_live10), ("live30", run_live30), ("bzseed", run_bzseed)],
           __file__, live=(BETA, "Skyy_SkyySacks"))
